"""Closed approved_record.v1 schemas and explicit create/update rules."""

from __future__ import annotations

import copy
import hashlib
import os
import stat
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from backend.story_knowledge.apply_contract import (
    ApplyContractError,
    MAX_APPROVED_RECORD_BYTES,
    MAX_SAFE_INTEGER,
    canonical_json_bytes,
    require_closed_object,
    require_integer,
    require_string,
    strict_json_loads,
    validate_field_id,
    validate_safe_id,
    validate_sha256,
)


ALL_APPROVED_DESTINATION_TYPES = frozenset(
    {
        "approved_character",
        "approved_location",
        "approved_timeline_event",
        "approved_relationship",
        "approved_organization",
        "approved_object",
        "approved_plot_thread",
        "approved_continuity_record",
        "approved_open_question",
        "approved_memory_index",
    }
)
ORDINARY_APPROVED_DESTINATION_TYPES = frozenset(
    ALL_APPROVED_DESTINATION_TYPES - {"approved_memory_index"}
)

_ENVELOPE_REQUIRED = {
    "schema_version",
    "record_version",
    "project_id",
    "destination_type",
    "destination_key",
    "source_candidate_id",
    "source_promotion_id",
    "source_candidate_snapshot_hash",
    "payload",
    "evidence_refs",
    "provenance_refs",
    "source_locators",
}


@dataclass(frozen=True)
class ApprovedRecordMaterial:
    record: dict[str, Any]
    canonical_bytes: bytes
    approved_record_hash: str
    approved_record_size: int


def _exact_unique(values: list[Any], label: str) -> None:
    seen: set[bytes] = set()
    for value in values:
        encoded = canonical_json_bytes(value)
        if encoded in seen:
            raise ApplyContractError("SCHEMA_ARRAY_ITEMS_NOT_UNIQUE", label)
        seen.add(encoded)


def _array(
    value: Any,
    *,
    label: str,
    minimum: int,
    maximum: int,
    validator: Callable[[Any], None],
    unique: bool = False,
) -> list[Any]:
    if not isinstance(value, list) or not minimum <= len(value) <= maximum:
        raise ApplyContractError("SCHEMA_ARRAY_INVALID", label)
    for item in value:
        validator(item)
    if unique:
        _exact_unique(value, label)
    return value


def _destination_type(value: Any, *, ordinary: bool) -> str:
    allowed = ORDINARY_APPROVED_DESTINATION_TYPES if ordinary else ALL_APPROVED_DESTINATION_TYPES
    if not isinstance(value, str) or value not in allowed:
        if value == "approved_memory_index" and ordinary:
            raise ApplyContractError("APPROVED_MEMORY_INDEX_ORDINARY_WRITE_FORBIDDEN")
        raise ApplyContractError("APPROVED_DESTINATION_TYPE_INVALID")
    return value


def approved_record_relative_path(
    destination_type: str,
    destination_key: str,
    *,
    ordinary: bool = True,
) -> Path:
    validated_type = _destination_type(destination_type, ordinary=ordinary)
    validated_key = validate_safe_id(destination_key, "destination_key")
    relative = Path(
        "writer_assistant",
        "approved_memory",
        validated_type,
        f"{validated_key}.json",
    )
    if len(relative.as_posix().encode("utf-8")) > 320:
        raise ApplyContractError("APPROVED_RECORD_PATH_TOO_LARGE")
    return relative


def approved_record_path(
    project_dir: str | Path,
    destination_type: str,
    destination_key: str,
    *,
    ordinary: bool = True,
) -> Path:
    return Path(project_dir) / approved_record_relative_path(
        destination_type,
        destination_key,
        ordinary=ordinary,
    )


def _validate_record_ref(value: Any) -> None:
    item = require_closed_object(
        value,
        required={"destination_type", "destination_key", "record_version", "content_hash"},
        label="record reference",
    )
    _destination_type(item["destination_type"], ordinary=False)
    validate_safe_id(item["destination_key"], "destination_key")
    require_integer(item["record_version"], label="record_version", minimum=1, maximum=2_147_483_647)
    validate_sha256(item["content_hash"], "content_hash")


