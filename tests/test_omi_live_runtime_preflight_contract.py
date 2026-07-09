"""PHASE8-IMPL-023-T013 live runtime preflight contract tests.

These tests do not run live OMI tools, call external services, call models,
persist candidates, mutate Memory/Canon, create promotion records, run
apply-promotion, or generate story prose.
"""

from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from backend import main
from backend import omi_runtime_preflight as preflight
from backend import project_manager


_MOCK_SPACY_AVAILABLE = {
    "spacy_package_available": True,
    "spacy_model_available": True,
    "spacy_model_name": "en_core_web_sm",
    "spacy_probe_detail": "spaCy model 'en_core_web_sm' loaded successfully",
}

_MOCK_SPACY_PACKAGE_MISSING = {
    "spacy_package_available": False,
    "spacy_model_available": False,
    "spacy_model_name": "en_core_web_sm",
    "spacy_probe_detail": "Python package not available: spacy",
}

_MOCK_SPACY_MODEL_MISSING = {
    "spacy_package_available": True,
    "spacy_model_available": False,
    "spacy_model_name": "en_core_web_sm",
    "spacy_probe_detail": "spaCy model 'en_core_web_sm' not found/loadable: mock model missing",
}


def _mock_spacy_probe(monkeypatch, result: dict | None = None) -> None:
    if result is not None:
        monkeypatch.setattr(
            preflight,
            "_spacy_model_probe",
            lambda _model_name: {**result, "spacy_model_name": _model_name},
        )
    else:
        monkeypatch.setattr(
            preflight,
            "_spacy_model_probe",
            lambda _model_name: {
                **_MOCK_SPACY_AVAILABLE,
                "spacy_model_name": _model_name,
            },
        )


EXPECTED_TOOLS = {
    "spacy",
    "ollama_model",
    "story_check",
    "booknlp",
    "ncp",
    "subtxt",
    "dramatica_flow",
    "deterministic_fallback",
}

EXPECTED_STATUSES = {
    "enabled",
    "disabled",
    "available",
    "unavailable",
    "blocked",
    "error",
    "not_configured",
}


def _report(env: dict[str, str] | None = None) -> dict:
    return preflight.build_omi_runtime_preflight_report("demo", env=env or {})


def _tools_by_name(report: dict) -> dict[str, dict]:
    return {tool["tool"]: tool for tool in report["tools"]}


def test_default_live_tools_are_disabled_or_readiness_only() -> None:
    report = _report()

    assert report["schema_version"] == "omi_runtime_preflight.v1"
    assert set(report["status_vocabulary"]) == EXPECTED_STATUSES
    assert report["global_live_tools_enabled"] is False
    assert report["live_runtime_tests_enabled"] is False
    assert {tool["tool"] for tool in report["tools"]} == EXPECTED_TOOLS
    assert report["safety"]["read_only"] is True
    assert report["safety"]["heavy_analysis_executed"] is False
    assert report["safety"]["external_services_called"] is False
    assert report["safety"]["live_models_called"] is False
    assert report["safety"]["candidate_persistence"] is False
    assert report["safety"]["memory_canon_mutation"] is False
    assert report["safety"]["promotion_or_apply_promotion"] is False
    assert report["safety"]["story_prose_generated"] is False

    for tool in report["tools"]:
        assert tool["status"] in {"disabled", "available"}
        assert tool["runtime_enabled"] is False
        assert tool["fixture_contract_exists"] is True
        assert tool["safety"]["heavy_analysis_executed"] is False


def test_missing_dependencies_return_unavailable_or_not_configured_without_crashing(
    monkeypatch,
) -> None:
    monkeypatch.setattr(preflight.importlib.util, "find_spec", lambda _name: None)
    monkeypatch.setattr(preflight.shutil, "which", lambda _name: None)

    report = _report(
        {
            "OMI_LIVE_TOOLS_ENABLED": "true",
            "OMI_LIVE_SPACY_ENABLED": "true",
            "OMI_LIVE_OLLAMA_ENABLED": "true",
            "OMI_LIVE_BOOKNLP_ENABLED": "true",
        }
    )
    tools = _tools_by_name(report)

    assert tools["spacy"]["status"] == "unavailable"
    assert tools["booknlp"]["status"] == "unavailable"
    assert tools["ollama_model"]["status"] == "not_configured"
    assert tools["spacy"]["runtime_dependency_status"] == "unavailable"
    assert tools["booknlp"]["runtime_dependency_status"] == "unavailable"
    assert tools["ollama_model"]["runtime_dependency_status"] == "not_configured"


