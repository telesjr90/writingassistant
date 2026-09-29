"""PHASE8-IMPL-025-T008 cross-adapter semantic guardrail regressions."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from backend import omi_analysis_orchestrator as oao, project_manager
from backend.story_knowledge import analysis_run_control
from backend.story_knowledge import semantic_guardrails as sg


def _finding(adapter: str = "ollama_model", **overrides: Any) -> dict[str, Any]:
    finding: dict[str, Any] = {
        "candidate_type": "character",
        "label": "Mara Vale",
        "extracted_claim": "Mara Vale appears as a character candidate",
        "evidence": [
            {
                "source_excerpt": "Mara Vale",
                "source_locator": "raw_idea:L1:C1-10",
                "source_id": "idea-1",
                "source_sha256": "a" * 64,
            }
        ],
        "source_locator": "raw_idea:L1:C1-10",
        "provenance": {
            "tool_source": adapter,
            "adapter": adapter,
            "support": "candidate support only",
            "operation_id": f"analyze-{adapter}",
            "original_output_reference_id": f"original-{adapter}",
        },
        "source_adapter": adapter,
        "support_label": "candidate support only",
        "owner_decision": {"decision": "pending", "approved": False},
        "review_status": "candidate_review_pending",
        "raw_finding_id": f"{adapter}-finding-1",
        "candidate_fingerprint": "omi-cand-test",
        "evidence_fingerprint": "omi-evid-test",
        "normalized_finding_id": f"omi-find-{adapter}-test",
        "duplicate_of": [],
        "related_finding_ids": [],
        "conflict_group_id": None,
        "uncertainty_label": None,
    }
    finding.update(overrides)
    return finding


def _producer_evidence(
    adapter: str = "booknlp", *, source_sha256: str = "a" * 64
) -> dict[str, Any]:
    return _finding(
        adapter,
        candidate_type="evidence_note",
        label="Upstream normalized evidence",
        extracted_claim="The source span supplies normalized evidence",
        evidence=[
            {
                "source_excerpt": "Mara Vale",
                "source_locator": "raw_idea:L1:C1-10",
                "source_id": "idea-1",
                "source_sha256": source_sha256,
            }
        ],
        raw_finding_id=f"{adapter}-evidence-1",
        normalized_finding_id=f"omi-find-{adapter}-evidence-1",
    )


def _input(
    finding: dict[str, Any],
    *,
    evidence: list[dict[str, Any]] | None = None,
    approved_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return sg.build_guardrail_input(
        finding,
        normalized_evidence=[_producer_evidence()] if evidence is None else evidence,
        source_lineage={
            "run_id": "run-1",
            "source_identity": {
                "source_id": "idea-1",
                "content_hash": "a" * 64,
            },
        },
        approved_context=approved_context,
    )


def _classify(finding: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
    return sg.evaluate_guardrail(_input(finding, **kwargs))


def test_exact_classification_vocabulary_and_contract_versions() -> None:
    assert sg.SEMANTIC_CLASSIFICATIONS == {
        "supported",
        "unsupported",
        "ambiguous",
        "subject_matter_only",
        "author_intent_dependent",
        "insufficient_evidence",
    }
    assert oao.OMI_SEMANTIC_GUARDRAIL_CONTRACT == {
        "contract_version": "omi-semantic-guardrails.v1",
        "annotation_schema_version": "omi-semantic-guardrail-annotation.v1",
        "classifications": sorted(sg.SEMANTIC_CLASSIFICATIONS),
        "execution_order": "post_normalization_pre_fusion",
        "separate_annotations": True,
        "rewrites_findings": False,
        "selects_truth_or_canon": False,
        "selects_owner_decision": False,
    }


@pytest.mark.parametrize(
    "adapter",
    [
        "ollama_model",
        "story_check",
        "ncp",
        "subtxt",
        "subtxt_informed_rubric",
        "dramatica_flow_informed_rubric",
    ],
)
def test_required_contributor_identities_share_one_classifier(adapter: str) -> None:
    finding = _finding(adapter)
    annotation = _classify(finding)

    assert annotation["classification"] == "supported"
    assert annotation["source_adapter"] == adapter
    assert annotation["normalized_finding_id"] == finding["normalized_finding_id"]
    assert annotation["operation_id"] == f"analyze-{adapter}"
    assert annotation["reason_codes"] == ["direct_normalized_evidence_support"]


def test_interpretive_finding_cannot_satisfy_its_own_evidence_dependency() -> None:
    finding = _finding("ollama_model")

    annotation = _classify(finding, evidence=[finding])

    assert annotation["classification"] == "insufficient_evidence"
    assert annotation["reason_codes"] == ["eligible_normalized_evidence_missing"]
    assert annotation["normalized_evidence_references"] == []
    assert annotation["normalized_evidence_dependency"] == {
        "required": True,
        "satisfied": False,
        "supplied_count": 1,
        "eligible_count": 0,
        "eligible_producer_adapters": [],
    }


def test_same_source_booknlp_evidence_satisfies_model_dependency() -> None:
    finding = _finding("ollama_model")
    producer = _producer_evidence("booknlp")

    annotation = _classify(finding, evidence=[producer])

    assert annotation["classification"] == "supported"
    assert annotation["normalized_evidence_dependency"]["satisfied"] is True
    assert annotation["normalized_evidence_dependency"][
        "eligible_producer_adapters"
    ] == ["booknlp"]
    assert annotation["normalized_evidence_references"][0][
        "producer_operation_id"
    ] == "analyze-booknlp"
    assert annotation["source_lineage"] == {
        "run_id": "run-1",
        "source_id": "idea-1",
        "source_hash": "a" * 64,
    }


def test_unrelated_source_normalized_evidence_fails_closed() -> None:
    finding = _finding("ollama_model")
    unrelated = _producer_evidence("spacy", source_sha256="b" * 64)

    annotation = _classify(finding, evidence=[unrelated])

    assert annotation["classification"] == "insufficient_evidence"
    assert annotation["reason_codes"] == [
        "normalized_evidence_source_lineage_mismatch"
    ]
    assert annotation["normalized_evidence_dependency"]["satisfied"] is False


def test_interpretive_findings_cannot_support_each_other() -> None:
    ollama = _finding("ollama_model")
    subtxt = _finding(
        "subtxt",
        raw_finding_id="subtxt-interpretive-1",
        normalized_finding_id="omi-find-subtxt-interpretive-1",
    )

    annotations = sg.assess_findings(
        [ollama, subtxt],
        normalized_evidence=[ollama, subtxt],
        source_lineage={
            "run_id": "run-1",
            "source_identity": {
                "source_id": "idea-1",
                "content_hash": "a" * 64,
            },
        },
    )

    assert [item["classification"] for item in annotations] == [
        "insufficient_evidence",
        "insufficient_evidence",
    ]
    assert all(
        item["reason_codes"] == ["eligible_normalized_evidence_missing"]
        for item in annotations
    )


def test_all_six_classifications_are_deterministically_reachable() -> None:
    supported = _finding()
    quarantined = _finding(
        support_metadata={
            "verification_state": "quarantined",
            "story_check_validator_result": {"outcome": "unsupported"},
        }
    )
    perspective = _finding(
        candidate_type="diagnostic_question",
        label="Throughline perspective question",
        extracted_claim="Which perspective should frame this throughline?",
    )
    subject_only = _finding(
        candidate_type="conflict_diagnostic",
        label="Archive topic conflict review",
        extracted_claim="The archive key is a source-of-conflict candidate",
        evidence=[
            {
                "source_excerpt": "The archive key is discussed",
                "source_locator": "raw_idea:L1:C1-28",
                "source_id": "idea-1",
                "source_sha256": "a" * 64,
            }
        ],
    )
    intent = _finding(
        candidate_type="storyform_context",
        label="Author intent context",
        extracted_claim="The author intended this as the thematic meaning",
    )
    missing = _finding(evidence=[])

    assert _classify(supported)["classification"] == "supported"
    assert _classify(quarantined)["classification"] == "unsupported"
    assert _classify(perspective)["classification"] == "ambiguous"
    assert _classify(subject_only)["classification"] == "subject_matter_only"
    assert _classify(intent)["classification"] == "author_intent_dependent"
    assert _classify(missing)["classification"] == "insufficient_evidence"


@pytest.mark.parametrize(
    ("finding", "classification", "reason_code"),
    [
        (
            _finding(
                candidate_type="storyform_context",
                label="Story Goal",
                extracted_claim="The archive key is the Story Goal",
            ),
            "unsupported",
            "storypoint_label_not_structurally_grounded",
        ),
        (
            _finding(
                candidate_type="throughline_context",
                label="Main Character Throughline",
                extracted_claim="Mara occupies the Main Character Throughline",
            ),
            "unsupported",
            "throughline_label_not_structurally_grounded",
        ),
        (
            _finding(
                candidate_type="diagnostic_question",
                label="Story-point context question",
                extracted_claim="Which Story Point is structurally supported?",
            ),
            "ambiguous",
            "storypoint_label_not_structurally_grounded",
        ),
    ],
)
def test_storypoint_throughline_and_perspective_overclaims_fail_closed(
    finding: dict[str, Any], classification: str, reason_code: str
) -> None:
    annotation = _classify(finding)
    assert annotation["classification"] == classification
    assert reason_code in annotation["reason_codes"]


def test_explicit_structural_grounding_can_support_without_tool_label_as_proof() -> None:
    storypoint = _finding(
        candidate_type="storyform_context",
        label="Story Goal",
        extracted_claim="The archive key is the Story Goal",
        support_metadata={"storypoint_grounded": True},
    )
    throughline = _finding(
        candidate_type="throughline_context",
        label="Main Character Throughline",
        extracted_claim="Mara occupies the Main Character Throughline",
        support_metadata={
            "throughline_grounded": True,
            "perspective_distinguished": True,
        },
    )

    assert _classify(storypoint)["classification"] == "supported"
    assert _classify(throughline)["classification"] == "supported"


def test_author_intent_requires_eligible_owner_controlled_approved_context() -> None:
    finding = _finding(
        candidate_type="storyform_context",
        label="Owner intent",
        extracted_claim="The owner intent identifies this context",
    )
    original = copy.deepcopy(finding)

    absent = _classify(finding)
    present = _classify(
        finding,
        approved_context={
            "approved": True,
            "owner_controlled": True,
            "context_id": "approved-context-1",
        },
    )

    assert absent["classification"] == "author_intent_dependent"
    assert present["classification"] == "supported"
    assert "eligible_approved_context_present" in present["reason_codes"]
    assert finding == original


@pytest.mark.parametrize(
    ("finding", "expected"),
    [
        (
            _finding(
                "subtxt_informed_rubric",
                candidate_type="diagnostic_question",
                label="Throughline perspective question",
                extracted_claim="Which perspective should frame this throughline?",
                uncertainty_label="requires_owner_interpretation",
            ),
            "ambiguous",
        ),
        (
            _finding(
                "subtxt_informed_rubric",
                candidate_type="diagnostic_question",
                label="Story-point context question",
                extracted_claim="Which Story Point is structurally supported?",
                uncertainty_label="requires_owner_interpretation",
            ),
            "ambiguous",
        ),
        (
            _finding(
                "subtxt_informed_rubric",
                candidate_type="conflict_diagnostic",
                label="Possible resistance mechanism",
                extracted_claim="A causal cue may support a mechanism hypothesis",
                evidence=[
                    {
                        "source_excerpt": "The deadline blocks Mara because resistance grows",
                        "source_locator": "raw_idea:L1:C1-49",
                        "source_id": "idea-1",
                        "source_sha256": "a" * 64,
                    }
                ],
                uncertainty_label="requires_owner_interpretation",
            ),
            "ambiguous",
        ),
        (
            _finding(
                "subtxt_informed_rubric",
                candidate_type="diagnostic_question",
                label="Subject versus conflict question",
                extracted_claim="Is the subject active conflict or only a topic?",
                uncertainty_label="requires_owner_interpretation",
            ),
            "subject_matter_only",
        ),
        (
            _finding(
                "subtxt_informed_rubric",
                candidate_type="diagnostic_question",
                label="Owner review question",
                extracted_claim="What additional context would clarify this reading?",
                uncertainty_label="requires_owner_interpretation",
            ),
            "ambiguous",
        ),
    ],
)
def test_owner_interpretation_is_not_author_intent(
    finding: dict[str, Any], expected: str
) -> None:
    annotation = _classify(finding)

    assert annotation["classification"] == expected
    assert annotation["classification"] != "author_intent_dependent"
    assert annotation["author_intent_or_approved_context"]["required"] is False


def test_source_mismatch_unverified_and_insufficient_states_remain_visible() -> None:
    mismatched = _finding()
    mismatched["evidence"][0]["source_sha256"] = "b" * 64
    unverified = _finding(
        support_metadata={"story_check_verification_state": "unverified"}
    )
    insufficient = _finding(
        candidate_type="evidence_note",
        label="Limited support",
        extracted_claim="The available evidence is insufficient evidence",
        uncertainty_label="insufficient_evidence",
    )

    mismatch_annotation = _classify(mismatched)
    unverified_annotation = _classify(unverified)
    insufficient_annotation = _classify(insufficient)
    assert mismatch_annotation["classification"] == "insufficient_evidence"
    assert mismatch_annotation["reason_codes"] == ["source_lineage_mismatch"]
    assert unverified_annotation["classification"] == "insufficient_evidence"
    assert unverified_annotation["verification_state"] == ["unverified"]
    assert insufficient_annotation["classification"] == "insufficient_evidence"
    assert insufficient_annotation["uncertainty_state"] == ["insufficient_evidence"]


def test_retained_story_check_diagnostics_are_assessed_without_candidate_creation() -> None:
    original_output = {
        "grounding": {
            "diagnostics": [
                {
                    "diagnostic_id": "unverified-throughline-question",
                    "classification": "question",
                    "message": "Which throughline is supported by the owner source?",
                    "evidence": [
                        {
                            "source_id": "idea-1",
                            "source_sha256": "a" * 64,
                            "start_byte": 0,
                            "end_byte": 9,
                            "excerpt": "Mara Vale",
                        }
                    ],
                    "verification_state": "unverified",
                    "validator_result": {
                        "outcome": "not_applicable",
                        "reason_codes": ["diagnostic_not_factual"],
                    },
                },
                {
                    "diagnostic_id": "quarantined-unsupported-fact",
                    "classification": "factual_warning",
                    "message": "The hearing occurs at midnight.",
                    "evidence": [],
                    "verification_state": "quarantined",
                    "validator_result": {
                        "outcome": "unsupported",
                        "reason_codes": ["evidence_absent"],
                    },
                },
            ]
        }
    }
    original = copy.deepcopy(original_output)

    annotations = sg.assess_retained_story_check_diagnostics(
        original_output,
        source_lineage={
            "run_id": "run-story-check",
            "source_identity": {
                "source_id": "idea-1",
                "content_hash": "a" * 64,
            },
        },
        original_output_reference="result-artifact",
    )

    assert original_output == original
    assert [item["classification"] for item in annotations] == [
        "insufficient_evidence",
        "unsupported",
    ]
    assert [item["reason_codes"] for item in annotations] == [
        ["unverified_grounding"],
        ["quarantined_or_rejected_grounding"],
    ]
    assert all(
        item["finding_kind"] == "retained_story_check_diagnostic"
        and item["candidate_transformation_performed"] is False
        and item["fusion_eligible"] is False
        and item["original_output_references"] == ["result-artifact"]
        and item["owner_decision"] == "not_selected"
        and item["canon_status"] == "not_selected"
        for item in annotations
    )
    assert sg.assess_retained_story_check_diagnostics(
        original_output,
        source_lineage={
            "run_id": "run-story-check",
            "source_identity": {
                "source_id": "idea-1",
                "content_hash": "a" * 64,
            },
        },
        original_output_reference="result-artifact",
    ) == annotations


def test_control_plane_retains_story_check_diagnostic_annotations_outside_fusion() -> None:
    original_output = {
        "grounding": {
            "diagnostics": [
                {
                    "diagnostic_id": "unverified-structure",
                    "classification": "structural_diagnostic",
                    "message": "The structure may require review.",
                    "evidence": [],
                    "verification_state": "unverified",
                    "validator_result": {
                        "outcome": "not_applicable",
                        "reason_codes": ["diagnostic_not_factual"],
                    },
                }
            ]
        }
    }
    result = {
        "findings": [],
        "operation_results": [
            {
                "operation_id": oao.OMI_STORY_CHECK_OPERATION_ID,
                "adapter": "story_check",
                "state": "empty",
                "explanation": "retained diagnostic only",
                "candidates": [],
                "original_output": original_output,
            }
        ],
    }
    snapshot = SimpleNamespace(
        identity=SimpleNamespace(
            to_dict=lambda: {
                "source_id": "idea-1",
                "content_hash": "a" * 64,
            }
        )
    )

    assessed = analysis_run_control._apply_semantic_guardrails(
        result,
        run_id="run-story-check",
        snapshot=snapshot,
    )

    assert assessed["findings"] == []
    assert assessed["guardrail_annotations"] == []
    assert assessed["fusion_summary"]["total_output_findings"] == 0
    assert len(assessed["retained_diagnostic_guardrail_annotations"]) == 1
    retained = assessed["retained_diagnostic_guardrail_annotations"][0]
    assert retained["classification"] == "insufficient_evidence"
    assert retained["reason_codes"] == ["unverified_grounding"]
    assert retained["fusion_eligible"] is False
    assert retained["candidate_transformation_performed"] is False
    assert result["operation_results"][0]["original_output"] == original_output


def test_input_finding_output_reference_and_nested_provenance_are_immutable() -> None:
    finding = _finding()
    guardrail_input = _input(finding)
    original_finding_bytes = json.dumps(finding, sort_keys=True).encode("utf-8")
    original_input = copy.deepcopy(guardrail_input)

    annotation = sg.evaluate_guardrail(guardrail_input)

    assert guardrail_input == original_input
    assert json.dumps(finding, sort_keys=True).encode("utf-8") == original_finding_bytes
    assert annotation["original_output_references"] == ["original-ollama_model"]
    assert annotation["owner_decision"] == "not_selected"
    assert annotation["canon_status"] == "not_selected"
    assert "classification" not in finding
    assert "reason_codes" not in finding


def test_multiple_annotations_preserve_evidence_and_provenance_and_are_parallel() -> None:
    first = _finding("ollama_model")
    second = _finding(
        "story_check",
        normalized_finding_id="omi-find-story-check-2",
        raw_finding_id="story-check-2",
        label="Throughline perspective question",
        candidate_type="diagnostic_question",
        extracted_claim="Which perspective should frame the throughline?",
    )
    originals = copy.deepcopy([first, second])

    annotations = sg.assess_findings([first, second])
    validated = sg.validate_guardrail_annotations([first, second], annotations)

    assert [first, second] == originals
    assert len(validated) == 2
    assert len({item["annotation_id"] for item in validated}) == 2
    assert [item["normalized_finding_id"] for item in validated] == [
        first["normalized_finding_id"],
        second["normalized_finding_id"],
    ]
    assert all(item["evidence_references"] for item in validated)


def test_reruns_are_byte_deterministic_and_context_changes_do_not_mutate_artifact() -> None:
    finding = _finding(
        label="Author intent",
        extracted_claim="The owner intent identifies this context",
    )
    artifact = {"message": {"content": json.dumps({"findings": [finding]})}}
    artifact_before = copy.deepcopy(artifact)

    first = _classify(finding)
    second = _classify(finding)
    changed = _classify(
        finding,
        approved_context={"approved": True, "owner_authored": True},
    )

    assert first == second
    assert first["classification"] == "author_intent_dependent"
    assert changed["classification"] == "supported"
    assert artifact == artifact_before


def test_booknlp_normalized_output_is_eligible_cross_adapter_evidence() -> None:
    booknlp = _finding(
        "booknlp",
        normalized_finding_id="omi-find-booknlp-evidence-1",
        raw_finding_id="booknlp-evidence-1",
        candidate_type="evidence_note",
        label="Archive key mention",
        extracted_claim="Archive key appears in normalized evidence",
    )
    ollama = _finding(
        "ollama_model",
        normalized_finding_id="omi-find-ollama-consumer-1",
        raw_finding_id="ollama-consumer-1",
    )

    annotation = sg.evaluate_guardrail(
        _input(ollama, evidence=[booknlp])
    )

    adapters = {
        item["source_adapter"]
        for item in annotation["normalized_evidence_references"]
    }
    assert adapters == {"booknlp"}
    assert annotation["classification"] == "supported"


def test_fusion_consumes_annotations_without_turning_agreement_into_truth() -> None:
    first = _finding(
        "ollama_model",
        candidate_type="storyform_context",
        label="Story Goal",
        extracted_claim="The archive key is the Story Goal",
    )
    second = _finding(
        "subtxt",
        normalized_finding_id="omi-find-subtxt-story-goal",
        raw_finding_id="subtxt-story-goal",
        candidate_type="storyform_context",
        label="Story Goal",
        extracted_claim="The archive key is the Story Goal",
    )
    originals = copy.deepcopy([first, second])
    prepared = oao.prepare_normalized_findings_for_guardrails([first, second])
    annotations = sg.assess_findings(
        prepared,
        normalized_evidence=[_producer_evidence()],
    )

    fused, summary = oao.fuse_normalized_findings(
        prepared, guardrail_annotations=annotations
    )

    assert [item["classification"] for item in annotations] == [
        "unsupported",
        "unsupported",
    ]
    assert summary["duplicate_group_count"] == 1
    assert summary["semantic_guardrails"]["classification_counts"]["unsupported"] == 2
    assert summary["semantic_guardrails"]["truth_selections"] == 0
    assert summary["semantic_guardrails"]["owner_approvals"] == 0
    assert [first, second] == originals
    assert [item["normalized_finding_id"] for item in annotations] == [
        item["normalized_finding_id"] for item in fused
    ]
    assert all(item["owner_decision"] == {"decision": "pending", "approved": False} for item in fused)
    assert all("guardrail" not in key for item in fused for key in item)


def _ollama_fixture() -> dict[str, Any]:
    return {
        "schema_version": oao.OMI_OLLAMA_SCHEMA_VERSION,
        "adapter": "ollama_model",
        "status": "succeeded",
        "explanation": "structured fixture output",
        "findings": [
            {
                "candidate_type": "throughline_context",
                "label": "Main Character Throughline",
                "extracted_claim": "Mara occupies the Main Character Throughline",
                "evidence": [
                    {
                        "source_excerpt": "Mara resists the archive deadline",
                        "source_locator": "raw_idea:L1:C1-34",
                    }
                ],
                "source_locator": "raw_idea:L1:C1-34",
                "raw_finding_id": "ollama-throughline-1",
                "support_label": "ollama model support only",
                "confidence": "medium support",
            }
        ],
    }


def test_orchestrator_orders_separate_guardrails_before_fusion() -> None:
    fixture = _ollama_fixture()
    original = copy.deepcopy(fixture)

    result = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        "Mara resists the archive deadline",
        source_idea_id="idea-1",
        persist_candidates=False,
        requested_adapters=["ollama_model"],
        adapter_fixture_outputs={"ollama_model": fixture},
    )

    assert fixture == original
    assert result["guardrail_contract"]["execution_order"] == (
        "post_normalization_pre_fusion"
    )
    assert len(result["guardrail_annotations"]) == len(result["findings"]) == 1
    annotation = result["guardrail_annotations"][0]
    finding = result["findings"][0]
    assert annotation["classification"] == "insufficient_evidence"
    assert annotation["reason_codes"] == ["eligible_normalized_evidence_missing"]
    assert annotation["normalized_finding_id"] == finding["normalized_finding_id"]
    assert annotation["immutable_finding_sha256"] == sg.immutable_finding_sha256(finding)
    assert finding["owner_decision"]["approved"] is False
    assert result["persisted_candidate_ids"] == []
    assert result["safety"]["no_memory_canon_mutation"] is True
    assert result["safety"]["no_apply_promotion"] is True
    assert result["safety"]["no_story_prose_generation"] is True


@pytest.mark.parametrize(
    "adapter",
    ["subtxt_informed_rubric", "dramatica_flow_informed_rubric"],
)
def test_app_owned_rubric_findings_flow_through_guardrails_in_process(
    adapter: str,
) -> None:
    result = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        (
            "Mara intends to recover the archive key, but the mentor blocks "
            "her because the hearing deadline creates resistance."
        ),
        persist_candidates=False,
        requested_adapters=[adapter],
    )

    assert result["findings"]
    assert len(result["guardrail_annotations"]) == len(result["findings"])
    assert all(
        item["classification"] == "insufficient_evidence"
        for item in result["guardrail_annotations"]
    )
    assert all(
        item["reason_codes"] == ["eligible_normalized_evidence_missing"]
        for item in result["guardrail_annotations"]
    )
    assert result["persisted_candidate_ids"] == []


def test_control_plane_applies_guardrails_and_fusion_exactly_once(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    projects = tmp_path / "projects"
    project = projects / "example"
    project.mkdir(parents=True)
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", projects)
    monkeypatch.setattr(project_manager, "REPO_ROOT", tmp_path)

    booknlp = _producer_evidence("booknlp")
    question = _finding(
        "ollama_model",
        candidate_type="diagnostic_question",
        label="Evidence review question",
        extracted_claim="Which interpretation is supported?",
        raw_finding_id="ollama-question-1",
        normalized_finding_id="omi-find-ollama-question-1",
    )
    for finding in (booknlp, question):
        finding["evidence"] = [
            {
                "source_excerpt": "Mara Vale",
                "source_locator": "raw_idea:exact",
            }
        ]
        finding["source_locator"] = "raw_idea:exact"
        finding["provenance"].pop("operation_id", None)
    booknlp["evidence"][0].update(
        {
            "byte_start": 0,
            "byte_end": len(b"Mara Vale"),
            "byte_offset_basis": "utf-8-bytes-zero-based-half-open",
        }
    )

    def runner(*args: Any, **kwargs: Any) -> dict[str, Any]:
        assert kwargs["requested_adapters"] == ["booknlp", "ollama_model"]
        return {
            "analysis_status": "succeeded",
            "explanation": "pre-guardrail fixture output",
            "source_idea_id": kwargs.get("source_idea_id"),
            "adapter_results": [
                {
                    "adapter": "booknlp",
                    "state": "succeeded",
                    "explanation": "producer completed",
                    "candidates": [booknlp],
                },
                {
                    "adapter": "ollama_model",
                    "state": "succeeded",
                    "explanation": "interpreter completed",
                    "candidates": [question],
                },
            ],
            "findings": [booknlp, question],
            "persisted_candidate_ids": [],
            "safety": {
                "no_prose": True,
                "no_memory_canon_mutation": True,
                "no_apply_promotion": True,
            },
        }

    assessment_calls: list[dict[str, Any]] = []
    fusion_calls: list[dict[str, Any]] = []
    real_assess = sg.assess_findings
    real_fuse = oao.fuse_normalized_findings

    def assess_spy(findings: Any, **kwargs: Any) -> list[dict[str, Any]]:
        assessment_calls.append(
            {
                "finding_count": len(findings),
                "uncertainty_before_fusion": [
                    item.get("uncertainty_label") for item in findings
                ],
                "normalized_evidence_adapters": [
                    item["source_adapter"]
                    for item in kwargs["normalized_evidence"]
                ],
            }
        )
        return real_assess(findings, **kwargs)

    def fuse_spy(findings: Any, **kwargs: Any):
        fusion_calls.append(
            {
                "finding_count": len(findings),
                "annotation_count": len(kwargs["guardrail_annotations"]),
            }
        )
        return real_fuse(findings, **kwargs)

    monkeypatch.setattr(sg, "assess_findings", assess_spy)
    monkeypatch.setattr(oao, "fuse_normalized_findings", fuse_spy)

    run = analysis_run_control.submit_analysis_run(
        "example",
        raw_idea="Mara Vale",
        source_idea_id="idea-1",
        requested_adapters=["booknlp", "ollama_model"],
        runner=runner,
        created_at="2026-09-25T22:00:00Z",
    )
    published = analysis_run_control.get_analysis_run_result(
        "example", run["run_id"]
    )["result"]

    assert assessment_calls == [
        {
            "finding_count": 2,
            "uncertainty_before_fusion": [None, None],
            "normalized_evidence_adapters": ["booknlp"],
        }
    ]
    assert fusion_calls == [{"finding_count": 2, "annotation_count": 2}]
    assert len(published["guardrail_annotations"]) == len(published["findings"]) == 2
    question_index = next(
        index
        for index, finding in enumerate(published["findings"])
        if finding["source_adapter"] == "ollama_model"
    )
    question_annotation = published["guardrail_annotations"][question_index]
    assert question_annotation["classification"] == "ambiguous"
    assert question_annotation["reason_codes"] == [
        "diagnostic_question_does_not_select_an_interpretation"
    ]
    assert question_annotation["normalized_evidence_dependency"][
        "eligible_producer_adapters"
    ] == ["booknlp"]
    assert question_annotation["source_lineage"]["run_id"] == run["run_id"]
    assert question_annotation["source_lineage"]["source_hash"] == __import__(
        "hashlib"
    ).sha256(b"Mara Vale").hexdigest()
    assert published["findings"][question_index]["uncertainty_label"] == (
        "diagnostic_question_support"
    )

    empty_run = analysis_run_control.submit_analysis_run(
        "example",
        raw_idea="No contributor output",
        source_idea_id="idea-empty",
        requested_adapters=["ollama_model"],
        runner=lambda *args, **kwargs: {
            "analysis_status": "fail_closed",
            "explanation": "empty contributor",
            "source_idea_id": kwargs.get("source_idea_id"),
            "adapter_results": [
                {
                    "adapter": "ollama_model",
                    "state": "failed_closed",
                    "explanation": "no valid findings",
                    "candidates": [],
                }
            ],
            "findings": [],
            "persisted_candidate_ids": [],
            "safety": {
                "no_prose": True,
                "no_memory_canon_mutation": True,
                "no_apply_promotion": True,
            },
        },
        created_at="2026-09-25T22:00:01Z",
    )
    empty = analysis_run_control.get_analysis_run_result(
        "example", empty_run["run_id"]
    )["result"]
    assert assessment_calls[-1]["finding_count"] == 0
    assert fusion_calls[-1] == {"finding_count": 0, "annotation_count": 0}
    assert empty["findings"] == []
    assert empty["guardrail_annotations"] == []
    assert empty["retained_diagnostic_guardrail_annotations"] == []
