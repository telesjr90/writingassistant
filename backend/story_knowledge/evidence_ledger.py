"""Immutable, content-free evidence/provenance ledger for analysis runs.

Ledger records attribute exact source spans, artifacts, transformations, output
dispositions, and all six accepted contributor states.  Source text and raw
tool/model output never enter the ledger; those payloads live only in the raw
artifact bundle so an owner deletion can physically remove them while this
cryptographic provenance remains interpretable.
"""

from __future__ import annotations

import copy
import fcntl
import hashlib
import json
import os
import re
import stat
import threading
from contextlib import contextmanager
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

from backend.story_knowledge.analysis_run_manifest import (
    ADAPTER_IDENTITIES,
    ADAPTER_RESULT_STATES,
    OUTPUT_DISPOSITIONS,
)
from backend.story_knowledge.source_map import (
    BYTE_OFFSET_BASIS,
    CHAR_OFFSET_BASIS,
    ExactSourceSnapshot,
    OffsetRange,
    build_canonical_source_locator,
    translate_exact_offset_range,
    validate_canonical_source_locator,
)


EVIDENCE_RECORD_VERSION = "analysis-evidence-record.v1"
EVIDENCE_LEDGER_EVENT_VERSION = "analysis-evidence-ledger-event.v1"
EVIDENCE_LEDGER_VERSION = "analysis-evidence-ledger.v1"
LEDGER_EVENT_TYPES = frozenset(
    {
        "artifact_recorded",
        "evidence_recorded",
        "output_recorded",
        "contributor_recorded",
        "artifact_deleted",
    }
)
DELETION_STATES = frozenset({"retained", "deleted"})
MAX_LEDGER_EVENT_BYTES = 4_194_304

_SAFE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,255}\Z")
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_EVENT_FILE = re.compile(r"([0-9]{12})_([0-9a-f]{64})\.json\Z")
_PROCESS_LEDGER_LOCKS: dict[tuple[str, str], threading.Lock] = {}
_PROCESS_LEDGER_LOCKS_GUARD = threading.Lock()


def canonical_json_bytes(value: Any) -> bytes:
    try:
        encoded = json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ValueError("value is not canonical JSON") from exc
    if len(encoded) > MAX_LEDGER_EVENT_BYTES:
        raise ValueError("ledger event exceeds size limit")
    return encoded


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _safe_id(value: Any, label: str) -> str:
    if not isinstance(value, str) or not _SAFE_ID.fullmatch(value) or ".." in value:
        raise ValueError(f"{label} must be a path-safe ID")
    if PurePosixPath(value).is_absolute() or PureWindowsPath(value).is_absolute():
        raise ValueError(f"{label} must be a path-safe ID")
    return value


def _sha256(value: Any, label: str) -> str:
    if not isinstance(value, str) or not _SHA256.fullmatch(value):
        raise ValueError(f"{label} must be lowercase SHA-256")
    return value


