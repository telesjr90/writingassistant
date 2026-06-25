"""Pure helpers for Writer Assistant Core review queue storage."""

import copy
import json
from datetime import datetime, timezone
from pathlib import Path

from backend.story_knowledge import candidate_record
from backend.story_knowledge import candidate_review_gate
from backend.story_knowledge import candidate_schema

_INDEX_SCHEMA_VERSION = 1

_REQUIRED_ENTRY_FIELDS = frozenset(
    {
        "queue_entry_id",
        "project_id",
        "candidate_record_id",
        "candidate_type",
        "target_category",
        "review_status",
        "lifecycle_state",
        "source_document",
        "source_locator",
        "evidence_summary",
        "evidence_refs",
        "provenance_summary",
        "provenance_refs",
        "confidence",
        "uncertainty_flags",
        "normalization_status",
        "raw_output_refs",
        "human_review_required",
        "created_at",
        "updated_at",
    }
)

_OPTIONAL_ENTRY_FIELDS = frozenset(
    {
        "group_key",
        "sort_key",
        "priority_reason",
        "reviewer_notes",
        "owner_visible_label",
        "related_candidate_ids",
        "conflict_candidate_ids",
        "duplicate_candidate_ids",
        "insufficient_evidence_reason",
        "rejected_output_reason",
        "storage_version",
        "entry_hash",
        "candidate_snapshot_hash",
    }
)

_ALLOWED_REVIEW_STATUS = frozenset(
    {
        "pending",
        "needs_info",
        "rejected",
        "deferred",
        "duplicate",
        "superseded",
        "archived",
    }
)

_ALLOWED_LIFECYCLE_STATES = frozenset(
    {
        "draft_ready_for_review",
        "needs_more_evidence",
        "blocked_invalid_support",
        "owner_review_pending",
        "owner_reviewed_rejected",
        "owner_reviewed_deferred",
        "duplicate_candidate",
        "superseded_candidate",
        "archived_without_promotion",
    }
)

_NON_CANDIDATE_STATUS = frozenset({"approved", "promoted"})
_NON_CANDIDATE_OWNER_DECISION = frozenset({"approve", "promote"})

_OWNER_ACTION_BASE_REQUIRED = frozenset(
    {
        "action_id",
        "project_id",
        "queue_entry_id",
        "candidate_record_id",
        "action_command",
        "resulting_review_status",
        "resulting_lifecycle_state",
        "acted_at",
        "reason_code",
        "reviewer_note",
        "source_document",
        "source_locator",
        "evidence_refs",
        "provenance_refs",
        "human_review_required",
        "no_promotion_performed",
        "no_memory_canon_mutation",
    }
)

_OWNER_ACTION_OPTIONAL = frozenset(
    {
        "actor_id",
        "actor_ref",
        "previous_review_status",
        "previous_lifecycle_state",
        "related_candidate_ids",
        "duplicate_candidate_ids",
        "superseded_by_candidate_id",
        "requested_evidence_note",
        "action_batch_id",
        "storage_version",
        "action_hash",
    }
)

