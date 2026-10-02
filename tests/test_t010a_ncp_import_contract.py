"""Focused T010A immutable NCP import and validation-before-import tests."""

from __future__ import annotations

import builtins
import copy
from dataclasses import FrozenInstanceError
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess

import pytest

from backend.story_knowledge.analysis_run_manifest import ArtifactReference
from backend.story_knowledge.ncp_import_contract import (
    NCP_APP_MAPPING_VERSION,
    NCP_IMPORT_CONTRACT_VERSION,
    NCP_UNKNOWN_FIELD_POLICY,
    SUPPORTED_NCP_SCHEMA_VERSION,
    NcpImportValidationError,
    compute_ncp_import_validation_hash,
    validate_ncp_import_artifact,
    validate_ncp_import_validation_record,
)
from backend.story_knowledge.raw_artifacts import build_raw_artifact_file_ref
from backend.story_knowledge.source_map import SourceIdentity


def _valid_payload(*, status: object = "complete") -> dict[str, object]:
    narrative: dict[str, object] = {
        "id": "narrative-t010a-001",
        "title": "Imported narrative metadata",
        "subtext": {"players": [], "storypoints": []},
    }
    if status is not _OMITTED:
        narrative["status"] = status
    return {
        "schema_version": "1.3.0",
        "story": {
            "id": "story-t010a-001",
            "title": "Owner-selected source title",
            "logline": "Owner-selected source text that must not be transformed.",
            "narratives": [narrative],
        },
        "future_extension": {
            "future_value": "preserved only in exact original bytes"
        },
    }


_OMITTED = object()


def _exact_bytes(payload: dict[str, object]) -> bytes:
    return json.dumps(
        payload, ensure_ascii=False, indent=2, sort_keys=False
    ).encode("utf-8")


def _validate(payload: dict[str, object], **overrides: object):
    values: dict[str, object] = {
        "project_id": "project-t010a",
        "source_reference": "owner-selected/imports/story.ncp.json",
    }
    values.update(overrides)
    return validate_ncp_import_artifact(_exact_bytes(payload), **values)


def test_valid_import_returns_deterministic_immutable_provenance_metadata() -> None:
    original_bytes = _exact_bytes(_valid_payload())
    kwargs = {
        "project_id": "project-t010a",
        "source_reference": "owner-selected/imports/story.ncp.json",
    }

    first = validate_ncp_import_artifact(original_bytes, **kwargs)
    second = validate_ncp_import_artifact(original_bytes, **kwargs)

    assert first == second
    assert first.contract_version == NCP_IMPORT_CONTRACT_VERSION
    assert first.ncp_schema_version == SUPPORTED_NCP_SCHEMA_VERSION == "1.3.0"
    assert first.app_mapping_version == NCP_APP_MAPPING_VERSION
    assert first.validation_outcome == "valid"
    assert first.validation_hash == compute_ncp_import_validation_hash(first.to_dict())
    assert first.validation_id == f"ncp-import-validation-{first.validation_hash[:32]}"

    expected_hash = hashlib.sha256(original_bytes).hexdigest()
    artifact = first.artifact
    assert artifact.artifact_id == f"ncp-import-{expected_hash}"
    assert artifact.original_bytes == original_bytes
    assert artifact.original_text.encode("utf-8") == original_bytes
    assert artifact.sha256 == expected_hash
    assert artifact.size_bytes == len(original_bytes)
    assert artifact.media_type == "application/json"
    assert artifact.source_reference == kwargs["source_reference"]
    assert artifact.support_data_only is True
    assert artifact.candidate_truth is False
    assert isinstance(artifact.source_identity, SourceIdentity)
    assert artifact.source_identity.source_document_type == "imported_context"
    assert artifact.source_identity.source_ownership.value == "owner_selected_imported"
    assert artifact.source_identity.content_hash == expected_hash
    assert isinstance(artifact.artifact_reference, ArtifactReference)
    assert artifact.artifact_reference.content_hash == expected_hash
    assert artifact.artifact_reference.source_snapshot_ids == (
        artifact.source_identity.snapshot_id,
    )

    record = validate_ncp_import_validation_record(first.to_dict())
    assert record == first.to_dict()
    assert "original_bytes" not in record["artifact"]
    assert record["artifact"]["original_bytes_preserved"] is True

    with pytest.raises(FrozenInstanceError):
        first.validation_outcome = "changed"  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        artifact.sha256 = "0" * 64  # type: ignore[misc]


