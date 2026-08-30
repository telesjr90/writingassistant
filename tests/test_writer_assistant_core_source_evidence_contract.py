"""Contract tests for PHASE8-IMPL-006 source-map and evidence helpers.

T003 is tests-first only. The future helper modules are intentionally imported
normally so this targeted file is expected red until T004 creates them:
- backend.story_knowledge.source_map
- backend.story_knowledge.evidence
"""

import inspect
import hashlib

import pytest

from backend.story_knowledge import candidate_record
from backend.story_knowledge import evidence
from backend.story_knowledge import source_map

ALLOWED_SOURCE_DOCUMENT_TYPES = (
    "scene",
    "chapter",
    "note",
    "material",
    "bible",
    "storyform",
    "omi",
    "imported_context",
)

ALLOWED_SEGMENT_TYPES = (
    "document",
    "section",
    "chapter",
    "scene",
    "paragraph",
    "sentence",
    "line",
    "token_window",
    "custom",
)

ALLOWED_LOCATOR_PRECISION_VALUES = (
    "exact",
    "normalized",
    "approximate",
    "document_only",
    "unknown",
)

ALLOWED_EVIDENCE_KINDS = (
    "direct_quote",
    "mention",
    "entity_span",
    "event_span",
    "dialogue_quote",
    "relationship_signal",
    "timeline_signal",
    "conflict_signal",
    "continuity_signal",
    "source_metadata",
    "tool_output_reference",
    "owner_note",
)

ALLOWED_RUN_TYPES = (
    "manual",
    "deterministic_local",
    "booknlp_raw_import",
    "spacy_baseline",
    "mock_fixture",
    "model_assisted_future",
)

ALLOWED_RUN_STATUSES = (
    "planned",
    "running",
    "complete",
    "failed",
    "partial",
    "rejected",
)

ALLOWED_ARTIFACT_KINDS = (
    "booknlp_tokens",
    "booknlp_entities",
    "booknlp_quotes",
    "booknlp_book_json",
    "booknlp_supersense",
    "booknlp_events",
    "spacy_doc",
    "mock_fixture",
    "other_raw_output",
)

SAFE_IDS = ("example", "scene_001", "chapter-001", "source_doc_001")

UNSAFE_IDS = (
    "",
    "   ",
    ".",
    "..",
    "../escape",
    "/absolute",
    "folder/name",
    "folder\\name",
    "C:\\escape",
    "safe/../escape",
)

FORBIDDEN_PATH_FIELDS = (
    "path",
    "absolute_path",
    "external_file_path",
    "training_path",
    "dataset_path",
    "package_path",
    "raw_book_path",
)

FORBIDDEN_MUTATION_FIELDS = (
    "write_to_canon",
    "mutate_memory",
    "apply_promotion",
    "approved_truth",
)

FORBIDDEN_GENERATED_PROSE_FIELDS = (
    "generated_text",
    "model_output",
    "rewritten_text",
    "continuation",
    "draft_prose",
    "generated_summary",
    "generated_outline",
    "rewritten_scene",
    "generated_prose",
)

FORBIDDEN_PROVENANCE_MODEL_FIELDS = (
    "model_prompt",
    "model_output",
    "ollama_request",
    "openai_response",
    "generated_prose",
    "rewritten_text",
    "continuation",
)

FORBIDDEN_DESTINATION_VALUES = (
    "write_to_canon",
    "mutate_memory",
    "apply_promotion",
    "rewrite_scene",
    "generate_prose",
)

FORBIDDEN_SOURCE_TERMS = (
    "booknlp",
    "spacy.load",
    "ollama",
    "openai",
    "requests",
    "httpx",
    "fastapi",
    "uvicorn",
    "subprocess",
    "training",
    "dataset_manifest",
    "jsonl",
    "write_to_canon",
    "mutate_memory",
    "apply_promotion",
    "generated_prose",
    "rewrite",
    "continuation",
    "world_state",
    "truth",
    ".write_text",
    ".mkdir",
    "open(",
)


def build_valid_source_document_ref(**overrides):
    source_document = {
        "project_id": "example",
        "source_document_type": "scene",
        "source_document_id": "scene_001",
        "source_document_version": "1",
        "source_label": "Opening scene",
        "source_path_hint": "Scenes / Opening scene",
        "content_hash": "sha256:source-doc-001",
        "content_hash_algorithm": "sha256",
        "created_at": "2026-06-19T00:00:00Z",
        "updated_at": "2026-06-19T00:00:00Z",
    }
    source_document.update(overrides)
    return source_document


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
        "char_end": 28,
        "byte_start": 0,
        "byte_end": 28,
        "token_start": 0,
        "token_end": 5,
        "text_excerpt": "Owner text marks the source.",
        "excerpt_hash": "sha256:excerpt-001",
    }
    segment.update(overrides)
    return segment


def build_valid_source_map(**overrides):
    source_map_record = {
        "source_map_id": "source_map_001",
        "project_id": "example",
        "source_document": build_valid_source_document_ref(),
        "snapshot_id": "snapshot_001",
        "snapshot_hash": "sha256:snapshot-001",
        "snapshot_hash_algorithm": "sha256",
        "snapshot_created_at": "2026-06-19T00:00:00Z",
        "text_encoding": "utf-8",
        "normalization_policy": "exact_utf8_decoded_snapshot",
        "line_index_available": True,
        "char_offset_policy": "python_string_offsets_half_open",
        "byte_offset_policy": "utf8_byte_offsets_optional",
        "token_offset_policy": "optional_tool_alignment",
        "segments": [build_valid_source_segment()],
    }
    source_map_record.update(overrides)
    return source_map_record