_OWNER_ACTION_ALLOWED_COMMANDS = frozenset(
    {
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
)

_OWNER_ACTION_ID_FIELDS = (
    "action_id",
    "project_id",
    "queue_entry_id",
    "candidate_record_id",
)

_OWNER_ACTION_TEXT_FIELDS = (
    "acted_at",
    "reason_code",
    "reviewer_note",
    "source_document",
)


def _now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _as_path(project_dir):
    if isinstance(project_dir, Path):
        return project_dir
    return Path(project_dir)


def _require_safe_id(value):
    if not isinstance(value, str):
        raise ValueError("invalid field")
    if not value.strip():
        raise ValueError("invalid field")
    if value != value.strip():
        raise ValueError("invalid field")
    if value in (".", ".."):
        raise ValueError("invalid field")
    if "/" in value or "\\" in value:
        raise ValueError("invalid field")
    if "." in value:
        raise ValueError("invalid field")
    if value.startswith("/"):
        raise ValueError("invalid field")
    if len(value) >= 2 and value[1] == ":" and value[0].isalpha():
        raise ValueError("invalid field")
    return value


def _require_confidence(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("invalid field")
    if value < 0.0 or value > 1.0:
        raise ValueError("invalid field")
    return value


def _require_list(value):
    if not isinstance(value, list):
        raise ValueError("invalid field")
    return value


def _require_non_empty_string(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("invalid field")
    return value


def validate_review_queue_entry(entry):
    if not isinstance(entry, dict):
        raise ValueError("invalid input")
    working = copy.deepcopy(entry)

    allowed = _REQUIRED_ENTRY_FIELDS | _OPTIONAL_ENTRY_FIELDS
    for key in working:
        if key not in allowed:
            raise ValueError("invalid field")
    for field in _REQUIRED_ENTRY_FIELDS:
        if field not in working:
            raise ValueError("invalid field")

    _require_safe_id(working["queue_entry_id"])
    _require_safe_id(working["project_id"])
    _require_safe_id(working["candidate_record_id"])

    candidate_type = working["candidate_type"]
    if candidate_type not in candidate_schema.CORE_CANDIDATE_TYPES:
        raise ValueError("invalid field")
    expected_category = candidate_schema.CORE_CANDIDATE_TARGET_CATEGORIES.get(
        candidate_type
    )
    if working["target_category"] != expected_category:
        raise ValueError("invalid field")

    if working["review_status"] not in _ALLOWED_REVIEW_STATUS:
        raise ValueError("invalid field")
    if working["lifecycle_state"] not in _ALLOWED_LIFECYCLE_STATES:
        raise ValueError("invalid field")

    _require_confidence(working["confidence"])
    _require_non_empty_string(working["source_document"])

    candidate_record.validate_source_locator(working["source_locator"])

    if not isinstance(working["evidence_summary"], str):
        raise ValueError("invalid field")
    if not isinstance(working["provenance_summary"], str):
        raise ValueError("invalid field")

    _require_list(working["evidence_refs"])
    _require_list(working["provenance_refs"])
    _require_list(working["uncertainty_flags"])
    _require_list(working["raw_output_refs"])

    _require_non_empty_string(working["normalization_status"])

    if not isinstance(working["human_review_required"], bool):
        raise ValueError("invalid field")

    _require_non_empty_string(working["created_at"])
    _require_non_empty_string(working["updated_at"])

    return working


def build_review_queue_entry_from_candidate_record(candidate_record_payload, *, project_id):
    if not isinstance(candidate_record_payload, dict):
        raise ValueError("invalid input")

    validated = candidate_record.validate_candidate_record(candidate_record_payload)
    if validated["status"] in _NON_CANDIDATE_STATUS:
        raise ValueError("invalid input")
    if validated["owner_decision"] in _NON_CANDIDATE_OWNER_DECISION:
        raise ValueError("invalid input")

    _require_safe_id(project_id)

    entry = candidate_review_gate.build_review_queue_entry(validated, project_id=project_id)
    return validate_review_queue_entry(entry)


def review_queue_storage_dir(project_dir):
    return _as_path(project_dir) / "writer_assistant" / "review_queue"


def _entries_dir(project_dir):
    return review_queue_storage_dir(project_dir) / "entries"


def review_queue_entry_path(project_dir, queue_entry_id):
    safe_id = _require_safe_id(queue_entry_id)
    return _entries_dir(project_dir) / "{0}.json".format(safe_id)


def review_queue_index_path(project_dir):
    return review_queue_storage_dir(project_dir) / "index.json"


def write_review_queue_entry(entry, *, project_dir):
    validated = validate_review_queue_entry(entry)
    entry_path = review_queue_entry_path(project_dir, validated["queue_entry_id"])
    entry_path.parent.mkdir(parents=True, exist_ok=True)
    entry_path.write_text(
        json.dumps(validated, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return {
        "persisted": True,
        "queue_entry_id": validated["queue_entry_id"],
        "project_id": validated["project_id"],
        "candidate_record_id": validated["candidate_record_id"],
        "review_status": validated["review_status"],
        "lifecycle_state": validated["lifecycle_state"],
        "candidate_linked": True,
        "review_workflow_only": True,
    }


def _load_entry_object(path):
    raw_text = path.read_text(encoding="utf-8")
    try:
        loaded = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise ValueError("invalid input") from exc
    if not isinstance(loaded, dict):
        raise ValueError("invalid input")
    return loaded


def read_review_queue_entry(queue_entry_id, *, project_dir):
    entry_path = review_queue_entry_path(project_dir, queue_entry_id)
    if not entry_path.is_file():
        raise ValueError("invalid input")
    loaded = _load_entry_object(entry_path)
    validated = validate_review_queue_entry(loaded)
    if validated["queue_entry_id"] != queue_entry_id:
        raise ValueError("invalid field")
    return validated


def list_review_queue_entries(*, project_dir):
    entries_dir = _entries_dir(project_dir)
    if not entries_dir.exists():
        return []

    results = []
    for item in entries_dir.iterdir():
        if not item.is_file():
            continue
        if item.suffix != ".json":
            continue
        loaded = _load_entry_object(item)
        validated = validate_review_queue_entry(loaded)
        if item.stem != validated["queue_entry_id"]:
            raise ValueError("invalid field")
        results.append(validated)

    results.sort(key=lambda value: value["queue_entry_id"])
    return results


def _index_entry_summary(entry):
    return {
        "queue_entry_id": entry["queue_entry_id"],
        "candidate_record_id": entry["candidate_record_id"],
        "candidate_type": entry["candidate_type"],
        "target_category": entry["target_category"],
        "review_status": entry["review_status"],
        "lifecycle_state": entry["lifecycle_state"],
        "confidence": entry["confidence"],
        "normalization_status": entry["normalization_status"],
        "human_review_required": entry["human_review_required"],
        "updated_at": entry["updated_at"],
    }


def build_review_queue_index(entries, *, project_id):
    if not isinstance(entries, list):
        raise ValueError("invalid input")
    _require_safe_id(project_id)

    validated_entries = []
    for entry in entries:
        validated = validate_review_queue_entry(entry)
        if validated["project_id"] != project_id:
            raise ValueError("invalid field")
        validated_entries.append(validated)

    summaries = []
    counts_by_review_status = {}
    counts_by_lifecycle_state = {}
    counts_by_candidate_type = {}
    for validated in validated_entries:
        summaries.append(_index_entry_summary(validated))
        review_status = validated["review_status"]
        lifecycle_state = validated["lifecycle_state"]
        candidate_type = validated["candidate_type"]
        counts_by_review_status[review_status] = (
            counts_by_review_status.get(review_status, 0) + 1
        )
        counts_by_lifecycle_state[lifecycle_state] = (
            counts_by_lifecycle_state.get(lifecycle_state, 0) + 1
        )
        counts_by_candidate_type[candidate_type] = (
            counts_by_candidate_type.get(candidate_type, 0) + 1
        )

    summaries.sort(key=lambda value: value["queue_entry_id"])

    return {
        "schema_version": _INDEX_SCHEMA_VERSION,
        "project_id": project_id,
        "generated_at": _now_iso(),
        "entries": summaries,
        "counts_by_review_status": counts_by_review_status,
        "counts_by_lifecycle_state": counts_by_lifecycle_state,
        "counts_by_candidate_type": counts_by_candidate_type,
    }


def validate_owner_action_record(action):
    if not isinstance(action, dict):
        raise ValueError("invalid input")
    working = copy.deepcopy(action)

    allowed = _OWNER_ACTION_BASE_REQUIRED | _OWNER_ACTION_OPTIONAL
    for key in working:
        if key not in allowed:
            raise ValueError("invalid field")
    for field in _OWNER_ACTION_BASE_REQUIRED:
        if field not in working:
            raise ValueError("invalid field")
    if "actor_id" not in working and "actor_ref" not in working:
        raise ValueError("invalid field")

    for id_field in _OWNER_ACTION_ID_FIELDS:
        _require_safe_id(working[id_field])

    if working["action_command"] not in _OWNER_ACTION_ALLOWED_COMMANDS:
        raise ValueError("invalid field")
    if working["resulting_review_status"] not in _ALLOWED_REVIEW_STATUS:
        raise ValueError("invalid field")
    if working["resulting_lifecycle_state"] not in _ALLOWED_LIFECYCLE_STATES:
        raise ValueError("invalid field")

    if working["no_promotion_performed"] is not True:
        raise ValueError("invalid field")
    if working["no_memory_canon_mutation"] is not True:
        raise ValueError("invalid field")

    if not isinstance(working["human_review_required"], bool):
        raise ValueError("invalid field")

    candidate_record.validate_source_locator(working["source_locator"])
    _require_list(working["evidence_refs"])
    _require_list(working["provenance_refs"])

    for text_field in _OWNER_ACTION_TEXT_FIELDS:
        if not isinstance(working[text_field], str):
            raise ValueError("invalid field")

    return working


__all__ = (
    "validate_review_queue_entry",
    "build_review_queue_entry_from_candidate_record",
    "review_queue_storage_dir",
    "review_queue_entry_path",
    "review_queue_index_path",
    "write_review_queue_entry",
    "read_review_queue_entry",
    "list_review_queue_entries",
    "build_review_queue_index",
    "validate_owner_action_record",
)
