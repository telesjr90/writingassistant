"""PHASE7-IMPL-005-T003 backend note/material route tests.

These tests follow the lightweight fake FastAPI / pydantic module pattern
from ``tests/test_scene_routes.py``. They assert:

1. Note list route returns metadata-compatible records for body-only notes.
2. Note read route returns exact body and metadata compatibility defaults.
3. Note save route saves body and does not create metadata.
4. Note metadata PUT creates metadata for an existing note body without
   changing the note body.
5. Note metadata PUT updates existing metadata without changing body.
6. Material list route returns metadata-compatible records for body-only
   materials.
7. Material read route returns exact body and metadata compatibility
   defaults.
8. Material save route saves body and does not create metadata.
9. Material metadata PUT creates metadata for an existing material body
   without changing the material body.
10. Material metadata PUT updates existing metadata without changing body.
11. Missing body behavior for metadata PUT remains safe.
12. Existing scene route contracts remain unchanged (covered by running
    ``tests/test_scene_routes.py`` unchanged).
"""

from __future__ import annotations

import json
import sys
import types
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


class _FakeFastAPI:
    def add_middleware(self, *args, **kwargs):
        return None

    def get(self, *args, **kwargs):
        return self._decorator

    def post(self, *args, **kwargs):
        return self._decorator

    def put(self, *args, **kwargs):
        return self._decorator

    @staticmethod
    def _decorator(func):
        return func


class _FakeHTTPException(Exception):
    def __init__(self, status_code, detail):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


class _FakeBaseModel:
    pass


fake_fastapi = types.ModuleType("fastapi")
fake_fastapi.FastAPI = _FakeFastAPI
fake_fastapi.HTTPException = _FakeHTTPException

fake_middleware = types.ModuleType("fastapi.middleware")
fake_cors = types.ModuleType("fastapi.middleware.cors")
fake_cors.CORSMiddleware = object

fake_pydantic = types.ModuleType("pydantic")
fake_pydantic.BaseModel = _FakeBaseModel

sys.modules.setdefault("fastapi", fake_fastapi)
sys.modules.setdefault("fastapi.middleware", fake_middleware)
sys.modules.setdefault("fastapi.middleware.cors", fake_cors)
sys.modules.setdefault("pydantic", fake_pydantic)

from backend import main  # noqa: E402  (imports follow sys.path setup)


PROJECT_NAME = "example"


@pytest.fixture
def project_dir(tmp_path, monkeypatch):
    """Point the live project_manager at a fresh tmp directory per test."""
    monkeypatch.setattr(main.project_manager, "PROJECTS_DIR", tmp_path)
    return tmp_path


# ---------------------------------------------------------------------------
# Note routes
# ---------------------------------------------------------------------------


def test_note_list_route_returns_compatibility_defaults_for_body_only_note(
    project_dir,
):
    content = "# Planning Note\n\nOwner-authored note text."
    main.project_manager.save_note(PROJECT_NAME, "note_001", content)

    response = main.get_notes(PROJECT_NAME)

    assert "notes" in response
    assert len(response["notes"]) == 1
    record = response["notes"][0]
    assert record["note_id"] == "note_001"
    assert record["project_id"] == PROJECT_NAME
    assert record["content_path"] == "notes/note_001.md"
    assert record["metadata_exists"] is False
    assert record["title"] == ""
    assert record["note_type"] == "general"
    assert record["status"] == "draft"

    metadata_path = project_dir / PROJECT_NAME / "note_metadata" / "note_001.json"
    assert not metadata_path.exists()


def test_note_read_route_returns_exact_body_and_metadata_compatibility_defaults(
    project_dir,
):
    content = "# Planning Note\n\nOwner-authored note text."
    main.project_manager.save_note(PROJECT_NAME, "note_001", content)

    response = main.get_note(PROJECT_NAME, "note_001")

    assert response["content"] == content
    assert "metadata" in response
    metadata = response["metadata"]
    assert metadata["note_id"] == "note_001"
    assert metadata["content_path"] == "notes/note_001.md"
    assert metadata["metadata_exists"] is False

    # Metadata must never be injected into the body.
    assert "note_type" not in response["content"]
    assert "notes/note_001.md" not in response["content"]

    metadata_path = project_dir / PROJECT_NAME / "note_metadata" / "note_001.json"
    assert not metadata_path.exists()


def test_note_save_route_saves_body_without_creating_metadata(project_dir):
    payload = types.SimpleNamespace(content="Owner-authored body.")

    response = main.update_note(PROJECT_NAME, "note_001", payload)

    assert response == {"status": "saved"}
    assert (
        main.project_manager.load_note(PROJECT_NAME, "note_001")
        == "Owner-authored body."
    )

    metadata_path = project_dir / PROJECT_NAME / "note_metadata" / "note_001.json"
    assert not metadata_path.exists()


