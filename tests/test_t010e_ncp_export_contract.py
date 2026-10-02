"""Focused T010E approved-context and candidate-review export tests."""

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
    NCP_CANDIDATE_REVIEW_LABEL,
    NCP_CANDIDATE_REVIEW_PACKAGE_KIND,
    NCP_EXPORT_CONTRACT_VERSION,
    NCP_EXPORT_OMISSION_POLICY,
    NCP_EXPORT_VALIDATION_STATE,
    NCP_STANDARD_EXPORT_LABEL,
    NCP_STANDARD_EXPORT_PACKAGE_KIND,
    NcpApprovedContextExportRecord,
    NcpCandidateReviewBundleSafetyBoundary,
    NcpExportPlanSafetyBoundary,
    NcpExportValidationError,
    NcpStandardExportSafetyBoundary,
    build_ncp_approved_context_export_record,
    compute_ncp_export_package_hash,
    compute_ncp_export_plan_hash,
    plan_ncp_exports,
    validate_ncp_export_plan_record,
)
from backend.story_knowledge.ncp_import_contract import (
    NCP_APP_MAPPING_VERSION,
    SUPPORTED_NCP_SCHEMA_VERSION,
    validate_ncp_import_artifact,
)
from backend.story_knowledge.ncp_mapping_contract import map_validated_ncp_import
from backend.story_knowledge.ncp_provenance_contract import (
    build_ncp_source_provenance,
)


CANDIDATE_SOURCE_PROSE = "Pending imported source prose must not leak into standard export."
APPROVED_SOURCE_PROSE = "Exact owner-approved context is passed through unchanged."


def _candidate_payload() -> dict[str, object]:
    return {
        "schema_version": "1.3.0",
        "future_candidate_field": {"preserve": "source metadata"},
        "story": {
            "id": "story-candidate-t010e",
            "title": "Pending source title",
            "narratives": [
                {
                    "id": "narrative-candidate",
                    "status": "complete",
                    "subtext": {
                        "players": [
                            {
                                "id": "player-candidate",
                                "summary": CANDIDATE_SOURCE_PROSE,
                                "future_player_field": "uninterpreted",
                            }
                        ]
                    },
                }
            ],
        },
    }


def _candidate_plan():
    payload = _candidate_payload()
    validated = validate_ncp_import_artifact(
        json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8"),
        project_id="project-t010e",
        source_reference="owner-selected/imports/t010e.ncp.json",
    )
    mapping = map_validated_ncp_import(validated)
    provenance = build_ncp_source_provenance(validated, mapping)
    return build_ncp_candidate_import_plan(validated, mapping, provenance)


def _approved_records() -> tuple[NcpApprovedContextExportRecord, ...]:
    return (
        build_ncp_approved_context_export_record(
            approved_context_record_id="approved-metadata-001",
            approval_record_id="approval-001",
            category="metadata",
            ncp_json_pointer="/story/title",
            source_value="Approved title",
        ),
        build_ncp_approved_context_export_record(
            approved_context_record_id="approved-player-001",
            approval_record_id="approval-002",
            category="player",
            ncp_json_pointer="/story/narratives/0/subtext/players/0",
            source_value={
                "id": "player-approved",
                "summary": APPROVED_SOURCE_PROSE,
            },
        ),
    )


def test_approved_context_produces_deterministic_standard_export_plan() -> None:
    first = plan_ncp_exports(_approved_records())
    second = plan_ncp_exports(_approved_records())

    assert first == second
    assert first.to_dict() == second.to_dict()
    assert first.contract_version == NCP_EXPORT_CONTRACT_VERSION
    assert first.ncp_schema_version == SUPPORTED_NCP_SCHEMA_VERSION == "1.3.0"
    assert first.app_mapping_version == NCP_APP_MAPPING_VERSION
    assert first.validation_state == NCP_EXPORT_VALIDATION_STATE
    assert first.standard_export.package_kind == NCP_STANDARD_EXPORT_PACKAGE_KIND
    assert first.standard_export.package_label == NCP_STANDARD_EXPORT_LABEL
    assert first.candidate_review_bundle is None
    assert first.export_plan_id == f"ncp-export-plan-{first.export_plan_hash[:32]}"
    assert compute_ncp_export_plan_hash(first.to_dict()) == first.export_plan_hash
    assert validate_ncp_export_plan_record(first.to_dict()) == first.to_dict()
    with pytest.raises(FrozenInstanceError):
        first.export_plan_hash = "changed"  # type: ignore[misc]


