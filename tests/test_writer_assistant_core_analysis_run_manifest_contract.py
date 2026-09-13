"""Deterministic T002 source identity and AnalysisRunManifest contracts."""

from dataclasses import FrozenInstanceError
import json

import pytest

from backend.story_knowledge.analysis_run_manifest import (
    ADAPTER_RESULT_STATES,
    ANALYSIS_RUN_MANIFEST_CONTRACT_VERSION,
    AdapterProvenance,
    AnalysisRunManifest,
    AnalysisRunManifestValidationError,
    ArtifactReference,
    ContributorLineage,
    DependencyEdge,
    OperationDeclaration,
    OutputLineage,
    ProvenanceComponent,
    TransformationLineage,
)
from backend.story_knowledge.source_map import build_exact_source_snapshot


UNKNOWN = ProvenanceComponent("unknown")
UNAVAILABLE = ProvenanceComponent("unavailable")


def source(*, document_id="scene_001", text="Owner source.", scene_id="scene_001"):
    return build_exact_source_snapshot(
        project_id="example",
        source_document_type="scene",
        source_document_id=document_id,
        source_document_version="1",
        source_ownership="owner_authored",
        source_content=text,
        scene_id=scene_id,
        source_map_id=f"map-{document_id}",
    ).identity


def operation(
    operation_id="extract",
    adapter_id="ollama_model",
    *,
    consumes=("owner_selected_source",),
    produces=("diagnostic_candidate_finding",),
):
    return OperationDeclaration(
        operation_id=operation_id,
        adapter_id=adapter_id,
        consumes=consumes,
        produces=produces,
        configuration={"temperature": 0, "nested": {"mode": "analysis"}},
        feature_flags={"exact_source": True},
    )


def provenance(operation_id="extract", adapter_id="ollama_model", **overrides):
    values = {
        "adapter_id": adapter_id,
        "operation_id": operation_id,
        "user_facing_label": "Exact-source structured analysis",
        "implementation_kind": "app_owned",
        "tool": ProvenanceComponent("available", "writer-assistant-adapter", "1"),
        "runtime": ProvenanceComponent("available", "python", "3"),
        "provider": UNKNOWN,
        "model": UNKNOWN,
    }
    values.update(overrides)
    return AdapterProvenance(**values)


def contributor(
    source_id,
    operation_id="extract",
    adapter_id="ollama_model",
    *,
    state="succeeded",
    coverage="complete",
    output_ids=("finding-001",),
    actual_provenance=None,
):
    return ContributorLineage(
        operation_id=operation_id,
        adapter_id=adapter_id,
        source_snapshot_ids=(source_id,),
        result_state=state,
        coverage=coverage,
        explanation="Attributable deterministic contract result.",
        provenance=actual_provenance
        or provenance(operation_id=operation_id, adapter_id=adapter_id),
        output_ids=output_ids,
    )


def manifest(**overrides):
    identity = source()
    artifact = ArtifactReference(
        artifact_id="raw-001",
        availability="available",
        source_snapshot_ids=(identity.snapshot_id,),
        content_hash="a" * 64,
        hash_algorithm="sha256",
        media_type="application/json",
    )
    transformation = TransformationLineage(
        transformation_id="normalize-001",
        operation_id="extract",
        transformation_kind="schema_validation",
        transformation_version="1",
        input_reference_ids=(artifact.artifact_id,),
        output_reference_ids=("finding-001",),
    )
    output = OutputLineage(
        output_id="finding-001",
        operation_id="extract",
        source_snapshot_ids=(identity.snapshot_id,),
        disposition="validated",
        original_output_reference_id=artifact.artifact_id,
        evidence_reference_ids=("evidence-001",),
        transformation_ids=(transformation.transformation_id,),
        verification_outcome="schema_validated",
    )
    values = {
        "run_id": "analysis-run-001",
        "project_id": "example",
        "sources": (identity,),
        "operations": (operation(),),
        "dependency_graph": (),
        "contributors": (contributor(identity.snapshot_id),),
        "artifact_references": (artifact,),
        "outputs": (output,),
        "transformations": (transformation,),
        "coverage": "complete",
        "created_at": "2026-08-30T19:00:00Z",
        "finalized_at": "2026-08-30T19:00:01Z",
        "configuration": {"analysis_profile": "exact-source"},
        "feature_flags": {"candidate_first": True},
    }
    values.update(overrides)
    return AnalysisRunManifest(**values)


