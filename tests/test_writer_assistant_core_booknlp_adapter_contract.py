"""Contract tests for PHASE8-IMPL-006 BookNLP-ready adapter boundaries.

T006 is tests-first only. The future pure adapter-contract module is imported
normally so this targeted file is expected red until a later task creates it:
- backend.story_knowledge.booknlp_adapter_contract

Fixtures are synthetic, owner-authored, in-memory dictionaries. These tests do
not install, import, or run BookNLP/spaCy and do not perform extraction.
"""

from copy import deepcopy
import inspect

import pytest

from backend.story_knowledge import evidence
from backend.story_knowledge import source_map
from backend.story_knowledge import booknlp_adapter_contract

SAMPLE_TEXT = 'Alice opened the brass door. "Wait," Bob said.'
PROJECT_ID = "example"
RUN_ID = "run_001"
SOURCE_MAP_ID = "source_map_001"
SNAPSHOT_ID = "snapshot_001"
SNAPSHOT_HASH = "sha256:snapshot-001"
SOURCE_HASH = "sha256:source-doc-001"

EXPECTED_PUBLIC_API = (
    "validate_booknlp_run_manifest",
    "validate_booknlp_raw_artifact_bundle",
    "normalize_booknlp_entity_mentions",
    "normalize_booknlp_quotes",
    "normalize_booknlp_events",
    "build_booknlp_candidate_drafts",
)

MANIFEST_REQUIRED_FIELDS = (
    "run_id",
    "project_id",
    "tool_name",
    "tool_version",
    "adapter_name",
    "adapter_version",
    "run_type",
    "status",
    "source_documents",
    "input_snapshot_hashes",
    "raw_artifacts",
    "artifact_hashes",
    "started_at",
    "finished_at",
    "parameters",
    "environment",
    "warnings",
    "errors",
    "human_review_required",
    "candidate_generation_allowed",
    "canon_write_allowed",
    "prose_generation_allowed",
)

BUNDLE_REQUIRED_FIELDS = (
    "bundle_id",
    "project_id",
    "run_manifest",
    "source_map",
    "tokens",
    "entities",
    "quotes",
    "book_json",
    "supersense",
    "events",
    "raw_output_references",
    "created_at",
)

ALLOWED_STATUSES = ("planned", "running", "complete", "failed", "partial", "rejected")

FORBIDDEN_PROSE_MUTATION_FIELDS = (
    "model_prompt",
    "model_output",
    "generated_prose",
    "rewritten_text",
    "continuation",
    "write_to_canon",
    "mutate_memory",
    "apply_promotion",
    "approved_truth",
)

BUNDLE_FORBIDDEN_SHORTCUT_FIELDS = (
    "is_canon",
    "is_candidate",
    "candidate_records",
    "memory_records",
    "canon_records",
    "storyform_truth",
)

CANDIDATE_DRAFT_REQUIRED_FIELDS = (
    "candidate_type",
    "target_category",
    "source_locator",
    "evidence",
    "provenance",
    "confidence",
    "raw_output_refs",
    "normalization_status",
)

FORBIDDEN_DRAFT_FIELDS_OR_VALUES = (
    "write_to_canon",
    "mutate_memory",
    "apply_promotion",
    "rewrite_scene",
    "generate_prose",
)

FORBIDDEN_PRODUCTION_SOURCE_TERMS = (
    "booknlp import",
    "from booknlp",
    "spacy.load",
    "ollama",
    "openai",
    "requests",
    "httpx",
    "fastapi",
    "uvicorn",
    "subprocess",
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


def build_valid_source_document_ref(**overrides):
    ref = {
        "project_id": PROJECT_ID,
        "source_document_type": "scene",
        "source_document_id": "scene_001",
        "source_document_version": "1",
        "source_label": "Opening scene",
        "source_path_hint": "Scenes / Opening scene",
        "content_hash": SOURCE_HASH,
        "content_hash_algorithm": "sha256",
        "created_at": "2026-06-19T00:00:00Z",
        "updated_at": "2026-06-19T00:00:00Z",
    }
    ref.update(overrides)
    return ref


def build_valid_source_segment(**overrides):
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
        "char_end": len(SAMPLE_TEXT),
        "byte_start": 0,
        "byte_end": len(SAMPLE_TEXT.encode("utf-8")),
        "token_start": 0,
        "token_end": 11,
        "text_excerpt": SAMPLE_TEXT,
        "excerpt_hash": "sha256:excerpt-001",
    }
    segment.update(overrides)
    return segment


