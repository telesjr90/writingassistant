"""Safety regressions for the PHASE8-IMPL-016 owner-action review workflow.

These tests intentionally cover only review workflow state. Forbidden command
names are present as rejected fixtures, not as implementation behavior.
"""

from __future__ import annotations

from pathlib import Path

import anyio
import httpx
import pytest

from backend import main


REPO_ROOT = Path(__file__).resolve().parents[1]

PROJECT_ID = "example"
QUEUE_ENTRY_ID = "review_queue_entry_scene_001_character_001"
CANDIDATE_ID = "core_candidate_scene_001_character_001"
ACTION_ROUTE = f"/api/projects/{PROJECT_ID}/review-queue/{QUEUE_ENTRY_ID}/actions"
READONLY_ENTRY_ROUTE = f"/api/projects/{PROJECT_ID}/review-queue/{QUEUE_ENTRY_ID}"

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

FORBIDDEN_PAYLOAD_FIELDS = (
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

FORBIDDEN_RESPONSE_CLAIMS = (
    "canon_mutation",
    "memory_mutation",
    "project_truth_mutation",
    "apply_promotion_result",
    "memory_write",
    "canon_write",
    "raw_artifact_result",
    "runtime_extraction",
    "model_call",
    "generated_prose",
    "training_record",
)

FRONTEND_PATHS = (
    REPO_ROOT / "frontend" / "src" / "api.js",
    REPO_ROOT / "frontend" / "src" / "App.jsx",
    REPO_ROOT / "frontend" / "src" / "components" / "ReviewQueuePanel.jsx",
    REPO_ROOT / "frontend" / "src" / "components" / "OwnerActionReviewControls.jsx",
)

BOUNDARY_SCAN_PATHS = (
    REPO_ROOT / "backend" / "review_api.py",
    REPO_ROOT / "backend" / "routes" / "review_queue.py",
    *FRONTEND_PATHS,
    REPO_ROOT / "frontend" / "src" / "styles.css",
    REPO_ROOT / "tests" / "test_writer_assistant_review_action_command_routes_contract.py",
    REPO_ROOT / "tests" / "test_frontend_owner_action_review_workflow_source.py",
    REPO_ROOT / "tests" / "test_owner_action_review_workflow_safety_regression.py",
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


@pytest.fixture
def route_client() -> RouteClient:
    return RouteClient()


def read_source(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def combined_frontend_source() -> str:
    return "\n".join(read_source(path) for path in FRONTEND_PATHS)


def combined_boundary_source() -> str:
    return "\n".join(read_source(path) for path in BOUNDARY_SCAN_PATHS if path.exists())


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
        "owner_note": "Owner-authored review note.",
        "rationale": "Owner-authored review rationale.",
        "expected_current_review_status": "pending",
        "expected_current_version": 1,
        "preserve_candidate_linkage": True,
        "preserve_evidence_provenance": True,
        "metadata": {
            "client_request_id": "phase8-impl-016-t006-safety-regression",
            "no_silent_promotion": True,
            "no_apply_promotion": True,
            "no_memory_canon_mutation": True,
            "no_project_truth_mutation": True,
            "no_raw_artifact_persistence": True,
            "no_runtime_extraction": True,
            "no_model_calls": True,
            "no_generated_prose": True,
            "no_training_artifacts": True,
        },
    }
    payload.update(overrides)
    return payload


def assert_no_forbidden_claims(value) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            assert key not in FORBIDDEN_RESPONSE_CLAIMS
            assert_no_forbidden_claims(nested)
    elif isinstance(value, list):
        for item in value:
            assert_no_forbidden_claims(item)


@pytest.mark.parametrize("action_type", ALLOWED_REVIEW_COMMANDS)
def test_allowed_review_commands_return_response_only_workflow_state(
    route_client: RouteClient,
    action_type: str,
) -> None:
    response = route_client.post(
        ACTION_ROUTE,
        json=review_command_payload(action_type),
    )

    assert response.status_code in {200, 202}
    payload = response.json()
    workflow_state = payload["review_workflow_state"]

    assert payload["status"] == "accepted"
    assert payload["action_type"] == action_type
    assert workflow_state["is_canon"] is False
    assert workflow_state["apply_promotion_performed"] is False
    assert workflow_state["memory_canon_mutation_performed"] is False
    assert workflow_state["project_truth_mutation_performed"] is False
    assert workflow_state["raw_artifact_persistence_performed"] is False
    assert workflow_state["runtime_extraction_performed"] is False
    assert workflow_state["model_call_performed"] is False
    assert workflow_state["generated_prose_performed"] is False
    assert workflow_state["training_artifact_performed"] is False
    assert payload["evidence_provenance"]["source_locator"]["candidate_id"] == CANDIDATE_ID
    assert any("not canon" in warning.lower() for warning in payload["warnings"])
    assert_no_forbidden_claims(payload)


@pytest.mark.parametrize("action_type", FORBIDDEN_COMMANDS)
def test_forbidden_owner_action_commands_fail_closed(
    route_client: RouteClient,
    action_type: str,
) -> None:
    response = route_client.post(
        ACTION_ROUTE,
        json=review_command_payload(action_type),
    )

    payload = response.json()
    assert response.status_code in {400, 403, 422}
    assert payload["status"] == "rejected"
    assert payload["action_type"] == action_type
    assert_no_forbidden_claims(payload)


@pytest.mark.parametrize("field_name", FORBIDDEN_PAYLOAD_FIELDS)
def test_forbidden_payload_fields_fail_closed(
    route_client: RouteClient,
    field_name: str,
) -> None:
    response = route_client.post(
        ACTION_ROUTE,
        json=review_command_payload("mark_reviewed", **{field_name: "blocked"}),
    )

    assert response.status_code in {400, 403, 422}
    assert response.json()["status"] == "rejected"
    assert_no_forbidden_claims(response.json())


def test_get_routes_remain_read_only_and_reject_action_payloads(
    route_client: RouteClient,
) -> None:
    response = route_client.get(
        READONLY_ENTRY_ROUTE,
        json=review_command_payload("mark_reviewed"),
    )

    assert response.status_code in {400, 405, 415, 422}


def test_frontend_api_helper_targets_owner_action_post_route() -> None:
    source = read_source(REPO_ROOT / "frontend" / "src" / "api.js")

    assert "export async function submitReviewQueueAction" in source
    assert "client.post(`/projects/${projectId}/review-queue/${queueEntryId}/actions`, payload)" in source


def test_frontend_controls_expose_only_allowed_review_workflow_commands() -> None:
    source = combined_frontend_source()

    for command in ALLOWED_REVIEW_COMMANDS:
        assert command in source
    for command in FORBIDDEN_COMMANDS:
        assert command not in source


def test_frontend_boundary_copy_and_evidence_context_remain_present() -> None:
    source = combined_frontend_source()

    for marker in (
        "candidate-only",
        "no-canon",
        "queue presence, confidence",
        "review status are not canon",
        "not project truth",
        "evidence/provenance/source",
        "source locator",
        "source_locator",
        "provenance_summary",
        "evidence_summary",
        "explicitly confirm this bounded review workflow command",
    ):
        assert marker in source


def test_frontend_payload_construction_excludes_forbidden_fields() -> None:
    source = read_source(REPO_ROOT / "frontend" / "src" / "api.js")
    body = source[source.index("export async function submitReviewQueueAction") :]

    for field_name in FORBIDDEN_PAYLOAD_FIELDS:
        assert field_name not in body
    assert "payload = {" in body
    assert "action_type: actionType" in body
    assert "owner_confirmed: true" in body
    assert "preserve_evidence_provenance: true" in body


def test_targeted_source_boundary_scan_distinguishes_rejected_fixtures() -> None:
    combined = combined_boundary_source()

    required_markers = [
        *ALLOWED_REVIEW_COMMANDS,
        "candidate-only",
        "no-canon",
        "queue presence",
        "confidence",
        "not canon",
        "evidence",
        "provenance",
        "source locator",
        "owner confirmation",
    ]
    missing = [item for item in required_markers if item not in combined]
    assert missing == []

    forbidden_implementation_markers = [
        "".join(("import ", "booknlp")),
        "".join(("from ", "booknlp")),
        "".join(("Book", "NLP(")),
        "".join(("import ", "spacy")),
        "".join(("from ", "spacy")),
        "".join(("spacy", ".load(")),
        "".join(("ollama", ".chat")),
        "".join(("ollama", ".generate")),
        "".join(("requests", ".post(")),
        "".join(("model", "_prompt:")),
        "".join(("generated", "_text:")),
        "".join(("prose", "_text:")),
        "".join(("scene", "_prose:")),
        "".join(("jsonl", "_output_path:")),
        "".join(("dataset", "_manifest_path:")),
        "".join(("model", "_artifact_path:")),
    ]
    hits = [item for item in forbidden_implementation_markers if item in combined]
    assert hits == []

    frontend = combined_frontend_source()
    forbidden_frontend_exposure = [
        *FORBIDDEN_COMMANDS,
        *FORBIDDEN_PAYLOAD_FIELDS,
    ]
    hits = [item for item in forbidden_frontend_exposure if item in frontend]
    assert hits == []
