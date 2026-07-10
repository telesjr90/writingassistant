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


# ---------------------------------------------------------------------------
# PHASE8-IMPL-023-T016C — Live Story Check adapter behind flags
# ---------------------------------------------------------------------------


def _reset_live_story_check_env(monkeypatch: Any) -> None:
    for name in (
        oao._OMI_LIVE_TOOLS_ENABLED_ENV,
        oao._OMI_LIVE_STORY_CHECK_ENABLED_ENV,
        oao._OMI_LIVE_STORY_CHECK_BLOCKED_ENV,
        oao._OMI_LIVE_STORY_CHECK_SCENE_ID_ENV,
    ):
        monkeypatch.delenv(name, raising=False)


def _structured_legacy_story_check_result() -> dict[str, Any]:
    """Return a structured legacy Story Check result with T016C1-safe text.

    T016C1 safety boundary: the live adapter must NOT rewrite unsafe legacy
    text. This fixture intentionally uses plain diagnostic text that does
    NOT carry truth/canon/final/approved/promoted/apply-promotion/
    rewrite/continue/outline/draft labels so the live adapter can convert
    the structured items into T008-shaped candidate findings.

    The unsafe-text variants live in the T016C1 unsafe-text fixtures
    below; see ``_unsafe_text_legacy_story_check_results``.
    """
    return {
        "task": "story_check",
        "coherence_score": 7,
        "throughline_alignment": {
            "overall_story": {
                "present": True,
                "evidence": [
                    "Mara must recover the archive key before the hearing"
                ],
                "concerns": [],
            },
            "main_character": {
                "present": False,
                "evidence": [],
                "concerns": [
                    "Main Character throughline is not on hand for this fixture."
                ],
            },
            "influence_character": {
                "present": False,
                "evidence": [],
                "concerns": [
                    "Influence Character pressure is not established by available evidence."
                ],
            },
            "relationship_story": {
                "present": False,
                "evidence": [],
                "concerns": [
                    "Generic relationship context is not Relationship Story proof."
                ],
            },
        },
        "theme_drift": {
            "status": "insufficient_evidence",
            "reason": "No owner-supplied Issue or Variation evidence is on hand.",
        },
        "character_consistency": {
            "status": "insufficient_evidence",
            "reason": "Character context is incomplete for this fixture.",
        },
        "warnings": [
            "[Factual] Treat this Story Check as candidate diagnostics only."
        ],
        "suggestions": [
            "What owner-supplied evidence would help identify a Main Character throughline?"
        ],
        "insufficient_evidence": [
            "Main Character evidence is not on hand for this fixture.",
            "Influence Character evidence is not on hand for this fixture.",
        ],
    }


def _unsafe_legacy_warning_fixture() -> dict[str, Any]:
    return {
        "task": "story_check",
        "warnings": [
            "[Factual] This is canon and approved truth for the project."
        ],
    }


def _unsafe_legacy_suggestion_fixture() -> dict[str, Any]:
    return {
        "task": "story_check",
        "suggestions": [
            "What rewrite should the next chapter use?"
        ],
    }


def _unsafe_legacy_concern_fixture() -> dict[str, Any]:
    return {
        "task": "story_check",
        "concerns": [
            "The final scene is canon for the project."
        ],
    }


def _unsafe_legacy_insufficient_evidence_fixture() -> dict[str, Any]:
    return {
        "task": "story_check",
        "insufficient_evidence": [
            "Main Character evidence is promoted truth."
        ],
    }


def _unsafe_legacy_apply_promotion_fixture() -> dict[str, Any]:
    return {
        "task": "story_check",
        "warnings": [
            "Create a promotion record and run apply-promotion on the scene."
        ],
    }


def _unique_unsafe_phrase_legacy_fixture() -> dict[str, Any]:
    """Return a legacy fixture where the suggestion text contains both
    a unique phrase (``MAGIC_PHRASE_ZZZ``) and a forbidden label
    (``approved``). The T016C1 safety checker must reject the text; the
    converter must NOT rewrite the unique phrase into a safe phrase and
    accept the finding.
    """
    return {
        "task": "story_check",
        "suggestions": [
            "What MAGIC_PHRASE_ZZZ approved evidence would help?"
        ],
    }


