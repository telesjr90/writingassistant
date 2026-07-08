"""PHASE8-IMPL-023-T010 fusion/dedupe/conflict/uncertainty contract tests.

These tests use fixture/mock output only. They do not call live Ollama,
Story Check, BookNLP, spaCy, NCP, Subtxt, dramatica-flow, external services,
or models. They do not persist AI/tool findings, mutate Memory/Canon, create
promotion records, run apply-promotion, or generate story prose.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from backend import omi_analysis_orchestrator as oao


RAW_IDEA = (
    "Owner analysis note: Mara Vale, archive key support, hearing deadline, "
    "and unresolved mentor relationship review material."
)


def _ollama_finding(**overrides: Any) -> dict[str, Any]:
    finding: dict[str, Any] = {
        "candidate_type": "character",
        "label": "Mara Vale",
        "extracted_claim": "Mara Vale appears as a character candidate",
        "evidence": [
            {
                "source_excerpt": "Mara Vale is named in the owner note",
                "source_locator": "raw_idea:L1:C21-30",
            }
        ],
        "source_locator": "raw_idea:L1:C21-30",
        "raw_finding_id": "ollama-mara-1",
        "support_label": "ollama model support strength only",
        "confidence": "medium support",
    }
    finding.update(overrides)
    return finding


def _ollama_envelope(findings: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": oao.OMI_OLLAMA_SCHEMA_VERSION,
        "adapter": "ollama_model",
        "status": "succeeded",
        "explanation": "fixture-only structured extraction",
        "findings": findings,
    }


def _booknlp_finding(**overrides: Any) -> dict[str, Any]:
    finding: dict[str, Any] = {
        "raw_finding_id": "booknlp-mara-1",
        "finding_type": "person_entity",
        "label": "mara vale",
        "extracted_claim": "mara vale appears as a person entity candidate",
        "evidence": [
            {
                "source_excerpt": "Mara Vale is named in the owner note",
                "source_locator": "raw_idea:L1:C21-30",
            }
        ],
        "source_locator": "raw_idea:L1:C21-30",
        "confidence": "medium support",
    }
    finding.update(overrides)
    return finding


def _booknlp_envelope(findings: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": oao.OMI_BOOKNLP_SCHEMA_VERSION,
        "adapter": "booknlp",
        "status": "succeeded",
        "explanation": "fixture-only BookNLP local NLP extraction",
        "provenance": {
            "tool_source": "booknlp",
            "adapter": "booknlp",
            "support": "BookNLP fixture support only",
        },
        "findings": findings,
    }


def _story_check_finding(**overrides: Any) -> dict[str, Any]:
    finding: dict[str, Any] = {
        "raw_finding_id": "story-check-question-1",
        "finding_type": "diagnostic_question",
        "label": "Mentor relationship review question",
        "question": (
            "Which throughline is supported by the unresolved mentor "
            "relationship?"
        ),
        "evidence": [
            {
                "source_excerpt": "unresolved mentor relationship review material",
                "source_locator": "raw_idea:L1:C84-129",
            }
        ],
        "source_locator": "raw_idea:L1:C84-129",
        "support_label": "Story Check diagnostic support only",
        "confidence": "medium support",
    }
    finding.update(overrides)
    return finding


def _story_check_envelope(findings: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": oao.OMI_STORY_CHECK_SCHEMA_VERSION,
        "adapter": "story_check",
        "status": "succeeded",
        "explanation": "fixture-only Story Check diagnostic handoff",
        "provenance": {
            "tool_source": "story_check",
            "adapter": "story_check",
            "support": "Story Check diagnostic support only",
        },
        "findings": findings,
    }


def _subtxt_finding(**overrides: Any) -> dict[str, Any]:
    finding: dict[str, Any] = {
        "raw_finding_id": "subtxt-insufficient-1",
        "finding_type": "insufficient_evidence_diagnostic",
        "label": "Mentor relationship insufficient evidence",
        "diagnostic_claim": (
            "The unresolved mentor relationship has insufficient evidence"
        ),
        "evidence": [
            {
                "source_excerpt": "unresolved mentor relationship review material",
                "source_locator": "raw_idea:L1:C84-129",
            }
        ],
        "source_locator": "raw_idea:L1:C84-129",
        "support_label": "low support",
        "confidence": "low support",
    }
    finding.update(overrides)
    return finding


def _subtxt_envelope(findings: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": oao.OMI_CONTEXT_SCHEMA_VERSION_BY_ADAPTER["subtxt"],
        "adapter": "subtxt",
        "status": "succeeded",
        "explanation": "fixture-only Subtxt diagnostic handoff",
        "provenance": {
            "tool_source": "subtxt",
            "adapter": "subtxt",
            "support": "Subtxt diagnostic support only",
        },
        "findings": findings,
    }


def _run_with_fixtures(
    requested_adapters: list[str],
    adapter_fixture_outputs: dict[str, Any],
    **kwargs: Any,
) -> dict[str, Any]:
    params = {
        "persist_candidates": False,
        "requested_adapters": requested_adapters,
        "adapter_fixture_outputs": adapter_fixture_outputs,
    }
    params.update(kwargs)
    return oao.analyze_omi_raw_idea_with_tools("demo", RAW_IDEA, **params)


def _find_by_adapter(result: dict[str, Any], adapter: str) -> dict[str, Any]:
    matches = [
        finding for finding in result["findings"]
        if finding["source_adapter"] == adapter
    ]
    assert len(matches) == 1
    return matches[0]


def test_equivalent_adapter_findings_are_fingerprinted_linked_and_preserved() -> None:
    fixtures = {
        "ollama_model": _ollama_envelope([_ollama_finding()]),
        "booknlp": _booknlp_envelope([_booknlp_finding()]),
    }

    result = _run_with_fixtures(["ollama_model", "booknlp"], fixtures)

    assert result["analysis_status"] == "succeeded"
    assert result["persisted_candidate_ids"] == []
    assert len(result["findings"]) == 2
    summary = result["fusion_summary"]
    assert summary["total_input_findings"] == 2
    assert summary["total_output_findings"] == 2
    assert summary["duplicate_group_count"] == 1
    assert summary["duplicate_finding_count"] == 1
    assert summary["conflict_group_count"] == 0
    assert summary["adapters_contributing_findings"] == [
        "booknlp",
        "ollama_model",
    ]

    ollama = _find_by_adapter(result, "ollama_model")
    booknlp = _find_by_adapter(result, "booknlp")
    assert ollama["candidate_fingerprint"] == booknlp["candidate_fingerprint"]
    assert ollama["evidence_fingerprint"] == booknlp["evidence_fingerprint"]
    assert booknlp["normalized_finding_id"] in ollama["related_finding_ids"]
    assert ollama["normalized_finding_id"] in booknlp["related_finding_ids"]
    assert (
        bool(ollama["duplicate_of"])
        != bool(booknlp["duplicate_of"])
    )

    assert ollama["source_adapter"] == "ollama_model"
    assert booknlp["source_adapter"] == "booknlp"
    assert ollama["provenance"]["adapter"] == "ollama_model"
    assert booknlp["provenance"]["adapter"] == "booknlp"
    assert ollama["evidence"][0]["source_excerpt"]
    assert booknlp["evidence"][0]["source_excerpt"]
    assert ollama["source_locator"] == "raw_idea:L1:C21-30"
    assert booknlp["source_locator"] == "raw_idea:L1:C21-30"
    assert ollama["owner_decision"]["decision"] == "pending"
    assert booknlp["owner_decision"]["decision"] == "pending"
    assert ollama["review_status"] == "candidate_review_pending"
    assert booknlp["review_status"] == "candidate_review_pending"
    assert ollama["confidence"] == "medium support"
    assert booknlp["confidence"] == "medium support"


def test_adapter_order_does_not_change_fingerprints_or_duplicate_grouping() -> None:
    fixtures = {
        "ollama_model": _ollama_envelope([_ollama_finding()]),
        "booknlp": _booknlp_envelope([_booknlp_finding()]),
    }

    forward = _run_with_fixtures(["ollama_model", "booknlp"], fixtures)
    reversed_result = _run_with_fixtures(["booknlp", "ollama_model"], fixtures)

    for adapter in ("ollama_model", "booknlp"):
        first = _find_by_adapter(forward, adapter)
        second = _find_by_adapter(reversed_result, adapter)
        assert first["candidate_fingerprint"] == second["candidate_fingerprint"]
        assert first["evidence_fingerprint"] == second["evidence_fingerprint"]
        assert first["normalized_finding_id"] == second["normalized_finding_id"]
        assert first["duplicate_of"] == second["duplicate_of"]
        assert first["related_finding_ids"] == second["related_finding_ids"]

    assert forward["fusion_summary"] == reversed_result["fusion_summary"]


def test_matching_type_label_with_different_claims_creates_conflict_group() -> None:
    fixtures = {
        "ollama_model": _ollama_envelope(
            [
                _ollama_finding(
                    candidate_type="object",
                    label="Archive Key",
                    extracted_claim="Archive key is held by Mara for review",
                    raw_finding_id="ollama-key-1",
                )
            ]
        ),
        "booknlp": _booknlp_envelope(
            [
                _booknlp_finding(
                    raw_finding_id="booknlp-key-1",
                    finding_type="object",
                    label="archive key",
                    extracted_claim="archive key is held by mentor for review",
                )
            ]
        ),
    }

    result = _run_with_fixtures(["ollama_model", "booknlp"], fixtures)

    assert result["analysis_status"] == "succeeded"
    assert result["fusion_summary"]["conflict_group_count"] == 1
    assert result["fusion_summary"]["duplicate_group_count"] == 0
    conflict_ids = {
        finding["conflict_group_id"] for finding in result["findings"]
    }
    assert len(conflict_ids) == 1
    conflict_id = conflict_ids.pop()
    assert conflict_id.startswith("omi-conflict-")
    for finding in result["findings"]:
        assert finding["uncertainty_label"] == "conflict_support"
        assert finding["owner_decision"]["decision"] == "pending"
        assert finding["owner_decision"]["approved"] is False
        assert finding["review_status"] == "candidate_review_pending"
        assert finding["duplicate_of"] == []
        assert "truth" not in finding["support_label"].lower()
        assert "canon" not in finding["support_label"].lower()
        assert "approved" not in finding["support_label"].lower()
        assert "promoted" not in finding["support_label"].lower()


def test_questions_and_low_support_receive_uncertainty_labels() -> None:
    result = _run_with_fixtures(
        ["story_check", "subtxt"],
        {
            "story_check": _story_check_envelope([_story_check_finding()]),
            "subtxt": _subtxt_envelope([_subtxt_finding()]),
        },
    )

    assert result["analysis_status"] == "succeeded"
    question = _find_by_adapter(result, "story_check")
    low_support = _find_by_adapter(result, "subtxt")
    assert question["candidate_type"] == "diagnostic_question"
    assert question["uncertainty_label"] == "diagnostic_question_support"
    assert low_support["candidate_type"] == "ambiguity"
    assert low_support["uncertainty_label"] == "insufficient_evidence_support"
    assert result["fusion_summary"]["uncertain_finding_count"] == 2


def test_persist_candidates_true_does_not_persist_tool_findings_or_mutate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import backend.project_manager as project_manager

    calls: list[dict[str, Any]] = []

    def spy_extract(*args: Any, **kwargs: Any) -> dict[str, Any]:
        calls.append({"args": args, "kwargs": kwargs})
        return {"candidates": [], "persisted_candidate_ids": []}

    monkeypatch.setattr(
        project_manager,
        "extract_omi_candidates_from_raw_idea",
        spy_extract,
    )

    result = _run_with_fixtures(
        ["ollama_model", "booknlp"],
        {
            "ollama_model": _ollama_envelope([_ollama_finding()]),
            "booknlp": _booknlp_envelope([_booknlp_finding()]),
        },
        persist_candidates=True,
        source_idea_id="idea_123",
    )

    assert result["analysis_status"] == "succeeded"
    assert result["persisted_candidate_ids"] == []
    assert calls == []
    assert result["safety"]["no_memory_canon_mutation"] is True
    assert result["safety"]["no_apply_promotion"] is True
    assert result["safety"]["no_story_prose_generation"] is True
    for finding in result["findings"]:
        forbidden_keys = {
            "promotion_record",
            "apply_promotion",
            "canon_mutation",
            "memory_mutation",
        }
        assert not forbidden_keys.intersection(finding)
