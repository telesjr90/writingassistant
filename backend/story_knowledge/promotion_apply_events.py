"""Deterministic append-only v2 promotion apply event storage."""

from __future__ import annotations

import hashlib
import os
import re
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from backend.story_knowledge.apply_contract import (
    ApplyContractError,
    MAX_APPROVED_RECORD_BYTES,
    MAX_PREPARATION_BYTES,
    MAX_REVISION_BYTES,
    canonical_json_bytes,
    canonical_sha256,
    preparation_relative_path,
    publish_immutable_file,
    require_closed_object,
    require_integer,
    require_string,
    revision_relative_path,
    sealed_revision_relative_path,
    strict_json_loads,
    validate_field_id,
    validate_owner_identity,
    validate_safe_id,
    validate_sha256,
    validate_timestamp,
    validate_uuid_v4,
)
from backend.story_knowledge.approved_records import (
    approved_record_relative_path,
)


MAX_EVENT_BYTES = 16_384
MAX_EVENT_SEQUENCE = 4_096
EVENT_VERSION = "promotion_apply_event.v2"
EVENT_SCOPE_VERSION = "promotion-apply-event-scope.v2"

_EVENT_FILE_RE = re.compile(r"^([0-9]{12})_([a-f0-9]{64})\.json$")
_TEMP_FILE_RE = re.compile(
    r"^\.tmp-[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$"
)
_APPLY_ID_RE = re.compile(r"^apply_[a-f0-9]{32}$")
_CHALLENGE_ID_RE = re.compile(r"^challenge_[a-f0-9]{16}_[a-f0-9]{64}$")

_BASE_FIELDS = {
    "object_kind",
    "event_version",
    "event_type",
    "event_id",
    "sequence",
    "previous_event_hash",
    "project_id",
    "promotion_id",
    "candidate_id",
    "revision",
    "idempotency_key",
    "operation_identity",
    "event_scope_hash",
    "created_at",
    "event_filename",
    "event_path",
    "event_content_hash",
}

_EVENT_FIELDS: dict[str, set[str]] = {
    "draft_preparation_started": {
        "preparation_id", "preparation_path", "preparation_artifact_hash",
        "preparation_artifact_size", "preparation_scope_hash",
        "canonical_request_body_hash", "expected_latest_revision",
        "expected_latest_draft_scope_hash", "assigned_revision",
        "planned_draft_scope_hash", "revision_path", "revision_canonical_hash",
        "revision_canonical_size", "approved_record_hash", "approved_record_size",
        "authoritative_owner_actor", "supersession_kind",
    },
    "draft_prepared": {
        "preparation_id", "preparation_path", "preparation_artifact_hash",
        "preparation_start_event_id", "preparation_scope_hash", "revision_path",
        "revision_canonical_hash", "revision_canonical_size", "draft_scope_hash",
        "approved_record_hash", "approved_record_size",
    },
    "draft_superseded": {
        "preparation_id", "preparation_scope_hash", "superseded_revision",
        "superseding_revision", "superseded_draft_scope_hash",
        "superseding_draft_scope_hash", "authoritative_owner_actor", "rationale",
    },
    "contract_approval_recorded": {
        "approval_scope_hash", "draft_scope_hash", "contract_approval",
    },
    "contract_approved": {
        "draft_scope_hash", "sealed_contract_hash", "approval_event_id",
        "sealed_revision_path",
    },
    "contract_revoked": {
        "sealed_contract_hash", "authoritative_owner_actor", "rationale",
    },
    "contract_superseded": {
        "preparation_id", "preparation_scope_hash", "superseded_revision",
        "superseding_revision", "sealed_contract_hash",
        "superseding_draft_scope_hash", "authoritative_owner_actor", "rationale",
    },
    "apply_intent": {
        "apply_id", "final_apply_scope_hash", "sealed_contract_hash", "operation",
        "destination_type", "destination_key", "destination_path",
        "before_state_snapshot_token", "before_state_version",
        "before_state_content_hash", "approved_record_hash", "approved_record_size",
        "sealed_revision_path", "approval_event_id", "seal_event_id",
        "authoritative_owner_actor", "final_confirmation_id", "challenge_id",
        "confirmed_at",
    },
    "apply_completed": {
        "apply_id", "intent_event_id", "sealed_contract_hash", "destination_path",
        "approved_record_hash", "approved_record_size", "approved_record_version",
        "completed_at",
    },
    "apply_failed_before_commit": {
        "apply_id", "intent_event_id", "outcome", "error_code",
    },
    "recovery_required": {
        "apply_id", "intent_event_id", "outcome", "error_code",
        "observed_record_hash", "observed_record_size", "observed_record_version",
    },
    "recovery_completed": {
        "apply_id", "intent_event_id", "recovery_required_event_id", "outcome",
        "error_code", "approved_record_hash", "approved_record_size",
        "approved_record_version",
    },
}

