"""Expected-red contract tests for the future review action command route.

PHASE8-IMPL-016-T003 is tests-first only. The future owner-action review
command boundary is expected at:

POST /api/projects/{project_id}/review-queue/{queue_entry_id}/actions

These tests define candidate review command behavior for PHASE8-IMPL-016-T004.
They must stay red until the future route/helper exists, and they must not add
owner action execution, command route runtime code, apply-promotion, memory/canon
mutation, raw artifact persistence, runtime extraction, model calls, generated
prose, or training data behavior.
"""

from __future__ import annotations

import anyio
import httpx
import pytest
from urllib.parse import quote

from backend import main


PROJECT_ID = "example"
QUEUE_ENTRY_ID = "review_queue_entry_scene_001_character_001"
CANDIDATE_ID = "core_candidate_scene_001_character_001"
OTHER_CANDIDATE_ID = "core_candidate_scene_999_character_999"

ACTION_ROUTE_TEMPLATE = (
    "/api/projects/{project_id}/review-queue/{queue_entry_id}/actions"
)
ACTION_ROUTE = ACTION_ROUTE_TEMPLATE.format(
    project_id=PROJECT_ID,
    queue_entry_id=QUEUE_ENTRY_ID,
)
READONLY_ENTRY_ROUTE = f"/api/projects/{PROJECT_ID}/review-queue/{QUEUE_ENTRY_ID}"
APPLY_PROMOTION_ROUTE = (
    f"/api/projects/{PROJECT_ID}/review-queue/{QUEUE_ENTRY_ID}/apply-promotion"
)

ALLOWED_REVIEW_COMMANDS = (
    "mark_reviewed",
    "request_more_evidence",
    "defer",
    "reject",
    "quarantine",
    "update_owner_note",
    "set_review_status",
)

FORBIDDEN_COMMANDS = (
    "apply_promotion",
    "promote_candidate",
    "write_memory",
    "write_canon",
    "mutate_project_truth",
    "persist_raw_artifact",
    "run_extraction",
    "run_booknlp",
    "run_spacy",
    "call_model",
    "model_assisted_extraction",
    "run_ncp",
    "run_subtxt",
    "run_dramatica_flow",
    "generate_prose",
    "rewrite_prose",
    "continue_scene",
    "outline_chapter",
    "create_training_jsonl",
    "export_dataset",
    "write_model_artifact",
)

UNSAFE_PROJECT_IDS = (
    "../escape",
    "..",
    ".",
    "/absolute",
    "folder/name",
    "folder\\name",
    ".hidden",
)

UNSAFE_QUEUE_ENTRY_IDS = (
    "../escape",
    "..",
    ".",
    "/absolute",
    "folder/name",
    "folder\\name",
    ".hidden",
)

UNEXPECTED_WRITE_TARGET_FIELDS = (
    "canon_path",
    "memory_path",
    "scene_path",
    "storyform_path",
    "raw_artifact_path",
    "model_prompt",
    "generated_text",
    "prose_text",
    "scene_prose",
    "jsonl_output_path",
    "dataset_manifest_path",
    "model_artifact_path",
)

FORBIDDEN_RESPONSE_FIELDS = (
    "canon_mutation",
    "apply_promotion_result",
    "raw_artifact_result",
    "generated_prose",
    "memory_write",
    "canon_write",
    "model_call",
    "runtime_extraction",
    "training_record",
)

MUTATION_INSTRUCTION_FIELDS = (
    "canon_mutation",
    "memory_mutation",
    "project_truth_mutation",
    "apply_promotion",
)

PROSE_PAYLOAD_FIELDS = ("generated_text", "prose_text", "scene_prose")

TRAINING_PAYLOAD_FIELDS = (
    "jsonl_output_path",
    "dataset_manifest_path",
    "model_artifact_path",
)


class RouteClient:
    def request(self, method: str, path: str, **kwargs) -> httpx.Response:
        async def send_request() -> httpx.Response:
            transport = httpx.ASGITransport(app=main.app)
            async with httpx.AsyncClient(
                transport=transport,
                base_url="http://testserver",
            ) as async_client:
                return await async_client.request(method, path, **kwargs)

        return anyio.run(send_request)

    def get(self, path: str, **kwargs) -> httpx.Response:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs) -> httpx.Response:
        return self.request("POST", path, **kwargs)

    def put(self, path: str, **kwargs) -> httpx.Response:
        return self.request("PUT", path, **kwargs)

    def patch(self, path: str, **kwargs) -> httpx.Response:
        return self.request("PATCH", path, **kwargs)

    def delete(self, path: str, **kwargs) -> httpx.Response:
        return self.request("DELETE", path, **kwargs)


