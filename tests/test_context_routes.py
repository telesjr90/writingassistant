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
from backend.storyform import Storyform


def test_bible_routes_load_and_save_json(tmp_path, monkeypatch):
    monkeypatch.setattr(main.project_manager, "PROJECTS_DIR", tmp_path)
    original = {"characters": [{"name": "prince"}]}
    main.project_manager.save_bible("example", original)

    assert main.get_bible("example") == original

    updated = {"characters": [], "unresolved": {"main_character": "unresolved"}}
    assert main.update_bible("example", updated) == {"status": "saved"}
    assert main.project_manager.load_bible("example") == updated


def test_bible_route_rejects_non_object_without_overwriting(tmp_path, monkeypatch):
    monkeypatch.setattr(main.project_manager, "PROJECTS_DIR", tmp_path)
    original = {"characters": [{"name": "princess"}]}
    main.project_manager.save_bible("example", original)

    try:
        main.update_bible("example", [])
    except main.HTTPException as exc:
        assert exc.status_code == 400
        assert "JSON object" in exc.detail
    else:
        raise AssertionError("non-object bible payload should raise HTTPException")

    assert main.project_manager.load_bible("example") == original


def test_storyform_routes_load_save_and_refresh_context(tmp_path, monkeypatch):
    monkeypatch.setattr(main.project_manager, "PROJECTS_DIR", tmp_path)
    storyform = Storyform.from_questionnaire({}).to_dict()
    main.project_manager.save_storyform_json("example", storyform)

    assert main.get_storyform("example") == storyform
    assert main.update_storyform("example", storyform) == {"status": "saved"}

    context = main.get_storyform_context("example")
    assert "Story: Quest for the Ember Crown" in context["context"]
    assert "Throughlines:" in context["context"]


def test_storyform_route_rejects_invalid_json_without_overwriting(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(main.project_manager, "PROJECTS_DIR", tmp_path)
    storyform = Storyform.from_questionnaire({}).to_dict()
    main.project_manager.save_storyform_json("example", storyform)
    storyform_path = tmp_path / "example" / "storyform.json"
    original_text = storyform_path.read_text(encoding="utf-8")

    try:
        main.update_storyform("example", {"story": {"title": "Invalid"}})
    except main.HTTPException as exc:
        assert exc.status_code == 400
    else:
        raise AssertionError("invalid storyform should raise HTTPException")

    assert storyform_path.read_text(encoding="utf-8") == original_text


def test_context_routes_return_safe_missing_file_errors(tmp_path, monkeypatch):
    monkeypatch.setattr(main.project_manager, "PROJECTS_DIR", tmp_path)

    for route in [main.get_bible, main.get_storyform, main.get_storyform_context]:
        try:
            route("example")
        except main.HTTPException as exc:
            assert exc.status_code == 404
        else:
            raise AssertionError("missing context file should raise HTTPException")


def test_context_routes_reject_unsafe_project_names(tmp_path, monkeypatch):
    monkeypatch.setattr(main.project_manager, "PROJECTS_DIR", tmp_path)

    try:
        main.update_bible("../outside", {})
    except main.HTTPException as exc:
        assert exc.status_code == 400
    else:
        raise AssertionError("unsafe project name should raise HTTPException")