def build_valid_source_map(**overrides):
    source_map_record = {
        "source_map_id": SOURCE_MAP_ID,
        "project_id": PROJECT_ID,
        "source_document": build_valid_source_document_ref(),
        "snapshot_id": SNAPSHOT_ID,
        "snapshot_hash": SNAPSHOT_HASH,
        "snapshot_hash_algorithm": "sha256",
        "snapshot_created_at": "2026-06-19T00:00:00Z",
        "text_encoding": "utf-8",
        "normalization_policy": "exact_utf8_decoded_snapshot",
        "line_index_available": True,
        "char_offset_policy": "python_string_offsets_half_open",
        "byte_offset_policy": "utf8_byte_offsets_for_raw_tool_alignment",
        "token_offset_policy": "booknlp_token_alignment_support",
        "segments": [build_valid_source_segment()],
    }
    source_map_record.update(overrides)
    return source_map_record


def build_valid_source_locator(**overrides):
    locator = {
        "project_id": PROJECT_ID,
        "source_document_type": "scene",
        "source_document_id": "scene_001",
        "source_document_version": "1",
        "source_map_id": SOURCE_MAP_ID,
        "snapshot_id": SNAPSHOT_ID,
        "snapshot_hash": SNAPSHOT_HASH,
        "segment_id": "segment_001",
        "section_id": None,
        "chapter_id": "chapter_001",
        "scene_id": "scene_001",
        "paragraph_index": 0,
        "sentence_index": 0,
        "line_start": 1,
        "line_end": 1,
        "char_start": 0,
        "char_end": len(SAMPLE_TEXT),
        "byte_start": 0,
        "byte_end": len(SAMPLE_TEXT.encode("utf-8")),
        "token_start": 0,
        "token_end": 11,
        "locator_precision": "exact",
        "source_label": "Opening scene",
        "source_hash": SOURCE_HASH,
    }
    locator.update(overrides)
    return locator


def build_evidence_record(**overrides):
    record = {
        "evidence_id": "evidence_001",
        "project_id": PROJECT_ID,
        "source_locator": build_valid_source_locator(),
        "source_document": build_valid_source_document_ref(),
        "source_map_id": SOURCE_MAP_ID,
        "snapshot_id": SNAPSHOT_ID,
        "snapshot_hash": SNAPSHOT_HASH,
        "evidence_kind": "mention",
        "claim_supported": "A source-derived extraction claim is attached to the locator.",
        "text_excerpt": SAMPLE_TEXT,
        "excerpt_hash": "sha256:excerpt-001",
        "char_start": 0,
        "char_end": len(SAMPLE_TEXT),
        "byte_start": 0,
        "byte_end": len(SAMPLE_TEXT.encode("utf-8")),
        "token_start": 0,
        "token_end": 11,
        "line_start": 1,
        "line_end": 1,
        "locator_precision": "exact",
        "confidence": 0.72,
        "created_at": "2026-06-19T00:00:00Z",
        "created_by": "booknlp_adapter_contract_fixture",
        "provenance": {
            "run_id": RUN_ID,
            "created_by": "booknlp_adapter_contract_fixture",
            "source_type": "owner_authored",
            "human_review_required": True,
        },
        "notes": "",
    }
    record.update(overrides)
    return record


def build_raw_output_reference(artifact_name, artifact_kind, artifact_hash, **overrides):
    reference = {
        "raw_output_id": f"raw_{artifact_kind}",
        "project_id": PROJECT_ID,
        "tool_name": "booknlp",
        "run_id": RUN_ID,
        "artifact_name": artifact_name,
        "artifact_kind": artifact_kind,
        "artifact_path_hint": f"writer_assistant/extractions/booknlp/{RUN_ID}/raw/{artifact_name}",
        "artifact_hash": artifact_hash,
        "artifact_hash_algorithm": "sha256",
        "created_at": "2026-06-19T00:00:00Z",
        "source_snapshot_hashes": [SNAPSHOT_HASH],
        "is_canon": False,
        "is_candidate": False,
    }
    reference.update(overrides)
    return reference


def build_mock_booknlp_tokens(**overrides):
    tokens = [
        {
            "token_id": 0,
            "sentence_id": 0,
            "paragraph_id": 0,
            "char_start": 0,
            "char_end": 5,
            "byte_start": 0,
            "byte_end": 5,
            "token": "Alice",
            "lemma": "Alice",
            "pos": "PROPN",
            "dependency": "nsubj",
            "ner": "PERSON",
            "source_locator": build_valid_source_locator(char_start=0, char_end=5, byte_start=0, byte_end=5, token_start=0, token_end=1),
        },
        {
            "token_id": 1,
            "sentence_id": 0,
            "paragraph_id": 0,
            "char_start": 6,
            "char_end": 12,
            "byte_start": 6,
            "byte_end": 12,
            "token": "opened",
            "lemma": "open",
            "pos": "VERB",
            "dependency": "ROOT",
            "ner": "O",
            "source_locator": build_valid_source_locator(char_start=6, char_end=12, byte_start=6, byte_end=12, token_start=1, token_end=2),
        },
        {
            "token_id": 6,
            "sentence_id": 0,
            "paragraph_id": 0,
            "char_start": 37,
            "char_end": 40,
            "byte_start": 37,
            "byte_end": 40,
            "token": "Bob",
            "lemma": "Bob",
            "pos": "PROPN",
            "dependency": "nsubj",
            "ner": "PERSON",
            "source_locator": build_valid_source_locator(char_start=37, char_end=40, byte_start=37, byte_end=40, token_start=6, token_end=7),
        },
    ]
    if overrides:
        tokens[0].update(overrides)
    return tokens


