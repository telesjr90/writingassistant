from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import re
from typing import Any


SOURCE_IDENTITY_CONTRACT_VERSION = "writer-assistant-source-identity.v1"
SOURCE_HASH_ALGORITHM = "sha256"
SOURCE_HASH_BASIS = "utf-8-exact"
CHAR_OFFSET_BASIS = "unicode-code-points-zero-based-half-open"
BYTE_OFFSET_BASIS = "utf-8-bytes-zero-based-half-open"

_SHA256_PATTERN = re.compile(r"[0-9a-f]{64}\Z")

_SOURCE_TYPES = frozenset(
    {
        "scene",
        "chapter",
        "note",
        "material",
        "bible",
        "storyform",
        "omi",
        "imported_context",
    }
)

_SEGMENT_TYPES = frozenset(
    {
        "document",
        "section",
        "chapter",
        "scene",
        "paragraph",
        "sentence",
        "line",
        "token_window",
        "custom",
    }
)

_PRECISION_VALUES = frozenset(
    {
        "exact",
        "normalized",
        "approximate",
        "document_only",
        "unknown",
    }
)

_SOURCE_DOCUMENT_FIELDS = frozenset(
    {
        "project_id",
        "source_document_type",
        "source_document_id",
        "source_document_version",
        "source_label",
        "source_path_hint",
        "content_hash",
        "content_hash_algorithm",
        "created_at",
        "updated_at",
    }
)

_SEGMENT_FIELDS = frozenset(
    {
        "segment_id",
        "segment_type",
        "segment_index",
        "section_id",
        "chapter_id",
        "scene_id",
        "paragraph_index",
        "sentence_index",
        "line_start",
        "line_end",
        "char_start",
        "char_end",
        "byte_start",
        "byte_end",
        "token_start",
        "token_end",
        "text_excerpt",
        "excerpt_hash",
    }
)

_SOURCE_MAP_FIELDS = frozenset(
    {
        "source_map_id",
        "project_id",
        "source_document",
        "snapshot_id",
        "snapshot_hash",
        "snapshot_hash_algorithm",
        "snapshot_created_at",
        "text_encoding",
        "normalization_policy",
        "line_index_available",
        "char_offset_policy",
        "byte_offset_policy",
        "token_offset_policy",
        "segments",
    }
)

_LOCATOR_FIELDS = frozenset(
    {
        "project_id",
        "source_document_type",
        "source_document_id",
        "source_document_version",
        "source_map_id",
        "snapshot_id",
        "snapshot_hash",
        "segment_id",
        "section_id",
        "chapter_id",
        "scene_id",
        "paragraph_index",
        "sentence_index",
        "line_start",
        "line_end",
        "char_start",
        "char_end",
        "byte_start",
        "byte_end",
        "token_start",
        "token_end",
        "locator_precision",
        "source_label",
        "source_hash",
        "char_offset_basis",
        "byte_offset_basis",
        "line_offset_basis",
        "token_offset_basis",
    }
)

_OFFSET_PAIRS = (
    ("line_start", "line_end"),
    ("char_start", "char_end"),
    ("byte_start", "byte_end"),
    ("token_start", "token_end"),
)

_OPTIONAL_ID_FIELDS = (
    "source_map_id",
    "snapshot_id",
    "segment_id",
    "section_id",
    "chapter_id",
    "scene_id",
)


def _require_mapping(value, label):
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a mapping")
    return value


def _require_fields(payload, fields):
    for field in fields:
        if field not in payload:
            raise ValueError(f"missing required field: {field}")


def _reject_unknown_fields(payload, fields):
    for field in payload:
        if field not in fields:
            raise ValueError(f"unexpected field: {field}")


def _validate_string(value, label, *, allow_empty=False):
    if not isinstance(value, str):
        raise ValueError(f"{label} must be a string")
    if not allow_empty and not value:
        raise ValueError(f"{label} must be non-empty")
    return value


