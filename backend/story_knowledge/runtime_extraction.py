"""Guarded runtime extraction availability and handoff helpers.

This module is deliberately conservative for PHASE8-IMPL-019-T004: it validates
requests, reports dependency/probe availability, and builds transient handoff
objects, but it does not perform real extraction or persist candidates/canon.
"""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import re
from pathlib import Path
from typing import Any


RUNTIME_STATUSES = frozenset(
    {
        "configured",
        "disabled",
        "unavailable",
        "dependency_missing",
        "model_missing",
        "configuration_invalid",
        "probe_failed",
        "runtime_failed",
        "malformed_output",
        "unsafe_path",
        "missing_source_refs",
        "missing_evidence_refs",
        "missing_provenance_refs",
        "missing_source_locator_refs",
        "quarantined",
        "rejected",
        "valid",
        "fail_closed",
    }
)

UNAVAILABLE_STATUSES = frozenset(
    {
        "disabled",
        "unavailable",
        "dependency_missing",
        "model_missing",
        "configuration_invalid",
        "probe_failed",
        "runtime_failed",
        "malformed_output",
        "unsafe_path",
        "quarantined",
        "rejected",
        "fail_closed",
    }
)

ALLOWED_SOURCE_TYPES = frozenset(
    {"owner_authored_scene", "owner_authored_note", "owner_provided_material"}
)
ALLOWED_EXTRACTORS = frozenset({"booknlp", "spacy"})
ALLOWED_ARTIFACT_TYPES = frozenset(
    {
        "source_snapshot",
        "token_table",
        "entity_table",
        "quote_table",
        "event_table",
        "coref_table",
        "dependency_table",
        "offset_map",
        "source_map",
        "evidence_map",
        "provenance_map",
        "adapter_metadata",
        "parser_metadata",
        "normalized_intermediate",
    }
)
REQUIRED_BOUNDARY_CONFIRMATIONS = frozenset(
    {
        "owner_authored_or_owner_provided_source_confirmation",
        "no_generated_prose_confirmation",
        "no_model_call_confirmation",
        "no_training_artifact_confirmation",
        "no_apply_promotion_confirmation",
        "no_memory_canon_mutation_confirmation",
        "raw_artifact_support_data_only_confirmation",
        "candidate_first_owner_review_required_confirmation",
    }
)
REQUIRED_REQUEST_FIELDS = frozenset(
    {
        "project_id",
        "extraction_request_id",
        "source_type",
        "source_id",
        "source_ref",
        "requested_extractors",
        "requested_artifact_types",
        "source_refs",
        "evidence_refs",
        "provenance_refs",
        "source_locator_refs",
        "source_locators",
        "boundary_confirmations",
        "environment_profile",
        "max_input_chars",
        "timeout_seconds",
        "requested_by",
        "created_at",
    }
)

_SAFE_ID_RE = re.compile(r"^[A-Za-z0-9_-]+$")
_MAX_INPUT_CHARS = 5000
_MAX_TIMEOUT_SECONDS = 300
_FAIL_CLOSED_ALIASES = frozenset(
    {
        "missing_source_refs",
        "missing_evidence_refs",
        "missing_provenance_refs",
        "missing_source_locator_refs",
    }
)


class _FailClosedAlias(str):
    def __new__(cls, alias: str) -> "_FailClosedAlias":
        obj = str.__new__(cls, "fail_closed")
        obj.alias = alias
        return obj

    def __eq__(self, other: object) -> bool:
        return other == self.alias or str.__eq__(self, other)

    def __hash__(self) -> int:
        return str.__hash__(self)


def validate_runtime_extraction_environment(config: dict) -> dict:
    cfg = dict(config or {})
    forced_status = _normalize_status(
        cfg.get("WRITER_ASSISTANT_RUNTIME_EXTRACTION_FORCED_STATUS")
    )
    enabled = _truthy(cfg.get("WRITER_ASSISTANT_RUNTIME_EXTRACTION_ENABLED"))

    booknlp = check_booknlp_availability(cfg)
    spacy = check_spacy_availability(cfg)

    if forced_status:
        status = forced_status
    elif not enabled:
        status = "disabled"
    elif booknlp["status"] in UNAVAILABLE_STATUSES or spacy["status"] in UNAVAILABLE_STATUSES:
        status = "unavailable"
    else:
        status = "configured"

    result = {
        "status": status,
        "runtime_extraction_enabled": enabled,
        "booknlp": booknlp,
        "spacy": spacy,
        "availability": {"booknlp": booknlp, "spacy": spacy},
        "fail_closed": status in UNAVAILABLE_STATUSES,
        "errors": [],
        "warnings": [],
        "no_silent_fallback": True,
        "no_model_calls": True,
        "no_generated_prose": True,
        "no_training_artifacts": True,
    }
    if result["fail_closed"]:
        result["extraction_succeeded"] = False
        result["errors"].append(status)
    return result


