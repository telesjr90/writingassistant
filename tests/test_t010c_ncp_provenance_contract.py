"""Focused T010C JSON-pointer and source-value provenance contract tests."""

from __future__ import annotations

import builtins
import copy
from dataclasses import FrozenInstanceError, replace
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess

import pytest

from backend.story_knowledge.ncp_import_contract import (
    NCP_APP_MAPPING_VERSION,
    SUPPORTED_NCP_SCHEMA_VERSION,
    validate_ncp_import_artifact,
)
from backend.story_knowledge.ncp_mapping_contract import (
    NCP_MAPPING_CATEGORIES,
    map_validated_ncp_import,
)
from backend.story_knowledge.ncp_provenance_contract import (
    NCP_EXTERNAL_STATUS_POLICY,
    NCP_PROVENANCE_CONTRACT_VERSION,
    NCP_SOURCE_VALUE_CANONICALIZATION,
    NcpProvenanceValidationError,
    build_ncp_source_provenance,
    canonical_source_value_json_bytes,
    compute_ncp_provenance_hash,
    source_value_sha256,
)


EXACT_SOURCE_TEXT = "Exact owner-authored source text; never transformed."


def _full_payload() -> dict[str, object]:
    return {
        "schema_version": "1.3.0",
        "future~/top": {"preserve": True},
        "story": {
            "id": "story-t010c",
            "title": "Source title",
            "metadata": {"locale": "en-US"},
            "ideation": {
                "theme~/branch": [
                    {"id": "idea-001", "summary": "Source theme"}
                ]
            },
            "settings": [
                {"id": "setting-001", "description": "Source setting"}
            ],
            "moments": [
                {
                    "id": "moment-001",
                    "summary": "Source moment",
                    "imperatives": ["Exact source intent"],
                }
            ],
            "authorial_intent": [
                {"id": "intent-001", "summary": "Source intent"}
            ],
            "narratives": [
                {
                    "id": "narrative-001",
                    "title": "Source narrative",
                    "status": "complete",
                    "metadata": {"version": "source-v1"},
                    "subtext": {
                        "perspectives": [
                            {"id": "perspective-001", "summary": "Source perspective"}
                        ],
                        "players": [
                            {
                                "id": "player~/001",
                                "name": "Source player",
                                "summary": EXACT_SOURCE_TEXT,
                                "future~/field": {"preserve": "exactly"},
                            }
                        ],
                        "dynamics": [
                            {"id": "dynamic-001", "dynamic": "story_driver"}
                        ],
                        "storypoints": [
                            {"id": "storypoint-001", "throughline": "Objective Story"}
                        ],
                        "storybeats": [
                            {"id": "storybeat-001", "sequence": 1}
                        ],
                    },
                    "storytelling": {
                        "overviews": [
                            {"id": "overview-001", "summary": "Source overview"}
                        ]
                    },
                }
            ],
        },
    }


def _minimal_payload() -> dict[str, object]:
    return {
        "schema_version": "1.3.0",
        "story": {
            "id": "story-t010c-minimal",
            "narratives": [
                {
                    "id": "narrative-minimal",
                    "subtext": {"players": []},
                }
            ],
        },
    }


def _validated(payload: dict[str, object]):
    return validate_ncp_import_artifact(
        json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8"),
        project_id="project-t010c",
        source_reference="owner-selected/imports/t010c.ncp.json",
    )


def _provenance(payload: dict[str, object]):
    validated = _validated(payload)
    mapping = map_validated_ncp_import(validated)
    return build_ncp_source_provenance(validated, mapping)


def _record(result, pointer: str, kind: str = "mapped_record"):
    return next(
        record
        for record in result.records
        if record.json_pointer == pointer and record.provenance_kind == kind
    )


