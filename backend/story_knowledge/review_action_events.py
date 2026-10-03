"""Immutable review-action events, chain validation, and entry locking."""

from __future__ import annotations

import base64
import copy
import errno
import fcntl
import hashlib
import os
import re
import stat
import threading
import uuid
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from backend.story_knowledge import apply_contract
from backend.story_knowledge import review_queue_storage


EVENT_SCHEMA_VERSION = "review_action_event.v1"

_EVENT_TYPES = frozenset(
    {
        "action_intent",
        "action_completed",
        "action_failed",
        "action_recovery_completed",
    }
)
_ACTION_COMMANDS = frozenset(
    {
        "approve",
        "mark_reviewed",
        "request_more_evidence",
        "defer",
        "reject",
        "mark_duplicate",
        "mark_split_required",
        "rename_candidate_metadata",
        "record_source_linkage_correction",
        "mark_superseded",
        "record_owner_authored_correction",
        "quarantine",
        "update_owner_note",
        "set_review_status",
    }
)
_FAILURE_REASONS = frozenset(
    {"QUEUE_WRITE_FAILED", "QUEUE_WRITE_PARTIAL", "QUEUE_STATE_CORRUPT"}
)

_COMMON_EVENT_FIELDS = frozenset(
    {
        "schema_version",
        "event_type",
        "event_hash",
        "sequence",
        "previous_event_hash",
        "project_id",
        "queue_entry_id",
        "candidate_record_id",
        "action_command",
        "action_id",
        "idempotency_key",
        "request_hash",
        "actor_type",
        "actor_ref",
    }
)
_INTENT_FIELDS = _COMMON_EVENT_FIELDS | frozenset(
    {
        "created_at",
        "completion_state",
        "queue_before_hash",
        "target_queue_canonical_bytes_b64url",
        "target_queue_hash",
        "candidate_before_hash",
        "evidence_projection_before_hash",
        "evidence_provenance_preserved",
        "candidate_not_mutated",
        "no_promotion_requested",
        "no_memory_canon_mutation_requested",
    }
)
_COMPLETED_FIELDS = _COMMON_EVENT_FIELDS | frozenset(
    {
        "intent_event_hash",
        "queue_after_hash",
        "candidate_after_hash",
        "evidence_projection_after_hash",
        "completed_at",
        "completion_state",
    }
)
_FAILED_FIELDS = _COMMON_EVENT_FIELDS | frozenset(
    {
        "intent_event_hash",
        "failure_reason",
        "failure_detail",
        "observed_queue_hash",
        "retryable",
        "failed_at",
        "completion_state",
    }
)
_RECOVERY_COMPLETED_FIELDS = _COMMON_EVENT_FIELDS | frozenset(
    {
        "intent_event_hash",
        "failed_event_hash",
        "queue_after_hash",
        "candidate_after_hash",
        "evidence_projection_after_hash",
        "completed_at",
        "completion_state",
    }
)
_FIELDS_BY_EVENT_TYPE = {
    "action_intent": _INTENT_FIELDS,
    "action_completed": _COMPLETED_FIELDS,
    "action_failed": _FAILED_FIELDS,
    "action_recovery_completed": _RECOVERY_COMPLETED_FIELDS,
}

_SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
_ACTION_ID_RE = re.compile(r"^rvact_([a-f0-9]{32})$")
_UUID4_RE = re.compile(
    r"^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$"
)
_RFC3339_UTC_RE = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"
    r"(?:\.[0-9]+)?Z$"
)
_EVENT_FILENAME_RE = re.compile(r"^([0-9]{12})_([a-f0-9]{64})\.json$")
_BASE64URL_RE = re.compile(r"^[A-Za-z0-9_-]+$")

_PROCESS_LOCKS: dict[tuple[Path, str], threading.Lock] = {}
_PROCESS_LOCKS_GUARD = threading.Lock()


def _canonical_json_bytes(value) -> bytes:
    return apply_contract.canonical_json_bytes(value)


def _canonical_sha256(value) -> str:
    return hashlib.sha256(_canonical_json_bytes(value)).hexdigest()


def _event_hash_without_member(event) -> str:
    preimage = dict(event)
    preimage.pop("event_hash", None)
    return _canonical_sha256(preimage)


def _validate_sha256(value, field="hash") -> str:
    if not isinstance(value, str) or not _SHA256_RE.fullmatch(value):
        raise ValueError("invalid {0}".format(field))
    return value