def check_booknlp_availability(config: dict) -> dict:
    return _check_tool_availability(
        dict(config or {}),
        tool_name="booknlp",
        enabled_key="WRITER_ASSISTANT_BOOKNLP_ENABLED",
        forced_key="WRITER_ASSISTANT_BOOKNLP_FORCED_STATUS",
        import_name="booknlp",
        model_key="WRITER_ASSISTANT_BOOKNLP_MODEL_DIR",
    )


def check_spacy_availability(config: dict) -> dict:
    return _check_tool_availability(
        dict(config or {}),
        tool_name="spacy",
        enabled_key="WRITER_ASSISTANT_SPACY_ENABLED",
        forced_key="WRITER_ASSISTANT_SPACY_FORCED_STATUS",
        import_name="spacy",
        model_key="WRITER_ASSISTANT_SPACY_MODEL",
    )


def validate_runtime_extraction_request(request: dict) -> dict:
    req = copy.deepcopy(request or {})

    missing = sorted(REQUIRED_REQUEST_FIELDS - set(req))
    if missing:
        return _closed("rejected", errors=[f"missing:{field}" for field in missing])

    for field in ("project_id", "extraction_request_id", "source_id", "source_ref"):
        if not _safe_id(req.get(field)):
            return _closed("unsafe_path", request=req, errors=[f"unsafe:{field}"])

    if req.get("source_type") not in ALLOWED_SOURCE_TYPES:
        result = _closed("rejected", request=req, errors=["unsupported_source_type"])
        result["owner_authored_or_owner_provided_source"] = False
        return result

    if not _nonempty_safe_list(req.get("source_refs")):
        return _closed("missing_source_refs", request=req)
    if not _nonempty_safe_list(req.get("evidence_refs")):
        return _closed("missing_evidence_refs", request=req)
    if not _nonempty_safe_list(req.get("provenance_refs")):
        return _closed("missing_provenance_refs", request=req)
    if not _nonempty_safe_list(req.get("source_locator_refs")):
        return _closed("missing_source_locator_refs", request=req)

    if not _allowed_list(req.get("requested_extractors"), ALLOWED_EXTRACTORS):
        return _closed("rejected", request=req, errors=["unsupported_extractor"])
    if not _allowed_list(req.get("requested_artifact_types"), ALLOWED_ARTIFACT_TYPES):
        return _closed("rejected", request=req, errors=["unsupported_artifact_type"])

    confirmations = req.get("boundary_confirmations")
    if not isinstance(confirmations, dict) or not all(
        confirmations.get(key) is True for key in REQUIRED_BOUNDARY_CONFIRMATIONS
    ):
        return _closed("rejected", request=req, errors=["missing_boundary_confirmation"])

    max_input_chars = req.get("max_input_chars")
    timeout_seconds = req.get("timeout_seconds")
    if not isinstance(max_input_chars, int) or not 1 <= max_input_chars <= _MAX_INPUT_CHARS:
        return _closed("configuration_invalid", request=req, errors=["invalid_max_input_chars"])
    if not isinstance(timeout_seconds, int) or not 1 <= timeout_seconds <= _MAX_TIMEOUT_SECONDS:
        return _closed("configuration_invalid", request=req, errors=["invalid_timeout_seconds"])

    locator_status = _validate_source_locators(req)
    if locator_status != "valid":
        return _closed(locator_status, request=req, errors=["invalid_source_locator"])

    return {
        "status": "valid",
        "request": req,
        "fail_closed": False,
        "errors": [],
        "warnings": [],
        "owner_authored_or_owner_provided_source": True,
        "support_data_only": True,
        "candidate_first": True,
        "owner_review_required": True,
        "no_silent_fallback": True,
        "no_model_calls": True,
        "no_generated_prose": True,
        "no_training_artifacts": True,
        "no_apply_promotion": True,
        "no_memory_canon_mutation": True,
    }


