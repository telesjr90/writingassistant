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

T018A extends the ``ncp`` adapter probe with a read-only schema-validator
surface inspection. NCP is treated as a schema/interchange validation
surface (not an automatic analysis runtime, not canon/truth). The probe
confirms the NCP source tree, ``package.json``, schema JSON/YAML, validator
scripts, and ``node``/``npm``/``node_modules`` are discoverable, and reports
a known ``ajv`` moderate / ``fast-uri`` high npm audit caveat. T018A never
runs ``npm install``, ``npm audit fix``, ``npm run validate:schema``, or
``npm run validate:file`` and never reads project data.

T018B extends the ``ncp`` adapter probe with read-only configuration
fields for the T018B live NCP candidate-import validation adapter. The
probe surfaces the explicit ``OMI_LIVE_NCP_INPUT_PATH`` and the opt-in
``OMI_LIVE_NCP_VALIDATE_WITH_NODE`` env vars as configuration only. The
probe does not read, parse, validate, or write any NCP file even when
the input path env var is set, and does not invoke Node or ``npm`` based
on these env vars. The probe is read-only and never mutates state.

T019A extends the ``subtxt`` adapter probe with a focused, read-only
Subtxt documentation/source preflight that replaces the current overbroad
generic Subtxt check. The new preflight inspects the actual local source
at ``.external_sources/subtxt-docs`` and accurately reports whether the
official Subtxt documentation source is present, whether its core
documentation surfaces are present, whether its README license declaration
and package metadata are discoverable, that this repository is a
documentation/reference surface (not a live Subtxt analysis runtime), that
no runnable Subtxt classifier, semantic-analysis executable, machine schema
validator, or local analysis API has been established, and that configured
command/path env vars are configuration evidence only and must not make the
runtime available. T019A does not implement a live Subtxt adapter.

T020A extends the ``dramatica_flow`` adapter probe with a focused, read-only
dramatica-flow source/runtime preflight. The new preflight inspects the
actual local source at ``.external_sources/dramatica-flow`` and the actual
editable virtual environment at
``.external_sources/venvs/dramatica-flow`` and accurately reports:

* source availability for the inspected metadata/source files
  (``pyproject.toml``, ``README.md``, ``README_EN.md``, ``cli/main.py``,
  ``core/validators/__init__.py``);
* exact package metadata (name, version, ``requires-python``, normalized
  declared dependencies, console script name and target);
* editable venv availability (Python, ``df`` entrypoint, single
  unambiguous ``dramatica_flow-*.dist-info`` directory);
* static AST-based CLI command discovery from ``cli/main.py``;
* analysis-candidate / prose-production command classification lists;
* static model/network and project-mutation surface evidence bounded to
  the audited metadata/source files (no broad full-source scan);
* license claim (README badge/text) versus license file (root ``LICENSE``
  family), with no legal conclusion;
* that the complete runtime is not authorized and is not available as a
  live analysis runtime in T020A, leaving the owner-controlled
  integration-path decision for T020B.

