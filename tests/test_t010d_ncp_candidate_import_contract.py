"""Focused T010D candidate-only NCP import planning contract tests."""

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

from backend.story_knowledge.ncp_candidate_import_contract import (
    NCP_CANDIDATE_IMPORT_CONTRACT_VERSION,
    NCP_CANDIDATE_REVIEW_STATUS,
    NCP_OMITTED_FIELD_IMPORT_POLICY,
    NcpCandidateImportSafetyBoundary,
    NcpCandidateImportValidationError,
    NcpExistingContextRecord,
    build_ncp_candidate_import_plan,
    compute_ncp_candidate_import_plan_hash,
    validate_ncp_candidate_import_plan_record,
)
from backend.story_knowledge.ncp_import_contract import validate_ncp_import_artifact
from backend.story_knowledge.ncp_mapping_contract import (
    NCP_MAPPING_CATEGORIES,
    map_validated_ncp_import,
)
from backend.story_knowledge.ncp_provenance_contract import (
    build_ncp_source_provenance,
)


EXACT_SOURCE_PROSE = "Exact owner-authored source prose remains only upstream."


def _full_payload() -> dict[str, object]:
    return {
        "schema_version": "1.3.0",
        "future_top_level": {"preserve": "uninterpreted"},
        "story": {
            "id": "story-t010d",
            "title": "Source title",
            "metadata": {"locale": "en-US"},
            "ideation": {"theme": [{"id": "idea-001", "summary": "Source theme"}]},
            "settings": [{"id": "setting-001", "description": "Source setting"}],
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
                                "id": "player-001",
                                "name": "Source player",
                                "summary": EXACT_SOURCE_PROSE,
                                "future_player_field": {"preserve": True},
                            }
                        ],
                        "dynamics": [
                            {"id": "dynamic-001", "dynamic": "story_driver"}
                        ],
                        "storypoints": [
                            {"id": "storypoint-001", "throughline": "Objective Story"}
                        ],
                        "storybeats": [{"id": "storybeat-001", "sequence": 1}],
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
            "id": "story-t010d-minimal",
            "narratives": [
                {
                    "id": "narrative-minimal",
                    "subtext": {"players": []},
                }
            ],
        },
    }


def _chain(payload: dict[str, object]):
    validated = validate_ncp_import_artifact(
        json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8"),
        project_id="project-t010d",
        source_reference="owner-selected/imports/t010d.ncp.json",
    )
    mapping = map_validated_ncp_import(validated)
    provenance = build_ncp_source_provenance(validated, mapping)
    return validated, mapping, provenance


def _plan(
    payload: dict[str, object],
    existing: tuple[NcpExistingContextRecord, ...] = (),
):
    validated, mapping, provenance = _chain(payload)
    return build_ncp_candidate_import_plan(
        validated,
        mapping,
        provenance,
        existing_context_records=existing,
    )


def _candidate(result, category: str, match_key: str | None = None):
    return next(
        candidate
        for candidate in result.candidates
        if candidate.category == category
        and (match_key is None or candidate.match_key == match_key)
    )


def test_valid_t010_chain_produces_deterministic_candidate_only_plan() -> None:
    validated, mapping, provenance = _chain(_full_payload())

    first = build_ncp_candidate_import_plan(validated, mapping, provenance)
    second = build_ncp_candidate_import_plan(validated, mapping, provenance)

    assert first == second
    assert first.to_dict() == second.to_dict()
    assert first.contract_version == NCP_CANDIDATE_IMPORT_CONTRACT_VERSION
    assert first.source_validation_id == validated.validation_id
    assert first.source_mapping_id == mapping.mapping_id
    assert first.source_provenance_id == provenance.provenance_id
    assert first.source_artifact_id == validated.artifact.artifact_id
    assert first.plan_id == f"ncp-candidate-import-plan-{first.plan_hash[:32]}"
    assert compute_ncp_candidate_import_plan_hash(first.to_dict()) == first.plan_hash
    assert validate_ncp_candidate_import_plan_record(first.to_dict()) == first.to_dict()
    with pytest.raises(FrozenInstanceError):
        first.plan_hash = "changed"  # type: ignore[misc]


@pytest.mark.parametrize(
    "chain_index,raw,code",
    [
        (0, b"raw", "validated_t010a_result_required"),
        (1, {}, "verified_t010b_mapping_required"),
        (2, None, "verified_t010c_provenance_required"),
    ],
)
def test_candidate_import_rejects_raw_or_unvalidated_inputs(
    chain_index: int, raw: object, code: str
) -> None:
    chain = list(_chain(_full_payload()))
    chain[chain_index] = raw

    with pytest.raises(NcpCandidateImportValidationError) as error:
        build_ncp_candidate_import_plan(*chain)  # type: ignore[arg-type]

    assert error.value.code == code


