"""Pure T010H operator-control and traceability contracts for the NCP gateway.

The contract turns validated T010A-T010G value objects into deterministic
operator affordances.  It can report that a standard package is ready for a
future execution handoff, but it cannot write an export, persist an import,
delete or purge artifacts, record review decisions, or mutate project truth.

Destination semantics, retention/deletion policy, destructive operations, and
candidate-bundle execution remain owner decisions.  Consequently destinations
are opaque operator-selected target identifiers rather than filesystem paths,
existing-target overwrite is rejected, and every destructive control is
disabled.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re
from typing import Mapping

from backend.story_knowledge.ncp_candidate_import_contract import (
    NCP_CANDIDATE_REVIEW_STATUS,
    NcpCandidateImportPlan,
)
from backend.story_knowledge.ncp_export_contract import (
    NCP_CANDIDATE_REVIEW_PACKAGE_KIND,
    NCP_STANDARD_EXPORT_PACKAGE_KIND,
    NcpExportPlan,
)
from backend.story_knowledge.ncp_export_validation_contract import (
    NCP_SCHEMA_JSON_PATH,
    NCP_SCHEMA_JSON_SHA256,
    NcpExportValidationResult,
    NcpSchemaInterfaceEvidence,
)
from backend.story_knowledge.ncp_import_contract import NcpImportValidationResult
from backend.story_knowledge.ncp_mapping_contract import NcpStructuralMappingResult
from backend.story_knowledge.ncp_provenance_contract import (
    NCP_EXTERNAL_STATUS_POLICY,
    NcpProvenanceResult,
    canonical_source_value_json_bytes,
)
from backend.story_knowledge.ncp_roundtrip_matrix_contract import (
    NCP_MATRIX_GATE_ALLOW,
    NCP_MATRIX_GATE_FAIL_CLOSED,
    NcpRoundTripMatrix,
    NcpRoundTripMatrixValidationError,
    build_ncp_roundtrip_matrix,
    validate_ncp_roundtrip_matrix_record,
)


NCP_OPERATOR_CONTROLS_CONTRACT_VERSION = "writer-assistant-ncp-operator-controls.v1"

NCP_ACTION_NONE = "none"
NCP_ACTION_STANDARD_EXPORT = "standard_approved_context_export"
NCP_ACTION_CANDIDATE_BUNDLE = "candidate_review_bundle_export"
NCP_ACTION_EXTERNAL_IMPORT_REVIEW = "external_import_owner_review"
NCP_ACTION_TRUSTED_ROUND_TRIP = "trusted_app_round_trip_import"
NCP_OPERATOR_ACTIONS = frozenset(
    {
        NCP_ACTION_NONE,
        NCP_ACTION_STANDARD_EXPORT,
        NCP_ACTION_CANDIDATE_BUNDLE,
        NCP_ACTION_EXTERNAL_IMPORT_REVIEW,
        NCP_ACTION_TRUSTED_ROUND_TRIP,
    }
)

NCP_DESTINATION_NOT_SELECTED = "not_selected"
NCP_DESTINATION_SELECTED_NEW_TARGET = "operator_selected_new_target"
NCP_DESTINATION_KIND = "opaque_operator_selected_export_target"
NCP_DESTINATION_POLICY = "explicit_new_target_only_no_path_or_overwrite"

NCP_RETENTION_POLICY_STATUS = "owner_decision_pending_no_action"
NCP_DESTRUCTIVE_POLICY_STATUS = "owner_decision_pending_all_actions_disabled"
NCP_CANDIDATE_BUNDLE_POLICY_STATUS = "owner_decision_pending_review_only"

NCP_AFFORDANCE_STANDARD_EXPORT = "standard_approved_context_export"
NCP_AFFORDANCE_CANDIDATE_BUNDLE = "candidate_review_bundle"
NCP_AFFORDANCE_EXTERNAL_IMPORT = "external_import_review"
NCP_AFFORDANCE_TRUSTED_ROUND_TRIP = "trusted_round_trip"
NCP_AFFORDANCE_MATRIX_GATES = "matrix_gate_diagnostics"
NCP_AFFORDANCE_KINDS = (
    NCP_AFFORDANCE_STANDARD_EXPORT,
    NCP_AFFORDANCE_CANDIDATE_BUNDLE,
    NCP_AFFORDANCE_EXTERNAL_IMPORT,
    NCP_AFFORDANCE_TRUSTED_ROUND_TRIP,
    NCP_AFFORDANCE_MATRIX_GATES,
)

_SAFE_DESTINATION_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


class NcpOperatorControlsValidationError(ValueError):
    """Fail-closed error for unsafe operator input or tampered controls."""

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
class NcpDestinationControl:
    selection_state: str
    destination_id: str | None
    destination_kind: str
    destination_policy: str
    operator_selected: bool
    safe_destination_ready: bool
    new_target_required: bool = True
    target_exists: bool = False
    overwrite_requested: bool = False
    arbitrary_path_accepted: bool = False
    path_traversal_accepted: bool = False
    destructive_action: bool = False
    destination_write_performed: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            field: getattr(self, field) for field in self.__dataclass_fields__
        }


def build_ncp_destination_control(
    destination_id: str | None = None,
    *,
    target_exists: bool = False,
    overwrite_requested: bool = False,
) -> NcpDestinationControl:
    """Build a path-free destination selection; reject overwrite semantics."""

    if type(target_exists) is not bool or type(overwrite_requested) is not bool:
        raise NcpOperatorControlsValidationError(
            "invalid_destination_state", "/destination", "destination flags must be booleans"
        )
    if target_exists or overwrite_requested:
        raise NcpOperatorControlsValidationError(
            "destructive_destination_blocked",
            "/destination",
            "existing-target and overwrite behavior is not authorized",
        )
    if destination_id is None:
        return NcpDestinationControl(
            selection_state=NCP_DESTINATION_NOT_SELECTED,
            destination_id=None,
            destination_kind=NCP_DESTINATION_KIND,
            destination_policy=NCP_DESTINATION_POLICY,
            operator_selected=False,
            safe_destination_ready=False,
        )
    if (
        not isinstance(destination_id, str)
        or not _SAFE_DESTINATION_ID.fullmatch(destination_id)
        or destination_id in {".", ".."}
    ):
        raise NcpOperatorControlsValidationError(
            "unsafe_destination_identifier",
            "/destination/destination_id",
            "destination must be an opaque safe identifier, never a path",
        )
    return NcpDestinationControl(
        selection_state=NCP_DESTINATION_SELECTED_NEW_TARGET,
        destination_id=destination_id,
        destination_kind=NCP_DESTINATION_KIND,
        destination_policy=NCP_DESTINATION_POLICY,
        operator_selected=True,
        safe_destination_ready=True,
    )


def _validate_destination(destination: object) -> NcpDestinationControl:
    if not isinstance(destination, NcpDestinationControl):
        raise NcpOperatorControlsValidationError(
            "destination_control_required", "/destination", "typed destination control required"
        )
    expected = build_ncp_destination_control(
        destination.destination_id,
        target_exists=destination.target_exists,
        overwrite_requested=destination.overwrite_requested,
    )
    if expected != destination:
        raise NcpOperatorControlsValidationError(
            "tampered_destination_control", "/destination", "destination safety changed"
        )
    return expected


@dataclass(frozen=True)
class NcpDestructiveActionPolicy:
    policy_status: str = NCP_DESTRUCTIVE_POLICY_STATUS
    visible_to_operator: bool = True
    destructive_operations_available: bool = False
    overwrite_enabled: bool = False
    replace_enabled: bool = False
    delete_enabled: bool = False
    purge_enabled: bool = False
    rollback_claimed: bool = False
    confirmation_available: bool = False
    execution_performed: bool = False

    def to_dict(self) -> dict[str, object]:
        return {field: getattr(self, field) for field in self.__dataclass_fields__}


@dataclass(frozen=True)
class NcpRetentionDeletionPolicy:
    policy_status: str = NCP_RETENTION_POLICY_STATUS
    visible_to_operator: bool = True
    retention_policy_decided: bool = False
    deletion_policy_decided: bool = False
    retention_action: str = "none"
    deletion_action: str = "disabled"
    purge_action: str = "disabled"
    artifact_deletion_performed: bool = False
    retention_purge_performed: bool = False
    surviving_provenance_preserved: bool = True

    def to_dict(self) -> dict[str, object]:
        return {field: getattr(self, field) for field in self.__dataclass_fields__}


@dataclass(frozen=True)
class NcpOperatorTraceability:
    schema_interface_id: str
    schema_interface_hash: str
    schema_path: str
    schema_sha256: str
    import_artifact_id: str
    import_artifact_sha256: str
    import_source_reference: str
    import_validation_id: str
    import_validation_hash: str
    mapping_id: str
    mapping_hash: str
    provenance_id: str
    provenance_hash: str
    candidate_import_plan_id: str
    candidate_import_plan_hash: str
    owner_review_handoff_id: str
    owner_review_status: str
    export_plan_id: str
    export_plan_hash: str
    standard_package_id: str
    standard_package_hash: str
    candidate_bundle_id: str | None
    candidate_bundle_hash: str | None
    export_validation_result_id: str
    export_validation_result_hash: str
    standard_validation_id: str
    standard_validation_hash: str
    candidate_bundle_validation_id: str | None
    candidate_bundle_validation_hash: str | None
    trusted_round_trip_provenance_id: str
    trusted_round_trip_provenance_hash: str
    matrix_id: str
    matrix_hash: str
    external_trust_assessment_id: str
    external_trust_assessment_hash: str
    external_status_pointers: tuple[str, ...]
    uninterpreted_provenance_ids: tuple[str, ...]
    omitted_or_empty_categories: tuple[str, ...]
    fail_closed_matrix_row_ids: tuple[str, ...]
    active_blocked_matrix_row_ids: tuple[str, ...]
    trusted_matrix_row_id: str
    standard_validation_gate_passed: bool
    trusted_matrix_gate_passed: bool
    external_complete_present: bool
    uninterpreted_fields_source_metadata_only: bool = True
    omitted_fields_deletion_intent: bool = False
    external_status_policy: str = NCP_EXTERNAL_STATUS_POLICY

    def to_dict(self) -> dict[str, object]:
        value = {
            field: getattr(self, field) for field in self.__dataclass_fields__
        }
        for field in (
            "external_status_pointers", "uninterpreted_provenance_ids",
            "omitted_or_empty_categories", "fail_closed_matrix_row_ids",
            "active_blocked_matrix_row_ids",
        ):
            value[field] = list(value[field])
        return value


@dataclass(frozen=True)
class NcpOperatorAffordance:
    affordance_id: str
    affordance_hash: str
    affordance_kind: str
    label: str
    state: str
    visible: bool
    enabled: bool
    ready_for_future_execution_handoff: bool
    separately_labeled: bool
    approved_context_only: bool
    review_only: bool
    trusted_round_trip: bool
    blocked_or_quarantined: bool
    requires_explicit_operator_intent: bool
    requires_safe_destination: bool
    requires_final_confirmation: bool
    trace_references: tuple[str, ...]
    execution_performed: bool = False
    destination_write_performed: bool = False
    local_approval: bool = False
    canon_authority: bool = False
    memory_authority: bool = False
    promotion_authority: bool = False
    apply_promotion_authority: bool = False

    def _hash_material(self) -> dict[str, object]:
        return {
            field: (list(getattr(self, field)) if field == "trace_references" else getattr(self, field))
            for field in self.__dataclass_fields__
            if field not in {"affordance_id", "affordance_hash"}
        }

    def to_dict(self) -> dict[str, object]:
        value = self._hash_material()
        value["affordance_id"] = self.affordance_id
        value["affordance_hash"] = self.affordance_hash
        return value


def _affordance(**values: object) -> NcpOperatorAffordance:
    provisional = NcpOperatorAffordance(
        affordance_id="pending", affordance_hash="pending", **values  # type: ignore[arg-type]
    )
    affordance_hash = _canonical_hash(provisional._hash_material())
    return NcpOperatorAffordance(
        affordance_id=f"ncp-operator-affordance-{affordance_hash[:32]}",
        affordance_hash=affordance_hash,
        **values,  # type: ignore[arg-type]
    )


@dataclass(frozen=True)
class NcpOperatorControlsSafetyBoundary:
    pure_in_memory_controls: bool = True
    t010a_through_t010g_revalidation_required: bool = True
    destination_is_opaque_identifier_not_path: bool = True
    destination_write_performed: bool = False
    file_write_performed: bool = False
    destructive_action_performed: bool = False
    deletion_performed: bool = False
    retention_purge_performed: bool = False
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
class NcpOperatorControlsPlan:
    controls_id: str
    controls_hash: str
    requested_action: str
    explicit_operator_intent: bool
    final_confirmation: bool
    destination: NcpDestinationControl
    affordances: tuple[NcpOperatorAffordance, ...]
    destructive_action_policy: NcpDestructiveActionPolicy
    retention_deletion_policy: NcpRetentionDeletionPolicy
    traceability: NcpOperatorTraceability
    safety_boundary: NcpOperatorControlsSafetyBoundary
    contract_version: str = NCP_OPERATOR_CONTROLS_CONTRACT_VERSION
    candidate_bundle_policy_status: str = NCP_CANDIDATE_BUNDLE_POLICY_STATUS
    actual_execution_supported: bool = False

    def _hash_material(self) -> dict[str, object]:
        return {
            "contract_version": self.contract_version,
            "candidate_bundle_policy_status": self.candidate_bundle_policy_status,
            "actual_execution_supported": self.actual_execution_supported,
            "requested_action": self.requested_action,
            "explicit_operator_intent": self.explicit_operator_intent,
            "final_confirmation": self.final_confirmation,
            "destination": self.destination.to_dict(),
            "affordances": [item.to_dict() for item in self.affordances],
            "destructive_action_policy": self.destructive_action_policy.to_dict(),
            "retention_deletion_policy": self.retention_deletion_policy.to_dict(),
            "traceability": self.traceability.to_dict(),
            "safety_boundary": self.safety_boundary.to_dict(),
        }

    def to_dict(self) -> dict[str, object]:
        value = self._hash_material()
        value["controls_id"] = self.controls_id
        value["controls_hash"] = self.controls_hash
        return value


def _revalidate_t010_chain(
    *,
    validated_import: NcpImportValidationResult,
    mapping: NcpStructuralMappingResult,
    provenance: NcpProvenanceResult,
    candidate_import_plan: NcpCandidateImportPlan,
    export_plan: NcpExportPlan,
    export_validation: NcpExportValidationResult,
    roundtrip_matrix: NcpRoundTripMatrix,
    schema_interface: NcpSchemaInterfaceEvidence,
) -> None:
    try:
        expected_matrix = build_ncp_roundtrip_matrix(
            validated_import=validated_import,
            mapping=mapping,
            provenance=provenance,
            candidate_import_plan=candidate_import_plan,
            export_plan=export_plan,
            export_validation=export_validation,
            schema_interface=schema_interface,
        )
        validate_ncp_roundtrip_matrix_record(roundtrip_matrix.to_dict())
    except (AttributeError, NcpRoundTripMatrixValidationError) as exc:
        raise NcpOperatorControlsValidationError(
            "invalid_t010_chain", "", "operator controls require intact T010A-T010G values"
        ) from exc
    if expected_matrix != roundtrip_matrix:
        raise NcpOperatorControlsValidationError(
            "t010g_integrity_failure", "/matrix", "round-trip matrix is not intact"
        )


def _standard_state(
    *,
    requested_action: str,
    explicit_operator_intent: bool,
    final_confirmation: bool,
    destination: NcpDestinationControl,
    validation_ready: bool,
    trusted_matrix_ready: bool,
) -> tuple[str, bool]:
    if requested_action != NCP_ACTION_STANDARD_EXPORT or not explicit_operator_intent:
        return "awaiting_explicit_operator_intent", False
    if not destination.safe_destination_ready:
        return "awaiting_safe_destination_selection", False
    if not validation_ready or not trusted_matrix_ready:
        return "blocked_validation_or_matrix_gate", False
    if not final_confirmation:
        return "awaiting_final_operator_confirmation", False
    return "ready_for_future_execution_handoff_no_write_performed", True


def build_ncp_operator_controls(
    *,
    validated_import: NcpImportValidationResult,
    mapping: NcpStructuralMappingResult,
    provenance: NcpProvenanceResult,
    candidate_import_plan: NcpCandidateImportPlan,
    export_plan: NcpExportPlan,
    export_validation: NcpExportValidationResult,
    roundtrip_matrix: NcpRoundTripMatrix,
    schema_interface: NcpSchemaInterfaceEvidence,
    requested_action: str = NCP_ACTION_NONE,
    explicit_operator_intent: bool = False,
    final_confirmation: bool = False,
    destination: NcpDestinationControl | None = None,
) -> NcpOperatorControlsPlan:
    """Build safe, traceable affordances without executing any operation."""

    if requested_action not in NCP_OPERATOR_ACTIONS:
        raise NcpOperatorControlsValidationError(
            "unsupported_operator_action", "/requested_action", "action is not supported"
        )
    if type(explicit_operator_intent) is not bool or type(final_confirmation) is not bool:
        raise NcpOperatorControlsValidationError(
            "invalid_operator_intent", "/intent", "intent flags must be booleans"
        )
    if final_confirmation and not explicit_operator_intent:
        raise NcpOperatorControlsValidationError(
            "confirmation_without_intent", "/final_confirmation", "confirmation requires intent"
        )
    if requested_action == NCP_ACTION_NONE and (explicit_operator_intent or final_confirmation):
        raise NcpOperatorControlsValidationError(
            "intent_without_action", "/requested_action", "explicit intent requires an action"
        )
    checked_destination = _validate_destination(
        destination if destination is not None else build_ncp_destination_control()
    )
    _revalidate_t010_chain(
        validated_import=validated_import,
        mapping=mapping,
        provenance=provenance,
        candidate_import_plan=candidate_import_plan,
        export_plan=export_plan,
        export_validation=export_validation,
        roundtrip_matrix=roundtrip_matrix,
        schema_interface=schema_interface,
    )

    standard_validation = export_validation.standard_export_validation
    trusted_row = next(
        row
        for row in roundtrip_matrix.rows
        if row.scenario_id == "trusted_app_generated_round_trip"
    )
    validation_ready = (
        standard_validation.package_kind == NCP_STANDARD_EXPORT_PACKAGE_KIND
        and standard_validation.package_exportable
        and standard_validation.standard_approved_context_export
        and standard_validation.trusted_round_trip_eligible
    )
    trusted_matrix_ready = (
        trusted_row.recommended_gate_outcome == NCP_MATRIX_GATE_ALLOW
        and trusted_row.trusted_round_trip_eligible
    )
    standard_state, standard_ready = _standard_state(
        requested_action=requested_action,
        explicit_operator_intent=explicit_operator_intent,
        final_confirmation=final_confirmation,
        destination=checked_destination,
        validation_ready=validation_ready,
        trusted_matrix_ready=trusted_matrix_ready,
    )
    bundle = export_plan.candidate_review_bundle
    bundle_validation = export_validation.candidate_review_bundle_validation
    fail_closed_rows = tuple(
        row.row_id
        for row in roundtrip_matrix.rows
        if row.recommended_gate_outcome == NCP_MATRIX_GATE_FAIL_CLOSED
    )
    active_blocked_rows = tuple(
        row.row_id
        for row in roundtrip_matrix.rows
        if row.scenario_source == "actual_t010_chain"
        and row.recommended_gate_outcome == NCP_MATRIX_GATE_FAIL_CLOSED
    )
    traceability = NcpOperatorTraceability(
        schema_interface_id=schema_interface.schema_interface_id,
        schema_interface_hash=schema_interface.schema_interface_hash,
        schema_path=NCP_SCHEMA_JSON_PATH,
        schema_sha256=NCP_SCHEMA_JSON_SHA256,
        import_artifact_id=validated_import.artifact.artifact_id,
        import_artifact_sha256=validated_import.artifact.sha256,
        import_source_reference=validated_import.artifact.source_reference,
        import_validation_id=validated_import.validation_id,
        import_validation_hash=validated_import.validation_hash,
        mapping_id=mapping.mapping_id,
        mapping_hash=mapping.mapping_hash,
        provenance_id=provenance.provenance_id,
        provenance_hash=provenance.provenance_hash,
        candidate_import_plan_id=candidate_import_plan.plan_id,
        candidate_import_plan_hash=candidate_import_plan.plan_hash,
        owner_review_handoff_id=candidate_import_plan.owner_review_handoff.handoff_id,
        owner_review_status=candidate_import_plan.owner_review_handoff.review_status,
        export_plan_id=export_plan.export_plan_id,
        export_plan_hash=export_plan.export_plan_hash,
        standard_package_id=export_plan.standard_export.package_id,
        standard_package_hash=export_plan.standard_export.package_hash,
        candidate_bundle_id=bundle.package_id if bundle else None,
        candidate_bundle_hash=bundle.package_hash if bundle else None,
        export_validation_result_id=export_validation.result_id,
        export_validation_result_hash=export_validation.result_hash,
        standard_validation_id=standard_validation.validation_id,
        standard_validation_hash=standard_validation.validation_hash,
        candidate_bundle_validation_id=(bundle_validation.validation_id if bundle_validation else None),
        candidate_bundle_validation_hash=(bundle_validation.validation_hash if bundle_validation else None),
        trusted_round_trip_provenance_id=export_validation.trusted_round_trip_provenance.provenance_id,
        trusted_round_trip_provenance_hash=export_validation.trusted_round_trip_provenance.provenance_hash,
        matrix_id=roundtrip_matrix.matrix_id,
        matrix_hash=roundtrip_matrix.matrix_hash,
        external_trust_assessment_id=roundtrip_matrix.external_trust_assessment_id,
        external_trust_assessment_hash=roundtrip_matrix.external_trust_assessment_hash,
        external_status_pointers=tuple(item.json_pointer for item in provenance.external_statuses),
        uninterpreted_provenance_ids=tuple(
            item.provenance_id for item in candidate_import_plan.uninterpreted_source_references
        ),
        omitted_or_empty_categories=tuple(
            item.category
            for item in candidate_import_plan.category_dispositions
            if item.source_state in {"omitted", "present_empty"}
        ),
        fail_closed_matrix_row_ids=fail_closed_rows,
        active_blocked_matrix_row_ids=active_blocked_rows,
        trusted_matrix_row_id=trusted_row.row_id,
        standard_validation_gate_passed=validation_ready,
        trusted_matrix_gate_passed=trusted_matrix_ready,
        external_complete_present=any(
            item.external_status == "complete" for item in provenance.external_statuses
        ),
    )

    standard_refs = (
        export_plan.standard_export.package_id,
        standard_validation.validation_id,
        trusted_row.row_id,
        roundtrip_matrix.matrix_id,
    )
    affordances = (
        _affordance(
            affordance_kind=NCP_AFFORDANCE_STANDARD_EXPORT,
            label="Approved Context Standard NCP Export",
            state=standard_state,
            visible=True,
            enabled=standard_ready,
            ready_for_future_execution_handoff=standard_ready,
            separately_labeled=True,
            approved_context_only=True,
            review_only=False,
            trusted_round_trip=validation_ready and trusted_matrix_ready,
            blocked_or_quarantined=not standard_ready,
            requires_explicit_operator_intent=True,
            requires_safe_destination=True,
            requires_final_confirmation=True,
            trace_references=standard_refs,
        ),
        _affordance(
            affordance_kind=NCP_AFFORDANCE_CANDIDATE_BUNDLE,
            label="Candidate Review Bundle - Review Only",
            state=(
                "blocked_owner_policy_pending"
                if bundle is not None
                else "unavailable_no_candidate_bundle"
            ),
            visible=True,
            enabled=False,
            ready_for_future_execution_handoff=False,
            separately_labeled=True,
            approved_context_only=False,
            review_only=True,
            trusted_round_trip=False,
            blocked_or_quarantined=True,
            requires_explicit_operator_intent=True,
            requires_safe_destination=True,
            requires_final_confirmation=True,
            trace_references=tuple(
                value
                for value in (
                    bundle.package_id if bundle else None,
                    bundle_validation.validation_id if bundle_validation else None,
                    candidate_import_plan.plan_id,
                )
                if value is not None
            ),
        ),
        _affordance(
            affordance_kind=NCP_AFFORDANCE_EXTERNAL_IMPORT,
            label="External NCP Import - Owner Review Required",
            state="candidate_only_owner_review_required",
            visible=True,
            enabled=True,
            ready_for_future_execution_handoff=False,
            separately_labeled=True,
            approved_context_only=False,
            review_only=True,
            trusted_round_trip=False,
            blocked_or_quarantined=True,
            requires_explicit_operator_intent=True,
            requires_safe_destination=False,
            requires_final_confirmation=False,
            trace_references=(
                validated_import.validation_id,
                candidate_import_plan.plan_id,
                candidate_import_plan.owner_review_handoff.handoff_id,
            ),
        ),
        _affordance(
            affordance_kind=NCP_AFFORDANCE_TRUSTED_ROUND_TRIP,
            label="Trusted App-Generated Round Trip",
            state=("available_validated_app_package" if trusted_matrix_ready else "blocked_trust_gate"),
            visible=True,
            enabled=trusted_matrix_ready,
            ready_for_future_execution_handoff=False,
            separately_labeled=True,
            approved_context_only=True,
            review_only=False,
            trusted_round_trip=trusted_matrix_ready,
            blocked_or_quarantined=not trusted_matrix_ready,
            requires_explicit_operator_intent=True,
            requires_safe_destination=False,
            requires_final_confirmation=True,
            trace_references=(
                export_validation.trusted_round_trip_provenance.provenance_id,
                trusted_row.row_id,
                roundtrip_matrix.matrix_id,
            ),
        ),
        _affordance(
            affordance_kind=NCP_AFFORDANCE_MATRIX_GATES,
            label="NCP Validation and Quarantine Gates",
            state=("guardrails_active_no_actual_block" if not active_blocked_rows else "actual_chain_blocked"),
            visible=True,
            enabled=False,
            ready_for_future_execution_handoff=False,
            separately_labeled=True,
            approved_context_only=False,
            review_only=True,
            trusted_round_trip=False,
            blocked_or_quarantined=bool(active_blocked_rows),
            requires_explicit_operator_intent=False,
            requires_safe_destination=False,
            requires_final_confirmation=False,
            trace_references=(roundtrip_matrix.matrix_id,) + fail_closed_rows,
        ),
    )

    provisional = NcpOperatorControlsPlan(
        controls_id="pending",
        controls_hash="pending",
        requested_action=requested_action,
        explicit_operator_intent=explicit_operator_intent,
        final_confirmation=final_confirmation,
        destination=checked_destination,
        affordances=affordances,
        destructive_action_policy=NcpDestructiveActionPolicy(),
        retention_deletion_policy=NcpRetentionDeletionPolicy(),
        traceability=traceability,
        safety_boundary=NcpOperatorControlsSafetyBoundary(),
    )
    controls_hash = _canonical_hash(provisional._hash_material())
    return NcpOperatorControlsPlan(
        controls_id=f"ncp-operator-controls-{controls_hash[:32]}",
        controls_hash=controls_hash,
        requested_action=provisional.requested_action,
        explicit_operator_intent=provisional.explicit_operator_intent,
        final_confirmation=provisional.final_confirmation,
        destination=provisional.destination,
        affordances=provisional.affordances,
        destructive_action_policy=provisional.destructive_action_policy,
        retention_deletion_policy=provisional.retention_deletion_policy,
        traceability=provisional.traceability,
        safety_boundary=provisional.safety_boundary,
    )


def compute_ncp_operator_controls_hash(record: Mapping[str, object]) -> str:
    material = dict(record)
    material.pop("controls_id", None)
    material.pop("controls_hash", None)
    return _canonical_hash(material)


def validate_ncp_operator_controls_record(record: object) -> dict[str, object]:
    """Validate serialized controls and reject authority/readiness escalation."""

    expected_fields = {
        "contract_version", "candidate_bundle_policy_status",
        "actual_execution_supported", "requested_action",
        "explicit_operator_intent", "final_confirmation", "destination",
        "affordances", "destructive_action_policy", "retention_deletion_policy",
        "traceability", "safety_boundary", "controls_id", "controls_hash",
    }
    if not isinstance(record, dict) or set(record) != expected_fields:
        raise NcpOperatorControlsValidationError(
            "invalid_operator_controls_record", "", "control fields are not closed"
        )
    if (
        record["contract_version"] != NCP_OPERATOR_CONTROLS_CONTRACT_VERSION
        or record["candidate_bundle_policy_status"] != NCP_CANDIDATE_BUNDLE_POLICY_STATUS
        or record["actual_execution_supported"] is not False
        or record["requested_action"] not in NCP_OPERATOR_ACTIONS
        or type(record["explicit_operator_intent"]) is not bool
        or type(record["final_confirmation"]) is not bool
        or record["safety_boundary"] != NcpOperatorControlsSafetyBoundary().to_dict()
        or record["destructive_action_policy"] != NcpDestructiveActionPolicy().to_dict()
        or record["retention_deletion_policy"] != NcpRetentionDeletionPolicy().to_dict()
    ):
        raise NcpOperatorControlsValidationError(
            "unsafe_operator_controls_boundary", "", "policy or safety boundary changed"
        )
    if record["final_confirmation"] and not record["explicit_operator_intent"]:
        raise NcpOperatorControlsValidationError(
            "confirmation_without_intent", "/final_confirmation", "confirmation requires intent"
        )
    if record["requested_action"] == NCP_ACTION_NONE and (
        record["explicit_operator_intent"] or record["final_confirmation"]
    ):
        raise NcpOperatorControlsValidationError(
            "intent_without_action", "/requested_action", "explicit intent requires an action"
        )
    destination = record["destination"]
    if not isinstance(destination, dict) or set(destination) != set(
        NcpDestinationControl.__dataclass_fields__
    ):
        raise NcpOperatorControlsValidationError(
            "invalid_destination_record", "/destination", "destination fields are not closed"
        )
    destination_id = destination["destination_id"]
    try:
        expected_destination = build_ncp_destination_control(
            destination_id if isinstance(destination_id, str) else None,
            target_exists=destination["target_exists"],
            overwrite_requested=destination["overwrite_requested"],
        )
    except NcpOperatorControlsValidationError as exc:
        raise NcpOperatorControlsValidationError(
            "unsafe_destination_record", "/destination", "destination is unsafe"
        ) from exc
    if expected_destination.to_dict() != destination:
        raise NcpOperatorControlsValidationError(
            "tampered_destination_control", "/destination", "destination safety changed"
        )
    traceability = record["traceability"]
    if not isinstance(traceability, dict) or set(traceability) != set(
        NcpOperatorTraceability.__dataclass_fields__
    ):
        raise NcpOperatorControlsValidationError(
            "invalid_traceability_record", "/traceability", "traceability fields are not closed"
        )
    for field in (
        "schema_interface_hash", "schema_sha256", "import_artifact_sha256",
        "import_validation_hash", "mapping_hash", "provenance_hash",
        "candidate_import_plan_hash", "export_plan_hash", "standard_package_hash",
        "export_validation_result_hash", "standard_validation_hash",
        "trusted_round_trip_provenance_hash", "matrix_hash",
        "external_trust_assessment_hash",
    ):
        if not _is_sha256(traceability[field]):
            raise NcpOperatorControlsValidationError(
                "invalid_traceability_hash", f"/traceability/{field}", "expected SHA-256"
            )
    if (
        traceability["schema_path"] != NCP_SCHEMA_JSON_PATH
        or traceability["schema_sha256"] != NCP_SCHEMA_JSON_SHA256
        or traceability["owner_review_status"] != NCP_CANDIDATE_REVIEW_STATUS
        or traceability["external_status_policy"] != NCP_EXTERNAL_STATUS_POLICY
        or traceability["uninterpreted_fields_source_metadata_only"] is not True
        or traceability["omitted_fields_deletion_intent"] is not False
        or type(traceability["external_complete_present"]) is not bool
        or type(traceability["standard_validation_gate_passed"]) is not bool
        or type(traceability["trusted_matrix_gate_passed"]) is not bool
    ):
        raise NcpOperatorControlsValidationError(
            "unsafe_traceability_record", "/traceability", "trace policy changed"
        )
    affordances = record["affordances"]
    if not isinstance(affordances, list) or tuple(
        item.get("affordance_kind") if isinstance(item, dict) else None
        for item in affordances
    ) != NCP_AFFORDANCE_KINDS:
        raise NcpOperatorControlsValidationError(
            "invalid_operator_affordances", "/affordances", "affordances are missing or reordered"
        )
    affordance_fields = set(NcpOperatorAffordance.__dataclass_fields__)
    by_kind: dict[str, dict[str, object]] = {}
    for index, affordance in enumerate(affordances):
        location = f"/affordances/{index}"
        if not isinstance(affordance, dict) or set(affordance) != affordance_fields:
            raise NcpOperatorControlsValidationError(
                "invalid_operator_affordance", location, "affordance fields are not closed"
            )
        material = dict(affordance)
        material.pop("affordance_id")
        material.pop("affordance_hash")
        actual_hash = _canonical_hash(material)
        if (
            affordance["affordance_hash"] != actual_hash
            or affordance["affordance_id"]
            != f"ncp-operator-affordance-{actual_hash[:32]}"
            or affordance["execution_performed"] is not False
            or affordance["destination_write_performed"] is not False
            or affordance["local_approval"] is not False
            or affordance["canon_authority"] is not False
            or affordance["memory_authority"] is not False
            or affordance["promotion_authority"] is not False
            or affordance["apply_promotion_authority"] is not False
        ):
            raise NcpOperatorControlsValidationError(
                "tampered_operator_affordance", location, "affordance authority or hash changed"
            )
        by_kind[affordance["affordance_kind"]] = affordance
    standard = by_kind[NCP_AFFORDANCE_STANDARD_EXPORT]
    expected_standard_state, expected_standard_ready = _standard_state(
        requested_action=record["requested_action"],
        explicit_operator_intent=record["explicit_operator_intent"],
        final_confirmation=record["final_confirmation"],
        destination=expected_destination,
        validation_ready=traceability["standard_validation_gate_passed"],
        trusted_matrix_ready=traceability["trusted_matrix_gate_passed"],
    )
    expected_standard_ready = (
        record["requested_action"] == NCP_ACTION_STANDARD_EXPORT
        and record["explicit_operator_intent"] is True
        and record["final_confirmation"] is True
        and destination["safe_destination_ready"] is True
        and traceability["standard_validation_gate_passed"] is True
        and traceability["trusted_matrix_gate_passed"] is True
        and not traceability["active_blocked_matrix_row_ids"]
    )
    candidate_bundle = by_kind[NCP_AFFORDANCE_CANDIDATE_BUNDLE]
    external_import = by_kind[NCP_AFFORDANCE_EXTERNAL_IMPORT]
    trusted_round_trip = by_kind[NCP_AFFORDANCE_TRUSTED_ROUND_TRIP]
    matrix_gates = by_kind[NCP_AFFORDANCE_MATRIX_GATES]
    if (
        standard["enabled"] is not expected_standard_ready
        or standard["ready_for_future_execution_handoff"] is not expected_standard_ready
        or standard["state"] != expected_standard_state
        or standard["blocked_or_quarantined"] is not (not expected_standard_ready)
        or standard["approved_context_only"] is not True
        or standard["review_only"] is not False
        or standard["trusted_round_trip"] is not (
            traceability["standard_validation_gate_passed"]
            and traceability["trusted_matrix_gate_passed"]
        )
        or candidate_bundle["enabled"] is not False
        or candidate_bundle["ready_for_future_execution_handoff"] is not False
        or candidate_bundle["separately_labeled"] is not True
        or candidate_bundle["approved_context_only"] is not False
        or candidate_bundle["review_only"] is not True
        or candidate_bundle["trusted_round_trip"] is not False
        or external_import["ready_for_future_execution_handoff"] is not False
        or external_import["separately_labeled"] is not True
        or external_import["approved_context_only"] is not False
        or external_import["review_only"] is not True
        or external_import["trusted_round_trip"] is not False
        or trusted_round_trip["enabled"] is not traceability["trusted_matrix_gate_passed"]
        or trusted_round_trip["trusted_round_trip"] is not traceability["trusted_matrix_gate_passed"]
        or trusted_round_trip["ready_for_future_execution_handoff"] is not False
        or trusted_round_trip["approved_context_only"] is not True
        or trusted_round_trip["review_only"] is not False
        or matrix_gates["enabled"] is not False
        or matrix_gates["ready_for_future_execution_handoff"] is not False
        or matrix_gates["approved_context_only"] is not False
        or matrix_gates["review_only"] is not True
    ):
        raise NcpOperatorControlsValidationError(
            "unsafe_operator_readiness", "/affordances", "readiness or trust escalated"
        )
    actual_hash = compute_ncp_operator_controls_hash(record)
    if (
        record["controls_hash"] != actual_hash
        or record["controls_id"] != f"ncp-operator-controls-{actual_hash[:32]}"
    ):
        raise NcpOperatorControlsValidationError(
            "operator_controls_hash_mismatch", "/controls_hash", "controls are not intact"
        )
    return json.loads(json.dumps(record, ensure_ascii=False))
