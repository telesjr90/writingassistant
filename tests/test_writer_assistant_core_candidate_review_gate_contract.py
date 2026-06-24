"""Contract tests for the future Writer Assistant Core candidate persistence gate.

PHASE8-IMPL-011-T004 is tests-first only. The future pure candidate review/
persistence gate module is imported normally so this targeted file is expected
red (collection ImportError) until PHASE8-IMPL-011-T005 creates it, if authorized:

- backend.story_knowledge.candidate_review_gate

Expected future public APIs:

- validate_candidate_draft_for_persistence(draft: dict) -> dict
- build_candidate_record_from_draft(draft: dict, *, project_id: str) -> dict
- build_review_queue_entry(candidate_record: dict, *, project_id: str) -> dict
- persist_candidate_record_for_review(candidate_record: dict, *, project_dir) -> dict

These tests encode the PHASE8-IMPL-011-T002 candidate draft to candidate record
persistence gate decision and the PHASE8-IMPL-011-T003 review queue data shape and
lifecycle decision.

All fixtures are small, synthetic, owner-authored/test-fabricated dictionaries.
These tests do not install, import, or run BookNLP/spaCy; do not call models or
tools; do not write memory/canon/project source files; do not write raw artifacts;
do not write training/JSONL/dataset files; and do not perform apply-promotion.
Filesystem assertions use pytest tmp_path only.
"""

import copy
import inspect
from pathlib import Path

import pytest

from backend.story_knowledge import candidate_record
from backend.story_knowledge import candidate_schema
from backend.story_knowledge import candidate_persistence
from backend.story_knowledge import candidate_storage

# The future gate module is imported normally; expected red until T005 exists.
from backend.story_knowledge import candidate_review_gate


# ---------------------------------------------------------------------------
# Contract constants
# ---------------------------------------------------------------------------

PROJECT_ID = "example"

EXPECTED_PUBLIC_API = (
    "validate_candidate_draft_for_persistence",
    "build_candidate_record_from_draft",
    "build_review_queue_entry",
    "persist_candidate_record_for_review",
)

# Required candidate draft fields (PHASE8-IMPL-011-T002 decision).
DRAFT_REQUIRED_FIELDS = frozenset(
    {
        "candidate_type",
        "target_category",
        "source_document",
        "source_locator",
        "evidence",
        "provenance",
        "confidence",
        "raw_output_refs",
        "normalization_status",
        "human_review_required",
    }
)

ACCEPTED_NORMALIZATION_STATUS = "normalized"

# Drafts that must fail closed by default (no queue-only quarantine in this gate).
QUARANTINE_NORMALIZATION_STATUSES = (
    "insufficient_evidence",
    "rejected_output",
)

# Extra keys that must be rejected on a candidate draft (unknown/forbidden).
FORBIDDEN_DRAFT_FIELDS = (
    "owner_decision",
    "status",
    "destination",
    "promoted",
    "approved",
    "canon",
    "memory_destination",
    "apply_promotion",
    "write_to_canon",
    "mutate_memory",
    "generated_prose",
    "rewrite",
    "continuation",
    "route_trigger",
    "ui_trigger",
    "ui_action_trigger",
    "model_call",
    "runtime_tool_trigger",
    "runtime_tool_name",
    "persist_raw_artifacts",
    "raw_output_directory",
    "candidate_records_path",
    "training",
    "dataset",
    "jsonl",
)

UNSAFE_ID_VALUES = (
    "../escape",
    "..",
    "/absolute",
    "C:\\escape",
    "folder/name",
    "folder\\name",
    "",
    "   ",
)

# Review queue entry shape (PHASE8-IMPL-011-T003 decision).
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
)

PERSIST_METADATA_REQUIRED_FIELDS = frozenset(
    {
        "persisted",
        "candidate_only",
        "review_pending",
        "candidate_id",
        "project_id",
    }
)

