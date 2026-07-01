"""PHASE8-IMPL-020-T006 model-assisted extraction safety regressions.

The model-assisted helper is pure in-memory analysis support only. It must not
call models/Ollama/network/process APIs, persist candidates, create review queue
entries, apply promotion, mutate approved memory/canon, create training
artifacts, or generate/rewrite/continue/outline/draft/revise/polish/improve/
expand/imitate story prose.
"""

from __future__ import annotations

import builtins
import sys
from pathlib import Path

import pytest

import backend.story_knowledge.candidate_review_gate as candidate_review_gate
import backend.story_knowledge.review_queue_storage as review_queue_storage
from backend.story_knowledge import model_assisted_extraction as model_assisted
from backend.story_knowledge.model_assisted_extraction import (
    build_model_assisted_candidate_observation_handoff,
    build_model_assisted_candidate_support,
    build_model_assisted_diagnostic_handoff,
    build_model_assisted_extraction_prompt_packet,
    build_model_assisted_review_handoff,
    run_guarded_model_assisted_extraction,
    validate_model_assisted_environment,
    validate_model_assisted_extraction_request,
    validate_model_assisted_output,
    validate_model_assisted_review_handoff,
)


SOURCE_REF = "source_ref_owner_scene_001"
EVIDENCE_REF = "evidence_ref_scene_001_span_001"
PROVENANCE_REF = "provenance_ref_owner_material_001"
SOURCE_LOCATOR_REF = "source_locator_ref_scene_001_chars_001"

REQUIRED_BOUNDARY_CONFIRMATIONS = frozenset(
    {
        "owner_authored_or_owner_provided_source_confirmation",
        "raw_source_text_separate_from_user_intent_confirmation",
        "owner-authored prose storage/editing is not model generation",
        "candidate-first",
        "owner-review required",
        "confidence is not truth",
        "model output is not canon",
        "no model output as truth",
        "no automatic canon",
        "no apply-promotion",
        "no memory/canon mutation",
        "no training artifacts",
        "no generated prose",
        "no rewrite",
        "no continuation",
        "no outline",
        "fail closed",
        "no silent fallback",
    }
)

REQUIRED_STATES = {
    "disabled",
    "unavailable",
    "model_unavailable",
    "model_call_blocked",
    "configuration_invalid",
    "request_invalid",
    "unsafe_path",
    "missing_source_refs",
    "missing_evidence_refs",
    "missing_provenance_refs",
    "missing_source_locator_refs",
    "source_locator_invalid",
    "unsupported_output_type",
    "malformed_output",
    "evidence_insufficient",
    "refused_no_prose",
    "quarantined",
    "rejected",
    "candidate_support_ready",
    "diagnostic_questions_ready",
    "valid",
    "fail_closed",
}

FORBIDDEN_OUTPUT_CLASSES = (
    "generated_prose",
    "rewritten_prose",
    "continuation",
    "outline",
    "draft",
    "revision",
    "style_imitation",
    "polish",
    "improvement",
    "expansion",
    "story_prose",
    "model_prompt",
    "model_completion",
    "training_jsonl",
    "dataset_manifest",
    "model_artifact",
    "promotion_record",
    "approved_memory",
    "canon",
    "bible",
    "storyform",
    "scene_mutation",
    "note_mutation",
    "material_mutation",
)

FORBIDDEN_PROMPT_INSTRUCTIONS = (
    "generate prose",
    "rewrite",
    "continue",
    "outline",
    "draft",
    "revise",
    "imitate style",
    "polish",
    "improve",
    "expand",
    "produce story prose",
)

FAIL_CLOSED_STATUSES = {
    "unsafe_path",
    "request_invalid",
    "source_locator_invalid",
    "unsupported_output_type",
    "malformed_output",
    "evidence_insufficient",
    "refused_no_prose",
    "quarantined",
    "rejected",
    "fail_closed",
    "missing_source_refs",
    "missing_evidence_refs",
    "missing_provenance_refs",
    "missing_source_locator_refs",
    "disabled",
    "unavailable",
    "model_unavailable",
    "model_call_blocked",
    "configuration_invalid",
}


def valid_request(**overrides):
    request = {
        "project_id": "example_project",
        "request_id": "model_assisted_extraction_request_001",
        "source_type": "owner-authored scene",
        "source_id": "scene_001",
        "source_path": "scenes/scene_001.md",
        "source_refs": [SOURCE_REF],
        "evidence_refs": [EVIDENCE_REF],
        "provenance_refs": [PROVENANCE_REF],
        "source_locator_refs": [SOURCE_LOCATOR_REF],
        "raw_source_text": "Owner-authored source excerpt for analysis only.",
        "user_intent": "Find evidence-backed candidate observations and diagnostic questions.",
        "boundary_confirmations": sorted(REQUIRED_BOUNDARY_CONFIRMATIONS),
        "requested_by": "owner",
        "created_at": "2026-06-30T00:00:00Z",
    }
    request.update(overrides)
    return request


