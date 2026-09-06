"""Official/full Subtxt runtime inventory and pure T005 contracts.

This module is deliberately non-executing.  It inventories only bounded local
signals, validates a future analysis-only request/result handoff, and keeps the
official ``subtxt`` identity separate from the app-owned
``subtxt_informed_rubric`` identity.  Runtime invocation, output conversion,
persistence, review integration, and live validation belong to T006.
"""

from __future__ import annotations

from dataclasses import dataclass
import importlib.metadata
from pathlib import Path
import re
import shutil
from typing import Iterable, Mapping

from backend.story_knowledge.analysis_run_manifest import (
    AdapterProvenance,
    AnalysisRunManifest,
    ProvenanceComponent,
)
from backend.story_knowledge.source_map import SourceIdentity


SUBTXT_RUNTIME_CONTRACT_VERSION = "official-subtxt-runtime-contract.v1"
OFFICIAL_SUBTXT_ADAPTER_ID = "subtxt"
APP_OWNED_SUBTXT_RUBRIC_ADAPTER_ID = "subtxt_informed_rubric"
APP_OWNED_SUBTXT_RUBRIC_INTERNAL_ID = "app_owned_subtxt_informed_rubric"
OFFICIAL_SUBTXT_OPERATION_ID = "analyze-subtxt"
SUBTXT_PROTECTED_SOURCE_REL = ".external_sources/subtxt-docs"

SUBTXT_DISCOVERY_STATES = frozenset(
    {
        "available",
        "configured",
        "missing",
        "inaccessible",
        "incompatible",
        "unsupported",
        "disabled",
        "unavailable",
        "malformed_configuration",
        "unknown_unverified",
    }
)

# T001/T003 already declare this exact operation as an analysis-only consumer
# of normalized evidence.  Current runtime evidence establishes no callable
# implementation of it, so runtime-supported and currently-available sets are
# intentionally empty.
OFFICIAL_SUBTXT_POLICY_PERMITTED_OPERATIONS = frozenset(
    {OFFICIAL_SUBTXT_OPERATION_ID}
)
CURRENT_SUBTXT_RUNTIME_SUPPORTED_OPERATIONS: frozenset[str] = frozenset()
CURRENT_SUBTXT_AVAILABLE_OPERATIONS: frozenset[str] = frozenset()

# The allowlist above is authoritative.  This named blocklist makes the known
# product-safety boundaries explicit; omission from this set never permits an
# operation.
OFFICIAL_SUBTXT_FORBIDDEN_OPERATIONS = frozenset(
    {
        "generate-story-prose",
        "write-story-prose",
        "continue-story-prose",
        "rewrite-story-prose",
        "imitate-story-prose",
        "polish-story-prose",
        "improve-story-prose",
        "expand-story-prose",
        "generate-outline",
        "produce-outline",
        "outline-story",
        "generate-draft",
        "produce-draft",
        "draft-story",
        "generate-revision",
        "revise-story-prose",
        "select-structural-truth",
        "approve-candidate",
        "automatically-approve-candidate",
        "promote-candidate",
        "automatically-promote-candidate",
        "apply-promotion",
        "mutate-project-story-content",
        "mutate-memory",
        "mutate-canon",
    }
)

SUBTXT_RESULT_STATES = frozenset(
    {
        "evidence_backed_success",
        "uncertainty",
        "unsupported_output",
        "unavailable_runtime",
        "runtime_failure",
        "incompatible_runtime",
        "malformed_output",
        "unsafe_output",
        "quarantined",
    }
)

SUBTXT_PROVENANCE_EXPECTATIONS = (
    "official_adapter_identity",
    "runtime_identity",
    "runtime_version",
    "callable_interface",
    "operation",
    "provider",
    "model",
    "model_version",
    "safe_configuration_identity",
    "transformation_lineage",
    "source_linkage",
    "run_linkage",
)

_KNOWN_CONFIGURATION_VARIABLES = (
    "OMI_LIVE_SUBTXT_COMMAND",
    "OMI_LIVE_SUBTXT_PATH",
)
_SAFE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,255}\Z")
_APP_OWNED_IDENTITIES = frozenset(
    {
        APP_OWNED_SUBTXT_RUBRIC_ADAPTER_ID,
        APP_OWNED_SUBTXT_RUBRIC_INTERNAL_ID,
    }
)