# Recursive forbidden-term scan applied to built records, queue entries, and
# persistence metadata returned by the future gate.
FORBIDDEN_OUTPUT_TERMS = (
    "promoted",
    "apply_promotion",
    "write_to_canon",
    "mutate_memory",
    "memory_destination",
    "storyform_truth",
    "generated_prose",
    "rewrite",
    "continuation",
    "route_trigger",
    "ui_action_trigger",
    "runtime_tool_trigger",
    "model_call",
    "dataset_manifest",
    "jsonl",
)

# Forbidden runtime/tool/prose/mutation/UI/route terms for the future production
# gate module source (PHASE8-IMPL-011-T004 source-level boundary contract).
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
    "mutate_memory",
    "storyform_truth",
    "generated_prose",
    "rewrite",
    "continuation",
    "dataset_manifest",
    "jsonl",
)

# Project-relative paths the persistence gate must never create.
FORBIDDEN_PROJECT_PATHS = (
    "memory",
    "memory.json",
    "bible.json",
    "storyform.json",
    "project.json",
    "scenes",
    "notes",
    "materials",
    "training",
    "dataset_manifest.json",
)

SAFE_CANDIDATE_ID = "core_candidate_scene_001_character_001"


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


def build_valid_source_document(**overrides):
    document = {
        "project_id": PROJECT_ID,
        "source_document_type": "scene",
        "source_document_id": "scene_001",
        "content_hash": "sha256:source-doc-001",
    }
    document.update(overrides)
    return document


def build_valid_evidence_item(**overrides):
    item = {
        "evidence_id": "evidence_001",
        "source_locator": build_valid_source_locator(),
        "source_text_excerpt": "",
        "summary": "",
        "supports_claim": "",
        "confidence": 0.5,
        "notes": "",
    }
    item.update(overrides)
    return item


def build_valid_provenance(**overrides):
    provenance = {
        "origin": "extractor",
        "extraction_method": "fixture_orchestrator",
        "timestamp": "2026-06-24T00:00:00Z",
        "human_review_required": True,
    }
    provenance.update(overrides)
    return provenance


def build_valid_candidate_draft(**overrides):
    draft = {
        "candidate_type": "character_candidate",
        "target_category": "characters",
        "source_document": build_valid_source_document(),
        "source_locator": build_valid_source_locator(),
        "evidence": [build_valid_evidence_item()],
        "provenance": build_valid_provenance(),
        "confidence": 0.4,
        "raw_output_refs": ["raw_booknlp_tokens"],
        "normalization_status": ACCEPTED_NORMALIZATION_STATUS,
        "human_review_required": True,
    }
    draft.update(overrides)
    return draft


def build_valid_candidate_record(**overrides):
    record = {
        "candidate_id": SAFE_CANDIDATE_ID,
        "project_id": PROJECT_ID,
        "candidate_type": "character_candidate",
        "status": "candidate",
        "target_category": "characters",
        "source_locator": build_valid_source_locator(),
        "evidence": [],
        "provenance": build_valid_provenance(origin="manual", extraction_method="owner_entry"),
        "owner_decision": "undecided",
        "destination": "omi_candidate_only",
        "confidence": 0.0,
        "created_at": "2026-06-24T00:00:00Z",
        "updated_at": "2026-06-24T00:00:00Z",
    }
    record.update(overrides)
    return record


def project_dir(tmp_path: Path) -> Path:
    return tmp_path / "my-project"


def all_project_paths(project: Path):
    if not project.exists():
        return []
    return list(project.rglob("*"))


def assert_no_writer_assistant_dir(project: Path):
    assert not (project / "writer_assistant").exists()


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
        assert hasattr(candidate_review_gate, name), name


def test_future_public_api_symbols_are_callable():
    for name in EXPECTED_PUBLIC_API:
        assert callable(getattr(candidate_review_gate, name)), name


