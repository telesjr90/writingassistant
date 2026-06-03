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

OUTPUT_GUARD_NOTE = "Output guard removed unsafe model-authored content."
OUTPUT_GUARD_INSUFFICIENT_EVIDENCE = (
    "Output guard removed model-authored prose-generation content; rerun analysis for safe diagnostics."
)

_OUTPUT_LEAKAGE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bhere\s+is\s+(?:a\s+)?(?:rewritten|revised|polished)\s+version\b", re.IGNORECASE),
    re.compile(r"\bcontinue\s+the\s+scene\s+with\b", re.IGNORECASE),
    re.compile(r"\bnew\s+dialogue\s*:", re.IGNORECASE),
    re.compile(r"\bdrafted\s+paragraph\s*:", re.IGNORECASE),
    re.compile(r"\bpolished\s+paragraph\s*:", re.IGNORECASE),
    re.compile(r"\bpolished\s+version\s*:", re.IGNORECASE),
    re.compile(r"\bin\s+the\s+style\s+of\b", re.IGNORECASE),
)


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


def output_text_appears_unsafe(text: str) -> bool:
    if not isinstance(text, str) or not text.strip():
        return False
    if is_prose_generation_request(text):
        return True
    return any(pattern.search(text) for pattern in _OUTPUT_LEAKAGE_PATTERNS)


def is_evidence_path(path: tuple[str, ...]) -> bool:
    return "evidence" in path


def sanitize_model_authored_text(value: str) -> tuple[str | None, bool]:
    if output_text_appears_unsafe(value):
        return None, True
    return value, False


def output_guard_diagnostics(triggered: bool, removed_count: int) -> dict[str, Any]:
    return {
        "output_guard_triggered": triggered,
        "output_guard_removed_count": removed_count,
    }


def sanitize_story_check_output(value: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(value, dict):
        return value

    sanitized, removed_count = _sanitize_output_value(value, ())
    if not isinstance(sanitized, dict):
        sanitized = {}

    if removed_count == 0:
        diagnostics = dict(sanitized.get("diagnostics")) if isinstance(sanitized.get("diagnostics"), dict) else {}
        diagnostics.update(output_guard_diagnostics(False, 0))
        sanitized["diagnostics"] = diagnostics
        return sanitized

    if removed_count >= 3:
        return {
            "task": "story_check",
            "coherence_score": 0,
            "warnings": ["[Factual] Model output included unsafe prose-generation content and was blocked."],
            "suggestions": [],
            "insufficient_evidence": [OUTPUT_GUARD_INSUFFICIENT_EVIDENCE],
            "diagnostics": {
                "task": "story_check",
                "schema_valid": False,
                "output_guard_triggered": True,
                "output_guard_removed_count": removed_count,
                "output_guard_severity": "severe",
                "message": STANDARD_REFUSAL_MESSAGE,
            },
        }

    warnings = list(sanitized.get("warnings")) if isinstance(sanitized.get("warnings"), list) else []
    guard_warning = "[Factual] Output guard removed unsafe model-authored content."
    if guard_warning not in warnings:
        warnings.append(guard_warning)
    sanitized["warnings"] = warnings[:5]

    insufficient_evidence = (
        list(sanitized.get("insufficient_evidence"))
        if isinstance(sanitized.get("insufficient_evidence"), list)
        else []
    )
    if OUTPUT_GUARD_INSUFFICIENT_EVIDENCE not in insufficient_evidence:
        insufficient_evidence.append(OUTPUT_GUARD_INSUFFICIENT_EVIDENCE)
    sanitized["insufficient_evidence"] = insufficient_evidence

    diagnostics = dict(sanitized.get("diagnostics")) if isinstance(sanitized.get("diagnostics"), dict) else {}
    diagnostics.update(output_guard_diagnostics(True, removed_count))
    diagnostics["output_guard_note"] = OUTPUT_GUARD_NOTE
    sanitized["diagnostics"] = diagnostics
    return sanitized


def _sanitize_output_value(value: Any, path: tuple[str, ...]) -> tuple[Any, int]:
    if isinstance(value, str):
        if is_evidence_path(path):
            return value, 0
        sanitized, triggered = sanitize_model_authored_text(value)
        return sanitized, 1 if triggered else 0

    if isinstance(value, list):
        sanitized_items: list[Any] = []
        removed_count = 0
        for item in value:
            sanitized_item, item_removed_count = _sanitize_output_value(item, path)
            removed_count += item_removed_count
            if sanitized_item is not None:
                sanitized_items.append(sanitized_item)
        return sanitized_items, removed_count

    if isinstance(value, dict):
        sanitized_dict: dict[str, Any] = {}
        removed_count = 0
        for key, item in value.items():
            key_text = str(key)
            sanitized_item, item_removed_count = _sanitize_output_value(item, path + (key_text,))
            removed_count += item_removed_count
            if sanitized_item is None and item_removed_count:
                if key_text in {"reason", "parser_warning", "raw_content"}:
                    sanitized_dict[key] = OUTPUT_GUARD_NOTE
                continue
            sanitized_dict[key] = sanitized_item
        return sanitized_dict, removed_count

    return value, 0
