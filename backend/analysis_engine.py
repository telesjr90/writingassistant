from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import requests

try:
    from . import analysis_modes, analysis_normalizer, project_manager
    from .storyform import Storyform
except ImportError:  # pragma: no cover - supports direct execution from backend/
    import analysis_modes
    import analysis_normalizer
    import project_manager
    from storyform import Storyform


PROMPT_PATH = Path(__file__).resolve().parent / "prompts" / "story_check.txt"
MOCK_STORY_CHECK_PATH = Path(__file__).resolve().parent / "mock_responses" / "story_check.json"
OLLAMA_CHAT_URL = os.getenv("OLLAMA_CHAT_URL", "http://localhost:11434/api/chat")
DEFAULT_OLLAMA_MODEL = "qwen3:8b"


def _parse_story_check_response(content: str) -> dict[str, Any]:
    return analysis_normalizer.normalize_story_check_output(content)


def _load_mock_story_check_response() -> dict[str, Any]:
    payload = json.loads(MOCK_STORY_CHECK_PATH.read_text(encoding="utf-8"))
    return analysis_normalizer.normalize_story_check_output(payload)


def run_story_check(project_name: str, scene_id: str) -> dict[str, Any]:
    try:
        mode = analysis_modes.get_analysis_mode()
        if mode == analysis_modes.MOCK:
            return _load_mock_story_check_response()

        timeout_seconds = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "300"))
        storyform_context = Storyform.from_file(project_name).to_prompt_context()
        scene_text = project_manager.load_scene(project_name, scene_id)
        bible_summary = json.dumps(
            project_manager.load_bible(project_name),
            indent=2,
            ensure_ascii=False,
        )
        prompt_template = PROMPT_PATH.read_text(encoding="utf-8")
        prompt = prompt_template.format(
            storyform_context=storyform_context,
            scene_text=scene_text,
            bible_summary=bible_summary,
        )

        response = requests.post(
            OLLAMA_CHAT_URL,
            json={
                "model": os.getenv("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL),
                "messages": [{"role": "user", "content": prompt}],
                "format": "json",
                "think": False,
                "options": {
                    "temperature": 0,
                    "num_predict": 512,
                },
                "stream": False,
            },
            timeout=timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        content = payload.get("message", {}).get("content", "")

        return _parse_story_check_response(content)
    except Exception as e:
        return {"error": str(e)}
