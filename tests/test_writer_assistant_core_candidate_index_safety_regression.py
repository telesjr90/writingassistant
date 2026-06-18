"""Focused regression tests for Writer Assistant Core candidate index safety.

PHASE8-IMPL-004-T005 hardens source-of-truth boundaries, stale/corrupt index
behavior, validation-before-index-write, and non-candidate path mutation safety.
"""

import inspect
import json
from pathlib import Path

import pytest

from backend.story_knowledge import candidate_index
from backend.story_knowledge import candidate_persistence
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

FORBIDDEN_PUBLIC_HELPERS = (
    "sync_candidate_index",
    "update_candidate_index_for_record",
    "delete_candidate_index_entry",
    "refresh_candidate_index_for_routes",
    "extract_candidate_index",
)

ALLOWED_SUMMARY_FIELDS = frozenset(
    {
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
    }
)

FORBIDDEN_SUMMARY_LEAKAGE_FIELDS = (
    "evidence",
    "provenance",
    "candidate_content",
    "content",
    "body",
    "text",
    "excerpt",
    "analysis",
    "model_output",
)

SENTINEL_PATHS = (
    "memory/sentinel.json",
    "bible.json",
    "storyform.json",
    "scenes/scene_001.md",
    "notes/note_001.md",
    "materials/material_001.md",
    "omi/idea_001.json",
)


def project_dir(tmp_path: Path) -> Path:
    return tmp_path / "my-project"


def index_file_path(project: Path) -> Path:
    return candidate_storage.candidate_index_path(project)


def candidates_dir(project: Path) -> Path:
    return project / "writer_assistant" / "candidates"


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


