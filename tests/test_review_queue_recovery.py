"""R1-R9 recovery and C001 fault-injection coverage."""

from __future__ import annotations

import asyncio
import json
import uuid
from pathlib import Path

import pytest

from backend import main, project_manager, review_api
from backend.story_knowledge import (
    candidate_persistence,
    candidate_record,
    candidate_review_gate,
    review_action_events,
    review_queue_storage,
)


PROJECT_ID = "example"
QUEUE_ENTRY_ID = "review_queue_entry_recovery_001"
CANDIDATE_ID = "core_candidate_recovery_001"
NOW = "2026-08-09T20:00:00Z"


def request_payload(**overrides) -> dict:
    result = {
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
    result.update(overrides)
    return result


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
def recovery_project(tmp_path: Path) -> tuple[Path, Path]:
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


def chain(roots: tuple[Path, Path]) -> list[dict]:
    return review_action_events.scan_review_action_event_chain(
        project_dir=roots[0], project_id=PROJECT_ID, queue_entry_id=QUEUE_ENTRY_ID
    )


def snapshot(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file()
    }


@pytest.mark.parametrize(
    ("shape", "queue_hash", "expected"),
    [
        ("intent", "before", "R1"),
        ("intent", "target", "R2"),
        ("intent", "other", "R3"),
        ("retryable", "before", "R4"),
        ("retryable", "target", "R5"),
        ("terminal", "other", "R6"),
        ("completed", "target", "R7"),
        ("completed", "other", "R8"),
    ],
)
def test_r1_r9_classification_exact_event_shape_and_queue_hash(
    shape: str, queue_hash: str, expected: str
) -> None:
    intent = {
        "event_type": "action_intent",
        "event_hash": "a" * 64,
        "queue_before_hash": "b" * 64,
        "target_queue_hash": "c" * 64,
    }
    events = [intent]
    if shape in {"retryable", "terminal"}:
        events.append(
            {
                "event_type": "action_failed",
                "intent_event_hash": intent["event_hash"],
                "retryable": shape == "retryable",
            }
        )
    elif shape == "completed":
        events.append(
            {
                "event_type": "action_completed",
                "intent_event_hash": intent["event_hash"],
            }
        )
    observed = {"before": "b" * 64, "target": "c" * 64, "other": "d" * 64}[queue_hash]
    assert review_api._classify_existing_action(events, intent, observed)[0] == expected


def test_r9_corruption_is_write_free(
    recovery_project: tuple[Path, Path]
) -> None:
    request = request_payload()
    execute(request, recovery_project)
    events_dir = review_action_events.review_action_events_dir(project_dir=recovery_project[0], queue_entry_id=QUEUE_ENTRY_ID)
    first = sorted(events_dir.iterdir())[0]
    first.write_bytes(first.read_bytes() + b"\n")
    before = snapshot(recovery_project[0])
    with pytest.raises(review_api.ReviewActionPersistenceFailure) as raised:
        execute(request_payload(), recovery_project)
    assert raised.value.payload["error_code"] == "REVIEW_ACTION_EVENT_CHAIN_CORRUPT"
    assert snapshot(recovery_project[0]) == before


@pytest.mark.parametrize("recovery_state", ("R1", "R2", "R4", "R5"))
def test_r1_r2_r4_r5_synchronously_publish_legal_completion(
    recovery_project: tuple[Path, Path], monkeypatch, recovery_state: str
) -> None:
    request = request_payload()
    original_replace = review_queue_storage.replace_review_queue_entry_atomic
    original_publish = review_action_events.publish_review_action_event

    if recovery_state in {"R1", "R4"}:
        def fail_replace(entry, *, project_dir):
            raise OSError("injected before replacement")
        monkeypatch.setattr(review_queue_storage, "replace_review_queue_entry_atomic", fail_replace)
    elif recovery_state == "R5":
        def partial_replace(entry, *, project_dir):
            original_replace(entry, project_dir=project_dir)
            raise OSError("injected after replacement")
        monkeypatch.setattr(review_queue_storage, "replace_review_queue_entry_atomic", partial_replace)
    else:
        def fail_completion(event, *, project_dir, queue_entry_id):
            if event["event_type"] == "action_completed":
                raise OSError("injected completion publication failure")
            return original_publish(event, project_dir=project_dir, queue_entry_id=queue_entry_id)
        monkeypatch.setattr(review_action_events, "publish_review_action_event", fail_completion)

    if recovery_state == "R1":
        def fail_failure_event(event, *, project_dir, queue_entry_id):
            if event["event_type"] == "action_failed":
                raise OSError("injected failure publication failure")
            return original_publish(event, project_dir=project_dir, queue_entry_id=queue_entry_id)
        monkeypatch.setattr(review_action_events, "publish_review_action_event", fail_failure_event)

    with pytest.raises(review_api.ReviewActionPersistenceFailure):
        execute(request, recovery_project)
    monkeypatch.setattr(review_queue_storage, "replace_review_queue_entry_atomic", original_replace)
    monkeypatch.setattr(review_action_events, "publish_review_action_event", original_publish)

    response = execute(request, recovery_project)
    assert response["status"] == "accepted"
    assert response["replay"] is True
    event_types = [event["event_type"] for event in chain(recovery_project)]
    expected_terminal = "action_completed" if recovery_state in {"R1", "R2"} else "action_recovery_completed"
    assert event_types[-1] == expected_terminal


def test_r3_appends_failed_only_and_r6_retry_is_write_free(
    recovery_project: tuple[Path, Path], monkeypatch
) -> None:
    request = request_payload()
    original_replace = review_queue_storage.replace_review_queue_entry_atomic
    original_publish = review_action_events.publish_review_action_event

    def corrupt_then_fail(entry, *, project_dir):
        path = review_queue_storage.review_queue_entry_path(project_dir, QUEUE_ENTRY_ID)
        path.write_text("{invalid", encoding="utf-8")
        raise OSError("injected corrupt replacement")

    def suppress_initial_failure(event, *, project_dir, queue_entry_id):
        if event["event_type"] == "action_failed":
            raise OSError("injected failure publication failure")
        return original_publish(event, project_dir=project_dir, queue_entry_id=queue_entry_id)

    monkeypatch.setattr(review_queue_storage, "replace_review_queue_entry_atomic", corrupt_then_fail)
    monkeypatch.setattr(review_action_events, "publish_review_action_event", suppress_initial_failure)
    with pytest.raises(review_api.ReviewActionPersistenceFailure):
        execute(request, recovery_project)
    monkeypatch.setattr(review_queue_storage, "replace_review_queue_entry_atomic", original_replace)
    monkeypatch.setattr(review_action_events, "publish_review_action_event", original_publish)

    with pytest.raises(review_api.ReviewActionPersistenceFailure):
        execute(request, recovery_project)
    assert [event["event_type"] for event in chain(recovery_project)] == ["action_intent", "action_failed"]
    before = snapshot(recovery_project[0])
    with pytest.raises(review_api.ReviewActionPersistenceFailure):
        execute(request, recovery_project)
    assert snapshot(recovery_project[0]) == before


def test_r7_replay_and_sticky_r8_same_and_new_keys_are_write_free(
    recovery_project: tuple[Path, Path]
) -> None:
    request = request_payload()
    first = execute(request, recovery_project)
    before_replay = snapshot(recovery_project[0])
    replay = execute(request, recovery_project)
    assert replay["completion_event_hash"] == first["completion_event_hash"]
    assert snapshot(recovery_project[0]) == before_replay

    project_dir, _ = recovery_project
    changed = review_queue_storage.read_review_queue_entry(QUEUE_ENTRY_ID, project_dir=project_dir)
    changed["owner_note"] = "Manual mismatch fixture"
    review_queue_storage.replace_review_queue_entry_atomic(changed, project_dir=project_dir)
    before_r8 = snapshot(project_dir)
    for attempted in (request, request_payload(expected_current_version=1)):
        with pytest.raises(review_api.ReviewActionPersistenceFailure) as raised:
            execute(attempted, recovery_project)
        assert raised.value.payload["error_code"] == "REVIEW_ACTION_POST_COMPLETION_INTEGRITY_FAILURE"
        assert snapshot(project_dir) == before_r8


def test_new_key_is_blocked_by_unresolved_r1_r6(
    recovery_project: tuple[Path, Path], monkeypatch
) -> None:
    original_replace = review_queue_storage.replace_review_queue_entry_atomic
    original_publish = review_action_events.publish_review_action_event
    first = request_payload()

    def fail_replace(entry, *, project_dir):
        raise OSError("injected")

    def fail_failure(event, *, project_dir, queue_entry_id):
        if event["event_type"] == "action_failed":
            raise OSError("injected")
        return original_publish(event, project_dir=project_dir, queue_entry_id=queue_entry_id)

    monkeypatch.setattr(review_queue_storage, "replace_review_queue_entry_atomic", fail_replace)
    monkeypatch.setattr(review_action_events, "publish_review_action_event", fail_failure)
    with pytest.raises(review_api.ReviewActionPersistenceFailure):
        execute(first, recovery_project)
    monkeypatch.setattr(review_queue_storage, "replace_review_queue_entry_atomic", original_replace)
    monkeypatch.setattr(review_action_events, "publish_review_action_event", original_publish)
    before = snapshot(recovery_project[0])
    with pytest.raises(review_api.ReviewActionPersistenceFailure) as raised:
        execute(request_payload(), recovery_project)
    assert raised.value.payload["error_code"] == "REVIEW_ACTION_PRIOR_ACTION_UNRESOLVED"
    assert snapshot(recovery_project[0]) == before


@pytest.mark.parametrize(
    ("mode", "reason", "retryable"),
    [
        ("before", "QUEUE_WRITE_FAILED", True),
        ("target", "QUEUE_WRITE_PARTIAL", True),
        ("corrupt", "QUEUE_STATE_CORRUPT", False),
    ],
)
def test_c001_before_target_and_corrupt_classification(
    recovery_project: tuple[Path, Path], monkeypatch, mode: str, reason: str, retryable: bool
) -> None:
    original = review_queue_storage.replace_review_queue_entry_atomic

    def injected(entry, *, project_dir):
        if mode == "target":
            original(entry, project_dir=project_dir)
        elif mode == "corrupt":
            review_queue_storage.review_queue_entry_path(project_dir, QUEUE_ENTRY_ID).write_text("{invalid", encoding="utf-8")
        raise OSError("injected replacement failure")

    monkeypatch.setattr(review_queue_storage, "replace_review_queue_entry_atomic", injected)
    with pytest.raises(review_api.ReviewActionPersistenceFailure):
        execute(request_payload(), recovery_project)
    failed = chain(recovery_project)[-1]
    assert failed["event_type"] == "action_failed"
    assert failed["failure_reason"] == reason
    assert failed["retryable"] is retryable


def test_c001_failure_event_publication_failure_leaves_intent_only(
    recovery_project: tuple[Path, Path], monkeypatch
) -> None:
    original_publish = review_action_events.publish_review_action_event
    monkeypatch.setattr(review_queue_storage, "replace_review_queue_entry_atomic", lambda *args, **kwargs: (_ for _ in ()).throw(OSError("injected")))

    def publish(event, *, project_dir, queue_entry_id):
        if event["event_type"] == "action_failed":
            raise OSError("injected event failure")
        return original_publish(event, project_dir=project_dir, queue_entry_id=queue_entry_id)

    monkeypatch.setattr(review_action_events, "publish_review_action_event", publish)
    with pytest.raises(review_api.ReviewActionPersistenceFailure):
        execute(request_payload(), recovery_project)
    assert [event["event_type"] for event in chain(recovery_project)] == ["action_intent"]


def test_get_and_startup_paths_do_not_scan_recover_or_write(
    recovery_project: tuple[Path, Path], monkeypatch
) -> None:
    project_dir, runtime = recovery_project
    before = snapshot(project_dir)
    monkeypatch.setattr(review_action_events, "scan_review_action_event_chain", lambda **kwargs: (_ for _ in ()).throw(AssertionError("GET scanned events")))
    response = review_api.get_review_queue_entry_readonly(
        {"project_id": PROJECT_ID, "queue_entry_id": QUEUE_ENTRY_ID}, project_dir=project_dir
    )
    assert response["entry"]["queue_entry_id"] == QUEUE_ENTRY_ID
    assert snapshot(project_dir) == before

    class RuntimeManager:
        runtime_dir = runtime

        def start(self):
            return self

        def close(self):
            return None

    manager = RuntimeManager()
    monkeypatch.setattr(
        main.ApplyPromotionRuntimeManager,
        "from_environment",
        lambda **kwargs: manager,
    )
    monkeypatch.setattr(main, "FinalChallengeRegistry", lambda: object())

    async def run_lifespan() -> None:
        async with main._application_lifespan(main.app):
            assert main.app.state.validated_runtime_dir is runtime

    asyncio.run(run_lifespan())
    assert snapshot(project_dir) == before


def test_manual_target_restoration_changes_r8_to_r7_and_allows_new_key(
    recovery_project: tuple[Path, Path]
) -> None:
    request = request_payload()
    execute(request, recovery_project)
    intent = chain(recovery_project)[0]
    project_dir, _ = recovery_project
    changed = review_queue_storage.read_review_queue_entry(QUEUE_ENTRY_ID, project_dir=project_dir)
    changed["owner_note"] = "Mismatch"
    review_queue_storage.replace_review_queue_entry_atomic(changed, project_dir=project_dir)
    with pytest.raises(review_api.ReviewActionPersistenceFailure):
        execute(request, recovery_project)
    target = review_api._decode_intent_target(intent)
    review_queue_storage.replace_review_queue_entry_atomic(target, project_dir=project_dir)
    assert execute(request, recovery_project)["replay"] is True
    next_request = request_payload(
        action_type="update_owner_note",
        owner_note="New owner note",
        expected_current_version=target["review_version"],
        expected_current_review_status=target["review_status"],
    )
    assert execute(next_request, recovery_project)["review_version"] == target["review_version"] + 1