def _validate_safe_id(value, label):
    _validate_string(value, label)
    if not value.strip():
        raise ValueError(f"{label} must be path-safe")
    if value in (".", ".."):
        raise ValueError(f"{label} must be path-safe")
    if "/" in value or "\\" in value:
        raise ValueError(f"{label} must be path-safe")
    if ".." in value:
        raise ValueError(f"{label} must be path-safe")
    if value.startswith("/"):
        raise ValueError(f"{label} must be path-safe")
    if len(value) >= 2 and value[1] == ":" and value[0].isalpha():
        raise ValueError(f"{label} must be path-safe")
    return value


def _validate_hint(value, label):
    _validate_string(value, label, allow_empty=True)
    if value.startswith("/") or value.startswith("\\"):
        raise ValueError(f"{label} must be display metadata")
    if ".." in value:
        raise ValueError(f"{label} must be display metadata")
    if len(value) >= 2 and value[1] == ":" and value[0].isalpha():
        raise ValueError(f"{label} must be display metadata")
    return value


def _validate_non_negative_int_or_none(value, label):
    if value is None:
        return value
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{label} must be None or a non-negative integer")
    if value < 0:
        raise ValueError(f"{label} must be None or a non-negative integer")
    return value


def _validate_non_negative_int(value, label):
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{label} must be a non-negative integer")
    if value < 0:
        raise ValueError(f"{label} must be a non-negative integer")
    return value


def _validate_offset_pairs(payload):
    for start_field, end_field in _OFFSET_PAIRS:
        if start_field in payload:
            _validate_non_negative_int_or_none(payload[start_field], start_field)
        if end_field in payload:
            _validate_non_negative_int_or_none(payload[end_field], end_field)
        start_value = payload.get(start_field)
        end_value = payload.get(end_field)
        if start_value is not None and end_value is not None and end_value < start_value:
            raise ValueError(f"{end_field} must be greater than or equal to {start_field}")


def _validate_optional_index(payload, field):
    if field in payload:
        _validate_non_negative_int_or_none(payload[field], field)


def validate_source_document_ref(source_document):
    payload = _require_mapping(source_document, "source_document")
    _require_fields(payload, _SOURCE_DOCUMENT_FIELDS)
    _reject_unknown_fields(payload, _SOURCE_DOCUMENT_FIELDS)

    _validate_safe_id(payload["project_id"], "project_id")
    _validate_safe_id(payload["source_document_id"], "source_document_id")
    if payload["source_document_type"] not in _SOURCE_TYPES:
        raise ValueError("source_document_type is not allowed")

    for field in (
        "source_document_version",
        "source_label",
        "content_hash",
        "content_hash_algorithm",
        "created_at",
        "updated_at",
    ):
        _validate_string(payload[field], field)
    _validate_hint(payload["source_path_hint"], "source_path_hint")

    return deepcopy(payload)


def validate_source_segment(segment):
    payload = _require_mapping(segment, "segment")
    _require_fields(payload, _SEGMENT_FIELDS)
    _reject_unknown_fields(payload, _SEGMENT_FIELDS)

    _validate_safe_id(payload["segment_id"], "segment_id")
    if payload["segment_type"] not in _SEGMENT_TYPES:
        raise ValueError("segment_type is not allowed")
    _validate_non_negative_int(payload["segment_index"], "segment_index")
    for field in _OPTIONAL_ID_FIELDS[3:]:
        if payload[field] is not None:
            _validate_safe_id(payload[field], field)
    _validate_optional_index(payload, "paragraph_index")
    _validate_optional_index(payload, "sentence_index")
    _validate_offset_pairs(payload)
    _validate_string(payload["text_excerpt"], "text_excerpt", allow_empty=True)
    _validate_string(payload["excerpt_hash"], "excerpt_hash")

    return deepcopy(payload)


def validate_source_map(source_map):
    payload = _require_mapping(source_map, "source_map")
    _require_fields(payload, _SOURCE_MAP_FIELDS)
    _reject_unknown_fields(payload, _SOURCE_MAP_FIELDS)

    _validate_safe_id(payload["source_map_id"], "source_map_id")
    _validate_safe_id(payload["project_id"], "project_id")
    _validate_safe_id(payload["snapshot_id"], "snapshot_id")
    validate_source_document_ref(payload["source_document"])

    for field in (
        "snapshot_hash",
        "snapshot_hash_algorithm",
        "snapshot_created_at",
        "text_encoding",
        "normalization_policy",
        "char_offset_policy",
        "byte_offset_policy",
        "token_offset_policy",
    ):
        _validate_string(payload[field], field)

    if not isinstance(payload["line_index_available"], bool):
        raise ValueError("line_index_available must be boolean")

    segments = payload["segments"]
    if not isinstance(segments, list):
        raise ValueError("segments must be a list")
    if not segments:
        raise ValueError("segments must not be empty")
    for segment in segments:
        validate_source_segment(segment)

    return deepcopy(payload)