class SubtxtRuntimeContractError(ValueError):
    """Raised when an official Subtxt contract would fail open."""


def _require_safe_id(value: object, label: str) -> str:
    if not isinstance(value, str) or not _SAFE_ID.fullmatch(value) or ".." in value:
        raise SubtxtRuntimeContractError(f"{label} must be a path-safe ID")
    return value


def _require_state(value: str, label: str) -> str:
    if value not in SUBTXT_DISCOVERY_STATES:
        raise SubtxtRuntimeContractError(f"{label} has an unknown state")
    return value


@dataclass(frozen=True)
class SubtxtCapabilitySet:
    """Three non-interchangeable capability planes for one preflight."""

    policy_permitted_operations: frozenset[str]
    runtime_supported_operations: frozenset[str]
    currently_available_operations: frozenset[str]

    def __post_init__(self) -> None:
        for field_name in (
            "policy_permitted_operations",
            "runtime_supported_operations",
            "currently_available_operations",
        ):
            values = frozenset(getattr(self, field_name))
            for value in values:
                _require_safe_id(value, field_name)
            object.__setattr__(self, field_name, values)
        if not self.policy_permitted_operations <= OFFICIAL_SUBTXT_POLICY_PERMITTED_OPERATIONS:
            raise SubtxtRuntimeContractError(
                "policy operations must come from the official analysis-only allowlist"
            )
        if self.policy_permitted_operations & OFFICIAL_SUBTXT_FORBIDDEN_OPERATIONS:
            raise SubtxtRuntimeContractError("forbidden operation cannot be policy permitted")
        if not self.runtime_supported_operations <= self.policy_permitted_operations:
            raise SubtxtRuntimeContractError(
                "runtime-supported operations must also be policy permitted"
            )
        if not self.currently_available_operations <= self.runtime_supported_operations:
            raise SubtxtRuntimeContractError(
                "currently available operations must also be runtime supported"
            )

    def require_available(self, operation_id: str) -> None:
        _require_safe_id(operation_id, "operation_id")
        if operation_id in OFFICIAL_SUBTXT_FORBIDDEN_OPERATIONS:
            raise SubtxtRuntimeContractError("operation is explicitly forbidden")
        if operation_id not in self.policy_permitted_operations:
            raise SubtxtRuntimeContractError(
                "operation is not positively allowed by policy"
            )
        if operation_id not in self.runtime_supported_operations:
            raise SubtxtRuntimeContractError(
                "operation is not supported by verified runtime evidence"
            )
        if operation_id not in self.currently_available_operations:
            raise SubtxtRuntimeContractError("operation is not currently available")

    def to_dict(self) -> dict[str, list[str]]:
        return {
            "policy_permitted_operations": sorted(self.policy_permitted_operations),
            "runtime_supported_operations": sorted(self.runtime_supported_operations),
            "currently_available_operations": sorted(
                self.currently_available_operations
            ),
        }


CURRENT_SUBTXT_CAPABILITIES = SubtxtCapabilitySet(
    policy_permitted_operations=OFFICIAL_SUBTXT_POLICY_PERMITTED_OPERATIONS,
    runtime_supported_operations=CURRENT_SUBTXT_RUNTIME_SUPPORTED_OPERATIONS,
    currently_available_operations=CURRENT_SUBTXT_AVAILABLE_OPERATIONS,
)


