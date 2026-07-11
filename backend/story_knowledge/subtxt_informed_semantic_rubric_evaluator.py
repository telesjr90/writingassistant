"""PHASE8-IMPL-023-T019D — App-owned Subtxt-informed semantic-rubric evaluator.

This module implements a pure, local, deterministic, rule-assisted, in-memory
evaluator that consumes the committed T019C request contract and produces the
committed T019C result contract. It is not a live Subtxt integration. It never
reads or copies external Subtxt documentation, never executes or impersonates
Subtxt, never calls a model, never persists candidates or review-queue entries,
never mutates Memory/Canon, never creates promotion records, never runs
apply-promotion, and never generates story prose.

The evaluator is standard-library only. It uses only ``re`` and ``copy`` from
the Python standard library plus the T019C contract module it consumes. OMI
adapter integration is intentionally deferred to a later child task (T019E).

Boundary phrases: confidence/support is not truth; tool output is not canon;
tool output is not truth; no automatic Storyform; no automatic
Dramatica/Storyform truth; no official Subtxt output; no live Subtxt runtime;
no generated prose; no rewrite; no continuation; no outline; no candidate
persistence; no review-queue creation; no Memory/Canon mutation; no promotion
record; no apply-promotion; no training/model artifacts; fail closed; no
silent fallback; queue presence is not approval; candidate persistence is not
canon.

Public surface area is exactly:

* ``SUBTXT_INFORMED_RUBRIC_EVALUATOR_VERSION``
* ``evaluate_subtxt_informed_semantic_rubric(request)``

All other helpers in this module are private.
"""

from __future__ import annotations

import copy
import re
from typing import Any

from backend.story_knowledge.subtxt_informed_semantic_rubric_contract import (
    ALLOWED_OPERATION_FLAGS,
    CATEGORY_TO_CANDIDATE_TYPE,
    CATEGORY_TO_STATEMENT_KIND,
    SUBTXT_INFORMED_RUBRIC_ID,
    SUBTXT_INFORMED_RUBRIC_OUTPUT_CLASS,
    SUBTXT_INFORMED_RUBRIC_RESULT_SCHEMA_VERSION,
    SUBTXT_INFORMED_RUBRIC_SUPPORT_LABEL,
    build_subtxt_informed_rubric_fail_closed_result,
    validate_subtxt_informed_rubric_request,
    validate_subtxt_informed_rubric_result,
)


SUBTXT_INFORMED_RUBRIC_EVALUATOR_VERSION = (
    "app_owned_subtxt_informed_rubric_evaluator.v1"
)


# ---------------------------------------------------------------------------
# Cue vocabulary (original app-owned; includes simple morphological variants
# of the words listed in the T019D task brief so the rules are stable under
# ordinary owner-source phrasing). Do not read or import external cue lists.
# ---------------------------------------------------------------------------

_INTENTION_CUES: tuple[str, ...] = (
    "want", "wants", "wanted", "wanting",
    "need", "needs", "needed", "needing",
    "must",
    "seek", "seeks", "sought", "seeking",
    "try", "tries", "tried", "trying",
    "plan", "plans", "planned", "planning",
    "decide", "decides", "decided", "deciding", "decision", "decisions",
    "attempt", "attempts", "attempted", "attempting",
)

_RESISTANCE_CUES: tuple[str, ...] = (
    "but",
    "however",
    "unless",
    "until",
    "prevent", "prevents", "prevented", "preventing", "prevention",
    "block", "blocks", "blocked", "blocking",
    "risk", "risks", "risked", "risking",
    "fail", "fails", "failed", "failing", "failure",
    "because",
)

_OPPOSING_PRESSURE_CUES: tuple[str, ...] = _RESISTANCE_CUES + (
    "against",
    "versus",
    "refuse", "refuses", "refused", "refusing",
    "oppose", "opposes", "opposed", "opposing",
    "threaten", "threatens", "threatened", "threatening",
    "compete", "competes", "competed", "competing",
    "despite",
)

_PRONOUN_CUES: tuple[str, ...] = (
    "i", "me", "my", "mine", "myself",
    "we", "us", "our", "ours", "ourselves",
    "he", "she", "him", "her", "his", "hers", "himself", "herself",
    "they", "them", "their", "theirs", "themselves",
    "it", "its", "itself",
)

_RELATIONSHIP_CUES: tuple[str, ...] = (
    "mentor", "rival", "partner", "parent", "child", "friend", "team",
)