def _validate_uuid4_key(value) -> str:
    if not isinstance(value, str) or not _UUID4_RE.fullmatch(value):
        raise ValueError("invalid idempotency_key")
    parsed = uuid.UUID(value)
    if parsed.version != 4 or parsed.variant != uuid.RFC_4122:
        raise ValueError("invalid idempotency_key")
    return value


def _validate_action_id(value) -> str:
    if not isinstance(value, str):
        raise ValueError("invalid action_id")
    match = _ACTION_ID_RE.fullmatch(value)
    if match is None:
        raise ValueError("invalid action_id")
    parsed = uuid.UUID(hex=match.group(1))
    if parsed.version != 4 or parsed.variant != uuid.RFC_4122:
        raise ValueError("invalid action_id")
    return value


def _validate_rfc3339_utc(value, field="timestamp") -> str:
    if not isinstance(value, str) or not _RFC3339_UTC_RE.fullmatch(value):
        raise ValueError("invalid {0}".format(field))
    try:
        datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ValueError("invalid {0}".format(field)) from exc
    return value


def _timestamp(value) -> datetime:
    _validate_rfc3339_utc(value)
    return datetime.fromisoformat(value[:-1] + "+00:00")


def _event_filename(event) -> str:
    sequence = event.get("sequence")
    if isinstance(sequence, bool) or not isinstance(sequence, int) or sequence < 1:
        raise ValueError("invalid sequence")
    event_hash = _validate_sha256(event.get("event_hash"), "event_hash")
    return "{0:012d}_{1}.json".format(sequence, event_hash)


def _validate_safe_id(value, field) -> str:
    try:
        return apply_contract.validate_safe_id(value, field)
    except ValueError as exc:
        raise ValueError("invalid {0}".format(field)) from exc


def _require_exact_fields(event, event_type) -> None:
    expected = _FIELDS_BY_EVENT_TYPE[event_type]
    if set(event) != expected:
        raise ValueError("invalid event fields")


def _validate_common(event) -> None:
    if event["schema_version"] != EVENT_SCHEMA_VERSION:
        raise ValueError("invalid schema_version")
    if event["event_type"] not in _EVENT_TYPES:
        raise ValueError("invalid event_type")

    sequence = event["sequence"]
    if isinstance(sequence, bool) or not isinstance(sequence, int) or sequence < 1:
        raise ValueError("invalid sequence")
    previous_hash = event["previous_event_hash"]
    if sequence == 1:
        if previous_hash is not None:
            raise ValueError("invalid previous_event_hash")
    else:
        _validate_sha256(previous_hash, "previous_event_hash")

    _validate_safe_id(event["project_id"], "project_id")
    _validate_safe_id(event["queue_entry_id"], "queue_entry_id")
    _validate_safe_id(event["candidate_record_id"], "candidate_record_id")
    if event["action_command"] not in _ACTION_COMMANDS:
        raise ValueError("invalid action_command")
    _validate_action_id(event["action_id"])
    _validate_uuid4_key(event["idempotency_key"])
    _validate_sha256(event["request_hash"], "request_hash")
    if event["actor_type"] != "owner" or event["actor_ref"] != "owner-reviewed":
        raise ValueError("invalid actor identity")

    _validate_sha256(event["event_hash"], "event_hash")
    if event["event_hash"] != _event_hash_without_member(event):
        raise ValueError("invalid event_hash")


def _validate_predecessor(event, predecessor) -> None:
    if predecessor is None:
        return
    if not isinstance(predecessor, dict):
        raise ValueError("invalid predecessor")
    predecessor_sequence = predecessor.get("sequence")
    if (
        isinstance(predecessor_sequence, bool)
        or not isinstance(predecessor_sequence, int)
        or event["sequence"] != predecessor_sequence + 1
    ):
        raise ValueError("invalid event sequence")
    if event["previous_event_hash"] != predecessor.get("event_hash"):
        raise ValueError("invalid predecessor hash")
    if event["event_type"] == "action_intent" and predecessor.get("event_type") not in {
        "action_completed",
        "action_recovery_completed",
    }:
        raise ValueError("intent does not follow a completed action")


_ACTION_IDENTITY_FIELDS = (
    "project_id",
    "queue_entry_id",
    "candidate_record_id",
    "action_command",
    "action_id",
    "idempotency_key",
    "request_hash",
    "actor_type",
    "actor_ref",
)