# ---------------------------------------------------------------------------
# 2. Candidate draft validation
# ---------------------------------------------------------------------------


def test_validate_draft_accepts_valid_fixture_and_returns_new_dict():
    draft = build_valid_candidate_draft()
    result = candidate_review_gate.validate_candidate_draft_for_persistence(draft)
    assert isinstance(result, dict)
    assert result is not draft


def test_validate_draft_accepts_only_dict_input():
    for invalid in (None, [], (), "draft", 1, 1.5, True):
        with pytest.raises(ValueError):
            candidate_review_gate.validate_candidate_draft_for_persistence(invalid)


def test_validate_draft_does_not_mutate_caller_input():
    draft = build_valid_candidate_draft()
    original = copy.deepcopy(draft)
    candidate_review_gate.validate_candidate_draft_for_persistence(draft)
    assert draft == original


def test_validate_draft_returned_copy_is_isolated_from_caller():
    draft = build_valid_candidate_draft()
    result = candidate_review_gate.validate_candidate_draft_for_persistence(draft)
    draft["confidence"] = 0.99
    draft["source_locator"]["source_document_id"] = "mutated"
    assert result["confidence"] == 0.4
    assert result["source_locator"]["source_document_id"] == "scene_001"


@pytest.mark.parametrize("missing_field", sorted(DRAFT_REQUIRED_FIELDS))
def test_validate_draft_rejects_missing_required_field(missing_field):
    draft = build_valid_candidate_draft()
    del draft[missing_field]
    with pytest.raises(ValueError):
        candidate_review_gate.validate_candidate_draft_for_persistence(draft)


@pytest.mark.parametrize("forbidden_field", FORBIDDEN_DRAFT_FIELDS)
def test_validate_draft_rejects_unknown_and_forbidden_fields(forbidden_field):
    draft = build_valid_candidate_draft(**{forbidden_field: "blocked"})
    with pytest.raises(ValueError):
        candidate_review_gate.validate_candidate_draft_for_persistence(draft)


@pytest.mark.parametrize(
    "candidate_type", sorted(candidate_schema.CORE_CANDIDATE_TYPES)
)
def test_validate_draft_accepts_supported_candidate_types(candidate_type):
    target_category = candidate_schema.CORE_CANDIDATE_TARGET_CATEGORIES[candidate_type]
    draft = build_valid_candidate_draft(
        candidate_type=candidate_type,
        target_category=target_category,
    )
    result = candidate_review_gate.validate_candidate_draft_for_persistence(draft)
    assert result["candidate_type"] == candidate_type


@pytest.mark.parametrize(
    "forbidden_type",
    ("generated_prose", "rewrite", "continuation", "unknown_type_xyz"),
)
def test_validate_draft_rejects_unsupported_candidate_types(forbidden_type):
    draft = build_valid_candidate_draft(candidate_type=forbidden_type)
    with pytest.raises(ValueError):
        candidate_review_gate.validate_candidate_draft_for_persistence(draft)


def test_validate_draft_rejects_mismatched_target_category():
    draft = build_valid_candidate_draft(
        candidate_type="character_candidate",
        target_category="timeline",
    )
    with pytest.raises(ValueError):
        candidate_review_gate.validate_candidate_draft_for_persistence(draft)


def test_validate_draft_requires_human_review_required_true():
    draft = build_valid_candidate_draft(human_review_required=False)
    with pytest.raises(ValueError):
        candidate_review_gate.validate_candidate_draft_for_persistence(draft)


@pytest.mark.parametrize("missing_support", ("source_document", "source_locator", "evidence", "provenance"))
def test_validate_draft_requires_source_and_evidence_support(missing_support):
    draft = build_valid_candidate_draft()
    del draft[missing_support]
    with pytest.raises(ValueError):
        candidate_review_gate.validate_candidate_draft_for_persistence(draft)