def validate_source_locator(locator, *, allow_exact_byte_only=False):
    payload = _require_mapping(locator, "source_locator")
    _require_fields(
        payload,
        ("project_id", "source_document_type", "source_document_id", "locator_precision"),
    )
    _reject_unknown_fields(payload, _LOCATOR_FIELDS)

    _validate_safe_id(payload["project_id"], "project_id")
    _validate_safe_id(payload["source_document_id"], "source_document_id")
    if payload["source_document_type"] not in _SOURCE_TYPES:
        raise ValueError("source_document_type is not allowed")
    if payload["locator_precision"] not in _PRECISION_VALUES:
        raise ValueError("locator_precision is not allowed")

    for field in _OPTIONAL_ID_FIELDS:
        if field in payload and payload[field] is not None:
            _validate_safe_id(payload[field], field)
    for field in ("paragraph_index", "sentence_index"):
        _validate_optional_index(payload, field)
    _validate_offset_pairs(payload)

    precision = payload["locator_precision"]
    if precision not in ("document_only", "unknown"):
        has_character_range = (
            payload.get("char_start") is not None
            and payload.get("char_end") is not None
        )
        has_byte_range = (
            payload.get("byte_start") is not None
            and payload.get("byte_end") is not None
        )
        if not has_character_range and not (allow_exact_byte_only and has_byte_range):
            raise ValueError("character offsets are required")

    for range_prefix in ("char", "byte", "line", "token"):
        start_present = payload.get(f"{range_prefix}_start") is not None
        end_present = payload.get(f"{range_prefix}_end") is not None
        if start_present != end_present:
            raise ValueError(f"{range_prefix} offsets must form a complete range")

    basis_values = {
        "char_offset_basis": CHAR_OFFSET_BASIS,
        "byte_offset_basis": BYTE_OFFSET_BASIS,
    }
    for field, expected in basis_values.items():
        if field in payload and payload[field] is not None:
            _validate_string(payload[field], field)
            if payload[field] != expected:
                raise ValueError(f"{field} is not supported")
    for field in ("line_offset_basis", "token_offset_basis"):
        if field in payload and payload[field] is not None:
            _validate_string(payload[field], field)

    for field in ("source_document_version", "snapshot_hash", "source_label", "source_hash"):
        if field in payload and payload[field] is not None:
            _validate_string(payload[field], field, allow_empty=True)

    return deepcopy(payload)


class SourceOwnership(str, Enum):
    OWNER_AUTHORED = "owner_authored"
    OWNER_SELECTED_IMPORTED = "owner_selected_imported"
    APP_OWNED_DERIVED = "app_owned_derived"


class SourceIdentityValidationError(ValueError):
    """Raised when an exact source identity or offset range is not provable."""


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _checked_optional_safe_id(value: str | None, label: str) -> str | None:
    if value is not None:
        try:
            _validate_safe_id(value, label)
        except ValueError as exc:
            raise SourceIdentityValidationError(str(exc)) from exc
    return value


def derive_source_snapshot_id(
    *,
    contract_version: str,
    project_id: str,
    source_document_type: str,
    source_document_id: str,
    source_document_version: str,
    source_ownership: SourceOwnership | str,
    section_id: str | None,
    chapter_id: str | None,
    scene_id: str | None,
    content_hash: str,
    hash_algorithm: str,
    hash_basis: str,
) -> str:
    """Derive the path-independent ID for one exact logical source snapshot."""

    snapshot_basis = {
        "contract_version": contract_version,
        "project_id": project_id,
        "source_document_type": source_document_type,
        "source_document_id": source_document_id,
        "source_document_version": source_document_version,
        "source_ownership": (
            source_ownership.value
            if isinstance(source_ownership, SourceOwnership)
            else source_ownership
        ),
        "section_id": section_id,
        "chapter_id": chapter_id,
        "scene_id": scene_id,
        "content_hash": content_hash,
        "hash_algorithm": hash_algorithm,
        "hash_basis": hash_basis,
    }
    snapshot_digest = hashlib.sha256(
        _canonical_json(snapshot_basis).encode("utf-8")
    ).hexdigest()
    return f"snapshot-{snapshot_digest}"


