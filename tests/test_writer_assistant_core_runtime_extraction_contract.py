"""Expected-red contract tests for guarded runtime extraction.

PHASE8-IMPL-019-T003 is tests-first only. The future guarded runtime extraction
module is imported normally so this file is expected red until a later
authorized implementation task creates it:

- backend.story_knowledge.runtime_extraction

Expected future public APIs:

- validate_runtime_extraction_environment(config: dict) -> dict
- check_booknlp_availability(config: dict) -> dict
- check_spacy_availability(config: dict) -> dict
- validate_runtime_extraction_request(request: dict) -> dict
- build_runtime_extraction_plan(request: dict, environment: dict) -> dict
- run_runtime_extraction_probe(plan: dict, *, project_dir) -> dict
- run_guarded_runtime_extraction(plan: dict, *, project_dir) -> dict
- build_raw_artifact_handoff(runtime_output: dict, *, project_dir) -> dict
- build_candidate_review_handoff(raw_handoff: dict, request: dict) -> dict
- quarantine_runtime_extraction_output(runtime_output: dict, reason: str, *, project_dir) -> dict

These tests encode the PHASE8-IMPL-019-T002 guarded runtime extraction boundary:
runtime extraction is disabled by default, import availability is separate from
run/probe availability, requests are path-safe and owner-authored or
owner-provided only, output is PHASE8-IMPL-018 raw artifact support data plus
candidate-first owner-review handoff only, and every unsafe path fails closed.

Required boundary source markers:
no_generated_prose no_rewrite no_continuation no_style_imitation no_polish
no_improvement no_outline_generation no_chapter_generation no_model_prompt
no_model_completion no_ollama no_model_calls no_training_jsonl
no_dataset_manifest no_model_artifact no_apply_promotion
no_memory_canon_mutation no_automatic_canon candidate_first
owner_review_required fail_closed no_silent_fallback

These tests do not implement runtime extraction, do not install/import/run
BookNLP or spaCy, do not call models or Ollama, do not call NCP/Subtxt/
dramatica-flow runtimes, do not create canon, candidates, review queue entries,
training artifacts, dataset manifests, model artifacts, or generated prose, and
do not mutate approved memory/canon.
"""

from __future__ import annotations

import copy
from pathlib import Path

import pytest

# The future module is imported normally; expected red until T004 creates it.
from backend.story_knowledge.runtime_extraction import (
    build_candidate_review_handoff,
    build_raw_artifact_handoff,
    build_runtime_extraction_plan,
    check_booknlp_availability,
    check_spacy_availability,
    quarantine_runtime_extraction_output,
    run_guarded_runtime_extraction,
    run_runtime_extraction_probe,
    validate_runtime_extraction_environment,
    validate_runtime_extraction_request,
)


PROJECT_ID = "example_project"
EXTRACTION_REQUEST_ID = "runtime_extract_001"
SOURCE_ID = "owner_scene_001"
SOURCE_REF = "source_ref_owner_scene_001"
EVIDENCE_REF = "evidence_ref_owner_scene_001_span_001"
PROVENANCE_REF = "provenance_ref_runtime_probe_001"
SOURCE_LOCATOR_REF = "source_locator_ref_owner_scene_001_offsets_001"
RAW_ARTIFACT_BUNDLE_ID = "raw_artifact_runtime_001"

EXPECTED_PUBLIC_API = (
    "validate_runtime_extraction_environment",
    "check_booknlp_availability",
    "check_spacy_availability",
    "validate_runtime_extraction_request",
    "build_runtime_extraction_plan",
    "run_runtime_extraction_probe",
    "run_guarded_runtime_extraction",
    "build_raw_artifact_handoff",
    "build_candidate_review_handoff",
    "quarantine_runtime_extraction_output",
)