def _validate_action_identity(event, intent) -> None:
    for field in _ACTION_IDENTITY_FIELDS:
        if event[field] != intent[field]:
            raise ValueError("invalid action linkage")


def _validated_intent(intent):
    validated = validate_review_action_event_v1(intent)
    if validated["event_type"] != "action_intent":
        raise ValueError("invalid intent linkage")
    return validated


def _validate_intent(event) -> None:
    _validate_rfc3339_utc(event["created_at"], "created_at")
    if event["completion_state"] != "intent":
        raise ValueError("invalid completion_state")
    for field in (
        "queue_before_hash",
        "target_queue_hash",
        "candidate_before_hash",
        "evidence_projection_before_hash",
    ):
        _validate_sha256(event[field], field)
    for field in (
        "evidence_provenance_preserved",
        "candidate_not_mutated",
        "no_promotion_requested",
        "no_memory_canon_mutation_requested",
    ):
        if event[field] is not True:
            raise ValueError("invalid safety assertion")

    encoded = event["target_queue_canonical_bytes_b64url"]
    if not isinstance(encoded, str) or not _BASE64URL_RE.fullmatch(encoded):
        raise ValueError("invalid target queue encoding")
    try:
        padding = "=" * ((4 - len(encoded) % 4) % 4)
        target_bytes = base64.b64decode(
            encoded + padding, altchars=b"-_", validate=True
        )
        target = apply_contract.strict_json_loads(target_bytes, max_bytes=4_194_304)
    except (ValueError, TypeError) as exc:
        raise ValueError("invalid target queue encoding") from exc
    validated_target = review_queue_storage.validate_review_queue_entry(target)
    if _canonical_json_bytes(validated_target) != target_bytes:
        raise ValueError("target queue bytes are not canonical")
    if hashlib.sha256(target_bytes).hexdigest() != event["target_queue_hash"]:
        raise ValueError("invalid target_queue_hash")
    for event_field, target_field in (
        ("project_id", "project_id"),
        ("queue_entry_id", "queue_entry_id"),
        ("candidate_record_id", "candidate_record_id"),
    ):
        if event[event_field] != validated_target[target_field]:
            raise ValueError("target queue linkage mismatch")
    target_pair = (
        validated_target["review_status"],
        validated_target["lifecycle_state"],
    )
    if event["action_command"] == "mark_duplicate":
        if target_pair != ("duplicate", "duplicate_candidate"):
            raise ValueError("invalid duplicate action target")
        if (
            not isinstance(validated_target.get("duplicate_candidate_ids"), list)
            or len(validated_target["duplicate_candidate_ids"]) != 1
            or validated_target.get("duplicate_target_queue_entry_id") is None
            or validated_target.get("duplicate_target_review_status") is None
            or validated_target.get("duplicate_target_lifecycle_state") is None
            or validated_target.get("duplicate_target_review_version") is None
        ):
            raise ValueError("invalid duplicate action linkage")
    elif target_pair == ("duplicate", "duplicate_candidate"):
        raise ValueError("duplicate target requires mark_duplicate action")
    if event["action_command"] == "mark_split_required":
        if target_pair != ("split_required", "incorrect_cluster_split_required"):
            raise ValueError("invalid split-required action target")
    elif target_pair == ("split_required", "incorrect_cluster_split_required"):
        raise ValueError("split-required target requires mark_split_required action")
    if event["action_command"] == "rename_candidate_metadata":
        if target_pair != ("correction_recorded", "rename_metadata_recorded"):
            raise ValueError("invalid rename-metadata action target")
        if (
            "original_owner_visible_label" not in validated_target
            or validated_target.get("requested_owner_visible_label") is None
            or validated_target.get("owner_visible_label")
            != validated_target.get("requested_owner_visible_label")
        ):
            raise ValueError("invalid rename-metadata action linkage")
    elif target_pair == ("correction_recorded", "rename_metadata_recorded"):
        raise ValueError("rename-metadata target requires explicit action")
    if event["action_command"] == "record_source_linkage_correction":
        if target_pair != (
            "correction_recorded",
            "source_linkage_correction_recorded",
        ):
            raise ValueError("invalid source-link correction action target")
        if (
            validated_target.get("original_source_locator")
            != validated_target.get("source_locator")
            or validated_target.get("requested_source_locator") is None
            or validated_target.get("requested_source_locator")
            == validated_target.get("source_locator")
        ):
            raise ValueError("invalid source-link correction action linkage")
    elif target_pair == (
        "correction_recorded",
        "source_linkage_correction_recorded",
    ):
        raise ValueError("source-link correction target requires explicit action")
    superseding_target_fields = (
        "superseding_target_queue_entry_id",
        "superseding_target_review_status",
        "superseding_target_lifecycle_state",
        "superseding_target_review_version",
    )
    if event["action_command"] == "mark_superseded":
        if target_pair != ("superseded", "superseded_candidate"):
            raise ValueError("invalid supersede action target")
        if (
            validated_target.get("superseded_by_candidate_id") is None
            or any(
                validated_target.get(field) is None
                for field in superseding_target_fields
            )
            or validated_target["superseded_by_candidate_id"]
            == event["candidate_record_id"]
            or validated_target["superseding_target_queue_entry_id"]
            == event["queue_entry_id"]
            or "owner_authored_correction" in validated_target
        ):
            raise ValueError("invalid supersede action linkage")
    elif target_pair == ("superseded", "superseded_candidate"):
        raise ValueError("supersede target requires mark_superseded action")
    if event["action_command"] == "record_owner_authored_correction":
        correction = validated_target.get("owner_authored_correction")
        if target_pair != (
            "correction_recorded",
            "owner_authored_correction_recorded",
        ):
            raise ValueError("invalid owner-authored correction action target")
        if (
            not isinstance(correction, str)
            or not correction.strip()
            or "superseded_by_candidate_id" in validated_target
            or any(field in validated_target for field in superseding_target_fields)
        ):
            raise ValueError("invalid owner-authored correction action linkage")
    elif target_pair == (
        "correction_recorded",
        "owner_authored_correction_recorded",
    ):
        raise ValueError("owner-authored correction target requires explicit action")


