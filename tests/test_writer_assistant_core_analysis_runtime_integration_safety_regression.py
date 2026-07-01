"""PHASE8-IMPL-021-T006-A safety regressions for analysis runtime guards.

These tests prove the helper stays pure, in-memory, fail-closed, and
analysis-only. They do not execute NCP, Subtxt, dramatica-flow, network,
subprocess, models, Ollama, backend.analysis_engine, git clone, dependency
install, file write, persistence helpers, apply-promotion, memory/canon
mutation, review queue writes, candidate writes, training artifacts, or prose
generation.
"""

from __future__ import annotations

import copy

import pytest

from backend.story_knowledge.analysis_runtime_integration import (
    build_analysis_runtime_candidate_observation_handoff,
    build_analysis_runtime_diagnostic_handoff,
    build_analysis_runtime_plan,
    build_analysis_runtime_review_handoff,
    run_guarded_analysis_runtime_integration,
    validate_analysis_runtime_allowlist_record,
    validate_analysis_runtime_output,
    validate_analysis_runtime_request,
    validate_analysis_runtime_review_handoff,
)


ALLOWLIST_KEY = "ncp_context_interchange_v1"
SOURCE_REF = "source_ref_owner_scene_001"
EVIDENCE_REF = "evidence_ref_scene_001_span_001"
PROVENANCE_REF = "provenance_ref_analysis_runtime_001"
SOURCE_LOCATOR_REF = "source_locator_ref_scene_001_chars_001"

ALLOWED_OUTPUT_CLASSES = (
    "evidence_backed_candidate_observation",
    "diagnostic_question",
    "uncertainty_note",
    "insufficient_evidence_note",
    "rubric_mapping_support",
    "context_interchange_support",
    "quarantined_result",
    "unavailable_result",
    "fail_closed_result",
    "refused_no_prose",
    "blocked_request",
)

FORBIDDEN_OUTPUT_CLASSES = (
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
)

UNSAFE_VALUES = (
    "",
    "../escape",
    "..%2fescape",
    "..\\escape",
    "/absolute/path",
    "C:\\absolute\\path",
    "nested/unsafe",
    "project with spaces",
)


def valid_allowlist_record(**overrides):
    record = {
        "tool_name": "NCP",
        "module_or_feature_name": "context_interchange",
        "allowed_action": "build_context_interchange_support",
        "forbidden_actions": list(FORBIDDEN_OUTPUT_CLASSES),
        "output_classes_allowed": list(ALLOWED_OUTPUT_CLASSES),
        "output_classes_forbidden": list(FORBIDDEN_OUTPUT_CLASSES),
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
        "audit_notes": (
            "NCP structured context interchange only; Subtxt rubric/diagnostic guidance only; "
            "dramatica-flow audited allowlist only"
        ),
    }
    record.update(overrides)
    return record


def valid_request(**overrides):
    request = {
        "project_id": "example_project",
        "tool_name": "NCP",
        "requested_action": "build_context_interchange_support",
        "allowlist_key": ALLOWLIST_KEY,
        "analysis_intent": "Build evidence-backed analysis support only.",
        "source_refs": [SOURCE_REF],
        "evidence_refs": [EVIDENCE_REF],
        "provenance_refs": [PROVENANCE_REF],
        "source_locator_refs": [SOURCE_LOCATOR_REF],
        "source_locator_refs_available": True,
        "source_paths": ["scenes/scene_001.md"],
        "owner_authored_or_owner_provided_source_confirmation": True,
        "no_generated_prose_confirmation": True,
        "no_rewrite_confirmation": True,
        "no_continuation_confirmation": True,
        "no_outline_confirmation": True,
        "no_training_confirmation": True,
        "no_canon_confirmation": True,
        "no_apply_promotion_confirmation": True,
    }
    request.update(overrides)
    return request


def valid_output(**overrides):
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
                "confidence_is_not_truth": True,
                "tool_output_is_not_canon": True,
                "tool_output_is_not_truth": True,
            }
        ],
        "diagnostic_questions": [
            {
                "question": "Which existing source evidence supports this analysis claim?",
                "source_refs": [SOURCE_REF],
                "evidence_refs": [EVIDENCE_REF],
                "provenance_refs": [PROVENANCE_REF],
                "source_locator_refs": [SOURCE_LOCATOR_REF],
            }
        ],
    }
    output.update(overrides)
    return output