# Exact values retained in each accepted event-specific scope. Universal identity
# and operation fields are added by _event_scope_document.
_SCOPE_FIELDS: dict[str, tuple[str, ...]] = {
    "draft_preparation_started": (
        "preparation_id", "preparation_path", "preparation_artifact_hash",
        "preparation_artifact_size", "preparation_scope_hash", "assigned_revision",
        "revision_path", "revision_canonical_hash", "revision_canonical_size",
        "planned_draft_scope_hash", "expected_latest_revision",
        "expected_latest_draft_scope_hash", "supersession_kind",
    ),
    "draft_prepared": (
        "preparation_id", "preparation_path", "preparation_artifact_hash",
        "preparation_start_event_id", "preparation_scope_hash", "revision_path",
        "revision_canonical_hash", "revision_canonical_size", "draft_scope_hash",
    ),
    "draft_superseded": (
        "preparation_id", "preparation_scope_hash", "superseded_revision",
        "superseding_revision", "superseded_draft_scope_hash",
        "superseding_draft_scope_hash", "authoritative_owner_actor",
    ),
    "contract_approval_recorded": (
        "approval_scope_hash", "draft_scope_hash", "contract_approval",
    ),
    "contract_approved": (
        "draft_scope_hash", "sealed_contract_hash", "approval_event_id",
        "sealed_revision_path",
    ),
    "contract_revoked": ("sealed_contract_hash", "authoritative_owner_actor"),
    "contract_superseded": (
        "preparation_id", "preparation_scope_hash", "superseded_revision",
        "superseding_revision", "sealed_contract_hash",
        "superseding_draft_scope_hash", "authoritative_owner_actor",
    ),
    "apply_intent": (
        "apply_id", "final_apply_scope_hash", "sealed_contract_hash", "operation",
        "destination_type", "destination_key", "destination_path",
        "before_state_snapshot_token", "before_state_version",
        "before_state_content_hash", "approved_record_hash", "approved_record_size",
        "sealed_revision_path", "approval_event_id", "seal_event_id",
        "authoritative_owner_actor", "final_confirmation_id", "challenge_id",
        "confirmed_at",
    ),
    "apply_completed": (
        "apply_id", "intent_event_id", "sealed_contract_hash", "destination_path",
        "approved_record_hash", "approved_record_size", "approved_record_version",
        "completed_at",
    ),
    "apply_failed_before_commit": ("apply_id", "intent_event_id", "outcome", "error_code"),
    "recovery_required": (
        "apply_id", "intent_event_id", "outcome", "error_code",
        "observed_record_hash", "observed_record_size", "observed_record_version",
    ),
    "recovery_completed": (
        "apply_id", "intent_event_id", "recovery_required_event_id", "outcome",
        "error_code", "approved_record_hash", "approved_record_size",
        "approved_record_version",
    ),
}


@dataclass(frozen=True)
class EventChain:
    events: tuple[dict[str, Any], ...]
    temporary_residue: tuple[str, ...]


@dataclass(frozen=True)
class EventPublication:
    event: dict[str, Any]
    replayed: bool


def event_directory_relative_path(promotion_id: str) -> Path:
    validate_safe_id(promotion_id, "promotion_id")
    return Path("writer_assistant", "promotion_audits", promotion_id, "events")


def event_relative_path(promotion_id: str, sequence: int, event_id: str) -> Path:
    require_integer(sequence, label="sequence", minimum=1, maximum=MAX_EVENT_SEQUENCE)
    validate_sha256(event_id, "event_id")
    filename = f"{sequence:012d}_{event_id}.json"
    relative = event_directory_relative_path(promotion_id) / filename
    if len(relative.as_posix().encode("utf-8")) > 320:
        raise ApplyContractError("APPLY_EVENT_PATH_ESCAPE")
    return relative


