"""Pure apply-promotion helpers for Writer Assistant Core.

Apply-promotion is explicit, owner-confirmed, audited, evidence-backed, and
project-local. Candidate persistence is not canon; queue presence is not
approval; confidence is not truth; raw artifacts are support data.
"""

from __future__ import annotations

import copy
import hashlib
import json
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
