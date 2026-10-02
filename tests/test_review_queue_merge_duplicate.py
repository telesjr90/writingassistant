"""T011B owner-controlled merge-duplicate lifecycle coverage."""

from __future__ import annotations

import uuid
from pathlib import Path

import pytest

from backend import project_manager, review_api
from backend.story_knowledge import (
    candidate_persistence,
    candidate_record,
    candidate_review_gate,
    candidate_storage,
    review_action_events,
    review_queue_storage,
)


PROJECT_ID = "example"
SOURCE_CANDIDATE_ID = "core_candidate_duplicate_source_001"
SOURCE_QUEUE_ENTRY_ID = "review_queue_entry_duplicate_source_001"
TARGET_CANDIDATE_ID = "core_candidate_duplicate_target_001"
TARGET_QUEUE_ENTRY_ID = "review_queue_entry_duplicate_target_001"
NOW = "2026-08-09T20:00:00Z"


def candidate(candidate_id: str, source_document_id: str, *, project_id=PROJECT_ID):
    return candidate_record.validate_candidate_record(
        {
            "candidate_id": candidate_id,
            "project_id": project_id,
            "candidate_type": "character_candidate",
            "status": "candidate",
            "target_category": "characters",
            "source_locator": {
                "project_id": project_id,
                "source_document_type": "scene",
                "source_document_id": source_document_id,
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


def queue_entry(candidate_value: dict, queue_entry_id: str, **overrides):
    entry = candidate_review_gate.build_review_queue_entry(
        candidate_value, project_id=candidate_value["project_id"]
    )
    entry.update(
        queue_entry_id=queue_entry_id,
        review_status="pending",
        lifecycle_state="owner_review_pending",
        review_version=0,
        evidence_summary="Evidence summary",
        evidence_refs=["evidence_001"],
        provenance_summary="Fixture provenance",
        provenance_refs=["fixture_orchestrator"],
    )
    entry.update(overrides)
    return review_queue_storage.validate_review_queue_entry(entry)


def command(**overrides):
    value = {
        "action_type": "mark_duplicate",
        "queue_entry_id": SOURCE_QUEUE_ENTRY_ID,
        "candidate_id": SOURCE_CANDIDATE_ID,
        "actor": "owner-reviewed",
        "owner_confirmed": True,
        "preserve_candidate_linkage": True,
        "preserve_evidence_provenance": True,
        "idempotency_key": str(uuid.uuid4()),
        "expected_current_review_status": "pending",
        "expected_current_version": 0,
        "owner_note": "Owner marks this candidate as a duplicate.",
        "rationale": "The evidence identifies the same analytical entity.",
        "duplicate_candidate_ids": [TARGET_CANDIDATE_ID],
        "duplicate_target_queue_entry_id": TARGET_QUEUE_ENTRY_ID,
        "duplicate_target_expected_review_status": "pending",
        "duplicate_target_expected_version": 0,
    }
    value.update(overrides)
    return value


@pytest.fixture
def duplicate_project(tmp_path: Path):
    projects = tmp_path / "projects"
    project_manager.create_project("Example", projects_dir=projects)
    project_dir = (projects / PROJECT_ID).resolve()
    source_candidate = candidate(SOURCE_CANDIDATE_ID, "scene_001")
    target_candidate = candidate(TARGET_CANDIDATE_ID, "scene_002")
    candidate_persistence.write_candidate_record(project_dir, source_candidate)
    candidate_persistence.write_candidate_record(project_dir, target_candidate)
    review_queue_storage.write_review_queue_entry(
        queue_entry(source_candidate, SOURCE_QUEUE_ENTRY_ID),
        project_dir=project_dir,
    )
    review_queue_storage.write_review_queue_entry(
        queue_entry(target_candidate, TARGET_QUEUE_ENTRY_ID),
        project_dir=project_dir,
    )
    runtime = tmp_path / "runtime"
    runtime.mkdir(mode=0o700)
    return project_dir, runtime


def execute(value: dict, roots):
    return review_api.execute_review_action_command(
        value,
        project_id=PROJECT_ID,
        queue_entry_id=SOURCE_QUEUE_ENTRY_ID,
        project_dir=roots[0],
        trusted_runtime_dir=roots[1],
    )


def snapshot(root: Path):
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file()
    }


def test_mark_duplicate_persists_only_audited_review_linkage(duplicate_project):
    project_dir, _ = duplicate_project
    source_candidate_path = candidate_storage.candidate_record_path(
        project_dir, SOURCE_CANDIDATE_ID
    )
    target_candidate_path = candidate_storage.candidate_record_path(
        project_dir, TARGET_CANDIDATE_ID
    )
    target_queue_path = review_queue_storage.review_queue_entry_path(
        project_dir, TARGET_QUEUE_ENTRY_ID
    )
    preserved_bytes = {
        "source_candidate": source_candidate_path.read_bytes(),
        "target_candidate": target_candidate_path.read_bytes(),
        "target_queue": target_queue_path.read_bytes(),
    }

    response = execute(command(), duplicate_project)
    persisted = review_queue_storage.read_review_queue_entry(
        SOURCE_QUEUE_ENTRY_ID, project_dir=project_dir
    )
    chain = review_action_events.scan_review_action_event_chain(
        project_dir=project_dir,
        project_id=PROJECT_ID,
        queue_entry_id=SOURCE_QUEUE_ENTRY_ID,
    )
    audited_target = review_api._decode_intent_target(chain[0])

    assert response["review_status"] == "duplicate"
    assert response["lifecycle_state"] == "duplicate_candidate"
    assert response["owner_review_completed"] is True
    assert response["duplicate_candidate_ids"] == [TARGET_CANDIDATE_ID]
    assert response["duplicate_target_queue_entry_id"] == TARGET_QUEUE_ENTRY_ID
    assert persisted["duplicate_target_review_status"] == "pending"
    assert persisted["duplicate_target_lifecycle_state"] == "owner_review_pending"
    assert persisted["duplicate_target_review_version"] == 0
    assert audited_target == persisted
    assert chain[0]["action_command"] == "mark_duplicate"
    assert chain[0]["evidence_provenance_preserved"] is True
    assert chain[0]["candidate_not_mutated"] is True
    assert chain[0]["no_promotion_requested"] is True
    assert chain[0]["no_memory_canon_mutation_requested"] is True
    assert response["review_workflow_state"]["is_canon"] is False
    assert response["review_workflow_state"]["source_candidate_deleted"] is False
    assert response["review_workflow_state"]["content_merge_performed"] is False
    assert response["review_workflow_state"]["promotion_created"] is False
    assert response["review_workflow_state"]["apply_promotion_performed"] is False
    assert source_candidate_path.read_bytes() == preserved_bytes["source_candidate"]
    assert target_candidate_path.read_bytes() == preserved_bytes["target_candidate"]
    assert target_queue_path.read_bytes() == preserved_bytes["target_queue"]
    assert not (project_dir / "writer_assistant" / "approved_memory").exists()
    assert not (project_dir / "writer_assistant" / "promotion_audit").exists()


def test_mark_duplicate_exact_replay_is_deterministic_and_new_action_fails_closed(
    duplicate_project,
):
    request = command()
    first = execute(request, duplicate_project)
    before_replay = snapshot(duplicate_project[0])
    replay = execute(request, duplicate_project)
    assert replay | {"replay": False} == first
    assert snapshot(duplicate_project[0]) == before_replay

    conflicting = command(
        expected_current_review_status="duplicate",
        expected_current_version=1,
    )
    before_conflict = snapshot(duplicate_project[0])
    with pytest.raises(review_api.ReviewActionUnprocessable) as raised:
        execute(conflicting, duplicate_project)
    assert raised.value.payload["error_code"] == "REVIEW_ACTION_INVALID_TRANSITION"
    assert snapshot(duplicate_project[0]) == before_conflict


@pytest.mark.parametrize(
    ("overrides", "error_type", "error_code"),
    (
        (
            {"duplicate_target_queue_entry_id": "missing_target"},
            review_api.ReviewActionNotFound,
            "REVIEW_ACTION_DUPLICATE_TARGET_NOT_FOUND",
        ),
        (
            {"duplicate_target_expected_version": 1},
            review_api.ReviewActionConflict,
            "REVIEW_ACTION_STALE_DUPLICATE_TARGET",
        ),
        (
            {"duplicate_target_expected_review_status": "approved"},
            review_api.ReviewActionConflict,
            "REVIEW_ACTION_STALE_DUPLICATE_TARGET",
        ),
    ),
)
def test_mark_duplicate_unknown_or_stale_target_is_write_free(
    duplicate_project, overrides, error_type, error_code
):
    before = snapshot(duplicate_project[0])
    with pytest.raises(error_type) as raised:
        execute(command(**overrides), duplicate_project)
    assert raised.value.payload["error_code"] == error_code
    assert snapshot(duplicate_project[0]) == before


def test_mark_duplicate_rejects_target_candidate_mismatch_and_terminal_target(
    duplicate_project,
):
    project_dir, _ = duplicate_project
    mismatch = command(duplicate_candidate_ids=["core_candidate_unknown_001"])
    before = snapshot(project_dir)
    with pytest.raises(review_api.ReviewActionUnprocessable):
        execute(mismatch, duplicate_project)
    assert snapshot(project_dir) == before

    target = review_queue_storage.read_review_queue_entry(
        TARGET_QUEUE_ENTRY_ID, project_dir=project_dir
    )
    target.update(
        review_status="rejected",
        lifecycle_state="owner_reviewed_rejected",
        review_version=1,
    )
    review_queue_storage.replace_review_queue_entry_atomic(
        target, project_dir=project_dir
    )
    before_terminal = snapshot(project_dir)
    with pytest.raises(review_api.ReviewActionConflict) as raised:
        execute(
            command(
                duplicate_target_expected_review_status="rejected",
                duplicate_target_expected_version=1,
            ),
            duplicate_project,
        )
    assert raised.value.payload["error_code"] == "REVIEW_ACTION_DUPLICATE_TARGET_CONFLICT"
    assert snapshot(project_dir) == before_terminal


def test_mark_duplicate_rejects_cross_project_target_without_writes(
    duplicate_project,
):
    project_dir, _ = duplicate_project
    other_candidate = candidate(
        TARGET_CANDIDATE_ID, "scene_002", project_id="other_project"
    )
    candidate_persistence.write_candidate_record(project_dir, other_candidate)
    review_queue_storage.replace_review_queue_entry_atomic(
        queue_entry(other_candidate, TARGET_QUEUE_ENTRY_ID),
        project_dir=project_dir,
    )
    before = snapshot(project_dir)
    with pytest.raises(review_api.ReviewActionUnprocessable) as raised:
        execute(command(), duplicate_project)
    assert raised.value.payload["error_code"] == "REVIEW_ACTION_INVALID_TRANSITION"
    assert snapshot(project_dir) == before


@pytest.mark.parametrize(
    "overrides",
    (
        {"duplicate_candidate_ids": [SOURCE_CANDIDATE_ID]},
        {"duplicate_target_queue_entry_id": SOURCE_QUEUE_ENTRY_ID},
        {"duplicate_candidate_ids": [TARGET_CANDIDATE_ID, "candidate_other"]},
        {"duplicate_target_queue_entry_id": "../escape"},
        {"duplicate_target_expected_version": True},
    ),
)
def test_mark_duplicate_request_rejects_self_multiple_unsafe_or_invalid_target(
    overrides,
):
    with pytest.raises(review_api.ReviewActionUnprocessable):
        review_api.validate_review_action_command_request(
            command(**overrides),
            project_id=PROJECT_ID,
            queue_entry_id=SOURCE_QUEUE_ENTRY_ID,
        )