def build_valid_source_locator(**overrides):
    locator = {
        "project_id": "example",
        "source_document_type": "scene",
        "source_document_id": "scene_001",
        "source_document_version": "1",
        "source_map_id": "source_map_001",
        "snapshot_id": "snapshot_001",
        "snapshot_hash": "sha256:snapshot-001",
        "segment_id": "segment_001",
        "section_id": None,
        "chapter_id": "chapter_001",
        "scene_id": "scene_001",
        "paragraph_index": 0,
        "sentence_index": 0,
        "line_start": 1,
        "line_end": 1,
        "char_start": 0,
        "char_end": 28,
        "byte_start": 0,
        "byte_end": 28,
        "token_start": 0,
        "token_end": 5,
        "locator_precision": "exact",
        "source_label": "Opening scene",
        "source_hash": "sha256:source-doc-001",
    }
    locator.update(overrides)
    return locator


def build_valid_evidence_record(**overrides):
    evidence_record = {
        "evidence_id": "evidence_001",
        "project_id": "example",
        "source_locator": build_valid_source_locator(),
        "source_document": build_valid_source_document_ref(),
        "source_map_id": "source_map_001",
        "snapshot_id": "snapshot_001",
        "snapshot_hash": "sha256:snapshot-001",
        "evidence_kind": "mention",
        "claim_supported": "Character name appears in owner-authored source text.",
        "text_excerpt": "Owner text marks the source.",
        "excerpt_hash": "sha256:excerpt-001",
        "char_start": 0,
        "char_end": 28,
        "byte_start": 0,
        "byte_end": 28,
        "token_start": 0,
        "token_end": 5,
        "line_start": 1,
        "line_end": 1,
        "locator_precision": "exact",
        "confidence": 0.75,
        "created_at": "2026-06-19T00:00:00Z",
        "created_by": "manual_contract_fixture",
        "provenance": {
            "run_id": "run_001",
            "created_by": "manual",
            "source_type": "owner_authored",
            "human_review_required": True,
        },
        "notes": "",
    }
    evidence_record.update(overrides)
    return evidence_record


def build_valid_extraction_run_provenance(**overrides):
    run = {
        "run_id": "run_001",
        "project_id": "example",
        "tool_name": "manual",
        "tool_version": "0",
        "adapter_name": "manual_contract_fixture",
        "adapter_version": "0",
        "run_type": "manual",
        "source_documents": [build_valid_source_document_ref()],
        "started_at": "2026-06-19T00:00:00Z",
        "finished_at": "2026-06-19T00:00:01Z",
        "status": "complete",
        "input_snapshot_hashes": ["sha256:snapshot-001"],
        "output_artifact_hashes": [],
        "created_candidate_ids": [],
        "rejected_output_count": 0,
        "insufficient_evidence_count": 0,
        "warnings": [],
        "parameters": {},
        "environment": {},
        "human_review_required": True,
    }
    run.update(overrides)
    return run


def build_valid_raw_output_reference(**overrides):
    reference = {
        "raw_output_id": "raw_output_001",
        "project_id": "example",
        "tool_name": "booknlp",
        "run_id": "run_001",
        "artifact_name": "output.tokens",
        "artifact_kind": "booknlp_tokens",
        "artifact_path_hint": "writer_assistant/extractions/booknlp/run_001/raw/output.tokens",
        "artifact_hash": "sha256:artifact-001",
        "artifact_hash_algorithm": "sha256",
        "created_at": "2026-06-19T00:00:00Z",
        "source_snapshot_hashes": ["sha256:snapshot-001"],
        "is_canon": False,
        "is_candidate": False,
    }
    reference.update(overrides)
    return reference


def build_existing_candidate_fixture(**overrides):
    candidate = {
        "candidate_id": "candidate_001",
        "project_id": "example",
        "candidate_type": "annotation_candidate",
        "status": "candidate",
        "target_category": "annotations_evidence_provenance",
        "source_locator": {
            "project_id": "example",
            "source_document_type": "scene",
            "source_document_id": "scene_001",
            "section_id": None,
            "chapter_id": "chapter_001",
            "scene_id": "scene_001",
            "line_start": 1,
            "line_end": 1,
            "char_start": 0,
            "char_end": 28,
            "source_hash": "sha256:source-doc-001",
        },
        "evidence": [
            {
                "evidence_id": "evidence_001",
                "source_locator": {
                    "project_id": "example",
                    "source_document_type": "scene",
                    "source_document_id": "scene_001",
                    "section_id": None,
                    "chapter_id": "chapter_001",
                    "scene_id": "scene_001",
                    "line_start": 1,
                    "line_end": 1,
                    "char_start": 0,
                    "char_end": 28,
                    "source_hash": "sha256:source-doc-001",
                },
                "source_text_excerpt": "Owner text marks the source.",
                "summary": "",
                "supports_claim": "Evidence is source-derived.",
                "confidence": 0.75,
                "notes": "",
            }
        ],
        "provenance": {
            "origin": "manual",
            "extraction_method": "owner_review_contract_fixture",
            "timestamp": "2026-06-19T00:00:00Z",
            "human_review_required": True,
            "source_hash": "sha256:source-doc-001",
            "snapshot_hash": "sha256:snapshot-001",
            "owner_reviewed": False,
        },
        "owner_decision": "undecided",
        "destination": "omi_candidate_only",
        "confidence": 0.75,
        "created_at": "2026-06-19T00:00:00Z",
        "updated_at": "2026-06-19T00:00:00Z",
    }
    candidate.update(overrides)
    return candidate


