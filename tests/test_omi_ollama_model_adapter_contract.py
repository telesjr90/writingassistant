"""PHASE8-IMPL-023-T006 Ollama/model fixture adapter contract tests.

These tests use fixture/mock output only. They do not call Ollama, import an
Ollama client, make HTTP requests, run Story Check, run BookNLP/spaCy, run
NCP/Subtxt/dramatica-flow, mutate Memory/Canon, run apply-promotion, or
generate story prose.
"""

from __future__ import annotations

import io
import json
import sys
import urllib.error
import urllib.request
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
    assert finding["evidence"][0]["source_locator"]
    assert finding["source_locator"] == finding["evidence"][0]["source_locator"]
    assert finding["evidence_fingerprint"].startswith("omi-evid-")
    assert finding["candidate_fingerprint"].startswith("omi-cand-")
    assert finding["normalized_finding_id"].startswith("omi-find-ollama_model-")
    return finding


def test_ollama_exact_source_operation_identity_is_explicit() -> None:
    assert oao.OMI_OLLAMA_ADAPTER_NAME == "ollama_model"
    assert oao.OMI_OLLAMA_EXACT_SOURCE_OPERATION_ID == "analyze-ollama-model"
    assert (
        oao.OMI_OLLAMA_EXACT_SOURCE_OPERATION_SEMANTICS
        == "exact_source_structured_extraction"
    )


def _normalized_evidence_fixture() -> tuple[dict[str, Any], dict[str, Any]]:
    source_identity = {
        "project_id": "demo",
        "snapshot_id": "snapshot-t007b",
        "content_hash": "a" * 64,
    }
    finding = oao.validate_normalized_finding(
        {
            "candidate_type": "evidence_note",
            "label": "Upstream evidence",
            "extracted_claim": "The selected clue supplies bounded support.",
            "evidence": [
                {
                    "source_excerpt": "library clue",
                    "source_locator": {
                        "snapshot_id": source_identity["snapshot_id"],
                        "source_hash": source_identity["content_hash"],
                    },
                }
            ],
            "source_locator": "raw_idea:L1:C0-12",
            "provenance": {
                "tool_source": "spacy",
                "adapter": "spacy",
                "support": "spaCy support only",
                "operation_id": "analyze-spacy",
            },
            "source_adapter": "spacy",
            "support_label": "bounded support",
            "owner_decision": {"decision": "pending", "approved": False},
            "review_status": "candidate_review_pending",
            "raw_finding_id": "spacy-upstream-001",
        }
    )
    packet = {
        "schema_version": oao.OMI_OLLAMA_NORMALIZED_EVIDENCE_PACKET_VERSION,
        "project_id": "demo",
        "run_id": "analysis-run-t007b",
        "source_identity": source_identity,
        "source_snapshot_id": source_identity["snapshot_id"],
        "source_content_hash": source_identity["content_hash"],
        "consumer_operation_id": oao.OMI_OLLAMA_NORMALIZED_EVIDENCE_OPERATION_ID,
        "items": [
            {
                "producer_operation_id": "analyze-spacy",
                "producer_adapter_id": "spacy",
                "normalized_finding_id": finding["normalized_finding_id"],
                "finding": finding,
                "source_refs": [],
                "evidence_refs": [],
                "provenance_refs": [],
                "source_locator_refs": [],
            }
        ],
    }
    return packet, source_identity


def _normalized_t007b_candidate(**overrides: Any) -> dict[str, Any]:
    candidate = {
        "candidate_type": "diagnostic_question",
        "label": "Evidence interpretation",
        "extracted_claim": "The bounded evidence leaves motive unresolved.",
        "evidence": [
            {
                "source_excerpt": "library clue",
                "source_locator": "raw_idea:L1:C0-12",
            }
        ],
        "source_locator": "raw_idea:L1:C0-12",
        "provenance": {
            "tool_source": "ollama_model",
            "adapter": "ollama_model",
            "support": "Ollama interpretation support only",
        },
        "source_adapter": "ollama_model",
        "support_label": "bounded interpretation support",
        "owner_decision": {"decision": "pending", "approved": False},
        "review_status": "candidate_review_pending",
        "raw_finding_id": "ollama-t007b-001",
    }
    candidate.update(overrides)
    return candidate


def test_ollama_normalized_evidence_operation_identity_and_bounded_runner() -> None:
    assert oao.OMI_OLLAMA_NORMALIZED_EVIDENCE_OPERATION_ID == (
        "analyze-ollama-normalized-evidence"
    )
    assert oao.OMI_OLLAMA_NORMALIZED_EVIDENCE_OPERATION_SEMANTICS == (
        "normalized_evidence_interpretation"
    )
    received = {}

    def runner(*, normalized_evidence_packet):
        received.update(normalized_evidence_packet)
        assert "raw_idea" not in normalized_evidence_packet
        assert "owner_selected_source" not in normalized_evidence_packet
        assert "raw_artifacts" not in normalized_evidence_packet
        return {
            "adapter": "ollama_model",
            "state": "succeeded",
            "explanation": "deterministic normalized-evidence fixture",
            "candidates": [_normalized_t007b_candidate()],
        }

    packet, identity = _normalized_evidence_fixture()
    result = oao.run_ollama_normalized_evidence_operation(
        packet,
        expected_run_id="analysis-run-t007b",
        expected_source_identity=identity,
        producer_operations={"analyze-spacy": "spacy"},
        runner=runner,
    )
    assert result["operation_id"] == oao.OMI_OLLAMA_NORMALIZED_EVIDENCE_OPERATION_ID
    assert result["adapter"] == oao.OMI_OLLAMA_ADAPTER_NAME
    assert result["state"] == "succeeded"
    assert received["items"][0]["finding"]["normalized_finding_id"]
    candidate = result["candidates"][0]
    assert candidate["provenance"]["operation_id"] == (
        oao.OMI_OLLAMA_NORMALIZED_EVIDENCE_OPERATION_ID
    )
    assert candidate["normalized_evidence_refs"] == [
        packet["items"][0]["normalized_finding_id"]
    ]
    assert candidate["owner_decision"] == {"decision": "pending", "approved": False}
    assert candidate["review_status"] == "candidate_review_pending"


