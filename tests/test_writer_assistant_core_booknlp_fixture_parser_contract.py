"""Contract tests for the future BookNLP fixture parser.

PHASE8-IMPL-008-T006 is tests-first only. The future pure parser module is
imported normally so this targeted file is expected red until a later task
creates it:
- backend.story_knowledge.booknlp_fixture_parser

Fixtures are synthetic, owner-authored, in-memory strings and dictionaries.
These tests do not install, import, or run BookNLP/spaCy and do not write raw
extraction artifacts.
"""

from copy import deepcopy
import json
from pathlib import Path

import pytest

from backend.story_knowledge import booknlp_adapter_contract
from backend.story_knowledge import evidence
from backend.story_knowledge import raw_extraction_storage
from backend.story_knowledge import source_map as source_map_helpers
from backend.story_knowledge import booknlp_fixture_parser

PROJECT_ID = "example"
RUN_ID = "run_20260621_001"
SOURCE_MAP_ID = "source_map_001"
SNAPSHOT_ID = "snapshot_001"
SNAPSHOT_HASH = "sha256:snapshot-001"
SOURCE_HASH = "sha256:source-doc-001"
CREATED_AT = "2026-06-21T00:00:00Z"

EXPECTED_PUBLIC_API = (
    "parse_booknlp_tokens_tsv",
    "parse_booknlp_entities_tsv",
    "parse_booknlp_quotes_tsv",
    "parse_booknlp_supersense_tsv",
    "parse_booknlp_book_json",
    "build_booknlp_raw_artifact_bundle_from_fixture_texts",
    "derive_booknlp_events_from_tokens",
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
        "event": "O",
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
        "adapter_name": "writer_assistant_booknlp_fixture_parser",
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
        "tokens_tsv": valid_tokens_tsv(event="EVENT"),
        "entities_tsv": valid_entities_tsv(),
        "quotes_tsv": valid_quotes_tsv(),
        "supersense_tsv": valid_supersense_tsv(),
        "book_json": valid_book_json_text(),
    }
    payload.update(overrides)
    return payload


def assert_all_public_apis_exist():
    for name in EXPECTED_PUBLIC_API:
        assert hasattr(booknlp_fixture_parser, name)


def mutate_tsv_header(text, replacement_header):
    lines = text.splitlines()
    lines[0] = "\t".join(replacement_header)
    return "\n".join(lines) + "\n"


def test_future_parser_module_exposes_expected_public_api():
    assert_all_public_apis_exist()


def test_parse_tokens_tsv_parses_valid_text_and_does_not_mutate_input():
    text = valid_tokens_tsv()
    before = text[:]
    rows = booknlp_fixture_parser.parse_booknlp_tokens_tsv(text)
    assert text == before
    assert rows == [
        {
            "paragraph_ID": 0,
            "sentence_ID": 0,
            "token_ID_within_sentence": 0,
            "token_ID_within_document": 0,
            "word": "Alice",
            "lemma": "Alice",
            "byte_onset": 0,
            "byte_offset": 5,
            "POS_tag": "PROPN",
            "fine_POS_tag": "NNP",
            "dependency_relation": "nsubj",
            "syntactic_head_ID": 1,
            "event": "O",
        }
    ]


@pytest.mark.parametrize(
    "text",
    [
        mutate_tsv_header(valid_tokens_tsv(), TOKENS_HEADER[:-1]),
        mutate_tsv_header(valid_tokens_tsv(), (*TOKENS_HEADER, "unknown")),
        "\t".join(TOKENS_HEADER) + "\n0\t0\n",
        valid_tokens_tsv(word=""),
        valid_tokens_tsv(byte_onset="-1"),
        valid_tokens_tsv(byte_onset="1.5"),
        valid_tokens_tsv(byte_onset="True"),
        valid_tokens_tsv(byte_onset="6", byte_offset="5"),
        "",
    ],
)
def test_parse_tokens_tsv_fails_closed_for_invalid_input(text):
    with pytest.raises(ValueError):
        booknlp_fixture_parser.parse_booknlp_tokens_tsv(text)


