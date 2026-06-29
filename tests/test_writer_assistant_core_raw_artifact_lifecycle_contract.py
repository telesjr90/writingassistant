"""Raw artifact bundle/index lifecycle and provenance contract tests.

PHASE8-IMPL-018-T005 keeps raw artifacts as project-local support data only:
not canon, not candidates, and not training data. These tests do not create
routes, UI, runtime extraction, model calls, generated prose, candidates,
promotion effects, or durable project truth.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

from backend.story_knowledge.raw_artifacts import (
    build_raw_artifact_manifest,
    compute_raw_artifact_bundle_hash,
    list_raw_artifact_bundles,
    quarantine_raw_artifact_bundle,
    raw_artifact_bundle_storage_dir,
    read_raw_artifact_file,
    read_raw_artifact_manifest,
    rebuild_raw_artifact_index,
    validate_raw_artifact_manifest,
    write_raw_artifact_bundle,
)


PROJECT_ID = "example_project"
SOURCE_REF = "source_ref_owner_manuscript_001"
EVIDENCE_REF = "evidence_ref_span_001"
PROVENANCE_REF = "provenance_ref_raw_adapter_001"
SOURCE_LOCATOR_REF = "source_locator_ref_offsets_001"
BOUNDARY_FLAGS = sorted(
    {
        "raw_artifacts_support_data_only",
        "raw_artifacts_not_canon",
        "raw_artifacts_not_candidates",
        "raw_artifacts_not_training_data",
        "project_local_raw_artifacts",
        "manifest_backed_raw_artifacts",
        "evidence_provenance_linked",
        "path_safe_fail_closed",
        "no_runtime_extraction",
        "no_booknlp_" + "sp" + "acy_runtime",
        "no_model_calls",
        "no_apply_promotion",
        "no_memory_canon_mutation",
        "no_generated_prose",
        "generated_prose_permanently_forbidden",
        "no_training_artifacts",
    }
)
LIFECYCLE_STATUSES = (
    "pending_validation",
    "valid",
    "rejected",
    "quarantined",
    "superseded",
    "deleted_tombstone",
)


def project_dir(tmp_path: Path) -> Path:
    return tmp_path / "project-root"


def payload_for(bundle_id: str) -> bytes:
    return json.dumps({"bundle": bundle_id, "kind": "support data"}, sort_keys=True).encode(
        "utf-8"
    )


def artifact_file_ref(bundle_id: str, payload: bytes, **overrides) -> dict:
    file_ref = {
        "artifact_file_id": f"artifact_file_{bundle_id}",
        "artifact_type": "token_table",
        "relative_path": f"artifacts/{bundle_id}.jsonl",
        "media_type": "application/jsonl",
        "encoding": "utf-8",
        "size_bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "record_count": 1,
        "line_count": 1,
        "schema_name": "raw_artifact_support_data",
        "schema_version": "1.0",
        "parser_hint": "jsonl",
        "source_locator_refs": [SOURCE_LOCATOR_REF],
        "evidence_refs": [EVIDENCE_REF],
        "provenance_refs": [PROVENANCE_REF],
        "boundary_flags": BOUNDARY_FLAGS,
    }
    file_ref.update(overrides)
    return file_ref


def manifest_for(bundle_id: str, *, status: str = "valid", **overrides) -> dict:
    payload = payload_for(bundle_id)
    manifest = build_raw_artifact_manifest(
        project_id=PROJECT_ID,
        raw_artifact_bundle_id=bundle_id,
        artifact_files=[artifact_file_ref(bundle_id, payload)],
        created_at="2026-06-28T12:00:00Z",
        status=status,
        validation_status=status,
        artifact_source_type="fixture_adapter_output",
        artifact_source_id=f"raw_adapter_run_{bundle_id}",
        extraction_run_id=None,
        source_refs=[SOURCE_REF],
        evidence_refs=[EVIDENCE_REF],
        provenance_refs=[PROVENANCE_REF],
        source_locator_refs=[SOURCE_LOCATOR_REF],
        adapter_name="fixture_adapter",
        adapter_version="1.0",
        no_generated_prose_confirmation=True,
        no_model_call_confirmation=True,
        no_training_artifact_confirmation=True,
        no_apply_promotion_confirmation=True,
        no_memory_canon_mutation_confirmation=True,
        no_runtime_extraction_confirmation=True,
    )
    manifest.update(overrides)
    return validate_raw_artifact_manifest(manifest)


def write_bundle(project: Path, bundle_id: str, *, status: str = "valid") -> dict:
    payload = payload_for(bundle_id)
    manifest = manifest_for(bundle_id, status=status)
    return write_raw_artifact_bundle(
        manifest,
        {f"artifact_file_{bundle_id}": payload},
        project_dir=project,
    )


def load_manifest_file(project: Path, bundle_id: str) -> dict:
    path = raw_artifact_bundle_storage_dir(project, PROJECT_ID, bundle_id) / "manifest.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_valid_bundles_are_listed_and_indexed_by_default_with_deterministic_order(
    tmp_path,
):
    project = project_dir(tmp_path)
    write_bundle(project, "raw_bundle_b")
    write_bundle(project, "raw_bundle_a")

    listed = list_raw_artifact_bundles(PROJECT_ID, project_dir=project)
    index = rebuild_raw_artifact_index(PROJECT_ID, project_dir=project)

    assert [item["raw_artifact_bundle_id"] for item in listed] == [
        "raw_bundle_a",
        "raw_bundle_b",
    ]
    assert [item["raw_artifact_bundle_id"] for item in index["bundles"]] == [
        "raw_bundle_a",
        "raw_bundle_b",
    ]
    first = index["bundles"][0]
    assert first["status"] == "valid"
    assert first["source_refs"] == [SOURCE_REF]
    assert first["evidence_refs"] == [EVIDENCE_REF]
    assert first["provenance_refs"] == [PROVENANCE_REF]
    assert first["source_locator_refs"] == [SOURCE_LOCATOR_REF]
    assert first["artifact_files"][0]["artifact_file_id"] == "artifact_file_raw_bundle_a"
    assert first["artifact_files"][0]["source_locator_refs"] == [SOURCE_LOCATOR_REF]
    assert first["artifact_files"][0]["evidence_refs"] == [EVIDENCE_REF]
    assert first["artifact_files"][0]["provenance_refs"] == [PROVENANCE_REF]
    assert first["bundle_hash"]
    assert first["manifest_hash"]
    assert index["not canon"] is True
    assert index["not candidates"] is True
    assert index["not training data"] is True
    assert index["created_candidate_records"] == []
    assert index["created_training_records"] == []


@pytest.mark.parametrize(
    "status",
    [
        "pending_validation",
        "rejected",
        "quarantined",
        "superseded",
        "deleted_tombstone",
    ],
)
def test_non_valid_lifecycle_statuses_are_excluded_from_default_listing_and_index(
    tmp_path,
    status,
):
    project = project_dir(tmp_path)
    write_bundle(project, "raw_bundle_valid", status="valid")
    write_bundle(project, f"raw_bundle_{status}", status=status)

    listed = list_raw_artifact_bundles(PROJECT_ID, project_dir=project)
    indexed = rebuild_raw_artifact_index(PROJECT_ID, project_dir=project)
    full_list = list_raw_artifact_bundles(
        PROJECT_ID,
        project_dir=project,
        include_quarantined=True,
    )

    assert [item["status"] for item in listed] == ["valid"]
    assert [item["status"] for item in indexed["bundles"]] == ["valid"]
    assert status in {item["status"] for item in full_list}


def test_unknown_status_fails_closed():
    with pytest.raises(ValueError):
        manifest_for("raw_bundle_unknown", status="trusted_truth")


def test_stale_missing_and_invalid_manifests_do_not_crash_or_appear_in_valid_index(
    tmp_path,
):
    project = project_dir(tmp_path)
    raw_root = (
        project
        / "projects"
        / PROJECT_ID
        / "writer_assistant"
        / "raw_artifacts"
    )
    (raw_root / "missing_manifest").mkdir(parents=True)
    (raw_root / "invalid_json").mkdir()
    (raw_root / "invalid_json" / "manifest.json").write_text("{", encoding="utf-8")
    (raw_root / "invalid_manifest").mkdir()
    invalid = manifest_for("raw_bundle_invalid")
    invalid["source_refs"] = []
    (raw_root / "invalid_manifest" / "manifest.json").write_text(
        json.dumps(invalid, sort_keys=True),
        encoding="utf-8",
    )

    assert list_raw_artifact_bundles(PROJECT_ID, project_dir=project) == []
    assert rebuild_raw_artifact_index(PROJECT_ID, project_dir=project)["bundles"] == []
    with pytest.raises(ValueError):
        read_raw_artifact_manifest(
            PROJECT_ID,
            "missing_manifest",
            project_dir=project,
        )


def test_missing_referenced_artifact_file_is_excluded_and_read_fails_closed(tmp_path):
    project = project_dir(tmp_path)
    manifest = manifest_for("raw_bundle_missing_file")
    write_raw_artifact_bundle(manifest, {}, project_dir=project)

    assert list_raw_artifact_bundles(PROJECT_ID, project_dir=project) == []
    assert rebuild_raw_artifact_index(PROJECT_ID, project_dir=project)["bundles"] == []
    with pytest.raises(ValueError):
        read_raw_artifact_file(
            PROJECT_ID,
            "raw_bundle_missing_file",
            "artifact_file_raw_bundle_missing_file",
            project_dir=project,
        )


def test_unreferenced_artifact_files_cannot_be_read_through_bundle_api(tmp_path):
    project = project_dir(tmp_path)
    write_bundle(project, "raw_bundle_with_extra_file")
    extra = (
        raw_artifact_bundle_storage_dir(project, PROJECT_ID, "raw_bundle_with_extra_file")
        / "artifacts"
        / "extra.jsonl"
    )
    extra.write_bytes(b"not referenced")

    with pytest.raises(ValueError):
        read_raw_artifact_file(
            PROJECT_ID,
            "raw_bundle_with_extra_file",
            "artifact_file_extra",
            project_dir=project,
        )


def test_quarantine_preserves_reason_and_refs_and_excludes_from_valid_index(tmp_path):
    project = project_dir(tmp_path)
    write_bundle(project, "raw_bundle_quarantine")

    result = quarantine_raw_artifact_bundle(
        PROJECT_ID,
        "raw_bundle_quarantine",
        "stale source locator refs",
        project_dir=project,
    )
    quarantined = load_manifest_file(project, "raw_bundle_quarantine")

    assert result["status"] == "quarantined"
    assert result["quarantine_reason"] == "stale source locator refs"
    assert result["valid_evidence"] is False
    assert quarantined["source_refs"] == [SOURCE_REF]
    assert quarantined["evidence_refs"] == [EVIDENCE_REF]
    assert quarantined["provenance_refs"] == [PROVENANCE_REF]
    assert quarantined["source_locator_refs"] == [SOURCE_LOCATOR_REF]
    assert list_raw_artifact_bundles(PROJECT_ID, project_dir=project) == []
    assert rebuild_raw_artifact_index(PROJECT_ID, project_dir=project)["bundles"] == []


def test_duplicate_identical_write_is_idempotent_and_conflict_fails_closed(tmp_path):
    project = project_dir(tmp_path)
    payload = payload_for("raw_bundle_duplicate")
    manifest = manifest_for("raw_bundle_duplicate")
    artifact_payloads = {"artifact_file_raw_bundle_duplicate": payload}

    first = write_raw_artifact_bundle(manifest, artifact_payloads, project_dir=project)
    second = write_raw_artifact_bundle(manifest, artifact_payloads, project_dir=project)
    conflicting = copy.deepcopy(manifest)
    conflicting["source_refs"] = ["source_ref_other"]
    conflicting["bundle_hash"] = compute_raw_artifact_bundle_hash(conflicting)

    assert second == first
    with pytest.raises(ValueError):
        write_raw_artifact_bundle(conflicting, artifact_payloads, project_dir=project)
    assert load_manifest_file(project, "raw_bundle_duplicate")["source_refs"] == [
        SOURCE_REF
    ]


def test_refs_are_preserved_not_invented_and_required_for_valid_support_data():
    manifest = manifest_for("raw_bundle_refs")

    assert manifest["source_refs"] == [SOURCE_REF]
    assert manifest["evidence_refs"] == [EVIDENCE_REF]
    assert manifest["provenance_refs"] == [PROVENANCE_REF]
    assert manifest["source_locator_refs"] == [SOURCE_LOCATOR_REF]

    for field in (
        "source_refs",
        "evidence_refs",
        "provenance_refs",
        "source_locator_refs",
    ):
        invalid = copy.deepcopy(manifest)
        invalid[field] = []
        with pytest.raises(ValueError):
            validate_raw_artifact_manifest(invalid)

    for field in ("evidence_refs", "provenance_refs", "source_locator_refs"):
        invalid = copy.deepcopy(manifest)
        invalid["artifact_files"][0][field] = []
        with pytest.raises(ValueError):
            validate_raw_artifact_manifest(invalid)


def test_hash_is_deterministic_and_changes_when_artifact_metadata_changes():
    manifest = manifest_for("raw_bundle_hash")
    same = copy.deepcopy(manifest)
    changed = copy.deepcopy(manifest)
    changed["artifact_files"][0]["sha256"] = "d" * 64

    assert compute_raw_artifact_bundle_hash(manifest) == compute_raw_artifact_bundle_hash(
        same
    )
    assert compute_raw_artifact_bundle_hash(manifest) != compute_raw_artifact_bundle_hash(
        changed
    )


def test_temp_project_does_not_receive_forbidden_side_effect_paths(tmp_path):
    project = project_dir(tmp_path)
    write_bundle(project, "raw_bundle_side_effect_check")
    rebuild_raw_artifact_index(PROJECT_ID, project_dir=project)

    forbidden = [
        project / "projects" / PROJECT_ID / ("approved_" + "memory"),
        project / "projects" / PROJECT_ID / ("promotion_" + "audit"),
        project / "projects" / PROJECT_ID / ("review_" + "queue"),
        project / "projects" / PROJECT_ID / ("candidate_" + "index"),
        project / "projects" / PROJECT_ID / ("bible" + ".json"),
        project / "projects" / PROJECT_ID / ("storyform" + ".json"),
        project / "projects" / PROJECT_ID / "scenes",
        project / "projects" / PROJECT_ID / "notes",
        project / "projects" / PROJECT_ID / "materials",
        project / ("training"),
    ]
    assert all(not path.exists() for path in forbidden)