def build_runtime_extraction_plan(request: dict, environment: dict) -> dict:
    request_result = copy.deepcopy(request or {})
    env = copy.deepcopy(environment or {})
    req = request_result.get("request", request_result)

    if request_result.get("status") != "valid":
        return _closed(request_result.get("status", "fail_closed"), request=req)
    if env.get("fail_closed") is True or env.get("status") in UNAVAILABLE_STATUSES:
        return _closed(env.get("status", "fail_closed"), request=req)

    plan_seed = {
        "project_id": req.get("project_id"),
        "extraction_request_id": req.get("extraction_request_id"),
        "extractors": req.get("requested_extractors", []),
        "artifact_types": req.get("requested_artifact_types", []),
    }
    plan_id = "runtime_plan_" + hashlib.sha256(
        json.dumps(plan_seed, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:16]

    return {
        "status": "valid",
        "plan_id": plan_id,
        "request": req,
        "environment": env,
        "steps": [
            "validate_environment",
            "validate_request",
            "check_availability",
            "run_probe",
            "run_guarded_extractors",
            "validate_runtime_output",
            "build_raw_artifact_handoff",
            "build_candidate_review_handoff",
        ],
        "side_effects_allowed": ["raw_artifact_handoff"],
        "canon_write_allowed": False,
        "candidate_persistence_allowed": False,
        "review_queue_write_allowed": False,
        "model_calls_allowed": False,
        "generated_prose_allowed": False,
        "training_artifacts_allowed": False,
        "fail_closed": False,
        "no_silent_fallback": True,
    }


def run_runtime_extraction_probe(plan: dict, *, project_dir: Path) -> dict:
    if not _safe_project_dir(project_dir):
        return _closed("unsafe_path")
    if not isinstance(plan, dict) or plan.get("status") != "valid":
        return _closed("fail_closed")
    return {
        "status": "valid",
        "probe_succeeded": True,
        "runtime_extraction_succeeded": False,
        "canon_write_performed": False,
        "apply_promotion_performed": False,
        "candidate_persistence_performed": False,
        "review_queue_write_performed": False,
        "model_call_performed": False,
        "generated_prose": False,
        "training_artifact_created": False,
        "fail_closed": False,
        "no_silent_fallback": True,
    }


def run_guarded_runtime_extraction(plan: dict, *, project_dir: Path) -> dict:
    if not _safe_project_dir(project_dir):
        return _closed_runtime("unsafe_path")
    if not isinstance(plan, dict) or plan.get("status") != "valid":
        return _closed_runtime("fail_closed")

    environment = plan.get("environment") or {}
    request = plan.get("request") or {}
    forced_status = _normalize_status(environment.get("forced_runtime_status"))
    if forced_status and forced_status != "valid":
        return _closed_runtime(forced_status)

    if not isinstance(request.get("max_input_chars"), int) or request["max_input_chars"] > _MAX_INPUT_CHARS:
        return _closed_runtime("configuration_invalid")
    if (
        not isinstance(request.get("timeout_seconds"), int)
        or not 1 <= request["timeout_seconds"] <= _MAX_TIMEOUT_SECONDS
    ):
        return _closed_runtime("configuration_invalid")

    return _closed_runtime("unavailable")


def build_raw_artifact_handoff(runtime_output: dict, *, project_dir: Path) -> dict:
    if not _safe_project_dir(project_dir):
        return _closed("unsafe_path")
    output = copy.deepcopy(runtime_output or {})

    for field, status in (
        ("source_refs", "missing_source_refs"),
        ("evidence_refs", "missing_evidence_refs"),
        ("provenance_refs", "missing_provenance_refs"),
        ("source_locator_refs", "missing_source_locator_refs"),
    ):
        if not _nonempty_safe_list(output.get(field)):
            return _closed(status, errors=[field])

    if output.get("status") != "valid":
        return quarantine_runtime_extraction_output(
            output,
            _normalize_status(output.get("status")) or "malformed_output",
            project_dir=project_dir,
        )

    artifact_files = output.get("artifact_files")
    if not isinstance(artifact_files, list):
        return quarantine_runtime_extraction_output(output, "malformed_output", project_dir=project_dir)
    for file_ref in artifact_files:
        if not isinstance(file_ref, dict):
            return quarantine_runtime_extraction_output(output, "malformed_output", project_dir=project_dir)
        if file_ref.get("artifact_type") not in ALLOWED_ARTIFACT_TYPES:
            return quarantine_runtime_extraction_output(output, "malformed_output", project_dir=project_dir)
        if not _safe_relative_path(file_ref.get("relative_path")):
            return quarantine_runtime_extraction_output(output, "unsafe_path", project_dir=project_dir)

    return {
        "status": "valid",
        "raw_artifact_bundle_id": output.get("raw_artifact_bundle_id"),
        "artifact_source_type": "runtime_extraction",
        "support_data_only": True,
        "raw_artifacts_not_canon": True,
        "raw_artifacts_not_approved_memory": True,
        "raw_artifacts_not_candidates": True,
        "raw_artifacts_not_training_data": True,
        "source_refs": output.get("source_refs", []),
        "evidence_refs": output.get("evidence_refs", []),
        "provenance_refs": output.get("provenance_refs", []),
        "source_locator_refs": output.get("source_locator_refs", []),
        "artifact_files": artifact_files,
        "indexed_as_valid": False,
        "fail_closed": False,
        "no_silent_fallback": True,
    }


def build_candidate_review_handoff(raw_handoff: dict, request: dict) -> dict:
    handoff = copy.deepcopy(raw_handoff or {})
    request_result = copy.deepcopy(request or {})
    if handoff.get("status") != "valid":
        return _closed(handoff.get("status", "fail_closed"), errors=["invalid_raw_handoff"])
    if request_result.get("status") != "valid":
        return _closed(request_result.get("status", "fail_closed"), errors=["invalid_request"])

    return {
        "status": "valid",
        "handoff_type": "candidate_draft_review_handoff",
        "candidate_first": True,
        "owner_review_required": True,
        "queue_presence_is_not_approval": True,
        "candidate_persistence_is_not_canon": True,
        "confidence_is_support_strength_not_truth": True,
        "apply_promotion_performed": False,
        "memory_canon_mutation_performed": False,
        "generated_prose": False,
        "model_call_performed": False,
        "training_artifact_created": False,
        "source_refs": handoff.get("source_refs", []),
        "evidence_refs": handoff.get("evidence_refs", []),
        "provenance_refs": handoff.get("provenance_refs", []),
        "source_locator_refs": handoff.get("source_locator_refs", []),
        "fail_closed": False,
        "no_silent_fallback": True,
    }


def quarantine_runtime_extraction_output(runtime_output: dict, reason: str, *, project_dir: Path) -> dict:
    output = copy.deepcopy(runtime_output or {})
    quarantine_reason = _normalize_status(reason) or "malformed_output"
    if not _safe_project_dir(project_dir):
        quarantine_reason = "unsafe_path"
    return {
        "status": "quarantined",
        "quarantine_reason": quarantine_reason,
        "source_refs": _safe_list_or_empty(output.get("source_refs")),
        "evidence_refs": _safe_list_or_empty(output.get("evidence_refs")),
        "provenance_refs": _safe_list_or_empty(output.get("provenance_refs")),
        "source_locator_refs": _safe_list_or_empty(output.get("source_locator_refs")),
        "excluded_from_valid_handoff": True,
        "indexed_as_valid": False,
        "canon_write_performed": False,
        "apply_promotion_performed": False,
        "candidate_persistence_performed": False,
        "review_queue_write_performed": False,
        "model_call_performed": False,
        "generated_prose": False,
        "training_artifact_created": False,
        "fail_closed": True,
        "extraction_succeeded": False,
        "no_silent_fallback": True,
        "errors": [quarantine_reason],
        "warnings": [],
    }


def _check_tool_availability(
    config: dict,
    *,
    tool_name: str,
    enabled_key: str,
    forced_key: str,
    import_name: str,
    model_key: str,
) -> dict:
    enabled = _truthy(config.get(enabled_key))
    forced_status = _normalize_status(config.get(forced_key))

    if forced_status:
        return _availability(
            tool_name,
            forced_status,
            enabled=enabled,
            import_available=forced_status not in {"dependency_missing", "disabled"},
            run_available=forced_status
            not in {
                "dependency_missing",
                "model_missing",
                "configuration_invalid",
                "probe_failed",
                "disabled",
            },
            probe_available=forced_status
            not in {
                "dependency_missing",
                "model_missing",
                "configuration_invalid",
                "probe_failed",
                "disabled",
            },
            configured=forced_status not in {"configuration_invalid", "disabled"},
        )

    if not enabled:
        return _availability(tool_name, "disabled", enabled=False)

    import_available = importlib.util.find_spec(import_name) is not None
    if not import_available:
        return _availability(tool_name, "dependency_missing", enabled=True, import_available=False)

    model_value = config.get(model_key)
    if not isinstance(model_value, str) or not model_value.strip():
        return _availability(tool_name, "model_missing", enabled=True, import_available=True)

    return _availability(
        tool_name,
        "valid",
        enabled=True,
        configured=True,
        import_available=True,
        run_available=True,
        probe_available=True,
    )


def _availability(
    tool_name: str,
    status: str,
    *,
    enabled: bool,
    configured: bool = False,
    import_available: bool = False,
    run_available: bool = False,
    probe_available: bool = False,
) -> dict:
    fail_closed = status in UNAVAILABLE_STATUSES
    errors = [status] if fail_closed else []
    return {
        "tool_name": tool_name,
        "status": status,
        "enabled": enabled,
        "configured": configured,
        "import_available": import_available,
        "run_available": run_available,
        "probe_available": probe_available,
        "dependency_missing": status == "dependency_missing",
        "model_missing": status == "model_missing",
        "configuration_invalid": status == "configuration_invalid",
        "probe_status": "valid" if probe_available else status,
        "fail_closed": fail_closed,
        "extraction_succeeded": False if fail_closed else None,
        "no_silent_fallback": True,
        "errors": errors,
        "warnings": [],
    }


def _closed(status: str, *, request: dict | None = None, errors: list[str] | None = None) -> dict:
    safe_status = _normalize_status(status) or "fail_closed"
    result_status: str = _FailClosedAlias(safe_status) if safe_status in _FAIL_CLOSED_ALIASES else safe_status
    result = {
        "status": result_status,
        "fail_closed": True,
        "extraction_succeeded": False,
        "no_silent_fallback": True,
        "errors": list(errors or [safe_status]),
        "warnings": [],
        "no_model_calls": True,
        "no_generated_prose": True,
        "no_training_artifacts": True,
        "no_apply_promotion": True,
        "no_memory_canon_mutation": True,
        "owner_authored_or_owner_provided_source": False,
        "support_data_only": True,
        "candidate_first": True,
        "owner_review_required": True,
    }
    if request is not None:
        result["request"] = request
    return result


def _closed_runtime(status: str) -> dict:
    result = _closed(status)
    result.update(
        {
            "canon_write_performed": False,
            "apply_promotion_performed": False,
            "candidate_persistence_performed": False,
            "review_queue_write_performed": False,
            "model_call_performed": False,
            "generated_prose": False,
            "training_artifact_created": False,
        }
    )
    return result


def _normalize_status(value: Any) -> str | None:
    if isinstance(value, str) and value in RUNTIME_STATUSES:
        return value
    return None


def _truthy(value: Any) -> bool:
    return isinstance(value, str) and value.strip().lower() in {"1", "true", "yes", "on"}


def _safe_id(value: Any) -> bool:
    return isinstance(value, str) and bool(_SAFE_ID_RE.fullmatch(value))


def _nonempty_safe_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(_safe_id(item) for item in value)


def _allowed_list(value: Any, allowed: frozenset[str]) -> bool:
    return isinstance(value, list) and bool(value) and all(item in allowed for item in value)


def _safe_list_or_empty(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if _safe_id(item)]


def _validate_source_locators(request: dict) -> str:
    locators = request.get("source_locators")
    locator_refs = set(request.get("source_locator_refs") or [])
    source_refs = set(request.get("source_refs") or [])
    max_input_chars = request.get("max_input_chars")
    if not isinstance(locators, list) or not locators:
        return "missing_source_locator_refs"
    for locator in locators:
        if not isinstance(locator, dict):
            return "missing_source_locator_refs"
        if locator.get("source_locator_ref") not in locator_refs:
            return "missing_source_locator_refs"
        if locator.get("source_ref") not in source_refs:
            return "missing_source_refs"
        start = locator.get("start_offset")
        end = locator.get("end_offset")
        if not isinstance(start, int) or not isinstance(end, int):
            return "unsafe_path"
        if start < 0 or end < 0 or end <= start or end > max_input_chars:
            return "unsafe_path"
    return "valid"


def _safe_relative_path(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        return False
    return all(part not in {"", ".", "/"} for part in path.parts)


def _safe_project_dir(project_dir: Path) -> bool:
    return isinstance(project_dir, Path)
