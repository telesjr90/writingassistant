"""Contract tests for future Writer Assistant Core candidate index helpers.

T004 is expected to implement `backend.story_knowledge.candidate_index` with:
- build_candidate_index(project_dir: Path) -> dict
- write_candidate_index(project_dir: Path) -> dict
- read_candidate_index(project_dir: Path) -> dict

Expected red until T004 because `candidate_index` module/helpers do not exist yet.
"""

import copy
import inspect
import json
from pathlib import Path

import pytest

from backend.story_knowledge import candidate_index
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

FULL_RECORD_FIELDS_NOT_IN_SUMMARY = (
    "project_id",
    "target_category",
    "source_locator",
    "evidence",
    "provenance",
    "owner_decision",
)

SENTINEL_PATHS = (
    "memory/sentinel.txt",
    "bible.json",
    "storyform.json",
    "scenes/sentinel.txt",
    "notes/sentinel.txt",
    "materials/sentinel.txt",
    "omi/sentinel.txt",
)

FORBIDDEN_WRITE_DIRS = (
    "memory",
    "scenes",
    "notes",
    "materials",
    "omi",
)

FORBIDDEN_WRITE_FILES = (
    "bible.json",
    "storyform.json",
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
        "evidence": [build_valid_evidence_item(document_id=document_id)],
        "provenance": build_valid_provenance(),
        "owner_decision": "undecided",
        "destination": "omi_candidate_only",
        "confidence": 0.8,
        "created_at": "2026-06-17T00:00:00Z",
        "updated_at": "2026-06-17T00:00:00Z",
    }
    record.update(overrides)
    return record


def project_dir(tmp_path: Path) -> Path:
    return tmp_path / "my-project"


def candidates_dir(project: Path) -> Path:
    return project / "writer_assistant" / "candidates"


def index_file_path(project: Path) -> Path:
    return candidate_storage.candidate_index_path(project)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def expected_empty_index() -> dict:
    return {
        "schema_version": 1,
        "kind": "writer_assistant_candidate_index",
        "source": "writer_assistant_candidates",
        "candidate_count": 0,
        "candidate_ids": [],
        "candidates": [],
        "generated_from": {
            "source_of_truth": "writer_assistant/candidates",
            "index_is_derived": True,
        },
    }


def expected_summary_from_record(record: dict) -> dict:
    source_document_ids = set()
    locator = record.get("source_locator") or {}
    if locator.get("source_document_id"):
        source_document_ids.add(locator["source_document_id"])
    for item in record.get("evidence") or []:
        item_locator = item.get("source_locator") or {}
        if item_locator.get("source_document_id"):
            source_document_ids.add(item_locator["source_document_id"])
    return {
        "candidate_id": record["candidate_id"],
        "candidate_type": record["candidate_type"],
        "status": record["status"],
        "destination": record["destination"],
        "confidence": record["confidence"],
        "source_document_ids": sorted(source_document_ids),
        "evidence_count": len(record.get("evidence") or []),
        "provenance_kind": record["provenance"]["origin"],
        "created_at": record["created_at"],
        "updated_at": record["updated_at"],
    }


def write_raw_index(project: Path, payload) -> Path:
    path = index_file_path(project)
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(payload, str):
        path.write_text(payload, encoding="utf-8")
    else:
        path.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return path


def create_sentinel_project_paths(project: Path) -> dict:
    sentinels = {}
    for relative in SENTINEL_PATHS:
        path = project / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"sentinel:{relative}", encoding="utf-8")
        sentinels[relative] = path.read_text(encoding="utf-8")
    return sentinels


def assert_sentinels_unchanged(project: Path, sentinels: dict):
    for relative, original in sentinels.items():
        path = project / relative
        assert path.exists(), f"missing sentinel path: {relative}"
        assert path.read_text(encoding="utf-8") == original


def build_valid_index_from_records(records) -> dict:
    summaries = [expected_summary_from_record(record) for record in records]
    summaries.sort(key=lambda item: item["candidate_id"])
    candidate_ids = [item["candidate_id"] for item in summaries]
    return {
        "schema_version": 1,
        "kind": "writer_assistant_candidate_index",
        "source": "writer_assistant_candidates",
        "candidate_count": len(candidate_ids),
        "candidate_ids": candidate_ids,
        "candidates": summaries,
        "generated_from": {
            "source_of_truth": "writer_assistant/candidates",
            "index_is_derived": True,
        },
    }


# ---------------------------------------------------------------------------
# Empty build behavior
# ---------------------------------------------------------------------------


def test_build_candidate_index_returns_empty_index_for_missing_candidate_directory(
    tmp_path,
):
    project = project_dir(tmp_path)
    result = candidate_index.build_candidate_index(project)

    assert result == expected_empty_index()
    assert not (project / "writer_assistant").exists()
    assert not index_file_path(project).exists()