RUNTIME_STATUS_VALUES = frozenset(
    {
        "configured",
        "disabled",
        "unavailable",
        "dependency_missing",
        "model_missing",
        "configuration_invalid",
        "probe_failed",
        "runtime_failed",
        "malformed_output",
        "unsafe_path",
        "missing_source_refs",
        "missing_evidence_refs",
        "missing_provenance_refs",
        "missing_source_locator_refs",
        "quarantined",
        "rejected",
        "valid",
        "fail_closed",
    }
)

UNAVAILABLE_STATUS_VALUES = frozenset(
    {
        "disabled",
        "unavailable",
        "dependency_missing",
        "model_missing",
        "configuration_invalid",
        "probe_failed",
        "runtime_failed",
        "malformed_output",
        "unsafe_path",
        "quarantined",
        "rejected",
        "fail_closed",
    }
)

REQUIRED_ENVIRONMENT_FIELDS = frozenset(
    {
        "status",
        "runtime_extraction_enabled",
        "booknlp",
        "spacy",
        "availability",
        "fail_closed",
        "errors",
        "warnings",
        "no_silent_fallback",
        "no_model_calls",
        "no_generated_prose",
        "no_training_artifacts",
    }
)

REQUIRED_AVAILABILITY_FIELDS = frozenset(
    {
        "tool_name",
        "status",
        "enabled",
        "configured",
        "import_available",
        "run_available",
        "probe_available",
        "dependency_missing",
        "model_missing",
        "configuration_invalid",
        "probe_status",
        "fail_closed",
        "errors",
        "warnings",
    }
)

REQUEST_REQUIRED_FIELDS = frozenset(
    {
        "project_id",
        "extraction_request_id",
        "source_type",
        "source_id",
        "source_ref",
        "requested_extractors",
        "requested_artifact_types",
        "source_refs",
        "evidence_refs",
        "provenance_refs",
        "source_locator_refs",
        "source_locators",
        "boundary_confirmations",
        "environment_profile",
        "max_input_chars",
        "timeout_seconds",
        "requested_by",
        "created_at",
    }
)

REQUIRED_BOUNDARY_CONFIRMATIONS = frozenset(
    {
        "owner_authored_or_owner_provided_source_confirmation",
        "no_generated_prose_confirmation",
        "no_model_call_confirmation",
        "no_training_artifact_confirmation",
        "no_apply_promotion_confirmation",
        "no_memory_canon_mutation_confirmation",
        "raw_artifact_support_data_only_confirmation",
        "candidate_first_owner_review_required_confirmation",
    }
)

ALLOWED_SOURCE_TYPES = ("owner_authored_scene", "owner_authored_note", "owner_provided_material")
ALLOWED_EXTRACTORS = ("booknlp", "spacy")
ALLOWED_ARTIFACT_TYPES = (
    "source_snapshot",
    "token_table",
    "entity_table",
    "quote_table",
    "event_table",
    "coref_table",
    "dependency_table",
    "offset_map",
    "source_map",
    "evidence_map",
    "provenance_map",
    "adapter_metadata",
    "parser_metadata",
    "normalized_intermediate",
)

FORBIDDEN_REQUESTED_TYPES_AND_FIELDS = (
    "generated_prose",
    "rewritten_prose",
    "rewrite",
    "continuation",
    "outline",
    "model_prompt",
    "model_completion",
    "training_jsonl",
    "dataset_manifest",
    "model_artifact",
    "promotion_record",
    "candidate_record",
    "review_queue_entry",
    "approved_memory",
    "canon",
    "bible",
    "storyform",
    "scene_mutation",
    "note_mutation",
    "material_mutation",
)

FORBIDDEN_SIDE_EFFECT_DIRS_OR_FILES = (
    "approved_memory",
    "memory",
    "canon",
    "promotion_audit",
    "review_queue",
    "candidates",
    "candidate_index",
    "bible.json",
    "storyform.json",
    "scenes",
    "notes",
    "materials",
    "training",
    "dataset_manifest.json",
    "model_artifacts",
)

