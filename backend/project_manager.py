from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
PROJECTS_DIR = REPO_ROOT / "projects"


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


def load_bible(project_name: str) -> dict[str, Any]:
    path = _project_dir(project_name) / "bible.json"
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)

    if not isinstance(data, dict):
        raise ValueError(f"Bible file must contain a JSON object: {path}")

    return data


def save_bible(project_name: str, data: dict[str, Any]) -> None:
    path = _project_dir(project_name) / "bible.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


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
