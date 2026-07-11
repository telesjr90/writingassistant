"""App-owned Subtxt-informed semantic-rubric contract (PHASE8-IMPL-023-T019C).

This module defines a pure, app-owned input/output contract for future
Subtxt-informed semantic-rubric evaluation. It is a contract-only module
that never executes Subtxt, never reads or imports ``.external_sources``,
never inspects or classifies real project text, never calls a model,
never persists candidates, and never mutates projects, Memory, or Canon.

Boundary phrases: confidence/support is not truth; tool output is not
canon; tool output is not truth; no automatic Storyform; no automatic
Dramatica/Storyform truth; no official Subtxt output; no live Subtxt
runtime; no generated prose; no rewrite; no continuation; no outline;
no candidate persistence; no review-queue creation; no Memory/Canon
mutation; no promotion record; no apply-promotion; no training/model
artifacts; fail closed; no silent fallback; queue presence is not
approval; candidate persistence is not canon.

Public surface area is exactly:

* ``SUBTXT_INFORMED_RUBRIC_REQUEST_SCHEMA_VERSION``
* ``SUBTXT_INFORMED_RUBRIC_RESULT_SCHEMA_VERSION``
* ``SUBTXT_INFORMED_RUBRIC_ID``
* ``SUBTXT_INFORMED_RUBRIC_OUTPUT_CLASS``
* ``SUBTXT_INFORMED_RUBRIC_SUPPORT_LABEL``
* ``ALLOWED_CATEGORIES`` (frozenset of diagnostic category names)
* ``QUESTION_CATEGORIES`` (frozenset of question category names)
* ``NON_QUESTION_CATEGORIES`` (frozenset of non-question category names)
* ``CATEGORY_TO_CANDIDATE_TYPE`` (frozenset of valid candidate type names)
* ``ALLOWED_CONFIDENCE_VALUES`` (frozenset of allowed confidence values)
* ``ALLOWED_UNCERTAINTY_VALUES`` (frozenset of allowed uncertainty values)
* ``ALLOWED_STATUSES`` (frozenset of allowed result statuses)
* ``ALLOWED_STATEMENT_KINDS`` (frozenset of allowed statement kinds)
* ``ALLOWED_REQUEST_SAFETY_CONFIRMATIONS`` (frozenset of required
  request safety confirmation keys)
* ``validate_subtxt_informed_rubric_request(request)``
* ``validate_subtxt_informed_rubric_result(result)``
* ``build_subtxt_informed_rubric_fail_closed_result(reason, *, request=None)``
"""

from __future__ import annotations

import copy
import re
from typing import Any


# ---------------------------------------------------------------------------
# Public schema and identity constants (exact strings).
# ---------------------------------------------------------------------------

SUBTXT_INFORMED_RUBRIC_REQUEST_SCHEMA_VERSION = (
    "omi_app_owned_subtxt_informed_rubric_request.v1"
)

SUBTXT_INFORMED_RUBRIC_RESULT_SCHEMA_VERSION = (
    "omi_app_owned_subtxt_informed_rubric_result.v1"
)

SUBTXT_INFORMED_RUBRIC_ID = "app_owned_subtxt_informed_rubric"

SUBTXT_INFORMED_RUBRIC_OUTPUT_CLASS = "rubric_mapping_support"

SUBTXT_INFORMED_RUBRIC_SUPPORT_LABEL = (
    "App-owned Subtxt-informed diagnostic support"
)


# ---------------------------------------------------------------------------
# Allowed category / candidate-type / status / confidence / uncertainty sets.
# ---------------------------------------------------------------------------

ALLOWED_CATEGORIES = frozenset(
    {
        "structural_diagnostic",
        "conflict_diagnostic",
        "throughline_context_question",
        "story_point_context_question",
        "source_of_conflict_hypothesis",
        "subject_vs_conflict_question",
        "ambiguity",
        "insufficient_evidence",
        "owner_review_question",
    }
)

QUESTION_CATEGORIES = frozenset(
    {
        "throughline_context_question",
        "story_point_context_question",
        "subject_vs_conflict_question",
        "owner_review_question",
    }
)

NON_QUESTION_CATEGORIES = frozenset(
    {
        "structural_diagnostic",
        "conflict_diagnostic",
        "source_of_conflict_hypothesis",
        "ambiguity",
        "insufficient_evidence",
    }
)

CATEGORY_TO_CANDIDATE_TYPE = {
    "structural_diagnostic": "structural_diagnostic",
    "conflict_diagnostic": "conflict_diagnostic",
    "throughline_context_question": "diagnostic_question",
    "story_point_context_question": "diagnostic_question",
    "source_of_conflict_hypothesis": "conflict_diagnostic",
    "subject_vs_conflict_question": "diagnostic_question",
    "ambiguity": "ambiguity",
    "insufficient_evidence": "evidence_note",
    "owner_review_question": "diagnostic_question",
}

