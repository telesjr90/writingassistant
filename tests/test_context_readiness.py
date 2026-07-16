from __future__ import annotations

import inspect
import json
import sys
import types
from pathlib import Path

import pytest


class _FakeFastAPI:
    def __init__(self, *args, **kwargs):
        pass

    def add_middleware(self, *args, **kwargs):
        return None

    def include_router(self, *args, **kwargs):
        return None

    def add_api_route(self, *args, **kwargs):
        return None

    def middleware(self, *args, **kwargs):
        return self._decorator

    def get(self, *args, **kwargs):
        return self._decorator

    def post(self, *args, **kwargs):
        return self._decorator

    def patch(self, *args, **kwargs):
        return self._decorator

    def put(self, *args, **kwargs):
        return self._decorator

    @staticmethod
    def _decorator(func):
        return func


class _FakeAPIRouter(_FakeFastAPI):
    pass


class _FakeHTTPException(Exception):
    def __init__(self, status_code, detail):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


class _FakeBaseModel:
    pass


fake_fastapi = types.ModuleType("fastapi")
fake_fastapi.APIRouter = _FakeAPIRouter
fake_fastapi.FastAPI = _FakeFastAPI
fake_fastapi.HTTPException = _FakeHTTPException
fake_fastapi.Request = object
fake_middleware = types.ModuleType("fastapi.middleware")
fake_cors = types.ModuleType("fastapi.middleware.cors")
fake_cors.CORSMiddleware = object
fake_responses = types.ModuleType("fastapi.responses")
fake_responses.JSONResponse = dict
fake_pydantic = types.ModuleType("pydantic")
fake_pydantic.BaseModel = _FakeBaseModel

sys.modules.setdefault("fastapi", fake_fastapi)
sys.modules.setdefault("fastapi.middleware", fake_middleware)
sys.modules.setdefault("fastapi.middleware.cors", fake_cors)
sys.modules.setdefault("fastapi.responses", fake_responses)
sys.modules.setdefault("pydantic", fake_pydantic)

from backend import context_readiness, main, project_manager
from backend.storyform import Storyform, _load_schema_from_repo_knowledge


def _create_project(tmp_path: Path, project_id: str = "demo") -> Path:
    project_manager.create_project("Demo", projects_dir=tmp_path)
    return tmp_path / project_id


def _tree_bytes(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _report(tmp_path: Path, monkeypatch, project_id: str = "demo") -> dict:
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)
    return context_readiness.build_project_context_readiness(project_id)


def test_absent_optional_resources_return_normal_stable_contract(tmp_path, monkeypatch):
    project_path = _create_project(tmp_path)
    before = _tree_bytes(project_path)

    first = _report(tmp_path, monkeypatch)
    second = _report(tmp_path, monkeypatch)

    assert first == second
    assert first["schema_version"] == "project_context_readiness.v1"
    assert first["project_id"] == "demo"
    assert first["status_vocabulary"] == [
        "absent",
        "invalid",
        "not_applicable",
        "ready",
        "unavailable",
    ]
    assert first["resource_order"] == ["bible", "storyform", "storyform_context"]
    assert first["resources"]["bible"]["state"] == "absent"
    assert first["resources"]["bible"]["reason_code"] == "bible_absent"
    assert first["resources"]["storyform"]["state"] == "absent"
    assert first["resources"]["storyform"]["reason_code"] == "storyform_absent"
    assert first["resources"]["storyform_context"]["state"] == "unavailable"
    assert (
        first["resources"]["storyform_context"]["reason_code"]
        == "storyform_context_storyform_absent"
    )
    assert main.get_project_context_readiness("demo") == first
    assert _tree_bytes(project_path) == before


def test_bible_present_valid_invalid_and_unsupported_encoding(tmp_path, monkeypatch):
    project_path = _create_project(tmp_path)
    bible_path = project_path / "bible.json"
    bible_path.write_text(json.dumps({"characters": []}), encoding="utf-8")

    ready = _report(tmp_path, monkeypatch)["resources"]["bible"]
    assert (ready["exists"], ready["structurally_valid"], ready["ready"]) == (
        True,
        True,
        True,
    )
    assert ready["state"] == "ready"
    assert ready["reason_code"] is None
    assert ready["source_locator"] == "bible.json"

    bible_path.write_text("{broken", encoding="utf-8")
    malformed_bytes = bible_path.read_bytes()
    malformed = _report(tmp_path, monkeypatch)["resources"]["bible"]
    assert malformed["state"] == "invalid"
    assert malformed["reason_code"] == "bible_malformed_json"
    assert bible_path.read_bytes() == malformed_bytes

    bible_path.write_bytes(b"\xff\xfe")
    unreadable_bytes = bible_path.read_bytes()
    unreadable = _report(tmp_path, monkeypatch)["resources"]["bible"]
    assert unreadable["state"] == "invalid"
    assert unreadable["reason_code"] == "bible_unsupported_encoding"
    assert all(str(tmp_path) not in detail for detail in unreadable["diagnostics"])
    assert bible_path.read_bytes() == unreadable_bytes