def _event_scope_document(
    *,
    event_type: str,
    project_id: str,
    promotion_id: str,
    candidate_id: str,
    revision: int | None,
    idempotency_key: str | None,
    operation_identity: str,
    content: dict[str, Any],
) -> dict[str, Any]:
    scope: dict[str, Any] = {
        "scope_version": EVENT_SCOPE_VERSION,
        "event_type": event_type,
        "project_id": project_id,
        "promotion_id": promotion_id,
        "candidate_id": candidate_id,
        "operation_identity": operation_identity,
        "idempotency_key": idempotency_key,
        "revision": revision,
    }
    for field in _SCOPE_FIELDS[event_type]:
        scope[field] = content[field]
    if "rationale" in content:
        scope["rationale_hash"] = canonical_sha256(content["rationale"])
    return scope


def event_scope_hash(
    *,
    event_type: str,
    project_id: str,
    promotion_id: str,
    candidate_id: str,
    revision: int | None,
    idempotency_key: str | None,
    operation_identity: str,
    content: dict[str, Any],
) -> str:
    if event_type not in _EVENT_FIELDS:
        raise ApplyContractError("APPLY_EVENT_UNKNOWN_TYPE")
    require_closed_object(content, required=_EVENT_FIELDS[event_type], label=f"{event_type} event content")
    return canonical_sha256(
        _event_scope_document(
            event_type=event_type,
            project_id=project_id,
            promotion_id=promotion_id,
            candidate_id=candidate_id,
            revision=revision,
            idempotency_key=idempotency_key,
            operation_identity=operation_identity,
            content=content,
        )
    )


def event_id_preimage(event: dict[str, Any]) -> dict[str, Any]:
    return {
        "event_version": event["event_version"],
        "event_type": event["event_type"],
        "project_id": event["project_id"],
        "promotion_id": event["promotion_id"],
        "candidate_id": event["candidate_id"],
        "revision": event["revision"],
        "sequence": event["sequence"],
        "previous_event_hash": event["previous_event_hash"],
        "idempotency_key": event["idempotency_key"],
        "operation_identity": event["operation_identity"],
        "event_scope_hash": event["event_scope_hash"],
        "created_at": event["created_at"],
    }


def _content_without_hash(event: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in event.items() if key != "event_content_hash"}


def _nullable_hash(value: Any, field: str) -> None:
    if value is not None:
        validate_sha256(value, field)


def _nullable_integer(
    value: Any, field: str, *, minimum: int, maximum: int
) -> None:
    if value is not None:
        require_integer(value, label=field, minimum=minimum, maximum=maximum)


def _validate_apply_id(value: Any) -> str:
    if not isinstance(value, str) or not _APPLY_ID_RE.fullmatch(value):
        raise ApplyContractError("INVALID_SAFE_ID", "apply_id")
    return value


def _validate_challenge_id(value: Any) -> str:
    if not isinstance(value, str) or not _CHALLENGE_ID_RE.fullmatch(value):
        raise ApplyContractError("INVALID_SAFE_ID", "challenge_id")
    return value


def _validate_contract_approval(value: Any, event: dict[str, Any]) -> None:
    approval = require_closed_object(
        value,
        required={
            "owner_actor", "project_id", "promotion_id", "revision",
            "draft_scope_hash", "before_state_snapshot_token",
            "approval_method", "approved_at",
        },
        label="contract approval",
    )
    validate_owner_identity(approval["owner_actor"])
    if (
        approval["project_id"] != event["project_id"]
        or approval["promotion_id"] != event["promotion_id"]
        or approval["revision"] != event["revision"]
        or approval["draft_scope_hash"] != event["draft_scope_hash"]
    ):
        raise ApplyContractError("PROMOTION_ASSOCIATION_INVALID")
    validate_sha256(approval["draft_scope_hash"], "draft_scope_hash")
    validate_sha256(
        approval["before_state_snapshot_token"], "before_state_snapshot_token"
    )
    if approval["approval_method"] != "explicit_apply_contract_approval":
        raise ApplyContractError("SCHEMA_STRING_INVALID", "approval_method")
    validate_timestamp(approval["approved_at"], "approved_at")


