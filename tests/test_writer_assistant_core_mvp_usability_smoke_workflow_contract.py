"""Workflow fixture coverage for the MVP usability smoke harness.

PHASE8-IMPL-022-T005 adds focused in-memory workflow fixture and owner-action
validation coverage only. These tests do not execute runtime extraction,
BookNLP, spaCy, NCP, Subtxt, dramatica-flow, models, network, subprocesses,
routes, frontend code, persistence, review queue writes, apply-promotion,
approved memory/canon mutation, training artifacts, or generated prose.
"""

from __future__ import annotations

import copy

import pytest

from backend.story_knowledge.mvp_usability_smoke import (
    build_mvp_usability_evidence_packet,
    classify_mvp_usability_blockers,
    run_guarded_mvp_usability_smoke,
    validate_mvp_usability_smoke_request,
)
from tests.test_writer_assistant_core_mvp_usability_smoke_contract import (
    APPROVED_RECORD_ID,
    CANDIDATE_ID,
    EVIDENCE_REF,
    PROJECT_ID,
    PROMOTION_AUDIT_ID,
    PROVENANCE_REF,
    QUEUE_ENTRY_ID,
    RAW_ARTIFACT_BUNDLE_ID,
    SMOKE_KEY,
    SOURCE_LOCATOR_REF,
    SOURCE_REF,
    valid_matrix,
    valid_request,
)


BOUNDARY_ASSERTIONS = {
    "candidate_first": True,
    "owner_review_required": True,
    "evidence_provenance_source_locator_backed_when_available": True,
    "confidence_is_not_truth": True,
    "tool_output_is_not_canon": True,
    "model_output_is_not_canon": True,
    "no_model_output_as_truth": True,
    "no_automatic_canon": True,
    "no_apply_promotion_outside_audited_path": True,
    "no_memory_canon_mutation_outside_owner_approved": True,
    "no_training_artifacts": True,
    "no_generated_prose": True,
    "no_rewrite": True,
    "no_continuation": True,
    "no_outline": True,
    "fail_closed": True,
    "no_silent_fallback": True,
    "queue_presence_is_not_approval": True,
    "candidate_persistence_is_not_canon": True,
    "mvp_is_not_complete": True,
    "end_to_end_usability_has_not_passed": True,
}


def realistic_workflow_fixture(**overrides):
    fixture = {
        "safe_project_id": PROJECT_ID,
        "project_workspace_loaded": True,
        "owner_authored_or_owner_provided_source_confirmation": True,
        "source_refs": [SOURCE_REF],
        "evidence_refs": [EVIDENCE_REF],
        "provenance_refs": [PROVENANCE_REF],
        "source_locator_refs": [SOURCE_LOCATOR_REF],
        "runtime_extraction_gate": "unavailable",
        "runtime_extraction_failure_gate": "fail_closed",
        "booknlp_availability_signal": "dependency_missing",
        "spacy_availability_signal": "dependency_missing",
        "raw_artifact_persistence_gate": "quarantined",
        "raw_artifact_bundle_id": RAW_ARTIFACT_BUNDLE_ID,
        "candidate_creation_review_handoff_gate": "review_pending",
        "candidate_id": CANDIDATE_ID,
        "review_queue_read_only_surface_gate": "valid",
        "review_queue_entry_id": QUEUE_ENTRY_ID,
        "review_queue_item_visible_read_only": True,
        "frontend_owner_action_execution_gate": "blocked",
        "owner_command": "request_owner_review",
        "owner_command_available": True,
        "owner_command_requires_explicit_confirmation": True,
        "apply_promotion_audited_owner_confirmation_gate": "blocked",
        "promotion_audit_id": PROMOTION_AUDIT_ID,
        "approved_memory_canon_owner_approved_workflow_gate": "blocked",
        "approved_record_id": APPROVED_RECORD_ID,
        "model_assisted_evidence_backed_extraction_gate": "refused",
        "analysis_only_ncp_subtxt_dramatica_flow_gate": "unavailable",
        "unavailable_quarantine_fail_closed_gate": "fail_closed",
        "no_prose_no_rewrite_no_continuation_no_outline_gate": "valid",
        "no_training_artifacts_gate": "valid",
        "no_silent_fallback_gate": "valid",
        "end_to_end_smoke_gate": "incomplete",
        "mvp_blocker_triage_gate": "triaged",
        "mvp_is_not_complete": True,
        "end_to_end_usability_has_not_passed": True,
        "boundary_assertions": copy.deepcopy(BOUNDARY_ASSERTIONS),
    }
    fixture.update(overrides)
    return fixture


