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


def _payload(**kwargs):
    return types.SimpleNamespace(**kwargs)


def test_omi_routes_create_and_list_ideas(tmp_path, monkeypatch):
    monkeypatch.setattr(main.project_manager, "PROJECTS_DIR", tmp_path)

    idea = main.create_omi_idea(
        "example",
        _payload(raw_idea="Owner-authored structural planning note.", provenance=None),
    )
    summary = main.get_omi("example")

    assert idea["status"] == "draft"
    assert idea["raw_idea"] == "Owner-authored structural planning note."
    assert summary["index"]["idea_ids"] == [idea["idea_id"]]
    assert summary["ideas"][0]["idea_id"] == idea["idea_id"]
    assert summary["candidates"] == []
    assert main.get_omi_idea("example", idea["idea_id"]) == idea


def test_omi_routes_create_and_get_candidate(tmp_path, monkeypatch):
    monkeypatch.setattr(main.project_manager, "PROJECTS_DIR", tmp_path)
    idea = main.create_omi_idea(
        "example",
        _payload(raw_idea="Capture candidate-only context.", provenance=None),
    )

    candidate = main.create_omi_candidate(
        "example",
        _payload(
            idea_id=idea["idea_id"],
            candidate_type="storyform_context_candidate",
            candidate_content={"throughline_note": "Unresolved until owner review."},
            destination="storyform_context_candidate",
            provenance=None,
            evidence=[],
        ),
    )
    summary = main.get_omi("example")

    assert candidate["status"] == "candidate"
    assert candidate["promotion_status"]["eligible"] is False
    assert summary["index"]["candidate_ids"] == [candidate["candidate_id"]]
    assert summary["candidates"][0]["candidate_id"] == candidate["candidate_id"]
    assert main.get_omi_candidate("example", candidate["candidate_id"]) == candidate


def test_omi_idea_route_rejects_empty_raw_idea(tmp_path, monkeypatch):
    monkeypatch.setattr(main.project_manager, "PROJECTS_DIR", tmp_path)

    try:
        main.create_omi_idea("example", _payload(raw_idea=" ", provenance=None))
    except main.HTTPException as exc:
        assert exc.status_code == 400
        assert "raw_idea" in exc.detail
    else:
        raise AssertionError("empty OMI raw idea should raise HTTPException")


def test_omi_candidate_route_rejects_unknown_idea(tmp_path, monkeypatch):
    monkeypatch.setattr(main.project_manager, "PROJECTS_DIR", tmp_path)

    try:
        main.create_omi_candidate(
            "example",
            _payload(
                idea_id="idea_missing",
                candidate_type="planning_note",
                candidate_content={"summary": "Candidate-only context."},
                destination="planning_notes",
                provenance=None,
                evidence=[],
            ),
        )
    except main.HTTPException as exc:
        assert exc.status_code == 404
    else:
        raise AssertionError("unknown idea_id should raise HTTPException")


def test_omi_candidate_route_rejects_invalid_type_and_destination(tmp_path, monkeypatch):
    monkeypatch.setattr(main.project_manager, "PROJECTS_DIR", tmp_path)
    idea = main.create_omi_idea(
        "example",
        _payload(raw_idea="Owner-authored idea.", provenance=None),
    )

    for candidate_type, destination in [
        ("dialogue", "planning_notes"),
        ("planning_note", "scene_prose"),
        ("planning_note", "rewrite"),
        ("planning_note", "continuation"),
    ]:
        try:
            main.create_omi_candidate(
                "example",
                _payload(
                    idea_id=idea["idea_id"],
                    candidate_type=candidate_type,
                    candidate_content={"summary": "Candidate-only context."},
                    destination=destination,
                    provenance=None,
                    evidence=[],
                ),
            )
        except main.HTTPException as exc:
            assert exc.status_code == 400
        else:
            raise AssertionError("invalid candidate fields should raise HTTPException")