def test_candidate_import_rejects_mismatched_provenance() -> None:
    validated, mapping, provenance = _chain(_full_payload())
    tampered = replace(provenance, provenance_hash="0" * 64)

    with pytest.raises(NcpCandidateImportValidationError) as error:
        build_ncp_candidate_import_plan(validated, mapping, tampered)

    assert error.value.code == "t010c_provenance_mismatch"


def test_candidates_are_category_specific_pending_and_never_truth() -> None:
    result = _plan(_full_payload())

    assert {candidate.category for candidate in result.candidates} == set(
        NCP_MAPPING_CATEGORIES
    )
    assert all(
        candidate.candidate_type == f"ncp_{candidate.category}_import_candidate"
        for candidate in result.candidates
    )
    assert all("story_fact" not in candidate.candidate_type for candidate in result.candidates)
    for candidate in result.candidates:
        assert candidate.review_status == NCP_CANDIDATE_REVIEW_STATUS
        assert candidate.candidate_only is True
        assert candidate.local_approval is False
        assert candidate.canon_authority is False
        assert candidate.memory_authority is False
        assert candidate.promotion_authority is False
        assert candidate.apply_promotion_authority is False
        assert candidate.persisted is False
        assert candidate.deletion_intent is False


def test_candidates_reference_exact_t010c_provenance_records() -> None:
    validated, mapping, provenance = _chain(_full_payload())
    result = build_ncp_candidate_import_plan(validated, mapping, provenance)
    provenance_by_id = {record.provenance_id: record for record in provenance.records}

    for candidate in result.candidates:
        source = provenance_by_id[candidate.source_provenance_id]
        assert source.provenance_kind == "mapped_record"
        assert source.mapping_record_id == candidate.source_mapping_record_id
        assert source.category == candidate.category
        assert source.json_pointer == candidate.source_json_pointer
        assert source.source_value_sha256 == candidate.source_value_sha256
        for provenance_id in candidate.field_provenance_ids:
            assert provenance_by_id[provenance_id].provenance_kind == "mapped_field"


def test_external_complete_remains_source_metadata_without_local_authority() -> None:
    result = _plan(_full_payload())
    status = result.external_statuses[0]

    assert status.external_status == "complete"
    assert status.source_metadata_only is True
    assert status.candidate_truth is False
    assert status.local_approval is False
    assert status.canon_authority is False
    assert status.promotion_authority is False
    assert status.apply_promotion_authority is False
    assert result.owner_review_handoff.review_status == "pending_owner_review"


def test_conflicts_are_pending_metadata_and_do_not_overwrite_existing_context() -> None:
    baseline = _plan(_full_payload())
    player = _candidate(baseline, "player", "id:player-001")
    setting = _candidate(baseline, "setting", "id:setting-001")
    existing = (
        NcpExistingContextRecord(
            context_record_id="approved-player-001",
            category="player",
            match_key=player.match_key,
            source_value_sha256="f" * 64,
            authority_scope="approved_context",
        ),
        NcpExistingContextRecord(
            context_record_id="truth-setting-001",
            category="setting",
            match_key=setting.match_key,
            source_value_sha256=setting.source_value_sha256,
            authority_scope="project_truth",
        ),
    )
    before = tuple(item.to_dict() for item in existing)

    result = _plan(_full_payload(), existing)
    conflicts = {
        item.candidate_plan_id: item for item in result.conflict_reconciliations
    }
    player_conflict = conflicts[_candidate(result, "player", "id:player-001").candidate_plan_id]
    setting_match = conflicts[_candidate(result, "setting", "id:setting-001").candidate_plan_id]

    assert player_conflict.conflict_state == "conflict_pending_owner_review"
    assert setting_match.conflict_state == "matches_existing"
    for reconciliation in (player_conflict, setting_match):
        assert reconciliation.owner_decision_status == "pending_owner_review"
        assert reconciliation.automatic_resolution is None
        assert reconciliation.overwrite_performed is False
        assert reconciliation.existing_context_mutated is False
        assert reconciliation.candidate_approved is False
    assert tuple(item.to_dict() for item in existing) == before
    assert tuple(item.to_dict() for item in result.existing_context_records) == before


def test_omitted_and_empty_categories_are_explicit_non_deleting_no_ops() -> None:
    result = _plan(_minimal_payload())
    dispositions = {
        item.category: item for item in result.category_dispositions
    }

    assert dispositions["player"].source_state == "present_empty"
    assert dispositions["player"].candidate_count == 0
    assert dispositions["player"].import_action == "no_op_empty"
    for category in set(NCP_MAPPING_CATEGORIES) - {"metadata", "narrative", "player"}:
        disposition = dispositions[category]
        assert disposition.source_state == "omitted"
        assert disposition.candidate_count == 0
        assert disposition.import_action == "no_op_omitted"
        assert disposition.preserves_existing_context is True
        assert disposition.deletion_intent is False
        assert disposition.omission_policy == NCP_OMITTED_FIELD_IMPORT_POLICY