def build_mock_booknlp_entities(**overrides):
    entities = [
        {
            "entity_id": "entity_001",
            "mention_id": "mention_001",
            "mention_text": "Alice",
            "entity_type": "PER",
            "char_start": 0,
            "char_end": 5,
            "token_start": 0,
            "token_end": 1,
            "source_locator": build_valid_source_locator(char_start=0, char_end=5, byte_start=0, byte_end=5, token_start=0, token_end=1),
            "confidence": 0.87,
            "cluster_id": "cluster_001",
        },
        {
            "entity_id": "entity_002",
            "mention_id": "mention_002",
            "mention_text": "Bob",
            "entity_type": "PER",
            "char_start": 37,
            "char_end": 40,
            "token_start": 6,
            "token_end": 7,
            "source_locator": build_valid_source_locator(char_start=37, char_end=40, byte_start=37, byte_end=40, token_start=6, token_end=7),
            "confidence": 0.82,
            "cluster_id": "cluster_002",
        },
    ]
    if overrides:
        entities[0].update(overrides)
    return entities


def build_mock_booknlp_quotes(**overrides):
    quotes = [
        {
            "quote_id": "quote_001",
            "quote_text": '"Wait,"',
            "char_start": 29,
            "char_end": 36,
            "speaker_entity_id": "entity_002",
            "speaker_mention_text": "Bob",
            "speaker_confidence": 0.73,
            "source_locator": build_valid_source_locator(char_start=29, char_end=36, byte_start=29, byte_end=36, token_start=4, token_end=6),
        }
    ]
    if overrides:
        quotes[0].update(overrides)
    return quotes


def build_mock_booknlp_book_json(**overrides):
    book_json = {
        "characters": [
            {
                "character_id": "cluster_001",
                "names": ["Alice"],
                "mention_count": 1,
                "raw_support_only": True,
            }
        ],
        "entities": {"cluster_001": ["mention_001"], "cluster_002": ["mention_002"]},
        "quotes": {"quote_001": {"speaker_entity_id": "entity_002"}},
        "metadata": {"source": "mock_fixture", "raw_support_only": True},
    }
    book_json.update(overrides)
    return book_json


def build_mock_booknlp_supersense(**overrides):
    supersense = [
        {
            "supersense_id": "supersense_001",
            "text": "brass door",
            "category": "noun.artifact",
            "char_start": 17,
            "char_end": 27,
            "source_locator": build_valid_source_locator(char_start=17, char_end=27, byte_start=17, byte_end=27, token_start=3, token_end=5),
            "confidence": 0.66,
        }
    ]
    if overrides:
        supersense[0].update(overrides)
    return supersense


def build_mock_booknlp_events(**overrides):
    events = [
        {
            "event_id": "event_001",
            "event_text": "opened",
            "event_type": "action_signal",
            "char_start": 6,
            "char_end": 12,
            "source_locator": build_valid_source_locator(char_start=6, char_end=12, byte_start=6, byte_end=12, token_start=1, token_end=2),
            "confidence": 0.68,
        }
    ]
    if overrides:
        events[0].update(overrides)
    return events


def build_mock_booknlp_run_manifest(**overrides):
    raw_artifacts = [
        build_raw_output_reference("tokens.tsv", "booknlp_tokens", "sha256:tokens"),
        build_raw_output_reference("entities.tsv", "booknlp_entities", "sha256:entities"),
        build_raw_output_reference("quotes.tsv", "booknlp_quotes", "sha256:quotes"),
        build_raw_output_reference("book.json", "booknlp_book_json", "sha256:book-json"),
        build_raw_output_reference("supersense.tsv", "booknlp_supersense", "sha256:supersense"),
        build_raw_output_reference("events.tsv", "booknlp_events", "sha256:events"),
    ]
    manifest = {
        "run_id": RUN_ID,
        "project_id": PROJECT_ID,
        "tool_name": "booknlp",
        "tool_version": "mock-0",
        "adapter_name": "booknlp_adapter_contract",
        "adapter_version": "0",
        "run_type": "booknlp_raw_import",
        "status": "complete",
        "source_documents": [build_valid_source_document_ref()],
        "input_snapshot_hashes": [SNAPSHOT_HASH],
        "raw_artifacts": raw_artifacts,
        "artifact_hashes": {
            "tokens": "sha256:tokens",
            "entities": "sha256:entities",
            "quotes": "sha256:quotes",
            "book_json": "sha256:book-json",
            "supersense": "sha256:supersense",
            "events": "sha256:events",
        },
        "started_at": "2026-06-19T00:00:00Z",
        "finished_at": "2026-06-19T00:00:01Z",
        "parameters": {"pipeline": "mock_fixture"},
        "environment": {"runtime": "contract_test"},
        "warnings": [],
        "errors": [],
        "human_review_required": True,
        "candidate_generation_allowed": False,
        "canon_write_allowed": False,
        "prose_generation_allowed": False,
    }
    manifest.update(overrides)
    return manifest


