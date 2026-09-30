"""Focused T009B causal, timeline, and thread diagnostic tests."""

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
from backend.story_knowledge.evidence_ledger import build_exact_evidence_record
from backend.story_knowledge.project_diagnostic_context import (
    build_diagnostic_support_reference,
    build_project_diagnostic_context,
    build_project_diagnostic_source,
)
from backend.story_knowledge.project_narrative_diagnostics import (
    PROJECT_NARRATIVE_DIAGNOSTIC_VERSION,
    ProjectNarrativeDiagnosticValidationError,
    build_causal_continuity_diagnostic,
    build_thread_activity_diagnostic,
    build_timeline_diagnostic,
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
        explanation="Deterministic T009B fixture lineage.",
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
        created_at="2026-09-29T12:00:00Z",
        finalized_at="2026-09-29T12:00:01Z",
        configuration={},
        feature_flags={"candidate_first": True},
    )


def _context():
    first = _snapshot("scene-001", "The first exact source.")
    second = _snapshot("scene-002", "The second exact source.")
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
        created_at="2026-09-29T12:00:00Z",
        character_range=OffsetRange(0, 3, CHAR_OFFSET_BASIS),
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
    context = build_project_diagnostic_context(
        project_id="example",
        sources=[
            build_project_diagnostic_source(first, source_role="primary"),
            build_project_diagnostic_source(second, source_role="comparison"),
        ],
        run_manifests=[manifest],
        evidence_records=[evidence],
        diagnostic_support_references=[support],
    )
    return context, first.identity.snapshot_id, second.identity.snapshot_id, evidence[
        "evidence_id"
    ]


def _causal():
    context, first_id, _, evidence_id = _context()
    diagnostic = build_causal_continuity_diagnostic(
        context=context,
        source_snapshot_ids=[first_id],
        cause_event_ref="event-cause-001",
        effect_event_ref="event-effect-001",
        assessment="supported_link",
        evidence_reference_ids=[evidence_id],
        diagnostic_support_reference_ids=["support-001"],
        support_classification="supported",
        uncertainty_classification="provisional",
    )
    return context, diagnostic


def test_causal_diagnostic_is_deterministic_read_only_and_evidence_backed():
    context, first = _causal()
    _, second = _causal()
    assert first == second
    assert first["schema_version"] == PROJECT_NARRATIVE_DIAGNOSTIC_VERSION
    assert first["diagnostic_kind"] == "causal_continuity"
    assert first["evidence_reference_ids"]
    assert first["lineage"] == {
        "run_ids": ["run-001"],
        "provenance_reference_ids": ["provenance-spacy-001"],
    }
    assert first["authority"]["truth_status"] == "not_settled"
    assert first["authority"]["canon_status"] == "not_selected"
    assert first["authority"]["world_state_status"] == "not_settled"
    assert first["authority"]["causality_status"] == "not_canonical"
    assert first["authority"]["relationship_status"] == "not_settled"
    assert first["authority"]["emotional_status"] == "not_settled"
    assert first["authority"]["author_intent_status"] == "not_inferred"
    assert first["authority"]["approved_memory_status"] == "not_established"
    assert first["behavior"] == {
        "persistence": "none",
        "runtime_execution": "none",
        "story_prose_output": "forbidden",
        "promotion": "none",
        "apply_promotion": "none",
        "memory_canon_mutation": "none",
    }
    assert validate_project_narrative_diagnostic(first, context) == first


@pytest.mark.parametrize(
    ("assessment", "with_evidence", "support", "uncertainty"),
    [
        ("supported_ordering", True, "supported", "provisional"),
        ("conflict", True, "ambiguous", "conflicting"),
        ("ambiguous", True, "ambiguous", "ambiguous"),
        (
            "insufficient_evidence",
            False,
            "insufficient_evidence",
            "insufficient_evidence",
        ),
    ],
)
def test_timeline_represents_support_conflict_ambiguity_and_insufficiency(
    assessment, with_evidence, support, uncertainty
):
    context, first_id, _, evidence_id = _context()
    diagnostic = build_timeline_diagnostic(
        context=context,
        source_snapshot_ids=[first_id],
        earlier_event_ref="event-earlier-001",
        later_event_ref="event-later-001",
        assessment=assessment,
        evidence_reference_ids=[evidence_id] if with_evidence else [],
        support_classification=support,
        uncertainty_classification=uncertainty,
    )
    assert diagnostic["payload"]["assessment"] == assessment
    assert diagnostic["authority"]["chronology_status"] == "not_canonical"
    assert "canonical_order" not in diagnostic["payload"]


@pytest.mark.parametrize("activity", ["active", "inactive"])
def test_active_and_inactive_thread_classification_requires_supported_evidence(activity):
    context, first_id, _, evidence_id = _context()
    diagnostic = build_thread_activity_diagnostic(
        context=context,
        source_snapshot_ids=[first_id],
        thread_ref="thread-001",
        activity_classification=activity,
        evidence_reference_ids=[evidence_id],
        support_classification="supported",
        uncertainty_classification="provisional",
    )
    assert diagnostic["payload"]["activity_classification"] == activity
    assert diagnostic["authority"]["thread_status"] == "diagnostic_only"

    with pytest.raises(ProjectNarrativeDiagnosticValidationError, match="requires evidence"):
        build_thread_activity_diagnostic(
            context=context,
            source_snapshot_ids=[first_id],
            thread_ref="thread-001",
            activity_classification=activity,
            support_classification="supported",
            uncertainty_classification="provisional",
        )


