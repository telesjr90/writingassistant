"""Expected-red contract tests for Writer Assistant Core MVP usability smoke.

PHASE8-IMPL-022-T003-A is tests-first only. The future module is imported
normally so this targeted file is expected red until a later authorized
implementation task (T004+) creates it:

- backend.story_knowledge.mvp_usability_smoke

Expected future public APIs:

- validate_mvp_usability_smoke_matrix(matrix: dict) -> dict
- validate_mvp_usability_smoke_request(request: dict) -> dict
- build_mvp_usability_smoke_plan(matrix: dict, request: dict) -> dict
- validate_mvp_usability_smoke_result(result: dict, plan: dict) -> dict
- build_mvp_usability_evidence_packet(result: dict) -> dict
- classify_mvp_usability_blockers(result: dict) -> dict
- run_guarded_mvp_usability_smoke(matrix: dict, request: dict, config: dict) -> dict

These tests encode the PHASE8-IMPL-022-T002 MVP end-to-end usability validation
matrix and acceptance gates decision. The smoke harness is expected to be:
candidate-first; owner review required; evidence/provenance/source-locator
backed when available; confidence is not truth; tool output is not canon;
model output is not canon; no model output as truth; no automatic canon;
no apply-promotion outside explicit audited owner-confirmed path; no memory or
canon mutation outside owner-approved workflow; queue presence is not approval;
candidate persistence is not canon; no training artifacts; no generated prose;
no rewrite; no continuation; no outline; fail closed; no silent fallback.

T003-A creates no runtime, helper, routes, UI, dependency changes, model
calls, persistence, canon, promotion, training, or generated-prose behavior.
It does not run BookNLP/spaCy, NCP/Subtxt/dramatica-flow, Ollama, network,
subprocess, package installer, git, file writes, or apply-promotion.
"""

from __future__ import annotations

import copy

import pytest

# The future module is imported normally; expected red until T004+ creates it.
from backend.story_knowledge.mvp_usability_smoke import (
    build_mvp_usability_evidence_packet,
    build_mvp_usability_smoke_plan,
    classify_mvp_usability_blockers,
    run_guarded_mvp_usability_smoke,
    validate_mvp_usability_smoke_matrix,
    validate_mvp_usability_smoke_request,
    validate_mvp_usability_smoke_result,
)


PROJECT_ID = "example_project"
SMOKE_KEY = "writer_assistant_core_mvp_usability_smoke_v1"

SOURCE_REF = "source_ref_owner_scene_001"
EVIDENCE_REF = "evidence_ref_scene_001_span_001"
PROVENANCE_REF = "provenance_ref_mvp_smoke_001"
SOURCE_LOCATOR_REF = "source_locator_ref_scene_001_chars_001"
RAW_ARTIFACT_BUNDLE_ID = "raw_artifact_bundle_mvp_smoke_001"
CANDIDATE_ID = "candidate_mvp_smoke_001"
QUEUE_ENTRY_ID = "review_queue_entry_mvp_smoke_001"
PROMOTION_AUDIT_ID = "promotion_audit_mvp_smoke_001"
APPROVED_RECORD_ID = "approved_record_mvp_smoke_001"

EXPECTED_PUBLIC_API = (
    "validate_mvp_usability_smoke_matrix",
    "validate_mvp_usability_smoke_request",
    "build_mvp_usability_smoke_plan",
    "validate_mvp_usability_smoke_result",
    "build_mvp_usability_evidence_packet",
    "classify_mvp_usability_blockers",
    "run_guarded_mvp_usability_smoke",
)

GATE_IDS = (
    "workspace_project_baseline",
    "owner_authored_source",
    "runtime_extraction_environment",
    "runtime_extraction_unavailable",
    "raw_artifact_persistence",
    "candidate_creation",
    "review_queue_read_only",
    "frontend_owner_action",
    "apply_promotion_audited",
    "approved_memory_canon_mutation",
    "model_assisted_evidence_backed",
    "analysis_only_runtime_integration",
    "no_prose_no_rewrite_no_continuation_no_outline",
    "no_training_artifacts",
    "no_silent_fallback",
    "end_to_end_smoke",
    "mvp_blocker_triage",
)

