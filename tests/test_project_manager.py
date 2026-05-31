import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend import project_manager


def test_save_and_load_bible_round_trips_json(tmp_path, monkeypatch):
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)
    bible = {
        "characters": [{"name": "Mara", "role": "Main Character"}],
        "locations": [{"name": "Frostgate"}],
        "items": [],
    }

    project_manager.save_bible("ember", bible)

    bible_path = tmp_path / "ember" / "bible.json"
    assert json.loads(bible_path.read_text(encoding="utf-8")) == bible
    assert project_manager.load_bible("ember") == bible


def test_load_bible_rejects_non_object_json(tmp_path, monkeypatch):
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)
    project_dir = tmp_path / "ember"
    project_dir.mkdir()
    (project_dir / "bible.json").write_text("[]", encoding="utf-8")

    with pytest.raises(ValueError, match="JSON object"):
        project_manager.load_bible("ember")


def test_save_and_load_scene_round_trips_markdown(tmp_path, monkeypatch):
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)
    content = "# Scene One\n\nMara checks the map."

    project_manager.save_scene("ember", "scene_001", content)

    scene_path = tmp_path / "ember" / "scenes" / "scene_001.md"
    assert scene_path.read_text(encoding="utf-8") == content
    assert project_manager.load_scene("ember", "scene_001") == content


def test_list_scenes_returns_sorted_markdown_scene_ids(tmp_path, monkeypatch):
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)
    scenes_dir = tmp_path / "ember" / "scenes"
    scenes_dir.mkdir(parents=True)
    (scenes_dir / "scene_010.md").write_text("ten", encoding="utf-8")
    (scenes_dir / "scene_002.md").write_text("two", encoding="utf-8")
    (scenes_dir / "notes.txt").write_text("ignore", encoding="utf-8")

    assert project_manager.list_scenes("ember") == ["scene_002", "scene_010"]


def test_list_scenes_returns_empty_list_when_scenes_dir_is_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)

    assert project_manager.list_scenes("ember") == []


def test_project_name_and_scene_id_must_be_single_path_components(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)

    with pytest.raises(ValueError):
        project_manager.save_bible("../outside", {})

    with pytest.raises(ValueError):
        project_manager.save_scene("ember", "../outside", "nope")