def _validate_record_refs(value: Any, label: str) -> None:
    _array(value, label=label, minimum=0, maximum=128, validator=_validate_record_ref, unique=True)


def _validate_nullable_hash(value: Any, label: str) -> None:
    if value is not None:
        validate_sha256(value, label)


def _validate_evidence_ref(value: Any) -> None:
    item = require_closed_object(
        value,
        required={"ref_id", "locator_id"},
        optional={"content_hash", "note"},
        label="evidence reference",
    )
    validate_safe_id(item["ref_id"], "ref_id")
    validate_safe_id(item["locator_id"], "locator_id")
    if "content_hash" in item:
        _validate_nullable_hash(item["content_hash"], "content_hash")
    if "note" in item:
        require_string(item["note"], label="note", maximum=2048)


def _validate_provenance_ref(value: Any) -> None:
    item = require_closed_object(
        value,
        required={"provenance_id", "source_kind", "source_id"},
        optional={"locator_id", "content_hash"},
        label="provenance reference",
    )
    validate_safe_id(item["provenance_id"], "provenance_id")
    validate_field_id(item["source_kind"], "source_kind")
    require_string(item["source_id"], label="source_id", minimum=1, maximum=256)
    if "locator_id" in item and item["locator_id"] is not None:
        validate_safe_id(item["locator_id"], "locator_id")
    if "content_hash" in item:
        _validate_nullable_hash(item["content_hash"], "content_hash")


def _validate_source_locator(value: Any) -> None:
    item = require_closed_object(
        value,
        required={"locator_id", "locator_kind", "locator"},
        optional={"content_hash"},
        label="source locator",
    )
    validate_safe_id(item["locator_id"], "locator_id")
    validate_field_id(item["locator_kind"], "locator_kind")
    require_string(item["locator"], label="locator", minimum=1, maximum=2048)
    if "content_hash" in item:
        _validate_nullable_hash(item["content_hash"], "content_hash")


def _validate_id_array(value: Any, label: str) -> None:
    _array(
        value,
        label=label,
        minimum=1,
        maximum=32,
        validator=lambda item: validate_safe_id(item, label),
        unique=True,
    )


def _validate_fact_value(value: Any) -> None:
    if value is None or isinstance(value, bool):
        return
    if isinstance(value, int):
        if abs(value) <= MAX_SAFE_INTEGER:
            return
    elif isinstance(value, float):
        canonical_json_bytes(value)
        if abs(value) <= MAX_SAFE_INTEGER:
            return
    elif isinstance(value, str) and len(value) <= 4096:
        canonical_json_bytes(value)
        return
    raise ApplyContractError("FACT_VALUE_INVALID")


def _validate_fact(value: Any) -> None:
    item = require_closed_object(
        value,
        required={"field", "value", "evidence_ref_ids", "provenance_ref_ids"},
        label="fact",
    )
    validate_field_id(item["field"], "field")
    _validate_fact_value(item["value"])
    _validate_id_array(item["evidence_ref_ids"], "evidence_ref_ids")
    _validate_id_array(item["provenance_ref_ids"], "provenance_ref_ids")


def _validate_facts(value: Any, *, required: bool) -> None:
    _array(
        value,
        label="facts",
        minimum=1 if required else 0,
        maximum=256,
        validator=_validate_fact,
    )


def _validate_string_array(value: Any, label: str, maximum: int, item_maximum: int) -> None:
    _array(
        value,
        label=label,
        minimum=0,
        maximum=maximum,
        validator=lambda item: require_string(item, label=label, minimum=1, maximum=item_maximum),
        unique=True,
    )