def build_mock_booknlp_raw_artifact_bundle(**overrides):
    manifest = build_mock_booknlp_run_manifest()
    bundle = {
        "bundle_id": "bundle_001",
        "project_id": PROJECT_ID,
        "run_manifest": manifest,
        "source_map": build_valid_source_map(),
        "tokens": build_mock_booknlp_tokens(),
        "entities": build_mock_booknlp_entities(),
        "quotes": build_mock_booknlp_quotes(),
        "book_json": build_mock_booknlp_book_json(),
        "supersense": build_mock_booknlp_supersense(),
        "events": build_mock_booknlp_events(),
        "raw_output_references": deepcopy(manifest["raw_artifacts"]),
        "created_at": "2026-06-19T00:00:02Z",
    }
    bundle.update(overrides)
    return bundle


def build_expected_candidate_draft(**overrides):
    draft = {
        "candidate_type": "character_candidate",
        "target_category": "characters",
        "source_locator": build_valid_source_locator(char_start=0, char_end=5, byte_start=0, byte_end=5, token_start=0, token_end=1),
        "evidence": [build_evidence_record(text_excerpt="Alice", char_start=0, char_end=5, byte_start=0, byte_end=5, token_start=0, token_end=1)],
        "provenance": {
            "run_id": RUN_ID,
            "created_by": "booknlp_adapter_contract",
            "source_type": "booknlp_raw_import",
            "human_review_required": True,
        },
        "confidence": 0.87,
        "raw_output_refs": [build_raw_output_reference("entities.tsv", "booknlp_entities", "sha256:entities")],
        "normalization_status": "candidate_draft",
    }
    draft.update(overrides)
    return draft


def remove_field(payload, field):
    copy = dict(payload)
    del copy[field]
    return copy


def with_extra(payload, field, value=True):
    copy = dict(payload)
    copy[field] = value
    return copy


def assert_rejects(validator, payload):
    with pytest.raises(ValueError):
        validator(payload)


def assert_not_mutated(callable_obj, *args):
    originals = deepcopy(args)
    try:
        callable_obj(*args)
    except ValueError:
        pass
    assert args == originals


def assert_draft_contract_shape(draft):
    assert set(CANDIDATE_DRAFT_REQUIRED_FIELDS).issubset(draft)
    assert isinstance(draft["evidence"], list)
    assert draft["evidence"]
    source_map.validate_source_locator(draft["source_locator"])
    for evidence_record in draft["evidence"]:
        evidence.validate_evidence_record(evidence_record)
    assert 0.0 <= draft["confidence"] <= 1.0
    assert draft["normalization_status"] in {
        "candidate_draft",
        "insufficient_evidence",
        "rejected_output",
    }
    assert draft.get("status") != "promoted"
    assert draft.get("owner_decision") != "promote"
    for forbidden in FORBIDDEN_PROSE_MUTATION_FIELDS + FORBIDDEN_DRAFT_FIELDS_OR_VALUES:
        assert forbidden not in draft
        assert forbidden not in draft.values()


def test_module_import_exposes_expected_future_api():
    for api_name in EXPECTED_PUBLIC_API:
        assert hasattr(booknlp_adapter_contract, api_name)


def test_existing_source_map_and_evidence_fixtures_validate():
    source_map.validate_source_document_ref(build_valid_source_document_ref())
    source_map.validate_source_segment(build_valid_source_segment())
    source_map.validate_source_map(build_valid_source_map())
    source_map.validate_source_locator(build_valid_source_locator())
    evidence.validate_raw_output_reference(
        build_raw_output_reference("tokens.tsv", "booknlp_tokens", "sha256:tokens")
    )
    evidence.validate_evidence_record(build_evidence_record())


def test_validate_booknlp_run_manifest_accepts_valid_manifest():
    validated = booknlp_adapter_contract.validate_booknlp_run_manifest(
        build_mock_booknlp_run_manifest()
    )
    assert validated == build_mock_booknlp_run_manifest()


@pytest.mark.parametrize("field", MANIFEST_REQUIRED_FIELDS)
def test_validate_booknlp_run_manifest_rejects_missing_required_fields(field):
    assert_rejects(
        booknlp_adapter_contract.validate_booknlp_run_manifest,
        remove_field(build_mock_booknlp_run_manifest(), field),
    )