def _validate_completed(event, *, intent) -> None:
    intent = _validated_intent(intent)
    _validate_action_identity(event, intent)
    _validate_sha256(event["intent_event_hash"], "intent_event_hash")
    if (
        event["sequence"] != intent["sequence"] + 1
        or event["previous_event_hash"] != intent["event_hash"]
        or event["intent_event_hash"] != intent["event_hash"]
    ):
        raise ValueError("completed event does not directly follow intent")
    for field in (
        "queue_after_hash",
        "candidate_after_hash",
        "evidence_projection_after_hash",
    ):
        _validate_sha256(event[field], field)
    if event["queue_after_hash"] != intent["target_queue_hash"]:
        raise ValueError("invalid queue_after_hash")
    if event["candidate_after_hash"] != intent["candidate_before_hash"]:
        raise ValueError("candidate hash changed")
    if (
        event["evidence_projection_after_hash"]
        != intent["evidence_projection_before_hash"]
    ):
        raise ValueError("evidence projection hash changed")
    _validate_rfc3339_utc(event["completed_at"], "completed_at")
    if _timestamp(event["completed_at"]) < _timestamp(intent["created_at"]):
        raise ValueError("completion precedes intent")
    if event["completion_state"] != "completed":
        raise ValueError("invalid completion_state")


def _validate_failed(event, *, intent) -> None:
    intent = _validated_intent(intent)
    _validate_action_identity(event, intent)
    _validate_sha256(event["intent_event_hash"], "intent_event_hash")
    if (
        event["sequence"] != intent["sequence"] + 1
        or event["previous_event_hash"] != intent["event_hash"]
        or event["intent_event_hash"] != intent["event_hash"]
    ):
        raise ValueError("failed event does not directly follow intent")
    reason = event["failure_reason"]
    if reason not in _FAILURE_REASONS:
        raise ValueError("invalid failure_reason")
    detail = event["failure_detail"]
    if (
        not isinstance(detail, str)
        or not 1 <= len(detail) <= 2_000
        or any(0xD800 <= ord(character) <= 0xDFFF for character in detail)
    ):
        raise ValueError("invalid failure_detail")
    if event["observed_queue_hash"] is not None:
        _validate_sha256(event["observed_queue_hash"], "observed_queue_hash")
    if not isinstance(event["retryable"], bool):
        raise ValueError("invalid retryable")
    expected_retryable = reason in {"QUEUE_WRITE_FAILED", "QUEUE_WRITE_PARTIAL"}
    if event["retryable"] is not expected_retryable:
        raise ValueError("retryability does not match failure_reason")
    _validate_rfc3339_utc(event["failed_at"], "failed_at")
    if _timestamp(event["failed_at"]) < _timestamp(intent["created_at"]):
        raise ValueError("failure precedes intent")
    if event["completion_state"] != "failed":
        raise ValueError("invalid completion_state")


