"""Expected-red contract tests for future raw artifact persistence APIs.

PHASE8-IMPL-018-T003 is tests-first only. The future pure raw artifact
persistence module is imported normally so this targeted file is expected red
until a later authorized implementation task creates it:

- backend.story_knowledge.raw_artifacts

Expected future public APIs:

- validate_raw_artifact_manifest(manifest: dict) -> dict
- build_raw_artifact_manifest(*, project_id: str, raw_artifact_bundle_id: str, artifact_files: list[dict], **metadata) -> dict
- validate_raw_artifact_file_ref(file_ref: dict) -> dict
- raw_artifact_bundle_storage_dir(project_dir, project_id: str, raw_artifact_bundle_id: str)
- raw_artifact_manifest_path(project_dir, project_id: str, raw_artifact_bundle_id: str)
- raw_artifact_index_path(project_dir, project_id: str, raw_artifact_bundle_id: str)
- write_raw_artifact_bundle(manifest: dict, artifact_files: dict, *, project_dir) -> dict
- read_raw_artifact_manifest(project_id: str, raw_artifact_bundle_id: str, *, project_dir) -> dict
- read_raw_artifact_file(project_id: str, raw_artifact_bundle_id: str, artifact_file_id: str, *, project_dir) -> bytes
- list_raw_artifact_bundles(project_id: str, *, project_dir, include_quarantined: bool = False) -> list[dict]
- rebuild_raw_artifact_index(project_id: str, *, project_dir) -> dict
- quarantine_raw_artifact_bundle(project_id: str, raw_artifact_bundle_id: str, reason: str, *, project_dir) -> dict
- compute_raw_artifact_bundle_hash(manifest: dict) -> str

These tests encode the PHASE8-IMPL-018-T002 raw artifact persistence boundary
and manifest model decision. Raw artifacts are support data, not canon, not
candidates, and not training data. These tests do not implement raw artifact
persistence helpers, do not write raw artifact files or indexes, do not run
runtime extraction, do not import or run BookNLP/spaCy, do not call models or
Ollama, do not call NCP/Subtxt/dramatica-flow runtimes, do not call
apply-promotion, do not mutate approved memory/canon, and do not create
generated prose, JSONL, datasets, manifests, or model artifacts.
"""

from __future__ import annotations

import copy
import hashlib
from pathlib import Path

import pytest

# The future module is imported normally; expected red until T004 creates it.
from backend.story_knowledge.raw_artifacts import (
    build_raw_artifact_manifest,
    compute_raw_artifact_bundle_hash,
    list_raw_artifact_bundles,
    quarantine_raw_artifact_bundle,
    raw_artifact_bundle_storage_dir,
    raw_artifact_index_path,
    raw_artifact_manifest_path,
    read_raw_artifact_file,
    read_raw_artifact_manifest,
    rebuild_raw_artifact_index,
    validate_raw_artifact_file_ref,
    validate_raw_artifact_manifest,
    write_raw_artifact_bundle,
)


PROJECT_ID = "example_project"
RAW_ARTIFACT_BUNDLE_ID = "raw_bundle_booknlp_fixture_001"
ARTIFACT_FILE_ID = "artifact_file_tokens_001"
SOURCE_REF = "source_ref_owner_manuscript_001"
EVIDENCE_REF = "evidence_ref_scene_001_span_001"
PROVENANCE_REF = "provenance_ref_fixture_adapter_001"
SOURCE_LOCATOR_REF = "source_locator_ref_scene_001_offsets_001"

EXPECTED_PUBLIC_API = (
    "validate_raw_artifact_manifest",
    "build_raw_artifact_manifest",
    "validate_raw_artifact_file_ref",
    "raw_artifact_bundle_storage_dir",
    "raw_artifact_manifest_path",
    "raw_artifact_index_path",
    "write_raw_artifact_bundle",
    "read_raw_artifact_manifest",
    "read_raw_artifact_file",
    "list_raw_artifact_bundles",
    "rebuild_raw_artifact_index",
    "quarantine_raw_artifact_bundle",
    "compute_raw_artifact_bundle_hash",
)

