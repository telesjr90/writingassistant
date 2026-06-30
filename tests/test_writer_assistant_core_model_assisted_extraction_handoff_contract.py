"""PHASE8-IMPL-020-T005 model-assisted handoff contract tests.

The handoff APIs are in-memory review support only. They must not persist
candidates, create review queue entries, apply promotion, mutate memory/canon,
create training artifacts, call models/Ollama, or produce story prose.
"""

from __future__ import annotations

from pathlib import Path

import backend.story_knowledge.model_assisted_extraction as model_assisted
from backend.story_knowledge.model_assisted_extraction import (
    build_model_assisted_candidate_observation_handoff,
    build_model_assisted_diagnostic_handoff,
    build_model_assisted_review_handoff,
    validate_model_assisted_review_handoff,
)


SOURCE_REF = "source_ref_owner_scene_001"
EVIDENCE_REF = "evidence_ref_scene_001_span_001"
PROVENANCE_REF = "provenance_ref_model_assisted_001"
SOURCE_LOCATOR_REF = "source_locator_ref_scene_001_chars_001"


EXPECTED_HANDOFF_APIS = (
    "build_model_assisted_review_handoff",
    "validate_model_assisted_review_handoff",
    "build_model_assisted_diagnostic_handoff",
    "build_model_assisted_candidate_observation_handoff",
)


def valid_candidate_output(**overrides):
    output = {
        "output_type": "evidence-backed candidate observation",
        "status": "candidate_support_ready",
        "source_refs": [SOURCE_REF],
        "evidence_refs": [EVIDENCE_REF],
        "provenance_refs": [PROVENANCE_REF],
        "source_locator_refs": [SOURCE_LOCATOR_REF],
        "candidate_support": [
            {
                "candidate_support_id": "candidate_support_001",
                "candidate_type": "character_observation",
                "observation": "Evidence-backed observation for owner review only.",
                "source_refs": [SOURCE_REF],
                "evidence_refs": [EVIDENCE_REF],
                "provenance_refs": [PROVENANCE_REF],
                "source_locator_refs": [SOURCE_LOCATOR_REF],
                "confidence": 0.4,
                "confidence_is_not_truth": True,
                "model_output_is_not_truth": True,
                "model_output_is_not_canon": True,
                "candidate_first": True,
                "owner_review_required": True,
            }
        ],
    }
    output.update(overrides)
    return output


def diagnostic_output(**overrides):
    output = {
        "output_type": "diagnostic question",
        "source_refs": [SOURCE_REF],
        "evidence_refs": [],
        "provenance_refs": [PROVENANCE_REF],
        "source_locator_refs": [SOURCE_LOCATOR_REF],
        "diagnostic_questions": [
            {
                "question": "What evidence would support this interpretation?",
                "source_refs": [SOURCE_REF],
                "provenance_refs": [PROVENANCE_REF],
                "source_locator_refs": [SOURCE_LOCATOR_REF],
            }
        ],
        "uncertainty_notes": ["Evidence is not enough for a truth claim."],
    }
    output.update(overrides)
    return output


def test_t005_handoff_public_api_surface_exists():
    for name in EXPECTED_HANDOFF_APIS:
        assert hasattr(model_assisted, name)
        assert callable(getattr(model_assisted, name))


def test_candidate_handoff_requires_source_evidence_provenance_and_locator_refs():
    handoff = build_model_assisted_candidate_observation_handoff(valid_candidate_output())
    assert handoff["handoff_type"] == "candidate_observation"
    assert handoff["handoff_status"] == "candidate_support_ready"
    assert handoff["candidate_support_ready"] is True
    assert handoff["source_refs"] == [SOURCE_REF]
    assert handoff["evidence_refs"] == [EVIDENCE_REF]
    assert handoff["provenance_refs"] == [PROVENANCE_REF]
    assert handoff["source_locator_refs"] == [SOURCE_LOCATOR_REF]
    assert handoff["candidate_first"] is True
    assert handoff["owner_review_required"] is True
    assert handoff["confidence_is_not_truth"] is True
    assert handoff["model_output_is_not_truth"] is True
    assert handoff["model_output_is_not_canon"] is True


def test_missing_evidence_becomes_insufficient_and_not_candidate_truth():
    output = valid_candidate_output(evidence_refs=[])
    output["candidate_support"][0]["evidence_refs"] = []
    handoff = build_model_assisted_candidate_observation_handoff(output)
    assert handoff["handoff_status"] in {"evidence_insufficient", "fail_closed"}
    assert handoff["candidate_support_ready"] is False
    assert handoff["evidence_insufficient"] is True
    assert handoff["fail_closed"] is True
    assert handoff["treat_as_candidate_truth"] is False
    assert handoff["candidate_truth_claim"] is False
    assert handoff["not_canon"] is True
    assert handoff["not_approved_memory"] is True


