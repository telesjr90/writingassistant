"""Focused T009A project-level diagnostic context contract tests."""

from __future__ import annotations

import copy
import hashlib

import pytest

from backend.story_knowledge.analysis_run_manifest import (
    AdapterProvenance,
    AnalysisRunManifest,
    ArtifactReference,
    ContributorLineage,
    OperationDeclaration,
    OutputLineage,
    ProvenanceComponent,
)
from backend.story_knowledge.approved_records import build_approved_record
from backend.story_knowledge.evidence_ledger import build_exact_evidence_record
from backend.story_knowledge.project_diagnostic_context import (
    PROJECT_DIAGNOSTIC_CONTEXT_VERSION,
    ProjectDiagnosticContextValidationError,
    build_approved_context_snapshot,
    build_diagnostic_support_reference,
    build_project_diagnostic_context,
    build_project_diagnostic_source,
    validate_project_diagnostic_context,
)
from backend.story_knowledge.source_map import (
    CHAR_OFFSET_BASIS,
    OffsetRange,
    build_exact_source_snapshot,
)


def _snapshot(document_id: str, text: str, *, version: str = "1"):
    return build_exact_source_snapshot(
        project_id="example",
        source_document_type="scene",
        source_document_id=document_id,
        source_document_version=version,
        source_ownership="owner_authored",
        source_content=text,
        scene_id=document_id,
        source_map_id=f"map-{document_id}-{version}",
    )


def _manifest(snapshot, *, run_id="run-001"):
    operation = OperationDeclaration(
        operation_id="analyze-spacy",
        adapter_id="spacy",
        consumes=("owner_selected_source",),
        produces=("normalized_evidence",),
        configuration={},
        feature_flags={},
    )
    artifact = ArtifactReference(
        artifact_id="artifact-001",
        availability="available",
        source_snapshot_ids=(snapshot.identity.snapshot_id,),
        content_hash="a" * 64,
        hash_algorithm="sha256",
        media_type="application/json",
    )
    output = OutputLineage(
        output_id="output-001",
        operation_id=operation.operation_id,
        source_snapshot_ids=(snapshot.identity.snapshot_id,),
        disposition="validated",
        original_output_reference_id=artifact.artifact_id,
        evidence_reference_ids=("evidence-placeholder",),
        verification_outcome="schema_validated",
    )
    provenance = AdapterProvenance(
        adapter_id="spacy",
        operation_id=operation.operation_id,
        user_facing_label="spaCy evidence extraction",
        implementation_kind="app_owned",
        tool=ProvenanceComponent("available", "spacy", "fixture"),
        runtime=ProvenanceComponent("available", "python", "3"),
        provider=ProvenanceComponent("unknown"),
        model=ProvenanceComponent("unknown"),
    )
    contributor = ContributorLineage(
        operation_id=operation.operation_id,
        adapter_id="spacy",
        source_snapshot_ids=(snapshot.identity.snapshot_id,),
        result_state="succeeded",
        coverage="complete",
        explanation="Deterministic test lineage.",
        provenance=provenance,
        output_ids=(output.output_id,),
    )
    return AnalysisRunManifest(
        run_id=run_id,
        project_id="example",
        sources=(snapshot.identity,),
        operations=(operation,),
        dependency_graph=(),
        contributors=(contributor,),
        artifact_references=(artifact,),
        outputs=(output,),
        transformations=(),
        coverage="complete",
        created_at="2026-09-29T12:00:00Z",
        finalized_at="2026-09-29T12:00:01Z",
        configuration={},
        feature_flags={"candidate_first": True},
    )


def _evidence(snapshot, *, run_id="run-001"):
    return build_exact_evidence_record(
        snapshot=snapshot,
        run_id=run_id,
        artifact_id="artifact-001",
        artifact_file_id="artifact-file-001",
        operation_id="analyze-spacy",
        adapter_id="spacy",
        disposition="validated",
        contributor_state="succeeded",
        created_at="2026-09-29T12:00:00Z",
        character_range=OffsetRange(
            0, min(5, len(snapshot.source_content)), CHAR_OFFSET_BASIS
        ),
        output_id="output-001",
    )


