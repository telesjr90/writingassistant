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

import backend.main as main
import backend.project_manager as project_manager

importlib.reload(project_manager)
importlib.reload(main)


def _write_project_json(
    project_dir: Path,
    *,
    project_id: str | None = None,
    title: str = "Test Project",
    created_at: str = "2026-01-01T00:00:00Z",
    updated_at: str = "2026-06-01T00:00:00Z",
    schema_version: str = "0.1.0",
    creation_method: str = "blank",
    raw_content: str | None = None,
) -> None:
    project_dir.mkdir(parents=True, exist_ok=True)
    if raw_content is not None:
        (project_dir / "project.json").write_text(raw_content, encoding="utf-8")
        return

    metadata = {
        "project_id": project_id if project_id is not None else project_dir.name,
        "title": title,
        "created_at": created_at,
        "updated_at": updated_at,
        "schema_version": schema_version,
        "creation_method": creation_method,
    }
    (project_dir / "project.json").write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8",
    )


def _assert_no_absolute_path_leak(record: dict) -> None:
    serialized = json.dumps(record)
    assert "/home" not in serialized
    assert "\\" not in serialized
    assert not any(
        part[1] == ":" and part[0].isalpha()
        for part in serialized.split('"')
        if len(part) >= 2
    )
    for value in record.values():
        if isinstance(value, str):
            assert not Path(value).is_absolute()
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, str):
                    assert not Path(item).is_absolute()


@pytest.fixture
def client():
    return TestClient(main.app)


class TestListProjectsMissingDir:
    def test_missing_projects_dir_returns_empty_list_without_crash(self, tmp_path):
        missing = tmp_path / "does-not-exist"
        assert project_manager.list_projects(projects_dir=missing) == []


class TestListProjectsValidProject:
    def test_valid_project_returns_one_valid_record(self, tmp_path):
        project_dir = tmp_path / "my-project"
        _write_project_json(project_dir)

        records = project_manager.list_projects(projects_dir=tmp_path)

        assert len(records) == 1
        record = records[0]
        assert record["project_id"] == "my-project"
        assert record["title"] == "Test Project"
        assert record["status"] == "valid"
        assert record["warnings"] == []
        assert record["relative_path"] == "my-project"
        assert not Path(record["relative_path"]).is_absolute()
        _assert_no_absolute_path_leak(record)


class TestListProjectsMissingProjectJson:
    def test_missing_project_json_produces_invalid_record(self, tmp_path):
        (tmp_path / "orphan-dir").mkdir()

        records = project_manager.list_projects(projects_dir=tmp_path)

        assert len(records) == 1
        record = records[0]
        assert record["status"] == "invalid"
        assert "missing project.json" in record["warnings"][0]
        _assert_no_absolute_path_leak(record)


class TestListProjectsInvalidJson:
    def test_invalid_json_produces_invalid_record_without_crash(self, tmp_path):
        project_dir = tmp_path / "bad-json"
        _write_project_json(project_dir, raw_content="{ not valid json")

        records = project_manager.list_projects(projects_dir=tmp_path)

        assert len(records) == 1
        record = records[0]
        assert record["status"] == "invalid"
        assert "invalid JSON" in record["warnings"][0]
        _assert_no_absolute_path_leak(record)


class TestListProjectsNonObjectJson:
    @pytest.mark.parametrize("raw_content", ["[]", '"just-a-string"'])
    def test_non_object_json_produces_invalid_record(self, tmp_path, raw_content):
        project_dir = tmp_path / "not-object"
        _write_project_json(project_dir, raw_content=raw_content)

        records = project_manager.list_projects(projects_dir=tmp_path)

        assert len(records) == 1
        record = records[0]
        assert record["status"] in {"invalid", "warning"}
        assert record["warnings"]
        _assert_no_absolute_path_leak(record)


class TestListProjectsMismatchedProjectId:
    def test_mismatched_folder_and_json_project_id_is_invalid(self, tmp_path):
        project_dir = tmp_path / "actual-id"
        _write_project_json(project_dir, project_id="other-id")

        records = project_manager.list_projects(projects_dir=tmp_path)

        assert len(records) == 1
        record = records[0]
        assert record["status"] == "invalid"
        assert "mismatch" in record["warnings"][0]
        assert record["project_id"] == "actual-id"
        _assert_no_absolute_path_leak(record)


class TestListProjectsUnsafeFolderNames:
    @pytest.mark.parametrize(
        "folder_name",
        ["api", "UPPERCASE", "-starts-hyphen", "has space"],
    )
    def test_unsafe_folder_names_produce_invalid_records(self, tmp_path, folder_name):
        (tmp_path / folder_name).mkdir()

        records = project_manager.list_projects(projects_dir=tmp_path)

        assert len(records) == 1
        record = records[0]
        assert record["status"] == "invalid"
        assert record["warnings"]
        _assert_no_absolute_path_leak(record)


class TestListProjectsSymlink:
    def test_symlink_outside_projects_dir_fails_closed(self, tmp_path):
        outside = tmp_path.parent / f"outside-{tmp_path.name}"
        outside.mkdir(exist_ok=True)
        link_path = tmp_path / "escape-link"
        try:
            link_path.symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError):
            pytest.skip("symlink creation not supported in this environment")

        records = project_manager.list_projects(projects_dir=tmp_path)

        assert len(records) == 1
        record = records[0]
        assert record["status"] in {"invalid", "warning"}
        assert record["warnings"]
        _assert_no_absolute_path_leak(record)