def test_standard_export_requires_explicit_approved_context() -> None:
    candidate_plan = _candidate_plan()

    with pytest.raises(NcpExportValidationError) as empty:
        plan_ncp_exports(())
    assert empty.value.code == "approved_context_required"

    with pytest.raises(NcpExportValidationError) as candidate:
        plan_ncp_exports(candidate_plan.candidates)  # type: ignore[arg-type]
    assert candidate.value.code == "approved_context_required"

    pending = replace(_approved_records()[0], owner_approved=False, pending_review=True)
    with pytest.raises(NcpExportValidationError) as pending_error:
        plan_ncp_exports((pending,))
    assert pending_error.value.code == "unapproved_standard_export_input"


def test_candidate_review_bundle_is_optional_and_separately_labeled() -> None:
    candidate_plan = _candidate_plan()
    standard_only = plan_ncp_exports(_approved_records())
    with_bundle = plan_ncp_exports(
        _approved_records(),
        include_candidate_review_bundle=True,
        candidate_import_plan=candidate_plan,
    )

    assert standard_only.candidate_review_bundle is None
    bundle = with_bundle.candidate_review_bundle
    assert bundle is not None
    assert bundle.package_kind == NCP_CANDIDATE_REVIEW_PACKAGE_KIND
    assert bundle.package_label == NCP_CANDIDATE_REVIEW_LABEL
    assert bundle.package_id != with_bundle.standard_export.package_id
    assert with_bundle.packages_separately_labeled is True
    assert with_bundle.candidate_bundle_merged_into_standard is False


def test_pending_candidates_never_leak_into_standard_export() -> None:
    candidate_plan = _candidate_plan()
    result = plan_ncp_exports(
        _approved_records(),
        include_candidate_review_bundle=True,
        candidate_import_plan=candidate_plan,
    )
    standard = result.standard_export.to_dict()
    bundle = result.candidate_review_bundle
    assert bundle is not None

    candidate_ids = {item.candidate_plan_id for item in candidate_plan.candidates}
    standard_text = json.dumps(standard, ensure_ascii=False)
    assert all(candidate_id not in standard_text for candidate_id in candidate_ids)
    assert standard["candidate_source_plan_id"] is None
    assert standard["candidate_review_bundle_id"] is None
    assert standard["safety_boundary"]["candidate_records_included"] is False
    assert {item.candidate_plan_id for item in bundle.records} == candidate_ids


def test_candidate_review_bundle_never_implies_approval_or_promotion() -> None:
    result = plan_ncp_exports(
        _approved_records(),
        include_candidate_review_bundle=True,
        candidate_import_plan=_candidate_plan(),
    )
    bundle = result.candidate_review_bundle
    assert bundle is not None

    assert bundle.approved_context is False
    assert bundle.standard_ncp_export is False
    for record in bundle.records:
        assert record.review_status == "pending_owner_review"
        assert record.candidate_only is True
        assert record.approved_context is False
        assert record.standard_export_eligible is False
        assert record.local_approval is False
        assert record.canon_authority is False
        assert record.memory_authority is False
        assert record.promotion_authority is False
        assert record.apply_promotion_authority is False


def test_external_complete_is_bundle_metadata_and_grants_no_export_authority() -> None:
    result = plan_ncp_exports(
        _approved_records(),
        include_candidate_review_bundle=True,
        candidate_import_plan=_candidate_plan(),
    )
    bundle = result.candidate_review_bundle
    assert bundle is not None
    status = bundle.external_status_metadata[0]

    assert status.external_status == "complete"
    assert status.source_metadata_only is True
    assert status.candidate_truth is False
    assert status.local_approval is False
    assert status.canon_authority is False
    assert status.promotion_authority is False
    assert status.apply_promotion_authority is False
    assert result.standard_export.candidate_source_plan_id is None
    assert result.standard_export.safety_boundary.external_status_grants_approval is False