def test_ollama_normalized_evidence_missing_invalid_and_mismatched_fail_closed() -> None:
    packet, identity = _normalized_evidence_fixture()
    calls = 0

    def runner(**kwargs):
        nonlocal calls
        calls += 1
        return {
            "adapter": "ollama_model",
            "state": "succeeded",
            "explanation": "must not run",
            "candidates": [_normalized_t007b_candidate()],
        }

    missing = oao.run_ollama_normalized_evidence_operation(
        None,
        expected_run_id="analysis-run-t007b",
        expected_source_identity=identity,
        producer_operations={"analyze-spacy": "spacy"},
        runner=runner,
    )
    assert missing["state"] == "unavailable"
    assert missing["candidates"] == []

    invalid_packets = []
    invalid_finding = json.loads(json.dumps(packet))
    invalid_finding["items"][0]["finding"] = {"candidate_type": "evidence_note"}
    invalid_packets.append((invalid_finding, "analysis-run-t007b", identity))
    wrong_run = json.loads(json.dumps(packet))
    wrong_run["run_id"] = "analysis-run-other"
    invalid_packets.append((wrong_run, "analysis-run-t007b", identity))
    wrong_source = json.loads(json.dumps(packet))
    wrong_source["source_snapshot_id"] = "snapshot-other"
    invalid_packets.append((wrong_source, "analysis-run-t007b", identity))
    opaque_artifact = json.loads(json.dumps(packet))
    opaque_artifact["raw_artifact"] = {"payload": "opaque output"}
    invalid_packets.append((opaque_artifact, "analysis-run-t007b", identity))

    for invalid, expected_run_id, expected_identity in invalid_packets:
        result = oao.run_ollama_normalized_evidence_operation(
            invalid,
            expected_run_id=expected_run_id,
            expected_source_identity=expected_identity,
            producer_operations={"analyze-spacy": "spacy"},
            runner=runner,
        )
        assert result["state"] == "failed_closed"
        assert result["candidates"] == []
    assert calls == 0


def test_ollama_normalized_evidence_unsafe_output_fails_closed() -> None:
    packet, identity = _normalized_evidence_fixture()
    unsafe_candidates = [
        _normalized_t007b_candidate(
            extracted_claim="Rewrite: continue the scene as polished prose."
        ),
        _normalized_t007b_candidate(support_label="canon truth support"),
        _normalized_t007b_candidate(
            owner_decision={"decision": "approve", "approved": True}
        ),
    ]
    for candidate in unsafe_candidates:
        raw_result = {
            "adapter": "ollama_model",
            "state": "succeeded",
            "explanation": "unsafe fixture",
            "candidates": [candidate],
        }
        result = oao.run_ollama_normalized_evidence_operation(
            packet,
            expected_run_id="analysis-run-t007b",
            expected_source_identity=identity,
            producer_operations={"analyze-spacy": "spacy"},
            runner=lambda **kwargs: raw_result,
        )
        assert result["state"] == "failed_closed"
        assert result["candidates"] == []
        assert result["original_output"] == raw_result
        assert result["original_output"] is not raw_result


def test_ollama_normalized_evidence_runner_exception_invents_no_output() -> None:
    packet, identity = _normalized_evidence_fixture()

    def runner(**kwargs):
        raise RuntimeError("deterministic runner failure")

    result = oao.run_ollama_normalized_evidence_operation(
        packet,
        expected_run_id="analysis-run-t007b",
        expected_source_identity=identity,
        producer_operations={"analyze-spacy": "spacy"},
        runner=runner,
    )
    assert result["state"] == "error"
    assert result["candidates"] == []
    assert "original_output" not in result
    assert "RuntimeError" in result["explanation"]


def test_ollama_model_without_fixture_does_not_call_live_model_and_returns_unavailable() -> None:
    result = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        RAW_IDEA,
        requested_adapters=["ollama_model"],
        adapter_config={"base_url": "http://127.0.0.1:11434"},
    )

    env = _assert_ollama_failed_closed(result)
    assert env["state"] == "unavailable"
    assert "t006 fixture" in env["explanation"].lower()
    assert "live ollama env" in env["explanation"].lower()


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


# ---------------------------------------------------------------------------
# T015C — Live Ollama structured extraction adapter behind flags
# ---------------------------------------------------------------------------


class _MockResponse:
    """Mock HTTP response with context manager support."""

    def __init__(self, data: dict[str, Any]) -> None:
        self._body = json.dumps(data).encode("utf-8")

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> _MockResponse:
        return self

    def __exit__(self, *args: Any) -> None:
        pass


class _MockRaisingUrlopen:
    """Callable that raises an HTTPError."""

    def __call__(self, request: Any, *args: Any, **kwargs: Any) -> None:
        msg = "mock HTTP error"
        raise urllib.error.HTTPError(
            "http://mock", 500, msg, {}, io.BytesIO(b"error")
        )


def _valid_ollama_chat_response(model_content: str) -> dict[str, Any]:
    """Build a valid Ollama /api/chat response dict."""
    return {
        "model": "qwen3:8b",
        "created_at": "2024-01-01T00:00:00Z",
        "message": {
            "role": "assistant",
            "content": model_content,
        },
        "done": True,
    }


def _valid_live_model_content(
    *, source: str = RAW_IDEA, source_span_id: str | None = None
) -> str:
    """Build a valid JSON string that passes validate_ollama_model_envelope."""
    if source_span_id is None:
        source_span_id = oao._build_ollama_source_span_catalog(source)[0][
            "source_span_id"
        ]
    return json.dumps({
        "schema_version": oao.OMI_OLLAMA_SCHEMA_VERSION,
        "adapter": "ollama_model",
        "status": "succeeded",
        "explanation": "live Ollama test extraction",
        "findings": [
            {
                "candidate_type": "character",
                "label": "Test Character Alpha",
                "extracted_claim": (
                    "Test Character Alpha is identified as a character candidate"
                ),
                "evidence": [
                    {
                        "source_span_id": source_span_id,
                    }
                ],
            }
        ],
    })


def _first_live_span_evidence(source: str = RAW_IDEA) -> list[dict[str, str]]:
    span_id = oao._build_ollama_source_span_catalog(source)[0]["source_span_id"]
    return [{"source_span_id": span_id}]