def _validate_recovery_completed(event, *, intent, failed) -> None:
    intent = _validated_intent(intent)
    failed = validate_review_action_event_v1(
        failed, predecessor=intent, intent=intent
    )
    if failed["event_type"] != "action_failed" or failed["retryable"] is not True:
        raise ValueError("invalid failed event linkage")
    _validate_action_identity(event, intent)
    _validate_action_identity(failed, intent)
    _validate_sha256(event["intent_event_hash"], "intent_event_hash")
    _validate_sha256(event["failed_event_hash"], "failed_event_hash")
    if (
        event["sequence"] != failed["sequence"] + 1
        or event["previous_event_hash"] != failed["event_hash"]
        or event["failed_event_hash"] != failed["event_hash"]
        or event["intent_event_hash"] != intent["event_hash"]
    ):
        raise ValueError("recovery event linkage mismatch")
    for field in (
        "queue_after_hash",
        "candidate_after_hash",
        "evidence_projection_after_hash",
    ):
        _validate_sha256(event[field], field)
    if event["queue_after_hash"] != intent["target_queue_hash"]:
        raise ValueError("invalid queue_after_hash")
    if event["candidate_after_hash"] != intent["candidate_before_hash"]:
        raise ValueError("candidate hash changed")
    if (
        event["evidence_projection_after_hash"]
        != intent["evidence_projection_before_hash"]
    ):
        raise ValueError("evidence projection hash changed")
    _validate_rfc3339_utc(event["completed_at"], "completed_at")
    if _timestamp(event["completed_at"]) < _timestamp(failed["failed_at"]):
        raise ValueError("recovery completion precedes failure")
    if event["completion_state"] != "completed":
        raise ValueError("invalid completion_state")


def validate_review_action_event_v1(
    event, *, predecessor=None, intent=None, failed=None
):
    """Validate one complete closed event and its supplied direct linkage."""

    if not isinstance(event, dict):
        raise ValueError("invalid event")
    working = copy.deepcopy(event)
    event_type = working.get("event_type")
    if event_type not in _EVENT_TYPES:
        raise ValueError("invalid event_type")
    _require_exact_fields(working, event_type)
    _validate_common(working)
    _validate_predecessor(working, predecessor)

    if event_type == "action_intent":
        _validate_intent(working)
    elif event_type == "action_completed":
        if intent is None:
            raise ValueError("missing intent linkage")
        _validate_completed(working, intent=intent)
        if predecessor is not None and predecessor.get("event_hash") != intent.get(
            "event_hash"
        ):
            raise ValueError("completed event predecessor is not its intent")
    elif event_type == "action_failed":
        if intent is None:
            raise ValueError("missing intent linkage")
        _validate_failed(working, intent=intent)
        if predecessor is not None and predecessor.get("event_hash") != intent.get(
            "event_hash"
        ):
            raise ValueError("failed event predecessor is not its intent")
    else:
        if intent is None or failed is None:
            raise ValueError("missing recovery linkage")
        _validate_recovery_completed(working, intent=intent, failed=failed)
        if predecessor is not None and predecessor.get("event_hash") != failed.get(
            "event_hash"
        ):
            raise ValueError("recovery predecessor is not its failure")
    return working


def _seal_event(event, **validation_context):
    sealed = dict(event)
    sealed["event_hash"] = _event_hash_without_member(sealed)
    return validate_review_action_event_v1(sealed, **validation_context)


def _common_from_intent(intent, *, event_type, sequence, previous_event_hash):
    return {
        "schema_version": EVENT_SCHEMA_VERSION,
        "event_type": event_type,
        "sequence": sequence,
        "previous_event_hash": previous_event_hash,
        **{field: intent[field] for field in _ACTION_IDENTITY_FIELDS},
    }


