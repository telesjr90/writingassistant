"""Pure app-owned dramatica-flow-informed analysis-rubric contract.

PHASE8-IMPL-023-T020C defines shapes and validation only.  This module does
not import, read, or execute dramatica-flow; call models, servers, networks,
or subprocesses; access project state; persist candidates; mutate Memory or
Canon; promote findings; or generate, revise, or continue prose.
"""

from __future__ import annotations

import copy
import re
from typing import Any


DRAMATICA_FLOW_INFORMED_RUBRIC_REQUEST_SCHEMA_VERSION = (
    "omi_app_owned_dramatica_flow_informed_rubric_request.v1"
)
DRAMATICA_FLOW_INFORMED_RUBRIC_RESULT_SCHEMA_VERSION = (
    "omi_app_owned_dramatica_flow_informed_rubric_result.v1"
)
DRAMATICA_FLOW_INFORMED_RUBRIC_ID = (
    "app_owned_dramatica_flow_informed_rubric"
)
DRAMATICA_FLOW_INFORMED_RUBRIC_OUTPUT_CLASS = "rubric_mapping_support"
DRAMATICA_FLOW_INFORMED_RUBRIC_SUPPORT_LABEL = (
    "App-owned dramatica-flow-informed diagnostic support"
)

ALLOWED_CATEGORIES = frozenset(
    {
        "causal_chain_diagnostic",
        "narrative_commitment_lifecycle_diagnostic",
        "emotional_state_consistency",
        "relationship_delta_diagnostic",
        "timeline_thread_activity_diagnostic",
        "information_boundary_diagnostic",
        "multidimensional_diagnostic_question",
        "ambiguity",
        "insufficient_evidence",
        "owner_review_question",
    }
)
QUESTION_CATEGORIES = frozenset(
    {"multidimensional_diagnostic_question", "owner_review_question"}
)
NON_QUESTION_CATEGORIES = ALLOWED_CATEGORIES - QUESTION_CATEGORIES

CATEGORY_TO_CANDIDATE_TYPE = {
    "causal_chain_diagnostic": "plot_thread",
    "narrative_commitment_lifecycle_diagnostic": "plot_thread",
    "emotional_state_consistency": "continuity_warning",
    "relationship_delta_diagnostic": "relationship",
    "timeline_thread_activity_diagnostic": "timeline_event",
    "information_boundary_diagnostic": "continuity_warning",
    "multidimensional_diagnostic_question": "diagnostic_question",
    "ambiguity": "ambiguity",
    "insufficient_evidence": "evidence_note",
    "owner_review_question": "diagnostic_question",
}
CATEGORY_TO_STATEMENT_KIND = {
    category: (
        "question"
        if category in QUESTION_CATEGORIES
        else "ambiguity"
        if category == "ambiguity"
        else "insufficient_evidence"
        if category == "insufficient_evidence"
        else "candidate_observation"
    )
    for category in ALLOWED_CATEGORIES
}

ALLOWED_CANDIDATE_TYPES = frozenset(CATEGORY_TO_CANDIDATE_TYPE.values())
ALLOWED_STATUSES = frozenset({"succeeded", "empty", "failed_closed", "error"})
ALLOWED_CONFIDENCE_VALUES = frozenset({"low_support", "medium_support"})
ALLOWED_UNCERTAINTY_VALUES = frozenset(
    {
        "null",
        "ambiguity",
        "insufficient_evidence",
        "conflicting_support",
        "requires_owner_interpretation",
    }
)
ALLOWED_STATEMENT_KINDS = frozenset(
    {"candidate_observation", "question", "ambiguity", "insufficient_evidence"}
)

ALLOWED_REQUEST_SAFETY_CONFIRMATIONS = frozenset(
    {
        "no_dramatica_flow_execution",
        "no_official_dramatica_flow_output_claim",
        "no_external_source_runtime_read",
        "no_model_provider_server_call",
        "no_external_project_truth_state_use_or_mutation",
        "no_automatic_storyform_truth",
        "no_prose_generation",
        "no_prose_rewrite",
        "no_prose_continuation",
        "no_outline",
        "no_candidate_persistence",
        "no_review_queue_creation",
        "no_memory_canon_mutation",
        "no_promotion_record",
        "no_apply_promotion",
        "no_training_artifacts",
    }
)

