"""Focused contract tests for immutable review-action event storage."""

import base64
import copy
import hashlib
import inspect
import os
import stat
from pathlib import Path

import pytest

from backend.story_knowledge import apply_contract
from backend.story_knowledge import review_action_events
from backend.story_knowledge import review_queue_storage


PROJECT_ID = "example"
QUEUE_ENTRY_ID = "review_queue_entry_scene_001_character_001"
CANDIDATE_ID = "core_candidate_scene_001_character_001"
ACTION_ID = "rvact_123e4567e89b42d3a456426614174000"
IDEMPOTENCY_KEY = "123e4567-e89b-42d3-a456-426614174000"
REQUEST_HASH = "1" * 64
QUEUE_BEFORE_HASH = "2" * 64
CANDIDATE_HASH = "3" * 64
EVIDENCE_HASH = "4" * 64
CREATED_AT = "2026-08-09T19:40:00Z"
FAILED_AT = "2026-08-09T19:40:01Z"
COMPLETED_AT = "2026-08-09T19:40:02Z"


def _queue_entry():
    return {
        "queue_entry_id": QUEUE_ENTRY_ID,
        "project_id": PROJECT_ID,
        "candidate_record_id": CANDIDATE_ID,
        "candidate_type": "character_candidate",
        "target_category": "characters",
        "review_status": "pending",
        "lifecycle_state": "owner_review_pending",
        "source_document": "scene_001",
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
        "evidence_summary": "Synthetic evidence summary.",
        "evidence_refs": [],
        "provenance_summary": "Synthetic provenance summary.",
        "provenance_refs": [],
        "confidence": 0.4,
        "uncertainty_flags": [],
        "normalization_status": "normalized",
        "raw_output_refs": [],
        "human_review_required": True,
        "created_at": "2026-08-09T19:39:00Z",
        "updated_at": "2026-08-09T19:40:00Z",
        "review_version": 1,
        "owner_review_completed": False,
        "owner_reviewed_at": None,
    }


def _target_material():
    target = review_queue_storage.validate_review_queue_entry(_queue_entry())
    raw = apply_contract.canonical_json_bytes(target)
    encoded = base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")
    return encoded, hashlib.sha256(raw).hexdigest()


def _intent(
    *,
    sequence=1,
    previous_event_hash=None,
    predecessor=None,
    action_id=ACTION_ID,
    idempotency_key=IDEMPOTENCY_KEY,
):
    encoded, target_hash = _target_material()
    return review_action_events.build_action_intent_event_v1(
        sequence=sequence,
        previous_event_hash=previous_event_hash,
        project_id=PROJECT_ID,
        queue_entry_id=QUEUE_ENTRY_ID,
        candidate_record_id=CANDIDATE_ID,
        action_command="mark_reviewed",
        action_id=action_id,
        idempotency_key=idempotency_key,
        request_hash=REQUEST_HASH,
        created_at=CREATED_AT,
        queue_before_hash=QUEUE_BEFORE_HASH,
        target_queue_canonical_bytes_b64url=encoded,
        target_queue_hash=target_hash,
        candidate_before_hash=CANDIDATE_HASH,
        evidence_projection_before_hash=EVIDENCE_HASH,
        predecessor=predecessor,
    )


def _completed(intent):
    return review_action_events.build_action_completed_event_v1(
        intent=intent,
        queue_after_hash=intent["target_queue_hash"],
        candidate_after_hash=CANDIDATE_HASH,
        evidence_projection_after_hash=EVIDENCE_HASH,
        completed_at=COMPLETED_AT,
    )


def _failed(intent, *, retryable=True):
    return review_action_events.build_action_failed_event_v1(
        intent=intent,
        failure_reason="QUEUE_WRITE_FAILED" if retryable else "QUEUE_STATE_CORRUPT",
        failure_detail="Synthetic bounded queue-write diagnostic.",
        observed_queue_hash=QUEUE_BEFORE_HASH,
        retryable=retryable,
        failed_at=FAILED_AT,
    )


def _recovery(intent, failed):
    return review_action_events.build_action_recovery_completed_event_v1(
        intent=intent,
        failed=failed,
        queue_after_hash=intent["target_queue_hash"],
        candidate_after_hash=CANDIDATE_HASH,
        evidence_projection_after_hash=EVIDENCE_HASH,
        completed_at=COMPLETED_AT,
    )


def _rehash(event):
    result = copy.deepcopy(event)
    result.pop("event_hash", None)
    result["event_hash"] = hashlib.sha256(
        apply_contract.canonical_json_bytes(result)
    ).hexdigest()
    return result


