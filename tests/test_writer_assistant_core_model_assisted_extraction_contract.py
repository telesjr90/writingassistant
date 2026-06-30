"""Expected-red contract tests for future model-assisted extraction APIs.

PHASE8-IMPL-020-T003 is tests-first only. The future module is imported
normally so this targeted file is expected red until a later authorized
implementation task creates it:

- backend.story_knowledge.model_assisted_extraction

Expected future public APIs:

- validate_model_assisted_extraction_request(request: dict) -> dict
- validate_model_assisted_environment(config: dict) -> dict
- build_model_assisted_extraction_prompt_packet(request: dict) -> dict
- validate_model_assisted_output(output: dict) -> dict
- build_model_assisted_candidate_support(output: dict) -> dict
- build_model_assisted_diagnostic_questions(output: dict) -> dict
- quarantine_model_assisted_output(output: dict, reason: str) -> dict
- run_guarded_model_assisted_extraction(request: dict, config: dict) -> dict

These tests encode the PHASE8-IMPL-020-T002 boundary decision. Future model
assistance is local-first, explicit, candidate-first, owner-review required,
evidence-backed, provenance-backed, source-locator-backed when available, and
fail closed with no silent fallback. Model output is not canon. Confidence is
not truth. No model output as truth.

T003 creates no implementation module, no candidate records, no review queue
entries, no approved memory/canon writes, no apply-promotion, no training
artifacts, no generated prose, no rewrite, no continuation, no outline, no
draft/revision/prose-production behavior, and no model_prompt or
model_completion artifacts.
"""

from __future__ import annotations

import copy

import pytest

# The future module is imported normally; expected red until T004 creates it.
from backend.story_knowledge.model_assisted_extraction import (
    build_model_assisted_candidate_support,
    build_model_assisted_diagnostic_questions,
    build_model_assisted_extraction_prompt_packet,
    quarantine_model_assisted_output,
    run_guarded_model_assisted_extraction,
    validate_model_assisted_environment,
    validate_model_assisted_extraction_request,
    validate_model_assisted_output,
)


PROJECT_ID = "example_project"
REQUEST_ID = "model_assisted_extraction_request_001"
SOURCE_REF = "source_ref_owner_scene_001"
EVIDENCE_REF = "evidence_ref_scene_001_span_001"
PROVENANCE_REF = "provenance_ref_owner_material_001"
SOURCE_LOCATOR_REF = "source_locator_ref_scene_001_chars_001"

EXPECTED_PUBLIC_API = (
    "validate_model_assisted_extraction_request",
    "validate_model_assisted_environment",
    "build_model_assisted_extraction_prompt_packet",
    "validate_model_assisted_output",
    "build_model_assisted_candidate_support",
    "build_model_assisted_diagnostic_questions",
    "quarantine_model_assisted_output",
    "run_guarded_model_assisted_extraction",
)

REQUIRED_REQUEST_FIELDS = frozenset(
    {
        "project_id",
        "request_id",
        "source_type",
        "source_id",
        "source_path",
        "source_refs",
        "evidence_refs",
        "provenance_refs",
        "source_locator_refs",
        "raw_source_text",
        "user_intent",
        "boundary_confirmations",
        "requested_by",
        "created_at",
    }
)

REQUIRED_REF_FIELDS = (
    "source_refs",
    "evidence_refs",
    "provenance_refs",
    "source_locator_refs",
)

ALLOWED_SOURCE_TYPES = (
    "owner-authored scene",
    "owner-authored note",
    "owner-provided material",
)

UNSUPPORTED_SOURCE_CLAIMS = (
    "model_generated_source",
    "assistant_authored_scene",
    "scraped_unknown_source",
    "training_corpus",
    "canon_without_evidence",
)

UNSAFE_PATHS = (
    "../escape.md",
    "/absolute/scene.md",
    "C:\\absolute\\scene.md",
    "scenes/../../escape.md",
    "scenes//scene.md",
    "scenes/./scene.md",
    ".",
    "..",
)

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

