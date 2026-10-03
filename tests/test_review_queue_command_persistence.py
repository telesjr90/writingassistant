"""Durable transition coverage for all review commands."""

from __future__ import annotations

import hashlib
import uuid
from pathlib import Path

import pytest

from backend import project_manager, review_api
from backend.story_knowledge import (
    analysis_run_manifest,
    apply_contract,
    candidate_persistence,
    candidate_record,
    candidate_review_gate,
    candidate_storage,
    review_queue_storage,
    source_map,
)


PROJECT_ID = "example"
QUEUE_ENTRY_ID = "review_queue_entry_command_001"
CANDIDATE_ID = "core_candidate_command_001"
TARGET_QUEUE_ENTRY_ID = "review_queue_entry_command_target_001"
TARGET_CANDIDATE_ID = "core_candidate_command_target_001"
NOW = "2026-08-09T20:00:00Z"
STATE_PAIRS = (
    ("pending", "draft_ready_for_review"),
    ("pending", "owner_review_pending"),
    ("needs_info", "needs_more_evidence"),
    ("needs_info", "blocked_invalid_support"),
    ("approved", "owner_reviewed_approved"),
    ("rejected", "owner_reviewed_rejected"),
    ("deferred", "owner_reviewed_deferred"),
    ("duplicate", "duplicate_candidate"),
    ("split_required", "incorrect_cluster_split_required"),
    ("correction_recorded", "rename_metadata_recorded"),
    ("correction_recorded", "source_linkage_correction_recorded"),
    ("correction_recorded", "owner_authored_correction_recorded"),
    ("needs_info", "rerun_selected_source_requested"),
    ("superseded", "superseded_candidate"),
    ("archived", "archived_without_promotion"),
)


def prior_run_fixture() -> tuple[dict, bytes]:
    identity = source_map.build_exact_source_snapshot(
        project_id=PROJECT_ID,
        source_document_type="scene",
        source_document_id="scene_001",
        source_document_version="1",
        source_ownership="owner_authored",
        source_content="Owner source.",
        scene_id="scene_001",
    ).identity
    operation = analysis_run_manifest.OperationDeclaration(
        operation_id="fixture-analysis",
        adapter_id="deterministic_fallback",
        consumes=("owner_selected_source",),
        produces=("diagnostic_candidate_finding",),
        configuration={},
        feature_flags={},
    )
    provenance = analysis_run_manifest.AdapterProvenance(
        adapter_id="deterministic_fallback",
        operation_id="fixture-analysis",
        user_facing_label="Fixture analysis",
        implementation_kind="fallback",
        tool=analysis_run_manifest.ProvenanceComponent("unknown"),
        runtime=analysis_run_manifest.ProvenanceComponent("unknown"),
        provider=analysis_run_manifest.ProvenanceComponent("unknown"),
        model=analysis_run_manifest.ProvenanceComponent("unknown"),
    )
    manifest = analysis_run_manifest.AnalysisRunManifest(
        run_id="analysis-run-prior-001",
        project_id=PROJECT_ID,
        sources=(identity,),
        operations=(operation,),
        dependency_graph=(),
        contributors=(
            analysis_run_manifest.ContributorLineage(
                operation_id="fixture-analysis",
                adapter_id="deterministic_fallback",
                source_snapshot_ids=(identity.snapshot_id,),
                result_state="empty",
                coverage="complete",
                explanation="No candidate output is created by this fixture.",
                provenance=provenance,
                output_ids=(),
            ),
        ),
        artifact_references=(),
        outputs=(),
        transformations=(),
        coverage="complete",
        created_at=NOW,
        finalized_at=NOW,
        configuration={},
        feature_flags={},
    )
    raw = apply_contract.canonical_json_bytes(manifest.to_dict())
    return {
        "prior_analysis_run_id": manifest.run_id,
        "prior_analysis_run_manifest_hash": hashlib.sha256(raw).hexdigest(),
        "prior_source_snapshot_id": identity.snapshot_id,
        "prior_source_hash": identity.content_hash,
        "prior_source_locator": candidate()["source_locator"],
        "selected_source_locator": candidate()["source_locator"],
    }, raw