def assert_accepts(validator, payload):
    validated = validator(payload)
    assert isinstance(validated, dict)
    assert validated == payload


def assert_rejects(validator, payload):
    with pytest.raises(ValueError):
        validator(payload)


def remove_field(payload, field):
    copy = dict(payload)
    del copy[field]
    return copy


def with_extra(payload, field, value=True):
    copy = dict(payload)
    copy[field] = value
    return copy


def assert_missing_fields_rejected(validator, builder, required_fields):
    for field in required_fields:
        assert_rejects(validator, remove_field(builder(), field))


def assert_forbidden_fields_rejected(validator, builder, fields):
    for field in fields:
        assert_rejects(validator, with_extra(builder(), field, True))


def assert_unsafe_ids_rejected(validator, builder, id_field):
    for unsafe_id in UNSAFE_IDS:
        assert_rejects(validator, builder(**{id_field: unsafe_id}))


def assert_offset_pair_rejected(validator, builder, start_field, end_field):
    assert_rejects(validator, builder(**{start_field: -1}))
    assert_rejects(validator, builder(**{end_field: -1}))
    assert_rejects(validator, builder(**{start_field: True}))
    assert_rejects(validator, builder(**{end_field: False}))
    assert_accepts(validator, builder(**{start_field: 5, end_field: 5}))
    assert_rejects(validator, builder(**{start_field: 6, end_field: 5}))


def build_t002_exact_snapshot(text="A café 雨.\n"):
    return source_map.build_exact_source_snapshot(
        project_id="example",
        source_document_type="scene",
        source_document_id="scene_001",
        source_document_version="1",
        source_ownership="owner_authored",
        source_content=text,
        source_map_id="source_map_001",
        chapter_id="chapter_001",
        scene_id="scene_001",
    )


def test_t002_source_identity_is_stable_hierarchical_and_path_independent():
    first = build_t002_exact_snapshot()
    second = build_t002_exact_snapshot()
    assert first.identity == second.identity
    assert first.identity.project_id == "example"
    assert first.identity.source_document_id == "scene_001"
    assert first.identity.chapter_id == "chapter_001"
    assert first.identity.scene_id == "scene_001"
    assert first.identity.snapshot_id == second.identity.snapshot_id
    assert "path" not in first.identity.to_json().casefold()


def test_t002_source_identity_enforces_shared_deterministic_snapshot_id():
    snapshot = build_t002_exact_snapshot()
    identity = snapshot.identity
    derivation_fields = {
        "contract_version": identity.contract_version,
        "project_id": identity.project_id,
        "source_document_type": identity.source_document_type,
        "source_document_id": identity.source_document_id,
        "source_document_version": identity.source_document_version,
        "source_ownership": identity.source_ownership,
        "section_id": identity.section_id,
        "chapter_id": identity.chapter_id,
        "scene_id": identity.scene_id,
        "content_hash": identity.content_hash,
        "hash_algorithm": identity.hash_algorithm,
        "hash_basis": identity.hash_basis,
    }
    derived_id = source_map.derive_source_snapshot_id(**derivation_fields)
    direct = source_map.SourceIdentity(
        **derivation_fields,
        snapshot_id=derived_id,
        source_map_id=identity.source_map_id,
    )

    assert direct == identity
    assert tuple(inspect.signature(source_map.derive_source_snapshot_id).parameters) == tuple(
        derivation_fields
    )
    assert source_map.SourceIdentity(
        **derivation_fields,
        snapshot_id=derived_id,
        source_map_id="different-display-map",
    ).snapshot_id == derived_id
    with pytest.raises(source_map.SourceIdentityValidationError, match="deterministic"):
        source_map.SourceIdentity(
            **derivation_fields,
            snapshot_id="snapshot-arbitrary-safe-id",
        )


def test_t002_optional_source_hierarchy_and_closed_ownership_type_contract():
    snapshot = source_map.build_exact_source_snapshot(
        project_id="example",
        source_document_type="note",
        source_document_id="note_001",
        source_document_version="1",
        source_ownership="owner_selected_imported",
        source_content="Exact imported owner selection.",
    )
    assert snapshot.identity.chapter_id is None
    assert snapshot.identity.scene_id is None
    assert snapshot.identity.source_ownership.value == "owner_selected_imported"
    with pytest.raises(source_map.SourceIdentityValidationError):
        build_t002_exact_snapshot().__class__(
            identity=source_map.SourceIdentity(
                project_id="example",
                source_document_type="scene",
                source_document_id="scene_001",
                source_document_version="1",
                source_ownership="external_truth",
                snapshot_id="snapshot-safe",
                content_hash="0" * 64,
            ),
            source_content="",
        )


@pytest.mark.parametrize("unsafe_id", UNSAFE_IDS)
def test_t002_source_identity_rejects_unsafe_ids(unsafe_id):
    with pytest.raises(source_map.SourceIdentityValidationError):
        source_map.build_exact_source_snapshot(
            project_id=unsafe_id,
            source_document_type="scene",
            source_document_id="scene_001",
            source_document_version="1",
            source_ownership="owner_authored",
            source_content="Exact.",
        )


