"""Minimal apply-promotion FastAPI route."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from backend import project_manager
from backend.story_knowledge import apply_promotion


router = APIRouter(prefix="/api/projects/{project_id}/apply-promotion")


def _minimal_candidate_record(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "candidate_id": payload.get("candidate_id"),
        "project_id": payload.get("project_id"),
        "candidate_type": payload.get("candidate_type"),
        "candidate_payload": payload.get("approved_payload", {}),
        "snapshot_hash": payload.get("source_candidate_snapshot_hash"),
    }


@router.post("")
def post_apply_promotion(project_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    body = dict(payload)
    if body.get("project_id") is not None and body["project_id"] != project_id:
        raise HTTPException(
            status_code=400,
            detail={
                "validation_status": "rejected",
                "errors": ["project_id"],
                "mutation_performed": False,
            },
        )
    body["project_id"] = project_id

    validated = apply_promotion.validate_promotion_request(body)
    if validated["validation_status"] != "valid":
        raise HTTPException(status_code=400, detail=validated)

    candidate_record = body.get("candidate_record")
    if candidate_record is None:
        candidate_record = _minimal_candidate_record(body)
    queue_entry = body.get("queue_entry")

    try:
        plan = apply_promotion.build_promotion_plan(
            body,
            candidate_record=candidate_record,
            queue_entry=queue_entry,
        )
        if plan.get("validation_status") != "valid":
            raise ValueError("invalid promotion plan")
        result = apply_promotion.apply_promotion_plan(
            plan,
            project_dir=project_manager.PROJECTS_DIR / project_id,
        )
    except (FileExistsError, ValueError) as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "validation_status": "rejected",
                "errors": [str(exc)],
                "mutation_performed": False,
            },
        ) from exc

    if result.get("promotion_status") not in {"applied", "dry_run"}:
        raise HTTPException(status_code=400, detail=result)
    return {"promotion_plan": plan, "promotion_result": result}
