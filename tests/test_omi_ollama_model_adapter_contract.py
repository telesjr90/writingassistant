"""PHASE8-IMPL-023-T006 Ollama/model fixture adapter contract tests.

These tests use fixture/mock output only. They do not call Ollama, import an
Ollama client, make HTTP requests, run Story Check, run BookNLP/spaCy, run
NCP/Subtxt/dramatica-flow, mutate Memory/Canon, run apply-promotion, or
generate story prose.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from backend import omi_analysis_orchestrator as oao


RAW_IDEA = (
    "Owner note: Test Character Alpha is a character candidate tied to "
    "the library clue."
)


def _valid_finding(**overrides: Any) -> dict[str, Any]:
    finding: dict[str, Any] = {
        "candidate_type": "character",
        "label": "Test Character Alpha",
        "extracted_claim": (
            "Test Character Alpha is identified as a character candidate"
        ),
        "evidence": [
            {
                "source_excerpt": (
                    "Owner note names Test Character Alpha as the library "
                    "investigator."
                ),
                "source_locator": "raw_idea:L1:C0-78",
            }
        ],
        "source_locator": "raw_idea:L1:C0-78",
        "raw_finding_id": "ollama-fixture-finding-1",
        "support_label": "ollama model support strength only",
        "confidence": "medium support",
    }
    finding.update(overrides)
    return finding


def _valid_envelope(**overrides: Any) -> dict[str, Any]:
    envelope: dict[str, Any] = {
        "schema_version": oao.OMI_OLLAMA_SCHEMA_VERSION,
        "adapter": "ollama_model",
        "status": "succeeded",
        "explanation": "fixture-only structured extraction",
        "diagnostics": ["fixture validated without live model runtime"],
        "findings": [_valid_finding()],
    }
    envelope.update(overrides)
    return envelope


def _run_with_fixture(fixture: Any, **kwargs: Any) -> dict[str, Any]:
    params = {
        "persist_candidates": False,
        "requested_adapters": ["ollama_model"],
        "adapter_fixture_outputs": {"ollama_model": fixture},
    }
    params.update(kwargs)
    return oao.analyze_omi_raw_idea_with_tools("demo", RAW_IDEA, **params)


def _assert_ollama_failed_closed(result: dict[str, Any]) -> dict[str, Any]:
    assert result["analysis_status"] == "fail_closed"
    assert result["findings"] == []
    assert result["persisted_candidate_ids"] == []
    adapter_results = [
        env for env in result["adapter_results"]
        if env["adapter"] == "ollama_model"
    ]
    assert len(adapter_results) == 1
    env = adapter_results[0]
    assert env["state"] in {"failed_closed", "unavailable", "error"}
    assert env["candidates"] == []
    assert env["explanation"]
    return env


def _assert_valid_ollama_result(result: dict[str, Any]) -> dict[str, Any]:
    assert result["analysis_status"] == "succeeded"
    assert result["persisted_candidate_ids"] == []
    assert len(result["findings"]) == 1

    adapter_env = result["adapter_results"][0]
    assert adapter_env["adapter"] == "ollama_model"
    assert adapter_env["state"] == "succeeded"
    assert len(adapter_env["candidates"]) == 1

    finding = result["findings"][0]
    assert finding["source_adapter"] == "ollama_model"
    assert finding["provenance"]["adapter"] == "ollama_model"
    assert finding["provenance"]["tool_source"] == "ollama_model"
    assert "support" in finding["support_label"].lower()
    for forbidden in ("truth", "canon", "approved", "promoted"):
        assert forbidden not in finding["support_label"].lower()
    assert finding["owner_decision"]["decision"] == "pending"
    assert finding["owner_decision"].get("approved") is False
    assert finding["review_status"] in {
        "candidate",
        "review_pending",
        "candidate_review_pending",
    }
    assert finding["evidence"][0]["source_locator"] == "raw_idea:L1:C0-78"
    assert finding["source_locator"] == "raw_idea:L1:C0-78"
    assert finding["evidence_fingerprint"].startswith("omi-evid-")
    assert finding["candidate_fingerprint"].startswith("omi-cand-")
    assert finding["normalized_finding_id"].startswith("omi-find-ollama_model-")
    return finding


def test_ollama_model_without_fixture_does_not_call_live_model_and_returns_unavailable() -> None:
    result = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        RAW_IDEA,
        requested_adapters=["ollama_model"],
        adapter_config={"base_url": "http://127.0.0.1:11434"},
    )

    env = _assert_ollama_failed_closed(result)
    assert env["state"] == "unavailable"
    assert "does not perform live ollama calls" in env["explanation"].lower()
    assert "environment variables" in env["explanation"].lower()


def test_valid_ollama_model_json_string_normalizes_to_candidate_only_findings() -> None:
    result = _run_with_fixture(json.dumps(_valid_envelope()))
    finding = _assert_valid_ollama_result(result)
    assert finding["extracted_claim"] == (
        "Test Character Alpha is identified as a character candidate"
    )


def test_valid_ollama_model_dict_normalizes_to_candidate_only_findings() -> None:
    result = _run_with_fixture(_valid_envelope())
    finding = _assert_valid_ollama_result(result)
    assert finding["label"] == "Test Character Alpha"


def test_ollama_model_rejects_non_json_output() -> None:
    result = _run_with_fixture("this is not json")
    env = _assert_ollama_failed_closed(result)
    assert "json" in env["explanation"].lower()


def test_ollama_model_rejects_top_level_array() -> None:
    for fixture in ([], json.dumps([]), 123):
        result = _run_with_fixture(fixture)
        env = _assert_ollama_failed_closed(result)
        assert "json object" in env["explanation"].lower()


def test_ollama_model_rejects_missing_or_unknown_schema_version() -> None:
    missing = _valid_envelope()
    del missing["schema_version"]
    unknown = _valid_envelope(schema_version="future.schema")

    for fixture in (missing, unknown):
        result = _run_with_fixture(fixture)
        env = _assert_ollama_failed_closed(result)
        assert "schema_version" in env["explanation"]


def test_ollama_model_rejects_missing_findings() -> None:
    fixture = _valid_envelope()
    del fixture["findings"]

    result = _run_with_fixture(fixture)
    env = _assert_ollama_failed_closed(result)
    assert "findings" in env["explanation"]


def test_ollama_model_rejects_wrong_adapter() -> None:
    result = _run_with_fixture(_valid_envelope(adapter="story_check"))
    env = _assert_ollama_failed_closed(result)
    assert "adapter" in env["explanation"].lower()


def test_ollama_model_rejects_invalid_status() -> None:
    result = _run_with_fixture(_valid_envelope(status="complete"))
    env = _assert_ollama_failed_closed(result)
    assert "status" in env["explanation"].lower()


def test_ollama_model_rejects_non_succeeded_state_with_findings() -> None:
    result = _run_with_fixture(_valid_envelope(status="empty"))
    env = _assert_ollama_failed_closed(result)
    assert "findings" in env["explanation"].lower()


def test_ollama_model_rejects_missing_evidence_or_source_locator() -> None:
    fixtures: list[dict[str, Any]] = []
    for missing_key in ("evidence", "source_locator", "extracted_claim"):
        fixture = _valid_envelope()
        del fixture["findings"][0][missing_key]
        fixtures.append(fixture)
    fixtures.append(_valid_envelope(findings=[
        _valid_finding(evidence=[{"note": "no source reference"}])
    ]))

    for fixture in fixtures:
        result = _run_with_fixture(fixture)
        _assert_ollama_failed_closed(result)


def test_ollama_model_rejects_unknown_candidate_type() -> None:
    fixture = _valid_envelope(findings=[
        _valid_finding(candidate_type="scene_prose")
    ])

    result = _run_with_fixture(fixture)
    env = _assert_ollama_failed_closed(result)
    assert "candidate_type" in env["explanation"]


def test_ollama_model_rejects_truth_canon_approved_promoted_labels() -> None:
    labels = (
        "truth support",
        "canon support",
        "approved support",
        "promoted support",
    )

    for support_label in labels:
        fixture = _valid_envelope(findings=[
            _valid_finding(support_label=support_label)
        ])
        result = _run_with_fixture(fixture)
        _assert_ollama_failed_closed(result)


def test_ollama_model_rejects_auto_approved_owner_decision() -> None:
    fixture = _valid_envelope(findings=[
        _valid_finding(
            owner_decision={"decision": "approve", "approved": True}
        )
    ])

    result = _run_with_fixture(fixture)
    env = _assert_ollama_failed_closed(result)
    assert "owner_decision" in env["explanation"]


def test_ollama_model_rejects_prose_like_extracted_claim() -> None:
    fixture = _valid_envelope(findings=[
        _valid_finding(extracted_claim="Rewrite: unsafe generated prose request")
    ])

    result = _run_with_fixture(fixture)
    env = _assert_ollama_failed_closed(result)
    assert "prose" in env["explanation"].lower()


def test_ollama_model_rejects_rewrite_continue_outline_draft_polish_improve_fields() -> None:
    forbidden_fields = (
        "rewrite",
        "continue",
        "outline",
        "draft",
        "polish",
        "improve",
        "expand",
        "imitate",
        "revise",
        "better_version",
        "story_text",
        "scene_prose",
        "chapter_prose",
    )

    for field_name in forbidden_fields:
        fixture = _valid_envelope()
        fixture["findings"][0][field_name] = "blocked fixture field"
        result = _run_with_fixture(fixture)
        env = _assert_ollama_failed_closed(result)
        assert "forbidden prose-intent field" in env["explanation"]


def test_ollama_model_findings_are_not_persisted_even_when_persist_candidates_true() -> None:
    result = _run_with_fixture(
        _valid_envelope(),
        persist_candidates=True,
        source_idea_id="idea_123",
    )

    _assert_valid_ollama_result(result)
    assert result["persisted_candidate_ids"] == []


def test_deterministic_fallback_remains_opt_in_and_fallback_only_after_ollama_adapter() -> None:
    result = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        "Character: Test Marker Alpha.",
        requested_adapters=["ollama_model"],
        adapter_fixture_outputs={"ollama_model": _valid_envelope()},
        allow_deterministic_fallback=False,
    )
    assert [env["adapter"] for env in result["adapter_results"]] == [
        "ollama_model"
    ]
    assert result["analysis_status"] == "succeeded"

    with_fallback = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        "Character: Test Marker Alpha.",
        requested_adapters=["ollama_model"],
        adapter_fixture_outputs={"ollama_model": _valid_envelope()},
        allow_deterministic_fallback=True,
    )
    fallback_envs = [
        env for env in with_fallback["adapter_results"]
        if env["adapter"] == "deterministic_fallback"
    ]
    assert len(fallback_envs) == 1
    assert fallback_envs[0].get("fallback_only") is True
    assert "fallback" in fallback_envs[0]["explanation"].lower()


def test_other_tool_adapters_remain_deferred_to_t007_t009() -> None:
    deferred = [
        "story_check",
        "booknlp",
        "spacy",
        "ncp",
        "subtxt",
        "dramatica_flow",
    ]

    result = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        RAW_IDEA,
        requested_adapters=deferred,
        allow_deterministic_fallback=False,
    )

    assert result["analysis_status"] == "fail_closed"
    assert result["findings"] == []
    assert result["persisted_candidate_ids"] == []
    observed = {env["adapter"]: env for env in result["adapter_results"]}
    assert set(observed) == set(deferred)
    for adapter in deferred:
        assert observed[adapter]["state"] == "unavailable"
        assert observed[adapter]["candidates"] == []
        assert observed[adapter]["explanation"]
    assert "T007" in observed["booknlp"]["explanation"]
    assert "T007" in observed["spacy"]["explanation"]
    assert "T008" in observed["story_check"]["explanation"]
    assert "T009" in observed["ncp"]["explanation"]
    assert "T009" in observed["subtxt"]["explanation"]
    assert "T009" in observed["dramatica_flow"]["explanation"]