# Coverage labels required by the T002 decision matrix. Each label must be
# discoverable in the smoke module attribute surface so the implementation
# cannot quietly drop a coverage area.
COVERAGE_MARKERS = (
    "workspace/project load",
    "owner-authored or owner-provided project text",
    "runtime extraction",
    "BookNLP",
    "spaCy",
    "unavailable",
    "quarantine",
    "fail_closed",
    "raw artifact persistence",
    "candidate creation",
    "candidate review",
    "review handoff",
    "review queue",
    "read-only review surface",
    "frontend owner-action execution",
    "apply-promotion",
    "approved memory/canon",
    "model-assisted evidence-backed extraction",
    "analysis-only NCP/Subtxt/dramatica-flow",
    "candidate-first",
    "owner review required",
    "confidence is not truth",
    "tool output is not canon",
    "model output is not canon",
    "no model output as truth",
    "no automatic canon",
    "no apply-promotion outside explicit audited owner-confirmed path",
    "no memory/canon mutation outside owner-approved workflow",
    "queue presence is not approval",
    "candidate persistence is not canon",
    "no generated prose",
    "no rewrite",
    "no continuation",
    "no outline",
    "no training artifacts",
    "no silent fallback",
    "MVP is not complete",
    "end-to-end usability has not passed",
)


# ---------------------------------------------------------------------------
# Test fixture helpers
# ---------------------------------------------------------------------------