def test_live_story_check_disabled_by_default_does_not_import_runtime(
    monkeypatch: Any,
) -> None:
    import backend.analysis_engine as analysis_engine

    _reset_live_story_check_env(monkeypatch)

    calls: list[tuple[str, str]] = []

    def fake_run_story_check(project_name: str, scene_id: str) -> dict[str, Any]:
        calls.append((project_name, scene_id))
        return _structured_legacy_story_check_result()

    monkeypatch.setattr(
        analysis_engine, "run_story_check", fake_run_story_check
    )

    result = _run_story_check(
        story_check_scene_id="scene_001",
    )

    assert calls == []
    env = _assert_failed_closed(result)
    assert env["state"] == "unavailable"
    assert "live story check" in env["explanation"].lower()


def test_live_story_check_enabled_with_mocked_runtime_normalizes_candidate_findings(
    monkeypatch: Any,
) -> None:
    import backend.analysis_engine as analysis_engine

    _reset_live_story_check_env(monkeypatch)
    monkeypatch.setenv(oao._OMI_LIVE_TOOLS_ENABLED_ENV, "1")
    monkeypatch.setenv(oao._OMI_LIVE_STORY_CHECK_ENABLED_ENV, "1")
    monkeypatch.setenv(oao._OMI_LIVE_STORY_CHECK_SCENE_ID_ENV, "scene_env_001")

    captured: dict[str, Any] = {}

    def fake_run_story_check(project_name: str, scene_id: str) -> dict[str, Any]:
        captured["project_name"] = project_name
        captured["scene_id"] = scene_id
        return _structured_legacy_story_check_result()

    monkeypatch.setattr(
        analysis_engine, "run_story_check", fake_run_story_check
    )

    result = oao.analyze_omi_raw_idea_with_tools(
        "demo_project",
        RAW_IDEA,
        persist_candidates=False,
        requested_adapters=["story_check"],
    )

    assert captured == {
        "project_name": "demo_project",
        "scene_id": "scene_env_001",
    }
    env = next(
        env for env in result["adapter_results"] if env["adapter"] == "story_check"
    )
    assert env["state"] == "succeeded"
    candidate_types = [finding["candidate_type"] for finding in result["findings"]]
    assert "structural_diagnostic" in candidate_types
    assert "diagnostic_question" in candidate_types
    assert "throughline_context" in candidate_types
    assert "storyform_context" in candidate_types
    assert "evidence_note" in candidate_types
    for finding in result["findings"]:
        assert finding["source_adapter"] == "story_check"
        assert finding["provenance"]["tool_source"] == "story_check"
        assert "support" in finding["provenance"]["support"].lower()
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
    assert result["persisted_candidate_ids"] == []
    assert result["safety"]["no_memory_canon_mutation"] is True
    assert result["safety"]["no_apply_promotion"] is True


def test_live_story_check_explicit_scene_id_overrides_env_scene_id(
    monkeypatch: Any,
) -> None:
    import backend.analysis_engine as analysis_engine

    _reset_live_story_check_env(monkeypatch)
    monkeypatch.setenv(oao._OMI_LIVE_TOOLS_ENABLED_ENV, "1")
    monkeypatch.setenv(oao._OMI_LIVE_STORY_CHECK_ENABLED_ENV, "1")
    monkeypatch.setenv(oao._OMI_LIVE_STORY_CHECK_SCENE_ID_ENV, "scene_env_001")

    captured: dict[str, Any] = {}

    def fake_run_story_check(project_name: str, scene_id: str) -> dict[str, Any]:
        captured["scene_id"] = scene_id
        return _structured_legacy_story_check_result()

    monkeypatch.setattr(
        analysis_engine, "run_story_check", fake_run_story_check
    )

    result = oao.analyze_omi_raw_idea_with_tools(
        "demo_project",
        RAW_IDEA,
        persist_candidates=False,
        requested_adapters=["story_check"],
        story_check_scene_id="scene_explicit_002",
    )

    assert captured["scene_id"] == "scene_explicit_002"
    env = next(
        env for env in result["adapter_results"] if env["adapter"] == "story_check"
    )
    assert env["state"] == "succeeded"