def test_build_candidate_index_returns_empty_index_for_empty_candidates_directory(
    tmp_path,
):
    project = project_dir(tmp_path)
    candidates_dir(project).mkdir(parents=True, exist_ok=True)

    result = candidate_index.build_candidate_index(project)

    assert result == expected_empty_index()
    assert not index_file_path(project).exists()


# ---------------------------------------------------------------------------
# Build valid derived index from candidate JSON
# ---------------------------------------------------------------------------


def test_build_candidate_index_derives_summary_from_candidate_records(tmp_path):
    project = project_dir(tmp_path)
    record = build_valid_candidate_record()
    candidate_persistence.write_candidate_record(project, record)

    result = candidate_index.build_candidate_index(project)

    assert result["schema_version"] == 1
    assert result["kind"] == "writer_assistant_candidate_index"
    assert result["source"] == "writer_assistant_candidates"
    assert result["candidate_count"] == 1
    assert result["candidate_ids"] == [record["candidate_id"]]
    assert result["generated_from"] == {
        "source_of_truth": "writer_assistant/candidates",
        "index_is_derived": True,
    }

    assert len(result["candidates"]) == 1
    summary = result["candidates"][0]
    expected = expected_summary_from_record(record)
    assert summary == expected

    for field in (
        "candidate_id",
        "candidate_type",
        "status",
        "destination",
        "confidence",
        "source_document_ids",
        "evidence_count",
        "provenance_kind",
        "created_at",
        "updated_at",
    ):
        assert field in summary

    for forbidden_field in FULL_RECORD_FIELDS_NOT_IN_SUMMARY:
        assert forbidden_field not in summary

    assert not index_file_path(project).exists()


# ---------------------------------------------------------------------------
# Deterministic ordering
# ---------------------------------------------------------------------------


def test_build_candidate_index_sorts_candidate_ids_and_summaries_by_candidate_id(
    tmp_path,
):
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

    candidate_persistence.write_candidate_record(project, record_c)
    candidate_persistence.write_candidate_record(project, record_a)
    candidate_persistence.write_candidate_record(project, record_b)

    result = candidate_index.build_candidate_index(project)
    expected_ids = sorted(
        [
            record_a["candidate_id"],
            record_b["candidate_id"],
            record_c["candidate_id"],
        ]
    )

    assert result["candidate_ids"] == expected_ids
    assert [item["candidate_id"] for item in result["candidates"]] == expected_ids


# ---------------------------------------------------------------------------
# Build ignores existing index
# ---------------------------------------------------------------------------


def test_build_candidate_index_ignores_existing_index_file(tmp_path):
    project = project_dir(tmp_path)
    record = build_valid_candidate_record()
    candidate_persistence.write_candidate_record(project, record)

    stale_index = {
        "schema_version": 1,
        "kind": "writer_assistant_candidate_index",
        "source": "writer_assistant_candidates",
        "candidate_count": 99,
        "candidate_ids": ["stale_candidate"],
        "candidates": [{"candidate_id": "stale_candidate"}],
        "generated_from": {
            "source_of_truth": "writer_assistant/candidates",
            "index_is_derived": True,
        },
    }
    index_path = write_raw_index(project, stale_index)
    original_index_text = index_path.read_text(encoding="utf-8")

    result = candidate_index.build_candidate_index(project)

    assert result["candidate_count"] == 1
    assert result["candidate_ids"] == [record["candidate_id"]]
    assert result["candidates"][0]["candidate_id"] == record["candidate_id"]
    assert index_path.read_text(encoding="utf-8") == original_index_text


# ---------------------------------------------------------------------------
# Build fails fast on invalid candidate JSON
# ---------------------------------------------------------------------------


def test_build_candidate_index_raises_value_error_for_invalid_candidate_json(tmp_path):
    project = project_dir(tmp_path)
    candidate_path = (
        candidates_dir(project) / "core_candidate_scene_001_character_001.json"
    )
    candidate_path.parent.mkdir(parents=True, exist_ok=True)
    candidate_path.write_text("{not valid json", encoding="utf-8")
    original_text = candidate_path.read_text(encoding="utf-8")

    with pytest.raises(ValueError):
        candidate_index.build_candidate_index(project)

    assert not index_file_path(project).exists()
    assert candidate_path.read_text(encoding="utf-8") == original_text


# ---------------------------------------------------------------------------
# Write behavior
# ---------------------------------------------------------------------------