def _validate_event_content_semantics(event: dict[str, Any]) -> None:
    """Validate the closed event variant, not only its self-consistent hashes."""

    event_type = event["event_type"]
    revision = event["revision"]
    key = event["idempotency_key"]
    if revision is None or key is None:
        raise ApplyContractError("SCHEMA_REQUIRED_FIELD_MISSING")
    promotion_id = event["promotion_id"]

    if event_type == "draft_preparation_started":
        expected_preparation_path = preparation_relative_path(
            promotion_id, event["preparation_id"]
        ).as_posix()
        if event["preparation_path"] != expected_preparation_path:
            raise ApplyContractError("APPLY_EVENT_PATH_ESCAPE")
        for field in (
            "preparation_artifact_hash", "preparation_scope_hash",
            "canonical_request_body_hash", "planned_draft_scope_hash",
            "revision_canonical_hash", "approved_record_hash",
        ):
            validate_sha256(event[field], field)
        require_integer(
            event["preparation_artifact_size"],
            label="preparation_artifact_size", minimum=1,
            maximum=MAX_PREPARATION_BYTES,
        )
        _nullable_integer(
            event["expected_latest_revision"], "expected_latest_revision",
            minimum=1, maximum=255,
        )
        _nullable_hash(
            event["expected_latest_draft_scope_hash"],
            "expected_latest_draft_scope_hash",
        )
        require_integer(
            event["assigned_revision"], label="assigned_revision",
            minimum=1, maximum=256,
        )
        if event["assigned_revision"] != revision:
            raise ApplyContractError("PROMOTION_ASSOCIATION_INVALID")
        if event["revision_path"] != revision_relative_path(
            promotion_id, revision
        ).as_posix():
            raise ApplyContractError("APPLY_EVENT_PATH_ESCAPE")
        require_integer(
            event["revision_canonical_size"], label="revision_canonical_size",
            minimum=1, maximum=MAX_REVISION_BYTES,
        )
        require_integer(
            event["approved_record_size"], label="approved_record_size",
            minimum=1, maximum=MAX_APPROVED_RECORD_BYTES,
        )
        validate_owner_identity(event["authoritative_owner_actor"])
        if event["supersession_kind"] not in {"none", "draft", "sealed"}:
            raise ApplyContractError("SCHEMA_STRING_INVALID", "supersession_kind")
        return

    if event_type == "draft_prepared":
        if event["preparation_path"] != preparation_relative_path(
            promotion_id, event["preparation_id"]
        ).as_posix():
            raise ApplyContractError("APPLY_EVENT_PATH_ESCAPE")
        for field in (
            "preparation_artifact_hash", "preparation_start_event_id",
            "preparation_scope_hash", "revision_canonical_hash",
            "draft_scope_hash", "approved_record_hash",
        ):
            validate_sha256(event[field], field)
        if event["revision_path"] != revision_relative_path(
            promotion_id, revision
        ).as_posix():
            raise ApplyContractError("APPLY_EVENT_PATH_ESCAPE")
        require_integer(
            event["revision_canonical_size"], label="revision_canonical_size",
            minimum=1, maximum=MAX_REVISION_BYTES,
        )
        require_integer(
            event["approved_record_size"], label="approved_record_size",
            minimum=1, maximum=MAX_APPROVED_RECORD_BYTES,
        )
        return

    if event_type in {"draft_superseded", "contract_superseded"}:
        preparation_relative_path(promotion_id, event["preparation_id"])
        validate_sha256(event["preparation_scope_hash"], "preparation_scope_hash")
        old_revision = require_integer(
            event["superseded_revision"], label="superseded_revision",
            minimum=1, maximum=255,
        )
        new_revision = require_integer(
            event["superseding_revision"], label="superseding_revision",
            minimum=2, maximum=256,
        )
        if new_revision != revision or new_revision <= old_revision:
            raise ApplyContractError("PROMOTION_ASSOCIATION_INVALID")
        if event_type == "draft_superseded":
            validate_sha256(
                event["superseded_draft_scope_hash"],
                "superseded_draft_scope_hash",
            )
        else:
            validate_sha256(event["sealed_contract_hash"], "sealed_contract_hash")
        validate_sha256(
            event["superseding_draft_scope_hash"],
            "superseding_draft_scope_hash",
        )
        validate_owner_identity(event["authoritative_owner_actor"])
        require_string(
            event["rationale"], label="rationale", minimum=1, maximum=4096
        )
        return

    if event_type == "contract_approval_recorded":
        validate_sha256(event["approval_scope_hash"], "approval_scope_hash")
        validate_sha256(event["draft_scope_hash"], "draft_scope_hash")
        _validate_contract_approval(event["contract_approval"], event)
        return

    if event_type == "contract_approved":
        for field in (
            "draft_scope_hash", "sealed_contract_hash", "approval_event_id"
        ):
            validate_sha256(event[field], field)
        if event["sealed_revision_path"] != sealed_revision_relative_path(
            promotion_id, revision
        ).as_posix():
            raise ApplyContractError("APPLY_EVENT_PATH_ESCAPE")
        return

    if event_type == "contract_revoked":
        validate_sha256(event["sealed_contract_hash"], "sealed_contract_hash")
        validate_owner_identity(event["authoritative_owner_actor"])
        require_string(
            event["rationale"], label="rationale", minimum=1, maximum=4096
        )
        return

    if event_type == "apply_intent":
        apply_id = _validate_apply_id(event["apply_id"])
        if event["operation_identity"] != apply_id:
            raise ApplyContractError("PROMOTION_ASSOCIATION_INVALID")
        for field in (
            "final_apply_scope_hash", "sealed_contract_hash",
            "before_state_snapshot_token", "approved_record_hash",
            "approval_event_id", "seal_event_id", "final_confirmation_id",
        ):
            validate_sha256(event[field], field)
        if event["operation"] not in {"create", "update"}:
            raise ApplyContractError("APPLY_OPERATION_INVALID")
        expected_destination = approved_record_relative_path(
            event["destination_type"], event["destination_key"]
        ).as_posix()
        if event["destination_path"] != expected_destination:
            raise ApplyContractError("APPLY_EVENT_PATH_ESCAPE")
        _nullable_integer(
            event["before_state_version"], "before_state_version",
            minimum=1, maximum=2_147_483_647,
        )
        _nullable_hash(
            event["before_state_content_hash"], "before_state_content_hash"
        )
        if event["operation"] == "create" and any(
            event[field] is not None
            for field in ("before_state_version", "before_state_content_hash")
        ):
            raise ApplyContractError("APPLY_CONTRACT_BEFORE_STATE_INVALID")
        if event["operation"] == "update" and any(
            event[field] is None
            for field in ("before_state_version", "before_state_content_hash")
        ):
            raise ApplyContractError("APPLY_CONTRACT_BEFORE_STATE_INVALID")
        require_integer(
            event["approved_record_size"], label="approved_record_size",
            minimum=1, maximum=MAX_APPROVED_RECORD_BYTES,
        )
        if event["sealed_revision_path"] != sealed_revision_relative_path(
            promotion_id, revision
        ).as_posix():
            raise ApplyContractError("APPLY_EVENT_PATH_ESCAPE")
        validate_owner_identity(event["authoritative_owner_actor"])
        _validate_challenge_id(event["challenge_id"])
        validate_timestamp(event["confirmed_at"], "confirmed_at")
        return

    apply_id = _validate_apply_id(event["apply_id"])
    if event["operation_identity"] != apply_id:
        raise ApplyContractError("PROMOTION_ASSOCIATION_INVALID")
    validate_sha256(event["intent_event_id"], "intent_event_id")
    if event_type == "apply_completed":
        validate_sha256(event["sealed_contract_hash"], "sealed_contract_hash")
        require_string(
            event["destination_path"], label="destination_path",
            minimum=1, maximum=320,
        )
        validate_sha256(event["approved_record_hash"], "approved_record_hash")
        require_integer(
            event["approved_record_size"], label="approved_record_size",
            minimum=1, maximum=MAX_APPROVED_RECORD_BYTES,
        )
        require_integer(
            event["approved_record_version"], label="approved_record_version",
            minimum=1, maximum=2_147_483_647,
        )
        validate_timestamp(event["completed_at"], "completed_at")
        return
    validate_field_id(event["error_code"], "error_code")
    if event_type == "apply_failed_before_commit":
        if event["outcome"] != "not_committed":
            raise ApplyContractError("SCHEMA_STRING_INVALID", "outcome")
        return
    if event_type == "recovery_required":
        if event["outcome"] != "unclassified":
            raise ApplyContractError("SCHEMA_STRING_INVALID", "outcome")
        _nullable_hash(event["observed_record_hash"], "observed_record_hash")
        _nullable_integer(
            event["observed_record_size"], "observed_record_size",
            minimum=1, maximum=MAX_APPROVED_RECORD_BYTES,
        )
        _nullable_integer(
            event["observed_record_version"], "observed_record_version",
            minimum=1, maximum=2_147_483_647,
        )
        return
    if event["outcome"] not in {"committed", "not_committed"}:
        raise ApplyContractError("SCHEMA_STRING_INVALID", "outcome")
    _nullable_hash(
        event["recovery_required_event_id"], "recovery_required_event_id"
    )
    if event["outcome"] == "committed":
        validate_sha256(event["approved_record_hash"], "approved_record_hash")
        require_integer(
            event["approved_record_size"], label="approved_record_size",
            minimum=1, maximum=MAX_APPROVED_RECORD_BYTES,
        )
        require_integer(
            event["approved_record_version"], label="approved_record_version",
            minimum=1, maximum=2_147_483_647,
        )
    elif any(
        event[field] is not None
        for field in (
            "approved_record_hash", "approved_record_size",
            "approved_record_version",
        )
    ):
        raise ApplyContractError("SCHEMA_TYPE_MISMATCH", "recovery record pair")