def _mock_live_ollama_env(monkeypatch: Any) -> None:
    """Set env vars to enable live Ollama."""
    monkeypatch.setenv("OMI_LIVE_TOOLS_ENABLED", "true")
    monkeypatch.setenv("OMI_LIVE_OLLAMA_ENABLED", "true")


def _mock_urlopen(monkeypatch: Any, response_data: dict[str, Any]) -> None:
    """Monkeypatch urllib.request.urlopen to return a mock response."""
    def mock_urlopen(request: Any, *args: Any, **kwargs: Any) -> _MockResponse:
        return _MockResponse(response_data)
    monkeypatch.setattr(urllib.request, "urlopen", mock_urlopen)


def _mock_urlopen_error(monkeypatch: Any) -> None:
    """Monkeypatch urllib.request.urlopen to raise an HTTPError."""
    monkeypatch.setattr(urllib.request, "urlopen", _MockRaisingUrlopen())


def test_live_ollama_disabled_by_default_returns_unavailable() -> None:
    """No env flags -> live Ollama path not triggered -> unavailable."""
    result = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        RAW_IDEA,
        requested_adapters=["ollama_model"],
        persist_candidates=False,
    )
    env = _assert_ollama_failed_closed(result)
    assert env["state"] == "unavailable"
    assert "T006 fixture" in env["explanation"] or "fixture" in env["explanation"]
    assert "execution_provenance" not in env
    assert "runtime_execution" not in env
    assert result["safety"]["no_real_tool_calls"] is True
    assert result["safety"]["no_model_calls"] is True
    assert result["safety"]["model_call_state"] == "not_occurred"


def test_live_ollama_enabled_with_mocked_valid_model_returns_candidates(
    monkeypatch: Any,
) -> None:
    """Live Ollama with mocked /api/chat returns normalized candidates."""
    _mock_live_ollama_env(monkeypatch)
    _mock_urlopen(
        monkeypatch,
        _valid_ollama_chat_response(_valid_live_model_content()),
    )
    result = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        RAW_IDEA,
        requested_adapters=["ollama_model"],
        persist_candidates=False,
    )
    finding = _assert_valid_ollama_result(result)
    assert finding["label"] == "Test Character Alpha"
    assert "ollama model" in finding["provenance"]["support"].lower()
    evidence = finding["evidence"][0]
    start = RAW_IDEA.index(evidence["source_excerpt"])
    end = start + len(evidence["source_excerpt"])
    assert (evidence["char_start"], evidence["char_end"]) == (start, end)
    assert evidence["char_offset_basis"] == oao.exact_source_map.CHAR_OFFSET_BASIS
    assert (evidence["byte_start"], evidence["byte_end"]) == (
        len(RAW_IDEA[:start].encode("utf-8")),
        len(RAW_IDEA[:end].encode("utf-8")),
    )
    assert evidence["byte_offset_basis"] == oao.exact_source_map.BYTE_OFFSET_BASIS
    assert evidence["artifact_file_id"] == "source-artifact"


def test_live_ollama_model_supplied_paraphrase_fails_closed_before_control_plane(
    monkeypatch: Any,
) -> None:
    """Model-authored evidence text is rejected instead of best-matched."""
    source = "Owner note: repeated clue, then repeated clue."
    content = json.dumps(
        {
            "schema_version": oao.OMI_OLLAMA_SCHEMA_VERSION,
            "adapter": "ollama_model",
            "status": "succeeded",
            "explanation": "mocked ambiguous extraction",
            "findings": [
                {
                    "candidate_type": "object",
                    "label": "Repeated clue",
                    "extracted_claim": "A repeated clue is identified as an object candidate",
                        "evidence": [
                            {
                                "source_excerpt": "repeated clue",
                                "source_locator": "text:1-2",
                            }
                        ],
                    }
            ],
        }
    )
    _mock_live_ollama_env(monkeypatch)
    _mock_urlopen(monkeypatch, _valid_ollama_chat_response(content))

    result = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        source,
        requested_adapters=["ollama_model"],
        persist_candidates=False,
    )

    envelope = _assert_ollama_failed_closed(result)
    assert "must contain only source_span_id" in envelope["explanation"]
    assert envelope["original_output"]["message"]["content"] == content
    assert envelope["runtime_execution"]["model_calls_occurred"] is True


def test_live_ollama_unknown_span_selection_fails_closed(
    monkeypatch: Any,
) -> None:
    """An ID outside the app-owned catalog cannot become evidence."""
    _mock_live_ollama_env(monkeypatch)
    content = _valid_live_model_content(
        source_span_id="source-span-9999-unknown000000"
    )
    _mock_urlopen(monkeypatch, _valid_ollama_chat_response(content))

    result = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        RAW_IDEA,
        requested_adapters=["ollama_model"],
        persist_candidates=True,
    )

    envelope = _assert_ollama_failed_closed(result)
    assert "unknown source_span_id" in envelope["explanation"]
    assert result["persisted_candidate_ids"] == []
    assert result["safety"]["no_memory_canon_mutation"] is True
    assert result["safety"]["no_apply_promotion"] is True
    assert result["safety"]["no_story_prose_generation"] is True


def test_live_ollama_duplicate_span_selection_fails_closed(
    monkeypatch: Any,
) -> None:
    """A finding cannot select the same exact span more than once."""
    span_id = oao._build_ollama_source_span_catalog(RAW_IDEA)[0][
        "source_span_id"
    ]
    payload = json.loads(_valid_live_model_content(source_span_id=span_id))
    payload["findings"][0]["evidence"].append({"source_span_id": span_id})
    content = json.dumps(payload)
    _mock_live_ollama_env(monkeypatch)
    _mock_urlopen(monkeypatch, _valid_ollama_chat_response(content))

    result = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        RAW_IDEA,
        requested_adapters=["ollama_model"],
        persist_candidates=False,
    )

    envelope = _assert_ollama_failed_closed(result)
    assert "selected duplicate source_span_id" in envelope["explanation"]
    assert envelope["original_output"]["message"]["content"] == content


