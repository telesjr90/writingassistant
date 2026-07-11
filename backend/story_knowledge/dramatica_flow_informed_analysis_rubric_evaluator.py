"""Pure app-owned deterministic evaluator for the committed T020C contract.

The evaluator examines only the supplied in-memory owner source.  Its cue
families, fixed diagnostic wording, thresholds, and precedence are app-owned.
It has no OMI wiring and performs no I/O or state changes.
"""

from __future__ import annotations

import copy
import re
from typing import Any

from backend.story_knowledge.dramatica_flow_informed_analysis_rubric_contract import (
    CATEGORY_TO_CANDIDATE_TYPE,
    CATEGORY_TO_STATEMENT_KIND,
    DRAMATICA_FLOW_INFORMED_RUBRIC_ID,
    DRAMATICA_FLOW_INFORMED_RUBRIC_OUTPUT_CLASS,
    DRAMATICA_FLOW_INFORMED_RUBRIC_RESULT_SCHEMA_VERSION,
    DRAMATICA_FLOW_INFORMED_RUBRIC_SUPPORT_LABEL,
    OPERATION_FLAGS,
    build_dramatica_flow_informed_rubric_fail_closed_result,
    validate_dramatica_flow_informed_rubric_request,
    validate_dramatica_flow_informed_rubric_result,
)


DRAMATICA_FLOW_INFORMED_RUBRIC_EVALUATOR_VERSION = (
    "app_owned_dramatica_flow_informed_rubric_evaluator.v1"
)


# Original app-owned cue families.  Each family is deliberately small and
# describes ordinary English signals rather than any third-party vocabulary.
_CAUSAL_CONNECTOR_CUES = (
    "because", "therefore", "thus", "consequently", "since", "so",
)
_CONSEQUENCE_CUES = (
    "causes", "caused", "causing", "leads to", "led to", "results in",
    "resulted in", "forces", "forced", "consequence", "outcome",
)
_COMMITMENT_OPEN_CUES = (
    "promise", "promises", "promised", "vow", "vows", "vowed",
    "mystery", "mysteries", "hook", "hooks", "obligation", "obligations",
    "unresolved", "unfinished", "still owes", "must return",
)
_COMMITMENT_FOLLOW_THROUGH_CUES = (
    "fulfilled", "kept the promise", "answered", "resolved", "followed through",
    "paid off", "abandoned", "forgotten", "left open",
)
_EMOTIONAL_STATE_CUES = (
    "afraid", "angry", "calm", "grieving", "hopeful", "ashamed", "relieved",
    "anxious", "joyful", "bitter", "numb", "fear", "anger", "grief",
)
_EMOTIONAL_CHANGE_CUES = (
    "became afraid", "grew angry", "calmed down", "felt relieved",
    "turned bitter", "no longer feared", "emotion changed", "mood shifted",
)
_RELATIONSHIP_ROLE_CUES = (
    "ally", "allies", "rival", "rivals", "friend", "friends", "partner",
    "partners", "mentor", "student", "parent", "child", "sibling", "enemy",
)
_RELATIONSHIP_CHANGE_CUES = (
    "became an ally", "became allies", "became a rival", "became rivals",
    "turned against", "reconciled",
    "betrayed", "separated", "grew closer", "drifted apart", "lost trust",
    "earned trust", "former ally", "former rival",
)
_TEMPORAL_ORDER_CUES = (
    "before", "after", "earlier", "later", "then", "meanwhile", "eventually",
    "the next day", "that night", "years ago",
)
_THREAD_ACTIVITY_CUES = (
    "returns", "returned", "reappears", "reappeared", "delayed", "postponed",
    "inactive", "dormant", "still waiting", "thread", "resumes", "resumed",
)
_KNOWLEDGE_ACCESS_CUES = (
    "knows", "knew", "learns", "learned", "discovers", "discovered",
    "realizes", "realized", "witnessed", "overheard", "read the letter",
    "inferred", "deduced",
)
_INFORMATION_TRANSFER_CUES = (
    "told", "reported", "revealed", "disclosed", "concealed", "hid from",
    "kept secret", "did not know", "could not know", "without being told",
)
_UNCERTAINTY_CUES = (
    "maybe", "perhaps", "might", "may have", "could be", "possibly", "seems",
    "appears", "unclear", "uncertain", "unknown", "not sure",
)
_CONFLICTING_SIGNAL_CUES = (
    "but also", "yet also", "on the other hand", "both true and false",
    "conflicting accounts", "contradictory accounts",
)

