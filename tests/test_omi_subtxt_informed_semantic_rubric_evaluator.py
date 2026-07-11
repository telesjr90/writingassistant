"""PHASE8-IMPL-023-T019D app-owned Subtxt-informed semantic-rubric evaluator tests.

These tests cover the pure, in-memory, deterministic/rule-assisted evaluator
that consumes the T019C request contract and produces the T019C result
contract. They never execute Subtxt, never read or import
``.external_sources``, never call a model, never persist candidates, never
mutate projects, Memory, or Canon, and never read real project files. The
tests use only the evaluator module, the T019C contract module, and
synthetic in-memory dictionaries.

Boundary phrases: confidence/support is not truth; tool output is not
canon; tool output is not truth; no automatic Storyform; no automatic
Dramatica/Storyform truth; no official Subtxt output; no live Subtxt
runtime; no generated prose; no rewrite; no continuation; no outline;
no candidate persistence; no review-queue creation; no Memory/Canon
mutation; no promotion record; no apply-promotion; no training/model
artifacts; fail closed; no silent fallback; queue presence is not
approval; candidate persistence is not canon.
"""

from __future__ import annotations

import copy
import re
import subprocess
import socket
import sys
from pathlib import Path
from typing import Any

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from backend.story_knowledge import (
    subtxt_informed_semantic_rubric_contract as sisc,
)
from backend.story_knowledge import (
    subtxt_informed_semantic_rubric_evaluator as sise,
)
from backend.story_knowledge import (
    analysis_runtime_integration as ari,
)


# ---------------------------------------------------------------------------
# Valid request fixture
# ---------------------------------------------------------------------------


def _valid_safety_confirmations() -> dict[str, bool]:
    return {
        "no_subtxt_execution": True,
        "no_official_subtxt_output_claim": True,
        "no_storyform_truth": True,
        "no_generated_prose": True,
        "no_rewrite": True,
        "no_continuation": True,
        "no_outline": True,
        "no_candidate_persistence": True,
        "no_review_queue_creation": True,
        "no_memory_canon_mutation": True,
        "no_promotion_record": True,
        "no_apply_promotion": True,
        "no_training_artifacts": True,
    }


def _valid_request(**overrides: Any) -> dict[str, Any]:
    request: dict[str, Any] = {
        "schema_version": sisc.SUBTXT_INFORMED_RUBRIC_REQUEST_SCHEMA_VERSION,
        "rubric_id": sisc.SUBTXT_INFORMED_RUBRIC_ID,
        "request_id": "request-001",
        "project_name": "example_project",
        "source_text": (
            "Mara wants to find the archive key, but a rival threatens to "
            "block her path. The mentor decides to help Mara. Later Mara "
            "discovers that the key is hidden in the tower."
        ),
        "source_locator": "source_locator_ref_owner_scene_001",
        "source_refs": ["source_ref_owner_scene_001"],
        "evidence_refs": ["evidence_ref_scene_001_span_001"],
        "provenance_refs": ["provenance_ref_rubric_001"],
        "source_locator_refs": [
            "source_locator_ref_owner_scene_001",
            "source_locator_ref_owner_scene_002",
        ],
        "requested_categories": [
            "structural_diagnostic",
            "conflict_diagnostic",
            "throughline_context_question",
            "story_point_context_question",
            "source_of_conflict_hypothesis",
            "subject_vs_conflict_question",
            "ambiguity",
            "insufficient_evidence",
            "owner_review_question",
        ],
        "analysis_intent": "diagnostic_support",
        "owner_authored_or_owner_provided_source": True,
        "safety_confirmations": _valid_safety_confirmations(),
    }
    request.update(overrides)
    return request


# ---------------------------------------------------------------------------
# 1. Public version and single public evaluator API
# ---------------------------------------------------------------------------


def test_evaluator_version_constant_is_exact():
    assert sise.SUBTXT_INFORMED_RUBRIC_EVALUATOR_VERSION == (
        "app_owned_subtxt_informed_rubric_evaluator.v1"
    )


def test_evaluator_exposes_exactly_one_public_evaluator_function():
    public_callables = [
        name
        for name in dir(sise)
        if not name.startswith("_")
        and callable(getattr(sise, name))
        and getattr(getattr(sise, name), "__module__", None)
        == sise.__name__
    ]
    assert "evaluate_subtxt_informed_semantic_rubric" in public_callables
    assert public_callables == ["evaluate_subtxt_informed_semantic_rubric"]


def test_evaluator_function_is_callable_with_object_request():
    result = sise.evaluate_subtxt_informed_semantic_rubric(_valid_request())
    assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# 2. Valid request produces a valid T019C result
# ---------------------------------------------------------------------------


def test_valid_request_produces_valid_t019c_result():
    result = sise.evaluate_subtxt_informed_semantic_rubric(_valid_request())
    response = sisc.validate_subtxt_informed_rubric_result(result)
    assert response["status"] == "valid", response["errors"]
    assert response["valid"] is True


def test_valid_request_result_status_is_succeeded_when_items_emitted():
    result = sise.evaluate_subtxt_informed_semantic_rubric(_valid_request())
    assert result["status"] == "succeeded"
    assert (result["candidate_support"] or result["diagnostic_questions"])


def test_valid_request_result_envelope_fields_match_t019c_contract():
    result = sise.evaluate_subtxt_informed_semantic_rubric(_valid_request())
    assert (
        result["schema_version"]
        == sisc.SUBTXT_INFORMED_RUBRIC_RESULT_SCHEMA_VERSION
    )
    assert result["rubric_id"] == sisc.SUBTXT_INFORMED_RUBRIC_ID
    assert result["output_class"] == sisc.SUBTXT_INFORMED_RUBRIC_OUTPUT_CLASS
    assert (
        result["display_label"]
        == sisc.SUBTXT_INFORMED_RUBRIC_SUPPORT_LABEL
    )


# ---------------------------------------------------------------------------
# 3. Invalid request returns fail-closed result
# ---------------------------------------------------------------------------