def valid_matrix(**overrides):
    matrix = {
        "matrix_key": SMOKE_KEY,
        "matrix_version": "1.0.0",
        "matrix_intent": "validate_writer_assistant_core_mvp_usability_end_to_end",
        "gate_ids": list(GATE_IDS),
        "coverage_markers": list(COVERAGE_MARKERS),
        "gate_definitions": {
            "workspace_project_baseline": {
                "gate_name": "workspace_project_baseline",
                "depends_on_prior_parents": [
                    "PHASE8-IMPL-014",
                    "PHASE8-IMPL-015",
                    "PHASE8-IMPL-016",
                    "PHASE8-IMPL-017",
                    "PHASE8-IMPL-018",
                    "PHASE8-IMPL-019",
                    "PHASE8-IMPL-020",
                    "PHASE8-IMPL-021",
                ],
                "expected_status_set": ["valid", "blocked"],
                "expected_state_set": [
                    "valid",
                    "unsafe_path",
                    "missing_project",
                    "ambiguous_project",
                    "blocked",
                ],
            },
            "owner_authored_source": {
                "gate_name": "owner_authored_source",
                "expected_status_set": ["valid", "blocked"],
                "expected_state_set": [
                    "valid",
                    "unknown_source",
                    "generated_source",
                    "missing_source_ownership",
                    "unsafe_locator",
                    "substituted_sample_data",
                    "blocked",
                ],
            },
            "runtime_extraction_environment": {
                "gate_name": "runtime_extraction_environment",
                "expected_status_set": [
                    "valid",
                    "disabled",
                    "unavailable",
                    "dependency_missing",
                    "model_missing",
                    "configuration_invalid",
                    "probe_failed",
                    "runtime_failed",
                    "fail_closed",
                ],
                "expected_state_set": [
                    "disabled",
                    "unavailable",
                    "dependency_missing",
                    "model_missing",
                    "configuration_invalid",
                    "probe_failed",
                    "runtime_failed",
                    "valid",
                    "fail_closed",
                ],
            },
            "runtime_extraction_unavailable": {
                "gate_name": "runtime_extraction_unavailable",
                "expected_status_set": ["blocked", "quarantined", "fail_closed", "valid"],
                "expected_state_set": [
                    "blocked",
                    "quarantined",
                    "fail_closed",
                    "valid",
                ],
            },
            "raw_artifact_persistence": {
                "gate_name": "raw_artifact_persistence",
                "expected_status_set": ["valid", "quarantined", "fail_closed"],
                "expected_state_set": [
                    "valid",
                    "quarantined",
                    "fail_closed",
                    "missing_manifest",
                    "unsafe_path",
                    "missing_refs",
                    "hash_mismatch",
                    "quarantine_indexed_as_valid",
                ],
            },
            "candidate_creation": {
                "gate_name": "candidate_creation",
                "expected_status_set": ["review_pending", "blocked", "fail_closed"],
                "expected_state_set": [
                    "review_pending",
                    "missing_evidence_refs",
                    "missing_provenance_refs",
                    "missing_source_locator_refs",
                    "unsafe_source_locator",
                    "forbidden_destination",
                    "blocked",
                    "fail_closed",
                ],
            },
            "review_queue_read_only": {
                "gate_name": "review_queue_read_only",
                "expected_status_set": ["valid", "blocked", "fail_closed"],
                "expected_state_set": [
                    "valid",
                    "queue_read_mutated_state",
                    "missing_refs_hidden",
                    "queue_treated_as_approval",
                    "canon_or_promotion_output",
                    "blocked",
                    "fail_closed",
                ],
            },
            "frontend_owner_action": {
                "gate_name": "frontend_owner_action",
                "expected_status_set": ["valid", "blocked", "fail_closed"],
                "expected_state_set": [
                    "valid",
                    "missing_explicit_owner_action",
                    "hidden_command",
                    "unsafe_command_accepted",
                    "promotion_or_canon_mutation_from_review_action",
                    "blocked",
                    "fail_closed",
                ],
            },
            "apply_promotion_audited": {
                "gate_name": "apply_promotion_audited",
                "expected_status_set": ["applied", "blocked", "fail_closed"],
                "expected_state_set": [
                    "applied",
                    "missing_owner_confirmation",
                    "missing_audit",
                    "invalid_destination",
                    "missing_refs",
                    "direct_mutation",
                    "blocked",
                    "fail_closed",
                ],
            },
            "approved_memory_canon_mutation": {
                "gate_name": "approved_memory_canon_mutation",
                "expected_status_set": ["mutated", "blocked", "fail_closed"],
                "expected_state_set": [
                    "mutated",
                    "mutation_outside_owner_approved_workflow",
                    "missing_audit",
                    "missing_source_refs",
                    "model_or_tool_output_promoted_as_truth",
                    "blocked",
                    "fail_closed",
                ],
            },
            "model_assisted_evidence_backed": {
                "gate_name": "model_assisted_evidence_backed",
                "expected_status_set": [
                    "candidate_support_ready",
                    "diagnostic_questions_ready",
                    "insufficient_evidence_note",
                    "refused",
                    "quarantined",
                    "unavailable",
                    "fail_closed",
                    "blocked",
                ],
                "expected_state_set": [
                    "candidate_support_ready",
                    "diagnostic_questions_ready",
                    "insufficient_evidence_note",
                    "refused",
                    "quarantined",
                    "unavailable",
                    "fail_closed",
                    "blocked",
                ],
            },
            "analysis_only_runtime_integration": {
                "gate_name": "analysis_only_runtime_integration",
                "expected_status_set": [
                    "valid",
                    "blocked",
                    "fail_closed",
                    "refused",
                    "unavailable",
                    "quarantined",
                ],
                "expected_state_set": [
                    "valid",
                    "unsupported_action",
                    "missing_allowlist",
                    "generated_prose",
                    "outline_generation",
                    "direct_canon_mutation",
                    "silent_fallback",
                    "blocked",
                    "fail_closed",
                ],
            },
            "no_prose_no_rewrite_no_continuation_no_outline": {
                "gate_name": "no_prose_no_rewrite_no_continuation_no_outline",
                "expected_status_set": ["blocked", "refused", "fail_closed", "valid"],
                "expected_state_set": [
                    "blocked",
                    "refused",
                    "fail_closed",
                    "valid",
                    "generated_prose",
                    "rewrite",
                    "continuation",
                    "outline",
                    "polish",
                    "improvement",
                    "expansion",
                    "style_imitation",
                    "story_prose",
                ],
            },
            "no_training_artifacts": {
                "gate_name": "no_training_artifacts",
                "expected_status_set": ["valid", "blocked", "fail_closed"],
                "expected_state_set": [
                    "valid",
                    "training_jsonl",
                    "dataset_manifest",
                    "model_artifact",
                    "fine_tuning_config",
                    "training_output",
                    "blocked",
                    "fail_closed",
                ],
            },
            "no_silent_fallback": {
                "gate_name": "no_silent_fallback",
                "expected_status_set": [
                    "valid",
                    "blocked",
                    "quarantined",
                    "unavailable",
                    "fail_closed",
                ],
                "expected_state_set": [
                    "valid",
                    "blocked",
                    "quarantined",
                    "unavailable",
                    "fail_closed",
                    "silent_fallback",
                    "hidden_mock",
                    "inferred_success",
                ],
            },
            "end_to_end_smoke": {
                "gate_name": "end_to_end_smoke",
                "expected_status_set": [
                    "valid",
                    "incomplete",
                    "blocked",
                    "fail_closed",
                ],
                "expected_state_set": [
                    "valid",
                    "missing_required_gate",
                    "missing_evidence",
                    "unsafe_mutation",
                    "unsupported_success",
                    "boundary_violation",
                    "incomplete",
                    "blocked",
                    "fail_closed",
                ],
            },
            "mvp_blocker_triage": {
                "gate_name": "mvp_blocker_triage",
                "expected_status_set": ["triaged", "blocked", "fail_closed"],
                "expected_state_set": [
                    "triaged",
                    "blocker",
                    "expected_red_gap",
                    "manual_smoke_needed",
                    "environment_unavailable",
                    "deferred_non_mvp",
                    "blocked",
                    "fail_closed",
                ],
            },
        },
        "owner_review_required": True,
        "candidate_first": True,
        "confidence_is_not_truth": True,
        "tool_output_is_not_canon": True,
        "model_output_is_not_canon": True,
        "no_model_output_as_truth": True,
        "no_automatic_canon": True,
        "no_apply_promotion_outside_audited_path": True,
        "no_memory_canon_mutation_outside_owner_approved": True,
        "queue_presence_is_not_approval": True,
        "candidate_persistence_is_not_canon": True,
        "no_generated_prose": True,
        "no_rewrite": True,
        "no_continuation": True,
        "no_outline": True,
        "no_training_artifacts": True,
        "no_silent_fallback": True,
        "mvp_is_not_complete": True,
        "end_to_end_usability_has_not_passed": True,
        "local_in_memory_validation_data_only": True,
    }
    matrix.update(overrides)
    return matrix


