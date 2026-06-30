"""PHASE8-IMPL-019-T005 raw artifact persistence handoff contract tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from backend.story_knowledge.raw_artifacts import read_raw_artifact_file
from backend.story_knowledge.runtime_extraction import (
    persist_runtime_extraction_raw_artifacts,
)


PROJECT_ID = "example_project"
EXTRACTION_REQUEST_ID = "runtime_extract_001"
RAW_ARTIFACT_BUNDLE_ID = "raw_artifact_runtime_001"
SOURCE_REF = "source_ref_owner_scene_001"
EVIDENCE_REF = "evidence_ref_owner_scene_001_span_001"
PROVENANCE_REF = "provenance_ref_runtime_probe_001"
SOURCE_LOCATOR_REF = "source_locator_ref_owner_scene_001_offsets_001"

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


def _assert_no_forbidden_destinations(project_dir: Path) -> None:
    roots = [
        project_dir,
        project_dir / "projects" / PROJECT_ID,
        project_dir / "projects" / PROJECT_ID / "writer_assistant",
    ]
    for root in roots:
        for relative_path in FORBIDDEN_DESTINATIONS:
            assert not (root / relative_path).exists(), root / relative_path


def test_valid_guarded_handoff_persists_project_local_raw_artifact_bundle(
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
    assert result["source_refs"] == [SOURCE_REF]
    assert result["evidence_refs"] == [EVIDENCE_REF]
    assert result["provenance_refs"] == [PROVENANCE_REF]
    assert result["source_locator_refs"] == [SOURCE_LOCATOR_REF]
    assert result["candidate_persistence_performed"] is False
    assert result["review_queue_write_performed"] is False
    assert result["canon_write_performed"] is False
    assert result["apply_promotion_performed"] is False
    assert result["model_call_performed"] is False
    assert result["generated_prose"] is False
    assert result["training_artifact_created"] is False

    manifest = result["manifest"]
    assert manifest["artifact_source_type"] == "runtime_extraction"
    assert manifest["artifact_source_id"] == EXTRACTION_REQUEST_ID
    assert manifest["status"] == "valid"
    assert manifest["source_refs"] == [SOURCE_REF]
    assert manifest["evidence_refs"] == [EVIDENCE_REF]
    assert manifest["provenance_refs"] == [PROVENANCE_REF]
    assert manifest["source_locator_refs"] == [SOURCE_LOCATOR_REF]

    payload = read_raw_artifact_file(
        PROJECT_ID,
        RAW_ARTIFACT_BUNDLE_ID,
        "tokens_001",
        project_dir=tmp_path,
    )
    decoded = json.loads(payload.decode("utf-8"))
    assert decoded[0]["source_ref"] == SOURCE_REF
    assert "model_prompt" not in decoded[0]
    assert "model_completion" not in decoded[0]
    _assert_no_forbidden_destinations(tmp_path)


def test_unsafe_artifact_types_are_rejected_without_persistence(tmp_path: Path) -> None:
    output = _runtime_output()
    output["artifact_files"][0]["artifact_type"] = "model_prompt"

    result = persist_runtime_extraction_raw_artifacts(output, project_dir=tmp_path)

    assert result["status"] in {"fail_closed", "quarantined", "rejected", "malformed_output"}
    assert result["fail_closed"] is True
    assert result.get("persisted") is not True
    assert not (
        tmp_path
        / "projects"
        / PROJECT_ID
        / "writer_assistant"
        / "raw_artifacts"
        / RAW_ARTIFACT_BUNDLE_ID
    ).exists()
    _assert_no_forbidden_destinations(tmp_path)


@pytest.mark.parametrize(
    ("missing_field", "expected_status"),
    (
        ("source_refs", "missing_source_refs"),
        ("evidence_refs", "missing_evidence_refs"),
        ("provenance_refs", "missing_provenance_refs"),
        ("source_locator_refs", "missing_source_locator_refs"),
    ),
)
def test_missing_refs_fail_closed_before_raw_artifact_write(
    tmp_path: Path,
    missing_field: str,
    expected_status: str,
) -> None:
    output = _runtime_output()
    output[missing_field] = []

    result = persist_runtime_extraction_raw_artifacts(output, project_dir=tmp_path)

    assert result["status"] == expected_status
    assert result["fail_closed"] is True
    assert result.get("persisted") is not True
    _assert_no_forbidden_destinations(tmp_path)


def test_malformed_tool_output_is_quarantined_or_rejected(tmp_path: Path) -> None:
    output = _runtime_output()
    output["artifact_payloads"] = {"unexpected_file": {"value": "support_data"}}

    result = persist_runtime_extraction_raw_artifacts(output, project_dir=tmp_path)

    assert result["status"] in {"fail_closed", "quarantined", "malformed_output", "rejected"}
    assert result.get("extraction_succeeded") is not True
    assert result.get("persisted") is not True
    _assert_no_forbidden_destinations(tmp_path)


def test_forbidden_payload_values_are_rejected_without_support_data_write(
    tmp_path: Path,
) -> None:
    output = _runtime_output()
    output["artifact_payloads"]["tokens_001"] = {"model_prompt": "forbidden"}

    result = persist_runtime_extraction_raw_artifacts(output, project_dir=tmp_path)

    assert result["status"] == "fail_closed"
    assert result["fail_closed"] is True
    assert result.get("persisted") is not True
    _assert_no_forbidden_destinations(tmp_path)


def test_raw_artifact_persistence_failure_fails_closed(
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

    assert result["status"] == "fail_closed"
    assert result["fail_closed"] is True
    assert result.get("persisted") is not True
    assert result["canon_write_performed"] is False
    assert result["apply_promotion_performed"] is False
    assert result["candidate_persistence_performed"] is False
    assert result["review_queue_write_performed"] is False
    _assert_no_forbidden_destinations(tmp_path)