def _payload_schema(
    payload: Any,
    *,
    payload_type: str,
    required: set[str],
    optional: set[str],
) -> dict[str, Any]:
    item = require_closed_object(
        payload,
        required={"payload_type", *required},
        optional=optional,
        label=f"{payload_type} payload",
    )
    if item["payload_type"] != payload_type:
        raise ApplyContractError("APPROVED_PAYLOAD_TYPE_MISMATCH")
    return item


def _common_optional_payload(item: dict[str, Any]) -> None:
    if "related_record_refs" in item:
        _validate_record_refs(item["related_record_refs"], "related_record_refs")


def _validate_payload(payload: Any, destination_type: str, *, ordinary: bool) -> None:
    if destination_type == "approved_character":
        item = _payload_schema(payload, payload_type=destination_type, required={"display_name", "facts"}, optional={"aliases", "related_record_refs"})
        require_string(item["display_name"], label="display_name", minimum=1, maximum=512)
        _validate_facts(item["facts"], required=True)
        if "aliases" in item:
            _validate_string_array(item["aliases"], "aliases", 64, 512)
    elif destination_type == "approved_location":
        item = _payload_schema(payload, payload_type=destination_type, required={"display_name", "facts"}, optional={"location_kind", "parent_location_refs", "related_record_refs"})
        require_string(item["display_name"], label="display_name", minimum=1, maximum=512)
        _validate_facts(item["facts"], required=True)
        if "location_kind" in item:
            require_string(item["location_kind"], label="location_kind", minimum=1, maximum=128)
        if "parent_location_refs" in item:
            _array(item["parent_location_refs"], label="parent_location_refs", minimum=0, maximum=16, validator=_validate_record_ref, unique=True)
    elif destination_type == "approved_timeline_event":
        item = _payload_schema(payload, payload_type=destination_type, required={"event_label", "facts"}, optional={"sequence_label", "participant_refs", "location_refs", "related_record_refs"})
        require_string(item["event_label"], label="event_label", minimum=1, maximum=512)
        _validate_facts(item["facts"], required=True)
        if "sequence_label" in item:
            require_string(item["sequence_label"], label="sequence_label", minimum=1, maximum=256)
        for field in ("participant_refs", "location_refs"):
            if field in item:
                _validate_record_refs(item[field], field)
    elif destination_type == "approved_relationship":
        item = _payload_schema(payload, payload_type=destination_type, required={"relationship_label", "endpoint_refs", "facts"}, optional={"relationship_kind", "related_record_refs"})
        require_string(item["relationship_label"], label="relationship_label", minimum=1, maximum=512)
        _array(item["endpoint_refs"], label="endpoint_refs", minimum=2, maximum=2, validator=_validate_record_ref, unique=True)
        _validate_facts(item["facts"], required=True)
        if "relationship_kind" in item:
            require_string(item["relationship_kind"], label="relationship_kind", minimum=1, maximum=128)
    elif destination_type == "approved_organization":
        item = _payload_schema(payload, payload_type=destination_type, required={"display_name", "facts"}, optional={"organization_kind", "member_refs", "location_refs", "related_record_refs"})
        require_string(item["display_name"], label="display_name", minimum=1, maximum=512)
        _validate_facts(item["facts"], required=True)
        if "organization_kind" in item:
            require_string(item["organization_kind"], label="organization_kind", minimum=1, maximum=128)
        for field in ("member_refs", "location_refs"):
            if field in item:
                _validate_record_refs(item[field], field)
    elif destination_type == "approved_object":
        item = _payload_schema(payload, payload_type=destination_type, required={"display_name", "facts"}, optional={"object_kind", "holder_refs", "location_refs", "related_record_refs"})
        require_string(item["display_name"], label="display_name", minimum=1, maximum=512)
        _validate_facts(item["facts"], required=True)
        if "object_kind" in item:
            require_string(item["object_kind"], label="object_kind", minimum=1, maximum=128)
        for field in ("holder_refs", "location_refs"):
            if field in item:
                _validate_record_refs(item[field], field)
    elif destination_type == "approved_plot_thread":
        item = _payload_schema(payload, payload_type=destination_type, required={"thread_label", "facts"}, optional={"participant_refs", "location_refs", "related_record_refs"})
        require_string(item["thread_label"], label="thread_label", minimum=1, maximum=512)
        _validate_facts(item["facts"], required=True)
        for field in ("participant_refs", "location_refs"):
            if field in item:
                _validate_record_refs(item[field], field)
    elif destination_type == "approved_continuity_record":
        item = _payload_schema(payload, payload_type=destination_type, required={"continuity_label", "facts"}, optional={"related_record_refs"})
        require_string(item["continuity_label"], label="continuity_label", minimum=1, maximum=512)
        _validate_facts(item["facts"], required=True)
    elif destination_type == "approved_open_question":
        item = _payload_schema(payload, payload_type=destination_type, required={"question_text", "facts"}, optional={"related_record_refs"})
        require_string(item["question_text"], label="question_text", minimum=1, maximum=2048)
        _validate_facts(item["facts"], required=False)
    elif destination_type == "approved_memory_index" and not ordinary:
        item = _payload_schema(payload, payload_type=destination_type, required={"entries"}, optional=set())
        _array(item["entries"], label="entries", minimum=0, maximum=1024, validator=_validate_memory_index_entry)
    else:
        _destination_type(destination_type, ordinary=ordinary)
        raise ApplyContractError("APPROVED_PAYLOAD_TYPE_MISMATCH")
    _common_optional_payload(item)