def test_unknown_fields_are_referenced_as_uninterpreted_not_imported_as_facts() -> None:
    result = _plan(_full_payload())
    pointers = {
        item.json_pointer for item in result.uninterpreted_source_references
    }

    assert "/future_top_level" in pointers
    assert "/story/narratives/0/subtext/players/0/future_player_field" in pointers
    for reference in result.uninterpreted_source_references:
        assert reference.preserved_as_source_metadata is True
        assert reference.imported_as_fact is False
        assert reference.candidate_created is False
        assert reference.deletion_intent is False


def test_owner_review_handoff_is_pending_and_separate_from_authority() -> None:
    result = _plan(_full_payload())
    handoff = result.owner_review_handoff

    assert handoff.candidate_plan_ids == tuple(
        candidate.candidate_plan_id for candidate in result.candidates
    )
    assert handoff.reconciliation_ids == tuple(
        conflict.reconciliation_id for conflict in result.conflict_reconciliations
    )
    assert handoff.review_status == "pending_owner_review"
    assert handoff.candidate_only is True
    assert handoff.owner_action_required is True
    assert handoff.owner_decision_recorded is False
    assert handoff.approval_performed is False
    assert handoff.promotion_performed is False
    assert handoff.apply_promotion_performed is False
    assert handoff.persisted is False


def test_tampered_safety_boundary_or_review_status_fails_validation() -> None:
    plan = _plan(_full_payload())
    weakened = copy.deepcopy(plan.to_dict())
    weakened["safety_boundary"]["project_state_write_performed"] = True

    with pytest.raises(NcpCandidateImportValidationError) as safety_error:
        validate_ncp_candidate_import_plan_record(weakened)
    assert safety_error.value.code == "weakened_safety_boundary"

    approved = copy.deepcopy(plan.to_dict())
    approved["owner_review_handoff"]["review_status"] = "approved"
    approved["plan_hash"] = compute_ncp_candidate_import_plan_hash(approved)
    approved["plan_id"] = f"ncp-candidate-import-plan-{approved['plan_hash'][:32]}"

    with pytest.raises(NcpCandidateImportValidationError) as review_error:
        validate_ncp_candidate_import_plan_record(approved)
    assert review_error.value.code == "unsafe_owner_review_handoff"

    candidate_approved = copy.deepcopy(plan.to_dict())
    candidate_approved["candidates"][0]["review_status"] = "approved"
    candidate_approved["plan_hash"] = compute_ncp_candidate_import_plan_hash(
        candidate_approved
    )
    candidate_approved["plan_id"] = (
        f"ncp-candidate-import-plan-{candidate_approved['plan_hash'][:32]}"
    )
    with pytest.raises(NcpCandidateImportValidationError) as candidate_error:
        validate_ncp_candidate_import_plan_record(candidate_approved)
    assert candidate_error.value.code == "unsafe_candidate_state"


def test_invalid_existing_context_fingerprints_fail_closed() -> None:
    validated, mapping, provenance = _chain(_full_payload())
    invalid = (
        NcpExistingContextRecord(
            context_record_id="existing-001",
            category="story_fact",
            match_key="id:any",
            source_value_sha256="not-a-hash",
            authority_scope="canon_write",
        ),
    )

    with pytest.raises(NcpCandidateImportValidationError) as error:
        build_ncp_candidate_import_plan(
            validated,
            mapping,
            provenance,
            existing_context_records=invalid,
        )

    assert error.value.code == "invalid_existing_context"


def test_plan_contains_no_copied_generated_or_transformed_story_prose() -> None:
    result = _plan(_full_payload())
    serialized = json.dumps(result.to_dict(), ensure_ascii=False)

    assert EXACT_SOURCE_PROSE not in serialized
    assert result.safety_boundary.generated_prose is False
    assert result.safety_boundary.prose_transformation is False
    assert result.safety_boundary.diagnostic_state_settled is False


def test_planning_performs_no_io_runtime_network_subprocess_model_or_write(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    validated, mapping, provenance = _chain(_full_payload())
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

    result = build_ncp_candidate_import_plan(validated, mapping, provenance)

    assert calls == []
    assert result.safety_boundary == NcpCandidateImportSafetyBoundary()
    safety = result.safety_boundary.to_dict()
    assert safety["in_memory_plan_only"] is True
    for field in (
        "candidate_persistence_performed",
        "review_write_performed",
        "project_state_write_performed",
        "existing_context_mutation_performed",
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
        "validator_execution",
        "diagnostic_state_settled",
    ):
        assert safety[field] is False