T020A is inspection and preflight only. It does not import or execute
dramatica-flow, does not run the Typer application, does not run the
``df`` entrypoint, does not start any server, does not call any model,
API, or network, and does not perform any subprocess or shell call. The
probe is standard-library only, fail-closed, and read-only. The result
of source or virtual-environment discovery never makes
``dramatica_flow_live_runtime_available`` true.
"""

from __future__ import annotations

import importlib.util
import os
import shutil
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import unquote, urlparse

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

NCP_SOURCE_REL = ".external_sources/narrative-context-protocol"
NCP_PACKAGE_JSON_REL = (
    ".external_sources/narrative-context-protocol/package.json"
)
NCP_SCHEMA_JSON_REL = (
    ".external_sources/narrative-context-protocol/schema/ncp-schema.json"
)
NCP_SCHEMA_YAML_REL = (
    ".external_sources/narrative-context-protocol/schema/ncp-schema.yaml"
)
NCP_VALIDATE_SCHEMA_SCRIPT_REL = (
    ".external_sources/narrative-context-protocol/tests/validate-schema.js"
)
NCP_VALIDATE_FILE_SCRIPT_REL = (
    ".external_sources/narrative-context-protocol/tests/validate-file.js"
)
NCP_NODE_MODULES_REL = (
    ".external_sources/narrative-context-protocol/node_modules"
)
NCP_VALIDATE_SCHEMA_PACKAGE_SCRIPT = "validate:schema"
NCP_VALIDATE_FILE_PACKAGE_SCRIPT = "validate:file"
NCP_AUDIT_CAVEAT = (
    "Known npm audit caveat (recorded, not fixed): "
    "ajv moderate (direct dependency, ReDoS when using $data option); "
    "fast-uri high (transitive dependency, path traversal / host confusion "
    "advisories). NCP source is schema/interchange only and is not exposed "
    "as a network/server path; do not run npm audit fix in preflight."
)

# T018B live NCP candidate-import validation adapter env vars.
# NCP_INPUT_PATH is the explicit owner-selected NCP JSON file path. The
# live adapter is disabled by default and fail-closed when this is unset,
# empty, outside the allowlisted roots, a symlink, a directory, or hidden
# unsafe. NCP_VALIDATE_WITH_NODE is the opt-in for invoking the in-repo
# Node ``validate:file`` subprocess. The opt-in is off by default and is
# only honored against the explicit safe input file; it is never used
# against project data.
NCP_INPUT_PATH_ENV = "OMI_LIVE_NCP_INPUT_PATH"
NCP_VALIDATE_WITH_NODE_ENV = "OMI_LIVE_NCP_VALIDATE_WITH_NODE"

# T019A Subtxt documentation source preflight constants.
# The official local clone SHA is:
#   ec66121364c039693314dcce4cde464e497bece4
SUBTXT_SOURCE_REL = ".external_sources/subtxt-docs"
SUBTXT_README_REL = ".external_sources/subtxt-docs/README.md"
SUBTXT_PACKAGE_JSON_REL = ".external_sources/subtxt-docs/package.json"
SUBTXT_CONTENT_ROOT_REL = ".external_sources/subtxt-docs/content"
SUBTXT_CONTENT_INDEX_REL = ".external_sources/subtxt-docs/content/index.yml"
SUBTXT_KEY_CONCEPTS_REL = (
    ".external_sources/subtxt-docs/content/1.getting-started/5.key-concepts.md"
)
SUBTXT_NARRATIVE_ASPECTS_REL = (
    ".external_sources/subtxt-docs/content/2.narrative-aspects"
)
SUBTXT_STORYPOINTS_REL = (
    ".external_sources/subtxt-docs/content/2.narrative-aspects/5.storypoints.md"
)
SUBTXT_STORYBEATS_REL = (
    ".external_sources/subtxt-docs/content/2.narrative-aspects/6.storybeats.md"
)
SUBTXT_NARRATIVE_INTELLIGENCE_INDEX_REL = (
    ".external_sources/subtxt-docs/content/5.narrative-intelligence/0.index.md"
)
SUBTXT_ADVANCED_CONCEPTS_INDEX_REL = (
    ".external_sources/subtxt-docs/content/6.advanced-concepts/0.index.md"
)
SUBTXT_NARRATIVE_TASKS_INDEX_REL = (
    ".external_sources/subtxt-docs/content/7.narrative-tasks/0.index.md"
)
SUBTXT_API_REFERENCE_INDEX_REL = (
    ".external_sources/subtxt-docs/content/8.API-reference/0.index.md"
)
SUBTXT_COMMAND_ENV = "OMI_LIVE_SUBTXT_COMMAND"
SUBTXT_PATH_ENV = "OMI_LIVE_SUBTXT_PATH"
SUBTXT_CC_LICENSE = (
    "Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International"
)

# T020A dramatica-flow source/runtime preflight constants.
# Source clone path: .external_sources/dramatica-flow
# Source Git HEAD (from prior context refresh):
#   890f099bfcb64adbf407fd83ab708c48e92b0766
# Package name: dramatica-flow; version 0.1.0
# Requires-Python: >=3.11
# Console script: df = cli.main:app
# Editable venv: .external_sources/venvs/dramatica-flow
# Editable direct_url: file:///.../.external_sources/dramatica-flow
# T020A is inspection and preflight only. It does not authorize a live
# adapter and does not make the live runtime available.
DRAMATICA_FLOW_SOURCE_REL = ".external_sources/dramatica-flow"
DRAMATICA_FLOW_VENV_REL = ".external_sources/venvs/dramatica-flow"
DRAMATICA_FLOW_PYPROJECT_REL = (
    ".external_sources/dramatica-flow/pyproject.toml"
)
DRAMATICA_FLOW_README_REL = (
    ".external_sources/dramatica-flow/README.md"
)
DRAMATICA_FLOW_README_EN_REL = (
    ".external_sources/dramatica-flow/README_EN.md"
)
DRAMATICA_FLOW_CLI_REL = (
    ".external_sources/dramatica-flow/cli/main.py"
)
DRAMATICA_FLOW_VALIDATORS_REL = (
    ".external_sources/dramatica-flow/core/validators/__init__.py"
)
DRAMATICA_FLOW_VENV_PYTHON_REL = (
    ".external_sources/venvs/dramatica-flow/bin/python"
)
DRAMATICA_FLOW_VENV_DF_REL = (
    ".external_sources/venvs/dramatica-flow/bin/df"
)
DRAMATICA_FLOW_DISTINFO_GLOB = (
    "dramatica_flow-*.dist-info"
)
DRAMATICA_FLOW_COMMAND_ENV = "OMI_LIVE_DRAMATICA_FLOW_COMMAND"
DRAMATICA_FLOW_PATH_ENV = "OMI_LIVE_DRAMATICA_FLOW_PATH"
DRAMATICA_FLOW_LICENSE_BASENAME_CANDIDATES: tuple[str, ...] = (
    "LICENSE",
    "LICENSE.md",
    "LICENSE.txt",
    "COPYING",
    "COPYING.md",
)
DRAMATICA_FLOW_ANALYSIS_CANDIDATE_COMMANDS: tuple[str, ...] = (
    "audit",
    "status",
)
DRAMATICA_FLOW_PROSE_PRODUCTION_COMMANDS: tuple[str, ...] = (
    "export",
    "revise",
    "write",
)
DRAMATICA_FLOW_RUNTIME_SURFACE_UNAVAILABLE = "unavailable"
DRAMATICA_FLOW_RUNTIME_SURFACE_SOURCE_ONLY = "source_only"
DRAMATICA_FLOW_RUNTIME_SURFACE_INSTALLED_REFERENCE = "installed_reference_surface"
DRAMATICA_FLOW_RUNTIME_SURFACE_DEGRADED = "degraded"
DRAMATICA_FLOW_RUNTIME_SURFACES: frozenset[str] = frozenset(
    {
        DRAMATICA_FLOW_RUNTIME_SURFACE_UNAVAILABLE,
        DRAMATICA_FLOW_RUNTIME_SURFACE_SOURCE_ONLY,
        DRAMATICA_FLOW_RUNTIME_SURFACE_INSTALLED_REFERENCE,
        DRAMATICA_FLOW_RUNTIME_SURFACE_DEGRADED,
    }
)

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


def _safe_read_json(absolute_path: Path) -> dict[str, Any] | None:
    """Read a JSON file into a dict, returning ``None`` on any failure.

    Read-only, fail-closed helper for small JSON metadata files such as
    ``package.json``. Never writes; never raises.
    """
    try:
        if not absolute_path.is_file():
            return None
    except OSError:
        return None
    try:
        with absolute_path.open("rb") as handle:
            data = handle.read()
    except OSError:
        return None
    try:
        import json
    except ImportError:  # pragma: no cover - json is always present
        return None
    try:
        parsed = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        return None
    if not isinstance(parsed, dict):
        return None
    return parsed


def _safe_read_text(absolute_path: Path, max_bytes: int = 65536) -> str | None:
    """Read a small text file into a string, returning ``None`` on failure.

    Read-only, fail-closed helper for small metadata files such as
    ``README.md``. Never writes; never raises.
    """
    try:
        if not absolute_path.is_file():
            return None
    except OSError:
        return None
    try:
        with absolute_path.open("rb") as handle:
            data = handle.read(max_bytes + 1)
        if len(data) > max_bytes:
            return None
        return data.decode("utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def _package_json_script_names(package_json: dict[str, Any]) -> list[str]:
    """Return the list of npm script names declared in a ``package.json`` dict.

    Read-only helper; ignores non-dict ``scripts`` blocks; returns an empty
    list when ``scripts`` is missing or malformed.
    """
    scripts = package_json.get("scripts")
    if not isinstance(scripts, dict):
        return []
    return [str(name) for name in scripts.keys() if isinstance(name, str)]


def _ncp_runtime_probe(env: Mapping[str, str] | None = None) -> dict[str, Any]:
    """Read-only NCP schema-validator surface probe.

    T018A scope: confirm the NCP source tree, ``package.json``, schema JSON,
    schema YAML, the two validator scripts (``validate:schema`` and
    ``validate:file``), the corresponding ``package.json`` script entries,
    ``node``/``npm`` command availability, and the presence of
    ``node_modules`` are all discoverable. Reports a known ``ajv`` moderate /
    ``fast-uri`` high npm audit caveat. The probe never runs ``npm install``,
    ``npm audit fix``, ``npm run validate:schema``, or
    ``npm run validate:file``. The probe does not import NCP as a Python
    module; it is a static, read-only surface inspection.

    T018B addition: the probe ALSO surfaces the explicit
    ``OMI_LIVE_NCP_INPUT_PATH`` and the opt-in
    ``OMI_LIVE_NCP_VALIDATE_WITH_NODE`` env vars as configuration only.
    The probe does not read, parse, validate, or write any NCP file even
    when the input path env var is set. The probe does not invoke Node or
    ``npm`` based on these env vars. The probe is read-only.

    Returns a flat dict of booleans, configured paths, and detail strings
    prefixed with ``ncp_``.
    """
    import json as _json  # local alias to keep the import scoped

    effective_env: Mapping[str, str] = os.environ if env is None else env

    source_root = _REPO_ROOT / NCP_SOURCE_REL
    source_available = source_root.is_dir()
    package_json_path = _REPO_ROOT / NCP_PACKAGE_JSON_REL
    schema_json_path = _REPO_ROOT / NCP_SCHEMA_JSON_REL
    schema_yaml_path = _REPO_ROOT / NCP_SCHEMA_YAML_REL
    validate_schema_script_path = _REPO_ROOT / NCP_VALIDATE_SCHEMA_SCRIPT_REL
    validate_file_script_path = _REPO_ROOT / NCP_VALIDATE_FILE_SCRIPT_REL
    node_modules_path = _REPO_ROOT / NCP_NODE_MODULES_REL

    package_json_available = package_json_path.is_file()
    schema_json_available = schema_json_path.is_file()
    schema_yaml_available = schema_yaml_path.is_file()
    validate_schema_script_available = validate_schema_script_path.is_file()
    validate_file_script_available = validate_file_script_path.is_file()
    node_modules_available = node_modules_path.is_dir()

    package_json_dict = _safe_read_json(package_json_path)
    script_names = _package_json_script_names(package_json_dict) if package_json_dict else []
    validate_schema_package_script_available = (
        NCP_VALIDATE_SCHEMA_PACKAGE_SCRIPT in script_names
    )
    validate_file_package_script_available = (
        NCP_VALIDATE_FILE_PACKAGE_SCRIPT in script_names
    )

    node_path = shutil.which("node")
    npm_path = shutil.which("npm")
    node_available = node_path is not None
    npm_available = npm_path is not None

    missing: list[str] = []
    if not source_available:
        missing.append(NCP_SOURCE_REL)
    if not package_json_available:
        missing.append(NCP_PACKAGE_JSON_REL)
    if not schema_json_available:
        missing.append(NCP_SCHEMA_JSON_REL)
    if not schema_yaml_available:
        missing.append(NCP_SCHEMA_YAML_REL)
    if not validate_schema_script_available:
        missing.append(NCP_VALIDATE_SCHEMA_SCRIPT_REL)
    if not validate_file_script_available:
        missing.append(NCP_VALIDATE_FILE_SCRIPT_REL)
    if not validate_schema_package_script_available:
        missing.append(f"package.json:{NCP_VALIDATE_SCHEMA_PACKAGE_SCRIPT}")
    if not validate_file_package_script_available:
        missing.append(f"package.json:{NCP_VALIDATE_FILE_PACKAGE_SCRIPT}")
    if not node_available:
        missing.append("command:node")
    if not npm_available:
        missing.append("command:npm")

    surface = "available"
    if missing:
        surface = "unavailable"
    elif not node_modules_available:
        surface = "degraded"

    ncp_input_path_value = _env_text(effective_env, NCP_INPUT_PATH_ENV) or ""
    ncp_input_path_configured = bool(ncp_input_path_value.strip())
    ncp_validate_with_node_enabled = _env_bool(
        effective_env, NCP_VALIDATE_WITH_NODE_ENV
    )

    if missing:
        detail = (
            "NCP schema-validator surface probe missing: "
            + ", ".join(missing)
        )
    elif not node_modules_available:
        detail = (
            "NCP schema-validator surface probe: source, package.json, schema "
            "JSON/YAML, validator scripts, validate:schema/validate:file "
            "package scripts, and node/npm all present; node_modules NOT "
            "present (validator scripts would not be runnable in this state; "
            "preflight does not run npm install)"
        )
    else:
        detail = (
            "NCP schema-validator surface probe: source, package.json, schema "
            "JSON/YAML, validator scripts, validate:schema/validate:file "
            "package scripts, node, npm, and node_modules all present; "
            "NCP is schema/interchange validation only, not automatic "
            "analysis runtime, and preflight does not execute "
            "validate:schema or validate:file. T018B live NCP candidate-"
            "import validation adapter is disabled by default and requires "
            "OMI_LIVE_NCP_INPUT_PATH to point at an explicit owner-selected "
            "NCP JSON file; preflight does not auto-scan project data."
        )

    return {
        "ncp_runtime_surface": surface,
        "ncp_source_path": NCP_SOURCE_REL,
        "ncp_source_available": source_available,
        "ncp_package_json_available": package_json_available,
        "ncp_schema_json_available": schema_json_available,
        "ncp_schema_yaml_available": schema_yaml_available,
        "ncp_validate_schema_script_available": validate_schema_script_available,
        "ncp_validate_file_script_available": validate_file_script_available,
        "ncp_validate_schema_package_script_available": (
            validate_schema_package_script_available
        ),
        "ncp_validate_file_package_script_available": (
            validate_file_package_script_available
        ),
        "ncp_node_available": node_available,
        "ncp_node_path": node_path,
        "ncp_npm_available": npm_available,
        "ncp_npm_path": npm_path,
        "ncp_node_modules_available": node_modules_available,
        "ncp_validator_available": (
            not missing
        ),
        "ncp_validator_status": surface,
        "ncp_audit_caveat": NCP_AUDIT_CAVEAT,
        "ncp_input_path_env": NCP_INPUT_PATH_ENV,
        "ncp_input_path_configured": ncp_input_path_configured,
        "ncp_input_path_value": ncp_input_path_value,
        "ncp_validate_with_node_env": NCP_VALIDATE_WITH_NODE_ENV,
        "ncp_validate_with_node_enabled": ncp_validate_with_node_enabled,
        "ncp_detail": detail,
    }


def _subtxt_docs_source_probe(
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Read-only Subtxt documentation source probe.

    T019A scope: inspect the actual local source at
    ``.external_sources/subtxt-docs`` and accurately report whether the
    official Subtxt documentation source is present, whether its core
    documentation surfaces are present, whether its README license
    declaration and package metadata are discoverable, that this repository
    is a documentation/reference surface (not a live Subtxt analysis
    runtime), that no runnable Subtxt classifier, semantic-analysis
    executable, machine schema validator, or local analysis API has been
    established, and that configured command/path env vars are configuration
    evidence only and must not make the runtime available.

    The probe is pure, read-only, fail-closed. It never executes package
    scripts, never runs Node, npm, pnpm, Nuxt, shell commands, subprocesses,
    or network calls, never imports code from ``.external_sources/subtxt-docs``,
    never starts the documentation website, never reads project data, never
    inspects arbitrary configured paths to decide runtime availability, never
    treats a configured command/path as proof that a runtime exists, and
    never mutates the source tree.
    """
    effective_env: Mapping[str, str] = os.environ if env is None else env

    source_root = _REPO_ROOT / SUBTXT_SOURCE_REL
    source_available = source_root.is_dir()

    readme_path = _REPO_ROOT / SUBTXT_README_REL
    package_json_path = _REPO_ROOT / SUBTXT_PACKAGE_JSON_REL
    content_root_path = _REPO_ROOT / SUBTXT_CONTENT_ROOT_REL
    content_index_path = _REPO_ROOT / SUBTXT_CONTENT_INDEX_REL
    key_concepts_path = _REPO_ROOT / SUBTXT_KEY_CONCEPTS_REL
    narrative_aspects_path = _REPO_ROOT / SUBTXT_NARRATIVE_ASPECTS_REL
    storypoints_path = _REPO_ROOT / SUBTXT_STORYPOINTS_REL
    storybeats_path = _REPO_ROOT / SUBTXT_STORYBEATS_REL
    narrative_intelligence_index_path = (
        _REPO_ROOT / SUBTXT_NARRATIVE_INTELLIGENCE_INDEX_REL
    )
    advanced_concepts_index_path = (
        _REPO_ROOT / SUBTXT_ADVANCED_CONCEPTS_INDEX_REL
    )
    narrative_tasks_index_path = _REPO_ROOT / SUBTXT_NARRATIVE_TASKS_INDEX_REL
    api_reference_index_path = _REPO_ROOT / SUBTXT_API_REFERENCE_INDEX_REL

    readme_available = readme_path.is_file()
    package_json_available = package_json_path.is_file()
    content_root_available = content_root_path.is_dir()
    content_index_available = content_index_path.is_file()
    key_concepts_available = key_concepts_path.is_file()
    narrative_aspects_available = narrative_aspects_path.is_dir()
    storypoints_available = storypoints_path.is_file()
    storybeats_available = storybeats_path.is_file()
    narrative_intelligence_available = narrative_intelligence_index_path.is_file()
    advanced_concepts_available = advanced_concepts_index_path.is_file()
    narrative_tasks_available = narrative_tasks_index_path.is_file()
    api_reference_available = api_reference_index_path.is_file()

    package_json_dict = _safe_read_json(package_json_path)
    package_json_parseable = package_json_dict is not None
    package_name = ""
    package_private = False
    package_scripts: list[str] = []
    if package_json_dict is not None:
        pkg_name = package_json_dict.get("name")
        if isinstance(pkg_name, str):
            package_name = pkg_name
        package_private = bool(package_json_dict.get("private"))
        package_scripts = _package_json_script_names(package_json_dict)
    if package_scripts:
        package_scripts = sorted(package_scripts)

    licence_declared = False
    licence_name = ""
    licence_source = ""
    if readme_available:
        readme_text = _safe_read_text(readme_path)
        if readme_text is not None and SUBTXT_CC_LICENSE in readme_text:
            licence_declared = True
            licence_name = "CC BY-NC-SA 4.0"
            licence_source = "README.md"

    core_surfaces_available = (
        content_root_available
        and content_index_available
        and key_concepts_available
        and narrative_aspects_available
    )

    if not source_available:
        runtime_surface = "unavailable"
    elif not core_surfaces_available:
        runtime_surface = "degraded"
    else:
        runtime_surface = "reference_only"

    docs_reference_available = (runtime_surface == "reference_only")

    command_value = _env_text(effective_env, SUBTXT_COMMAND_ENV) or ""
    command_configured = bool(command_value)
    path_value = _env_text(effective_env, SUBTXT_PATH_ENV) or ""
    path_configured = bool(path_value)

    live_runtime_available = False
    live_runtime_status = (
        "reference_only" if docs_reference_available else "unavailable"
    )

    if not source_available:
        detail = (
            f"Subtxt documentation source not found at "
            f"{SUBTXT_SOURCE_REL}. No Subtxt reference surface "
            f"available. T019A does not execute Subtxt. "
            f"A separate owner-controlled integration-path "
            f"decision is required."
        )
    elif runtime_surface == "degraded":
        detail = (
            f"Subtxt documentation source present at "
            f"{SUBTXT_SOURCE_REL} but one or more core documentation "
            f"surfaces are missing or unreadable. "
            f"The local source is a Subtxt documentation/reference "
            f"repository (package name: {package_name}). "
            f"Documentation availability is not live-runtime "
            f"availability. Package scripts are Nuxt docs-site "
            f"operations, not Subtxt analysis. "
            f"T019A does not execute Subtxt. "
            f"A separate owner-controlled integration-path "
            f"decision is required."
        )
    else:
        script_names_str = (
            ", ".join(package_scripts) if package_scripts else "none"
        )
        detail = (
            f"Subtxt documentation source present at "
            f"{SUBTXT_SOURCE_REL}. "
            f"The local source is a Subtxt documentation/reference "
            f"repository (package name: {package_name}, "
            f"private: {str(package_private).lower()}, "
            f"docs-site scripts: {script_names_str}). "
            f"Documentation availability is not live-runtime "
            f"availability. Package scripts are Nuxt docs-site "
            f"operations, not Subtxt analysis. "
            f"T019A does not execute Subtxt. "
            f"A separate owner-controlled integration-path "
            f"decision is required."
        )

    return {
        "subtxt_runtime_surface": runtime_surface,
        "subtxt_source_path": SUBTXT_SOURCE_REL,
        "subtxt_source_available": source_available,
        "subtxt_readme_available": readme_available,
        "subtxt_package_json_available": package_json_available,
        "subtxt_package_json_parseable": package_json_parseable,
        "subtxt_content_root_available": content_root_available,
        "subtxt_content_index_available": content_index_available,
        "subtxt_key_concepts_available": key_concepts_available,
        "subtxt_narrative_aspects_available": narrative_aspects_available,
        "subtxt_storypoints_docs_available": storypoints_available,
        "subtxt_storybeats_docs_available": storybeats_available,
        "subtxt_narrative_intelligence_available": (
            narrative_intelligence_available
        ),
        "subtxt_advanced_concepts_available": advanced_concepts_available,
        "subtxt_narrative_tasks_available": narrative_tasks_available,
        "subtxt_api_reference_available": api_reference_available,
        "subtxt_package_name": package_name,
        "subtxt_package_private": package_private,
        "subtxt_package_scripts": package_scripts,
        "subtxt_license_declared": licence_declared,
        "subtxt_license_name": licence_name,
        "subtxt_license_source": licence_source,
        "subtxt_docs_reference_available": docs_reference_available,
        "subtxt_live_runtime_available": live_runtime_available,
        "subtxt_live_runtime_status": live_runtime_status,
        "subtxt_command_env": SUBTXT_COMMAND_ENV,
        "subtxt_command_configured": command_configured,
        "subtxt_command_value": command_value,
        "subtxt_path_env": SUBTXT_PATH_ENV,
        "subtxt_path_configured": path_configured,
        "subtxt_path_value": path_value,
        "subtxt_detail": detail,
    }


