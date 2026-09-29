"""Pure read-only project diagnostic context contract.

This module shapes exact project sources and existing lineage into a bounded
input value for later T009 diagnostics. It performs no I/O, execution,
persistence, candidate creation, approval, promotion, or project mutation.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from typing import Any

from backend.story_knowledge.analysis_run_manifest import (
    AnalysisRunManifest,
    analysis_run_manifest_from_dict,
)
from backend.story_knowledge.approved_records import (
    ApprovedRecordMaterial,
    approved_record_material,
)
from backend.story_knowledge.evidence_ledger import validate_evidence_record_v1
from backend.story_knowledge.semantic_guardrails import SEMANTIC_CLASSIFICATIONS
from backend.story_knowledge.source_map import ExactSourceSnapshot, SourceIdentity


PROJECT_DIAGNOSTIC_CONTEXT_VERSION = "project-diagnostic-context.v1"
PROJECT_DIAGNOSTIC_SOURCE_VERSION = "project-diagnostic-source.v1"
APPROVED_CONTEXT_SNAPSHOT_VERSION = "project-approved-context-snapshot.v1"
DIAGNOSTIC_SUPPORT_REFERENCE_VERSION = "project-diagnostic-support-reference.v1"

SOURCE_ROLES = frozenset({"primary", "comparison", "reference"})
SUPPORT_KINDS = frozenset({"candidate", "diagnostic", "guardrail_annotation"})
SUPPORT_CLASSIFICATIONS = frozenset({*SEMANTIC_CLASSIFICATIONS, "unclassified"})
UNCERTAINTY_CLASSIFICATIONS = frozenset(
    {
        "provisional",
        "ambiguous",
        "conflicting",
        "author_intent_dependent",
        "insufficient_evidence",
    }
)

_SAFE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,255}\Z")
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_CONTEXT_POLICY = {
    "mode": "analysis_read_only",
    "source_boundary": "separate_exact_sources",
    "approved_context_boundary": "explicit_approved_records_only",
    "diagnostic_authority": "support_only_unsettled",
    "owner_control": "required",
    "mutation": "none",
    "prose_generation": "forbidden",
}


class ProjectDiagnosticContextValidationError(ValueError):
    """Raised when project diagnostic context is unsafe or unprovable."""


def _canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _fail(message: str, exc: Exception | None = None) -> None:
    error = ProjectDiagnosticContextValidationError(message)
    if exc is None:
        raise error
    raise error from exc


def _closed_object(
    value: Any,
    *,
    required: set[str],
    optional: set[str] = set(),
    label: str,
) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        _fail(f"{label} must be an object")
    item = dict(value)
    if set(item) - required - optional:
        _fail(f"{label} fields are not closed")
    if not required <= set(item):
        _fail(f"{label} is missing required fields")
    return item


def _safe_id(value: Any, label: str) -> str:
    if not isinstance(value, str) or not _SAFE_ID.fullmatch(value):
        _fail(f"{label} must be a safe identifier")
    return value


def _sha256(value: Any, label: str) -> str:
    if not isinstance(value, str) or not _SHA256.fullmatch(value):
        _fail(f"{label} must be a lowercase SHA-256 digest")
    return value


def _id_list(value: Any, label: str, *, non_empty: bool = True) -> list[str]:
    if not isinstance(value, list) or (non_empty and not value):
        qualifier = "a non-empty " if non_empty else "a "
        _fail(f"{label} must be {qualifier}list")
    checked = [_safe_id(item, label) for item in value]
    if len(checked) != len(set(checked)):
        _fail(f"{label} contains duplicates")
    return sorted(checked)


def _source_identity(value: Any) -> SourceIdentity:
    if not isinstance(value, Mapping):
        _fail("source identity must be an object")
    try:
        return SourceIdentity(**dict(value))
    except (TypeError, ValueError) as exc:
        _fail("invalid exact source identity", exc)


def build_project_diagnostic_source(
    source: ExactSourceSnapshot | SourceIdentity,
    *,
    source_role: str,
) -> dict[str, Any]:
    """Build one explicit source boundary without flattening adjacent sources."""

    if source_role not in SOURCE_ROLES:
        _fail("source_role is not allowed")
    if isinstance(source, ExactSourceSnapshot):
        value = {
            "schema_version": PROJECT_DIAGNOSTIC_SOURCE_VERSION,
            "source_role": source_role,
            "source_type": source.identity.source_document_type,
            "snapshot_kind": "exact_source_snapshot",
            "source_snapshot": source.to_dict(include_content=True),
        }
    elif isinstance(source, SourceIdentity):
        value = {
            "schema_version": PROJECT_DIAGNOSTIC_SOURCE_VERSION,
            "source_role": source_role,
            "source_type": source.source_document_type,
            "snapshot_kind": "source_identity_reference",
            "source_identity": source.to_dict(),
        }
    else:
        _fail("source must be an ExactSourceSnapshot or SourceIdentity")
    return _validate_source(value)[0]


def _validate_source(value: Any) -> tuple[dict[str, Any], SourceIdentity]:
    common = {
        "schema_version",
        "source_role",
        "source_type",
        "snapshot_kind",
    }
    if not isinstance(value, Mapping):
        _fail("diagnostic source must be an object")
    kind = value.get("snapshot_kind")
    if kind == "exact_source_snapshot":
        item = _closed_object(
            value,
            required=common | {"source_snapshot"},
            label="exact diagnostic source",
        )
        snapshot_value = _closed_object(
            item["source_snapshot"],
            required={
                "identity",
                "offsets",
                "character_length",
                "utf8_byte_length",
                "source_content",
            },
            label="exact source snapshot",
        )
        identity = _source_identity(snapshot_value["identity"])
        try:
            snapshot = ExactSourceSnapshot(
                identity=identity,
                source_content=snapshot_value["source_content"],
                char_offset_basis=snapshot_value["offsets"]["character"]["basis"],
                byte_offset_basis=snapshot_value["offsets"]["byte"]["basis"],
                line_offset_basis=snapshot_value["offsets"]["line"]["basis"],
                token_offset_basis=snapshot_value["offsets"]["token"]["basis"],
            )
        except (KeyError, TypeError, ValueError) as exc:
            _fail("invalid exact source snapshot", exc)
        if snapshot.to_dict(include_content=True) != snapshot_value:
            _fail("exact source snapshot metadata or hash mismatch")
    elif kind == "source_identity_reference":
        item = _closed_object(
            value,
            required=common | {"source_identity"},
            label="diagnostic source identity reference",
        )
        identity = _source_identity(item["source_identity"])
    else:
        _fail("snapshot_kind is not allowed")
    if item["schema_version"] != PROJECT_DIAGNOSTIC_SOURCE_VERSION:
        _fail("unsupported diagnostic source schema_version")
    if item["source_role"] not in SOURCE_ROLES:
        _fail("source_role is not allowed")
    if item["source_type"] != identity.source_document_type:
        _fail("source_type does not match exact source identity")
    return copy.deepcopy(item), identity


def build_approved_context_snapshot(
    approved_record: ApprovedRecordMaterial | Mapping[str, Any],
    *,
    source_snapshot_ids: Sequence[str],
    context_role: str = "reference",
) -> dict[str, Any]:
    """Snapshot only an existing explicitly approved record and its provenance."""

    try:
        material = (
            approved_record
            if isinstance(approved_record, ApprovedRecordMaterial)
            else approved_record_material(approved_record)
        )
    except (TypeError, ValueError) as exc:
        _fail("approved context requires a valid approved record", exc)
    if context_role not in SOURCE_ROLES:
        _fail("approved context_role is not allowed")
    snapshot_ids = _id_list(list(source_snapshot_ids), "source_snapshot_ids")
    basis = {
        "approved_record_hash": material.approved_record_hash,
        "source_snapshot_ids": snapshot_ids,
        "context_role": context_role,
    }
    value = {
        "schema_version": APPROVED_CONTEXT_SNAPSHOT_VERSION,
        "context_snapshot_id": (
            "approved-context-"
            + hashlib.sha256(_canonical_json_bytes(basis)).hexdigest()
        ),
        "context_role": context_role,
        "permission_basis": "existing_explicit_approved_record",
        "source_snapshot_ids": snapshot_ids,
        "approved_record_hash": material.approved_record_hash,
        "approved_record": material.record,
    }
    return _validate_approved_context_snapshot(value)[0]


def _validate_approved_context_snapshot(
    value: Any,
) -> tuple[dict[str, Any], set[str]]:
    item = _closed_object(
        value,
        required={
            "schema_version",
            "context_snapshot_id",
            "context_role",
            "permission_basis",
            "source_snapshot_ids",
            "approved_record_hash",
            "approved_record",
        },
        label="approved context snapshot",
    )
    if item["schema_version"] != APPROVED_CONTEXT_SNAPSHOT_VERSION:
        _fail("unsupported approved context snapshot schema_version")
    _safe_id(item["context_snapshot_id"], "context_snapshot_id")
    if item["context_role"] not in SOURCE_ROLES:
        _fail("approved context_role is not allowed")
    if item["permission_basis"] != "existing_explicit_approved_record":
        _fail("approved context lacks explicit permission basis")
    source_ids = _id_list(item["source_snapshot_ids"], "source_snapshot_ids")
    try:
        material = approved_record_material(item["approved_record"])
    except (TypeError, ValueError) as exc:
        _fail("approved context contains an invalid approved record", exc)
    if (
        _sha256(item["approved_record_hash"], "approved_record_hash")
        != material.approved_record_hash
    ):
        _fail("approved context record hash mismatch")
    if not material.record["provenance_refs"] or not material.record["evidence_refs"]:
        _fail("approved context requires evidence and provenance")
    basis = {
        "approved_record_hash": material.approved_record_hash,
        "source_snapshot_ids": source_ids,
        "context_role": item["context_role"],
    }
    expected_id = (
        "approved-context-" + hashlib.sha256(_canonical_json_bytes(basis)).hexdigest()
    )
    if item["context_snapshot_id"] != expected_id:
        _fail("approved context snapshot identity mismatch")
    normalized = copy.deepcopy(item)
    normalized["source_snapshot_ids"] = source_ids
    normalized["approved_record"] = material.record
    return normalized, set(source_ids)


def build_diagnostic_support_reference(
    *,
    support_reference_id: str,
    support_kind: str,
    source_snapshot_ids: Sequence[str],
    run_id: str,
    evidence_reference_ids: Sequence[str],
    provenance_reference_ids: Sequence[str],
    support_classification: str,
    uncertainty_classification: str,
) -> dict[str, Any]:
    value = {
        "schema_version": DIAGNOSTIC_SUPPORT_REFERENCE_VERSION,
        "support_reference_id": support_reference_id,
        "support_kind": support_kind,
        "source_snapshot_ids": list(source_snapshot_ids),
        "run_id": run_id,
        "evidence_reference_ids": list(evidence_reference_ids),
        "provenance_reference_ids": list(provenance_reference_ids),
        "support_classification": support_classification,
        "uncertainty_classification": uncertainty_classification,
        "authority": "support_only_unsettled",
        "read_only": True,
    }
    return _validate_support_reference(value)[0]


def _validate_support_reference(value: Any) -> tuple[dict[str, Any], set[str]]:
    item = _closed_object(
        value,
        required={
            "schema_version",
            "support_reference_id",
            "support_kind",
            "source_snapshot_ids",
            "run_id",
            "evidence_reference_ids",
            "provenance_reference_ids",
            "support_classification",
            "uncertainty_classification",
            "authority",
            "read_only",
        },
        label="diagnostic support reference",
    )
    if item["schema_version"] != DIAGNOSTIC_SUPPORT_REFERENCE_VERSION:
        _fail("unsupported diagnostic support schema_version")
    _safe_id(item["support_reference_id"], "support_reference_id")
    _safe_id(item["run_id"], "run_id")
    if item["support_kind"] not in SUPPORT_KINDS:
        _fail("support_kind is not allowed")
    if item["support_classification"] not in SUPPORT_CLASSIFICATIONS:
        _fail("support_classification is not allowed")
    if item["uncertainty_classification"] not in UNCERTAINTY_CLASSIFICATIONS:
        _fail("uncertainty_classification is not allowed")
    if item["authority"] != "support_only_unsettled" or item["read_only"] is not True:
        _fail("diagnostic support cannot settle project truth")
    source_ids = _id_list(item["source_snapshot_ids"], "source_snapshot_ids")
    evidence_ids = _id_list(item["evidence_reference_ids"], "evidence_reference_ids")
    provenance_ids = _id_list(
        item["provenance_reference_ids"], "provenance_reference_ids"
    )
    normalized = copy.deepcopy(item)
    normalized["source_snapshot_ids"] = source_ids
    normalized["evidence_reference_ids"] = evidence_ids
    normalized["provenance_reference_ids"] = provenance_ids
    return normalized, set(source_ids)


def _manifest(value: AnalysisRunManifest | Mapping[str, Any]) -> AnalysisRunManifest:
    if isinstance(value, AnalysisRunManifest):
        return value
    try:
        return analysis_run_manifest_from_dict(value)
    except (TypeError, ValueError, KeyError) as exc:
        _fail("invalid analysis run manifest", exc)


def build_project_diagnostic_context(
    *,
    project_id: str,
    sources: Sequence[Mapping[str, Any]],
    run_manifests: Sequence[AnalysisRunManifest | Mapping[str, Any]] = (),
    evidence_records: Sequence[Mapping[str, Any]] = (),
    approved_context_snapshots: Sequence[Mapping[str, Any]] = (),
    diagnostic_support_references: Sequence[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    """Build a deterministic, serializable T009A context value."""

    value = {
        "schema_version": PROJECT_DIAGNOSTIC_CONTEXT_VERSION,
        "project_id": project_id,
        "sources": [copy.deepcopy(dict(item)) for item in sources],
        "run_manifests": [_manifest(item).to_dict() for item in run_manifests],
        "evidence_records": [copy.deepcopy(dict(item)) for item in evidence_records],
        "approved_context_snapshots": [
            copy.deepcopy(dict(item)) for item in approved_context_snapshots
        ],
        "diagnostic_support_references": [
            copy.deepcopy(dict(item)) for item in diagnostic_support_references
        ],
        "context_policy": copy.deepcopy(_CONTEXT_POLICY),
    }
    return validate_project_diagnostic_context(value)


def validate_project_diagnostic_context(value: Any) -> dict[str, Any]:
    """Validate and normalize one closed, read-only project context value."""

    item = _closed_object(
        value,
        required={
            "schema_version",
            "project_id",
            "sources",
            "run_manifests",
            "evidence_records",
            "approved_context_snapshots",
            "diagnostic_support_references",
            "context_policy",
        },
        label="project diagnostic context",
    )
    if item["schema_version"] != PROJECT_DIAGNOSTIC_CONTEXT_VERSION:
        _fail("unsupported project diagnostic context schema_version")
    project_id = _safe_id(item["project_id"], "project_id")
    if item["context_policy"] != _CONTEXT_POLICY:
        _fail("project diagnostic context policy cannot be weakened")
    for field in (
        "sources",
        "run_manifests",
        "evidence_records",
        "approved_context_snapshots",
        "diagnostic_support_references",
    ):
        if not isinstance(item[field], list):
            _fail(f"{field} must be a list")
    if not item["sources"]:
        _fail("project diagnostic context requires at least one exact source")

    sources: list[dict[str, Any]] = []
    identities: dict[str, SourceIdentity] = {}
    logical_source_keys: set[tuple[Any, ...]] = set()
    for source_value in item["sources"]:
        source, identity = _validate_source(source_value)
        if identity.project_id != project_id:
            _fail("source project_id mismatch")
        if identity.snapshot_id in identities:
            _fail("duplicate source snapshot identity")
        logical_key = (
            identity.project_id,
            identity.source_document_type,
            identity.source_document_id,
            identity.source_document_version,
            identity.section_id,
            identity.chapter_id,
            identity.scene_id,
        )
        if logical_key in logical_source_keys:
            _fail("conflicting source identities require distinct source versions")
        identities[identity.snapshot_id] = identity
        logical_source_keys.add(logical_key)
        sources.append(source)
    source_ids = set(identities)

    manifests: list[dict[str, Any]] = []
    manifests_by_run: dict[str, AnalysisRunManifest] = {}
    for manifest_value in item["run_manifests"]:
        manifest = _manifest(manifest_value)
        if manifest.project_id != project_id:
            _fail("analysis run project_id mismatch")
        if manifest.run_id in manifests_by_run:
            _fail("duplicate analysis run identity")
        for identity in manifest.sources:
            expected = identities.get(identity.snapshot_id)
            if expected is None or expected != identity:
                _fail("analysis run source lineage is outside this context")
        manifests_by_run[manifest.run_id] = manifest
        manifests.append(manifest.to_dict())

    evidence: list[dict[str, Any]] = []
    evidence_ids: set[str] = set()
    for evidence_value in item["evidence_records"]:
        try:
            record = validate_evidence_record_v1(evidence_value)
        except (TypeError, ValueError) as exc:
            _fail("invalid evidence record", exc)
        if record["project_id"] != project_id:
            _fail("evidence project_id mismatch")
        run_manifest = manifests_by_run.get(record["run_id"])
        if run_manifest is None:
            _fail("evidence requires its analysis run manifest")
        evidence_identity = _source_identity(record["source_identity"])
        expected = identities.get(evidence_identity.snapshot_id)
        if expected is None or expected != evidence_identity:
            _fail("evidence source lineage is outside this context")
        artifact_by_id = {
            artifact.artifact_id: artifact
            for artifact in run_manifest.artifact_references
        }
        artifact = artifact_by_id.get(record["artifact_id"])
        if (
            artifact is None
            or evidence_identity.snapshot_id not in artifact.source_snapshot_ids
        ):
            _fail("evidence artifact lineage does not match its analysis run")
        operation_by_id = {
            operation.operation_id: operation
            for operation in run_manifest.operations
        }
        operation = operation_by_id.get(record["operation_id"])
        if operation is None or operation.adapter_id != record["adapter_id"]:
            _fail("evidence operation provenance does not match its analysis run")
        if record["output_id"] is not None:
            output_by_id = {
                output.output_id: output for output in run_manifest.outputs
            }
            output = output_by_id.get(record["output_id"])
            if (
                output is None
                or output.operation_id != record["operation_id"]
                or output.original_output_reference_id != record["artifact_id"]
                or evidence_identity.snapshot_id not in output.source_snapshot_ids
            ):
                _fail("evidence output lineage does not match its analysis run")
        if record["evidence_id"] in evidence_ids:
            _fail("duplicate evidence identity")
        evidence_ids.add(record["evidence_id"])
        evidence.append(record)

    approved_snapshots: list[dict[str, Any]] = []
    approved_ids: set[str] = set()
    for approved_value in item["approved_context_snapshots"]:
        approved, approved_source_ids = _validate_approved_context_snapshot(
            approved_value
        )
        if approved["approved_record"]["project_id"] != project_id:
            _fail("approved context project_id mismatch")
        if not approved_source_ids <= source_ids:
            _fail("approved context references an unknown source snapshot")
        approved_id = approved["context_snapshot_id"]
        if approved_id in approved_ids:
            _fail("duplicate approved context snapshot")
        approved_ids.add(approved_id)
        approved_snapshots.append(approved)

    support_refs: list[dict[str, Any]] = []
    support_ids: set[str] = set()
    for support_value in item["diagnostic_support_references"]:
        support, support_source_ids = _validate_support_reference(support_value)
        if not support_source_ids <= source_ids:
            _fail("diagnostic support references an unknown source snapshot")
        if support["run_id"] not in manifests_by_run:
            _fail("diagnostic support requires its analysis run manifest")
        if not set(support["evidence_reference_ids"]) <= evidence_ids:
            _fail("diagnostic support references unknown evidence")
        support_id = support["support_reference_id"]
        if support_id in support_ids:
            _fail("duplicate diagnostic support reference")
        support_ids.add(support_id)
        support_refs.append(support)

    def source_sort_key(source: dict[str, Any]) -> tuple[str, str]:
        if "source_snapshot" in source:
            snapshot_id = source["source_snapshot"]["identity"]["snapshot_id"]
        else:
            snapshot_id = source["source_identity"]["snapshot_id"]
        return snapshot_id, source["source_role"]

    return {
        "schema_version": PROJECT_DIAGNOSTIC_CONTEXT_VERSION,
        "project_id": project_id,
        "sources": sorted(sources, key=source_sort_key),
        "run_manifests": sorted(manifests, key=lambda manifest: manifest["run_id"]),
        "evidence_records": sorted(evidence, key=lambda record: record["evidence_id"]),
        "approved_context_snapshots": sorted(
            approved_snapshots, key=lambda snapshot: snapshot["context_snapshot_id"]
        ),
        "diagnostic_support_references": sorted(
            support_refs, key=lambda support: support["support_reference_id"]
        ),
        "context_policy": copy.deepcopy(_CONTEXT_POLICY),
    }


__all__ = (
    "PROJECT_DIAGNOSTIC_CONTEXT_VERSION",
    "PROJECT_DIAGNOSTIC_SOURCE_VERSION",
    "APPROVED_CONTEXT_SNAPSHOT_VERSION",
    "DIAGNOSTIC_SUPPORT_REFERENCE_VERSION",
    "SOURCE_ROLES",
    "SUPPORT_KINDS",
    "SUPPORT_CLASSIFICATIONS",
    "UNCERTAINTY_CLASSIFICATIONS",
    "ProjectDiagnosticContextValidationError",
    "build_project_diagnostic_source",
    "build_approved_context_snapshot",
    "build_diagnostic_support_reference",
    "build_project_diagnostic_context",
    "validate_project_diagnostic_context",
)
