"""T011G backend-only grouped review-queue lifecycle and audit validation."""

from __future__ import annotations

import asyncio
import base64
import hashlib
from pathlib import Path
from types import SimpleNamespace

import pytest

from backend import project_manager, review_api
from backend.routes import review_queue
from backend.story_knowledge import apply_contract, review_action_events, review_queue_storage


PROJECT_ID = "example"
NOW = "2026-08-09T20:00:00Z"
STATE_PAIRS = (
    ("approved", "owner_reviewed_approved"),
    ("rejected", "owner_reviewed_rejected"),
    ("needs_info", "needs_more_evidence"),
    ("duplicate", "duplicate_candidate"),
    ("split_required", "incorrect_cluster_split_required"),
    ("correction_recorded", "rename_metadata_recorded"),
    ("correction_recorded", "source_linkage_correction_recorded"),
    ("superseded", "superseded_candidate"),
    ("correction_recorded", "owner_authored_correction_recorded"),
    ("needs_info", "rerun_selected_source_requested"),
)


def _locator(source_document_id: str) -> dict:
    return {
        "project_id": PROJECT_ID,
        "source_document_type": "scene",
        "source_document_id": source_document_id,
        "section_id": None,
        "chapter_id": None,
        "scene_id": source_document_id,
        "line_start": None,
        "line_end": None,
        "char_start": None,
        "char_end": None,
        "source_hash": None,
    }


def _entry(index: int, pair: tuple[str, str]) -> dict:
    source_locator = _locator(f"scene_{index:03d}")
    entry = {
        "queue_entry_id": f"review_queue_entry_grouped_{index:03d}",
        "project_id": PROJECT_ID,
        "candidate_record_id": f"core_candidate_grouped_{index:03d}",
        "candidate_type": "character_candidate",
        "target_category": "characters",
        "review_status": pair[0],
        "lifecycle_state": pair[1],
        "source_document": source_locator["source_document_id"],
        "source_locator": source_locator,
        "evidence_summary": f"Evidence summary {index}",
        "evidence_refs": [f"evidence_grouped_{index:03d}"],
        "provenance_summary": f"Provenance summary {index}",
        "provenance_refs": [f"provenance_grouped_{index:03d}"],
        "confidence": 0.4,
        "uncertainty_flags": [],
        "normalization_status": "normalized",
        "raw_output_refs": [],
        "human_review_required": True,
        "created_at": NOW,
        "updated_at": NOW,
        "review_version": 1,
        "owner_note": f"Owner note {index}",
        "rationale": f"Owner rationale {index}",
        "owner_review_completed": True,
        "owner_reviewed_at": NOW,
    }
    if pair == ("needs_info", "needs_more_evidence"):
        entry["insufficient_evidence_reason"] = "More source evidence is required."
    elif pair == ("duplicate", "duplicate_candidate"):
        entry.update(
            duplicate_candidate_ids=["core_candidate_duplicate_target"],
            duplicate_target_queue_entry_id="review_queue_entry_duplicate_target",
            duplicate_target_review_status="pending",
            duplicate_target_lifecycle_state="owner_review_pending",
            duplicate_target_review_version=0,
        )
    elif pair == ("correction_recorded", "rename_metadata_recorded"):
        entry.update(
            original_owner_visible_label="Original label",
            requested_owner_visible_label="Owner-corrected label",
            owner_visible_label="Owner-corrected label",
        )
    elif pair == ("correction_recorded", "source_linkage_correction_recorded"):
        entry.update(
            original_source_locator=source_locator,
            requested_source_locator=_locator("scene_corrected"),
        )
    elif pair == ("superseded", "superseded_candidate"):
        entry.update(
            superseded_by_candidate_id="core_candidate_superseding_target",
            superseding_target_queue_entry_id="review_queue_entry_superseding_target",
            superseding_target_review_status="pending",
            superseding_target_lifecycle_state="owner_review_pending",
            superseding_target_review_version=0,
        )
    elif pair == (
        "correction_recorded",
        "owner_authored_correction_recorded",
    ):
        entry["owner_authored_correction"] = "  Exact owner-supplied correction.\n"
    elif pair == ("needs_info", "rerun_selected_source_requested"):
        entry.update(
            prior_analysis_run_id="analysis_run_prior_grouped_001",
            prior_analysis_run_manifest_hash="a" * 64,
            prior_source_snapshot_id="source_snapshot_prior_grouped_001",
            prior_source_hash="b" * 64,
            prior_source_locator=source_locator,
            selected_source_locator=source_locator,
            prior_run_lineage_verification="verified_analysis_run_manifest",
        )
    return review_queue_storage.validate_review_queue_entry(entry)


