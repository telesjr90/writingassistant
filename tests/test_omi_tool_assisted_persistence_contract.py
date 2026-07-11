"""PHASE8-IMPL-023-T011 candidate-only fused AI/tool persistence tests.

These tests use fixture/mock adapter output only. They do not call live
Ollama, Story Check, BookNLP, spaCy, NCP, Subtxt, dramatica-flow, external
services, or models. They do not mutate Memory/Canon, create promotion
records, run apply-promotion, or generate story prose.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from backend import omi_analysis_orchestrator as oao
from backend import project_manager


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


def _ollama_envelope(findings: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": oao.OMI_OLLAMA_SCHEMA_VERSION,
        "adapter": "ollama_model",
        "status": "succeeded",
        "explanation": "fixture-only structured extraction",
        "findings": findings,
    }


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


def _tool_assisted_finding(source_adapter: str, suffix: str) -> dict[str, Any]:
    support_label = f"{source_adapter} support only"
    return {
        "candidate_type": "structural_diagnostic",
        "label": f"Diagnostic {suffix}",
        "extracted_claim": f"Diagnostic {suffix} is review material",
        "evidence": [
            {
                "source_excerpt": f"Evidence for diagnostic {suffix}",
                "source_locator": f"raw_idea:L1:C{suffix}-1",
            }
        ],
        "source_locator": f"raw_idea:L1:C{suffix}-1",
        "source_adapter": source_adapter,
        "provenance": {
            "adapter": source_adapter,
            "tool_source": source_adapter,
            "support": support_label,
        },
        "support_label": support_label,
        "support_metadata": {
            "basis": f"bounded {source_adapter} diagnostic support",
            "support_only": True,
        },
        "confidence": "medium support",
        "owner_decision": {"approved": False, "decision": "pending"},
        "review_status": "candidate_review_pending",
        "raw_finding_id": f"{source_adapter}::raw::{suffix}",
        "candidate_fingerprint": f"omi-cand-{source_adapter}-{suffix}",
        "evidence_fingerprint": f"omi-evid-{source_adapter}-{suffix}",
        "normalized_finding_id": f"omi-find-{source_adapter}-{suffix}",
        "duplicate_of": [],
        "related_finding_ids": [],
        "conflict_group_id": None,
        "uncertainty_label": None,
    }


def _create_temporary_omi_idea(tmp_path, monkeypatch) -> dict[str, Any]:
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)
    return project_manager.create_omi_idea("demo", RAW_IDEA)


def _fixtures_with_duplicate_and_conflict() -> dict[str, Any]:
    return {
        "ollama_model": _ollama_envelope(
            [
                _ollama_finding(),
                _ollama_finding(
                    candidate_type="object",
                    label="Archive Key",
                    extracted_claim="Archive key is held by Mara for review",
                    raw_finding_id="ollama-key-1",
                    evidence=[
                        {
                            "source_excerpt": "archive key support",
                            "source_locator": "raw_idea:L1:C33-52",
                        }
                    ],
                    source_locator="raw_idea:L1:C33-52",
                ),
            ]
        ),
        "booknlp": _booknlp_envelope(
            [
                _booknlp_finding(),
                _booknlp_finding(
                    raw_finding_id="booknlp-key-1",
                    finding_type="object",
                    label="archive key",
                    extracted_claim="archive key is held by mentor for review",
                    evidence=[
                        {
                            "source_excerpt": "archive key support",
                            "source_locator": "raw_idea:L1:C33-52",
                        }
                    ],
                    source_locator="raw_idea:L1:C33-52",
                ),
            ]
        ),
    }


def _run_with_fixtures(
    *,
    persist_candidates: bool,
    source_idea_id: str | None,
    fixtures: dict[str, Any] | None = None,
    raw_idea: str = RAW_IDEA,
) -> dict[str, Any]:
    return oao.analyze_omi_raw_idea_with_tools(
        "demo",
        raw_idea,
        source_idea_id=source_idea_id,
        persist_candidates=persist_candidates,
        requested_adapters=["ollama_model", "booknlp"],
        adapter_fixture_outputs=fixtures or _fixtures_with_duplicate_and_conflict(),
    )


def test_persist_false_returns_fused_findings_without_writes(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)
    idea = project_manager.create_omi_idea("demo", RAW_IDEA)

    result = _run_with_fixtures(
        persist_candidates=False,
        source_idea_id=idea["idea_id"],
    )

    assert result["analysis_status"] == "succeeded"
    assert len(result["findings"]) == 4
    assert result["persisted_candidate_ids"] == []
    assert result["persistence_status"] == "not_requested"
    assert project_manager.get_omi_summary("demo")["index"]["candidate_ids"] == []


def test_persist_true_writes_pending_candidate_only_review_records(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)
    idea = project_manager.create_omi_idea("demo", RAW_IDEA)

    result = _run_with_fixtures(
        persist_candidates=True,
        source_idea_id=idea["idea_id"],
    )

    assert result["analysis_status"] == "succeeded"
    assert result["persistence_status"] == "persisted"
    assert len(result["persisted_candidate_ids"]) == 4
    assert len(result["new_candidate_ids"]) == 4
    assert result["reused_candidate_ids"] == []

    summary = project_manager.get_omi_summary("demo")
    assert summary["index"]["candidate_ids"] == sorted(result["persisted_candidate_ids"])
    assert summary["promotions"] == []

    duplicate_records = []
    conflict_records = []
    for record in summary["candidates"]:
        assert record["status"] == "candidate"
        assert record["owner_decision"]["decision"] == "pending"
        assert record["owner_decision"]["approved"] is False
        assert record["promotion_status"]["eligible"] is False
        assert record["idea_id"] == idea["idea_id"]
        assert record["evidence"]
        assert record["provenance"]["source_type"] == project_manager.OMI_TOOL_ASSISTED_CANDIDATE_SOURCE
        assert record["provenance"]["adapter"] == record["provenance"]["tool_source"]

        content = record["candidate_content"]
        assert content["source"] == project_manager.OMI_TOOL_ASSISTED_CANDIDATE_SOURCE
        assert content["candidate_first"] is True
        assert content["review_material_only"] is True
        assert content["queue_presence_is_not_approval"] is True
        assert content["support_only"] is True
        assert content["candidate_type"]
        assert content["label"]
        assert content["name"] == content["label"]
        assert content["extracted_claim"]
        assert content["diagnostic_claim"] == content["extracted_claim"]
        assert content["evidence"]
        assert content["source_locator"]
        assert content["provenance"]
        assert content["source_adapter"] == content["tool_source"]
        assert "support" in content["support_label"].lower()
        assert content["owner_decision"]["decision"] == "pending"
        assert content["review_status"] == "candidate_review_pending"
        assert content["candidate_fingerprint"].startswith("omi-cand-")
        assert content["evidence_fingerprint"].startswith("omi-evid-")
        assert content["normalized_finding_id"].startswith("omi-find-")
        assert content["tool_assisted_candidate_key"].startswith("omi-tool-candidate-")
        assert content["duplicate_metadata"]["related_finding_ids"] is not None

        forbidden_status_values = {"canon", "truth", "approved", "promoted"}
        assert record["status"] not in forbidden_status_values
        assert content["review_status"] not in forbidden_status_values
        assert content["owner_decision"]["decision"] == "pending"
        assert "truth" not in content["support_label"].lower()
        assert "canon" not in content["support_label"].lower()
        assert "approved" not in content["support_label"].lower()
        assert "promoted" not in content["support_label"].lower()

        if content["candidate_type"] == "character":
            duplicate_records.append(record)
        if content["candidate_type"] == "object":
            conflict_records.append(record)

    assert len(duplicate_records) == 2
    assert any(
        record["candidate_content"]["duplicate_metadata"]["duplicate_of"]
        for record in duplicate_records
    )
    assert all(
        record["candidate_content"]["duplicate_metadata"]["related_finding_ids"]
        for record in duplicate_records
    )
    assert len(conflict_records) == 2
    assert {
        record["candidate_content"]["uncertainty_label"]
        for record in conflict_records
    } == {"conflict_support"}
    assert all(
        record["candidate_content"]["conflict_group_id"].startswith("omi-conflict-")
        for record in conflict_records
    )
    assert all(record["evidence"][0]["source_excerpt"] for record in summary["candidates"])


def test_missing_source_context_returns_non_persistence_status_without_writes(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)

    missing_source = _run_with_fixtures(
        persist_candidates=True,
        source_idea_id=None,
    )
    assert missing_source["analysis_status"] == "succeeded"
    assert missing_source["persisted_candidate_ids"] == []
    assert missing_source["persistence_status"] == "source_idea_required"

    unknown_source = _run_with_fixtures(
        persist_candidates=True,
        source_idea_id="idea_missing",
    )
    assert unknown_source["analysis_status"] == "succeeded"
    assert unknown_source["persisted_candidate_ids"] == []
    assert unknown_source["persistence_status"] == "source_idea_not_found"
    assert project_manager.get_omi_summary("demo")["index"]["candidate_ids"] == []


def test_source_snapshot_mismatch_and_unsafe_findings_write_nothing(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)
    idea = project_manager.create_omi_idea("demo", RAW_IDEA)

    mismatch = _run_with_fixtures(
        persist_candidates=True,
        source_idea_id=idea["idea_id"],
        raw_idea="Owner analysis note with different source text.",
    )
    assert mismatch["persisted_candidate_ids"] == []
    assert mismatch["persistence_status"] == "source_idea_mismatch"

    unsafe = _run_with_fixtures(
        persist_candidates=True,
        source_idea_id=idea["idea_id"],
        fixtures={
            "ollama_model": _ollama_envelope(
                [
                    _ollama_finding(
                        raw_finding_id="unsafe-1",
                        extracted_claim="Rewrite: a polished chapter scene",
                    )
                ]
            ),
            "booknlp": _booknlp_envelope([]),
        },
    )
    assert unsafe["analysis_status"] == "fail_closed"
    assert unsafe["persisted_candidate_ids"] == []
    assert unsafe["persistence_status"] == "no_candidates_persisted"
    assert project_manager.get_omi_summary("demo")["index"]["candidate_ids"] == []


def test_rerun_same_fused_findings_reuses_candidates_without_truth_mutation(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)
    project_dir = tmp_path / "demo"
    scenes_dir = project_dir / "scenes"
    scenes_dir.mkdir(parents=True)
    truth_files = {
        project_dir / "bible.json": '{"characters": []}\n',
        project_dir / "storyform.json": '{"schema_version": "ncp-0.1"}\n',
        project_dir / "owner_memory.json": '{"notes": []}\n',
        scenes_dir / "scene_001.md": "Owner-authored fixture text.",
    }
    for path, content in truth_files.items():
        path.write_text(content, encoding="utf-8")
    idea = project_manager.create_omi_idea("demo", RAW_IDEA)

    first = _run_with_fixtures(
        persist_candidates=True,
        source_idea_id=idea["idea_id"],
    )
    second = _run_with_fixtures(
        persist_candidates=True,
        source_idea_id=idea["idea_id"],
    )

    assert first["persistence_status"] == "persisted"
    assert second["persistence_status"] == "already_persisted"
    assert second["persisted_candidate_ids"] == first["persisted_candidate_ids"]
    assert second["new_candidate_ids"] == []
    assert second["reused_candidate_ids"] == first["persisted_candidate_ids"]

    summary = project_manager.get_omi_summary("demo")
    assert len(summary["candidates"]) == len(first["persisted_candidate_ids"])
    assert summary["promotions"] == []
    assert not hasattr(project_manager, "apply_omi_promotion")
    for path, content in truth_files.items():
        assert path.read_text(encoding="utf-8") == content


def test_persistence_allowlist_includes_current_app_owned_adapter_identities() -> None:
    assert "subtxt_informed_rubric" in project_manager.OMI_TOOL_ASSISTED_ADAPTER_IDENTITIES
    assert (
        "dramatica_flow_informed_rubric"
        in project_manager.OMI_TOOL_ASSISTED_ADAPTER_IDENTITIES
    )


@pytest.mark.parametrize(
    "source_adapter",
    ["subtxt_informed_rubric", "dramatica_flow_informed_rubric"],
)
def test_app_owned_findings_persist_with_candidate_only_metadata(
    source_adapter: str, tmp_path, monkeypatch
) -> None:
    idea = _create_temporary_omi_idea(tmp_path, monkeypatch)
    finding = _tool_assisted_finding(source_adapter, "one")

    result = project_manager.persist_omi_tool_assisted_findings_as_candidates(
        "demo",
        raw_idea=RAW_IDEA,
        source_idea_id=idea["idea_id"],
        findings=[finding],
    )

    assert result["persistence_status"] == "persisted"
    assert len(result["new_candidate_ids"]) == 1
    assert result["persisted_candidate_ids"] == result["new_candidate_ids"]

    summary = project_manager.get_omi_summary("demo")
    assert len(summary["candidates"]) == 1
    record = summary["candidates"][0]
    content = record["candidate_content"]
    assert record["status"] == "candidate"
    assert record["evidence"] == finding["evidence"]
    assert record["provenance"]["adapter"] == source_adapter
    assert record["provenance"]["tool_source"] == source_adapter
    assert record["owner_decision"]["approved"] is False
    assert record["owner_decision"]["decision"] == "pending"
    assert record["promotion_status"]["eligible"] is False
    assert content["source_adapter"] == source_adapter
    assert content["tool_source"] == source_adapter
    assert content["provenance"]["adapter"] == source_adapter
    assert content["provenance"]["tool_source"] == source_adapter
    assert content["evidence"] == finding["evidence"]
    assert content["support_label"] == finding["support_label"]
    assert content["support_metadata"] == finding["support_metadata"]
    assert content["candidate_fingerprint"] == finding["candidate_fingerprint"]
    assert content["evidence_fingerprint"] == finding["evidence_fingerprint"]
    assert content["normalized_finding_id"] == finding["normalized_finding_id"]
    assert content["owner_decision"]["approved"] is False
    assert content["owner_decision"]["decision"] == "pending"
    assert content["review_status"] == "candidate_review_pending"


def test_mixed_app_owned_findings_persist_once_and_replay_both_ids(
    tmp_path, monkeypatch
) -> None:
    idea = _create_temporary_omi_idea(tmp_path, monkeypatch)
    findings = [
        _tool_assisted_finding("subtxt_informed_rubric", "mixed-subtxt"),
        _tool_assisted_finding("dramatica_flow_informed_rubric", "mixed-dramatica"),
    ]

    first = project_manager.persist_omi_tool_assisted_findings_as_candidates(
        "demo",
        raw_idea=RAW_IDEA,
        source_idea_id=idea["idea_id"],
        findings=findings,
    )
    second = project_manager.persist_omi_tool_assisted_findings_as_candidates(
        "demo",
        raw_idea=RAW_IDEA,
        source_idea_id=idea["idea_id"],
        findings=findings,
    )

    assert first["persistence_status"] == "persisted"
    assert len(first["persisted_candidate_ids"]) == 2
    assert len(first["new_candidate_ids"]) == 2
    assert first["reused_candidate_ids"] == []
    assert len(project_manager.get_omi_summary("demo")["candidates"]) == 2
    assert second["persistence_status"] == "already_persisted"
    assert second["persisted_candidate_ids"] == first["persisted_candidate_ids"]
    assert second["new_candidate_ids"] == []
    assert second["reused_candidate_ids"] == first["persisted_candidate_ids"]


def test_unknown_app_owned_identity_fails_closed_without_candidate_write(
    tmp_path, monkeypatch
) -> None:
    idea = _create_temporary_omi_idea(tmp_path, monkeypatch)
    finding = _tool_assisted_finding("unknown_adapter", "unknown")

    result = project_manager.persist_omi_tool_assisted_findings_as_candidates(
        "demo",
        raw_idea=RAW_IDEA,
        source_idea_id=idea["idea_id"],
        findings=[finding],
    )

    assert result["persistence_status"] == "invalid_finding_failed_closed"
    assert result["persisted_candidate_ids"] == []
    assert result["new_candidate_ids"] == []
    assert result["reused_candidate_ids"] == []
    assert "Unknown OMI tool-assisted source_adapter: unknown_adapter" in result[
        "persistence_explanation"
    ]
    assert project_manager.get_omi_summary("demo")["index"]["candidate_ids"] == []