def _validate_memory_index_entry(value: Any) -> None:
    item = require_closed_object(
        value,
        required={"destination_type", "destination_key", "destination_path", "record_version", "content_hash"},
        label="memory index entry",
    )
    _destination_type(item["destination_type"], ordinary=False)
    key = validate_safe_id(item["destination_key"], "destination_key")
    expected = approved_record_relative_path(item["destination_type"], key, ordinary=False).as_posix()
    if item["destination_path"] != expected:
        raise ApplyContractError("APPROVED_RECORD_PATH_MISMATCH")
    require_integer(item["record_version"], label="record_version", minimum=1, maximum=2_147_483_647)
    validate_sha256(item["content_hash"], "content_hash")


def validate_approved_record(
    record: Any,
    *,
    ordinary: bool = True,
) -> dict[str, Any]:
    item = require_closed_object(
        record,
        required=_ENVELOPE_REQUIRED,
        optional={"owner_note"},
        label="approved record",
    )
    if item["schema_version"] != "approved_record.v1":
        raise ApplyContractError("APPROVED_RECORD_SCHEMA_VERSION_INVALID")
    require_integer(item["record_version"], label="record_version", minimum=1, maximum=2_147_483_647)
    validate_safe_id(item["project_id"], "project_id")
    destination_type = _destination_type(item["destination_type"], ordinary=ordinary)
    validate_safe_id(item["destination_key"], "destination_key")
    validate_safe_id(item["source_candidate_id"], "source_candidate_id")
    validate_safe_id(item["source_promotion_id"], "source_promotion_id")
    validate_sha256(item["source_candidate_snapshot_hash"], "source_candidate_snapshot_hash")
    _validate_payload(item["payload"], destination_type, ordinary=ordinary)
    _array(item["evidence_refs"], label="evidence_refs", minimum=1, maximum=128, validator=_validate_evidence_ref)
    _array(item["provenance_refs"], label="provenance_refs", minimum=1, maximum=128, validator=_validate_provenance_ref)
    _array(item["source_locators"], label="source_locators", minimum=1, maximum=128, validator=_validate_source_locator)
    if "owner_note" in item:
        require_string(item["owner_note"], label="owner_note", maximum=4096)

    material = canonical_json_bytes(item)
    if len(material) > MAX_APPROVED_RECORD_BYTES:
        raise ApplyContractError("APPROVED_RECORD_TOO_LARGE")
    return copy.deepcopy(item)