def _context(event, intent, failed):
    if event["event_type"] == "action_intent":
        return {}
    if event["event_type"] in {"action_completed", "action_failed"}:
        return {"predecessor": intent, "intent": intent}
    return {"predecessor": failed, "intent": intent, "failed": failed}


def _event_path(project, event):
    return review_action_events.review_action_events_dir(
        project_dir=project, queue_entry_id=QUEUE_ENTRY_ID
    ) / "{0:012d}_{1}.json".format(event["sequence"], event["event_hash"])


def test_all_four_complete_closed_event_schemas_validate():
    intent = _intent()
    completed = _completed(intent)
    failed = _failed(intent)
    recovery = _recovery(intent, failed)

    assert review_action_events.validate_review_action_event_v1(intent) == intent
    assert (
        review_action_events.validate_review_action_event_v1(
            completed, predecessor=intent, intent=intent
        )
        == completed
    )
    assert (
        review_action_events.validate_review_action_event_v1(
            failed, predecessor=intent, intent=intent
        )
        == failed
    )
    assert (
        review_action_events.validate_review_action_event_v1(
            recovery, predecessor=failed, intent=intent, failed=failed
        )
        == recovery
    )


def test_duplicate_intent_requires_explicit_command_and_audited_target_linkage():
    target = _queue_entry()
    target.update(
        review_status="duplicate",
        lifecycle_state="duplicate_candidate",
        duplicate_candidate_ids=["core_candidate_target_001"],
        duplicate_target_queue_entry_id="review_queue_entry_target_001",
        duplicate_target_review_status="pending",
        duplicate_target_lifecycle_state="owner_review_pending",
        duplicate_target_review_version=0,
        owner_review_completed=True,
        owner_reviewed_at=COMPLETED_AT,
    )
    target = review_queue_storage.validate_review_queue_entry(target)
    raw = apply_contract.canonical_json_bytes(target)
    encoded = base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")
    values = {
        "sequence": 1,
        "previous_event_hash": None,
        "project_id": PROJECT_ID,
        "queue_entry_id": QUEUE_ENTRY_ID,
        "candidate_record_id": CANDIDATE_ID,
        "action_command": "mark_duplicate",
        "action_id": ACTION_ID,
        "idempotency_key": IDEMPOTENCY_KEY,
        "request_hash": REQUEST_HASH,
        "created_at": CREATED_AT,
        "queue_before_hash": QUEUE_BEFORE_HASH,
        "target_queue_canonical_bytes_b64url": encoded,
        "target_queue_hash": hashlib.sha256(raw).hexdigest(),
        "candidate_before_hash": CANDIDATE_HASH,
        "evidence_projection_before_hash": EVIDENCE_HASH,
    }
    intent = review_action_events.build_action_intent_event_v1(**values)
    assert intent["action_command"] == "mark_duplicate"

    with pytest.raises(ValueError):
        review_action_events.build_action_intent_event_v1(
            **{**values, "action_command": "set_review_status"}
        )


def test_split_required_intent_requires_its_explicit_command():
    target = _queue_entry()
    target.update(
        review_status="split_required",
        lifecycle_state="incorrect_cluster_split_required",
        owner_note="Split this incorrect cluster.",
        rationale="It combines distinct analytical claims.",
        owner_review_completed=True,
        owner_reviewed_at=COMPLETED_AT,
    )
    target = review_queue_storage.validate_review_queue_entry(target)
    raw = apply_contract.canonical_json_bytes(target)
    encoded = base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")
    values = {
        "sequence": 1,
        "previous_event_hash": None,
        "project_id": PROJECT_ID,
        "queue_entry_id": QUEUE_ENTRY_ID,
        "candidate_record_id": CANDIDATE_ID,
        "action_command": "mark_split_required",
        "action_id": ACTION_ID,
        "idempotency_key": IDEMPOTENCY_KEY,
        "request_hash": REQUEST_HASH,
        "created_at": CREATED_AT,
        "queue_before_hash": QUEUE_BEFORE_HASH,
        "target_queue_canonical_bytes_b64url": encoded,
        "target_queue_hash": hashlib.sha256(raw).hexdigest(),
        "candidate_before_hash": CANDIDATE_HASH,
        "evidence_projection_before_hash": EVIDENCE_HASH,
    }
    assert review_action_events.build_action_intent_event_v1(**values)[
        "action_command"
    ] == "mark_split_required"
    with pytest.raises(ValueError):
        review_action_events.build_action_intent_event_v1(
            **{**values, "action_command": "set_review_status"}
        )


