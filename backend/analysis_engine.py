from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import requests

try:
    from . import analysis_modes, analysis_normalizer, guardrails, project_manager
    from .story_check_grounding_contract import build_story_check_source_snapshot
    from .story_check_grounding_integration import (
        StoryCheckGroundingIntegrationError,
        build_story_check_grounding_failure,
        ground_story_check_result,
    )
    from .storyform import Storyform
except ImportError:  # pragma: no cover - supports direct execution from backend/
    import analysis_modes
    import analysis_normalizer
    import guardrails
    import project_manager
    from story_check_grounding_contract import build_story_check_source_snapshot
    from story_check_grounding_integration import (
        StoryCheckGroundingIntegrationError,
        build_story_check_grounding_failure,
        ground_story_check_result,
    )
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
    source_snapshot = None
    try:
        scene_text = project_manager.load_scene(project_name, scene_id)
        source_snapshot = build_story_check_source_snapshot(
            project_id=project_name,
            source_type="scene",
            source_id=scene_id,
            source_content=scene_text,
        )
        mode = analysis_modes.get_analysis_mode()
        if mode == analysis_modes.MOCK:
            return ground_story_check_result(
                _load_mock_story_check_response(), source_snapshot
            )

        timeout_seconds = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "300"))
        storyform_context = Storyform.from_file(project_name).to_prompt_context()
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

        return ground_story_check_result(
            _parse_story_check_response(content), source_snapshot
        )
    except StoryCheckGroundingIntegrationError as exc:
        if source_snapshot is not None:
            return build_story_check_grounding_failure(source_snapshot, str(exc))
        return {"error": str(exc)}
    except Exception as e:
        return {"error": str(e)}
