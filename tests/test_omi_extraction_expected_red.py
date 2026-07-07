import sys
import types
from pathlib import Path


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

RAW_IDEA_WITH_EVIDENCE = "\n".join(
    [
        "Character: Test Character Alpha.",
        "Location: Test Location Beta.",
        "Organization: Test Group Gamma.",
        "Object: Test Object Delta.",
        "Timeline event: Test Event Epsilon occurs on day 12.",
        "Relationship: Test Character Alpha distrusts Test Character Zeta.",
        "Plot thread: find why Test Group Gamma hid Test Object Delta.",
        "Story fact: Test Object Delta is stored at Test Location Beta.",
        "Open question: who ordered Test Event Epsilon?",
        "Storyform context: owner marks broken trust as the central inequity note.",
    ]
)

EXPECTED_TYPES = {
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


def _require_extraction_route():
    assert hasattr(main, "extract_omi_candidates"), (
        "Expected-red: backend must expose extract_omi_candidates for "
        "POST /api/projects/{project_name}/omi/extractions."
    )
    return main.extract_omi_candidates


def _assert_candidate_contract(candidate: dict) -> None:
    assert candidate["candidate_type"] in EXPECTED_TYPES
    assert candidate.get("label") or candidate.get("name")
    assert candidate.get("extracted_claim")
    assert candidate.get("evidence")
    assert candidate.get("provenance")
    assert candidate.get("status") in {
        "candidate",
        "review_pending",
        "owner_review",
        "candidate_review_pending",
    }
    assert candidate.get("owner_decision", {}).get("decision") == "pending"

    provenance = candidate["provenance"]
    assert provenance.get("source_type") in {
        "omi_raw_idea",
        "owner_input",
        "raw_idea_extraction",
    }
    assert provenance.get("model") is None
    assert provenance.get("prompt_id") is None
    assert provenance.get("extractor_name") or provenance.get("tool")

    support_keys = {"confidence", "support_strength"}
    if support_keys.intersection(candidate):
        support_label = str(
            candidate.get("support_label")
            or candidate.get("support_strength_label")
            or candidate.get("confidence_label")
            or ""
        ).lower()
        assert "support" in support_label
        assert "truth" not in support_label


def _assert_extraction_result_contract(result: dict) -> None:
    assert result["extraction_status"] == "succeeded"
    assert result["source_locator"]
    assert result["candidates"]
    observed_types = {candidate["candidate_type"] for candidate in result["candidates"]}
    assert EXPECTED_TYPES.issubset(observed_types)
    for candidate in result["candidates"]:
        _assert_candidate_contract(candidate)


def test_omi_raw_idea_extraction_route_and_request_contract_expected_red() -> None:
    source = MAIN_SOURCE.read_text(encoding="utf-8")

    assert "class OMIExtractionRequest" in source
    assert "/api/projects/{project_name}/omi/extractions" in source
    assert "def extract_omi_candidates" in source
    assert "raw_idea" in source
    assert "source_idea_id" in source
    assert "persist_candidates" in source
    assert hasattr(project_manager, "extract_omi_candidates_from_raw_idea")


def test_raw_idea_extraction_returns_evidence_backed_candidates_expected_red(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setattr(main.project_manager, "PROJECTS_DIR", tmp_path)

    def fail_story_check(*args, **kwargs):
        raise AssertionError("OMI raw idea extraction MVP must not call model paths")

    monkeypatch.setattr(main._analysis_module, "run_story_check", fail_story_check)

    idea = main.create_omi_idea(
        "example",
        _payload(raw_idea=RAW_IDEA_WITH_EVIDENCE, provenance=None),
    )
    extract_omi_candidates = _require_extraction_route()

    result = extract_omi_candidates(
        "example",
        _payload(
            raw_idea=RAW_IDEA_WITH_EVIDENCE,
            source_idea_id=idea["idea_id"],
            persist_candidates=False,
        ),
    )

    assert result["source_idea_id"] == idea["idea_id"]
    _assert_extraction_result_contract(result)
    assert main.get_omi("example")["index"]["candidate_ids"] == []


def test_empty_raw_idea_extraction_fails_closed_without_shells_expected_red(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setattr(main.project_manager, "PROJECTS_DIR", tmp_path)
    extract_omi_candidates = _require_extraction_route()

    result = extract_omi_candidates(
        "example",
        _payload(raw_idea="   ", source_idea_id=None, persist_candidates=True),
    )

    assert result["extraction_status"] in {"empty", "fail_closed"}
    assert result["explanation"]
    assert result["candidates"] == []
    assert main.get_omi("example")["index"]["candidate_ids"] == []
    candidate_dir = tmp_path / "example" / "omi" / "candidates"
    assert not candidate_dir.exists() or list(candidate_dir.glob("*.json")) == []


def test_persisted_extracted_candidates_remain_candidate_first_expected_red(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setattr(main.project_manager, "PROJECTS_DIR", tmp_path)

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

    idea = main.create_omi_idea(
        "example",
        _payload(raw_idea=RAW_IDEA_WITH_EVIDENCE, provenance=None),
    )
    extract_omi_candidates = _require_extraction_route()

    result = extract_omi_candidates(
        "example",
        _payload(
            raw_idea=RAW_IDEA_WITH_EVIDENCE,
            source_idea_id=idea["idea_id"],
            persist_candidates=True,
        ),
    )

    _assert_extraction_result_contract(result)
    summary = main.get_omi("example")
    assert len(summary["candidates"]) == len(result["candidates"])
    assert summary["promotions"] == []

    for candidate in summary["candidates"]:
        assert candidate["status"] not in {"approved", "promoted", "canon"}
        assert candidate.get("owner_decision", {}).get("decision") == "pending"
        assert candidate.get("promotion_status", {}).get("eligible") is False

    for path, content in truth_files.items():
        assert path.read_text(encoding="utf-8") == content

    assert not hasattr(main, "apply_omi_promotion")
