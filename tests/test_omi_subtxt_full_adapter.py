"""Focused T006 official/full Subtxt adapter and integration validation.

All runtime behavior in this file is explicitly mocked.  These tests never
call a real Subtxt runtime, the app-owned Subtxt-informed rubric, a model, or
an external service, and never promote or mutate Memory/Canon.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from backend import omi_analysis_orchestrator as oao
from backend import project_manager
from backend.story_knowledge import raw_artifacts
from backend.story_knowledge.analysis_run_manifest import (
    AdapterProvenance,
    AnalysisRunManifest,
    ArtifactReference,
    ContributorLineage,
    DependencyEdge,
    OperationDeclaration,
    OutputLineage,
    ProvenanceComponent,
)
from backend.story_knowledge.analysis_runtime_integration import (
    SUBTXT_APP_MAPPED_OUTPUT_SCHEMA_VERSION,
    OfficialSubtxtRunnerError,
    OfficialSubtxtRunnerResponse,
    OfficialSubtxtRuntimeIncompatibleError,
    OfficialSubtxtRuntimeTimeoutError,
    OfficialSubtxtRuntimeUnavailableError,
    persist_official_subtxt_execution_evidence,
    run_official_subtxt_adapter,
)
from backend.story_knowledge.evidence_ledger import (
    build_exact_evidence_record,
    scan_evidence_ledger,
)
from backend.story_knowledge.source_map import (
    CHAR_OFFSET_BASIS,
    OffsetRange,
    build_exact_source_snapshot,
    project_candidate_source_locator,
)
from backend.story_knowledge.subtxt_runtime_contract import (
    APP_OWNED_SUBTXT_RUBRIC_ADAPTER_ID,
    APP_OWNED_SUBTXT_RUBRIC_INTERNAL_ID,
    OFFICIAL_SUBTXT_ADAPTER_ID,
    OFFICIAL_SUBTXT_FORBIDDEN_OPERATIONS,
    OFFICIAL_SUBTXT_OPERATION_ID,
    OFFICIAL_SUBTXT_POLICY_PERMITTED_OPERATIONS,
    SubtxtAnalysisRequest,
    SubtxtCapabilitySet,
    SubtxtRuntimeInventory,
    SubtxtRuntimeProvenance,
)


RAW_IDEA = "Owner note identifies a conflict pattern for bounded analysis."
NATIVE_RAW_OUTPUT = b"\xffSUBTXT-NATIVE-ANALYSIS\x00"
CREATED_AT = "2026-09-05T20:00:00Z"


def _component(
    availability: str = "unknown",
    name: str | None = None,
    version: str | None = None,
) -> ProvenanceComponent:
    return ProvenanceComponent(availability, name, version)


def _adapter_provenance(
    adapter_id: str,
    operation_id: str,
    *,
    implementation_kind: str = "unknown",
) -> AdapterProvenance:
    return AdapterProvenance(
        adapter_id=adapter_id,
        operation_id=operation_id,
        user_facing_label=adapter_id,
        implementation_kind=implementation_kind,
        tool=_component(),
        runtime=_component(),
        provider=_component(),
        model=_component(),
    )


def _fixture() -> tuple[SubtxtAnalysisRequest, dict[str, Any]]:
    snapshot = build_exact_source_snapshot(
        project_id="demo",
        source_document_type="omi",
        source_document_id="idea-001",
        source_document_version="1",
        source_ownership="owner_authored",
        source_content=RAW_IDEA,
    )
    evidence = build_exact_evidence_record(
        snapshot=snapshot,
        run_id="run-subtxt-001",
        artifact_id="normalized-evidence-artifact",
        artifact_file_id="normalized-evidence-file",
        operation_id="extract-evidence",
        adapter_id="spacy",
        disposition="validated",
        contributor_state="succeeded",
        character_range=OffsetRange(0, len(RAW_IDEA), CHAR_OFFSET_BASIS),
        created_at=CREATED_AT,
        output_id="normalized-output-1",
    )
    producer = OperationDeclaration(
        operation_id="extract-evidence",
        adapter_id="spacy",
        consumes=("owner_selected_source",),
        produces=("normalized_evidence",),
        configuration={},
        feature_flags={},
    )
    consumer = OperationDeclaration(
        operation_id=OFFICIAL_SUBTXT_OPERATION_ID,
        adapter_id=OFFICIAL_SUBTXT_ADAPTER_ID,
        consumes=("normalized_evidence",),
        produces=("diagnostic_candidate_finding",),
        configuration={},
        feature_flags={},
    )
    normalized_artifact = ArtifactReference(
        artifact_id="normalized-evidence-artifact",
        availability="available",
        source_snapshot_ids=(snapshot.identity.snapshot_id,),
        content_hash="1" * 64,
        hash_algorithm="sha256",
        media_type="application/json",
    )
    source_artifact = ArtifactReference(
        artifact_id="source-artifact",
        availability="available",
        source_snapshot_ids=(snapshot.identity.snapshot_id,),
        content_hash=snapshot.identity.content_hash,
        hash_algorithm="sha256",
        media_type="text/plain",
    )
    output = OutputLineage(
        output_id="normalized-output-1",
        operation_id="extract-evidence",
        source_snapshot_ids=(snapshot.identity.snapshot_id,),
        disposition="validated",
        original_output_reference_id=normalized_artifact.artifact_id,
        evidence_reference_ids=(evidence["evidence_id"],),
        verification_outcome="validated",
    )
    manifest = AnalysisRunManifest(
        run_id="run-subtxt-001",
        project_id="demo",
        sources=(snapshot.identity,),
        operations=(producer, consumer),
        dependency_graph=(
            DependencyEdge(
                "extract-evidence",
                OFFICIAL_SUBTXT_OPERATION_ID,
                "normalized_evidence",
            ),
        ),
        contributors=(
            ContributorLineage(
                operation_id="extract-evidence",
                adapter_id="spacy",
                source_snapshot_ids=(snapshot.identity.snapshot_id,),
                result_state="succeeded",
                coverage="complete",
                explanation="normalized evidence produced",
                provenance=_adapter_provenance("spacy", "extract-evidence"),
                output_ids=(output.output_id,),
            ),
            ContributorLineage(
                operation_id=OFFICIAL_SUBTXT_OPERATION_ID,
                adapter_id=OFFICIAL_SUBTXT_ADAPTER_ID,
                source_snapshot_ids=(snapshot.identity.snapshot_id,),
                result_state="unavailable",
                coverage="none",
                explanation="official runtime execution is a later handoff",
                provenance=_adapter_provenance(
                    OFFICIAL_SUBTXT_ADAPTER_ID,
                    OFFICIAL_SUBTXT_OPERATION_ID,
                    implementation_kind="official_external",
                ),
            ),
        ),
        artifact_references=(normalized_artifact, source_artifact),
        outputs=(output,),
        transformations=(),
        coverage="partial",
        created_at=CREATED_AT,
        finalized_at=CREATED_AT,
        configuration={},
        feature_flags={},
    )
    capabilities = SubtxtCapabilitySet(
        policy_permitted_operations=OFFICIAL_SUBTXT_POLICY_PERMITTED_OPERATIONS,
        runtime_supported_operations=frozenset({OFFICIAL_SUBTXT_OPERATION_ID}),
        currently_available_operations=frozenset({OFFICIAL_SUBTXT_OPERATION_ID}),
    )
    request = SubtxtAnalysisRequest(
        analysis_run_manifest=manifest,
        source_identity=snapshot.identity,
        analysis_run_id=manifest.run_id,
        source_snapshot_id=snapshot.identity.snapshot_id,
        source_content_sha256=snapshot.identity.content_hash,
        source_artifact_reference_id=source_artifact.artifact_id,
        normalized_evidence_reference_ids=(evidence["evidence_id"],),
        operation_id=OFFICIAL_SUBTXT_OPERATION_ID,
        capabilities=capabilities,
        runtime_identity=_component(
            "available", "mock-official-subtxt-runtime", "1.2.3"
        ),
        callable_interface=_component(
            "available", "mock-official-subtxt-analysis-interface", "1"
        ),
    )
    return request, evidence


def _ready_inventory(request: SubtxtAnalysisRequest) -> SubtxtRuntimeInventory:
    return SubtxtRuntimeInventory(
        protected_source_path=".external_sources/subtxt-docs",
        protected_source_state="missing",
        protected_source_classification="not_currently_present",
        installed_package_state="available",
        installed_package_metadata=(("mock-subtxt-runtime", "1.2.3"),),
        executable_state="missing",
        executable_name=None,
        callable_library_state="available",
        callable_local_api_state="missing",
        network_api_state="missing",
        configuration_state="configured",
        configured_variable_names=("OMI_LIVE_SUBTXT_PATH",),
        installation_access_state="available",
        runtime_version_state="available",
        runtime_version="1.2.3",
        provider_state="unknown_unverified",
        provider=None,
        model_state="unknown_unverified",
        model=None,
        model_version=None,
        supported_operation_evidence_state="available",
        compatibility_state="available",
        unsupported_or_unverified_interfaces=("cli", "network_api"),
        capabilities=request.capabilities,
        ready=True,
        readiness_state="available",
        detail="Mock-only verified official-runtime seam for deterministic tests.",
    )


def _runtime_provenance(request: SubtxtAnalysisRequest) -> SubtxtRuntimeProvenance:
    return SubtxtRuntimeProvenance(
        adapter=AdapterProvenance(
            adapter_id=OFFICIAL_SUBTXT_ADAPTER_ID,
            operation_id=OFFICIAL_SUBTXT_OPERATION_ID,
            user_facing_label="Mock official Subtxt analysis",
            implementation_kind="official_external",
            tool=_component("available", "Subtxt", "1.2.3"),
            runtime=request.runtime_identity,
            provider=_component(),
            model=_component(),
        ),
        callable_interface=request.callable_interface,
        safe_configuration_identity=_component(
            "available", "mock-subtxt-safe-analysis-config", "1"
        ),
        analysis_run_id=request.analysis_run_id,
        source_snapshot_ids=(request.source_snapshot_id,),
        transformation_ids=(),
    )


def _candidate_locator(evidence: dict[str, Any]) -> str:
    return json.dumps(
        project_candidate_source_locator(evidence["source_locator"]),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _mapped_output(
    request: SubtxtAnalysisRequest,
    evidence_record: dict[str, Any],
    **finding_overrides: Any,
) -> dict[str, Any]:
    source_locator = _candidate_locator(evidence_record)
    finding = {
        "raw_finding_id": "subtxt-raw-finding-1",
        "candidate_type": "structural_diagnostic",
        "label": "Conflict pattern review",
        "extracted_claim": "The source evidence supports review of a conflict pattern",
        "evidence": [
            {
                "evidence_reference_id": evidence_record["evidence_id"],
                "source_locator": source_locator,
            }
        ],
        "source_locator": source_locator,
        "evidence_reference_ids": [evidence_record["evidence_id"]],
        "support_label": "official Subtxt evidence support only",
    }
    finding.update(finding_overrides)
    return {
        "schema_version": SUBTXT_APP_MAPPED_OUTPUT_SCHEMA_VERSION,
        "analysis_run_id": request.analysis_run_id,
        "source_snapshot_id": request.source_snapshot_id,
        "source_content_sha256": request.source_content_sha256,
        "operation_id": OFFICIAL_SUBTXT_OPERATION_ID,
        "findings": [finding],
    }


def _response(
    request: SubtxtAnalysisRequest,
    evidence: dict[str, Any],
    *,
    output: dict[str, Any] | None = None,
    raw_output: bytes = NATIVE_RAW_OUTPUT,
) -> OfficialSubtxtRunnerResponse:
    mapped = output or _mapped_output(request, evidence)
    return OfficialSubtxtRunnerResponse(
        raw_output=raw_output,
        mapped_output=mapped,
        provenance=_runtime_provenance(request),
    )


def _run_success():
    request, evidence = _fixture()
    calls: list[dict[str, Any]] = []

    def runner(**kwargs: Any) -> OfficialSubtxtRunnerResponse:
        calls.append(kwargs)
        return _response(request, evidence)

    execution = run_official_subtxt_adapter(
        request,
        (evidence,),
        preflight_inventory=_ready_inventory(request),
        runner=runner,
        timeout_seconds=7,
    )
    return request, evidence, execution, calls


def test_valid_mock_success_normalizes_with_exact_identity_and_lineage() -> None:
    request, evidence, execution, calls = _run_success()

    assert len(calls) == 1
    assert calls[0]["timeout_seconds"] == 7.0
    assert calls[0]["normalized_evidence"][0]["evidence_id"] == evidence["evidence_id"]
    assert execution.result.state == "evidence_backed_success"
    assert execution.result.analysis_run_id == request.analysis_run_id
    assert execution.result.source_snapshot_id == request.source_snapshot_id
    assert execution.result.source_content_sha256 == request.source_content_sha256
    assert execution.result.operation_id == "analyze-subtxt"
    assert execution.result.provenance.adapter.adapter_id == "subtxt"
    assert execution.result.provenance.adapter.implementation_kind == "official_external"
    assert execution.raw_output is not None
    assert len(execution.findings) == 1

    finding = execution.findings[0]
    assert oao.validate_normalized_finding(finding)["source_adapter"] == "subtxt"
    assert finding["source_adapter"] == finding["provenance"]["adapter"] == "subtxt"
    assert finding["provenance"]["tool_source"] == "subtxt"
    assert finding["provenance"]["implementation_kind"] == "official_external"
    assert finding["provenance"]["analysis_run_id"] == request.analysis_run_id
    assert finding["provenance"]["source_content_sha256"] == request.source_content_sha256
    assert finding["evidence_refs"] == [evidence["evidence_id"]]
    assert finding["source_locator"] == _candidate_locator(evidence)
    assert finding["evidence"][0]["source_locator"] == _candidate_locator(evidence)
    assert finding["owner_decision"] == {"decision": "pending", "approved": False}
    assert finding["review_status"] == "candidate_review_pending"
    assert finding["uncertainty_label"] is None
    assert execution.transformations[0].input_reference_ids == (
        execution.result.raw_output_reference_id,
        "normalized-output-1",
    )
    assert execution.output_lineage[0].disposition == "validated"
    assert execution.output_lineage[0].evidence_reference_ids == (
        evidence["evidence_id"],
    )
    assert execution.to_dict()["result"]["candidate_conversion_performed"] is True
    assert execution.to_dict()["result"]["candidate_persistence_performed"] is False
    manifest = execution.finalized_manifest
    subtxt_contributor = next(
        item for item in manifest.contributors if item.adapter_id == "subtxt"
    )
    assert manifest.coverage == "complete"
    assert subtxt_contributor.result_state == "succeeded"
    assert subtxt_contributor.coverage == "complete"
    assert subtxt_contributor.output_ids == (
        execution.findings[0]["normalized_finding_id"],
    )
    assert execution.result.raw_output_reference_id in {
        item.artifact_id for item in manifest.artifact_references
    }
    assert execution.transformations[0] in manifest.transformations
    assert execution.output_lineage[0] in manifest.outputs

    guardrail = execution.semantic_guardrail_inputs[0]
    assert guardrail["original_normalized_finding"] == finding
    assert guardrail["guardrail_classification"] is None
    assert guardrail["guardrail_policy_applied"] is False
    assert "supported" not in guardrail
    assert "unsupported" not in guardrail
    assert execution.to_dict()["safety"] == {
        "analysis_only": True,
        "story_prose_generated_or_transformed": False,
        "structural_truth_selected": False,
        "candidate_automatically_approved": False,
        "promotion_performed": False,
        "apply_promotion_performed": False,
        "memory_or_canon_mutated": False,
        "training_or_dataset_artifact_created": False,
        "app_owned_rubric_fallback_performed": False,
    }


def test_mapped_locator_cannot_override_canonical_t003_evidence_grounding() -> None:
    request, evidence = _fixture()
    invented_locator = "source_locator_ref_conflict_pattern"
    output = _mapped_output(
        request,
        evidence,
        source_locator=invented_locator,
        evidence=[
            {
                "evidence_reference_id": evidence["evidence_id"],
                "source_locator": invented_locator,
            }
        ],
    )

    execution = run_official_subtxt_adapter(
        request,
        (evidence,),
        preflight_inventory=_ready_inventory(request),
        runner=lambda **_kwargs: _response(request, evidence, output=output),
    )

    assert execution.result.state == "quarantined"
    assert execution.result.quarantined is True
    assert "canonical T003 evidence" in execution.result.reason
    assert execution.findings == ()


def test_candidate_locator_is_derived_when_app_mapping_makes_no_locator_claim() -> None:
    request, evidence = _fixture()
    output = _mapped_output(request, evidence)
    del output["findings"][0]["source_locator"]
    del output["findings"][0]["evidence"][0]["source_locator"]

    execution = run_official_subtxt_adapter(
        request,
        (evidence,),
        preflight_inventory=_ready_inventory(request),
        runner=lambda **_kwargs: _response(request, evidence, output=output),
    )

    assert execution.result.state == "evidence_backed_success"
    assert execution.findings[0]["source_locator"] == _candidate_locator(evidence)
    assert execution.findings[0]["evidence"][0]["source_locator"] == (
        _candidate_locator(evidence)
    )


def test_native_raw_bytes_are_separate_from_app_owned_mapping_and_lineage() -> None:
    request, evidence = _fixture()
    mapped = _mapped_output(request, evidence)
    serialized_mapping = json.dumps(
        mapped, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")

    execution = run_official_subtxt_adapter(
        request,
        (evidence,),
        preflight_inventory=_ready_inventory(request),
        runner=lambda **_kwargs: _response(
            request,
            evidence,
            output=mapped,
            raw_output=NATIVE_RAW_OUTPUT,
        ),
    )

    assert NATIVE_RAW_OUTPUT != serialized_mapping
    assert execution.raw_output == NATIVE_RAW_OUTPUT
    assert execution.result.state == "evidence_backed_success"
    assert execution.transformations[0].transformation_kind == (
        "official_subtxt_app_mapped_output_normalization"
    )
    assert execution.transformations[0].input_reference_ids[0] == (
        execution.result.raw_output_reference_id
    )
    assert execution.output_lineage[0].original_output_reference_id == (
        execution.result.raw_output_reference_id
    )


@pytest.mark.parametrize(
    "operation_id",
    [*sorted(OFFICIAL_SUBTXT_FORBIDDEN_OPERATIONS), "unnamed-operation"],
)
def test_forbidden_and_unnamed_operations_stop_before_runner(
    operation_id: str,
) -> None:
    request, evidence = _fixture()
    object.__setattr__(request, "operation_id", operation_id)
    calls = 0

    def runner(**_kwargs: Any) -> OfficialSubtxtRunnerResponse:
        nonlocal calls
        calls += 1
        raise AssertionError("runner must not execute")

    with pytest.raises(ValueError, match="forbidden|allowlisted"):
        run_official_subtxt_adapter(
            request,
            (evidence,),
            preflight_inventory=_ready_inventory(request),
            runner=runner,
        )
    assert calls == 0


def test_configuration_support_compatibility_and_availability_remain_separate() -> None:
    request, evidence = _fixture()
    calls = 0

    def runner(**_kwargs: Any) -> OfficialSubtxtRunnerResponse:
        nonlocal calls
        calls += 1
        raise AssertionError("runner must not execute")

    configured_only = copy.deepcopy(_ready_inventory(request).__dict__)
    configured_only.update(
        ready=False,
        readiness_state="unavailable",
        supported_operation_evidence_state="unknown_unverified",
        compatibility_state="unknown_unverified",
    )
    unavailable = SubtxtRuntimeInventory(**configured_only)
    first = run_official_subtxt_adapter(
        request,
        (evidence,),
        preflight_inventory=unavailable,
        runner=runner,
    )
    assert first.result.state == "unavailable_runtime"
    assert first.result.state != "incompatible_runtime"
    assert "not verified" in first.result.reason

    incompatible_values = copy.deepcopy(_ready_inventory(request).__dict__)
    incompatible_values.update(
        ready=False,
        readiness_state="unavailable",
        compatibility_state="incompatible",
    )
    incompatible = SubtxtRuntimeInventory(**incompatible_values)
    second = run_official_subtxt_adapter(
        request,
        (evidence,),
        preflight_inventory=incompatible,
        runner=runner,
    )
    assert second.result.state == "incompatible_runtime"
    assert first.result.state != second.result.state
    assert calls == 0


@pytest.mark.parametrize(
    ("error", "state", "reason_fragment"),
    [
        (OfficialSubtxtRuntimeUnavailableError("missing"), "unavailable_runtime", "failure"),
        (OfficialSubtxtRuntimeIncompatibleError("version"), "incompatible_runtime", "failure"),
        (OfficialSubtxtRuntimeTimeoutError("deadline"), "runtime_failure", "timeout"),
        (OfficialSubtxtRunnerError("failure"), "runtime_failure", "failure"),
    ],
)
def test_mocked_runtime_failures_are_explicit_and_nonproducing(
    error: Exception,
    state: str,
    reason_fragment: str,
) -> None:
    request, evidence = _fixture()

    def runner(**_kwargs: Any) -> OfficialSubtxtRunnerResponse:
        raise error

    execution = run_official_subtxt_adapter(
        request,
        (evidence,),
        preflight_inventory=_ready_inventory(request),
        runner=runner,
    )
    assert execution.result.state == state
    assert reason_fragment in execution.result.reason.lower()
    assert execution.findings == ()
    assert execution.raw_output is None


def test_malformed_output_is_preserved_and_quarantined() -> None:
    request, evidence = _fixture()

    def runner(**_kwargs: Any) -> OfficialSubtxtRunnerResponse:
        return OfficialSubtxtRunnerResponse(
            raw_output=b"not-json",
            mapped_output={},
            provenance=_runtime_provenance(request),
        )

    execution = run_official_subtxt_adapter(
        request,
        (evidence,),
        preflight_inventory=_ready_inventory(request),
        runner=runner,
    )
    assert execution.result.state == "malformed_output"
    assert execution.result.quarantined is True
    assert execution.raw_output == b"not-json"
    assert execution.output_lineage[0].disposition == "quarantined"
    assert execution.findings == ()


def test_malformed_unhashable_evidence_fails_closed_without_escaping() -> None:
    request, evidence = _fixture()
    output = _mapped_output(request, evidence)
    output["findings"][0]["evidence_reference_ids"] = [["not-a-string"]]

    execution = run_official_subtxt_adapter(
        request,
        (evidence,),
        preflight_inventory=_ready_inventory(request),
        runner=lambda **_kwargs: _response(request, evidence, output=output),
    )
    assert execution.result.state == "unsupported_output"
    assert execution.result.quarantined is True
    assert execution.findings == ()


def test_unsafe_output_is_not_rewritten_and_is_quarantined() -> None:
    request, evidence = _fixture()
    unsafe = _mapped_output(request, evidence)
    unsafe["generated_prose"] = "Runtime attempted prohibited story output."

    execution = run_official_subtxt_adapter(
        request,
        (evidence,),
        preflight_inventory=_ready_inventory(request),
        runner=lambda **_kwargs: _response(request, evidence, output=unsafe),
    )
    assert execution.result.state == "unsafe_output"
    assert execution.result.quarantined is True
    assert execution.raw_output == NATIVE_RAW_OUTPUT
    assert execution.findings == ()


@pytest.mark.parametrize("case", ["unsupported_schema", "missing_evidence"])
def test_unsupported_output_and_missing_evidence_fail_closed(case: str) -> None:
    request, evidence = _fixture()
    output = _mapped_output(request, evidence)
    if case == "unsupported_schema":
        output["schema_version"] = "future-unverified-schema"
    else:
        output["findings"][0]["evidence"] = []
        output["findings"][0]["evidence_reference_ids"] = []

    execution = run_official_subtxt_adapter(
        request,
        (evidence,),
        preflight_inventory=_ready_inventory(request),
        runner=lambda **_kwargs: _response(request, evidence, output=output),
    )
    assert execution.result.state == "unsupported_output"
    assert execution.result.quarantined is True
    assert execution.findings == ()


@pytest.mark.parametrize("field", ["analysis_run_id", "source_snapshot_id", "source_content_sha256"])
def test_runtime_source_or_run_mismatch_is_quarantined(field: str) -> None:
    request, evidence = _fixture()
    output = _mapped_output(request, evidence)
    output[field] = "f" * 64 if field == "source_content_sha256" else "mismatch"

    execution = run_official_subtxt_adapter(
        request,
        (evidence,),
        preflight_inventory=_ready_inventory(request),
        runner=lambda **_kwargs: _response(request, evidence, output=output),
    )
    assert execution.result.state == "quarantined"
    assert execution.result.quarantined is True
    assert execution.findings == ()


def test_mismatched_normalized_evidence_stops_before_runtime() -> None:
    request, evidence = _fixture()
    bad = copy.deepcopy(evidence)
    bad["run_id"] = "another-run"
    calls = 0

    def runner(**_kwargs: Any) -> OfficialSubtxtRunnerResponse:
        nonlocal calls
        calls += 1
        raise AssertionError("runner must not execute")

    execution = run_official_subtxt_adapter(
        request,
        (bad,),
        preflight_inventory=_ready_inventory(request),
        runner=runner,
    )
    assert execution.result.state == "quarantined"
    assert calls == 0
    assert execution.raw_output is None


def test_mock_success_is_deterministic_and_has_no_app_owned_fallback() -> None:
    _, _, first, first_calls = _run_success()
    _, _, second, second_calls = _run_success()

    assert first.to_dict() == second.to_dict()
    assert len(first_calls) == len(second_calls) == 1
    serialized = json.dumps(first.to_dict(), sort_keys=True)
    assert APP_OWNED_SUBTXT_RUBRIC_ADAPTER_ID not in serialized
    assert APP_OWNED_SUBTXT_RUBRIC_INTERNAL_ID not in serialized
    assert first.result.provenance.adapter.adapter_id == OFFICIAL_SUBTXT_ADAPTER_ID


def test_raw_artifact_and_evidence_ledger_persistence_reuse_t003(tmp_path: Path) -> None:
    request, evidence, execution, _ = _run_success()
    first = persist_official_subtxt_execution_evidence(
        execution,
        storage_root=tmp_path,
        created_at=CREATED_AT,
    )
    second = persist_official_subtxt_execution_evidence(
        execution,
        storage_root=tmp_path,
        created_at=CREATED_AT,
    )

    assert first == second
    assert first["persistence_status"] == "persisted"
    assert first["candidate_persistence_performed"] is False
    artifact_ref = first["raw_artifact_ref"]
    retained = raw_artifacts.read_immutable_raw_artifact_bundle(
        request.source_identity.project_id,
        artifact_ref["artifact_id"],
        project_dir=tmp_path,
    )
    file_ref = retained["artifact_files"][0]
    assert file_ref["artifact_file_id"] == execution.result.raw_output_reference_id
    assert file_ref["sha256"] == execution.to_dict()["raw_output"]["sha256"]
    assert file_ref["sha256"] == hashlib.sha256(NATIVE_RAW_OUTPUT).hexdigest()
    assert file_ref["media_type"] == "application/octet-stream"
    assert file_ref["encoding"] is None
    assert file_ref["schema_name"] is None
    persisted_payloads = list(tmp_path.rglob("official-subtxt-runtime-output.bin"))
    assert len(persisted_payloads) == 1
    assert persisted_payloads[0].read_bytes() == NATIVE_RAW_OUTPUT
    assert retained["analysis_run_manifest_ref"]["run_id"] == request.analysis_run_id
    assert retained["source_refs"] == [request.source_snapshot_id]
    assert retained["evidence_refs"] == [evidence["evidence_id"]]
    assert retained["adapter_name"] == "subtxt"

    chain = scan_evidence_ledger(
        project_dir=tmp_path / "projects" / "demo",
        project_id="demo",
        run_id=request.analysis_run_id,
    )
    assert [event["event_type"] for event in chain] == [
        "artifact_recorded",
        "output_recorded",
        "contributor_recorded",
    ]
    output_event = chain[1]["payload"]
    assert output_event["evidence_reference_ids"] == [evidence["evidence_id"]]
    assert output_event["transformation_ids"] == [
        execution.transformations[0].transformation_id
    ]
    assert chain[2]["payload"]["adapter_id"] == "subtxt"
    assert chain[2]["payload"]["result_state"] == "succeeded"


def test_quarantined_non_utf8_runtime_bytes_retain_t003_failure_lineage(
    tmp_path: Path,
) -> None:
    request, evidence = _fixture()
    execution = run_official_subtxt_adapter(
        request,
        (evidence,),
        preflight_inventory=_ready_inventory(request),
        runner=lambda **_kwargs: OfficialSubtxtRunnerResponse(
            raw_output=b"\xff\xfe",
            mapped_output={},
            provenance=_runtime_provenance(request),
        ),
    )
    persisted = persist_official_subtxt_execution_evidence(
        execution,
        storage_root=tmp_path,
        created_at=CREATED_AT,
    )
    retained = raw_artifacts.read_immutable_raw_artifact_bundle(
        "demo",
        persisted["raw_artifact_ref"]["artifact_id"],
        project_dir=tmp_path,
    )
    assert retained["artifact_files"][0]["media_type"] == "application/octet-stream"
    assert retained["artifact_files"][0]["relative_path"].endswith(".bin")
    assert retained["artifact_files"][0]["encoding"] is None
    persisted_payloads = list(tmp_path.rglob("official-subtxt-runtime-output.bin"))
    assert len(persisted_payloads) == 1
    assert persisted_payloads[0].read_bytes() == b"\xff\xfe"
    chain = scan_evidence_ledger(
        project_dir=tmp_path / "projects" / "demo",
        project_id="demo",
        run_id=request.analysis_run_id,
    )
    assert chain[1]["payload"]["disposition"] == "quarantined"
    assert chain[2]["payload"]["result_state"] == "failed_closed"


def test_official_findings_use_existing_candidate_persistence_and_group_shape(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _, _, execution, _ = _run_success()
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)
    project_dir = tmp_path / "demo"
    project_dir.mkdir()
    truth_files = {
        project_dir / "bible.json": '{"characters": []}\n',
        project_dir / "storyform.json": '{"storyform": null}\n',
        project_dir / "owner_memory.json": '{"notes": []}\n',
    }
    for path, content_value in truth_files.items():
        path.write_text(content_value, encoding="utf-8")
    idea = project_manager.create_omi_idea("demo", RAW_IDEA)

    first = project_manager.persist_omi_tool_assisted_findings_as_candidates(
        "demo",
        raw_idea=RAW_IDEA,
        source_idea_id=idea["idea_id"],
        findings=list(execution.findings),
    )
    second = project_manager.persist_omi_tool_assisted_findings_as_candidates(
        "demo",
        raw_idea=RAW_IDEA,
        source_idea_id=idea["idea_id"],
        findings=list(execution.findings),
    )
    assert first["persistence_status"] == "persisted"
    assert second["persistence_status"] == "already_persisted"
    assert second["persisted_candidate_ids"] == first["persisted_candidate_ids"]

    summary = project_manager.get_omi_summary("demo")
    assert summary["promotions"] == []
    assert summary["ideas"][0]["linked_candidate_ids"] == first["persisted_candidate_ids"]
    record = summary["candidates"][0]
    content = record["candidate_content"]
    assert record["status"] == "candidate"
    assert record["owner_decision"]["decision"] == "pending"
    assert record["owner_decision"]["approved"] is False
    assert record["owner_decision"]["approval_confirmed"] is False
    assert record["promotion_status"]["eligible"] is False
    assert content["source"] == project_manager.OMI_TOOL_ASSISTED_CANDIDATE_SOURCE
    assert content["source_adapter"] == content["tool_source"] == "subtxt"
    assert content["review_status"] == "candidate_review_pending"
    assert content["provenance"]["implementation_kind"] == "official_external"
    assert content["provenance"]["analysis_run_id"] == execution.request.analysis_run_id
    assert content["provenance"]["source_content_sha256"] == execution.request.source_content_sha256
    assert content["provenance"]["raw_output_reference_id"] == execution.result.raw_output_reference_id
    assert content["provenance"]["transformation_ids"] == [
        execution.transformations[0].transformation_id
    ]
    assert content["evidence"] == list(execution.findings[0]["evidence"])

    grouping_source = (
        Path(__file__).resolve().parents[1] / "frontend/src/omiGroupedReview.js"
    ).read_text(encoding="utf-8")
    assert "content.source_adapter" in grouping_source
    assert "source-adapter:${candidate.sourceAdapter" in grouping_source
    assert "'subtxt'" not in grouping_source
    for path, content_value in truth_files.items():
        assert path.read_text(encoding="utf-8") == content_value


def test_invalid_or_mismatched_findings_write_nothing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _, _, execution, _ = _run_success()
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)
    idea = project_manager.create_omi_idea("demo", RAW_IDEA)
    unsafe = copy.deepcopy(execution.findings[0])
    unsafe["extracted_claim"] = "Rewrite: a polished chapter scene"

    invalid = project_manager.persist_omi_tool_assisted_findings_as_candidates(
        "demo",
        raw_idea=RAW_IDEA,
        source_idea_id=idea["idea_id"],
        findings=[unsafe],
    )
    mismatch = project_manager.persist_omi_tool_assisted_findings_as_candidates(
        "demo",
        raw_idea="different owner input",
        source_idea_id=idea["idea_id"],
        findings=list(execution.findings),
    )
    assert invalid["persistence_status"] == "invalid_finding_failed_closed"
    assert mismatch["persistence_status"] == "source_idea_mismatch"
    summary = project_manager.get_omi_summary("demo")
    assert summary["candidates"] == []
    assert summary["promotions"] == []
    assert not hasattr(project_manager, "apply_omi_promotion")
