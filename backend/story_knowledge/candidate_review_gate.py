import copy
import hashlib
from datetime import datetime, timezone

from backend.story_knowledge import candidate_schema
from backend.story_knowledge.candidate_record import (
    validate_candidate_record,
    validate_source_locator,
    validate_evidence_item,
    validate_provenance,
)
from backend.story_knowledge.candidate_persistence import write_candidate_record


_DRAFT_REQUIRED_FIELDS = frozenset(
    {
        "candidate_type",
        "target_category",
        "source_document",
        "source_locator",
        "evidence",
        "provenance",
        "confidence",
        "raw_output_refs",
        "normalization_status",
        "human_review_required",
    }
)

_ACCEPTED_NORMALIZATION_STATUS = "normalized"
_RECORD_STATUS = "candidate"
_RECORD_OWNER_DECISION = "undecided"
_RECORD_DESTINATION = "omi_candidate_only"
_QUEUE_REVIEW_STATUS = "pending"
_QUEUE_LIFECYCLE_STATE = "draft_ready_for_review"

_PROVENANCE_REF_FIELDS = (
    "origin",
    "extraction_method",
    "adapter_name",
    "adapter_version",
)


def _now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _require_mapping(value):
    if not isinstance(value, dict):
        raise ValueError("invalid input")
    return value


def _require_path_safe(value):
    if not isinstance(value, str):
        raise ValueError("invalid field")
    if not value.strip():
        raise ValueError("invalid field")
    if value in (".", ".."):
        raise ValueError("invalid field")
    if "/" in value or "\\" in value:
        raise ValueError("invalid field")
    if ".." in value:
        raise ValueError("invalid field")
    if value.startswith("/"):
        raise ValueError("invalid field")
    if len(value) >= 2 and value[1] == ":" and value[0].isalpha():
        raise ValueError("invalid field")
    return value


def _require_confidence(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("invalid field")
    if value < 0.0 or value > 1.0:
        raise ValueError("invalid field")
    return value


def _as_string_list(value):
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str)]
    return []


def _coerce_review_flag(provenance):
    if provenance.get("human_review_required") is False:
        return False
    return True


def _build_candidate_id(project_id, candidate_type, source_locator, evidence, provenance, confidence):
    source_document_id = str(source_locator.get("source_document_id", ""))
    safe_source = _require_path_safe(source_document_id)
    basis = "|".join(
        [
            project_id,
            candidate_type,
            source_document_id,
            repr(confidence),
            str(provenance.get("origin", "")),
            str(provenance.get("extraction_method", "")),
            str(provenance.get("timestamp", "")),
            str(len(evidence)),
        ]
    )
    digest = hashlib.sha256(basis.encode("utf-8")).hexdigest()[:12]
    return "core_candidate_{0}_{1}".format(safe_source, digest)


def _build_queue_entry_id(project_id, candidate_id):
    basis = "|".join([project_id, candidate_id])
    digest = hashlib.sha256(basis.encode("utf-8")).hexdigest()[:16]
    return "review_queue_entry_{0}".format(digest)


def validate_candidate_draft_for_persistence(draft):
    payload = _require_mapping(draft)
    working = copy.deepcopy(payload)

    for field in _DRAFT_REQUIRED_FIELDS:
        if field not in working:
            raise ValueError("invalid field")
    for key in working:
        if key not in _DRAFT_REQUIRED_FIELDS:
            raise ValueError("invalid field")

    candidate_type = working["candidate_type"]
    if candidate_type not in candidate_schema.CORE_CANDIDATE_TYPES:
        raise ValueError("invalid field")

    expected_category = candidate_schema.CORE_CANDIDATE_TARGET_CATEGORIES.get(
        candidate_type
    )
    if working["target_category"] != expected_category:
        raise ValueError("invalid field")

    source_document = working["source_document"]
    if not isinstance(source_document, dict) or not source_document:
        raise ValueError("invalid support data")

    validate_source_locator(working["source_locator"])

    evidence = working["evidence"]
    if not isinstance(evidence, list):
        raise ValueError("invalid support data")
    for item in evidence:
        validate_evidence_item(item)

    validate_provenance(working["provenance"])

    _require_confidence(working["confidence"])

    if not isinstance(working["raw_output_refs"], list):
        raise ValueError("invalid field")

    if working["normalization_status"] != _ACCEPTED_NORMALIZATION_STATUS:
        raise ValueError("invalid field")

    if working["human_review_required"] is not True:
        raise ValueError("invalid field")

    return working


