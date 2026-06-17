"""Contract tests for future Writer Assistant Core candidate persistence helpers.

T004 is expected to implement `backend.story_knowledge.candidate_persistence` with:
- write_candidate_record(project_dir: Path, record: dict) -> dict
- read_candidate_record(project_dir: Path, candidate_id: str) -> dict

List/index helpers remain deferred to T005/T006.
Index read/write remains deferred to a later parent per T002 decision.
"""

import copy
import inspect
import json
from pathlib import Path

import pytest

from backend.story_knowledge import candidate_persistence
from backend.story_knowledge import candidate_record
from backend.story_knowledge import candidate_storage

SAFE_CANDIDATE_ID = "core_candidate_scene_001_character_001"

UNSAFE_CANDIDATE_IDS = (
    "../escape",
    "..",
    ".",
    "/absolute",
    "C:\\escape",
    "folder/name",
    "folder\\name",
    "",
    "   ",
    "candidate.json",
    "core_candidate_../escape",
)

FORBIDDEN_WRITE_PATHS = (
    "writer_assistant/index.json",
    "memory",
    "bible.json",
    "storyform.json",
    "scenes",
    "notes",
    "materials",
    "omi",
)

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


def build_valid_source_locator(**overrides):
    locator = {
        "project_id": "example",
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
        "origin": "manual",
        "extraction_method": "owner_entry",
        "timestamp": "2026-06-16T00:00:00Z",
        "human_review_required": True,
    }
    provenance.update(overrides)
    return provenance


def build_valid_candidate_record(**overrides):
    record = {
        "candidate_id": SAFE_CANDIDATE_ID,
        "project_id": "example",
        "candidate_type": "character_candidate",
        "status": "candidate",
        "target_category": "characters",
        "source_locator": build_valid_source_locator(),
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


def all_project_paths(project: Path):
    if not project.exists():
        return []
    return [path for path in project.rglob("*")]


def assert_no_writer_assistant_dir(project: Path):
    writer_assistant = project / "writer_assistant"
    assert not writer_assistant.exists()


# ---------------------------------------------------------------------------
# Existing helper compatibility
# ---------------------------------------------------------------------------


def test_valid_fixture_passes_candidate_record_validation():
    record = build_valid_candidate_record()
    result = candidate_record.validate_candidate_record(record)
    assert result["candidate_id"] == SAFE_CANDIDATE_ID


def test_valid_fixture_aligns_with_candidate_storage_path(tmp_path):
    project = project_dir(tmp_path)
    record = build_valid_candidate_record()
    candidate_record.validate_candidate_record(record)
    path = candidate_storage.candidate_record_path(project, record["candidate_id"])
    assert path == (
        project / "writer_assistant" / "candidates" / f"{SAFE_CANDIDATE_ID}.json"
    )


# ---------------------------------------------------------------------------
# Write valid record contract
# ---------------------------------------------------------------------------


def test_write_candidate_record_persists_valid_record(tmp_path):
    project = project_dir(tmp_path)
    record = build_valid_candidate_record()
    result = candidate_persistence.write_candidate_record(project, record)

    assert isinstance(result, dict)
    assert result == record or result == candidate_record.validate_candidate_record(record)

    candidate_path = candidate_storage.candidate_record_path(project, SAFE_CANDIDATE_ID)
    assert candidate_path.exists()
    assert candidate_path.is_file()
    assert "writer_assistant" in candidate_path.parts
    assert "candidates" in candidate_path.parts

    file_content = json.loads(candidate_path.read_text(encoding="utf-8"))
    assert file_content == result

    index_path = project / "writer_assistant" / "index.json"
    assert not index_path.exists()


# ---------------------------------------------------------------------------
# Write creates only allowed directories/files
# ---------------------------------------------------------------------------


def test_write_creates_only_allowed_directories_and_files(tmp_path):
    project = project_dir(tmp_path)
    record = build_valid_candidate_record()
    candidate_persistence.write_candidate_record(project, record)

    writer_assistant = project / "writer_assistant"
    candidates_dir = writer_assistant / "candidates"
    candidate_path = candidates_dir / f"{SAFE_CANDIDATE_ID}.json"

    assert writer_assistant.is_dir()
    assert candidates_dir.is_dir()
    assert candidate_path.is_file()

    for forbidden in FORBIDDEN_WRITE_PATHS:
        forbidden_path = project / forbidden
        assert not forbidden_path.exists(), f"forbidden path created: {forbidden_path}"

    all_paths = all_project_paths(project)
    assert len(all_paths) == 3
    assert set(all_paths) == {writer_assistant, candidates_dir, candidate_path}


# ---------------------------------------------------------------------------
# Validation-before-write contract
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "invalid_record",
    [
        pytest.param(
            {k: v for k, v in build_valid_candidate_record().items() if k != "candidate_type"},
            id="missing_candidate_type",
        ),
        pytest.param(
            {**build_valid_candidate_record(), "unknown_field": "x"},
            id="unknown_field",
        ),
        pytest.param(
            build_valid_candidate_record(candidate_id="../escape"),
            id="invalid_candidate_id",
        ),
        pytest.param(
            build_valid_candidate_record(
                candidate_type="character_candidate",
                target_category="timeline",
            ),
            id="mismatched_target_category",
        ),
        pytest.param(
            build_valid_candidate_record(destination="write_to_canon"),
            id="invalid_destination",
        ),
        pytest.param(
            build_valid_candidate_record(confidence=1.5),
            id="invalid_confidence",
        ),
    ],
)
def test_write_rejects_invalid_record_before_creating_files(tmp_path, invalid_record):
    project = project_dir(tmp_path)
    with pytest.raises(ValueError):
        candidate_persistence.write_candidate_record(project, invalid_record)
    assert_no_writer_assistant_dir(project)