def valid_output(**overrides):
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
        "diagnostic_questions": [
            {
                "question": "What evidence would support this interpretation?",
                "source_refs": [SOURCE_REF],
                "provenance_refs": [PROVENANCE_REF],
                "source_locator_refs": [SOURCE_LOCATOR_REF],
            }
        ],
        "uncertainty_notes": [],
        "insufficient_evidence_notes": [],
    }
    output.update(overrides)
    return output


def assert_not_truth_or_persistence(result):
    text = str(result).lower()
    assert "confidence is not truth" in text or result.get("confidence_is_not_truth") is True
    assert "model output is not canon" in text or result.get("model_output_is_not_canon") is True
    assert "no model output as truth" in text or result.get("no_model_output_as_truth") is True
    assert result.get("candidate_record_written", False) is False
    assert result.get("review_queue_entry_written", False) is False
    assert result.get("apply_promotion_performed", False) is False
    assert result.get("memory_canon_mutated", False) is False
    assert result.get("training_artifact_created", False) is False


def test_no_model_network_process_or_analysis_engine_execution(monkeypatch):
    imported = []
    original_import = builtins.__import__

    def guarded_import(name, *args, **kwargs):
        root = name.split(".", 1)[0]
        if name == "backend.analysis_engine" or root in {
            "requests",
            "httpx",
            "urllib",
            "subprocess",
            "ollama",
        }:
            imported.append(name)
            raise AssertionError(f"forbidden runtime import: {name}")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded_import)

    for config in (
        {},
        {"model_assistance_enabled": True},
        {"model_assistance_forced_status": "valid"},
        {"model_assistance_forced_status": "model_call_blocked"},
        {"model_assistance_forced_status": "configuration_invalid"},
    ):
        result = run_guarded_model_assisted_extraction(valid_request(), config)
        assert result["model_call_performed"] is False
        assert result["status"] not in {
            "valid",
            "candidate_support_ready",
            "diagnostic_questions_ready",
        }
        assert result["fail_closed"] is True
        assert result["no_silent_fallback"] is True
        assert_not_truth_or_persistence(result)

    assert imported == []
    assert "backend.analysis_engine" not in sys.modules


def test_helper_source_has_no_runtime_or_side_effect_markers():
    source = Path(model_assisted.__file__).read_text(encoding="utf-8")
    for marker in (
        "requests.post",
        "httpx",
        "urllib.request",
        "ollama",
        "analysis_engine",
        "subprocess",
        "write_text(",
        "mkdir(",
        "open(",
        "apply_promotion(",
        "write_candidate_record(",
        "write_review_queue_entry(",
    ):
        assert marker not in source


@pytest.mark.parametrize(
    "source_path",
    (
        "../escape.md",
        "/absolute/scene.md",
        "C:\\absolute\\scene.md",
        "C:/absolute/scene.md",
        "scenes\\scene_001.md",
        "scenes/../../escape.md",
        "scenes//scene.md",
        "scenes/./scene.md",
        ".",
        "..",
        "",
        ".hidden/scene.md",
        "scenes/.../escape.md",
        "scenes/%2e%2e/escape.md",
    ),
)
def test_unsafe_source_paths_fail_closed_without_success_states(source_path):
    result = validate_model_assisted_extraction_request(valid_request(source_path=source_path))
    assert result["status"] in FAIL_CLOSED_STATUSES
    assert result["status"] != "valid"
    assert result["request_valid"] is False
    assert result["fail_closed"] is True
    assert result.get("candidate_support_ready", False) is False


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("project_id", ""),
        ("project_id", "../project"),
        ("project_id", "C:\\project"),
        ("request_id", ""),
        ("request_id", "request/001"),
        ("source_id", ""),
        ("source_id", "../scene"),
        ("source_id", "scene\\001"),
    ),
)
def test_empty_or_unsafe_ids_are_request_invalid(field, value):
    result = validate_model_assisted_extraction_request(valid_request(**{field: value}))
    assert result["status"] == "request_invalid"
    assert result["request_valid"] is False
    assert result["fail_closed"] is True


@pytest.mark.parametrize(
    "source_type",
    (
        "model_generated_source",
        "assistant_authored_scene",
        "scraped_unknown_source",
        "training_corpus",
        "canon_without_evidence",
        "",
    ),
)
def test_unsupported_source_claims_are_rejected_without_candidate_or_training_state(source_type):
    result = validate_model_assisted_extraction_request(valid_request(source_type=source_type))
    assert result["status"] in {"request_invalid", "rejected", "quarantined", "fail_closed"}
    assert result["request_valid"] is False
    assert result["status"] not in {"valid", "candidate_support_ready", "diagnostic_questions_ready"}
    assert result.get("persist_as_training_data", False) is False


