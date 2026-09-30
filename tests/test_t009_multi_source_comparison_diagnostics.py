"""Focused T009F multi-source comparison diagnostic tests."""

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
    build_multi_source_comparison_diagnostic,
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


def _manifest(snapshot, suffix: str):
    operation = OperationDeclaration(
        operation_id=f"analyze-spacy-{suffix}",
        adapter_id="spacy",
        consumes=("owner_selected_source",),
        produces=("normalized_evidence",),
        configuration={},
        feature_flags={},
    )
    artifact = ArtifactReference(
        artifact_id=f"artifact-{suffix}",
        availability="available",
        source_snapshot_ids=(snapshot.identity.snapshot_id,),
        content_hash=suffix[0] * 64,
        hash_algorithm="sha256",
        media_type="application/json",
    )
    output = OutputLineage(
        output_id=f"output-{suffix}",
        operation_id=operation.operation_id,
        source_snapshot_ids=(snapshot.identity.snapshot_id,),
        disposition="validated",
        original_output_reference_id=artifact.artifact_id,
        evidence_reference_ids=(f"evidence-placeholder-{suffix}",),
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
        explanation="Deterministic T009F fixture lineage.",
        provenance=provenance,
        output_ids=(output.output_id,),
    )
    return AnalysisRunManifest(
        run_id=f"run-{suffix}",
        project_id="example",
        sources=(snapshot.identity,),
        operations=(operation,),
        dependency_graph=(),
        contributors=(contributor,),
        artifact_references=(artifact,),
        outputs=(output,),
        transformations=(),
        coverage="complete",
        created_at="2026-09-30T03:00:00Z",
        finalized_at="2026-09-30T03:00:01Z",
        configuration={},
        feature_flags={"candidate_first": True},
    )


def _approved_record(suffix: str):
    return build_approved_record(
        record_version=1,
        project_id="example",
        destination_type="approved_continuity_record",
        destination_key=f"continuity-{suffix}",
        source_candidate_id=f"candidate-{suffix}",
        source_promotion_id=f"promotion-{suffix}",
        source_candidate_snapshot_hash=suffix[0] * 64,
        payload={
            "payload_type": "approved_continuity_record",
            "continuity_label": f"Owner-approved reference {suffix}",
            "facts": [
                {
                    "field": "reference_state",
                    "value": "owner_approved",
                    "evidence_ref_ids": [f"evidence-approved-{suffix}"],
                    "provenance_ref_ids": [f"provenance-approved-{suffix}"],
                }
            ],
        },
        evidence_refs=[
            {
                "ref_id": f"evidence-approved-{suffix}",
                "locator_id": f"locator-{suffix}",
            }
        ],
        provenance_refs=[
            {
                "provenance_id": f"provenance-approved-{suffix}",
                "source_kind": "owner_decision",
                "source_id": f"decision-{suffix}",
            }
        ],
        source_locators=[
            {
                "locator_id": f"locator-{suffix}",
                "locator_kind": "source_snapshot",
                "locator": f"scene:scene-{suffix}",
            }
        ],
    )


def _context():
    snapshots = {
        suffix: _snapshot(f"scene-{suffix}", f"Exact source {suffix}.")
        for suffix in ("aaa", "bbb", "ccc")
    }
    manifests = {
        suffix: _manifest(snapshot, suffix)
        for suffix, snapshot in snapshots.items()
    }
    evidence = {
        suffix: build_exact_evidence_record(
            snapshot=snapshot,
            run_id=manifests[suffix].run_id,
            artifact_id=f"artifact-{suffix}",
            artifact_file_id=f"artifact-file-{suffix}",
            operation_id=f"analyze-spacy-{suffix}",
            adapter_id="spacy",
            disposition="validated",
            contributor_state="succeeded",
            created_at="2026-09-30T03:00:00Z",
            character_range=OffsetRange(0, 5, CHAR_OFFSET_BASIS),
            output_id=f"output-{suffix}",
        )
        for suffix, snapshot in snapshots.items()
    }
    support = {
        suffix: build_diagnostic_support_reference(
            support_reference_id=f"support-{suffix}",
            support_kind="diagnostic",
            source_snapshot_ids=[snapshot.identity.snapshot_id],
            run_id=manifests[suffix].run_id,
            evidence_reference_ids=[evidence[suffix]["evidence_id"]],
            provenance_reference_ids=[f"provenance-spacy-{suffix}"],
            support_classification="supported",
            uncertainty_classification="provisional",
        )
        for suffix, snapshot in snapshots.items()
    }
    approved = {
        suffix: build_approved_context_snapshot(
            _approved_record(suffix),
            source_snapshot_ids=[snapshot.identity.snapshot_id],
        )
        for suffix, snapshot in snapshots.items()
    }
    context = build_project_diagnostic_context(
        project_id="example",
        sources=[
            build_project_diagnostic_source(
                snapshots["aaa"], source_role="primary"
            ),
            build_project_diagnostic_source(
                snapshots["bbb"], source_role="comparison"
            ),
            build_project_diagnostic_source(
                snapshots["ccc"], source_role="reference"
            ),
        ],
        run_manifests=list(manifests.values()),
        evidence_records=list(evidence.values()),
        approved_context_snapshots=list(approved.values()),
        diagnostic_support_references=list(support.values()),
    )
    return {
        "context": context,
        "source": {
            suffix: snapshot.identity.snapshot_id
            for suffix, snapshot in snapshots.items()
        },
        "evidence": {
            suffix: record["evidence_id"] for suffix, record in evidence.items()
        },
        "support": {
            suffix: record["support_reference_id"]
            for suffix, record in support.items()
        },
        "approved": {
            suffix: record["context_snapshot_id"]
            for suffix, record in approved.items()
        },
    }


