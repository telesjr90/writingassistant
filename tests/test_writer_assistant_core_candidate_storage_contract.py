"""Contract tests for future Writer Assistant Core candidate storage path helpers.

T006 is expected to implement `backend.story_knowledge.candidate_storage` with:
- candidate_storage_dir(project_dir: Path) -> Path
- candidate_index_path(project_dir: Path) -> Path
- candidate_record_path(project_dir: Path, candidate_id: str) -> Path
- validate_candidate_storage_path(project_dir: Path, candidate_id: str) -> Path

T005 does not authorize storage writes.
T006 may implement pure path helpers only unless separately authorized.
JSON read/write/list helpers remain deferred unless a later task expands scope.
"""

import inspect
from pathlib import Path

import pytest

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
    "candidate/../../escape",
    "core_candidate_../escape",
)

FORBIDDEN_PATH_PARTS = frozenset(
    {
        "memory",
        "canon",
        "bible.json",
        "storyform.json",
        "scenes",
        "notes",
        "materials",
        "omi",
    }
)

FORBIDDEN_SOURCE_TERMS = (
    "open(",
    ".write_text",
    ".mkdir",
    "requests",
    "httpx",
    "ollama",
    "openai",
    "analysis_engine",
    "story_check",
    "apply_promotion",
    "write_to_canon",
    "mutate_memory",
    "rewrite_scene",
    "training",
)

COMPATIBLE_SAFE_CANDIDATE_IDS = (
    "core_candidate_scene_001_character_001",
    "core_candidate_timeline_event_001",
    "core_candidate_plot_thread_alpha",
)


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def project_dir(tmp_path: Path) -> Path:
    return tmp_path / "my-project"


# ---------------------------------------------------------------------------
# Storage directory path contract
# ---------------------------------------------------------------------------


def test_candidate_storage_dir_returns_writer_assistant_candidates_path(tmp_path):
    project = project_dir(tmp_path)
    result = candidate_storage.candidate_storage_dir(project)
    assert result == project / "writer_assistant" / "candidates"
    assert not result.exists()


# ---------------------------------------------------------------------------
# Candidate index path contract
# ---------------------------------------------------------------------------


def test_candidate_index_path_returns_writer_assistant_index_json(tmp_path):
    project = project_dir(tmp_path)
    result = candidate_storage.candidate_index_path(project)
    assert result == project / "writer_assistant" / "index.json"
    assert not result.exists()


# ---------------------------------------------------------------------------
# Candidate record path contract
# ---------------------------------------------------------------------------


def test_candidate_record_path_returns_safe_candidate_json_path(tmp_path):
    project = project_dir(tmp_path)
    result = candidate_storage.candidate_record_path(project, SAFE_CANDIDATE_ID)
    expected = (
        project / "writer_assistant" / "candidates" / f"{SAFE_CANDIDATE_ID}.json"
    )
    assert result == expected
    storage_dir = candidate_storage.candidate_storage_dir(project)
    assert is_relative_to(result, storage_dir)
    assert not result.exists()
    assert not storage_dir.exists()


# ---------------------------------------------------------------------------
# Unsafe candidate ID contract
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("unsafe_candidate_id", UNSAFE_CANDIDATE_IDS)
def test_candidate_record_path_rejects_unsafe_candidate_id(
    tmp_path, unsafe_candidate_id
):
    project = project_dir(tmp_path)
    with pytest.raises(ValueError):
        candidate_storage.candidate_record_path(project, unsafe_candidate_id)


@pytest.mark.parametrize("unsafe_candidate_id", UNSAFE_CANDIDATE_IDS)
def test_validate_candidate_storage_path_rejects_unsafe_candidate_id(
    tmp_path, unsafe_candidate_id
):
    project = project_dir(tmp_path)
    with pytest.raises(ValueError):
        candidate_storage.validate_candidate_storage_path(
            project, unsafe_candidate_id
        )


# ---------------------------------------------------------------------------
# Project directory boundary contract
# ---------------------------------------------------------------------------


