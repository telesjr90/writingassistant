"""read-only FastAPI routes over backend.review_api review queue helpers."""

from __future__ import annotations

import math
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from backend import review_api


router = APIRouter(prefix="/api/projects/{project_id}/review-queue")

_QUERY_FIELDS = {
    "review_status",
    "lifecycle_state",
    "candidate_type",
    "target_category",
    "normalization_status",
    "has_raw_refs",
    "confidence_min",
    "confidence_max",
    "sort_by",
    "sort_direction",
    "limit",
    "offset",
    "cursor",
}

_SORT_FIELDS = {
    "queue_entry_id",
    "candidate_record_id",
    "candidate_type",
    "target_category",
    "review_status",
    "lifecycle_state",
    "confidence",
    "normalization_status",
    "updated_at",
    "created_at",
}

_ENTRY_REQUIRED_FIELDS = {
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


def _error_detail(
    message: str,
    *,
    project_id: str | None = None,
    queue_entry_id: str | None = None,
) -> dict[str, Any]:
    detail: dict[str, Any] = {
        "schema_version": review_api.SCHEMA_VERSION,
        "error": message,
        "warnings": [message],
        "errors": [message],
    }
    if project_id is not None:
        detail["project_id"] = project_id
    if queue_entry_id is not None:
        detail["queue_entry_id"] = queue_entry_id
    return detail


async def _reject_request_body(request: Request, project_id: str) -> None:
    body = await request.body()
    if body.strip():
        raise HTTPException(
            status_code=400,
            detail=_error_detail("GET request body is not allowed", project_id=project_id),
        )


def _parse_bool(value: str) -> bool:
    if value == "true":
        return True
    if value == "false":
        return False
    raise ValueError("invalid query")


def _parse_number(value: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ValueError("invalid query")
    return parsed


def _parse_non_negative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise ValueError("invalid query")
    return parsed


def _request_from_query(
    *,
    project_id: str,
    queue_entry_id: str | None,
    request: Request,
) -> dict[str, Any]:
    values: dict[str, Any] = {"project_id": project_id}
    if queue_entry_id is not None:
        values["queue_entry_id"] = queue_entry_id

    for field, value in request.query_params.multi_items():
        if field not in _QUERY_FIELDS:
            raise HTTPException(
                status_code=400,
                detail=_error_detail("unsupported query field", project_id=project_id),
            )
        if field == "has_raw_refs":
            values[field] = _parse_bool(value)
        elif field in {"confidence_min", "confidence_max"}:
            values[field] = _parse_number(value)
        elif field in {"limit", "offset"}:
            values[field] = _parse_non_negative_int(value)
        else:
            values[field] = value

    if values.get("sort_by", "queue_entry_id") not in _SORT_FIELDS:
        raise ValueError("invalid query")
    if values.get("sort_direction", "asc") not in {"asc", "desc"}:
        raise ValueError("invalid query")

    return review_api.validate_review_queue_read_request(values)


def _read_request(
    *,
    project_id: str,
    queue_entry_id: str | None = None,
    request: Request,
) -> dict[str, Any]:
    try:
        return _request_from_query(
            project_id=project_id,
            queue_entry_id=queue_entry_id,
            request=request,
        )
    except HTTPException:
        raise
    except (TypeError, ValueError, OverflowError) as exc:
        raise HTTPException(
            status_code=400,
            detail=_error_detail(
                "invalid review queue read request",
                project_id=project_id,
                queue_entry_id=queue_entry_id,
            ),
        ) from exc


def _safe_text_id(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    if value != value.strip() or not value:
        return False
    if value in {".", ".."}:
        return False
    if value.startswith(".") or value.startswith("/") or "/" in value or "\\" in value:
        return False
    if len(value) >= 2 and value[1] == ":":
        return False
    return True


def _ensure_entry(
    entry: Any,
    *,
    project_id: str,
    queue_entry_id: str | None = None,
    full: bool,
) -> None:
    if not isinstance(entry, dict):
        raise ValueError("invalid response")
    if full and not _ENTRY_REQUIRED_FIELDS <= set(entry):
        raise ValueError("invalid response")
    if full and entry.get("project_id") != project_id:
        raise ValueError("invalid response")
    if "project_id" in entry and entry["project_id"] != project_id:
        raise ValueError("invalid response")
    if queue_entry_id is not None and entry.get("queue_entry_id") != queue_entry_id:
        raise ValueError("invalid response")
    for field in ("project_id", "queue_entry_id", "candidate_record_id"):
        if field in entry and not _safe_text_id(entry[field]):
            raise ValueError("invalid response")
    if entry.get("human_review_required") is not True:
        raise ValueError("invalid response")
    for field in ("evidence_refs", "provenance_refs", "raw_output_refs"):
        if field in entry and not isinstance(entry[field], list):
            raise ValueError("invalid response")
    if "confidence" in entry and isinstance(entry["confidence"], bool):
        raise ValueError("invalid response")
    if "confidence" in entry and not isinstance(entry["confidence"], (int, float)):
        raise ValueError("invalid response")


def _ensure_payload(
    payload: Any,
    *,
    project_id: str,
    payload_key: str,
    queue_entry_id: str | None = None,
) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("invalid response")
    if payload.get("schema_version") != review_api.SCHEMA_VERSION:
        raise ValueError("invalid response")
    if payload.get("project_id") != project_id:
        raise ValueError("invalid response")
    if not isinstance(payload.get("warnings", []), list):
        raise ValueError("invalid response")
    if not isinstance(payload.get("errors", []), list):
        raise ValueError("invalid response")

    if payload_key == "entries":
        entries = payload.get("entries")
        if not isinstance(entries, list):
            raise ValueError("invalid response")
        for entry in entries:
            _ensure_entry(entry, project_id=project_id, full=True)
    elif payload_key == "entry":
        payload.setdefault("queue_entry_id", queue_entry_id)
        if payload.get("queue_entry_id") != queue_entry_id:
            raise ValueError("invalid response")
        entry = payload.get("entry")
        if entry is not None:
            _ensure_entry(
                entry,
                project_id=project_id,
                queue_entry_id=queue_entry_id,
                full=True,
            )
    elif payload_key == "index":
        entries = payload.get("entries")
        if not isinstance(entries, list):
            raise ValueError("invalid response")
        for entry in entries:
            _ensure_entry(entry, project_id=project_id, full=False)
    elif payload_key == "summary":
        if not isinstance(payload.get("summary"), dict):
            raise ValueError("invalid response")
    else:
        raise ValueError("invalid response")

    return payload


def _readonly_response(
    helper,
    valid_request: dict[str, Any],
    *,
    payload_key: str,
) -> dict[str, Any]:
    try:
        payload = helper(valid_request)
        return _ensure_payload(
            payload,
            project_id=valid_request["project_id"],
            queue_entry_id=valid_request.get("queue_entry_id"),
            payload_key=payload_key,
        )
    except HTTPException:
        raise
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=422,
            detail=_error_detail(
                "invalid review queue read response",
                project_id=valid_request.get("project_id"),
                queue_entry_id=valid_request.get("queue_entry_id"),
            ),
        ) from exc


def _command_error_response(
    exc: Exception,
    *,
    project_id: str | None = None,
    queue_entry_id: str | None = None,
    status_code: int = 422,
) -> JSONResponse:
    detail = exc.args[0] if exc.args else "invalid review action command"
    if isinstance(detail, dict):
        payload = detail
    else:
        payload = {
            "schema_version": review_api.SCHEMA_VERSION,
            "status": "rejected",
            "project_id": project_id,
            "queue_entry_id": queue_entry_id,
            "action_type": None,
            "candidate_id": None,
            "warnings": [str(detail)],
            "errors": [str(detail)],
        }
    return JSONResponse(status_code=status_code, content=payload)


# @router.post /review-queue/{queue_entry_id}/actions
async def execute_review_queue_action(
    project_id: str,
    queue_entry_id: str,
    request: Request,
) -> Any:
    try:
        payload = await request.json()
    except ValueError as exc:
        return _command_error_response(
            exc,
            project_id=project_id,
            queue_entry_id=queue_entry_id,
            status_code=400,
        )
    try:
        return review_api.execute_review_action_command(
            payload,
            project_id=project_id,
            queue_entry_id=queue_entry_id,
        )
    except review_api.ReviewActionCommandRejected as exc:
        return _command_error_response(
            exc,
            project_id=project_id,
            queue_entry_id=queue_entry_id,
            status_code=exc.status_code,
        )
    except (TypeError, ValueError) as exc:
        return _command_error_response(
            exc,
            project_id=project_id,
            queue_entry_id=queue_entry_id,
            status_code=422,
        )


router.add_api_route(
    "/{queue_entry_id}/actions",
    execute_review_queue_action,
    methods=["POST"],
    response_model=None,
)


@router.get("")
async def list_review_queue(project_id: str, request: Request) -> dict[str, Any]:
    await _reject_request_body(request, project_id)
    raw_path = request.scope.get("raw_path", b"")
    if isinstance(raw_path, bytes) and raw_path.endswith(b"/review-queue/."):
        raise HTTPException(
            status_code=400,
            detail=_error_detail("invalid review queue read request", project_id=project_id),
        )
    if request.url.path.endswith("/review-queue/"):
        raise HTTPException(
            status_code=400,
            detail=_error_detail("invalid review queue read request", project_id=project_id),
        )
    valid = _read_request(project_id=project_id, request=request)
    return _readonly_response(
        review_api.list_review_queue_entries_readonly,
        valid,
        payload_key="entries",
    )


@router.get("/index")
async def get_review_queue_index(project_id: str, request: Request) -> dict[str, Any]:
    await _reject_request_body(request, project_id)
    valid = _read_request(project_id=project_id, request=request)
    return _readonly_response(
        review_api.get_review_queue_index_readonly,
        valid,
        payload_key="index",
    )


@router.get("/summary")
async def get_review_queue_summary(project_id: str, request: Request) -> dict[str, Any]:
    await _reject_request_body(request, project_id)
    valid = _read_request(project_id=project_id, request=request)
    return _readonly_response(
        review_api.get_review_queue_summary_readonly,
        valid,
        payload_key="summary",
    )


@router.get("/{queue_entry_id}")
async def get_review_queue_entry(
    project_id: str,
    queue_entry_id: str,
    request: Request,
) -> dict[str, Any]:
    await _reject_request_body(request, project_id)
    valid = _read_request(
        project_id=project_id,
        queue_entry_id=queue_entry_id,
        request=request,
    )
    return _readonly_response(
        review_api.get_review_queue_entry_readonly,
        valid,
        payload_key="entry",
    )
