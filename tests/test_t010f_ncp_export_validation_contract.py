"""Focused T010F validation-before-export and round-trip trust tests."""

from __future__ import annotations

import builtins
import copy
from dataclasses import FrozenInstanceError, replace
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
    NCP_CANDIDATE_REVIEW_PACKAGE_KIND,
    NCP_EXPORT_OMISSION_POLICY,
    NCP_STANDARD_EXPORT_PACKAGE_KIND,
    NcpStandardExportSafetyBoundary,
    build_ncp_approved_context_export_record,
    compute_ncp_export_package_hash,
    compute_ncp_export_plan_hash,
    plan_ncp_exports,
)
from backend.story_knowledge.ncp_export_validation_contract import (
    NCP_EXPORT_VALIDATION_CONTRACT_VERSION,
    NCP_PACKAGE_JSON_PATH,
    NCP_PACKAGE_JSON_SHA256,
    NCP_SCHEMA_JSON_PATH,
    NCP_SCHEMA_JSON_SHA256,
    NCP_SCHEMA_RECOVERY_PATH,
    NCP_SCHEMA_RECOVERY_SHA256,
    NCP_SCHEMA_YAML_PATH,
    NCP_SCHEMA_YAML_SHA256,
    NcpExportPreflightValidationError,
    NcpExportValidationSafetyBoundary,
    assess_external_ncp_round_trip_trust,
    build_ncp_schema_interface_evidence,
    compute_ncp_export_validation_result_hash,
    validate_ncp_export_before_export,
    validate_ncp_export_validation_result_record,
)
from backend.story_knowledge.ncp_import_contract import (
    validate_ncp_import_artifact,
)
from backend.story_knowledge.ncp_mapping_contract import map_validated_ncp_import
from backend.story_knowledge.ncp_provenance_contract import (
    NCP_EXTERNAL_STATUS_POLICY,
    build_ncp_source_provenance,
)


ROOT = Path(__file__).resolve().parents[1]
APPROVED_LOG_LINE = "Owner-approved context stays exact; validation adds no prose."
PENDING_SOURCE_TEXT = "Pending imported source text remains review-only metadata."


def _schema_interface():
    return build_ncp_schema_interface_evidence(
        schema_json_bytes=(ROOT / NCP_SCHEMA_JSON_PATH).read_bytes(),
        schema_yaml_bytes=(ROOT / NCP_SCHEMA_YAML_PATH).read_bytes(),
        package_json_bytes=(ROOT / NCP_PACKAGE_JSON_PATH).read_bytes(),
        recovery_record_bytes=(ROOT / NCP_SCHEMA_RECOVERY_PATH).read_bytes(),
    )


