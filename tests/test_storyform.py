import json
import sys
from pathlib import Path

import pytest
from jsonschema.exceptions import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.storyform import Storyform


def test_from_questionnaire_returns_valid_storyform():
    storyform = Storyform.from_questionnaire({})

    Storyform.validate_data(storyform.to_dict())

    assert storyform.data["schema_version"] == "1.3.0"
    assert storyform.data["story"]["title"] == "Quest for the Ember Crown"


def test_from_file_loads_and_validates_project_storyform(tmp_path, monkeypatch):
    project_dir = tmp_path / "sample"
    project_dir.mkdir()
    storyform = Storyform.from_questionnaire({})
    (project_dir / "storyform.json").write_text(
        json.dumps(storyform.to_dict()),
        encoding="utf-8",
    )
    monkeypatch.setattr(Storyform, "PROJECTS_DIR", tmp_path)

    loaded = Storyform.from_file("sample")

    assert loaded.data == storyform.data


def test_from_file_rejects_invalid_storyform(tmp_path, monkeypatch):
    project_dir = tmp_path / "broken"
    project_dir.mkdir()
    (project_dir / "storyform.json").write_text(
        json.dumps({"story": {"title": "Missing required fields"}}),
        encoding="utf-8",
    )
    monkeypatch.setattr(Storyform, "PROJECTS_DIR", tmp_path)

    with pytest.raises(ValidationError):
        Storyform.from_file("broken")


def test_prompt_context_summarizes_throughlines_and_storypoints():
    context = Storyform.from_questionnaire({}).to_prompt_context()

    assert "Story: Quest for the Ember Crown" in context
    assert "Throughlines:" in context
    assert "Objective Story: Domain: Physics" in context
    assert "Concern: Obtaining" in context
    assert "Issue: Value" in context
    assert "Main Character: Domain: Situation" in context
    assert "Storybeats:" in context
    assert "Objective Story signpost 1 / Learning" in context
