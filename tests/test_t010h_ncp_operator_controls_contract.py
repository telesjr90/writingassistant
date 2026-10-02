"""Focused T010H operator-safe NCP controls contract tests."""

from __future__ import annotations

import builtins
import copy
from dataclasses import FrozenInstanceError
import json
import os
from pathlib import Path
import socket
import subprocess

import pytest

from backend.story_knowledge.ncp_candidate_import_contract import (
    build_ncp_candidate_import_plan,
)
from backend.story_knowledge.ncp_export_contract import (
    build_ncp_approved_context_export_record,
    plan_ncp_exports,
)
from backend.story_knowledge.ncp_export_validation_contract import (
    NCP_PACKAGE_JSON_PATH,
    NCP_SCHEMA_JSON_PATH,
    NCP_SCHEMA_RECOVERY_PATH,
    NCP_SCHEMA_YAML_PATH,
    build_ncp_schema_interface_evidence,
    validate_ncp_export_before_export,
)
from backend.story_knowledge.ncp_import_contract import validate_ncp_import_artifact
from backend.story_knowledge.ncp_mapping_contract import map_validated_ncp_import
from backend.story_knowledge.ncp_operator_controls_contract import (
    NCP_ACTION_CANDIDATE_BUNDLE,
    NCP_ACTION_STANDARD_EXPORT,
    NCP_AFFORDANCE_CANDIDATE_BUNDLE,
    NCP_AFFORDANCE_EXTERNAL_IMPORT,
    NCP_AFFORDANCE_MATRIX_GATES,
    NCP_AFFORDANCE_STANDARD_EXPORT,
    NCP_AFFORDANCE_TRUSTED_ROUND_TRIP,
    NCP_DESTRUCTIVE_POLICY_STATUS,
    NCP_RETENTION_POLICY_STATUS,
    NcpOperatorControlsSafetyBoundary,
    NcpOperatorControlsValidationError,
    build_ncp_destination_control,
    build_ncp_operator_controls,
    compute_ncp_operator_controls_hash,
    validate_ncp_operator_controls_record,
)
from backend.story_knowledge.ncp_provenance_contract import (
    NCP_EXTERNAL_STATUS_POLICY,
    build_ncp_source_provenance,
)
from backend.story_knowledge.ncp_roundtrip_matrix_contract import (
    build_ncp_roundtrip_matrix,
)


ROOT = Path(__file__).resolve().parents[1]
APPROVED_SOURCE_TEXT = "Exact owner-approved analysis context remains unchanged."
EXTERNAL_SOURCE_TEXT = "External analysis evidence remains pending owner review."


def _schema_interface():
    return build_ncp_schema_interface_evidence(
        schema_json_bytes=(ROOT / NCP_SCHEMA_JSON_PATH).read_bytes(),
        schema_yaml_bytes=(ROOT / NCP_SCHEMA_YAML_PATH).read_bytes(),
        package_json_bytes=(ROOT / NCP_PACKAGE_JSON_PATH).read_bytes(),
        recovery_record_bytes=(ROOT / NCP_SCHEMA_RECOVERY_PATH).read_bytes(),
    )


def _approved_story() -> dict[str, object]:
    return {
        "id": "story_t010h",
        "title": "Approved analysis fixture",
        "genre": "analysis-fixture",
        "logline": APPROVED_SOURCE_TEXT,
        "created_at": "2026-10-01T12:00:00Z",
        "narratives": [
            {
                "id": "narrative_t010h",
                "title": "Approved narrative context",
                "subtext": {
                    "perspectives": [],
                    "players": [],
                    "dynamics": [],
                    "storypoints": [],
                    "storybeats": [],
                },
                "storytelling": {"overviews": [], "moments": []},
            }
        ],
    }


