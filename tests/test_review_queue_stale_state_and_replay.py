"""Canonical request, stale-state, and durable replay tests."""

from __future__ import annotations

import json
import uuid
from pathlib import Path

import pytest

from backend import project_manager, review_api
from backend.story_knowledge import (
    candidate_persistence,
    candidate_record,
    candidate_review_gate,
    review_action_events,
    review_queue_storage,
)


PROJECT_ID = "example"
QUEUE_ENTRY_ID = "review_queue_entry_replay_001"
CANDIDATE_ID = "core_candidate_replay_001"
NOW = "2026-08-09T20:00:00Z"


def payload(**overrides) -> dict:
    value = {
        "action_type": "mark_reviewed",
        "queue_entry_id": QUEUE_ENTRY_ID,
        "candidate_id": CANDIDATE_ID,
        "actor": "owner-reviewed",
        "owner_confirmed": True,
        "preserve_candidate_linkage": True,
        "preserve_evidence_provenance": True,
        "idempotency_key": str(uuid.uuid4()),
        "expected_current_review_status": "pending",
        "expected_current_version": 0,
    }
    value.update(overrides)
    return value


def validated(value: dict | None = None) -> dict:
    return review_api.validate_review_action_command_request(
        value or payload(), project_id=PROJECT_ID, queue_entry_id=QUEUE_ENTRY_ID
    )


