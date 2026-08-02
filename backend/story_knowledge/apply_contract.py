"""Strict canonical JSON and primitive validation for apply-promotion contracts.

This module is deliberately storage- and route-agnostic. Later T008D phases use
these helpers to ensure every hash and persisted byte string is derived from the
same bounded representation.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import stat
import uuid
from base64 import urlsafe_b64decode, urlsafe_b64encode
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


MAX_SAFE_INTEGER = 9_007_199_254_740_991
MAX_JSON_DEPTH = 32
MAX_REQUEST_BYTES = 1_114_112
MAX_APPROVED_RECORD_BYTES = 262_144
MAX_REVISION_BYTES = 1_048_576
MAX_SEALED_REVISION_BYTES = 1_081_344
MAX_PREPARATION_BYTES = 2_621_440

_SAFE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$")
_FIELD_ID_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,63}$")
_SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
_TIMESTAMP_RE = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"
    r"(?:\.[0-9]+)?(?:Z|[+-][0-9]{2}:[0-9]{2})$"
)
_UUID_V4_RE = re.compile(
    r"^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$"
)
_PREPARATION_ID_RE = re.compile(r"^prep_[a-f0-9]{64}$")
_REVISION_NAME_RE = re.compile(r"^revision_([1-9][0-9]{0,2})\.json$")
_BASE64URL_RE = re.compile(r"^[A-Za-z0-9_-]+$")

_REVISION_REQUIRED = {
    "object_kind",
    "contract_schema_version",
    "project_id",
    "promotion_id",
    "candidate_id",
    "revision",
    "supersedes_revision",
    "prepared_by",
    "prepared_at",
    "operation",
    "destination",
    "source_candidate_snapshot_hash",
    "evidence_refs",
    "provenance_refs",
    "source_locators",
    "proposed_approved_record",
    "approved_record_hash",
    "approved_record_size",
    "duplicate_resolution",
    "dependency_resolution",
    "before_state",
    "draft_scope_hash",
}
_DRAFT_SCOPE_FIELDS = (
    "object_kind",
    "contract_schema_version",
    "project_id",
    "promotion_id",
    "candidate_id",
    "revision",
    "supersedes_revision",
    "prepared_by",
    "prepared_at",
    "operation",
    "destination",
    "source_candidate_snapshot_hash",
    "evidence_refs",
    "provenance_refs",
    "source_locators",
    "proposed_approved_record",
    "duplicate_resolution",
    "dependency_resolution",
    "before_state",
)
_PREPARATION_REQUIRED = {
    "object_kind",
    "preparation_schema_version",
    "project_id",
    "promotion_id",
    "candidate_id",
    "preparation_id",
    "preparation_path",
    "idempotency_key",
    "preparation_scope_hash",
    "canonical_request_body_hash",
    "requested_operation",
    "destination",
    "prior_lineage_expectations",
    "assigned_revision",
    "revision_path",
    "supersession_kind",
    "revision_canonical_encoding",
    "revision_canonical_bytes_b64url",
    "revision_canonical_hash",
    "revision_canonical_size",
    "draft_scope_hash",
    "approved_record_hash",
    "approved_record_size",
    "source_candidate_snapshot_hash",
    "revision",
    "artifact_created_at",
}


class ApplyContractError(ValueError):
    """Stable fail-closed contract error."""

    def __init__(self, code: str, message: str | None = None) -> None:
        self.code = code
        super().__init__(message or code)


def _reject_constant(value: str) -> None:
    raise ApplyContractError("JSON_NON_FINITE_NUMBER", f"non-finite JSON number: {value}")


def _parse_int(value: str) -> int:
    parsed = int(value)
    if abs(parsed) > MAX_SAFE_INTEGER:
        raise ApplyContractError("JSON_UNSAFE_NUMBER", "integer exceeds the safe JSON range")
    return parsed


def _parse_float(value: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ApplyContractError("JSON_NON_FINITE_NUMBER", "number must be finite")
    if abs(parsed) > MAX_SAFE_INTEGER:
        raise ApplyContractError("JSON_UNSAFE_NUMBER", "number exceeds the safe JSON range")
    return parsed


def _object_from_pairs(pairs: Iterable[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ApplyContractError("JSON_DUPLICATE_KEY", f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def _contains_surrogate(value: str) -> bool:
    return any(0xD800 <= ord(character) <= 0xDFFF for character in value)


def _validate_tree(value: Any, *, depth: int = 0) -> None:
    if isinstance(value, dict):
        next_depth = depth + 1
        if next_depth > MAX_JSON_DEPTH:
            raise ApplyContractError("JSON_MAXIMUM_DEPTH_EXCEEDED")
        for key, nested in value.items():
            if not isinstance(key, str):
                raise ApplyContractError("JSON_OBJECT_KEY_INVALID")
            if _contains_surrogate(key):
                raise ApplyContractError("JSON_INVALID_SURROGATE")
            _validate_tree(nested, depth=next_depth)
        return
    if isinstance(value, list):
        next_depth = depth + 1
        if next_depth > MAX_JSON_DEPTH:
            raise ApplyContractError("JSON_MAXIMUM_DEPTH_EXCEEDED")
        for nested in value:
            _validate_tree(nested, depth=next_depth)
        return
    if isinstance(value, str):
        if _contains_surrogate(value):
            raise ApplyContractError("JSON_INVALID_SURROGATE")
        return
    if value is None or isinstance(value, bool):
        return
    if isinstance(value, int):
        if abs(value) > MAX_SAFE_INTEGER:
            raise ApplyContractError("JSON_UNSAFE_NUMBER")
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ApplyContractError("JSON_NON_FINITE_NUMBER")
        if abs(value) > MAX_SAFE_INTEGER:
            raise ApplyContractError("JSON_UNSAFE_NUMBER")
        return
    raise ApplyContractError("JSON_UNSUPPORTED_VALUE", f"unsupported JSON value: {type(value).__name__}")


def strict_json_loads(
    raw: bytes | bytearray | memoryview | str,
    *,
    max_bytes: int = MAX_REQUEST_BYTES,
) -> Any:
    """Parse bounded strict UTF-8 JSON and reject ambiguous representations."""

    if max_bytes < 0:
        raise ValueError("max_bytes must be nonnegative")
    if isinstance(raw, str):
        if raw.startswith("\ufeff"):
            raise ApplyContractError("JSON_BOM_FORBIDDEN")
        if _contains_surrogate(raw):
            raise ApplyContractError("JSON_INVALID_SURROGATE")
        try:
            encoded = raw.encode("utf-8", errors="strict")
        except UnicodeEncodeError as exc:
            raise ApplyContractError("JSON_INVALID_UTF8") from exc
        if len(encoded) > max_bytes:
            raise ApplyContractError("REQUEST_TOO_LARGE")
        text = raw
    elif isinstance(raw, (bytes, bytearray, memoryview)):
        encoded = bytes(raw)
        if len(encoded) > max_bytes:
            raise ApplyContractError("REQUEST_TOO_LARGE")
        if encoded.startswith(b"\xef\xbb\xbf"):
            raise ApplyContractError("JSON_BOM_FORBIDDEN")
        try:
            text = encoded.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            raise ApplyContractError("JSON_INVALID_UTF8") from exc
    else:
        raise TypeError("raw JSON must be bytes or str")

    try:
        parsed = json.loads(
            text,
            object_pairs_hook=_object_from_pairs,
            parse_constant=_reject_constant,
            parse_int=_parse_int,
            parse_float=_parse_float,
        )
    except ApplyContractError:
        raise
    except (json.JSONDecodeError, ValueError) as exc:
        raise ApplyContractError("JSON_MALFORMED", str(exc)) from exc

    _validate_tree(parsed)
    return parsed


def _canonical_float(value: float) -> str:
    if value == 0.0:
        return "0"
    if value.is_integer():
        return str(int(value))
    rendered = repr(value).lower()
    if "e" not in rendered:
        return rendered
    mantissa, exponent = rendered.split("e", 1)
    sign = ""
    if exponent.startswith(("+", "-")):
        if exponent[0] == "-":
            sign = "-"
        exponent = exponent[1:]
    exponent = exponent.lstrip("0") or "0"
    return f"{mantissa}e{sign}{exponent}"


def _canonical_text(value: Any) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return _canonical_float(value)
    if isinstance(value, list):
        return "[" + ",".join(_canonical_text(item) for item in value) + "]"
    if isinstance(value, dict):
        members = []
        for key in sorted(value):
            members.append(
                json.dumps(key, ensure_ascii=False, separators=(",", ":"))
                + ":"
                + _canonical_text(value[key])
            )
        return "{" + ",".join(members) + "}"
    raise ApplyContractError("JSON_UNSUPPORTED_VALUE")


def canonical_json_bytes(value: Any, *, max_bytes: int | None = None) -> bytes:
    """Return deterministic canonical JSON v1 UTF-8 bytes with no newline."""

    _validate_tree(value)
    try:
        encoded = _canonical_text(value).encode("utf-8", errors="strict")
    except UnicodeEncodeError as exc:
        raise ApplyContractError("JSON_INVALID_SURROGATE") from exc
    if max_bytes is not None and len(encoded) > max_bytes:
        raise ApplyContractError("CANONICAL_JSON_TOO_LARGE")
    return encoded


def canonical_sha256(value: Any, *, max_bytes: int | None = None) -> str:
    return hashlib.sha256(canonical_json_bytes(value, max_bytes=max_bytes)).hexdigest()


def validate_safe_id(value: Any, field: str = "identifier") -> str:
    if not isinstance(value, str) or not _SAFE_ID_RE.fullmatch(value):
        raise ApplyContractError("INVALID_SAFE_ID", f"invalid {field}")
    return value


def validate_field_id(value: Any, field: str = "field") -> str:
    if not isinstance(value, str) or not _FIELD_ID_RE.fullmatch(value):
        raise ApplyContractError("INVALID_FIELD_ID", f"invalid {field}")
    return value


def validate_sha256(value: Any, field: str = "hash") -> str:
    if not isinstance(value, str) or not _SHA256_RE.fullmatch(value):
        raise ApplyContractError("INVALID_SHA256", f"invalid {field}")
    return value


def validate_timestamp(value: Any, field: str = "timestamp") -> str:
    if not isinstance(value, str) or len(value) > 40 or not _TIMESTAMP_RE.fullmatch(value):
        raise ApplyContractError("INVALID_TIMESTAMP", f"invalid {field}")
    candidate = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise ApplyContractError("INVALID_TIMESTAMP", f"invalid {field}") from exc
    return value


def require_closed_object(
    value: Any,
    *,
    required: set[str],
    optional: set[str] | None = None,
    label: str,
) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ApplyContractError("SCHEMA_TYPE_MISMATCH", f"{label} must be an object")
    optional = optional or set()
    keys = set(value)
    missing = required - keys
    unknown = keys - required - optional
    if missing:
        raise ApplyContractError("SCHEMA_REQUIRED_FIELD_MISSING", f"{label}: {sorted(missing)}")
    if unknown:
        raise ApplyContractError("SCHEMA_UNKNOWN_FIELD", f"{label}: {sorted(unknown)}")
    return value


def require_string(
    value: Any,
    *,
    label: str,
    minimum: int = 0,
    maximum: int,
) -> str:
    if not isinstance(value, str) or not minimum <= len(value) <= maximum:
        raise ApplyContractError("SCHEMA_STRING_INVALID", label)
    if _contains_surrogate(value):
        raise ApplyContractError("JSON_INVALID_SURROGATE", label)
    return value


def require_integer(value: Any, *, label: str, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
        raise ApplyContractError("SCHEMA_INTEGER_INVALID", label)
    return value


def validate_uuid_v4(value: Any, field: str = "idempotency_key") -> str:
    if not isinstance(value, str) or not _UUID_V4_RE.fullmatch(value):
        raise ApplyContractError("INVALID_UUID_V4", f"invalid {field}")
    return value


def validate_owner_identity(value: Any) -> dict[str, Any]:
    owner = require_closed_object(
        value,
        required={
            "actor_type",
            "owner_id",
            "display_name",
            "identity_source",
            "config_version",
            "config_hash",
        },
        label="owner identity",
    )
    if owner["actor_type"] != "owner" or owner["identity_source"] != "project_local_owner_config":
        raise ApplyContractError("OWNER_IDENTITY_INVALID")
    validate_safe_id(owner["owner_id"], "owner_id")
    require_string(owner["display_name"], label="display_name", minimum=1, maximum=160)
    require_integer(owner["config_version"], label="config_version", minimum=1, maximum=2_147_483_647)
    validate_sha256(owner["config_hash"], "config_hash")
    return owner


def preparation_id(project_id: str, promotion_id: str, idempotency_key: str) -> str:
    validate_safe_id(project_id, "project_id")
    validate_safe_id(promotion_id, "promotion_id")
    validate_uuid_v4(idempotency_key)
    digest = canonical_sha256(
        {
            "protocol": "apply-contract-preparation-id.v1",
            "project_id": project_id,
            "promotion_id": promotion_id,
            "idempotency_key": idempotency_key,
        }
    )
    return f"prep_{digest}"


def preparation_relative_path(promotion_id: str, preparation: str) -> Path:
    validate_safe_id(promotion_id, "promotion_id")
    if not isinstance(preparation, str) or not _PREPARATION_ID_RE.fullmatch(preparation):
        raise ApplyContractError("APPLY_CONTRACT_PREPARATION_ID_INVALID")
    return Path(
        "writer_assistant",
        "apply_contracts",
        promotion_id,
        "preparations",
        f"{preparation}.json",
    )


def revision_relative_path(promotion_id: str, revision: int) -> Path:
    validate_safe_id(promotion_id, "promotion_id")
    require_integer(revision, label="revision", minimum=1, maximum=256)
    return Path("writer_assistant", "apply_contracts", promotion_id, f"revision_{revision}.json")


def sealed_revision_relative_path(promotion_id: str, revision: int) -> Path:
    validate_safe_id(promotion_id, "promotion_id")
    require_integer(revision, label="revision", minimum=1, maximum=256)
    return Path("writer_assistant", "apply_contracts", promotion_id, f"sealed_revision_{revision}.json")


def preparation_scope_hash(
    *,
    project_id: str,
    promotion_id: str,
    requested_operation: str,
    approved_destination_type: str,
    destination_key: str,
    canonical_request_body_hash: str,
    expected_latest_revision: int | None,
    expected_latest_draft_scope_hash: str | None,
) -> str:
    validate_safe_id(project_id, "project_id")
    validate_safe_id(promotion_id, "promotion_id")
    validate_safe_id(destination_key, "destination_key")
    if requested_operation not in {"create", "update"}:
        raise ApplyContractError("APPLY_OPERATION_INVALID")
    validate_sha256(canonical_request_body_hash, "canonical_request_body_hash")
    if expected_latest_revision is not None:
        require_integer(expected_latest_revision, label="expected_latest_revision", minimum=1, maximum=255)
    if expected_latest_draft_scope_hash is not None:
        validate_sha256(expected_latest_draft_scope_hash, "expected_latest_draft_scope_hash")
    return canonical_sha256(
        {
            "operation_kind": "prepare",
            "project_id": project_id,
            "promotion_id": promotion_id,
            "requested_operation": requested_operation,
            "approved_destination_type": approved_destination_type,
            "destination_key": destination_key,
            "canonical_request_body_hash": canonical_request_body_hash,
            "expected_latest_revision": expected_latest_revision,
            "expected_latest_draft_scope_hash": expected_latest_draft_scope_hash,
        }
    )


def draft_scope_hash(revision: dict[str, Any]) -> str:
    missing = set(_DRAFT_SCOPE_FIELDS) - set(revision)
    if missing:
        raise ApplyContractError("SCHEMA_REQUIRED_FIELD_MISSING", f"revision C1: {sorted(missing)}")
    return canonical_sha256({field: revision[field] for field in _DRAFT_SCOPE_FIELDS})


def _validate_destination(value: Any) -> dict[str, Any]:
    from backend.story_knowledge.approved_records import approved_record_relative_path

    destination = require_closed_object(
        value,
        required={"approved_destination_type", "destination_key", "destination_path"},
        label="destination",
    )
    expected = approved_record_relative_path(
        destination["approved_destination_type"], destination["destination_key"]
    ).as_posix()
    if destination["destination_path"] != expected:
        raise ApplyContractError("APPLY_CONTRACT_DESTINATION_PATH_MISMATCH")
    return destination


def _validate_before_state(value: Any, *, operation: str) -> dict[str, Any]:
    from backend.story_knowledge.approved_records import approved_record_material

    state = require_closed_object(
        value,
        required={"state", "path", "record_version", "content_hash", "content", "observed_at", "snapshot_token"},
        label="before state",
    )
    require_string(state["path"], label="before-state path", minimum=1, maximum=320)
    validate_timestamp(state["observed_at"], "observed_at")
    validate_sha256(state["snapshot_token"], "snapshot_token")
    if state["state"] == "absent":
        if operation != "create" or any(state[field] is not None for field in ("record_version", "content_hash", "content")):
            raise ApplyContractError("APPLY_CONTRACT_BEFORE_STATE_INVALID")
    elif state["state"] == "present":
        if operation != "update":
            raise ApplyContractError("APPLY_CONTRACT_BEFORE_STATE_INVALID")
        require_integer(state["record_version"], label="record_version", minimum=1, maximum=2_147_483_647)
        material = approved_record_material(state["content"])
        if material.record["record_version"] != state["record_version"] or material.approved_record_hash != state["content_hash"]:
            raise ApplyContractError("APPLY_CONTRACT_BEFORE_STATE_INVALID")
    else:
        raise ApplyContractError("APPLY_CONTRACT_BEFORE_STATE_INVALID")
    return state


def _validate_unique_safe_ids(value: Any, *, label: str, maximum: int = 128) -> list[str]:
    if not isinstance(value, list) or len(value) > maximum:
        raise ApplyContractError("SCHEMA_ARRAY_INVALID", label)
    for item in value:
        validate_safe_id(item, label)
    if len(set(value)) != len(value):
        raise ApplyContractError("SCHEMA_ARRAY_ITEMS_NOT_UNIQUE", label)
    return value


def _validate_record_reference(value: Any) -> dict[str, Any]:
    reference = require_closed_object(
        value,
        required={"destination_type", "destination_key", "record_version", "content_hash"},
        label="approved record reference",
    )
    from backend.story_knowledge.approved_records import approved_record_relative_path

    approved_record_relative_path(reference["destination_type"], reference["destination_key"], ordinary=False)
    require_integer(reference["record_version"], label="record_version", minimum=1, maximum=2_147_483_647)
    validate_sha256(reference["content_hash"], "content_hash")
    return reference


def _validate_duplicate_resolution(value: Any, *, operation: str) -> dict[str, Any]:
    resolution = require_closed_object(
        value,
        required={
            "state", "rationale", "evidence_refs", "reviewed_candidate_ids",
            "reviewed_approved_records", "resolved_by", "resolved_at",
            "resolution_scope_hash",
        },
        label="duplicate resolution",
    )
    allowed = (
        {"unresolved", "distinct_record", "do_not_apply"}
        if operation == "create"
        else {"unresolved", "update_existing", "merge_into_existing", "do_not_apply"}
    )
    if resolution["state"] not in allowed:
        raise ApplyContractError("APPLY_CONTRACT_DUPLICATE_RESOLUTION_INVALID")
    require_string(resolution["rationale"], label="duplicate rationale", minimum=1, maximum=4096)
    evidence = _validate_unique_safe_ids(resolution["evidence_refs"], label="evidence_refs")
    reviewed = _validate_unique_safe_ids(resolution["reviewed_candidate_ids"], label="reviewed_candidate_ids")
    refs = resolution["reviewed_approved_records"]
    if not isinstance(refs, list) or len(refs) > 128:
        raise ApplyContractError("SCHEMA_ARRAY_INVALID", "reviewed_approved_records")
    for reference in refs:
        _validate_record_reference(reference)
    if len({canonical_json_bytes(reference) for reference in refs}) != len(refs):
        raise ApplyContractError("SCHEMA_ARRAY_ITEMS_NOT_UNIQUE", "reviewed_approved_records")
    if resolution["state"] == "unresolved":
        if any(resolution[field] is not None for field in ("resolved_by", "resolved_at", "resolution_scope_hash")):
            raise ApplyContractError("APPLY_CONTRACT_DUPLICATE_RESOLUTION_INVALID")
    else:
        if not evidence or not reviewed:
            raise ApplyContractError("APPLY_CONTRACT_DUPLICATE_RESOLUTION_INVALID")
        validate_owner_identity(resolution["resolved_by"])
        validate_timestamp(resolution["resolved_at"], "resolved_at")
        validate_sha256(resolution["resolution_scope_hash"], "resolution_scope_hash")
    return resolution


def _validate_dependency_entry(value: Any) -> dict[str, Any]:
    entry = require_closed_object(
        value,
        required={
            "dependency_id", "kind", "required", "status", "target", "rationale",
            "evidence_ref_ids", "provenance_ref_ids", "resolved_by", "resolved_at",
        },
        optional={"applicability_rule"},
        label="dependency entry",
    )
    validate_safe_id(entry["dependency_id"], "dependency_id")
    validate_field_id(entry["kind"], "kind")
    if not isinstance(entry["required"], bool) or entry["status"] not in {"unresolved", "satisfied", "not_applicable", "blocked"}:
        raise ApplyContractError("APPLY_CONTRACT_DEPENDENCY_RESOLUTION_INVALID")
    if entry["target"] is not None:
        _validate_record_reference(entry["target"])
    require_string(entry["rationale"], label="dependency rationale", minimum=1, maximum=4096)
    _validate_unique_safe_ids(entry["evidence_ref_ids"], label="evidence_ref_ids")
    _validate_unique_safe_ids(entry["provenance_ref_ids"], label="provenance_ref_ids")
    if entry["resolved_by"] is not None:
        validate_owner_identity(entry["resolved_by"])
    if entry["resolved_at"] is not None:
        validate_timestamp(entry["resolved_at"], "resolved_at")
    if "applicability_rule" in entry:
        require_string(entry["applicability_rule"], label="applicability_rule", minimum=1, maximum=2048)
    return entry


def _validate_dependency_resolution(value: Any) -> dict[str, Any]:
    resolution = require_closed_object(
        value,
        required={
            "state", "dependencies", "rationale", "evidence_ref_ids",
            "resolved_by", "resolved_at", "resolution_scope_hash",
        },
        label="dependency resolution",
    )
    if resolution["state"] not in {"unresolved", "none_declared", "satisfied", "blocked"}:
        raise ApplyContractError("APPLY_CONTRACT_DEPENDENCY_RESOLUTION_INVALID")
    dependencies = resolution["dependencies"]
    if not isinstance(dependencies, list) or len(dependencies) > 256:
        raise ApplyContractError("SCHEMA_ARRAY_INVALID", "dependencies")
    for dependency in dependencies:
        _validate_dependency_entry(dependency)
    require_string(resolution["rationale"], label="dependency rationale", minimum=1, maximum=4096)
    evidence = _validate_unique_safe_ids(resolution["evidence_ref_ids"], label="evidence_ref_ids")
    if resolution["state"] == "unresolved":
        if any(resolution[field] is not None for field in ("resolved_by", "resolved_at", "resolution_scope_hash")):
            raise ApplyContractError("APPLY_CONTRACT_DEPENDENCY_RESOLUTION_INVALID")
    else:
        if not evidence or (resolution["state"] == "none_declared" and dependencies) or (resolution["state"] in {"satisfied", "blocked"} and not dependencies):
            raise ApplyContractError("APPLY_CONTRACT_DEPENDENCY_RESOLUTION_INVALID")
        validate_owner_identity(resolution["resolved_by"])
        validate_timestamp(resolution["resolved_at"], "resolved_at")
        validate_sha256(resolution["resolution_scope_hash"], "resolution_scope_hash")
    return resolution


def _validate_prior_lineage_expectations(value: Any) -> dict[str, Any]:
    expectations = require_closed_object(
        value,
        required={
            "expected_state", "expected_latest_revision", "expected_latest_draft_scope_hash",
            "expected_active_sealed_revision", "expected_active_sealed_contract_hash",
        },
        label="prior lineage expectations",
    )
    if expectations["expected_state"] not in {"no_contract", "draft_active", "sealed_active", "revoked"}:
        raise ApplyContractError("APPLY_CONTRACT_PREPARATION_ARTIFACT_CORRUPT")
    for field in ("expected_latest_revision", "expected_active_sealed_revision"):
        if expectations[field] is not None:
            require_integer(expectations[field], label=field, minimum=1, maximum=255)
    for field in ("expected_latest_draft_scope_hash", "expected_active_sealed_contract_hash"):
        if expectations[field] is not None:
            validate_sha256(expectations[field], field)
    return expectations


def validate_revision(value: Any) -> dict[str, Any]:
    from backend.story_knowledge.approved_records import approved_record_material

    revision = require_closed_object(value, required=_REVISION_REQUIRED, label="revision")
    if revision["object_kind"] != "apply_contract_revision" or revision["contract_schema_version"] != "omi_apply_contract_revision.v1":
        raise ApplyContractError("APPLY_CONTRACT_REVISION_SCHEMA_INVALID")
    for field in ("project_id", "promotion_id", "candidate_id"):
        validate_safe_id(revision[field], field)
    number = require_integer(revision["revision"], label="revision", minimum=1, maximum=256)
    supersedes = revision["supersedes_revision"]
    if supersedes is not None:
        require_integer(supersedes, label="supersedes_revision", minimum=1, maximum=255)
    if (number == 1 and supersedes is not None) or (number > 1 and supersedes != number - 1):
        raise ApplyContractError("APPLY_CONTRACT_REVISION_LINEAGE_INVALID")
    validate_owner_identity(revision["prepared_by"])
    validate_timestamp(revision["prepared_at"], "prepared_at")
    if revision["operation"] not in {"create", "update"}:
        raise ApplyContractError("APPLY_OPERATION_INVALID")
    destination = _validate_destination(revision["destination"])
    validate_sha256(revision["source_candidate_snapshot_hash"], "source_candidate_snapshot_hash")
    material = approved_record_material(revision["proposed_approved_record"])
    record = material.record
    expected_record_values = {
        "project_id": revision["project_id"],
        "source_candidate_id": revision["candidate_id"],
        "source_promotion_id": revision["promotion_id"],
        "source_candidate_snapshot_hash": revision["source_candidate_snapshot_hash"],
        "destination_type": destination["approved_destination_type"],
        "destination_key": destination["destination_key"],
    }
    if any(record[field] != expected for field, expected in expected_record_values.items()):
        raise ApplyContractError("APPLY_CONTRACT_REVISION_RECORD_ASSOCIATION_MISMATCH")
    if revision["evidence_refs"] != record["evidence_refs"] or revision["provenance_refs"] != record["provenance_refs"] or revision["source_locators"] != record["source_locators"]:
        raise ApplyContractError("APPLY_CONTRACT_REVISION_RECORD_ASSOCIATION_MISMATCH")
    if revision["approved_record_hash"] != material.approved_record_hash:
        raise ApplyContractError("APPROVED_RECORD_HASH_MISMATCH")
    if revision["approved_record_size"] != material.approved_record_size:
        raise ApplyContractError("APPROVED_RECORD_SIZE_MISMATCH")
    _validate_duplicate_resolution(revision["duplicate_resolution"], operation=revision["operation"])
    _validate_dependency_resolution(revision["dependency_resolution"])
    _validate_before_state(revision["before_state"], operation=revision["operation"])
    if revision["draft_scope_hash"] != draft_scope_hash(revision):
        raise ApplyContractError("APPLY_CONTRACT_DRAFT_SCOPE_HASH_MISMATCH")
    canonical_json_bytes(revision, max_bytes=MAX_REVISION_BYTES)
    return revision


def build_revision(**fields: Any) -> dict[str, Any]:
    revision = {
        "object_kind": "apply_contract_revision",
        "contract_schema_version": "omi_apply_contract_revision.v1",
        **fields,
    }
    revision["draft_scope_hash"] = draft_scope_hash(revision)
    return validate_revision(revision)


def build_sealed_revision(
    revision: dict[str, Any], contract_approval: dict[str, Any], approval_event_id: str
) -> dict[str, Any]:
    validate_revision(revision)
    validate_sha256(approval_event_id, "approval_event_id")
    approval = require_closed_object(
        contract_approval,
        required={"owner_actor", "project_id", "promotion_id", "revision", "draft_scope_hash", "before_state_snapshot_token", "approval_method", "approved_at"},
        label="contract approval",
    )
    validate_owner_identity(approval["owner_actor"])
    if (
        approval["project_id"] != revision["project_id"]
        or approval["promotion_id"] != revision["promotion_id"]
        or approval["revision"] != revision["revision"]
        or approval["draft_scope_hash"] != revision["draft_scope_hash"]
        or approval["before_state_snapshot_token"] != revision["before_state"]["snapshot_token"]
        or approval["approval_method"] != "explicit_apply_contract_approval"
    ):
        raise ApplyContractError("APPLY_CONTRACT_APPROVAL_MISMATCH")
    validate_timestamp(approval["approved_at"], "approved_at")
    preimage = {
        "object_kind": "sealed_apply_contract_revision",
        "sealed_schema_version": "sealed_apply_contract_revision.v1",
        "revision": revision,
        "contract_approval": approval,
        "approval_event_id": approval_event_id,
    }
    sealed = {**preimage, "sealed_contract_hash": canonical_sha256(preimage)}
    canonical_json_bytes(sealed, max_bytes=MAX_SEALED_REVISION_BYTES)
    return sealed


def validate_sealed_revision(value: Any) -> dict[str, Any]:
    sealed = require_closed_object(
        value,
        required={
            "object_kind",
            "sealed_schema_version",
            "revision",
            "contract_approval",
            "approval_event_id",
            "sealed_contract_hash",
        },
        label="sealed revision",
    )
    if (
        sealed["object_kind"] != "sealed_apply_contract_revision"
        or sealed["sealed_schema_version"] != "sealed_apply_contract_revision.v1"
    ):
        raise ApplyContractError("APPLY_CONTRACT_SEALED_REVISION_INVALID")
    expected = build_sealed_revision(
        sealed["revision"], sealed["contract_approval"], sealed["approval_event_id"]
    )
    if expected != sealed:
        raise ApplyContractError("APPLY_CONTRACT_SEALED_HASH_MISMATCH")
    return sealed


def load_revision(
    project_dir: str | Path, *, promotion_id: str, revision: int
) -> dict[str, Any]:
    raw = read_immutable_file(
        project_dir,
        revision_relative_path(promotion_id, revision),
        max_bytes=MAX_REVISION_BYTES,
        missing_code="APPLY_CONTRACT_REVISION_NOT_FOUND",
        unsafe_code="APPLY_CONTRACT_REVISION_CORRUPT",
    )
    try:
        parsed = strict_json_loads(raw, max_bytes=MAX_REVISION_BYTES)
        validated = validate_revision(parsed)
        if canonical_json_bytes(validated, max_bytes=MAX_REVISION_BYTES) != raw:
            raise ApplyContractError("APPLY_CONTRACT_REVISION_CORRUPT")
        return validated
    except ApplyContractError as exc:
        if exc.code == "APPLY_CONTRACT_REVISION_NOT_FOUND":
            raise
        raise ApplyContractError("APPLY_CONTRACT_REVISION_CORRUPT") from exc


def load_sealed_revision(
    project_dir: str | Path, *, promotion_id: str, revision: int
) -> dict[str, Any]:
    raw = read_immutable_file(
        project_dir,
        sealed_revision_relative_path(promotion_id, revision),
        max_bytes=MAX_SEALED_REVISION_BYTES,
        missing_code="APPLY_CONTRACT_SEALED_REVISION_NOT_FOUND",
        unsafe_code="APPLY_CONTRACT_SEALED_REVISION_CORRUPT",
    )
    try:
        parsed = strict_json_loads(raw, max_bytes=MAX_SEALED_REVISION_BYTES)
        validated = validate_sealed_revision(parsed)
        if canonical_json_bytes(validated, max_bytes=MAX_SEALED_REVISION_BYTES) != raw:
            raise ApplyContractError("APPLY_CONTRACT_SEALED_REVISION_CORRUPT")
        return validated
    except ApplyContractError as exc:
        if exc.code == "APPLY_CONTRACT_SEALED_REVISION_NOT_FOUND":
            raise
        raise ApplyContractError("APPLY_CONTRACT_SEALED_REVISION_CORRUPT") from exc


@dataclass(frozen=True)
class PreparationMaterial:
    artifact: dict[str, Any]
    artifact_bytes: bytes
    artifact_hash: str
    revision_bytes: bytes


def build_preparation_artifact(
    *,
    project_id: str,
    promotion_id: str,
    candidate_id: str,
    idempotency_key: str,
    preparation_scope_hash_value: str,
    canonical_request_body_hash: str,
    prior_lineage_expectations: dict[str, Any],
    supersession_kind: str,
    revision: dict[str, Any],
    artifact_created_at: str,
) -> PreparationMaterial:
    validate_revision(revision)
    prep_id = preparation_id(project_id, promotion_id, idempotency_key)
    revision_bytes = canonical_json_bytes(revision, max_bytes=MAX_REVISION_BYTES)
    artifact = {
        "object_kind": "apply_contract_preparation",
        "preparation_schema_version": "apply_contract_preparation.v1",
        "project_id": project_id,
        "promotion_id": promotion_id,
        "candidate_id": candidate_id,
        "preparation_id": prep_id,
        "preparation_path": preparation_relative_path(promotion_id, prep_id).as_posix(),
        "idempotency_key": idempotency_key,
        "preparation_scope_hash": preparation_scope_hash_value,
        "canonical_request_body_hash": canonical_request_body_hash,
        "requested_operation": revision["operation"],
        "destination": revision["destination"],
        "prior_lineage_expectations": prior_lineage_expectations,
        "assigned_revision": revision["revision"],
        "revision_path": revision_relative_path(promotion_id, revision["revision"]).as_posix(),
        "supersession_kind": supersession_kind,
        "revision_canonical_encoding": "base64url-no-padding",
        "revision_canonical_bytes_b64url": urlsafe_b64encode(revision_bytes).decode("ascii").rstrip("="),
        "revision_canonical_hash": hashlib.sha256(revision_bytes).hexdigest(),
        "revision_canonical_size": len(revision_bytes),
        "draft_scope_hash": revision["draft_scope_hash"],
        "approved_record_hash": revision["approved_record_hash"],
        "approved_record_size": revision["approved_record_size"],
        "source_candidate_snapshot_hash": revision["source_candidate_snapshot_hash"],
        "revision": revision,
        "artifact_created_at": artifact_created_at,
    }
    return validate_preparation_artifact(artifact)


def validate_preparation_artifact(value: Any) -> PreparationMaterial:
    artifact = require_closed_object(value, required=_PREPARATION_REQUIRED, label="preparation artifact")
    if artifact["object_kind"] != "apply_contract_preparation" or artifact["preparation_schema_version"] != "apply_contract_preparation.v1":
        raise ApplyContractError("APPLY_CONTRACT_PREPARATION_ARTIFACT_CORRUPT")
    for field in ("project_id", "promotion_id", "candidate_id"):
        validate_safe_id(artifact[field], field)
    validate_uuid_v4(artifact["idempotency_key"])
    expected_id = preparation_id(artifact["project_id"], artifact["promotion_id"], artifact["idempotency_key"])
    if artifact["preparation_id"] != expected_id or artifact["preparation_path"] != preparation_relative_path(artifact["promotion_id"], expected_id).as_posix():
        raise ApplyContractError("APPLY_CONTRACT_PREPARATION_ARTIFACT_CORRUPT")
    for field in ("preparation_scope_hash", "canonical_request_body_hash", "revision_canonical_hash", "draft_scope_hash", "approved_record_hash", "source_candidate_snapshot_hash"):
        validate_sha256(artifact[field], field)
    expectations = _validate_prior_lineage_expectations(artifact["prior_lineage_expectations"])
    validate_timestamp(artifact["artifact_created_at"], "artifact_created_at")
    if artifact["supersession_kind"] not in {"none", "draft", "sealed"} or artifact["revision_canonical_encoding"] != "base64url-no-padding":
        raise ApplyContractError("APPLY_CONTRACT_PREPARATION_ARTIFACT_CORRUPT")
    revision = validate_revision(artifact["revision"])
    if artifact["assigned_revision"] != revision["revision"] or artifact["revision_path"] != revision_relative_path(artifact["promotion_id"], revision["revision"]).as_posix():
        raise ApplyContractError("APPLY_CONTRACT_PREPARATION_ARTIFACT_CORRUPT")
    try:
        encoded = artifact["revision_canonical_bytes_b64url"]
        if not isinstance(encoded, str) or not _BASE64URL_RE.fullmatch(encoded) or "=" in encoded:
            raise ValueError
        revision_bytes = urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4))
    except (ValueError, TypeError) as exc:
        raise ApplyContractError("APPLY_CONTRACT_PREPARATION_ARTIFACT_CORRUPT") from exc
    canonical_revision = canonical_json_bytes(revision, max_bytes=MAX_REVISION_BYTES)
    if revision_bytes != canonical_revision:
        raise ApplyContractError("APPLY_CONTRACT_PREPARATION_HASH_MISMATCH")
    if artifact["revision_canonical_hash"] != hashlib.sha256(revision_bytes).hexdigest() or artifact["revision_canonical_size"] != len(revision_bytes):
        raise ApplyContractError("APPLY_CONTRACT_PREPARATION_HASH_MISMATCH")
    associated = {
        "project_id": revision["project_id"],
        "promotion_id": revision["promotion_id"],
        "candidate_id": revision["candidate_id"],
        "requested_operation": revision["operation"],
        "destination": revision["destination"],
        "draft_scope_hash": revision["draft_scope_hash"],
        "approved_record_hash": revision["approved_record_hash"],
        "approved_record_size": revision["approved_record_size"],
        "source_candidate_snapshot_hash": revision["source_candidate_snapshot_hash"],
    }
    if any(artifact[field] != expected for field, expected in associated.items()):
        raise ApplyContractError("APPLY_CONTRACT_PREPARATION_HASH_MISMATCH")
    expected_scope = preparation_scope_hash(
        project_id=artifact["project_id"],
        promotion_id=artifact["promotion_id"],
        requested_operation=artifact["requested_operation"],
        approved_destination_type=artifact["destination"]["approved_destination_type"],
        destination_key=artifact["destination"]["destination_key"],
        canonical_request_body_hash=artifact["canonical_request_body_hash"],
        expected_latest_revision=expectations["expected_latest_revision"],
        expected_latest_draft_scope_hash=expectations["expected_latest_draft_scope_hash"],
    )
    if artifact["preparation_scope_hash"] != expected_scope:
        raise ApplyContractError("APPLY_CONTRACT_PREPARATION_HASH_MISMATCH")
    artifact_bytes = canonical_json_bytes(artifact, max_bytes=MAX_PREPARATION_BYTES)
    return PreparationMaterial(artifact, artifact_bytes, hashlib.sha256(artifact_bytes).hexdigest(), revision_bytes)


def _safe_directory(project_dir: str | Path, relative: Path, *, create: bool) -> Path:
    root = Path(project_dir).resolve(strict=True)
    current = root
    for part in relative.parts:
        current = current / part
        if current.exists() or current.is_symlink():
            metadata = os.lstat(current)
            if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
                raise ApplyContractError("APPLY_CONTRACT_STORAGE_UNSAFE")
        elif create:
            current.mkdir(mode=0o700)
        else:
            raise FileNotFoundError(current)
    try:
        current.resolve(strict=True).relative_to(root)
    except ValueError as exc:
        raise ApplyContractError("APPLY_CONTRACT_STORAGE_UNSAFE") from exc
    return current


def read_immutable_file(project_dir: str | Path, relative: Path, *, max_bytes: int, missing_code: str, unsafe_code: str) -> bytes:
    parent = _safe_directory(project_dir, relative.parent, create=False)
    path = parent / relative.name
    try:
        metadata = os.lstat(path)
    except FileNotFoundError as exc:
        raise ApplyContractError(missing_code) from exc
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
        raise ApplyContractError(unsafe_code)
    if metadata.st_size > max_bytes:
        raise ApplyContractError(unsafe_code)
    raw = path.read_bytes()
    if len(raw) != metadata.st_size:
        raise ApplyContractError(unsafe_code)
    return raw


def publish_immutable_file(project_dir: str | Path, relative: Path, raw: bytes, *, conflict_code: str) -> bool:
    """No-overwrite publish; return True only for an exact existing replay."""

    parent = _safe_directory(project_dir, relative.parent, create=True)
    target = parent / relative.name
    if target.exists() or target.is_symlink():
        existing = read_immutable_file(project_dir, relative, max_bytes=len(raw), missing_code=conflict_code, unsafe_code=conflict_code)
        if existing != raw:
            raise ApplyContractError(conflict_code)
        return True
    temp = parent / f".tmp-{uuid.uuid4()}"
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(temp, flags, 0o600)
    try:
        with os.fdopen(descriptor, "wb", closefd=True) as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temp, target, follow_symlinks=False)
        except FileExistsError:
            existing = read_immutable_file(project_dir, relative, max_bytes=len(raw), missing_code=conflict_code, unsafe_code=conflict_code)
            if existing != raw:
                raise ApplyContractError(conflict_code)
            return True
        finally:
            temp.unlink(missing_ok=True)
        directory_fd = os.open(parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
        return False
    finally:
        temp.unlink(missing_ok=True)


def publish_preparation_artifact(project_dir: str | Path, material: PreparationMaterial) -> bool:
    validated = validate_preparation_artifact(material.artifact)
    return publish_immutable_file(
        project_dir,
        Path(validated.artifact["preparation_path"]),
        validated.artifact_bytes,
        conflict_code="APPLY_CONTRACT_PREPARATION_SCOPE_CONFLICT",
    )


def load_preparation_artifact(
    project_dir: str | Path, *, project_id: str, promotion_id: str, idempotency_key: str
) -> PreparationMaterial:
    prep_id = preparation_id(project_id, promotion_id, idempotency_key)
    relative = preparation_relative_path(promotion_id, prep_id)
    raw = read_immutable_file(
        project_dir,
        relative,
        max_bytes=MAX_PREPARATION_BYTES,
        missing_code="APPLY_CONTRACT_PREPARATION_ARTIFACT_MISSING",
        unsafe_code="APPLY_CONTRACT_PREPARATION_ARTIFACT_CORRUPT",
    )
    try:
        parsed = strict_json_loads(raw, max_bytes=MAX_PREPARATION_BYTES)
        material = validate_preparation_artifact(parsed)
    except ApplyContractError as exc:
        if exc.code.startswith("APPLY_CONTRACT_PREPARATION_"):
            raise
        raise ApplyContractError("APPLY_CONTRACT_PREPARATION_ARTIFACT_CORRUPT") from exc
    if material.artifact_bytes != raw:
        raise ApplyContractError("APPLY_CONTRACT_PREPARATION_ARTIFACT_CORRUPT")
    return material


def publish_revision_from_preparation(project_dir: str | Path, material: PreparationMaterial) -> bool:
    validated = validate_preparation_artifact(material.artifact)
    relative = Path(validated.artifact["revision_path"])
    contract_dir = _safe_directory(project_dir, relative.parent, create=True)
    existing_numbers: list[int] = []
    for entry in contract_dir.iterdir():
        match = _REVISION_NAME_RE.fullmatch(entry.name)
        if match:
            existing_numbers.append(int(match.group(1)))
    assigned = validated.artifact["assigned_revision"]
    if sorted(number for number in existing_numbers if number != assigned) != list(range(1, assigned)):
        raise ApplyContractError("APPLY_CONTRACT_PREPARATION_REVISION_CONFLICT")
    return publish_immutable_file(
        project_dir,
        relative,
        validated.revision_bytes,
        conflict_code="APPLY_CONTRACT_PREPARATION_REVISION_CONFLICT",
    )


def recover_preparation_revision(
    project_dir: str | Path,
    *,
    project_id: str,
    promotion_id: str,
    idempotency_key: str,
    expected_preparation_scope_hash: str,
) -> tuple[PreparationMaterial, bool]:
    """Resume artifact-to-revision publication without consulting mutable authority."""

    material = load_preparation_artifact(
        project_dir,
        project_id=project_id,
        promotion_id=promotion_id,
        idempotency_key=idempotency_key,
    )
    if material.artifact["preparation_scope_hash"] != expected_preparation_scope_hash:
        raise ApplyContractError("APPLY_CONTRACT_PREPARATION_SCOPE_CONFLICT")
    replayed_revision = publish_revision_from_preparation(project_dir, material)
    return material, replayed_revision


__all__ = (
    "ApplyContractError",
    "MAX_APPROVED_RECORD_BYTES",
    "MAX_JSON_DEPTH",
    "MAX_REQUEST_BYTES",
    "MAX_SAFE_INTEGER",
    "MAX_PREPARATION_BYTES",
    "MAX_REVISION_BYTES",
    "MAX_SEALED_REVISION_BYTES",
    "PreparationMaterial",
    "build_preparation_artifact",
    "build_revision",
    "build_sealed_revision",
    "canonical_json_bytes",
    "canonical_sha256",
    "require_closed_object",
    "require_integer",
    "require_string",
    "draft_scope_hash",
    "load_preparation_artifact",
    "load_revision",
    "load_sealed_revision",
    "preparation_id",
    "preparation_relative_path",
    "preparation_scope_hash",
    "publish_immutable_file",
    "publish_preparation_artifact",
    "publish_revision_from_preparation",
    "read_immutable_file",
    "recover_preparation_revision",
    "revision_relative_path",
    "sealed_revision_relative_path",
    "strict_json_loads",
    "validate_field_id",
    "validate_safe_id",
    "validate_sha256",
    "validate_timestamp",
    "validate_owner_identity",
    "validate_preparation_artifact",
    "validate_revision",
    "validate_sealed_revision",
    "validate_uuid_v4",
)