def test_t002_exact_snapshot_hash_preserves_content_bytes_and_line_endings():
    lf = build_t002_exact_snapshot("first\nsecond")
    crlf = build_t002_exact_snapshot("first\r\nsecond")
    changed = build_t002_exact_snapshot("first\nchanged")
    assert lf.identity.content_hash == hashlib.sha256(b"first\nsecond").hexdigest()
    assert lf.identity.snapshot_id != crlf.identity.snapshot_id
    assert lf.identity.content_hash != crlf.identity.content_hash
    assert lf.identity.snapshot_id != changed.identity.snapshot_id


def test_t002_ascii_and_multibyte_offset_translation_is_exact():
    ascii_snapshot = build_t002_exact_snapshot("alpha beta")
    ascii_chars = source_map.OffsetRange(6, 10, source_map.CHAR_OFFSET_BASIS)
    assert source_map.translate_exact_offset_range(
        ascii_snapshot,
        ascii_chars,
        target_basis=source_map.BYTE_OFFSET_BASIS,
    ) == source_map.OffsetRange(6, 10, source_map.BYTE_OFFSET_BASIS)

    multibyte = build_t002_exact_snapshot("A café 雨.")
    character_range = source_map.OffsetRange(2, 8, source_map.CHAR_OFFSET_BASIS)
    byte_range = source_map.translate_exact_offset_range(
        multibyte,
        character_range,
        target_basis=source_map.BYTE_OFFSET_BASIS,
        expected_snapshot_id=multibyte.identity.snapshot_id,
        expected_content_hash=multibyte.identity.content_hash,
    )
    assert byte_range == source_map.OffsetRange(2, 11, source_map.BYTE_OFFSET_BASIS)
    assert source_map.translate_exact_offset_range(
        multibyte,
        byte_range,
        target_basis=source_map.CHAR_OFFSET_BASIS,
    ) == character_range


def test_t002_offset_translation_rejects_split_codepoints_and_snapshot_mismatch():
    snapshot = build_t002_exact_snapshot("é")
    with pytest.raises(source_map.SourceIdentityValidationError, match="splits"):
        source_map.translate_exact_offset_range(
            snapshot,
            source_map.OffsetRange(0, 1, source_map.BYTE_OFFSET_BASIS),
            target_basis=source_map.CHAR_OFFSET_BASIS,
        )
    with pytest.raises(source_map.SourceIdentityValidationError, match="identity mismatch"):
        source_map.translate_exact_offset_range(
            snapshot,
            source_map.OffsetRange(0, 1, source_map.CHAR_OFFSET_BASIS),
            target_basis=source_map.BYTE_OFFSET_BASIS,
            expected_snapshot_id="snapshot-other",
        )
    with pytest.raises(source_map.SourceIdentityValidationError, match="hash mismatch"):
        source_map.translate_exact_offset_range(
            snapshot,
            source_map.OffsetRange(0, 1, source_map.CHAR_OFFSET_BASIS),
            target_basis=source_map.BYTE_OFFSET_BASIS,
            expected_content_hash="0" * 64,
        )


def test_t002_offset_availability_and_basis_are_explicit_without_token_fabrication():
    snapshot = build_t002_exact_snapshot()
    offsets = snapshot.to_dict()["offsets"]
    assert offsets["character"] == {
        "available": True,
        "basis": source_map.CHAR_OFFSET_BASIS,
    }
    assert offsets["byte"] == {
        "available": True,
        "basis": source_map.BYTE_OFFSET_BASIS,
    }
    assert offsets["line"] == {"available": False, "basis": None}
    assert offsets["token"] == {"available": False, "basis": None}


def test_t002_canonical_locator_keeps_char_and_byte_bases_distinct():
    snapshot = build_t002_exact_snapshot("A café 雨.")
    char_range = source_map.OffsetRange(2, 8, source_map.CHAR_OFFSET_BASIS)
    byte_range = source_map.translate_exact_offset_range(
        snapshot,
        char_range,
        target_basis=source_map.BYTE_OFFSET_BASIS,
    )
    locator = source_map.build_canonical_source_locator(
        snapshot.identity,
        character_range=char_range,
        byte_range=byte_range,
        exact_snapshot=snapshot,
    )
    assert (locator["char_start"], locator["char_end"]) == (2, 8)
    assert (locator["byte_start"], locator["byte_end"]) == (2, 11)
    assert locator["char_offset_basis"] == source_map.CHAR_OFFSET_BASIS
    assert locator["byte_offset_basis"] == source_map.BYTE_OFFSET_BASIS


def test_t002_canonical_locator_rejects_unproved_or_mismatched_dual_ranges():
    snapshot = build_t002_exact_snapshot("A café 雨.")
    character_range = source_map.OffsetRange(2, 8, source_map.CHAR_OFFSET_BASIS)
    byte_range = source_map.OffsetRange(2, 11, source_map.BYTE_OFFSET_BASIS)
    with pytest.raises(source_map.SourceIdentityValidationError, match="exact snapshot"):
        source_map.build_canonical_source_locator(
            snapshot.identity,
            character_range=character_range,
            byte_range=byte_range,
        )
    with pytest.raises(source_map.SourceIdentityValidationError, match="same exact span"):
        source_map.build_canonical_source_locator(
            snapshot.identity,
            character_range=character_range,
            byte_range=source_map.OffsetRange(2, 10, source_map.BYTE_OFFSET_BASIS),
            exact_snapshot=snapshot,
        )