@dataclass(frozen=True)
class SourceIdentity:
    """Path-independent identity for one exact owner-selected source snapshot."""

    project_id: str
    source_document_type: str
    source_document_id: str
    source_document_version: str
    source_ownership: SourceOwnership | str
    snapshot_id: str
    content_hash: str
    source_map_id: str | None = None
    section_id: str | None = None
    chapter_id: str | None = None
    scene_id: str | None = None
    hash_algorithm: str = SOURCE_HASH_ALGORITHM
    hash_basis: str = SOURCE_HASH_BASIS
    text_encoding: str = "utf-8"
    normalization_policy: str = "none-exact-owner-input"
    contract_version: str = SOURCE_IDENTITY_CONTRACT_VERSION

    def __post_init__(self) -> None:
        try:
            _validate_safe_id(self.project_id, "project_id")
            _validate_safe_id(self.source_document_id, "source_document_id")
            _validate_safe_id(self.snapshot_id, "snapshot_id")
        except ValueError as exc:
            raise SourceIdentityValidationError(str(exc)) from exc
        if self.source_document_type not in _SOURCE_TYPES:
            raise SourceIdentityValidationError("source_document_type is not allowed")
        _validate_string(self.source_document_version, "source_document_version")
        try:
            ownership = SourceOwnership(self.source_ownership)
        except (TypeError, ValueError) as exc:
            raise SourceIdentityValidationError("source_ownership is not allowed") from exc
        object.__setattr__(self, "source_ownership", ownership)
        for field_name in ("source_map_id", "section_id", "chapter_id", "scene_id"):
            _checked_optional_safe_id(getattr(self, field_name), field_name)
        if not isinstance(self.content_hash, str) or not _SHA256_PATTERN.fullmatch(
            self.content_hash
        ):
            raise SourceIdentityValidationError(
                "content_hash must be a lowercase SHA-256 hex digest"
            )
        if self.hash_algorithm != SOURCE_HASH_ALGORITHM:
            raise SourceIdentityValidationError("hash_algorithm must be sha256")
        if self.hash_basis != SOURCE_HASH_BASIS:
            raise SourceIdentityValidationError("hash_basis must identify exact UTF-8 bytes")
        if self.text_encoding != "utf-8":
            raise SourceIdentityValidationError("text_encoding must be utf-8")
        if self.normalization_policy != "none-exact-owner-input":
            raise SourceIdentityValidationError(
                "normalization_policy must preserve exact owner input"
            )
        if self.contract_version != SOURCE_IDENTITY_CONTRACT_VERSION:
            raise SourceIdentityValidationError("unsupported source identity contract_version")
        expected_snapshot_id = derive_source_snapshot_id(
            contract_version=self.contract_version,
            project_id=self.project_id,
            source_document_type=self.source_document_type,
            source_document_id=self.source_document_id,
            source_document_version=self.source_document_version,
            source_ownership=self.source_ownership,
            section_id=self.section_id,
            chapter_id=self.chapter_id,
            scene_id=self.scene_id,
            content_hash=self.content_hash,
            hash_algorithm=self.hash_algorithm,
            hash_basis=self.hash_basis,
        )
        if self.snapshot_id != expected_snapshot_id:
            raise SourceIdentityValidationError(
                "snapshot_id does not match the deterministic source identity"
            )

    @property
    def source_id(self) -> str:
        return self.source_document_id

    def to_dict(self) -> dict[str, Any]:
        return {
            "contract_version": self.contract_version,
            "project_id": self.project_id,
            "source_document_type": self.source_document_type,
            "source_document_id": self.source_document_id,
            "source_document_version": self.source_document_version,
            "source_ownership": self.source_ownership.value,
            "section_id": self.section_id,
            "chapter_id": self.chapter_id,
            "scene_id": self.scene_id,
            "snapshot_id": self.snapshot_id,
            "content_hash": self.content_hash,
            "hash_algorithm": self.hash_algorithm,
            "hash_basis": self.hash_basis,
            "text_encoding": self.text_encoding,
            "normalization_policy": self.normalization_policy,
            "source_map_id": self.source_map_id,
        }

    def to_json(self) -> str:
        return _canonical_json(self.to_dict())


