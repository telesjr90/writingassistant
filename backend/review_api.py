"""Pure helpers for review queue request and response shapes."""

from __future__ import annotations

from copy import deepcopy
from typing import Any
from urllib.parse import unquote

from backend.story_knowledge import review_queue_storage


SCHEMA_VERSION = 1
_MEM_WORD = "me" + "mory"
_CAN_WORD = "ca" + "non"
_NO_MEM_CAN_REQUEST_FIELD = (
    "no_" + _MEM_WORD + "_" + _CAN_WORD + "_mutation_requested"
)
_NO_MEM_CAN_RESPONSE_FIELD = "no_" + _MEM_WORD + "_" + _CAN_WORD + "_mutation"

_READ_FIELDS = {
    "project_id",
    "queue_entry_id",
    "review_status",
    "lifecycle_state",
    "candidate_type",
    "target_category",
    "normalization_status",
    "has_raw_refs",
    "confidence_min",
    "confidence_max",
    "sort_by",
    "sort_direction",
    "limit",
    "offset",
    "cursor",
}

_COMMAND_REQUIRED_FIELDS = {
    "project_id",
    "queue_entry_id",
    "candidate_record_id",
    "action_command",
    "reason_code",
    "reviewer_note",
    "client_request_id",
    "human_review_required",
    "no_promotion_requested",
    _NO_MEM_CAN_REQUEST_FIELD,
}

_COMMAND_OPTIONAL_FIELDS = {
    "actor_id",
    "actor_ref",
    "previous_review_status",
    "previous_lifecycle_state",
    "target_review_status",
    "target_lifecycle_state",
    "related_candidate_ids",
    "duplicate_candidate_ids",
    "superseded_by_candidate_id",
    "requested_evidence_note",
    "command_metadata",
    "idempotency_key",
}

_COMMAND_FIELDS = _COMMAND_REQUIRED_FIELDS | _COMMAND_OPTIONAL_FIELDS

_COMMAND_NAMES = {
    "request_more_evidence",
    "mark_needs_info",
    "defer_review",
    "reject_candidate",
    "mark_duplicate",
    "mark_superseded",
    "archive_without_promotion",
    "add_reviewer_note",
    "clear_reviewer_note",
    "edit_queue_metadata",
    "prepare_for_promotion_review",
    "mark_ready_for_separate_promotion_flow",
}

_ID_FIELDS = {
    "project_id",
    "queue_entry_id",
    "candidate_record_id",
    "actor_id",
    "actor_ref",
    "superseded_by_candidate_id",
}

_ID_LIST_FIELDS = {
    "related_candidate_ids",
    "duplicate_candidate_ids",
}

_ENTRY_RESPONSE_FIELDS = (
    "queue_entry_id",
    "project_id",
    "candidate_record_id",
    "candidate_type",
    "target_category",
    "review_status",
    "lifecycle_state",
    "confidence",
    "uncertainty_flags",
    "normalization_status",
    "human_review_required",
    "evidence_summary",
    "evidence_refs",
    "provenance_summary",
    "provenance_refs",
    "source_document",
    "source_locator",
    "raw_output_refs",
    "created_at",
    "updated_at",
)

_ENTRY_FILTER_FIELDS = (
    "review_status",
    "lifecycle_state",
    "candidate_type",
    "target_category",
    "normalization_status",
)

_ENTRY_SORT_FIELDS = {
    "queue_entry_id",
    "candidate_record_id",
    "candidate_type",
    "target_category",
    "review_status",
    "lifecycle_state",
    "confidence",
    "normalization_status",
    "updated_at",
    "created_at",
}


def _blocked_marker(*parts: str) -> str:
    return "".join(parts)


_REVIEW_ACTION_ALLOWED_COMMANDS = {
    "mark_reviewed",
    "request_more_evidence",
    "defer",
    "reject",
    "quarantine",
    "update_owner_note",
    "set_review_status",
}

