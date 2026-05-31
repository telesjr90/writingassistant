from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft202012Validator as JsonSchemaValidator
except ImportError:  # pragma: no cover - older local jsonschema fallback
    from jsonschema import Draft7Validator as JsonSchemaValidator


ALLOWED_TASKS = {
    "story_check": "story_check.schema.json",
    "throughline_classification": "throughline_classification.schema.json",
    "writer_questions": "writer_questions.schema.json",
    "out_of_scope_refusal": "out_of_scope_refusal.schema.json",
}

REQUIRED_SCHEMA_FILES = {
    "sft_record": "sft_record.schema.json",
    **ALLOWED_TASKS,
}

PROSE_REQUEST_PATTERNS = [
    (
        re.compile(
            r"\b(?:write|draft|compose|generate)\b.{0,80}"
            r"\b(?:scene|chapter|paragraph|prose|dialogue|monologue|passage|opening|ending)\b",
            re.IGNORECASE,
        ),
        "user_request asks to write or generate prose",
    ),
    (
        re.compile(
            r"\b(?:rewrite|revise|polish|improve|line[- ]?edit)\b.{0,80}"
            r"\b(?:scene|chapter|paragraph|prose|dialogue|monologue|passage|text)\b",
            re.IGNORECASE,
        ),
        "user_request asks to rewrite or improve prose",
    ),
    (
        re.compile(
            r"\b(?:continue|finish|extend)\b.{0,80}"
            r"\b(?:scene|story|chapter|passage|prose|draft)\b",
            re.IGNORECASE,
        ),
        "user_request asks to continue prose",
    ),
    (
        re.compile(r"\badd\s+(?:some\s+)?dialogue\b", re.IGNORECASE),
        "user_request asks to add dialogue",
    ),
]

GOLD_PROSE_PATTERNS = [
    (
        re.compile(r"\bhere(?:'s| is)\s+(?:a\s+)?revised\s+scene\b", re.IGNORECASE),
        "appears to introduce a revised scene",
    ),
    (
        re.compile(
            r"\b(?:revised|rewritten|replacement)\s+"
            r"(?:scene|dialogue|passage|paragraph|chapter|prose)\b",
            re.IGNORECASE,
        ),
        "appears to include replacement scene text or dialogue",
    ),
    (
        re.compile(r"\bhere(?:'s| is)\s+(?:a\s+)?(?:rewrite|new draft)\b", re.IGNORECASE),
        "appears to introduce rewritten prose",
    ),
    (
        re.compile(r"\btry this\s+(?:version|draft|line|dialogue)\b", re.IGNORECASE),
        "appears to offer replacement prose",
    ),
    (
        re.compile(r"^\s*(?:revised version|rewrite|new scene|new dialogue)\s*:", re.IGNORECASE),
        "appears to label generated replacement prose",
    ),
]


@dataclass(frozen=True)
class Finding:
    line: int | None
    severity: str
    message: str


@dataclass(frozen=True)
class Validators:
    sft_top_level: Any
    task_outputs: dict[str, Any]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate Phase 2 multi-task JSONL training records against local schemas "
            "and analysis-only safety checks."
        )
    )
    parser.add_argument("--input", required=True, type=Path, help="Path to a JSONL dataset file.")
    parser.add_argument(
        "--schemas",
        required=True,
        type=Path,
        help="Path to the training/schemas directory.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat no-prose safety flags as errors instead of warnings.",
    )
    return parser.parse_args(argv)