def test_standard_and_candidate_packages_have_distinct_safety_contracts() -> None:
    result = plan_ncp_exports(
        _approved_records(),
        include_candidate_review_bundle=True,
        candidate_import_plan=_candidate_plan(),
    )
    bundle = result.candidate_review_bundle
    assert bundle is not None

    assert result.safety_boundary == NcpExportPlanSafetyBoundary()
    assert result.standard_export.safety_boundary == NcpStandardExportSafetyBoundary()
    assert bundle.safety_boundary == NcpCandidateReviewBundleSafetyBoundary()
    assert result.standard_export.safety_boundary.approved_context_only is True
    assert bundle.safety_boundary.approved_context is False
    assert bundle.safety_boundary.standard_ncp_export is False
    assert bundle.safety_boundary.merged_into_standard_export is False


def test_candidate_bundle_cannot_be_silently_included_or_merged() -> None:
    candidate_plan = _candidate_plan()
    with pytest.raises(NcpExportValidationError) as unrequested:
        plan_ncp_exports(
            _approved_records(),
            candidate_import_plan=candidate_plan,
        )
    assert unrequested.value.code == "candidate_bundle_not_requested"

    plan = plan_ncp_exports(
        _approved_records(),
        include_candidate_review_bundle=True,
        candidate_import_plan=candidate_plan,
    )
    merged = copy.deepcopy(plan.to_dict())
    merged["candidate_bundle_merged_into_standard"] = True
    merged["export_plan_hash"] = compute_ncp_export_plan_hash(merged)
    merged["export_plan_id"] = f"ncp-export-plan-{merged['export_plan_hash'][:32]}"
    with pytest.raises(NcpExportValidationError) as merged_error:
        validate_ncp_export_plan_record(merged)
    assert merged_error.value.code == "unsupported_export_contract"


def test_omitted_and_unmapped_categories_are_metadata_not_deletion() -> None:
    result = plan_ncp_exports(_approved_records())
    omitted = result.standard_export.omissions

    assert {item.category for item in omitted}.isdisjoint({"metadata", "player"})
    assert omitted
    for item in omitted:
        assert item.omission_state == "omitted"
        assert item.reason == "no_explicit_approved_context_record"
        assert item.deletion_intent is False
        assert item.deletion_operation is False
        assert item.preserves_existing_context is True
        assert item.omission_policy == NCP_EXPORT_OMISSION_POLICY


def test_unknown_candidate_metadata_is_not_approved_unless_explicitly_supplied() -> None:
    candidate_plan = _candidate_plan()
    result = plan_ncp_exports(
        _approved_records(),
        include_candidate_review_bundle=True,
        candidate_import_plan=candidate_plan,
    )
    bundle = result.candidate_review_bundle
    assert bundle is not None
    standard_pointers = {
        record.ncp_json_pointer for record in result.standard_export.records
    }
    candidate_unknown_pointers = {
        item.json_pointer for item in bundle.uninterpreted_source_metadata
    }

    assert "/future_candidate_field" in candidate_unknown_pointers
    assert "/future_candidate_field" not in standard_pointers
    assert all(item.approved_fact is False for item in bundle.uninterpreted_source_metadata)
    assert all(
        item.standard_export_eligible is False
        for item in bundle.uninterpreted_source_metadata
    )

    explicit = build_ncp_approved_context_export_record(
        approved_context_record_id="approved-future-001",
        approval_record_id="approval-future-001",
        category="metadata",
        ncp_json_pointer="/story/future_approved_field",
        source_value={"owner": "approved for exchange"},
    )
    explicitly_approved = plan_ncp_exports(_approved_records() + (explicit,))
    assert "/story/future_approved_field" in {
        record.ncp_json_pointer
        for record in explicitly_approved.standard_export.records
    }


def test_export_packages_are_version_pinned_and_tamper_evident() -> None:
    plan = plan_ncp_exports(
        _approved_records(),
        include_candidate_review_bundle=True,
        candidate_import_plan=_candidate_plan(),
    )
    standard = plan.standard_export
    bundle = plan.candidate_review_bundle
    assert bundle is not None

    assert standard.ncp_schema_version == bundle.ncp_schema_version == "1.3.0"
    assert standard.app_mapping_version == bundle.app_mapping_version
    assert compute_ncp_export_package_hash(standard.to_dict()) == standard.package_hash
    assert compute_ncp_export_package_hash(bundle.to_dict()) == bundle.package_hash
    assert validate_ncp_export_plan_record(plan.to_dict()) == plan.to_dict()

    tampered = copy.deepcopy(plan.to_dict())
    tampered["standard_export"]["records"][0]["source_value"] = "tampered"
    tampered["standard_export"]["package_hash"] = compute_ncp_export_package_hash(
        tampered["standard_export"]
    )
    tampered["standard_export"]["package_id"] = (
        f"ncp-standard-export-{tampered['standard_export']['package_hash'][:32]}"
    )
    tampered["export_plan_hash"] = compute_ncp_export_plan_hash(tampered)
    tampered["export_plan_id"] = f"ncp-export-plan-{tampered['export_plan_hash'][:32]}"
    with pytest.raises(NcpExportValidationError) as error:
        validate_ncp_export_plan_record(tampered)
    assert error.value.code == "approved_value_hash_mismatch"