@pytest.fixture
def route_client() -> RouteClient:
    return RouteClient()


def review_command_payload(action_type: str, **overrides) -> dict:
    payload = {
        "action_type": action_type,
        "queue_entry_id": QUEUE_ENTRY_ID,
        "candidate_id": CANDIDATE_ID,
        "actor": {
            "actor_type": "owner",
            "owner_confirmed": True,
            "owner_confirmation_marker": "owner-reviewed",
        },
        "owner_confirmed": True,
        "owner_note": "Owner-authored candidate review rationale.",
        "rationale": "Owner-authored review command metadata.",
        "expected_current_review_status": "pending",
        "expected_current_version": 1,
        "preserve_candidate_linkage": True,
        "preserve_evidence_provenance": True,
        "metadata": {
            "client_request_id": "phase8-impl-016-t003-contract",
            "no_silent_promotion": True,
            "no_apply_promotion": True,
            "no_memory_canon_mutation": True,
            "no_raw_artifact_persistence": True,
            "no_runtime_extraction": True,
            "no_model_calls": True,
            "no_generated_prose": True,
        },
    }
    payload.update(overrides)
    return payload


def encode_unsafe_route_id(value: str) -> str:
    return quote(value, safe="").replace(".", "%2E")


def assert_no_forbidden_response_fields(value) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            assert key not in FORBIDDEN_RESPONSE_FIELDS, key
            assert_no_forbidden_response_fields(nested)
    elif isinstance(value, list):
        for item in value:
            assert_no_forbidden_response_fields(item)


def assert_future_accepted_response_boundary(payload: dict, action_type: str) -> None:
    assert payload["status"] in {"accepted", "rejected"}
    assert payload["action_type"] == action_type
    assert payload["queue_entry_id"] == QUEUE_ENTRY_ID
    assert payload["candidate_id"] == CANDIDATE_ID
    assert "review_workflow_state" in payload
    assert payload["review_workflow_state"]["is_canon"] is False
    assert payload["review_workflow_state"]["apply_promotion_performed"] is False
    assert payload["review_workflow_state"]["memory_canon_mutation_performed"] is False
    assert "warnings" in payload
    assert any("not canon" in warning.lower() for warning in payload["warnings"])
    assert "evidence_provenance" in payload
    assert "source_locator" in payload["evidence_provenance"]
    assert_no_forbidden_response_fields(payload)


@pytest.mark.parametrize("action_type", ALLOWED_REVIEW_COMMANDS)
def test_allowed_review_workflow_commands_are_future_post_actions(
    route_client: RouteClient,
    action_type: str,
):
    response = route_client.post(
        ACTION_ROUTE,
        json=review_command_payload(action_type),
    )

    assert response.status_code in {200, 202}
    assert_future_accepted_response_boundary(response.json(), action_type)


@pytest.mark.parametrize("action_type", FORBIDDEN_COMMANDS)
def test_forbidden_owner_action_commands_fail_closed(
    route_client: RouteClient,
    action_type: str,
):
    response = route_client.post(
        ACTION_ROUTE,
        json=review_command_payload(action_type),
    )

    assert response.status_code in {400, 403, 422}
    payload = response.json()
    assert payload["status"] == "rejected"
    assert payload["action_type"] == action_type
    assert_no_forbidden_response_fields(payload)


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param(
            review_command_payload("mark_reviewed") | {"action_type": None},
            id="missing action_type",
        ),
        pytest.param(
            review_command_payload("totally_unknown_review_command"),
            id="unknown action_type",
        ),
        pytest.param(
            review_command_payload(
                "reject",
                owner_confirmed=False,
                actor={"actor_type": "owner", "owner_confirmed": False},
            ),
            id="missing owner confirmation when required",
        ),
        pytest.param(["not", "a", "mapping"], id="malformed payload shape"),
        pytest.param(
            review_command_payload("mark_reviewed", candidate_id=OTHER_CANDIDATE_ID),
            id="queue/candidate mismatch",
        ),
        pytest.param(
            review_command_payload(
                "mark_reviewed",
                instructions={
                    "write_canon": True,
                    "mutate_project_truth": True,
                },
            ),
            id="direct canon/memory/project-truth mutation instructions",
        ),
    ],
)
def test_malformed_or_unsafe_payloads_fail_closed(
    route_client: RouteClient,
    payload,
):
    response = route_client.post(ACTION_ROUTE, json=payload)

    assert response.status_code in {400, 403, 422}
    assert_no_forbidden_response_fields(response.json())