def _snapshot(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file()
    }


def _publish_approved_chain(project_dir: Path, entry: dict) -> None:
    raw = apply_contract.canonical_json_bytes(entry)
    encoded = base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")
    intent = review_action_events.build_action_intent_event_v1(
        sequence=1,
        previous_event_hash=None,
        project_id=PROJECT_ID,
        queue_entry_id=entry["queue_entry_id"],
        candidate_record_id=entry["candidate_record_id"],
        action_command="approve",
        action_id="rvact_123e4567e89b42d3a456426614174001",
        idempotency_key="123e4567-e89b-42d3-a456-426614174001",
        request_hash="1" * 64,
        created_at=NOW,
        queue_before_hash="2" * 64,
        target_queue_canonical_bytes_b64url=encoded,
        target_queue_hash=hashlib.sha256(raw).hexdigest(),
        candidate_before_hash="3" * 64,
        evidence_projection_before_hash="4" * 64,
    )
    review_action_events.publish_review_action_event(
        intent, project_dir=project_dir, queue_entry_id=entry["queue_entry_id"]
    )
    completed = review_action_events.build_action_completed_event_v1(
        intent=intent,
        queue_after_hash=intent["target_queue_hash"],
        candidate_after_hash=intent["candidate_before_hash"],
        evidence_projection_after_hash=intent["evidence_projection_before_hash"],
        completed_at=NOW,
    )
    review_action_events.publish_review_action_event(
        completed, project_dir=project_dir, queue_entry_id=entry["queue_entry_id"]
    )


@pytest.fixture
def grouped_project(tmp_path: Path) -> tuple[Path, list[dict]]:
    projects = tmp_path / "projects"
    project_manager.create_project("Example", projects_dir=projects)
    project_dir = (projects / PROJECT_ID).resolve()
    entries = [_entry(index, pair) for index, pair in enumerate(STATE_PAIRS, 1)]
    for entry in entries:
        review_queue_storage.write_review_queue_entry(entry, project_dir=project_dir)
    _publish_approved_chain(project_dir, entries[0])
    return project_dir, entries


