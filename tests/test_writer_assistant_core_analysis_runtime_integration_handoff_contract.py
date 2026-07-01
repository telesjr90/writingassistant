"""Focused PHASE8-IMPL-021-T005 handoff contract tests.

These tests cover in-memory evidence-backed handoffs only. They do not execute
NCP, Subtxt, dramatica-flow, network, subprocess, models, Ollama, persistence,
review queue creation, apply-promotion, memory/canon mutation, training
artifacts, generated prose, rewrite, continuation, outline, draft, revision,
polish, expansion, style imitation, export-as-prose, chapter prose, or story
prose behavior.
"""

from __future__ import annotations

import copy

import pytest

from backend.story_knowledge.analysis_runtime_integration import (
    build_analysis_runtime_candidate_observation_handoff,
    build_analysis_runtime_diagnostic_handoff,
    build_analysis_runtime_review_handoff,
    validate_analysis_runtime_review_handoff,
)


SOURCE_REF = "source_ref_owner_scene_001"
EVIDENCE_REF = "evidence_ref_scene_001_span_001"
PROVENANCE_REF = "provenance_ref_analysis_runtime_001"
SOURCE_LOCATOR_REF = "source_locator_ref_scene_001_chars_001"

EXPECTED_HANDOFF_API = (
    "build_analysis_runtime_candidate_observation_handoff",
    "build_analysis_runtime_diagnostic_handoff",
    "build_analysis_runtime_review_handoff",
    "validate_analysis_runtime_review_handoff",
)

FORBIDDEN_PROSE_INTENTS = (
    "generate prose for the next scene",
    "rewrite this chapter",
    "continue the passage",
    "make an outline",
    "draft the ending",
    "revise the scene",
    "polish the dialogue",
    "expand the paragraph",
    "imitate this style",
    "export as prose",
    "write story prose",
)


def valid_candidate_output(**overrides):
    output = {
        "output_class": "evidence_backed_candidate_observation",
        "status": "candidate_support_ready",
        "source_refs": [SOURCE_REF],
        "evidence_refs": [EVIDENCE_REF],
        "provenance_refs": [PROVENANCE_REF],
        "source_locator_refs": [SOURCE_LOCATOR_REF],
        "candidate_observations": [
            {
                "candidate_observation_id": "candidate_observation_001",
                "claim": "Evidence-backed candidate observation.",
                "source_refs": [SOURCE_REF],
                "evidence_refs": [EVIDENCE_REF],
                "provenance_refs": [PROVENANCE_REF],
                "source_locator_refs": [SOURCE_LOCATOR_REF],
                "confidence": 0.42,
                "candidate_first": True,
                "owner_review_required": True,
                "confidence_is_not_truth": True,
                "tool_output_is_not_canon": True,
                "tool_output_is_not_truth": True,
            }
        ],
    }
    output.update(overrides)
    return output


def valid_diagnostic_output(**overrides):
    output = {
        "output_class": "diagnostic_question",
        "status": "diagnostic_questions_ready",
        "source_refs": [SOURCE_REF],
        "evidence_refs": [EVIDENCE_REF],
        "provenance_refs": [PROVENANCE_REF],
        "source_locator_refs": [SOURCE_LOCATOR_REF],
        "diagnostic_questions": [
            {
                "question": "Which existing source evidence supports this analysis claim?",
                "source_refs": [SOURCE_REF],
                "evidence_refs": [EVIDENCE_REF],
                "provenance_refs": [PROVENANCE_REF],
                "source_locator_refs": [SOURCE_LOCATOR_REF],
            }
        ],
        "uncertainty_notes": [],
        "insufficient_evidence_notes": [],
    }
    output.update(overrides)
    return output


def assert_handoff_boundaries(handoff):
    assert handoff["in_memory_only"] is True
    assert handoff["pure_data_only"] is True
    assert handoff["candidate-first"] is True
    assert handoff["owner review"] is True
    assert handoff["confidence is not truth"] is True
    assert handoff["tool output is not canon"] is True
    assert handoff["tool output is not truth"] is True
    assert handoff["no automatic canon"] is True
    assert handoff["no apply-promotion"] is True
    assert handoff["no memory/canon mutation"] is True
    assert handoff["no training artifacts"] is True
    assert handoff["no generated prose"] is True
    assert handoff["fail closed"] is True
    assert handoff["no silent fallback"] is True
    assert handoff["queue presence is not approval"] is True
    assert handoff["candidate persistence is not canon"] is True
    assert handoff["persists_candidates"] is False
    assert handoff["creates_candidate_records"] is False
    assert handoff["creates_review_queue_entries"] is False
    assert handoff["applies_promotion"] is False
    assert handoff["memory_canon_write"] is False
    assert handoff["approved_memory_write"] is False
    assert handoff["canon_write"] is False
    assert handoff["mutates_memory_canon"] is False
    assert handoff["creates_training_artifacts"] is False
    assert handoff["training_artifact_created"] is False
    assert handoff["generates_prose"] is False
    assert handoff["executes_ncp"] is False
    assert handoff["executes_subtxt"] is False
    assert handoff["executes_dramatica_flow"] is False
    assert handoff["calls_network"] is False
    assert handoff["calls_subprocess"] is False
    assert handoff["calls_models_or_ollama"] is False


