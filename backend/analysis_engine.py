from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

import requests

try:
    from jsonschema import Draft202012Validator as JsonSchemaValidator
except ImportError:  # pragma: no cover - runtime can still normalize without schema validation
    JsonSchemaValidator = None  # type: ignore[assignment]

try:
    from . import project_manager
    from .storyform import Storyform
except ImportError:  # pragma: no cover - supports direct execution from backend/
    import project_manager
    from storyform import Storyform


PROMPT_PATH = Path(__file__).resolve().parent / "prompts" / "story_check.txt"
STORY_CHECK_SCHEMA_PATH = Path(__file__).resolve().parent.parent / "training" / "schemas" / "story_check.schema.json"
OLLAMA_CHAT_URL = os.getenv("OLLAMA_CHAT_URL", "http://localhost:11434/api/chat")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:8b")
ALLOWED_WARNING_PREFIXES = (
    "[Plot/Temporal]",
    "[Character]",
    "[Worldbuilding]",
    "[Factual]",
    "[Stylistic]",
)
PROSE_GENERATION_RE = re.compile(
    r"\b(?:write|draft|compose|generate|rewrite|revise|polish|improve|continue|finish|extend)\b"
    r".{0,80}\b(?:scene|chapter|paragraph|prose|dialogue|monologue|passage|text|story)\b",
    re.IGNORECASE,
)


def _fallback_response(message: str, *, raw_content: str | None = None) -> dict[str, Any]:
    response: dict[str, Any] = {
        "coherence_score": 0,
        "warnings": [f"[Factual] {message}"],
        "suggestions": [],
        "diagnostics": {
            "task": "story_check",
            "schema_valid": False,
            "parser_warning": message,
            "insufficient_evidence": ["A valid JSON Story Check response was not available."],
        },
    }
    if raw_content is not None:
        response["raw_diagnostics"] = {"raw_content": raw_content[:4000]}
    return response


def _coerce_score(value: Any) -> int:
    try:
        score = int(value)
    except (TypeError, ValueError):
        return 0
    return max(0, min(10, score))


def _list_of_strings(value: Any, *, limit: int | None = None) -> list[str]:
    if not isinstance(value, list):
        return []
    items = [item.strip() for item in value if isinstance(item, str) and item.strip()]
    return items[:limit] if limit is not None else items


def _normalize_warning(value: str) -> str:
    warning = value.strip()
    if warning.startswith(ALLOWED_WARNING_PREFIXES):
        return warning
    return f"[Factual] {warning}"


def _normalize_warnings(value: Any) -> list[str]:
    warnings = [_normalize_warning(item) for item in _list_of_strings(value, limit=5)]
    return warnings


def _is_safe_question(value: str) -> bool:
    text = value.strip()
    return text.endswith("?") and PROSE_GENERATION_RE.search(text) is None


def _normalize_suggestions(value: Any) -> list[str]:
    questions = [item.strip() for item in _list_of_strings(value, limit=3) if _is_safe_question(item)]
    return questions


def _story_check_schema_errors(parsed: dict[str, Any]) -> list[str]:
    if JsonSchemaValidator is None or not STORY_CHECK_SCHEMA_PATH.exists():
        return []
    try:
        schema = json.loads(STORY_CHECK_SCHEMA_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    validator = JsonSchemaValidator(schema)
    errors: list[str] = []
    for error in sorted(validator.iter_errors(parsed), key=lambda item: list(item.absolute_path)):
        path = ".".join(str(part) for part in error.absolute_path) or "$"
        errors.append(f"{path}: {error.message}")
    return errors


def _looks_like_rich_story_check(parsed: dict[str, Any]) -> bool:
    return parsed.get("task") == "story_check" or any(
        key in parsed
        for key in (
            "throughline_alignment",
            "theme_drift",
            "character_consistency",
            "insufficient_evidence",
        )
    )


def _normalize_story_check(parsed: dict[str, Any]) -> dict[str, Any]:
    warnings = _normalize_warnings(parsed.get("warnings"))
    suggestions = _normalize_suggestions(parsed.get("suggestions"))
    response: dict[str, Any] = {
        "coherence_score": _coerce_score(parsed.get("coherence_score")),
        "warnings": warnings,
        "suggestions": suggestions,
    }

    if _looks_like_rich_story_check(parsed):
        schema_errors = _story_check_schema_errors(parsed)
        diagnostics = dict(parsed)
        diagnostics["schema_valid"] = not schema_errors
        if schema_errors:
            diagnostics["schema_errors"] = schema_errors
            response["warnings"] = (
                warnings + ["[Factual] Story Check diagnostics did not fully match the Phase 2 schema."]
            )[:5]
        response["diagnostics"] = diagnostics
    else:
        response["diagnostics"] = {
            "task": "story_check",
            "schema_valid": False,
            "legacy_small_schema": True,
            "insufficient_evidence": [],
        }

    if not response["warnings"] and not response["suggestions"]:
        response["warnings"] = ["[Factual] Story Check response contained no warnings or diagnostic questions."]
    return response


def _parse_story_check_response(content: str) -> dict[str, Any]:
    try:
        parsed = json.loads(content)
    except (TypeError, json.JSONDecodeError):
        return _fallback_response("Failed to parse LLM response", raw_content=content)

    if not isinstance(parsed, dict):
        return _fallback_response("Failed to parse LLM response", raw_content=content)

    return _normalize_story_check(parsed)


def run_story_check(project_name: str, scene_id: str) -> dict[str, Any]:
    try:
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
                "model": OLLAMA_MODEL,
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