def assert_non_execution_boundary(result):
    assert result["executes_ncp"] is False
    assert result["executes_subtxt"] is False
    assert result["executes_dramatica_flow"] is False
    assert result["calls_network"] is False
    assert result["calls_subprocess"] is False
    assert result["calls_models_or_ollama"] is False
    assert result["runs_git_clone"] is False
    assert result["installs_dependencies"] is False
    assert result["runs_package_installers"] is False
    assert result["persists_candidates"] is False
    assert result["creates_review_queue_entries"] is False
    assert result["applies_promotion"] is False
    assert result["mutates_memory_canon"] is False
    assert result["creates_training_artifacts"] is False
    assert result["generates_prose"] is False


def test_guarded_runtime_never_executes_tools_or_side_effect_paths():
    result = run_guarded_analysis_runtime_integration(
        valid_request(), {ALLOWLIST_KEY: valid_allowlist_record()}, {"enabled": True}
    )
    assert result["status"] in {"disabled", "unavailable", "blocked_request", "fail_closed"}
    assert result["status"] != "valid"
    assert result["fail_closed"] is True
    assert result["no_silent_fallback"] is True
    assert result["candidate_support_ready"] is False
    assert result["writes_files"] is False
    assert result["calls_persistence_helpers"] is False
    assert_non_execution_boundary(result)


@pytest.mark.parametrize("value", UNSAFE_VALUES)
@pytest.mark.parametrize(
    "field",
    ("project_id", "allowlist_key", "source_refs", "evidence_refs", "provenance_refs"),
)
def test_unsafe_request_ids_refs_and_sources_fail_closed_without_readiness(field, value):
    request = valid_request(**{field: value if field != "project_id" else value})
    if field in {"source_refs", "evidence_refs", "provenance_refs"}:
        request[field] = [value]
    result = validate_analysis_runtime_request(
        request, {ALLOWLIST_KEY: valid_allowlist_record()}
    )
    assert result["status"] in {"unsafe_path", "allowlist_missing", "request_invalid"}
    assert result["fail_closed"] is True
    assert result["request_valid"] is False
    assert result["candidate_support_ready"] is False
    assert result["becomes_canon"] is False
    assert result["becomes_training_data"] is False


@pytest.mark.parametrize(
    "source_claim",
    ("unsupported_external_claim", "canon", "approved_memory", "training_jsonl"),
)
def test_unsupported_source_claims_never_become_valid_or_truth(source_claim):
    output = valid_output(output_class=source_claim)
    result = validate_analysis_runtime_output(output, valid_allowlist_record())
    assert result["status"] in {"unsupported_output_type", "forbidden_output_type"}
    assert result["fail_closed"] is True
    assert result["allowed_output_class"] is False
    assert result["tool_output_is_not_canon"] is True
    assert result["tool_output_is_not_truth"] is True


@pytest.mark.parametrize(
    "allowlist",
    (
        {},
        {ALLOWLIST_KEY: None},
        {ALLOWLIST_KEY: {"tool_name": "NCP"}},
        {ALLOWLIST_KEY: valid_allowlist_record(tool_name="unsupported_tool")},
        {ALLOWLIST_KEY: valid_allowlist_record(allowed_action="unsupported_action")},
        {ALLOWLIST_KEY: valid_allowlist_record(allowed_action="build_rubric_mapping_support")},
    ),
)
def test_allowlist_bypass_attempts_fail_closed(allowlist):
    result = validate_analysis_runtime_request(valid_request(), allowlist)
    assert result["status"] in {
        "allowlist_missing",
        "allowlist_denied",
        "unsupported_tool",
        "unsupported_action",
        "fail_closed",
    }
    assert result["fail_closed"] is True
    assert result["request_valid"] is False


def test_tool_boundaries_are_allowlist_only_and_non_executing():
    for tool_name, action in (
        ("NCP", "build_context_interchange_support"),
        ("Subtxt", "build_rubric_mapping_support"),
        ("dramatica-flow", "build_audited_flow_support"),
    ):
        record = valid_allowlist_record(tool_name=tool_name, allowed_action=action)
        allowlist = {ALLOWLIST_KEY: record}
        request = valid_request(tool_name=tool_name, requested_action=action)
        allowed = validate_analysis_runtime_allowlist_record(record)
        plan = build_analysis_runtime_plan(request, allowlist)
        assert allowed["status"] == "valid"
        assert allowed["tool_boundaries"]["NCP"] == "structured context interchange only"
        assert allowed["tool_boundaries"]["Subtxt"] == "rubric/diagnostic guidance only"
        assert allowed["tool_boundaries"]["dramatica-flow"] == "audited allowlist"
        assert plan["status"] == "valid"
        assert plan["in_memory_only"] is True
        assert_non_execution_boundary(plan)


