"""T011F owner-controlled rerun request and prior-run lineage coverage."""

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
    review_action_events,
    review_queue_storage,
    source_map,
)


PROJECT_ID = "example"
CANDIDATE_ID = "core_candidate_rerun_source_001"
QUEUE_ENTRY_ID = "review_queue_entry_rerun_source_001"
RUN_ID = "analysis-run-prior-001"
NOW = "2026-08-09T20:00:00Z"


def _candidate() -> dict:
    locator = {
        "project_id": PROJECT_ID,
        "source_document_type": "scene",
        "source_document_id": "scene_001",
        "scene_id": "scene_001",
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
                    "evidence_id": "evidence_rerun_001",
                    "source_locator": locator,
                    "summary": "Evidence remains attached to the source candidate.",
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


def _manifest() -> tuple[analysis_run_manifest.AnalysisRunManifest, bytes]:
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
        run_id=RUN_ID,
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
                explanation="This prior run produced no candidate fixture output.",
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
    return manifest, apply_contract.canonical_json_bytes(manifest.to_dict())


def _command(**overrides) -> dict:
    manifest, raw = _manifest()
    locator = _candidate()["source_locator"]
    value = {
        "action_type": "request_rerun_selected_source",
        "queue_entry_id": QUEUE_ENTRY_ID,
        "candidate_id": CANDIDATE_ID,
        "actor": "owner-reviewed",
        "owner_confirmed": True,
        "preserve_candidate_linkage": True,
        "preserve_evidence_provenance": True,
        "idempotency_key": str(uuid.uuid4()),
        "expected_current_review_status": "pending",
        "expected_current_version": 0,
        "owner_note": "Owner requests a rerun of this selected source.",
        "rationale": "Prior analysis needs another candidate-only review pass.",
        "prior_analysis_run_id": manifest.run_id,
        "prior_analysis_run_manifest_hash": hashlib.sha256(raw).hexdigest(),
        "prior_source_snapshot_id": manifest.sources[0].snapshot_id,
        "prior_source_hash": manifest.sources[0].content_hash,
        "prior_source_locator": locator,
        "selected_source_locator": locator,
    }
    value.update(overrides)
    return value


@pytest.fixture
def rerun_project(tmp_path: Path) -> tuple[Path, Path]:
    projects = tmp_path / "projects"
    project_manager.create_project("Example", projects_dir=projects)
    project_dir = (projects / PROJECT_ID).resolve()
    candidate = _candidate()
    candidate_persistence.write_candidate_record(project_dir, candidate)
    entry = candidate_review_gate.build_review_queue_entry(
        candidate, project_id=PROJECT_ID
    )
    entry.update(
        queue_entry_id=QUEUE_ENTRY_ID,
        review_status="pending",
        lifecycle_state="owner_review_pending",
        review_version=0,
        evidence_summary="Retained evidence summary",
        evidence_refs=["evidence_rerun_001"],
        provenance_summary="fixture_orchestrator",
        provenance_refs=["fixture_orchestrator"],
    )
    review_queue_storage.write_review_queue_entry(entry, project_dir=project_dir)
    manifest, raw = _manifest()
    manifest_path = (
        project_dir
        / "writer_assistant"
        / "analysis_runs"
        / manifest.run_id
        / "manifest.json"
    )
    manifest_path.parent.mkdir(parents=True)
    manifest_path.write_bytes(raw)
    runtime = tmp_path / "runtime"
    runtime.mkdir(mode=0o700)
    return project_dir, runtime


def _execute(value: dict, roots: tuple[Path, Path]) -> dict:
    return review_api.execute_review_action_command(
        value,
        project_id=PROJECT_ID,
        queue_entry_id=QUEUE_ENTRY_ID,
        project_dir=roots[0],
        trusted_runtime_dir=roots[1],
    )


def _snapshot(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file()
    }


def test_rerun_request_persists_verified_lineage_without_execution_or_mutation(
    rerun_project,
):
    project_dir, _ = rerun_project
    candidate_path = candidate_storage.candidate_record_path(project_dir, CANDIDATE_ID)
    candidate_before = candidate_path.read_bytes()
    source_before = review_queue_storage.read_review_queue_entry(
        QUEUE_ENTRY_ID, project_dir=project_dir
    )
    request = _command()

    response = _execute(request, rerun_project)
    replay = _execute(request, rerun_project)
    persisted = review_queue_storage.read_review_queue_entry(
        QUEUE_ENTRY_ID, project_dir=project_dir
    )
    chain = review_action_events.scan_review_action_event_chain(
        project_dir=project_dir,
        project_id=PROJECT_ID,
        queue_entry_id=QUEUE_ENTRY_ID,
    )

    assert response["review_status"] == "needs_info"
    assert response["lifecycle_state"] == "rerun_selected_source_requested"
    assert response["replay"] is False
    assert replay["replay"] is True
    assert replay["action_id"] == response["action_id"]
    assert len(chain) == 2
    assert chain[0]["action_command"] == "request_rerun_selected_source"
    assert review_api._decode_intent_target(chain[0]) == persisted
    assert persisted["prior_run_lineage_verification"] == (
        "verified_analysis_run_manifest"
    )
    for field in (
        "prior_analysis_run_id",
        "prior_analysis_run_manifest_hash",
        "prior_source_snapshot_id",
        "prior_source_hash",
        "prior_source_locator",
        "selected_source_locator",
    ):
        assert persisted[field] == request[field]
        assert response[field] == request[field]
    assert persisted["source_locator"] == source_before["source_locator"]
    assert persisted["evidence_refs"] == source_before["evidence_refs"]
    assert persisted["provenance_refs"] == source_before["provenance_refs"]
    assert candidate_path.read_bytes() == candidate_before
    workflow = response["review_workflow_state"]
    assert workflow["rerun_request_scope"] == "review_lifecycle_metadata_only"
    for flag in (
        "is_canon",
        "promotion_created",
        "apply_promotion_performed",
        "memory_canon_mutation_performed",
        "project_truth_mutation_performed",
        "candidate_record_mutation_performed",
        "source_candidate_deleted",
        "generated_prose_performed",
        "runtime_extraction_performed",
        "model_call_performed",
        "rerun_execution_performed",
        "candidate_generation_performed",
    ):
        assert workflow[flag] is False


@pytest.mark.parametrize(
    ("overrides", "error_code"),
    (
        ({"prior_analysis_run_manifest_hash": "0" * 64}, "REVIEW_ACTION_INVALID_PRIOR_RUN_LINEAGE"),
        ({"prior_source_hash": "0" * 64}, "REVIEW_ACTION_INVALID_PRIOR_RUN_LINEAGE"),
        ({"prior_source_snapshot_id": "missing-snapshot"}, "REVIEW_ACTION_INVALID_PRIOR_RUN_LINEAGE"),
        ({"prior_analysis_run_id": "missing-run"}, "REVIEW_ACTION_PRIOR_RUN_NOT_FOUND"),
    ),
)
def test_invalid_or_unknown_prior_lineage_fails_before_durable_review_writes(
    rerun_project, overrides, error_code
):
    project_dir, _ = rerun_project
    before = _snapshot(project_dir)
    with pytest.raises(review_api.ReviewActionCommandError) as exc_info:
        _execute(_command(**overrides), rerun_project)
    assert exc_info.value.payload["error_code"] == error_code
    assert _snapshot(project_dir) == before


@pytest.mark.parametrize(
    "overrides",
    (
        {"prior_analysis_run_id": "../unsafe"},
        {"prior_analysis_run_manifest_hash": "A" * 64},
        {
            "selected_source_locator": {
                "project_id": "another-project",
                "source_document_type": "scene",
                "source_document_id": "scene_001",
                "scene_id": "scene_001",
            }
        },
    ),
)
def test_unsafe_ids_hashes_and_cross_project_selected_sources_fail_closed(overrides):
    with pytest.raises(review_api.ReviewActionUnprocessable):
        review_api.validate_review_action_command_request(
            _command(**overrides),
            project_id=PROJECT_ID,
            queue_entry_id=QUEUE_ENTRY_ID,
        )


def test_rerun_metadata_is_state_specific_and_generic_status_cannot_create_it():
    candidate = _candidate()
    entry = candidate_review_gate.build_review_queue_entry(
        candidate, project_id=PROJECT_ID
    )
    entry.update(
        queue_entry_id=QUEUE_ENTRY_ID,
        review_status="pending",
        lifecycle_state="owner_review_pending",
    )
    command = review_api.validate_review_action_command_request(
        _command(), project_id=PROJECT_ID, queue_entry_id=QUEUE_ENTRY_ID
    )
    target = review_api.compute_review_queue_transition(
        review_queue_storage.validate_review_queue_entry(entry),
        command,
        command_time=NOW,
    )
    assert target["owner_review_completed"] is False
    mixed = dict(entry)
    mixed.update({field: target[field] for field in (
        "prior_analysis_run_id",
        "prior_analysis_run_manifest_hash",
        "prior_source_snapshot_id",
        "prior_source_hash",
        "prior_source_locator",
        "selected_source_locator",
        "prior_run_lineage_verification",
    )})
    with pytest.raises(ValueError):
        review_queue_storage.validate_review_queue_entry(mixed)
    with pytest.raises(ValueError):
        review_action_events.build_action_intent_event_v1(
            sequence=1,
            previous_event_hash=None,
            project_id=PROJECT_ID,
            queue_entry_id=QUEUE_ENTRY_ID,
            candidate_record_id=CANDIDATE_ID,
            action_command="set_review_status",
            action_id="rvact_fixture_001",
            idempotency_key=str(uuid.uuid4()),
            request_hash="a" * 64,
            created_at=NOW,
            queue_before_hash="b" * 64,
            target_queue_canonical_bytes_b64url=__import__("base64").urlsafe_b64encode(
                apply_contract.canonical_json_bytes(target)
            ).rstrip(b"=").decode("ascii"),
            target_queue_hash=hashlib.sha256(
                apply_contract.canonical_json_bytes(target)
            ).hexdigest(),
            candidate_before_hash="c" * 64,
            evidence_projection_before_hash="d" * 64,
        )


def test_rerun_request_is_terminal_without_an_explicit_reopen(rerun_project):
    _execute(_command(), rerun_project)
    with pytest.raises(review_api.ReviewActionUnprocessable) as exc_info:
        _execute(
            _command(
                idempotency_key=str(uuid.uuid4()),
                expected_current_review_status="needs_info",
                expected_current_version=1,
            ),
            rerun_project,
        )
    assert exc_info.value.payload["error_code"] == "REVIEW_ACTION_INVALID_TRANSITION"
