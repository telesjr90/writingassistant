"""Pure helpers for review queue request and response shapes."""

from __future__ import annotations

import base64
import hashlib
import json
import os
import stat
import uuid
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import unquote

from backend.story_knowledge import analysis_run_manifest
from backend.story_knowledge import apply_contract
from backend.story_knowledge import candidate_persistence
from backend.story_knowledge import candidate_record
from backend.story_knowledge import review_action_events
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
    "duplicate_target_queue_entry_id",
    "duplicate_target_expected_review_status",
    "duplicate_target_expected_version",
    "superseded_by_candidate_id",
    "superseding_target_queue_entry_id",
    "superseding_target_expected_review_status",
    "superseding_target_expected_version",
    "owner_authored_correction",
    "prior_analysis_run_id",
    "prior_analysis_run_manifest_hash",
    "prior_source_snapshot_id",
    "prior_source_hash",
    "prior_source_locator",
    "selected_source_locator",
    "requested_evidence_note",
    "command_metadata",
    "idempotency_key",
    "requested_owner_visible_label",
    "requested_source_locator",
}

_COMMAND_FIELDS = _COMMAND_REQUIRED_FIELDS | _COMMAND_OPTIONAL_FIELDS

_COMMAND_NAMES = {
    "approve_candidate",
    "request_more_evidence",
    "mark_needs_info",
    "defer_review",
    "reject_candidate",
    "mark_duplicate",
    "mark_split_required",
    "rename_candidate_metadata",
    "record_source_linkage_correction",
    "mark_superseded",
    "record_owner_authored_correction",
    "request_rerun_selected_source",
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
    "duplicate_target_queue_entry_id",
    "superseding_target_queue_entry_id",
    "prior_analysis_run_id",
    "prior_source_snapshot_id",
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
    "review_version",
    "owner_note",
    "rationale",
    "rejected_output_reason",
    "insufficient_evidence_reason",
    "owner_review_completed",
    "owner_reviewed_at",
    "owner_visible_label",
    "original_owner_visible_label",
    "requested_owner_visible_label",
    "original_source_locator",
    "requested_source_locator",
    "duplicate_candidate_ids",
    "duplicate_target_queue_entry_id",
    "duplicate_target_review_status",
    "duplicate_target_lifecycle_state",
    "duplicate_target_review_version",
    "superseded_by_candidate_id",
    "superseding_target_queue_entry_id",
    "superseding_target_review_status",
    "superseding_target_lifecycle_state",
    "superseding_target_review_version",
    "owner_authored_correction",
    "prior_analysis_run_id",
    "prior_analysis_run_manifest_hash",
    "prior_source_snapshot_id",
    "prior_source_hash",
    "prior_source_locator",
    "selected_source_locator",
    "prior_run_lineage_verification",
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
    "approve",
    "mark_reviewed",
    "request_more_evidence",
    "defer",
    "reject",
    "mark_duplicate",
    "mark_split_required",
    "rename_candidate_metadata",
    "record_source_linkage_correction",
    "mark_superseded",
    "record_owner_authored_correction",
    "request_rerun_selected_source",
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

_REVIEW_ACTION_COMMON_FIELDS = frozenset(
    {
        "action_type",
        "queue_entry_id",
        "candidate_id",
        "actor",
        "owner_confirmed",
        "preserve_candidate_linkage",
        "preserve_evidence_provenance",
        "idempotency_key",
        "expected_current_review_status",
        "expected_current_version",
    }
)
_REVIEW_ACTION_COMMAND_FIELDS = frozenset(
    {
        "target_review_status",
        "duplicate_candidate_ids",
        "duplicate_target_queue_entry_id",
        "duplicate_target_expected_review_status",
        "duplicate_target_expected_version",
        "superseded_by_candidate_id",
        "superseding_target_queue_entry_id",
        "superseding_target_expected_review_status",
        "superseding_target_expected_version",
        "owner_authored_correction",
        "owner_note",
        "rationale",
        "rejected_output_reason",
        "insufficient_evidence_reason",
        "quarantine_note",
        "requested_owner_visible_label",
        "requested_source_locator",
        "prior_analysis_run_id",
        "prior_analysis_run_manifest_hash",
        "prior_source_snapshot_id",
        "prior_source_hash",
        "prior_source_locator",
        "selected_source_locator",
    }
)
_REVIEW_ACTION_FIELDS = (
    _REVIEW_ACTION_COMMON_FIELDS
    | _REVIEW_ACTION_COMMAND_FIELDS
    | _REVIEW_ACTION_FORBIDDEN_FIELDS
)
_REVIEW_STATUSES = frozenset(
    {
        "pending",
        "needs_info",
        "approved",
        "rejected",
        "deferred",
        "duplicate",
        "split_required",
        "correction_recorded",
        "superseded",
        "archived",
    }
)
_VALID_REVIEW_STATE_PAIRS = frozenset(
    {
        ("pending", "draft_ready_for_review"),
        ("pending", "owner_review_pending"),
        ("needs_info", "needs_more_evidence"),
        ("needs_info", "blocked_invalid_support"),
        ("approved", "owner_reviewed_approved"),
        ("rejected", "owner_reviewed_rejected"),
        ("deferred", "owner_reviewed_deferred"),
        ("duplicate", "duplicate_candidate"),
        ("split_required", "incorrect_cluster_split_required"),
        ("correction_recorded", "rename_metadata_recorded"),
        ("correction_recorded", "source_linkage_correction_recorded"),
        ("correction_recorded", "owner_authored_correction_recorded"),
        ("needs_info", "rerun_selected_source_requested"),
        ("superseded", "superseded_candidate"),
        ("archived", "archived_without_promotion"),
    }
)
_TARGET_STATE_PAIRS = {
    "pending": ("pending", "owner_review_pending"),
    "needs_info": ("needs_info", "needs_more_evidence"),
    "rejected": ("rejected", "owner_reviewed_rejected"),
    "deferred": ("deferred", "owner_reviewed_deferred"),
    "duplicate": ("duplicate", "duplicate_candidate"),
    "split_required": ("split_required", "incorrect_cluster_split_required"),
    "superseded": ("superseded", "superseded_candidate"),
    "archived": ("archived", "archived_without_promotion"),
}
_COMMAND_ALLOWED_SOURCE_PAIRS = {
    "approve": frozenset(
        {
            ("pending", "draft_ready_for_review"),
            ("pending", "owner_review_pending"),
            ("needs_info", "needs_more_evidence"),
            ("deferred", "owner_reviewed_deferred"),
        }
    ),
    "mark_reviewed": frozenset(
        {
            ("pending", "draft_ready_for_review"),
            ("pending", "owner_review_pending"),
            ("needs_info", "needs_more_evidence"),
            ("deferred", "owner_reviewed_deferred"),
        }
    ),
    "request_more_evidence": frozenset(
        {
            ("pending", "draft_ready_for_review"),
            ("pending", "owner_review_pending"),
            ("needs_info", "needs_more_evidence"),
            ("deferred", "owner_reviewed_deferred"),
        }
    ),
    "defer": frozenset(
        {
            ("pending", "draft_ready_for_review"),
            ("pending", "owner_review_pending"),
            ("needs_info", "needs_more_evidence"),
            ("deferred", "owner_reviewed_deferred"),
        }
    ),
    "reject": frozenset(
        {
            ("pending", "draft_ready_for_review"),
            ("pending", "owner_review_pending"),
            ("needs_info", "needs_more_evidence"),
            ("deferred", "owner_reviewed_deferred"),
        }
    ),
    "mark_duplicate": frozenset(
        {
            ("pending", "draft_ready_for_review"),
            ("pending", "owner_review_pending"),
            ("needs_info", "needs_more_evidence"),
            ("deferred", "owner_reviewed_deferred"),
        }
    ),
    "mark_split_required": frozenset(
        {
            ("pending", "draft_ready_for_review"),
            ("pending", "owner_review_pending"),
            ("needs_info", "needs_more_evidence"),
            ("deferred", "owner_reviewed_deferred"),
        }
    ),
    "rename_candidate_metadata": frozenset(
        {
            ("pending", "draft_ready_for_review"),
            ("pending", "owner_review_pending"),
            ("needs_info", "needs_more_evidence"),
            ("deferred", "owner_reviewed_deferred"),
        }
    ),
    "record_source_linkage_correction": frozenset(
        {
            ("pending", "draft_ready_for_review"),
            ("pending", "owner_review_pending"),
            ("needs_info", "needs_more_evidence"),
            ("deferred", "owner_reviewed_deferred"),
        }
    ),
    "mark_superseded": frozenset(
        {
            ("pending", "draft_ready_for_review"),
            ("pending", "owner_review_pending"),
            ("needs_info", "needs_more_evidence"),
            ("deferred", "owner_reviewed_deferred"),
        }
    ),
    "record_owner_authored_correction": frozenset(
        {
            ("pending", "draft_ready_for_review"),
            ("pending", "owner_review_pending"),
            ("needs_info", "needs_more_evidence"),
            ("deferred", "owner_reviewed_deferred"),
        }
    ),
    "request_rerun_selected_source": frozenset(
        {
            ("pending", "draft_ready_for_review"),
            ("pending", "owner_review_pending"),
            ("needs_info", "needs_more_evidence"),
            ("deferred", "owner_reviewed_deferred"),
        }
    ),
    "quarantine": frozenset(
        {
            ("pending", "draft_ready_for_review"),
            ("pending", "owner_review_pending"),
            ("needs_info", "needs_more_evidence"),
        }
    ),
    "update_owner_note": _VALID_REVIEW_STATE_PAIRS,
    "set_review_status": _VALID_REVIEW_STATE_PAIRS
    - {
        ("approved", "owner_reviewed_approved"),
        ("duplicate", "duplicate_candidate"),
        ("split_required", "incorrect_cluster_split_required"),
        ("correction_recorded", "rename_metadata_recorded"),
        ("correction_recorded", "source_linkage_correction_recorded"),
        ("correction_recorded", "owner_authored_correction_recorded"),
        ("needs_info", "rerun_selected_source_requested"),
        ("superseded", "superseded_candidate"),
    },
}
_COMMAND_FIELD_RULES = {
    "approve": (frozenset({"owner_note"}), frozenset({"rationale"})),
    "mark_reviewed": (frozenset(), frozenset({"owner_note", "rationale"})),
    "request_more_evidence": (
        frozenset({"owner_note"}),
        frozenset({"rationale", "insufficient_evidence_reason"}),
    ),
    "defer": (frozenset({"owner_note"}), frozenset({"rationale"})),
    "reject": (
        frozenset({"owner_note"}),
        frozenset({"rationale", "rejected_output_reason"}),
    ),
    "mark_duplicate": (
        frozenset(
            {
                "owner_note",
                "duplicate_candidate_ids",
                "duplicate_target_queue_entry_id",
                "duplicate_target_expected_review_status",
                "duplicate_target_expected_version",
            }
        ),
        frozenset({"rationale"}),
    ),
    "mark_split_required": (
        frozenset({"owner_note", "rationale"}),
        frozenset(),
    ),
    "rename_candidate_metadata": (
        frozenset({"owner_note", "rationale", "requested_owner_visible_label"}),
        frozenset(),
    ),
    "record_source_linkage_correction": (
        frozenset({"owner_note", "rationale", "requested_source_locator"}),
        frozenset(),
    ),
    "mark_superseded": (
        frozenset(
            {
                "owner_note",
                "rationale",
                "superseded_by_candidate_id",
                "superseding_target_queue_entry_id",
                "superseding_target_expected_review_status",
                "superseding_target_expected_version",
            }
        ),
        frozenset(),
    ),
    "record_owner_authored_correction": (
        frozenset({"owner_note", "rationale", "owner_authored_correction"}),
        frozenset(),
    ),
    "request_rerun_selected_source": (
        frozenset(
            {
                "owner_note",
                "rationale",
                "prior_analysis_run_id",
                "prior_analysis_run_manifest_hash",
                "prior_source_snapshot_id",
                "prior_source_hash",
                "prior_source_locator",
                "selected_source_locator",
            }
        ),
        frozenset(),
    ),
    "quarantine": (
        frozenset({"owner_note"}),
        frozenset({"rationale", "quarantine_note"}),
    ),
    "update_owner_note": (frozenset({"owner_note"}), frozenset({"rationale"})),
}
_CANONICAL_REQUEST_FIELDS = (
    "request_schema_version",
    "project_id",
    "queue_entry_id",
    "candidate_id",
    "action_type",
    "actor",
    "owner_confirmed",
    "preserve_candidate_linkage",
    "preserve_evidence_provenance",
    "expected_current_review_status",
    "expected_current_version",
    "target_review_status",
    "duplicate_candidate_ids",
    "duplicate_target_queue_entry_id",
    "duplicate_target_expected_review_status",
    "duplicate_target_expected_version",
    "superseded_by_candidate_id",
    "superseding_target_queue_entry_id",
    "superseding_target_expected_review_status",
    "superseding_target_expected_version",
    "owner_authored_correction",
    "prior_analysis_run_id",
    "prior_analysis_run_manifest_hash",
    "prior_source_snapshot_id",
    "prior_source_hash",
    "prior_source_locator",
    "selected_source_locator",
    "owner_note",
    "rationale",
    "rejected_output_reason",
    "insufficient_evidence_reason",
    "quarantine_note",
    "requested_owner_visible_label",
    "requested_source_locator",
)
_EVIDENCE_PROVENANCE_PROJECTION_FIELDS = (
    "source_document",
    "source_locator",
    "evidence_summary",
    "evidence_refs",
    "provenance_summary",
    "provenance_refs",
    "raw_output_refs",
)
_MAX_REVIEW_VERSION = 2_147_483_647
_DUPLICATE_TARGET_ALLOWED_STATE_PAIRS = frozenset(
    {
        ("pending", "draft_ready_for_review"),
        ("pending", "owner_review_pending"),
        ("needs_info", "needs_more_evidence"),
        ("approved", "owner_reviewed_approved"),
        ("deferred", "owner_reviewed_deferred"),
    }
)
_SUPERSEDING_TARGET_ALLOWED_STATE_PAIRS = _DUPLICATE_TARGET_ALLOWED_STATE_PAIRS


class ReviewActionCommandError(ValueError):
    """Closed, route-safe review command failure."""

    status_code = 500

    def __init__(
        self,
        message: str,
        *,
        error_code: str,
        project_id: str | None = None,
        queue_entry_id: str | None = None,
        action_command: str | None = None,
        candidate_id: str | None = None,
        extra: dict[str, Any] | None = None,
    ) -> None:
        payload = {
            "schema_version": SCHEMA_VERSION,
            "status": "rejected",
            "error_code": error_code,
            "project_id": project_id,
            "queue_entry_id": queue_entry_id,
            "action_command": action_command,
            "candidate_id": candidate_id,
            "warnings": [message],
            "errors": [message],
        }
        if extra:
            payload.update(deepcopy(extra))
        self.payload = payload
        super().__init__(payload)


class ReviewActionBadRequest(ReviewActionCommandError):
    status_code = 400


class ReviewActionForbidden(ReviewActionCommandError):
    status_code = 403


class ReviewActionNotFound(ReviewActionCommandError):
    status_code = 404


class ReviewActionConflict(ReviewActionCommandError):
    status_code = 409


class ReviewActionUnprocessable(ReviewActionCommandError):
    status_code = 422


class ReviewActionLockUnavailable(ReviewActionCommandError):
    status_code = 423


class ReviewActionPersistenceFailure(ReviewActionCommandError):
    status_code = 500


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
    if any(0xD800 <= ord(character) <= 0xDFFF for character in value):
        raise ValueError("unsafe id")
    return value


def _require_sha256(value: Any) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise ValueError("invalid SHA-256")
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
        "duplicate_target_expected_review_status",
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
    safe = {
        field: deepcopy(entry[field])
        for field in _ENTRY_RESPONSE_FIELDS
        if field in entry
    }
    safe.setdefault("review_version", 0)
    safe.setdefault("owner_note", None)
    safe.setdefault("rationale", None)
    safe.setdefault("rejected_output_reason", None)
    safe.setdefault("insufficient_evidence_reason", None)
    safe.setdefault("owner_review_completed", False)
    safe.setdefault("owner_reviewed_at", None)
    return safe


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


def _command_error(
    error_type: type[ReviewActionCommandError],
    message: str,
    *,
    error_code: str,
    project_id: str | None = None,
    queue_entry_id: str | None = None,
    request: dict[str, Any] | None = None,
    extra: dict[str, Any] | None = None,
) -> ReviewActionCommandError:
    request = request or {}
    return error_type(
        message,
        error_code=error_code,
        project_id=project_id,
        queue_entry_id=queue_entry_id,
        action_command=request.get("action_type"),
        candidate_id=request.get("candidate_id"),
        extra=extra,
    )


def _require_unicode_scalar_text(
    value: Any,
    *,
    maximum: int,
    allow_null: bool = True,
) -> str | None:
    if value is None and allow_null:
        return None
    if not isinstance(value, str) or len(value) > maximum:
        raise ValueError("invalid text")
    if any(0xD800 <= ord(character) <= 0xDFFF for character in value):
        raise ValueError("invalid text")
    return value


def _require_owner_visible_label(value: Any) -> str:
    label = _require_unicode_scalar_text(value, maximum=256, allow_null=False)
    if (
        not label
        or label != label.strip()
        or label in {".", ".."}
        or "/" in label
        or "\\" in label
        or any(ord(character) < 32 or ord(character) == 127 for character in label)
    ):
        raise ValueError("invalid owner-visible label")
    return label


def _require_uuid4(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("invalid UUIDv4")
    try:
        parsed = uuid.UUID(value)
    except (AttributeError, ValueError) as exc:
        raise ValueError("invalid UUIDv4") from exc
    if parsed.version != 4 or str(parsed) != value:
        raise ValueError("invalid UUIDv4")
    return value


def _set_review_status_field_rules(target: Any) -> tuple[frozenset[str], frozenset[str]]:
    if target not in _TARGET_STATE_PAIRS:
        raise ValueError("invalid target review status")
    if target in {"duplicate", "split_required", "superseded"}:
        raise ValueError("specialized lifecycle state requires its explicit command")
    required = {"target_review_status"}
    optional = {"rationale"}
    if target in {"pending", "archived"}:
        optional.add("owner_note")
    else:
        required.add("owner_note")
    if target == "needs_info":
        optional.add("insufficient_evidence_reason")
    elif target == "rejected":
        optional.add("rejected_output_reason")
    elif target == "superseded":
        required.add("superseded_by_candidate_id")
    return frozenset(required), frozenset(optional)


def validate_review_action_command_request(
    request: Any,
    *,
    project_id: str,
    queue_entry_id: str,
) -> dict[str, Any]:
    body = request if isinstance(request, dict) else {}
    try:
        _safe_id(project_id)
        _safe_id(queue_entry_id)
    except (TypeError, ValueError) as exc:
        raise _command_error(
            ReviewActionUnprocessable,
            "invalid route identity",
            error_code="REVIEW_ACTION_INVALID_IDENTITY",
            project_id=project_id,
            queue_entry_id=queue_entry_id,
            request=body,
        ) from exc
    if not isinstance(request, dict):
        raise _command_error(
            ReviewActionUnprocessable,
            "request must be a JSON object",
            error_code="REVIEW_ACTION_INVALID_REQUEST",
            project_id=project_id,
            queue_entry_id=queue_entry_id,
        )
    value = _copy_mapping(request)
    unsupported = set(value) - _REVIEW_ACTION_FIELDS
    if unsupported:
        raise _command_error(
            ReviewActionUnprocessable,
            "unsupported request field",
            error_code="REVIEW_ACTION_INVALID_FIELD",
            project_id=project_id,
            queue_entry_id=queue_entry_id,
            request=value,
        )
    forbidden = set(value) & _REVIEW_ACTION_FORBIDDEN_FIELDS
    if forbidden:
        raise _command_error(
            ReviewActionForbidden,
            "forbidden request field",
            error_code="REVIEW_ACTION_FORBIDDEN_FIELD",
            project_id=project_id,
            queue_entry_id=queue_entry_id,
            request=value,
        )

    action_type = value.get("action_type")
    if action_type in _REVIEW_ACTION_FORBIDDEN_COMMANDS:
        raise _command_error(
            ReviewActionForbidden,
            "forbidden command",
            error_code="REVIEW_ACTION_FORBIDDEN_COMMAND",
            project_id=project_id,
            queue_entry_id=queue_entry_id,
            request=value,
        )
    if action_type not in _REVIEW_ACTION_ALLOWED_COMMANDS:
        raise _command_error(
            ReviewActionUnprocessable,
            "unknown or missing command",
            error_code="REVIEW_ACTION_INVALID_COMMAND",
            project_id=project_id,
            queue_entry_id=queue_entry_id,
            request=value,
        )

    for field in (
        "owner_confirmed",
        "preserve_candidate_linkage",
        "preserve_evidence_provenance",
    ):
        if value.get(field) is not True:
            raise _command_error(
                ReviewActionForbidden,
                "owner confirmation and preservation assertions are required",
                error_code="REVIEW_ACTION_CONFIRMATION_REQUIRED",
                project_id=project_id,
                queue_entry_id=queue_entry_id,
                request=value,
            )
    if value.get("actor") != "owner-reviewed":
        raise _command_error(
            ReviewActionForbidden,
            "owner confirmation is required",
            error_code="REVIEW_ACTION_CONFIRMATION_REQUIRED",
            project_id=project_id,
            queue_entry_id=queue_entry_id,
            request=value,
        )

    missing_common = _REVIEW_ACTION_COMMON_FIELDS - set(value)
    if missing_common:
        raise _command_error(
            ReviewActionUnprocessable,
            "missing required request field",
            error_code="REVIEW_ACTION_INVALID_REQUEST",
            project_id=project_id,
            queue_entry_id=queue_entry_id,
            request=value,
        )
    if value["queue_entry_id"] != queue_entry_id:
        raise _command_error(
            ReviewActionUnprocessable,
            "queue entry identity mismatch",
            error_code="REVIEW_ACTION_INVALID_IDENTITY",
            project_id=project_id,
            queue_entry_id=queue_entry_id,
            request=value,
        )
    try:
        _safe_id(value["candidate_id"])
        _require_uuid4(value["idempotency_key"])
    except (TypeError, ValueError) as exc:
        raise _command_error(
            ReviewActionUnprocessable,
            "invalid candidate identity or idempotency key",
            error_code="REVIEW_ACTION_INVALID_IDENTITY",
            project_id=project_id,
            queue_entry_id=queue_entry_id,
            request=value,
        ) from exc
    if value["expected_current_review_status"] not in _REVIEW_STATUSES:
        raise _command_error(
            ReviewActionUnprocessable,
            "invalid expected review status",
            error_code="REVIEW_ACTION_INVALID_STATUS",
            project_id=project_id,
            queue_entry_id=queue_entry_id,
            request=value,
        )
    expected_version = value["expected_current_version"]
    if (
        isinstance(expected_version, bool)
        or not isinstance(expected_version, int)
        or not 0 <= expected_version <= _MAX_REVIEW_VERSION
    ):
        raise _command_error(
            ReviewActionUnprocessable,
            "invalid expected review version",
            error_code="REVIEW_ACTION_INVALID_VERSION",
            project_id=project_id,
            queue_entry_id=queue_entry_id,
            request=value,
        )

    try:
        if action_type == "set_review_status":
            required, optional = _set_review_status_field_rules(
                value.get("target_review_status")
            )
        else:
            required, optional = _COMMAND_FIELD_RULES[action_type]
    except ValueError as exc:
        raise _command_error(
            ReviewActionUnprocessable,
            "invalid target review status",
            error_code="REVIEW_ACTION_INVALID_STATUS",
            project_id=project_id,
            queue_entry_id=queue_entry_id,
            request=value,
        ) from exc
    supplied_command_fields = set(value) & _REVIEW_ACTION_COMMAND_FIELDS
    forbidden_for_command = supplied_command_fields - required - optional
    if forbidden_for_command:
        raise _command_error(
            ReviewActionForbidden,
            "field is forbidden for this command",
            error_code="REVIEW_ACTION_FORBIDDEN_FIELD",
            project_id=project_id,
            queue_entry_id=queue_entry_id,
            request=value,
        )
    if not required <= set(value):
        raise _command_error(
            ReviewActionUnprocessable,
            "missing command-required field",
            error_code="REVIEW_ACTION_INVALID_REQUEST",
            project_id=project_id,
            queue_entry_id=queue_entry_id,
            request=value,
        )

    try:
        for field, maximum in (
            ("owner_note", 10_000),
            ("rationale", 1_000),
            ("quarantine_note", 10_000),
            ("rejected_output_reason", 10_000),
            ("insufficient_evidence_reason", 10_000),
            ("owner_authored_correction", 10_000),
        ):
            if field in value:
                _require_unicode_scalar_text(value[field], maximum=maximum)
        if "owner_note" in required and (
            not isinstance(value["owner_note"], str)
            or (action_type != "update_owner_note" and not value["owner_note"])
        ):
            raise ValueError("owner_note is required")
        if "rationale" in required and (
            not isinstance(value["rationale"], str) or not value["rationale"]
        ):
            raise ValueError("rationale is required")
        if "requested_owner_visible_label" in required:
            _require_owner_visible_label(value["requested_owner_visible_label"])
        if "requested_source_locator" in required:
            corrected_locator = candidate_record.validate_source_locator(
                value["requested_source_locator"]
            )
            if corrected_locator["project_id"] != project_id:
                raise ValueError("corrected source locator must remain project-local")
        if "duplicate_candidate_ids" in required:
            duplicate_ids = value["duplicate_candidate_ids"]
            if not isinstance(duplicate_ids, list) or len(duplicate_ids) != 1:
                raise ValueError("duplicate candidate IDs are required")
            for duplicate_id in duplicate_ids:
                _safe_id(duplicate_id)
            if len(set(duplicate_ids)) != len(duplicate_ids):
                raise ValueError("duplicate candidate IDs must be unique")
            if duplicate_ids[0] == value["candidate_id"]:
                raise ValueError("candidate cannot duplicate itself")
            target_queue_entry_id = _safe_id(
                value["duplicate_target_queue_entry_id"]
            )
            if target_queue_entry_id == value["queue_entry_id"]:
                raise ValueError("queue entry cannot duplicate itself")
            target_status = value["duplicate_target_expected_review_status"]
            if target_status not in _REVIEW_STATUSES:
                raise ValueError("invalid duplicate target status")
            target_version = value["duplicate_target_expected_version"]
            if (
                isinstance(target_version, bool)
                or not isinstance(target_version, int)
                or not 0 <= target_version <= _MAX_REVIEW_VERSION
            ):
                raise ValueError("invalid duplicate target version")
        if "superseded_by_candidate_id" in required:
            superseding_id = _safe_id(value["superseded_by_candidate_id"])
            if superseding_id == value["candidate_id"]:
                raise ValueError("candidate cannot supersede itself")
            target_queue_entry_id = _safe_id(
                value["superseding_target_queue_entry_id"]
            )
            if target_queue_entry_id == value["queue_entry_id"]:
                raise ValueError("queue entry cannot supersede itself")
            target_status = value["superseding_target_expected_review_status"]
            if target_status not in _REVIEW_STATUSES:
                raise ValueError("invalid superseding target status")
            target_version = value["superseding_target_expected_version"]
            if (
                isinstance(target_version, bool)
                or not isinstance(target_version, int)
                or not 0 <= target_version <= _MAX_REVIEW_VERSION
            ):
                raise ValueError("invalid superseding target version")
        if "owner_authored_correction" in required:
            correction = value["owner_authored_correction"]
            if not isinstance(correction, str) or not correction.strip():
                raise ValueError("owner-authored correction is required")
        if action_type == "request_rerun_selected_source":
            _safe_id(value["prior_analysis_run_id"])
            _safe_id(value["prior_source_snapshot_id"])
            _require_sha256(value["prior_analysis_run_manifest_hash"])
            prior_source_hash = _require_sha256(value["prior_source_hash"])
            prior_locator = candidate_record.validate_source_locator(
                value["prior_source_locator"]
            )
            selected_locator = candidate_record.validate_source_locator(
                value["selected_source_locator"]
            )
            if (
                prior_locator["project_id"] != project_id
                or selected_locator["project_id"] != project_id
                or prior_locator != selected_locator
                or prior_locator.get("source_hash") not in {None, prior_source_hash}
            ):
                raise ValueError("invalid rerun source lineage")
    except (TypeError, ValueError) as exc:
        raise _command_error(
            ReviewActionUnprocessable,
            "invalid command field value",
            error_code="REVIEW_ACTION_INVALID_FIELD",
            project_id=project_id,
            queue_entry_id=queue_entry_id,
            request=value,
        ) from exc
    return value


def build_canonical_review_action_request_record(
    validated_request: dict[str, Any],
    *,
    project_id: str,
    queue_entry_id: str,
) -> dict[str, Any]:
    record = {
        "request_schema_version": 1,
        "project_id": project_id,
        "queue_entry_id": queue_entry_id,
        "candidate_id": validated_request["candidate_id"],
        "action_type": validated_request["action_type"],
        "actor": validated_request["actor"],
        "owner_confirmed": validated_request["owner_confirmed"],
        "preserve_candidate_linkage": validated_request[
            "preserve_candidate_linkage"
        ],
        "preserve_evidence_provenance": validated_request[
            "preserve_evidence_provenance"
        ],
        "expected_current_review_status": validated_request[
            "expected_current_review_status"
        ],
        "expected_current_version": validated_request["expected_current_version"],
        "target_review_status": validated_request.get("target_review_status"),
        "duplicate_candidate_ids": deepcopy(
            validated_request.get("duplicate_candidate_ids")
        ),
        "duplicate_target_queue_entry_id": validated_request.get(
            "duplicate_target_queue_entry_id"
        ),
        "duplicate_target_expected_review_status": validated_request.get(
            "duplicate_target_expected_review_status"
        ),
        "duplicate_target_expected_version": validated_request.get(
            "duplicate_target_expected_version"
        ),
        "superseded_by_candidate_id": validated_request.get(
            "superseded_by_candidate_id"
        ),
        "superseding_target_queue_entry_id": validated_request.get(
            "superseding_target_queue_entry_id"
        ),
        "superseding_target_expected_review_status": validated_request.get(
            "superseding_target_expected_review_status"
        ),
        "superseding_target_expected_version": validated_request.get(
            "superseding_target_expected_version"
        ),
        "owner_authored_correction": validated_request.get(
            "owner_authored_correction"
        ),
        "prior_analysis_run_id": validated_request.get(
            "prior_analysis_run_id"
        ),
        "prior_analysis_run_manifest_hash": validated_request.get(
            "prior_analysis_run_manifest_hash"
        ),
        "prior_source_snapshot_id": validated_request.get(
            "prior_source_snapshot_id"
        ),
        "prior_source_hash": validated_request.get("prior_source_hash"),
        "prior_source_locator": deepcopy(
            validated_request.get("prior_source_locator")
        ),
        "selected_source_locator": deepcopy(
            validated_request.get("selected_source_locator")
        ),
        "owner_note": validated_request.get("owner_note"),
        "rationale": validated_request.get("rationale"),
        "rejected_output_reason": validated_request.get("rejected_output_reason"),
        "insufficient_evidence_reason": validated_request.get(
            "insufficient_evidence_reason"
        ),
        "quarantine_note": validated_request.get("quarantine_note"),
        "requested_owner_visible_label": validated_request.get(
            "requested_owner_visible_label"
        ),
        "requested_source_locator": deepcopy(
            validated_request.get("requested_source_locator")
        ),
    }
    if tuple(record) != _CANONICAL_REQUEST_FIELDS:
        raise ValueError("invalid canonical request record")
    return record


def canonical_review_action_request_bytes(record: dict[str, Any]) -> bytes:
    if not isinstance(record, dict) or set(record) != set(_CANONICAL_REQUEST_FIELDS):
        raise ValueError("invalid canonical request record")
    ordered = {field: deepcopy(record[field]) for field in _CANONICAL_REQUEST_FIELDS}
    if ordered["request_schema_version"] != 1:
        raise ValueError("invalid canonical request record")
    for field in (
        "project_id",
        "queue_entry_id",
        "candidate_id",
        "action_type",
        "actor",
        "expected_current_review_status",
    ):
        value = ordered[field]
        if not isinstance(value, str):
            raise ValueError("invalid canonical request record")
        _require_unicode_scalar_text(value, maximum=max(len(value), 1), allow_null=False)
    for field in (
        "owner_confirmed",
        "preserve_candidate_linkage",
        "preserve_evidence_provenance",
    ):
        if not isinstance(ordered[field], bool):
            raise ValueError("invalid canonical request record")
    version = ordered["expected_current_version"]
    if (
        isinstance(version, bool)
        or not isinstance(version, int)
        or not 0 <= version <= _MAX_REVIEW_VERSION
    ):
        raise ValueError("invalid canonical request record")
    for field in (
        "target_review_status",
        "duplicate_target_queue_entry_id",
        "duplicate_target_expected_review_status",
        "superseded_by_candidate_id",
        "superseding_target_queue_entry_id",
        "superseding_target_expected_review_status",
        "owner_authored_correction",
        "prior_analysis_run_id",
        "prior_analysis_run_manifest_hash",
        "prior_source_snapshot_id",
        "prior_source_hash",
        "owner_note",
        "rationale",
        "rejected_output_reason",
        "insufficient_evidence_reason",
        "quarantine_note",
        "requested_owner_visible_label",
    ):
        value = ordered[field]
        if value is not None:
            if not isinstance(value, str):
                raise ValueError("invalid canonical request record")
            _require_unicode_scalar_text(value, maximum=max(len(value), 1), allow_null=False)
    requested_source_locator = ordered["requested_source_locator"]
    if requested_source_locator is not None:
        candidate_record.validate_source_locator(requested_source_locator)
    for field in ("prior_source_locator", "selected_source_locator"):
        locator = ordered[field]
        if locator is not None:
            candidate_record.validate_source_locator(locator)
    for field in ("prior_analysis_run_manifest_hash", "prior_source_hash"):
        digest = ordered[field]
        if digest is not None:
            _require_sha256(digest)
    duplicate_ids = ordered["duplicate_candidate_ids"]
    if duplicate_ids is not None:
        if not isinstance(duplicate_ids, list):
            raise ValueError("invalid canonical request record")
        for item in duplicate_ids:
            if not isinstance(item, str):
                raise ValueError("invalid canonical request record")
            _require_unicode_scalar_text(item, maximum=max(len(item), 1), allow_null=False)
    duplicate_target_version = ordered["duplicate_target_expected_version"]
    if duplicate_target_version is not None and (
        isinstance(duplicate_target_version, bool)
        or not isinstance(duplicate_target_version, int)
        or not 0 <= duplicate_target_version <= _MAX_REVIEW_VERSION
    ):
        raise ValueError("invalid canonical request record")
    superseding_target_version = ordered["superseding_target_expected_version"]
    if superseding_target_version is not None and (
        isinstance(superseding_target_version, bool)
        or not isinstance(superseding_target_version, int)
        or not 0 <= superseding_target_version <= _MAX_REVIEW_VERSION
    ):
        raise ValueError("invalid canonical request record")
    return json.dumps(
        ordered,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
    ).encode("utf-8")


def hash_review_action_request(record: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_review_action_request_bytes(record)).hexdigest()


def _transition_error(command: dict[str, Any], message: str) -> ReviewActionUnprocessable:
    return _command_error(
        ReviewActionUnprocessable,
        message,
        error_code="REVIEW_ACTION_INVALID_TRANSITION",
        queue_entry_id=command.get("queue_entry_id"),
        request=command,
    )


def _validated_duplicate_target(
    source: dict[str, Any],
    command: dict[str, Any],
    duplicate_target: Any,
) -> dict[str, Any]:
    try:
        target = review_queue_storage.validate_review_queue_entry(duplicate_target)
    except (TypeError, ValueError) as exc:
        raise _transition_error(command, "invalid duplicate target queue entry") from exc
    target_candidate_ids = command.get("duplicate_candidate_ids")
    if (
        not isinstance(target_candidate_ids, list)
        or len(target_candidate_ids) != 1
        or target["queue_entry_id"] != command.get("duplicate_target_queue_entry_id")
        or target["candidate_record_id"] != target_candidate_ids[0]
        or target["project_id"] != source["project_id"]
        or target["queue_entry_id"] == source["queue_entry_id"]
        or target["candidate_record_id"] == source["candidate_record_id"]
        or target["candidate_type"] != source["candidate_type"]
        or target["target_category"] != source["target_category"]
    ):
        raise _transition_error(command, "duplicate source/target linkage mismatch")
    if (
        target["review_status"]
        != command.get("duplicate_target_expected_review_status")
        or target["review_version"]
        != command.get("duplicate_target_expected_version")
    ):
        raise _command_error(
            ReviewActionConflict,
            "stale duplicate target status or version",
            error_code="REVIEW_ACTION_STALE_DUPLICATE_TARGET",
            project_id=source["project_id"],
            queue_entry_id=source["queue_entry_id"],
            request=command,
        )
    target_pair = (target["review_status"], target["lifecycle_state"])
    if target_pair not in _DUPLICATE_TARGET_ALLOWED_STATE_PAIRS:
        raise _command_error(
            ReviewActionConflict,
            "duplicate target is not eligible",
            error_code="REVIEW_ACTION_DUPLICATE_TARGET_CONFLICT",
            project_id=source["project_id"],
            queue_entry_id=source["queue_entry_id"],
            request=command,
        )
    return target


def _validated_superseding_target(
    source: dict[str, Any],
    command: dict[str, Any],
    superseding_target: Any,
) -> dict[str, Any]:
    try:
        target = review_queue_storage.validate_review_queue_entry(
            superseding_target
        )
    except (TypeError, ValueError) as exc:
        raise _transition_error(
            command, "invalid superseding target queue entry"
        ) from exc
    if (
        target["queue_entry_id"]
        != command.get("superseding_target_queue_entry_id")
        or target["candidate_record_id"]
        != command.get("superseded_by_candidate_id")
        or target["project_id"] != source["project_id"]
        or target["queue_entry_id"] == source["queue_entry_id"]
        or target["candidate_record_id"] == source["candidate_record_id"]
        or target["candidate_type"] != source["candidate_type"]
        or target["target_category"] != source["target_category"]
    ):
        raise _transition_error(command, "supersede source/target linkage mismatch")
    if (
        target["review_status"]
        != command.get("superseding_target_expected_review_status")
        or target["review_version"]
        != command.get("superseding_target_expected_version")
    ):
        raise _command_error(
            ReviewActionConflict,
            "stale superseding target status or version",
            error_code="REVIEW_ACTION_STALE_SUPERSEDING_TARGET",
            project_id=source["project_id"],
            queue_entry_id=source["queue_entry_id"],
            request=command,
        )
    target_pair = (target["review_status"], target["lifecycle_state"])
    if target_pair not in _SUPERSEDING_TARGET_ALLOWED_STATE_PAIRS:
        raise _command_error(
            ReviewActionConflict,
            "superseding target is not eligible",
            error_code="REVIEW_ACTION_SUPERSEDING_TARGET_CONFLICT",
            project_id=source["project_id"],
            queue_entry_id=source["queue_entry_id"],
            request=command,
        )
    return target


def _validate_prior_run_lineage(
    source: dict[str, Any],
    command: dict[str, Any],
    *,
    project_dir: Path,
) -> None:
    run_id = command["prior_analysis_run_id"]
    manifest_path = (
        project_dir
        / "writer_assistant"
        / "analysis_runs"
        / run_id
        / "manifest.json"
    )
    try:
        resolved_manifest = manifest_path.resolve(strict=True)
        expected_manifest = manifest_path
        metadata = os.lstat(manifest_path)
        if (
            resolved_manifest != expected_manifest
            or stat.S_ISLNK(metadata.st_mode)
            or not stat.S_ISREG(metadata.st_mode)
            or metadata.st_nlink != 1
        ):
            raise ValueError("unsafe prior-run manifest path")
        raw = resolved_manifest.read_bytes()
        payload = apply_contract.strict_json_loads(raw, max_bytes=4_194_304)
        if apply_contract.canonical_json_bytes(payload) != raw:
            raise ValueError("prior-run manifest is not canonical")
        manifest = analysis_run_manifest.analysis_run_manifest_from_dict(payload)
    except FileNotFoundError as exc:
        raise _command_error(
            ReviewActionNotFound,
            "prior analysis run manifest was not found",
            error_code="REVIEW_ACTION_PRIOR_RUN_NOT_FOUND",
            project_id=source["project_id"],
            queue_entry_id=source["queue_entry_id"],
            request=command,
        ) from exc
    except (OSError, TypeError, ValueError) as exc:
        raise _command_error(
            ReviewActionUnprocessable,
            "prior analysis run manifest is invalid",
            error_code="REVIEW_ACTION_INVALID_PRIOR_RUN_LINEAGE",
            project_id=source["project_id"],
            queue_entry_id=source["queue_entry_id"],
            request=command,
        ) from exc

    requested_locator = candidate_record.validate_source_locator(
        command["selected_source_locator"]
    )
    matching_source = next(
        (
            item
            for item in manifest.sources
            if item.snapshot_id == command["prior_source_snapshot_id"]
        ),
        None,
    )
    source_locator = source["source_locator"]
    expected_locator_fields = {
        "project_id": matching_source.project_id if matching_source else None,
        "source_document_type": (
            matching_source.source_document_type if matching_source else None
        ),
        "source_document_id": (
            matching_source.source_document_id if matching_source else None
        ),
    }
    for optional_field in ("section_id", "chapter_id", "scene_id"):
        if matching_source is not None and getattr(matching_source, optional_field) is not None:
            expected_locator_fields[optional_field] = getattr(
                matching_source, optional_field
            )
    if (
        manifest.run_id != run_id
        or manifest.project_id != source["project_id"]
        or hashlib.sha256(raw).hexdigest()
        != command["prior_analysis_run_manifest_hash"]
        or matching_source is None
        or matching_source.content_hash != command["prior_source_hash"]
        or requested_locator != command["prior_source_locator"]
        or requested_locator != source_locator
        or any(
            requested_locator.get(field) != expected
            for field, expected in expected_locator_fields.items()
        )
        or requested_locator.get("source_hash")
        not in {None, matching_source.content_hash}
    ):
        raise _command_error(
            ReviewActionUnprocessable,
            "prior analysis run lineage does not match the selected source",
            error_code="REVIEW_ACTION_INVALID_PRIOR_RUN_LINEAGE",
            project_id=source["project_id"],
            queue_entry_id=source["queue_entry_id"],
            request=command,
        )


def compute_review_queue_transition(
    queue_entry: dict[str, Any],
    command: dict[str, Any],
    *,
    command_time: str,
    duplicate_target: dict[str, Any] | None = None,
    superseding_target: dict[str, Any] | None = None,
) -> dict[str, Any]:
    try:
        source = review_queue_storage.validate_review_queue_entry(queue_entry)
    except (TypeError, ValueError) as exc:
        raise _transition_error(command, "invalid source queue entry") from exc
    action = command["action_type"]
    source_pair = (source["review_status"], source["lifecycle_state"])
    if source_pair not in _COMMAND_ALLOWED_SOURCE_PAIRS[action]:
        raise _transition_error(command, "command is not allowed from current state")
    if source["review_version"] >= _MAX_REVIEW_VERSION:
        raise _transition_error(command, "review version overflow")

    target = deepcopy(source)
    state_change = action not in {"mark_reviewed", "update_owner_note"}
    if action == "approve":
        target["review_status"], target["lifecycle_state"] = (
            "approved",
            "owner_reviewed_approved",
        )
    elif action == "set_review_status":
        target_status = command["target_review_status"]
        if source_pair == ("archived", "archived_without_promotion") and target_status != "pending":
            raise _transition_error(command, "archived entries may only reopen to pending")
        target["review_status"], target["lifecycle_state"] = _TARGET_STATE_PAIRS[
            target_status
        ]
    elif action == "request_more_evidence":
        target["review_status"], target["lifecycle_state"] = _TARGET_STATE_PAIRS[
            "needs_info"
        ]
    elif action == "defer":
        target["review_status"], target["lifecycle_state"] = _TARGET_STATE_PAIRS[
            "deferred"
        ]
    elif action == "reject":
        target["review_status"], target["lifecycle_state"] = _TARGET_STATE_PAIRS[
            "rejected"
        ]
    elif action == "mark_duplicate":
        duplicate_target = _validated_duplicate_target(
            source, command, duplicate_target
        )
        target["review_status"], target["lifecycle_state"] = _TARGET_STATE_PAIRS[
            "duplicate"
        ]
    elif action == "mark_split_required":
        target["review_status"], target["lifecycle_state"] = _TARGET_STATE_PAIRS[
            "split_required"
        ]
    elif action == "rename_candidate_metadata":
        requested_label = command["requested_owner_visible_label"]
        if requested_label == source.get("owner_visible_label"):
            raise _transition_error(command, "rename must change owner-visible metadata")
        target["review_status"] = "correction_recorded"
        target["lifecycle_state"] = "rename_metadata_recorded"
    elif action == "record_source_linkage_correction":
        requested_locator = command["requested_source_locator"]
        if requested_locator == source["source_locator"]:
            raise _transition_error(command, "source-link correction must change linkage")
        target["review_status"] = "correction_recorded"
        target["lifecycle_state"] = "source_linkage_correction_recorded"
    elif action == "mark_superseded":
        superseding_target = _validated_superseding_target(
            source, command, superseding_target
        )
        target["review_status"], target["lifecycle_state"] = _TARGET_STATE_PAIRS[
            "superseded"
        ]
    elif action == "record_owner_authored_correction":
        target["review_status"] = "correction_recorded"
        target["lifecycle_state"] = "owner_authored_correction_recorded"
    elif action == "request_rerun_selected_source":
        if (
            command["prior_source_locator"] != source["source_locator"]
            or command["selected_source_locator"] != source["source_locator"]
        ):
            raise _transition_error(
                command, "rerun-selected-source linkage mismatch"
            )
        target["review_status"] = "needs_info"
        target["lifecycle_state"] = "rerun_selected_source_requested"
    elif action == "quarantine":
        target["review_status"], target["lifecycle_state"] = (
            "needs_info",
            "blocked_invalid_support",
        )

    if state_change:
        previous_pair = source_pair
        target_pair = (target["review_status"], target["lifecycle_state"])
        for field in (
            "duplicate_candidate_ids",
            "duplicate_target_queue_entry_id",
            "duplicate_target_review_status",
            "duplicate_target_lifecycle_state",
            "duplicate_target_review_version",
            "superseded_by_candidate_id",
            "superseding_target_queue_entry_id",
            "superseding_target_review_status",
            "superseding_target_lifecycle_state",
            "superseding_target_review_version",
            "owner_authored_correction",
            "rejected_output_reason",
            "insufficient_evidence_reason",
            "quarantine_note",
            "original_owner_visible_label",
            "requested_owner_visible_label",
            "original_source_locator",
            "requested_source_locator",
            "prior_analysis_run_id",
            "prior_analysis_run_manifest_hash",
            "prior_source_snapshot_id",
            "prior_source_hash",
            "prior_source_locator",
            "selected_source_locator",
            "prior_run_lineage_verification",
        ):
            target[field] = None
        target["owner_review_completed"] = False
        target["owner_reviewed_at"] = None

        if target_pair == ("needs_info", "needs_more_evidence"):
            supplied = command.get("insufficient_evidence_reason")
            if supplied is not None:
                target["insufficient_evidence_reason"] = supplied
            elif previous_pair == target_pair:
                target["insufficient_evidence_reason"] = source.get(
                    "insufficient_evidence_reason"
                )
        elif target_pair == ("needs_info", "blocked_invalid_support"):
            supplied = command.get("quarantine_note")
            if supplied is not None:
                target["quarantine_note"] = supplied
            elif previous_pair == target_pair:
                target["quarantine_note"] = source.get("quarantine_note")
        elif target_pair == ("rejected", "owner_reviewed_rejected"):
            supplied = command.get("rejected_output_reason")
            if supplied is not None:
                target["rejected_output_reason"] = supplied
            elif previous_pair == target_pair:
                target["rejected_output_reason"] = source.get(
                    "rejected_output_reason"
                )
        elif target_pair == ("duplicate", "duplicate_candidate"):
            target["duplicate_candidate_ids"] = deepcopy(
                command["duplicate_candidate_ids"]
            )
            target["duplicate_target_queue_entry_id"] = duplicate_target[
                "queue_entry_id"
            ]
            target["duplicate_target_review_status"] = duplicate_target[
                "review_status"
            ]
            target["duplicate_target_lifecycle_state"] = duplicate_target[
                "lifecycle_state"
            ]
            target["duplicate_target_review_version"] = duplicate_target[
                "review_version"
            ]
        elif target_pair == ("superseded", "superseded_candidate"):
            target["superseded_by_candidate_id"] = command[
                "superseded_by_candidate_id"
            ]
            target["superseding_target_queue_entry_id"] = superseding_target[
                "queue_entry_id"
            ]
            target["superseding_target_review_status"] = superseding_target[
                "review_status"
            ]
            target["superseding_target_lifecycle_state"] = superseding_target[
                "lifecycle_state"
            ]
            target["superseding_target_review_version"] = superseding_target[
                "review_version"
            ]
        elif target_pair == ("correction_recorded", "rename_metadata_recorded"):
            target["original_owner_visible_label"] = source.get(
                "owner_visible_label"
            )
            target["requested_owner_visible_label"] = command[
                "requested_owner_visible_label"
            ]
            target["owner_visible_label"] = command["requested_owner_visible_label"]
        elif target_pair == (
            "correction_recorded",
            "source_linkage_correction_recorded",
        ):
            target["original_source_locator"] = deepcopy(source["source_locator"])
            target["requested_source_locator"] = deepcopy(
                command["requested_source_locator"]
            )
        elif target_pair == (
            "correction_recorded",
            "owner_authored_correction_recorded",
        ):
            target["owner_authored_correction"] = command[
                "owner_authored_correction"
            ]
        elif target_pair == ("needs_info", "rerun_selected_source_requested"):
            for field in (
                "prior_analysis_run_id",
                "prior_analysis_run_manifest_hash",
                "prior_source_snapshot_id",
                "prior_source_hash",
                "prior_source_locator",
                "selected_source_locator",
            ):
                target[field] = deepcopy(command[field])
            target["prior_run_lineage_verification"] = (
                "verified_analysis_run_manifest"
            )

    if action in {
        "approve",
        "reject",
        "mark_duplicate",
        "mark_split_required",
        "rename_candidate_metadata",
        "record_source_linkage_correction",
        "mark_superseded",
        "record_owner_authored_correction",
    }:
        target["owner_review_completed"] = True
        target["owner_reviewed_at"] = command_time
    elif action == "mark_reviewed":
        target["owner_review_completed"] = True
        target["owner_reviewed_at"] = command_time
    if "owner_note" in command and command["owner_note"] is not None:
        if action == "update_owner_note" and command["owner_note"] == "":
            target["owner_note"] = None
        else:
            target["owner_note"] = command["owner_note"]
    if command.get("rationale") is not None:
        target["rationale"] = command["rationale"]

    target["review_version"] = source["review_version"] + 1
    target["updated_at"] = command_time
    try:
        return review_queue_storage.validate_review_queue_entry(target)
    except (TypeError, ValueError) as exc:
        raise _transition_error(command, "computed target queue entry is invalid") from exc


def _canonical_queue_bytes(queue_entry: dict[str, Any]) -> bytes:
    validated = review_queue_storage.validate_review_queue_entry(queue_entry)
    return apply_contract.canonical_json_bytes(validated)


def _canonical_queue_hash(queue_entry: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical_queue_bytes(queue_entry)).hexdigest()


def _linked_candidate_bytes_and_hash(
    queue_entry: dict[str, Any], *, project_dir: Path
) -> tuple[bytes, str]:
    candidate_id = queue_entry["candidate_record_id"]
    candidate = candidate_persistence.read_candidate_record(project_dir, candidate_id)
    if (
        candidate.get("candidate_id") != candidate_id
        or candidate.get("project_id") != queue_entry["project_id"]
    ):
        raise ValueError("candidate linkage mismatch")
    raw = apply_contract.canonical_json_bytes(candidate)
    return raw, hashlib.sha256(raw).hexdigest()


def _evidence_provenance_projection_hash(queue_entry: dict[str, Any]) -> str:
    projection = {
        field: deepcopy(queue_entry[field])
        for field in _EVIDENCE_PROVENANCE_PROJECTION_FIELDS
    }
    return hashlib.sha256(apply_contract.canonical_json_bytes(projection)).hexdigest()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace(
        "+00:00", "Z"
    )


def _read_current_queue_state(
    *, project_dir: Path, queue_entry_id: str
) -> tuple[dict[str, Any] | None, str | None]:
    try:
        queue_entry = review_queue_storage.read_review_queue_entry(
            queue_entry_id, project_dir=project_dir
        )
    except (OSError, TypeError, ValueError):
        return None, None
    return queue_entry, _canonical_queue_hash(queue_entry)


def _action_parts(
    chain: list[dict[str, Any]], intent: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    index = chain.index(intent)
    terminal = chain[index + 1] if index + 1 < len(chain) else None
    if terminal is not None and terminal.get("intent_event_hash") != intent["event_hash"]:
        terminal = None
    if terminal is not None and terminal["event_type"] == "action_failed":
        recovery = chain[index + 2] if index + 2 < len(chain) else None
        if recovery is not None and recovery.get("intent_event_hash") == intent["event_hash"]:
            terminal = recovery
    return intent, terminal


def _classify_existing_action(
    chain: list[dict[str, Any]],
    intent: dict[str, Any],
    current_queue_hash: str | None,
) -> tuple[str, dict[str, Any] | None]:
    index = chain.index(intent)
    next_event = chain[index + 1] if index + 1 < len(chain) else None
    if next_event is None or next_event.get("intent_event_hash") != intent["event_hash"]:
        if current_queue_hash == intent["queue_before_hash"]:
            return "R1", None
        if current_queue_hash == intent["target_queue_hash"]:
            return "R2", None
        return "R3", None
    if next_event["event_type"] == "action_failed":
        if not next_event["retryable"]:
            return "R6", next_event
        recovery = chain[index + 2] if index + 2 < len(chain) else None
        if recovery is not None and recovery.get("intent_event_hash") == intent["event_hash"]:
            if current_queue_hash == intent["target_queue_hash"]:
                return "R7", recovery
            return "R8", recovery
        if current_queue_hash == intent["queue_before_hash"]:
            return "R4", next_event
        if current_queue_hash == intent["target_queue_hash"]:
            return "R5", next_event
        return "R6", next_event
    if next_event["event_type"] == "action_completed":
        if current_queue_hash == intent["target_queue_hash"]:
            return "R7", next_event
        return "R8", next_event
    raise ValueError("invalid action event path")


def _manual_failure(
    message: str,
    *,
    error_code: str,
    intent: dict[str, Any] | None,
    extra: dict[str, Any] | None = None,
) -> ReviewActionPersistenceFailure:
    details = {"manual_recovery_required": True}
    if intent is not None:
        details["action_id"] = intent["action_id"]
    if extra:
        details.update(extra)
    request = None
    if intent is not None:
        request = {
            "action_type": intent["action_command"],
            "candidate_id": intent["candidate_record_id"],
        }
    return _command_error(
        ReviewActionPersistenceFailure,
        message,
        error_code=error_code,
        project_id=intent.get("project_id") if intent else None,
        queue_entry_id=intent.get("queue_entry_id") if intent else None,
        request=request,
        extra=details,
    )


def _decode_intent_target(intent: dict[str, Any]) -> dict[str, Any]:
    encoded = intent["target_queue_canonical_bytes_b64url"]
    padding = "=" * (-len(encoded) % 4)
    try:
        raw = base64.b64decode(encoded + padding, altchars=b"-_", validate=True)
        loaded = apply_contract.strict_json_loads(raw, max_bytes=4_194_304)
        target = review_queue_storage.validate_review_queue_entry(loaded)
    except (OSError, TypeError, ValueError) as exc:
        raise _manual_failure(
            "persisted action target is invalid",
            error_code="REVIEW_ACTION_INTENT_INTEGRITY_FAILURE",
            intent=intent,
        ) from exc
    if (
        apply_contract.canonical_json_bytes(target) != raw
        or hashlib.sha256(raw).hexdigest() != intent["target_queue_hash"]
    ):
        raise _manual_failure(
            "persisted action target is invalid",
            error_code="REVIEW_ACTION_INTENT_INTEGRITY_FAILURE",
            intent=intent,
        )
    return target


def _verify_after_hashes(
    intent: dict[str, Any], *, project_dir: Path
) -> tuple[dict[str, Any], str, str]:
    queue_entry, queue_hash = _read_current_queue_state(
        project_dir=project_dir, queue_entry_id=intent["queue_entry_id"]
    )
    if queue_entry is None or queue_hash != intent["target_queue_hash"]:
        raise _manual_failure(
            "target queue integrity verification failed",
            error_code="REVIEW_ACTION_QUEUE_INTEGRITY_FAILURE",
            intent=intent,
        )
    try:
        _, candidate_hash = _linked_candidate_bytes_and_hash(
            queue_entry, project_dir=project_dir
        )
        projection_hash = _evidence_provenance_projection_hash(queue_entry)
    except (OSError, TypeError, ValueError) as exc:
        raise _manual_failure(
            "candidate or evidence integrity verification failed",
            error_code="REVIEW_ACTION_TERMINAL_INTEGRITY_FAILURE",
            intent=intent,
        ) from exc
    if (
        candidate_hash != intent["candidate_before_hash"]
        or projection_hash != intent["evidence_projection_before_hash"]
    ):
        raise _manual_failure(
            "candidate or evidence integrity verification failed",
            error_code="REVIEW_ACTION_TERMINAL_INTEGRITY_FAILURE",
            intent=intent,
        )
    return queue_entry, candidate_hash, projection_hash


def _build_success_response(
    intent: dict[str, Any],
    completion: dict[str, Any],
    queue_entry: dict[str, Any],
    *,
    replay: bool,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "accepted",
        "replay": replay,
        "action_command": intent["action_command"],
        "action_id": intent["action_id"],
        "project_id": intent["project_id"],
        "queue_entry_id": intent["queue_entry_id"],
        "candidate_id": intent["candidate_record_id"],
        "review_status": queue_entry["review_status"],
        "lifecycle_state": queue_entry["lifecycle_state"],
        "review_version": queue_entry["review_version"],
        "owner_review_completed": queue_entry["owner_review_completed"],
        "owner_reviewed_at": queue_entry["owner_reviewed_at"],
        "owner_note": queue_entry.get("owner_note"),
        "rationale": queue_entry.get("rationale"),
        "rejected_output_reason": queue_entry.get("rejected_output_reason"),
        "insufficient_evidence_reason": queue_entry.get(
            "insufficient_evidence_reason"
        ),
        "duplicate_candidate_ids": deepcopy(
            queue_entry.get("duplicate_candidate_ids")
        ),
        "duplicate_target_queue_entry_id": queue_entry.get(
            "duplicate_target_queue_entry_id"
        ),
        "duplicate_target_review_status": queue_entry.get(
            "duplicate_target_review_status"
        ),
        "duplicate_target_lifecycle_state": queue_entry.get(
            "duplicate_target_lifecycle_state"
        ),
        "duplicate_target_review_version": queue_entry.get(
            "duplicate_target_review_version"
        ),
        "owner_visible_label": queue_entry.get("owner_visible_label"),
        "original_owner_visible_label": queue_entry.get(
            "original_owner_visible_label"
        ),
        "requested_owner_visible_label": queue_entry.get(
            "requested_owner_visible_label"
        ),
        "original_source_locator": deepcopy(
            queue_entry.get("original_source_locator")
        ),
        "requested_source_locator": deepcopy(
            queue_entry.get("requested_source_locator")
        ),
        "superseded_by_candidate_id": queue_entry.get(
            "superseded_by_candidate_id"
        ),
        "superseding_target_queue_entry_id": queue_entry.get(
            "superseding_target_queue_entry_id"
        ),
        "superseding_target_review_status": queue_entry.get(
            "superseding_target_review_status"
        ),
        "superseding_target_lifecycle_state": queue_entry.get(
            "superseding_target_lifecycle_state"
        ),
        "superseding_target_review_version": queue_entry.get(
            "superseding_target_review_version"
        ),
        "owner_authored_correction": queue_entry.get(
            "owner_authored_correction"
        ),
        "prior_analysis_run_id": queue_entry.get("prior_analysis_run_id"),
        "prior_analysis_run_manifest_hash": queue_entry.get(
            "prior_analysis_run_manifest_hash"
        ),
        "prior_source_snapshot_id": queue_entry.get("prior_source_snapshot_id"),
        "prior_source_hash": queue_entry.get("prior_source_hash"),
        "prior_source_locator": deepcopy(queue_entry.get("prior_source_locator")),
        "selected_source_locator": deepcopy(
            queue_entry.get("selected_source_locator")
        ),
        "prior_run_lineage_verification": queue_entry.get(
            "prior_run_lineage_verification"
        ),
        "completion_event_hash": completion["event_hash"],
        "review_workflow_state": {
            "approval_scope": "review_lifecycle_metadata_only",
            "duplicate_linkage_scope": "review_lifecycle_metadata_only",
            "split_scope": "review_lifecycle_metadata_only",
            "rename_scope": "review_lifecycle_metadata_only",
            "source_linkage_correction_scope": "review_lifecycle_metadata_only",
            "supersede_scope": "review_lifecycle_metadata_only",
            "owner_authored_correction_scope": (
                "review_lifecycle_metadata_only"
            ),
            "rerun_request_scope": "review_lifecycle_metadata_only",
            "is_canon": False,
            "candidate_record_mutation_performed": False,
            "target_candidate_mutation_performed": False,
            "source_candidate_deleted": False,
            "content_merge_performed": False,
            "content_split_performed": False,
            "split_target_records_created": False,
            "promotion_created": False,
            "apply_promotion_performed": False,
            "memory_canon_mutation_performed": False,
            "project_truth_mutation_performed": False,
            "raw_artifact_persistence_performed": False,
            "runtime_extraction_performed": False,
            "model_call_performed": False,
            "rerun_execution_performed": False,
            "candidate_generation_performed": False,
            "generated_prose_performed": False,
            "owner_authored_correction_performed": (
                intent["action_command"] == "record_owner_authored_correction"
            ),
            "source_linkage_mutation_performed": False,
            "source_document_mutation_performed": False,
            "training_artifact_performed": False,
        },
        "warnings": [
            "accepted as review workflow state only; not canon and no promotion performed"
        ],
        "errors": [],
    }


def _publish_completion(
    intent: dict[str, Any],
    *,
    project_dir: Path,
    failed: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    queue_entry, candidate_hash, projection_hash = _verify_after_hashes(
        intent, project_dir=project_dir
    )
    completed_at = _utc_now()
    if failed is None:
        completion = review_action_events.build_action_completed_event_v1(
            intent=intent,
            queue_after_hash=intent["target_queue_hash"],
            candidate_after_hash=candidate_hash,
            evidence_projection_after_hash=projection_hash,
            completed_at=completed_at,
        )
    else:
        completion = review_action_events.build_action_recovery_completed_event_v1(
            intent=intent,
            failed=failed,
            queue_after_hash=intent["target_queue_hash"],
            candidate_after_hash=candidate_hash,
            evidence_projection_after_hash=projection_hash,
            completed_at=completed_at,
        )
    try:
        published = review_action_events.publish_review_action_event(
            completion,
            project_dir=project_dir,
            queue_entry_id=intent["queue_entry_id"],
        )
    except Exception as exc:
        raise _command_error(
            ReviewActionPersistenceFailure,
            "completion event publication failed",
            error_code="REVIEW_ACTION_COMPLETION_WRITE_FAILED",
            project_id=intent["project_id"],
            queue_entry_id=intent["queue_entry_id"],
            request={
                "action_type": intent["action_command"],
                "candidate_id": intent["candidate_record_id"],
            },
        ) from exc
    return queue_entry, published


def _recover_r1(intent: dict[str, Any], *, project_dir: Path) -> dict[str, Any]:
    target = _decode_intent_target(intent)
    try:
        review_queue_storage.replace_review_queue_entry_atomic(
            target, project_dir=project_dir
        )
    except Exception as exc:
        _publish_queue_write_failure(intent, exc, project_dir=project_dir)
    queue_entry, completion = _publish_completion(intent, project_dir=project_dir)
    return _build_success_response(intent, completion, queue_entry, replay=True)


def _recover_r2(intent: dict[str, Any], *, project_dir: Path) -> dict[str, Any]:
    _decode_intent_target(intent)
    queue_entry, completion = _publish_completion(intent, project_dir=project_dir)
    return _build_success_response(intent, completion, queue_entry, replay=True)


def _recover_r4(
    intent: dict[str, Any], failed: dict[str, Any], *, project_dir: Path
) -> dict[str, Any]:
    target = _decode_intent_target(intent)
    try:
        review_queue_storage.replace_review_queue_entry_atomic(
            target, project_dir=project_dir
        )
    except Exception as exc:
        raise _manual_failure(
            "retryable queue recovery write failed",
            error_code="REVIEW_ACTION_RECOVERY_WRITE_FAILED",
            intent=intent,
        ) from exc
    queue_entry, completion = _publish_completion(
        intent, failed=failed, project_dir=project_dir
    )
    return _build_success_response(intent, completion, queue_entry, replay=True)


def _recover_r5(
    intent: dict[str, Any], failed: dict[str, Any], *, project_dir: Path
) -> dict[str, Any]:
    _decode_intent_target(intent)
    queue_entry, completion = _publish_completion(
        intent, failed=failed, project_dir=project_dir
    )
    return _build_success_response(intent, completion, queue_entry, replay=True)


def _return_r6(
    intent: dict[str, Any], failed: dict[str, Any] | None
) -> None:
    extra = {"recovery_state": "R6"}
    if failed is not None:
        extra.update(
            {
                "failure_reason": failed.get("failure_reason"),
                "retryable": failed.get("retryable"),
                "failure_event_hash": failed.get("event_hash"),
            }
        )
    raise _manual_failure(
        "review action requires manual recovery",
        error_code="REVIEW_ACTION_MANUAL_RECOVERY_REQUIRED",
        intent=intent,
        extra=extra,
    )


def _return_r7_replay(
    intent: dict[str, Any], completion: dict[str, Any], *, project_dir: Path
) -> dict[str, Any]:
    queue_entry, candidate_hash, projection_hash = _verify_after_hashes(
        intent, project_dir=project_dir
    )
    if (
        completion["queue_after_hash"] != intent["target_queue_hash"]
        or completion["candidate_after_hash"] != candidate_hash
        or completion["evidence_projection_after_hash"] != projection_hash
    ):
        raise _manual_failure(
            "completion integrity verification failed",
            error_code="REVIEW_ACTION_TERMINAL_INTEGRITY_FAILURE",
            intent=intent,
        )
    return _build_success_response(intent, completion, queue_entry, replay=True)


def _return_r8(
    intent: dict[str, Any],
    completion: dict[str, Any],
    current_queue_hash: str | None,
) -> None:
    raise _manual_failure(
        "completed review action queue state does not match its durable target",
        error_code="REVIEW_ACTION_POST_COMPLETION_INTEGRITY_FAILURE",
        intent=intent,
        extra={
            "completion_event_hash": completion["event_hash"],
            "expected_queue_hash": intent["target_queue_hash"],
            "observed_queue_hash": current_queue_hash,
        },
    )


def _return_r9(
    *, project_id: str, queue_entry_id: str, request: dict[str, Any]
) -> None:
    raise _command_error(
        ReviewActionPersistenceFailure,
        "review action event chain is corrupt",
        error_code="REVIEW_ACTION_EVENT_CHAIN_CORRUPT",
        project_id=project_id,
        queue_entry_id=queue_entry_id,
        request=request,
        extra={"manual_recovery_required": True, "recovery_state": "R9"},
    )


def _publish_queue_write_failure(
    intent: dict[str, Any], failure: Exception, *, project_dir: Path
) -> None:
    queue_entry, observed_hash = _read_current_queue_state(
        project_dir=project_dir, queue_entry_id=intent["queue_entry_id"]
    )
    if queue_entry is not None and observed_hash == intent["queue_before_hash"]:
        reason, retryable = "QUEUE_WRITE_FAILED", True
    elif queue_entry is not None and observed_hash == intent["target_queue_hash"]:
        reason, retryable = "QUEUE_WRITE_PARTIAL", True
    else:
        reason, retryable = "QUEUE_STATE_CORRUPT", False
    detail = "atomic queue replacement failed ({0})".format(
        type(failure).__name__
    )[:2000]
    failed = review_action_events.build_action_failed_event_v1(
        intent=intent,
        failure_reason=reason,
        failure_detail=detail,
        observed_queue_hash=observed_hash,
        retryable=retryable,
        failed_at=_utc_now(),
    )
    try:
        review_action_events.publish_review_action_event(
            failed,
            project_dir=project_dir,
            queue_entry_id=intent["queue_entry_id"],
        )
    except Exception as exc:
        raise _command_error(
            ReviewActionPersistenceFailure,
            "queue write and failure-event publication failed",
            error_code="REVIEW_ACTION_FAILURE_EVENT_WRITE_FAILED",
            project_id=intent["project_id"],
            queue_entry_id=intent["queue_entry_id"],
            request={
                "action_type": intent["action_command"],
                "candidate_id": intent["candidate_record_id"],
            },
        ) from exc
    raise _command_error(
        ReviewActionPersistenceFailure,
        "queue replacement failed",
        error_code=reason,
        project_id=intent["project_id"],
        queue_entry_id=intent["queue_entry_id"],
        request={
            "action_type": intent["action_command"],
            "candidate_id": intent["candidate_record_id"],
        },
        extra={
            "manual_recovery_required": not retryable,
            "retryable": retryable,
            "observed_queue_hash": observed_hash,
        },
    )


def _enforce_chain_head_health(
    chain: list[dict[str, Any]],
    current_queue_hash: str | None,
    *,
    project_dir: Path,
) -> None:
    if not chain:
        return
    intent = next(
        (event for event in reversed(chain) if event["event_type"] == "action_intent"),
        None,
    )
    if intent is None:
        raise ValueError("event chain has no intent")
    state, terminal = _classify_existing_action(chain, intent, current_queue_hash)
    if state == "R7":
        _return_r7_replay(intent, terminal, project_dir=project_dir)
        return
    if state == "R8":
        _return_r8(intent, terminal, current_queue_hash)
    raise _manual_failure(
        "an earlier review action is unresolved",
        error_code="REVIEW_ACTION_PRIOR_ACTION_UNRESOLVED",
        intent=intent,
        extra={"recovery_state": state},
    )


def execute_review_action_command(
    request: Any,
    *,
    project_id: str,
    queue_entry_id: str,
    project_dir: Path,
    trusted_runtime_dir: Path,
) -> dict[str, Any]:
    valid = validate_review_action_command_request(
        request, project_id=project_id, queue_entry_id=queue_entry_id
    )
    record = build_canonical_review_action_request_record(
        valid, project_id=project_id, queue_entry_id=queue_entry_id
    )
    request_hash = hash_review_action_request(record)
    if not isinstance(project_dir, Path) or not isinstance(trusted_runtime_dir, Path):
        raise _command_error(
            ReviewActionUnprocessable,
            "invalid injected path",
            error_code="REVIEW_ACTION_INVALID_PATH",
            project_id=project_id,
            queue_entry_id=queue_entry_id,
            request=valid,
        )
    try:
        resolved_project_dir = project_dir.resolve(strict=True)
    except OSError as exc:
        raise _command_error(
            ReviewActionUnprocessable,
            "invalid project directory",
            error_code="REVIEW_ACTION_INVALID_PATH",
            project_id=project_id,
            queue_entry_id=queue_entry_id,
            request=valid,
        ) from exc
    if (
        resolved_project_dir != project_dir
        or not resolved_project_dir.is_dir()
        or not (resolved_project_dir / "project.json").is_file()
    ):
        raise _command_error(
            ReviewActionUnprocessable,
            "invalid project directory",
            error_code="REVIEW_ACTION_INVALID_PATH",
            project_id=project_id,
            queue_entry_id=queue_entry_id,
            request=valid,
        )

    try:
        lock = review_action_events.acquire_review_action_lock(
            trusted_runtime_dir=trusted_runtime_dir,
            project_id=project_id,
            queue_entry_id=queue_entry_id,
        )
        with lock:
            try:
                chain = review_action_events.scan_review_action_event_chain(
                    project_dir=resolved_project_dir,
                    project_id=project_id,
                    queue_entry_id=queue_entry_id,
                )
            except (OSError, TypeError, ValueError):
                _return_r9(
                    project_id=project_id,
                    queue_entry_id=queue_entry_id,
                    request=valid,
                )

            queue_entry, queue_hash = _read_current_queue_state(
                project_dir=resolved_project_dir, queue_entry_id=queue_entry_id
            )
            existing_intent = next(
                (
                    event
                    for event in chain
                    if event["event_type"] == "action_intent"
                    and event["idempotency_key"] == valid["idempotency_key"]
                ),
                None,
            )
            if existing_intent is not None:
                if existing_intent["request_hash"] != request_hash:
                    raise _command_error(
                        ReviewActionConflict,
                        "idempotency key was already used for another request",
                        error_code="REVIEW_ACTION_IDEMPOTENCY_CONFLICT",
                        project_id=project_id,
                        queue_entry_id=queue_entry_id,
                        request=valid,
                    )
                state, terminal = _classify_existing_action(
                    chain, existing_intent, queue_hash
                )
                if state == "R1":
                    return _recover_r1(existing_intent, project_dir=resolved_project_dir)
                if state == "R2":
                    return _recover_r2(existing_intent, project_dir=resolved_project_dir)
                if state == "R3":
                    failed = review_action_events.build_action_failed_event_v1(
                        intent=existing_intent,
                        failure_reason="QUEUE_STATE_CORRUPT",
                        failure_detail="intent-only queue state is missing, invalid, or unexpected",
                        observed_queue_hash=queue_hash,
                        retryable=False,
                        failed_at=_utc_now(),
                    )
                    try:
                        review_action_events.publish_review_action_event(
                            failed,
                            project_dir=resolved_project_dir,
                            queue_entry_id=queue_entry_id,
                        )
                    except Exception as exc:
                        raise _command_error(
                            ReviewActionPersistenceFailure,
                            "R3 failure event publication failed",
                            error_code="REVIEW_ACTION_FAILURE_EVENT_WRITE_FAILED",
                            project_id=project_id,
                            queue_entry_id=queue_entry_id,
                            request=valid,
                        ) from exc
                    raise _manual_failure(
                        "intent-only queue state requires manual recovery",
                        error_code="REVIEW_ACTION_MANUAL_RECOVERY_REQUIRED",
                        intent=existing_intent,
                        extra={
                            "recovery_state": "R3",
                            "failure_reason": failed["failure_reason"],
                            "failure_event_hash": failed["event_hash"],
                            "retryable": False,
                        },
                    )
                if state == "R4":
                    return _recover_r4(
                        existing_intent, terminal, project_dir=resolved_project_dir
                    )
                if state == "R5":
                    return _recover_r5(
                        existing_intent, terminal, project_dir=resolved_project_dir
                    )
                if state == "R6":
                    _return_r6(existing_intent, terminal)
                if state == "R7":
                    return _return_r7_replay(
                        existing_intent, terminal, project_dir=resolved_project_dir
                    )
                if state == "R8":
                    _return_r8(existing_intent, terminal, queue_hash)

            _enforce_chain_head_health(
                chain, queue_hash, project_dir=resolved_project_dir
            )
            if queue_entry is None:
                entry_path = review_queue_storage.review_queue_entry_path(
                    resolved_project_dir, queue_entry_id
                )
                error_type = (
                    ReviewActionNotFound
                    if not entry_path.exists()
                    else ReviewActionPersistenceFailure
                )
                raise _command_error(
                    error_type,
                    "queue entry was not found"
                    if error_type is ReviewActionNotFound
                    else "persisted queue entry is invalid",
                    error_code="REVIEW_ACTION_QUEUE_ENTRY_NOT_FOUND"
                    if error_type is ReviewActionNotFound
                    else "REVIEW_ACTION_QUEUE_STATE_INVALID",
                    project_id=project_id,
                    queue_entry_id=queue_entry_id,
                    request=valid,
                )
            if queue_entry.get("project_id") != project_id:
                raise _command_error(
                    ReviewActionUnprocessable,
                    "queue/project linkage mismatch",
                    error_code="REVIEW_ACTION_INVALID_LINKAGE",
                    project_id=project_id,
                    queue_entry_id=queue_entry_id,
                    request=valid,
                )
            if queue_entry.get("candidate_record_id") != valid["candidate_id"]:
                raise _command_error(
                    ReviewActionUnprocessable,
                    "queue/candidate linkage mismatch",
                    error_code="REVIEW_ACTION_INVALID_LINKAGE",
                    project_id=project_id,
                    queue_entry_id=queue_entry_id,
                    request=valid,
                )
            if (
                queue_entry["review_status"]
                != valid["expected_current_review_status"]
                or queue_entry["review_version"] != valid["expected_current_version"]
            ):
                raise _command_error(
                    ReviewActionConflict,
                    "stale review status or version",
                    error_code="REVIEW_ACTION_STALE_STATE",
                    project_id=project_id,
                    queue_entry_id=queue_entry_id,
                    request=valid,
                )
            try:
                _, candidate_hash = _linked_candidate_bytes_and_hash(
                    queue_entry, project_dir=resolved_project_dir
                )
                projection_hash = _evidence_provenance_projection_hash(queue_entry)
            except (OSError, TypeError, ValueError) as exc:
                raise _command_error(
                    ReviewActionUnprocessable,
                    "linked candidate or evidence provenance is invalid",
                    error_code="REVIEW_ACTION_INVALID_LINKAGE",
                    project_id=project_id,
                    queue_entry_id=queue_entry_id,
                    request=valid,
                ) from exc

            duplicate_target = None
            if valid["action_type"] == "mark_duplicate":
                target_queue_entry_id = valid["duplicate_target_queue_entry_id"]
                try:
                    duplicate_target = review_queue_storage.read_review_queue_entry(
                        target_queue_entry_id,
                        project_dir=resolved_project_dir,
                    )
                except (OSError, TypeError, ValueError) as exc:
                    target_path = review_queue_storage.review_queue_entry_path(
                        resolved_project_dir, target_queue_entry_id
                    )
                    error_type = (
                        ReviewActionNotFound
                        if not target_path.exists()
                        else ReviewActionUnprocessable
                    )
                    raise _command_error(
                        error_type,
                        "duplicate target queue entry was not found"
                        if error_type is ReviewActionNotFound
                        else "duplicate target queue entry is invalid",
                        error_code="REVIEW_ACTION_DUPLICATE_TARGET_NOT_FOUND"
                        if error_type is ReviewActionNotFound
                        else "REVIEW_ACTION_INVALID_DUPLICATE_TARGET",
                        project_id=project_id,
                        queue_entry_id=queue_entry_id,
                        request=valid,
                    ) from exc
                try:
                    _linked_candidate_bytes_and_hash(
                        duplicate_target, project_dir=resolved_project_dir
                    )
                    _evidence_provenance_projection_hash(duplicate_target)
                except (OSError, TypeError, ValueError) as exc:
                    raise _command_error(
                        ReviewActionUnprocessable,
                        "duplicate target candidate or support linkage is invalid",
                        error_code="REVIEW_ACTION_INVALID_DUPLICATE_TARGET",
                        project_id=project_id,
                        queue_entry_id=queue_entry_id,
                        request=valid,
                    ) from exc

            superseding_target = None
            if valid["action_type"] == "mark_superseded":
                target_queue_entry_id = valid[
                    "superseding_target_queue_entry_id"
                ]
                try:
                    superseding_target = review_queue_storage.read_review_queue_entry(
                        target_queue_entry_id,
                        project_dir=resolved_project_dir,
                    )
                except (OSError, TypeError, ValueError) as exc:
                    target_path = review_queue_storage.review_queue_entry_path(
                        resolved_project_dir, target_queue_entry_id
                    )
                    error_type = (
                        ReviewActionNotFound
                        if not target_path.exists()
                        else ReviewActionUnprocessable
                    )
                    raise _command_error(
                        error_type,
                        "superseding target queue entry was not found"
                        if error_type is ReviewActionNotFound
                        else "superseding target queue entry is invalid",
                        error_code="REVIEW_ACTION_SUPERSEDING_TARGET_NOT_FOUND"
                        if error_type is ReviewActionNotFound
                        else "REVIEW_ACTION_INVALID_SUPERSEDING_TARGET",
                        project_id=project_id,
                        queue_entry_id=queue_entry_id,
                        request=valid,
                    ) from exc
                try:
                    _linked_candidate_bytes_and_hash(
                        superseding_target, project_dir=resolved_project_dir
                    )
                    _evidence_provenance_projection_hash(superseding_target)
                except (OSError, TypeError, ValueError) as exc:
                    raise _command_error(
                        ReviewActionUnprocessable,
                        "superseding target candidate or support linkage is invalid",
                        error_code="REVIEW_ACTION_INVALID_SUPERSEDING_TARGET",
                        project_id=project_id,
                        queue_entry_id=queue_entry_id,
                        request=valid,
                    ) from exc
            if valid["action_type"] == "request_rerun_selected_source":
                _validate_prior_run_lineage(
                    queue_entry,
                    valid,
                    project_dir=resolved_project_dir,
                )
            command_time = _utc_now()
            target = compute_review_queue_transition(
                queue_entry,
                valid,
                command_time=command_time,
                duplicate_target=duplicate_target,
                superseding_target=superseding_target,
            )
            target_bytes = _canonical_queue_bytes(target)
            target_hash = hashlib.sha256(target_bytes).hexdigest()
            action_id = "rvact_" + uuid.uuid4().hex
            intent = review_action_events.build_action_intent_event_v1(
                sequence=len(chain) + 1,
                previous_event_hash=chain[-1]["event_hash"] if chain else None,
                project_id=project_id,
                queue_entry_id=queue_entry_id,
                candidate_record_id=valid["candidate_id"],
                action_command=valid["action_type"],
                action_id=action_id,
                idempotency_key=valid["idempotency_key"],
                request_hash=request_hash,
                created_at=command_time,
                queue_before_hash=queue_hash,
                target_queue_canonical_bytes_b64url=base64.urlsafe_b64encode(
                    target_bytes
                ).rstrip(b"=").decode("ascii"),
                target_queue_hash=target_hash,
                candidate_before_hash=candidate_hash,
                evidence_projection_before_hash=projection_hash,
                predecessor=chain[-1] if chain else None,
            )
            try:
                intent = review_action_events.publish_review_action_event(
                    intent,
                    project_dir=resolved_project_dir,
                    queue_entry_id=queue_entry_id,
                )
            except Exception as exc:
                raise _command_error(
                    ReviewActionPersistenceFailure,
                    "intent event publication failed",
                    error_code="REVIEW_ACTION_INTENT_WRITE_FAILED",
                    project_id=project_id,
                    queue_entry_id=queue_entry_id,
                    request=valid,
                ) from exc
            try:
                review_queue_storage.replace_review_queue_entry_atomic(
                    target, project_dir=resolved_project_dir
                )
            except Exception as exc:
                _publish_queue_write_failure(
                    intent, exc, project_dir=resolved_project_dir
                )
            persisted, completion = _publish_completion(
                intent, project_dir=resolved_project_dir
            )
            return _build_success_response(
                intent, completion, persisted, replay=False
            )
    except BlockingIOError as exc:
        raise _command_error(
            ReviewActionLockUnavailable,
            "review action lock is unavailable",
            error_code="REVIEW_ACTION_LOCK_UNAVAILABLE",
            project_id=project_id,
            queue_entry_id=queue_entry_id,
            request=valid,
        ) from exc
    except ReviewActionCommandError:
        raise
    except (OSError, TypeError, ValueError) as exc:
        raise _command_error(
            ReviewActionPersistenceFailure,
            "review action runtime or persistence integrity failure",
            error_code="REVIEW_ACTION_PERSISTENCE_FAILURE",
            project_id=project_id,
            queue_entry_id=queue_entry_id,
            request=valid,
        ) from exc


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
    if value["action_command"] == "mark_duplicate":
        required = {
            "duplicate_candidate_ids",
            "duplicate_target_queue_entry_id",
            "duplicate_target_expected_review_status",
            "duplicate_target_expected_version",
        }
        if not required <= set(value):
            raise ValueError("invalid request")
        duplicate_ids = value["duplicate_candidate_ids"]
        if (
            len(duplicate_ids) != 1
            or duplicate_ids[0] == value["candidate_record_id"]
            or value["duplicate_target_queue_entry_id"] == value["queue_entry_id"]
            or value["duplicate_target_expected_review_status"]
            not in _REVIEW_STATUSES
        ):
            raise ValueError("invalid request")
        target_version = value["duplicate_target_expected_version"]
        if (
            isinstance(target_version, bool)
            or not isinstance(target_version, int)
            or not 0 <= target_version <= _MAX_REVIEW_VERSION
        ):
            raise ValueError("invalid request")
    if value["action_command"] == "rename_candidate_metadata":
        _require_owner_visible_label(value.get("requested_owner_visible_label"))
    if value["action_command"] == "record_source_linkage_correction":
        locator = candidate_record.validate_source_locator(
            value.get("requested_source_locator")
        )
        if locator["project_id"] != value["project_id"]:
            raise ValueError("invalid request")
    if value["action_command"] == "mark_superseded":
        required = {
            "superseded_by_candidate_id",
            "superseding_target_queue_entry_id",
            "superseding_target_expected_review_status",
            "superseding_target_expected_version",
        }
        if not required <= set(value):
            raise ValueError("invalid request")
        if (
            value["superseded_by_candidate_id"] == value["candidate_record_id"]
            or value["superseding_target_queue_entry_id"]
            == value["queue_entry_id"]
            or value["superseding_target_expected_review_status"]
            not in _REVIEW_STATUSES
        ):
            raise ValueError("invalid request")
        target_version = value["superseding_target_expected_version"]
        if (
            isinstance(target_version, bool)
            or not isinstance(target_version, int)
            or not 0 <= target_version <= _MAX_REVIEW_VERSION
        ):
            raise ValueError("invalid request")
    if value["action_command"] == "record_owner_authored_correction":
        correction = _require_unicode_scalar_text(
            value.get("owner_authored_correction"),
            maximum=10_000,
            allow_null=False,
        )
        if not correction.strip():
            raise ValueError("invalid request")
    if value["action_command"] == "request_rerun_selected_source":
        required = {
            "prior_analysis_run_id",
            "prior_analysis_run_manifest_hash",
            "prior_source_snapshot_id",
            "prior_source_hash",
            "prior_source_locator",
            "selected_source_locator",
        }
        if not required <= set(value):
            raise ValueError("invalid request")
        _safe_id(value["prior_analysis_run_id"])
        _safe_id(value["prior_source_snapshot_id"])
        _require_sha256(value["prior_analysis_run_manifest_hash"])
        prior_source_hash = _require_sha256(value["prior_source_hash"])
        prior_locator = candidate_record.validate_source_locator(
            value["prior_source_locator"]
        )
        selected_locator = candidate_record.validate_source_locator(
            value["selected_source_locator"]
        )
        if (
            prior_locator["project_id"] != value["project_id"]
            or selected_locator["project_id"] != value["project_id"]
            or prior_locator != selected_locator
            or prior_locator.get("source_hash") not in {None, prior_source_hash}
        ):
            raise ValueError("invalid request")
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