def test_handoff_public_api_surface_is_available():
    api = {
        "build_analysis_runtime_candidate_observation_handoff": (
            build_analysis_runtime_candidate_observation_handoff
        ),
        "build_analysis_runtime_diagnostic_handoff": build_analysis_runtime_diagnostic_handoff,
        "build_analysis_runtime_review_handoff": build_analysis_runtime_review_handoff,
        "validate_analysis_runtime_review_handoff": validate_analysis_runtime_review_handoff,
    }
    assert tuple(api) == EXPECTED_HANDOFF_API
    assert all(callable(fn) for fn in api.values())


def test_candidate_observation_handoff_succeeds_with_valid_refs_and_preserves_refs():
    handoff = build_analysis_runtime_candidate_observation_handoff(valid_candidate_output())
    assert handoff["status"] == "candidate_support_ready"
    assert handoff["candidate_observation_handoff_ready"] is True
    assert handoff["source_refs"] == [SOURCE_REF]
    assert handoff["evidence_refs"] == [EVIDENCE_REF]
    assert handoff["provenance_refs"] == [PROVENANCE_REF]
    assert handoff["source_locator_refs"] == [SOURCE_LOCATOR_REF]
    assert handoff["candidate_observations"][0]["source_locator_refs"] == [SOURCE_LOCATOR_REF]
    assert_handoff_boundaries(handoff)


@pytest.mark.parametrize(
    ("field", "expected_status"),
    [
        ("source_refs", "missing_source_refs"),
        ("evidence_refs", "missing_evidence_refs"),
        ("provenance_refs", "missing_provenance_refs"),
        ("source_locator_refs", "missing_source_locator_refs"),
    ],
)
def test_candidate_observation_handoff_rejects_missing_refs(field, expected_status):
    output = valid_candidate_output()
    output[field] = []
    output["candidate_observations"][0][field] = []
    handoff = build_analysis_runtime_candidate_observation_handoff(output)
    assert handoff["status"] == expected_status
    assert handoff["fail_closed"] is True
    assert handoff["candidate_observation_handoff_ready"] is False
    assert_handoff_boundaries(handoff)


def test_candidate_observation_handoff_rejects_invalid_source_locator_refs():
    output = valid_candidate_output(source_locator_refs=["ambiguous_locator"])
    output["candidate_observations"][0]["source_locator_refs"] = ["ambiguous_locator"]
    handoff = build_analysis_runtime_candidate_observation_handoff(output)
    assert handoff["status"] == "source_locator_invalid"
    assert handoff["fail_closed"] is True


def test_candidate_observation_handoff_rejects_insufficient_or_quarantined_evidence():
    insufficient = build_analysis_runtime_candidate_observation_handoff(
        valid_candidate_output(candidate_observations=[])
    )
    quarantined = build_analysis_runtime_candidate_observation_handoff(
        valid_candidate_output(status="quarantined")
    )
    assert insufficient["status"] == "evidence_insufficient"
    assert quarantined["status"] == "quarantined"
    assert insufficient["fail_closed"] is True
    assert quarantined["fail_closed"] is True


def test_diagnostic_handoff_succeeds_for_questions_and_preserves_refs():
    handoff = build_analysis_runtime_diagnostic_handoff(valid_diagnostic_output())
    assert handoff["status"] == "diagnostic_questions_ready"
    assert handoff["diagnostic_handoff_ready"] is True
    assert handoff["diagnostic_questions"][0]["source_refs"] == [SOURCE_REF]
    assert handoff["source_refs"] == [SOURCE_REF]
    assert handoff["evidence_refs"] == [EVIDENCE_REF]
    assert handoff["provenance_refs"] == [PROVENANCE_REF]
    assert handoff["source_locator_refs"] == [SOURCE_LOCATOR_REF]
    assert_handoff_boundaries(handoff)