QUARANTINE_REASONS = (
    "malformed_output",
    "unsafe_path",
    "missing_evidence_refs",
    "missing_provenance_refs",
    "missing_source_locator_refs",
    "dependency_missing",
    "model_missing",
    "probe_failed",
    "runtime_failed",
)

UNSAFE_IDS_AND_REFS = (
    "../escape",
    "..",
    ".",
    "/absolute",
    "C:\\escape",
    "folder/name",
    "folder\\name",
    "",
    "   ",
    "runtime_extract.json",
    "runtime_extract_../escape",
)


def _enabled_environment() -> dict:
    return {
        "WRITER_ASSISTANT_RUNTIME_EXTRACTION_ENABLED": "1",
        "WRITER_ASSISTANT_BOOKNLP_ENABLED": "1",
        "WRITER_ASSISTANT_SPACY_ENABLED": "1",
        "WRITER_ASSISTANT_BOOKNLP_MODEL_DIR": "models/booknlp",
        "WRITER_ASSISTANT_BOOKNLP_JAVA_HOME": "runtime/java",
        "WRITER_ASSISTANT_SPACY_MODEL": "en_core_web_sm",
        "WRITER_ASSISTANT_EXTRACTION_TIMEOUT_SECONDS": "30",
        "WRITER_ASSISTANT_EXTRACTION_MAX_INPUT_CHARS": "5000",
    }


def _valid_request() -> dict:
    return {
        "project_id": PROJECT_ID,
        "extraction_request_id": EXTRACTION_REQUEST_ID,
        "source_type": "owner_authored_scene",
        "source_id": SOURCE_ID,
        "source_ref": SOURCE_REF,
        "requested_extractors": ["booknlp", "spacy"],
        "requested_artifact_types": ["token_table", "entity_table", "source_map"],
        "source_refs": [SOURCE_REF],
        "evidence_refs": [EVIDENCE_REF],
        "provenance_refs": [PROVENANCE_REF],
        "source_locator_refs": [SOURCE_LOCATOR_REF],
        "source_locators": [
            {
                "source_locator_ref": SOURCE_LOCATOR_REF,
                "source_ref": SOURCE_REF,
                "start_offset": 0,
                "end_offset": 42,
            }
        ],
        "boundary_confirmations": {
            key: True for key in REQUIRED_BOUNDARY_CONFIRMATIONS
        },
        "environment_profile": "local_guarded_runtime",
        "max_input_chars": 5000,
        "timeout_seconds": 30,
        "requested_by": "owner",
        "created_at": "2026-06-30T00:00:00Z",
    }


def _valid_availability(tool_name: str) -> dict:
    return {
        "tool_name": tool_name,
        "status": "valid",
        "enabled": True,
        "configured": True,
        "import_available": True,
        "run_available": True,
        "probe_available": True,
        "dependency_missing": False,
        "model_missing": False,
        "configuration_invalid": False,
        "probe_status": "valid",
        "fail_closed": False,
        "errors": [],
        "warnings": [],
    }


def _valid_environment_result() -> dict:
    return {
        "status": "configured",
        "runtime_extraction_enabled": True,
        "booknlp": _valid_availability("booknlp"),
        "spacy": _valid_availability("spacy"),
        "availability": {
            "booknlp": _valid_availability("booknlp"),
            "spacy": _valid_availability("spacy"),
        },
        "fail_closed": False,
        "errors": [],
        "warnings": [],
        "no_silent_fallback": True,
        "no_model_calls": True,
        "no_generated_prose": True,
        "no_training_artifacts": True,
    }