def test_t002_canonical_locator_accepts_explicit_story_check_byte_only_basis():
    snapshot = build_t002_exact_snapshot("A café 雨.")
    locator = source_map.build_canonical_source_locator(
        snapshot.identity,
        byte_range=source_map.OffsetRange(2, 11, source_map.BYTE_OFFSET_BASIS),
    )
    assert locator["char_start"] is None
    assert locator["byte_offset_basis"] == source_map.BYTE_OFFSET_BASIS
    assert source_map.validate_canonical_source_locator(locator) == locator

    without_basis = dict(locator)
    without_basis["byte_offset_basis"] = None
    with pytest.raises(ValueError, match="byte_offset_basis"):
        source_map.validate_canonical_source_locator(without_basis)


def test_t002_canonical_exact_locator_enforces_sha256_hash_consistency():
    snapshot = build_t002_exact_snapshot("A café 雨.")
    locator = source_map.build_canonical_source_locator(
        snapshot.identity,
        byte_range=source_map.OffsetRange(2, 11, source_map.BYTE_OFFSET_BASIS),
    )
    assert source_map.validate_canonical_source_locator(locator) == locator

    for field in ("snapshot_hash", "source_hash"):
        malformed = dict(locator)
        malformed[field] = "not-a-lowercase-sha256"
        with pytest.raises(ValueError, match=field):
            source_map.validate_canonical_source_locator(malformed)

    mismatch = dict(locator)
    mismatch["source_hash"] = "0" * 64
    with pytest.raises(ValueError, match="must match"):
        source_map.validate_canonical_source_locator(mismatch)

    legacy_locator = build_valid_source_locator()
    assert source_map.validate_source_locator(legacy_locator) == legacy_locator


def test_source_document_ref_accepts_valid_fixture():
    assert_accepts(
        source_map.validate_source_document_ref,
        build_valid_source_document_ref(),
    )


def test_source_document_ref_rejects_missing_required_fields():
    required = (
        "project_id",
        "source_document_type",
        "source_document_id",
        "source_document_version",
        "source_label",
        "source_path_hint",
        "content_hash",
        "content_hash_algorithm",
        "created_at",
        "updated_at",
    )
    assert_missing_fields_rejected(
        source_map.validate_source_document_ref,
        build_valid_source_document_ref,
        required,
    )


@pytest.mark.parametrize("source_document_type", ALLOWED_SOURCE_DOCUMENT_TYPES)
def test_source_document_ref_accepts_allowed_document_types(source_document_type):
    assert_accepts(
        source_map.validate_source_document_ref,
        build_valid_source_document_ref(source_document_type=source_document_type),
    )


def test_source_document_ref_rejects_unknown_document_type():
    assert_rejects(
        source_map.validate_source_document_ref,
        build_valid_source_document_ref(source_document_type="external_book"),
    )


def test_source_document_ref_rejects_unsafe_project_and_source_ids():
    assert_unsafe_ids_rejected(
        source_map.validate_source_document_ref,
        build_valid_source_document_ref,
        "project_id",
    )
    assert_unsafe_ids_rejected(
        source_map.validate_source_document_ref,
        build_valid_source_document_ref,
        "source_document_id",
    )
    for safe_id in SAFE_IDS:
        assert_accepts(
            source_map.validate_source_document_ref,
            build_valid_source_document_ref(source_document_id=safe_id),
        )


def test_source_document_ref_treats_path_hint_as_display_metadata_only():
    assert_accepts(
        source_map.validate_source_document_ref,
        build_valid_source_document_ref(source_path_hint="Scene list / Opening"),
    )
    assert_rejects(
        source_map.validate_source_document_ref,
        build_valid_source_document_ref(source_path_hint="/absolute/source.txt"),
    )
    assert_rejects(
        source_map.validate_source_document_ref,
        build_valid_source_document_ref(source_path_hint="../outside/source.txt"),
    )


def test_source_document_ref_rejects_path_and_mutation_fields():
    assert_forbidden_fields_rejected(
        source_map.validate_source_document_ref,
        build_valid_source_document_ref,
        FORBIDDEN_PATH_FIELDS + FORBIDDEN_MUTATION_FIELDS,
    )


def test_source_segment_accepts_valid_fixture():
    assert_accepts(source_map.validate_source_segment, build_valid_source_segment())


def test_source_segment_rejects_missing_required_fields():
    required = (
        "segment_id",
        "segment_type",
        "segment_index",
        "section_id",
        "chapter_id",
        "scene_id",
        "paragraph_index",
        "sentence_index",
        "line_start",
        "line_end",
        "char_start",
        "char_end",
        "byte_start",
        "byte_end",
        "token_start",
        "token_end",
        "text_excerpt",
        "excerpt_hash",
    )
    assert_missing_fields_rejected(
        source_map.validate_source_segment,
        build_valid_source_segment,
        required,
    )


@pytest.mark.parametrize("segment_type", ALLOWED_SEGMENT_TYPES)
def test_source_segment_accepts_allowed_segment_types(segment_type):
    assert_accepts(
        source_map.validate_source_segment,
        build_valid_source_segment(segment_type=segment_type),
    )


def test_source_segment_rejects_unknown_segment_type():
    assert_rejects(
        source_map.validate_source_segment,
        build_valid_source_segment(segment_type="generated_summary"),
    )


def test_source_segment_enforces_half_open_offset_rules():
    for start_field, end_field in (
        ("line_start", "line_end"),
        ("char_start", "char_end"),
        ("byte_start", "byte_end"),
        ("token_start", "token_end"),
    ):
        assert_offset_pair_rejected(
            source_map.validate_source_segment,
            build_valid_source_segment,
            start_field,
            end_field,
        )