def owner_action_expectations(**overrides):
    expectations = {
        "review_queue_item_visible_read_only": True,
        "owner_command_available": True,
        "owner_command_requires_explicit_confirmation": True,
        "apply_promotion_requires_explicit_audited_owner_confirmation": True,
        "approved_memory_canon_mutation_requires_owner_approved_workflow": True,
        "queue_presence_is_not_approval": True,
        "candidate_persistence_is_not_canon": True,
        "apply_promotion_is_separate_from_extraction_review_queue_and_confidence": True,
        "apply_promotion_without_explicit_owner_confirmation": False,
        "approved_memory_canon_mutation_before_owner_approval": False,
        "queue_presence_treated_as_approval": False,
        "candidate_persistence_treated_as_canon": False,
        "confidence_treated_as_truth": False,
        "tool_output_treated_as_canon": False,
        "model_output_treated_as_canon": False,
        "silent_fallback_treated_as_pass": False,
        "mvp_complete_claim": False,
        "end_to_end_usability_passed_claim": False,
    }
    expectations.update(overrides)
    return expectations


def workflow_request(**overrides):
    request = valid_request(
        workflow_fixture=realistic_workflow_fixture(),
        owner_action_expectations=owner_action_expectations(),
    )
    request.update(overrides)
    return request