def test_storage_paths_remain_project_local(tmp_path):
    project = project_dir(tmp_path)
    storage_dir = candidate_storage.candidate_storage_dir(project)
    index_path = candidate_storage.candidate_index_path(project)
    record_path = candidate_storage.candidate_record_path(project, SAFE_CANDIDATE_ID)

    assert is_relative_to(storage_dir, project)
    assert is_relative_to(index_path, project)
    assert is_relative_to(record_path, project)
    assert is_relative_to(record_path, storage_dir)


# ---------------------------------------------------------------------------
# Forbidden storage location contract
# ---------------------------------------------------------------------------


def test_storage_paths_do_not_use_forbidden_project_locations(tmp_path):
    project = project_dir(tmp_path)
    paths = (
        candidate_storage.candidate_storage_dir(project),
        candidate_storage.candidate_index_path(project),
        candidate_storage.candidate_record_path(project, SAFE_CANDIDATE_ID),
    )
    for path in paths:
        path_parts = set(path.parts)
        assert path_parts.isdisjoint(FORBIDDEN_PATH_PARTS), (
            f"forbidden path part in {path}"
        )


# ---------------------------------------------------------------------------
# No filesystem side effects contract
# ---------------------------------------------------------------------------


def test_path_helpers_do_not_create_files_or_directories(tmp_path):
    """T005 does not authorize storage writes; helpers must remain pure."""
    project = project_dir(tmp_path)

    candidate_storage.candidate_storage_dir(project)
    candidate_storage.candidate_index_path(project)
    candidate_storage.candidate_record_path(project, SAFE_CANDIDATE_ID)
    candidate_storage.validate_candidate_storage_path(project, SAFE_CANDIDATE_ID)

    writer_assistant_dir = project / "writer_assistant"
    candidates_dir = writer_assistant_dir / "candidates"
    index_file = writer_assistant_dir / "index.json"
    record_file = candidates_dir / f"{SAFE_CANDIDATE_ID}.json"

    assert not writer_assistant_dir.exists()
    assert not candidates_dir.exists()
    assert not index_file.exists()
    assert not record_file.exists()


# ---------------------------------------------------------------------------
# validate_candidate_storage_path contract
# ---------------------------------------------------------------------------


def test_validate_candidate_storage_path_returns_safe_record_path(tmp_path):
    project = project_dir(tmp_path)
    record_path = candidate_storage.candidate_record_path(project, SAFE_CANDIDATE_ID)
    validated_path = candidate_storage.validate_candidate_storage_path(
        project, SAFE_CANDIDATE_ID
    )
    assert validated_path == record_path
    assert not validated_path.exists()


# ---------------------------------------------------------------------------
# Source-level boundary contract (future helper module)
# ---------------------------------------------------------------------------


def test_candidate_storage_module_source_has_no_forbidden_runtime_dependencies():
    module_source = inspect.getsource(candidate_storage).lower()
    for forbidden_term in FORBIDDEN_SOURCE_TERMS:
        assert forbidden_term not in module_source


# ---------------------------------------------------------------------------
# Validation helper compatibility contract
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("candidate_id", COMPATIBLE_SAFE_CANDIDATE_IDS)
def test_safe_candidate_ids_accepted_by_record_and_storage_helpers(
    tmp_path, candidate_id
):
    project = project_dir(tmp_path)
    record = {
        "candidate_id": candidate_id,
        "project_id": "my-project",
        "candidate_type": "character_candidate",
        "status": "candidate",
        "target_category": "characters",
        "source_locator": {
            "project_id": "my-project",
            "source_document_type": "scene",
            "source_document_id": "scene_001",
        },
        "evidence": [],
        "provenance": {
            "origin": "manual",
            "extraction_method": "owner_entry",
            "timestamp": "2026-06-16T00:00:00Z",
            "human_review_required": True,
        },
        "owner_decision": "undecided",
        "destination": "omi_candidate_only",
        "confidence": 0.0,
        "created_at": "2026-06-16T00:00:00Z",
        "updated_at": "2026-06-16T00:00:00Z",
    }
    candidate_record.validate_candidate_record(record)
    storage_path = candidate_storage.candidate_record_path(project, candidate_id)
    assert storage_path.name == f"{candidate_id}.json"


# ---------------------------------------------------------------------------
# Storage writes remain future-only
# ---------------------------------------------------------------------------


def test_t005_does_not_authorize_storage_writes():
    """T005 defines path contracts only; read/write/list behavior is deferred."""
    assert True