def valid_request(**overrides):
    request = {
        "project_id": PROJECT_ID,
        "smoke_key": SMOKE_KEY,
        "smoke_intent": "validate_writer_assistant_core_mvp_usability",
        "source_refs": [SOURCE_REF],
        "evidence_refs": [EVIDENCE_REF],
        "provenance_refs": [PROVENANCE_REF],
        "source_locator_refs": [SOURCE_LOCATOR_REF],
        "owner_authored_or_owner_provided_source_confirmation": True,
        "owner_review_required_confirmation": True,
        "candidate_first_confirmation": True,
        "confidence_is_not_truth_confirmation": True,
        "tool_output_is_not_canon_confirmation": True,
        "model_output_is_not_canon_confirmation": True,
        "no_model_output_as_truth_confirmation": True,
        "no_automatic_canon_confirmation": True,
        "no_apply_promotion_outside_audited_path_confirmation": True,
        "no_memory_canon_mutation_outside_owner_approved_confirmation": True,
        "queue_presence_is_not_approval_confirmation": True,
        "candidate_persistence_is_not_canon_confirmation": True,
        "no_generated_prose_confirmation": True,
        "no_rewrite_confirmation": True,
        "no_continuation_confirmation": True,
        "no_outline_confirmation": True,
        "no_training_artifacts_confirmation": True,
        "no_silent_fallback_confirmation": True,
        "config": {
            "forced_status": "blocked",
            "forced_gate_id": "no_silent_fallback",
        },
    }
    request.update(overrides)
    return request