# ---------------------------------------------------------------------------
# Caller input mutation contract
# ---------------------------------------------------------------------------


def test_write_does_not_mutate_caller_input(tmp_path):
    project = project_dir(tmp_path)
    record = build_valid_candidate_record()
    original = copy.deepcopy(record)
    candidate_persistence.write_candidate_record(project, record)
    assert record == original


# ---------------------------------------------------------------------------
# Same-ID overwrite contract
# ---------------------------------------------------------------------------


def test_write_overwrites_same_candidate_id_without_append_or_merge(tmp_path):
    project = project_dir(tmp_path)
    first = build_valid_candidate_record(updated_at="2026-06-16T00:00:00Z")
    second = build_valid_candidate_record(
        updated_at="2026-06-17T12:00:00Z",
        confidence=0.75,
    )

    candidate_persistence.write_candidate_record(project, first)
    candidate_persistence.write_candidate_record(project, second)

    candidate_path = candidate_storage.candidate_record_path(project, SAFE_CANDIDATE_ID)
    file_content = json.loads(candidate_path.read_text(encoding="utf-8"))
    assert file_content["updated_at"] == "2026-06-17T12:00:00Z"
    assert file_content["confidence"] == 0.75

    candidates_dir = project / "writer_assistant" / "candidates"
    json_files = list(candidates_dir.glob("*.json"))
    assert len(json_files) == 1


# ---------------------------------------------------------------------------
# Read valid record contract
# ---------------------------------------------------------------------------


def test_read_candidate_record_returns_valid_record(tmp_path):
    project = project_dir(tmp_path)
    record = build_valid_candidate_record()
    candidate_persistence.write_candidate_record(project, record)

    before_paths = set(all_project_paths(project))
    result = candidate_persistence.read_candidate_record(project, SAFE_CANDIDATE_ID)
    after_paths = set(all_project_paths(project))

    assert result == record or result == candidate_record.validate_candidate_record(record)
    assert before_paths == after_paths
    assert not (project / "writer_assistant" / "index.json").exists()


# ---------------------------------------------------------------------------
# Read missing file contract
# ---------------------------------------------------------------------------


def test_read_missing_candidate_raises_file_not_found(tmp_path):
    project = project_dir(tmp_path)
    with pytest.raises(FileNotFoundError):
        candidate_persistence.read_candidate_record(project, SAFE_CANDIDATE_ID)

    assert_no_writer_assistant_dir(project)


# ---------------------------------------------------------------------------
# Read malformed JSON contract
# ---------------------------------------------------------------------------