REQUEST_REQUIRED_FIELDS = frozenset(
    {
        "schema_version", "rubric_id", "request_id", "project_name",
        "source_text", "source_locator", "source_refs", "evidence_refs",
        "provenance_refs", "source_locator_refs", "requested_categories",
        "analysis_intent", "owner_authored_or_owner_provided_source",
        "safety_confirmations",
    }
)
RESULT_REQUIRED_FIELDS = frozenset(
    {
        "schema_version", "rubric_id", "output_class", "status",
        "display_label", "provenance", "source_refs", "evidence_refs",
        "provenance_refs", "source_locator_refs", "candidate_support",
        "diagnostic_questions", "uncertainty_notes",
        "insufficient_evidence_notes", "safety",
    }
)
RESULT_ALLOWED_FIELDS = RESULT_REQUIRED_FIELDS | {"fail_closed_reason"}
ITEM_REQUIRED_FIELDS = frozenset(
    {
        "item_id", "category", "candidate_type", "label", "diagnostic_text",
        "statement_kind", "evidence", "source_locator", "source_refs",
        "evidence_refs", "provenance_refs", "source_locator_refs",
        "provenance", "support_label", "confidence", "uncertainty_label",
        "owner_decision", "review_status", "executes_dramatica_flow",
        "official_dramatica_flow_output", "calls_model_provider_server",
        "reads_external_source_runtime", "uses_external_project_state",
    }
)
EVIDENCE_REQUIRED_FIELDS = frozenset({"source_excerpt", "source_locator"})
OPERATION_FLAGS = (
    "executes_dramatica_flow",
    "official_dramatica_flow_output",
    "calls_model_provider_server",
    "reads_external_source_runtime",
    "uses_external_project_state",
    "mutates_external_project_state",
    "persists_candidates",
    "creates_review_queue_entries",
    "mutates_memory_canon",
    "creates_promotion_records",
    "applies_promotion",
    "generates_prose",
    "rewrites_prose",
    "continues_prose",
    "creates_outline",
    "creates_training_artifacts",
)
ITEM_OPERATION_FLAGS = (
    "executes_dramatica_flow", "official_dramatica_flow_output",
    "calls_model_provider_server", "reads_external_source_runtime",
    "uses_external_project_state",
)

_SAFE_ID_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
_SAFE_LOCATOR_RE = re.compile(r"^source_locator_ref_[A-Za-z0-9_.-]+$")
_UNSAFE_RE = re.compile(
    r"\b(?:truth|canon(?:ical|ized)?|final(?:ity)?|approv(?:e|ed|al)|promot(?:e|ed|ion)|"
    r"storyform|\bos\b|\bmc\b|\bic\b|\brs\b|domain|concern|issue|problem|solution|"
    r"approach|dynamic|signpost|official(?:[ _-]+dramatica(?:[ _-]+flow)?)?|"
    r"live(?:[ _-]+dramatica(?:[ _-]+flow)?)?|execut(?:e|ed|ion)|confirm(?:ed|ation)?|"
    r"endors(?:e|ed|ement)|writer(?:[ _-]+agent)?|architect(?:[ _-]+agent)?|"
    r"auditor(?:[ _-]+agent)?|reviser(?:[ _-]+agent)?|generate(?:d)?(?:[ _-]+prose)?|"
    r"writing(?:[ _-]+instruction)?|rewrite|continu(?:e|ation)|outline|draft|polish|"
    r"improv(?:e|ement)|expand|revision|revise|imitat(?:e|ion)|export|model|provider|"
    r"api|network|server|external(?:[ _-]+(?:project|chapter|snapshot|thread|world|truth))?|chapter|snapshot|"
    r"world(?:[ _-]+state)?|truth(?:[ _-]+file)?|persist(?:ence|ed)?|review(?:[ _-]+queue)|"
    r"memory(?:[ _-]+canon)?|apply(?:[ _-]+promotion)|training(?:[ _-]+artifact)?|"
    r"model(?:[ _-]+artifact)?)\b",
    re.IGNORECASE,
)
_SAFE_LITERAL_VALUES = {
    DRAMATICA_FLOW_INFORMED_RUBRIC_ID,
    DRAMATICA_FLOW_INFORMED_RUBRIC_REQUEST_SCHEMA_VERSION,
    DRAMATICA_FLOW_INFORMED_RUBRIC_RESULT_SCHEMA_VERSION,
    DRAMATICA_FLOW_INFORMED_RUBRIC_SUPPORT_LABEL,
}