def test_live_ollama_runner_preserves_exact_owner_source_bytes(
    monkeypatch: Any,
) -> None:
    """The exact-source operation preserves a semantically observable newline."""
    source = (
        "VALIDATION RECORD.\n"
        "Person: Mara Vale.\n"
        "Object: brass compass.\n"
    )
    source_bytes = source.encode("utf-8")
    bodies: list[bytes] = []

    def capture_urlopen(request: Any, *args: Any, **kwargs: Any) -> _MockResponse:
        bodies.append(request.data)
        return _MockResponse(
            _valid_ollama_chat_response(
                _valid_live_model_content(source=source)
            )
        )

    _mock_live_ollama_env(monkeypatch)
    monkeypatch.setattr(urllib.request, "urlopen", capture_urlopen)
    result = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        source,
        requested_adapters=["ollama_model"],
        persist_candidates=False,
    )

    assert source.endswith("\n")
    assert len(source_bytes) == 61
    assert __import__("hashlib").sha256(source_bytes).hexdigest() == (
        "4da6a38ab30a3702ec91d4c03facea2703ee13e173d2de067aa9ed022a647970"
    )
    assert result["analysis_status"] == "succeeded"
    assert len(bodies) == 1
    sent_body = json.loads(bodies[0].decode("utf-8"))
    runtime_source = sent_body["messages"][1]["content"]
    assert runtime_source == source
    assert len(runtime_source.encode("utf-8")) == len(source_bytes)
    assert __import__("hashlib").sha256(
        runtime_source.encode("utf-8")
    ).hexdigest() == __import__("hashlib").sha256(source_bytes).hexdigest()


def test_live_ollama_uses_env_base_url(monkeypatch: Any) -> None:
    """Live Ollama uses OMI_LIVE_OLLAMA_BASE_URL env var."""
    _mock_live_ollama_env(monkeypatch)
    monkeypatch.setenv("OMI_LIVE_OLLAMA_BASE_URL", "http://custom:11434")
    calls: list[str] = []

    def capture_urlopen(request: Any, *args: Any, **kwargs: Any) -> _MockResponse:
        full_url = request.full_url if hasattr(request, "full_url") else str(request)
        calls.append(full_url)
        return _MockResponse(
            _valid_ollama_chat_response(_valid_live_model_content())
        )

    monkeypatch.setattr(urllib.request, "urlopen", capture_urlopen)
    result = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        RAW_IDEA,
        requested_adapters=["ollama_model"],
        persist_candidates=False,
    )
    assert result["analysis_status"] == "succeeded"
    assert len(calls) == 1
    assert "custom:11434" in calls[0]


def test_live_ollama_uses_env_model(monkeypatch: Any) -> None:
    """Live Ollama uses OMI_LIVE_OLLAMA_MODEL env var."""
    _mock_live_ollama_env(monkeypatch)
    monkeypatch.setenv("OMI_LIVE_OLLAMA_MODEL", "phi3:mini")

    bodies: list[bytes] = []

    def capture_urlopen(request: Any, *args: Any, **kwargs: Any) -> _MockResponse:
        bodies.append(request.data)
        return _MockResponse(
            _valid_ollama_chat_response(_valid_live_model_content())
        )

    monkeypatch.setattr(urllib.request, "urlopen", capture_urlopen)
    result = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        RAW_IDEA,
        requested_adapters=["ollama_model"],
        persist_candidates=False,
    )
    assert result["analysis_status"] == "succeeded"
    assert len(bodies) == 1
    sent_body = json.loads(bodies[0].decode("utf-8"))
    assert sent_body["model"] == "phi3:mini"


def test_live_ollama_uses_env_model_name_compat(monkeypatch: Any) -> None:
    """Live Ollama falls back to OMI_LIVE_OLLAMA_MODEL_NAME for compat."""
    _mock_live_ollama_env(monkeypatch)
    monkeypatch.setenv("OMI_LIVE_OLLAMA_MODEL_NAME", "compat-model")

    bodies: list[bytes] = []

    def capture_urlopen(request: Any, *args: Any, **kwargs: Any) -> _MockResponse:
        bodies.append(request.data)
        return _MockResponse(
            _valid_ollama_chat_response(_valid_live_model_content())
        )

    monkeypatch.setattr(urllib.request, "urlopen", capture_urlopen)
    result = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        RAW_IDEA,
        requested_adapters=["ollama_model"],
        persist_candidates=False,
    )
    assert result["analysis_status"] == "succeeded"
    assert len(bodies) == 1
    sent_body = json.loads(bodies[0].decode("utf-8"))
    assert sent_body["model"] == "compat-model"


def test_live_ollama_http_error_fails_closed(monkeypatch: Any) -> None:
    """HTTP error/timeout -> fail closed with no findings."""
    _mock_live_ollama_env(monkeypatch)
    _mock_urlopen_error(monkeypatch)

    result = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        RAW_IDEA,
        requested_adapters=["ollama_model"],
        persist_candidates=False,
    )
    env = _assert_ollama_failed_closed(result)
    assert "HTTP" in env["explanation"] or "failed" in env["explanation"]
    assert "original_output" not in env
    for plane in ("tool", "runtime", "provider", "model"):
        assert env["execution_provenance"][plane] == {
            "availability": "unknown",
            "name": None,
            "version": None,
        }
    assert env["runtime_execution"] == {
        "authorized": True,
        "real_tool_calls_occurred": True,
        "model_calls_occurred": None,
    }
    assert result["safety"]["no_real_tool_calls"] is False
    assert result["safety"]["authorized_real_tool_calls_occurred"] is True
    assert result["safety"]["no_model_calls"] is None
    assert result["safety"]["model_calls_occurred"] is None
    assert result["safety"]["model_call_state"] == "unknown"
    assert result["safety"]["no_prohibited_real_tool_calls"] is True
    assert result["safety"]["no_memory_canon_mutation"] is True
    assert result["safety"]["no_apply_promotion"] is True


def test_live_ollama_invalid_response_json_fails_closed(
    monkeypatch: Any,
) -> None:
    """Non-JSON model content -> fail closed with no findings."""
    _mock_live_ollama_env(monkeypatch)
    _mock_urlopen(
        monkeypatch,
        _valid_ollama_chat_response("this is not json"),
    )

    result = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        RAW_IDEA,
        requested_adapters=["ollama_model"],
        persist_candidates=False,
    )
    env = _assert_ollama_failed_closed(result)
    assert "validation" in env["explanation"].lower() or "json" in (
        env["explanation"].lower()
    )