def test_global_live_flag_without_per_tool_flag_does_not_enable_tools() -> None:
    report = _report({"OMI_LIVE_TOOLS_ENABLED": "true"})

    for tool in report["tools"]:
        assert tool["global_enabled"] is True
        assert tool["tool_enabled"] is False
        assert tool["runtime_enabled"] is False
        assert tool["status"] in {"disabled", "available"}
        assert tool["safety"]["live_models_called"] is False


def test_per_tool_flags_are_recognized_and_still_require_global_gate(monkeypatch) -> None:
    _mock_spacy_probe(monkeypatch)

    per_tool_only = _tools_by_name(_report({"OMI_LIVE_SPACY_ENABLED": "true"}))["spacy"]
    assert per_tool_only["tool_enabled"] is True
    assert per_tool_only["global_enabled"] is False
    assert per_tool_only["runtime_enabled"] is False
    assert per_tool_only["status"] == "available"

    fully_enabled = _tools_by_name(
        _report({"OMI_LIVE_TOOLS_ENABLED": "true", "OMI_LIVE_SPACY_ENABLED": "true"})
    )["spacy"]
    assert fully_enabled["runtime_enabled"] is True
    assert fully_enabled["status"] == "enabled"


def test_preflight_distinguishes_fixture_contract_config_dependency_and_enablement(
    monkeypatch,
) -> None:
    _mock_spacy_probe(monkeypatch)

    tool = _tools_by_name(
        _report({"OMI_LIVE_TOOLS_ENABLED": "true", "OMI_LIVE_SPACY_ENABLED": "true"})
    )["spacy"]

    assert tool["fixture_contract_exists"] is True
    assert tool["runtime_configured"] is True
    assert tool["runtime_dependency_available"] is True
    assert tool["runtime_dependency_status"] == "available"
    assert tool["runtime_enabled"] is True
    assert tool["status"] == "enabled"


def test_blocked_status_is_explicit_and_overrides_enablement(monkeypatch) -> None:
    _mock_spacy_probe(monkeypatch)

    tool = _tools_by_name(
        _report(
            {
                "OMI_LIVE_TOOLS_ENABLED": "true",
                "OMI_LIVE_SPACY_ENABLED": "true",
                "OMI_LIVE_SPACY_BLOCKED": "true",
                "OMI_LIVE_SPACY_BLOCKED_REASON": "Owner decision pending.",
            }
        )
    )["spacy"]

    assert tool["status"] == "blocked"
    assert tool["runtime_enabled"] is True
    assert tool["blocked"] is True
    assert tool["blocked_reason"] == "Owner decision pending."


def test_preflight_is_read_only_and_does_not_persist_or_promote(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)
    idea = project_manager.create_omi_idea("demo", "Owner-authored planning note.")
    before = project_manager.get_omi_summary("demo")

    report = preflight.build_omi_runtime_preflight_report("demo", env={})

    after = project_manager.get_omi_summary("demo")
    assert after == before
    assert after["index"]["idea_ids"] == [idea["idea_id"]]
    assert after["index"]["candidate_ids"] == []
    assert after["promotions"] == []
    assert report["safety"]["candidate_persistence"] is False
    assert report["safety"]["memory_canon_mutation"] is False
    assert report["safety"]["promotion_or_apply_promotion"] is False
    assert report["safety"]["story_prose_generated"] is False


def test_route_wrapper_returns_read_only_preflight_without_project_writes(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)
    project_manager.create_omi_idea("demo", "Owner-authored route preflight note.")
    before = project_manager.get_omi_summary("demo")

    report = main.get_omi_runtime_preflight("demo")

    assert report["project_name"] == "demo"
    assert report["safety"]["read_only"] is True
    assert project_manager.get_omi_summary("demo") == before


# ---------------------------------------------------------------------------
# T014B — spaCy runtime availability check
# ---------------------------------------------------------------------------