class TestListProjectsSorting:
    def test_valid_projects_sort_before_invalid_and_by_updated_at_desc(self, tmp_path):
        older = tmp_path / "older-project"
        newer = tmp_path / "newer-project"
        _write_project_json(
            older,
            title="Older",
            updated_at="2026-01-01T00:00:00Z",
        )
        _write_project_json(
            newer,
            title="Newer",
            updated_at="2026-06-10T00:00:00Z",
        )
        (tmp_path / "broken").mkdir()

        records = project_manager.list_projects(projects_dir=tmp_path)

        assert len(records) == 3
        assert records[0]["project_id"] == "newer-project"
        assert records[1]["project_id"] == "older-project"
        assert records[2]["status"] != "valid"


class TestListProjectsDuplicates:
    def test_duplicate_metadata_project_id_marks_records_invalid(self):
        records = [
            {
                "project_id": "folder-a",
                "status": "invalid",
                "warnings": ["project_id mismatch between folder and project.json"],
                "_metadata_project_id": "shared-id",
            },
            {
                "project_id": "folder-b",
                "status": "invalid",
                "warnings": ["project_id mismatch between folder and project.json"],
                "_metadata_project_id": "shared-id",
            },
        ]

        updated = project_manager._apply_duplicate_project_id_warnings(records)

        for record in updated:
            assert record["status"] == "invalid"
            assert any("duplicate project_id" in warning for warning in record["warnings"])


class TestLoadProjectMetadata:
    def test_valid_id_returns_metadata(self, tmp_path):
        project_dir = tmp_path / "my-project"
        _write_project_json(project_dir, title="Loaded Title")

        metadata = project_manager.load_project_metadata("my-project", projects_dir=tmp_path)

        assert metadata["project_id"] == "my-project"
        assert metadata["title"] == "Loaded Title"
        assert metadata["status"] == "valid"
        assert metadata["warnings"] == []
        _assert_no_absolute_path_leak(metadata)

    def test_unsafe_project_id_returns_warning_record(self):
        metadata = project_manager.load_project_metadata("../escape")

        assert metadata["status"] == "invalid"
        assert "unsafe project_id" in metadata["warnings"][0]
        _assert_no_absolute_path_leak(metadata)

    def test_missing_project_returns_invalid_record(self, tmp_path):
        metadata = project_manager.load_project_metadata("missing-id", projects_dir=tmp_path)

        assert metadata["status"] == "invalid"
        assert "does not exist" in metadata["warnings"][0]
        _assert_no_absolute_path_leak(metadata)

    def test_corrupt_metadata_returns_invalid_record(self, tmp_path):
        project_dir = tmp_path / "corrupt"
        _write_project_json(project_dir, raw_content="{ broken")

        metadata = project_manager.load_project_metadata("corrupt", projects_dir=tmp_path)

        assert metadata["status"] == "invalid"
        assert metadata["warnings"]
        _assert_no_absolute_path_leak(metadata)


class TestGetProjectsRoute:
    def test_get_projects_success(self, client, monkeypatch):
        fake_projects = [
            {"project_id": "alpha", "title": "Alpha", "status": "valid", "warnings": []},
            {"project_id": "beta", "title": "Beta", "status": "valid", "warnings": []},
        ]

        monkeypatch.setattr(
            main.project_manager,
            "list_projects",
            lambda: fake_projects,
        )

        response = client.get("/api/projects")

        assert response.status_code == 200
        body = response.json()
        assert body == {"projects": fake_projects, "count": 2}

    def test_get_projects_file_not_found_returns_empty_list(self, client, monkeypatch):
        def raise_file_not_found():
            raise FileNotFoundError("projects root missing")

        monkeypatch.setattr(main.project_manager, "list_projects", raise_file_not_found)

        response = client.get("/api/projects")

        assert response.status_code == 200
        assert response.json() == {"projects": [], "count": 0}

    def test_get_projects_value_error_returns_safe_400(self, client, monkeypatch):
        def raise_value_error():
            raise ValueError(
                "Project path /home/evil/projects/foo is not inside the projects directory"
            )

        monkeypatch.setattr(main.project_manager, "list_projects", raise_value_error)

        response = client.get("/api/projects")

        assert response.status_code == 400
        detail = response.json()["detail"]
        assert detail == "Unable to list projects"
        assert "/home" not in detail
        assert "\\" not in detail

    def test_get_projects_runtime_error_returns_500(self, client, monkeypatch):
        def raise_runtime_error():
            raise RuntimeError("disk failure")

        monkeypatch.setattr(main.project_manager, "list_projects", raise_runtime_error)

        response = client.get("/api/projects")

        assert response.status_code == 500
        assert response.json()["detail"] == "Failed to list projects"

    def test_get_projects_collection_route_not_shadowed(self, client, monkeypatch):
        sentinel = [
            {
                "project_id": "collection-check",
                "title": "Collection",
                "status": "valid",
                "warnings": [],
            }
        ]
        monkeypatch.setattr(main.project_manager, "list_projects", lambda: sentinel)

        response = client.get("/api/projects")

        assert response.status_code == 200
        body = response.json()
        assert "projects" in body
        assert "count" in body
        assert body["count"] == len(body["projects"])