def build_action_intent_event_v1(
    *,
    sequence,
    previous_event_hash,
    project_id,
    queue_entry_id,
    candidate_record_id,
    action_command,
    action_id,
    idempotency_key,
    request_hash,
    created_at,
    queue_before_hash,
    target_queue_canonical_bytes_b64url,
    target_queue_hash,
    candidate_before_hash,
    evidence_projection_before_hash,
    predecessor=None,
):
    event = {
        "schema_version": EVENT_SCHEMA_VERSION,
        "event_type": "action_intent",
        "sequence": sequence,
        "previous_event_hash": previous_event_hash,
        "project_id": project_id,
        "queue_entry_id": queue_entry_id,
        "candidate_record_id": candidate_record_id,
        "action_command": action_command,
        "action_id": action_id,
        "idempotency_key": idempotency_key,
        "request_hash": request_hash,
        "actor_type": "owner",
        "actor_ref": "owner-reviewed",
        "created_at": created_at,
        "completion_state": "intent",
        "queue_before_hash": queue_before_hash,
        "target_queue_canonical_bytes_b64url": target_queue_canonical_bytes_b64url,
        "target_queue_hash": target_queue_hash,
        "candidate_before_hash": candidate_before_hash,
        "evidence_projection_before_hash": evidence_projection_before_hash,
        "evidence_provenance_preserved": True,
        "candidate_not_mutated": True,
        "no_promotion_requested": True,
        "no_memory_canon_mutation_requested": True,
    }
    return _seal_event(event, predecessor=predecessor)


def build_action_completed_event_v1(
    *,
    intent,
    queue_after_hash,
    candidate_after_hash,
    evidence_projection_after_hash,
    completed_at,
    sequence=None,
    previous_event_hash=None,
):
    intent = _validated_intent(intent)
    sequence = intent["sequence"] + 1 if sequence is None else sequence
    previous_event_hash = (
        intent["event_hash"] if previous_event_hash is None else previous_event_hash
    )
    event = {
        **_common_from_intent(
            intent,
            event_type="action_completed",
            sequence=sequence,
            previous_event_hash=previous_event_hash,
        ),
        "intent_event_hash": intent["event_hash"],
        "queue_after_hash": queue_after_hash,
        "candidate_after_hash": candidate_after_hash,
        "evidence_projection_after_hash": evidence_projection_after_hash,
        "completed_at": completed_at,
        "completion_state": "completed",
    }
    return _seal_event(event, predecessor=intent, intent=intent)


def build_action_failed_event_v1(
    *,
    intent,
    failure_reason,
    failure_detail,
    observed_queue_hash,
    retryable,
    failed_at,
    sequence=None,
    previous_event_hash=None,
):
    intent = _validated_intent(intent)
    sequence = intent["sequence"] + 1 if sequence is None else sequence
    previous_event_hash = (
        intent["event_hash"] if previous_event_hash is None else previous_event_hash
    )
    event = {
        **_common_from_intent(
            intent,
            event_type="action_failed",
            sequence=sequence,
            previous_event_hash=previous_event_hash,
        ),
        "intent_event_hash": intent["event_hash"],
        "failure_reason": failure_reason,
        "failure_detail": failure_detail,
        "observed_queue_hash": observed_queue_hash,
        "retryable": retryable,
        "failed_at": failed_at,
        "completion_state": "failed",
    }
    return _seal_event(event, predecessor=intent, intent=intent)


def build_action_recovery_completed_event_v1(
    *,
    intent,
    failed,
    queue_after_hash,
    candidate_after_hash,
    evidence_projection_after_hash,
    completed_at,
    sequence=None,
    previous_event_hash=None,
):
    intent = _validated_intent(intent)
    failed = validate_review_action_event_v1(
        failed, predecessor=intent, intent=intent
    )
    sequence = failed["sequence"] + 1 if sequence is None else sequence
    previous_event_hash = (
        failed["event_hash"] if previous_event_hash is None else previous_event_hash
    )
    event = {
        **_common_from_intent(
            intent,
            event_type="action_recovery_completed",
            sequence=sequence,
            previous_event_hash=previous_event_hash,
        ),
        "intent_event_hash": intent["event_hash"],
        "failed_event_hash": failed["event_hash"],
        "queue_after_hash": queue_after_hash,
        "candidate_after_hash": candidate_after_hash,
        "evidence_projection_after_hash": evidence_projection_after_hash,
        "completed_at": completed_at,
        "completion_state": "completed",
    }
    return _seal_event(
        event, predecessor=failed, intent=intent, failed=failed
    )


