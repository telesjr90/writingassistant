"""Contract tests for the future review-safe extraction orchestrator.

PHASE8-IMPL-010-T003 is tests-first only. The future pure orchestration module
is imported normally so this targeted file is expected red until T004 creates it:
- backend.story_knowledge.extraction_orchestrator

Fixtures are synthetic, owner-authored, in-memory strings and dictionaries.
These tests do not install, import, or run BookNLP/spaCy; do not write raw
artifacts or candidates; and do not mutate memory/canon.
"""

from copy import deepcopy
import json
from pathlib import Path

import pytest

from backend.story_knowledge import booknlp_adapter_contract
from backend.story_knowledge import booknlp_fixture_parser
from backend.story_knowledge import evidence
from backend.story_knowledge import raw_extraction_storage
from backend.story_knowledge import source_map as source_map_helpers
from backend.story_knowledge import extraction_orchestrator

PROJECT_ID = "example"
RUN_ID = "run_20260624_001"
PIPELINE_ID = "fixture_pipeline_001"
SOURCE_MAP_ID = "source_map_001"
SNAPSHOT_ID = "snapshot_001"
SNAPSHOT_HASH = "sha256:snapshot-001"
SOURCE_HASH = "sha256:source-doc-001"
CREATED_AT = "2026-06-24T00:00:00Z"

EXPECTED_PUBLIC_API = (
    "validate_extraction_pipeline_request",
    "build_fixture_extraction_pipeline_plan",
    "run_fixture_extraction_pipeline",
)

REQUEST_REQUIRED_FIELDS = (
    "project_id",
    "source_document",
    "source_map",
    "run_manifest",
    "raw_output_references",
    "fixture_texts",
    "requested_outputs",
    "human_review_required",
    "persist_candidates",
    "persist_raw_artifacts",
    "allow_runtime_tools",
    "allow_model_calls",
    "allow_canon_write",
    "allow_prose_generation",
)

SAFE_POLICY_FLAGS = {
    "human_review_required": True,
    "persist_candidates": False,
    "persist_raw_artifacts": False,
    "allow_runtime_tools": False,
    "allow_model_calls": False,
    "allow_canon_write": False,
    "allow_prose_generation": False,
}

REQUESTED_OUTPUTS = (
    "raw_artifact_bundle",
    "candidate_drafts",
    "evidence_records",
    "review_handoff",
)

EXPECTED_PLAN_STEPS = (
    "source_map_validation",
    "fixture_parser",
    "raw_bundle_builder",
    "raw_manifest_validation",
    "adapter_bundle_validation",
    "candidate_draft_support",
    "evidence_validation",
    "review_handoff",
)

EXPECTED_RUN_OUTPUT_FIELDS = (
    "pipeline_id",
    "project_id",
    "source_document",
    "source_map",
    "run_manifest",
    "raw_artifact_bundle",
    "raw_output_references",
    "candidate_drafts",
    "evidence_records",
    "provenance",
    "warnings",
    "errors",
    "human_review_required",
    "persisted_candidates",
    "persisted_raw_artifacts",
    "canon_write_performed",
    "prose_generated",
)

UNSAFE_POLICY_FLAG_OVERRIDES = (
    ("human_review_required", False),
    ("persist_candidates", True),
    ("persist_raw_artifacts", True),
    ("allow_runtime_tools", True),
    ("allow_model_calls", True),
    ("allow_canon_write", True),
    ("allow_prose_generation", True),
)

FORBIDDEN_REQUEST_FIELDS = (
    "candidate_persistence_destination",
    "raw_persistence_destination",
    "memory_write",
    "canon_write",
    "route_trigger",
    "ui_trigger",
    "generated_prose",
    "rewrite",
    "continuation",
    "external_tool_runtime",
)

FORBIDDEN_NESTED_FIELDS = (
    "candidate_records_path",
    "raw_output_directory",
    "write_to_canon",
    "mutate_memory",
    "apply_promotion",
    "route_trigger",
    "ui_trigger",
    "generated_prose",
    "rewrite_scene",
    "continuation",
    "runtime_tool_name",
)