def _comparison(fixture=None, **overrides):
    fixture = fixture or _context()
    values = {
        "context": fixture["context"],
        "source_snapshot_ids": [
            fixture["source"]["bbb"],
            fixture["source"]["aaa"],
        ],
        "comparison_subject_ref": "subject-001",
        "comparison_axis_ref": "continuity-axis-001",
        "source_comparison_refs": [
            {
                "source_snapshot_id": fixture["source"]["bbb"],
                "comparison_reference_id": "state-bbb",
            },
            {
                "source_snapshot_id": fixture["source"]["aaa"],
                "comparison_reference_id": "state-aaa",
            },
        ],
        "assessment": "supported_difference",
        "related_diagnostic_context_ref": "diagnostic-context-001",
        "evidence_reference_ids": [
            fixture["evidence"]["bbb"],
            fixture["evidence"]["aaa"],
        ],
        "diagnostic_support_reference_ids": [
            fixture["support"]["bbb"],
            fixture["support"]["aaa"],
        ],
        "approved_context_snapshot_ids": [
            fixture["approved"]["bbb"],
            fixture["approved"]["aaa"],
        ],
        "support_classification": "supported",
        "uncertainty_classification": "provisional",
    }
    values.update(overrides)
    return fixture, build_multi_source_comparison_diagnostic(**values)


def test_comparison_is_deterministic_read_only_evidence_backed_and_non_canon():
    fixture, first = _comparison()
    _, second = _comparison()
    assert first == second
    assert first["schema_version"] == PROJECT_NARRATIVE_DIAGNOSTIC_VERSION
    assert first["diagnostic_kind"] == "multi_source_comparison"
    assert first["source_snapshot_ids"] == sorted(
        [fixture["source"]["aaa"], fixture["source"]["bbb"]]
    )
    assert first["payload"]["source_comparison_refs"] == sorted(
        first["payload"]["source_comparison_refs"],
        key=lambda item: item["source_snapshot_id"],
    )
    assert first["authority"]["multi_source_comparison_status"] == "diagnostic_only"
    assert first["authority"]["truth_status"] == "not_settled"
    assert first["authority"]["canon_status"] == "not_selected"
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
    assert first["lineage"]["run_ids"] == ["run-aaa", "run-bbb"]
    assert validate_project_narrative_diagnostic(first, fixture["context"]) == first


@pytest.mark.parametrize(
    ("assessment", "support", "uncertainty", "with_evidence"),
    [
        ("supported_alignment", "supported", "provisional", True),
        ("supported_difference", "supported", "provisional", True),
        ("supported_gap", "supported", "provisional", True),
        ("supported_conflict", "ambiguous", "conflicting", True),
        ("unsupported", "unsupported", "ambiguous", False),
        ("ambiguous", "ambiguous", "ambiguous", False),
        (
            "insufficient_evidence",
            "insufficient_evidence",
            "insufficient_evidence",
            False,
        ),
    ],
)
def test_all_assessments_remain_diagnostic_only(
    assessment, support, uncertainty, with_evidence
):
    fixture = _context()
    evidence = (
        [fixture["evidence"]["aaa"], fixture["evidence"]["bbb"]]
        if with_evidence
        else []
    )
    _, diagnostic = _comparison(
        fixture,
        assessment=assessment,
        evidence_reference_ids=evidence,
        diagnostic_support_reference_ids=[],
        approved_context_snapshot_ids=[],
        support_classification=support,
        uncertainty_classification=uncertainty,
    )
    assert diagnostic["payload"]["assessment"] == assessment
    assert diagnostic["authority"]["truth_status"] == "not_settled"
    assert diagnostic["authority"]["canon_status"] == "not_selected"
    assert diagnostic["authority"]["multi_source_comparison_status"] == (
        "diagnostic_only"
    )