def test_each_event_schema_rejects_missing_unknown_wrong_type_and_invalid_null_fields():
    intent = _intent()
    failed = _failed(intent)
    events = (intent, _completed(intent), failed, _recovery(intent, failed))
    for event in events:
        context = _context(event, intent, failed)
        missing = copy.deepcopy(event)
        del missing["event_hash"]
        unknown = _rehash({**event, "unknown_field": "blocked"})
        wrong_type = _rehash({**event, "sequence": "1"})
        invalid_null = _rehash({**event, "action_id": None})
        for invalid in (missing, unknown, wrong_type, invalid_null):
            with pytest.raises(ValueError):
                review_action_events.validate_review_action_event_v1(
                    invalid, **context
                )


def test_event_hash_omits_event_hash_member_and_matches_filename(tmp_path):
    intent = _intent()
    preimage = dict(intent)
    del preimage["event_hash"]
    expected_hash = hashlib.sha256(
        apply_contract.canonical_json_bytes(preimage)
    ).hexdigest()
    assert intent["event_hash"] == expected_hash

    project = tmp_path / "project"
    project.mkdir()
    review_action_events.publish_review_action_event(
        intent, project_dir=project, queue_entry_id=QUEUE_ENTRY_ID
    )
    assert _event_path(project, intent).is_file()


def test_event_sequence_and_predecessor_chain_is_contiguous(tmp_path):
    intent = _intent()
    completed = _completed(intent)
    second_intent = _intent(
        sequence=3,
        previous_event_hash=completed["event_hash"],
        predecessor=completed,
        action_id="rvact_223e4567e89b42d3a456426614174000",
        idempotency_key="223e4567-e89b-42d3-a456-426614174000",
    )
    project = tmp_path / "project"
    project.mkdir()
    for event in (intent, completed, second_intent):
        review_action_events.publish_review_action_event(
            event, project_dir=project, queue_entry_id=QUEUE_ENTRY_ID
        )
    chain = review_action_events.scan_review_action_event_chain(
        project_dir=project,
        project_id=PROJECT_ID,
        queue_entry_id=QUEUE_ENTRY_ID,
    )
    assert [event["sequence"] for event in chain] == [1, 2, 3]
    assert chain[2]["previous_event_hash"] == chain[1]["event_hash"]

    gap = _rehash({**second_intent, "sequence": 4})
    with pytest.raises(ValueError):
        review_action_events.validate_review_action_event_v1(
            gap, predecessor=completed
        )


def test_completed_and_failed_directly_link_their_intent():
    intent = _intent()
    completed = _completed(intent)
    failed = _failed(intent)
    review_action_events.validate_review_action_event_v1(
        completed, predecessor=intent, intent=intent
    )
    review_action_events.validate_review_action_event_v1(
        failed, predecessor=intent, intent=intent
    )

    bad_completed = _rehash({**completed, "intent_event_hash": "5" * 64})
    bad_failed = _rehash({**failed, "candidate_record_id": "other_candidate"})
    with pytest.raises(ValueError):
        review_action_events.validate_review_action_event_v1(
            bad_completed, predecessor=intent, intent=intent
        )
    with pytest.raises(ValueError):
        review_action_events.validate_review_action_event_v1(
            bad_failed, predecessor=intent, intent=intent
        )


def test_recovery_completed_directly_links_retryable_failure_and_original_intent():
    intent = _intent()
    failed = _failed(intent)
    recovery = _recovery(intent, failed)
    review_action_events.validate_review_action_event_v1(
        recovery, predecessor=failed, intent=intent, failed=failed
    )

    nonretryable = _failed(intent, retryable=False)
    with pytest.raises(ValueError):
        _recovery(intent, nonretryable)
    bad_recovery = _rehash({**recovery, "intent_event_hash": "6" * 64})
    with pytest.raises(ValueError):
        review_action_events.validate_review_action_event_v1(
            bad_recovery, predecessor=failed, intent=intent, failed=failed
        )


def test_action_failed_cannot_follow_action_completed():
    intent = _intent()
    completed = _completed(intent)
    failed_after_completed = _rehash(
        {
            **_failed(intent),
            "sequence": completed["sequence"] + 1,
            "previous_event_hash": completed["event_hash"],
        }
    )
    with pytest.raises(ValueError):
        review_action_events.validate_review_action_event_v1(
            failed_after_completed, predecessor=completed, intent=intent
        )


def test_recovery_required_event_and_linkage_are_rejected():
    intent = _intent()
    failed = _failed(intent)
    recovery = _recovery(intent, failed)
    recovery_required = _rehash(
        {**recovery, "event_type": "action_recovery_required"}
    )
    forbidden_linkage = _rehash(
        {**recovery, "recovery_required_event_hash": "7" * 64}
    )
    for invalid in (recovery_required, forbidden_linkage):
        with pytest.raises(ValueError):
            review_action_events.validate_review_action_event_v1(
                invalid, predecessor=failed, intent=intent, failed=failed
            )