def test_t002_source_identity_and_t003_file_reference_compatibility() -> None:
    result = _validate(_valid_payload(status="draft"))
    artifact = result.artifact

    file_ref = build_raw_artifact_file_ref(
        artifact_file_id=f"original-{artifact.sha256[:24]}",
        artifact_type=artifact.artifact_type,
        relative_path="original/ncp-import.json",
        media_type=artifact.media_type,
        payload=artifact.original_bytes,
        source_locator_refs=[artifact.source_identity.snapshot_id],
        evidence_refs=[],
        provenance_refs=[result.validation_id],
        schema_name="narrative-context-protocol",
        schema_version=result.ncp_schema_version,
        parser_hint=result.app_mapping_version,
        model_calls_occurred=False,
    )

    assert file_ref["artifact_type"] == "source_snapshot"
    assert file_ref["sha256"] == artifact.sha256
    assert file_ref["size_bytes"] == artifact.size_bytes
    assert file_ref["media_type"] == artifact.media_type
    assert file_ref["schema_version"] == SUPPORTED_NCP_SCHEMA_VERSION
    assert "raw_artifacts_support_data_only" in file_ref["boundary_flags"]
    assert "raw_artifacts_not_candidates" in file_ref["boundary_flags"]
    assert "raw_artifacts_not_canon" in file_ref["boundary_flags"]
    assert "no_model_calls" in file_ref["boundary_flags"]


def test_external_complete_is_metadata_only_and_never_local_approval() -> None:
    result = _validate(_valid_payload(status="complete"))

    assert result.external_narrative_statuses[0].to_dict() == {
        "narrative_id": "narrative-t010a-001",
        "json_pointer": "/story/narratives/0/status",
        "external_status": "complete",
        "status_present": True,
        "local_approval": False,
    }
    safety = result.safety_boundary.to_dict()
    assert safety["approval_performed"] is False
    assert safety["promotion_performed"] is False
    assert safety["apply_promotion_performed"] is False
    assert safety["memory_write_performed"] is False
    assert safety["canon_write_performed"] is False
    assert safety["candidate_truth"] is False


def test_omitted_external_status_remains_explicitly_omitted_metadata() -> None:
    result = _validate(_valid_payload(status=_OMITTED))
    metadata = result.external_narrative_statuses[0]

    assert metadata.status_present is False
    assert metadata.external_status is None
    assert metadata.local_approval is False


def test_unknown_future_top_level_fields_are_reported_and_preserved_exactly() -> None:
    payload = _valid_payload(status="candidate")
    payload["z_future"] = {"meaning": "not interpreted"}
    payload["a_future"] = [1, 2, 3]
    original_bytes = _exact_bytes(payload)

    result = validate_ncp_import_artifact(
        original_bytes,
        project_id="project-t010a",
        source_reference="source://selected-ncp",
    )

    assert result.unknown_field_policy == NCP_UNKNOWN_FIELD_POLICY
    assert result.preserved_uninterpreted_top_level_pointers == (
        "/a_future",
        "/future_extension",
        "/z_future",
    )
    assert result.artifact.original_bytes == original_bytes
    assert result.safety_boundary.project_state_write_performed is False
    assert result.safety_boundary.candidate_write_performed is False


@pytest.mark.parametrize(
    "mutate, expected_pointer",
    [
        (lambda value: value.pop("schema_version"), "/schema_version"),
        (lambda value: value.pop("story"), "/story"),
        (lambda value: value["story"].pop("id"), "/story/id"),
        (lambda value: value["story"].pop("narratives"), "/story/narratives"),
        (
            lambda value: value["story"]["narratives"][0].pop("id"),
            "/story/narratives/0/id",
        ),
    ],
)
def test_missing_required_fields_fail_closed(mutate, expected_pointer: str) -> None:
    payload = _valid_payload()
    mutate(payload)

    with pytest.raises(NcpImportValidationError) as error:
        _validate(payload)

    assert error.value.code == "missing_required_field"
    assert error.value.json_pointer == expected_pointer


@pytest.mark.parametrize("schema_version", ["1.2.0", "1.4.0", "2.0.0", None])
def test_unsupported_schema_versions_fail_closed(schema_version: object) -> None:
    payload = _valid_payload()
    payload["schema_version"] = schema_version

    with pytest.raises(NcpImportValidationError) as error:
        _validate(payload)

    assert error.value.code == "unsupported_schema_version"
    assert error.value.json_pointer == "/schema_version"


@pytest.mark.parametrize(
    "artifact, code",
    [
        (b"[]", "invalid_top_level"),
        (b'{"schema_version":"1.3.0",', "malformed_json"),
        (
            b'{"schema_version":"1.3.0","schema_version":"1.3.0","story":{}}',
            "ambiguous_duplicate_key",
        ),
        (
            b'{"schema_version":"1.3.0","story":{"id":"s","narratives":[]},"n":NaN}',
            "malformed_json",
        ),
        (b"\xff", "invalid_utf8"),
    ],
)
def test_malformed_or_ambiguous_input_fails_closed(artifact: bytes, code: str) -> None:
    with pytest.raises(NcpImportValidationError) as error:
        validate_ncp_import_artifact(
            artifact,
            project_id="project-t010a",
            source_reference="selected.json",
        )

    assert error.value.code == code