@pytest.mark.parametrize("status", ALLOWED_STATUSES)
def test_validate_booknlp_run_manifest_accepts_allowed_statuses(status):
    manifest = build_mock_booknlp_run_manifest(status=status)
    assert booknlp_adapter_contract.validate_booknlp_run_manifest(manifest)["status"] == status


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("status", "unknown"),
        ("tool_name", "spacy"),
        ("run_type", "runtime_extraction"),
        ("human_review_required", False),
        ("candidate_generation_allowed", True),
        ("canon_write_allowed", True),
        ("prose_generation_allowed", True),
        ("source_documents", {"not": "a-list"}),
    ),
)
def test_validate_booknlp_run_manifest_rejects_policy_violations(field, value):
    assert_rejects(
        booknlp_adapter_contract.validate_booknlp_run_manifest,
        build_mock_booknlp_run_manifest(**{field: value}),
    )


def test_validate_booknlp_run_manifest_validates_nested_refs_and_artifacts():
    manifest = build_mock_booknlp_run_manifest(
        source_documents=[build_valid_source_document_ref(source_document_id="../escape")]
    )
    assert_rejects(booknlp_adapter_contract.validate_booknlp_run_manifest, manifest)

    manifest = build_mock_booknlp_run_manifest(
        raw_artifacts=[
            build_raw_output_reference(
                "tokens.tsv",
                "booknlp_tokens",
                "sha256:tokens",
                is_candidate=True,
            )
        ]
    )
    assert_rejects(booknlp_adapter_contract.validate_booknlp_run_manifest, manifest)


@pytest.mark.parametrize("field", FORBIDDEN_PROSE_MUTATION_FIELDS)
def test_validate_booknlp_run_manifest_rejects_prompt_prose_and_mutation_fields(field):
    assert_rejects(
        booknlp_adapter_contract.validate_booknlp_run_manifest,
        with_extra(build_mock_booknlp_run_manifest(), field, "forbidden"),
    )


def test_validate_booknlp_run_manifest_does_not_mutate_caller_input():
    manifest = build_mock_booknlp_run_manifest()
    assert_not_mutated(booknlp_adapter_contract.validate_booknlp_run_manifest, manifest)


def test_validate_booknlp_raw_artifact_bundle_accepts_valid_bundle():
    validated = booknlp_adapter_contract.validate_booknlp_raw_artifact_bundle(
        build_mock_booknlp_raw_artifact_bundle()
    )
    assert validated == build_mock_booknlp_raw_artifact_bundle()


@pytest.mark.parametrize("field", BUNDLE_REQUIRED_FIELDS)
def test_validate_booknlp_raw_artifact_bundle_rejects_missing_required_fields(field):
    assert_rejects(
        booknlp_adapter_contract.validate_booknlp_raw_artifact_bundle,
        remove_field(build_mock_booknlp_raw_artifact_bundle(), field),
    )


def test_validate_booknlp_raw_artifact_bundle_validates_nested_manifest_source_map_and_refs():
    assert_rejects(
        booknlp_adapter_contract.validate_booknlp_raw_artifact_bundle,
        build_mock_booknlp_raw_artifact_bundle(
            run_manifest=build_mock_booknlp_run_manifest(tool_name="wrong_tool")
        ),
    )
    assert_rejects(
        booknlp_adapter_contract.validate_booknlp_raw_artifact_bundle,
        build_mock_booknlp_raw_artifact_bundle(
            source_map=build_valid_source_map(snapshot_hash="")
        ),
    )
    assert_rejects(
        booknlp_adapter_contract.validate_booknlp_raw_artifact_bundle,
        build_mock_booknlp_raw_artifact_bundle(
            raw_output_references=[
                build_raw_output_reference("tokens.tsv", "booknlp_tokens", "")
            ]
        ),
    )


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("tokens", {}),
        ("entities", {}),
        ("quotes", {}),
        ("book_json", []),
        ("supersense", {}),
        ("events", {}),
        ("raw_output_references", {}),
    ),
)
def test_validate_booknlp_raw_artifact_bundle_requires_expected_collection_shapes(field, value):
    assert_rejects(
        booknlp_adapter_contract.validate_booknlp_raw_artifact_bundle,
        build_mock_booknlp_raw_artifact_bundle(**{field: value}),
    )


@pytest.mark.parametrize("field", BUNDLE_FORBIDDEN_SHORTCUT_FIELDS + FORBIDDEN_PROSE_MUTATION_FIELDS)
def test_validate_booknlp_raw_artifact_bundle_rejects_canon_candidate_prose_mutation_fields(field):
    assert_rejects(
        booknlp_adapter_contract.validate_booknlp_raw_artifact_bundle,
        with_extra(build_mock_booknlp_raw_artifact_bundle(), field, True),
    )