def test_invalid_request_returns_fail_closed_result():
    bad = {"not": "a valid request"}
    result = sise.evaluate_subtxt_informed_semantic_rubric(bad)
    assert isinstance(result, dict)
    assert result["status"] == "failed_closed"
    assert result["candidate_support"] == []
    assert result["diagnostic_questions"] == []
    assert result["fail_closed_reason"] == "request_validation_failed"


def test_non_dict_request_returns_fail_closed_result():
    result = sise.evaluate_subtxt_informed_semantic_rubric("not a dict")
    assert isinstance(result, dict)
    assert result["status"] == "failed_closed"
    assert result["fail_closed_reason"] == "request_validation_failed"


def test_invalid_request_result_passes_t019c_validator():
    bad: dict = {
        "source_refs": ["source_ref_owner_scene_001"],
        "evidence_refs": ["evidence_ref_scene_001_span_001"],
        "provenance_refs": ["provenance_ref_rubric_001"],
        "source_locator_refs": ["source_locator_ref_owner_scene_001"],
    }
    result = sise.evaluate_subtxt_informed_semantic_rubric(bad)
    response = sisc.validate_subtxt_informed_rubric_result(result)
    assert response["status"] == "valid", response["errors"]


# ---------------------------------------------------------------------------
# 4. Caller request is not mutated
# ---------------------------------------------------------------------------


def test_caller_request_is_not_mutated_on_valid_request():
    req = _valid_request()
    snapshot = copy.deepcopy(req)
    sise.evaluate_subtxt_informed_semantic_rubric(req)
    assert req == snapshot


def test_caller_request_is_not_mutated_on_invalid_request():
    req: dict[str, Any] = {"not": "a valid request"}
    snapshot = copy.deepcopy(req)
    sise.evaluate_subtxt_informed_semantic_rubric(req)
    assert req == snapshot


# ---------------------------------------------------------------------------
# 5. Repeated evaluation is deterministic
# ---------------------------------------------------------------------------


def test_repeated_evaluation_produces_equal_results():
    req = _valid_request()
    first = sise.evaluate_subtxt_informed_semantic_rubric(copy.deepcopy(req))
    second = sise.evaluate_subtxt_informed_semantic_rubric(copy.deepcopy(req))
    assert first == second


def test_repeated_evaluation_with_short_input_is_deterministic():
    req = _valid_request(
        source_text="too short",
        requested_categories=[
            "insufficient_evidence",
            "owner_review_question",
        ],
    )
    first = sise.evaluate_subtxt_informed_semantic_rubric(copy.deepcopy(req))
    second = sise.evaluate_subtxt_informed_semantic_rubric(copy.deepcopy(req))
    assert first == second


# ---------------------------------------------------------------------------
# 6. Category order follows requested order
# ---------------------------------------------------------------------------


def test_category_order_follows_requested_order_for_questions():
    req = _valid_request(
        source_text=(
            "Before, Mara and Jonah argued, and later Mara decided to leave. "
            "When Mara discovers the truth, the mentor warns her."
        ),
        requested_categories=[
            "story_point_context_question",
            "throughline_context_question",
            "owner_review_question",
        ],
    )
    result = sise.evaluate_subtxt_informed_semantic_rubric(req)
    questions = result["diagnostic_questions"]
    assert [q["category"] for q in questions] == [
        "story_point_context_question",
        "throughline_context_question",
        "owner_review_question",
    ]


def test_category_order_follows_requested_order_for_observations_and_questions():
    req = _valid_request(
        source_text=(
            "Mara wants the key, but the rival blocks her. Mara and Jonah "
            "discover the truth later. The mentor decides to help."
        ),
        requested_categories=[
            "structural_diagnostic",
            "conflict_diagnostic",
            "throughline_context_question",
            "owner_review_question",
        ],
    )
    result = sise.evaluate_subtxt_informed_semantic_rubric(req)
    all_categories = [
        item["category"] for item in result["candidate_support"]
    ] + [
        item["category"] for item in result["diagnostic_questions"]
    ]
    assert all_categories == [
        "structural_diagnostic",
        "conflict_diagnostic",
        "throughline_context_question",
        "owner_review_question",
    ]


# ---------------------------------------------------------------------------
# 7. At most one item per category
# ---------------------------------------------------------------------------


def test_at_most_one_item_per_category_in_candidate_support():
    req = _valid_request(
        source_text=(
            "Mara wants the key, but the rival blocks her. Mara wants help, "
            "but the mentor is away. The key matters, but Mara must wait."
        ),
    )
    result = sise.evaluate_subtxt_informed_semantic_rubric(req)
    for category in sisc.NON_QUESTION_CATEGORIES:
        emitted = [
            item
            for item in result["candidate_support"]
            if item["category"] == category
        ]
        assert len(emitted) <= 1


def test_at_most_one_item_per_category_in_diagnostic_questions():
    req = _valid_request(
        source_text=(
            "Mara and Jonah later decide to leave, then Mara discovers the "
            "truth, and then the mentor changes plans."
        ),
    )
    result = sise.evaluate_subtxt_informed_semantic_rubric(req)
    for category in sisc.QUESTION_CATEGORIES:
        emitted = [
            item
            for item in result["diagnostic_questions"]
            if item["category"] == category
        ]
        assert len(emitted) <= 1


# ---------------------------------------------------------------------------
# 8. Each of the nine categories triggers independently
# ---------------------------------------------------------------------------


def test_structural_diagnostic_triggers_on_intention_and_resistance():
    req = _valid_request(
        source_text="Mara wants the key, but the rival blocks her path.",
        requested_categories=["structural_diagnostic", "owner_review_question"],
    )
    result = sise.evaluate_subtxt_informed_semantic_rubric(req)
    assert any(
        item["category"] == "structural_diagnostic"
        for item in result["candidate_support"]
    )


def test_conflict_diagnostic_triggers_on_opposing_pressure():
    req = _valid_request(
        source_text="Mara versus the rival. The rival opposes Mara.",
        requested_categories=["conflict_diagnostic", "owner_review_question"],
    )
    result = sise.evaluate_subtxt_informed_semantic_rubric(req)
    assert any(
        item["category"] == "conflict_diagnostic"
        for item in result["candidate_support"]
    )