def test_manifest_is_deterministic_versioned_and_contains_exact_source_refs():
    first = manifest()
    second = manifest()
    assert first.contract_version == ANALYSIS_RUN_MANIFEST_CONTRACT_VERSION
    assert first.to_json() == second.to_json()
    assert json.loads(first.to_json()) == first.to_dict()
    serialized_source = first.to_dict()["sources"][0]
    assert serialized_source["snapshot_id"] == first.sources[0].snapshot_id
    assert serialized_source["content_hash"] == first.sources[0].content_hash
    assert serialized_source["source_map_id"] == "map-scene_001"


def test_manifest_and_nested_configuration_are_immutable_and_defensive():
    value = manifest()
    with pytest.raises(FrozenInstanceError):
        value.run_id = "changed"  # type: ignore[misc]
    with pytest.raises(TypeError):
        value.configuration["new"] = True  # type: ignore[index]
    with pytest.raises(TypeError):
        value.operations[0].configuration["temperature"] = 1  # type: ignore[index]
    serialized = value.to_dict()
    serialized["configuration"]["analysis_profile"] = "changed"
    assert value.configuration["analysis_profile"] == "exact-source"


def test_manifest_and_operation_configuration_require_finite_json_floats():
    assert manifest(configuration={"threshold": 0.25}).configuration["threshold"] == 0.25
    for non_finite in (float("nan"), float("inf"), float("-inf")):
        with pytest.raises(AnalysisRunManifestValidationError, match="finite"):
            manifest(configuration={"threshold": non_finite})

    with pytest.raises(AnalysisRunManifestValidationError, match="finite"):
        OperationDeclaration(
            operation_id="extract",
            adapter_id="ollama_model",
            consumes=("owner_selected_source",),
            produces=("diagnostic_candidate_finding",),
            configuration={"nested": {"thresholds": [0.5, float("nan")] }},
            feature_flags={},
        )


def test_manifest_supports_multiple_exact_sources_with_stable_order():
    first = source(document_id="scene_002", text="Second.", scene_id="scene_002")
    second = source(document_id="scene_001", text="First.", scene_id="scene_001")
    value = manifest(
        sources=(first, second),
        contributors=(contributor(first.snapshot_id),),
        artifact_references=(
            ArtifactReference(
                "raw-001",
                "available",
                (first.snapshot_id,),
                "a" * 64,
                "sha256",
            ),
        ),
        outputs=(
            OutputLineage(
                "finding-001",
                "extract",
                (first.snapshot_id,),
                "validated",
                "raw-001",
            ),
        ),
        transformations=(),
    )
    assert [item.snapshot_id for item in value.sources] == sorted(
        item.snapshot_id for item in value.sources
    )


def test_actual_and_explicitly_unavailable_provenance_are_distinct():
    actual = provenance(
        tool=ProvenanceComponent("available", "story-check", "2"),
        runtime=ProvenanceComponent("available", "ollama", "0.11"),
        provider=ProvenanceComponent("available", "local-ollama"),
        model=ProvenanceComponent("available", "qwen3:8b", "digest-1"),
    )
    assert actual.to_dict()["model"]["name"] == "qwen3:8b"
    assert provenance(tool=UNAVAILABLE, runtime=UNKNOWN).tool.availability == "unavailable"
    with pytest.raises(AnalysisRunManifestValidationError, match="must not fabricate"):
        ProvenanceComponent("unavailable", "pretend-tool", "1")


def test_dependency_graph_validates_declared_classes_and_stable_serialization():
    identity = source()
    producer = operation(
        "evidence",
        "spacy",
        produces=("normalized_evidence",),
    )
    consumer = operation(
        "interpret",
        "subtxt",
        consumes=("normalized_evidence",),
    )
    edge = DependencyEdge("evidence", "interpret", "normalized_evidence")
    contributors = (
        contributor(
            identity.snapshot_id,
            "evidence",
            "spacy",
            output_ids=(),
            actual_provenance=provenance("evidence", "spacy"),
        ),
        contributor(
            identity.snapshot_id,
            "interpret",
            "subtxt",
            output_ids=(),
            actual_provenance=provenance("interpret", "subtxt"),
        ),
    )
    value = manifest(
        operations=(consumer, producer),
        dependency_graph=(edge,),
        contributors=contributors,
        artifact_references=(),
        outputs=(),
        transformations=(),
    )
    assert value.to_dict()["dependency_graph"] == [edge.to_dict()]