def test_validate_booknlp_raw_artifact_bundle_does_not_mutate_caller_input():
    bundle = build_mock_booknlp_raw_artifact_bundle()
    assert_not_mutated(booknlp_adapter_contract.validate_booknlp_raw_artifact_bundle, bundle)


def test_token_artifact_contract_accepts_source_mapped_half_open_offsets():
    token = build_mock_booknlp_tokens()[0]
    assert token["char_start"] == 0
    assert token["char_end"] == 5
    assert token["char_start"] >= 0
    assert token["char_end"] > token["char_start"]
    source_map.validate_source_locator(token["source_locator"])
    booknlp_adapter_contract.validate_booknlp_raw_artifact_bundle(
        build_mock_booknlp_raw_artifact_bundle(tokens=build_mock_booknlp_tokens())
    )


@pytest.mark.parametrize(
    "tokens",
    (
        build_mock_booknlp_tokens(char_start=-1),
        build_mock_booknlp_tokens(char_start=7, char_end=5),
        build_mock_booknlp_tokens(source_locator=None),
        build_mock_booknlp_tokens(is_candidate=True),
        build_mock_booknlp_tokens(is_canon=True),
    ),
)
def test_token_artifact_rejects_invalid_offsets_missing_locator_and_direct_candidate_canon(tokens):
    assert_rejects(
        booknlp_adapter_contract.validate_booknlp_raw_artifact_bundle,
        build_mock_booknlp_raw_artifact_bundle(tokens=tokens),
    )


def test_entity_artifact_contract_accepts_support_only_mentions():
    entity = build_mock_booknlp_entities()[0]
    assert entity["entity_type"] == "PER"
    assert 0.0 <= entity["confidence"] <= 1.0
    source_map.validate_source_locator(entity["source_locator"])
    booknlp_adapter_contract.validate_booknlp_raw_artifact_bundle(
        build_mock_booknlp_raw_artifact_bundle(entities=build_mock_booknlp_entities())
    )


@pytest.mark.parametrize(
    "entities",
    (
        build_mock_booknlp_entities(confidence=-0.1),
        build_mock_booknlp_entities(confidence=1.1),
        build_mock_booknlp_entities(char_start=6, char_end=5),
        build_mock_booknlp_entities(source_locator=None),
        build_mock_booknlp_entities(approved_truth=True),
    ),
)
def test_entity_artifact_rejects_invalid_confidence_offsets_locator_and_truth_shortcuts(entities):
    assert_rejects(
        booknlp_adapter_contract.validate_booknlp_raw_artifact_bundle,
        build_mock_booknlp_raw_artifact_bundle(entities=entities),
    )


def test_entity_mentions_normalize_to_candidate_drafts_with_evidence_not_persistence_records():
    drafts = booknlp_adapter_contract.normalize_booknlp_entity_mentions(
        build_mock_booknlp_raw_artifact_bundle(),
        build_valid_source_map(),
    )
    assert isinstance(drafts, list)
    assert drafts
    for draft in drafts:
        # Candidate draft types may precede candidate_record registration, so this
        # checks draft shape instead of requiring persistence validation.
        assert_draft_contract_shape(draft)
        assert draft["target_category"] in {
            "characters",
            "locations_settings",
            "organizations_groups",
            "objects_items",
        }


def test_entity_normalization_fails_closed_for_unsupported_entity_type_without_guessing():
    bundle = build_mock_booknlp_raw_artifact_bundle(
        entities=build_mock_booknlp_entities(entity_type="UNKNOWN")
    )
    drafts = booknlp_adapter_contract.normalize_booknlp_entity_mentions(
        bundle,
        build_valid_source_map(),
    )
    assert drafts
    assert all(draft["normalization_status"] in {"rejected_output", "insufficient_evidence"} for draft in drafts)


def test_entity_normalization_does_not_mutate_inputs():
    bundle = build_mock_booknlp_raw_artifact_bundle()
    source_map_record = build_valid_source_map()
    assert_not_mutated(
        booknlp_adapter_contract.normalize_booknlp_entity_mentions,
        bundle,
        source_map_record,
    )


def test_quote_artifact_contract_accepts_source_derived_quote_support_only():
    quote = build_mock_booknlp_quotes()[0]
    assert quote["quote_text"] == '"Wait,"'
    assert 0.0 <= quote["speaker_confidence"] <= 1.0
    source_map.validate_source_locator(quote["source_locator"])
    booknlp_adapter_contract.validate_booknlp_raw_artifact_bundle(
        build_mock_booknlp_raw_artifact_bundle(quotes=build_mock_booknlp_quotes())
    )


