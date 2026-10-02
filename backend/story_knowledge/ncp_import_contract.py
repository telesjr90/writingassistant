"""Pure T010A contract for validating an original NCP import artifact.

This module validates exact caller-supplied JSON bytes before any candidate
construction or project-state write is possible.  It preserves the original
bytes in an immutable value object, pins the supported NCP and app-mapping
versions, and exposes T002/T003-compatible source and artifact identities.

It deliberately does not map NCP fields, build candidates, persist artifacts,
call an NCP runtime or validator, invoke a model, or settle project truth.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Mapping

from backend.story_knowledge.analysis_run_manifest import ArtifactReference
from backend.story_knowledge.source_map import (
    SourceIdentity,
    SourceIdentityValidationError,
    build_exact_source_snapshot,
)


NCP_IMPORT_CONTRACT_VERSION = "writer-assistant-ncp-import-validation.v1"
SUPPORTED_NCP_SCHEMA_VERSION = "1.3.0"
NCP_APP_MAPPING_VERSION = "writer-assistant-ncp-mapping.v1"
NCP_IMPORT_MEDIA_TYPE = "application/json"
NCP_IMPORT_ARTIFACT_TYPE = "source_snapshot"
NCP_UNKNOWN_FIELD_POLICY = (
    "preserve_exact_original_bytes_report_top_level_do_not_interpret"
)
MAX_NCP_IMPORT_BYTES = 8 * 1024 * 1024

_KNOWN_TOP_LEVEL_FIELDS = frozenset({"schema_version", "story"})
_FORBIDDEN_TOP_LEVEL_FIELDS = frozenset(
    {
        "approved",
        "approved_memory",
        "apply_promotion",
        "canon",
        "canonical_truth",
        "candidate_records",
        "local_approval",
        "owner_approved",
        "promotion",
        "promotion_records",
        "review_records",
    }
)
_EXTERNAL_NARRATIVE_STATUSES = frozenset({"candidate", "draft", "complete"})


class NcpImportValidationError(ValueError):
    """Deterministic fail-closed validation error for one import artifact."""

    def __init__(self, code: str, json_pointer: str, detail: str) -> None:
        self.code = code
        self.json_pointer = json_pointer
        self.detail = detail
        super().__init__(f"{code} at {json_pointer or '/'}: {detail}")


class _DuplicateJsonKey(ValueError):
    pass


def _canonical_json_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def _json_pointer_segment(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON constant is not supported: {value}")


def _closed_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise _DuplicateJsonKey(key)
        value[key] = item
    return value


def _require_nonempty_string(value: Any, pointer: str) -> str:
    if not isinstance(value, str) or not value.strip() or "\x00" in value:
        raise NcpImportValidationError(
            "invalid_required_field",
            pointer,
            "required value must be a non-empty string without NUL",
        )
    return value


def _require_field(value: Mapping[str, Any], field: str, pointer: str) -> Any:
    if field not in value:
        field_pointer = f"{pointer}/{_json_pointer_segment(field)}" if pointer else f"/{field}"
        raise NcpImportValidationError(
            "missing_required_field",
            field_pointer,
            "required field is absent",
        )
    return value[field]


def _validate_source_reference(value: Any) -> str:
    if (
        not isinstance(value, str)
        or not value.strip()
        or "\x00" in value
        or len(value) > 4096
    ):
        raise NcpImportValidationError(
            "invalid_source_reference",
            "/",
            "source_reference must be a non-empty bounded string without NUL",
        )
    return value


@dataclass(frozen=True)
class NcpExternalStatusMetadata:
    """External lifecycle metadata that has no local approval authority."""

    narrative_id: str
    json_pointer: str
    external_status: str | None
    status_present: bool
    local_approval: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "narrative_id": self.narrative_id,
            "json_pointer": self.json_pointer,
            "external_status": self.external_status,
            "status_present": self.status_present,
            "local_approval": self.local_approval,
        }


@dataclass(frozen=True)
class NcpImportSafetyBoundary:
    """Explicit negative capabilities for this validation-only slice."""

    support_data_only: bool = True
    candidate_truth: bool = False
    candidate_construction_performed: bool = False
    project_state_write_performed: bool = False
    candidate_write_performed: bool = False
    review_write_performed: bool = False
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
            "support_data_only": self.support_data_only,
            "candidate_truth": self.candidate_truth,
            "candidate_construction_performed": self.candidate_construction_performed,
            "project_state_write_performed": self.project_state_write_performed,
            "candidate_write_performed": self.candidate_write_performed,
            "review_write_performed": self.review_write_performed,
            "approval_performed": self.approval_performed,
            "promotion_performed": self.promotion_performed,
            "apply_promotion_performed": self.apply_promotion_performed,
            "memory_write_performed": self.memory_write_performed,
            "canon_write_performed": self.canon_write_performed,
            "generated_prose": self.generated_prose,
            "prose_transformation": self.prose_transformation,
            "live_ncp_execution": self.live_ncp_execution,
            "node_execution": self.node_execution,
            "npm_execution": self.npm_execution,
            "subprocess_execution": self.subprocess_execution,
            "network_execution": self.network_execution,
            "model_execution": self.model_execution,
            "diagnostic_state_settled": self.diagnostic_state_settled,
        }


@dataclass(frozen=True)
class NcpOriginalImportArtifact:
    """Exact immutable NCP bytes plus support-data provenance metadata."""

    artifact_id: str
    original_bytes: bytes
    sha256: str
    size_bytes: int
    media_type: str
    encoding: str
    source_reference: str
    source_identity: SourceIdentity
    artifact_reference: ArtifactReference
    artifact_type: str = NCP_IMPORT_ARTIFACT_TYPE
    support_data_only: bool = True
    candidate_truth: bool = False

    @property
    def original_text(self) -> str:
        return self.original_bytes.decode(self.encoding)

    def to_dict(self) -> dict[str, object]:
        """Return provenance metadata without duplicating source content."""

        return {
            "artifact_id": self.artifact_id,
            "artifact_type": self.artifact_type,
            "sha256": self.sha256,
            "hash_algorithm": "sha256",
            "size_bytes": self.size_bytes,
            "media_type": self.media_type,
            "encoding": self.encoding,
            "source_reference": self.source_reference,
            "source_identity": self.source_identity.to_dict(),
            "analysis_run_artifact_reference": self.artifact_reference.to_dict(),
            "original_bytes_preserved": True,
            "support_data_only": self.support_data_only,
            "candidate_truth": self.candidate_truth,
        }


@dataclass(frozen=True)
class NcpImportValidationResult:
    """Deterministic successful validation result; invalid input raises."""

    validation_id: str
    project_id: str
    story_id: str
    artifact: NcpOriginalImportArtifact
    external_narrative_statuses: tuple[NcpExternalStatusMetadata, ...]
    preserved_uninterpreted_top_level_pointers: tuple[str, ...]
    safety_boundary: NcpImportSafetyBoundary
    validation_hash: str
    contract_version: str = NCP_IMPORT_CONTRACT_VERSION
    ncp_schema_version: str = SUPPORTED_NCP_SCHEMA_VERSION
    app_mapping_version: str = NCP_APP_MAPPING_VERSION
    validation_outcome: str = "valid"
    unknown_field_policy: str = NCP_UNKNOWN_FIELD_POLICY

    def _hash_material(self) -> dict[str, object]:
        return {
            "contract_version": self.contract_version,
            "project_id": self.project_id,
            "story_id": self.story_id,
            "artifact": self.artifact.to_dict(),
            "ncp_schema_version": self.ncp_schema_version,
            "app_mapping_version": self.app_mapping_version,
            "validation_outcome": self.validation_outcome,
            "unknown_field_policy": self.unknown_field_policy,
            "preserved_uninterpreted_top_level_pointers": list(
                self.preserved_uninterpreted_top_level_pointers
            ),
            "external_narrative_statuses": [
                item.to_dict() for item in self.external_narrative_statuses
            ],
            "safety_boundary": self.safety_boundary.to_dict(),
        }

    def to_dict(self) -> dict[str, object]:
        value = self._hash_material()
        value["validation_id"] = self.validation_id
        value["validation_hash"] = self.validation_hash
        return value


def compute_ncp_import_validation_hash(record: Mapping[str, object]) -> str:
    """Hash a serialized result while excluding its derived identity fields."""

    material = dict(record)
    material.pop("validation_id", None)
    material.pop("validation_hash", None)
    return hashlib.sha256(_canonical_json_bytes(material)).hexdigest()


def validate_ncp_import_validation_record(record: object) -> dict[str, object]:
    """Verify the closed serialized result and its tamper-evident hash."""

    required_fields = {
        "contract_version",
        "project_id",
        "story_id",
        "artifact",
        "ncp_schema_version",
        "app_mapping_version",
        "validation_outcome",
        "unknown_field_policy",
        "preserved_uninterpreted_top_level_pointers",
        "external_narrative_statuses",
        "safety_boundary",
        "validation_id",
        "validation_hash",
    }
    if not isinstance(record, dict) or set(record) != required_fields:
        raise NcpImportValidationError(
            "invalid_validation_record", "/", "validation record fields are not closed"
        )
    if record["contract_version"] != NCP_IMPORT_CONTRACT_VERSION:
        raise NcpImportValidationError(
            "unsupported_contract_version", "/contract_version", "unsupported contract"
        )
    if record["ncp_schema_version"] != SUPPORTED_NCP_SCHEMA_VERSION:
        raise NcpImportValidationError(
            "unsupported_schema_version", "/ncp_schema_version", "unsupported schema"
        )
    if record["app_mapping_version"] != NCP_APP_MAPPING_VERSION:
        raise NcpImportValidationError(
            "unsupported_mapping_version", "/app_mapping_version", "unsupported mapping"
        )
    if record["validation_outcome"] != "valid":
        raise NcpImportValidationError(
            "invalid_validation_outcome", "/validation_outcome", "outcome must be valid"
        )
    if record["unknown_field_policy"] != NCP_UNKNOWN_FIELD_POLICY:
        raise NcpImportValidationError(
            "weakened_unknown_field_policy",
            "/unknown_field_policy",
            "unknown fields must remain preserved and uninterpreted",
        )
    if record["safety_boundary"] != NcpImportSafetyBoundary().to_dict():
        raise NcpImportValidationError(
            "weakened_safety_boundary",
            "/safety_boundary",
            "validation cannot gain mutation, approval, runtime, or prose authority",
        )

    artifact = record["artifact"]
    if not isinstance(artifact, dict):
        raise NcpImportValidationError(
            "invalid_artifact_metadata", "/artifact", "artifact metadata must be an object"
        )
    expected_artifact_fields = {
        "artifact_id",
        "artifact_type",
        "sha256",
        "hash_algorithm",
        "size_bytes",
        "media_type",
        "encoding",
        "source_reference",
        "source_identity",
        "analysis_run_artifact_reference",
        "original_bytes_preserved",
        "support_data_only",
        "candidate_truth",
    }
    if set(artifact) != expected_artifact_fields:
        raise NcpImportValidationError(
            "invalid_artifact_metadata", "/artifact", "artifact metadata fields are not closed"
        )
    artifact_hash = artifact["sha256"]
    if (
        not isinstance(artifact_hash, str)
        or len(artifact_hash) != 64
        or any(character not in "0123456789abcdef" for character in artifact_hash)
        or artifact["artifact_id"] != f"ncp-import-{artifact_hash}"
        or artifact["artifact_type"] != NCP_IMPORT_ARTIFACT_TYPE
        or artifact["hash_algorithm"] != "sha256"
        or artifact["media_type"] != NCP_IMPORT_MEDIA_TYPE
        or artifact["encoding"] != "utf-8"
        or type(artifact["size_bytes"]) is not int
        or artifact["size_bytes"] <= 0
        or artifact["original_bytes_preserved"] is not True
        or artifact["support_data_only"] is not True
        or artifact["candidate_truth"] is not False
    ):
        raise NcpImportValidationError(
            "invalid_artifact_metadata",
            "/artifact",
            "artifact identity or support-data boundary is inconsistent",
        )
    source_identity = artifact["source_identity"]
    artifact_reference = artifact["analysis_run_artifact_reference"]
    if not isinstance(source_identity, dict) or not isinstance(artifact_reference, dict):
        raise NcpImportValidationError(
            "invalid_artifact_lineage",
            "/artifact/source_identity",
            "T002 artifact lineage must be explicit",
        )
    if (
        source_identity.get("project_id") != record["project_id"]
        or source_identity.get("source_document_type") != "imported_context"
        or source_identity.get("source_ownership") != "owner_selected_imported"
        or source_identity.get("content_hash") != artifact_hash
        or source_identity.get("source_document_version")
        != SUPPORTED_NCP_SCHEMA_VERSION
        or artifact_reference.get("artifact_id") != artifact["artifact_id"]
        or artifact_reference.get("availability") != "available"
        or artifact_reference.get("content_hash") != artifact_hash
        or artifact_reference.get("hash_algorithm") != "sha256"
        or artifact_reference.get("media_type") != NCP_IMPORT_MEDIA_TYPE
        or artifact_reference.get("source_snapshot_ids")
        != [source_identity.get("snapshot_id")]
    ):
        raise NcpImportValidationError(
            "invalid_artifact_lineage",
            "/artifact",
            "T002 source and manifest artifact identities disagree",
        )

    statuses = record["external_narrative_statuses"]
    if not isinstance(statuses, list) or not statuses:
        raise NcpImportValidationError(
            "invalid_external_status_metadata",
            "/external_narrative_statuses",
            "external status metadata must be non-empty",
        )
    for index, status in enumerate(statuses):
        if (
            not isinstance(status, dict)
            or set(status)
            != {
                "narrative_id",
                "json_pointer",
                "external_status",
                "status_present",
                "local_approval",
            }
            or status["local_approval"] is not False
            or type(status["status_present"]) is not bool
            or (
                status["status_present"]
                and status["external_status"] not in _EXTERNAL_NARRATIVE_STATUSES
            )
            or (
                not status["status_present"] and status["external_status"] is not None
            )
        ):
            raise NcpImportValidationError(
                "invalid_external_status_metadata",
                f"/external_narrative_statuses/{index}",
                "external status cannot imply local approval",
            )
    actual_hash = compute_ncp_import_validation_hash(record)
    expected_id = f"ncp-import-validation-{actual_hash[:32]}"
    if record["validation_hash"] != actual_hash or record["validation_id"] != expected_id:
        raise NcpImportValidationError(
            "validation_record_hash_mismatch",
            "/validation_hash",
            "validation metadata is not intact",
        )
    return json.loads(json.dumps(record, ensure_ascii=False))


def _parse_exact_json(original_bytes: bytes) -> tuple[str, dict[str, Any]]:
    try:
        original_text = original_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise NcpImportValidationError(
            "invalid_utf8", "/", "artifact must contain exact UTF-8 JSON"
        ) from exc
    try:
        parsed = json.loads(
            original_text,
            object_pairs_hook=_closed_json_object,
            parse_constant=_reject_json_constant,
        )
    except _DuplicateJsonKey as exc:
        raise NcpImportValidationError(
            "ambiguous_duplicate_key", "/", "JSON object contains a duplicate key"
        ) from exc
    except (json.JSONDecodeError, RecursionError, ValueError) as exc:
        raise NcpImportValidationError(
            "malformed_json", "/", "artifact is not bounded strict JSON"
        ) from exc
    if not isinstance(parsed, dict):
        raise NcpImportValidationError(
            "invalid_top_level", "/", "top-level JSON value must be an object"
        )
    return original_text, parsed


def _validate_ncp_document(
    parsed: Mapping[str, Any],
) -> tuple[str, tuple[NcpExternalStatusMetadata, ...], tuple[str, ...]]:
    unsafe_fields = sorted(
        field
        for field in parsed
        if field.casefold() in _FORBIDDEN_TOP_LEVEL_FIELDS
    )
    if unsafe_fields:
        pointer = f"/{_json_pointer_segment(unsafe_fields[0])}"
        raise NcpImportValidationError(
            "unsafe_local_authority_field",
            pointer,
            "NCP input cannot assert local approval, canon, or promotion state",
        )

    schema_version = _require_field(parsed, "schema_version", "")
    if schema_version != SUPPORTED_NCP_SCHEMA_VERSION:
        raise NcpImportValidationError(
            "unsupported_schema_version",
            "/schema_version",
            f"only NCP schema {SUPPORTED_NCP_SCHEMA_VERSION} is supported",
        )

    story = _require_field(parsed, "story", "")
    if not isinstance(story, dict):
        raise NcpImportValidationError(
            "invalid_required_field", "/story", "story must be an object"
        )
    story_id = _require_nonempty_string(
        _require_field(story, "id", "/story"), "/story/id"
    )
    narratives = _require_field(story, "narratives", "/story")
    if not isinstance(narratives, list) or not narratives:
        raise NcpImportValidationError(
            "invalid_required_field",
            "/story/narratives",
            "story.narratives must be a non-empty array",
        )

    statuses: list[NcpExternalStatusMetadata] = []
    narrative_ids: set[str] = set()
    for index, narrative in enumerate(narratives):
        pointer = f"/story/narratives/{index}"
        if not isinstance(narrative, dict):
            raise NcpImportValidationError(
                "invalid_required_field", pointer, "narrative must be an object"
            )
        narrative_id = _require_nonempty_string(
            _require_field(narrative, "id", pointer), f"{pointer}/id"
        )
        if narrative_id in narrative_ids:
            raise NcpImportValidationError(
                "ambiguous_narrative_id",
                f"{pointer}/id",
                "narrative IDs must be unique",
            )
        narrative_ids.add(narrative_id)
        status_present = "status" in narrative
        external_status = narrative.get("status")
        if status_present and external_status not in _EXTERNAL_NARRATIVE_STATUSES:
            raise NcpImportValidationError(
                "unsupported_external_status",
                f"{pointer}/status",
                "external status must be candidate, draft, complete, or omitted",
            )
        statuses.append(
            NcpExternalStatusMetadata(
                narrative_id=narrative_id,
                json_pointer=f"{pointer}/status",
                external_status=external_status if status_present else None,
                status_present=status_present,
            )
        )

    unknown_pointers = tuple(
        f"/{_json_pointer_segment(field)}"
        for field in sorted(set(parsed) - _KNOWN_TOP_LEVEL_FIELDS)
    )
    return story_id, tuple(statuses), unknown_pointers


def validate_ncp_import_artifact(
    artifact_content: bytes | str,
    *,
    project_id: str,
    source_reference: str,
    media_type: str = NCP_IMPORT_MEDIA_TYPE,
) -> NcpImportValidationResult:
    """Validate exact NCP JSON and return immutable, non-writing metadata.

    Invalid, unsupported, ambiguous, incomplete, or unsafe input raises
    :class:`NcpImportValidationError`.  No candidate or project-state API is
    accepted by this function, so validation necessarily precedes those
    later T010B+ concerns.
    """

    if isinstance(artifact_content, str):
        original_bytes = artifact_content.encode("utf-8")
    elif isinstance(artifact_content, bytes):
        original_bytes = artifact_content
    else:
        raise NcpImportValidationError(
            "invalid_artifact_type", "/", "artifact_content must be bytes or text"
        )
    if not original_bytes:
        raise NcpImportValidationError(
            "empty_artifact", "/", "artifact must not be empty"
        )
    if len(original_bytes) > MAX_NCP_IMPORT_BYTES:
        raise NcpImportValidationError(
            "artifact_too_large", "/", "artifact exceeds the bounded import limit"
        )
    if media_type != NCP_IMPORT_MEDIA_TYPE:
        raise NcpImportValidationError(
            "unsupported_media_type", "/", "only application/json is supported"
        )
    checked_source_reference = _validate_source_reference(source_reference)

    original_text, parsed = _parse_exact_json(original_bytes)
    story_id, statuses, unknown_pointers = _validate_ncp_document(parsed)

    content_hash = hashlib.sha256(original_bytes).hexdigest()
    artifact_id = f"ncp-import-{content_hash}"
    try:
        snapshot = build_exact_source_snapshot(
            project_id=project_id,
            source_document_type="imported_context",
            source_document_id=artifact_id,
            source_document_version=SUPPORTED_NCP_SCHEMA_VERSION,
            source_ownership="owner_selected_imported",
            source_content=original_text,
        )
    except SourceIdentityValidationError as exc:
        raise NcpImportValidationError(
            "invalid_project_identity", "/", "project_id is not a valid T002 identity"
        ) from exc

    artifact_reference = ArtifactReference(
        artifact_id=artifact_id,
        availability="available",
        source_snapshot_ids=(snapshot.identity.snapshot_id,),
        content_hash=content_hash,
        hash_algorithm="sha256",
        media_type=media_type,
    )
    artifact = NcpOriginalImportArtifact(
        artifact_id=artifact_id,
        original_bytes=original_bytes,
        sha256=content_hash,
        size_bytes=len(original_bytes),
        media_type=media_type,
        encoding="utf-8",
        source_reference=checked_source_reference,
        source_identity=snapshot.identity,
        artifact_reference=artifact_reference,
    )
    safety_boundary = NcpImportSafetyBoundary()
    provisional = NcpImportValidationResult(
        validation_id="pending",
        project_id=project_id,
        story_id=story_id,
        artifact=artifact,
        external_narrative_statuses=statuses,
        preserved_uninterpreted_top_level_pointers=unknown_pointers,
        safety_boundary=safety_boundary,
        validation_hash="pending",
    )
    validation_hash = hashlib.sha256(
        _canonical_json_bytes(provisional._hash_material())
    ).hexdigest()
    result = NcpImportValidationResult(
        validation_id=f"ncp-import-validation-{validation_hash[:32]}",
        project_id=project_id,
        story_id=story_id,
        artifact=artifact,
        external_narrative_statuses=statuses,
        preserved_uninterpreted_top_level_pointers=unknown_pointers,
        safety_boundary=safety_boundary,
        validation_hash=validation_hash,
    )
    validate_ncp_import_validation_record(result.to_dict())
    return result