_TEMPORAL_CHANGE_CUES: tuple[str, ...] = (
    "before", "after", "then", "when", "until", "later",
    "changes", "decides", "discovers", "reveals", "returns",
)

_CAUSAL_SINGLE_CUES: tuple[str, ...] = (
    "because", "therefore", "causes", "forces",
)

_CAUSAL_MULTI_CUES: tuple[str, ...] = (
    "leads to", "results in",
)

_UNCERTAINTY_CUES: tuple[str, ...] = (
    "maybe", "perhaps", "might", "could",
    "seems", "appears", "unclear", "unknown", "possibly",
)

_UNCERTAINTY_MULTI_CUES: tuple[str, ...] = (
    "not sure",
)


# ---------------------------------------------------------------------------
# Cue regexes (all case-insensitive; multi-word cues matched as full phrases).
# ---------------------------------------------------------------------------


def _build_single_word_regex(cues: tuple[str, ...]) -> re.Pattern[str]:
    parts = [r"\b" + re.escape(c) for c in cues]
    return re.compile("|".join(parts), re.IGNORECASE)


def _build_multi_word_regex(cues: tuple[str, ...]) -> re.Pattern[str]:
    parts = [re.escape(c) for c in cues]
    return re.compile("|".join(parts), re.IGNORECASE)


def _build_causal_regex() -> re.Pattern[str]:
    parts = [r"\b" + re.escape(c) for c in _CAUSAL_SINGLE_CUES]
    parts.extend(re.escape(c) for c in _CAUSAL_MULTI_CUES)
    return re.compile("|".join(parts), re.IGNORECASE)


def _build_uncertainty_regex() -> re.Pattern[str]:
    parts = [r"\b" + re.escape(c) for c in _UNCERTAINTY_CUES]
    parts.extend(re.escape(c) for c in _UNCERTAINTY_MULTI_CUES)
    return re.compile("|".join(parts), re.IGNORECASE)


_INTENTION_RE: re.Pattern[str] = _build_single_word_regex(_INTENTION_CUES)
_RESISTANCE_RE: re.Pattern[str] = _build_single_word_regex(_RESISTANCE_CUES)
_OPPOSING_PRESSURE_RE: re.Pattern[str] = _build_single_word_regex(
    _OPPOSING_PRESSURE_CUES
)
_PRONOUN_RE: re.Pattern[str] = _build_single_word_regex(_PRONOUN_CUES)
_RELATIONSHIP_RE: re.Pattern[str] = _build_single_word_regex(_RELATIONSHIP_CUES)
_TEMPORAL_RE: re.Pattern[str] = _build_single_word_regex(_TEMPORAL_CHANGE_CUES)
_CAUSAL_RE: re.Pattern[str] = _build_causal_regex()
_UNCERTAINTY_RE: re.Pattern[str] = _build_uncertainty_regex()
_NAME_TOKEN_RE: re.Pattern[str] = re.compile(r"\b[A-Z][a-z]{1,}\b")
_WORD_TOKEN_RE: re.Pattern[str] = re.compile(r"\b\w+\b")
_SENTENCE_OR_LINE_SPLIT_RE: re.Pattern[str] = re.compile(
    r"(?<=[.!?])\s+|\n+"
)


# ---------------------------------------------------------------------------
# Deterministic per-category item IDs.
# ---------------------------------------------------------------------------

_CATEGORY_TO_ITEM_NUMBER: dict[str, int] = {
    "structural_diagnostic": 1,
    "conflict_diagnostic": 2,
    "throughline_context_question": 3,
    "story_point_context_question": 4,
    "source_of_conflict_hypothesis": 5,
    "subject_vs_conflict_question": 6,
    "ambiguity": 7,
    "insufficient_evidence": 8,
    "owner_review_question": 9,
}


# ---------------------------------------------------------------------------
# Fixed app-owned diagnostic text and labels per category. Diagnostic text
# must NEVER be derived from the owner-provided source.
# ---------------------------------------------------------------------------

_CATEGORY_LABELS: dict[str, str] = {
    "structural_diagnostic": "Intention and resistance signal",
    "conflict_diagnostic": "Opposing pressure signal",
    "throughline_context_question": "Throughline perspective question",
    "story_point_context_question": "Story-point context question",
    "source_of_conflict_hypothesis": "Possible resistance mechanism",
    "subject_vs_conflict_question": "Subject versus conflict question",
    "ambiguity": "Uncertain structural reading",
    "insufficient_evidence": "Limited diagnostic support",
    "owner_review_question": "Owner review question",
}