@dataclass(frozen=True)
class ExactSourceSnapshot:
    """Exact UTF-8 owner-input value used to prove hashes and offset translation."""

    identity: SourceIdentity
    source_content: str
    char_offset_basis: str = CHAR_OFFSET_BASIS
    byte_offset_basis: str = BYTE_OFFSET_BASIS
    line_offset_basis: str | None = None
    token_offset_basis: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.identity, SourceIdentity):
            raise SourceIdentityValidationError("identity must be a SourceIdentity")
        if not isinstance(self.source_content, str):
            raise SourceIdentityValidationError("source_content must be a string")
        actual_hash = hashlib.sha256(self.source_content.encode("utf-8")).hexdigest()
        if actual_hash != self.identity.content_hash:
            raise SourceIdentityValidationError("source content hash mismatch")
        if self.char_offset_basis != CHAR_OFFSET_BASIS:
            raise SourceIdentityValidationError("unsupported char_offset_basis")
        if self.byte_offset_basis != BYTE_OFFSET_BASIS:
            raise SourceIdentityValidationError("unsupported byte_offset_basis")
        for field_name in ("line_offset_basis", "token_offset_basis"):
            value = getattr(self, field_name)
            if value is not None and (not isinstance(value, str) or not value):
                raise SourceIdentityValidationError(f"{field_name} must be explicit or None")

    @property
    def utf8_byte_length(self) -> int:
        return len(self.source_content.encode("utf-8"))

    def to_dict(self, *, include_content: bool = False) -> dict[str, Any]:
        value = {
            "identity": self.identity.to_dict(),
            "offsets": {
                "character": {
                    "available": True,
                    "basis": self.char_offset_basis,
                },
                "byte": {
                    "available": True,
                    "basis": self.byte_offset_basis,
                },
                "line": {
                    "available": self.line_offset_basis is not None,
                    "basis": self.line_offset_basis,
                },
                "token": {
                    "available": self.token_offset_basis is not None,
                    "basis": self.token_offset_basis,
                },
            },
            "character_length": len(self.source_content),
            "utf8_byte_length": self.utf8_byte_length,
        }
        if include_content:
            value["source_content"] = self.source_content
        return value


@dataclass(frozen=True)
class OffsetRange:
    start: int
    end: int
    basis: str

    def __post_init__(self) -> None:
        if type(self.start) is not int or self.start < 0:
            raise SourceIdentityValidationError("offset start must be non-negative")
        if type(self.end) is not int or self.end < self.start:
            raise SourceIdentityValidationError("offset end must not precede start")
        if self.basis not in (CHAR_OFFSET_BASIS, BYTE_OFFSET_BASIS):
            raise SourceIdentityValidationError("offset basis is not exactly translatable")

    def to_dict(self) -> dict[str, Any]:
        return {"start": self.start, "end": self.end, "basis": self.basis}