def _approved_record():
    return build_approved_record(
        record_version=1,
        project_id="example",
        destination_type="approved_continuity_record",
        destination_key="continuity-001",
        source_candidate_id="candidate-001",
        source_promotion_id="promotion-001",
        source_candidate_snapshot_hash="b" * 64,
        payload={
            "payload_type": "approved_continuity_record",
            "continuity_label": "Owner-approved continuity reference",
            "facts": [
                {
                    "field": "continuity_state",
                    "value": "known",
                    "evidence_ref_ids": ["evidence-approved-001"],
                    "provenance_ref_ids": ["provenance-approved-001"],
                }
            ],
        },
        evidence_refs=[
            {"ref_id": "evidence-approved-001", "locator_id": "locator-001"}
        ],
        provenance_refs=[
            {
                "provenance_id": "provenance-approved-001",
                "source_kind": "owner_decision",
                "source_id": "decision-001",
            }
        ],
        source_locators=[
            {
                "locator_id": "locator-001",
                "locator_kind": "source_snapshot",
                "locator": "scene:scene-001",
            }
        ],
    )


def _full_context():
    first = _snapshot("scene-001", "First exact source.")
    second = _snapshot("scene-002", "Second exact source.")
    manifest = _manifest(first)
    evidence = _evidence(first)
    approved = build_approved_context_snapshot(
        _approved_record(),
        source_snapshot_ids=[first.identity.snapshot_id],
    )
    support = build_diagnostic_support_reference(
        support_reference_id="candidate-001",
        support_kind="candidate",
        source_snapshot_ids=[first.identity.snapshot_id],
        run_id=manifest.run_id,
        evidence_reference_ids=[evidence["evidence_id"]],
        provenance_reference_ids=["provenance-spacy-001"],
        support_classification="supported",
        uncertainty_classification="provisional",
    )
    return build_project_diagnostic_context(
        project_id="example",
        sources=[
            build_project_diagnostic_source(
                second.identity, source_role="comparison"
            ),
            build_project_diagnostic_source(first, source_role="primary"),
        ],
        run_manifests=[manifest],
        evidence_records=[evidence],
        approved_context_snapshots=[approved],
        diagnostic_support_references=[support],
    )


def test_context_is_deterministic_versioned_and_preserves_exact_source_boundaries():
    first = _full_context()
    second = _full_context()
    assert first == second
    assert first["schema_version"] == PROJECT_DIAGNOSTIC_CONTEXT_VERSION
    assert len(first["sources"]) == 2
    assert {source["snapshot_kind"] for source in first["sources"]} == {
        "exact_source_snapshot",
        "source_identity_reference",
    }
    exact = next(source for source in first["sources"] if "source_snapshot" in source)
    assert exact["source_snapshot"]["source_content"] == "First exact source."
    assert exact["source_snapshot"]["identity"]["content_hash"] == hashlib.sha256(
        b"First exact source."
    ).hexdigest()
    assert first["context_policy"]["source_boundary"] == "separate_exact_sources"


def test_context_preserves_run_artifact_evidence_and_provenance_lineage():
    context = _full_context()
    manifest = context["run_manifests"][0]
    evidence = context["evidence_records"][0]
    support = context["diagnostic_support_references"][0]
    assert manifest["run_id"] == evidence["run_id"] == support["run_id"]
    assert (
        evidence["artifact_id"]
        == manifest["artifact_references"][0]["artifact_id"]
    )
    assert support["evidence_reference_ids"] == [evidence["evidence_id"]]
    assert support["authority"] == "support_only_unsettled"
    assert support["read_only"] is True