FORBIDDEN_OUTPUT_OR_REQUEST_TERMS = (
    "promoted",
    "owner_decision",
    "approved_memory_write",
    "canon_write",
    "storyform_truth",
    "route_trigger",
    "ui_trigger",
    "generated_prose",
    "rewrite",
    "continuation",
    "apply_promotion",
    "dataset_output",
    "training_output",
)

FORBIDDEN_PLAN_OR_RUN_FIELDS = (
    "filesystem_path",
    "project_dir",
    "output_dir",
    "candidate_path",
    "raw_path",
    "route_trigger",
    "ui_trigger",
    "package_install",
    "runtime_invocation",
    "tool_command",
)

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
    "pathlib.Path",
    "Path(",
    "open(",
    ".write_text",
    ".mkdir",
    "training",
    "dataset_manifest",
    "jsonl",
    "generated_prose",
    "rewrite",
    "continuation",
    "write_to_canon",
    "mutate_memory",
    "apply_promotion",
    "world_state",
    "storyform_truth",
)

TOKENS_HEADER = (
    "paragraph_ID",
    "sentence_ID",
    "token_ID_within_sentence",
    "token_ID_within_document",
    "word",
    "lemma",
    "byte_onset",
    "byte_offset",
    "POS_tag",
    "fine_POS_tag",
    "dependency_relation",
    "syntactic_head_ID",
    "event",
)

ENTITIES_HEADER = ("COREF", "start_token", "end_token", "prop", "cat", "text")
QUOTES_HEADER = (
    "quote_start",
    "quote_end",
    "mention_start",
    "mention_end",
    "mention_phrase",
    "char_id",
    "quote",
)
SUPERSENSE_HEADER = ("start_token", "end_token", "supersense_category", "text")


def tsv_text(header, rows):
    return "\n".join(["\t".join(header), *["\t".join(row) for row in rows]]) + "\n"


def valid_tokens_tsv(**overrides):
    row = {
        "paragraph_ID": "0",
        "sentence_ID": "0",
        "token_ID_within_sentence": "0",
        "token_ID_within_document": "0",
        "word": "Alice",
        "lemma": "Alice",
        "byte_onset": "0",
        "byte_offset": "5",
        "POS_tag": "PROPN",
        "fine_POS_tag": "NNP",
        "dependency_relation": "nsubj",
        "syntactic_head_ID": "1",
        "event": "EVENT",
    }
    row.update(overrides)
    return tsv_text(TOKENS_HEADER, [[row[column] for column in TOKENS_HEADER]])


def valid_entities_tsv(**overrides):
    row = {
        "COREF": "1",
        "start_token": "0",
        "end_token": "0",
        "prop": "PROP",
        "cat": "PER",
        "text": "Alice",
    }
    row.update(overrides)
    return tsv_text(ENTITIES_HEADER, [[row[column] for column in ENTITIES_HEADER]])


def valid_quotes_tsv(**overrides):
    row = {
        "quote_start": "4",
        "quote_end": "5",
        "mention_start": "6",
        "mention_end": "6",
        "mention_phrase": "Bob",
        "char_id": "2",
        "quote": "Wait.",
    }
    row.update(overrides)
    return tsv_text(QUOTES_HEADER, [[row[column] for column in QUOTES_HEADER]])


def valid_supersense_tsv(**overrides):
    row = {
        "start_token": "0",
        "end_token": "0",
        "supersense_category": "noun.person",
        "text": "Alice",
    }
    row.update(overrides)
    return tsv_text(SUPERSENSE_HEADER, [[row[column] for column in SUPERSENSE_HEADER]])


def valid_book_json_text(**overrides):
    book = {
        "characters": [
            {
                "agent": ["opened"],
                "patient": [],
                "mod": [],
                "poss": [],
                "id": 1,
                "g": {"she/her": 2},
                "count": 2,
                "mentions": {
                    "proper": [{"c": "Alice", "n": 2}],
                    "common": [],
                    "pronoun": [{"c": "she", "n": 2}],
                },
            }
        ]
    }
    book.update(overrides)
    return json.dumps(book)


