"""PHASE8-IMPL-023-T008 Story Check diagnostic fixture adapter tests.

These tests use fixture/mock diagnostic output only. They do not import or run
Story Check, call external services, call models, mutate Memory/Canon, persist
AI/tool candidates, create promotion records, run apply-promotion, or generate
story prose.
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
    "Owner note: Mara must recover the archive key before the hearing. "
    "The note leaves the mentor relationship unresolved."
)


def _story_check_finding(**overrides: Any) -> dict[str, Any]:
    finding: dict[str, Any] = {
        "raw_finding_id": "story-check-structural-1",
        "finding_type": "structural_diagnostic",
        "label": "Archive key pressure",
        "diagnostic_claim": (
            "The archive key creates structural pressure around the hearing"
        ),
        "evidence": [
            {
                "source_excerpt": (
                    "Mara must recover the archive key before the hearing"
                ),
                "source_locator": "raw_idea:L1:C12-66",
            }
        ],
        "source_locator": "raw_idea:L1:C12-66",
        "support_label": "Story Check diagnostic support only",
        "confidence": "medium support",
    }
    finding.update(overrides)
    return finding


def _story_check_envelope(
    findings: list[dict[str, Any]] | None = None,
    **overrides: Any,
) -> dict[str, Any]:
    envelope: dict[str, Any] = {
        "schema_version": oao.OMI_STORY_CHECK_SCHEMA_VERSION,
        "adapter": "story_check",
        "status": "succeeded",
        "explanation": "fixture-only Story Check diagnostic handoff",
        "provenance": {
            "tool_source": "story_check",
            "adapter": "story_check",
            "support": "Story Check diagnostic support only",
        },
        "findings": findings if findings is not None else [_story_check_finding()],
    }
    envelope.update(overrides)
    return envelope


def _run_story_check(fixture: Any | None = None, **kwargs: Any) -> dict[str, Any]:
    params: dict[str, Any] = {
        "persist_candidates": False,
        "requested_adapters": ["story_check"],
    }
    if fixture is not None:
        params["adapter_fixture_outputs"] = {"story_check": fixture}
    params.update(kwargs)
    return oao.analyze_omi_raw_idea_with_tools("demo", RAW_IDEA, **params)


def _story_check_env(result: dict[str, Any]) -> dict[str, Any]:
    envs = [
        env for env in result["adapter_results"]
        if env["adapter"] == "story_check"
    ]
    assert len(envs) == 1
    return envs[0]


def _assert_failed_closed(result: dict[str, Any]) -> dict[str, Any]:
    assert result["analysis_status"] == "fail_closed"
    assert result["findings"] == []
    assert result["persisted_candidate_ids"] == []
    env = _story_check_env(result)
    assert env["state"] in {"failed_closed", "unavailable", "error"}
    assert env["candidates"] == []
    assert env["explanation"]
    return env


def _assert_candidate_only_finding(finding: dict[str, Any]) -> None:
    assert finding["source_adapter"] == "story_check"
    assert finding["provenance"]["tool_source"] == "story_check"
    assert finding["provenance"]["adapter"] == "story_check"
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
    assert finding["normalized_finding_id"].startswith("omi-find-story_check-")
    for forbidden in ("truth", "canon", "final", "approved", "promoted"):
        assert forbidden not in finding["support_label"].lower()


def test_story_check_without_fixture_returns_unavailable_and_no_findings() -> None:
    result = _run_story_check(adapter_config={"runtime": "disabled"})

    env = _assert_failed_closed(result)
    assert env["state"] == "unavailable"
    assert "fixture" in env["explanation"].lower()
    assert "live story check" in env["explanation"].lower()
    assert result["persisted_candidate_ids"] == []


def test_valid_story_check_diagnostic_fixture_normalizes_candidate_only_findings() -> None:
    fixture = _story_check_envelope(
        [
            _story_check_finding(),
            _story_check_finding(
                raw_finding_id="story-check-storyform-1",
                finding_type="storyform_context",
                label="Storyform pressure support",
                diagnostic_claim=(
                    "The hearing deadline supports storyform context review"
                ),
            ),
            _story_check_finding(
                raw_finding_id="story-check-throughline-1",
                finding_type="throughline_context",
                label="Mentor relationship context",
                diagnostic_claim=(
                    "The unresolved mentor relationship supports throughline review"
                ),
                evidence=[
                    {
                        "source_excerpt": (
                            "The note leaves the mentor relationship unresolved"
                        ),
                        "source_locator": "raw_idea:L1:C68-119",
                    }
                ],
                source_locator="raw_idea:L1:C68-119",
            ),
            _story_check_finding(
                raw_finding_id="story-check-plot-1",
                finding_type="plot_thread_diagnostic",
                label="Archive key plot thread",
                diagnostic_claim="The archive key is evidence for a plot thread",
            ),
            _story_check_finding(
                raw_finding_id="story-check-relationship-1",
                finding_type="relationship_diagnostic",
                label="Mara and mentor relationship",
                diagnostic_claim=(
                    "The mentor relationship is flagged as relationship support"
                ),
                evidence=[
                    {
                        "source_excerpt": (
                            "The note leaves the mentor relationship unresolved"
                        ),
                        "source_locator": "raw_idea:L1:C68-119",
                    }
                ],
                source_locator="raw_idea:L1:C68-119",
            ),
        ]
    )

    result = _run_story_check(fixture)

    assert result["analysis_status"] == "succeeded"
    assert result["persisted_candidate_ids"] == []
    assert _story_check_env(result)["state"] == "succeeded"
    assert [finding["candidate_type"] for finding in result["findings"]] == [
        "structural_diagnostic",
        "storyform_context",
        "throughline_context",
        "plot_thread",
        "relationship",
    ]
    for finding in result["findings"]:
        _assert_candidate_only_finding(finding)


def test_valid_story_check_diagnostic_question_is_review_support_not_prose() -> None:
    fixture = _story_check_envelope(
        [
            _story_check_finding(
                raw_finding_id="story-check-question-1",
                finding_type="diagnostic_question",
                label="Mentor relationship ambiguity",
                question=(
                    "Which throughline is supported by the unresolved mentor "
                    "relationship?"
                ),
                evidence=[
                    {
                        "source_excerpt": (
                            "The note leaves the mentor relationship unresolved"
                        ),
                        "source_locator": "raw_idea:L1:C68-119",
                    }
                ],
                source_locator="raw_idea:L1:C68-119",
            )
        ]
    )

    result = _run_story_check(json.dumps(fixture))

    assert result["analysis_status"] == "succeeded"
    finding = result["findings"][0]
    assert finding["candidate_type"] == "diagnostic_question"
    assert finding["extracted_claim"].endswith("?")
    _assert_candidate_only_finding(finding)


def test_story_check_invalid_json_schema_adapter_or_unknown_type_fails_closed() -> None:
    fixtures: list[Any] = [
        "not json",
        _story_check_envelope(schema_version="future.story_check.schema"),
        _story_check_envelope(adapter="ollama_model"),
        _story_check_envelope([
            _story_check_finding(finding_type="scene_prose")
        ]),
    ]

    for fixture in fixtures:
        _assert_failed_closed(_run_story_check(fixture))


def test_story_check_missing_evidence_fails_closed() -> None:
    fixture = _story_check_envelope([_story_check_finding()])
    del fixture["findings"][0]["evidence"]

    env = _assert_failed_closed(_run_story_check(fixture))
    assert "evidence" in env["explanation"].lower()


def test_story_check_missing_source_locator_fails_closed() -> None:
    fixture = _story_check_envelope([_story_check_finding()])
    del fixture["findings"][0]["source_locator"]

    env = _assert_failed_closed(_run_story_check(fixture))
    assert "source_locator" in env["explanation"]


def test_story_check_missing_provenance_fails_closed() -> None:
    fixture = _story_check_envelope()
    del fixture["provenance"]

    env = _assert_failed_closed(_run_story_check(fixture))
    assert "provenance" in env["explanation"].lower()


def test_story_check_truth_canon_approved_or_final_labels_fail_closed() -> None:
    fixtures = [
        _story_check_envelope([
            _story_check_finding(support_label="truth support")
        ]),
        _story_check_envelope([
            _story_check_finding(support_label="canon support")
        ]),
        _story_check_envelope([
            _story_check_finding(owner_decision={"decision": "approve", "approved": True})
        ]),
        _story_check_envelope([
            _story_check_finding(support_label="final support")
        ]),
        _story_check_envelope([
            _story_check_finding(review_status="approved")
        ]),
    ]

    for fixture in fixtures:
        _assert_failed_closed(_run_story_check(fixture))


def test_story_check_prose_rewrite_outline_draft_continue_suggestions_fail_closed() -> None:
    fixtures = [
        _story_check_envelope([
            _story_check_finding(diagnostic_claim="Rewrite: a polished version begins")
        ]),
        _story_check_envelope([
            _story_check_finding(question="What should happen next in the scene?")
        ]),
        _story_check_envelope([
            _story_check_finding(outline="blocked outline field")
        ]),
        _story_check_envelope([
            _story_check_finding(diagnostic_claim="Draft the next chapter around Mara")
        ]),
        _story_check_envelope([
            _story_check_finding(diagnostic_claim="Continue the story after the hearing")
        ]),
    ]

    for fixture in fixtures:
        env = _assert_failed_closed(_run_story_check(fixture))
        assert "prose" in env["explanation"].lower() or "diagnostic" in (
            env["explanation"].lower()
        )


def test_story_check_memory_canon_promotion_apply_promotion_and_persistence_fail_closed() -> None:
    fixtures = [
        _story_check_envelope([
            _story_check_finding(memory_mutation={"target": "Memory"})
        ]),
        _story_check_envelope([
            _story_check_finding(canon_mutation={"target": "Canon"})
        ]),
        _story_check_envelope([
            _story_check_finding(promotion_record={"id": "unsafe"})
        ]),
        _story_check_envelope([
            _story_check_finding(apply_promotion={"enabled": True})
        ]),
        _story_check_envelope([
            _story_check_finding(persist_candidates=True)
        ]),
    ]

    for fixture in fixtures:
        env = _assert_failed_closed(_run_story_check(fixture))
        assert (
            "promotion" in env["explanation"].lower()
            or "memory/canon" in env["explanation"].lower()
            or "persist" in env["explanation"].lower()
        )


def test_story_check_findings_are_not_persisted_even_when_persist_candidates_true(
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

    result = _run_story_check(
        _story_check_envelope(),
        persist_candidates=True,
        source_idea_id="idea_123",
    )

    assert result["analysis_status"] == "succeeded"
    assert result["persisted_candidate_ids"] == []
    assert result["safety"]["no_memory_canon_mutation"] is True
    assert result["safety"]["no_apply_promotion"] is True
    assert calls == []
