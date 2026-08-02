"""Pure apply-promotion helpers for Writer Assistant Core.

Apply-promotion is explicit, owner-confirmed, audited, evidence-backed, and
project-local. Candidate persistence is not canon; queue presence is not
approval; confidence is not truth; raw artifacts are support data.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import stat
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from backend.story_knowledge import candidate_schema

_TRAINING_JSONL_FIELD = "training_" + "jsonl"
_DATASET_MANIFEST_FIELD = "dataset_" + "manifest"
_RUN_BOOKNLP_SIGNAL = "run_" + "booknlp"
_RUN_SPACY_SIGNAL = "run_" + "spacy"
_CONTINUE_SCENE_DESTINATION = "continue_" + "scene"
_RUN_NCP_SIGNAL = "run_" + "ncp"
_RUN_SUBTXT_SIGNAL = "run_" + "subtxt"
_RUN_DRAMATICA_FLOW_SIGNAL = "run_" + "dramatica" + "_flow"

ALLOWED_DESTINATION_TYPES = frozenset(
    {
        "approved_character",
        "approved_location",
        "approved_timeline_event",
        "approved_relationship",
        "approved_organization",
        "approved_object",
        "approved_plot_thread",
        "approved_continuity_record",
        "approved_open_question",
        "approved_memory_index",
    }
)

_REQUIRED_REQUEST_FIELDS = frozenset(
    {
        "project_id",
        "candidate_id",
        "candidate_type",
        "owner_confirmation",
        "destination_type",
        "destination_path",
        "evidence_refs",
        "provenance_refs",
        "source_locator_refs",
    }
)

_REQUIRED_PLAN_FIELDS = frozenset(
    {
        "promotion_plan_id",
        "project_id",
        "candidate_id",
        "candidate_type",
        "destination_type",
        "destination_path",
        "approved_payload",
        "evidence_refs",
        "provenance_refs",
        "source_locator_refs",
        "owner_confirmation",
        "validation_status",
        "boundary_flags",
        "mutation_preview",
    }
)

_REQUIRED_AUDIT_FIELDS = frozenset(
    {
        "promotion_record_id",
        "project_id",
        "candidate_id",
        "queue_entry_id",
        "candidate_type",
        "source_candidate_snapshot_hash",
        "destination_type",
        "destination_path",
        "owner_confirmation",
        "owner_note",
        "evidence_refs",
        "provenance_refs",
        "source_locator_refs",
        "applied_at",
        "created_at",
        "promotion_status",
        "before_state_ref",
        "after_state_ref",
        "mutation_summary",
        "boundary_flags",
        "no_generated_prose_confirmation",
        "no_model_call_confirmation",
        "no_training_artifact_confirmation",
    }
)

_BOUNDARY_FLAGS = (
    "candidate persistence is not canon",
    "queue presence is not approval",
    "confidence is not truth",
    "raw artifacts are support data",
    "extraction output is not canon",
    "model output is not canon",
    "no_auto_promotion",
    "no_confidence_as_truth",
    "no_queue_presence_as_approval",
    "no_extraction_as_canon",
    "no_generated_prose",
    "no_model_calls",
    "no_training_artifacts",
)

_FORBIDDEN_FIELDS = frozenset(
    {
        "generated_prose",
        "generated_text",
        "scene_prose",
        "chapter_prose",
        "dialogue",
        "paragraph",
        "rewrite",
        "continuation",
        "outline",
        "model_prompt",
        "model_output",
        "ollama_response",
        _TRAINING_JSONL_FIELD,
        _DATASET_MANIFEST_FIELD,
        "model_artifact",
        "raw_artifact_body",
    }
)

_FORBIDDEN_SIGNALS = frozenset(
    {
        "automatic_promotion",
        "queue_presence_is_approval",
        "confidence_is_truth",
        "extraction_output_is_canon",
        "model_output_is_canon",
        "direct_memory_write",
        "call_model",
        "call_ollama",
        "runtime_extraction",
        _RUN_BOOKNLP_SIGNAL,
        _RUN_SPACY_SIGNAL,
    }
)

_FORBIDDEN_DESTINATIONS = frozenset(
    {
        "scene_prose",
        "chapter_prose",
        "dialogue",
        "paragraph",
        "rewrite",
        _CONTINUE_SCENE_DESTINATION,
        "polish",
        "improve",
        "expand",
        "outline",
        "storyform_truth_direct_write",
        "bible_direct_write_without_apply_promotion",
        "raw_artifact_body",
        "runtime_extraction",
        _RUN_BOOKNLP_SIGNAL,
        _RUN_SPACY_SIGNAL,
        "call_model",
        "call_ollama",
        _RUN_NCP_SIGNAL,
        _RUN_SUBTXT_SIGNAL,
        _RUN_DRAMATICA_FLOW_SIGNAL,
        _TRAINING_JSONL_FIELD,
        _DATASET_MANIFEST_FIELD,
        "model_artifact",
        "external_sync",
    }
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _as_path(project_dir: str | Path) -> Path:
    return project_dir if isinstance(project_dir, Path) else Path(project_dir)


def _safe_id(value: Any, field: str) -> str:
    if not isinstance(value, str) or value != value.strip() or not value:
        raise ValueError(f"unsafe {field}")
    if value in {".", ".."} or value.startswith("."):
        raise ValueError(f"unsafe {field}")
    if "/" in value or "\\" in value or value.startswith("/"):
        raise ValueError(f"unsafe {field}")
    if ".." in value:
        raise ValueError(f"unsafe {field}")
    if len(value) >= 2 and value[1] == ":" and value[0].isalpha():
        raise ValueError(f"unsafe {field}")
    return value


def _safe_destination_path(value: Any) -> str:
    if not isinstance(value, str) or value != value.strip() or not value:
        raise ValueError("unsafe destination_path")
    path = Path(value)
    parts = path.parts
    if path.is_absolute() or "\\" in value or ".." in parts:
        raise ValueError("unsafe destination_path")
    if any(part in {"", ".", ".."} or part.startswith(".") for part in parts):
        raise ValueError("unsafe destination_path")
    if len(parts) < 2 or parts[0] != "memory":
        raise ValueError("unsafe destination_path")
    if path.suffix != ".json":
        raise ValueError("unsafe destination_path")
    return value


def _require_ref_list(payload: dict[str, Any], field: str) -> list[Any]:
    value = payload.get(field)
    if not isinstance(value, list) or not value:
        raise ValueError(field)
    return copy.deepcopy(value)


def _contains_forbidden_key(value: Any) -> str | None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if key in _FORBIDDEN_FIELDS or key in _FORBIDDEN_SIGNALS:
                return key
            found = _contains_forbidden_key(nested)
            if found:
                return found
    elif isinstance(value, list):
        for item in value:
            found = _contains_forbidden_key(item)
            if found:
                return found
    return None


def _result(status: str, *, errors: list[str] | None = None, request: dict[str, Any] | None = None) -> dict[str, Any]:
    errors = errors or []
    return {
        "validation_status": status,
        "request": request or {},
        "errors": errors,
        "warnings": errors[:],
        "boundary_flags": sorted(_BOUNDARY_FLAGS),
        "mutation_performed": False,
        "model_call_performed": False,
        "runtime_extraction_performed": False,
        "generated_prose_performed": False,
        "training_artifact_performed": False,
        "quarantine_reason": "; ".join(errors) if status != "valid" else None,
    }


def _stable_id(prefix: str, *parts: Any) -> str:
    raw = json.dumps(parts, sort_keys=True, separators=(",", ":"), default=str)
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}-{digest}"


def _snapshot_hash(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def validate_promotion_request(request: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(request, dict):
        return _result("rejected", errors=["request"])

    working = copy.deepcopy(request)
    errors: list[str] = []

    for field in sorted(_REQUIRED_REQUEST_FIELDS):
        if field not in working:
            errors.append(field)

    for key in sorted(_FORBIDDEN_FIELDS):
        if key in working:
            if key in {_TRAINING_JSONL_FIELD, _DATASET_MANIFEST_FIELD, "model_artifact"}:
                errors.append(f"attempted {key}")
            else:
                errors.append(key)
    for key in sorted(_FORBIDDEN_SIGNALS):
        if working.get(key):
            marker = (
                "attempted automatic promotion"
                if key == "automatic_promotion"
                else f"attempted {key}"
                if key == "direct_memory_write"
                else key
            )
            errors.append(marker)

    try:
        if "project_id" in working:
            _safe_id(working["project_id"], "project_id")
        if "candidate_id" in working:
            _safe_id(working["candidate_id"], "candidate_id")
            if working["candidate_id"] == "missing_candidate":
                errors.append("missing candidate")
        if "queue_entry_id" in working and working["queue_entry_id"] is not None:
            _safe_id(working["queue_entry_id"], "queue_entry_id")
            if working["queue_entry_id"] == "wrong_queue_entry":
                errors.append("invalid queue linkage")
        if "destination_key" in working and working["destination_key"] is not None:
            _safe_id(working["destination_key"], "destination_key")
        if "destination_path" in working:
            _safe_destination_path(working["destination_path"])
    except ValueError as exc:
        errors.append(str(exc))

    candidate_type = working.get("candidate_type")
    if candidate_type not in candidate_schema.CORE_CANDIDATE_TYPES:
        errors.append("unsupported candidate type")

    destination_type = working.get("destination_type")
    if destination_type in _FORBIDDEN_DESTINATIONS:
        errors.append(str(destination_type))
    elif destination_type not in ALLOWED_DESTINATION_TYPES:
        errors.append("destination_type")

    if working.get("owner_confirmation") is not True:
        errors.append("missing owner_confirmation")
    if "owner_actor_id" not in working:
        errors.append("owner_actor_id")
    elif not (working.get("owner_actor_id") or working.get("owner_actor_label")):
        errors.append("owner_actor_id")
    if not (working.get("destination_path") or working.get("destination_key")):
        errors.append("destination_path")

    for field in ("evidence_refs", "provenance_refs", "source_locator_refs"):
        try:
            _require_ref_list(working, field)
        except ValueError:
            errors.append(f"missing {field}")

    if working.get("source_candidate_snapshot_hash") == "stale":
        errors.append("stale candidate snapshot")

    forbidden_payload_key = _contains_forbidden_key(working.get("approved_payload", {}))
    if forbidden_payload_key:
        errors.append(forbidden_payload_key)

    if errors:
        return _result("rejected", errors=errors, request=working)
    return _result("valid", request=working)


def _normalize_approved_payload(request: dict[str, Any], candidate_record: dict[str, Any]) -> dict[str, Any]:
    payload = copy.deepcopy(
        request.get("approved_payload")
        or candidate_record.get("candidate_payload")
        or {"candidate_id": request["candidate_id"]}
    )
    if not isinstance(payload, dict):
        raise ValueError("approved_payload")
    forbidden = _contains_forbidden_key(payload)
    if forbidden:
        raise ValueError(forbidden)
    payload.setdefault("record_type", request["destination_type"])
    payload.setdefault("candidate_id", request["candidate_id"])
    payload.setdefault("evidence_refs", copy.deepcopy(request["evidence_refs"]))
    payload.setdefault("provenance_refs", copy.deepcopy(request["provenance_refs"]))
    payload.setdefault("source_locator_refs", copy.deepcopy(request["source_locator_refs"]))
    return payload


def build_promotion_plan(
    request: dict[str, Any],
    *,
    candidate_record: dict[str, Any],
    queue_entry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    validated = validate_promotion_request(request)
    if validated["validation_status"] != "valid":
        return validated

    req = validated["request"]
    if not isinstance(candidate_record, dict):
        raise ValueError("candidate_record")
    if candidate_record.get("candidate_id") != req["candidate_id"]:
        raise ValueError("candidate_id")
    if candidate_record.get("project_id") != req["project_id"]:
        raise ValueError("project_id")
    if candidate_record.get("candidate_type") != req["candidate_type"]:
        raise ValueError("candidate_type")
    if queue_entry is not None:
        if queue_entry.get("queue_entry_id") != req.get("queue_entry_id"):
            raise ValueError("invalid queue linkage")
        if queue_entry.get("candidate_record_id") != req["candidate_id"]:
            raise ValueError("invalid queue linkage")

    candidate_snapshot = req.get("source_candidate_snapshot_hash") or candidate_record.get(
        "snapshot_hash"
    )
    if candidate_snapshot and candidate_record.get("snapshot_hash"):
        if candidate_snapshot != candidate_record["snapshot_hash"]:
            raise ValueError("stale candidate snapshot")

    approved_payload = _normalize_approved_payload(req, candidate_record)
    promotion_plan_id = _stable_id(
        "promotion-plan",
        req["project_id"],
        req["candidate_id"],
        req["destination_type"],
        req.get("destination_key") or req["destination_path"],
        candidate_snapshot,
    )

    return validate_promotion_plan(
        {
            "promotion_plan_id": promotion_plan_id,
            "project_id": req["project_id"],
            "candidate_id": req["candidate_id"],
            "queue_entry_id": req.get("queue_entry_id"),
            "candidate_type": req["candidate_type"],
            "destination_type": req["destination_type"],
            "destination_path": req["destination_path"],
            "destination_key": req.get("destination_key"),
            "approved_payload": approved_payload,
            "evidence_refs": copy.deepcopy(req["evidence_refs"]),
            "provenance_refs": copy.deepcopy(req["provenance_refs"]),
            "source_locator_refs": copy.deepcopy(req["source_locator_refs"]),
            "owner_actor_id": req.get("owner_actor_id"),
            "owner_actor_label": req.get("owner_actor_label"),
            "owner_confirmation": True,
            "owner_note": req.get("owner_note", ""),
            "source_candidate_snapshot_hash": candidate_snapshot
            or _snapshot_hash(candidate_record),
            "validation_status": "valid",
            "boundary_flags": sorted(_BOUNDARY_FLAGS),
            "mutation_preview": {
                "will_mutate_only_after_apply": True,
                "target": req["destination_path"],
            },
            "mutation_performed": False,
            "dry_run": bool(req.get("dry_run", False)),
        }
    )


def validate_promotion_plan(plan: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(plan, dict):
        return _result("rejected", errors=["plan"])
    working = copy.deepcopy(plan)
    errors: list[str] = []

    for field in sorted(_REQUIRED_PLAN_FIELDS):
        if field not in working:
            errors.append(field)
    try:
        for field in ("promotion_plan_id", "project_id", "candidate_id"):
            if field in working:
                _safe_id(working[field], field)
        if working.get("queue_entry_id") is not None:
            _safe_id(working["queue_entry_id"], "queue_entry_id")
        if working.get("destination_key") is not None:
            _safe_id(working["destination_key"], "destination_key")
        if "destination_path" in working:
            _safe_destination_path(working["destination_path"])
    except ValueError as exc:
        errors.append(str(exc))

    if working.get("owner_confirmation") is not True:
        errors.append("owner_confirmation")
    if not (working.get("owner_actor_id") or working.get("owner_actor_label")):
        errors.append("owner_actor_id")
    if working.get("destination_type") not in ALLOWED_DESTINATION_TYPES:
        errors.append("destination_type")
    if working.get("candidate_type") not in candidate_schema.CORE_CANDIDATE_TYPES:
        errors.append("candidate_type")
    for field in ("evidence_refs", "provenance_refs", "source_locator_refs"):
        try:
            _require_ref_list(working, field)
        except ValueError:
            errors.append(field)
    forbidden_payload_key = _contains_forbidden_key(working.get("approved_payload", {}))
    if forbidden_payload_key:
        errors.append(forbidden_payload_key)

    if errors:
        working["validation_status"] = "rejected"
        result = _result("rejected", errors=errors)
        result.update(working)
        return result

    working["validation_status"] = "valid"
    working["boundary_flags"] = sorted(set(working.get("boundary_flags", [])) | set(_BOUNDARY_FLAGS))
    working["mutation_performed"] = False
    return working


def build_promotion_audit_record(
    plan: dict[str, Any],
    *,
    before_state_ref: str | None = None,
    after_state_ref: str | None = None,
) -> dict[str, Any]:
    status = plan.get("promotion_status") or ("dry_run" if plan.get("dry_run") else "applied")
    now = _now_iso()
    promotion_record_id = _stable_id(
        "promotion-record",
        plan.get("project_id"),
        plan.get("candidate_id"),
        plan.get("destination_type"),
        plan.get("destination_key") or plan.get("destination_path"),
        plan.get("source_candidate_snapshot_hash"),
    )
    return {
        "promotion_record_id": promotion_record_id,
        "project_id": plan.get("project_id"),
        "candidate_id": plan.get("candidate_id"),
        "queue_entry_id": plan.get("queue_entry_id"),
        "candidate_type": plan.get("candidate_type"),
        "source_candidate_snapshot_hash": plan.get("source_candidate_snapshot_hash")
        or _snapshot_hash(plan.get("approved_payload")),
        "destination_type": plan.get("destination_type"),
        "destination_path": plan.get("destination_path"),
        "destination_key": plan.get("destination_key"),
        "owner_actor_id": plan.get("owner_actor_id"),
        "owner_actor_label": plan.get("owner_actor_label"),
        "owner_confirmation": plan.get("owner_confirmation") is True,
        "owner_note": plan.get("owner_note", ""),
        "evidence_refs": copy.deepcopy(plan.get("evidence_refs", [])),
        "provenance_refs": copy.deepcopy(plan.get("provenance_refs", [])),
        "source_locator_refs": copy.deepcopy(plan.get("source_locator_refs", [])),
        "applied_at": now,
        "created_at": now,
        "promotion_status": status,
        "before_state_ref": before_state_ref,
        "after_state_ref": after_state_ref,
        "mutation_summary": {
            "destination_type": plan.get("destination_type"),
            "destination_path": plan.get("destination_path"),
            "approved_memory_only": True,
        },
        "boundary_flags": sorted(set(plan.get("boundary_flags", [])) | set(_BOUNDARY_FLAGS)),
        "no_generated_prose_confirmation": True,
        "no_model_call_confirmation": True,
        "no_training_artifact_confirmation": True,
    }


def validate_promotion_audit_record(record: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(record, dict):
        return _result("rejected", errors=["record"])
    working = copy.deepcopy(record)
    errors: list[str] = []
    for field in sorted(_REQUIRED_AUDIT_FIELDS):
        if field not in working:
            errors.append(field)
    if not (working.get("owner_actor_id") or working.get("owner_actor_label")):
        errors.append("owner_actor_id")
    if working.get("owner_confirmation") is not True:
        errors.append("owner_confirmation")
    if working.get("promotion_status") not in {"applied", "rejected", "blocked", "dry_run"}:
        errors.append("promotion_status")
    for field in ("no_generated_prose_confirmation", "no_model_call_confirmation", "no_training_artifact_confirmation"):
        if working.get(field) is not True:
            errors.append(field)
    for field in ("evidence_refs", "provenance_refs", "source_locator_refs"):
        try:
            _require_ref_list(working, field)
        except ValueError:
            errors.append(field)
    if errors:
        return _result("rejected", errors=errors)
    return {"validation_status": "valid", "record": working, "errors": [], "warnings": []}


def promotion_audit_storage_dir(project_dir: str | Path) -> Path:
    return _as_path(project_dir) / "writer_assistant" / "promotion_audit"


def promotion_audit_record_path(project_dir: str | Path, promotion_record_id: str) -> Path:
    safe_id = _safe_id(promotion_record_id, "promotion_record_id")
    return promotion_audit_storage_dir(project_dir) / f"{safe_id}.json"


def write_promotion_audit_record(record: dict[str, Any], *, project_dir: str | Path) -> dict[str, Any]:
    validated = validate_promotion_audit_record(record)
    if validated["validation_status"] != "valid":
        raise ValueError("invalid audit record")
    stored = validated["record"]
    path = promotion_audit_record_path(project_dir, stored["promotion_record_id"])
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        existing = read_promotion_audit_record(stored["promotion_record_id"], project_dir=project_dir)
        if existing != stored:
            raise FileExistsError("promotion audit record is append-only")
        return existing
    path.write_text(json.dumps(stored, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return stored


def read_promotion_audit_record(promotion_record_id: str, *, project_dir: str | Path) -> dict[str, Any]:
    path = promotion_audit_record_path(project_dir, promotion_record_id)
    if not path.is_file():
        raise ValueError("missing promotion audit record")
    loaded = json.loads(path.read_text(encoding="utf-8"))
    validated = validate_promotion_audit_record(loaded)
    if validated["validation_status"] != "valid":
        raise ValueError("invalid audit record")
    return validated["record"]


def list_promotion_audit_records(*, project_dir: str | Path) -> list[dict[str, Any]]:
    directory = promotion_audit_storage_dir(project_dir)
    if not directory.exists():
        return []
    records: list[dict[str, Any]] = []
    for item in directory.iterdir():
        if item.is_file() and item.suffix == ".json":
            records.append(read_promotion_audit_record(item.stem, project_dir=project_dir))
    records.sort(key=lambda record: record["promotion_record_id"])
    return records


def _approved_memory_path(project_dir: str | Path, plan: dict[str, Any]) -> Path:
    destination_key = plan.get("destination_key") or Path(plan["destination_path"]).stem
    safe_key = _safe_id(destination_key, "destination_key")
    destination_type = plan["destination_type"]
    if destination_type not in ALLOWED_DESTINATION_TYPES:
        raise ValueError("destination_type")
    return (
        _as_path(project_dir)
        / "writer_assistant"
        / "approved_memory"
        / destination_type
        / f"{safe_key}.json"
    )


def apply_promotion_plan(plan: dict[str, Any], *, project_dir: str | Path) -> dict[str, Any]:
    valid_plan = validate_promotion_plan(plan)
    if valid_plan.get("validation_status") != "valid":
        audit = build_promotion_audit_record({**plan, "promotion_status": "rejected"})
        return {
            "promotion_status": "rejected",
            "promotion_record_id": audit["promotion_record_id"],
            "mutation_performed": False,
            "partial_mutation_performed": False,
            "audit_record": audit,
            "errors": valid_plan.get("errors", ["invalid plan"]),
        }

    if valid_plan.get("source_candidate_snapshot_hash") == "stale":
        audit = build_promotion_audit_record({**valid_plan, "promotion_status": "blocked"})
        return {
            "promotion_status": "blocked",
            "promotion_record_id": audit["promotion_record_id"],
            "mutation_performed": False,
            "partial_mutation_performed": False,
            "audit_record": audit,
            "errors": ["stale candidate snapshot"],
        }

    approved_path = _approved_memory_path(project_dir, valid_plan)
    after_state_ref = str(approved_path.relative_to(_as_path(project_dir)))
    status = "dry_run" if valid_plan.get("dry_run") else "applied"
    audit = build_promotion_audit_record(
        {**valid_plan, "promotion_status": status},
        before_state_ref=None,
        after_state_ref=after_state_ref if status == "applied" else None,
    )

    if valid_plan.get("dry_run"):
        return {
            "promotion_status": "dry_run",
            "promotion_record_id": audit["promotion_record_id"],
            "mutation_performed": False,
            "partial_mutation_performed": False,
            "audit_record": audit,
            "errors": [],
        }

    if valid_plan.get("force_audit_write_failure"):
        blocked = build_promotion_audit_record({**valid_plan, "promotion_status": "blocked"})
        return {
            "promotion_status": "blocked",
            "promotion_record_id": blocked["promotion_record_id"],
            "mutation_performed": False,
            "partial_mutation_performed": False,
            "audit_record": blocked,
            "errors": ["audit write failure"],
        }

    try:
        written_audit = write_promotion_audit_record(audit, project_dir=project_dir)
    except Exception as exc:
        blocked = build_promotion_audit_record({**valid_plan, "promotion_status": "blocked"})
        return {
            "promotion_status": "blocked",
            "promotion_record_id": blocked["promotion_record_id"],
            "mutation_performed": False,
            "partial_mutation_performed": False,
            "audit_record": blocked,
            "errors": [str(exc) or "audit write failure"],
        }

    approved_path.parent.mkdir(parents=True, exist_ok=True)
    approved_object = {
        "schema_version": 1,
        "project_id": valid_plan["project_id"],
        "promotion_record_id": written_audit["promotion_record_id"],
        "candidate_id": valid_plan["candidate_id"],
        "candidate_type": valid_plan["candidate_type"],
        "destination_type": valid_plan["destination_type"],
        "destination_key": valid_plan.get("destination_key") or approved_path.stem,
        "approved_payload": copy.deepcopy(valid_plan["approved_payload"]),
        "evidence_refs": copy.deepcopy(valid_plan["evidence_refs"]),
        "provenance_refs": copy.deepcopy(valid_plan["provenance_refs"]),
        "source_locator_refs": copy.deepcopy(valid_plan["source_locator_refs"]),
        "owner_actor_id": valid_plan.get("owner_actor_id"),
        "owner_actor_label": valid_plan.get("owner_actor_label"),
        "owner_confirmation": True,
        "boundary_flags": sorted(_BOUNDARY_FLAGS),
    }
    approved_path.write_text(
        json.dumps(approved_object, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return {
        "promotion_status": "applied",
        "promotion_record_id": written_audit["promotion_record_id"],
        "mutation_performed": True,
        "partial_mutation_performed": False,
        "audit_record": written_audit,
        "approved_memory_path": str(approved_path),
        "errors": [],
    }


__all__ = (
    "validate_promotion_request",
    "build_promotion_plan",
    "validate_promotion_plan",
    "build_promotion_audit_record",
    "apply_promotion_plan",
    "validate_promotion_audit_record",
    "promotion_audit_storage_dir",
    "promotion_audit_record_path",
    "write_promotion_audit_record",
    "read_promotion_audit_record",
    "list_promotion_audit_records",
)


# T008D immutable apply-contract lifecycle.  The legacy plan helpers above stay
# readable until the final-apply route is replaced in Phase 5; none of these
# lifecycle operations call the legacy writer.

from backend.story_knowledge.apply_contract import (  # noqa: E402
    ApplyContractError,
    MAX_PREPARATION_BYTES,
    MAX_SEALED_REVISION_BYTES,
    build_preparation_artifact,
    build_revision,
    build_sealed_revision,
    canonical_json_bytes,
    canonical_sha256,
    load_preparation_artifact,
    load_revision,
    load_sealed_revision,
    preparation_id,
    preparation_scope_hash,
    publish_immutable_file,
    publish_preparation_artifact,
    publish_revision_from_preparation,
    require_closed_object,
    require_integer,
    require_string,
    sealed_revision_relative_path,
    strict_json_loads,
    validate_field_id,
    validate_safe_id,
    validate_preparation_artifact,
    validate_sha256,
    validate_uuid_v4,
)
from backend.story_knowledge.approved_records import (  # noqa: E402
    MAX_APPROVED_RECORD_BYTES,
    approved_record_material,
    approved_record_relative_path,
    build_approved_record,
    commit_approved_record,
    load_approved_record,
    validate_record_operation,
)
from backend.story_knowledge.owner_identity import load_local_owner_identity  # noqa: E402
from backend.story_knowledge.promotion_apply_events import (  # noqa: E402
    append_event,
    scan_event_chain,
)
from backend.story_knowledge.promotion_apply_runtime import (  # noqa: E402
    FinalChallengeRegistry,
)


_REVISION_FILE_RE = re.compile(r"^revision_([1-9][0-9]{0,2})\.json$")
_SEALED_FILE_RE = re.compile(r"^sealed_revision_([1-9][0-9]{0,2})\.json$")
_TERMINAL_EVENT_TYPES = {
    "apply_intent",
    "apply_completed",
    "apply_failed_before_commit",
    "recovery_required",
    "recovery_completed",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _association(
    *, project_id: str, promotion_id: str, promotion: dict[str, Any], candidate: dict[str, Any]
) -> tuple[str, dict[str, Any]]:
    validate_safe_id(project_id, "project_id")
    validate_safe_id(promotion_id, "promotion_id")
    if not isinstance(promotion, dict) or not isinstance(candidate, dict):
        raise ApplyContractError("PROMOTION_ASSOCIATION_INVALID")
    candidate_id = promotion.get("candidate_id")
    validate_safe_id(candidate_id, "candidate_id")
    if (
        promotion.get("project_id") != project_id
        or promotion.get("promotion_id") != promotion_id
        or candidate.get("project_id") != project_id
        or candidate.get("candidate_id") != candidate_id
    ):
        raise ApplyContractError("PROMOTION_ASSOCIATION_INVALID")
    snapshot = promotion.get("source_snapshot")
    if not isinstance(snapshot, dict):
        raise ApplyContractError("PROMOTION_SOURCE_SNAPSHOT_REQUIRED")
    if snapshot.get("project_id") != project_id or snapshot.get("candidate_id") != candidate_id:
        raise ApplyContractError("PROMOTION_ASSOCIATION_INVALID")
    return candidate_id, snapshot


def _normalized_authority_refs(
    *, project_id: str, promotion_id: str, candidate_id: str, promotion: dict[str, Any], snapshot: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    candidate_locator = {
        "locator_id": "candidate_snapshot",
        "locator_kind": "omi_candidate_snapshot",
        "locator": f"omi/candidates/{candidate_id}.json#source_snapshot",
        "content_hash": canonical_sha256(snapshot),
    }
    promotion_locator = {
        "locator_id": "promotion_handoff",
        "locator_kind": "omi_promotion",
        "locator": f"omi/promotions/{promotion_id}.json",
        "content_hash": canonical_sha256(promotion),
    }
    locators = [candidate_locator, promotion_locator]

    evidence_input = promotion.get("evidence")
    if evidence_input is None:
        evidence_input = snapshot.get("evidence")
    if not isinstance(evidence_input, list) or not evidence_input:
        raise ApplyContractError("PROMOTION_EVIDENCE_REQUIRED")
    evidence_refs: list[dict[str, Any]] = []
    for index, evidence in enumerate(evidence_input, start=1):
        digest = canonical_sha256(evidence)
        evidence_refs.append(
            {
                "ref_id": f"evidence_{index}",
                "locator_id": "candidate_snapshot",
                "content_hash": digest,
            }
        )

    provenance_input = promotion.get("provenance")
    if provenance_input is None:
        provenance_input = snapshot.get("provenance")
    if isinstance(provenance_input, dict) and "source_type" not in provenance_input and "source_kind" not in provenance_input:
        provenance_items = list(provenance_input.values())
    else:
        provenance_items = provenance_input if isinstance(provenance_input, list) else [provenance_input]
    if not provenance_items or any(not isinstance(item, dict) for item in provenance_items):
        raise ApplyContractError("PROMOTION_PROVENANCE_REQUIRED")
    provenance_refs: list[dict[str, Any]] = []
    for index, item in enumerate(provenance_items, start=1):
        source_kind = item.get("source_type") or item.get("source_kind")
        validate_field_id(source_kind, "source_kind")
        source_id = item.get("source_path") or item.get("source_label") or item.get("source_id")
        require_string(source_id, label="source_id", minimum=1, maximum=256)
        provenance_refs.append(
            {
                "provenance_id": f"provenance_{index}",
                "source_kind": source_kind,
                "source_id": source_id,
                "locator_id": "candidate_snapshot",
                "content_hash": canonical_sha256(item),
            }
        )
    return evidence_refs, provenance_refs, locators


def _safe_current_record(
    project_dir: Path, destination_type: str, destination_key: str, *, ordinary: bool = True
) -> tuple[dict[str, Any] | None, str, Path]:
    relative = approved_record_relative_path(
        destination_type, destination_key, ordinary=ordinary
    )
    root = project_dir.resolve(strict=True)
    current = root
    for part in relative.parts[:-1]:
        current = current / part
        if current.exists() or current.is_symlink():
            metadata = os.lstat(current)
            if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
                raise ApplyContractError("APPROVED_RECORD_UNSAFE_PATH")
        else:
            return None, relative.as_posix(), root / relative
    target = root / relative
    try:
        metadata = os.lstat(target)
    except FileNotFoundError:
        return None, relative.as_posix(), target
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
        raise ApplyContractError("APPROVED_RECORD_UNSAFE_PATH")
    if metadata.st_size > MAX_APPROVED_RECORD_BYTES:
        raise ApplyContractError("APPROVED_RECORD_TOO_LARGE")
    material = load_approved_record(target, ordinary=ordinary)
    return material.record, relative.as_posix(), target


def _before_state(
    project_dir: Path, destination_type: str, destination_key: str, *, observed_at: str
) -> dict[str, Any]:
    record, relative, _ = _safe_current_record(project_dir, destination_type, destination_key)
    if record is None:
        state = {
            "state": "absent",
            "path": relative,
            "record_version": None,
            "content_hash": None,
            "content": None,
        }
    else:
        state = {
            "state": "present",
            "path": relative,
            "record_version": record["record_version"],
            "content_hash": canonical_sha256(record),
            "content": record,
        }
    token = canonical_sha256({"protocol": "approved-before-state.v1", **state})
    return {**state, "observed_at": observed_at, "snapshot_token": token}


def _closed_prepare_request(body: Any) -> dict[str, Any]:
    request = require_closed_object(
        body,
        required={
            "idempotency_key", "expected_latest_revision", "expected_latest_draft_scope_hash",
            "operation", "approved_destination_type", "destination_key", "payload",
            "duplicate_resolution", "dependency_resolution", "supersession",
        },
        optional={"owner_note"},
        label="preparation request",
    )
    validate_uuid_v4(request["idempotency_key"])
    if request["expected_latest_revision"] is not None:
        require_integer(request["expected_latest_revision"], label="expected_latest_revision", minimum=1, maximum=255)
    if request["expected_latest_draft_scope_hash"] is not None:
        validate_sha256(request["expected_latest_draft_scope_hash"], "expected_latest_draft_scope_hash")
    if request["operation"] not in {"create", "update"}:
        raise ApplyContractError("APPLY_OPERATION_INVALID")
    approved_record_relative_path(request["approved_destination_type"], request["destination_key"])
    if not isinstance(request["payload"], dict):
        raise ApplyContractError("SCHEMA_TYPE_MISMATCH", "payload")
    if "owner_note" in request:
        require_string(request["owner_note"], label="owner_note", maximum=4096)
    _validate_decision_inputs(request["duplicate_resolution"], request["dependency_resolution"])
    _validate_supersession(request["supersession"])
    return request


def _validate_decision_inputs(duplicate: Any, dependency: Any) -> None:
    duplicate = require_closed_object(
        duplicate,
        required={"state", "rationale", "evidence_ref_ids", "reviewed_candidate_ids", "reviewed_approved_records"},
        label="duplicate resolution input",
    )
    if duplicate["state"] not in {"unresolved", "distinct_record", "update_existing", "merge_into_existing", "do_not_apply"}:
        raise ApplyContractError("APPLY_CONTRACT_DUPLICATE_RESOLUTION_INVALID")
    require_string(duplicate["rationale"], label="duplicate rationale", minimum=1, maximum=4096)
    for field in ("evidence_ref_ids", "reviewed_candidate_ids"):
        if not isinstance(duplicate[field], list) or len(duplicate[field]) > 128:
            raise ApplyContractError("SCHEMA_ARRAY_INVALID", field)
        for value in duplicate[field]:
            validate_safe_id(value, field)
        if len(set(duplicate[field])) != len(duplicate[field]):
            raise ApplyContractError("SCHEMA_ARRAY_ITEMS_NOT_UNIQUE", field)
    if not isinstance(duplicate["reviewed_approved_records"], list) or len(duplicate["reviewed_approved_records"]) > 128:
        raise ApplyContractError("SCHEMA_ARRAY_INVALID", "reviewed_approved_records")
    dependency = require_closed_object(
        dependency,
        required={"state", "dependencies", "rationale", "evidence_ref_ids"},
        label="dependency resolution input",
    )
    if dependency["state"] not in {"unresolved", "none_declared", "satisfied", "blocked"}:
        raise ApplyContractError("APPLY_CONTRACT_DEPENDENCY_RESOLUTION_INVALID")
    require_string(dependency["rationale"], label="dependency rationale", minimum=1, maximum=4096)
    if not isinstance(dependency["evidence_ref_ids"], list) or len(dependency["evidence_ref_ids"]) > 128:
        raise ApplyContractError("SCHEMA_ARRAY_INVALID", "evidence_ref_ids")
    for value in dependency["evidence_ref_ids"]:
        validate_safe_id(value, "evidence_ref_ids")
    if not isinstance(dependency["dependencies"], list) or len(dependency["dependencies"]) > 256:
        raise ApplyContractError("SCHEMA_ARRAY_INVALID", "dependencies")
    required = {"dependency_id", "kind", "required", "status", "target", "rationale", "evidence_ref_ids", "provenance_ref_ids"}
    for entry in dependency["dependencies"]:
        item = require_closed_object(entry, required=required, optional={"applicability_rule"}, label="dependency input")
        validate_safe_id(item["dependency_id"], "dependency_id")
        validate_field_id(item["kind"], "kind")
        if not isinstance(item["required"], bool) or item["status"] not in {"unresolved", "satisfied", "not_applicable", "blocked"}:
            raise ApplyContractError("APPLY_CONTRACT_DEPENDENCY_RESOLUTION_INVALID")
        require_string(item["rationale"], label="dependency rationale", minimum=1, maximum=4096)
        for field in ("evidence_ref_ids", "provenance_ref_ids"):
            if not isinstance(item[field], list) or len(item[field]) > 128:
                raise ApplyContractError("SCHEMA_ARRAY_INVALID", field)
            for value in item[field]:
                validate_safe_id(value, field)


def _validate_supersession(value: Any) -> None:
    if value is None:
        return
    if not isinstance(value, dict) or value.get("kind") not in {"draft", "sealed"}:
        raise ApplyContractError("APPLY_CONTRACT_SUPERSESSION_INVALID")
    if value["kind"] == "draft":
        require_closed_object(value, required={"kind", "superseded_revision", "superseded_draft_scope_hash", "rationale"}, label="draft supersession")
        validate_sha256(value["superseded_draft_scope_hash"], "superseded_draft_scope_hash")
    else:
        require_closed_object(value, required={"kind", "superseded_revision", "sealed_contract_hash", "rationale", "confirmed"}, label="sealed supersession")
        validate_sha256(value["sealed_contract_hash"], "sealed_contract_hash")
        if value["confirmed"] is not True:
            raise ApplyContractError("APPLY_CONTRACT_SUPERSESSION_INVALID")
    require_integer(value["superseded_revision"], label="superseded_revision", minimum=1, maximum=255)
    require_string(value["rationale"], label="supersession rationale", minimum=1, maximum=4096)


def _stamp_decisions(
    *, duplicate: dict[str, Any], dependency: dict[str, Any], owner: dict[str, Any], decided_at: str,
    operation: str, evidence_ids: set[str], provenance_ids: set[str]
) -> tuple[dict[str, Any], dict[str, Any]]:
    duplicate = copy.deepcopy(duplicate)
    if operation == "create" and duplicate["state"] not in {"unresolved", "distinct_record", "do_not_apply"}:
        raise ApplyContractError("APPLY_CONTRACT_DUPLICATE_RESOLUTION_INVALID")
    if operation == "update" and duplicate["state"] not in {"unresolved", "update_existing", "merge_into_existing", "do_not_apply"}:
        raise ApplyContractError("APPLY_CONTRACT_DUPLICATE_RESOLUTION_INVALID")
    if not set(duplicate["evidence_ref_ids"]).issubset(evidence_ids):
        raise ApplyContractError("APPLY_CONTRACT_EVIDENCE_REFERENCE_INVALID")
    duplicate["evidence_refs"] = duplicate.pop("evidence_ref_ids")
    if duplicate["state"] == "unresolved":
        duplicate.update(resolved_by=None, resolved_at=None, resolution_scope_hash=None)
    else:
        duplicate.update(resolved_by=copy.deepcopy(owner), resolved_at=decided_at)
        duplicate["resolution_scope_hash"] = canonical_sha256({"protocol": "duplicate-resolution.v1", "operation": operation, **duplicate})

    dependency = copy.deepcopy(dependency)
    if not set(dependency["evidence_ref_ids"]).issubset(evidence_ids):
        raise ApplyContractError("APPLY_CONTRACT_EVIDENCE_REFERENCE_INVALID")
    stamped_entries = []
    for entry in dependency["dependencies"]:
        if not set(entry["evidence_ref_ids"]).issubset(evidence_ids) or not set(entry["provenance_ref_ids"]).issubset(provenance_ids):
            raise ApplyContractError("APPLY_CONTRACT_DEPENDENCY_REFERENCE_INVALID")
        stamped = copy.deepcopy(entry)
        resolved = stamped["status"] != "unresolved"
        stamped.update(resolved_by=copy.deepcopy(owner) if resolved else None, resolved_at=decided_at if resolved else None)
        stamped_entries.append(stamped)
    dependency["dependencies"] = stamped_entries
    if dependency["state"] == "unresolved":
        dependency.update(resolved_by=None, resolved_at=None, resolution_scope_hash=None)
    else:
        dependency.update(resolved_by=copy.deepcopy(owner), resolved_at=decided_at)
        dependency["resolution_scope_hash"] = canonical_sha256({"protocol": "dependency-resolution.v1", **dependency})
    return duplicate, dependency


def _contract_dir(project_dir: Path, promotion_id: str) -> Path:
    return project_dir / "writer_assistant" / "apply_contracts" / promotion_id


def _preparation_materials(project_dir: Path, promotion_id: str) -> list[Any]:
    directory = _contract_dir(project_dir, promotion_id) / "preparations"
    if not directory.exists() and not directory.is_symlink():
        return []
    metadata = os.lstat(directory)
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
        raise ApplyContractError("APPLY_CONTRACT_PREPARATION_ARTIFACT_CORRUPT")
    materials: list[Any] = []
    for path in sorted(directory.iterdir(), key=lambda item: os.fsencode(item.name)):
        if path.name.startswith(".tmp-"):
            continue
        metadata = os.lstat(path)
        if (
            stat.S_ISLNK(metadata.st_mode)
            or not stat.S_ISREG(metadata.st_mode)
            or metadata.st_nlink != 1
            or metadata.st_size > MAX_PREPARATION_BYTES
        ):
            raise ApplyContractError("APPLY_CONTRACT_PREPARATION_ARTIFACT_CORRUPT")
        raw = path.read_bytes()
        try:
            material = validate_preparation_artifact(
                strict_json_loads(raw, max_bytes=MAX_PREPARATION_BYTES)
            )
        except ApplyContractError as exc:
            raise ApplyContractError(
                "APPLY_CONTRACT_PREPARATION_ARTIFACT_CORRUPT"
            ) from exc
        if (
            path.name != f"{material.artifact['preparation_id']}.json"
            or raw != material.artifact_bytes
        ):
            raise ApplyContractError("APPLY_CONTRACT_PREPARATION_ARTIFACT_CORRUPT")
        materials.append(material)
    return materials


def _incomplete_preparations(
    project_dir: Path, promotion_id: str, events: list[dict[str, Any]]
) -> list[str]:
    prepared_ids = {
        event["preparation_id"]
        for event in events
        if event["event_type"] == "draft_prepared"
    }
    superseded_ids = {
        event["preparation_id"]
        for event in events
        if event["event_type"] in {"draft_superseded", "contract_superseded"}
    }
    incomplete: list[str] = []
    for material in _preparation_materials(project_dir, promotion_id):
        artifact = material.artifact
        complete = artifact["preparation_id"] in prepared_ids
        if artifact["supersession_kind"] != "none":
            complete = complete and artifact["preparation_id"] in superseded_ids
        if not complete:
            incomplete.append(artifact["preparation_id"])
    return incomplete


def _preparation_diagnostics(
    project_dir: Path,
    promotion_id: str,
    preparation_ids: list[str],
    events: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    event_types = {
        preparation_id: {
            event["event_type"]
            for event in events
            if event.get("preparation_id") == preparation_id
        }
        for preparation_id in preparation_ids
    }
    diagnostics: list[dict[str, Any]] = []
    directory = _contract_dir(project_dir, promotion_id) / "preparations"
    for preparation_id_value in preparation_ids:
        raw = (directory / f"{preparation_id_value}.json").read_bytes()
        material = validate_preparation_artifact(
            strict_json_loads(raw, max_bytes=MAX_PREPARATION_BYTES)
        )
        artifact = material.artifact
        revision_exists = (project_dir / artifact["revision_path"]).is_file()
        types = event_types[preparation_id_value]
        if not revision_exists:
            status = "preparation_artifact_published"
        elif "draft_preparation_started" not in types:
            status = "preparation_revision_published"
        else:
            status = "preparation_events_incomplete"
        diagnostics.append(
            {
                "status": status,
                "preparation_id": preparation_id_value,
                "preparation_path": artifact["preparation_path"],
                "revision": artifact["assigned_revision"],
                "revision_path": artifact["revision_path"],
                "revision_canonical_hash": artifact["revision_canonical_hash"],
                "draft_scope_hash": artifact["draft_scope_hash"],
                "same_key_retry_can_resume": True,
            }
        )
    return diagnostics


def derive_apply_contract_lineage(
    *, project_dir: Path, project_id: str, promotion_id: str, candidate_id: str
) -> dict[str, Any]:
    directory = _contract_dir(project_dir, promotion_id)
    revisions: list[dict[str, Any]] = []
    seals: dict[int, dict[str, Any]] = {}
    if directory.exists() or directory.is_symlink():
        metadata = os.lstat(directory)
        if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
            raise ApplyContractError("APPLY_CONTRACT_STORAGE_UNSAFE")
        revision_numbers: list[int] = []
        sealed_numbers: list[int] = []
        for entry in directory.iterdir():
            revision_match = _REVISION_FILE_RE.fullmatch(entry.name)
            sealed_match = _SEALED_FILE_RE.fullmatch(entry.name)
            if revision_match:
                revision_numbers.append(int(revision_match.group(1)))
            elif sealed_match:
                sealed_numbers.append(int(sealed_match.group(1)))
            elif entry.name != "preparations" and not entry.name.startswith(".tmp-"):
                raise ApplyContractError("APPLY_CONTRACT_STORAGE_UNSAFE")
        if sorted(revision_numbers) != list(range(1, len(revision_numbers) + 1)):
            raise ApplyContractError("APPLY_CONTRACT_REVISION_LINEAGE_INVALID")
        for number in sorted(revision_numbers):
            revision = load_revision(project_dir, promotion_id=promotion_id, revision=number)
            if revision["project_id"] != project_id or revision["candidate_id"] != candidate_id:
                raise ApplyContractError("PROMOTION_ASSOCIATION_INVALID")
            revisions.append(revision)
        for number in sorted(sealed_numbers):
            if number not in revision_numbers:
                raise ApplyContractError("APPLY_CONTRACT_SEALED_REVISION_CORRUPT")
            sealed = load_sealed_revision(project_dir, promotion_id=promotion_id, revision=number)
            if sealed["revision"] != revisions[number - 1]:
                raise ApplyContractError("APPLY_CONTRACT_SEALED_REVISION_CORRUPT")
            seals[number] = sealed
    preparation_materials = _preparation_materials(Path(project_dir), promotion_id)
    preparations_by_revision: dict[int, list[Any]] = {}
    for material in preparation_materials:
        artifact = material.artifact
        if (
            artifact["project_id"] != project_id
            or artifact["promotion_id"] != promotion_id
            or artifact["candidate_id"] != candidate_id
        ):
            raise ApplyContractError("PROMOTION_ASSOCIATION_INVALID")
        preparations_by_revision.setdefault(
            artifact["assigned_revision"], []
        ).append(material)
    if any(len(materials) != 1 for materials in preparations_by_revision.values()):
        raise ApplyContractError(
            "APPLY_CONTRACT_PREPARATION_REVISION_CONFLICT"
        )
    for number, revision in enumerate(revisions, start=1):
        assigned = preparations_by_revision.get(number, [])
        if not assigned:
            raise ApplyContractError(
                "APPLY_CONTRACT_PREPARATION_ARTIFACT_MISSING"
            )
        if len(assigned) != 1:
            raise ApplyContractError(
                "APPLY_CONTRACT_PREPARATION_REVISION_CONFLICT"
            )
        if (
            assigned[0].revision_bytes
            != canonical_json_bytes(revision)
        ):
            raise ApplyContractError(
                "APPLY_CONTRACT_PREPARATION_REVISION_CONFLICT"
            )
    if any(number > len(revisions) + 1 for number in preparations_by_revision):
        raise ApplyContractError("APPLY_CONTRACT_PREPARATION_ARTIFACT_CORRUPT")

    chain = scan_event_chain(project_dir, project_id=project_id, promotion_id=promotion_id)
    preparation_events: dict[str, list[dict[str, Any]]] = {}
    for event in chain.events:
        if event["candidate_id"] != candidate_id:
            raise ApplyContractError("PROMOTION_ASSOCIATION_INVALID")
        if event["revision"] is not None and not 1 <= event["revision"] <= len(revisions):
            raise ApplyContractError("APPLY_EVENT_REFERENCE_MISSING_OR_CORRUPT")
        if event["event_type"] in {
            "draft_preparation_started", "draft_prepared", "draft_superseded", "contract_superseded"
        }:
            try:
                material = load_preparation_artifact(
                    project_dir,
                    project_id=project_id,
                    promotion_id=promotion_id,
                    idempotency_key=event["idempotency_key"],
                )
            except ApplyContractError as exc:
                raise ApplyContractError("APPLY_EVENT_REFERENCE_MISSING_OR_CORRUPT") from exc
            if (
                material.artifact["preparation_id"] != event["preparation_id"]
                or material.artifact["assigned_revision"] != event["revision"]
            ):
                raise ApplyContractError("APPLY_EVENT_REFERENCE_MISSING_OR_CORRUPT")
            artifact = material.artifact
            common_expected = {
                "preparation_scope_hash": artifact["preparation_scope_hash"],
                "operation_identity": artifact["preparation_id"],
            }
            if event["event_type"] == "draft_preparation_started":
                common_expected.update(
                    {
                        "preparation_path": artifact["preparation_path"],
                        "preparation_artifact_hash": material.artifact_hash,
                        "preparation_artifact_size": len(material.artifact_bytes),
                        "canonical_request_body_hash": artifact[
                            "canonical_request_body_hash"
                        ],
                        "assigned_revision": artifact["assigned_revision"],
                        "planned_draft_scope_hash": artifact["draft_scope_hash"],
                        "revision_path": artifact["revision_path"],
                        "revision_canonical_hash": artifact[
                            "revision_canonical_hash"
                        ],
                        "revision_canonical_size": artifact[
                            "revision_canonical_size"
                        ],
                        "approved_record_hash": artifact["approved_record_hash"],
                        "approved_record_size": artifact["approved_record_size"],
                        "authoritative_owner_actor": artifact["revision"][
                            "prepared_by"
                        ],
                        "supersession_kind": artifact["supersession_kind"],
                        "expected_latest_revision": artifact[
                            "prior_lineage_expectations"
                        ]["expected_latest_revision"],
                        "expected_latest_draft_scope_hash": artifact[
                            "prior_lineage_expectations"
                        ]["expected_latest_draft_scope_hash"],
                    }
                )
            elif event["event_type"] == "draft_prepared":
                common_expected.update(
                    {
                        "preparation_path": artifact["preparation_path"],
                        "preparation_artifact_hash": material.artifact_hash,
                        "revision_path": artifact["revision_path"],
                        "revision_canonical_hash": artifact[
                            "revision_canonical_hash"
                        ],
                        "revision_canonical_size": artifact[
                            "revision_canonical_size"
                        ],
                        "draft_scope_hash": artifact["draft_scope_hash"],
                        "approved_record_hash": artifact["approved_record_hash"],
                        "approved_record_size": artifact["approved_record_size"],
                    }
                )
            else:
                common_expected["superseding_revision"] = artifact[
                    "assigned_revision"
                ]
                common_expected["superseding_draft_scope_hash"] = artifact[
                    "draft_scope_hash"
                ]
                expectations = artifact["prior_lineage_expectations"]
                if event["event_type"] == "draft_superseded":
                    common_expected.update(
                        {
                            "superseded_revision": expectations[
                                "expected_latest_revision"
                            ],
                            "superseded_draft_scope_hash": expectations[
                                "expected_latest_draft_scope_hash"
                            ],
                        }
                    )
                else:
                    common_expected.update(
                        {
                            "superseded_revision": expectations[
                                "expected_active_sealed_revision"
                            ],
                            "sealed_contract_hash": expectations[
                                "expected_active_sealed_contract_hash"
                            ],
                        }
                    )
                expected_kind = (
                    "draft"
                    if event["event_type"] == "draft_superseded"
                    else "sealed"
                )
                if artifact["supersession_kind"] != expected_kind:
                    raise ApplyContractError(
                        "APPLY_EVENT_REFERENCE_MISSING_OR_CORRUPT"
                    )
            if any(event.get(field) != expected for field, expected in common_expected.items()):
                raise ApplyContractError(
                    "APPLY_EVENT_REFERENCE_MISSING_OR_CORRUPT"
                )
            preparation_events.setdefault(
                artifact["preparation_id"], []
            ).append(event)
    for preparation_id_value, related in preparation_events.items():
        started = [
            event for event in related
            if event["event_type"] == "draft_preparation_started"
        ]
        prepared = [
            event for event in related if event["event_type"] == "draft_prepared"
        ]
        if len(started) > 1 or len(prepared) > 1:
            raise ApplyContractError("AMBIGUOUS_OR_CONFLICTING_HISTORY")
        if prepared and (
            len(started) != 1
            or prepared[0]["preparation_start_event_id"]
            != started[0]["event_id"]
        ):
            raise ApplyContractError("APPLY_EVENT_REFERENCE_MISSING_OR_CORRUPT")
    approved = [event for event in chain.events if event["event_type"] == "contract_approved"]
    recorded_approvals = [
        event for event in chain.events
        if event["event_type"] == "contract_approval_recorded"
    ]
    activated_approval_ids = {event["approval_event_id"] for event in approved}
    incomplete_approval_ids = [
        event["event_id"] for event in recorded_approvals
        if event["event_id"] not in activated_approval_ids
    ]
    if len(incomplete_approval_ids) > 1:
        raise ApplyContractError("AMBIGUOUS_OR_CONFLICTING_HISTORY")
    revoked_hashes = {event["sealed_contract_hash"] for event in chain.events if event["event_type"] in {"contract_revoked", "contract_superseded"}}
    active = [event for event in approved if event["sealed_contract_hash"] not in revoked_hashes]
    if len(active) > 1:
        raise ApplyContractError("AMBIGUOUS_OR_CONFLICTING_HISTORY")
    for event in approved:
        sealed = seals.get(event["revision"])
        approval_matches = [
            approval for approval in recorded_approvals
            if approval["event_id"] == event["approval_event_id"]
        ]
        if (
            sealed is None
            or len(approval_matches) != 1
            or sealed["sealed_contract_hash"] != event["sealed_contract_hash"]
            or sealed["approval_event_id"] != event["approval_event_id"]
            or event["sealed_revision_path"]
            != sealed_revision_relative_path(
                promotion_id, event["revision"]
            ).as_posix()
            or event["draft_scope_hash"]
            != sealed["revision"]["draft_scope_hash"]
            or approval_matches[0]["contract_approval"]
            != sealed["contract_approval"]
            or approval_matches[0]["draft_scope_hash"]
            != event["draft_scope_hash"]
            or approval_matches[0]["idempotency_key"]
            != event["idempotency_key"]
            or approval_matches[0]["operation_identity"]
            != event["operation_identity"]
        ):
            raise ApplyContractError("APPLY_EVENT_REFERENCE_MISSING_OR_CORRUPT")
    for number, sealed in seals.items():
        matching_recorded = [
            event for event in recorded_approvals
            if event["event_id"] == sealed["approval_event_id"]
            and event["revision"] == number
            and event["contract_approval"] == sealed["contract_approval"]
        ]
        if len(matching_recorded) != 1:
            raise ApplyContractError("APPLY_EVENT_REFERENCE_MISSING_OR_CORRUPT")
    seal_events_by_hash = {
        event["sealed_contract_hash"]: event for event in approved
    }
    if len(seal_events_by_hash) != len(approved):
        raise ApplyContractError("AMBIGUOUS_OR_CONFLICTING_HISTORY")
    terminal_seal_events = [
        event for event in chain.events
        if event["event_type"] in {"contract_revoked", "contract_superseded"}
    ]
    terminal_hashes = [event["sealed_contract_hash"] for event in terminal_seal_events]
    if len(terminal_hashes) != len(set(terminal_hashes)):
        raise ApplyContractError("AMBIGUOUS_OR_CONFLICTING_HISTORY")
    for event in terminal_seal_events:
        activation = seal_events_by_hash.get(event["sealed_contract_hash"])
        sealed = seals.get(event["superseded_revision"] if event["event_type"] == "contract_superseded" else event["revision"])
        if (
            activation is None
            or sealed is None
            or activation["revision"]
            != (
                event["superseded_revision"]
                if event["event_type"] == "contract_superseded"
                else event["revision"]
            )
            or sealed["sealed_contract_hash"] != event["sealed_contract_hash"]
            or event["authoritative_owner_actor"]
            != sealed["contract_approval"]["owner_actor"]
        ):
            raise ApplyContractError("APPLY_EVENT_REFERENCE_MISSING_OR_CORRUPT")
    latest = revisions[-1] if revisions else None
    intents = [event for event in chain.events if event["event_type"] == "apply_intent"]
    completions = [event for event in chain.events if event["event_type"] == "apply_completed"]
    failures = [
        event for event in chain.events
        if event["event_type"] == "apply_failed_before_commit"
    ]
    recoveries = [event for event in chain.events if event["event_type"] == "recovery_completed"]
    recovery_required_events = [
        event for event in chain.events if event["event_type"] == "recovery_required"
    ]
    if len(completions) > 1:
        raise ApplyContractError("AMBIGUOUS_OR_CONFLICTING_HISTORY")
    intents_by_id = {event["apply_id"]: event for event in intents}
    if len(intents_by_id) != len(intents):
        raise ApplyContractError("AMBIGUOUS_OR_CONFLICTING_HISTORY")
    for event in completions + failures + recoveries + recovery_required_events:
        intent = intents_by_id.get(event["apply_id"])
        if intent is None or event["intent_event_id"] != intent["event_id"]:
            raise ApplyContractError("APPLY_EVENT_REFERENCE_MISSING_OR_CORRUPT")
    for intent in intents:
        sealed = seals.get(intent["revision"])
        seal_events = [
            event for event in approved
            if event["event_id"] == intent["seal_event_id"]
        ]
        if sealed is None or len(seal_events) != 1:
            raise ApplyContractError("APPLY_EVENT_REFERENCE_MISSING_OR_CORRUPT")
        _validate_intent_contract(intent, sealed, seal_events[0])
    for completion in completions:
        intent = intents_by_id[completion["apply_id"]]
        revision = seals[intent["revision"]]["revision"]
        _validate_completion(completion, intent, revision)
        if not _observation_matches_after(
            _destination_observation(Path(project_dir), revision), revision
        ):
            raise ApplyContractError("APPLY_COMPLETION_RECORD_MISMATCH")
    for recovery in recoveries:
        intent = intents_by_id[recovery["apply_id"]]
        revision = seals[intent["revision"]]["revision"]
        required_reference = recovery["recovery_required_event_id"]
        if required_reference is not None:
            matching_required = [
                event for event in recovery_required_events
                if event["event_id"] == required_reference
                and event["apply_id"] == recovery["apply_id"]
            ]
            if len(matching_required) != 1:
                raise ApplyContractError(
                    "APPLY_EVENT_REFERENCE_MISSING_OR_CORRUPT"
                )
        if recovery["outcome"] == "committed" and (
            recovery["approved_record_hash"] != intent["approved_record_hash"]
            or recovery["approved_record_size"] != intent["approved_record_size"]
            or recovery["approved_record_version"]
            != revision["proposed_approved_record"]["record_version"]
        ):
            raise ApplyContractError("APPLY_COMMITTED_RECORD_MISMATCH")
        observation = _destination_observation(Path(project_dir), revision)
        if recovery["outcome"] == "committed":
            if not _observation_matches_after(observation, revision):
                raise ApplyContractError("APPLY_COMMITTED_RECORD_MISMATCH")
        elif not _observation_matches_before(observation, revision):
            raise ApplyContractError("RECOVERY_REQUIRED")
    terminal_apply_ids = {
        event["apply_id"] for event in completions + recoveries
    }
    active_intents = [
        event for event in intents if event["apply_id"] not in terminal_apply_ids
    ]
    if len(active_intents) > 1:
        raise ApplyContractError("AMBIGUOUS_OR_CONFLICTING_HISTORY")
    unresolved_recovery_ids = {
        event["apply_id"] for event in recovery_required_events
    } - {event["apply_id"] for event in recoveries}
    committed_recovery_ids = {
        event["apply_id"] for event in recoveries if event["outcome"] == "committed"
    }
    if completions:
        state = "applied"
    elif committed_recovery_ids:
        state = "recovery_completed"
    elif unresolved_recovery_ids:
        state = "recovery_required"
    elif active_intents:
        state = "apply_intent"
    elif active:
        state = "sealed_active"
    elif approved and not latest:
        state = "revoked"
    elif approved and latest and latest["revision"] == approved[-1]["revision"]:
        state = "revoked"
    elif latest:
        prepared = [event for event in chain.events if event["event_type"] == "draft_prepared" and event["revision"] == latest["revision"] and event["draft_scope_hash"] == latest["draft_scope_hash"]]
        state = "draft_active" if len(prepared) == 1 else "preparation_events_incomplete"
    else:
        state = "no_contract"
    if incomplete_approval_ids and state not in {"applied", "recovery_required"}:
        state = "approval_publication_incomplete"
    incomplete_preparation_ids = _incomplete_preparations(
        Path(project_dir), promotion_id, list(chain.events)
    )
    preparation_diagnostics = _preparation_diagnostics(
        Path(project_dir), promotion_id, incomplete_preparation_ids, list(chain.events)
    )
    if incomplete_preparation_ids:
        state = preparation_diagnostics[0]["status"]
    active_sealed = seals.get(active[0]["revision"]) if active else None
    return {
        "state": state,
        "latest_revision": None if latest is None else latest["revision"],
        "latest_draft_scope_hash": None if latest is None else latest["draft_scope_hash"],
        "active_sealed_revision": None if active_sealed is None else active_sealed["revision"]["revision"],
        "active_sealed_contract_hash": None if active_sealed is None else active_sealed["sealed_contract_hash"],
        "revisions": revisions,
        "seals": seals,
        "events": list(chain.events),
        "temporary_residue": list(chain.temporary_residue),
        "incomplete_preparation_ids": incomplete_preparation_ids,
        "preparation_status": preparation_diagnostics,
        "incomplete_approval_event_id": incomplete_approval_ids[0] if incomplete_approval_ids else None,
    }


def _append_preparation_events(
    project_dir: Path, material: Any, supersession: dict[str, Any] | None
) -> bool:
    artifact = material.artifact
    revision = artifact["revision"]
    common = {
        "project_id": artifact["project_id"],
        "promotion_id": artifact["promotion_id"],
        "candidate_id": artifact["candidate_id"],
        "revision": artifact["assigned_revision"],
        "idempotency_key": artifact["idempotency_key"],
        "operation_identity": artifact["preparation_id"],
        "created_at": artifact["artifact_created_at"],
    }
    started_content = {
        "preparation_id": artifact["preparation_id"],
        "preparation_path": artifact["preparation_path"],
        "preparation_artifact_hash": material.artifact_hash,
        "preparation_artifact_size": len(material.artifact_bytes),
        "preparation_scope_hash": artifact["preparation_scope_hash"],
        "canonical_request_body_hash": artifact["canonical_request_body_hash"],
        "expected_latest_revision": artifact["prior_lineage_expectations"]["expected_latest_revision"],
        "expected_latest_draft_scope_hash": artifact["prior_lineage_expectations"]["expected_latest_draft_scope_hash"],
        "assigned_revision": artifact["assigned_revision"],
        "planned_draft_scope_hash": artifact["draft_scope_hash"],
        "revision_path": artifact["revision_path"],
        "revision_canonical_hash": artifact["revision_canonical_hash"],
        "revision_canonical_size": artifact["revision_canonical_size"],
        "approved_record_hash": artifact["approved_record_hash"],
        "approved_record_size": artifact["approved_record_size"],
        "authoritative_owner_actor": revision["prepared_by"],
        "supersession_kind": artifact["supersession_kind"],
    }
    started = append_event(project_dir, event_type="draft_preparation_started", content=started_content, **common)
    prepared_content = {
        "preparation_id": artifact["preparation_id"],
        "preparation_path": artifact["preparation_path"],
        "preparation_artifact_hash": material.artifact_hash,
        "preparation_start_event_id": started.event["event_id"],
        "preparation_scope_hash": artifact["preparation_scope_hash"],
        "revision_path": artifact["revision_path"],
        "revision_canonical_hash": artifact["revision_canonical_hash"],
        "revision_canonical_size": artifact["revision_canonical_size"],
        "draft_scope_hash": artifact["draft_scope_hash"],
        "approved_record_hash": artifact["approved_record_hash"],
        "approved_record_size": artifact["approved_record_size"],
    }
    prepared = append_event(project_dir, event_type="draft_prepared", content=prepared_content, **common)
    superseded_replayed = True
    if artifact["supersession_kind"] == "draft":
        content = {
            "preparation_id": artifact["preparation_id"],
            "preparation_scope_hash": artifact["preparation_scope_hash"],
            "superseded_revision": supersession["superseded_revision"],
            "superseding_revision": artifact["assigned_revision"],
            "superseded_draft_scope_hash": supersession["superseded_draft_scope_hash"],
            "superseding_draft_scope_hash": artifact["draft_scope_hash"],
            "authoritative_owner_actor": revision["prepared_by"],
            "rationale": supersession["rationale"],
        }
        superseded_replayed = append_event(project_dir, event_type="draft_superseded", content=content, **common).replayed
    elif artifact["supersession_kind"] == "sealed":
        content = {
            "preparation_id": artifact["preparation_id"],
            "preparation_scope_hash": artifact["preparation_scope_hash"],
            "superseded_revision": supersession["superseded_revision"],
            "superseding_revision": artifact["assigned_revision"],
            "sealed_contract_hash": supersession["sealed_contract_hash"],
            "superseding_draft_scope_hash": artifact["draft_scope_hash"],
            "authoritative_owner_actor": revision["prepared_by"],
            "rationale": supersession["rationale"],
        }
        superseded_replayed = append_event(project_dir, event_type="contract_superseded", content=content, **common).replayed
    return started.replayed and prepared.replayed and superseded_replayed


def _preparation_response(material: Any, *, replayed: bool, recovered: bool) -> dict[str, Any]:
    artifact = material.artifact
    return {
        "preparation_id": artifact["preparation_id"],
        "preparation_path": artifact["preparation_path"],
        "revision": artifact["assigned_revision"],
        "revision_path": artifact["revision_path"],
        "revision_canonical_hash": artifact["revision_canonical_hash"],
        "revision_canonical_size": artifact["revision_canonical_size"],
        "draft_scope_hash": artifact["draft_scope_hash"],
        "approved_record_hash": artifact["approved_record_hash"],
        "approved_record_size": artifact["approved_record_size"],
        "lineage_state": "draft_active",
        "recovery_status": "recovered" if recovered else "complete",
        "replayed": replayed,
    }


def prepare_apply_contract(
    *, project_dir: Path, project_id: str, promotion_id: str, promotion: dict[str, Any],
    candidate: dict[str, Any], owner: dict[str, Any], body: Any
) -> tuple[dict[str, Any], int]:
    request = _closed_prepare_request(body)
    body_without_key = {key: value for key, value in request.items() if key != "idempotency_key"}
    request_hash = canonical_sha256(body_without_key)
    scope_hash = preparation_scope_hash(
        project_id=project_id,
        promotion_id=promotion_id,
        requested_operation=request["operation"],
        approved_destination_type=request["approved_destination_type"],
        destination_key=request["destination_key"],
        canonical_request_body_hash=request_hash,
        expected_latest_revision=request["expected_latest_revision"],
        expected_latest_draft_scope_hash=request["expected_latest_draft_scope_hash"],
    )
    prep_path = _contract_dir(project_dir, promotion_id) / "preparations" / f"{preparation_id(project_id, promotion_id, request['idempotency_key'])}.json"
    if prep_path.exists() or prep_path.is_symlink():
        material = load_preparation_artifact(
            project_dir, project_id=project_id, promotion_id=promotion_id, idempotency_key=request["idempotency_key"]
        )
        candidate_id = material.artifact["candidate_id"]
        if material.artifact["preparation_scope_hash"] != scope_hash:
            raise ApplyContractError("APPLY_CONTRACT_PREPARATION_SCOPE_CONFLICT")
        publish_revision_from_preparation(project_dir, material)
        events_replayed = _append_preparation_events(project_dir, material, request["supersession"])
        lineage = derive_apply_contract_lineage(
            project_dir=project_dir, project_id=project_id, promotion_id=promotion_id, candidate_id=candidate_id
        )
        if lineage["state"] != "draft_active" or lineage["latest_draft_scope_hash"] != material.artifact["draft_scope_hash"]:
            raise ApplyContractError("APPLY_CONTRACT_PREPARATION_PUBLICATION_INCOMPLETE")
        return _preparation_response(material, replayed=True, recovered=not events_replayed), 200

    candidate_id, snapshot = _association(
        project_id=project_id, promotion_id=promotion_id, promotion=promotion, candidate=candidate
    )
    if not owner:
        owner = load_local_owner_identity(project_dir, project_id=project_id)
    lineage = derive_apply_contract_lineage(
        project_dir=project_dir, project_id=project_id, promotion_id=promotion_id, candidate_id=candidate_id
    )
    if _incomplete_preparations(project_dir, promotion_id, lineage["events"]):
        raise ApplyContractError("APPLY_CONTRACT_PREPARATION_INCOMPLETE")
    if lineage["state"] in {"preparation_events_incomplete", "recovery_required", "applied"}:
        raise ApplyContractError("APPLY_CONTRACT_LINEAGE_BLOCKED")
    if (
        request["expected_latest_revision"] != lineage["latest_revision"]
        or request["expected_latest_draft_scope_hash"] != lineage["latest_draft_scope_hash"]
    ):
        raise ApplyContractError("APPLY_CONTRACT_LINEAGE_EXPECTATION_MISMATCH")
    supersession = request["supersession"]
    if lineage["state"] in {"no_contract", "revoked"}:
        if supersession is not None:
            raise ApplyContractError("APPLY_CONTRACT_SUPERSESSION_INVALID")
    elif lineage["state"] == "draft_active":
        if not isinstance(supersession, dict) or supersession.get("kind") != "draft" or supersession["superseded_revision"] != lineage["latest_revision"] or supersession["superseded_draft_scope_hash"] != lineage["latest_draft_scope_hash"]:
            raise ApplyContractError("APPLY_CONTRACT_SUPERSESSION_REQUIRED")
    elif lineage["state"] == "sealed_active":
        if not isinstance(supersession, dict) or supersession.get("kind") != "sealed" or supersession["superseded_revision"] != lineage["active_sealed_revision"] or supersession["sealed_contract_hash"] != lineage["active_sealed_contract_hash"]:
            raise ApplyContractError("APPLY_CONTRACT_SUPERSESSION_REQUIRED")
        active = lineage["seals"][lineage["active_sealed_revision"]]["revision"]
        if active["destination"]["approved_destination_type"] != request["approved_destination_type"] or active["destination"]["destination_key"] != request["destination_key"]:
            raise ApplyContractError("NEW_PROMOTION_REQUIRED")

    prepared_at = _now()
    before = _before_state(
        project_dir, request["approved_destination_type"], request["destination_key"], observed_at=prepared_at
    )
    before_record = before["content"]
    version = 1 if before_record is None else before_record["record_version"] + 1
    evidence, provenance, locators = _normalized_authority_refs(
        project_id=project_id, promotion_id=promotion_id, candidate_id=candidate_id, promotion=promotion, snapshot=snapshot
    )
    duplicate, dependency = _stamp_decisions(
        duplicate=request["duplicate_resolution"], dependency=request["dependency_resolution"],
        owner=owner, decided_at=prepared_at, operation=request["operation"],
        evidence_ids={item["ref_id"] for item in evidence},
        provenance_ids={item["provenance_id"] for item in provenance},
    )
    approved = build_approved_record(
        record_version=version,
        project_id=project_id,
        destination_type=request["approved_destination_type"],
        destination_key=request["destination_key"],
        source_candidate_id=candidate_id,
        source_promotion_id=promotion_id,
        source_candidate_snapshot_hash=canonical_sha256(snapshot),
        payload=request["payload"],
        evidence_refs=evidence,
        provenance_refs=provenance,
        source_locators=locators,
        owner_note=request.get("owner_note"),
    )
    validate_record_operation(request["operation"], approved.record, before_record=before_record)
    number = 1 if lineage["latest_revision"] is None else lineage["latest_revision"] + 1
    revision = build_revision(
        project_id=project_id,
        promotion_id=promotion_id,
        candidate_id=candidate_id,
        revision=number,
        supersedes_revision=lineage["latest_revision"],
        prepared_by=owner,
        prepared_at=prepared_at,
        operation=request["operation"],
        destination={
            "approved_destination_type": request["approved_destination_type"],
            "destination_key": request["destination_key"],
            "destination_path": approved_record_relative_path(request["approved_destination_type"], request["destination_key"]).as_posix(),
        },
        source_candidate_snapshot_hash=canonical_sha256(snapshot),
        evidence_refs=evidence,
        provenance_refs=provenance,
        source_locators=locators,
        proposed_approved_record=approved.record,
        approved_record_hash=approved.approved_record_hash,
        approved_record_size=approved.approved_record_size,
        duplicate_resolution=duplicate,
        dependency_resolution=dependency,
        before_state=before,
    )
    if (
        revision["dependency_resolution"]["state"] == "satisfied"
        and _dependency_truth_blockers(project_dir, revision)
    ):
        raise ApplyContractError("APPLY_CONTRACT_DEPENDENCY_REFERENCE_INVALID")
    if (
        revision["duplicate_resolution"]["state"] != "unresolved"
        and _duplicate_truth_blockers(project_dir, revision)
    ):
        raise ApplyContractError("APPLY_CONTRACT_DUPLICATE_REFERENCE_INVALID")
    expectations = {
        "expected_state": lineage["state"],
        "expected_latest_revision": lineage["latest_revision"],
        "expected_latest_draft_scope_hash": lineage["latest_draft_scope_hash"],
        "expected_active_sealed_revision": lineage["active_sealed_revision"],
        "expected_active_sealed_contract_hash": lineage["active_sealed_contract_hash"],
    }
    material = build_preparation_artifact(
        project_id=project_id,
        promotion_id=promotion_id,
        candidate_id=candidate_id,
        idempotency_key=request["idempotency_key"],
        preparation_scope_hash_value=scope_hash,
        canonical_request_body_hash=request_hash,
        prior_lineage_expectations=expectations,
        supersession_kind="none" if supersession is None else supersession["kind"],
        revision=revision,
        artifact_created_at=prepared_at,
    )
    publish_preparation_artifact(project_dir, material)
    publish_revision_from_preparation(project_dir, material)
    _append_preparation_events(project_dir, material, supersession)
    completed = derive_apply_contract_lineage(
        project_dir=project_dir, project_id=project_id, promotion_id=promotion_id, candidate_id=candidate_id
    )
    if completed["state"] != "draft_active" or completed["latest_revision"] != number:
        raise ApplyContractError("APPLY_CONTRACT_PREPARATION_PUBLICATION_INCOMPLETE")
    return _preparation_response(material, replayed=False, recovered=False), 201


def _decision_blockers(revision: dict[str, Any]) -> list[dict[str, str]]:
    blockers: list[dict[str, str]] = []
    duplicate_state = revision["duplicate_resolution"]["state"]
    allowed_duplicate = (
        {"distinct_record"}
        if revision["operation"] == "create"
        else {"update_existing", "merge_into_existing"}
    )
    if duplicate_state not in allowed_duplicate:
        blockers.append({"code": "DUPLICATE_DECISION_BLOCKS_APPLY", "field": "duplicate_resolution"})
    dependency = revision["dependency_resolution"]
    if dependency["state"] not in {"none_declared", "satisfied"}:
        blockers.append({"code": "DEPENDENCY_DECISION_BLOCKS_APPLY", "field": "dependency_resolution"})
    if any(item["required"] and item["status"] != "satisfied" for item in dependency["dependencies"]):
        blockers.append({"code": "REQUIRED_DEPENDENCY_UNSATISFIED", "field": "dependency_resolution.dependencies"})
    return blockers


def _dependency_truth_blockers(
    project_dir: Path, revision: dict[str, Any]
) -> list[dict[str, str]]:
    blockers: list[dict[str, str]] = []
    for dependency in revision["dependency_resolution"]["dependencies"]:
        target = dependency["target"]
        if target is None:
            continue
        current, _, _ = _safe_current_record(
            project_dir,
            target["destination_type"],
            target["destination_key"],
            ordinary=False,
        )
        matches = (
            current is not None
            and current["record_version"] == target["record_version"]
            and canonical_sha256(current) == target["content_hash"]
        )
        if not matches:
            blockers.append(
                {
                    "code": "DEPENDENCY_TARGET_CHANGED_OR_MISSING",
                    "field": f"dependency_resolution.dependencies.{dependency['dependency_id']}",
                }
            )
    return blockers


def _duplicate_truth_blockers(
    project_dir: Path, revision: dict[str, Any]
) -> list[dict[str, str]]:
    blockers: list[dict[str, str]] = []
    for reference in revision["duplicate_resolution"]["reviewed_approved_records"]:
        current, _, _ = _safe_current_record(
            project_dir,
            reference["destination_type"],
            reference["destination_key"],
            ordinary=False,
        )
        if (
            current is None
            or current["record_version"] != reference["record_version"]
            or canonical_sha256(current) != reference["content_hash"]
        ):
            blockers.append(
                {
                    "code": "DUPLICATE_REVIEW_TARGET_CHANGED_OR_MISSING",
                    "field": "duplicate_resolution.reviewed_approved_records",
                }
            )
    return blockers


def _closed_approval_request(body: Any) -> dict[str, Any]:
    request = require_closed_object(
        body,
        required={
            "idempotency_key", "expected_latest_revision", "expected_latest_draft_scope_hash",
            "before_state_snapshot_token", "confirmed", "approval_method",
        },
        label="approval request",
    )
    validate_uuid_v4(request["idempotency_key"])
    require_integer(request["expected_latest_revision"], label="expected_latest_revision", minimum=1, maximum=256)
    validate_sha256(request["expected_latest_draft_scope_hash"], "expected_latest_draft_scope_hash")
    validate_sha256(request["before_state_snapshot_token"], "before_state_snapshot_token")
    if request["confirmed"] is not True or request["approval_method"] != "explicit_apply_contract_approval":
        raise ApplyContractError("APPLY_CONTRACT_EXPLICIT_APPROVAL_REQUIRED")
    return request


def approve_apply_contract(
    *, project_dir: Path, project_id: str, promotion_id: str, promotion: dict[str, Any],
    candidate: dict[str, Any], owner: dict[str, Any], revision_number: int, body: Any
) -> tuple[dict[str, Any], int]:
    request = _closed_approval_request(body)
    require_integer(revision_number, label="revision", minimum=1, maximum=256)
    operation_identity = f"approval_{canonical_sha256({'project_id': project_id, 'promotion_id': promotion_id, 'revision': revision_number, 'idempotency_key': request['idempotency_key']})}"
    raw_chain = scan_event_chain(
        project_dir, project_id=project_id, promotion_id=promotion_id
    )
    recorded_replay = [
        event for event in raw_chain.events
        if event["event_type"] == "contract_approval_recorded"
        and event["operation_identity"] == operation_identity
        and event["idempotency_key"] == request["idempotency_key"]
    ]
    if recorded_replay:
        candidate_id = recorded_replay[0]["candidate_id"]
    else:
        candidate_id, _ = _association(
            project_id=project_id, promotion_id=promotion_id, promotion=promotion, candidate=candidate
        )
        if not owner:
            owner = load_local_owner_identity(project_dir, project_id=project_id)
    lineage = derive_apply_contract_lineage(
        project_dir=project_dir, project_id=project_id, promotion_id=promotion_id, candidate_id=candidate_id
    )
    if revision_number != lineage["latest_revision"] or revision_number > len(lineage["revisions"]):
        raise ApplyContractError("APPLY_CONTRACT_DRAFT_NOT_ACTIVE")
    revision = lineage["revisions"][revision_number - 1]
    if (
        request["expected_latest_revision"] != revision_number
        or request["expected_latest_draft_scope_hash"] != revision["draft_scope_hash"]
        or request["before_state_snapshot_token"] != revision["before_state"]["snapshot_token"]
    ):
        raise ApplyContractError("APPLY_CONTRACT_APPROVAL_MISMATCH")
    existing = [
        event for event in lineage["events"]
        if event["event_type"] == "contract_approval_recorded"
        and event["operation_identity"] == operation_identity
        and event["idempotency_key"] == request["idempotency_key"]
    ]
    approval_owner = existing[0]["contract_approval"]["owner_actor"] if existing else owner
    if not existing:
        if lineage["state"] != "draft_active":
            code = (
                "APPROVAL_PUBLICATION_INCOMPLETE"
                if lineage["state"] == "approval_publication_incomplete"
                else "APPLY_CONTRACT_DRAFT_NOT_ACTIVE"
            )
            raise ApplyContractError(code)
        if owner != revision["prepared_by"]:
            raise ApplyContractError("OWNER_IDENTITY_CHANGED")
        current = _before_state(
            project_dir,
            revision["destination"]["approved_destination_type"],
            revision["destination"]["destination_key"],
            observed_at=_now(),
        )
        if current["snapshot_token"] != revision["before_state"]["snapshot_token"]:
            raise ApplyContractError("APPLY_CONTRACT_BEFORE_STATE_CHANGED")
        blockers = (
            _decision_blockers(revision)
            + _dependency_truth_blockers(project_dir, revision)
            + _duplicate_truth_blockers(project_dir, revision)
        )
        if blockers:
            raise ApplyContractError(blockers[0]["code"])
    approval_scope = canonical_sha256(
        {
            "operation_kind": "approve",
            "project_id": project_id,
            "promotion_id": promotion_id,
            "revision": revision_number,
            "draft_scope_hash": revision["draft_scope_hash"],
            "before_state_snapshot_token": revision["before_state"]["snapshot_token"],
            "authoritative_owner_actor": approval_owner,
            "approval_method": request["approval_method"],
        }
    )
    if existing:
        if existing[0]["approval_scope_hash"] != approval_scope:
            raise ApplyContractError("APPLY_EVENT_IDEMPOTENCY_SCOPE_CONFLICT")
        approval = existing[0]["contract_approval"]
        approved_at = existing[0]["created_at"]
    else:
        approved_at = _now()
        approval = {
            "owner_actor": approval_owner,
            "project_id": project_id,
            "promotion_id": promotion_id,
            "revision": revision_number,
            "draft_scope_hash": revision["draft_scope_hash"],
            "before_state_snapshot_token": revision["before_state"]["snapshot_token"],
            "approval_method": request["approval_method"],
            "approved_at": approved_at,
        }
    common = {
        "project_id": project_id,
        "promotion_id": promotion_id,
        "candidate_id": candidate_id,
        "revision": revision_number,
        "idempotency_key": request["idempotency_key"],
        "operation_identity": operation_identity,
        "created_at": approved_at,
    }
    recorded = append_event(
        project_dir,
        event_type="contract_approval_recorded",
        content={
            "approval_scope_hash": approval_scope,
            "draft_scope_hash": revision["draft_scope_hash"],
            "contract_approval": approval,
        },
        **common,
    )
    sealed = build_sealed_revision(revision, approval, recorded.event["event_id"])
    sealed_relative = sealed_revision_relative_path(promotion_id, revision_number)
    sealed_replayed = publish_immutable_file(
        project_dir,
        sealed_relative,
        canonical_json_bytes(sealed, max_bytes=MAX_SEALED_REVISION_BYTES),
        conflict_code="APPLY_CONTRACT_SEALED_REVISION_CONFLICT",
    )
    approved_event = append_event(
        project_dir,
        event_type="contract_approved",
        content={
            "draft_scope_hash": revision["draft_scope_hash"],
            "sealed_contract_hash": sealed["sealed_contract_hash"],
            "approval_event_id": recorded.event["event_id"],
            "sealed_revision_path": sealed_relative.as_posix(),
        },
        **common,
    )
    response = {
        "revision": revision_number,
        "draft_scope_hash": revision["draft_scope_hash"],
        "sealed_contract_hash": sealed["sealed_contract_hash"],
        "sealed_revision_path": sealed_relative.as_posix(),
        "approval_event_id": recorded.event["event_id"],
        "seal_event_id": approved_event.event["event_id"],
        "lineage_state": "sealed_active",
        "replayed": recorded.replayed and sealed_replayed and approved_event.replayed,
    }
    return response, 200 if response["replayed"] else 201


def _closed_revocation_request(body: Any) -> dict[str, Any]:
    request = require_closed_object(
        body,
        required={"idempotency_key", "revision", "sealed_contract_hash", "rationale", "confirmed", "method"},
        label="revocation request",
    )
    validate_uuid_v4(request["idempotency_key"])
    require_integer(request["revision"], label="revision", minimum=1, maximum=256)
    validate_sha256(request["sealed_contract_hash"], "sealed_contract_hash")
    require_string(request["rationale"], label="rationale", minimum=1, maximum=4096)
    if request["confirmed"] is not True or request["method"] != "explicit_contract_revocation":
        raise ApplyContractError("APPLY_CONTRACT_EXPLICIT_REVOCATION_REQUIRED")
    return request


def revoke_apply_contract(
    *, project_dir: Path, project_id: str, promotion_id: str, promotion: dict[str, Any],
    candidate: dict[str, Any], owner: dict[str, Any], revision_number: int, body: Any
) -> tuple[dict[str, Any], int]:
    request = _closed_revocation_request(body)
    candidate_id, _ = _association(
        project_id=project_id, promotion_id=promotion_id, promotion=promotion, candidate=candidate
    )
    if request["revision"] != revision_number:
        raise ApplyContractError("APPLY_CONTRACT_REVOCATION_MISMATCH")
    lineage = derive_apply_contract_lineage(
        project_dir=project_dir, project_id=project_id, promotion_id=promotion_id, candidate_id=candidate_id
    )
    replay = [
        event for event in lineage["events"]
        if event["event_type"] == "contract_revoked"
        and event["revision"] == revision_number
        and event["idempotency_key"] == request["idempotency_key"]
    ]
    if replay:
        event = replay[0]
        if (
            event["sealed_contract_hash"] != request["sealed_contract_hash"]
            or event["rationale"] != request["rationale"]
        ):
            raise ApplyContractError("APPLY_EVENT_IDEMPOTENCY_SCOPE_CONFLICT")
        return {
            "revision": revision_number,
            "sealed_contract_hash": request["sealed_contract_hash"],
            "revocation_event_id": event["event_id"],
            "lineage_state": "revoked",
            "replayed": True,
        }, 200
    if not owner:
        owner = load_local_owner_identity(project_dir, project_id=project_id)
    if (
        lineage["state"] != "sealed_active"
        or lineage["active_sealed_revision"] != revision_number
        or lineage["active_sealed_contract_hash"] != request["sealed_contract_hash"]
    ):
        raise ApplyContractError("APPLY_CONTRACT_SEAL_NOT_ACTIVE")
    sealed = lineage["seals"][revision_number]
    if owner != sealed["contract_approval"]["owner_actor"]:
        raise ApplyContractError("OWNER_IDENTITY_CHANGED")
    revocation_scope = canonical_sha256(
        {
            "operation_kind": "revoke",
            "project_id": project_id,
            "promotion_id": promotion_id,
            "revision": revision_number,
            "sealed_contract_hash": request["sealed_contract_hash"],
            "authoritative_owner_actor": owner,
            "method": request["method"],
            "rationale_hash": canonical_sha256(request["rationale"]),
        }
    )
    operation_identity = f"revocation_{canonical_sha256({'scope': revocation_scope, 'key': request['idempotency_key']})}"
    created_at = _now()
    publication = append_event(
        project_dir,
        event_type="contract_revoked",
        project_id=project_id,
        promotion_id=promotion_id,
        candidate_id=candidate_id,
        revision=revision_number,
        idempotency_key=request["idempotency_key"],
        operation_identity=operation_identity,
        created_at=created_at,
        content={
            "sealed_contract_hash": request["sealed_contract_hash"],
            "authoritative_owner_actor": owner,
            "rationale": request["rationale"],
        },
    )
    return {
        "revision": revision_number,
        "sealed_contract_hash": request["sealed_contract_hash"],
        "revocation_event_id": publication.event["event_id"],
        "lineage_state": "revoked",
        "replayed": publication.replayed,
    }, 200 if publication.replayed else 201


def _closed_challenge_request(body: Any) -> dict[str, Any]:
    request = require_closed_object(
        body,
        required={"revision", "sealed_contract_hash", "before_state_snapshot_token", "idempotency_key"},
        label="final challenge request",
    )
    require_integer(request["revision"], label="revision", minimum=1, maximum=256)
    validate_sha256(request["sealed_contract_hash"], "sealed_contract_hash")
    validate_sha256(request["before_state_snapshot_token"], "before_state_snapshot_token")
    validate_uuid_v4(request["idempotency_key"])
    return request


def issue_final_challenge(
    *, project_dir: Path, project_id: str, promotion_id: str, promotion: dict[str, Any],
    candidate: dict[str, Any], owner: dict[str, Any], body: Any,
    registry: FinalChallengeRegistry
) -> tuple[dict[str, Any], int]:
    request = _closed_challenge_request(body)
    candidate_id, _ = _association(
        project_id=project_id, promotion_id=promotion_id, promotion=promotion, candidate=candidate
    )
    lineage = derive_apply_contract_lineage(
        project_dir=project_dir, project_id=project_id, promotion_id=promotion_id, candidate_id=candidate_id
    )
    if (
        lineage["state"] != "sealed_active"
        or lineage["active_sealed_revision"] != request["revision"]
        or lineage["active_sealed_contract_hash"] != request["sealed_contract_hash"]
    ):
        raise ApplyContractError("APPLY_CONTRACT_SEAL_NOT_ACTIVE")
    sealed = lineage["seals"][request["revision"]]
    revision = sealed["revision"]
    if owner != sealed["contract_approval"]["owner_actor"] or owner != revision["prepared_by"]:
        raise ApplyContractError("OWNER_IDENTITY_CHANGED")
    current = _before_state(
        project_dir,
        revision["destination"]["approved_destination_type"],
        revision["destination"]["destination_key"],
        observed_at=_now(),
    )
    if (
        request["before_state_snapshot_token"] != revision["before_state"]["snapshot_token"]
        or current["snapshot_token"] != revision["before_state"]["snapshot_token"]
    ):
        raise ApplyContractError("APPLY_CONTRACT_BEFORE_STATE_CHANGED")
    blockers = (
        _decision_blockers(revision)
        + _dependency_truth_blockers(project_dir, revision)
        + _duplicate_truth_blockers(project_dir, revision)
    )
    if blockers:
        raise ApplyContractError(blockers[0]["code"])
    response = registry.issue(
        project_id=project_id,
        promotion_id=promotion_id,
        revision=request["revision"],
        sealed_contract_hash=request["sealed_contract_hash"],
        before_state_snapshot_token=request["before_state_snapshot_token"],
        operation=revision["operation"],
        destination_path=revision["destination"]["destination_path"],
        authoritative_owner_actor=owner,
        idempotency_key=request["idempotency_key"],
    )
    return response, 200 if response["replayed"] else 201


def read_apply_contract(
    *, project_dir: Path, project_id: str, promotion_id: str, promotion: dict[str, Any],
    candidate: dict[str, Any], owner: dict[str, Any], selected_revision: int | None
) -> dict[str, Any]:
    candidate_id, snapshot = _association(
        project_id=project_id, promotion_id=promotion_id, promotion=promotion, candidate=candidate
    )
    lineage = derive_apply_contract_lineage(
        project_dir=project_dir, project_id=project_id, promotion_id=promotion_id, candidate_id=candidate_id
    )
    if selected_revision is not None:
        require_integer(selected_revision, label="revision", minimum=1, maximum=256)
        if selected_revision > len(lineage["revisions"]):
            raise ApplyContractError("APPLY_CONTRACT_REVISION_NOT_FOUND")
        selected = lineage["revisions"][selected_revision - 1]
    else:
        selected = lineage["revisions"][-1] if lineage["revisions"] else None
    sealed = None if selected is None else lineage["seals"].get(selected["revision"])
    if selected is None:
        current_before = None
        blockers = [{"code": "APPLY_CONTRACT_NOT_PREPARED", "field": "lineage"}]
    else:
        current_before = _before_state(
            project_dir,
            selected["destination"]["approved_destination_type"],
            selected["destination"]["destination_key"],
            observed_at=_now(),
        )
        blockers = (
            _decision_blockers(selected)
            + _dependency_truth_blockers(project_dir, selected)
            + _duplicate_truth_blockers(project_dir, selected)
        )
        if current_before["snapshot_token"] != selected["before_state"]["snapshot_token"]:
            blockers.append({"code": "APPLY_CONTRACT_BEFORE_STATE_CHANGED", "field": "before_state"})
        if owner != selected["prepared_by"]:
            blockers.append({"code": "OWNER_IDENTITY_CHANGED", "field": "authoritative_owner"})
    evidence, provenance, locators = _normalized_authority_refs(
        project_id=project_id, promotion_id=promotion_id, candidate_id=candidate_id,
        promotion=promotion, snapshot=snapshot,
    )
    public_lineage = {
        key: value for key, value in lineage.items()
        if key not in {"revisions", "seals", "events"}
    }
    public_lineage.update(
        {
            "project_id": project_id,
            "promotion_id": promotion_id,
            "candidate_id": candidate_id,
            "revision_count": len(lineage["revisions"]),
            "event_count": len(lineage["events"]),
            "authority": {
                "source_candidate_snapshot_hash": canonical_sha256(snapshot),
                "evidence_refs": evidence,
                "provenance_refs": provenance,
                "source_locators": locators,
            },
        }
    )
    return {
        "lineage": public_lineage,
        "selected_revision": selected,
        "sealed_revision": sealed,
        "authoritative_owner": owner,
        "current_before_state": current_before,
        "revalidation": {
            "promotion_association_valid": True,
            "owner_matches_revision": selected is None or owner == selected["prepared_by"],
            "before_state_matches_revision": selected is None or current_before["snapshot_token"] == selected["before_state"]["snapshot_token"],
            "eligible_for_final_challenge": bool(selected and sealed and not blockers and lineage["state"] == "sealed_active"),
        },
        "blockers": blockers,
    }


def _safe_legacy_audit_entries(
    project_dir: Path, *, project_id: str, promotion_id: str, candidate_id: str
) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for relative_root in (
        Path("writer_assistant", "promotion_audit"),
        Path("writer_assistant", "promotion_audits"),
    ):
        root = project_dir / relative_root
        if not root.exists():
            continue
        metadata = os.lstat(root)
        if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
            raise ApplyContractError("LEGACY_AUDIT_UNSAFE_PATH")
        for path in sorted(root.iterdir(), key=lambda item: os.fsencode(item.name)):
            if path.is_dir() and not path.is_symlink():
                continue
            metadata = os.lstat(path)
            if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1 or metadata.st_size > 1_048_576:
                raise ApplyContractError("LEGACY_AUDIT_UNSAFE_PATH")
            try:
                raw = path.read_bytes()
                value = strict_json_loads(raw, max_bytes=1_048_576)
            except ApplyContractError as exc:
                raise ApplyContractError("LEGACY_AUDIT_INVALID") from exc
            if not isinstance(value, dict):
                raise ApplyContractError("LEGACY_AUDIT_INVALID")
            validation = validate_promotion_audit_record(value)
            if validation.get("validation_status") != "valid":
                raise ApplyContractError("LEGACY_AUDIT_INVALID")
            validated = validation["record"]
            associated = (
                value.get("promotion_id") == promotion_id
                or (
                    validated.get("project_id") == project_id
                    and validated.get("candidate_id") == candidate_id
                )
            )
            if not associated:
                continue
            entries.append(
                {
                    "source_kind": "legacy_event",
                    "source_path": path.relative_to(project_dir).as_posix(),
                    "source_hash": hashlib.sha256(raw).hexdigest(),
                    "event": validated,
                }
            )
    return sorted(
        entries,
        key=lambda entry: (
            entry["event"].get("applied_at") or entry["event"].get("created_at") or "",
            entry["source_path"],
            entry["source_hash"],
        ),
    )


def read_apply_audit(
    *, project_dir: Path, project_id: str, promotion_id: str, promotion: dict[str, Any],
    candidate: dict[str, Any]
) -> dict[str, Any]:
    candidate_id, _ = _association(
        project_id=project_id, promotion_id=promotion_id, promotion=promotion, candidate=candidate
    )
    lineage = derive_apply_contract_lineage(
        project_dir=project_dir, project_id=project_id, promotion_id=promotion_id, candidate_id=candidate_id
    )
    legacy = _safe_legacy_audit_entries(
        project_dir,
        project_id=project_id,
        promotion_id=promotion_id,
        candidate_id=candidate_id,
    )
    v2 = [
        {"source_kind": "v2_event", "sequence": event["sequence"], "event": event}
        for event in lineage["events"]
    ]
    return {
        "project_id": project_id,
        "promotion_id": promotion_id,
        "candidate_id": candidate_id,
        "lineage_state": lineage["state"],
        "entries": legacy + v2,
        "conflicts": [],
    }


_FINAL_CHALLENGE_ID_RE = re.compile(
    r"^challenge_[a-f0-9]{16}_[a-f0-9]{64}$"
)


def _closed_final_apply_request(body: Any, *, promotion_id: str) -> dict[str, Any]:
    request = require_closed_object(
        body,
        required={
            "promotion_id", "revision", "sealed_contract_hash",
            "before_state_snapshot_token", "challenge_id", "challenge_response",
            "final_confirmation", "idempotency_key",
        },
        label="final apply request",
    )
    if validate_safe_id(request["promotion_id"], "promotion_id") != promotion_id:
        raise ApplyContractError("PROMOTION_ASSOCIATION_INVALID")
    require_integer(request["revision"], label="revision", minimum=1, maximum=256)
    validate_sha256(request["sealed_contract_hash"], "sealed_contract_hash")
    validate_sha256(request["before_state_snapshot_token"], "before_state_snapshot_token")
    if not isinstance(request["challenge_id"], str) or not _FINAL_CHALLENGE_ID_RE.fullmatch(request["challenge_id"]):
        raise ApplyContractError("FINAL_CHALLENGE_UNKNOWN")
    validate_sha256(request["challenge_response"], "challenge_response")
    confirmation = require_closed_object(
        request["final_confirmation"],
        required={"confirmed", "method"},
        label="final confirmation",
    )
    if confirmation["confirmed"] is not True or confirmation["method"] != "explicit_final_apply_confirmation":
        raise ApplyContractError("FINAL_CONFIRMATION_REQUIRED")
    validate_uuid_v4(request["idempotency_key"])
    return request


def _final_apply_scope(
    *, project_id: str, promotion_id: str, revision: dict[str, Any],
    sealed_contract_hash: str, authoritative_owner_actor: dict[str, Any]
) -> dict[str, Any]:
    return {
        "operation_kind": "final_apply",
        "project_id": project_id,
        "promotion_id": promotion_id,
        "revision": revision["revision"],
        "sealed_contract_hash": sealed_contract_hash,
        "before_state_snapshot_token": revision["before_state"]["snapshot_token"],
        "operation": revision["operation"],
        "destination_type": revision["destination"]["approved_destination_type"],
        "destination_key": revision["destination"]["destination_key"],
        "destination_path": revision["destination"]["destination_path"],
        "approved_record_hash": revision["approved_record_hash"],
        "approved_record_size": revision["approved_record_size"],
        "authoritative_owner_actor": authoritative_owner_actor,
        "final_confirmation_method": "explicit_final_apply_confirmation",
    }


def _apply_identity(
    *, project_id: str, promotion_id: str, idempotency_key: str
) -> str:
    digest = canonical_sha256(
        {
            "protocol": "apply-promotion-operation-id.v1",
            "project_id": project_id,
            "promotion_id": promotion_id,
            "idempotency_key": idempotency_key,
        }
    )
    return f"apply_{digest[:32]}"


def _intent_events_for_key(
    events: list[dict[str, Any]], idempotency_key: str
) -> list[dict[str, Any]]:
    return [
        event for event in events
        if event["event_type"] == "apply_intent"
        and event["idempotency_key"] == idempotency_key
    ]


def _event_for_apply(
    events: list[dict[str, Any]], event_type: str, apply_id: str
) -> list[dict[str, Any]]:
    return [
        event for event in events
        if event["event_type"] == event_type and event.get("apply_id") == apply_id
    ]


def _validate_intent_contract(
    intent: dict[str, Any], sealed: dict[str, Any], seal_event: dict[str, Any]
) -> None:
    revision = sealed["revision"]
    expected = {
        "revision": revision["revision"],
        "sealed_contract_hash": sealed["sealed_contract_hash"],
        "operation": revision["operation"],
        "destination_type": revision["destination"]["approved_destination_type"],
        "destination_key": revision["destination"]["destination_key"],
        "destination_path": revision["destination"]["destination_path"],
        "before_state_snapshot_token": revision["before_state"]["snapshot_token"],
        "before_state_version": revision["before_state"]["record_version"],
        "before_state_content_hash": revision["before_state"]["content_hash"],
        "approved_record_hash": revision["approved_record_hash"],
        "approved_record_size": revision["approved_record_size"],
        "sealed_revision_path": sealed_revision_relative_path(
            revision["promotion_id"], revision["revision"]
        ).as_posix(),
        "approval_event_id": sealed["approval_event_id"],
        "seal_event_id": seal_event["event_id"],
        "authoritative_owner_actor": sealed["contract_approval"]["owner_actor"],
    }
    if any(intent[field] != value for field, value in expected.items()):
        raise ApplyContractError("APPLY_INTENT_SEALED_RECORD_MISMATCH")
    expected_scope = canonical_sha256(
        _final_apply_scope(
            project_id=revision["project_id"],
            promotion_id=revision["promotion_id"],
            revision=revision,
            sealed_contract_hash=sealed["sealed_contract_hash"],
            authoritative_owner_actor=intent["authoritative_owner_actor"],
        )
    )
    if intent["final_apply_scope_hash"] != expected_scope:
        raise ApplyContractError("APPLY_EVENT_IDEMPOTENCY_SCOPE_CONFLICT")


def _destination_observation(
    project_dir: Path, revision: dict[str, Any]
) -> dict[str, Any]:
    destination = revision["destination"]
    try:
        record, _, path = _safe_current_record(
            project_dir,
            destination["approved_destination_type"],
            destination["destination_key"],
        )
    except ApplyContractError:
        path = project_dir / destination["destination_path"]
        try:
            metadata = os.lstat(path)
            if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
                raise OSError
            raw = path.read_bytes()
            if not 1 <= len(raw) <= MAX_APPROVED_RECORD_BYTES:
                raise OSError
            return {
                "state": "unclassified",
                "record": None,
                "hash": hashlib.sha256(raw).hexdigest(),
                "size": len(raw),
                "version": None,
            }
        except OSError:
            return {
                "state": "unclassified",
                "record": None,
                "hash": None,
                "size": None,
                "version": None,
            }
    if record is None:
        return {"state": "absent", "record": None, "hash": None, "size": None, "version": None}
    material = approved_record_material(record)
    return {
        "state": "present",
        "record": record,
        "hash": material.approved_record_hash,
        "size": material.approved_record_size,
        "version": record["record_version"],
    }


def _observation_matches_before(observation: dict[str, Any], revision: dict[str, Any]) -> bool:
    before = revision["before_state"]
    if before["state"] == "absent":
        return observation["state"] == "absent"
    if observation["state"] != "present":
        return False
    expected = approved_record_material(before["content"])
    return (
        observation["hash"] == expected.approved_record_hash
        and observation["size"] == expected.approved_record_size
        and observation["version"] == expected.record["record_version"]
        and observation["record"] == expected.record
    )


def _observation_matches_after(observation: dict[str, Any], revision: dict[str, Any]) -> bool:
    if observation["state"] != "present":
        return False
    expected = approved_record_material(revision["proposed_approved_record"])
    return (
        observation["hash"] == expected.approved_record_hash
        and observation["size"] == expected.approved_record_size
        and observation["version"] == expected.record["record_version"]
        and observation["record"] == expected.record
    )


def _apply_response(
    *, intent: dict[str, Any], revision: dict[str, Any], replayed: bool
) -> dict[str, Any]:
    return {
        "apply_id": intent["apply_id"],
        "project_id": intent["project_id"],
        "promotion_id": intent["promotion_id"],
        "candidate_id": intent["candidate_id"],
        "revision": intent["revision"],
        "sealed_contract_hash": intent["sealed_contract_hash"],
        "destination_path": intent["destination_path"],
        "before_state_content_hash": intent["before_state_content_hash"],
        "approved_record_hash": intent["approved_record_hash"],
        "approved_record_size": intent["approved_record_size"],
        "approved_record_version": revision["proposed_approved_record"]["record_version"],
        "lineage_state": "applied",
        "replayed": replayed,
    }


def _publish_apply_completion(
    *, project_dir: Path, intent: dict[str, Any], revision: dict[str, Any],
    completed_at: str | None = None
) -> dict[str, Any]:
    completed_at = completed_at or _now()
    publication = append_event(
        project_dir,
        event_type="apply_completed",
        project_id=intent["project_id"],
        promotion_id=intent["promotion_id"],
        candidate_id=intent["candidate_id"],
        revision=intent["revision"],
        idempotency_key=intent["idempotency_key"],
        operation_identity=intent["apply_id"],
        created_at=completed_at,
        content={
            "apply_id": intent["apply_id"],
            "intent_event_id": intent["event_id"],
            "sealed_contract_hash": intent["sealed_contract_hash"],
            "destination_path": intent["destination_path"],
            "approved_record_hash": intent["approved_record_hash"],
            "approved_record_size": intent["approved_record_size"],
            "approved_record_version": revision["proposed_approved_record"]["record_version"],
            "completed_at": completed_at,
        },
    )
    return publication.event


def _validate_completion(
    completion: dict[str, Any], intent: dict[str, Any], revision: dict[str, Any]
) -> None:
    expected = {
        "intent_event_id": intent["event_id"],
        "revision": intent["revision"],
        "sealed_contract_hash": intent["sealed_contract_hash"],
        "destination_path": intent["destination_path"],
        "approved_record_hash": intent["approved_record_hash"],
        "approved_record_size": intent["approved_record_size"],
        "approved_record_version": revision["proposed_approved_record"]["record_version"],
    }
    if any(completion[field] != value for field, value in expected.items()):
        raise ApplyContractError("APPLY_COMPLETION_RECORD_MISMATCH")


def _recover_apply_intent(
    *, project_dir: Path, lineage: dict[str, Any], intent: dict[str, Any],
    sealed: dict[str, Any], seal_event: dict[str, Any]
) -> dict[str, Any]:
    revision = sealed["revision"]
    _validate_intent_contract(intent, sealed, seal_event)
    completions = _event_for_apply(lineage["events"], "apply_completed", intent["apply_id"])
    if len(completions) > 1:
        raise ApplyContractError("AMBIGUOUS_OR_CONFLICTING_HISTORY")
    observation = _destination_observation(project_dir, revision)
    if completions:
        _validate_completion(completions[0], intent, revision)
        if not _observation_matches_after(observation, revision):
            raise ApplyContractError("APPLY_COMPLETION_RECORD_MISMATCH")
        return _apply_response(intent=intent, revision=revision, replayed=True)

    recovery_completed = _event_for_apply(
        lineage["events"], "recovery_completed", intent["apply_id"]
    )
    if len(recovery_completed) > 1:
        raise ApplyContractError("AMBIGUOUS_OR_CONFLICTING_HISTORY")
    if recovery_completed:
        recovery = recovery_completed[0]
        if recovery["intent_event_id"] != intent["event_id"]:
            raise ApplyContractError("APPLY_EVENT_REFERENCE_MISSING_OR_CORRUPT")
        if recovery["outcome"] == "not_committed":
            if not _observation_matches_before(observation, revision):
                raise ApplyContractError("RECOVERY_REQUIRED")
            raise ApplyContractError("APPLY_FAILED_BEFORE_COMMIT")
        if (
            recovery["approved_record_hash"] != intent["approved_record_hash"]
            or recovery["approved_record_size"] != intent["approved_record_size"]
            or recovery["approved_record_version"]
            != revision["proposed_approved_record"]["record_version"]
            or not _observation_matches_after(observation, revision)
        ):
            raise ApplyContractError("APPLY_COMMITTED_RECORD_MISMATCH")
        _publish_apply_completion(
            project_dir=project_dir, intent=intent, revision=revision
        )
        return _apply_response(intent=intent, revision=revision, replayed=True)

    recovery_required = _event_for_apply(
        lineage["events"], "recovery_required", intent["apply_id"]
    )
    if len(recovery_required) > 1:
        raise ApplyContractError("AMBIGUOUS_OR_CONFLICTING_HISTORY")
    recovery_required_id = recovery_required[0]["event_id"] if recovery_required else None
    timestamp = _now()
    common = {
        "project_id": intent["project_id"],
        "promotion_id": intent["promotion_id"],
        "candidate_id": intent["candidate_id"],
        "revision": intent["revision"],
        "idempotency_key": intent["idempotency_key"],
        "operation_identity": intent["apply_id"],
        "created_at": timestamp,
    }
    if _observation_matches_after(observation, revision):
        append_event(
            project_dir,
            event_type="recovery_completed",
            content={
                "apply_id": intent["apply_id"],
                "intent_event_id": intent["event_id"],
                "recovery_required_event_id": recovery_required_id,
                "outcome": "committed",
                "error_code": "committed_record_verified",
                "approved_record_hash": intent["approved_record_hash"],
                "approved_record_size": intent["approved_record_size"],
                "approved_record_version": revision["proposed_approved_record"]["record_version"],
            },
            **common,
        )
        _publish_apply_completion(
            project_dir=project_dir, intent=intent, revision=revision
        )
        return _apply_response(intent=intent, revision=revision, replayed=True)

    if _observation_matches_before(observation, revision):
        append_event(
            project_dir,
            event_type="apply_failed_before_commit",
            content={
                "apply_id": intent["apply_id"],
                "intent_event_id": intent["event_id"],
                "outcome": "not_committed",
                "error_code": "destination_matches_before_state",
            },
            **common,
        )
        append_event(
            project_dir,
            event_type="recovery_completed",
            content={
                "apply_id": intent["apply_id"],
                "intent_event_id": intent["event_id"],
                "recovery_required_event_id": recovery_required_id,
                "outcome": "not_committed",
                "error_code": "destination_matches_before_state",
                "approved_record_hash": None,
                "approved_record_size": None,
                "approved_record_version": None,
            },
            **common,
        )
        raise ApplyContractError("APPLY_FAILED_BEFORE_COMMIT")

    if not recovery_required:
        append_event(
            project_dir,
            event_type="recovery_required",
            content={
                "apply_id": intent["apply_id"],
                "intent_event_id": intent["event_id"],
                "outcome": "unclassified",
                "error_code": "record_state_unclassified",
                "observed_record_hash": observation["hash"],
                "observed_record_size": observation["size"],
                "observed_record_version": observation["version"],
            },
            **common,
        )
    raise ApplyContractError("RECOVERY_REQUIRED")


def final_apply_promotion(
    *, project_dir: Path, project_id: str, promotion_id: str,
    promotion: dict[str, Any], candidate: dict[str, Any], body: Any,
    registry: FinalChallengeRegistry
) -> dict[str, Any]:
    request = _closed_final_apply_request(body, promotion_id=promotion_id)
    raw_chain = scan_event_chain(
        project_dir, project_id=project_id, promotion_id=promotion_id
    )
    existing_intents = _intent_events_for_key(
        list(raw_chain.events), request["idempotency_key"]
    )
    if len(existing_intents) > 1:
        raise ApplyContractError("AMBIGUOUS_OR_CONFLICTING_HISTORY")

    if existing_intents:
        intent = existing_intents[0]
        if (
            request["revision"] != intent["revision"]
            or request["sealed_contract_hash"] != intent["sealed_contract_hash"]
            or request["before_state_snapshot_token"]
            != intent["before_state_snapshot_token"]
        ):
            raise ApplyContractError("APPLY_EVENT_IDEMPOTENCY_SCOPE_CONFLICT")
        lineage = derive_apply_contract_lineage(
            project_dir=project_dir,
            project_id=project_id,
            promotion_id=promotion_id,
            candidate_id=intent["candidate_id"],
        )
        sealed = lineage["seals"].get(intent["revision"])
        if sealed is None:
            raise ApplyContractError("APPLY_EVENT_REFERENCE_MISSING_OR_CORRUPT")
        matching_seal_events = [
            event for event in lineage["events"]
            if event["event_type"] == "contract_approved"
            and event["event_id"] == intent["seal_event_id"]
            and event["sealed_contract_hash"] == intent["sealed_contract_hash"]
        ]
        if len(matching_seal_events) != 1:
            raise ApplyContractError("APPLY_EVENT_REFERENCE_MISSING_OR_CORRUPT")
        _validate_intent_contract(intent, sealed, matching_seal_events[0])
        return _recover_apply_intent(
            project_dir=project_dir,
            lineage=lineage,
            intent=intent,
            sealed=sealed,
            seal_event=matching_seal_events[0],
        )

    candidate_id, _ = _association(
        project_id=project_id,
        promotion_id=promotion_id,
        promotion=promotion,
        candidate=candidate,
    )
    lineage = derive_apply_contract_lineage(
        project_dir=project_dir,
        project_id=project_id,
        promotion_id=promotion_id,
        candidate_id=candidate_id,
    )
    for prior_intent in [
        event for event in lineage["events"] if event["event_type"] == "apply_intent"
    ]:
        if _event_for_apply(lineage["events"], "apply_completed", prior_intent["apply_id"]):
            raise ApplyContractError("COMPLETED_APPLY_EXISTS")
        prior_recovery = _event_for_apply(
            lineage["events"], "recovery_completed", prior_intent["apply_id"]
        )
        if not prior_recovery or prior_recovery[-1]["outcome"] != "not_committed":
            raise ApplyContractError("APPLY_INTENT_EXISTS")
    if (
        lineage["state"] != "sealed_active"
        or lineage["active_sealed_revision"] != request["revision"]
        or lineage["active_sealed_contract_hash"] != request["sealed_contract_hash"]
    ):
        raise ApplyContractError("APPLY_CONTRACT_SEAL_NOT_ACTIVE")
    sealed = lineage["seals"].get(request["revision"])
    if sealed is None:
        raise ApplyContractError("APPLY_CONTRACT_SEALED_REVISION_NOT_FOUND")
    revision = sealed["revision"]
    if request["before_state_snapshot_token"] != revision["before_state"]["snapshot_token"]:
        raise ApplyContractError("APPLY_CONTRACT_BEFORE_STATE_CHANGED")
    matching_seal_events = [
        event for event in lineage["events"]
        if event["event_type"] == "contract_approved"
        and event["revision"] == request["revision"]
        and event["sealed_contract_hash"] == request["sealed_contract_hash"]
        and event["approval_event_id"] == sealed["approval_event_id"]
    ]
    if len(matching_seal_events) != 1:
        raise ApplyContractError("APPLY_EVENT_REFERENCE_MISSING_OR_CORRUPT")
    seal_event = matching_seal_events[0]
    owner = load_local_owner_identity(project_dir, project_id=project_id)
    if (
        owner != revision["prepared_by"]
        or owner != sealed["contract_approval"]["owner_actor"]
    ):
        raise ApplyContractError("OWNER_IDENTITY_CHANGED")
    legacy = _safe_legacy_audit_entries(
        project_dir,
        project_id=project_id,
        promotion_id=promotion_id,
        candidate_id=candidate_id,
    )
    if any(entry["event"].get("promotion_status") == "applied" for entry in legacy):
        raise ApplyContractError("COMPLETED_APPLY_EXISTS")
    current = _before_state(
        project_dir,
        revision["destination"]["approved_destination_type"],
        revision["destination"]["destination_key"],
        observed_at=_now(),
    )
    if current["snapshot_token"] != revision["before_state"]["snapshot_token"]:
        raise ApplyContractError("APPLY_CONTRACT_BEFORE_STATE_CHANGED")
    blockers = (
        _decision_blockers(revision)
        + _dependency_truth_blockers(project_dir, revision)
        + _duplicate_truth_blockers(project_dir, revision)
    )
    if blockers:
        raise ApplyContractError(blockers[0]["code"])
    proposed = approved_record_material(revision["proposed_approved_record"])
    if proposed.approved_record_hash != revision["approved_record_hash"]:
        raise ApplyContractError("APPROVED_RECORD_HASH_MISMATCH")
    if proposed.approved_record_size != revision["approved_record_size"]:
        raise ApplyContractError("APPROVED_RECORD_SIZE_MISMATCH")

    challenge_scope = {
        "protocol": "apply-promotion-final-challenge.v1",
        "project_id": project_id,
        "promotion_id": promotion_id,
        "revision": revision["revision"],
        "sealed_contract_hash": sealed["sealed_contract_hash"],
        "before_state_snapshot_token": revision["before_state"]["snapshot_token"],
        "operation": revision["operation"],
        "destination_path": revision["destination"]["destination_path"],
        "authoritative_owner_actor": owner,
        "challenge_id": request["challenge_id"],
    }
    stored_scope = registry.outstanding_scope(request["challenge_id"])
    if any(stored_scope.get(field) != value for field, value in challenge_scope.items()):
        raise ApplyContractError("FINAL_CHALLENGE_SCOPE_MISMATCH")
    accepted_scope = registry.begin_consumption(
        challenge_id=request["challenge_id"],
        challenge_response=request["challenge_response"],
        expected_challenge_scope=stored_scope,
    )
    confirmed_at = _now()
    confirmation_binding = {
        "project_id": project_id,
        "promotion_id": promotion_id,
        "revision": revision["revision"],
        "sealed_contract_hash": sealed["sealed_contract_hash"],
        "before_state_snapshot_token": revision["before_state"]["snapshot_token"],
        "operation": revision["operation"],
        "destination_path": revision["destination"]["destination_path"],
        "authoritative_owner_actor": owner,
        "confirmation_method": request["final_confirmation"]["method"],
        "challenge_id": request["challenge_id"],
        "confirmed_at": confirmed_at,
    }
    final_confirmation_id = canonical_sha256(confirmation_binding)
    final_scope_hash = canonical_sha256(
        _final_apply_scope(
            project_id=project_id,
            promotion_id=promotion_id,
            revision=revision,
            sealed_contract_hash=sealed["sealed_contract_hash"],
            authoritative_owner_actor=owner,
        )
    )
    apply_id = _apply_identity(
        project_id=project_id,
        promotion_id=promotion_id,
        idempotency_key=request["idempotency_key"],
    )
    intent_content = {
        "apply_id": apply_id,
        "final_apply_scope_hash": final_scope_hash,
        "sealed_contract_hash": sealed["sealed_contract_hash"],
        "operation": revision["operation"],
        "destination_type": revision["destination"]["approved_destination_type"],
        "destination_key": revision["destination"]["destination_key"],
        "destination_path": revision["destination"]["destination_path"],
        "before_state_snapshot_token": revision["before_state"]["snapshot_token"],
        "before_state_version": revision["before_state"]["record_version"],
        "before_state_content_hash": revision["before_state"]["content_hash"],
        "approved_record_hash": revision["approved_record_hash"],
        "approved_record_size": revision["approved_record_size"],
        "sealed_revision_path": sealed_revision_relative_path(
            promotion_id, revision["revision"]
        ).as_posix(),
        "approval_event_id": sealed["approval_event_id"],
        "seal_event_id": seal_event["event_id"],
        "authoritative_owner_actor": owner,
        "final_confirmation_id": final_confirmation_id,
        "challenge_id": accepted_scope["challenge_id"],
        "confirmed_at": confirmed_at,
    }
    try:
        intent_publication = append_event(
            project_dir,
            event_type="apply_intent",
            project_id=project_id,
            promotion_id=promotion_id,
            candidate_id=candidate_id,
            revision=revision["revision"],
            idempotency_key=request["idempotency_key"],
            operation_identity=apply_id,
            created_at=confirmed_at,
            content=intent_content,
        )
    except Exception:
        registry.invalidate_before_intent(request["challenge_id"])
        raise
    intent = intent_publication.event
    registry.complete_consumption(request["challenge_id"])

    try:
        current_before_commit = _before_state(
            project_dir,
            revision["destination"]["approved_destination_type"],
            revision["destination"]["destination_key"],
            observed_at=_now(),
        )
        if current_before_commit["snapshot_token"] != revision["before_state"]["snapshot_token"]:
            raise ApplyContractError("APPLY_CONTRACT_BEFORE_STATE_CHANGED")
        commit_blockers = (
            _dependency_truth_blockers(project_dir, revision)
            + _duplicate_truth_blockers(project_dir, revision)
        )
        if commit_blockers:
            raise ApplyContractError(commit_blockers[0]["code"])
        committed = commit_approved_record(
            project_dir,
            operation=revision["operation"],
            before_record=revision["before_state"]["content"],
            proposed_record=revision["proposed_approved_record"],
        )
        if (
            committed.approved_record_hash != intent["approved_record_hash"]
            or committed.approved_record_size != intent["approved_record_size"]
        ):
            raise ApplyContractError("APPLY_COMMITTED_RECORD_MISMATCH")
    except Exception:
        refreshed = derive_apply_contract_lineage(
            project_dir=project_dir,
            project_id=project_id,
            promotion_id=promotion_id,
            candidate_id=candidate_id,
        )
        return _recover_apply_intent(
            project_dir=project_dir,
            lineage=refreshed,
            intent=intent,
            sealed=sealed,
            seal_event=seal_event,
        )

    _publish_apply_completion(
        project_dir=project_dir,
        intent=intent,
        revision=revision,
    )
    return _apply_response(intent=intent, revision=revision, replayed=False)


__all__ += (
    "approve_apply_contract",
    "derive_apply_contract_lineage",
    "issue_final_challenge",
    "final_apply_promotion",
    "prepare_apply_contract",
    "read_apply_audit",
    "read_apply_contract",
    "revoke_apply_contract",
)