def valid_result(**overrides):
    result = {
        "smoke_key": SMOKE_KEY,
        "project_id": PROJECT_ID,
        "gate_id": "no_silent_fallback",
        "gate_status": "blocked",
        "gate_state": "silent_fallback",
        "gate_results": [
            {
                "gate_id": "no_silent_fallback",
                "gate_status": "blocked",
                "gate_state": "silent_fallback",
                "evidence_refs": [EVIDENCE_REF],
                "provenance_refs": [PROVENANCE_REF],
                "source_locator_refs": [SOURCE_LOCATOR_REF],
            }
        ],
        "owner_review_required": True,
        "candidate_first": True,
        "confidence_is_not_truth": True,
        "tool_output_is_not_canon": True,
        "model_output_is_not_canon": True,
        "no_model_output_as_truth": True,
        "no_automatic_canon": True,
        "no_apply_promotion_outside_audited_path": True,
        "no_memory_canon_mutation_outside_owner_approved": True,
        "queue_presence_is_not_approval": True,
        "candidate_persistence_is_not_canon": True,
        "no_generated_prose": True,
        "no_rewrite": True,
        "no_continuation": True,
        "no_outline": True,
        "no_training_artifacts": True,
        "no_silent_fallback": True,
        "mvp_is_not_complete": True,
        "end_to_end_usability_has_not_passed": True,
    }
    result.update(overrides)
    return result


# ---------------------------------------------------------------------------
# Public API surface
# ---------------------------------------------------------------------------


def test_expected_public_api_surface_is_available():
    """Future module must expose the documented public API by name."""

    api = {
        "validate_mvp_usability_smoke_matrix": validate_mvp_usability_smoke_matrix,
        "validate_mvp_usability_smoke_request": validate_mvp_usability_smoke_request,
        "build_mvp_usability_smoke_plan": build_mvp_usability_smoke_plan,
        "validate_mvp_usability_smoke_result": validate_mvp_usability_smoke_result,
        "build_mvp_usability_evidence_packet": build_mvp_usability_evidence_packet,
        "classify_mvp_usability_blockers": classify_mvp_usability_blockers,
        "run_guarded_mvp_usability_smoke": run_guarded_mvp_usability_smoke,
    }
    assert tuple(api) == EXPECTED_PUBLIC_API
    assert all(callable(fn) for fn in api.values())


# ---------------------------------------------------------------------------
# Matrix validation
# ---------------------------------------------------------------------------


def test_matrix_validation_requires_complete_in_memory_policy_and_no_runtime_execution():
    result = validate_mvp_usability_smoke_matrix(valid_matrix())
    assert result["status"] == "valid"
    assert result["matrix_valid"] is True
    assert result["local_in_memory_validation_data_only"] is True
    assert result["creates_runtime_execution"] is False
    assert result["creates_routes"] is False
    assert result["persists_data"] is False
    assert result["mutates_canon"] is False
    assert result["applies_promotion"] is False
    assert result["creates_training_artifacts"] is False
    assert result["generates_prose"] is False
    assert result["executes_booknlp"] is False
    assert result["executes_spacy"] is False
    assert result["executes_ncp"] is False
    assert result["executes_subtxt"] is False
    assert result["executes_dramatica_flow"] is False
    assert result["calls_models_or_ollama"] is False
    assert result["calls_network"] is False
    assert result["calls_subprocess"] is False
    assert result["runs_package_installers"] is False
    assert result["runs_git_clone"] is False
    assert result["writes_files"] is False
    assert result["mvp_is_not_complete"] is True
    assert result["end_to_end_usability_has_not_passed"] is True


@pytest.mark.parametrize("marker", COVERAGE_MARKERS)
def test_matrix_validation_requires_every_coverage_marker(marker):
    matrix = valid_matrix()
    matrix["coverage_markers"] = [
        m for m in COVERAGE_MARKERS if m != marker
    ]
    result = validate_mvp_usability_smoke_matrix(matrix)
    assert result["status"] == "fail_closed"
    assert result["fail_closed"] is True
    assert marker in result["missing_coverage_markers"]