def test_parse_tokens_tsv_header_only_returns_empty_list():
    assert booknlp_fixture_parser.parse_booknlp_tokens_tsv("\t".join(TOKENS_HEADER) + "\n") == []


def test_parse_entities_tsv_parses_valid_text_and_keeps_raw_support_only():
    rows = booknlp_fixture_parser.parse_booknlp_entities_tsv(valid_entities_tsv())
    assert rows == [
        {
            "COREF": 1,
            "start_token": 0,
            "end_token": 0,
            "prop": "PROP",
            "cat": "PER",
            "text": "Alice",
        }
    ]
    assert "candidate_records" not in rows[0]
    assert "approved_truth" not in rows[0]


@pytest.mark.parametrize(
    "text",
    [
        mutate_tsv_header(valid_entities_tsv(), ENTITIES_HEADER[:-1]),
        mutate_tsv_header(valid_entities_tsv(), (*ENTITIES_HEADER, "unknown")),
        "\t".join(ENTITIES_HEADER) + "\n1\t0\n",
        valid_entities_tsv(text=""),
        valid_entities_tsv(cat=""),
        valid_entities_tsv(COREF="-1"),
        valid_entities_tsv(COREF="False"),
        valid_entities_tsv(start_token="2", end_token="1"),
    ],
)
def test_parse_entities_tsv_fails_closed_for_invalid_input(text):
    with pytest.raises(ValueError):
        booknlp_fixture_parser.parse_booknlp_entities_tsv(text)


def test_parse_quotes_tsv_parses_valid_text_and_keeps_attribution_raw():
    rows = booknlp_fixture_parser.parse_booknlp_quotes_tsv(valid_quotes_tsv())
    assert rows == [
        {
            "quote_start": 4,
            "quote_end": 5,
            "mention_start": 6,
            "mention_end": 6,
            "mention_phrase": "Bob",
            "char_id": 2,
            "quote": "Wait.",
        }
    ]
    assert "speaker_truth" not in rows[0]
    assert "canon_records" not in rows[0]
    assert "candidate_records" not in rows[0]


@pytest.mark.parametrize(
    "text",
    [
        mutate_tsv_header(valid_quotes_tsv(), QUOTES_HEADER[:-1]),
        mutate_tsv_header(valid_quotes_tsv(), (*QUOTES_HEADER, "unknown")),
        "\t".join(QUOTES_HEADER) + "\n4\t5\n",
        valid_quotes_tsv(quote=""),
        valid_quotes_tsv(char_id="-1"),
        valid_quotes_tsv(char_id="True"),
        valid_quotes_tsv(quote_start="6", quote_end="5"),
        valid_quotes_tsv(mention_start="7", mention_end="6"),
    ],
)
def test_parse_quotes_tsv_fails_closed_for_invalid_input(text):
    with pytest.raises(ValueError):
        booknlp_fixture_parser.parse_booknlp_quotes_tsv(text)


def test_parse_supersense_tsv_parses_valid_text_and_remains_raw_support():
    rows = booknlp_fixture_parser.parse_booknlp_supersense_tsv(valid_supersense_tsv())
    assert rows == [
        {
            "start_token": 0,
            "end_token": 0,
            "supersense_category": "noun.person",
            "text": "Alice",
        }
    ]
    assert "candidate_records" not in rows[0]
    assert "approved_truth" not in rows[0]


@pytest.mark.parametrize(
    "text",
    [
        mutate_tsv_header(valid_supersense_tsv(), SUPERSENSE_HEADER[:-1]),
        mutate_tsv_header(valid_supersense_tsv(), (*SUPERSENSE_HEADER, "unknown")),
        "\t".join(SUPERSENSE_HEADER) + "\n0\n",
        valid_supersense_tsv(text=""),
        valid_supersense_tsv(supersense_category=""),
        valid_supersense_tsv(start_token="-1"),
        valid_supersense_tsv(start_token="False"),
        valid_supersense_tsv(start_token="2", end_token="1"),
    ],
)
def test_parse_supersense_tsv_fails_closed_for_invalid_input(text):
    with pytest.raises(ValueError):
        booknlp_fixture_parser.parse_booknlp_supersense_tsv(text)


