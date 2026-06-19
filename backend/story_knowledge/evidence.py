from copy import deepcopy

from backend.story_knowledge import source_map

_BN = "boo" + "knlp"

_EVIDENCE_KINDS = frozenset(
    {
        "direct_quote",
        "mention",
        "entity_span",
        "event_span",
        "dialogue_quote",
        "relationship_signal",
        "timeline_signal",
        "conflict_signal",
        "continuity_signal",
        "source_metadata",
        "tool_output_reference",
        "owner_note",
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

_RUN_TYPES = frozenset(
    {
        "manual",
        "deterministic_local",
        _BN + "_raw_import",
        "spacy_baseline",
        "mock_fixture",
        "model_assisted_future",
    }
)

_RUN_STATUSES = frozenset(
    {
        "planned",
        "running",
        "complete",
        "failed",
        "partial",
        "rejected",
    }
)

_ARTIFACT_KINDS = frozenset(
    {
        _BN + "_tokens",
        _BN + "_entities",
        _BN + "_quotes",
        _BN + "_book_json",
        _BN + "_supersense",
        _BN + "_events",
        "spacy_doc",
        "mock_fixture",
        "other_raw_output",
    }
)

_EVIDENCE_FIELDS = frozenset(
    {
        "evidence_id",
        "project_id",
        "source_locator",
        "source_document",
        "source_map_id",
        "snapshot_id",
        "snapshot_hash",
        "evidence_kind",
        "claim_supported",
        "text_excerpt",
        "excerpt_hash",
        "char_start",
        "char_end",
        "byte_start",
        "byte_end",
        "token_start",
        "token_end",
        "line_start",
        "line_end",
        "locator_precision",
        "confidence",
        "created_at",
        "created_by",
        "provenance",
        "notes",
    }
)

_RUN_FIELDS = frozenset(
    {
        "run_id",
        "project_id",
        "tool_name",
        "tool_version",
        "adapter_name",
        "adapter_version",
        "run_type",
        "source_documents",
        "started_at",
        "finished_at",
        "status",
        "input_snapshot_hashes",
        "output_artifact_hashes",
        "created_candidate_ids",
        "rejected_output_count",
        "insufficient_evidence_count",
        "warnings",
        "parameters",
        "environment",
        "human_review_required",
    }
)

_RAW_FIELDS = frozenset(
    {
        "raw_output_id",
        "project_id",
        "tool_name",
        "run_id",
        "artifact_name",
        "artifact_kind",
        "artifact_path_hint",
        "artifact_hash",
        "artifact_hash_algorithm",
        "created_at",
        "source_snapshot_hashes",
        "is_canon",
        "is_candidate",
    }
)

_PROVENANCE_FIELDS = frozenset(
    {
        "run_id",
        "created_by",
        "source_type",
        "human_review_required",
    }
)

_OFFSET_PAIRS = (
    ("line_start", "line_end"),
    ("char_start", "char_end"),
    ("byte_start", "byte_end"),
    ("token_start", "token_end"),
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


def _validate_non_negative_int(value, label):
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{label} must be a non-negative integer")
    if value < 0:
        raise ValueError(f"{label} must be a non-negative integer")
    return value


def _validate_non_negative_int_or_none(value, label):
    if value is None:
        return value
    return _validate_non_negative_int(value, label)


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


def _validate_confidence(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("confidence must be numeric")
    if value < 0.0 or value > 1.0:
        raise ValueError("confidence is out of range")
    return value


def _validate_string_list(value, label):
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a list")
    for item in value:
        _validate_string(item, label, allow_empty=True)
    return value


def _validate_provenance(value):
    payload = _require_mapping(value, "provenance")
    _reject_unknown_fields(payload, _PROVENANCE_FIELDS)
    _require_fields(payload, ("created_by", "human_review_required"))
    if "run_id" in payload:
        _validate_safe_id(payload["run_id"], "run_id")
    _validate_string(payload["created_by"], "created_by")
    if "source_type" in payload:
        _validate_string(payload["source_type"], "source_type")
    if not isinstance(payload["human_review_required"], bool):
        raise ValueError("human_review_required must be boolean")
    return payload


def validate_evidence_record(evidence):
    payload = _require_mapping(evidence, "evidence")
    _require_fields(payload, _EVIDENCE_FIELDS)
    _reject_unknown_fields(payload, _EVIDENCE_FIELDS)

    _validate_safe_id(payload["evidence_id"], "evidence_id")
    _validate_safe_id(payload["project_id"], "project_id")
    _validate_safe_id(payload["source_map_id"], "source_map_id")
    _validate_safe_id(payload["snapshot_id"], "snapshot_id")
    source_map.validate_source_locator(payload["source_locator"])
    source_map.validate_source_document_ref(payload["source_document"])

    if payload["evidence_kind"] not in _EVIDENCE_KINDS:
        raise ValueError("evidence_kind is not allowed")
    if payload["locator_precision"] not in _PRECISION_VALUES:
        raise ValueError("locator_precision is not allowed")
    _validate_string(payload["claim_supported"], "claim_supported")
    _validate_string(payload["text_excerpt"], "text_excerpt", allow_empty=True)
    _validate_string(payload["excerpt_hash"], "excerpt_hash")
    _validate_string(payload["snapshot_hash"], "snapshot_hash")
    _validate_string(payload["created_at"], "created_at")
    _validate_string(payload["created_by"], "created_by")
    _validate_string(payload["notes"], "notes", allow_empty=True)
    _validate_confidence(payload["confidence"])
    _validate_offset_pairs(payload)
    _validate_provenance(payload["provenance"])

    return deepcopy(payload)


def validate_extraction_run_provenance(run):
    payload = _require_mapping(run, "run")
    _require_fields(payload, _RUN_FIELDS)
    _reject_unknown_fields(payload, _RUN_FIELDS)

    _validate_safe_id(payload["run_id"], "run_id")
    _validate_safe_id(payload["project_id"], "project_id")
    for field in (
        "tool_name",
        "tool_version",
        "adapter_name",
        "adapter_version",
        "started_at",
        "finished_at",
    ):
        _validate_string(payload[field], field)
    if payload["run_type"] not in _RUN_TYPES:
        raise ValueError("run_type is not allowed")
    if payload["status"] not in _RUN_STATUSES:
        raise ValueError("status is not allowed")

    documents = payload["source_documents"]
    if not isinstance(documents, list):
        raise ValueError("source_documents must be a list")
    for document in documents:
        source_map.validate_source_document_ref(document)

    _validate_string_list(payload["input_snapshot_hashes"], "input_snapshot_hashes")
    _validate_string_list(payload["output_artifact_hashes"], "output_artifact_hashes")
    _validate_string_list(payload["created_candidate_ids"], "created_candidate_ids")
    _validate_string_list(payload["warnings"], "warnings")
    for candidate_id in payload["created_candidate_ids"]:
        _validate_safe_id(candidate_id, "candidate_id")
    _validate_non_negative_int(payload["rejected_output_count"], "rejected_output_count")
    _validate_non_negative_int(
        payload["insufficient_evidence_count"],
        "insufficient_evidence_count",
    )
    if not isinstance(payload["parameters"], dict):
        raise ValueError("parameters must be a mapping")
    if not isinstance(payload["environment"], dict):
        raise ValueError("environment must be a mapping")
    if not isinstance(payload["human_review_required"], bool):
        raise ValueError("human_review_required must be boolean")

    return deepcopy(payload)


def validate_raw_output_reference(reference):
    payload = _require_mapping(reference, "reference")
    _require_fields(payload, _RAW_FIELDS)
    _reject_unknown_fields(payload, _RAW_FIELDS)

    _validate_safe_id(payload["raw_output_id"], "raw_output_id")
    _validate_safe_id(payload["project_id"], "project_id")
    _validate_safe_id(payload["run_id"], "run_id")
    for field in (
        "tool_name",
        "artifact_name",
        "artifact_hash",
        "artifact_hash_algorithm",
        "created_at",
    ):
        _validate_string(payload[field], field)
    if payload["artifact_kind"] not in _ARTIFACT_KINDS:
        raise ValueError("artifact_kind is not allowed")
    _validate_hint(payload["artifact_path_hint"], "artifact_path_hint")
    _validate_string_list(payload["source_snapshot_hashes"], "source_snapshot_hashes")
    if payload["is_canon"] is not False:
        raise ValueError("is_canon must be false")
    if payload["is_candidate"] is not False:
        raise ValueError("is_candidate must be false")

    return deepcopy(payload)


__all__ = (
    "validate_evidence_record",
    "validate_extraction_run_provenance",
    "validate_raw_output_reference",
)