def test_source_segment_allows_none_offsets_but_rejects_bad_excerpt_and_prose_fields():
    assert_accepts(
        source_map.validate_source_segment,
        build_valid_source_segment(char_start=None, char_end=None),
    )
    assert_rejects(
        source_map.validate_source_segment,
        build_valid_source_segment(text_excerpt=123),
    )
    assert_forbidden_fields_rejected(
        source_map.validate_source_segment,
        build_valid_source_segment,
        FORBIDDEN_GENERATED_PROSE_FIELDS,
    )


def test_source_map_accepts_valid_fixture():
    assert_accepts(source_map.validate_source_map, build_valid_source_map())


def test_source_map_rejects_missing_required_fields():
    required = (
        "source_map_id",
        "project_id",
        "source_document",
        "snapshot_id",
        "snapshot_hash",
        "snapshot_hash_algorithm",
        "snapshot_created_at",
        "text_encoding",
        "normalization_policy",
        "line_index_available",
        "char_offset_policy",
        "byte_offset_policy",
        "token_offset_policy",
        "segments",
    )
    assert_missing_fields_rejected(
        source_map.validate_source_map,
        build_valid_source_map,
        required,
    )


def test_source_map_validates_nested_source_document_and_segments():
    invalid_document = build_valid_source_document_ref(source_document_type="dataset")
    assert_rejects(
        source_map.validate_source_map,
        build_valid_source_map(source_document=invalid_document),
    )
    assert_rejects(
        source_map.validate_source_map,
        build_valid_source_map(segments="not-a-list"),
    )
    assert_rejects(source_map.validate_source_map, build_valid_source_map(segments=[]))
    assert_rejects(
        source_map.validate_source_map,
        build_valid_source_map(segments=[build_valid_source_segment(char_start=-1)]),
    )


def test_source_map_rejects_unsafe_ids_and_non_bool_line_index_flag():
    for field in ("source_map_id", "project_id", "snapshot_id"):
        assert_unsafe_ids_rejected(source_map.validate_source_map, build_valid_source_map, field)
    assert_rejects(
        source_map.validate_source_map,
        build_valid_source_map(line_index_available="yes"),
    )


def test_source_map_rejects_canon_mutation_and_generated_prose_fields():
    source_map_forbidden = (
        "canon",
        "approved_truth",
        "memory_path",
        "write_to_canon",
        "mutate_memory",
        "apply_promotion",
        "generated_summary",
        "generated_outline",
        "rewritten_scene",
        "continuation",
    )
    assert_forbidden_fields_rejected(
        source_map.validate_source_map,
        build_valid_source_map,
        source_map_forbidden,
    )


def test_source_locator_accepts_valid_fixture():
    assert_accepts(source_map.validate_source_locator, build_valid_source_locator())


def test_source_locator_rejects_missing_core_required_fields():
    required = (
        "project_id",
        "source_document_type",
        "source_document_id",
        "locator_precision",
    )
    assert_missing_fields_rejected(
        source_map.validate_source_locator,
        build_valid_source_locator,
        required,
    )


@pytest.mark.parametrize("locator_precision", ALLOWED_LOCATOR_PRECISION_VALUES)
def test_source_locator_accepts_allowed_precision_values(locator_precision):
    locator = build_valid_source_locator(locator_precision=locator_precision)
    if locator_precision in ("document_only", "unknown"):
        locator["char_start"] = None
        locator["char_end"] = None
    assert_accepts(source_map.validate_source_locator, locator)


def test_source_locator_rejects_unknown_precision_and_source_type():
    assert_rejects(
        source_map.validate_source_locator,
        build_valid_source_locator(locator_precision="guessed"),
    )
    assert_rejects(
        source_map.validate_source_locator,
        build_valid_source_locator(source_document_type="training"),
    )


def test_source_locator_rejects_unsafe_ids_paths_generated_text_and_mutation_fields():
    assert_unsafe_ids_rejected(
        source_map.validate_source_locator,
        build_valid_source_locator,
        "project_id",
    )
    assert_unsafe_ids_rejected(
        source_map.validate_source_locator,
        build_valid_source_locator,
        "source_document_id",
    )
    assert_forbidden_fields_rejected(
        source_map.validate_source_locator,
        build_valid_source_locator,
        FORBIDDEN_PATH_FIELDS + FORBIDDEN_GENERATED_PROSE_FIELDS + FORBIDDEN_MUTATION_FIELDS,
    )


def test_source_locator_enforces_offsets_and_first_slice_char_offsets():
    for start_field, end_field in (
        ("line_start", "line_end"),
        ("char_start", "char_end"),
        ("byte_start", "byte_end"),
        ("token_start", "token_end"),
    ):
        assert_offset_pair_rejected(
            source_map.validate_source_locator,
            build_valid_source_locator,
            start_field,
            end_field,
        )
    assert_rejects(
        source_map.validate_source_locator,
        build_valid_source_locator(char_start=None, char_end=None, locator_precision="exact"),
    )
    assert_accepts(
        source_map.validate_source_locator,
        build_valid_source_locator(
            char_start=None,
            char_end=None,
            locator_precision="document_only",
        ),
    )


def test_evidence_record_accepts_valid_fixture():
    assert_accepts(evidence.validate_evidence_record, build_valid_evidence_record())


