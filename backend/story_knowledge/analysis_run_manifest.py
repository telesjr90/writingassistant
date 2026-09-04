"""Pure immutable identity and lineage contract for one analysis run.

The values in this module do not execute adapters, perform I/O, persist
artifacts or candidates, mutate projects, or control live execution.  They
describe a finalized run declaration and its attributable result lineage.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass
import json
import math
from pathlib import PurePosixPath, PureWindowsPath
import re
from typing import Any

from backend.story_knowledge.source_map import SourceIdentity


ANALYSIS_RUN_MANIFEST_CONTRACT_VERSION = "analysis-run-manifest.v1"

ADAPTER_RESULT_STATES = frozenset(
    {"succeeded", "empty", "skipped", "unavailable", "failed_closed", "error"}
)

ADAPTER_IDENTITIES = frozenset(
    {
        "ollama_model",
        "story_check",
        "booknlp",
        "spacy",
        "ncp",
        "subtxt",
        "subtxt_informed_rubric",
        "dramatica_flow_informed_rubric",
        "dramatica_flow",
        "deterministic_fallback",
    }
)

DEPENDENCY_CLASSES = frozenset(
    {
        "owner_selected_source",
        "imported_artifact",
        "raw_extraction_evidence",
        "normalized_evidence",
        "diagnostic_candidate_finding",
        "guardrail_annotation",
        "fused_finding",
        "approved_context",
        "gateway_input_output",
    }
)

PROVENANCE_AVAILABILITY = frozenset({"available", "unavailable", "unknown"})
IMPLEMENTATION_KINDS = frozenset(
    {"official_external", "app_owned", "fixture_mock", "fallback", "unknown"}
)
OUTPUT_DISPOSITIONS = frozenset(
    {"validated", "rejected", "quarantined", "unverified"}
)
COVERAGE_CLASSIFICATIONS = frozenset({"complete", "partial", "degraded"})
CONTRIBUTOR_COVERAGE = frozenset({"complete", "partial", "none"})

_SAFE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,255}\Z")
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_BLOCKED_SEMANTIC_KEYS = frozenset(
    {
        "generated_prose",
        "generated_text",
        "draft_prose",
        "rewritten_text",
        "continuation",
        "outline",
        "canon",
        "canonical_truth",
        "approved_truth",
        "automatic_truth",
        "promotion",
        "apply_promotion",
        "mutate_memory",
        "write_to_canon",
        "candidate_records",
        "persist_candidates",
        "storage_path",
        "artifact_path",
    }
)


class AnalysisRunManifestValidationError(ValueError):
    """Raised when a run manifest cannot be reproduced or attributed safely."""


def _require_string(value: object, label: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str):
        raise AnalysisRunManifestValidationError(f"{label} must be a string")
    if not allow_empty and not value:
        raise AnalysisRunManifestValidationError(f"{label} must not be empty")
    if "\x00" in value:
        raise AnalysisRunManifestValidationError(f"{label} must not contain NUL")
    return value


def _safe_id(value: object, label: str) -> str:
    identifier = _require_string(value, label)
    if not _SAFE_ID.fullmatch(identifier):
        raise AnalysisRunManifestValidationError(f"{label} must be a path-safe ID")
    if ".." in identifier:
        raise AnalysisRunManifestValidationError(f"{label} must be a path-safe ID")
    if PurePosixPath(identifier).is_absolute() or PureWindowsPath(identifier).is_absolute():
        raise AnalysisRunManifestValidationError(f"{label} must not be an absolute path")
    return identifier


def _optional_string(value: object | None, label: str) -> str | None:
    if value is None:
        return None
    return _require_string(value, label)


def _check_semantic_key(key: object) -> str:
    checked = _require_string(key, "configuration key")
    if checked.casefold() in _BLOCKED_SEMANTIC_KEYS:
        raise AnalysisRunManifestValidationError(
            f"configuration key is outside the analysis-only boundary: {checked}"
        )
    return checked


def _freeze_json(value: object) -> object:
    if value is None or type(value) in (bool, int, str):
        return value
    if type(value) is float:
        if not math.isfinite(value):
            raise AnalysisRunManifestValidationError(
                "configuration float values must be finite"
            )
        return value
    if isinstance(value, Mapping):
        return FrozenJsonObject.from_mapping(value)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return tuple(_freeze_json(item) for item in value)
    raise AnalysisRunManifestValidationError("configuration must contain JSON values only")


def _thaw_json(value: object) -> object:
    if isinstance(value, FrozenJsonObject):
        return value.to_dict()
    if isinstance(value, tuple):
        return [_thaw_json(item) for item in value]
    return value


@dataclass(frozen=True)
class FrozenJsonObject(Mapping[str, object]):
    """Recursively immutable, key-sorted JSON object."""

    _items: tuple[tuple[str, object], ...]

    @classmethod
    def from_mapping(cls, value: Mapping[str, object]) -> "FrozenJsonObject":
        items = []
        for key in sorted(value):
            checked_key = _check_semantic_key(key)
            items.append((checked_key, _freeze_json(value[key])))
        return cls(tuple(items))

    def __getitem__(self, key: str) -> object:
        for item_key, value in self._items:
            if item_key == key:
                return value
        raise KeyError(key)

    def __iter__(self) -> Iterator[str]:
        return (key for key, _ in self._items)

    def __len__(self) -> int:
        return len(self._items)

    def to_dict(self) -> dict[str, object]:
        return {key: _thaw_json(value) for key, value in self._items}


def _frozen_mapping(value: object, label: str) -> FrozenJsonObject:
    if isinstance(value, FrozenJsonObject):
        return value
    if not isinstance(value, Mapping):
        raise AnalysisRunManifestValidationError(f"{label} must be a mapping")
    return FrozenJsonObject.from_mapping(value)


@dataclass(frozen=True)
class ProvenanceComponent:
    """One actual tool/runtime/provider/model identity or explicit absence."""

    availability: str
    name: str | None = None
    version: str | None = None

    def __post_init__(self) -> None:
        if self.availability not in PROVENANCE_AVAILABILITY:
            raise AnalysisRunManifestValidationError("invalid provenance availability")
        name = _optional_string(self.name, "provenance name")
        version = _optional_string(self.version, "provenance version")
        if name is not None and (
            PurePosixPath(name).is_absolute() or PureWindowsPath(name).is_absolute()
        ):
            raise AnalysisRunManifestValidationError(
                "provenance identity must not be an absolute path"
            )
        if self.availability == "available" and name is None:
            raise AnalysisRunManifestValidationError(
                "available provenance requires its actual name"
            )
        if self.availability != "available" and (name is not None or version is not None):
            raise AnalysisRunManifestValidationError(
                "unavailable/unknown provenance must not fabricate identity values"
            )
        if version is not None and name is None:
            raise AnalysisRunManifestValidationError("provenance version requires a name")

    def to_dict(self) -> dict[str, object]:
        return {
            "availability": self.availability,
            "name": self.name,
            "version": self.version,
        }


@dataclass(frozen=True)
class AdapterProvenance:
    adapter_id: str
    operation_id: str
    user_facing_label: str
    implementation_kind: str
    tool: ProvenanceComponent
    runtime: ProvenanceComponent
    provider: ProvenanceComponent
    model: ProvenanceComponent

    def __post_init__(self) -> None:
        if self.adapter_id not in ADAPTER_IDENTITIES:
            raise AnalysisRunManifestValidationError("unknown adapter identity")
        _safe_id(self.operation_id, "operation_id")
        _require_string(self.user_facing_label, "user_facing_label")
        if self.implementation_kind not in IMPLEMENTATION_KINDS:
            raise AnalysisRunManifestValidationError("invalid implementation_kind")
        for field_name in ("tool", "runtime", "provider", "model"):
            if not isinstance(getattr(self, field_name), ProvenanceComponent):
                raise AnalysisRunManifestValidationError(
                    f"{field_name} must be a ProvenanceComponent"
                )
        if self.adapter_id == "deterministic_fallback" and self.implementation_kind != "fallback":
            raise AnalysisRunManifestValidationError(
                "deterministic_fallback must remain identified as fallback"
            )
        if self.implementation_kind == "fallback" and self.adapter_id != "deterministic_fallback":
            raise AnalysisRunManifestValidationError(
                "fallback implementation_kind is reserved for deterministic_fallback"
            )

    def to_dict(self) -> dict[str, object]:
        return {
            "adapter_id": self.adapter_id,
            "operation_id": self.operation_id,
            "user_facing_label": self.user_facing_label,
            "implementation_kind": self.implementation_kind,
            "tool": self.tool.to_dict(),
            "runtime": self.runtime.to_dict(),
            "provider": self.provider.to_dict(),
            "model": self.model.to_dict(),
        }


@dataclass(frozen=True)
class OperationDeclaration:
    operation_id: str
    adapter_id: str
    consumes: tuple[str, ...]
    produces: tuple[str, ...]
    configuration: FrozenJsonObject | Mapping[str, object]
    feature_flags: FrozenJsonObject | Mapping[str, object]

    def __post_init__(self) -> None:
        _safe_id(self.operation_id, "operation_id")
        if self.adapter_id not in ADAPTER_IDENTITIES:
            raise AnalysisRunManifestValidationError("unknown adapter identity")
        for label, values in (("consumes", self.consumes), ("produces", self.produces)):
            if not isinstance(values, tuple) or not values:
                raise AnalysisRunManifestValidationError(f"{label} must be a non-empty tuple")
            if len(set(values)) != len(values) or any(
                value not in DEPENDENCY_CLASSES for value in values
            ):
                raise AnalysisRunManifestValidationError(f"{label} has invalid dependency classes")
        object.__setattr__(self, "configuration", _frozen_mapping(self.configuration, "configuration"))
        object.__setattr__(self, "feature_flags", _frozen_mapping(self.feature_flags, "feature_flags"))

    def to_dict(self) -> dict[str, object]:
        return {
            "operation_id": self.operation_id,
            "adapter_id": self.adapter_id,
            "consumes": list(self.consumes),
            "produces": list(self.produces),
            "configuration": self.configuration.to_dict(),
            "feature_flags": self.feature_flags.to_dict(),
        }


@dataclass(frozen=True)
class DependencyEdge:
    producer_operation_id: str
    consumer_operation_id: str
    dependency_class: str

    def __post_init__(self) -> None:
        _safe_id(self.producer_operation_id, "producer_operation_id")
        _safe_id(self.consumer_operation_id, "consumer_operation_id")
        if self.producer_operation_id == self.consumer_operation_id:
            raise AnalysisRunManifestValidationError("operation cannot depend on itself")
        if self.dependency_class not in DEPENDENCY_CLASSES:
            raise AnalysisRunManifestValidationError("unknown dependency_class")

    def to_dict(self) -> dict[str, str]:
        return {
            "producer_operation_id": self.producer_operation_id,
            "consumer_operation_id": self.consumer_operation_id,
            "dependency_class": self.dependency_class,
        }


@dataclass(frozen=True)
class ArtifactReference:
    """Storage-independent identity boundary for T003 to implement later."""

    artifact_id: str
    availability: str
    source_snapshot_ids: tuple[str, ...]
    content_hash: str | None = None
    hash_algorithm: str | None = None
    media_type: str | None = None

    def __post_init__(self) -> None:
        _safe_id(self.artifact_id, "artifact_id")
        if self.availability not in PROVENANCE_AVAILABILITY:
            raise AnalysisRunManifestValidationError("invalid artifact availability")
        if not isinstance(self.source_snapshot_ids, tuple) or not self.source_snapshot_ids:
            raise AnalysisRunManifestValidationError(
                "artifact source_snapshot_ids must be a non-empty tuple"
            )
        for snapshot_id in self.source_snapshot_ids:
            _safe_id(snapshot_id, "source_snapshot_id")
        if len(set(self.source_snapshot_ids)) != len(self.source_snapshot_ids):
            raise AnalysisRunManifestValidationError("duplicate artifact source snapshot")
        if self.content_hash is not None and not _SHA256.fullmatch(self.content_hash):
            raise AnalysisRunManifestValidationError("artifact content_hash must be SHA-256")
        if self.content_hash is None and self.hash_algorithm is not None:
            raise AnalysisRunManifestValidationError("hash_algorithm requires content_hash")
        if self.content_hash is not None and self.hash_algorithm != "sha256":
            raise AnalysisRunManifestValidationError("artifact hash_algorithm must be sha256")
        if self.availability == "available" and self.content_hash is None:
            raise AnalysisRunManifestValidationError(
                "available artifact reference requires exact content_hash"
            )
        _optional_string(self.media_type, "media_type")

    def to_dict(self) -> dict[str, object]:
        return {
            "artifact_id": self.artifact_id,
            "availability": self.availability,
            "source_snapshot_ids": list(self.source_snapshot_ids),
            "content_hash": self.content_hash,
            "hash_algorithm": self.hash_algorithm,
            "media_type": self.media_type,
        }


@dataclass(frozen=True)
class TransformationLineage:
    transformation_id: str
    operation_id: str
    transformation_kind: str
    transformation_version: str
    input_reference_ids: tuple[str, ...]
    output_reference_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        _safe_id(self.transformation_id, "transformation_id")
        _safe_id(self.operation_id, "operation_id")
        _require_string(self.transformation_kind, "transformation_kind")
        _require_string(self.transformation_version, "transformation_version")
        for label, values in (
            ("input_reference_ids", self.input_reference_ids),
            ("output_reference_ids", self.output_reference_ids),
        ):
            if not isinstance(values, tuple) or not values:
                raise AnalysisRunManifestValidationError(f"{label} must be non-empty")
            for reference_id in values:
                _safe_id(reference_id, label)

    def to_dict(self) -> dict[str, object]:
        return {
            "transformation_id": self.transformation_id,
            "operation_id": self.operation_id,
            "transformation_kind": self.transformation_kind,
            "transformation_version": self.transformation_version,
            "input_reference_ids": list(self.input_reference_ids),
            "output_reference_ids": list(self.output_reference_ids),
        }


@dataclass(frozen=True)
class OutputLineage:
    output_id: str
    operation_id: str
    source_snapshot_ids: tuple[str, ...]
    disposition: str
    original_output_reference_id: str
    evidence_reference_ids: tuple[str, ...] = ()
    transformation_ids: tuple[str, ...] = ()
    verification_outcome: str | None = None
    guardrail_outcome: str | None = None
    missing_evidence_reason: str | None = None

    def __post_init__(self) -> None:
        _safe_id(self.output_id, "output_id")
        _safe_id(self.operation_id, "operation_id")
        _safe_id(self.original_output_reference_id, "original_output_reference_id")
        if self.disposition not in OUTPUT_DISPOSITIONS:
            raise AnalysisRunManifestValidationError("invalid output disposition")
        if not isinstance(self.source_snapshot_ids, tuple) or not self.source_snapshot_ids:
            raise AnalysisRunManifestValidationError(
                "output source_snapshot_ids must be non-empty"
            )
        for values, label in (
            (self.source_snapshot_ids, "source_snapshot_id"),
            (self.evidence_reference_ids, "evidence_reference_id"),
            (self.transformation_ids, "transformation_id"),
        ):
            for value in values:
                _safe_id(value, label)
        for field_name in (
            "verification_outcome",
            "guardrail_outcome",
            "missing_evidence_reason",
        ):
            _optional_string(getattr(self, field_name), field_name)
        if self.disposition in {"rejected", "quarantined", "unverified"} and not (
            self.verification_outcome
            or self.guardrail_outcome
            or self.missing_evidence_reason
        ):
            raise AnalysisRunManifestValidationError(
                "unsuccessful/unverified output requires an attributable reason"
            )

    def to_dict(self) -> dict[str, object]:
        return {
            "output_id": self.output_id,
            "operation_id": self.operation_id,
            "source_snapshot_ids": list(self.source_snapshot_ids),
            "disposition": self.disposition,
            "original_output_reference_id": self.original_output_reference_id,
            "evidence_reference_ids": list(self.evidence_reference_ids),
            "transformation_ids": list(self.transformation_ids),
            "verification_outcome": self.verification_outcome,
            "guardrail_outcome": self.guardrail_outcome,
            "missing_evidence_reason": self.missing_evidence_reason,
        }


@dataclass(frozen=True)
class ContributorLineage:
    operation_id: str
    adapter_id: str
    source_snapshot_ids: tuple[str, ...]
    result_state: str
    coverage: str
    explanation: str
    provenance: AdapterProvenance
    output_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _safe_id(self.operation_id, "operation_id")
        if self.adapter_id not in ADAPTER_IDENTITIES:
            raise AnalysisRunManifestValidationError("unknown adapter identity")
        if self.result_state not in ADAPTER_RESULT_STATES:
            raise AnalysisRunManifestValidationError("undeclared adapter result state")
        if self.coverage not in CONTRIBUTOR_COVERAGE:
            raise AnalysisRunManifestValidationError("invalid contributor coverage")
        _require_string(self.explanation, "contributor explanation")
        if not isinstance(self.provenance, AdapterProvenance):
            raise AnalysisRunManifestValidationError("invalid contributor provenance")
        if self.provenance.adapter_id != self.adapter_id:
            raise AnalysisRunManifestValidationError(
                "contributor provenance cannot impersonate another adapter"
            )
        if self.provenance.operation_id != self.operation_id:
            raise AnalysisRunManifestValidationError("contributor operation mismatch")
        if not self.source_snapshot_ids:
            raise AnalysisRunManifestValidationError(
                "contributor source_snapshot_ids must be non-empty"
            )
        for values, label in (
            (self.source_snapshot_ids, "source_snapshot_id"),
            (self.output_ids, "output_id"),
        ):
            for value in values:
                _safe_id(value, label)

    def to_dict(self) -> dict[str, object]:
        return {
            "operation_id": self.operation_id,
            "adapter_id": self.adapter_id,
            "source_snapshot_ids": list(self.source_snapshot_ids),
            "result_state": self.result_state,
            "coverage": self.coverage,
            "explanation": self.explanation,
            "provenance": self.provenance.to_dict(),
            "output_ids": list(self.output_ids),
        }


def _assert_unique(values: Sequence[object], key_name: str) -> None:
    keys = [getattr(value, key_name) for value in values]
    if len(keys) != len(set(keys)):
        raise AnalysisRunManifestValidationError(f"duplicate {key_name}")


def _validate_acyclic(operation_ids: set[str], edges: tuple[DependencyEdge, ...]) -> None:
    graph = {operation_id: [] for operation_id in operation_ids}
    for edge in edges:
        if edge.producer_operation_id not in graph or edge.consumer_operation_id not in graph:
            raise AnalysisRunManifestValidationError("dependency references unknown operation")
        graph[edge.producer_operation_id].append(edge.consumer_operation_id)
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(operation_id: str) -> None:
        if operation_id in visiting:
            raise AnalysisRunManifestValidationError("dependency graph contains a cycle")
        if operation_id in visited:
            return
        visiting.add(operation_id)
        for consumer in graph[operation_id]:
            visit(consumer)
        visiting.remove(operation_id)
        visited.add(operation_id)

    for operation_id in sorted(graph):
        visit(operation_id)


@dataclass(frozen=True)
class AnalysisRunManifest:
    run_id: str
    project_id: str
    sources: tuple[SourceIdentity, ...]
    operations: tuple[OperationDeclaration, ...]
    dependency_graph: tuple[DependencyEdge, ...]
    contributors: tuple[ContributorLineage, ...]
    artifact_references: tuple[ArtifactReference, ...]
    outputs: tuple[OutputLineage, ...]
    transformations: tuple[TransformationLineage, ...]
    coverage: str
    created_at: str
    finalized_at: str
    configuration: FrozenJsonObject | Mapping[str, object]
    feature_flags: FrozenJsonObject | Mapping[str, object]
    contract_version: str = ANALYSIS_RUN_MANIFEST_CONTRACT_VERSION

    def __post_init__(self) -> None:
        _safe_id(self.run_id, "run_id")
        _safe_id(self.project_id, "project_id")
        if self.contract_version != ANALYSIS_RUN_MANIFEST_CONTRACT_VERSION:
            raise AnalysisRunManifestValidationError("unsupported manifest contract_version")
        if self.coverage not in COVERAGE_CLASSIFICATIONS:
            raise AnalysisRunManifestValidationError("invalid run coverage")
        _require_string(self.created_at, "created_at")
        _require_string(self.finalized_at, "finalized_at")
        if not self.sources or not self.operations or not self.contributors:
            raise AnalysisRunManifestValidationError(
                "manifest requires sources, operations, and contributor lineage"
            )
        for source in self.sources:
            if not isinstance(source, SourceIdentity):
                raise AnalysisRunManifestValidationError("invalid source identity")
            if source.project_id != self.project_id:
                raise AnalysisRunManifestValidationError("source project_id mismatch")
        source_keys = [
            (
                source.project_id,
                source.source_document_type,
                source.source_document_id,
                source.source_document_version,
                source.section_id,
                source.chapter_id,
                source.scene_id,
            )
            for source in self.sources
        ]
        if len(source_keys) != len(set(source_keys)):
            raise AnalysisRunManifestValidationError(
                "ambiguous duplicate source document identity"
            )
        _assert_unique(self.sources, "snapshot_id")
        _assert_unique(self.operations, "operation_id")
        _assert_unique(self.contributors, "operation_id")
        _assert_unique(self.artifact_references, "artifact_id")
        _assert_unique(self.outputs, "output_id")
        _assert_unique(self.transformations, "transformation_id")
        if len(self.dependency_graph) != len(set(self.dependency_graph)):
            raise AnalysisRunManifestValidationError("duplicate dependency edge")

        operation_by_id = {operation.operation_id: operation for operation in self.operations}
        contributor_by_operation = {
            contributor.operation_id: contributor for contributor in self.contributors
        }
        if set(operation_by_id) != set(contributor_by_operation):
            raise AnalysisRunManifestValidationError(
                "every declared operation requires contributor lineage"
            )
        snapshot_ids = {source.snapshot_id for source in self.sources}
        artifact_ids = {reference.artifact_id for reference in self.artifact_references}
        output_ids = {output.output_id for output in self.outputs}
        transformation_ids = {
            transformation.transformation_id for transformation in self.transformations
        }
        for operation in self.operations:
            if operation.adapter_id not in ADAPTER_IDENTITIES:
                raise AnalysisRunManifestValidationError("unknown operation adapter")
        for contributor in self.contributors:
            operation = operation_by_id.get(contributor.operation_id)
            if operation is None or operation.adapter_id != contributor.adapter_id:
                raise AnalysisRunManifestValidationError(
                    "contributor does not match declared operation"
                )
            if not set(contributor.source_snapshot_ids) <= snapshot_ids:
                raise AnalysisRunManifestValidationError(
                    "contributor references an unknown source snapshot"
                )
            if not set(contributor.output_ids) <= output_ids:
                raise AnalysisRunManifestValidationError(
                    "contributor references an unknown output"
                )
            claimed_outputs = [
                output
                for output in self.outputs
                if output.output_id in contributor.output_ids
            ]
            if any(output.operation_id != contributor.operation_id for output in claimed_outputs):
                raise AnalysisRunManifestValidationError(
                    "contributor cannot claim another operation's output"
                )
            if contributor.result_state in {"empty", "skipped", "unavailable"} and (
                contributor.output_ids
            ):
                raise AnalysisRunManifestValidationError(
                    "non-producing contributor state cannot claim outputs"
                )
            if contributor.result_state in {"failed_closed", "error"} and any(
                output.disposition == "validated" for output in claimed_outputs
            ):
                raise AnalysisRunManifestValidationError(
                    "failed contributor cannot claim validated output"
                )
        claimed_output_ids = {
            output_id
            for contributor in self.contributors
            for output_id in contributor.output_ids
        }
        if claimed_output_ids != output_ids:
            raise AnalysisRunManifestValidationError(
                "every output requires exactly attributable contributor lineage"
            )
        for reference in self.artifact_references:
            if not set(reference.source_snapshot_ids) <= snapshot_ids:
                raise AnalysisRunManifestValidationError(
                    "artifact references an unknown source snapshot"
                )
        for output in self.outputs:
            if output.operation_id not in operation_by_id:
                raise AnalysisRunManifestValidationError("output references unknown operation")
            if not set(output.source_snapshot_ids) <= snapshot_ids:
                raise AnalysisRunManifestValidationError(
                    "output references an unknown source snapshot"
                )
            if output.original_output_reference_id not in artifact_ids:
                raise AnalysisRunManifestValidationError(
                    "output requires a declared original artifact reference"
                )
            artifact = next(
                reference
                for reference in self.artifact_references
                if reference.artifact_id == output.original_output_reference_id
            )
            if not set(output.source_snapshot_ids) <= set(artifact.source_snapshot_ids):
                raise AnalysisRunManifestValidationError(
                    "output source lineage does not match its original artifact"
                )
            if not set(output.transformation_ids) <= transformation_ids:
                raise AnalysisRunManifestValidationError(
                    "output references an unknown transformation"
                )
        reference_ids = artifact_ids | output_ids
        for transformation in self.transformations:
            if transformation.operation_id not in operation_by_id:
                raise AnalysisRunManifestValidationError(
                    "transformation references unknown operation"
                )
            if not set(transformation.input_reference_ids) <= reference_ids:
                raise AnalysisRunManifestValidationError(
                    "transformation input reference is unknown"
                )
            if not set(transformation.output_reference_ids) <= reference_ids:
                raise AnalysisRunManifestValidationError(
                    "transformation output reference is unknown"
                )
        _validate_acyclic(set(operation_by_id), self.dependency_graph)
        for edge in self.dependency_graph:
            producer = operation_by_id[edge.producer_operation_id]
            consumer = operation_by_id[edge.consumer_operation_id]
            if edge.dependency_class not in producer.produces:
                raise AnalysisRunManifestValidationError(
                    "dependency class is not produced by its producer"
                )
            if edge.dependency_class not in consumer.consumes:
                raise AnalysisRunManifestValidationError(
                    "dependency class is not consumed by its consumer"
                )
        if self.coverage == "complete" and any(
            contributor.result_state not in {"succeeded", "empty"}
            or contributor.coverage != "complete"
            for contributor in self.contributors
        ):
            raise AnalysisRunManifestValidationError(
                "complete run coverage cannot hide partial or unsuccessful contributors"
            )

        object.__setattr__(self, "configuration", _frozen_mapping(self.configuration, "configuration"))
        object.__setattr__(self, "feature_flags", _frozen_mapping(self.feature_flags, "feature_flags"))
        object.__setattr__(self, "sources", tuple(sorted(self.sources, key=lambda item: item.snapshot_id)))
        object.__setattr__(self, "operations", tuple(sorted(self.operations, key=lambda item: item.operation_id)))
        object.__setattr__(
            self,
            "dependency_graph",
            tuple(
                sorted(
                    self.dependency_graph,
                    key=lambda item: (
                        item.producer_operation_id,
                        item.consumer_operation_id,
                        item.dependency_class,
                    ),
                )
            ),
        )
        object.__setattr__(self, "contributors", tuple(sorted(self.contributors, key=lambda item: item.operation_id)))
        object.__setattr__(self, "artifact_references", tuple(sorted(self.artifact_references, key=lambda item: item.artifact_id)))
        object.__setattr__(self, "outputs", tuple(sorted(self.outputs, key=lambda item: item.output_id)))
        object.__setattr__(self, "transformations", tuple(sorted(self.transformations, key=lambda item: item.transformation_id)))

    def to_dict(self) -> dict[str, object]:
        return {
            "contract_version": self.contract_version,
            "run_id": self.run_id,
            "project_id": self.project_id,
            "sources": [source.to_dict() for source in self.sources],
            "operations": [operation.to_dict() for operation in self.operations],
            "dependency_graph": [edge.to_dict() for edge in self.dependency_graph],
            "contributors": [contributor.to_dict() for contributor in self.contributors],
            "artifact_references": [reference.to_dict() for reference in self.artifact_references],
            "outputs": [output.to_dict() for output in self.outputs],
            "transformations": [item.to_dict() for item in self.transformations],
            "coverage": self.coverage,
            "created_at": self.created_at,
            "finalized_at": self.finalized_at,
            "configuration": self.configuration.to_dict(),
            "feature_flags": self.feature_flags.to_dict(),
            "safety_boundary": {
                "analytical_output": True,
                "candidate_first": True,
                "owner_control_required": True,
                "automatic_truth_selection": False,
                "project_mutation_performed": False,
            },
        }

    def to_json(self) -> str:
        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )


def analysis_run_manifest_from_dict(value: object) -> AnalysisRunManifest:
    """Deterministically reconstruct and fully validate a persisted v1 value.

    This is a compatible read only. It performs no write or physical migration.
    """

    if not isinstance(value, Mapping):
        raise AnalysisRunManifestValidationError("manifest must be a mapping")
    payload = dict(value)
    required = {
        "contract_version", "run_id", "project_id", "sources", "operations",
        "dependency_graph", "contributors", "artifact_references", "outputs",
        "transformations", "coverage", "created_at", "finalized_at",
        "configuration", "feature_flags", "safety_boundary",
    }
    if set(payload) != required:
        raise AnalysisRunManifestValidationError("persisted manifest fields are not closed")

    def component(item: object) -> ProvenanceComponent:
        if not isinstance(item, Mapping):
            raise AnalysisRunManifestValidationError("invalid provenance component")
        return ProvenanceComponent(**dict(item))

    sources = tuple(SourceIdentity(**dict(item)) for item in payload["sources"])
    operations = tuple(
        OperationDeclaration(
            operation_id=item["operation_id"],
            adapter_id=item["adapter_id"],
            consumes=tuple(item["consumes"]),
            produces=tuple(item["produces"]),
            configuration=item["configuration"],
            feature_flags=item["feature_flags"],
        )
        for item in payload["operations"]
    )
    edges = tuple(DependencyEdge(**dict(item)) for item in payload["dependency_graph"])
    contributors = []
    for item in payload["contributors"]:
        provenance = item["provenance"]
        contributors.append(
            ContributorLineage(
                operation_id=item["operation_id"],
                adapter_id=item["adapter_id"],
                source_snapshot_ids=tuple(item["source_snapshot_ids"]),
                result_state=item["result_state"],
                coverage=item["coverage"],
                explanation=item["explanation"],
                provenance=AdapterProvenance(
                    adapter_id=provenance["adapter_id"],
                    operation_id=provenance["operation_id"],
                    user_facing_label=provenance["user_facing_label"],
                    implementation_kind=provenance["implementation_kind"],
                    tool=component(provenance["tool"]),
                    runtime=component(provenance["runtime"]),
                    provider=component(provenance["provider"]),
                    model=component(provenance["model"]),
                ),
                output_ids=tuple(item["output_ids"]),
            )
        )
    artifacts = tuple(
        ArtifactReference(
            artifact_id=item["artifact_id"],
            availability=item["availability"],
            source_snapshot_ids=tuple(item["source_snapshot_ids"]),
            content_hash=item["content_hash"],
            hash_algorithm=item["hash_algorithm"],
            media_type=item["media_type"],
        )
        for item in payload["artifact_references"]
    )
    outputs = tuple(
        OutputLineage(
            output_id=item["output_id"],
            operation_id=item["operation_id"],
            source_snapshot_ids=tuple(item["source_snapshot_ids"]),
            disposition=item["disposition"],
            original_output_reference_id=item["original_output_reference_id"],
            evidence_reference_ids=tuple(item["evidence_reference_ids"]),
            transformation_ids=tuple(item["transformation_ids"]),
            verification_outcome=item["verification_outcome"],
            guardrail_outcome=item["guardrail_outcome"],
            missing_evidence_reason=item["missing_evidence_reason"],
        )
        for item in payload["outputs"]
    )
    transformations = tuple(
        TransformationLineage(
            transformation_id=item["transformation_id"],
            operation_id=item["operation_id"],
            transformation_kind=item["transformation_kind"],
            transformation_version=item["transformation_version"],
            input_reference_ids=tuple(item["input_reference_ids"]),
            output_reference_ids=tuple(item["output_reference_ids"]),
        )
        for item in payload["transformations"]
    )
    manifest = AnalysisRunManifest(
        run_id=payload["run_id"],
        project_id=payload["project_id"],
        sources=sources,
        operations=operations,
        dependency_graph=edges,
        contributors=tuple(contributors),
        artifact_references=artifacts,
        outputs=outputs,
        transformations=transformations,
        coverage=payload["coverage"],
        created_at=payload["created_at"],
        finalized_at=payload["finalized_at"],
        configuration=payload["configuration"],
        feature_flags=payload["feature_flags"],
        contract_version=payload["contract_version"],
    )
    if manifest.to_dict() != payload:
        raise AnalysisRunManifestValidationError("persisted manifest is non-canonical")
    return manifest


__all__ = [
    "ANALYSIS_RUN_MANIFEST_CONTRACT_VERSION",
    "ADAPTER_RESULT_STATES",
    "ADAPTER_IDENTITIES",
    "DEPENDENCY_CLASSES",
    "AnalysisRunManifestValidationError",
    "FrozenJsonObject",
    "ProvenanceComponent",
    "AdapterProvenance",
    "OperationDeclaration",
    "DependencyEdge",
    "ArtifactReference",
    "TransformationLineage",
    "OutputLineage",
    "ContributorLineage",
    "AnalysisRunManifest",
    "analysis_run_manifest_from_dict",
]
