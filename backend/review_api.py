"""Pure helpers for review queue request and response shapes."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


SCHEMA_VERSION = 1

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
    "no_memory_canon_mutation_requested",
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


def _copy_mapping(value: dict[str, Any]) -> dict[str, Any]:
    return deepcopy(value)


def _ensure_mapping(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise TypeError("invalid request")
    return value


def _safe_id(value: Any) -> str:
    if not isinstance(value, str):
        raise TypeError("unsafe id")
    if value != value.strip() or not value:
        raise ValueError("unsafe id")
    if value in {".", ".."}:
        raise ValueError("unsafe id")
    if value.startswith(".") or value.startswith("/") or "\\" in value or "/" in value:
        raise ValueError("unsafe id")
    if len(value) >= 2 and value[1] == ":":
        raise ValueError("unsafe id")
    return value


def _check_id_lists(request: dict[str, Any]) -> None:
    for field in _ID_LIST_FIELDS:
        if field not in request:
            continue
        values = request[field]
        if not isinstance(values, list):
            raise TypeError("invalid request")
        for value in values:
            _safe_id(value)


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
        "no_memory_canon_mutation_requested",
    ):
        if value[field] is not True:
            raise ValueError("invalid request")
    for field in _ID_FIELDS:
        if field in value:
            _safe_id(value[field])
    _check_id_lists(value)
    return _copy_mapping(value)


def list_review_queue_entries_readonly(request: Any) -> dict[str, Any]:
    valid = validate_review_queue_read_request(request)
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


def get_review_queue_entry_readonly(request: Any) -> dict[str, Any]:
    valid = validate_review_queue_read_request(request)
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


def get_review_queue_index_readonly(request: Any) -> dict[str, Any]:
    valid = validate_review_queue_read_request(request)
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


def get_review_queue_summary_readonly(request: Any) -> dict[str, Any]:
    valid = validate_review_queue_read_request(request)
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
        "no_memory_canon_mutation": True,
        "warnings": [],
        "errors": [],
    }