def _external_payload() -> dict[str, object]:
    story = _approved_story()
    narrative = story["narratives"][0]  # type: ignore[index]
    narrative["status"] = "complete"  # type: ignore[index]
    narrative["subtext"]["players"] = [  # type: ignore[index]
        {
            "id": "player_pending_t010h",
            "summary": EXTERNAL_SOURCE_TEXT,
            "future_player_field": {"preserve": True},
        }
    ]
    return {
        "schema_version": "1.3.0",
        "future_top_level": {"uninterpreted": True},
        "story": story,
    }


def _chain() -> dict[str, object]:
    validated = validate_ncp_import_artifact(
        json.dumps(_external_payload(), ensure_ascii=False, indent=2).encode("utf-8"),
        project_id="project-t010h",
        source_reference="owner-selected/imports/t010h.ncp.json",
    )
    mapping = map_validated_ncp_import(validated)
    provenance = build_ncp_source_provenance(validated, mapping)
    candidate_plan = build_ncp_candidate_import_plan(validated, mapping, provenance)
    approved = (
        build_ncp_approved_context_export_record(
            approved_context_record_id="approved-context-t010h",
            approval_record_id="approval-t010h",
            category="metadata",
            ncp_json_pointer="/story",
            source_value=_approved_story(),
        ),
    )
    export_plan = plan_ncp_exports(
        approved,
        include_candidate_review_bundle=True,
        candidate_import_plan=candidate_plan,
    )
    schema_interface = _schema_interface()
    export_validation = validate_ncp_export_before_export(
        export_plan, schema_interface
    )
    matrix_inputs = {
        "validated_import": validated,
        "mapping": mapping,
        "provenance": provenance,
        "candidate_import_plan": candidate_plan,
        "export_plan": export_plan,
        "export_validation": export_validation,
        "schema_interface": schema_interface,
    }
    matrix = build_ncp_roundtrip_matrix(**matrix_inputs)
    return {**matrix_inputs, "roundtrip_matrix": matrix}


def _controls(**overrides: object):
    values = _chain()
    values.update(overrides)
    return build_ncp_operator_controls(**values)  # type: ignore[arg-type]


def _affordance(plan, kind: str):
    return next(item for item in plan.affordances if item.affordance_kind == kind)


def test_controls_are_deterministic_frozen_and_bound_to_full_trace_chain() -> None:
    first = _controls()
    second = _controls()

    assert first == second
    assert first.controls_hash == compute_ncp_operator_controls_hash(first.to_dict())
    assert validate_ncp_operator_controls_record(first.to_dict()) == first.to_dict()
    trace = first.traceability
    assert trace.schema_interface_id
    assert trace.schema_interface_hash
    assert trace.import_validation_id and trace.mapping_id and trace.provenance_id
    assert trace.candidate_import_plan_id and trace.owner_review_handoff_id
    assert trace.export_plan_id and trace.standard_package_id
    assert trace.export_validation_result_id and trace.standard_validation_id
    assert trace.trusted_round_trip_provenance_id
    assert trace.matrix_id and trace.trusted_matrix_row_id
    assert trace.standard_validation_gate_passed is True
    assert trace.trusted_matrix_gate_passed is True
    with pytest.raises(FrozenInstanceError):
        first.controls_hash = "changed"  # type: ignore[misc]


def test_standard_export_requires_intent_destination_validation_matrix_and_confirmation() -> None:
    initial = _controls()
    initial_standard = _affordance(initial, NCP_AFFORDANCE_STANDARD_EXPORT)
    assert initial_standard.state == "awaiting_explicit_operator_intent"
    assert initial_standard.enabled is False

    intended = _controls(
        requested_action=NCP_ACTION_STANDARD_EXPORT,
        explicit_operator_intent=True,
    )
    assert _affordance(intended, NCP_AFFORDANCE_STANDARD_EXPORT).state == (
        "awaiting_safe_destination_selection"
    )

    destination = build_ncp_destination_control("operator-export-t010h")
    unconfirmed = _controls(
        requested_action=NCP_ACTION_STANDARD_EXPORT,
        explicit_operator_intent=True,
        destination=destination,
    )
    assert _affordance(unconfirmed, NCP_AFFORDANCE_STANDARD_EXPORT).state == (
        "awaiting_final_operator_confirmation"
    )

    ready = _controls(
        requested_action=NCP_ACTION_STANDARD_EXPORT,
        explicit_operator_intent=True,
        final_confirmation=True,
        destination=destination,
    )
    standard = _affordance(ready, NCP_AFFORDANCE_STANDARD_EXPORT)
    assert standard.enabled is True
    assert standard.ready_for_future_execution_handoff is True
    assert standard.approved_context_only is True
    assert standard.execution_performed is False
    assert standard.destination_write_performed is False
    assert ready.actual_execution_supported is False