def test_live_story_check_missing_scene_id_fails_closed_without_runtime_call(
    monkeypatch: Any,
) -> None:
    import backend.analysis_engine as analysis_engine

    _reset_live_story_check_env(monkeypatch)
    monkeypatch.setenv(oao._OMI_LIVE_TOOLS_ENABLED_ENV, "1")
    monkeypatch.setenv(oao._OMI_LIVE_STORY_CHECK_ENABLED_ENV, "1")

    calls: list[tuple[str, str]] = []

    def fake_run_story_check(project_name: str, scene_id: str) -> dict[str, Any]:
        calls.append((project_name, scene_id))
        return _structured_legacy_story_check_result()

    monkeypatch.setattr(
        analysis_engine, "run_story_check", fake_run_story_check
    )

    result = oao.analyze_omi_raw_idea_with_tools(
        "demo_project",
        RAW_IDEA,
        persist_candidates=False,
        requested_adapters=["story_check"],
    )

    assert calls == []
    env = _assert_failed_closed(result)
    assert env["state"] == "unavailable"
    assert "scene id" in env["explanation"].lower()
    assert result["persisted_candidate_ids"] == []


def test_live_story_check_blocked_flag_overrides_live_availability(
    monkeypatch: Any,
) -> None:
    import backend.analysis_engine as analysis_engine

    _reset_live_story_check_env(monkeypatch)
    monkeypatch.setenv(oao._OMI_LIVE_TOOLS_ENABLED_ENV, "1")
    monkeypatch.setenv(oao._OMI_LIVE_STORY_CHECK_ENABLED_ENV, "1")
    monkeypatch.setenv(oao._OMI_LIVE_STORY_CHECK_SCENE_ID_ENV, "scene_env_001")
    monkeypatch.setenv(oao._OMI_LIVE_STORY_CHECK_BLOCKED_ENV, "1")

    calls: list[tuple[str, str]] = []

    def fake_run_story_check(project_name: str, scene_id: str) -> dict[str, Any]:
        calls.append((project_name, scene_id))
        return _structured_legacy_story_check_result()

    monkeypatch.setattr(
        analysis_engine, "run_story_check", fake_run_story_check
    )

    result = oao.analyze_omi_raw_idea_with_tools(
        "demo_project",
        RAW_IDEA,
        persist_candidates=False,
        requested_adapters=["story_check"],
    )

    assert calls == []
    env = _assert_failed_closed(result)
    assert env["state"] == "unavailable"


def test_live_story_check_runtime_exception_fails_closed(
    monkeypatch: Any,
) -> None:
    import backend.analysis_engine as analysis_engine

    _reset_live_story_check_env(monkeypatch)
    monkeypatch.setenv(oao._OMI_LIVE_TOOLS_ENABLED_ENV, "1")
    monkeypatch.setenv(oao._OMI_LIVE_STORY_CHECK_ENABLED_ENV, "1")
    monkeypatch.setenv(oao._OMI_LIVE_STORY_CHECK_SCENE_ID_ENV, "scene_env_001")

    def fake_run_story_check(project_name: str, scene_id: str) -> dict[str, Any]:
        raise RuntimeError("simulated ollama http timeout")

    monkeypatch.setattr(
        analysis_engine, "run_story_check", fake_run_story_check
    )

    result = oao.analyze_omi_raw_idea_with_tools(
        "demo_project",
        RAW_IDEA,
        persist_candidates=False,
        requested_adapters=["story_check"],
    )

    env = _assert_failed_closed(result)
    assert env["state"] == "failed_closed"
    assert "runtime" in env["explanation"].lower()
    assert result["persisted_candidate_ids"] == []


def test_live_story_check_malformed_legacy_result_fails_closed(
    monkeypatch: Any,
) -> None:
    import backend.analysis_engine as analysis_engine

    _reset_live_story_check_env(monkeypatch)
    monkeypatch.setenv(oao._OMI_LIVE_TOOLS_ENABLED_ENV, "1")
    monkeypatch.setenv(oao._OMI_LIVE_STORY_CHECK_ENABLED_ENV, "1")
    monkeypatch.setenv(oao._OMI_LIVE_STORY_CHECK_SCENE_ID_ENV, "scene_env_001")

    malformed_payloads: list[Any] = [
        None,
        "not a dict",
        {"error": "upstream ollama failure"},
        {"coherence_score": 7, "task": "story_check"},
    ]

    for payload in malformed_payloads:
        def make_fake(value: Any) -> Any:
            def fake_run_story_check(project_name: str, scene_id: str) -> Any:
                return value
            return fake_run_story_check

        monkeypatch.setattr(
            analysis_engine, "run_story_check", make_fake(payload)
        )

        result = oao.analyze_omi_raw_idea_with_tools(
            "demo_project",
            RAW_IDEA,
            persist_candidates=False,
            requested_adapters=["story_check"],
        )
        env = _assert_failed_closed(result)
        assert env["state"] in {"failed_closed", "error"}
        assert result["persisted_candidate_ids"] == []