def _approved_story() -> dict[str, object]:
    return {
        "id": "story_t010f",
        "title": "Owner-approved title",
        "genre": "Analysis fixture",
        "logline": APPROVED_LOG_LINE,
        "created_at": "2026-09-30T12:00:00Z",
        "narratives": [
            {
                "id": "narrative_t010f",
                "title": "Owner-approved narrative",
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


def _approved_records():
    return (
        build_ncp_approved_context_export_record(
            approved_context_record_id="approved-context-t010f",
            approval_record_id="approval-t010f",
            category="metadata",
            ncp_json_pointer="/story",
            source_value=_approved_story(),
        ),
    )


def _external_payload() -> dict[str, object]:
    story = _approved_story()
    narrative = story["narratives"][0]  # type: ignore[index]
    narrative["status"] = "complete"  # type: ignore[index]
    narrative["subtext"]["players"] = [  # type: ignore[index]
        {
            "id": "player_pending",
            "summary": PENDING_SOURCE_TEXT,
            "future_player_field": "uninterpreted source metadata",
        }
    ]
    return {
        "schema_version": "1.3.0",
        "future_top_level": {"preserve": True},
        "story": story,
    }


def _validated_external_import():
    return validate_ncp_import_artifact(
        json.dumps(_external_payload(), ensure_ascii=False, indent=2).encode("utf-8"),
        project_id="project-t010f",
        source_reference="owner-selected/imports/t010f.ncp.json",
    )


def _candidate_plan():
    validated = _validated_external_import()
    mapping = map_validated_ncp_import(validated)
    provenance = build_ncp_source_provenance(validated, mapping)
    return build_ncp_candidate_import_plan(validated, mapping, provenance)


def _export_plan(*, include_candidate_bundle: bool = False):
    return plan_ncp_exports(
        _approved_records(),
        include_candidate_review_bundle=include_candidate_bundle,
        candidate_import_plan=_candidate_plan() if include_candidate_bundle else None,
    )


def _export_plan_with_storybeat(*, scope: str, sequence: int):
    story = _approved_story()
    narrative = story["narratives"][0]  # type: ignore[index]
    narrative["subtext"]["storybeats"] = [  # type: ignore[index]
        {
            "id": "beat_t010f",
            "scope": scope,
            "sequence": sequence,
            "summary": "Owner-approved structural beat context.",
            "storytelling": "Owner-approved storytelling context.",
            "perspectives": [],
        }
    ]
    record = build_ncp_approved_context_export_record(
        approved_context_record_id="approved-context-storybeat-t010f",
        approval_record_id="approval-storybeat-t010f",
        category="storybeat",
        ncp_json_pointer="/story",
        source_value=story,
    )
    return plan_ncp_exports((record,))


def test_standard_export_validates_before_export_and_earns_round_trip_trust() -> None:
    result = validate_ncp_export_before_export(_export_plan(), _schema_interface())
    standard = result.standard_export_validation
    trust = result.trusted_round_trip_provenance

    assert result.validation_before_export_complete is True
    assert result.contract_version == NCP_EXPORT_VALIDATION_CONTRACT_VERSION
    assert standard.package_kind == NCP_STANDARD_EXPORT_PACKAGE_KIND
    assert standard.package_exportable is True
    assert standard.validation_outcome == "valid_standard_approved_context_export"
    assert standard.trusted_round_trip_eligible is True
    assert trust.trusted_round_trip_eligible is True
    assert trust.approved_context_only is True
    assert trust.candidate_bundle_trusted is False
    assert trust.external_import_trusted is False
    assert validate_ncp_export_validation_result_record(result.to_dict()) == result.to_dict()
    with pytest.raises(FrozenInstanceError):
        result.result_hash = "changed"  # type: ignore[misc]


def test_validation_binds_exact_recovered_repo_local_interface() -> None:
    evidence = _schema_interface()
    result = validate_ncp_export_before_export(_export_plan(), evidence)
    artifacts = {
        item.repo_relative_path: item.sha256 for item in evidence.artifacts
    }

    assert artifacts == {
        NCP_SCHEMA_JSON_PATH: NCP_SCHEMA_JSON_SHA256,
        NCP_SCHEMA_YAML_PATH: NCP_SCHEMA_YAML_SHA256,
        NCP_PACKAGE_JSON_PATH: NCP_PACKAGE_JSON_SHA256,
        NCP_SCHEMA_RECOVERY_PATH: NCP_SCHEMA_RECOVERY_SHA256,
    }
    assert evidence.schema_draft == "http://json-schema.org/draft-07/schema#"
    assert evidence.schema_title == "Narrative Context Protocol Schema"
    assert evidence.validator_surface_status == "optional_unavailable_not_executed"
    assert evidence.node_validator_executed is False
    assert result.standard_export_validation.schema_path == NCP_SCHEMA_JSON_PATH
    assert result.standard_export_validation.schema_sha256 == NCP_SCHEMA_JSON_SHA256


def test_candidate_bundle_validates_separately_but_never_earns_standard_trust() -> None:
    result = validate_ncp_export_before_export(
        _export_plan(include_candidate_bundle=True), _schema_interface()
    )
    candidate = result.candidate_review_bundle_validation
    assert candidate is not None

    assert candidate.package_kind == NCP_CANDIDATE_REVIEW_PACKAGE_KIND
    assert candidate.validation_outcome == "valid_separately_labeled_candidate_review_bundle"
    assert candidate.package_exportable is True
    assert candidate.standard_approved_context_export is False
    assert candidate.candidate_review_bundle is True
    assert candidate.trusted_round_trip_eligible is False
    assert candidate.validated_document_sha256 is None
    assert result.trusted_round_trip_provenance.candidate_bundle_trusted is False


def test_external_import_and_complete_status_never_gain_round_trip_trust() -> None:
    assessment = assess_external_ncp_round_trip_trust(_validated_external_import())

    assert assessment.source_kind == "external_imported_ncp"
    assert assessment.trusted_round_trip_eligible is False
    assert assessment.required_import_flow == "t010a_through_t010d_candidate_review"
    assert assessment.external_status_policy == NCP_EXTERNAL_STATUS_POLICY
    assert assessment.external_statuses[0].external_status == "complete"
    assert assessment.external_statuses[0].local_approval is False
    assert assessment.local_approval is False
    assert assessment.canon_authority is False
    assert assessment.promotion_authority is False
    assert assessment.apply_promotion_authority is False

    with pytest.raises(NcpExportPreflightValidationError) as raw:
        validate_ncp_export_before_export(_external_payload(), _schema_interface())  # type: ignore[arg-type]
    assert raw.value.code == "app_generated_t010e_export_plan_required"


def test_pending_candidates_and_unknown_metadata_cannot_leak_into_standard() -> None:
    plan = _export_plan(include_candidate_bundle=True)
    result = validate_ncp_export_before_export(plan, _schema_interface())
    standard_text = json.dumps(plan.standard_export.to_dict(), ensure_ascii=False)
    candidate = plan.candidate_review_bundle
    assert candidate is not None

    assert PENDING_SOURCE_TEXT not in standard_text
    assert "/future_top_level" in {
        item.json_pointer for item in candidate.uninterpreted_source_metadata
    }
    assert all(
        item.standard_export_eligible is False
        for item in candidate.uninterpreted_source_metadata
    )
    assert result.standard_export_validation.standard_approved_context_export is True
    assert result.candidate_review_bundle_validation is not None


def test_unsupported_or_tampered_schema_interface_fails_closed() -> None:
    evidence = _schema_interface()
    with pytest.raises(NcpExportPreflightValidationError) as bytes_error:
        build_ncp_schema_interface_evidence(
            schema_json_bytes=evidence.schema_json_bytes + b" ",
            schema_yaml_bytes=evidence.schema_yaml_bytes,
            package_json_bytes=evidence.package_json_bytes,
            recovery_record_bytes=evidence.recovery_record_bytes,
        )
    assert bytes_error.value.code == "unsupported_schema_interface_identity"

    weakened = replace(evidence, schema_interface_id="other-interface")
    with pytest.raises(NcpExportPreflightValidationError) as metadata_error:
        validate_ncp_export_before_export(_export_plan(), weakened)
    assert metadata_error.value.code == "schema_interface_evidence_mismatch"


def test_tampered_package_hash_and_safety_boundary_fail_closed() -> None:
    plan = _export_plan()
    bad_package = replace(plan.standard_export, package_hash="0" * 64)
    with pytest.raises(NcpExportPreflightValidationError) as package_error:
        validate_ncp_export_before_export(
            replace(plan, standard_export=bad_package), _schema_interface()
        )
    assert package_error.value.code == "invalid_t010e_export_plan"

    weakened_safety = replace(
        plan.standard_export.safety_boundary,
        candidate_records_included=True,
    )
    unsafe_package = replace(plan.standard_export, safety_boundary=weakened_safety)
    with pytest.raises(NcpExportPreflightValidationError) as safety_error:
        validate_ncp_export_before_export(
            replace(plan, standard_export=unsafe_package), _schema_interface()
        )
    assert safety_error.value.code == "invalid_t010e_export_plan"


def test_missing_approved_provenance_fails_even_with_recomputed_t010e_hashes() -> None:
    plan = _export_plan()
    record = replace(plan.standard_export.records[0], approval_record_id="")
    provisional_package = replace(
        plan.standard_export,
        records=(record,),
        package_id="pending",
        package_hash="pending",
    )
    package_hash = compute_ncp_export_package_hash(provisional_package._hash_material())
    bad_package = replace(
        provisional_package,
        package_id=f"ncp-standard-export-{package_hash[:32]}",
        package_hash=package_hash,
    )
    provisional_plan = replace(
        plan,
        standard_export=bad_package,
        export_plan_id="pending",
        export_plan_hash="pending",
    )
    plan_hash = compute_ncp_export_plan_hash(provisional_plan._hash_material())
    bad_plan = replace(
        provisional_plan,
        export_plan_id=f"ncp-export-plan-{plan_hash[:32]}",
        export_plan_hash=plan_hash,
    )

    with pytest.raises(NcpExportPreflightValidationError) as error:
        validate_ncp_export_before_export(bad_plan, _schema_interface())
    assert error.value.code == "missing_approved_context_provenance"


def test_recovered_schema_is_applied_to_assembled_standard_document() -> None:
    invalid_story = _approved_story()
    invalid_story.pop("logline")
    record = build_ncp_approved_context_export_record(
        approved_context_record_id="approved-invalid-schema",
        approval_record_id="approval-invalid-schema",
        category="metadata",
        ncp_json_pointer="/story",
        source_value=invalid_story,
    )

    with pytest.raises(NcpExportPreflightValidationError) as error:
        validate_ncp_export_before_export(
            plan_ncp_exports((record,)), _schema_interface()
        )
    assert error.value.code == "schema_validation_failed"
    assert error.value.location == "/story/logline"


@pytest.mark.parametrize(
    ("scope", "sequence"),
    (
        ("signpost", 0),
        ("signpost", 5),
        ("progression", 17),
        ("event", 65),
    ),
)
def test_storybeat_numeric_bound_violations_fail_closed(
    scope: str, sequence: int
) -> None:
    with pytest.raises(NcpExportPreflightValidationError) as error:
        validate_ncp_export_before_export(
            _export_plan_with_storybeat(scope=scope, sequence=sequence),
            _schema_interface(),
        )

    assert error.value.code == "schema_validation_failed"
    assert error.value.location == "/story/narratives/0/subtext/storybeats/0/sequence"


@pytest.mark.parametrize(
    ("scope", "sequence"),
    (
        ("signpost", 1),
        ("signpost", 4),
        ("progression", 16),
        ("event", 64),
    ),
)
def test_storybeat_numeric_boundary_values_remain_valid(
    scope: str, sequence: int
) -> None:
    result = validate_ncp_export_before_export(
        _export_plan_with_storybeat(scope=scope, sequence=sequence),
        _schema_interface(),
    )

    assert result.standard_export_validation.package_exportable is True
    assert result.standard_export_validation.trusted_round_trip_eligible is True
    assert result.trusted_round_trip_provenance.trusted_round_trip_eligible is True


def test_omissions_and_unknowns_remain_metadata_not_deletion_or_approval() -> None:
    plan = _export_plan(include_candidate_bundle=True)
    result = validate_ncp_export_before_export(plan, _schema_interface())
    candidate = plan.candidate_review_bundle
    assert candidate is not None

    assert result.standard_export_validation.omission_policy == NCP_EXPORT_OMISSION_POLICY
    for omission in plan.standard_export.omissions + candidate.omissions:
        assert omission.deletion_intent is False
        assert omission.deletion_operation is False
        assert omission.preserves_existing_context is True
    for metadata in candidate.uninterpreted_source_metadata:
        assert metadata.source_metadata_only is True
        assert metadata.approved_fact is False
        assert metadata.deletion_intent is False


def test_validation_result_is_deterministic_and_nested_tampering_is_detected() -> None:
    plan = _export_plan(include_candidate_bundle=True)
    evidence = _schema_interface()
    first = validate_ncp_export_before_export(plan, evidence)
    second = validate_ncp_export_before_export(plan, evidence)
    assert first == second
    assert first.result_hash == compute_ncp_export_validation_result_hash(first.to_dict())

    tampered = copy.deepcopy(first.to_dict())
    tampered["standard_export_validation"]["package_hash"] = "0" * 64
    tampered["result_hash"] = compute_ncp_export_validation_result_hash(tampered)
    tampered["result_id"] = (
        f"ncp-export-validation-result-{tampered['result_hash'][:32]}"
    )
    with pytest.raises(NcpExportPreflightValidationError) as error:
        validate_ncp_export_validation_result_record(tampered)
    assert error.value.code == "nested_validation_hash_mismatch"


def test_validation_has_no_io_runtime_state_write_or_prose_transformation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    plan = _export_plan(include_candidate_bundle=True)
    evidence = _schema_interface()

    def forbidden(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("forbidden side effect")

    monkeypatch.setattr(builtins, "open", forbidden)
    monkeypatch.setattr(Path, "write_text", forbidden)
    monkeypatch.setattr(Path, "write_bytes", forbidden)
    monkeypatch.setattr(Path, "mkdir", forbidden)
    monkeypatch.setattr(subprocess, "run", forbidden)
    monkeypatch.setattr(subprocess, "Popen", forbidden)
    monkeypatch.setattr(os, "system", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)

    result = validate_ncp_export_before_export(plan, evidence)
    output = json.dumps(result.to_dict(), ensure_ascii=False)
    assert APPROVED_LOG_LINE not in output
    assert PENDING_SOURCE_TEXT not in output
    assert result.safety_boundary == NcpExportValidationSafetyBoundary()
    for validation in (
        result.standard_export_validation,
        result.candidate_review_bundle_validation,
    ):
        if validation is not None:
            assert validation.safety_boundary == NcpExportValidationSafetyBoundary()
            assert validation.safety_boundary.file_write_performed is False
            assert validation.safety_boundary.export_destination_write_performed is False
            assert validation.safety_boundary.project_state_write_performed is False
            assert validation.safety_boundary.candidate_write_performed is False
            assert validation.safety_boundary.review_write_performed is False
            assert validation.safety_boundary.memory_write_performed is False
            assert validation.safety_boundary.canon_write_performed is False
            assert validation.safety_boundary.promotion_performed is False
            assert validation.safety_boundary.apply_promotion_performed is False
            assert validation.safety_boundary.node_execution is False
            assert validation.safety_boundary.npm_execution is False
            assert validation.safety_boundary.subprocess_execution is False
            assert validation.safety_boundary.network_execution is False
            assert validation.safety_boundary.model_execution is False
            assert validation.safety_boundary.generated_prose is False
            assert validation.safety_boundary.prose_transformation is False


def test_external_complete_never_changes_standard_trust_or_approved_content() -> None:
    with_bundle = validate_ncp_export_before_export(
        _export_plan(include_candidate_bundle=True), _schema_interface()
    )
    without_bundle = validate_ncp_export_before_export(
        _export_plan(include_candidate_bundle=False), _schema_interface()
    )

    assert (
        with_bundle.standard_export_validation.package_hash
        == without_bundle.standard_export_validation.package_hash
    )
    assert (
        with_bundle.standard_export_validation.external_status_policy
        == NCP_EXTERNAL_STATUS_POLICY
    )
    assert with_bundle.trusted_round_trip_provenance.local_approval_created is False


def test_serialized_safety_or_trust_escalation_fails_closed() -> None:
    result = validate_ncp_export_before_export(_export_plan(), _schema_interface())
    unsafe = copy.deepcopy(result.to_dict())
    unsafe["trusted_round_trip_provenance"]["external_import_trusted"] = True
    unsafe["result_hash"] = compute_ncp_export_validation_result_hash(unsafe)
    unsafe["result_id"] = f"ncp-export-validation-result-{unsafe['result_hash'][:32]}"

    with pytest.raises(NcpExportPreflightValidationError) as error:
        validate_ncp_export_validation_result_record(unsafe)
    assert error.value.code == "unsafe_round_trip_provenance"


def test_package_safety_remains_app_generated_approved_context_only() -> None:
    plan = _export_plan()
    assert plan.standard_export.safety_boundary == NcpStandardExportSafetyBoundary()
    result = validate_ncp_export_before_export(plan, _schema_interface())
    validation = result.standard_export_validation

    assert validation.app_generated is True
    assert validation.standard_approved_context_export is True
    assert validation.candidate_review_bundle is False
    assert validation.app_provenance_refs
    assert validation.safety_boundary.approval_performed is False
    assert validation.safety_boundary.external_validator_execution is False
