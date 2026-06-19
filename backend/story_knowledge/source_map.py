from copy import deepcopy

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


def validate_source_locator(locator):
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
        if payload.get("char_start") is None or payload.get("char_end") is None:
            raise ValueError("character offsets are required")

    for field in ("source_document_version", "snapshot_hash", "source_label", "source_hash"):
        if field in payload and payload[field] is not None:
            _validate_string(payload[field], field, allow_empty=True)

    return deepcopy(payload)


__all__ = (
    "validate_source_document_ref",
    "validate_source_segment",
    "validate_source_map",
    "validate_source_locator",
)
