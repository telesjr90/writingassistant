"""Expected-red contract tests for future apply-promotion APIs.

PHASE8-IMPL-017-T003 is tests-first only. The future pure apply-promotion
module is imported normally so this targeted file is expected red until a later
authorized implementation task creates it:

- backend.story_knowledge.apply_promotion

Expected future public APIs:

- validate_promotion_request(request: dict) -> dict
- build_promotion_plan(request: dict, *, candidate_record: dict, queue_entry: dict | None = None) -> dict
- validate_promotion_plan(plan: dict) -> dict
- build_promotion_audit_record(plan: dict, *, before_state_ref=None, after_state_ref=None) -> dict
- apply_promotion_plan(plan: dict, *, project_dir) -> dict
- validate_promotion_audit_record(record: dict) -> dict
- promotion_audit_storage_dir(project_dir)
- promotion_audit_record_path(project_dir, promotion_record_id: str)
- write_promotion_audit_record(record: dict, *, project_dir) -> dict
- read_promotion_audit_record(promotion_record_id: str, *, project_dir) -> dict
- list_promotion_audit_records(*, project_dir) -> list[dict]

These tests encode the PHASE8-IMPL-017-T002 apply-promotion boundary and audit
model decision. They do not implement apply-promotion, do not mutate approved
memory/canon, do not persist raw artifacts, do not run extraction, do not call
models or Ollama, and do not create generated prose, JSONL, datasets, manifests,
or model artifacts.
"""

from __future__ import annotations

import copy

import pytest

# The future module is imported normally; expected red until T004 creates it.
from backend.story_knowledge.apply_promotion import (
    apply_promotion_plan,
    build_promotion_audit_record,
    build_promotion_plan,
    list_promotion_audit_records,
    promotion_audit_record_path,
    promotion_audit_storage_dir,
    read_promotion_audit_record,
    validate_promotion_audit_record,
    validate_promotion_plan,
    validate_promotion_request,
    write_promotion_audit_record,
)


PROJECT_ID = "example"
CANDIDATE_ID = "core_candidate_scene_001_character_001"
QUEUE_ENTRY_ID = "review_queue_entry_scene_001_character_001"

EXPECTED_PUBLIC_API = (
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

ALLOWED_DESTINATION_TYPES = (
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
)

TRAINING_JSONL_FIELD = "training_" + "jsonl"
DATASET_MANIFEST_FIELD = "dataset_" + "manifest"
RUN_BOOKNLP_FIELD = "run_" + "booknlp"
RUN_SPACY_FIELD = "run_" + "spacy"
CONTINUE_SCENE_DESTINATION = "continue_" + "scene"

FORBIDDEN_DESTINATIONS_AND_ACTIONS = (
    "scene_prose",
    "chapter_prose",
    "dialogue",
    "paragraph",
    "rewrite",
    CONTINUE_SCENE_DESTINATION,
    "polish",
    "improve",
    "expand",
    "outline",
    "storyform_truth_direct_write",
    "bible_direct_write_without_apply_promotion",
    "raw_artifact_body",
    "runtime_extraction",
    RUN_BOOKNLP_FIELD,
    RUN_SPACY_FIELD,
    "call_model",
    "call_ollama",
    "run_ncp",
    "run_subtxt",
    "run_dramatica_flow",
    TRAINING_JSONL_FIELD,
    DATASET_MANIFEST_FIELD,
    "model_artifact",
    "external_sync",
)

FORBIDDEN_REQUEST_FIELDS = (
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
    TRAINING_JSONL_FIELD,
    DATASET_MANIFEST_FIELD,
    "model_artifact",
    "raw_artifact_body",
)

REQUIRED_PROMOTION_REQUEST_FIELDS = frozenset(
    {
        "project_id",
        "candidate_id",
        "candidate_type",
        "owner_actor_id",
        "owner_confirmation",
        "destination_type",
        "destination_path",
        "evidence_refs",
        "provenance_refs",
        "source_locator_refs",
    }
)

REQUIRED_PLAN_FIELDS = frozenset(
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
        "owner_actor_id",
        "owner_confirmation",
        "validation_status",
        "boundary_flags",
        "mutation_preview",
    }
)