def candidate(
    candidate_id: str = CANDIDATE_ID,
    source_document_id: str = "scene_001",
) -> dict:
    return candidate_record.validate_candidate_record(
        {
            "candidate_id": candidate_id,
            "project_id": PROJECT_ID,
            "candidate_type": "character_candidate",
            "status": "candidate",
            "target_category": "characters",
            "source_locator": {
                "project_id": PROJECT_ID,
                "source_document_type": "scene",
                "source_document_id": source_document_id,
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


def queue_entry(pair=("pending", "owner_review_pending"), **overrides) -> dict:
    entry = candidate_review_gate.build_review_queue_entry(candidate(), project_id=PROJECT_ID)
    entry.update(
        queue_entry_id=QUEUE_ENTRY_ID,
        review_status=pair[0],
        lifecycle_state=pair[1],
        evidence_summary="Evidence summary",
        evidence_refs=["evidence_001"],
        provenance_summary="Fixture provenance",
        provenance_refs=["fixture_orchestrator"],
        review_version=0,
        owner_note="Existing owner note",
        rationale="Existing rationale",
        duplicate_candidate_ids=None,
        rejected_output_reason=None,
        insufficient_evidence_reason=None,
        quarantine_note=None,
        owner_review_completed=False,
        owner_reviewed_at=None,
    )
    entry.update(overrides)
    if pair == ("correction_recorded", "rename_metadata_recorded"):
        entry.update(
            original_owner_visible_label="Original review label",
            requested_owner_visible_label="Corrected review label",
            owner_visible_label="Corrected review label",
        )
    elif pair == (
        "correction_recorded",
        "source_linkage_correction_recorded",
    ):
        entry.update(
            original_source_locator=entry["source_locator"],
            requested_source_locator={
                **entry["source_locator"],
                "source_document_id": "scene_002",
            },
        )
    elif pair == (
        "correction_recorded",
        "owner_authored_correction_recorded",
    ):
        entry["owner_authored_correction"] = "Exact owner correction."
    elif pair == ("superseded", "superseded_candidate"):
        entry.setdefault("superseded_by_candidate_id", TARGET_CANDIDATE_ID)
        entry.setdefault(
            "superseding_target_queue_entry_id", TARGET_QUEUE_ENTRY_ID
        )
        entry.setdefault("superseding_target_review_status", "pending")
        entry.setdefault(
            "superseding_target_lifecycle_state", "owner_review_pending"
        )
        entry.setdefault("superseding_target_review_version", 0)
    elif pair == ("needs_info", "rerun_selected_source_requested"):
        lineage, _ = prior_run_fixture()
        entry.update(lineage)
        entry["prior_run_lineage_verification"] = "verified_analysis_run_manifest"
    return review_queue_storage.validate_review_queue_entry(entry)


def duplicate_target_queue_entry(**overrides) -> dict:
    target_candidate = candidate(TARGET_CANDIDATE_ID, "scene_002")
    entry = candidate_review_gate.build_review_queue_entry(
        target_candidate, project_id=PROJECT_ID
    )
    entry.update(
        queue_entry_id=TARGET_QUEUE_ENTRY_ID,
        review_status="pending",
        lifecycle_state="owner_review_pending",
        review_version=0,
    )
    entry.update(overrides)
    return review_queue_storage.validate_review_queue_entry(entry)


def command(action: str, **overrides) -> dict:
    payload = {
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
    required = {
        "approve": {"owner_note": "Approve for review lifecycle only"},
        "request_more_evidence": {"owner_note": "Need more support"},
        "defer": {"owner_note": "Defer for owner review"},
        "reject": {"owner_note": "Reject after review"},
        "mark_duplicate": {
            "owner_note": "Merge duplicate into the selected candidate",
            "duplicate_candidate_ids": [TARGET_CANDIDATE_ID],
            "duplicate_target_queue_entry_id": TARGET_QUEUE_ENTRY_ID,
            "duplicate_target_expected_review_status": "pending",
            "duplicate_target_expected_version": 0,
        },
        "mark_split_required": {
            "owner_note": "This cluster must be split before further review",
            "rationale": "The source combines independently reviewable claims",
        },
        "rename_candidate_metadata": {
            "owner_note": "Owner requests a review-only display rename",
            "rationale": "The prior display label is misleading",
            "requested_owner_visible_label": "Corrected review label",
        },
        "record_source_linkage_correction": {
            "owner_note": "Owner records corrected source linkage",
            "rationale": "The candidate was linked to the wrong scene",
            "requested_source_locator": {
                "project_id": PROJECT_ID,
                "source_document_type": "scene",
                "source_document_id": "scene_002",
            },
        },
        "mark_superseded": {
            "owner_note": "Owner supersedes this review candidate",
            "rationale": "A newer candidate represents the corrected analysis",
            "superseded_by_candidate_id": TARGET_CANDIDATE_ID,
            "superseding_target_queue_entry_id": TARGET_QUEUE_ENTRY_ID,
            "superseding_target_expected_review_status": "pending",
            "superseding_target_expected_version": 0,
        },
        "record_owner_authored_correction": {
            "owner_note": "Owner records an exact correction",
            "rationale": "The candidate review metadata needs correction",
            "owner_authored_correction": "Exact owner correction.",
        },
        "request_rerun_selected_source": {
            "owner_note": "Owner requests a selected-source rerun.",
            "rationale": "The prior analysis requires another candidate-only review pass.",
            **prior_run_fixture()[0],
        },
        "quarantine": {"owner_note": "Support is invalid"},
        "update_owner_note": {"owner_note": "Updated owner note"},
        "set_review_status": {
            "target_review_status": "deferred",
            "owner_note": "Defer through generic status command",
        },
    }
    payload.update(required.get(action, {}))
    payload.update(overrides)
    return review_api.validate_review_action_command_request(
        payload, project_id=PROJECT_ID, queue_entry_id=QUEUE_ENTRY_ID
    )


@pytest.fixture
def persisted_project(tmp_path: Path) -> tuple[Path, Path]:
    projects = tmp_path / "projects"
    project_manager.create_project("Example", projects_dir=projects)
    project_dir = (projects / PROJECT_ID).resolve()
    candidate_persistence.write_candidate_record(project_dir, candidate())
    candidate_persistence.write_candidate_record(
        project_dir, candidate(TARGET_CANDIDATE_ID, "scene_002")
    )
    review_queue_storage.write_review_queue_entry(queue_entry(), project_dir=project_dir)
    review_queue_storage.write_review_queue_entry(
        duplicate_target_queue_entry(), project_dir=project_dir
    )
    lineage, manifest_raw = prior_run_fixture()
    manifest_path = (
        project_dir
        / "writer_assistant"
        / "analysis_runs"
        / lineage["prior_analysis_run_id"]
        / "manifest.json"
    )
    manifest_path.parent.mkdir(parents=True)
    manifest_path.write_bytes(manifest_raw)
    runtime = tmp_path / "runtime"
    runtime.mkdir(mode=0o700)
    return project_dir, runtime


@pytest.mark.parametrize("action", tuple(review_api._REVIEW_ACTION_ALLOWED_COMMANDS))
def test_each_command_accepts_only_its_allowed_source_pairs(action: str) -> None:
    accepted = review_api._COMMAND_ALLOWED_SOURCE_PAIRS[action]
    for pair in STATE_PAIRS:
        cmd = command(action)
        if action == "set_review_status" and pair == ("archived", "archived_without_promotion"):
            cmd = command(action, target_review_status="pending", owner_note=None)
        if pair in accepted:
            review_api.compute_review_queue_transition(
                queue_entry(pair),
                cmd,
                command_time=NOW,
                duplicate_target=duplicate_target_queue_entry()
                if action == "mark_duplicate"
                else None,
                superseding_target=duplicate_target_queue_entry()
                if action == "mark_superseded"
                else None,
            )
        else:
            with pytest.raises(review_api.ReviewActionUnprocessable):
                review_api.compute_review_queue_transition(
                    queue_entry(pair),
                    cmd,
                    command_time=NOW,
                    duplicate_target=duplicate_target_queue_entry()
                    if action == "mark_duplicate"
                    else None,
                    superseding_target=duplicate_target_queue_entry()
                    if action == "mark_superseded"
                    else None,
                )


def test_set_review_status_derives_exact_target_pairs_and_archive_rule() -> None:
    for status, pair in review_api._TARGET_STATE_PAIRS.items():
        if status in {"duplicate", "split_required", "superseded"}:
            continue
        extras = {}
        if status not in {"pending", "archived"}:
            extras["owner_note"] = "Owner disposition"
        result = review_api.compute_review_queue_transition(
            queue_entry(), command("set_review_status", target_review_status=status, **extras), command_time=NOW
        )
        assert (result["review_status"], result["lifecycle_state"]) == pair
    with pytest.raises(review_api.ReviewActionUnprocessable):
        review_api.compute_review_queue_transition(
            queue_entry(("archived", "archived_without_promotion")),
            command("set_review_status", target_review_status="rejected", owner_note="No"),
            command_time=NOW,
        )

    with pytest.raises(review_api.ReviewActionUnprocessable):
        command(
            "set_review_status",
            target_review_status="duplicate",
            duplicate_candidate_ids=[TARGET_CANDIDATE_ID],
            owner_note="Duplicate",
        )
    with pytest.raises(review_api.ReviewActionUnprocessable):
        command("set_review_status", target_review_status="split_required")
    with pytest.raises(review_api.ReviewActionUnprocessable):
        command("set_review_status", target_review_status="superseded")


def test_each_target_sets_preserves_and_clears_exact_fields() -> None:
    source = queue_entry(
        duplicate_candidate_ids=["core_candidate_old_duplicate"],
        rejected_output_reason="old reject",
        insufficient_evidence_reason="old evidence",
        quarantine_note="old quarantine",
        owner_review_completed=True,
        owner_reviewed_at=NOW,
    )
    result = review_api.compute_review_queue_transition(
        source,
        command("mark_duplicate"),
        command_time=NOW,
        duplicate_target=duplicate_target_queue_entry(),
    )
    assert result["duplicate_candidate_ids"] == [TARGET_CANDIDATE_ID]
    assert result["duplicate_target_queue_entry_id"] == TARGET_QUEUE_ENTRY_ID
    assert result["duplicate_target_review_status"] == "pending"
    assert result["duplicate_target_lifecycle_state"] == "owner_review_pending"
    assert result["duplicate_target_review_version"] == 0
    for field in ("rejected_output_reason", "insufficient_evidence_reason", "quarantine_note"):
        assert result[field] is None
    assert "superseded_by_candidate_id" not in result
    assert result["owner_review_completed"] is True
    assert result["owner_reviewed_at"] == NOW
    assert result["rationale"] == source["rationale"]


@pytest.mark.parametrize(
    ("action", "extras", "expected_pair", "review_complete"),
    (
        (
            "approve",
            {"rationale": "Evidence supports review approval."},
            ("approved", "owner_reviewed_approved"),
            True,
        ),
        (
            "reject",
            {"rejected_output_reason": "Evidence contradicts the claim."},
            ("rejected", "owner_reviewed_rejected"),
            True,
        ),
        (
            "request_more_evidence",
            {"insufficient_evidence_reason": "A second source is required."},
            ("needs_info", "needs_more_evidence"),
            False,
        ),
    ),
)
def test_t011a_dispositions_are_explicit_auditable_review_metadata(
    action: str,
    extras: dict,
    expected_pair: tuple[str, str],
    review_complete: bool,
) -> None:
    source = queue_entry()
    result = review_api.compute_review_queue_transition(
        source,
        command(action, **extras),
        command_time=NOW,
    )
    assert (result["review_status"], result["lifecycle_state"]) == expected_pair
    assert result["owner_review_completed"] is review_complete
    assert result["owner_reviewed_at"] == (NOW if review_complete else None)
    assert result["candidate_record_id"] == source["candidate_record_id"]
    assert result["evidence_refs"] == source["evidence_refs"]
    assert result["provenance_refs"] == source["provenance_refs"]
    for field, value in extras.items():
        assert result[field] == value


@pytest.mark.parametrize(
    "terminal_pair",
    (
        ("approved", "owner_reviewed_approved"),
        ("rejected", "owner_reviewed_rejected"),
    ),
)
@pytest.mark.parametrize(
    "action",
    ("approve", "reject", "request_more_evidence"),
)
def test_t011a_terminal_dispositions_fail_closed_on_repeated_or_conflicting_action(
    terminal_pair: tuple[str, str],
    action: str,
) -> None:
    with pytest.raises(review_api.ReviewActionUnprocessable):
        review_api.compute_review_queue_transition(
            queue_entry(terminal_pair),
            command(action),
            command_time=NOW,
        )


def test_mark_reviewed_sets_completion_without_changing_state() -> None:
    source = queue_entry(insufficient_evidence_reason="keep")
    result = review_api.compute_review_queue_transition(source, command("mark_reviewed"), command_time=NOW)
    assert (result["review_status"], result["lifecycle_state"]) == (source["review_status"], source["lifecycle_state"])
    assert result["owner_review_completed"] is True
    assert result["owner_reviewed_at"] == NOW
    assert result["insufficient_evidence_reason"] == "keep"


def test_update_owner_note_clear_and_completion_preservation() -> None:
    source = queue_entry(owner_review_completed=True, owner_reviewed_at=NOW)
    result = review_api.compute_review_queue_transition(source, command("update_owner_note", owner_note=""), command_time=NOW)
    assert result["owner_note"] is None
    assert result["owner_review_completed"] is True
    assert result["owner_reviewed_at"] == NOW


def test_legacy_version_zero_first_command_and_increment_once() -> None:
    legacy = queue_entry()
    legacy.pop("review_version")
    result = review_api.compute_review_queue_transition(legacy, command("mark_reviewed"), command_time=NOW)
    assert result["review_version"] == 1


@pytest.mark.parametrize("action", tuple(review_api._REVIEW_ACTION_ALLOWED_COMMANDS))
def test_command_candidate_and_evidence_projection_hashes_are_unchanged(
    persisted_project: tuple[Path, Path], action: str
) -> None:
    project_dir, runtime = persisted_project
    before_entry = review_queue_storage.read_review_queue_entry(QUEUE_ENTRY_ID, project_dir=project_dir)
    candidate_path = candidate_storage.candidate_record_path(project_dir, CANDIDATE_ID)
    candidate_before = hashlib.sha256(candidate_path.read_bytes()).hexdigest()
    projection_before = review_api._evidence_provenance_projection_hash(before_entry)
    review_api.execute_review_action_command(command(action), project_id=PROJECT_ID, queue_entry_id=QUEUE_ENTRY_ID, project_dir=project_dir, trusted_runtime_dir=runtime)
    after_entry = review_queue_storage.read_review_queue_entry(QUEUE_ENTRY_ID, project_dir=project_dir)
    assert hashlib.sha256(candidate_path.read_bytes()).hexdigest() == candidate_before
    assert review_api._evidence_provenance_projection_hash(after_entry) == projection_before


@pytest.mark.parametrize("action", tuple(review_api._REVIEW_ACTION_ALLOWED_COMMANDS))
def test_each_command_post_then_authoritative_get_returns_persisted_state(
    persisted_project: tuple[Path, Path], action: str
) -> None:
    project_dir, runtime = persisted_project
    response = review_api.execute_review_action_command(command(action), project_id=PROJECT_ID, queue_entry_id=QUEUE_ENTRY_ID, project_dir=project_dir, trusted_runtime_dir=runtime)
    observed = review_api.get_review_queue_entry_readonly({"project_id": PROJECT_ID, "queue_entry_id": QUEUE_ENTRY_ID}, project_dir=project_dir)["entry"]
    assert response["review_status"] == observed["review_status"]
    assert response["lifecycle_state"] == observed["lifecycle_state"]
    assert response["review_version"] == observed["review_version"] == 1