def test_unsupported_thread_activity_requires_explicit_uncertainty():
    context, first_id, _, _ = _context()
    diagnostic = build_thread_activity_diagnostic(
        context=context,
        source_snapshot_ids=[first_id],
        thread_ref="thread-001",
        activity_classification="uncertain",
        support_classification="insufficient_evidence",
        uncertainty_classification="insufficient_evidence",
    )
    assert diagnostic["payload"]["activity_classification"] == "uncertain"

    with pytest.raises(
        ProjectNarrativeDiagnosticValidationError, match="explicit uncertainty"
    ):
        build_thread_activity_diagnostic(
            context=context,
            source_snapshot_ids=[first_id],
            thread_ref="thread-001",
            activity_classification="uncertain",
            support_classification="unclassified",
            uncertainty_classification="provisional",
        )


def test_unknown_source_evidence_and_context_references_fail_closed():
    context, first_id, _, evidence_id = _context()
    with pytest.raises(ProjectNarrativeDiagnosticValidationError, match="unknown source"):
        build_timeline_diagnostic(
            context=context,
            source_snapshot_ids=["snapshot-unknown"],
            earlier_event_ref="event-001",
            later_event_ref="event-002",
            assessment="supported_ordering",
            evidence_reference_ids=[evidence_id],
            support_classification="supported",
            uncertainty_classification="provisional",
        )
    with pytest.raises(ProjectNarrativeDiagnosticValidationError, match="unknown context"):
        build_timeline_diagnostic(
            context=context,
            source_snapshot_ids=[first_id],
            earlier_event_ref="event-001",
            later_event_ref="event-002",
            assessment="supported_ordering",
            evidence_reference_ids=["evidence-unknown"],
            support_classification="supported",
            uncertainty_classification="provisional",
        )


def test_exact_source_boundaries_are_preserved_and_cannot_be_flattened():
    context, first_id, second_id, evidence_id = _context()
    with pytest.raises(
        ProjectNarrativeDiagnosticValidationError, match="undeclared source boundary"
    ):
        build_causal_continuity_diagnostic(
            context=context,
            source_snapshot_ids=[second_id],
            cause_event_ref="event-001",
            effect_event_ref="event-002",
            assessment="supported_link",
            evidence_reference_ids=[evidence_id],
            support_classification="supported",
            uncertainty_classification="provisional",
        )

    _, diagnostic = _causal()
    diagnostic["combined_source_text"] = "flattened source"
    with pytest.raises(ProjectNarrativeDiagnosticValidationError, match="not closed"):
        validate_project_narrative_diagnostic(diagnostic, context)
    assert first_id != second_id


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("raw_model_output", {"text": "opaque"}),
        ("raw_tool_output", {"status": "approved"}),
        ("canon", True),
        ("truth", "settled"),
        ("approved_memory", True),
        ("canonical_chronology", ["event-001", "event-002"]),
        ("definitive_causality", True),
        ("final_thread_truth", "active"),
        ("generate_story_prose", True),
        ("rewrite_intent", True),
        ("continuation_intent", True),
        ("promotion", True),
        ("apply_promotion", True),
        ("mutate_memory_canon", True),
    ],
)
def test_raw_output_truth_prose_promotion_and_mutation_intents_fail_closed(
    field, value
):
    context, diagnostic = _causal()
    diagnostic[field] = value
    with pytest.raises(ProjectNarrativeDiagnosticValidationError, match="not closed"):
        validate_project_narrative_diagnostic(diagnostic, context)


def test_weakened_read_only_policy_and_fabricated_lineage_fail_closed():
    context, diagnostic = _causal()
    diagnostic["authority"]["truth_status"] = "settled"
    with pytest.raises(ProjectNarrativeDiagnosticValidationError, match="authority"):
        validate_project_narrative_diagnostic(diagnostic, context)

    context, diagnostic = _causal()
    diagnostic["behavior"]["persistence"] = "write"
    with pytest.raises(ProjectNarrativeDiagnosticValidationError, match="behavior"):
        validate_project_narrative_diagnostic(diagnostic, context)

    context, diagnostic = _causal()
    diagnostic["lineage"]["run_ids"] = ["run-fabricated"]
    with pytest.raises(ProjectNarrativeDiagnosticValidationError, match="lineage"):
        validate_project_narrative_diagnostic(diagnostic, context)


def test_serialization_and_ids_are_deterministic_and_tamper_evident():
    context, diagnostic = _causal()
    first = serialize_project_narrative_diagnostic(diagnostic, context)
    second = serialize_project_narrative_diagnostic(copy.deepcopy(diagnostic), context)
    assert first == second
    assert json.loads(first) == diagnostic

    tampered = copy.deepcopy(diagnostic)
    tampered["payload"]["effect_event_ref"] = "event-effect-002"
    with pytest.raises(ProjectNarrativeDiagnosticValidationError, match="diagnostic_id"):
        validate_project_narrative_diagnostic(tampered, context)


def test_build_and_validation_have_no_persistence_or_runtime_behavior(tmp_path):
    before = list(tmp_path.iterdir())
    context, diagnostic = _causal()
    validated = validate_project_narrative_diagnostic(diagnostic, context)
    validated["source_snapshot_ids"].clear()
    assert diagnostic["source_snapshot_ids"]
    assert list(tmp_path.iterdir()) == before
    assert diagnostic["behavior"]["runtime_execution"] == "none"
    assert diagnostic["behavior"]["persistence"] == "none"