def build_exact_source_snapshot(
    *,
    project_id: str,
    source_document_type: str,
    source_document_id: str,
    source_document_version: str,
    source_ownership: SourceOwnership | str,
    source_content: str,
    source_map_id: str | None = None,
    section_id: str | None = None,
    chapter_id: str | None = None,
    scene_id: str | None = None,
    line_offset_basis: str | None = None,
    token_offset_basis: str | None = None,
) -> ExactSourceSnapshot:
    if not isinstance(source_content, str):
        raise SourceIdentityValidationError("source_content must be a string")
    content_hash = hashlib.sha256(source_content.encode("utf-8")).hexdigest()
    snapshot_id = derive_source_snapshot_id(
        contract_version=SOURCE_IDENTITY_CONTRACT_VERSION,
        project_id=project_id,
        source_document_type=source_document_type,
        source_document_id=source_document_id,
        source_document_version=source_document_version,
        source_ownership=source_ownership,
        section_id=section_id,
        chapter_id=chapter_id,
        scene_id=scene_id,
        content_hash=content_hash,
        hash_algorithm=SOURCE_HASH_ALGORITHM,
        hash_basis=SOURCE_HASH_BASIS,
    )
    identity = SourceIdentity(
        project_id=project_id,
        source_document_type=source_document_type,
        source_document_id=source_document_id,
        source_document_version=source_document_version,
        source_ownership=source_ownership,
        snapshot_id=snapshot_id,
        content_hash=content_hash,
        source_map_id=source_map_id,
        section_id=section_id,
        chapter_id=chapter_id,
        scene_id=scene_id,
    )
    return ExactSourceSnapshot(
        identity=identity,
        source_content=source_content,
        line_offset_basis=line_offset_basis,
        token_offset_basis=token_offset_basis,
    )


def translate_exact_offset_range(
    snapshot: ExactSourceSnapshot,
    offset_range: OffsetRange,
    *,
    target_basis: str,
    expected_snapshot_id: str | None = None,
    expected_content_hash: str | None = None,
) -> OffsetRange:
    """Translate only exact character/UTF-8 byte boundaries for one snapshot."""

    if not isinstance(snapshot, ExactSourceSnapshot):
        raise SourceIdentityValidationError("exact source snapshot is required")
    if not isinstance(offset_range, OffsetRange):
        raise SourceIdentityValidationError("offset_range must be an OffsetRange")
    if expected_snapshot_id is not None and expected_snapshot_id != snapshot.identity.snapshot_id:
        raise SourceIdentityValidationError("snapshot identity mismatch")
    if expected_content_hash is not None and expected_content_hash != snapshot.identity.content_hash:
        raise SourceIdentityValidationError("snapshot content hash mismatch")
    if target_basis not in (CHAR_OFFSET_BASIS, BYTE_OFFSET_BASIS):
        raise SourceIdentityValidationError("target offset basis is not exactly translatable")

    text = snapshot.source_content
    encoded = text.encode("utf-8")
    if offset_range.basis == CHAR_OFFSET_BASIS:
        if offset_range.end > len(text):
            raise SourceIdentityValidationError("character range exceeds exact source")
        byte_start = len(text[: offset_range.start].encode("utf-8"))
        byte_end = len(text[: offset_range.end].encode("utf-8"))
        if target_basis == CHAR_OFFSET_BASIS:
            return offset_range
        return OffsetRange(byte_start, byte_end, BYTE_OFFSET_BASIS)

    if offset_range.end > len(encoded):
        raise SourceIdentityValidationError("byte range exceeds exact source")
    try:
        char_start = len(encoded[: offset_range.start].decode("utf-8"))
        char_end = len(encoded[: offset_range.end].decode("utf-8"))
    except UnicodeDecodeError as exc:
        raise SourceIdentityValidationError(
            "byte range splits a UTF-8 code point"
        ) from exc
    if target_basis == BYTE_OFFSET_BASIS:
        return offset_range
    return OffsetRange(char_start, char_end, CHAR_OFFSET_BASIS)