CATEGORY_TO_STATEMENT_KIND = {
    "structural_diagnostic": "candidate_observation",
    "conflict_diagnostic": "candidate_observation",
    "source_of_conflict_hypothesis": "hypothesis",
    "ambiguity": "ambiguity",
    "insufficient_evidence": "insufficient_evidence",
}

ALLOWED_CANDIDATE_TYPES = frozenset(
    {
        "structural_diagnostic",
        "conflict_diagnostic",
        "diagnostic_question",
        "ambiguity",
        "evidence_note",
    }
)

ALLOWED_CONFIDENCE_VALUES = frozenset(
    {"low_support", "medium_support", "high_support"}
)

ALLOWED_UNCERTAINTY_VALUES = frozenset(
    {
        "null",
        "ambiguity",
        "insufficient_evidence",
        "conflicting_support",
        "requires_owner_interpretation",
    }
)

ALLOWED_STATUSES = frozenset(
    {"succeeded", "empty", "failed_closed", "error"}
)

ALLOWED_STATEMENT_KINDS = frozenset(
    {
        "candidate_observation",
        "hypothesis",
        "ambiguity",
        "insufficient_evidence",
        "question",
    }
)

ALLOWED_REQUEST_SAFETY_CONFIRMATIONS = frozenset(
    {
        "no_subtxt_execution",
        "no_official_subtxt_output_claim",
        "no_storyform_truth",
        "no_generated_prose",
        "no_rewrite",
        "no_continuation",
        "no_outline",
        "no_candidate_persistence",
        "no_review_queue_creation",
        "no_memory_canon_mutation",
        "no_promotion_record",
        "no_apply_promotion",
        "no_training_artifacts",
    }
)


# ---------------------------------------------------------------------------
# Required field sets and item/result base shapes.
# ---------------------------------------------------------------------------

REQUEST_REQUIRED_FIELDS = frozenset(
    {
        "schema_version",
        "rubric_id",
        "request_id",
        "project_name",
        "source_text",
        "source_locator",
        "source_refs",
        "evidence_refs",
        "provenance_refs",
        "source_locator_refs",
        "requested_categories",
        "analysis_intent",
        "owner_authored_or_owner_provided_source",
        "safety_confirmations",
    }
)

RESULT_REQUIRED_FIELDS = frozenset(
    {
        "schema_version",
        "rubric_id",
        "output_class",
        "status",
        "display_label",
        "provenance",
        "source_refs",
        "evidence_refs",
        "provenance_refs",
        "source_locator_refs",
        "candidate_support",
        "diagnostic_questions",
        "uncertainty_notes",
        "insufficient_evidence_notes",
        "safety",
    }
)

ITEM_REQUIRED_FIELDS = frozenset(
    {
        "item_id",
        "category",
        "candidate_type",
        "label",
        "diagnostic_text",
        "statement_kind",
        "evidence",
        "source_locator",
        "source_refs",
        "evidence_refs",
        "provenance_refs",
        "source_locator_refs",
        "provenance",
        "support_label",
        "confidence",
        "uncertainty_label",
        "owner_decision",
        "review_status",
        "executes_subtxt",
        "official_subtxt_output",
    }
)

EVIDENCE_REQUIRED_FIELDS = frozenset({"source_excerpt", "source_locator"})