def build_source_document_ref(**overrides):
    record = {
        "project_id": PROJECT_ID,
        "source_document_type": "scene",
        "source_document_id": "scene_001",
        "source_document_version": "1",
        "source_label": "Opening scene",
        "source_path_hint": "scenes/scene_001.md",
        "content_hash": SOURCE_HASH,
        "content_hash_algorithm": "sha256",
        "created_at": CREATED_AT,
        "updated_at": CREATED_AT,
    }
    record.update(overrides)
    return record


def build_source_segment(**overrides):
    segment = {
        "segment_id": "segment_001",
        "segment_type": "sentence",
        "segment_index": 0,
        "section_id": None,
        "chapter_id": "chapter_001",
        "scene_id": "scene_001",
        "paragraph_index": 0,
        "sentence_index": 0,
        "line_start": 1,
        "line_end": 1,
        "char_start": 0,
        "char_end": 5,
        "byte_start": 0,
        "byte_end": 5,
        "token_start": 0,
        "token_end": 1,
        "text_excerpt": "Alice",
        "excerpt_hash": "sha256:excerpt-001",
    }
    segment.update(overrides)
    return segment


def build_source_map(**overrides):
    record = {
        "source_map_id": SOURCE_MAP_ID,
        "project_id": PROJECT_ID,
        "source_document": build_source_document_ref(),
        "snapshot_id": SNAPSHOT_ID,
        "snapshot_hash": SNAPSHOT_HASH,
        "snapshot_hash_algorithm": "sha256",
        "snapshot_created_at": CREATED_AT,
        "text_encoding": "utf-8",
        "normalization_policy": "exact_utf8_decoded_snapshot",
        "line_index_available": True,
        "char_offset_policy": "python_string_offsets_half_open",
        "byte_offset_policy": "utf8_byte_offsets_for_raw_tool_alignment",
        "token_offset_policy": "booknlp_token_alignment_support",
        "segments": [build_source_segment()],
    }
    record.update(overrides)
    return record


def raw_output_reference(artifact_name, artifact_kind, path_part="raw", **overrides):
    reference = {
        "raw_output_id": f"raw_{artifact_kind}",
        "project_id": PROJECT_ID,
        "tool_name": "booknlp",
        "run_id": RUN_ID,
        "artifact_name": artifact_name,
        "artifact_kind": artifact_kind,
        "artifact_path_hint": (
            f"writer_assistant/extractions/booknlp/{RUN_ID}/{path_part}/{artifact_name}"
        ),
        "artifact_hash": f"sha256:{artifact_kind}",
        "artifact_hash_algorithm": "sha256",
        "created_at": CREATED_AT,
        "source_snapshot_hashes": [SNAPSHOT_HASH],
        "is_canon": False,
        "is_candidate": False,
    }
    reference.update(overrides)
    return reference


def storage_raw_reference(artifact_name, artifact_kind, **overrides):
    return raw_output_reference(artifact_name, artifact_kind, "raw", **overrides)


def storage_derived_reference(**overrides):
    return raw_output_reference(
        "events.json",
        "booknlp_events_derived",
        "derived",
        raw_output_id="derived_booknlp_events",
        **overrides,
    )


def adapter_raw_output_references():
    return [
        raw_output_reference("tokens.tsv", "booknlp_tokens"),
        raw_output_reference("entities.tsv", "booknlp_entities"),
        raw_output_reference("quotes.tsv", "booknlp_quotes"),
        raw_output_reference("supersense.tsv", "booknlp_supersense"),
        raw_output_reference("book.json", "booknlp_book_json"),
        raw_output_reference("events.json", "booknlp_events", "derived"),
    ]


