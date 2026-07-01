"""Safety regression coverage for the MVP usability smoke harness.

PHASE8-IMPL-022-T006 adds no-prose, no-canon, no-training,
no-execution/no-persistence, and no-silent-fallback boundary validation only.
These tests are pure in-memory checks and do not execute runtime extraction,
BookNLP, spaCy, NCP, Subtxt, dramatica-flow, models/Ollama, network,
subprocesses, package installs, filesystem writes, candidate persistence,
review queue writes, apply-promotion, approved memory/canon mutation, training
artifact creation, or generated prose.
"""

from __future__ import annotations

import copy

import pytest

from backend.story_knowledge.mvp_usability_smoke import (
    build_mvp_usability_evidence_packet,
    build_mvp_usability_smoke_plan,
    classify_mvp_usability_blockers,
    run_guarded_mvp_usability_smoke,
    validate_mvp_usability_smoke_matrix,
    validate_mvp_usability_smoke_request,
    validate_mvp_usability_smoke_result,
)
from tests.test_writer_assistant_core_mvp_usability_smoke_contract import (
    EVIDENCE_REF,
    PROJECT_ID,
    PROVENANCE_REF,
    SOURCE_LOCATOR_REF,
    SOURCE_REF,
    valid_matrix,
    valid_request,
    valid_result,
)
from tests.test_writer_assistant_core_mvp_usability_smoke_workflow_contract import (
    owner_action_expectations,
    realistic_workflow_fixture,
    workflow_request,
    workflow_result,
)


FORBIDDEN_PROSE_MARKERS = (
    "generated_prose",
    "rewritten_prose",
    "continuation",
    "outline",
    "draft",
    "revision",
    "polish",
    "improvement",
    "expansion",
    "style_imitation",
    "export_as_prose",
    "chapter_prose",
    "story_prose",
    "prose_production",
)

FORBIDDEN_CANON_SHORTCUT_MARKERS = (
    "tool_output_is_canon",
    "model_output_is_canon",
    "model_output_is_truth",
    "raw_artifact_is_canon",
    "candidate_is_canon",
    "candidate_persistence_is_canon",
    "review_queue_presence_is_approval",
    "confidence_is_truth",
    "evidence_packet_is_approved_memory",
    "evidence_packet_is_canon",
    "mutates_canon",
    "canon_mutation_before_owner_approval",
    "automatic_canon",
    "apply_promotion_outside_audited_path",
)

FORBIDDEN_TRAINING_MARKERS = (
    "training_jsonl",
    "dataset_manifest",
    "model_artifact",
    "fine_tuning_dataset",
    "training_export",
    "eval_dataset_export",
    "generated_training_record",
    "model_completion_artifact_as_truth",
)

