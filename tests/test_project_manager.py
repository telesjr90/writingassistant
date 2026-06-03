import json
import sys
from pathlib import Path

import pytest
from jsonschema.exceptions import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend import project_manager
from backend.storyform import Storyform


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


def test_save_bible_rejects_non_object_data(tmp_path, monkeypatch):
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)

    with pytest.raises(ValueError, match="JSON object"):
        project_manager.save_bible("ember", [])


def test_save_and_load_storyform_json_round_trips_valid_data(tmp_path, monkeypatch):
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)
    storyform = Storyform.from_questionnaire({}).to_dict()

    project_manager.save_storyform_json("ember", storyform)

    storyform_path = tmp_path / "ember" / "storyform.json"
    assert json.loads(storyform_path.read_text(encoding="utf-8")) == storyform
    assert project_manager.load_storyform_json("ember") == storyform


def test_save_storyform_json_rejects_invalid_data_without_overwriting(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)
    valid_storyform = Storyform.from_questionnaire({}).to_dict()
    project_manager.save_storyform_json("ember", valid_storyform)
    storyform_path = tmp_path / "ember" / "storyform.json"
    original_text = storyform_path.read_text(encoding="utf-8")

    with pytest.raises(ValidationError):
        project_manager.save_storyform_json("ember", {"story": {"title": "Invalid"}})

    assert storyform_path.read_text(encoding="utf-8") == original_text


def test_save_and_load_scene_round_trips_markdown(tmp_path, monkeypatch):
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)
    content = "# Scene One\n\nMara checks the map."

    project_manager.save_scene("ember", "scene_001", content)

    scene_path = tmp_path / "ember" / "scenes" / "scene_001.md"
    assert scene_path.read_text(encoding="utf-8") == content
    assert project_manager.load_scene("ember", "scene_001") == content


def test_save_and_load_empty_scene_round_trips(tmp_path, monkeypatch):
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)

    project_manager.save_scene("ember", "empty_scene", "")

    scene_path = tmp_path / "ember" / "scenes" / "empty_scene.md"
    assert scene_path.read_text(encoding="utf-8") == ""
    assert project_manager.load_scene("ember", "empty_scene") == ""


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


def test_create_omi_idea_creates_storage_and_index(tmp_path, monkeypatch):
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)

    idea = project_manager.create_omi_idea("ember", "Track the antagonist pressure.")

    assert idea["idea_id"].startswith("idea_")
    assert idea["project_id"] == "ember"
    assert idea["raw_idea"] == "Track the antagonist pressure."
    assert idea["status"] == "draft"
    assert idea["owner_decision"]["decision"] == "pending"
    assert idea["owner_decision"]["approved"] is False
    assert idea["provenance"]["source_type"] == "owner_input"
    assert idea["provenance"]["created_by"] == "owner"
    assert idea["linked_candidate_ids"] == []

    omi_dir = tmp_path / "ember" / "omi"
    assert (omi_dir / "ideas" / f"{idea['idea_id']}.json").exists()
    assert (omi_dir / "candidates").is_dir()
    assert (omi_dir / "promotions").is_dir()

    index = project_manager.load_omi_index("ember")
    assert index["idea_ids"] == [idea["idea_id"]]
    assert index["candidate_ids"] == []
    assert index["promotion_ids"] == []


def test_list_omi_ideas_returns_created_records(tmp_path, monkeypatch):
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)
    first = project_manager.create_omi_idea("ember", "First structural note.")
    second = project_manager.create_omi_idea("ember", "Second structural note.")

    loaded_ids = {idea["idea_id"] for idea in project_manager.list_omi_ideas("ember")}

    assert loaded_ids == {first["idea_id"], second["idea_id"]}
    assert project_manager.load_omi_idea("ember", first["idea_id"]) == first


