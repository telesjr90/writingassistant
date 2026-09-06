from __future__ import annotations

from pathlib import Path

import pytest

from backend import omi_runtime_preflight
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
from backend.story_knowledge.source_map import build_exact_source_snapshot
from backend.story_knowledge.subtxt_informed_semantic_rubric_contract import (
    SUBTXT_INFORMED_RUBRIC_ID,
)
from backend.story_knowledge.subtxt_runtime_contract import (
    APP_OWNED_SUBTXT_RUBRIC_ADAPTER_ID,
    APP_OWNED_SUBTXT_RUBRIC_INTERNAL_ID,
    CURRENT_SUBTXT_CAPABILITIES,
    OFFICIAL_SUBTXT_ADAPTER_ID,
    OFFICIAL_SUBTXT_FORBIDDEN_OPERATIONS,
    OFFICIAL_SUBTXT_OPERATION_ID,
    OFFICIAL_SUBTXT_POLICY_PERMITTED_OPERATIONS,
    SUBTXT_RESULT_STATES,
    SubtxtAnalysisRequest,
    SubtxtAnalysisResult,
    SubtxtCapabilitySet,
    SubtxtRuntimeContractError,
    SubtxtRuntimeProvenance,
    discover_official_subtxt_runtime,
    unknown_official_subtxt_provenance,
)


def _component(
    availability: str = "unknown",
    name: str | None = None,
    version: str | None = None,
) -> ProvenanceComponent:
    return ProvenanceComponent(availability, name, version)


def _adapter_provenance(
    operation_id: str,
    adapter_id: str,
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


def _manifest_and_source() -> tuple[AnalysisRunManifest, object]:
    snapshot = build_exact_source_snapshot(
        project_id="project-1",
        source_document_type="omi",
        source_document_id="owner-source-1",
        source_document_version="1",
        source_ownership="owner_authored",
        source_content="Owner-authored analysis input.",
    )
    source = snapshot.identity
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
    raw = ArtifactReference(
        artifact_id="normalized-evidence-artifact",
        availability="available",
        source_snapshot_ids=(source.snapshot_id,),
        content_hash="1" * 64,
        hash_algorithm="sha256",
        media_type="application/json",
    )
    source_artifact = ArtifactReference(
        artifact_id="source-artifact",
        availability="available",
        source_snapshot_ids=(source.snapshot_id,),
        content_hash=source.content_hash,
        hash_algorithm="sha256",
        media_type="text/plain",
    )
    output = OutputLineage(
        output_id="normalized-output-1",
        operation_id="extract-evidence",
        source_snapshot_ids=(source.snapshot_id,),
        disposition="validated",
        original_output_reference_id=raw.artifact_id,
        evidence_reference_ids=("evidence-1",),
        verification_outcome="validated",
    )
    manifest = AnalysisRunManifest(
        run_id="run-1",
        project_id=source.project_id,
        sources=(source,),
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
                source_snapshot_ids=(source.snapshot_id,),
                result_state="succeeded",
                coverage="complete",
                explanation="normalized evidence produced",
                provenance=_adapter_provenance("extract-evidence", "spacy"),
                output_ids=(output.output_id,),
            ),
            ContributorLineage(
                operation_id=OFFICIAL_SUBTXT_OPERATION_ID,
                adapter_id=OFFICIAL_SUBTXT_ADAPTER_ID,
                source_snapshot_ids=(source.snapshot_id,),
                result_state="unavailable",
                coverage="none",
                explanation="runtime not invoked",
                provenance=_adapter_provenance(
                    OFFICIAL_SUBTXT_OPERATION_ID,
                    OFFICIAL_SUBTXT_ADAPTER_ID,
                    implementation_kind="official_external",
                ),
            ),
        ),
        artifact_references=(raw, source_artifact),
        outputs=(output,),
        transformations=(),
        coverage="partial",
        created_at="2026-09-04T00:00:00Z",
        finalized_at="2026-09-04T00:00:00Z",
        configuration={},
        feature_flags={},
    )
    return manifest, source


