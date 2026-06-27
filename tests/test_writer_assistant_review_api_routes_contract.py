"""Contract tests for future read-only review queue FastAPI routes.

PHASE8-IMPL-015-T003 is tests-first / expected-red only. The future routes must
wrap backend.review_api read-only helpers and must not implement owner action
execution, owner action execution routes, apply-promotion, memory/canon mutation,
raw artifact persistence,
runtime extraction, model calls, or generated prose.
"""

from __future__ import annotations

from pathlib import Path

import anyio
import httpx
import pytest

from backend import main
from backend import review_api


PROJECT_ID = "example"
QUEUE_ENTRY_ID = "review_queue_entry_scene_001_character_001"
CANDIDATE_RECORD_ID = "core_candidate_scene_001_character_001"

LIST_ROUTE = f"/api/projects/{PROJECT_ID}/review-queue"
ENTRY_ROUTE = f"{LIST_ROUTE}/{QUEUE_ENTRY_ID}"
INDEX_ROUTE = f"{LIST_ROUTE}/index"
SUMMARY_ROUTE = f"{LIST_ROUTE}/summary"

READ_ONLY_ROUTES = {
    "list": LIST_ROUTE,
    "get": ENTRY_ROUTE,
    "index": INDEX_ROUTE,
    "summary": SUMMARY_ROUTE,
}

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

WRITE_METHODS = ("post", "put", "patch", "delete")

EXPECTED_ENTRY_FIELDS = {
    "queue_entry_id",
    "project_id",
    "candidate_record_id",
    "candidate_type",
    "target_category",
    "review_status",
    "lifecycle_state",
    "confidence",
    "uncertainty_flags",
    "normalization_status",
    "human_review_required",
    "evidence_summary",
    "evidence_refs",
    "provenance_summary",
    "provenance_refs",
    "source_document",
    "source_locator",
    "raw_output_refs",
    "created_at",
    "updated_at",
}

FORBIDDEN_RESPONSE_FIELDS = {
    "command",
    "owner_action_command",
    "owner_action_execution",
    "owner_action_execution_result",
    "promotion",
    "promoted",
    "apply_promotion",
    "apply_promotion_result",
    "memory_write",
    "canon_write",
    "memory_canon_write",
    "raw_artifact_persistence",
    "runtime_extraction",
    "model_call",
    "generated_prose",
    "rewrite",
    "continuation",
    "filesystem_path",
}