def build_valid_index_from_records(records) -> dict:
    summaries = []
    for record in records:
        source_document_ids = set()
        locator = record.get("source_locator") or {}
        if locator.get("source_document_id"):
            source_document_ids.add(locator["source_document_id"])
        for item in record.get("evidence") or []:
            item_locator = item.get("source_locator") or {}
            if item_locator.get("source_document_id"):
                source_document_ids.add(item_locator["source_document_id"])
        summaries.append(
            {
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
        )
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


# ---------------------------------------------------------------------------
# 1. Source-of-truth safety
# ---------------------------------------------------------------------------


def test_build_uses_candidate_json_even_when_index_contains_conflicting_valid_candidate_ids(
    tmp_path,
):
    project = project_dir(tmp_path)
    record_a = build_valid_candidate_record()
    candidate_persistence.write_candidate_record(project, record_a)

    stale_candidate_b = build_valid_candidate_record(
        candidate_id="core_candidate_stale_other_001",
        candidate_type="location_candidate",
        target_category="locations_settings",
        document_id="scene_002",
    )
    write_raw_index(project, build_valid_index_from_records([stale_candidate_b]))
    index_path = index_file_path(project)
    stale_index_text = index_path.read_text(encoding="utf-8")

    result = candidate_index.build_candidate_index(project)

    assert result["candidate_count"] == 1
    assert result["candidate_ids"] == [record_a["candidate_id"]]
    assert result["candidates"][0]["candidate_id"] == record_a["candidate_id"]
    assert "core_candidate_stale_other_001" not in result["candidate_ids"]
    assert index_path.read_text(encoding="utf-8") == stale_index_text


# ---------------------------------------------------------------------------
# 2. Write refresh safety
# ---------------------------------------------------------------------------


def test_write_refreshes_index_from_candidate_json_and_replaces_stale_valid_index(
    tmp_path,
):
    project = project_dir(tmp_path)
    record_a = build_valid_candidate_record()
    candidate_path = candidate_storage.candidate_record_path(
        project, record_a["candidate_id"]
    )
    candidate_persistence.write_candidate_record(project, record_a)
    candidate_before = candidate_path.read_text(encoding="utf-8")

    stale_candidate_b = build_valid_candidate_record(
        candidate_id="core_candidate_stale_other_001",
        candidate_type="location_candidate",
        target_category="locations_settings",
        document_id="scene_002",
    )
    write_raw_index(project, build_valid_index_from_records([stale_candidate_b]))

    result = candidate_index.write_candidate_index(project)

    assert result["candidate_count"] == 1
    assert result["candidate_ids"] == [record_a["candidate_id"]]
    assert "core_candidate_stale_other_001" not in result["candidate_ids"]
    assert candidate_path.read_text(encoding="utf-8") == candidate_before


# ---------------------------------------------------------------------------
# 3. Corrupt index read/build/write separation
# ---------------------------------------------------------------------------


def test_read_corrupt_index_raises_without_repairing_file(tmp_path):
    project = project_dir(tmp_path)
    index_path = write_raw_index(project, "{not valid json")
    corrupt_text = index_path.read_text(encoding="utf-8")

    with pytest.raises(ValueError):
        candidate_index.read_candidate_index(project)

    assert index_path.read_text(encoding="utf-8") == corrupt_text
    assert not candidates_dir(project).exists()


def test_build_ignores_corrupt_index_without_repairing_it(tmp_path):
    project = project_dir(tmp_path)
    record = build_valid_candidate_record()
    candidate_persistence.write_candidate_record(project, record)

    index_path = write_raw_index(project, "{not valid json")
    corrupt_text = index_path.read_text(encoding="utf-8")

    result = candidate_index.build_candidate_index(project)

    assert result["candidate_count"] == 1
    assert result["candidate_ids"] == [record["candidate_id"]]
    assert index_path.read_text(encoding="utf-8") == corrupt_text


def test_write_overwrites_corrupt_index_only_after_candidate_records_validate(tmp_path):
    project = project_dir(tmp_path)
    record = build_valid_candidate_record()
    candidate_persistence.write_candidate_record(project, record)
    write_raw_index(project, "{not valid json")

    result = candidate_index.write_candidate_index(project)

    index_path = index_file_path(project)
    parsed = json.loads(index_path.read_text(encoding="utf-8"))
    assert parsed == result
    assert result["candidate_ids"] == [record["candidate_id"]]


# ---------------------------------------------------------------------------
# 4. Corrupt index is not overwritten when candidate records are invalid
# ---------------------------------------------------------------------------


def test_write_does_not_replace_corrupt_index_when_candidate_records_are_invalid(
    tmp_path,
):
    project = project_dir(tmp_path)
    index_path = write_raw_index(project, "{not valid json")
    corrupt_text = index_path.read_text(encoding="utf-8")

    invalid_candidate_path = (
        candidates_dir(project) / "core_candidate_scene_001_character_001.json"
    )
    invalid_candidate_path.parent.mkdir(parents=True, exist_ok=True)
    invalid_candidate_path.write_text("{not valid json", encoding="utf-8")
    invalid_text = invalid_candidate_path.read_text(encoding="utf-8")

    with pytest.raises(ValueError):
        candidate_index.write_candidate_index(project)

    assert index_path.read_text(encoding="utf-8") == corrupt_text
    assert invalid_candidate_path.read_text(encoding="utf-8") == invalid_text


# ---------------------------------------------------------------------------
# 5. Candidate file mutation safety
# ---------------------------------------------------------------------------


def test_index_write_does_not_rewrite_candidate_files_or_change_candidate_payloads(
    tmp_path,
):
    project = project_dir(tmp_path)
    record_a = build_valid_candidate_record()
    record_b = build_valid_candidate_record(
        candidate_id="core_candidate_scene_002_location_001",
        document_id="scene_002",
        candidate_type="location_candidate",
        target_category="locations_settings",
    )
    candidate_persistence.write_candidate_record(project, record_a)
    candidate_persistence.write_candidate_record(project, record_b)

    candidate_paths = {
        record_a["candidate_id"]: candidate_storage.candidate_record_path(
            project, record_a["candidate_id"]
        ),
        record_b["candidate_id"]: candidate_storage.candidate_record_path(
            project, record_b["candidate_id"]
        ),
    }
    before_text = {
        candidate_id: path.read_text(encoding="utf-8")
        for candidate_id, path in candidate_paths.items()
    }
    before_parsed = {
        candidate_id: json.loads(text) for candidate_id, text in before_text.items()
    }

    candidate_index.write_candidate_index(project)

    for candidate_id, path in candidate_paths.items():
        after_text = path.read_text(encoding="utf-8")
        assert after_text == before_text[candidate_id]
        assert json.loads(after_text) == before_parsed[candidate_id]


# ---------------------------------------------------------------------------
# 6. Non-candidate project path mutation safety
# ---------------------------------------------------------------------------


def test_index_helpers_preserve_non_candidate_project_truth_files_and_directories(
    tmp_path,
):
    project = project_dir(tmp_path)
    sentinels = create_sentinel_project_paths(project)
    sentinel_folder_names = ("memory", "scenes", "notes", "materials", "omi")

    def files_in_sentinel_folders() -> set[Path]:
        found = set()
        for folder_name in sentinel_folder_names:
            folder = project / folder_name
            if folder.exists():
                found.update(path for path in folder.rglob("*") if path.is_file())
        return found

    before_sentinel_folder_files = files_in_sentinel_folders()
    all_files_before = {path for path in project.rglob("*") if path.is_file()}

    record = build_valid_candidate_record()
    candidate_persistence.write_candidate_record(project, record)

    candidate_index.build_candidate_index(project)
    candidate_index.write_candidate_index(project)
    candidate_index.read_candidate_index(project)

    assert_sentinels_unchanged(project, sentinels)
    assert files_in_sentinel_folders() == before_sentinel_folder_files

    all_files_after = {path for path in project.rglob("*") if path.is_file()}
    new_files = all_files_after - all_files_before
    allowed_new = {
        index_file_path(project),
        candidate_storage.candidate_record_path(project, record["candidate_id"]),
    }
    assert new_files == allowed_new


# ---------------------------------------------------------------------------
# 7. No accidental candidate directory creation during empty build/read
# ---------------------------------------------------------------------------


def test_build_missing_candidates_does_not_create_writer_assistant_or_index(tmp_path):
    project = project_dir(tmp_path)

    candidate_index.build_candidate_index(project)

    assert not (project / "writer_assistant").exists()
    assert not index_file_path(project).exists()


def test_read_missing_index_does_not_create_writer_assistant_or_index(tmp_path):
    project = project_dir(tmp_path)

    with pytest.raises(FileNotFoundError):
        candidate_index.read_candidate_index(project)

    assert not (project / "writer_assistant").exists()
    assert not index_file_path(project).exists()


# ---------------------------------------------------------------------------
# 8. Existing candidate directory safety during empty write
# ---------------------------------------------------------------------------


def test_write_empty_index_does_not_create_candidates_directory_when_missing(tmp_path):
    project = project_dir(tmp_path)

    candidate_index.write_candidate_index(project)

    assert index_file_path(project).exists()
    assert not candidates_dir(project).exists()
    assert list(project.iterdir()) == [project / "writer_assistant"]


# ---------------------------------------------------------------------------
# 9. Index summary does not leak full candidate payload or prose-like body fields
# ---------------------------------------------------------------------------


def test_index_summary_contains_only_allowed_summary_fields(tmp_path):
    project = project_dir(tmp_path)
    record = build_valid_candidate_record()
    candidate_persistence.write_candidate_record(project, record)

    result = candidate_index.build_candidate_index(project)

    assert len(result["candidates"]) == 1
    summary = result["candidates"][0]
    assert set(summary.keys()) == ALLOWED_SUMMARY_FIELDS
    for forbidden_field in FORBIDDEN_SUMMARY_LEAKAGE_FIELDS:
        assert forbidden_field not in summary


# ---------------------------------------------------------------------------
# 10. Source document ID derivation safety
# ---------------------------------------------------------------------------


def test_source_document_ids_are_unique_sorted_and_derived_from_evidence_only(tmp_path):
    project = project_dir(tmp_path)
    record = build_valid_candidate_record(
        source_locator=build_valid_source_locator(document_id="scene_003"),
        evidence=[
            build_valid_evidence_item(document_id="scene_002"),
            build_valid_evidence_item(
                document_id="scene_001",
                evidence_id="evidence_002",
            ),
            build_valid_evidence_item(
                document_id="scene_002",
                evidence_id="evidence_003",
            ),
        ],
    )
    candidate_persistence.write_candidate_record(project, record)

    result = candidate_index.build_candidate_index(project)
    summary = result["candidates"][0]

    assert summary["source_document_ids"] == ["scene_001", "scene_002", "scene_003"]
    assert summary["destination"] == record["destination"]
    assert summary["provenance_kind"] == record["provenance"]["origin"]
    assert "omi_candidate_only" not in summary["source_document_ids"]


# ---------------------------------------------------------------------------
# 11. Source-level boundary regression
# ---------------------------------------------------------------------------


def test_candidate_index_source_has_no_runtime_route_model_extraction_or_promotion_dependencies():
    module_source = inspect.getsource(candidate_index).lower()
    for forbidden_term in FORBIDDEN_SOURCE_TERMS:
        assert forbidden_term not in module_source


# ---------------------------------------------------------------------------
# 12. API surface regression
# ---------------------------------------------------------------------------


def test_candidate_index_public_api_remains_minimal():
    for helper_name in (
        "build_candidate_index",
        "write_candidate_index",
        "read_candidate_index",
    ):
        helper = getattr(candidate_index, helper_name, None)
        assert callable(helper), f"missing public helper: {helper_name}"

    for forbidden_helper in FORBIDDEN_PUBLIC_HELPERS:
        assert not hasattr(candidate_index, forbidden_helper), (
            f"unexpected public helper: {forbidden_helper}"
        )