def test_throughline_context_question_triggers_on_two_actor_signals():
    req = _valid_request(
        source_text=(
            "Mara and Jonah discuss the archive key. The mentor and the "
            "rival both watch from the doorway."
        ),
        requested_categories=[
            "throughline_context_question",
            "owner_review_question",
        ],
    )
    result = sise.evaluate_subtxt_informed_semantic_rubric(req)
    assert any(
        item["category"] == "throughline_context_question"
        for item in result["diagnostic_questions"]
    )


def test_story_point_context_question_triggers_on_temporal_cue():
    req = _valid_request(
        source_text="Before the storm, Mara decides to leave.",
        requested_categories=[
            "story_point_context_question",
            "owner_review_question",
        ],
    )
    result = sise.evaluate_subtxt_informed_semantic_rubric(req)
    assert any(
        item["category"] == "story_point_context_question"
        for item in result["diagnostic_questions"]
    )


def test_source_of_conflict_hypothesis_triggers_on_causal_and_resistance():
    req = _valid_request(
        source_text=(
            "Mara wants the key, because the rival blocks her path and "
            "therefore the archive stays closed."
        ),
        requested_categories=[
            "source_of_conflict_hypothesis",
            "owner_review_question",
        ],
    )
    result = sise.evaluate_subtxt_informed_semantic_rubric(req)
    assert any(
        item["category"] == "source_of_conflict_hypothesis"
        for item in result["candidate_support"]
    )


def test_subject_vs_conflict_question_triggers_on_actor_without_pressure():
    req = _valid_request(
        source_text="Mara mentions the key in passing.",
        requested_categories=[
            "subject_vs_conflict_question",
            "owner_review_question",
        ],
    )
    result = sise.evaluate_subtxt_informed_semantic_rubric(req)
    assert any(
        item["category"] == "subject_vs_conflict_question"
        for item in result["diagnostic_questions"]
    )


def test_ambiguity_triggers_on_uncertainty_cue():
    req = _valid_request(
        source_text="Maybe Mara could find the key, perhaps later.",
        requested_categories=["ambiguity", "owner_review_question"],
    )
    result = sise.evaluate_subtxt_informed_semantic_rubric(req)
    assert any(
        item["category"] == "ambiguity"
        for item in result["candidate_support"]
    )


def test_insufficient_evidence_triggers_on_short_input():
    req = _valid_request(
        source_text="Short text.",
        requested_categories=[
            "insufficient_evidence",
            "owner_review_question",
        ],
    )
    result = sise.evaluate_subtxt_informed_semantic_rubric(req)
    assert any(
        item["category"] == "insufficient_evidence"
        for item in result["candidate_support"]
    )


def test_owner_review_question_always_emits_for_valid_non_empty_source():
    req = _valid_request(
        source_text=(
            "Mara wants the key, but the rival blocks her."
        ),
        requested_categories=["owner_review_question"],
    )
    result = sise.evaluate_subtxt_informed_semantic_rubric(req)
    assert any(
        item["category"] == "owner_review_question"
        for item in result["diagnostic_questions"]
    )


# ---------------------------------------------------------------------------
# 9. Each category does not trigger without its required cues
# ---------------------------------------------------------------------------


def test_structural_diagnostic_does_not_trigger_without_resistance():
    req = _valid_request(
        source_text="Mara wants the key and the mentor smiles.",
        requested_categories=[
            "structural_diagnostic",
            "owner_review_question",
        ],
    )
    result = sise.evaluate_subtxt_informed_semantic_rubric(req)
    assert not any(
        item["category"] == "structural_diagnostic"
        for item in result["candidate_support"]
    )


def test_conflict_diagnostic_does_not_trigger_without_opposing_pressure():
    req = _valid_request(
        source_text="Mara walks home and smiles at the mentor.",
        requested_categories=[
            "conflict_diagnostic",
            "owner_review_question",
        ],
    )
    result = sise.evaluate_subtxt_informed_semantic_rubric(req)
    assert not any(
        item["category"] == "conflict_diagnostic"
        for item in result["candidate_support"]
    )


def test_throughline_question_does_not_trigger_with_few_actor_signals():
    req = _valid_request(
        source_text="Mara walks home and smiles.",
        requested_categories=[
            "throughline_context_question",
            "owner_review_question",
        ],
    )
    result = sise.evaluate_subtxt_informed_semantic_rubric(req)
    assert not any(
        item["category"] == "throughline_context_question"
        for item in result["diagnostic_questions"]
    )


def test_story_point_question_does_not_trigger_without_temporal_cue():
    req = _valid_request(
        source_text="Mara walks home and smiles at the mentor.",
        requested_categories=[
            "story_point_context_question",
            "owner_review_question",
        ],
    )
    result = sise.evaluate_subtxt_informed_semantic_rubric(req)
    assert not any(
        item["category"] == "story_point_context_question"
        for item in result["diagnostic_questions"]
    )


def test_source_of_conflict_hypothesis_requires_both_causal_and_resistance():
    req_no_resistance = _valid_request(
        source_text="Mara walks home as the mentor smiles at her.",
        requested_categories=[
            "source_of_conflict_hypothesis",
            "owner_review_question",
        ],
    )
    result_no_resistance = sise.evaluate_subtxt_informed_semantic_rubric(
        req_no_resistance
    )
    assert not any(
        item["category"] == "source_of_conflict_hypothesis"
        for item in result_no_resistance["candidate_support"]
    )

    req_no_causal = _valid_request(
        source_text="Mara wants the key, but the rival blocks her path.",
        requested_categories=[
            "source_of_conflict_hypothesis",
            "owner_review_question",
        ],
    )
    result_no_causal = sise.evaluate_subtxt_informed_semantic_rubric(
        req_no_causal
    )
    assert not any(
        item["category"] == "source_of_conflict_hypothesis"
        for item in result_no_causal["candidate_support"]
    )