@dataclass(frozen=True)
class SubtxtRuntimeInventory:
    """Truthful bounded discovery result; never proof of execution."""

    protected_source_path: str
    protected_source_state: str
    protected_source_classification: str
    installed_package_state: str
    installed_package_metadata: tuple[tuple[str, str | None], ...]
    executable_state: str
    executable_name: str | None
    callable_library_state: str
    callable_local_api_state: str
    network_api_state: str
    configuration_state: str
    configured_variable_names: tuple[str, ...]
    installation_access_state: str
    runtime_version_state: str
    runtime_version: str | None
    provider_state: str
    provider: str | None
    model_state: str
    model: str | None
    model_version: str | None
    supported_operation_evidence_state: str
    compatibility_state: str
    unsupported_or_unverified_interfaces: tuple[str, ...]
    capabilities: SubtxtCapabilitySet
    ready: bool
    readiness_state: str
    detail: str
    contract_version: str = SUBTXT_RUNTIME_CONTRACT_VERSION
    official_adapter_identity: str = OFFICIAL_SUBTXT_ADAPTER_ID
    app_owned_rubric_identity: str = APP_OWNED_SUBTXT_RUBRIC_ADAPTER_ID

    def __post_init__(self) -> None:
        if not isinstance(self.capabilities, SubtxtCapabilitySet):
            raise SubtxtRuntimeContractError("Subtxt capability set is required")
        for field_name in (
            "protected_source_state",
            "installed_package_state",
            "executable_state",
            "callable_library_state",
            "callable_local_api_state",
            "network_api_state",
            "configuration_state",
            "installation_access_state",
            "runtime_version_state",
            "provider_state",
            "model_state",
            "supported_operation_evidence_state",
            "compatibility_state",
            "readiness_state",
        ):
            _require_state(getattr(self, field_name), field_name)
        if self.contract_version != SUBTXT_RUNTIME_CONTRACT_VERSION:
            raise SubtxtRuntimeContractError("unsupported inventory contract version")
        if self.official_adapter_identity != OFFICIAL_SUBTXT_ADAPTER_ID:
            raise SubtxtRuntimeContractError("official Subtxt identity cannot be relabeled")
        if self.app_owned_rubric_identity != APP_OWNED_SUBTXT_RUBRIC_ADAPTER_ID:
            raise SubtxtRuntimeContractError("app-owned rubric identity cannot be relabeled")
        if self.ready != (self.readiness_state == "available"):
            raise SubtxtRuntimeContractError("runtime readiness fields are inconsistent")
        if self.ready:
            if not self.capabilities.currently_available_operations:
                raise SubtxtRuntimeContractError(
                    "runtime readiness requires a currently available operation"
                )

    def to_dict(self) -> dict[str, object]:
        return {
            "contract_version": self.contract_version,
            "official_adapter_identity": self.official_adapter_identity,
            "app_owned_rubric_identity": self.app_owned_rubric_identity,
            "protected_source_path": self.protected_source_path,
            "protected_source_state": self.protected_source_state,
            "protected_source_classification": self.protected_source_classification,
            "installed_package_state": self.installed_package_state,
            "installed_package_metadata": [
                {"name": name, "version": version}
                for name, version in self.installed_package_metadata
            ],
            "executable_state": self.executable_state,
            "executable_name": self.executable_name,
            "callable_library_state": self.callable_library_state,
            "callable_local_api_state": self.callable_local_api_state,
            "network_api_state": self.network_api_state,
            "configuration_state": self.configuration_state,
            "configured_variable_names": list(self.configured_variable_names),
            "configuration_values_exposed": False,
            "installation_access_state": self.installation_access_state,
            "runtime_version_state": self.runtime_version_state,
            "runtime_version": self.runtime_version,
            "provider_state": self.provider_state,
            "provider": self.provider,
            "model_state": self.model_state,
            "model": self.model,
            "model_version": self.model_version,
            "supported_operation_evidence_state": (
                self.supported_operation_evidence_state
            ),
            "compatibility_state": self.compatibility_state,
            "unsupported_or_unverified_interfaces": list(
                self.unsupported_or_unverified_interfaces
            ),
            "capabilities": self.capabilities.to_dict(),
            "ready": self.ready,
            "readiness_state": self.readiness_state,
            "detail": self.detail,
            "discovery_executed_runtime": False,
            "network_access_performed": False,
            "persistence_performed": False,
        }


def _installed_subtxt_distribution_records() -> tuple[str, tuple[tuple[str, str | None], ...]]:
    try:
        records = []
        for distribution in importlib.metadata.distributions():
            name = distribution.metadata.get("Name")
            if isinstance(name, str) and "subtxt" in name.casefold():
                records.append((name, distribution.version or None))
        return "available", tuple(sorted(records))
    except Exception:
        return "inaccessible", ()