@pytest.mark.parametrize(
    "destination_id",
    ["../escape", "/absolute/path", "folder/name", "folder\\name", ".", "..", ""],
)
def test_destination_controls_reject_paths_and_unsafe_identifiers(destination_id: str) -> None:
    with pytest.raises(NcpOperatorControlsValidationError) as error:
        build_ncp_destination_control(destination_id)
    assert error.value.code == "unsafe_destination_identifier"


@pytest.mark.parametrize(
    "flags", [{"target_exists": True}, {"overwrite_requested": True}]
)
def test_destination_controls_block_existing_targets_and_overwrite(flags: dict[str, bool]) -> None:
    with pytest.raises(NcpOperatorControlsValidationError) as error:
        build_ncp_destination_control("operator-export-t010h", **flags)
    assert error.value.code == "destructive_destination_blocked"


def test_candidate_bundle_external_import_and_round_trip_remain_separate() -> None:
    plan = _controls(
        requested_action=NCP_ACTION_CANDIDATE_BUNDLE,
        explicit_operator_intent=True,
        final_confirmation=True,
        destination=build_ncp_destination_control("candidate-review-t010h"),
    )
    bundle = _affordance(plan, NCP_AFFORDANCE_CANDIDATE_BUNDLE)
    external = _affordance(plan, NCP_AFFORDANCE_EXTERNAL_IMPORT)
    trusted = _affordance(plan, NCP_AFFORDANCE_TRUSTED_ROUND_TRIP)
    matrix = _affordance(plan, NCP_AFFORDANCE_MATRIX_GATES)

    assert bundle.state == "blocked_owner_policy_pending"
    assert bundle.enabled is False
    assert bundle.separately_labeled is True
    assert bundle.review_only is True
    assert bundle.approved_context_only is False
    assert bundle.trusted_round_trip is False
    assert external.state == "candidate_only_owner_review_required"
    assert external.review_only is True
    assert external.local_approval is False
    assert external.trusted_round_trip is False
    assert trusted.enabled is True
    assert trusted.trusted_round_trip is True
    assert trusted.ready_for_future_execution_handoff is False
    assert matrix.enabled is False


def test_external_complete_unknown_and_omitted_fields_remain_metadata_only() -> None:
    plan = _controls()
    trace = plan.traceability

    assert trace.external_complete_present is True
    assert trace.external_status_pointers
    assert trace.external_status_policy == NCP_EXTERNAL_STATUS_POLICY
    assert trace.uninterpreted_provenance_ids
    assert trace.uninterpreted_fields_source_metadata_only is True
    assert trace.omitted_or_empty_categories
    assert trace.omitted_fields_deletion_intent is False
    assert all(item.local_approval is False for item in plan.affordances)
    assert all(item.canon_authority is False for item in plan.affordances)


def test_destructive_and_retention_policies_are_visible_but_cannot_execute() -> None:
    plan = _controls()
    destructive = plan.destructive_action_policy
    retention = plan.retention_deletion_policy

    assert destructive.policy_status == NCP_DESTRUCTIVE_POLICY_STATUS
    assert destructive.visible_to_operator is True
    assert destructive.destructive_operations_available is False
    assert destructive.overwrite_enabled is False
    assert destructive.delete_enabled is False
    assert destructive.purge_enabled is False
    assert destructive.execution_performed is False
    assert retention.policy_status == NCP_RETENTION_POLICY_STATUS
    assert retention.visible_to_operator is True
    assert retention.retention_policy_decided is False
    assert retention.deletion_policy_decided is False
    assert retention.artifact_deletion_performed is False
    assert retention.retention_purge_performed is False