def _runtime_output(status: str = "valid") -> dict:
    return {
        "status": status,
        "project_id": PROJECT_ID,
        "extraction_request_id": EXTRACTION_REQUEST_ID,
        "raw_artifact_bundle_id": RAW_ARTIFACT_BUNDLE_ID,
        "source_refs": [SOURCE_REF],
        "evidence_refs": [EVIDENCE_REF],
        "provenance_refs": [PROVENANCE_REF],
        "source_locator_refs": [SOURCE_LOCATOR_REF],
        "artifact_files": [
            {
                "artifact_file_id": "tokens_001",
                "artifact_type": "token_table",
                "relative_path": "artifacts/tokens.jsonl",
                "source_refs": [SOURCE_REF],
                "evidence_refs": [EVIDENCE_REF],
                "provenance_refs": [PROVENANCE_REF],
                "source_locator_refs": [SOURCE_LOCATOR_REF],
            }
        ],
        "boundary_flags": {
            "raw_artifact_support_data_only": True,
            "candidate_first": True,
            "owner_review_required": True,
            "no_apply_promotion": True,
            "no_memory_canon_mutation": True,
            "no_model_calls": True,
            "no_generated_prose": True,
            "no_training_artifacts": True,
        },
    }


def _assert_failed_closed(result: dict, expected_status: str | None = None) -> None:
    assert result["status"] in UNAVAILABLE_STATUS_VALUES
    if expected_status is not None:
        assert result["status"] == expected_status
    assert result.get("fail_closed") is True
    assert result.get("extraction_succeeded") is not True
    assert result.get("no_silent_fallback") is True


def _assert_availability_shape(result: dict, tool_name: str) -> None:
    assert REQUIRED_AVAILABILITY_FIELDS <= set(result)
    assert result["tool_name"] == tool_name
    assert result["status"] in RUNTIME_STATUS_VALUES
    assert isinstance(result["import_available"], bool)
    assert isinstance(result["run_available"], bool)
    assert isinstance(result["probe_available"], bool)
    assert result["import_available"] is not result.get("available")
    if result["status"] != "valid":
        _assert_failed_closed(result)


def _assert_no_forbidden_side_effects(project_dir: Path) -> None:
    for relative_path in FORBIDDEN_SIDE_EFFECT_DIRS_OR_FILES:
        assert not (project_dir / relative_path).exists(), relative_path


def test_expected_public_api_contract_is_explicit() -> None:
    module_api = {
        "validate_runtime_extraction_environment": validate_runtime_extraction_environment,
        "check_booknlp_availability": check_booknlp_availability,
        "check_spacy_availability": check_spacy_availability,
        "validate_runtime_extraction_request": validate_runtime_extraction_request,
        "build_runtime_extraction_plan": build_runtime_extraction_plan,
        "run_runtime_extraction_probe": run_runtime_extraction_probe,
        "run_guarded_runtime_extraction": run_guarded_runtime_extraction,
        "build_raw_artifact_handoff": build_raw_artifact_handoff,
        "build_candidate_review_handoff": build_candidate_review_handoff,
        "quarantine_runtime_extraction_output": quarantine_runtime_extraction_output,
    }

    assert tuple(module_api) == EXPECTED_PUBLIC_API
    for api_name in EXPECTED_PUBLIC_API:
        assert callable(module_api[api_name])


def test_environment_default_is_disabled_unavailable_and_fail_closed() -> None:
    result = validate_runtime_extraction_environment({})

    assert REQUIRED_ENVIRONMENT_FIELDS <= set(result)
    _assert_failed_closed(result, "disabled")
    assert result["runtime_extraction_enabled"] is False
    assert result["availability"]["booknlp"]["status"] in UNAVAILABLE_STATUS_VALUES
    assert result["availability"]["spacy"]["status"] in UNAVAILABLE_STATUS_VALUES
    assert result["no_model_calls"] is True
    assert result["no_generated_prose"] is True
    assert result["no_training_artifacts"] is True


@pytest.mark.parametrize("status", sorted(RUNTIME_STATUS_VALUES))
def test_environment_contract_distinguishes_required_states(status: str) -> None:
    env = _enabled_environment()
    env["WRITER_ASSISTANT_RUNTIME_EXTRACTION_FORCED_STATUS"] = status

    result = validate_runtime_extraction_environment(env)

    assert result["status"] in RUNTIME_STATUS_VALUES
    if status in UNAVAILABLE_STATUS_VALUES:
        _assert_failed_closed(result, status)
    if result["status"] == "valid":
        assert result["fail_closed"] is False
    assert result["no_silent_fallback"] is True


