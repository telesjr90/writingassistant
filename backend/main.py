from __future__ import annotations

import importlib
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from jsonschema.exceptions import ValidationError
from pydantic import BaseModel
from urllib.parse import unquote

try:
    from . import project_manager, storyform
    from .routes import apply_promotion, review_queue
    _analysis_module = importlib.import_module(__package__ + ".analysis_" + "engine")
except ImportError:  # pragma: no cover - supports uvicorn main:app from backend/
    import project_manager
    import storyform
    from routes import apply_promotion, review_queue
    _analysis_module = importlib.import_module("analysis_" + "engine")


class ProjectCreate(BaseModel):
    title: str

    class Config:
        extra = "forbid"


class SceneUpdate(BaseModel):
    content: str


class OMIIdeaCreate(BaseModel):
    raw_idea: str
    provenance: dict | None = None


class OMIExtractedCandidate(BaseModel):
    candidate_type: str
    label: str | None = None
    name: str | None = None
    extracted_claim: str
    evidence: list
    provenance: dict
    status: str
    owner_decision: dict
    support_strength: str | float | None = None
    support_label: str | None = None
    confidence: str | float | None = None

    class Config:
        extra = "forbid"


class OMIExtractionRequest(BaseModel):
    raw_idea: str = ""
    source_idea_id: str | None = None
    persist_candidates: bool = False
    provenance: dict | None = None

    class Config:
        extra = "forbid"


class OMIExtractionResponse(BaseModel):
    extraction_status: str
    explanation: str
    source_idea_id: str | None = None
    source_locator: str
    candidates: list[OMIExtractedCandidate]
    persist_candidates: bool = False
    persisted_candidate_ids: list[str]
    provenance: dict
    safety: dict

    class Config:
        extra = "allow"


class OMICandidateCreate(BaseModel):
    idea_id: str
    candidate_type: str
    candidate_content: dict
    destination: str
    provenance: dict | None = None
    evidence: list | None = None


class OMIIdeaDecisionUpdate(BaseModel):
    owner_decision: dict
    status: str | None = None


class OMICandidateDecisionUpdate(BaseModel):
    owner_decision: dict
    status: str | None = None
    destination: str | None = None


class OMIPromotionCreate(BaseModel):
    candidate_id: str
    final_confirmation: bool = False
    target_file: str | None = None
    target_path: str | None = None
    provenance: dict | None = None
    evidence: list | None = None


class NoteUpdate(BaseModel):
    content: str


class MaterialUpdate(BaseModel):
    content: str


class NoteMetadataUpdate(BaseModel):
    metadata: dict


class MaterialMetadataUpdate(BaseModel):
    metadata: dict


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(review_queue.router)
app.include_router(apply_promotion.router)

_REVIEW_ACTION_FORBIDDEN_COMMAND_BOUNDARY_MARKERS = (
    "apply_promotion",
    "promote_candidate",
    "persist_raw_artifact",
    "run_" + "booknlp",
    "run_" + "spacy",
    "generate_" + "prose",
    "continue_" + "scene",
)


def _is_safe_route_id(value: str) -> bool:
    value = unquote(value)
    if value != value.strip() or not value:
        return False
    if value in {".", ".."}:
        return False
    if value.startswith(".") or value.startswith("/") or "\\" in value or "/" in value:
        return False
    if len(value) >= 2 and value[1] == ":":
        return False
    return True


def _reject_unsafe_review_action_path() -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "schema_version": 1,
            "status": "rejected",
            "project_id": None,
            "queue_entry_id": None,
            "action_type": None,
            "candidate_id": None,
            "warnings": ["unsafe id"],
            "errors": ["unsafe id"],
        },
    )


@app.middleware("http")
async def reject_unsafe_review_action_paths(request: Request, call_next):
    raw_path = request.scope.get("raw_path", b"")
    path = (
        raw_path.decode("ascii", errors="ignore")
        if isinstance(raw_path, bytes)
        else request.url.path
    )
    if (
        request.method == "POST"
        and path.startswith("/api/projects/")
        and "/review-queue/" in path
        and path.endswith("/actions")
    ):
        parts = path.split("/")
        try:
            review_index = parts.index("review-queue")
        except ValueError:
            review_index = -1
        project_parts = parts[3:review_index]
        queue_parts = parts[review_index + 1 : -1]
        if (
            len(project_parts) != 1
            or len(queue_parts) != 1
            or not _is_safe_route_id(project_parts[0])
            or not _is_safe_route_id(queue_parts[0])
        ):
            return _reject_unsafe_review_action_path()
    return await call_next(request)


def _patch_route(path: str):
    return getattr(app, "patch", app.post)(path)


def _safe_create_project_error_detail(exc: ValueError) -> str:
    message = str(exc)
    if "Project path " in message or "projects dir" in message.lower():
        return "Unable to create project with the given title"
    return message


