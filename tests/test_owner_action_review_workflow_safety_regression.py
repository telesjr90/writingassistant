"""Cross-command prohibition against mutations outside review workflow state."""

from __future__ import annotations

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
OTHER_PROJECT_ID = "other"
QUEUE_ENTRY_ID = "review_queue_entry_safety_001"
CANDIDATE_ID = "core_candidate_safety_001"
NOW = "2026-08-09T20:00:00Z"
COMMANDS = (
    "mark_reviewed",
    "request_more_evidence",
    "defer",
    "reject",
    "quarantine",
    "update_owner_note",
    "set_review_status",
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


def command(action: str) -> dict:
    result = {
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
    }
    result.update(
        {
            "request_more_evidence": {"owner_note": "Need more evidence"},
            "defer": {"owner_note": "Defer"},
            "reject": {"owner_note": "Reject"},
            "quarantine": {"owner_note": "Quarantine"},
            "update_owner_note": {"owner_note": "Owner note"},
            "set_review_status": {
                "target_review_status": "deferred",
                "owner_note": "Defer through status",
            },
        }.get(action, {})
    )
    return result


def snapshot_paths(paths: list[Path]) -> dict[str, bytes]:
    result = {}
    for root in paths:
        for path in root.rglob("*"):
            if path.is_file():
                result[str(path)] = path.read_bytes()
    return result


@pytest.mark.parametrize("action", COMMANDS)
def test_all_review_commands_mutate_only_selected_queue_and_event_paths(
    tmp_path: Path, action: str
) -> None:
    projects = tmp_path / "projects"
    project_manager.create_project("Example", projects_dir=projects)
    project_manager.create_project("Other", projects_dir=projects)
    project_dir = (projects / PROJECT_ID).resolve()
    other_dir = (projects / OTHER_PROJECT_ID).resolve()
    candidate_value = candidate()
    candidate_persistence.write_candidate_record(project_dir, candidate_value)
    entry = candidate_review_gate.build_review_queue_entry(candidate_value, project_id=PROJECT_ID)
    entry["queue_entry_id"] = QUEUE_ENTRY_ID
    review_queue_storage.write_review_queue_entry(entry, project_dir=project_dir)
    runtime = tmp_path / "runtime"
    runtime.mkdir(mode=0o700)
    with review_action_events.acquire_review_action_lock(
        trusted_runtime_dir=runtime,
        project_id=PROJECT_ID,
        queue_entry_id=QUEUE_ENTRY_ID,
    ):
        pass

    forbidden_roots = []
    for relative in (
        "memory",
        "canon",
        "promotions",
        "apply-promotion",
        "book-sources",
        "story-prose",
        "model-artifacts",
        "extraction-artifacts",
        "training",
        "datasets",
    ):
        root = project_dir / relative
        root.mkdir(parents=True)
        (root / "sentinel.txt").write_text(f"immutable {relative}\n", encoding="utf-8")
        forbidden_roots.append(root)
    (other_dir / "unrelated.txt").write_text("unrelated project\n", encoding="utf-8")
    forbidden_roots.extend([runtime, other_dir])
    before = snapshot_paths(forbidden_roots)

    response = review_api.execute_review_action_command(
        command(action),
        project_id=PROJECT_ID,
        queue_entry_id=QUEUE_ENTRY_ID,
        project_dir=project_dir,
        trusted_runtime_dir=runtime,
    )

    assert response["status"] == "accepted"
    workflow_state = response["review_workflow_state"]
    expected_safety_state = {
        "is_canon": False,
        "apply_promotion_performed": False,
        "memory_canon_mutation_performed": False,
        "project_truth_mutation_performed": False,
        "raw_artifact_persistence_performed": False,
        "runtime_extraction_performed": False,
        "model_call_performed": False,
        "generated_prose_performed": False,
        "training_artifact_performed": False,
    }
    assert {
        key: workflow_state.get(key) for key in expected_safety_state
    } == expected_safety_state
    assert workflow_state["approval_scope"] == "review_lifecycle_metadata_only"
    assert workflow_state["candidate_record_mutation_performed"] is False
    assert workflow_state["promotion_created"] is False
    assert workflow_state["rerun_execution_performed"] is False
    assert workflow_state["candidate_generation_performed"] is False
    after = snapshot_paths(forbidden_roots)
    assert after == before