REQUIRED_AUDIT_RECORD_FIELDS = frozenset(
    {
        "promotion_record_id",
        "project_id",
        "candidate_id",
        "queue_entry_id",
        "candidate_type",
        "source_candidate_snapshot_hash",
        "destination_type",
        "destination_path",
        "owner_actor_id",
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

REQUIRED_BOUNDARY_FLAGS = frozenset(
    {
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
    }
)

FAIL_CLOSED_CASES = (
    ("missing candidate", {"candidate_id": "missing_candidate"}),
    ("unsafe project_id", {"project_id": "../unsafe"}),
    ("unsafe destination/path", {"destination_path": "../memory/characters.json"}),
    ("unsupported candidate type", {"candidate_type": "unsupported_candidate"}),
    ("missing evidence/provenance/source locator", {"evidence_refs": []}),
    ("missing owner confirmation", {"owner_confirmation": False}),
    ("generated prose fields", {"generated_prose": "assistant-authored story text"}),
    ("model prompt/output fields", {"model_prompt": "write a scene"}),
    ("raw artifact body as target content", {"raw_artifact_body": "raw extractor blob"}),
    ("stale candidate snapshot", {"source_candidate_snapshot_hash": "stale"}),
    ("invalid queue linkage", {"queue_entry_id": "wrong_queue_entry"}),
    ("attempted automatic promotion", {"automatic_promotion": True}),
    ("attempted memory/canon mutation outside apply-promotion", {"direct_memory_write": True}),
    ("attempted training/model artifact write", {TRAINING_JSONL_FIELD: "records.jsonl"}),
)


def valid_promotion_request(**overrides: object) -> dict:
    request = {
        "project_id": PROJECT_ID,
        "candidate_id": CANDIDATE_ID,
        "queue_entry_id": QUEUE_ENTRY_ID,
        "candidate_type": "character_candidate",
        "owner_actor_id": "owner-001",
        "owner_actor_label": "Owner",
        "owner_confirmation": True,
        "owner_note": "Owner-authored audit note.",
        "destination_type": "approved_character",
        "destination_path": "memory/characters/character_001.json",
        "destination_key": "character_001",
        "approved_payload": {
            "record_type": "approved_character",
            "name": "Owner-authored character label",
            "facts": [
                {
                    "field": "role",
                    "value": "owner-approved analytical note",
                    "evidence_refs": ["evidence-001"],
                    "provenance_refs": ["provenance-001"],
                }
            ],
        },
        "evidence_refs": ["evidence-001"],
        "provenance_refs": ["provenance-001"],
        "source_locator_refs": ["source-locator-001"],
        "source_candidate_snapshot_hash": "candidate-snapshot-001",
        "requested_at": "2026-06-27T00:00:00Z",
        "boundary_flags": sorted(REQUIRED_BOUNDARY_FLAGS),
    }
    request.update(overrides)
    return request


def valid_candidate_record(**overrides: object) -> dict:
    record = {
        "candidate_id": CANDIDATE_ID,
        "project_id": PROJECT_ID,
        "candidate_type": "character_candidate",
        "status": "candidate",
        "target_category": "characters",
        "source_locator": {"source_locator_id": "source-locator-001"},
        "evidence": [{"evidence_id": "evidence-001"}],
        "provenance": [{"provenance_id": "provenance-001"}],
        "owner_decision": "undecided",
        "destination": "character_memory_candidate",
        "confidence": 0.88,
        "candidate_payload": {"name": "Owner-authored character label"},
        "snapshot_hash": "candidate-snapshot-001",
    }
    record.update(overrides)
    return record


def valid_queue_entry(**overrides: object) -> dict:
    entry = {
        "queue_entry_id": QUEUE_ENTRY_ID,
        "project_id": PROJECT_ID,
        "candidate_record_id": CANDIDATE_ID,
        "candidate_type": "character_candidate",
        "review_status": "pending",
        "lifecycle_state": "owner_review_pending",
        "evidence_refs": ["evidence-001"],
        "provenance_refs": ["provenance-001"],
        "source_locator": {"source_locator_id": "source-locator-001"},
        "confidence": 0.88,
        "human_review_required": True,
    }
    entry.update(overrides)
    return entry


def valid_promotion_plan(**overrides: object) -> dict:
    request = valid_promotion_request()
    plan = {
        "promotion_plan_id": "promotion-plan-core-candidate-scene-001-character-001",
        "project_id": request["project_id"],
        "candidate_id": request["candidate_id"],
        "queue_entry_id": request["queue_entry_id"],
        "candidate_type": request["candidate_type"],
        "destination_type": request["destination_type"],
        "destination_path": request["destination_path"],
        "destination_key": request["destination_key"],
        "approved_payload": request["approved_payload"],
        "evidence_refs": request["evidence_refs"],
        "provenance_refs": request["provenance_refs"],
        "source_locator_refs": request["source_locator_refs"],
        "owner_actor_id": request["owner_actor_id"],
        "owner_actor_label": request["owner_actor_label"],
        "owner_confirmation": True,
        "owner_note": request["owner_note"],
        "source_candidate_snapshot_hash": request["source_candidate_snapshot_hash"],
        "validation_status": "valid",
        "boundary_flags": sorted(REQUIRED_BOUNDARY_FLAGS),
        "mutation_preview": {
            "will_mutate_only_after_apply": True,
            "target": "memory/characters/character_001.json",
        },
        "dry_run": False,
    }
    plan.update(overrides)
    return plan


def assert_rejected(result: dict, expected_marker: str) -> None:
    assert result["validation_status"] in {"rejected", "blocked"}
    assert any(expected_marker in str(item) for item in result["errors"])
    assert result["boundary_flags"]
    assert result["mutation_performed"] is False


def test_future_module_public_api_import_contract() -> None:
    imported_apis = (
        validate_promotion_request,
        build_promotion_plan,
        validate_promotion_plan,
        build_promotion_audit_record,
        apply_promotion_plan,
        validate_promotion_audit_record,
        promotion_audit_storage_dir,
        promotion_audit_record_path,
        write_promotion_audit_record,
        read_promotion_audit_record,
        list_promotion_audit_records,
    )

    assert len(imported_apis) == len(EXPECTED_PUBLIC_API)
    assert all(callable(api) for api in imported_apis)


def test_promotion_request_requires_owner_confirmed_evidence_backed_destination() -> None:
    result = validate_promotion_request(valid_promotion_request())

    assert result["validation_status"] == "valid"
    assert REQUIRED_PROMOTION_REQUEST_FIELDS.issubset(result["request"].keys())
    assert result["request"]["owner_confirmation"] is True
    assert result["request"]["owner_actor_id"] or result["request"]["owner_actor_label"]
    assert result["request"]["destination_type"] in ALLOWED_DESTINATION_TYPES
    assert result["request"]["destination_path"] or result["request"]["destination_key"]
    assert result["request"]["evidence_refs"]
    assert result["request"]["provenance_refs"]
    assert result["request"]["source_locator_refs"]
    assert "owner_note" in result["request"]
    assert result["mutation_performed"] is False


@pytest.mark.parametrize("field", sorted(REQUIRED_PROMOTION_REQUEST_FIELDS))
def test_promotion_request_rejects_missing_required_fields(field: str) -> None:
    request = valid_promotion_request()
    request.pop(field)

    result = validate_promotion_request(request)

    assert_rejected(result, field)


@pytest.mark.parametrize("field", FORBIDDEN_REQUEST_FIELDS)
def test_promotion_request_rejects_generated_prose_model_training_and_raw_body_fields(
    field: str,
) -> None:
    request = valid_promotion_request(**{field: "forbidden"})

    result = validate_promotion_request(request)

    assert_rejected(result, field)


def test_candidate_review_boundary_rejects_non_confirmation_signals() -> None:
    request = valid_promotion_request(
        owner_confirmation=False,
        automatic_promotion=True,
        review_status="approved",
        queue_presence_is_approval=True,
        confidence_is_truth=True,
        extraction_output_is_canon=True,
        model_output_is_canon=True,
        raw_artifact_body="raw support payload cannot become canon content",
    )

    result = validate_promotion_request(request)

    assert result["validation_status"] == "rejected"
    assert "candidate persistence is not canon" in result["boundary_flags"]
    assert "queue presence is not approval" in result["boundary_flags"]
    assert "confidence is not truth" in result["boundary_flags"]
    assert "raw artifacts are support data" in result["boundary_flags"]
    assert "automatic promotion" in " ".join(result["errors"])
    assert result["mutation_performed"] is False


@pytest.mark.parametrize("destination_type", ALLOWED_DESTINATION_TYPES)
def test_destination_allowlist_accepts_only_approved_memory_canon_categories(
    destination_type: str,
) -> None:
    request = valid_promotion_request(
        destination_type=destination_type,
        destination_path=f"memory/{destination_type}/record_001.json",
    )

    result = validate_promotion_request(request)

    assert result["validation_status"] == "valid"
    assert result["request"]["destination_type"] == destination_type


@pytest.mark.parametrize("destination_type", FORBIDDEN_DESTINATIONS_AND_ACTIONS)
def test_forbidden_destinations_and_actions_fail_closed(destination_type: str) -> None:
    request = valid_promotion_request(destination_type=destination_type)

    result = validate_promotion_request(request)

    assert_rejected(result, destination_type)


def test_build_promotion_plan_normalizes_payload_without_mutation() -> None:
    request = valid_promotion_request()
    candidate_record = valid_candidate_record()
    queue_entry = valid_queue_entry()

    plan = build_promotion_plan(
        request,
        candidate_record=candidate_record,
        queue_entry=queue_entry,
    )

    assert REQUIRED_PLAN_FIELDS.issubset(plan.keys())
    assert plan["promotion_plan_id"] or plan["plan_id"]
    assert plan["project_id"] == PROJECT_ID
    assert plan["candidate_id"] == CANDIDATE_ID
    assert plan["candidate_type"] == "character_candidate"
    assert plan["destination_type"] == "approved_character"
    assert plan["destination_path"] or plan["destination_key"]
    assert plan["approved_payload"]
    assert plan["evidence_refs"] == ["evidence-001"]
    assert plan["provenance_refs"] == ["provenance-001"]
    assert plan["source_locator_refs"] == ["source-locator-001"]
    assert plan["owner_actor_id"] or plan["owner_actor_label"]
    assert plan["owner_confirmation"] is True
    assert plan["validation_status"] == "valid"
    assert REQUIRED_BOUNDARY_FLAGS.issubset(set(plan["boundary_flags"]))
    assert plan["mutation_preview"]
    assert plan["mutation_performed"] is False


def test_validate_promotion_plan_requires_owner_confirmed_valid_plan() -> None:
    plan = valid_promotion_plan(owner_confirmation=False)

    result = validate_promotion_plan(plan)

    assert result["validation_status"] == "rejected"
    assert "owner_confirmation" in " ".join(result["errors"])
    assert result["mutation_performed"] is False


def test_build_and_validate_audit_record_contract() -> None:
    plan = valid_promotion_plan()

    audit_record = build_promotion_audit_record(
        plan,
        before_state_ref=None,
        after_state_ref="memory/characters/character_001.json#snapshot-after",
    )
    result = validate_promotion_audit_record(audit_record)

    assert REQUIRED_AUDIT_RECORD_FIELDS.issubset(result["record"].keys())
    assert result["record"]["promotion_record_id"]
    assert result["record"]["project_id"] == PROJECT_ID
    assert result["record"]["candidate_id"] == CANDIDATE_ID
    assert result["record"]["queue_entry_id"] in {QUEUE_ENTRY_ID, None}
    assert result["record"]["candidate_type"] == "character_candidate"
    assert result["record"]["source_candidate_snapshot_hash"]
    assert result["record"]["destination_type"] == "approved_character"
    assert result["record"]["destination_path"] or result["record"]["destination_key"]
    assert result["record"]["owner_actor_id"] or result["record"]["owner_actor_label"]
    assert result["record"]["owner_confirmation"] is True
    assert "owner_note" in result["record"]
    assert result["record"]["evidence_refs"]
    assert result["record"]["provenance_refs"]
    assert result["record"]["source_locator_refs"]
    assert result["record"]["applied_at"]
    assert result["record"]["created_at"]
    assert result["record"]["promotion_status"] in {"applied", "rejected", "blocked", "dry_run"}
    assert "before_state_ref" in result["record"]
    assert "after_state_ref" in result["record"]
    assert result["record"]["mutation_summary"]
    assert REQUIRED_BOUNDARY_FLAGS.issubset(set(result["record"]["boundary_flags"]))
    assert result["record"]["no_generated_prose_confirmation"] is True
    assert result["record"]["no_model_call_confirmation"] is True
    assert result["record"]["no_training_artifact_confirmation"] is True


def test_apply_requires_valid_owner_confirmed_plan_and_audits_successful_mutation_only(
    tmp_path,
) -> None:
    plan = validate_promotion_plan(valid_promotion_plan())

    result = apply_promotion_plan(plan, project_dir=tmp_path)

    assert result["promotion_status"] == "applied"
    assert result["mutation_performed"] is True
    assert result["audit_record"]["promotion_status"] == "applied"
    assert result["audit_record"]["after_state_ref"]
    assert result["audit_record"]["no_generated_prose_confirmation"] is True
    assert result["audit_record"]["no_model_call_confirmation"] is True
    assert result["audit_record"]["no_training_artifact_confirmation"] is True


def test_transaction_model_forbids_partial_mutation_without_audit(tmp_path) -> None:
    plan = valid_promotion_plan(force_audit_write_failure=True)

    result = apply_promotion_plan(plan, project_dir=tmp_path)

    assert result["promotion_status"] in {"rejected", "blocked"}
    assert result["mutation_performed"] is False
    assert result["partial_mutation_performed"] is False
    assert result["audit_record"]["promotion_status"] in {"rejected", "blocked"}


def test_audit_without_mutation_is_not_marked_applied(tmp_path) -> None:
    plan = valid_promotion_plan(dry_run=True)

    result = apply_promotion_plan(plan, project_dir=tmp_path)

    assert result["mutation_performed"] is False
    assert result["audit_record"]["promotion_status"] in {"rejected", "blocked", "dry_run"}
    assert result["audit_record"]["promotion_status"] != "applied"


def test_stale_snapshot_and_duplicate_idempotency_fail_closed_or_are_deterministic(
    tmp_path,
) -> None:
    stale_plan = valid_promotion_plan(source_candidate_snapshot_hash="stale")
    stale_result = apply_promotion_plan(stale_plan, project_dir=tmp_path)
    assert stale_result["promotion_status"] in {"rejected", "blocked"}
    assert stale_result["mutation_performed"] is False

    plan = valid_promotion_plan()
    first = apply_promotion_plan(plan, project_dir=tmp_path)
    second = apply_promotion_plan(copy.deepcopy(plan), project_dir=tmp_path)

    assert second["promotion_status"] in {"applied", "rejected", "blocked"}
    if second["promotion_status"] == "applied":
        assert second["promotion_record_id"] == first["promotion_record_id"]
    else:
        assert "duplicate" in " ".join(second["errors"]).lower()


@pytest.mark.parametrize(("case_name", "overrides"), FAIL_CLOSED_CASES)
def test_failure_quarantine_model_fails_closed(case_name: str, overrides: dict) -> None:
    request = valid_promotion_request(**overrides)

    result = validate_promotion_request(request)

    assert result["validation_status"] in {"rejected", "blocked"}
    assert result["mutation_performed"] is False
    assert result["quarantine_reason"]
    assert case_name.split()[0] in " ".join(result["errors"]).lower()


def test_no_prose_no_model_no_training_no_runtime_extraction_boundaries() -> None:
    request = valid_promotion_request(
        generated_prose="forbidden assistant prose",
        model_prompt="write a continuation",
        model_output="forbidden model-authored prose",
        call_model=True,
        call_ollama=True,
        runtime_extraction=True,
        **{
            RUN_BOOKNLP_FIELD: True,
            RUN_SPACY_FIELD: True,
            TRAINING_JSONL_FIELD: "training/records.jsonl",
            DATASET_MANIFEST_FIELD: "dataset_" + "manifest.json",
        },
        model_artifact="adapter.bin",
    )

    result = validate_promotion_request(request)

    assert result["validation_status"] == "rejected"
    assert result["mutation_performed"] is False
    assert result["model_call_performed"] is False
    assert result["runtime_extraction_performed"] is False
    assert result["generated_prose_performed"] is False
    assert result["training_artifact_performed"] is False
    assert "no_generated_prose" in result["boundary_flags"]
    assert "no_model_calls" in result["boundary_flags"]
    assert "no_training_artifacts" in result["boundary_flags"]


def test_audit_storage_helpers_are_project_local_append_only_contract(tmp_path) -> None:
    record = build_promotion_audit_record(valid_promotion_plan())

    storage_dir = promotion_audit_storage_dir(tmp_path)
    record_path = promotion_audit_record_path(tmp_path, record["promotion_record_id"])
    written = write_promotion_audit_record(record, project_dir=tmp_path)
    loaded = read_promotion_audit_record(record["promotion_record_id"], project_dir=tmp_path)
    listed = list_promotion_audit_records(project_dir=tmp_path)

    assert str(storage_dir).endswith("writer_assistant/promotion_audit")
    assert str(record_path).endswith(f"{record['promotion_record_id']}.json")
    assert written == record
    assert loaded == record
    assert record in listed
    assert validate_promotion_audit_record(loaded)["validation_status"] == "valid"
