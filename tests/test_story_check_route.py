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


def _patch_story_check(monkeypatch, payload):
    def fake_run_story_check(project_name, scene_id):
        assert project_name == "example"
        assert scene_id == "scene_001"
        return payload

    monkeypatch.setattr(main.analysis_engine, "run_story_check", fake_run_story_check)


def test_story_check_route_returns_minimal_report(monkeypatch):
    payload = {
        "coherence_score": 6,
        "warnings": ["[Factual] Missing approved context."],
        "suggestions": ["What evidence is missing?"],
    }
    _patch_story_check(monkeypatch, payload)

    body = main.story_check("example", "scene_001")

    assert body == payload
    assert {"coherence_score", "warnings", "suggestions"} <= set(body)


def test_story_check_route_returns_rich_report(monkeypatch):
    payload = {
        "task": "story_check",
        "coherence_score": 7,
        "throughline_alignment": {
            "overall_story": {"present": True, "evidence": ["source span"], "concerns": []},
            "main_character": {"present": False, "evidence": [], "concerns": ["Missing MC evidence."]},
            "influence_character": {"present": False, "evidence": [], "concerns": ["Missing IC evidence."]},
            "relationship_story": {"present": False, "evidence": [], "concerns": ["Missing RS evidence."]},
        },
        "theme_drift": {"status": "insufficient_evidence", "reason": "Approved Issue is absent."},
        "character_consistency": {
            "status": "insufficient_evidence",
            "reason": "Approved character context is incomplete.",
        },
        "warnings": [],
        "suggestions": ["What owner-approved evidence is missing?"],
        "insufficient_evidence": ["Influence Character evidence is not supplied."],
    }
    _patch_story_check(monkeypatch, payload)

    body = main.story_check("example", "scene_001")

    assert body["task"] == "story_check"
    assert body["throughline_alignment"] == payload["throughline_alignment"]
    assert body["insufficient_evidence"] == payload["insufficient_evidence"]


def test_story_check_route_returns_fallback_report(monkeypatch):
    payload = {
        "task": "story_check",
        "coherence_score": 0,
        "warnings": ["[Factual] Failed to parse LLM response"],
        "suggestions": [],
        "insufficient_evidence": ["A valid JSON Story Check response was not available."],
        "diagnostics": {
            "task": "story_check",
            "schema_valid": False,
            "parser_warning": "Failed to parse LLM response",
            "insufficient_evidence": ["A valid JSON Story Check response was not available."],
        },
        "raw_diagnostics": {"raw_content": "not json"},
    }
    _patch_story_check(monkeypatch, payload)

    body = main.story_check("example", "scene_001")

    assert body["coherence_score"] == 0
    assert body["diagnostics"]["schema_valid"] is False
    assert body["raw_diagnostics"] == {"raw_content": "not json"}


def test_story_check_route_allows_missing_rich_fields_and_unknown_fields(monkeypatch):
    payload = {
        "task": "story_check",
        "coherence_score": 4,
        "warnings": [],
        "suggestions": [],
        "diagnostics": {"schema_valid": False},
        "unknown_future_field": {"preserved": True},
    }
    _patch_story_check(monkeypatch, payload)

    body = main.story_check("example", "scene_001")

    assert body["diagnostics"] == {"schema_valid": False}
    assert body["unknown_future_field"] == {"preserved": True}


def test_story_check_route_returns_error_shaped_report(monkeypatch):
    payload = {"error": "Story check failed."}
    _patch_story_check(monkeypatch, payload)

    body = main.story_check("example", "scene_001")

    assert body == payload


def test_story_check_route_returns_mock_mode_output_without_ollama(monkeypatch):
    monkeypatch.setenv("ANALYSIS_MODE", "mock")

    def fail_post(*args, **kwargs):
        raise AssertionError("mock route must not call Ollama")

    monkeypatch.setattr(main.analysis_engine.requests, "post", fail_post)

    body = main.story_check("example", "scene_001")

    assert body["task"] == "story_check"
    assert body["diagnostics"]["analysis_mode"] == "mock"
    assert body["diagnostics"]["schema_valid"] is True
    assert body["throughline_alignment"]["influence_character"]["present"] is False
    assert body["throughline_alignment"]["relationship_story"]["present"] is False