def test_live_story_check_prose_only_legacy_result_fails_closed(
    monkeypatch: Any,
) -> None:
    import backend.analysis_engine as analysis_engine

    _reset_live_story_check_env(monkeypatch)
    monkeypatch.setenv(oao._OMI_LIVE_TOOLS_ENABLED_ENV, "1")
    monkeypatch.setenv(oao._OMI_LIVE_STORY_CHECK_ENABLED_ENV, "1")
    monkeypatch.setenv(oao._OMI_LIVE_STORY_CHECK_SCENE_ID_ENV, "scene_env_001")

    prose_only = {
        "task": "story_check",
        "narrative_prose": (
            "The princess walked into the grand hall and met the prince. "
            "They danced until the clock struck midnight and the spell was "
            "broken. The chapter ends with the kingdom celebrating."
        ),
    }

    def fake_run_story_check(project_name: str, scene_id: str) -> dict[str, Any]:
        return prose_only

    monkeypatch.setattr(
        analysis_engine, "run_story_check", fake_run_story_check
    )

    result = oao.analyze_omi_raw_idea_with_tools(
        "demo_project",
        RAW_IDEA,
        persist_candidates=False,
        requested_adapters=["story_check"],
    )

    env = _assert_failed_closed(result)
    assert env["state"] == "failed_closed"
    assert result["findings"] == []


def test_live_story_check_unsafe_output_fails_closed_via_t008_validator(
    monkeypatch: Any,
) -> None:
    import backend.analysis_engine as analysis_engine

    _reset_live_story_check_env(monkeypatch)
    monkeypatch.setenv(oao._OMI_LIVE_TOOLS_ENABLED_ENV, "1")
    monkeypatch.setenv(oao._OMI_LIVE_STORY_CHECK_ENABLED_ENV, "1")
    monkeypatch.setenv(oao._OMI_LIVE_STORY_CHECK_SCENE_ID_ENV, "scene_env_001")

    unsafe_payload = {
        "task": "story_check",
        "warnings": [
            "[Factual] This is canon and approved truth for the project."
        ],
        "suggestions": [
            "What rewrite should the next chapter use?"
        ],
    }

    def fake_run_story_check(project_name: str, scene_id: str) -> dict[str, Any]:
        return unsafe_payload

    monkeypatch.setattr(
        analysis_engine, "run_story_check", fake_run_story_check
    )

    result = oao.analyze_omi_raw_idea_with_tools(
        "demo_project",
        RAW_IDEA,
        persist_candidates=False,
        requested_adapters=["story_check"],
    )

    env = _assert_failed_closed(result)
    assert env["state"] in {"failed_closed", "error"}
    assert result["persisted_candidate_ids"] == []


def test_live_story_check_legacy_error_shape_returns_error_state(
    monkeypatch: Any,
) -> None:
    import backend.analysis_engine as analysis_engine

    _reset_live_story_check_env(monkeypatch)
    monkeypatch.setenv(oao._OMI_LIVE_TOOLS_ENABLED_ENV, "1")
    monkeypatch.setenv(oao._OMI_LIVE_STORY_CHECK_ENABLED_ENV, "1")
    monkeypatch.setenv(oao._OMI_LIVE_STORY_CHECK_SCENE_ID_ENV, "scene_env_001")

    def fake_run_story_check(project_name: str, scene_id: str) -> dict[str, Any]:
        return {"error": "upstream ollama returned 500"}

    monkeypatch.setattr(
        analysis_engine, "run_story_check", fake_run_story_check
    )

    result = oao.analyze_omi_raw_idea_with_tools(
        "demo_project",
        RAW_IDEA,
        persist_candidates=False,
        requested_adapters=["story_check"],
    )

    env = _assert_failed_closed(result)
    assert env["state"] == "error"
    assert "upstream ollama returned 500" in env["explanation"]
    assert result["persisted_candidate_ids"] == []


def test_live_story_check_existing_fixture_tests_still_pass() -> None:
    result = _run_story_check(_story_check_envelope())
    assert result["analysis_status"] == "succeeded"
    env = _story_check_env(result)
    assert env["state"] == "succeeded"


