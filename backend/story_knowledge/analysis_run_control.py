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

_ADAPTER_OPERATION_CONTRACT = {
    "spacy": {
        "consumes": ("owner_selected_source",),
        "produces": ("raw_extraction_evidence", "normalized_evidence"),
        "role": "source_evidence_producer",
        "label": "spaCy evidence production",
    },
    "booknlp": {
        "consumes": ("owner_selected_source",),
        "produces": ("raw_extraction_evidence", "normalized_evidence"),
        "role": "source_evidence_producer",
        "label": "BookNLP evidence production",
    },
    "ollama_model": {
        "consumes": ("owner_selected_source",),
        "produces": ("diagnostic_candidate_finding",),
        "role": "exact_source_structured_extractor",
        "label": "Ollama exact-source structured extraction",
    },
    "story_check": {
        "consumes": ("owner_selected_source",),
        "produces": ("diagnostic_candidate_finding",),
        "role": "grounded_diagnostic_consumer",
        "label": "Story Check grounded diagnostics",
    },
    "subtxt_informed_rubric": {
        "consumes": ("owner_selected_source",),
        "produces": ("diagnostic_candidate_finding",),
        "role": "app_owned_direct_source_rubric",
        "label": "App-owned Subtxt-informed rubric",
    },
    "dramatica_flow_informed_rubric": {
        "consumes": ("owner_selected_source",),
        "produces": ("diagnostic_candidate_finding",),
        "role": "app_owned_direct_source_rubric",
        "label": "App-owned dramatica-flow-informed rubric",
    },
    "deterministic_fallback": {
        "consumes": ("owner_selected_source",),
        "produces": ("diagnostic_candidate_finding",),
        "role": "fallback_safety_baseline",
        "label": "Deterministic fallback analysis",
    },
    "subtxt": {
        "consumes": ("normalized_evidence",),
        "produces": ("diagnostic_candidate_finding",),
        "role": "normalized_evidence_consumer",
        "label": "Subtxt normalized-evidence interpretation",
    },
    "dramatica_flow": {
        "consumes": ("normalized_evidence",),
        "produces": ("diagnostic_candidate_finding",),
        "role": "normalized_evidence_consumer",
        "label": "dramatica-flow normalized-evidence interpretation",
    },
    "ncp": {
        "consumes": ("imported_artifact",),
        "produces": ("gateway_input_output",),
        "role": "gateway_import_export",
        "label": "NCP gateway/import-export",
    },
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
) -> dict[str, Any]:
    return {
        "project_id": project_id,
        "source_idea_id": source_idea_id,
        "source_snapshot_id": snapshot_id,
        "requested_adapters": sorted(requested_adapters),
        "allow_deterministic_fallback": allow_deterministic_fallback,
        "persist_candidates": False,
        "execution_mode": "synchronous",
    }


def _prepare_stable_submission(
    *,
    project_id: str,
    raw_idea: str,
    source_idea_id: str | None,
    requested_adapters: list[str],
    allow_deterministic_fallback: bool,
) -> tuple[Any, list[str], str, str]:
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
    )
    request_hash = canonical_sha256(request)
    return snapshot, effective_adapters, request_hash, f"analysis-run-{request_hash[:32]}"


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
) -> AdapterProvenance:
    contract = _ADAPTER_OPERATION_CONTRACT[adapter_id]
    supplied = [
        {key: copy.deepcopy(value) for key, value in item.items() if key not in {"tool_source", "adapter", "support"}}
        for item in finding_provenance
        if any(key not in {"tool_source", "adapter", "support"} for key in item)
    ]
    if supplied and any(item != supplied[0] for item in supplied[1:]):
        raise ValueError("conflicting actual provenance for one adapter operation")
    metadata = supplied[0] if supplied else {}
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
    result: Any, *, selected_adapters: list[str]
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
    checked = copy.deepcopy(result)
    checked["adapter_results"] = validated_envelopes
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
    provenance_refs: list[str],
) -> dict[str, Any]:
    from backend.story_knowledge.raw_artifacts import _REQUIRED_BOUNDARY_FLAGS

    return {
        "artifact_file_id": artifact_file_id,
        "artifact_type": artifact_type,
        "relative_path": relative_path,
        "media_type": media_type,
        "encoding": "utf-8",
        "size_bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "record_count": 1,
        "line_count": None,
        "schema_name": "t003_analysis_support_data",
        "schema_version": "1",
        "parser_hint": "json",
        "source_locator_refs": [source_ref],
        "evidence_refs": evidence_refs,
        "provenance_refs": provenance_refs,
        "boundary_flags": sorted(_REQUIRED_BOUNDARY_FLAGS),
    }