def test_candidate_handoff_preserves_blocker_refs_when_locator_is_missing():
    output = valid_candidate_output(source_locator_refs=[])
    output["candidate_support"][0]["source_locator_refs"] = []
    handoff = build_model_assisted_candidate_observation_handoff(output)
    assert handoff["handoff_status"] in {"evidence_insufficient", "fail_closed"}
    assert handoff["source_refs"] == [SOURCE_REF]
    assert handoff["evidence_refs"] == [EVIDENCE_REF]
    assert handoff["provenance_refs"] == [PROVENANCE_REF]
    assert handoff["source_locator_refs"] == []
    assert "missing_source_locator_refs" in handoff["owner_review_blockers"]


def test_diagnostic_fallback_creates_questions_without_prose_generation():
    handoff = build_model_assisted_diagnostic_handoff(diagnostic_output())
    assert handoff["handoff_type"] == "diagnostic"
    assert handoff["handoff_status"] == "diagnostic_questions_ready"
    assert handoff["diagnostic_questions_ready"] is True
    assert handoff["candidate_support_ready"] is False
    assert handoff["uncertainty_note"] is True
    assert handoff["insufficient_evidence_note"] is False
    for forbidden in ("rewrite", "continuation", "outline", "draft", "polish", "story_prose"):
        assert handoff[forbidden] is False


def test_refused_prose_request_becomes_refused_no_prose_or_blocked_request():
    handoff = build_model_assisted_diagnostic_handoff(
        diagnostic_output(user_intent="Please rewrite this chapter as story prose.")
    )
    assert handoff["handoff_status"] in {"refused_no_prose", "blocked_request", "fail_closed"}
    assert handoff["refused_no_prose"] is True
    assert handoff["blocked_request"] is True
    assert handoff["generated_prose"] is False
    assert handoff["rewritten_prose"] is False
    assert handoff["no_generated_prose"] is True


def test_review_handoff_is_in_memory_only_and_not_persistence():
    handoff = build_model_assisted_review_handoff(valid_candidate_output(), diagnostic_output())
    assert handoff["handoff_type"] == "review"
    assert handoff["in_memory_only"] is True
    assert handoff["side_effect_free"] is True
    assert handoff["writes_files"] is False
    assert handoff["creates_candidate_records"] is False
    assert handoff["creates_review_queue_entries"] is False
    assert handoff["candidate_record_written"] is False
    assert handoff["review_queue_entry_written"] is False
    assert handoff["apply_promotion_performed"] is False
    assert handoff["memory_canon_mutated"] is False
    assert handoff["training_artifact_created"] is False
    assert handoff["model_call_performed"] is False


def test_review_handoff_boundary_notes_are_explicit():
    handoff = build_model_assisted_review_handoff(valid_candidate_output(), diagnostic_output())
    assert handoff["queue_presence_is_approval"] is False
    assert handoff["candidate_persistence_is_canon"] is False
    assert handoff["queue_boundary_note"] == "queue presence is not approval"
    assert handoff["candidate_persistence_boundary_note"] == "candidate persistence is not canon"
    assert "separate explicit owner-confirmed path" in handoff["apply_promotion_boundary_note"]
    assert handoff["confidence_is_not_truth"] is True
    assert handoff["model_output_is_not_truth"] is True
    assert handoff["no_model_output_as_truth"] is True
    assert handoff["no_automatic_canon"] is True


def test_review_handoff_preserves_refs_from_candidate_and_diagnostic_support():
    handoff = build_model_assisted_review_handoff(valid_candidate_output(), diagnostic_output())
    assert handoff["source_refs"] == [SOURCE_REF]
    assert handoff["evidence_refs"] == [EVIDENCE_REF]
    assert handoff["provenance_refs"] == [PROVENANCE_REF]
    assert handoff["source_locator_refs"] == [SOURCE_LOCATOR_REF]
    assert handoff["candidate_handoff"]["source_refs"] == [SOURCE_REF]
    assert handoff["diagnostic_handoff"]["source_locator_refs"] == [SOURCE_LOCATOR_REF]


def test_review_handoff_validation_fails_closed_without_silent_fallback():
    handoff = build_model_assisted_review_handoff(valid_candidate_output(), diagnostic_output())
    validation = validate_model_assisted_review_handoff(handoff)
    assert validation["handoff_valid"] is True
    assert validation["status"] == "valid"
    assert validation["no_silent_fallback"] is True

    broken = dict(handoff)
    broken.pop("handoff_status")
    invalid = validate_model_assisted_review_handoff(broken)
    assert invalid["handoff_valid"] is False
    assert invalid["status"] == "fail_closed"
    assert "handoff_status" in invalid["missing_handoff_fields"]


def test_handoff_source_has_no_persistence_or_model_call_markers():
    source = Path(model_assisted.__file__).read_text(encoding="utf-8")
    forbidden_runtime_markers = (
        "requests.post",
        "httpx",
        "urllib.request",
        "subprocess",
        "write_candidate_record(",
        "write_review_queue_entry(",
        "apply_promotion(",
    )
    for marker in forbidden_runtime_markers:
        assert marker not in source