def build_storage_manifest(**overrides):
    manifest = {
        "run_id": RUN_ID,
        "project_id": PROJECT_ID,
        "tool_name": "booknlp",
        "tool_version": "fixture",
        "adapter_name": "writer_assistant_booknlp_fixture_orchestrator",
        "adapter_version": "contract",
        "run_type": "booknlp_fixture_parse",
        "status": "complete",
        "source_documents": [build_source_document_ref()],
        "source_snapshot_hashes": [SNAPSHOT_HASH],
        "storage_root": "writer_assistant/extractions",
        "run_dir": f"writer_assistant/extractions/booknlp/{RUN_ID}",
        "raw_artifacts": [
            storage_raw_reference("tokens.tsv", "booknlp_tokens"),
            storage_raw_reference("entities.tsv", "booknlp_entities"),
            storage_raw_reference("quotes.tsv", "booknlp_quotes"),
            storage_raw_reference("supersense.tsv", "booknlp_supersense"),
            storage_raw_reference("book.json", "booknlp_book_json"),
        ],
        "derived_artifacts": [storage_derived_reference()],
        "artifact_hashes": {
            "tokens.tsv": "sha256:tokens",
            "entities.tsv": "sha256:entities",
            "quotes.tsv": "sha256:quotes",
            "supersense.tsv": "sha256:supersense",
            "book.json": "sha256:book",
            "events.json": "sha256:events",
        },
        "created_at": CREATED_AT,
        "updated_at": CREATED_AT,
        "parameters": {},
        "environment": {},
        "warnings": [],
        "errors": [],
        "human_review_required": True,
        "candidate_generation_allowed": False,
        "canon_write_allowed": False,
        "prose_generation_allowed": False,
    }
    manifest.update(overrides)
    return manifest


def fixture_texts(**overrides):
    payload = {
        "tokens_tsv": valid_tokens_tsv(),
        "entities_tsv": valid_entities_tsv(),
        "quotes_tsv": valid_quotes_tsv(),
        "supersense_tsv": valid_supersense_tsv(),
        "book_json": valid_book_json_text(),
    }
    payload.update(overrides)
    return payload


def build_pipeline_request(**overrides):
    request = {
        "project_id": PROJECT_ID,
        "source_document": build_source_document_ref(),
        "source_map": build_source_map(),
        "run_manifest": build_storage_manifest(),
        "raw_output_references": adapter_raw_output_references(),
        "fixture_texts": fixture_texts(),
        "requested_outputs": list(REQUESTED_OUTPUTS),
        **SAFE_POLICY_FLAGS,
    }
    request.update(overrides)
    return request


def assert_no_extraction_side_effects(project: Path) -> None:
    writer_assistant = project / "writer_assistant"
    extractions = writer_assistant / "extractions"
    run = extractions / "booknlp" / RUN_ID

    assert not project.exists()
    assert not writer_assistant.exists()
    assert not extractions.exists()
    assert not (extractions / "booknlp").exists()
    assert not run.exists()
    assert not (run / "raw").exists()
    assert not (run / "derived").exists()
    assert not (run / "manifest.json").exists()
    assert not (run / "raw" / "tokens.tsv").exists()
    assert not (writer_assistant / "candidates").exists()
    assert not (writer_assistant / "index.json").exists()
    assert not (writer_assistant / "memory").exists()
    assert not (writer_assistant / "canon").exists()
    assert not (project / "bible.json").exists()
    assert not (project / "storyform.json").exists()
    assert not (project / "training").exists()
    assert not (project / "dataset_manifest.json").exists()


def assert_no_forbidden_keys_or_values(payload, forbidden_terms):
    if isinstance(payload, dict):
        for key, value in payload.items():
            lowered_key = str(key).lower()
            assert lowered_key not in forbidden_terms
            assert_no_forbidden_keys_or_values(value, forbidden_terms)
    elif isinstance(payload, list):
        for item in payload:
            assert_no_forbidden_keys_or_values(item, forbidden_terms)
    elif isinstance(payload, str):
        lowered_value = payload.lower()
        for term in forbidden_terms:
            assert term not in lowered_value


def test_future_public_api_symbols_are_present():
    for name in EXPECTED_PUBLIC_API:
        assert hasattr(extraction_orchestrator, name), name


def test_validate_request_accepts_only_dict_input():
    for invalid in (None, [], (), "request"):
        with pytest.raises(ValueError):
            extraction_orchestrator.validate_extraction_pipeline_request(invalid)


def test_validate_request_requires_all_contract_fields():
    for field in REQUEST_REQUIRED_FIELDS:
        request = build_pipeline_request()
        request.pop(field)

        with pytest.raises(ValueError):
            extraction_orchestrator.validate_extraction_pipeline_request(request)


