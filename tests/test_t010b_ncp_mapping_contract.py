"""Focused T010B explicit NCP structural mapping contract tests."""

from __future__ import annotations

import builtins
import copy
from dataclasses import FrozenInstanceError, replace
import json
import os
from pathlib import Path
import socket
import subprocess

import pytest

from backend.story_knowledge.ncp_import_contract import (
    NCP_APP_MAPPING_VERSION,
    NCP_UNKNOWN_FIELD_POLICY,
    SUPPORTED_NCP_SCHEMA_VERSION,
    validate_ncp_import_artifact,
)
from backend.story_knowledge.ncp_mapping_contract import (
    NCP_MAPPING_CATEGORIES,
    NCP_MAPPING_CONTRACT_VERSION,
    NCP_MAPPING_DEFINITIONS,
    NCP_OMISSION_POLICY,
    NcpMappingValidationError,
    map_validated_ncp_import,
)


EXACT_PLAYER_SUMMARY = "Owner-authored player context remains exact and untransformed."


def _full_payload() -> dict[str, object]:
    return {
        "schema_version": "1.3.0",
        "future_extension": {"future_value": "preserve without interpretation"},
        "story": {
            "id": "story-t010b-001",
            "title": "Owner-selected structural source",
            "genre": "mystery",
            "logline": "Owner-authored source context is preserved, not rewritten.",
            "language": "en",
            "future_story_field": {"future": True},
            "metadata": {"locale": "en-US", "future_metadata": "preserved"},
            "ideation": {
                "character": ["An owner-authored character seed."],
                "theme": [
                    {
                        "id": "idea-theme-001",
                        "summary": "An owner-authored thematic seed.",
                        "future_idea_field": "preserved",
                    }
                ],
            },
            "settings": [
                {
                    "id": "setting-001",
                    "name": "Archive",
                    "description": "Owner-authored setting context.",
                }
            ],
            "moments": [
                {
                    "id": "moment-001",
                    "title": "Archive hearing",
                    "summary": "Owner-authored moment context.",
                    "setting_id": "setting-001",
                    "storybeats": ["storybeat-001"],
                    "storypoints": ["storypoint-001"],
                    "imperatives": [
                        "Preserve this exact owner-authored scene-purpose note."
                    ],
                }
            ],
            "authorial_intent": [
                {
                    "id": "intent-001",
                    "summary": "Owner-authored intent context remains source data.",
                }
            ],
            "narratives": [
                {
                    "id": "narrative-001",
                    "title": "Primary narrative",
                    "status": "complete",
                    "metadata": {"version": "owner-source-v1"},
                    "subtext": {
                        "perspectives": [
                            {
                                "id": "perspective-001",
                                "author_structural_pov": "i",
                                "summary": "Owner-authored perspective context.",
                            }
                        ],
                        "players": [
                            {
                                "id": "player-001",
                                "name": "Mara Vale",
                                "role": "main_character",
                                "summary": EXACT_PLAYER_SUMMARY,
                                "perspectives": ["perspective-001"],
                                "future_player_field": "preserved",
                            }
                        ],
                        "dynamics": [
                            {
                                "id": "dynamic-001",
                                "dynamic": "story_driver",
                                "vector": "action",
                                "summary": "Owner-authored dynamic context.",
                            }
                        ],
                        "storypoints": [
                            {
                                "id": "storypoint-001",
                                "appreciation": "Objective Story Concern",
                                "narrative_function": "Structural source context.",
                                "throughline": "Objective Story",
                            }
                        ],
                        "storybeats": [
                            {
                                "id": "storybeat-001",
                                "throughline": "Objective Story",
                                "sequence": 1,
                                "summary": "Owner-authored beat context.",
                            }
                        ],
                    },
                    "storytelling": {
                        "overviews": [
                            {
                                "id": "overview-001",
                                "title": "Narrative overview",
                                "summary": "Owner-authored overview context.",
                            }
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
            "id": "story-t010b-minimal",
            "narratives": [{"id": "narrative-minimal"}],
        },
    }


def _validated(payload: dict[str, object]):
    original = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
    return validate_ncp_import_artifact(
        original,
        project_id="project-t010b",
        source_reference="owner-selected/imports/t010b.ncp.json",
    )


def _mapped(payload: dict[str, object]):
    return map_validated_ncp_import(_validated(payload))


def _records(result, category: str):
    return [record for record in result.records if record.category == category]


def test_valid_t010a_result_maps_all_categories_deterministically() -> None:
    validated = _validated(_full_payload())

    first = map_validated_ncp_import(validated)
    second = map_validated_ncp_import(validated)

    assert first == second
    assert first.to_dict() == second.to_dict()
    assert first.contract_version == NCP_MAPPING_CONTRACT_VERSION
    assert first.ncp_schema_version == SUPPORTED_NCP_SCHEMA_VERSION == "1.3.0"
    assert first.app_mapping_version == NCP_APP_MAPPING_VERSION
    assert first.source_validation_id == validated.validation_id
    assert first.source_validation_hash == validated.validation_hash
    assert first.artifact_id == validated.artifact.artifact_id
    assert first.mapping_id == f"ncp-structural-mapping-{first.mapping_hash[:32]}"
    assert tuple(definition.category for definition in first.definitions) == (
        NCP_MAPPING_CATEGORIES
    )
    assert {record.category for record in first.records} == set(
        NCP_MAPPING_CATEGORIES
    )
    assert all(state.state == "mapped" for state in first.category_states)

    with pytest.raises(FrozenInstanceError):
        first.mapping_hash = "changed"  # type: ignore[misc]


def test_every_category_has_an_explicit_distinct_non_story_fact_mapping() -> None:
    assert tuple(definition.category for definition in NCP_MAPPING_DEFINITIONS) == (
        NCP_MAPPING_CATEGORIES
    )
    mapping_types = [definition.app_mapping_type for definition in NCP_MAPPING_DEFINITIONS]

    assert len(mapping_types) == len(set(mapping_types)) == 12
    assert all(mapping_type.startswith("ncp_") for mapping_type in mapping_types)
    assert all(mapping_type.endswith("_mapping") for mapping_type in mapping_types)
    assert all("story_fact" not in mapping_type for mapping_type in mapping_types)
    for definition in NCP_MAPPING_DEFINITIONS:
        serialized = definition.to_dict()
        assert serialized["schema_version"] == SUPPORTED_NCP_SCHEMA_VERSION
        assert serialized["app_mapping_version"] == NCP_APP_MAPPING_VERSION
        assert serialized["candidate_type"] is None
        assert serialized["omission_policy"] == NCP_OMISSION_POLICY


def test_exact_source_values_are_preserved_without_prose_transformation() -> None:
    result = _mapped(_full_payload())
    player = _records(result, "player")[0]
    moment = _records(result, "moment")[0]
    authorial_records = _records(result, "authorial_intent")

    assert player.source_value["summary"] == EXACT_PLAYER_SUMMARY
    assert moment.source_value["summary"] == "Owner-authored moment context."
    assert any(
        record.source_value
        == "Preserve this exact owner-authored scene-purpose note."
        for record in authorial_records
    )
    assert result.safety_boundary.generated_prose is False
    assert result.safety_boundary.prose_transformation is False
    assert result.safety_boundary.diagnostic_state_settled is False


def test_unknown_fields_remain_preserved_uninterpreted_and_t010c_is_deferred() -> None:
    validated = _validated(_full_payload())
    result = map_validated_ncp_import(validated)
    player = _records(result, "player")[0]
    story_metadata = next(
        record
        for record in _records(result, "metadata")
        if record.source_path == ("story",)
    )

    assert result.unknown_field_policy == NCP_UNKNOWN_FIELD_POLICY
    assert result.preserved_uninterpreted_top_level_pointers == (
        "/future_extension",
    )
    assert "future_player_field" in player.preserved_uninterpreted_field_names
    assert player.source_value["future_player_field"] == "preserved"
    assert "future_story_field" in (
        story_metadata.preserved_uninterpreted_field_names
    )
    assert validated.artifact.original_bytes == _validated(_full_payload()).artifact.original_bytes
    for record in result.to_dict()["records"]:
        assert record["json_pointer_provenance"] is None
        assert record["source_value_hash"] is None
        assert record["deletion_intent"] is False


def test_missing_and_empty_optional_categories_are_non_deleting_states() -> None:
    result = _mapped(_minimal_payload())
    states = {state.category: state for state in result.category_states}

    assert states["narrative"].state == "mapped"
    assert states["metadata"].state == "mapped"
    for category in set(NCP_MAPPING_CATEGORIES) - {"narrative", "metadata"}:
        assert states[category].state == "omitted"
        assert states[category].record_count == 0
        assert states[category].deletion_intent is False
        assert states[category].omission_policy == NCP_OMISSION_POLICY

    payload = _minimal_payload()
    payload["story"]["narratives"][0]["subtext"] = {"players": []}
    empty_result = _mapped(payload)
    empty_states = {state.category: state for state in empty_result.category_states}
    assert empty_states["player"].state == "present_empty"
    assert empty_states["player"].deletion_intent is False


def test_external_complete_remains_source_metadata_only() -> None:
    result = _mapped(_full_payload())

    assert tuple(
        item.to_dict() for item in result.external_narrative_statuses
    ) == (
        {
            "narrative_id": "narrative-001",
            "json_pointer": "/story/narratives/0/status",
            "external_status": "complete",
            "status_present": True,
            "local_approval": False,
        },
    )
    with pytest.raises(FrozenInstanceError):
        result.external_narrative_statuses[0].local_approval = True  # type: ignore[misc]
    assert _records(result, "narrative")[0].local_approval is False
    assert result.safety_boundary.approval_performed is False
    assert result.safety_boundary.promotion_performed is False
    assert result.safety_boundary.apply_promotion_performed is False
    assert result.safety_boundary.memory_write_performed is False
    assert result.safety_boundary.canon_write_performed is False


@pytest.mark.parametrize(
    "mutate, code",
    [
        (
            lambda value: value["story"].update({"ideation": []}),
            "malformed_category_shape",
        ),
        (
            lambda value: value["story"]["narratives"][0]["subtext"].update(
                {"players": {}}
            ),
            "malformed_category_shape",
        ),
        (
            lambda value: value["story"]["narratives"][0]["subtext"].update(
                {"players": ["not-an-object"]}
            ),
            "malformed_category_item",
        ),
        (
            lambda value: value["story"].update({"authorial_intent": [7]}),
            "malformed_category_item",
        ),
        (
            lambda value: value["story"]["narratives"][0].update(
                {"subtext": []}
            ),
            "malformed_category_shape",
        ),
    ],
)
def test_malformed_category_shapes_fail_closed(mutate, code: str) -> None:
    payload = _full_payload()
    mutate(payload)

    with pytest.raises(NcpMappingValidationError) as error:
        _mapped(payload)

    assert error.value.code == code


def test_duplicate_category_ids_fail_closed_as_ambiguous() -> None:
    payload = _full_payload()
    players = payload["story"]["narratives"][0]["subtext"]["players"]
    players.append(copy.deepcopy(players[0]))

    with pytest.raises(NcpMappingValidationError) as error:
        _mapped(payload)

    assert error.value.code == "ambiguous_category_id"


@pytest.mark.parametrize("raw_input", [b"{}", {}, None, "raw JSON"])
def test_mapping_rejects_raw_or_unvalidated_input(raw_input: object) -> None:
    with pytest.raises(NcpMappingValidationError) as error:
        map_validated_ncp_import(raw_input)  # type: ignore[arg-type]

    assert error.value.code == "validated_t010a_result_required"


def test_mapping_revalidates_exact_t010a_bytes_before_mapping() -> None:
    validated = _validated(_full_payload())
    tampered_artifact = replace(validated.artifact, original_bytes=b"{}")
    tampered_result = replace(validated, artifact=tampered_artifact)

    with pytest.raises(NcpMappingValidationError) as error:
        map_validated_ncp_import(tampered_result)

    assert error.value.code == "t010a_revalidation_failed"


def test_mapping_performs_no_io_runtime_network_subprocess_model_or_write(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    validated = _validated(_full_payload())
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

    result = map_validated_ncp_import(validated)

    assert calls == []
    safety = result.safety_boundary.to_dict()
    assert safety["in_memory_only"] is True
    assert safety["validated_t010a_input_required"] is True
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
