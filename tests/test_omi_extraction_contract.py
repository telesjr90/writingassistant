import sys
import types
from pathlib import Path

import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


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

from backend import main, project_manager


REPO_ROOT = Path(__file__).resolve().parents[1]
MAIN_SOURCE = REPO_ROOT / "backend" / "main.py"

EXPECTED_EXTRACTED_TYPES = {
    "character",
    "location",
    "timeline_event",
    "relationship",
    "organization",
    "object",
    "plot_thread",
    "story_fact",
    "open_question",
    "storyform_context",
}


def _payload(**kwargs):
    return types.SimpleNamespace(**kwargs)


def test_backend_extraction_contract_symbols_and_allowed_types_exist() -> None:
    source = MAIN_SOURCE.read_text(encoding="utf-8")

    assert "class OMIExtractionRequest" in source
    assert "class OMIExtractionResponse" in source
    assert "class OMIExtractedCandidate" in source
    assert "/api/projects/{project_name}/omi/extractions" in source
    assert "def extract_omi_candidates" in source
    assert hasattr(project_manager, "extract_omi_candidates_from_raw_idea")
    assert project_manager.OMI_EXTRACTED_CANDIDATE_TYPES == EXPECTED_EXTRACTED_TYPES


def test_empty_extraction_fails_closed_without_candidate_shells(tmp_path, monkeypatch):
    monkeypatch.setattr(main.project_manager, "PROJECTS_DIR", tmp_path)

    result = main.extract_omi_candidates(
        "example",
        _payload(raw_idea="   ", source_idea_id=None, persist_candidates=True, provenance=None),
    )

    assert result["extraction_status"] == "empty"
    assert result["status"] == "empty"
    assert result["explanation"]
    assert result["candidates"] == []
    assert result["persisted_candidate_ids"] == []
    assert result["persistence_status"] == "no_candidates_persisted"
    assert result["safety"]["no_memory_canon_mutation"] is True
    assert result["safety"]["no_promotion_records_created"] is True
    assert main.get_omi("example")["index"]["candidate_ids"] == []

    candidate_dir = tmp_path / "example" / "omi" / "candidates"
    assert not candidate_dir.exists() or list(candidate_dir.glob("*.json")) == []