def review_action_events_dir(*, project_dir, queue_entry_id):
    queue_entry_id = _validate_safe_id(queue_entry_id, "queue_entry_id")
    return (
        Path(project_dir)
        / "writer_assistant"
        / "review_queue"
        / "actions"
        / queue_entry_id
        / "events"
    )


def scan_review_action_event_chain(
    *, project_dir, project_id, queue_entry_id
):
    """Return the fully validated event chain or fail closed on any corruption."""

    project_id = _validate_safe_id(project_id, "project_id")
    queue_entry_id = _validate_safe_id(queue_entry_id, "queue_entry_id")
    events_dir = review_action_events_dir(
        project_dir=project_dir, queue_entry_id=queue_entry_id
    )
    try:
        directory_metadata = os.lstat(events_dir)
    except FileNotFoundError:
        return []
    if stat.S_ISLNK(directory_metadata.st_mode) or not stat.S_ISDIR(
        directory_metadata.st_mode
    ):
        raise ValueError("invalid event directory")

    items = sorted(events_dir.iterdir(), key=lambda item: item.name)
    validated_chain = []
    events_by_hash = {}
    intent_keys = set()
    action_ids = set()
    for item in items:
        metadata = os.lstat(item)
        if (
            stat.S_ISLNK(metadata.st_mode)
            or not stat.S_ISREG(metadata.st_mode)
            or metadata.st_nlink != 1
        ):
            raise ValueError("invalid event file")
        filename_match = _EVENT_FILENAME_RE.fullmatch(item.name)
        if filename_match is None:
            raise ValueError("invalid event filename")
        raw = item.read_bytes()
        try:
            event = apply_contract.strict_json_loads(raw, max_bytes=4_194_304)
        except ValueError as exc:
            raise ValueError("invalid event JSON") from exc
        if not isinstance(event, dict) or _canonical_json_bytes(event) != raw:
            raise ValueError("invalid event canonical bytes")

        predecessor = validated_chain[-1] if validated_chain else None
        event_type = event.get("event_type")
        intent = None
        failed = None
        if event_type in {"action_completed", "action_failed"}:
            intent = predecessor
        elif event_type == "action_recovery_completed":
            failed = predecessor
            intent = events_by_hash.get(event.get("intent_event_hash"))
        validated = validate_review_action_event_v1(
            event, predecessor=predecessor, intent=intent, failed=failed
        )
        if validated["sequence"] != len(validated_chain) + 1:
            raise ValueError("event chain sequence is not contiguous")
        if (
            validated["project_id"] != project_id
            or validated["queue_entry_id"] != queue_entry_id
        ):
            raise ValueError("event storage linkage mismatch")
        if int(filename_match.group(1)) != validated["sequence"]:
            raise ValueError("event filename sequence mismatch")
        if filename_match.group(2) != validated["event_hash"]:
            raise ValueError("event filename hash mismatch")
        if item.name != _event_filename(validated):
            raise ValueError("invalid event filename")

        if event_type == "action_intent":
            key = validated["idempotency_key"]
            action_id = validated["action_id"]
            if key in intent_keys or action_id in action_ids:
                raise ValueError("duplicate action identity")
            intent_keys.add(key)
            action_ids.add(action_id)
        validated_chain.append(validated)
        events_by_hash[validated["event_hash"]] = validated

    return validated_chain


def publish_review_action_event(event, *, project_dir, queue_entry_id):
    """Validate and immutably publish exactly the next event in one chain."""

    if not isinstance(event, dict):
        raise ValueError("invalid event")
    queue_entry_id = _validate_safe_id(queue_entry_id, "queue_entry_id")
    if event.get("queue_entry_id") != queue_entry_id:
        raise ValueError("event queue_entry_id mismatch")
    project_id = _validate_safe_id(event.get("project_id"), "project_id")
    chain = scan_review_action_event_chain(
        project_dir=project_dir,
        project_id=project_id,
        queue_entry_id=queue_entry_id,
    )
    predecessor = chain[-1] if chain else None
    event_type = event.get("event_type")
    intent = None
    failed = None
    if event_type in {"action_completed", "action_failed"}:
        intent = predecessor
    elif event_type == "action_recovery_completed":
        failed = predecessor
        intent = next(
            (
                item
                for item in chain
                if item["event_hash"] == event.get("intent_event_hash")
            ),
            None,
        )
    validated = validate_review_action_event_v1(
        event, predecessor=predecessor, intent=intent, failed=failed
    )
    if validated["sequence"] != len(chain) + 1:
        raise ValueError("event is not the next sequence")

    filename = _event_filename(validated)
    relative = (
        Path("writer_assistant")
        / "review_queue"
        / "actions"
        / queue_entry_id
        / "events"
        / filename
    )
    if (Path(project_dir) / relative).exists():
        raise apply_contract.ApplyContractError("REVIEW_ACTION_EVENT_CONFLICT")
    replayed = apply_contract.publish_immutable_file(
        project_dir,
        relative,
        _canonical_json_bytes(validated),
        conflict_code="REVIEW_ACTION_EVENT_CONFLICT",
    )
    if replayed:
        raise apply_contract.ApplyContractError("REVIEW_ACTION_EVENT_CONFLICT")
    return validated


