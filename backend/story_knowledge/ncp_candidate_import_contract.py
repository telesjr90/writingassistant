"""Pure T010D candidate-only import planning for validated NCP mappings.

This module verifies the complete T010A/T010B/T010C chain, then creates an
immutable in-memory plan.  Plan records reference source provenance rather
than copying or transforming source prose.  Existing project context is
accepted only as immutable identity/hash metadata for conflict comparison;
the planner never reads or writes project storage and never resolves a
conflict, approves a candidate, or mutates truth.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Mapping

from backend.story_knowledge.ncp_import_contract import (
    NCP_APP_MAPPING_VERSION,
    SUPPORTED_NCP_SCHEMA_VERSION,
    NcpImportValidationResult,
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
    NcpExternalStatusProvenance,
    NcpProvenanceResult,
    NcpProvenanceValidationError,
    build_ncp_source_provenance,
    canonical_source_value_json_bytes,
)


NCP_CANDIDATE_IMPORT_CONTRACT_VERSION = (
    "writer-assistant-ncp-candidate-import-plan.v1"
)
NCP_CANDIDATE_REVIEW_STATUS = "pending_owner_review"
NCP_CONFLICT_DECISION_STATUS = "pending_owner_review"
NCP_OMITTED_FIELD_IMPORT_POLICY = "omitted_or_empty_is_no_op_not_deletion"
NCP_MATCH_KEY_POLICY = "category_plus_source_id_or_json_pointer"
NCP_EXISTING_CONTEXT_AUTHORITY_SCOPES = frozenset(
    {"approved_context", "project_truth"}
)
NCP_CONFLICT_STATES = frozenset(
    {
        "no_existing_match",
        "matches_existing",
        "conflict_pending_owner_review",
        "ambiguous_existing_matches_pending_owner_review",
        "ambiguous_import_matches_pending_owner_review",
    }
)


class NcpCandidateImportValidationError(ValueError):
    """Fail-closed error for invalid candidate-only import planning input."""

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
        raise NcpCandidateImportValidationError(
            "invalid_existing_context", location, "identifier must be non-empty text"
        )
    return value


@dataclass(frozen=True)
class NcpExistingContextRecord:
    """Immutable caller-supplied fingerprint; no project value is mutated."""

    context_record_id: str
    category: str
    match_key: str
    source_value_sha256: str
    authority_scope: str

    def to_dict(self) -> dict[str, str]:
        return {
            "context_record_id": self.context_record_id,
            "category": self.category,
            "match_key": self.match_key,
            "source_value_sha256": self.source_value_sha256,
            "authority_scope": self.authority_scope,
        }


@dataclass(frozen=True)
class NcpCandidateImportRecord:
    candidate_plan_id: str
    candidate_type: str
    category: str
    app_mapping_type: str
    match_key: str
    source_mapping_record_id: str
    source_json_pointer: str
    source_value_sha256: str
    source_provenance_id: str
    field_provenance_ids: tuple[str, ...]
    preserved_uninterpreted_provenance_ids: tuple[str, ...]
    reconciliation_id: str
    review_status: str = NCP_CANDIDATE_REVIEW_STATUS
    candidate_only: bool = True
    local_approval: bool = False
    canon_authority: bool = False
    memory_authority: bool = False
    promotion_authority: bool = False
    apply_promotion_authority: bool = False
    persisted: bool = False
    deletion_intent: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "candidate_plan_id": self.candidate_plan_id,
            "candidate_type": self.candidate_type,
            "category": self.category,
            "app_mapping_type": self.app_mapping_type,
            "match_key": self.match_key,
            "source_mapping_record_id": self.source_mapping_record_id,
            "source_json_pointer": self.source_json_pointer,
            "source_value_sha256": self.source_value_sha256,
            "source_provenance_id": self.source_provenance_id,
            "field_provenance_ids": list(self.field_provenance_ids),
            "preserved_uninterpreted_provenance_ids": list(
                self.preserved_uninterpreted_provenance_ids
            ),
            "reconciliation_id": self.reconciliation_id,
            "review_status": self.review_status,
            "candidate_only": self.candidate_only,
            "local_approval": self.local_approval,
            "canon_authority": self.canon_authority,
            "memory_authority": self.memory_authority,
            "promotion_authority": self.promotion_authority,
            "apply_promotion_authority": self.apply_promotion_authority,
            "persisted": self.persisted,
            "deletion_intent": self.deletion_intent,
        }


@dataclass(frozen=True)
class NcpConflictReconciliation:
    reconciliation_id: str
    candidate_plan_id: str
    category: str
    match_key: str
    conflict_state: str
    existing_context_record_ids: tuple[str, ...]
    existing_source_value_hashes: tuple[str, ...]
    import_candidate_plan_ids_for_match: tuple[str, ...]
    owner_decision_status: str = NCP_CONFLICT_DECISION_STATUS
    automatic_resolution: None = None
    overwrite_performed: bool = False
    existing_context_mutated: bool = False
    candidate_approved: bool = False
    deletion_intent: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "reconciliation_id": self.reconciliation_id,
            "candidate_plan_id": self.candidate_plan_id,
            "category": self.category,
            "match_key": self.match_key,
            "conflict_state": self.conflict_state,
            "existing_context_record_ids": list(self.existing_context_record_ids),
            "existing_source_value_hashes": list(
                self.existing_source_value_hashes
            ),
            "import_candidate_plan_ids_for_match": list(
                self.import_candidate_plan_ids_for_match
            ),
            "owner_decision_status": self.owner_decision_status,
            "automatic_resolution": self.automatic_resolution,
            "overwrite_performed": self.overwrite_performed,
            "existing_context_mutated": self.existing_context_mutated,
            "candidate_approved": self.candidate_approved,
            "deletion_intent": self.deletion_intent,
        }


@dataclass(frozen=True)
class NcpCategoryImportDisposition:
    category: str
    source_state: str
    candidate_count: int
    import_action: str
    preserves_existing_context: bool = True
    deletion_intent: bool = False
    omission_policy: str = NCP_OMITTED_FIELD_IMPORT_POLICY

    def to_dict(self) -> dict[str, object]:
        return {
            "category": self.category,
            "source_state": self.source_state,
            "candidate_count": self.candidate_count,
            "import_action": self.import_action,
            "preserves_existing_context": self.preserves_existing_context,
            "deletion_intent": self.deletion_intent,
            "omission_policy": self.omission_policy,
        }


@dataclass(frozen=True)
class NcpUninterpretedSourceReference:
    provenance_id: str
    category: str | None
    json_pointer: str
    source_value_sha256: str
    preserved_as_source_metadata: bool = True
    imported_as_fact: bool = False
    candidate_created: bool = False
    deletion_intent: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "provenance_id": self.provenance_id,
            "category": self.category,
            "json_pointer": self.json_pointer,
            "source_value_sha256": self.source_value_sha256,
            "preserved_as_source_metadata": self.preserved_as_source_metadata,
            "imported_as_fact": self.imported_as_fact,
            "candidate_created": self.candidate_created,
            "deletion_intent": self.deletion_intent,
        }


@dataclass(frozen=True)
class NcpOwnerReviewHandoff:
    handoff_id: str
    candidate_plan_ids: tuple[str, ...]
    reconciliation_ids: tuple[str, ...]
    review_status: str = NCP_CANDIDATE_REVIEW_STATUS
    candidate_only: bool = True
    owner_action_required: bool = True
    owner_decision_recorded: bool = False
    approval_performed: bool = False
    promotion_performed: bool = False
    apply_promotion_performed: bool = False
    persisted: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "handoff_id": self.handoff_id,
            "candidate_plan_ids": list(self.candidate_plan_ids),
            "reconciliation_ids": list(self.reconciliation_ids),
            "review_status": self.review_status,
            "candidate_only": self.candidate_only,
            "owner_action_required": self.owner_action_required,
            "owner_decision_recorded": self.owner_decision_recorded,
            "approval_performed": self.approval_performed,
            "promotion_performed": self.promotion_performed,
            "apply_promotion_performed": self.apply_promotion_performed,
            "persisted": self.persisted,
        }


@dataclass(frozen=True)
class NcpCandidateImportSafetyBoundary:
    in_memory_plan_only: bool = True
    validated_t010a_input_required: bool = True
    verified_t010b_mapping_required: bool = True
    verified_t010c_provenance_required: bool = True
    candidate_persistence_performed: bool = False
    review_write_performed: bool = False
    project_state_write_performed: bool = False
    existing_context_mutation_performed: bool = False
    approval_performed: bool = False
    promotion_performed: bool = False
    apply_promotion_performed: bool = False
    memory_write_performed: bool = False
    canon_write_performed: bool = False
    generated_prose: bool = False
    prose_transformation: bool = False
    live_ncp_execution: bool = False
    node_execution: bool = False
    npm_execution: bool = False
    subprocess_execution: bool = False
    network_execution: bool = False
    model_execution: bool = False
    validator_execution: bool = False
    diagnostic_state_settled: bool = False

    def to_dict(self) -> dict[str, bool]:
        return {
            field: getattr(self, field)
            for field in self.__dataclass_fields__
        }


@dataclass(frozen=True)
class NcpCandidateImportPlan:
    plan_id: str
    plan_hash: str
    source_validation_id: str
    source_mapping_id: str
    source_provenance_id: str
    source_artifact_id: str
    story_id: str
    existing_context_records: tuple[NcpExistingContextRecord, ...]
    candidates: tuple[NcpCandidateImportRecord, ...]
    conflict_reconciliations: tuple[NcpConflictReconciliation, ...]
    category_dispositions: tuple[NcpCategoryImportDisposition, ...]
    uninterpreted_source_references: tuple[NcpUninterpretedSourceReference, ...]
    external_statuses: tuple[NcpExternalStatusProvenance, ...]
    owner_review_handoff: NcpOwnerReviewHandoff
    safety_boundary: NcpCandidateImportSafetyBoundary
    contract_version: str = NCP_CANDIDATE_IMPORT_CONTRACT_VERSION
    ncp_schema_version: str = SUPPORTED_NCP_SCHEMA_VERSION
    app_mapping_version: str = NCP_APP_MAPPING_VERSION
    match_key_policy: str = NCP_MATCH_KEY_POLICY
    omitted_field_policy: str = NCP_OMITTED_FIELD_IMPORT_POLICY
    external_status_policy: str = NCP_EXTERNAL_STATUS_POLICY

    def _hash_material(self) -> dict[str, object]:
        return {
            "contract_version": self.contract_version,
            "ncp_schema_version": self.ncp_schema_version,
            "app_mapping_version": self.app_mapping_version,
            "source_validation_id": self.source_validation_id,
            "source_mapping_id": self.source_mapping_id,
            "source_provenance_id": self.source_provenance_id,
            "source_artifact_id": self.source_artifact_id,
            "story_id": self.story_id,
            "existing_context_records": [
                item.to_dict() for item in self.existing_context_records
            ],
            "candidates": [item.to_dict() for item in self.candidates],
            "conflict_reconciliations": [
                item.to_dict() for item in self.conflict_reconciliations
            ],
            "category_dispositions": [
                item.to_dict() for item in self.category_dispositions
            ],
            "uninterpreted_source_references": [
                item.to_dict() for item in self.uninterpreted_source_references
            ],
            "external_statuses": [item.to_dict() for item in self.external_statuses],
            "owner_review_handoff": self.owner_review_handoff.to_dict(),
            "match_key_policy": self.match_key_policy,
            "omitted_field_policy": self.omitted_field_policy,
            "external_status_policy": self.external_status_policy,
            "safety_boundary": self.safety_boundary.to_dict(),
        }

    def to_dict(self) -> dict[str, object]:
        value = self._hash_material()
        value["plan_id"] = self.plan_id
        value["plan_hash"] = self.plan_hash
        return value


def compute_ncp_candidate_import_plan_hash(record: Mapping[str, object]) -> str:
    """Compute the deterministic hash for a serialized candidate import plan."""

    material = dict(record)
    material.pop("plan_id", None)
    material.pop("plan_hash", None)
    return _canonical_hash(material)


def _validated_existing_context(
    records: tuple[NcpExistingContextRecord, ...],
) -> tuple[NcpExistingContextRecord, ...]:
    if not isinstance(records, tuple):
        raise NcpCandidateImportValidationError(
            "invalid_existing_context",
            "/existing_context_records",
            "existing context fingerprints must be supplied as an immutable tuple",
        )
    seen_ids: set[str] = set()
    validated: list[NcpExistingContextRecord] = []
    for index, item in enumerate(records):
        location = f"/existing_context_records/{index}"
        if not isinstance(item, NcpExistingContextRecord):
            raise NcpCandidateImportValidationError(
                "invalid_existing_context", location, "record type is not supported"
            )
        _require_identifier(item.context_record_id, f"{location}/context_record_id")
        _require_identifier(item.match_key, f"{location}/match_key")
        if item.context_record_id in seen_ids:
            raise NcpCandidateImportValidationError(
                "ambiguous_existing_context",
                f"{location}/context_record_id",
                "context record identity is duplicated",
            )
        if item.category not in NCP_MAPPING_CATEGORIES:
            raise NcpCandidateImportValidationError(
                "invalid_existing_context", f"{location}/category", "category is unsupported"
            )
        if not _is_sha256(item.source_value_sha256):
            raise NcpCandidateImportValidationError(
                "invalid_existing_context",
                f"{location}/source_value_sha256",
                "source value hash must be lowercase SHA-256",
            )
        if item.authority_scope not in NCP_EXISTING_CONTEXT_AUTHORITY_SCOPES:
            raise NcpCandidateImportValidationError(
                "invalid_existing_context",
                f"{location}/authority_scope",
                "authority scope must be approved_context or project_truth",
            )
        seen_ids.add(item.context_record_id)
        validated.append(item)
    return tuple(
        sorted(
            validated,
            key=lambda item: (item.category, item.match_key, item.context_record_id),
        )
    )


def _candidate_match_key(source_value: object, json_pointer: str) -> str:
    if isinstance(source_value, dict):
        identifier = source_value.get("id")
        if isinstance(identifier, str) and identifier.strip() and "\x00" not in identifier:
            return f"id:{identifier}"
    return f"pointer:{json_pointer}"


def _reconciliation_state(
    candidate: NcpCandidateImportRecord,
    same_import_candidates: tuple[NcpCandidateImportRecord, ...],
    existing_matches: tuple[NcpExistingContextRecord, ...],
) -> str:
    if len(same_import_candidates) > 1:
        return "ambiguous_import_matches_pending_owner_review"
    if not existing_matches:
        return "no_existing_match"
    existing_hashes = {item.source_value_sha256 for item in existing_matches}
    if len(existing_matches) > 1:
        return "ambiguous_existing_matches_pending_owner_review"
    if existing_hashes == {candidate.source_value_sha256}:
        return "matches_existing"
    return "conflict_pending_owner_review"


def build_ncp_candidate_import_plan(
    validated_import: NcpImportValidationResult,
    mapping: NcpStructuralMappingResult,
    provenance: NcpProvenanceResult,
    *,
    existing_context_records: tuple[NcpExistingContextRecord, ...] = (),
) -> NcpCandidateImportPlan:
    """Create a deterministic pending-review plan without persisting anything."""

    if not isinstance(validated_import, NcpImportValidationResult):
        raise NcpCandidateImportValidationError(
            "validated_t010a_result_required", "", "T010A validation is required"
        )
    if not isinstance(mapping, NcpStructuralMappingResult):
        raise NcpCandidateImportValidationError(
            "verified_t010b_mapping_required", "", "T010B mapping is required"
        )
    if not isinstance(provenance, NcpProvenanceResult):
        raise NcpCandidateImportValidationError(
            "verified_t010c_provenance_required", "", "T010C provenance is required"
        )
    try:
        expected_mapping = map_validated_ncp_import(validated_import)
        if expected_mapping != mapping:
            raise NcpCandidateImportValidationError(
                "t010b_mapping_mismatch", "", "mapping does not match validated source"
            )
        expected_provenance = build_ncp_source_provenance(validated_import, mapping)
        if expected_provenance != provenance:
            raise NcpCandidateImportValidationError(
                "t010c_provenance_mismatch",
                "",
                "provenance does not match validated source and mapping",
            )
    except (NcpMappingValidationError, NcpProvenanceValidationError) as exc:
        raise NcpCandidateImportValidationError(
            "source_chain_revalidation_failed",
            "",
            "T010A/T010B/T010C source chain no longer validates",
        ) from exc

    existing = _validated_existing_context(existing_context_records)
    mapped_provenance: dict[str, list[object]] = {}
    for item in provenance.records:
        if item.mapping_record_id is not None:
            mapped_provenance.setdefault(item.mapping_record_id, []).append(item)

    candidates: list[NcpCandidateImportRecord] = []
    for mapped_record in mapping.records:
        related = mapped_provenance.get(mapped_record.mapping_record_id, [])
        record_provenance = [
            item for item in related if item.provenance_kind == "mapped_record"
        ]
        if len(record_provenance) != 1:
            raise NcpCandidateImportValidationError(
                "incomplete_t010c_provenance",
                mapped_record.mapping_record_id,
                "each mapping record must have exactly one source provenance record",
            )
        source = record_provenance[0]
        match_key = _candidate_match_key(
            mapped_record.source_value, source.json_pointer
        )
        candidate_material = {
            "contract_version": NCP_CANDIDATE_IMPORT_CONTRACT_VERSION,
            "source_artifact_id": provenance.source_artifact_id,
            "source_mapping_record_id": mapped_record.mapping_record_id,
            "source_provenance_id": source.provenance_id,
        }
        candidate_digest = _canonical_hash(candidate_material)
        candidate_plan_id = f"ncp-candidate-plan-{candidate_digest[:32]}"
        reconciliation_digest = _canonical_hash(
            {"candidate_plan_id": candidate_plan_id, "match_key": match_key}
        )
        candidates.append(
            NcpCandidateImportRecord(
                candidate_plan_id=candidate_plan_id,
                candidate_type=f"ncp_{mapped_record.category}_import_candidate",
                category=mapped_record.category,
                app_mapping_type=mapped_record.app_mapping_type,
                match_key=match_key,
                source_mapping_record_id=mapped_record.mapping_record_id,
                source_json_pointer=source.json_pointer,
                source_value_sha256=source.source_value_sha256,
                source_provenance_id=source.provenance_id,
                field_provenance_ids=tuple(
                    sorted(
                        item.provenance_id
                        for item in related
                        if item.provenance_kind == "mapped_field"
                    )
                ),
                preserved_uninterpreted_provenance_ids=tuple(
                    sorted(
                        item.provenance_id
                        for item in related
                        if item.provenance_kind == "preserved_uninterpreted_field"
                    )
                ),
                reconciliation_id=(
                    f"ncp-reconciliation-{reconciliation_digest[:32]}"
                ),
            )
        )
    candidates.sort(
        key=lambda item: (
            NCP_MAPPING_CATEGORIES.index(item.category),
            item.source_json_pointer,
            item.candidate_plan_id,
        )
    )

    candidate_groups: dict[tuple[str, str], list[NcpCandidateImportRecord]] = {}
    for candidate in candidates:
        candidate_groups.setdefault(
            (candidate.category, candidate.match_key), []
        ).append(candidate)
    existing_groups: dict[tuple[str, str], list[NcpExistingContextRecord]] = {}
    for item in existing:
        existing_groups.setdefault((item.category, item.match_key), []).append(item)

    reconciliations: list[NcpConflictReconciliation] = []
    for candidate in candidates:
        key = (candidate.category, candidate.match_key)
        same_import = tuple(candidate_groups[key])
        existing_matches = tuple(existing_groups.get(key, []))
        state = _reconciliation_state(candidate, same_import, existing_matches)
        reconciliations.append(
            NcpConflictReconciliation(
                reconciliation_id=candidate.reconciliation_id,
                candidate_plan_id=candidate.candidate_plan_id,
                category=candidate.category,
                match_key=candidate.match_key,
                conflict_state=state,
                existing_context_record_ids=tuple(
                    item.context_record_id for item in existing_matches
                ),
                existing_source_value_hashes=tuple(
                    item.source_value_sha256 for item in existing_matches
                ),
                import_candidate_plan_ids_for_match=tuple(
                    item.candidate_plan_id for item in same_import
                ),
            )
        )

    candidate_counts = {
        category: sum(candidate.category == category for candidate in candidates)
        for category in NCP_MAPPING_CATEGORIES
    }
    state_by_category = {state.category: state for state in mapping.category_states}
    dispositions: list[NcpCategoryImportDisposition] = []
    for category in NCP_MAPPING_CATEGORIES:
        state = state_by_category[category]
        action = {
            "mapped": "plan_candidates",
            "present_empty": "no_op_empty",
            "omitted": "no_op_omitted",
        }[state.state]
        dispositions.append(
            NcpCategoryImportDisposition(
                category=category,
                source_state=state.state,
                candidate_count=candidate_counts[category],
                import_action=action,
            )
        )

    uninterpreted = tuple(
        NcpUninterpretedSourceReference(
            provenance_id=item.provenance_id,
            category=item.category,
            json_pointer=item.json_pointer,
            source_value_sha256=item.source_value_sha256,
        )
        for item in provenance.records
        if item.provenance_kind.startswith("preserved_uninterpreted")
    )
    candidate_ids = tuple(item.candidate_plan_id for item in candidates)
    reconciliation_ids = tuple(
        item.reconciliation_id for item in reconciliations
    )
    handoff_digest = _canonical_hash(
        {
            "source_provenance_id": provenance.provenance_id,
            "candidate_plan_ids": list(candidate_ids),
            "reconciliation_ids": list(reconciliation_ids),
        }
    )
    handoff = NcpOwnerReviewHandoff(
        handoff_id=f"ncp-owner-review-handoff-{handoff_digest[:32]}",
        candidate_plan_ids=candidate_ids,
        reconciliation_ids=reconciliation_ids,
    )
    provisional = NcpCandidateImportPlan(
        plan_id="pending",
        plan_hash="pending",
        source_validation_id=validated_import.validation_id,
        source_mapping_id=mapping.mapping_id,
        source_provenance_id=provenance.provenance_id,
        source_artifact_id=validated_import.artifact.artifact_id,
        story_id=validated_import.story_id,
        existing_context_records=existing,
        candidates=tuple(candidates),
        conflict_reconciliations=tuple(reconciliations),
        category_dispositions=tuple(dispositions),
        uninterpreted_source_references=uninterpreted,
        external_statuses=provenance.external_statuses,
        owner_review_handoff=handoff,
        safety_boundary=NcpCandidateImportSafetyBoundary(),
    )
    plan_hash = compute_ncp_candidate_import_plan_hash(provisional._hash_material())
    return NcpCandidateImportPlan(
        plan_id=f"ncp-candidate-import-plan-{plan_hash[:32]}",
        plan_hash=plan_hash,
        source_validation_id=provisional.source_validation_id,
        source_mapping_id=provisional.source_mapping_id,
        source_provenance_id=provisional.source_provenance_id,
        source_artifact_id=provisional.source_artifact_id,
        story_id=provisional.story_id,
        existing_context_records=provisional.existing_context_records,
        candidates=provisional.candidates,
        conflict_reconciliations=provisional.conflict_reconciliations,
        category_dispositions=provisional.category_dispositions,
        uninterpreted_source_references=provisional.uninterpreted_source_references,
        external_statuses=provisional.external_statuses,
        owner_review_handoff=provisional.owner_review_handoff,
        safety_boundary=provisional.safety_boundary,
    )


def validate_ncp_candidate_import_plan_record(
    record: object,
) -> dict[str, object]:
    """Validate a serialized plan and reject weakened safety/review state."""

    expected_fields = {
        "contract_version",
        "ncp_schema_version",
        "app_mapping_version",
        "source_validation_id",
        "source_mapping_id",
        "source_provenance_id",
        "source_artifact_id",
        "story_id",
        "existing_context_records",
        "candidates",
        "conflict_reconciliations",
        "category_dispositions",
        "uninterpreted_source_references",
        "external_statuses",
        "owner_review_handoff",
        "match_key_policy",
        "omitted_field_policy",
        "external_status_policy",
        "safety_boundary",
        "plan_id",
        "plan_hash",
    }
    if not isinstance(record, dict) or set(record) != expected_fields:
        raise NcpCandidateImportValidationError(
            "invalid_plan_record", "", "plan fields are not closed"
        )
    if (
        record["contract_version"] != NCP_CANDIDATE_IMPORT_CONTRACT_VERSION
        or record["ncp_schema_version"] != SUPPORTED_NCP_SCHEMA_VERSION
        or record["app_mapping_version"] != NCP_APP_MAPPING_VERSION
        or record["match_key_policy"] != NCP_MATCH_KEY_POLICY
        or record["omitted_field_policy"] != NCP_OMITTED_FIELD_IMPORT_POLICY
        or record["external_status_policy"] != NCP_EXTERNAL_STATUS_POLICY
    ):
        raise NcpCandidateImportValidationError(
            "unsupported_plan_contract", "", "plan version or policy is unsupported"
        )
    if record["safety_boundary"] != NcpCandidateImportSafetyBoundary().to_dict():
        raise NcpCandidateImportValidationError(
            "weakened_safety_boundary",
            "/safety_boundary",
            "candidate import plan cannot gain write, authority, runtime, or prose capability",
        )

    candidates = record["candidates"]
    if not isinstance(candidates, list) or not candidates:
        raise NcpCandidateImportValidationError(
            "invalid_candidate_plan", "/candidates", "candidate plan must be non-empty"
        )
    candidate_ids: list[str] = []
    for index, candidate in enumerate(candidates):
        location = f"/candidates/{index}"
        if not isinstance(candidate, dict):
            raise NcpCandidateImportValidationError(
                "invalid_candidate_plan", location, "candidate must be an object"
            )
        category = candidate.get("category")
        if (
            category not in NCP_MAPPING_CATEGORIES
            or candidate.get("candidate_type")
            != f"ncp_{category}_import_candidate"
            or candidate.get("review_status") != NCP_CANDIDATE_REVIEW_STATUS
            or candidate.get("candidate_only") is not True
            or candidate.get("local_approval") is not False
            or candidate.get("canon_authority") is not False
            or candidate.get("memory_authority") is not False
            or candidate.get("promotion_authority") is not False
            or candidate.get("apply_promotion_authority") is not False
            or candidate.get("persisted") is not False
            or candidate.get("deletion_intent") is not False
            or "story_fact" in str(candidate.get("candidate_type"))
        ):
            raise NcpCandidateImportValidationError(
                "unsafe_candidate_state", location, "candidate-only boundary is weakened"
            )
        candidate_id = candidate.get("candidate_plan_id")
        if not isinstance(candidate_id, str) or not _is_sha256(
            candidate.get("source_value_sha256")
        ):
            raise NcpCandidateImportValidationError(
                "invalid_candidate_plan", location, "candidate identity or hash is invalid"
            )
        candidate_ids.append(candidate_id)

    conflicts = record["conflict_reconciliations"]
    if not isinstance(conflicts, list) or len(conflicts) != len(candidates):
        raise NcpCandidateImportValidationError(
            "invalid_reconciliation_plan",
            "/conflict_reconciliations",
            "every candidate requires reconciliation metadata",
        )
    reconciliation_ids: list[str] = []
    for index, conflict in enumerate(conflicts):
        location = f"/conflict_reconciliations/{index}"
        if (
            not isinstance(conflict, dict)
            or conflict.get("conflict_state") not in NCP_CONFLICT_STATES
            or conflict.get("owner_decision_status")
            != NCP_CONFLICT_DECISION_STATUS
            or conflict.get("automatic_resolution") is not None
            or conflict.get("overwrite_performed") is not False
            or conflict.get("existing_context_mutated") is not False
            or conflict.get("candidate_approved") is not False
            or conflict.get("deletion_intent") is not False
        ):
            raise NcpCandidateImportValidationError(
                "unsafe_reconciliation_state",
                location,
                "conflict reconciliation must remain pending and non-mutating",
            )
        reconciliation_id = conflict.get("reconciliation_id")
        if not isinstance(reconciliation_id, str):
            raise NcpCandidateImportValidationError(
                "invalid_reconciliation_plan", location, "reconciliation ID is invalid"
            )
        reconciliation_ids.append(reconciliation_id)

    dispositions = record["category_dispositions"]
    if not isinstance(dispositions, list) or len(dispositions) != len(
        NCP_MAPPING_CATEGORIES
    ):
        raise NcpCandidateImportValidationError(
            "invalid_category_dispositions",
            "/category_dispositions",
            "every mapping category requires an import disposition",
        )
    for index, disposition in enumerate(dispositions):
        if (
            not isinstance(disposition, dict)
            or disposition.get("category") != NCP_MAPPING_CATEGORIES[index]
            or disposition.get("import_action")
            not in {"plan_candidates", "no_op_empty", "no_op_omitted"}
            or disposition.get("preserves_existing_context") is not True
            or disposition.get("deletion_intent") is not False
            or disposition.get("omission_policy")
            != NCP_OMITTED_FIELD_IMPORT_POLICY
        ):
            raise NcpCandidateImportValidationError(
                "unsafe_category_disposition",
                f"/category_dispositions/{index}",
                "omission or empty state cannot imply deletion",
            )

    uninterpreted = record["uninterpreted_source_references"]
    if not isinstance(uninterpreted, list) or any(
        not isinstance(item, dict)
        or item.get("preserved_as_source_metadata") is not True
        or item.get("imported_as_fact") is not False
        or item.get("candidate_created") is not False
        or item.get("deletion_intent") is not False
        for item in uninterpreted
    ):
        raise NcpCandidateImportValidationError(
            "unsafe_uninterpreted_source_state",
            "/uninterpreted_source_references",
            "unknown source values must remain uninterpreted metadata",
        )

    statuses = record["external_statuses"]
    if not isinstance(statuses, list) or any(
        not isinstance(item, dict)
        or item.get("source_metadata_only") is not True
        or item.get("candidate_truth") is not False
        or item.get("local_approval") is not False
        or item.get("canon_authority") is not False
        or item.get("promotion_authority") is not False
        or item.get("apply_promotion_authority") is not False
        or item.get("deletion_intent") is not False
        for item in statuses
    ):
        raise NcpCandidateImportValidationError(
            "unsafe_external_status_state",
            "/external_statuses",
            "external status cannot gain local authority",
        )

    handoff = record["owner_review_handoff"]
    if (
        not isinstance(handoff, dict)
        or handoff.get("candidate_plan_ids") != candidate_ids
        or handoff.get("reconciliation_ids") != reconciliation_ids
        or handoff.get("review_status") != NCP_CANDIDATE_REVIEW_STATUS
        or handoff.get("candidate_only") is not True
        or handoff.get("owner_action_required") is not True
        or handoff.get("owner_decision_recorded") is not False
        or handoff.get("approval_performed") is not False
        or handoff.get("promotion_performed") is not False
        or handoff.get("apply_promotion_performed") is not False
        or handoff.get("persisted") is not False
    ):
        raise NcpCandidateImportValidationError(
            "unsafe_owner_review_handoff",
            "/owner_review_handoff",
            "review handoff must remain pending, candidate-only, and unpersisted",
        )

    actual_hash = compute_ncp_candidate_import_plan_hash(record)
    if (
        record["plan_hash"] != actual_hash
        or record["plan_id"] != f"ncp-candidate-import-plan-{actual_hash[:32]}"
    ):
        raise NcpCandidateImportValidationError(
            "plan_hash_mismatch", "/plan_hash", "candidate import plan is not intact"
        )
    return json.loads(json.dumps(record, ensure_ascii=False))