@pytest.mark.parametrize(
    ("field", "expected_status"),
    [
        ("source_refs", "missing_source_refs"),
        ("evidence_refs", "missing_evidence_refs"),
        ("provenance_refs", "missing_provenance_refs"),
        ("source_locator_refs", "missing_source_locator_refs"),
    ],
)
def test_missing_required_refs_fail_closed(field, expected_status):
    result = validate_analysis_runtime_request(
        valid_request(**{field: []}), {ALLOWLIST_KEY: valid_allowlist_record()}
    )
    assert result["status"] == expected_status
    assert result["fail_closed"] is True


@pytest.mark.parametrize("locator", ("", "ambiguous", "../locator", "source_locator_ref_"))
def test_invalid_source_locators_fail_closed_or_quarantine(locator):
    request = validate_analysis_runtime_request(
        valid_request(source_locator_refs=[locator]), {ALLOWLIST_KEY: valid_allowlist_record()}
    )
    output = build_analysis_runtime_candidate_observation_handoff(
        valid_output(source_locator_refs=[locator])
    )
    assert request["status"] in {"missing_source_locator_refs", "source_locator_invalid"}
    assert request["fail_closed"] is True
    assert output["status"] in {"missing_source_locator_refs", "source_locator_invalid"}
    assert output["fail_closed"] is True


@pytest.mark.parametrize("output_class", FORBIDDEN_OUTPUT_CLASSES)
def test_direct_forbidden_output_classes_are_rejected(output_class):
    result = validate_analysis_runtime_output(
        valid_output(output_class=output_class), valid_allowlist_record()
    )
    assert result["status"] == "forbidden_output_type"
    assert result["fail_closed"] is True
    assert result["allowed_output_class"] is False


@pytest.mark.parametrize("output_class", FORBIDDEN_OUTPUT_CLASSES)
def test_nested_forbidden_output_classes_are_rejected(output_class):
    output = valid_output(
        nested={
            "candidate": {
                "output_class": output_class,
                "intent": output_class,
            }
        }
    )
    result = validate_analysis_runtime_output(output, valid_allowlist_record())
    assert result["status"] == "forbidden_output_type"
    assert result["fail_closed"] is True
    assert result["allowed_output_class"] is False


def test_prose_intents_are_refused_no_prose_and_blocked_request_safe():
    for intent in (
        "generate prose for the next scene",
        "rewrite this chapter",
        "continue the passage",
        "make an outline",
        "draft the ending",
        "revise the scene",
        "polish the dialogue",
        "improve the paragraph",
        "expand the paragraph",
        "imitate this style",
        "export as prose",
        "write story prose",
    ):
        result = validate_analysis_runtime_request(
            valid_request(analysis_intent=intent), {ALLOWLIST_KEY: valid_allowlist_record()}
        )
        assert result["status"] in {"refused_no_prose", "blocked_request"}
        assert result["fail_closed"] is True
        assert result["generates_prose"] is False
        assert result["becomes_canon"] is False
        assert result["becomes_training_data"] is False


def test_handoffs_remain_in_memory_only_and_queue_presence_is_not_approval():
    candidate = build_analysis_runtime_candidate_observation_handoff(valid_output())
    diagnostic = build_analysis_runtime_diagnostic_handoff(valid_output())
    review = build_analysis_runtime_review_handoff(candidate, diagnostic)
    for handoff in (candidate, diagnostic, review):
        assert handoff["in_memory_only"] is True
        assert handoff["pure_data_only"] is True
        assert handoff["queue presence is not approval"] is True
        assert handoff["candidate persistence is not canon"] is True
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
        assert handoff["persists_candidates"] is False
        assert handoff["creates_candidate_records"] is False
        assert handoff["creates_review_queue_entries"] is False
        assert handoff["applies_promotion"] is False
        assert handoff["memory_canon_write"] is False
        assert handoff["approved_memory_write"] is False
        assert handoff["canon_write"] is False
        assert handoff["creates_training_artifacts"] is False
        assert handoff["training_artifact_created"] is False
        assert handoff["generates_prose"] is False
        assert_non_execution_boundary(handoff)


def test_review_handoff_rejects_persistence_promotion_canon_training_side_effect_flags():
    candidate = build_analysis_runtime_candidate_observation_handoff(valid_output())
    diagnostic = build_analysis_runtime_diagnostic_handoff(valid_output())
    review = build_analysis_runtime_review_handoff(candidate, diagnostic)
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
        assert result["fail_closed"] is True
        assert result["review_handoff_valid"] is False