def test_valid_t010b_mapping_produces_deterministic_category_provenance() -> None:
    validated = _validated(_full_payload())
    mapping = map_validated_ncp_import(validated)

    first = build_ncp_source_provenance(validated, mapping)
    second = build_ncp_source_provenance(validated, mapping)

    assert first == second
    assert first.to_dict() == second.to_dict()
    assert first.contract_version == NCP_PROVENANCE_CONTRACT_VERSION
    assert first.ncp_schema_version == SUPPORTED_NCP_SCHEMA_VERSION == "1.3.0"
    assert first.app_mapping_version == NCP_APP_MAPPING_VERSION
    assert first.source_validation_id == validated.validation_id
    assert first.source_mapping_id == mapping.mapping_id
    assert first.source_artifact_id == validated.artifact.artifact_id
    assert first.provenance_id == f"ncp-provenance-{first.provenance_hash[:32]}"
    assert compute_ncp_provenance_hash(first.to_dict()) == first.provenance_hash

    mapped_categories = {
        record.category
        for record in first.records
        if record.provenance_kind == "mapped_record"
    }
    assert mapped_categories == set(NCP_MAPPING_CATEGORIES)
    assert all(record.category != "story_fact" for record in first.records)
    with pytest.raises(FrozenInstanceError):
        first.provenance_hash = "changed"  # type: ignore[misc]


def test_json_pointers_escape_keys_and_hash_exact_id_values() -> None:
    result = _provenance(_full_payload())

    ideation = _record(result, "/story/ideation/theme~0~1branch/0")
    unknown = _record(
        result,
        "/story/narratives/0/subtext/players/0/future~0~1field",
        "preserved_uninterpreted_field",
    )
    unknown_top = _record(
        result,
        "/future~0~1top",
        "preserved_uninterpreted_top_level",
    )
    player_id = _record(
        result,
        "/story/narratives/0/subtext/players/0/id",
        "mapped_field",
    )

    assert ideation.category == "ideation"
    assert unknown.interpreted_by_mapping is False
    assert unknown_top.interpreted_by_mapping is False
    assert player_id.source_value_sha256 == source_value_sha256("player~/001")
    assert player_id.json_pointer.endswith("/id")


def test_source_value_hash_uses_canonical_json_and_changes_with_value() -> None:
    value = {"z": [2, 1], "a": {"text": "exact"}}
    expected_bytes = b'{"a":{"text":"exact"},"z":[2,1]}'

    assert canonical_source_value_json_bytes(value) == expected_bytes
    assert source_value_sha256(value) == hashlib.sha256(expected_bytes).hexdigest()
    assert source_value_sha256(value) != source_value_sha256(
        {"z": [2, 1], "a": {"text": "changed"}}
    )


def test_unrelated_object_key_reordering_does_not_change_source_value_hash() -> None:
    payload = _full_payload()
    reordered = {
        "story": payload["story"],
        "future~/top": payload["future~/top"],
        "schema_version": payload["schema_version"],
    }

    first = _provenance(payload)
    second = _provenance(reordered)
    pointer = "/story/narratives/0/subtext/players/0/summary"

    assert _record(first, pointer, "mapped_field").source_value_sha256 == (
        _record(second, pointer, "mapped_field").source_value_sha256
    )
    assert first.source_artifact_id != second.source_artifact_id


def test_changing_source_value_changes_only_its_value_hash_contract() -> None:
    original = _full_payload()
    changed = copy.deepcopy(original)
    changed["story"]["narratives"][0]["subtext"]["players"][0]["summary"] = (
        "Changed source value"
    )
    pointer = "/story/narratives/0/subtext/players/0/summary"

    original_record = _record(_provenance(original), pointer, "mapped_field")
    changed_record = _record(_provenance(changed), pointer, "mapped_field")

    assert original_record.source_value_sha256 != changed_record.source_value_sha256


def test_external_complete_is_hashed_source_metadata_without_authority() -> None:
    result = _provenance(_full_payload())
    status = result.external_statuses[0]

    assert status.json_pointer == "/story/narratives/0/status"
    assert status.external_status == "complete"
    assert status.source_value_sha256 == source_value_sha256("complete")
    assert result.external_status_policy == NCP_EXTERNAL_STATUS_POLICY
    assert status.source_metadata_only is True
    assert status.candidate_truth is False
    assert status.local_approval is False
    assert status.canon_authority is False
    assert status.promotion_authority is False
    assert status.apply_promotion_authority is False
    with pytest.raises(FrozenInstanceError):
        status.local_approval = True  # type: ignore[misc]