@pytest.mark.parametrize("gate_id", GATE_IDS)
def test_matrix_validation_requires_every_gate_definition(gate_id):
    matrix = valid_matrix()
    matrix["gate_definitions"] = {
        key: value
        for key, value in matrix["gate_definitions"].items()
        if key != gate_id
    }
    result = validate_mvp_usability_smoke_matrix(matrix)
    assert result["status"] == "fail_closed"
    assert result["fail_closed"] is True
    assert gate_id in result["missing_gate_ids"]


def test_matrix_validation_rejects_runtime_or_canon_mutation_misconfiguration():
    result = validate_mvp_usability_smoke_matrix(
        valid_matrix(local_in_memory_validation_data_only=False)
    )
    assert result["status"] == "fail_closed"
    assert result["fail_closed"] is True
    assert result["local_in_memory_validation_data_only"] is False


def test_matrix_validation_rejects_mvp_complete_or_usability_passed_claims():
    completed = validate_mvp_usability_smoke_matrix(
        valid_matrix(mvp_is_not_complete=False)
    )
    assert completed["status"] == "fail_closed"
    assert completed["fail_closed"] is True

    passed = validate_mvp_usability_smoke_matrix(
        valid_matrix(end_to_end_usability_has_not_passed=False)
    )
    assert passed["status"] == "fail_closed"
    assert passed["fail_closed"] is True


# ---------------------------------------------------------------------------
# Request validation
# ---------------------------------------------------------------------------


def test_request_validation_requires_safe_owner_sources_refs_and_confirmations():
    result = validate_mvp_usability_smoke_request(valid_request())
    assert result["status"] == "valid"
    assert result["request_valid"] is True
    assert result["owner_authored_or_owner_provided_source"] is True
    assert result["owner_review_required"] is True
    assert result["candidate_first"] is True
    assert result["confidence_is_not_truth"] is True
    assert result["tool_output_is_not_canon"] is True
    assert result["model_output_is_not_canon"] is True
    assert result["no_model_output_as_truth"] is True
    assert result["no_automatic_canon"] is True
    assert result["no_apply_promotion_outside_audited_path"] is True
    assert result["no_memory_canon_mutation_outside_owner_approved"] is True
    assert result["queue_presence_is_not_approval"] is True
    assert result["candidate_persistence_is_not_canon"] is True
    assert result["no_generated_prose"] is True
    assert result["no_rewrite"] is True
    assert result["no_continuation"] is True
    assert result["no_outline"] is True
    assert result["no_training_artifacts"] is True
    assert result["no_silent_fallback"] is True


UNSAFE_PROJECT_IDS = (
    "../escape",
    "/absolute",
    "project/../../escape",
    "project with spaces",
)


@pytest.mark.parametrize("project_id", UNSAFE_PROJECT_IDS)
def test_request_validation_fails_closed_for_unsafe_project_ids(project_id):
    result = validate_mvp_usability_smoke_request(
        valid_request(project_id=project_id)
    )
    assert result["status"] in {"request_invalid", "unsafe_path"}
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
def test_request_validation_fails_closed_when_required_refs_are_missing(
    field, expected_status
):
    result = validate_mvp_usability_smoke_request(
        valid_request(**{field: []})
    )
    assert result["status"] == expected_status
    assert result["fail_closed"] is True


def test_request_validation_requires_source_ownership_confirmation():
    result = validate_mvp_usability_smoke_request(
        valid_request(
            owner_authored_or_owner_provided_source_confirmation=False
        )
    )
    assert result["status"] == "missing_source_ownership"
    assert result["fail_closed"] is True


# ---------------------------------------------------------------------------
# Plan building
# ---------------------------------------------------------------------------