def test_parse_book_json_parses_valid_object_and_keeps_g_raw_metadata_only():
    parsed = booknlp_fixture_parser.parse_booknlp_book_json(valid_book_json_text())
    assert parsed["characters"][0]["g"] == {"she/her": 2}
    assert "gender" not in parsed["characters"][0]
    assert "identity" not in parsed["characters"][0]
    assert "personal_attribute_claims" not in parsed["characters"][0]
    assert "candidate_records" not in parsed
    assert "memory_records" not in parsed
    assert "canon_records" not in parsed
    assert "omi_records" not in parsed


@pytest.mark.parametrize(
    "text",
    [
        "{",
        "[]",
        json.dumps({"not_characters": []}),
        json.dumps({"characters": {}}),
        json.dumps({"characters": ["Alice"]}),
        json.dumps({"characters": [{"id": 1, "mentions": []}]}),
        json.dumps({"characters": [{"id": 1, "mentions": {"proper": [{"c": "Alice"}]}}]}),
    ],
)
def test_parse_book_json_fails_closed_for_invalid_shape(text):
    with pytest.raises(ValueError):
        booknlp_fixture_parser.parse_booknlp_book_json(text)


def test_derive_events_from_tokens_uses_tokens_event_column_only():
    tokens = [
        {
            "paragraph_ID": 0,
            "sentence_ID": 0,
            "token_ID_within_sentence": 0,
            "token_ID_within_document": 0,
            "word": "opened",
            "lemma": "open",
            "byte_onset": 6,
            "byte_offset": 12,
            "POS_tag": "VERB",
            "fine_POS_tag": "VBD",
            "dependency_relation": "ROOT",
            "syntactic_head_ID": 0,
            "event": "EVENT",
        },
        {
            "paragraph_ID": 0,
            "sentence_ID": 0,
            "token_ID_within_sentence": 1,
            "token_ID_within_document": 1,
            "word": "door",
            "lemma": "door",
            "byte_onset": 13,
            "byte_offset": 17,
            "POS_tag": "NOUN",
            "fine_POS_tag": "NN",
            "dependency_relation": "obj",
            "syntactic_head_ID": 0,
            "event": "O",
        },
    ]
    events = booknlp_fixture_parser.derive_booknlp_events_from_tokens(tokens)
    assert events == [
        {
            "event_id": "booknlp_event_0",
            "event_text": "opened",
            "event_type": "booknlp_token_event",
            "token_ID_within_document": 0,
            "token_id": 0,
            "event": "EVENT",
            "word": "opened",
            "byte_onset": 6,
            "byte_offset": 12,
            "confidence": 0.0,
        }
    ]
    booknlp_adapter_contract.validate_booknlp_raw_artifact_bundle(
        build_expected_bundle(events=events)
    )


def test_derive_events_from_tokens_empty_and_non_event_markers_produce_no_events():
    rows = booknlp_fixture_parser.parse_booknlp_tokens_tsv(valid_tokens_tsv(event="O"))
    assert booknlp_fixture_parser.derive_booknlp_events_from_tokens(rows) == []
    rows = booknlp_fixture_parser.parse_booknlp_tokens_tsv(valid_tokens_tsv(event=""))
    with pytest.raises(ValueError):
        booknlp_fixture_parser.derive_booknlp_events_from_tokens(rows)


def test_no_events_raw_fixture_input_is_accepted():
    payload = fixture_texts(events_tsv="event_id\tevent\n1\topened\n")
    with pytest.raises(ValueError):
        booknlp_fixture_parser.build_booknlp_raw_artifact_bundle_from_fixture_texts(
            payload,
            run_manifest=build_storage_manifest(),
            source_map=build_source_map(),
            raw_output_references=adapter_raw_output_references(),
        )


