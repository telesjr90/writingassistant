import importlib
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# test_context_routes.py registers lightweight fakes in sys.modules during collection.
for _mod in (
    "fastapi",
    "fastapi.middleware",
    "fastapi.middleware.cors",
    "fastapi.testclient",
    "pydantic",
):
    sys.modules.pop(_mod, None)

from fastapi.testclient import TestClient
from pydantic import ValidationError

import backend.main as main
import backend.project_manager as project_manager

importlib.reload(project_manager)
importlib.reload(main)


@pytest.fixture
def client():
    return TestClient(main.app)


class TestDeriveProjectId:
    def test_normal_title_becomes_safe_lowercase_slug(self):
        assert project_manager.derive_project_id("My Project") == "my-project"

    def test_spaces_and_punctuation_are_handled_safely(self):
        assert project_manager.derive_project_id("Hello, World!") == "hello-world"
        assert project_manager.derive_project_id("  spaced   out  ") == "spaced-out"

    def test_unicode_accents_are_ascii_folded(self):
        assert project_manager.derive_project_id("Café René") == "cafe-rene"
        assert project_manager.derive_project_id("naïve coöperation") == "naive-cooperation"

    def test_blank_title_is_rejected(self):
        with pytest.raises(ValueError, match="must not be blank"):
            project_manager.derive_project_id("   ")

    def test_title_normalizing_to_no_valid_id_is_rejected(self):
        with pytest.raises(ValueError, match="empty project ID"):
            project_manager.derive_project_id("!!!")
        with pytest.raises(ValueError, match="empty project ID"):
            project_manager.derive_project_id("...")


class TestValidateProjectId:
    @pytest.mark.parametrize(
        "project_id",
        [
            "",
            "/absolute/path",
            "..",
            "foo/bar",
            r"foo\bar",
            "c:project",
            "api",
            "projects",
            "omi",
            "-starts-with-hyphen",
            "UPPERCASE",
            "has space",
        ],
    )
    def test_rejects_unsafe_project_ids(self, project_id):
        with pytest.raises(ValueError):
            project_manager.validate_project_id(project_id)

    @pytest.mark.parametrize("project_id", ["my-project", "my_project"])
    def test_accepts_safe_project_ids(self, project_id):
        assert project_manager.validate_project_id(project_id) == project_id


class TestResolveProjectIdWithCollision:
    def test_returns_base_id_when_unused(self, tmp_path):
        assert (
            project_manager.resolve_project_id_with_collision("my-project", tmp_path)
            == "my-project"
        )

    def test_returns_base_2_when_base_folder_exists(self, tmp_path):
        (tmp_path / "my-project").mkdir()
        assert (
            project_manager.resolve_project_id_with_collision("my-project", tmp_path)
            == "my-project-2"
        )

    def test_returns_base_3_when_base_and_base_2_exist(self, tmp_path):
        (tmp_path / "my-project").mkdir()
        (tmp_path / "my-project-2").mkdir()
        assert (
            project_manager.resolve_project_id_with_collision("my-project", tmp_path)
            == "my-project-3"
        )

    def test_does_not_overwrite_existing_folders(self, tmp_path):
        existing = tmp_path / "my-project"
        existing.mkdir()
        marker = existing / "keep.txt"
        marker.write_text("preserve", encoding="utf-8")

        resolved = project_manager.resolve_project_id_with_collision("my-project", tmp_path)

        assert resolved == "my-project-2"
        assert marker.read_text(encoding="utf-8") == "preserve"
        assert not (tmp_path / "my-project-2").exists()