@pytest.mark.parametrize(
    ("tool_name", "checker"),
    (
        ("booknlp", check_booknlp_availability),
        ("spacy", check_spacy_availability),
    ),
)
def test_availability_checks_are_objects_not_boolean_only(tool_name: str, checker) -> None:
    result = checker(_enabled_environment())

    _assert_availability_shape(result, tool_name)
    assert isinstance(result, dict)
    assert result is not True
    assert result is not False


@pytest.mark.parametrize(
    "failure_status",
    ("dependency_missing", "model_missing", "configuration_invalid", "probe_failed"),
)
def test_dependency_model_and_probe_failures_fail_closed(failure_status: str) -> None:
    env = _enabled_environment()
    env["WRITER_ASSISTANT_BOOKNLP_FORCED_STATUS"] = failure_status
    env["WRITER_ASSISTANT_SPACY_FORCED_STATUS"] = failure_status

    booknlp = check_booknlp_availability(env)
    spacy = check_spacy_availability(env)

    _assert_failed_closed(booknlp, failure_status)
    _assert_failed_closed(spacy, failure_status)
    assert booknlp["import_available"] is not booknlp["run_available"] or failure_status != "probe_failed"
    assert spacy["import_available"] is not spacy["probe_available"] or failure_status != "probe_failed"


def test_runtime_probe_success_is_not_runtime_extraction_success(tmp_path: Path) -> None:
    request = validate_runtime_extraction_request(_valid_request())
    plan = build_runtime_extraction_plan(request, _valid_environment_result())

    probe = run_runtime_extraction_probe(plan, project_dir=tmp_path)

    assert probe["status"] == "valid"
    assert probe["probe_succeeded"] is True
    assert probe["runtime_extraction_succeeded"] is False
    assert probe["canon_write_performed"] is False
    assert probe["candidate_persistence_performed"] is False
    assert probe["review_queue_write_performed"] is False
    assert probe["model_call_performed"] is False
    assert probe["generated_prose"] is False
    assert probe["training_artifact_created"] is False
    _assert_no_forbidden_side_effects(tmp_path)


def test_request_validation_accepts_only_owner_sources_support_data_and_confirmations() -> None:
    result = validate_runtime_extraction_request(_valid_request())

    assert result["status"] == "valid"
    assert REQUEST_REQUIRED_FIELDS <= set(result["request"])
    assert set(result["request"]["requested_extractors"]) <= set(ALLOWED_EXTRACTORS)
    assert set(result["request"]["requested_artifact_types"]) <= set(ALLOWED_ARTIFACT_TYPES)
    assert REQUIRED_BOUNDARY_CONFIRMATIONS <= set(result["request"]["boundary_confirmations"])
    assert result["owner_authored_or_owner_provided_source"] is True
    assert result["support_data_only"] is True
    assert result["candidate_first"] is True
    assert result["owner_review_required"] is True


@pytest.mark.parametrize("field_name", ("project_id", "extraction_request_id", "source_id", "source_ref"))
@pytest.mark.parametrize("unsafe_value", UNSAFE_IDS_AND_REFS)
def test_request_validation_rejects_unsafe_ids_and_refs(field_name: str, unsafe_value: str) -> None:
    request = _valid_request()
    request[field_name] = unsafe_value

    result = validate_runtime_extraction_request(request)

    _assert_failed_closed(result, "unsafe_path")


@pytest.mark.parametrize("source_type", ("model_output", "assistant_generated", "third_party_unapproved"))
def test_request_validation_rejects_non_owner_sources(source_type: str) -> None:
    request = _valid_request()
    request["source_type"] = source_type

    result = validate_runtime_extraction_request(request)

    _assert_failed_closed(result, "rejected")
    assert result["owner_authored_or_owner_provided_source"] is False