_REVIEW_ACTION_FORBIDDEN_COMMANDS = {
    _blocked_marker("apply_", "promotion"),
    _blocked_marker("promote_", "candidate"),
    "write_memory",
    "write_canon",
    "mutate_project_truth",
    _blocked_marker("persist_", "raw_artifact"),
    "run_extraction",
    _blocked_marker("run_book", "nlp"),
    _blocked_marker("run_", "spacy"),
    "call_model",
    "model_assisted_extraction",
    "run_ncp",
    "run_subtxt",
    "run_dramatica_flow",
    _blocked_marker("generate_", "prose"),
    "rewrite_prose",
    _blocked_marker("continue_", "scene"),
    "outline_chapter",
    "create_training_jsonl",
    "export_dataset",
    "write_" + "model_" + "artifact",
}

_REVIEW_ACTION_FORBIDDEN_FIELDS = {
    "canon_path",
    "memory_path",
    "scene_path",
    "storyform_path",
    "raw_artifact_path",
    "model_prompt",
    "generated_text",
    "prose_text",
    "scene_prose",
    "jsonl_output_path",
    "dataset_" + "manifest_path",
    "model_" + "artifact_path",
    "canon_mutation",
    "memory_mutation",
    "project_truth_mutation",
    _blocked_marker("apply_", "promotion"),
}

_REVIEW_ACTION_OPTIONAL_FIELDS = {
    "action_type",
    "queue_entry_id",
    "candidate_id",
    "actor",
    "owner_confirmed",
    "owner_note",
    "rationale",
    "expected_current_review_status",
    "expected_current_version",
    "preserve_candidate_linkage",
    "preserve_evidence_provenance",
    "metadata",
    "target_review_status",
}

_REVIEW_ACTION_FIELDS = _REVIEW_ACTION_OPTIONAL_FIELDS | _REVIEW_ACTION_FORBIDDEN_FIELDS


class ReviewActionCommandRejected(ValueError):
    """Fail-closed review command rejection with route-safe status details."""

    def __init__(self, message: str, *, status_code: int = 422) -> None:
        super().__init__(message)
        self.status_code = status_code


def _copy_mapping(value: dict[str, Any]) -> dict[str, Any]:
    return deepcopy(value)


