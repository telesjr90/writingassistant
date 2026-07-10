"""Read-only runtime preflight for future live OMI tool adapters.

T013 scope only: report configuration, feature-flag, fixture-contract, and
dependency availability signals without running analysis, models, or external
services.

T016B extends the ``story_check`` adapter probe with read-only checks for the
in-repo ``backend.analysis_engine`` runtime surface, the prompt file, the
mock fixture, ``backend.analysis_modes`` validity, the ``storyform`` surface,
and the ``requests`` Python package. T016B does not import or execute
``backend.analysis_engine.run_story_check``, does not call the legacy Story
Check route, and does not call Ollama.
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

OMI_LIVE_SPACY_MODEL_DEFAULT = "en_core_web_sm"
OMI_LIVE_SPACY_MODEL_ENV = "OMI_LIVE_SPACY_MODEL"

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

OMI_LIVE_OLLAMA_BASE_URL_ENV = "OMI_LIVE_OLLAMA_BASE_URL"
OMI_LIVE_OLLAMA_BASE_URL_DEFAULT = "http://127.0.0.1:11434"

OMI_LIVE_OLLAMA_MODEL_ENV = "OMI_LIVE_OLLAMA_MODEL"
OMI_LIVE_OLLAMA_MODEL_DEFAULT = "qwen3:8b"

STORY_CHECK_ANALYSIS_ENGINE_REL = "backend/analysis_engine.py"
STORY_CHECK_PROMPT_REL = "backend/prompts/story_check.txt"
STORY_CHECK_MOCK_FIXTURE_REL = "backend/mock_responses/story_check.json"
STORY_CHECK_ANALYSIS_MODES_REL = "backend/analysis_modes.py"
STORY_CHECK_STORYFORM_REL = "backend/storyform.py"
STORY_CHECK_REQUESTS_MODULE = "requests"
STORY_CHECK_ANALYSIS_MODE_ENV = "ANALYSIS_MODE"
STORY_CHECK_OLLAMA_BASE_URL_ENV = "OLLAMA_BASE_URL"
STORY_CHECK_OLLAMA_BASE_URL_DEFAULT = "http://localhost:11434"
STORY_CHECK_OLLAMA_MODEL_ENV = "OLLAMA_MODEL"
STORY_CHECK_OLLAMA_MODEL_DEFAULT = "qwen3:8b"
STORY_CHECK_OLLAMA_TIMEOUT_ENV = "OLLAMA_TIMEOUT_SECONDS"
STORY_CHECK_OLLAMA_TIMEOUT_DEFAULT = "300"

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


def _path_readable(relative_path: str) -> bool:
    """Read-only readability probe for a repo-relative file.

    Fail-closed: returns False when the file is missing, is not a regular
    file, or cannot be opened for reading. Does not read the contents and
    does not write anything.
    """
    try:
        path = _REPO_ROOT / relative_path
    except (TypeError, ValueError):
        return False
    try:
        if not path.is_file():
            return False
    except OSError:
        return False
    try:
        with path.open("rb"):
            return True
    except OSError:
        return False


def _spacy_model_probe(model_name: str) -> dict[str, Any]:
    """Probe spaCy package and selected model availability.

    Fail-closed, read-only. Only imports spaCy inside the probe path.
    Returns (spacy_package_available, spacy_model_available, model_name, detail).
    """
    if not _find_module("spacy"):
        return {
            "spacy_package_available": False,
            "spacy_model_available": False,
            "spacy_model_name": model_name,
            "spacy_probe_detail": "Python package not available: spacy",
        }
    try:
        import spacy

        spacy.load(model_name)
        return {
            "spacy_package_available": True,
            "spacy_model_available": True,
            "spacy_model_name": model_name,
            "spacy_probe_detail": f"spaCy model '{model_name}' loaded successfully",
        }
    except OSError as exc:
        return {
            "spacy_package_available": True,
            "spacy_model_available": False,
            "spacy_model_name": model_name,
            "spacy_probe_detail": (
                f"spaCy model '{model_name}' not found/loadable: {exc}"
            ),
        }
    except Exception as exc:
        return {
            "spacy_package_available": True,
            "spacy_model_available": False,
            "spacy_model_name": model_name,
            "spacy_probe_detail": (
                f"spaCy model '{model_name}' load failed: "
                f"{type(exc).__name__}: {exc}"
            ),
        }


def _story_check_runtime_probe(env: Mapping[str, str]) -> dict[str, Any]:
    """Read-only Story Check runtime preflight probe.

    T016B scope: confirm the in-repo Story Check runtime surface, the prompt
    file, the mock fixture, the ``analysis_modes`` module, the ``storyform``
    module surface, and the ``requests`` Python package are all available
    without importing or executing ``backend.analysis_engine.run_story_check``
    and without calling the legacy Story Check route. Also surfaces the
    configured Ollama baseline URL/model/timeout env vars as configuration
    only; it never calls Ollama.

    The result is a flat dict of booleans, configured values, and detail
    strings. The caller is responsible for combining these into a status
    word using the existing T013 status vocabulary.
    """
    analysis_engine_available = _path_exists(STORY_CHECK_ANALYSIS_ENGINE_REL)
    prompt_available = _path_exists(STORY_CHECK_PROMPT_REL)
    mock_fixture_available = _path_exists(STORY_CHECK_MOCK_FIXTURE_REL)
    analysis_modes_available = _path_exists(STORY_CHECK_ANALYSIS_MODES_REL)
    storyform_surface_available = _path_exists(STORY_CHECK_STORYFORM_REL)
    requests_available = _find_module(STORY_CHECK_REQUESTS_MODULE)

    missing: list[str] = []
    if not analysis_engine_available:
        missing.append(STORY_CHECK_ANALYSIS_ENGINE_REL)
    if not prompt_available:
        missing.append(STORY_CHECK_PROMPT_REL)
    if not analysis_modes_available:
        missing.append(STORY_CHECK_ANALYSIS_MODES_REL)
    if not storyform_surface_available:
        missing.append(STORY_CHECK_STORYFORM_REL)
    if not requests_available:
        missing.append(f"python:{STORY_CHECK_REQUESTS_MODULE}")

    optional_missing: list[str] = []
    if not mock_fixture_available:
        optional_missing.append(STORY_CHECK_MOCK_FIXTURE_REL)

    if missing:
        detail = (
            "Story Check runtime surface probe missing: "
            + ", ".join(missing)
        )
    elif optional_missing:
        detail = (
            "Story Check runtime surface probe: analysis_engine, prompt, "
            "analysis_modes, storyform, and requests package all present; "
            "optional missing: "
            + ", ".join(optional_missing)
        )
    else:
        detail = (
            "Story Check runtime surface probe: analysis_engine, prompt, mock "
            "fixture, analysis_modes, storyform, and requests package all present"
        )

    ollama_base_url = (
        _env_text(env, STORY_CHECK_OLLAMA_BASE_URL_ENV)
        or STORY_CHECK_OLLAMA_BASE_URL_DEFAULT
    )
    ollama_model_name = (
        _env_text(env, STORY_CHECK_OLLAMA_MODEL_ENV)
        or STORY_CHECK_OLLAMA_MODEL_DEFAULT
    )
    ollama_timeout_text = (
        _env_text(env, STORY_CHECK_OLLAMA_TIMEOUT_ENV)
        or STORY_CHECK_OLLAMA_TIMEOUT_DEFAULT
    )

    try:
        ollama_timeout_seconds: float = float(ollama_timeout_text)
    except (TypeError, ValueError):
        ollama_timeout_seconds = float(STORY_CHECK_OLLAMA_TIMEOUT_DEFAULT)

    analysis_mode_value = _env_text(env, STORY_CHECK_ANALYSIS_MODE_ENV) or ""
    try:
        valid_analysis_modes = {"mock", "ollama_baseline"}
        if analysis_mode_value == "":
            analysis_mode_configured = True
            analysis_mode_value = "ollama_baseline"
        else:
            analysis_mode_configured = analysis_mode_value in valid_analysis_modes
            if not analysis_mode_configured:
                analysis_mode_value = "ollama_baseline"
    except Exception:  # pragma: no cover - defensive fail-closed branch
        analysis_mode_configured = False
        analysis_mode_value = "ollama_baseline"

    return {
        "story_check_runtime_surface": (
            "available" if not missing else "unavailable"
        ),
        "story_check_analysis_engine_available": analysis_engine_available,
        "story_check_prompt_available": prompt_available,
        "story_check_mock_fixture_available": mock_fixture_available,
        "story_check_analysis_modes_available": analysis_modes_available,
        "story_check_storyform_surface_available": storyform_surface_available,
        "story_check_requests_available": requests_available,
        "story_check_ollama_base_url": ollama_base_url,
        "story_check_ollama_model_name": ollama_model_name,
        "story_check_ollama_timeout_seconds": ollama_timeout_seconds,
        "story_check_analysis_mode_value": analysis_mode_value,
        "story_check_analysis_mode_configured": analysis_mode_configured,
        "story_check_detail": detail,
    }


def _ollama_http_probe(base_url: str, model_name: str) -> dict[str, Any]:
    """Probe Ollama HTTP API availability.

    Read-only: only calls /api/version and /api/tags.
    Fail-closed on connection errors, timeouts, invalid JSON, missing fields.
    Uses Python standard library only (urllib.request).
    """
    import json
    import urllib.error
    import urllib.request

    clean_base = base_url.rstrip("/")
    result: dict[str, Any] = {
        "ollama_base_url": base_url,
        "ollama_api_available": False,
        "ollama_version": None,
        "ollama_model_name": model_name,
        "ollama_model_available": False,
        "ollama_probe_detail": "",
    }

    try:
        version_url = f"{clean_base}/api/version"
        req = urllib.request.Request(version_url, method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            version_data = json.loads(resp.read().decode())
        ollama_version = version_data.get("version")
        if not ollama_version:
            result["ollama_probe_detail"] = (
                f"Ollama HTTP API reachable at {clean_base} but "
                f"/api/version missing 'version' field"
            )
            return result
        result["ollama_version"] = ollama_version
    except json.JSONDecodeError as exc:
        result["ollama_probe_detail"] = (
            f"Ollama HTTP API /api/version returned invalid JSON at "
            f"{clean_base}: {exc}"
        )
        return result
    except Exception as exc:
        result["ollama_probe_detail"] = (
            f"Ollama HTTP API unavailable at {clean_base}: "
            f"{type(exc).__name__}: {exc}"
        )
        return result

    try:
        tags_url = f"{clean_base}/api/tags"
        req = urllib.request.Request(tags_url, method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            tags_data = json.loads(resp.read().decode())
        models = tags_data.get("models", [])
        model_names = [m.get("name", "") for m in models]
        model_available = model_name in model_names
        result["ollama_api_available"] = True
        result["ollama_model_available"] = model_available
        if model_available:
            result["ollama_probe_detail"] = (
                f"Ollama HTTP API available (version {ollama_version}), "
                f"model '{model_name}' found in /api/tags"
            )
        else:
            installed = ', '.join(sorted(model_names)) if model_names else "(none)"
            result["ollama_probe_detail"] = (
                f"Ollama HTTP API available (version {ollama_version}), "
                f"model '{model_name}' NOT found in /api/tags. "
                f"Installed models: {installed}"
            )
    except json.JSONDecodeError as exc:
        result["ollama_probe_detail"] = (
            f"Ollama HTTP API /api/tags returned invalid JSON at "
            f"{clean_base}: {exc}"
        )
    except Exception as exc:
        result["ollama_probe_detail"] = (
            f"Ollama HTTP API version probe succeeded (version {ollama_version}), "
            f"but /api/tags probe failed: {type(exc).__name__}: {exc}"
        )

    return result


def _dependency_probe(adapter: str, env: Mapping[str, str]) -> dict[str, Any]:
    if adapter == "spacy":
        configured = True
        model_name = (
            _env_text(env, OMI_LIVE_SPACY_MODEL_ENV) or OMI_LIVE_SPACY_MODEL_DEFAULT
        )
        probe = _spacy_model_probe(model_name)
        available = probe["spacy_package_available"] and probe["spacy_model_available"]
        detail = probe["spacy_probe_detail"]
        dependency_status = (
            "available" if available else "unavailable"
        )
        return {
            "runtime_configured": configured,
            "runtime_dependency_available": available,
            "runtime_dependency_status": dependency_status,
            "probe_detail": detail,
            "spacy_model_name": probe["spacy_model_name"],
            "spacy_model_available": probe["spacy_model_available"],
        }
    elif adapter == "booknlp":
        configured = True
        available = _find_module("booknlp") or shutil.which("booknlp") is not None
        detail = "Python package/executable probe: booknlp"
    elif adapter == "ollama_model":
        base_url = (
            _env_text(env, OMI_LIVE_OLLAMA_BASE_URL_ENV)
            or OMI_LIVE_OLLAMA_BASE_URL_DEFAULT
        )
        model_name = (
            _env_text(env, OMI_LIVE_OLLAMA_MODEL_ENV)
            or _env_text(env, "OMI_LIVE_OLLAMA_MODEL_NAME")
            or OMI_LIVE_OLLAMA_MODEL_DEFAULT
        )
        probe = _ollama_http_probe(base_url, model_name)
        configured = True
        available = probe["ollama_api_available"] and probe["ollama_model_available"]
        if not available and shutil.which("ollama"):
            available = True
            detail = (
                f"Ollama CLI available, HTTP API not probed/available "
                f"({probe['ollama_probe_detail']})"
            )
        else:
            detail = probe["ollama_probe_detail"]
        dependency_status = (
            "available" if available else "unavailable"
        )
        return {
            "runtime_configured": configured,
            "runtime_dependency_available": available,
            "runtime_dependency_status": dependency_status,
            "probe_detail": detail,
            "ollama_base_url": probe["ollama_base_url"],
            "ollama_api_available": probe["ollama_api_available"],
            "ollama_version": probe["ollama_version"],
            "ollama_model_name": probe["ollama_model_name"],
            "ollama_model_available": probe["ollama_model_available"],
            "ollama_probe_detail": probe["ollama_probe_detail"],
        }
    elif adapter == "story_check":
        probe = _story_check_runtime_probe(env)
        configured = bool(
            probe["story_check_analysis_engine_available"]
            and probe["story_check_prompt_available"]
            and probe["story_check_analysis_modes_available"]
            and probe["story_check_storyform_surface_available"]
            and probe["story_check_requests_available"]
        )
        available = configured
        detail = probe["story_check_detail"]
        return {
            "runtime_configured": configured,
            "runtime_dependency_available": available,
            "runtime_dependency_status": (
                "available" if available else "not_configured"
            ),
            "probe_detail": detail,
            "story_check_runtime_surface": probe["story_check_runtime_surface"],
            "story_check_analysis_engine_available": probe[
                "story_check_analysis_engine_available"
            ],
            "story_check_prompt_available": probe["story_check_prompt_available"],
            "story_check_mock_fixture_available": probe[
                "story_check_mock_fixture_available"
            ],
            "story_check_analysis_modes_available": probe[
                "story_check_analysis_modes_available"
            ],
            "story_check_storyform_surface_available": probe[
                "story_check_storyform_surface_available"
            ],
            "story_check_requests_available": probe["story_check_requests_available"],
            "story_check_ollama_base_url": probe["story_check_ollama_base_url"],
            "story_check_ollama_model_name": probe["story_check_ollama_model_name"],
            "story_check_ollama_timeout_seconds": probe[
                "story_check_ollama_timeout_seconds"
            ],
            "story_check_analysis_mode_value": probe[
                "story_check_analysis_mode_value"
            ],
            "story_check_analysis_mode_configured": probe[
                "story_check_analysis_mode_configured"
            ],
            "story_check_detail": detail,
        }
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

    report = {
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
    if adapter == "spacy":
        report["spacy_model_name"] = dependency.get("spacy_model_name")
        report["spacy_model_available"] = dependency.get("spacy_model_available")
    if adapter == "ollama_model":
        report["ollama_base_url"] = dependency.get("ollama_base_url")
        report["ollama_api_available"] = dependency.get("ollama_api_available")
        report["ollama_version"] = dependency.get("ollama_version")
        report["ollama_model_name"] = dependency.get("ollama_model_name")
        report["ollama_model_available"] = dependency.get("ollama_model_available")
        report["ollama_probe_detail"] = dependency.get("ollama_probe_detail")
    if adapter == "story_check":
        report["story_check_runtime_surface"] = dependency.get(
            "story_check_runtime_surface"
        )
        report["story_check_analysis_engine_available"] = dependency.get(
            "story_check_analysis_engine_available"
        )
        report["story_check_prompt_available"] = dependency.get(
            "story_check_prompt_available"
        )
        report["story_check_mock_fixture_available"] = dependency.get(
            "story_check_mock_fixture_available"
        )
        report["story_check_analysis_modes_available"] = dependency.get(
            "story_check_analysis_modes_available"
        )
        report["story_check_storyform_surface_available"] = dependency.get(
            "story_check_storyform_surface_available"
        )
        report["story_check_requests_available"] = dependency.get(
            "story_check_requests_available"
        )
        report["story_check_ollama_base_url"] = dependency.get(
            "story_check_ollama_base_url"
        )
        report["story_check_ollama_model_name"] = dependency.get(
            "story_check_ollama_model_name"
        )
        report["story_check_ollama_timeout_seconds"] = dependency.get(
            "story_check_ollama_timeout_seconds"
        )
        report["story_check_analysis_mode_value"] = dependency.get(
            "story_check_analysis_mode_value"
        )
        report["story_check_analysis_mode_configured"] = dependency.get(
            "story_check_analysis_mode_configured"
        )
        report["story_check_detail"] = dependency.get("story_check_detail")
    return report


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
