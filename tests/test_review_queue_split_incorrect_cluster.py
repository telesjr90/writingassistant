"""T011C owner-controlled split-incorrect-cluster lifecycle coverage."""

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
CANDIDATE_ID = "core_candidate_incorrect_cluster_001"
QUEUE_ENTRY_ID = "review_queue_entry_incorrect_cluster_001"
NOW = "2026-08-09T20:00:00Z"


def candidate() -> dict:
    locator = {
        "project_id": PROJECT_ID,
        "source_document_type": "scene",
        "source_document_id": "scene_001",
    }
    return candidate_record.validate_candidate_record(
        {
            "candidate_id": CANDIDATE_ID,
            "project_id": PROJECT_ID,
            "candidate_type": "character_candidate",
            "status": "candidate",
            "target_category": "characters",
            "source_locator": locator,
            "evidence": [
                {
                    "evidence_id": "evidence_cluster_001",
                    "source_locator": locator,
                    "summary": "Evidence retained with the source cluster.",
                    "confidence": 0.4,
                }
            ],
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


def command(**overrides) -> dict:
    value = {
        "action_type": "mark_split_required",
        "queue_entry_id": QUEUE_ENTRY_ID,
        "candidate_id": CANDIDATE_ID,
        "actor": "owner-reviewed",
        "owner_confirmed": True,
        "preserve_candidate_linkage": True,
        "preserve_evidence_provenance": True,
        "idempotency_key": str(uuid.uuid4()),
        "expected_current_review_status": "pending",
        "expected_current_version": 0,
        "owner_note": "Owner marks this incorrect cluster for a later split.",
        "rationale": "The evidence contains two independently reviewable claims.",
    }
    value.update(overrides)
    return value


@pytest.fixture
def split_project(tmp_path: Path) -> tuple[Path, Path]:
    projects = tmp_path / "projects"
    project_manager.create_project("Example", projects_dir=projects)
    project_dir = (projects / PROJECT_ID).resolve()
    candidate_value = candidate()
    candidate_persistence.write_candidate_record(project_dir, candidate_value)
    entry = candidate_review_gate.build_review_queue_entry(
        candidate_value, project_id=PROJECT_ID
    )
    entry.update(
        queue_entry_id=QUEUE_ENTRY_ID,
        review_status="pending",
        lifecycle_state="owner_review_pending",
        review_version=0,
        evidence_summary="One retained evidence item",
        evidence_refs=["evidence_cluster_001"],
        provenance_summary="fixture_orchestrator",
        provenance_refs=["fixture_orchestrator"],
    )
    review_queue_storage.write_review_queue_entry(entry, project_dir=project_dir)
    runtime = tmp_path / "runtime"
    runtime.mkdir(mode=0o700)
    return project_dir, runtime


def execute(value: dict, roots: tuple[Path, Path]) -> dict:
    return review_api.execute_review_action_command(
        value,
        project_id=PROJECT_ID,
        queue_entry_id=QUEUE_ENTRY_ID,
        project_dir=roots[0],
        trusted_runtime_dir=roots[1],
    )


def snapshot(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file()
    }


def test_split_required_persists_only_audited_review_metadata(split_project):
    project_dir, _ = split_project
    candidate_path = candidate_storage.candidate_record_path(project_dir, CANDIDATE_ID)
    candidate_before = candidate_path.read_bytes()

    response = execute(command(), split_project)
    persisted = review_queue_storage.read_review_queue_entry(
        QUEUE_ENTRY_ID, project_dir=project_dir
    )
    chain = review_action_events.scan_review_action_event_chain(
        project_dir=project_dir,
        project_id=PROJECT_ID,
        queue_entry_id=QUEUE_ENTRY_ID,
    )

    assert response["review_status"] == "split_required"
    assert response["lifecycle_state"] == "incorrect_cluster_split_required"
    assert response["owner_review_completed"] is True
    assert response["owner_note"] == command()["owner_note"]
    assert response["rationale"] == command()["rationale"]
    assert review_api._decode_intent_target(chain[0]) == persisted
    assert chain[0]["action_command"] == "mark_split_required"
    assert chain[0]["evidence_provenance_preserved"] is True
    assert chain[0]["candidate_not_mutated"] is True
    workflow = response["review_workflow_state"]
    assert workflow["split_scope"] == "review_lifecycle_metadata_only"
    assert workflow["is_canon"] is False
    assert workflow["candidate_record_mutation_performed"] is False
    assert workflow["source_candidate_deleted"] is False
    assert workflow["content_split_performed"] is False
    assert workflow["split_target_records_created"] is False
    assert workflow["promotion_created"] is False
    assert workflow["apply_promotion_performed"] is False
    assert workflow["memory_canon_mutation_performed"] is False
    assert workflow["project_truth_mutation_performed"] is False
    assert workflow["generated_prose_performed"] is False
    assert workflow["owner_authored_correction_performed"] is False
    assert candidate_path.read_bytes() == candidate_before
    assert persisted["evidence_refs"] == ["evidence_cluster_001"]
    assert persisted["provenance_refs"] == ["fixture_orchestrator"]
    assert not (project_dir / "writer_assistant" / "approved_memory").exists()
    assert not (project_dir / "writer_assistant" / "promotion_audit").exists()


def test_split_required_exact_replay_and_terminal_conflict(split_project):
    request = command()
    first = execute(request, split_project)
    before_replay = snapshot(split_project[0])
    replay = execute(request, split_project)
    assert replay | {"replay": False} == first
    assert snapshot(split_project[0]) == before_replay

    conflict = command(
        action_type="approve",
        expected_current_review_status="split_required",
        expected_current_version=1,
    )
    before_conflict = snapshot(split_project[0])
    with pytest.raises(review_api.ReviewActionUnprocessable) as raised:
        execute(conflict, split_project)
    assert raised.value.payload["error_code"] == "REVIEW_ACTION_INVALID_TRANSITION"
    assert snapshot(split_project[0]) == before_conflict


def test_split_required_stale_state_is_write_free(split_project):
    before = snapshot(split_project[0])
    with pytest.raises(review_api.ReviewActionConflict) as raised:
        execute(command(expected_current_version=1), split_project)
    assert raised.value.payload["error_code"] == "REVIEW_ACTION_STALE_STATE"
    assert snapshot(split_project[0]) == before


@pytest.mark.parametrize(
    "overrides",
    (
        {"owner_note": ""},
        {"rationale": ""},
        {"duplicate_candidate_ids": ["core_candidate_target_001"]},
        {"split_target_candidate_ids": ["../escape"]},
    ),
)
def test_split_required_rejects_missing_or_target_linkage_fields(overrides):
    with pytest.raises(
        (review_api.ReviewActionForbidden, review_api.ReviewActionUnprocessable)
    ):
        review_api.validate_review_action_command_request(
            command(**overrides),
            project_id=PROJECT_ID,
            queue_entry_id=QUEUE_ENTRY_ID,
        )


def test_generic_status_command_cannot_mark_split_required():
    request = command(
        action_type="set_review_status",
        target_review_status="split_required",
    )
    with pytest.raises(review_api.ReviewActionUnprocessable):
        review_api.validate_review_action_command_request(
            request,
            project_id=PROJECT_ID,
            queue_entry_id=QUEUE_ENTRY_ID,
        )
