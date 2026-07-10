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
        "ncp_detail": "all present",
    }


def _patch_ncp_probe(
    monkeypatch,
    result: dict[str, object] | None = None,
) -> None:
    """Patch ``_ncp_runtime_probe`` for tests that must not depend on the
    real ``.external_sources/narrative-context-protocol`` tree, real node,
    or real npm."""
    if result is None:
        result = _all_ncp_surfaces_available_result()
    monkeypatch.setattr(
        preflight,
        "_ncp_runtime_probe",
        lambda: {key: value for key, value in result.items()},
    )


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