def _validate_event_semantics(event: dict[str, Any]) -> None:
    event_type = event.get("event_type")
    if event_type not in _EVENT_FIELDS:
        raise ApplyContractError("APPLY_EVENT_UNKNOWN_TYPE")
    require_closed_object(event, required=_BASE_FIELDS | _EVENT_FIELDS[event_type], label="promotion apply event")
    if event["object_kind"] != "promotion_apply_event":
        raise ApplyContractError("APPLY_EVENT_MALFORMED")
    if event["event_version"] != EVENT_VERSION:
        raise ApplyContractError("APPLY_EVENT_UNSUPPORTED_VERSION")
    for field in ("project_id", "promotion_id", "candidate_id", "operation_identity"):
        validate_safe_id(event[field], field)
    sequence = require_integer(event["sequence"], label="sequence", minimum=1, maximum=MAX_EVENT_SEQUENCE)
    if event["revision"] is not None:
        require_integer(event["revision"], label="revision", minimum=1, maximum=256)
    if event["idempotency_key"] is not None:
        validate_uuid_v4(event["idempotency_key"])
    if event["previous_event_hash"] is not None:
        validate_sha256(event["previous_event_hash"], "previous_event_hash")
    validate_timestamp(event["created_at"], "created_at")
    expected_id = canonical_sha256(event_id_preimage(event))
    if event["event_id"] != expected_id:
        raise ApplyContractError("APPLY_EVENT_FILENAME_ID_MISMATCH")
    expected_relative = event_relative_path(event["promotion_id"], sequence, expected_id)
    if event["event_filename"] != expected_relative.name:
        raise ApplyContractError("APPLY_EVENT_FILENAME_ID_MISMATCH")
    if event["event_path"] != expected_relative.as_posix():
        raise ApplyContractError("APPLY_EVENT_PATH_ESCAPE")
    expected_content_hash = canonical_sha256(_content_without_hash(event))
    if event["event_content_hash"] != expected_content_hash:
        raise ApplyContractError("APPLY_EVENT_CONTENT_HASH_MISMATCH")
    try:
        canonical_json_bytes(event, max_bytes=MAX_EVENT_BYTES)
    except ApplyContractError as exc:
        if exc.code == "CANONICAL_JSON_TOO_LARGE":
            raise ApplyContractError("AUDIT_EVENT_TOO_LARGE") from exc
        raise
    try:
        _validate_event_content_semantics(event)
    except ApplyContractError as exc:
        raise ApplyContractError("APPLY_EVENT_MALFORMED") from exc
    content = {field: event[field] for field in _EVENT_FIELDS[event_type]}
    expected_scope = event_scope_hash(
        event_type=event_type,
        project_id=event["project_id"],
        promotion_id=event["promotion_id"],
        candidate_id=event["candidate_id"],
        revision=event["revision"],
        idempotency_key=event["idempotency_key"],
        operation_identity=event["operation_identity"],
        content=content,
    )
    if event["event_scope_hash"] != expected_scope:
        raise ApplyContractError("APPLY_EVENT_IDEMPOTENCY_SCOPE_CONFLICT")
    try:
        canonical_json_bytes(event, max_bytes=MAX_EVENT_BYTES)
    except ApplyContractError as exc:
        if exc.code == "CANONICAL_JSON_TOO_LARGE":
            raise ApplyContractError("AUDIT_EVENT_TOO_LARGE") from exc
        raise


