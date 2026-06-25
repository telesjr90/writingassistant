"""Contract tests for the future Writer Assistant Core review queue storage helper.

PHASE8-IMPL-012-T004 is tests-first only. The future pure review queue storage
module is imported normally so this targeted file is expected red (collection
ImportError) until PHASE8-IMPL-012-T005 creates it, if authorized:

- backend.story_knowledge.review_queue_storage

Expected future public APIs:

- validate_review_queue_entry(entry: dict) -> dict
- build_review_queue_entry_from_candidate_record(candidate_record: dict, *, project_id: str) -> dict
- review_queue_storage_dir(project_dir)
- review_queue_entry_path(project_dir, queue_entry_id: str)
- review_queue_index_path(project_dir)
- write_review_queue_entry(entry: dict, *, project_dir) -> dict
- read_review_queue_entry(queue_entry_id: str, *, project_dir) -> dict
- list_review_queue_entries(*, project_dir) -> list[dict]
- build_review_queue_index(entries: list[dict], *, project_id: str) -> dict
- validate_owner_action_record(action: dict) -> dict

These tests encode the PHASE8-IMPL-012-T002 review queue storage contract decision
and the PHASE8-IMPL-012-T003 owner action workflow boundary decision (which extend
the PHASE8-IMPL-011-T003 review queue data shape and lifecycle decision).

All fixtures are small, synthetic, owner-authored/test-fabricated dictionaries.
These tests do not install, import, or run BookNLP/spaCy; do not call models or
tools; do not write memory/canon/project source files; do not write raw artifacts;
do not write training/JSONL/dataset files; and do not perform apply-promotion.
Filesystem assertions use pytest tmp_path only.
"""

import copy
from pathlib import Path

import pytest

from backend.story_knowledge import candidate_record
from backend.story_knowledge import candidate_review_gate

# The future storage module is imported normally; expected red until T005 exists.
from backend.story_knowledge import review_queue_storage


# ---------------------------------------------------------------------------
# Contract constants
# ---------------------------------------------------------------------------

PROJECT_ID = "example"