REQUIRED_MANIFEST_FIELDS = frozenset(
    {
        "schema_version",
        "raw_artifact_bundle_id",
        "project_id",
        "created_at",
        "updated_at",
        "status",
        "artifact_source_type",
        "artifact_source_id",
        "extraction_run_id",
        "source_refs",
        "evidence_refs",
        "provenance_refs",
        "source_locator_refs",
        "tool_name",
        "tool_version",
        "adapter_name",
        "adapter_version",
        "pipeline_name",
        "pipeline_version",
        "artifact_files",
        "bundle_hash",
        "boundary_flags",
        "validation_status",
        "quarantine_reason",
        "no_generated_prose_confirmation",
        "no_model_call_confirmation",
        "no_training_artifact_confirmation",
        "no_apply_promotion_confirmation",
        "no_memory_canon_mutation_confirmation",
        "no_runtime_extraction_confirmation",
    }
)

MANIFEST_HASH_FIELDS = frozenset({"manifest_hash", "content_hash"})

REQUIRED_ARTIFACT_FILE_FIELDS = frozenset(
    {
        "artifact_file_id",
        "artifact_type",
        "relative_path",
        "media_type",
        "encoding",
        "size_bytes",
        "sha256",
        "record_count",
        "line_count",
        "schema_name",
        "schema_version",
        "parser_hint",
        "source_locator_refs",
        "evidence_refs",
        "provenance_refs",
        "boundary_flags",
    }
)

ALLOWED_RAW_ARTIFACT_STATUSES = (
    "pending_validation",
    "valid",
    "rejected",
    "quarantined",
    "superseded",
    "deleted_tombstone",
)

ALLOWED_SUPPORT_DATA_ARTIFACT_TYPES = (
    "source_snapshot",
    "token_table",
    "entity_table",
    "quote_table",
    "event_table",
    "coref_table",
    "dependency_table",
    "offset_map",
    "source_map",
    "evidence_map",
    "provenance_map",
    "adapter_metadata",
    "parser_metadata",
    "normalized_intermediate",
)

FORBIDDEN_ARTIFACT_TYPES_DESTINATIONS_AND_ACTIONS = (
    "canon",
    "approved_memory",
    "candidate_record",
    "review_queue_entry",
    "promotion_record",
    "training_jsonl",
    "dataset_manifest",
    "model_artifact",
    "generated_prose",
    "rewritten_prose",
    "continuation",
    "outline",
    "model_prompt",
    "model_completion",
    "runtime_extraction_trigger",
)

FORBIDDEN_PATH_PATTERNS = (
    "../escape.json",
    "..",
    ".",
    "/absolute/path.json",  # absolute paths
    "C:\\absolute\\path.json",
    "artifacts/../../escape.json",  # path traversal
    "artifacts//tokens.jsonl",
    "artifacts/./tokens.jsonl",
    "artifacts/link@symlink",
    "artifacts/.hidden_escape",
    "artifacts/con",
    "artifacts/nul",
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
    "raw_bundle/../../escape",
    "raw_bundle_../escape",
)