def _safe_normalize_requirement_specs(
    raw_dependencies: Any,
) -> list[str]:
    """Normalize a ``project.dependencies`` TOML list into sorted requirement specs.

    Read-only helper; ignores non-list inputs; strips whitespace; drops empty
    entries; returns an empty list when missing or malformed. Never raises.
    """
    if not isinstance(raw_dependencies, list):
        return []
    cleaned: list[str] = []
    for entry in raw_dependencies:
        if not isinstance(entry, str):
            continue
        text = entry.strip()
        if not text:
            continue
        cleaned.append(text)
    return sorted(set(cleaned))


def _safe_collect_required_dist(metadata_text: str) -> list[str]:
    """Parse the ``Requires-Dist:`` lines of a dist-info ``METADATA`` file.

    Read-only helper; returns the sorted, deduplicated, whitespace-stripped
    requirement specifiers. Never raises.
    """
    if not isinstance(metadata_text, str) or not metadata_text:
        return []
    out: list[str] = []
    for line in metadata_text.splitlines():
        if not line.startswith("Requires-Dist:"):
            continue
        spec = line[len("Requires-Dist:"):].strip()
        if not spec:
            continue
        if ";" in spec:
            head = spec.split(";", 1)[0].strip()
            if not head:
                continue
            spec = head
        if spec.lower() == "setuptools":
            continue
        out.append(spec)
    return sorted(set(out))


def _safe_parse_console_entry_points(entry_points_text: str) -> list[tuple[str, str]]:
    """Parse a dist-info ``entry_points.txt`` into ``(name, target)`` pairs.

    Read-only helper; returns the sorted-by-name console-script pairs found
    under the ``[console_scripts]`` section. Ignores other sections, blank
    lines, and comments. Never raises.
    """
    if not isinstance(entry_points_text, str) or not entry_points_text:
        return []
    pairs: list[tuple[str, str]] = []
    in_console_scripts = False
    for raw_line in entry_points_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            in_console_scripts = line == "[console_scripts]"
            continue
        if not in_console_scripts or "=" not in line:
            continue
        name, _, target = line.partition("=")
        name = name.strip()
        target = target.strip()
        if not name or not target:
            continue
        pairs.append((name, target))
    pairs.sort(key=lambda item: item[0])
    return pairs


def _safe_parse_pyproject_console_scripts(
    project_section: dict[str, Any],
) -> list[tuple[str, str]]:
    """Parse a pyproject ``[project.scripts]`` section into ``(name, target)`` pairs.

    Read-only helper; returns sorted-by-name pairs. Never raises.
    """
    scripts = project_section.get("scripts")
    if not isinstance(scripts, dict):
        return []
    pairs: list[tuple[str, str]] = []
    for name, target in scripts.items():
        if not isinstance(name, str) or not isinstance(target, str):
            continue
        name_clean = name.strip()
        target_clean = target.strip()
        if not name_clean or not target_clean:
            continue
        pairs.append((name_clean, target_clean))
    pairs.sort(key=lambda item: item[0])
    return pairs


def _safe_discover_dramatica_flow_dist_info(
    venv_root: Path,
    distinfo_glob: str,
) -> tuple[list[Path], Path | None]:
    """Discover the unique ``dramatica_flow-*.dist-info`` directory.

    Walks ``<venv>/lib/python*/site-packages/`` without expanding shell
    globs (purely through ``Path.iterdir``) and applies the
    ``distinfo_glob`` pattern. Returns ``(matches, selected)``. When there
    is exactly one unambiguous match, ``selected`` is the unique path.
    When there are zero or multiple matches, ``selected`` is ``None`` and
    the matches list is returned for reporting. Never raises.
    """
    matches: list[Path] = []
    selected: Path | None = None
    try:
        if not venv_root.is_dir():
            return matches, selected
        lib_dir = venv_root / "lib"
        if not lib_dir.is_dir():
            return matches, selected
        for py_dir in lib_dir.iterdir():
            if not py_dir.is_dir():
                continue
            if not py_dir.name.startswith("python"):
                continue
            site_packages = py_dir / "site-packages"
            if not site_packages.is_dir():
                continue
            for entry in site_packages.iterdir():
                if not entry.is_dir():
                    continue
                if _fnmatch(entry.name, distinfo_glob):
                    matches.append(entry)
    except OSError:
        return matches, selected
    matches.sort(key=lambda p: p.as_posix())
    if len(matches) == 1:
        selected = matches[0]
    return matches, selected


def _fnmatch(name: str, pattern: str) -> bool:
    """A minimal ``fnmatch.fnmatch`` substitute for a single ``*`` glob.

    The probe only needs the ``*`` wildcard in
    ``dramatica_flow-*.dist-info``; using ``fnmatch.fnmatch`` directly is
    also acceptable, but the helper keeps the probe standard-library-only
    and deterministic without importing ``fnmatch`` for one pattern.
    """
    if "*" not in pattern:
        return name == pattern
    head, _, tail = pattern.partition("*")
    if not name.startswith(head):
        return False
    if not tail:
        return True
    return name.endswith(tail) and len(name) >= len(head) + len(tail)


