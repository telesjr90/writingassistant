import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend import guardrails, project_manager


REPO_ROOT = Path(__file__).resolve().parents[1]
PROJECT_NAME = "ember"
BLOCKED_PROSE_VALUES = [
    "scene_prose",
    "dialogue",
    "rewrite",
    "continuation",
    "chapter",
    "final_story_text",
    "polished_prose",
    "style_imitation",
]


def _write_project_truth_files(root: Path, project_name: str = PROJECT_NAME) -> dict[Path, str]:
    project_dir = root / project_name
    scenes_dir = project_dir / "scenes"
    scenes_dir.mkdir(parents=True)
    files = {
        project_dir / "project.json": '{"title": "Fixture"}\n',
        project_dir / "bible.json": '{"characters": []}\n',
        project_dir / "storyform.json": '{"schema_version": "ncp-0.1"}\n',
        project_dir / "owner_memory.json": '{"notes": []}\n',
        scenes_dir / "scene_001.md": "Owner-authored fixture text.",
    }

    for path, content in files.items():
        path.write_text(content, encoding="utf-8")

    return files


def _assert_project_truth_unchanged(files: dict[Path, str]) -> None:
    for path, content in files.items():
        assert path.read_text(encoding="utf-8") == content


def _create_candidate(
    candidate_content: dict | None = None,
    destination: str = "planning_notes",
    candidate_type: str = "planning_note",
) -> dict:
    idea = project_manager.create_omi_idea(
        PROJECT_NAME,
        "Owner-authored planning idea.",
    )
    return project_manager.create_omi_candidate(
        PROJECT_NAME,
        idea["idea_id"],
        candidate_type,
        candidate_content or {"summary": "Candidate-only structural planning note."},
        destination,
        evidence=[],
    )


def _approve_candidate(candidate: dict) -> dict:
    reviewed = project_manager.update_omi_candidate_decision(
        PROJECT_NAME,
        candidate["candidate_id"],
        {"decision": "pending"},
        status="owner_review",
    )
    return project_manager.update_omi_candidate_decision(
        PROJECT_NAME,
        reviewed["candidate_id"],
        {"decision": "approve", "approval_confirmed": True},
        status="approved",
    )


def _candidate_path(root: Path, candidate_id: str) -> Path:
    return root / PROJECT_NAME / "omi" / "candidates" / f"{candidate_id}.json"


