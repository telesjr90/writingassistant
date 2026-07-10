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
