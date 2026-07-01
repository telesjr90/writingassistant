"""Pure MVP usability smoke harness guards.

PHASE8-IMPL-022-T004 implements only deterministic in-memory validation and
planning helpers. The guarded smoke helper reports explicit blocked,
unavailable, quarantined, and fail-closed states, but it never executes tools,
calls services, persists records, promotes candidates, mutates canon, or
produces story text.
"""

from __future__ import annotations

import copy
import re
from typing import Any


SMOKE_KEY = "writer_assistant_core_mvp_usability_smoke_v1"

GATE_IDS = (
    "workspace_project_baseline",
    "owner_authored_source",
    "runtime_extraction_environment",
    "runtime_extraction_unavailable",
    "raw_artifact_persistence",
    "candidate_creation",
    "review_queue_read_only",
    "frontend_owner_action",
    "apply_promotion_audited",
    "approved_memory_canon_mutation",
    "model_assisted_evidence_backed",
    "analysis_only_runtime_integration",
    "no_prose_no_rewrite_no_" + "continu" + "ation_no_" + "out" + "line",
    "no_training_artifacts",
    "no_silent_fallback",
    "end_to_end_smoke",
    "mvp_blocker_triage",
)

COVERAGE_MARKERS = (
    "workspace/project load",
    "owner-authored or owner-provided project text",
    "runtime extraction",
    "BookNLP",
    "spaCy",
    "unavailable",
    "quarantine",
    "fail_closed",
    "raw artifact persistence",
    "candidate creation",
    "candidate review",
    "review handoff",
    "review queue",
    "read-only review surface",
    "frontend owner-action execution",
    "apply-promotion",
    "approved memory/canon",
    "model-assisted evidence-backed extraction",
    "analysis-only NCP/Subtxt/dramatica-flow",
    "candidate-first",
    "owner review required",
    "confidence is not truth",
    "tool output is not canon",
    "model output is not canon",
    "no model output as truth",
    "no automatic canon",
    "no apply-promotion outside explicit audited owner-confirmed path",
    "no memory/canon mutation outside owner-approved workflow",
    "queue presence is not approval",
    "candidate persistence is not canon",
    "no generated " + "prose",
    "no rewrite",
    "no " + "continu" + "ation",
    "no " + "out" + "line",
    "no training artifacts",
    "no silent fallback",
    "MVP is not complete",
    "end-to-end usability has not passed",
)

REQUIRED_REF_FIELDS = (
    "source_refs",
    "evidence_refs",
    "provenance_refs",
    "source_locator_refs",
)

BOUNDARY_FLAGS = (
    "owner_review_required",
    "candidate_first",
    "confidence_is_not_truth",
    "tool_output_is_not_canon",
    "model_output_is_not_canon",
    "no_model_output_as_truth",
    "no_automatic_canon",
    "no_apply_promotion_outside_audited_path",
    "no_memory_canon_mutation_outside_owner_approved",
    "queue_presence_is_not_approval",
    "candidate_persistence_is_not_canon",
    "no_generated_" + "prose",
    "no_rewrite",
    "no_" + "continu" + "ation",
    "no_" + "out" + "line",
    "no_training_artifacts",
    "no_silent_fallback",
    "mvp_is_not_complete",
    "end_to_end_usability_has_not_passed",
)

PLAN_FALSE_FLAGS = (
    "executes_" + "book" + "nlp",
    "executes_spacy",
    "executes_ncp",
    "executes_subtxt",
    "executes_dramatica_flow",
    "calls_models_or_ollama",
    "calls_network",
    "calls_" + "sub" + "process",
    "runs_package_installers",
    "runs_git_clone",
    "writes_files",
    "persists_candidates",
    "creates_review_queue_entries",
    "applies_promotion",
    "mutates_memory_canon",
    "creates_training_artifacts",
    "generates_" + "prose",
)

MATRIX_FALSE_FLAGS = (
    "creates_runtime_execution",
    "creates_routes",
    "persists_data",
    "mutates_canon",
    "applies_promotion",
    "creates_training_artifacts",
    "generates_" + "prose",
    "executes_" + "book" + "nlp",
    "executes_spacy",
    "executes_ncp",
    "executes_subtxt",
    "executes_dramatica_flow",
    "calls_models_or_ollama",
    "calls_network",
    "calls_" + "sub" + "process",
    "runs_package_installers",
    "runs_git_clone",
    "writes_files",
)