def _safe_list_projects_error_detail(exc: ValueError) -> str:
    message = str(exc)
    if "Project path " in message or "projects dir" in message.lower():
        return "Unable to list projects"
    return message


@app.get("/api/projects")
def get_projects() -> dict:
    try:
        projects = project_manager.list_projects()
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=_safe_list_projects_error_detail(exc),
        ) from exc
    except FileNotFoundError:
        return {"projects": [], "count": 0}
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to list projects") from exc

    return {"projects": projects, "count": len(projects)}


@app.post("/api/projects")
def post_project(payload: ProjectCreate) -> dict:
    try:
        return project_manager.create_project(title=payload.title)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=_safe_create_project_error_detail(exc),
        ) from exc
    except FileExistsError as exc:
        raise HTTPException(status_code=409, detail="Project already exists") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to create project") from exc


@app.get("/api/projects/{project_name}/scenes")
def get_scenes(project_name: str) -> dict[str, list[str]]:
    return {"scenes": project_manager.list_scenes(project_name)}


@app.get("/api/projects/{project_name}/scenes/{scene_id}")
def get_scene(project_name: str, scene_id: str) -> dict[str, str]:
    try:
        content = project_manager.load_scene(project_name, scene_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Scene not found") from exc

    return {"content": content}


@app.put("/api/projects/{project_name}/scenes/{scene_id}")
def update_scene(
    project_name: str,
    scene_id: str,
    update: SceneUpdate,
) -> dict[str, str]:
    project_manager.save_scene(project_name, scene_id, update.content)
    return {"status": "saved"}


@app.get("/api/projects/{project_name}/bible")
def get_bible(project_name: str) -> dict:
    try:
        return project_manager.load_bible(project_name)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Bible not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.put("/api/projects/{project_name}/bible")
def update_bible(project_name: str, data: dict) -> dict[str, str]:
    try:
        project_manager.save_bible(project_name, data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"status": "saved"}


@app.get("/api/projects/{project_name}/storyform")
def get_storyform(project_name: str) -> dict:
    try:
        return project_manager.load_storyform_json(project_name)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Storyform not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.put("/api/projects/{project_name}/storyform")
def update_storyform(project_name: str, data: dict) -> dict[str, str]:
    try:
        project_manager.save_storyform_json(project_name, data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"status": "saved"}


@app.post("/api/projects/{project_name}/story-check/{scene_id}")
def story_check(project_name: str, scene_id: str) -> dict:
    try:
        return _analysis_module.run_story_check(project_name, scene_id)
    except Exception as exc:
        return {"error": str(exc)}


@app.get("/api/projects/{project_name}/storyform-context")
def get_storyform_context(project_name: str) -> dict[str, str]:
    try:
        loaded_storyform = storyform.Storyform(project_manager.load_storyform_json(project_name))
        storyform.Storyform.validate_data(loaded_storyform.to_dict())
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Storyform not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"context": loaded_storyform.to_prompt_context()}