class TestCreateProject:
    def test_creates_project_directory_and_metadata(self, tmp_path):
        metadata = project_manager.create_project("My Project", projects_dir=tmp_path)

        project_path = tmp_path / "my-project"
        assert project_path.is_dir()
        assert (project_path / "project.json").is_file()
        for folder in project_manager.WORKSPACE_CORE_FOLDERS:
            assert (project_path / folder).is_dir()

        assert metadata["project_id"] == "my-project"
        assert metadata["title"] == "My Project"
        assert metadata["created_at"]
        assert metadata["updated_at"]
        assert metadata["schema_version"] == project_manager.PROJECT_SCHEMA_VERSION
        assert metadata["creation_method"] == project_manager.PROJECT_CREATION_METHOD_BLANK
        assert metadata["owner_approved_truth_policy"] == project_manager.OWNER_APPROVED_TRUTH_POLICY

        saved = json.loads((project_path / "project.json").read_text(encoding="utf-8"))
        assert saved == metadata

    def test_created_path_remains_under_projects_dir(self, tmp_path):
        project_manager.create_project("Scoped Project", projects_dir=tmp_path)
        for path in tmp_path.rglob("*"):
            assert path.resolve().is_relative_to(tmp_path.resolve())

    def test_does_not_create_forbidden_workspace_artifacts(self, tmp_path):
        project_manager.create_project("Safe Project", projects_dir=tmp_path)
        project_path = tmp_path / "safe-project"

        forbidden_files = ["bible.json", "storyform.json"]
        for filename in forbidden_files:
            assert not (project_path / filename).exists()

        forbidden_dirs = ["omi", "memory"]
        for dirname in forbidden_dirs:
            assert not (project_path / dirname).exists()

        scene_files = list((project_path / "scenes").glob("*.md"))
        assert scene_files == []

    def test_duplicate_title_produces_deterministic_suffix(self, tmp_path):
        first = project_manager.create_project("My Project", projects_dir=tmp_path)
        second = project_manager.create_project("My Project", projects_dir=tmp_path)

        assert first["project_id"] == "my-project"
        assert second["project_id"] == "my-project-2"
        assert (tmp_path / "my-project").is_dir()
        assert (tmp_path / "my-project-2").is_dir()


class TestPostProjectRoute:
    def test_post_project_success(self, client, monkeypatch):
        received: dict[str, str] = {}

        def fake_create_project(*, title: str):
            received["title"] = title
            return {
                "project_id": "my-project",
                "title": title,
                "created_at": "2026-01-01T00:00:00Z",
                "updated_at": "2026-01-01T00:00:00Z",
                "schema_version": "0.1.0",
                "creation_method": "blank",
                "owner_approved_truth_policy": project_manager.OWNER_APPROVED_TRUTH_POLICY,
            }

        monkeypatch.setattr(main.project_manager, "create_project", fake_create_project)

        response = client.post("/api/projects", json={"title": "My Project"})

        assert response.status_code == 200
        assert response.json()["project_id"] == "my-project"
        assert response.json()["title"] == "My Project"
        assert received["title"] == "My Project"

    def test_post_project_value_error_returns_400(self, client, monkeypatch):
        def fake_create_project(*, title: str):
            raise ValueError("blank project title")

        monkeypatch.setattr(main.project_manager, "create_project", fake_create_project)

        response = client.post("/api/projects", json={"title": " "})

        assert response.status_code == 400
        assert response.json()["detail"] == "blank project title"

    def test_post_project_does_not_leak_unsafe_paths(self, client, monkeypatch):
        def fake_create_project(*, title: str):
            raise ValueError(
                "Project path /evil/projects/foo is not inside the projects directory /safe"
            )

        monkeypatch.setattr(main.project_manager, "create_project", fake_create_project)

        response = client.post("/api/projects", json={"title": "Evil"})

        assert response.status_code == 400
        detail = response.json()["detail"]
        assert detail == "Unable to create project with the given title"
        assert "/evil" not in detail

    def test_post_project_file_exists_returns_409(self, client, monkeypatch):
        def fake_create_project(*, title: str):
            raise FileExistsError("Project directory already exists")

        monkeypatch.setattr(main.project_manager, "create_project", fake_create_project)

        response = client.post("/api/projects", json={"title": "Duplicate"})

        assert response.status_code == 409
        assert response.json()["detail"] == "Project already exists"

    def test_post_project_runtime_error_returns_500(self, client, monkeypatch):
        def fake_create_project(*, title: str):
            raise RuntimeError("disk failure")

        monkeypatch.setattr(main.project_manager, "create_project", fake_create_project)

        response = client.post("/api/projects", json={"title": "Broken"})

        assert response.status_code == 500
        assert response.json()["detail"] == "Failed to create project"

    def test_post_project_rejects_owner_supplied_project_id(self, client):
        response = client.post(
            "/api/projects",
            json={"title": "A", "project_id": "evil"},
        )

        assert response.status_code == 422

    def test_project_create_model_forbids_extra_fields(self):
        with pytest.raises(ValidationError):
            main.ProjectCreate.model_validate({"title": "A", "project_id": "evil"})
