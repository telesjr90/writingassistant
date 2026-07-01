"""Expected-red contract tests for analysis-only runtime integration APIs.

PHASE8-IMPL-021-T003 is tests-first only. The future module is imported
normally so this targeted file is expected red until a later authorized
implementation task creates it:

- backend.story_knowledge.analysis_runtime_integration

Expected future public APIs:

- validate_analysis_runtime_allowlist_record(record: dict) -> dict
- validate_analysis_runtime_request(request: dict, allowlist: dict) -> dict
- build_analysis_runtime_plan(request: dict, allowlist: dict) -> dict
- validate_analysis_runtime_output(output: dict, allowlist_record: dict) -> dict
- build_analysis_runtime_candidate_support(output: dict) -> dict
- build_analysis_runtime_diagnostic_questions(output: dict) -> dict
- quarantine_analysis_runtime_output(output: dict, reason: str) -> dict
- run_guarded_analysis_runtime_integration(request: dict, allowlist: dict, config: dict) -> dict

These tests encode the PHASE8-IMPL-021-T002 boundary decision. NCP is
structured context interchange only. Subtxt is rubric/diagnostic guidance
only. dramatica-flow is usable only through audited allowlist records, and
dramatica-flow prose/write/revise/export/chapter/outline/generation paths are
blocked. Tool output is not canon. Tool output is not truth. Owner intent
inference is not truth. Owner review remains mandatory. Apply-promotion remains
the separate explicit audited owner-confirmed path.

T003 creates no runtime, helper implementation, routes, UI, dependency changes,
model calls, persistence, canon, promotion, training, or generated-prose
behavior. It does not execute NCP, Subtxt, or dramatica-flow; it does not call
network, subprocess, Ollama, package installers, git clone, file writes,
persistence helpers, apply-promotion, or memory/canon mutation.
"""

from __future__ import annotations

import copy

import pytest

# The future module is imported normally; expected red until T004 creates it.
from backend.story_knowledge.analysis_runtime_integration import (
    build_analysis_runtime_candidate_support,
    build_analysis_runtime_diagnostic_questions,
    build_analysis_runtime_plan,
    quarantine_analysis_runtime_output,
    run_guarded_analysis_runtime_integration,
    validate_analysis_runtime_allowlist_record,
    validate_analysis_runtime_output,
    validate_analysis_runtime_request,
)


PROJECT_ID = "example_project"
ALLOWLIST_KEY = "ncp_context_interchange_v1"
SOURCE_REF = "source_ref_owner_scene_001"
EVIDENCE_REF = "evidence_ref_scene_001_span_001"
PROVENANCE_REF = "provenance_ref_analysis_runtime_001"
SOURCE_LOCATOR_REF = "source_locator_ref_scene_001_chars_001"

EXPECTED_PUBLIC_API = (
    "validate_analysis_runtime_allowlist_record",
    "validate_analysis_runtime_request",
    "build_analysis_runtime_plan",
    "validate_analysis_runtime_output",
    "build_analysis_runtime_candidate_support",
    "build_analysis_runtime_diagnostic_questions",
    "quarantine_analysis_runtime_output",
    "run_guarded_analysis_runtime_integration",
)

ALLOWLIST_REQUIRED_FIELDS = frozenset(
    {
        "tool_name",
        "module_or_feature_name",
        "allowed_action",
        "forbidden_actions",
        "output_classes_allowed",
        "output_classes_forbidden",
        "required_refs",
        "source_locator_policy",
        "evidence_policy",
        "provenance_policy",
        "owner_review_policy",
        "fail_closed_policy",
        "no_silent_fallback_policy",
        "no_prose_policy",
        "no_training_policy",
        "no_canon_policy",
        "no_apply_promotion_policy",
        "validation_tests_required",
        "audit_notes",
    }
)

REQUEST_REQUIRED_FIELDS = frozenset(
    {
        "project_id",
        "tool_name",
        "requested_action",
        "allowlist_key",
        "analysis_intent",
        "source_refs",
        "evidence_refs",
        "provenance_refs",
        "source_locator_refs",
        "owner_authored_or_owner_provided_source_confirmation",
        "no_generated_prose_confirmation",
        "no_rewrite_confirmation",
        "no_continuation_confirmation",
        "no_outline_confirmation",
        "no_training_confirmation",
        "no_canon_confirmation",
        "no_apply_promotion_confirmation",
    }
)

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