@pytest.mark.parametrize(
    ("field", "expected_status"),
    (
        ("source_refs", "missing_source_refs"),
        ("evidence_refs", "missing_evidence_refs"),
        ("provenance_refs", "missing_provenance_refs"),
        ("source_locator_refs", "missing_source_locator_refs"),
    ),
)
def test_missing_required_refs_fail_closed_and_never_become_truth(field, expected_status):
    result = validate_model_assisted_extraction_request(valid_request(**{field: []}))
    assert result["status"] == expected_status
    assert result["request_valid"] is False
    assert result["fail_closed"] is True
    assert result["status"] not in {"valid", "candidate_support_ready", "diagnostic_questions_ready"}
    assert_not_truth_or_persistence(result)


@pytest.mark.parametrize(
    "source_locator_refs",
    (
        [""],
        ["ambiguous_locator"],
        ["source_locator_ref_ambiguous"],
        ["source_locator_ref_scene_001_chars_001", "ambiguous_locator"],
        ["../locator"],
        ["C:\\locator"],
    ),
)
def test_malformed_ambiguous_or_invalid_source_locators_fail_closed(source_locator_refs):
    request_result = validate_model_assisted_extraction_request(
        valid_request(source_locator_refs=source_locator_refs)
    )
    assert request_result["status"] in {
        "missing_source_locator_refs",
        "source_locator_invalid",
        "request_invalid",
        "rejected",
        "quarantined",
        "fail_closed",
    }
    assert request_result["status"] != "valid"
    assert request_result["request_valid"] is False

    output = valid_output(source_locator_refs=source_locator_refs)
    output["candidate_support"][0]["source_locator_refs"] = source_locator_refs
    output["candidate_support"][0]["source_locator_status"] = "ambiguous"
    support = build_model_assisted_candidate_support(output)
    assert support["status"] in {
        "source_locator_invalid",
        "evidence_insufficient",
        "rejected",
        "quarantined",
        "fail_closed",
        "missing_source_locator_refs",
    }
    assert support["candidate_support_ready"] is False
    assert support["treat_as_candidate_truth"] is False


@pytest.mark.parametrize("output_type", FORBIDDEN_OUTPUT_CLASSES)
def test_direct_forbidden_output_classes_are_rejected(output_type):
    result = validate_model_assisted_output(valid_output(output_type=output_type))
    assert result["status"] in {
        "refused_no_prose",
        "blocked_request",
        "unsupported_output_type",
        "rejected",
        "quarantined",
        "fail_closed",
    }
    assert result["allowed_output_class"] is False
    assert result["candidate_support_ready"] is False
    assert result["status"] not in {"valid", "candidate_support_ready", "diagnostic_questions_ready"}


@pytest.mark.parametrize("output_type", FORBIDDEN_OUTPUT_CLASSES)
def test_nested_forbidden_output_classes_are_refused_in_handoffs(output_type):
    output = valid_output(
        nested={"output_type": output_type},
        candidate_support=[
            {
                **valid_output()["candidate_support"][0],
                "nested_intent": {"output_type": output_type},
            }
        ],
    )
    candidate = build_model_assisted_candidate_observation_handoff(output)
    diagnostic = build_model_assisted_diagnostic_handoff(output)
    assert candidate["handoff_status"] in {
        "refused_no_prose",
        "blocked_request",
        "unsupported_output_type",
        "rejected",
        "quarantined",
        "fail_closed",
    }
    assert diagnostic["handoff_status"] in {
        "refused_no_prose",
        "blocked_request",
        "unsupported_output_type",
        "rejected",
        "quarantined",
        "fail_closed",
    }
    assert candidate["generated_prose"] is False
    assert diagnostic["generated_prose"] is False
    assert candidate["candidate_support_ready"] is False
    assert diagnostic["diagnostic_questions_ready"] is False


def test_prompt_packet_preserves_refs_and_guard_confirmations_without_prose_or_truth_state():
    packet = build_model_assisted_extraction_prompt_packet(valid_request())
    assert packet["status"] == "valid"
    assert packet["source_refs"] == [SOURCE_REF]
    assert packet["evidence_refs"] == [EVIDENCE_REF]
    assert packet["provenance_refs"] == [PROVENANCE_REF]
    assert packet["source_locator_refs"] == [SOURCE_LOCATOR_REF]
    assert set(packet["guard_confirmations"]) == {
        "no-prose",
        "no-rewrite",
        "no-continuation",
        "no-outline",
        "no-training",
        "no-canon",
        "no-apply-promotion",
    }
    assert packet["packet_is_training_data"] is False
    assert packet["persist_as_project_truth"] is False
    assert packet["persist_as_training_data"] is False
    packet_text = " ".join(str(value).lower() for value in packet.values())
    for forbidden in FORBIDDEN_PROMPT_INSTRUCTIONS:
        assert forbidden not in packet_text
    assert "model_prompt" not in packet_text
    assert "model_completion" not in packet_text