def test_write_candidate_index_writes_stable_json_to_index_path(tmp_path):
    project = project_dir(tmp_path)
    record = build_valid_candidate_record()
    candidate_path = candidate_storage.candidate_record_path(
        project, record["candidate_id"]
    )
    candidate_persistence.write_candidate_record(project, record)
    candidate_before = candidate_path.read_text(encoding="utf-8")

    result = candidate_index.write_candidate_index(project)
    index_path = index_file_path(project)

    assert index_path == candidate_storage.candidate_index_path(project)
    assert index_path.exists()

    file_text = index_path.read_text(encoding="utf-8")
    assert file_text.endswith("\n")
    assert read_json(index_path) == result
    assert result == build_valid_index_from_records([record])

    parsed = json.loads(file_text)
    assert list(parsed.keys()) == sorted(parsed.keys())
    assert candidate_path.read_text(encoding="utf-8") == candidate_before


def test_write_candidate_index_creates_only_index_parent_directory(tmp_path):
    project = project_dir(tmp_path)

    result = candidate_index.write_candidate_index(project)
    index_path = index_file_path(project)

    assert index_path.exists()
    assert result == expected_empty_index()

    for forbidden_dir in FORBIDDEN_WRITE_DIRS:
        assert not (project / forbidden_dir).exists()
    for forbidden_file in FORBIDDEN_WRITE_FILES:
        assert not (project / forbidden_file).exists()


def test_write_candidate_index_overwrites_corrupt_existing_index_when_candidates_are_valid(
    tmp_path,
):
    project = project_dir(tmp_path)
    write_raw_index(project, "{not valid json")
    record = build_valid_candidate_record()
    candidate_path = candidate_storage.candidate_record_path(
        project, record["candidate_id"]
    )
    candidate_persistence.write_candidate_record(project, record)
    candidate_before = candidate_path.read_text(encoding="utf-8")

    result = candidate_index.write_candidate_index(project)

    assert read_json(index_file_path(project)) == result
    assert result["candidate_ids"] == [record["candidate_id"]]
    assert candidate_path.read_text(encoding="utf-8") == candidate_before


# ---------------------------------------------------------------------------
# Read valid index
# ---------------------------------------------------------------------------


def test_read_candidate_index_reads_and_validates_existing_index(tmp_path):
    project = project_dir(tmp_path)
    record = build_valid_candidate_record()
    candidate_persistence.write_candidate_record(project, record)

    written = candidate_index.write_candidate_index(project)
    before_paths = {path for path in project.rglob("*")}

    read_result = candidate_index.read_candidate_index(project)

    after_paths = {path for path in project.rglob("*")}
    assert read_result == written
    assert before_paths == after_paths


# ---------------------------------------------------------------------------
# Read missing index
# ---------------------------------------------------------------------------


def test_read_candidate_index_raises_file_not_found_for_missing_index(tmp_path):
    project = project_dir(tmp_path)

    with pytest.raises(FileNotFoundError):
        candidate_index.read_candidate_index(project)

    assert not (project / "writer_assistant").exists()
    assert not index_file_path(project).exists()


# ---------------------------------------------------------------------------
# Read malformed index JSON
# ---------------------------------------------------------------------------


def test_read_candidate_index_raises_value_error_for_malformed_index_json(tmp_path):
    project = project_dir(tmp_path)
    index_path = write_raw_index(project, "{not valid json")
    original_text = index_path.read_text(encoding="utf-8")

    with pytest.raises(ValueError):
        candidate_index.read_candidate_index(project)

    assert index_path.read_text(encoding="utf-8") == original_text


def test_read_candidate_index_raises_value_error_for_non_object_index_json(tmp_path):
    project = project_dir(tmp_path)
    write_raw_index(project, "[]")

    with pytest.raises(ValueError):
        candidate_index.read_candidate_index(project)


# ---------------------------------------------------------------------------
# Read invalid index shape
# ---------------------------------------------------------------------------


def _valid_index_with_one_summary() -> dict:
    record = build_valid_candidate_record()
    return build_valid_index_from_records([record])