def _base_response(status: str, valid: bool, fail_closed: bool) -> dict[str, Any]:
    result = {"status": status, "valid": valid, "fail_closed": fail_closed, "errors": []}
    result.update({key: False for key in OPERATION_FLAGS})
    return result


def _failure(errors: list[str], normalized_key: str, normalized: Any) -> dict[str, Any]:
    result = _base_response("fail_closed", False, True)
    result["errors"] = list(errors)
    result[normalized_key] = copy.deepcopy(normalized)
    return result


def _success(normalized_key: str, normalized: dict[str, Any]) -> dict[str, Any]:
    result = _base_response("valid", True, False)
    result[normalized_key] = copy.deepcopy(normalized)
    return result


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value)


def _safe_id(value: Any) -> bool:
    return _non_empty_string(value) and bool(_SAFE_ID_RE.fullmatch(value))


def _valid_refs(value: Any, *, locator: bool = False) -> bool:
    pattern = _SAFE_LOCATOR_RE if locator else _SAFE_ID_RE
    return (
        isinstance(value, list) and bool(value)
        and len(value) == len(set(value))
        and all(isinstance(item, str) and bool(pattern.fullmatch(item)) for item in value)
    )


def _valid_provenance(value: Any) -> bool:
    return value == {
        "tool_source": DRAMATICA_FLOW_INFORMED_RUBRIC_ID,
        "adapter": DRAMATICA_FLOW_INFORMED_RUBRIC_ID,
        "support": DRAMATICA_FLOW_INFORMED_RUBRIC_SUPPORT_LABEL,
        "executes_dramatica_flow": False,
        "official_dramatica_flow_output": False,
    }


