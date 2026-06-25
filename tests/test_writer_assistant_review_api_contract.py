"""Contract tests for the future Writer Assistant Core review API boundary.

PHASE8-IMPL-013-T005 is tests-first only. The future review API module is
imported normally so this targeted file is expected red until a later authorized
task creates the module and symbols:

- backend.review_api

Expected future public APIs:

- list_review_queue_entries_readonly
- get_review_queue_entry_readonly
- get_review_queue_index_readonly
- get_review_queue_summary_readonly
- validate_review_queue_read_request
- validate_owner_action_command_request
- build_owner_action_command_response

These tests encode the PHASE8-IMPL-013-T002 read-only review queue API contract,
the PHASE8-IMPL-013-T003 owner action command API contract, and the
PHASE8-IMPL-013-T004 review UI planning boundary. They intentionally do not
implement backend routes, FastAPI endpoints, frontend helpers, owner action
execution, apply-promotion, memory/canon mutation, raw artifact persistence,
runtime extraction, or generated prose.
"""

from pathlib import Path

import pytest

# The future API module is imported normally; expected red until implemented.
from backend import review_api


PROJECT_ID = "example"
QUEUE_ENTRY_ID = "review_queue_entry_scene_001_character_001"
CANDIDATE_RECORD_ID = "core_candidate_scene_001_character_001"

EXPECTED_PUBLIC_API = (
    "list_review_queue_entries_readonly",
    "get_review_queue_entry_readonly",
    "get_review_queue_index_readonly",
    "get_review_queue_summary_readonly",
    "validate_review_queue_read_request",
    "validate_owner_action_command_request",
    "build_owner_action_command_response",
)