@pytest.mark.parametrize(
    "mutator,case_id",
    [
        pytest.param(
            lambda index: {k: v for k, v in index.items() if k != "schema_version"},
            "missing_schema_version",
        ),
        pytest.param(
            lambda index: {**index, "schema_version": 2},
            "wrong_schema_version",
        ),
        pytest.param(
            lambda index: {**index, "kind": "wrong_kind"},
            "wrong_kind",
        ),
        pytest.param(
            lambda index: {**index, "source": "wrong_source"},
            "wrong_source",
        ),
        pytest.param(
            lambda index: {**index, "candidate_count": 99},
            "candidate_count_mismatch",
        ),
        pytest.param(
            lambda index: {
                **index,
                "candidate_ids": list(reversed(index["candidate_ids"])),
            },
            "candidate_ids_not_sorted",
        ),
        pytest.param(
            lambda index: {
                **index,
                "candidates": list(reversed(index["candidates"])),
            },
            "candidates_not_sorted",
        ),
        pytest.param(
            lambda index: {
                **index,
                "candidate_ids": index["candidate_ids"] + ["extra_id"],
            },
            "candidate_ids_not_matching_summaries",
        ),
        pytest.param(
            lambda index: {
                **index,
                "candidates": [
                    {k: v for k, v in index["candidates"][0].items() if k != "candidate_id"}
                ],
            },
            "summary_missing_candidate_id",
        ),
        pytest.param(
            lambda index: {
                **index,
                "candidates": [
                    {
                        **index["candidates"][0],
                        "source_document_ids": ["scene_002", "scene_001"],
                    }
                ],
            },
            "summary_invalid_source_document_ids_order",
        ),
        pytest.param(
            lambda index: {
                **index,
                "generated_from": {
                    **index["generated_from"],
                    "index_is_derived": False,
                },
            },
            "generated_from_index_is_derived_false",
        ),
        pytest.param(
            lambda index: {
                **index,
                "generated_from": {
                    **index["generated_from"],
                    "source_of_truth": "memory/canon",
                },
            },
            "generated_from_wrong_source_of_truth",
        ),
    ],
)
def test_read_candidate_index_raises_value_error_for_invalid_index_shape(
    tmp_path, mutator, case_id
):
    project = project_dir(tmp_path)
    base_index = _valid_index_with_one_summary()
    if case_id in ("candidate_ids_not_sorted", "candidates_not_sorted"):
        second_record = build_valid_candidate_record(
            candidate_id="core_candidate_scene_002_location_001",
            document_id="scene_002",
            candidate_type="location_candidate",
            target_category="locations_settings",
        )
        base_index = build_valid_index_from_records(
            [build_valid_candidate_record(), second_record]
        )
    invalid_index = mutator(copy.deepcopy(base_index))
    write_raw_index(project, invalid_index)

    with pytest.raises(ValueError):
        candidate_index.read_candidate_index(project)


# ---------------------------------------------------------------------------
# Read does not rebuild stale index
# ---------------------------------------------------------------------------


def test_read_candidate_index_does_not_rebuild_or_compare_stale_index(tmp_path):
    project = project_dir(tmp_path)
    record = build_valid_candidate_record()
    candidate_path = candidate_storage.candidate_record_path(
        project, record["candidate_id"]
    )
    candidate_persistence.write_candidate_record(project, record)
    candidate_before = candidate_path.read_text(encoding="utf-8")

    stale_but_valid = expected_empty_index()
    index_path = write_raw_index(project, stale_but_valid)
    index_before = index_path.read_text(encoding="utf-8")

    result = candidate_index.read_candidate_index(project)

    assert result == stale_but_valid
    assert candidate_path.read_text(encoding="utf-8") == candidate_before
    assert index_path.read_text(encoding="utf-8") == index_before


# ---------------------------------------------------------------------------
# Index never overrides candidate JSON
# ---------------------------------------------------------------------------


def test_index_never_overrides_candidate_json_source_of_truth(tmp_path):
    project = project_dir(tmp_path)
    record = build_valid_candidate_record()
    candidate_path = candidate_storage.candidate_record_path(
        project, record["candidate_id"]
    )
    candidate_persistence.write_candidate_record(project, record)
    candidate_before = candidate_path.read_text(encoding="utf-8")

    fake_index = build_valid_index_from_records(
        [
            build_valid_candidate_record(
                candidate_id="core_candidate_fake_other_001",
                candidate_type="location_candidate",
                target_category="locations_settings",
            )
        ]
    )
    write_raw_index(project, fake_index)

    result = candidate_index.build_candidate_index(project)

    assert result["candidate_count"] == 1
    assert result["candidate_ids"] == [record["candidate_id"]]
    assert result["candidates"][0]["candidate_id"] == record["candidate_id"]
    assert candidate_path.read_text(encoding="utf-8") == candidate_before


# ---------------------------------------------------------------------------
# Boundary side effects
# ---------------------------------------------------------------------------


def test_index_helpers_do_not_touch_non_candidate_project_paths(tmp_path):
    project = project_dir(tmp_path)
    sentinels = create_sentinel_project_paths(project)
    record = build_valid_candidate_record()
    candidate_persistence.write_candidate_record(project, record)

    candidate_index.build_candidate_index(project)
    candidate_index.write_candidate_index(project)

    assert_sentinels_unchanged(project, sentinels)


# ---------------------------------------------------------------------------
# Source-level boundary test for future module
# ---------------------------------------------------------------------------


def test_candidate_index_module_source_has_no_forbidden_runtime_dependencies():
    module_source = inspect.getsource(candidate_index).lower()
    for forbidden_term in FORBIDDEN_SOURCE_TERMS:
        assert forbidden_term not in module_source