def test_evidence_record_rejects_missing_required_fields():
    required = (
        "evidence_id",
        "project_id",
        "source_locator",
        "source_document",
        "source_map_id",
        "snapshot_id",
        "snapshot_hash",
        "evidence_kind",
        "claim_supported",
        "text_excerpt",
        "excerpt_hash",
        "char_start",
        "char_end",
        "byte_start",
        "byte_end",
        "token_start",
        "token_end",
        "line_start",
        "line_end",
        "locator_precision",
        "confidence",
        "created_at",
        "created_by",
        "provenance",
        "notes",
    )
    assert_missing_fields_rejected(
        evidence.validate_evidence_record,
        build_valid_evidence_record,
        required,
    )


@pytest.mark.parametrize("evidence_kind", ALLOWED_EVIDENCE_KINDS)
def test_evidence_record_accepts_allowed_kinds(evidence_kind):
    assert_accepts(
        evidence.validate_evidence_record,
        build_valid_evidence_record(evidence_kind=evidence_kind),
    )


def test_evidence_record_rejects_unknown_kind_and_invalid_nested_records():
    assert_rejects(
        evidence.validate_evidence_record,
        build_valid_evidence_record(evidence_kind="story_truth"),
    )
    assert_rejects(
        evidence.validate_evidence_record,
        build_valid_evidence_record(
            source_locator=build_valid_source_locator(locator_precision="guessed")
        ),
    )
    assert_rejects(
        evidence.validate_evidence_record,
        build_valid_evidence_record(
            source_document=build_valid_source_document_ref(source_document_type="training")
        ),
    )


def test_evidence_record_enforces_confidence_claim_and_provenance_boundaries():
    for confidence in (0.0, 1.0):
        assert_accepts(
            evidence.validate_evidence_record,
            build_valid_evidence_record(confidence=confidence),
        )
    for confidence in (-0.01, 1.01, True, "high"):
        assert_rejects(
            evidence.validate_evidence_record,
            build_valid_evidence_record(confidence=confidence),
        )
    assert_rejects(
        evidence.validate_evidence_record,
        build_valid_evidence_record(claim_supported=["not", "a", "string"]),
    )
    assert_rejects(
        evidence.validate_evidence_record,
        build_valid_evidence_record(
            provenance={
                "created_by": "model",
                "human_review_required": True,
                "model_prompt": "forbidden",
            }
        ),
    )


def test_evidence_record_rejects_generated_prose_and_mutation_fields():
    assert_forbidden_fields_rejected(
        evidence.validate_evidence_record,
        build_valid_evidence_record,
        FORBIDDEN_GENERATED_PROSE_FIELDS + FORBIDDEN_MUTATION_FIELDS,
    )


def test_extraction_run_provenance_accepts_valid_fixture():
    assert_accepts(
        evidence.validate_extraction_run_provenance,
        build_valid_extraction_run_provenance(),
    )


def test_extraction_run_provenance_rejects_missing_required_fields():
    required = (
        "run_id",
        "project_id",
        "tool_name",
        "tool_version",
        "adapter_name",
        "adapter_version",
        "run_type",
        "source_documents",
        "started_at",
        "finished_at",
        "status",
        "input_snapshot_hashes",
        "output_artifact_hashes",
        "created_candidate_ids",
        "rejected_output_count",
        "insufficient_evidence_count",
        "warnings",
        "parameters",
        "environment",
        "human_review_required",
    )
    assert_missing_fields_rejected(
        evidence.validate_extraction_run_provenance,
        build_valid_extraction_run_provenance,
        required,
    )


@pytest.mark.parametrize("run_type", ALLOWED_RUN_TYPES)
def test_extraction_run_provenance_accepts_allowed_run_types(run_type):
    assert_accepts(
        evidence.validate_extraction_run_provenance,
        build_valid_extraction_run_provenance(run_type=run_type),
    )


@pytest.mark.parametrize("status", ALLOWED_RUN_STATUSES)
def test_extraction_run_provenance_accepts_allowed_statuses(status):
    assert_accepts(
        evidence.validate_extraction_run_provenance,
        build_valid_extraction_run_provenance(status=status),
    )


def test_extraction_run_provenance_rejects_invalid_shapes_counts_and_forbidden_fields():
    assert_rejects(
        evidence.validate_extraction_run_provenance,
        build_valid_extraction_run_provenance(run_type="live_model_call"),
    )
    assert_rejects(
        evidence.validate_extraction_run_provenance,
        build_valid_extraction_run_provenance(status="promoted"),
    )
    assert_rejects(
        evidence.validate_extraction_run_provenance,
        build_valid_extraction_run_provenance(human_review_required="yes"),
    )
    assert_rejects(
        evidence.validate_extraction_run_provenance,
        build_valid_extraction_run_provenance(source_documents="scene_001"),
    )
    assert_rejects(
        evidence.validate_extraction_run_provenance,
        build_valid_extraction_run_provenance(
            source_documents=[build_valid_source_document_ref(source_document_type="dataset")]
        ),
    )
    assert_rejects(
        evidence.validate_extraction_run_provenance,
        build_valid_extraction_run_provenance(created_candidate_ids="candidate_001"),
    )
    for count_field in ("rejected_output_count", "insufficient_evidence_count"):
        assert_rejects(
            evidence.validate_extraction_run_provenance,
            build_valid_extraction_run_provenance(**{count_field: -1}),
        )
        assert_rejects(
            evidence.validate_extraction_run_provenance,
            build_valid_extraction_run_provenance(**{count_field: True}),
        )
    assert_forbidden_fields_rejected(
        evidence.validate_extraction_run_provenance,
        build_valid_extraction_run_provenance,
        FORBIDDEN_PROVENANCE_MODEL_FIELDS + ("write_to_canon", "mutate_memory", "apply_promotion"),
    )