def discover_official_subtxt_runtime(
    *,
    repo_root: str | Path,
    env: Mapping[str, str] | None = None,
    distribution_records: Iterable[tuple[str, str | None]] | None = None,
    executable_path: str | None = None,
) -> SubtxtRuntimeInventory:
    """Inspect bounded local signals without importing or executing Subtxt.

    ``distribution_records`` and ``executable_path`` are test/provisioning
    evidence seams.  A discovered record/path remains unverified and cannot by
    itself make the runtime ready.
    """

    root = Path(repo_root)
    source_path = root / SUBTXT_PROTECTED_SOURCE_REL
    try:
        source_state = "available" if source_path.is_dir() else "missing"
    except OSError:
        source_state = "inaccessible"

    if distribution_records is None:
        metadata_probe_state, records = _installed_subtxt_distribution_records()
    else:
        metadata_probe_state = "available"
        records = tuple(
            sorted(
                (str(name), None if version is None else str(version))
                for name, version in distribution_records
                if "subtxt" in str(name).casefold()
            )
        )
    package_state = (
        "inaccessible"
        if metadata_probe_state == "inaccessible"
        else ("available" if records else "missing")
    )

    discovered_executable = executable_path
    if executable_path is None:
        discovered_executable = shutil.which("subtxt")
    executable_state = "available" if discovered_executable else "missing"

    effective_env = {} if env is None else env
    present_names = tuple(
        name for name in _KNOWN_CONFIGURATION_VARIABLES if name in effective_env
    )
    malformed_names = tuple(
        name
        for name in present_names
        if not isinstance(effective_env.get(name), str)
        or not str(effective_env.get(name)).strip()
    )
    if malformed_names:
        configuration_state = "malformed_configuration"
    elif present_names:
        configuration_state = "configured"
    else:
        configuration_state = "missing"

    artifact_present = bool(records or discovered_executable)
    callable_state = "unknown_unverified" if artifact_present else "missing"
    installation_state = "unknown_unverified" if artifact_present else "missing"
    detail = (
        "No official/full Subtxt callable runtime is established by the bounded "
        "current-machine evidence. Source/package/executable/configuration signals "
        "are inventory only; no runtime operation, import, network request, or "
        "compatibility test was performed."
    )
    return SubtxtRuntimeInventory(
        protected_source_path=SUBTXT_PROTECTED_SOURCE_REL,
        protected_source_state=source_state,
        protected_source_classification=(
            "historical_documentation_reference_only"
            if source_state == "available"
            else "not_currently_present"
        ),
        installed_package_state=package_state,
        installed_package_metadata=records,
        executable_state=executable_state,
        executable_name="subtxt" if discovered_executable else None,
        callable_library_state=callable_state,
        callable_local_api_state="unknown_unverified",
        network_api_state="unknown_unverified",
        configuration_state=configuration_state,
        configured_variable_names=present_names,
        installation_access_state=installation_state,
        runtime_version_state="unknown_unverified",
        runtime_version=None,
        provider_state="unknown_unverified",
        provider=None,
        model_state="unknown_unverified",
        model=None,
        model_version=None,
        supported_operation_evidence_state="unknown_unverified",
        compatibility_state="unknown_unverified",
        unsupported_or_unverified_interfaces=(
            "cli",
            "importable_library",
            "local_api",
            "network_api",
            "source_runtime_package",
        ),
        capabilities=CURRENT_SUBTXT_CAPABILITIES,
        ready=False,
        readiness_state="unavailable",
        detail=detail,
    )