def test_live_ollama_invalid_control_character_fails_closed_without_mutation(
    monkeypatch: Any,
) -> None:
    """Literal control characters are retained as raw output, never repaired."""
    invalid_content = (
        '{"schema_version":"omi_ollama_structured_extraction.v1",'
        '"adapter":"ollama_model","status":"empty",'
        '"explanation":"invalid\ncontrol character","findings":[]}'
    )
    _mock_live_ollama_env(monkeypatch)
    _mock_urlopen(
        monkeypatch,
        _valid_ollama_chat_response(invalid_content),
    )

    result = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        RAW_IDEA,
        requested_adapters=["ollama_model"],
        persist_candidates=True,
    )

    envelope = _assert_ollama_failed_closed(result)
    assert envelope["original_output"]["message"]["content"] == invalid_content
    assert "invalid control character" in envelope["explanation"].lower()
    assert result["persisted_candidate_ids"] == []
    assert result["safety"]["no_memory_canon_mutation"] is True
    assert result["safety"]["no_apply_promotion"] is True
    assert result["safety"]["no_story_prose_generation"] is True


def test_live_ollama_invalid_person_type_retains_original_and_runtime_truth(
    monkeypatch: Any,
) -> None:
    """Rejected live output remains immutable support, never a finding/candidate."""

    _mock_live_ollama_env(monkeypatch)
    invalid_content = json.dumps(
        {
            "schema_version": oao.OMI_OLLAMA_SCHEMA_VERSION,
            "adapter": "ollama_model",
            "status": "succeeded",
            "explanation": "mocked live extraction with an invalid type",
            "findings": [
                {
                    "candidate_type": "person",
                    "label": "Mara Vale",
                    "extracted_claim": "Mara Vale is named in the validation record.",
                    "evidence": _first_live_span_evidence(),
                    "support_label": "ollama model support strength only",
                }
            ],
        }
    )
    _mock_urlopen(
        monkeypatch,
        _valid_ollama_chat_response(invalid_content),
    )

    result = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        RAW_IDEA,
        requested_adapters=["ollama_model"],
        persist_candidates=False,
    )

    env = _assert_ollama_failed_closed(result)
    assert "candidate_type" in env["explanation"]
    assert json.loads(env["original_output"]["message"]["content"])["findings"][0][
        "candidate_type"
    ] == "person"
    assert env["original_output"]["message"]["content"] == invalid_content
    assert env["candidates"] == []
    assert result["findings"] == []
    assert result["persisted_candidate_ids"] == []
    assert env["execution_provenance"] == {
        "implementation_kind": "official_external",
        "user_facing_label": "Ollama exact-source structured extraction",
        "tool": {"availability": "available", "name": "Ollama", "version": None},
        "runtime": {
            "availability": "available",
            "name": "Ollama HTTP API",
            "version": None,
        },
        "provider": {"availability": "available", "name": "Ollama", "version": None},
        "model": {"availability": "available", "name": "qwen3:8b", "version": None},
    }
    assert env["runtime_execution"] == {
        "authorized": True,
        "real_tool_calls_occurred": True,
        "model_calls_occurred": True,
    }
    assert result["safety"]["no_prohibited_real_tool_calls"] is True
    assert result["safety"]["no_real_tool_calls"] is False
    assert result["safety"]["authorized_real_tool_calls_occurred"] is True
    assert result["safety"]["no_model_calls"] is False
    assert result["safety"]["model_calls_occurred"] is True
    assert result["safety"]["model_call_state"] == "occurred"
    assert result["safety"]["no_memory_canon_mutation"] is True
    assert result["safety"]["no_apply_promotion"] is True


def test_live_ollama_missing_message_content_fails_closed(
    monkeypatch: Any,
) -> None:
    """Response missing message.content -> fail closed."""
    _mock_live_ollama_env(monkeypatch)
    _mock_urlopen(
        monkeypatch,
        {
            "model": "qwen3:8b",
            "message": {},
            "done": True,
        },
    )

    result = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        RAW_IDEA,
        requested_adapters=["ollama_model"],
        persist_candidates=False,
    )
    env = _assert_ollama_failed_closed(result)
    assert "message" in env["explanation"].lower() or "content" in (
        env["explanation"].lower()
    )


def test_live_ollama_prose_output_fails_closed(
    monkeypatch: Any,
) -> None:
    """Prose/markdown/wrapped content -> fail closed."""
    _mock_live_ollama_env(monkeypatch)
    prose_content = (
        "Meanwhile the room grew dark and the rain hammered the windows."
    )
    _mock_urlopen(
        monkeypatch,
        _valid_ollama_chat_response(
            json.dumps({
                "schema_version": oao.OMI_OLLAMA_SCHEMA_VERSION,
                "adapter": "ollama_model",
                "status": "succeeded",
                "findings": [
                    {
                        "candidate_type": "character",
                        "label": "Room",
                        "extracted_claim": prose_content,
                            "evidence": _first_live_span_evidence(),
                    }
                ],
            })
        ),
    )

    result = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        RAW_IDEA,
        requested_adapters=["ollama_model"],
        persist_candidates=False,
    )
    env = _assert_ollama_failed_closed(result)
    assert "prose" in env["explanation"].lower()


def test_live_ollama_unsafe_output_fails_closed(
    monkeypatch: Any,
) -> None:
    """Truth/canon/approval output -> fail closed."""
    _mock_live_ollama_env(monkeypatch)
    _mock_urlopen(
        monkeypatch,
        _valid_ollama_chat_response(
            json.dumps({
                "schema_version": oao.OMI_OLLAMA_SCHEMA_VERSION,
                "adapter": "ollama_model",
                "status": "succeeded",
                "findings": [
                    {
                        "candidate_type": "character",
                        "label": "Test",
                        "extracted_claim": (
                            "Test is a confirmed canonical fact"
                        ),
                            "evidence": _first_live_span_evidence(),
                            "support_label": "canon truth support",
                    }
                ],
            })
        ),
    )

    result = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        RAW_IDEA,
        requested_adapters=["ollama_model"],
        persist_candidates=False,
    )
    env = _assert_ollama_failed_closed(result)
    assert "truth" in env["explanation"].lower() or "canon" in (
        env["explanation"].lower()
    )