def test_immutable_publication_rejects_collision_or_replacement(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    intent = _intent()
    review_action_events.publish_review_action_event(
        intent, project_dir=project, queue_entry_id=QUEUE_ENTRY_ID
    )
    event_path = _event_path(project, intent)
    original_bytes = event_path.read_bytes()

    with pytest.raises(ValueError):
        review_action_events.publish_review_action_event(
            intent, project_dir=project, queue_entry_id=QUEUE_ENTRY_ID
        )
    replacement = _rehash({**intent, "created_at": "2026-08-09T19:40:03Z"})
    with pytest.raises(ValueError):
        review_action_events.publish_review_action_event(
            replacement, project_dir=project, queue_entry_id=QUEUE_ENTRY_ID
        )
    assert event_path.read_bytes() == original_bytes
    assert len(list(event_path.parent.iterdir())) == 1


def test_chain_scan_rejects_schema_hash_filename_sequence_and_linkage_corruption(
    tmp_path,
):
    def published_chain(label):
        project = tmp_path / label
        project.mkdir()
        intent = _intent()
        completed = _completed(intent)
        for event in (intent, completed):
            review_action_events.publish_review_action_event(
                event, project_dir=project, queue_entry_id=QUEUE_ENTRY_ID
            )
        return project, intent, completed

    for corruption in ("schema", "hash", "filename", "sequence", "linkage"):
        project, intent, completed = published_chain(corruption)
        original_path = _event_path(project, completed)
        corrupted = copy.deepcopy(completed)
        target_path = original_path
        if corruption == "schema":
            corrupted["schema_version"] = "review_action_event.v0"
            corrupted = _rehash(corrupted)
            target_path = _event_path(project, corrupted)
        elif corruption == "hash":
            corrupted["event_hash"] = "0" * 64
        elif corruption == "filename":
            target_path = original_path.with_name(
                "{0:012d}_{1}.json".format(completed["sequence"], "0" * 64)
            )
        elif corruption == "sequence":
            corrupted["sequence"] = 3
            corrupted = _rehash(corrupted)
            target_path = _event_path(project, corrupted)
        else:
            corrupted["queue_after_hash"] = "8" * 64
            corrupted = _rehash(corrupted)
            target_path = _event_path(project, corrupted)

        original_path.unlink()
        target_path.write_bytes(apply_contract.canonical_json_bytes(corrupted))
        with pytest.raises(ValueError):
            review_action_events.scan_review_action_event_chain(
                project_dir=project,
                project_id=PROJECT_ID,
                queue_entry_id=QUEUE_ENTRY_ID,
            )


def test_lock_uses_injected_runtime_path_and_is_nonblocking(tmp_path):
    runtime = tmp_path / "trusted-runtime"
    runtime.mkdir(mode=0o700)
    with review_action_events.acquire_review_action_lock(
        trusted_runtime_dir=runtime,
        project_id=PROJECT_ID,
        queue_entry_id=QUEUE_ENTRY_ID,
    ) as lock_path:
        assert lock_path.parent == runtime / "review-queue-locks"
        expected_digest = hashlib.sha256(
            (PROJECT_ID + "/" + QUEUE_ENTRY_ID).encode("utf-8")
        ).hexdigest()
        assert lock_path.name == "review-queue-{0}.lock".format(expected_digest)
        metadata = os.lstat(lock_path)
        assert stat.S_ISREG(metadata.st_mode)
        assert metadata.st_size == 0
        assert metadata.st_nlink == 1
        assert stat.S_IMODE(metadata.st_mode) == 0o600
        assert metadata.st_uid == os.getuid()
        with pytest.raises(BlockingIOError):
            with review_action_events.acquire_review_action_lock(
                trusted_runtime_dir=runtime,
                project_id=PROJECT_ID,
                queue_entry_id=QUEUE_ENTRY_ID,
            ):
                pytest.fail("contended lock unexpectedly acquired")

    with review_action_events.acquire_review_action_lock(
        trusted_runtime_dir=runtime,
        project_id=PROJECT_ID,
        queue_entry_id=QUEUE_ENTRY_ID,
    ):
        pass


def test_event_module_has_no_environment_or_runtime_root_selection():
    source = inspect.getsource(review_action_events).lower()
    for forbidden in (
        "os.environ",
        "getenv(",
        "expanduser(",
        "path.home(",
        "tempfile.gettempdir",
        "writing_assistant_runtime_dir",
        "runtime_dir_resolver",
    ):
        assert forbidden not in source
    signature = inspect.signature(review_action_events.acquire_review_action_lock)
    assert signature.parameters["trusted_runtime_dir"].annotation in {Path, "Path"}