def candidate() -> dict:
    return candidate_record.validate_candidate_record(
        {
            "candidate_id": CANDIDATE_ID,
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


@pytest.fixture
def durable_project(tmp_path: Path) -> tuple[Path, Path]:
    projects = tmp_path / "projects"
    project_manager.create_project("Example", projects_dir=projects)
    project_dir = (projects / PROJECT_ID).resolve()
    candidate_value = candidate()
    candidate_persistence.write_candidate_record(project_dir, candidate_value)
    entry = candidate_review_gate.build_review_queue_entry(candidate_value, project_id=PROJECT_ID)
    entry["queue_entry_id"] = QUEUE_ENTRY_ID
    review_queue_storage.write_review_queue_entry(entry, project_dir=project_dir)
    runtime = tmp_path / "runtime"
    runtime.mkdir(mode=0o700)
    return project_dir, runtime


def execute(value: dict, roots: tuple[Path, Path]) -> dict:
    project_dir, runtime = roots
    return review_api.execute_review_action_command(
        value,
        project_id=PROJECT_ID,
        queue_entry_id=QUEUE_ENTRY_ID,
        project_dir=project_dir,
        trusted_runtime_dir=runtime,
    )


def tree_snapshot(root: Path) -> dict[str, bytes]:
    return {
        item.relative_to(root).as_posix(): item.read_bytes()
        for item in root.rglob("*")
        if item.is_file()
    }


def test_canonical_request_record_has_exact_22_fields_and_bytes() -> None:
    record = review_api.build_canonical_review_action_request_record(
        validated(), project_id=PROJECT_ID, queue_entry_id=QUEUE_ENTRY_ID
    )
    assert tuple(record) == review_api._CANONICAL_REQUEST_FIELDS
    assert len(record) == 22
    raw = review_api.canonical_review_action_request_bytes(record)
    assert raw == json.dumps(record, ensure_ascii=False, separators=(",", ":")).encode()
    assert not raw.endswith(b"\n")


def test_canonical_request_missing_null_unicode_integer_and_array_order_cases() -> None:
    first = payload(
        action_type="mark_duplicate",
        owner_note=" Café e\u0301 ",
        duplicate_candidate_ids=["core_candidate_b"],
        duplicate_target_queue_entry_id="review_queue_entry_b",
        duplicate_target_expected_review_status="pending",
        duplicate_target_expected_version=0,
    )
    second = dict(first, duplicate_candidate_ids=["core_candidate_a"])
    record = review_api.build_canonical_review_action_request_record(validated(first), project_id=PROJECT_ID, queue_entry_id=QUEUE_ENTRY_ID)
    explicit_null = dict(first, rationale=None)
    null_record = review_api.build_canonical_review_action_request_record(validated(explicit_null), project_id=PROJECT_ID, queue_entry_id=QUEUE_ENTRY_ID)
    assert record == null_record
    assert " Café e\\u0301 " not in review_api.canonical_review_action_request_bytes(record).decode()
    assert " Café e\u0301 " in review_api.canonical_review_action_request_bytes(record).decode()
    assert review_api.hash_review_action_request(record) != review_api.hash_review_action_request(review_api.build_canonical_review_action_request_record(validated(second), project_id=PROJECT_ID, queue_entry_id=QUEUE_ENTRY_ID))
    with pytest.raises(review_api.ReviewActionUnprocessable):
        validated(payload(expected_current_version=True))
    with pytest.raises(review_api.ReviewActionUnprocessable):
        validated(dict(first, duplicate_candidate_ids=["core_candidate_a", "core_candidate_b"]))


def test_idempotency_key_and_transport_fields_are_excluded_from_request_hash() -> None:
    one = validated(payload(idempotency_key=str(uuid.uuid4())))
    two = validated(payload(idempotency_key=str(uuid.uuid4())))
    one["headers"] = {"trace": "one"}
    two["headers"] = {"trace": "two"}
    one_record = review_api.build_canonical_review_action_request_record(one, project_id=PROJECT_ID, queue_entry_id=QUEUE_ENTRY_ID)
    two_record = review_api.build_canonical_review_action_request_record(two, project_id=PROJECT_ID, queue_entry_id=QUEUE_ENTRY_ID)
    assert review_api.hash_review_action_request(one_record) == review_api.hash_review_action_request(two_record)


def test_chain_validation_and_queue_hash_precede_key_lookup(
    durable_project: tuple[Path, Path], monkeypatch
) -> None:
    project_dir, _ = durable_project
    entry_path = review_queue_storage.review_queue_entry_path(project_dir, QUEUE_ENTRY_ID)
    before = entry_path.read_bytes()
    monkeypatch.setattr(review_action_events, "scan_review_action_event_chain", lambda **kwargs: (_ for _ in ()).throw(ValueError("corrupt")))
    with pytest.raises(review_api.ReviewActionPersistenceFailure) as raised:
        execute(payload(), durable_project)
    assert raised.value.payload["error_code"] == "REVIEW_ACTION_EVENT_CHAIN_CORRUPT"
    assert entry_path.read_bytes() == before


def test_same_key_different_hash_is_409_even_for_r8_shaped_queue(
    durable_project: tuple[Path, Path]
) -> None:
    request = payload()
    execute(request, durable_project)
    project_dir, _ = durable_project
    changed = review_queue_storage.read_review_queue_entry(QUEUE_ENTRY_ID, project_dir=project_dir)
    changed["owner_note"] = "Authorized external corruption fixture"
    review_queue_storage.replace_review_queue_entry_atomic(changed, project_dir=project_dir)
    with pytest.raises(review_api.ReviewActionConflict):
        execute(dict(request, rationale="different request"), durable_project)


def test_same_key_same_hash_bypasses_stale_status_and_version(
    durable_project: tuple[Path, Path]
) -> None:
    request = payload()
    execute(request, durable_project)
    replay = execute(request, durable_project)
    assert replay["replay"] is True
    assert replay["review_version"] == 1


def test_new_key_stale_status_version_and_aba_are_409_without_writes(
    durable_project: tuple[Path, Path]
) -> None:
    project_dir, _ = durable_project
    before = tree_snapshot(project_dir)
    with pytest.raises(review_api.ReviewActionConflict):
        execute(payload(expected_current_version=1), durable_project)
    assert tree_snapshot(project_dir) == before
    with pytest.raises(review_api.ReviewActionConflict):
        execute(payload(expected_current_review_status="deferred"), durable_project)
    assert tree_snapshot(project_dir) == before


def test_replay_preserves_version_and_reconstructs_original_response(
    durable_project: tuple[Path, Path]
) -> None:
    request = payload(owner_note="Original owner note")
    first = execute(request, durable_project)
    replay = execute(request, durable_project)
    assert replay | {"replay": False} == first
    assert replay["review_version"] == 1


def test_restart_replay_uses_only_durable_state(durable_project: tuple[Path, Path]) -> None:
    request = payload()
    first = execute(request, durable_project)
    replay = execute(json.loads(json.dumps(request)), durable_project)
    assert replay["action_id"] == first["action_id"]
    assert replay["completion_event_hash"] == first["completion_event_hash"]
    assert replay["replay"] is True


def test_approve_replay_is_deterministic_and_conflicting_disposition_fails_closed(
    durable_project: tuple[Path, Path],
) -> None:
    request = payload(
        action_type="approve",
        owner_note="Owner approves this review lifecycle state only.",
        rationale="Evidence is sufficient for review approval.",
    )
    first = execute(request, durable_project)
    before_replay = tree_snapshot(durable_project[0])
    replay = execute(request, durable_project)
    assert replay | {"replay": False} == first
    assert replay["review_status"] == "approved"
    assert replay["lifecycle_state"] == "owner_reviewed_approved"
    assert replay["review_workflow_state"]["is_canon"] is False
    assert replay["review_workflow_state"]["promotion_created"] is False
    assert tree_snapshot(durable_project[0]) == before_replay

    conflict = payload(
        action_type="reject",
        owner_note="Conflicting terminal disposition.",
        expected_current_review_status="approved",
        expected_current_version=1,
    )
    before_conflict = tree_snapshot(durable_project[0])
    with pytest.raises(review_api.ReviewActionUnprocessable) as raised:
        execute(conflict, durable_project)
    assert raised.value.payload["error_code"] == "REVIEW_ACTION_INVALID_TRANSITION"
    assert tree_snapshot(durable_project[0]) == before_conflict