PROMPT_PACKET_GUARDS = frozenset(
    {
        "no-prose",
        "no-rewrite",
        "no-continuation",
        "no-outline",
        "no-training",
        "no-canon",
        "no-apply-promotion",
    }
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

ALLOWED_OUTPUT_CLASSES = (
    "evidence-backed candidate observation",
    "diagnostic question",
    "uncertainty note",
    "insufficient-evidence note",
    "candidate extraction support",
    "safe refusal / blocked request result",
    "unavailable / fail-closed / quarantined result",
)

FORBIDDEN_OUTPUT_CLASSES = (
    "generated_prose",
    "rewritten_prose",
    "continuation",
    "outline",
    "draft",
    "revision",
    "style imitation",
    "polish",
    "improvement",
    "expansion",
    "model_prompt artifact",
    "model_completion artifact",
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

REQUIRED_STATES = (
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
)

PROSE_REQUESTS = (
    "Please generate prose for the next scene.",
    "Rewrite this chapter.",
    "Continue the scene.",
    "Make an outline for the next chapter.",
    "Draft the ending.",
    "Revise this passage.",
    "Polish this dialogue.",
    "Expand this paragraph.",
    "Imitate this author's style.",
    "Produce story prose from these notes.",
)


def valid_request(**overrides):
    request = {
        "project_id": PROJECT_ID,
        "request_id": REQUEST_ID,
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
        "candidate_support": [
            {
                "candidate_support_id": "candidate_support_001",
                "candidate_type": "character_observation",
                "observation": "The source evidence supports a character observation.",
                "source_refs": [SOURCE_REF],
                "evidence_refs": [EVIDENCE_REF],
                "provenance_refs": [PROVENANCE_REF],
                "source_locator_refs": [SOURCE_LOCATOR_REF],
                "confidence": 0.42,
                "confidence_is_not_truth": True,
                "model_output_is_not_canon": True,
                "no_model_output_as_truth": True,
                "candidate_first": True,
                "owner_review_required": True,
            }
        ],
        "diagnostic_questions": [],
        "uncertainty_notes": [],
        "insufficient_evidence_notes": [],
        "source_refs": [SOURCE_REF],
        "evidence_refs": [EVIDENCE_REF],
        "provenance_refs": [PROVENANCE_REF],
        "source_locator_refs": [SOURCE_LOCATOR_REF],
        "boundary_flags": sorted(REQUIRED_BOUNDARY_CONFIRMATIONS),
    }
    output.update(overrides)
    return output


def test_expected_public_api_surface_is_available():
    api = {
        "validate_model_assisted_extraction_request": validate_model_assisted_extraction_request,
        "validate_model_assisted_environment": validate_model_assisted_environment,
        "build_model_assisted_extraction_prompt_packet": build_model_assisted_extraction_prompt_packet,
        "validate_model_assisted_output": validate_model_assisted_output,
        "build_model_assisted_candidate_support": build_model_assisted_candidate_support,
        "build_model_assisted_diagnostic_questions": build_model_assisted_diagnostic_questions,
        "quarantine_model_assisted_output": quarantine_model_assisted_output,
        "run_guarded_model_assisted_extraction": run_guarded_model_assisted_extraction,
    }
    assert tuple(api) == EXPECTED_PUBLIC_API
    assert all(callable(fn) for fn in api.values())


def test_request_validation_requires_safe_owner_sources_and_refs():
    result = validate_model_assisted_extraction_request(valid_request())
    assert result["status"] == "valid"
    assert result["request_valid"] is True
    assert result["source_type"] in ALLOWED_SOURCE_TYPES
    assert set(REQUIRED_REQUEST_FIELDS).issubset(result["normalized_request"])
    expected_refs = {
        "source_refs": [SOURCE_REF],
        "evidence_refs": [EVIDENCE_REF],
        "provenance_refs": [PROVENANCE_REF],
        "source_locator_refs": [SOURCE_LOCATOR_REF],
    }
    for field in REQUIRED_REF_FIELDS:
        assert result["normalized_request"][field] == expected_refs[field]
    assert result["raw_source_text_is_separate_from_user_intent"] is True
    assert result["owner_authored_storage_editing_is_not_model_generation"] is True


@pytest.mark.parametrize("path", UNSAFE_PATHS)
def test_request_validation_fails_closed_for_unsafe_paths(path):
    result = validate_model_assisted_extraction_request(valid_request(source_path=path))
    assert result["status"] == "unsafe_path"
    assert result["fail_closed"] is True
    assert result["request_valid"] is False


@pytest.mark.parametrize(
    ("field", "expected_status"),
    [
        ("source_refs", "missing_source_refs"),
        ("evidence_refs", "missing_evidence_refs"),
        ("provenance_refs", "missing_provenance_refs"),
        ("source_locator_refs", "missing_source_locator_refs"),
    ],
)
def test_request_validation_fails_closed_when_required_refs_are_missing(field, expected_status):
    request = valid_request()
    request[field] = []
    result = validate_model_assisted_extraction_request(request)
    assert result["status"] == expected_status
    assert result["fail_closed"] is True
    assert result["request_valid"] is False


@pytest.mark.parametrize("source_type", UNSUPPORTED_SOURCE_CLAIMS)
def test_request_validation_rejects_unsupported_source_claims(source_type):
    result = validate_model_assisted_extraction_request(valid_request(source_type=source_type))
    assert result["status"] == "request_invalid"
    assert result["fail_closed"] is True
    assert result["unsupported_source_claim"] == source_type


def test_environment_validation_is_disabled_unavailable_or_explicitly_configured_only():
    disabled = validate_model_assisted_environment({})
    assert disabled["status"] == "disabled"
    assert disabled["model_assistance_available"] is False
    assert disabled["fail_closed"] is True
    assert disabled["no_silent_fallback"] is True

    unavailable = validate_model_assisted_environment(
        {"WRITER_ASSISTANT_MODEL_ASSISTED_EXTRACTION_ENABLED": "1"}
    )
    assert unavailable["status"] in {"unavailable", "model_unavailable", "configuration_invalid"}
    assert unavailable["model_assistance_available"] is False
    assert unavailable["model_output_is_not_truth"] is True
    assert unavailable["confidence_is_not_truth"] is True


def test_environment_validation_reports_all_future_states_explicitly():
    result = validate_model_assisted_environment(
        {"WRITER_ASSISTANT_MODEL_ASSISTED_EXTRACTION_ENABLED": "0"}
    )
    assert set(REQUIRED_STATES).issubset(set(result["known_states"]))
    for state in (
        "disabled",
        "unavailable",
        "model_unavailable",
        "model_call_blocked",
        "configuration_invalid",
        "fail_closed",
    ):
        assert state in result["known_states"]


def test_prompt_packet_preserves_refs_and_guard_confirmations_without_generation_instructions():
    packet = build_model_assisted_extraction_prompt_packet(valid_request())
    assert packet["status"] == "valid"
    assert packet["source_refs"] == [SOURCE_REF]
    assert packet["evidence_refs"] == [EVIDENCE_REF]
    assert packet["provenance_refs"] == [PROVENANCE_REF]
    assert packet["source_locator_refs"] == [SOURCE_LOCATOR_REF]
    assert PROMPT_PACKET_GUARDS.issubset(set(packet["guard_confirmations"]))
    assert packet["raw_source_text"] != packet["user_intent"]
    assert packet["persist_as_project_truth"] is False
    assert packet["persist_as_training_data"] is False
    packet_text = " ".join(str(value).lower() for value in packet.values())
    for forbidden in FORBIDDEN_PROMPT_INSTRUCTIONS:
        assert forbidden not in packet_text
    assert "model_prompt artifact" not in packet_text


@pytest.mark.parametrize("output_type", ALLOWED_OUTPUT_CLASSES)
def test_output_validation_accepts_only_allowed_analysis_support_classes(output_type):
    output = valid_output(output_type=output_type)
    result = validate_model_assisted_output(output)
    assert result["status"] in {
        "valid",
        "candidate_support_ready",
        "diagnostic_questions_ready",
        "evidence_insufficient",
        "refused_no_prose",
        "quarantined",
        "fail_closed",
    }
    assert result["output_type"] == output_type
    assert result["allowed_output_class"] is True
    assert result["model_output_is_not_truth"] is True
    assert result["model_output_is_not_canon"] is True
    assert result["confidence_is_not_truth"] is True


@pytest.mark.parametrize("output_type", FORBIDDEN_OUTPUT_CLASSES)
def test_output_validation_rejects_forbidden_output_classes(output_type):
    result = validate_model_assisted_output(valid_output(output_type=output_type))
    assert result["status"] == "unsupported_output_type"
    assert result["fail_closed"] is True
    assert result["allowed_output_class"] is False


@pytest.mark.parametrize(
    ("field", "expected_status"),
    [
        ("source_refs", "missing_source_refs"),
        ("evidence_refs", "missing_evidence_refs"),
        ("provenance_refs", "missing_provenance_refs"),
        ("source_locator_refs", "missing_source_locator_refs"),
    ],
)
def test_candidate_support_requires_traceable_refs_when_available(field, expected_status):
    output = valid_output()
    output[field] = []
    output["candidate_support"][0][field] = []
    result = build_model_assisted_candidate_support(output)
    assert result["status"] == expected_status
    assert result["fail_closed"] is True
    assert result["candidate_support_ready"] is False


def test_invalid_or_ambiguous_locators_become_insufficient_rejected_or_quarantined():
    output = valid_output(source_locator_refs=["ambiguous_locator"])
    output["candidate_support"][0]["source_locator_refs"] = ["ambiguous_locator"]
    output["candidate_support"][0]["source_locator_status"] = "ambiguous"
    result = build_model_assisted_candidate_support(output)
    assert result["status"] in {
        "source_locator_invalid",
        "evidence_insufficient",
        "rejected",
        "quarantined",
        "fail_closed",
    }
    assert result["candidate_support_ready"] is False
    assert result["treat_as_candidate_truth"] is False


def test_model_interpretations_without_evidence_become_diagnostics_or_uncertainty():
    output = valid_output(
        output_type="uncertainty note",
        evidence_refs=[],
        candidate_support=[],
        diagnostic_questions=[
            {
                "question": "What evidence would support this interpretation?",
                "source_refs": [SOURCE_REF],
                "provenance_refs": [PROVENANCE_REF],
                "source_locator_refs": [SOURCE_LOCATOR_REF],
            }
        ],
        uncertainty_notes=["uncertainty note: evidence is missing"],
    )
    result = build_model_assisted_diagnostic_questions(output)
    assert result["status"] == "diagnostic_questions_ready"
    assert result["diagnostic_questions"]
    assert result["candidate_support_ready"] is False
    assert result["model_interpretation_without_evidence_is_candidate_truth"] is False


def test_candidate_review_boundary_never_creates_records_or_queue_entries():
    result = build_model_assisted_candidate_support(valid_output())
    assert result["status"] == "candidate_support_ready"
    assert result["candidate_first"] is True
    assert result["owner_review_required"] is True
    assert result["creates_candidate_records"] is False
    assert result["creates_review_queue_entries"] is False
    assert result["candidate_persistence_is_canon"] is False
    assert result["queue_presence_is_approval"] is False
    assert result["apply_promotion_performed"] is False


def test_memory_canon_training_and_prose_boundaries_are_hard_false():
    result = run_guarded_model_assisted_extraction(valid_request(), {})
    assert result["status"] in {"disabled", "unavailable", "model_unavailable", "fail_closed"}
    assert result["writes_approved_memory"] is False
    assert result["writes_canon"] is False
    assert result["mutates_bible"] is False
    assert result["mutates_storyform"] is False
    assert result["mutates_scenes"] is False
    assert result["mutates_notes"] is False
    assert result["mutates_materials"] is False
    assert result["applies_promotion"] is False
    assert result["creates_training_artifacts"] is False
    assert result["generates_prose"] is False
    assert result["rewrites_prose"] is False
    assert result["continues_prose"] is False
    assert result["creates_outline"] is False


@pytest.mark.parametrize("user_intent", PROSE_REQUESTS)
def test_prose_requests_are_refused_or_redirected_to_diagnostic_questions(user_intent):
    request = valid_request(user_intent=user_intent)
    result = run_guarded_model_assisted_extraction(request, {"model_assistance_enabled": True})
    assert result["status"] in {"refused_no_prose", "diagnostic_questions_ready", "fail_closed"}
    assert result["generated_prose"] is False
    assert result["rewrite"] is False
    assert result["continuation"] is False
    assert result["outline"] is False
    assert result["allowed_help"] in {"diagnostic question", "diagnostic questions", "analysis"}


def test_insufficient_evidence_fallback_is_required_for_unsupported_claims():
    output = valid_output(
        output_type="evidence-backed candidate observation",
        evidence_refs=[],
        insufficient_evidence_notes=["insufficient-evidence: no support for the claim"],
    )
    result = validate_model_assisted_output(output)
    assert result["status"] in {"evidence_insufficient", "rejected", "fail_closed"}
    assert result["candidate_support_ready"] is False
    assert result["insufficient_evidence_required"] is True


def test_quarantine_preserves_reason_refs_and_support_only_boundary():
    output = valid_output(output_type="malformed_output", status="malformed_output")
    quarantined = quarantine_model_assisted_output(output, reason="malformed_output")
    assert quarantined["status"] == "quarantined"
    assert quarantined["quarantine_reason"] == "malformed_output"
    assert quarantined["source_refs"] == [SOURCE_REF]
    assert quarantined["evidence_refs"] == [EVIDENCE_REF]
    assert quarantined["provenance_refs"] == [PROVENANCE_REF]
    assert quarantined["source_locator_refs"] == [SOURCE_LOCATOR_REF]
    assert quarantined["support_data_only"] is True
    assert quarantined["approved_memory_write"] is False
    assert quarantined["canon_write"] is False
    assert quarantined["training_artifact_created"] is False


def test_request_objects_are_not_mutated_by_validation_or_packet_building():
    request = valid_request()
    original = copy.deepcopy(request)
    validate_model_assisted_extraction_request(request)
    build_model_assisted_extraction_prompt_packet(request)
    assert request == original