def test_comparison_requires_two_distinct_well_formed_source_references():
    fixture = _context()
    one_source_ref = [
        {
            "source_snapshot_id": fixture["source"]["aaa"],
            "comparison_reference_id": "state-aaa",
        }
    ]
    with pytest.raises(ProjectNarrativeDiagnosticValidationError, match="two source"):
        _comparison(
            fixture,
            source_snapshot_ids=[fixture["source"]["aaa"]],
            source_comparison_refs=one_source_ref,
            evidence_reference_ids=[fixture["evidence"]["aaa"]],
            diagnostic_support_reference_ids=[],
            approved_context_snapshot_ids=[],
        )

    duplicate_source_refs = [
        one_source_ref[0],
        {
            "source_snapshot_id": fixture["source"]["aaa"],
            "comparison_reference_id": "state-other",
        },
    ]
    with pytest.raises(ProjectNarrativeDiagnosticValidationError, match="distinct"):
        _comparison(fixture, source_comparison_refs=duplicate_source_refs)

    duplicate_comparison_refs = [
        one_source_ref[0],
        {
            "source_snapshot_id": fixture["source"]["bbb"],
            "comparison_reference_id": "state-aaa",
        },
    ]
    with pytest.raises(ProjectNarrativeDiagnosticValidationError, match="distinct"):
        _comparison(fixture, source_comparison_refs=duplicate_comparison_refs)

    with pytest.raises(ProjectNarrativeDiagnosticValidationError, match="not closed"):
        _comparison(fixture, source_comparison_refs=["not-a-ref", "also-not-a-ref"])

    malformed = copy.deepcopy(_comparison(fixture)[1])
    malformed["payload"]["source_comparison_refs"][0]["source_text"] = "flattened"
    with pytest.raises(ProjectNarrativeDiagnosticValidationError, match="not closed"):
        validate_project_narrative_diagnostic(malformed, fixture["context"])


def test_payload_sources_must_exactly_match_declared_source_boundaries():
    fixture = _context()
    refs = copy.deepcopy(_comparison(fixture)[1]["payload"]["source_comparison_refs"])
    refs[1] = {
        "source_snapshot_id": fixture["source"]["ccc"],
        "comparison_reference_id": "state-ccc",
    }
    with pytest.raises(ProjectNarrativeDiagnosticValidationError, match="match declared"):
        _comparison(fixture, source_comparison_refs=refs)


def test_supported_comparison_requires_evidence_for_every_compared_source():
    fixture = _context()
    with pytest.raises(ProjectNarrativeDiagnosticValidationError, match="require evidence"):
        _comparison(fixture, evidence_reference_ids=[])
    with pytest.raises(
        ProjectNarrativeDiagnosticValidationError, match="every compared source"
    ):
        _comparison(
            fixture,
            evidence_reference_ids=[fixture["evidence"]["aaa"]],
        )


def test_unsupported_without_evidence_requires_explicit_uncertainty():
    fixture = _context()
    with pytest.raises(
        ProjectNarrativeDiagnosticValidationError,
        match="evidence or explicit uncertainty",
    ):
        _comparison(
            fixture,
            assessment="unsupported",
            evidence_reference_ids=[],
            diagnostic_support_reference_ids=[],
            approved_context_snapshot_ids=[],
            support_classification="unsupported",
            uncertainty_classification="provisional",
        )