def test_grouped_projection_covers_all_t011_states_and_preserves_audit_metadata(
    grouped_project: tuple[Path, list[dict]],
) -> None:
    project_dir, entries = grouped_project
    before = _snapshot(project_dir)

    first = review_api.get_review_queue_grouped_audit_readonly(
        {"project_id": PROJECT_ID}, project_dir=project_dir
    )
    second = review_api.get_review_queue_grouped_audit_readonly(
        {"project_id": PROJECT_ID}, project_dir=project_dir
    )

    assert first == second
    assert _snapshot(project_dir) == before
    assert first["summary"]["entry_count"] == len(STATE_PAIRS)
    assert first["summary"]["group_count"] == len(STATE_PAIRS)
    assert first["summary"]["audited_entry_count"] == 1
    assert {
        (group["review_status"], group["lifecycle_state"])
        for group in first["groups"]
    } == set(STATE_PAIRS)

    projected = {
        (group["review_status"], group["lifecycle_state"]): group["entries"][0]
        for group in first["groups"]
    }
    for source in entries:
        item = projected[(source["review_status"], source["lifecycle_state"])]
        assert item["entry"]["queue_entry_id"] == source["queue_entry_id"]
        assert item["entry"]["candidate_record_id"] == source["candidate_record_id"]
        assert item["entry"]["review_version"] == source["review_version"]
        assert item["entry"]["source_locator"] == source["source_locator"]
        assert item["entry"]["evidence_refs"] == source["evidence_refs"]
        assert item["entry"]["provenance_refs"] == source["provenance_refs"]
        assert item["entry"]["owner_note"] == source["owner_note"]
        assert item["entry"]["rationale"] == source["rationale"]
        assert item["audit"]["chain_validated"] is True

    approved_audit = projected[("approved", "owner_reviewed_approved")]["audit"]
    assert approved_audit["chain_state"] == "completed"
    assert approved_audit["event_count"] == 2
    assert approved_audit["action_count"] == 1
    assert approved_audit["latest_action_command"] == "approve"
    assert approved_audit["chain_head_event_hash"] == approved_audit["events"][-1]["event_hash"]
    assert approved_audit["events"][0]["idempotency_key"]
    assert "target_queue_canonical_bytes_b64url" not in approved_audit["events"][0]

    duplicate = projected[("duplicate", "duplicate_candidate")]["entry"]
    assert duplicate["duplicate_target_queue_entry_id"] == "review_queue_entry_duplicate_target"
    rename = projected[("correction_recorded", "rename_metadata_recorded")]["entry"]
    assert rename["requested_owner_visible_label"] == "Owner-corrected label"
    source_correction = projected[("correction_recorded", "source_linkage_correction_recorded")]["entry"]
    assert source_correction["original_source_locator"] != source_correction["requested_source_locator"]
    superseded = projected[("superseded", "superseded_candidate")]["entry"]
    assert superseded["superseded_by_candidate_id"] == "core_candidate_superseding_target"
    owner_correction = projected[("correction_recorded", "owner_authored_correction_recorded")]["entry"]
    assert owner_correction["owner_authored_correction"] == "  Exact owner-supplied correction.\n"
    rerun = projected[("needs_info", "rerun_selected_source_requested")]["entry"]
    assert rerun["prior_run_lineage_verification"] == "verified_analysis_run_manifest"

    workflow = first["review_workflow_state"]
    assert workflow["projection_scope"] == "review_queue_grouped_audit_read_only"
    assert all(value is False for key, value in workflow.items() if key != "projection_scope")
    assert not (project_dir / "writer_assistant" / "approved_memory").exists()
    assert not (project_dir / "writer_assistant" / "promotion_audit").exists()


def test_grouped_projection_rejects_incomplete_specialized_metadata(tmp_path: Path) -> None:
    entry = _entry(1, ("duplicate", "duplicate_candidate"))
    for field in (
        "duplicate_candidate_ids",
        "duplicate_target_queue_entry_id",
        "duplicate_target_review_status",
        "duplicate_target_lifecycle_state",
        "duplicate_target_review_version",
    ):
        entry.pop(field)
    entry = review_queue_storage.validate_review_queue_entry(entry)
    review_queue_storage.write_review_queue_entry(entry, project_dir=tmp_path)

    with pytest.raises(ValueError, match="incomplete grouped review metadata"):
        review_api.get_review_queue_grouped_audit_readonly(
            {"project_id": PROJECT_ID}, project_dir=tmp_path
        )


def test_grouped_projection_rejects_event_chain_that_no_longer_matches_entry(
    grouped_project: tuple[Path, list[dict]],
) -> None:
    project_dir, entries = grouped_project
    changed = dict(entries[0])
    changed["owner_note"] = "Unaudited post-action change."
    review_queue_storage.replace_review_queue_entry_atomic(
        changed, project_dir=project_dir
    )

    with pytest.raises(ValueError, match="does not match queue entry"):
        review_api.get_review_queue_grouped_audit_readonly(
            {"project_id": PROJECT_ID}, project_dir=project_dir
        )


class _EmptyQuery:
    def multi_items(self):
        return []


class _ReadRequest:
    query_params = _EmptyQuery()
    scope = {"raw_path": b"/api/projects/example/review-queue/grouped-audit"}
    url = SimpleNamespace(path="/api/projects/example/review-queue/grouped-audit")

    async def body(self):
        return b""


def test_grouped_audit_route_is_read_only_and_separate_from_omi(
    grouped_project: tuple[Path, list[dict]], monkeypatch
) -> None:
    project_dir, _ = grouped_project
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", project_dir.parent)
    before = _snapshot(project_dir)

    response = asyncio.run(
        review_queue.get_review_queue_grouped_audit(PROJECT_ID, _ReadRequest())
    )

    assert response["project_id"] == PROJECT_ID
    assert response["groups"]
    assert _snapshot(project_dir) == before
    route_paths = {route.path for route in review_queue.router.routes}
    assert "/api/projects/{project_id}/review-queue/grouped-audit" in route_paths
    assert all("/omi" not in path for path in route_paths)
