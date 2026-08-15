"""Route-only contract for durable review action commands."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from backend import project_manager, review_api
from backend.routes import review_queue


PROJECT_ID = "example"
QUEUE_ENTRY_ID = "review_queue_entry_scene_001_character_001"
CANDIDATE_ID = "core_candidate_scene_001_character_001"
IDEMPOTENCY_KEY = "123e4567-e89b-42d3-a456-426614174000"


def review_command_payload(**overrides) -> dict:
    payload = {
        "action_type": "mark_reviewed",
        "queue_entry_id": QUEUE_ENTRY_ID,
        "candidate_id": CANDIDATE_ID,
        "actor": "owner-reviewed",
        "owner_confirmed": True,
        "preserve_candidate_linkage": True,
        "preserve_evidence_provenance": True,
        "idempotency_key": IDEMPOTENCY_KEY,
        "expected_current_review_status": "pending",
        "expected_current_version": 0,
    }
    payload.update(overrides)
    return payload


class FakeRequest:
    def __init__(self, payload, runtime: Path, *, malformed: bool = False) -> None:
        self._payload = payload
        self._malformed = malformed
        self.app = SimpleNamespace(
            state=SimpleNamespace(validated_runtime_dir=runtime)
        )

    async def json(self):
        if self._malformed:
            raise ValueError("malformed JSON")
        return self._payload


def invoke(request: FakeRequest):
    return asyncio.run(
        review_queue.execute_review_queue_action(PROJECT_ID, QUEUE_ENTRY_ID, request)
    )


@pytest.fixture
def route_context(monkeypatch, tmp_path: Path) -> tuple[Path, Path]:
    projects_dir = tmp_path / "projects"
    project_manager.create_project("Example", projects_dir=projects_dir)
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", projects_dir)
    runtime = tmp_path / "runtime"
    return (projects_dir / PROJECT_ID).resolve(), runtime


def test_route_forwards_project_dir_and_identical_validated_runtime_path(
    route_context: tuple[Path, Path], monkeypatch
) -> None:
    project_dir, runtime = route_context
    calls = []

    def execute(payload, **kwargs):
        calls.append((payload, kwargs))
        return {"schema_version": 1, "status": "accepted", "replay": False}

    monkeypatch.setattr(review_api, "execute_review_action_command", execute)
    request = FakeRequest(review_command_payload(), runtime)
    response = invoke(request)

    assert response["status"] == "accepted"
    payload, kwargs = calls[0]
    assert payload == review_command_payload()
    assert kwargs["project_dir"] == project_dir
    assert kwargs["trusted_runtime_dir"] is runtime


@pytest.mark.parametrize(
    ("error_type", "status"),
    [
        (review_api.ReviewActionBadRequest, 400),
        (review_api.ReviewActionForbidden, 403),
        (review_api.ReviewActionNotFound, 404),
        (review_api.ReviewActionConflict, 409),
        (review_api.ReviewActionUnprocessable, 422),
        (review_api.ReviewActionLockUnavailable, 423),
        (review_api.ReviewActionPersistenceFailure, 500),
    ],
)
def test_command_exception_mapping(
    route_context: tuple[Path, Path], monkeypatch, error_type, status: int
) -> None:
    def execute(*args, **kwargs):
        raise error_type("bounded failure", error_code="BOUNDED_FAILURE")

    monkeypatch.setattr(review_api, "execute_review_action_command", execute)
    response = invoke(FakeRequest(review_command_payload(), route_context[1]))
    assert response.status_code == status
    assert json.loads(response.body)["error_code"] == "BOUNDED_FAILURE"


def test_successful_closed_envelope_is_http_200_never_202(
    route_context: tuple[Path, Path], monkeypatch
) -> None:
    expected = {
        "schema_version": 1,
        "status": "accepted",
        "replay": False,
        "action_command": "mark_reviewed",
        "warnings": [],
        "errors": [],
    }
    monkeypatch.setattr(
        review_api, "execute_review_action_command", lambda *args, **kwargs: expected
    )
    assert invoke(FakeRequest(review_command_payload(), route_context[1])) == expected


def test_malformed_json_is_400(route_context: tuple[Path, Path]) -> None:
    response = invoke(FakeRequest(None, route_context[1], malformed=True))
    assert response.status_code == 400


@pytest.mark.parametrize(
    ("payload", "status"),
    [
        (review_command_payload(action_type="apply_promotion"), 403),
        (review_command_payload(canon_path="blocked"), 403),
        (review_command_payload(action_type="unknown"), 422),
    ],
)
def test_forbidden_fields_and_commands_are_mapped(
    route_context: tuple[Path, Path], monkeypatch, payload, status: int
) -> None:
    def execute(body, **kwargs):
        review_api.validate_review_action_command_request(
            body, project_id=PROJECT_ID, queue_entry_id=QUEUE_ENTRY_ID
        )

    monkeypatch.setattr(review_api, "execute_review_action_command", execute)
    response = invoke(FakeRequest(payload, route_context[1]))
    assert response.status_code == status


def test_get_post_method_separation() -> None:
    action_route = next(
        route
        for route in review_queue.router.routes
        if route.path.endswith("/{queue_entry_id}/actions")
    )
    assert action_route.methods == {"POST"}
    get_routes = [
        route
        for route in review_queue.router.routes
        if not route.path.endswith("/{queue_entry_id}/actions")
    ]
    assert get_routes
    assert all(route.methods == {"GET"} for route in get_routes)
