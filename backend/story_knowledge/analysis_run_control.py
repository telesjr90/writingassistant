"""Synchronous application-owned OMI analysis-run control plane.

Submission completes in the request process.  No queue, background worker,
generalized timeout, or cancellation behavior is implied.  The default runner
is the existing candidate-first OMI orchestrator; tests may inject a fake
runner without invoking external tools.
"""

from __future__ import annotations

import copy
import fcntl
import hashlib
import json
import os
import re
import stat
import threading
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from backend import omi_analysis_orchestrator, omi_runtime_preflight, project_manager
from backend.story_knowledge import booknlp_adapter_contract
from backend.story_knowledge.analysis_run_manifest import (
    AdapterProvenance,
    AnalysisRunManifest,
    ArtifactReference,
    ContributorLineage,
    DependencyEdge,
    OperationDeclaration,
    OutputLineage,
    ProvenanceComponent,
    TransformationLineage,
)
from backend.story_knowledge.evidence_ledger import (
    EVIDENCE_LEDGER_VERSION,
    append_evidence_ledger_event,
    build_exact_evidence_record,
    canonical_json_bytes,
    canonical_sha256,
    scan_evidence_ledger,
)
from backend.story_knowledge.raw_artifacts import (
    IMMUTABLE_RAW_ARTIFACT_VERSION,
    build_immutable_raw_artifact_manifest,
    delete_immutable_raw_artifact_bundle,
    raw_artifact_boundary_flags,
    read_immutable_raw_artifact_bundle,
    write_immutable_raw_artifact_bundle,
)
from backend.story_knowledge.source_map import (
    BYTE_OFFSET_BASIS,
    CHAR_OFFSET_BASIS,
    OffsetRange,
    build_exact_source_snapshot,
    translate_exact_offset_range,
)


ANALYSIS_RUN_RECORD_VERSION = "omi-analysis-run-record.v1"
ANALYSIS_RUN_CONTROL_VERSION = "omi-analysis-control-plane.v1"
ANALYSIS_RUN_STATES = frozenset({"complete", "partial", "degraded", "error"})
SUPPORTED_ADAPTERS = frozenset(omi_analysis_orchestrator.OMI_TOOL_ADAPTER_IDENTITIES)
_PROCESS_SUBMISSION_LOCKS: dict[tuple[str, str], threading.Lock] = {}
_PROCESS_SUBMISSION_LOCKS_GUARD = threading.Lock()


class _BoundedAnalysisExecutionError(Exception):
    def __init__(self, original: Exception) -> None:
        super().__init__(str(original))
        self.original = original