_WORD_RE = re.compile(r"\b[\w'-]+\b")
_SPAN_SPLIT_RE = re.compile(r"(?<=[.!?;:])(?:[ \t]+|\r?\n+)|\r?\n+")


def _cue_pattern(cues: tuple[str, ...]) -> re.Pattern[str]:
    alternatives = sorted((re.escape(cue) for cue in cues), key=len, reverse=True)
    return re.compile(r"(?<!\w)(?:" + "|".join(alternatives) + r")(?!\w)", re.IGNORECASE)


_CAUSAL_CONNECTOR_RE = _cue_pattern(_CAUSAL_CONNECTOR_CUES)
_CONSEQUENCE_RE = _cue_pattern(_CONSEQUENCE_CUES)
_COMMITMENT_OPEN_RE = _cue_pattern(_COMMITMENT_OPEN_CUES)
_COMMITMENT_FOLLOW_THROUGH_RE = _cue_pattern(_COMMITMENT_FOLLOW_THROUGH_CUES)
_EMOTIONAL_STATE_RE = _cue_pattern(_EMOTIONAL_STATE_CUES)
_EMOTIONAL_CHANGE_RE = _cue_pattern(_EMOTIONAL_CHANGE_CUES)
_RELATIONSHIP_ROLE_RE = _cue_pattern(_RELATIONSHIP_ROLE_CUES)
_RELATIONSHIP_CHANGE_RE = _cue_pattern(_RELATIONSHIP_CHANGE_CUES)
_TEMPORAL_ORDER_RE = _cue_pattern(_TEMPORAL_ORDER_CUES)
_THREAD_ACTIVITY_RE = _cue_pattern(_THREAD_ACTIVITY_CUES)
_KNOWLEDGE_ACCESS_RE = _cue_pattern(_KNOWLEDGE_ACCESS_CUES)
_INFORMATION_TRANSFER_RE = _cue_pattern(_INFORMATION_TRANSFER_CUES)
_UNCERTAINTY_RE = _cue_pattern(_UNCERTAINTY_CUES)
_CONFLICTING_SIGNAL_RE = _cue_pattern(_CONFLICTING_SIGNAL_CUES)

_SUBSTANTIVE_CATEGORIES = frozenset(
    {
        "causal_chain_diagnostic",
        "narrative_commitment_lifecycle_diagnostic",
        "emotional_state_consistency",
        "relationship_delta_diagnostic",
        "timeline_thread_activity_diagnostic",
        "information_boundary_diagnostic",
    }
)
_QUESTION_CATEGORIES = frozenset(
    {"multidimensional_diagnostic_question", "owner_review_question"}
)
_MIN_MATERIAL_WORDS = 12

_CATEGORY_LABELS = {
    "causal_chain_diagnostic": "Causal linkage signal",
    "narrative_commitment_lifecycle_diagnostic": "Commitment lifecycle signal",
    "emotional_state_consistency": "Emotional consistency signal",
    "relationship_delta_diagnostic": "Relationship change signal",
    "timeline_thread_activity_diagnostic": "Timeline activity signal",
    "information_boundary_diagnostic": "Information boundary signal",
    "multidimensional_diagnostic_question": "Cross-dimension diagnostic question",
    "ambiguity": "Ambiguous diagnostic signal",
    "insufficient_evidence": "Limited diagnostic evidence",
    "owner_review_question": "Owner diagnostic question",
}
_CATEGORY_DIAGNOSTIC_TEXT = {
    "causal_chain_diagnostic": (
        "The evidence contains cause or consequence signals that warrant owner interpretation."
    ),
    "narrative_commitment_lifecycle_diagnostic": (
        "The evidence contains an open commitment or follow-through signal that warrants owner interpretation."
    ),
    "emotional_state_consistency": (
        "The evidence contains an emotional state or change signal that warrants a consistency check."
    ),
    "relationship_delta_diagnostic": (
        "The evidence contains a relationship role or change signal that warrants owner interpretation."
    ),
    "timeline_thread_activity_diagnostic": (
        "The evidence contains ordering or thread-activity signals that warrant a timing check."
    ),
    "information_boundary_diagnostic": (
        "The evidence contains knowledge-access or disclosure signals that warrant an information-boundary check."
    ),
    "multidimensional_diagnostic_question": (
        "How should the owner interpret the interaction among the distinct diagnostic dimensions indicated by this evidence?"
    ),
    "ambiguity": (
        "The evidence contains uncertainty or competing signals that leave the diagnostic reading open."
    ),
    "insufficient_evidence": (
        "The available evidence is too limited for a substantive diagnostic observation."
    ),
    "owner_review_question": (
        "Which diagnostic dimension should receive the owner's closest attention in this evidence?"
    ),
}


