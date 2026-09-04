"""Canonical OMI synchronous analysis-run control-plane routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.story_knowledge import analysis_run_control


router = APIRouter(prefix="/api/projects/{project_id}/omi/analysis")
_delete_route = getattr(router, "delete", router.post)


class AnalysisRunSubmit(BaseModel):
    raw_idea: str
    source_idea_id: str | None = None
    requested_adapters: list[str]
    allow_deterministic_fallback: bool = False
    idempotency_key: str | None = None

    class Config:
        extra = "forbid"


class ArtifactDeletionRequest(BaseModel):
    deletion_id: str
    owner_controlled: bool

    class Config:
        extra = "forbid"


def _raise(exc: Exception) -> None:
    if isinstance(exc, FileNotFoundError):
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    message = str(exc)
    status = 409 if "conflict" in message or "collision" in message else 400
    raise HTTPException(status_code=status, detail=message) from exc


@router.get("/tools")
def get_supported_analysis_tools(project_id: str) -> dict:
    try:
        return analysis_run_control.supported_analysis_tools(project_id)
    except (ValueError, FileNotFoundError) as exc:
        _raise(exc)


@router.post("/runs")
def submit_analysis_run(project_id: str, payload: AnalysisRunSubmit) -> dict:
    try:
        return analysis_run_control.submit_analysis_run(
            project_id,
            raw_idea=payload.raw_idea,
            source_idea_id=payload.source_idea_id,
            requested_adapters=payload.requested_adapters,
            allow_deterministic_fallback=payload.allow_deterministic_fallback,
            idempotency_key=payload.idempotency_key,
        )
    except (ValueError, FileNotFoundError) as exc:
        _raise(exc)


@router.get("/runs/{run_id}")
def get_analysis_run_status(project_id: str, run_id: str) -> dict:
    try:
        return analysis_run_control.get_analysis_run_status(project_id, run_id)
    except (ValueError, FileNotFoundError) as exc:
        _raise(exc)


@router.get("/runs/{run_id}/result")
def get_analysis_run_result(project_id: str, run_id: str) -> dict:
    try:
        return analysis_run_control.get_analysis_run_result(project_id, run_id)
    except (ValueError, FileNotFoundError) as exc:
        _raise(exc)


@_delete_route("/runs/{run_id}/artifacts")
def delete_analysis_run_artifacts(
    project_id: str, run_id: str, payload: ArtifactDeletionRequest
) -> dict:
    try:
        return analysis_run_control.delete_analysis_run_artifacts(
            project_id,
            run_id,
            deletion_id=payload.deletion_id,
            owner_controlled=payload.owner_controlled,
        )
    except (ValueError, FileNotFoundError) as exc:
        _raise(exc)


__all__ = ["router"]
