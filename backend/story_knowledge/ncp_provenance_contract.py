"""Pure T010C provenance contract for validated, mapped NCP source values.

The builder accepts the successful T010A validation result together with its
deterministic T010B mapping result.  It revalidates both, resolves every source
path against the original JSON artifact, and emits immutable RFC 6901 JSON
pointers plus SHA-256 hashes of canonical JSON source values.

This module does not construct or persist candidates, interpret external
status as local authority, mutate project state, call runtimes, or transform
source prose.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Mapping

from backend.story_knowledge.ncp_import_contract import (
    NCP_APP_MAPPING_VERSION,
    NCP_UNKNOWN_FIELD_POLICY,
    SUPPORTED_NCP_SCHEMA_VERSION,
    NcpImportValidationResult,
)
from backend.story_knowledge.ncp_mapping_contract import (
    NCP_MAPPING_CATEGORIES,
    NCP_OMISSION_POLICY,
    NcpMappingCategoryState,
    NcpMappingValidationError,
    NcpStructuralMappingResult,
    map_validated_ncp_import,
)


NCP_PROVENANCE_CONTRACT_VERSION = "writer-assistant-ncp-source-provenance.v1"
NCP_SOURCE_VALUE_HASH_ALGORITHM = "sha256"
NCP_SOURCE_VALUE_CANONICALIZATION = "utf8-json-sort-keys-no-whitespace-v1"
NCP_EXTERNAL_STATUS_POLICY = "source_metadata_only_no_local_authority"


class NcpProvenanceValidationError(ValueError):
    """Fail-closed error for invalid T010C provenance input."""

    def __init__(self, code: str, json_pointer: str, detail: str) -> None:
        self.code = code
        self.json_pointer = json_pointer
        self.detail = detail
        super().__init__(f"{code} at {json_pointer or '/'}: {detail}")


def canonical_source_value_json_bytes(value: object) -> bytes:
    """Return deterministic JSON bytes used only for source-value hashing."""

    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    except (TypeError, ValueError, RecursionError) as exc:
        raise NcpProvenanceValidationError(
            "non_canonical_source_value",
            "",
            "source value cannot be represented as bounded canonical JSON",
        ) from exc


def source_value_sha256(value: object) -> str:
    """Hash an exact JSON source value without normalizing its prose."""

    return hashlib.sha256(canonical_source_value_json_bytes(value)).hexdigest()


def _escape_json_pointer_segment(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")


def json_pointer_from_path(path: tuple[str | int, ...]) -> str:
    """Render an RFC 6901 pointer for a path in the original NCP JSON."""

    if not path:
        return ""
    return "/" + "/".join(
        _escape_json_pointer_segment(str(segment)) for segment in path
    )


def _path_from_json_pointer(pointer: str) -> tuple[str, ...]:
    if pointer == "":
        return ()
    if not pointer.startswith("/"):
        raise NcpProvenanceValidationError(
            "invalid_json_pointer", pointer, "JSON pointer must be absolute"
        )
    path: list[str] = []
    for raw_segment in pointer[1:].split("/"):
        segment = ""
        index = 0
        while index < len(raw_segment):
            character = raw_segment[index]
            if character != "~":
                segment += character
                index += 1
                continue
            if index + 1 >= len(raw_segment) or raw_segment[index + 1] not in "01":
                raise NcpProvenanceValidationError(
                    "invalid_json_pointer", pointer, "JSON pointer escape is invalid"
                )
            segment += "~" if raw_segment[index + 1] == "0" else "/"
            index += 2
        path.append(segment)
    return tuple(path)


def _resolve_path(document: object, path: tuple[str | int, ...]) -> object:
    current = document
    for segment in path:
        pointer = json_pointer_from_path(path)
        if isinstance(current, dict) and isinstance(segment, str):
            if segment not in current:
                raise NcpProvenanceValidationError(
                    "source_path_not_found", pointer, "mapping path is absent from source"
                )
            current = current[segment]
        elif isinstance(current, list) and isinstance(segment, int):
            if segment < 0 or segment >= len(current):
                raise NcpProvenanceValidationError(
                    "source_path_not_found", pointer, "mapping index is outside source"
                )
            current = current[segment]
        else:
            raise NcpProvenanceValidationError(
                "source_path_shape_mismatch",
                pointer,
                "mapping path does not match the original JSON shape",
            )
    return current


def _resolve_pointer(document: object, pointer: str) -> object:
    path: list[str | int] = []
    current = document
    for segment in _path_from_json_pointer(pointer):
        if isinstance(current, list):
            if not segment.isdigit():
                raise NcpProvenanceValidationError(
                    "source_path_shape_mismatch", pointer, "array pointer segment is not an index"
                )
            typed_segment: str | int = int(segment)
        else:
            typed_segment = segment
        path.append(typed_segment)
        current = _resolve_path(document, tuple(path))
    return current


@dataclass(frozen=True)
class NcpSourceValueProvenance:
    provenance_id: str
    provenance_kind: str
    category: str | None
    app_mapping_type: str | None
    mapping_record_id: str | None
    field_name: str | None
    json_pointer: str
    source_value_sha256: str
    source_artifact_id: str
    source_validation_id: str
    source_mapping_id: str
    interpreted_by_mapping: bool
    source_metadata_only: bool
    candidate_truth: bool = False
    local_approval: bool = False
    canon_authority: bool = False
    deletion_intent: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "provenance_id": self.provenance_id,
            "provenance_kind": self.provenance_kind,
            "category": self.category,
            "app_mapping_type": self.app_mapping_type,
            "mapping_record_id": self.mapping_record_id,
            "field_name": self.field_name,
            "json_pointer": self.json_pointer,
            "source_value_sha256": self.source_value_sha256,
            "hash_algorithm": NCP_SOURCE_VALUE_HASH_ALGORITHM,
            "canonicalization": NCP_SOURCE_VALUE_CANONICALIZATION,
            "source_artifact_id": self.source_artifact_id,
            "source_validation_id": self.source_validation_id,
            "source_mapping_id": self.source_mapping_id,
            "interpreted_by_mapping": self.interpreted_by_mapping,
            "source_metadata_only": self.source_metadata_only,
            "candidate_truth": self.candidate_truth,
            "local_approval": self.local_approval,
            "canon_authority": self.canon_authority,
            "deletion_intent": self.deletion_intent,
        }


@dataclass(frozen=True)
class NcpExternalStatusProvenance:
    narrative_id: str
    json_pointer: str
    external_status: str | None
    status_present: bool
    source_value_sha256: str | None
    source_metadata_only: bool = True
    candidate_truth: bool = False
    local_approval: bool = False
    canon_authority: bool = False
    promotion_authority: bool = False
    apply_promotion_authority: bool = False
    deletion_intent: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "narrative_id": self.narrative_id,
            "json_pointer": self.json_pointer,
            "external_status": self.external_status,
            "status_present": self.status_present,
            "source_value_sha256": self.source_value_sha256,
            "hash_algorithm": (
                NCP_SOURCE_VALUE_HASH_ALGORITHM if self.status_present else None
            ),
            "canonicalization": (
                NCP_SOURCE_VALUE_CANONICALIZATION if self.status_present else None
            ),
            "status_policy": NCP_EXTERNAL_STATUS_POLICY,
            "source_metadata_only": self.source_metadata_only,
            "candidate_truth": self.candidate_truth,
            "local_approval": self.local_approval,
            "canon_authority": self.canon_authority,
            "promotion_authority": self.promotion_authority,
            "apply_promotion_authority": self.apply_promotion_authority,
            "deletion_intent": self.deletion_intent,
        }


@dataclass(frozen=True)
class NcpProvenanceSafetyBoundary:
    in_memory_only: bool = True
    validated_t010a_input_required: bool = True
    verified_t010b_mapping_required: bool = True
    candidate_construction_performed: bool = False
    candidate_write_performed: bool = False
    review_write_performed: bool = False
    project_state_write_performed: bool = False
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
    diagnostic_state_settled: bool = False

    def to_dict(self) -> dict[str, bool]:
        return {
            field: getattr(self, field)
            for field in self.__dataclass_fields__
        }


@dataclass(frozen=True)
class NcpProvenanceResult:
    provenance_id: str
    provenance_hash: str
    source_validation_id: str
    source_validation_hash: str
    source_mapping_id: str
    source_mapping_hash: str
    source_artifact_id: str
    story_id: str
    records: tuple[NcpSourceValueProvenance, ...]
    external_statuses: tuple[NcpExternalStatusProvenance, ...]
    category_states: tuple[NcpMappingCategoryState, ...]
    preserved_uninterpreted_top_level_pointers: tuple[str, ...]
    safety_boundary: NcpProvenanceSafetyBoundary
    contract_version: str = NCP_PROVENANCE_CONTRACT_VERSION
    ncp_schema_version: str = SUPPORTED_NCP_SCHEMA_VERSION
    app_mapping_version: str = NCP_APP_MAPPING_VERSION
    unknown_field_policy: str = NCP_UNKNOWN_FIELD_POLICY
    omission_policy: str = NCP_OMISSION_POLICY
    external_status_policy: str = NCP_EXTERNAL_STATUS_POLICY

    def _hash_material(self) -> dict[str, object]:
        return {
            "contract_version": self.contract_version,
            "ncp_schema_version": self.ncp_schema_version,
            "app_mapping_version": self.app_mapping_version,
            "source_validation_id": self.source_validation_id,
            "source_validation_hash": self.source_validation_hash,
            "source_mapping_id": self.source_mapping_id,
            "source_mapping_hash": self.source_mapping_hash,
            "source_artifact_id": self.source_artifact_id,
            "story_id": self.story_id,
            "records": [record.to_dict() for record in self.records],
            "external_statuses": [item.to_dict() for item in self.external_statuses],
            "category_states": [state.to_dict() for state in self.category_states],
            "preserved_uninterpreted_top_level_pointers": list(
                self.preserved_uninterpreted_top_level_pointers
            ),
            "unknown_field_policy": self.unknown_field_policy,
            "omission_policy": self.omission_policy,
            "external_status_policy": self.external_status_policy,
            "safety_boundary": self.safety_boundary.to_dict(),
        }

    def to_dict(self) -> dict[str, object]:
        value = self._hash_material()
        value["provenance_id"] = self.provenance_id
        value["provenance_hash"] = self.provenance_hash
        return value


def compute_ncp_provenance_hash(record: Mapping[str, object]) -> str:
    """Compute the tamper-evident hash for a serialized provenance result."""

    material = dict(record)
    material.pop("provenance_id", None)
    material.pop("provenance_hash", None)
    return hashlib.sha256(canonical_source_value_json_bytes(material)).hexdigest()


def _build_source_record(
    *,
    provenance_kind: str,
    category: str | None,
    app_mapping_type: str | None,
    mapping_record_id: str | None,
    field_name: str | None,
    path: tuple[str | int, ...],
    source_value: object,
    artifact_id: str,
    validation_id: str,
    mapping_id: str,
    interpreted_by_mapping: bool,
) -> NcpSourceValueProvenance:
    pointer = json_pointer_from_path(path)
    value_hash = source_value_sha256(source_value)
    identity = {
        "artifact_id": artifact_id,
        "mapping_id": mapping_id,
        "provenance_kind": provenance_kind,
        "json_pointer": pointer,
    }
    digest = source_value_sha256(identity)
    return NcpSourceValueProvenance(
        provenance_id=f"ncp-source-provenance-{digest[:32]}",
        provenance_kind=provenance_kind,
        category=category,
        app_mapping_type=app_mapping_type,
        mapping_record_id=mapping_record_id,
        field_name=field_name,
        json_pointer=pointer,
        source_value_sha256=value_hash,
        source_artifact_id=artifact_id,
        source_validation_id=validation_id,
        source_mapping_id=mapping_id,
        interpreted_by_mapping=interpreted_by_mapping,
        source_metadata_only=True,
    )


def build_ncp_source_provenance(
    validated_import: NcpImportValidationResult,
    mapping: NcpStructuralMappingResult,
) -> NcpProvenanceResult:
    """Build deterministic provenance only after T010A and T010B succeed."""

    if not isinstance(validated_import, NcpImportValidationResult):
        raise NcpProvenanceValidationError(
            "validated_t010a_result_required",
            "",
            "provenance accepts only a successful T010A validation result",
        )
    if not isinstance(mapping, NcpStructuralMappingResult):
        raise NcpProvenanceValidationError(
            "verified_t010b_mapping_required",
            "",
            "provenance accepts only a T010B structural mapping result",
        )
    try:
        expected_mapping = map_validated_ncp_import(validated_import)
    except NcpMappingValidationError as exc:
        raise NcpProvenanceValidationError(
            "t010a_or_t010b_revalidation_failed",
            "",
            "source artifact no longer produces a valid structural mapping",
        ) from exc
    if expected_mapping != mapping:
        raise NcpProvenanceValidationError(
            "t010b_mapping_mismatch",
            "",
            "supplied mapping does not match the validated original artifact",
        )

    parsed = json.loads(validated_import.artifact.original_text)
    records: list[NcpSourceValueProvenance] = []
    for mapped_record in mapping.records:
        source_value = _resolve_path(parsed, mapped_record.source_path)
        if source_value != mapped_record.source_value:
            raise NcpProvenanceValidationError(
                "mapped_source_value_mismatch",
                json_pointer_from_path(mapped_record.source_path),
                "mapped value does not equal the value in the original artifact",
            )
        records.append(
            _build_source_record(
                provenance_kind="mapped_record",
                category=mapped_record.category,
                app_mapping_type=mapped_record.app_mapping_type,
                mapping_record_id=mapped_record.mapping_record_id,
                field_name=None,
                path=mapped_record.source_path,
                source_value=source_value,
                artifact_id=mapping.artifact_id,
                validation_id=mapping.source_validation_id,
                mapping_id=mapping.mapping_id,
                interpreted_by_mapping=True,
            )
        )
        if isinstance(source_value, dict):
            for field_name in mapped_record.mapped_field_names:
                field_value = source_value[field_name]
                records.append(
                    _build_source_record(
                        provenance_kind="mapped_field",
                        category=mapped_record.category,
                        app_mapping_type=mapped_record.app_mapping_type,
                        mapping_record_id=mapped_record.mapping_record_id,
                        field_name=field_name,
                        path=mapped_record.source_path + (field_name,),
                        source_value=field_value,
                        artifact_id=mapping.artifact_id,
                        validation_id=mapping.source_validation_id,
                        mapping_id=mapping.mapping_id,
                        interpreted_by_mapping=True,
                    )
                )
            for field_name in mapped_record.preserved_uninterpreted_field_names:
                field_value = source_value[field_name]
                records.append(
                    _build_source_record(
                        provenance_kind="preserved_uninterpreted_field",
                        category=mapped_record.category,
                        app_mapping_type=mapped_record.app_mapping_type,
                        mapping_record_id=mapped_record.mapping_record_id,
                        field_name=field_name,
                        path=mapped_record.source_path + (field_name,),
                        source_value=field_value,
                        artifact_id=mapping.artifact_id,
                        validation_id=mapping.source_validation_id,
                        mapping_id=mapping.mapping_id,
                        interpreted_by_mapping=False,
                    )
                )

    for pointer in mapping.preserved_uninterpreted_top_level_pointers:
        value = _resolve_pointer(parsed, pointer)
        records.append(
            _build_source_record(
                provenance_kind="preserved_uninterpreted_top_level",
                category=None,
                app_mapping_type=None,
                mapping_record_id=None,
                field_name=_path_from_json_pointer(pointer)[-1],
                path=tuple(_path_from_json_pointer(pointer)),
                source_value=value,
                artifact_id=mapping.artifact_id,
                validation_id=mapping.source_validation_id,
                mapping_id=mapping.mapping_id,
                interpreted_by_mapping=False,
            )
        )

    records.sort(
        key=lambda item: (
            item.json_pointer,
            item.provenance_kind,
            item.category or "",
            item.mapping_record_id or "",
        )
    )

    statuses: list[NcpExternalStatusProvenance] = []
    for status in mapping.external_narrative_statuses:
        value_hash: str | None = None
        if status.status_present:
            source_status = _resolve_pointer(parsed, status.json_pointer)
            if source_status != status.external_status:
                raise NcpProvenanceValidationError(
                    "external_status_mismatch",
                    status.json_pointer,
                    "external status does not match the original artifact",
                )
            value_hash = source_value_sha256(source_status)
        statuses.append(
            NcpExternalStatusProvenance(
                narrative_id=status.narrative_id,
                json_pointer=status.json_pointer,
                external_status=status.external_status,
                status_present=status.status_present,
                source_value_sha256=value_hash,
            )
        )

    actual_categories = {record.category for record in mapping.records}
    if not actual_categories.issubset(NCP_MAPPING_CATEGORIES):
        raise NcpProvenanceValidationError(
            "unsupported_mapping_category",
            "",
            "mapping contains a category outside the pinned T010B contract",
        )

    provisional = NcpProvenanceResult(
        provenance_id="pending",
        provenance_hash="pending",
        source_validation_id=mapping.source_validation_id,
        source_validation_hash=mapping.source_validation_hash,
        source_mapping_id=mapping.mapping_id,
        source_mapping_hash=mapping.mapping_hash,
        source_artifact_id=mapping.artifact_id,
        story_id=mapping.story_id,
        records=tuple(records),
        external_statuses=tuple(statuses),
        category_states=mapping.category_states,
        preserved_uninterpreted_top_level_pointers=(
            mapping.preserved_uninterpreted_top_level_pointers
        ),
        safety_boundary=NcpProvenanceSafetyBoundary(),
    )
    provenance_hash = compute_ncp_provenance_hash(provisional._hash_material())
    return NcpProvenanceResult(
        provenance_id=f"ncp-provenance-{provenance_hash[:32]}",
        provenance_hash=provenance_hash,
        source_validation_id=provisional.source_validation_id,
        source_validation_hash=provisional.source_validation_hash,
        source_mapping_id=provisional.source_mapping_id,
        source_mapping_hash=provisional.source_mapping_hash,
        source_artifact_id=provisional.source_artifact_id,
        story_id=provisional.story_id,
        records=provisional.records,
        external_statuses=provisional.external_statuses,
        category_states=provisional.category_states,
        preserved_uninterpreted_top_level_pointers=(
            provisional.preserved_uninterpreted_top_level_pointers
        ),
        safety_boundary=provisional.safety_boundary,
    )