def _exact_finding_evidence_ranges(snapshot, finding: dict[str, Any]) -> list[tuple[OffsetRange, OffsetRange]]:
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
        resolved.append((char_range, translated_bytes))
    if not resolved:
        raise ValueError("finding has no exact attributable evidence")
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


def _build_manifest_and_evidence(
    *,
    project_id: str,
    run_id: str,
    snapshot,
    result: dict[str, Any],
    requested_adapters: list[str],
    source_artifact_hash: str,
    result_artifact_hash: str,
    created_at: str,
) -> tuple[AnalysisRunManifest, list[dict[str, Any]]]:
    adapter_results = list(result.get("adapter_results") or [])
    by_adapter = {item["adapter"]: item for item in adapter_results}
    operations = []
    contributors = []
    outputs = []
    transformations = []
    evidence_records = []
    findings = list(result.get("findings") or [])
    output_ids_by_adapter: dict[str, list[str]] = {adapter: [] for adapter in requested_adapters}
    whole_span = OffsetRange(0, len(snapshot.source_content), CHAR_OFFSET_BASIS)
    for adapter_id in requested_adapters:
        operation_id = f"analyze-{adapter_id.replace('_', '-')}"
        adapter_result = by_adapter.get(adapter_id) or {
            "adapter": adapter_id,
            "state": "error",
            "explanation": "selected adapter returned no attributable result envelope",
            "candidates": [],
        }
        state = adapter_result["state"]
        contract = _ADAPTER_OPERATION_CONTRACT[adapter_id]
        operations.append(
            OperationDeclaration(
                operation_id=operation_id,
                adapter_id=adapter_id,
                consumes=contract["consumes"],
                produces=contract["produces"],
                configuration={
                    "execution_mode": "synchronous",
                    "adapter_role": contract["role"],
                },
                feature_flags={"candidate_persistence": False},
            )
        )
        disposition = "validated" if state in {"succeeded", "empty"} else "unverified"
        reason = None if disposition == "validated" else adapter_result["explanation"]
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
    for index, finding in enumerate(findings):
        adapter_id = finding.get("source_adapter")
        if adapter_id not in output_ids_by_adapter:
            raise ValueError("finding adapter was not selected")
        operation_id = f"analyze-{adapter_id.replace('_', '-')}"
        output_id = str(finding.get("normalized_finding_id") or finding.get("raw_finding_id") or f"finding-{index}")
        # T002 IDs permit dots/colons but no traversal; prefixing a digest also
        # avoids carrying an unsafe producer-controlled identifier into paths.
        output_id = f"output-{hashlib.sha256(output_id.encode('utf-8')).hexdigest()[:24]}"
        transformation_id = f"transform-{output_id[7:]}"
        output_ids_by_adapter[adapter_id].append(output_id)
        output_evidence_ids = []
        for character_range, byte_range in _exact_finding_evidence_ranges(snapshot, finding):
            output_evidence = build_exact_evidence_record(
                snapshot=snapshot,
                run_id=run_id,
                artifact_id=f"bundle-{run_id}",
                artifact_file_id="source-artifact",
                operation_id=operation_id,
                adapter_id=adapter_id,
                disposition="validated",
                contributor_state=by_adapter[adapter_id]["state"],
                character_range=character_range,
                byte_range=byte_range,
                created_at=created_at,
                transformation_ids=(transformation_id,),
                output_id=output_id,
            )
            evidence_records.append(output_evidence)
            output_evidence_ids.append(output_evidence["evidence_id"])
        transformations.append(
            TransformationLineage(
                transformation_id=transformation_id,
                operation_id=operation_id,
                transformation_kind="validated_normalization",
                transformation_version="1",
                input_reference_ids=("result-artifact",),
                output_reference_ids=(output_id,),
            )
        )
        outputs.append(
            OutputLineage(
                output_id=output_id,
                operation_id=operation_id,
                source_snapshot_ids=(snapshot.identity.snapshot_id,),
                disposition="validated",
                original_output_reference_id="result-artifact",
                evidence_reference_ids=tuple(output_evidence_ids),
                transformation_ids=(transformation_id,),
                verification_outcome="omi_boundary_validated",
            )
        )
    coverage = _coverage(adapter_results)
    for adapter_id in requested_adapters:
        adapter_result = by_adapter.get(adapter_id) or {
            "state": "error",
            "explanation": "selected adapter returned no attributable result envelope",
        }
        state = adapter_result["state"]
        contributors.append(
            ContributorLineage(
                operation_id=f"analyze-{adapter_id.replace('_', '-')}",
                adapter_id=adapter_id,
                source_snapshot_ids=(snapshot.identity.snapshot_id,),
                result_state=state,
                coverage="complete" if state in {"succeeded", "empty"} else "none",
                explanation=adapter_result["explanation"],
                provenance=_adapter_provenance(
                    adapter_id,
                    f"analyze-{adapter_id.replace('_', '-')}",
                    state,
                    [
                        finding["provenance"] for finding in findings
                        if finding["source_adapter"] == adapter_id
                    ],
                ),
                output_ids=tuple(output_ids_by_adapter[adapter_id]),
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
    request_hash: str,
    run_id: str,
    idempotency_key: str | None = None,
    runner: Callable[..., dict[str, Any]] | None = None,
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
        result = execute(
            project_id,
            raw_idea,
            source_idea_id=source_idea_id,
            persist_candidates=False,
            requested_adapters=effective_adapters,
            allow_deterministic_fallback=False,
        )
    except Exception as exc:
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
            "findings": [],
            "persisted_candidate_ids": [],
            "safety": omi_analysis_orchestrator.build_orchestrator_safety_envelope(),
        }
    result = _validate_analysis_result(result, selected_adapters=effective_adapters)
    source_payload = raw_idea.encode("utf-8")
    result_payload = canonical_json_bytes(result)
    manifest, evidence_records = _build_manifest_and_evidence(
        project_id=project_id,
        run_id=run_id,
        snapshot=snapshot,
        result=result,
        requested_adapters=effective_adapters,
        source_artifact_hash=hashlib.sha256(source_payload).hexdigest(),
        result_artifact_hash=hashlib.sha256(result_payload).hexdigest(),
        created_at=timestamp,
    )
    manifest_dict = manifest.to_dict()
    manifest_hash = canonical_sha256(manifest_dict)
    manifest_path = run_path / "manifest.json"
    _write_immutable_object(manifest_path, manifest_dict)
    evidence_ids = [record["evidence_id"] for record in evidence_records]
    provenance_refs = [f"contributor-{adapter}" for adapter in effective_adapters]
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
        ),
    ]
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
    )
    write_immutable_raw_artifact_bundle(
        raw_manifest,
        {"source-artifact": source_payload, "result-artifact": result_payload},
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
            idempotency_key=f"contributor-{contributor['adapter_id']}",
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
    allow_deterministic_fallback: bool = False,
    idempotency_key: str | None = None,
    runner: Callable[..., dict[str, Any]] | None = None,
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
    snapshot, effective_adapters, request_hash, run_id = _prepare_stable_submission(
        project_id=project_id,
        raw_idea=raw_idea,
        source_idea_id=source_idea_id,
        requested_adapters=requested_adapters,
        allow_deterministic_fallback=allow_deterministic_fallback,
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
                request_hash=request_hash,
                run_id=run_id,
                idempotency_key=idempotency_key,
                runner=runner,
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