def _provenance() -> dict[str, object]:
    return {
        "tool_source": DRAMATICA_FLOW_INFORMED_RUBRIC_ID,
        "adapter": DRAMATICA_FLOW_INFORMED_RUBRIC_ID,
        "support": DRAMATICA_FLOW_INFORMED_RUBRIC_SUPPORT_LABEL,
        "executes_dramatica_flow": False,
        "official_dramatica_flow_output": False,
    }


def _safety() -> dict[str, bool]:
    return {flag: False for flag in OPERATION_FLAGS}


def _split_evidence_spans(source_text: str) -> list[str]:
    """Return ordered non-empty exact substrings split at punctuation/lines."""
    return [span for span in _SPAN_SPLIT_RE.split(source_text) if span and span.strip()]


def _match_text(span: str) -> str:
    return span.replace("\r\n", "\n").replace("\r", "\n")


def _signal_pair(text: str, first: re.Pattern[str], second: re.Pattern[str]) -> tuple[bool, bool]:
    return bool(first.search(text)), bool(second.search(text))


def _dimension_signals(span: str) -> dict[str, tuple[bool, bool]]:
    text = _match_text(span)
    return {
        "causal_chain_diagnostic": _signal_pair(text, _CAUSAL_CONNECTOR_RE, _CONSEQUENCE_RE),
        "narrative_commitment_lifecycle_diagnostic": _signal_pair(
            text, _COMMITMENT_OPEN_RE, _COMMITMENT_FOLLOW_THROUGH_RE
        ),
        "emotional_state_consistency": _signal_pair(text, _EMOTIONAL_STATE_RE, _EMOTIONAL_CHANGE_RE),
        "relationship_delta_diagnostic": _signal_pair(text, _RELATIONSHIP_ROLE_RE, _RELATIONSHIP_CHANGE_RE),
        "timeline_thread_activity_diagnostic": _signal_pair(text, _TEMPORAL_ORDER_RE, _THREAD_ACTIVITY_RE),
        "information_boundary_diagnostic": _signal_pair(text, _KNOWLEDGE_ACCESS_RE, _INFORMATION_TRANSFER_RE),
    }


def _qualifying_signal(category: str, span: str) -> tuple[bool, bool]:
    pair = _dimension_signals(span).get(category, (False, False))
    return any(pair), all(pair)


def _multidimensional(span: str) -> bool:
    return sum(any(pair) for pair in _dimension_signals(span).values()) >= 2


def _build_item(
    request: dict[str, Any], category: str, category_order: int, span: str,
    *, confidence: str, uncertainty: str,
) -> dict[str, object]:
    source_locator = request["source_locator"]
    return {
        "item_id": f"rubric_item_{category_order:02d}_{category}",
        "category": category,
        "candidate_type": CATEGORY_TO_CANDIDATE_TYPE[category],
        "label": _CATEGORY_LABELS[category],
        "diagnostic_text": _CATEGORY_DIAGNOSTIC_TEXT[category],
        "statement_kind": CATEGORY_TO_STATEMENT_KIND[category],
        "evidence": [{"source_excerpt": span, "source_locator": source_locator}],
        "source_locator": source_locator,
        "source_refs": list(request["source_refs"]),
        "evidence_refs": list(request["evidence_refs"]),
        "provenance_refs": list(request["provenance_refs"]),
        "source_locator_refs": list(request["source_locator_refs"]),
        "provenance": _provenance(),
        "support_label": DRAMATICA_FLOW_INFORMED_RUBRIC_SUPPORT_LABEL,
        "confidence": confidence,
        "uncertainty_label": uncertainty,
        "owner_decision": {"approved": False, "decision": "pending"},
        "review_status": "candidate_review_pending",
        "executes_dramatica_flow": False,
        "official_dramatica_flow_output": False,
        "calls_model_provider_server": False,
        "reads_external_source_runtime": False,
        "uses_external_project_state": False,
    }


def _empty_result(request: dict[str, Any]) -> dict[str, object]:
    return _result_envelope(request, status="empty")


def _result_envelope(request: dict[str, Any], *, status: str) -> dict[str, object]:
    return {
        "schema_version": DRAMATICA_FLOW_INFORMED_RUBRIC_RESULT_SCHEMA_VERSION,
        "rubric_id": DRAMATICA_FLOW_INFORMED_RUBRIC_ID,
        "output_class": DRAMATICA_FLOW_INFORMED_RUBRIC_OUTPUT_CLASS,
        "status": status,
        "display_label": DRAMATICA_FLOW_INFORMED_RUBRIC_SUPPORT_LABEL,
        "provenance": _provenance(),
        "source_refs": list(request["source_refs"]),
        "evidence_refs": list(request["evidence_refs"]),
        "provenance_refs": list(request["provenance_refs"]),
        "source_locator_refs": list(request["source_locator_refs"]),
        "candidate_support": [],
        "diagnostic_questions": [],
        "uncertainty_notes": [],
        "insufficient_evidence_notes": [],
        "safety": _safety(),
    }