_OPERATION_CONTRACTS = {
    "analyze-spacy": {
        "adapter_id": "spacy",
        "consumes": ("owner_selected_source",),
        "produces": ("raw_extraction_evidence", "normalized_evidence"),
        "role": "source_evidence_producer",
        "label": "spaCy evidence production",
    },
    "analyze-booknlp": {
        "adapter_id": "booknlp",
        "consumes": ("owner_selected_source",),
        "produces": ("raw_extraction_evidence", "normalized_evidence"),
        "role": "source_evidence_producer",
        "label": "BookNLP evidence production",
    },
    omi_analysis_orchestrator.OMI_OLLAMA_EXACT_SOURCE_OPERATION_ID: {
        "adapter_id": omi_analysis_orchestrator.OMI_OLLAMA_ADAPTER_NAME,
        "operation_semantics": (
            omi_analysis_orchestrator.OMI_OLLAMA_EXACT_SOURCE_OPERATION_SEMANTICS
        ),
        "consumes": ("owner_selected_source",),
        "produces": ("diagnostic_candidate_finding",),
        "role": "exact_source_structured_extractor",
        "label": "Ollama exact-source structured extraction",
    },
    omi_analysis_orchestrator.OMI_OLLAMA_NORMALIZED_EVIDENCE_OPERATION_ID: {
        "adapter_id": omi_analysis_orchestrator.OMI_OLLAMA_ADAPTER_NAME,
        "operation_semantics": (
            omi_analysis_orchestrator.OMI_OLLAMA_NORMALIZED_EVIDENCE_OPERATION_SEMANTICS
        ),
        "consumes": ("normalized_evidence",),
        "produces": ("diagnostic_candidate_finding",),
        "role": "normalized_evidence_interpreter",
        "label": "Ollama normalized-evidence interpretation",
    },
    omi_analysis_orchestrator.OMI_STORY_CHECK_OPERATION_ID: {
        "adapter_id": "story_check",
        "consumes": ("owner_selected_source",),
        "produces": ("diagnostic_candidate_finding",),
        "role": "grounded_diagnostic_consumer",
        "label": "Story Check grounded diagnostics",
    },
    "analyze-subtxt-informed-rubric": {
        "adapter_id": "subtxt_informed_rubric",
        "consumes": ("owner_selected_source",),
        "produces": ("diagnostic_candidate_finding",),
        "role": "app_owned_direct_source_rubric",
        "label": "App-owned Subtxt-informed rubric",
    },
    "analyze-dramatica-flow-informed-rubric": {
        "adapter_id": "dramatica_flow_informed_rubric",
        "consumes": ("owner_selected_source",),
        "produces": ("diagnostic_candidate_finding",),
        "role": "app_owned_direct_source_rubric",
        "label": "App-owned dramatica-flow-informed rubric",
    },
    "analyze-deterministic-fallback": {
        "adapter_id": "deterministic_fallback",
        "consumes": ("owner_selected_source",),
        "produces": ("diagnostic_candidate_finding",),
        "role": "fallback_safety_baseline",
        "label": "Deterministic fallback analysis",
    },
    "analyze-subtxt": {
        "adapter_id": "subtxt",
        "consumes": ("normalized_evidence",),
        "produces": ("diagnostic_candidate_finding",),
        "role": "normalized_evidence_consumer",
        "label": "Subtxt normalized-evidence interpretation",
    },
    "analyze-dramatica-flow": {
        "adapter_id": "dramatica_flow",
        "consumes": ("normalized_evidence",),
        "produces": ("diagnostic_candidate_finding",),
        "role": "normalized_evidence_consumer",
        "label": "dramatica-flow normalized-evidence interpretation",
    },
    "analyze-ncp": {
        "adapter_id": "ncp",
        "consumes": ("imported_artifact",),
        "produces": ("gateway_input_output",),
        "role": "gateway_import_export",
        "label": "NCP gateway/import-export",
    },
}
_DEFAULT_OPERATION_BY_ADAPTER = {
    "spacy": "analyze-spacy",
    "booknlp": "analyze-booknlp",
    "ollama_model": omi_analysis_orchestrator.OMI_OLLAMA_EXACT_SOURCE_OPERATION_ID,
    "story_check": omi_analysis_orchestrator.OMI_STORY_CHECK_OPERATION_ID,
    "subtxt_informed_rubric": "analyze-subtxt-informed-rubric",
    "dramatica_flow_informed_rubric": "analyze-dramatica-flow-informed-rubric",
    "deterministic_fallback": "analyze-deterministic-fallback",
    "subtxt": "analyze-subtxt",
    "dramatica_flow": "analyze-dramatica-flow",
    "ncp": "analyze-ncp",
}
# Compatibility view for callers that still inspect the default operation by
# adapter. Operation contracts themselves are keyed independently above so a
# later operation may retain the same adapter identity without replacing this
# exact-source Ollama operation.
_ADAPTER_OPERATION_CONTRACT = {
    adapter_id: _OPERATION_CONTRACTS[operation_id]
    for adapter_id, operation_id in _DEFAULT_OPERATION_BY_ADAPTER.items()
}
_UNPROVIDED_CONTROL_PLANE_INPUTS = {
    "subtxt": "normalized evidence is not supplied by the T003 control plane",
    "dramatica_flow": "normalized evidence and authorized runtime are not supplied by the T003 control plane",
    "ncp": "an explicit owner-selected imported artifact is not supplied by the raw-source request",
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _project_dir(project_id: str) -> Path:
    safe = project_manager.validate_project_id(project_id)
    root = project_manager.PROJECTS_DIR.resolve()
    path = project_manager.PROJECTS_DIR / safe
    if path.is_symlink() or not path.is_dir():
        raise FileNotFoundError("Project not found")
    resolved = path.resolve(strict=True)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError("project path escapes projects root") from exc
    return resolved


def analysis_run_dir(project_dir: str | Path, run_id: str) -> Path:
    # The frozen T002 value validator is authoritative for the same run IDs;
    # reject filesystem spellings before constructing a path here as well.
    if (
        not isinstance(run_id, str)
        or not run_id
        or ".." in run_id
        or "/" in run_id
        or "\\" in run_id
        or Path(run_id).is_absolute()
    ):
        raise ValueError("run_id must be path-safe")
    return Path(project_dir) / "writer_assistant" / "analysis_runs" / run_id


@contextmanager
def _acquire_submission_lock(*, project_dir: Path, project_id: str, scope: str):
    """Serialize one project-local submission/idempotency scope."""

    digest = hashlib.sha256(f"{project_id}/{scope}".encode("utf-8")).hexdigest()
    lock_root = project_dir / "writer_assistant" / "analysis_run_locks"
    for path in (project_dir / "writer_assistant", lock_root):
        if path.exists() and path.is_symlink():
            raise ValueError("unsafe analysis submission lock path")
    lock_root.mkdir(parents=True, exist_ok=True, mode=0o700)
    directory_metadata = os.stat(lock_root, follow_symlinks=False)
    if (
        not stat.S_ISDIR(directory_metadata.st_mode)
        or directory_metadata.st_uid != os.getuid()
        or stat.S_IMODE(directory_metadata.st_mode) & 0o077
    ):
        raise ValueError("unsafe analysis submission lock directory")
    process_key = (str(project_dir), digest)
    with _PROCESS_SUBMISSION_LOCKS_GUARD:
        process_lock = _PROCESS_SUBMISSION_LOCKS.setdefault(process_key, threading.Lock())
    process_lock.acquire()
    descriptor = None
    locked = False
    try:
        descriptor = os.open(
            lock_root / f"submission-{digest}.lock",
            os.O_CREAT | os.O_RDWR | os.O_CLOEXEC | os.O_NOFOLLOW,
            0o600,
        )
        metadata = os.fstat(descriptor)
        if (
            not stat.S_ISREG(metadata.st_mode)
            or stat.S_IMODE(metadata.st_mode) != 0o600
            or metadata.st_uid != os.getuid()
            or metadata.st_size != 0
            or metadata.st_nlink != 1
        ):
            raise ValueError("unsafe analysis submission lock file")
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        locked = True
        yield
    finally:
        if locked and descriptor is not None:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
        if descriptor is not None:
            os.close(descriptor)
        process_lock.release()


def _read_canonical_object(path: Path) -> dict[str, Any]:
    metadata = os.lstat(path)
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
        raise ValueError("unsafe analysis run file")
    raw = path.read_bytes()
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid analysis run JSON") from exc
    if not isinstance(value, dict) or canonical_json_bytes(value) != raw:
        raise ValueError("analysis run file is not canonical JSON")
    return value


def _write_immutable_object(path: Path, value: dict[str, Any]) -> bool:
    raw = canonical_json_bytes(value)
    if path.exists():
        if _read_canonical_object(path) != value:
            raise ValueError("immutable analysis run conflict")
        return True
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.parent.is_symlink():
        raise ValueError("unsafe analysis run directory")
    try:
        with path.open("xb") as handle:
            handle.write(raw)
    except FileExistsError as exc:
        raise ValueError("immutable analysis run conflict") from exc
    return False


def _stable_request(
    *,
    project_id: str,
    source_idea_id: str | None,
    snapshot_id: str,
    requested_adapters: list[str],
    allow_deterministic_fallback: bool,
    requested_operations: list[str] | None = None,
) -> dict[str, Any]:
    request = {
        "project_id": project_id,
        "source_idea_id": source_idea_id,
        "source_snapshot_id": snapshot_id,
        "requested_adapters": sorted(requested_adapters),
        "allow_deterministic_fallback": allow_deterministic_fallback,
        "persist_candidates": False,
        "execution_mode": "synchronous",
    }
    if requested_operations is not None:
        request["requested_operations"] = sorted(requested_operations)
    return request


def _resolve_requested_operations(
    effective_adapters: list[str],
    requested_operations: list[str] | None,
) -> list[str]:
    if requested_operations is None:
        return [_DEFAULT_OPERATION_BY_ADAPTER[adapter] for adapter in effective_adapters]
    if not isinstance(requested_operations, list) or not requested_operations:
        raise ValueError("requested_operations must be a non-empty list when provided")
    if len(requested_operations) != len(set(requested_operations)):
        raise ValueError("requested_operations contains duplicates")
    if any(operation_id not in _OPERATION_CONTRACTS for operation_id in requested_operations):
        raise ValueError("unsupported operation selection")
    selected_adapters = {
        _OPERATION_CONTRACTS[operation_id]["adapter_id"]
        for operation_id in requested_operations
    }
    if selected_adapters != set(effective_adapters):
        raise ValueError("requested operation selection does not match requested adapters")
    return sorted(requested_operations)


def _prepare_stable_submission(
    *,
    project_id: str,
    raw_idea: str,
    source_idea_id: str | None,
    requested_adapters: list[str],
    allow_deterministic_fallback: bool,
    requested_operations: list[str] | None = None,
) -> tuple[Any, list[str], list[str], str, str]:
    """Normalize once for both request locking and durable run identity."""

    if not isinstance(raw_idea, str):
        raise ValueError("raw_idea must be a string")
    if not isinstance(requested_adapters, list) or not requested_adapters:
        raise ValueError("requested_adapters must be a non-empty list")
    if len(requested_adapters) != len(set(requested_adapters)):
        raise ValueError("requested_adapters contains duplicates")
    if any(adapter not in SUPPORTED_ADAPTERS for adapter in requested_adapters):
        raise ValueError("unsupported adapter selection")
    if not isinstance(allow_deterministic_fallback, bool):
        raise ValueError("allow_deterministic_fallback must be a bool")
    effective_adapters = list(requested_adapters)
    if allow_deterministic_fallback and "deterministic_fallback" not in effective_adapters:
        effective_adapters.append("deterministic_fallback")
    effective_adapters = sorted(effective_adapters)
    if (
        requested_operations is not None
        and allow_deterministic_fallback
        and "analyze-deterministic-fallback" not in requested_operations
    ):
        requested_operations = [
            *requested_operations,
            "analyze-deterministic-fallback",
        ]
    effective_operations = _resolve_requested_operations(
        effective_adapters, requested_operations
    )
    source_id = source_idea_id or "request-source"
    snapshot = build_exact_source_snapshot(
        project_id=project_id,
        source_document_type="omi",
        source_document_id=source_id,
        source_document_version="1",
        source_ownership="owner_authored",
        source_content=raw_idea,
    )
    request = _stable_request(
        project_id=project_id,
        source_idea_id=source_idea_id,
        snapshot_id=snapshot.identity.snapshot_id,
        requested_adapters=effective_adapters,
        allow_deterministic_fallback=allow_deterministic_fallback,
        requested_operations=(
            effective_operations if requested_operations is not None else None
        ),
    )
    request_hash = canonical_sha256(request)
    return (
        snapshot,
        effective_adapters,
        effective_operations,
        request_hash,
        f"analysis-run-{request_hash[:32]}",
    )


def supported_analysis_tools(
    project_id: str | None = None, *, env: dict[str, str] | None = None
) -> dict[str, Any]:
    preflight = omi_runtime_preflight.build_omi_runtime_preflight_report(project_id, env=env)
    preflight_by_adapter = {item["tool"]: item for item in preflight["tools"]}
    tools = []
    for adapter_id in sorted(SUPPORTED_ADAPTERS):
        readiness = preflight_by_adapter.get(adapter_id)
        tools.append(
            {
                "adapter_id": adapter_id,
                "selectable": True,
                "result_states": sorted(omi_analysis_orchestrator.OMI_ADAPTER_RESULT_STATES),
                "readiness": copy.deepcopy(readiness),
                "fixture_or_injected_runner_supported": True,
                "preflight_status": readiness.get("status") if readiness else "not_configured",
                "preflight_does_not_prove_execution": True,
            }
        )
    return {
        "schema_version": ANALYSIS_RUN_CONTROL_VERSION,
        "project_id": project_id,
        "execution_mode": "synchronous",
        "timeout": {"supported": False, "request_field": None},
        "cancellation": {"supported": False, "route": None},
        "tools": tools,
        "preflight_schema_version": preflight["schema_version"],
        "candidate_persistence": False,
        "automatic_approval_or_promotion": False,
        "memory_canon_mutation": False,
        "story_prose_generation": False,
    }


def _provenance_component(metadata: dict[str, Any], plane: str, state: str) -> ProvenanceComponent:
    supplied = metadata.get(plane)
    if isinstance(supplied, dict):
        return ProvenanceComponent(
            supplied.get("availability", "available" if supplied.get("name") else "unknown"),
            supplied.get("name"),
            supplied.get("version"),
        )
    name = metadata.get(f"{plane}_name")
    version = metadata.get(f"{plane}_version")
    if name is not None:
        return ProvenanceComponent("available", name, version)
    availability = "unavailable" if state in {"unavailable", "skipped", "failed_closed", "error"} else "unknown"
    return ProvenanceComponent(availability)


def _adapter_provenance(
    adapter_id: str,
    operation_id: str,
    state: str,
    finding_provenance: list[dict[str, Any]],
    execution_provenance: dict[str, Any] | None = None,
) -> AdapterProvenance:
    contract = _OPERATION_CONTRACTS[operation_id]
    if contract["adapter_id"] != adapter_id:
        raise ValueError("operation contract does not match adapter identity")
    control_fields = {"tool_source", "adapter", "support", "operation_id"}

    def actual_provenance(item: dict[str, Any]) -> dict[str, Any]:
        claimed_operation_id = item.get("operation_id")
        if claimed_operation_id is not None and claimed_operation_id != operation_id:
            raise ValueError("provenance operation attribution mismatch")
        return {
            key: copy.deepcopy(value)
            for key, value in item.items()
            if key not in control_fields
        }

    supplied = [
        actual
        for item in finding_provenance
        if (actual := actual_provenance(item))
    ]
    execution_metadata = (
        actual_provenance(execution_provenance)
        if execution_provenance is not None
        else None
    )
    if execution_metadata:
        supplied.append(execution_metadata)
    if supplied and any(item != supplied[0] for item in supplied[1:]):
        raise ValueError("conflicting actual provenance for one adapter operation")
    metadata = (
        execution_metadata
        if execution_metadata
        else supplied[0] if supplied else {}
    )
    if adapter_id == "deterministic_fallback":
        default_kind = "fallback"
    elif adapter_id.endswith("_informed_rubric"):
        default_kind = "app_owned"
    else:
        default_kind = "unknown"
    kind = metadata.get("implementation_kind", default_kind)
    if default_kind in {"fallback", "app_owned"} and kind != default_kind:
        raise ValueError("adapter implementation identity cannot be relabeled")
    return AdapterProvenance(
        adapter_id=adapter_id,
        operation_id=operation_id,
        user_facing_label=metadata.get("user_facing_label", contract["label"]),
        implementation_kind=kind,
        tool=_provenance_component(metadata, "tool", state),
        runtime=_provenance_component(metadata, "runtime", state),
        provider=_provenance_component(metadata, "provider", state),
        model=_provenance_component(metadata, "model", state),
    )


def _coverage(adapter_results: list[dict[str, Any]]) -> str:
    states = [item["state"] for item in adapter_results]
    if states and all(state in {"succeeded", "empty"} for state in states):
        return "complete"
    if any(state in {"succeeded", "empty"} for state in states):
        return "partial"
    return "degraded"


def _run_state(coverage: str, result: dict[str, Any]) -> str:
    if result.get("analysis_status") == "error":
        return "error"
    return coverage


def _validate_analysis_result(
    result: Any,
    *,
    selected_adapters: list[str],
    selected_operations: list[str] | None = None,
) -> dict[str, Any]:
    if not isinstance(result, dict):
        raise ValueError("analysis runner returned an invalid result")
    forbidden_keys = {
        "generated_prose", "rewritten_prose", "continuation", "outline",
        "automatic_approval", "promotion", "apply_promotion", "canon",
        "memory_mutation",
    }

    def reject_forbidden(value: Any) -> None:
        if isinstance(value, dict):
            if forbidden_keys & set(value):
                raise ValueError("analysis result crossed a product safety boundary")
            for nested in value.values():
                reject_forbidden(nested)
        elif isinstance(value, list):
            for nested in value:
                reject_forbidden(nested)

    reject_forbidden(result)
    if result.get("analysis_status") not in {"succeeded", "empty", "fail_closed", "error"}:
        raise ValueError("invalid analysis result status")
    envelopes = result.get("adapter_results")
    if not isinstance(envelopes, list):
        raise ValueError("analysis result requires adapter_results")
    validated_envelopes = [
        omi_analysis_orchestrator.validate_adapter_result(item) for item in envelopes
    ]
    identities = [item["adapter"] for item in validated_envelopes]
    if len(identities) != len(set(identities)) or set(identities) != set(selected_adapters):
        raise ValueError("analysis result contributor selection mismatch")
    operations = selected_operations or [
        _DEFAULT_OPERATION_BY_ADAPTER[adapter_id]
        for adapter_id in selected_adapters
    ]
    if len(operations) != len(set(operations)) or any(
        operation_id not in _OPERATION_CONTRACTS for operation_id in operations
    ):
        raise ValueError("analysis result operation selection mismatch")
    supplied_operation_results = result.get("operation_results")
    validated_operation_results: list[dict[str, Any]] = []
    if supplied_operation_results is not None:
        if not isinstance(supplied_operation_results, list):
            raise ValueError("analysis result operation_results must be a list")
        for operation_result in supplied_operation_results:
            if not isinstance(operation_result, dict):
                raise ValueError("analysis operation result must be an object")
            operation_id = operation_result.get("operation_id")
            if operation_id not in operations:
                raise ValueError("analysis result carries an unselected operation")
            envelope = omi_analysis_orchestrator.validate_adapter_result(
                {
                    key: copy.deepcopy(value)
                    for key, value in operation_result.items()
                    if key not in {"operation_id", "original_output"}
                }
            )
            if envelope["adapter"] != _OPERATION_CONTRACTS[operation_id]["adapter_id"]:
                raise ValueError("analysis operation result adapter mismatch")
            validated_operation_result = {"operation_id": operation_id, **envelope}
            if "original_output" in operation_result:
                if not isinstance(operation_result["original_output"], dict):
                    raise ValueError("analysis operation original_output must be an object")
                validated_operation_result["original_output"] = copy.deepcopy(
                    operation_result["original_output"]
                )
            validated_operation_results.append(validated_operation_result)
        if {item["operation_id"] for item in validated_operation_results} != set(operations):
            raise ValueError("analysis result operation selection mismatch")
    else:
        operations_by_adapter: dict[str, list[str]] = {}
        for operation_id in operations:
            operations_by_adapter.setdefault(
                _OPERATION_CONTRACTS[operation_id]["adapter_id"], []
            ).append(operation_id)
        if any(len(operation_ids) != 1 for operation_ids in operations_by_adapter.values()):
            raise ValueError("multi-operation analysis requires operation_results")
        for envelope in validated_envelopes:
            validated_operation_results.append(
                {
                    "operation_id": operations_by_adapter[envelope["adapter"]][0],
                    **copy.deepcopy(envelope),
                }
            )
    findings = result.get("findings")
    if not isinstance(findings, list):
        raise ValueError("analysis result requires findings")
    validated_findings = []
    provenance_extension_fields = {
        "implementation_kind", "user_facing_label", "tool", "runtime",
        "provider", "model", "tool_name", "tool_version", "runtime_name",
        "runtime_version", "provider_name", "provider_version", "model_name",
        "model_version",
    }
    for item in findings:
        validated = omi_analysis_orchestrator.validate_normalized_finding(item)
        original_provenance = item.get("provenance") if isinstance(item, dict) else None
        if isinstance(original_provenance, dict):
            for field in provenance_extension_fields:
                if field in original_provenance:
                    validated["provenance"][field] = copy.deepcopy(
                        original_provenance[field]
                    )
        candidate_operations = [
            operation_id
            for operation_id in operations
            if _OPERATION_CONTRACTS[operation_id]["adapter_id"]
            == validated["source_adapter"]
        ]
        operation_id = validated["provenance"].get("operation_id")
        if operation_id is None and len(candidate_operations) == 1:
            operation_id = candidate_operations[0]
            validated["provenance"]["operation_id"] = operation_id
        if operation_id not in candidate_operations:
            raise ValueError("finding operation attribution is missing or mismatched")
        validated_findings.append(validated)
    if result.get("persisted_candidate_ids", []) != []:
        raise ValueError("analysis control plane cannot persist candidates")
    for field in ("new_candidate_ids", "reused_candidate_ids"):
        if result.get(field, []) != []:
            raise ValueError("analysis control plane cannot persist candidates")
    safety = result.get("safety")
    if not isinstance(safety, dict):
        raise ValueError("analysis result requires a safety envelope")
    for field in ("no_prose", "no_memory_canon_mutation", "no_apply_promotion"):
        if safety.get(field) is not True:
            raise ValueError("analysis result safety boundary is not affirmative")
    runtime_results = [
        item["runtime_execution"]
        for item in validated_operation_results
        if "runtime_execution" in item
    ]
    if runtime_results:
        real_tool_calls_occurred = any(
            item["real_tool_calls_occurred"] for item in runtime_results
        )
        model_calls_occurred = _aggregate_model_call_state(
            validated_operation_results
        )
        if safety.get("no_real_tool_calls") is not (not real_tool_calls_occurred):
            raise ValueError("analysis result misreports real tool execution")
        expected_no_model_calls = (
            None if model_calls_occurred is None else not model_calls_occurred
        )
        if safety.get("no_model_calls") is not expected_no_model_calls:
            raise ValueError("analysis result misreports model execution")
        if safety.get("authorized_real_tool_calls_occurred") is not real_tool_calls_occurred:
            raise ValueError("analysis result misreports authorized tool execution")
        if safety.get("model_calls_occurred") is not model_calls_occurred:
            raise ValueError("analysis result misreports model execution")
        expected_model_call_state = (
            "unknown"
            if model_calls_occurred is None
            else "occurred"
            if model_calls_occurred
            else "not_occurred"
        )
        if safety.get("model_call_state") != expected_model_call_state:
            raise ValueError("analysis result misreports model execution state")
    checked = copy.deepcopy(result)
    checked["adapter_results"] = validated_envelopes
    checked["operation_results"] = validated_operation_results
    checked["findings"] = validated_findings
    return _enforce_t001_control_plane_inputs(checked)


def _enforce_t001_control_plane_inputs(result: dict[str, Any]) -> dict[str, Any]:
    """Keep selected consumers visible without fabricating unavailable inputs."""

    checked = copy.deepcopy(result)
    blocked_adapters = set()
    for envelope in checked["adapter_results"]:
        reason = _UNPROVIDED_CONTROL_PLANE_INPUTS.get(envelope["adapter"])
        if reason is None:
            continue
        blocked_adapters.add(envelope["adapter"])
        if envelope["state"] not in {"unavailable", "skipped", "failed_closed", "error"}:
            envelope["state"] = "unavailable"
            envelope["explanation"] = reason
            envelope["candidates"] = []
    if blocked_adapters:
        for operation_result in checked.get("operation_results", []):
            if operation_result["adapter"] in blocked_adapters:
                operation_result["state"] = "unavailable"
                operation_result["explanation"] = _UNPROVIDED_CONTROL_PLANE_INPUTS[
                    operation_result["adapter"]
                ]
                operation_result["candidates"] = []
        checked["findings"] = [
            finding for finding in checked["findings"]
            if finding["source_adapter"] not in blocked_adapters
        ]
    states = [item["state"] for item in checked["adapter_results"]]
    if (
        checked.get("analysis_status") != "error"
        and states
        and not any(state in {"succeeded", "empty"} for state in states)
    ):
        checked["analysis_status"] = "fail_closed"
    return checked


def _file_ref(
    *, artifact_file_id: str, artifact_type: str, relative_path: str,
    media_type: str, payload: bytes, source_ref: str, evidence_refs: list[str],
    provenance_refs: list[str], record_count: int = 1, line_count: int | None = None,
    schema_name: str = "t003_analysis_support_data", schema_version: str = "1",
    parser_hint: str = "json",
    model_calls_occurred: bool | None = False,
) -> dict[str, Any]:
    return {
        "artifact_file_id": artifact_file_id,
        "artifact_type": artifact_type,
        "relative_path": relative_path,
        "media_type": media_type,
        "encoding": "utf-8",
        "size_bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "record_count": record_count,
        "line_count": line_count,
        "schema_name": schema_name,
        "schema_version": schema_version,
        "parser_hint": parser_hint,
        "source_locator_refs": [source_ref],
        "evidence_refs": evidence_refs,
        "provenance_refs": provenance_refs,
        "boundary_flags": raw_artifact_boundary_flags(
            model_calls_occurred=model_calls_occurred
        ),
    }


def _aggregate_model_call_state(
    operation_results: list[dict[str, Any]],
) -> bool | None:
    states = [
        item["runtime_execution"]["model_calls_occurred"]
        for item in operation_results
        if "runtime_execution" in item
    ]
    if any(state is True for state in states):
        return True
    if any(state is None for state in states):
        return None
    return False


def _ollama_original_output_handoffs(
    result: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    """Build immutable file handoffs for live T007A original outputs only."""

    handoffs: dict[str, dict[str, Any]] = {}
    operation_id = omi_analysis_orchestrator.OMI_OLLAMA_EXACT_SOURCE_OPERATION_ID
    for operation_result in result.get("operation_results", []):
        if operation_result.get("operation_id") != operation_id:
            continue
        runtime_execution = operation_result.get("runtime_execution") or {}
        original_output = operation_result.get("original_output")
        if (
            runtime_execution.get("real_tool_calls_occurred") is not True
            or not isinstance(original_output, dict)
        ):
            continue
        artifact_file_id = f"original-output-{operation_id}"
        handoffs[operation_id] = {
            "artifact_file_id": artifact_file_id,
            "artifact_type": "adapter_metadata",
            "relative_path": f"artifacts/{artifact_file_id}.json",
            "media_type": "application/json",
            "payload": canonical_json_bytes(copy.deepcopy(original_output)),
            "schema_name": omi_analysis_orchestrator.OMI_OLLAMA_LIVE_ORIGINAL_OUTPUT_VERSION,
            "schema_version": "1",
        }
    return handoffs


def _extract_booknlp_raw_artifact_handoffs(
    result: dict[str, Any], snapshot: Any
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    """Validate and detach in-memory BookNLP bytes before result publication."""

    checked = copy.deepcopy(result)
    handoffs: dict[str, dict[str, Any]] = {}
    for envelope in checked["adapter_results"]:
        handoff = envelope.pop("raw_artifacts", None)
        if handoff is None:
            continue
        if envelope["adapter"] != "booknlp":
            raise ValueError("only booknlp may publish a BookNLP raw artifact handoff")
        validated = booknlp_adapter_contract.validate_booknlp_raw_artifact_handoff(
            handoff
        )
        identity = validated["source_identity"]
        if (
            identity["project_id"] != snapshot.identity.project_id
            or identity["snapshot_id"] != snapshot.identity.snapshot_id
            or identity["content_hash"] != snapshot.identity.content_hash
        ):
            raise ValueError("BookNLP raw artifact source identity mismatch")
        handoffs["booknlp"] = validated
    return checked, handoffs


def _exact_finding_evidence_ranges(
    snapshot,
    finding: dict[str, Any],
    *,
    artifact_hashes: dict[str, str] | None = None,
) -> list[tuple[OffsetRange, OffsetRange, str]]:
    """Resolve each validated finding evidence item to one exact source span."""

    resolved = []
    for item in finding["evidence"]:
        locator = item.get("source_locator", item.get("locator"))
        offset_source = locator if isinstance(locator, dict) else item
        if not isinstance(offset_source, dict):
            offset_source = {}
        for field, expected in (
            ("snapshot_id", snapshot.identity.snapshot_id),
            ("snapshot_hash", snapshot.identity.content_hash),
            ("source_hash", snapshot.identity.content_hash),
        ):
            if offset_source.get(field) is not None and offset_source[field] != expected:
                raise ValueError("finding evidence does not match the submitted snapshot")
        char_range = None
        byte_range = None
        char_start = offset_source.get("char_start")
        char_end = offset_source.get("char_end")
        if char_start is not None or char_end is not None:
            if offset_source.get("char_offset_basis") != CHAR_OFFSET_BASIS:
                raise ValueError("finding character offsets lack the exact T002 basis")
            char_range = OffsetRange(char_start, char_end, CHAR_OFFSET_BASIS)
        byte_start = offset_source.get("byte_start")
        byte_end = offset_source.get("byte_end")
        if byte_start is not None or byte_end is not None:
            if offset_source.get("byte_offset_basis") != BYTE_OFFSET_BASIS:
                raise ValueError("finding byte offsets lack the exact T002 basis")
            byte_range = OffsetRange(byte_start, byte_end, BYTE_OFFSET_BASIS)
        if char_range is None and byte_range is None and isinstance(locator, str):
            locator_match = re.fullmatch(r"raw_idea:L1:C([0-9]+)-([0-9]+)", locator)
            if locator_match is not None and finding["source_adapter"] == "spacy":
                char_range = OffsetRange(
                    int(locator_match.group(1)), int(locator_match.group(2)), CHAR_OFFSET_BASIS
                )
            elif locator_match is not None and finding["source_adapter"] == "booknlp":
                byte_range = OffsetRange(
                    int(locator_match.group(1)), int(locator_match.group(2)), BYTE_OFFSET_BASIS
                )
        if char_range is None and byte_range is None:
            if finding["source_adapter"] == "booknlp":
                raise ValueError(
                    "BookNLP evidence requires exact declared byte or character offsets"
                )
            excerpt = item.get("source_excerpt", item.get("excerpt"))
            if not isinstance(excerpt, str) or not excerpt:
                raise ValueError("finding evidence has no exact attributable source span")
            starts = []
            cursor = 0
            while True:
                match = snapshot.source_content.find(excerpt, cursor)
                if match < 0:
                    break
                starts.append(match)
                cursor = match + 1
            if len(starts) != 1:
                raise ValueError("finding evidence excerpt is missing or ambiguous in submitted snapshot")
            char_range = OffsetRange(starts[0], starts[0] + len(excerpt), CHAR_OFFSET_BASIS)
        if char_range is None:
            char_range = translate_exact_offset_range(
                snapshot,
                byte_range,
                target_basis=CHAR_OFFSET_BASIS,
                expected_snapshot_id=snapshot.identity.snapshot_id,
                expected_content_hash=snapshot.identity.content_hash,
            )
        translated_bytes = translate_exact_offset_range(
            snapshot,
            char_range,
            target_basis=BYTE_OFFSET_BASIS,
            expected_snapshot_id=snapshot.identity.snapshot_id,
            expected_content_hash=snapshot.identity.content_hash,
        )
        if byte_range is not None and byte_range != translated_bytes:
            raise ValueError("finding character and byte offsets identify different spans")
        excerpt = item.get("source_excerpt", item.get("excerpt"))
        if isinstance(excerpt, str) and snapshot.source_content[char_range.start:char_range.end] != excerpt:
            raise ValueError("finding evidence excerpt does not match its exact offsets")
        artifact_file_id = offset_source.get("artifact_file_id", "source-artifact")
        if not isinstance(artifact_file_id, str) or not artifact_file_id:
            raise ValueError("finding evidence artifact_file_id is invalid")
        if artifact_file_id != "source-artifact":
            if not artifact_hashes or artifact_file_id not in artifact_hashes:
                raise ValueError("finding evidence references an unavailable raw artifact")
            declared_hash = offset_source.get("artifact_sha256")
            if declared_hash is not None and declared_hash != artifact_hashes[artifact_file_id]:
                raise ValueError("finding evidence raw artifact hash mismatch")
        resolved.append((char_range, translated_bytes, artifact_file_id))
    if not resolved:
        raise ValueError("finding has no exact attributable evidence")
    return resolved


def _story_check_grounding_diagnostics(
    snapshot,
    operation_result: dict[str, Any],
) -> list[dict[str, Any]]:
    """Return source-bound diagnostics from the immutable grounded output."""

    operation_state = operation_result.get("state")
    if operation_state not in {"succeeded", "empty", "failed_closed"}:
        return []
    original_output = operation_result.get("original_output")
    if not isinstance(original_output, dict) or not isinstance(
        original_output.get("grounding"), dict
    ):
        return []
    try:
        validated = omi_analysis_orchestrator.validate_story_check_grounded_result(
            original_output,
            project_name=snapshot.identity.project_id,
            source_id=snapshot.identity.source_id,
            source_content=snapshot.source_content,
        )
    except ValueError:
        if operation_state == "failed_closed":
            return []
        raise
    if operation_state in {"succeeded", "empty"}:
        if validated["state"] != operation_state:
            raise ValueError("Story Check operation state disagrees with grounding output")
        if validated["candidates"] != operation_result["candidates"]:
            raise ValueError("Story Check candidates disagree with grounding output")
    elif validated["candidates"] or operation_result["candidates"]:
        raise ValueError(
            "failed-closed Story Check operation cannot attribute verified candidates"
        )
    return copy.deepcopy(original_output["grounding"]["diagnostics"])


def _story_check_diagnostic_evidence_ranges(
    snapshot,
    diagnostic: dict[str, Any],
) -> list[tuple[OffsetRange, OffsetRange]]:
    """Translate only exact byte evidence retained by the grounding contract."""

    resolved = []
    for reference in diagnostic["evidence"]:
        if reference["source_id"] != snapshot.identity.source_id:
            raise ValueError("Story Check evidence source identity mismatch")
        if reference["source_sha256"] != snapshot.identity.content_hash:
            raise ValueError("Story Check evidence source hash mismatch")
        byte_range = OffsetRange(
            reference["start_byte"], reference["end_byte"], BYTE_OFFSET_BASIS
        )
        character_range = translate_exact_offset_range(
            snapshot,
            byte_range,
            target_basis=CHAR_OFFSET_BASIS,
            expected_snapshot_id=snapshot.identity.snapshot_id,
            expected_content_hash=snapshot.identity.content_hash,
        )
        if (
            snapshot.source_content[character_range.start : character_range.end]
            != reference["excerpt"]
        ):
            raise ValueError("Story Check evidence excerpt mismatch")
        resolved.append((character_range, byte_range))
    return resolved


def _dependency_graph_for_operations(operations: list[OperationDeclaration]) -> tuple[DependencyEdge, ...]:
    edges = []
    for producer in operations:
        for consumer in operations:
            if producer.operation_id == consumer.operation_id:
                continue
            for dependency_class in sorted(set(producer.produces) & set(consumer.consumes)):
                edges.append(
                    DependencyEdge(
                        producer_operation_id=producer.operation_id,
                        consumer_operation_id=consumer.operation_id,
                        dependency_class=dependency_class,
                    )
                )
    return tuple(
        sorted(
            edges,
            key=lambda edge: (
                edge.producer_operation_id,
                edge.consumer_operation_id,
                edge.dependency_class,
            ),
        )
    )


def _build_normalized_evidence_packet(
    *,
    project_id: str,
    run_id: str,
    snapshot: Any,
    producer_operations: dict[str, str],
    findings: list[dict[str, Any]],
    artifact_hashes: dict[str, str] | None = None,
) -> dict[str, Any] | None:
    items = []
    for finding in findings:
        operation_id = finding["provenance"].get("operation_id")
        if operation_id not in producer_operations:
            continue
        validated = omi_analysis_orchestrator.validate_normalized_finding(finding)
        if validated["source_adapter"] != producer_operations[operation_id]:
            raise ValueError("normalized evidence producer attribution mismatch")
        _exact_finding_evidence_ranges(
            snapshot,
            validated,
            artifact_hashes=artifact_hashes,
        )

        def refs(field: str) -> list[str]:
            value = validated.get(field, [])
            if value is None:
                return []
            if not isinstance(value, list) or not all(
                isinstance(item, str) and item for item in value
            ):
                raise ValueError(f"normalized evidence {field} must be list[str]")
            return list(value)

        items.append(
            {
                "producer_operation_id": operation_id,
                "producer_adapter_id": validated["source_adapter"],
                "normalized_finding_id": validated["normalized_finding_id"],
                "finding": validated,
                "source_refs": refs("source_refs"),
                "evidence_refs": refs("evidence_refs"),
                "provenance_refs": refs("provenance_refs"),
                "source_locator_refs": refs("source_locator_refs"),
            }
        )
    if not items:
        return None
    identity = snapshot.identity.to_dict()
    return {
        "schema_version": (
            omi_analysis_orchestrator.OMI_OLLAMA_NORMALIZED_EVIDENCE_PACKET_VERSION
        ),
        "project_id": project_id,
        "run_id": run_id,
        "source_identity": identity,
        "source_snapshot_id": snapshot.identity.snapshot_id,
        "source_content_hash": snapshot.identity.content_hash,
        "consumer_operation_id": (
            omi_analysis_orchestrator.OMI_OLLAMA_NORMALIZED_EVIDENCE_OPERATION_ID
        ),
        "items": items,
    }


def _execute_requested_operations(
    *,
    execute: Callable[..., dict[str, Any]],
    project_id: str,
    raw_idea: str,
    source_idea_id: str | None,
    snapshot: Any,
    run_id: str,
    effective_adapters: list[str],
    effective_operations: list[str],
    operation_runners: dict[str, Callable[..., dict[str, Any]]] | None,
) -> dict[str, Any]:
    def call_upstream(adapters: list[str]) -> dict[str, Any]:
        try:
            return execute(
                project_id,
                raw_idea,
                source_idea_id=source_idea_id,
                persist_candidates=False,
                requested_adapters=adapters,
                allow_deterministic_fallback=False,
            )
        except Exception as exc:
            raise _BoundedAnalysisExecutionError(exc) from exc

    t007b_operation_id = (
        omi_analysis_orchestrator.OMI_OLLAMA_NORMALIZED_EVIDENCE_OPERATION_ID
    )
    if t007b_operation_id not in effective_operations:
        result = call_upstream(effective_adapters)
        return _validate_analysis_result(
            result,
            selected_adapters=effective_adapters,
            selected_operations=effective_operations,
        )
    if operation_runners is not None:
        if not isinstance(operation_runners, dict):
            raise ValueError("operation_runners must be a dict[str, Callable]")
        for operation_id, operation_runner in operation_runners.items():
            if (
                operation_id != t007b_operation_id
                or operation_id not in effective_operations
                or not callable(operation_runner)
            ):
                raise ValueError("operation_runners contains an invalid operation runner")

    upstream_operations = [
        operation_id
        for operation_id in effective_operations
        if operation_id != t007b_operation_id
    ]
    upstream_adapters = [
        _OPERATION_CONTRACTS[operation_id]["adapter_id"]
        for operation_id in upstream_operations
    ]
    if len(upstream_adapters) != len(set(upstream_adapters)):
        raise ValueError("unsupported duplicate-adapter upstream operation selection")
    if upstream_operations:
        upstream_result = call_upstream(upstream_adapters)
        upstream_result = _validate_analysis_result(
            upstream_result,
            selected_adapters=upstream_adapters,
            selected_operations=upstream_operations,
        )
    else:
        upstream_result = {
            "analysis_status": "fail_closed",
            "explanation": "no upstream operations were selected",
            "source_idea_id": source_idea_id,
            "adapter_results": [],
            "operation_results": [],
            "findings": [],
            "persisted_candidate_ids": [],
            "new_candidate_ids": [],
            "reused_candidate_ids": [],
            "safety": omi_analysis_orchestrator.build_orchestrator_safety_envelope(),
        }
    producer_operations = {
        operation_id: _OPERATION_CONTRACTS[operation_id]["adapter_id"]
        for operation_id in upstream_operations
        if "normalized_evidence" in _OPERATION_CONTRACTS[operation_id]["produces"]
        and any(
            result["operation_id"] == operation_id
            and result["state"] == "succeeded"
            for result in upstream_result["operation_results"]
        )
    }
    try:
        packet = _build_normalized_evidence_packet(
            project_id=project_id,
            run_id=run_id,
            snapshot=snapshot,
            producer_operations=producer_operations,
            findings=upstream_result["findings"],
            artifact_hashes={
                item["artifact_file_id"]: item["sha256"]
                for envelope in upstream_result["adapter_results"]
                for item in (envelope.get("raw_artifacts") or {}).get("files", [])
            },
        )
    except ValueError as exc:
        t007b_result = {
            "operation_id": t007b_operation_id,
            "adapter": omi_analysis_orchestrator.OMI_OLLAMA_ADAPTER_NAME,
            "state": "failed_closed",
            "explanation": f"normalized-evidence handoff failed closed: {exc}",
            "candidates": [],
        }
    else:
        t007b_result = omi_analysis_orchestrator.run_ollama_normalized_evidence_operation(
            packet,
            expected_run_id=run_id,
            expected_source_identity=snapshot.identity.to_dict(),
            producer_operations=producer_operations,
            runner=(operation_runners or {}).get(t007b_operation_id),
        )
    operation_results = [
        *copy.deepcopy(upstream_result["operation_results"]),
        copy.deepcopy(t007b_result),
    ]
    adapter_results = copy.deepcopy(upstream_result["adapter_results"])
    if not any(
        item["adapter"] == omi_analysis_orchestrator.OMI_OLLAMA_ADAPTER_NAME
        for item in adapter_results
    ):
        adapter_results.append(
            {
                key: copy.deepcopy(value)
                for key, value in t007b_result.items()
                if key not in {"operation_id", "original_output"}
            }
        )
    findings = [
        *copy.deepcopy(upstream_result["findings"]),
        *copy.deepcopy(t007b_result["candidates"]),
    ]
    findings, fusion_summary = omi_analysis_orchestrator.fuse_normalized_findings(
        findings
    )
    states = [item["state"] for item in operation_results]
    analysis_status = (
        "succeeded"
        if findings
        else "error" if states and all(state == "error" for state in states)
        else "fail_closed"
    )
    real_tool_calls_occurred = any(
        item.get("runtime_execution", {}).get("real_tool_calls_occurred") is True
        for item in operation_results
    )
    model_calls_occurred = _aggregate_model_call_state(operation_results)
    result = {
        "analysis_status": analysis_status,
        "explanation": (
            "Selected operations executed sequentially with normalized evidence "
            "provided only to declared consumers; findings remain candidate-only."
        ),
        "source_idea_id": source_idea_id,
        "adapter_results": adapter_results,
        "operation_results": operation_results,
        "findings": findings,
        "fusion_contract": {
            field: None
            for field in omi_analysis_orchestrator.OMI_FUSION_FINDING_FIELDS
        },
        "fusion_summary": fusion_summary,
        "persisted_candidate_ids": [],
        "new_candidate_ids": [],
        "reused_candidate_ids": [],
        "persistence_status": "not_requested",
        "persistence_explanation": (
            "The T007B control plane does not persist candidates."
        ),
        "safety": omi_analysis_orchestrator.build_orchestrator_safety_envelope(
            real_tool_calls_occurred=real_tool_calls_occurred,
            model_calls_occurred=model_calls_occurred,
        ),
    }
    return _validate_analysis_result(
        result,
        selected_adapters=effective_adapters,
        selected_operations=effective_operations,
    )


def _build_manifest_and_evidence(
    *,
    project_id: str,
    run_id: str,
    snapshot,
    result: dict[str, Any],
    requested_adapters: list[str],
    requested_operations: list[str],
    source_artifact_hash: str,
    result_artifact_hash: str,
    created_at: str,
    raw_artifact_handoffs: dict[str, dict[str, Any]] | None = None,
    original_output_handoffs: dict[str, dict[str, Any]] | None = None,
) -> tuple[AnalysisRunManifest, list[dict[str, Any]]]:
    adapter_results = list(result.get("adapter_results") or [])
    operation_results = list(result.get("operation_results") or [])
    by_operation = {item["operation_id"]: item for item in operation_results}
    operations = []
    contributors = []
    outputs = []
    transformations = []
    evidence_records = []
    findings = list(result.get("findings") or [])
    output_ids_by_operation: dict[str, list[str]] = {
        operation_id: [] for operation_id in requested_operations
    }
    operation_ids_by_adapter: dict[str, list[str]] = {}
    for operation_id in requested_operations:
        operation_ids_by_adapter.setdefault(
            _OPERATION_CONTRACTS[operation_id]["adapter_id"], []
        ).append(operation_id)
    handoffs = raw_artifact_handoffs or {}
    original_handoffs = original_output_handoffs or {}
    booknlp_artifact_hashes = {
        item["artifact_file_id"]: item["sha256"]
        for item in handoffs.get("booknlp", {}).get("files", [])
    }
    story_check_operation_id = omi_analysis_orchestrator.OMI_STORY_CHECK_OPERATION_ID
    story_check_diagnostics = (
        _story_check_grounding_diagnostics(
            snapshot,
            by_operation.get(story_check_operation_id, {}),
        )
        if story_check_operation_id in requested_operations
        else []
    )
    story_check_diagnostics_by_id = {
        diagnostic["diagnostic_id"]: diagnostic
        for diagnostic in story_check_diagnostics
    }
    if len(story_check_diagnostics_by_id) != len(story_check_diagnostics):
        raise ValueError("Story Check grounding diagnostic IDs must be unique")
    whole_span = OffsetRange(0, len(snapshot.source_content), CHAR_OFFSET_BASIS)
    operation_evidence_ids: dict[str, str] = {}
    for operation_id in requested_operations:
        contract = _OPERATION_CONTRACTS[operation_id]
        adapter_id = contract["adapter_id"]
        operation_result = by_operation.get(operation_id) or {
            "adapter": adapter_id,
            "state": "error",
            "explanation": "selected operation returned no attributable result envelope",
            "candidates": [],
        }
        state = operation_result["state"]
        operation_configuration = {
            "execution_mode": "synchronous",
            "adapter_role": contract["role"],
        }
        if "operation_semantics" in contract:
            operation_configuration["operation_semantics"] = contract[
                "operation_semantics"
            ]
        operations.append(
            OperationDeclaration(
                operation_id=operation_id,
                adapter_id=adapter_id,
                consumes=contract["consumes"],
                produces=contract["produces"],
                configuration=operation_configuration,
                feature_flags={"candidate_persistence": False},
            )
        )
        disposition = "validated" if state in {"succeeded", "empty"} else "unverified"
        reason = None if disposition == "validated" else operation_result["explanation"]
        evidence = build_exact_evidence_record(
            snapshot=snapshot,
            run_id=run_id,
            artifact_id=f"bundle-{run_id}",
            artifact_file_id="source-artifact",
            operation_id=operation_id,
            adapter_id=adapter_id,
            disposition=disposition,
            contributor_state=state,
            character_range=whole_span,
            created_at=created_at,
            reason=reason,
        )
        evidence_records.append(evidence)
        operation_evidence_ids[operation_id] = evidence["evidence_id"]
    finding_outputs: list[tuple[dict[str, Any], str, str, str]] = []
    for index, finding in enumerate(findings):
        adapter_id = finding.get("source_adapter")
        if adapter_id not in operation_ids_by_adapter:
            raise ValueError("finding adapter was not selected")
        operation_id = finding.get("provenance", {}).get("operation_id")
        if operation_id not in operation_ids_by_adapter[adapter_id]:
            raise ValueError("finding operation was not selected")
        output_material = str(
            finding.get("normalized_finding_id")
            or finding.get("raw_finding_id")
            or f"finding-{index}"
        )
        if len(operation_ids_by_adapter[adapter_id]) > 1:
            output_material = f"{operation_id}|{output_material}"
        # T002 IDs permit dots/colons but no traversal; prefixing a digest also
        # avoids carrying an unsafe producer-controlled identifier into paths.
        output_id = f"output-{hashlib.sha256(output_material.encode('utf-8')).hexdigest()[:24]}"
        transformation_id = f"transform-{output_id[7:]}"
        output_ids_by_operation[operation_id].append(output_id)
        finding_outputs.append((finding, operation_id, output_id, transformation_id))
    for finding, operation_id, output_id, transformation_id in finding_outputs:
        adapter_id = _OPERATION_CONTRACTS[operation_id]["adapter_id"]
        story_check_diagnostic = None
        if operation_id == story_check_operation_id and story_check_diagnostics:
            story_check_diagnostic = story_check_diagnostics_by_id.get(
                finding.get("raw_finding_id")
            )
            if (
                story_check_diagnostic is None
                or story_check_diagnostic["verification_state"] != "verified"
            ):
                raise ValueError(
                    "Story Check candidate lacks verified grounding lineage"
                )
        output_evidence_ids = []
        finding_artifact_ids: list[str] = []
        for character_range, byte_range, artifact_file_id in _exact_finding_evidence_ranges(
            snapshot,
            finding,
            artifact_hashes=booknlp_artifact_hashes,
        ):
            finding_artifact_ids.append(artifact_file_id)
            output_evidence = build_exact_evidence_record(
                snapshot=snapshot,
                run_id=run_id,
                artifact_id=f"bundle-{run_id}",
                artifact_file_id=artifact_file_id,
                operation_id=operation_id,
                adapter_id=adapter_id,
                disposition="validated",
                contributor_state=by_operation[operation_id]["state"],
                character_range=character_range,
                byte_range=byte_range,
                created_at=created_at,
                transformation_ids=(transformation_id,),
                output_id=output_id,
            )
            evidence_records.append(output_evidence)
            output_evidence_ids.append(output_evidence["evidence_id"])
        normalized_input_ids = tuple(
            output_id_value
            for producer_operation_id in requested_operations
            if "normalized_evidence"
            in _OPERATION_CONTRACTS[producer_operation_id]["produces"]
            for output_id_value in output_ids_by_operation[producer_operation_id]
        )
        consumes_normalized_evidence = (
            "normalized_evidence" in _OPERATION_CONTRACTS[operation_id]["consumes"]
        )
        if consumes_normalized_evidence and not normalized_input_ids:
            raise ValueError("normalized-evidence output lacks upstream output lineage")
        transformation_inputs = (
            normalized_input_ids
            if consumes_normalized_evidence
            else ("result-artifact",)
            if story_check_diagnostic is not None
            else tuple(dict.fromkeys(finding_artifact_ids)) or ("result-artifact",)
        )
        transformations.append(
            TransformationLineage(
                transformation_id=transformation_id,
                operation_id=operation_id,
                transformation_kind=(
                    "normalized_evidence_interpretation"
                    if consumes_normalized_evidence
                    else "validated_normalization"
                ),
                transformation_version="1",
                input_reference_ids=transformation_inputs,
                output_reference_ids=(output_id,),
            )
        )
        outputs.append(
            OutputLineage(
                output_id=output_id,
                operation_id=operation_id,
                source_snapshot_ids=(snapshot.identity.snapshot_id,),
                disposition="validated",
                original_output_reference_id=(
                    original_handoffs[operation_id]["artifact_file_id"]
                    if operation_id in original_handoffs
                    else "result-artifact"
                    if consumes_normalized_evidence or story_check_diagnostic is not None
                    else finding_artifact_ids[0] if finding_artifact_ids else "result-artifact"
                ),
                evidence_reference_ids=tuple(output_evidence_ids),
                transformation_ids=(transformation_id,),
                verification_outcome=(
                    story_check_diagnostic["validator_result"]["outcome"]
                    if story_check_diagnostic is not None
                    else "omi_boundary_validated"
                ),
            )
        )
    for operation_id, handoff in original_handoffs.items():
        if output_ids_by_operation[operation_id]:
            continue
        operation_result = by_operation[operation_id]
        state = operation_result["state"]
        disposition = (
            "validated"
            if state in {"succeeded", "empty"}
            else "rejected"
            if state == "failed_closed"
            else "unverified"
        )
        output_material = f"{operation_id}|original-runtime-output"
        output_id = (
            "output-"
            + hashlib.sha256(output_material.encode("utf-8")).hexdigest()[:24]
        )
        output_ids_by_operation[operation_id].append(output_id)
        outputs.append(
            OutputLineage(
                output_id=output_id,
                operation_id=operation_id,
                source_snapshot_ids=(snapshot.identity.snapshot_id,),
                disposition=disposition,
                original_output_reference_id=handoff["artifact_file_id"],
                evidence_reference_ids=(operation_evidence_ids[operation_id],),
                verification_outcome=(
                    "normalization_accepted"
                    if disposition == "validated"
                    else "normalization_rejected"
                    if disposition == "rejected"
                    else "normalization_unverified"
                ),
                missing_evidence_reason=(
                    operation_result["explanation"]
                    if disposition != "validated"
                    else None
                ),
            )
        )
    candidate_story_check_ids = {
        finding["raw_finding_id"]
        for finding, operation_id, _, _ in finding_outputs
        if operation_id == story_check_operation_id
    }
    for diagnostic in story_check_diagnostics:
        if diagnostic["diagnostic_id"] in candidate_story_check_ids:
            continue
        disposition = (
            "validated"
            if diagnostic["verification_state"] == "verified"
            else diagnostic["verification_state"]
        )
        validator_result = diagnostic["validator_result"]
        reason = ",".join(validator_result["reason_codes"])
        output_material = (
            f"{story_check_operation_id}|grounding|{diagnostic['diagnostic_id']}"
        )
        output_id = (
            "output-"
            + hashlib.sha256(output_material.encode("utf-8")).hexdigest()[:24]
        )
        output_evidence_ids = []
        for character_range, byte_range in _story_check_diagnostic_evidence_ranges(
            snapshot, diagnostic
        ):
            output_evidence = build_exact_evidence_record(
                snapshot=snapshot,
                run_id=run_id,
                artifact_id=f"bundle-{run_id}",
                artifact_file_id="source-artifact",
                operation_id=story_check_operation_id,
                adapter_id=omi_analysis_orchestrator.OMI_STORY_CHECK_ADAPTER_NAME,
                disposition=disposition,
                contributor_state=by_operation[story_check_operation_id]["state"],
                character_range=character_range,
                byte_range=byte_range,
                created_at=created_at,
                output_id=output_id,
                reason=None if disposition == "validated" else reason,
            )
            evidence_records.append(output_evidence)
            output_evidence_ids.append(output_evidence["evidence_id"])
        output_ids_by_operation[story_check_operation_id].append(output_id)
        outputs.append(
            OutputLineage(
                output_id=output_id,
                operation_id=story_check_operation_id,
                source_snapshot_ids=(snapshot.identity.snapshot_id,),
                disposition=disposition,
                original_output_reference_id="result-artifact",
                evidence_reference_ids=tuple(output_evidence_ids),
                verification_outcome=validator_result["outcome"],
                missing_evidence_reason=(
                    reason if disposition != "validated" else None
                ),
            )
        )
    coverage = _coverage(operation_results)
    for operation_id in requested_operations:
        adapter_id = _OPERATION_CONTRACTS[operation_id]["adapter_id"]
        operation_result = by_operation.get(operation_id) or {
            "state": "error",
            "explanation": "selected operation returned no attributable result envelope",
        }
        state = operation_result["state"]
        contributors.append(
            ContributorLineage(
                operation_id=operation_id,
                adapter_id=adapter_id,
                source_snapshot_ids=(snapshot.identity.snapshot_id,),
                result_state=state,
                coverage="complete" if state in {"succeeded", "empty"} else "none",
                explanation=operation_result["explanation"],
                provenance=_adapter_provenance(
                    adapter_id,
                    operation_id,
                    state,
                    ([handoffs[adapter_id]["provenance"]] if adapter_id in handoffs else []) + [
                        finding["provenance"] for finding in findings
                        if finding["source_adapter"] == adapter_id
                        and finding["provenance"].get("operation_id") == operation_id
                    ],
                    operation_result.get("execution_provenance"),
                ),
                output_ids=tuple(output_ids_by_operation[operation_id]),
            )
        )
    manifest = AnalysisRunManifest(
        run_id=run_id,
        project_id=project_id,
        sources=(snapshot.identity,),
        operations=tuple(operations),
        dependency_graph=_dependency_graph_for_operations(operations),
        contributors=tuple(contributors),
        artifact_references=(
            ArtifactReference(
                artifact_id="result-artifact",
                availability="available",
                source_snapshot_ids=(snapshot.identity.snapshot_id,),
                content_hash=result_artifact_hash,
                hash_algorithm="sha256",
                media_type="application/json",
            ),
            ArtifactReference(
                artifact_id="source-artifact",
                availability="available",
                source_snapshot_ids=(snapshot.identity.snapshot_id,),
                content_hash=source_artifact_hash,
                hash_algorithm="sha256",
                media_type="text/plain",
            ),
            *tuple(
                ArtifactReference(
                    artifact_id=item["artifact_file_id"],
                    availability="available",
                    source_snapshot_ids=(snapshot.identity.snapshot_id,),
                    content_hash=item["sha256"],
                    hash_algorithm="sha256",
                    media_type=item["media_type"],
                )
                for handoff in handoffs.values()
                for item in handoff["files"]
            ),
            *tuple(
                ArtifactReference(
                    artifact_id=item["artifact_file_id"],
                    availability="available",
                    source_snapshot_ids=(snapshot.identity.snapshot_id,),
                    content_hash=hashlib.sha256(item["payload"]).hexdigest(),
                    hash_algorithm="sha256",
                    media_type=item["media_type"],
                )
                for item in original_handoffs.values()
            ),
        ),
        outputs=tuple(outputs),
        transformations=tuple(transformations),
        coverage=coverage,
        created_at=created_at,
        finalized_at=created_at,
        configuration={"execution_mode": "synchronous", "retention": "explicit-owner-deletion-only"},
        feature_flags={"candidate_first": True, "automatic_promotion": False},
    )
    return manifest, evidence_records


def _find_idempotency_record(
    project_dir: Path, *, idempotency_key: str, request_hash: str
) -> dict[str, Any] | None:
    runs_root = project_dir / "writer_assistant" / "analysis_runs"
    if not runs_root.exists():
        return None
    if runs_root.is_symlink() or not runs_root.is_dir():
        raise ValueError("unsafe analysis runs directory")
    match = None
    for child in sorted(runs_root.iterdir(), key=lambda path: os.fsencode(path.name)):
        if child.is_symlink() or not child.is_dir():
            raise ValueError("unsafe analysis run entry")
        record_path = child / "run.json"
        if not record_path.exists():
            continue
        record = _validate_run_record(_read_canonical_object(record_path))
        if record.get("idempotency_key") != idempotency_key:
            continue
        if record["request_hash"] != request_hash:
            raise ValueError("analysis run idempotency conflict")
        if match is not None:
            raise ValueError("duplicate analysis idempotency record")
        match = record
    return match


def _submit_analysis_run_locked(
    project_id: str,
    *,
    raw_idea: str,
    source_idea_id: str | None,
    snapshot: Any,
    effective_adapters: list[str],
    effective_operations: list[str],
    request_hash: str,
    run_id: str,
    idempotency_key: str | None = None,
    runner: Callable[..., dict[str, Any]] | None = None,
    operation_runners: dict[str, Callable[..., dict[str, Any]]] | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    """Execute and durably finalize one deterministic synchronous run."""

    project_dir = _project_dir(project_id)
    if idempotency_key is not None and (
        not isinstance(idempotency_key, str) or not idempotency_key or ".." in idempotency_key
    ):
        raise ValueError("idempotency_key must be a safe non-empty string")
    run_path = analysis_run_dir(project_dir, run_id)
    record_path = run_path / "run.json"
    if idempotency_key is not None:
        matched_record = _find_idempotency_record(
            project_dir, idempotency_key=idempotency_key, request_hash=request_hash
        )
        if matched_record is not None:
            existing = get_analysis_run_status(project_id, matched_record["run_id"])
            existing["idempotent_replay"] = True
            return existing
    if record_path.exists():
        existing = get_analysis_run_status(project_id, run_id)
        if existing["request_hash"] != request_hash:
            raise ValueError("analysis run replay conflict")
        if idempotency_key is not None and existing["idempotency_key"] != idempotency_key:
            raise ValueError("analysis run idempotency conflict")
        existing["idempotent_replay"] = True
        return existing
    timestamp = created_at or _now()
    execute = runner or omi_analysis_orchestrator.analyze_omi_raw_idea_with_tools
    try:
        result = _execute_requested_operations(
            execute=execute,
            project_id=project_id,
            raw_idea=raw_idea,
            source_idea_id=source_idea_id,
            snapshot=snapshot,
            run_id=run_id,
            effective_adapters=effective_adapters,
            effective_operations=effective_operations,
            operation_runners=operation_runners,
        )
    except _BoundedAnalysisExecutionError as bounded_exc:
        exc = bounded_exc.original
        result = {
            "analysis_status": "error",
            "explanation": f"bounded synchronous analysis error: {type(exc).__name__}",
            "source_idea_id": source_idea_id,
            "adapter_results": [
                {
                    "adapter": adapter,
                    "state": "error",
                    "explanation": f"adapter run ended in controlled error: {type(exc).__name__}",
                    "candidates": [],
                }
                for adapter in effective_adapters
            ],
            "operation_results": [
                {
                    "operation_id": operation_id,
                    "adapter": _OPERATION_CONTRACTS[operation_id]["adapter_id"],
                    "state": "error",
                    "explanation": (
                        f"operation run ended in controlled error: {type(exc).__name__}"
                    ),
                    "candidates": [],
                }
                for operation_id in effective_operations
            ],
            "findings": [],
            "persisted_candidate_ids": [],
            "safety": omi_analysis_orchestrator.build_orchestrator_safety_envelope(),
        }
    result = _validate_analysis_result(
        result,
        selected_adapters=effective_adapters,
        selected_operations=effective_operations,
    )
    result, raw_artifact_handoffs = _extract_booknlp_raw_artifact_handoffs(
        result, snapshot
    )
    original_output_handoffs = _ollama_original_output_handoffs(result)
    model_calls_occurred = _aggregate_model_call_state(
        result.get("operation_results", [])
    )
    source_payload = raw_idea.encode("utf-8")
    result_payload = canonical_json_bytes(result)
    manifest, evidence_records = _build_manifest_and_evidence(
        project_id=project_id,
        run_id=run_id,
        snapshot=snapshot,
        result=result,
        requested_adapters=effective_adapters,
        requested_operations=effective_operations,
        source_artifact_hash=hashlib.sha256(source_payload).hexdigest(),
        result_artifact_hash=hashlib.sha256(result_payload).hexdigest(),
        created_at=timestamp,
        raw_artifact_handoffs=raw_artifact_handoffs,
        original_output_handoffs=original_output_handoffs,
    )
    manifest_dict = manifest.to_dict()
    manifest_hash = canonical_sha256(manifest_dict)
    manifest_path = run_path / "manifest.json"
    _write_immutable_object(manifest_path, manifest_dict)
    evidence_ids = [record["evidence_id"] for record in evidence_records]
    adapter_operation_counts = {
        adapter_id: sum(
            _OPERATION_CONTRACTS[operation_id]["adapter_id"] == adapter_id
            for operation_id in effective_operations
        )
        for adapter_id in effective_adapters
    }
    contributor_ref_by_operation = {
        operation_id: (
            f"contributor-{operation_id}"
            if adapter_operation_counts[_OPERATION_CONTRACTS[operation_id]["adapter_id"]] > 1
            else f"contributor-{_OPERATION_CONTRACTS[operation_id]['adapter_id']}"
        )
        for operation_id in effective_operations
    }
    provenance_refs = list(contributor_ref_by_operation.values())
    bundle_id = f"bundle-{run_id}"
    files = [
        _file_ref(
            artifact_file_id="source-artifact",
            artifact_type="source_snapshot",
            relative_path="artifacts/source.txt",
            media_type="text/plain",
            payload=source_payload,
            source_ref=snapshot.identity.snapshot_id,
            evidence_refs=evidence_ids,
            provenance_refs=provenance_refs,
            model_calls_occurred=model_calls_occurred,
        ),
        _file_ref(
            artifact_file_id="result-artifact",
            artifact_type="adapter_metadata",
            relative_path="artifacts/result.json",
            media_type="application/json",
            payload=result_payload,
            source_ref=snapshot.identity.snapshot_id,
            evidence_refs=evidence_ids,
            provenance_refs=provenance_refs,
            model_calls_occurred=model_calls_occurred,
        ),
    ]
    raw_payloads: dict[str, bytes] = {
        "source-artifact": source_payload,
        "result-artifact": result_payload,
    }
    for adapter_id, handoff in raw_artifact_handoffs.items():
        for item in handoff["files"]:
            payload = item["payload"].encode("utf-8")
            files.append(
                _file_ref(
                    artifact_file_id=item["artifact_file_id"],
                    artifact_type=item["artifact_type"],
                    relative_path=item["relative_path"],
                    media_type=item["media_type"],
                    payload=payload,
                    source_ref=snapshot.identity.snapshot_id,
                    evidence_refs=evidence_ids,
                    provenance_refs=[
                        contributor_ref_by_operation[
                            next(
                                operation_id
                                for operation_id in effective_operations
                                if _OPERATION_CONTRACTS[operation_id]["adapter_id"]
                                == adapter_id
                            )
                        ]
                    ],
                    record_count=item["record_count"],
                    line_count=item["line_count"],
                    schema_name=item["schema_name"],
                    schema_version=item["schema_version"],
                    parser_hint=item["parser_hint"],
                    model_calls_occurred=model_calls_occurred,
                )
            )
            raw_payloads[item["artifact_file_id"]] = payload
    for operation_id, item in original_output_handoffs.items():
        files.append(
            _file_ref(
                artifact_file_id=item["artifact_file_id"],
                artifact_type=item["artifact_type"],
                relative_path=item["relative_path"],
                media_type=item["media_type"],
                payload=item["payload"],
                source_ref=snapshot.identity.snapshot_id,
                evidence_refs=evidence_ids,
                provenance_refs=[contributor_ref_by_operation[operation_id]],
                schema_name=item["schema_name"],
                schema_version=item["schema_version"],
                model_calls_occurred=model_calls_occurred,
            )
        )
        raw_payloads[item["artifact_file_id"]] = item["payload"]
    raw_manifest = build_immutable_raw_artifact_manifest(
        project_id=project_id,
        run_id=run_id,
        raw_artifact_bundle_id=bundle_id,
        artifact_files=files,
        analysis_run_manifest_hash=manifest_hash,
        created_at=timestamp,
        source_refs=[snapshot.identity.snapshot_id],
        evidence_refs=evidence_ids,
        provenance_refs=provenance_refs,
        source_locator_refs=[snapshot.identity.snapshot_id],
        adapter_name="omi_analysis_control",
        adapter_version="1",
        model_calls_occurred=model_calls_occurred,
    )
    write_immutable_raw_artifact_bundle(
        raw_manifest,
        raw_payloads,
        project_dir=project_manager.REPO_ROOT,
    )
    append_evidence_ledger_event(
        project_dir=project_dir,
        project_id=project_id,
        run_id=run_id,
        event_type="artifact_recorded",
        idempotency_key="artifact-bundle",
        created_at=timestamp,
        payload={
            "artifact_id": bundle_id,
            "artifact_manifest_hash": raw_manifest["manifest_hash"],
            "artifact_bundle_hash": raw_manifest["bundle_hash"],
            "analysis_run_manifest_hash": manifest_hash,
            "source_snapshot_ids": [snapshot.identity.snapshot_id],
            "availability": "available",
        },
    )
    for record in evidence_records:
        append_evidence_ledger_event(
            project_dir=project_dir,
            project_id=project_id,
            run_id=run_id,
            event_type="evidence_recorded",
            idempotency_key=record["evidence_id"],
            created_at=timestamp,
            payload=record,
        )
    for output in manifest_dict["outputs"]:
        append_evidence_ledger_event(
            project_dir=project_dir,
            project_id=project_id,
            run_id=run_id,
            event_type="output_recorded",
            idempotency_key=output["output_id"],
            created_at=timestamp,
            payload=output,
        )
    for contributor in manifest_dict["contributors"]:
        append_evidence_ledger_event(
            project_dir=project_dir,
            project_id=project_id,
            run_id=run_id,
            event_type="contributor_recorded",
            idempotency_key=contributor_ref_by_operation[
                contributor["operation_id"]
            ],
            created_at=timestamp,
            payload=contributor,
        )
    chain = scan_evidence_ledger(project_dir=project_dir, project_id=project_id, run_id=run_id)
    record = {
        "schema_version": ANALYSIS_RUN_RECORD_VERSION,
        "project_id": project_id,
        "run_id": run_id,
        "request_hash": request_hash,
        "idempotency_key": idempotency_key,
        "state": _run_state(manifest.coverage, result),
        "coverage": manifest.coverage,
        "analysis_status": result.get("analysis_status"),
        "created_at": timestamp,
        "finalized_at": timestamp,
        "execution_mode": "synchronous",
        "timeout_supported": False,
        "cancellation_supported": False,
        "manifest_ref": {
            "contract_version": manifest.contract_version,
            "manifest_hash": manifest_hash,
            "relative_path": "manifest.json",
        },
        "raw_artifact_ref": {
            "schema_version": IMMUTABLE_RAW_ARTIFACT_VERSION,
            "artifact_id": bundle_id,
            "manifest_hash": raw_manifest["manifest_hash"],
            "bundle_hash": raw_manifest["bundle_hash"],
        },
        "evidence_ledger_ref": {
            "schema_version": EVIDENCE_LEDGER_VERSION,
            "event_count_at_finalization": len(chain),
            "head_hash_at_finalization": chain[-1]["event_hash"] if chain else None,
        },
        "candidate_persistence_performed": False,
        "automatic_approval_or_promotion_performed": False,
        "memory_canon_mutation_performed": False,
        "story_prose_generated": False,
    }
    record["record_hash"] = canonical_sha256(record)
    _write_immutable_object(record_path, record)
    response = _status_response(record, chain)
    response["idempotent_replay"] = False
    return response


def submit_analysis_run(
    project_id: str,
    *,
    raw_idea: str,
    source_idea_id: str | None,
    requested_adapters: list[str],
    requested_operations: list[str] | None = None,
    allow_deterministic_fallback: bool = False,
    idempotency_key: str | None = None,
    runner: Callable[..., dict[str, Any]] | None = None,
    operation_runners: dict[str, Callable[..., dict[str, Any]]] | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    """Serialize one project-scoped logical submission before execution."""

    project_dir = _project_dir(project_id)
    if idempotency_key is not None and (
        not isinstance(idempotency_key, str)
        or not idempotency_key
        or len(idempotency_key) > 256
        or ".." in idempotency_key
        or "/" in idempotency_key
        or "\\" in idempotency_key
    ):
        raise ValueError("idempotency_key must be a safe non-empty string")
    (
        snapshot,
        effective_adapters,
        effective_operations,
        request_hash,
        run_id,
    ) = _prepare_stable_submission(
        project_id=project_id,
        raw_idea=raw_idea,
        source_idea_id=source_idea_id,
        requested_adapters=requested_adapters,
        allow_deterministic_fallback=allow_deterministic_fallback,
        requested_operations=requested_operations,
    )
    request_scope = f"request:{request_hash}"

    def execute_under_request_lock():
        with _acquire_submission_lock(
            project_dir=project_dir, project_id=project_id, scope=request_scope
        ):
            return _submit_analysis_run_locked(
                project_id,
                raw_idea=raw_idea,
                source_idea_id=source_idea_id,
                snapshot=snapshot,
                effective_adapters=effective_adapters,
                effective_operations=effective_operations,
                request_hash=request_hash,
                run_id=run_id,
                idempotency_key=idempotency_key,
                runner=runner,
                operation_runners=operation_runners,
                created_at=created_at,
            )

    if idempotency_key is None:
        return execute_under_request_lock()
    with _acquire_submission_lock(
        project_dir=project_dir,
        project_id=project_id,
        scope=f"idempotency:{idempotency_key}",
    ):
        return execute_under_request_lock()


def _validate_run_record(record: dict[str, Any]) -> dict[str, Any]:
    value = copy.deepcopy(record)
    required = {
        "schema_version", "project_id", "run_id", "request_hash",
        "idempotency_key", "state", "coverage", "analysis_status",
        "created_at", "finalized_at", "execution_mode", "timeout_supported",
        "cancellation_supported", "manifest_ref", "raw_artifact_ref",
        "evidence_ledger_ref", "candidate_persistence_performed",
        "automatic_approval_or_promotion_performed",
        "memory_canon_mutation_performed", "story_prose_generated", "record_hash",
    }
    if set(value) != required:
        raise ValueError("analysis run record fields are not closed")
    if value.get("schema_version") != ANALYSIS_RUN_RECORD_VERSION:
        raise ValueError("unsupported analysis run record version")
    recorded_hash = value.pop("record_hash", None)
    if recorded_hash != canonical_sha256(value):
        raise ValueError("analysis run record hash mismatch")
    value["record_hash"] = recorded_hash
    if value.get("state") not in ANALYSIS_RUN_STATES:
        raise ValueError("invalid analysis run state")
    if value.get("execution_mode") != "synchronous":
        raise ValueError("unsupported analysis execution mode")
    if value.get("timeout_supported") is not False or value.get("cancellation_supported") is not False:
        raise ValueError("unsupported control capability claimed")
    if value["manifest_ref"].get("relative_path") != "manifest.json":
        raise ValueError("unsafe analysis manifest path")
    for boundary in (
        "candidate_persistence_performed",
        "automatic_approval_or_promotion_performed",
        "memory_canon_mutation_performed",
        "story_prose_generated",
    ):
        if value[boundary] is not False:
            raise ValueError("analysis run crossed a product safety boundary")
    return value


def _status_response(record: dict[str, Any], chain) -> dict[str, Any]:
    value = copy.deepcopy(record)
    value["evidence_ledger_ref"]["current_event_count"] = len(chain)
    value["evidence_ledger_ref"]["current_head_hash"] = chain[-1]["event_hash"] if chain else None
    value["idempotent_replay"] = False
    return value


def get_analysis_run_status(project_id: str, run_id: str) -> dict[str, Any]:
    project_dir = _project_dir(project_id)
    run_path = analysis_run_dir(project_dir, run_id)
    record = _validate_run_record(_read_canonical_object(run_path / "run.json"))
    if record["project_id"] != project_id or record["run_id"] != run_id:
        raise ValueError("analysis run storage linkage mismatch")
    manifest = _read_canonical_object(run_path / record["manifest_ref"]["relative_path"])
    if canonical_sha256(manifest) != record["manifest_ref"]["manifest_hash"]:
        raise ValueError("analysis run manifest tamper detected")
    chain = scan_evidence_ledger(project_dir=project_dir, project_id=project_id, run_id=run_id)
    return _status_response(record, chain)


def get_analysis_run_result(project_id: str, run_id: str) -> dict[str, Any]:
    status = get_analysis_run_status(project_id, run_id)
    artifact_id = status["raw_artifact_ref"]["artifact_id"]
    artifact = read_immutable_raw_artifact_bundle(
        project_id, artifact_id, project_dir=project_manager.REPO_ROOT
    )
    if artifact.get("status") == "deletion_in_progress":
        return {
            "project_id": project_id,
            "run_id": run_id,
            "state": status["state"],
            "artifact_status": "deletion_in_progress",
            "deletion_state": "in_progress",
            "result_available": False,
            "content_available": artifact["content_available"],
            "replayable": False,
            "deletion_intent": artifact["deletion_intent"],
            "manifest_ref": status["manifest_ref"],
            "evidence_ledger_ref": status["evidence_ledger_ref"],
        }
    if artifact.get("status") == "deleted":
        return {
            "project_id": project_id,
            "run_id": run_id,
            "state": status["state"],
            "artifact_status": "deleted",
            "result_available": False,
            "replayable": False,
            "tombstone": artifact["tombstone"],
            "manifest_ref": status["manifest_ref"],
            "evidence_ledger_ref": status["evidence_ledger_ref"],
        }
    result_ref = next(
        item for item in artifact["artifact_files"] if item["artifact_file_id"] == "result-artifact"
    )
    bundle_dir = (
        project_manager.REPO_ROOT / "projects" / project_id / "writer_assistant"
        / "raw_artifacts" / artifact_id
    )
    path = bundle_dir / result_ref["relative_path"]
    metadata = os.lstat(path)
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
        raise ValueError("unsafe analysis result artifact")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != result_ref["sha256"]:
        raise ValueError("analysis result artifact tamper detected")
    result = json.loads(raw.decode("utf-8"))
    return {
        "project_id": project_id,
        "run_id": run_id,
        "state": status["state"],
        "artifact_status": "retained",
        "result_available": True,
        "replayable": True,
        "result": result,
        "manifest_ref": status["manifest_ref"],
        "raw_artifact_ref": status["raw_artifact_ref"],
        "evidence_ledger_ref": status["evidence_ledger_ref"],
    }


def _delete_analysis_run_artifacts_locked(
    project_id: str,
    run_id: str,
    *,
    deletion_id: str,
    deleted_at: str | None = None,
    owner_controlled: bool,
) -> dict[str, Any]:
    project_dir = _project_dir(project_id)
    status = get_analysis_run_status(project_id, run_id)
    timestamp = deleted_at or _now()
    chain = scan_evidence_ledger(project_dir=project_dir, project_id=project_id, run_id=run_id)
    result = delete_immutable_raw_artifact_bundle(
        project_id,
        status["raw_artifact_ref"]["artifact_id"],
        project_dir=project_manager.REPO_ROOT,
        deleted_at=timestamp,
        deletion_id=deletion_id,
        owner_controlled=owner_controlled,
        ledger_head_hash=chain[-1]["event_hash"] if chain else None,
    )
    append_evidence_ledger_event(
        project_dir=project_dir,
        project_id=project_id,
        run_id=run_id,
        event_type="artifact_deleted",
        idempotency_key=deletion_id,
        created_at=timestamp,
        payload=result["tombstone"],
    )
    return {
        **result,
        "project_id": project_id,
        "run_id": run_id,
        "candidate_review_promotion_approved_stores_mutated": False,
    }


def delete_analysis_run_artifacts(
    project_id: str,
    run_id: str,
    *,
    deletion_id: str,
    deleted_at: str | None = None,
    owner_controlled: bool,
) -> dict[str, Any]:
    project_dir = _project_dir(project_id)
    with _acquire_submission_lock(
        project_dir=project_dir,
        project_id=project_id,
        scope=f"deletion:{run_id}",
    ):
        return _delete_analysis_run_artifacts_locked(
            project_id,
            run_id,
            deletion_id=deletion_id,
            deleted_at=deleted_at,
            owner_controlled=owner_controlled,
        )


__all__ = [
    "ANALYSIS_RUN_RECORD_VERSION",
    "ANALYSIS_RUN_CONTROL_VERSION",
    "ANALYSIS_RUN_STATES",
    "analysis_run_dir",
    "supported_analysis_tools",
    "submit_analysis_run",
    "get_analysis_run_status",
    "get_analysis_run_result",
    "delete_analysis_run_artifacts",
]