def _events_directory(project_dir: str | Path, promotion_id: str, *, create: bool) -> Path | None:
    root = Path(project_dir).resolve(strict=True)
    current = root
    for part in event_directory_relative_path(promotion_id).parts:
        current = current / part
        if current.exists() or current.is_symlink():
            metadata = os.lstat(current)
            if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
                raise ApplyContractError("APPLY_EVENT_UNSAFE_PATH")
        elif create:
            current.mkdir(mode=0o700)
        else:
            return None
    try:
        current.resolve(strict=True).relative_to(root)
    except ValueError as exc:
        raise ApplyContractError("APPLY_EVENT_PATH_ESCAPE") from exc
    return current


def scan_event_chain(
    project_dir: str | Path,
    *,
    project_id: str,
    promotion_id: str,
    reference_validator: Callable[[dict[str, Any]], None] | None = None,
) -> EventChain:
    """Fully validate bounded history before exposing any lookup result."""

    validate_safe_id(project_id, "project_id")
    validate_safe_id(promotion_id, "promotion_id")
    directory = _events_directory(project_dir, promotion_id, create=False)
    if directory is None:
        return EventChain((), ())
    entries = sorted(directory.iterdir(), key=lambda path: os.fsencode(path.name))
    events: list[dict[str, Any]] = []
    residue: list[str] = []
    candidates: list[tuple[Path, re.Match[str]]] = []
    claimed_sequences: set[int] = set()
    claimed_ids: set[str] = set()
    for entry in entries:
        if _TEMP_FILE_RE.fullmatch(entry.name):
            residue.append(entry.name)
            continue
        match = _EVENT_FILE_RE.fullmatch(entry.name)
        if not match:
            raise ApplyContractError("APPLY_EVENT_MALFORMED")
        claimed_sequence = int(match.group(1))
        claimed_id = match.group(2)
        if claimed_sequence in claimed_sequences:
            raise ApplyContractError("APPLY_EVENT_DUPLICATE_SEQUENCE")
        if claimed_id in claimed_ids:
            raise ApplyContractError("APPLY_EVENT_DUPLICATE_ID")
        claimed_sequences.add(claimed_sequence)
        claimed_ids.add(claimed_id)
        candidates.append((entry, match))
    seen_sequences: set[int] = set()
    seen_ids: set[str] = set()
    replay_scopes: dict[tuple[str, str, str], str] = {}
    previous_bytes: bytes | None = None
    for entry, match in candidates:
        sequence = int(match.group(1))
        filename_id = match.group(2)
        if sequence in seen_sequences:
            raise ApplyContractError("APPLY_EVENT_DUPLICATE_SEQUENCE")
        if filename_id in seen_ids:
            raise ApplyContractError("APPLY_EVENT_DUPLICATE_ID")
        if sequence != len(events) + 1:
            raise ApplyContractError("APPLY_EVENT_SEQUENCE_GAP")
        metadata = os.lstat(entry)
        if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
            raise ApplyContractError("APPLY_EVENT_UNSAFE_PATH")
        if metadata.st_size > MAX_EVENT_BYTES:
            raise ApplyContractError("AUDIT_EVENT_TOO_LARGE")
        raw = entry.read_bytes()
        try:
            event = strict_json_loads(raw, max_bytes=MAX_EVENT_BYTES)
            if canonical_json_bytes(event, max_bytes=MAX_EVENT_BYTES) != raw:
                raise ApplyContractError("APPLY_EVENT_MALFORMED")
        except ApplyContractError as exc:
            if exc.code in {"REQUEST_TOO_LARGE", "CANONICAL_JSON_TOO_LARGE"}:
                raise ApplyContractError("AUDIT_EVENT_TOO_LARGE") from exc
            raise
        expected_previous = None if previous_bytes is None else hashlib.sha256(previous_bytes).hexdigest()
        if event.get("previous_event_hash") != expected_previous:
            raise ApplyContractError("APPLY_EVENT_PREVIOUS_HASH_MISMATCH")
        _validate_event_semantics(event)
        if event["project_id"] != project_id or event["promotion_id"] != promotion_id:
            raise ApplyContractError("APPLY_EVENT_PATH_ESCAPE")
        if event["sequence"] != sequence:
            raise ApplyContractError("APPLY_EVENT_FILENAME_SEQUENCE_MISMATCH")
        if event["event_id"] != filename_id:
            raise ApplyContractError("APPLY_EVENT_FILENAME_ID_MISMATCH")
        replay_key = (event["event_type"], event["operation_identity"], str(event["idempotency_key"]))
        if replay_key in replay_scopes:
            if replay_scopes[replay_key] != event["event_scope_hash"]:
                raise ApplyContractError("APPLY_EVENT_IDEMPOTENCY_SCOPE_CONFLICT")
            raise ApplyContractError("APPLY_EVENT_DUPLICATE_ID")
        replay_scopes[replay_key] = event["event_scope_hash"]
        if reference_validator is not None:
            try:
                reference_validator(event)
            except ApplyContractError as exc:
                raise ApplyContractError("APPLY_EVENT_REFERENCE_MISSING_OR_CORRUPT") from exc
        seen_sequences.add(sequence)
        seen_ids.add(filename_id)
        events.append(event)
        previous_bytes = raw
        if len(events) > MAX_EVENT_SEQUENCE:
            raise ApplyContractError("APPLY_EVENT_SEQUENCE_EXHAUSTED")
    return EventChain(tuple(events), tuple(residue))