@pytest.mark.parametrize("invalid_confidence", (-0.01, 1.01, "high", True, None))
def test_validate_draft_rejects_invalid_confidence(invalid_confidence):
    draft = build_valid_candidate_draft(confidence=invalid_confidence)
    with pytest.raises(ValueError):
        candidate_review_gate.validate_candidate_draft_for_persistence(draft)


@pytest.mark.parametrize("quarantine_status", QUARANTINE_NORMALIZATION_STATUSES)
def test_validate_draft_fails_closed_for_quarantine_normalization_status(quarantine_status):
    draft = build_valid_candidate_draft(normalization_status=quarantine_status)
    with pytest.raises(ValueError):
        candidate_review_gate.validate_candidate_draft_for_persistence(draft)


@pytest.mark.parametrize("unsafe_value", UNSAFE_ID_VALUES)
def test_validate_draft_rejects_unsafe_source_project_id(unsafe_value):
    draft = build_valid_candidate_draft(
        source_locator=build_valid_source_locator(project_id=unsafe_value)
    )
    with pytest.raises(ValueError):
        candidate_review_gate.validate_candidate_draft_for_persistence(draft)


def test_validate_draft_rejects_path_traversal_source_document_id():
    draft = build_valid_candidate_draft(
        source_locator=build_valid_source_locator(
            source_document_id="../../etc/passwd"
        )
    )
    with pytest.raises(ValueError):
        candidate_review_gate.validate_candidate_draft_for_persistence(draft)


# ---------------------------------------------------------------------------
# 3. Candidate record build
# ---------------------------------------------------------------------------


def test_build_record_returns_schema_valid_candidate_only_record():
    draft = build_valid_candidate_draft()
    record = candidate_review_gate.build_candidate_record_from_draft(
        draft, project_id=PROJECT_ID
    )
    validated = candidate_record.validate_candidate_record(record)
    assert validated["status"] == "candidate"
    assert validated["project_id"] == PROJECT_ID
    assert validated["candidate_type"] == "character_candidate"
    assert validated["target_category"] == "characters"


def test_build_record_preserves_candidate_only_state_and_no_owner_approval():
    draft = build_valid_candidate_draft()
    record = candidate_review_gate.build_candidate_record_from_draft(
        draft, project_id=PROJECT_ID
    )
    assert record["status"] == "candidate"
    assert record["owner_decision"] == "undecided"
    assert record["destination"] in candidate_schema.CORE_DESTINATION_VALUES
    assert record["destination"] not in (
        "write_to_canon",
        "apply_promotion",
        "mutate_memory",
    )


def test_build_record_preserves_source_evidence_provenance_and_confidence():
    draft = build_valid_candidate_draft()
    record = candidate_review_gate.build_candidate_record_from_draft(
        draft, project_id=PROJECT_ID
    )
    assert record["confidence"] == draft["confidence"]
    assert record["source_locator"]["source_document_id"] == "scene_001"
    assert len(record["evidence"]) == len(draft["evidence"])
    for item in record["evidence"]:
        candidate_record.validate_evidence_item(item)
    candidate_record.validate_provenance(record["provenance"])
    assert record["provenance"]["human_review_required"] is True


def test_build_record_uses_path_safe_generated_candidate_id():
    draft = build_valid_candidate_draft()
    record = candidate_review_gate.build_candidate_record_from_draft(
        draft, project_id=PROJECT_ID
    )
    candidate_id = record["candidate_id"]
    assert isinstance(candidate_id, str)
    assert candidate_id.strip()
    assert "/" not in candidate_id
    assert "\\" not in candidate_id
    assert ".." not in candidate_id
    assert not candidate_id.endswith(".json")


def test_build_record_does_not_emit_forbidden_promotion_or_mutation_fields():
    draft = build_valid_candidate_draft()
    record = candidate_review_gate.build_candidate_record_from_draft(
        draft, project_id=PROJECT_ID
    )
    assert_no_forbidden_terms(record, FORBIDDEN_OUTPUT_TERMS)