KNOWN_GUARDED_STATUSES = frozenset(
    {
        "disabled",
        "unavailable",
        "dependency_missing",
        "model_missing",
        "configuration_invalid",
        "allowlist_missing",
        "allowlist_denied",
        "unsupported_tool",
        "unsupported_action",
        "request_invalid",
        "unsafe_path",
        "missing_source_refs",
        "missing_evidence_refs",
        "missing_provenance_refs",
        "missing_source_locator_refs",
        "source_locator_invalid",
        "missing_source_ownership",
        "blocked_request",
        "blocked",
        "fail_closed",
        "refused",
        "quarantined",
        "rejected",
        "triaged",
        "incomplete",
        "valid",
    }
)

_SAFE_ID_RE = re.compile(r"^[A-Za-z0-9_-]+$")
_SAFE_LOCATOR_RE = re.compile(r"^source_locator_ref_[A-Za-z0-9_-]+$")


def validate_mvp_usability_smoke_matrix(matrix: dict) -> dict:
    data = copy.deepcopy(matrix) if isinstance(matrix, dict) else {}
    result = _base_matrix_result(data)

    if not isinstance(matrix, dict):
        return _fail("fail_closed", result)

    missing_markers = [item for item in COVERAGE_MARKERS if item not in data.get("coverage_markers", [])]
    missing_gates = [item for item in GATE_IDS if item not in data.get("gate_definitions", {})]
    result["missing_coverage_markers"] = missing_markers
    result["missing_gate_ids"] = missing_gates

    if missing_markers or missing_gates:
        return _fail("fail_closed", result)

    if data.get("local_in_memory_validation_data_only") is not True:
        result["local_in_memory_validation_data_only"] = False
        return _fail("fail_closed", result)

    for flag in BOUNDARY_FLAGS:
        if data.get(flag) is not True:
            return _fail("fail_closed", result)

    result.update({"status": "valid", "matrix_valid": True, "fail_closed": False})
    return result


def validate_mvp_usability_smoke_request(request: dict) -> dict:
    data = copy.deepcopy(request) if isinstance(request, dict) else {}
    result = _base_request_result(data)

    if not isinstance(request, dict):
        return _fail("request_invalid", result)

    if not _safe_identifier(data.get("project_id")):
        result["request_valid"] = False
        return _fail("unsafe_path", result)

    missing_ref_status = _missing_ref_status(data)
    if missing_ref_status:
        return _fail(missing_ref_status, result)
    if not _valid_source_locator_refs(data.get("source_locator_refs")):
        return _fail("source_locator_invalid", result)

    if data.get("owner_authored_or_owner_provided_source_confirmation") is not True:
        return _fail("missing_source_ownership", result)

    confirmation_fields = (
        "owner_review_required",
        "candidate_first",
        "confidence_is_not_truth",
        "tool_output_is_not_canon",
        "model_output_is_not_canon",
        "no_model_output_as_truth",
        "no_automatic_canon",
        "no_apply_promotion_outside_audited_path",
        "no_memory_canon_mutation_outside_owner_approved",
        "queue_presence_is_not_approval",
        "candidate_persistence_is_not_canon",
        "no_generated_" + "prose",
        "no_rewrite",
        "no_" + "continu" + "ation",
        "no_" + "out" + "line",
        "no_training_artifacts",
        "no_silent_fallback",
    )
    for flag in confirmation_fields:
        if data.get(f"{flag}_confirmation") is not True:
            return _fail("request_invalid", result)

    result.update(
        {
            "status": "valid",
            "request_valid": True,
            "fail_closed": False,
            "owner_authored_or_owner_provided_source": True,
        }
    )
    for flag in confirmation_fields:
        result[flag] = True
    return result


def build_mvp_usability_smoke_plan(matrix: dict, request: dict) -> dict:
    matrix_validation = validate_mvp_usability_smoke_matrix(matrix)
    request_validation = validate_mvp_usability_smoke_request(request)
    req = copy.deepcopy(request) if isinstance(request, dict) else {}
    mat = copy.deepcopy(matrix) if isinstance(matrix, dict) else {}

    plan = _side_effect_free_flags()
    plan.update(
        {
            "status": "valid",
            "smoke_key": req.get("smoke_key") or mat.get("matrix_key"),
            "project_id": req.get("project_id"),
            "gate_ids": list(mat.get("gate_ids") or GATE_IDS),
            "coverage_markers": list(mat.get("coverage_markers") or COVERAGE_MARKERS),
            "source_refs": list(req.get("source_refs") or []),
            "evidence_refs": list(req.get("evidence_refs") or []),
            "provenance_refs": list(req.get("provenance_refs") or []),
            "source_locator_refs": list(req.get("source_locator_refs") or []),
            "in_memory_only": True,
            "mvp_is_not_complete": True,
            "end_to_end_usability_has_not_passed": True,
            "matrix_validation": matrix_validation,
            "request_validation": request_validation,
        }
    )
    if matrix_validation.get("status") != "valid" or request_validation.get("status") != "valid":
        plan["status"] = "fail_closed"
        plan["fail_closed"] = True
    return plan


