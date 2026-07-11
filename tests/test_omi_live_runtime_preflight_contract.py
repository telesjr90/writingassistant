"""PHASE8-IMPL-023-T013 live runtime preflight contract tests.

These tests do not run live OMI tools, call external services, call models,
persist candidates, mutate Memory/Canon, create promotion records, run
apply-promotion, or generate story prose.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest


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


_MOCK_OLLAMA_AVAILABLE = {
    "ollama_base_url": "http://127.0.0.1:11434",
    "ollama_api_available": True,
    "ollama_version": "0.31.1",
    "ollama_model_name": "qwen3:8b",
    "ollama_model_available": True,
    "ollama_probe_detail": (
        "Ollama HTTP API available (version 0.31.1), "
        "model 'qwen3:8b' found in /api/tags"
    ),
}

_MOCK_OLLAMA_UNREACHABLE = {
    "ollama_base_url": "http://127.0.0.1:11434",
    "ollama_api_available": False,
    "ollama_version": None,
    "ollama_model_name": "qwen3:8b",
    "ollama_model_available": False,
    "ollama_probe_detail": (
        "Ollama HTTP API unavailable at http://127.0.0.1:11434: "
        "URLError: Connection refused"
    ),
}

_MOCK_OLLAMA_MODEL_MISSING = {
    "ollama_base_url": "http://127.0.0.1:11434",
    "ollama_api_available": True,
    "ollama_version": "0.31.1",
    "ollama_model_name": "qwen3:8b",
    "ollama_model_available": False,
    "ollama_probe_detail": (
        "Ollama HTTP API available (version 0.31.1), "
        "model 'qwen3:8b' NOT found in /api/tags. "
        "Installed models: nomic-embed-text:latest, phi3:mini"
    ),
}

_MOCK_OLLAMA_INVALID_JSON = {
    "ollama_base_url": "http://127.0.0.1:11434",
    "ollama_api_available": False,
    "ollama_version": None,
    "ollama_model_name": "qwen3:8b",
    "ollama_model_available": False,
    "ollama_probe_detail": (
        "Ollama HTTP API /api/version returned invalid JSON at "
        "http://127.0.0.1:11434: Expecting value: line 1 column 1 (char 0)"
    ),
}


def _mock_ollama_probe(monkeypatch, result: dict | None = None) -> None:
    if result is not None:
        monkeypatch.setattr(
            preflight,
            "_ollama_http_probe",
            lambda base_url, model_name: {
                **result,
                "ollama_base_url": base_url,
                "ollama_model_name": model_name,
            },
        )
    else:
        monkeypatch.setattr(
            preflight,
            "_ollama_http_probe",
            lambda base_url, model_name: {
                **_MOCK_OLLAMA_AVAILABLE,
                "ollama_base_url": base_url,
                "ollama_model_name": model_name,
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
    _mock_ollama_probe(monkeypatch, _MOCK_OLLAMA_UNREACHABLE)

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
    assert tools["ollama_model"]["status"] == "unavailable"
    assert tools["spacy"]["runtime_dependency_status"] == "unavailable"
    assert tools["booknlp"]["runtime_dependency_status"] == "unavailable"
    assert tools["ollama_model"]["runtime_dependency_status"] == "unavailable"


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


# ---------------------------------------------------------------------------
# T015B — Ollama HTTP API preflight and model availability
# ---------------------------------------------------------------------------


def test_ollama_global_live_tools_disabled_reports_disabled_or_available(
    monkeypatch,
) -> None:
    _mock_ollama_probe(monkeypatch, _MOCK_OLLAMA_AVAILABLE)

    tools = _tools_by_name(_report({"OMI_LIVE_OLLAMA_ENABLED": "true"}))
    ollama_tool = tools["ollama_model"]

    assert ollama_tool["global_enabled"] is False
    assert ollama_tool["runtime_enabled"] is False
    assert ollama_tool["status"] in {"disabled", "available"}
    assert ollama_tool["safety"]["read_only"] is True
    assert ollama_tool["safety"]["external_services_called"] is False
    assert ollama_tool["safety"]["live_models_called"] is False


def test_ollama_tool_flag_disabled_reports_available_when_dependency_ready(
    monkeypatch,
) -> None:
    _mock_ollama_probe(monkeypatch, _MOCK_OLLAMA_AVAILABLE)

    tools = _tools_by_name(_report({"OMI_LIVE_TOOLS_ENABLED": "true"}))
    ollama_tool = tools["ollama_model"]

    assert ollama_tool["global_enabled"] is True
    assert ollama_tool["tool_enabled"] is False
    assert ollama_tool["runtime_enabled"] is False
    assert ollama_tool["status"] in {"disabled", "available"}
    assert ollama_tool["ollama_api_available"] is True


def test_ollama_blocked_flag_overrides_http_availability(monkeypatch) -> None:
    _mock_ollama_probe(monkeypatch, _MOCK_OLLAMA_AVAILABLE)

    tools = _tools_by_name(
        _report(
            {
                "OMI_LIVE_TOOLS_ENABLED": "true",
                "OMI_LIVE_OLLAMA_ENABLED": "true",
                "OMI_LIVE_OLLAMA_BLOCKED": "true",
                "OMI_LIVE_OLLAMA_BLOCKED_REASON": "Testing blocked override.",
            }
        )
    )
    ollama_tool = tools["ollama_model"]

    assert ollama_tool["status"] == "blocked"
    assert ollama_tool["blocked"] is True
    assert ollama_tool["blocked_reason"] == "Testing blocked override."
    assert ollama_tool["runtime_dependency_available"] is True
    assert ollama_tool["ollama_api_available"] is True


def test_ollama_http_reachable_with_model_present_reports_available(
    monkeypatch,
) -> None:
    _mock_ollama_probe(monkeypatch, _MOCK_OLLAMA_AVAILABLE)

    tools = _tools_by_name(
        _report(
            {
                "OMI_LIVE_TOOLS_ENABLED": "true",
                "OMI_LIVE_OLLAMA_ENABLED": "true",
            }
        )
    )
    ollama_tool = tools["ollama_model"]

    assert ollama_tool["status"] == "enabled"
    assert ollama_tool["runtime_dependency_available"] is True
    assert ollama_tool["runtime_dependency_status"] == "available"
    assert ollama_tool["ollama_api_available"] is True
    assert ollama_tool["ollama_version"] == "0.31.1"
    assert ollama_tool["ollama_model_available"] is True
    assert ollama_tool["ollama_model_name"] == "qwen3:8b"
    assert "found in /api/tags" in ollama_tool["ollama_probe_detail"]
    assert "found in /api/tags" in ollama_tool["probe_detail"]


def test_ollama_http_reachable_but_model_missing_reports_unavailable(
    monkeypatch,
) -> None:
    _mock_ollama_probe(monkeypatch, _MOCK_OLLAMA_MODEL_MISSING)

    tools = _tools_by_name(
        _report(
            {
                "OMI_LIVE_TOOLS_ENABLED": "true",
                "OMI_LIVE_OLLAMA_ENABLED": "true",
            }
        )
    )
    ollama_tool = tools["ollama_model"]

    assert ollama_tool["status"] == "unavailable"
    assert ollama_tool["runtime_dependency_available"] is False
    assert ollama_tool["runtime_dependency_status"] == "unavailable"
    assert ollama_tool["ollama_api_available"] is True
    assert ollama_tool["ollama_model_available"] is False
    assert ollama_tool["ollama_model_name"] == "qwen3:8b"
    assert "NOT found" in ollama_tool["probe_detail"]


def test_ollama_http_endpoint_unreachable_reports_unavailable(monkeypatch) -> None:
    _mock_ollama_probe(monkeypatch, _MOCK_OLLAMA_UNREACHABLE)

    tools = _tools_by_name(
        _report(
            {
                "OMI_LIVE_TOOLS_ENABLED": "true",
                "OMI_LIVE_OLLAMA_ENABLED": "true",
            }
        )
    )
    ollama_tool = tools["ollama_model"]

    assert ollama_tool["status"] == "unavailable"
    assert ollama_tool["runtime_dependency_available"] is False
    assert ollama_tool["ollama_api_available"] is False
    assert ollama_tool["ollama_version"] is None
    assert ollama_tool["ollama_model_available"] is False
    assert "unavailable" in ollama_tool["probe_detail"].lower()


def test_ollama_invalid_json_fails_closed(monkeypatch) -> None:
    _mock_ollama_probe(monkeypatch, _MOCK_OLLAMA_INVALID_JSON)

    tools = _tools_by_name(
        _report(
            {
                "OMI_LIVE_TOOLS_ENABLED": "true",
                "OMI_LIVE_OLLAMA_ENABLED": "true",
            }
        )
    )
    ollama_tool = tools["ollama_model"]

    assert ollama_tool["status"] == "unavailable"
    assert ollama_tool["ollama_api_available"] is False
    assert ollama_tool["ollama_model_available"] is False
    assert "invalid JSON" in ollama_tool["probe_detail"]


def test_ollama_base_url_env_var_changes_reported_url(monkeypatch) -> None:
    _mock_ollama_probe(monkeypatch)

    tools = _tools_by_name(
        _report(
            {
                "OMI_LIVE_TOOLS_ENABLED": "true",
                "OMI_LIVE_OLLAMA_ENABLED": "true",
                "OMI_LIVE_OLLAMA_BASE_URL": "http://192.168.1.100:11434",
            }
        )
    )
    ollama_tool = tools["ollama_model"]

    assert ollama_tool["ollama_base_url"] == "http://192.168.1.100:11434"


def test_ollama_model_env_var_changes_reported_model(monkeypatch) -> None:
    _mock_ollama_probe(monkeypatch)

    tools = _tools_by_name(
        _report(
            {
                "OMI_LIVE_TOOLS_ENABLED": "true",
                "OMI_LIVE_OLLAMA_ENABLED": "true",
                "OMI_LIVE_OLLAMA_MODEL": "phi3:mini",
            }
        )
    )
    ollama_tool = tools["ollama_model"]

    assert ollama_tool["ollama_model_name"] == "phi3:mini"


# ---------------------------------------------------------------------------
# T016B — Story Check runtime preflight/config/availability check
# ---------------------------------------------------------------------------


def _mock_story_check_probe(
    monkeypatch,
    *,
    analysis_engine: bool = True,
    prompt: bool = True,
    mock_fixture: bool = True,
    analysis_modes: bool = True,
    storyform: bool = True,
    requests_available: bool = True,
) -> None:
    """Patch ``_path_exists`` and ``_find_module`` for the Story Check probe.

    The T016B probe consults a known set of relative paths and the
    ``requests`` Python module. Tests use this helper to flip individual
    dependencies on/off without touching the real repo.
    """

    paths_map: dict[str, bool] = {
        "backend/analysis_engine.py": analysis_engine,
        "backend/prompts/story_check.txt": prompt,
        "backend/mock_responses/story_check.json": mock_fixture,
        "backend/analysis_modes.py": analysis_modes,
        "backend/storyform.py": storyform,
    }

    def fake_path_exists(relative_path: str) -> bool:
        if relative_path in paths_map:
            return paths_map[relative_path]
        return False

    def fake_find_module(module_name: str):
        if module_name == "requests":
            return object() if requests_available else None
        return None

    monkeypatch.setattr(preflight, "_path_exists", fake_path_exists)
    monkeypatch.setattr(preflight.importlib.util, "find_spec", fake_find_module)


def test_story_check_runtime_with_all_surfaces_and_requests_reports_available(
    monkeypatch,
) -> None:
    _mock_story_check_probe(monkeypatch)

    tool = _tools_by_name(_report())["story_check"]

    assert tool["status"] in {"disabled", "available"}
    assert tool["runtime_configured"] is True
    assert tool["runtime_dependency_available"] is True
    assert tool["runtime_dependency_status"] == "available"
    assert tool["story_check_runtime_surface"] == "available"
    assert tool["story_check_analysis_engine_available"] is True
    assert tool["story_check_prompt_available"] is True
    assert tool["story_check_mock_fixture_available"] is True
    assert tool["story_check_analysis_modes_available"] is True
    assert tool["story_check_storyform_surface_available"] is True
    assert tool["story_check_requests_available"] is True
    assert "all present" in tool["story_check_detail"].lower()
    assert tool["story_check_detail"] == tool["probe_detail"]
    assert tool["story_check_ollama_base_url"] == "http://localhost:11434"
    assert tool["story_check_ollama_model_name"] == "qwen3:8b"
    assert tool["story_check_ollama_timeout_seconds"] == 300.0
    assert tool["story_check_analysis_mode_value"] == "ollama_baseline"
    assert tool["story_check_analysis_mode_configured"] is True
    assert tool["safety"]["read_only"] is True
    assert tool["safety"]["external_services_called"] is False
    assert tool["safety"]["live_models_called"] is False


def test_story_check_disabled_by_default_reports_safe_read_only_state(
    monkeypatch,
) -> None:
    _mock_story_check_probe(monkeypatch)

    tool = _tools_by_name(_report())["story_check"]

    assert tool["global_enabled"] is False
    assert tool["tool_enabled"] is False
    assert tool["runtime_enabled"] is False
    assert tool["blocked"] is False
    assert tool["status"] in {"disabled", "available"}
    assert tool["safety"]["read_only"] is True
    assert tool["safety"]["external_services_called"] is False
    assert tool["safety"]["live_models_called"] is False
    assert tool["safety"]["heavy_analysis_executed"] is False


def test_story_check_live_enabled_flag_changes_status_when_runtime_ready(
    monkeypatch,
) -> None:
    _mock_story_check_probe(monkeypatch)

    tool = _tools_by_name(
        _report(
            {
                "OMI_LIVE_TOOLS_ENABLED": "true",
                "OMI_LIVE_STORY_CHECK_ENABLED": "true",
            }
        )
    )["story_check"]

    assert tool["global_enabled"] is True
    assert tool["tool_enabled"] is True
    assert tool["runtime_enabled"] is True
    assert tool["blocked"] is False
    assert tool["runtime_configured"] is True
    assert tool["runtime_dependency_available"] is True
    assert tool["status"] == "enabled"
    assert tool["safety"]["read_only"] is True
    assert tool["safety"]["external_services_called"] is False


def test_story_check_live_enabled_but_unconfigured_reports_not_configured(
    monkeypatch,
) -> None:
    _mock_story_check_probe(monkeypatch, prompt=False)

    tool = _tools_by_name(
        _report(
            {
                "OMI_LIVE_TOOLS_ENABLED": "true",
                "OMI_LIVE_STORY_CHECK_ENABLED": "true",
            }
        )
    )["story_check"]

    assert tool["runtime_enabled"] is True
    assert tool["runtime_configured"] is False
    assert tool["runtime_dependency_available"] is False
    assert tool["runtime_dependency_status"] in {"not_configured", "unavailable"}
    assert tool["status"] == "not_configured"
    assert tool["story_check_prompt_available"] is False
    assert "prompts/story_check.txt" in tool["story_check_detail"]


def test_story_check_blocked_flag_overrides_available_runtime(
    monkeypatch,
) -> None:
    _mock_story_check_probe(monkeypatch)

    tool = _tools_by_name(
        _report(
            {
                "OMI_LIVE_TOOLS_ENABLED": "true",
                "OMI_LIVE_STORY_CHECK_ENABLED": "true",
                "OMI_LIVE_STORY_CHECK_BLOCKED": "true",
                "OMI_LIVE_STORY_CHECK_BLOCKED_REASON": "Owner decision pending.",
            }
        )
    )["story_check"]

    assert tool["runtime_enabled"] is True
    assert tool["runtime_dependency_available"] is True
    assert tool["blocked"] is True
    assert tool["blocked_reason"] == "Owner decision pending."
    assert tool["status"] == "blocked"


def test_story_check_missing_prompt_file_reports_unavailable_safely(
    monkeypatch,
) -> None:
    _mock_story_check_probe(monkeypatch, prompt=False)

    tool = _tools_by_name(
        _report(
            {
                "OMI_LIVE_TOOLS_ENABLED": "true",
                "OMI_LIVE_STORY_CHECK_ENABLED": "true",
            }
        )
    )["story_check"]

    assert tool["story_check_prompt_available"] is False
    assert tool["runtime_configured"] is False
    assert tool["runtime_dependency_available"] is False
    assert tool["runtime_dependency_status"] in {"not_configured", "unavailable"}
    assert tool["status"] in {"not_configured", "unavailable"}
    assert "prompts/story_check.txt" in tool["story_check_detail"]


def test_story_check_missing_mock_fixture_reports_partial_availability(
    monkeypatch,
) -> None:
    """Missing mock fixture is reported but does not block the live runtime.

    The mock fixture is only required for ``ANALYSIS_MODE=mock``; the live
    path still needs the analysis engine, prompt, analysis_modes,
    storyform, and ``requests``. T016B chooses to treat the mock fixture as
    a partial-availability signal: when only the mock fixture is missing,
    the probe remains available but reports ``mock_fixture_available:
    False`` and a partial-availability detail.
    """
    _mock_story_check_probe(monkeypatch, mock_fixture=False)

    tool = _tools_by_name(
        _report(
            {
                "OMI_LIVE_TOOLS_ENABLED": "true",
                "OMI_LIVE_STORY_CHECK_ENABLED": "true",
            }
        )
    )["story_check"]

    assert tool["story_check_mock_fixture_available"] is False
    assert tool["runtime_configured"] is True
    assert tool["runtime_dependency_available"] is True
    assert tool["runtime_dependency_status"] == "available"
    assert tool["status"] == "enabled"
    assert "mock_responses/story_check.json" in tool["story_check_detail"]


def test_story_check_missing_requests_package_reports_unavailable(
    monkeypatch,
) -> None:
    _mock_story_check_probe(monkeypatch, requests_available=False)

    tool = _tools_by_name(
        _report(
            {
                "OMI_LIVE_TOOLS_ENABLED": "true",
                "OMI_LIVE_STORY_CHECK_ENABLED": "true",
            }
        )
    )["story_check"]

    assert tool["story_check_requests_available"] is False
    assert tool["runtime_configured"] is False
    assert tool["runtime_dependency_available"] is False
    assert tool["runtime_dependency_status"] in {"not_configured", "unavailable"}
    assert tool["status"] in {"not_configured", "unavailable"}
    assert "python:requests" in tool["story_check_detail"]


def test_story_check_missing_analysis_engine_reports_unavailable(
    monkeypatch,
) -> None:
    _mock_story_check_probe(monkeypatch, analysis_engine=False)

    tool = _tools_by_name(
        _report(
            {
                "OMI_LIVE_TOOLS_ENABLED": "true",
                "OMI_LIVE_STORY_CHECK_ENABLED": "true",
            }
        )
    )["story_check"]

    assert tool["story_check_analysis_engine_available"] is False
    assert tool["runtime_configured"] is False
    assert tool["runtime_dependency_available"] is False
    assert tool["runtime_dependency_status"] in {"not_configured", "unavailable"}
    assert tool["status"] in {"not_configured", "unavailable"}
    assert "analysis_engine.py" in tool["story_check_detail"]


def test_story_check_preflight_does_not_call_run_story_check(monkeypatch) -> None:
    _mock_story_check_probe(monkeypatch)

    calls: list[tuple[str, str]] = []

    class _Sentinel:
        def __call__(self, *args, **kwargs):  # pragma: no cover - never reached
            calls.append(("args", args))
            raise AssertionError(
                "run_story_check must not be called from preflight"
            )

    sentinel = _Sentinel()
    monkeypatch.setattr(
        "backend.analysis_engine.run_story_check",
        sentinel,
        raising=False,
    )

    report = _report(
        {
            "OMI_LIVE_TOOLS_ENABLED": "true",
            "OMI_LIVE_STORY_CHECK_ENABLED": "true",
        }
    )

    assert calls == []
    tool = _tools_by_name(report)["story_check"]
    assert tool["safety"]["read_only"] is True
    assert tool["safety"]["external_services_called"] is False
    assert tool["safety"]["live_models_called"] is False
    assert tool["safety"]["heavy_analysis_executed"] is False


def test_story_check_preflight_does_not_call_ollama_or_network(
    monkeypatch,
) -> None:
    _mock_story_check_probe(monkeypatch)
    _mock_ollama_probe(monkeypatch, _MOCK_OLLAMA_UNREACHABLE)

    network_attempts: list[tuple[str, tuple]] = []

    def fake_urlopen(*args, **kwargs):
        network_attempts.append(("urlopen", args))
        raise AssertionError(
            "urllib urlopen must not be called by Story Check preflight"
        )

    def fake_request(*args, **kwargs):
        network_attempts.append(("request", args))
        raise AssertionError(
            "urllib Request must not be called by Story Check preflight"
        )

    def fake_requests_post(*args, **kwargs):
        network_attempts.append(("requests.post", args))
        raise AssertionError(
            "requests.post must not be called by Story Check preflight"
        )

    def fake_requests_get(*args, **kwargs):
        network_attempts.append(("requests.get", args))
        raise AssertionError(
            "requests.get must not be called by Story Check preflight"
        )

    import urllib.request

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(urllib.request, "Request", fake_request)
    monkeypatch.setattr("requests.post", fake_requests_post, raising=False)
    monkeypatch.setattr("requests.get", fake_requests_get, raising=False)

    report = _report(
        {
            "OMI_LIVE_TOOLS_ENABLED": "true",
            "OMI_LIVE_STORY_CHECK_ENABLED": "true",
            "OMI_LIVE_OLLAMA_BASE_URL": "http://172.25.144.1:11434",
            "OMI_LIVE_OLLAMA_MODEL": "qwen3:8b",
        }
    )

    assert network_attempts == []
    tool = _tools_by_name(report)["story_check"]
    assert tool["safety"]["external_services_called"] is False
    assert tool["safety"]["live_models_called"] is False
    assert tool["safety"]["heavy_analysis_executed"] is False


def test_story_check_ollama_config_env_vars_are_surfaced_read_only(
    monkeypatch,
) -> None:
    _mock_story_check_probe(monkeypatch)

    tool = _tools_by_name(
        _report(
            {
                "OLLAMA_BASE_URL": "http://172.25.144.1:11434",
                "OLLAMA_MODEL": "phi3:mini",
                "OLLAMA_TIMEOUT_SECONDS": "180",
                "ANALYSIS_MODE": "mock",
            }
        )
    )["story_check"]

    assert tool["story_check_ollama_base_url"] == "http://172.25.144.1:11434"
    assert tool["story_check_ollama_model_name"] == "phi3:mini"
    assert tool["story_check_ollama_timeout_seconds"] == 180.0
    assert tool["story_check_analysis_mode_value"] == "mock"
    assert tool["story_check_analysis_mode_configured"] is True


def test_story_check_invalid_analysis_mode_falls_back_to_default(
    monkeypatch,
) -> None:
    _mock_story_check_probe(monkeypatch)

    tool = _tools_by_name(
        _report(
            {
                "ANALYSIS_MODE": "bogus-mode",
            }
        )
    )["story_check"]

    assert tool["story_check_analysis_mode_value"] == "ollama_baseline"
    assert tool["story_check_analysis_mode_configured"] is False


def test_story_check_invalid_ollama_timeout_falls_back_to_default(
    monkeypatch,
) -> None:
    _mock_story_check_probe(monkeypatch)

    tool = _tools_by_name(_report({"OLLAMA_TIMEOUT_SECONDS": "not-a-number"}))[
        "story_check"
    ]

    assert tool["story_check_ollama_timeout_seconds"] == 300.0


def test_story_check_missing_storyform_or_analysis_modes_reports_unavailable(
    monkeypatch,
) -> None:
    _mock_story_check_probe(monkeypatch, storyform=False, analysis_modes=False)

    tool = _tools_by_name(
        _report(
            {
                "OMI_LIVE_TOOLS_ENABLED": "true",
                "OMI_LIVE_STORY_CHECK_ENABLED": "true",
            }
        )
    )["story_check"]

    assert tool["story_check_storyform_surface_available"] is False
    assert tool["story_check_analysis_modes_available"] is False
    assert tool["runtime_configured"] is False
    assert tool["runtime_dependency_available"] is False
    assert tool["runtime_dependency_status"] in {"not_configured", "unavailable"}
    assert tool["status"] in {"not_configured", "unavailable"}
    assert "storyform.py" in tool["story_check_detail"]
    assert "analysis_modes.py" in tool["story_check_detail"]


def test_story_check_preflight_does_not_persist_or_promote(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)
    project_manager.create_omi_idea("demo", "Owner-authored preflight note.")
    before = project_manager.get_omi_summary("demo")

    _mock_story_check_probe(monkeypatch)

    report = _report(
        {
            "OMI_LIVE_TOOLS_ENABLED": "true",
            "OMI_LIVE_STORY_CHECK_ENABLED": "true",
        }
    )

    after = project_manager.get_omi_summary("demo")
    assert after == before
    tool = _tools_by_name(report)["story_check"]
    assert tool["safety"]["candidate_persistence"] is False
    assert tool["safety"]["memory_canon_mutation"] is False
    assert tool["safety"]["promotion_or_apply_promotion"] is False
    assert tool["safety"]["story_prose_generated"] is False


# ---------------------------------------------------------------------------
# T017A — BookNLP runtime preflight after install
# ---------------------------------------------------------------------------

_MOCK_BOOKNLP_ALL_AVAILABLE: dict[str, object] = {
    "booknlp_runtime_surface": "available",
    "booknlp_package_available": True,
    "booknlp_package_version": "1.0.8",
    "booknlp_module_available": True,
    "booknlp_entrypoint_available": True,
    "booknlp_spacy_available": True,
    "booknlp_spacy_version": "3.8.14",
    "booknlp_spacy_model_available": True,
    "booknlp_tensorflow_available": True,
    "booknlp_tensorflow_version": "2.21.0",
    "booknlp_torch_available": True,
    "booknlp_torch_version": "2.10.0+cu129",
    "booknlp_transformers_available": True,
    "booknlp_transformers_version": "5.5.0",
    "booknlp_setuptools_available": True,
    "booknlp_setuptools_version": "80.9.0",
    "booknlp_pkg_resources_available": True,
    "booknlp_setuptools_compatibility_detail": (
        "setuptools==80.9.0, pkg_resources available: "
        "compatible with BookNLP import"
    ),
    "booknlp_detail": (
        "BookNLP package 1.0.8 available; booknlp.booknlp entrypoint available; "
        "spaCy: available; en_core_web_sm: available; "
        "tensorflow: available; torch: available; "
        "transformers: available; pkg_resources available; "
        "torch=2.10.0+cu129 < 2.11 (cpp extensions skipped, non-blocking for import)"
    ),
}

_MOCK_BOOKNLP_PACKAGE_MISSING: dict[str, object] = {
    "booknlp_runtime_surface": "unavailable",
    "booknlp_package_available": False,
    "booknlp_package_version": None,
    "booknlp_module_available": False,
    "booknlp_entrypoint_available": False,
    "booknlp_spacy_available": False,
    "booknlp_spacy_version": None,
    "booknlp_spacy_model_available": False,
    "booknlp_tensorflow_available": False,
    "booknlp_tensorflow_version": None,
    "booknlp_torch_available": False,
    "booknlp_torch_version": None,
    "booknlp_transformers_available": False,
    "booknlp_transformers_version": None,
    "booknlp_setuptools_available": False,
    "booknlp_setuptools_version": None,
    "booknlp_pkg_resources_available": False,
    "booknlp_setuptools_compatibility_detail": (
        "setuptools not available: BookNLP needs pkg_resources"
    ),
    "booknlp_detail": "BookNLP package NOT available",
}

_MOCK_BOOKNLP_ENTRYPOINT_MISSING: dict[str, object] = {
    "booknlp_runtime_surface": "degraded",
    "booknlp_package_available": True,
    "booknlp_package_version": "1.0.8",
    "booknlp_module_available": False,
    "booknlp_entrypoint_available": False,
    "booknlp_spacy_available": True,
    "booknlp_spacy_version": "3.8.14",
    "booknlp_spacy_model_available": True,
    "booknlp_tensorflow_available": True,
    "booknlp_tensorflow_version": "2.21.0",
    "booknlp_torch_available": True,
    "booknlp_torch_version": "2.10.0+cu129",
    "booknlp_transformers_available": True,
    "booknlp_transformers_version": "5.5.0",
    "booknlp_setuptools_available": True,
    "booknlp_setuptools_version": "80.9.0",
    "booknlp_pkg_resources_available": True,
    "booknlp_setuptools_compatibility_detail": (
        "setuptools==80.9.0, pkg_resources available: "
        "compatible with BookNLP import"
    ),
    "booknlp_detail": (
        "BookNLP package 1.0.8 available; "
        "booknlp.booknlp entrypoint NOT available; "
        "spaCy: available; en_core_web_sm: available; "
        "tensorflow: available; torch: available; "
        "transformers: available; pkg_resources available; "
        "torch=2.10.0+cu129 < 2.11 (cpp extensions skipped, non-blocking for import)"
    ),
}

_MOCK_BOOKNLP_SPACY_MODEL_MISSING: dict[str, object] = {
    "booknlp_runtime_surface": "available",
    "booknlp_package_available": True,
    "booknlp_package_version": "1.0.8",
    "booknlp_module_available": True,
    "booknlp_entrypoint_available": True,
    "booknlp_spacy_available": True,
    "booknlp_spacy_version": "3.8.14",
    "booknlp_spacy_model_available": False,
    "booknlp_tensorflow_available": True,
    "booknlp_tensorflow_version": "2.21.0",
    "booknlp_torch_available": True,
    "booknlp_torch_version": "2.10.0+cu129",
    "booknlp_transformers_available": True,
    "booknlp_transformers_version": "5.5.0",
    "booknlp_setuptools_available": True,
    "booknlp_setuptools_version": "80.9.0",
    "booknlp_pkg_resources_available": True,
    "booknlp_setuptools_compatibility_detail": (
        "setuptools==80.9.0, pkg_resources available: "
        "compatible with BookNLP import"
    ),
    "booknlp_detail": (
        "BookNLP package 1.0.8 available; booknlp.booknlp entrypoint available; "
        "spaCy: available; en_core_web_sm: NOT available; "
        "tensorflow: available; torch: available; "
        "transformers: available; pkg_resources available; "
        "torch=2.10.0+cu129 < 2.11 (cpp extensions skipped, non-blocking for import)"
    ),
}

_MOCK_BOOKNLP_PKG_RESOURCES_MISSING: dict[str, object] = {
    "booknlp_runtime_surface": "available",
    "booknlp_package_available": True,
    "booknlp_package_version": "1.0.8",
    "booknlp_module_available": True,
    "booknlp_entrypoint_available": True,
    "booknlp_spacy_available": True,
    "booknlp_spacy_version": "3.8.14",
    "booknlp_spacy_model_available": True,
    "booknlp_tensorflow_available": True,
    "booknlp_tensorflow_version": "2.21.0",
    "booknlp_torch_available": True,
    "booknlp_torch_version": "2.10.0+cu129",
    "booknlp_transformers_available": True,
    "booknlp_transformers_version": "5.5.0",
    "booknlp_setuptools_available": True,
    "booknlp_setuptools_version": "82.0.1",
    "booknlp_pkg_resources_available": False,
    "booknlp_setuptools_compatibility_detail": (
        "setuptools==82.0.1, pkg_resources NOT available: "
        "BookNLP needs pkg_resources; pin setuptools<81"
    ),
    "booknlp_detail": (
        "BookNLP package 1.0.8 available; booknlp.booknlp entrypoint available; "
        "spaCy: available; en_core_web_sm: available; "
        "tensorflow: available; torch: available; "
        "transformers: available; "
        "pkg_resources NOT available (pin setuptools<81); "
        "torch=2.10.0+cu129 < 2.11 (cpp extensions skipped, non-blocking for import)"
    ),
}

_MOCK_BOOKNLP_SETUPTOOLS_80_9: dict[str, object] = {
    "booknlp_runtime_surface": "available",
    "booknlp_package_available": True,
    "booknlp_package_version": "1.0.8",
    "booknlp_module_available": True,
    "booknlp_entrypoint_available": True,
    "booknlp_spacy_available": True,
    "booknlp_spacy_version": "3.8.14",
    "booknlp_spacy_model_available": True,
    "booknlp_tensorflow_available": True,
    "booknlp_tensorflow_version": "2.21.0",
    "booknlp_torch_available": True,
    "booknlp_torch_version": "2.10.0+cu129",
    "booknlp_transformers_available": True,
    "booknlp_transformers_version": "5.5.0",
    "booknlp_setuptools_available": True,
    "booknlp_setuptools_version": "80.9.0",
    "booknlp_pkg_resources_available": True,
    "booknlp_setuptools_compatibility_detail": (
        "setuptools==80.9.0, pkg_resources available: "
        "compatible with BookNLP import"
    ),
    "booknlp_detail": (
        "BookNLP package 1.0.8 available; booknlp.booknlp entrypoint available; "
        "spaCy: available; en_core_web_sm: available; "
        "tensorflow: available; torch: available; "
        "transformers: available; pkg_resources available; "
        "torch=2.10.0+cu129 < 2.11 (cpp extensions skipped, non-blocking for import)"
    ),
}

_MOCK_BOOKNLP_TORCH_CAVEAT: dict[str, object] = {
    "booknlp_runtime_surface": "available",
    "booknlp_package_available": True,
    "booknlp_package_version": "1.0.8",
    "booknlp_module_available": True,
    "booknlp_entrypoint_available": True,
    "booknlp_spacy_available": True,
    "booknlp_spacy_version": "3.8.14",
    "booknlp_spacy_model_available": True,
    "booknlp_tensorflow_available": True,
    "booknlp_tensorflow_version": "2.21.0",
    "booknlp_torch_available": True,
    "booknlp_torch_version": "2.10.0+cu129",
    "booknlp_transformers_available": True,
    "booknlp_transformers_version": "5.5.0",
    "booknlp_setuptools_available": True,
    "booknlp_setuptools_version": "80.9.0",
    "booknlp_pkg_resources_available": True,
    "booknlp_setuptools_compatibility_detail": (
        "setuptools==80.9.0, pkg_resources available: "
        "compatible with BookNLP import"
    ),
    "booknlp_detail": (
        "BookNLP package 1.0.8 available; booknlp.booknlp entrypoint available; "
        "spaCy: available; en_core_web_sm: available; "
        "tensorflow: available; torch: available; "
        "transformers: available; pkg_resources available; "
        "torch=2.10.0+cu129 < 2.11 (cpp extensions skipped, non-blocking for import)"
    ),
}


def _mock_booknlp_probe(monkeypatch, result: dict[str, object] | None = None) -> None:
    if result is not None:
        monkeypatch.setattr(
            preflight,
            "_booknlp_runtime_probe",
            lambda: dict(result),
        )
    else:
        monkeypatch.setattr(
            preflight,
            "_booknlp_runtime_probe",
            lambda: dict(_MOCK_BOOKNLP_ALL_AVAILABLE),
        )


def test_booknlp_preflight_disabled_by_default_remains_safe() -> None:
    report = _report()
    tools = _tools_by_name(report)

    tool = tools["booknlp"]
    assert tool["global_enabled"] is False
    assert tool["tool_enabled"] is False
    assert tool["runtime_enabled"] is False
    assert tool["blocked"] is False
    assert tool["status"] in {"disabled", "available"}
    assert tool["safety"]["read_only"] is True
    assert tool["safety"]["heavy_analysis_executed"] is False
    assert tool["safety"]["external_services_called"] is False
    assert tool["safety"]["live_models_called"] is False
    assert tool["safety"]["candidate_persistence"] is False
    assert tool["safety"]["memory_canon_mutation"] is False
    assert tool["safety"]["promotion_or_apply_promotion"] is False
    assert tool["safety"]["story_prose_generated"] is False


def test_booknlp_enabled_with_all_dependencies_reports_enabled(
    monkeypatch,
) -> None:
    _mock_booknlp_probe(monkeypatch, _MOCK_BOOKNLP_ALL_AVAILABLE)

    tool = _tools_by_name(
        _report(
            {
                "OMI_LIVE_TOOLS_ENABLED": "true",
                "OMI_LIVE_BOOKNLP_ENABLED": "true",
            }
        )
    )["booknlp"]

    assert tool["status"] == "enabled"
    assert tool["runtime_dependency_available"] is True
    assert tool["runtime_dependency_status"] == "available"
    assert tool["booknlp_runtime_surface"] == "available"
    assert tool["booknlp_package_available"] is True
    assert tool["booknlp_package_version"] == "1.0.8"
    assert tool["booknlp_module_available"] is True
    assert tool["booknlp_entrypoint_available"] is True
    assert tool["booknlp_spacy_available"] is True
    assert tool["booknlp_spacy_version"] == "3.8.14"
    assert tool["booknlp_spacy_model_available"] is True
    assert tool["booknlp_tensorflow_available"] is True
    assert tool["booknlp_tensorflow_version"] == "2.21.0"
    assert tool["booknlp_torch_available"] is True
    assert tool["booknlp_torch_version"] == "2.10.0+cu129"
    assert tool["booknlp_transformers_available"] is True
    assert tool["booknlp_transformers_version"] == "5.5.0"
    assert tool["booknlp_setuptools_available"] is True
    assert tool["booknlp_setuptools_version"] == "80.9.0"
    assert tool["booknlp_pkg_resources_available"] is True
    assert "compatible" in tool["booknlp_setuptools_compatibility_detail"]
    assert "BookNLP package" in tool["booknlp_detail"]
    assert tool["safety"]["read_only"] is True
    assert tool["safety"]["heavy_analysis_executed"] is False


def test_booknlp_missing_package_reports_unavailable(
    monkeypatch,
) -> None:
    _mock_booknlp_probe(monkeypatch, _MOCK_BOOKNLP_PACKAGE_MISSING)

    tool = _tools_by_name(
        _report(
            {
                "OMI_LIVE_TOOLS_ENABLED": "true",
                "OMI_LIVE_BOOKNLP_ENABLED": "true",
            }
        )
    )["booknlp"]

    assert tool["status"] == "unavailable"
    assert tool["runtime_dependency_available"] is False
    assert tool["runtime_dependency_status"] == "unavailable"
    assert tool["booknlp_runtime_surface"] == "unavailable"
    assert tool["booknlp_package_available"] is False
    assert tool["booknlp_entrypoint_available"] is False
    assert "NOT available" in tool["probe_detail"]
    assert tool["safety"]["heavy_analysis_executed"] is False


def test_booknlp_missing_entrypoint_reports_degraded_with_clear_detail(
    monkeypatch,
) -> None:
    _mock_booknlp_probe(monkeypatch, _MOCK_BOOKNLP_ENTRYPOINT_MISSING)

    tool = _tools_by_name(
        _report(
            {
                "OMI_LIVE_TOOLS_ENABLED": "true",
                "OMI_LIVE_BOOKNLP_ENABLED": "true",
            }
        )
    )["booknlp"]

    assert tool["status"] == "unavailable"
    assert tool["runtime_dependency_available"] is False
    assert tool["booknlp_runtime_surface"] == "degraded"
    assert tool["booknlp_package_available"] is True
    assert tool["booknlp_module_available"] is False
    assert tool["booknlp_entrypoint_available"] is False
    assert "entrypoint NOT available" in tool["probe_detail"]


def test_booknlp_missing_spacy_model_reports_degraded_with_clear_detail(
    monkeypatch,
) -> None:
    _mock_booknlp_probe(monkeypatch, _MOCK_BOOKNLP_SPACY_MODEL_MISSING)

    tool = _tools_by_name(
        _report(
            {
                "OMI_LIVE_TOOLS_ENABLED": "true",
                "OMI_LIVE_BOOKNLP_ENABLED": "true",
            }
        )
    )["booknlp"]

    assert tool["status"] == "enabled"
    assert tool["runtime_dependency_available"] is True
    assert tool["booknlp_runtime_surface"] == "available"
    assert tool["booknlp_spacy_available"] is True
    assert tool["booknlp_spacy_model_available"] is False
    assert "en_core_web_sm: NOT available" in tool["booknlp_detail"]


def test_booknlp_missing_pkg_resources_reports_setuptools_compatibility_detail(
    monkeypatch,
) -> None:
    _mock_booknlp_probe(monkeypatch, _MOCK_BOOKNLP_PKG_RESOURCES_MISSING)

    tool = _tools_by_name(
        _report(
            {
                "OMI_LIVE_TOOLS_ENABLED": "true",
                "OMI_LIVE_BOOKNLP_ENABLED": "true",
            }
        )
    )["booknlp"]

    assert tool["status"] == "enabled"
    assert tool["booknlp_setuptools_version"] == "82.0.1"
    assert tool["booknlp_pkg_resources_available"] is False
    assert "pin setuptools<81" in tool["booknlp_setuptools_compatibility_detail"]
    assert "pkg_resources NOT available" in tool["booknlp_detail"]


def test_booknlp_setuptools_80_9_with_pkg_resources_reports_compatible(
    monkeypatch,
) -> None:
    _mock_booknlp_probe(monkeypatch, _MOCK_BOOKNLP_SETUPTOOLS_80_9)

    tool = _tools_by_name(
        _report(
            {
                "OMI_LIVE_TOOLS_ENABLED": "true",
                "OMI_LIVE_BOOKNLP_ENABLED": "true",
            }
        )
    )["booknlp"]

    assert tool["booknlp_setuptools_version"] == "80.9.0"
    assert tool["booknlp_pkg_resources_available"] is True
    assert "compatible" in tool["booknlp_setuptools_compatibility_detail"]


def test_booknlp_torch_caveat_does_not_by_itself_fail_availability(
    monkeypatch,
) -> None:
    _mock_booknlp_probe(monkeypatch, _MOCK_BOOKNLP_TORCH_CAVEAT)

    tool = _tools_by_name(
        _report(
            {
                "OMI_LIVE_TOOLS_ENABLED": "true",
                "OMI_LIVE_BOOKNLP_ENABLED": "true",
            }
        )
    )["booknlp"]

    assert tool["status"] == "enabled"
    assert tool["booknlp_torch_available"] is True
    assert tool["booknlp_torch_version"] == "2.10.0+cu129"
    assert tool["runtime_dependency_available"] is True
    assert "cpp extensions skipped" in tool["booknlp_detail"]


def test_booknlp_blocked_flag_overrides_availability(
    monkeypatch,
) -> None:
    _mock_booknlp_probe(monkeypatch, _MOCK_BOOKNLP_ALL_AVAILABLE)

    tool = _tools_by_name(
        _report(
            {
                "OMI_LIVE_TOOLS_ENABLED": "true",
                "OMI_LIVE_BOOKNLP_ENABLED": "true",
                "OMI_LIVE_BOOKNLP_BLOCKED": "true",
                "OMI_LIVE_BOOKNLP_BLOCKED_REASON": (
                    "Owner decision pending."
                ),
            }
        )
    )["booknlp"]

    assert tool["status"] == "blocked"
    assert tool["blocked"] is True
    assert tool["blocked_reason"] == "Owner decision pending."
    assert tool["runtime_dependency_available"] is True


def test_booknlp_preflight_does_not_invoke_booknlp_processing(
    monkeypatch,
) -> None:
    _mock_booknlp_probe(monkeypatch, _MOCK_BOOKNLP_ALL_AVAILABLE)

    booknlp_calls: list[tuple] = []

    class _ProcessingSentinel:
        def process(self, *args, **kwargs):
            booknlp_calls.append(("process", args, kwargs))
            raise AssertionError(
                "BookNLP.process must not be called from preflight"
            )

    monkeypatch.setattr(
        preflight,
        "_booknlp_runtime_probe",
        lambda: dict(_MOCK_BOOKNLP_ALL_AVAILABLE),
    )

    report = _report(
        {
            "OMI_LIVE_TOOLS_ENABLED": "true",
            "OMI_LIVE_BOOKNLP_ENABLED": "true",
        }
    )

    assert booknlp_calls == []
    tool = _tools_by_name(report)["booknlp"]
    assert tool["safety"]["read_only"] is True
    assert tool["safety"]["heavy_analysis_executed"] is False


def test_booknlp_preflight_does_not_persist_or_mutate(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)
    project_manager.create_omi_idea("demo", "Owner-authored preflight note.")
    before = project_manager.get_omi_summary("demo")

    _mock_booknlp_probe(monkeypatch, _MOCK_BOOKNLP_ALL_AVAILABLE)

    report = _report(
        {
            "OMI_LIVE_TOOLS_ENABLED": "true",
            "OMI_LIVE_BOOKNLP_ENABLED": "true",
        }
    )

    after = project_manager.get_omi_summary("demo")
    assert after == before
    tool = _tools_by_name(report)["booknlp"]
    assert tool["safety"]["candidate_persistence"] is False
    assert tool["safety"]["memory_canon_mutation"] is False
    assert tool["safety"]["promotion_or_apply_promotion"] is False
    assert tool["safety"]["story_prose_generated"] is False


# ---------------------------------------------------------------------------
# T018A — NCP schema-validator preflight
# ---------------------------------------------------------------------------


def _all_ncp_surfaces_available_result() -> dict[str, object]:
    return {
        "ncp_runtime_surface": "available",
        "ncp_source_path": ".external_sources/narrative-context-protocol",
        "ncp_source_available": True,
        "ncp_package_json_available": True,
        "ncp_schema_json_available": True,
        "ncp_schema_yaml_available": True,
        "ncp_validate_schema_script_available": True,
        "ncp_validate_file_script_available": True,
        "ncp_validate_schema_package_script_available": True,
        "ncp_validate_file_package_script_available": True,
        "ncp_node_available": True,
        "ncp_node_path": "/usr/bin/node",
        "ncp_npm_available": True,
        "ncp_npm_path": "/usr/bin/npm",
        "ncp_node_modules_available": True,
        "ncp_validator_available": True,
        "ncp_validator_status": "available",
        "ncp_audit_caveat": (
            "ajv moderate; fast-uri high; do not run npm audit fix"
        ),
        "ncp_input_path_env": "OMI_LIVE_NCP_INPUT_PATH",
        "ncp_input_path_configured": False,
        "ncp_input_path_value": "",
        "ncp_validate_with_node_env": "OMI_LIVE_NCP_VALIDATE_WITH_NODE",
        "ncp_validate_with_node_enabled": False,
        "ncp_detail": "all present",
    }


def _patch_ncp_probe(
    monkeypatch,
    result: dict[str, object] | None = None,
    *,
    env_aware: bool = False,
) -> None:
    """Patch ``_ncp_runtime_probe`` for tests that must not depend on the
    real ``.external_sources/narrative-context-protocol`` tree, real node,
    or real npm. T018B takes an optional env argument; the patch accepts
    any args and returns a fresh copy of the result dict so per-test
    mutations cannot leak.

    When ``env_aware`` is True, the patched probe mirrors the real
    implementation's behavior of surfacing the explicit
    ``OMI_LIVE_NCP_INPUT_PATH`` and ``OMI_LIVE_NCP_VALIDATE_WITH_NODE``
    env vars as configuration. Otherwise the patched probe returns the
    static result dict unchanged.
    """
    if result is None:
        result = _all_ncp_surfaces_available_result()

    def _patched(env: object | None = None) -> dict[str, object]:
        output = {key: value for key, value in result.items()}
        if env_aware and env is not None:
            mapping = dict(env)
            raw_path = str(mapping.get("OMI_LIVE_NCP_INPUT_PATH", "") or "")
            output["ncp_input_path_value"] = raw_path.strip()
            output["ncp_input_path_configured"] = bool(
                output["ncp_input_path_value"]
            )
            raw_vwn = str(
                mapping.get("OMI_LIVE_NCP_VALIDATE_WITH_NODE", "") or ""
            )
            output["ncp_validate_with_node_enabled"] = (
                raw_vwn.strip().lower() in {"1", "true", "yes", "on"}
            )
        return output

    monkeypatch.setattr(preflight, "_ncp_runtime_probe", _patched)


def test_ncp_preflight_disabled_by_default_remains_safe_read_only() -> None:
    report = _report()
    tool = _tools_by_name(report)["ncp"]

    assert tool["global_enabled"] is False
    assert tool["tool_enabled"] is False
    assert tool["runtime_enabled"] is False
    assert tool["blocked"] is False
    assert tool["status"] in {"disabled", "available"}
    assert tool["safety"]["read_only"] is True
    assert tool["safety"]["heavy_analysis_executed"] is False
    assert tool["safety"]["external_services_called"] is False
    assert tool["safety"]["live_models_called"] is False
    assert tool["safety"]["candidate_persistence"] is False
    assert tool["safety"]["memory_canon_mutation"] is False
    assert tool["safety"]["promotion_or_apply_promotion"] is False
    assert tool["safety"]["story_prose_generated"] is False


def test_ncp_all_surfaces_and_node_npm_available_reports_validator_available(
    monkeypatch,
) -> None:
    _patch_ncp_probe(monkeypatch, _all_ncp_surfaces_available_result())

    tool = _tools_by_name(
        _report(
            {
                "OMI_LIVE_TOOLS_ENABLED": "true",
                "OMI_LIVE_NCP_ENABLED": "true",
            }
        )
    )["ncp"]

    assert tool["status"] == "enabled"
    assert tool["runtime_enabled"] is True
    assert tool["runtime_dependency_available"] is True
    assert tool["runtime_dependency_status"] == "available"
    assert tool["ncp_runtime_surface"] == "available"
    assert tool["ncp_source_path"] == ".external_sources/narrative-context-protocol"
    assert tool["ncp_source_available"] is True
    assert tool["ncp_package_json_available"] is True
    assert tool["ncp_schema_json_available"] is True
    assert tool["ncp_schema_yaml_available"] is True
    assert tool["ncp_validate_schema_script_available"] is True
    assert tool["ncp_validate_file_script_available"] is True
    assert tool["ncp_validate_schema_package_script_available"] is True
    assert tool["ncp_validate_file_package_script_available"] is True
    assert tool["ncp_node_available"] is True
    assert tool["ncp_npm_available"] is True
    assert tool["ncp_node_modules_available"] is True
    assert tool["ncp_validator_available"] is True
    assert tool["ncp_validator_status"] == "available"
    assert "ajv" in tool["ncp_audit_caveat"]
    assert "fast-uri" in tool["ncp_audit_caveat"]
    assert tool["safety"]["read_only"] is True


def test_ncp_missing_source_reports_unavailable_with_clear_detail(
    monkeypatch,
) -> None:
    bad = _all_ncp_surfaces_available_result()
    bad["ncp_source_available"] = False
    bad["ncp_runtime_surface"] = "unavailable"
    bad["ncp_validator_available"] = False
    bad["ncp_validator_status"] = "unavailable"
    bad["ncp_detail"] = (
        "NCP schema-validator surface probe missing: "
        ".external_sources/narrative-context-protocol"
    )
    _patch_ncp_probe(monkeypatch, bad)

    tool = _tools_by_name(
        _report(
            {
                "OMI_LIVE_TOOLS_ENABLED": "true",
                "OMI_LIVE_NCP_ENABLED": "true",
            }
        )
    )["ncp"]

    assert tool["status"] in {"unavailable", "not_configured"}
    assert tool["runtime_dependency_available"] is False
    assert tool["ncp_source_available"] is False
    assert tool["ncp_validator_available"] is False
    assert tool["ncp_validator_status"] == "unavailable"
    assert ".external_sources/narrative-context-protocol" in tool["ncp_detail"]


def test_ncp_missing_package_json_reports_unavailable_with_clear_detail(
    monkeypatch,
) -> None:
    bad = _all_ncp_surfaces_available_result()
    bad["ncp_package_json_available"] = False
    bad["ncp_validate_schema_package_script_available"] = False
    bad["ncp_validate_file_package_script_available"] = False
    bad["ncp_runtime_surface"] = "unavailable"
    bad["ncp_validator_available"] = False
    bad["ncp_validator_status"] = "unavailable"
    bad["ncp_detail"] = "missing package.json"
    _patch_ncp_probe(monkeypatch, bad)

    tool = _tools_by_name(
        _report(
            {
                "OMI_LIVE_TOOLS_ENABLED": "true",
                "OMI_LIVE_NCP_ENABLED": "true",
            }
        )
    )["ncp"]

    assert tool["status"] == "unavailable"
    assert tool["ncp_package_json_available"] is False
    assert tool["ncp_validate_schema_package_script_available"] is False
    assert tool["ncp_validate_file_package_script_available"] is False
    assert tool["ncp_validator_available"] is False
    assert "package.json" in tool["ncp_detail"]


def test_ncp_missing_schema_json_reports_unavailable_with_clear_detail(
    monkeypatch,
) -> None:
    bad = _all_ncp_surfaces_available_result()
    bad["ncp_schema_json_available"] = False
    bad["ncp_runtime_surface"] = "unavailable"
    bad["ncp_validator_available"] = False
    bad["ncp_validator_status"] = "unavailable"
    bad["ncp_detail"] = "missing schema/ncp-schema.json"
    _patch_ncp_probe(monkeypatch, bad)

    tool = _tools_by_name(
        _report(
            {
                "OMI_LIVE_TOOLS_ENABLED": "true",
                "OMI_LIVE_NCP_ENABLED": "true",
            }
        )
    )["ncp"]

    assert tool["status"] == "unavailable"
    assert tool["ncp_schema_json_available"] is False
    assert tool["ncp_validator_available"] is False
    assert "ncp-schema.json" in tool["ncp_detail"]


def test_ncp_missing_schema_yaml_reports_unavailable_with_clear_detail(
    monkeypatch,
) -> None:
    bad = _all_ncp_surfaces_available_result()
    bad["ncp_schema_yaml_available"] = False
    bad["ncp_runtime_surface"] = "unavailable"
    bad["ncp_validator_available"] = False
    bad["ncp_validator_status"] = "unavailable"
    bad["ncp_detail"] = "missing schema/ncp-schema.yaml"
    _patch_ncp_probe(monkeypatch, bad)

    tool = _tools_by_name(
        _report(
            {
                "OMI_LIVE_TOOLS_ENABLED": "true",
                "OMI_LIVE_NCP_ENABLED": "true",
            }
        )
    )["ncp"]

    assert tool["status"] == "unavailable"
    assert tool["ncp_schema_yaml_available"] is False
    assert tool["ncp_validator_available"] is False
    assert "ncp-schema.yaml" in tool["ncp_detail"]


def test_ncp_missing_validate_schema_script_reports_unavailable_with_clear_detail(
    monkeypatch,
) -> None:
    bad = _all_ncp_surfaces_available_result()
    bad["ncp_validate_schema_script_available"] = False
    bad["ncp_runtime_surface"] = "unavailable"
    bad["ncp_validator_available"] = False
    bad["ncp_validator_status"] = "unavailable"
    bad["ncp_detail"] = "missing tests/validate-schema.js"
    _patch_ncp_probe(monkeypatch, bad)

    tool = _tools_by_name(
        _report(
            {
                "OMI_LIVE_TOOLS_ENABLED": "true",
                "OMI_LIVE_NCP_ENABLED": "true",
            }
        )
    )["ncp"]

    assert tool["status"] == "unavailable"
    assert tool["ncp_validate_schema_script_available"] is False
    assert "validate-schema.js" in tool["ncp_detail"]


def test_ncp_missing_validate_file_script_reports_unavailable_with_clear_detail(
    monkeypatch,
) -> None:
    bad = _all_ncp_surfaces_available_result()
    bad["ncp_validate_file_script_available"] = False
    bad["ncp_runtime_surface"] = "unavailable"
    bad["ncp_validator_available"] = False
    bad["ncp_validator_status"] = "unavailable"
    bad["ncp_detail"] = "missing tests/validate-file.js"
    _patch_ncp_probe(monkeypatch, bad)

    tool = _tools_by_name(
        _report(
            {
                "OMI_LIVE_TOOLS_ENABLED": "true",
                "OMI_LIVE_NCP_ENABLED": "true",
            }
        )
    )["ncp"]

    assert tool["status"] == "unavailable"
    assert tool["ncp_validate_file_script_available"] is False
    assert "validate-file.js" in tool["ncp_detail"]


def test_ncp_missing_validate_schema_package_script_reports_unavailable(
    monkeypatch,
) -> None:
    bad = _all_ncp_surfaces_available_result()
    bad["ncp_validate_schema_package_script_available"] = False
    bad["ncp_runtime_surface"] = "unavailable"
    bad["ncp_validator_available"] = False
    bad["ncp_validator_status"] = "unavailable"
    bad["ncp_detail"] = "missing package.json:validate:schema"
    _patch_ncp_probe(monkeypatch, bad)

    tool = _tools_by_name(
        _report(
            {
                "OMI_LIVE_TOOLS_ENABLED": "true",
                "OMI_LIVE_NCP_ENABLED": "true",
            }
        )
    )["ncp"]

    assert tool["status"] == "unavailable"
    assert tool["ncp_validate_schema_package_script_available"] is False
    assert "validate:schema" in tool["ncp_detail"]


def test_ncp_missing_validate_file_package_script_reports_unavailable(
    monkeypatch,
) -> None:
    bad = _all_ncp_surfaces_available_result()
    bad["ncp_validate_file_package_script_available"] = False
    bad["ncp_runtime_surface"] = "unavailable"
    bad["ncp_validator_available"] = False
    bad["ncp_validator_status"] = "unavailable"
    bad["ncp_detail"] = "missing package.json:validate:file"
    _patch_ncp_probe(monkeypatch, bad)

    tool = _tools_by_name(
        _report(
            {
                "OMI_LIVE_TOOLS_ENABLED": "true",
                "OMI_LIVE_NCP_ENABLED": "true",
            }
        )
    )["ncp"]

    assert tool["status"] == "unavailable"
    assert tool["ncp_validate_file_package_script_available"] is False
    assert "validate:file" in tool["ncp_detail"]


def test_ncp_missing_node_reports_unavailable_with_clear_detail(
    monkeypatch,
) -> None:
    bad = _all_ncp_surfaces_available_result()
    bad["ncp_node_available"] = False
    bad["ncp_node_path"] = None
    bad["ncp_runtime_surface"] = "unavailable"
    bad["ncp_validator_available"] = False
    bad["ncp_validator_status"] = "unavailable"
    bad["ncp_detail"] = "missing command:node"
    _patch_ncp_probe(monkeypatch, bad)

    tool = _tools_by_name(
        _report(
            {
                "OMI_LIVE_TOOLS_ENABLED": "true",
                "OMI_LIVE_NCP_ENABLED": "true",
            }
        )
    )["ncp"]

    assert tool["status"] == "unavailable"
    assert tool["ncp_node_available"] is False
    assert tool["ncp_node_path"] is None
    assert "command:node" in tool["ncp_detail"]


def test_ncp_missing_npm_reports_unavailable_with_clear_detail(
    monkeypatch,
) -> None:
    bad = _all_ncp_surfaces_available_result()
    bad["ncp_npm_available"] = False
    bad["ncp_npm_path"] = None
    bad["ncp_runtime_surface"] = "unavailable"
    bad["ncp_validator_available"] = False
    bad["ncp_validator_status"] = "unavailable"
    bad["ncp_detail"] = "missing command:npm"
    _patch_ncp_probe(monkeypatch, bad)

    tool = _tools_by_name(
        _report(
            {
                "OMI_LIVE_TOOLS_ENABLED": "true",
                "OMI_LIVE_NCP_ENABLED": "true",
            }
        )
    )["ncp"]

    assert tool["status"] == "unavailable"
    assert tool["ncp_npm_available"] is False
    assert tool["ncp_npm_path"] is None
    assert "command:npm" in tool["ncp_detail"]


def test_ncp_existing_node_modules_is_reported_when_present(
    monkeypatch,
) -> None:
    _patch_ncp_probe(monkeypatch, _all_ncp_surfaces_available_result())

    tool = _tools_by_name(
        _report(
            {
                "OMI_LIVE_TOOLS_ENABLED": "true",
                "OMI_LIVE_NCP_ENABLED": "true",
            }
        )
    )["ncp"]

    assert tool["ncp_node_modules_available"] is True


def test_ncp_missing_node_modules_reports_degraded_with_clear_detail(
    monkeypatch,
) -> None:
    bad = _all_ncp_surfaces_available_result()
    bad["ncp_node_modules_available"] = False
    bad["ncp_runtime_surface"] = "degraded"
    bad["ncp_validator_available"] = True
    bad["ncp_validator_status"] = "degraded"
    bad["ncp_detail"] = (
        "node_modules NOT present (validator scripts would not be runnable in "
        "this state; preflight does not run npm install)"
    )
    _patch_ncp_probe(monkeypatch, bad)

    tool = _tools_by_name(
        _report(
            {
                "OMI_LIVE_TOOLS_ENABLED": "true",
                "OMI_LIVE_NCP_ENABLED": "true",
            }
        )
    )["ncp"]

    assert tool["status"] == "enabled"
    assert tool["ncp_node_modules_available"] is False
    assert tool["ncp_runtime_surface"] == "degraded"
    assert "node_modules" in tool["ncp_detail"]
    assert "npm install" in tool["ncp_detail"]


def test_ncp_blocked_flag_overrides_validator_availability(
    monkeypatch,
) -> None:
    _patch_ncp_probe(monkeypatch, _all_ncp_surfaces_available_result())

    tool = _tools_by_name(
        _report(
            {
                "OMI_LIVE_TOOLS_ENABLED": "true",
                "OMI_LIVE_NCP_ENABLED": "true",
                "OMI_LIVE_NCP_BLOCKED": "true",
                "OMI_LIVE_NCP_BLOCKED_REASON": "Owner decision pending.",
            }
        )
    )["ncp"]

    assert tool["status"] == "blocked"
    assert tool["blocked"] is True
    assert tool["blocked_reason"] == "Owner decision pending."
    assert tool["runtime_dependency_available"] is True
    assert tool["ncp_validator_available"] is True


def test_ncp_preflight_does_not_run_npm_install_or_audit_fix_or_validate(
    tmp_path, monkeypatch
) -> None:
    """Preflight must not invoke npm install, npm audit fix, or
    npm run validate:schema / npm run validate:file. We assert this by
    intercepting subprocess / shell / network probes and confirming
    neither the real NCP probe nor the patched probe path triggers any of
    them. The Ollama probe is also mocked so that no real Ollama HTTP
    request is attempted during this test.
    """
    _patch_ncp_probe(monkeypatch, _all_ncp_surfaces_available_result())
    _mock_ollama_probe(monkeypatch, _MOCK_OLLAMA_UNREACHABLE)

    attempted_subprocess_calls: list[tuple[str, tuple]] = []
    attempted_network_calls: list[tuple[str, tuple]] = []
    attempted_node_calls: list[tuple[str, tuple]] = []
    attempted_npm_calls: list[tuple[str, tuple]] = []

    def fake_subprocess_run(*args, **kwargs):
        attempted_subprocess_calls.append(("subprocess.run", args))
        raise AssertionError(
            "subprocess.run must not be called by NCP preflight"
        )

    def fake_subprocess_popen(*args, **kwargs):
        attempted_subprocess_calls.append(("subprocess.Popen", args))
        raise AssertionError(
            "subprocess.Popen must not be called by NCP preflight"
        )

    def fake_urlopen(*args, **kwargs):
        attempted_network_calls.append(("urlopen", args))
        raise AssertionError(
            "urllib urlopen must not be called by NCP preflight"
        )

    def fake_node(*args, **kwargs):
        attempted_node_calls.append(("node", args))
        raise AssertionError(
            "node must not be invoked by NCP preflight"
        )

    def fake_npm(*args, **kwargs):
        attempted_npm_calls.append(("npm", args))
        raise AssertionError(
            "npm must not be invoked by NCP preflight"
        )

    import subprocess
    import urllib.request

    monkeypatch.setattr(subprocess, "run", fake_subprocess_run, raising=False)
    monkeypatch.setattr(subprocess, "Popen", fake_subprocess_popen, raising=False)
    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(subprocess, "check_call", fake_node, raising=False)
    monkeypatch.setattr(subprocess, "check_output", fake_node, raising=False)
    monkeypatch.setattr(subprocess, "call", fake_npm, raising=False)

    report = _report(
        {
            "OMI_LIVE_TOOLS_ENABLED": "true",
            "OMI_LIVE_NCP_ENABLED": "true",
        }
    )

    assert attempted_subprocess_calls == []
    assert attempted_network_calls == []
    assert attempted_node_calls == []
    assert attempted_npm_calls == []

    tool = _tools_by_name(report)["ncp"]
    assert tool["safety"]["read_only"] is True
    assert tool["safety"]["external_services_called"] is False
    assert tool["safety"]["live_models_called"] is False
    assert tool["safety"]["heavy_analysis_executed"] is False
    assert tool["safety"]["candidate_persistence"] is False
    assert tool["safety"]["memory_canon_mutation"] is False
    assert tool["safety"]["promotion_or_apply_promotion"] is False
    assert tool["safety"]["story_prose_generated"] is False


def test_ncp_preflight_does_not_persist_or_mutate(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)
    project_manager.create_omi_idea("demo", "Owner-authored NCP preflight note.")
    before = project_manager.get_omi_summary("demo")
    _patch_ncp_probe(monkeypatch, _all_ncp_surfaces_available_result())

    report = _report(
        {
            "OMI_LIVE_TOOLS_ENABLED": "true",
            "OMI_LIVE_NCP_ENABLED": "true",
        }
    )

    after = project_manager.get_omi_summary("demo")
    assert after == before
    tool = _tools_by_name(report)["ncp"]
    assert tool["safety"]["candidate_persistence"] is False
    assert tool["safety"]["memory_canon_mutation"] is False
    assert tool["safety"]["promotion_or_apply_promotion"] is False
    assert tool["safety"]["story_prose_generated"] is False


def test_ncp_audit_caveat_is_reported_verbatim() -> None:
    """Audit caveat text is reported as known owner evidence, not run."""
    report = _report()
    tool = _tools_by_name(report)["ncp"]

    caveat = tool["ncp_audit_caveat"]
    assert isinstance(caveat, str)
    assert "ajv" in caveat
    assert "moderate" in caveat
    assert "fast-uri" in caveat
    assert "high" in caveat
    assert "npm audit fix" in caveat
    assert "recorded, not fixed" in caveat


# ---------------------------------------------------------------------------
# T018B — NCP candidate-import validation adapter preflight fields
# ---------------------------------------------------------------------------


def test_ncp_t018b_input_path_env_field_is_reported(monkeypatch) -> None:
    _patch_ncp_probe(monkeypatch, _all_ncp_surfaces_available_result())
    tool = _tools_by_name(_report())["ncp"]
    assert tool["ncp_input_path_env"] == "OMI_LIVE_NCP_INPUT_PATH"
    assert tool["ncp_input_path_configured"] is False
    assert tool["ncp_input_path_value"] == ""
    assert tool["ncp_validate_with_node_env"] == "OMI_LIVE_NCP_VALIDATE_WITH_NODE"
    assert tool["ncp_validate_with_node_enabled"] is False


def test_ncp_t018b_input_path_configured_when_env_set(monkeypatch) -> None:
    _patch_ncp_probe(monkeypatch, _all_ncp_surfaces_available_result(), env_aware=True)
    env = {
        "OMI_LIVE_TOOLS_ENABLED": "true",
        "OMI_LIVE_NCP_ENABLED": "true",
        "OMI_LIVE_NCP_INPUT_PATH": (
            ".external_sources/narrative-context-protocol/examples/"
            "complete-storyform-template.json"
        ),
    }
    tool = _tools_by_name(_report(env))["ncp"]
    assert tool["ncp_input_path_env"] == "OMI_LIVE_NCP_INPUT_PATH"
    assert tool["ncp_input_path_configured"] is True
    assert (
        tool["ncp_input_path_value"]
        == ".external_sources/narrative-context-protocol/examples/"
        "complete-storyform-template.json"
    )
    assert tool["ncp_validate_with_node_enabled"] is False


def test_ncp_t018b_validate_with_node_opt_in_is_reported(monkeypatch) -> None:
    _patch_ncp_probe(monkeypatch, _all_ncp_surfaces_available_result(), env_aware=True)
    env = {
        "OMI_LIVE_TOOLS_ENABLED": "true",
        "OMI_LIVE_NCP_ENABLED": "true",
        "OMI_LIVE_NCP_INPUT_PATH": (
            ".external_sources/narrative-context-protocol/examples/"
            "complete-storyform-template.json"
        ),
        "OMI_LIVE_NCP_VALIDATE_WITH_NODE": "true",
    }
    tool = _tools_by_name(_report(env))["ncp"]
    assert tool["ncp_validate_with_node_env"] == "OMI_LIVE_NCP_VALIDATE_WITH_NODE"
    assert tool["ncp_validate_with_node_enabled"] is True


def test_ncp_t018b_preflight_does_not_read_input_file(monkeypatch, tmp_path) -> None:
    """Preflight must NOT read the OMI_LIVE_NCP_INPUT_PATH file. We point
    the env var at a path the test owns; if preflight ever reads it, the
    file content sentinel would be flagged by the test's safety
    assertions (read-only preflight cannot read or mutate the file)."""
    _patch_ncp_probe(monkeypatch, _all_ncp_surfaces_available_result(), env_aware=True)
    sentinel = tmp_path / "should_not_be_read.json"
    sentinel.write_text('{"would_be_read": true}', encoding="utf-8")

    report = _report(
        {
            "OMI_LIVE_TOOLS_ENABLED": "true",
            "OMI_LIVE_NCP_ENABLED": "true",
            "OMI_LIVE_NCP_INPUT_PATH": str(sentinel),
        }
    )
    tool = _tools_by_name(report)["ncp"]
    assert tool["ncp_input_path_configured"] is True
    assert tool["ncp_input_path_value"] == str(sentinel)
    assert tool["status"] in {"enabled", "available", "disabled"}
    # Preflight must not perform analysis or mutate state.
    assert tool["safety"]["read_only"] is True
    assert tool["safety"]["heavy_analysis_executed"] is False
    assert tool["safety"]["external_services_called"] is False
    assert tool["safety"]["live_models_called"] is False
    assert tool["safety"]["candidate_persistence"] is False
    assert tool["safety"]["memory_canon_mutation"] is False
    assert tool["safety"]["promotion_or_apply_promotion"] is False
    assert tool["safety"]["story_prose_generated"] is False
    # The sentinel file should be untouched (still on disk, content preserved).
    assert sentinel.exists()
    assert sentinel.read_text(encoding="utf-8") == '{"would_be_read": true}'


# ---------------------------------------------------------------------------
# T019A — Subtxt docs/source preflight
# ---------------------------------------------------------------------------


def _subtxt_full_reference_result() -> dict[str, object]:
    return {
        "subtxt_runtime_surface": "reference_only",
        "subtxt_source_path": ".external_sources/subtxt-docs",
        "subtxt_source_available": True,
        "subtxt_readme_available": True,
        "subtxt_package_json_available": True,
        "subtxt_package_json_parseable": True,
        "subtxt_content_root_available": True,
        "subtxt_content_index_available": True,
        "subtxt_key_concepts_available": True,
        "subtxt_narrative_aspects_available": True,
        "subtxt_storypoints_docs_available": True,
        "subtxt_storybeats_docs_available": True,
        "subtxt_narrative_intelligence_available": True,
        "subtxt_advanced_concepts_available": True,
        "subtxt_narrative_tasks_available": True,
        "subtxt_api_reference_available": True,
        "subtxt_package_name": "nuxt-ui-pro-template-docs",
        "subtxt_package_private": True,
        "subtxt_package_scripts": [
            "build",
            "dev",
            "generate",
            "lint",
            "postinstall",
            "preview",
            "typecheck",
        ],
        "subtxt_license_declared": True,
        "subtxt_license_name": "CC BY-NC-SA 4.0",
        "subtxt_license_source": "README.md",
        "subtxt_docs_reference_available": True,
        "subtxt_live_runtime_available": False,
        "subtxt_live_runtime_status": "reference_only",
        "subtxt_command_env": "OMI_LIVE_SUBTXT_COMMAND",
        "subtxt_command_configured": False,
        "subtxt_command_value": "",
        "subtxt_path_env": "OMI_LIVE_SUBTXT_PATH",
        "subtxt_path_configured": False,
        "subtxt_path_value": "",
        "subtxt_detail": (
            "Subtxt documentation source present at "
            ".external_sources/subtxt-docs. "
            "The local source is a Subtxt documentation/reference "
            "repository (package name: nuxt-ui-pro-template-docs, "
            "private: true, "
            "docs-site scripts: build, dev, generate, lint, "
            "postinstall, preview, typecheck). "
            "Documentation availability is not live-runtime "
            "availability. Package scripts are Nuxt docs-site "
            "operations, not Subtxt analysis. "
            "T019A does not execute Subtxt. "
            "A separate owner-controlled integration-path "
            "decision is required."
        ),
    }


def _patch_subtxt_probe(
    monkeypatch,
    result: dict[str, object] | None = None,
) -> None:
    if result is None:
        result = _subtxt_full_reference_result()

    def _patched(env: object | None = None) -> dict[str, object]:
        output = {key: value for key, value in result.items()}
        mapping = dict(env) if env is not None else {}
        raw_cmd = str(mapping.get("OMI_LIVE_SUBTXT_COMMAND", "") or "")
        output["subtxt_command_value"] = raw_cmd.strip()
        output["subtxt_command_configured"] = bool(output["subtxt_command_value"])
        raw_path = str(mapping.get("OMI_LIVE_SUBTXT_PATH", "") or "")
        output["subtxt_path_value"] = raw_path.strip()
        output["subtxt_path_configured"] = bool(output["subtxt_path_value"])
        return output

    monkeypatch.setattr(preflight, "_subtxt_docs_source_probe", _patched)


def test_subtxt_disabled_by_default_remains_read_only() -> None:
    report = _report()
    tool = _tools_by_name(report)["subtxt"]

    assert tool["global_enabled"] is False
    assert tool["tool_enabled"] is False
    assert tool["runtime_enabled"] is False
    assert tool["blocked"] is False
    assert tool["status"] in {"disabled", "available"}
    assert tool["safety"]["read_only"] is True
    assert tool["safety"]["heavy_analysis_executed"] is False
    assert tool["safety"]["external_services_called"] is False
    assert tool["safety"]["live_models_called"] is False
    assert tool["safety"]["candidate_persistence"] is False
    assert tool["safety"]["memory_canon_mutation"] is False
    assert tool["safety"]["promotion_or_apply_promotion"] is False
    assert tool["safety"]["story_prose_generated"] is False


def test_subtxt_full_docs_surface_reports_reference_only(
    monkeypatch,
) -> None:
    _patch_subtxt_probe(monkeypatch, _subtxt_full_reference_result())

    tool = _tools_by_name(_report())["subtxt"]

    assert tool["subtxt_runtime_surface"] == "reference_only"
    assert tool["subtxt_source_path"] == ".external_sources/subtxt-docs"
    assert tool["subtxt_source_available"] is True
    assert tool["subtxt_docs_reference_available"] is True
    assert tool["subtxt_live_runtime_available"] is False
    assert tool["subtxt_live_runtime_status"] == "reference_only"
    assert tool["subtxt_readme_available"] is True
    assert tool["subtxt_package_json_available"] is True
    assert tool["subtxt_package_json_parseable"] is True
    assert tool["subtxt_content_root_available"] is True
    assert tool["subtxt_content_index_available"] is True
    assert tool["subtxt_key_concepts_available"] is True
    assert tool["subtxt_narrative_aspects_available"] is True
    assert tool["subtxt_storypoints_docs_available"] is True
    assert tool["subtxt_storybeats_docs_available"] is True
    assert tool["subtxt_narrative_intelligence_available"] is True
    assert tool["subtxt_advanced_concepts_available"] is True
    assert tool["subtxt_narrative_tasks_available"] is True
    assert tool["subtxt_api_reference_available"] is True
    assert tool["subtxt_package_name"] == "nuxt-ui-pro-template-docs"
    assert tool["subtxt_package_private"] is True
    assert isinstance(tool["subtxt_package_scripts"], list)
    assert "build" in tool["subtxt_package_scripts"]
    assert "dev" in tool["subtxt_package_scripts"]
    assert "generate" in tool["subtxt_package_scripts"]
    assert "Subtxt documentation source present" in tool["probe_detail"]
    assert tool["subtxt_detail"] == tool["probe_detail"]


def test_subtxt_docs_reference_does_not_make_live_runtime_available(
    monkeypatch,
) -> None:
    _patch_subtxt_probe(monkeypatch, _subtxt_full_reference_result())

    tool = _tools_by_name(
        _report(
            {
                "OMI_LIVE_TOOLS_ENABLED": "true",
                "OMI_LIVE_SUBTXT_ENABLED": "true",
            }
        )
    )["subtxt"]

    assert tool["global_enabled"] is True
    assert tool["tool_enabled"] is True
    assert tool["runtime_enabled"] is True
    assert tool["subtxt_docs_reference_available"] is True
    assert tool["subtxt_live_runtime_available"] is False
    assert tool["runtime_dependency_available"] is False
    assert tool["runtime_dependency_status"] == "available"
    assert tool["status"] == "unavailable"
    assert tool["safety"]["read_only"] is True


def test_subtxt_enabled_plus_global_does_not_falsely_report_runnable_runtime(
    monkeypatch,
) -> None:
    _patch_subtxt_probe(monkeypatch, _subtxt_full_reference_result())

    tool = _tools_by_name(
        _report(
            {
                "OMI_LIVE_TOOLS_ENABLED": "true",
                "OMI_LIVE_SUBTXT_ENABLED": "true",
                "OMI_LIVE_SUBTXT_COMMAND": "subtxt",
                "OMI_LIVE_SUBTXT_PATH": "/opt/subtxt",
            }
        )
    )["subtxt"]

    assert tool["runtime_enabled"] is True
    assert tool["subtxt_live_runtime_available"] is False
    assert tool["runtime_dependency_available"] is False
    assert tool["status"] == "unavailable"


def test_subtxt_source_path_is_exact_subtxt_docs_not_generic_external_sources(
    monkeypatch,
) -> None:
    _patch_subtxt_probe(monkeypatch, _subtxt_full_reference_result())

    tool = _tools_by_name(_report())["subtxt"]

    assert tool["subtxt_source_path"] == ".external_sources/subtxt-docs"
    assert tool["subtxt_source_path"] != ".external_sources"


def test_subtxt_missing_source_root_reports_unavailable(
    monkeypatch,
) -> None:
    bad = _subtxt_full_reference_result()
    bad["subtxt_runtime_surface"] = "unavailable"
    bad["subtxt_source_available"] = False
    bad["subtxt_docs_reference_available"] = False
    bad["subtxt_live_runtime_status"] = "unavailable"
    bad["subtxt_detail"] = (
        "Subtxt documentation source not found at "
        ".external_sources/subtxt-docs. No Subtxt reference surface "
        "available. T019A does not execute Subtxt. "
        "A separate owner-controlled integration-path "
        "decision is required."
    )
    _patch_subtxt_probe(monkeypatch, bad)

    tool = _tools_by_name(_report())["subtxt"]

    assert tool["subtxt_runtime_surface"] == "unavailable"
    assert tool["subtxt_source_available"] is False
    assert tool["subtxt_docs_reference_available"] is False
    assert tool["runtime_configured"] is False
    assert tool["runtime_dependency_available"] is False
    assert tool["runtime_dependency_status"] == "unavailable"
    assert "not found" in tool["probe_detail"]
    assert tool["status"] in {"disabled", "unavailable"}


def test_subtxt_missing_readme_reports_safely(
    monkeypatch,
) -> None:
    bad = _subtxt_full_reference_result()
    bad["subtxt_readme_available"] = False
    bad["subtxt_license_declared"] = False
    bad["subtxt_license_name"] = ""
    bad["subtxt_license_source"] = ""
    _patch_subtxt_probe(monkeypatch, bad)

    tool = _tools_by_name(_report())["subtxt"]

    assert tool["subtxt_readme_available"] is False
    assert tool["subtxt_license_declared"] is False
    assert tool["subtxt_license_name"] == ""
    assert tool["subtxt_license_source"] == ""
    assert tool["subtxt_runtime_surface"] in {"degraded", "reference_only"}


def test_subtxt_missing_malformed_package_json_reports_safely(
    monkeypatch,
) -> None:
    bad = _subtxt_full_reference_result()
    bad["subtxt_package_json_available"] = True
    bad["subtxt_package_json_parseable"] = False
    bad["subtxt_package_name"] = ""
    bad["subtxt_package_private"] = False
    bad["subtxt_package_scripts"] = []
    _patch_subtxt_probe(monkeypatch, bad)

    tool = _tools_by_name(_report())["subtxt"]

    assert tool["subtxt_package_json_available"] is True
    assert tool["subtxt_package_json_parseable"] is False
    assert tool["subtxt_package_name"] == ""
    assert tool["subtxt_package_private"] is False
    assert tool["subtxt_package_scripts"] == []


def test_subtxt_missing_content_root_reports_degraded(
    monkeypatch,
) -> None:
    bad = _subtxt_full_reference_result()
    bad["subtxt_content_root_available"] = False
    bad["subtxt_content_index_available"] = False
    bad["subtxt_key_concepts_available"] = False
    bad["subtxt_narrative_aspects_available"] = False
    bad["subtxt_runtime_surface"] = "degraded"
    bad["subtxt_docs_reference_available"] = False
    bad["subtxt_live_runtime_status"] = "unavailable"
    bad["subtxt_detail"] = (
        "Subtxt documentation source present at "
        ".external_sources/subtxt-docs but one or more core "
        "documentation surfaces are missing or unreadable."
    )
    _patch_subtxt_probe(monkeypatch, bad)

    tool = _tools_by_name(
        _report(
            {
                "OMI_LIVE_TOOLS_ENABLED": "true",
                "OMI_LIVE_SUBTXT_ENABLED": "true",
            }
        )
    )["subtxt"]

    assert tool["subtxt_runtime_surface"] == "degraded"
    assert tool["subtxt_source_available"] is True
    assert tool["subtxt_content_root_available"] is False
    assert tool["subtxt_content_index_available"] is False
    assert tool["subtxt_docs_reference_available"] is False
    assert tool["subtxt_live_runtime_available"] is False
    assert tool["subtxt_live_runtime_status"] == "unavailable"
    assert "missing" in tool["probe_detail"] or "degraded" in tool["probe_detail"] or "unreadable" in tool["probe_detail"]


def test_subtxt_missing_key_docs_reports_degraded(
    monkeypatch,
) -> None:
    bad = _subtxt_full_reference_result()
    bad["subtxt_key_concepts_available"] = False
    bad["subtxt_narrative_aspects_available"] = False
    bad["subtxt_runtime_surface"] = "degraded"
    bad["subtxt_docs_reference_available"] = False
    bad["subtxt_live_runtime_status"] = "unavailable"
    bad["subtxt_detail"] = (
        "Subtxt documentation source present at "
        ".external_sources/subtxt-docs but one or more core "
        "documentation surfaces are missing or unreadable."
    )
    _patch_subtxt_probe(monkeypatch, bad)

    tool = _tools_by_name(_report())["subtxt"]

    assert tool["subtxt_runtime_surface"] == "degraded"
    assert tool["subtxt_source_available"] is True
    assert tool["subtxt_key_concepts_available"] is False
    assert tool["subtxt_narrative_aspects_available"] is False
    assert tool["subtxt_docs_reference_available"] is False


def test_subtxt_license_detected_from_readme(
    monkeypatch,
) -> None:
    _patch_subtxt_probe(monkeypatch, _subtxt_full_reference_result())

    tool = _tools_by_name(_report())["subtxt"]

    assert tool["subtxt_license_declared"] is True
    assert tool["subtxt_license_name"] == "CC BY-NC-SA 4.0"
    assert tool["subtxt_license_source"] == "README.md"


def test_subtxt_package_metadata_reported_without_executing_scripts(
    monkeypatch,
) -> None:
    _patch_subtxt_probe(monkeypatch, _subtxt_full_reference_result())

    tool = _tools_by_name(_report())["subtxt"]

    assert tool["subtxt_package_name"] == "nuxt-ui-pro-template-docs"
    assert tool["subtxt_package_private"] is True
    assert tool["subtxt_package_scripts"] == [
        "build",
        "dev",
        "generate",
        "lint",
        "postinstall",
        "preview",
        "typecheck",
    ]


def test_subtxt_command_env_surfaced_as_configuration_only(
    monkeypatch,
) -> None:
    _patch_subtxt_probe(
        monkeypatch,
        _subtxt_full_reference_result(),
    )
    env = {
        "OMI_LIVE_SUBTXT_COMMAND": "/usr/local/bin/subtxt",
    }
    tool = _tools_by_name(_report(env))["subtxt"]

    assert tool["subtxt_command_env"] == "OMI_LIVE_SUBTXT_COMMAND"
    assert tool["subtxt_command_configured"] is True
    assert tool["subtxt_command_value"] == "/usr/local/bin/subtxt"
    assert tool["subtxt_live_runtime_available"] is False
    assert tool["subtxt_path_configured"] is False
    assert tool["subtxt_path_value"] == ""


def test_subtxt_path_env_surfaced_as_configuration_only(
    monkeypatch,
) -> None:
    _patch_subtxt_probe(
        monkeypatch,
        _subtxt_full_reference_result(),
    )
    env = {
        "OMI_LIVE_SUBTXT_PATH": "/home/user/subtxt-runtime",
    }
    tool = _tools_by_name(_report(env))["subtxt"]

    assert tool["subtxt_path_env"] == "OMI_LIVE_SUBTXT_PATH"
    assert tool["subtxt_path_configured"] is True
    assert tool["subtxt_path_value"] == "/home/user/subtxt-runtime"
    assert tool["subtxt_live_runtime_available"] is False
    assert tool["runtime_dependency_available"] is False


def test_subtxt_blocked_flag_overrides_docs_availability(
    monkeypatch,
) -> None:
    _patch_subtxt_probe(monkeypatch, _subtxt_full_reference_result())

    tool = _tools_by_name(
        _report(
            {
                "OMI_LIVE_TOOLS_ENABLED": "true",
                "OMI_LIVE_SUBTXT_ENABLED": "true",
                "OMI_LIVE_SUBTXT_BLOCKED": "true",
                "OMI_LIVE_SUBTXT_BLOCKED_REASON": (
                    "Owner decision pending."
                ),
            }
        )
    )["subtxt"]

    assert tool["status"] == "blocked"
    assert tool["blocked"] is True
    assert tool["blocked_reason"] == "Owner decision pending."
    assert tool["subtxt_source_available"] is True
    assert tool["subtxt_docs_reference_available"] is True
    assert tool["subtxt_live_runtime_available"] is False


def test_subtxt_preflight_does_not_invoke_subprocess_shell_network_or_npm(
    monkeypatch,
) -> None:
    _patch_subtxt_probe(monkeypatch, _subtxt_full_reference_result())
    _mock_ollama_probe(monkeypatch, _MOCK_OLLAMA_UNREACHABLE)

    attempted_subprocess: list[tuple[str, tuple]] = []
    attempted_network: list[tuple[str, tuple]] = []

    import subprocess
    import urllib.request

    def fake_subprocess_run(*args, **kwargs):
        attempted_subprocess.append(("subprocess.run", args))
        raise AssertionError(
            "subprocess.run must not be called by Subtxt preflight"
        )

    def fake_subprocess_popen(*args, **kwargs):
        attempted_subprocess.append(("subprocess.Popen", args))
        raise AssertionError(
            "subprocess.Popen must not be called by Subtxt preflight"
        )

    def fake_urlopen(*args, **kwargs):
        attempted_network.append(("urlopen", args))
        raise AssertionError(
            "urllib urlopen must not be called by Subtxt preflight"
        )

    monkeypatch.setattr(subprocess, "run", fake_subprocess_run, raising=False)
    monkeypatch.setattr(subprocess, "Popen", fake_subprocess_popen, raising=False)
    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    report = _report(
        {
            "OMI_LIVE_TOOLS_ENABLED": "true",
            "OMI_LIVE_SUBTXT_ENABLED": "true",
        }
    )

    assert attempted_subprocess == []
    assert attempted_network == []

    tool = _tools_by_name(report)["subtxt"]
    assert tool["safety"]["read_only"] is True
    assert tool["safety"]["external_services_called"] is False
    assert tool["safety"]["live_models_called"] is False
    assert tool["safety"]["heavy_analysis_executed"] is False
    assert tool["safety"]["candidate_persistence"] is False
    assert tool["safety"]["memory_canon_mutation"] is False
    assert tool["safety"]["promotion_or_apply_promotion"] is False
    assert tool["safety"]["story_prose_generated"] is False


def test_subtxt_preflight_does_not_persist_or_mutate(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)
    project_manager.create_omi_idea("demo", "Owner-authored subtxt preflight note.")
    before = project_manager.get_omi_summary("demo")

    _patch_subtxt_probe(monkeypatch, _subtxt_full_reference_result())

    report = _report(
        {
            "OMI_LIVE_TOOLS_ENABLED": "true",
            "OMI_LIVE_SUBTXT_ENABLED": "true",
        }
    )

    after = project_manager.get_omi_summary("demo")
    assert after == before
    tool = _tools_by_name(report)["subtxt"]
    assert tool["safety"]["candidate_persistence"] is False
    assert tool["safety"]["memory_canon_mutation"] is False
    assert tool["safety"]["promotion_or_apply_promotion"] is False
    assert tool["safety"]["story_prose_generated"] is False


# ─────────────────────────────────────────────────────────────────────────────
# PHASE8-IMPL-023-T020A dramatica-flow source/runtime preflight tests
# ─────────────────────────────────────────────────────────────────────────────

_DF_MIN_PYPROJECT = (
    "[project]\n"
    'name = "dramatica-flow"\n'
    'version = "0.1.0"\n'
    'requires-python = ">=3.11"\n'
    "dependencies = [\n"
    '    "openai>=1.30.0",\n'
    '    "typer>=0.12.0",\n'
    '    "fastapi>=0.110.0",\n'
    '    "uvicorn>=0.29.0",\n'
    "]\n"
    "\n"
    "[project.scripts]\n"
    'df = "cli.main:app"\n'
)

_DF_MIN_CLI = (
    '"""Minimal dramatica-flow CLI for preflight tests."""\n'
    "import typer\n"
    "\n"
    "app = typer.Typer(name=\"df\")\n"
    "setup_app = typer.Typer()\n"
    "app.add_typer(setup_app, name=\"setup\")\n"
    "\n"
    "@app.command()\n"
    "def init(name: str) -> None:\n"
    "    pass\n"
    "\n"
    "@app.command()\n"
    "def book(title: str) -> None:\n"
    "    pass\n"
    "\n"
    "@app.command()\n"
    "def write() -> None:\n"
    "    pass\n"
    "\n"
    "@app.command()\n"
    "def audit() -> None:\n"
    "    pass\n"
    "\n"
    "@app.command()\n"
    "def revise() -> None:\n"
    "    pass\n"
    "\n"
    "@app.command()\n"
    "def status() -> None:\n"
    "    pass\n"
    "\n"
    "@app.command()\n"
    "def export() -> None:\n"
    "    pass\n"
    "\n"
    "@app.command()\n"
    "def doctor() -> None:\n"
    "    pass\n"
)

_DF_MIN_VALIDATORS = (
    '"""Minimal validators for preflight tests."""\n'
    "import re\n"
    "AI_MARKER_WORDS = []\n"
)

_DF_MIN_README = (
    "# Dramatica-Flow\n"
    "\n"
    "[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)\n"
    "\n"
    "A test README with an MIT license badge and FastAPI/Ollama/DeepSeek mentions.\n"
    "\n"
    "## Features\n"
    "\n"
    "- OpenAI-compatible LLM provider (DeepSeek)\n"
    "- FastAPI web UI on uvicorn\n"
    "- Ollama local model backend\n"
)

_DF_MIN_README_EN = (
    "# Dramatica-Flow (EN)\n"
    "\n"
    "[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)\n"
    "\n"
    "A test README_EN with an MIT license badge.\n"
)


def _write_minimal_dramatica_flow_source(source_root) -> None:
    """Create a minimal but parseable on-disk source tree at source_root."""
    source_root.mkdir(parents=True, exist_ok=True)
    (source_root / "pyproject.toml").write_text(_DF_MIN_PYPROJECT, encoding="utf-8")
    (source_root / "README.md").write_text(_DF_MIN_README, encoding="utf-8")
    (source_root / "README_EN.md").write_text(_DF_MIN_README_EN, encoding="utf-8")
    cli_dir = source_root / "cli"
    cli_dir.mkdir(exist_ok=True)
    (cli_dir / "main.py").write_text(_DF_MIN_CLI, encoding="utf-8")
    validators_pkg = source_root / "core" / "validators"
    validators_pkg.mkdir(parents=True, exist_ok=True)
    (validators_pkg / "__init__.py").write_text(
        _DF_MIN_VALIDATORS, encoding="utf-8"
    )


def _write_minimal_dramatica_flow_venv(
    venv_root,
    *,
    include_dist_info: bool = True,
    include_editable: bool = True,
    editable_source_url: str | None = None,
    extra_dist_infos: tuple[str, ...] = (),
) -> None:
    """Create a minimal editable virtual environment under venv_root."""
    venv_root.mkdir(parents=True, exist_ok=True)
    bin_dir = venv_root / "bin"
    bin_dir.mkdir(exist_ok=True)
    (bin_dir / "python").write_text("#!/bin/sh\necho stub\n", encoding="utf-8")
    (bin_dir / "df").write_text("#!/bin/sh\necho stub\n", encoding="utf-8")
    lib_dir = venv_root / "lib" / "python3.12" / "site-packages"
    lib_dir.mkdir(parents=True, exist_ok=True)
    if include_dist_info:
        dist_info = lib_dir / "dramatica_flow-0.1.0.dist-info"
        dist_info.mkdir(exist_ok=True)
        if editable_source_url is None:
            url = (
                "file://"
                + str((venv_root.parent.parent / "dramatica-flow").resolve())
            )
        else:
            url = editable_source_url
        if include_editable:
            direct_url = '{"dir_info": {"editable": true}, "url": "' + url + '"}'
        else:
            direct_url = '{"url": "' + url + '"}'
        (dist_info / "direct_url.json").write_text(direct_url, encoding="utf-8")
        (dist_info / "entry_points.txt").write_text(
            "[console_scripts]\ndf = cli.main:app\n", encoding="utf-8"
        )
        (dist_info / "METADATA").write_text(
            "Metadata-Version: 2.4\n"
            "Name: dramatica-flow\n"
            "Version: 0.1.0\n"
            "Requires-Python: >=3.11\n",
            encoding="utf-8",
        )
    for extra in extra_dist_infos:
        (lib_dir / extra).mkdir(exist_ok=True)


def _patch_dramatica_flow_probe(
    monkeypatch,
    result: dict[str, object] | None = None,
) -> None:
    """Replace dramatica-flow probing and isolate unrelated runtime probes."""
    if result is None:
        result = _dramatica_flow_full_surface_result()
    original_dependency_probe = preflight._dependency_probe

    def _patched(env: object | None = None) -> dict[str, object]:
        output = {key: value for key, value in result.items()}
        mapping = dict(env) if env is not None else {}
        raw_cmd = str(mapping.get("OMI_LIVE_DRAMATICA_FLOW_COMMAND", "") or "")
        output["dramatica_flow_command_value"] = raw_cmd.strip()
        output["dramatica_flow_command_configured"] = bool(
            output["dramatica_flow_command_value"]
        )
        raw_path = str(mapping.get("OMI_LIVE_DRAMATICA_FLOW_PATH", "") or "")
        output["dramatica_flow_path_value"] = raw_path.strip()
        output["dramatica_flow_path_configured"] = bool(
            output["dramatica_flow_path_value"]
        )
        return output

    monkeypatch.setattr(preflight, "_dramatica_flow_runtime_probe", _patched)

    def _patched_dependency_probe(adapter: str, env) -> dict[str, object]:
        if adapter in {"dramatica_flow", "deterministic_fallback"}:
            return original_dependency_probe(adapter, env)
        return {
            "runtime_configured": False,
            "runtime_dependency_available": False,
            "runtime_dependency_status": "unavailable",
            "probe_detail": (
                f"{adapter} probe intentionally isolated for T020A report test"
            ),
        }

    monkeypatch.setattr(preflight, "_dependency_probe", _patched_dependency_probe)


def _dramatica_flow_full_surface_result() -> dict[str, object]:
    """Return a fully-installed + fully-parsed dramatica_flow probe result.

    Reflects the expected values for the committed real
    ``.external_sources/dramatica-flow`` source + editable venv.
    """
    return {
        "dramatica_flow_source_root": ".external_sources/dramatica-flow",
        "dramatica_flow_source_available": True,
        "dramatica_flow_pyproject_available": True,
        "dramatica_flow_readme_available": True,
        "dramatica_flow_readme_en_available": True,
        "dramatica_flow_cli_source_available": True,
        "dramatica_flow_validators_source_available": True,
        "dramatica_flow_package_name": "dramatica-flow",
        "dramatica_flow_package_version": "0.1.0",
        "dramatica_flow_requires_python": ">=3.11",
        "dramatica_flow_declared_dependencies": [
            "fastapi>=0.110.0",
            "openai>=1.30.0",
            "typer>=0.12.0",
            "uvicorn>=0.29.0",
        ],
        "dramatica_flow_console_script_name": "df",
        "dramatica_flow_console_script_target": "cli.main:app",
        "dramatica_flow_package_metadata_consistent": True,
        "dramatica_flow_console_script_consistent": True,
        "dramatica_flow_dist_info_metadata_consistent": True,
        "dramatica_flow_dist_info_console_script_consistent": True,
        "dramatica_flow_pyproject_console_script_name": "df",
        "dramatica_flow_pyproject_console_script_target": "cli.main:app",
        "dramatica_flow_dist_info_console_script_name": "df",
        "dramatica_flow_dist_info_console_script_target": "cli.main:app",
        "dramatica_flow_dist_info_name": "dramatica_flow-0.1.0.dist-info",
        "dramatica_flow_dist_info_count": 1,
        "dramatica_flow_dist_info_package_name": "dramatica-flow",
        "dramatica_flow_dist_info_package_version": "0.1.0",
        "dramatica_flow_dist_info_requires_python": ">=3.11",
        "dramatica_flow_dist_info_declared_dependencies": [],
        "dramatica_flow_direct_url_present": True,
        "dramatica_flow_direct_url_error": "",
        "dramatica_flow_venv_root": ".external_sources/venvs/dramatica-flow",
        "dramatica_flow_venv_available": True,
        "dramatica_flow_venv_python_available": True,
        "dramatica_flow_df_entrypoint_available": True,
        "dramatica_flow_dist_info_available": True,
        "dramatica_flow_editable_install": True,
        "dramatica_flow_editable_source": (
            "file:///tmp/.external_sources/dramatica-flow"
        ),
        "dramatica_flow_editable_source_matches_expected": True,
        "dramatica_flow_detected_cli_commands": [
            "audit",
            "book",
            "create",
            "delete",
            "doctor",
            "export",
            "init",
            "init-templates",
            "list",
            "load",
            "revise",
            "setup",
            "show",
            "status",
            "threads",
            "update",
            "write",
        ],
        "dramatica_flow_analysis_candidate_commands": ["audit", "status"],
        "dramatica_flow_prose_production_commands": ["export", "revise", "write"],
        "dramatica_flow_model_or_network_surface_detected": True,
        "dramatica_flow_project_mutation_surface_detected": True,
        "dramatica_flow_license_claimed": True,
        "dramatica_flow_license_name": "MIT",
        "dramatica_flow_license_source": "README.md, README_EN.md",
        "dramatica_flow_license_file_available": False,
        "dramatica_flow_license_verified": False,
        "dramatica_flow_reference_surface_available": True,
        "dramatica_flow_installation_surface_available": True,
        "dramatica_flow_analysis_only_runtime_authorized": False,
        "dramatica_flow_live_runtime_available": False,
        "dramatica_flow_integration_decision_required": True,
        "dramatica_flow_runtime_surface": "installed_reference_surface",
        "dramatica_flow_command_env": "OMI_LIVE_DRAMATICA_FLOW_COMMAND",
        "dramatica_flow_command_configured": False,
        "dramatica_flow_command_value": "",
        "dramatica_flow_path_env": "OMI_LIVE_DRAMATICA_FLOW_PATH",
        "dramatica_flow_path_configured": False,
        "dramatica_flow_path_value": "",
        "dramatica_flow_probe_detail": (
            "dramatica-flow source and editable venv are present; T020A is "
            "inspection and preflight only; live adapter is not authorized; "
            "the owner-controlled integration-path decision is deferred to T020B."
        ),
    }


@pytest.fixture
def dramatica_flow_tmp_repo(monkeypatch, tmp_path):
    """Set up a tmp repo with a parseable dramatica-flow source + venv."""
    source_root = tmp_path / ".external_sources" / "dramatica-flow"
    _write_minimal_dramatica_flow_source(source_root)
    venv_root = tmp_path / ".external_sources" / "venvs" / "dramatica-flow"
    _write_minimal_dramatica_flow_venv(venv_root)
    monkeypatch.setattr(preflight, "_REPO_ROOT", tmp_path)
    return tmp_path


def test_dramatica_flow_t020a_disabled_by_default_remains_read_only() -> None:
    report = _report()
    tool = _tools_by_name(report)["dramatica_flow"]

    assert tool["global_enabled"] is False
    assert tool["tool_enabled"] is False
    assert tool["runtime_enabled"] is False
    assert tool["blocked"] is False
    assert tool["safety"]["read_only"] is True
    assert tool["safety"]["external_services_called"] is False
    assert tool["safety"]["live_models_called"] is False
    assert tool["safety"]["candidate_persistence"] is False
    assert tool["safety"]["memory_canon_mutation"] is False
    assert tool["safety"]["promotion_or_apply_promotion"] is False
    assert tool["safety"]["story_prose_generated"] is False
    assert tool["safety"]["heavy_analysis_executed"] is False


def test_dramatica_flow_t020a_source_unavailable_reports_unavailable(
    monkeypatch, tmp_path
) -> None:
    monkeypatch.setattr(preflight, "_REPO_ROOT", tmp_path)

    result = preflight._dramatica_flow_runtime_probe({})

    assert result["dramatica_flow_source_available"] is False
    assert result["dramatica_flow_pyproject_available"] is False
    assert result["dramatica_flow_readme_available"] is False
    assert result["dramatica_flow_cli_source_available"] is False
    assert result["dramatica_flow_reference_surface_available"] is False
    assert result["dramatica_flow_runtime_surface"] == "unavailable"
    assert result["dramatica_flow_live_runtime_available"] is False
    assert result["dramatica_flow_analysis_only_runtime_authorized"] is False
    assert result["dramatica_flow_integration_decision_required"] is True


def test_dramatica_flow_t020a_source_only_reports_source_only_surface(
    monkeypatch, tmp_path
) -> None:
    source_root = tmp_path / ".external_sources" / "dramatica-flow"
    _write_minimal_dramatica_flow_source(source_root)
    monkeypatch.setattr(preflight, "_REPO_ROOT", tmp_path)

    result = preflight._dramatica_flow_runtime_probe({})

    assert result["dramatica_flow_source_available"] is True
    assert result["dramatica_flow_pyproject_available"] is True
    assert result["dramatica_flow_venv_available"] is False
    assert result["dramatica_flow_dist_info_available"] is False
    assert result["dramatica_flow_reference_surface_available"] is True
    assert result["dramatica_flow_installation_surface_available"] is False
    assert result["dramatica_flow_runtime_surface"] == "source_only"
    assert result["dramatica_flow_live_runtime_available"] is False


def test_dramatica_flow_t020a_full_source_and_venv_reports_installed_reference_surface(
    dramatica_flow_tmp_repo,
) -> None:
    result = preflight._dramatica_flow_runtime_probe({})

    assert result["dramatica_flow_source_available"] is True
    assert result["dramatica_flow_venv_available"] is True
    assert result["dramatica_flow_reference_surface_available"] is True
    assert result["dramatica_flow_installation_surface_available"] is True
    assert result["dramatica_flow_runtime_surface"] == "installed_reference_surface"
    assert result["dramatica_flow_live_runtime_available"] is False


def test_dramatica_flow_t020a_exact_package_metadata(
    dramatica_flow_tmp_repo,
) -> None:
    result = preflight._dramatica_flow_runtime_probe({})

    assert result["dramatica_flow_package_name"] == "dramatica-flow"
    assert result["dramatica_flow_package_version"] == "0.1.0"
    assert result["dramatica_flow_requires_python"] == ">=3.11"
    assert result["dramatica_flow_dist_info_package_name"] == "dramatica-flow"
    assert result["dramatica_flow_dist_info_package_version"] == "0.1.0"
    assert result["dramatica_flow_dist_info_requires_python"] == ">=3.11"


def test_dramatica_flow_t020a_dependency_normalization_and_sorting(
    dramatica_flow_tmp_repo,
) -> None:
    result = preflight._dramatica_flow_runtime_probe({})

    deps = result["dramatica_flow_declared_dependencies"]
    assert deps == sorted(deps)
    assert deps == [
        "fastapi>=0.110.0",
        "openai>=1.30.0",
        "typer>=0.12.0",
        "uvicorn>=0.29.0",
    ]


def test_dramatica_flow_t020a_exact_console_script(
    dramatica_flow_tmp_repo,
) -> None:
    result = preflight._dramatica_flow_runtime_probe({})

    assert result["dramatica_flow_console_script_name"] == "df"
    assert result["dramatica_flow_console_script_target"] == "cli.main:app"
    assert result["dramatica_flow_pyproject_console_script_name"] == "df"
    assert result["dramatica_flow_pyproject_console_script_target"] == "cli.main:app"
    assert result["dramatica_flow_dist_info_console_script_name"] == "df"
    assert result["dramatica_flow_dist_info_console_script_target"] == "cli.main:app"


def test_dramatica_flow_t020a_venv_python_presence(
    monkeypatch, tmp_path
) -> None:
    source_root = tmp_path / ".external_sources" / "dramatica-flow"
    _write_minimal_dramatica_flow_source(source_root)
    venv_root = tmp_path / ".external_sources" / "venvs" / "dramatica-flow"
    venv_root.mkdir(parents=True)
    (venv_root / "lib" / "python3.12" / "site-packages").mkdir(parents=True)
    bin_dir = venv_root / "bin"
    bin_dir.mkdir()
    (bin_dir / "df").write_text("#!/bin/sh\n", encoding="utf-8")
    (venv_root / "lib" / "python3.12" / "site-packages" / "dramatica_flow-0.1.0.dist-info").mkdir()
    monkeypatch.setattr(preflight, "_REPO_ROOT", tmp_path)

    result = preflight._dramatica_flow_runtime_probe({})

    assert result["dramatica_flow_venv_available"] is True
    assert result["dramatica_flow_venv_python_available"] is False
    assert result["dramatica_flow_runtime_surface"] == "source_only"


def test_dramatica_flow_t020a_df_entrypoint_presence(
    monkeypatch, tmp_path
) -> None:
    source_root = tmp_path / ".external_sources" / "dramatica-flow"
    _write_minimal_dramatica_flow_source(source_root)
    venv_root = tmp_path / ".external_sources" / "venvs" / "dramatica-flow"
    venv_root.mkdir(parents=True)
    lib = venv_root / "lib" / "python3.12" / "site-packages"
    lib.mkdir(parents=True)
    (lib / "dramatica_flow-0.1.0.dist-info").mkdir()
    (venv_root / "bin").mkdir()
    (venv_root / "bin" / "python").write_text("#!/bin/sh\n", encoding="utf-8")
    monkeypatch.setattr(preflight, "_REPO_ROOT", tmp_path)

    result = preflight._dramatica_flow_runtime_probe({})

    assert result["dramatica_flow_venv_python_available"] is True
    assert result["dramatica_flow_df_entrypoint_available"] is False
    assert result["dramatica_flow_runtime_surface"] == "source_only"


def test_dramatica_flow_t020a_dist_info_discovery(
    dramatica_flow_tmp_repo,
) -> None:
    result = preflight._dramatica_flow_runtime_probe({})

    assert result["dramatica_flow_dist_info_available"] is True
    assert result["dramatica_flow_dist_info_name"] == "dramatica_flow-0.1.0.dist-info"
    assert result["dramatica_flow_dist_info_count"] == 1


def test_dramatica_flow_t020a_editable_install_detection(
    dramatica_flow_tmp_repo,
) -> None:
    result = preflight._dramatica_flow_runtime_probe({})

    assert result["dramatica_flow_editable_install"] is True
    assert result["dramatica_flow_direct_url_present"] is True
    assert result["dramatica_flow_direct_url_error"] == ""


def test_dramatica_flow_t020a_expected_editable_source_match(
    dramatica_flow_tmp_repo,
) -> None:
    result = preflight._dramatica_flow_runtime_probe({})

    assert result["dramatica_flow_editable_source_matches_expected"] is True
    assert result["dramatica_flow_editable_source"].endswith(
        "/.external_sources/dramatica-flow"
    )


def test_dramatica_flow_t020a_source_mismatch_reports_false(
    monkeypatch, tmp_path
) -> None:
    source_root = tmp_path / ".external_sources" / "dramatica-flow"
    _write_minimal_dramatica_flow_source(source_root)
    venv_root = tmp_path / ".external_sources" / "venvs" / "dramatica-flow"
    _write_minimal_dramatica_flow_venv(
        venv_root,
        editable_source_url="file:///some/other/path",
    )
    monkeypatch.setattr(preflight, "_REPO_ROOT", tmp_path)

    result = preflight._dramatica_flow_runtime_probe({})

    assert result["dramatica_flow_editable_install"] is True
    assert result["dramatica_flow_editable_source_matches_expected"] is False


def test_dramatica_flow_t020a_malformed_direct_url(
    monkeypatch, tmp_path
) -> None:
    source_root = tmp_path / ".external_sources" / "dramatica-flow"
    _write_minimal_dramatica_flow_source(source_root)
    venv_root = tmp_path / ".external_sources" / "venvs" / "dramatica-flow"
    _write_minimal_dramatica_flow_venv(venv_root)
    dist_info = (
        venv_root
        / "lib"
        / "python3.12"
        / "site-packages"
        / "dramatica_flow-0.1.0.dist-info"
    )
    (dist_info / "direct_url.json").write_text("{ not valid json", encoding="utf-8")
    monkeypatch.setattr(preflight, "_REPO_ROOT", tmp_path)

    result = preflight._dramatica_flow_runtime_probe({})

    assert result["dramatica_flow_direct_url_present"] is False
    assert "invalid JSON" in result["dramatica_flow_direct_url_error"]
    assert result["dramatica_flow_editable_install"] is False
    assert result["dramatica_flow_editable_source_matches_expected"] is False


def test_dramatica_flow_t020a_malformed_entry_points(
    monkeypatch, tmp_path
) -> None:
    source_root = tmp_path / ".external_sources" / "dramatica-flow"
    _write_minimal_dramatica_flow_source(source_root)
    venv_root = tmp_path / ".external_sources" / "venvs" / "dramatica-flow"
    _write_minimal_dramatica_flow_venv(venv_root)
    dist_info = (
        venv_root
        / "lib"
        / "python3.12"
        / "site-packages"
        / "dramatica_flow-0.1.0.dist-info"
    )
    (dist_info / "entry_points.txt").write_text(
        "[console_scripts]\nbroken line without equals\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(preflight, "_REPO_ROOT", tmp_path)

    result = preflight._dramatica_flow_runtime_probe({})

    assert result["dramatica_flow_dist_info_console_script_name"] == ""
    assert result["dramatica_flow_dist_info_console_script_target"] == ""
    assert result["dramatica_flow_console_script_name"] == "df"
    assert result["dramatica_flow_console_script_target"] == "cli.main:app"


def test_dramatica_flow_t020a_malformed_pyproject_fails_closed(
    monkeypatch, tmp_path
) -> None:
    source_root = tmp_path / ".external_sources" / "dramatica-flow"
    _write_minimal_dramatica_flow_source(source_root)
    (source_root / "pyproject.toml").write_text("[project\n", encoding="utf-8")
    venv_root = tmp_path / ".external_sources" / "venvs" / "dramatica-flow"
    _write_minimal_dramatica_flow_venv(venv_root)
    monkeypatch.setattr(preflight, "_REPO_ROOT", tmp_path)

    result = preflight._dramatica_flow_runtime_probe({})

    assert result["dramatica_flow_pyproject_available"] is True
    assert result["dramatica_flow_package_name"] == ""
    assert result["dramatica_flow_package_version"] == ""
    assert result["dramatica_flow_requires_python"] == ""
    assert result["dramatica_flow_console_script_name"] == "df"
    assert result["dramatica_flow_dist_info_package_name"] == "dramatica-flow"
    assert result["dramatica_flow_package_metadata_consistent"] is False
    assert result["dramatica_flow_reference_surface_available"] is False
    assert result["dramatica_flow_runtime_surface"] == "degraded"
    assert result["dramatica_flow_live_runtime_available"] is False


def test_dramatica_flow_t020a_malformed_cli_source_fails_closed(
    monkeypatch, tmp_path
) -> None:
    source_root = tmp_path / ".external_sources" / "dramatica-flow"
    _write_minimal_dramatica_flow_source(source_root)
    (source_root / "cli" / "main.py").write_text(
        "def broken(:\n", encoding="utf-8"
    )
    venv_root = tmp_path / ".external_sources" / "venvs" / "dramatica-flow"
    _write_minimal_dramatica_flow_venv(venv_root)
    monkeypatch.setattr(preflight, "_REPO_ROOT", tmp_path)

    result = preflight._dramatica_flow_runtime_probe({})

    assert result["dramatica_flow_cli_source_available"] is True
    assert result["dramatica_flow_detected_cli_commands"] == []
    assert result["dramatica_flow_analysis_candidate_commands"] == []
    assert result["dramatica_flow_prose_production_commands"] == []
    assert result["dramatica_flow_live_runtime_available"] is False


def test_dramatica_flow_t020a_non_file_direct_url_fails_closed(
    monkeypatch, tmp_path
) -> None:
    source_root = tmp_path / ".external_sources" / "dramatica-flow"
    _write_minimal_dramatica_flow_source(source_root)
    venv_root = tmp_path / ".external_sources" / "venvs" / "dramatica-flow"
    _write_minimal_dramatica_flow_venv(
        venv_root,
        editable_source_url="https://example.test/dramatica-flow",
    )
    monkeypatch.setattr(preflight, "_REPO_ROOT", tmp_path)

    result = preflight._dramatica_flow_runtime_probe({})

    assert result["dramatica_flow_direct_url_present"] is True
    assert result["dramatica_flow_editable_install"] is True
    assert result["dramatica_flow_editable_source_matches_expected"] is False
    assert result["dramatica_flow_live_runtime_available"] is False


def test_dramatica_flow_t020a_non_editable_direct_url_fails_closed(
    monkeypatch, tmp_path
) -> None:
    source_root = tmp_path / ".external_sources" / "dramatica-flow"
    _write_minimal_dramatica_flow_source(source_root)
    venv_root = tmp_path / ".external_sources" / "venvs" / "dramatica-flow"
    _write_minimal_dramatica_flow_venv(venv_root, include_editable=False)
    monkeypatch.setattr(preflight, "_REPO_ROOT", tmp_path)

    result = preflight._dramatica_flow_runtime_probe({})

    assert result["dramatica_flow_direct_url_present"] is True
    assert result["dramatica_flow_editable_install"] is False
    assert result["dramatica_flow_editable_source_matches_expected"] is False
    assert result["dramatica_flow_installation_surface_available"] is False
    assert result["dramatica_flow_live_runtime_available"] is False


def test_dramatica_flow_t020a_multiple_dist_info_directories(
    monkeypatch, tmp_path
) -> None:
    source_root = tmp_path / ".external_sources" / "dramatica-flow"
    _write_minimal_dramatica_flow_source(source_root)
    venv_root = tmp_path / ".external_sources" / "venvs" / "dramatica-flow"
    _write_minimal_dramatica_flow_venv(
        venv_root,
        extra_dist_infos=("dramatica_flow-0.2.0.dist-info",),
    )
    monkeypatch.setattr(preflight, "_REPO_ROOT", tmp_path)

    result = preflight._dramatica_flow_runtime_probe({})

    assert result["dramatica_flow_dist_info_available"] is False
    assert result["dramatica_flow_dist_info_count"] == 2
    assert result["dramatica_flow_installation_surface_available"] is False
    assert result["dramatica_flow_runtime_surface"] == "source_only"


def test_dramatica_flow_t020a_command_discovery(
    dramatica_flow_tmp_repo,
) -> None:
    result = preflight._dramatica_flow_runtime_probe({})

    detected = set(result["dramatica_flow_detected_cli_commands"])
    for expected in (
        "init",
        "book",
        "setup",
        "write",
        "audit",
        "revise",
        "status",
        "export",
        "doctor",
    ):
        assert expected in detected
    assert detected == set(result["dramatica_flow_detected_cli_commands"])
    assert result["dramatica_flow_detected_cli_commands"] == sorted(
        result["dramatica_flow_detected_cli_commands"]
    )


def test_dramatica_flow_t020a_analysis_candidate_command_classification(
    monkeypatch,
) -> None:
    _patch_dramatica_flow_probe(monkeypatch, _dramatica_flow_full_surface_result())
    tool = _tools_by_name(_report())["dramatica_flow"]

    assert tool["dramatica_flow_analysis_candidate_commands"] == ["audit", "status"]


def test_dramatica_flow_t020a_prose_production_command_classification(
    monkeypatch,
) -> None:
    _patch_dramatica_flow_probe(monkeypatch, _dramatica_flow_full_surface_result())
    tool = _tools_by_name(_report())["dramatica_flow"]

    assert tool["dramatica_flow_prose_production_commands"] == [
        "export",
        "revise",
        "write",
    ]


def test_dramatica_flow_t020a_doctor_not_classified_as_safe_analysis(
    monkeypatch,
) -> None:
    _patch_dramatica_flow_probe(monkeypatch, _dramatica_flow_full_surface_result())
    tool = _tools_by_name(_report())["dramatica_flow"]

    assert "doctor" not in tool["dramatica_flow_analysis_candidate_commands"]
    assert "doctor" not in tool["dramatica_flow_prose_production_commands"]


def test_dramatica_flow_t020a_model_network_capability_detection(
    dramatica_flow_tmp_repo,
) -> None:
    result = preflight._dramatica_flow_runtime_probe({})

    assert result["dramatica_flow_model_or_network_surface_detected"] is True


def test_dramatica_flow_t020a_project_mutation_capability_detection(
    dramatica_flow_tmp_repo,
) -> None:
    result = preflight._dramatica_flow_runtime_probe({})

    assert result["dramatica_flow_project_mutation_surface_detected"] is True


def test_dramatica_flow_t020a_readme_mit_claim(
    dramatica_flow_tmp_repo,
) -> None:
    result = preflight._dramatica_flow_runtime_probe({})

    assert result["dramatica_flow_license_claimed"] is True
    assert result["dramatica_flow_license_name"] == "MIT"
    assert "README.md" in result["dramatica_flow_license_source"]
    assert "README_EN.md" in result["dramatica_flow_license_source"]


def test_dramatica_flow_t020a_missing_root_license_file(
    dramatica_flow_tmp_repo,
) -> None:
    result = preflight._dramatica_flow_runtime_probe({})

    assert result["dramatica_flow_license_file_available"] is False
    assert result["dramatica_flow_license_verified"] is False


def test_dramatica_flow_t020a_present_root_license_file(
    monkeypatch, tmp_path
) -> None:
    source_root = tmp_path / ".external_sources" / "dramatica-flow"
    _write_minimal_dramatica_flow_source(source_root)
    (source_root / "LICENSE").write_text("MIT License\n", encoding="utf-8")
    venv_root = tmp_path / ".external_sources" / "venvs" / "dramatica-flow"
    _write_minimal_dramatica_flow_venv(venv_root)
    monkeypatch.setattr(preflight, "_REPO_ROOT", tmp_path)

    result = preflight._dramatica_flow_runtime_probe({})

    assert result["dramatica_flow_license_claimed"] is True
    assert result["dramatica_flow_license_file_available"] is True
    assert result["dramatica_flow_license_verified"] is True


def test_dramatica_flow_t020a_license_claim_is_not_license_verification(
    dramatica_flow_tmp_repo,
) -> None:
    result = preflight._dramatica_flow_runtime_probe({})

    assert result["dramatica_flow_license_claimed"] is True
    assert result["dramatica_flow_license_verified"] is False


def test_dramatica_flow_t020a_live_runtime_always_false(
    monkeypatch,
) -> None:
    _patch_dramatica_flow_probe(monkeypatch, _dramatica_flow_full_surface_result())
    for env in (
        {},
        {
            "OMI_LIVE_TOOLS_ENABLED": "true",
            "OMI_LIVE_DRAMATICA_FLOW_ENABLED": "true",
            "OMI_LIVE_DRAMATICA_FLOW_COMMAND": "df",
            "OMI_LIVE_DRAMATICA_FLOW_PATH": "/opt/df",
        },
        {
            "OMI_LIVE_DRAMATICA_FLOW_BLOCKED": "false",
        },
    ):
        tool = _tools_by_name(_report(env))["dramatica_flow"]
        assert tool["dramatica_flow_live_runtime_available"] is False
        assert tool["runtime_dependency_available"] is False


def test_dramatica_flow_t020a_analysis_only_authorization_always_false(
    monkeypatch,
) -> None:
    _patch_dramatica_flow_probe(monkeypatch, _dramatica_flow_full_surface_result())
    for env in (
        {},
        {
            "OMI_LIVE_TOOLS_ENABLED": "true",
            "OMI_LIVE_DRAMATICA_FLOW_ENABLED": "true",
            "OMI_LIVE_DRAMATICA_FLOW_COMMAND": "df",
        },
    ):
        tool = _tools_by_name(_report(env))["dramatica_flow"]
        assert tool["dramatica_flow_analysis_only_runtime_authorized"] is False


def test_dramatica_flow_t020a_integration_decision_required(
    monkeypatch,
) -> None:
    _patch_dramatica_flow_probe(monkeypatch, _dramatica_flow_full_surface_result())
    tool = _tools_by_name(_report())["dramatica_flow"]

    assert tool["dramatica_flow_integration_decision_required"] is True


def test_dramatica_flow_t020a_configured_command_does_not_enable_runtime(
    monkeypatch,
) -> None:
    _patch_dramatica_flow_probe(monkeypatch, _dramatica_flow_full_surface_result())
    tool = _tools_by_name(
        _report({"OMI_LIVE_DRAMATICA_FLOW_COMMAND": "df"})
    )["dramatica_flow"]

    assert tool["dramatica_flow_command_configured"] is True
    assert tool["dramatica_flow_command_value"] == "df"
    assert tool["dramatica_flow_live_runtime_available"] is False


def test_dramatica_flow_t020a_configured_path_does_not_enable_runtime(
    monkeypatch,
) -> None:
    _patch_dramatica_flow_probe(monkeypatch, _dramatica_flow_full_surface_result())
    tool = _tools_by_name(
        _report({"OMI_LIVE_DRAMATICA_FLOW_PATH": "/opt/df"})
    )["dramatica_flow"]

    assert tool["dramatica_flow_path_configured"] is True
    assert tool["dramatica_flow_path_value"] == "/opt/df"
    assert tool["dramatica_flow_live_runtime_available"] is False


def test_dramatica_flow_t020a_global_per_tool_enabled_does_not_enable_runtime(
    monkeypatch,
) -> None:
    _patch_dramatica_flow_probe(monkeypatch, _dramatica_flow_full_surface_result())
    tool = _tools_by_name(
        _report(
            {
                "OMI_LIVE_TOOLS_ENABLED": "true",
                "OMI_LIVE_DRAMATICA_FLOW_ENABLED": "true",
            }
        )
    )["dramatica_flow"]

    assert tool["global_enabled"] is True
    assert tool["tool_enabled"] is True
    assert tool["runtime_enabled"] is True
    assert tool["dramatica_flow_live_runtime_available"] is False
    assert tool["runtime_dependency_available"] is False
    assert tool["status"] in {"disabled", "unavailable"}


def test_dramatica_flow_t020a_blocked_state_remains_authoritative(
    monkeypatch,
) -> None:
    _patch_dramatica_flow_probe(monkeypatch, _dramatica_flow_full_surface_result())
    tool = _tools_by_name(
        _report(
            {
                "OMI_LIVE_TOOLS_ENABLED": "true",
                "OMI_LIVE_DRAMATICA_FLOW_ENABLED": "true",
                "OMI_LIVE_DRAMATICA_FLOW_BLOCKED": "true",
                "OMI_LIVE_DRAMATICA_FLOW_BLOCKED_REASON": (
                    "T020A: owner decision pending."
                ),
            }
        )
    )["dramatica_flow"]

    assert tool["status"] == "blocked"
    assert tool["blocked"] is True
    assert tool["blocked_reason"] == "T020A: owner decision pending."
    assert tool["dramatica_flow_live_runtime_available"] is False
    assert tool["dramatica_flow_reference_surface_available"] is True
    assert tool["dramatica_flow_installation_surface_available"] is True


def test_dramatica_flow_t020a_dependency_record_contains_new_fields(
    monkeypatch,
) -> None:
    _patch_dramatica_flow_probe(monkeypatch, _dramatica_flow_full_surface_result())
    tool = _tools_by_name(_report())["dramatica_flow"]

    for key in (
        "dramatica_flow_source_root",
        "dramatica_flow_source_available",
        "dramatica_flow_pyproject_available",
        "dramatica_flow_readme_available",
        "dramatica_flow_readme_en_available",
        "dramatica_flow_cli_source_available",
        "dramatica_flow_validators_source_available",
        "dramatica_flow_package_name",
        "dramatica_flow_package_version",
        "dramatica_flow_requires_python",
        "dramatica_flow_declared_dependencies",
        "dramatica_flow_console_script_name",
        "dramatica_flow_console_script_target",
        "dramatica_flow_package_metadata_consistent",
        "dramatica_flow_console_script_consistent",
        "dramatica_flow_dist_info_metadata_consistent",
        "dramatica_flow_dist_info_console_script_consistent",
        "dramatica_flow_venv_root",
        "dramatica_flow_venv_available",
        "dramatica_flow_venv_python_available",
        "dramatica_flow_df_entrypoint_available",
        "dramatica_flow_dist_info_available",
        "dramatica_flow_editable_install",
        "dramatica_flow_editable_source",
        "dramatica_flow_editable_source_matches_expected",
        "dramatica_flow_detected_cli_commands",
        "dramatica_flow_analysis_candidate_commands",
        "dramatica_flow_prose_production_commands",
        "dramatica_flow_model_or_network_surface_detected",
        "dramatica_flow_project_mutation_surface_detected",
        "dramatica_flow_license_claimed",
        "dramatica_flow_license_name",
        "dramatica_flow_license_source",
        "dramatica_flow_license_file_available",
        "dramatica_flow_license_verified",
        "dramatica_flow_reference_surface_available",
        "dramatica_flow_installation_surface_available",
        "dramatica_flow_analysis_only_runtime_authorized",
        "dramatica_flow_live_runtime_available",
        "dramatica_flow_integration_decision_required",
        "dramatica_flow_runtime_surface",
        "dramatica_flow_command_env",
        "dramatica_flow_path_env",
        "dramatica_flow_probe_detail",
    ):
        assert key in tool, f"missing key: {key}"


def test_dramatica_flow_t020a_no_subprocess_shell_network_behavior(
    monkeypatch,
    dramatica_flow_tmp_repo,
) -> None:
    import subprocess
    import urllib.request

    attempted_subprocess: list[tuple[str, tuple]] = []
    attempted_network: list[tuple[str, tuple]] = []

    def fake_subprocess_run(*args, **kwargs):
        attempted_subprocess.append(("subprocess.run", args))
        raise AssertionError(
            "subprocess.run must not be called by dramatica-flow preflight"
        )

    def fake_subprocess_popen(*args, **kwargs):
        attempted_subprocess.append(("subprocess.Popen", args))
        raise AssertionError(
            "subprocess.Popen must not be called by dramatica-flow preflight"
        )

    def fake_urlopen(*args, **kwargs):
        attempted_network.append(("urlopen", args))
        raise AssertionError(
            "urllib urlopen must not be called by dramatica-flow preflight"
        )

    monkeypatch.setattr(subprocess, "run", fake_subprocess_run, raising=False)
    monkeypatch.setattr(subprocess, "Popen", fake_subprocess_popen, raising=False)
    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    result = preflight._dramatica_flow_runtime_probe({})

    assert attempted_subprocess == []
    assert attempted_network == []
    assert result["dramatica_flow_source_available"] is True
    assert result["dramatica_flow_runtime_surface"] == "installed_reference_surface"
    assert result["dramatica_flow_live_runtime_available"] is False
    assert result["dramatica_flow_analysis_only_runtime_authorized"] is False


def test_dramatica_flow_t020a_complete_report_isolates_unrelated_probes(
    monkeypatch,
) -> None:
    _patch_dramatica_flow_probe(monkeypatch, _dramatica_flow_full_surface_result())

    import subprocess
    import urllib.request

    def fake_subprocess_run(*args, **kwargs):
        raise AssertionError("unrelated subprocess.run must stay isolated")

    def fake_subprocess_popen(*args, **kwargs):
        raise AssertionError("unrelated subprocess.Popen must stay isolated")

    def fake_urlopen(*args, **kwargs):
        raise AssertionError("unrelated urllib urlopen must stay isolated")

    monkeypatch.setattr(subprocess, "run", fake_subprocess_run, raising=False)
    monkeypatch.setattr(subprocess, "Popen", fake_subprocess_popen, raising=False)
    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    report = _report(
        {
            "OMI_LIVE_TOOLS_ENABLED": "true",
            "OMI_LIVE_DRAMATICA_FLOW_ENABLED": "true",
        }
    )

    tool = _tools_by_name(report)["dramatica_flow"]
    assert tool["safety"]["read_only"] is True
    assert tool["safety"]["external_services_called"] is False
    assert tool["safety"]["live_models_called"] is False
    assert tool["safety"]["heavy_analysis_executed"] is False
    assert tool["safety"]["candidate_persistence"] is False
    assert tool["safety"]["memory_canon_mutation"] is False
    assert tool["safety"]["promotion_or_apply_promotion"] is False
    assert tool["safety"]["story_prose_generated"] is False


def test_dramatica_flow_t020a_no_source_or_venv_mutation(
    tmp_path, monkeypatch
) -> None:
    src_root = tmp_path / ".external_sources" / "dramatica-flow"
    _write_minimal_dramatica_flow_source(src_root)
    venv_root = tmp_path / ".external_sources" / "venvs" / "dramatica-flow"
    _write_minimal_dramatica_flow_venv(venv_root)
    monkeypatch.setattr(preflight, "_REPO_ROOT", tmp_path)

    before = []
    for path in (
        src_root / "pyproject.toml",
        src_root / "README.md",
        src_root / "README_EN.md",
        src_root / "cli" / "main.py",
        src_root / "core" / "validators" / "__init__.py",
        venv_root / "bin" / "python",
        venv_root / "bin" / "df",
        venv_root / "lib" / "python3.12" / "site-packages"
        / "dramatica_flow-0.1.0.dist-info" / "direct_url.json",
        venv_root / "lib" / "python3.12" / "site-packages"
        / "dramatica_flow-0.1.0.dist-info" / "entry_points.txt",
        venv_root / "lib" / "python3.12" / "site-packages"
        / "dramatica_flow-0.1.0.dist-info" / "METADATA",
    ):
        before.append(
            (str(path), path.read_bytes())
        )

    preflight._dramatica_flow_runtime_probe({})
    _patch_dramatica_flow_probe(monkeypatch, _dramatica_flow_full_surface_result())
    _report(
        {
            "OMI_LIVE_TOOLS_ENABLED": "true",
            "OMI_LIVE_DRAMATICA_FLOW_ENABLED": "true",
        }
    )

    for path_str, original_bytes in before:
        with open(path_str, "rb") as handle:
            current_bytes = handle.read()
        assert current_bytes == original_bytes


def test_dramatica_flow_t020a_existing_tool_preflight_behavior_unchanged(
    monkeypatch,
) -> None:
    _patch_dramatica_flow_probe(monkeypatch, _dramatica_flow_full_surface_result())

    report = _report()
    tools = _tools_by_name(report)

    assert tools["spacy"]["status"] in {"disabled", "available"}
    assert tools["ollama_model"]["status"] in {"disabled", "available", "unavailable"}
    assert tools["story_check"]["status"] in {"disabled", "available", "unavailable"}
    assert tools["booknlp"]["status"] in {"disabled", "available", "unavailable"}
    assert tools["ncp"]["status"] in {"disabled", "available", "unavailable"}
    assert tools["subtxt"]["status"] in {"disabled", "available", "unavailable"}
    assert tools["deterministic_fallback"]["status"] in {"disabled", "available"}
    assert tools["dramatica_flow"]["status"] in {"disabled", "available", "unavailable"}
    for tool in tools.values():
        assert tool["safety"]["read_only"] is True
        assert tool["safety"]["candidate_persistence"] is False
        assert tool["safety"]["memory_canon_mutation"] is False
        assert tool["safety"]["promotion_or_apply_promotion"] is False
        assert tool["safety"]["story_prose_generated"] is False