def test_approved_context_is_explicit_separate_hashed_and_provenance_backed():
    context = _full_context()
    approved = context["approved_context_snapshots"][0]
    assert approved["permission_basis"] == "existing_explicit_approved_record"
    assert approved["approved_record_hash"] == _approved_record().approved_record_hash
    assert approved["approved_record"]["evidence_refs"]
    assert approved["approved_record"]["provenance_refs"]
    assert "support_reference_id" not in approved
    assert context["diagnostic_support_references"][0]["support_reference_id"] == (
        "candidate-001"
    )


@pytest.mark.parametrize(
    "unsafe_value",
    [
        {"model_output": "raw output"},
        {"review_status": "candidate_review_pending"},
        {"candidate_id": "candidate-001"},
    ],
)
def test_raw_output_candidate_and_review_queue_state_cannot_be_approved_context(
    unsafe_value,
):
    with pytest.raises(ProjectDiagnosticContextValidationError, match="approved record"):
        build_approved_context_snapshot(
            unsafe_value,
            source_snapshot_ids=[
                _snapshot("scene-001", "Source").identity.snapshot_id
            ],
        )


def test_empty_sources_duplicate_sources_conflicts_and_hash_mismatch_fail_closed():
    with pytest.raises(ProjectDiagnosticContextValidationError, match="at least one"):
        build_project_diagnostic_context(project_id="example", sources=[])

    snapshot = _snapshot("scene-001", "Source")
    source = build_project_diagnostic_source(snapshot, source_role="primary")
    with pytest.raises(ProjectDiagnosticContextValidationError, match="duplicate"):
        build_project_diagnostic_context(
            project_id="example", sources=[source, source]
        )

    conflicting = copy.deepcopy(source)
    conflicting["source_snapshot"]["source_content"] = "Tampered"
    with pytest.raises(ProjectDiagnosticContextValidationError, match="source snapshot"):
        build_project_diagnostic_context(project_id="example", sources=[conflicting])

    same_logical_source = build_project_diagnostic_source(
        _snapshot("scene-001", "Different bytes"), source_role="comparison"
    )
    with pytest.raises(ProjectDiagnosticContextValidationError, match="conflicting"):
        build_project_diagnostic_context(
            project_id="example", sources=[source, same_logical_source]
        )


@pytest.mark.parametrize(
    "field,value",
    [
        ("combined_source_text", "flattened"),
        ("raw_model_output", {"text": "opaque"}),
        ("approved", True),
        ("canon", True),
        ("promotion", True),
        ("apply_promotion", True),
        ("rewrite_intent", True),
        ("generated_prose", "text"),
        ("mutate_memory", True),
        ("canonical_chronology", "settled"),
        ("author_intent_is_true", True),
    ],
)
def test_flattening_truth_generation_and_mutation_fields_fail_closed(field, value):
    context = _full_context()
    context[field] = value
    with pytest.raises(
        ProjectDiagnosticContextValidationError, match="fields are not closed"
    ):
        validate_project_diagnostic_context(context)


def test_unknown_lineage_and_weakened_policy_fail_closed():
    context = _full_context()
    context["diagnostic_support_references"][0]["evidence_reference_ids"] = [
        "evidence-unknown"
    ]
    with pytest.raises(ProjectDiagnosticContextValidationError, match="unknown evidence"):
        validate_project_diagnostic_context(context)

    context = _full_context()
    context["evidence_records"][0]["artifact_id"] = "artifact-unknown"
    with pytest.raises(ProjectDiagnosticContextValidationError, match="artifact lineage"):
        validate_project_diagnostic_context(context)

    context = _full_context()
    context["context_policy"]["mutation"] = "memory"
    with pytest.raises(
        ProjectDiagnosticContextValidationError, match="cannot be weakened"
    ):
        validate_project_diagnostic_context(context)


def test_validation_is_defensive_and_performs_no_persistence(tmp_path):
    before = list(tmp_path.iterdir())
    context = _full_context()
    validated = validate_project_diagnostic_context(context)
    validated["sources"].clear()
    assert len(context["sources"]) == 2
    assert list(tmp_path.iterdir()) == before