def _bucket_for(category: str) -> str:
    if category in _QUESTION_CATEGORIES:
        return "diagnostic_questions"
    if category == "ambiguity":
        return "uncertainty_notes"
    if category == "insufficient_evidence":
        return "insufficient_evidence_notes"
    return "candidate_support"


def _evaluate_category(
    request: dict[str, Any], category: str, category_order: int, spans: list[str],
) -> dict[str, object] | None:
    if category == "insufficient_evidence":
        return None
    if category == "owner_review_question":
        return _build_item(
            request, category, category_order, spans[0],
            confidence="low_support", uncertainty="requires_owner_interpretation",
        )
    for span in spans:
        if category in _SUBSTANTIVE_CATEGORIES:
            qualifies, dual_signal = _qualifying_signal(category, span)
            if qualifies:
                conflicting = bool(_CONFLICTING_SIGNAL_RE.search(_match_text(span)))
                return _build_item(
                    request, category, category_order, span,
                    confidence="medium_support" if dual_signal else "low_support",
                    uncertainty="conflicting_support" if conflicting else "null",
                )
        elif category == "multidimensional_diagnostic_question" and _multidimensional(span):
            return _build_item(
                request, category, category_order, span,
                confidence="low_support", uncertainty="requires_owner_interpretation",
            )
        elif category == "ambiguity" and (
            _UNCERTAINTY_RE.search(_match_text(span))
            or _CONFLICTING_SIGNAL_RE.search(_match_text(span))
        ):
            return _build_item(
                request, category, category_order, span,
                confidence="low_support", uncertainty="ambiguity",
            )
    return None


def _construct_result(request: dict[str, Any]) -> dict[str, object]:
    spans = _split_evidence_spans(request["source_text"])
    result = _result_envelope(request, status="succeeded")
    fired_substantive = False
    category_orders = {
        category: order
        for order, category in enumerate(request["requested_categories"], start=1)
    }

    for category in request["requested_categories"]:
        item = _evaluate_category(request, category, category_orders[category], spans)
        if item is None:
            continue
        result[_bucket_for(category)].append(item)  # type: ignore[union-attr]
        if category in _SUBSTANTIVE_CATEGORIES:
            fired_substantive = True

    if "insufficient_evidence" in category_orders:
        materially_short = len(_WORD_RE.findall(request["source_text"])) < _MIN_MATERIAL_WORDS
        if materially_short or not fired_substantive:
            category = "insufficient_evidence"
            item = _build_item(
                request, category, category_orders[category], spans[0],
                confidence="low_support", uncertainty="insufficient_evidence",
            )
            result["insufficient_evidence_notes"].append(item)  # type: ignore[union-attr]

    buckets = (
        "candidate_support", "diagnostic_questions", "uncertainty_notes",
        "insufficient_evidence_notes",
    )
    if not any(result[bucket] for bucket in buckets):
        return _empty_result(request)
    return result


def evaluate_dramatica_flow_informed_analysis_rubric(
    request: object,
) -> dict[str, object]:
    """Validate, evaluate, validate again, and fail closed on every failure."""
    safe_request: dict[str, Any] | None = None
    try:
        if isinstance(request, dict):
            safe_request = copy.deepcopy(request)
        else:
            return build_dramatica_flow_informed_rubric_fail_closed_result(
                "request_validation_failed", request=None
            )

        request_validation = validate_dramatica_flow_informed_rubric_request(safe_request)
        if request_validation.get("status") != "valid":
            return build_dramatica_flow_informed_rubric_fail_closed_result(
                "request_validation_failed", request=safe_request
            )
        normalized_request = request_validation["normalized_request"]
        generated = _construct_result(normalized_request)
        result_validation = validate_dramatica_flow_informed_rubric_result(generated)
        if result_validation.get("status") != "valid":
            return build_dramatica_flow_informed_rubric_fail_closed_result(
                "result_validation_failed", request=normalized_request
            )
        return result_validation["normalized_result"]
    except Exception:
        return build_dramatica_flow_informed_rubric_fail_closed_result(
            "unexpected_evaluator_failure", request=safe_request
        )
