"""T011D owner-controlled rename and source-link correction coverage."""

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
CANDIDATE_ID = "core_candidate_correction_001"
QUEUE_ENTRY_ID = "review_queue_entry_correction_001"
NOW = "2026-08-09T20:00:00Z"
ORIGINAL_LOCATOR = {
    "project_id": PROJECT_ID,
    "source_document_type": "scene",
    "source_document_id": "scene_001",
    "scene_id": "scene_001",
}
CORRECTED_LOCATOR = {
    "project_id": PROJECT_ID,
    "source_document_type": "scene",
    "source_document_id": "scene_002",
    "scene_id": "scene_002",
}


def candidate() -> dict:
    return candidate_record.validate_candidate_record(
        {
            "candidate_id": CANDIDATE_ID,
            "project_id": PROJECT_ID,
            "candidate_type": "character_candidate",
            "status": "candidate",
            "target_category": "characters",
            "source_locator": ORIGINAL_LOCATOR,
            "evidence": [
                {
                    "evidence_id": "evidence_correction_001",
                    "source_locator": ORIGINAL_LOCATOR,
                    "summary": "Original evidence remains immutable.",
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


def command(action: str, **overrides) -> dict:
    value = {
        "action_type": action,
        "queue_entry_id": QUEUE_ENTRY_ID,
        "candidate_id": CANDIDATE_ID,
        "actor": "owner-reviewed",
        "owner_confirmed": True,
        "preserve_candidate_linkage": True,
        "preserve_evidence_provenance": True,
        "idempotency_key": str(uuid.uuid4()),
        "expected_current_review_status": "pending",
        "expected_current_version": 0,
        "owner_note": "Owner records bounded review metadata only.",
        "rationale": "The existing review metadata needs correction.",
    }
    if action == "rename_candidate_metadata":
        value["requested_owner_visible_label"] = "Corrected review label"
    elif action == "record_source_linkage_correction":
        value["requested_source_locator"] = CORRECTED_LOCATOR
    value.update(overrides)
    return value


@pytest.fixture
def correction_project(tmp_path: Path) -> tuple[Path, Path]:
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
        owner_visible_label="Original review label",
        evidence_summary="Original evidence summary",
        evidence_refs=["evidence_correction_001"],
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


def assert_common_safety(response: dict, project_dir: Path, candidate_before: bytes):
    workflow = response["review_workflow_state"]
    assert workflow["is_canon"] is False
    assert workflow["candidate_record_mutation_performed"] is False
    assert workflow["source_candidate_deleted"] is False
    assert workflow["content_merge_performed"] is False
    assert workflow["content_split_performed"] is False
    assert workflow["promotion_created"] is False
    assert workflow["apply_promotion_performed"] is False
    assert workflow["memory_canon_mutation_performed"] is False
    assert workflow["project_truth_mutation_performed"] is False
    assert workflow["generated_prose_performed"] is False
    assert workflow["owner_authored_correction_performed"] is False
    assert workflow["source_document_mutation_performed"] is False
    candidate_path = candidate_storage.candidate_record_path(project_dir, CANDIDATE_ID)
    assert candidate_path.read_bytes() == candidate_before
    assert not (project_dir / "writer_assistant" / "approved_memory").exists()
    assert not (project_dir / "writer_assistant" / "promotion_audit").exists()


def test_rename_updates_only_audited_owner_visible_review_metadata(
    correction_project,
):
    project_dir, _ = correction_project
    candidate_path = candidate_storage.candidate_record_path(project_dir, CANDIDATE_ID)
    candidate_before = candidate_path.read_bytes()
    source_before = review_queue_storage.read_review_queue_entry(
        QUEUE_ENTRY_ID, project_dir=project_dir
    )

    response = execute(command("rename_candidate_metadata"), correction_project)
    persisted = review_queue_storage.read_review_queue_entry(
        QUEUE_ENTRY_ID, project_dir=project_dir
    )
    chain = review_action_events.scan_review_action_event_chain(
        project_dir=project_dir,
        project_id=PROJECT_ID,
        queue_entry_id=QUEUE_ENTRY_ID,
    )

    assert response["review_status"] == "correction_recorded"
    assert response["lifecycle_state"] == "rename_metadata_recorded"
    assert response["owner_visible_label"] == "Corrected review label"
    assert response["original_owner_visible_label"] == "Original review label"
    assert response["requested_owner_visible_label"] == "Corrected review label"
    assert persisted["source_locator"] == source_before["source_locator"]
    assert persisted["evidence_refs"] == source_before["evidence_refs"]
    assert persisted["provenance_refs"] == source_before["provenance_refs"]
    assert review_api._decode_intent_target(chain[0]) == persisted
    assert chain[0]["action_command"] == "rename_candidate_metadata"
    assert chain[0]["candidate_not_mutated"] is True
    assert chain[0]["evidence_provenance_preserved"] is True
    assert response["review_workflow_state"]["rename_scope"] == (
        "review_lifecycle_metadata_only"
    )
    assert_common_safety(response, project_dir, candidate_before)


def test_source_link_correction_records_old_and_requested_values_without_relinking(
    correction_project,
):
    project_dir, _ = correction_project
    candidate_path = candidate_storage.candidate_record_path(project_dir, CANDIDATE_ID)
    candidate_before = candidate_path.read_bytes()
    source_before = review_queue_storage.read_review_queue_entry(
        QUEUE_ENTRY_ID, project_dir=project_dir
    )

    response = execute(
        command("record_source_linkage_correction"), correction_project
    )
    persisted = review_queue_storage.read_review_queue_entry(
        QUEUE_ENTRY_ID, project_dir=project_dir
    )

    assert response["review_status"] == "correction_recorded"
    assert response["lifecycle_state"] == "source_linkage_correction_recorded"
    assert response["original_source_locator"] == ORIGINAL_LOCATOR
    assert response["requested_source_locator"] == CORRECTED_LOCATOR
    assert persisted["source_locator"] == source_before["source_locator"]
    assert persisted["source_document"] == source_before["source_document"]
    assert persisted["evidence_refs"] == source_before["evidence_refs"]
    assert persisted["provenance_refs"] == source_before["provenance_refs"]
    workflow = response["review_workflow_state"]
    assert workflow["source_linkage_correction_scope"] == (
        "review_lifecycle_metadata_only"
    )
    assert workflow["source_linkage_mutation_performed"] is False
    assert_common_safety(response, project_dir, candidate_before)


@pytest.mark.parametrize(
    "action",
    ("rename_candidate_metadata", "record_source_linkage_correction"),
)
def test_correction_exact_replay_and_conflicting_action_fail_closed(
    correction_project, action
):
    request = command(action)
    first = execute(request, correction_project)
    before_replay = snapshot(correction_project[0])
    replay = execute(request, correction_project)
    assert replay | {"replay": False} == first
    assert snapshot(correction_project[0]) == before_replay

    conflicting_action = (
        "record_source_linkage_correction"
        if action == "rename_candidate_metadata"
        else "rename_candidate_metadata"
    )
    conflict = command(
        conflicting_action,
        expected_current_review_status="correction_recorded",
        expected_current_version=1,
    )
    before_conflict = snapshot(correction_project[0])
    with pytest.raises(review_api.ReviewActionUnprocessable) as raised:
        execute(conflict, correction_project)
    assert raised.value.payload["error_code"] == "REVIEW_ACTION_INVALID_TRANSITION"
    assert snapshot(correction_project[0]) == before_conflict


@pytest.mark.parametrize(
    "overrides",
    (
        {"requested_owner_visible_label": ""},
        {"requested_owner_visible_label": " ../escape "},
        {"requested_owner_visible_label": "folder/name"},
        {"requested_owner_visible_label": "x" * 257},
        {"requested_owner_visible_label": "bad\ud800"},
    ),
)
def test_rename_rejects_unsafe_or_invalid_labels(overrides):
    with pytest.raises(review_api.ReviewActionUnprocessable):
        review_api.validate_review_action_command_request(
            command("rename_candidate_metadata", **overrides),
            project_id=PROJECT_ID,
            queue_entry_id=QUEUE_ENTRY_ID,
        )


@pytest.mark.parametrize(
    "locator",
    (
        None,
        {},
        {**CORRECTED_LOCATOR, "project_id": "other_project"},
        {**CORRECTED_LOCATOR, "source_document_id": "../escape"},
        {**CORRECTED_LOCATOR, "unknown": "blocked"},
    ),
)
def test_source_link_correction_rejects_missing_unsafe_or_cross_project(locator):
    with pytest.raises(review_api.ReviewActionUnprocessable):
        review_api.validate_review_action_command_request(
            command(
                "record_source_linkage_correction",
                requested_source_locator=locator,
            ),
            project_id=PROJECT_ID,
            queue_entry_id=QUEUE_ENTRY_ID,
        )


@pytest.mark.parametrize(
    ("action", "overrides"),
    (
        (
            "rename_candidate_metadata",
            {"requested_owner_visible_label": "Original review label"},
        ),
        (
            "record_source_linkage_correction",
            {"requested_source_locator": ORIGINAL_LOCATOR},
        ),
    ),
)
def test_noop_corrections_and_stale_versions_are_write_free(
    correction_project, action, overrides
):
    before = snapshot(correction_project[0])
    with pytest.raises(review_api.ReviewActionUnprocessable):
        execute(command(action, **overrides), correction_project)
    assert snapshot(correction_project[0]) == before

    with pytest.raises(review_api.ReviewActionConflict):
        execute(command(action, expected_current_version=1), correction_project)
    assert snapshot(correction_project[0]) == before


def test_generic_status_command_cannot_create_correction_state():
    request = command(
        "rename_candidate_metadata",
        action_type="set_review_status",
        target_review_status="correction_recorded",
    )
    with pytest.raises(review_api.ReviewActionUnprocessable):
        review_api.validate_review_action_command_request(
            request,
            project_id=PROJECT_ID,
            queue_entry_id=QUEUE_ENTRY_ID,
        )