def _available_capabilities() -> SubtxtCapabilitySet:
    return SubtxtCapabilitySet(
        policy_permitted_operations=OFFICIAL_SUBTXT_POLICY_PERMITTED_OPERATIONS,
        runtime_supported_operations=frozenset({OFFICIAL_SUBTXT_OPERATION_ID}),
        currently_available_operations=frozenset({OFFICIAL_SUBTXT_OPERATION_ID}),
    )


def _request(**overrides: object) -> SubtxtAnalysisRequest:
    manifest, source = _manifest_and_source()
    values = {
        "analysis_run_manifest": manifest,
        "source_identity": source,
        "analysis_run_id": manifest.run_id,
        "source_snapshot_id": source.snapshot_id,
        "source_content_sha256": source.content_hash,
        "source_artifact_reference_id": "source-artifact",
        "normalized_evidence_reference_ids": ("evidence-1",),
        "operation_id": OFFICIAL_SUBTXT_OPERATION_ID,
        "capabilities": _available_capabilities(),
        "runtime_identity": _component(
            "available", "verified-official-subtxt-runtime", "verified-version"
        ),
        "callable_interface": _component(
            "available", "verified-official-subtxt-interface", "1"
        ),
    }
    values.update(overrides)
    return SubtxtAnalysisRequest(**values)


def _known_provenance() -> SubtxtRuntimeProvenance:
    manifest, source = _manifest_and_source()
    return SubtxtRuntimeProvenance(
        adapter=AdapterProvenance(
            adapter_id=OFFICIAL_SUBTXT_ADAPTER_ID,
            operation_id=OFFICIAL_SUBTXT_OPERATION_ID,
            user_facing_label="Official Subtxt analysis",
            implementation_kind="official_external",
            tool=_component("available", "Subtxt"),
            runtime=_component("available", "Subtxt runtime", "verified-version"),
            provider=_component("unknown"),
            model=_component("unknown"),
        ),
        callable_interface=_component("available", "verified-interface", "1"),
        safe_configuration_identity=_component("unknown"),
        analysis_run_id=manifest.run_id,
        source_snapshot_ids=(source.snapshot_id,),
        transformation_ids=("transform-1",),
    )


def test_official_and_app_owned_subtxt_identities_are_distinct() -> None:
    assert OFFICIAL_SUBTXT_ADAPTER_ID == "subtxt"
    assert APP_OWNED_SUBTXT_RUBRIC_ADAPTER_ID == "subtxt_informed_rubric"
    assert APP_OWNED_SUBTXT_RUBRIC_INTERNAL_ID == SUBTXT_INFORMED_RUBRIC_ID
    assert OFFICIAL_SUBTXT_ADAPTER_ID not in {
        APP_OWNED_SUBTXT_RUBRIC_ADAPTER_ID,
        APP_OWNED_SUBTXT_RUBRIC_INTERNAL_ID,
    }


def test_policy_runtime_support_and_current_availability_are_distinct() -> None:
    assert CURRENT_SUBTXT_CAPABILITIES.policy_permitted_operations == {
        OFFICIAL_SUBTXT_OPERATION_ID
    }
    assert CURRENT_SUBTXT_CAPABILITIES.runtime_supported_operations == frozenset()
    assert CURRENT_SUBTXT_CAPABILITIES.currently_available_operations == frozenset()
    with pytest.raises(SubtxtRuntimeContractError, match="supported"):
        CURRENT_SUBTXT_CAPABILITIES.require_available(OFFICIAL_SUBTXT_OPERATION_ID)


def test_unknown_operation_is_rejected_by_positive_allowlist() -> None:
    with pytest.raises(SubtxtRuntimeContractError, match="positively allowed"):
        _available_capabilities().require_available("unknown-operation")


@pytest.mark.parametrize("operation_id", sorted(OFFICIAL_SUBTXT_FORBIDDEN_OPERATIONS))
def test_every_named_generation_rewrite_mutation_operation_is_rejected(
    operation_id: str,
) -> None:
    with pytest.raises(SubtxtRuntimeContractError, match="forbidden"):
        _available_capabilities().require_available(operation_id)


