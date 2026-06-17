"""Pure validation helpers for Writer Assistant Core candidate records."""

from copy import copy

from backend.story_knowledge import candidate_schema

_STORED_STATUS_VALUES = frozenset(
    {
        "candidate",
        "owner_review",
        "approved",
        "rejected",
        "needs_revision",
        "archived",
    }
)

_STORED_OWNER_DECISION_VALUES = frozenset(
    {
        "undecided",
        "approve",
        "reject",
        "needs_revision",
        "archive",
    }
)

_SOURCE_DOCUMENT_TYPES = frozenset(
    {
        "scene",
        "note",
        "material",
        "bible",
        "storyform",
        "omi",
    }
)

_SOURCE_LOCATOR_ALLOWED_FIELDS = frozenset(
    {
        "project_id",
        "source_document_type",
        "source_document_id",
        "section_id",
        "chapter_id",
        "scene_id",
        "start_offset",
        "end_offset",
        "line_start",
        "line_end",
        "char_start",
        "char_end",
        "source_hash",
    }
)

_EVIDENCE_ALLOWED_FIELDS = frozenset(
    {
        "evidence_id",
        "source_locator",
        "source_text_excerpt",
        "summary",
        "supports_claim",
        "confidence",
        "notes",
        "line_start",
        "line_end",
        "char_start",
        "char_end",
    }
)

_PROVENANCE_ALLOWED_FIELDS = frozenset(
    {
        "origin",
        "extraction_method",
        "timestamp",
        "human_review_required",
        "updated_at",
        "source_snapshot_hash",
        "created_by",
        "source_type",
        "license_status",
        "adapter_name",
        "adapter_version",
        "reviewed_at",
        "reviewed_by",
        "source_hash",
        "snapshot_hash",
        "owner_reviewed",
    }
)

_PROVENANCE_ORIGINS = frozenset(
    {
        "manual",
        "extractor",
        "model_assisted",
        "imported",
    }
)

_RECORD_REQUIRED_FIELDS = frozenset(
    {
        "candidate_id",
        "project_id",
        "candidate_type",
        "status",
        "target_category",
        "source_locator",
        "evidence",
        "provenance",
        "owner_decision",
        "destination",
        "confidence",
        "created_at",
        "updated_at",
    }
)

_RECORD_OPTIONAL_FIELDS = frozenset(
    {
        "uncertainty",
        "links",
        "notes",
        "owner_review_notes",
        "schema_version",
        "source_snapshot_hash",
    }
)

_OFFSET_FIELDS = frozenset(
    {
        "start_offset",
        "end_offset",
        "line_start",
        "line_end",
        "char_start",
        "char_end",
    }
)


def _require_mapping(value, label):
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a mapping")
    return value


def _require_fields(payload, required_fields):
    for field in required_fields:
        if field not in payload:
            raise ValueError(f"missing required field: {field}")


def _validate_safe_id(value, label):
    if not isinstance(value, str):
        raise ValueError(f"{label} must be a string")
    if not value or not value.strip():
        raise ValueError(f"{label} must be a non-empty path-safe identifier")
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


def _validate_confidence(value, label="confidence"):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be numeric between 0.0 and 1.0")
    if value < 0.0 or value > 1.0:
        raise ValueError(f"{label} must be numeric between 0.0 and 1.0")
    return value


def _validate_non_negative_int_or_none(value, label):
    if value is None:
        return value
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{label} must be None or a non-negative integer")
    if value < 0:
        raise ValueError(f"{label} must be None or a non-negative integer")
    return value


def _field_name_is_disallowed(key):
    lower = key.lower()
    if lower == "path" or lower.endswith("_path"):
        return True
    if lower.endswith("_request") or lower.endswith("_prompt"):
        return True
    return False


def _reject_unknown_fields(payload, allowed_fields):
    for key in payload:
        if key not in allowed_fields or _field_name_is_disallowed(key):
            raise ValueError(f"unexpected field: {key}")