def test_spacy_package_missing_reports_unavailable_with_clear_reason(monkeypatch) -> None:
    _mock_spacy_probe(monkeypatch, _MOCK_SPACY_PACKAGE_MISSING)

    tools = _tools_by_name(
        _report(
            {
                "OMI_LIVE_TOOLS_ENABLED": "true",
                "OMI_LIVE_SPACY_ENABLED": "true",
            }
        )
    )
    spacy_tool = tools["spacy"]

    assert spacy_tool["status"] == "unavailable"
    assert spacy_tool["runtime_dependency_available"] is False
    assert spacy_tool["runtime_dependency_status"] == "unavailable"
    assert spacy_tool["spacy_model_available"] is False
    assert spacy_tool["spacy_model_name"] == "en_core_web_sm"
    assert "not available" in spacy_tool["probe_detail"].lower()


def test_spacy_model_missing_reports_unavailable_with_model_specific_reason(
    monkeypatch,
) -> None:
    _mock_spacy_probe(monkeypatch, _MOCK_SPACY_MODEL_MISSING)

    tools = _tools_by_name(
        _report(
            {
                "OMI_LIVE_TOOLS_ENABLED": "true",
                "OMI_LIVE_SPACY_ENABLED": "true",
            }
        )
    )
    spacy_tool = tools["spacy"]

    assert spacy_tool["status"] == "unavailable"
    assert spacy_tool["runtime_dependency_available"] is False
    assert spacy_tool["runtime_dependency_status"] == "unavailable"
    assert spacy_tool["spacy_model_available"] is False
    assert spacy_tool["spacy_model_name"] == "en_core_web_sm"
    assert "mock model missing" in spacy_tool["probe_detail"]


def test_spacy_package_and_model_available_reports_available(monkeypatch) -> None:
    _mock_spacy_probe(monkeypatch, _MOCK_SPACY_AVAILABLE)

    tools = _tools_by_name(
        _report(
            {
                "OMI_LIVE_TOOLS_ENABLED": "true",
                "OMI_LIVE_SPACY_ENABLED": "true",
            }
        )
    )
    spacy_tool = tools["spacy"]

    assert spacy_tool["status"] == "enabled"
    assert spacy_tool["runtime_dependency_available"] is True
    assert spacy_tool["runtime_dependency_status"] == "available"
    assert spacy_tool["spacy_model_available"] is True
    assert spacy_tool["spacy_model_name"] == "en_core_web_sm"
    assert "loaded successfully" in spacy_tool["probe_detail"]


def test_spacy_model_env_var_changes_reported_model_name(monkeypatch) -> None:
    _mock_spacy_probe(monkeypatch)

    tools = _tools_by_name(
        _report(
            {
                "OMI_LIVE_TOOLS_ENABLED": "true",
                "OMI_LIVE_SPACY_ENABLED": "true",
                "OMI_LIVE_SPACY_MODEL": "en_core_web_md",
            }
        )
    )
    spacy_tool = tools["spacy"]

    assert spacy_tool["spacy_model_name"] == "en_core_web_md"


def test_spacy_blocked_flag_overrides_availability(monkeypatch) -> None:
    _mock_spacy_probe(monkeypatch, _MOCK_SPACY_AVAILABLE)

    tools = _tools_by_name(
        _report(
            {
                "OMI_LIVE_TOOLS_ENABLED": "true",
                "OMI_LIVE_SPACY_ENABLED": "true",
                "OMI_LIVE_SPACY_BLOCKED": "true",
                "OMI_LIVE_SPACY_BLOCKED_REASON": "Owner decision pending.",
            }
        )
    )
    spacy_tool = tools["spacy"]

    assert spacy_tool["status"] == "blocked"
    assert spacy_tool["blocked"] is True
    assert spacy_tool["blocked_reason"] == "Owner decision pending."
    assert spacy_tool["runtime_dependency_available"] is True
    assert spacy_tool["spacy_model_available"] is True


def test_spacy_global_live_tools_disabled_reports_disabled_or_available(monkeypatch) -> None:
    _mock_spacy_probe(monkeypatch, _MOCK_SPACY_AVAILABLE)

    tools = _tools_by_name(_report({"OMI_LIVE_SPACY_ENABLED": "true"}))
    spacy_tool = tools["spacy"]

    assert spacy_tool["global_enabled"] is False
    assert spacy_tool["runtime_enabled"] is False
    assert spacy_tool["status"] in {"disabled", "available"}
    assert spacy_tool["safety"]["read_only"] is True
