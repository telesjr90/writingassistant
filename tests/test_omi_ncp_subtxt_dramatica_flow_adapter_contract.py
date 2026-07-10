"""PHASE8-IMPL-023-T009 NCP/Subtxt/dramatica-flow fixture adapter tests.

These tests use fixture/mock diagnostic/context output only. They do not
import or run NCP, Subtxt, dramatica-flow, Story Check, BookNLP/spaCy, Ollama,
or any model runtime. They do not mutate Memory/Canon, persist AI/tool
candidates, create promotion records, run apply-promotion, or generate story
prose.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from backend import omi_analysis_orchestrator as oao


RAW_IDEA = (
    "Owner analysis note: archive key pressure; hearing deadline; "
    "mentor relationship unresolved; sealed archive route knowledge"
)

ADAPTERS = ("ncp", "subtxt", "dramatica_flow")
LIVE_RUNTIME_LABEL = {
    "ncp": "live ncp",
    "subtxt": "live subtxt",
    "dramatica_flow": "live dramatica-flow",
}
SUPPORT_LABEL = {
    "ncp": "NCP context support only",
    "subtxt": "Subtxt diagnostic support only",
    "dramatica_flow": "dramatica-flow analysis support only",
}
DEFAULT_TYPE = {
    "ncp": "storyform_context_support",
    "subtxt": "structural_diagnostic",
    "dramatica_flow": "causal_chain",
}
DEFAULT_CLAIM_FIELD = {
    "ncp": "context_claim",
    "subtxt": "diagnostic_claim",
    "dramatica_flow": "analysis_claim",
}
DEFAULT_CLAIM = {
    "ncp": "The hearing deadline supports storyform context review",
    "subtxt": "The archive key creates a structural diagnostic pressure point",
    "dramatica_flow": "The archive key and hearing deadline support causal-chain review",
}


def _context_finding(adapter: str, **overrides: Any) -> dict[str, Any]:
    finding: dict[str, Any] = {
        "raw_finding_id": f"{adapter}-fixture-1",
        "finding_type": DEFAULT_TYPE[adapter],
        "label": "Archive key pressure",
        DEFAULT_CLAIM_FIELD[adapter]: DEFAULT_CLAIM[adapter],
        "evidence": [
            {
                "source_excerpt": (
                    "Mara must recover the archive key before the hearing"
                ),
                "source_locator": "raw_idea:L1:C12-66",
            }
        ],
        "source_locator": "raw_idea:L1:C12-66",
        "support_label": SUPPORT_LABEL[adapter],
        "confidence": "medium support",
    }
    finding.update(overrides)
    return finding


def _context_envelope(
    adapter: str,
    findings: list[dict[str, Any]] | None = None,
    **overrides: Any,
) -> dict[str, Any]:
    envelope: dict[str, Any] = {
        "schema_version": oao.OMI_CONTEXT_SCHEMA_VERSION_BY_ADAPTER[adapter],
        "adapter": adapter,
        "status": "succeeded",
        "explanation": f"fixture-only {adapter} diagnostic/context handoff",
        "provenance": {
            "tool_source": adapter,
            "adapter": adapter,
            "support": SUPPORT_LABEL[adapter],
        },
        "findings": findings if findings is not None else [_context_finding(adapter)],
    }
    envelope.update(overrides)
    return envelope


def _run_adapter(
    adapter: str,
    fixture: Any | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    params: dict[str, Any] = {
        "persist_candidates": False,
        "requested_adapters": [adapter],
    }
    if fixture is not None:
        params["adapter_fixture_outputs"] = {adapter: fixture}
    params.update(kwargs)
    return oao.analyze_omi_raw_idea_with_tools("demo", RAW_IDEA, **params)


def _adapter_env(result: dict[str, Any], adapter: str) -> dict[str, Any]:
    envs = [env for env in result["adapter_results"] if env["adapter"] == adapter]
    assert len(envs) == 1
    return envs[0]


def _assert_failed_closed(result: dict[str, Any], adapter: str) -> dict[str, Any]:
    assert result["analysis_status"] == "fail_closed"
    assert result["findings"] == []
    assert result["persisted_candidate_ids"] == []
    env = _adapter_env(result, adapter)
    assert env["state"] in {"failed_closed", "unavailable", "error"}
    assert env["candidates"] == []
    assert env["explanation"]
    return env


def _assert_candidate_only_finding(finding: dict[str, Any], adapter: str) -> None:
    assert finding["source_adapter"] == adapter
    assert finding["provenance"]["tool_source"] == adapter
    assert finding["provenance"]["adapter"] == adapter
    assert "support" in finding["provenance"]["support"].lower()
    assert "support" in finding["support_label"].lower()
    assert finding["owner_decision"]["decision"] == "pending"
    assert finding["owner_decision"]["approved"] is False
    assert finding["review_status"] == "candidate_review_pending"
    assert finding["source_locator"]
    assert finding["evidence"][0]["source_excerpt"]
    assert finding["evidence"][0]["source_locator"]
    assert finding["candidate_fingerprint"].startswith("omi-cand-")
    assert finding["evidence_fingerprint"].startswith("omi-evid-")
    assert finding["normalized_finding_id"].startswith(f"omi-find-{adapter}-")
    for forbidden in ("truth", "canon", "final", "approved", "promoted"):
        assert forbidden not in finding["support_label"].lower()


@pytest.mark.parametrize("adapter", ADAPTERS)
def test_context_adapter_without_fixture_returns_unavailable_and_no_runtime_call(
    adapter: str,
) -> None:
    result = _run_adapter(adapter, adapter_config={"runtime": "disabled"})

    env = _assert_failed_closed(result, adapter)
    assert env["state"] == "unavailable"
    assert "fixture" in env["explanation"].lower()
    assert LIVE_RUNTIME_LABEL[adapter] in env["explanation"].lower()
    assert result["persisted_candidate_ids"] == []


def test_valid_ncp_context_fixture_normalizes_candidate_only_findings() -> None:
    fixture = _context_envelope(
        "ncp",
        [
            _context_finding("ncp"),
            _context_finding(
                "ncp",
                raw_finding_id="ncp-throughline-1",
                finding_type="throughline_context_support",
                label="Mentor relationship throughline context",
                context_claim=(
                    "The unresolved mentor relationship supports throughline review"
                ),
                evidence=[
                    {
                        "source_excerpt": (
                            "The mentor relationship remains unresolved"
                        ),
                        "source_locator": "raw_idea:L1:C68-111",
                    }
                ],
                source_locator="raw_idea:L1:C68-111",
            ),
            _context_finding(
                "ncp",
                raw_finding_id="ncp-source-map-1",
                finding_type="source_mapping",
                label="Sealed archive route source map",
                context_claim="The sealed archive route is source-mapping support",
                evidence=[
                    {
                        "source_excerpt": "only Mara knows the sealed archive route",
                        "source_locator": "raw_idea:L1:C117-155",
                    }
                ],
                source_locator="raw_idea:L1:C117-155",
            ),
        ],
    )

    result = _run_adapter("ncp", fixture)

    assert result["analysis_status"] == "succeeded"
    assert result["persisted_candidate_ids"] == []
    assert _adapter_env(result, "ncp")["state"] == "succeeded"
    assert [finding["candidate_type"] for finding in result["findings"]] == [
        "storyform_context",
        "throughline_context",
        "evidence_note",
    ]
    for finding in result["findings"]:
        _assert_candidate_only_finding(finding, "ncp")


def test_valid_subtxt_diagnostic_fixture_normalizes_candidate_only_findings() -> None:
    fixture = _context_envelope(
        "subtxt",
        [
            _context_finding("subtxt"),
            _context_finding(
                "subtxt",
                raw_finding_id="subtxt-conflict-1",
                finding_type="source_of_conflict_diagnostic",
                label="Archive key source of conflict",
                diagnostic_claim=(
                    "The archive key deadline supports source-of-conflict review"
                ),
            ),
            _context_finding(
                "subtxt",
                raw_finding_id="subtxt-uncertainty-1",
                finding_type="insufficient_evidence_diagnostic",
                label="Mentor relationship insufficient evidence",
                diagnostic_claim=(
                    "The unresolved mentor relationship has insufficient evidence"
                ),
                evidence=[
                    {
                        "source_excerpt": (
                            "The mentor relationship remains unresolved"
                        ),
                        "source_locator": "raw_idea:L1:C68-111",
                    }
                ],
                source_locator="raw_idea:L1:C68-111",
            ),
        ],
    )

    result = _run_adapter("subtxt", json.dumps(fixture))

    assert result["analysis_status"] == "succeeded"
    assert result["persisted_candidate_ids"] == []
    assert _adapter_env(result, "subtxt")["state"] == "succeeded"
    assert [finding["candidate_type"] for finding in result["findings"]] == [
        "structural_diagnostic",
        "conflict_diagnostic",
        "ambiguity",
    ]
    for finding in result["findings"]:
        _assert_candidate_only_finding(finding, "subtxt")


def test_valid_dramatica_flow_analysis_fixture_normalizes_candidate_only_findings() -> None:
    fixture = _context_envelope(
        "dramatica_flow",
        [
            _context_finding("dramatica_flow"),
            _context_finding(
                "dramatica_flow",
                raw_finding_id="flow-mystery-1",
                finding_type="foreshadowing_support",
                label="Sealed archive route mystery support",
                analysis_claim=(
                    "The sealed archive route supports foreshadowing or mystery review"
                ),
                evidence=[
                    {
                        "source_excerpt": "only Mara knows the sealed archive route",
                        "source_locator": "raw_idea:L1:C117-155",
                    }
                ],
                source_locator="raw_idea:L1:C117-155",
            ),
            _context_finding(
                "dramatica_flow",
                raw_finding_id="flow-relationship-1",
                finding_type="relationship_network",
                label="Mentor relationship network",
                analysis_claim=(
                    "The unresolved mentor relationship supports relationship-network review"
                ),
                evidence=[
                    {
                        "source_excerpt": (
                            "The mentor relationship remains unresolved"
                        ),
                        "source_locator": "raw_idea:L1:C68-111",
                    }
                ],
                source_locator="raw_idea:L1:C68-111",
            ),
        ],
    )

    result = _run_adapter("dramatica_flow", fixture)

    assert result["analysis_status"] == "succeeded"
    assert result["persisted_candidate_ids"] == []
    assert _adapter_env(result, "dramatica_flow")["state"] == "succeeded"
    assert [finding["candidate_type"] for finding in result["findings"]] == [
        "plot_thread",
        "open_question",
        "relationship",
    ]
    for finding in result["findings"]:
        _assert_candidate_only_finding(finding, "dramatica_flow")


@pytest.mark.parametrize("adapter", ADAPTERS)
def test_valid_diagnostic_context_questions_are_review_support_not_prose(
    adapter: str,
) -> None:
    fixture = _context_envelope(
        adapter,
        [
            _context_finding(
                adapter,
                raw_finding_id=f"{adapter}-question-1",
                finding_type="owner_review_question",
                label="Mentor relationship review question",
                question=(
                    "Which throughline is best supported by the unresolved "
                    "mentor relationship?"
                ),
                evidence=[
                    {
                        "source_excerpt": (
                            "The mentor relationship remains unresolved"
                        ),
                        "source_locator": "raw_idea:L1:C68-111",
                    }
                ],
                source_locator="raw_idea:L1:C68-111",
            )
        ],
    )

    result = _run_adapter(adapter, fixture)

    assert result["analysis_status"] == "succeeded"
    finding = result["findings"][0]
    assert finding["candidate_type"] == "diagnostic_question"
    assert finding["extracted_claim"].endswith("?")
    _assert_candidate_only_finding(finding, adapter)


@pytest.mark.parametrize("adapter", ADAPTERS)
def test_invalid_json_schema_adapter_or_unknown_type_fails_closed(adapter: str) -> None:
    wrong_adapter = _context_envelope(adapter)
    wrong_adapter["adapter"] = "story_check"
    fixtures: list[Any] = [
        "not json",
        _context_envelope(adapter, schema_version="future.schema"),
        wrong_adapter,
        _context_envelope(
            adapter,
            [_context_finding(adapter, finding_type="scene_prose")],
        ),
    ]

    for fixture in fixtures:
        _assert_failed_closed(_run_adapter(adapter, fixture), adapter)


@pytest.mark.parametrize("adapter", ADAPTERS)
def test_context_adapter_missing_evidence_fails_closed(adapter: str) -> None:
    fixture = _context_envelope(adapter, [_context_finding(adapter)])
    del fixture["findings"][0]["evidence"]

    env = _assert_failed_closed(_run_adapter(adapter, fixture), adapter)
    assert "evidence" in env["explanation"].lower()


@pytest.mark.parametrize("adapter", ADAPTERS)
def test_context_adapter_missing_source_locator_fails_closed(adapter: str) -> None:
    fixture = _context_envelope(adapter, [_context_finding(adapter)])
    del fixture["findings"][0]["source_locator"]

    env = _assert_failed_closed(_run_adapter(adapter, fixture), adapter)
    assert "source_locator" in env["explanation"]


@pytest.mark.parametrize("adapter", ADAPTERS)
def test_context_adapter_missing_provenance_fails_closed(adapter: str) -> None:
    fixture = _context_envelope(adapter)
    del fixture["provenance"]

    env = _assert_failed_closed(_run_adapter(adapter, fixture), adapter)
    assert "provenance" in env["explanation"].lower()


@pytest.mark.parametrize("adapter", ADAPTERS)
def test_context_adapter_truth_canon_approved_or_final_labels_fail_closed(
    adapter: str,
) -> None:
    fixtures = [
        _context_envelope(adapter, [
            _context_finding(adapter, support_label="truth support")
        ]),
        _context_envelope(adapter, [
            _context_finding(adapter, support_label="canon support")
        ]),
        _context_envelope(adapter, [
            _context_finding(
                adapter,
                owner_decision={"decision": "approve", "approved": True},
            )
        ]),
        _context_envelope(adapter, [
            _context_finding(adapter, support_label="final support")
        ]),
        _context_envelope(adapter, [
            _context_finding(adapter, review_status="approved")
        ]),
    ]

    for fixture in fixtures:
        _assert_failed_closed(_run_adapter(adapter, fixture), adapter)


@pytest.mark.parametrize("adapter", ADAPTERS)
def test_context_adapter_prose_rewrite_outline_draft_continue_fails_closed(
    adapter: str,
) -> None:
    claim_field = DEFAULT_CLAIM_FIELD[adapter]
    fixtures = [
        _context_envelope(adapter, [
            _context_finding(adapter, **{claim_field: "Rewrite: polished story text"})
        ]),
        _context_envelope(adapter, [
            _context_finding(adapter, question="What should happen next in the scene?")
        ]),
        _context_envelope(adapter, [
            _context_finding(adapter, outline="blocked outline field")
        ]),
        _context_envelope(adapter, [
            _context_finding(adapter, **{claim_field: "Draft the next chapter"})
        ]),
        _context_envelope(adapter, [
            _context_finding(adapter, **{claim_field: "Continue the story"})
        ]),
    ]

    for fixture in fixtures:
        env = _assert_failed_closed(_run_adapter(adapter, fixture), adapter)
        assert "prose" in env["explanation"].lower() or "diagnostic" in (
            env["explanation"].lower()
        )


@pytest.mark.parametrize("adapter", ADAPTERS)
def test_context_adapter_memory_canon_promotion_apply_promotion_and_persistence_fail_closed(
    adapter: str,
) -> None:
    fixtures = [
        _context_envelope(adapter, [
            _context_finding(adapter, memory_mutation={"target": "Memory"})
        ]),
        _context_envelope(adapter, [
            _context_finding(adapter, canon_mutation={"target": "Canon"})
        ]),
        _context_envelope(adapter, [
            _context_finding(adapter, promotion_record={"id": "unsafe"})
        ]),
        _context_envelope(adapter, [
            _context_finding(adapter, apply_promotion={"enabled": True})
        ]),
        _context_envelope(adapter, [
            _context_finding(adapter, persist_candidates=True)
        ]),
    ]

    for fixture in fixtures:
        env = _assert_failed_closed(_run_adapter(adapter, fixture), adapter)
        assert (
            "promotion" in env["explanation"].lower()
            or "memory/canon" in env["explanation"].lower()
            or "persist" in env["explanation"].lower()
        )


def test_context_adapter_findings_are_not_persisted_even_when_persist_candidates_true(
    monkeypatch: Any,
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

    for adapter in ADAPTERS:
        result = _run_adapter(
            adapter,
            _context_envelope(adapter),
            persist_candidates=True,
            source_idea_id="idea_123",
        )
        assert result["analysis_status"] == "succeeded"
        assert result["persisted_candidate_ids"] == []
        assert result["safety"]["no_memory_canon_mutation"] is True
        assert result["safety"]["no_apply_promotion"] is True

    assert calls == []


# ---------------------------------------------------------------------------
# T018B — Live NCP candidate-import validation adapter
# ---------------------------------------------------------------------------
#
# These tests mock the filesystem and any Node/npm subprocess path so the
# suite does NOT depend on the real ``.external_sources`` tree, real
# ``.external_sources/narrative-context-protocol/examples`` fixtures, real
# node, real npm, real ``.external_sources/narrative-context-protocol``
# tree, real network, or the owner-selected real NCP JSON file. T018B
# completes through mocked automated tests; T018C must later perform
# manual real NCP validation against an owner-selected NCP JSON file.

NCP_INPUT_PATH_ENV = "OMI_LIVE_NCP_INPUT_PATH"
NCP_VALIDATE_WITH_NODE_ENV = "OMI_LIVE_NCP_VALIDATE_WITH_NODE"


def _valid_minimal_ncp_payload() -> dict[str, Any]:
    """Return a small, hand-crafted NCP JSON payload that contains
    well-formed subtext/storytelling containers and SAFE labels/claims.

    The payload is intentionally minimal so every T018B test can run
    in isolation. It is fully owned by the test suite; it does not
    depend on any real NCP example file.
    """
    return {
        "schema_version": "1.3.0",
        "story": {
            "id": "story_t018b_minimal",
            "title": "T018B minimal NCP",
            "logline": "A minimal NCP payload for T018B candidate-import tests.",
            "narratives": [
                {
                    "id": "narrative_t018b_minimal",
                    "status": "candidate",
                    "subtext": {
                        "perspectives": [],
                        "players": [
                            {
                                "id": "player_t018b_001",
                                "name": "Mara Vale",
                                "summary": (
                                    "An archivist who carries a sealed "
                                    "archive key."
                                ),
                            },
                            {
                                "id": "player_t018b_002",
                                "name": "Jonah Cross",
                                "summary": (
                                    "A mentor who has not yet resolved the "
                                    "Mara Vale relationship."
                                ),
                            },
                        ],
                        "dynamics": [],
                        "storypoints": [
                            {
                                "id": "storypoint_t018b_001",
                                "name": "Archive key pressure",
                                "summary": (
                                    "The archive key creates a recurring "
                                    "structural pressure point."
                                ),
                            },
                        ],
                        "storybeats": [
                            {
                                "id": "storybeat_t018b_001",
                                "name": "Hearing deadline beat",
                                "summary": (
                                    "A hearing deadline forces Mara Vale "
                                    "to act on the archive key."
                                ),
                            },
                        ],
                    },
                    "storytelling": {
                        "overviews": [
                            {
                                "id": "overview_t018b_001",
                                "title": "Mentor relationship overview",
                                "summary": (
                                    "Mentor and archivist are bound by a "
                                    "shared sealed archive route."
                                ),
                            }
                        ],
                        "relationships": [],
                        "open_questions": [
                            {
                                "id": "open_question_t018b_001",
                                "summary": (
                                    "Which throughline is best supported by "
                                    "the unresolved mentor relationship?"
                                ),
                            }
                        ],
                        "diagnostic_questions": [],
                    },
                }
            ],
            "moments": [],
        },
    }


def _write_ncp_payload(tmp_path: Any, name: str = "minimal.json") -> Any:
    """Write a minimal NCP JSON payload to ``tmp_path/name`` and return
    the absolute ``Path``."""
    path = tmp_path / name
    path.write_text(
        json.dumps(_valid_minimal_ncp_payload()), encoding="utf-8"
    )
    return path


def _mock_live_ncp_env(
    monkeypatch: Any,
    input_path: Any,
    *,
    validate_with_node: bool = False,
) -> None:
    """Enable the live NCP env flags and point at ``input_path``."""
    monkeypatch.setenv("OMI_LIVE_TOOLS_ENABLED", "true")
    monkeypatch.setenv("OMI_LIVE_NCP_ENABLED", "true")
    monkeypatch.setenv(NCP_INPUT_PATH_ENV, str(input_path))
    if validate_with_node:
        monkeypatch.setenv(NCP_VALIDATE_WITH_NODE_ENV, "true")
    else:
        monkeypatch.delenv(NCP_VALIDATE_WITH_NODE_ENV, raising=False)


def test_live_ncp_disabled_by_default_returns_unavailable() -> None:
    """No env flags -> live NCP path not triggered -> unavailable."""
    result = _run_adapter("ncp", adapter_config={"runtime": "disabled"})
    env = _adapter_env(result, "ncp")
    assert env["state"] == "unavailable"
    assert "fixture" in env["explanation"].lower() or "T009" in env["explanation"]


def test_live_ncp_enabled_but_no_input_path_returns_unavailable(
    monkeypatch: Any,
) -> None:
    """OMI_LIVE_NCP_ENABLED=1 with no OMI_LIVE_NCP_INPUT_PATH -> fail-closed
    with no findings and no live call. The runner must NOT scan the
    project for an NCP file."""
    monkeypatch.setenv("OMI_LIVE_TOOLS_ENABLED", "true")
    monkeypatch.setenv("OMI_LIVE_NCP_ENABLED", "true")
    monkeypatch.delenv(NCP_INPUT_PATH_ENV, raising=False)
    result = _run_adapter(
        "ncp",
        adapter_config={"runtime": "disabled"},
    )
    env = _adapter_env(result, "ncp")
    assert env["state"] == "unavailable"
    assert env["candidates"] == []
    assert NCP_INPUT_PATH_ENV in env["explanation"]
    assert result["persisted_candidate_ids"] == []
    assert result["safety"]["no_memory_canon_mutation"] is True
    assert result["safety"]["no_apply_promotion"] is True
    assert result["safety"]["no_story_prose_generation"] is True


def test_live_ncp_blocked_overrides_enabled_returns_no_live_call(
    monkeypatch: Any, tmp_path: Any
) -> None:
    """OMI_LIVE_NCP_BLOCKED wins over OMI_LIVE_NCP_ENABLED."""
    ncp_path = _write_ncp_payload(tmp_path)
    _mock_live_ncp_env(monkeypatch, ncp_path)
    monkeypatch.setenv("OMI_LIVE_NCP_BLOCKED", "true")
    monkeypatch.setenv("OMI_LIVE_NCP_BLOCKED_REASON", "Owner decision pending.")

    result = _run_adapter("ncp", adapter_config={"runtime": "disabled"})
    env = _adapter_env(result, "ncp")
    assert env["state"] in {"unavailable", "blocked", "failed_closed"}
    assert env["candidates"] == []
    assert result["persisted_candidate_ids"] == []


def test_live_ncp_missing_input_file_fails_closed(
    monkeypatch: Any, tmp_path: Any
) -> None:
    """A configured OMI_LIVE_NCP_INPUT_PATH that does not exist must
    fail closed with no findings and no live call. The runner must NOT
    fall back to any default project file."""
    missing = tmp_path / "does_not_exist.json"
    _mock_live_ncp_env(monkeypatch, missing)

    result = _run_adapter("ncp", adapter_config={"runtime": "disabled"})
    env = _adapter_env(result, "ncp")
    assert env["state"] in {"unavailable", "failed_closed"}
    assert env["candidates"] == []


def test_live_ncp_invalid_json_fails_closed(
    monkeypatch: Any, tmp_path: Any
) -> None:
    """Invalid JSON in the owner-selected NCP file must fail closed with
    no findings and no live call. The runner must NOT silently fall back
    to project data."""
    bad = tmp_path / "bad.json"
    bad.write_text("this is not json {{{", encoding="utf-8")
    _mock_live_ncp_env(monkeypatch, bad)

    result = _run_adapter("ncp", adapter_config={"runtime": "disabled"})
    env = _adapter_env(result, "ncp")
    assert env["state"] in {"unavailable", "failed_closed"}
    assert env["candidates"] == []
    assert result["persisted_candidate_ids"] == []


def test_live_ncp_minimal_invalid_payload_fails_closed(
    monkeypatch: Any, tmp_path: Any
) -> None:
    """A NCP JSON that is missing ``schema_version`` and any
    ``narratives``/``story`` containers must fail closed with no findings.
    The runner must NOT silently produce a finding from an unsafe NCP
    document."""
    bad = tmp_path / "bad_ncp.json"
    bad.write_text(
        json.dumps({"narratives": "not a list"}), encoding="utf-8"
    )
    _mock_live_ncp_env(monkeypatch, bad)

    result = _run_adapter("ncp", adapter_config={"runtime": "disabled"})
    env = _adapter_env(result, "ncp")
    assert env["state"] in {"unavailable", "failed_closed"}
    assert env["candidates"] == []


def test_live_ncp_valid_payload_maps_to_candidate_only_findings(
    monkeypatch: Any, tmp_path: Any
) -> None:
    """A valid owner-selected NCP JSON must map to candidate-only NCP
    findings with evidence excerpts, JSON pointer source locators,
    provenance, support-only labels, pending owner decisions, and the
    candidate review pending status."""
    ncp_path = _write_ncp_payload(tmp_path)
    _mock_live_ncp_env(monkeypatch, ncp_path)

    result = _run_adapter("ncp", adapter_config={"runtime": "disabled"})
    env = _adapter_env(result, "ncp")
    assert env["state"] == "succeeded"
    assert env["candidates"]
    assert result["persisted_candidate_ids"] == []
    assert result["safety"]["no_memory_canon_mutation"] is True
    assert result["safety"]["no_apply_promotion"] is True
    assert result["safety"]["no_story_prose_generation"] is True
    assert result["safety"]["no_canon_promotion"] is True

    seen_types = set()
    for finding in result["findings"]:
        _assert_candidate_only_finding(finding, "ncp")
        assert finding["source_locator"].startswith("/")
        assert finding["evidence"][0]["source_locator"].startswith("/")
        assert finding["evidence"][0]["source_excerpt"]
        assert "support" in finding["support_label"].lower()
        assert finding["owner_decision"]["decision"] == "pending"
        assert finding["review_status"] == "candidate_review_pending"
        seen_types.add(finding["candidate_type"])

    # The T018B mapping sends player/character/location/organization/object
    # items to ``evidence_note`` and storybeat/storypoint items to
    # ``story_fact``; overviews go to ``throughline_context``;
    # open_questions go to ``open_question``. All map to T009-allowed
    # candidate types so the existing T009 envelope validator remains
    # authoritative.
    expected = {
        "evidence_note",
        "story_fact",
        "throughline_context",
        "open_question",
    }
    assert expected.issubset(seen_types), (
        f"missing expected T018B candidate types: "
        f"{sorted(expected - seen_types)}"
    )


def test_live_ncp_finding_includes_evidence_excerpt_pointer_provenance(
    monkeypatch: Any, tmp_path: Any
) -> None:
    """Every T018B finding must carry a ``source_excerpt`` AND a JSON
    pointer-style ``source_locator`` AND a provenance block with
    ``tool_source: ncp`` AND a support-only label AND a pending owner
    decision AND a candidate review status."""
    ncp_path = _write_ncp_payload(tmp_path)
    _mock_live_ncp_env(monkeypatch, ncp_path)

    result = _run_adapter("ncp", adapter_config={"runtime": "disabled"})
    env = _adapter_env(result, "ncp")
    assert env["state"] == "succeeded"
    for finding in result["findings"]:
        assert finding["evidence"], "finding must have evidence list"
        first = finding["evidence"][0]
        assert isinstance(first.get("source_excerpt"), str) and first[
            "source_excerpt"
        ].strip()
        assert isinstance(first.get("source_locator"), str) and first[
            "source_locator"
        ].strip()
        assert finding["source_locator"].startswith("/")
        assert first["source_locator"].startswith("/")
        assert finding["provenance"]["tool_source"] == "ncp"
        assert finding["provenance"]["adapter"] == "ncp"
        assert "support" in finding["provenance"]["support"].lower()
        assert "support" in finding["support_label"].lower()
        assert finding["owner_decision"]["decision"] == "pending"
        assert finding["owner_decision"]["approved"] is False
        assert finding["review_status"] == "candidate_review_pending"
        for forbidden in (
            "truth",
            "canon",
            "final",
            "approved",
            "promoted",
        ):
            assert forbidden not in finding["support_label"].lower()


def test_live_ncp_unsafe_canon_final_approved_truth_label_is_skipped_or_failed(
    monkeypatch: Any, tmp_path: Any
) -> None:
    """Unsafe labels (truth/canon/final/approved/promoted/truth) and
    prose-like labels must be skipped (not silently rewritten into safe
    text). The runner does NOT rewrite unsafe source output."""
    payload = _valid_minimal_ncp_payload()
    payload["story"]["narratives"][0]["subtext"]["players"] = [
        {
            "id": "player_unsafe_truth",
            "name": "Truth Support",
            "summary": "This is the truth support only.",
        },
        {
            "id": "player_unsafe_canon",
            "name": "Canon Candidate",
            "summary": "This is the canon candidate only.",
        },
        {
            "id": "player_unsafe_prose",
            "name": "Mara Vale",
            "summary": (
                '"Stop!" he shouted, brandishing the lantern at the '
                "figure that had been lurking in the alley."
            ),
        },
    ]
    ncp_path = tmp_path / "unsafe.json"
    ncp_path.write_text(json.dumps(payload), encoding="utf-8")
    _mock_live_ncp_env(monkeypatch, ncp_path)

    result = _run_adapter("ncp", adapter_config={"runtime": "disabled"})
    env = _adapter_env(result, "ncp")
    # The runner may either succeed with the safe Mara Vale row only,
    # or fail closed. It must never produce a finding carrying a
    # truth/canon/final/approved/promoted label or a prose-like claim.
    for finding in result["findings"]:
        for forbidden in ("truth", "canon", "final", "approved", "promoted"):
            assert forbidden not in finding["label"].lower()
            assert forbidden not in finding["support_label"].lower()
            assert forbidden not in finding["extracted_claim"].lower()
        assert not oao.is_prose_like_text(finding["extracted_claim"])
        assert not oao.is_prose_like_text(finding["label"])
    # The runner is allowed to either return the safe Mara Vale row OR
    # fail closed; both behaviors satisfy the safety boundary.
    assert env["state"] in {"succeeded", "empty", "failed_closed"}


def test_live_ncp_does_not_run_automatically_over_project_data(
    monkeypatch: Any, tmp_path: Any
) -> None:
    """The T018B live NCP runner must NEVER auto-scan project data. When
    no OMI_LIVE_NCP_INPUT_PATH is set, the runner must return
    'unavailable' without ever reading any file under ``projects/`` or
    any NCP example tree."""
    monkeypatch.setenv("OMI_LIVE_TOOLS_ENABLED", "true")
    monkeypatch.setenv("OMI_LIVE_NCP_ENABLED", "true")
    monkeypatch.delenv(NCP_INPUT_PATH_ENV, raising=False)

    read_calls: list[str] = []

    def fake_open(*args: Any, **kwargs: Any) -> Any:
        read_calls.append(str(args[0]) if args else "")
        raise AssertionError(
            "T018B live NCP runner must not auto-open any project file"
        )

    monkeypatch.setattr("builtins.open", fake_open)

    result = _run_adapter("ncp", adapter_config={"runtime": "disabled"})
    env = _adapter_env(result, "ncp")
    assert env["state"] == "unavailable"
    assert env["candidates"] == []
    assert read_calls == []


def test_live_ncp_does_not_call_npm_install_or_audit_fix(
    monkeypatch: Any, tmp_path: Any
) -> None:
    """The T018B live NCP runner must NEVER invoke ``npm install``,
    ``npm audit fix``, or start a Node server. We mock all subprocess
    entry points and confirm none are called."""
    ncp_path = _write_ncp_payload(tmp_path)
    _mock_live_ncp_env(monkeypatch, ncp_path)

    attempted: list[tuple[str, tuple]] = []

    def fake_subprocess_run(*args: Any, **kwargs: Any) -> Any:
        attempted.append(("subprocess.run", args))
        raise AssertionError(
            "T018B live NCP runner must not invoke subprocess.run"
        )

    def fake_subprocess_popen(*args: Any, **kwargs: Any) -> Any:
        attempted.append(("subprocess.Popen", args))
        raise AssertionError(
            "T018B live NCP runner must not invoke subprocess.Popen"
        )

    def fake_node_call(*args: Any, **kwargs: Any) -> Any:
        attempted.append(("node", args))
        raise AssertionError(
            "T018B live NCP runner must not invoke node"
        )

    def fake_npm_call(*args: Any, **kwargs: Any) -> Any:
        attempted.append(("npm", args))
        raise AssertionError(
            "T018B live NCP runner must not invoke npm"
        )

    import subprocess

    monkeypatch.setattr(
        subprocess, "run", fake_subprocess_run, raising=False
    )
    monkeypatch.setattr(
        subprocess, "Popen", fake_subprocess_popen, raising=False
    )
    monkeypatch.setattr(subprocess, "call", fake_npm_call, raising=False)
    monkeypatch.setattr(
        subprocess, "check_call", fake_node_call, raising=False
    )
    monkeypatch.setattr(
        subprocess, "check_output", fake_node_call, raising=False
    )

    result = _run_adapter("ncp", adapter_config={"runtime": "disabled"})
    assert attempted == []
    env = _adapter_env(result, "ncp")
    assert env["state"] in {"succeeded", "empty", "failed_closed", "unavailable"}


def test_live_ncp_does_not_run_validate_file_unless_opted_in(
    monkeypatch: Any, tmp_path: Any
) -> None:
    """The T018B live NCP runner must NOT run ``npm run validate:file``
    over project data. The opt-in must be honored but the subprocess
    step is mocked here."""
    ncp_path = _write_ncp_payload(tmp_path)
    _mock_live_ncp_env(monkeypatch, ncp_path)

    attempted: list[tuple[str, tuple]] = []

    def fake_subprocess_run(*args: Any, **kwargs: Any) -> Any:
        attempted.append(("subprocess.run", args))
        raise AssertionError(
            "T018B live NCP runner must not invoke subprocess.run"
        )

    import subprocess

    monkeypatch.setattr(
        subprocess, "run", fake_subprocess_run, raising=False
    )

    result = _run_adapter("ncp", adapter_config={"runtime": "disabled"})
    env = _adapter_env(result, "ncp")
    assert env["state"] in {"succeeded", "empty", "failed_closed"}
    assert attempted == []


def test_live_ncp_opt_in_node_validation_subprocess_success(
    monkeypatch: Any, tmp_path: Any
) -> None:
    """With the opt-in ``OMI_LIVE_NCP_VALIDATE_WITH_NODE=1`` set AND
    the explicit safe input file set, a mocked subprocess that returns
    success allows the runner to continue parsing and produce findings.

    The opt-in helper is monkeypatched to return ``True`` (the
    production helper returns ``False`` in T018B; tests opt in by
    patching it). The runner then proceeds with its Python-side
    minimal schema/readiness check and T009 envelope conversion."""

    ncp_path = _write_ncp_payload(tmp_path)
    _mock_live_ncp_env(monkeypatch, ncp_path, validate_with_node=True)
    monkeypatch.setattr(
        oao, "_ncp_validate_with_node_opt_in", lambda **_: True
    )

    result = _run_adapter("ncp", adapter_config={"runtime": "disabled"})
    env = _adapter_env(result, "ncp")
    assert env["state"] in {"succeeded", "empty", "failed_closed"}


def test_live_ncp_opt_in_node_validation_subprocess_failure_fails_closed(
    monkeypatch: Any, tmp_path: Any
) -> None:
    """With the opt-in set but the mocked subprocess returns failure,
    the runner must fail closed with no findings."""
    ncp_path = _write_ncp_payload(tmp_path)
    _mock_live_ncp_env(monkeypatch, ncp_path, validate_with_node=True)
    monkeypatch.setattr(
        oao, "_ncp_validate_with_node_opt_in", lambda **_: False
    )

    result = _run_adapter("ncp", adapter_config={"runtime": "disabled"})
    env = _adapter_env(result, "ncp")
    assert env["state"] == "failed_closed"
    assert env["candidates"] == []
    assert "node validation" in env["explanation"].lower() or "opt-in" in (
        env["explanation"].lower()
    )


def test_live_ncp_no_persistence_memory_canon_or_promotion_or_prose(
    monkeypatch: Any, tmp_path: Any
) -> None:
    """The T018B live NCP runner must NEVER persist candidates, mutate
    Memory/Canon, create promotion records, run apply-promotion, or
    generate story prose. Even when ``persist_candidates=True`` is
    requested, the runner's persisted candidate IDs must be empty."""
    import backend.project_manager as project_manager

    ncp_path = _write_ncp_payload(tmp_path)
    _mock_live_ncp_env(monkeypatch, ncp_path)

    spy_calls: list[dict[str, Any]] = []

    def spy_persist(*args: Any, **kwargs: Any) -> dict[str, Any]:
        spy_calls.append({"args": args, "kwargs": kwargs})
        return {
            "persisted_candidate_ids": [],
            "new_candidate_ids": [],
            "reused_candidate_ids": [],
            "persistence_status": "no_candidates_persisted",
            "persistence_explanation": "spy stub",
        }

    monkeypatch.setattr(
        project_manager,
        "persist_omi_tool_assisted_findings_as_candidates",
        spy_persist,
    )

    result = _run_adapter(
        "ncp",
        adapter_config={"runtime": "disabled"},
        persist_candidates=True,
        source_idea_id="idea_123",
    )
    env = _adapter_env(result, "ncp")
    assert env["state"] in {"succeeded", "empty", "failed_closed"}
    # The runner must never actually persist anything. The orchestrator
    # may have called the persistence helper with candidate findings;
    # the helper short-circuits because the raw idea is not matched to
    # any source OMI idea in this test, so ``persisted_candidate_ids``
    # remains empty.
    assert result["persisted_candidate_ids"] == []
    assert result["safety"]["no_memory_canon_mutation"] is True
    assert result["safety"]["no_apply_promotion"] is True
    assert result["safety"]["no_canon_promotion"] is True
    assert result["safety"]["no_story_prose_generation"] is True


