"""Cross-diagnostic T009G safety and non-authority regression tests."""

from __future__ import annotations

import copy
import json

import pytest

from backend.story_knowledge.project_diagnostic_context import (
    build_project_diagnostic_context,
    build_project_diagnostic_source,
)
from backend.story_knowledge.project_narrative_diagnostics import (
    DIAGNOSTIC_KINDS,
    ProjectNarrativeDiagnosticValidationError,
    build_causal_continuity_diagnostic,
    build_emotional_state_delta_diagnostic,
    build_hook_foreshadowing_diagnostic,
    build_information_boundary_diagnostic,
    build_multi_source_comparison_diagnostic,
    build_narrative_lifecycle_diagnostic,
    build_promise_payoff_diagnostic,
    build_relationship_delta_diagnostic,
    build_thread_activity_diagnostic,
    build_timeline_diagnostic,
    serialize_project_narrative_diagnostic,
    validate_project_narrative_diagnostic,
)
from backend.story_knowledge.source_map import build_exact_source_snapshot


AUTHORITY_BOUNDARY = {
    "mode": "read_only_non_authoritative",
    "truth_status": "not_settled",
    "canon_status": "not_selected",
    "world_state_status": "not_settled",
    "chronology_status": "not_canonical",
    "causality_status": "not_canonical",
    "thread_status": "diagnostic_only",
    "relationship_status": "not_settled",
    "emotional_status": "not_settled",
    "promise_payoff_status": "diagnostic_only",
    "hook_foreshadowing_status": "diagnostic_only",
    "lifecycle_status": "not_canonical",
    "multi_source_comparison_status": "diagnostic_only",
    "author_intent_status": "not_inferred",
    "approved_memory_status": "not_established",
    "owner_control": "required",
}

BEHAVIOR_BOUNDARY = {
    "persistence": "none",
    "runtime_execution": "none",
    "story_prose_output": "forbidden",
    "promotion": "none",
    "apply_promotion": "none",
    "memory_canon_mutation": "none",
}

FORBIDDEN_SETTLEMENT_FIELDS = (
    ("world_state", {"state": "settled"}),
    ("canonical_world_state", True),
    ("truth", "settled"),
    ("truth_status", "settled"),
    ("canon", True),
    ("canonical_fact", True),
    ("canonical_chronology", True),
    ("canonical_causality", True),
    ("canonical_relationship", True),
    ("canonical_emotion", True),
    ("canonical_hook", True),
    ("canonical_promise", True),
    ("canonical_payoff", True),
    ("canonical_lifecycle_state", True),
    ("source_priority", "source-primary"),
    ("source_correctness", "source-primary"),
    ("approved_memory", True),
    ("author_intent", "inferred"),
    ("future_story_obligation", "required"),
    ("generated_story_text", "forbidden"),
    ("generate_outline", True),
    ("generate_chapter", True),
    ("generate_revision", True),
    ("generate_continuation", True),
    ("rewrite_intent", True),
    ("continuation_intent", True),
    ("promotion", True),
    ("apply_promotion", True),
    ("mutate_memory_canon", True),
    ("raw_model_output", {"status": "approved"}),
    ("raw_tool_output", {"status": "approved"}),
)


def _fixture() -> dict[str, object]:
    snapshots = [
        build_exact_source_snapshot(
            project_id="t009g-example",
            source_document_type="scene",
            source_document_id=f"scene-{suffix}",
            source_document_version="1",
            source_ownership="owner_authored",
            source_content=f"Exact diagnostic source {suffix}.",
            scene_id=f"scene-{suffix}",
            source_map_id=f"map-{suffix}",
        )
        for suffix in ("primary", "comparison", "reference")
    ]
    context = build_project_diagnostic_context(
        project_id="t009g-example",
        sources=[
            build_project_diagnostic_source(snapshots[0], source_role="primary"),
            build_project_diagnostic_source(
                snapshots[1], source_role="comparison"
            ),
            build_project_diagnostic_source(
                snapshots[2], source_role="reference"
            ),
        ],
    )
    return {
        "context": context,
        "source_ids": [snapshot.identity.snapshot_id for snapshot in snapshots],
    }