@pytest.mark.parametrize(
    "quotes",
    (
        build_mock_booknlp_quotes(speaker_confidence=-0.01),
        build_mock_booknlp_quotes(speaker_confidence=1.01),
        build_mock_booknlp_quotes(source_locator=None),
        build_mock_booknlp_quotes(generated_dialogue="No generated dialogue."),
        build_mock_booknlp_quotes(speaker_truth=True),
    ),
)
def test_quote_artifact_rejects_invalid_confidence_missing_locator_and_generated_dialogue(quotes):
    assert_rejects(
        booknlp_adapter_contract.validate_booknlp_raw_artifact_bundle,
        build_mock_booknlp_raw_artifact_bundle(quotes=quotes),
    )


def test_quote_normalization_keeps_speaker_attribution_as_candidate_support():
    drafts = booknlp_adapter_contract.normalize_booknlp_quotes(
        build_mock_booknlp_raw_artifact_bundle(),
        build_valid_source_map(),
    )
    assert isinstance(drafts, list)
    assert drafts
    for draft in drafts:
        assert_draft_contract_shape(draft)
        assert draft["confidence"] <= 1.0
        assert "speaker_truth" not in draft
        assert "generated_dialogue" not in draft


def test_quote_normalization_fails_closed_for_ambiguous_speaker_without_truth_claim():
    bundle = build_mock_booknlp_raw_artifact_bundle(
        quotes=build_mock_booknlp_quotes(speaker_entity_id=None, speaker_confidence=0.0)
    )
    drafts = booknlp_adapter_contract.normalize_booknlp_quotes(bundle, build_valid_source_map())
    assert drafts
    assert all(draft["normalization_status"] in {"rejected_output", "insufficient_evidence"} for draft in drafts)


def test_book_json_artifact_contract_accepts_aggregate_support_only():
    bundle = build_mock_booknlp_raw_artifact_bundle(book_json=build_mock_booknlp_book_json())
    validated = booknlp_adapter_contract.validate_booknlp_raw_artifact_bundle(bundle)
    assert validated["book_json"]["metadata"]["raw_support_only"] is True


@pytest.mark.parametrize(
    "book_json",
    (
        build_mock_booknlp_book_json(update_bible=True),
        build_mock_booknlp_book_json(update_storyform=True),
        build_mock_booknlp_book_json(update_memory=True),
        build_mock_booknlp_book_json(approved_character_roster=["Alice"]),
        build_mock_booknlp_book_json(storyform_truth={"throughline": "guessed"}),
    ),
)
def test_book_json_rejects_bible_storyform_memory_canon_and_roster_shortcuts(book_json):
    assert_rejects(
        booknlp_adapter_contract.validate_booknlp_raw_artifact_bundle,
        build_mock_booknlp_raw_artifact_bundle(book_json=book_json),
    )


def test_supersense_artifact_contract_accepts_semantic_support_only():
    record = build_mock_booknlp_supersense()[0]
    assert record["category"] == "noun.artifact"
    assert 0.0 <= record["confidence"] <= 1.0
    source_map.validate_source_locator(record["source_locator"])
    booknlp_adapter_contract.validate_booknlp_raw_artifact_bundle(
        build_mock_booknlp_raw_artifact_bundle(supersense=build_mock_booknlp_supersense())
    )


@pytest.mark.parametrize(
    "supersense",
    (
        build_mock_booknlp_supersense(confidence=-0.1),
        build_mock_booknlp_supersense(confidence=1.1),
        build_mock_booknlp_supersense(source_locator=None),
        build_mock_booknlp_supersense(dramatica_label="Issue"),
        build_mock_booknlp_supersense(subtxt_label="Conflict"),
    ),
)
def test_supersense_rejects_invalid_confidence_locator_and_structural_labels(supersense):
    assert_rejects(
        booknlp_adapter_contract.validate_booknlp_raw_artifact_bundle,
        build_mock_booknlp_raw_artifact_bundle(supersense=supersense),
    )


def test_event_artifact_contract_accepts_action_support_only():
    event = build_mock_booknlp_events()[0]
    assert event["event_type"] == "action_signal"
    assert 0.0 <= event["confidence"] <= 1.0
    source_map.validate_source_locator(event["source_locator"])
    booknlp_adapter_contract.validate_booknlp_raw_artifact_bundle(
        build_mock_booknlp_raw_artifact_bundle(events=build_mock_booknlp_events())
    )


@pytest.mark.parametrize(
    "events",
    (
        build_mock_booknlp_events(char_start=-1),
        build_mock_booknlp_events(char_start=12, char_end=6),
        build_mock_booknlp_events(confidence=-0.1),
        build_mock_booknlp_events(confidence=1.1),
        build_mock_booknlp_events(source_locator=None),
        build_mock_booknlp_events(timeline_canon=True),
        build_mock_booknlp_events(causal_chain_truth=True),
    ),
)
def test_event_artifact_rejects_invalid_offsets_confidence_locator_and_truth_shortcuts(events):
    assert_rejects(
        booknlp_adapter_contract.validate_booknlp_raw_artifact_bundle,
        build_mock_booknlp_raw_artifact_bundle(events=events),
    )


