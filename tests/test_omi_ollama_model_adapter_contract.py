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


def _valid_live_model_content() -> str:
    """Build a valid JSON string that passes validate_ollama_model_envelope."""
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
                        "source_excerpt": (
                            "Owner note names Test Character Alpha as "
                            "the library investigator."
                        ),
                        "source_locator": "raw_idea:L1:C0-78",
                    }
                ],
                "source_locator": "raw_idea:L1:C0-78",
                "support_label": "ollama model support strength only",
            }
        ],
    })


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
                        "evidence": [
                            {
                                "source_excerpt": "the room grew dark",
                                "source_locator": "raw_idea:L1:C0-20",
                            }
                        ],
                        "source_locator": "raw_idea:L1:C0-20",
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
                        "evidence": [
                            {
                                "source_excerpt": "test",
                                "source_locator": "raw_idea:L1:C0-5",
                            }
                        ],
                        "source_locator": "raw_idea:L1:C0-5",
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