def test_existing_fixture_ollama_tests_still_pass() -> None:
    """Existing fixture-only Ollama tests remain unaffected by live path."""
    result = _run_with_fixture(json.dumps(_valid_envelope()))
    _assert_valid_ollama_result(result)

    result2 = _run_with_fixture("not json")
    _assert_ollama_failed_closed(result2)

    result3 = _run_with_fixture([])
    _assert_ollama_failed_closed(result3)

    result4 = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        RAW_IDEA,
        requested_adapters=["ollama_model"],
        persist_candidates=False,
    )
    _assert_ollama_failed_closed(result4)


# ---------------------------------------------------------------------------
# T015E — Disable Qwen thinking mode for live Ollama structured extraction
# ---------------------------------------------------------------------------


def test_live_ollama_request_payload_includes_think_false(
    monkeypatch: Any,
) -> None:
    """Live Ollama /api/chat payload includes top-level ``think: false``.

    Qwen3 thinking-mode output would otherwise consume the response budget
    and leave ``message.content`` empty. The top-level ``think`` field is
    the Ollama-level switch to disable thinking output.
    """
    _mock_live_ollama_env(monkeypatch)
    bodies: list[bytes] = []

    def capture_urlopen(request: Any, *args: Any, **kwargs: Any) -> _MockResponse:
        bodies.append(request.data)
        return _MockResponse(
            _valid_ollama_chat_response(_valid_live_model_content())
        )

    monkeypatch.setattr(urllib.request, "urlopen", capture_urlopen)
    result = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        RAW_IDEA,
        requested_adapters=["ollama_model"],
        persist_candidates=False,
    )
    assert result["analysis_status"] == "succeeded"
    assert len(bodies) == 1
    sent_body = json.loads(bodies[0].decode("utf-8"))
    assert sent_body.get("think") is False
    assert sent_body.get("stream") is False
    assert sent_body.get("model") == "qwen3:8b"
    output_format = sent_body.get("format")
    assert output_format["type"] == "object"
    assert output_format["additionalProperties"] is False
    assert output_format["required"] == [
        "schema_version",
        "adapter",
        "status",
        "explanation",
        "findings",
    ]
    finding_schema = output_format["properties"]["findings"]["items"]
    assert finding_schema["required"] == [
        "candidate_type",
        "label",
        "extracted_claim",
        "evidence",
    ]
    evidence_schema = finding_schema["properties"]["evidence"]["items"]
    assert evidence_schema["required"] == ["source_span_id"]
    assert sent_body["messages"][1]["content"] == RAW_IDEA
    catalog = json.loads(sent_body["messages"][2]["content"])
    expected_spans = oao._build_ollama_source_span_catalog(RAW_IDEA)
    assert catalog["source_span_catalog"] == [
        {
            "source_span_id": span["source_span_id"],
            "source_text": span["source_excerpt"],
        }
        for span in expected_spans
    ]


def test_live_ollama_parses_extraction_json_only_from_message_content(
    monkeypatch: Any,
) -> None:
    """Adapter extracts JSON only from ``message.content``, not ``message.thinking``.

    Even if Qwen3 thinking-mode output contains a valid-looking extraction
    envelope, the adapter must read only ``message.content`` and must not
    treat ``message.thinking`` as extraction output.
    """
    _mock_live_ollama_env(monkeypatch)
    valid_extraction_in_thinking = json.dumps({
        "schema_version": oao.OMI_OLLAMA_SCHEMA_VERSION,
        "adapter": "ollama_model",
        "status": "succeeded",
        "explanation": "embedded in thinking trace (must be ignored)",
        "findings": [
            {
                "candidate_type": "character",
                "label": "Thinking Leaked Character",
                "extracted_claim": (
                    "Thinking Leaked Character appears in the thinking trace"
                ),
                "evidence": [
                    {
                        "source_excerpt": (
                            "Owner note names Thinking Leaked Character"
                        ),
                        "source_locator": "raw_idea:L1:C0-78",
                    }
                ],
                "source_locator": "raw_idea:L1:C0-78",
                "support_label": "ollama model support strength only",
            }
        ],
    })
    content_extraction = _valid_live_model_content()
    _mock_urlopen(
        monkeypatch,
        {
            "model": "qwen3:8b",
            "created_at": "2024-01-01T00:00:00Z",
            "message": {
                "role": "assistant",
                "content": content_extraction,
                "thinking": valid_extraction_in_thinking,
            },
            "done": True,
        },
    )

    result = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        RAW_IDEA,
        requested_adapters=["ollama_model"],
        persist_candidates=False,
    )
    finding = _assert_valid_ollama_result(result)
    assert finding["label"] == "Test Character Alpha"
    assert "Thinking Leaked Character" not in json.dumps(result["findings"])


def test_live_ollama_empty_content_with_thinking_fails_closed(
    monkeypatch: Any,
) -> None:
    """Empty ``message.content`` with non-empty ``message.thinking`` fails closed.

    This is the exact failure shape Qwen3 thinking-mode produces when the
    response budget is consumed by thinking output: ``message.content`` is
    empty and ``message.thinking`` is non-empty. The adapter must fail
    closed with no findings and must not parse ``message.thinking``.
    """
    _mock_live_ollama_env(monkeypatch)
    thinking_trace = (
        "Let me analyze the raw idea and extract candidate findings. "
        "First, identify character entities. Then, identify location entities. "
        "Finally, structure the JSON output."
    )
    _mock_urlopen(
        monkeypatch,
        {
            "model": "qwen3:8b",
            "created_at": "2024-01-01T00:00:00Z",
            "message": {
                "role": "assistant",
                "content": "",
                "thinking": thinking_trace,
            },
            "done_reason": "length",
            "done": True,
        },
    )

    result = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        RAW_IDEA,
        requested_adapters=["ollama_model"],
        persist_candidates=False,
    )
    env = _assert_ollama_failed_closed(result)
    assert result["findings"] == []
    assert result["persisted_candidate_ids"] == []
    assert "validation" in env["explanation"].lower() or "json" in (
        env["explanation"].lower()
    )