REQUIRED_STATES = (
    "disabled",
    "unavailable",
    "dependency_missing",
    "configuration_invalid",
    "allowlist_missing",
    "allowlist_denied",
    "unsupported_tool",
    "unsupported_action",
    "request_invalid",
    "unsafe_path",
    "missing_source_refs",
    "missing_evidence_refs",
    "missing_provenance_refs",
    "missing_source_locator_refs",
    "source_locator_invalid",
    "unsupported_output_type",
    "forbidden_output_type",
    "malformed_output",
    "evidence_insufficient",
    "refused_no_prose",
    "blocked_request",
    "quarantined",
    "rejected",
    "diagnostic_questions_ready",
    "candidate_support_ready",
    "valid",
    "fail_closed",
)

SUPPORTED_TOOLS = ("NCP", "Subtxt", "dramatica-flow")
UNSUPPORTED_TOOLS = ("prose_generator", "repo_cloner", "ollama_writer")
UNSAFE_PROJECT_IDS = ("../escape", "/absolute", "project/../../escape", "project with spaces")
UNSAFE_PATHS = ("../scene.md", "/tmp/scene.md", "C:\\scene.md", "scenes/../../escape.md")
PROSE_REQUESTS = (
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


def valid_allowlist_record(**overrides):
    record = {
        "tool_name": "NCP",
        "module_or_feature_name": "context_interchange",
        "allowed_action": "build_context_interchange_support",
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
        "audit_notes": "local in-memory validation data only; audited allowlist",
    }
    record.update(overrides)
    return record


def valid_request(**overrides):
    request = {
        "project_id": PROJECT_ID,
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
        "candidate_support": [
            {
                "candidate_support_id": "candidate_support_001",
                "claim": "Evidence-backed candidate observation.",
                "source_refs": [SOURCE_REF],
                "evidence_refs": [EVIDENCE_REF],
                "provenance_refs": [PROVENANCE_REF],
                "source_locator_refs": [SOURCE_LOCATOR_REF],
                "candidate_first": True,
                "owner_review_required": True,
                "confidence": 0.42,
                "confidence_is_not_truth": True,
                "tool_output_is_not_canon": True,
                "tool_output_is_not_truth": True,
                "no_model_output_as_truth": True,
            }
        ],
        "diagnostic_questions": [],
        "boundary_flags": [
            "candidate-first",
            "owner review",
            "confidence is not truth",
            "tool output is not canon",
            "tool output is not truth",
            "no model output as truth",
            "queue presence is not approval",
            "candidate persistence is not canon",
        ],
    }
    output.update(overrides)
    return output


def test_expected_public_api_surface_is_available():
    api = {
        "validate_analysis_runtime_allowlist_record": validate_analysis_runtime_allowlist_record,
        "validate_analysis_runtime_request": validate_analysis_runtime_request,
        "build_analysis_runtime_plan": build_analysis_runtime_plan,
        "validate_analysis_runtime_output": validate_analysis_runtime_output,
        "build_analysis_runtime_candidate_support": build_analysis_runtime_candidate_support,
        "build_analysis_runtime_diagnostic_questions": build_analysis_runtime_diagnostic_questions,
        "quarantine_analysis_runtime_output": quarantine_analysis_runtime_output,
        "run_guarded_analysis_runtime_integration": run_guarded_analysis_runtime_integration,
    }
    assert tuple(api) == EXPECTED_PUBLIC_API
    assert all(callable(fn) for fn in api.values())


def test_allowlist_record_validation_requires_complete_local_in_memory_policy():
    result = validate_analysis_runtime_allowlist_record(valid_allowlist_record())
    assert result["status"] == "valid"
    assert result["allowlist_record_valid"] is True
    assert set(ALLOWLIST_REQUIRED_FIELDS).issubset(result["normalized_record"])
    assert result["local_in_memory_validation_data_only"] is True
    assert result["creates_runtime_execution"] is False
    assert result["creates_routes"] is False
    assert result["persists_data"] is False
    assert result["mutates_canon"] is False
    assert result["creates_training_artifacts"] is False
    assert result["generates_prose"] is False


@pytest.mark.parametrize("field", sorted(ALLOWLIST_REQUIRED_FIELDS))
def test_allowlist_record_missing_required_fields_fail_closed(field):
    record = valid_allowlist_record()
    record.pop(field)
    result = validate_analysis_runtime_allowlist_record(record)
    assert result["status"] == "fail_closed"
    assert result["fail_closed"] is True
    assert result["allowlist_record_valid"] is False
    assert field in result["missing_fields"]


@pytest.mark.parametrize("tool_name", UNSUPPORTED_TOOLS)
def test_allowlist_validation_rejects_unsupported_tools(tool_name):
    result = validate_analysis_runtime_allowlist_record(
        valid_allowlist_record(tool_name=tool_name)
    )
    assert result["status"] == "unsupported_tool"
    assert result["fail_closed"] is True


def test_allowlist_missing_and_denied_actions_are_explicit_fail_closed_states():
    missing = validate_analysis_runtime_request(valid_request(), allowlist={})
    assert missing["status"] == "allowlist_missing"
    assert missing["fail_closed"] is True

    denied = validate_analysis_runtime_request(
        valid_request(requested_action="generate_prose"),
        {ALLOWLIST_KEY: valid_allowlist_record()},
    )
    assert denied["status"] in {"allowlist_denied", "unsupported_action", "refused_no_prose"}
    assert denied["fail_closed"] is True


def test_request_validation_requires_safe_owner_sources_refs_and_confirmations():
    result = validate_analysis_runtime_request(
        valid_request(), {ALLOWLIST_KEY: valid_allowlist_record()}
    )
    assert result["status"] == "valid"
    assert result["request_valid"] is True
    assert set(REQUEST_REQUIRED_FIELDS).issubset(result["normalized_request"])
    assert result["source_refs"] == [SOURCE_REF]
    assert result["evidence_refs"] == [EVIDENCE_REF]
    assert result["provenance_refs"] == [PROVENANCE_REF]
    assert result["source_locator_refs"] == [SOURCE_LOCATOR_REF]
    assert result["owner_authored_or_owner_provided_source"] is True
    assert result["no_generated_prose"] is True
    assert result["no_rewrite"] is True
    assert result["no_continuation"] is True
    assert result["no_outline"] is True
    assert result["no_training"] is True
    assert result["no_canon"] is True
    assert result["no_apply_promotion"] is True


@pytest.mark.parametrize("project_id", UNSAFE_PROJECT_IDS)
def test_request_validation_fails_closed_for_unsafe_project_ids(project_id):
    result = validate_analysis_runtime_request(
        valid_request(project_id=project_id), {ALLOWLIST_KEY: valid_allowlist_record()}
    )
    assert result["status"] in {"request_invalid", "unsafe_path"}
    assert result["fail_closed"] is True
    assert result["request_valid"] is False


@pytest.mark.parametrize("path", UNSAFE_PATHS)
def test_request_validation_fails_closed_for_unsafe_paths(path):
    result = validate_analysis_runtime_request(
        valid_request(source_paths=[path]), {ALLOWLIST_KEY: valid_allowlist_record()}
    )
    assert result["status"] == "unsafe_path"
    assert result["fail_closed"] is True


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
    result = validate_analysis_runtime_request(
        valid_request(**{field: []}), {ALLOWLIST_KEY: valid_allowlist_record()}
    )
    assert result["status"] == expected_status
    assert result["fail_closed"] is True


def test_invalid_required_source_locator_refs_fail_closed():
    result = validate_analysis_runtime_request(
        valid_request(source_locator_refs=["ambiguous_locator"]),
        {ALLOWLIST_KEY: valid_allowlist_record()},
    )
    assert result["status"] == "source_locator_invalid"
    assert result["fail_closed"] is True


@pytest.mark.parametrize("analysis_intent", PROSE_REQUESTS)
def test_requests_for_prose_or_outline_paths_are_refused_or_blocked(analysis_intent):
    result = validate_analysis_runtime_request(
        valid_request(analysis_intent=analysis_intent),
        {ALLOWLIST_KEY: valid_allowlist_record()},
    )
    assert result["status"] in {"refused_no_prose", "blocked_request", "unsupported_action"}
    assert result["generates_prose"] is False
    assert result["rewrites_prose"] is False
    assert result["continues_prose"] is False
    assert result["creates_outline"] is False
    assert result["becomes_canon"] is False
    assert result["becomes_training_data"] is False
    assert result["applies_promotion"] is False


def test_plan_building_is_deterministic_in_memory_and_non_executing():
    request = valid_request()
    allowlist = {ALLOWLIST_KEY: valid_allowlist_record()}
    first = build_analysis_runtime_plan(request, allowlist)
    second = build_analysis_runtime_plan(copy.deepcopy(request), copy.deepcopy(allowlist))
    assert first == second
    assert first["status"] == "valid"
    assert first["tool_name"] == "NCP"
    assert first["requested_action"] == "build_context_interchange_support"
    assert first["allowlist_key"] == ALLOWLIST_KEY
    assert first["allowed_action"] == "build_context_interchange_support"
    assert set(first["required_refs"]) == {
        "source_refs",
        "evidence_refs",
        "provenance_refs",
        "source_locator_refs",
    }
    assert first["in_memory_only"] is True
    assert first["executes_ncp"] is False
    assert first["executes_subtxt"] is False
    assert first["executes_dramatica_flow"] is False
    assert first["clones_repositories"] is False
    assert first["installs_dependencies"] is False
    assert first["calls_models_or_ollama"] is False
    assert first["persists_candidates"] is False
    assert first["creates_review_queue_entries"] is False
    assert first["mutates_memory_canon"] is False
    assert first["applies_promotion"] is False
    assert first["creates_training_artifacts"] is False
    assert first["generates_prose"] is False


@pytest.mark.parametrize("output_class", ALLOWED_OUTPUT_CLASSES)
def test_output_validation_accepts_only_allowed_analysis_support_classes(output_class):
    result = validate_analysis_runtime_output(
        valid_output(output_class=output_class), valid_allowlist_record()
    )
    assert result["status"] in {
        "valid",
        "candidate_support_ready",
        "diagnostic_questions_ready",
        "evidence_insufficient",
        "quarantined",
        "unavailable",
        "fail_closed",
        "refused_no_prose",
        "blocked_request",
    }
    assert result["allowed_output_class"] is True
    assert result["output_class"] == output_class
    assert result["tool_output_is_not_truth"] is True
    assert result["tool_output_is_not_canon"] is True
    assert result["confidence_is_not_truth"] is True


@pytest.mark.parametrize("output_class", FORBIDDEN_OUTPUT_CLASSES)
def test_output_validation_rejects_forbidden_output_classes(output_class):
    result = validate_analysis_runtime_output(
        valid_output(output_class=output_class), valid_allowlist_record()
    )
    assert result["status"] in {"forbidden_output_type", "unsupported_output_type"}
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
def test_candidate_support_requires_traceable_refs_when_required_or_available(
    field, expected_status
):
    output = valid_output()
    output[field] = []
    output["candidate_support"][0][field] = []
    result = build_analysis_runtime_candidate_support(output)
    assert result["status"] == expected_status
    assert result["fail_closed"] is True
    assert result["candidate_support_ready"] is False


def test_candidate_support_is_candidate_first_and_not_truth_or_canon():
    result = build_analysis_runtime_candidate_support(valid_output())
    assert result["status"] == "candidate_support_ready"
    assert result["candidate_first"] is True
    assert result["owner_review_required"] is True
    assert result["confidence_is_not_truth"] is True
    assert result["tool_output_is_not_canon"] is True
    assert result["tool_output_is_not_truth"] is True
    assert result["no_model_output_as_truth"] is True
    assert result["queue_presence_is_approval"] is False
    assert result["candidate_persistence_is_canon"] is False
    assert result["creates_candidate_records"] is False
    assert result["creates_review_queue_entries"] is False


def test_unsupported_or_insufficiently_evidenced_claims_become_diagnostics():
    output = valid_output(
        output_class="insufficient_evidence_note",
        evidence_refs=[],
        candidate_support=[],
        diagnostic_questions=[
            {
                "question": "What source evidence would support this analysis claim?",
                "source_refs": [SOURCE_REF],
                "provenance_refs": [PROVENANCE_REF],
                "source_locator_refs": [SOURCE_LOCATOR_REF],
            }
        ],
    )
    result = build_analysis_runtime_diagnostic_questions(output)
    assert result["status"] in {"diagnostic_questions_ready", "evidence_insufficient"}
    assert result["candidate_support_ready"] is False
    assert result["unsupported_claim_became_truth"] is False
    assert result["insufficient_evidence_note_required"] is True


def test_diagnostic_questions_do_not_include_prose_suggestions():
    output = valid_output(
        output_class="diagnostic_question",
        candidate_support=[],
        diagnostic_questions=[
            {
                "question": "Which existing source evidence supports this analysis claim?",
                "source_refs": [SOURCE_REF],
                "evidence_refs": [EVIDENCE_REF],
                "provenance_refs": [PROVENANCE_REF],
                "source_locator_refs": [SOURCE_LOCATOR_REF],
            }
        ],
    )
    result = build_analysis_runtime_diagnostic_questions(output)
    question_text = " ".join(q["question"].lower() for q in result["diagnostic_questions"])
    for forbidden in PROSE_REQUESTS:
        assert forbidden not in question_text
    assert result["generates_prose"] is False
    assert result["rewrites_prose"] is False
    assert result["continues_prose"] is False
    assert result["creates_outline"] is False


def test_quarantine_preserves_reason_refs_and_blocks_side_effects():
    quarantined = quarantine_analysis_runtime_output(
        valid_output(output_class="malformed_output", status="malformed_output"),
        reason="malformed_output",
    )
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
    assert quarantined["generated_prose"] is False


def test_guarded_runtime_reports_explicit_unavailable_states_without_silent_success():
    result = run_guarded_analysis_runtime_integration(
        valid_request(), {ALLOWLIST_KEY: valid_allowlist_record()}, {}
    )
    assert result["status"] in {
        "disabled",
        "unavailable",
        "dependency_missing",
        "configuration_invalid",
        "allowlist_missing",
        "allowlist_denied",
        "unsupported_tool",
        "unsupported_action",
        "request_invalid",
        "blocked_request",
        "refused_no_prose",
        "quarantined",
        "rejected",
        "fail_closed",
    }
    assert result["no_silent_fallback"] is True
    assert result["candidate_support_ready"] is False
    assert result["executes_ncp"] is False
    assert result["executes_subtxt"] is False
    assert result["executes_dramatica_flow"] is False
    assert result["calls_network"] is False
    assert result["calls_subprocess"] is False
    assert result["calls_models_or_ollama"] is False
    assert result["runs_package_installers"] is False
    assert result["runs_git_clone"] is False
    assert result["writes_files"] is False
    assert result["calls_persistence_helpers"] is False
    assert result["applies_promotion"] is False
    assert result["mutates_memory_canon"] is False


def test_disabled_missing_or_denied_allowlist_states_do_not_become_success():
    for allowlist in ({}, {ALLOWLIST_KEY: valid_allowlist_record(allowed_action="other_action")}):
        result = run_guarded_analysis_runtime_integration(valid_request(), allowlist, {})
        assert result["status"] in {
            "disabled",
            "allowlist_missing",
            "allowlist_denied",
            "unsupported_action",
            "fail_closed",
        }
        assert result["status"] != "valid"
        assert result["candidate_support_ready"] is False


def test_required_state_vocabulary_is_reported_by_guarded_runtime():
    result = run_guarded_analysis_runtime_integration(
        valid_request(), {ALLOWLIST_KEY: valid_allowlist_record()}, {"forced_status": "disabled"}
    )
    assert set(REQUIRED_STATES).issubset(set(result["known_states"]))


@pytest.mark.parametrize("tool_name", SUPPORTED_TOOLS)
def test_tool_specific_boundaries_are_encoded(tool_name):
    action = {
        "NCP": "build_context_interchange_support",
        "Subtxt": "build_rubric_mapping_support",
        "dramatica-flow": "build_audited_flow_support",
    }[tool_name]
    record = valid_allowlist_record(
        tool_name=tool_name,
        allowed_action=action,
        module_or_feature_name=action,
    )
    result = validate_analysis_runtime_allowlist_record(record)
    assert result["status"] == "valid"
    assert result["tool_boundaries"]["NCP"] == "structured context interchange only"
    assert result["tool_boundaries"]["Subtxt"] == "rubric/diagnostic guidance only"
    assert result["tool_boundaries"]["dramatica-flow"] == "audited allowlist"
    assert result["dramatica_flow_prose_write_revise_export_chapter_outline_generation_blocked"] is True
    assert result["tool_output_is_not_canon"] is True
    assert result["tool_output_is_not_truth"] is True
    assert result["owner_intent_inference_is_not_truth"] is True
    assert result["owner_review_required"] is True
    assert result["apply_promotion_is_separate_owner_confirmed_path"] is True


def test_request_and_allowlist_objects_are_not_mutated():
    request = valid_request()
    allowlist = {ALLOWLIST_KEY: valid_allowlist_record()}
    original_request = copy.deepcopy(request)
    original_allowlist = copy.deepcopy(allowlist)
    validate_analysis_runtime_request(request, allowlist)
    build_analysis_runtime_plan(request, allowlist)
    assert request == original_request
    assert allowlist == original_allowlist