_CATEGORY_DIAGNOSTIC_TEXT: dict[str, str] = {
    "structural_diagnostic": (
        "The evidence contains an intention paired with resistance or "
        "consequence and may support structural review."
    ),
    "conflict_diagnostic": (
        "The evidence contains opposing pressures that may support "
        "conflict-focused review."
    ),
    "throughline_context_question": (
        "Which perspective should the owner use when reviewing the goal "
        "and resistance signals in this evidence?"
    ),
    "story_point_context_question": (
        "Which structural context best describes the change indicated by "
        "this evidence?"
    ),
    "source_of_conflict_hypothesis": (
        "A causal cue and a resistance cue occur in the same evidence "
        "span and may support a mechanism hypothesis."
    ),
    "subject_vs_conflict_question": (
        "Does the highlighted subject actively create resistance, or is "
        "it only the topic being described?"
    ),
    "ambiguity": (
        "The evidence uses uncertainty language that leaves the "
        "structural reading open."
    ),
    "insufficient_evidence": (
        "The available evidence does not contain enough explicit support "
        "for a stronger diagnostic observation."
    ),
    "owner_review_question": (
        "What additional owner-provided context would clarify the "
        "structural reading of this evidence?"
    ),
}


# ---------------------------------------------------------------------------
# Small private helpers.
# ---------------------------------------------------------------------------


def _safe_provenance_dict() -> dict[str, Any]:
    return {
        "tool_source": SUBTXT_INFORMED_RUBRIC_ID,
        "adapter": SUBTXT_INFORMED_RUBRIC_ID,
        "support": SUBTXT_INFORMED_RUBRIC_SUPPORT_LABEL,
        "executes_subtxt": False,
        "official_subtxt_output": False,
    }


def _safe_safety_dict() -> dict[str, bool]:
    return {key: False for key in ALLOWED_OPERATION_FLAGS}


def _split_into_evidence_spans(source_text: str) -> list[str]:
    """Split the owner-provided source into ordered non-empty evidence spans.

    The original ``source_text`` is used unchanged so that each evidence span
    remains an exact substring of the owner-provided source. Whitespace-only
    spans are removed. Line-ending normalization is applied separately to a
    local copy of the text used only for cue matching.
    """
    if not isinstance(source_text, str) or not source_text:
        return []
    raw_spans = _SENTENCE_OR_LINE_SPLIT_RE.split(source_text)
    return [span for span in raw_spans if span and span.strip()]


def _span_for_cue_matching(span: str) -> str:
    """Return a line-ending-normalized copy of the span for cue matching only.

    The original span is still used as the evidence excerpt.
    """
    return span.replace("\r\n", "\n").replace("\r", "\n")


def _source_word_token_count(source_text: str) -> int:
    return len(_WORD_TOKEN_RE.findall(source_text or ""))


def _span_has_pronoun(span: str) -> bool:
    return bool(_PRONOUN_RE.search(_span_for_cue_matching(span)))


def _span_distinct_name_tokens(span: str) -> set[str]:
    return set(_NAME_TOKEN_RE.findall(span))


def _span_has_relationship_cue(span: str) -> bool:
    return bool(_RELATIONSHIP_RE.search(_span_for_cue_matching(span)))


def _count_distinct_actor_signal_categories(span: str) -> int:
    """Count distinct actor-signal categories present in the span.

    A span triggers throughline-style perspective questions when it carries
    at least two distinct actor-signal categories out of: pronoun presence,
    two or more distinct capitalized name-like tokens, and a relationship cue.
    """
    categories = 0
    if _span_has_pronoun(span):
        categories += 1
    if len(_span_distinct_name_tokens(span)) >= 2:
        categories += 1
    if _span_has_relationship_cue(span):
        categories += 1
    return categories


def _span_has_actor_signal(span: str) -> bool:
    """Return True if the span contains any actor/topic signal."""
    if _span_has_pronoun(span):
        return True
    if _span_distinct_name_tokens(span):
        return True
    return False


def _evidence_pair(span: str, source_locator: str) -> list[dict[str, str]]:
    return [
        {
            "source_excerpt": span,
            "source_locator": source_locator,
        }
    ]