def test_build_record_does_not_mutate_caller_input():
    draft = build_valid_candidate_draft()
    original = copy.deepcopy(draft)
    candidate_review_gate.build_candidate_record_from_draft(draft, project_id=PROJECT_ID)
    assert draft == original


def test_build_record_fails_closed_for_invalid_draft():
    draft = build_valid_candidate_draft()
    del draft["evidence"]
    with pytest.raises(ValueError):
        candidate_review_gate.build_candidate_record_from_draft(
            draft, project_id=PROJECT_ID
        )


@pytest.mark.parametrize("unsafe_value", UNSAFE_ID_VALUES)
def test_build_record_rejects_unsafe_project_id(unsafe_value):
    draft = build_valid_candidate_draft()
    with pytest.raises(ValueError):
        candidate_review_gate.build_candidate_record_from_draft(
            draft, project_id=unsafe_value
        )


# ---------------------------------------------------------------------------
# 4. Review queue entry build (PHASE8-IMPL-011-T003 shape)
# ---------------------------------------------------------------------------


def test_build_queue_entry_returns_required_fields():
    record = candidate_record.validate_candidate_record(build_valid_candidate_record())
    entry = candidate_review_gate.build_review_queue_entry(record, project_id=PROJECT_ID)
    assert isinstance(entry, dict)
    assert REQUIRED_QUEUE_FIELDS.issubset(set(entry))
    assert entry["project_id"] == PROJECT_ID
    assert entry["candidate_record_id"] == record["candidate_id"]
    assert entry["candidate_type"] == record["candidate_type"]
    assert entry["target_category"] == record["target_category"]


def test_build_queue_entry_uses_allowed_review_status_and_lifecycle_state():
    record = candidate_record.validate_candidate_record(build_valid_candidate_record())
    entry = candidate_review_gate.build_review_queue_entry(record, project_id=PROJECT_ID)
    assert entry["review_status"] in ALLOWED_REVIEW_STATUS_VALUES
    assert entry["lifecycle_state"] in ALLOWED_LIFECYCLE_STATES
    assert entry["review_status"] != "approved"
    assert entry["human_review_required"] is True


def test_build_queue_entry_carries_evidence_and_provenance_support_shapes():
    record = candidate_record.validate_candidate_record(build_valid_candidate_record())
    entry = candidate_review_gate.build_review_queue_entry(record, project_id=PROJECT_ID)
    assert isinstance(entry["evidence_refs"], list)
    assert isinstance(entry["provenance_refs"], list)
    assert isinstance(entry["uncertainty_flags"], list)
    assert isinstance(entry["raw_output_refs"], list)
    assert isinstance(entry["evidence_summary"], str)
    assert isinstance(entry["provenance_summary"], str)
    assert isinstance(entry["normalization_status"], str)


@pytest.mark.parametrize("forbidden_field", FORBIDDEN_QUEUE_FIELDS)
def test_build_queue_entry_does_not_include_forbidden_fields(forbidden_field):
    record = candidate_record.validate_candidate_record(build_valid_candidate_record())
    entry = candidate_review_gate.build_review_queue_entry(record, project_id=PROJECT_ID)
    assert forbidden_field not in entry


def test_build_queue_entry_output_has_no_forbidden_terms():
    record = candidate_record.validate_candidate_record(build_valid_candidate_record())
    entry = candidate_review_gate.build_review_queue_entry(record, project_id=PROJECT_ID)
    assert_no_forbidden_terms(entry, FORBIDDEN_OUTPUT_TERMS)


def test_build_queue_entry_does_not_mutate_caller_input():
    record = candidate_record.validate_candidate_record(build_valid_candidate_record())
    original = copy.deepcopy(record)
    candidate_review_gate.build_review_queue_entry(record, project_id=PROJECT_ID)
    assert record == original