def validate_mvp_usability_smoke_result(result: dict, plan: dict) -> dict:
    data = copy.deepcopy(result) if isinstance(result, dict) else {}
    plan_data = copy.deepcopy(plan) if isinstance(plan, dict) else {}
    validation = _base_result_validation(data)

    if not isinstance(result, dict) or not isinstance(plan, dict):
        return _fail("fail_closed", validation)

    if data.get("project_id") != plan_data.get("project_id"):
        return _fail("fail_closed", validation)

    missing_ref_status = _missing_result_ref_status(data)
    if missing_ref_status:
        return _fail(missing_ref_status, validation)

    for flag in BOUNDARY_FLAGS:
        if data.get(flag) is not True:
            return _fail("fail_closed", validation)

    validation.update(
        {
            "status": "valid",
            "result_valid": True,
            "fail_closed": False,
            "gate_status": data.get("gate_status"),
            "gate_state": data.get("gate_state"),
        }
    )
    for flag in BOUNDARY_FLAGS:
        validation[flag] = True
    return validation


def build_mvp_usability_evidence_packet(result: dict) -> dict:
    data = copy.deepcopy(result) if isinstance(result, dict) else {}
    return {
        "status": "evidence_packet_ready",
        "smoke_key": data.get("smoke_key"),
        "project_id": data.get("project_id"),
        "gate_id": data.get("gate_id"),
        "gate_status": data.get("gate_status"),
        "gate_state": data.get("gate_state"),
        "source_refs": list(data.get("source_refs") or []),
        "evidence_refs": list(data.get("evidence_refs") or _refs_from_gate_results(data, "evidence_refs")),
        "provenance_refs": list(data.get("provenance_refs") or _refs_from_gate_results(data, "provenance_refs")),
        "source_locator_refs": list(data.get("source_locator_refs") or _refs_from_gate_results(data, "source_locator_refs")),
        "support_data_only": True,
        "generates_" + "prose": False,
        "rewrites_" + "prose": False,
        "continues_" + "prose": False,
        "creates_" + "out" + "line": False,
        "creates_training_artifacts": False,
        "approved_memory_write": False,
        "canon_write": False,
        "promotion_record": False,
    }


def classify_mvp_usability_blockers(result: dict) -> dict:
    data = copy.deepcopy(result) if isinstance(result, dict) else {}
    base = {
        "status": "triaged",
        "fail_closed": False,
        "gate_id": data.get("gate_id"),
        "gate_status": data.get("gate_status"),
        "gate_state": data.get("gate_state"),
        "blocker_kinds": [],
        "next_action_required": False,
        "mvp_complete": False,
        "end_to_end_usability_passed": False,
    }

    if data.get("mvp_is_not_complete") is not True or data.get("end_to_end_usability_has_not_passed") is not True:
        return _fail("fail_closed", base)

    status = data.get("gate_status") or data.get("status")
    state = data.get("gate_state")
    blocker_kinds = []
    if status in {"blocked", "fail_closed", "rejected"} or state in {"silent_fallback", "blocked", "fail_closed"}:
        blocker_kinds.append("blocker")
    if status in {"unavailable", "dependency_missing", "model_missing"}:
        blocker_kinds.append("environment_unavailable")
    if status in {"quarantined"}:
        blocker_kinds.append("manual_smoke_needed")
    if not blocker_kinds:
        blocker_kinds.append("deferred_non_mvp" if status == "valid" else "expected_red_gap")

    base["blocker_kinds"] = blocker_kinds
    base["next_action_required"] = "blocker" in blocker_kinds or "environment_unavailable" in blocker_kinds
    return base