def test_validate_request_rejects_unknown_fields():
    request = build_pipeline_request(unknown_field=True)

    with pytest.raises(ValueError):
        extraction_orchestrator.validate_extraction_pipeline_request(request)


def test_validate_request_returns_deep_copy_and_blocks_caller_mutation_leaks():
    request = build_pipeline_request()

    validated = extraction_orchestrator.validate_extraction_pipeline_request(request)
    request["project_id"] = "changed"
    request["source_document"]["source_label"] = "changed"
    request["fixture_texts"]["tokens_tsv"] = valid_tokens_tsv(word="Changed")

    assert validated is not request
    assert validated["project_id"] == PROJECT_ID
    assert validated["source_document"]["source_label"] == "Opening scene"
    assert "Changed" not in validated["fixture_texts"]["tokens_tsv"]

    validated["source_document"]["source_label"] = "mutated return"
    assert request["source_document"]["source_label"] == "changed"


def test_validate_request_uses_existing_source_raw_and_evidence_validators():
    request = build_pipeline_request()

    validated = extraction_orchestrator.validate_extraction_pipeline_request(request)

    assert validated["source_document"] == source_map_helpers.validate_source_document_ref(
        request["source_document"]
    )
    assert validated["source_map"] == source_map_helpers.validate_source_map(
        request["source_map"]
    )
    assert validated[
        "run_manifest"
    ] == raw_extraction_storage.validate_extraction_run_manifest(
        request["run_manifest"]
    )
    assert validated["raw_output_references"] == [
        evidence.validate_raw_output_reference(reference)
        for reference in request["raw_output_references"]
    ]


def test_validate_request_accepts_only_in_memory_fixture_texts():
    request = build_pipeline_request()
    validated = extraction_orchestrator.validate_extraction_pipeline_request(request)

    assert validated["fixture_texts"] == request["fixture_texts"]

    for field in request["fixture_texts"]:
        invalid = build_pipeline_request(
            fixture_texts={**request["fixture_texts"], field: Path("tokens.tsv")}
        )
        with pytest.raises(ValueError):
            extraction_orchestrator.validate_extraction_pipeline_request(invalid)


def test_validate_request_rejects_unsupported_fixture_keys():
    request = build_pipeline_request(
        fixture_texts={**fixture_texts(), "events_tsv": "event\ttext\n0\tAlice\n"}
    )

    with pytest.raises(ValueError):
        extraction_orchestrator.validate_extraction_pipeline_request(request)


def test_validate_request_rejects_invalid_requested_outputs():
    for requested_outputs in (
        [],
        ["raw_artifact_bundle", "runtime_tool_invocation"],
        ["candidate_json"],
        "raw_artifact_bundle",
    ):
        request = build_pipeline_request(requested_outputs=requested_outputs)

        with pytest.raises(ValueError):
            extraction_orchestrator.validate_extraction_pipeline_request(request)


@pytest.mark.parametrize("field,value", UNSAFE_POLICY_FLAG_OVERRIDES)
def test_validate_request_fails_closed_for_unsafe_policy_flags(field, value):
    request = build_pipeline_request(**{field: value})

    with pytest.raises(ValueError):
        extraction_orchestrator.validate_extraction_pipeline_request(request)


@pytest.mark.parametrize("field", FORBIDDEN_REQUEST_FIELDS)
def test_validate_request_rejects_forbidden_top_level_requests(field):
    request = build_pipeline_request(**{field: "blocked"})

    with pytest.raises(ValueError):
        extraction_orchestrator.validate_extraction_pipeline_request(request)


@pytest.mark.parametrize("field", FORBIDDEN_NESTED_FIELDS)
def test_validate_request_rejects_forbidden_nested_values(field):
    request = build_pipeline_request()
    request["run_manifest"]["parameters"][field] = "blocked"

    with pytest.raises(ValueError):
        extraction_orchestrator.validate_extraction_pipeline_request(request)


def test_validate_request_fails_closed_for_invalid_source_document():
    request = build_pipeline_request(
        source_document=build_source_document_ref(source_document_type="unsupported")
    )

    with pytest.raises(ValueError):
        extraction_orchestrator.validate_extraction_pipeline_request(request)