def test_plan_building_is_deterministic_and_in_memory():
    request = valid_request()
    matrix = valid_matrix()
    first = build_mvp_usability_smoke_plan(matrix, request)
    second = build_mvp_usability_smoke_plan(
        copy.deepcopy(matrix), copy.deepcopy(request)
    )
    assert first == second
    assert first["status"] == "valid"
    assert first["smoke_key"] == SMOKE_KEY
    assert first["project_id"] == PROJECT_ID
    assert first["gate_ids"] == list(GATE_IDS)
    assert first["coverage_markers"] == list(COVERAGE_MARKERS)
    assert first["in_memory_only"] is True
    assert first["executes_booknlp"] is False
    assert first["executes_spacy"] is False
    assert first["executes_ncp"] is False
    assert first["executes_subtxt"] is False
    assert first["executes_dramatica_flow"] is False
    assert first["calls_models_or_ollama"] is False
    assert first["calls_network"] is False
    assert first["calls_subprocess"] is False
    assert first["runs_package_installers"] is False
    assert first["runs_git_clone"] is False
    assert first["writes_files"] is False
    assert first["persists_candidates"] is False
    assert first["creates_review_queue_entries"] is False
    assert first["applies_promotion"] is False
    assert first["mutates_memory_canon"] is False
    assert first["creates_training_artifacts"] is False
    assert first["generates_prose"] is False
    assert first["mvp_is_not_complete"] is True
    assert first["end_to_end_usability_has_not_passed"] is True


def test_plan_building_does_not_mutate_matrix_or_request():
    matrix = valid_matrix()
    request = valid_request()
    original_matrix = copy.deepcopy(matrix)
    original_request = copy.deepcopy(request)
    build_mvp_usability_smoke_plan(matrix, request)
    assert matrix == original_matrix
    assert request == original_request


# ---------------------------------------------------------------------------
# Result validation
# ---------------------------------------------------------------------------


def test_result_validation_requires_traceable_refs_and_boundary_assertions():
    plan = build_mvp_usability_smoke_plan(valid_matrix(), valid_request())
    result = validate_mvp_usability_smoke_result(valid_result(), plan)
    assert result["status"] == "valid"
    assert result["result_valid"] is True
    assert result["gate_status"] == "blocked"
    assert result["gate_state"] == "silent_fallback"
    assert result["owner_review_required"] is True
    assert result["candidate_first"] is True
    assert result["confidence_is_not_truth"] is True
    assert result["tool_output_is_not_canon"] is True
    assert result["model_output_is_not_canon"] is True
    assert result["no_model_output_as_truth"] is True
    assert result["no_automatic_canon"] is True
    assert result["queue_presence_is_not_approval"] is True
    assert result["candidate_persistence_is_not_canon"] is True
    assert result["no_generated_prose"] is True
    assert result["no_silent_fallback"] is True
    assert result["mvp_is_not_complete"] is True
    assert result["end_to_end_usability_has_not_passed"] is True


def test_result_validation_rejects_mvp_complete_or_usability_passed_claims():
    plan = build_mvp_usability_smoke_plan(valid_matrix(), valid_request())
    completed = validate_mvp_usability_smoke_result(
        valid_result(mvp_is_not_complete=False), plan
    )
    assert completed["status"] == "fail_closed"
    assert completed["fail_closed"] is True

    passed = validate_mvp_usability_smoke_result(
        valid_result(end_to_end_usability_has_not_passed=False), plan
    )
    assert passed["status"] == "fail_closed"
    assert passed["fail_closed"] is True


def test_result_validation_rejects_owner_review_or_candidate_first_overrides():
    plan = build_mvp_usability_smoke_plan(valid_matrix(), valid_request())
    reviewed = validate_mvp_usability_smoke_result(
        valid_result(owner_review_required=False), plan
    )
    assert reviewed["status"] == "fail_closed"

    candidate = validate_mvp_usability_smoke_result(
        valid_result(candidate_first=False), plan
    )
    assert candidate["status"] == "fail_closed"


# ---------------------------------------------------------------------------
# Evidence packet
# ---------------------------------------------------------------------------


def test_evidence_packet_preserves_refs_and_does_not_produce_prose():
    result = valid_result()
    packet = build_mvp_usability_evidence_packet(result)
    assert packet["status"] == "evidence_packet_ready"
    assert packet["source_refs"] == result.get("source_refs", [])
    assert packet["gate_id"] == result["gate_id"]
    assert packet["gate_status"] == result["gate_status"]
    assert packet["gate_state"] == result["gate_state"]
    assert packet["support_data_only"] is True
    assert packet["generates_prose"] is False
    assert packet["rewrites_prose"] is False
    assert packet["continues_prose"] is False
    assert packet["creates_outline"] is False
    assert packet["creates_training_artifacts"] is False
    assert packet["approved_memory_write"] is False
    assert packet["canon_write"] is False
    assert packet["promotion_record"] is False


