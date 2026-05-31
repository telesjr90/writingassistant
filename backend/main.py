from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

try:
    from . import analysis_engine, project_manager, storyform
except ImportError:  # pragma: no cover - supports uvicorn main:app from backend/
    import analysis_engine
    import project_manager
    import storyform


class SceneUpdate(BaseModel):
    content: str


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/projects/{project_name}/scenes")
def get_scenes(project_name: str) -> dict[str, list[str]]:
    return {"scenes": project_manager.list_scenes(project_name)}


@app.get("/api/projects/{project_name}/scenes/{scene_id}")
def get_scene(project_name: str, scene_id: str) -> dict[str, str]:
    try:
        content = project_manager.load_scene(project_name, scene_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Scene not found") from exc

    if not content:
        raise HTTPException(status_code=404, detail="Scene not found")

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
    return project_manager.load_bible(project_name)


@app.post("/api/projects/{project_name}/story-check/{scene_id}")
def story_check(project_name: str, scene_id: str) -> dict:
    try:
        return analysis_engine.run_story_check(project_name, scene_id)
    except Exception as exc:
        return {"error": str(exc)}


@app.get("/api/projects/{project_name}/storyform-context")
def get_storyform_context(project_name: str) -> dict[str, str]:
    loaded_storyform = storyform.Storyform.from_file(project_name)
    return {"context": loaded_storyform.to_prompt_context()}