def test_live_story_check_persistence_boundary_remains_safe(
    monkeypatch: Any,
) -> None:
    import backend.project_manager as project_manager

    _reset_live_story_check_env(monkeypatch)
    monkeypatch.setenv(oao._OMI_LIVE_TOOLS_ENABLED_ENV, "1")
    monkeypatch.setenv(oao._OMI_LIVE_STORY_CHECK_ENABLED_ENV, "1")
    monkeypatch.setenv(oao._OMI_LIVE_STORY_CHECK_SCENE_ID_ENV, "scene_env_001")

    def fake_run_story_check(project_name: str, scene_id: str) -> dict[str, Any]:
        return _structured_legacy_story_check_result()

    monkeypatch.setattr(
        "backend.analysis_engine.run_story_check",
        fake_run_story_check,
        raising=False,
    )

    original_extract = project_manager.extract_omi_candidates_from_raw_idea
    original_persist = getattr(
        project_manager, "persist_omi_tool_assisted_findings_as_candidates", None
    )
    extract_calls: list[dict[str, Any]] = []
    persist_calls: list[dict[str, Any]] = []

    def spy_extract(*args: Any, **kwargs: Any) -> dict[str, Any]:
        extract_calls.append({"args": args, "kwargs": kwargs})
        return original_extract(*args, **kwargs)

    def spy_persist(*args: Any, **kwargs: Any) -> dict[str, Any]:
        persist_calls.append({"args": args, "kwargs": kwargs})
        return {
            "persisted_candidate_ids": [],
            "new_candidate_ids": [],
            "reused_candidate_ids": [],
            "persistence_status": "no_candidates_persisted",
            "persistence_explanation": "spy no-op",
        }

    monkeypatch.setattr(
        project_manager, "extract_omi_candidates_from_raw_idea", spy_extract
    )
    if original_persist is not None:
        monkeypatch.setattr(
            project_manager,
            "persist_omi_tool_assisted_findings_as_candidates",
            spy_persist,
        )

    result = oao.analyze_omi_raw_idea_with_tools(
        "demo_project",
        RAW_IDEA,
        persist_candidates=False,
        requested_adapters=["story_check"],
        source_idea_id="idea_xyz",
    )

    assert result["persisted_candidate_ids"] == []
    assert result["safety"]["no_memory_canon_mutation"] is True
    assert result["safety"]["no_apply_promotion"] is True
    assert result["safety"]["no_canon_promotion"] is True


def test_live_story_check_does_not_call_legacy_route() -> None:
    import backend.main as main_module

    route_calls: list[tuple[str, str]] = []

    if not hasattr(main_module, "story_check"):
        return

    def fake_story_check_route(project_name: str, scene_id: str) -> dict[str, Any]:
        route_calls.append((project_name, scene_id))
        return {"error": "should not be called"}

    original = main_module.story_check
    main_module.story_check = fake_story_check_route  # type: ignore[assignment]
    try:
        assert callable(oao._build_story_check_live_runner)
        runner = oao._build_story_check_live_runner(adapter_config=None)
        assert runner is not None
        assert callable(runner)
    finally:
        main_module.story_check = original  # type: ignore[assignment]

    assert route_calls == []


def test_live_story_check_orchestrator_does_not_call_real_runtime_when_flags_off(
    monkeypatch: Any,
) -> None:
    import backend.analysis_engine as analysis_engine

    _reset_live_story_check_env(monkeypatch)
    monkeypatch.setenv(oao._OMI_LIVE_STORY_CHECK_ENABLED_ENV, "1")
    monkeypatch.setenv(oao._OMI_LIVE_STORY_CHECK_SCENE_ID_ENV, "scene_env_001")
    monkeypatch.delenv(oao._OMI_LIVE_TOOLS_ENABLED_ENV, raising=False)

    calls: list[tuple[str, str]] = []

    def fake_run_story_check(project_name: str, scene_id: str) -> dict[str, Any]:
        calls.append((project_name, scene_id))
        return _structured_legacy_story_check_result()

    monkeypatch.setattr(
        analysis_engine, "run_story_check", fake_run_story_check
    )

    result = oao.analyze_omi_raw_idea_with_tools(
        "demo_project",
        RAW_IDEA,
        persist_candidates=False,
        requested_adapters=["story_check"],
    )

    assert calls == []
    env = _assert_failed_closed(result)
    assert env["state"] == "unavailable"
    assert result["persisted_candidate_ids"] == []


# ---------------------------------------------------------------------------
# PHASE8-IMPL-023-T016C1 — Tighten Story Check live converter sanitizer boundary
# ---------------------------------------------------------------------------