def test_diagnostic_handoff_succeeds_for_insufficient_evidence_notes():
    handoff = build_analysis_runtime_diagnostic_handoff(
        valid_diagnostic_output(
            output_class="insufficient_evidence_note",
            diagnostic_questions=[],
            insufficient_evidence_notes=[
                {
                    "note": "insufficient evidence",
                    "source_refs": [SOURCE_REF],
                    "evidence_refs": [],
                    "provenance_refs": [PROVENANCE_REF],
                    "source_locator_refs": [SOURCE_LOCATOR_REF],
                }
            ],
        )
    )
    assert handoff["status"] == "evidence_insufficient"
    assert handoff["fail_closed"] is True
    assert handoff["diagnostic_handoff_ready"] is True
    assert handoff["insufficient_evidence_notes"]
    assert_handoff_boundaries(handoff)


@pytest.mark.parametrize("intent", FORBIDDEN_PROSE_INTENTS)
def test_diagnostic_handoff_refuses_forbidden_prose_write_revise_export_outline_intents(intent):
    handoff = build_analysis_runtime_diagnostic_handoff(
        valid_diagnostic_output(
            output_class="diagnostic_question",
            diagnostic_questions=[{"question": intent}],
        )
    )
    assert handoff["status"] == "refused_no_prose"
    assert handoff["fail_closed"] is True
    assert handoff["generates_prose"] is False
    assert handoff["rewrites_prose"] is False
    assert handoff["continues_prose"] is False
    assert handoff["creates_outline"] is False


def test_diagnostic_handoff_allows_explicit_refusal_blocked_quarantined_unavailable_states():
    for status in ("refused_no_prose", "blocked_request", "quarantined", "unavailable"):
        handoff = build_analysis_runtime_diagnostic_handoff(
            valid_diagnostic_output(status=status)
        )
        assert handoff["status"] == status
        assert handoff["fail_closed"] is True
        assert handoff["diagnostic_handoff_ready"] is True
        assert_handoff_boundaries(handoff)


def test_review_handoff_aggregates_candidate_and_diagnostic_handoffs_only():
    candidate = build_analysis_runtime_candidate_observation_handoff(valid_candidate_output())
    diagnostic = build_analysis_runtime_diagnostic_handoff(valid_diagnostic_output())
    review = build_analysis_runtime_review_handoff(candidate, [diagnostic])
    assert review["status"] == "valid"
    assert review["review_handoff_ready"] is True
    assert review["candidate_handoffs"] == [candidate]
    assert review["diagnostic_handoffs"] == [diagnostic]
    assert review["source_refs"] == [SOURCE_REF]
    assert review["evidence_refs"] == [EVIDENCE_REF]
    assert review["provenance_refs"] == [PROVENANCE_REF]
    assert review["source_locator_refs"] == [SOURCE_LOCATOR_REF]
    assert_handoff_boundaries(review)


def test_validate_review_handoff_accepts_valid_aggregate_and_rejects_invalid_payload():
    candidate = build_analysis_runtime_candidate_observation_handoff(valid_candidate_output())
    diagnostic = build_analysis_runtime_diagnostic_handoff(valid_diagnostic_output())
    review = build_analysis_runtime_review_handoff([candidate], [diagnostic])
    valid = validate_analysis_runtime_review_handoff(review)
    assert valid["status"] == "valid"
    assert valid["review_handoff_valid"] is True

    invalid = copy.deepcopy(review)
    invalid["candidate_handoffs"] = [{"handoff_type": "review_queue_entry"}]
    rejected = validate_analysis_runtime_review_handoff(invalid)
    assert rejected["status"] == "rejected"
    assert rejected["fail_closed"] is True


def test_review_handoff_validation_rejects_side_effect_flags():
    review = build_analysis_runtime_review_handoff(
        build_analysis_runtime_candidate_observation_handoff(valid_candidate_output()),
        build_analysis_runtime_diagnostic_handoff(valid_diagnostic_output()),
    )
    for key in (
        "persists_candidates",
        "creates_review_queue_entries",
        "applies_promotion",
        "mutates_memory_canon",
        "creates_training_artifacts",
        "generates_prose",
    ):
        mutated = copy.deepcopy(review)
        mutated[key] = True
        result = validate_analysis_runtime_review_handoff(mutated)
        assert result["status"] == "fail_closed"
        assert result["review_handoff_valid"] is False


def test_no_persistence_queue_promotion_canon_training_or_runtime_execution_boundaries():
    candidate = build_analysis_runtime_candidate_observation_handoff(valid_candidate_output())
    diagnostic = build_analysis_runtime_diagnostic_handoff(valid_diagnostic_output())
    review = build_analysis_runtime_review_handoff(candidate, diagnostic)
    for handoff in (candidate, diagnostic, review):
        assert_handoff_boundaries(handoff)
