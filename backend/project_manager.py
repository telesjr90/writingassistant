from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


REPO_ROOT = Path(__file__).resolve().parents[1]
PROJECTS_DIR = REPO_ROOT / "projects"

OMI_CANDIDATE_TYPES = {
    "planning_note",
    "project_bible_candidate",
    "storyform_context_candidate",
    "scene_prompt_context_candidate",
    "template_starter_candidate",
}

OMI_DESTINATIONS = {
    "planning_notes",
    "project_bible_candidate",
    "storyform_context_candidate",
    "scene_prompt_context_candidate",
    "template_starter_candidate",
    "discard",
}

OMI_BLOCKED_DESTINATIONS = {
    "scene_prose",
    "chapter",
    "dialogue",
    "rewrite",
    "continuation",
    "final_story_text",
}


def _safe_path_component(value: str, label: str) -> str:
    if not value:
        raise ValueError(f"{label} must not be empty")

    path = Path(value)
    if path.is_absolute() or path.parts != (value,) or value in {".", ".."}:
        raise ValueError(f"{label} must be a single path component")

    return value


def _project_dir(project_name: str) -> Path:
    safe_name = _safe_path_component(project_name, "project_name")
    return PROJECTS_DIR / safe_name


def _scene_path(project_name: str, scene_id: str) -> Path:
    safe_scene_id = _safe_path_component(scene_id, "scene_id")
    return _project_dir(project_name) / "scenes" / f"{safe_scene_id}.md"


def _json_path(project_name: str, filename: str) -> Path:
    return _project_dir(project_name) / filename


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _new_record_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}"


def _omi_dir(project_name: str) -> Path:
    return _project_dir(project_name) / "omi"


def _omi_index_path(project_name: str) -> Path:
    return _omi_dir(project_name) / "index.json"


def _omi_record_path(project_name: str, folder_name: str, record_id: str, label: str) -> Path:
    safe_id = _safe_path_component(record_id, label)
    return _omi_dir(project_name) / folder_name / f"{safe_id}.json"


def _load_json_object(project_name: str, filename: str, label: str) -> dict[str, Any]:
    path = _json_path(project_name, filename)
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)

    if not isinstance(data, dict):
        raise ValueError(f"{label} file must contain a JSON object: {path}")

    return data