def _build(
    kind: str,
    fixture: dict[str, object],
    *,
    supported_without_evidence: bool = False,
) -> dict[str, object]:
    context = fixture["context"]
    source_ids = fixture["source_ids"]
    assert isinstance(source_ids, list)
    source_id = source_ids[0]
    support = "supported" if supported_without_evidence else "insufficient_evidence"
    uncertainty = (
        "provisional" if supported_without_evidence else "insufficient_evidence"
    )
    common = {
        "context": context,
        "source_snapshot_ids": [source_id],
        "support_classification": support,
        "uncertainty_classification": uncertainty,
    }

    if kind == "causal_continuity":
        return build_causal_continuity_diagnostic(
            **common,
            cause_event_ref="event-cause",
            effect_event_ref="event-effect",
            assessment=(
                "supported_link"
                if supported_without_evidence
                else "insufficient_evidence"
            ),
        )
    if kind == "chronology_timeline":
        return build_timeline_diagnostic(
            **common,
            earlier_event_ref="event-earlier",
            later_event_ref="event-later",
            assessment=(
                "supported_ordering"
                if supported_without_evidence
                else "insufficient_evidence"
            ),
        )
    if kind == "thread_activity":
        return build_thread_activity_diagnostic(
            **common,
            thread_ref="thread-main",
            activity_classification=(
                "active" if supported_without_evidence else "uncertain"
            ),
        )
    if kind == "information_boundary":
        return build_information_boundary_diagnostic(
            **common,
            information_ref="information-key",
            apparently_informed_actor_ref="actor-informed",
            apparently_uninformed_actor_ref="actor-uninformed",
            assessment=(
                "supported_boundary"
                if supported_without_evidence
                else "insufficient_evidence"
            ),
        )
    if kind == "relationship_delta":
        return build_relationship_delta_diagnostic(
            **common,
            participant_refs=["actor-b", "actor-a"],
            relationship_axis="trust",
            prior_reference="relationship-prior",
            later_reference="relationship-later",
            delta_assessment=(
                "supported_change"
                if supported_without_evidence
                else "insufficient_evidence"
            ),
        )
    if kind == "emotional_state_delta":
        return build_emotional_state_delta_diagnostic(
            **common,
            subject_ref="actor-a",
            emotional_axis="trust",
            prior_reference="emotion-prior",
            later_reference="emotion-later",
            related_context_ref="relationship-context",
            delta_assessment=(
                "supported_change"
                if supported_without_evidence
                else "insufficient_evidence"
            ),
        )
    if kind == "promise_payoff":
        return build_promise_payoff_diagnostic(
            **common,
            promise_ref="promise-a",
            payoff_ref="payoff-a",
            narrative_element_ref="thread-main",
            lifecycle_context_ref="lifecycle-context",
            assessment=(
                "supported_pairing"
                if supported_without_evidence
                else "insufficient_evidence"
            ),
        )
    if kind == "hook_foreshadowing":
        return build_hook_foreshadowing_diagnostic(
            **common,
            hook_ref="hook-a",
            foreshadowing_ref="foreshadowing-a",
            target_ref="target-a",
            lifecycle_context_ref="lifecycle-context",
            assessment=(
                "supported_link"
                if supported_without_evidence
                else "insufficient_evidence"
            ),
        )
    if kind == "narrative_lifecycle":
        return build_narrative_lifecycle_diagnostic(
            **common,
            lifecycle_subject_ref="thread-main",
            lifecycle_stage_ref="stage-current",
            prior_reference=None,
            current_reference=(
                "state-current" if supported_without_evidence else None
            ),
            related_thread_ref="thread-related",
            assessment=(
                "supported_active"
                if supported_without_evidence
                else "insufficient_evidence"
            ),
        )
    if kind == "multi_source_comparison":
        compared_ids = source_ids[:2]
        return build_multi_source_comparison_diagnostic(
            context=context,
            source_snapshot_ids=compared_ids,
            comparison_subject_ref="subject-a",
            comparison_axis_ref="continuity-axis",
            source_comparison_refs=[
                {
                    "source_snapshot_id": compared_ids[1],
                    "comparison_reference_id": "comparison-b",
                },
                {
                    "source_snapshot_id": compared_ids[0],
                    "comparison_reference_id": "comparison-a",
                },
            ],
            related_diagnostic_context_ref="diagnostic-context",
            assessment=(
                "supported_alignment"
                if supported_without_evidence
                else "insufficient_evidence"
            ),
            support_classification=support,
            uncertainty_classification=uncertainty,
        )
    raise AssertionError(f"uncovered diagnostic kind: {kind}")