def test_runtime_supported_and_available_sets_cannot_bypass_policy() -> None:
    with pytest.raises(SubtxtRuntimeContractError, match="policy permitted"):
        SubtxtCapabilitySet(
            policy_permitted_operations=OFFICIAL_SUBTXT_POLICY_PERMITTED_OPERATIONS,
            runtime_supported_operations=frozenset({"rewrite-story-prose"}),
            currently_available_operations=frozenset({"rewrite-story-prose"}),
        )


def test_configured_path_command_package_or_executable_cannot_report_ready(
    tmp_path: Path,
) -> None:
    inventory = discover_official_subtxt_runtime(
        repo_root=tmp_path,
        env={
            "OMI_LIVE_SUBTXT_COMMAND": "subtxt",
            "OMI_LIVE_SUBTXT_PATH": "/opt/subtxt",
        },
        distribution_records=(("subtxt-runtime", "9.9"),),
        executable_path="/usr/local/bin/subtxt",
    )
    assert inventory.configuration_state == "configured"
    assert inventory.installed_package_state == "available"
    assert inventory.executable_state == "available"
    assert inventory.callable_library_state == "unknown_unverified"
    assert inventory.runtime_version is None
    assert inventory.ready is False
    assert inventory.readiness_state == "unavailable"
    assert inventory.capabilities.currently_available_operations == frozenset()
    assert inventory.to_dict()["configuration_values_exposed"] is False


def test_blank_known_configuration_is_malformed_and_not_ready(tmp_path: Path) -> None:
    inventory = discover_official_subtxt_runtime(
        repo_root=tmp_path,
        env={"OMI_LIVE_SUBTXT_COMMAND": "   "},
        distribution_records=(),
        executable_path="",
    )
    assert inventory.configuration_state == "malformed_configuration"
    assert inventory.ready is False


def test_current_bounded_machine_inventory_is_precise_and_non_ready() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    inventory = discover_official_subtxt_runtime(repo_root=repo_root, env={})
    assert inventory.protected_source_state == "missing"
    assert inventory.installed_package_state == "missing"
    assert inventory.executable_state == "missing"
    assert inventory.configuration_state == "missing"
    assert inventory.callable_library_state == "missing"
    assert inventory.network_api_state == "unknown_unverified"
    assert inventory.provider_state == "unknown_unverified"
    assert inventory.model_state == "unknown_unverified"
    assert inventory.compatibility_state == "unknown_unverified"
    assert inventory.ready is False
    assert inventory.readiness_state == "unavailable"


def test_omi_preflight_exposes_official_inventory_without_claiming_readiness() -> None:
    dependency = omi_runtime_preflight._dependency_probe(
        "subtxt",
        {
            "OMI_LIVE_SUBTXT_COMMAND": "subtxt",
            "OMI_LIVE_SUBTXT_PATH": "/opt/subtxt",
        },
    )
    inventory = dependency["subtxt_official_runtime_inventory"]
    assert dependency["runtime_configured"] is True
    assert dependency["runtime_dependency_available"] is False
    assert dependency["runtime_dependency_status"] == "unavailable"
    assert inventory["configuration_state"] == "configured"
    assert inventory["configuration_values_exposed"] is False
    assert inventory["ready"] is False
    assert inventory["capabilities"]["runtime_supported_operations"] == []
    assert inventory["capabilities"]["currently_available_operations"] == []


def test_discovery_does_not_invoke_runtime_network_or_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    before = tuple(tmp_path.iterdir())

    def forbidden(*args: object, **kwargs: object) -> object:
        raise AssertionError("runtime/network/process entry point called")

    monkeypatch.setattr("subprocess.run", forbidden)
    monkeypatch.setattr("subprocess.Popen", forbidden)
    monkeypatch.setattr("urllib.request.urlopen", forbidden)
    monkeypatch.setattr("importlib.import_module", forbidden)
    inventory = discover_official_subtxt_runtime(
        repo_root=tmp_path,
        env={},
        distribution_records=(),
        executable_path="",
    )
    assert inventory.ready is False
    assert tuple(tmp_path.iterdir()) == before