def test_validate_request_fails_closed_for_invalid_source_map():
    request = build_pipeline_request(source_map=build_source_map(segments=[]))

    with pytest.raises(ValueError):
        extraction_orchestrator.validate_extraction_pipeline_request(request)


def test_validate_request_fails_closed_for_invalid_run_manifest():
    request = build_pipeline_request(
        run_manifest=build_storage_manifest(human_review_required=False)
    )

    with pytest.raises(ValueError):
        extraction_orchestrator.validate_extraction_pipeline_request(request)


def test_validate_request_fails_closed_for_invalid_raw_output_references():
    request = build_pipeline_request(
        raw_output_references=[
            raw_output_reference("tokens.tsv", "booknlp_tokens", is_canon=True)
        ]
    )

    with pytest.raises(ValueError):
        extraction_orchestrator.validate_extraction_pipeline_request(request)


def test_validate_request_fails_closed_for_invalid_fixture_texts():
    request = build_pipeline_request(
        fixture_texts={**fixture_texts(), "tokens_tsv": "tokens.tsv"}
    )

    with pytest.raises(ValueError):
        extraction_orchestrator.validate_extraction_pipeline_request(request)


def test_build_fixture_plan_validates_request_and_returns_in_memory_plan():
    request = build_pipeline_request()
    original = deepcopy(request)

    plan = extraction_orchestrator.build_fixture_extraction_pipeline_plan(request)

    assert request == original
    assert plan["project_id"] == PROJECT_ID
    assert plan["source_document"] == source_map_helpers.validate_source_document_ref(
        request["source_document"]
    )
    assert plan["fixture_only"] is True
    assert plan["human_review_required"] is True
    assert plan["persist_candidates"] is False
    assert plan["persist_raw_artifacts"] is False
    assert plan["allow_runtime_tools"] is False
    assert plan["allow_model_calls"] is False
    assert plan["allow_canon_write"] is False
    assert plan["allow_prose_generation"] is False
    assert isinstance(plan["pipeline_steps"], list)
    assert set(EXPECTED_PLAN_STEPS).issubset(set(plan["pipeline_steps"]))
    assert_no_forbidden_keys_or_values(plan, FORBIDDEN_PLAN_OR_RUN_FIELDS)


def test_build_fixture_plan_fails_closed_for_invalid_request():
    request = build_pipeline_request(persist_candidates=True)

    with pytest.raises(ValueError):
        extraction_orchestrator.build_fixture_extraction_pipeline_plan(request)


def test_run_fixture_pipeline_returns_review_safe_in_memory_output(monkeypatch):
    request = build_pipeline_request()
    original = deepcopy(request)
    calls = {
        "bundle_builder": 0,
        "bundle_validator": 0,
        "candidate_drafts": 0,
    }
    real_bundle_builder = (
        booknlp_fixture_parser.build_booknlp_raw_artifact_bundle_from_fixture_texts
    )
    real_bundle_validator = booknlp_adapter_contract.validate_booknlp_raw_artifact_bundle
    real_draft_builder = booknlp_adapter_contract.build_booknlp_candidate_drafts

    def tracking_bundle_builder(*args, **kwargs):
        calls["bundle_builder"] += 1
        return real_bundle_builder(*args, **kwargs)

    def tracking_bundle_validator(*args, **kwargs):
        calls["bundle_validator"] += 1
        return real_bundle_validator(*args, **kwargs)

    def tracking_draft_builder(*args, **kwargs):
        calls["candidate_drafts"] += 1
        return real_draft_builder(*args, **kwargs)

    monkeypatch.setattr(
        booknlp_fixture_parser,
        "build_booknlp_raw_artifact_bundle_from_fixture_texts",
        tracking_bundle_builder,
    )
    monkeypatch.setattr(
        booknlp_adapter_contract,
        "validate_booknlp_raw_artifact_bundle",
        tracking_bundle_validator,
    )
    monkeypatch.setattr(
        booknlp_adapter_contract,
        "build_booknlp_candidate_drafts",
        tracking_draft_builder,
    )

    result = extraction_orchestrator.run_fixture_extraction_pipeline(request)

    assert request == original
    assert calls["bundle_builder"] == 1
    assert calls["bundle_validator"] >= 1
    assert calls["candidate_drafts"] >= 1
    assert set(EXPECTED_RUN_OUTPUT_FIELDS) == set(result)
    assert result["pipeline_id"] == PIPELINE_ID or isinstance(result["pipeline_id"], str)
    assert result["project_id"] == PROJECT_ID
    assert result["source_document"] == source_map_helpers.validate_source_document_ref(
        request["source_document"]
    )
    assert result["source_map"] == source_map_helpers.validate_source_map(
        request["source_map"]
    )
    assert result[
        "run_manifest"
    ] == raw_extraction_storage.validate_extraction_run_manifest(
        request["run_manifest"]
    )
    assert result["raw_output_references"] == [
        evidence.validate_raw_output_reference(reference)
        for reference in request["raw_output_references"]
    ]
    assert booknlp_adapter_contract.validate_booknlp_raw_artifact_bundle(
        result["raw_artifact_bundle"]
    )
    assert isinstance(result["candidate_drafts"], list)
    assert isinstance(result["evidence_records"], list)
    assert isinstance(result["provenance"], dict)
    assert isinstance(result["warnings"], list)
    assert isinstance(result["errors"], list)
    assert result["human_review_required"] is True
    assert result["persisted_candidates"] is False
    assert result["persisted_raw_artifacts"] is False
    assert result["canon_write_performed"] is False
    assert result["prose_generated"] is False
    assert_no_forbidden_keys_or_values(result, FORBIDDEN_OUTPUT_OR_REQUEST_TERMS)