def build_expected_adapter_manifest():
    storage_manifest = build_storage_manifest()
    return {
        "run_id": storage_manifest["run_id"],
        "project_id": storage_manifest["project_id"],
        "tool_name": storage_manifest["tool_name"],
        "tool_version": storage_manifest["tool_version"],
        "adapter_name": storage_manifest["adapter_name"],
        "adapter_version": storage_manifest["adapter_version"],
        "run_type": "booknlp_raw_import",
        "status": storage_manifest["status"],
        "source_documents": deepcopy(storage_manifest["source_documents"]),
        "input_snapshot_hashes": deepcopy(storage_manifest["source_snapshot_hashes"]),
        "raw_artifacts": adapter_raw_output_references(),
        "artifact_hashes": deepcopy(storage_manifest["artifact_hashes"]),
        "started_at": storage_manifest["created_at"],
        "finished_at": storage_manifest["updated_at"],
        "parameters": deepcopy(storage_manifest["parameters"]),
        "environment": deepcopy(storage_manifest["environment"]),
        "warnings": deepcopy(storage_manifest["warnings"]),
        "errors": deepcopy(storage_manifest["errors"]),
        "human_review_required": True,
        "candidate_generation_allowed": False,
        "canon_write_allowed": False,
        "prose_generation_allowed": False,
    }


def build_expected_bundle(**overrides):
    bundle = {
        "bundle_id": "booknlp_fixture_bundle_001",
        "project_id": PROJECT_ID,
        "run_manifest": build_expected_adapter_manifest(),
        "source_map": build_source_map(),
        "tokens": booknlp_fixture_parser.parse_booknlp_tokens_tsv(valid_tokens_tsv()),
        "entities": booknlp_fixture_parser.parse_booknlp_entities_tsv(valid_entities_tsv()),
        "quotes": booknlp_fixture_parser.parse_booknlp_quotes_tsv(valid_quotes_tsv()),
        "book_json": booknlp_fixture_parser.parse_booknlp_book_json(valid_book_json_text()),
        "supersense": booknlp_fixture_parser.parse_booknlp_supersense_tsv(
            valid_supersense_tsv()
        ),
        "events": [],
        "raw_output_references": adapter_raw_output_references(),
        "created_at": CREATED_AT,
    }
    bundle.update(overrides)
    return bundle


def test_bundle_builder_accepts_in_memory_strings_and_validates_contracts():
    source_map = build_source_map()
    manifest = build_storage_manifest()
    references = adapter_raw_output_references()
    before = (deepcopy(manifest), deepcopy(source_map), deepcopy(references))
    bundle = booknlp_fixture_parser.build_booknlp_raw_artifact_bundle_from_fixture_texts(
        fixture_texts(),
        run_manifest=manifest,
        source_map=source_map,
        raw_output_references=references,
    )

    raw_extraction_storage.validate_extraction_run_manifest(manifest)
    source_map_helpers.validate_source_map(source_map)
    for reference in references:
        evidence.validate_raw_output_reference(reference)
    booknlp_adapter_contract.validate_booknlp_raw_artifact_bundle(bundle)

    assert manifest == before[0]
    assert source_map == before[1]
    assert references == before[2]
    assert bundle["project_id"] == PROJECT_ID
    assert bundle["bundle_id"]
    assert bundle["created_at"]
    assert set(bundle) == {
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
    }


def test_bundle_builder_derives_events_from_token_event_column():
    bundle = booknlp_fixture_parser.build_booknlp_raw_artifact_bundle_from_fixture_texts(
        fixture_texts(tokens_tsv=valid_tokens_tsv(word="opened", lemma="open", event="EVENT")),
        run_manifest=build_storage_manifest(),
        source_map=build_source_map(),
        raw_output_references=adapter_raw_output_references(),
    )
    assert bundle["events"]
    assert bundle["events"][0]["word"] == "opened"
    assert bundle["events"][0]["event"] == "EVENT"
    assert "timeline_canon" not in bundle["events"][0]
    assert "causal_chain_truth" not in bundle["events"][0]
    assert "approved_truth" not in bundle["events"][0]


