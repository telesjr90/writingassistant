"""Contract tests for future Writer Assistant Core candidate list helper.

T006 is expected to implement `list_candidate_records` on
`backend.story_knowledge.candidate_persistence`.

Index read/write remains deferred to a later parent per T002 decision.
T005 is list-only despite the child label mentioning list/index.
"""

import inspect
import json
from pathlib import Path

import pytest

from backend.story_knowledge import candidate_persistence
from backend.story_knowledge import candidate_record
from backend.story_knowledge import candidate_storage

FORBIDDEN_SOURCE_TERMS = (
    "ollama",
    "openai",
    "requests",
    "httpx",
    "analysis_engine",
    "story_check",
    "spacy",
    "gliner",
    "booknlp",
    "frontend",
    "fastapi",
    "apirouter",
    "training",
    "dataset",
    "apply_promotion",
    "write_to_canon",
    "mutate_memory",
    "rewrite_scene",
)


# ---------------------------------------------------------------------------
# Fixture builders
# ---------------------------------------------------------------------------


def build_valid_source_locator(document_id="scene_001", **overrides):
    locator = {
        "project_id": "example",
        "source_document_type": "scene",
        "source_document_id": document_id,
        "section_id": None,
        "chapter_id": None,
        "scene_id": document_id,
        "line_start": None,
        "line_end": None,
        "char_start": None,
        "char_end": None,
        "source_hash": None,
    }
    locator.update(overrides)
    return locator


def build_valid_evidence_item(document_id="scene_001", **overrides):
    item = {
        "evidence_id": "evidence_001",
        "source_locator": build_valid_source_locator(document_id=document_id),
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
        "origin": "manual",
        "extraction_method": "owner_entry",
        "timestamp": "2026-06-16T00:00:00Z",
        "human_review_required": True,
    }
    provenance.update(overrides)
    return provenance


def build_valid_candidate_record(
    candidate_id="core_candidate_scene_001_character_001",
    document_id="scene_001",
    **overrides,
):
    record = {
        "candidate_id": candidate_id,
        "project_id": "example",
        "candidate_type": "character_candidate",
        "status": "candidate",
        "target_category": "characters",
        "source_locator": build_valid_source_locator(document_id=document_id),
        "evidence": [],
        "provenance": build_valid_provenance(),
        "owner_decision": "undecided",
        "destination": "omi_candidate_only",
        "confidence": 0.0,
        "created_at": "2026-06-16T00:00:00Z",
        "updated_at": "2026-06-16T00:00:00Z",
    }
    record.update(overrides)
    return record


def project_dir(tmp_path: Path) -> Path:
    return tmp_path / "my-project"


def candidates_dir(project: Path) -> Path:
    return project / "writer_assistant" / "candidates"


def index_path(project: Path) -> Path:
    return project / "writer_assistant" / "index.json"


def write_raw_candidate(project: Path, record: dict) -> Path:
    candidate_record.validate_candidate_record(record)
    candidate_path = candidate_storage.candidate_record_path(
        project, record["candidate_id"]
    )
    candidate_path.parent.mkdir(parents=True, exist_ok=True)
    candidate_path.write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return candidate_path


# ---------------------------------------------------------------------------
# Missing / empty directory contract
# ---------------------------------------------------------------------------


def test_list_missing_candidate_directory_returns_empty_without_side_effects(tmp_path):
    project = project_dir(tmp_path)
    result = candidate_persistence.list_candidate_records(project)

    assert result == []
    assert not (project / "writer_assistant").exists()
    assert not index_path(project).exists()


def test_list_empty_candidate_directory_returns_empty_without_index_creation(tmp_path):
    project = project_dir(tmp_path)
    candidates_dir(project).mkdir(parents=True, exist_ok=True)

    result = candidate_persistence.list_candidate_records(project)

    assert result == []
    assert not index_path(project).exists()


# ---------------------------------------------------------------------------
# Valid listing / sorting contract
# ---------------------------------------------------------------------------


def test_list_returns_valid_records_sorted_by_candidate_id(tmp_path):
    project = project_dir(tmp_path)
    record_c = build_valid_candidate_record(
        candidate_id="core_candidate_timeline_event_001",
        candidate_type="timeline_event_candidate",
        target_category="timeline",
    )
    record_a = build_valid_candidate_record(
        candidate_id="core_candidate_scene_001_character_001",
    )
    record_b = build_valid_candidate_record(
        candidate_id="core_candidate_scene_002_location_001",
        document_id="scene_002",
        candidate_type="location_candidate",
        target_category="locations_settings",
    )

    write_raw_candidate(project, record_c)
    write_raw_candidate(project, record_a)
    write_raw_candidate(project, record_b)

    result = candidate_persistence.list_candidate_records(project)

    assert isinstance(result, list)
    assert len(result) == 3
    assert [item["candidate_id"] for item in result] == sorted(
        [
            record_a["candidate_id"],
            record_b["candidate_id"],
            record_c["candidate_id"],
        ]
    )
    for item in result:
        candidate_record.validate_candidate_record(item)
    assert not index_path(project).exists()


# ---------------------------------------------------------------------------
# File filtering contract
# ---------------------------------------------------------------------------


