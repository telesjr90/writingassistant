"""Deterministic readiness contract for optional project context resources.

This module only inspects the project-local Bible and storyform inputs and
derives storyform prompt-context readiness.  It never creates, repairs, or
persists resources and never invokes an analysis runtime or model.
"""

from __future__ import annotations

import json
import stat
from pathlib import Path
from typing import Any

from jsonschema.exceptions import ValidationError

try:
    from . import project_manager
    from .storyform import Storyform
except ImportError:  # pragma: no cover - supports direct module execution
    import project_manager
    from storyform import Storyform


SCHEMA_VERSION = "project_context_readiness.v1"
STATE_VOCABULARY = (
    "absent",
    "invalid",
    "not_applicable",
    "ready",
    "unavailable",
)
RESOURCE_ORDER = ("bible", "storyform", "storyform_context")


def _resource_result(
    resource_id: str,
    resource_type: str,
    *,
    exists: bool,
    structurally_valid: bool,
    ready: bool,
    state: str,
    reason_code: str | None,
    diagnostics: list[str],
    source_locator: str,
) -> dict[str, Any]:
    if state not in STATE_VOCABULARY:  # pragma: no cover - internal invariant
        raise ValueError(f"Unsupported context readiness state: {state}")
    return {
        "resource_id": resource_id,
        "resource_type": resource_type,
        "exists": exists,
        "structurally_valid": structurally_valid,
        "ready": ready,
        "state": state,
        "reason_code": reason_code,
        "diagnostics": diagnostics[:3],
        "source_locator": source_locator,
    }


def _resolve_project_directory(project_id: str, projects_dir: Path) -> Path:
    project_manager.validate_project_id(project_id)
    project_path = project_manager._project_path_for_id(project_id, projects_dir)
    if not project_path.exists():
        raise FileNotFoundError("Project not found")
    if not project_path.is_dir():
        raise ValueError("Project path is not a directory")
    return project_path


def _resource_path(project_path: Path, filename: str) -> Path:
    path = project_path / filename
    if path.is_symlink():
        raise ValueError("Unsafe resource locator")
    try:
        path.resolve().relative_to(project_path.resolve())
    except (OSError, ValueError) as exc:
        raise ValueError("Unsafe resource locator") from exc
    return path


def _load_optional_json_object(path: Path) -> tuple[str, dict[str, Any] | None]:
    try:
        mode = path.stat().st_mode
    except FileNotFoundError:
        return "absent", None
    if not stat.S_ISREG(mode):
        return "unsupported_structure", None
    try:
        with path.open(encoding="utf-8") as handle:
            value = json.load(handle)
    except FileNotFoundError:
        return "absent", None
    except UnicodeError:
        return "unsupported_encoding", None
    except json.JSONDecodeError:
        return "malformed_json", None
    if not isinstance(value, dict):
        return "unsupported_structure", None
    return "loaded", value


def _assess_bible(project_path: Path) -> dict[str, Any]:
    locator = "bible.json"
    load_state, _data = _load_optional_json_object(
        _resource_path(project_path, locator)
    )
    if load_state == "absent":
        return _resource_result(
            "bible",
            "project_json",
            exists=False,
            structurally_valid=False,
            ready=False,
            state="absent",
            reason_code="bible_absent",
            diagnostics=["Optional Bible resource is not present."],
            source_locator=locator,
        )
    if load_state != "loaded":
        reason = {
            "malformed_json": "bible_malformed_json",
            "unsupported_encoding": "bible_unsupported_encoding",
            "unsupported_structure": "bible_unsupported_structure",
        }[load_state]
        diagnostic = {
            "malformed_json": "Bible resource is not valid JSON.",
            "unsupported_encoding": "Bible resource is not readable as UTF-8 JSON.",
            "unsupported_structure": "Bible resource must be a regular JSON object file.",
        }[load_state]
        return _resource_result(
            "bible",
            "project_json",
            exists=True,
            structurally_valid=False,
            ready=False,
            state="invalid",
            reason_code=reason,
            diagnostics=[diagnostic],
            source_locator=locator,
        )
    return _resource_result(
        "bible",
        "project_json",
        exists=True,
        structurally_valid=True,
        ready=True,
        state="ready",
        reason_code=None,
        diagnostics=[],
        source_locator=locator,
    )


