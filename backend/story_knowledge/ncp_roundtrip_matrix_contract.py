"""Deterministic T010G NCP drift and round-trip validation matrix.

The matrix revalidates the pure T010A through T010F value chain before it
emits actual and adversarial scenario rows.  Rows classify schema drift,
semantic drift, generic-fact flattening, export completeness, metadata
preservation, integrity failures, and round-trip trust.  They contain only
identities, hashes, policy labels, and category names; source prose is never
copied into the matrix.

This module performs no persistence, destination writes, live validation,
Node/npm/subprocess/network/model execution, owner decisions, or local truth
mutation.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Mapping

from backend.story_knowledge.ncp_candidate_import_contract import (
    NCP_CANDIDATE_REVIEW_STATUS,
    NCP_OMITTED_FIELD_IMPORT_POLICY,
    NcpCandidateImportPlan,
    NcpCandidateImportValidationError,
    validate_ncp_candidate_import_plan_record,
)
from backend.story_knowledge.ncp_export_contract import (
    NCP_CANDIDATE_REVIEW_PACKAGE_KIND,
    NCP_EXPORT_OMISSION_POLICY,
    NCP_STANDARD_EXPORT_PACKAGE_KIND,
    NcpExportPlan,
    NcpExportValidationError,
    validate_ncp_export_plan_record,
)
from backend.story_knowledge.ncp_export_validation_contract import (
    NCP_EXTERNAL_IMPORT_REQUIRED_FLOW,
    NCP_SCHEMA_JSON_PATH,
    NCP_SCHEMA_JSON_SHA256,
    NcpExportPreflightValidationError,
    NcpExportValidationResult,
    NcpSchemaInterfaceEvidence,
    assess_external_ncp_round_trip_trust,
    validate_ncp_export_before_export,
    validate_ncp_export_validation_result_record,
)
from backend.story_knowledge.ncp_import_contract import (
    NCP_APP_MAPPING_VERSION,
    NCP_UNKNOWN_FIELD_POLICY,
    SUPPORTED_NCP_SCHEMA_VERSION,
    NcpImportValidationError,
    NcpImportValidationResult,
    validate_ncp_import_artifact,
)
from backend.story_knowledge.ncp_mapping_contract import (
    NCP_MAPPING_CATEGORIES,
    NCP_OMISSION_POLICY,
    NcpMappingValidationError,
    NcpStructuralMappingResult,
    map_validated_ncp_import,
)
from backend.story_knowledge.ncp_provenance_contract import (
    NCP_EXTERNAL_STATUS_POLICY,
    NcpProvenanceResult,
    NcpProvenanceValidationError,
    build_ncp_source_provenance,
    canonical_source_value_json_bytes,
)


NCP_ROUNDTRIP_MATRIX_CONTRACT_VERSION = "writer-assistant-ncp-roundtrip-matrix.v1"
NCP_MATRIX_SOURCE_KIND = "pure_local_t010a_through_t010f_contract_matrix"
NCP_MATRIX_GENERIC_FACT_SHAPE = "story_fact"

NCP_MATRIX_CLASS_EXACT_SCHEMA = "exact_supported_schema_interface"
NCP_MATRIX_CLASS_SCHEMA_DRIFT = "schema_drift"
NCP_MATRIX_CLASS_SEMANTIC_DRIFT = "semantic_drift"
NCP_MATRIX_CLASS_FLATTENING = "flattening_risk"
NCP_MATRIX_CLASS_EXPORT_COMPLETENESS = "export_completeness_failure"
NCP_MATRIX_CLASS_INTEGRITY = "tamper_or_integrity_failure"
NCP_MATRIX_CLASS_METADATA = "source_metadata_preservation"
NCP_MATRIX_CLASS_OMISSION = "omission_non_deletion"
NCP_MATRIX_CLASS_TRUSTED = "trusted_app_generated_round_trip"
NCP_MATRIX_CLASS_REVIEW_ONLY = "review_only_round_trip"
NCP_MATRIX_CLASS_EXTERNAL = "external_import_untrusted"

NCP_MATRIX_GATE_CONTINUE = "continue_validation"
NCP_MATRIX_GATE_FAIL_CLOSED = "fail_closed"
NCP_MATRIX_GATE_ALLOW = "allow_trusted_round_trip"
NCP_MATRIX_GATE_REVIEW_ONLY = "quarantine_for_owner_review"
NCP_MATRIX_GATE_PRESERVE = "preserve_as_non_authoritative_metadata"

NCP_REQUIRED_MATRIX_SCENARIOS = (
    "exact_supported_schema_interface",
    "unsupported_schema_hash",
    "unsupported_schema_version",
    "unsupported_schema_path",
    "semantic_category_identity_shift",
    "generic_story_fact_flattening",
    "missing_required_approved_category",
    "missing_approved_provenance",
    "weakened_safety_boundary",
    "candidate_bundle_treated_as_standard",
    "pending_candidate_leakage",
    "external_complete_source_metadata",
    "unknown_source_field_preserved",
    "omitted_field_non_deletion",
    "tampered_package_identity",
    "tampered_validation_identity",
    "tampered_round_trip_provenance",
    "trusted_app_generated_round_trip",
    "external_import_round_trip_rejected",
    "candidate_review_bundle_round_trip",
)


class NcpRoundTripMatrixValidationError(ValueError):
    """Fail-closed error for invalid chain evidence or matrix records."""

    def __init__(self, code: str, location: str, detail: str) -> None:
        self.code = code
        self.location = location
        self.detail = detail
        super().__init__(f"{code} at {location or '/'}: {detail}")


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(canonical_source_value_json_bytes(value)).hexdigest()


def _is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


@dataclass(frozen=True)
class NcpRoundTripMatrixSafetyBoundary:
    pure_in_memory_matrix: bool = True
    t010a_through_t010f_revalidation_required: bool = True
    exact_repo_local_schema_identity_required: bool = True
    destination_write_performed: bool = False
    file_write_performed: bool = False
    project_state_write_performed: bool = False
    candidate_write_performed: bool = False
    review_write_performed: bool = False
    memory_write_performed: bool = False
    canon_write_performed: bool = False
    approval_performed: bool = False
    promotion_performed: bool = False
    apply_promotion_performed: bool = False
    generated_prose: bool = False
    prose_transformation: bool = False
    live_ncp_execution: bool = False
    node_execution: bool = False
    npm_execution: bool = False
    subprocess_execution: bool = False
    network_execution: bool = False
    model_execution: bool = False
    external_validator_execution: bool = False

    def to_dict(self) -> dict[str, bool]:
        return {field: getattr(self, field) for field in self.__dataclass_fields__}


@dataclass(frozen=True)
class NcpRoundTripMatrixRow:
    row_id: str
    row_hash: str
    scenario_id: str
    scenario_source: str
    classifications: tuple[str, ...]
    severity: str
    impact: str
    recommended_gate_outcome: str
    evidence_references: tuple[str, ...]
    schema_interface_id: str
    schema_interface_hash: str
    export_validation_id: str | None
    export_validation_hash: str | None
    package_kind: str | None
    category_identity: str | None
    schema_drift: bool = False
    semantic_drift: bool = False
    flattening_risk: bool = False
    export_completeness_failure: bool = False
    integrity_failure: bool = False
    trusted_round_trip_eligible: bool = False
    review_only: bool = False
    source_metadata_only: bool = False
    deletion_intent: bool = False
    local_approval: bool = False
    canon_authority: bool = False
    memory_authority: bool = False
    promotion_authority: bool = False
    apply_promotion_authority: bool = False

    def _hash_material(self) -> dict[str, object]:
        return {
            "scenario_id": self.scenario_id,
            "scenario_source": self.scenario_source,
            "classifications": list(self.classifications),
            "severity": self.severity,
            "impact": self.impact,
            "recommended_gate_outcome": self.recommended_gate_outcome,
            "evidence_references": list(self.evidence_references),
            "schema_interface_id": self.schema_interface_id,
            "schema_interface_hash": self.schema_interface_hash,
            "export_validation_id": self.export_validation_id,
            "export_validation_hash": self.export_validation_hash,
            "package_kind": self.package_kind,
            "category_identity": self.category_identity,
            "schema_drift": self.schema_drift,
            "semantic_drift": self.semantic_drift,
            "flattening_risk": self.flattening_risk,
            "export_completeness_failure": self.export_completeness_failure,
            "integrity_failure": self.integrity_failure,
            "trusted_round_trip_eligible": self.trusted_round_trip_eligible,
            "review_only": self.review_only,
            "source_metadata_only": self.source_metadata_only,
            "deletion_intent": self.deletion_intent,
            "local_approval": self.local_approval,
            "canon_authority": self.canon_authority,
            "memory_authority": self.memory_authority,
            "promotion_authority": self.promotion_authority,
            "apply_promotion_authority": self.apply_promotion_authority,
        }

    def to_dict(self) -> dict[str, object]:
        value = self._hash_material()
        value["row_id"] = self.row_id
        value["row_hash"] = self.row_hash
        return value


@dataclass(frozen=True)
class NcpRoundTripMatrix:
    matrix_id: str
    matrix_hash: str
    schema_interface_id: str
    schema_interface_hash: str
    schema_path: str
    schema_sha256: str
    supported_ncp_schema_version: str
    app_mapping_version: str
    import_validation_id: str
    import_validation_hash: str
    mapping_id: str
    mapping_hash: str
    provenance_id: str
    provenance_hash: str
    candidate_import_plan_id: str
    candidate_import_plan_hash: str
    export_plan_id: str
    export_plan_hash: str
    export_validation_result_id: str
    export_validation_result_hash: str
    external_trust_assessment_id: str
    external_trust_assessment_hash: str
    rows: tuple[NcpRoundTripMatrixRow, ...]
    safety_boundary: NcpRoundTripMatrixSafetyBoundary
    contract_version: str = NCP_ROUNDTRIP_MATRIX_CONTRACT_VERSION
    source_kind: str = NCP_MATRIX_SOURCE_KIND

    def _hash_material(self) -> dict[str, object]:
        return {
            "contract_version": self.contract_version,
            "source_kind": self.source_kind,
            "schema_interface_id": self.schema_interface_id,
            "schema_interface_hash": self.schema_interface_hash,
            "schema_path": self.schema_path,
            "schema_sha256": self.schema_sha256,
            "supported_ncp_schema_version": self.supported_ncp_schema_version,
            "app_mapping_version": self.app_mapping_version,
            "import_validation_id": self.import_validation_id,
            "import_validation_hash": self.import_validation_hash,
            "mapping_id": self.mapping_id,
            "mapping_hash": self.mapping_hash,
            "provenance_id": self.provenance_id,
            "provenance_hash": self.provenance_hash,
            "candidate_import_plan_id": self.candidate_import_plan_id,
            "candidate_import_plan_hash": self.candidate_import_plan_hash,
            "export_plan_id": self.export_plan_id,
            "export_plan_hash": self.export_plan_hash,
            "export_validation_result_id": self.export_validation_result_id,
            "export_validation_result_hash": self.export_validation_result_hash,
            "external_trust_assessment_id": self.external_trust_assessment_id,
            "external_trust_assessment_hash": self.external_trust_assessment_hash,
            "rows": [row.to_dict() for row in self.rows],
            "safety_boundary": self.safety_boundary.to_dict(),
        }

    def to_dict(self) -> dict[str, object]:
        value = self._hash_material()
        value["matrix_id"] = self.matrix_id
        value["matrix_hash"] = self.matrix_hash
        return value


def _row(
    *,
    scenario_id: str,
    scenario_source: str,
    classifications: tuple[str, ...],
    severity: str,
    impact: str,
    gate: str,
    evidence: tuple[str, ...],
    schema_interface: NcpSchemaInterfaceEvidence,
    validation_id: str | None,
    validation_hash: str | None,
    package_kind: str | None = None,
    category_identity: str | None = None,
    schema_drift: bool = False,
    semantic_drift: bool = False,
    flattening_risk: bool = False,
    export_completeness_failure: bool = False,
    integrity_failure: bool = False,
    trusted: bool = False,
    review_only: bool = False,
    source_metadata_only: bool = False,
) -> NcpRoundTripMatrixRow:
    ordered_evidence = tuple(dict.fromkeys(evidence))
    provisional = NcpRoundTripMatrixRow(
        row_id="pending",
        row_hash="pending",
        scenario_id=scenario_id,
        scenario_source=scenario_source,
        classifications=classifications,
        severity=severity,
        impact=impact,
        recommended_gate_outcome=gate,
        evidence_references=ordered_evidence,
        schema_interface_id=schema_interface.schema_interface_id,
        schema_interface_hash=schema_interface.schema_interface_hash,
        export_validation_id=validation_id,
        export_validation_hash=validation_hash,
        package_kind=package_kind,
        category_identity=category_identity,
        schema_drift=schema_drift,
        semantic_drift=semantic_drift,
        flattening_risk=flattening_risk,
        export_completeness_failure=export_completeness_failure,
        integrity_failure=integrity_failure,
        trusted_round_trip_eligible=trusted,
        review_only=review_only,
        source_metadata_only=source_metadata_only,
    )
    row_hash = _canonical_hash(provisional._hash_material())
    return NcpRoundTripMatrixRow(
        row_id=f"ncp-roundtrip-row-{row_hash[:32]}",
        row_hash=row_hash,
        scenario_id=provisional.scenario_id,
        scenario_source=provisional.scenario_source,
        classifications=provisional.classifications,
        severity=provisional.severity,
        impact=provisional.impact,
        recommended_gate_outcome=provisional.recommended_gate_outcome,
        evidence_references=provisional.evidence_references,
        schema_interface_id=provisional.schema_interface_id,
        schema_interface_hash=provisional.schema_interface_hash,
        export_validation_id=provisional.export_validation_id,
        export_validation_hash=provisional.export_validation_hash,
        package_kind=provisional.package_kind,
        category_identity=provisional.category_identity,
        schema_drift=provisional.schema_drift,
        semantic_drift=provisional.semantic_drift,
        flattening_risk=provisional.flattening_risk,
        export_completeness_failure=provisional.export_completeness_failure,
        integrity_failure=provisional.integrity_failure,
        trusted_round_trip_eligible=provisional.trusted_round_trip_eligible,
        review_only=provisional.review_only,
        source_metadata_only=provisional.source_metadata_only,
    )


def _revalidate_chain(
    *,
    validated_import: NcpImportValidationResult,
    mapping: NcpStructuralMappingResult,
    provenance: NcpProvenanceResult,
    candidate_import_plan: NcpCandidateImportPlan,
    export_plan: NcpExportPlan,
    export_validation: NcpExportValidationResult,
    schema_interface: NcpSchemaInterfaceEvidence,
) -> None:
    if not isinstance(validated_import, NcpImportValidationResult):
        raise NcpRoundTripMatrixValidationError(
            "t010a_result_required", "/import", "matrix requires a T010A result"
        )
    try:
        expected_import = validate_ncp_import_artifact(
            validated_import.artifact.original_bytes,
            project_id=validated_import.project_id,
            source_reference=validated_import.artifact.source_reference,
            media_type=validated_import.artifact.media_type,
        )
        expected_mapping = map_validated_ncp_import(validated_import)
        expected_provenance = build_ncp_source_provenance(validated_import, mapping)
        validate_ncp_candidate_import_plan_record(candidate_import_plan.to_dict())
        validate_ncp_export_plan_record(export_plan.to_dict())
        validate_ncp_export_validation_result_record(export_validation.to_dict())
        expected_export_validation = validate_ncp_export_before_export(
            export_plan, schema_interface
        )
    except (
        AttributeError,
        NcpImportValidationError,
        NcpMappingValidationError,
        NcpProvenanceValidationError,
        NcpCandidateImportValidationError,
        NcpExportValidationError,
        NcpExportPreflightValidationError,
    ) as exc:
        raise NcpRoundTripMatrixValidationError(
            "invalid_t010_chain", "", "T010A through T010F evidence failed revalidation"
        ) from exc
    if expected_import != validated_import:
        raise NcpRoundTripMatrixValidationError(
            "t010a_integrity_failure", "/import", "T010A result is not intact"
        )
    if expected_mapping != mapping:
        raise NcpRoundTripMatrixValidationError(
            "t010b_integrity_failure", "/mapping", "T010B result is not intact"
        )
    if expected_provenance != provenance:
        raise NcpRoundTripMatrixValidationError(
            "t010c_integrity_failure", "/provenance", "T010C result is not intact"
        )
    if (
        candidate_import_plan.source_validation_id != validated_import.validation_id
        or candidate_import_plan.source_mapping_id != mapping.mapping_id
        or candidate_import_plan.source_provenance_id != provenance.provenance_id
        or candidate_import_plan.source_artifact_id != validated_import.artifact.artifact_id
    ):
        raise NcpRoundTripMatrixValidationError(
            "t010d_lineage_failure", "/candidate_import", "T010D lineage is mismatched"
        )
    bundle = export_plan.candidate_review_bundle
    if bundle is not None and (
        bundle.source_candidate_import_plan_id != candidate_import_plan.plan_id
    ):
        raise NcpRoundTripMatrixValidationError(
            "t010e_lineage_failure", "/export/candidate_review_bundle", "T010E bundle is unrelated"
        )
    if expected_export_validation != export_validation:
        raise NcpRoundTripMatrixValidationError(
            "t010f_integrity_failure", "/export_validation", "T010F result is not intact"
        )


def _build_rows(
    *,
    validated_import: NcpImportValidationResult,
    mapping: NcpStructuralMappingResult,
    provenance: NcpProvenanceResult,
    candidate_import_plan: NcpCandidateImportPlan,
    export_plan: NcpExportPlan,
    export_validation: NcpExportValidationResult,
    schema_interface: NcpSchemaInterfaceEvidence,
) -> tuple[NcpRoundTripMatrixRow, ...]:
    standard = export_validation.standard_export_validation
    candidate_validation = export_validation.candidate_review_bundle_validation
    external_assessment = assess_external_ncp_round_trip_trust(validated_import)
    actual = "actual_t010_chain"
    fixture = "adversarial_contract_fixture"
    common = (
        schema_interface.schema_interface_id,
        schema_interface.schema_interface_hash,
        export_validation.result_id,
        export_validation.result_hash,
    )
    standard_refs = common + (
        standard.validation_id,
        standard.validation_hash,
        standard.package_id,
        standard.package_hash,
    )
    complete_statuses = tuple(
        status
        for status in validated_import.external_narrative_statuses
        if status.external_status == "complete"
    )
    complete_source = actual if complete_statuses else fixture
    complete_evidence = tuple(
        status.json_pointer for status in complete_statuses
    ) or ("fixture:external-status-complete",)
    rows = [
        _row(
            scenario_id="exact_supported_schema_interface",
            scenario_source=actual,
            classifications=(NCP_MATRIX_CLASS_EXACT_SCHEMA,),
            severity="info",
            impact="recovered_schema_identity_matches_pinned_supported_interface",
            gate=NCP_MATRIX_GATE_CONTINUE,
            evidence=common + (NCP_SCHEMA_JSON_PATH, NCP_SCHEMA_JSON_SHA256),
            schema_interface=schema_interface,
            validation_id=standard.validation_id,
            validation_hash=standard.validation_hash,
            package_kind=standard.package_kind,
        ),
        _row(
            scenario_id="unsupported_schema_hash",
            scenario_source=fixture,
            classifications=(NCP_MATRIX_CLASS_SCHEMA_DRIFT,),
            severity="critical",
            impact="schema_bytes_no_longer_match_supported_interface",
            gate=NCP_MATRIX_GATE_FAIL_CLOSED,
            evidence=common + (NCP_SCHEMA_JSON_SHA256, "fixture:unsupported-schema-sha256"),
            schema_interface=schema_interface,
            validation_id=standard.validation_id,
            validation_hash=standard.validation_hash,
            package_kind=standard.package_kind,
            schema_drift=True,
        ),
        _row(
            scenario_id="unsupported_schema_version",
            scenario_source=fixture,
            classifications=(NCP_MATRIX_CLASS_SCHEMA_DRIFT,),
            severity="critical",
            impact="declared_schema_version_is_not_supported",
            gate=NCP_MATRIX_GATE_FAIL_CLOSED,
            evidence=common + (SUPPORTED_NCP_SCHEMA_VERSION, "fixture:future-schema-version"),
            schema_interface=schema_interface,
            validation_id=standard.validation_id,
            validation_hash=standard.validation_hash,
            package_kind=standard.package_kind,
            schema_drift=True,
        ),
        _row(
            scenario_id="unsupported_schema_path",
            scenario_source=fixture,
            classifications=(NCP_MATRIX_CLASS_SCHEMA_DRIFT,),
            severity="critical",
            impact="declared_schema_path_is_not_the_recovered_interface",
            gate=NCP_MATRIX_GATE_FAIL_CLOSED,
            evidence=common + (NCP_SCHEMA_JSON_PATH, "fixture:other-schema-path"),
            schema_interface=schema_interface,
            validation_id=standard.validation_id,
            validation_hash=standard.validation_hash,
            package_kind=standard.package_kind,
            schema_drift=True,
        ),
        _row(
            scenario_id="semantic_category_identity_shift",
            scenario_source=fixture,
            classifications=(NCP_MATRIX_CLASS_SEMANTIC_DRIFT,),
            severity="critical",
            impact="category_meaning_changes_while_json_shape_remains_structural",
            gate=NCP_MATRIX_GATE_FAIL_CLOSED,
            evidence=standard_refs + ("player", "storypoint"),
            schema_interface=schema_interface,
            validation_id=standard.validation_id,
            validation_hash=standard.validation_hash,
            package_kind=standard.package_kind,
            category_identity="player_to_storypoint",
            semantic_drift=True,
        ),
        _row(
            scenario_id="generic_story_fact_flattening",
            scenario_source=fixture,
            classifications=(NCP_MATRIX_CLASS_FLATTENING, NCP_MATRIX_CLASS_SEMANTIC_DRIFT),
            severity="critical",
            impact="typed_ncp_category_would_be_reduced_to_lossy_generic_fact",
            gate=NCP_MATRIX_GATE_FAIL_CLOSED,
            evidence=standard_refs + (mapping.mapping_id, mapping.mapping_hash) + tuple(NCP_MAPPING_CATEGORIES) + (NCP_MATRIX_GENERIC_FACT_SHAPE,),
            schema_interface=schema_interface,
            validation_id=standard.validation_id,
            validation_hash=standard.validation_hash,
            package_kind=standard.package_kind,
            category_identity=NCP_MATRIX_GENERIC_FACT_SHAPE,
            semantic_drift=True,
            flattening_risk=True,
        ),
        _row(
            scenario_id="missing_required_approved_category",
            scenario_source=fixture,
            classifications=(NCP_MATRIX_CLASS_EXPORT_COMPLETENESS,),
            severity="error",
            impact="required_approved_context_category_is_absent_from_export",
            gate=NCP_MATRIX_GATE_FAIL_CLOSED,
            evidence=standard_refs + ("required:metadata", "fixture:metadata-absent"),
            schema_interface=schema_interface,
            validation_id=standard.validation_id,
            validation_hash=standard.validation_hash,
            package_kind=standard.package_kind,
            category_identity="metadata",
            export_completeness_failure=True,
        ),
        _row(
            scenario_id="missing_approved_provenance",
            scenario_source=fixture,
            classifications=(NCP_MATRIX_CLASS_EXPORT_COMPLETENESS, NCP_MATRIX_CLASS_SEMANTIC_DRIFT),
            severity="critical",
            impact="approved_export_value_has_no_owner_approval_provenance",
            gate=NCP_MATRIX_GATE_FAIL_CLOSED,
            evidence=standard_refs + ("fixture:missing-approval-provenance",),
            schema_interface=schema_interface,
            validation_id=standard.validation_id,
            validation_hash=standard.validation_hash,
            package_kind=standard.package_kind,
            semantic_drift=True,
            export_completeness_failure=True,
        ),
        _row(
            scenario_id="weakened_safety_boundary",
            scenario_source=fixture,
            classifications=(NCP_MATRIX_CLASS_SEMANTIC_DRIFT, NCP_MATRIX_CLASS_EXPORT_COMPLETENESS),
            severity="critical",
            impact="write_or_authority_boundary_differs_from_validated_contract",
            gate=NCP_MATRIX_GATE_FAIL_CLOSED,
            evidence=standard_refs + ("fixture:safety-boundary-weakened",),
            schema_interface=schema_interface,
            validation_id=standard.validation_id,
            validation_hash=standard.validation_hash,
            package_kind=standard.package_kind,
            semantic_drift=True,
            export_completeness_failure=True,
        ),
        _row(
            scenario_id="candidate_bundle_treated_as_standard",
            scenario_source=fixture,
            classifications=(NCP_MATRIX_CLASS_SEMANTIC_DRIFT, NCP_MATRIX_CLASS_REVIEW_ONLY),
            severity="critical",
            impact="review_bundle_would_be_laundered_as_approved_context",
            gate=NCP_MATRIX_GATE_FAIL_CLOSED,
            evidence=common + (NCP_CANDIDATE_REVIEW_PACKAGE_KIND, NCP_STANDARD_EXPORT_PACKAGE_KIND),
            schema_interface=schema_interface,
            validation_id=(candidate_validation.validation_id if candidate_validation else None),
            validation_hash=(candidate_validation.validation_hash if candidate_validation else None),
            package_kind=NCP_CANDIDATE_REVIEW_PACKAGE_KIND,
            semantic_drift=True,
            review_only=True,
        ),
        _row(
            scenario_id="pending_candidate_leakage",
            scenario_source=fixture,
            classifications=(NCP_MATRIX_CLASS_SEMANTIC_DRIFT, NCP_MATRIX_CLASS_EXPORT_COMPLETENESS),
            severity="critical",
            impact="pending_import_candidate_would_enter_standard_approved_export",
            gate=NCP_MATRIX_GATE_FAIL_CLOSED,
            evidence=standard_refs + (candidate_import_plan.plan_id, NCP_CANDIDATE_REVIEW_STATUS),
            schema_interface=schema_interface,
            validation_id=standard.validation_id,
            validation_hash=standard.validation_hash,
            package_kind=standard.package_kind,
            semantic_drift=True,
            export_completeness_failure=True,
        ),
        _row(
            scenario_id="external_complete_source_metadata",
            scenario_source=complete_source,
            classifications=(NCP_MATRIX_CLASS_EXTERNAL, NCP_MATRIX_CLASS_METADATA),
            severity="warning",
            impact="external_complete_remains_source_metadata_without_local_authority",
            gate=NCP_MATRIX_GATE_REVIEW_ONLY,
            evidence=(
                schema_interface.schema_interface_id,
                external_assessment.assessment_id,
                external_assessment.assessment_hash,
                NCP_EXTERNAL_STATUS_POLICY,
                "external-status:complete",
            ) + complete_evidence,
            schema_interface=schema_interface,
            validation_id=None,
            validation_hash=None,
            review_only=True,
            source_metadata_only=True,
        ),
        _row(
            scenario_id="unknown_source_field_preserved",
            scenario_source=actual,
            classifications=(NCP_MATRIX_CLASS_METADATA,),
            severity="info",
            impact="unknown_field_stays_uninterpreted_source_metadata",
            gate=NCP_MATRIX_GATE_PRESERVE,
            evidence=(
                schema_interface.schema_interface_id,
                provenance.provenance_id,
                NCP_UNKNOWN_FIELD_POLICY,
            ) + tuple(candidate_import_plan.uninterpreted_source_references[index].provenance_id for index in range(len(candidate_import_plan.uninterpreted_source_references))),
            schema_interface=schema_interface,
            validation_id=None,
            validation_hash=None,
            source_metadata_only=True,
        ),
        _row(
            scenario_id="omitted_field_non_deletion",
            scenario_source=actual,
            classifications=(NCP_MATRIX_CLASS_OMISSION,),
            severity="info",
            impact="omitted_or_unmapped_field_preserves_existing_context",
            gate=NCP_MATRIX_GATE_PRESERVE,
            evidence=(
                schema_interface.schema_interface_id,
                export_plan.export_plan_id,
                NCP_OMISSION_POLICY,
                NCP_OMITTED_FIELD_IMPORT_POLICY,
                NCP_EXPORT_OMISSION_POLICY,
            ),
            schema_interface=schema_interface,
            validation_id=standard.validation_id,
            validation_hash=standard.validation_hash,
            package_kind=standard.package_kind,
            source_metadata_only=True,
        ),
        _row(
            scenario_id="tampered_package_identity",
            scenario_source=fixture,
            classifications=(NCP_MATRIX_CLASS_INTEGRITY, NCP_MATRIX_CLASS_EXPORT_COMPLETENESS),
            severity="critical",
            impact="package_identity_or_hash_no_longer_matches_t010e",
            gate=NCP_MATRIX_GATE_FAIL_CLOSED,
            evidence=standard_refs + ("fixture:tampered-package-hash",),
            schema_interface=schema_interface,
            validation_id=standard.validation_id,
            validation_hash=standard.validation_hash,
            package_kind=standard.package_kind,
            export_completeness_failure=True,
            integrity_failure=True,
        ),
        _row(
            scenario_id="tampered_validation_identity",
            scenario_source=fixture,
            classifications=(NCP_MATRIX_CLASS_INTEGRITY, NCP_MATRIX_CLASS_EXPORT_COMPLETENESS),
            severity="critical",
            impact="validation_identity_or_hash_no_longer_matches_t010f",
            gate=NCP_MATRIX_GATE_FAIL_CLOSED,
            evidence=standard_refs + ("fixture:tampered-validation-hash",),
            schema_interface=schema_interface,
            validation_id=standard.validation_id,
            validation_hash=standard.validation_hash,
            package_kind=standard.package_kind,
            export_completeness_failure=True,
            integrity_failure=True,
        ),
        _row(
            scenario_id="tampered_round_trip_provenance",
            scenario_source=fixture,
            classifications=(NCP_MATRIX_CLASS_INTEGRITY, NCP_MATRIX_CLASS_SEMANTIC_DRIFT, NCP_MATRIX_CLASS_EXPORT_COMPLETENESS),
            severity="critical",
            impact="trusted_round_trip_provenance_no_longer_matches_validation",
            gate=NCP_MATRIX_GATE_FAIL_CLOSED,
            evidence=standard_refs + (
                export_validation.trusted_round_trip_provenance.provenance_id,
                export_validation.trusted_round_trip_provenance.provenance_hash,
                "fixture:tampered-provenance",
            ),
            schema_interface=schema_interface,
            validation_id=standard.validation_id,
            validation_hash=standard.validation_hash,
            package_kind=standard.package_kind,
            semantic_drift=True,
            export_completeness_failure=True,
            integrity_failure=True,
        ),
        _row(
            scenario_id="trusted_app_generated_round_trip",
            scenario_source=actual,
            classifications=(NCP_MATRIX_CLASS_TRUSTED, NCP_MATRIX_CLASS_EXACT_SCHEMA),
            severity="info",
            impact="validated_app_generated_approved_context_is_round_trip_eligible",
            gate=NCP_MATRIX_GATE_ALLOW,
            evidence=standard_refs + (
                export_validation.trusted_round_trip_provenance.provenance_id,
                export_validation.trusted_round_trip_provenance.provenance_hash,
            ),
            schema_interface=schema_interface,
            validation_id=standard.validation_id,
            validation_hash=standard.validation_hash,
            package_kind=standard.package_kind,
            trusted=True,
        ),
        _row(
            scenario_id="external_import_round_trip_rejected",
            scenario_source=actual,
            classifications=(NCP_MATRIX_CLASS_EXTERNAL, NCP_MATRIX_CLASS_REVIEW_ONLY),
            severity="warning",
            impact="external_import_must_return_to_candidate_review_flow",
            gate=NCP_MATRIX_GATE_REVIEW_ONLY,
            evidence=(
                schema_interface.schema_interface_id,
                validated_import.validation_id,
                candidate_import_plan.plan_id,
                external_assessment.assessment_id,
                NCP_EXTERNAL_IMPORT_REQUIRED_FLOW,
            ),
            schema_interface=schema_interface,
            validation_id=None,
            validation_hash=None,
            review_only=True,
            source_metadata_only=True,
        ),
        _row(
            scenario_id="candidate_review_bundle_round_trip",
            scenario_source=actual,
            classifications=(NCP_MATRIX_CLASS_REVIEW_ONLY,),
            severity="warning",
            impact="candidate_bundle_stays_separately_labeled_and_review_only",
            gate=NCP_MATRIX_GATE_REVIEW_ONLY,
            evidence=(
                schema_interface.schema_interface_id,
                candidate_import_plan.plan_id,
                NCP_CANDIDATE_REVIEW_PACKAGE_KIND,
            ) + ((candidate_validation.validation_id, candidate_validation.validation_hash) if candidate_validation else ("candidate-bundle:not-requested",)),
            schema_interface=schema_interface,
            validation_id=(candidate_validation.validation_id if candidate_validation else None),
            validation_hash=(candidate_validation.validation_hash if candidate_validation else None),
            package_kind=NCP_CANDIDATE_REVIEW_PACKAGE_KIND,
            review_only=True,
            source_metadata_only=True,
        ),
    ]
    return tuple(rows)


def build_ncp_roundtrip_matrix(
    *,
    validated_import: NcpImportValidationResult,
    mapping: NcpStructuralMappingResult,
    provenance: NcpProvenanceResult,
    candidate_import_plan: NcpCandidateImportPlan,
    export_plan: NcpExportPlan,
    export_validation: NcpExportValidationResult,
    schema_interface: NcpSchemaInterfaceEvidence,
) -> NcpRoundTripMatrix:
    """Revalidate T010A-F and build the closed deterministic T010G matrix."""

    _revalidate_chain(
        validated_import=validated_import,
        mapping=mapping,
        provenance=provenance,
        candidate_import_plan=candidate_import_plan,
        export_plan=export_plan,
        export_validation=export_validation,
        schema_interface=schema_interface,
    )
    external_assessment = assess_external_ncp_round_trip_trust(validated_import)
    rows = _build_rows(
        validated_import=validated_import,
        mapping=mapping,
        provenance=provenance,
        candidate_import_plan=candidate_import_plan,
        export_plan=export_plan,
        export_validation=export_validation,
        schema_interface=schema_interface,
    )
    if tuple(row.scenario_id for row in rows) != NCP_REQUIRED_MATRIX_SCENARIOS:
        raise NcpRoundTripMatrixValidationError(
            "incomplete_matrix", "/rows", "required T010G scenarios are missing"
        )
    provisional = NcpRoundTripMatrix(
        matrix_id="pending",
        matrix_hash="pending",
        schema_interface_id=schema_interface.schema_interface_id,
        schema_interface_hash=schema_interface.schema_interface_hash,
        schema_path=NCP_SCHEMA_JSON_PATH,
        schema_sha256=NCP_SCHEMA_JSON_SHA256,
        supported_ncp_schema_version=SUPPORTED_NCP_SCHEMA_VERSION,
        app_mapping_version=NCP_APP_MAPPING_VERSION,
        import_validation_id=validated_import.validation_id,
        import_validation_hash=validated_import.validation_hash,
        mapping_id=mapping.mapping_id,
        mapping_hash=mapping.mapping_hash,
        provenance_id=provenance.provenance_id,
        provenance_hash=provenance.provenance_hash,
        candidate_import_plan_id=candidate_import_plan.plan_id,
        candidate_import_plan_hash=candidate_import_plan.plan_hash,
        export_plan_id=export_plan.export_plan_id,
        export_plan_hash=export_plan.export_plan_hash,
        export_validation_result_id=export_validation.result_id,
        export_validation_result_hash=export_validation.result_hash,
        external_trust_assessment_id=external_assessment.assessment_id,
        external_trust_assessment_hash=external_assessment.assessment_hash,
        rows=rows,
        safety_boundary=NcpRoundTripMatrixSafetyBoundary(),
    )
    matrix_hash = _canonical_hash(provisional._hash_material())
    return NcpRoundTripMatrix(
        matrix_id=f"ncp-roundtrip-matrix-{matrix_hash[:32]}",
        matrix_hash=matrix_hash,
        schema_interface_id=provisional.schema_interface_id,
        schema_interface_hash=provisional.schema_interface_hash,
        schema_path=provisional.schema_path,
        schema_sha256=provisional.schema_sha256,
        supported_ncp_schema_version=provisional.supported_ncp_schema_version,
        app_mapping_version=provisional.app_mapping_version,
        import_validation_id=provisional.import_validation_id,
        import_validation_hash=provisional.import_validation_hash,
        mapping_id=provisional.mapping_id,
        mapping_hash=provisional.mapping_hash,
        provenance_id=provisional.provenance_id,
        provenance_hash=provisional.provenance_hash,
        candidate_import_plan_id=provisional.candidate_import_plan_id,
        candidate_import_plan_hash=provisional.candidate_import_plan_hash,
        export_plan_id=provisional.export_plan_id,
        export_plan_hash=provisional.export_plan_hash,
        export_validation_result_id=provisional.export_validation_result_id,
        export_validation_result_hash=provisional.export_validation_result_hash,
        external_trust_assessment_id=provisional.external_trust_assessment_id,
        external_trust_assessment_hash=provisional.external_trust_assessment_hash,
        rows=provisional.rows,
        safety_boundary=provisional.safety_boundary,
    )


def compute_ncp_roundtrip_matrix_hash(record: Mapping[str, object]) -> str:
    material = dict(record)
    material.pop("matrix_id", None)
    material.pop("matrix_hash", None)
    return _canonical_hash(material)


def validate_ncp_roundtrip_matrix_record(record: object) -> dict[str, object]:
    """Validate serialized T010G output and its row-level integrity."""

    expected_fields = {
        "contract_version", "source_kind", "schema_interface_id",
        "schema_interface_hash", "schema_path", "schema_sha256",
        "supported_ncp_schema_version", "app_mapping_version",
        "import_validation_id", "import_validation_hash", "mapping_id",
        "mapping_hash", "provenance_id", "provenance_hash",
        "candidate_import_plan_id", "candidate_import_plan_hash",
        "export_plan_id", "export_plan_hash", "export_validation_result_id",
        "export_validation_result_hash", "external_trust_assessment_id",
        "external_trust_assessment_hash", "rows", "safety_boundary",
        "matrix_id", "matrix_hash",
    }
    if not isinstance(record, dict) or set(record) != expected_fields:
        raise NcpRoundTripMatrixValidationError(
            "invalid_matrix_record", "", "matrix fields are not closed"
        )
    if (
        record["contract_version"] != NCP_ROUNDTRIP_MATRIX_CONTRACT_VERSION
        or record["source_kind"] != NCP_MATRIX_SOURCE_KIND
        or record["schema_path"] != NCP_SCHEMA_JSON_PATH
        or record["schema_sha256"] != NCP_SCHEMA_JSON_SHA256
        or record["supported_ncp_schema_version"] != SUPPORTED_NCP_SCHEMA_VERSION
        or record["app_mapping_version"] != NCP_APP_MAPPING_VERSION
        or record["safety_boundary"] != NcpRoundTripMatrixSafetyBoundary().to_dict()
    ):
        raise NcpRoundTripMatrixValidationError(
            "unsupported_matrix_contract", "", "matrix version, schema, or safety changed"
        )
    for field in (
        "schema_interface_hash", "import_validation_hash", "mapping_hash",
        "provenance_hash", "candidate_import_plan_hash", "export_plan_hash",
        "export_validation_result_hash", "external_trust_assessment_hash",
    ):
        if not _is_sha256(record[field]):
            raise NcpRoundTripMatrixValidationError(
                "invalid_matrix_hash_reference", f"/{field}", "expected SHA-256 identity"
            )
    rows = record["rows"]
    if not isinstance(rows, list) or tuple(
        row.get("scenario_id") if isinstance(row, dict) else None for row in rows
    ) != NCP_REQUIRED_MATRIX_SCENARIOS:
        raise NcpRoundTripMatrixValidationError(
            "incomplete_matrix", "/rows", "required scenarios are absent or reordered"
        )
    row_expected_fields = set(NcpRoundTripMatrixRow.__dataclass_fields__)
    seen_ids: set[str] = set()
    for index, row in enumerate(rows):
        location = f"/rows/{index}"
        if not isinstance(row, dict) or set(row) != row_expected_fields:
            raise NcpRoundTripMatrixValidationError(
                "invalid_matrix_row", location, "row fields are not closed"
            )
        material = dict(row)
        material.pop("row_id")
        material.pop("row_hash")
        row_hash = _canonical_hash(material)
        if (
            row["row_hash"] != row_hash
            or row["row_id"] != f"ncp-roundtrip-row-{row_hash[:32]}"
            or row["row_id"] in seen_ids
        ):
            raise NcpRoundTripMatrixValidationError(
                "matrix_row_hash_mismatch", location, "row identity is not intact and unique"
            )
        seen_ids.add(row["row_id"])
        if (
            row["schema_interface_id"] != record["schema_interface_id"]
            or row["schema_interface_hash"] != record["schema_interface_hash"]
            or not isinstance(row["evidence_references"], list)
            or not row["evidence_references"]
            or len(row["evidence_references"]) != len(set(row["evidence_references"]))
            or row["local_approval"] is not False
            or row["canon_authority"] is not False
            or row["memory_authority"] is not False
            or row["promotion_authority"] is not False
            or row["apply_promotion_authority"] is not False
            or row["deletion_intent"] is not False
        ):
            raise NcpRoundTripMatrixValidationError(
                "unsafe_matrix_row", location, "row binding or authority boundary changed"
            )
        failure = any(
            row[field] is True
            for field in (
                "schema_drift", "semantic_drift", "flattening_risk",
                "export_completeness_failure", "integrity_failure",
            )
        )
        if failure and row["recommended_gate_outcome"] != NCP_MATRIX_GATE_FAIL_CLOSED:
            raise NcpRoundTripMatrixValidationError(
                "unsafe_matrix_gate", location, "drift or integrity failure must fail closed"
            )
        classifications = row["classifications"]
        if not isinstance(classifications, list) or (
            row["schema_drift"]
            != (NCP_MATRIX_CLASS_SCHEMA_DRIFT in classifications)
            or row["semantic_drift"]
            != (NCP_MATRIX_CLASS_SEMANTIC_DRIFT in classifications)
            or row["flattening_risk"]
            != (NCP_MATRIX_CLASS_FLATTENING in classifications)
            or row["export_completeness_failure"]
            != (NCP_MATRIX_CLASS_EXPORT_COMPLETENESS in classifications)
            or row["integrity_failure"]
            != (NCP_MATRIX_CLASS_INTEGRITY in classifications)
            or row["trusted_round_trip_eligible"]
            != (NCP_MATRIX_CLASS_TRUSTED in classifications)
        ):
            raise NcpRoundTripMatrixValidationError(
                "inconsistent_matrix_classification",
                location,
                "classification labels and machine-checkable flags disagree",
            )
        if row["trusted_round_trip_eligible"] is True and (
            row["recommended_gate_outcome"] != NCP_MATRIX_GATE_ALLOW
            or row["package_kind"] != NCP_STANDARD_EXPORT_PACKAGE_KIND
            or row["review_only"] is not False
        ):
            raise NcpRoundTripMatrixValidationError(
                "unsafe_matrix_trust", location, "only validated standard export may be trusted"
            )
    actual_hash = compute_ncp_roundtrip_matrix_hash(record)
    if (
        record["matrix_hash"] != actual_hash
        or record["matrix_id"] != f"ncp-roundtrip-matrix-{actual_hash[:32]}"
    ):
        raise NcpRoundTripMatrixValidationError(
            "matrix_hash_mismatch", "/matrix_hash", "matrix is not intact"
        )
    return json.loads(json.dumps(record, ensure_ascii=False))