@dataclass(frozen=True)
class SubtxtAnalysisRequest:
    """Pure future-call request bound directly to T002/T003 identities."""

    analysis_run_manifest: AnalysisRunManifest
    source_identity: SourceIdentity
    analysis_run_id: str
    source_snapshot_id: str
    source_content_sha256: str
    source_artifact_reference_id: str
    normalized_evidence_reference_ids: tuple[str, ...]
    operation_id: str
    capabilities: SubtxtCapabilitySet
    runtime_identity: ProvenanceComponent
    callable_interface: ProvenanceComponent
    analysis_intent: str = "analysis_only"
    adapter_identity: str = OFFICIAL_SUBTXT_ADAPTER_ID
    expected_implementation_kind: str = "official_external"
    evidence_and_provenance_required: bool = True
    contract_version: str = SUBTXT_RUNTIME_CONTRACT_VERSION

    def __post_init__(self) -> None:
        if not isinstance(self.analysis_run_manifest, AnalysisRunManifest):
            raise SubtxtRuntimeContractError("T002 AnalysisRunManifest is required")
        if not isinstance(self.source_identity, SourceIdentity):
            raise SubtxtRuntimeContractError("T002 SourceIdentity is required")
        if self.adapter_identity != OFFICIAL_SUBTXT_ADAPTER_ID:
            raise SubtxtRuntimeContractError("official Subtxt request identity mismatch")
        if self.expected_implementation_kind != "official_external":
            raise SubtxtRuntimeContractError("official Subtxt must remain external")
        if self.analysis_intent != "analysis_only":
            raise SubtxtRuntimeContractError("Subtxt request must be analysis-only")
        if self.evidence_and_provenance_required is not True:
            raise SubtxtRuntimeContractError("evidence and provenance are required")
        if self.contract_version != SUBTXT_RUNTIME_CONTRACT_VERSION:
            raise SubtxtRuntimeContractError("unsupported request contract version")
        for value, label in (
            (self.analysis_run_id, "analysis_run_id"),
            (self.source_snapshot_id, "source_snapshot_id"),
            (self.source_artifact_reference_id, "source_artifact_reference_id"),
            (self.operation_id, "operation_id"),
        ):
            _require_safe_id(value, label)
        if (
            not isinstance(self.normalized_evidence_reference_ids, tuple)
            or not self.normalized_evidence_reference_ids
            or len(set(self.normalized_evidence_reference_ids))
            != len(self.normalized_evidence_reference_ids)
        ):
            raise SubtxtRuntimeContractError("normalized evidence references are required")
        for evidence_id in self.normalized_evidence_reference_ids:
            _require_safe_id(evidence_id, "normalized_evidence_reference_id")
        if not isinstance(self.capabilities, SubtxtCapabilitySet):
            raise SubtxtRuntimeContractError("Subtxt capability set is required")
        for component, label in (
            (self.runtime_identity, "runtime identity"),
            (self.callable_interface, "callable interface"),
        ):
            if not isinstance(component, ProvenanceComponent):
                raise SubtxtRuntimeContractError(f"{label} provenance is required")
            if component.availability != "available" or component.name is None:
                raise SubtxtRuntimeContractError(
                    f"verified available {label} is required"
                )
            if component.name in _APP_OWNED_IDENTITIES:
                raise SubtxtRuntimeContractError(
                    "official Subtxt request cannot impersonate the app-owned rubric"
                )

        manifest = self.analysis_run_manifest
        source = self.source_identity
        if self.analysis_run_id != manifest.run_id:
            raise SubtxtRuntimeContractError("analysis run linkage mismatch")
        if source not in manifest.sources:
            raise SubtxtRuntimeContractError("source identity is not in the run manifest")
        if self.source_snapshot_id != source.snapshot_id:
            raise SubtxtRuntimeContractError("source snapshot linkage mismatch")
        if self.source_content_sha256 != source.content_hash:
            raise SubtxtRuntimeContractError("exact source SHA-256 mismatch")

        operations = {
            item.operation_id: item for item in manifest.operations
        }
        operation = operations.get(self.operation_id)
        if operation is None or operation.adapter_id != OFFICIAL_SUBTXT_ADAPTER_ID:
            raise SubtxtRuntimeContractError("manifest has no matching Subtxt operation")
        if "normalized_evidence" not in operation.consumes:
            raise SubtxtRuntimeContractError(
                "official Subtxt operation must consume normalized evidence"
            )
        if "diagnostic_candidate_finding" not in operation.produces:
            raise SubtxtRuntimeContractError(
                "official Subtxt operation must produce diagnostic candidate findings"
            )
        producer_operation_ids = {
            edge.producer_operation_id
            for edge in manifest.dependency_graph
            if (
                edge.consumer_operation_id == self.operation_id
                and edge.dependency_class == "normalized_evidence"
            )
        }
        if not producer_operation_ids:
            raise SubtxtRuntimeContractError(
                "normalized evidence dependency lineage is required"
            )
        if not all(
            "normalized_evidence" in operations[producer_id].produces
            for producer_id in producer_operation_ids
        ):
            raise SubtxtRuntimeContractError(
                "normalized evidence producer declaration is invalid"
            )
        artifacts = {
            item.artifact_id: item for item in manifest.artifact_references
        }
        source_artifact = artifacts.get(self.source_artifact_reference_id)
        if source_artifact is None:
            raise SubtxtRuntimeContractError("source artifact reference is unknown")
        if source_artifact.availability != "available":
            raise SubtxtRuntimeContractError("source artifact is not available")
        if source.snapshot_id not in source_artifact.source_snapshot_ids:
            raise SubtxtRuntimeContractError("source artifact snapshot mismatch")
        if source_artifact.content_hash != source.content_hash:
            raise SubtxtRuntimeContractError("source artifact SHA-256 mismatch")

        evidence_ids = {
            evidence_id
            for output in manifest.outputs
            if output.operation_id in producer_operation_ids
            for evidence_id in output.evidence_reference_ids
        }
        if not set(self.normalized_evidence_reference_ids) <= evidence_ids:
            raise SubtxtRuntimeContractError(
                "normalized evidence reference is not declared by the run manifest"
            )
        self.capabilities.require_available(self.operation_id)

    def to_dict(self) -> dict[str, object]:
        return {
            "contract_version": self.contract_version,
            "analysis_run_id": self.analysis_run_id,
            "project_id": self.source_identity.project_id,
            "source_identity": self.source_identity.to_dict(),
            "source_snapshot_id": self.source_snapshot_id,
            "source_content_sha256": self.source_content_sha256,
            "source_artifact_reference_id": self.source_artifact_reference_id,
            "normalized_evidence_reference_ids": list(
                self.normalized_evidence_reference_ids
            ),
            "operation_id": self.operation_id,
            "adapter_identity": self.adapter_identity,
            "runtime_identity": self.runtime_identity.to_dict(),
            "callable_interface": self.callable_interface.to_dict(),
            "expected_implementation_kind": self.expected_implementation_kind,
            "analysis_intent": self.analysis_intent,
            "evidence_and_provenance_required": self.evidence_and_provenance_required,
            "provenance_expectations": list(SUBTXT_PROVENANCE_EXPECTATIONS),
            "capabilities": self.capabilities.to_dict(),
            "safety": _safety_boundary(),
        }