def test_subject_vs_conflict_question_does_not_trigger_without_actor():
    req = _valid_request(
        source_text="The storm blocks the path.",
        requested_categories=[
            "subject_vs_conflict_question",
            "owner_review_question",
        ],
    )
    result = sise.evaluate_subtxt_informed_semantic_rubric(req)
    assert not any(
        item["category"] == "subject_vs_conflict_question"
        for item in result["diagnostic_questions"]
    )


def test_ambiguity_does_not_trigger_without_uncertainty_cue():
    req = _valid_request(
        source_text="Mara wants the key, but the rival blocks her path.",
        requested_categories=["ambiguity", "owner_review_question"],
    )
    result = sise.evaluate_subtxt_informed_semantic_rubric(req)
    assert not any(
        item["category"] == "ambiguity"
        for item in result["candidate_support"]
    )


def test_insufficient_evidence_does_not_trigger_when_substantive_match_found():
    req = _valid_request(
        source_text=(
            "Mara wants the key, but the rival blocks her path and the "
            "storm threatens the coast at dawn."
        ),
        requested_categories=[
            "insufficient_evidence",
            "structural_diagnostic",
            "owner_review_question",
        ],
    )
    result = sise.evaluate_subtxt_informed_semantic_rubric(req)
    assert not any(
        item["category"] == "insufficient_evidence"
        for item in result["candidate_support"]
    )


# ---------------------------------------------------------------------------
# 10. Category-to-candidate-type mapping is exact
# ---------------------------------------------------------------------------