def _build_item(
    *,
    item_id: str,
    category: str,
    span: str,
    source_locator: str,
    confidence: str,
    uncertainty_label: str,
    statement_kind: str,
    source_refs: list[str],
    evidence_refs: list[str],
    provenance_refs: list[str],
    source_locator_refs: list[str],
) -> dict[str, Any]:
    return {
        "item_id": item_id,
        "category": category,
        "candidate_type": CATEGORY_TO_CANDIDATE_TYPE[category],
        "label": _CATEGORY_LABELS[category],
        "diagnostic_text": _CATEGORY_DIAGNOSTIC_TEXT[category],
        "statement_kind": statement_kind,
        "evidence": _evidence_pair(span, source_locator),
        "source_locator": source_locator,
        "source_refs": list(source_refs),
        "evidence_refs": list(evidence_refs),
        "provenance_refs": list(provenance_refs),
        "source_locator_refs": list(source_locator_refs),
        "provenance": _safe_provenance_dict(),
        "support_label": SUBTXT_INFORMED_RUBRIC_SUPPORT_LABEL,
        "confidence": confidence,
        "uncertainty_label": uncertainty_label,
        "owner_decision": {"approved": False, "decision": "pending"},
        "review_status": "candidate_review_pending",
        "executes_subtxt": False,
        "official_subtxt_output": False,
    }


def _make_item_id(category: str) -> str:
    number = _CATEGORY_TO_ITEM_NUMBER.get(category, 0)
    return f"rubric_item_{number:02d}_{category}"


# ---------------------------------------------------------------------------
# Per-category rule evaluation against a single evidence span. Returns a
# fully-shaped item dict when the rule fires, else ``None``. The
# ``insufficient_evidence`` rule is decided at the orchestrator level, not
# per-span, so its branch always returns ``None`` here.
# ---------------------------------------------------------------------------


def _evaluate_span_for_category(
    category: str,
    span: str,
    *,
    source_locator: str,
    source_refs: list[str],
    evidence_refs: list[str],
    provenance_refs: list[str],
    source_locator_refs: list[str],
) -> dict[str, Any] | None:
    text = _span_for_cue_matching(span)

    if category == "structural_diagnostic":
        has_intention = bool(_INTENTION_RE.search(text))
        has_resistance = bool(_RESISTANCE_RE.search(text))
        if not (has_intention and has_resistance):
            return None
        return _build_item(
            item_id=_make_item_id(category),
            category=category,
            span=span,
            source_locator=source_locator,
            confidence="medium_support",
            uncertainty_label="null",
            statement_kind="candidate_observation",
            source_refs=source_refs,
            evidence_refs=evidence_refs,
            provenance_refs=provenance_refs,
            source_locator_refs=source_locator_refs,
        )

    if category == "conflict_diagnostic":
        if not _OPPOSING_PRESSURE_RE.search(text):
            return None
        return _build_item(
            item_id=_make_item_id(category),
            category=category,
            span=span,
            source_locator=source_locator,
            confidence="low_support",
            uncertainty_label="null",
            statement_kind="candidate_observation",
            source_refs=source_refs,
            evidence_refs=evidence_refs,
            provenance_refs=provenance_refs,
            source_locator_refs=source_locator_refs,
        )

    if category == "throughline_context_question":
        if _count_distinct_actor_signal_categories(span) < 2:
            return None
        return _build_item(
            item_id=_make_item_id(category),
            category=category,
            span=span,
            source_locator=source_locator,
            confidence="low_support",
            uncertainty_label="requires_owner_interpretation",
            statement_kind="question",
            source_refs=source_refs,
            evidence_refs=evidence_refs,
            provenance_refs=provenance_refs,
            source_locator_refs=source_locator_refs,
        )

    if category == "story_point_context_question":
        if not _TEMPORAL_RE.search(text):
            return None
        return _build_item(
            item_id=_make_item_id(category),
            category=category,
            span=span,
            source_locator=source_locator,
            confidence="low_support",
            uncertainty_label="requires_owner_interpretation",
            statement_kind="question",
            source_refs=source_refs,
            evidence_refs=evidence_refs,
            provenance_refs=provenance_refs,
            source_locator_refs=source_locator_refs,
        )

    if category == "source_of_conflict_hypothesis":
        has_causal = bool(_CAUSAL_RE.search(text))
        has_resistance = bool(_RESISTANCE_RE.search(text))
        if not (has_causal and has_resistance):
            return None
        return _build_item(
            item_id=_make_item_id(category),
            category=category,
            span=span,
            source_locator=source_locator,
            confidence="medium_support",
            uncertainty_label="requires_owner_interpretation",
            statement_kind="hypothesis",
            source_refs=source_refs,
            evidence_refs=evidence_refs,
            provenance_refs=provenance_refs,
            source_locator_refs=source_locator_refs,
        )

    if category == "subject_vs_conflict_question":
        if not _span_has_actor_signal(span):
            return None
        if _OPPOSING_PRESSURE_RE.search(text):
            return None
        return _build_item(
            item_id=_make_item_id(category),
            category=category,
            span=span,
            source_locator=source_locator,
            confidence="low_support",
            uncertainty_label="requires_owner_interpretation",
            statement_kind="question",
            source_refs=source_refs,
            evidence_refs=evidence_refs,
            provenance_refs=provenance_refs,
            source_locator_refs=source_locator_refs,
        )

    if category == "ambiguity":
        if not _UNCERTAINTY_RE.search(text):
            return None
        return _build_item(
            item_id=_make_item_id(category),
            category=category,
            span=span,
            source_locator=source_locator,
            confidence="low_support",
            uncertainty_label="ambiguity",
            statement_kind="ambiguity",
            source_refs=source_refs,
            evidence_refs=evidence_refs,
            provenance_refs=provenance_refs,
            source_locator_refs=source_locator_refs,
        )

    if category == "insufficient_evidence":
        # Decided at the orchestrator level; never fires per-span.
        return None

    if category == "owner_review_question":
        return _build_item(
            item_id=_make_item_id(category),
            category=category,
            span=span,
            source_locator=source_locator,
            confidence="low_support",
            uncertainty_label="requires_owner_interpretation",
            statement_kind="question",
            source_refs=source_refs,
            evidence_refs=evidence_refs,
            provenance_refs=provenance_refs,
            source_locator_refs=source_locator_refs,
        )

    return None


