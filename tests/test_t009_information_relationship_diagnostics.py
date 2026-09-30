"""Focused T009C information-boundary and relationship-delta tests."""

from __future__ import annotations

import copy
import json

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
    build_approved_context_snapshot,
    build_diagnostic_support_reference,
    build_project_diagnostic_context,
    build_project_diagnostic_source,
)
from backend.story_knowledge.project_narrative_diagnostics import (
    PROJECT_NARRATIVE_DIAGNOSTIC_VERSION,
    ProjectNarrativeDiagnosticValidationError,
    build_information_boundary_diagnostic,
    build_relationship_delta_diagnostic,
    serialize_project_narrative_diagnostic,
    validate_project_narrative_diagnostic,
)
from backend.story_knowledge.source_map import (
    CHAR_OFFSET_BASIS,
    OffsetRange,
    build_exact_source_snapshot,
)


def _snapshot(document_id: str, text: str):
    return build_exact_source_snapshot(
        project_id="example",
        source_document_type="scene",
        source_document_id=document_id,
        source_document_version="1",
        source_ownership="owner_authored",
        source_content=text,
        scene_id=document_id,
        source_map_id=f"map-{document_id}",
    )


def _manifest(snapshot):
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
        explanation="Deterministic T009C fixture lineage.",
        provenance=provenance,
        output_ids=(output.output_id,),
    )
    return AnalysisRunManifest(
        run_id="run-001",
        project_id="example",
        sources=(snapshot.identity,),
        operations=(operation,),
        dependency_graph=(),
        contributors=(contributor,),
        artifact_references=(artifact,),
        outputs=(output,),
        transformations=(),
        coverage="complete",
        created_at="2026-09-30T00:00:00Z",
        finalized_at="2026-09-30T00:00:01Z",
        configuration={},
        feature_flags={"candidate_first": True},
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
            "continuity_label": "Owner-approved diagnostic reference",
            "facts": [
                {
                    "field": "reference_state",
                    "value": "owner_approved",
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


def _context():
    first = _snapshot("scene-001", "First exact diagnostic source.")
    second = _snapshot("scene-002", "Second exact diagnostic source.")
    manifest = _manifest(first)
    evidence = build_exact_evidence_record(
        snapshot=first,
        run_id=manifest.run_id,
        artifact_id="artifact-001",
        artifact_file_id="artifact-file-001",
        operation_id="analyze-spacy",
        adapter_id="spacy",
        disposition="validated",
        contributor_state="succeeded",
        created_at="2026-09-30T00:00:00Z",
        character_range=OffsetRange(0, 5, CHAR_OFFSET_BASIS),
        output_id="output-001",
    )
    support = build_diagnostic_support_reference(
        support_reference_id="support-001",
        support_kind="diagnostic",
        source_snapshot_ids=[first.identity.snapshot_id],
        run_id=manifest.run_id,
        evidence_reference_ids=[evidence["evidence_id"]],
        provenance_reference_ids=["provenance-spacy-001"],
        support_classification="supported",
        uncertainty_classification="provisional",
    )
    approved = build_approved_context_snapshot(
        _approved_record(),
        source_snapshot_ids=[first.identity.snapshot_id],
    )
    context = build_project_diagnostic_context(
        project_id="example",
        sources=[
            build_project_diagnostic_source(first, source_role="primary"),
            build_project_diagnostic_source(second, source_role="comparison"),
        ],
        run_manifests=[manifest],
        evidence_records=[evidence],
        approved_context_snapshots=[approved],
        diagnostic_support_references=[support],
    )
    return {
        "context": context,
        "first_source": first.identity.snapshot_id,
        "second_source": second.identity.snapshot_id,
        "evidence": evidence["evidence_id"],
        "support": support["support_reference_id"],
        "approved": approved["context_snapshot_id"],
    }


def _information():
    fixture = _context()
    diagnostic = build_information_boundary_diagnostic(
        context=fixture["context"],
        source_snapshot_ids=[fixture["first_source"]],
        information_ref="information-001",
        apparently_informed_actor_ref="actor-001",
        apparently_uninformed_actor_ref="actor-002",
        assessment="supported_boundary",
        evidence_reference_ids=[fixture["evidence"]],
        diagnostic_support_reference_ids=[fixture["support"]],
        approved_context_snapshot_ids=[fixture["approved"]],
        support_classification="supported",
        uncertainty_classification="provisional",
    )
    return fixture, diagnostic


def _relationship():
    fixture = _context()
    diagnostic = build_relationship_delta_diagnostic(
        context=fixture["context"],
        source_snapshot_ids=[fixture["first_source"]],
        participant_refs=["actor-002", "actor-001"],
        relationship_axis="trust",
        prior_reference="relationship-state-001",
        later_reference="relationship-state-002",
        delta_assessment="supported_change",
        evidence_reference_ids=[fixture["evidence"]],
        diagnostic_support_reference_ids=[fixture["support"]],
        approved_context_snapshot_ids=[fixture["approved"]],
        support_classification="supported",
        uncertainty_classification="provisional",
    )
    return fixture, diagnostic


def test_information_boundary_is_deterministic_read_only_and_non_canon():
    fixture, first = _information()
    _, second = _information()
    assert first == second
    assert first["schema_version"] == PROJECT_NARRATIVE_DIAGNOSTIC_VERSION
    assert first["diagnostic_kind"] == "information_boundary"
    assert first["payload"] == {
        "information_ref": "information-001",
        "apparently_informed_actor_ref": "actor-001",
        "apparently_uninformed_actor_ref": "actor-002",
        "assessment": "supported_boundary",
    }
    assert first["evidence_reference_ids"] == [fixture["evidence"]]
    assert first["lineage"] == {
        "run_ids": ["run-001"],
        "provenance_reference_ids": [
            "provenance-approved-001",
            "provenance-spacy-001",
        ],
    }
    assert first["authority"]["truth_status"] == "not_settled"
    assert first["authority"]["canon_status"] == "not_selected"
    assert first["authority"]["world_state_status"] == "not_settled"
    assert first["authority"]["author_intent_status"] == "not_inferred"
    assert validate_project_narrative_diagnostic(first, fixture["context"]) == first


def test_relationship_delta_is_deterministic_read_only_and_non_canon():
    fixture, first = _relationship()
    _, second = _relationship()
    assert first == second
    assert first["diagnostic_kind"] == "relationship_delta"
    assert first["payload"]["participant_refs"] == ["actor-001", "actor-002"]
    assert first["payload"]["relationship_axis"] == "trust"
    assert first["payload"]["prior_reference"] == "relationship-state-001"
    assert first["payload"]["later_reference"] == "relationship-state-002"
    assert first["payload"]["delta_assessment"] == "supported_change"
    assert first["authority"]["relationship_status"] == "not_settled"
    assert first["authority"]["emotional_status"] == "not_settled"
    assert first["authority"]["canon_status"] == "not_selected"
    assert first["behavior"]["persistence"] == "none"
    assert first["behavior"]["runtime_execution"] == "none"
    assert validate_project_narrative_diagnostic(first, fixture["context"]) == first


@pytest.mark.parametrize("kind", ["information", "relationship"])
def test_supported_information_and_relationship_classifications_require_evidence(kind):
    fixture = _context()
    common = {
        "context": fixture["context"],
        "source_snapshot_ids": [fixture["first_source"]],
        "support_classification": "supported",
        "uncertainty_classification": "provisional",
    }
    with pytest.raises(ProjectNarrativeDiagnosticValidationError, match="require evidence"):
        if kind == "information":
            build_information_boundary_diagnostic(
                **common,
                information_ref="information-001",
                apparently_informed_actor_ref="actor-001",
                apparently_uninformed_actor_ref="actor-002",
                assessment="supported_boundary",
            )
        else:
            build_relationship_delta_diagnostic(
                **common,
                participant_refs=["actor-001", "actor-002"],
                relationship_axis="trust",
                prior_reference="relationship-state-001",
                later_reference="relationship-state-002",
                delta_assessment="supported_change",
            )


@pytest.mark.parametrize(
    ("assessment", "with_evidence", "support", "uncertainty"),
    [
        ("conflict", True, "ambiguous", "conflicting"),
        ("ambiguous", False, "ambiguous", "ambiguous"),
        (
            "insufficient_evidence",
            False,
            "insufficient_evidence",
            "insufficient_evidence",
        ),
    ],
)
def test_information_uncertainty_states_remain_diagnostic_only(
    assessment, with_evidence, support, uncertainty
):
    fixture = _context()
    diagnostic = build_information_boundary_diagnostic(
        context=fixture["context"],
        source_snapshot_ids=[fixture["first_source"]],
        information_ref="information-001",
        apparently_informed_actor_ref="actor-001",
        apparently_uninformed_actor_ref="actor-002",
        assessment=assessment,
        evidence_reference_ids=[fixture["evidence"]] if with_evidence else [],
        support_classification=support,
        uncertainty_classification=uncertainty,
    )
    assert diagnostic["payload"]["assessment"] == assessment
    assert diagnostic["authority"]["truth_status"] == "not_settled"
    assert diagnostic["authority"]["canon_status"] == "not_selected"


@pytest.mark.parametrize(
    ("assessment", "with_evidence", "support", "uncertainty"),
    [
        ("conflict", True, "ambiguous", "conflicting"),
        ("ambiguous", False, "ambiguous", "ambiguous"),
        (
            "insufficient_evidence",
            False,
            "insufficient_evidence",
            "insufficient_evidence",
        ),
        ("unsupported", False, "unsupported", "ambiguous"),
    ],
)
def test_relationship_uncertainty_states_remain_diagnostic_only(
    assessment, with_evidence, support, uncertainty
):
    fixture = _context()
    diagnostic = build_relationship_delta_diagnostic(
        context=fixture["context"],
        source_snapshot_ids=[fixture["first_source"]],
        participant_refs=["actor-001", "actor-002"],
        relationship_axis="trust",
        prior_reference="relationship-state-001",
        later_reference="relationship-state-002",
        delta_assessment=assessment,
        evidence_reference_ids=[fixture["evidence"]] if with_evidence else [],
        support_classification=support,
        uncertainty_classification=uncertainty,
    )
    assert diagnostic["payload"]["delta_assessment"] == assessment
    assert diagnostic["authority"]["relationship_status"] == "not_settled"
    assert diagnostic["authority"]["emotional_status"] == "not_settled"


def test_unsupported_relationship_delta_requires_evidence_or_explicit_uncertainty():
    fixture = _context()
    with pytest.raises(
        ProjectNarrativeDiagnosticValidationError,
        match="evidence or explicit uncertainty",
    ):
        build_relationship_delta_diagnostic(
            context=fixture["context"],
            source_snapshot_ids=[fixture["first_source"]],
            participant_refs=["actor-001", "actor-002"],
            relationship_axis="trust",
            prior_reference="relationship-state-001",
            later_reference="relationship-state-002",
            delta_assessment="unsupported",
            support_classification="unsupported",
            uncertainty_classification="provisional",
        )


@pytest.mark.parametrize(
    ("field", "unknown", "message"),
    [
        ("source_snapshot_ids", ["snapshot-unknown"], "unknown source"),
        ("evidence_reference_ids", ["evidence-unknown"], "unknown evidence"),
        (
            "diagnostic_support_reference_ids",
            ["support-unknown"],
            "unknown support",
        ),
        (
            "approved_context_snapshot_ids",
            ["approved-context-unknown"],
            "unknown approved context",
        ),
    ],
)
def test_all_context_references_must_be_known(field, unknown, message):
    fixture, diagnostic = _information()
    diagnostic[field] = unknown
    with pytest.raises(ProjectNarrativeDiagnosticValidationError, match=message):
        validate_project_narrative_diagnostic(diagnostic, fixture["context"])


@pytest.mark.parametrize("basis", ["evidence", "support", "approved"])
def test_evidence_support_and_approved_context_cannot_cross_source_boundaries(basis):
    fixture = _context()
    kwargs = {
        "evidence_reference_ids": [],
        "diagnostic_support_reference_ids": [],
        "approved_context_snapshot_ids": [],
    }
    if basis == "evidence":
        kwargs["evidence_reference_ids"] = [fixture["evidence"]]
    elif basis == "support":
        kwargs["diagnostic_support_reference_ids"] = [fixture["support"]]
    else:
        kwargs["approved_context_snapshot_ids"] = [fixture["approved"]]
    with pytest.raises(
        ProjectNarrativeDiagnosticValidationError,
        match="undeclared source boundary",
    ):
        build_information_boundary_diagnostic(
            context=fixture["context"],
            source_snapshot_ids=[fixture["second_source"]],
            information_ref="information-001",
            apparently_informed_actor_ref="actor-001",
            apparently_uninformed_actor_ref="actor-002",
            assessment="ambiguous",
            support_classification="ambiguous",
            uncertainty_classification="ambiguous",
            **kwargs,
        )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("combined_source_text", "flattened"),
        ("raw_model_output", {"text": "opaque"}),
        ("raw_tool_output", {"state": "approved"}),
        ("truth", "settled"),
        ("canon", True),
        ("approved_memory", True),
        ("canonical_information_state", "known"),
        ("definitive_relationship_truth", "allies"),
        ("final_emotional_truth", "trust"),
        ("author_intent", "inferred"),
        ("generate_story_prose", True),
        ("rewrite_intent", True),
        ("continuation_intent", True),
        ("promotion", True),
        ("apply_promotion", True),
        ("mutate_memory_canon", True),
    ],
)
def test_flattening_raw_output_truth_prose_promotion_and_mutation_fail_closed(
    field, value
):
    fixture, diagnostic = _information()
    diagnostic[field] = value
    with pytest.raises(ProjectNarrativeDiagnosticValidationError, match="not closed"):
        validate_project_narrative_diagnostic(diagnostic, fixture["context"])


@pytest.mark.parametrize(
    ("support", "uncertainty"),
    [
        ("author_intent_dependent", "provisional"),
        ("ambiguous", "author_intent_dependent"),
    ],
)
def test_information_and_relationship_claims_cannot_infer_author_intent(
    support, uncertainty
):
    fixture = _context()
    with pytest.raises(ProjectNarrativeDiagnosticValidationError, match="author intent"):
        build_information_boundary_diagnostic(
            context=fixture["context"],
            source_snapshot_ids=[fixture["first_source"]],
            information_ref="information-001",
            apparently_informed_actor_ref="actor-001",
            apparently_uninformed_actor_ref="actor-002",
            assessment="ambiguous",
            evidence_reference_ids=[fixture["evidence"]],
            support_classification=support,
            uncertainty_classification=uncertainty,
        )


def test_payloads_are_closed_and_relationship_references_are_bounded():
    fixture, information = _information()
    information["payload"]["character_knowledge_is_true"] = True
    with pytest.raises(ProjectNarrativeDiagnosticValidationError, match="not closed"):
        validate_project_narrative_diagnostic(information, fixture["context"])

    fixture = _context()
    with pytest.raises(ProjectNarrativeDiagnosticValidationError, match="duplicates"):
        build_relationship_delta_diagnostic(
            context=fixture["context"],
            source_snapshot_ids=[fixture["first_source"]],
            participant_refs=["actor-001", "actor-001"],
            relationship_axis="trust",
            prior_reference="relationship-state-001",
            later_reference="relationship-state-002",
            delta_assessment="ambiguous",
            support_classification="ambiguous",
            uncertainty_classification="ambiguous",
        )


def test_weakened_authority_behavior_and_fabricated_lineage_fail_closed():
    fixture, diagnostic = _relationship()
    diagnostic["authority"]["relationship_status"] = "settled"
    with pytest.raises(ProjectNarrativeDiagnosticValidationError, match="authority"):
        validate_project_narrative_diagnostic(diagnostic, fixture["context"])

    fixture, diagnostic = _relationship()
    diagnostic["behavior"]["runtime_execution"] = "enabled"
    with pytest.raises(ProjectNarrativeDiagnosticValidationError, match="behavior"):
        validate_project_narrative_diagnostic(diagnostic, fixture["context"])

    fixture, diagnostic = _relationship()
    diagnostic["lineage"]["run_ids"] = ["run-fabricated"]
    with pytest.raises(ProjectNarrativeDiagnosticValidationError, match="lineage"):
        validate_project_narrative_diagnostic(diagnostic, fixture["context"])


@pytest.mark.parametrize("builder", [_information, _relationship])
def test_serialization_and_ids_are_deterministic_and_tamper_evident(builder):
    fixture, diagnostic = builder()
    first = serialize_project_narrative_diagnostic(
        diagnostic, fixture["context"]
    )
    second = serialize_project_narrative_diagnostic(
        copy.deepcopy(diagnostic), fixture["context"]
    )
    assert first == second
    assert json.loads(first) == diagnostic

    tampered = copy.deepcopy(diagnostic)
    tampered["support_classification"] = "ambiguous"
    with pytest.raises(ProjectNarrativeDiagnosticValidationError):
        validate_project_narrative_diagnostic(tampered, fixture["context"])


def test_empty_context_and_build_validation_have_no_runtime_or_persistence(tmp_path):
    fixture, diagnostic = _information()
    invalid_context = copy.deepcopy(fixture["context"])
    invalid_context["sources"] = []
    with pytest.raises(ProjectNarrativeDiagnosticValidationError, match="valid T009A"):
        build_information_boundary_diagnostic(
            context=invalid_context,
            source_snapshot_ids=[fixture["first_source"]],
            information_ref="information-001",
            apparently_informed_actor_ref="actor-001",
            apparently_uninformed_actor_ref="actor-002",
            assessment="supported_boundary",
            evidence_reference_ids=[fixture["evidence"]],
            support_classification="supported",
            uncertainty_classification="provisional",
        )

    before = list(tmp_path.iterdir())
    validated = validate_project_narrative_diagnostic(
        diagnostic, fixture["context"]
    )
    validated["source_snapshot_ids"].clear()
    assert diagnostic["source_snapshot_ids"]
    assert list(tmp_path.iterdir()) == before
    assert diagnostic["behavior"] == {
        "persistence": "none",
        "runtime_execution": "none",
        "story_prose_output": "forbidden",
        "promotion": "none",
        "apply_promotion": "none",
        "memory_canon_mutation": "none",
    }