def test_event_normalization_returns_candidate_support_only():
    drafts = booknlp_adapter_contract.normalize_booknlp_events(
        build_mock_booknlp_raw_artifact_bundle(),
        build_valid_source_map(),
    )
    assert isinstance(drafts, list)
    assert drafts
    for draft in drafts:
        assert_draft_contract_shape(draft)
        assert "timeline_canon" not in draft
        assert "causal_chain_truth" not in draft


@pytest.mark.parametrize(
    "bundle",
    (
        build_mock_booknlp_raw_artifact_bundle(events=build_mock_booknlp_events(source_locator=None)),
        build_mock_booknlp_raw_artifact_bundle(events=build_mock_booknlp_events(char_start=12, char_end=6)),
        build_mock_booknlp_raw_artifact_bundle(events=build_mock_booknlp_events(confidence=None)),
    ),
)
def test_event_normalization_fails_closed_for_invalid_structurally_usable_claims(bundle):
    drafts = booknlp_adapter_contract.normalize_booknlp_events(bundle, build_valid_source_map())
    assert drafts
    assert all(draft["normalization_status"] in {"rejected_output", "insufficient_evidence"} for draft in drafts)


def test_candidate_draft_builder_combines_entity_quote_and_event_drafts_without_promotion():
    drafts = booknlp_adapter_contract.build_booknlp_candidate_drafts(
        build_mock_booknlp_raw_artifact_bundle(),
        build_valid_source_map(),
    )
    assert isinstance(drafts, list)
    assert drafts
    for draft in drafts:
        assert_draft_contract_shape(draft)
        assert draft.get("status") != "promoted"
        assert draft.get("owner_decision") != "promote"


def test_candidate_draft_builder_fails_closed_for_unsupported_raw_artifacts():
    bundle = build_mock_booknlp_raw_artifact_bundle(unknown_artifact=[{"kind": "mystery"}])
    with pytest.raises(ValueError):
        booknlp_adapter_contract.build_booknlp_candidate_drafts(bundle, build_valid_source_map())


def test_candidate_draft_builder_does_not_mutate_inputs():
    bundle = build_mock_booknlp_raw_artifact_bundle()
    source_map_record = build_valid_source_map()
    assert_not_mutated(
        booknlp_adapter_contract.build_booknlp_candidate_drafts,
        bundle,
        source_map_record,
    )


@pytest.mark.parametrize(
    "bundle",
    (
        build_mock_booknlp_raw_artifact_bundle(
            run_manifest=build_mock_booknlp_run_manifest(input_snapshot_hashes=[])
        ),
        build_mock_booknlp_raw_artifact_bundle(
            run_manifest=build_mock_booknlp_run_manifest(
                source_documents=[build_valid_source_document_ref(source_document_id="../bad")]
            )
        ),
        build_mock_booknlp_raw_artifact_bundle(tokens=build_mock_booknlp_tokens(source_locator=None)),
        build_mock_booknlp_raw_artifact_bundle(tokens=build_mock_booknlp_tokens(char_start=8, char_end=3)),
        build_mock_booknlp_raw_artifact_bundle(raw_output_references=[]),
        with_extra(build_mock_booknlp_raw_artifact_bundle(), "model_output", "forbidden"),
    ),
)
def test_fail_closed_invalid_manifest_bundle_locator_offsets_hashes_and_mutation_fields_raise(bundle):
    with pytest.raises(ValueError):
        booknlp_adapter_contract.validate_booknlp_raw_artifact_bundle(bundle)


@pytest.mark.parametrize(
    "bundle",
    (
        build_mock_booknlp_raw_artifact_bundle(entities=build_mock_booknlp_entities(entity_type="ALIEN")),
        build_mock_booknlp_raw_artifact_bundle(entities=build_mock_booknlp_entities(confidence=None)),
        build_mock_booknlp_raw_artifact_bundle(quotes=build_mock_booknlp_quotes(speaker_entity_id=None)),
    ),
)
def test_fail_closed_ambiguous_or_unsupported_claims_return_rejected_or_insufficient_evidence(bundle):
    drafts = booknlp_adapter_contract.build_booknlp_candidate_drafts(bundle, build_valid_source_map())
    assert drafts
    assert all(draft["normalization_status"] in {"rejected_output", "insufficient_evidence"} for draft in drafts)


def test_runtime_tool_boundary_future_module_source_has_no_runtime_dependency_or_io_terms():
    production_source = inspect.getsource(booknlp_adapter_contract)
    for forbidden in FORBIDDEN_PRODUCTION_SOURCE_TERMS:
        assert forbidden not in production_source


def test_candidate_draft_evidence_uses_existing_helper_shapes_where_possible():
    draft = build_expected_candidate_draft()
    assert_draft_contract_shape(draft)
    # Future adapter candidate draft types may not be persistence-registered yet.
    # Persistence validation is intentionally deferred to the implementation task.