FORBIDDEN_EXECUTION_PERSISTENCE_MARKERS = (
    "runtime_extraction_execution",
    "booknlp_execution",
    "spacy_execution",
    "ncp_execution",
    "subtxt_execution",
    "dramatica_flow_execution",
    "model_ollama_call",
    "network",
    "subprocess",
    "package_install",
    "filesystem_write",
    "project_file_write",
    "candidate_persistence_write",
    "review_queue_write",
    "apply_promotion_execution",
    "approved_memory_canon_mutation",
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


def nested_payload(marker: str, value=True) -> dict:
    return {
        "outer": [
            {
                "inner": {
                    "result_class": marker,
                    "payload": [{marker: value}],
                }
            }
        ]
    }


def assert_fail_closed(result: dict) -> None:
    assert result["status"] in {
        "fail_closed",
        "request_invalid",
        "unsafe_path",
        "missing_source_refs",
        "missing_evidence_refs",
        "missing_provenance_refs",
        "missing_source_locator_refs",
        "source_locator_invalid",
        "missing_source_ownership",
    }
    assert result["fail_closed"] is True


@pytest.mark.parametrize("marker", FORBIDDEN_PROSE_MARKERS)
def test_no_prose_markers_fail_closed_across_nested_inputs(marker):
    matrix = valid_matrix(extra_gate_payload=nested_payload(marker))
    request = valid_request(workflow_fixture=realistic_workflow_fixture(extra=nested_payload(marker)))
    plan = build_mvp_usability_smoke_plan(valid_matrix(), valid_request())
    result = valid_result(extra_payload=nested_payload(marker))

    assert_fail_closed(validate_mvp_usability_smoke_matrix(matrix))
    assert_fail_closed(validate_mvp_usability_smoke_request(request))
    assert_fail_closed(validate_mvp_usability_smoke_result(result, plan))
    packet = build_mvp_usability_evidence_packet(result)
    assert packet["status"] == "fail_closed"
    assert packet["support_data_only"] is True
    triage = classify_mvp_usability_blockers(workflow_result(extra_payload=nested_payload(marker)))
    assert triage["status"] == "fail_closed"
    guarded = run_guarded_mvp_usability_smoke(
        valid_matrix(),
        valid_request(),
        {"forced_status": "valid", "authorization": marker},
    )
    assert guarded["status"] == "fail_closed"


@pytest.mark.parametrize("marker", FORBIDDEN_CANON_SHORTCUT_MARKERS)
def test_no_canon_and_no_approved_memory_shortcuts_fail_closed(marker):
    request = workflow_request(
        owner_action_expectations=owner_action_expectations(
            extra_shortcut=nested_payload(marker)
        )
    )
    plan = build_mvp_usability_smoke_plan(valid_matrix(), valid_request())
    result = workflow_result(owner_action_output=nested_payload(marker))

    assert_fail_closed(validate_mvp_usability_smoke_request(request))
    assert_fail_closed(validate_mvp_usability_smoke_result(result, plan))
    packet = build_mvp_usability_evidence_packet(result)
    assert packet["status"] == "fail_closed"
    assert packet["canon_write"] is False
    assert packet["approved_memory_write"] is False
    triage = classify_mvp_usability_blockers(result)
    assert triage["status"] == "fail_closed"


@pytest.mark.parametrize("marker", FORBIDDEN_TRAINING_MARKERS)
def test_no_training_artifacts_or_training_exports_fail_closed(marker):
    request = valid_request(task_output=marker)
    result = valid_result(training_payload=nested_payload(marker))

    assert_fail_closed(validate_mvp_usability_smoke_request(request))
    packet = build_mvp_usability_evidence_packet(result)
    assert packet["status"] == "fail_closed"
    assert packet["creates_training_artifacts"] is False
    assert packet["training_data"] is False


@pytest.mark.parametrize("marker", FORBIDDEN_EXECUTION_PERSISTENCE_MARKERS)
def test_guarded_run_remains_non_executing_and_in_memory(marker):
    result = run_guarded_mvp_usability_smoke(
        valid_matrix(),
        valid_request(),
        {"forced_status": "valid", marker: True},
    )

    assert result["status"] == "fail_closed"
    assert result["executes_booknlp"] is False
    assert result["executes_spacy"] is False
    assert result["executes_ncp"] is False
    assert result["executes_subtxt"] is False
    assert result["executes_dramatica_flow"] is False
    assert result["calls_models_or_ollama"] is False
    assert result["calls_network"] is False
    assert result["calls_subprocess"] is False
    assert result["runs_package_installers"] is False
    assert result["writes_files"] is False
    assert result["persists_candidates"] is False
    assert result["creates_review_queue_entries"] is False
    assert result["applies_promotion"] is False
    assert result["mutates_memory_canon"] is False
    assert result["creates_training_artifacts"] is False
    assert result["generates_prose"] is False


@pytest.mark.parametrize(
    ("override", "expected_status"),
    [
        ({"project_id": ""}, "unsafe_path"),
        ({"project_id": "../escape"}, "unsafe_path"),
        ({"source_refs": []}, "missing_source_refs"),
        ({"evidence_refs": []}, "missing_evidence_refs"),
        ({"provenance_refs": []}, "missing_provenance_refs"),
        ({"source_locator_refs": []}, "missing_source_locator_refs"),
        ({"source_locator_refs": ["../source_locator_ref_bad"]}, "source_locator_invalid"),
        ({"owner_authored_or_owner_provided_source_confirmation": False}, "missing_source_ownership"),
        ({"no_generated_prose_confirmation": False}, "request_invalid"),
        ({"no_rewrite_confirmation": False}, "request_invalid"),
        ({"no_continuation_confirmation": False}, "request_invalid"),
        ({"no_outline_confirmation": False}, "request_invalid"),
        ({"no_training_artifacts_confirmation": False}, "request_invalid"),
    ],
)
def test_incomplete_or_malformed_requests_fail_closed_without_silent_pass(override, expected_status):
    validation = validate_mvp_usability_smoke_request(valid_request(**override))

    assert validation["status"] == expected_status
    assert validation["fail_closed"] is True
    assert validation["request_valid"] is False


@pytest.mark.parametrize(
    "missing_field",
    [
        "runtime_extraction_gate",
        "booknlp_availability_signal",
        "spacy_availability_signal",
        "raw_artifact_persistence_gate",
        "candidate_creation_review_handoff_gate",
        "review_queue_read_only_surface_gate",
        "frontend_owner_action_execution_gate",
        "apply_promotion_audited_owner_confirmation_gate",
        "approved_memory_canon_owner_approved_workflow_gate",
        "model_assisted_evidence_backed_extraction_gate",
        "analysis_only_ncp_subtxt_dramatica_flow_gate",
        "owner_command_available",
    ],
)
def test_missing_workflow_fixture_signals_fail_closed(missing_field):
    fixture = realistic_workflow_fixture()
    fixture.pop(missing_field, None)

    validation = validate_mvp_usability_smoke_request(
        valid_request(workflow_fixture=fixture)
    )

    assert validation["status"] == "fail_closed"
    assert validation["fail_closed"] is True


@pytest.mark.parametrize(
    "forced_status",
    ["unsupported_success", "silent_fallback_claimed_as_pass", "mvp_complete_claim"],
)
def test_unsupported_or_suspicious_guarded_statuses_never_silent_pass(forced_status):
    result = run_guarded_mvp_usability_smoke(
        valid_matrix(),
        valid_request(),
        {"forced_status": forced_status},
    )

    assert result["status"] != "valid"
    assert result["status"] in {"blocked", "fail_closed"}
    assert result["mvp_is_not_complete"] is True
    assert result["end_to_end_usability_has_not_passed"] is True


def test_valid_blocked_evidence_packet_preserves_refs_boundaries_and_support_data_only_markers():
    result = workflow_result(
        gate_status="quarantined",
        gate_state="missing_raw_artifacts",
        source_refs=[SOURCE_REF],
        evidence_refs=[EVIDENCE_REF],
        provenance_refs=[PROVENANCE_REF],
        source_locator_refs=[SOURCE_LOCATOR_REF],
        boundary_assertions=copy.deepcopy(BOUNDARY_ASSERTIONS),
        blocker_classifications=[
            "missing_raw_artifacts",
            "manual_smoke_needed",
            "fail_closed",
        ],
    )

    packet = build_mvp_usability_evidence_packet(result)

    assert packet["status"] == "evidence_packet_ready"
    assert packet["source_refs"] == [SOURCE_REF]
    assert packet["evidence_refs"] == [EVIDENCE_REF]
    assert packet["provenance_refs"] == [PROVENANCE_REF]
    assert packet["source_locator_refs"] == [SOURCE_LOCATOR_REF]
    assert packet["boundary_assertions"] == BOUNDARY_ASSERTIONS
    assert packet["blocker_classifications"] == [
        "missing_raw_artifacts",
        "manual_smoke_needed",
        "fail_closed",
    ]
    assert packet["support_data_only"] is True
    assert packet["generates_prose"] is False
    assert packet["canon_write"] is False
    assert packet["approved_memory_write"] is False
    assert packet["training_data"] is False


def test_required_boundary_assertions_are_preserved_in_guarded_blocked_result():
    result = run_guarded_mvp_usability_smoke(
        valid_matrix(),
        workflow_request(),
        {"forced_status": "blocked", "forced_gate_id": "end_to_end_smoke"},
    )

    assert result["candidate_first"] is True
    assert result["owner_review_required"] is True
    assert result["confidence_is_not_truth"] is True
    assert result["tool_output_is_not_canon"] is True
    assert result["model_output_is_not_canon"] is True
    assert result["no_model_output_as_truth"] is True
    assert result["no_automatic_canon"] is True
    assert result["no_apply_promotion_outside_audited_path"] is True
    assert result["no_memory_canon_mutation_outside_owner_approved"] is True
    assert result["no_training_artifacts"] is True
    assert result["no_generated_prose"] is True
    assert result["no_rewrite"] is True
    assert result["no_continuation"] is True
    assert result["no_outline"] is True
    assert result["no_silent_fallback"] is True
    assert result["queue_presence_is_not_approval"] is True
    assert result["candidate_persistence_is_not_canon"] is True
    assert result["mvp_is_not_complete"] is True
    assert result["end_to_end_usability_has_not_passed"] is True
    assert result["gate_status"] == "blocked"
    assert result["project_id"] == PROJECT_ID