def append_event(
    project_dir: str | Path,
    *,
    event_type: str,
    project_id: str,
    promotion_id: str,
    candidate_id: str,
    revision: int | None,
    idempotency_key: str | None,
    operation_identity: str,
    created_at: str,
    content: dict[str, Any],
    reference_validator: Callable[[dict[str, Any]], None] | None = None,
) -> EventPublication:
    """Append one event after full validation, or return exact idempotent replay."""

    chain = scan_event_chain(
        project_dir,
        project_id=project_id,
        promotion_id=promotion_id,
        reference_validator=reference_validator,
    )
    validate_safe_id(candidate_id, "candidate_id")
    validate_safe_id(operation_identity, "operation_identity")
    validate_timestamp(created_at, "created_at")
    if revision is not None:
        require_integer(revision, label="revision", minimum=1, maximum=256)
    if idempotency_key is not None:
        validate_uuid_v4(idempotency_key)
    scope_hash = event_scope_hash(
        event_type=event_type,
        project_id=project_id,
        promotion_id=promotion_id,
        candidate_id=candidate_id,
        revision=revision,
        idempotency_key=idempotency_key,
        operation_identity=operation_identity,
        content=content,
    )
    matches = [
        event for event in chain.events
        if event["event_type"] == event_type
        and event["operation_identity"] == operation_identity
        and event["idempotency_key"] == idempotency_key
    ]
    if matches:
        if len(matches) != 1:
            raise ApplyContractError("APPLY_EVENT_DUPLICATE_ID")
        if matches[0]["event_scope_hash"] != scope_hash:
            raise ApplyContractError("APPLY_EVENT_IDEMPOTENCY_SCOPE_CONFLICT")
        return EventPublication(matches[0], True)
    sequence = len(chain.events) + 1
    if sequence > MAX_EVENT_SEQUENCE:
        raise ApplyContractError("APPLY_EVENT_SEQUENCE_EXHAUSTED")
    previous_hash = (
        None
        if not chain.events
        else hashlib.sha256(canonical_json_bytes(chain.events[-1])).hexdigest()
    )
    event: dict[str, Any] = {
        "object_kind": "promotion_apply_event",
        "event_version": EVENT_VERSION,
        "event_type": event_type,
        "sequence": sequence,
        "previous_event_hash": previous_hash,
        "project_id": project_id,
        "promotion_id": promotion_id,
        "candidate_id": candidate_id,
        "revision": revision,
        "idempotency_key": idempotency_key,
        "operation_identity": operation_identity,
        "event_scope_hash": scope_hash,
        "created_at": created_at,
        **content,
    }
    event["event_id"] = canonical_sha256(event_id_preimage(event))
    relative = event_relative_path(promotion_id, sequence, event["event_id"])
    event["event_filename"] = relative.name
    event["event_path"] = relative.as_posix()
    event["event_content_hash"] = canonical_sha256(_content_without_hash(event))
    _validate_event_semantics(event)
    raw = canonical_json_bytes(event, max_bytes=MAX_EVENT_BYTES)
    replayed = publish_immutable_file(
        project_dir,
        relative,
        raw,
        conflict_code="APPLY_EVENT_DUPLICATE_SEQUENCE",
    )
    if reference_validator is not None:
        reference_validator(event)
    return EventPublication(event, replayed)


def find_events(
    project_dir: str | Path,
    *,
    project_id: str,
    promotion_id: str,
    event_type: str | None = None,
    operation_identity: str | None = None,
    idempotency_key: str | None = None,
) -> tuple[dict[str, Any], ...]:
    chain = scan_event_chain(project_dir, project_id=project_id, promotion_id=promotion_id)
    return tuple(
        event for event in chain.events
        if (event_type is None or event["event_type"] == event_type)
        and (operation_identity is None or event["operation_identity"] == operation_identity)
        and (idempotency_key is None or event["idempotency_key"] == idempotency_key)
    )


__all__ = (
    "EVENT_SCOPE_VERSION",
    "EVENT_VERSION",
    "EventChain",
    "EventPublication",
    "MAX_EVENT_BYTES",
    "MAX_EVENT_SEQUENCE",
    "append_event",
    "event_directory_relative_path",
    "event_id_preimage",
    "event_relative_path",
    "event_scope_hash",
    "find_events",
    "scan_event_chain",
)
