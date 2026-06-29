"""PHASE8-IMPL-018-T006 raw artifact safety regression tests.

Raw artifacts are support data only: not canon, not candidates, not training
data, path-safe, and fail-closed. These tests prove the helper cannot be used
as a side-effect path into extraction, model calls, apply-promotion, approved
memory/canon mutation, candidate/review queue creation, or generated prose.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

from backend.story_knowledge import raw_artifacts
from backend.story_knowledge.raw_artifacts import (
    build_raw_artifact_manifest,
    list_raw_artifact_bundles,
    quarantine_raw_artifact_bundle,
    raw_artifact_bundle_storage_dir,
    read_raw_artifact_file,
    read_raw_artifact_manifest,
    rebuild_raw_artifact_index,
    validate_raw_artifact_file_ref,
    validate_raw_artifact_manifest,
    write_raw_artifact_bundle,
)


PROJECT_ID = "example_project"
SOURCE_REF = "source_ref_owner_manuscript_001"
EVIDENCE_REF = "evidence_ref_span_001"
PROVENANCE_REF = "provenance_ref_raw_artifact_adapter_001"
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
        "no_booknlp_spacy_runtime",
        "no_model_calls",
        "no_apply_promotion",
        "no_memory_canon_mutation",
        "no_generated_prose",
        "generated_prose_permanently_forbidden",
        "no_training_artifacts",
    }
)

FORBIDDEN_SIDE_EFFECT_PATHS = (
    "approved_memory",
    "promotion_audit",
    "review_queue",
    "candidates",
    "candidate_index",
    "bible.json",
    "storyform.json",
    "scenes",
    "notes",
    "materials",
    "training",
    "dataset_manifests",
    "model_artifacts",
    "training/reports",
)

FORBIDDEN_CANON_TYPES_AND_DESTINATIONS = (
    "canon",
    "approved_memory",
    "promotion_record",
)

FORBIDDEN_CANDIDATE_TYPES = (
    "candidate_record",
    "review_queue_entry",
)

FORBIDDEN_TRAINING_TYPES_AND_DESTINATIONS = (
    "training_jsonl",
    "dataset_manifest",
    "model_artifact",
)

FORBIDDEN_EXTRACTION_MODEL_AND_PROSE_TYPES = (
    "runtime_extraction_trigger",
    "model_prompt",
    "model_completion",
    "generated_prose",
    "rewritten_prose",
    "continuation",
    "outline",
)

UNSAFE_IDS = (
    "../escape",
    "..",
    ".",
    "/absolute",
    "C:\\escape",
    "folder/name",
    "folder\\name",
    "",
    "   ",
    "raw_bundle.json",
    "raw_bundle_../escape",
)

UNSAFE_RELATIVE_PATHS = (
    "",
    "/absolute/path.jsonl",
    "C:\\absolute\\path.jsonl",
    "../escape.jsonl",
    "artifacts/../../escape.jsonl",
    "artifacts//tokens.jsonl",
    "artifacts/./tokens.jsonl",
    "artifacts/link@symlink",
    "artifacts/.hidden",
    "artifacts/con",
    "artifacts/nul",
)

FORBIDDEN_SOURCE_MARKERS = (
    "import ollama",
    "ollama.",
    "analysis_engine",
    "BookNLP",
    "spacy",
    "subprocess",
    "requests.",
    "urllib.request",
    "run_ncp",
    "run_subtxt",
    "run_dramatica_flow",
    "generate_prose",
    "rewrite_prose",
    "continue_scene",
    "outline_chapter",
)


def project_dir(tmp_path: Path) -> Path:
    return tmp_path / "project-root"


def payload_for(bundle_id: str) -> bytes:
    return json.dumps(
        {"bundle": bundle_id, "kind": "raw artifact support data"},
        sort_keys=True,
    ).encode("utf-8")


def artifact_file_id_for(bundle_id: str) -> str:
    return f"artifact_file_{bundle_id}"


def artifact_file_ref(bundle_id: str, payload: bytes, **overrides) -> dict:
    file_ref = {
        "artifact_file_id": artifact_file_id_for(bundle_id),
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


def manifest_for(bundle_id: str, *, payload: bytes | None = None, **overrides) -> dict:
    payload = payload if payload is not None else payload_for(bundle_id)
    manifest = build_raw_artifact_manifest(
        project_id=PROJECT_ID,
        raw_artifact_bundle_id=bundle_id,
        artifact_files=[artifact_file_ref(bundle_id, payload)],
        created_at="2026-06-28T12:00:00Z",
        status="valid",
        validation_status="valid",
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
    if overrides:
        return manifest
    return validate_raw_artifact_manifest(manifest)


def write_valid_bundle(project: Path, bundle_id: str) -> dict:
    payload = payload_for(bundle_id)
    return write_raw_artifact_bundle(
        manifest_for(bundle_id, payload=payload),
        {artifact_file_id_for(bundle_id): payload},
        project_dir=project,
    )


def forbidden_paths(project: Path) -> list[Path]:
    root = project / "projects" / PROJECT_ID
    return [
        root / "approved_memory",
        root / "promotion_audit",
        root / "review_queue",
        root / "candidates",
        root / "candidate_index",
        root / "bible.json",
        root / "storyform.json",
        root / "scenes",
        root / "notes",
        root / "materials",
        project / "training",
        project / "dataset_manifests",
        project / "model_artifacts",
        project / "training" / "reports",
    ]


def assert_no_forbidden_side_effect_paths(project: Path) -> None:
    assert FORBIDDEN_SIDE_EFFECT_PATHS
    assert all(not path.exists() for path in forbidden_paths(project))


def assert_side_effect_free_result(result: dict) -> None:
    assert result["created_candidates"] == []
    assert result["created_review_queue_entries"] == []
    assert result["apply_promotion_called"] is False
    assert result["approved_memory_mutated"] is False
    assert result["canon_mutated"] is False
    assert result["training_artifacts_written"] == []
    assert result["runtime_extraction_triggered"] is False
    assert result["model_calls"] == []
    assert result["generated_prose"] is None


def test_raw_artifact_operations_remain_support_data_only_without_side_effect_paths(
    tmp_path,
):
    project = project_dir(tmp_path)
    result = write_valid_bundle(project, "raw_bundle_support_only")

    manifest = read_raw_artifact_manifest(
        PROJECT_ID,
        "raw_bundle_support_only",
        project_dir=project,
    )
    payload = read_raw_artifact_file(
        PROJECT_ID,
        "raw_bundle_support_only",
        artifact_file_id_for("raw_bundle_support_only"),
        project_dir=project,
    )
    listed = list_raw_artifact_bundles(PROJECT_ID, project_dir=project)
    index = rebuild_raw_artifact_index(PROJECT_ID, project_dir=project)
    quarantine = quarantine_raw_artifact_bundle(
        PROJECT_ID,
        "raw_bundle_support_only",
        "owner requested support data quarantine",
        project_dir=project,
    )

    assert_side_effect_free_result(result)
    assert_side_effect_free_result(quarantine)
    assert manifest["source_refs"] == [SOURCE_REF]
    assert payload == payload_for("raw_bundle_support_only")
    assert listed[0]["raw_artifact_bundle_id"] == "raw_bundle_support_only"
    assert index["index_type"] == "raw_artifact_support_data_index"
    assert index["not canon"] is True
    assert index["not candidates"] is True
    assert index["not training data"] is True
    assert index["created_candidate_records"] == []
    assert index["created_training_records"] == []
    assert_no_forbidden_side_effect_paths(project)


@pytest.mark.parametrize(
    "forbidden_value",
    FORBIDDEN_CANON_TYPES_AND_DESTINATIONS
    + FORBIDDEN_CANDIDATE_TYPES
    + FORBIDDEN_TRAINING_TYPES_AND_DESTINATIONS
    + FORBIDDEN_EXTRACTION_MODEL_AND_PROSE_TYPES,
)
def test_forbidden_artifact_types_and_destination_like_manifest_values_are_rejected(
    tmp_path,
    forbidden_value,
):
    project = project_dir(tmp_path)
    payload = payload_for("raw_bundle_forbidden_type")

    with pytest.raises(ValueError):
        validate_raw_artifact_file_ref(
            artifact_file_ref(
                "raw_bundle_forbidden_type",
                payload,
                artifact_type=forbidden_value,
            )
        )

    invalid = manifest_for("raw_bundle_forbidden_type", payload=payload)
    invalid["artifact_source_type"] = forbidden_value
    invalid["bundle_hash"] = raw_artifacts.compute_raw_artifact_bundle_hash(invalid)
    with pytest.raises(ValueError):
        write_raw_artifact_bundle(
            invalid,
            {artifact_file_id_for("raw_bundle_forbidden_type"): payload},
            project_dir=project,
        )
    assert not (project / "projects").exists()


@pytest.mark.parametrize("field", ("destination", "action", "approved_memory"))
def test_forbidden_manifest_destination_or_action_fields_fail_closed_before_writes(
    tmp_path,
    field,
):
    project = project_dir(tmp_path)
    payload = payload_for("raw_bundle_forbidden_field")
    invalid = manifest_for("raw_bundle_forbidden_field", payload=payload)
    invalid[field] = "canon"

    with pytest.raises(ValueError):
        write_raw_artifact_bundle(
            invalid,
            {artifact_file_id_for("raw_bundle_forbidden_field"): payload},
            project_dir=project,
        )
    assert not (project / "projects").exists()


@pytest.mark.parametrize("unsafe_id", UNSAFE_IDS)
def test_project_bundle_and_file_ids_are_path_safe_and_fail_closed(unsafe_id, tmp_path):
    project = project_dir(tmp_path)
    payload = payload_for("raw_bundle_path_safe")

    with pytest.raises(ValueError):
        raw_artifact_bundle_storage_dir(project, unsafe_id, "raw_bundle_path_safe")
    with pytest.raises(ValueError):
        raw_artifact_bundle_storage_dir(project, PROJECT_ID, unsafe_id)
    with pytest.raises(ValueError):
        validate_raw_artifact_file_ref(
            artifact_file_ref(
                "raw_bundle_path_safe",
                payload,
                artifact_file_id=unsafe_id,
            )
        )
    assert not (project / "projects").exists()


@pytest.mark.parametrize("relative_path", UNSAFE_RELATIVE_PATHS)
def test_relative_paths_are_path_safe_and_fail_closed_before_writes(
    relative_path,
    tmp_path,
):
    project = project_dir(tmp_path)
    payload = payload_for("raw_bundle_unsafe_path")

    with pytest.raises(ValueError):
        build_raw_artifact_manifest(
            project_id=PROJECT_ID,
            raw_artifact_bundle_id="raw_bundle_unsafe_path",
            artifact_files=[
                artifact_file_ref(
                    "raw_bundle_unsafe_path",
                    payload,
                    relative_path=relative_path,
                )
            ],
            artifact_source_type="fixture_adapter_output",
            artifact_source_id="raw_adapter_run_unsafe_path",
            source_refs=[SOURCE_REF],
            evidence_refs=[EVIDENCE_REF],
            provenance_refs=[PROVENANCE_REF],
            source_locator_refs=[SOURCE_LOCATOR_REF],
            no_generated_prose_confirmation=True,
            no_model_call_confirmation=True,
            no_training_artifact_confirmation=True,
            no_apply_promotion_confirmation=True,
            no_memory_canon_mutation_confirmation=True,
            no_runtime_extraction_confirmation=True,
        )
    assert not (project / "projects").exists()


def test_unreferenced_missing_and_hash_mismatched_artifact_reads_fail_closed(tmp_path):
    project = project_dir(tmp_path)
    write_valid_bundle(project, "raw_bundle_read_safety")

    with pytest.raises(ValueError):
        read_raw_artifact_file(
            PROJECT_ID,
            "raw_bundle_read_safety",
            "artifact_file_unreferenced",
            project_dir=project,
        )

    bundle_dir = raw_artifact_bundle_storage_dir(
        project,
        PROJECT_ID,
        "raw_bundle_read_safety",
    )
    referenced_file = bundle_dir / "artifacts" / "raw_bundle_read_safety.jsonl"
    referenced_file.unlink()
    with pytest.raises(ValueError):
        read_raw_artifact_file(
            PROJECT_ID,
            "raw_bundle_read_safety",
            artifact_file_id_for("raw_bundle_read_safety"),
            project_dir=project,
        )

    write_valid_bundle(project, "raw_bundle_hash_mismatch")
    mismatched_file = (
        raw_artifact_bundle_storage_dir(project, PROJECT_ID, "raw_bundle_hash_mismatch")
        / "artifacts"
        / "raw_bundle_hash_mismatch.jsonl"
    )
    mismatched_file.write_bytes(b"tampered support data")
    with pytest.raises(ValueError):
        read_raw_artifact_file(
            PROJECT_ID,
            "raw_bundle_hash_mismatch",
            artifact_file_id_for("raw_bundle_hash_mismatch"),
            project_dir=project,
        )


def test_payload_hash_and_size_mismatch_fail_closed_for_valid_reads_and_indexing(
    tmp_path,
):
    project = project_dir(tmp_path)
    payload = payload_for("raw_bundle_payload_mismatch")
    manifest = manifest_for("raw_bundle_payload_mismatch", payload=payload)

    write_raw_artifact_bundle(
        manifest,
        {artifact_file_id_for("raw_bundle_payload_mismatch"): b"wrong"},
        project_dir=project,
    )

    assert list_raw_artifact_bundles(PROJECT_ID, project_dir=project) == []
    assert rebuild_raw_artifact_index(PROJECT_ID, project_dir=project)["bundles"] == []
    with pytest.raises(ValueError):
        read_raw_artifact_file(
            PROJECT_ID,
            "raw_bundle_payload_mismatch",
            artifact_file_id_for("raw_bundle_payload_mismatch"),
            project_dir=project,
        )


def test_invalid_manifests_and_refs_fail_before_partial_writes(tmp_path):
    project = project_dir(tmp_path)
    valid = manifest_for("raw_bundle_invalid_manifest")
    invalid_cases = []
    for field in ("source_refs", "provenance_refs"):
        invalid = copy.deepcopy(valid)
        invalid[field] = []
        invalid_cases.append(invalid)
    for confirmation in (
        "no_generated_prose_confirmation",
        "no_model_call_confirmation",
        "no_training_artifact_confirmation",
        "no_apply_promotion_confirmation",
        "no_memory_canon_mutation_confirmation",
        "no_runtime_extraction_confirmation",
    ):
        invalid = copy.deepcopy(valid)
        invalid[confirmation] = False
        invalid_cases.append(invalid)
    for field, value in (
        ("status", "trusted_truth"),
        ("validation_status", "trusted_truth"),
    ):
        invalid = copy.deepcopy(valid)
        invalid[field] = value
        invalid_cases.append(invalid)
    invalid = copy.deepcopy(valid)
    invalid["artifact_files"][0]["artifact_type"] = "canon"
    invalid_cases.append(invalid)
    invalid = copy.deepcopy(valid)
    invalid["artifact_files"].append(copy.deepcopy(valid["artifact_files"][0]))
    invalid_cases.append(invalid)

    for index, invalid_manifest in enumerate(invalid_cases):
        with pytest.raises(ValueError):
            write_raw_artifact_bundle(
                invalid_manifest,
                {artifact_file_id_for("raw_bundle_invalid_manifest"): payload_for("x")},
                project_dir=project / f"case_{index}",
            )
        assert not (project / f"case_{index}" / "projects").exists()


def test_invalid_json_manifest_on_disk_is_excluded_from_list_and_index(tmp_path):
    project = project_dir(tmp_path)
    invalid_dir = (
        project
        / "projects"
        / PROJECT_ID
        / "writer_assistant"
        / "raw_artifacts"
        / "raw_bundle_invalid_json"
    )
    invalid_dir.mkdir(parents=True)
    (invalid_dir / "manifest.json").write_text("{", encoding="utf-8")

    assert list_raw_artifact_bundles(PROJECT_ID, project_dir=project) == []
    assert rebuild_raw_artifact_index(PROJECT_ID, project_dir=project)["bundles"] == []
    assert_no_forbidden_side_effect_paths(project)


def test_quarantine_is_not_valid_evidence_and_has_no_promotion_or_queue_side_effects(
    tmp_path,
):
    project = project_dir(tmp_path)
    write_valid_bundle(project, "raw_bundle_quarantine_safety")

    result = quarantine_raw_artifact_bundle(
        PROJECT_ID,
        "raw_bundle_quarantine_safety",
        "hash mismatch in support data",
        project_dir=project,
    )
    manifest_path = (
        raw_artifact_bundle_storage_dir(
            project,
            PROJECT_ID,
            "raw_bundle_quarantine_safety",
        )
        / "manifest.json"
    )
    quarantined = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert result["quarantine_reason"] == "hash mismatch in support data"
    assert result["valid_evidence"] is False
    assert quarantined["status"] == "quarantined"
    assert quarantined["quarantine_reason"] == "hash mismatch in support data"
    assert list_raw_artifact_bundles(PROJECT_ID, project_dir=project) == []
    assert rebuild_raw_artifact_index(PROJECT_ID, project_dir=project)["bundles"] == []
    assert_side_effect_free_result(result)
    assert_no_forbidden_side_effect_paths(project)


def test_raw_artifact_source_has_no_extraction_model_apply_promotion_or_prose_paths():
    source_text = Path(raw_artifacts.__file__).read_text(
        encoding="utf-8",
        errors="ignore",
    )
    assert "import apply_promotion" not in source_text
    assert "apply-promotion" not in source_text
    assert "promotion_audit" not in source_text
    assert "review_queue" not in source_text
    assert "candidate_index" not in source_text
    assert "bible.json" not in source_text
    assert "storyform.json" not in source_text
    assert "scenes/" not in source_text
    assert "notes/" not in source_text
    assert "materials/" not in source_text
    assert "training/" not in source_text
    assert all(marker not in source_text for marker in FORBIDDEN_SOURCE_MARKERS)
    assert "runtime_extraction_trigger" in source_text
    assert "model_prompt" in source_text
    assert "model_completion" in source_text
    assert "generated_prose" in source_text
    assert "rewritten_prose" in source_text
    assert "continuation" in source_text
    assert "outline" in source_text
