"""Focused T010G NCP drift and round-trip matrix contract tests."""

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
    build_ncp_candidate_import_plan,
)
from backend.story_knowledge.ncp_export_contract import (
    NCP_CANDIDATE_REVIEW_PACKAGE_KIND,
    NCP_STANDARD_EXPORT_PACKAGE_KIND,
    build_ncp_approved_context_export_record,
    plan_ncp_exports,
)
from backend.story_knowledge.ncp_export_validation_contract import (
    NCP_SCHEMA_JSON_PATH,
    NCP_SCHEMA_JSON_SHA256,
    NCP_SCHEMA_RECOVERY_PATH,
    NCP_SCHEMA_YAML_PATH,
    NCP_PACKAGE_JSON_PATH,
    build_ncp_schema_interface_evidence,
    validate_ncp_export_before_export,
)
from backend.story_knowledge.ncp_import_contract import validate_ncp_import_artifact
from backend.story_knowledge.ncp_mapping_contract import (
    NCP_MAPPING_CATEGORIES,
    map_validated_ncp_import,
)
from backend.story_knowledge.ncp_provenance_contract import (
    NCP_EXTERNAL_STATUS_POLICY,
    build_ncp_source_provenance,
)
from backend.story_knowledge.ncp_roundtrip_matrix_contract import (
    NCP_MATRIX_CLASS_EXACT_SCHEMA,
    NCP_MATRIX_CLASS_EXPORT_COMPLETENESS,
    NCP_MATRIX_CLASS_FLATTENING,
    NCP_MATRIX_CLASS_SCHEMA_DRIFT,
    NCP_MATRIX_CLASS_SEMANTIC_DRIFT,
    NCP_MATRIX_GATE_ALLOW,
    NCP_MATRIX_GATE_FAIL_CLOSED,
    NCP_MATRIX_GATE_PRESERVE,
    NCP_MATRIX_GATE_REVIEW_ONLY,
    NCP_MATRIX_GENERIC_FACT_SHAPE,
    NCP_REQUIRED_MATRIX_SCENARIOS,
    NcpRoundTripMatrixSafetyBoundary,
    NcpRoundTripMatrixValidationError,
    build_ncp_roundtrip_matrix,
    compute_ncp_roundtrip_matrix_hash,
    validate_ncp_roundtrip_matrix_record,
)


ROOT = Path(__file__).resolve().parents[1]
APPROVED_SOURCE_TEXT = "Exact owner-approved context is validated without transformation."
EXTERNAL_SOURCE_TEXT = "External source text remains candidate-only evidence."


def _schema_interface():
    return build_ncp_schema_interface_evidence(
        schema_json_bytes=(ROOT / NCP_SCHEMA_JSON_PATH).read_bytes(),
        schema_yaml_bytes=(ROOT / NCP_SCHEMA_YAML_PATH).read_bytes(),
        package_json_bytes=(ROOT / NCP_PACKAGE_JSON_PATH).read_bytes(),
        recovery_record_bytes=(ROOT / NCP_SCHEMA_RECOVERY_PATH).read_bytes(),
    )


def _approved_story() -> dict[str, object]:
    return {
        "id": "story_t010g",
        "title": "Approved title",
        "genre": "analysis-fixture",
        "logline": APPROVED_SOURCE_TEXT,
        "created_at": "2026-10-01T12:00:00Z",
        "narratives": [
            {
                "id": "narrative_t010g",
                "title": "Approved narrative",
                "subtext": {
                    "perspectives": [],
                    "players": [],
                    "dynamics": [],
                    "storypoints": [],
                    "storybeats": [],
                },
                "storytelling": {"overviews": [], "moments": []},
            }
        ],
    }


def _external_payload() -> dict[str, object]:
    story = _approved_story()
    narrative = story["narratives"][0]  # type: ignore[index]
    narrative["status"] = "complete"  # type: ignore[index]
    narrative["subtext"]["players"] = [  # type: ignore[index]
        {
            "id": "player_external",
            "name": "External player",
            "summary": EXTERNAL_SOURCE_TEXT,
            "future_player_field": {"preserve": True},
        }
    ]
    return {
        "schema_version": "1.3.0",
        "future_top_level": {"uninterpreted": True},
        "story": story,
    }