# ---------------------------------------------------------------------------
# Blocker classification
# ---------------------------------------------------------------------------


def test_blocker_classification_records_blocker_evidence_and_next_action():
    result = valid_result()
    classified = classify_mvp_usability_blockers(result)
    assert classified["status"] == "triaged"
    assert classified["gate_id"] == result["gate_id"]
    assert classified["gate_status"] == "blocked"
    assert "blocker" in classified["blocker_kinds"]
    assert classified["next_action_required"] is True
    assert classified["mvp_complete"] is False
    assert classified["end_to_end_usability_passed"] is False


def test_blocker_classification_rejects_mvp_complete_or_usability_passed_claims():
    completed = classify_mvp_usability_blockers(
        valid_result(mvp_is_not_complete=False)
    )
    assert completed["status"] == "fail_closed"
    assert completed["fail_closed"] is True

    passed = classify_mvp_usability_blockers(
        valid_result(end_to_end_usability_has_not_passed=False)
    )
    assert passed["status"] == "fail_closed"
    assert passed["fail_closed"] is True


# ---------------------------------------------------------------------------
# Guarded run
# ---------------------------------------------------------------------------


GUARDED_STATUSES = frozenset(
    {
        "disabled",
        "unavailable",
        "dependency_missing",
        "model_missing",
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
        "missing_source_ownership",
        "blocked_request",
        "blocked",
        "fail_closed",
        "refused",
        "quarantined",
        "rejected",
        "triaged",
        "incomplete",
        "valid",
    }
)


def test_guarded_smoke_runs_without_runtime_side_effects():
    result = run_guarded_mvp_usability_smoke(
        valid_matrix(),
        valid_request(),
        {"forced_status": "blocked", "forced_gate_id": "no_silent_fallback"},
    )
    assert result["status"] in GUARDED_STATUSES
    assert result["no_silent_fallback"] is True
    assert result["executes_booknlp"] is False
    assert result["executes_spacy"] is False
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
    assert result["creates_training_artifacts"] is False
    assert result["generates_prose"] is False
    assert result["mvp_is_not_complete"] is True
    assert result["end_to_end_usability_has_not_passed"] is True


def test_guarded_smoke_reports_explicit_unavailable_states_without_silent_success():
    for config in (
        {"forced_status": "disabled", "forced_gate_id": "runtime_extraction_environment"},
        {"forced_status": "dependency_missing", "forced_gate_id": "runtime_extraction_environment"},
        {"forced_status": "fail_closed", "forced_gate_id": "no_silent_fallback"},
    ):
        result = run_guarded_mvp_usability_smoke(
            valid_matrix(), valid_request(), config
        )
        assert result["status"] in GUARDED_STATUSES
        assert result["status"] != "valid" or config["forced_status"] == "valid"
        assert result["no_silent_fallback"] is True


# ---------------------------------------------------------------------------
# Coverage marker documentation contract
# ---------------------------------------------------------------------------


def test_all_required_coverage_markers_are_documented_in_the_matrix_fixture():
    """The matrix fixture must enumerate every required coverage marker."""

    matrix = valid_matrix()
    missing = [
        marker for marker in COVERAGE_MARKERS if marker not in matrix["coverage_markers"]
    ]
    assert missing == []


def test_no_prose_and_no_training_markers_are_documented_in_the_matrix_fixture():
    matrix = valid_matrix()
    for required in (
        "no generated prose",
        "no rewrite",
        "no continuation",
        "no outline",
        "no training artifacts",
        "no silent fallback",
        "candidate-first",
        "owner review required",
        "confidence is not truth",
        "tool output is not canon",
        "model output is not canon",
        "no model output as truth",
        "no automatic canon",
        "queue presence is not approval",
        "candidate persistence is not canon",
    ):
        assert required in matrix["coverage_markers"]
