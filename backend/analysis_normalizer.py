from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft202012Validator as JsonSchemaValidator
except ImportError:  # pragma: no cover - normalizer still works without jsonschema
    JsonSchemaValidator = None  # type: ignore[assignment]

try:
    from . import guardrails
except ImportError:  # pragma: no cover - supports direct execution from backend/
    import guardrails


STORY_CHECK_SCHEMA_PATH = Path(__file__).resolve().parent.parent / "training" / "schemas" / "story_check.schema.json"
MISSING_JSON_EVIDENCE = "A valid JSON Story Check response was not available."
RAW_CONTENT_LIMIT = 4000
MAX_WARNINGS = 5
MAX_SUGGESTIONS = 5
MAX_EVIDENCE_ITEMS = 5
MAX_INSUFFICIENT_EVIDENCE = 10
ALLOWED_WARNING_PREFIXES = (
    "[Plot/Temporal]",
    "[Character]",
    "[Worldbuilding]",
    "[Factual]",
    "[Stylistic]",
)
THROUGHLINE_KEYS = (
    "overall_story",
    "main_character",
    "influence_character",
    "relationship_story",
)
THEME_DRIFT_STATUSES = {"none", "mild", "serious", "insufficient_evidence"}
CHARACTER_CONSISTENCY_STATUSES = {"consistent", "inconsistent", "insufficient_evidence"}