def test_export_records_remain_category_aware_not_story_fact() -> None:
    result = plan_ncp_exports(
        _approved_records(),
        include_candidate_review_bundle=True,
        candidate_import_plan=_candidate_plan(),
    )
    bundle = result.candidate_review_bundle
    assert bundle is not None

    assert {item.category for item in result.standard_export.records} == {
        "metadata",
        "player",
    }
    assert all(item.category != "story_fact" for item in result.standard_export.records)
    assert all("story_fact" not in item.candidate_type for item in bundle.records)


def test_approved_values_are_passed_through_without_prose_transformation() -> None:
    records = _approved_records()
    result = plan_ncp_exports(records)
    player = next(
        item for item in result.standard_export.records if item.category == "player"
    )

    assert player.source_value == records[1].source_value
    assert player.source_value["summary"] == APPROVED_SOURCE_PROSE
    assert result.standard_export.safety_boundary.generated_prose is False
    assert result.standard_export.safety_boundary.prose_transformation is False


def test_candidate_source_prose_is_not_copied_into_review_bundle() -> None:
    result = plan_ncp_exports(
        _approved_records(),
        include_candidate_review_bundle=True,
        candidate_import_plan=_candidate_plan(),
    )
    bundle = result.candidate_review_bundle
    assert bundle is not None

    assert CANDIDATE_SOURCE_PROSE not in json.dumps(bundle.to_dict(), ensure_ascii=False)
    assert bundle.safety_boundary.generated_prose is False
    assert bundle.safety_boundary.prose_transformation is False


def test_export_planning_performs_no_io_runtime_network_model_or_write(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    approved = _approved_records()
    candidate_plan = _candidate_plan()
    calls: list[str] = []

    def forbidden(name: str):
        def _fail(*args, **kwargs):
            calls.append(name)
            raise AssertionError(f"forbidden side effect: {name}")

        return _fail

    monkeypatch.setattr(builtins, "open", forbidden("open"))
    monkeypatch.setattr(Path, "write_text", forbidden("Path.write_text"))
    monkeypatch.setattr(Path, "write_bytes", forbidden("Path.write_bytes"))
    monkeypatch.setattr(Path, "mkdir", forbidden("Path.mkdir"))
    monkeypatch.setattr(subprocess, "run", forbidden("subprocess.run"))
    monkeypatch.setattr(subprocess, "Popen", forbidden("subprocess.Popen"))
    monkeypatch.setattr(subprocess, "check_call", forbidden("subprocess.check_call"))
    monkeypatch.setattr(subprocess, "check_output", forbidden("subprocess.check_output"))
    monkeypatch.setattr(socket, "create_connection", forbidden("socket.create_connection"))
    monkeypatch.setattr(os, "system", forbidden("os.system"))

    result = plan_ncp_exports(
        approved,
        include_candidate_review_bundle=True,
        candidate_import_plan=candidate_plan,
    )

    assert calls == []
    assert result.safety_boundary == NcpExportPlanSafetyBoundary()
    for boundary in (
        result.safety_boundary.to_dict(),
        result.standard_export.safety_boundary.to_dict(),
        result.candidate_review_bundle.safety_boundary.to_dict(),
    ):
        for field in (
            "file_write_performed",
            "project_state_write_performed",
            "candidate_write_performed",
            "review_write_performed",
            "memory_write_performed",
            "canon_write_performed",
            "promotion_performed",
            "apply_promotion_performed",
            "generated_prose",
            "prose_transformation",
            "live_ncp_execution",
            "node_execution",
            "npm_execution",
            "subprocess_execution",
            "network_execution",
            "model_execution",
            "validator_execution",
        ):
            if field in boundary:
                assert boundary[field] is False