def test_candidate_diagnostic_and_review_handoffs_remain_in_memory_and_side_effect_free(monkeypatch):
    def forbidden_call(*args, **kwargs):
        raise AssertionError("review/candidate persistence boundary was crossed")

    monkeypatch.setattr(candidate_review_gate, "write_candidate_record", forbidden_call)
    monkeypatch.setattr(review_queue_storage, "write_review_queue_entry", forbidden_call)

    candidate = build_model_assisted_candidate_observation_handoff(valid_output())
    diagnostic = build_model_assisted_diagnostic_handoff(valid_output(output_type="diagnostic question"))
    review = build_model_assisted_review_handoff(candidate, diagnostic)
    validation = validate_model_assisted_review_handoff(review)

    assert candidate["handoff_status"] == "candidate_support_ready"
    assert diagnostic["handoff_status"] == "diagnostic_questions_ready"
    assert review["handoff_type"] == "review"
    assert review["in_memory_only"] is True
    assert review["side_effect_free"] is True
    assert review["writes_files"] is False
    assert review["candidate_record_written"] is False
    assert review["review_queue_entry_written"] is False
    assert review["creates_candidate_records"] is False
    assert review["creates_review_queue_entries"] is False
    assert review["apply_promotion_performed"] is False
    assert review["memory_canon_mutated"] is False
    assert review["training_artifact_created"] is False
    assert review["model_call_performed"] is False
    assert review["queue_presence_is_approval"] is False
    assert review["candidate_persistence_is_canon"] is False
    assert review["queue_boundary_note"] == "queue presence is not approval"
    assert review["candidate_persistence_boundary_note"] == "candidate persistence is not canon"
    assert review["no_automatic_canon"] is True
    assert "apply-promotion" in review["apply_promotion_boundary_note"]
    assert validation["status"] == "valid"
    assert_not_truth_or_persistence(review)


def test_diagnostic_handoff_cannot_include_prose_suggestions_or_rewrite_intents():
    output = valid_output(
        output_type="diagnostic question",
        diagnostic_questions=[
            {
                "question": "Please rewrite this chapter as story prose.",
                "source_refs": [SOURCE_REF],
                "provenance_refs": [PROVENANCE_REF],
                "source_locator_refs": [SOURCE_LOCATOR_REF],
            }
        ],
    )
    handoff = build_model_assisted_diagnostic_handoff(output)
    assert handoff["handoff_status"] in {"refused_no_prose", "blocked_request", "fail_closed"}
    for forbidden_flag in (
        "generated_prose",
        "rewrite",
        "rewritten_prose",
        "continuation",
        "outline",
        "draft",
        "revision",
        "style_imitation",
        "polish",
        "improvement",
        "expansion",
        "story_prose",
    ):
        assert handoff[forbidden_flag] is False


def test_state_vocabulary_is_explicit_and_false_success_is_not_returned_when_blocked():
    environment = validate_model_assisted_environment({})
    assert REQUIRED_STATES.issubset(set(environment["known_states"]))

    for forced_status in REQUIRED_STATES - {"valid"}:
        result = run_guarded_model_assisted_extraction(
            valid_request(), {"model_assistance_forced_status": forced_status}
        )
        if forced_status in {"candidate_support_ready", "diagnostic_questions_ready"}:
            assert result["status"] == "model_call_blocked"
        else:
            assert result["status"] == forced_status
        assert result["status"] not in {"valid", "candidate_support_ready", "diagnostic_questions_ready"}
        assert result["fail_closed"] is True
        assert result["model_call_performed"] is False


def test_no_model_output_as_truth_markers_are_preserved_in_review_handoff_text():
    review = build_model_assisted_review_handoff(valid_output(), valid_output())
    review_text = str(review).lower()
    assert "confidence is not truth" in review_text or review["confidence_is_not_truth"] is True
    assert "model output is not canon" in review_text or review["model_output_is_not_canon"] is True
    assert "no model output as truth" in review_text or review["no_model_output_as_truth"] is True
    assert "queue presence is not approval" in review_text
    assert "candidate persistence is not canon" in review_text
    assert review["not_canon"] is True
    assert review["not_approved_memory"] is True
    assert review["not_training_data"] is True