READ_REQUEST_ALLOWED_FIELDS = {
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

READ_REQUEST_FORBIDDEN_FIELDS = (
    "owner_decision",
    "review_status_mutation",
    "lifecycle_state_mutation",
    "action_command",
    "approve",
    "promote",
    "canon",
    "approved",
    "promoted",
    "apply_promotion",
    "apply-promotion",
    "memory_destination",
    "canon_destination",
    "raw_artifact_write_intent",
    "raw_artifact_read_intent",
    "runtime_tool_trigger",
    "model_call",
    "run_booknlp",
    "run_spacy",
    "generated_prose",
    "rewrite",
    "continuation",
    "path",
    "filesystem_path",
    "unknown_field",
)

UNSAFE_ID_VALUES = (
    "../escape",
    "..",
    ".",
    "/absolute",
    "C:\\escape",
    "folder/name",
    "folder\\name",
    "",
    "   ",
    ".hidden",
)

READ_RESPONSE_ALLOWED_FIELDS = {
    "schema_version",
    "project_id",
    "entries",
    "entry",
    "queue_entry_id",
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
    "pagination",
    "summary",
    "metadata",
    "warnings",
    "errors",
}

READ_RESPONSE_FORBIDDEN_FIELDS = (
    "approved",
    "approved_truth",
    "canon",
    "canon_truth",
    "memory_write",
    "memory_write_result",
    "promoted",
    "promoted_state",
    "apply_promotion",
    "apply_promotion_trigger",
    "owner_action_execution_result",
    "generated_prose",
    "model_call",
    "runtime_extraction",
    "raw_artifact_persistence",
    "filesystem_path",
)

OWNER_ACTION_REQUIRED_FIELDS = {
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

OWNER_ACTION_OPTIONAL_FIELDS = {
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
    "apply_promotion",
    "write_to_memory",
    "write_to_canon",
    "mutate_memory",
    "mark_canon",
    "mark_approved_truth",
    "generate_prose",
    "rewrite_source",
    "continue_scene",
    "run_extractor",
    "run_booknlp",
    "run_spacy",
    "persist_raw_artifact",
    "create_training_record",
    "export_jsonl",
    "totally_unknown_command",
)

OWNER_ACTION_FORBIDDEN_FIELDS = (
    "approved",
    "promoted",
    "canon",
    "owner_decision_approved",
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
    "source_body_edit",
    "path",
)

OWNER_ACTION_RESPONSE_REQUIRED_FIELDS = {
    "schema_version",
    "project_id",
    "queue_entry_id",
    "candidate_record_id",
    "action_command",
    "accepted",
    "review_status",
    "lifecycle_state",
    "owner_action_record",
    "evidence_refs",
    "provenance_refs",
    "source_locator",
    "source_document",
    "human_review_required",
    "no_promotion_performed",
    "no_memory_canon_mutation",
    "warnings",
    "errors",
}

OWNER_ACTION_RESPONSE_FORBIDDEN_FIELDS = (
    "approved_truth",
    "canon_truth",
    "promoted_state",
    "memory_write_result",
    "apply_promotion_result",
    "generated_prose",
    "rewritten_source",
    "continuation_text",
    "runtime_extraction_output",
    "raw_artifact_persistence_result",
)

FORBIDDEN_SIDE_EFFECT_PATHS = (
    "memory",
    "memory/index.json",
    "bible.json",
    "storyform.json",
    "project.json",
    "scenes",
    "chapters",
    "notes",
    "materials",
    "writer_assistant/extractions",
    "raw_artifacts",
    "training",
    "dataset_manifest.json",
    "records.jsonl",
)

FORBIDDEN_SOURCE_TERMS = (
    "@app.get",
    "@app.post",
    "@app.put",
    "@app.patch",
    "@app.delete",
    "APIRouter",
    "FastAPI(",
    "write_to_memory",
    "write_to_canon",
    "apply_promotion",
    "promote_candidate",
    "approve_candidate",
    "generated_prose",
    "rewrite_source",
    "continue_scene",
    "run_booknlp",
    "run_spacy",
    "persist_raw_artifact",
    "create_training_record",
    "export_jsonl",
)


def valid_read_request(**overrides):
    request = {
        "project_id": PROJECT_ID,
        "queue_entry_id": QUEUE_ENTRY_ID,
        "review_status": "pending",
        "lifecycle_state": "draft_ready_for_review",
        "candidate_type": "character",
        "target_category": "character_memory_record",
        "normalization_status": "normalized",
        "has_raw_refs": True,
        "confidence_min": 0.0,
        "confidence_max": 1.0,
        "sort_by": "queue_entry_id",
        "sort_direction": "asc",
        "limit": 25,
        "offset": 0,
    }
    request.update(overrides)
    return request


def valid_queue_entry(**overrides):
    entry = {
        "schema_version": 1,
        "project_id": PROJECT_ID,
        "queue_entry_id": QUEUE_ENTRY_ID,
        "candidate_record_id": CANDIDATE_RECORD_ID,
        "candidate_type": "character",
        "target_category": "character_memory_record",
        "review_status": "pending",
        "lifecycle_state": "draft_ready_for_review",
        "confidence": 0.72,
        "uncertainty_flags": ["owner_review_required"],
        "normalization_status": "normalized",
        "human_review_required": True,
        "evidence_summary": "Owner-authored fixture evidence summary.",
        "evidence_refs": ["evidence_scene_001_001"],
        "provenance_summary": "Fixture parser support only.",
        "provenance_refs": ["provenance_fixture_001"],
        "source_document": {"source_document_id": "scene_001", "label": "Scene 001"},
        "source_locator": {
            "source_document_id": "scene_001",
            "start_offset": 0,
            "end_offset": 42,
        },
        "raw_output_refs": ["raw_ref_fixture_001"],
        "created_at": "2026-06-25T00:00:00Z",
        "updated_at": "2026-06-25T00:00:00Z",
    }
    entry.update(overrides)
    return entry


def valid_owner_action_command(**overrides):
    request = {
        "project_id": PROJECT_ID,
        "queue_entry_id": QUEUE_ENTRY_ID,
        "candidate_record_id": CANDIDATE_RECORD_ID,
        "action_command": "request_more_evidence",
        "actor_ref": "owner",
        "reason_code": "needs_source_support",
        "reviewer_note": "Needs more source support before any later review.",
        "client_request_id": "client_request_001",
        "human_review_required": True,
        "no_promotion_requested": True,
        "no_memory_canon_mutation_requested": True,
        "previous_review_status": "pending",
        "previous_lifecycle_state": "draft_ready_for_review",
        "target_review_status": "needs_info",
        "target_lifecycle_state": "needs_more_evidence",
        "command_metadata": {"surface": "future_review_ui_contract"},
    }
    request.update(overrides)
    return request


def valid_owner_action_response(**overrides):
    response = {
        "schema_version": 1,
        "project_id": PROJECT_ID,
        "queue_entry_id": QUEUE_ENTRY_ID,
        "candidate_record_id": CANDIDATE_RECORD_ID,
        "action_command": "request_more_evidence",
        "accepted": True,
        "review_status": "needs_info",
        "lifecycle_state": "needs_more_evidence",
        "owner_action_record": {
            "action_command": "request_more_evidence",
            "no_promotion_performed": True,
            "no_memory_canon_mutation": True,
        },
        "evidence_refs": ["evidence_scene_001_001"],
        "provenance_refs": ["provenance_fixture_001"],
        "source_locator": {
            "source_document_id": "scene_001",
            "start_offset": 0,
            "end_offset": 42,
        },
        "source_document": {"source_document_id": "scene_001", "label": "Scene 001"},
        "human_review_required": True,
        "no_promotion_performed": True,
        "no_memory_canon_mutation": True,
        "warnings": ["No promotion or canon write was performed."],
        "errors": [],
    }
    response.update(overrides)
    return response


def assert_no_forbidden_keys(value, forbidden_terms):
    if isinstance(value, dict):
        for key, nested in value.items():
            assert key not in forbidden_terms, key
            assert_no_forbidden_keys(nested, forbidden_terms)
    elif isinstance(value, list):
        for item in value:
            assert_no_forbidden_keys(item, forbidden_terms)


def existing_relative_paths(root: Path):
    if not root.exists():
        return set()
    return {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.exists()
    }


def test_future_review_api_module_exposes_expected_public_symbols():
    for name in EXPECTED_PUBLIC_API:
        assert hasattr(review_api, name), name
        assert callable(getattr(review_api, name)), name


@pytest.mark.parametrize("invalid_input", [None, [], (), "project", 42, True])
def test_validate_review_queue_read_request_accepts_only_dict_input(invalid_input):
    with pytest.raises((TypeError, ValueError)):
        review_api.validate_review_queue_read_request(invalid_input)


def test_validate_review_queue_read_request_requires_project_id():
    request = valid_read_request()
    del request["project_id"]

    with pytest.raises((TypeError, ValueError)):
        review_api.validate_review_queue_read_request(request)


def test_validate_review_queue_read_request_accepts_safe_read_filters_and_returns_copy():
    request = valid_read_request()
    result = review_api.validate_review_queue_read_request(request)

    assert result == request
    assert result is not request
    assert set(result) <= READ_REQUEST_ALLOWED_FIELDS

    result["project_id"] = "changed"
    assert request["project_id"] == PROJECT_ID


@pytest.mark.parametrize("field", READ_REQUEST_FORBIDDEN_FIELDS)
def test_validate_review_queue_read_request_rejects_write_runtime_raw_prose_path_and_unknown_fields(field):
    request = valid_read_request(**{field: "blocked"})

    with pytest.raises((TypeError, ValueError)):
        review_api.validate_review_queue_read_request(request)


@pytest.mark.parametrize("id_field", ["project_id", "queue_entry_id"])
@pytest.mark.parametrize("unsafe_value", UNSAFE_ID_VALUES)
def test_validate_review_queue_read_request_rejects_unsafe_ids(id_field, unsafe_value):
    request = valid_read_request(**{id_field: unsafe_value})

    with pytest.raises((TypeError, ValueError)):
        review_api.validate_review_queue_read_request(request)


def test_readonly_response_shape_preserves_review_support_fields_without_truth_or_mutation_terms():
    response = review_api.list_review_queue_entries_readonly(valid_read_request())

    assert response["schema_version"]
    assert response["project_id"] == PROJECT_ID
    assert "entries" in response
    assert set(response) <= READ_RESPONSE_ALLOWED_FIELDS
    assert_no_forbidden_keys(response, READ_RESPONSE_FORBIDDEN_FIELDS)

    entries = response["entries"]
    assert isinstance(entries, list)
    for entry in entries:
        assert {
            "queue_entry_id",
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
        } <= set(entry)
        assert entry["human_review_required"] is True
        assert_no_forbidden_keys(entry, READ_RESPONSE_FORBIDDEN_FIELDS)


def test_readonly_single_entry_response_shape_is_support_only():
    response = review_api.get_review_queue_entry_readonly(
        valid_read_request(queue_entry_id=QUEUE_ENTRY_ID)
    )

    assert response["schema_version"]
    assert response["project_id"] == PROJECT_ID
    assert "entry" in response
    assert set(response) <= READ_RESPONSE_ALLOWED_FIELDS
    assert_no_forbidden_keys(response, READ_RESPONSE_FORBIDDEN_FIELDS)


@pytest.mark.parametrize("invalid_input", [None, [], (), "command", 42, True])
def test_validate_owner_action_command_request_accepts_only_dict_input(invalid_input):
    with pytest.raises((TypeError, ValueError)):
        review_api.validate_owner_action_command_request(invalid_input)


@pytest.mark.parametrize("missing_field", sorted(OWNER_ACTION_REQUIRED_FIELDS))
def test_validate_owner_action_command_request_requires_mandatory_audit_and_safety_fields(missing_field):
    request = valid_owner_action_command()
    del request[missing_field]

    with pytest.raises((TypeError, ValueError)):
        review_api.validate_owner_action_command_request(request)


def test_validate_owner_action_command_request_requires_actor_ref_or_actor_id():
    request = valid_owner_action_command()
    request.pop("actor_ref")

    with pytest.raises((TypeError, ValueError)):
        review_api.validate_owner_action_command_request(request)


@pytest.mark.parametrize("command", OWNER_ACTION_ALLOWED_COMMANDS)
def test_validate_owner_action_command_request_accepts_only_t003_allowed_commands(command):
    request = valid_owner_action_command(action_command=command)
    result = review_api.validate_owner_action_command_request(request)

    assert result["action_command"] == command
    assert result is not request
    assert set(result) <= OWNER_ACTION_REQUIRED_FIELDS | OWNER_ACTION_OPTIONAL_FIELDS


@pytest.mark.parametrize("command", OWNER_ACTION_FORBIDDEN_COMMANDS)
def test_validate_owner_action_command_request_rejects_t003_forbidden_commands(command):
    request = valid_owner_action_command(action_command=command)

    with pytest.raises((TypeError, ValueError)):
        review_api.validate_owner_action_command_request(request)


@pytest.mark.parametrize("field", OWNER_ACTION_FORBIDDEN_FIELDS)
def test_validate_owner_action_command_request_rejects_forbidden_and_unknown_fields(field):
    request = valid_owner_action_command(**{field: "blocked"})

    with pytest.raises((TypeError, ValueError)):
        review_api.validate_owner_action_command_request(request)


@pytest.mark.parametrize(
    "flag",
    [
        "human_review_required",
        "no_promotion_requested",
        "no_memory_canon_mutation_requested",
    ],
)
def test_validate_owner_action_command_request_rejects_false_safety_affirmations(flag):
    request = valid_owner_action_command(**{flag: False})

    with pytest.raises((TypeError, ValueError)):
        review_api.validate_owner_action_command_request(request)


@pytest.mark.parametrize("id_field", ["project_id", "queue_entry_id", "candidate_record_id"])
@pytest.mark.parametrize("unsafe_value", UNSAFE_ID_VALUES)
def test_validate_owner_action_command_request_rejects_unsafe_ids_and_path_traversal(id_field, unsafe_value):
    request = valid_owner_action_command(**{id_field: unsafe_value})

    with pytest.raises((TypeError, ValueError)):
        review_api.validate_owner_action_command_request(request)


def test_validate_owner_action_command_request_does_not_mutate_caller_input():
    request = valid_owner_action_command()
    original = valid_owner_action_command()

    result = review_api.validate_owner_action_command_request(request)

    assert request == original
    assert result is not request


def test_build_owner_action_command_response_returns_workflow_only_shape():
    response = review_api.build_owner_action_command_response(
        valid_owner_action_command(),
        owner_action_record=valid_owner_action_response()["owner_action_record"],
        queue_entry=valid_queue_entry(),
    )

    assert OWNER_ACTION_RESPONSE_REQUIRED_FIELDS <= set(response)
    assert response["human_review_required"] is True
    assert response["no_promotion_performed"] is True
    assert response["no_memory_canon_mutation"] is True
    assert_no_forbidden_keys(response, OWNER_ACTION_RESPONSE_FORBIDDEN_FIELDS)


def test_readonly_validators_and_response_builders_create_no_files(tmp_path):
    before = existing_relative_paths(tmp_path)

    review_api.validate_review_queue_read_request(valid_read_request())
    review_api.validate_owner_action_command_request(valid_owner_action_command())
    review_api.build_owner_action_command_response(
        valid_owner_action_command(),
        owner_action_record=valid_owner_action_response()["owner_action_record"],
        queue_entry=valid_queue_entry(),
    )

    assert existing_relative_paths(tmp_path) == before
    for forbidden in FORBIDDEN_SIDE_EFFECT_PATHS:
        assert not (tmp_path / forbidden).exists(), forbidden


def test_future_review_api_contract_must_not_write_forbidden_project_paths(tmp_path):
    review_api.validate_review_queue_read_request(valid_read_request(project_id=PROJECT_ID))

    for forbidden in FORBIDDEN_SIDE_EFFECT_PATHS:
        forbidden_path = tmp_path / forbidden
        assert not forbidden_path.exists(), forbidden_path
    assert not list(tmp_path.rglob("*.jsonl"))


def test_future_review_api_source_has_no_route_runtime_prose_raw_or_mutation_implementation_terms():
    source_file = Path(review_api.__file__)
    source = source_file.read_text(encoding="utf-8")

    for term in FORBIDDEN_SOURCE_TERMS:
        assert term not in source, term