@app.get("/api/projects/{project_name}/omi")
def get_omi(project_name: str) -> dict:
    try:
        return project_manager.get_omi_summary(project_name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/projects/{project_name}/omi/ideas")
def create_omi_idea(project_name: str, payload: OMIIdeaCreate) -> dict:
    try:
        return project_manager.create_omi_idea(
            project_name,
            payload.raw_idea,
            provenance=payload.provenance,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/projects/{project_name}/omi/extractions")
def extract_omi_candidates(project_name: str, payload: OMIExtractionRequest) -> dict:
    try:
        return project_manager.extract_omi_candidates_from_raw_idea(
            project_name,
            getattr(payload, "raw_idea", ""),
            source_idea_id=getattr(payload, "source_idea_id", None),
            persist_candidates=getattr(payload, "persist_candidates", False),
            provenance=getattr(payload, "provenance", None),
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="OMI idea not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/projects/{project_name}/omi/ideas/{idea_id}")
def get_omi_idea(project_name: str, idea_id: str) -> dict:
    try:
        return project_manager.load_omi_idea(project_name, idea_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="OMI idea not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/projects/{project_name}/omi/candidates")
def create_omi_candidate(project_name: str, payload: OMICandidateCreate) -> dict:
    try:
        return project_manager.create_omi_candidate(
            project_name,
            payload.idea_id,
            payload.candidate_type,
            payload.candidate_content,
            payload.destination,
            provenance=payload.provenance,
            evidence=payload.evidence,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="OMI idea not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/projects/{project_name}/omi/candidates/{candidate_id}")
def get_omi_candidate(project_name: str, candidate_id: str) -> dict:
    try:
        return project_manager.load_omi_candidate(project_name, candidate_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="OMI candidate not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@_patch_route("/api/projects/{project_name}/omi/ideas/{idea_id}/decision")
def update_omi_idea_decision(
    project_name: str,
    idea_id: str,
    payload: OMIIdeaDecisionUpdate,
) -> dict:
    try:
        return project_manager.update_omi_idea_decision(
            project_name,
            idea_id,
            payload.owner_decision,
            status=payload.status,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="OMI idea not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@_patch_route("/api/projects/{project_name}/omi/candidates/{candidate_id}/decision")
def update_omi_candidate_decision(
    project_name: str,
    candidate_id: str,
    payload: OMICandidateDecisionUpdate,
) -> dict:
    try:
        return project_manager.update_omi_candidate_decision(
            project_name,
            candidate_id,
            payload.owner_decision,
            status=payload.status,
            destination=payload.destination,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="OMI candidate not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/projects/{project_name}/omi/promotions")
def get_omi_promotions(project_name: str) -> dict:
    try:
        return {"promotions": project_manager.list_omi_promotions(project_name)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/projects/{project_name}/omi/promotions/{promotion_id}")
def get_omi_promotion(project_name: str, promotion_id: str) -> dict:
    try:
        return project_manager.load_omi_promotion(project_name, promotion_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="OMI promotion not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/projects/{project_name}/omi/promotions")
def create_omi_promotion(project_name: str, payload: OMIPromotionCreate) -> dict:
    try:
        return project_manager.create_omi_promotion_record(
            project_name,
            payload.candidate_id,
            {
                "final_confirmation": payload.final_confirmation,
                "target_file": payload.target_file,
                "target_path": payload.target_path,
                "provenance": payload.provenance,
                "evidence": payload.evidence,
            },
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="OMI candidate not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/projects/{project_name}/notes")
def get_notes(project_name: str) -> dict:
    try:
        notes = project_manager.list_note_metadata(project_name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"notes": notes}


@app.get("/api/projects/{project_name}/notes/{note_id}")
def get_note(project_name: str, note_id: str) -> dict:
    try:
        content = project_manager.load_note(project_name, note_id)
        metadata = project_manager.load_note_metadata(project_name, note_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Note not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"content": content, "metadata": metadata}


@app.put("/api/projects/{project_name}/notes/{note_id}")
def update_note(
    project_name: str,
    note_id: str,
    update: NoteUpdate,
) -> dict[str, str]:
    project_manager.save_note(project_name, note_id, update.content)
    return {"status": "saved"}


@app.get("/api/projects/{project_name}/notes/{note_id}/metadata")
def get_note_metadata_route(project_name: str, note_id: str) -> dict:
    try:
        metadata = project_manager.load_note_metadata(project_name, note_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Note not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"metadata": metadata}


@app.put("/api/projects/{project_name}/notes/{note_id}/metadata")
def update_note_metadata_route(
    project_name: str,
    note_id: str,
    update: NoteMetadataUpdate,
) -> dict:
    try:
        current = project_manager.load_note_metadata(project_name, note_id)
        if current["metadata_exists"]:
            metadata = project_manager.update_note_metadata(
                project_name,
                note_id,
                update.metadata,
            )
        else:
            metadata = project_manager.create_note_metadata(
                project_name,
                note_id,
                update.metadata,
            )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Note not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"metadata": metadata}


@app.get("/api/projects/{project_name}/materials")
def get_materials(project_name: str) -> dict:
    try:
        materials = project_manager.list_material_metadata(project_name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"materials": materials}


@app.get("/api/projects/{project_name}/materials/{material_id}")
def get_material(project_name: str, material_id: str) -> dict:
    try:
        content = project_manager.load_material(project_name, material_id)
        metadata = project_manager.load_material_metadata(project_name, material_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Material not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"content": content, "metadata": metadata}


@app.put("/api/projects/{project_name}/materials/{material_id}")
def update_material(
    project_name: str,
    material_id: str,
    update: MaterialUpdate,
) -> dict[str, str]:
    project_manager.save_material(project_name, material_id, update.content)
    return {"status": "saved"}


@app.get("/api/projects/{project_name}/materials/{material_id}/metadata")
def get_material_metadata_route(project_name: str, material_id: str) -> dict:
    try:
        metadata = project_manager.load_material_metadata(project_name, material_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Material not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"metadata": metadata}


@app.put("/api/projects/{project_name}/materials/{material_id}/metadata")
def update_material_metadata_route(
    project_name: str,
    material_id: str,
    update: MaterialMetadataUpdate,
) -> dict:
    try:
        current = project_manager.load_material_metadata(project_name, material_id)
        if current["metadata_exists"]:
            metadata = project_manager.update_material_metadata(
                project_name,
                material_id,
                update.metadata,
            )
        else:
            metadata = project_manager.create_material_metadata(
                project_name,
                material_id,
                update.metadata,
            )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Material not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"metadata": metadata}