def _save_json_object(project_name: str, filename: str, data: dict[str, Any], label: str) -> None:
    if not isinstance(data, dict):
        raise ValueError(f"{label} data must be a JSON object")

    path = _json_path(project_name, filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _write_json_object(path: Path, data: dict[str, Any], label: str, *, overwrite: bool) -> None:
    if not isinstance(data, dict):
        raise ValueError(f"{label} data must be a JSON object")
    if path.exists() and not overwrite:
        raise FileExistsError(f"{label} already exists: {path.name}")

    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(f".{path.name}.{uuid4().hex}.tmp")

    try:
        temp_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        temp_path.replace(path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def _load_json_object_from_path(path: Path, label: str) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)

    if not isinstance(data, dict):
        raise ValueError(f"{label} file must contain a JSON object: {path}")

    return data


def _default_omi_index(project_name: str) -> dict[str, Any]:
    return {
        "project_id": project_name,
        "idea_ids": [],
        "candidate_ids": [],
        "promotion_ids": [],
        "last_updated": None,
    }


def _normalise_omi_index(project_name: str, index: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(index, dict):
        raise ValueError("OMI index data must be a JSON object")

    return {
        "project_id": project_name,
        "idea_ids": sorted(set(index.get("idea_ids", []))),
        "candidate_ids": sorted(set(index.get("candidate_ids", []))),
        "promotion_ids": sorted(set(index.get("promotion_ids", []))),
        "last_updated": index.get("last_updated"),
    }


def _default_omi_provenance(
    *,
    source_type: str = "owner_input",
    source_path: str | None = None,
    source_label: str = "Manual OMI entry",
) -> dict[str, Any]:
    return {
        "source_type": source_type,
        "source_path": source_path,
        "source_label": source_label,
        "created_by": "owner",
        "tool": "app",
        "model": None,
        "prompt_id": None,
        "timestamp": _utc_now(),
        "source_hash": None,
        "snapshot_hash": None,
        "confidence": None,
        "notes": [],
    }


def _normalise_provenance(
    provenance: dict[str, Any] | None,
    *,
    source_path: str | None,
    source_label: str,
) -> dict[str, Any]:
    if provenance is None:
        return _default_omi_provenance(source_path=source_path, source_label=source_label)
    if not isinstance(provenance, dict):
        raise ValueError("OMI provenance must be a JSON object")

    merged = _default_omi_provenance(source_path=source_path, source_label=source_label)
    merged.update(provenance)
    merged.setdefault("timestamp", _utc_now())
    return merged


def _default_owner_decision() -> dict[str, Any]:
    return {
        "decision": "pending",
        "approved": False,
        "decided_by": None,
        "decided_at": None,
        "notes": "",
    }


def _validate_omi_destination(destination: str) -> str:
    if destination in OMI_BLOCKED_DESTINATIONS or destination not in OMI_DESTINATIONS:
        raise ValueError(f"Unsupported OMI destination: {destination}")
    return destination


def _validate_omi_candidate_type(candidate_type: str) -> str:
    if candidate_type not in OMI_CANDIDATE_TYPES:
        raise ValueError(f"Unsupported OMI candidate_type: {candidate_type}")
    return candidate_type


def load_bible(project_name: str) -> dict[str, Any]:
    return _load_json_object(project_name, "bible.json", "Bible")


def save_bible(project_name: str, data: dict[str, Any]) -> None:
    _save_json_object(project_name, "bible.json", data, "Bible")


def load_storyform_json(project_name: str) -> dict[str, Any]:
    return _load_json_object(project_name, "storyform.json", "Storyform")


def save_storyform_json(project_name: str, data: dict[str, Any]) -> None:
    if not isinstance(data, dict):
        raise ValueError("Storyform data must be a JSON object")

    try:
        from .storyform import Storyform
    except ImportError:  # pragma: no cover - supports direct module execution
        from storyform import Storyform

    Storyform.validate_data(data)
    _save_json_object(project_name, "storyform.json", data, "Storyform")


def load_scene(project_name: str, scene_id: str) -> str:
    return _scene_path(project_name, scene_id).read_text(encoding="utf-8")


def save_scene(project_name: str, scene_id: str, content: str) -> None:
    path = _scene_path(project_name, scene_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def list_scenes(project_name: str) -> list[str]:
    scenes_dir = _project_dir(project_name) / "scenes"
    if not scenes_dir.exists():
        return []

    return [path.stem for path in sorted(scenes_dir.glob("*.md")) if path.is_file()]


def ensure_omi_storage(project_name: str) -> None:
    omi_dir = _omi_dir(project_name)
    (omi_dir / "ideas").mkdir(parents=True, exist_ok=True)
    (omi_dir / "candidates").mkdir(parents=True, exist_ok=True)
    (omi_dir / "promotions").mkdir(parents=True, exist_ok=True)


def load_omi_index(project_name: str) -> dict[str, Any]:
    path = _omi_index_path(project_name)
    if not path.exists():
        return _default_omi_index(project_name)

    return _normalise_omi_index(
        project_name,
        _load_json_object_from_path(path, "OMI index"),
    )


def save_omi_index(project_name: str, index: dict[str, Any]) -> None:
    ensure_omi_storage(project_name)
    normalized = _normalise_omi_index(project_name, index)
    normalized["last_updated"] = normalized.get("last_updated") or _utc_now()
    _write_json_object(_omi_index_path(project_name), normalized, "OMI index", overwrite=True)


def create_omi_idea(
    project_name: str,
    raw_idea: str,
    provenance: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not isinstance(raw_idea, str) or not raw_idea.strip():
        raise ValueError("OMI raw_idea must not be empty")

    ensure_omi_storage(project_name)
    idea_id = _new_record_id("idea")
    timestamp = _utc_now()
    idea = {
        "idea_id": idea_id,
        "project_id": project_name,
        "raw_idea": raw_idea.strip(),
        "status": "draft",
        "created_at": timestamp,
        "updated_at": timestamp,
        "provenance": _normalise_provenance(
            provenance,
            source_path=None,
            source_label="Manual OMI raw idea",
        ),
        "owner_decision": _default_owner_decision(),
        "linked_candidate_ids": [],
    }

    _write_json_object(
        _omi_record_path(project_name, "ideas", idea_id, "idea_id"),
        idea,
        "OMI idea",
        overwrite=False,
    )

    index = load_omi_index(project_name)
    index["idea_ids"] = sorted(set(index.get("idea_ids", [])) | {idea_id})
    index["last_updated"] = timestamp
    save_omi_index(project_name, index)

    return idea


def list_omi_ideas(project_name: str) -> list[dict[str, Any]]:
    index = load_omi_index(project_name)
    ideas: list[dict[str, Any]] = []

    for idea_id in index.get("idea_ids", []):
        try:
            ideas.append(load_omi_idea(project_name, idea_id))
        except FileNotFoundError:
            continue

    return ideas


def load_omi_idea(project_name: str, idea_id: str) -> dict[str, Any]:
    return _load_json_object_from_path(
        _omi_record_path(project_name, "ideas", idea_id, "idea_id"),
        "OMI idea",
    )


def create_omi_candidate(
    project_name: str,
    idea_id: str,
    candidate_type: str,
    candidate_content: dict[str, Any],
    destination: str,
    provenance: dict[str, Any] | None = None,
    evidence: list[Any] | None = None,
) -> dict[str, Any]:
    if not isinstance(candidate_content, dict):
        raise ValueError("OMI candidate_content must be a JSON object")
    if evidence is not None and not isinstance(evidence, list):
        raise ValueError("OMI evidence must be a JSON array")

    _validate_omi_candidate_type(candidate_type)
    _validate_omi_destination(destination)
    idea = load_omi_idea(project_name, idea_id)

    ensure_omi_storage(project_name)
    candidate_id = _new_record_id("candidate")
    timestamp = _utc_now()
    candidate = {
        "candidate_id": candidate_id,
        "project_id": project_name,
        "idea_id": idea_id,
        "candidate_type": candidate_type,
        "candidate_content": candidate_content,
        "status": "candidate",
        "destination": destination,
        "provenance": _normalise_provenance(
            provenance,
            source_path=f"omi/ideas/{idea_id}.json",
            source_label="Manual OMI candidate",
        ),
        "evidence": evidence or [],
        "owner_decision": _default_owner_decision(),
        "promotion_status": {
            "eligible": False,
            "promotion_id": None,
            "blocked_reasons": [
                "owner approval required",
                "final confirmation required",
            ],
        },
        "created_at": timestamp,
        "updated_at": timestamp,
    }

    _write_json_object(
        _omi_record_path(project_name, "candidates", candidate_id, "candidate_id"),
        candidate,
        "OMI candidate",
        overwrite=False,
    )

    idea["linked_candidate_ids"] = sorted(
        set(idea.get("linked_candidate_ids", [])) | {candidate_id}
    )
    idea["updated_at"] = timestamp
    _write_json_object(
        _omi_record_path(project_name, "ideas", idea_id, "idea_id"),
        idea,
        "OMI idea",
        overwrite=True,
    )

    index = load_omi_index(project_name)
    index["idea_ids"] = sorted(set(index.get("idea_ids", [])) | {idea_id})
    index["candidate_ids"] = sorted(set(index.get("candidate_ids", [])) | {candidate_id})
    index["last_updated"] = timestamp
    save_omi_index(project_name, index)

    return candidate


def list_omi_candidates(
    project_name: str,
    idea_id: str | None = None,
) -> list[dict[str, Any]]:
    if idea_id is not None:
        _safe_path_component(idea_id, "idea_id")

    index = load_omi_index(project_name)
    candidates: list[dict[str, Any]] = []

    for candidate_id in index.get("candidate_ids", []):
        try:
            candidate = load_omi_candidate(project_name, candidate_id)
        except FileNotFoundError:
            continue
        if idea_id is None or candidate.get("idea_id") == idea_id:
            candidates.append(candidate)

    return candidates


def load_omi_candidate(project_name: str, candidate_id: str) -> dict[str, Any]:
    return _load_json_object_from_path(
        _omi_record_path(project_name, "candidates", candidate_id, "candidate_id"),
        "OMI candidate",
    )


def get_omi_summary(project_name: str) -> dict[str, Any]:
    return {
        "index": load_omi_index(project_name),
        "ideas": list_omi_ideas(project_name),
        "candidates": list_omi_candidates(project_name),
    }