def _chain():
    validated = validate_ncp_import_artifact(
        json.dumps(_external_payload(), ensure_ascii=False, indent=2).encode("utf-8"),
        project_id="project-t010g",
        source_reference="owner-selected/imports/t010g.ncp.json",
    )
    mapping = map_validated_ncp_import(validated)
    provenance = build_ncp_source_provenance(validated, mapping)
    candidate_plan = build_ncp_candidate_import_plan(validated, mapping, provenance)
    approved = (
        build_ncp_approved_context_export_record(
            approved_context_record_id="approved-context-t010g",
            approval_record_id="approval-t010g",
            category="metadata",
            ncp_json_pointer="/story",
            source_value=_approved_story(),
        ),
    )
    export_plan = plan_ncp_exports(
        approved,
        include_candidate_review_bundle=True,
        candidate_import_plan=candidate_plan,
    )
    schema_interface = _schema_interface()
    export_validation = validate_ncp_export_before_export(
        export_plan, schema_interface
    )
    return {
        "validated_import": validated,
        "mapping": mapping,
        "provenance": provenance,
        "candidate_import_plan": candidate_plan,
        "export_plan": export_plan,
        "export_validation": export_validation,
        "schema_interface": schema_interface,
    }


def _matrix(chain: dict[str, object] | None = None):
    return build_ncp_roundtrip_matrix(**(chain or _chain()))  # type: ignore[arg-type]


def _row(matrix, scenario_id: str):
    return next(row for row in matrix.rows if row.scenario_id == scenario_id)


def test_matrix_is_deterministic_complete_and_bound_to_recovered_interface() -> None:
    chain = _chain()
    first = _matrix(chain)
    second = _matrix(chain)

    assert first == second
    assert tuple(row.scenario_id for row in first.rows) == NCP_REQUIRED_MATRIX_SCENARIOS
    assert first.schema_path == NCP_SCHEMA_JSON_PATH
    assert first.schema_sha256 == NCP_SCHEMA_JSON_SHA256
    assert first.schema_interface_id == chain["schema_interface"].schema_interface_id
    assert first.schema_interface_hash == chain["schema_interface"].schema_interface_hash
    assert all(row.schema_interface_id == first.schema_interface_id for row in first.rows)
    assert all(row.schema_interface_hash == first.schema_interface_hash for row in first.rows)
    assert first.matrix_hash == compute_ncp_roundtrip_matrix_hash(first.to_dict())
    assert validate_ncp_roundtrip_matrix_record(first.to_dict()) == first.to_dict()
    with pytest.raises(FrozenInstanceError):
        first.matrix_hash = "changed"  # type: ignore[misc]


def test_exact_interface_is_distinct_from_schema_drift() -> None:
    matrix = _matrix()
    exact = _row(matrix, "exact_supported_schema_interface")

    assert exact.classifications == (NCP_MATRIX_CLASS_EXACT_SCHEMA,)
    assert exact.schema_drift is False
    assert exact.recommended_gate_outcome == "continue_validation"
    for scenario_id in (
        "unsupported_schema_hash",
        "unsupported_schema_version",
        "unsupported_schema_path",
    ):
        drift = _row(matrix, scenario_id)
        assert drift.classifications == (NCP_MATRIX_CLASS_SCHEMA_DRIFT,)
        assert drift.schema_drift is True
        assert drift.recommended_gate_outcome == NCP_MATRIX_GATE_FAIL_CLOSED


def test_semantic_drift_and_generic_fact_flattening_fail_closed() -> None:
    matrix = _matrix()
    semantic = _row(matrix, "semantic_category_identity_shift")
    flattened = _row(matrix, "generic_story_fact_flattening")

    assert semantic.semantic_drift is True
    assert NCP_MATRIX_CLASS_SEMANTIC_DRIFT in semantic.classifications
    assert semantic.category_identity == "player_to_storypoint"
    assert semantic.recommended_gate_outcome == NCP_MATRIX_GATE_FAIL_CLOSED
    assert flattened.flattening_risk is True
    assert flattened.semantic_drift is True
    assert NCP_MATRIX_CLASS_FLATTENING in flattened.classifications
    assert flattened.category_identity == NCP_MATRIX_GENERIC_FACT_SHAPE
    assert set(NCP_MAPPING_CATEGORIES).issubset(flattened.evidence_references)
    assert flattened.recommended_gate_outcome == NCP_MATRIX_GATE_FAIL_CLOSED


def test_export_completeness_rows_cover_category_provenance_and_safety() -> None:
    matrix = _matrix()
    for scenario_id in (
        "missing_required_approved_category",
        "missing_approved_provenance",
        "weakened_safety_boundary",
        "pending_candidate_leakage",
    ):
        row = _row(matrix, scenario_id)
        assert NCP_MATRIX_CLASS_EXPORT_COMPLETENESS in row.classifications
        assert row.export_completeness_failure is True
        assert row.recommended_gate_outcome == NCP_MATRIX_GATE_FAIL_CLOSED
        assert row.evidence_references