def test_request_reuses_t002_t003_run_source_artifact_and_evidence_links() -> None:
    request = _request()
    value = request.to_dict()
    assert value["analysis_run_id"] == request.analysis_run_manifest.run_id
    assert value["source_identity"] == request.source_identity.to_dict()
    assert value["source_snapshot_id"] == request.source_identity.snapshot_id
    assert value["source_content_sha256"] == request.source_identity.content_hash
    assert value["source_artifact_reference_id"] == "source-artifact"
    assert value["normalized_evidence_reference_ids"] == ["evidence-1"]
    assert value["adapter_identity"] == "subtxt"
    assert value["analysis_intent"] == "analysis_only"


@pytest.mark.parametrize(
    ("field", "value", "message"),
    (
        ("analysis_run_id", "other-run", "run linkage"),
        ("source_snapshot_id", "other-snapshot", "snapshot linkage"),
        ("source_content_sha256", "0" * 64, "SHA-256"),
        ("source_artifact_reference_id", "missing-artifact", "unknown"),
        ("normalized_evidence_reference_ids", ("missing-evidence",), "not declared"),
        ("analysis_intent", "generate_story", "analysis-only"),
        ("adapter_identity", "subtxt_informed_rubric", "identity mismatch"),
    ),
)
def test_request_linkage_and_analysis_only_mismatches_fail_closed(
    field: str, value: object, message: str
) -> None:
    with pytest.raises(SubtxtRuntimeContractError, match=message):
        _request(**{field: value})


def test_request_rejects_current_unverified_operation_support() -> None:
    with pytest.raises(SubtxtRuntimeContractError, match="supported"):
        _request(capabilities=CURRENT_SUBTXT_CAPABILITIES)


@pytest.mark.parametrize("field", ("runtime_identity", "callable_interface"))
def test_request_requires_verified_runtime_and_callable_interface(field: str) -> None:
    with pytest.raises(SubtxtRuntimeContractError, match="verified available"):
        _request(**{field: _component("unknown")})


def test_unknown_provenance_stays_unknown_without_synthesized_values() -> None:
    manifest, source = _manifest_and_source()
    provenance = unknown_official_subtxt_provenance(
        analysis_run_id=manifest.run_id,
        operation_id=OFFICIAL_SUBTXT_OPERATION_ID,
        source_snapshot_ids=(source.snapshot_id,),
    )
    value = provenance.to_dict()
    for plane in ("tool", "runtime", "provider", "model"):
        assert value["adapter"][plane] == {
            "availability": "unknown",
            "name": None,
            "version": None,
        }
    assert value["callable_interface"]["availability"] == "unknown"


def test_unknown_operation_cannot_enter_official_result_provenance() -> None:
    manifest, source = _manifest_and_source()
    with pytest.raises(SubtxtRuntimeContractError, match="operation mismatch"):
        unknown_official_subtxt_provenance(
            analysis_run_id=manifest.run_id,
            operation_id="unknown-operation",
            source_snapshot_ids=(source.snapshot_id,),
        )


def test_official_provenance_cannot_claim_app_owned_identity() -> None:
    manifest, source = _manifest_and_source()
    fake = AdapterProvenance(
        adapter_id=OFFICIAL_SUBTXT_ADAPTER_ID,
        operation_id=OFFICIAL_SUBTXT_OPERATION_ID,
        user_facing_label="fake",
        implementation_kind="official_external",
        tool=_component("available", APP_OWNED_SUBTXT_RUBRIC_INTERNAL_ID),
        runtime=_component(),
        provider=_component(),
        model=_component(),
    )
    with pytest.raises(SubtxtRuntimeContractError, match="impersonate"):
        SubtxtRuntimeProvenance(
            adapter=fake,
            callable_interface=_component(),
            safe_configuration_identity=_component(),
            analysis_run_id=manifest.run_id,
            source_snapshot_ids=(source.snapshot_id,),
            transformation_ids=(),
        )