def _run_live_with_legacy(
    monkeypatch: Any,
    legacy_result: dict[str, Any],
) -> dict[str, Any]:
    import backend.analysis_engine as analysis_engine

    _reset_live_story_check_env(monkeypatch)
    monkeypatch.setenv(oao._OMI_LIVE_TOOLS_ENABLED_ENV, "1")
    monkeypatch.setenv(oao._OMI_LIVE_STORY_CHECK_ENABLED_ENV, "1")
    monkeypatch.setenv(oao._OMI_LIVE_STORY_CHECK_SCENE_ID_ENV, "scene_env_001")

    def fake_run_story_check(project_name: str, scene_id: str) -> dict[str, Any]:
        return legacy_result

    monkeypatch.setattr(
        analysis_engine, "run_story_check", fake_run_story_check
    )

    return oao.analyze_omi_raw_idea_with_tools(
        "demo_project",
        RAW_IDEA,
        persist_candidates=False,
        requested_adapters=["story_check"],
    )


def test_t016c1_unsafe_canon_approved_in_warning_fails_closed(
    monkeypatch: Any,
) -> None:
    result = _run_live_with_legacy(
        monkeypatch, _unsafe_legacy_warning_fixture()
    )
    env = _assert_failed_closed(result)
    assert env["state"] == "failed_closed"
    assert result["findings"] == []
    assert result["persisted_candidate_ids"] == []


def test_t016c1_unsafe_rewrite_in_suggestion_fails_closed(
    monkeypatch: Any,
) -> None:
    result = _run_live_with_legacy(
        monkeypatch, _unsafe_legacy_suggestion_fixture()
    )
    env = _assert_failed_closed(result)
    assert env["state"] == "failed_closed"
    assert result["findings"] == []


def test_t016c1_unsafe_final_in_concern_fails_closed(
    monkeypatch: Any,
) -> None:
    result = _run_live_with_legacy(
        monkeypatch, _unsafe_legacy_concern_fixture()
    )
    env = _assert_failed_closed(result)
    assert env["state"] == "failed_closed"
    assert result["findings"] == []


def test_t016c1_unsafe_promoted_in_insufficient_evidence_fails_closed(
    monkeypatch: Any,
) -> None:
    result = _run_live_with_legacy(
        monkeypatch, _unsafe_legacy_insufficient_evidence_fixture()
    )
    env = _assert_failed_closed(result)
    assert env["state"] == "failed_closed"
    assert result["findings"] == []


def test_t016c1_unsafe_apply_promotion_text_fails_closed(
    monkeypatch: Any,
) -> None:
    result = _run_live_with_legacy(
        monkeypatch, _unsafe_legacy_apply_promotion_fixture()
    )
    env = _assert_failed_closed(result)
    assert env["state"] == "failed_closed"
    assert result["findings"] == []


def test_t016c1_unsafe_legacy_text_is_not_sanitized_into_finding(
    monkeypatch: Any,
) -> None:
    """The unique unsafe phrase must NOT appear in any finding text.

    T016C1 boundary: the live adapter must NOT rewrite unsafe legacy
    text. If the text contained the unique phrase ``MAGIC_PHRASE_ZZZ``
    (e.g. ``"What owner-supplied MAGIC_PHRASE_ZZZ evidence would help?"``)
    before sanitization, the adapter must SKIP the item and never accept
    a rewritten phrase as a finding. The correct behavior is fail-closed
    with no findings, not sanitized acceptance.
    """
    result = _run_live_with_legacy(
        monkeypatch, _unique_unsafe_phrase_legacy_fixture()
    )
    env = _assert_failed_closed(result)
    assert env["state"] == "failed_closed"
    assert result["findings"] == []
    for adapter_env in result["adapter_results"]:
        assert "MAGIC_PHRASE_ZZZ" not in json.dumps(adapter_env)


def test_t016c1_safe_legacy_text_still_converts_to_candidate_finding(
    monkeypatch: Any,
) -> None:
    result = _run_live_with_legacy(
        monkeypatch, _structured_legacy_story_check_result()
    )
    env = next(
        env for env in result["adapter_results"] if env["adapter"] == "story_check"
    )
    assert env["state"] == "succeeded"
    assert result["findings"]
    for finding in result["findings"]:
        assert finding["source_adapter"] == "story_check"
        assert finding["provenance"]["tool_source"] == "story_check"
        assert "support" in finding["provenance"]["support"].lower()
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
    assert result["persisted_candidate_ids"] == []
    assert result["safety"]["no_memory_canon_mutation"] is True
    assert result["safety"]["no_apply_promotion"] is True


