from __future__ import annotations

import re
from typing import Any


STANDARD_REFUSAL_MESSAGE = (
    "I can analyze structure and ask diagnostic questions, but I cannot write or rewrite story prose."
)

ALLOWED_HELP = [
    "analysis",
    "diagnostic questions",
    "structural classification",
]

OWNER_AUTHORED_CONTENT_FIELDS = {
    "bible",
    "bible_json",
    "content",
    "context",
    "note",
    "notes",
    "owner_memory",
    "planning_note",
    "planning_notes",
    "raw_idea",
    "scene",
    "scene_text",
    "storyform",
    "storyform_json",
}

FREEFORM_REQUEST_FIELDS = {
    "analysis_request",
    "assistant_request",
    "freeform_request",
    "instruction",
    "model_request",
    "prompt",
    "request",
    "raw_instruction",
    "user_request",
    "writer_request",
}


_REQUEST_PREFIX = (
    r"(?:^\s*(?:please\s+)?|"
    r"\b(?:can you|could you|would you|will you|i need you to|i want you to|"
    r"help me|give me|make this|turn this into)\s+)"
)

_PROSE_TARGET = (
    r"(?:scene|next scene|chapter|paragraph|opening|ending|monologue|dialogue|"
    r"passage|story prose|prose|text|story|writing)"
)

_REQUEST_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "prose_imitation",
        re.compile(
            rf"{_REQUEST_PREFIX}(?:imitate|mimic)\b.{{0,80}}\b(?:author|style|voice|tone)\b|"
            rf"{_REQUEST_PREFIX}write\s+in\s+the\s+style\s+of\b",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
    (
        "prose_continuation",
        re.compile(
            rf"{_REQUEST_PREFIX}(?:continue|finish|extend)\b.{{0,80}}\b{_PROSE_TARGET}\b",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
    (
        "prose_rewrite",
        re.compile(
            rf"{_REQUEST_PREFIX}(?:rewrite|revise)\b.{{0,80}}\b{_PROSE_TARGET}\b",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
    (
        "prose_improvement",
        re.compile(
            rf"{_REQUEST_PREFIX}(?:polish|improve)\b.{{0,80}}\b(?:prose|text|writing|scene|paragraph|chapter|dialogue)\b|"
            rf"{_REQUEST_PREFIX}make\s+this\s+sound\s+better\b",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
    (
        "prose_generation",
        re.compile(
            rf"{_REQUEST_PREFIX}(?:write|draft|compose|generate|create)\b.{{0,80}}\b{_PROSE_TARGET}\b|"
            rf"{_REQUEST_PREFIX}give\s+me\s+the\s+actual\s+prose\b",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
)


def classify_request(text: str) -> str | None:
    if not isinstance(text, str) or not text.strip():
        return None

    for request_type, pattern in _REQUEST_PATTERNS:
        if pattern.search(text):
            return request_type
    return None


def is_prose_generation_request(text: str) -> bool:
    return classify_request(text) is not None


def is_owner_authored_content_field(field_name: str) -> bool:
    if not isinstance(field_name, str):
        return False

    normalized = field_name.strip().lower()
    return normalized in OWNER_AUTHORED_CONTENT_FIELDS


def should_guard_request_field(field_name: str) -> bool:
    if not isinstance(field_name, str):
        return False

    normalized = field_name.strip().lower()
    if is_owner_authored_content_field(normalized):
        return False

    return normalized in FREEFORM_REQUEST_FIELDS or normalized.endswith("_request")


def guard_freeform_request(text: str) -> dict[str, Any] | None:
    request_type = classify_request(text)
    if request_type is None:
        return None

    return refusal_response(request_type=request_type)


def refusal_response(request_type: str = "prose_generation") -> dict[str, Any]:
    return {
        "task": "out_of_scope_refusal",
        "request_type": request_type,
        "allowed_help": list(ALLOWED_HELP),
        "message": STANDARD_REFUSAL_MESSAGE,
    }


def output_appears_to_contain_prose_generation(value: Any) -> bool:
    if isinstance(value, str):
        return is_prose_generation_request(value)

    if isinstance(value, dict):
        return any(output_appears_to_contain_prose_generation(item) for item in value.values())

    if isinstance(value, list):
        return any(output_appears_to_contain_prose_generation(item) for item in value)

    return False
