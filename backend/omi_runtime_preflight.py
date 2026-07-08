"""Read-only runtime preflight for future live OMI tool adapters.

T013 scope only: report configuration, feature-flag, fixture-contract, and
dependency availability signals without running analysis, models, or external
services.
"""

from __future__ import annotations

import importlib.util
import os
import shutil
from pathlib import Path
from typing import Any, Mapping

try:
    from . import omi_analysis_orchestrator as oao
except ImportError:  # pragma: no cover - supports direct backend/ imports
    import omi_analysis_orchestrator as oao


OMI_RUNTIME_PREFLIGHT_STATUSES: frozenset[str] = frozenset(
    {
        "enabled",
        "disabled",
        "available",
        "unavailable",
        "blocked",
        "error",
        "not_configured",
    }
)

OMI_LIVE_TOOLS_ENABLED_ENV = "OMI_LIVE_TOOLS_ENABLED"
OMI_LIVE_RUNTIME_TESTS_ENV = "OMI_LIVE_RUNTIME_TESTS"

OMI_LIVE_TOOL_ENABLED_ENVS: dict[str, str] = {
    "spacy": "OMI_LIVE_SPACY_ENABLED",
    "ollama_model": "OMI_LIVE_OLLAMA_ENABLED",
    "story_check": "OMI_LIVE_STORY_CHECK_ENABLED",
    "booknlp": "OMI_LIVE_BOOKNLP_ENABLED",
    "ncp": "OMI_LIVE_NCP_ENABLED",
    "subtxt": "OMI_LIVE_SUBTXT_ENABLED",
    "dramatica_flow": "OMI_LIVE_DRAMATICA_FLOW_ENABLED",
    "deterministic_fallback": "OMI_LIVE_DETERMINISTIC_FALLBACK_ENABLED",
}

OMI_LIVE_TOOL_BLOCKED_ENVS: dict[str, str] = {
    adapter: f"{enabled_env.removesuffix('_ENABLED')}_BLOCKED"
    for adapter, enabled_env in OMI_LIVE_TOOL_ENABLED_ENVS.items()
}

OMI_LIVE_TOOL_BLOCKED_REASON_ENVS: dict[str, str] = {
    adapter: f"{blocked_env}_REASON"
    for adapter, blocked_env in OMI_LIVE_TOOL_BLOCKED_ENVS.items()
}

_REPO_ROOT = Path(__file__).resolve().parents[1]