def _overwrite_candidate(root: Path, candidate: dict) -> None:
    _candidate_path(root, candidate["candidate_id"]).write_text(
        json.dumps(candidate, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _promotion_request(**overrides):
    payload = {
        "final_confirmation": True,
        "target_file": "bible.json",
        "target_path": "bible.json",
    }
    payload.update(overrides)
    return payload


def test_omi_rejects_prose_generation_candidate_types_and_destinations(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)
    files = _write_project_truth_files(tmp_path)
    idea = project_manager.create_omi_idea(PROJECT_NAME, "Keep this candidate-only.")

    for blocked_value in BLOCKED_PROSE_VALUES:
        before_candidates = project_manager.load_omi_index(PROJECT_NAME)["candidate_ids"]

        with pytest.raises(ValueError):
            project_manager.create_omi_candidate(
                PROJECT_NAME,
                idea["idea_id"],
                blocked_value,
                {"summary": "Blocked candidate type."},
                "planning_notes",
            )

        with pytest.raises(ValueError):
            project_manager.create_omi_candidate(
                PROJECT_NAME,
                idea["idea_id"],
                "planning_note",
                {"summary": "Blocked destination."},
                blocked_value,
            )

        assert project_manager.load_omi_index(PROJECT_NAME)["candidate_ids"] == before_candidates

    _assert_project_truth_unchanged(files)


def test_owner_authored_raw_idea_with_command_like_words_is_candidate_only(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)
    files = _write_project_truth_files(tmp_path)
    raw_idea = (
        "Owner planning note uses write, dialogue, chapter, and continue as context words."
    )

    idea = project_manager.create_omi_idea(PROJECT_NAME, raw_idea)

    assert idea["raw_idea"] == raw_idea
    assert idea["status"] == "draft"
    assert guardrails.should_guard_request_field("raw_idea") is False
    assert (tmp_path / PROJECT_NAME / "omi" / "ideas" / f"{idea['idea_id']}.json").exists()
    _assert_project_truth_unchanged(files)


def test_owner_authored_candidate_content_with_craft_terms_is_candidate_only(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)
    files = _write_project_truth_files(tmp_path)
    content = {
        "summary": "Planning note mentions dialogue, chapter, style, and rewrite as context.",
        "fields": ["owner review only"],
    }

    candidate = _create_candidate(
        candidate_content=content,
        destination="project_bible_candidate",
        candidate_type="project_bible_candidate",
    )

    assert candidate["candidate_content"] == content
    assert candidate["destination"] == "project_bible_candidate"
    assert guardrails.should_guard_request_field("planning_notes") is False
    assert project_manager.load_omi_candidate(PROJECT_NAME, candidate["candidate_id"]) == candidate
    _assert_project_truth_unchanged(files)


def test_creating_omi_records_never_silently_promotes_to_project_truth(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)
    files = _write_project_truth_files(tmp_path)

    idea = project_manager.create_omi_idea(PROJECT_NAME, "Candidate-only idea.")
    candidate = project_manager.create_omi_candidate(
        PROJECT_NAME,
        idea["idea_id"],
        "storyform_context_candidate",
        {"summary": "Candidate-only storyform context."},
        "storyform_context_candidate",
        evidence=[{"source": "owner", "note": "review evidence"}],
    )

    assert candidate["status"] == "candidate"
    assert candidate["promotion_status"]["eligible"] is False
    _assert_project_truth_unchanged(files)


def test_promotion_record_creation_is_record_only_and_has_no_apply_route(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)
    files = _write_project_truth_files(tmp_path)
    candidate = _approve_candidate(
        _create_candidate(
            {"summary": "Structured project bible candidate."},
            destination="project_bible_candidate",
            candidate_type="project_bible_candidate",
        )
    )

    promotion = project_manager.create_omi_promotion_record(
        PROJECT_NAME,
        candidate["candidate_id"],
        _promotion_request(),
    )

    assert promotion["source_snapshot"]["candidate_id"] == candidate["candidate_id"]
    assert promotion["status"] == project_manager.OMI_PROMOTION_RECORD_STATUS
    assert promotion["status"] != "promoted"
    assert project_manager.load_omi_index(PROJECT_NAME)["promotion_ids"] == [
        promotion["promotion_id"]
    ]
    assert not hasattr(project_manager, "apply_omi_promotion")
    assert "apply_omi_promotion" not in (REPO_ROOT / "backend" / "main.py").read_text(
        encoding="utf-8"
    )
    _assert_project_truth_unchanged(files)


@pytest.mark.parametrize(
    ("candidate_edit", "payload", "match"),
    [
        ({"status": "candidate"}, {}, "status must be approved"),
        ({"owner_decision": {"decision": "approve", "approval_confirmed": False}}, {}, "approval confirmation"),
        ({"destination": "discard"}, {}, "discard"),
        ({"destination": "scene_prose"}, {}, "allowed destination"),
        ({"provenance": {}}, {}, "provenance"),
        ({"candidate_content": []}, {}, "candidate_content"),
        ({}, {"final_confirmation": False}, "final_confirmation"),
        ({}, {"target_file": None, "target_path": None}, "target_file or target_path"),
        ({}, {"target_file": "../bible.json", "target_path": None}, "target"),
        ({}, {"target_file": "scenes/scene_001.md", "target_path": None}, "target"),
        ({}, {"target_file": "final_story_text", "target_path": None}, "target"),
    ],
)
def test_promotion_gate_blocks_incomplete_or_unsafe_requests(
    tmp_path,
    monkeypatch,
    candidate_edit,
    payload,
    match,
):
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)
    files = _write_project_truth_files(tmp_path)
    candidate = _approve_candidate(
        _create_candidate(
            {"summary": "Structured candidate."},
            destination="project_bible_candidate",
            candidate_type="project_bible_candidate",
        )
    )
    edited_candidate = json.loads(json.dumps(candidate))
    edited_candidate.update(candidate_edit)
    _overwrite_candidate(tmp_path, edited_candidate)
    request = _promotion_request(**payload)
    before_index = project_manager.load_omi_index(PROJECT_NAME)

    with pytest.raises(ValueError, match=match):
        project_manager.create_omi_promotion_record(
            PROJECT_NAME,
            candidate["candidate_id"],
            request,
        )

    assert project_manager.load_omi_index(PROJECT_NAME) == before_index
    assert project_manager.list_omi_promotions(PROJECT_NAME) == []
    _assert_project_truth_unchanged(files)


def test_unknown_candidate_cannot_create_promotion_record(tmp_path, monkeypatch):
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)
    files = _write_project_truth_files(tmp_path)

    with pytest.raises(FileNotFoundError):
        project_manager.create_omi_promotion_record(
            PROJECT_NAME,
            "candidate_missing",
            _promotion_request(),
        )

    _assert_project_truth_unchanged(files)