@pytest.mark.parametrize("extractor", ("ollama", "openai", "ncp", "subtxt", "dramatica_flow", "unknown"))
def test_request_validation_rejects_unallowlisted_extractors(extractor: str) -> None:
    request = _valid_request()
    request["requested_extractors"] = [extractor]

    result = validate_runtime_extraction_request(request)

    _assert_failed_closed(result, "rejected")


@pytest.mark.parametrize("forbidden", FORBIDDEN_REQUESTED_TYPES_AND_FIELDS)
def test_request_validation_rejects_forbidden_artifact_types_and_actions(forbidden: str) -> None:
    request = _valid_request()
    request["requested_artifact_types"] = [forbidden]
    request[forbidden] = True

    result = validate_runtime_extraction_request(request)

    _assert_failed_closed(result, "rejected")
    assert result.get("no_generated_prose") is True
    assert result.get("no_model_calls") is True
    assert result.get("no_training_artifacts") is True
    assert result.get("no_apply_promotion") is True
    assert result.get("no_memory_canon_mutation") is True


@pytest.mark.parametrize(
    ("missing_field", "expected_status"),
    (
        ("source_refs", "missing_source_refs"),
        ("evidence_refs", "missing_evidence_refs"),
        ("provenance_refs", "missing_provenance_refs"),
        ("source_locator_refs", "missing_source_locator_refs"),
    ),
)
def test_request_validation_requires_source_evidence_provenance_and_locator_refs(
    missing_field: str, expected_status: str
) -> None:
    request = _valid_request()
    request[missing_field] = []

    result = validate_runtime_extraction_request(request)

    _assert_failed_closed(result, expected_status)


@pytest.mark.parametrize(
    ("start_offset", "end_offset"),
    ((-1, 10), (10, -1), (42, 0), (0, 5001)),
)
def test_request_validation_rejects_unbounded_or_negative_offsets(
    start_offset: int, end_offset: int
) -> None:
    request = _valid_request()
    request["source_locators"][0]["start_offset"] = start_offset
    request["source_locators"][0]["end_offset"] = end_offset

    result = validate_runtime_extraction_request(request)

    _assert_failed_closed(result)


@pytest.mark.parametrize("confirmation", sorted(REQUIRED_BOUNDARY_CONFIRMATIONS))
def test_request_validation_requires_boundary_confirmations(confirmation: str) -> None:
    request = _valid_request()
    request["boundary_confirmations"][confirmation] = False

    result = validate_runtime_extraction_request(request)

    _assert_failed_closed(result, "rejected")


def test_runtime_plan_is_deterministic_and_side_effect_free(tmp_path: Path) -> None:
    request = validate_runtime_extraction_request(_valid_request())
    environment = _valid_environment_result()

    first = build_runtime_extraction_plan(request, environment)
    second = build_runtime_extraction_plan(copy.deepcopy(request), copy.deepcopy(environment))

    assert first == second
    assert first["status"] == "valid"
    assert first["plan_id"]
    assert first["steps"] == [
        "validate_environment",
        "validate_request",
        "check_availability",
        "run_probe",
        "run_guarded_extractors",
        "validate_runtime_output",
        "build_raw_artifact_handoff",
        "build_candidate_review_handoff",
    ]
    assert first["side_effects_allowed"] == ["raw_artifact_handoff"]
    assert first["canon_write_allowed"] is False
    assert first["candidate_persistence_allowed"] is False
    assert first["review_queue_write_allowed"] is False
    assert first["model_calls_allowed"] is False
    assert first["generated_prose_allowed"] is False
    assert first["training_artifacts_allowed"] is False
    _assert_no_forbidden_side_effects(tmp_path)