# ---------------------------------------------------------------------------
# T015F — Narrow no-prose guard scope and configure live Ollama timeout
# ---------------------------------------------------------------------------


_OWNER_PROSE_IDEA = (
    "Detective Mara Vale meets Jonah Cross at the old Vancouver "
    "observatory after midnight while the brass compass from the "
    "missing ship points toward Blackwater Pier under a sky full of "
    "low clouds and a cold wind off the water."
)


def test_live_ollama_default_timeout_is_180_seconds(monkeypatch: Any) -> None:
    """T015F: live Ollama HTTP timeout defaults to 180 seconds.

    The 30-second hard-coded timeout is too short for ``qwen3:8b`` with
    the full T006 system prompt (~111s on the owner's hardware). The
    default is now 180 seconds, configurable via
    ``OMI_LIVE_OLLAMA_TIMEOUT_SECONDS``.
    """
    _mock_live_ollama_env(monkeypatch)
    captured: dict[str, Any] = {}

    def capture_urlopen(request: Any, *args: Any, **kwargs: Any) -> _MockResponse:
        captured["timeout"] = kwargs.get("timeout", args[0] if args else None)
        return _MockResponse(
            _valid_ollama_chat_response(_valid_live_model_content())
        )

    monkeypatch.setattr(urllib.request, "urlopen", capture_urlopen)
    result = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        RAW_IDEA,
        requested_adapters=["ollama_model"],
        persist_candidates=False,
    )
    assert result["analysis_status"] == "succeeded"
    assert captured["timeout"] == 180.0
    assert captured["timeout"] > 0


def test_live_ollama_env_timeout_override_is_honored(monkeypatch: Any) -> None:
    """T015F: ``OMI_LIVE_OLLAMA_TIMEOUT_SECONDS=240`` uses 240-second timeout."""
    _mock_live_ollama_env(monkeypatch)
    monkeypatch.setenv("OMI_LIVE_OLLAMA_TIMEOUT_SECONDS", "240")
    captured: dict[str, Any] = {}

    def capture_urlopen(request: Any, *args: Any, **kwargs: Any) -> _MockResponse:
        captured["timeout"] = kwargs.get("timeout", args[0] if args else None)
        return _MockResponse(
            _valid_ollama_chat_response(_valid_live_model_content())
        )

    monkeypatch.setattr(urllib.request, "urlopen", capture_urlopen)
    result = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        RAW_IDEA,
        requested_adapters=["ollama_model"],
        persist_candidates=False,
    )
    assert result["analysis_status"] == "succeeded"
    assert captured["timeout"] == 240.0


def test_live_ollama_invalid_timeout_falls_back_to_default(monkeypatch: Any) -> None:
    """T015F: invalid timeout values fall back to the safe 180s default.

    Non-numeric, zero, negative, blank, and out-of-range values all
    fall back to the default. The HTTP call always uses a finite,
    positive timeout — never ``None`` (infinite) and never
    zero/negative.
    """
    invalid_values = (
        "abc",  # non-numeric
        "",  # blank
        "0",  # zero
        "-1",  # negative
        "0.0",  # zero float
        "-3.5",  # negative float
        "99999",  # above max
        "inf",  # infinity-like
        "nan",  # NaN-like
    )
    for bad_value in invalid_values:
        monkeypatch.setenv("OMI_LIVE_TOOLS_ENABLED", "true")
        monkeypatch.setenv("OMI_LIVE_OLLAMA_ENABLED", "true")
        monkeypatch.setenv("OMI_LIVE_OLLAMA_TIMEOUT_SECONDS", bad_value)
        captured: dict[str, Any] = {}

        def capture_urlopen(
            request: Any, *args: Any, **kwargs: Any
        ) -> _MockResponse:
            captured["timeout"] = kwargs.get(
                "timeout", args[0] if args else None
            )
            return _MockResponse(
                _valid_ollama_chat_response(_valid_live_model_content())
            )

        monkeypatch.setattr(urllib.request, "urlopen", capture_urlopen)
        result = oao.analyze_omi_raw_idea_with_tools(
            "demo",
            RAW_IDEA,
            requested_adapters=["ollama_model"],
            persist_candidates=False,
        )
        assert result["analysis_status"] == "succeeded", (
            f"unexpected fail_closed for invalid timeout value {bad_value!r}"
        )
        assert captured["timeout"] == 180.0, (
            f"invalid timeout {bad_value!r} should fall back to 180s, "
            f"got {captured['timeout']!r}"
        )
        # Cleanup
        monkeypatch.delenv("OMI_LIVE_OLLAMA_TIMEOUT_SECONDS", raising=False)


def test_live_ollama_missing_timeout_uses_default(monkeypatch: Any) -> None:
    """T015F: missing ``OMI_LIVE_OLLAMA_TIMEOUT_SECONDS`` uses 180s default."""
    _mock_live_ollama_env(monkeypatch)
    monkeypatch.delenv("OMI_LIVE_OLLAMA_TIMEOUT_SECONDS", raising=False)
    captured: dict[str, Any] = {}

    def capture_urlopen(request: Any, *args: Any, **kwargs: Any) -> _MockResponse:
        captured["timeout"] = kwargs.get("timeout", args[0] if args else None)
        return _MockResponse(
            _valid_ollama_chat_response(_valid_live_model_content())
        )

    monkeypatch.setattr(urllib.request, "urlopen", capture_urlopen)
    result = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        RAW_IDEA,
        requested_adapters=["ollama_model"],
        persist_candidates=False,
    )
    assert result["analysis_status"] == "succeeded"
    assert captured["timeout"] == 180.0