@pytest.mark.parametrize("field_name", UNEXPECTED_WRITE_TARGET_FIELDS)
def test_unexpected_write_target_fields_fail_closed(
    route_client: RouteClient,
    field_name: str,
):
    response = route_client.post(
        ACTION_ROUTE,
        json=review_command_payload("mark_reviewed", **{field_name: "unsafe"}),
    )

    assert response.status_code in {400, 403, 422}
    assert_no_forbidden_response_fields(response.json())


@pytest.mark.parametrize("field_name", MUTATION_INSTRUCTION_FIELDS)
def test_direct_memory_canon_or_project_truth_mutation_fields_fail_closed(
    route_client: RouteClient,
    field_name: str,
):
    response = route_client.post(
        ACTION_ROUTE,
        json=review_command_payload("quarantine", **{field_name: True}),
    )

    assert response.status_code in {400, 403, 422}
    assert_no_forbidden_response_fields(response.json())


@pytest.mark.parametrize("unsafe_project_id", UNSAFE_PROJECT_IDS)
def test_unsafe_project_id_fails_closed_for_command_route(
    route_client: RouteClient,
    unsafe_project_id: str,
):
    path = ACTION_ROUTE_TEMPLATE.format(
        project_id=encode_unsafe_route_id(unsafe_project_id),
        queue_entry_id=QUEUE_ENTRY_ID,
    )

    response = route_client.post(
        path,
        json=review_command_payload("mark_reviewed"),
    )

    assert response.status_code in {400, 422}


@pytest.mark.parametrize("unsafe_queue_entry_id", UNSAFE_QUEUE_ENTRY_IDS)
def test_unsafe_queue_entry_id_fails_closed_for_command_route(
    route_client: RouteClient,
    unsafe_queue_entry_id: str,
):
    path_entry_id = encode_unsafe_route_id(unsafe_queue_entry_id)
    path = ACTION_ROUTE_TEMPLATE.format(
        project_id=PROJECT_ID,
        queue_entry_id=path_entry_id,
    )

    response = route_client.post(
        path,
        json=review_command_payload("mark_reviewed"),
    )

    assert response.status_code in {400, 422}


def test_readonly_get_route_remains_separate_from_command_route(
    route_client: RouteClient,
):
    response = route_client.get(
        READONLY_ENTRY_ROUTE,
        json=review_command_payload("mark_reviewed"),
    )

    assert response.status_code in {400, 405, 415, 422}


def test_command_route_is_post_only(
    route_client: RouteClient,
):
    for method in ("get", "put", "patch", "delete"):
        requester = getattr(route_client, method)
        kwargs = {}
        if method in {"put", "patch"}:
            kwargs["json"] = review_command_payload("mark_reviewed")

        response = requester(ACTION_ROUTE, **kwargs)

        assert response.status_code == 405


def test_no_apply_promotion_route_exists_in_phase8_impl_016(
    route_client: RouteClient,
):
    response = route_client.post(
        APPLY_PROMOTION_ROUTE,
        json=review_command_payload("apply_promotion"),
    )

    assert response.status_code in {404, 405}


@pytest.mark.parametrize("action_type", ("generate_prose", "rewrite_prose", "continue_scene"))
def test_generated_prose_commands_are_rejected(route_client: RouteClient, action_type: str):
    response = route_client.post(
        ACTION_ROUTE,
        json=review_command_payload(action_type),
    )

    assert response.status_code in {400, 403, 422}
    assert_no_forbidden_response_fields(response.json())


@pytest.mark.parametrize("field_name", PROSE_PAYLOAD_FIELDS)
def test_prose_payload_fields_are_rejected(route_client: RouteClient, field_name: str):
    response = route_client.post(
        ACTION_ROUTE,
        json=review_command_payload("update_owner_note", **{field_name: "blocked"}),
    )

    assert response.status_code in {400, 403, 422}
    assert_no_forbidden_response_fields(response.json())


@pytest.mark.parametrize(
    "action_type",
    ("create_training_jsonl", "export_dataset", "write_model_artifact"),
)
def test_training_dataset_and_model_artifact_commands_are_rejected(
    route_client: RouteClient,
    action_type: str,
):
    response = route_client.post(
        ACTION_ROUTE,
        json=review_command_payload(action_type),
    )

    assert response.status_code in {400, 403, 422}
    assert_no_forbidden_response_fields(response.json())


@pytest.mark.parametrize("field_name", TRAINING_PAYLOAD_FIELDS)
def test_training_dataset_and_model_artifact_payload_fields_are_rejected(
    route_client: RouteClient,
    field_name: str,
):
    response = route_client.post(
        ACTION_ROUTE,
        json=review_command_payload("defer", **{field_name: "blocked"}),
    )

    assert response.status_code in {400, 403, 422}
    assert_no_forbidden_response_fields(response.json())