def test_create_omi_candidate_links_to_idea_and_updates_index(tmp_path, monkeypatch):
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)
    idea = project_manager.create_omi_idea("ember", "Consider a planning-only note.")

    candidate = project_manager.create_omi_candidate(
        "ember",
        idea["idea_id"],
        "planning_note",
        {"summary": "Structural planning note", "questions": []},
        "planning_notes",
        evidence=[],
    )

    assert candidate["candidate_id"].startswith("candidate_")
    assert candidate["project_id"] == "ember"
    assert candidate["idea_id"] == idea["idea_id"]
    assert candidate["candidate_type"] == "planning_note"
    assert candidate["destination"] == "planning_notes"
    assert candidate["status"] == "candidate"
    assert candidate["promotion_status"]["eligible"] is False
    assert "owner approval required" in candidate["promotion_status"]["blocked_reasons"]
    assert candidate["owner_decision"]["approved"] is False

    updated_idea = project_manager.load_omi_idea("ember", idea["idea_id"])
    assert updated_idea["linked_candidate_ids"] == [candidate["candidate_id"]]

    index = project_manager.load_omi_index("ember")
    assert index["idea_ids"] == [idea["idea_id"]]
    assert index["candidate_ids"] == [candidate["candidate_id"]]
    assert project_manager.list_omi_candidates("ember") == [candidate]
    assert project_manager.list_omi_candidates("ember", idea["idea_id"]) == [candidate]


def test_create_omi_candidate_rejects_unknown_idea(tmp_path, monkeypatch):
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)

    with pytest.raises(FileNotFoundError):
        project_manager.create_omi_candidate(
            "ember",
            "idea_missing",
            "planning_note",
            {"summary": "Structural planning note"},
            "planning_notes",
        )


def test_create_omi_idea_rejects_empty_raw_idea(tmp_path, monkeypatch):
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)

    with pytest.raises(ValueError, match="raw_idea"):
        project_manager.create_omi_idea("ember", "   ")


def test_create_omi_candidate_rejects_invalid_type_and_destination(tmp_path, monkeypatch):
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)
    idea = project_manager.create_omi_idea("ember", "Keep planning separate.")

    with pytest.raises(ValueError, match="candidate_type"):
        project_manager.create_omi_candidate(
            "ember",
            idea["idea_id"],
            "dialogue",
            {"summary": "Invalid type"},
            "planning_notes",
        )

    with pytest.raises(ValueError, match="destination"):
        project_manager.create_omi_candidate(
            "ember",
            idea["idea_id"],
            "planning_note",
            {"summary": "Invalid destination"},
            "scene_prose",
        )

    with pytest.raises(ValueError, match="destination"):
        project_manager.create_omi_candidate(
            "ember",
            idea["idea_id"],
            "planning_note",
            {"summary": "Invalid destination"},
            "rewrite",
        )


def test_create_omi_candidate_requires_object_content_and_array_evidence(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)
    idea = project_manager.create_omi_idea("ember", "Keep candidate structured.")

    with pytest.raises(ValueError, match="candidate_content"):
        project_manager.create_omi_candidate(
            "ember",
            idea["idea_id"],
            "planning_note",
            [],
            "planning_notes",
        )

    with pytest.raises(ValueError, match="evidence"):
        project_manager.create_omi_candidate(
            "ember",
            idea["idea_id"],
            "planning_note",
            {"summary": "Structured candidate"},
            "planning_notes",
            evidence={},
        )


def test_omi_create_does_not_modify_project_truth_files(tmp_path, monkeypatch):
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)
    project_dir = tmp_path / "ember"
    scenes_dir = project_dir / "scenes"
    scenes_dir.mkdir(parents=True)
    files = {
        project_dir / "project.json": '{"title": "Fixture"}\n',
        project_dir / "bible.json": '{"characters": []}\n',
        project_dir / "storyform.json": '{"schema_version": "ncp-0.1"}\n',
        scenes_dir / "scene_001.md": "Owner-authored scene text.",
    }
    for path, content in files.items():
        path.write_text(content, encoding="utf-8")

    idea = project_manager.create_omi_idea("ember", "Owner-authored planning input.")
    project_manager.create_omi_candidate(
        "ember",
        idea["idea_id"],
        "project_bible_candidate",
        {"summary": "Candidate-only context"},
        "project_bible_candidate",
    )

    for path, content in files.items():
        assert path.read_text(encoding="utf-8") == content


def test_omi_path_components_must_be_safe(tmp_path, monkeypatch):
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)
    idea = project_manager.create_omi_idea("ember", "Safe idea.")

    with pytest.raises(ValueError):
        project_manager.create_omi_idea("../outside", "Nope.")

    with pytest.raises(ValueError):
        project_manager.load_omi_idea("ember", "../outside")

    with pytest.raises(ValueError):
        project_manager.list_omi_candidates("ember", "../outside")

    with pytest.raises(ValueError):
        project_manager.load_omi_candidate("ember", "../outside")

    assert project_manager.load_omi_idea("ember", idea["idea_id"]) == idea