def test_nonempty_extraction_contract_succeeds_for_explicit_marker_t004(tmp_path, monkeypatch):
    monkeypatch.setattr(main.project_manager, "PROJECTS_DIR", tmp_path)

    def fail_story_check(*args, **kwargs):
        raise AssertionError("OMI extraction contract must not call Story Check")

    monkeypatch.setattr(main._analysis_module, "run_story_check", fail_story_check)

    project_dir = tmp_path / "example"
    scenes_dir = project_dir / "scenes"
    scenes_dir.mkdir(parents=True)
    truth_files = {
        project_dir / "bible.json": '{"characters": []}\n',
        project_dir / "storyform.json": '{"schema_version": "ncp-0.1"}\n',
        project_dir / "owner_memory.json": '{"notes": []}\n',
        scenes_dir / "scene_001.md": "Owner-authored fixture text.",
    }
    for path, content in truth_files.items():
        path.write_text(content, encoding="utf-8")

    raw_idea = "Character: Test Entity Alpha."
    idea = main.create_omi_idea(
        "example",
        _payload(raw_idea=raw_idea, provenance=None),
    )

    result = main.extract_omi_candidates(
        "example",
        _payload(
            raw_idea=raw_idea,
            source_idea_id=idea["idea_id"],
            persist_candidates=True,
            provenance=None,
        ),
    )

    assert result["extraction_status"] == "succeeded"
    assert result["source_idea_id"] == idea["idea_id"]
    assert result["source_locator"] == f"omi/ideas/{idea['idea_id']}.json#raw_idea"
    assert result["candidate_count"] == 1
    assert result["persistence_status"] == "persisted"
    assert len(result["persisted_candidate_ids"]) == 1
    candidate = result["candidates"][0]
    assert candidate["candidate_type"] == "character"
    assert candidate["label"] == "Test Entity Alpha"
    assert candidate["name"] == "Test Entity Alpha"
    assert candidate["extracted_claim"] == "Test Entity Alpha."
    assert candidate["owner_decision"]["decision"] == "pending"
    assert candidate["status"] == "candidate_review_pending"
    assert candidate["support_label"] == project_manager.OMI_EXTRACTION_SUPPORT_LABEL
    evidence = candidate["evidence"][0]
    assert evidence["source_excerpt"] == raw_idea
    assert evidence["source_locator"].startswith(
        f"omi/ideas/{idea['idea_id']}.json#raw_idea:L1:C0-"
    )
    assert evidence["line_number"] == 1
    assert evidence["char_start"] == 0
    assert evidence["owner_authored"] is True
    assert result["safety"]["no_memory_canon_mutation"] is True
    assert result["safety"]["no_promotion_records_created"] is True
    summary = main.get_omi("example")
    assert summary["index"]["candidate_ids"] == result["persisted_candidate_ids"]
    assert main.get_omi("example")["promotions"] == []
    stored_candidate = summary["candidates"][0]
    assert stored_candidate["candidate_type"] == "project_bible_candidate"
    assert stored_candidate["status"] == "candidate"
    assert stored_candidate["owner_decision"]["decision"] == "pending"
    assert stored_candidate["promotion_status"]["eligible"] is False
    assert stored_candidate["candidate_content"]["candidate_first"] is True
    assert stored_candidate["candidate_content"]["canon"] is False
    for path, content in truth_files.items():
        assert path.read_text(encoding="utf-8") == content


def test_nonempty_extraction_without_supported_markers_fails_closed_without_writes(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(main.project_manager, "PROJECTS_DIR", tmp_path)

    raw_idea = "A loose owner note without an explicit extraction marker."
    result = main.extract_omi_candidates(
        "example",
        _payload(
            raw_idea=raw_idea,
            source_idea_id=None,
            persist_candidates=True,
            provenance=None,
        ),
    )

    assert result["extraction_status"] == "fail_closed"
    assert "No supported explicit OMI extraction markers" in result["explanation"]
    assert result["candidates"] == []
    assert result["persisted_candidate_ids"] == []
    assert result["persistence_status"] == "no_candidates_persisted"
    assert main.get_omi("example")["index"]["candidate_ids"] == []


def test_extracted_candidate_schema_validation_is_evidence_backed_and_pending():
    candidate = {
        "candidate_type": "character",
        "label": "Test Entity Alpha",
        "extracted_claim": "The raw idea names Test Entity Alpha as a character candidate.",
        "evidence": [
            {
                "source_excerpt": "Character: Test Entity Alpha.",
                "source_locator": "request.raw_idea:0-29",
            }
        ],
        "provenance": {
            "source_type": "omi_raw_idea",
            "source_idea_id": "idea_123",
            "extractor_name": "deterministic_fixture",
            "model": None,
            "prompt_id": None,
        },
        "status": "candidate_review_pending",
        "owner_decision": {"decision": "pending"},
        "support_strength": 0.5,
        "support_label": project_manager.OMI_EXTRACTION_SUPPORT_LABEL,
    }

    validated = project_manager.validate_omi_extracted_candidate(candidate)

    assert validated["candidate_type"] == "character"
    assert validated["owner_decision"]["decision"] == "pending"
    assert validated["owner_decision"]["approved"] is False

    invalid_type = dict(candidate, candidate_type="scene_prose")
    with pytest.raises(ValueError, match="candidate_type"):
        project_manager.validate_omi_extracted_candidate(invalid_type)

    approved = dict(candidate, owner_decision={"decision": "approve", "approval_confirmed": True})
    with pytest.raises(ValueError, match="pending"):
        project_manager.validate_omi_extracted_candidate(approved)