def test_run_fixture_pipeline_fails_closed_for_invalid_adapter_bundle(monkeypatch):
    def invalid_bundle(*args, **kwargs):
        return {"bundle_id": "invalid"}

    monkeypatch.setattr(
        booknlp_fixture_parser,
        "build_booknlp_raw_artifact_bundle_from_fixture_texts",
        invalid_bundle,
    )

    with pytest.raises(ValueError):
        extraction_orchestrator.run_fixture_extraction_pipeline(build_pipeline_request())


def test_run_fixture_pipeline_fails_closed_for_missing_evidence_when_required():
    request = build_pipeline_request(requested_outputs=["evidence_records"])
    request["raw_output_references"] = []

    with pytest.raises(ValueError):
        extraction_orchestrator.run_fixture_extraction_pipeline(request)


@pytest.mark.parametrize("field,value", UNSAFE_POLICY_FLAG_OVERRIDES)
def test_run_fixture_pipeline_rejects_unsafe_policy_flags(field, value):
    request = build_pipeline_request(**{field: value})

    with pytest.raises(ValueError):
        extraction_orchestrator.run_fixture_extraction_pipeline(request)


@pytest.mark.parametrize("field", FORBIDDEN_NESTED_FIELDS)
def test_run_fixture_pipeline_rejects_persistence_canon_runtime_and_prose_requests(field):
    request = build_pipeline_request()
    request["source_map"]["segments"][0][field] = "blocked"

    with pytest.raises(ValueError):
        extraction_orchestrator.run_fixture_extraction_pipeline(request)


def test_run_fixture_pipeline_does_not_create_project_files(tmp_path):
    project = tmp_path / "my-project"
    request = build_pipeline_request()
    request["sentinel_project_dir"] = str(project)

    with pytest.raises(ValueError):
        extraction_orchestrator.run_fixture_extraction_pipeline(request)

    assert_no_extraction_side_effects(project)

    result = extraction_orchestrator.run_fixture_extraction_pipeline(
        build_pipeline_request()
    )
    assert result["persisted_candidates"] is False
    assert result["persisted_raw_artifacts"] is False
    assert_no_extraction_side_effects(project)


def test_source_scan_for_future_orchestrator_rejects_runtime_tool_and_mutation_terms():
    source_path = Path("backend/story_knowledge/extraction_orchestrator.py")
    if not source_path.exists():
        return

    source = source_path.read_text(encoding="utf-8").lower()

    for term in FORBIDDEN_PRODUCTION_SOURCE_TERMS:
        assert term.lower() not in source