def test_app_owned_provenance_cannot_impersonate_official_subtxt() -> None:
    manifest, source = _manifest_and_source()
    app_owned = _adapter_provenance(
        OFFICIAL_SUBTXT_OPERATION_ID,
        APP_OWNED_SUBTXT_RUBRIC_ADAPTER_ID,
        implementation_kind="app_owned",
    )
    with pytest.raises(SubtxtRuntimeContractError, match="identity mismatch"):
        SubtxtRuntimeProvenance(
            adapter=app_owned,
            callable_interface=_component(),
            safe_configuration_identity=_component(),
            analysis_run_id=manifest.run_id,
            source_snapshot_ids=(source.snapshot_id,),
            transformation_ids=(),
        )


@pytest.mark.parametrize("state", sorted(SUBTXT_RESULT_STATES - {"evidence_backed_success"}))
def test_non_success_result_states_remain_explicit_and_fail_closed(state: str) -> None:
    manifest, source = _manifest_and_source()
    provenance = unknown_official_subtxt_provenance(
        analysis_run_id=manifest.run_id,
        operation_id=OFFICIAL_SUBTXT_OPERATION_ID,
        source_snapshot_ids=(source.snapshot_id,),
    )
    quarantined = state in {
        "unsupported_output",
        "malformed_output",
        "unsafe_output",
        "quarantined",
    }
    result = SubtxtAnalysisResult(
        state=state,
        analysis_run_id=manifest.run_id,
        source_snapshot_id=source.snapshot_id,
        source_content_sha256=source.content_hash,
        operation_id=OFFICIAL_SUBTXT_OPERATION_ID,
        provenance=provenance,
        raw_output_reference_id="raw-output-1" if state == "uncertainty" else None,
        reason="explicit non-success reason",
        quarantined=quarantined,
    )
    value = result.to_dict()
    assert value["state"] == state
    assert value["candidate_conversion_performed"] is False
    assert value["candidate_persistence_performed"] is False
    assert value["safety"]["result_is_truth_or_canon"] is False


def test_evidence_backed_success_requires_known_runtime_interface_and_evidence() -> None:
    manifest, source = _manifest_and_source()
    result = SubtxtAnalysisResult(
        state="evidence_backed_success",
        analysis_run_id=manifest.run_id,
        source_snapshot_id=source.snapshot_id,
        source_content_sha256=source.content_hash,
        operation_id=OFFICIAL_SUBTXT_OPERATION_ID,
        provenance=_known_provenance(),
        raw_output_reference_id="raw-output-1",
        evidence_reference_ids=("evidence-1",),
        transformation_ids=("transform-1",),
    )
    value = result.to_dict()
    assert value["output_disposition"] == "validated"
    assert all(
        flag is False
        for name, flag in value["safety"].items()
        if name != "analysis_only"
    )
    assert value["safety"]["analysis_only"] is True


def test_success_cannot_use_unknown_runtime_or_missing_evidence() -> None:
    manifest, source = _manifest_and_source()
    unknown = unknown_official_subtxt_provenance(
        analysis_run_id=manifest.run_id,
        operation_id=OFFICIAL_SUBTXT_OPERATION_ID,
        source_snapshot_ids=(source.snapshot_id,),
    )
    with pytest.raises(SubtxtRuntimeContractError, match="evidence references"):
        SubtxtAnalysisResult(
            state="evidence_backed_success",
            analysis_run_id=manifest.run_id,
            source_snapshot_id=source.snapshot_id,
            source_content_sha256=source.content_hash,
            operation_id=OFFICIAL_SUBTXT_OPERATION_ID,
            provenance=unknown,
            raw_output_reference_id="raw-output-1",
        )


def test_public_contract_has_no_runtime_invocation_or_persistence_api() -> None:
    from backend.story_knowledge import subtxt_runtime_contract as contract

    exported = set(contract.__all__)
    forbidden_prefixes = ("run_", "invoke_", "execute_", "persist_", "promote_")
    assert not any(name.startswith(forbidden_prefixes) for name in exported)