def workflow_result(**overrides):
    result = {
        "smoke_key": SMOKE_KEY,
        "project_id": PROJECT_ID,
        "gate_id": "end_to_end_smoke",
        "gate_status": "incomplete",
        "gate_state": "missing_required_gate",
        "source_refs": [SOURCE_REF],
        "evidence_refs": [EVIDENCE_REF],
        "provenance_refs": [PROVENANCE_REF],
        "source_locator_refs": [SOURCE_LOCATOR_REF],
        "gate_results": [
            {
                "gate_id": "workspace_project_baseline",
                "gate_status": "valid",
                "gate_state": "valid",
                "evidence_refs": [EVIDENCE_REF],
                "provenance_refs": [PROVENANCE_REF],
                "source_locator_refs": [SOURCE_LOCATOR_REF],
            },
            {
                "gate_id": "runtime_extraction_environment",
                "gate_status": "dependency_missing",
                "gate_state": "dependency_missing",
                "evidence_refs": [EVIDENCE_REF],
                "provenance_refs": [PROVENANCE_REF],
                "source_locator_refs": [SOURCE_LOCATOR_REF],
            },
            {
                "gate_id": "end_to_end_smoke",
                "gate_status": "incomplete",
                "gate_state": "missing_required_gate",
                "evidence_refs": [EVIDENCE_REF],
                "provenance_refs": [PROVENANCE_REF],
                "source_locator_refs": [SOURCE_LOCATOR_REF],
            },
        ],
        "blocker_classifications": [
            "missing_runtime_extraction",
            "missing_booknlp_spacy_availability",
            "missing_end_to_end_smoke",
        ],
        "boundary_assertions": copy.deepcopy(BOUNDARY_ASSERTIONS),
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


def test_realistic_workflow_fixture_validates_as_in_memory_expectations_only():
    request = workflow_request()
    original = copy.deepcopy(request)

    validation = validate_mvp_usability_smoke_request(request)

    assert validation["status"] == "valid"
    assert validation["request_valid"] is True
    assert request == original


@pytest.mark.parametrize(
    "shortcut",
    [
        "apply_promotion_without_explicit_owner_confirmation",
        "approved_memory_canon_mutation_before_owner_approval",
        "queue_presence_treated_as_approval",
        "candidate_persistence_treated_as_canon",
        "confidence_treated_as_truth",
        "tool_output_treated_as_canon",
        "model_output_treated_as_canon",
        "silent_fallback_treated_as_pass",
        "mvp_complete_claim",
        "end_to_end_usability_passed_claim",
    ],
)
def test_owner_action_shortcuts_fail_closed(shortcut):
    request = workflow_request(
        owner_action_expectations=owner_action_expectations(**{shortcut: True})
    )

    validation = validate_mvp_usability_smoke_request(request)

    assert validation["status"] == "fail_closed"
    assert validation["fail_closed"] is True
    assert validation["request_valid"] is False


@pytest.mark.parametrize(
    "expectation",
    [
        "review_queue_item_visible_read_only",
        "owner_command_available",
        "owner_command_requires_explicit_confirmation",
        "apply_promotion_requires_explicit_audited_owner_confirmation",
        "approved_memory_canon_mutation_requires_owner_approved_workflow",
        "queue_presence_is_not_approval",
        "candidate_persistence_is_not_canon",
        "apply_promotion_is_separate_from_extraction_review_queue_and_confidence",
    ],
)
def test_missing_owner_action_expectation_fails_closed(expectation):
    request = workflow_request(
        owner_action_expectations=owner_action_expectations(**{expectation: False})
    )

    validation = validate_mvp_usability_smoke_request(request)

    assert validation["status"] == "fail_closed"
    assert validation["fail_closed"] is True


def test_evidence_packet_preserves_refs_gate_statuses_blockers_and_boundaries():
    packet = build_mvp_usability_evidence_packet(workflow_result())

    assert packet["source_refs"] == [SOURCE_REF]
    assert packet["evidence_refs"] == [EVIDENCE_REF]
    assert packet["provenance_refs"] == [PROVENANCE_REF]
    assert packet["source_locator_refs"] == [SOURCE_LOCATOR_REF]
    assert packet["gate_results"][1]["gate_status"] == "dependency_missing"
    assert "missing_runtime_extraction" in packet["blocker_classifications"]
    assert packet["boundary_assertions"]["confidence_is_not_truth"] is True
    assert packet["support_data_only"] is True
    assert packet["canon_write"] is False
    assert packet["approved_memory_write"] is False
    assert packet["training_data"] is False
    assert packet["promotion_record"] is False
    assert packet["generates_prose"] is False
    assert packet["review_queue_write"] is False
    assert packet["candidate_persistence_write"] is False


@pytest.mark.parametrize(
    ("gate_id", "gate_status", "gate_state", "expected"),
    [
        ("workspace_project_baseline", "blocked", "missing_project", "missing_workspace_project_load"),
        ("owner_authored_source", "blocked", "missing_source_ownership", "missing_owner_source_confirmation"),
        ("runtime_extraction_environment", "unavailable", "unavailable", "missing_runtime_extraction"),
        ("runtime_extraction_environment", "dependency_missing", "dependency_missing", "missing_booknlp_spacy_availability"),
        ("raw_artifact_persistence", "blocked", "missing_manifest", "missing_raw_artifacts"),
        ("candidate_creation", "blocked", "blocked", "missing_candidate_review_handoff"),
        ("review_queue_read_only", "blocked", "blocked", "missing_review_queue_read_only_surface"),
        ("frontend_owner_action", "blocked", "missing_explicit_owner_action", "missing_frontend_owner_action_execution"),
        ("apply_promotion_audited", "blocked", "missing_owner_confirmation", "missing_apply_promotion_audit_confirmation"),
        ("approved_memory_canon_mutation", "blocked", "mutation_outside_owner_approved_workflow", "missing_approved_memory_canon_owner_gate"),
        ("model_assisted_evidence_backed", "blocked", "blocked", "missing_model_assisted_evidence_backed_extraction"),
        ("analysis_only_runtime_integration", "blocked", "missing_allowlist", "missing_analysis_only_runtime_validation"),
        ("approved_memory_canon_mutation", "fail_closed", "model_or_tool_output_promoted_as_truth", "unsafe_canon_shortcut"),
        ("no_prose_no_rewrite_no_continuation_no_outline", "blocked", "generated_prose", "prose_rewrite_continuation_outline_behavior"),
        ("no_training_artifacts", "blocked", "training_jsonl", "training_artifact_behavior"),
        ("no_silent_fallback", "blocked", "silent_fallback", "silent_fallback"),
        ("end_to_end_smoke", "incomplete", "missing_required_gate", "missing_end_to_end_smoke"),
        ("mvp_blocker_triage", "blocked", "blocker", "missing_mvp_blocker_triage"),
    ],
)
def test_blocker_triage_identifies_specific_workflow_blockers(
    gate_id, gate_status, gate_state, expected
):
    triage = classify_mvp_usability_blockers(
        workflow_result(
            gate_id=gate_id,
            gate_status=gate_status,
            gate_state=gate_state,
        )
    )

    assert triage["status"] == "triaged"
    assert expected in triage["blocker_kinds"]


@pytest.mark.parametrize(
    "claim",
    [
        {"mvp_is_not_complete": False},
        {"end_to_end_usability_has_not_passed": False},
    ],
)
def test_blocker_triage_fails_closed_for_premature_success_claims(claim):
    triage = classify_mvp_usability_blockers(workflow_result(**claim))

    assert triage["status"] == "fail_closed"
    assert triage["fail_closed"] is True
    assert triage["mvp_complete"] is False
    assert triage["end_to_end_usability_passed"] is False


def test_guarded_run_is_deterministic_in_memory_and_side_effect_free():
    matrix = valid_matrix()
    request = workflow_request()
    config = {"forced_status": "quarantined", "forced_gate_id": "runtime_extraction_unavailable"}
    original_request = copy.deepcopy(request)

    first = run_guarded_mvp_usability_smoke(matrix, request, config)
    second = run_guarded_mvp_usability_smoke(copy.deepcopy(matrix), copy.deepcopy(request), copy.deepcopy(config))

    assert first == second
    assert request == original_request
    assert first["status"] == "quarantined"
    assert first["executes_booknlp"] is False
    assert first["executes_spacy"] is False
    assert first["executes_ncp"] is False
    assert first["executes_subtxt"] is False
    assert first["executes_dramatica_flow"] is False
    assert first["calls_models_or_ollama"] is False
    assert first["calls_network"] is False
    assert first["calls_subprocess"] is False
    assert first["writes_files"] is False
    assert first["persists_candidates"] is False
    assert first["creates_review_queue_entries"] is False
    assert first["applies_promotion"] is False
    assert first["mutates_memory_canon"] is False
    assert first["creates_training_artifacts"] is False
    assert first["generates_prose"] is False
    assert first["mvp_is_not_complete"] is True
    assert first["end_to_end_usability_has_not_passed"] is True


@pytest.mark.parametrize("forced_status", ["blocked", "unavailable", "quarantined", "fail_closed"])
def test_guarded_run_returns_explicit_blocked_unavailable_quarantined_fail_closed_states(forced_status):
    result = run_guarded_mvp_usability_smoke(
        valid_matrix(),
        workflow_request(),
        {"forced_status": forced_status},
    )

    assert result["status"] == forced_status
    assert result["mvp_is_not_complete"] is True
    assert result["end_to_end_usability_has_not_passed"] is True


def test_guarded_run_fails_closed_for_unsafe_owner_action_fixture():
    result = run_guarded_mvp_usability_smoke(
        valid_matrix(),
        workflow_request(
            owner_action_expectations=owner_action_expectations(
                queue_presence_treated_as_approval=True
            )
        ),
        {"forced_status": "valid"},
    )

    assert result["status"] == "fail_closed"
    assert result["fail_closed"] is True
    assert result["applies_promotion"] is False
    assert result["mutates_memory_canon"] is False