def _env_bool(env: Mapping[str, str], name: str, default: bool = False) -> bool:
    value = env.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_text(env: Mapping[str, str], name: str) -> str | None:
    value = env.get(name)
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _find_module(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def _path_exists(relative_path: str) -> bool:
    return (_REPO_ROOT / relative_path).exists()


def _dependency_probe(adapter: str, env: Mapping[str, str]) -> dict[str, Any]:
    if adapter == "spacy":
        configured = True
        available = _find_module("spacy")
        detail = "Python package probe: spacy"
    elif adapter == "booknlp":
        configured = True
        available = _find_module("booknlp") or shutil.which("booknlp") is not None
        detail = "Python package/executable probe: booknlp"
    elif adapter == "ollama_model":
        configured = bool(
            _env_text(env, "OMI_LIVE_OLLAMA_MODEL")
            or _env_text(env, "OMI_LIVE_OLLAMA_MODEL_NAME")
            or shutil.which("ollama")
        )
        available = shutil.which("ollama") is not None
        detail = "Executable probe only: ollama; no HTTP/model call"
    elif adapter == "story_check":
        configured = _path_exists("backend/analysis_engine.py")
        available = configured
        detail = "In-repo module surface probe: backend/analysis_engine.py"
    elif adapter == "ncp":
        configured = bool(
            _env_text(env, "OMI_LIVE_NCP_COMMAND")
            or _env_text(env, "OMI_LIVE_NCP_PATH")
            or _path_exists(".external_sources")
        )
        command = _env_text(env, "OMI_LIVE_NCP_COMMAND")
        path = _env_text(env, "OMI_LIVE_NCP_PATH")
        available = bool(
            (command and shutil.which(command))
            or (path and Path(path).exists())
            or _path_exists(".external_sources")
        )
        detail = "Configured command/path or existing in-repo source surface probe"
    elif adapter == "subtxt":
        configured = bool(
            _env_text(env, "OMI_LIVE_SUBTXT_COMMAND")
            or _env_text(env, "OMI_LIVE_SUBTXT_PATH")
            or _path_exists(".external_sources")
        )
        command = _env_text(env, "OMI_LIVE_SUBTXT_COMMAND")
        path = _env_text(env, "OMI_LIVE_SUBTXT_PATH")
        available = bool(
            (command and shutil.which(command))
            or (path and Path(path).exists())
            or _path_exists(".external_sources")
        )
        detail = "Configured command/path or existing in-repo source surface probe"
    elif adapter == "dramatica_flow":
        configured = bool(
            _env_text(env, "OMI_LIVE_DRAMATICA_FLOW_COMMAND")
            or _env_text(env, "OMI_LIVE_DRAMATICA_FLOW_PATH")
            or _path_exists(".external_sources")
        )
        command = _env_text(env, "OMI_LIVE_DRAMATICA_FLOW_COMMAND")
        path = _env_text(env, "OMI_LIVE_DRAMATICA_FLOW_PATH")
        available = bool(
            (command and shutil.which(command))
            or (path and Path(path).exists())
            or _path_exists(".external_sources")
        )
        detail = "Configured command/path or existing in-repo source surface probe"
    elif adapter == "deterministic_fallback":
        configured = True
        available = hasattr(oao, "OMI_DETERMINISTIC_FALLBACK_ADAPTER_NAME")
        detail = "In-repo fallback surface probe only"
    else:
        configured = False
        available = False
        detail = "Unknown adapter"

    dependency_status = (
        "available" if available else "not_configured" if not configured else "unavailable"
    )
    return {
        "runtime_configured": configured,
        "runtime_dependency_available": available,
        "runtime_dependency_status": dependency_status,
        "probe_detail": detail,
    }


def _tool_report(adapter: str, env: Mapping[str, str]) -> dict[str, Any]:
    enabled_env = OMI_LIVE_TOOL_ENABLED_ENVS[adapter]
    blocked_env = OMI_LIVE_TOOL_BLOCKED_ENVS[adapter]
    blocked_reason_env = OMI_LIVE_TOOL_BLOCKED_REASON_ENVS[adapter]

    fixture_contract_exists = adapter in oao.OMI_ADAPTER_CONTRACTS
    global_enabled = _env_bool(env, OMI_LIVE_TOOLS_ENABLED_ENV)
    tool_enabled = _env_bool(env, enabled_env)
    runtime_tests_enabled = _env_bool(env, OMI_LIVE_RUNTIME_TESTS_ENV)
    runtime_enabled = global_enabled and tool_enabled
    blocked = _env_bool(env, blocked_env)

    try:
        dependency = _dependency_probe(adapter, env)
        if blocked:
            status = "blocked"
            explanation = "Tool is explicitly blocked by environment/configuration."
        elif runtime_enabled and not dependency["runtime_configured"]:
            status = "not_configured"
            explanation = "Live runtime is enabled but required configuration is missing."
        elif runtime_enabled and not dependency["runtime_dependency_available"]:
            status = "unavailable"
            explanation = "Live runtime is enabled but dependency probe is unavailable."
        elif runtime_enabled:
            status = "enabled"
            explanation = "Live runtime is feature-flag enabled for local/manual use."
        elif dependency["runtime_dependency_available"]:
            status = "available"
            explanation = "Dependency appears available, but live runtime flags are disabled."
        else:
            status = "disabled"
            explanation = "Live runtime flags are disabled; no runtime analysis was run."
    except Exception as exc:  # pragma: no cover - defensive fail-closed branch
        dependency = {
            "runtime_configured": False,
            "runtime_dependency_available": False,
            "runtime_dependency_status": "error",
            "probe_detail": f"{type(exc).__name__}: {exc}",
        }
        status = "error"
        explanation = "Read-only runtime preflight failed for this adapter."

    if status not in OMI_RUNTIME_PREFLIGHT_STATUSES:
        status = "error"

    return {
        "tool": adapter,
        "status": status,
        "fixture_contract_exists": fixture_contract_exists,
        "runtime_configured": dependency["runtime_configured"],
        "runtime_dependency_available": dependency["runtime_dependency_available"],
        "runtime_dependency_status": dependency["runtime_dependency_status"],
        "runtime_enabled": runtime_enabled,
        "global_enabled": global_enabled,
        "tool_enabled": tool_enabled,
        "runtime_tests_enabled": runtime_tests_enabled,
        "feature_flags": {
            "global": OMI_LIVE_TOOLS_ENABLED_ENV,
            "tool": enabled_env,
            "runtime_tests": OMI_LIVE_RUNTIME_TESTS_ENV,
            "blocked": blocked_env,
            "blocked_reason": blocked_reason_env,
        },
        "blocked": blocked,
        "blocked_reason": _env_text(env, blocked_reason_env),
        "probe_detail": dependency["probe_detail"],
        "explanation": explanation,
        "safety": {
            "read_only": True,
            "heavy_analysis_executed": False,
            "external_services_called": False,
            "live_models_called": False,
            "candidate_persistence": False,
            "memory_canon_mutation": False,
            "promotion_or_apply_promotion": False,
            "story_prose_generated": False,
        },
    }


def build_omi_runtime_preflight_report(
    project_name: str | None = None,
    *,
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Return a read-only live-runtime readiness report.

    ``project_name`` is accepted for route symmetry only; the preflight does not
    load or mutate project files.
    """

    effective_env = os.environ if env is None else env
    tools = [_tool_report(adapter, effective_env) for adapter in sorted(OMI_LIVE_TOOL_ENABLED_ENVS)]

    return {
        "schema_version": "omi_runtime_preflight.v1",
        "project_name": project_name,
        "status_vocabulary": sorted(OMI_RUNTIME_PREFLIGHT_STATUSES),
        "global_live_tools_enabled": _env_bool(effective_env, OMI_LIVE_TOOLS_ENABLED_ENV),
        "live_runtime_tests_enabled": _env_bool(effective_env, OMI_LIVE_RUNTIME_TESTS_ENV),
        "feature_flags": {
            "global": OMI_LIVE_TOOLS_ENABLED_ENV,
            "runtime_tests": OMI_LIVE_RUNTIME_TESTS_ENV,
            "tools": dict(OMI_LIVE_TOOL_ENABLED_ENVS),
            "blocked": dict(OMI_LIVE_TOOL_BLOCKED_ENVS),
            "blocked_reasons": dict(OMI_LIVE_TOOL_BLOCKED_REASON_ENVS),
        },
        "tools": tools,
        "summary": {
            "tool_count": len(tools),
            "enabled": sum(1 for tool in tools if tool["status"] == "enabled"),
            "available": sum(1 for tool in tools if tool["status"] == "available"),
            "disabled": sum(1 for tool in tools if tool["status"] == "disabled"),
            "unavailable": sum(1 for tool in tools if tool["status"] == "unavailable"),
            "blocked": sum(1 for tool in tools if tool["status"] == "blocked"),
            "error": sum(1 for tool in tools if tool["status"] == "error"),
            "not_configured": sum(1 for tool in tools if tool["status"] == "not_configured"),
        },
        "safety": {
            "read_only": True,
            "heavy_analysis_executed": False,
            "external_services_called": False,
            "live_models_called": False,
            "candidate_persistence": False,
            "memory_canon_mutation": False,
            "promotion_or_apply_promotion": False,
            "story_prose_generated": False,
        },
        "mvp_note": (
            "Fixture contract availability and preflight readiness do not prove "
            "live analysis and do not count as PHASE8-IMPL-023 MVP completion."
        ),
    }
