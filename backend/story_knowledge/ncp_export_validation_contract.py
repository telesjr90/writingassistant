"""Pure T010F validation-before-export and round-trip trust contracts.

Validation consumes an intact T010E plan plus caller-supplied bytes for the
recovered repo-local NCP schema/interface artifacts.  The artifact bytes must
match pinned identities before the standard package is assembled in memory
and checked against the exact recovered Draft-07 JSON Schema.  No filesystem
destination, Node/npm validator, subprocess, network, model, or live NCP
runtime is used.

Only an app-generated, schema-valid, approved-context standard package earns
trusted round-trip provenance.  A separately labeled candidate-review bundle
may validate as review metadata but never earns standard-export or round-trip
authority.  External imports always remain on the T010A-T010D review path.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re
from typing import Mapping

from backend.story_knowledge.ncp_export_contract import (
    NCP_CANDIDATE_REVIEW_PACKAGE_KIND,
    NCP_EXPORT_CONTRACT_VERSION,
    NCP_EXPORT_OMISSION_POLICY,
    NCP_STANDARD_EXPORT_PACKAGE_KIND,
    NcpCandidateReviewBundle,
    NcpExportPlan,
    NcpExportValidationError,
    NcpStandardExportPackage,
    validate_ncp_export_plan_record,
)
from backend.story_knowledge.ncp_import_contract import (
    NCP_APP_MAPPING_VERSION,
    SUPPORTED_NCP_SCHEMA_VERSION,
    NcpExternalStatusMetadata,
    NcpImportValidationError,
    NcpImportValidationResult,
    validate_ncp_import_artifact,
)
from backend.story_knowledge.ncp_provenance_contract import (
    NCP_EXTERNAL_STATUS_POLICY,
    canonical_source_value_json_bytes,
)


NCP_EXPORT_VALIDATION_CONTRACT_VERSION = (
    "writer-assistant-ncp-export-validation.v1"
)
NCP_TRUSTED_ROUND_TRIP_PROVENANCE_VERSION = (
    "writer-assistant-ncp-trusted-round-trip.v1"
)
NCP_SCHEMA_DRAFT = "http://json-schema.org/draft-07/schema#"
NCP_SCHEMA_TITLE = "Narrative Context Protocol Schema"
NCP_SCHEMA_INTERFACE_KIND = "recovered_repo_local_ncp_schema_interface"
NCP_SCHEMA_VALIDATION_MODE = "pure_local_exact_recovered_draft07_schema"
NCP_EXTERNAL_IMPORT_REQUIRED_FLOW = "t010a_through_t010d_candidate_review"

NCP_SCHEMA_JSON_PATH = (
    ".external_sources/narrative-context-protocol/schema/ncp-schema.json"
)
NCP_SCHEMA_YAML_PATH = (
    ".external_sources/narrative-context-protocol/schema/ncp-schema.yaml"
)
NCP_PACKAGE_JSON_PATH = (
    ".external_sources/narrative-context-protocol/package.json"
)
NCP_SCHEMA_RECOVERY_PATH = (
    ".external_sources/narrative-context-protocol/SCHEMA_INTERFACE_RECOVERY.md"
)

NCP_SCHEMA_JSON_SHA256 = (
    "34197d575b261905a43c4e79c48435df833deeeecd85cce918b00850f2bf8ca4"
)
NCP_SCHEMA_YAML_SHA256 = (
    "0ab46f2008de871f5ebdede36232885dcd4c20df86011aa080cbce13b9199d5e"
)
NCP_PACKAGE_JSON_SHA256 = (
    "3b2c38d74678980e66d205f67b3bbcedb8bdeff45659aec9954046e83d559141"
)
NCP_SCHEMA_RECOVERY_SHA256 = (
    "f8ea76ff1acd3fba1608b1c28e326ebb9e799d32f7a9a5c9538a19537dabe7f3"
)


class NcpExportPreflightValidationError(ValueError):
    """Fail-closed error for T010F evidence, schema, package, or trust input."""

    def __init__(self, code: str, location: str, detail: str) -> None:
        self.code = code
        self.location = location
        self.detail = detail
        super().__init__(f"{code} at {location or '/'}: {detail}")


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(canonical_source_value_json_bytes(value)).hexdigest()


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


@dataclass(frozen=True)
class NcpSchemaInterfaceArtifact:
    role: str
    repo_relative_path: str
    sha256: str

    def to_dict(self) -> dict[str, str]:
        return {
            "role": self.role,
            "repo_relative_path": self.repo_relative_path,
            "sha256": self.sha256,
        }


@dataclass(frozen=True)
class NcpSchemaInterfaceEvidence:
    schema_interface_id: str
    schema_interface_hash: str
    artifacts: tuple[NcpSchemaInterfaceArtifact, ...]
    schema_json_bytes: bytes
    schema_yaml_bytes: bytes
    package_json_bytes: bytes
    recovery_record_bytes: bytes
    schema_draft: str
    schema_title: str
    root_required_fields: tuple[str, ...]
    root_additional_properties: bool
    package_validate_schema_command: str
    package_validate_file_command: str
    interface_kind: str = NCP_SCHEMA_INTERFACE_KIND
    supported_ncp_schema_version: str = SUPPORTED_NCP_SCHEMA_VERSION
    validator_surface_status: str = "optional_unavailable_not_executed"
    node_validator_executed: bool = False
    npm_validator_executed: bool = False
    subprocess_validator_executed: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_interface_id": self.schema_interface_id,
            "schema_interface_hash": self.schema_interface_hash,
            "interface_kind": self.interface_kind,
            "supported_ncp_schema_version": self.supported_ncp_schema_version,
            "schema_draft": self.schema_draft,
            "schema_title": self.schema_title,
            "root_required_fields": list(self.root_required_fields),
            "root_additional_properties": self.root_additional_properties,
            "package_validate_schema_command": self.package_validate_schema_command,
            "package_validate_file_command": self.package_validate_file_command,
            "validator_surface_status": self.validator_surface_status,
            "node_validator_executed": self.node_validator_executed,
            "npm_validator_executed": self.npm_validator_executed,
            "subprocess_validator_executed": self.subprocess_validator_executed,
            "artifacts": [item.to_dict() for item in self.artifacts],
        }


def build_ncp_schema_interface_evidence(
    *,
    schema_json_bytes: bytes,
    schema_yaml_bytes: bytes,
    package_json_bytes: bytes,
    recovery_record_bytes: bytes,
) -> NcpSchemaInterfaceEvidence:
    """Verify exact recovered bytes and build immutable interface evidence."""

    supplied = (
        ("draft07_json_schema", NCP_SCHEMA_JSON_PATH, NCP_SCHEMA_JSON_SHA256, schema_json_bytes),
        ("yaml_schema_mirror", NCP_SCHEMA_YAML_PATH, NCP_SCHEMA_YAML_SHA256, schema_yaml_bytes),
        ("package_interface", NCP_PACKAGE_JSON_PATH, NCP_PACKAGE_JSON_SHA256, package_json_bytes),
        ("recovery_record", NCP_SCHEMA_RECOVERY_PATH, NCP_SCHEMA_RECOVERY_SHA256, recovery_record_bytes),
    )
    artifacts: list[NcpSchemaInterfaceArtifact] = []
    for role, path, expected_hash, content in supplied:
        if not isinstance(content, bytes) or _sha256_bytes(content) != expected_hash:
            raise NcpExportPreflightValidationError(
                "unsupported_schema_interface_identity",
                path,
                "repo-local schema/interface bytes do not match the pinned artifact",
            )
        artifacts.append(NcpSchemaInterfaceArtifact(role, path, expected_hash))
    try:
        schema = json.loads(schema_json_bytes.decode("utf-8"))
        package = json.loads(package_json_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise NcpExportPreflightValidationError(
            "malformed_schema_interface", "", "schema/interface JSON is malformed"
        ) from exc
    if (
        not isinstance(schema, dict)
        or schema.get("$schema") != NCP_SCHEMA_DRAFT
        or schema.get("title") != NCP_SCHEMA_TITLE
        or schema.get("type") != "object"
        or schema.get("required") != ["schema_version", "story"]
        or schema.get("additionalProperties") is not False
    ):
        raise NcpExportPreflightValidationError(
            "unsupported_schema_interface_shape",
            NCP_SCHEMA_JSON_PATH,
            "recovered schema identity does not expose the supported root contract",
        )
    scripts = package.get("scripts") if isinstance(package, dict) else None
    if not isinstance(scripts, dict) or scripts.get("validate:schema") != (
        "node tests/validate-schema.js"
    ) or scripts.get("validate:file") != "node tests/validate-file.js":
        raise NcpExportPreflightValidationError(
            "unsupported_schema_interface_shape",
            NCP_PACKAGE_JSON_PATH,
            "package interface does not declare the recovered validation commands",
        )
    material = {
        "interface_kind": NCP_SCHEMA_INTERFACE_KIND,
        "supported_ncp_schema_version": SUPPORTED_NCP_SCHEMA_VERSION,
        "schema_draft": NCP_SCHEMA_DRAFT,
        "schema_title": NCP_SCHEMA_TITLE,
        "artifacts": [item.to_dict() for item in artifacts],
        "validator_surface_status": "optional_unavailable_not_executed",
    }
    interface_hash = _canonical_hash(material)
    return NcpSchemaInterfaceEvidence(
        schema_interface_id=f"ncp-schema-interface-{interface_hash[:32]}",
        schema_interface_hash=interface_hash,
        artifacts=tuple(artifacts),
        schema_json_bytes=schema_json_bytes,
        schema_yaml_bytes=schema_yaml_bytes,
        package_json_bytes=package_json_bytes,
        recovery_record_bytes=recovery_record_bytes,
        schema_draft=NCP_SCHEMA_DRAFT,
        schema_title=NCP_SCHEMA_TITLE,
        root_required_fields=("schema_version", "story"),
        root_additional_properties=False,
        package_validate_schema_command=scripts["validate:schema"],
        package_validate_file_command=scripts["validate:file"],
    )


def _revalidate_schema_interface(
    evidence: NcpSchemaInterfaceEvidence,
) -> NcpSchemaInterfaceEvidence:
    if not isinstance(evidence, NcpSchemaInterfaceEvidence):
        raise NcpExportPreflightValidationError(
            "schema_interface_evidence_required",
            "",
            "validation requires recovered repo-local schema/interface evidence",
        )
    expected = build_ncp_schema_interface_evidence(
        schema_json_bytes=evidence.schema_json_bytes,
        schema_yaml_bytes=evidence.schema_yaml_bytes,
        package_json_bytes=evidence.package_json_bytes,
        recovery_record_bytes=evidence.recovery_record_bytes,
    )
    if expected != evidence:
        raise NcpExportPreflightValidationError(
            "schema_interface_evidence_mismatch",
            "",
            "schema/interface evidence metadata is not deterministic or intact",
        )
    return expected


def _pointer_segments(pointer: str) -> tuple[str, ...]:
    if not pointer.startswith("/"):
        raise NcpExportPreflightValidationError(
            "invalid_export_pointer", pointer, "approved export pointer must be absolute"
        )
    segments: list[str] = []
    for raw in pointer[1:].split("/"):
        result = ""
        index = 0
        while index < len(raw):
            if raw[index] != "~":
                result += raw[index]
                index += 1
            elif index + 1 < len(raw) and raw[index + 1] in "01":
                result += "~" if raw[index + 1] == "0" else "/"
                index += 2
            else:
                raise NcpExportPreflightValidationError(
                    "invalid_export_pointer", pointer, "JSON pointer escape is invalid"
                )
        segments.append(result)
    return tuple(segments)


def _set_document_pointer(document: dict[str, object], pointer: str, value: object) -> None:
    segments = _pointer_segments(pointer)
    current: object = document
    for index, segment in enumerate(segments):
        final = index == len(segments) - 1
        next_is_index = not final and segments[index + 1].isdigit()
        if isinstance(current, dict):
            if final:
                if segment in current and current[segment] != value:
                    raise NcpExportPreflightValidationError(
                        "overlapping_approved_export_values",
                        pointer,
                        "approved records assign conflicting values",
                    )
                current[segment] = value
                return
            if segment not in current:
                current[segment] = [] if next_is_index else {}
            current = current[segment]
        elif isinstance(current, list):
            if not segment.isdigit():
                raise NcpExportPreflightValidationError(
                    "invalid_export_pointer", pointer, "array segment must be an index"
                )
            array_index = int(segment)
            if array_index > len(current):
                raise NcpExportPreflightValidationError(
                    "sparse_export_array", pointer, "approved export arrays cannot be sparse"
                )
            if final:
                if array_index == len(current):
                    current.append(value)
                elif current[array_index] != value:
                    raise NcpExportPreflightValidationError(
                        "overlapping_approved_export_values",
                        pointer,
                        "approved records assign conflicting values",
                    )
                return
            if array_index == len(current):
                current.append([] if next_is_index else {})
            current = current[array_index]
        else:
            raise NcpExportPreflightValidationError(
                "overlapping_approved_export_values",
                pointer,
                "approved record path crosses an existing scalar value",
            )


def _assemble_standard_document(package: NcpStandardExportPackage) -> dict[str, object]:
    document: dict[str, object] = {"schema_version": package.ncp_schema_version}
    for record in package.records:
        _set_document_pointer(document, record.ncp_json_pointer, record.source_value)
    return document


def _schema_pointer_get(root: Mapping[str, object], pointer: str) -> object:
    current: object = root
    for raw in pointer[2:].split("/"):
        segment = raw.replace("~1", "/").replace("~0", "~")
        if not isinstance(current, dict) or segment not in current:
            raise NcpExportPreflightValidationError(
                "unsupported_schema_reference", pointer, "schema reference is absent"
            )
        current = current[segment]
    return current


def _json_type_matches(instance: object, expected: str) -> bool:
    return {
        "object": isinstance(instance, dict),
        "array": isinstance(instance, list),
        "string": isinstance(instance, str),
        "integer": type(instance) is int,
        "number": type(instance) in {int, float},
        "boolean": type(instance) is bool,
        "null": instance is None,
    }.get(expected, False)


def _schema_matches(instance: object, schema: object, root: Mapping[str, object]) -> bool:
    try:
        _validate_schema_value(instance, schema, root, "")
    except NcpExportPreflightValidationError:
        return False
    return True


def _validate_schema_value(
    instance: object,
    schema: object,
    root: Mapping[str, object],
    pointer: str,
) -> None:
    if not isinstance(schema, dict):
        raise NcpExportPreflightValidationError(
            "unsupported_schema_keyword", pointer, "schema node must be an object"
        )
    if "$ref" in schema:
        reference = schema["$ref"]
        if not isinstance(reference, str) or not reference.startswith("#/"):
            raise NcpExportPreflightValidationError(
                "unsupported_schema_reference", pointer, "only local schema refs are supported"
            )
        _validate_schema_value(instance, _schema_pointer_get(root, reference), root, pointer)
        return
    if "allOf" in schema:
        for branch in schema["allOf"]:
            _validate_schema_value(instance, branch, root, pointer)
    if "anyOf" in schema and not any(
        _schema_matches(instance, branch, root) for branch in schema["anyOf"]
    ):
        raise NcpExportPreflightValidationError(
            "schema_validation_failed", pointer, "value matches no allowed schema branch"
        )
    if "if" in schema and _schema_matches(instance, schema["if"], root):
        if "then" in schema:
            _validate_schema_value(instance, schema["then"], root, pointer)
    elif "else" in schema:
        _validate_schema_value(instance, schema["else"], root, pointer)
    if "const" in schema and instance != schema["const"]:
        raise NcpExportPreflightValidationError(
            "schema_validation_failed", pointer, "value does not match schema const"
        )
    if "enum" in schema and instance not in schema["enum"]:
        raise NcpExportPreflightValidationError(
            "schema_validation_failed", pointer, "value is outside schema enum"
        )
    expected_type = schema.get("type")
    if isinstance(expected_type, str) and not _json_type_matches(instance, expected_type):
        raise NcpExportPreflightValidationError(
            "schema_validation_failed", pointer, f"value is not schema type {expected_type}"
        )
    for keyword, violates_bound, detail in (
        ("minimum", lambda value, bound: value < bound, "below schema minimum"),
        ("maximum", lambda value, bound: value > bound, "above schema maximum"),
    ):
        if keyword not in schema:
            continue
        bound = schema[keyword]
        if type(bound) not in {int, float}:
            raise NcpExportPreflightValidationError(
                "unsupported_schema_keyword",
                pointer,
                f"schema {keyword} must be numeric",
            )
        if type(instance) in {int, float} and violates_bound(instance, bound):
            raise NcpExportPreflightValidationError(
                "schema_validation_failed",
                pointer,
                f"number is {detail} {bound}",
            )
    pattern = schema.get("pattern")
    if isinstance(pattern, str) and isinstance(instance, str):
        try:
            matches = re.search(pattern, instance) is not None
        except re.error as exc:
            raise NcpExportPreflightValidationError(
                "unsupported_schema_pattern", pointer, "schema regex is unsupported"
            ) from exc
        if not matches:
            raise NcpExportPreflightValidationError(
                "schema_validation_failed", pointer, "string does not match schema pattern"
            )
    if isinstance(instance, dict):
        required = schema.get("required", [])
        if isinstance(required, list):
            for field in required:
                if field not in instance:
                    raise NcpExportPreflightValidationError(
                        "schema_validation_failed",
                        f"{pointer}/{field}" if pointer else f"/{field}",
                        "required schema field is absent",
                    )
        properties = schema.get("properties", {})
        if not isinstance(properties, dict):
            properties = {}
        for field in sorted(instance):
            field_pointer = f"{pointer}/{field}" if pointer else f"/{field}"
            if field in properties:
                _validate_schema_value(instance[field], properties[field], root, field_pointer)
            elif schema.get("additionalProperties") is False:
                raise NcpExportPreflightValidationError(
                    "schema_validation_failed", field_pointer, "additional property is forbidden"
                )
            elif isinstance(schema.get("additionalProperties"), dict):
                _validate_schema_value(
                    instance[field], schema["additionalProperties"], root, field_pointer
                )
    if isinstance(instance, list) and isinstance(schema.get("items"), dict):
        for index, item in enumerate(instance):
            _validate_schema_value(item, schema["items"], root, f"{pointer}/{index}")


@dataclass(frozen=True)
class NcpExportValidationSafetyBoundary:
    validation_before_export: bool = True
    pure_in_memory_validation: bool = True
    exact_repo_local_schema_bytes_required: bool = True
    file_write_performed: bool = False
    export_destination_write_performed: bool = False
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
        return {
            field: getattr(self, field)
            for field in self.__dataclass_fields__
        }


@dataclass(frozen=True)
class NcpPackageValidationRecord:
    validation_id: str
    validation_hash: str
    source_export_plan_id: str
    source_export_plan_hash: str
    package_id: str
    package_hash: str
    package_kind: str
    schema_interface_id: str
    schema_interface_hash: str
    schema_path: str
    schema_sha256: str
    validation_outcome: str
    package_exportable: bool
    standard_approved_context_export: bool
    candidate_review_bundle: bool
    trusted_round_trip_eligible: bool
    app_generated: bool
    app_provenance_refs: tuple[str, ...]
    validated_document_sha256: str | None
    omission_policy: str
    external_status_policy: str
    safety_boundary: NcpExportValidationSafetyBoundary
    contract_version: str = NCP_EXPORT_VALIDATION_CONTRACT_VERSION
    ncp_schema_version: str = SUPPORTED_NCP_SCHEMA_VERSION
    app_mapping_version: str = NCP_APP_MAPPING_VERSION
    app_export_version: str = NCP_EXPORT_CONTRACT_VERSION
    schema_validation_mode: str = NCP_SCHEMA_VALIDATION_MODE

    def _hash_material(self) -> dict[str, object]:
        return {
            "contract_version": self.contract_version,
            "ncp_schema_version": self.ncp_schema_version,
            "app_mapping_version": self.app_mapping_version,
            "app_export_version": self.app_export_version,
            "schema_validation_mode": self.schema_validation_mode,
            "source_export_plan_id": self.source_export_plan_id,
            "source_export_plan_hash": self.source_export_plan_hash,
            "package_id": self.package_id,
            "package_hash": self.package_hash,
            "package_kind": self.package_kind,
            "schema_interface_id": self.schema_interface_id,
            "schema_interface_hash": self.schema_interface_hash,
            "schema_path": self.schema_path,
            "schema_sha256": self.schema_sha256,
            "validation_outcome": self.validation_outcome,
            "package_exportable": self.package_exportable,
            "standard_approved_context_export": self.standard_approved_context_export,
            "candidate_review_bundle": self.candidate_review_bundle,
            "trusted_round_trip_eligible": self.trusted_round_trip_eligible,
            "app_generated": self.app_generated,
            "app_provenance_refs": list(self.app_provenance_refs),
            "validated_document_sha256": self.validated_document_sha256,
            "omission_policy": self.omission_policy,
            "external_status_policy": self.external_status_policy,
            "safety_boundary": self.safety_boundary.to_dict(),
        }

    def to_dict(self) -> dict[str, object]:
        value = self._hash_material()
        value["validation_id"] = self.validation_id
        value["validation_hash"] = self.validation_hash
        return value


@dataclass(frozen=True)
class NcpTrustedRoundTripProvenance:
    provenance_id: str
    provenance_hash: str
    export_validation_id: str
    export_validation_hash: str
    source_export_plan_id: str
    source_export_plan_hash: str
    standard_package_id: str
    standard_package_hash: str
    schema_interface_id: str
    schema_interface_hash: str
    approval_provenance_refs: tuple[str, ...]
    source_kind: str = "trusted_app_generated_standard_export"
    trusted_round_trip_eligible: bool = True
    approved_context_only: bool = True
    candidate_bundle_trusted: bool = False
    external_import_trusted: bool = False
    local_approval_created: bool = False
    contract_version: str = NCP_TRUSTED_ROUND_TRIP_PROVENANCE_VERSION

    def _hash_material(self) -> dict[str, object]:
        return {
            "contract_version": self.contract_version,
            "source_kind": self.source_kind,
            "export_validation_id": self.export_validation_id,
            "export_validation_hash": self.export_validation_hash,
            "source_export_plan_id": self.source_export_plan_id,
            "source_export_plan_hash": self.source_export_plan_hash,
            "standard_package_id": self.standard_package_id,
            "standard_package_hash": self.standard_package_hash,
            "schema_interface_id": self.schema_interface_id,
            "schema_interface_hash": self.schema_interface_hash,
            "approval_provenance_refs": list(self.approval_provenance_refs),
            "trusted_round_trip_eligible": self.trusted_round_trip_eligible,
            "approved_context_only": self.approved_context_only,
            "candidate_bundle_trusted": self.candidate_bundle_trusted,
            "external_import_trusted": self.external_import_trusted,
            "local_approval_created": self.local_approval_created,
        }

    def to_dict(self) -> dict[str, object]:
        value = self._hash_material()
        value["provenance_id"] = self.provenance_id
        value["provenance_hash"] = self.provenance_hash
        return value


@dataclass(frozen=True)
class NcpExportValidationResult:
    result_id: str
    result_hash: str
    schema_interface: NcpSchemaInterfaceEvidence
    standard_export_validation: NcpPackageValidationRecord
    candidate_review_bundle_validation: NcpPackageValidationRecord | None
    trusted_round_trip_provenance: NcpTrustedRoundTripProvenance
    safety_boundary: NcpExportValidationSafetyBoundary
    contract_version: str = NCP_EXPORT_VALIDATION_CONTRACT_VERSION
    validation_before_export_complete: bool = True

    def _hash_material(self) -> dict[str, object]:
        return {
            "contract_version": self.contract_version,
            "validation_before_export_complete": self.validation_before_export_complete,
            "schema_interface": self.schema_interface.to_dict(),
            "standard_export_validation": self.standard_export_validation.to_dict(),
            "candidate_review_bundle_validation": (
                self.candidate_review_bundle_validation.to_dict()
                if self.candidate_review_bundle_validation is not None
                else None
            ),
            "trusted_round_trip_provenance": (
                self.trusted_round_trip_provenance.to_dict()
            ),
            "safety_boundary": self.safety_boundary.to_dict(),
        }

    def to_dict(self) -> dict[str, object]:
        value = self._hash_material()
        value["result_id"] = self.result_id
        value["result_hash"] = self.result_hash
        return value


@dataclass(frozen=True)
class NcpExternalImportTrustAssessment:
    assessment_id: str
    assessment_hash: str
    source_validation_id: str
    source_artifact_id: str
    source_artifact_sha256: str
    external_statuses: tuple[NcpExternalStatusMetadata, ...]
    source_kind: str = "external_imported_ncp"
    trust_outcome: str = "untrusted_external_requires_candidate_review"
    trusted_round_trip_eligible: bool = False
    required_import_flow: str = NCP_EXTERNAL_IMPORT_REQUIRED_FLOW
    external_status_policy: str = NCP_EXTERNAL_STATUS_POLICY
    local_approval: bool = False
    canon_authority: bool = False
    promotion_authority: bool = False
    apply_promotion_authority: bool = False

    def _hash_material(self) -> dict[str, object]:
        return {
            "source_kind": self.source_kind,
            "trust_outcome": self.trust_outcome,
            "source_validation_id": self.source_validation_id,
            "source_artifact_id": self.source_artifact_id,
            "source_artifact_sha256": self.source_artifact_sha256,
            "external_statuses": [item.to_dict() for item in self.external_statuses],
            "trusted_round_trip_eligible": self.trusted_round_trip_eligible,
            "required_import_flow": self.required_import_flow,
            "external_status_policy": self.external_status_policy,
            "local_approval": self.local_approval,
            "canon_authority": self.canon_authority,
            "promotion_authority": self.promotion_authority,
            "apply_promotion_authority": self.apply_promotion_authority,
        }

    def to_dict(self) -> dict[str, object]:
        value = self._hash_material()
        value["assessment_id"] = self.assessment_id
        value["assessment_hash"] = self.assessment_hash
        return value


def _build_package_validation(
    *,
    export_plan: NcpExportPlan,
    package: NcpStandardExportPackage | NcpCandidateReviewBundle,
    evidence: NcpSchemaInterfaceEvidence,
    outcome: str,
    package_exportable: bool,
    standard: bool,
    trusted: bool,
    provenance_refs: tuple[str, ...],
    document_hash: str | None,
) -> NcpPackageValidationRecord:
    provisional = NcpPackageValidationRecord(
        validation_id="pending",
        validation_hash="pending",
        source_export_plan_id=export_plan.export_plan_id,
        source_export_plan_hash=export_plan.export_plan_hash,
        package_id=package.package_id,
        package_hash=package.package_hash,
        package_kind=package.package_kind,
        schema_interface_id=evidence.schema_interface_id,
        schema_interface_hash=evidence.schema_interface_hash,
        schema_path=NCP_SCHEMA_JSON_PATH,
        schema_sha256=NCP_SCHEMA_JSON_SHA256,
        validation_outcome=outcome,
        package_exportable=package_exportable,
        standard_approved_context_export=standard,
        candidate_review_bundle=not standard,
        trusted_round_trip_eligible=trusted,
        app_generated=True,
        app_provenance_refs=provenance_refs,
        validated_document_sha256=document_hash,
        omission_policy=NCP_EXPORT_OMISSION_POLICY,
        external_status_policy=NCP_EXTERNAL_STATUS_POLICY,
        safety_boundary=NcpExportValidationSafetyBoundary(),
    )
    validation_hash = _canonical_hash(provisional._hash_material())
    return NcpPackageValidationRecord(
        validation_id=f"ncp-export-validation-{validation_hash[:32]}",
        validation_hash=validation_hash,
        source_export_plan_id=provisional.source_export_plan_id,
        source_export_plan_hash=provisional.source_export_plan_hash,
        package_id=provisional.package_id,
        package_hash=provisional.package_hash,
        package_kind=provisional.package_kind,
        schema_interface_id=provisional.schema_interface_id,
        schema_interface_hash=provisional.schema_interface_hash,
        schema_path=provisional.schema_path,
        schema_sha256=provisional.schema_sha256,
        validation_outcome=provisional.validation_outcome,
        package_exportable=provisional.package_exportable,
        standard_approved_context_export=provisional.standard_approved_context_export,
        candidate_review_bundle=provisional.candidate_review_bundle,
        trusted_round_trip_eligible=provisional.trusted_round_trip_eligible,
        app_generated=provisional.app_generated,
        app_provenance_refs=provisional.app_provenance_refs,
        validated_document_sha256=provisional.validated_document_sha256,
        omission_policy=provisional.omission_policy,
        external_status_policy=provisional.external_status_policy,
        safety_boundary=provisional.safety_boundary,
    )


def _build_round_trip_provenance(
    export_plan: NcpExportPlan,
    validation: NcpPackageValidationRecord,
    evidence: NcpSchemaInterfaceEvidence,
) -> NcpTrustedRoundTripProvenance:
    provisional = NcpTrustedRoundTripProvenance(
        provenance_id="pending",
        provenance_hash="pending",
        export_validation_id=validation.validation_id,
        export_validation_hash=validation.validation_hash,
        source_export_plan_id=export_plan.export_plan_id,
        source_export_plan_hash=export_plan.export_plan_hash,
        standard_package_id=validation.package_id,
        standard_package_hash=validation.package_hash,
        schema_interface_id=evidence.schema_interface_id,
        schema_interface_hash=evidence.schema_interface_hash,
        approval_provenance_refs=validation.app_provenance_refs,
    )
    provenance_hash = _canonical_hash(provisional._hash_material())
    return NcpTrustedRoundTripProvenance(
        provenance_id=f"ncp-trusted-round-trip-{provenance_hash[:32]}",
        provenance_hash=provenance_hash,
        export_validation_id=provisional.export_validation_id,
        export_validation_hash=provisional.export_validation_hash,
        source_export_plan_id=provisional.source_export_plan_id,
        source_export_plan_hash=provisional.source_export_plan_hash,
        standard_package_id=provisional.standard_package_id,
        standard_package_hash=provisional.standard_package_hash,
        schema_interface_id=provisional.schema_interface_id,
        schema_interface_hash=provisional.schema_interface_hash,
        approval_provenance_refs=provisional.approval_provenance_refs,
    )


def validate_ncp_export_before_export(
    export_plan: NcpExportPlan,
    schema_interface: NcpSchemaInterfaceEvidence,
) -> NcpExportValidationResult:
    """Validate T010E packages before export and issue standard trust metadata."""

    if not isinstance(export_plan, NcpExportPlan):
        raise NcpExportPreflightValidationError(
            "app_generated_t010e_export_plan_required",
            "",
            "external or untyped packages cannot enter trusted export validation",
        )
    evidence = _revalidate_schema_interface(schema_interface)
    try:
        validate_ncp_export_plan_record(export_plan.to_dict())
    except NcpExportValidationError as exc:
        raise NcpExportPreflightValidationError(
            "invalid_t010e_export_plan",
            "",
            "export plan is not an intact supported T010E app-generated plan",
        ) from exc

    standard = export_plan.standard_export
    if standard.package_kind != NCP_STANDARD_EXPORT_PACKAGE_KIND:
        raise NcpExportPreflightValidationError(
            "unsafe_standard_package_kind",
            "/standard_export/package_kind",
            "standard validation accepts approved-context package kind only",
        )
    if (
        standard.candidate_source_plan_id is not None
        or standard.candidate_review_bundle_id is not None
        or standard.safety_boundary.candidate_records_included
        or standard.safety_boundary.pending_review_records_included
        or standard.safety_boundary.unresolved_conflicts_included
        or standard.safety_boundary.candidate_review_bundle_merged
    ):
        raise NcpExportPreflightValidationError(
            "candidate_leakage_into_standard_export",
            "/standard_export",
            "pending candidates or review bundles cannot enter standard validation",
        )
    provenance_refs: list[str] = [export_plan.export_plan_id, standard.package_id]
    for index, record in enumerate(standard.records):
        if (
            not record.approved_context_record_id.strip()
            or not record.approval_record_id.strip()
            or not record.owner_approved
            or record.candidate_record
            or record.pending_review
        ):
            raise NcpExportPreflightValidationError(
                "missing_approved_context_provenance",
                f"/standard_export/records/{index}",
                "every standard value needs explicit approved-context provenance",
            )
        provenance_refs.extend(
            (record.approved_context_record_id, record.approval_record_id)
        )
    if len(provenance_refs) != len(set(provenance_refs)):
        raise NcpExportPreflightValidationError(
            "ambiguous_approved_context_provenance",
            "/standard_export/records",
            "app provenance references must be unique",
        )
    document = _assemble_standard_document(standard)
    try:
        schema = json.loads(evidence.schema_json_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise NcpExportPreflightValidationError(
            "malformed_schema_interface", NCP_SCHEMA_JSON_PATH, "schema JSON is malformed"
        ) from exc
    _validate_schema_value(document, schema, schema, "")
    document_hash = _canonical_hash(document)
    standard_validation = _build_package_validation(
        export_plan=export_plan,
        package=standard,
        evidence=evidence,
        outcome="valid_standard_approved_context_export",
        package_exportable=True,
        standard=True,
        trusted=True,
        provenance_refs=tuple(provenance_refs),
        document_hash=document_hash,
    )

    candidate_validation: NcpPackageValidationRecord | None = None
    candidate_bundle = export_plan.candidate_review_bundle
    if candidate_bundle is not None:
        if candidate_bundle.package_kind != NCP_CANDIDATE_REVIEW_PACKAGE_KIND:
            raise NcpExportPreflightValidationError(
                "unsafe_candidate_review_package_kind",
                "/candidate_review_bundle/package_kind",
                "review bundle must retain its separate package kind",
            )
        candidate_refs = (
            export_plan.export_plan_id,
            candidate_bundle.package_id,
            candidate_bundle.source_candidate_import_plan_id,
        )
        if any(not value.strip() for value in candidate_refs):
            raise NcpExportPreflightValidationError(
                "missing_candidate_bundle_provenance",
                "/candidate_review_bundle",
                "review bundle requires app plan provenance",
            )
        candidate_validation = _build_package_validation(
            export_plan=export_plan,
            package=candidate_bundle,
            evidence=evidence,
            outcome="valid_separately_labeled_candidate_review_bundle",
            package_exportable=True,
            standard=False,
            trusted=False,
            provenance_refs=candidate_refs,
            document_hash=None,
        )

    trusted_provenance = _build_round_trip_provenance(
        export_plan, standard_validation, evidence
    )
    provisional = NcpExportValidationResult(
        result_id="pending",
        result_hash="pending",
        schema_interface=evidence,
        standard_export_validation=standard_validation,
        candidate_review_bundle_validation=candidate_validation,
        trusted_round_trip_provenance=trusted_provenance,
        safety_boundary=NcpExportValidationSafetyBoundary(),
    )
    result_hash = _canonical_hash(provisional._hash_material())
    return NcpExportValidationResult(
        result_id=f"ncp-export-validation-result-{result_hash[:32]}",
        result_hash=result_hash,
        schema_interface=provisional.schema_interface,
        standard_export_validation=provisional.standard_export_validation,
        candidate_review_bundle_validation=(
            provisional.candidate_review_bundle_validation
        ),
        trusted_round_trip_provenance=(
            provisional.trusted_round_trip_provenance
        ),
        safety_boundary=provisional.safety_boundary,
    )


def assess_external_ncp_round_trip_trust(
    validated_import: NcpImportValidationResult,
) -> NcpExternalImportTrustAssessment:
    """Keep every external NCP artifact untrusted and on the review path."""

    if not isinstance(validated_import, NcpImportValidationResult):
        raise NcpExportPreflightValidationError(
            "validated_external_import_required",
            "",
            "external trust assessment requires a successful T010A result",
        )
    try:
        expected = validate_ncp_import_artifact(
            validated_import.artifact.original_bytes,
            project_id=validated_import.project_id,
            source_reference=validated_import.artifact.source_reference,
            media_type=validated_import.artifact.media_type,
        )
    except NcpImportValidationError as exc:
        raise NcpExportPreflightValidationError(
            "external_import_revalidation_failed",
            "",
            "external NCP artifact no longer passes T010A",
        ) from exc
    if expected != validated_import:
        raise NcpExportPreflightValidationError(
            "external_import_validation_mismatch",
            "",
            "external import validation result is not intact",
        )
    statuses = validated_import.external_narrative_statuses
    provisional = NcpExternalImportTrustAssessment(
        assessment_id="pending",
        assessment_hash="pending",
        source_validation_id=validated_import.validation_id,
        source_artifact_id=validated_import.artifact.artifact_id,
        source_artifact_sha256=validated_import.artifact.sha256,
        external_statuses=statuses,
    )
    assessment_hash = _canonical_hash(provisional._hash_material())
    return NcpExternalImportTrustAssessment(
        assessment_id=f"ncp-external-trust-{assessment_hash[:32]}",
        assessment_hash=assessment_hash,
        source_validation_id=provisional.source_validation_id,
        source_artifact_id=provisional.source_artifact_id,
        source_artifact_sha256=provisional.source_artifact_sha256,
        external_statuses=provisional.external_statuses,
    )


def compute_ncp_export_validation_result_hash(record: Mapping[str, object]) -> str:
    material = dict(record)
    material.pop("result_id", None)
    material.pop("result_hash", None)
    return _canonical_hash(material)


def _validate_nested_hash(
    record: Mapping[str, object],
    *,
    id_field: str,
    hash_field: str,
    id_prefix: str,
    location: str,
) -> None:
    material = dict(record)
    material.pop(id_field, None)
    material.pop(hash_field, None)
    actual_hash = _canonical_hash(material)
    if (
        record.get(hash_field) != actual_hash
        or record.get(id_field) != f"{id_prefix}{actual_hash[:32]}"
    ):
        raise NcpExportPreflightValidationError(
            "nested_validation_hash_mismatch",
            location,
            "nested validation or provenance metadata is not intact",
        )


def validate_ncp_export_validation_result_record(
    record: object,
) -> dict[str, object]:
    """Validate serialized T010F output and reject weakened trust semantics."""

    expected_fields = {
        "contract_version",
        "validation_before_export_complete",
        "schema_interface",
        "standard_export_validation",
        "candidate_review_bundle_validation",
        "trusted_round_trip_provenance",
        "safety_boundary",
        "result_id",
        "result_hash",
    }
    if not isinstance(record, dict) or set(record) != expected_fields:
        raise NcpExportPreflightValidationError(
            "invalid_validation_result", "", "validation result fields are not closed"
        )
    if (
        record["contract_version"] != NCP_EXPORT_VALIDATION_CONTRACT_VERSION
        or record["validation_before_export_complete"] is not True
        or record["safety_boundary"] != NcpExportValidationSafetyBoundary().to_dict()
    ):
        raise NcpExportPreflightValidationError(
            "weakened_validation_boundary",
            "/safety_boundary",
            "validation-before-export safety boundary is not intact",
        )
    interface = record["schema_interface"]
    expected_artifacts = [
        NcpSchemaInterfaceArtifact(
            "draft07_json_schema", NCP_SCHEMA_JSON_PATH, NCP_SCHEMA_JSON_SHA256
        ).to_dict(),
        NcpSchemaInterfaceArtifact(
            "yaml_schema_mirror", NCP_SCHEMA_YAML_PATH, NCP_SCHEMA_YAML_SHA256
        ).to_dict(),
        NcpSchemaInterfaceArtifact(
            "package_interface", NCP_PACKAGE_JSON_PATH, NCP_PACKAGE_JSON_SHA256
        ).to_dict(),
        NcpSchemaInterfaceArtifact(
            "recovery_record", NCP_SCHEMA_RECOVERY_PATH, NCP_SCHEMA_RECOVERY_SHA256
        ).to_dict(),
    ]
    expected_interface_hash = _canonical_hash(
        {
            "interface_kind": NCP_SCHEMA_INTERFACE_KIND,
            "supported_ncp_schema_version": SUPPORTED_NCP_SCHEMA_VERSION,
            "schema_draft": NCP_SCHEMA_DRAFT,
            "schema_title": NCP_SCHEMA_TITLE,
            "artifacts": expected_artifacts,
            "validator_surface_status": "optional_unavailable_not_executed",
        }
    )
    if (
        not isinstance(interface, dict)
        or interface.get("interface_kind") != NCP_SCHEMA_INTERFACE_KIND
        or interface.get("supported_ncp_schema_version")
        != SUPPORTED_NCP_SCHEMA_VERSION
        or interface.get("schema_draft") != NCP_SCHEMA_DRAFT
        or interface.get("schema_title") != NCP_SCHEMA_TITLE
        or interface.get("root_required_fields") != ["schema_version", "story"]
        or interface.get("root_additional_properties") is not False
        or interface.get("package_validate_schema_command")
        != "node tests/validate-schema.js"
        or interface.get("package_validate_file_command")
        != "node tests/validate-file.js"
        or interface.get("validator_surface_status")
        != "optional_unavailable_not_executed"
        or interface.get("node_validator_executed") is not False
        or interface.get("npm_validator_executed") is not False
        or interface.get("subprocess_validator_executed") is not False
        or interface.get("artifacts") != expected_artifacts
        or interface.get("schema_interface_hash") != expected_interface_hash
        or interface.get("schema_interface_id")
        != f"ncp-schema-interface-{expected_interface_hash[:32]}"
    ):
        raise NcpExportPreflightValidationError(
            "unsupported_schema_interface_identity",
            "/schema_interface",
            "serialized schema/interface binding is unsupported",
        )
    standard = record["standard_export_validation"]
    if (
        not isinstance(standard, dict)
        or standard.get("package_kind") != NCP_STANDARD_EXPORT_PACKAGE_KIND
        or standard.get("validation_outcome")
        != "valid_standard_approved_context_export"
        or standard.get("package_exportable") is not True
        or standard.get("standard_approved_context_export") is not True
        or standard.get("candidate_review_bundle") is not False
        or standard.get("trusted_round_trip_eligible") is not True
        or standard.get("app_generated") is not True
        or not standard.get("app_provenance_refs")
        or not _is_sha256(standard.get("validated_document_sha256"))
        or standard.get("safety_boundary")
        != NcpExportValidationSafetyBoundary().to_dict()
        or standard.get("schema_interface_id")
        != interface.get("schema_interface_id")
        or standard.get("schema_interface_hash")
        != interface.get("schema_interface_hash")
        or standard.get("schema_path") != NCP_SCHEMA_JSON_PATH
        or standard.get("schema_sha256") != NCP_SCHEMA_JSON_SHA256
        or standard.get("ncp_schema_version") != SUPPORTED_NCP_SCHEMA_VERSION
        or standard.get("app_mapping_version") != NCP_APP_MAPPING_VERSION
        or standard.get("app_export_version") != NCP_EXPORT_CONTRACT_VERSION
        or standard.get("contract_version")
        != NCP_EXPORT_VALIDATION_CONTRACT_VERSION
        or standard.get("schema_validation_mode") != NCP_SCHEMA_VALIDATION_MODE
        or standard.get("omission_policy") != NCP_EXPORT_OMISSION_POLICY
        or standard.get("external_status_policy") != NCP_EXTERNAL_STATUS_POLICY
    ):
        raise NcpExportPreflightValidationError(
            "unsafe_standard_validation_record",
            "/standard_export_validation",
            "standard package validation cannot lose approved app provenance",
        )
    _validate_nested_hash(
        standard,
        id_field="validation_id",
        hash_field="validation_hash",
        id_prefix="ncp-export-validation-",
        location="/standard_export_validation",
    )
    candidate = record["candidate_review_bundle_validation"]
    if candidate is not None and (
        not isinstance(candidate, dict)
        or candidate.get("package_kind") != NCP_CANDIDATE_REVIEW_PACKAGE_KIND
        or candidate.get("validation_outcome")
        != "valid_separately_labeled_candidate_review_bundle"
        or candidate.get("standard_approved_context_export") is not False
        or candidate.get("candidate_review_bundle") is not True
        or candidate.get("package_exportable") is not True
        or candidate.get("trusted_round_trip_eligible") is not False
        or candidate.get("app_generated") is not True
        or not candidate.get("app_provenance_refs")
        or candidate.get("validated_document_sha256") is not None
        or candidate.get("safety_boundary")
        != NcpExportValidationSafetyBoundary().to_dict()
        or candidate.get("schema_interface_id")
        != interface.get("schema_interface_id")
        or candidate.get("schema_interface_hash")
        != interface.get("schema_interface_hash")
        or candidate.get("schema_path") != NCP_SCHEMA_JSON_PATH
        or candidate.get("schema_sha256") != NCP_SCHEMA_JSON_SHA256
        or candidate.get("ncp_schema_version") != SUPPORTED_NCP_SCHEMA_VERSION
        or candidate.get("app_mapping_version") != NCP_APP_MAPPING_VERSION
        or candidate.get("app_export_version") != NCP_EXPORT_CONTRACT_VERSION
        or candidate.get("contract_version")
        != NCP_EXPORT_VALIDATION_CONTRACT_VERSION
        or candidate.get("schema_validation_mode") != NCP_SCHEMA_VALIDATION_MODE
        or candidate.get("omission_policy") != NCP_EXPORT_OMISSION_POLICY
        or candidate.get("external_status_policy") != NCP_EXTERNAL_STATUS_POLICY
    ):
        raise NcpExportPreflightValidationError(
            "unsafe_candidate_bundle_validation_record",
            "/candidate_review_bundle_validation",
            "candidate bundle cannot gain standard or round-trip trust",
        )
    if isinstance(candidate, dict):
        _validate_nested_hash(
            candidate,
            id_field="validation_id",
            hash_field="validation_hash",
            id_prefix="ncp-export-validation-",
            location="/candidate_review_bundle_validation",
        )
    trust = record["trusted_round_trip_provenance"]
    if (
        not isinstance(trust, dict)
        or trust.get("contract_version")
        != NCP_TRUSTED_ROUND_TRIP_PROVENANCE_VERSION
        or trust.get("source_kind") != "trusted_app_generated_standard_export"
        or trust.get("trusted_round_trip_eligible") is not True
        or trust.get("approved_context_only") is not True
        or trust.get("candidate_bundle_trusted") is not False
        or trust.get("external_import_trusted") is not False
        or trust.get("local_approval_created") is not False
        or not trust.get("approval_provenance_refs")
        or trust.get("export_validation_id") != standard.get("validation_id")
        or trust.get("export_validation_hash") != standard.get("validation_hash")
        or trust.get("source_export_plan_id")
        != standard.get("source_export_plan_id")
        or trust.get("source_export_plan_hash")
        != standard.get("source_export_plan_hash")
        or trust.get("standard_package_id") != standard.get("package_id")
        or trust.get("standard_package_hash") != standard.get("package_hash")
        or trust.get("schema_interface_id")
        != interface.get("schema_interface_id")
        or trust.get("schema_interface_hash")
        != interface.get("schema_interface_hash")
        or trust.get("approval_provenance_refs")
        != standard.get("app_provenance_refs")
    ):
        raise NcpExportPreflightValidationError(
            "unsafe_round_trip_provenance",
            "/trusted_round_trip_provenance",
            "trusted provenance is not restricted to validated approved context",
        )
    _validate_nested_hash(
        trust,
        id_field="provenance_id",
        hash_field="provenance_hash",
        id_prefix="ncp-trusted-round-trip-",
        location="/trusted_round_trip_provenance",
    )
    actual_hash = compute_ncp_export_validation_result_hash(record)
    if (
        record["result_hash"] != actual_hash
        or record["result_id"]
        != f"ncp-export-validation-result-{actual_hash[:32]}"
    ):
        raise NcpExportPreflightValidationError(
            "validation_result_hash_mismatch",
            "/result_hash",
            "validation result is not intact",
        )
    return json.loads(json.dumps(record, ensure_ascii=False))