@dataclass(frozen=True)
class SubtxtRuntimeProvenance:
    """Official provenance that preserves unknown components as unknown."""

    adapter: AdapterProvenance
    callable_interface: ProvenanceComponent
    safe_configuration_identity: ProvenanceComponent
    analysis_run_id: str
    source_snapshot_ids: tuple[str, ...]
    transformation_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.adapter, AdapterProvenance):
            raise SubtxtRuntimeContractError("T002 AdapterProvenance is required")
        if self.adapter.adapter_id != OFFICIAL_SUBTXT_ADAPTER_ID:
            raise SubtxtRuntimeContractError("official provenance identity mismatch")
        if self.adapter.operation_id != OFFICIAL_SUBTXT_OPERATION_ID:
            raise SubtxtRuntimeContractError("official provenance operation mismatch")
        if self.adapter.implementation_kind != "official_external":
            raise SubtxtRuntimeContractError("official provenance must be external")
        for component in (
            self.adapter.tool,
            self.adapter.runtime,
            self.adapter.provider,
            self.adapter.model,
            self.callable_interface,
            self.safe_configuration_identity,
        ):
            if not isinstance(component, ProvenanceComponent):
                raise SubtxtRuntimeContractError("invalid provenance component")
            if component.name in _APP_OWNED_IDENTITIES:
                raise SubtxtRuntimeContractError(
                    "official Subtxt provenance cannot impersonate the app-owned rubric"
                )
        _require_safe_id(self.analysis_run_id, "analysis_run_id")
        if (
            not isinstance(self.source_snapshot_ids, tuple)
            or not self.source_snapshot_ids
            or len(set(self.source_snapshot_ids)) != len(self.source_snapshot_ids)
        ):
            raise SubtxtRuntimeContractError("source provenance linkage is required")
        for value in self.source_snapshot_ids:
            _require_safe_id(value, "source_snapshot_id")
        if not isinstance(self.transformation_ids, tuple) or len(
            set(self.transformation_ids)
        ) != len(self.transformation_ids):
            raise SubtxtRuntimeContractError("transformation lineage must be a unique tuple")
        for value in self.transformation_ids:
            _require_safe_id(value, "transformation_id")

    def to_dict(self) -> dict[str, object]:
        return {
            "adapter": self.adapter.to_dict(),
            "callable_interface": self.callable_interface.to_dict(),
            "safe_configuration_identity": self.safe_configuration_identity.to_dict(),
            "analysis_run_id": self.analysis_run_id,
            "source_snapshot_ids": list(self.source_snapshot_ids),
            "transformation_ids": list(self.transformation_ids),
        }