def approved_record_material(
    record: Any,
    *,
    ordinary: bool = True,
) -> ApprovedRecordMaterial:
    validated = validate_approved_record(record, ordinary=ordinary)
    encoded = canonical_json_bytes(validated)
    return ApprovedRecordMaterial(
        record=validated,
        canonical_bytes=encoded,
        approved_record_hash=hashlib.sha256(encoded).hexdigest(),
        approved_record_size=len(encoded),
    )


def build_approved_record(
    *,
    record_version: int,
    project_id: str,
    destination_type: str,
    destination_key: str,
    source_candidate_id: str,
    source_promotion_id: str,
    source_candidate_snapshot_hash: str,
    payload: dict[str, Any],
    evidence_refs: list[dict[str, Any]],
    provenance_refs: list[dict[str, Any]],
    source_locators: list[dict[str, Any]],
    owner_note: str | None = None,
    ordinary: bool = True,
) -> ApprovedRecordMaterial:
    record: dict[str, Any] = {
        "schema_version": "approved_record.v1",
        "record_version": record_version,
        "project_id": project_id,
        "destination_type": destination_type,
        "destination_key": destination_key,
        "source_candidate_id": source_candidate_id,
        "source_promotion_id": source_promotion_id,
        "source_candidate_snapshot_hash": source_candidate_snapshot_hash,
        "payload": copy.deepcopy(payload),
        "evidence_refs": copy.deepcopy(evidence_refs),
        "provenance_refs": copy.deepcopy(provenance_refs),
        "source_locators": copy.deepcopy(source_locators),
    }
    if owner_note is not None:
        record["owner_note"] = owner_note
    return approved_record_material(record, ordinary=ordinary)


def validate_record_operation(
    operation: str,
    proposed_record: Any,
    *,
    before_record: Any | None,
) -> ApprovedRecordMaterial:
    """Validate explicit operation and versions without inferring from existence."""

    proposed = approved_record_material(proposed_record)
    if operation == "create":
        if before_record is not None:
            raise ApplyContractError("CREATE_REQUIRES_ABSENT_BEFORE_STATE")
        if proposed.record["record_version"] != 1:
            raise ApplyContractError("CREATE_RECORD_VERSION_INVALID")
        return proposed
    if operation != "update":
        raise ApplyContractError("APPLY_OPERATION_INVALID")
    if before_record is None:
        raise ApplyContractError("UPDATE_REQUIRES_PRESENT_BEFORE_STATE")
    before = approved_record_material(before_record)
    for field in ("project_id", "destination_type", "destination_key"):
        if before.record[field] != proposed.record[field]:
            raise ApplyContractError("UPDATE_RECORD_IDENTITY_MISMATCH")
    prior_version = before.record["record_version"]
    if prior_version >= 2_147_483_647 or proposed.record["record_version"] != prior_version + 1:
        raise ApplyContractError("UPDATE_RECORD_VERSION_INVALID")
    return proposed


def load_approved_record(path: str | Path, *, ordinary: bool = True) -> ApprovedRecordMaterial:
    raw = Path(path).read_bytes()
    parsed = strict_json_loads(raw, max_bytes=MAX_APPROVED_RECORD_BYTES)
    material = approved_record_material(parsed, ordinary=ordinary)
    if raw != material.canonical_bytes:
        raise ApplyContractError("APPROVED_RECORD_NONCANONICAL")
    return material


def _approved_directory(
    project_dir: str | Path, relative: Path, *, create: bool
) -> Path:
    root = Path(project_dir).resolve(strict=True)
    current = root
    for part in relative.parts:
        current = current / part
        if current.exists() or current.is_symlink():
            metadata = os.lstat(current)
            if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
                raise ApplyContractError("APPROVED_RECORD_UNSAFE_PATH")
        elif create:
            current.mkdir(mode=0o700)
        else:
            raise FileNotFoundError(current)
    try:
        current.resolve(strict=True).relative_to(root)
    except ValueError as exc:
        raise ApplyContractError("APPROVED_RECORD_UNSAFE_PATH") from exc
    return current