@pytest.mark.parametrize(
    ("field", "unknown", "message"),
    [
        ("source_snapshot_ids", ["snapshot-unknown", "snapshot-other"], "unknown source"),
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
    fixture, diagnostic = _comparison()
    diagnostic[field] = unknown
    with pytest.raises(ProjectNarrativeDiagnosticValidationError, match=message):
        validate_project_narrative_diagnostic(diagnostic, fixture["context"])


@pytest.mark.parametrize("basis", ["evidence", "support", "approved"])
def test_basis_cannot_cross_undeclared_source_boundaries(basis):
    fixture = _context()
    overrides = {
        "evidence_reference_ids": [
            fixture["evidence"]["aaa"],
            fixture["evidence"]["bbb"],
        ],
        "diagnostic_support_reference_ids": [],
        "approved_context_snapshot_ids": [],
    }
    if basis == "evidence":
        overrides["evidence_reference_ids"].append(fixture["evidence"]["ccc"])
    elif basis == "support":
        overrides["diagnostic_support_reference_ids"] = [fixture["support"]["ccc"]]
    else:
        overrides["approved_context_snapshot_ids"] = [fixture["approved"]["ccc"]]
    with pytest.raises(
        ProjectNarrativeDiagnosticValidationError,
        match="undeclared source boundary",
    ):
        _comparison(fixture, **overrides)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("combined_source_text", "flattened"),
        ("merged_source_payload", {"sources": "flattened"}),
        ("raw_model_output", {"state": "approved"}),
        ("raw_tool_output", {"state": "approved"}),
        ("truth", "settled"),
        ("canon", True),
        ("approved_memory", True),
        ("canonical_comparison", True),
        ("canonical_reconciliation", True),
        ("canonical_conflict", True),
        ("source_priority", "source-a"),
        ("definitive_timeline", True),
        ("definitive_world_truth", True),
        ("definitive_relationship_truth", True),
        ("definitive_emotional_truth", True),
        ("canonical_promise_payoff", True),
        ("canonical_hook", True),
        ("canonical_lifecycle_state", True),
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
    fixture, diagnostic = _comparison()
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
def test_comparison_cannot_infer_author_intent(support, uncertainty):
    fixture = _context()
    with pytest.raises(ProjectNarrativeDiagnosticValidationError, match="author intent"):
        _comparison(
            fixture,
            assessment="ambiguous",
            support_classification=support,
            uncertainty_classification=uncertainty,
        )


def test_payload_is_closed_and_compact():
    fixture, diagnostic = _comparison()
    diagnostic["payload"]["canonical_source"] = fixture["source"]["aaa"]
    with pytest.raises(ProjectNarrativeDiagnosticValidationError, match="not closed"):
        validate_project_narrative_diagnostic(diagnostic, fixture["context"])

    fixture = _context()
    with pytest.raises(ProjectNarrativeDiagnosticValidationError, match="safe identifier"):
        _comparison(fixture, comparison_axis_ref="../canonical-axis")


def test_weakened_authority_behavior_and_fabricated_lineage_fail_closed():
    fixture, diagnostic = _comparison()
    diagnostic["authority"]["multi_source_comparison_status"] = "canonical"
    with pytest.raises(ProjectNarrativeDiagnosticValidationError, match="authority"):
        validate_project_narrative_diagnostic(diagnostic, fixture["context"])

    fixture, diagnostic = _comparison()
    diagnostic["behavior"]["runtime_execution"] = "enabled"
    with pytest.raises(ProjectNarrativeDiagnosticValidationError, match="behavior"):
        validate_project_narrative_diagnostic(diagnostic, fixture["context"])

    fixture, diagnostic = _comparison()
    diagnostic["lineage"]["run_ids"] = ["run-fabricated"]
    with pytest.raises(ProjectNarrativeDiagnosticValidationError, match="lineage"):
        validate_project_narrative_diagnostic(diagnostic, fixture["context"])


def test_serialization_and_id_are_deterministic_and_tamper_evident():
    fixture, diagnostic = _comparison()
    first = serialize_project_narrative_diagnostic(diagnostic, fixture["context"])
    second = serialize_project_narrative_diagnostic(
        copy.deepcopy(diagnostic), fixture["context"]
    )
    assert first == second
    assert json.loads(first) == diagnostic

    tampered = copy.deepcopy(diagnostic)
    tampered["payload"]["comparison_axis_ref"] = "axis-tampered"
    with pytest.raises(ProjectNarrativeDiagnosticValidationError, match="diagnostic_id"):
        validate_project_narrative_diagnostic(tampered, fixture["context"])


def test_empty_context_and_build_validation_have_no_runtime_or_persistence(tmp_path):
    fixture, diagnostic = _comparison()
    invalid_context = copy.deepcopy(fixture["context"])
    invalid_context["sources"] = []
    with pytest.raises(ProjectNarrativeDiagnosticValidationError, match="valid T009A"):
        _comparison(fixture | {"context": invalid_context})

    before = list(tmp_path.iterdir())
    validated = validate_project_narrative_diagnostic(
        diagnostic, fixture["context"]
    )
    validated["source_snapshot_ids"].clear()
    assert diagnostic["source_snapshot_ids"]
    assert list(tmp_path.iterdir()) == before
    assert diagnostic["behavior"]["persistence"] == "none"
    assert diagnostic["behavior"]["runtime_execution"] == "none"