def load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as handle:
            data = json.load(handle)
    except OSError as exc:
        raise ValueError(f"Could not read schema {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in schema {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError(f"Schema {path} must contain a JSON object.")

    return data


def make_sft_top_level_schema(sft_schema: dict[str, Any]) -> dict[str, Any]:
    top_level_schema = copy.deepcopy(sft_schema)
    top_level_schema["properties"]["gold_output"] = {"type": "object"}
    top_level_schema.pop("allOf", None)
    return top_level_schema


def load_validators(schema_dir: Path) -> Validators:
    schema_dir = schema_dir.resolve()
    schemas: dict[str, dict[str, Any]] = {}

    for key, filename in REQUIRED_SCHEMA_FILES.items():
        schema_path = schema_dir / filename
        if not schema_path.exists():
            raise ValueError(f"Missing required schema: {schema_path}")
        schema = load_json(schema_path)
        JsonSchemaValidator.check_schema(schema)
        schemas[key] = schema

    sft_top_schema = make_sft_top_level_schema(schemas["sft_record"])
    JsonSchemaValidator.check_schema(sft_top_schema)

    task_validators = {
        task: JsonSchemaValidator(schemas[task])
        for task in ALLOWED_TASKS
    }

    return Validators(
        sft_top_level=JsonSchemaValidator(sft_top_schema),
        task_outputs=task_validators,
    )


def format_schema_error(error: Any) -> str:
    path = ".".join(str(part) for part in error.absolute_path)
    location = path or "$"
    return f"{location}: {error.message}"


def schema_findings(
    validator: Any,
    value: Any,
    line_number: int,
    label: str,
) -> list[Finding]:
    findings: list[Finding] = []
    for error in sorted(validator.iter_errors(value), key=lambda item: list(item.absolute_path)):
        findings.append(
            Finding(
                line=line_number,
                severity="error",
                message=f"{label} schema violation: {format_schema_error(error)}",
            )
        )
    return findings


def iter_string_fields(value: Any, path: str = "gold_output") -> list[tuple[str, str]]:
    if isinstance(value, str):
        return [(path, value)]

    if isinstance(value, list):
        fields: list[tuple[str, str]] = []
        for index, item in enumerate(value):
            fields.extend(iter_string_fields(item, f"{path}[{index}]"))
        return fields

    if isinstance(value, dict):
        fields = []
        for key, item in value.items():
            fields.extend(iter_string_fields(item, f"{path}.{key}"))
        return fields

    return []


def safety_severity(strict: bool) -> str:
    return "error" if strict else "warning"


def validate_prose_request(
    record: dict[str, Any],
    line_number: int,
    strict: bool,
) -> list[Finding]:
    task = record.get("task")
    if task == "out_of_scope_refusal":
        return []

    user_request = record.get("user_request")
    if not isinstance(user_request, str):
        return []

    findings: list[Finding] = []
    for pattern, message in PROSE_REQUEST_PATTERNS:
        if pattern.search(user_request):
            findings.append(
                Finding(
                    line=line_number,
                    severity=safety_severity(strict),
                    message=message,
                )
            )
            break

    return findings


def validate_gold_output_no_prose(
    gold_output: Any,
    line_number: int,
    strict: bool,
) -> list[Finding]:
    findings: list[Finding] = []
    if not isinstance(gold_output, (dict, list, str)):
        return findings

    for path, text in iter_string_fields(gold_output):
        for pattern, message in GOLD_PROSE_PATTERNS:
            if pattern.search(text):
                findings.append(
                    Finding(
                        line=line_number,
                        severity=safety_severity(strict),
                        message=f"{path}: {message}",
                    )
                )
                break

    return findings


def validate_story_check_limits(
    gold_output: dict[str, Any],
    line_number: int,
) -> list[Finding]:
    findings: list[Finding] = []
    for field in ("warnings", "suggestions"):
        value = gold_output.get(field)
        if isinstance(value, list) and len(value) > 5:
            findings.append(
                Finding(
                    line=line_number,
                    severity="error",
                    message=f"gold_output.{field} must contain at most 5 items.",
                )
            )
    return findings


def validate_writer_questions(
    gold_output: dict[str, Any],
    line_number: int,
) -> list[Finding]:
    if gold_output.get("no_prose_generated") is True:
        return []

    return [
        Finding(
            line=line_number,
            severity="error",
            message="gold_output.no_prose_generated must be true for writer_questions.",
        )
    ]


def validate_refusal_message(
    gold_output: dict[str, Any],
    line_number: int,
    strict: bool,
) -> list[Finding]:
    message = gold_output.get("message")
    if not isinstance(message, str):
        return []

    findings: list[Finding] = []
    for pattern, reason in GOLD_PROSE_PATTERNS:
        if pattern.search(message):
            findings.append(
                Finding(
                    line=line_number,
                    severity=safety_severity(strict),
                    message=f"gold_output.message: refusal message {reason}",
                )
            )
            break

    return findings


def validate_record(
    record: dict[str, Any],
    line_number: int,
    validators: Validators,
    strict: bool,
) -> list[Finding]:
    findings = schema_findings(validators.sft_top_level, record, line_number, "SFT record")

    task = record.get("task")
    gold_output = record.get("gold_output")

    if task not in ALLOWED_TASKS:
        return findings

    if not isinstance(gold_output, dict):
        return findings

    gold_task = gold_output.get("task")
    if gold_task != task:
        findings.append(
            Finding(
                line=line_number,
                severity="error",
                message=f"gold_output.task must match record task {task!r}.",
            )
        )

    findings.extend(
        schema_findings(
            validators.task_outputs[task],
            gold_output,
            line_number,
            f"{task} output",
        )
    )

    if task == "story_check":
        findings.extend(validate_story_check_limits(gold_output, line_number))
    elif task == "writer_questions":
        findings.extend(validate_writer_questions(gold_output, line_number))
    elif task == "out_of_scope_refusal":
        findings.extend(validate_refusal_message(gold_output, line_number, strict))

    findings.extend(validate_prose_request(record, line_number, strict))
    findings.extend(validate_gold_output_no_prose(gold_output, line_number, strict))
    return findings


def validate_jsonl(
    input_path: Path,
    validators: Validators,
    strict: bool,
) -> tuple[int, list[Finding]]:
    findings: list[Finding] = []
    record_count = 0

    try:
        handle = input_path.open(encoding="utf-8")
    except OSError as exc:
        return 0, [Finding(line=None, severity="error", message=f"Could not read input: {exc}")]

    with handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                findings.append(
                    Finding(
                        line=line_number,
                        severity="error",
                        message=f"Invalid JSON: {exc.msg} at column {exc.colno}.",
                    )
                )
                continue

            if not isinstance(record, dict):
                findings.append(
                    Finding(
                        line=line_number,
                        severity="error",
                        message="JSONL record must be a JSON object.",
                    )
                )
                continue

            record_count += 1
            findings.extend(validate_record(record, line_number, validators, strict))

    return record_count, findings


def print_report(input_path: Path, record_count: int, findings: list[Finding]) -> None:
    for finding in findings:
        line = f":{finding.line}" if finding.line is not None else ""
        print(
            f"{input_path}{line}: {finding.severity}: {finding.message}",
            file=sys.stderr,
        )

    error_count = sum(1 for finding in findings if finding.severity == "error")
    warning_count = sum(1 for finding in findings if finding.severity == "warning")
    print(f"Validated {record_count} record(s) from {input_path}.")
    print(f"{error_count} error(s), {warning_count} warning(s).")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    try:
        validators = load_validators(args.schemas)
    except ValueError as exc:
        print(f"Schema setup error: {exc}", file=sys.stderr)
        return 2

    record_count, findings = validate_jsonl(args.input, validators, args.strict)
    print_report(args.input, record_count, findings)

    return 1 if any(finding.severity == "error" for finding in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