def test_read_malformed_json_raises_value_error_without_repair(tmp_path):
    project = project_dir(tmp_path)
    candidate_path = candidate_storage.candidate_record_path(project, SAFE_CANDIDATE_ID)
    candidate_path.parent.mkdir(parents=True, exist_ok=True)
    candidate_path.write_text("{not valid json", encoding="utf-8")
    original_text = candidate_path.read_text(encoding="utf-8")

    with pytest.raises(ValueError):
        candidate_persistence.read_candidate_record(project, SAFE_CANDIDATE_ID)

    assert candidate_path.read_text(encoding="utf-8") == original_text


# ---------------------------------------------------------------------------
# Read non-dict JSON root contract
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("invalid_root", ["[]", '"string"', "42"])
def test_read_non_dict_json_root_raises_value_error(tmp_path, invalid_root):
    project = project_dir(tmp_path)
    candidate_path = candidate_storage.candidate_record_path(project, SAFE_CANDIDATE_ID)
    candidate_path.parent.mkdir(parents=True, exist_ok=True)
    candidate_path.write_text(invalid_root, encoding="utf-8")

    with pytest.raises(ValueError):
        candidate_persistence.read_candidate_record(project, SAFE_CANDIDATE_ID)


# ---------------------------------------------------------------------------
# Read invalid record contract
# ---------------------------------------------------------------------------


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
def test_read_invalid_record_raises_value_error(tmp_path, invalid_payload):
    project = project_dir(tmp_path)
    candidate_path = candidate_storage.candidate_record_path(project, SAFE_CANDIDATE_ID)
    candidate_path.parent.mkdir(parents=True, exist_ok=True)
    candidate_path.write_text(
        json.dumps(invalid_payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        candidate_persistence.read_candidate_record(project, SAFE_CANDIDATE_ID)


# ---------------------------------------------------------------------------
# Read candidate ID mismatch contract
# ---------------------------------------------------------------------------


def test_read_candidate_id_mismatch_raises_value_error(tmp_path):
    project = project_dir(tmp_path)
    candidate_id_a = SAFE_CANDIDATE_ID
    candidate_id_b = "core_candidate_timeline_event_001"
    record = build_valid_candidate_record(candidate_id=candidate_id_b)

    candidate_path = candidate_storage.candidate_record_path(project, candidate_id_a)
    candidate_path.parent.mkdir(parents=True, exist_ok=True)
    candidate_path.write_text(
        json.dumps(record, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        candidate_persistence.read_candidate_record(project, candidate_id_a)


# ---------------------------------------------------------------------------
# Unsafe candidate ID contract
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("unsafe_candidate_id", UNSAFE_CANDIDATE_IDS)
def test_read_rejects_unsafe_candidate_id_without_side_effects(
    tmp_path, unsafe_candidate_id
):
    project = project_dir(tmp_path)
    with pytest.raises(ValueError):
        candidate_persistence.read_candidate_record(project, unsafe_candidate_id)
    assert_no_writer_assistant_dir(project)


@pytest.mark.parametrize("unsafe_candidate_id", UNSAFE_CANDIDATE_IDS)
def test_write_rejects_unsafe_candidate_id_without_side_effects(
    tmp_path, unsafe_candidate_id
):
    project = project_dir(tmp_path)
    record = build_valid_candidate_record(candidate_id=unsafe_candidate_id)
    with pytest.raises(ValueError):
        candidate_persistence.write_candidate_record(project, record)
    assert_no_writer_assistant_dir(project)


# ---------------------------------------------------------------------------
# List/index out of scope for T003
# ---------------------------------------------------------------------------


def test_t003_does_not_require_list_or_index_helpers():
    """T003 covers write/read only; list added in T006; index deferred to later parent."""
    assert hasattr(candidate_persistence, "list_candidate_records")
    assert not hasattr(candidate_persistence, "write_candidate_index")
    assert not hasattr(candidate_persistence, "read_candidate_index")


# ---------------------------------------------------------------------------
# Source-level boundary contract (future helper module)
# ---------------------------------------------------------------------------


def test_candidate_persistence_module_source_has_no_forbidden_runtime_dependencies():
    module_source = inspect.getsource(candidate_persistence).lower()
    for forbidden_term in FORBIDDEN_SOURCE_TERMS:
        assert forbidden_term not in module_source
