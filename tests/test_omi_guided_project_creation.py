from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from backend import main, project_manager


@pytest.fixture
def projects_root(tmp_path, monkeypatch):
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)
    return tmp_path


def _idea_path(root: Path, result: dict) -> Path:
    return (
        root
        / result["project_id"]
        / "omi"
        / "ideas"
        / f"{result['omi_idea_id']}.json"
    )


def _forbid_runtime_and_truth_writes(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("guided creation crossed a prohibited runtime boundary")

    for name in (
        "create_omi_candidate",
        "create_omi_promotion_record",
        "extract_omi_candidates_from_raw_idea",
        "save_bible",
        "save_storyform_json",
        "save_scene",
    ):
        monkeypatch.setattr(project_manager, name, forbidden)


def test_complete_guided_creation_preserves_input_and_links_storage(
    projects_root, monkeypatch
):
    _forbid_runtime_and_truth_writes(monkeypatch)
    title = "  Owner's  Project: One!  "
    raw_idea = "\r\n  Owner idea line one.\nLine two.  \r\n"
    setup_notes = "  Setup note.\r\n\nSecond line.  "

    result = project_manager.create_omi_guided_project(
        title=title,
        raw_idea=raw_idea,
        setup_notes=setup_notes,
    )

    assert result["status"] == "complete"
    assert result["project_id"] == "owner-s-project-one"
    assert result["title"] == "Owner's  Project: One!"
    assert result["creation_method"] == "omi_guided"
    assert result["setup_note_id"] == "omi_guided_setup_notes"

    project_dir = projects_root / result["project_id"]
    project_metadata = json.loads(
        (project_dir / "project.json").read_text(encoding="utf-8")
    )
    assert result["project_metadata"] == project_metadata
    assert project_metadata["creation_method"] == "omi_guided"
    assert project_metadata["title"] == "Owner's  Project: One!"
    assert project_metadata["omi_guided_creation"] == {
        "status": "complete",
        "omi_idea_id": result["omi_idea_id"],
        "setup_note_id": result["setup_note_id"],
        "owner_authored": True,
        "model_generated": False,
        "is_canon": False,
        "owner_approval_status": "pending",
    }
    assert raw_idea not in json.dumps(project_metadata)
    assert setup_notes not in json.dumps(project_metadata)

    idea = json.loads(_idea_path(projects_root, result).read_text(encoding="utf-8"))
    assert idea["raw_idea"].encode() == raw_idea.encode()
    assert idea["status"] == "draft"
    assert idea["owner_decision"]["decision"] == "pending"
    assert idea["owner_decision"]["approved"] is False
    assert idea["linked_candidate_ids"] == []
    assert idea["provenance"]["source_type"] == "owner_input"
    assert idea["provenance"]["source"] == "owner"
    assert idea["provenance"]["created_by"] == "owner"
    assert idea["provenance"]["creation_method"] == "omi_guided"
    assert idea["provenance"]["model"] is None
    assert idea["provenance"]["tool"] is None
    assert idea["provenance"]["model_generated"] is False
    assert idea["provenance"]["is_canon"] is False

    note_path = project_dir / "notes" / "omi_guided_setup_notes.md"
    assert note_path.read_bytes() == setup_notes.encode()
    note_metadata = project_manager.load_note_metadata(
        result["project_id"], result["setup_note_id"]
    )
    assert note_metadata["metadata_exists"] is True
    assert note_metadata["status"] == "pending_owner_use"
    assert note_metadata["model_generated"] is False
    assert note_metadata["is_canon"] is False
    assert note_metadata["owner_approval_status"] == "pending"
    assert note_metadata["provenance"]["created_by"] == "owner"
    assert note_metadata["provenance"]["creation_method"] == "omi_guided"
    assert note_metadata["provenance"]["model_generated"] is False
    assert note_metadata["provenance"]["is_canon"] is False

    omi_dir = project_dir / "omi"
    assert list((omi_dir / "candidates").glob("*.json")) == []
    assert list((omi_dir / "promotions").glob("*.json")) == []
    assert not (project_dir / "bible.json").exists()
    assert not (project_dir / "storyform.json").exists()
    assert not (project_dir / "memory").exists()
    assert list((project_dir / "scenes").iterdir()) == []
    assert not (project_dir / project_manager._OMI_GUIDED_TRANSACTION_MARKER).exists()


def test_empty_setup_note_is_stored_and_has_metadata(projects_root):
    result = project_manager.create_omi_guided_project("Empty Notes", "Owner idea", "")

    assert project_manager.load_note(
        result["project_id"], result["setup_note_id"]
    ) == ""
    assert project_manager.load_note_metadata(
        result["project_id"], result["setup_note_id"]
    )["metadata_exists"] is True


def test_guided_route_contract_and_blank_route_remain_distinct(projects_root):
    guided = main.post_omi_guided_project(
        main.OMIGuidedProjectCreate.model_validate(
            {"title": "Route Project", "raw_idea": "Owner idea", "setup_notes": ""}
        )
    )
    blank = main.post_project(SimpleNamespace(title="Blank Project"))

    assert guided["status"] == "complete"
    assert guided["creation_method"] == "omi_guided"
    assert blank["creation_method"] == "blank"
    assert "omi_guided_creation" not in blank
    assert not (projects_root / "blank-project" / "omi").exists()


def test_guided_request_requires_exact_string_fields():
    valid = {"title": "Project", "raw_idea": "Idea", "setup_notes": ""}
    for missing in valid:
        payload = dict(valid)
        payload.pop(missing)
        with pytest.raises(ValidationError):
            main.OMIGuidedProjectCreate.model_validate(payload)

    for field in valid:
        payload = dict(valid)
        payload[field] = 7
        with pytest.raises(ValidationError):
            main.OMIGuidedProjectCreate.model_validate(payload)

    extra = dict(valid, project_id="unsafe")
    with pytest.raises(ValidationError):
        main.OMIGuidedProjectCreate.model_validate(extra)


@pytest.mark.parametrize("title", ["   ", "!!!", "api"])
def test_guided_creation_rejects_unsafe_titles_without_mutation(
    title, projects_root
):
    with pytest.raises(main.HTTPException) as exc_info:
        main.post_omi_guided_project(
            SimpleNamespace(title=title, raw_idea="Owner idea", setup_notes="notes")
        )

    assert exc_info.value.status_code == 400
    assert list(projects_root.iterdir()) == []
    assert str(projects_root) not in str(exc_info.value.detail)


def test_semantically_blank_raw_idea_is_rejected_before_mutation(projects_root):
    with pytest.raises(main.HTTPException) as exc_info:
        main.post_omi_guided_project(
            SimpleNamespace(title="No Idea", raw_idea=" \r\n\t ", setup_notes="")
        )

    assert exc_info.value.status_code == 400
    assert "raw_idea" in str(exc_info.value.detail)
    assert list(projects_root.iterdir()) == []


def test_duplicate_titles_use_deterministic_suffixes(projects_root):
    first = project_manager.create_omi_guided_project("Duplicate", "First", "")
    second = project_manager.create_omi_guided_project("Duplicate", "Second", "")

    assert first["project_id"] == "duplicate"
    assert second["project_id"] == "duplicate-2"


@pytest.mark.parametrize(
    ("failed_step", "install_failure"),
    [
        (
            "persist_omi_idea",
            lambda monkeypatch, fail: monkeypatch.setattr(
                project_manager, "create_omi_idea", fail
            ),
        ),
        (
            "persist_setup_note",
            lambda monkeypatch, fail: monkeypatch.setattr(
                project_manager, "save_note", fail
            ),
        ),
        (
            "persist_setup_note_metadata",
            lambda monkeypatch, fail: monkeypatch.setattr(
                project_manager, "create_note_metadata", fail
            ),
        ),
        (
            "link_guided_creation_metadata",
            None,
        ),
    ],
)
def test_each_persistence_failure_rolls_back_without_residual_project(
    failed_step, install_failure, projects_root, monkeypatch
):
    def fail(*args, **kwargs):
        raise OSError("injected persistence failure")

    if install_failure is not None:
        install_failure(monkeypatch, fail)
    else:
        original_write = project_manager._write_json_object

        def fail_link(path, data, label, *, overwrite):
            if path.name == "project.json" and overwrite:
                fail()
            return original_write(path, data, label, overwrite=overwrite)

        monkeypatch.setattr(project_manager, "_write_json_object", fail_link)

    with pytest.raises(project_manager.OMIGuidedCreationError) as exc_info:
        project_manager.create_omi_guided_project(
            "Rollback Project", "  exact idea  ", " exact notes "
        )

    result = exc_info.value.result
    assert result["status"] == "failed_rolled_back"
    assert result["failed_step"] == failed_step
    assert result["rollback_attempted"] is True
    assert result["rollback_succeeded"] is True
    assert result["title"] == "Rollback Project"
    assert result["raw_idea"] == "  exact idea  "
    assert result["setup_notes"] == " exact notes "
    assert not (projects_root / "rollback-project").exists()


def test_rollback_never_deletes_preexisting_collision_target(
    projects_root, monkeypatch
):
    existing = projects_root / "collision"
    existing.mkdir()
    marker = existing / "keep.txt"
    marker.write_text("preserve", encoding="utf-8")

    def fail(*args, **kwargs):
        raise OSError("injected note failure")

    monkeypatch.setattr(project_manager, "save_note", fail)
    with pytest.raises(project_manager.OMIGuidedCreationError) as exc_info:
        project_manager.create_omi_guided_project("Collision", "Owner idea", "")

    assert exc_info.value.result["project_id"] == "collision-2"
    assert marker.read_text(encoding="utf-8") == "preserve"
    assert existing.is_dir()
    assert not (projects_root / "collision-2").exists()


def test_rollback_failure_reports_recovery_required_and_retains_values(
    projects_root, monkeypatch
):
    def fail_note(*args, **kwargs):
        raise OSError("private disk detail")

    def fail_cleanup(*args, **kwargs):
        raise OSError("private cleanup detail")

    monkeypatch.setattr(project_manager, "save_note", fail_note)
    monkeypatch.setattr(project_manager.shutil, "rmtree", fail_cleanup)
    payload = {
        "title": "Recovery Project",
        "raw_idea": "  retain idea\r\n",
        "setup_notes": " retain notes ",
    }

    response = main.post_omi_guided_project(SimpleNamespace(**payload))

    assert response.status_code == 500
    result = json.loads(response.body)
    assert result["status"] == "recovery_required"
    assert result["project_id"] == "recovery-project"
    assert result["failed_step"] == "persist_setup_note"
    assert result["rollback_attempted"] is True
    assert result["rollback_succeeded"] is False
    assert result["title"] == payload["title"]
    assert result["raw_idea"] == payload["raw_idea"]
    assert result["setup_notes"] == payload["setup_notes"]
    assert "private" not in result["message"]
    assert str(projects_root) not in response.body.decode()
    assert (projects_root / "recovery-project").is_dir()