def _scan_unsafe(value: Any, path: str, errors: list[str]) -> None:
    """Reject unsafe claims recursively; evidence excerpts are owner quotations."""
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else str(key)
            if not isinstance(key, str):
                errors.append(f"{child_path} uses a non-string key")
                continue
            if key == "source_excerpt" and path.endswith(".evidence_item"):
                continue
            _scan_unsafe(child, child_path, errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            child_path = f"{path}[{index}]"
            evidence_path = f"{path}.evidence_item" if path.endswith(".evidence") else child_path
            _scan_unsafe(child, evidence_path, errors)
    elif isinstance(value, str) and value not in _SAFE_LITERAL_VALUES and _UNSAFE_RE.search(value):
        errors.append(f"{path} contains forbidden output language")


def validate_dramatica_flow_informed_rubric_request(request: object) -> dict[str, Any]:
    """Validate and deep-copy a diagnostic-only owner-source request."""
    if not isinstance(request, dict):
        return _failure(["request must be a dictionary"], "normalized_request", {})
    normalized = copy.deepcopy(request)
    errors: list[str] = []
    missing = sorted(REQUEST_REQUIRED_FIELDS - set(normalized))
    unexpected = sorted(set(normalized) - REQUEST_REQUIRED_FIELDS)
    if missing:
        errors.append(f"missing required request fields: {missing}")
    if unexpected:
        errors.append(f"unexpected request fields: {unexpected}")
    if normalized.get("schema_version") != DRAMATICA_FLOW_INFORMED_RUBRIC_REQUEST_SCHEMA_VERSION:
        errors.append("schema_version must use the exact app-owned request schema")
    if normalized.get("rubric_id") != DRAMATICA_FLOW_INFORMED_RUBRIC_ID:
        errors.append("rubric_id must use the exact app-owned rubric identity")
    for field in ("request_id", "project_name", "source_locator"):
        if not _safe_id(normalized.get(field)):
            errors.append(f"{field} must be a non-empty safe identifier")
    if not _non_empty_string(normalized.get("source_text")):
        errors.append("source_text must be a non-empty owner-authored or owner-provided string")
    for field in ("source_refs", "evidence_refs", "provenance_refs"):
        if not _valid_refs(normalized.get(field)):
            errors.append(f"{field} must be a non-empty ordered unique safe reference list")
    if not _valid_refs(normalized.get("source_locator_refs"), locator=True):
        errors.append("source_locator_refs must be a non-empty ordered unique locator-reference list")
    if normalized.get("source_locator") not in (normalized.get("source_locator_refs") or []):
        errors.append("source_locator must appear in source_locator_refs")
    categories = normalized.get("requested_categories")
    if not isinstance(categories, list) or not categories or len(categories) != len(set(categories)):
        errors.append("requested_categories must be a non-empty ordered unique list")
    elif any(category not in ALLOWED_CATEGORIES for category in categories):
        errors.append("requested_categories contains an unknown category")
    if normalized.get("analysis_intent") != "diagnostic_support":
        errors.append("analysis_intent must equal 'diagnostic_support'")
    if normalized.get("owner_authored_or_owner_provided_source") is not True:
        errors.append("owner_authored_or_owner_provided_source must be exactly True")
    confirmations = normalized.get("safety_confirmations")
    if not isinstance(confirmations, dict):
        errors.append("safety_confirmations must be a dictionary")
    else:
        if set(confirmations) != ALLOWED_REQUEST_SAFETY_CONFIRMATIONS:
            errors.append("safety_confirmations must contain exactly the required keys")
        for key in ALLOWED_REQUEST_SAFETY_CONFIRMATIONS:
            if confirmations.get(key) is not True:
                errors.append(f"safety_confirmations[{key!r}] must be exactly True")
    if errors:
        return _failure(errors, "normalized_request", normalized)
    return _success("normalized_request", normalized)


def _validate_evidence(value: Any, source_locator: Any, path: str, errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        errors.append(f"{path} must be a non-empty evidence list")
        return
    for index, evidence in enumerate(value):
        item_path = f"{path}[{index}]"
        if not isinstance(evidence, dict):
            errors.append(f"{item_path} must be a dictionary")
            continue
        if set(evidence) != EVIDENCE_REQUIRED_FIELDS:
            errors.append(f"{item_path} must contain only source_excerpt and source_locator")
        if not _non_empty_string(evidence.get("source_excerpt")):
            errors.append(f"{item_path}.source_excerpt must be non-empty")
        if evidence.get("source_locator") != source_locator:
            errors.append(f"{item_path}.source_locator must match the item source_locator")


def _validate_item(item: Any, bucket: str, index: int, errors: list[str], ids: set[str]) -> None:
    path = f"{bucket}[{index}]"
    if not isinstance(item, dict):
        errors.append(f"{path} must be a dictionary")
        return
    missing = sorted(ITEM_REQUIRED_FIELDS - set(item))
    unexpected = sorted(set(item) - ITEM_REQUIRED_FIELDS)
    if missing:
        errors.append(f"{path} missing required item fields: {missing}")
    if unexpected:
        errors.append(f"{path} contains unexpected item fields: {unexpected}")
    item_id = item.get("item_id")
    if not _safe_id(item_id):
        errors.append(f"{path}.item_id must be a safe unique identifier")
    elif item_id in ids:
        errors.append(f"{path}.item_id must be unique")
    else:
        ids.add(item_id)
    category = item.get("category")
    allowed_bucket = QUESTION_CATEGORIES if bucket == "diagnostic_questions" else NON_QUESTION_CATEGORIES
    if category not in allowed_bucket:
        errors.append(f"{path}.category is not allowed in {bucket}")
    if item.get("candidate_type") != CATEGORY_TO_CANDIDATE_TYPE.get(category):
        errors.append(f"{path}.candidate_type does not match category mapping")
    if item.get("statement_kind") != CATEGORY_TO_STATEMENT_KIND.get(category):
        errors.append(f"{path}.statement_kind does not match category mapping")
    for field in ("label", "diagnostic_text"):
        if not _non_empty_string(item.get(field)):
            errors.append(f"{path}.{field} must be a non-empty string")
    if category in QUESTION_CATEGORIES and isinstance(item.get("diagnostic_text"), str) and not item["diagnostic_text"].rstrip().endswith("?"):
        errors.append(f"{path}.diagnostic_text must end with '?' for a question")
    source_locator = item.get("source_locator")
    if not _safe_id(source_locator):
        errors.append(f"{path}.source_locator must be a safe locator")
    _validate_evidence(item.get("evidence"), source_locator, f"{path}.evidence", errors)
    for field in ("source_refs", "evidence_refs", "provenance_refs"):
        if not _valid_refs(item.get(field)):
            errors.append(f"{path}.{field} must be a non-empty ordered unique safe list")
    if not _valid_refs(item.get("source_locator_refs"), locator=True):
        errors.append(f"{path}.source_locator_refs must be a non-empty ordered unique locator list")
    if source_locator not in (item.get("source_locator_refs") or []):
        errors.append(f"{path}.source_locator must appear in source_locator_refs")
    if not _valid_provenance(item.get("provenance")):
        errors.append(f"{path}.provenance must be exact app-owned provenance")
    if item.get("support_label") != DRAMATICA_FLOW_INFORMED_RUBRIC_SUPPORT_LABEL:
        errors.append(f"{path}.support_label must be the exact app-owned support label")
    confidence = item.get("confidence")
    if confidence not in ALLOWED_CONFIDENCE_VALUES:
        errors.append(f"{path}.confidence must be low_support or medium_support")
    uncertainty = item.get("uncertainty_label")
    if uncertainty not in ALLOWED_UNCERTAINTY_VALUES:
        errors.append(f"{path}.uncertainty_label is not allowed")
    elif category == "ambiguity" and uncertainty != "ambiguity":
        errors.append(f"{path}.uncertainty_label must be ambiguity")
    elif category == "insufficient_evidence" and uncertainty != "insufficient_evidence":
        errors.append(f"{path}.uncertainty_label must be insufficient_evidence")
    elif category in QUESTION_CATEGORIES and uncertainty not in {"null", "requires_owner_interpretation"}:
        errors.append(f"{path}.uncertainty_label is invalid for a question")
    elif category not in {"ambiguity", "insufficient_evidence"} | QUESTION_CATEGORIES and uncertainty not in {"null", "conflicting_support", "requires_owner_interpretation"}:
        errors.append(f"{path}.uncertainty_label is invalid for substantive support")
    if item.get("owner_decision") != {"approved": False, "decision": "pending"}:
        errors.append(f"{path}.owner_decision must remain pending and unapproved")
    if item.get("review_status") != "candidate_review_pending":
        errors.append(f"{path}.review_status must equal candidate_review_pending")
    for flag in ITEM_OPERATION_FLAGS:
        if item.get(flag) is not False:
            errors.append(f"{path}.{flag} must be exactly False")


def validate_dramatica_flow_informed_rubric_result(result: object) -> dict[str, Any]:
    """Validate and deep-copy an app-owned rubric result; fail closed on claims."""
    if not isinstance(result, dict):
        return _failure(["result must be a dictionary"], "normalized_result", {})
    normalized = copy.deepcopy(result)
    errors: list[str] = []
    missing = sorted(RESULT_REQUIRED_FIELDS - set(normalized))
    unexpected = sorted(set(normalized) - RESULT_ALLOWED_FIELDS)
    if missing:
        errors.append(f"missing required result fields: {missing}")
    if unexpected:
        errors.append(f"unexpected result fields: {unexpected}")
    if normalized.get("schema_version") != DRAMATICA_FLOW_INFORMED_RUBRIC_RESULT_SCHEMA_VERSION:
        errors.append("schema_version must use the exact app-owned result schema")
    if normalized.get("rubric_id") != DRAMATICA_FLOW_INFORMED_RUBRIC_ID:
        errors.append("rubric_id must use the exact app-owned rubric identity")
    if normalized.get("output_class") != DRAMATICA_FLOW_INFORMED_RUBRIC_OUTPUT_CLASS:
        errors.append("output_class must equal rubric_mapping_support")
    if normalized.get("display_label") != DRAMATICA_FLOW_INFORMED_RUBRIC_SUPPORT_LABEL:
        errors.append("display_label must use the exact app-owned support label")
    status = normalized.get("status")
    if status not in ALLOWED_STATUSES:
        errors.append("status is not allowed")
    if not _valid_provenance(normalized.get("provenance")):
        errors.append("provenance must be exact app-owned provenance")
    for field in ("source_refs", "evidence_refs", "provenance_refs"):
        if not _valid_refs(normalized.get(field)):
            errors.append(f"{field} must be a non-empty ordered unique safe list")
    if not _valid_refs(normalized.get("source_locator_refs"), locator=True):
        errors.append("source_locator_refs must be a non-empty ordered unique locator list")
    buckets = ("candidate_support", "diagnostic_questions", "uncertainty_notes", "insufficient_evidence_notes")
    for bucket in buckets:
        if not isinstance(normalized.get(bucket), list):
            errors.append(f"{bucket} must be a list")
    safety = normalized.get("safety")
    if not isinstance(safety, dict) or set(safety) != set(OPERATION_FLAGS):
        errors.append("safety must contain exactly the hard-false operation flags")
    elif any(safety.get(flag) is not False for flag in OPERATION_FLAGS):
        errors.append("every safety operation flag must be exactly False")
    ids: set[str] = set()
    bucket_categories = {
        "candidate_support": NON_QUESTION_CATEGORIES - {"ambiguity", "insufficient_evidence"},
        "diagnostic_questions": QUESTION_CATEGORIES,
        "uncertainty_notes": frozenset({"ambiguity"}),
        "insufficient_evidence_notes": frozenset({"insufficient_evidence"}),
    }
    for bucket, allowed in bucket_categories.items():
        value = normalized.get(bucket)
        if isinstance(value, list):
            for index, item in enumerate(value):
                _validate_item(item, "diagnostic_questions" if bucket == "diagnostic_questions" else "candidate_support", index, errors, ids)
                if isinstance(item, dict) and item.get("category") not in allowed:
                    errors.append(f"{bucket}[{index}].category is not allowed in this bucket")
    finding_count = sum(len(normalized.get(bucket) or []) for bucket in buckets if isinstance(normalized.get(bucket), list))
    if status == "succeeded" and finding_count == 0:
        errors.append("succeeded status requires at least one finding")
    if status in {"empty", "failed_closed", "error"} and finding_count:
        errors.append("non-success status must contain empty finding buckets")
    reason = normalized.get("fail_closed_reason")
    if status in {"failed_closed", "error"} and not _non_empty_string(reason):
        errors.append("failed_closed and error statuses require a safe fail_closed_reason")
    if status in {"succeeded", "empty"} and reason is not None:
        errors.append("successful or empty results must not contain fail_closed_reason")
    _scan_unsafe(normalized, "result", errors)
    if errors:
        return _failure(errors, "normalized_result", normalized)
    return _success("normalized_result", normalized)


def _provenance() -> dict[str, Any]:
    return {
        "tool_source": DRAMATICA_FLOW_INFORMED_RUBRIC_ID,
        "adapter": DRAMATICA_FLOW_INFORMED_RUBRIC_ID,
        "support": DRAMATICA_FLOW_INFORMED_RUBRIC_SUPPORT_LABEL,
        "executes_dramatica_flow": False,
        "official_dramatica_flow_output": False,
    }


def _safe_refs(request: Any) -> dict[str, list[str]]:
    result = {field: [] for field in ("source_refs", "evidence_refs", "provenance_refs", "source_locator_refs")}
    if not isinstance(request, dict):
        return result
    for field in ("source_refs", "evidence_refs", "provenance_refs"):
        value = request.get(field)
        if _valid_refs(value):
            result[field] = copy.deepcopy(value)
    value = request.get("source_locator_refs")
    if _valid_refs(value, locator=True):
        result["source_locator_refs"] = copy.deepcopy(value)
    return result


def _safe_reason(reason: Any) -> str:
    if not isinstance(reason, str) or not reason.strip() or _UNSAFE_RE.search(reason):
        return "unsafe_or_invalid_input"
    compact = " ".join(reason.split())
    return compact[:160] or "unsafe_or_invalid_input"


def build_dramatica_flow_informed_rubric_fail_closed_result(
    reason: object, *, request: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Build a complete, safe, empty result without raising on malformed input."""
    refs = _safe_refs(request)
    return {
        "schema_version": DRAMATICA_FLOW_INFORMED_RUBRIC_RESULT_SCHEMA_VERSION,
        "rubric_id": DRAMATICA_FLOW_INFORMED_RUBRIC_ID,
        "output_class": DRAMATICA_FLOW_INFORMED_RUBRIC_OUTPUT_CLASS,
        "status": "failed_closed",
        "display_label": DRAMATICA_FLOW_INFORMED_RUBRIC_SUPPORT_LABEL,
        "provenance": _provenance(),
        **refs,
        "candidate_support": [],
        "diagnostic_questions": [],
        "uncertainty_notes": [],
        "insufficient_evidence_notes": [],
        "safety": {flag: False for flag in OPERATION_FLAGS},
        "fail_closed_reason": _safe_reason(reason),
    }