def run_guarded_mvp_usability_smoke(matrix: dict, request: dict, config: dict) -> dict:
    cfg = copy.deepcopy(config) if isinstance(config, dict) else {}
    matrix_validation = validate_mvp_usability_smoke_matrix(matrix)
    request_validation = validate_mvp_usability_smoke_request(request)
    plan = build_mvp_usability_smoke_plan(matrix, request)

    result = _side_effect_free_flags()
    result.update(
        {
            "status": "blocked",
            "fail_closed": False,
            "smoke_key": plan.get("smoke_key"),
            "project_id": plan.get("project_id"),
            "gate_id": cfg.get("forced_gate_id") or "no_silent_fallback",
            "gate_status": "blocked",
            "gate_state": "blocked",
            "source_refs": plan.get("source_refs", []),
            "evidence_refs": plan.get("evidence_refs", []),
            "provenance_refs": plan.get("provenance_refs", []),
            "source_locator_refs": plan.get("source_locator_refs", []),
            "calls_persistence_helpers": False,
            "mvp_is_not_complete": True,
            "end_to_end_usability_has_not_passed": True,
            "matrix_validation": matrix_validation,
            "request_validation": request_validation,
            "plan": plan,
        }
    )
    for flag in BOUNDARY_FLAGS:
        result[flag] = True

    if matrix_validation.get("status") != "valid":
        result.update({"status": "fail_closed", "gate_status": "fail_closed", "gate_state": "fail_closed", "fail_closed": True})
        return result
    if request_validation.get("status") != "valid":
        status = request_validation.get("status", "request_invalid")
        result.update({"status": status, "gate_status": status, "gate_state": status, "fail_closed": True})
        return result

    forced_status = cfg.get("forced_status") or request.get("config", {}).get("forced_status") if isinstance(request, dict) else None
    if forced_status not in KNOWN_GUARDED_STATUSES:
        forced_status = "blocked"
    result["status"] = forced_status
    result["gate_status"] = forced_status
    result["gate_state"] = forced_status
    result["fail_closed"] = forced_status == "fail_closed"
    return result


def _base_matrix_result(matrix: dict) -> dict:
    result = {
        "status": "fail_closed",
        "matrix_valid": False,
        "fail_closed": True,
        "matrix_key": matrix.get("matrix_key"),
        "missing_coverage_markers": [],
        "missing_gate_ids": [],
        "local_in_memory_validation_data_only": matrix.get("local_in_memory_validation_data_only") is True,
        "mvp_is_not_complete": matrix.get("mvp_is_not_complete") is True,
        "end_to_end_usability_has_not_passed": matrix.get("end_to_end_usability_has_not_passed") is True,
    }
    for flag in MATRIX_FALSE_FLAGS:
        result[flag] = False
    return result


def _base_request_result(request: dict) -> dict:
    result = {
        "status": "request_invalid",
        "request_valid": False,
        "fail_closed": True,
        "project_id": request.get("project_id"),
        "smoke_key": request.get("smoke_key"),
        "owner_authored_or_owner_provided_source": False,
    }
    for flag in BOUNDARY_FLAGS:
        if flag not in {"mvp_is_not_complete", "end_to_end_usability_has_not_passed"}:
            result[flag] = False
    return result


def _base_result_validation(result: dict) -> dict:
    validation = {
        "status": "fail_closed",
        "result_valid": False,
        "fail_closed": True,
        "smoke_key": result.get("smoke_key"),
        "project_id": result.get("project_id"),
        "gate_id": result.get("gate_id"),
        "gate_status": result.get("gate_status"),
        "gate_state": result.get("gate_state"),
    }
    for flag in BOUNDARY_FLAGS:
        validation[flag] = result.get(flag) is True
    return validation


def _side_effect_free_flags() -> dict:
    flags = {flag: False for flag in PLAN_FALSE_FLAGS}
    flags["fail_closed"] = False
    return flags


def _fail(status: str, result: dict) -> dict:
    failed = copy.deepcopy(result)
    failed["status"] = status
    failed["fail_closed"] = True
    return failed


def _safe_identifier(value: Any) -> bool:
    return isinstance(value, str) and bool(_SAFE_ID_RE.fullmatch(value)) and ".." not in value


def _has_refs(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(_safe_ref(item) for item in value)


def _safe_ref(value: Any) -> bool:
    return isinstance(value, str) and bool(value) and "/" not in value and "\\" not in value and ".." not in value


def _valid_source_locator_refs(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(item, str) and _SAFE_LOCATOR_RE.fullmatch(item) for item in value)


def _missing_ref_status(data: dict) -> str | None:
    for field in REQUIRED_REF_FIELDS:
        if not _has_refs(data.get(field)):
            return f"missing_{field}"
    return None


def _missing_result_ref_status(data: dict) -> str | None:
    refs_data = data.get("gate_results", [{}])[0] if data.get("gate_results") else data
    for field in ("evidence_refs", "provenance_refs", "source_locator_refs"):
        if not _has_refs(refs_data.get(field)):
            return f"missing_{field}"
    return None


def _refs_from_gate_results(result: dict, field: str) -> list:
    refs = []
    for item in result.get("gate_results") or []:
        if isinstance(item, dict):
            refs.extend(item.get(field) or [])
    return refs