def test_note_metadata_put_creates_metadata_without_changing_note_body(project_dir):
    content = "Owner-authored note text."
    main.project_manager.save_note(PROJECT_NAME, "note_001", content)

    update = types.SimpleNamespace(
        metadata={
            "title": "Planning Note",
            "note_type": "research",
            "status": "active",
            "tags": ["map", "research"],
            "linked_chapter_ids": ["chapter_001"],
            "linked_scene_ids": ["scene_001"],
            "owner_notes": "Owner-authored metadata note.",
        }
    )

    response = main.update_note_metadata_route(PROJECT_NAME, "note_001", update)

    assert "metadata" in response
    metadata = response["metadata"]
    assert metadata["note_id"] == "note_001"
    assert metadata["project_id"] == PROJECT_NAME
    assert metadata["content_path"] == "notes/note_001.md"
    assert metadata["metadata_exists"] is True
    assert metadata["metadata_path"] == "note_metadata/note_001.json"
    assert metadata["title"] == "Planning Note"
    assert metadata["note_type"] == "research"
    assert metadata["status"] == "active"
    assert metadata["tags"] == ["map", "research"]
    assert metadata["linked_chapter_ids"] == ["chapter_001"]
    assert metadata["linked_scene_ids"] == ["scene_001"]
    assert metadata["owner_notes"] == "Owner-authored metadata note."
    # Provenance defaults come from the helper normalisation layer.
    assert metadata["provenance"]["created_by"] == "owner"

    # Body must remain exact and untouched.
    assert main.project_manager.load_note(PROJECT_NAME, "note_001") == content


def test_note_metadata_put_updates_existing_metadata_without_changing_body(
    project_dir,
):
    content = "Owner-authored note text."
    main.project_manager.save_note(PROJECT_NAME, "note_001", content)
    main.project_manager.create_note_metadata(
        PROJECT_NAME,
        "note_001",
        {"title": "Initial", "status": "draft", "tags": []},
    )

    body_before = main.project_manager.load_note(PROJECT_NAME, "note_001")
    metadata_path = (
        project_dir / PROJECT_NAME / "note_metadata" / "note_001.json"
    )
    raw_before = metadata_path.read_text(encoding="utf-8")

    update = types.SimpleNamespace(
        metadata={
            "title": "Updated",
            "status": "active",
            "tags": ["revision"],
            "owner_notes": "Owner update note.",
        }
    )

    response = main.update_note_metadata_route(PROJECT_NAME, "note_001", update)

    metadata = response["metadata"]
    assert metadata["title"] == "Updated"
    assert metadata["status"] == "active"
    assert metadata["tags"] == ["revision"]
    assert metadata["owner_notes"] == "Owner update note."
    # Safe identity fields remain derived from the request, not the payload.
    assert metadata["project_id"] == PROJECT_NAME
    assert metadata["note_id"] == "note_001"
    assert metadata["content_path"] == "notes/note_001.md"
    assert metadata["metadata_exists"] is True

    # Body must remain exact and untouched.
    assert main.project_manager.load_note(PROJECT_NAME, "note_001") == body_before
    # The metadata file was rewritten by the update, not preserved verbatim,
    # but the on-disk content_path remains derived.
    raw_after = metadata_path.read_text(encoding="utf-8")
    assert raw_after != raw_before
    persisted = json.loads(raw_after)
    assert persisted["content_path"] == "notes/note_001.md"
    assert persisted["title"] == "Updated"


def test_note_metadata_put_for_missing_body_raises_http_error(project_dir):
    update = types.SimpleNamespace(metadata={"title": "Missing"})

    with pytest.raises(main.HTTPException) as exc_info:
        main.update_note_metadata_route(PROJECT_NAME, "note_missing", update)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Note not found"

    assert not (
        project_dir / PROJECT_NAME / "notes" / "note_missing.md"
    ).exists()
    assert not (
        project_dir / PROJECT_NAME / "note_metadata" / "note_missing.json"
    ).exists()


# ---------------------------------------------------------------------------
# Material routes
# ---------------------------------------------------------------------------


def test_material_list_route_returns_compatibility_defaults_for_body_only_material(
    project_dir,
):
    content = "# Research Material\n\nOwner-provided material text."
    main.project_manager.save_material(PROJECT_NAME, "material_001", content)

    response = main.get_materials(PROJECT_NAME)

    assert "materials" in response
    assert len(response["materials"]) == 1
    record = response["materials"][0]
    assert record["material_id"] == "material_001"
    assert record["project_id"] == PROJECT_NAME
    assert record["content_path"] == "materials/material_001.md"
    assert record["metadata_exists"] is False
    assert record["title"] == ""
    assert record["material_type"] == "text_reference"
    assert record["status"] == "draft"
    assert record["source_kind"] == "owner_text"
    assert record["license_status"] == "owner_provided"

    metadata_path = (
        project_dir / PROJECT_NAME / "material_metadata" / "material_001.json"
    )
    assert not metadata_path.exists()


def test_material_read_route_returns_exact_body_and_metadata_compatibility_defaults(
    project_dir,
):
    content = "# Research Material\n\nOwner-provided material text."
    main.project_manager.save_material(PROJECT_NAME, "material_001", content)

    response = main.get_material(PROJECT_NAME, "material_001")

    assert response["content"] == content
    assert "metadata" in response
    metadata = response["metadata"]
    assert metadata["material_id"] == "material_001"
    assert metadata["content_path"] == "materials/material_001.md"
    assert metadata["metadata_exists"] is False

    # Metadata must never be injected into the body.
    assert "material_type" not in response["content"]
    assert "materials/material_001.md" not in response["content"]

    metadata_path = (
        project_dir / PROJECT_NAME / "material_metadata" / "material_001.json"
    )
    assert not metadata_path.exists()