def test_t016c1_converter_owned_labels_are_generic_and_safe(
    monkeypatch: Any,
) -> None:
    result = _run_live_with_legacy(
        monkeypatch, _structured_legacy_story_check_result()
    )
    assert result["findings"]
    allowed_label_prefixes = (
        "Story Check warning",
        "Story Check concern",
        "Story Check question",
        "Story Check insufficient evidence",
        "Story Check throughline diagnostic",
        "Story Check storyform diagnostic",
        "Story Check character consistency diagnostic",
    )
    for finding in result["findings"]:
        label = finding["label"]
        assert any(
            label == prefix or label.startswith(prefix + ":")
            for prefix in allowed_label_prefixes
        ), f"unexpected label: {label!r}"
        for forbidden in (
            "truth",
            "canon",
            "final",
            "approved",
            "promoted",
        ):
            assert forbidden not in label.lower()
    claim_blob = " ".join(finding["extracted_claim"] for finding in result["findings"])
    for forbidden in (
        "truth",
        "canon",
        "final",
        "approved",
        "promoted",
    ):
        assert forbidden not in claim_blob.lower()


def test_t016c1_partial_unsafe_legacy_items_are_skipped_safe_items_kept(
    monkeypatch: Any,
) -> None:
    """Mixed legacy result: one safe suggestion + one unsafe suggestion.

    The safe suggestion should be converted into a T008 finding; the
    unsafe one should be skipped at the item level. The envelope should
    remain ``succeeded`` because at least one safe item remains.
    """
    mixed_legacy = {
        "task": "story_check",
        "suggestions": [
            "What evidence would help identify a Main Character throughline?",
            "What rewrite should the next chapter use?",
        ],
    }
    result = _run_live_with_legacy(monkeypatch, mixed_legacy)
    env = next(
        env for env in result["adapter_results"] if env["adapter"] == "story_check"
    )
    assert env["state"] == "succeeded"
    assert result["findings"]
    for finding in result["findings"]:
        assert finding["candidate_type"] == "diagnostic_question"
        assert "rewrite" not in finding["extracted_claim"].lower()
        assert "rewrite" not in finding["evidence"][0]["source_excerpt"].lower()


def test_t016c1_unsafe_throughline_evidence_is_skipped(
    monkeypatch: Any,
) -> None:
    """Unsafe throughline evidence is skipped, not synthesized.

    T016C1: the converter must NOT generate placeholder text from the
    ``present``/``status`` flag alone. If the throughline evidence and
    concerns are all unsafe, the throughline item is skipped entirely
    (no synthetic excerpt), and the envelope fails closed if no other
    safe items exist.
    """
    legacy = {
        "task": "story_check",
        "throughline_alignment": {
            "main_character": {
                "present": False,
                "evidence": [
                    "Main Character throughline is approved and final truth."
                ],
                "concerns": [
                    "Influence Character pressure is canon and locked."
                ],
            },
        },
    }
    result = _run_live_with_legacy(monkeypatch, legacy)
    env = _assert_failed_closed(result)
    assert env["state"] == "failed_closed"
    assert result["findings"] == []


def test_t016c1_unsafe_theme_drift_reason_is_skipped(
    monkeypatch: Any,
) -> None:
    """Unsafe ``theme_drift.reason`` is skipped, not converted.

    If the reason text contains forbidden truth/canon/final/approved
    labels, the theme_drift item is skipped. If no other safe items
    exist, the envelope fails closed.
    """
    legacy = {
        "task": "story_check",
        "theme_drift": {
            "status": "insufficient_evidence",
            "reason": "No approved evidence is on hand for the project canon.",
        },
    }
    result = _run_live_with_legacy(monkeypatch, legacy)
    env = _assert_failed_closed(result)
    assert env["state"] == "failed_closed"
    assert result["findings"] == []