@contextmanager
def acquire_review_action_lock(
    *, trusted_runtime_dir: Path, project_id: str, queue_entry_id: str
):
    """Acquire one injected-runtime entry lock without waiting."""

    if not isinstance(trusted_runtime_dir, Path):
        raise TypeError("trusted_runtime_dir must be a Path")
    project_id = _validate_safe_id(project_id, "project_id")
    queue_entry_id = _validate_safe_id(queue_entry_id, "queue_entry_id")
    digest = hashlib.sha256(
        (project_id + "/" + queue_entry_id).encode("utf-8")
    ).hexdigest()
    filename = "review-queue-{0}.lock".format(digest)
    process_key = (trusted_runtime_dir, digest)
    with _PROCESS_LOCKS_GUARD:
        process_lock = _PROCESS_LOCKS.setdefault(process_key, threading.Lock())
    if not process_lock.acquire(blocking=False):
        raise BlockingIOError(errno.EWOULDBLOCK, "review action lock unavailable")

    root_descriptor = None
    lock_directory_descriptor = None
    lock_descriptor = None
    file_locked = False
    try:
        root_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW
        root_descriptor = os.open(trusted_runtime_dir, root_flags)
        try:
            os.mkdir("review-queue-locks", mode=0o700, dir_fd=root_descriptor)
        except FileExistsError:
            pass
        directory_metadata = os.stat(
            "review-queue-locks", dir_fd=root_descriptor, follow_symlinks=False
        )
        if (
            not stat.S_ISDIR(directory_metadata.st_mode)
            or directory_metadata.st_uid != os.getuid()
            or stat.S_IMODE(directory_metadata.st_mode) & 0o077
        ):
            raise ValueError("unsafe review action lock directory")

        lock_directory_descriptor = os.open(
            "review-queue-locks", root_flags, dir_fd=root_descriptor
        )
        lock_flags = os.O_CREAT | os.O_RDWR | os.O_CLOEXEC | os.O_NOFOLLOW
        lock_descriptor = os.open(
            filename, lock_flags, 0o600, dir_fd=lock_directory_descriptor
        )
        lock_metadata = os.fstat(lock_descriptor)
        if (
            not stat.S_ISREG(lock_metadata.st_mode)
            or lock_metadata.st_size != 0
            or lock_metadata.st_uid != os.getuid()
            or stat.S_IMODE(lock_metadata.st_mode) != 0o600
            or lock_metadata.st_nlink != 1
        ):
            raise ValueError("unsafe review action lock file")
        try:
            fcntl.flock(lock_descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise BlockingIOError(
                errno.EWOULDBLOCK, "review action lock unavailable"
            ) from exc
        file_locked = True
        yield trusted_runtime_dir / "review-queue-locks" / filename
    finally:
        if file_locked and lock_descriptor is not None:
            fcntl.flock(lock_descriptor, fcntl.LOCK_UN)
        if lock_descriptor is not None:
            os.close(lock_descriptor)
        if lock_directory_descriptor is not None:
            os.close(lock_directory_descriptor)
        if root_descriptor is not None:
            os.close(root_descriptor)
        process_lock.release()


__all__ = (
    "build_action_intent_event_v1",
    "build_action_completed_event_v1",
    "build_action_failed_event_v1",
    "build_action_recovery_completed_event_v1",
    "validate_review_action_event_v1",
    "review_action_events_dir",
    "scan_review_action_event_chain",
    "publish_review_action_event",
    "acquire_review_action_lock",
)