REQUIRED_BOUNDARY_FLAGS = frozenset(
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


def project_dir(tmp_path: Path) -> Path:
    return tmp_path / "project-root"


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def valid_artifact_file_ref(**overrides):
    file_ref = {
        "artifact_file_id": ARTIFACT_FILE_ID,
        "artifact_type": "token_table",
        "relative_path": "artifacts/tokens.jsonl",
        "media_type": "application/jsonl",
        "encoding": "utf-8",
        "size_bytes": 128,
        "sha256": "a" * 64,
        "record_count": 3,
        "line_count": 3,
        "schema_name": "booknlp_tokens",
        "schema_version": "1.0",
        "parser_hint": "jsonl",
        "source_locator_refs": [SOURCE_LOCATOR_REF],
        "evidence_refs": [EVIDENCE_REF],
        "provenance_refs": [PROVENANCE_REF],
        "boundary_flags": sorted(REQUIRED_BOUNDARY_FLAGS),
    }
    file_ref.update(overrides)
    return file_ref


def valid_manifest(**overrides):
    manifest = {
        "schema_version": "1.0",
        "raw_artifact_bundle_id": RAW_ARTIFACT_BUNDLE_ID,
        "project_id": PROJECT_ID,
        "created_at": "2026-06-28T12:00:00Z",
        "updated_at": None,
        "status": "valid",
        "artifact_source_type": "fixture_adapter_output",
        "artifact_source_id": "booknlp_fixture_adapter_run_001",
        "extraction_run_id": None,
        "source_refs": [SOURCE_REF],
        "evidence_refs": [EVIDENCE_REF],
        "provenance_refs": [PROVENANCE_REF],
        "source_locator_refs": [SOURCE_LOCATOR_REF],
        "tool_name": None,
        "tool_version": None,
        "adapter_name": "booknlp_fixture_adapter",
        "adapter_version": "1.0",
        "pipeline_name": None,
        "pipeline_version": None,
        "artifact_files": [valid_artifact_file_ref()],
        "bundle_hash": "b" * 64,
        "manifest_hash": "c" * 64,
        "boundary_flags": sorted(REQUIRED_BOUNDARY_FLAGS),
        "validation_status": "valid",
        "quarantine_reason": None,
        "no_generated_prose_confirmation": True,
        "no_model_call_confirmation": True,
        "no_training_artifact_confirmation": True,
        "no_apply_promotion_confirmation": True,
        "no_memory_canon_mutation_confirmation": True,
        "no_runtime_extraction_confirmation": True,
    }
    manifest.update(overrides)
    return manifest


def test_future_raw_artifact_module_public_api_import_contract():
    imported = {
        name
        for name in EXPECTED_PUBLIC_API
        if globals().get(name) is not None
    }
    assert imported == set(EXPECTED_PUBLIC_API)


def test_validate_raw_artifact_manifest_requires_required_fields_and_hash():
    manifest = valid_manifest()
    result = validate_raw_artifact_manifest(manifest)
    assert result["validation_status"] == "valid"

    for field in REQUIRED_MANIFEST_FIELDS:
        invalid = copy.deepcopy(manifest)
        invalid.pop(field)
        with pytest.raises(ValueError):
            validate_raw_artifact_manifest(invalid)

    invalid_without_hash = copy.deepcopy(manifest)
    for field in MANIFEST_HASH_FIELDS:
        invalid_without_hash.pop(field, None)
    with pytest.raises(ValueError):
        validate_raw_artifact_manifest(invalid_without_hash)


@pytest.mark.parametrize("status", ALLOWED_RAW_ARTIFACT_STATUSES)
def test_validate_raw_artifact_manifest_accepts_only_allowlisted_statuses(status):
    manifest = valid_manifest(status=status, validation_status=status)
    result = validate_raw_artifact_manifest(manifest)
    assert result["status"] == status


def test_validate_raw_artifact_manifest_rejects_unknown_status_fail_closed():
    manifest = valid_manifest(status="trusted_truth", validation_status="trusted_truth")
    with pytest.raises(ValueError):
        validate_raw_artifact_manifest(manifest)


def test_validate_raw_artifact_file_ref_requires_required_fields():
    file_ref = valid_artifact_file_ref()
    result = validate_raw_artifact_file_ref(file_ref)
    assert result["artifact_file_id"] == ARTIFACT_FILE_ID

    for field in REQUIRED_ARTIFACT_FILE_FIELDS:
        invalid = copy.deepcopy(file_ref)
        invalid.pop(field)
        with pytest.raises(ValueError):
            validate_raw_artifact_file_ref(invalid)


@pytest.mark.parametrize("artifact_type", ALLOWED_SUPPORT_DATA_ARTIFACT_TYPES)
def test_validate_raw_artifact_file_ref_accepts_support_data_artifact_types_only(
    artifact_type,
):
    file_ref = valid_artifact_file_ref(artifact_type=artifact_type)
    result = validate_raw_artifact_file_ref(file_ref)
    assert result["artifact_type"] == artifact_type


@pytest.mark.parametrize(
    "forbidden_value", FORBIDDEN_ARTIFACT_TYPES_DESTINATIONS_AND_ACTIONS
)
def test_validate_raw_artifact_file_ref_rejects_forbidden_artifact_types_destinations_and_actions(
    forbidden_value,
):
    file_ref = valid_artifact_file_ref(artifact_type=forbidden_value)
    with pytest.raises(ValueError):
        validate_raw_artifact_file_ref(file_ref)


@pytest.mark.parametrize("unsafe_relative_path", FORBIDDEN_PATH_PATTERNS)
def test_validate_raw_artifact_file_ref_rejects_absolute_paths_path_traversal_and_reserved_patterns(
    unsafe_relative_path,
):
    file_ref = valid_artifact_file_ref(relative_path=unsafe_relative_path)
    with pytest.raises(ValueError):
        validate_raw_artifact_file_ref(file_ref)


@pytest.mark.parametrize("unsafe_id", UNSAFE_IDS)
def test_validate_raw_artifact_manifest_rejects_unsafe_project_id(unsafe_id):
    manifest = valid_manifest(project_id=unsafe_id)
    with pytest.raises(ValueError):
        validate_raw_artifact_manifest(manifest)


@pytest.mark.parametrize("unsafe_id", UNSAFE_IDS)
def test_validate_raw_artifact_manifest_rejects_unsafe_raw_artifact_bundle_id(
    unsafe_id,
):
    manifest = valid_manifest(raw_artifact_bundle_id=unsafe_id)
    with pytest.raises(ValueError):
        validate_raw_artifact_manifest(manifest)


@pytest.mark.parametrize("unsafe_id", UNSAFE_IDS)
def test_validate_raw_artifact_file_ref_rejects_unsafe_artifact_file_id(unsafe_id):
    file_ref = valid_artifact_file_ref(artifact_file_id=unsafe_id)
    with pytest.raises(ValueError):
        validate_raw_artifact_file_ref(file_ref)


def test_raw_artifact_storage_path_helpers_are_project_local_and_deterministic(tmp_path):
    project = project_dir(tmp_path)
    bundle_dir = raw_artifact_bundle_storage_dir(
        project, PROJECT_ID, RAW_ARTIFACT_BUNDLE_ID
    )
    manifest_path = raw_artifact_manifest_path(
        project, PROJECT_ID, RAW_ARTIFACT_BUNDLE_ID
    )
    index_path = raw_artifact_index_path(project, PROJECT_ID, RAW_ARTIFACT_BUNDLE_ID)

    expected_bundle_dir = (
        project
        / "projects"
        / PROJECT_ID
        / "writer_assistant"
        / "raw_artifacts"
        / RAW_ARTIFACT_BUNDLE_ID
    )
    assert bundle_dir == expected_bundle_dir
    assert manifest_path == expected_bundle_dir / "manifest.json"
    assert index_path == expected_bundle_dir / "indexes" / "index.json"
    assert is_relative_to(bundle_dir, project)
    assert is_relative_to(manifest_path, bundle_dir)
    assert is_relative_to(index_path, bundle_dir)
    assert not bundle_dir.exists()
    assert not manifest_path.exists()
    assert not index_path.exists()


def test_build_raw_artifact_manifest_requires_source_evidence_provenance_linkage():
    manifest = build_raw_artifact_manifest(
        project_id=PROJECT_ID,
        raw_artifact_bundle_id=RAW_ARTIFACT_BUNDLE_ID,
        artifact_files=[valid_artifact_file_ref()],
        artifact_source_type="fixture_adapter_output",
        artifact_source_id="booknlp_fixture_adapter_run_001",
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
    assert manifest["source_refs"] == [SOURCE_REF]
    assert manifest["evidence_refs"] == [EVIDENCE_REF]
    assert manifest["provenance_refs"] == [PROVENANCE_REF]
    assert manifest["source_locator_refs"] == [SOURCE_LOCATOR_REF]

    for required_link in ("source_refs", "provenance_refs"):
        kwargs = {
            "project_id": PROJECT_ID,
            "raw_artifact_bundle_id": RAW_ARTIFACT_BUNDLE_ID,
            "artifact_files": [valid_artifact_file_ref()],
            "artifact_source_type": "fixture_adapter_output",
            "artifact_source_id": "booknlp_fixture_adapter_run_001",
            "source_refs": [SOURCE_REF],
            "evidence_refs": [EVIDENCE_REF],
            "provenance_refs": [PROVENANCE_REF],
            "source_locator_refs": [SOURCE_LOCATOR_REF],
        }
        kwargs[required_link] = []
        with pytest.raises(ValueError):
            build_raw_artifact_manifest(**kwargs)


def test_write_raw_artifact_bundle_validates_first_and_writes_manifest_plus_artifact_files_only(
    tmp_path,
):
    project = project_dir(tmp_path)
    manifest = valid_manifest()
    artifact_payloads = {ARTIFACT_FILE_ID: b'{"token": "support data only"}\n'}

    result = write_raw_artifact_bundle(manifest, artifact_payloads, project_dir=project)

    assert result["raw_artifact_bundle_id"] == RAW_ARTIFACT_BUNDLE_ID
    assert result["created_candidates"] == []
    assert result["created_review_queue_entries"] == []
    assert result["apply_promotion_called"] is False
    assert result["approved_memory_mutated"] is False
    assert result["canon_mutated"] is False
    assert result["training_artifacts_written"] == []
    assert result["runtime_extraction_triggered"] is False
    assert result["model_calls"] == []
    assert result["generated_prose"] is None

    invalid = valid_manifest(status="canon")
    with pytest.raises(ValueError):
        write_raw_artifact_bundle(invalid, artifact_payloads, project_dir=project)


def test_write_raw_artifact_bundle_avoids_partial_writes_when_validation_fails(tmp_path):
    project = project_dir(tmp_path)
    invalid = valid_manifest(source_refs=[])

    with pytest.raises(ValueError):
        write_raw_artifact_bundle(
            invalid,
            {ARTIFACT_FILE_ID: b"invalid support data"},
            project_dir=project,
        )

    assert not (project / "projects").exists()


def test_read_manifest_and_file_are_limited_to_valid_project_local_manifest_refs(
    tmp_path,
):
    project = project_dir(tmp_path)
    payload = b'{"token": "support data only"}\n'
    file_ref = valid_artifact_file_ref(sha256=hashlib.sha256(payload).hexdigest())
    manifest = valid_manifest(artifact_files=[file_ref])
    write_raw_artifact_bundle(manifest, {ARTIFACT_FILE_ID: payload}, project_dir=project)

    manifest = read_raw_artifact_manifest(
        PROJECT_ID, RAW_ARTIFACT_BUNDLE_ID, project_dir=project
    )
    payload = read_raw_artifact_file(
        PROJECT_ID, RAW_ARTIFACT_BUNDLE_ID, ARTIFACT_FILE_ID, project_dir=project
    )

    assert validate_raw_artifact_manifest(manifest)["status"] == "valid"
    assert isinstance(payload, bytes)

    with pytest.raises(ValueError):
        read_raw_artifact_file(
            PROJECT_ID,
            RAW_ARTIFACT_BUNDLE_ID,
            "../escape",
            project_dir=project,
        )


def test_list_and_rebuild_index_keep_indexes_as_rebuildable_support_data_only(
    tmp_path,
):
    project = project_dir(tmp_path)

    listed = list_raw_artifact_bundles(PROJECT_ID, project_dir=project)
    rebuilt = rebuild_raw_artifact_index(PROJECT_ID, project_dir=project)

    assert all(item["status"] == "valid" for item in listed)
    assert all(item["status"] != "quarantined" for item in listed)
    assert rebuilt["index_type"] == "raw_artifact_support_data_index"
    assert rebuilt["not canon"] is True
    assert rebuilt["not candidates"] is True
    assert rebuilt["not training data"] is True
    assert rebuilt["created_candidate_records"] == []
    assert rebuilt["created_training_records"] == []


def test_list_raw_artifact_bundles_excludes_quarantined_invalid_bundles_by_default(
    tmp_path,
):
    project = project_dir(tmp_path)

    default_list = list_raw_artifact_bundles(PROJECT_ID, project_dir=project)
    full_list = list_raw_artifact_bundles(
        PROJECT_ID,
        project_dir=project,
        include_quarantined=True,
    )

    assert all(item["status"] != "quarantined" for item in default_list)
    assert len(full_list) >= len(default_list)


def test_quarantine_raw_artifact_bundle_records_reason_and_never_marks_valid_evidence(
    tmp_path,
):
    project = project_dir(tmp_path)

    result = quarantine_raw_artifact_bundle(
        PROJECT_ID,
        RAW_ARTIFACT_BUNDLE_ID,
        "missing required source/provenance linkage",
        project_dir=project,
    )

    assert result["status"] in {"quarantined", "rejected"}
    assert result["quarantine_reason"] == "missing required source/provenance linkage"
    assert result["valid_evidence"] is False
    assert result["created_candidates"] == []
    assert result["apply_promotion_called"] is False
    assert result["approved_memory_mutated"] is False
    assert result["canon_mutated"] is False
    assert result["runtime_extraction_triggered"] is False
    assert result["model_calls"] == []
    assert result["generated_prose"] is None


def test_compute_raw_artifact_bundle_hash_is_deterministic_and_content_metadata_sensitive():
    manifest = valid_manifest()

    first = compute_raw_artifact_bundle_hash(manifest)
    second = compute_raw_artifact_bundle_hash(copy.deepcopy(manifest))
    changed = copy.deepcopy(manifest)
    changed["artifact_files"][0]["sha256"] = "d" * 64

    assert first == second
    assert first != compute_raw_artifact_bundle_hash(changed)


def test_duplicate_bundle_ids_are_idempotent_or_rejected_fail_closed(tmp_path):
    project = project_dir(tmp_path)
    manifest = valid_manifest()
    conflicting = valid_manifest(source_refs=["source_ref_other"])

    first = write_raw_artifact_bundle(
        manifest,
        {ARTIFACT_FILE_ID: b"support data"},
        project_dir=project,
    )
    second = write_raw_artifact_bundle(
        manifest,
        {ARTIFACT_FILE_ID: b"support data"},
        project_dir=project,
    )

    assert second == first
    with pytest.raises(ValueError):
        write_raw_artifact_bundle(
            conflicting,
            {ARTIFACT_FILE_ID: b"conflict"},
            project_dir=project,
        )


def test_raw_artifact_persistence_api_exposes_no_runtime_no_prose_no_training_actions():
    forbidden_runtime_or_prose_actions = {
        "run_booknlp",
        "run_spacy",
        "install_booknlp",
        "install_spacy",
        "call_ollama",
        "call_model",
        "run_ncp",
        "run_subtxt",
        "run_dramatica_flow",
        "generate_prose",
        "rewrite_prose",
        "continue_scene",
        "outline_story",
        "create_training_jsonl",
        "write_dataset_manifest",
        "write_model_artifact",
        "apply_promotion",
        "write_approved_memory",
        "write_canon",
    }
    assert forbidden_runtime_or_prose_actions.isdisjoint(set(EXPECTED_PUBLIC_API))


@pytest.mark.parametrize("forbidden_value", FORBIDDEN_ARTIFACT_TYPES_DESTINATIONS_AND_ACTIONS)
def test_validate_raw_artifact_manifest_rejects_forbidden_destinations_anywhere_fail_closed(
    forbidden_value,
):
    manifest = valid_manifest(
        artifact_source_type=forbidden_value,
        boundary_flags=sorted(REQUIRED_BOUNDARY_FLAGS | {forbidden_value}),
    )

    with pytest.raises(ValueError):
        validate_raw_artifact_manifest(manifest)
