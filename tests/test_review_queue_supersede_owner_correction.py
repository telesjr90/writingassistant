"""T011E owner-controlled supersede and correction lifecycle coverage."""

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
SOURCE_CANDIDATE_ID = "core_candidate_superseded_source_001"
SOURCE_QUEUE_ENTRY_ID = "review_queue_entry_superseded_source_001"
TARGET_CANDIDATE_ID = "core_candidate_superseding_target_001"
TARGET_QUEUE_ENTRY_ID = "review_queue_entry_superseding_target_001"
NOW = "2026-08-09T20:00:00Z"
OWNER_CORRECTION = "  Owner correction: Café e\u0301 remains exact.\n"


def candidate(
    candidate_id: str,
    source_document_id: str,
    *,
    project_id: str = PROJECT_ID,
    candidate_type: str = "character_candidate",
) -> dict:
    target_category = (
        "characters" if candidate_type == "character_candidate" else "timeline"
    )
    locator = {
        "project_id": project_id,
        "source_document_type": "scene",
        "source_document_id": source_document_id,
    }
    return candidate_record.validate_candidate_record(
        {
            "candidate_id": candidate_id,
            "project_id": project_id,
            "candidate_type": candidate_type,
            "status": "candidate",
            "target_category": target_category,
            "source_locator": locator,
            "evidence": [
                {
                    "evidence_id": f"evidence_{candidate_id}",
                    "source_locator": locator,
                    "summary": "Evidence remains attached to this candidate.",
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


def queue_entry(candidate_value: dict, queue_entry_id: str, **overrides) -> dict:
    entry = candidate_review_gate.build_review_queue_entry(
        candidate_value, project_id=candidate_value["project_id"]
    )
    entry.update(
        queue_entry_id=queue_entry_id,
        review_status="pending",
        lifecycle_state="owner_review_pending",
        review_version=0,
        evidence_summary="Retained evidence summary",
        evidence_refs=[f"evidence_{candidate_value['candidate_id']}"],
        provenance_summary="fixture_orchestrator",
        provenance_refs=["fixture_orchestrator"],
    )
    entry.update(overrides)
    return review_queue_storage.validate_review_queue_entry(entry)


def command(action: str, **overrides) -> dict:
    value = {
        "action_type": action,
        "queue_entry_id": SOURCE_QUEUE_ENTRY_ID,
        "candidate_id": SOURCE_CANDIDATE_ID,
        "actor": "owner-reviewed",
        "owner_confirmed": True,
        "preserve_candidate_linkage": True,
        "preserve_evidence_provenance": True,
        "idempotency_key": str(uuid.uuid4()),
        "expected_current_review_status": "pending",
        "expected_current_version": 0,
        "owner_note": "Owner records bounded review metadata only.",
        "rationale": "The owner explicitly selected this lifecycle action.",
    }
    if action == "mark_superseded":
        value.update(
            superseded_by_candidate_id=TARGET_CANDIDATE_ID,
            superseding_target_queue_entry_id=TARGET_QUEUE_ENTRY_ID,
            superseding_target_expected_review_status="pending",
            superseding_target_expected_version=0,
        )
    elif action == "record_owner_authored_correction":
        value["owner_authored_correction"] = OWNER_CORRECTION
    value.update(overrides)
    return value


@pytest.fixture
def review_project(tmp_path: Path) -> tuple[Path, Path]:
    projects = tmp_path / "projects"
    project_manager.create_project("Example", projects_dir=projects)
    project_dir = (projects / PROJECT_ID).resolve()
    source = candidate(SOURCE_CANDIDATE_ID, "scene_001")
    target = candidate(TARGET_CANDIDATE_ID, "scene_002")
    candidate_persistence.write_candidate_record(project_dir, source)
    candidate_persistence.write_candidate_record(project_dir, target)
    review_queue_storage.write_review_queue_entry(
        queue_entry(source, SOURCE_QUEUE_ENTRY_ID), project_dir=project_dir
    )
    review_queue_storage.write_review_queue_entry(
        queue_entry(target, TARGET_QUEUE_ENTRY_ID), project_dir=project_dir
    )
    runtime = tmp_path / "runtime"
    runtime.mkdir(mode=0o700)
    return project_dir, runtime


def execute(value: dict, roots: tuple[Path, Path]) -> dict:
    return review_api.execute_review_action_command(
        value,
        project_id=PROJECT_ID,
        queue_entry_id=SOURCE_QUEUE_ENTRY_ID,
        project_dir=roots[0],
        trusted_runtime_dir=roots[1],
    )


def snapshot(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file()
    }


def assert_non_canon_safety(response: dict) -> None:
    workflow = response["review_workflow_state"]
    assert workflow["is_canon"] is False
    assert workflow["candidate_record_mutation_performed"] is False
    assert workflow["target_candidate_mutation_performed"] is False
    assert workflow["source_candidate_deleted"] is False
    assert workflow["content_merge_performed"] is False
    assert workflow["content_split_performed"] is False
    assert workflow["promotion_created"] is False
    assert workflow["apply_promotion_performed"] is False
    assert workflow["memory_canon_mutation_performed"] is False
    assert workflow["project_truth_mutation_performed"] is False
    assert workflow["runtime_extraction_performed"] is False
    assert workflow["model_call_performed"] is False
    assert workflow["generated_prose_performed"] is False


def test_supersede_persists_audited_linkage_without_mutating_candidates_or_target(
    review_project,
):
    project_dir, _ = review_project
    source_candidate_path = candidate_storage.candidate_record_path(
        project_dir, SOURCE_CANDIDATE_ID
    )
    target_candidate_path = candidate_storage.candidate_record_path(
        project_dir, TARGET_CANDIDATE_ID
    )
    target_queue_path = review_queue_storage.review_queue_entry_path(
        project_dir, TARGET_QUEUE_ENTRY_ID
    )
    preserved = {
        "source": source_candidate_path.read_bytes(),
        "target": target_candidate_path.read_bytes(),
        "target_queue": target_queue_path.read_bytes(),
    }

    response = execute(command("mark_superseded"), review_project)
    persisted = review_queue_storage.read_review_queue_entry(
        SOURCE_QUEUE_ENTRY_ID, project_dir=project_dir
    )
    chain = review_action_events.scan_review_action_event_chain(
        project_dir=project_dir,
        project_id=PROJECT_ID,
        queue_entry_id=SOURCE_QUEUE_ENTRY_ID,
    )

    assert response["review_status"] == "superseded"
    assert response["lifecycle_state"] == "superseded_candidate"
    assert response["superseded_by_candidate_id"] == TARGET_CANDIDATE_ID
    assert response["superseding_target_queue_entry_id"] == TARGET_QUEUE_ENTRY_ID
    assert persisted["superseding_target_review_status"] == "pending"
    assert persisted["superseding_target_lifecycle_state"] == "owner_review_pending"
    assert persisted["superseding_target_review_version"] == 0
    assert review_api._decode_intent_target(chain[0]) == persisted
    assert chain[0]["action_command"] == "mark_superseded"
    assert chain[0]["candidate_not_mutated"] is True
    assert chain[0]["evidence_provenance_preserved"] is True
    assert response["review_workflow_state"]["supersede_scope"] == (
        "review_lifecycle_metadata_only"
    )
    assert response["review_workflow_state"][
        "owner_authored_correction_performed"
    ] is False
    assert_non_canon_safety(response)
    assert source_candidate_path.read_bytes() == preserved["source"]
    assert target_candidate_path.read_bytes() == preserved["target"]
    assert target_queue_path.read_bytes() == preserved["target_queue"]


def test_owner_correction_preserves_exact_owner_text_as_review_metadata_only(
    review_project,
):
    project_dir, _ = review_project
    candidate_path = candidate_storage.candidate_record_path(
        project_dir, SOURCE_CANDIDATE_ID
    )
    candidate_before = candidate_path.read_bytes()
    source_before = review_queue_storage.read_review_queue_entry(
        SOURCE_QUEUE_ENTRY_ID, project_dir=project_dir
    )

    response = execute(command("record_owner_authored_correction"), review_project)
    persisted = review_queue_storage.read_review_queue_entry(
        SOURCE_QUEUE_ENTRY_ID, project_dir=project_dir
    )

    assert response["review_status"] == "correction_recorded"
    assert response["lifecycle_state"] == "owner_authored_correction_recorded"
    assert response["owner_authored_correction"] == OWNER_CORRECTION
    assert persisted["owner_authored_correction"] == OWNER_CORRECTION
    assert persisted["source_locator"] == source_before["source_locator"]
    assert persisted["evidence_refs"] == source_before["evidence_refs"]
    assert persisted["provenance_refs"] == source_before["provenance_refs"]
    workflow = response["review_workflow_state"]
    assert workflow["owner_authored_correction_performed"] is True
    assert workflow["owner_authored_correction_scope"] == (
        "review_lifecycle_metadata_only"
    )
    assert_non_canon_safety(response)
    assert candidate_path.read_bytes() == candidate_before


@pytest.mark.parametrize(
    "action", ("mark_superseded", "record_owner_authored_correction")
)
def test_exact_replay_and_conflicting_terminal_action_are_write_free(
    review_project, action
):
    request = command(action)
    first = execute(request, review_project)
    before_replay = snapshot(review_project[0])
    replay = execute(request, review_project)
    assert replay | {"replay": False} == first
    assert snapshot(review_project[0]) == before_replay

    conflict = command(
        "record_owner_authored_correction"
        if action == "mark_superseded"
        else "mark_superseded",
        expected_current_review_status=first["review_status"],
        expected_current_version=1,
    )
    before_conflict = snapshot(review_project[0])
    with pytest.raises(review_api.ReviewActionUnprocessable) as raised:
        execute(conflict, review_project)
    assert raised.value.payload["error_code"] == "REVIEW_ACTION_INVALID_TRANSITION"
    assert snapshot(review_project[0]) == before_conflict


@pytest.mark.parametrize(
    ("overrides", "error_type", "error_code"),
    (
        (
            {"superseding_target_queue_entry_id": "missing_target"},
            review_api.ReviewActionNotFound,
            "REVIEW_ACTION_SUPERSEDING_TARGET_NOT_FOUND",
        ),
        (
            {"superseding_target_expected_version": 1},
            review_api.ReviewActionConflict,
            "REVIEW_ACTION_STALE_SUPERSEDING_TARGET",
        ),
        (
            {"superseding_target_expected_review_status": "approved"},
            review_api.ReviewActionConflict,
            "REVIEW_ACTION_STALE_SUPERSEDING_TARGET",
        ),
    ),
)
def test_supersede_unknown_or_stale_target_is_write_free(
    review_project, overrides, error_type, error_code
):
    before = snapshot(review_project[0])
    with pytest.raises(error_type) as raised:
        execute(command("mark_superseded", **overrides), review_project)
    assert raised.value.payload["error_code"] == error_code
    assert snapshot(review_project[0]) == before


def test_supersede_rejects_target_candidate_mismatch_and_terminal_target(
    review_project,
):
    project_dir, _ = review_project
    before = snapshot(project_dir)
    with pytest.raises(review_api.ReviewActionUnprocessable):
        execute(
            command(
                "mark_superseded",
                superseded_by_candidate_id="core_candidate_unknown_001",
            ),
            review_project,
        )
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
                "mark_superseded",
                superseding_target_expected_review_status="rejected",
                superseding_target_expected_version=1,
            ),
            review_project,
        )
    assert raised.value.payload["error_code"] == (
        "REVIEW_ACTION_SUPERSEDING_TARGET_CONFLICT"
    )
    assert snapshot(project_dir) == before_terminal


@pytest.mark.parametrize(
    ("project_id", "candidate_type"),
    (
        ("other_project", "character_candidate"),
        (PROJECT_ID, "timeline_event_candidate"),
    ),
)
def test_supersede_rejects_cross_project_or_cross_type_target_without_writes(
    review_project, project_id, candidate_type
):
    project_dir, _ = review_project
    invalid_target = candidate(
        TARGET_CANDIDATE_ID,
        "scene_002",
        project_id=project_id,
        candidate_type=candidate_type,
    )
    candidate_persistence.write_candidate_record(project_dir, invalid_target)
    review_queue_storage.replace_review_queue_entry_atomic(
        queue_entry(invalid_target, TARGET_QUEUE_ENTRY_ID),
        project_dir=project_dir,
    )
    before = snapshot(project_dir)
    with pytest.raises(review_api.ReviewActionUnprocessable) as raised:
        execute(command("mark_superseded"), review_project)
    assert raised.value.payload["error_code"] in {
        "REVIEW_ACTION_INVALID_TRANSITION",
        "REVIEW_ACTION_INVALID_SUPERSEDING_TARGET",
    }
    assert snapshot(project_dir) == before


@pytest.mark.parametrize(
    "overrides",
    (
        {"superseded_by_candidate_id": SOURCE_CANDIDATE_ID},
        {"superseding_target_queue_entry_id": SOURCE_QUEUE_ENTRY_ID},
        {"superseding_target_queue_entry_id": "../escape"},
        {"superseding_target_expected_version": True},
    ),
)
def test_supersede_request_rejects_self_unsafe_or_invalid_target(overrides):
    with pytest.raises(review_api.ReviewActionUnprocessable):
        review_api.validate_review_action_command_request(
            command("mark_superseded", **overrides),
            project_id=PROJECT_ID,
            queue_entry_id=SOURCE_QUEUE_ENTRY_ID,
        )


@pytest.mark.parametrize(
    "correction", (None, "", "   ", "x" * 10_001, "bad\ud800")
)
def test_owner_correction_rejects_missing_empty_oversized_or_invalid_text(correction):
    with pytest.raises(review_api.ReviewActionUnprocessable):
        review_api.validate_review_action_command_request(
            command(
                "record_owner_authored_correction",
                owner_authored_correction=correction,
            ),
            project_id=PROJECT_ID,
            queue_entry_id=SOURCE_QUEUE_ENTRY_ID,
        )


@pytest.mark.parametrize("target_status", ("superseded", "correction_recorded"))
def test_generic_status_command_cannot_create_t011e_states(target_status):
    request = command(
        "record_owner_authored_correction",
        action_type="set_review_status",
        target_review_status=target_status,
    )
    with pytest.raises(review_api.ReviewActionUnprocessable):
        review_api.validate_review_action_command_request(
            request,
            project_id=PROJECT_ID,
            queue_entry_id=SOURCE_QUEUE_ENTRY_ID,
        )