def _set_nested(record: dict[str, object], path: tuple[object, ...], value: object) -> None:
    target: object = record
    for part in path[:-1]:
        target = target[part]  # type: ignore[index]
    target[path[-1]] = value  # type: ignore[index]


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (("affordances", 0, "enabled"), True),
        (("destination", "safe_destination_ready"), True),
        (("destructive_action_policy", "delete_enabled"), True),
        (("retention_deletion_policy", "deletion_action"), "delete"),
        (("traceability", "trusted_matrix_gate_passed"), False),
        (("affordances", 2, "local_approval"), True),
        (("affordances", 1, "promotion_authority"), True),
        (("affordances", 1, "apply_promotion_authority"), True),
        (("safety_boundary", "destination_write_performed"), True),
        (("safety_boundary", "network_execution"), True),
    ],
)
def test_tampered_readiness_destination_authority_and_safety_fail_closed(
    path: tuple[object, ...], value: object
) -> None:
    record = copy.deepcopy(_controls().to_dict())
    _set_nested(record, path, value)
    with pytest.raises(NcpOperatorControlsValidationError):
        validate_ncp_operator_controls_record(record)


def test_recomputed_top_hash_cannot_hide_semantic_readiness_escalation() -> None:
    record = copy.deepcopy(_controls().to_dict())
    record["traceability"]["standard_validation_gate_passed"] = False  # type: ignore[index]
    standard = record["affordances"][0]  # type: ignore[index]
    standard["enabled"] = True
    standard["ready_for_future_execution_handoff"] = True
    material = dict(standard)
    material.pop("affordance_id")
    material.pop("affordance_hash")
    import hashlib

    canonical = json.dumps(
        material, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    affordance_hash = hashlib.sha256(canonical).hexdigest()
    standard["affordance_hash"] = affordance_hash
    standard["affordance_id"] = f"ncp-operator-affordance-{affordance_hash[:32]}"
    controls_hash = compute_ncp_operator_controls_hash(record)
    record["controls_hash"] = controls_hash
    record["controls_id"] = f"ncp-operator-controls-{controls_hash[:32]}"

    with pytest.raises(NcpOperatorControlsValidationError) as error:
        validate_ncp_operator_controls_record(record)
    assert error.value.code == "unsafe_operator_readiness"


def test_controls_perform_no_io_runtime_calls_or_state_writes(monkeypatch) -> None:
    chain = _chain()

    def forbidden(*_args, **_kwargs):
        raise AssertionError("operator controls attempted a forbidden external action")

    monkeypatch.setattr(builtins, "open", forbidden)
    monkeypatch.setattr(Path, "write_text", forbidden)
    monkeypatch.setattr(Path, "write_bytes", forbidden)
    monkeypatch.setattr(subprocess, "run", forbidden)
    monkeypatch.setattr(subprocess, "Popen", forbidden)
    monkeypatch.setattr(os, "system", forbidden)
    monkeypatch.setattr(socket, "socket", forbidden)

    plan = build_ncp_operator_controls(**chain)  # type: ignore[arg-type]
    assert plan.safety_boundary == NcpOperatorControlsSafetyBoundary()
    assert plan.actual_execution_supported is False
    assert all(item.execution_performed is False for item in plan.affordances)


def test_operator_output_contains_no_generated_or_transformed_story_prose() -> None:
    serialized = json.dumps(_controls().to_dict(), ensure_ascii=False)

    assert APPROVED_SOURCE_TEXT not in serialized
    assert EXTERNAL_SOURCE_TEXT not in serialized
    assert "story_fact" not in serialized
    assert _controls().safety_boundary.generated_prose is False
    assert _controls().safety_boundary.prose_transformation is False