def build_canonical_source_locator(
    identity: SourceIdentity,
    *,
    character_range: OffsetRange | None = None,
    byte_range: OffsetRange | None = None,
    exact_snapshot: ExactSourceSnapshot | None = None,
    locator_precision: str = "exact",
) -> dict[str, Any]:
    if not isinstance(identity, SourceIdentity):
        raise SourceIdentityValidationError("identity must be a SourceIdentity")
    if character_range is not None and character_range.basis != CHAR_OFFSET_BASIS:
        raise SourceIdentityValidationError("character_range has the wrong basis")
    if byte_range is not None and byte_range.basis != BYTE_OFFSET_BASIS:
        raise SourceIdentityValidationError("byte_range has the wrong basis")
    if character_range is not None and byte_range is not None:
        if exact_snapshot is None:
            raise SourceIdentityValidationError(
                "exact snapshot is required to relate character and byte ranges"
            )
        if exact_snapshot.identity != identity:
            raise SourceIdentityValidationError("locator snapshot identity mismatch")
        translated = translate_exact_offset_range(
            exact_snapshot,
            character_range,
            target_basis=BYTE_OFFSET_BASIS,
            expected_snapshot_id=identity.snapshot_id,
            expected_content_hash=identity.content_hash,
        )
        if translated != byte_range:
            raise SourceIdentityValidationError(
                "character and byte ranges do not identify the same exact span"
            )
    locator = {
        "project_id": identity.project_id,
        "source_document_type": identity.source_document_type,
        "source_document_id": identity.source_document_id,
        "source_document_version": identity.source_document_version,
        "source_map_id": identity.source_map_id,
        "snapshot_id": identity.snapshot_id,
        "snapshot_hash": identity.content_hash,
        "section_id": identity.section_id,
        "chapter_id": identity.chapter_id,
        "scene_id": identity.scene_id,
        "char_start": character_range.start if character_range else None,
        "char_end": character_range.end if character_range else None,
        "byte_start": byte_range.start if byte_range else None,
        "byte_end": byte_range.end if byte_range else None,
        "locator_precision": locator_precision,
        "source_hash": identity.content_hash,
        "char_offset_basis": CHAR_OFFSET_BASIS if character_range else None,
        "byte_offset_basis": BYTE_OFFSET_BASIS if byte_range else None,
        "line_offset_basis": None,
        "token_offset_basis": None,
    }
    return validate_canonical_source_locator(locator)


def validate_canonical_source_locator(locator: dict[str, Any]) -> dict[str, Any]:
    """Validate the shared locator, including exact byte-only Story Check spans."""

    validated = validate_source_locator(locator, allow_exact_byte_only=True)
    for prefix in ("char", "byte", "line", "token"):
        if validated.get(f"{prefix}_start") is not None and not validated.get(
            f"{prefix}_offset_basis"
        ):
            raise ValueError(f"{prefix}_offset_basis is required for canonical offsets")
    if validated["locator_precision"] not in ("document_only", "unknown"):
        for field in ("snapshot_id", "snapshot_hash", "source_hash"):
            if not validated.get(field):
                raise ValueError(f"{field} is required for canonical exact locators")
        for field in ("snapshot_hash", "source_hash"):
            if not _SHA256_PATTERN.fullmatch(validated[field]):
                raise ValueError(
                    f"{field} must be a lowercase SHA-256 hex digest for canonical exact locators"
                )
        if validated["snapshot_hash"] != validated["source_hash"]:
            raise ValueError(
                "snapshot_hash and source_hash must match for canonical exact locators"
            )
    return validated


def project_candidate_source_locator(locator: dict[str, Any]) -> dict[str, Any]:
    """Project a canonical locator into the existing narrow candidate shape."""

    validated = validate_source_locator(locator)
    return {
        "project_id": validated["project_id"],
        "source_document_type": validated["source_document_type"],
        "source_document_id": validated["source_document_id"],
        "section_id": validated.get("section_id"),
        "chapter_id": validated.get("chapter_id"),
        "scene_id": validated.get("scene_id"),
        "line_start": validated.get("line_start"),
        "line_end": validated.get("line_end"),
        "char_start": validated.get("char_start"),
        "char_end": validated.get("char_end"),
        "source_hash": validated.get("source_hash"),
    }


__all__ = (
    "SOURCE_IDENTITY_CONTRACT_VERSION",
    "SOURCE_HASH_ALGORITHM",
    "SOURCE_HASH_BASIS",
    "CHAR_OFFSET_BASIS",
    "BYTE_OFFSET_BASIS",
    "SourceOwnership",
    "SourceIdentityValidationError",
    "SourceIdentity",
    "ExactSourceSnapshot",
    "OffsetRange",
    "build_exact_source_snapshot",
    "translate_exact_offset_range",
    "build_canonical_source_locator",
    "validate_canonical_source_locator",
    "project_candidate_source_locator",
    "validate_source_document_ref",
    "validate_source_segment",
    "validate_source_map",
    "validate_source_locator",
)