def _validate_offset_fields(payload, allowed_fields):
    for field in _OFFSET_FIELDS:
        if field in allowed_fields and field in payload:
            _validate_non_negative_int_or_none(payload[field], field)


def validate_source_locator(locator):
    payload = _require_mapping(locator, "source_locator")
    _require_fields(
        payload,
        ("project_id", "source_document_type", "source_document_id"),
    )
    _reject_unknown_fields(payload, _SOURCE_LOCATOR_ALLOWED_FIELDS)

    _validate_safe_id(payload["project_id"], "project_id")

    document_type = payload["source_document_type"]
    if document_type not in _SOURCE_DOCUMENT_TYPES:
        raise ValueError("source_document_type is not allowed")

    _validate_safe_id(payload["source_document_id"], "source_document_id")
    _validate_offset_fields(payload, _SOURCE_LOCATOR_ALLOWED_FIELDS)

    return copy(payload)


def validate_evidence_item(item):
    payload = _require_mapping(item, "evidence item")
    _require_fields(payload, ("source_locator", "confidence"))
    _reject_unknown_fields(payload, _EVIDENCE_ALLOWED_FIELDS)

    validate_source_locator(payload["source_locator"])
    _validate_confidence(payload["confidence"])
    _validate_offset_fields(payload, _EVIDENCE_ALLOWED_FIELDS)

    return copy(payload)


def validate_provenance(provenance):
    payload = _require_mapping(provenance, "provenance")
    _require_fields(
        payload,
        ("origin", "extraction_method", "timestamp", "human_review_required"),
    )
    _reject_unknown_fields(payload, _PROVENANCE_ALLOWED_FIELDS)

    origin = payload["origin"]
    if origin not in _PROVENANCE_ORIGINS:
        raise ValueError("origin is not allowed")

    if not isinstance(payload["human_review_required"], bool):
        raise ValueError("human_review_required must be boolean")

    return copy(payload)


def _validate_uncertainty(value):
    if value is None:
        return value
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        if not all(isinstance(entry, str) for entry in value):
            raise ValueError("uncertainty must be a string or list of strings")
        return value
    raise ValueError("uncertainty must be a string or list of strings")


def validate_candidate_record(record):
    payload = _require_mapping(record, "candidate record")
    _require_fields(payload, _RECORD_REQUIRED_FIELDS)

    allowed_fields = _RECORD_REQUIRED_FIELDS | _RECORD_OPTIONAL_FIELDS
    _reject_unknown_fields(payload, allowed_fields)

    _validate_safe_id(payload["candidate_id"], "candidate_id")
    _validate_safe_id(payload["project_id"], "project_id")

    candidate_type = payload["candidate_type"]
    if candidate_type not in candidate_schema.CORE_CANDIDATE_TYPES:
        raise ValueError("candidate_type is not allowed")

    expected_category = candidate_schema.CORE_CANDIDATE_TARGET_CATEGORIES.get(
        candidate_type
    )
    if payload["target_category"] != expected_category:
        raise ValueError("target_category does not match candidate_type")

    validate_source_locator(payload["source_locator"])

    evidence = payload["evidence"]
    if not isinstance(evidence, list):
        raise ValueError("evidence must be a list")
    for item in evidence:
        validate_evidence_item(item)

    validate_provenance(payload["provenance"])
    _validate_confidence(payload["confidence"])

    if "uncertainty" in payload:
        _validate_uncertainty(payload["uncertainty"])

    status = payload["status"]
    if status not in _STORED_STATUS_VALUES:
        raise ValueError("status is not allowed")

    owner_decision = payload["owner_decision"]
    if owner_decision not in _STORED_OWNER_DECISION_VALUES:
        raise ValueError("owner_decision is not allowed")

    destination = payload["destination"]
    if destination not in candidate_schema.CORE_DESTINATION_VALUES:
        raise ValueError("destination is not allowed")

    return copy(payload)


__all__ = (
    "validate_candidate_record",
    "validate_source_locator",
    "validate_evidence_item",
    "validate_provenance",
)
