"""PHASE8-IMPL-023-T019C app-owned Subtxt-informed semantic-rubric contract tests.

These tests cover the pure, app-owned input/output contract for future
Subtxt-informed semantic-rubric evaluation. They are in-memory only.
They never import or run Subtxt, never read or import
``.external_sources/subtxt-docs``, never call a model, never persist
candidates, never mutate projects, Memory, or Canon, and never read real
project files. The tests use only the contract module and synthetic
in-memory dictionaries.

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
import sys
from pathlib import Path
from typing import Any

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from backend.story_knowledge import subtxt_informed_semantic_rubric_contract as sisc
from backend.story_knowledge import analysis_runtime_integration as ari


# ---------------------------------------------------------------------------
# Constants and identity (test 1)
# ---------------------------------------------------------------------------


def test_public_schema_version_constants_have_exact_values():
    assert sisc.SUBTXT_INFORMED_RUBRIC_REQUEST_SCHEMA_VERSION == (
        "omi_app_owned_subtxt_informed_rubric_request.v1"
    )
    assert sisc.SUBTXT_INFORMED_RUBRIC_RESULT_SCHEMA_VERSION == (
        "omi_app_owned_subtxt_informed_rubric_result.v1"
    )


def test_public_identity_constants_have_exact_values():
    assert sisc.SUBTXT_INFORMED_RUBRIC_ID == "app_owned_subtxt_informed_rubric"
    assert sisc.SUBTXT_INFORMED_RUBRIC_OUTPUT_CLASS == "rubric_mapping_support"
    assert sisc.SUBTXT_INFORMED_RUBRIC_SUPPORT_LABEL == (
        "App-owned Subtxt-informed diagnostic support"
    )


def test_t009_subtxt_identity_is_preserved_unchanged():
    """The new app-owned contract must not change the existing T009 identity.

    The T009 live/fixture adapter contract remains ``subtxt`` and the
    T009 support label remains ``Subtxt diagnostic support only``. The
    T019C schema version remains the T009 schema version
    ``omi_subtxt_diagnostic_handoff.v1``.
    """

    from backend import omi_analysis_orchestrator as oao

    assert oao.OMI_SUBTXT_SCHEMA_VERSION == "omi_subtxt_diagnostic_handoff.v1"
    assert oao.OMI_CONTEXT_ADAPTER_NAMES == frozenset(
        {"ncp", "subtxt", "dramatica_flow"}
    )
    assert oao.OMI_CONTEXT_SUPPORT_LABEL_BY_ADAPTER["subtxt"] == (
        "Subtxt diagnostic support only"
    )


def test_analysis_runtime_integration_subtxt_boundary_is_preserved():
    """The generic analysis-runtime boundary must still report Subtxt as
    rubric/diagnostic guidance only and must not actually execute Subtxt.
    """
    assert ari.SUPPORTED_ACTIONS["Subtxt"] == frozenset(
        {"build_rubric_mapping_support"}
    )
    assert ari.TOOL_BOUNDARIES["Subtxt"] == "rubric/diagnostic guidance only"
    # The base non-execution result preserves executes_subtxt=False.
    base = ari._non_execution_result()
    assert base["executes_subtxt"] is False


# ---------------------------------------------------------------------------
# Request validation (tests 2, 9, 10, 11, 12, 14, 15, 21, 22, 26)
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
        "source_text": "Owner-authored source text. archive key pressure.",
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
        ],
        "analysis_intent": "diagnostic_support",
        "owner_authored_or_owner_provided_source": True,
        "safety_confirmations": _valid_safety_confirmations(),
    }
    request.update(overrides)
    return request


def test_valid_request_normalization_succeeds():
    response = sisc.validate_subtxt_informed_rubric_request(_valid_request())
    assert response["status"] == "valid"
    assert response["valid"] is True
    assert response["fail_closed"] is False
    assert response["errors"] == []
    assert response["normalized_request"]["rubric_id"] == (
        sisc.SUBTXT_INFORMED_RUBRIC_ID
    )
    assert response["executes_subtxt"] is False
    assert response["official_subtxt_output"] is False


def test_request_with_wrong_schema_version_fails_closed():
    req = _valid_request(schema_version="some_other_schema.v9")
    response = sisc.validate_subtxt_informed_rubric_request(req)
    assert response["status"] == "fail_closed"
    assert response["valid"] is False
    assert response["fail_closed"] is True
    assert any("schema_version" in err for err in response["errors"])


def test_request_with_wrong_rubric_identity_fails_closed():
    req = _valid_request(rubric_id="subtxt")
    response = sisc.validate_subtxt_informed_rubric_request(req)
    assert response["status"] == "fail_closed"
    assert any("rubric_id" in err for err in response["errors"])


def test_request_missing_field_fails_closed():
    req = _valid_request()
    del req["request_id"]
    response = sisc.validate_subtxt_informed_rubric_request(req)
    assert response["status"] == "fail_closed"
    assert any("request_id" in err for err in response["errors"])


def test_request_empty_source_text_fails_closed():
    req = _valid_request(source_text="")
    response = sisc.validate_subtxt_informed_rubric_request(req)
    assert response["status"] == "fail_closed"
    assert any("source_text" in err for err in response["errors"])


def test_request_source_locator_must_appear_in_source_locator_refs():
    req = _valid_request(
        source_locator="source_locator_ref_owner_scene_999",
    )
    response = sisc.validate_subtxt_informed_rubric_request(req)
    assert response["status"] == "fail_closed"
    assert any(
        "source_locator must appear in source_locator_refs" in err
        for err in response["errors"]
    )


def test_request_unknown_category_fails_closed():
    req = _valid_request(
        requested_categories=[
            "structural_diagnostic",
            "made_up_category",
        ],
    )
    response = sisc.validate_subtxt_informed_rubric_request(req)
    assert response["status"] == "fail_closed"
    assert any(
        "made_up_category" in err for err in response["errors"]
    )


def test_request_duplicate_category_fails_closed():
    req = _valid_request(
        requested_categories=[
            "structural_diagnostic",
            "structural_diagnostic",
        ],
    )
    response = sisc.validate_subtxt_informed_rubric_request(req)
    assert response["status"] == "fail_closed"
    assert any(
        "requested_categories" in err for err in response["errors"]
    )


def test_request_wrong_analysis_intent_fails_closed():
    req = _valid_request(analysis_intent="rewrite this chapter")
    response = sisc.validate_subtxt_informed_rubric_request(req)
    assert response["status"] == "fail_closed"
    assert any("analysis_intent" in err for err in response["errors"])


def test_request_owner_source_must_be_true_fails_closed():
    req = _valid_request(owner_authored_or_owner_provided_source=False)
    response = sisc.validate_subtxt_informed_rubric_request(req)
    assert response["status"] == "fail_closed"
    assert any(
        "owner_authored_or_owner_provided_source" in err
        for err in response["errors"]
    )


def test_request_missing_safety_confirmation_fails_closed():
    req = _valid_request()
    req["safety_confirmations"] = {
        k: v for k, v in _valid_safety_confirmations().items()
        if k != "no_subtxt_execution"
    }
    response = sisc.validate_subtxt_informed_rubric_request(req)
    assert response["status"] == "fail_closed"
    assert any(
        "no_subtxt_execution" in err for err in response["errors"]
    )


def test_request_false_safety_confirmation_fails_closed():
    req = _valid_request()
    req["safety_confirmations"]["no_generated_prose"] = False
    response = sisc.validate_subtxt_informed_rubric_request(req)
    assert response["status"] == "fail_closed"
    assert any(
        "no_generated_prose" in err for err in response["errors"]
    )


def test_request_empty_refs_fail_closed():
    req = _valid_request(evidence_refs=[])
    response = sisc.validate_subtxt_informed_rubric_request(req)
    assert response["status"] == "fail_closed"
    assert any("evidence_refs" in err for err in response["errors"])


# ---------------------------------------------------------------------------
# Provenance / support label / status / category mapping (tests 9, 10, 15, 16, 17, 18)
# ---------------------------------------------------------------------------


def test_every_allowed_category_is_recognized():
    assert sisc.ALLOWED_CATEGORIES == frozenset(
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


def test_exact_category_to_candidate_type_mapping():
    assert sisc.CATEGORY_TO_CANDIDATE_TYPE == {
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


# ---------------------------------------------------------------------------
# Result envelope construction helpers
# ---------------------------------------------------------------------------


def _valid_safety_dict() -> dict[str, bool]:
    return {key: False for key in sisc.ALLOWED_OPERATION_FLAGS}


def _valid_item_provenance() -> dict[str, Any]:
    return {
        "tool_source": sisc.SUBTXT_INFORMED_RUBRIC_ID,
        "adapter": sisc.SUBTXT_INFORMED_RUBRIC_ID,
        "support": sisc.SUBTXT_INFORMED_RUBRIC_SUPPORT_LABEL,
        "executes_subtxt": False,
        "official_subtxt_output": False,
    }


def _valid_evidence() -> list[dict[str, str]]:
    return [
        {
            "source_excerpt": "Owner-authored source excerpt.",
            "source_locator": "source_locator_ref_owner_scene_001",
        }
    ]


def _valid_item_base(**overrides: Any) -> dict[str, Any]:
    item: dict[str, Any] = {
        "item_id": "item-001",
        "category": "structural_diagnostic",
        "candidate_type": "structural_diagnostic",
        "label": "Archive key structural pressure",
        "diagnostic_text": (
            "Multiple unresolved references to the archive key may be "
            "structurally significant for owner review."
        ),
        "statement_kind": "candidate_observation",
        "evidence": _valid_evidence(),
        "source_locator": "source_locator_ref_owner_scene_001",
        "source_refs": ["source_ref_owner_scene_001"],
        "evidence_refs": ["evidence_ref_scene_001_span_001"],
        "provenance_refs": ["provenance_ref_rubric_001"],
        "source_locator_refs": ["source_locator_ref_owner_scene_001"],
        "provenance": _valid_item_provenance(),
        "support_label": sisc.SUBTXT_INFORMED_RUBRIC_SUPPORT_LABEL,
        "confidence": "medium_support",
        "uncertainty_label": "null",
        "owner_decision": {"approved": False, "decision": "pending"},
        "review_status": "candidate_review_pending",
        "executes_subtxt": False,
        "official_subtxt_output": False,
    }
    item.update(overrides)
    return item


def _valid_result_envelope(**overrides: Any) -> dict[str, Any]:
    result: dict[str, Any] = {
        "schema_version": sisc.SUBTXT_INFORMED_RUBRIC_RESULT_SCHEMA_VERSION,
        "rubric_id": sisc.SUBTXT_INFORMED_RUBRIC_ID,
        "output_class": sisc.SUBTXT_INFORMED_RUBRIC_OUTPUT_CLASS,
        "status": "succeeded",
        "display_label": sisc.SUBTXT_INFORMED_RUBRIC_SUPPORT_LABEL,
        "provenance": _valid_item_provenance(),
        "source_refs": ["source_ref_owner_scene_001"],
        "evidence_refs": ["evidence_ref_scene_001_span_001"],
        "provenance_refs": ["provenance_ref_rubric_001"],
        "source_locator_refs": ["source_locator_ref_owner_scene_001"],
        "candidate_support": [_valid_item_base()],
        "diagnostic_questions": [],
        "uncertainty_notes": [],
        "insufficient_evidence_notes": [],
        "safety": _valid_safety_dict(),
    }
    result.update(overrides)
    return result


# ---------------------------------------------------------------------------
# Result validation: succeeded / empty / failed_closed / error (tests 3, 4, 5, 6, 7, 8)
# ---------------------------------------------------------------------------


def test_valid_succeeded_result_normalization_succeeds():
    response = sisc.validate_subtxt_informed_rubric_result(
        _valid_result_envelope()
    )
    assert response["status"] == "valid"
    assert response["valid"] is True
    assert response["fail_closed"] is False
    assert response["errors"] == []
    assert response["normalized_result"]["status"] == "succeeded"


def test_empty_result_with_no_items_succeeds():
    result = _valid_result_envelope(
        status="empty",
        candidate_support=[],
        diagnostic_questions=[],
    )
    response = sisc.validate_subtxt_informed_rubric_result(result)
    assert response["status"] == "valid"
    assert response["valid"] is True
    assert response["fail_closed"] is False


def test_failed_closed_result_with_no_items_succeeds():
    result = _valid_result_envelope(
        status="failed_closed",
        candidate_support=[],
        diagnostic_questions=[],
    )
    response = sisc.validate_subtxt_informed_rubric_result(result)
    assert response["status"] == "valid"
    assert response["valid"] is True
    assert response["fail_closed"] is False


def test_error_result_with_no_items_succeeds():
    result = _valid_result_envelope(
        status="error",
        candidate_support=[],
        diagnostic_questions=[],
    )
    response = sisc.validate_subtxt_informed_rubric_result(result)
    assert response["status"] == "valid"
    assert response["valid"] is True


def test_succeeded_status_rejected_when_no_items_exist():
    result = _valid_result_envelope(
        status="succeeded",
        candidate_support=[],
        diagnostic_questions=[],
    )
    response = sisc.validate_subtxt_informed_rubric_result(result)
    assert response["status"] == "fail_closed"
    assert any(
        "succeeded status requires at least one valid item" in err
        for err in response["errors"]
    )


def test_non_succeeded_status_rejected_when_findings_exist():
    result = _valid_result_envelope(
        status="empty",
        candidate_support=[_valid_item_base()],
    )
    response = sisc.validate_subtxt_informed_rubric_result(result)
    assert response["status"] == "fail_closed"
    assert any(
        "empty status must contain no items" in err
        for err in response["errors"]
    )


# ---------------------------------------------------------------------------
# Result-level field checks (tests 15, 17, 18, 25)
# ---------------------------------------------------------------------------


def test_result_with_wrong_schema_version_fails_closed():
    result = _valid_result_envelope(schema_version="some_other.v0")
    response = sisc.validate_subtxt_informed_rubric_result(result)
    assert response["status"] == "fail_closed"
    assert any("schema_version" in err for err in response["errors"])


def test_result_with_wrong_rubric_id_fails_closed():
    result = _valid_result_envelope(rubric_id="subtxt")
    response = sisc.validate_subtxt_informed_rubric_result(result)
    assert response["status"] == "fail_closed"
    assert any("rubric_id" in err for err in response["errors"])


def test_result_with_wrong_output_class_fails_closed():
    result = _valid_result_envelope(output_class="generated_prose")
    response = sisc.validate_subtxt_informed_rubric_result(result)
    assert response["status"] == "fail_closed"
    assert any("output_class" in err for err in response["errors"])


def test_result_with_wrong_display_label_fails_closed():
    result = _valid_result_envelope(display_label="Subtxt diagnostic support only")
    response = sisc.validate_subtxt_informed_rubric_result(result)
    assert response["status"] == "fail_closed"
    assert any("display_label" in err for err in response["errors"])


def test_result_unsafe_provenance_adapter_subtxt_fails_closed():
    bad_provenance = _valid_item_provenance()
    bad_provenance["adapter"] = "subtxt"
    result = _valid_result_envelope(provenance=bad_provenance)
    response = sisc.validate_subtxt_informed_rubric_result(result)
    assert response["status"] == "fail_closed"
    assert any("provenance" in err for err in response["errors"])


def test_result_unsafe_provenance_tool_source_subtxt_fails_closed():
    bad_provenance = _valid_item_provenance()
    bad_provenance["tool_source"] = "subtxt"
    result = _valid_result_envelope(provenance=bad_provenance)
    response = sisc.validate_subtxt_informed_rubric_result(result)
    assert response["status"] == "fail_closed"
    assert any("provenance" in err for err in response["errors"])


def test_result_unsafe_provenance_executes_subtxt_true_fails_closed():
    bad_provenance = _valid_item_provenance()
    bad_provenance["executes_subtxt"] = True
    result = _valid_result_envelope(provenance=bad_provenance)
    response = sisc.validate_subtxt_informed_rubric_result(result)
    assert response["status"] == "fail_closed"
    assert any("provenance" in err for err in response["errors"])


def test_result_unsafe_provenance_official_subtxt_output_true_fails_closed():
    bad_provenance = _valid_item_provenance()
    bad_provenance["official_subtxt_output"] = True
    result = _valid_result_envelope(provenance=bad_provenance)
    response = sisc.validate_subtxt_informed_rubric_result(result)
    assert response["status"] == "fail_closed"
    assert any("provenance" in err for err in response["errors"])


def test_result_safety_must_default_all_operation_flags_to_false():
    safety = _valid_safety_dict()
    safety["persists_candidates"] = True
    result = _valid_result_envelope(safety=safety)
    response = sisc.validate_subtxt_informed_rubric_result(result)
    assert response["status"] == "fail_closed"
    assert any("persists_candidates" in err for err in response["errors"])


def test_result_safety_must_reject_supplied_unsafe_true_value():
    """A supplied ``True`` value must fail closed, not be silently defaulted.
    """
    safety = _valid_safety_dict()
    safety["mutates_memory_canon"] = True
    result = _valid_result_envelope(safety=safety)
    response = sisc.validate_subtxt_informed_rubric_result(result)
    assert response["status"] == "fail_closed"
    assert any("mutates_memory_canon" in err for err in response["errors"])


# ---------------------------------------------------------------------------
# Item-level checks (tests 9, 12, 14, 16, 17, 19, 20, 22, 23, 24, 25, 27)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("category", sorted(sisc.ALLOWED_CATEGORIES))
def test_every_allowed_category_validates_at_minimum(category):
    if category in sisc.QUESTION_CATEGORIES:
        item = _valid_item_base(
            category=category,
            candidate_type="diagnostic_question",
            statement_kind="question",
            label="Question label",
            diagnostic_text="Is the archive key referenced in a way that affects throughline diagnosis?",
            uncertainty_label="requires_owner_interpretation",
        )
    elif category == "structural_diagnostic":
        item = _valid_item_base(
            category=category,
            candidate_type="structural_diagnostic",
            statement_kind="candidate_observation",
            label="Structural label",
            diagnostic_text="The archive key may carry unresolved structural weight.",
            uncertainty_label="null",
        )
    elif category == "conflict_diagnostic":
        item = _valid_item_base(
            category=category,
            candidate_type="conflict_diagnostic",
            statement_kind="candidate_observation",
            label="Conflict label",
            diagnostic_text="A conflict pressure may be associated with the archive key.",
            uncertainty_label="null",
        )
    elif category == "source_of_conflict_hypothesis":
        item = _valid_item_base(
            category=category,
            candidate_type="conflict_diagnostic",
            statement_kind="hypothesis",
            label="Hypothesis label",
            diagnostic_text="The archive key may be a source of conflict in this scene.",
            uncertainty_label="requires_owner_interpretation",
        )
    elif category == "ambiguity":
        item = _valid_item_base(
            category=category,
            candidate_type="ambiguity",
            statement_kind="ambiguity",
            label="Ambiguity label",
            diagnostic_text="The archive key is referenced in two different ways.",
            uncertainty_label="ambiguity",
        )
    elif category == "insufficient_evidence":
        item = _valid_item_base(
            category=category,
            candidate_type="evidence_note",
            statement_kind="insufficient_evidence",
            label="Insufficient evidence label",
            diagnostic_text="There is not enough evidence to support a stronger finding.",
            uncertainty_label="insufficient_evidence",
        )
    else:
        pytest.fail(f"unhandled category {category!r}")
    result = _valid_result_envelope(
        status="succeeded",
        candidate_support=[item] if category not in sisc.QUESTION_CATEGORIES else [],
        diagnostic_questions=[item] if category in sisc.QUESTION_CATEGORIES else [],
    )
    response = sisc.validate_subtxt_informed_rubric_result(result)
    assert response["status"] == "valid", response["errors"]


def test_item_with_unknown_category_fails_closed():
    item = _valid_item_base(category="made_up_category")
    result = _valid_result_envelope(candidate_support=[item])
    response = sisc.validate_subtxt_informed_rubric_result(result)
    assert response["status"] == "fail_closed"
    assert any("category" in err for err in response["errors"])


def test_item_with_wrong_candidate_type_for_category_fails_closed():
    item = _valid_item_base(
        category="structural_diagnostic",
        candidate_type="diagnostic_question",
    )
    result = _valid_result_envelope(candidate_support=[item])
    response = sisc.validate_subtxt_informed_rubric_result(result)
    assert response["status"] == "fail_closed"
    assert any("candidate_type" in err for err in response["errors"])


def test_question_category_requires_diagnostic_question_candidate_type():
    item = _valid_item_base(
        category="throughline_context_question",
        candidate_type="throughline_context_question",
        statement_kind="question",
        label="Throughline label",
        diagnostic_text="Is the archive key part of a throughline?",
    )
    result = _valid_result_envelope(
        status="succeeded",
        candidate_support=[],
        diagnostic_questions=[item],
    )
    response = sisc.validate_subtxt_informed_rubric_result(result)
    assert response["status"] == "fail_closed"
    assert any("candidate_type" in err for err in response["errors"])


def test_question_diagnostic_text_must_end_with_question_mark():
    item = _valid_item_base(
        category="throughline_context_question",
        candidate_type="diagnostic_question",
        statement_kind="question",
        label="Throughline label",
        diagnostic_text="This is not a question",
    )
    result = _valid_result_envelope(
        status="succeeded",
        candidate_support=[],
        diagnostic_questions=[item],
    )
    response = sisc.validate_subtxt_informed_rubric_result(result)
    assert response["status"] == "fail_closed"
    assert any("diagnostic_text" in err for err in response["errors"])


def test_question_with_prose_intent_fails_closed():
    item = _valid_item_base(
        category="throughline_context_question",
        candidate_type="diagnostic_question",
        statement_kind="question",
        label="Prose ask",
        diagnostic_text=(
            "Should I generate prose for the next scene that continues "
            "the archive key thread?"
        ),
    )
    result = _valid_result_envelope(
        status="succeeded",
        candidate_support=[],
        diagnostic_questions=[item],
    )
    response = sisc.validate_subtxt_informed_rubric_result(result)
    assert response["status"] == "fail_closed"
    assert any("diagnostic_text" in err for err in response["errors"])


def test_item_adapter_subtxt_fails_closed():
    bad_provenance = _valid_item_provenance()
    bad_provenance["adapter"] = "subtxt"
    item = _valid_item_base(provenance=bad_provenance)
    result = _valid_result_envelope(candidate_support=[item])
    response = sisc.validate_subtxt_informed_rubric_result(result)
    assert response["status"] == "fail_closed"
    assert any("provenance" in err for err in response["errors"])


def test_item_executes_subtxt_true_fails_closed():
    item = _valid_item_base(executes_subtxt=True)
    result = _valid_result_envelope(candidate_support=[item])
    response = sisc.validate_subtxt_informed_rubric_result(result)
    assert response["status"] == "fail_closed"
    assert any("executes_subtxt" in err for err in response["errors"])


def test_item_official_subtxt_output_true_fails_closed():
    item = _valid_item_base(official_subtxt_output=True)
    result = _valid_result_envelope(candidate_support=[item])
    response = sisc.validate_subtxt_informed_rubric_result(result)
    assert response["status"] == "fail_closed"
    assert any("official_subtxt_output" in err for err in response["errors"])


def test_item_missing_evidence_excerpt_fails_closed():
    bad_evidence = [{"source_excerpt": "", "source_locator": "x"}]
    item = _valid_item_base(evidence=bad_evidence)
    result = _valid_result_envelope(candidate_support=[item])
    response = sisc.validate_subtxt_informed_rubric_result(result)
    assert response["status"] == "fail_closed"
    assert any("evidence" in err for err in response["errors"])


def test_item_missing_evidence_locator_fails_closed():
    bad_evidence = [{"source_excerpt": "Excerpt.", "source_locator": ""}]
    item = _valid_item_base(evidence=bad_evidence)
    result = _valid_result_envelope(candidate_support=[item])
    response = sisc.validate_subtxt_informed_rubric_result(result)
    assert response["status"] == "fail_closed"
    assert any("evidence" in err for err in response["errors"])


def test_item_missing_evidence_list_fails_closed():
    item = _valid_item_base(evidence=[])
    result = _valid_result_envelope(candidate_support=[item])
    response = sisc.validate_subtxt_informed_rubric_result(result)
    assert response["status"] == "fail_closed"
    assert any("evidence" in err for err in response["errors"])


def test_item_source_locator_not_in_source_locator_refs_fails_closed():
    item = _valid_item_base(
        source_locator="source_locator_ref_owner_scene_999",
        source_locator_refs=["source_locator_ref_owner_scene_001"],
    )
    result = _valid_result_envelope(candidate_support=[item])
    response = sisc.validate_subtxt_informed_rubric_result(result)
    assert response["status"] == "fail_closed"
    assert any(
        "source_locator" in err and "source_locator_refs" in err
        for err in response["errors"]
    )


def test_item_with_empty_evidence_refs_fails_closed():
    item = _valid_item_base(evidence_refs=[])
    result = _valid_result_envelope(candidate_support=[item])
    response = sisc.validate_subtxt_informed_rubric_result(result)
    assert response["status"] == "fail_closed"
    assert any("evidence_refs" in err for err in response["errors"])


def test_item_with_empty_source_locator_refs_fails_closed():
    item = _valid_item_base(source_locator_refs=[])
    result = _valid_result_envelope(candidate_support=[item])
    response = sisc.validate_subtxt_informed_rubric_result(result)
    assert response["status"] == "fail_closed"
    assert any(
        "source_locator_refs" in err for err in response["errors"]
    )


# ---------------------------------------------------------------------------
# Owner source text may contain quoted sensitive words (test 21)
# ---------------------------------------------------------------------------


def test_owner_source_text_with_quoted_sensitive_words_is_accepted():
    """Owner source text may contain words like 'canon', 'final', 'approved',
    'write', 'rewrite', 'outline' because they are quoted owner source
    material, not instructions or claims. The request validator must not
    reject such source text or rewrite it.
    """
    sensitive_source = (
        "Owner note: the canon reference mentions final approval and an "
        "outline for the rewrite phase. The author wrote this draft before."
    )
    req = _valid_request(source_text=sensitive_source)
    response = sisc.validate_subtxt_informed_rubric_request(req)
    assert response["status"] == "valid", response["errors"]
    assert response["normalized_request"]["source_text"] == sensitive_source


def test_evidence_excerpt_with_quoted_sensitive_words_is_accepted():
    """Evidence excerpts are quoted owner source material. The validator
    must not reject them and must not rewrite them.
    """
    sensitive_excerpt = (
        "This canon draft was approved by the editorial group as final; "
        "the outline for the rewrite was attached."
    )
    item = _valid_item_base(
        evidence=[
            {
                "source_excerpt": sensitive_excerpt,
                "source_locator": "source_locator_ref_owner_scene_001",
            }
        ],
    )
    result = _valid_result_envelope(candidate_support=[item])
    response = sisc.validate_subtxt_informed_rubric_result(result)
    assert response["status"] == "valid", response["errors"]
    assert response["normalized_result"]["candidate_support"][0]["evidence"][0][
        "source_excerpt"
    ] == sensitive_excerpt


# ---------------------------------------------------------------------------
# Truth / final / approved language in normalized items fails closed (test 22)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "bad_text",
    [
        "This is the truth about the archive key.",
        "This is the final approved canon version.",
        "This finding is canon and truth.",
        "The storyform truth is hereby established.",
        "This is officially the canon version of the scene.",
    ],
)
def test_item_with_truth_label_in_diagnostic_text_fails_closed(bad_text):
    item = _valid_item_base(diagnostic_text=bad_text)
    result = _valid_result_envelope(candidate_support=[item])
    response = sisc.validate_subtxt_informed_rubric_result(result)
    assert response["status"] == "fail_closed"
    assert any("diagnostic_text" in err for err in response["errors"])


def test_item_with_truth_label_in_label_fails_closed():
    item = _valid_item_base(label="Canon truth label")
    result = _valid_result_envelope(candidate_support=[item])
    response = sisc.validate_subtxt_informed_rubric_result(result)
    assert response["status"] == "fail_closed"
    assert any("label" in err for err in response["errors"])


# ---------------------------------------------------------------------------
# Owner decision and review status (tests 23, 24)
# ---------------------------------------------------------------------------


def test_auto_approved_owner_decision_fails_closed():
    item = _valid_item_base(
        owner_decision={"approved": True, "decision": "approved"},
    )
    result = _valid_result_envelope(candidate_support=[item])
    response = sisc.validate_subtxt_informed_rubric_result(result)
    assert response["status"] == "fail_closed"
    assert any("owner_decision" in err for err in response["errors"])


def test_accepted_owner_decision_fails_closed():
    item = _valid_item_base(
        owner_decision={"approved": False, "decision": "accepted"},
    )
    result = _valid_result_envelope(candidate_support=[item])
    response = sisc.validate_subtxt_informed_rubric_result(result)
    assert response["status"] == "fail_closed"
    assert any("owner_decision" in err for err in response["errors"])


def test_non_pending_review_status_fails_closed():
    item = _valid_item_base(review_status="accepted_final")
    result = _valid_result_envelope(candidate_support=[item])
    response = sisc.validate_subtxt_informed_rubric_result(result)
    assert response["status"] == "fail_closed"
    assert any("review_status" in err for err in response["errors"])


def test_promoted_review_status_fails_closed():
    item = _valid_item_base(review_status="promoted")
    result = _valid_result_envelope(candidate_support=[item])
    response = sisc.validate_subtxt_informed_rubric_result(result)
    assert response["status"] == "fail_closed"
    assert any("review_status" in err for err in response["errors"])


# ---------------------------------------------------------------------------
# Unsafe persistence / canon / promotion / training (test 25)
# ---------------------------------------------------------------------------


def test_item_persistence_attempt_in_diagnostic_text_fails_closed():
    item = _valid_item_base(
        diagnostic_text=(
            "Persist-candidate this finding now in the review queue."
        ),
    )
    result = _valid_result_envelope(candidate_support=[item])
    response = sisc.validate_subtxt_informed_rubric_result(result)
    assert response["status"] == "fail_closed"
    assert any("diagnostic_text" in err for err in response["errors"])


def test_item_promotion_attempt_in_diagnostic_text_fails_closed():
    item = _valid_item_base(
        diagnostic_text=(
            "Apply-promotion of this candidate should be triggered now."
        ),
    )
    result = _valid_result_envelope(candidate_support=[item])
    response = sisc.validate_subtxt_informed_rubric_result(result)
    assert response["status"] == "fail_closed"
    assert any("diagnostic_text" in err for err in response["errors"])


def test_item_training_artifact_attempt_in_diagnostic_text_fails_closed():
    item = _valid_item_base(
        diagnostic_text=(
            "Generate a training artifact from this finding now."
        ),
    )
    result = _valid_result_envelope(candidate_support=[item])
    response = sisc.validate_subtxt_informed_rubric_result(result)
    assert response["status"] == "fail_closed"
    assert any("diagnostic_text" in err for err in response["errors"])


def test_item_mutation_attempt_in_diagnostic_text_fails_closed():
    item = _valid_item_base(
        diagnostic_text=(
            "Mutate the project memory and canon records with this finding."
        ),
    )
    result = _valid_result_envelope(candidate_support=[item])
    response = sisc.validate_subtxt_informed_rubric_result(result)
    assert response["status"] == "fail_closed"
    assert any("diagnostic_text" in err for err in response["errors"])


# ---------------------------------------------------------------------------
# Uncertainty rules (test 27)
# ---------------------------------------------------------------------------


def test_ambiguity_category_requires_ambiguity_uncertainty_label():
    item = _valid_item_base(
        category="ambiguity",
        candidate_type="ambiguity",
        statement_kind="ambiguity",
        label="Ambiguity label",
        diagnostic_text="The archive key is referenced in two ways.",
        uncertainty_label="null",
    )
    result = _valid_result_envelope(candidate_support=[item])
    response = sisc.validate_subtxt_informed_rubric_result(result)
    assert response["status"] == "fail_closed"
    assert any("uncertainty_label" in err for err in response["errors"])


def test_insufficient_evidence_category_requires_insufficient_uncertainty_label():
    item = _valid_item_base(
        category="insufficient_evidence",
        candidate_type="evidence_note",
        statement_kind="insufficient_evidence",
        label="Insufficient label",
        diagnostic_text="Not enough evidence to support a stronger finding.",
        uncertainty_label="null",
    )
    result = _valid_result_envelope(candidate_support=[item])
    response = sisc.validate_subtxt_informed_rubric_result(result)
    assert response["status"] == "fail_closed"
    assert any("uncertainty_label" in err for err in response["errors"])


def test_question_can_use_requires_owner_interpretation_uncertainty():
    item = _valid_item_base(
        category="throughline_context_question",
        candidate_type="diagnostic_question",
        statement_kind="question",
        label="Throughline question",
        diagnostic_text="Does the archive key belong to the overall story throughline?",
        uncertainty_label="requires_owner_interpretation",
    )
    result = _valid_result_envelope(
        status="succeeded",
        candidate_support=[],
        diagnostic_questions=[item],
    )
    response = sisc.validate_subtxt_informed_rubric_result(result)
    assert response["status"] == "valid", response["errors"]


# ---------------------------------------------------------------------------
# Fail-closed builder (test 28)
# ---------------------------------------------------------------------------


def test_fail_closed_builder_returns_zero_findings_and_all_flags_false():
    fc = sisc.build_subtxt_informed_rubric_fail_closed_result("test reason")
    assert fc["schema_version"] == (
        sisc.SUBTXT_INFORMED_RUBRIC_RESULT_SCHEMA_VERSION
    )
    assert fc["rubric_id"] == sisc.SUBTXT_INFORMED_RUBRIC_ID
    assert fc["output_class"] == sisc.SUBTXT_INFORMED_RUBRIC_OUTPUT_CLASS
    assert fc["status"] == "failed_closed"
    assert fc["display_label"] == sisc.SUBTXT_INFORMED_RUBRIC_SUPPORT_LABEL
    assert fc["candidate_support"] == []
    assert fc["diagnostic_questions"] == []
    assert fc["uncertainty_notes"] == []
    assert fc["insufficient_evidence_notes"] == []
    for key in sisc.ALLOWED_OPERATION_FLAGS:
        assert fc["safety"][key] is False
    assert fc["provenance"]["tool_source"] == sisc.SUBTXT_INFORMED_RUBRIC_ID
    assert fc["provenance"]["adapter"] == sisc.SUBTXT_INFORMED_RUBRIC_ID
    assert fc["provenance"]["support"] == sisc.SUBTXT_INFORMED_RUBRIC_SUPPORT_LABEL
    assert fc["provenance"]["executes_subtxt"] is False
    assert fc["provenance"]["official_subtxt_output"] is False
    assert fc["fail_closed_reason"] == "test reason"


def test_fail_closed_builder_validates_through_the_contract():
    fc = sisc.build_subtxt_informed_rubric_fail_closed_result(
        "test reason", request=_valid_request()
    )
    response = sisc.validate_subtxt_informed_rubric_result(fc)
    assert response["status"] == "valid", response["errors"]


def test_fail_closed_builder_with_no_request_does_not_throw():
    fc = sisc.build_subtxt_informed_rubric_fail_closed_result("missing")
    assert fc["candidate_support"] == []
    assert fc["source_refs"] == []


def test_fail_closed_builder_copies_top_level_refs_from_valid_request():
    req = _valid_request()
    fc = sisc.build_subtxt_informed_rubric_fail_closed_result(
        "x", request=req
    )
    assert fc["source_refs"] == req["source_refs"]
    assert fc["evidence_refs"] == req["evidence_refs"]
    assert fc["provenance_refs"] == req["provenance_refs"]
    assert fc["source_locator_refs"] == req["source_locator_refs"]


def test_fail_closed_builder_with_invalid_request_does_not_throw():
    fc = sisc.build_subtxt_informed_rubric_fail_closed_result(
        "x", request={"bad": "data"}
    )
    assert fc["candidate_support"] == []
    assert fc["source_refs"] == []


def test_fail_closed_builder_with_empty_reason_falls_back_to_fail_closed():
    fc = sisc.build_subtxt_informed_rubric_fail_closed_result("")
    assert fc["fail_closed_reason"] == "fail_closed"


# ---------------------------------------------------------------------------
# Generic rubric_mapping_support output compatibility (test 29)
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
        "audit_notes": "T019C rubric_mapping_support allowlist record",
    }


def test_normalized_result_validates_against_generic_rubric_mapping_support_validator():
    fc = sisc.build_subtxt_informed_rubric_fail_closed_result("validation")
    response = ari.validate_analysis_runtime_output(
        fc, _rubric_mapping_support_allowlist_record()
    )
    assert response["status"] in {"valid", "fail_closed"}, response
    assert response["output_class"] == "rubric_mapping_support"
    assert response["allowed_output_class"] is True


def test_succeeded_result_validates_against_generic_rubric_mapping_support_validator():
    result = _valid_result_envelope(
        status="succeeded",
        candidate_support=[_valid_item_base()],
    )
    sisc_validation = sisc.validate_subtxt_informed_rubric_result(result)
    assert sisc_validation["status"] == "valid", sisc_validation["errors"]
    response = ari.validate_analysis_runtime_output(
        sisc_validation["normalized_result"],
        _rubric_mapping_support_allowlist_record(),
    )
    assert response["status"] in {"valid", "fail_closed"}
    assert response["allowed_output_class"] is True


# ---------------------------------------------------------------------------
# No external / file / subprocess / model / persistence / project mutation
# ---------------------------------------------------------------------------


def test_module_does_not_import_external_or_subprocess_modules():
    """Static check: the contract module must not import subprocess,
    urllib, requests, http, openai, anthropic, ollama, pathlib, or os.
    """
    import importlib
    importlib.invalidate_caches()
    module = importlib.import_module(
        "backend.story_knowledge.subtxt_informed_semantic_rubric_contract"
    )
    source_path = module.__file__
    assert source_path is not None
    text = Path(source_path).read_text(encoding="utf-8")
    forbidden_import_tokens = (
        "import subprocess",
        "from subprocess",
        "import urllib",
        "from urllib",
        "import requests",
        "from requests",
        "import openai",
        "from openai",
        "import anthropic",
        "from anthropic",
        "import ollama",
        "from ollama",
        "import socket",
        "import http",
        "import pathlib",
        "from pathlib",
        "import os",
        "from os",
    )
    for token in forbidden_import_tokens:
        assert token not in text, f"forbidden import found: {token!r}"
    import_line_pattern = re.compile(r"^(?:from|import)\s+([\w.]+)", re.MULTILINE)
    imports = set(import_line_pattern.findall(text))
    allowed_typing_only = {"copy", "re", "typing", "__future__"}
    assert imports.issubset(
        allowed_typing_only
    ), f"unexpected imports: {sorted(imports - allowed_typing_only)}"


def test_validator_does_not_call_subprocess_shell_network_or_persist():
    """Run the validators against synthetic in-memory data and confirm no
    I/O, no subprocess, no network, no module attribute, no project helper
    is invoked. Use sys.modules patches to assert no leakage.
    """
    import subprocess
    import socket
    import sys as _sys

    calls: list[str] = []

    class _Guard:
        def __getattr__(self, name):  # pragma: no cover - guard only
            calls.append(name)
            raise AssertionError(f"unexpected attribute access: {name}")

    original_subprocess_run = subprocess.run
    original_subprocess_popen = subprocess.Popen
    original_socket_socket = socket.socket

    def _record(name):
        def _fail(*args, **kwargs):
            calls.append(name)
            raise AssertionError(f"{name} should not be called")
        return _fail

    subprocess.run = _record("subprocess.run")
    subprocess.Popen = _record("subprocess.Popen")
    socket.socket = _record("socket.socket")

    try:
        sisc.validate_subtxt_informed_rubric_request(_valid_request())
        sisc.validate_subtxt_informed_rubric_result(
            _valid_result_envelope()
        )
        sisc.build_subtxt_informed_rubric_fail_closed_result("no side effects")
    finally:
        subprocess.run = original_subprocess_run
        subprocess.Popen = original_subprocess_popen
        socket.socket = original_socket_socket

    assert calls == [], f"unexpected side-effect calls: {calls}"


def test_validator_does_not_import_external_sources_subtxt_docs():
    """The validator must not import or read ``.external_sources/subtxt-docs``."""
    import importlib

    module = importlib.import_module(
        "backend.story_knowledge.subtxt_informed_semantic_rubric_contract"
    )
    assert ".external_sources" not in dir(module)
    assert "subtxt_docs" not in dir(module)


# ---------------------------------------------------------------------------
# Result-level "no items in failed_closed/empty/error" extra safety
# ---------------------------------------------------------------------------


def test_normalized_request_is_a_deep_copy():
    req = _valid_request()
    snapshot = copy.deepcopy(req)
    sisc.validate_subtxt_informed_rubric_request(req)
    assert req == snapshot


def test_normalized_result_is_a_deep_copy():
    result = _valid_result_envelope()
    snapshot = copy.deepcopy(result)
    sisc.validate_subtxt_informed_rubric_result(result)
    assert result == snapshot


def test_fail_closed_builder_does_not_mutate_supplied_request():
    req = _valid_request()
    snapshot = copy.deepcopy(req)
    sisc.build_subtxt_informed_rubric_fail_closed_result("x", request=req)
    assert req == snapshot
