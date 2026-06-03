from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import requests

try:
    from . import analysis_modes, analysis_normalizer, guardrails, project_manager
    from .storyform import Storyform
except ImportError:  # pragma: no cover - supports direct execution from backend/
    import analysis_modes
    import analysis_normalizer
    import guardrails
    import project_manager
    from storyform import Storyform


PROMPT_PATH = Path(__file__).resolve().parent / "prompts" / "story_check.txt"
MOCK_STORY_CHECK_PATH = Path(__file__).resolve().parent / "mock_responses" / "story_check.json"
DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL = "qwen3:8b"
OLLAMA_STORY_CHECK_NUM_PREDICT = 2048


def _parse_story_check_response(content: str) -> dict[str, Any]:
    return guardrails.sanitize_story_check_output(
        analysis_normalizer.normalize_story_check_output(content)
    )


def _load_mock_story_check_response() -> dict[str, Any]:
    payload = json.loads(MOCK_STORY_CHECK_PATH.read_text(encoding="utf-8"))
    return guardrails.sanitize_story_check_output(
        analysis_normalizer.normalize_story_check_output(payload)
    )


def _ollama_chat_url() -> str:
    base_url = os.getenv("OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL).rstrip("/")
    return f"{base_url}/api/chat"


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
            _ollama_chat_url(),
            json={
                "model": os.getenv("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL),
                "messages": [{"role": "user", "content": prompt}],
                "format": "json",
                "think": False,
                "options": {
                    "temperature": 0,
                    "num_predict": OLLAMA_STORY_CHECK_NUM_PREDICT,
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