@pytest.mark.parametrize(
    "bad_fixtures",
    [
        {"tokens_tsv": Path("tokens.tsv")},
        {"entities_tsv": "fixtures/entities.tsv"},
        {"book_json": Path("book.json")},
        {"events_tsv": "not accepted"},
        {"unsupported": "value"},
    ],
)
def test_bundle_builder_rejects_paths_and_unsupported_fixture_keys(bad_fixtures):
    payload = fixture_texts()
    payload.update(bad_fixtures)
    with pytest.raises(ValueError):
        booknlp_fixture_parser.build_booknlp_raw_artifact_bundle_from_fixture_texts(
            payload,
            run_manifest=build_storage_manifest(),
            source_map=build_source_map(),
            raw_output_references=adapter_raw_output_references(),
        )


@pytest.mark.parametrize(
    "manifest, source_map, references",
    [
        (Path("manifest.json"), build_source_map(), adapter_raw_output_references()),
        (build_storage_manifest(), Path("source_map.json"), adapter_raw_output_references()),
        (build_storage_manifest(), build_source_map(), Path("raw_refs.json")),
    ],
)
def test_bundle_builder_rejects_manifest_source_map_and_refs_as_paths(
    manifest,
    source_map,
    references,
):
    with pytest.raises(ValueError):
        booknlp_fixture_parser.build_booknlp_raw_artifact_bundle_from_fixture_texts(
            fixture_texts(),
            run_manifest=manifest,
            source_map=source_map,
            raw_output_references=references,
        )


def test_bundle_builder_does_not_call_normalizers_candidate_builder_or_filesystem(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("parser builder must not call this helper")

    monkeypatch.setattr(booknlp_adapter_contract, "build_booknlp_candidate_drafts", forbidden)
    monkeypatch.setattr(booknlp_adapter_contract, "normalize_booknlp_entity_mentions", forbidden)
    monkeypatch.setattr(booknlp_adapter_contract, "normalize_booknlp_quotes", forbidden)
    monkeypatch.setattr(booknlp_adapter_contract, "normalize_booknlp_events", forbidden)
    monkeypatch.setattr("builtins.open", forbidden)

    bundle = booknlp_fixture_parser.build_booknlp_raw_artifact_bundle_from_fixture_texts(
        fixture_texts(),
        run_manifest=build_storage_manifest(),
        source_map=build_source_map(),
        raw_output_references=adapter_raw_output_references(),
    )
    assert "candidate_records" not in bundle
    assert "candidate_json" not in bundle
    assert "memory_records" not in bundle
    assert "canon_records" not in bundle


def test_raw_output_references_remain_non_canon_non_candidate_and_policy_bound():
    references = adapter_raw_output_references()
    for reference in references:
        validated = evidence.validate_raw_output_reference(reference)
        assert validated["is_canon"] is False
        assert validated["is_candidate"] is False

    manifest = build_storage_manifest(candidate_generation_allowed=True)
    with pytest.raises(ValueError):
        booknlp_fixture_parser.build_booknlp_raw_artifact_bundle_from_fixture_texts(
            fixture_texts(),
            run_manifest=manifest,
            source_map=build_source_map(),
            raw_output_references=references,
        )


def test_parser_stays_separate_from_storage_write_read_list_helpers():
    assert not hasattr(raw_extraction_storage, "write_raw_artifact")
    assert not hasattr(raw_extraction_storage, "read_raw_artifact")
    assert not hasattr(raw_extraction_storage, "list_raw_artifacts")
    assert not hasattr(booknlp_fixture_parser, "write_raw_artifact")
    assert not hasattr(booknlp_fixture_parser, "read_raw_artifact")
    assert not hasattr(booknlp_fixture_parser, "list_raw_artifacts")


def test_future_parser_source_rejects_forbidden_runtime_tool_prose_and_mutation_terms():
    source_path = Path("backend/story_knowledge/booknlp_fixture_parser.py")
    if not source_path.exists():
        return
    source = source_path.read_text(encoding="utf-8")
    violations = [term for term in FORBIDDEN_PRODUCTION_SOURCE_TERMS if term in source]
    assert violations == []