def test_dependency_graph_rejects_self_edges_cycles_and_unknown_operations():
    with pytest.raises(AnalysisRunManifestValidationError, match="itself"):
        DependencyEdge("extract", "extract", "normalized_evidence")

    identity = source()
    first = operation(
        "first",
        "spacy",
        consumes=("normalized_evidence",),
        produces=("normalized_evidence",),
    )
    second = operation(
        "second",
        "subtxt",
        consumes=("normalized_evidence",),
        produces=("normalized_evidence",),
    )
    contributors = (
        contributor(identity.snapshot_id, "first", "spacy", output_ids=(), actual_provenance=provenance("first", "spacy")),
        contributor(identity.snapshot_id, "second", "subtxt", output_ids=(), actual_provenance=provenance("second", "subtxt")),
    )
    with pytest.raises(AnalysisRunManifestValidationError, match="cycle"):
        manifest(
            operations=(first, second),
            dependency_graph=(
                DependencyEdge("first", "second", "normalized_evidence"),
                DependencyEdge("second", "first", "normalized_evidence"),
            ),
            contributors=contributors,
            artifact_references=(),
            outputs=(),
            transformations=(),
        )
    with pytest.raises(AnalysisRunManifestValidationError, match="unknown operation"):
        manifest(dependency_graph=(DependencyEdge("extract", "missing", "diagnostic_candidate_finding"),))


@pytest.mark.parametrize("state", sorted(ADAPTER_RESULT_STATES))
def test_all_and_only_existing_adapter_result_states_remain_visible(state):
    identity = source()
    producing = state == "succeeded"
    acceptable_completion = state in {"succeeded", "empty"}
    value = manifest(
        contributors=(
            contributor(
                identity.snapshot_id,
                state=state,
                coverage="complete" if acceptable_completion else "none",
                output_ids=("finding-001",) if producing else (),
            ),
        ),
        artifact_references=manifest().artifact_references if producing else (),
        outputs=manifest().outputs if producing else (),
        transformations=manifest().transformations if producing else (),
        coverage="complete" if acceptable_completion else "partial",
    )
    assert value.contributors[0].result_state == state
    assert value.contributors[0].explanation


def test_undeclared_adapter_result_state_is_rejected():
    with pytest.raises(AnalysisRunManifestValidationError, match="result state"):
        contributor(source().snapshot_id, state="partial")


def test_complete_coverage_cannot_hide_unsuccessful_contributor():
    identity = source()
    with pytest.raises(AnalysisRunManifestValidationError, match="complete run"):
        manifest(
            contributors=(
                contributor(
                    identity.snapshot_id,
                    state="unavailable",
                    coverage="none",
                    output_ids=(),
                ),
            ),
            artifact_references=(),
            outputs=(),
            transformations=(),
            coverage="complete",
        )


@pytest.mark.parametrize("disposition", ("rejected", "quarantined", "unverified"))
def test_unsuccessful_output_remains_attributable_with_reason(disposition):
    identity = source()
    artifact = ArtifactReference(
        "raw-rejected",
        "unknown",
        (identity.snapshot_id,),
    )
    output = OutputLineage(
        "unsafe-output",
        "extract",
        (identity.snapshot_id,),
        disposition,
        artifact.artifact_id,
        missing_evidence_reason="direct evidence was absent",
        guardrail_outcome="excluded from candidate path",
    )
    value = manifest(
        contributors=(
            contributor(
                identity.snapshot_id,
                state="failed_closed" if disposition != "unverified" else "succeeded",
                coverage="partial",
                output_ids=(output.output_id,),
            ),
        ),
        artifact_references=(artifact,),
        outputs=(output,),
        transformations=(),
        coverage="partial",
    )
    serialized = value.to_dict()["outputs"][0]
    assert serialized["disposition"] == disposition
    assert serialized["original_output_reference_id"] == "raw-rejected"
    assert serialized["missing_evidence_reason"]
    assert value.coverage == "partial"


def test_unsuccessful_output_without_reason_fails_closed():
    with pytest.raises(AnalysisRunManifestValidationError, match="reason"):
        OutputLineage(
            "unsafe-output",
            "extract",
            (source().snapshot_id,),
            "quarantined",
            "raw-001",
        )