EXPECTED_PUBLIC_API = (
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

# Required stored queue entry fields (PHASE8-IMPL-012-T002 decision, aligned with
# the PHASE8-IMPL-011-T003 in-memory queue entry shape).
REQUIRED_QUEUE_FIELDS = frozenset(
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

ALLOWED_REVIEW_STATUS_VALUES = frozenset(
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

ALLOWED_LIFECYCLE_STATES = frozenset(
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

# Forbidden queue entry fields (PHASE8-IMPL-012-T002 decision).
FORBIDDEN_QUEUE_FIELDS = (
    "owner_decision_approved",
    "owner_decision",
    "promoted",
    "approved",
    "canon",
    "memory_destination",
    "apply_promotion",
    "storyform_truth",
    "generated_prose",
    "rewrite",
    "continuation",
    "route_trigger",
    "ui_action_trigger",
    "runtime_tool_trigger",
    "model_call",
    "raw_artifact_write_intent",
    "training_destination",
    "jsonl_destination",
)

# Optional stored queue entry fields that must be accepted (PHASE8-IMPL-012-T002).
ALLOWED_OPTIONAL_QUEUE_FIELDS = {
    "reviewer_notes": "Owner has not reviewed this entry yet.",
    "group_key": "scene_001",
    "owner_visible_label": "Character support to review",
}

# Required owner action record fields (PHASE8-IMPL-012-T003 decision). The fixture
# carries actor_id (the actor_id-or-actor_ref requirement is exercised separately).
OWNER_ACTION_REQUIRED_FIELDS = frozenset(
    {
        "action_id",
        "project_id",
        "queue_entry_id",
        "candidate_record_id",
        "action_command",
        "resulting_review_status",
        "resulting_lifecycle_state",
        "actor_id",
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

OWNER_ACTION_ALLOWED_COMMANDS = (
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
)

OWNER_ACTION_FORBIDDEN_COMMANDS = (
    "approve_candidate",
    "promote_candidate",
    "write_to_memory",
    "write_to_canon",
    "apply_promotion",
    "generate_prose",
    "rewrite_source",
    "continue_scene",
    "run_extractor",
)

OWNER_ACTION_FORBIDDEN_STATES = (
    "approved",
    "promoted",
    "canon",
    "memory",
)

OWNER_ACTION_FORBIDDEN_FIELDS = (
    "approved",
    "promoted",
    "canon",
    "memory_destination",
    "apply_promotion",
    "storyform_truth",
    "bible_destination",
    "generated_prose",
    "rewrite",
    "continuation",
    "route_trigger",
    "ui_action_trigger",
    "runtime_tool_trigger",
    "model_call",
    "raw_artifact_write_intent",
    "training_destination",
    "jsonl_destination",
)

UNSAFE_ID_VALUES = (
    "../escape",
    "..",
    "/absolute",
    "C:\\escape",
    "folder/name",
    "folder\\name",
    ".hidden",
    "entry.json",
    "",
    "   ",
)

# Derived review queue index contract (PHASE8-IMPL-012-T002 decision).
REQUIRED_INDEX_FIELDS = frozenset(
    {
        "schema_version",
        "project_id",
        "entries",
        "counts_by_review_status",
        "counts_by_lifecycle_state",
        "counts_by_candidate_type",
    }
)

INDEX_TIMESTAMP_FIELDS = ("updated_at", "generated_at")

REQUIRED_INDEX_ENTRY_FIELDS = frozenset(
    {
        "queue_entry_id",
        "candidate_record_id",
        "candidate_type",
        "target_category",
        "review_status",
        "lifecycle_state",
        "confidence",
        "normalization_status",
        "human_review_required",
        "updated_at",
    }
)

# Recursive forbidden-term scan applied to built/validated entries, owner action
# records, and derived index payloads returned by the future storage helper.
FORBIDDEN_OUTPUT_TERMS = (
    "owner_decision_approved",
    "apply_promotion",
    "write_to_canon",
    "write_to_memory",
    "mutate_memory",
    "memory_destination",
    "storyform_truth",
    "generated_prose",
    "route_trigger",
    "ui_action_trigger",
    "runtime_tool_trigger",
    "model_call",
    "raw_artifact_write_intent",
    "training_destination",
    "jsonl_destination",
    "dataset_manifest",
)

# Forbidden runtime/tool/prose/mutation/UI/route terms for the future production
# storage module source (PHASE8-IMPL-012-T004 source-level boundary contract).
FORBIDDEN_PRODUCTION_SOURCE_TERMS = (
    "booknlp import",
    "from booknlp",
    "import booknlp",
    "spacy.load",
    "import spacy",
    "from spacy",
    "ollama",
    "openai",
    "requests",
    "httpx",
    "fastapi",
    "uvicorn",
    "subprocess",
    "frontend",
    "apply_promotion",
    "write_to_canon",
    "write_to_memory",
    "mutate_memory",
    "storyform_truth",
    "generated_prose",
    "rewrite",
    "continuation",
    "run_extractor",
    "route_trigger",
    "ui_action_trigger",
    "runtime_tool_trigger",
    "model_call",
    "training",
    "dataset_manifest",
    "jsonl",
)

# Project-relative paths the review queue storage helper must never create.
FORBIDDEN_PROJECT_PATHS = (
    "memory",
    "memory.json",
    "bible.json",
    "storyform.json",
    "project.json",
    "scenes",
    "chapters",
    "notes",
    "materials",
    "omi",
    "training",
    "dataset_manifest.json",
)

SAFE_CANDIDATE_ID = "core_candidate_scene_001_character_001"
SAFE_QUEUE_ENTRY_ID = "review_queue_entry_scene_001_character_001"
SAFE_ACTION_ID = "review_action_scene_001_character_001"


# ---------------------------------------------------------------------------
# Fixture builders (synthetic, owner-authored/test-fabricated)
# ---------------------------------------------------------------------------


def build_valid_source_locator(**overrides):
    locator = {
        "project_id": PROJECT_ID,
        "source_document_type": "scene",
        "source_document_id": "scene_001",
        "section_id": None,
        "chapter_id": None,
        "scene_id": "scene_001",
        "line_start": None,
        "line_end": None,
        "char_start": None,
        "char_end": None,
        "source_hash": None,
    }
    locator.update(overrides)
    return locator


def build_valid_provenance(**overrides):
    provenance = {
        "origin": "extractor",
        "extraction_method": "fixture_orchestrator",
        "timestamp": "2026-06-24T00:00:00Z",
        "human_review_required": True,
    }
    provenance.update(overrides)
    return provenance


def build_valid_candidate_record(**overrides):
    record = {
        "candidate_id": SAFE_CANDIDATE_ID,
        "project_id": PROJECT_ID,
        "candidate_type": "character_candidate",
        "status": "candidate",
        "target_category": "characters",
        "source_locator": build_valid_source_locator(),
        "evidence": [],
        "provenance": build_valid_provenance(),
        "owner_decision": "undecided",
        "destination": "omi_candidate_only",
        "confidence": 0.4,
        "created_at": "2026-06-24T00:00:00Z",
        "updated_at": "2026-06-24T00:00:00Z",
    }
    record.update(overrides)
    return record


def build_valid_queue_entry(**overrides):
    """Build a faithful queue entry using the completed PHASE8-IMPL-011 builder."""
    record = candidate_record.validate_candidate_record(build_valid_candidate_record())
    entry = candidate_review_gate.build_review_queue_entry(record, project_id=PROJECT_ID)
    entry.update(overrides)
    return entry


def build_valid_owner_action_record(**overrides):
    action = {
        "action_id": SAFE_ACTION_ID,
        "project_id": PROJECT_ID,
        "queue_entry_id": SAFE_QUEUE_ENTRY_ID,
        "candidate_record_id": SAFE_CANDIDATE_ID,
        "action_command": "reject_candidate",
        "resulting_review_status": "rejected",
        "resulting_lifecycle_state": "owner_reviewed_rejected",
        "actor_id": "owner_001",
        "acted_at": "2026-06-24T00:00:00Z",
        "reason_code": "insufficient_support",
        "reviewer_note": "Owner needs more evidence before review.",
        "source_document": "scene_001",
        "source_locator": build_valid_source_locator(),
        "evidence_refs": ["evidence_001"],
        "provenance_refs": ["extractor"],
        "human_review_required": True,
        "no_promotion_performed": True,
        "no_memory_canon_mutation": True,
    }
    action.update(overrides)
    return action


def project_dir(tmp_path: Path) -> Path:
    return tmp_path / "my-project"


def all_project_paths(project: Path):
    if not project.exists():
        return []
    return list(project.rglob("*"))


def assert_no_review_queue_dir(project: Path):
    assert not (project / "writer_assistant" / "review_queue").exists()


def assert_no_forbidden_paths(project: Path):
    for forbidden in FORBIDDEN_PROJECT_PATHS:
        assert not (project / forbidden).exists(), forbidden


def assert_no_forbidden_terms(payload, forbidden_terms):
    if isinstance(payload, dict):
        for key, value in payload.items():
            lowered_key = str(key).lower()
            for term in forbidden_terms:
                assert term not in lowered_key, (term, key)
            assert_no_forbidden_terms(value, forbidden_terms)
    elif isinstance(payload, list):
        for item in payload:
            assert_no_forbidden_terms(item, forbidden_terms)
    elif isinstance(payload, str):
        lowered_value = payload.lower()
        for term in forbidden_terms:
            assert term not in lowered_value, (term, payload)


# ---------------------------------------------------------------------------
# 1. Future module / API expectations
# ---------------------------------------------------------------------------


def test_future_public_api_symbols_are_present():
    for name in EXPECTED_PUBLIC_API:
        assert hasattr(review_queue_storage, name), name


def test_future_public_api_symbols_are_callable():
    for name in EXPECTED_PUBLIC_API:
        assert callable(getattr(review_queue_storage, name)), name


# ---------------------------------------------------------------------------
# 2. Queue entry validation
# ---------------------------------------------------------------------------


def test_validate_entry_accepts_valid_fixture_and_returns_new_dict():
    entry = build_valid_queue_entry()
    result = review_queue_storage.validate_review_queue_entry(entry)
    assert isinstance(result, dict)
    assert result is not entry
    assert REQUIRED_QUEUE_FIELDS.issubset(set(result))


def test_validate_entry_accepts_only_dict_input():
    for invalid in (None, [], (), "entry", 1, 1.5, True):
        with pytest.raises(ValueError):
            review_queue_storage.validate_review_queue_entry(invalid)


def test_validate_entry_does_not_mutate_caller_input():
    entry = build_valid_queue_entry()
    original = copy.deepcopy(entry)
    review_queue_storage.validate_review_queue_entry(entry)
    assert entry == original


def test_validate_entry_returned_copy_is_isolated_from_caller():
    entry = build_valid_queue_entry()
    result = review_queue_storage.validate_review_queue_entry(entry)
    entry["confidence"] = 0.99
    entry["source_locator"]["source_document_id"] = "mutated"
    assert result["confidence"] != 0.99
    assert result["source_locator"]["source_document_id"] == "scene_001"


@pytest.mark.parametrize("missing_field", sorted(REQUIRED_QUEUE_FIELDS))
def test_validate_entry_rejects_missing_required_field(missing_field):
    entry = build_valid_queue_entry()
    del entry[missing_field]
    with pytest.raises(ValueError):
        review_queue_storage.validate_review_queue_entry(entry)


def test_validate_entry_rejects_unknown_field():
    entry = build_valid_queue_entry(totally_unknown_field_xyz="blocked")
    with pytest.raises(ValueError):
        review_queue_storage.validate_review_queue_entry(entry)


@pytest.mark.parametrize("forbidden_field", FORBIDDEN_QUEUE_FIELDS)
def test_validate_entry_rejects_forbidden_fields(forbidden_field):
    entry = build_valid_queue_entry(**{forbidden_field: "blocked"})
    with pytest.raises(ValueError):
        review_queue_storage.validate_review_queue_entry(entry)


def test_validate_entry_accepts_allowed_optional_fields():
    entry = build_valid_queue_entry(**ALLOWED_OPTIONAL_QUEUE_FIELDS)
    result = review_queue_storage.validate_review_queue_entry(entry)
    for field in ALLOWED_OPTIONAL_QUEUE_FIELDS:
        assert field in result


@pytest.mark.parametrize("review_status", sorted(ALLOWED_REVIEW_STATUS_VALUES))
def test_validate_entry_accepts_allowed_review_status(review_status):
    entry = build_valid_queue_entry(review_status=review_status)
    result = review_queue_storage.validate_review_queue_entry(entry)
    assert result["review_status"] == review_status


@pytest.mark.parametrize("lifecycle_state", sorted(ALLOWED_LIFECYCLE_STATES))
def test_validate_entry_accepts_allowed_lifecycle_state(lifecycle_state):
    entry = build_valid_queue_entry(lifecycle_state=lifecycle_state)
    result = review_queue_storage.validate_review_queue_entry(entry)
    assert result["lifecycle_state"] == lifecycle_state


@pytest.mark.parametrize("bad_status", ("approved", "promoted", "canon", "unknown_status"))
def test_validate_entry_rejects_unsupported_review_status(bad_status):
    entry = build_valid_queue_entry(review_status=bad_status)
    with pytest.raises(ValueError):
        review_queue_storage.validate_review_queue_entry(entry)


@pytest.mark.parametrize(
    "bad_state", ("approved", "promoted", "canon", "owner_reviewed_approved", "unknown_state")
)
def test_validate_entry_rejects_unsupported_lifecycle_state(bad_state):
    entry = build_valid_queue_entry(lifecycle_state=bad_state)
    with pytest.raises(ValueError):
        review_queue_storage.validate_review_queue_entry(entry)


@pytest.mark.parametrize("invalid_confidence", (-0.01, 1.01, "high", True, None))
def test_validate_entry_rejects_invalid_confidence(invalid_confidence):
    entry = build_valid_queue_entry(confidence=invalid_confidence)
    with pytest.raises(ValueError):
        review_queue_storage.validate_review_queue_entry(entry)


@pytest.mark.parametrize("unsafe_value", UNSAFE_ID_VALUES)
def test_validate_entry_rejects_unsafe_queue_entry_id(unsafe_value):
    entry = build_valid_queue_entry(queue_entry_id=unsafe_value)
    with pytest.raises(ValueError):
        review_queue_storage.validate_review_queue_entry(entry)


@pytest.mark.parametrize("unsafe_value", UNSAFE_ID_VALUES)
def test_validate_entry_rejects_unsafe_project_id(unsafe_value):
    entry = build_valid_queue_entry(project_id=unsafe_value)
    with pytest.raises(ValueError):
        review_queue_storage.validate_review_queue_entry(entry)


@pytest.mark.parametrize("unsafe_value", UNSAFE_ID_VALUES)
def test_validate_entry_rejects_unsafe_candidate_record_id(unsafe_value):
    entry = build_valid_queue_entry(candidate_record_id=unsafe_value)
    with pytest.raises(ValueError):
        review_queue_storage.validate_review_queue_entry(entry)


def test_validate_entry_output_has_no_forbidden_terms():
    entry = build_valid_queue_entry()
    result = review_queue_storage.validate_review_queue_entry(entry)
    assert_no_forbidden_terms(result, FORBIDDEN_OUTPUT_TERMS)


# ---------------------------------------------------------------------------
# 3. Queue entry build from candidate record
# ---------------------------------------------------------------------------


def test_build_entry_from_candidate_returns_required_fields():
    record = candidate_record.validate_candidate_record(build_valid_candidate_record())
    entry = review_queue_storage.build_review_queue_entry_from_candidate_record(
        record, project_id=PROJECT_ID
    )
    assert isinstance(entry, dict)
    assert REQUIRED_QUEUE_FIELDS.issubset(set(entry))
    assert entry["project_id"] == PROJECT_ID
    assert entry["candidate_record_id"] == record["candidate_id"]
    assert entry["candidate_type"] == record["candidate_type"]
    assert entry["target_category"] == record["target_category"]


def test_build_entry_from_candidate_sets_pending_draft_lifecycle():
    record = candidate_record.validate_candidate_record(build_valid_candidate_record())
    entry = review_queue_storage.build_review_queue_entry_from_candidate_record(
        record, project_id=PROJECT_ID
    )
    assert entry["review_status"] == "pending"
    assert entry["lifecycle_state"] == "draft_ready_for_review"
    assert entry["review_status"] != "approved"


def test_build_entry_from_candidate_preserves_support_shapes():
    record = candidate_record.validate_candidate_record(build_valid_candidate_record())
    entry = review_queue_storage.build_review_queue_entry_from_candidate_record(
        record, project_id=PROJECT_ID
    )
    assert entry["confidence"] == record["confidence"]
    assert entry["source_document"] == record["source_locator"]["source_document_id"]
    assert isinstance(entry["evidence_refs"], list)
    assert isinstance(entry["provenance_refs"], list)
    assert isinstance(entry["uncertainty_flags"], list)
    assert isinstance(entry["raw_output_refs"], list)
    assert isinstance(entry["normalization_status"], str)
    assert entry["human_review_required"] is True


def test_build_entry_from_candidate_output_validates_and_has_no_forbidden_fields():
    record = candidate_record.validate_candidate_record(build_valid_candidate_record())
    entry = review_queue_storage.build_review_queue_entry_from_candidate_record(
        record, project_id=PROJECT_ID
    )
    validated = review_queue_storage.validate_review_queue_entry(entry)
    assert validated["candidate_record_id"] == record["candidate_id"]
    for forbidden in FORBIDDEN_QUEUE_FIELDS:
        assert forbidden not in entry
    assert_no_forbidden_terms(entry, FORBIDDEN_OUTPUT_TERMS)


def test_build_entry_from_candidate_does_not_mutate_caller_input():
    record = candidate_record.validate_candidate_record(build_valid_candidate_record())
    original = copy.deepcopy(record)
    review_queue_storage.build_review_queue_entry_from_candidate_record(
        record, project_id=PROJECT_ID
    )
    assert record == original


def test_build_entry_from_candidate_rejects_invalid_candidate_record():
    invalid = build_valid_candidate_record()
    del invalid["candidate_type"]
    with pytest.raises(ValueError):
        review_queue_storage.build_review_queue_entry_from_candidate_record(
            invalid, project_id=PROJECT_ID
        )


def test_build_entry_from_candidate_rejects_promoted_candidate_record():
    promoted = build_valid_candidate_record(status="promoted")
    with pytest.raises(ValueError):
        review_queue_storage.build_review_queue_entry_from_candidate_record(
            promoted, project_id=PROJECT_ID
        )


def test_build_entry_from_candidate_rejects_approved_candidate_record():
    approved = build_valid_candidate_record(status="approved", owner_decision="approve")
    with pytest.raises(ValueError):
        review_queue_storage.build_review_queue_entry_from_candidate_record(
            approved, project_id=PROJECT_ID
        )


@pytest.mark.parametrize("unsafe_value", UNSAFE_ID_VALUES)
def test_build_entry_from_candidate_rejects_unsafe_project_id(unsafe_value):
    record = candidate_record.validate_candidate_record(build_valid_candidate_record())
    with pytest.raises(ValueError):
        review_queue_storage.build_review_queue_entry_from_candidate_record(
            record, project_id=unsafe_value
        )


# ---------------------------------------------------------------------------
# 4. Storage path helpers (project-local only)
# ---------------------------------------------------------------------------


def test_review_queue_storage_dir_is_project_local(tmp_path):
    project = project_dir(tmp_path)
    storage_dir = Path(review_queue_storage.review_queue_storage_dir(project))
    assert storage_dir == project / "writer_assistant" / "review_queue"


def test_review_queue_entry_path_is_project_local(tmp_path):
    project = project_dir(tmp_path)
    entry_path = Path(
        review_queue_storage.review_queue_entry_path(project, SAFE_QUEUE_ENTRY_ID)
    )
    expected = (
        project
        / "writer_assistant"
        / "review_queue"
        / "entries"
        / f"{SAFE_QUEUE_ENTRY_ID}.json"
    )
    assert entry_path == expected


def test_review_queue_index_path_is_project_local(tmp_path):
    project = project_dir(tmp_path)
    index_path = Path(review_queue_storage.review_queue_index_path(project))
    assert index_path == project / "writer_assistant" / "review_queue" / "index.json"


@pytest.mark.parametrize("unsafe_value", UNSAFE_ID_VALUES)
def test_review_queue_entry_path_rejects_unsafe_id(tmp_path, unsafe_value):
    project = project_dir(tmp_path)
    with pytest.raises(ValueError):
        review_queue_storage.review_queue_entry_path(project, unsafe_value)


def test_review_queue_entry_path_rejects_nested_path_segments(tmp_path):
    project = project_dir(tmp_path)
    for unsafe in ("a/b", "a\\b", "../sibling", "nested/entry"):
        with pytest.raises(ValueError):
            review_queue_storage.review_queue_entry_path(project, unsafe)


# ---------------------------------------------------------------------------
# 5. Write / read / list / index (tmp_path only)
# ---------------------------------------------------------------------------


def test_write_review_queue_entry_persists_project_local_only(tmp_path):
    project = project_dir(tmp_path)
    entry = build_valid_queue_entry()
    result = review_queue_storage.write_review_queue_entry(entry, project_dir=project)
    assert isinstance(result, dict)

    entry_path = Path(
        review_queue_storage.review_queue_entry_path(project, entry["queue_entry_id"])
    )
    assert entry_path.exists()
    assert entry_path.is_file()
    assert "writer_assistant" in entry_path.parts
    assert "review_queue" in entry_path.parts
    assert "entries" in entry_path.parts
    assert_no_forbidden_paths(project)


def test_write_then_read_round_trips_a_valid_entry(tmp_path):
    project = project_dir(tmp_path)
    entry = build_valid_queue_entry()
    review_queue_storage.write_review_queue_entry(entry, project_dir=project)

    stored = review_queue_storage.read_review_queue_entry(
        entry["queue_entry_id"], project_dir=project
    )
    assert stored["queue_entry_id"] == entry["queue_entry_id"]
    assert stored["candidate_record_id"] == entry["candidate_record_id"]
    revalidated = review_queue_storage.validate_review_queue_entry(stored)
    assert revalidated["queue_entry_id"] == entry["queue_entry_id"]


def test_list_review_queue_entries_returns_valid_entries(tmp_path):
    project = project_dir(tmp_path)
    entry = build_valid_queue_entry()
    review_queue_storage.write_review_queue_entry(entry, project_dir=project)

    entries = review_queue_storage.list_review_queue_entries(project_dir=project)
    assert isinstance(entries, list)
    assert len(entries) == 1
    assert entries[0]["queue_entry_id"] == entry["queue_entry_id"]
    review_queue_storage.validate_review_queue_entry(entries[0])


def test_list_review_queue_entries_empty_when_no_queue(tmp_path):
    project = project_dir(tmp_path)
    entries = review_queue_storage.list_review_queue_entries(project_dir=project)
    assert entries == []
    assert_no_review_queue_dir(project)


def test_write_review_queue_entry_fails_closed_for_invalid_entry(tmp_path):
    project = project_dir(tmp_path)
    invalid = build_valid_queue_entry(review_status="approved")
    with pytest.raises(ValueError):
        review_queue_storage.write_review_queue_entry(invalid, project_dir=project)
    assert_no_review_queue_dir(project)
    assert_no_forbidden_paths(project)


@pytest.mark.parametrize("unsafe_value", UNSAFE_ID_VALUES)
def test_write_review_queue_entry_fails_closed_for_unsafe_id(tmp_path, unsafe_value):
    project = project_dir(tmp_path)
    invalid = build_valid_queue_entry(queue_entry_id=unsafe_value)
    with pytest.raises(ValueError):
        review_queue_storage.write_review_queue_entry(invalid, project_dir=project)
    assert_no_review_queue_dir(project)


def test_write_review_queue_entry_does_not_mutate_caller_input(tmp_path):
    project = project_dir(tmp_path)
    entry = build_valid_queue_entry()
    original = copy.deepcopy(entry)
    review_queue_storage.write_review_queue_entry(entry, project_dir=project)
    assert entry == original


def test_build_review_queue_index_returns_derived_summary():
    entry = build_valid_queue_entry()
    index = review_queue_storage.build_review_queue_index([entry], project_id=PROJECT_ID)
    assert isinstance(index, dict)
    assert REQUIRED_INDEX_FIELDS.issubset(set(index))
    assert index["project_id"] == PROJECT_ID
    assert any(field in index for field in INDEX_TIMESTAMP_FIELDS)
    assert isinstance(index["entries"], list)
    assert len(index["entries"]) == 1
    assert isinstance(index["counts_by_review_status"], dict)
    assert isinstance(index["counts_by_lifecycle_state"], dict)
    assert isinstance(index["counts_by_candidate_type"], dict)


def test_build_review_queue_index_entries_are_minimal():
    entry = build_valid_queue_entry()
    index = review_queue_storage.build_review_queue_index([entry], project_id=PROJECT_ID)
    summary = index["entries"][0]
    assert set(summary) == REQUIRED_INDEX_ENTRY_FIELDS
    assert summary["queue_entry_id"] == entry["queue_entry_id"]
    assert summary["candidate_record_id"] == entry["candidate_record_id"]


def test_build_review_queue_index_has_no_approval_or_promotion_fields():
    entry = build_valid_queue_entry()
    index = review_queue_storage.build_review_queue_index([entry], project_id=PROJECT_ID)
    assert_no_forbidden_terms(index, FORBIDDEN_OUTPUT_TERMS)
    for forbidden in ("approved", "promoted", "canon", "owner_decision_approved"):
        assert forbidden not in index


def test_build_review_queue_index_rejects_invalid_entries():
    invalid = build_valid_queue_entry(review_status="approved")
    with pytest.raises(ValueError):
        review_queue_storage.build_review_queue_index([invalid], project_id=PROJECT_ID)


@pytest.mark.parametrize("unsafe_value", UNSAFE_ID_VALUES)
def test_build_review_queue_index_rejects_unsafe_project_id(unsafe_value):
    entry = build_valid_queue_entry()
    with pytest.raises(ValueError):
        review_queue_storage.build_review_queue_index([entry], project_id=unsafe_value)


# ---------------------------------------------------------------------------
# 6. Owner action record validation (PHASE8-IMPL-012-T003 boundary)
# ---------------------------------------------------------------------------


def test_validate_owner_action_accepts_valid_fixture_and_returns_new_dict():
    action = build_valid_owner_action_record()
    result = review_queue_storage.validate_owner_action_record(action)
    assert isinstance(result, dict)
    assert result is not action
    assert OWNER_ACTION_REQUIRED_FIELDS.issubset(set(result))


def test_validate_owner_action_accepts_only_dict_input():
    for invalid in (None, [], (), "action", 1, 1.5, True):
        with pytest.raises(ValueError):
            review_queue_storage.validate_owner_action_record(invalid)


def test_validate_owner_action_does_not_mutate_caller_input():
    action = build_valid_owner_action_record()
    original = copy.deepcopy(action)
    review_queue_storage.validate_owner_action_record(action)
    assert action == original


def test_validate_owner_action_returned_copy_is_isolated_from_caller():
    action = build_valid_owner_action_record()
    result = review_queue_storage.validate_owner_action_record(action)
    action["reason_code"] = "mutated"
    action["source_locator"]["source_document_id"] = "mutated"
    assert result["reason_code"] == "insufficient_support"
    assert result["source_locator"]["source_document_id"] == "scene_001"


@pytest.mark.parametrize("missing_field", sorted(OWNER_ACTION_REQUIRED_FIELDS))
def test_validate_owner_action_rejects_missing_required_field(missing_field):
    action = build_valid_owner_action_record()
    del action[missing_field]
    with pytest.raises(ValueError):
        review_queue_storage.validate_owner_action_record(action)


def test_validate_owner_action_accepts_actor_ref_alternative():
    action = build_valid_owner_action_record()
    del action["actor_id"]
    action["actor_ref"] = "owner_session_001"
    result = review_queue_storage.validate_owner_action_record(action)
    assert result.get("actor_ref") == "owner_session_001"


def test_validate_owner_action_requires_some_actor_reference():
    action = build_valid_owner_action_record()
    del action["actor_id"]
    with pytest.raises(ValueError):
        review_queue_storage.validate_owner_action_record(action)


@pytest.mark.parametrize("command", OWNER_ACTION_ALLOWED_COMMANDS)
def test_validate_owner_action_accepts_allowed_commands(command):
    action = build_valid_owner_action_record(action_command=command)
    result = review_queue_storage.validate_owner_action_record(action)
    assert result["action_command"] == command


@pytest.mark.parametrize("command", OWNER_ACTION_FORBIDDEN_COMMANDS)
def test_validate_owner_action_rejects_forbidden_commands(command):
    action = build_valid_owner_action_record(action_command=command)
    with pytest.raises(ValueError):
        review_queue_storage.validate_owner_action_record(action)


def test_validate_owner_action_rejects_unknown_command():
    action = build_valid_owner_action_record(action_command="totally_unknown_command")
    with pytest.raises(ValueError):
        review_queue_storage.validate_owner_action_record(action)


@pytest.mark.parametrize("review_status", sorted(ALLOWED_REVIEW_STATUS_VALUES))
def test_validate_owner_action_accepts_allowed_resulting_review_status(review_status):
    action = build_valid_owner_action_record(resulting_review_status=review_status)
    result = review_queue_storage.validate_owner_action_record(action)
    assert result["resulting_review_status"] == review_status


@pytest.mark.parametrize("lifecycle_state", sorted(ALLOWED_LIFECYCLE_STATES))
def test_validate_owner_action_accepts_allowed_resulting_lifecycle_state(lifecycle_state):
    action = build_valid_owner_action_record(resulting_lifecycle_state=lifecycle_state)
    result = review_queue_storage.validate_owner_action_record(action)
    assert result["resulting_lifecycle_state"] == lifecycle_state


@pytest.mark.parametrize("bad_state", OWNER_ACTION_FORBIDDEN_STATES)
def test_validate_owner_action_rejects_forbidden_resulting_review_status(bad_state):
    action = build_valid_owner_action_record(resulting_review_status=bad_state)
    with pytest.raises(ValueError):
        review_queue_storage.validate_owner_action_record(action)


@pytest.mark.parametrize("bad_state", OWNER_ACTION_FORBIDDEN_STATES)
def test_validate_owner_action_rejects_forbidden_resulting_lifecycle_state(bad_state):
    action = build_valid_owner_action_record(resulting_lifecycle_state=bad_state)
    with pytest.raises(ValueError):
        review_queue_storage.validate_owner_action_record(action)


@pytest.mark.parametrize("bad_value", (False, "true", 1, None, 0))
def test_validate_owner_action_requires_no_promotion_performed_true(bad_value):
    action = build_valid_owner_action_record(no_promotion_performed=bad_value)
    with pytest.raises(ValueError):
        review_queue_storage.validate_owner_action_record(action)


@pytest.mark.parametrize("bad_value", (False, "true", 1, None, 0))
def test_validate_owner_action_requires_no_memory_canon_mutation_true(bad_value):
    action = build_valid_owner_action_record(no_memory_canon_mutation=bad_value)
    with pytest.raises(ValueError):
        review_queue_storage.validate_owner_action_record(action)


@pytest.mark.parametrize("forbidden_field", OWNER_ACTION_FORBIDDEN_FIELDS)
def test_validate_owner_action_rejects_forbidden_fields(forbidden_field):
    action = build_valid_owner_action_record(**{forbidden_field: "blocked"})
    with pytest.raises(ValueError):
        review_queue_storage.validate_owner_action_record(action)


def test_validate_owner_action_rejects_unknown_field():
    action = build_valid_owner_action_record(totally_unknown_field_xyz="blocked")
    with pytest.raises(ValueError):
        review_queue_storage.validate_owner_action_record(action)


@pytest.mark.parametrize(
    "id_field",
    ("action_id", "project_id", "queue_entry_id", "candidate_record_id"),
)
@pytest.mark.parametrize("unsafe_value", UNSAFE_ID_VALUES)
def test_validate_owner_action_rejects_unsafe_ids(id_field, unsafe_value):
    action = build_valid_owner_action_record(**{id_field: unsafe_value})
    with pytest.raises(ValueError):
        review_queue_storage.validate_owner_action_record(action)


@pytest.mark.parametrize("missing_support", ("source_locator", "evidence_refs", "provenance_refs"))
def test_validate_owner_action_requires_source_and_evidence_support(missing_support):
    action = build_valid_owner_action_record()
    del action[missing_support]
    with pytest.raises(ValueError):
        review_queue_storage.validate_owner_action_record(action)


def test_validate_owner_action_output_has_no_forbidden_terms():
    action = build_valid_owner_action_record()
    result = review_queue_storage.validate_owner_action_record(action)
    assert_no_forbidden_terms(result, FORBIDDEN_OUTPUT_TERMS)


# ---------------------------------------------------------------------------
# 7. Fail-closed matrices
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "mutate",
    [
        pytest.param(lambda e: e.update(review_status="approved"), id="approved_review_status"),
        pytest.param(lambda e: e.update(lifecycle_state="owner_reviewed_approved"), id="approved_lifecycle"),
        pytest.param(lambda e: e.pop("source_locator"), id="missing_source_locator"),
        pytest.param(lambda e: e.pop("evidence_refs"), id="missing_evidence_refs"),
        pytest.param(lambda e: e.pop("provenance_refs"), id="missing_provenance_refs"),
        pytest.param(lambda e: e.update(confidence=2.0), id="invalid_confidence"),
        pytest.param(lambda e: e.update(approved=True), id="approved_field"),
        pytest.param(lambda e: e.update(promoted=True), id="promoted_field"),
        pytest.param(lambda e: e.update(canon=True), id="canon_field"),
        pytest.param(lambda e: e.update(apply_promotion=True), id="apply_promotion_field"),
        pytest.param(
            lambda e: e.update(memory_destination="memory/index.json"),
            id="memory_destination_field",
        ),
        pytest.param(lambda e: e.update(storyform_truth=True), id="storyform_truth_field"),
        pytest.param(lambda e: e.update(generated_prose="text"), id="generated_prose_field"),
        pytest.param(lambda e: e.update(rewrite="text"), id="rewrite_field"),
        pytest.param(lambda e: e.update(continuation="text"), id="continuation_field"),
        pytest.param(
            lambda e: e.update(raw_artifact_write_intent="writer_assistant/extractions"),
            id="raw_artifact_write_intent_field",
        ),
        pytest.param(lambda e: e.update(runtime_tool_trigger="booknlp"), id="runtime_tool_field"),
        pytest.param(lambda e: e.update(model_call=True), id="model_call_field"),
        pytest.param(lambda e: e.update(training_destination="training/"), id="training_field"),
        pytest.param(lambda e: e.update(jsonl_destination="x.jsonl"), id="jsonl_field"),
        pytest.param(lambda e: e.update(unknown_field_xyz="x"), id="unknown_field"),
    ],
)
def test_validate_entry_fail_closed_matrix(mutate):
    entry = build_valid_queue_entry()
    mutate(entry)
    with pytest.raises(ValueError):
        review_queue_storage.validate_review_queue_entry(entry)


@pytest.mark.parametrize(
    "mutate",
    [
        pytest.param(lambda a: a.update(action_command="approve_candidate"), id="approve_command"),
        pytest.param(lambda a: a.update(action_command="promote_candidate"), id="promote_command"),
        pytest.param(lambda a: a.update(action_command="apply_promotion"), id="apply_promotion_command"),
        pytest.param(lambda a: a.update(action_command="run_extractor"), id="run_extractor_command"),
        pytest.param(lambda a: a.update(resulting_review_status="approved"), id="approved_state"),
        pytest.param(lambda a: a.update(resulting_lifecycle_state="promoted"), id="promoted_state"),
        pytest.param(lambda a: a.update(no_promotion_performed=False), id="promotion_performed"),
        pytest.param(lambda a: a.update(no_memory_canon_mutation=False), id="memory_mutation"),
        pytest.param(lambda a: a.update(apply_promotion=True), id="apply_promotion_field"),
        pytest.param(
            lambda a: a.update(memory_destination="memory/index.json"),
            id="memory_destination_field",
        ),
        pytest.param(lambda a: a.update(generated_prose="text"), id="generated_prose_field"),
        pytest.param(lambda a: a.update(rewrite="text"), id="rewrite_field"),
        pytest.param(lambda a: a.update(continuation="text"), id="continuation_field"),
        pytest.param(
            lambda a: a.update(raw_artifact_write_intent="writer_assistant/extractions"),
            id="raw_artifact_write_intent_field",
        ),
        pytest.param(lambda a: a.update(runtime_tool_trigger="booknlp"), id="runtime_tool_field"),
        pytest.param(lambda a: a.update(model_call=True), id="model_call_field"),
        pytest.param(lambda a: a.update(training_destination="training/"), id="training_field"),
        pytest.param(lambda a: a.update(jsonl_destination="x.jsonl"), id="jsonl_field"),
        pytest.param(lambda a: a.pop("source_locator"), id="missing_source_locator"),
        pytest.param(lambda a: a.pop("evidence_refs"), id="missing_evidence_refs"),
        pytest.param(lambda a: a.pop("provenance_refs"), id="missing_provenance_refs"),
        pytest.param(lambda a: a.update(queue_entry_id="../escape"), id="unsafe_queue_entry_id"),
        pytest.param(lambda a: a.update(unknown_field_xyz="x"), id="unknown_field"),
    ],
)
def test_validate_owner_action_fail_closed_matrix(mutate):
    action = build_valid_owner_action_record()
    mutate(action)
    with pytest.raises(ValueError):
        review_queue_storage.validate_owner_action_record(action)


# ---------------------------------------------------------------------------
# 8. No-side-effect guarantees (tmp_path only)
# ---------------------------------------------------------------------------


def test_validate_and_build_helpers_create_no_files(tmp_path):
    project = project_dir(tmp_path)
    record = candidate_record.validate_candidate_record(build_valid_candidate_record())
    entry = review_queue_storage.build_review_queue_entry_from_candidate_record(
        record, project_id=PROJECT_ID
    )
    review_queue_storage.validate_review_queue_entry(entry)
    review_queue_storage.build_review_queue_index([entry], project_id=PROJECT_ID)
    review_queue_storage.validate_owner_action_record(build_valid_owner_action_record())
    assert all_project_paths(project) == []
    assert not project.exists()


def test_write_creates_only_review_queue_storage_paths(tmp_path):
    project = project_dir(tmp_path)
    entry = build_valid_queue_entry()
    review_queue_storage.write_review_queue_entry(entry, project_dir=project)

    for path in all_project_paths(project):
        relative = path.relative_to(project)
        assert relative.parts[0] == "writer_assistant", relative
        if len(relative.parts) >= 2:
            assert relative.parts[1] == "review_queue", relative
    assert_no_forbidden_paths(project)


def test_storage_helpers_do_not_create_memory_canon_or_source_files(tmp_path):
    project = project_dir(tmp_path)
    entry = build_valid_queue_entry()
    review_queue_storage.write_review_queue_entry(entry, project_dir=project)
    review_queue_storage.read_review_queue_entry(
        entry["queue_entry_id"], project_dir=project
    )
    review_queue_storage.list_review_queue_entries(project_dir=project)
    assert_no_forbidden_paths(project)


# ---------------------------------------------------------------------------
# 9. Source-level boundary contract (future production module)
# ---------------------------------------------------------------------------


def test_future_storage_module_source_has_no_forbidden_runtime_or_prose_terms():
    source_path = Path("backend/story_knowledge/review_queue_storage.py")
    if not source_path.exists():
        return

    source = source_path.read_text(encoding="utf-8").lower()
    for term in FORBIDDEN_PRODUCTION_SOURCE_TERMS:
        assert term.lower() not in source, term