def unknown_official_subtxt_provenance(
    *, analysis_run_id: str, operation_id: str, source_snapshot_ids: tuple[str, ...]
) -> SubtxtRuntimeProvenance:
    """Build explicit unknown provenance without synthesizing runtime facts."""

    return SubtxtRuntimeProvenance(
        adapter=AdapterProvenance(
            adapter_id=OFFICIAL_SUBTXT_ADAPTER_ID,
            operation_id=operation_id,
            user_facing_label="Official/full Subtxt runtime path (unverified)",
            implementation_kind="official_external",
            tool=ProvenanceComponent("unknown"),
            runtime=ProvenanceComponent("unknown"),
            provider=ProvenanceComponent("unknown"),
            model=ProvenanceComponent("unknown"),
        ),
        callable_interface=ProvenanceComponent("unknown"),
        safe_configuration_identity=ProvenanceComponent("unknown"),
        analysis_run_id=analysis_run_id,
        source_snapshot_ids=source_snapshot_ids,
        transformation_ids=(),
    )


@dataclass(frozen=True)
class SubtxtAnalysisResult:
    """Content-free result envelope; T006 owns raw output and conversion."""

    state: str
    analysis_run_id: str
    source_snapshot_id: str
    source_content_sha256: str
    operation_id: str
    provenance: SubtxtRuntimeProvenance
    raw_output_reference_id: str | None = None
    evidence_reference_ids: tuple[str, ...] = ()
    transformation_ids: tuple[str, ...] = ()
    reason: str | None = None
    quarantined: bool = False
    contract_version: str = SUBTXT_RUNTIME_CONTRACT_VERSION

    def __post_init__(self) -> None:
        if self.state not in SUBTXT_RESULT_STATES:
            raise SubtxtRuntimeContractError("unknown Subtxt result state")
        if self.contract_version != SUBTXT_RUNTIME_CONTRACT_VERSION:
            raise SubtxtRuntimeContractError("unsupported result contract version")
        for value, label in (
            (self.analysis_run_id, "analysis_run_id"),
            (self.source_snapshot_id, "source_snapshot_id"),
            (self.operation_id, "operation_id"),
        ):
            _require_safe_id(value, label)
        if not re.fullmatch(r"[0-9a-f]{64}", self.source_content_sha256):
            raise SubtxtRuntimeContractError("source_content_sha256 must be exact SHA-256")
        if not isinstance(self.provenance, SubtxtRuntimeProvenance):
            raise SubtxtRuntimeContractError("official runtime provenance is required")
        if self.provenance.analysis_run_id != self.analysis_run_id:
            raise SubtxtRuntimeContractError("result run provenance mismatch")
        if self.provenance.adapter.operation_id != self.operation_id:
            raise SubtxtRuntimeContractError("result operation provenance mismatch")
        if self.source_snapshot_id not in self.provenance.source_snapshot_ids:
            raise SubtxtRuntimeContractError("result source provenance mismatch")
        if self.raw_output_reference_id is not None:
            _require_safe_id(self.raw_output_reference_id, "raw_output_reference_id")
        if not isinstance(self.evidence_reference_ids, tuple) or len(
            set(self.evidence_reference_ids)
        ) != len(self.evidence_reference_ids):
            raise SubtxtRuntimeContractError("evidence lineage must be a unique tuple")
        for value in self.evidence_reference_ids:
            _require_safe_id(value, "evidence_reference_id")
        if not isinstance(self.transformation_ids, tuple) or len(
            set(self.transformation_ids)
        ) != len(self.transformation_ids):
            raise SubtxtRuntimeContractError("transformation lineage must be a unique tuple")
        for value in self.transformation_ids:
            _require_safe_id(value, "transformation_id")
        if self.reason is not None and (
            not isinstance(self.reason, str) or not self.reason.strip()
        ):
            raise SubtxtRuntimeContractError("result reason must be a non-empty string")
        if tuple(self.transformation_ids) != tuple(self.provenance.transformation_ids):
            raise SubtxtRuntimeContractError("transformation provenance mismatch")

        if self.state == "evidence_backed_success":
            if self.quarantined:
                raise SubtxtRuntimeContractError("successful output cannot be quarantined")
            if not self.raw_output_reference_id or not self.evidence_reference_ids:
                raise SubtxtRuntimeContractError(
                    "success requires raw output and evidence references"
                )
            if self.provenance.adapter.runtime.availability != "available":
                raise SubtxtRuntimeContractError("success requires known runtime identity")
            if self.provenance.callable_interface.availability != "available":
                raise SubtxtRuntimeContractError("success requires known callable interface")
        elif self.state == "uncertainty":
            if not self.reason or not self.raw_output_reference_id:
                raise SubtxtRuntimeContractError(
                    "uncertainty requires a reason and preserved raw output reference"
                )
        else:
            if not self.reason:
                raise SubtxtRuntimeContractError("non-success result requires a reason")
        if self.state in {
            "unsupported_output",
            "malformed_output",
            "unsafe_output",
            "quarantined",
        } and not self.quarantined:
            raise SubtxtRuntimeContractError("unsafe/unusable output must be quarantined")

    def to_dict(self) -> dict[str, object]:
        disposition = {
            "evidence_backed_success": "validated",
            "uncertainty": "unverified",
        }.get(self.state, "quarantined" if self.quarantined else "unverified")
        return {
            "contract_version": self.contract_version,
            "state": self.state,
            "analysis_run_id": self.analysis_run_id,
            "source_snapshot_id": self.source_snapshot_id,
            "source_content_sha256": self.source_content_sha256,
            "operation_id": self.operation_id,
            "provenance": self.provenance.to_dict(),
            "raw_output_reference_id": self.raw_output_reference_id,
            "evidence_reference_ids": list(self.evidence_reference_ids),
            "transformation_ids": list(self.transformation_ids),
            "reason": self.reason,
            "quarantined": self.quarantined,
            "output_disposition": disposition,
            "candidate_conversion_performed": False,
            "candidate_persistence_performed": False,
            "safety": _safety_boundary(),
        }