FORBIDDEN_ROUTE_SOURCE_TERMS = (
    "@app." + "post",
    "@app." + "put",
    "@app." + "patch",
    "@app." + "delete",
    ".post(",
    ".put(",
    ".patch(",
    ".delete(",
    "write_review_queue_entry" + "(",
    "write_candidate",
    "execute_owner_action",
    "validate_owner_action_command_request(",
    "build_owner_action_command_response(",
    "apply_promotion" + "(",
    "write_to_memory" + "(",
    "write_to_canon" + "(",
    "persist_raw_artifact",
    "raw_artifact_persistence",
    "runtime_extraction",
    "run_booknlp" + "(",
    "run_spacy" + "(",
    "ollama",
    "model_call",
    "generate_prose" + "(",
    "generated_prose",
    "rewrite_source",
    "continue_scene",
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


def client() -> RouteClient:
    return RouteClient()


def sample_entry() -> dict:
    return {
        "queue_entry_id": QUEUE_ENTRY_ID,
        "project_id": PROJECT_ID,
        "candidate_record_id": CANDIDATE_RECORD_ID,
        "candidate_type": "character",
        "target_category": "character_memory_record",
        "review_status": "pending",
        "lifecycle_state": "draft_ready_for_review",
        "confidence": 0.72,
        "uncertainty_flags": ["owner_review_required"],
        "normalization_status": "normalized",
        "human_review_required": True,
        "evidence_summary": "Synthetic test support only.",
        "evidence_refs": ["evidence_scene_001_001"],
        "provenance_summary": "Fixture parser support only.",
        "provenance_refs": ["provenance_fixture_001"],
        "source_document": {"source_document_id": "scene_001", "label": "Scene 001"},
        "source_locator": {
            "source_document_id": "scene_001",
            "start_offset": 0,
            "end_offset": 42,
        },
        "raw_output_refs": ["raw_ref_fixture_001"],
        "created_at": "2026-06-25T00:00:00Z",
        "updated_at": "2026-06-25T00:00:00Z",
    }


def assert_no_forbidden_keys(value) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            assert key not in FORBIDDEN_RESPONSE_FIELDS, key
            assert_no_forbidden_keys(nested)
    elif isinstance(value, list):
        for item in value:
            assert_no_forbidden_keys(item)


def assert_entry_preserves_review_support(entry: dict) -> None:
    assert EXPECTED_ENTRY_FIELDS <= set(entry)
    assert entry["queue_entry_id"] == QUEUE_ENTRY_ID
    assert entry["project_id"] == PROJECT_ID
    assert entry["candidate_record_id"] == CANDIDATE_RECORD_ID
    assert entry["evidence_refs"]
    assert entry["provenance_refs"]
    assert entry["source_document"]["source_document_id"] == "scene_001"
    assert entry["source_locator"]["source_document_id"] == "scene_001"
    assert entry["raw_output_refs"] == ["raw_ref_fixture_001"]
    assert isinstance(entry["confidence"], float)
    assert entry["uncertainty_flags"] == ["owner_review_required"]
    assert entry["normalization_status"] == "normalized"
    assert entry["human_review_required"] is True
    assert_no_forbidden_keys(entry)


@pytest.fixture
def route_client() -> RouteClient:
    return client()


@pytest.fixture
def readonly_helper_spies(monkeypatch):
    calls: list[tuple[str, dict]] = []
    entry = sample_entry()

    def list_readonly(request: dict, **kwargs) -> dict:
        calls.append(("list", dict(request)))
        return {
            "schema_version": 1,
            "project_id": request["project_id"],
            "entries": [entry],
            "pagination": {
                "limit": request.get("limit"),
                "offset": request.get("offset"),
                "cursor": request.get("cursor"),
                "total_count": 1,
                "returned_count": 1,
            },
            "summary": {"entry_count": 1},
            "metadata": {
                "read_only": True,
                "no_promotion_performed": True,
                "no_memory_canon_mutation": True,
            },
            "warnings": ["Queue presence is not approval."],
            "errors": [],
        }

    def get_readonly(request: dict, **kwargs) -> dict:
        calls.append(("get", dict(request)))
        return {
            "schema_version": 1,
            "project_id": request["project_id"],
            "queue_entry_id": request["queue_entry_id"],
            "entry": entry,
            "metadata": {
                "read_only": True,
                "no_promotion_performed": True,
                "no_memory_canon_mutation": True,
            },
            "warnings": ["Confidence is support strength, not truth."],
            "errors": [],
        }

    def index_readonly(request: dict, **kwargs) -> dict:
        calls.append(("index", dict(request)))
        return {
            "schema_version": 1,
            "project_id": request["project_id"],
            "entries": [
                {
                    "queue_entry_id": QUEUE_ENTRY_ID,
                    "candidate_record_id": CANDIDATE_RECORD_ID,
                    "review_status": "pending",
                    "lifecycle_state": "draft_ready_for_review",
                    "candidate_type": "character",
                    "target_category": "character_memory_record",
                    "confidence": 0.72,
                    "human_review_required": True,
                }
            ],
            "summary": {"entry_count": 1},
            "metadata": {
                "read_only": True,
                "derived_rebuildable_index": True,
                "no_promotion_performed": True,
                "no_memory_canon_mutation": True,
            },
            "warnings": [],
            "errors": [],
        }

    def summary_readonly(request: dict, **kwargs) -> dict:
        calls.append(("summary", dict(request)))
        return {
            "schema_version": 1,
            "project_id": request["project_id"],
            "summary": {
                "entry_count": 1,
                "counts_by_review_status": {"pending": 1},
                "counts_by_lifecycle_state": {"draft_ready_for_review": 1},
                "counts_by_candidate_type": {"character": 1},
            },
            "metadata": {
                "read_only": True,
                "no_promotion_performed": True,
                "no_memory_canon_mutation": True,
            },
            "warnings": [],
            "errors": [],
        }

    monkeypatch.setattr(
        review_api,
        "list_review_queue_entries_readonly",
        list_readonly,
    )
    monkeypatch.setattr(review_api, "get_review_queue_entry_readonly", get_readonly)
    monkeypatch.setattr(review_api, "get_review_queue_index_readonly", index_readonly)
    monkeypatch.setattr(
        review_api,
        "get_review_queue_summary_readonly",
        summary_readonly,
    )
    return calls


@pytest.mark.parametrize(
    ("route_name", "path"),
    READ_ONLY_ROUTES.items(),
)
def test_expected_readonly_review_queue_get_routes_exist_and_return_contract_shape(
    route_client: RouteClient,
    readonly_helper_spies,
    route_name: str,
    path: str,
):
    response = route_client.get(path)

    assert response.status_code == 200
    payload = response.json()
    assert payload["schema_version"] == 1
    assert payload["project_id"] == PROJECT_ID
    assert_no_forbidden_keys(payload)

    if route_name == "list":
        assert "entries" in payload
        assert "summary" in payload
        assert "pagination" in payload
        assert_entry_preserves_review_support(payload["entries"][0])
    elif route_name == "get":
        assert payload["queue_entry_id"] == QUEUE_ENTRY_ID
        assert_entry_preserves_review_support(payload["entry"])
    elif route_name == "index":
        assert "entries" in payload
        assert "summary" in payload
        assert payload["metadata"]["derived_rebuildable_index"] is True
    elif route_name == "summary":
        assert "summary" in payload
        assert payload["summary"]["entry_count"] == 1

    assert readonly_helper_spies[-1][0] == route_name


@pytest.mark.parametrize("path", READ_ONLY_ROUTES.values())
@pytest.mark.parametrize("method", WRITE_METHODS)
def test_readonly_review_queue_routes_are_get_only(
    route_client: RouteClient,
    path: str,
    method: str,
):
    if method == "delete":
        response = route_client.delete(path)
    else:
        response = getattr(route_client, method)(
            path,
            json={"command": "request_more_evidence"},
        )

    assert response.status_code in {405, 422}


@pytest.mark.parametrize("unsafe_project_id", UNSAFE_PROJECT_IDS)
def test_readonly_review_queue_routes_fail_closed_for_unsafe_project_ids(
    route_client: RouteClient,
    unsafe_project_id: str,
):
    path = f"/api/projects/{unsafe_project_id}/review-queue"

    response = route_client.get(path)

    assert response.status_code in {400, 404, 422}


@pytest.mark.parametrize("unsafe_queue_entry_id", UNSAFE_QUEUE_ENTRY_IDS)
def test_single_entry_route_fails_closed_for_unsafe_queue_entry_ids(
    route_client: RouteClient,
    unsafe_queue_entry_id: str,
):
    path_entry_id = "%2E" if unsafe_queue_entry_id == "." else unsafe_queue_entry_id
    path = f"/api/projects/{PROJECT_ID}/review-queue/{path_entry_id}"

    response = route_client.get(path)

    assert response.status_code in {400, 404, 422}


@pytest.mark.parametrize(
    "query",
    [
        {"unknown_field": "blocked"},
        {"sort_by": "apply_promotion"},
        {"sort_direction": "sideways"},
        {"has_raw_refs": "not-a-bool"},
        {"confidence_min": "not-a-number"},
        {"confidence_max": "not-a-number"},
        {"limit": "-1"},
        {"offset": "-1"},
    ],
)
def test_unknown_filters_sorts_and_malformed_query_fields_fail_closed(
    route_client: RouteClient,
    query: dict[str, str],
):
    response = route_client.get(LIST_ROUTE, params=query)

    assert response.status_code in {400, 422}


def test_get_routes_fail_closed_for_forbidden_request_body(route_client: RouteClient):
    response = route_client.request(
        "GET",
        LIST_ROUTE,
        json={
            "owner_action_execution": True,
            "apply-promotion": True,
            "memory/canon": True,
            "raw artifact": True,
            "runtime extraction": True,
            "model": True,
            "generated prose": True,
        },
    )

    assert response.status_code in {400, 415, 422}


def test_list_route_preserves_missing_queue_as_readonly_empty_response(
    route_client: RouteClient,
    monkeypatch,
):
    def missing_queue(request: dict, **kwargs) -> dict:
        return {
            "schema_version": 1,
            "project_id": request["project_id"],
            "entries": [],
            "pagination": {"limit": None, "offset": None, "cursor": None},
            "summary": {"entry_count": 0},
            "metadata": {"read_only": True, "storage_consulted": True},
            "warnings": ["unavailable storage"],
            "errors": ["unavailable storage"],
        }

    monkeypatch.setattr(
        review_api,
        "list_review_queue_entries_readonly",
        missing_queue,
    )

    response = route_client.get(LIST_ROUTE)

    assert response.status_code == 200
    payload = response.json()
    assert payload["entries"] == []
    assert payload["summary"]["entry_count"] == 0
    assert payload["warnings"]
    assert payload["errors"]
    assert_no_forbidden_keys(payload)


def test_index_route_returns_derived_rebuildable_data_without_persistence(
    route_client: RouteClient,
    monkeypatch,
):
    def missing_index(request: dict, **kwargs) -> dict:
        return {
            "schema_version": 1,
            "project_id": request["project_id"],
            "entries": [],
            "summary": {"entry_count": 0},
            "metadata": {
                "read_only": True,
                "storage_consulted": True,
                "derived_rebuildable_index": True,
            },
            "warnings": ["unavailable storage"],
            "errors": ["unavailable storage"],
        }

    monkeypatch.setattr(
        review_api,
        "get_review_queue_index_readonly",
        missing_index,
    )

    response = route_client.get(INDEX_ROUTE)

    assert response.status_code == 200
    payload = response.json()
    assert payload["entries"] == []
    assert payload["summary"]["entry_count"] == 0
    assert payload["metadata"]["derived_rebuildable_index"] is True
    assert_no_forbidden_keys(payload)


def test_malformed_queue_entry_fails_closed_without_cleaning_into_review_ready_entry(
    route_client: RouteClient,
    monkeypatch,
):
    def malformed_entry(request: dict, **kwargs) -> dict:
        return {
            "schema_version": 1,
            "project_id": request["project_id"],
            "entry": {
                "queue_entry_id": request["queue_entry_id"],
                "project_id": request["project_id"],
                "candidate_record_id": CANDIDATE_RECORD_ID,
                "human_review_required": False,
            },
            "metadata": {"read_only": True},
            "warnings": ["invalid entry"],
            "errors": ["invalid entry"],
        }

    monkeypatch.setattr(
        review_api,
        "get_review_queue_entry_readonly",
        malformed_entry,
    )

    response = route_client.get(ENTRY_ROUTE)

    assert response.status_code in {400, 422, 500}


def test_summary_route_returns_counts_and_status_only_without_queue_mutation(
    route_client: RouteClient,
    readonly_helper_spies,
):
    response = route_client.get(SUMMARY_ROUTE)

    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"] == {
        "entry_count": 1,
        "counts_by_review_status": {"pending": 1},
        "counts_by_lifecycle_state": {"draft_ready_for_review": 1},
        "counts_by_candidate_type": {"character": 1},
    }
    assert payload["metadata"]["read_only"] is True
    assert readonly_helper_spies[-1][0] == "summary"
    assert_no_forbidden_keys(payload)


def test_future_route_source_contains_only_backend_review_api_readonly_boundary():
    route_source = Path("backend/routes/review_queue.py")
    if not route_source.exists():
        pytest.skip(
            "backend/routes/review_queue.py is absent in T003; route source scan "
            "activates after the T004 implementation creates the file."
        )

    text = route_source.read_text(encoding="utf-8")
    assert "backend.review_api" in text or "from backend import review_api" in text
    for helper_name in (
        "validate_review_queue_read_request",
        "list_review_queue_entries_readonly",
        "get_review_queue_entry_readonly",
        "get_review_queue_index_readonly",
        "get_review_queue_summary_readonly",
    ):
        assert helper_name in text
    for forbidden in FORBIDDEN_ROUTE_SOURCE_TERMS:
        assert forbidden not in text