def test_extraction_run_provenance_model_assisted_future_is_structural_only():
    assert_accepts(
        evidence.validate_extraction_run_provenance,
        build_valid_extraction_run_provenance(run_type="model_assisted_future"),
    )
    assert_rejects(
        evidence.validate_extraction_run_provenance,
        build_valid_extraction_run_provenance(
            run_type="model_assisted_future",
            model_prompt="forbidden",
        ),
    )


def test_raw_output_reference_accepts_valid_fixture():
    assert_accepts(evidence.validate_raw_output_reference, build_valid_raw_output_reference())


def test_raw_output_reference_rejects_missing_required_fields():
    required = (
        "raw_output_id",
        "project_id",
        "tool_name",
        "run_id",
        "artifact_name",
        "artifact_kind",
        "artifact_path_hint",
        "artifact_hash",
        "artifact_hash_algorithm",
        "created_at",
        "source_snapshot_hashes",
        "is_canon",
        "is_candidate",
    )
    assert_missing_fields_rejected(
        evidence.validate_raw_output_reference,
        build_valid_raw_output_reference,
        required,
    )


@pytest.mark.parametrize("artifact_kind", ALLOWED_ARTIFACT_KINDS)
def test_raw_output_reference_accepts_allowed_artifact_kinds(artifact_kind):
    assert_accepts(
        evidence.validate_raw_output_reference,
        build_valid_raw_output_reference(artifact_kind=artifact_kind),
    )


def test_raw_output_reference_rejects_unknown_artifact_kind_and_canon_candidate_flags():
    assert_rejects(
        evidence.validate_raw_output_reference,
        build_valid_raw_output_reference(artifact_kind="approved_truth"),
    )
    assert_rejects(
        evidence.validate_raw_output_reference,
        build_valid_raw_output_reference(is_canon=True),
    )
    assert_rejects(
        evidence.validate_raw_output_reference,
        build_valid_raw_output_reference(is_candidate=True),
    )


def test_raw_output_reference_path_hint_is_debug_only_and_rejects_forbidden_fields():
    assert_accepts(
        evidence.validate_raw_output_reference,
        build_valid_raw_output_reference(
            artifact_path_hint="writer_assistant/extractions/booknlp/run_001/raw/output.tokens"
        ),
    )
    assert_rejects(
        evidence.validate_raw_output_reference,
        build_valid_raw_output_reference(artifact_path_hint="/absolute/output.tokens"),
    )
    assert_rejects(
        evidence.validate_raw_output_reference,
        build_valid_raw_output_reference(artifact_path_hint="../training/output.tokens"),
    )
    assert_forbidden_fields_rejected(
        evidence.validate_raw_output_reference,
        build_valid_raw_output_reference,
        FORBIDDEN_PATH_FIELDS + FORBIDDEN_MUTATION_FIELDS,
    )


@pytest.mark.parametrize(
    "artifact_kind",
    (
        "booknlp_tokens",
        "booknlp_entities",
        "booknlp_quotes",
        "booknlp_book_json",
        "booknlp_supersense",
        "booknlp_events",
    ),
)
def test_booknlp_ready_raw_artifacts_are_references_only(artifact_kind):
    reference = build_valid_raw_output_reference(
        artifact_kind=artifact_kind,
        source_snapshot_hashes=["sha256:snapshot-001"],
        is_canon=False,
        is_candidate=False,
    )
    assert_accepts(evidence.validate_raw_output_reference, reference)
    assert_rejects(
        evidence.validate_raw_output_reference,
        with_extra(reference, "write_to_canon", True),
    )
    assert_rejects(
        evidence.validate_raw_output_reference,
        with_extra(reference, "generated_prose", "forbidden"),
    )


def test_existing_candidate_validation_accepts_evidence_backed_candidate_fixture():
    validated = candidate_record.validate_candidate_record(build_existing_candidate_fixture())
    assert validated["status"] == "candidate"
    assert validated["destination"] == "omi_candidate_only"
    assert validated["provenance"]["human_review_required"] is True


def test_existing_candidate_validation_keeps_approval_and_confidence_candidate_only():
    candidate = build_existing_candidate_fixture(
        status="approved",
        owner_decision="approve",
        confidence=1.0,
        destination="project_memory_candidate",
    )
    validated = candidate_record.validate_candidate_record(candidate)
    assert validated["status"] == "approved"
    assert validated["confidence"] == 1.0
    assert "write_to_canon" not in validated
    assert "mutate_memory" not in validated
    assert "apply_promotion" not in validated


@pytest.mark.parametrize("destination", FORBIDDEN_DESTINATION_VALUES)
def test_existing_candidate_validation_rejects_forbidden_destinations(destination):
    assert_rejects(
        candidate_record.validate_candidate_record,
        build_existing_candidate_fixture(destination=destination),
    )


def test_future_candidate_schema_extension_is_limited_to_source_evidence_helpers():
    # Current candidate_record validation intentionally accepts the older embedded
    # evidence shape. T004 may extend source/evidence helpers without changing
    # candidate schema in this T003 tests-first task.
    full_future_evidence = build_valid_evidence_record()
    assert "source_document" in full_future_evidence
    assert "locator_precision" in full_future_evidence


def test_future_source_map_and_evidence_modules_do_not_gain_runtime_dependencies():
    for module in (source_map, evidence):
        module_source = inspect.getsource(module)
        lowered = module_source.lower()
        for forbidden in FORBIDDEN_SOURCE_TERMS:
            assert forbidden.lower() not in lowered