def test_omi_raw_idea_allows_owner_authored_context_words(tmp_path, monkeypatch):
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)

    idea = project_manager.create_omi_idea(
        "ember",
        'Owner note mentions write, dialogue, chapter, and continue as context terms.',
    )

    assert "dialogue" in idea["raw_idea"]


def test_update_omi_idea_decision_to_owner_review(tmp_path, monkeypatch):
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)
    idea = project_manager.create_omi_idea("ember", "Review this planning note.")

    updated = project_manager.update_omi_idea_decision(
        "ember",
        idea["idea_id"],
        {"decision": "pending", "notes": "Owner review requested."},
        status="owner_review",
    )

    assert updated["status"] == "owner_review"
    assert updated["owner_decision"]["decision"] == "pending"
    assert updated["owner_decision"]["notes"] == "Owner review requested."
    assert updated["owner_decision"]["approved"] is False
    assert updated["updated_at"] != idea["updated_at"]


def test_approve_omi_idea_requires_confirmation(tmp_path, monkeypatch):
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)
    idea = project_manager.create_omi_idea("ember", "Approval candidate.")
    reviewed = project_manager.update_omi_idea_decision(
        "ember",
        idea["idea_id"],
        {"decision": "pending"},
        status="owner_review",
    )
    before = project_manager.load_omi_idea("ember", idea["idea_id"])

    with pytest.raises(ValueError, match="approval_confirmed"):
        project_manager.update_omi_idea_decision(
            "ember",
            reviewed["idea_id"],
            {"decision": "approve", "approval_confirmed": False},
            status="approved",
        )

    assert project_manager.load_omi_idea("ember", idea["idea_id"]) == before

    approved = project_manager.update_omi_idea_decision(
        "ember",
        reviewed["idea_id"],
        {"decision": "approve", "approval_confirmed": True, "notes": "Approved."},
        status="approved",
    )

    assert approved["status"] == "approved"
    assert approved["owner_decision"]["approved"] is True
    assert approved["owner_decision"]["approval_confirmed"] is True
    assert approved["owner_decision"]["decided_by"] == "owner"
    assert approved["owner_decision"]["decided_at"]


def test_reject_omi_idea_and_invalid_updates_preserve_file(tmp_path, monkeypatch):
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)
    idea = project_manager.create_omi_idea("ember", "Rejectable note.")
    reviewed = project_manager.update_omi_idea_decision(
        "ember",
        idea["idea_id"],
        {"decision": "pending"},
        status="owner_review",
    )

    rejected = project_manager.update_omi_idea_decision(
        "ember",
        reviewed["idea_id"],
        {"decision": "reject", "notes": "Not relevant."},
        status="rejected",
    )

    assert rejected["status"] == "rejected"
    assert rejected["owner_decision"]["decision"] == "reject"

    before = project_manager.load_omi_idea("ember", idea["idea_id"])

    with pytest.raises(ValueError, match="owner_decision"):
        project_manager.update_omi_idea_decision(
            "ember",
            idea["idea_id"],
            {"decision": "promote"},
            status="approved",
        )

    with pytest.raises(ValueError, match="Invalid OMI status transition"):
        project_manager.update_omi_idea_decision(
            "ember",
            idea["idea_id"],
            {"decision": "pending"},
            status="approved",
        )

    assert project_manager.load_omi_idea("ember", idea["idea_id"]) == before


def test_update_omi_candidate_destination_and_decision(tmp_path, monkeypatch):
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)
    idea = project_manager.create_omi_idea("ember", "Candidate destination.")
    candidate = project_manager.create_omi_candidate(
        "ember",
        idea["idea_id"],
        "planning_note",
        {"summary": "Candidate-only context"},
        "planning_notes",
    )

    updated = project_manager.update_omi_candidate_decision(
        "ember",
        candidate["candidate_id"],
        {"decision": "pending", "notes": "Move to owner review."},
        status="owner_review",
        destination="project_bible_candidate",
    )

    assert updated["status"] == "owner_review"
    assert updated["destination"] == "project_bible_candidate"
    assert updated["promotion_status"]["eligible"] is False
    assert updated["updated_at"] != candidate["updated_at"]