def test_real_supported_round_trip_trust_and_non_trust_are_separate() -> None:
    matrix = _matrix()
    trusted = _row(matrix, "trusted_app_generated_round_trip")
    external = _row(matrix, "external_import_round_trip_rejected")
    review = _row(matrix, "candidate_review_bundle_round_trip")

    assert trusted.package_kind == NCP_STANDARD_EXPORT_PACKAGE_KIND
    assert trusted.trusted_round_trip_eligible is True
    assert trusted.review_only is False
    assert trusted.recommended_gate_outcome == NCP_MATRIX_GATE_ALLOW
    assert trusted.export_validation_id is not None
    assert trusted.export_validation_hash is not None

    assert external.trusted_round_trip_eligible is False
    assert external.review_only is True
    assert external.source_metadata_only is True
    assert external.recommended_gate_outcome == NCP_MATRIX_GATE_REVIEW_ONLY

    assert review.package_kind == NCP_CANDIDATE_REVIEW_PACKAGE_KIND
    assert review.trusted_round_trip_eligible is False
    assert review.review_only is True
    assert review.recommended_gate_outcome == NCP_MATRIX_GATE_REVIEW_ONLY


def test_external_complete_and_candidate_bundle_never_gain_local_authority() -> None:
    matrix = _matrix()
    complete = _row(matrix, "external_complete_source_metadata")
    bundle_as_standard = _row(matrix, "candidate_bundle_treated_as_standard")

    assert "external-status:complete" in complete.evidence_references
    assert NCP_EXTERNAL_STATUS_POLICY in complete.evidence_references
    assert complete.source_metadata_only is True
    assert complete.review_only is True
    assert complete.local_approval is False
    assert complete.canon_authority is False
    assert complete.memory_authority is False
    assert complete.promotion_authority is False
    assert complete.apply_promotion_authority is False
    assert bundle_as_standard.semantic_drift is True
    assert bundle_as_standard.recommended_gate_outcome == NCP_MATRIX_GATE_FAIL_CLOSED


def test_unknown_and_omitted_fields_remain_non_deleting_metadata() -> None:
    matrix = _matrix()
    unknown = _row(matrix, "unknown_source_field_preserved")
    omitted = _row(matrix, "omitted_field_non_deletion")

    assert unknown.source_metadata_only is True
    assert unknown.recommended_gate_outcome == NCP_MATRIX_GATE_PRESERVE
    assert unknown.deletion_intent is False
    assert omitted.source_metadata_only is True
    assert omitted.recommended_gate_outcome == NCP_MATRIX_GATE_PRESERVE
    assert omitted.deletion_intent is False
    assert all(row.deletion_intent is False for row in matrix.rows)


def test_adversarial_identity_rows_are_tamper_evident_and_fail_closed() -> None:
    matrix = _matrix()
    for scenario_id in (
        "tampered_package_identity",
        "tampered_validation_identity",
        "tampered_round_trip_provenance",
    ):
        row = _row(matrix, scenario_id)
        assert row.integrity_failure is True
        assert row.recommended_gate_outcome == NCP_MATRIX_GATE_FAIL_CLOSED
        assert row.row_id == f"ncp-roundtrip-row-{row.row_hash[:32]}"


@pytest.mark.parametrize(
    "mutate, expected_code",
    [
        (
            lambda chain: chain.update(
                schema_interface=replace(
                    chain["schema_interface"], schema_interface_id="unsupported"
                )
            ),
            "invalid_t010_chain",
        ),
        (
            lambda chain: chain.update(
                export_plan=replace(
                    chain["export_plan"],
                    standard_export=replace(
                        chain["export_plan"].standard_export, package_hash="0" * 64
                    ),
                )
            ),
            "invalid_t010_chain",
        ),
        (
            lambda chain: chain.update(
                export_validation=replace(
                    chain["export_validation"], result_hash="0" * 64
                )
            ),
            "invalid_t010_chain",
        ),
        (
            lambda chain: chain.update(
                export_plan=replace(
                    chain["export_plan"],
                    standard_export=replace(
                        chain["export_plan"].standard_export,
                        safety_boundary=replace(
                            chain["export_plan"].standard_export.safety_boundary,
                            candidate_records_included=True,
                        ),
                    ),
                )
            ),
            "invalid_t010_chain",
        ),
        (
            lambda chain: chain.update(
                provenance=replace(chain["provenance"], provenance_hash="0" * 64)
            ),
            "t010c_integrity_failure",
        ),
    ],
)
def test_tampered_live_chain_inputs_fail_before_matrix_build(mutate, expected_code) -> None:
    chain = _chain()
    mutate(chain)
    with pytest.raises(NcpRoundTripMatrixValidationError) as error:
        _matrix(chain)
    assert error.value.code == expected_code