def _safe_detect_dramatica_flow_cli_commands(cli_source: str) -> list[str]:
    """Static AST-based Typer CLI command-name detection for dramatica-flow.

    Read-only; parses the ``cli/main.py`` source with ``ast`` only; never
    imports or executes dramatica-flow. Identifies:

    * top-level ``@<typer>.command()`` and ``@<typer>.command("name")``
      decorators on module-level function definitions;
    * sub-typer registered names via
      ``app.add_typer(sub_app, name="<name>")`` calls.

    Returns the sorted, deduplicated union of detected command names. When
    parsing fails or the source is missing, returns an empty list.
    """
    import ast as _ast

    if not isinstance(cli_source, str) or not cli_source:
        return []
    try:
        tree = _ast.parse(cli_source)
    except (SyntaxError, ValueError):
        return []

    detected: set[str] = set()
    typer_vars: set[str] = set()

    for node in tree.body:
        if (
            isinstance(node, _ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], _ast.Name)
            and isinstance(node.value, _ast.Call)
        ):
            target = node.targets[0]
            if _is_typer_call(node.value):
                typer_vars.add(target.id)

    for node in tree.body:
        if isinstance(node, _ast.Expr) and isinstance(node.value, _ast.Call):
            call = node.value
            if (
                isinstance(call.func, _ast.Attribute)
                and call.func.attr == "add_typer"
                and isinstance(call.func.value, _ast.Name)
            ):
                for kw in call.keywords:
                    if kw.arg == "name" and isinstance(kw.value, _ast.Constant):
                        if isinstance(kw.value.value, str):
                            name = kw.value.value.strip()
                            if name:
                                detected.add(name)

    for node in tree.body:
        if not isinstance(node, _ast.FunctionDef):
            continue
        for decorator in node.decorator_list:
            cmd_name = _command_name_from_decorator(decorator, node.name)
            if cmd_name is None:
                continue
            if cmd_name.typer_var is None:
                continue
            if cmd_name.typer_var in typer_vars:
                if cmd_name.command_name:
                    detected.add(cmd_name.command_name)

    return sorted(detected)


class _TyperCommandName:
    __slots__ = ("typer_var", "command_name")

    def __init__(self, typer_var: str | None, command_name: str) -> None:
        self.typer_var = typer_var
        self.command_name = command_name


def _is_typer_call(call: object) -> bool:
    import ast as _ast

    if not isinstance(call, _ast.Call):
        return False
    func = call.func
    if isinstance(func, _ast.Name) and func.id == "Typer":
        return True
    if isinstance(func, _ast.Attribute) and func.attr == "Typer":
        return True
    return False


def _command_name_from_decorator(
    decorator: object,
    function_name: str,
) -> _TyperCommandName | None:
    import ast as _ast

    if not isinstance(decorator, _ast.Call):
        return None
    func = decorator.func
    if not isinstance(func, _ast.Attribute):
        return None
    if func.attr != "command":
        return None
    if not isinstance(func.value, _ast.Name):
        return None
    typer_var = func.value.id
    if decorator.args:
        first = decorator.args[0]
        if isinstance(first, _ast.Constant) and isinstance(first.value, str):
            name = first.value.strip()
            if name:
                return _TyperCommandName(typer_var, name)
    return _TyperCommandName(typer_var, function_name or "")


def _safe_read_dramatica_flow_console_entrypoints(
    dist_info_path: Path,
) -> list[tuple[str, str]]:
    """Read the ``entry_points.txt`` of a single resolved dist-info directory.

    Returns the sorted-by-name ``(name, target)`` console-script pairs, or
    an empty list when the file is missing, unreadable, or malformed.
    """
    entry_points_path = dist_info_path / "entry_points.txt"
    try:
        if not entry_points_path.is_file():
            return []
    except OSError:
        return []
    try:
        with entry_points_path.open("rb") as handle:
            data = handle.read()
    except OSError:
        return []
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return []
    return _safe_parse_console_entry_points(text)


def _safe_read_dramatica_flow_direct_url(
    dist_info_path: Path,
) -> tuple[dict[str, Any] | None, str | None]:
    """Read the ``direct_url.json`` of a single resolved dist-info directory.

    Returns ``(parsed_dict, error_detail)``. ``parsed_dict`` is ``None`` on
    any failure. ``error_detail`` is a short human-readable string when the
    read/parse failed, otherwise ``None``. Never raises.
    """
    direct_url_path = dist_info_path / "direct_url.json"
    import json as _json

    try:
        if not direct_url_path.is_file():
            return None, "direct_url.json missing"
    except OSError:
        return None, "direct_url.json not accessible"
    try:
        with direct_url_path.open("rb") as handle:
            data = handle.read()
    except OSError as exc:
        return None, f"direct_url.json read failed: {type(exc).__name__}"
    try:
        parsed = _json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        return None, f"direct_url.json invalid JSON: {exc}"
    if not isinstance(parsed, dict):
        return None, "direct_url.json is not a JSON object"
    return parsed, None


def _safe_resolve_file_url_path(url: str) -> Path | None:
    """Resolve an editable ``file://`` URL to a local path.

    Returns ``None`` for malformed, non-file, host-qualified, empty, or
    unresolvable URLs. Never raises.
    """
    if not isinstance(url, str) or not url:
        return None
    try:
        parsed = urlparse(url)
    except ValueError:
        return None
    if parsed.scheme != "file":
        return None
    if parsed.netloc not in {"", "localhost"}:
        return None
    path_text = unquote(parsed.path or "")
    if not path_text:
        return None
    try:
        return Path(path_text).resolve()
    except (OSError, RuntimeError, ValueError):
        return None


def _safe_detect_model_or_network_evidence(
    pyproject_text: str | None,
    cli_source_text: str | None,
    validators_source_text: str | None,
) -> bool:
    """Detect static model/network evidence in audited metadata/source files.

    Bounded static indicator check. Looks for known tokens in
    ``pyproject.toml`` dependencies, ``cli/main.py`` text, and
    ``core/validators/__init__.py`` text. Does not perform a broad full-
    source scan.
    """
    indicators = (
        "openai",
        "deepseek",
        "ollama",
        "fastapi",
        "uvicorn",
        "llm",
        "model",
    )
    haystacks: tuple[str | None, ...] = (
        pyproject_text,
        cli_source_text,
        validators_source_text,
    )
    for hay in haystacks:
        if not isinstance(hay, str) or not hay:
            continue
        haystack = hay.lower()
        for token in indicators:
            if token in haystack:
                return True
    return False


def _safe_detect_project_mutation_evidence(
    cli_source_text: str | None,
    validators_source_text: str | None,
    pyproject_text: str | None,
) -> bool:
    """Detect static project-mutation evidence in audited metadata/source files.

    Bounded static indicator check. Looks for known project-mutation
    surface tokens in the audited files. Does not perform a broad full-
    source scan.
    """
    indicators = (
        "init",
        "setup",
        "book",
        "world_state",
        "truth",
        "outline",
        "chapter",
        "story_bible",
        "revise",
        "export",
        "project",
        "state",
    )
    haystacks: tuple[str | None, ...] = (
        cli_source_text,
        validators_source_text,
        pyproject_text,
    )
    for hay in haystacks:
        if not isinstance(hay, str) or not hay:
            continue
        haystack = hay.lower()
        for token in indicators:
            if token in haystack:
                return True
    return False


def _safe_detect_license_claim(
    readme_text: str | None,
    readme_en_text: str | None,
) -> tuple[bool, str, str]:
    """Detect a README-claimed MIT license from the audited README files.

    Returns ``(claimed, name, source)``. ``source`` is a comma-separated
    sorted list of README files that mention the MIT license, or an empty
    string when no claim is found.
    """
    sources: list[str] = []
    if isinstance(readme_text, str) and readme_text:
        if "MIT" in readme_text:
            sources.append("README.md")
    if isinstance(readme_en_text, str) and readme_en_text:
        if "MIT" in readme_en_text:
            sources.append("README_EN.md")
    if sources:
        return True, "MIT", ", ".join(sorted(set(sources)))
    return False, "", ""


def _safe_detect_license_file(source_root: Path) -> bool:
    """Return True if a root-level license file exists and is readable.

    The check is intentionally limited to the configured basename candidates
    and never inspects dependency license files.
    """
    for basename in DRAMATICA_FLOW_LICENSE_BASENAME_CANDIDATES:
        candidate = source_root / basename
        try:
            if not candidate.is_file():
                continue
        except OSError:
            continue
        try:
            with candidate.open("rb"):
                return True
        except OSError:
            continue
    return False