def test_unknown_fields_remain_uninterpreted_and_are_never_flattened() -> None:
    result = _provenance(_full_payload())
    uninterpreted = [
        record
        for record in result.records
        if record.provenance_kind.startswith("preserved_uninterpreted")
    ]

    assert {record.json_pointer for record in uninterpreted} >= {
        "/future~0~1top",
        "/story/narratives/0/subtext/players/0/future~0~1field",
    }
    assert all(record.interpreted_by_mapping is False for record in uninterpreted)
    assert all(record.source_metadata_only is True for record in uninterpreted)
    assert all(record.candidate_truth is False for record in uninterpreted)
    assert all(record.category != "story_fact" for record in uninterpreted)


def test_missing_and_empty_categories_remain_non_deleting_states() -> None:
    result = _provenance(_minimal_payload())
    states = {state.category: state for state in result.category_states}

    assert states["player"].state == "present_empty"
    assert states["player"].deletion_intent is False
    for category in set(NCP_MAPPING_CATEGORIES) - {"metadata", "narrative", "player"}:
        assert states[category].state == "omitted"
        assert states[category].record_count == 0
        assert states[category].deletion_intent is False
    status = result.external_statuses[0]
    assert status.status_present is False
    assert status.source_value_sha256 is None
    assert status.deletion_intent is False


@pytest.mark.parametrize(
    "validated,mapping,code",
    [
        (b"raw", object(), "validated_t010a_result_required"),
        (None, object(), "validated_t010a_result_required"),
    ],
)
def test_provenance_rejects_unvalidated_raw_input(validated, mapping, code: str) -> None:
    with pytest.raises(NcpProvenanceValidationError) as error:
        build_ncp_source_provenance(validated, mapping)  # type: ignore[arg-type]

    assert error.value.code == code


def test_provenance_rejects_missing_or_mismatched_t010b_mapping() -> None:
    validated = _validated(_full_payload())
    mapping = map_validated_ncp_import(validated)

    with pytest.raises(NcpProvenanceValidationError) as missing:
        build_ncp_source_provenance(validated, {})  # type: ignore[arg-type]
    assert missing.value.code == "verified_t010b_mapping_required"

    with pytest.raises(NcpProvenanceValidationError) as mismatch:
        build_ncp_source_provenance(
            validated, replace(mapping, mapping_hash="0" * 64)
        )
    assert mismatch.value.code == "t010b_mapping_mismatch"


def test_provenance_emits_hashes_not_generated_or_transformed_prose() -> None:
    result = _provenance(_full_payload())
    serialized = json.dumps(result.to_dict(), ensure_ascii=False)

    assert EXACT_SOURCE_TEXT not in serialized
    assert result.safety_boundary.generated_prose is False
    assert result.safety_boundary.prose_transformation is False
    assert result.safety_boundary.diagnostic_state_settled is False
    assert all(record.source_metadata_only is True for record in result.records)


def test_provenance_performs_no_io_runtime_network_subprocess_model_or_write(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    validated = _validated(_full_payload())
    mapping = map_validated_ncp_import(validated)
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

    result = build_ncp_source_provenance(validated, mapping)

    assert calls == []
    safety = result.safety_boundary.to_dict()
    assert safety["in_memory_only"] is True
    assert safety["validated_t010a_input_required"] is True
    assert safety["verified_t010b_mapping_required"] is True
    for field in (
        "candidate_construction_performed",
        "candidate_write_performed",
        "review_write_performed",
        "project_state_write_performed",
        "approval_performed",
        "promotion_performed",
        "apply_promotion_performed",
        "memory_write_performed",
        "canon_write_performed",
        "generated_prose",
        "prose_transformation",
        "live_ncp_execution",
        "node_execution",
        "npm_execution",
        "subprocess_execution",
        "network_execution",
        "model_execution",
        "diagnostic_state_settled",
    ):
        assert safety[field] is False


def test_canonicalization_contract_is_explicit() -> None:
    result = _provenance(_full_payload())
    serialized_record = result.records[0].to_dict()

    assert serialized_record["canonicalization"] == NCP_SOURCE_VALUE_CANONICALIZATION
    assert serialized_record["hash_algorithm"] == "sha256"
    assert serialized_record["deletion_intent"] is False