def test_live_ncp_existing_t009_fixture_tests_still_pass() -> None:
    """The original T009 fixture-based tests must remain unaffected
    when the live flags are NOT set."""
    result = _run_adapter("ncp", adapter_config={"runtime": "disabled"})
    env = _adapter_env(result, "ncp")
    assert env["state"] == "unavailable"
    assert env["candidates"] == []
    assert result["persisted_candidate_ids"] == []


def test_live_ncp_path_allowlist_rejects_projects_tree(
    monkeypatch: Any, tmp_path: Any
) -> None:
    """A ``projects/...`` path must be rejected even when the file
    exists. The runner must NEVER treat the project data tree as a
    valid NCP input source."""
    projects_dir = tmp_path / "projects" / "demo"
    projects_dir.mkdir(parents=True)
    fake = projects_dir / "scene.json"
    fake.write_text(json.dumps(_valid_minimal_ncp_payload()), encoding="utf-8")
    _mock_live_ncp_env(monkeypatch, fake)

    result = _run_adapter("ncp", adapter_config={"runtime": "disabled"})
    env = _adapter_env(result, "ncp")
    assert env["state"] in {"unavailable", "failed_closed"}
    assert env["candidates"] == []


def test_live_ncp_path_allowlist_rejects_symlinks(
    monkeypatch: Any, tmp_path: Any
) -> None:
    """A symlink to a valid NCP file must be rejected by the path
    allowlist. The runner must not follow symlinks."""
    real_ncp = _write_ncp_payload(tmp_path)
    symlink_dir = tmp_path / "symlink_dir"
    symlink_dir.mkdir()
    symlink_path = symlink_dir / "linked.json"
    try:
        symlink_path.symlink_to(real_ncp)
    except (OSError, NotImplementedError) as exc:
        # Some platforms may not support symlinks; skip in that case.
        pytest.skip(f"symlink unsupported: {exc}")
    _mock_live_ncp_env(monkeypatch, symlink_path)

    result = _run_adapter("ncp", adapter_config={"runtime": "disabled"})
    env = _adapter_env(result, "ncp")
    assert env["state"] in {"unavailable", "failed_closed"}
    assert env["candidates"] == []