def test_matrix_record_rejects_row_or_gate_tampering() -> None:
    matrix = _matrix()
    tampered = copy.deepcopy(matrix.to_dict())
    tampered["rows"][1]["recommended_gate_outcome"] = NCP_MATRIX_GATE_ALLOW
    tampered["rows"][1]["row_hash"] = "0" * 64
    tampered["matrix_hash"] = compute_ncp_roundtrip_matrix_hash(tampered)
    tampered["matrix_id"] = f"ncp-roundtrip-matrix-{tampered['matrix_hash'][:32]}"

    with pytest.raises(NcpRoundTripMatrixValidationError) as error:
        validate_ncp_roundtrip_matrix_record(tampered)
    assert error.value.code == "matrix_row_hash_mismatch"


def test_every_row_has_deterministic_evidence_and_gate_outcome() -> None:
    matrix = _matrix()
    allowed_gates = {
        "continue_validation",
        NCP_MATRIX_GATE_FAIL_CLOSED,
        NCP_MATRIX_GATE_ALLOW,
        NCP_MATRIX_GATE_REVIEW_ONLY,
        NCP_MATRIX_GATE_PRESERVE,
    }

    assert len({row.row_id for row in matrix.rows}) == len(matrix.rows)
    for row in matrix.rows:
        assert row.row_id == f"ncp-roundtrip-row-{row.row_hash[:32]}"
        assert row.evidence_references
        assert len(row.evidence_references) == len(set(row.evidence_references))
        assert row.recommended_gate_outcome in allowed_gates
        if any(
            (
                row.schema_drift,
                row.semantic_drift,
                row.flattening_risk,
                row.export_completeness_failure,
                row.integrity_failure,
            )
        ):
            assert row.recommended_gate_outcome == NCP_MATRIX_GATE_FAIL_CLOSED


def test_matrix_performs_no_io_runtime_or_state_mutation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    chain = _chain()

    def forbidden(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("forbidden side effect")

    monkeypatch.setattr(builtins, "open", forbidden)
    monkeypatch.setattr(Path, "write_text", forbidden)
    monkeypatch.setattr(Path, "write_bytes", forbidden)
    monkeypatch.setattr(Path, "mkdir", forbidden)
    monkeypatch.setattr(subprocess, "run", forbidden)
    monkeypatch.setattr(subprocess, "Popen", forbidden)
    monkeypatch.setattr(os, "system", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)

    matrix = _matrix(chain)
    assert matrix.safety_boundary == NcpRoundTripMatrixSafetyBoundary()
    safety = matrix.safety_boundary
    assert safety.destination_write_performed is False
    assert safety.file_write_performed is False
    assert safety.project_state_write_performed is False
    assert safety.candidate_write_performed is False
    assert safety.review_write_performed is False
    assert safety.memory_write_performed is False
    assert safety.canon_write_performed is False
    assert safety.approval_performed is False
    assert safety.promotion_performed is False
    assert safety.apply_promotion_performed is False
    assert safety.node_execution is False
    assert safety.npm_execution is False
    assert safety.subprocess_execution is False
    assert safety.network_execution is False
    assert safety.model_execution is False
    assert safety.external_validator_execution is False


def test_matrix_never_copies_generates_or_transforms_story_prose() -> None:
    matrix = _matrix()
    serialized = json.dumps(matrix.to_dict(), ensure_ascii=False)

    assert APPROVED_SOURCE_TEXT not in serialized
    assert EXTERNAL_SOURCE_TEXT not in serialized
    assert matrix.safety_boundary.generated_prose is False
    assert matrix.safety_boundary.prose_transformation is False
    assert all(row.local_approval is False for row in matrix.rows)
    assert all(row.canon_authority is False for row in matrix.rows)
    assert all(row.memory_authority is False for row in matrix.rows)
    assert all(row.promotion_authority is False for row in matrix.rows)
    assert all(row.apply_promotion_authority is False for row in matrix.rows)