def test_approve_omi_candidate_requires_confirmation(tmp_path, monkeypatch):
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)
    idea = project_manager.create_omi_idea("ember", "Candidate approval.")
    candidate = project_manager.create_omi_candidate(
        "ember",
        idea["idea_id"],
        "planning_note",
        {"summary": "Candidate-only context"},
        "planning_notes",
    )
    reviewed = project_manager.update_omi_candidate_decision(
        "ember",
        candidate["candidate_id"],
        {"decision": "pending"},
        status="owner_review",
    )
    before = project_manager.load_omi_candidate("ember", candidate["candidate_id"])

    with pytest.raises(ValueError, match="approval_confirmed"):
        project_manager.update_omi_candidate_decision(
            "ember",
            reviewed["candidate_id"],
            {"decision": "approve", "approval_confirmed": False},
            status="approved",
        )

    assert project_manager.load_omi_candidate("ember", candidate["candidate_id"]) == before

    approved = project_manager.update_omi_candidate_decision(
        "ember",
        reviewed["candidate_id"],
        {"decision": "approve", "approval_confirmed": True},
        status="approved",
    )

    assert approved["status"] == "approved"
    assert approved["owner_decision"]["approved"] is True
    assert approved["promotion_status"]["eligible"] is False
    assert "final confirmation required" in approved["promotion_status"]["blocked_reasons"]


def test_reject_omi_candidate_and_invalid_destination_or_status(tmp_path, monkeypatch):
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)
    idea = project_manager.create_omi_idea("ember", "Candidate rejection.")
    candidate = project_manager.create_omi_candidate(
        "ember",
        idea["idea_id"],
        "planning_note",
        {"summary": "Candidate-only context"},
        "planning_notes",
    )
    reviewed = project_manager.update_omi_candidate_decision(
        "ember",
        candidate["candidate_id"],
        {"decision": "pending"},
        status="owner_review",
    )

    rejected = project_manager.update_omi_candidate_decision(
        "ember",
        reviewed["candidate_id"],
        {"decision": "reject", "notes": "Not useful."},
        status="rejected",
    )

    assert rejected["status"] == "rejected"
    assert rejected["owner_decision"]["decision"] == "reject"

    before = project_manager.load_omi_candidate("ember", candidate["candidate_id"])

    with pytest.raises(ValueError, match="destination"):
        project_manager.update_omi_candidate_decision(
            "ember",
            candidate["candidate_id"],
            {"decision": "pending"},
            destination="scene_prose",
        )

    with pytest.raises(ValueError, match="promoted status"):
        project_manager.update_omi_candidate_decision(
            "ember",
            candidate["candidate_id"],
            {"decision": "pending"},
            status="promoted",
        )

    with pytest.raises(FileNotFoundError):
        project_manager.update_omi_candidate_decision(
            "ember",
            "candidate_missing",
            {"decision": "pending"},
        )

    assert project_manager.load_omi_candidate("ember", candidate["candidate_id"]) == before


def test_omi_decision_update_does_not_modify_project_truth_files(tmp_path, monkeypatch):
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)
    project_dir = tmp_path / "ember"
    scenes_dir = project_dir / "scenes"
    scenes_dir.mkdir(parents=True)
    files = {
        project_dir / "project.json": '{"title": "Fixture"}\n',
        project_dir / "bible.json": '{"characters": []}\n',
        project_dir / "storyform.json": '{"schema_version": "ncp-0.1"}\n',
        scenes_dir / "scene_001.md": "Owner-authored scene text.",
    }
    for path, content in files.items():
        path.write_text(content, encoding="utf-8")

    idea = project_manager.create_omi_idea("ember", "Owner-authored planning input.")
    candidate = project_manager.create_omi_candidate(
        "ember",
        idea["idea_id"],
        "project_bible_candidate",
        {"summary": "Candidate-only context"},
        "project_bible_candidate",
    )
    project_manager.update_omi_idea_decision(
        "ember",
        idea["idea_id"],
        {"decision": "pending", "notes": "write dialogue chapter context only"},
        status="owner_review",
    )
    project_manager.update_omi_candidate_decision(
        "ember",
        candidate["candidate_id"],
        {"decision": "pending", "notes": "write dialogue chapter context only"},
        status="owner_review",
        destination="storyform_context_candidate",
    )

    for path, content in files.items():
        assert path.read_text(encoding="utf-8") == content