# ---------------------------------------------------------------------------
# Orchestrator-level helpers.
# ---------------------------------------------------------------------------


def _requested_categories(request: dict[str, Any]) -> list[str]:
    categories = request.get("requested_categories") or []
    if not isinstance(categories, list):
        return []
    return [
        category
        for category in categories
        if isinstance(category, str) and category
    ]


def _copy_top_level_refs(request: dict[str, Any]) -> dict[str, list[str]]:
    return {
        "source_refs": list(request.get("source_refs") or []),
        "evidence_refs": list(request.get("evidence_refs") or []),
        "provenance_refs": list(request.get("provenance_refs") or []),
        "source_locator_refs": list(request.get("source_locator_refs") or []),
    }


def _is_substantive_non_question_category(category: str) -> bool:
    return category in {
        "structural_diagnostic",
        "conflict_diagnostic",
        "source_of_conflict_hypothesis",
        "ambiguity",
    }


def _build_empty_result(
    request: dict[str, Any],
) -> dict[str, Any]:
    refs = _copy_top_level_refs(request)
    return {
        "schema_version": SUBTXT_INFORMED_RUBRIC_RESULT_SCHEMA_VERSION,
        "rubric_id": SUBTXT_INFORMED_RUBRIC_ID,
        "output_class": SUBTXT_INFORMED_RUBRIC_OUTPUT_CLASS,
        "status": "empty",
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
    }


def _build_succeeded_result(
    request: dict[str, Any],
    *,
    candidate_support: list[dict[str, Any]],
    diagnostic_questions: list[dict[str, Any]],
) -> dict[str, Any]:
    refs = _copy_top_level_refs(request)
    return {
        "schema_version": SUBTXT_INFORMED_RUBRIC_RESULT_SCHEMA_VERSION,
        "rubric_id": SUBTXT_INFORMED_RUBRIC_ID,
        "output_class": SUBTXT_INFORMED_RUBRIC_OUTPUT_CLASS,
        "status": "succeeded",
        "display_label": SUBTXT_INFORMED_RUBRIC_SUPPORT_LABEL,
        "provenance": _safe_provenance_dict(),
        "source_refs": refs["source_refs"],
        "evidence_refs": refs["evidence_refs"],
        "provenance_refs": refs["provenance_refs"],
        "source_locator_refs": refs["source_locator_refs"],
        "candidate_support": candidate_support,
        "diagnostic_questions": diagnostic_questions,
        "uncertainty_notes": [],
        "insufficient_evidence_notes": [],
        "safety": _safe_safety_dict(),
    }


# ---------------------------------------------------------------------------
# Public evaluator API.
# ---------------------------------------------------------------------------