def test_list_ignores_non_json_files_and_nested_directories(tmp_path):
    project = project_dir(tmp_path)
    valid_record = build_valid_candidate_record()
    write_raw_candidate(project, valid_record)

    storage = candidates_dir(project)
    (storage / "README.txt").write_text("ignore me", encoding="utf-8")
    (storage / "candidate.tmp").write_text("ignore me", encoding="utf-8")
    nested = storage / "nested"
    nested.mkdir()
    (nested / "ignored.json").write_text("{}", encoding="utf-8")

    result = candidate_persistence.list_candidate_records(project)

    assert len(result) == 1
    assert result[0]["candidate_id"] == valid_record["candidate_id"]
    assert not index_path(project).exists()


def test_list_ignores_existing_writer_assistant_index_file(tmp_path):
    project = project_dir(tmp_path)
    valid_record = build_valid_candidate_record()
    write_raw_candidate(project, valid_record)

    index_file = index_path(project)
    index_file.parent.mkdir(parents=True, exist_ok=True)
    index_payload = {"candidate_ids": ["stale"], "generated": True}
    index_file.write_text(
        json.dumps(index_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    original_index_text = index_file.read_text(encoding="utf-8")

    result = candidate_persistence.list_candidate_records(project)

    assert len(result) == 1
    assert result[0]["candidate_id"] == valid_record["candidate_id"]
    assert index_file.read_text(encoding="utf-8") == original_index_text


# ---------------------------------------------------------------------------
# Invalid candidate JSON contract
# ---------------------------------------------------------------------------


def test_list_raises_value_error_for_malformed_candidate_json(tmp_path):
    project = project_dir(tmp_path)
    candidate_path = candidates_dir(project) / "core_candidate_scene_001_character_001.json"
    candidate_path.parent.mkdir(parents=True, exist_ok=True)
    candidate_path.write_text("{not valid json", encoding="utf-8")
    original_text = candidate_path.read_text(encoding="utf-8")

    with pytest.raises(ValueError):
        candidate_persistence.list_candidate_records(project)

    assert candidate_path.read_text(encoding="utf-8") == original_text


def test_list_raises_value_error_for_non_object_json_root(tmp_path):
    project = project_dir(tmp_path)
    candidate_path = candidates_dir(project) / "core_candidate_scene_001_character_001.json"
    candidate_path.parent.mkdir(parents=True, exist_ok=True)
    candidate_path.write_text("[]", encoding="utf-8")

    with pytest.raises(ValueError):
        candidate_persistence.list_candidate_records(project)


@pytest.mark.parametrize(
    "invalid_payload",
    [
        pytest.param(
            {k: v for k, v in build_valid_candidate_record().items() if k != "candidate_type"},
            id="missing_candidate_type",
        ),
        pytest.param(
            build_valid_candidate_record(confidence=2.0),
            id="invalid_confidence",
        ),
        pytest.param(
            build_valid_candidate_record(destination="mutate_memory"),
            id="invalid_destination",
        ),
    ],
)
def test_list_raises_value_error_for_invalid_candidate_record(tmp_path, invalid_payload):
    project = project_dir(tmp_path)
    candidate_path = candidates_dir(project) / "core_candidate_scene_001_character_001.json"
    candidate_path.parent.mkdir(parents=True, exist_ok=True)
    candidate_path.write_text(
        json.dumps(invalid_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        candidate_persistence.list_candidate_records(project)


def test_list_raises_value_error_for_filename_record_candidate_id_mismatch(tmp_path):
    project = project_dir(tmp_path)
    filename_id = "core_candidate_a"
    record_id = "core_candidate_b"
    record = build_valid_candidate_record(candidate_id=record_id)

    candidate_path = candidates_dir(project) / f"{filename_id}.json"
    candidate_path.parent.mkdir(parents=True, exist_ok=True)
    candidate_path.write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        candidate_persistence.list_candidate_records(project)


# ---------------------------------------------------------------------------
# Side-effect contract
# ---------------------------------------------------------------------------


def test_list_is_side_effect_free_for_existing_candidate_files(tmp_path):
    project = project_dir(tmp_path)
    record = build_valid_candidate_record()
    candidate_path = write_raw_candidate(project, record)
    before_text = candidate_path.read_text(encoding="utf-8")
    before_mtime = candidate_path.stat().st_mtime_ns

    result = candidate_persistence.list_candidate_records(project)

    assert len(result) == 1
    assert candidate_path.read_text(encoding="utf-8") == before_text
    assert candidate_path.stat().st_mtime_ns == before_mtime
    assert not index_path(project).exists()


# ---------------------------------------------------------------------------
# Index deferral contract
# ---------------------------------------------------------------------------


def test_t005_does_not_require_index_helpers():
    """T005 covers list-only; index read/write deferred to later parent."""
    assert not hasattr(candidate_persistence, "write_candidate_index")
    assert not hasattr(candidate_persistence, "read_candidate_index")


# ---------------------------------------------------------------------------
# Source-level boundary contract (future helper module)
# ---------------------------------------------------------------------------


def test_candidate_persistence_source_has_no_forbidden_runtime_dependencies():
    module_source = inspect.getsource(candidate_persistence).lower()
    for forbidden_term in FORBIDDEN_SOURCE_TERMS:
        assert forbidden_term not in module_source