def _safety_boundary() -> dict[str, bool]:
    return {
        "analysis_only": True,
        "story_prose_generated": False,
        "story_prose_rewritten": False,
        "story_prose_continued": False,
        "story_prose_imitated": False,
        "story_prose_polished_or_improved": False,
        "story_prose_expanded": False,
        "outline_draft_or_revision_produced": False,
        "structural_truth_selected": False,
        "project_story_content_mutated": False,
        "memory_or_canon_mutated": False,
        "candidate_automatically_approved": False,
        "promotion_performed": False,
        "apply_promotion_performed": False,
        "result_is_truth_or_canon": False,
    }


__all__ = (
    "SUBTXT_RUNTIME_CONTRACT_VERSION",
    "OFFICIAL_SUBTXT_ADAPTER_ID",
    "APP_OWNED_SUBTXT_RUBRIC_ADAPTER_ID",
    "APP_OWNED_SUBTXT_RUBRIC_INTERNAL_ID",
    "OFFICIAL_SUBTXT_OPERATION_ID",
    "SUBTXT_PROTECTED_SOURCE_REL",
    "SUBTXT_DISCOVERY_STATES",
    "OFFICIAL_SUBTXT_POLICY_PERMITTED_OPERATIONS",
    "CURRENT_SUBTXT_RUNTIME_SUPPORTED_OPERATIONS",
    "CURRENT_SUBTXT_AVAILABLE_OPERATIONS",
    "OFFICIAL_SUBTXT_FORBIDDEN_OPERATIONS",
    "SUBTXT_RESULT_STATES",
    "SUBTXT_PROVENANCE_EXPECTATIONS",
    "SubtxtRuntimeContractError",
    "SubtxtCapabilitySet",
    "CURRENT_SUBTXT_CAPABILITIES",
    "SubtxtRuntimeInventory",
    "discover_official_subtxt_runtime",
    "SubtxtAnalysisRequest",
    "SubtxtRuntimeProvenance",
    "unknown_official_subtxt_provenance",
    "SubtxtAnalysisResult",
)