def test_empty_contributor_may_retain_unverified_and_quarantined_outputs():
    identity = source()
    artifact = ArtifactReference(
        "raw-grounding",
        "unknown",
        (identity.snapshot_id,),
    )
    outputs = (
        OutputLineage(
            "unverified-diagnostic",
            "extract",
            (identity.snapshot_id,),
            "unverified",
            artifact.artifact_id,
            verification_outcome="not_applicable",
            missing_evidence_reason="validation_not_applicable",
        ),
        OutputLineage(
            "quarantined-diagnostic",
            "extract",
            (identity.snapshot_id,),
            "quarantined",
            artifact.artifact_id,
            verification_outcome="unsupported",
            missing_evidence_reason="evidence_absent",
        ),
    )

    value = manifest(
        contributors=(
            contributor(
                identity.snapshot_id,
                state="empty",
                coverage="complete",
                output_ids=tuple(output.output_id for output in outputs),
            ),
        ),
        artifact_references=(artifact,),
        outputs=outputs,
        transformations=(),
        coverage="complete",
    )

    assert value.contributors[0].result_state == "empty"
    assert [output.disposition for output in value.outputs] == [
        "quarantined",
        "unverified",
    ]


def test_empty_contributor_cannot_claim_validated_output():
    identity = source()
    with pytest.raises(
        AnalysisRunManifestValidationError,
        match="empty contributor can claim only unverified or quarantined output",
    ):
        manifest(
            contributors=(
                contributor(
                    identity.snapshot_id,
                    state="empty",
                    coverage="complete",
                ),
            ),
        )


def test_transformation_lineage_keeps_original_and_derived_references():
    serialized = manifest().to_dict()
    transformation = serialized["transformations"][0]
    assert transformation["input_reference_ids"] == ["raw-001"]
    assert transformation["output_reference_ids"] == ["finding-001"]
    assert serialized["outputs"][0]["transformation_ids"] == ["normalize-001"]


def test_source_hash_and_snapshot_references_fail_closed():
    identity = source()
    with pytest.raises(AnalysisRunManifestValidationError, match="unknown source snapshot"):
        manifest(
            contributors=(contributor("snapshot-missing"),),
        )
    with pytest.raises(AnalysisRunManifestValidationError, match="ambiguous duplicate"):
        manifest(sources=(identity, identity))


def test_fallback_cannot_impersonate_a_missing_adapter():
    identity = source()
    fake = provenance("extract", "deterministic_fallback", implementation_kind="fallback")
    with pytest.raises(AnalysisRunManifestValidationError, match="impersonate"):
        contributor(
            identity.snapshot_id,
            adapter_id="story_check",
            actual_provenance=fake,
        )


def test_fallback_implementation_kind_is_symmetric_with_adapter_identity():
    assert provenance(
        "extract",
        "deterministic_fallback",
        implementation_kind="fallback",
    ).implementation_kind == "fallback"
    with pytest.raises(AnalysisRunManifestValidationError, match="identified as fallback"):
        provenance("extract", "deterministic_fallback", implementation_kind="app_owned")
    for adapter_id in ("story_check", "ollama_model"):
        with pytest.raises(AnalysisRunManifestValidationError, match="reserved"):
            provenance("extract", adapter_id, implementation_kind="fallback")


def test_absolute_identity_and_storage_or_product_mutation_fields_are_rejected():
    with pytest.raises(AnalysisRunManifestValidationError, match="path-safe"):
        manifest(run_id="/tmp/run")
    with pytest.raises(AnalysisRunManifestValidationError, match="absolute path"):
        provenance(tool=ProvenanceComponent("available", "/usr/bin/tool", "1"))
    with pytest.raises(TypeError):
        AnalysisRunManifest(generated_prose="no")  # type: ignore[call-arg]
    for forbidden in ("generated_prose", "canon", "apply_promotion", "storage_path"):
        with pytest.raises(AnalysisRunManifestValidationError, match="analysis-only"):
            manifest(configuration={forbidden: True})


def test_manifest_has_no_execution_control_or_persistence_state():
    serialized = manifest().to_dict()
    forbidden = {
        "status",
        "updated_at",
        "storage_root",
        "run_dir",
        "cancel_requested",
        "timeout_seconds",
    }
    assert forbidden.isdisjoint(serialized)
    assert serialized["safety_boundary"] == {
        "analytical_output": True,
        "candidate_first": True,
        "owner_control_required": True,
        "automatic_truth_selection": False,
        "project_mutation_performed": False,
    }