def test_category_to_candidate_type_mapping_is_exact():
    expected = {
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
    result = sise.evaluate_subtxt_informed_semantic_rubric(_valid_request())
    seen: dict[str, str] = {}
    for item in result["candidate_support"] + result["diagnostic_questions"]:
        seen[item["category"]] = item["candidate_type"]
    for category, candidate_type in expected.items():
        if category in seen:
            assert seen[category] == candidate_type


# ---------------------------------------------------------------------------
# 11. Candidate and question placement
# ---------------------------------------------------------------------------


def test_non_question_items_go_to_candidate_support():
    req = _valid_request(
        source_text=(
            "Mara wants the key, but the rival blocks her path. "
            "Because the rival opposes Mara, the archive stays sealed."
        ),
        requested_categories=[
            "structural_diagnostic",
            "conflict_diagnostic",
            "source_of_conflict_hypothesis",
            "ambiguity",
            "insufficient_evidence",
        ],
    )
    result = sise.evaluate_subtxt_informed_semantic_rubric(req)
    for item in result["candidate_support"]:
        assert item["category"] in sisc.NON_QUESTION_CATEGORIES
    assert result["diagnostic_questions"] == []


def test_question_items_go_to_diagnostic_questions():
    req = _valid_request(
        source_text=(
            "Before, Mara and Jonah discuss the key, then Mara decides to "
            "leave. Later Mara discovers the truth."
        ),
        requested_categories=[
            "throughline_context_question",
            "story_point_context_question",
            "subject_vs_conflict_question",
            "owner_review_question",
        ],
    )
    result = sise.evaluate_subtxt_informed_semantic_rubric(req)
    for item in result["diagnostic_questions"]:
        assert item["category"] in sisc.QUESTION_CATEGORIES
    assert result["candidate_support"] == []


# ---------------------------------------------------------------------------
# 12. Statement-kind mapping is exact
# ---------------------------------------------------------------------------


def test_statement_kind_mapping_is_exact():
    result = sise.evaluate_subtxt_informed_semantic_rubric(_valid_request())
    expected = {
        "structural_diagnostic": "candidate_observation",
        "conflict_diagnostic": "candidate_observation",
        "source_of_conflict_hypothesis": "hypothesis",
        "ambiguity": "ambiguity",
        "insufficient_evidence": "insufficient_evidence",
    }
    seen: dict[str, str] = {}
    for item in result["candidate_support"] + result["diagnostic_questions"]:
        seen[item["category"]] = item["statement_kind"]
    for category, kind in expected.items():
        if category in seen:
            assert seen[category] == kind


def test_question_items_have_question_statement_kind():
    result = sise.evaluate_subtxt_informed_semantic_rubric(_valid_request())
    for item in result["diagnostic_questions"]:
        assert item["statement_kind"] == "question"


# ---------------------------------------------------------------------------
# 13. Evidence excerpt is an exact source substring
# ---------------------------------------------------------------------------


def test_evidence_excerpt_is_exact_substring_of_source_text():
    source_text = (
        "Mara wants the key, but the rival blocks her path. "
        "Mara and the mentor later discuss the next step."
    )
    req = _valid_request(
        source_text=source_text,
        requested_categories=[
            "structural_diagnostic",
            "conflict_diagnostic",
            "throughline_context_question",
            "story_point_context_question",
            "owner_review_question",
        ],
    )
    result = sise.evaluate_subtxt_informed_semantic_rubric(req)
    for item in result["candidate_support"] + result["diagnostic_questions"]:
        for evidence in item["evidence"]:
            assert evidence["source_excerpt"] in source_text


# ---------------------------------------------------------------------------
# 14. Evidence is not copied into generated diagnostic text
# ---------------------------------------------------------------------------


def test_evidence_is_not_copied_into_diagnostic_text():
    source_text = (
        "Mara wants the key, but the rival blocks her path."
    )
    req = _valid_request(
        source_text=source_text,
        requested_categories=[
            "structural_diagnostic",
            "conflict_diagnostic",
            "source_of_conflict_hypothesis",
            "owner_review_question",
        ],
    )
    result = sise.evaluate_subtxt_informed_semantic_rubric(req)
    for item in result["candidate_support"] + result["diagnostic_questions"]:
        for evidence in item["evidence"]:
            assert evidence["source_excerpt"] != item["diagnostic_text"]


# ---------------------------------------------------------------------------
# 15. Request refs and locator are preserved
# ---------------------------------------------------------------------------


def test_top_level_refs_and_locator_are_preserved():
    req = _valid_request()
    result = sise.evaluate_subtxt_informed_semantic_rubric(req)
    assert result["source_refs"] == req["source_refs"]
    assert result["evidence_refs"] == req["evidence_refs"]
    assert result["provenance_refs"] == req["provenance_refs"]
    assert result["source_locator_refs"] == req["source_locator_refs"]


def test_item_locator_appears_in_source_locator_refs():
    result = sise.evaluate_subtxt_informed_semantic_rubric(_valid_request())
    for item in result["candidate_support"] + result["diagnostic_questions"]:
        assert item["source_locator"] in item["source_locator_refs"]


def test_item_refs_are_copied_from_request():
    result = sise.evaluate_subtxt_informed_semantic_rubric(_valid_request())
    for item in result["candidate_support"] + result["diagnostic_questions"]:
        assert item["source_refs"] == [
            "source_ref_owner_scene_001"
        ]
        assert item["evidence_refs"] == [
            "evidence_ref_scene_001_span_001"
        ]
        assert item["provenance_refs"] == ["provenance_ref_rubric_001"]


# ---------------------------------------------------------------------------
# 16. Owner decision and review status remain pending
# ---------------------------------------------------------------------------


def test_owner_decision_and_review_status_remain_pending():
    result = sise.evaluate_subtxt_informed_semantic_rubric(_valid_request())
    for item in result["candidate_support"] + result["diagnostic_questions"]:
        assert item["owner_decision"] == {
            "approved": False,
            "decision": "pending",
        }
        assert item["review_status"] == "candidate_review_pending"


# ---------------------------------------------------------------------------
# 17. Exact app-owned identity and label
# ---------------------------------------------------------------------------


def test_top_level_provenance_uses_app_owned_identity():
    result = sise.evaluate_subtxt_informed_semantic_rubric(_valid_request())
    provenance = result["provenance"]
    assert provenance["tool_source"] == sisc.SUBTXT_INFORMED_RUBRIC_ID
    assert provenance["adapter"] == sisc.SUBTXT_INFORMED_RUBRIC_ID
    assert provenance["support"] == sisc.SUBTXT_INFORMED_RUBRIC_SUPPORT_LABEL
    assert provenance["executes_subtxt"] is False
    assert provenance["official_subtxt_output"] is False


def test_item_provenance_and_support_label_use_app_owned_identity():
    result = sise.evaluate_subtxt_informed_semantic_rubric(_valid_request())
    for item in result["candidate_support"] + result["diagnostic_questions"]:
        assert (
            item["provenance"]["tool_source"]
            == sisc.SUBTXT_INFORMED_RUBRIC_ID
        )
        assert (
            item["provenance"]["adapter"]
            == sisc.SUBTXT_INFORMED_RUBRIC_ID
        )
        assert (
            item["provenance"]["support"]
            == sisc.SUBTXT_INFORMED_RUBRIC_SUPPORT_LABEL
        )
        assert (
            item["support_label"]
            == sisc.SUBTXT_INFORMED_RUBRIC_SUPPORT_LABEL
        )


# ---------------------------------------------------------------------------
# 18. Never uses subtxt provenance identity
# ---------------------------------------------------------------------------


def test_evaluator_never_uses_subtxt_provenance_identity():
    result = sise.evaluate_subtxt_informed_semantic_rubric(_valid_request())
    assert result["provenance"]["tool_source"] != "subtxt"
    assert result["provenance"]["adapter"] != "subtxt"
    for item in result["candidate_support"] + result["diagnostic_questions"]:
        assert item["provenance"]["tool_source"] != "subtxt"
        assert item["provenance"]["adapter"] != "subtxt"


# ---------------------------------------------------------------------------
# 19. All safety flags are false
# ---------------------------------------------------------------------------


def test_all_safety_flags_are_false():
    result = sise.evaluate_subtxt_informed_semantic_rubric(_valid_request())
    for key in sisc.ALLOWED_OPERATION_FLAGS:
        assert result["safety"][key] is False


# ---------------------------------------------------------------------------
# 20. No live/official Subtxt claim
# ---------------------------------------------------------------------------


def test_no_live_or_official_subtxt_claim():
    result = sise.evaluate_subtxt_informed_semantic_rubric(_valid_request())
    assert result["provenance"]["executes_subtxt"] is False
    assert result["provenance"]["official_subtxt_output"] is False
    for item in result["candidate_support"] + result["diagnostic_questions"]:
        assert item["executes_subtxt"] is False
        assert item["official_subtxt_output"] is False
    serialized = str(result)
    assert "subtxt runtime result" not in serialized.lower()
    assert "live subtxt analysis" not in serialized.lower()
    assert "official subtxt diagnosis" not in serialized.lower()
    assert "subtxt-confirmed storyform" not in serialized.lower()


# ---------------------------------------------------------------------------
# 21. Confidence policy
# ---------------------------------------------------------------------------


def test_confidence_policy_no_high_support():
    result = sise.evaluate_subtxt_informed_semantic_rubric(_valid_request())
    for item in result["candidate_support"] + result["diagnostic_questions"]:
        assert item["confidence"] != "high_support"


def test_confidence_medium_for_dual_cue_observations():
    req = _valid_request(
        source_text=(
            "Mara wants the key, but the rival blocks her path, because the "
            "archive stays sealed and the storm threatens the coast."
        ),
        requested_categories=[
            "structural_diagnostic",
            "source_of_conflict_hypothesis",
            "owner_review_question",
        ],
    )
    result = sise.evaluate_subtxt_informed_semantic_rubric(req)
    structural = next(
        item
        for item in result["candidate_support"]
        if item["category"] == "structural_diagnostic"
    )
    assert structural["confidence"] == "medium_support"
    hypothesis = next(
        item
        for item in result["candidate_support"]
        if item["category"] == "source_of_conflict_hypothesis"
    )
    assert hypothesis["confidence"] == "medium_support"


def test_confidence_low_for_questions_and_ambiguity_and_insufficient():
    result = sise.evaluate_subtxt_informed_semantic_rubric(_valid_request())
    low_categories = {
        "throughline_context_question",
        "story_point_context_question",
        "subject_vs_conflict_question",
        "owner_review_question",
        "ambiguity",
        "insufficient_evidence",
    }
    for item in result["candidate_support"] + result["diagnostic_questions"]:
        if item["category"] in low_categories:
            assert item["confidence"] == "low_support"


# ---------------------------------------------------------------------------
# 22. Uncertainty policy
# ---------------------------------------------------------------------------


def test_uncertainty_policy_ambiguity():
    req = _valid_request(
        source_text="Maybe Mara could find the key, perhaps later.",
        requested_categories=["ambiguity", "owner_review_question"],
    )
    result = sise.evaluate_subtxt_informed_semantic_rubric(req)
    ambiguity = next(
        item
        for item in result["candidate_support"]
        if item["category"] == "ambiguity"
    )
    assert ambiguity["uncertainty_label"] == "ambiguity"


def test_uncertainty_policy_insufficient_evidence():
    req = _valid_request(
        source_text="Short text.",
        requested_categories=[
            "insufficient_evidence",
            "owner_review_question",
        ],
    )
    result = sise.evaluate_subtxt_informed_semantic_rubric(req)
    insufficient = next(
        item
        for item in result["candidate_support"]
        if item["category"] == "insufficient_evidence"
    )
    assert insufficient["uncertainty_label"] == "insufficient_evidence"


def test_uncertainty_policy_questions_and_hypotheses_owner_interpretation():
    req = _valid_request(
        source_text=(
            "Mara and Jonah discuss the key, then Mara decides to leave. "
            "Because the rival blocks her, Mara waits."
        ),
        requested_categories=[
            "throughline_context_question",
            "story_point_context_question",
            "subject_vs_conflict_question",
            "source_of_conflict_hypothesis",
            "owner_review_question",
        ],
    )
    result = sise.evaluate_subtxt_informed_semantic_rubric(req)
    for item in result["diagnostic_questions"]:
        assert (
            item["uncertainty_label"] == "requires_owner_interpretation"
        )
    for item in result["candidate_support"]:
        if item["category"] == "source_of_conflict_hypothesis":
            assert (
                item["uncertainty_label"]
                == "requires_owner_interpretation"
            )


def test_uncertainty_policy_null_for_other_observations():
    req = _valid_request(
        source_text="Mara wants the key, but the rival blocks her path.",
        requested_categories=[
            "structural_diagnostic",
            "conflict_diagnostic",
            "owner_review_question",
        ],
    )
    result = sise.evaluate_subtxt_informed_semantic_rubric(req)
    for item in result["candidate_support"]:
        if item["category"] in {
            "structural_diagnostic",
            "conflict_diagnostic",
        }:
            assert item["uncertainty_label"] == "null"


# ---------------------------------------------------------------------------
# 23. Short input produces insufficient-evidence item when requested
# ---------------------------------------------------------------------------


def test_short_input_produces_insufficient_evidence_item():
    req = _valid_request(
        source_text="A few words here.",
        requested_categories=[
            "insufficient_evidence",
            "owner_review_question",
        ],
    )
    result = sise.evaluate_subtxt_informed_semantic_rubric(req)
    assert any(
        item["category"] == "insufficient_evidence"
        for item in result["candidate_support"]
    )


# ---------------------------------------------------------------------------
# 24. No-match request returns empty
# ---------------------------------------------------------------------------


def test_no_match_request_returns_empty_status():
    req = _valid_request(
        source_text="Calm and quiet day in the village.",
        requested_categories=[
            "structural_diagnostic",
            "conflict_diagnostic",
            "source_of_conflict_hypothesis",
            "ambiguity",
        ],
    )
    result = sise.evaluate_subtxt_informed_semantic_rubric(req)
    assert result["status"] == "empty"
    assert result["candidate_support"] == []
    assert result["diagnostic_questions"] == []


def test_empty_result_validates_through_t019c_validator():
    req = _valid_request(
        source_text="Calm and quiet day in the village.",
        requested_categories=["structural_diagnostic"],
    )
    result = sise.evaluate_subtxt_informed_semantic_rubric(req)
    response = sisc.validate_subtxt_informed_rubric_result(result)
    assert response["status"] == "valid", response["errors"]


# ---------------------------------------------------------------------------
# 25. Owner-review question always emits for valid non-empty source
# ---------------------------------------------------------------------------


def test_owner_review_question_always_emits_for_valid_non_empty_source_case1():
    req = _valid_request(
        source_text="Mara walks home and smiles.",
        requested_categories=["owner_review_question"],
    )
    result = sise.evaluate_subtxt_informed_semantic_rubric(req)
    assert any(
        item["category"] == "owner_review_question"
        for item in result["diagnostic_questions"]
    )


def test_owner_review_question_always_emits_for_valid_non_empty_source_case2():
    req = _valid_request(
        source_text="Maybe Mara could find the key, perhaps later.",
        requested_categories=["owner_review_question"],
    )
    result = sise.evaluate_subtxt_informed_semantic_rubric(req)
    assert any(
        item["category"] == "owner_review_question"
        for item in result["diagnostic_questions"]
    )


# ---------------------------------------------------------------------------
# 26. Source-of-conflict hypothesis requires both causal and resistance cues
# ---------------------------------------------------------------------------


def test_source_of_conflict_requires_both_causal_and_resistance():
    req = _valid_request(
        source_text=(
            "Mara wants the key, because the rival blocks her path, "
            "therefore Mara waits."
        ),
        requested_categories=[
            "source_of_conflict_hypothesis",
            "owner_review_question",
        ],
    )
    result = sise.evaluate_subtxt_informed_semantic_rubric(req)
    assert any(
        item["category"] == "source_of_conflict_hypothesis"
        for item in result["candidate_support"]
    )


# ---------------------------------------------------------------------------
# 27. Question text ends with ?
# ---------------------------------------------------------------------------


def test_question_text_ends_with_question_mark():
    req = _valid_request(
        source_text=(
            "Mara and Jonah discuss the key, then Mara decides to leave."
        ),
        requested_categories=[
            "throughline_context_question",
            "story_point_context_question",
            "subject_vs_conflict_question",
            "owner_review_question",
        ],
    )
    result = sise.evaluate_subtxt_informed_semantic_rubric(req)
    for item in result["diagnostic_questions"]:
        assert item["diagnostic_text"].rstrip().endswith("?")


# ---------------------------------------------------------------------------
# 28. Source text with sensitive words is preserved and not falsely rejected
# ---------------------------------------------------------------------------


def test_source_text_with_sensitive_words_is_preserved():
    sensitive_source = (
        "The canon draft mentions a final approved rewrite outline. "
        "Mara wants the key, but the rival blocks her."
    )
    req = _valid_request(source_text=sensitive_source)
    result = sise.evaluate_subtxt_informed_semantic_rubric(req)
    assert result["status"] == "succeeded"
    for item in result["candidate_support"] + result["diagnostic_questions"]:
        for evidence in item["evidence"]:
            assert isinstance(evidence["source_excerpt"], str)
            assert evidence["source_excerpt"] in sensitive_source


# ---------------------------------------------------------------------------
# 29. Generated fields pass the T019C recursive safety checks
# ---------------------------------------------------------------------------


def test_generated_fields_pass_t019c_recursive_safety_checks():
    result = sise.evaluate_subtxt_informed_semantic_rubric(_valid_request())
    response = sisc.validate_subtxt_informed_rubric_result(result)
    assert response["status"] == "valid", response["errors"]


# ---------------------------------------------------------------------------
# 30. Evaluator result passes validate_subtxt_informed_rubric_result
# ---------------------------------------------------------------------------


def test_evaluator_result_passes_t019c_result_validator():
    result = sise.evaluate_subtxt_informed_semantic_rubric(_valid_request())
    response = sisc.validate_subtxt_informed_rubric_result(result)
    assert response["status"] == "valid", response["errors"]


# ---------------------------------------------------------------------------
# 31. Evaluator result passes generic rubric_mapping_support validation
# ---------------------------------------------------------------------------


def _rubric_mapping_support_allowlist_record() -> dict[str, Any]:
    return {
        "tool_name": "Subtxt",
        "module_or_feature_name": "build_rubric_mapping_support",
        "allowed_action": "build_rubric_mapping_support",
        "forbidden_actions": [
            "generate_prose",
            "rewrite",
            "continuation",
            "outline",
            "draft",
            "revision",
            "polish",
            "expansion",
            "style_imitation",
            "export_as_prose",
            "apply_promotion",
            "canon_mutation",
            "training_artifact",
        ],
        "output_classes_allowed": ["rubric_mapping_support"],
        "output_classes_forbidden": [
            "generated_prose",
            "rewritten_prose",
            "continuation",
            "outline",
            "chapter_generation",
            "draft",
            "revision",
            "polish",
            "improvement",
            "expansion",
            "style_imitation",
            "export_as_prose",
            "story_prose",
            "model_prompt_artifact",
            "model_completion_artifact",
            "training_jsonl",
            "dataset_manifest",
            "model_artifact",
            "promotion_record",
            "approved_memory",
            "canon",
            "bible",
            "storyform_truth",
            "scene_mutation",
            "note_mutation",
            "material_mutation",
        ],
        "required_refs": [
            "source_refs",
            "evidence_refs",
            "provenance_refs",
            "source_locator_refs",
        ],
        "source_locator_policy": "required_when_available",
        "evidence_policy": "required",
        "provenance_policy": "required",
        "owner_review_policy": "owner review required",
        "fail_closed_policy": "fail closed",
        "no_silent_fallback_policy": "no silent fallback",
        "no_prose_policy": "no generated prose",
        "no_training_policy": "no training artifacts",
        "no_canon_policy": "no automatic canon",
        "no_apply_promotion_policy": "no apply-promotion",
        "validation_tests_required": True,
        "audit_notes": "T019D rubric_mapping_support allowlist record",
    }


def test_succeeded_result_validates_against_generic_runtime_validator():
    result = sise.evaluate_subtxt_informed_semantic_rubric(_valid_request())
    response = ari.validate_analysis_runtime_output(
        result, _rubric_mapping_support_allowlist_record()
    )
    assert response["allowed_output_class"] is True
    assert response["output_class"] == "rubric_mapping_support"


def test_fail_closed_result_validates_against_generic_runtime_validator():
    bad = {"not": "a valid request"}
    result = sise.evaluate_subtxt_informed_semantic_rubric(bad)
    response = ari.validate_analysis_runtime_output(
        result, _rubric_mapping_support_allowlist_record()
    )
    assert response["allowed_output_class"] is True
    assert response["output_class"] == "rubric_mapping_support"


# ---------------------------------------------------------------------------
# 32. Unexpected internal evaluator failure returns fail closed
# ---------------------------------------------------------------------------


def test_unexpected_internal_failure_returns_fail_closed(monkeypatch):
    def _boom(*_args, **_kwargs):
        raise RuntimeError("simulated internal evaluator failure")

    monkeypatch.setattr(
        sise, "_split_into_evidence_spans", _boom
    )
    result = sise.evaluate_subtxt_informed_semantic_rubric(_valid_request())
    assert result["status"] == "failed_closed"
    assert result["fail_closed_reason"] == "unexpected_evaluator_failure"
    assert result["candidate_support"] == []
    assert result["diagnostic_questions"] == []


# ---------------------------------------------------------------------------
# 33. No file I/O
# ---------------------------------------------------------------------------


def test_evaluator_module_does_not_open_files():
    source_path = sise.__file__
    assert source_path is not None
    text = Path(source_path).read_text(encoding="utf-8")
    forbidden_open_tokens = (
        "open(",
        "Path(",
        "with open(",
    )
    for token in forbidden_open_tokens:
        assert token not in text, f"forbidden open token found: {token!r}"


# ---------------------------------------------------------------------------
# 34. No subprocess/shell/network
# ---------------------------------------------------------------------------


def test_evaluator_module_does_not_use_subprocess_shell_or_network():
    source_path = sise.__file__
    assert source_path is not None
    text = Path(source_path).read_text(encoding="utf-8")
    forbidden_tokens = (
        "subprocess",
        "urllib",
        "requests",
        "socket",
        "http.client",
        "httpx",
    )
    for token in forbidden_tokens:
        assert token not in text, f"forbidden network/shell token: {token!r}"


def test_evaluator_runtime_does_not_call_subprocess_shell_or_network(monkeypatch):
    calls: list[str] = []
    original_subprocess_run = subprocess.run
    original_subprocess_popen = subprocess.Popen
    original_socket_socket = socket.socket

    def _record(name):
        def _fail(*args, **kwargs):
            calls.append(name)
            raise AssertionError(f"{name} should not be called")
        return _fail

    monkeypatch.setattr(subprocess, "run", _record("subprocess.run"))
    monkeypatch.setattr(subprocess, "Popen", _record("subprocess.Popen"))
    monkeypatch.setattr(socket, "socket", _record("socket.socket"))

    try:
        sise.evaluate_subtxt_informed_semantic_rubric(_valid_request())
    finally:
        monkeypatch.setattr(subprocess, "run", original_subprocess_run)
        monkeypatch.setattr(subprocess, "Popen", original_subprocess_popen)
        monkeypatch.setattr(socket, "socket", original_socket_socket)

    assert calls == [], f"unexpected side-effect calls: {calls}"


# ---------------------------------------------------------------------------
# 35. No environment-variable read
# ---------------------------------------------------------------------------


def test_evaluator_module_does_not_import_os_or_read_env():
    source_path = sise.__file__
    assert source_path is not None
    text = Path(source_path).read_text(encoding="utf-8")
    assert "import os" not in text
    assert "from os" not in text
    assert "os.environ" not in text
    assert "getenv" not in text


# ---------------------------------------------------------------------------
# 36. No model import/call
# ---------------------------------------------------------------------------


def test_evaluator_module_does_not_import_model_clients():
    source_path = sise.__file__
    assert source_path is not None
    text = Path(source_path).read_text(encoding="utf-8")
    forbidden_tokens = (
        "openai",
        "anthropic",
        "ollama",
        "ollama",
    )
    for token in forbidden_tokens:
        assert token not in text, (
            f"forbidden model import token: {token!r}"
        )


# ---------------------------------------------------------------------------
# 37. No project-storage helper
# ---------------------------------------------------------------------------


def test_evaluator_module_does_not_import_project_storage():
    source_path = sise.__file__
    assert source_path is not None
    text = Path(source_path).read_text(encoding="utf-8")
    forbidden_tokens = (
        "project_manager",
        "candidate_storage",
        "candidate_index",
        "candidate_record",
        "candidate_schema",
        "review_queue_storage",
        "raw_artifacts",
        "raw_extraction_storage",
        "candidate_persistence",
        "candidate_review_gate",
        "apply_promotion",
    )
    for token in forbidden_tokens:
        assert token not in text, (
            f"forbidden project-storage import: {token!r}"
        )


# ---------------------------------------------------------------------------
# 38. No candidate-persistence helper
# ---------------------------------------------------------------------------


def test_evaluator_module_does_not_call_candidate_persistence():
    source_path = sise.__file__
    assert source_path is not None
    text = Path(source_path).read_text(encoding="utf-8")
    forbidden_tokens = (
        "persist_candidate",
        "create_candidate",
        "save_candidate",
        "write_candidate",
        "add_candidate",
        "store_candidate",
        "persist_finding",
    )
    for token in forbidden_tokens:
        assert token not in text, (
            f"forbidden candidate-persistence call: {token!r}"
        )


# ---------------------------------------------------------------------------
# 39. No promotion/apply-promotion helper
# ---------------------------------------------------------------------------


def test_evaluator_module_does_not_call_promotion_or_apply_promotion():
    source_path = sise.__file__
    assert source_path is not None
    text = Path(source_path).read_text(encoding="utf-8")
    forbidden_tokens = (
        "apply_promotion",
        "promote_to_canon",
        "promotion_record",
        "mutate_canon",
        "mutate_memory",
        "approved_memory",
    )
    for token in forbidden_tokens:
        assert token not in text, (
            f"forbidden promotion helper: {token!r}"
        )


# ---------------------------------------------------------------------------
# 40. No .external_sources read or import
# ---------------------------------------------------------------------------


def test_evaluator_module_does_not_read_or_import_external_sources():
    import importlib

    module = importlib.import_module(
        "backend.story_knowledge.subtxt_informed_semantic_rubric_evaluator"
    )
    assert ".external_sources" not in dir(module)
    assert "subtxt_docs" not in dir(module)
    assert "narrative_context_protocol" not in dir(module)
    source_path = module.__file__
    assert source_path is not None
    text = Path(source_path).read_text(encoding="utf-8")
    assert ".external_sources" not in text
    assert "subtxt_docs" not in text
    assert "narrative_context_protocol" not in text


# ---------------------------------------------------------------------------
# Additional safety module-imports check
# ---------------------------------------------------------------------------


def test_evaluator_module_imports_only_standard_library_plus_contract():
    source_path = sise.__file__
    assert source_path is not None
    text = Path(source_path).read_text(encoding="utf-8")
    import_line_pattern = re.compile(
        r"^(?:from|import)\s+([\w.]+)", re.MULTILINE
    )
    imports = set(import_line_pattern.findall(text))
    allowed_typing_only = {
        "copy",
        "re",
        "typing",
        "__future__",
        "backend.story_knowledge.subtxt_informed_semantic_rubric_contract",
    }
    unexpected = imports - allowed_typing_only
    assert not unexpected, f"unexpected imports: {sorted(unexpected)}"


# ---------------------------------------------------------------------------
# Extra safety: no Storyform / no Dramatica truth claim
# ---------------------------------------------------------------------------


def test_evaluator_does_not_emit_storyform_or_dramatica_truth_claim():
    result = sise.evaluate_subtxt_informed_semantic_rubric(_valid_request())
    serialized = str(result).lower()
    for forbidden in (
        "storyform",
        "dramatica",
        " throughline ",
        "objectively speak",
        "conclusiv",
        "definitiv",
    ):
        assert forbidden not in serialized, (
            f"forbidden truth token {forbidden!r} in evaluator output"
        )