def test_build_queue_entry_rejects_invalid_candidate_record():
    invalid = build_valid_candidate_record()
    del invalid["candidate_type"]
    with pytest.raises(ValueError):
        candidate_review_gate.build_review_queue_entry(invalid, project_id=PROJECT_ID)


def test_build_queue_entry_rejects_promoted_candidate_record():
    promoted = build_valid_candidate_record(status="promoted")
    with pytest.raises(ValueError):
        candidate_review_gate.build_review_queue_entry(promoted, project_id=PROJECT_ID)


# ---------------------------------------------------------------------------
# 5. Persistence gate (tmp_path only)
# ---------------------------------------------------------------------------


def test_persist_writes_candidate_only_record_to_project_local_storage(tmp_path):
    project = project_dir(tmp_path)
    record = candidate_record.validate_candidate_record(build_valid_candidate_record())
    metadata = candidate_review_gate.persist_candidate_record_for_review(
        record, project_dir=project
    )

    candidate_path = candidate_storage.candidate_record_path(project, SAFE_CANDIDATE_ID)
    assert candidate_path.exists()
    assert candidate_path.is_file()
    assert "writer_assistant" in candidate_path.parts
    assert "candidates" in candidate_path.parts

    stored = candidate_persistence.read_candidate_record(project, SAFE_CANDIDATE_ID)
    assert stored["candidate_id"] == SAFE_CANDIDATE_ID
    assert stored["status"] == "candidate"

    assert isinstance(metadata, dict)
    assert PERSIST_METADATA_REQUIRED_FIELDS.issubset(set(metadata))
    assert metadata["persisted"] is True
    assert metadata["candidate_only"] is True
    assert metadata["review_pending"] is True
    assert metadata["candidate_id"] == SAFE_CANDIDATE_ID
    assert metadata["project_id"] == PROJECT_ID
    assert_no_forbidden_terms(metadata, FORBIDDEN_OUTPUT_TERMS)


def test_persist_does_not_write_memory_canon_or_project_source_files(tmp_path):
    project = project_dir(tmp_path)
    record = candidate_record.validate_candidate_record(build_valid_candidate_record())
    candidate_review_gate.persist_candidate_record_for_review(record, project_dir=project)
    assert_no_forbidden_paths(project)


def test_persist_does_not_mutate_caller_input(tmp_path):
    project = project_dir(tmp_path)
    record = candidate_record.validate_candidate_record(build_valid_candidate_record())
    original = copy.deepcopy(record)
    candidate_review_gate.persist_candidate_record_for_review(record, project_dir=project)
    assert record == original


def test_persist_fails_closed_for_invalid_record_without_side_effects(tmp_path):
    project = project_dir(tmp_path)
    invalid = build_valid_candidate_record(destination="write_to_canon")
    with pytest.raises(ValueError):
        candidate_review_gate.persist_candidate_record_for_review(
            invalid, project_dir=project
        )
    assert_no_writer_assistant_dir(project)
    assert_no_forbidden_paths(project)


@pytest.mark.parametrize("unsafe_value", UNSAFE_ID_VALUES)
def test_persist_fails_closed_for_unsafe_candidate_id(tmp_path, unsafe_value):
    project = project_dir(tmp_path)
    record = build_valid_candidate_record(candidate_id=unsafe_value)
    with pytest.raises(ValueError):
        candidate_review_gate.persist_candidate_record_for_review(
            record, project_dir=project
        )
    assert_no_writer_assistant_dir(project)


def test_persist_fails_closed_for_promoted_record(tmp_path):
    project = project_dir(tmp_path)
    record = build_valid_candidate_record(status="promoted")
    with pytest.raises(ValueError):
        candidate_review_gate.persist_candidate_record_for_review(
            record, project_dir=project
        )
    assert_no_writer_assistant_dir(project)