def test_omi_routes_reject_unsafe_project_and_record_names(tmp_path, monkeypatch):
    monkeypatch.setattr(main.project_manager, "PROJECTS_DIR", tmp_path)
    idea = main.create_omi_idea(
        "example",
        _payload(raw_idea="Safe idea.", provenance=None),
    )

    try:
        main.create_omi_idea("../outside", _payload(raw_idea="Nope.", provenance=None))
    except main.HTTPException as exc:
        assert exc.status_code == 400
    else:
        raise AssertionError("unsafe project name should raise HTTPException")

    for route in [main.get_omi_idea, main.get_omi_candidate]:
        try:
            route("example", "../outside")
        except main.HTTPException as exc:
            assert exc.status_code == 400
        else:
            raise AssertionError("unsafe OMI record id should raise HTTPException")

    assert main.get_omi_idea("example", idea["idea_id"]) == idea


def test_omi_routes_do_not_guard_owner_raw_idea_as_request_intent(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(main.project_manager, "PROJECTS_DIR", tmp_path)

    idea = main.create_omi_idea(
        "example",
        _payload(
            raw_idea=(
                "Owner context mentions write, dialogue, chapter, and continue "
                "without asking the assistant to produce prose."
            ),
            provenance=None,
        ),
    )

    assert "dialogue" in idea["raw_idea"]


def test_omi_routes_do_not_call_ollama(tmp_path, monkeypatch):
    monkeypatch.setattr(main.project_manager, "PROJECTS_DIR", tmp_path)

    def fail_story_check(*args, **kwargs):
        raise AssertionError("OMI routes must not call analysis engine")

    monkeypatch.setattr(main.analysis_engine, "run_story_check", fail_story_check)

    idea = main.create_omi_idea(
        "example",
        _payload(raw_idea="Owner-authored planning input.", provenance=None),
    )
    candidate = main.create_omi_candidate(
        "example",
        _payload(
            idea_id=idea["idea_id"],
            candidate_type="planning_note",
            candidate_content={"summary": "Candidate-only context."},
            destination="planning_notes",
            provenance=None,
            evidence=[],
        ),
    )

    assert candidate["idea_id"] == idea["idea_id"]


def test_omi_idea_decision_route_updates_owner_review(tmp_path, monkeypatch):
    monkeypatch.setattr(main.project_manager, "PROJECTS_DIR", tmp_path)
    idea = main.create_omi_idea(
        "example",
        _payload(raw_idea="Review this idea.", provenance=None),
    )

    updated = main.update_omi_idea_decision(
        "example",
        idea["idea_id"],
        _payload(
            owner_decision={"decision": "pending", "notes": "Ready for review."},
            status="owner_review",
        ),
    )

    assert updated["status"] == "owner_review"
    assert updated["owner_decision"]["notes"] == "Ready for review."


def test_omi_idea_decision_route_rejects_unconfirmed_approval(tmp_path, monkeypatch):
    monkeypatch.setattr(main.project_manager, "PROJECTS_DIR", tmp_path)
    idea = main.create_omi_idea(
        "example",
        _payload(raw_idea="Review this idea.", provenance=None),
    )
    reviewed = main.update_omi_idea_decision(
        "example",
        idea["idea_id"],
        _payload(owner_decision={"decision": "pending"}, status="owner_review"),
    )

    try:
        main.update_omi_idea_decision(
            "example",
            reviewed["idea_id"],
            _payload(
                owner_decision={"decision": "approve", "approval_confirmed": False},
                status="approved",
            ),
        )
    except main.HTTPException as exc:
        assert exc.status_code == 400
        assert "approval_confirmed" in exc.detail
    else:
        raise AssertionError("unconfirmed idea approval should raise HTTPException")


def test_omi_candidate_decision_route_updates_destination(tmp_path, monkeypatch):
    monkeypatch.setattr(main.project_manager, "PROJECTS_DIR", tmp_path)
    idea = main.create_omi_idea(
        "example",
        _payload(raw_idea="Candidate destination.", provenance=None),
    )
    candidate = main.create_omi_candidate(
        "example",
        _payload(
            idea_id=idea["idea_id"],
            candidate_type="planning_note",
            candidate_content={"summary": "Candidate-only context."},
            destination="planning_notes",
            provenance=None,
            evidence=[],
        ),
    )

    updated = main.update_omi_candidate_decision(
        "example",
        candidate["candidate_id"],
        _payload(
            owner_decision={"decision": "pending", "notes": "Move destination."},
            status="owner_review",
            destination="storyform_context_candidate",
        ),
    )

    assert updated["status"] == "owner_review"
    assert updated["destination"] == "storyform_context_candidate"
    assert updated["promotion_status"]["eligible"] is False


def test_omi_candidate_decision_route_rejects_invalid_destination_and_promoted_status(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(main.project_manager, "PROJECTS_DIR", tmp_path)
    idea = main.create_omi_idea(
        "example",
        _payload(raw_idea="Candidate destination.", provenance=None),
    )
    candidate = main.create_omi_candidate(
        "example",
        _payload(
            idea_id=idea["idea_id"],
            candidate_type="planning_note",
            candidate_content={"summary": "Candidate-only context."},
            destination="planning_notes",
            provenance=None,
            evidence=[],
        ),
    )

    for destination in ["scene_prose", "dialogue", "rewrite", "continuation", "chapter"]:
        try:
            main.update_omi_candidate_decision(
                "example",
                candidate["candidate_id"],
                _payload(
                    owner_decision={"decision": "pending"},
                    status="candidate",
                    destination=destination,
                ),
            )
        except main.HTTPException as exc:
            assert exc.status_code == 400
            assert "destination" in exc.detail
        else:
            raise AssertionError("invalid destination should raise HTTPException")

    try:
        main.update_omi_candidate_decision(
            "example",
            candidate["candidate_id"],
            _payload(
                owner_decision={"decision": "pending"},
                status="promoted",
                destination=None,
            ),
        )
    except main.HTTPException as exc:
        assert exc.status_code == 400
        assert "promoted" in exc.detail
    else:
        raise AssertionError("promoted status should raise HTTPException")


def test_omi_candidate_decision_route_rejects_unknown_candidate(tmp_path, monkeypatch):
    monkeypatch.setattr(main.project_manager, "PROJECTS_DIR", tmp_path)

    try:
        main.update_omi_candidate_decision(
            "example",
            "candidate_missing",
            _payload(
                owner_decision={"decision": "pending"},
                status="owner_review",
                destination=None,
            ),
        )
    except main.HTTPException as exc:
        assert exc.status_code == 404
    else:
        raise AssertionError("unknown candidate should raise HTTPException")


def test_omi_decision_routes_do_not_call_ollama_or_promote(tmp_path, monkeypatch):
    monkeypatch.setattr(main.project_manager, "PROJECTS_DIR", tmp_path)

    def fail_story_check(*args, **kwargs):
        raise AssertionError("OMI decision routes must not call analysis engine")

    monkeypatch.setattr(main.analysis_engine, "run_story_check", fail_story_check)
    idea = main.create_omi_idea(
        "example",
        _payload(raw_idea="Owner-authored planning input.", provenance=None),
    )
    candidate = main.create_omi_candidate(
        "example",
        _payload(
            idea_id=idea["idea_id"],
            candidate_type="planning_note",
            candidate_content={"summary": "Candidate-only context."},
            destination="planning_notes",
            provenance=None,
            evidence=[],
        ),
    )

    updated = main.update_omi_candidate_decision(
        "example",
        candidate["candidate_id"],
        _payload(
            owner_decision={
                "decision": "pending",
                "notes": "write dialogue chapter are owner context terms",
            },
            status="owner_review",
            destination="planning_notes",
        ),
    )

    assert updated["promotion_status"]["eligible"] is False
    assert not hasattr(main, "promote_omi_candidate")