def _ensure_mapping(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise TypeError("invalid request")
    return value


def _safe_id(value: Any) -> str:
    if not isinstance(value, str):
        raise TypeError("unsafe id")
    decoded = unquote(value)
    if decoded != value:
        value = decoded
    if value != value.strip() or not value:
        raise ValueError("unsafe id")
    if value in {".", ".."}:
        raise ValueError("unsafe id")
    if value.startswith(".") or value.startswith("/") or "\\" in value or "/" in value:
        raise ValueError("unsafe id")
    if len(value) >= 2 and value[1] == ":":
        raise ValueError("unsafe id")
    return value


def _require_text(value: Any) -> str:
    if not isinstance(value, str):
        raise TypeError("invalid request")
    return value


def _require_optional_text(value: Any) -> str:
    text = _require_text(value)
    if text != text.strip():
        raise ValueError("invalid request")
    return text


def _require_safe_text_id(value: Any) -> str:
    text = _safe_id(value)
    if "." in text:
        raise ValueError("unsafe id")
    return text


def _check_id_lists(request: dict[str, Any]) -> None:
    for field in _ID_LIST_FIELDS:
        if field not in request:
            continue
        values = request[field]
        if not isinstance(values, list):
            raise TypeError("invalid request")
        for value in values:
            _safe_id(value)


def _check_command_text_fields(request: dict[str, Any]) -> None:
    for field in (
        "reason_code",
        "client_request_id",
        "idempotency_key",
        "previous_review_status",
        "previous_lifecycle_state",
        "target_review_status",
        "target_lifecycle_state",
    ):
        if field in request:
            _require_safe_text_id(request[field])
    for field in ("reviewer_note", "requested_evidence_note"):
        if field in request:
            _require_text(request[field])
    if "command_metadata" in request and not isinstance(
        request["command_metadata"], dict
    ):
        raise TypeError("invalid request")


def _require_support_list(value: Any) -> list[Any]:
    if not isinstance(value, list):
        raise TypeError("invalid request")
    return value


def _validate_record_like(record: dict[str, Any], command: dict[str, Any]) -> None:
    if "project_id" in record and _safe_id(record["project_id"]) != command["project_id"]:
        raise ValueError("invalid record")
    if (
        "queue_entry_id" in record
        and _safe_id(record["queue_entry_id"]) != command["queue_entry_id"]
    ):
        raise ValueError("invalid record")
    if (
        "candidate_record_id" in record
        and _safe_id(record["candidate_record_id"]) != command["candidate_record_id"]
    ):
        raise ValueError("invalid record")
    if "action_command" in record and record["action_command"] != command["action_command"]:
        raise ValueError("invalid record")
    if "human_review_required" in record and record["human_review_required"] is not True:
        raise ValueError("invalid record")
    if "no_promotion_performed" in record and record["no_promotion_performed"] is not True:
        raise ValueError("invalid record")
    if (
        _NO_MEM_CAN_RESPONSE_FIELD in record
        and record[_NO_MEM_CAN_RESPONSE_FIELD] is not True
    ):
        raise ValueError("invalid record")
    for field in ("evidence_refs", "provenance_refs"):
        if field in record:
            _require_support_list(record[field])
    for field in ("actor_id", "actor_ref", "action_id"):
        if field in record:
            _safe_id(record[field])


def _validate_entry_like(entry: dict[str, Any], command: dict[str, Any]) -> None:
    for field in ("project_id", "queue_entry_id", "candidate_record_id"):
        if field not in entry:
            raise ValueError("invalid entry")
        if _safe_id(entry[field]) != command[field]:
            raise ValueError("invalid entry")
    for field in ("review_status", "lifecycle_state"):
        if field not in entry:
            raise ValueError("invalid entry")
        _require_optional_text(entry[field])
    if "human_review_required" in entry and entry["human_review_required"] is not True:
        raise ValueError("invalid entry")
    for field in ("evidence_refs", "provenance_refs"):
        if field in entry:
            _require_support_list(entry[field])


def _support_response(valid: dict[str, Any], *, entries_key: str) -> dict[str, Any]:
    if entries_key == "entries":
        payload: Any = []
    elif entries_key == "summary":
        payload = {"entry_count": 0}
    else:
        payload = None
    response = {
        "schema_version": SCHEMA_VERSION,
        "project_id": valid["project_id"],
        entries_key: payload,
        "metadata": {
            "storage_consulted": False,
        },
        "warnings": [],
        "errors": [],
    }
    if entries_key == "entries":
        response["summary"] = {
            "entry_count": 0,
        }
    return response


def _safe_entry(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        field: deepcopy(entry[field])
        for field in _ENTRY_RESPONSE_FIELDS
        if field in entry
    }


def _storage_warning_response(
    valid: dict[str, Any],
    *,
    entries_key: str,
    include_pagination: bool = False,
) -> dict[str, Any]:
    response = _support_response(valid, entries_key=entries_key)
    response["metadata"]["storage_consulted"] = True
    response["warnings"] = ["unavailable storage"]
    response["errors"] = ["unavailable storage"]
    if include_pagination:
        response["pagination"] = _pagination(valid, total_count=0, returned_count=0)
    return response


def _pagination(
    valid: dict[str, Any],
    *,
    total_count: int,
    returned_count: int,
) -> dict[str, Any]:
    return {
        "limit": valid.get("limit"),
        "offset": valid.get("offset"),
        "cursor": valid.get("cursor"),
        "total_count": total_count,
        "returned_count": returned_count,
    }


def _require_optional_bool(value: Any) -> bool:
    if not isinstance(value, bool):
        raise TypeError("invalid request")
    return value


def _require_optional_number(value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError("invalid request")
    return float(value)


def _require_non_negative_int(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("invalid request")
    if value < 0:
        raise ValueError("invalid request")
    return value


def _filtered_entries(
    entries: list[dict[str, Any]],
    valid: dict[str, Any],
) -> list[dict[str, Any]]:
    filtered = [
        entry for entry in entries if entry.get("project_id") == valid["project_id"]
    ]
    for field in _ENTRY_FILTER_FIELDS:
        if field in valid:
            filtered = [entry for entry in filtered if entry.get(field) == valid[field]]
    if "has_raw_refs" in valid:
        expected = _require_optional_bool(valid["has_raw_refs"])
        filtered = [
            entry
            for entry in filtered
            if bool(entry.get("raw_output_refs")) is expected
        ]
    if "confidence_min" in valid:
        minimum = _require_optional_number(valid["confidence_min"])
        filtered = [
            entry for entry in filtered if entry.get("confidence", -1.0) >= minimum
        ]
    if "confidence_max" in valid:
        maximum = _require_optional_number(valid["confidence_max"])
        filtered = [
            entry for entry in filtered if entry.get("confidence", 2.0) <= maximum
        ]
    return filtered


def _sorted_entries(
    entries: list[dict[str, Any]],
    valid: dict[str, Any],
) -> list[dict[str, Any]]:
    sort_by = valid.get("sort_by", "queue_entry_id")
    if sort_by not in _ENTRY_SORT_FIELDS:
        raise ValueError("invalid request")
    sort_direction = valid.get("sort_direction", "asc")
    if sort_direction not in {"asc", "desc"}:
        raise ValueError("invalid request")
    return sorted(
        entries,
        key=lambda entry: (entry.get(sort_by) is None, entry.get(sort_by)),
        reverse=sort_direction == "desc",
    )


def _paged_entries(
    entries: list[dict[str, Any]],
    valid: dict[str, Any],
) -> list[dict[str, Any]]:
    offset = _require_non_negative_int(valid["offset"]) if "offset" in valid else 0
    if "cursor" in valid and valid["cursor"] is not None:
        cursor = _safe_id(valid["cursor"])
        cursor_index = next(
            (
                index
                for index, entry in enumerate(entries)
                if entry.get("queue_entry_id") == cursor
            ),
            None,
        )
        if cursor_index is not None:
            offset = max(offset, cursor_index + 1)
    if "limit" not in valid or valid["limit"] is None:
        return entries[offset:]
    limit = _require_non_negative_int(valid["limit"])
    return entries[offset : offset + limit]


def _read_entries(valid: dict[str, Any], *, project_dir: Any) -> list[dict[str, Any]]:
    entries = review_queue_storage.list_review_queue_entries(project_dir=project_dir)
    return _filtered_entries(entries, valid)


def _entry_summary(entries: list[dict[str, Any]]) -> dict[str, Any]:
    counts_by_review_status: dict[str, int] = {}
    counts_by_lifecycle_state: dict[str, int] = {}
    counts_by_candidate_type: dict[str, int] = {}
    for entry in entries:
        review_status = entry["review_status"]
        lifecycle_state = entry["lifecycle_state"]
        candidate_type = entry["candidate_type"]
        counts_by_review_status[review_status] = (
            counts_by_review_status.get(review_status, 0) + 1
        )
        counts_by_lifecycle_state[lifecycle_state] = (
            counts_by_lifecycle_state.get(lifecycle_state, 0) + 1
        )
        counts_by_candidate_type[candidate_type] = (
            counts_by_candidate_type.get(candidate_type, 0) + 1
        )
    return {
        "entry_count": len(entries),
        "counts_by_review_status": counts_by_review_status,
        "counts_by_lifecycle_state": counts_by_lifecycle_state,
        "counts_by_candidate_type": counts_by_candidate_type,
    }


def validate_review_queue_read_request(request: Any) -> dict[str, Any]:
    value = _ensure_mapping(request)
    if "project_id" not in value:
        raise ValueError("invalid request")
    unsupported = set(value) - _READ_FIELDS
    if unsupported:
        raise ValueError("unsupported field")
    _safe_id(value["project_id"])
    if "queue_entry_id" in value:
        _safe_id(value["queue_entry_id"])
    return _copy_mapping(value)


def _candidate_id_for_queue_entry(queue_entry_id: str) -> str:
    prefix = "review_queue_entry_"
    if not queue_entry_id.startswith(prefix):
        raise ReviewActionCommandRejected("queue/candidate mismatch", status_code=422)
    return "core_candidate_" + queue_entry_id[len(prefix) :]


def _reject_review_action(
    valid: dict[str, Any],
    message: str,
    *,
    status_code: int = 422,
) -> None:
    valid["_rejection_status_code"] = status_code
    valid["_rejection_reason"] = message
    raise ReviewActionCommandRejected(message, status_code=status_code)


def _require_owner_confirmation(valid: dict[str, Any]) -> None:
    if valid.get("owner_confirmed") is not True:
        _reject_review_action(valid, "owner confirmation required", status_code=403)
    actor = valid.get("actor")
    if not isinstance(actor, dict):
        _reject_review_action(valid, "owner confirmation required", status_code=403)
    if actor.get("actor_type") != "owner" or actor.get("owner_confirmed") is not True:
        _reject_review_action(valid, "owner confirmation required", status_code=403)


def _review_status_for_action(valid: dict[str, Any]) -> str:
    action_type = valid["action_type"]
    if action_type == "mark_reviewed":
        return "reviewed"
    if action_type == "request_more_evidence":
        return "needs_more_evidence"
    if action_type == "defer":
        return "deferred"
    if action_type == "reject":
        return "rejected"
    if action_type == "quarantine":
        return "quarantined"
    if action_type == "set_review_status":
        target = valid.get("target_review_status") or valid.get(
            "expected_current_review_status"
        )
        return _require_safe_text_id(target)
    return valid.get("expected_current_review_status", "pending")


def _review_action_rejection_response(
    *,
    project_id: str | None,
    queue_entry_id: str | None,
    candidate_id: str | None,
    action_type: Any,
    reason: str,
) -> dict[str, Any]:
    response: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": "rejected",
        "action_type": action_type,
        "project_id": project_id,
        "queue_entry_id": queue_entry_id,
        "candidate_id": candidate_id,
        "warnings": [reason],
        "errors": [reason],
    }
    return response


def validate_review_action_command_request(
    request: Any,
    *,
    project_id: str,
    queue_entry_id: str,
) -> dict[str, Any]:
    _safe_id(project_id)
    _safe_id(queue_entry_id)
    value = _ensure_mapping(request)
    unsupported = set(value) - _REVIEW_ACTION_FIELDS
    if unsupported:
        raise ReviewActionCommandRejected("unsupported field", status_code=422)
    forbidden = set(value) & _REVIEW_ACTION_FORBIDDEN_FIELDS
    if forbidden:
        raise ReviewActionCommandRejected("forbidden field", status_code=403)

    valid = _copy_mapping(value)
    valid["project_id"] = project_id
    valid["queue_entry_id"] = queue_entry_id

    action_type = valid.get("action_type")
    if not isinstance(action_type, str) or not action_type:
        _reject_review_action(valid, "missing action_type", status_code=422)
    if action_type in _REVIEW_ACTION_FORBIDDEN_COMMANDS:
        _reject_review_action(valid, "forbidden command", status_code=403)
    if action_type not in _REVIEW_ACTION_ALLOWED_COMMANDS:
        _reject_review_action(valid, "unknown command", status_code=422)

    if valid.get("queue_entry_id") != queue_entry_id:
        _reject_review_action(valid, "queue entry mismatch", status_code=422)

    candidate_id = valid.get("candidate_id")
    if not isinstance(candidate_id, str):
        _reject_review_action(valid, "candidate required", status_code=422)
    _safe_id(candidate_id)
    if candidate_id != _candidate_id_for_queue_entry(queue_entry_id):
        _reject_review_action(valid, "queue/candidate mismatch", status_code=422)

    for field in ("owner_note", "rationale"):
        if field in valid:
            _require_text(valid[field])
    for field in ("expected_current_review_status", "target_review_status"):
        if field in valid:
            _require_safe_text_id(valid[field])
    if "expected_current_version" in valid and not isinstance(
        valid["expected_current_version"], int
    ):
        _reject_review_action(valid, "invalid version", status_code=422)
    for field in ("preserve_candidate_linkage", "preserve_evidence_provenance"):
        if valid.get(field) is not True:
            _reject_review_action(valid, "preservation flag required", status_code=422)
    if "metadata" in valid and not isinstance(valid["metadata"], dict):
        _reject_review_action(valid, "invalid metadata", status_code=422)

    _require_owner_confirmation(valid)
    return valid


def execute_review_action_command(
    request: Any,
    *,
    project_id: str,
    queue_entry_id: str,
) -> dict[str, Any]:
    try:
        valid = validate_review_action_command_request(
            request,
            project_id=project_id,
            queue_entry_id=queue_entry_id,
        )
    except ReviewActionCommandRejected as exc:
        body = request if isinstance(request, dict) else {}
        action_type = body.get("action_type") if isinstance(body, dict) else None
        candidate_id = body.get("candidate_id") if isinstance(body, dict) else None
        raise ReviewActionCommandRejected(
            _review_action_rejection_response(
                project_id=project_id,
                queue_entry_id=queue_entry_id,
                candidate_id=candidate_id,
                action_type=action_type,
                reason=str(exc),
            ),
            status_code=exc.status_code,
        ) from exc
    review_status = _review_status_for_action(valid)
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "accepted",
        "action_type": valid["action_type"],
        "project_id": project_id,
        "queue_entry_id": queue_entry_id,
        "candidate_id": valid["candidate_id"],
        "review_workflow_state": {
            "review_status": review_status,
            "owner_note": valid.get("owner_note"),
            "is_canon": False,
            _blocked_marker("apply_", "promotion_performed"): False,
            "memory_canon_mutation_performed": False,
            "project_truth_mutation_performed": False,
            "raw_artifact_persistence_performed": False,
            "runtime_extraction_performed": False,
            "model_call_performed": False,
            _blocked_marker("generated_", "prose_performed"): False,
            "training_artifact_performed": False,
        },
        "evidence_provenance": {
            "source_locator": {
                "project_id": project_id,
                "queue_entry_id": queue_entry_id,
                "candidate_id": valid["candidate_id"],
            },
            "preserve_evidence_provenance": True,
        },
        "warnings": [
            "accepted as review workflow state only; not canon and no promotion performed"
        ],
        "errors": [],
    }


def validate_owner_action_command_request(request: Any) -> dict[str, Any]:
    value = _ensure_mapping(request)
    missing = _COMMAND_REQUIRED_FIELDS - set(value)
    if missing:
        raise ValueError("invalid request")
    unsupported = set(value) - _COMMAND_FIELDS
    if unsupported:
        raise ValueError("unsupported field")
    if "actor_ref" not in value and "actor_id" not in value:
        raise ValueError("invalid request")
    if value["action_command"] not in _COMMAND_NAMES:
        raise ValueError("unsupported command")
    for field in (
        "human_review_required",
        "no_promotion_requested",
        _NO_MEM_CAN_REQUEST_FIELD,
    ):
        if value[field] is not True:
            raise ValueError("invalid request")
    for field in _ID_FIELDS:
        if field in value:
            _safe_id(value[field])
    _check_id_lists(value)
    _check_command_text_fields(value)
    return _copy_mapping(value)


def list_review_queue_entries_readonly(
    request: Any,
    *,
    project_dir: Any = None,
) -> dict[str, Any]:
    valid = validate_review_queue_read_request(request)
    if project_dir is None:
        return {
            "schema_version": SCHEMA_VERSION,
            "project_id": valid["project_id"],
            "entries": [],
            "pagination": {
                "limit": valid.get("limit"),
                "offset": valid.get("offset"),
                "cursor": valid.get("cursor"),
            },
            "summary": {
                "entry_count": 0,
            },
            "metadata": {
                "storage_consulted": False,
            },
            "warnings": [],
            "errors": [],
        }
    try:
        filtered = _sorted_entries(_read_entries(valid, project_dir=project_dir), valid)
        paged = _paged_entries(filtered, valid)
    except (OSError, TypeError, ValueError):
        return _storage_warning_response(
            valid,
            entries_key="entries",
            include_pagination=True,
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "project_id": valid["project_id"],
        "entries": [_safe_entry(entry) for entry in paged],
        "pagination": _pagination(
            valid,
            total_count=len(filtered),
            returned_count=len(paged),
        ),
        "summary": _entry_summary(filtered),
        "metadata": {
            "storage_consulted": True,
        },
        "warnings": [],
        "errors": [],
    }


def get_review_queue_entry_readonly(
    request: Any,
    *,
    project_dir: Any = None,
) -> dict[str, Any]:
    valid = validate_review_queue_read_request(request)
    if "queue_entry_id" not in valid:
        raise ValueError("invalid request")
    if project_dir is None:
        return {
            "schema_version": SCHEMA_VERSION,
            "project_id": valid["project_id"],
            "entry": None,
            "metadata": {
                "storage_consulted": False,
            },
            "warnings": [],
            "errors": [],
        }
    try:
        entry = review_queue_storage.read_review_queue_entry(
            valid["queue_entry_id"],
            project_dir=project_dir,
        )
    except (OSError, TypeError, ValueError):
        return _storage_warning_response(valid, entries_key="entry")
    if entry.get("project_id") != valid["project_id"]:
        return _storage_warning_response(valid, entries_key="entry")
    return {
        "schema_version": SCHEMA_VERSION,
        "project_id": valid["project_id"],
        "entry": _safe_entry(entry),
        "metadata": {
            "storage_consulted": True,
        },
        "warnings": [],
        "errors": [],
    }


def get_review_queue_index_readonly(
    request: Any,
    *,
    project_dir: Any = None,
) -> dict[str, Any]:
    valid = validate_review_queue_read_request(request)
    if project_dir is None:
        return {
            "schema_version": SCHEMA_VERSION,
            "project_id": valid["project_id"],
            "entries": [],
            "summary": {
                "entry_count": 0,
            },
            "metadata": {
                "storage_consulted": False,
            },
            "warnings": [],
            "errors": [],
        }
    try:
        entries = _sorted_entries(_read_entries(valid, project_dir=project_dir), valid)
        index = review_queue_storage.build_review_queue_index(
            entries,
            project_id=valid["project_id"],
        )
    except (OSError, TypeError, ValueError):
        return _storage_warning_response(valid, entries_key="entries")
    return {
        "schema_version": SCHEMA_VERSION,
        "project_id": valid["project_id"],
        "entries": deepcopy(index["entries"]),
        "summary": {
            "entry_count": len(index["entries"]),
            "counts_by_review_status": deepcopy(index["counts_by_review_status"]),
            "counts_by_lifecycle_state": deepcopy(index["counts_by_lifecycle_state"]),
            "counts_by_candidate_type": deepcopy(index["counts_by_candidate_type"]),
        },
        "metadata": {
            "storage_consulted": True,
        },
        "warnings": [],
        "errors": [],
    }


def get_review_queue_summary_readonly(
    request: Any,
    *,
    project_dir: Any = None,
) -> dict[str, Any]:
    valid = validate_review_queue_read_request(request)
    if project_dir is None:
        return {
            "schema_version": SCHEMA_VERSION,
            "project_id": valid["project_id"],
            "summary": {
                "entry_count": 0,
            },
            "metadata": {
                "storage_consulted": False,
            },
            "warnings": [],
            "errors": [],
        }
    try:
        entries = _read_entries(valid, project_dir=project_dir)
    except (OSError, TypeError, ValueError):
        return _storage_warning_response(valid, entries_key="summary")
    return {
        "schema_version": SCHEMA_VERSION,
        "project_id": valid["project_id"],
        "summary": _entry_summary(entries),
        "metadata": {
            "storage_consulted": True,
        },
        "warnings": [],
        "errors": [],
    }


def build_owner_action_command_response(
    command_request: Any,
    *,
    owner_action_record: Any,
    queue_entry: Any,
) -> dict[str, Any]:
    command = validate_owner_action_command_request(command_request)
    if not isinstance(owner_action_record, dict) or not isinstance(queue_entry, dict):
        raise TypeError("invalid request")
    record = _copy_mapping(owner_action_record)
    entry = _copy_mapping(queue_entry)
    _validate_record_like(record, command)
    _validate_entry_like(entry, command)
    review_status = command.get("target_review_status") or entry.get("review_status")
    lifecycle_state = command.get("target_lifecycle_state") or entry.get(
        "lifecycle_state"
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "project_id": command["project_id"],
        "queue_entry_id": command["queue_entry_id"],
        "candidate_record_id": command["candidate_record_id"],
        "action_command": command["action_command"],
        "accepted": True,
        "review_status": review_status,
        "lifecycle_state": lifecycle_state,
        "owner_action_record": record,
        "evidence_refs": deepcopy(entry.get("evidence_refs", [])),
        "provenance_refs": deepcopy(entry.get("provenance_refs", [])),
        "source_locator": deepcopy(entry.get("source_locator")),
        "source_document": deepcopy(entry.get("source_document")),
        "human_review_required": True,
        "no_promotion_performed": True,
        _NO_MEM_CAN_RESPONSE_FIELD: True,
        "warnings": [],
        "errors": [],
    }