def _dramatica_flow_runtime_probe(
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Read-only dramatica-flow source/runtime preflight.

    T020A scope: inspect the actual local source at
    ``.external_sources/dramatica-flow`` and the actual editable virtual
    environment at ``.external_sources/venvs/dramatica-flow`` and accurately
    report:

    * source availability for the audited metadata/source files;
    * exact package metadata;
    * editable venv availability (Python, ``df`` entrypoint, single
      unambiguous ``dramatica_flow-*.dist-info`` directory);
    * static AST-based CLI command discovery from ``cli/main.py``;
    * analysis-candidate / prose-production command classification lists;
    * static model/network and project-mutation surface evidence bounded
      to the audited metadata/source files;
    * license claim (README badge/text) versus license file (root
      ``LICENSE`` family), with no legal conclusion;
    * that the complete runtime is not authorized and is not available as
      a live analysis runtime in T020A, leaving the owner-controlled
      integration-path decision for T020B.

    The probe is pure, read-only, fail-closed, and standard-library only.
    It never imports or executes dramatica-flow, never runs the Typer
    application, never runs the ``df`` entrypoint, never starts any
    server, never calls any model, API, or network, and never performs
    any subprocess, shell, or package-management call. It never mutates
    the source tree or the editable virtual environment.

    The probe ALWAYS reports ``dramatica_flow_live_runtime_available``
    as ``False`` and ``dramatica_flow_analysis_only_runtime_authorized``
    as ``False``, regardless of what source or installation evidence is
    discovered. The owner-controlled integration-path decision is the
    responsibility of T020B.
    """
    effective_env: Mapping[str, str] = os.environ if env is None else env

    source_root = _REPO_ROOT / DRAMATICA_FLOW_SOURCE_REL
    venv_root = _REPO_ROOT / DRAMATICA_FLOW_VENV_REL
    pyproject_path = _REPO_ROOT / DRAMATICA_FLOW_PYPROJECT_REL
    readme_path = _REPO_ROOT / DRAMATICA_FLOW_README_REL
    readme_en_path = _REPO_ROOT / DRAMATICA_FLOW_README_EN_REL
    cli_path = _REPO_ROOT / DRAMATICA_FLOW_CLI_REL
    validators_path = _REPO_ROOT / DRAMATICA_FLOW_VALIDATORS_REL
    venv_python_path = _REPO_ROOT / DRAMATICA_FLOW_VENV_PYTHON_REL
    venv_df_path = _REPO_ROOT / DRAMATICA_FLOW_VENV_DF_REL

    source_available = source_root.is_dir()
    pyproject_available = pyproject_path.is_file()
    readme_available = readme_path.is_file()
    readme_en_available = readme_en_path.is_file()
    cli_source_available = cli_path.is_file()
    validators_source_available = validators_path.is_file()

    venv_available = venv_root.is_dir()
    venv_python_available = venv_python_path.is_file() or venv_python_path.is_symlink()
    df_entrypoint_available = venv_df_path.is_file() or venv_df_path.is_symlink()

    package_name = ""
    package_version = ""
    requires_python = ""
    declared_dependencies: list[str] = []
    pyproject_console_pairs: list[tuple[str, str]] = []
    pyproject_text: str | None = None
    if pyproject_available:
        pyproject_text = _safe_read_text(pyproject_path)
        if pyproject_text is not None:
            try:
                import tomllib as _tomllib
            except ImportError:  # pragma: no cover - tomllib always present on 3.11+
                _tomllib = None
            if _tomllib is not None:
                try:
                    parsed_pyproject = _tomllib.loads(pyproject_text)
                except (ValueError, TypeError):
                    parsed_pyproject = None
                if isinstance(parsed_pyproject, dict):
                    project = parsed_pyproject.get("project")
                    if isinstance(project, dict):
                        pkg_name = project.get("name")
                        if isinstance(pkg_name, str):
                            package_name = pkg_name
                        pkg_version = project.get("version")
                        if isinstance(pkg_version, str):
                            package_version = pkg_version
                        req_py = project.get("requires-python")
                        if isinstance(req_py, str):
                            requires_python = req_py
                        declared_dependencies = _safe_normalize_requirement_specs(
                            project.get("dependencies")
                        )
                        pyproject_console_pairs = _safe_parse_pyproject_console_scripts(
                            project
                        )

    dist_info_matches: list[Path] = []
    dist_info_selected: Path | None = None
    if venv_available:
        dist_info_matches, dist_info_selected = _safe_discover_dramatica_flow_dist_info(
            venv_root,
            DRAMATICA_FLOW_DISTINFO_GLOB,
        )

    dist_info_available = dist_info_selected is not None
    dist_info_name = dist_info_selected.name if dist_info_selected is not None else ""
    dist_info_count = len(dist_info_matches)

    editable_install = False
    editable_source = ""
    editable_source_matches_expected = False
    direct_url_error: str | None = None
    direct_url_parsed: dict[str, Any] | None = None
    metadata_dependencies: list[str] = []
    metadata_console_pairs: list[tuple[str, str]] = []
    dist_info_console_pairs: list[tuple[str, str]] = []
    package_name_dist = ""
    package_version_dist = ""
    requires_python_dist = ""
    if dist_info_selected is not None:
        parsed, error = _safe_read_dramatica_flow_direct_url(dist_info_selected)
        if parsed is not None:
            direct_url_parsed = parsed
        if error is not None:
            direct_url_error = error
        metadata_path = dist_info_selected / "METADATA"
        try:
            if metadata_path.is_file():
                metadata_text = _safe_read_text(metadata_path)
                if metadata_text is not None:
                    for line in metadata_text.splitlines():
                        if line.startswith("Name:"):
                            value = line[len("Name:"):].strip()
                            if value:
                                package_name_dist = value
                        elif line.startswith("Version:"):
                            value = line[len("Version:"):].strip()
                            if value:
                                package_version_dist = value
                        elif line.startswith("Requires-Python:"):
                            value = line[len("Requires-Python:"):].strip()
                            if value:
                                requires_python_dist = value
                    metadata_dependencies = _safe_collect_required_dist(metadata_text)
        except OSError:
            pass
        dist_info_console_pairs = _safe_read_dramatica_flow_console_entrypoints(
            dist_info_selected
        )
        if direct_url_parsed is not None:
            dir_info = direct_url_parsed.get("dir_info")
            if isinstance(dir_info, dict):
                editable_install = bool(dir_info.get("editable"))
            url = direct_url_parsed.get("url")
            if isinstance(url, str):
                editable_source = url
            elif url is not None:
                editable_source = str(url)
        if (
            isinstance(editable_source, str)
            and editable_source
            and editable_install
            and source_available
        ):
            try:
                editable_source_path = _safe_resolve_file_url_path(editable_source)
                expected_source_path = source_root.resolve()
                if editable_source_path == expected_source_path:
                    editable_source_matches_expected = True
            except OSError:
                editable_source_matches_expected = False

    pyproject_console_name = ""
    pyproject_console_target = ""
    if pyproject_console_pairs:
        pyproject_console_name = pyproject_console_pairs[0][0]
        pyproject_console_target = pyproject_console_pairs[0][1]

    dist_info_console_name = ""
    dist_info_console_target = ""
    if dist_info_console_pairs:
        dist_info_console_name = dist_info_console_pairs[0][0]
        dist_info_console_target = dist_info_console_pairs[0][1]

    resolved_console_name = dist_info_console_name or pyproject_console_name
    resolved_console_target = (
        dist_info_console_target or pyproject_console_target
    )
    package_metadata_consistent = (
        package_name == "dramatica-flow"
        and package_version == "0.1.0"
        and requires_python == ">=3.11"
    )
    pyproject_console_script_consistent = (
        pyproject_console_name == "df"
        and pyproject_console_target == "cli.main:app"
    )
    dist_info_metadata_consistent = (
        dist_info_available
        and package_name_dist == "dramatica-flow"
        and package_version_dist == "0.1.0"
        and requires_python_dist == ">=3.11"
    )
    dist_info_console_script_consistent = (
        dist_info_available
        and dist_info_console_name == "df"
        and dist_info_console_target == "cli.main:app"
    )
    console_script_consistent = (
        resolved_console_name == "df"
        and resolved_console_target == "cli.main:app"
        and pyproject_console_script_consistent
    )

    cli_source_text: str | None = None
    if cli_source_available:
        cli_source_text = _safe_read_text(cli_path)
    validators_source_text: str | None = None
    if validators_source_available:
        validators_source_text = _safe_read_text(validators_path)

    detected_cli_commands = _safe_detect_dramatica_flow_cli_commands(
        cli_source_text or ""
    )

    analysis_candidate_commands = sorted(
        set(DRAMATICA_FLOW_ANALYSIS_CANDIDATE_COMMANDS).intersection(
            detected_cli_commands
        )
    )
    prose_production_commands = sorted(
        set(DRAMATICA_FLOW_PROSE_PRODUCTION_COMMANDS).intersection(
            detected_cli_commands
        )
    )

    model_or_network_detected = _safe_detect_model_or_network_evidence(
        pyproject_text,
        cli_source_text,
        validators_source_text,
    )
    project_mutation_detected = _safe_detect_project_mutation_evidence(
        cli_source_text,
        validators_source_text,
        pyproject_text,
    )

    readme_text: str | None = None
    if readme_available:
        readme_text = _safe_read_text(readme_path)
    readme_en_text: str | None = None
    if readme_en_available:
        readme_en_text = _safe_read_text(readme_en_path)

    license_claimed, license_name, license_source = _safe_detect_license_claim(
        readme_text,
        readme_en_text,
    )
    license_file_available = (
        source_available and _safe_detect_license_file(source_root)
    )
    license_verified = license_claimed and license_file_available

    reference_surface_available = (
        source_available
        and pyproject_available
        and readme_available
        and readme_en_available
        and cli_source_available
        and validators_source_available
        and package_metadata_consistent
        and console_script_consistent
    )
    installation_surface_available = (
        venv_available
        and venv_python_available
        and df_entrypoint_available
        and dist_info_available
        and editable_install
        and editable_source_matches_expected
        and dist_info_metadata_consistent
        and dist_info_console_script_consistent
    )

    if not source_available:
        runtime_surface = DRAMATICA_FLOW_RUNTIME_SURFACE_UNAVAILABLE
    elif not reference_surface_available:
        runtime_surface = DRAMATICA_FLOW_RUNTIME_SURFACE_DEGRADED
    elif installation_surface_available:
        runtime_surface = DRAMATICA_FLOW_RUNTIME_SURFACE_INSTALLED_REFERENCE
    else:
        runtime_surface = DRAMATICA_FLOW_RUNTIME_SURFACE_SOURCE_ONLY

    live_runtime_available = False
    analysis_only_runtime_authorized = False
    integration_decision_required = True

    command_value = _env_text(effective_env, DRAMATICA_FLOW_COMMAND_ENV) or ""
    command_configured = bool(command_value)
    path_value = _env_text(effective_env, DRAMATICA_FLOW_PATH_ENV) or ""
    path_configured = bool(path_value)

    detail_parts: list[str] = []
    if not source_available:
        detail_parts.append(
            f"dramatica-flow source not found at {DRAMATICA_FLOW_SOURCE_REL}."
        )
    else:
        detail_parts.append(
            f"dramatica-flow source present at {DRAMATICA_FLOW_SOURCE_REL} "
            f"(package={package_name or 'unknown'}, "
            f"version={package_version or 'unknown'}, "
            f"requires-python={requires_python or 'unknown'})."
        )
    if installation_surface_available:
        detail_parts.append(
            f"Editable virtual environment present at "
            f"{DRAMATICA_FLOW_VENV_REL} (python, df entrypoint, "
            f"dramatica_flow-*.dist-info)."
        )
    else:
        detail_parts.append(
            f"Editable virtual environment not fully available at "
            f"{DRAMATICA_FLOW_VENV_REL}; runtime_surface="
            f"{runtime_surface}."
        )
    if model_or_network_detected:
        detail_parts.append(
            "Static model/network surface evidence detected in audited "
            "metadata/source files."
        )
    if project_mutation_detected:
        detail_parts.append(
            "Static project-mutation surface evidence detected in audited "
            "metadata/source files."
        )
    if license_claimed:
        detail_parts.append(
            f"License claimed as {license_name} via {license_source}; "
            f"license file available={license_file_available}; "
            f"license verified={license_verified}."
        )
    else:
        detail_parts.append("No README license claim detected.")
    detail_parts.append(
        "T020A is inspection and preflight only; the live adapter is not "
        "authorized; dramatica_flow_live_runtime_available is always False; "
        "the owner-controlled integration-path decision is deferred to T020B."
    )
    detail = " ".join(detail_parts)

    if runtime_surface not in DRAMATICA_FLOW_RUNTIME_SURFACES:
        runtime_surface = DRAMATICA_FLOW_RUNTIME_SURFACE_DEGRADED

    return {
        "dramatica_flow_source_root": DRAMATICA_FLOW_SOURCE_REL,
        "dramatica_flow_source_available": source_available,
        "dramatica_flow_pyproject_available": pyproject_available,
        "dramatica_flow_readme_available": readme_available,
        "dramatica_flow_readme_en_available": readme_en_available,
        "dramatica_flow_cli_source_available": cli_source_available,
        "dramatica_flow_validators_source_available": validators_source_available,
        "dramatica_flow_package_name": package_name,
        "dramatica_flow_package_version": package_version,
        "dramatica_flow_requires_python": requires_python,
        "dramatica_flow_declared_dependencies": declared_dependencies,
        "dramatica_flow_console_script_name": resolved_console_name,
        "dramatica_flow_console_script_target": resolved_console_target,
        "dramatica_flow_package_metadata_consistent": (
            package_metadata_consistent
        ),
        "dramatica_flow_console_script_consistent": console_script_consistent,
        "dramatica_flow_dist_info_metadata_consistent": (
            dist_info_metadata_consistent
        ),
        "dramatica_flow_dist_info_console_script_consistent": (
            dist_info_console_script_consistent
        ),
        "dramatica_flow_pyproject_console_script_name": pyproject_console_name,
        "dramatica_flow_pyproject_console_script_target": pyproject_console_target,
        "dramatica_flow_dist_info_console_script_name": dist_info_console_name,
        "dramatica_flow_dist_info_console_script_target": dist_info_console_target,
        "dramatica_flow_dist_info_name": dist_info_name,
        "dramatica_flow_dist_info_count": dist_info_count,
        "dramatica_flow_dist_info_package_name": package_name_dist,
        "dramatica_flow_dist_info_package_version": package_version_dist,
        "dramatica_flow_dist_info_requires_python": requires_python_dist,
        "dramatica_flow_dist_info_declared_dependencies": metadata_dependencies,
        "dramatica_flow_dist_info_console_pairs": [
            {"name": name, "target": target}
            for name, target in dist_info_console_pairs
        ],
        "dramatica_flow_direct_url_present": direct_url_parsed is not None,
        "dramatica_flow_direct_url_error": direct_url_error or "",
        "dramatica_flow_venv_root": DRAMATICA_FLOW_VENV_REL,
        "dramatica_flow_venv_available": venv_available,
        "dramatica_flow_venv_python_available": venv_python_available,
        "dramatica_flow_df_entrypoint_available": df_entrypoint_available,
        "dramatica_flow_dist_info_available": dist_info_available,
        "dramatica_flow_editable_install": editable_install,
        "dramatica_flow_editable_source": editable_source,
        "dramatica_flow_editable_source_matches_expected": (
            editable_source_matches_expected
        ),
        "dramatica_flow_detected_cli_commands": detected_cli_commands,
        "dramatica_flow_analysis_candidate_commands": analysis_candidate_commands,
        "dramatica_flow_prose_production_commands": prose_production_commands,
        "dramatica_flow_model_or_network_surface_detected": (
            model_or_network_detected
        ),
        "dramatica_flow_project_mutation_surface_detected": (
            project_mutation_detected
        ),
        "dramatica_flow_license_claimed": license_claimed,
        "dramatica_flow_license_name": license_name,
        "dramatica_flow_license_source": license_source,
        "dramatica_flow_license_file_available": license_file_available,
        "dramatica_flow_license_verified": license_verified,
        "dramatica_flow_reference_surface_available": reference_surface_available,
        "dramatica_flow_installation_surface_available": (
            installation_surface_available
        ),
        "dramatica_flow_analysis_only_runtime_authorized": (
            analysis_only_runtime_authorized
        ),
        "dramatica_flow_live_runtime_available": live_runtime_available,
        "dramatica_flow_integration_decision_required": (
            integration_decision_required
        ),
        "dramatica_flow_runtime_surface": runtime_surface,
        "dramatica_flow_command_env": DRAMATICA_FLOW_COMMAND_ENV,
        "dramatica_flow_command_configured": command_configured,
        "dramatica_flow_command_value": command_value,
        "dramatica_flow_path_env": DRAMATICA_FLOW_PATH_ENV,
        "dramatica_flow_path_configured": path_configured,
        "dramatica_flow_path_value": path_value,
        "dramatica_flow_probe_detail": detail,
    }


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


def _booknlp_runtime_probe() -> dict[str, Any]:
    """Read-only BookNLP runtime surface probe.

    Uses safe ``importlib.util.find_spec`` and ``importlib.metadata.version``
    for package and version checks. Imports spaCy only for the model-load
    probe (same pattern as ``_spacy_model_probe``). Does not import heavy
    BookNLP, TensorFlow, or Torch modules. Does not run BookNLP processing.

    Returns a flat dict of boolean/surface/version/compatibility fields
    prefixed with ``booknlp_``.
    """
    import importlib.metadata

    def _safe_version(pkg: str) -> str | None:
        try:
            return importlib.metadata.version(pkg)
        except Exception:
            return None

    result: dict[str, Any] = {
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
        "booknlp_setuptools_compatibility_detail": None,
        "booknlp_detail": "",
    }

    booknlp_spec = importlib.util.find_spec("booknlp")
    result["booknlp_package_available"] = booknlp_spec is not None
    if booknlp_spec is not None:
        result["booknlp_package_version"] = _safe_version("booknlp")
        result["booknlp_module_available"] = (
            importlib.util.find_spec("booknlp.booknlp") is not None
        )
        result["booknlp_entrypoint_available"] = result["booknlp_module_available"]

    spacy_spec = importlib.util.find_spec("spacy")
    result["booknlp_spacy_available"] = spacy_spec is not None
    if spacy_spec is not None:
        result["booknlp_spacy_version"] = _safe_version("spacy")
        try:
            import spacy
            spacy.load(OMI_LIVE_SPACY_MODEL_DEFAULT)
            result["booknlp_spacy_model_available"] = True
        except Exception:
            result["booknlp_spacy_model_available"] = False

    tf_spec = importlib.util.find_spec("tensorflow")
    result["booknlp_tensorflow_available"] = tf_spec is not None
    if tf_spec is not None:
        result["booknlp_tensorflow_version"] = _safe_version("tensorflow")

    torch_spec = importlib.util.find_spec("torch")
    result["booknlp_torch_available"] = torch_spec is not None
    if torch_spec is not None:
        result["booknlp_torch_version"] = _safe_version("torch")

    transformers_spec = importlib.util.find_spec("transformers")
    result["booknlp_transformers_available"] = transformers_spec is not None
    if transformers_spec is not None:
        result["booknlp_transformers_version"] = _safe_version("transformers")

    st_spec = importlib.util.find_spec("setuptools")
    result["booknlp_setuptools_available"] = st_spec is not None
    if st_spec is not None:
        result["booknlp_setuptools_version"] = _safe_version("setuptools")

    pr_spec = importlib.util.find_spec("pkg_resources")
    result["booknlp_pkg_resources_available"] = pr_spec is not None

    st_ver = result["booknlp_setuptools_version"]
    pr_avail = result["booknlp_pkg_resources_available"]
    if st_ver and pr_avail:
        result["booknlp_setuptools_compatibility_detail"] = (
            f"setuptools=={st_ver}, pkg_resources available: "
            f"compatible with BookNLP import"
        )
    elif st_ver and not pr_avail:
        result["booknlp_setuptools_compatibility_detail"] = (
            f"setuptools=={st_ver}, pkg_resources NOT available: "
            f"BookNLP needs pkg_resources; pin setuptools<81"
        )
    elif not st_ver:
        result["booknlp_setuptools_compatibility_detail"] = (
            "setuptools not available: BookNLP needs pkg_resources"
        )
    else:
        result["booknlp_setuptools_compatibility_detail"] = (
            "setuptools/pkg_resources status unknown"
        )

    detail_parts: list[str] = []
    if result["booknlp_package_available"]:
        ver = result["booknlp_package_version"] or ""
        detail_parts.append(f"BookNLP package {ver} available")
        if result["booknlp_entrypoint_available"]:
            detail_parts.append("booknlp.booknlp entrypoint available")
        else:
            detail_parts.append("booknlp.booknlp entrypoint NOT available")
    else:
        detail_parts.append("BookNLP package NOT available")

    detail_parts.append(
        f"spaCy: "
        f"{'available' if result['booknlp_spacy_available'] else 'NOT available'}"
    )
    if result["booknlp_spacy_available"]:
        detail_parts.append(
            f"en_core_web_sm: "
            f"{'available' if result['booknlp_spacy_model_available'] else 'NOT available'}"
        )

    detail_parts.append(
        f"tensorflow: "
        f"{'available' if result['booknlp_tensorflow_available'] else 'NOT available'}"
    )
    detail_parts.append(
        f"torch: "
        f"{'available' if result['booknlp_torch_available'] else 'NOT available'}"
    )
    detail_parts.append(
        f"transformers: "
        f"{'available' if result['booknlp_transformers_available'] else 'NOT available'}"
    )

    if pr_avail:
        detail_parts.append("pkg_resources available")
    else:
        detail_parts.append("pkg_resources NOT available (pin setuptools<81)")

    torch_ver_str = result["booknlp_torch_version"]
    if torch_ver_str:
        try:
            parts = torch_ver_str.replace("+", ".").split(".")
            if len(parts) >= 2:
                major, minor = int(parts[0]), int(parts[1])
                if major < 2 or (major == 2 and minor < 11):
                    detail_parts.append(
                        f"torch={torch_ver_str} < 2.11 (cpp extensions skipped, "
                        f"non-blocking for import)"
                    )
        except (ValueError, IndexError):
            pass

    result["booknlp_detail"] = "; ".join(detail_parts)

    if result["booknlp_package_available"] and result["booknlp_entrypoint_available"]:
        result["booknlp_runtime_surface"] = "available"
    elif not result["booknlp_package_available"]:
        result["booknlp_runtime_surface"] = "unavailable"
    else:
        result["booknlp_runtime_surface"] = "degraded"

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
        probe = _booknlp_runtime_probe()
        configured = True
        available = (
            probe["booknlp_package_available"]
            and probe["booknlp_entrypoint_available"]
        )
        detail = probe["booknlp_detail"]
        dependency_status = "available" if available else "unavailable"
        return {
            "runtime_configured": configured,
            "runtime_dependency_available": available,
            "runtime_dependency_status": dependency_status,
            "probe_detail": detail,
            "booknlp_runtime_surface": probe["booknlp_runtime_surface"],
            "booknlp_package_available": probe["booknlp_package_available"],
            "booknlp_package_version": probe["booknlp_package_version"],
            "booknlp_module_available": probe["booknlp_module_available"],
            "booknlp_entrypoint_available": probe["booknlp_entrypoint_available"],
            "booknlp_spacy_available": probe["booknlp_spacy_available"],
            "booknlp_spacy_version": probe["booknlp_spacy_version"],
            "booknlp_spacy_model_available": probe["booknlp_spacy_model_available"],
            "booknlp_tensorflow_available": probe["booknlp_tensorflow_available"],
            "booknlp_tensorflow_version": probe["booknlp_tensorflow_version"],
            "booknlp_torch_available": probe["booknlp_torch_available"],
            "booknlp_torch_version": probe["booknlp_torch_version"],
            "booknlp_transformers_available": probe["booknlp_transformers_available"],
            "booknlp_transformers_version": probe["booknlp_transformers_version"],
            "booknlp_setuptools_available": probe["booknlp_setuptools_available"],
            "booknlp_setuptools_version": probe["booknlp_setuptools_version"],
            "booknlp_pkg_resources_available": probe["booknlp_pkg_resources_available"],
            "booknlp_setuptools_compatibility_detail": probe[
                "booknlp_setuptools_compatibility_detail"
            ],
            "booknlp_detail": probe["booknlp_detail"],
        }
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
        probe = _ncp_runtime_probe(env)
        configured = probe["ncp_source_available"]
        available = probe["ncp_validator_available"]
        detail = probe["ncp_detail"]
        return {
            "runtime_configured": configured,
            "runtime_dependency_available": available,
            "runtime_dependency_status": (
                "available" if available else "unavailable"
            ),
            "probe_detail": detail,
            "ncp_runtime_surface": probe["ncp_runtime_surface"],
            "ncp_source_path": probe["ncp_source_path"],
            "ncp_source_available": probe["ncp_source_available"],
            "ncp_package_json_available": probe["ncp_package_json_available"],
            "ncp_schema_json_available": probe["ncp_schema_json_available"],
            "ncp_schema_yaml_available": probe["ncp_schema_yaml_available"],
            "ncp_validate_schema_script_available": probe[
                "ncp_validate_schema_script_available"
            ],
            "ncp_validate_file_script_available": probe[
                "ncp_validate_file_script_available"
            ],
            "ncp_validate_schema_package_script_available": probe[
                "ncp_validate_schema_package_script_available"
            ],
            "ncp_validate_file_package_script_available": probe[
                "ncp_validate_file_package_script_available"
            ],
            "ncp_node_available": probe["ncp_node_available"],
            "ncp_node_path": probe["ncp_node_path"],
            "ncp_npm_available": probe["ncp_npm_available"],
            "ncp_npm_path": probe["ncp_npm_path"],
            "ncp_node_modules_available": probe["ncp_node_modules_available"],
            "ncp_validator_available": probe["ncp_validator_available"],
            "ncp_validator_status": probe["ncp_validator_status"],
            "ncp_audit_caveat": probe["ncp_audit_caveat"],
            "ncp_input_path_env": probe["ncp_input_path_env"],
            "ncp_input_path_configured": probe["ncp_input_path_configured"],
            "ncp_input_path_value": probe["ncp_input_path_value"],
            "ncp_validate_with_node_env": probe["ncp_validate_with_node_env"],
            "ncp_validate_with_node_enabled": probe[
                "ncp_validate_with_node_enabled"
            ],
            "ncp_detail": detail,
        }
    elif adapter == "subtxt":
        probe = _subtxt_docs_source_probe(env)
        configured = probe["subtxt_source_available"]
        available = False
        surface = probe["subtxt_runtime_surface"]
        if surface == "unavailable":
            dependency_status = "unavailable"
        elif surface == "degraded":
            dependency_status = "unavailable"
        else:
            dependency_status = "available"
        detail = probe["subtxt_detail"]
        return {
            "runtime_configured": configured,
            "runtime_dependency_available": available,
            "runtime_dependency_status": dependency_status,
            "probe_detail": detail,
            "subtxt_runtime_surface": probe["subtxt_runtime_surface"],
            "subtxt_source_path": probe["subtxt_source_path"],
            "subtxt_source_available": probe["subtxt_source_available"],
            "subtxt_readme_available": probe["subtxt_readme_available"],
            "subtxt_package_json_available": probe[
                "subtxt_package_json_available"
            ],
            "subtxt_package_json_parseable": probe[
                "subtxt_package_json_parseable"
            ],
            "subtxt_content_root_available": probe[
                "subtxt_content_root_available"
            ],
            "subtxt_content_index_available": probe[
                "subtxt_content_index_available"
            ],
            "subtxt_key_concepts_available": probe[
                "subtxt_key_concepts_available"
            ],
            "subtxt_narrative_aspects_available": probe[
                "subtxt_narrative_aspects_available"
            ],
            "subtxt_storypoints_docs_available": probe[
                "subtxt_storypoints_docs_available"
            ],
            "subtxt_storybeats_docs_available": probe[
                "subtxt_storybeats_docs_available"
            ],
            "subtxt_narrative_intelligence_available": probe[
                "subtxt_narrative_intelligence_available"
            ],
            "subtxt_advanced_concepts_available": probe[
                "subtxt_advanced_concepts_available"
            ],
            "subtxt_narrative_tasks_available": probe[
                "subtxt_narrative_tasks_available"
            ],
            "subtxt_api_reference_available": probe[
                "subtxt_api_reference_available"
            ],
            "subtxt_package_name": probe["subtxt_package_name"],
            "subtxt_package_private": probe["subtxt_package_private"],
            "subtxt_package_scripts": probe["subtxt_package_scripts"],
            "subtxt_license_declared": probe["subtxt_license_declared"],
            "subtxt_license_name": probe["subtxt_license_name"],
            "subtxt_license_source": probe["subtxt_license_source"],
            "subtxt_docs_reference_available": probe[
                "subtxt_docs_reference_available"
            ],
            "subtxt_live_runtime_available": probe[
                "subtxt_live_runtime_available"
            ],
            "subtxt_live_runtime_status": probe["subtxt_live_runtime_status"],
            "subtxt_command_env": probe["subtxt_command_env"],
            "subtxt_command_configured": probe["subtxt_command_configured"],
            "subtxt_command_value": probe["subtxt_command_value"],
            "subtxt_path_env": probe["subtxt_path_env"],
            "subtxt_path_configured": probe["subtxt_path_configured"],
            "subtxt_path_value": probe["subtxt_path_value"],
            "subtxt_detail": detail,
        }
    elif adapter == "dramatica_flow":
        probe = _dramatica_flow_runtime_probe(env)
        reference_available = probe["dramatica_flow_reference_surface_available"]
        installation_available = probe["dramatica_flow_installation_surface_available"]
        configured = bool(reference_available or installation_available)
        available = False
        dependency_status = "unavailable"
        detail = probe["dramatica_flow_probe_detail"]
        return {
            "runtime_configured": configured,
            "runtime_dependency_available": available,
            "runtime_dependency_status": dependency_status,
            "probe_detail": detail,
            "dramatica_flow_source_root": probe["dramatica_flow_source_root"],
            "dramatica_flow_source_available": probe[
                "dramatica_flow_source_available"
            ],
            "dramatica_flow_pyproject_available": probe[
                "dramatica_flow_pyproject_available"
            ],
            "dramatica_flow_readme_available": probe[
                "dramatica_flow_readme_available"
            ],
            "dramatica_flow_readme_en_available": probe[
                "dramatica_flow_readme_en_available"
            ],
            "dramatica_flow_cli_source_available": probe[
                "dramatica_flow_cli_source_available"
            ],
            "dramatica_flow_validators_source_available": probe[
                "dramatica_flow_validators_source_available"
            ],
            "dramatica_flow_package_name": probe["dramatica_flow_package_name"],
            "dramatica_flow_package_version": probe[
                "dramatica_flow_package_version"
            ],
            "dramatica_flow_requires_python": probe[
                "dramatica_flow_requires_python"
            ],
            "dramatica_flow_declared_dependencies": probe[
                "dramatica_flow_declared_dependencies"
            ],
            "dramatica_flow_console_script_name": probe[
                "dramatica_flow_console_script_name"
            ],
            "dramatica_flow_console_script_target": probe[
                "dramatica_flow_console_script_target"
            ],
            "dramatica_flow_package_metadata_consistent": probe[
                "dramatica_flow_package_metadata_consistent"
            ],
            "dramatica_flow_console_script_consistent": probe[
                "dramatica_flow_console_script_consistent"
            ],
            "dramatica_flow_dist_info_metadata_consistent": probe[
                "dramatica_flow_dist_info_metadata_consistent"
            ],
            "dramatica_flow_dist_info_console_script_consistent": probe[
                "dramatica_flow_dist_info_console_script_consistent"
            ],
            "dramatica_flow_pyproject_console_script_name": probe[
                "dramatica_flow_pyproject_console_script_name"
            ],
            "dramatica_flow_pyproject_console_script_target": probe[
                "dramatica_flow_pyproject_console_script_target"
            ],
            "dramatica_flow_dist_info_console_script_name": probe[
                "dramatica_flow_dist_info_console_script_name"
            ],
            "dramatica_flow_dist_info_console_script_target": probe[
                "dramatica_flow_dist_info_console_script_target"
            ],
            "dramatica_flow_dist_info_name": probe["dramatica_flow_dist_info_name"],
            "dramatica_flow_dist_info_count": probe["dramatica_flow_dist_info_count"],
            "dramatica_flow_dist_info_package_name": probe[
                "dramatica_flow_dist_info_package_name"
            ],
            "dramatica_flow_dist_info_package_version": probe[
                "dramatica_flow_dist_info_package_version"
            ],
            "dramatica_flow_dist_info_requires_python": probe[
                "dramatica_flow_dist_info_requires_python"
            ],
            "dramatica_flow_dist_info_declared_dependencies": probe[
                "dramatica_flow_dist_info_declared_dependencies"
            ],
            "dramatica_flow_direct_url_present": probe[
                "dramatica_flow_direct_url_present"
            ],
            "dramatica_flow_direct_url_error": probe[
                "dramatica_flow_direct_url_error"
            ],
            "dramatica_flow_venv_root": probe["dramatica_flow_venv_root"],
            "dramatica_flow_venv_available": probe["dramatica_flow_venv_available"],
            "dramatica_flow_venv_python_available": probe[
                "dramatica_flow_venv_python_available"
            ],
            "dramatica_flow_df_entrypoint_available": probe[
                "dramatica_flow_df_entrypoint_available"
            ],
            "dramatica_flow_dist_info_available": probe[
                "dramatica_flow_dist_info_available"
            ],
            "dramatica_flow_editable_install": probe[
                "dramatica_flow_editable_install"
            ],
            "dramatica_flow_editable_source": probe["dramatica_flow_editable_source"],
            "dramatica_flow_editable_source_matches_expected": probe[
                "dramatica_flow_editable_source_matches_expected"
            ],
            "dramatica_flow_detected_cli_commands": probe[
                "dramatica_flow_detected_cli_commands"
            ],
            "dramatica_flow_analysis_candidate_commands": probe[
                "dramatica_flow_analysis_candidate_commands"
            ],
            "dramatica_flow_prose_production_commands": probe[
                "dramatica_flow_prose_production_commands"
            ],
            "dramatica_flow_model_or_network_surface_detected": probe[
                "dramatica_flow_model_or_network_surface_detected"
            ],
            "dramatica_flow_project_mutation_surface_detected": probe[
                "dramatica_flow_project_mutation_surface_detected"
            ],
            "dramatica_flow_license_claimed": probe[
                "dramatica_flow_license_claimed"
            ],
            "dramatica_flow_license_name": probe["dramatica_flow_license_name"],
            "dramatica_flow_license_source": probe["dramatica_flow_license_source"],
            "dramatica_flow_license_file_available": probe[
                "dramatica_flow_license_file_available"
            ],
            "dramatica_flow_license_verified": probe[
                "dramatica_flow_license_verified"
            ],
            "dramatica_flow_reference_surface_available": probe[
                "dramatica_flow_reference_surface_available"
            ],
            "dramatica_flow_installation_surface_available": probe[
                "dramatica_flow_installation_surface_available"
            ],
            "dramatica_flow_analysis_only_runtime_authorized": probe[
                "dramatica_flow_analysis_only_runtime_authorized"
            ],
            "dramatica_flow_live_runtime_available": probe[
                "dramatica_flow_live_runtime_available"
            ],
            "dramatica_flow_integration_decision_required": probe[
                "dramatica_flow_integration_decision_required"
            ],
            "dramatica_flow_runtime_surface": probe["dramatica_flow_runtime_surface"],
            "dramatica_flow_command_env": probe["dramatica_flow_command_env"],
            "dramatica_flow_command_configured": probe[
                "dramatica_flow_command_configured"
            ],
            "dramatica_flow_command_value": probe["dramatica_flow_command_value"],
            "dramatica_flow_path_env": probe["dramatica_flow_path_env"],
            "dramatica_flow_path_configured": probe[
                "dramatica_flow_path_configured"
            ],
            "dramatica_flow_path_value": probe["dramatica_flow_path_value"],
            "dramatica_flow_detail": detail,
        }
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
    if adapter == "booknlp":
        report["booknlp_runtime_surface"] = dependency.get(
            "booknlp_runtime_surface"
        )
        report["booknlp_package_available"] = dependency.get(
            "booknlp_package_available"
        )
        report["booknlp_package_version"] = dependency.get(
            "booknlp_package_version"
        )
        report["booknlp_module_available"] = dependency.get(
            "booknlp_module_available"
        )
        report["booknlp_entrypoint_available"] = dependency.get(
            "booknlp_entrypoint_available"
        )
        report["booknlp_spacy_available"] = dependency.get(
            "booknlp_spacy_available"
        )
        report["booknlp_spacy_version"] = dependency.get(
            "booknlp_spacy_version"
        )
        report["booknlp_spacy_model_available"] = dependency.get(
            "booknlp_spacy_model_available"
        )
        report["booknlp_tensorflow_available"] = dependency.get(
            "booknlp_tensorflow_available"
        )
        report["booknlp_tensorflow_version"] = dependency.get(
            "booknlp_tensorflow_version"
        )
        report["booknlp_torch_available"] = dependency.get(
            "booknlp_torch_available"
        )
        report["booknlp_torch_version"] = dependency.get(
            "booknlp_torch_version"
        )
        report["booknlp_transformers_available"] = dependency.get(
            "booknlp_transformers_available"
        )
        report["booknlp_transformers_version"] = dependency.get(
            "booknlp_transformers_version"
        )
        report["booknlp_setuptools_available"] = dependency.get(
            "booknlp_setuptools_available"
        )
        report["booknlp_setuptools_version"] = dependency.get(
            "booknlp_setuptools_version"
        )
        report["booknlp_pkg_resources_available"] = dependency.get(
            "booknlp_pkg_resources_available"
        )
        report["booknlp_setuptools_compatibility_detail"] = dependency.get(
            "booknlp_setuptools_compatibility_detail"
        )
        report["booknlp_detail"] = dependency.get("booknlp_detail")
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
    if adapter == "ncp":
        report["ncp_runtime_surface"] = dependency.get("ncp_runtime_surface")
        report["ncp_source_path"] = dependency.get("ncp_source_path")
        report["ncp_source_available"] = dependency.get("ncp_source_available")
        report["ncp_package_json_available"] = dependency.get(
            "ncp_package_json_available"
        )
        report["ncp_schema_json_available"] = dependency.get(
            "ncp_schema_json_available"
        )
        report["ncp_schema_yaml_available"] = dependency.get(
            "ncp_schema_yaml_available"
        )
        report["ncp_validate_schema_script_available"] = dependency.get(
            "ncp_validate_schema_script_available"
        )
        report["ncp_validate_file_script_available"] = dependency.get(
            "ncp_validate_file_script_available"
        )
        report["ncp_validate_schema_package_script_available"] = dependency.get(
            "ncp_validate_schema_package_script_available"
        )
        report["ncp_validate_file_package_script_available"] = dependency.get(
            "ncp_validate_file_package_script_available"
        )
        report["ncp_node_available"] = dependency.get("ncp_node_available")
        report["ncp_node_path"] = dependency.get("ncp_node_path")
        report["ncp_npm_available"] = dependency.get("ncp_npm_available")
        report["ncp_npm_path"] = dependency.get("ncp_npm_path")
        report["ncp_node_modules_available"] = dependency.get(
            "ncp_node_modules_available"
        )
        report["ncp_validator_available"] = dependency.get(
            "ncp_validator_available"
        )
        report["ncp_validator_status"] = dependency.get("ncp_validator_status")
        report["ncp_audit_caveat"] = dependency.get("ncp_audit_caveat")
        report["ncp_input_path_env"] = dependency.get("ncp_input_path_env")
        report["ncp_input_path_configured"] = dependency.get(
            "ncp_input_path_configured"
        )
        report["ncp_input_path_value"] = dependency.get("ncp_input_path_value")
        report["ncp_validate_with_node_env"] = dependency.get(
            "ncp_validate_with_node_env"
        )
        report["ncp_validate_with_node_enabled"] = dependency.get(
            "ncp_validate_with_node_enabled"
        )
        report["ncp_detail"] = dependency.get("ncp_detail")
    if adapter == "subtxt":
        report["subtxt_runtime_surface"] = dependency.get(
            "subtxt_runtime_surface"
        )
        report["subtxt_source_path"] = dependency.get("subtxt_source_path")
        report["subtxt_source_available"] = dependency.get(
            "subtxt_source_available"
        )
        report["subtxt_readme_available"] = dependency.get(
            "subtxt_readme_available"
        )
        report["subtxt_package_json_available"] = dependency.get(
            "subtxt_package_json_available"
        )
        report["subtxt_package_json_parseable"] = dependency.get(
            "subtxt_package_json_parseable"
        )
        report["subtxt_content_root_available"] = dependency.get(
            "subtxt_content_root_available"
        )
        report["subtxt_content_index_available"] = dependency.get(
            "subtxt_content_index_available"
        )
        report["subtxt_key_concepts_available"] = dependency.get(
            "subtxt_key_concepts_available"
        )
        report["subtxt_narrative_aspects_available"] = dependency.get(
            "subtxt_narrative_aspects_available"
        )
        report["subtxt_storypoints_docs_available"] = dependency.get(
            "subtxt_storypoints_docs_available"
        )
        report["subtxt_storybeats_docs_available"] = dependency.get(
            "subtxt_storybeats_docs_available"
        )
        report["subtxt_narrative_intelligence_available"] = dependency.get(
            "subtxt_narrative_intelligence_available"
        )
        report["subtxt_advanced_concepts_available"] = dependency.get(
            "subtxt_advanced_concepts_available"
        )
        report["subtxt_narrative_tasks_available"] = dependency.get(
            "subtxt_narrative_tasks_available"
        )
        report["subtxt_api_reference_available"] = dependency.get(
            "subtxt_api_reference_available"
        )
        report["subtxt_package_name"] = dependency.get("subtxt_package_name")
        report["subtxt_package_private"] = dependency.get(
            "subtxt_package_private"
        )
        report["subtxt_package_scripts"] = dependency.get(
            "subtxt_package_scripts"
        )
        report["subtxt_license_declared"] = dependency.get(
            "subtxt_license_declared"
        )
        report["subtxt_license_name"] = dependency.get("subtxt_license_name")
        report["subtxt_license_source"] = dependency.get(
            "subtxt_license_source"
        )
        report["subtxt_docs_reference_available"] = dependency.get(
            "subtxt_docs_reference_available"
        )
        report["subtxt_live_runtime_available"] = dependency.get(
            "subtxt_live_runtime_available"
        )
        report["subtxt_live_runtime_status"] = dependency.get(
            "subtxt_live_runtime_status"
        )
        report["subtxt_command_env"] = dependency.get("subtxt_command_env")
        report["subtxt_command_configured"] = dependency.get(
            "subtxt_command_configured"
        )
        report["subtxt_command_value"] = dependency.get(
            "subtxt_command_value"
        )
        report["subtxt_path_env"] = dependency.get("subtxt_path_env")
        report["subtxt_path_configured"] = dependency.get(
            "subtxt_path_configured"
        )
        report["subtxt_path_value"] = dependency.get("subtxt_path_value")
        report["subtxt_detail"] = dependency.get("subtxt_detail")
    if adapter == "dramatica_flow":
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
            "dramatica_flow_pyproject_console_script_name",
            "dramatica_flow_pyproject_console_script_target",
            "dramatica_flow_dist_info_console_script_name",
            "dramatica_flow_dist_info_console_script_target",
            "dramatica_flow_dist_info_name",
            "dramatica_flow_dist_info_count",
            "dramatica_flow_dist_info_package_name",
            "dramatica_flow_dist_info_package_version",
            "dramatica_flow_dist_info_requires_python",
            "dramatica_flow_dist_info_declared_dependencies",
            "dramatica_flow_direct_url_present",
            "dramatica_flow_direct_url_error",
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
            "dramatica_flow_command_configured",
            "dramatica_flow_command_value",
            "dramatica_flow_path_env",
            "dramatica_flow_path_configured",
            "dramatica_flow_path_value",
            "dramatica_flow_probe_detail",
        ):
            report[key] = dependency.get(key)
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