ALLOWED_OPERATION_FLAGS = (
    "executes_subtxt",
    "official_subtxt_output",
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


# ---------------------------------------------------------------------------
# Regex patterns.
# ---------------------------------------------------------------------------

_SAFE_ID_RE = re.compile(r"^[A-Za-z0-9_-]+$")
_SAFE_SOURCE_LOCATOR_RE = re.compile(r"^source_locator_ref_[A-Za-z0-9_-]+$")
_SAFE_REF_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
_REQUEST_ID_RE = re.compile(r"^[A-Za-z0-9_.-]+$")

# Recursive unsafe output patterns checked in normalized findings / labels /
# claims / questions / metadata / operation fields. These do NOT apply to
# source_text or evidence.source_excerpt (quoted owner source material).
_UNSAFE_OUTPUT_RE = re.compile(
    r"\b("
    r"truth|final|canon|canonized|approved|promoted\b|"
    r"storyform|storyform_truth|"
    r"objectively speak|conclusiv|definitiv\b|"
    r"\bos\b|\bmc\b|\bic\b|\brs\b|"
    r"\bproblem\b|\bsolution\b|\bconcern\b|\bissue\b|"
    r"\bdomain\b|\bapproach\b|\bdynamic\b|\bsignpost\b|"
    r"official[ _-]?subtxt|subtxt[ _-]?official|"
    r"live[ _-]?subtxt|subtxt[ _-]?runtime|"
    r"subtxt[ _-]?confirm|subtxt[ _-]?endors|subtxt[ _-]?compat|"
    r"generate[_ -]?prose|write[_ -]?prose|story[_ -]?prose|"
    r"rewrite|continu(?:e|ation)|outlin(?:e|ing)|draft|"
    r"polish|improve|expand|revis(?:e|ion)|imitat|chapter|"
    r"persist[_ -]?candidate|review[_ -]?queue|"
    r"memory[_ -]?canon|canon[_ -]?mutation|"
    r"promotion[_ -]?record|apply[_ -]?promotion|"
    r"training[_ -]?artifact|model[_ -]?artifact|"
    r"project[_ -]?mutation|scene[_ -]?mutation|note[_ -]?mutation|material[_ -]?mutation"
    r")\b",
    re.IGNORECASE,
)

# Prose-intent patterns that mark a diagnostic question as a request to
# generate prose / continuation / outline / etc. (defensive overlap with
# _UNSAFE_OUTPUT_RE, kept explicit because the question branch must refuse
# such questions even when no other truth label is present).
_PROSE_INTENT_QUESTION_RE = re.compile(
    r"\b(generate|rewrite|continue|outline|draft|polish|improve|"
    r"expand|imitate|write|export|revise)\b.{0,80}\b("
    r"prose|scene|chapter|ending|passage|dialogue|paragraph|style|"
    r"sentence|paragraph|continuation|rewrite|draft|story|"
    r"the next|the following|an outline|a draft"
    r")\b",
    re.IGNORECASE | re.DOTALL,
)


# ---------------------------------------------------------------------------
# Validation response builders.
# ---------------------------------------------------------------------------


def _base_response(status: str, *, valid: bool, fail_closed: bool) -> dict[str, Any]:
    response: dict[str, Any] = {
        "status": status,
        "valid": valid,
        "fail_closed": fail_closed,
        "errors": [],
        "executes_subtxt": False,
        "official_subtxt_output": False,
        "persists_candidates": False,
        "creates_review_queue_entries": False,
        "mutates_memory_canon": False,
        "creates_promotion_records": False,
        "applies_promotion": False,
        "generates_prose": False,
        "rewrites_prose": False,
        "continues_prose": False,
        "creates_outline": False,
        "creates_training_artifacts": False,
    }
    return response


def _fail_response(errors: list[str], **extra: Any) -> dict[str, Any]:
    response = _base_response("fail_closed", valid=False, fail_closed=True)
    for key, value in extra.items():
        response[key] = value
    response["errors"] = list(errors)
    return response


def _valid_request_response(normalized_request: dict[str, Any]) -> dict[str, Any]:
    response = _base_response("valid", valid=True, fail_closed=False)
    response["normalized_request"] = copy.deepcopy(normalized_request)
    response["errors"] = []
    return response


def _valid_result_response(normalized_result: dict[str, Any]) -> dict[str, Any]:
    response = _base_response("valid", valid=True, fail_closed=False)
    response["normalized_result"] = copy.deepcopy(normalized_result)
    response["errors"] = []
    return response


# ---------------------------------------------------------------------------
# Small helper predicates (all pure).
# ---------------------------------------------------------------------------


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value)


def _safe_identifier(value: Any) -> bool:
    return isinstance(value, str) and bool(_SAFE_ID_RE.fullmatch(value))


def _safe_request_id(value: Any) -> bool:
    return isinstance(value, str) and bool(_REQUEST_ID_RE.fullmatch(value))


def _safe_source_locator_ref(value: Any) -> bool:
    return (
        isinstance(value, str)
        and bool(value)
        and bool(_SAFE_SOURCE_LOCATOR_RE.fullmatch(value))
    )


def _safe_ref_string(value: Any) -> bool:
    return (
        isinstance(value, str)
        and bool(value)
        and bool(_SAFE_REF_RE.fullmatch(value))
    )


def _is_non_empty_ref_list(value: Any) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(_safe_ref_string(item) for item in value)
    )


def _is_non_empty_source_locator_ref_list(value: Any) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(_safe_source_locator_ref(item) for item in value)
    )


def _is_deduplicated_string_list(value: Any) -> bool:
    if not isinstance(value, list) or not value:
        return False
    seen: set[str] = set()
    for item in value:
        if not _is_non_empty_string(item):
            return False
        if item in seen:
            return False
        seen.add(item)
    return True


def _is_evidence_list(value: Any) -> bool:
    if not isinstance(value, list) or not value:
        return False
    for item in value:
        if not isinstance(item, dict):
            return False
        excerpt = item.get("source_excerpt")
        locator = item.get("source_locator")
        if not _is_non_empty_string(excerpt):
            return False
        if not _is_non_empty_string(locator):
            return False
    return True


