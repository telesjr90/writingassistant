import json
import sys
import types
from pathlib import Path


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

from backend import main


def test_scene_route_loads_empty_scene(tmp_path, monkeypatch):
    monkeypatch.setattr(main.project_manager, "PROJECTS_DIR", tmp_path)
    main.project_manager.save_scene("example", "empty_scene", "")

    assert main.get_scene("example", "empty_scene") == {"content": ""}


def test_scene_list_route_returns_markdown_scene_ids_when_metadata_exists(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(main.project_manager, "PROJECTS_DIR", tmp_path)
    main.project_manager.save_scene("example", "scene_001", "Owner-authored body.")
    main.project_manager.create_scene_metadata(
        "example",
        "scene_001",
        {"title": "Owner title", "chapter_id": "chapter_001"},
    )

    assert main.get_scenes("example") == {"scenes": ["scene_001"]}


def test_scene_list_route_lists_legacy_scenes_without_metadata_directory(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(main.project_manager, "PROJECTS_DIR", tmp_path)
    main.project_manager.save_scene("example", "scene_002", "Second owner body.")
    main.project_manager.save_scene("example", "scene_001", "First owner body.")
    metadata_dir = tmp_path / "example" / "scene_metadata"
    assert not metadata_dir.exists()

    assert main.get_scenes("example") == {"scenes": ["scene_001", "scene_002"]}
    assert not metadata_dir.exists()


def test_scene_read_route_returns_body_when_metadata_exists(tmp_path, monkeypatch):
    monkeypatch.setattr(main.project_manager, "PROJECTS_DIR", tmp_path)
    content = "# Scene One\n\nOwner-authored body."
    main.project_manager.save_scene("example", "scene_001", content)
    main.project_manager.create_scene_metadata(
        "example",
        "scene_001",
        {
            "title": "Owner title",
            "chapter_id": "chapter_001",
            "order_index": 3,
        },
    )

    assert main.get_scene("example", "scene_001") == {"content": content}
    assert "Owner title" not in main.get_scene("example", "scene_001")["content"]
    assert "chapter_001" not in main.get_scene("example", "scene_001")["content"]


def test_scene_read_route_keeps_legacy_scene_without_metadata_read_only(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(main.project_manager, "PROJECTS_DIR", tmp_path)
    content = "Owner-authored legacy scene body."
    main.project_manager.save_scene("example", "scene_001", content)
    metadata_path = tmp_path / "example" / "scene_metadata" / "scene_001.json"
    assert not metadata_path.exists()

    assert main.get_scene("example", "scene_001") == {"content": content}
    assert not metadata_path.exists()


def test_scene_route_saves_empty_scene(tmp_path, monkeypatch):
    monkeypatch.setattr(main.project_manager, "PROJECTS_DIR", tmp_path)
    update = types.SimpleNamespace(content="")

    assert main.update_scene("example", "empty_scene", update) == {"status": "saved"}
    assert main.project_manager.load_scene("example", "empty_scene") == ""


def test_scene_update_route_changes_only_explicit_body_not_metadata(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(main.project_manager, "PROJECTS_DIR", tmp_path)
    main.project_manager.save_scene("example", "scene_001", "Original owner body.")
    main.project_manager.create_scene_metadata(
        "example",
        "scene_001",
        {"title": "Owner title", "chapter_id": "chapter_001"},
    )
    metadata_path = tmp_path / "example" / "scene_metadata" / "scene_001.json"
    metadata_before = metadata_path.read_text(encoding="utf-8")
    update = types.SimpleNamespace(content="Updated owner body.")

    assert main.update_scene("example", "scene_001", update) == {"status": "saved"}
    assert main.project_manager.load_scene("example", "scene_001") == "Updated owner body."
    assert metadata_path.read_text(encoding="utf-8") == metadata_before


def test_scene_update_route_preserves_legacy_scene_without_creating_metadata(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(main.project_manager, "PROJECTS_DIR", tmp_path)
    main.project_manager.save_scene("example", "scene_001", "Original owner body.")
    metadata_path = tmp_path / "example" / "scene_metadata" / "scene_001.json"
    update = types.SimpleNamespace(content="Explicit updated owner body.")
    assert not metadata_path.exists()

    assert main.update_scene("example", "scene_001", update) == {"status": "saved"}
    assert main.project_manager.load_scene("example", "scene_001") == (
        "Explicit updated owner body."
    )
    assert not metadata_path.exists()


def test_scene_update_route_preserves_metadata_safe_identity(tmp_path, monkeypatch):
    monkeypatch.setattr(main.project_manager, "PROJECTS_DIR", tmp_path)
    main.project_manager.save_scene("example", "scene_001", "Original owner body.")
    main.project_manager.create_scene_metadata(
        "example",
        "scene_001",
        {"title": "Owner title", "chapter_id": "chapter_001"},
    )
    update = types.SimpleNamespace(content="Updated owner body.")

    assert main.update_scene("example", "scene_001", update) == {"status": "saved"}

    metadata = main.project_manager.load_scene_metadata("example", "scene_001")
    assert metadata["project_id"] == "example"
    assert metadata["scene_id"] == "scene_001"
    assert metadata["content_path"] == "scenes/scene_001.md"
    assert main.project_manager.load_scene("example", "scene_001") == "Updated owner body."


def test_scene_route_does_not_guard_owner_authored_scene_text(tmp_path, monkeypatch):
    monkeypatch.setattr(main.project_manager, "PROJECTS_DIR", tmp_path)
    content = (
        'The note on the desk said "continue this chapter," but nobody treated it '
        "as an instruction to the assistant."
    )
    update = types.SimpleNamespace(content=content)

    assert main.update_scene("example", "scene_001", update) == {"status": "saved"}
    assert main.project_manager.load_scene("example", "scene_001") == content


def test_scene_route_returns_safe_missing_scene_error(tmp_path, monkeypatch):
    monkeypatch.setattr(main.project_manager, "PROJECTS_DIR", tmp_path)
    metadata_dir = tmp_path / "example" / "scene_metadata"
    metadata_dir.mkdir(parents=True)
    (metadata_dir / "other_scene.json").write_text(
        json.dumps({"scene_id": "other_scene"}),
        encoding="utf-8",
    )

    try:
        main.get_scene("example", "missing_scene")
    except main.HTTPException as exc:
        assert exc.status_code == 404
        assert exc.detail == "Scene not found"
    else:
        raise AssertionError("missing scene should raise HTTPException")

    assert not (tmp_path / "example" / "scenes" / "missing_scene.md").exists()
    assert not (metadata_dir / "missing_scene.json").exists()