def test_material_save_route_saves_body_without_creating_metadata(project_dir):
    payload = types.SimpleNamespace(content="Owner-provided body.")

    response = main.update_material(PROJECT_NAME, "material_001", payload)

    assert response == {"status": "saved"}
    assert (
        main.project_manager.load_material(PROJECT_NAME, "material_001")
        == "Owner-provided body."
    )

    metadata_path = (
        project_dir / PROJECT_NAME / "material_metadata" / "material_001.json"
    )
    assert not metadata_path.exists()


def test_material_metadata_put_creates_metadata_without_changing_material_body(
    project_dir,
):
    content = "Owner-provided material text."
    main.project_manager.save_material(PROJECT_NAME, "material_001", content)

    update = types.SimpleNamespace(
        metadata={
            "title": "Research Material",
            "material_type": "research",
            "status": "active",
            "source_kind": "citation",
            "source_citation": "Owner-provided citation",
            "license_status": "reference_only",
            "usage_restrictions": ["no_training"],
            "source_warnings": ["review_license"],
            "tags": ["reference"],
            "owner_notes": "Owner-authored metadata note.",
        }
    )

    response = main.update_material_metadata_route(
        PROJECT_NAME, "material_001", update
    )

    assert "metadata" in response
    metadata = response["metadata"]
    assert metadata["material_id"] == "material_001"
    assert metadata["project_id"] == PROJECT_NAME
    assert metadata["content_path"] == "materials/material_001.md"
    assert metadata["metadata_exists"] is True
    assert metadata["metadata_path"] == "material_metadata/material_001.json"
    assert metadata["title"] == "Research Material"
    assert metadata["material_type"] == "research"
    assert metadata["status"] == "active"
    assert metadata["source_kind"] == "citation"
    assert metadata["source_citation"] == "Owner-provided citation"
    assert metadata["license_status"] == "reference_only"
    assert metadata["usage_restrictions"] == ["no_training"]
    assert metadata["source_warnings"] == ["review_license"]
    assert metadata["tags"] == ["reference"]
    assert metadata["owner_notes"] == "Owner-authored metadata note."

    # Body must remain exact and untouched.
    assert main.project_manager.load_material(PROJECT_NAME, "material_001") == content


def test_material_metadata_put_updates_existing_metadata_without_changing_body(
    project_dir,
):
    content = "Owner-provided material text."
    main.project_manager.save_material(PROJECT_NAME, "material_001", content)
    main.project_manager.create_material_metadata(
        PROJECT_NAME,
        "material_001",
        {"title": "Initial", "status": "draft"},
    )

    body_before = main.project_manager.load_material(PROJECT_NAME, "material_001")
    metadata_path = (
        project_dir / PROJECT_NAME / "material_metadata" / "material_001.json"
    )
    raw_before = metadata_path.read_text(encoding="utf-8")

    update = types.SimpleNamespace(
        metadata={
            "title": "Updated",
            "status": "active",
            "source_kind": "research_link",
            "source_citation": "Updated citation",
            "license_status": "licensed_for_project",
            "tags": ["reference", "updated"],
        }
    )

    response = main.update_material_metadata_route(
        PROJECT_NAME, "material_001", update
    )

    metadata = response["metadata"]
    assert metadata["title"] == "Updated"
    assert metadata["status"] == "active"
    assert metadata["source_kind"] == "research_link"
    assert metadata["source_citation"] == "Updated citation"
    assert metadata["license_status"] == "licensed_for_project"
    assert metadata["tags"] == ["reference", "updated"]
    # Safe identity fields remain derived from the request, not the payload.
    assert metadata["project_id"] == PROJECT_NAME
    assert metadata["material_id"] == "material_001"
    assert metadata["content_path"] == "materials/material_001.md"
    assert metadata["metadata_exists"] is True

    # Body must remain exact and untouched.
    assert (
        main.project_manager.load_material(PROJECT_NAME, "material_001")
        == body_before
    )
    # The metadata file was rewritten by the update.
    raw_after = metadata_path.read_text(encoding="utf-8")
    assert raw_after != raw_before
    persisted = json.loads(raw_after)
    assert persisted["content_path"] == "materials/material_001.md"
    assert persisted["title"] == "Updated"


def test_material_metadata_put_for_missing_body_raises_http_error(project_dir):
    update = types.SimpleNamespace(metadata={"title": "Missing"})

    with pytest.raises(main.HTTPException) as exc_info:
        main.update_material_metadata_route(
            PROJECT_NAME, "material_missing", update
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Material not found"

    assert not (
        project_dir / PROJECT_NAME / "materials" / "material_missing.md"
    ).exists()
    assert not (
        project_dir
        / PROJECT_NAME
        / "material_metadata"
        / "material_missing.json"
    ).exists()