def _timestamp(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value or not value.endswith("Z"):
        raise ValueError(f"{label} must be an explicit UTC timestamp")
    return value


def _string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a list")
    checked = [_safe_id(item, label) for item in value]
    if len(checked) != len(set(checked)):
        raise ValueError(f"{label} contains duplicates")
    return checked


def build_exact_evidence_record(
    *,
    snapshot: ExactSourceSnapshot,
    run_id: str,
    artifact_id: str,
    artifact_file_id: str,
    operation_id: str,
    adapter_id: str,
    disposition: str,
    contributor_state: str,
    created_at: str,
    character_range: OffsetRange | None = None,
    byte_range: OffsetRange | None = None,
    transformation_ids: tuple[str, ...] = (),
    output_id: str | None = None,
    reason: str | None = None,
) -> dict[str, Any]:
    """Build a deterministic exact-span record without retaining excerpt text."""

    if not isinstance(snapshot, ExactSourceSnapshot):
        raise ValueError("exact source snapshot is required")
    if character_range is None and byte_range is None:
        raise ValueError("one exact character or byte range is required")
    if character_range is not None and character_range.basis != CHAR_OFFSET_BASIS:
        raise ValueError("character_range must use the exact character basis")
    if byte_range is not None and byte_range.basis != BYTE_OFFSET_BASIS:
        raise ValueError("byte_range must use the exact UTF-8 byte basis")
    if character_range is None:
        character_range = translate_exact_offset_range(
            snapshot,
            byte_range,
            target_basis=CHAR_OFFSET_BASIS,
            expected_snapshot_id=snapshot.identity.snapshot_id,
            expected_content_hash=snapshot.identity.content_hash,
        )
    translated_byte_range = translate_exact_offset_range(
        snapshot,
        character_range,
        target_basis=BYTE_OFFSET_BASIS,
        expected_snapshot_id=snapshot.identity.snapshot_id,
        expected_content_hash=snapshot.identity.content_hash,
    )
    if byte_range is not None and translated_byte_range != byte_range:
        raise ValueError("character and byte evidence ranges identify different spans")
    byte_range = translated_byte_range
    excerpt = snapshot.source_content[character_range.start : character_range.end]
    excerpt_bytes = excerpt.encode("utf-8")
    locator = build_canonical_source_locator(
        snapshot.identity,
        character_range=character_range,
        byte_range=byte_range,
        exact_snapshot=snapshot,
    )
    material = {
        "project_id": snapshot.identity.project_id,
        "run_id": run_id,
        "snapshot_id": snapshot.identity.snapshot_id,
        "artifact_id": artifact_id,
        "artifact_file_id": artifact_file_id,
        "operation_id": operation_id,
        "adapter_id": adapter_id,
        "output_id": output_id,
        "locator": locator,
        "excerpt_hash": hashlib.sha256(excerpt_bytes).hexdigest(),
    }
    record = {
        "schema_version": EVIDENCE_RECORD_VERSION,
        "evidence_id": f"evidence-{canonical_sha256(material)[:32]}",
        "project_id": snapshot.identity.project_id,
        "run_id": run_id,
        "source_identity": snapshot.identity.to_dict(),
        "source_locator": locator,
        "artifact_id": artifact_id,
        "artifact_file_id": artifact_file_id,
        "operation_id": operation_id,
        "adapter_id": adapter_id,
        "output_id": output_id,
        "transformation_ids": list(transformation_ids),
        "disposition": disposition,
        "contributor_state": contributor_state,
        "excerpt_hash": hashlib.sha256(excerpt_bytes).hexdigest(),
        "excerpt_size_bytes": len(excerpt_bytes),
        "created_at": created_at,
        "content_available": True,
        "deletion_state": "retained",
        "reason": reason,
        "support_is_truth": False,
        "candidate_or_canon": False,
    }
    return validate_evidence_record_v1(record)


def validate_evidence_record_v1(record: Any) -> dict[str, Any]:
    required = {
        "schema_version", "evidence_id", "project_id", "run_id",
        "source_identity", "source_locator", "artifact_id", "artifact_file_id",
        "operation_id", "adapter_id", "output_id", "transformation_ids",
        "disposition", "contributor_state", "excerpt_hash", "excerpt_size_bytes",
        "created_at", "content_available", "deletion_state", "reason",
        "support_is_truth", "candidate_or_canon",
    }
    if not isinstance(record, dict) or set(record) != required:
        raise ValueError("invalid evidence record fields")
    value = copy.deepcopy(record)
    if value["schema_version"] != EVIDENCE_RECORD_VERSION:
        raise ValueError("unsupported evidence record version")
    for field in (
        "evidence_id", "project_id", "run_id", "artifact_id", "artifact_file_id",
        "operation_id",
    ):
        _safe_id(value[field], field)
    if value["adapter_id"] not in ADAPTER_IDENTITIES:
        raise ValueError("unknown adapter identity")
    if value["disposition"] not in OUTPUT_DISPOSITIONS:
        raise ValueError("unknown output disposition")
    if value["contributor_state"] not in ADAPTER_RESULT_STATES:
        raise ValueError("unknown contributor state")
    if value["output_id"] is not None:
        _safe_id(value["output_id"], "output_id")
    value["transformation_ids"] = _string_list(
        value["transformation_ids"], "transformation_id"
    )
    _sha256(value["excerpt_hash"], "excerpt_hash")
    if type(value["excerpt_size_bytes"]) is not int or value["excerpt_size_bytes"] < 0:
        raise ValueError("excerpt_size_bytes must be a non-negative integer")
    _timestamp(value["created_at"], "created_at")
    if value["deletion_state"] not in DELETION_STATES:
        raise ValueError("invalid deletion_state")
    if value["content_available"] is not (value["deletion_state"] == "retained"):
        raise ValueError("content availability and deletion state disagree")
    if value["reason"] is not None and (
        not isinstance(value["reason"], str) or not value["reason"]
    ):
        raise ValueError("reason must be a non-empty string or null")
    if value["disposition"] != "validated" and not value["reason"]:
        raise ValueError("unsuccessful/unverified evidence requires a reason")
    if value["support_is_truth"] is not False or value["candidate_or_canon"] is not False:
        raise ValueError("evidence remains support data only")
    identity = value["source_identity"]
    if not isinstance(identity, dict):
        raise ValueError("source_identity must be an object")
    if identity.get("project_id") != value["project_id"]:
        raise ValueError("source project linkage mismatch")
    if identity.get("snapshot_id") != value["source_locator"].get("snapshot_id"):
        raise ValueError("source snapshot linkage mismatch")
    if identity.get("content_hash") != value["source_locator"].get("snapshot_hash"):
        raise ValueError("source hash linkage mismatch")
    validate_canonical_source_locator(value["source_locator"])
    return value


def evidence_ledger_events_dir(*, project_dir: str | Path, run_id: str) -> Path:
    return (
        Path(project_dir)
        / "writer_assistant"
        / "analysis_runs"
        / _safe_id(run_id, "run_id")
        / "evidence_ledger"
        / "events"
    )


def _assert_safe_ledger_ancestry(project_dir: str | Path, run_id: str) -> Path:
    root = Path(project_dir)
    if root.is_symlink():
        raise ValueError("unsafe project directory")
    events = evidence_ledger_events_dir(project_dir=root, run_id=run_id)
    for path in (
        root / "writer_assistant",
        root / "writer_assistant" / "analysis_runs",
        root / "writer_assistant" / "analysis_runs" / run_id,
        root / "writer_assistant" / "analysis_runs" / run_id / "evidence_ledger",
        events,
    ):
        if path.exists() and path.is_symlink():
            raise ValueError("unsafe ledger storage path")
    try:
        events.resolve(strict=False).relative_to(root.resolve(strict=False))
    except ValueError as exc:
        raise ValueError("ledger path escapes project") from exc
    return events


def _event_without_hash(event: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in event.items() if key != "event_hash"}


@contextmanager
def _acquire_ledger_publication_lock(
    *, project_dir: str | Path, project_id: str, run_id: str
):
    """Serialize one project's run ledger across threads and processes."""

    root = Path(project_dir)
    _safe_id(project_id, "project_id")
    _safe_id(run_id, "run_id")
    lock_root = root / "writer_assistant" / "analysis_run_locks"
    for path in (root / "writer_assistant", lock_root):
        if path.exists() and path.is_symlink():
            raise ValueError("unsafe ledger lock path")
    lock_root.mkdir(parents=True, exist_ok=True, mode=0o700)
    directory_metadata = os.stat(lock_root, follow_symlinks=False)
    if (
        not stat.S_ISDIR(directory_metadata.st_mode)
        or directory_metadata.st_uid != os.getuid()
        or stat.S_IMODE(directory_metadata.st_mode) & 0o077
    ):
        raise ValueError("unsafe ledger lock directory")
    digest = hashlib.sha256(f"{project_id}/{run_id}/ledger".encode("utf-8")).hexdigest()
    process_key = (str(root.resolve(strict=False)), digest)
    with _PROCESS_LEDGER_LOCKS_GUARD:
        process_lock = _PROCESS_LEDGER_LOCKS.setdefault(process_key, threading.Lock())
    process_lock.acquire()
    descriptor = None
    locked = False
    try:
        descriptor = os.open(
            lock_root / f"ledger-{digest}.lock",
            os.O_CREAT | os.O_RDWR | os.O_CLOEXEC | os.O_NOFOLLOW,
            0o600,
        )
        metadata = os.fstat(descriptor)
        if (
            not stat.S_ISREG(metadata.st_mode)
            or stat.S_IMODE(metadata.st_mode) != 0o600
            or metadata.st_uid != os.getuid()
            or metadata.st_size != 0
            or metadata.st_nlink != 1
        ):
            raise ValueError("unsafe ledger lock file")
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        locked = True
        yield
    finally:
        if locked and descriptor is not None:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
        if descriptor is not None:
            os.close(descriptor)
        process_lock.release()


def validate_ledger_event_v1(
    event: Any, *, predecessor: dict[str, Any] | None = None
) -> dict[str, Any]:
    required = {
        "schema_version", "ledger_version", "event_type", "sequence",
        "previous_event_hash", "event_hash", "event_scope_hash", "project_id",
        "run_id", "idempotency_key", "created_at", "payload",
    }
    if not isinstance(event, dict) or set(event) != required:
        raise ValueError("invalid ledger event fields")
    value = copy.deepcopy(event)
    if value["schema_version"] != EVIDENCE_LEDGER_EVENT_VERSION:
        raise ValueError("unsupported ledger event version")
    if value["ledger_version"] != EVIDENCE_LEDGER_VERSION:
        raise ValueError("unsupported ledger version")
    if value["event_type"] not in LEDGER_EVENT_TYPES:
        raise ValueError("invalid ledger event type")
    if type(value["sequence"]) is not int or value["sequence"] < 1:
        raise ValueError("invalid ledger sequence")
    for field in ("project_id", "run_id", "idempotency_key"):
        _safe_id(value[field], field)
    _timestamp(value["created_at"], "created_at")
    if not isinstance(value["payload"], dict):
        raise ValueError("ledger payload must be an object")
    _sha256(value["event_scope_hash"], "event_scope_hash")
    _sha256(value["event_hash"], "event_hash")
    expected_previous = predecessor["event_hash"] if predecessor else None
    if value["previous_event_hash"] != expected_previous:
        raise ValueError("ledger previous hash mismatch")
    if value["sequence"] != (predecessor["sequence"] + 1 if predecessor else 1):
        raise ValueError("ledger sequence is not contiguous")
    scope = {
        "event_type": value["event_type"],
        "project_id": value["project_id"],
        "run_id": value["run_id"],
        "idempotency_key": value["idempotency_key"],
        "payload": value["payload"],
    }
    if canonical_sha256(scope) != value["event_scope_hash"]:
        raise ValueError("ledger event scope hash mismatch")
    if canonical_sha256(_event_without_hash(value)) != value["event_hash"]:
        raise ValueError("ledger event hash mismatch")
    if value["event_type"] == "evidence_recorded":
        validate_evidence_record_v1(value["payload"])
    if value["event_type"] == "contributor_recorded":
        contributor_fields = {
            "operation_id", "adapter_id", "source_snapshot_ids", "result_state",
            "coverage", "explanation", "provenance", "output_ids",
        }
        if set(value["payload"]) != contributor_fields:
            raise ValueError("invalid contributor ledger payload")
        if value["payload"].get("result_state") not in ADAPTER_RESULT_STATES:
            raise ValueError("invalid contributor result state")
        if value["payload"].get("adapter_id") not in ADAPTER_IDENTITIES:
            raise ValueError("invalid contributor adapter")
        _safe_id(value["payload"]["operation_id"], "operation_id")
        _string_list(value["payload"]["source_snapshot_ids"], "source_snapshot_id")
        _string_list(value["payload"]["output_ids"], "output_id")
        if value["payload"]["coverage"] not in {"complete", "partial", "none"}:
            raise ValueError("invalid contributor coverage")
        if not isinstance(value["payload"]["explanation"], str) or not value["payload"]["explanation"]:
            raise ValueError("invalid contributor explanation")
        if not isinstance(value["payload"]["provenance"], dict):
            raise ValueError("invalid contributor provenance")
    if value["event_type"] == "output_recorded":
        output_fields = {
            "output_id", "operation_id", "source_snapshot_ids", "disposition",
            "original_output_reference_id", "evidence_reference_ids",
            "transformation_ids", "verification_outcome", "guardrail_outcome",
            "missing_evidence_reason",
        }
        if set(value["payload"]) != output_fields:
            raise ValueError("invalid output ledger payload")
        if value["payload"].get("disposition") not in OUTPUT_DISPOSITIONS:
            raise ValueError("invalid output disposition")
        for field in ("output_id", "operation_id", "original_output_reference_id"):
            _safe_id(value["payload"][field], field)
        for field in ("source_snapshot_ids", "evidence_reference_ids", "transformation_ids"):
            _string_list(value["payload"][field], field)
        if value["payload"]["disposition"] in {"rejected", "quarantined", "unverified"} and not any(
            value["payload"].get(field)
            for field in ("verification_outcome", "guardrail_outcome", "missing_evidence_reason")
        ):
            raise ValueError("unsuccessful output ledger payload requires a reason")
    if value["event_type"] == "artifact_recorded":
        artifact_fields = {
            "artifact_id", "artifact_manifest_hash", "artifact_bundle_hash",
            "analysis_run_manifest_hash", "source_snapshot_ids", "availability",
        }
        if set(value["payload"]) != artifact_fields:
            raise ValueError("invalid artifact ledger payload")
        _safe_id(value["payload"]["artifact_id"], "artifact_id")
        for field in (
            "artifact_manifest_hash", "artifact_bundle_hash", "analysis_run_manifest_hash"
        ):
            _sha256(value["payload"][field], field)
        _string_list(value["payload"]["source_snapshot_ids"], "source_snapshot_id")
        if value["payload"]["availability"] not in {"available", "unavailable", "deleted"}:
            raise ValueError("invalid artifact availability")
    if value["event_type"] == "artifact_deleted":
        validate_deletion_tombstone(value["payload"])
    return value


def scan_evidence_ledger(
    *, project_dir: str | Path, project_id: str, run_id: str
) -> tuple[dict[str, Any], ...]:
    _safe_id(project_id, "project_id")
    events_dir = _assert_safe_ledger_ancestry(project_dir, run_id)
    try:
        metadata = os.lstat(events_dir)
    except FileNotFoundError:
        return ()
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
        raise ValueError("unsafe ledger directory")
    chain: list[dict[str, Any]] = []
    replay_keys: dict[tuple[str, str], str] = {}
    for path in sorted(events_dir.iterdir(), key=lambda item: os.fsencode(item.name)):
        match = _EVENT_FILE.fullmatch(path.name)
        file_metadata = os.lstat(path)
        if (
            match is None
            or stat.S_ISLNK(file_metadata.st_mode)
            or not stat.S_ISREG(file_metadata.st_mode)
            or file_metadata.st_nlink != 1
            or file_metadata.st_size > MAX_LEDGER_EVENT_BYTES
        ):
            raise ValueError("unsafe or malformed ledger event file")
        raw = path.read_bytes()
        try:
            loaded = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("invalid ledger event JSON") from exc
        if canonical_json_bytes(loaded) != raw:
            raise ValueError("ledger event is not canonical JSON")
        validated = validate_ledger_event_v1(
            loaded, predecessor=chain[-1] if chain else None
        )
        if validated["project_id"] != project_id or validated["run_id"] != run_id:
            raise ValueError("ledger storage linkage mismatch")
        if int(match.group(1)) != validated["sequence"]:
            raise ValueError("ledger filename sequence mismatch")
        if match.group(2) != validated["event_hash"]:
            raise ValueError("ledger filename hash mismatch")
        replay_key = (validated["event_type"], validated["idempotency_key"])
        prior = replay_keys.get(replay_key)
        if prior is not None:
            if prior != validated["event_scope_hash"]:
                raise ValueError("ledger idempotency conflict")
            raise ValueError("duplicate ledger idempotency key")
        replay_keys[replay_key] = validated["event_scope_hash"]
        chain.append(validated)
    return tuple(chain)


def append_evidence_ledger_event(
    *,
    project_dir: str | Path,
    project_id: str,
    run_id: str,
    event_type: str,
    idempotency_key: str,
    created_at: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    """Append exactly once; identical replay returns the original event."""

    _safe_id(idempotency_key, "idempotency_key")
    if event_type not in LEDGER_EVENT_TYPES:
        raise ValueError("invalid ledger event type")
    scope = {
        "event_type": event_type,
        "project_id": project_id,
        "run_id": run_id,
        "idempotency_key": idempotency_key,
        "payload": copy.deepcopy(payload),
    }
    scope_hash = canonical_sha256(scope)
    with _acquire_ledger_publication_lock(
        project_dir=project_dir, project_id=project_id, run_id=run_id
    ):
        chain = scan_evidence_ledger(
            project_dir=project_dir, project_id=project_id, run_id=run_id
        )
        matches = [
            event for event in chain
            if event["event_type"] == event_type
            and event["idempotency_key"] == idempotency_key
        ]
        if matches:
            if len(matches) == 1 and matches[0]["event_scope_hash"] == scope_hash:
                return copy.deepcopy(matches[0])
            raise ValueError("ledger idempotency conflict")
        event = {
            "schema_version": EVIDENCE_LEDGER_EVENT_VERSION,
            "ledger_version": EVIDENCE_LEDGER_VERSION,
            "event_type": event_type,
            "sequence": len(chain) + 1,
            "previous_event_hash": chain[-1]["event_hash"] if chain else None,
            "event_hash": "0" * 64,
            "event_scope_hash": scope_hash,
            "project_id": project_id,
            "run_id": run_id,
            "idempotency_key": idempotency_key,
            "created_at": created_at,
            "payload": copy.deepcopy(payload),
        }
        event["event_hash"] = canonical_sha256(_event_without_hash(event))
        validated = validate_ledger_event_v1(
            event, predecessor=chain[-1] if chain else None
        )
        events_dir = _assert_safe_ledger_ancestry(project_dir, run_id)
        events_dir.mkdir(parents=True, exist_ok=True)
        if events_dir.is_symlink():
            raise ValueError("unsafe ledger directory")
        path = events_dir / f"{validated['sequence']:012d}_{validated['event_hash']}.json"
        try:
            with path.open("xb") as handle:
                handle.write(canonical_json_bytes(validated))
        except FileExistsError as exc:
            raise ValueError("ledger event collision") from exc
        return copy.deepcopy(validated)


def resolve_evidence_ledger(
    *, project_dir: str | Path, project_id: str, run_id: str
) -> tuple[dict[str, Any], ...]:
    """Project surviving records through later deletion tombstones."""

    chain = scan_evidence_ledger(
        project_dir=project_dir, project_id=project_id, run_id=run_id
    )
    deleted_artifacts = {
        event["payload"]["artifact_id"]: event["payload"]
        for event in chain
        if event["event_type"] == "artifact_deleted"
    }
    resolved = []
    for event in chain:
        projected = copy.deepcopy(event)
        if event["event_type"] == "evidence_recorded":
            artifact_id = event["payload"]["artifact_id"]
            if artifact_id in deleted_artifacts:
                projected["payload"]["content_available"] = False
                projected["payload"]["deletion_state"] = "deleted"
                projected["payload"]["reason"] = "owner_deleted_raw_artifact"
                projected["resolution"] = {
                    "status": "deleted",
                    "replayable": False,
                    "tombstone": copy.deepcopy(deleted_artifacts[artifact_id]),
                }
        resolved.append(projected)
    return tuple(resolved)


def build_deletion_tombstone(
    *,
    project_id: str,
    run_id: str,
    artifact_id: str,
    source_snapshot_ids: list[str],
    artifact_hashes: list[str],
    manifest_hash: str,
    ledger_head_hash: str | None,
    deleted_at: str,
    deletion_id: str,
) -> dict[str, Any]:
    tombstone = {
        "schema_version": "analysis-artifact-deletion-tombstone.v1",
        "deletion_id": deletion_id,
        "project_id": project_id,
        "run_id": run_id,
        "artifact_id": artifact_id,
        "source_snapshot_ids": list(source_snapshot_ids),
        "artifact_hashes": list(artifact_hashes),
        "manifest_hash": manifest_hash,
        "ledger_head_hash": ledger_head_hash,
        "deletion_state": "deleted",
        "deleted_at": deleted_at,
        "content_available": False,
        "replayable": False,
        "content_retained": False,
    }
    return validate_deletion_tombstone(tombstone)


def validate_deletion_tombstone(value: Any) -> dict[str, Any]:
    required = {
        "schema_version", "deletion_id", "project_id", "run_id", "artifact_id",
        "source_snapshot_ids", "artifact_hashes", "manifest_hash",
        "ledger_head_hash", "deletion_state", "deleted_at", "content_available",
        "replayable", "content_retained",
    }
    if not isinstance(value, dict) or set(value) != required:
        raise ValueError("invalid deletion tombstone fields")
    result = copy.deepcopy(value)
    if result["schema_version"] != "analysis-artifact-deletion-tombstone.v1":
        raise ValueError("unsupported deletion tombstone version")
    for field in ("deletion_id", "project_id", "run_id", "artifact_id"):
        _safe_id(result[field], field)
    result["source_snapshot_ids"] = _string_list(
        result["source_snapshot_ids"], "source_snapshot_id"
    )
    if not isinstance(result["artifact_hashes"], list) or not result["artifact_hashes"]:
        raise ValueError("artifact_hashes must be non-empty")
    for digest in result["artifact_hashes"]:
        _sha256(digest, "artifact_hash")
    _sha256(result["manifest_hash"], "manifest_hash")
    if result["ledger_head_hash"] is not None:
        _sha256(result["ledger_head_hash"], "ledger_head_hash")
    _timestamp(result["deleted_at"], "deleted_at")
    if (
        result["deletion_state"] != "deleted"
        or result["content_available"] is not False
        or result["replayable"] is not False
        or result["content_retained"] is not False
    ):
        raise ValueError("tombstone must be content-free and non-replayable")
    forbidden = {"source_text", "excerpt", "raw_output", "generated_text", "payload"}
    if forbidden & set(result):
        raise ValueError("tombstone contains content")
    return result


__all__ = [
    "EVIDENCE_RECORD_VERSION",
    "EVIDENCE_LEDGER_EVENT_VERSION",
    "EVIDENCE_LEDGER_VERSION",
    "LEDGER_EVENT_TYPES",
    "build_exact_evidence_record",
    "validate_evidence_record_v1",
    "evidence_ledger_events_dir",
    "scan_evidence_ledger",
    "append_evidence_ledger_event",
    "resolve_evidence_ledger",
    "build_deletion_tombstone",
    "validate_deletion_tombstone",
    "canonical_json_bytes",
    "canonical_sha256",
]