def _is_owner_decision_pending(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and value.get("approved") is False
        and value.get("decision") == "pending"
    )


def _is_safe_provenance(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    if value.get("tool_source") != SUBTXT_INFORMED_RUBRIC_ID:
        return False
    if value.get("adapter") != SUBTXT_INFORMED_RUBRIC_ID:
        return False
    if value.get("support") != SUBTXT_INFORMED_RUBRIC_SUPPORT_LABEL:
        return False
    if value.get("executes_subtxt") is not False:
        return False
    if value.get("official_subtxt_output") is not False:
        return False
    return True


def _has_any_unsafe_word(text: str) -> bool:
    return bool(_UNSAFE_OUTPUT_RE.search(text))


def _has_prose_intent_question(text: str) -> bool:
    return bool(_PROSE_INTENT_QUESTION_RE.search(text))


def _check_unsafe_label_text(
    label: Any,
    field_path: str,
    errors: list[str],
) -> None:
    """Fail-closed on unsafe labels/texts in normalized items (not source
    text and not evidence excerpts)."""
    if isinstance(label, str) and _has_any_unsafe_word(label):
        errors.append(
            f"{field_path} contains forbidden truth/canon/prose/runtime/mutation language: {label!r}"
        )


def _check_prose_intent_in_question(
    text: Any,
    field_path: str,
    errors: list[str],
) -> None:
    if isinstance(text, str) and _has_prose_intent_question(text):
        errors.append(
            f"{field_path} requests prose/rewrite/continuation/outline/draft/expand/polish/improve/revise/imitate which is forbidden in diagnostic questions: {text!r}"
        )


# ---------------------------------------------------------------------------
# request_id / project_name / source_locator validation helpers.
# ---------------------------------------------------------------------------


def _is_valid_request_id(value: Any) -> bool:
    return _is_non_empty_string(value) and _safe_request_id(value)


def _is_valid_project_name(value: Any) -> bool:
    return _is_non_empty_string(value) and _safe_identifier(value)


def _is_valid_source_locator(value: Any) -> bool:
    return _is_non_empty_string(value) and _safe_identifier(value)


# ---------------------------------------------------------------------------
# Public validators.
# ---------------------------------------------------------------------------


def validate_subtxt_informed_rubric_request(
    request: object,
) -> dict[str, Any]:
    """Validate an app-owned Subtxt-informed semantic-rubric request.

    Returns a validation-response dict (never raises for ordinary invalid
    input). See module docstring for boundary phrases.
    """

    if not isinstance(request, dict):
        return _fail_response(
            ["request must be a dictionary"],
            normalized_request={},
        )

    normalized = copy.deepcopy(request)
    errors: list[str] = []

    missing = sorted(REQUEST_REQUIRED_FIELDS - set(normalized))
    if missing:
        return _fail_response(
            [f"missing required request fields: {missing}"],
            normalized_request=normalized,
        )

    if normalized.get("schema_version") != SUBTXT_INFORMED_RUBRIC_REQUEST_SCHEMA_VERSION:
        errors.append(
            "schema_version must equal "
            f"{SUBTXT_INFORMED_RUBRIC_REQUEST_SCHEMA_VERSION!r}"
        )

    if normalized.get("rubric_id") != SUBTXT_INFORMED_RUBRIC_ID:
        errors.append(
            f"rubric_id must equal {SUBTXT_INFORMED_RUBRIC_ID!r}"
        )

    if not _is_valid_request_id(normalized.get("request_id")):
        errors.append("request_id must be a non-empty safe identifier")

    if not _is_valid_project_name(normalized.get("project_name")):
        errors.append("project_name must be a non-empty safe identifier")

    if not _is_non_empty_string(normalized.get("source_text")):
        errors.append("source_text must be a non-empty string")

    source_locator = normalized.get("source_locator")
    if not _is_valid_source_locator(source_locator):
        errors.append("source_locator must be a non-empty safe source locator")

    for field in ("source_refs", "evidence_refs", "provenance_refs"):
        if not _is_non_empty_ref_list(normalized.get(field)):
            errors.append(
                f"{field} must be a non-empty list of non-empty safe strings"
            )

    if not _is_non_empty_source_locator_ref_list(normalized.get("source_locator_refs")):
        errors.append(
            "source_locator_refs must be a non-empty list of non-empty "
            "'source_locator_ref_*' safe strings"
        )

    if (
        isinstance(source_locator, str)
        and isinstance(normalized.get("source_locator_refs"), list)
        and source_locator
        and source_locator not in normalized["source_locator_refs"]
    ):
        errors.append(
            "source_locator must appear in source_locator_refs"
        )

    requested_categories = normalized.get("requested_categories")
    if not _is_deduplicated_string_list(requested_categories):
        errors.append(
            "requested_categories must be a non-empty deduplicated list of "
            "non-empty strings"
        )
    else:
        for category in requested_categories:
            if category not in ALLOWED_CATEGORIES:
                errors.append(
                    f"requested_categories contains unknown category {category!r}"
                )

    if normalized.get("analysis_intent") != "diagnostic_support":
        errors.append(
            "analysis_intent must equal 'diagnostic_support'"
        )

    if normalized.get("owner_authored_or_owner_provided_source") is not True:
        errors.append(
            "owner_authored_or_owner_provided_source must be exactly True"
        )

    safety_confirmations = normalized.get("safety_confirmations")
    if not isinstance(safety_confirmations, dict):
        errors.append("safety_confirmations must be a dictionary")
    else:
        missing_confirmations = sorted(
            ALLOWED_REQUEST_SAFETY_CONFIRMATIONS - set(safety_confirmations)
        )
        if missing_confirmations:
            errors.append(
                "safety_confirmations missing required keys: "
                f"{missing_confirmations}"
            )
        else:
            for key in sorted(ALLOWED_REQUEST_SAFETY_CONFIRMATIONS):
                if safety_confirmations.get(key) is not True:
                    errors.append(
                        f"safety_confirmations[{key!r}] must be exactly True"
                    )

    if errors:
        return _fail_response(errors, normalized_request=normalized)

    return _valid_request_response(normalized)


def validate_subtxt_informed_rubric_result(
    result: object,
) -> dict[str, Any]:
    """Validate an app-owned Subtxt-informed semantic-rubric result.

    Returns a validation-response dict (never raises for ordinary invalid
    input). See module docstring for boundary phrases.
    """

    if not isinstance(result, dict):
        return _fail_response(
            ["result must be a dictionary"],
            normalized_result={},
        )

    normalized = copy.deepcopy(result)
    errors: list[str] = []

    missing = sorted(RESULT_REQUIRED_FIELDS - set(normalized))
    if missing:
        return _fail_response(
            [f"missing required result fields: {missing}"],
            normalized_result=normalized,
        )

    if normalized.get("schema_version") != SUBTXT_INFORMED_RUBRIC_RESULT_SCHEMA_VERSION:
        errors.append(
            "schema_version must equal "
            f"{SUBTXT_INFORMED_RUBRIC_RESULT_SCHEMA_VERSION!r}"
        )

    if normalized.get("rubric_id") != SUBTXT_INFORMED_RUBRIC_ID:
        errors.append(
            f"rubric_id must equal {SUBTXT_INFORMED_RUBRIC_ID!r}"
        )

    if normalized.get("output_class") != SUBTXT_INFORMED_RUBRIC_OUTPUT_CLASS:
        errors.append(
            f"output_class must equal {SUBTXT_INFORMED_RUBRIC_OUTPUT_CLASS!r}"
        )

    if normalized.get("display_label") != SUBTXT_INFORMED_RUBRIC_SUPPORT_LABEL:
        errors.append(
            f"display_label must equal {SUBTXT_INFORMED_RUBRIC_SUPPORT_LABEL!r}"
        )

    if normalized.get("status") not in ALLOWED_STATUSES:
        errors.append(
            f"status must be one of {sorted(ALLOWED_STATUSES)}"
        )

    if not _is_safe_provenance(normalized.get("provenance")):
        errors.append(
            "provenance must use app-owned identity "
            f"{SUBTXT_INFORMED_RUBRIC_ID!r} and the exact support label, "
            "with executes_subtxt=False and official_subtxt_output=False"
        )

    for field in ("source_refs", "evidence_refs", "provenance_refs"):
        if not _is_non_empty_ref_list(normalized.get(field)):
            errors.append(
                f"{field} must be a non-empty list of non-empty safe strings"
            )

    if not _is_non_empty_source_locator_ref_list(normalized.get("source_locator_refs")):
        errors.append(
            "source_locator_refs must be a non-empty list of non-empty "
            "'source_locator_ref_*' safe strings"
        )

    if not isinstance(normalized.get("candidate_support"), list):
        errors.append("candidate_support must be a list")
    if not isinstance(normalized.get("diagnostic_questions"), list):
        errors.append("diagnostic_questions must be a list")
    if not isinstance(normalized.get("uncertainty_notes"), list):
        errors.append("uncertainty_notes must be a list")
    if not isinstance(normalized.get("insufficient_evidence_notes"), list):
        errors.append("insufficient_evidence_notes must be a list")

    safety = normalized.get("safety")
    if not isinstance(safety, dict):
        errors.append("safety must be a dictionary")
    else:
        for key in ALLOWED_OPERATION_FLAGS:
            if safety.get(key) is not False:
                errors.append(
                    f"safety[{key!r}] must be exactly False"
                )

    if isinstance(normalized.get("candidate_support"), list) and isinstance(
        normalized.get("diagnostic_questions"), list
    ) and isinstance(safety, dict):
        _validate_items(
            normalized,
            errors,
        )

    if errors:
        return _fail_response(errors, normalized_result=normalized)

    return _valid_result_response(normalized)


def _validate_items(
    normalized: dict[str, Any],
    errors: list[str],
) -> None:
    candidate_support = normalized["candidate_support"]
    diagnostic_questions = normalized["diagnostic_questions"]
    status = normalized.get("status")

    for index, item in enumerate(candidate_support):
        _validate_non_question_item(
            item, f"candidate_support[{index}]", errors
        )

    for index, item in enumerate(diagnostic_questions):
        _validate_question_item(
            item, f"diagnostic_questions[{index}]", errors
        )

    if status == "succeeded":
        if not candidate_support and not diagnostic_questions:
            errors.append(
                "succeeded status requires at least one valid item in "
                "candidate_support or diagnostic_questions"
            )
    elif status in {"empty", "failed_closed", "error"}:
        if candidate_support or diagnostic_questions:
            errors.append(
                f"{status} status must contain no items in "
                "candidate_support or diagnostic_questions"
            )


def _validate_non_question_item(
    item: Any,
    field_path: str,
    errors: list[str],
) -> None:
    if not isinstance(item, dict):
        errors.append(f"{field_path} must be a dictionary")
        return

    missing = sorted(ITEM_REQUIRED_FIELDS - set(item))
    if missing:
        errors.append(
            f"{field_path} missing required item fields: {missing}"
        )
        return

    category = item.get("category")
    if category not in NON_QUESTION_CATEGORIES:
        errors.append(
            f"{field_path}.category must be one of "
            f"{sorted(NON_QUESTION_CATEGORIES)}"
        )
        return

    expected_candidate_type = CATEGORY_TO_CANDIDATE_TYPE.get(category)
    if item.get("candidate_type") != expected_candidate_type:
        errors.append(
            f"{field_path}.candidate_type must equal "
            f"{expected_candidate_type!r} for category {category!r}"
        )

    expected_statement_kind = CATEGORY_TO_STATEMENT_KIND.get(category)
    if item.get("statement_kind") != expected_statement_kind:
        errors.append(
            f"{field_path}.statement_kind must equal "
            f"{expected_statement_kind!r} for category {category!r}"
        )

    if item.get("statement_kind") not in ALLOWED_STATEMENT_KINDS:
        errors.append(
            f"{field_path}.statement_kind must be one of "
            f"{sorted(ALLOWED_STATEMENT_KINDS)}"
        )

    label = item.get("label")
    if not _is_non_empty_string(label):
        errors.append(f"{field_path}.label must be a non-empty string")
        _check_unsafe_label_text(label, f"{field_path}.label", errors)
    else:
        _check_unsafe_label_text(label, f"{field_path}.label", errors)

    diagnostic_text = item.get("diagnostic_text")
    if not _is_non_empty_string(diagnostic_text):
        errors.append(f"{field_path}.diagnostic_text must be a non-empty string")
    else:
        if _has_prose_intent_question(diagnostic_text):
            errors.append(
                f"{field_path}.diagnostic_text is prose-like or requests "
                "prose/rewrite/continuation/outline/draft/expand/polish/"
                "improve/revise/imitate which is forbidden in normalized "
                "diagnostic text"
            )
        if _has_any_unsafe_word(diagnostic_text):
            errors.append(
                f"{field_path}.diagnostic_text contains forbidden "
                "truth/canon/approved/prose/runtime/mutation language"
            )

    if not _is_evidence_list(item.get("evidence")):
        errors.append(
            f"{field_path}.evidence must be a non-empty list of "
            "{source_excerpt, source_locator} items"
        )

    if not _is_non_empty_string(item.get("source_locator")):
        errors.append(f"{field_path}.source_locator must be a non-empty string")
    elif item.get("source_locator") not in (item.get("source_locator_refs") or []):
        errors.append(
            f"{field_path}.source_locator must appear in source_locator_refs"
        )

    for field in ("source_refs", "evidence_refs", "provenance_refs"):
        if not _is_non_empty_ref_list(item.get(field)):
            errors.append(
                f"{field_path}.{field} must be a non-empty list of "
                "non-empty safe strings"
            )

    if not _is_non_empty_source_locator_ref_list(item.get("source_locator_refs")):
        errors.append(
            f"{field_path}.source_locator_refs must be a non-empty list "
            "of 'source_locator_ref_*' safe strings"
        )

    if not _is_safe_provenance(item.get("provenance")):
        errors.append(
            f"{field_path}.provenance must use the app-owned identity and "
            "exact support label, with executes_subtxt=False and "
            "official_subtxt_output=False"
        )

    if item.get("support_label") != SUBTXT_INFORMED_RUBRIC_SUPPORT_LABEL:
        errors.append(
            f"{field_path}.support_label must equal "
            f"{SUBTXT_INFORMED_RUBRIC_SUPPORT_LABEL!r}"
        )

    if item.get("confidence") not in ALLOWED_CONFIDENCE_VALUES:
        errors.append(
            f"{field_path}.confidence must be one of "
            f"{sorted(ALLOWED_CONFIDENCE_VALUES)}"
        )

    uncertainty = item.get("uncertainty_label")
    if uncertainty not in ALLOWED_UNCERTAINTY_VALUES:
        errors.append(
            f"{field_path}.uncertainty_label must be one of "
            f"{sorted(ALLOWED_UNCERTAINTY_VALUES)}"
        )
    elif category == "ambiguity" and uncertainty != "ambiguity":
        errors.append(
            f"{field_path}.uncertainty_label must equal 'ambiguity' for "
            "category 'ambiguity'"
        )
    elif category == "insufficient_evidence" and uncertainty != "insufficient_evidence":
        errors.append(
            f"{field_path}.uncertainty_label must equal 'insufficient_evidence' "
            "for category 'insufficient_evidence'"
        )

    if not _is_owner_decision_pending(item.get("owner_decision")):
        errors.append(
            f"{field_path}.owner_decision must equal "
            "{'approved': False, 'decision': 'pending'}"
        )

    if item.get("review_status") != "candidate_review_pending":
        errors.append(
            f"{field_path}.review_status must equal 'candidate_review_pending'"
        )

    if item.get("executes_subtxt") is not False:
        errors.append(f"{field_path}.executes_subtxt must be exactly False")
    if item.get("official_subtxt_output") is not False:
        errors.append(
            f"{field_path}.official_subtxt_output must be exactly False"
        )


def _validate_question_item(
    item: Any,
    field_path: str,
    errors: list[str],
) -> None:
    if not isinstance(item, dict):
        errors.append(f"{field_path} must be a dictionary")
        return

    missing = sorted(ITEM_REQUIRED_FIELDS - set(item))
    if missing:
        errors.append(
            f"{field_path} missing required item fields: {missing}"
        )
        return

    category = item.get("category")
    if category not in QUESTION_CATEGORIES:
        errors.append(
            f"{field_path}.category must be one of "
            f"{sorted(QUESTION_CATEGORIES)}"
        )
        return

    if item.get("candidate_type") != "diagnostic_question":
        errors.append(
            f"{field_path}.candidate_type must equal 'diagnostic_question' "
            f"for question category {category!r}"
        )

    if item.get("statement_kind") != "question":
        errors.append(
            f"{field_path}.statement_kind must equal 'question' for "
            f"category {category!r}"
        )

    label = item.get("label")
    if not _is_non_empty_string(label):
        errors.append(f"{field_path}.label must be a non-empty string")
    _check_unsafe_label_text(label, f"{field_path}.label", errors)

    diagnostic_text = item.get("diagnostic_text")
    if not _is_non_empty_string(diagnostic_text):
        errors.append(f"{field_path}.diagnostic_text must be a non-empty string")
    else:
        if not diagnostic_text.rstrip().endswith("?"):
            errors.append(
                f"{field_path}.diagnostic_text must end with '?' for "
                f"question category {category!r}"
            )
        _check_prose_intent_in_question(
            diagnostic_text, f"{field_path}.diagnostic_text", errors
        )
        if _has_any_unsafe_word(diagnostic_text):
            errors.append(
                f"{field_path}.diagnostic_text contains forbidden "
                "truth/canon/approved/prose/runtime/mutation language"
            )

    if not _is_evidence_list(item.get("evidence")):
        errors.append(
            f"{field_path}.evidence must be a non-empty list of "
            "{source_excerpt, source_locator} items"
        )

    if not _is_non_empty_string(item.get("source_locator")):
        errors.append(f"{field_path}.source_locator must be a non-empty string")
    elif item.get("source_locator") not in (item.get("source_locator_refs") or []):
        errors.append(
            f"{field_path}.source_locator must appear in source_locator_refs"
        )

    for field in ("source_refs", "evidence_refs", "provenance_refs"):
        if not _is_non_empty_ref_list(item.get(field)):
            errors.append(
                f"{field_path}.{field} must be a non-empty list of "
                "non-empty safe strings"
            )

    if not _is_non_empty_source_locator_ref_list(item.get("source_locator_refs")):
        errors.append(
            f"{field_path}.source_locator_refs must be a non-empty list "
            "of 'source_locator_ref_*' safe strings"
        )

    if not _is_safe_provenance(item.get("provenance")):
        errors.append(
            f"{field_path}.provenance must use the app-owned identity and "
            "exact support label, with executes_subtxt=False and "
            "official_subtxt_output=False"
        )

    if item.get("support_label") != SUBTXT_INFORMED_RUBRIC_SUPPORT_LABEL:
        errors.append(
            f"{field_path}.support_label must equal "
            f"{SUBTXT_INFORMED_RUBRIC_SUPPORT_LABEL!r}"
        )

    if item.get("confidence") not in ALLOWED_CONFIDENCE_VALUES:
        errors.append(
            f"{field_path}.confidence must be one of "
            f"{sorted(ALLOWED_CONFIDENCE_VALUES)}"
        )

    uncertainty = item.get("uncertainty_label")
    if uncertainty not in ALLOWED_UNCERTAINTY_VALUES:
        errors.append(
            f"{field_path}.uncertainty_label must be one of "
            f"{sorted(ALLOWED_UNCERTAINTY_VALUES)}"
        )
    elif uncertainty != "null" and uncertainty != "requires_owner_interpretation":
        errors.append(
            f"{field_path}.uncertainty_label for question category "
            f"{category!r} must be 'null' or 'requires_owner_interpretation'"
        )

    if not _is_owner_decision_pending(item.get("owner_decision")):
        errors.append(
            f"{field_path}.owner_decision must equal "
            "{'approved': False, 'decision': 'pending'}"
        )

    if item.get("review_status") != "candidate_review_pending":
        errors.append(
            f"{field_path}.review_status must equal 'candidate_review_pending'"
        )

    if item.get("executes_subtxt") is not False:
        errors.append(f"{field_path}.executes_subtxt must be exactly False")
    if item.get("official_subtxt_output") is not False:
        errors.append(
            f"{field_path}.official_subtxt_output must be exactly False"
        )


# ---------------------------------------------------------------------------
# Safe provenance builder and fail-closed result builder.
# ---------------------------------------------------------------------------


def _safe_provenance_dict() -> dict[str, Any]:
    return {
        "tool_source": SUBTXT_INFORMED_RUBRIC_ID,
        "adapter": SUBTXT_INFORMED_RUBRIC_ID,
        "support": SUBTXT_INFORMED_RUBRIC_SUPPORT_LABEL,
        "executes_subtxt": False,
        "official_subtxt_output": False,
    }


def _safe_safety_dict() -> dict[str, Any]:
    return {key: False for key in ALLOWED_OPERATION_FLAGS}


def _copy_top_level_refs_from_request(
    request: dict[str, Any] | None,
) -> dict[str, list[str]]:
    if not isinstance(request, dict):
        return {
            "source_refs": [],
            "evidence_refs": [],
            "provenance_refs": [],
            "source_locator_refs": [],
        }
    return {
        "source_refs": list(request.get("source_refs") or []),
        "evidence_refs": list(request.get("evidence_refs") or []),
        "provenance_refs": list(request.get("provenance_refs") or []),
        "source_locator_refs": list(request.get("source_locator_refs") or []),
    }


def build_subtxt_informed_rubric_fail_closed_result(
    reason: str,
    *,
    request: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a complete fail-closed result-envelope-shaped dictionary.

    The result is always a complete result-envelope-shaped dict with zero
    candidates, zero questions, app-owned provenance, and all operation
    flags set to ``False``. The optional ``request`` is consulted for
    top-level ref copying only; an invalid or missing request is
    tolerated and does not raise.
    """

    if not isinstance(reason, str) or not reason.strip():
        safe_reason = "fail_closed"
    else:
        safe_reason = reason

    refs = _copy_top_level_refs_from_request(request)

    return {
        "schema_version": SUBTXT_INFORMED_RUBRIC_RESULT_SCHEMA_VERSION,
        "rubric_id": SUBTXT_INFORMED_RUBRIC_ID,
        "output_class": SUBTXT_INFORMED_RUBRIC_OUTPUT_CLASS,
        "status": "failed_closed",
        "display_label": SUBTXT_INFORMED_RUBRIC_SUPPORT_LABEL,
        "provenance": _safe_provenance_dict(),
        "source_refs": refs["source_refs"],
        "evidence_refs": refs["evidence_refs"],
        "provenance_refs": refs["provenance_refs"],
        "source_locator_refs": refs["source_locator_refs"],
        "candidate_support": [],
        "diagnostic_questions": [],
        "uncertainty_notes": [],
        "insufficient_evidence_notes": [],
        "safety": _safe_safety_dict(),
        "fail_closed_reason": safe_reason,
    }