def _all_diagnostics(
    fixture: dict[str, object],
) -> dict[str, dict[str, object]]:
    return {kind: _build(kind, fixture) for kind in sorted(DIAGNOSTIC_KINDS)}


def test_all_accepted_builders_are_deterministic_read_only_and_non_authoritative():
    fixture = _fixture()
    context_before = copy.deepcopy(fixture["context"])
    first = _all_diagnostics(fixture)
    second = _all_diagnostics(fixture)

    assert set(first) == DIAGNOSTIC_KINDS
    assert first == second
    assert fixture["context"] == context_before
    assert len({item["diagnostic_id"] for item in first.values()}) == len(
        DIAGNOSTIC_KINDS
    )

    for kind, diagnostic in first.items():
        assert diagnostic["diagnostic_kind"] == kind
        assert diagnostic["support_classification"] == "insufficient_evidence"
        assert diagnostic["uncertainty_classification"] == "insufficient_evidence"
        assert diagnostic["authority"] == AUTHORITY_BOUNDARY
        assert diagnostic["behavior"] == BEHAVIOR_BOUNDARY
        assert validate_project_narrative_diagnostic(
            diagnostic, fixture["context"]
        ) == diagnostic
        serialized = serialize_project_narrative_diagnostic(
            diagnostic, fixture["context"]
        )
        assert json.loads(serialized) == diagnostic
        assert serialized == serialize_project_narrative_diagnostic(
            copy.deepcopy(diagnostic), fixture["context"]
        )


@pytest.mark.parametrize("kind", sorted(DIAGNOSTIC_KINDS))
def test_no_diagnostic_kind_can_weaken_authority_or_enable_behavior(kind):
    fixture = _fixture()
    baseline = _build(kind, fixture)

    for field, expected in AUTHORITY_BOUNDARY.items():
        weakened = copy.deepcopy(baseline)
        weakened["authority"][field] = f"weakened-{expected}"
        with pytest.raises(
            ProjectNarrativeDiagnosticValidationError, match="authority"
        ):
            validate_project_narrative_diagnostic(weakened, fixture["context"])

    for field, expected in BEHAVIOR_BOUNDARY.items():
        enabled = copy.deepcopy(baseline)
        enabled["behavior"][field] = f"enabled-{expected}"
        with pytest.raises(
            ProjectNarrativeDiagnosticValidationError, match="behavior"
        ):
            validate_project_narrative_diagnostic(enabled, fixture["context"])


@pytest.mark.parametrize("kind", sorted(DIAGNOSTIC_KINDS))
def test_settlement_generation_promotion_and_raw_output_fields_fail_closed(kind):
    fixture = _fixture()
    baseline = _build(kind, fixture)

    for location in ("top_level", "payload"):
        for field, value in FORBIDDEN_SETTLEMENT_FIELDS:
            unsafe = copy.deepcopy(baseline)
            target = unsafe if location == "top_level" else unsafe["payload"]
            target[field] = copy.deepcopy(value)
            with pytest.raises(
                ProjectNarrativeDiagnosticValidationError, match="not closed"
            ):
                validate_project_narrative_diagnostic(
                    unsafe, fixture["context"]
                )


@pytest.mark.parametrize("kind", sorted(DIAGNOSTIC_KINDS))
def test_unknown_references_and_fabricated_run_lineage_fail_closed(kind):
    fixture = _fixture()
    baseline = _build(kind, fixture)
    cases = (
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
    )
    for field, value, message in cases:
        unsafe = copy.deepcopy(baseline)
        unsafe[field] = value
        with pytest.raises(
            ProjectNarrativeDiagnosticValidationError, match=message
        ):
            validate_project_narrative_diagnostic(unsafe, fixture["context"])

    fabricated = copy.deepcopy(baseline)
    fabricated["lineage"]["run_ids"] = ["run-fabricated"]
    with pytest.raises(
        ProjectNarrativeDiagnosticValidationError, match="lineage"
    ):
        validate_project_narrative_diagnostic(fabricated, fixture["context"])