# ---------------------------------------------------------------------------
# 6. Fail-closed coverage
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "mutate",
    [
        pytest.param(lambda d: d.pop("source_locator"), id="missing_source_locator"),
        pytest.param(lambda d: d.pop("source_document"), id="missing_source_document"),
        pytest.param(lambda d: d.pop("evidence"), id="missing_evidence"),
        pytest.param(lambda d: d.pop("provenance"), id="missing_provenance"),
        pytest.param(lambda d: d.update(confidence=2.0), id="invalid_confidence"),
        pytest.param(
            lambda d: d.update(candidate_type="not_a_real_candidate"),
            id="unsupported_candidate_type",
        ),
        pytest.param(lambda d: d.update(owner_decision="approve"), id="owner_decision_prefilled"),
        pytest.param(lambda d: d.update(status="approved"), id="approved_status"),
        pytest.param(lambda d: d.update(promoted=True), id="promoted_field"),
        pytest.param(lambda d: d.update(canon=True), id="canon_field"),
        pytest.param(lambda d: d.update(apply_promotion=True), id="apply_promotion_field"),
        pytest.param(
            lambda d: d.update(memory_destination="memory/index.json"),
            id="memory_destination_field",
        ),
        pytest.param(lambda d: d.update(generated_prose="text"), id="generated_prose_field"),
        pytest.param(lambda d: d.update(rewrite="text"), id="rewrite_field"),
        pytest.param(lambda d: d.update(continuation="text"), id="continuation_field"),
        pytest.param(
            lambda d: d.update(raw_output_directory="writer_assistant/extractions"),
            id="raw_artifact_write_intent",
        ),
        pytest.param(lambda d: d.update(runtime_tool_name="booknlp"), id="runtime_tool_intent"),
        pytest.param(lambda d: d.update(model_call=True), id="model_call_intent"),
        pytest.param(lambda d: d.update(jsonl="record"), id="jsonl_field"),
        pytest.param(lambda d: d.update(dataset="record"), id="dataset_field"),
        pytest.param(lambda d: d.update(human_review_required=False), id="human_review_false"),
    ],
)
def test_validate_draft_fail_closed_matrix(mutate):
    draft = build_valid_candidate_draft()
    mutate(draft)
    with pytest.raises(ValueError):
        candidate_review_gate.validate_candidate_draft_for_persistence(draft)


# ---------------------------------------------------------------------------
# 7. No-side-effect guarantees (tmp_path only)
# ---------------------------------------------------------------------------


def test_validate_and_build_helpers_create_no_files(tmp_path):
    project = project_dir(tmp_path)
    draft = build_valid_candidate_draft()
    candidate_review_gate.validate_candidate_draft_for_persistence(draft)
    record = candidate_review_gate.build_candidate_record_from_draft(
        draft, project_id=PROJECT_ID
    )
    candidate_review_gate.build_review_queue_entry(record, project_id=PROJECT_ID)
    assert all_project_paths(project) == []
    assert not project.exists()


def test_persist_creates_only_candidate_storage_paths(tmp_path):
    project = project_dir(tmp_path)
    record = candidate_record.validate_candidate_record(build_valid_candidate_record())
    candidate_review_gate.persist_candidate_record_for_review(record, project_dir=project)

    for path in all_project_paths(project):
        relative = path.relative_to(project)
        assert relative.parts[0] == "writer_assistant", relative
    assert_no_forbidden_paths(project)


# ---------------------------------------------------------------------------
# 8. Source-level boundary contract (future production module)
# ---------------------------------------------------------------------------


def test_future_gate_module_source_has_no_forbidden_runtime_or_prose_terms():
    source_path = Path("backend/story_knowledge/candidate_review_gate.py")
    if not source_path.exists():
        return

    source = source_path.read_text(encoding="utf-8").lower()
    for term in FORBIDDEN_PRODUCTION_SOURCE_TERMS:
        assert term.lower() not in source, term
