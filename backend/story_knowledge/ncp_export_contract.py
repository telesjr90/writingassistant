"""Pure T010E planning contract for separated NCP export packages.

The standard package accepts only explicit owner-approved context values.  An
optional candidate-review package can be derived from a validated T010D plan,
but it is separately typed and labeled, contains references rather than story
content, and can never be merged into or mistaken for the standard export.

This slice plans immutable in-memory metadata only.  It does not assemble or
write a final NCP file, validate an export with an external schema/runtime,
establish round-trip trust, mutate project state, or transform source prose.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Mapping

from backend.story_knowledge.ncp_candidate_import_contract import (
    NCP_CANDIDATE_REVIEW_STATUS,
    NcpCandidateImportPlan,
    NcpCandidateImportValidationError,
    NcpConflictReconciliation,
    validate_ncp_candidate_import_plan_record,
)
from backend.story_knowledge.ncp_import_contract import (
    NCP_APP_MAPPING_VERSION,
    SUPPORTED_NCP_SCHEMA_VERSION,
)
from backend.story_knowledge.ncp_mapping_contract import NCP_MAPPING_CATEGORIES
from backend.story_knowledge.ncp_provenance_contract import (
    NCP_EXTERNAL_STATUS_POLICY,
    NcpExternalStatusProvenance,
    canonical_source_value_json_bytes,
)


NCP_EXPORT_CONTRACT_VERSION = "writer-assistant-ncp-export-plan.v1"
NCP_STANDARD_EXPORT_PACKAGE_KIND = "standard_ncp_approved_context_export"
NCP_STANDARD_EXPORT_LABEL = "Approved Context Standard NCP Export"
NCP_CANDIDATE_REVIEW_PACKAGE_KIND = "candidate_review_bundle"
NCP_CANDIDATE_REVIEW_LABEL = "NCP Candidate Review Bundle - Not Approved Context"
NCP_EXPORT_VALIDATION_STATE = "not_validated_t010e_deferred_to_t010f"
NCP_EXPORT_OMISSION_POLICY = "omitted_or_unmapped_is_metadata_not_deletion"


class NcpExportValidationError(ValueError):
    """Fail-closed error for unsafe or ambiguous export planning input."""

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


def _require_identifier(value: object, location: str) -> str:
    if not isinstance(value, str) or not value.strip() or "\x00" in value:
        raise NcpExportValidationError(
            "invalid_export_input", location, "identifier must be non-empty text"
        )
    return value


def _validate_json_pointer(pointer: object, location: str) -> str:
    if not isinstance(pointer, str) or not pointer.startswith("/"):
        raise NcpExportValidationError(
            "invalid_ncp_target_pointer", location, "target must be an absolute JSON pointer"
        )
    index = 0
    while index < len(pointer):
        if pointer[index] != "~":
            index += 1
            continue
        if index + 1 >= len(pointer) or pointer[index + 1] not in "01":
            raise NcpExportValidationError(
                "invalid_ncp_target_pointer", location, "target has an invalid pointer escape"
            )
        index += 2
    if pointer != "/schema_version" and not (
        pointer == "/story" or pointer.startswith("/story/")
    ):
        raise NcpExportValidationError(
            "invalid_ncp_target_pointer",
            location,
            "approved context target must be inside the supported NCP document",
        )
    return pointer


@dataclass(frozen=True)
class NcpApprovedContextExportRecord:
    """One explicit approved value eligible for the standard export plan."""

    approved_context_record_id: str
    approval_record_id: str
    category: str
    ncp_json_pointer: str
    source_value_json: str
    source_value_sha256: str
    approval_state: str = "approved"
    source_authority: str = "approved_context"
    owner_approved: bool = True
    candidate_record: bool = False
    pending_review: bool = False
    deletion_intent: bool = False

    @property
    def source_value(self) -> object:
        return json.loads(self.source_value_json)

    def to_dict(self) -> dict[str, object]:
        return {
            "approved_context_record_id": self.approved_context_record_id,
            "approval_record_id": self.approval_record_id,
            "category": self.category,
            "ncp_json_pointer": self.ncp_json_pointer,
            "source_value": self.source_value,
            "source_value_sha256": self.source_value_sha256,
            "approval_state": self.approval_state,
            "source_authority": self.source_authority,
            "owner_approved": self.owner_approved,
            "candidate_record": self.candidate_record,
            "pending_review": self.pending_review,
            "deletion_intent": self.deletion_intent,
        }


def build_ncp_approved_context_export_record(
    *,
    approved_context_record_id: str,
    approval_record_id: str,
    category: str,
    ncp_json_pointer: str,
    source_value: object,
) -> NcpApprovedContextExportRecord:
    """Create an immutable record without rewriting its approved JSON value."""

    source_value_json = canonical_source_value_json_bytes(source_value).decode("utf-8")
    return NcpApprovedContextExportRecord(
        approved_context_record_id=approved_context_record_id,
        approval_record_id=approval_record_id,
        category=category,
        ncp_json_pointer=ncp_json_pointer,
        source_value_json=source_value_json,
        source_value_sha256=hashlib.sha256(
            source_value_json.encode("utf-8")
        ).hexdigest(),
    )


@dataclass(frozen=True)
class NcpExportOmission:
    category: str
    omission_state: str
    reason: str
    deletion_intent: bool = False
    deletion_operation: bool = False
    preserves_existing_context: bool = True
    omission_policy: str = NCP_EXPORT_OMISSION_POLICY

    def to_dict(self) -> dict[str, object]:
        return {
            "category": self.category,
            "omission_state": self.omission_state,
            "reason": self.reason,
            "deletion_intent": self.deletion_intent,
            "deletion_operation": self.deletion_operation,
            "preserves_existing_context": self.preserves_existing_context,
            "omission_policy": self.omission_policy,
        }


@dataclass(frozen=True)
class NcpStandardExportSafetyBoundary:
    approved_context_only: bool = True
    candidate_records_included: bool = False
    pending_review_records_included: bool = False
    unresolved_conflicts_included: bool = False
    candidate_review_bundle_merged: bool = False
    external_status_grants_approval: bool = False
    file_write_performed: bool = False
    project_state_write_performed: bool = False
    candidate_write_performed: bool = False
    review_write_performed: bool = False
    memory_write_performed: bool = False
    canon_write_performed: bool = False
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
    validator_execution: bool = False

    def to_dict(self) -> dict[str, bool]:
        return {
            field: getattr(self, field)
            for field in self.__dataclass_fields__
        }


@dataclass(frozen=True)
class NcpStandardExportPackage:
    package_id: str
    package_hash: str
    records: tuple[NcpApprovedContextExportRecord, ...]
    omissions: tuple[NcpExportOmission, ...]
    package_kind: str = NCP_STANDARD_EXPORT_PACKAGE_KIND
    package_label: str = NCP_STANDARD_EXPORT_LABEL
    ncp_schema_version: str = SUPPORTED_NCP_SCHEMA_VERSION
    app_mapping_version: str = NCP_APP_MAPPING_VERSION
    validation_state: str = NCP_EXPORT_VALIDATION_STATE
    approved_context_only: bool = True
    candidate_source_plan_id: None = None
    candidate_review_bundle_id: None = None
    safety_boundary: NcpStandardExportSafetyBoundary = NcpStandardExportSafetyBoundary()

    def _hash_material(self) -> dict[str, object]:
        return {
            "package_kind": self.package_kind,
            "package_label": self.package_label,
            "ncp_schema_version": self.ncp_schema_version,
            "app_mapping_version": self.app_mapping_version,
            "validation_state": self.validation_state,
            "approved_context_only": self.approved_context_only,
            "candidate_source_plan_id": self.candidate_source_plan_id,
            "candidate_review_bundle_id": self.candidate_review_bundle_id,
            "records": [item.to_dict() for item in self.records],
            "omissions": [item.to_dict() for item in self.omissions],
            "safety_boundary": self.safety_boundary.to_dict(),
        }

    def to_dict(self) -> dict[str, object]:
        value = self._hash_material()
        value["package_id"] = self.package_id
        value["package_hash"] = self.package_hash
        return value


@dataclass(frozen=True)
class NcpCandidateReviewBundleRecord:
    candidate_plan_id: str
    candidate_type: str
    category: str
    source_provenance_id: str
    source_json_pointer: str
    source_value_sha256: str
    reconciliation_id: str
    review_status: str = NCP_CANDIDATE_REVIEW_STATUS
    candidate_only: bool = True
    approved_context: bool = False
    standard_export_eligible: bool = False
    local_approval: bool = False
    canon_authority: bool = False
    memory_authority: bool = False
    promotion_authority: bool = False
    apply_promotion_authority: bool = False
    deletion_intent: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "candidate_plan_id": self.candidate_plan_id,
            "candidate_type": self.candidate_type,
            "category": self.category,
            "source_provenance_id": self.source_provenance_id,
            "source_json_pointer": self.source_json_pointer,
            "source_value_sha256": self.source_value_sha256,
            "reconciliation_id": self.reconciliation_id,
            "review_status": self.review_status,
            "candidate_only": self.candidate_only,
            "approved_context": self.approved_context,
            "standard_export_eligible": self.standard_export_eligible,
            "local_approval": self.local_approval,
            "canon_authority": self.canon_authority,
            "memory_authority": self.memory_authority,
            "promotion_authority": self.promotion_authority,
            "apply_promotion_authority": self.apply_promotion_authority,
            "deletion_intent": self.deletion_intent,
        }


@dataclass(frozen=True)
class NcpCandidateReviewSourceMetadata:
    provenance_id: str
    category: str | None
    json_pointer: str
    source_value_sha256: str
    source_metadata_only: bool = True
    approved_fact: bool = False
    standard_export_eligible: bool = False
    deletion_intent: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "provenance_id": self.provenance_id,
            "category": self.category,
            "json_pointer": self.json_pointer,
            "source_value_sha256": self.source_value_sha256,
            "source_metadata_only": self.source_metadata_only,
            "approved_fact": self.approved_fact,
            "standard_export_eligible": self.standard_export_eligible,
            "deletion_intent": self.deletion_intent,
        }


@dataclass(frozen=True)
class NcpCandidateReviewBundleSafetyBoundary:
    separately_labeled: bool = True
    candidate_only: bool = True
    approved_context: bool = False
    standard_ncp_export: bool = False
    merged_into_standard_export: bool = False
    external_status_grants_approval: bool = False
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
    validator_execution: bool = False

    def to_dict(self) -> dict[str, bool]:
        return {
            field: getattr(self, field)
            for field in self.__dataclass_fields__
        }


@dataclass(frozen=True)
class NcpCandidateReviewBundle:
    package_id: str
    package_hash: str
    source_candidate_import_plan_id: str
    records: tuple[NcpCandidateReviewBundleRecord, ...]
    conflict_reconciliations: tuple[NcpConflictReconciliation, ...]
    omissions: tuple[NcpExportOmission, ...]
    uninterpreted_source_metadata: tuple[NcpCandidateReviewSourceMetadata, ...]
    external_status_metadata: tuple[NcpExternalStatusProvenance, ...]
    package_kind: str = NCP_CANDIDATE_REVIEW_PACKAGE_KIND
    package_label: str = NCP_CANDIDATE_REVIEW_LABEL
    ncp_schema_version: str = SUPPORTED_NCP_SCHEMA_VERSION
    app_mapping_version: str = NCP_APP_MAPPING_VERSION
    validation_state: str = NCP_EXPORT_VALIDATION_STATE
    approved_context: bool = False
    standard_ncp_export: bool = False
    safety_boundary: NcpCandidateReviewBundleSafetyBoundary = (
        NcpCandidateReviewBundleSafetyBoundary()
    )

    def _hash_material(self) -> dict[str, object]:
        return {
            "package_kind": self.package_kind,
            "package_label": self.package_label,
            "ncp_schema_version": self.ncp_schema_version,
            "app_mapping_version": self.app_mapping_version,
            "validation_state": self.validation_state,
            "approved_context": self.approved_context,
            "standard_ncp_export": self.standard_ncp_export,
            "source_candidate_import_plan_id": self.source_candidate_import_plan_id,
            "records": [item.to_dict() for item in self.records],
            "conflict_reconciliations": [
                item.to_dict() for item in self.conflict_reconciliations
            ],
            "omissions": [item.to_dict() for item in self.omissions],
            "uninterpreted_source_metadata": [
                item.to_dict() for item in self.uninterpreted_source_metadata
            ],
            "external_status_metadata": [
                item.to_dict() for item in self.external_status_metadata
            ],
            "safety_boundary": self.safety_boundary.to_dict(),
        }

    def to_dict(self) -> dict[str, object]:
        value = self._hash_material()
        value["package_id"] = self.package_id
        value["package_hash"] = self.package_hash
        return value


@dataclass(frozen=True)
class NcpExportPlanSafetyBoundary:
    pure_in_memory_plan: bool = True
    packages_strictly_separated: bool = True
    file_write_performed: bool = False
    project_state_write_performed: bool = False
    candidate_write_performed: bool = False
    review_write_performed: bool = False
    memory_write_performed: bool = False
    canon_write_performed: bool = False
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
    validator_execution: bool = False

    def to_dict(self) -> dict[str, bool]:
        return {
            field: getattr(self, field)
            for field in self.__dataclass_fields__
        }


@dataclass(frozen=True)
class NcpExportPlan:
    export_plan_id: str
    export_plan_hash: str
    standard_export: NcpStandardExportPackage
    candidate_review_bundle: NcpCandidateReviewBundle | None
    safety_boundary: NcpExportPlanSafetyBoundary
    contract_version: str = NCP_EXPORT_CONTRACT_VERSION
    ncp_schema_version: str = SUPPORTED_NCP_SCHEMA_VERSION
    app_mapping_version: str = NCP_APP_MAPPING_VERSION
    validation_state: str = NCP_EXPORT_VALIDATION_STATE
    packages_separately_labeled: bool = True
    candidate_bundle_merged_into_standard: bool = False

    def _hash_material(self) -> dict[str, object]:
        return {
            "contract_version": self.contract_version,
            "ncp_schema_version": self.ncp_schema_version,
            "app_mapping_version": self.app_mapping_version,
            "validation_state": self.validation_state,
            "standard_export": self.standard_export.to_dict(),
            "candidate_review_bundle": (
                self.candidate_review_bundle.to_dict()
                if self.candidate_review_bundle is not None
                else None
            ),
            "packages_separately_labeled": self.packages_separately_labeled,
            "candidate_bundle_merged_into_standard": (
                self.candidate_bundle_merged_into_standard
            ),
            "safety_boundary": self.safety_boundary.to_dict(),
        }

    def to_dict(self) -> dict[str, object]:
        value = self._hash_material()
        value["export_plan_id"] = self.export_plan_id
        value["export_plan_hash"] = self.export_plan_hash
        return value


def compute_ncp_export_package_hash(record: Mapping[str, object]) -> str:
    material = dict(record)
    material.pop("package_id", None)
    material.pop("package_hash", None)
    return _canonical_hash(material)


def compute_ncp_export_plan_hash(record: Mapping[str, object]) -> str:
    material = dict(record)
    material.pop("export_plan_id", None)
    material.pop("export_plan_hash", None)
    return _canonical_hash(material)


def _validated_approved_records(
    records: tuple[NcpApprovedContextExportRecord, ...],
) -> tuple[NcpApprovedContextExportRecord, ...]:
    if not isinstance(records, tuple) or not records:
        raise NcpExportValidationError(
            "approved_context_required",
            "/approved_context_records",
            "standard export requires a non-empty immutable tuple of approved context",
        )
    seen_ids: set[str] = set()
    seen_pointers: set[str] = set()
    validated: list[NcpApprovedContextExportRecord] = []
    for index, record in enumerate(records):
        location = f"/approved_context_records/{index}"
        if not isinstance(record, NcpApprovedContextExportRecord):
            raise NcpExportValidationError(
                "approved_context_required",
                location,
                "candidate, pending, or untyped input is not approved context",
            )
        _require_identifier(
            record.approved_context_record_id,
            f"{location}/approved_context_record_id",
        )
        _require_identifier(record.approval_record_id, f"{location}/approval_record_id")
        pointer = _validate_json_pointer(
            record.ncp_json_pointer, f"{location}/ncp_json_pointer"
        )
        if record.category not in NCP_MAPPING_CATEGORIES:
            raise NcpExportValidationError(
                "unsupported_approved_category", f"{location}/category", "category is unsupported"
            )
        try:
            source_value = json.loads(record.source_value_json)
        except (json.JSONDecodeError, TypeError) as exc:
            raise NcpExportValidationError(
                "invalid_approved_value", f"{location}/source_value", "value is not JSON"
            ) from exc
        canonical = canonical_source_value_json_bytes(source_value).decode("utf-8")
        if canonical != record.source_value_json or record.source_value_sha256 != _canonical_hash(
            source_value
        ):
            raise NcpExportValidationError(
                "approved_value_hash_mismatch",
                f"{location}/source_value_sha256",
                "approved value is not canonical or its hash is not intact",
            )
        if (
            record.approval_state != "approved"
            or record.source_authority != "approved_context"
            or record.owner_approved is not True
            or record.candidate_record is not False
            or record.pending_review is not False
            or record.deletion_intent is not False
        ):
            raise NcpExportValidationError(
                "unapproved_standard_export_input",
                location,
                "standard export accepts approved context only",
            )
        if record.approved_context_record_id in seen_ids or pointer in seen_pointers:
            raise NcpExportValidationError(
                "ambiguous_approved_context",
                location,
                "record identity and target pointer must be unique",
            )
        seen_ids.add(record.approved_context_record_id)
        seen_pointers.add(pointer)
        validated.append(record)
    return tuple(
        sorted(
            validated,
            key=lambda item: (
                NCP_MAPPING_CATEGORIES.index(item.category),
                item.ncp_json_pointer,
                item.approved_context_record_id,
            ),
        )
    )


def _omissions_for_approved_records(
    records: tuple[NcpApprovedContextExportRecord, ...],
) -> tuple[NcpExportOmission, ...]:
    represented = {record.category for record in records}
    return tuple(
        NcpExportOmission(
            category=category,
            omission_state="omitted",
            reason="no_explicit_approved_context_record",
        )
        for category in NCP_MAPPING_CATEGORIES
        if category not in represented
    )


def _build_standard_package(
    records: tuple[NcpApprovedContextExportRecord, ...],
) -> NcpStandardExportPackage:
    omissions = _omissions_for_approved_records(records)
    provisional = NcpStandardExportPackage(
        package_id="pending",
        package_hash="pending",
        records=records,
        omissions=omissions,
    )
    package_hash = compute_ncp_export_package_hash(provisional._hash_material())
    return NcpStandardExportPackage(
        package_id=f"ncp-standard-export-{package_hash[:32]}",
        package_hash=package_hash,
        records=provisional.records,
        omissions=provisional.omissions,
    )


def _build_candidate_review_bundle(
    candidate_plan: NcpCandidateImportPlan,
) -> NcpCandidateReviewBundle:
    try:
        validate_ncp_candidate_import_plan_record(candidate_plan.to_dict())
    except (AttributeError, NcpCandidateImportValidationError) as exc:
        raise NcpExportValidationError(
            "invalid_candidate_review_source",
            "/candidate_import_plan",
            "candidate bundle requires an intact T010D pending-review plan",
        ) from exc
    records = tuple(
        NcpCandidateReviewBundleRecord(
            candidate_plan_id=item.candidate_plan_id,
            candidate_type=item.candidate_type,
            category=item.category,
            source_provenance_id=item.source_provenance_id,
            source_json_pointer=item.source_json_pointer,
            source_value_sha256=item.source_value_sha256,
            reconciliation_id=item.reconciliation_id,
        )
        for item in candidate_plan.candidates
    )
    omissions = tuple(
        NcpExportOmission(
            category=item.category,
            omission_state=item.source_state,
            reason=item.import_action,
        )
        for item in candidate_plan.category_dispositions
        if item.source_state in {"omitted", "present_empty"}
    )
    uninterpreted = tuple(
        NcpCandidateReviewSourceMetadata(
            provenance_id=item.provenance_id,
            category=item.category,
            json_pointer=item.json_pointer,
            source_value_sha256=item.source_value_sha256,
        )
        for item in candidate_plan.uninterpreted_source_references
    )
    conflicts = candidate_plan.conflict_reconciliations
    statuses = candidate_plan.external_statuses
    provisional = NcpCandidateReviewBundle(
        package_id="pending",
        package_hash="pending",
        source_candidate_import_plan_id=candidate_plan.plan_id,
        records=records,
        conflict_reconciliations=conflicts,
        omissions=omissions,
        uninterpreted_source_metadata=uninterpreted,
        external_status_metadata=statuses,
    )
    package_hash = compute_ncp_export_package_hash(provisional._hash_material())
    return NcpCandidateReviewBundle(
        package_id=f"ncp-candidate-review-bundle-{package_hash[:32]}",
        package_hash=package_hash,
        source_candidate_import_plan_id=provisional.source_candidate_import_plan_id,
        records=provisional.records,
        conflict_reconciliations=provisional.conflict_reconciliations,
        omissions=provisional.omissions,
        uninterpreted_source_metadata=provisional.uninterpreted_source_metadata,
        external_status_metadata=provisional.external_status_metadata,
    )


def plan_ncp_exports(
    approved_context_records: tuple[NcpApprovedContextExportRecord, ...],
    *,
    include_candidate_review_bundle: bool = False,
    candidate_import_plan: NcpCandidateImportPlan | None = None,
) -> NcpExportPlan:
    """Plan separated packages without assembling, validating, or writing NCP."""

    if type(include_candidate_review_bundle) is not bool:
        raise NcpExportValidationError(
            "invalid_candidate_bundle_request",
            "/include_candidate_review_bundle",
            "candidate bundle request must be explicit boolean",
        )
    approved = _validated_approved_records(approved_context_records)
    standard = _build_standard_package(approved)
    if include_candidate_review_bundle:
        if not isinstance(candidate_import_plan, NcpCandidateImportPlan):
            raise NcpExportValidationError(
                "candidate_review_source_required",
                "/candidate_import_plan",
                "requested candidate bundle requires a T010D plan",
            )
        candidate_bundle = _build_candidate_review_bundle(candidate_import_plan)
    else:
        if candidate_import_plan is not None:
            raise NcpExportValidationError(
                "candidate_bundle_not_requested",
                "/candidate_import_plan",
                "candidate plan cannot be silently included in standard export",
            )
        candidate_bundle = None

    provisional = NcpExportPlan(
        export_plan_id="pending",
        export_plan_hash="pending",
        standard_export=standard,
        candidate_review_bundle=candidate_bundle,
        safety_boundary=NcpExportPlanSafetyBoundary(),
    )
    plan_hash = compute_ncp_export_plan_hash(provisional._hash_material())
    return NcpExportPlan(
        export_plan_id=f"ncp-export-plan-{plan_hash[:32]}",
        export_plan_hash=plan_hash,
        standard_export=provisional.standard_export,
        candidate_review_bundle=provisional.candidate_review_bundle,
        safety_boundary=provisional.safety_boundary,
    )


def validate_ncp_export_plan_record(record: object) -> dict[str, object]:
    """Validate serialized package separation, authority, and integrity."""

    expected_fields = {
        "contract_version",
        "ncp_schema_version",
        "app_mapping_version",
        "validation_state",
        "standard_export",
        "candidate_review_bundle",
        "packages_separately_labeled",
        "candidate_bundle_merged_into_standard",
        "safety_boundary",
        "export_plan_id",
        "export_plan_hash",
    }
    if not isinstance(record, dict) or set(record) != expected_fields:
        raise NcpExportValidationError(
            "invalid_export_plan", "", "export plan fields are not closed"
        )
    if (
        record["contract_version"] != NCP_EXPORT_CONTRACT_VERSION
        or record["ncp_schema_version"] != SUPPORTED_NCP_SCHEMA_VERSION
        or record["app_mapping_version"] != NCP_APP_MAPPING_VERSION
        or record["validation_state"] != NCP_EXPORT_VALIDATION_STATE
        or record["packages_separately_labeled"] is not True
        or record["candidate_bundle_merged_into_standard"] is not False
    ):
        raise NcpExportValidationError(
            "unsupported_export_contract", "", "version, validation, or separation policy changed"
        )
    if record["safety_boundary"] != NcpExportPlanSafetyBoundary().to_dict():
        raise NcpExportValidationError(
            "weakened_export_safety_boundary",
            "/safety_boundary",
            "export planning cannot gain write, runtime, model, or prose capability",
        )

    standard = record["standard_export"]
    if not isinstance(standard, dict):
        raise NcpExportValidationError(
            "invalid_standard_export", "/standard_export", "standard package is required"
        )
    if (
        standard.get("package_kind") != NCP_STANDARD_EXPORT_PACKAGE_KIND
        or standard.get("package_label") != NCP_STANDARD_EXPORT_LABEL
        or standard.get("ncp_schema_version") != SUPPORTED_NCP_SCHEMA_VERSION
        or standard.get("app_mapping_version") != NCP_APP_MAPPING_VERSION
        or standard.get("validation_state") != NCP_EXPORT_VALIDATION_STATE
        or standard.get("approved_context_only") is not True
        or standard.get("candidate_source_plan_id") is not None
        or standard.get("candidate_review_bundle_id") is not None
        or standard.get("safety_boundary")
        != NcpStandardExportSafetyBoundary().to_dict()
    ):
        raise NcpExportValidationError(
            "unsafe_standard_export",
            "/standard_export",
            "standard package must remain approved-context-only",
        )
    standard_records = standard.get("records")
    if not isinstance(standard_records, list) or not standard_records:
        raise NcpExportValidationError(
            "invalid_standard_export", "/standard_export/records", "approved records are required"
        )
    for index, item in enumerate(standard_records):
        if (
            not isinstance(item, dict)
            or item.get("category") not in NCP_MAPPING_CATEGORIES
            or item.get("approval_state") != "approved"
            or item.get("source_authority") != "approved_context"
            or item.get("owner_approved") is not True
            or item.get("candidate_record") is not False
            or item.get("pending_review") is not False
            or item.get("deletion_intent") is not False
            or "story_fact" in str(item.get("category"))
        ):
            raise NcpExportValidationError(
                "unapproved_standard_export_input",
                f"/standard_export/records/{index}",
                "standard export contains non-approved input",
            )
        _validate_json_pointer(
            item.get("ncp_json_pointer"),
            f"/standard_export/records/{index}/ncp_json_pointer",
        )
        if (
            not _is_sha256(item.get("source_value_sha256"))
            or item.get("source_value_sha256") != _canonical_hash(item.get("source_value"))
        ):
            raise NcpExportValidationError(
                "approved_value_hash_mismatch",
                f"/standard_export/records/{index}/source_value_sha256",
                "approved standard-export value hash is not intact",
            )
    if any(
        not isinstance(item, dict)
        or item.get("deletion_intent") is not False
        or item.get("deletion_operation") is not False
        or item.get("preserves_existing_context") is not True
        or item.get("omission_policy") != NCP_EXPORT_OMISSION_POLICY
        for item in standard.get("omissions", [])
    ):
        raise NcpExportValidationError(
            "unsafe_export_omission",
            "/standard_export/omissions",
            "omission metadata cannot become deletion",
        )
    standard_hash = compute_ncp_export_package_hash(standard)
    if (
        standard.get("package_hash") != standard_hash
        or standard.get("package_id") != f"ncp-standard-export-{standard_hash[:32]}"
    ):
        raise NcpExportValidationError(
            "standard_package_hash_mismatch",
            "/standard_export/package_hash",
            "standard package is not intact",
        )

    bundle = record["candidate_review_bundle"]
    if bundle is not None:
        if not isinstance(bundle, dict):
            raise NcpExportValidationError(
                "invalid_candidate_review_bundle",
                "/candidate_review_bundle",
                "candidate bundle must be an object or null",
            )
        if (
            bundle.get("package_kind") != NCP_CANDIDATE_REVIEW_PACKAGE_KIND
            or bundle.get("package_label") != NCP_CANDIDATE_REVIEW_LABEL
            or bundle.get("ncp_schema_version") != SUPPORTED_NCP_SCHEMA_VERSION
            or bundle.get("app_mapping_version") != NCP_APP_MAPPING_VERSION
            or bundle.get("approved_context") is not False
            or bundle.get("standard_ncp_export") is not False
            or bundle.get("validation_state") != NCP_EXPORT_VALIDATION_STATE
            or bundle.get("safety_boundary")
            != NcpCandidateReviewBundleSafetyBoundary().to_dict()
        ):
            raise NcpExportValidationError(
                "unsafe_candidate_review_bundle",
                "/candidate_review_bundle",
                "candidate bundle must remain separately labeled and non-approved",
            )
        for index, item in enumerate(bundle.get("records", [])):
            if (
                not isinstance(item, dict)
                or item.get("category") not in NCP_MAPPING_CATEGORIES
                or item.get("review_status") != NCP_CANDIDATE_REVIEW_STATUS
                or item.get("candidate_only") is not True
                or item.get("approved_context") is not False
                or item.get("standard_export_eligible") is not False
                or item.get("local_approval") is not False
                or item.get("canon_authority") is not False
                or item.get("memory_authority") is not False
                or item.get("promotion_authority") is not False
                or item.get("apply_promotion_authority") is not False
                or item.get("deletion_intent") is not False
                or not _is_sha256(item.get("source_value_sha256"))
                or "story_fact" in str(item.get("candidate_type"))
            ):
                raise NcpExportValidationError(
                    "unsafe_candidate_review_record",
                    f"/candidate_review_bundle/records/{index}",
                    "candidate review record gained approval or export authority",
                )
        if any(
            not isinstance(item, dict)
            or item.get("owner_decision_status") != NCP_CANDIDATE_REVIEW_STATUS
            or item.get("automatic_resolution") is not None
            or item.get("overwrite_performed") is not False
            or item.get("existing_context_mutated") is not False
            or item.get("candidate_approved") is not False
            or item.get("deletion_intent") is not False
            for item in bundle.get("conflict_reconciliations", [])
        ):
            raise NcpExportValidationError(
                "unsafe_candidate_review_conflict",
                "/candidate_review_bundle/conflict_reconciliations",
                "review-bundle conflicts must remain pending and non-mutating",
            )
        if any(
            not isinstance(item, dict)
            or item.get("deletion_intent") is not False
            or item.get("deletion_operation") is not False
            or item.get("preserves_existing_context") is not True
            or item.get("omission_policy") != NCP_EXPORT_OMISSION_POLICY
            for item in bundle.get("omissions", [])
        ):
            raise NcpExportValidationError(
                "unsafe_export_omission",
                "/candidate_review_bundle/omissions",
                "candidate-bundle omission metadata cannot become deletion",
            )
        if any(
            not isinstance(item, dict)
            or item.get("source_metadata_only") is not True
            or item.get("approved_fact") is not False
            or item.get("standard_export_eligible") is not False
            or item.get("deletion_intent") is not False
            for item in bundle.get("uninterpreted_source_metadata", [])
        ):
            raise NcpExportValidationError(
                "unsafe_uninterpreted_export_metadata",
                "/candidate_review_bundle/uninterpreted_source_metadata",
                "uninterpreted values cannot become approved export facts",
            )
        if any(
            not isinstance(item, dict)
            or item.get("source_metadata_only") is not True
            or item.get("candidate_truth") is not False
            or item.get("local_approval") is not False
            or item.get("canon_authority") is not False
            or item.get("promotion_authority") is not False
            or item.get("apply_promotion_authority") is not False
            or item.get("deletion_intent") is not False
            or item.get("status_policy") != NCP_EXTERNAL_STATUS_POLICY
            for item in bundle.get("external_status_metadata", [])
        ):
            raise NcpExportValidationError(
                "unsafe_external_status_export_metadata",
                "/candidate_review_bundle/external_status_metadata",
                "external status cannot make a candidate approved",
            )
        bundle_hash = compute_ncp_export_package_hash(bundle)
        if (
            bundle.get("package_hash") != bundle_hash
            or bundle.get("package_id")
            != f"ncp-candidate-review-bundle-{bundle_hash[:32]}"
            or bundle.get("package_id") == standard.get("package_id")
        ):
            raise NcpExportValidationError(
                "candidate_bundle_hash_mismatch",
                "/candidate_review_bundle/package_hash",
                "candidate bundle identity is invalid or overlaps standard export",
            )

    plan_hash = compute_ncp_export_plan_hash(record)
    if (
        record["export_plan_hash"] != plan_hash
        or record["export_plan_id"] != f"ncp-export-plan-{plan_hash[:32]}"
    ):
        raise NcpExportValidationError(
            "export_plan_hash_mismatch",
            "/export_plan_hash",
            "export plan is not intact",
        )
    return json.loads(json.dumps(record, ensure_ascii=False))