def _load_safe_target(path: Path, *, ordinary: bool = True) -> ApprovedRecordMaterial:
    try:
        metadata = os.lstat(path)
    except FileNotFoundError as exc:
        raise ApplyContractError("APPROVED_RECORD_NOT_FOUND") from exc
    if (
        stat.S_ISLNK(metadata.st_mode)
        or not stat.S_ISREG(metadata.st_mode)
        or metadata.st_nlink != 1
        or metadata.st_size > MAX_APPROVED_RECORD_BYTES
    ):
        raise ApplyContractError("APPROVED_RECORD_UNSAFE_PATH")
    material = load_approved_record(path, ordinary=ordinary)
    if len(material.canonical_bytes) != metadata.st_size:
        raise ApplyContractError("APPROVED_RECORD_READ_CHANGED")
    return material


def commit_approved_record(
    project_dir: str | Path,
    *,
    operation: str,
    before_record: dict[str, Any] | None,
    proposed_record: dict[str, Any],
) -> ApprovedRecordMaterial:
    """Atomically create or replace exactly one approved record."""

    proposed = validate_record_operation(
        operation, proposed_record, before_record=before_record
    )
    relative = approved_record_relative_path(
        proposed.record["destination_type"], proposed.record["destination_key"]
    )
    parent = _approved_directory(project_dir, relative.parent, create=True)
    target = parent / relative.name

    if operation == "create":
        if target.exists() or target.is_symlink():
            raise ApplyContractError("CREATE_REQUIRES_ABSENT_BEFORE_STATE")
    else:
        current = _load_safe_target(target)
        expected = approved_record_material(before_record)
        if (
            current.approved_record_hash != expected.approved_record_hash
            or current.approved_record_size != expected.approved_record_size
            or current.record != expected.record
        ):
            raise ApplyContractError("APPLY_CONTRACT_BEFORE_STATE_CHANGED")

    temporary = parent / f".tmp-{uuid.uuid4()}"
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_CLOEXEC", 0)
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(temporary, flags, 0o600)
    try:
        with os.fdopen(descriptor, "wb", closefd=True) as handle:
            handle.write(proposed.canonical_bytes)
            handle.flush()
            os.fsync(handle.fileno())

        if operation == "create":
            if target.exists() or target.is_symlink():
                raise ApplyContractError("CREATE_REQUIRES_ABSENT_BEFORE_STATE")
            try:
                os.link(temporary, target, follow_symlinks=False)
            except FileExistsError as exc:
                raise ApplyContractError("CREATE_REQUIRES_ABSENT_BEFORE_STATE") from exc
            temporary.unlink()
        else:
            current = _load_safe_target(target)
            expected = approved_record_material(before_record)
            if (
                current.approved_record_hash != expected.approved_record_hash
                or current.approved_record_size != expected.approved_record_size
                or current.record != expected.record
            ):
                raise ApplyContractError("APPLY_CONTRACT_BEFORE_STATE_CHANGED")
            os.replace(temporary, target)

        directory_fd = os.open(parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
        committed = _load_safe_target(target)
        if (
            committed.approved_record_hash != proposed.approved_record_hash
            or committed.approved_record_size != proposed.approved_record_size
            or committed.record != proposed.record
        ):
            raise ApplyContractError("APPLY_COMMITTED_RECORD_MISMATCH")
        return committed
    finally:
        temporary.unlink(missing_ok=True)


__all__ = (
    "ALL_APPROVED_DESTINATION_TYPES",
    "ApprovedRecordMaterial",
    "ORDINARY_APPROVED_DESTINATION_TYPES",
    "approved_record_material",
    "approved_record_path",
    "approved_record_relative_path",
    "build_approved_record",
    "commit_approved_record",
    "load_approved_record",
    "validate_approved_record",
    "validate_record_operation",
)
