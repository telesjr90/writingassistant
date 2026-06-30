"""PHASE8-IMPL-019-T006 runtime extraction safety regression tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from backend.story_knowledge.raw_artifacts import read_raw_artifact_file
from backend.story_knowledge.runtime_extraction import (
    build_raw_artifact_handoff,
    build_runtime_extraction_plan,
    persist_runtime_extraction_raw_artifacts,
    quarantine_runtime_extraction_output,
    run_guarded_runtime_extraction,
    run_runtime_extraction_probe,
    validate_runtime_extraction_environment,
    validate_runtime_extraction_request,
)


PROJECT_ID = "example_project"
EXTRACTION_REQUEST_ID = "runtime_extract_001"
SOURCE_ID = "owner_scene_001"
SOURCE_REF = "source_ref_owner_scene_001"
EVIDENCE_REF = "evidence_ref_owner_scene_001_span_001"
PROVENANCE_REF = "provenance_ref_runtime_probe_001"
SOURCE_LOCATOR_REF = "source_locator_ref_owner_scene_001_offsets_001"
RAW_ARTIFACT_BUNDLE_ID = "raw_artifact_runtime_001"

REQUIRED_BOUNDARY_CONFIRMATIONS = (
    "owner_authored_or_owner_provided_source_confirmation",
    "no_generated_prose_confirmation",
    "no_model_call_confirmation",
    "no_training_artifact_confirmation",
    "no_apply_promotion_confirmation",
    "no_memory_canon_mutation_confirmation",
    "raw_artifact_support_data_only_confirmation",
    "candidate_first_owner_review_required_confirmation",
)

FORBIDDEN_DESTINATIONS = (
    "approved_memory",
    "memory",
    "canon",
    "promotion_audit",
    "review_queue",
    "candidates",
    "candidate_index",
    "training",
    "dataset",
    "model_artifacts",
    "bible.json",
    "storyform.json",
    "scenes",
    "notes",
    "materials",
)

FORBIDDEN_ARTIFACTS = (
    "generated_prose",
    "rewritten_prose",
    "continuation",
    "outline",
    "model_prompt",
    "model_completion",
    "training_jsonl",
    "dataset_manifest",
    "model_artifact",
    "promotion_record",
    "candidate_record",
    "review_queue_entry",
    "approved_memory",
    "canon",
    "bible",
    "storyform",
    "scene_mutation",
    "note_mutation",
    "material_mutation",
)

UNSUCCESSFUL_STATUSES = (
    "disabled",
    "unavailable",
    "dependency_missing",
    "model_missing",
    "configuration_invalid",
    "probe_failed",
    "runtime_failed",
    "malformed_output",
    "unsafe_path",
    "quarantined",
    "rejected",
    "fail_closed",
)


def _valid_request() -> dict:
    return {
        "project_id": PROJECT_ID,
        "extraction_request_id": EXTRACTION_REQUEST_ID,
        "source_type": "owner_authored_scene",
        "source_id": SOURCE_ID,
        "source_ref": SOURCE_REF,
        "requested_extractors": ["booknlp", "spacy"],
        "requested_artifact_types": ["token_table", "entity_table", "source_map"],
        "source_refs": [SOURCE_REF],
        "evidence_refs": [EVIDENCE_REF],
        "provenance_refs": [PROVENANCE_REF],
        "source_locator_refs": [SOURCE_LOCATOR_REF],
        "source_locators": [
            {
                "source_locator_ref": SOURCE_LOCATOR_REF,
                "source_ref": SOURCE_REF,
                "start_offset": 0,
                "end_offset": 42,
            }
        ],
        "boundary_confirmations": {
            key: True for key in REQUIRED_BOUNDARY_CONFIRMATIONS
        },
        "environment_profile": "local_guarded_runtime",
        "max_input_chars": 5000,
        "timeout_seconds": 30,
        "requested_by": "owner",
        "created_at": "2026-06-30T00:00:00Z",
    }


def _valid_environment() -> dict:
    return {
        "status": "configured",
        "runtime_extraction_enabled": True,
        "booknlp": {"status": "valid", "fail_closed": False},
        "spacy": {"status": "valid", "fail_closed": False},
        "availability": {
            "booknlp": {"status": "valid", "fail_closed": False},
            "spacy": {"status": "valid", "fail_closed": False},
        },
        "fail_closed": False,
        "errors": [],
        "warnings": [],
        "no_silent_fallback": True,
        "no_model_calls": True,
        "no_generated_prose": True,
        "no_training_artifacts": True,
    }


def _runtime_output() -> dict:
    return {
        "status": "valid",
        "project_id": PROJECT_ID,
        "extraction_request_id": EXTRACTION_REQUEST_ID,
        "raw_artifact_bundle_id": RAW_ARTIFACT_BUNDLE_ID,
        "extraction_run_id": "runtime_probe_run_001",
        "tool_name": "spacy",
        "tool_version": "probe_only",
        "adapter_name": "guarded_runtime_adapter",
        "adapter_version": "1",
        "pipeline_name": "raw_artifact_handoff",
        "pipeline_version": "1",
        "source_refs": [SOURCE_REF],
        "evidence_refs": [EVIDENCE_REF],
        "provenance_refs": [PROVENANCE_REF],
        "source_locator_refs": [SOURCE_LOCATOR_REF],
        "artifact_files": [
            {
                "artifact_file_id": "tokens_001",
                "artifact_type": "token_table",
                "relative_path": "artifacts/tokens.json",
                "source_locator_refs": [SOURCE_LOCATOR_REF],
                "evidence_refs": [EVIDENCE_REF],
                "provenance_refs": [PROVENANCE_REF],
                "record_count": 1,
                "line_count": 1,
                "schema_name": "runtime_token_support_data",
                "schema_version": "1",
                "parser_hint": "json",
            }
        ],
        "artifact_payloads": {
            "tokens_001": [
                {
                    "token": "OwnerProvidedToken",
                    "source_ref": SOURCE_REF,
                    "source_locator_ref": SOURCE_LOCATOR_REF,
                    "evidence_ref": EVIDENCE_REF,
                    "provenance_ref": PROVENANCE_REF,
                }
            ]
        },
    }


def _assert_fail_closed(result: dict, expected_status: str | None = None) -> None:
    if expected_status is not None:
        assert result["status"] == expected_status
    assert result.get("fail_closed") is True
    assert result.get("extraction_succeeded") is not True
    assert result.get("no_silent_fallback") is True


def _assert_no_forbidden_files(project_dir: Path) -> None:
    for path in project_dir.rglob("*"):
        relative = path.relative_to(project_dir)
        parts = set(relative.parts)
        assert not (parts & set(FORBIDDEN_DESTINATIONS)), relative
        assert relative.name not in FORBIDDEN_DESTINATIONS, relative


def _assert_no_runtime_side_effect_flags(result: dict) -> None:
    assert result.get("canon_write_performed") is False
    assert result.get("apply_promotion_performed") is False
    assert result.get("candidate_persistence_performed") is False
    assert result.get("review_queue_write_performed") is False
    assert result.get("model_call_performed") is False
    assert result.get("generated_prose") is False
    assert result.get("training_artifact_created") is False


def test_valid_support_data_persistence_writes_only_raw_artifact_bundle(
    tmp_path: Path,
) -> None:
    result = persist_runtime_extraction_raw_artifacts(
        _runtime_output(),
        project_dir=tmp_path,
    )

    assert result["status"] == "valid"
    assert result["support_data_only"] is True
    assert result["raw_artifacts_not_canon"] is True
    assert result["raw_artifacts_not_approved_memory"] is True
    assert result["raw_artifacts_not_candidates"] is True
    assert result["raw_artifacts_not_training_data"] is True
    assert result["extraction_succeeded"] is False
    _assert_no_runtime_side_effect_flags(result)

    raw_root = (
        tmp_path
        / "projects"
        / PROJECT_ID
        / "writer_assistant"
        / "raw_artifacts"
        / RAW_ARTIFACT_BUNDLE_ID
    )
    assert raw_root.is_dir()
    assert Path(result["manifest_path"]).is_relative_to(raw_root)
    payload = read_raw_artifact_file(
        PROJECT_ID,
        RAW_ARTIFACT_BUNDLE_ID,
        "tokens_001",
        project_dir=tmp_path,
    )
    decoded = json.loads(payload.decode("utf-8"))
    assert decoded[0]["source_ref"] == SOURCE_REF
    _assert_no_forbidden_files(tmp_path)


@pytest.mark.parametrize(
    "source_path",
    (
        "../escape.txt",
        "safe/../../escape.txt",
        "/tmp/escape.txt",
        "C:\\escape.txt",
        "safe\\escape.txt",
        "",
        ".",
    ),
)
def test_source_paths_with_traversal_or_absolute_forms_fail_closed(
    source_path: str,
) -> None:
    request = _valid_request()
    request["source_path"] = source_path

    result = validate_runtime_extraction_request(request)

    _assert_fail_closed(result, "unsafe_path")


@pytest.mark.parametrize("field", ("project_id", "extraction_request_id", "source_id"))
@pytest.mark.parametrize("unsafe_value", ("../escape", "/absolute", "folder/name", "bad.id", ""))
def test_unsafe_project_request_and_source_ids_fail_closed(
    field: str,
    unsafe_value: str,
) -> None:
    request = _valid_request()
    request[field] = unsafe_value

    result = validate_runtime_extraction_request(request)

    _assert_fail_closed(result, "unsafe_path")


@pytest.mark.parametrize(
    "source_type",
    ("assistant_generated", "model_output", "third_party_unapproved", "project_unknown"),
)
def test_unsupported_or_non_owner_source_claims_fail_closed(source_type: str) -> None:
    request = _valid_request()
    request["source_type"] = source_type

    result = validate_runtime_extraction_request(request)

    _assert_fail_closed(result, "rejected")
    assert result["owner_authored_or_owner_provided_source"] is False


@pytest.mark.parametrize(
    ("field", "expected_status"),
    (
        ("source_refs", "missing_source_refs"),
        ("evidence_refs", "missing_evidence_refs"),
        ("provenance_refs", "missing_provenance_refs"),
        ("source_locator_refs", "missing_source_locator_refs"),
    ),
)
def test_required_refs_are_not_optional(field: str, expected_status: str) -> None:
    request = _valid_request()
    request[field] = []

    result = validate_runtime_extraction_request(request)

    _assert_fail_closed(result, expected_status)


@pytest.mark.parametrize(
    "locator_patch",
    (
        {"source_locator_ref": "unknown_locator"},
        {"source_ref": "unknown_source"},
        {"start_offset": -1},
        {"end_offset": -1},
        {"start_offset": 42, "end_offset": 42},
        {"end_offset": 5001},
        {"start_offset": "0"},
    ),
)
def test_invalid_source_locators_and_offsets_fail_closed(locator_patch: dict) -> None:
    request = _valid_request()
    request["source_locators"][0].update(locator_patch)

    result = validate_runtime_extraction_request(request)

    _assert_fail_closed(result)
    assert any(result["status"] == status for status in {
        "unsafe_path",
        "missing_source_refs",
        "missing_source_locator_refs",
    })


@pytest.mark.parametrize("forbidden_artifact", FORBIDDEN_ARTIFACTS)
def test_forbidden_requested_artifacts_are_rejected(forbidden_artifact: str) -> None:
    request = _valid_request()
    request["requested_artifact_types"] = [forbidden_artifact]

    result = validate_runtime_extraction_request(request)

    _assert_fail_closed(result, "rejected")
    assert result["no_model_calls"] is True
    assert result["no_generated_prose"] is True
    assert result["no_training_artifacts"] is True
    assert result["no_apply_promotion"] is True
    assert result["no_memory_canon_mutation"] is True


@pytest.mark.parametrize("forbidden_artifact", FORBIDDEN_ARTIFACTS)
def test_forbidden_raw_artifact_types_are_not_valid_handoffs(
    tmp_path: Path,
    forbidden_artifact: str,
) -> None:
    output = _runtime_output()
    output["artifact_files"][0]["artifact_type"] = forbidden_artifact

    result = build_raw_artifact_handoff(output, project_dir=tmp_path)

    assert result["status"] == "quarantined"
    assert result["excluded_from_valid_handoff"] is True
    assert result["indexed_as_valid"] is False
    _assert_fail_closed(result)
    _assert_no_runtime_side_effect_flags(result)
    _assert_no_forbidden_files(tmp_path)


@pytest.mark.parametrize(
    "relative_path",
    (
        "../escape.json",
        "/tmp/escape.json",
        "C:\\escape.json",
        "approved_memory/tokens.json",
        "memory/tokens.json",
        "canon/tokens.json",
        "promotion_audit/tokens.json",
        "review_queue/tokens.json",
        "candidates/tokens.json",
        "candidate_index/tokens.json",
        "training/tokens.json",
        "dataset/tokens.json",
        "model_artifacts/tokens.json",
        "bible.json",
        "storyform.json",
        "scenes/tokens.json",
        "notes/tokens.json",
        "materials/tokens.json",
    ),
)
def test_unsafe_raw_artifact_relative_paths_are_rejected(
    tmp_path: Path,
    relative_path: str,
) -> None:
    output = _runtime_output()
    output["artifact_files"][0]["relative_path"] = relative_path

    result = persist_runtime_extraction_raw_artifacts(output, project_dir=tmp_path)

    _assert_fail_closed(result)
    assert result.get("persisted") is not True
    _assert_no_forbidden_files(tmp_path)


@pytest.mark.parametrize("forbidden_payload_key", FORBIDDEN_ARTIFACTS)
def test_forbidden_payload_markers_are_rejected_without_persistence(
    tmp_path: Path,
    forbidden_payload_key: str,
) -> None:
    output = _runtime_output()
    output["artifact_payloads"]["tokens_001"] = {forbidden_payload_key: "blocked"}

    result = persist_runtime_extraction_raw_artifacts(output, project_dir=tmp_path)

    _assert_fail_closed(result, "fail_closed")
    assert result.get("persisted") is not True
    _assert_no_forbidden_files(tmp_path)


@pytest.mark.parametrize(
    ("missing_field", "expected_status"),
    (
        ("source_refs", "missing_source_refs"),
        ("evidence_refs", "missing_evidence_refs"),
        ("provenance_refs", "missing_provenance_refs"),
        ("source_locator_refs", "missing_source_locator_refs"),
    ),
)
def test_missing_runtime_output_refs_fail_closed_before_persistence(
    tmp_path: Path,
    missing_field: str,
    expected_status: str,
) -> None:
    output = _runtime_output()
    output[missing_field] = []

    result = persist_runtime_extraction_raw_artifacts(output, project_dir=tmp_path)

    _assert_fail_closed(result, expected_status)
    assert result.get("persisted") is not True
    _assert_no_forbidden_files(tmp_path)


def test_malformed_or_incomplete_tool_output_is_quarantined_not_success(
    tmp_path: Path,
) -> None:
    output = _runtime_output()
    output["artifact_files"] = [{"artifact_file_id": "tokens_001"}]

    result = persist_runtime_extraction_raw_artifacts(output, project_dir=tmp_path)

    _assert_fail_closed(result)
    assert result.get("status") in {"fail_closed", "quarantined", "malformed_output"}
    assert result.get("persisted") is not True
    _assert_no_forbidden_files(tmp_path)


@pytest.mark.parametrize("status", UNSUCCESSFUL_STATUSES)
def test_unavailable_and_fail_closed_states_never_report_success(status: str) -> None:
    env = {"WRITER_ASSISTANT_RUNTIME_EXTRACTION_FORCED_STATUS": status}

    result = validate_runtime_extraction_environment(env)

    _assert_fail_closed(result, status)
    assert result["runtime_extraction_enabled"] is False


def test_probe_success_quarantine_and_unavailable_are_not_extraction_success(
    tmp_path: Path,
) -> None:
    request = validate_runtime_extraction_request(_valid_request())
    plan = build_runtime_extraction_plan(request, _valid_environment())

    probe = run_runtime_extraction_probe(plan, project_dir=tmp_path)
    runtime = run_guarded_runtime_extraction(plan, project_dir=tmp_path)
    quarantine = quarantine_runtime_extraction_output(
        _runtime_output(),
        "malformed_output",
        project_dir=tmp_path,
    )

    assert probe["status"] == "valid"
    assert probe["probe_succeeded"] is True
    assert probe["runtime_extraction_succeeded"] is False
    _assert_no_runtime_side_effect_flags(probe)
    _assert_fail_closed(runtime, "unavailable")
    _assert_no_runtime_side_effect_flags(runtime)
    assert quarantine["status"] == "quarantined"
    _assert_fail_closed(quarantine)
    _assert_no_runtime_side_effect_flags(quarantine)
    _assert_no_forbidden_files(tmp_path)


def test_raw_artifact_persistence_failure_fails_closed_without_side_effects(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _raise(*args, **kwargs):
        raise OSError("write failed")

    monkeypatch.setattr(
        "backend.story_knowledge.runtime_extraction.write_raw_artifact_bundle",
        _raise,
    )

    result = persist_runtime_extraction_raw_artifacts(
        _runtime_output(),
        project_dir=tmp_path,
    )

    _assert_fail_closed(result, "fail_closed")
    assert result.get("persisted") is not True
    _assert_no_runtime_side_effect_flags(result)
    _assert_no_forbidden_files(tmp_path)