def _assess_storyform(
    project_path: Path,
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    locator = "storyform.json"
    load_state, data = _load_optional_json_object(
        _resource_path(project_path, locator)
    )
    if load_state == "absent":
        return (
            _resource_result(
                "storyform",
                "project_json",
                exists=False,
                structurally_valid=False,
                ready=False,
                state="absent",
                reason_code="storyform_absent",
                diagnostics=["Optional storyform resource is not present."],
                source_locator=locator,
            ),
            None,
        )
    if load_state != "loaded":
        reason = {
            "malformed_json": "storyform_malformed_json",
            "unsupported_encoding": "storyform_unsupported_encoding",
            "unsupported_structure": "storyform_unsupported_structure",
        }[load_state]
        diagnostic = {
            "malformed_json": "Storyform resource is not valid JSON.",
            "unsupported_encoding": "Storyform resource is not readable as UTF-8 JSON.",
            "unsupported_structure": "Storyform resource must be a regular JSON object file.",
        }[load_state]
        return (
            _resource_result(
                "storyform",
                "project_json",
                exists=True,
                structurally_valid=False,
                ready=False,
                state="invalid",
                reason_code=reason,
                diagnostics=[diagnostic],
                source_locator=locator,
            ),
            None,
        )

    try:
        Storyform.validate_data(data)
    except ValidationError:
        return (
            _resource_result(
                "storyform",
                "project_json",
                exists=True,
                structurally_valid=False,
                ready=False,
                state="invalid",
                reason_code="storyform_schema_invalid",
                diagnostics=["Storyform resource does not satisfy the supported schema."],
                source_locator=locator,
            ),
            None,
        )
    except (FileNotFoundError, OSError, ValueError, json.JSONDecodeError):
        return (
            _resource_result(
                "storyform",
                "project_json",
                exists=True,
                structurally_valid=False,
                ready=False,
                state="unavailable",
                reason_code="storyform_validation_dependency_unavailable",
                diagnostics=["The deterministic storyform validator is unavailable."],
                source_locator=locator,
            ),
            None,
        )

    return (
        _resource_result(
            "storyform",
            "project_json",
            exists=True,
            structurally_valid=True,
            ready=True,
            state="ready",
            reason_code=None,
            diagnostics=[],
            source_locator=locator,
        ),
        data,
    )


def _assess_storyform_context(
    storyform_result: dict[str, Any],
    storyform_data: dict[str, Any] | None,
) -> dict[str, Any]:
    locator = "storyform.json"
    if storyform_result["state"] == "absent":
        return _resource_result(
            "storyform_context",
            "derived_context",
            exists=False,
            structurally_valid=False,
            ready=False,
            state="unavailable",
            reason_code="storyform_context_storyform_absent",
            diagnostics=["Storyform context requires a present storyform."],
            source_locator=locator,
        )
    if storyform_result["state"] == "invalid":
        return _resource_result(
            "storyform_context",
            "derived_context",
            exists=False,
            structurally_valid=False,
            ready=False,
            state="unavailable",
            reason_code="storyform_context_storyform_invalid",
            diagnostics=["Storyform context requires a structurally valid storyform."],
            source_locator=locator,
        )
    if not storyform_result["ready"] or storyform_data is None:
        return _resource_result(
            "storyform_context",
            "derived_context",
            exists=False,
            structurally_valid=False,
            ready=False,
            state="unavailable",
            reason_code="storyform_context_validation_dependency_unavailable",
            diagnostics=["Storyform context validation prerequisites are unavailable."],
            source_locator=locator,
        )

    try:
        context = Storyform(storyform_data).to_prompt_context()
    except Exception:
        return _resource_result(
            "storyform_context",
            "derived_context",
            exists=False,
            structurally_valid=False,
            ready=False,
            state="unavailable",
            reason_code="storyform_context_construction_failed",
            diagnostics=["Storyform context could not be constructed deterministically."],
            source_locator=locator,
        )
    if not isinstance(context, str) or not context.strip():
        return _resource_result(
            "storyform_context",
            "derived_context",
            exists=False,
            structurally_valid=False,
            ready=False,
            state="unavailable",
            reason_code="storyform_context_empty",
            diagnostics=["Storyform context construction produced no usable context."],
            source_locator=locator,
        )
    return _resource_result(
        "storyform_context",
        "derived_context",
        exists=True,
        structurally_valid=True,
        ready=True,
        state="ready",
        reason_code=None,
        diagnostics=[],
        source_locator=locator,
    )


def build_project_context_readiness(
    project_id: str,
    *,
    projects_dir: Path | None = None,
) -> dict[str, Any]:
    """Return deterministic readiness without loading analysis runtimes."""

    root = project_manager.PROJECTS_DIR if projects_dir is None else projects_dir
    project_path = _resolve_project_directory(project_id, root)
    bible = _assess_bible(project_path)
    storyform, storyform_data = _assess_storyform(project_path)
    storyform_context = _assess_storyform_context(storyform, storyform_data)
    resources = {
        "bible": bible,
        "storyform": storyform,
        "storyform_context": storyform_context,
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "project_id": project_id,
        "status_vocabulary": list(STATE_VOCABULARY),
        "resource_order": list(RESOURCE_ORDER),
        "resources": resources,
        "summary": {
            "resource_count": len(resources),
            "ready_count": sum(1 for result in resources.values() if result["ready"]),
            "all_ready": all(result["ready"] for result in resources.values()),
        },
        "safety": {
            "read_only": True,
            "analysis_runtime_invoked": False,
            "model_or_external_tool_invoked": False,
            "resource_mutation": False,
            "candidate_persistence": False,
            "promotion_or_apply_promotion": False,
            "memory_canon_mutation": False,
            "story_prose_generated": False,
        },
    }
