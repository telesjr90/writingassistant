"""Read-only review queue API contract including persisted review support fields."""

from __future__ import annotations

from pathlib import Path

import pytest

from backend import project_manager, review_api
from backend.story_knowledge import (
    candidate_record,
    candidate_review_gate,
    review_action_events,
    review_queue_storage,
)


PROJECT_ID = "example"
CANDIDATE_RECORD_ID = "core_candidate_readonly_001"
QUEUE_ENTRY_ID = "review_queue_entry_readonly_001"
NOW = "2026-08-09T20:00:00Z"
EXPECTED_ENTRY_FIELDS = {
    "queue_entry_id",
    "project_id",
    "candidate_record_id",
    "candidate_type",
    "target_category",
    "review_status",
    "lifecycle_state",
    "confidence",
    "uncertainty_flags",
    "normalization_status",
    "human_review_required",
    "evidence_summary",
    "evidence_refs",
    "provenance_summary",
    "provenance_refs",
    "source_document",
    "source_locator",
    "raw_output_refs",
    "created_at",
    "updated_at",
    "review_version",
    "owner_note",
    "owner_review_completed",
    "owner_reviewed_at",
}


def sample_candidate() -> dict:
    return candidate_record.validate_candidate_record(
        {
            "candidate_id": CANDIDATE_RECORD_ID,
            "project_id": PROJECT_ID,
            "candidate_type": "character_candidate",
            "status": "candidate",
            "target_category": "characters",
            "source_locator": {
                "project_id": PROJECT_ID,
                "source_document_type": "scene",
                "source_document_id": "scene_001",
                "section_id": None,
                "chapter_id": None,
                "scene_id": "scene_001",
                "line_start": None,
                "line_end": None,
                "char_start": None,
                "char_end": None,
                "source_hash": None,
            },
            "evidence": [],
            "provenance": {
                "origin": "extractor",
                "extraction_method": "fixture_orchestrator",
                "timestamp": NOW,
                "human_review_required": True,
            },
            "owner_decision": "undecided",
            "destination": "omi_candidate_only",
            "confidence": 0.4,
            "created_at": NOW,
            "updated_at": NOW,
        }
    )


def sample_entry() -> dict:
    entry = candidate_review_gate.build_review_queue_entry(
        sample_candidate(), project_id=PROJECT_ID
    )
    entry.update(
        queue_entry_id=QUEUE_ENTRY_ID,
        review_version=3,
        owner_note="Owner-authored review note.",
        owner_review_completed=True,
        owner_reviewed_at=NOW,
    )
    return review_queue_storage.validate_review_queue_entry(entry)


def assert_entry_preserves_review_support(entry: dict) -> None:
    assert EXPECTED_ENTRY_FIELDS <= set(entry)
    assert entry["review_version"] == 3
    assert entry["owner_note"] == "Owner-authored review note."
    assert entry["owner_review_completed"] is True
    assert entry["owner_reviewed_at"] == NOW
    assert entry["evidence_refs"] == sample_entry()["evidence_refs"]
    assert entry["provenance_refs"] == sample_entry()["provenance_refs"]


def snapshot(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file()
    }


@pytest.fixture
def persisted_project(tmp_path: Path) -> Path:
    projects = tmp_path / "projects"
    project_manager.create_project("Example", projects_dir=projects)
    project_dir = (projects / PROJECT_ID).resolve()
    review_queue_storage.write_review_queue_entry(
        sample_entry(), project_dir=project_dir
    )
    return project_dir


@pytest.fixture
def readonly_spies(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("read-only API attempted event scan, recovery, or write")

    monkeypatch.setattr(review_action_events, "scan_review_action_event_chain", forbidden)
    monkeypatch.setattr(review_action_events, "publish_review_action_event", forbidden)
    monkeypatch.setattr(review_queue_storage, "replace_review_queue_entry_atomic", forbidden)


def test_real_persisted_get_returns_extended_fields_without_mutation(
    persisted_project: Path, readonly_spies
) -> None:
    before = snapshot(persisted_project)
    response = review_api.get_review_queue_entry_readonly(
        {"project_id": PROJECT_ID, "queue_entry_id": QUEUE_ENTRY_ID},
        project_dir=persisted_project,
    )
    assert_entry_preserves_review_support(response["entry"])
    assert response["metadata"]["storage_consulted"] is True
    assert snapshot(persisted_project) == before


def test_list_get_index_and_summary_remain_observational(
    persisted_project: Path, readonly_spies
) -> None:
    before = snapshot(persisted_project)
    list_response = review_api.list_review_queue_entries_readonly(
        {"project_id": PROJECT_ID}, project_dir=persisted_project
    )
    get_response = review_api.get_review_queue_entry_readonly(
        {"project_id": PROJECT_ID, "queue_entry_id": QUEUE_ENTRY_ID},
        project_dir=persisted_project,
    )
    index_response = review_api.get_review_queue_index_readonly(
        {"project_id": PROJECT_ID}, project_dir=persisted_project
    )
    summary_response = review_api.get_review_queue_summary_readonly(
        {"project_id": PROJECT_ID}, project_dir=persisted_project
    )
    assert_entry_preserves_review_support(list_response["entries"][0])
    assert_entry_preserves_review_support(get_response["entry"])
    assert index_response["summary"]["entry_count"] == 1
    assert summary_response["summary"]["entry_count"] == 1
    assert snapshot(persisted_project) == before


def test_legacy_get_normalizes_review_support_without_writing(
    persisted_project: Path, readonly_spies
) -> None:
    entry_path = review_queue_storage.review_queue_entry_path(
        persisted_project, QUEUE_ENTRY_ID
    )
    legacy = sample_entry()
    for field in (
        "review_version",
        "owner_note",
        "owner_review_completed",
        "owner_reviewed_at",
    ):
        legacy.pop(field, None)
    import json

    entry_path.write_text(json.dumps(legacy, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    before = entry_path.read_bytes()
    response = review_api.get_review_queue_entry_readonly(
        {"project_id": PROJECT_ID, "queue_entry_id": QUEUE_ENTRY_ID},
        project_dir=persisted_project,
    )
    assert response["entry"]["review_version"] == 0
    assert response["entry"]["owner_note"] is None
    assert response["entry"]["owner_review_completed"] is False
    assert response["entry"]["owner_reviewed_at"] is None
    assert entry_path.read_bytes() == before


def test_missing_queue_is_an_observational_empty_or_warning_response(tmp_path: Path) -> None:
    missing = tmp_path / "missing-project"
    response = review_api.list_review_queue_entries_readonly(
        {"project_id": PROJECT_ID}, project_dir=missing
    )
    assert response["entries"] == []
    assert not missing.exists()