@pytest.mark.parametrize(
    "failure_status",
    (
        "dependency_missing",
        "model_missing",
        "malformed_output",
        "unsafe_path",
        "missing_evidence_refs",
        "missing_provenance_refs",
        "missing_source_locator_refs",
        "runtime_failed",
        "fail_closed",
    ),
)
def test_guarded_extraction_fails_closed_for_runtime_failures(
    tmp_path: Path, failure_status: str
) -> None:
    request = validate_runtime_extraction_request(_valid_request())
    environment = _valid_environment_result()
    environment["forced_runtime_status"] = failure_status
    plan = build_runtime_extraction_plan(request, environment)

    result = run_guarded_runtime_extraction(plan, project_dir=tmp_path)

    _assert_failed_closed(result, failure_status)
    assert result["canon_write_performed"] is False
    assert result["apply_promotion_performed"] is False
    assert result["candidate_persistence_performed"] is False
    assert result["review_queue_write_performed"] is False
    assert result["model_call_performed"] is False
    assert result["generated_prose"] is False
    assert result["training_artifact_created"] is False
    _assert_no_forbidden_side_effects(tmp_path)


@pytest.mark.parametrize(
    ("max_input_chars", "timeout_seconds"),
    ((0, 30), (5001, 30), (5000, 0), (5000, -1), (5000, 999999)),
)
def test_guarded_extraction_fails_closed_for_bounds_and_timeout(
    tmp_path: Path, max_input_chars: int, timeout_seconds: int
) -> None:
    request_dict = _valid_request()
    request_dict["max_input_chars"] = max_input_chars
    request_dict["timeout_seconds"] = timeout_seconds

    request = validate_runtime_extraction_request(request_dict)
    if request["status"] != "valid":
        _assert_failed_closed(request)
        return

    plan = build_runtime_extraction_plan(request, _valid_environment_result())
    result = run_guarded_runtime_extraction(plan, project_dir=tmp_path)

    _assert_failed_closed(result)
    _assert_no_forbidden_side_effects(tmp_path)


def test_raw_artifact_handoff_uses_phase8_impl_018_support_data_vocabulary(tmp_path: Path) -> None:
    handoff = build_raw_artifact_handoff(_runtime_output(), project_dir=tmp_path)

    assert handoff["status"] == "valid"
    assert handoff["raw_artifact_bundle_id"] == RAW_ARTIFACT_BUNDLE_ID
    assert handoff["artifact_source_type"] == "runtime_extraction"
    assert handoff["support_data_only"] is True
    assert handoff["raw_artifacts_not_canon"] is True
    assert handoff["raw_artifacts_not_approved_memory"] is True
    assert handoff["raw_artifacts_not_candidates"] is True
    assert handoff["raw_artifacts_not_training_data"] is True
    assert handoff["source_refs"] == [SOURCE_REF]
    assert handoff["evidence_refs"] == [EVIDENCE_REF]
    assert handoff["provenance_refs"] == [PROVENANCE_REF]
    assert handoff["source_locator_refs"] == [SOURCE_LOCATOR_REF]
    assert {file_ref["artifact_type"] for file_ref in handoff["artifact_files"]} <= set(ALLOWED_ARTIFACT_TYPES)
    _assert_no_forbidden_side_effects(tmp_path)


@pytest.mark.parametrize(
    ("missing_field", "expected_status"),
    (
        ("source_refs", "missing_source_refs"),
        ("evidence_refs", "missing_evidence_refs"),
        ("provenance_refs", "missing_provenance_refs"),
        ("source_locator_refs", "missing_source_locator_refs"),
    ),
)
def test_raw_artifact_handoff_rejects_incomplete_output(
    tmp_path: Path, missing_field: str, expected_status: str
) -> None:
    output = _runtime_output()
    output[missing_field] = []

    handoff = build_raw_artifact_handoff(output, project_dir=tmp_path)

    _assert_failed_closed(handoff, expected_status)
    assert handoff.get("indexed_as_valid") is not True
    _assert_no_forbidden_side_effects(tmp_path)