def build_candidate_record_from_draft(draft, *, project_id):
    validated_draft = validate_candidate_draft_for_persistence(draft)
    _require_path_safe(project_id)

    candidate_type = validated_draft["candidate_type"]
    target_category = validated_draft["target_category"]
    source_locator = copy.deepcopy(validated_draft["source_locator"])
    evidence = copy.deepcopy(validated_draft["evidence"])
    provenance = copy.deepcopy(validated_draft["provenance"])
    confidence = validated_draft["confidence"]

    candidate_id = _build_candidate_id(
        project_id,
        candidate_type,
        source_locator,
        evidence,
        provenance,
        confidence,
    )
    timestamp = _now_iso()

    record = {
        "candidate_id": candidate_id,
        "project_id": project_id,
        "candidate_type": candidate_type,
        "status": _RECORD_STATUS,
        "target_category": target_category,
        "source_locator": source_locator,
        "evidence": evidence,
        "provenance": provenance,
        "owner_decision": _RECORD_OWNER_DECISION,
        "destination": _RECORD_DESTINATION,
        "confidence": confidence,
        "created_at": timestamp,
        "updated_at": timestamp,
    }

    return validate_candidate_record(record)


def build_review_queue_entry(candidate_record, *, project_id):
    validated = validate_candidate_record(candidate_record)
    _require_path_safe(project_id)

    source_locator = copy.deepcopy(validated["source_locator"])
    evidence = validated.get("evidence") or []
    provenance = validated.get("provenance") or {}

    evidence_refs = []
    for item in evidence:
        if isinstance(item, dict):
            evidence_id = item.get("evidence_id")
            if isinstance(evidence_id, str) and evidence_id.strip():
                evidence_refs.append(evidence_id)

    provenance_refs = []
    for key in _PROVENANCE_REF_FIELDS:
        value = provenance.get(key)
        if isinstance(value, str) and value.strip():
            provenance_refs.append(value)

    candidate_id = validated["candidate_id"]
    timestamp = _now_iso()

    return {
        "queue_entry_id": _build_queue_entry_id(project_id, candidate_id),
        "project_id": project_id,
        "candidate_record_id": candidate_id,
        "candidate_type": validated["candidate_type"],
        "target_category": validated["target_category"],
        "review_status": _QUEUE_REVIEW_STATUS,
        "lifecycle_state": _QUEUE_LIFECYCLE_STATE,
        "source_document": source_locator.get("source_document_id", ""),
        "source_locator": source_locator,
        "evidence_summary": "{0} evidence item(s)".format(len(evidence)),
        "evidence_refs": evidence_refs,
        "provenance_summary": "; ".join(provenance_refs),
        "provenance_refs": provenance_refs,
        "confidence": validated["confidence"],
        "uncertainty_flags": _as_string_list(validated.get("uncertainty")),
        "normalization_status": _ACCEPTED_NORMALIZATION_STATUS,
        "raw_output_refs": [],
        "human_review_required": _coerce_review_flag(provenance),
        "created_at": validated.get("created_at") or timestamp,
        "updated_at": validated.get("updated_at") or timestamp,
    }


def persist_candidate_record_for_review(candidate_record, *, project_dir):
    validated = validate_candidate_record(candidate_record)
    written = write_candidate_record(project_dir, validated)
    return {
        "persisted": True,
        "candidate_only": True,
        "review_pending": True,
        "candidate_id": written["candidate_id"],
        "project_id": written["project_id"],
    }


__all__ = (
    "validate_candidate_draft_for_persistence",
    "build_candidate_record_from_draft",
    "build_review_queue_entry",
    "persist_candidate_record_for_review",
)
