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


def test_scene_route_saves_empty_scene(tmp_path, monkeypatch):
    monkeypatch.setattr(main.project_manager, "PROJECTS_DIR", tmp_path)
    update = types.SimpleNamespace(content="")

    assert main.update_scene("example", "empty_scene", update) == {"status": "saved"}
    assert main.project_manager.load_scene("example", "empty_scene") == ""


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

    try:
        main.get_scene("example", "missing_scene")
    except main.HTTPException as exc:
        assert exc.status_code == 404
        assert exc.detail == "Scene not found"
    else:
        raise AssertionError("missing scene should raise HTTPException")