@pytest.mark.parametrize("kind", sorted(DIAGNOSTIC_KINDS))
def test_supported_classifications_cannot_exist_without_direct_evidence(kind):
    fixture = _fixture()
    with pytest.raises(
        ProjectNarrativeDiagnosticValidationError, match=r"require.*evidence"
    ):
        _build(kind, fixture, supported_without_evidence=True)


def test_ambiguous_and_unsupported_states_remain_explicit_and_non_authoritative():
    fixture = _fixture()
    source_id = fixture["source_ids"][0]
    ambiguous = build_relationship_delta_diagnostic(
        context=fixture["context"],
        source_snapshot_ids=[source_id],
        participant_refs=["actor-a", "actor-b"],
        relationship_axis="trust",
        prior_reference="relationship-prior",
        later_reference="relationship-later",
        delta_assessment="ambiguous",
        support_classification="ambiguous",
        uncertainty_classification="ambiguous",
    )
    unsupported = build_promise_payoff_diagnostic(
        context=fixture["context"],
        source_snapshot_ids=[source_id],
        promise_ref="promise-a",
        payoff_ref=None,
        narrative_element_ref="thread-main",
        assessment="unsupported",
        support_classification="unsupported",
        uncertainty_classification="ambiguous",
    )

    assert ambiguous["payload"]["delta_assessment"] == "ambiguous"
    assert ambiguous["support_classification"] == "ambiguous"
    assert unsupported["payload"]["assessment"] == "unsupported"
    assert unsupported["support_classification"] == "unsupported"
    for diagnostic in (ambiguous, unsupported):
        assert diagnostic["authority"] == AUTHORITY_BOUNDARY
        assert diagnostic["behavior"] == BEHAVIOR_BOUNDARY


def test_multi_source_diagnostic_preserves_exact_source_boundaries():
    fixture = _fixture()
    source_ids = fixture["source_ids"]
    with pytest.raises(
        ProjectNarrativeDiagnosticValidationError, match="match declared"
    ):
        build_multi_source_comparison_diagnostic(
            context=fixture["context"],
            source_snapshot_ids=[source_ids[0], source_ids[2]],
            comparison_subject_ref="subject-a",
            comparison_axis_ref="continuity-axis",
            source_comparison_refs=[
                {
                    "source_snapshot_id": source_ids[0],
                    "comparison_reference_id": "comparison-a",
                },
                {
                    "source_snapshot_id": source_ids[1],
                    "comparison_reference_id": "comparison-b",
                },
            ],
            assessment="insufficient_evidence",
            support_classification="insufficient_evidence",
            uncertainty_classification="insufficient_evidence",
        )


@pytest.mark.parametrize("kind", sorted(DIAGNOSTIC_KINDS))
def test_diagnostic_ids_are_tamper_evident(kind):
    fixture = _fixture()
    diagnostic = _build(kind, fixture)
    tampered = copy.deepcopy(diagnostic)
    tampered["diagnostic_id"] = "narrative-diagnostic-" + "0" * 64
    with pytest.raises(
        ProjectNarrativeDiagnosticValidationError, match="diagnostic_id"
    ):
        validate_project_narrative_diagnostic(tampered, fixture["context"])


def test_build_and_validation_do_not_mutate_inputs_or_write_artifacts(tmp_path):
    fixture = _fixture()
    context_before = copy.deepcopy(fixture["context"])
    diagnostics = _all_diagnostics(fixture)
    before = list(tmp_path.iterdir())

    for diagnostic in diagnostics.values():
        diagnostic_before = copy.deepcopy(diagnostic)
        validated = validate_project_narrative_diagnostic(
            diagnostic, fixture["context"]
        )
        validated["payload"]["validation_probe"] = True
        validated["source_snapshot_ids"].clear()
        assert diagnostic == diagnostic_before

    assert fixture["context"] == context_before
    assert list(tmp_path.iterdir()) == before
    assert all(
        diagnostic["behavior"] == BEHAVIOR_BOUNDARY
        for diagnostic in diagnostics.values()
    )