def test_omi_boundary_helpers_do_not_call_model_paths(tmp_path, monkeypatch):
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)

    def fail_if_called(*args, **kwargs):
        raise AssertionError("OMI boundary tests must not call model paths")

    import backend.analysis_engine as analysis_engine

    monkeypatch.setattr(analysis_engine, "run_story_check", fail_if_called)

    idea = project_manager.create_omi_idea(PROJECT_NAME, "Owner-authored idea.")
    candidate = project_manager.create_omi_candidate(
        PROJECT_NAME,
        idea["idea_id"],
        "planning_note",
        {"summary": "Candidate-only context."},
        "planning_notes",
    )

    assert candidate["idea_id"] == idea["idea_id"]


def test_omi_does_not_read_or_transform_owner_sample_input(tmp_path, monkeypatch):
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)

    def fail_read_text(self, *args, **kwargs):
        if self.name == "owner_sample_input.md":
            raise AssertionError("OMI must not read owner_sample_input.md automatically")
        return original_read_text(self, *args, **kwargs)

    original_read_text = Path.read_text
    monkeypatch.setattr(Path, "read_text", fail_read_text)

    idea = project_manager.create_omi_idea(PROJECT_NAME, "Manual owner input only.")

    assert idea["raw_idea"] == "Manual owner input only."


def test_omi_frontend_boundary_copy_and_no_unsafe_controls():
    source = (REPO_ROOT / "frontend" / "src" / "components" / "OMIPanel.jsx").read_text(
        encoding="utf-8"
    )
    lower_source = source.lower()

    assert "omi stores candidate planning material only" in lower_source
    assert "does not write story prose or change project truth" in lower_source
    assert "promotion record does not change bible, storyform, scenes, or project truth" in lower_source
    assert "create promotion record" in lower_source

    forbidden_ui_phrases = [
        "generate prose",
        "rewrite scene",
        "continue story",
        "polish prose",
        "improve prose",
        "apply to story",
        "write to scene",
    ]
    for phrase in forbidden_ui_phrases:
        assert phrase not in lower_source


def test_omi_path_traversal_is_blocked_for_ideas_candidates_and_promotions(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)
    idea = project_manager.create_omi_idea(PROJECT_NAME, "Safe path test.")
    candidate = project_manager.create_omi_candidate(
        PROJECT_NAME,
        idea["idea_id"],
        "planning_note",
        {"summary": "Safe candidate."},
        "planning_notes",
    )

    with pytest.raises(ValueError):
        project_manager.create_omi_idea("../outside", "unsafe")
    with pytest.raises(ValueError):
        project_manager.load_omi_idea(PROJECT_NAME, "../outside")
    with pytest.raises(ValueError):
        project_manager.load_omi_candidate(PROJECT_NAME, "../outside")
    with pytest.raises(ValueError):
        project_manager.load_omi_promotion(PROJECT_NAME, "../outside")

    loaded_idea = project_manager.load_omi_idea(PROJECT_NAME, idea["idea_id"])
    assert loaded_idea["idea_id"] == idea["idea_id"]
    assert loaded_idea["linked_candidate_ids"] == [candidate["candidate_id"]]
    assert project_manager.load_omi_candidate(PROJECT_NAME, candidate["candidate_id"]) == candidate