def test_storyform_valid_malformed_unsupported_and_validator_failure(tmp_path, monkeypatch):
    project_path = _create_project(tmp_path)
    storyform_path = project_path / "storyform.json"
    valid = Storyform.from_questionnaire({}).to_dict()
    storyform_path.write_text(json.dumps(valid), encoding="utf-8")

    ready = _report(tmp_path, monkeypatch)["resources"]["storyform"]
    assert ready["state"] == "ready"
    assert ready["structurally_valid"] is True

    storyform_path.write_text("{broken", encoding="utf-8")
    malformed = _report(tmp_path, monkeypatch)["resources"]["storyform"]
    assert malformed["state"] == "invalid"
    assert malformed["reason_code"] == "storyform_malformed_json"

    storyform_path.write_text("[]", encoding="utf-8")
    unsupported = _report(tmp_path, monkeypatch)["resources"]["storyform"]
    assert unsupported["reason_code"] == "storyform_unsupported_structure"

    invalid = {"story": {"title": "Missing required fields"}}
    storyform_path.write_text(json.dumps(invalid), encoding="utf-8")
    before = storyform_path.read_bytes()
    failed_validation = _report(tmp_path, monkeypatch)["resources"]["storyform"]
    assert failed_validation["state"] == "invalid"
    assert failed_validation["reason_code"] == "storyform_schema_invalid"
    assert storyform_path.read_bytes() == before


def test_storyform_context_ready_and_tracks_storyform_failure_causes(tmp_path, monkeypatch):
    project_path = _create_project(tmp_path)
    storyform_path = project_path / "storyform.json"
    storyform_path.write_text(
        json.dumps(Storyform.from_questionnaire({}).to_dict()),
        encoding="utf-8",
    )
    before = _tree_bytes(project_path)

    ready = _report(tmp_path, monkeypatch)["resources"]["storyform_context"]
    assert ready["resource_type"] == "derived_context"
    assert ready["state"] == "ready"
    assert ready["exists"] is True
    assert ready["structurally_valid"] is True
    assert ready["ready"] is True
    assert _tree_bytes(project_path) == before

    storyform_path.unlink()
    absent = _report(tmp_path, monkeypatch)["resources"]["storyform_context"]
    assert absent["reason_code"] == "storyform_context_storyform_absent"

    storyform_path.write_text("{}", encoding="utf-8")
    invalid = _report(tmp_path, monkeypatch)["resources"]["storyform_context"]
    assert invalid["reason_code"] == "storyform_context_storyform_invalid"


def test_storyform_context_reports_missing_deterministic_validator_input(
    tmp_path, monkeypatch
):
    project_path = _create_project(tmp_path)
    (project_path / "storyform.json").write_text(
        json.dumps(Storyform.from_questionnaire({}).to_dict()),
        encoding="utf-8",
    )
    missing_schema = tmp_path / "missing-storyform-schema.md"
    _load_schema_from_repo_knowledge.cache_clear()
    monkeypatch.setattr(Storyform, "SCHEMA_DOC_PATH", missing_schema)

    report = _report(tmp_path, monkeypatch)

    assert report["resources"]["storyform"]["state"] == "unavailable"
    assert (
        report["resources"]["storyform"]["reason_code"]
        == "storyform_validation_dependency_unavailable"
    )
    assert report["resources"]["storyform_context"]["state"] == "unavailable"
    assert (
        report["resources"]["storyform_context"]["reason_code"]
        == "storyform_context_validation_dependency_unavailable"
    )
    _load_schema_from_repo_knowledge.cache_clear()


def test_unsafe_locator_and_genuine_request_failures_remain_transport_failures(
    tmp_path, monkeypatch
):
    project_path = _create_project(tmp_path)
    outside = tmp_path / "outside.json"
    outside.write_text("{}", encoding="utf-8")
    (project_path / "bible.json").symlink_to(outside)
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)

    with pytest.raises(main.HTTPException) as unsafe:
        main.get_project_context_readiness("demo")
    assert unsafe.value.status_code == 400
    assert str(tmp_path) not in unsafe.value.detail

    with pytest.raises(main.HTTPException) as invalid_id:
        main.get_project_context_readiness("../outside")
    assert invalid_id.value.status_code == 400

    with pytest.raises(main.HTTPException) as missing_project:
        main.get_project_context_readiness("missing")
    assert missing_project.value.status_code == 404

    monkeypatch.setattr(
        context_readiness,
        "_resolve_project_directory",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(PermissionError("secret path")),
    )
    with pytest.raises(main.HTTPException) as permission_failure:
        main.get_project_context_readiness("demo")
    assert permission_failure.value.status_code == 500
    assert "secret path" not in permission_failure.value.detail


def test_contract_schema_is_stable_bounded_and_does_not_leak_absolute_paths(
    tmp_path, monkeypatch
):
    _create_project(tmp_path)
    report = _report(tmp_path, monkeypatch)
    expected_fields = {
        "resource_id",
        "resource_type",
        "exists",
        "structurally_valid",
        "ready",
        "state",
        "reason_code",
        "diagnostics",
        "source_locator",
    }
    for resource_id, result in report["resources"].items():
        assert set(result) == expected_fields
        assert result["resource_id"] == resource_id
        assert len(result["diagnostics"]) <= 3
        assert not Path(result["source_locator"]).is_absolute()
    assert str(tmp_path) not in json.dumps(report)


def test_readiness_contract_has_no_runtime_model_or_mutation_surface():
    source = inspect.getsource(context_readiness)
    forbidden = (
        "run_story_check(",
        "requests.",
        "subprocess.",
        "create_omi_candidate(",
        "create_omi_promotion(",
        "persist_candidate(",
        "apply_omi_promotion(",
        "apply_promotion(",
        "save_bible(",
        "save_storyform_json(",
        "write_memory(",
        "save_memory(",
        "write_canon(",
        "save_canon(",
        "run_ollama(",
        "run_booknlp(",
        "run_spacy(",
        "run_ncp(",
        "run_subtxt(",
        "run_dramatica_flow(",
    )
    assert all(marker not in source for marker in forbidden)

    assert context_readiness.build_project_context_readiness.__doc__