def test_live_ollama_think_false_preserved_in_request_payload(
    monkeypatch: Any,
) -> None:
    """T015F: T015E ``think: false`` is preserved in the live request payload.

    The T015E Qwen3 thinking-mode fix remains intact: top-level
    ``think: false``, ``stream: false``, and ``options.num_predict``
    continue to be sent on the ``/api/chat`` request body.
    """
    _mock_live_ollama_env(monkeypatch)
    monkeypatch.setenv("OMI_LIVE_OLLAMA_TIMEOUT_SECONDS", "300")
    bodies: list[bytes] = []

    def capture_urlopen(request: Any, *args: Any, **kwargs: Any) -> _MockResponse:
        bodies.append(request.data)
        return _MockResponse(
            _valid_ollama_chat_response(_valid_live_model_content())
        )

    monkeypatch.setattr(urllib.request, "urlopen", capture_urlopen)
    result = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        RAW_IDEA,
        requested_adapters=["ollama_model"],
        persist_candidates=False,
    )
    assert result["analysis_status"] == "succeeded"
    assert len(bodies) == 1
    sent_body = json.loads(bodies[0].decode("utf-8"))
    assert sent_body.get("think") is False
    assert sent_body.get("stream") is False
    assert sent_body.get("model") == "qwen3:8b"
    assert sent_body.get("options", {}).get("num_predict") == 2048


def test_live_ollama_accepts_owner_prose_input(monkeypatch: Any) -> None:
    """T015F: owner-authored prose input is accepted by the live Ollama path.

    A 35+ word owner-authored raw idea that ends with a period and
    triggers ``is_prose_like_text`` is no longer rejected at the
    orchestrator entrypoint. The live Ollama adapter receives the text
    as the user message and the model analyzes it. With a mocked
    ``/api/chat`` response, the orchestrator produces normalized
    findings.
    """
    # Sanity check: the prose input is long, ends with a period, and
    # would have been blocked by the pre-T015F prose guard.
    assert len(_OWNER_PROSE_IDEA.split()) >= 35
    assert _OWNER_PROSE_IDEA.endswith(".")
    assert oao.is_prose_like_text(_OWNER_PROSE_IDEA)

    _mock_live_ollama_env(monkeypatch)
    monkeypatch.setenv("OMI_LIVE_OLLAMA_TIMEOUT_SECONDS", "180")
    _mock_urlopen(
        monkeypatch,
        _valid_ollama_chat_response(
            _valid_live_model_content(source=_OWNER_PROSE_IDEA)
        ),
    )

    result = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        _OWNER_PROSE_IDEA,
        requested_adapters=["ollama_model"],
        persist_candidates=False,
    )

    # No raw-idea prose-guard failure in the explanation.
    assert "raw idea text looks like story prose" not in (
        result["explanation"].lower()
    )
    assert "raw idea text resembles story prose" not in (
        result["explanation"].lower()
    )

    # Mocked valid model content produces a normalized finding.
    assert result["analysis_status"] == "succeeded"
    assert len(result["findings"]) == 1
    finding = result["findings"][0]
    assert finding["source_adapter"] == "ollama_model"
    assert result["persisted_candidate_ids"] == []


def test_live_ollama_model_prose_output_still_fails_closed(
    monkeypatch: Any,
) -> None:
    """T015F: AI/tool/model prose-shape output still fails closed.

    A live Ollama response whose ``message.content`` envelope contains
    a prose-shaped ``extracted_claim`` is rejected by the strict
    envelope validator. Findings list stays empty, no candidate
    persistence is invoked.
    """
    _mock_live_ollama_env(monkeypatch)
    prose_content = (
        "Meanwhile the room grew dark and the rain hammered the windows "
        "and the candles flickered one by one down the long hallway."
    )
    _mock_urlopen(
        monkeypatch,
        _valid_ollama_chat_response(
            json.dumps({
                "schema_version": oao.OMI_OLLAMA_SCHEMA_VERSION,
                "adapter": "ollama_model",
                "status": "succeeded",
                "findings": [
                    {
                        "candidate_type": "character",
                        "label": "Room",
                        "extracted_claim": prose_content,
                            "evidence": _first_live_span_evidence(),
                    }
                ],
            })
        ),
    )

    result = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        RAW_IDEA,
        requested_adapters=["ollama_model"],
        persist_candidates=False,
    )
    env = _assert_ollama_failed_closed(result)
    assert "prose" in env["explanation"].lower()
    assert result["persisted_candidate_ids"] == []


def test_live_ollama_model_unsafe_truth_output_still_fails_closed(
    monkeypatch: Any,
) -> None:
    """T015F: AI/tool/model truth/canon/approval output still fails closed.

    The truth-label guard on model output is preserved. ``support_label``
    values containing ``canon``, ``truth``, ``approved``, or ``promoted``
    cause the envelope validator to reject the response with no
    findings.
    """
    _mock_live_ollama_env(monkeypatch)
    _mock_urlopen(
        monkeypatch,
        _valid_ollama_chat_response(
            json.dumps({
                "schema_version": oao.OMI_OLLAMA_SCHEMA_VERSION,
                "adapter": "ollama_model",
                "status": "succeeded",
                "findings": [
                    {
                        "candidate_type": "character",
                        "label": "Test",
                        "extracted_claim": (
                            "Test is a confirmed canonical fact"
                        ),
                            "evidence": _first_live_span_evidence(),
                            "support_label": "canon truth support",
                    }
                ],
            })
        ),
    )

    result = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        RAW_IDEA,
        requested_adapters=["ollama_model"],
        persist_candidates=False,
    )
    env = _assert_ollama_failed_closed(result)
    assert "truth" in env["explanation"].lower() or "canon" in (
        env["explanation"].lower()
    )
    assert result["persisted_candidate_ids"] == []


def test_live_ollama_persistence_boundary_remains_safe(monkeypatch: Any) -> None:
    """T015F: persist_candidates=False is honored; no candidate persistence.

    With a mocked valid model response, ``persist_candidates=False``
    never invokes candidate persistence. The orchestrator returns
    ``persisted_candidate_ids == []`` and ``persistence_status ==
    "not_requested"`` even when findings are produced.
    """
    _mock_live_ollama_env(monkeypatch)
    monkeypatch.setenv("OMI_LIVE_OLLAMA_TIMEOUT_SECONDS", "180")
    _mock_urlopen(
        monkeypatch,
        _valid_ollama_chat_response(_valid_live_model_content()),
    )
    result = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        RAW_IDEA,
        requested_adapters=["ollama_model"],
        persist_candidates=False,
    )
    assert result["analysis_status"] == "succeeded"
    assert len(result["findings"]) == 1
    assert result["persisted_candidate_ids"] == []
    assert result["persistence_status"] == "not_requested"