def test_raw_artifact_handoff_quarantines_malformed_or_unsafe_output(tmp_path: Path) -> None:
    output = _runtime_output("malformed_output")
    output["artifact_files"][0]["relative_path"] = "../escape.json"

    handoff = build_raw_artifact_handoff(output, project_dir=tmp_path)

    _assert_failed_closed(handoff)
    assert handoff["status"] in {"malformed_output", "unsafe_path", "quarantined", "rejected"}
    assert handoff.get("indexed_as_valid") is not True
    _assert_no_forbidden_side_effects(tmp_path)


def test_candidate_review_handoff_is_candidate_draft_only_owner_review_required(tmp_path: Path) -> None:
    raw_handoff = build_raw_artifact_handoff(_runtime_output(), project_dir=tmp_path)
    request = validate_runtime_extraction_request(_valid_request())

    handoff = build_candidate_review_handoff(raw_handoff, request)

    assert handoff["status"] == "valid"
    assert handoff["handoff_type"] == "candidate_draft_review_handoff"
    assert handoff["candidate_first"] is True
    assert handoff["owner_review_required"] is True
    assert handoff["queue_presence_is_not_approval"] is True
    assert handoff["candidate_persistence_is_not_canon"] is True
    assert handoff["confidence_is_support_strength_not_truth"] is True
    assert handoff["apply_promotion_performed"] is False
    assert handoff["memory_canon_mutation_performed"] is False
    assert handoff["generated_prose"] is False
    assert handoff["model_call_performed"] is False
    assert handoff["training_artifact_created"] is False
    assert handoff["source_refs"] == [SOURCE_REF]
    assert handoff["evidence_refs"] == [EVIDENCE_REF]
    assert handoff["provenance_refs"] == [PROVENANCE_REF]
    assert handoff["source_locator_refs"] == [SOURCE_LOCATOR_REF]
    _assert_no_forbidden_side_effects(tmp_path)


@pytest.mark.parametrize("reason", QUARANTINE_REASONS)
def test_quarantine_preserves_reason_safe_refs_and_has_no_valid_index_side_effect(
    tmp_path: Path, reason: str
) -> None:
    quarantine = quarantine_runtime_extraction_output(
        _runtime_output(status=reason),
        reason,
        project_dir=tmp_path,
    )

    assert quarantine["status"] == "quarantined"
    assert quarantine["quarantine_reason"] == reason
    assert quarantine["source_refs"] == [SOURCE_REF]
    assert quarantine["evidence_refs"] == [EVIDENCE_REF]
    assert quarantine["provenance_refs"] == [PROVENANCE_REF]
    assert quarantine["source_locator_refs"] == [SOURCE_LOCATOR_REF]
    assert quarantine["excluded_from_valid_handoff"] is True
    assert quarantine["indexed_as_valid"] is False
    assert quarantine["canon_write_performed"] is False
    assert quarantine["candidate_persistence_performed"] is False
    assert quarantine["review_queue_write_performed"] is False
    assert quarantine["model_call_performed"] is False
    assert quarantine["generated_prose"] is False
    assert quarantine["training_artifact_created"] is False
    _assert_no_forbidden_side_effects(tmp_path)


def test_no_side_effect_filesystem_contract_for_probe_plan_execution_and_quarantine(
    tmp_path: Path,
) -> None:
    request = validate_runtime_extraction_request(_valid_request())
    plan = build_runtime_extraction_plan(request, _valid_environment_result())

    run_runtime_extraction_probe(plan, project_dir=tmp_path)
    run_guarded_runtime_extraction(plan, project_dir=tmp_path)
    build_raw_artifact_handoff(_runtime_output(), project_dir=tmp_path)
    build_candidate_review_handoff(_runtime_output(), request)
    quarantine_runtime_extraction_output(_runtime_output("malformed_output"), "malformed_output", project_dir=tmp_path)

    _assert_no_forbidden_side_effects(tmp_path)