def extract_json_object(text: str) -> dict[str, Any] | None:
    if not isinstance(text, str) or not text.strip():
        return None

    stripped = text.strip()
    if stripped[0] in "[\"0123456789-tnf":
        return None

    decoder = json.JSONDecoder()
    if stripped.startswith("{"):
        try:
            parsed, end = decoder.raw_decode(stripped)
        except json.JSONDecodeError:
            return None
        if not isinstance(parsed, dict) or stripped[end:].strip():
            return None
        return parsed

    first_object_start = text.find("{")
    if first_object_start < 0:
        return None
    try:
        parsed, end = decoder.raw_decode(text[first_object_start:])
    except json.JSONDecodeError:
        return None
    if not isinstance(parsed, dict):
        return None

    after_object = text[first_object_start + end :]
    for index, char in enumerate(after_object):
        if char != "{":
            continue
        try:
            other, _ = decoder.raw_decode(after_object[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(other, dict):
            return None
    return parsed


def fallback_story_check_response(message: str, *, raw_content: str | None = None) -> dict[str, Any]:
    response: dict[str, Any] = {
        "task": "story_check",
        "coherence_score": 0,
        "warnings": [f"[Factual] {message}"],
        "suggestions": [],
        "insufficient_evidence": [MISSING_JSON_EVIDENCE],
        "diagnostics": {
            "task": "story_check",
            "schema_valid": False,
            "parser_warning": message,
            "insufficient_evidence": [MISSING_JSON_EVIDENCE],
        },
    }
    if raw_content is not None:
        response["raw_diagnostics"] = {"raw_content": raw_content[:RAW_CONTENT_LIMIT]}
    return response


def validate_story_check_schema(value: dict[str, Any]) -> tuple[bool, list[str]]:
    if JsonSchemaValidator is None or not STORY_CHECK_SCHEMA_PATH.exists():
        return False, ["Story Check schema validation unavailable."]
    try:
        schema = json.loads(STORY_CHECK_SCHEMA_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return False, [f"Story Check schema could not be loaded: {exc}"]

    validator = JsonSchemaValidator(schema)
    errors: list[str] = []
    for error in sorted(validator.iter_errors(value), key=lambda item: list(item.absolute_path)):
        path = ".".join(str(part) for part in error.absolute_path) or "$"
        errors.append(f"{path}: {error.message}")
    return not errors, errors


def normalize_story_check_output(raw_output: object, *, raw_content: str | None = None) -> dict[str, Any]:
    parsed: dict[str, Any] | None
    if isinstance(raw_output, dict):
        parsed = raw_output
    elif isinstance(raw_output, str):
        parsed = extract_json_object(raw_output)
        raw_content = raw_output if raw_content is None else raw_content
    else:
        parsed = None

    if parsed is None:
        return fallback_story_check_response("Failed to parse LLM response", raw_content=raw_content)

    normalized = _normalize_story_check_object(parsed)
    if raw_content is not None:
        normalized["raw_diagnostics"] = {"raw_content": raw_content[:RAW_CONTENT_LIMIT]}
    return normalized


def _normalize_story_check_object(parsed: dict[str, Any]) -> dict[str, Any]:
    warnings = _normalize_warnings(parsed.get("warnings"))
    suggestions = _normalize_suggestions(parsed.get("suggestions"))
    insufficient_evidence = _normalize_string_list(
        parsed.get("insufficient_evidence"),
        limit=MAX_INSUFFICIENT_EVIDENCE,
    )
    looks_rich = _looks_like_rich_story_check(parsed)

    response: dict[str, Any] = {
        "task": "story_check",
        "coherence_score": _coerce_score(parsed.get("coherence_score")),
        "warnings": warnings,
        "suggestions": suggestions,
    }

    if insufficient_evidence:
        response["insufficient_evidence"] = insufficient_evidence

    rich_candidate: dict[str, Any] = {}
    throughline_alignment = _normalize_throughline_alignment(parsed.get("throughline_alignment"))
    if throughline_alignment is not None:
        rich_candidate["throughline_alignment"] = throughline_alignment
        response["throughline_alignment"] = throughline_alignment

    theme_drift = _normalize_status_reason(parsed.get("theme_drift"), THEME_DRIFT_STATUSES)
    if theme_drift is not None:
        rich_candidate["theme_drift"] = theme_drift
        response["theme_drift"] = theme_drift

    character_consistency = _normalize_status_reason(
        parsed.get("character_consistency"),
        CHARACTER_CONSISTENCY_STATUSES,
    )
    if character_consistency is not None:
        rich_candidate["character_consistency"] = character_consistency
        response["character_consistency"] = character_consistency

    if looks_rich:
        schema_candidate = {
            "task": "story_check",
            "coherence_score": response["coherence_score"],
            "warnings": warnings,
            "suggestions": suggestions,
            "insufficient_evidence": insufficient_evidence,
            **rich_candidate,
        }
        schema_valid, schema_errors = validate_story_check_schema(schema_candidate)
        diagnostics = _safe_diagnostics(parsed.get("diagnostics"))
        diagnostics.update(
            {
                "task": "story_check",
                "schema_valid": schema_valid,
                "insufficient_evidence": insufficient_evidence,
            }
        )
        if schema_errors:
            diagnostics["schema_errors"] = schema_errors
            response["warnings"] = (
                warnings + ["[Factual] Story Check diagnostics did not fully match the Phase 2 schema."]
            )[:MAX_WARNINGS]
        response["diagnostics"] = diagnostics
    else:
        response["diagnostics"] = {
            "task": "story_check",
            "schema_valid": False,
            "legacy_small_schema": True,
            "insufficient_evidence": insufficient_evidence,
        }

    if not response["warnings"] and not response["suggestions"]:
        response["warnings"] = ["[Factual] Story Check response contained no warnings or diagnostic questions."]
    return response


def _coerce_score(value: Any) -> int:
    try:
        score = int(value)
    except (TypeError, ValueError):
        return 0
    return max(0, min(10, score))


def _normalize_string_list(value: Any, *, limit: int) -> list[str]:
    if not isinstance(value, list):
        return []
    items: list[str] = []
    for item in value:
        text = item.strip() if isinstance(item, str) else str(item).strip()
        if text:
            items.append(text)
        if len(items) >= limit:
            break
    return items


def _normalize_warning(value: str) -> str:
    warning = value.strip()
    if warning.startswith(ALLOWED_WARNING_PREFIXES):
        return warning
    return f"[Factual] {warning}"


def _normalize_warnings(value: Any) -> list[str]:
    return [_normalize_warning(item) for item in _normalize_string_list(value, limit=MAX_WARNINGS)]


def _is_safe_question(value: str) -> bool:
    text = value.strip()
    return text.endswith("?") and not guardrails.is_prose_generation_request(text)


def _normalize_suggestions(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []

    suggestions: list[str] = []
    for item in value:
        text = item.strip() if isinstance(item, str) else str(item).strip()
        if text and _is_safe_question(text):
            suggestions.append(text)
        if len(suggestions) >= MAX_SUGGESTIONS:
            break
    return suggestions


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


def _normalize_throughline_alignment(value: Any) -> dict[str, dict[str, Any]] | None:
    if not isinstance(value, dict):
        return None

    normalized: dict[str, dict[str, Any]] = {}
    for key in THROUGHLINE_KEYS:
        item = value.get(key)
        if not isinstance(item, dict):
            continue
        normalized[key] = {
            "present": item.get("present") is True,
            "evidence": _normalize_string_list(item.get("evidence"), limit=MAX_EVIDENCE_ITEMS),
            "concerns": _normalize_string_list(item.get("concerns"), limit=MAX_EVIDENCE_ITEMS),
        }
    return normalized if normalized else None


def _normalize_status_reason(value: Any, allowed_statuses: set[str]) -> dict[str, str] | None:
    if not isinstance(value, dict):
        return None

    status = value.get("status")
    reason = value.get("reason")
    if not isinstance(status, str) or status not in allowed_statuses:
        status = "insufficient_evidence"
    reason_text = reason.strip() if isinstance(reason, str) and reason.strip() else "Insufficient evidence."
    return {"status": status, "reason": reason_text}


def _safe_diagnostics(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}