@pytest.mark.parametrize(
    "field", ["approved", "approved_memory", "canon", "promotion", "apply_promotion"]
)
def test_unsafe_top_level_local_authority_fields_fail_closed(field: str) -> None:
    payload = _valid_payload()
    payload[field] = True

    with pytest.raises(NcpImportValidationError) as error:
        _validate(payload)

    assert error.value.code == "unsafe_local_authority_field"
    assert error.value.json_pointer == f"/{field}"


def test_invalid_narrative_shape_status_and_duplicate_ids_fail_closed() -> None:
    payload = _valid_payload(status="approved")
    with pytest.raises(NcpImportValidationError, match="unsupported_external_status"):
        _validate(payload)

    payload = _valid_payload(status="candidate")
    payload["story"]["narratives"].append(
        {"id": "narrative-t010a-001", "status": "draft"}
    )
    with pytest.raises(NcpImportValidationError, match="ambiguous_narrative_id"):
        _validate(payload)

    payload = _valid_payload(status="candidate")
    payload["story"]["narratives"] = []
    with pytest.raises(NcpImportValidationError, match="invalid_required_field"):
        _validate(payload)


def test_validation_metadata_is_tamper_evident() -> None:
    record = _validate(_valid_payload()).to_dict()
    tampered = copy.deepcopy(record)
    tampered["artifact"]["sha256"] = "0" * 64

    with pytest.raises(NcpImportValidationError) as error:
        validate_ncp_import_validation_record(tampered)

    assert error.value.code == "invalid_artifact_metadata"

    weakened = copy.deepcopy(record)
    weakened["safety_boundary"]["approval_performed"] = True
    weakened_hash = compute_ncp_import_validation_hash(weakened)
    weakened["validation_hash"] = weakened_hash
    weakened["validation_id"] = f"ncp-import-validation-{weakened_hash[:32]}"
    with pytest.raises(NcpImportValidationError) as error:
        validate_ncp_import_validation_record(weakened)
    assert error.value.code == "weakened_safety_boundary"


def test_validation_does_not_echo_or_transform_story_text() -> None:
    source_phrase = "Owner-selected source text that must not be transformed."
    result = _validate(_valid_payload())
    serialized_metadata = json.dumps(result.to_dict(), sort_keys=True)

    assert source_phrase not in serialized_metadata
    assert result.artifact.original_text.count(source_phrase) == 1
    assert result.safety_boundary.generated_prose is False
    assert result.safety_boundary.prose_transformation is False
    assert result.safety_boundary.diagnostic_state_settled is False


def test_validation_invokes_no_io_runtime_network_subprocess_or_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []

    def forbidden(name: str):
        def _fail(*args, **kwargs):
            calls.append(name)
            raise AssertionError(f"forbidden side effect: {name}")

        return _fail

    monkeypatch.setattr(builtins, "open", forbidden("open"))
    monkeypatch.setattr(Path, "write_text", forbidden("Path.write_text"))
    monkeypatch.setattr(Path, "write_bytes", forbidden("Path.write_bytes"))
    monkeypatch.setattr(Path, "mkdir", forbidden("Path.mkdir"))
    monkeypatch.setattr(subprocess, "run", forbidden("subprocess.run"))
    monkeypatch.setattr(subprocess, "Popen", forbidden("subprocess.Popen"))
    monkeypatch.setattr(subprocess, "check_call", forbidden("subprocess.check_call"))
    monkeypatch.setattr(subprocess, "check_output", forbidden("subprocess.check_output"))
    monkeypatch.setattr(socket, "create_connection", forbidden("socket.create_connection"))
    monkeypatch.setattr(os, "system", forbidden("os.system"))

    result = _validate(_valid_payload(status="complete"))

    assert result.validation_outcome == "valid"
    assert calls == []
    safety = result.safety_boundary.to_dict()
    for field in (
        "project_state_write_performed",
        "candidate_write_performed",
        "review_write_performed",
        "promotion_performed",
        "apply_promotion_performed",
        "memory_write_performed",
        "canon_write_performed",
        "live_ncp_execution",
        "node_execution",
        "npm_execution",
        "subprocess_execution",
        "network_execution",
        "model_execution",
        "generated_prose",
        "prose_transformation",
    ):
        assert safety[field] is False