def test_t016c1_persistence_boundary_remains_safe_after_unsafe_skip(
    monkeypatch: Any,
) -> None:
    """persist_candidates=True path: unsafe legacy text still fails closed,
    and the persistence helpers are NOT invoked in failure paths.
    """
    import backend.project_manager as project_manager

    _reset_live_story_check_env(monkeypatch)
    monkeypatch.setenv(oao._OMI_LIVE_TOOLS_ENABLED_ENV, "1")
    monkeypatch.setenv(oao._OMI_LIVE_STORY_CHECK_ENABLED_ENV, "1")
    monkeypatch.setenv(oao._OMI_LIVE_STORY_CHECK_SCENE_ID_ENV, "scene_env_001")

    extract_calls: list[Any] = []
    persist_calls: list[Any] = []

    def spy_extract(*args: Any, **kwargs: Any) -> dict[str, Any]:
        extract_calls.append({"args": args, "kwargs": kwargs})
        return {"candidates": [], "persisted_candidate_ids": []}

    def spy_persist(*args: Any, **kwargs: Any) -> dict[str, Any]:
        persist_calls.append({"args": args, "kwargs": kwargs})
        return {
            "persisted_candidate_ids": [],
            "new_candidate_ids": [],
            "reused_candidate_ids": [],
            "persistence_status": "no_candidates_persisted",
            "persistence_explanation": "spy no-op",
        }

    import backend.analysis_engine as analysis_engine

    def fake_run_story_check(project_name: str, scene_id: str) -> dict[str, Any]:
        return _unsafe_legacy_apply_promotion_fixture()

    monkeypatch.setattr(analysis_engine, "run_story_check", fake_run_story_check)
    monkeypatch.setattr(
        project_manager, "extract_omi_candidates_from_raw_idea", spy_extract
    )
    if hasattr(project_manager, "persist_omi_tool_assisted_findings_as_candidates"):
        monkeypatch.setattr(
            project_manager,
            "persist_omi_tool_assisted_findings_as_candidates",
            spy_persist,
        )

    result = oao.analyze_omi_raw_idea_with_tools(
        "demo_project",
        RAW_IDEA,
        persist_candidates=True,
        requested_adapters=["story_check"],
        source_idea_id="idea_xyz",
    )

    env = _assert_failed_closed(result)
    assert env["state"] == "failed_closed"
    assert result["persisted_candidate_ids"] == []
    assert result["safety"]["no_memory_canon_mutation"] is True
    assert result["safety"]["no_apply_promotion"] is True
    assert result["safety"]["no_canon_promotion"] is True
    assert extract_calls == []


def test_t016c1_t008_validator_remains_authoritative(
    monkeypatch: Any,
) -> None:
    """The T008 ``validate_story_check_fixture_envelope`` is the
    authoritative validator. Even when the converter produces a
    well-shaped envelope, the T008 validator may reject it for prose,
    missing evidence, or unsafe output.
    """
    from backend.omi_analysis_orchestrator import (
        _story_check_result_to_envelope,
    )

    envelope = _story_check_result_to_envelope(
        {"task": "story_check", "coherence_score": 7},
        project_name="demo_project",
        scene_id="scene_env_001",
    )
    assert envelope["status"] == "failed_closed"
    assert envelope["findings"] == []

    prose_only = _story_check_result_to_envelope(
        {
            "task": "story_check",
            "narrative_prose": (
                "The princess walked into the grand hall and met the "
                "prince. They danced until the clock struck midnight."
            ),
        },
        project_name="demo_project",
        scene_id="scene_env_001",
    )
    assert prose_only["status"] == "failed_closed"
    assert prose_only["findings"] == []

    error_shape = _story_check_result_to_envelope(
        {"error": "upstream ollama returned 500"},
        project_name="demo_project",
        scene_id="scene_env_001",
    )
    assert error_shape["status"] == "error"
    assert error_shape["findings"] == []


def test_t016c1_existing_fixture_tests_still_pass() -> None:
    """T008 fixture path remains supported and unchanged by T016C1."""
    result = _run_story_check(_story_check_envelope())
    assert result["analysis_status"] == "succeeded"
    env = _story_check_env(result)
    assert env["state"] == "succeeded"


def test_t016c1_existing_t016c_runtime_success_test_still_uses_safe_text() -> None:
    """The T016C runtime-success test now uses T016C1-safe text only.

    This test asserts that the legacy fixture used by the
    T016C runtime-success test does not contain truth/canon/final/
    approved/promoted labels, so the live adapter can convert it into
    T008-shaped findings.
    """
    legacy = _structured_legacy_story_check_result()
    blob = json.dumps(legacy)
    for forbidden in (
        "approved",
        "promoted",
        " canon ",
        "truth",
        "final",
    ):
        assert forbidden not in blob.lower(), (
            f"T016C1 safety boundary violated: legacy fixture contains "
            f"forbidden label {forbidden!r}; the live adapter must NOT "
            f"sanitize it. Update _structured_legacy_story_check_result "
            f"to use safe text."
        )