def evaluate_subtxt_informed_semantic_rubric(
    request: object,
) -> dict[str, Any]:
    """Evaluate a T019C request and return a T019C result envelope.

    The flow is:

    1. ``validate_subtxt_informed_rubric_request`` is called on a deep copy
       of the supplied request. The original caller's data is never mutated.
    2. On request validation failure, a fail-closed result is returned
       through ``build_subtxt_informed_rubric_fail_closed_result``.
    3. On a valid request, the evaluator walks ``requested_categories`` in
       request order, scans the source in order, and emits at most one item
       per category using original app-owned cue rules.
    4. The produced result is validated through
       ``validate_subtxt_informed_rubric_result``. On any validation failure
       a fail-closed result is returned with the deterministic reason
       ``result_validation_failed``.
    5. Any unexpected internal exception is caught and converted into a
       fail-closed result with the deterministic reason
       ``unexpected_evaluator_failure``.
    """
    safe_request: dict[str, Any] | None = (
        copy.deepcopy(request) if isinstance(request, dict) else None
    )

    try:
        if safe_request is None:
            return build_subtxt_informed_rubric_fail_closed_result(
                "request_validation_failed",
                request=None,
            )

        request_validation = validate_subtxt_informed_rubric_request(
            safe_request
        )
        if request_validation.get("status") != "valid":
            return build_subtxt_informed_rubric_fail_closed_result(
                "request_validation_failed",
                request=safe_request,
            )

        normalized_request: dict[str, Any] = request_validation.get(
            "normalized_request", safe_request
        )

        source_text: str = normalized_request.get("source_text", "") or ""
        source_locator: str = (
            normalized_request.get("source_locator", "") or ""
        )

        refs = _copy_top_level_refs(normalized_request)
        source_refs = refs["source_refs"]
        evidence_refs = refs["evidence_refs"]
        provenance_refs = refs["provenance_refs"]
        source_locator_refs = refs["source_locator_refs"]

        spans = _split_into_evidence_spans(source_text)
        word_count = _source_word_token_count(source_text)

        requested = _requested_categories(normalized_request)

        candidate_support: list[dict[str, Any]] = []
        diagnostic_questions: list[dict[str, Any]] = []
        substantive_non_question_fired = False

        for category in requested:
            if category == "insufficient_evidence":
                # Defer to the orchestrator pass below; do not scan spans.
                continue

            fired_item: dict[str, Any] | None = None
            for span in spans:
                fired_item = _evaluate_span_for_category(
                    category,
                    span,
                    source_locator=source_locator,
                    source_refs=source_refs,
                    evidence_refs=evidence_refs,
                    provenance_refs=provenance_refs,
                    source_locator_refs=source_locator_refs,
                )
                if fired_item is not None:
                    break

            if fired_item is None:
                continue

            if _is_substantive_non_question_category(category):
                substantive_non_question_fired = True

            if category in {
                "throughline_context_question",
                "story_point_context_question",
                "subject_vs_conflict_question",
                "owner_review_question",
            }:
                diagnostic_questions.append(fired_item)
            else:
                candidate_support.append(fired_item)

        if "insufficient_evidence" in requested:
            short_input = word_count < 12
            no_substantive = not substantive_non_question_fired
            if short_input or no_substantive:
                first_span = spans[0] if spans else source_text
                insufficient_item = _build_item(
                    item_id=_make_item_id("insufficient_evidence"),
                    category="insufficient_evidence",
                    span=first_span,
                    source_locator=source_locator,
                    confidence="low_support",
                    uncertainty_label="insufficient_evidence",
                    statement_kind="insufficient_evidence",
                    source_refs=source_refs,
                    evidence_refs=evidence_refs,
                    provenance_refs=provenance_refs,
                    source_locator_refs=source_locator_refs,
                )
                candidate_support.append(insufficient_item)

        if not candidate_support and not diagnostic_questions:
            result = _build_empty_result(normalized_request)
        else:
            result = _build_succeeded_result(
                normalized_request,
                candidate_support=candidate_support,
                diagnostic_questions=diagnostic_questions,
            )

        result_validation = validate_subtxt_informed_rubric_result(result)
        if result_validation.get("status") != "valid":
            return build_subtxt_informed_rubric_fail_closed_result(
                "result_validation_failed",
                request=normalized_request,
            )

        return result_validation["normalized_result"]
    except Exception:
        return build_subtxt_informed_rubric_fail_closed_result(
            "unexpected_evaluator_failure",
            request=safe_request,
        )
