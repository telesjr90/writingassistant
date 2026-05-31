from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from training.scripts import validate_dataset


PREDICTION_FIELDS = (
    "prediction",
    "output",
    "model_output",
    "assistant_output",
    "gold_output",
)

WARNING_PREFIXES = (
    "[Plot/Temporal]",
    "[Character]",
    "[Worldbuilding]",
    "[Factual]",
    "[Stylistic]",
)

DRAFT_OR_BLOCKED_STATUSES = {
    "draft_needs_human_review",
    "blocked_pending_owner_decision",
}

MANUAL_REVIEW_COLUMNS = (
    "evidence_span_relevance",
    "change_vs_steadfast_contrast_accuracy",
    "appropriately_refused_to_overclaim",
    "no_prose_boundary_preserved",
)


@dataclass
class PredictionLine:
    line_number: int
    raw: Any | None
    valid_json: bool
    error: str | None = None
    record_id: str | None = None
    output: Any | None = None
    output_error: str | None = None


@dataclass
class EvaluationResult:
    gold_count: int
    prediction_line_count: int
    valid_prediction_json_count: int
    schema_compliant_count: int = 0
    refusal_no_prose_violation_count: int = 0
    task_count: Counter[str] = field(default_factory=Counter)
    throughline_confusion_counts: dict[str, Counter[str]] = field(
        default_factory=lambda: defaultdict(Counter)
    )
    insufficient_evidence_cases: int = 0
    insufficient_evidence_calibrated_count: int = 0
    overclaim_count: int = 0
    missing_key_count: int = 0
    extra_key_count: int = 0
    warning_prefix_total: int = 0
    warning_prefix_valid_count: int = 0
    warning_prefix_invalid_count: int = 0
    suggestion_question_total: int = 0
    suggestion_question_valid_count: int = 0
    suggestion_question_invalid_count: int = 0
    draft_or_blocked_leak_count: int = 0
    provisional_or_review_required_gold_count: int = 0
    missing_prediction_count: int = 0
    extra_prediction_count: int = 0
    invalid_prediction_lines: list[str] = field(default_factory=list)
    schema_errors: list[str] = field(default_factory=list)
    manual_review_rows: list[dict[str, str]] = field(default_factory=list)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate model JSONL outputs against held-out Phase 2 eval gold. "
            "Predictions may be raw task JSON objects or wrapper objects with an id "
            "plus one of: prediction, output, model_output, assistant_output, gold_output."
        )
    )
    parser.add_argument(
        "--predictions",
        required=True,
        type=Path,
        help="Path to model predictions JSONL.",
    )
    parser.add_argument(
        "--gold",
        required=True,
        type=Path,
        help="Path to eval_checklist_seed.jsonl.",
    )
    parser.add_argument(
        "--schemas",
        required=True,
        type=Path,
        help="Path to the training/schemas directory.",
    )
    parser.add_argument(
        "--report",
        required=True,
        type=Path,
        help="Path to write a Markdown evaluation report.",
    )
    return parser.parse_args(argv)


def read_jsonl(path: Path) -> tuple[list[Any], list[str]]:
    records: list[Any] = []
    errors: list[str] = []

    try:
        handle = path.open(encoding="utf-8")
    except OSError as exc:
        return [], [f"Could not read {path}: {exc}"]

    with handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue

            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                errors.append(
                    f"{path}:{line_number}: Invalid JSON: {exc.msg} at column {exc.colno}."
                )

    return records, errors


def extract_prediction_output(record: Any) -> tuple[str | None, Any | None, str | None]:
    if not isinstance(record, dict):
        return None, None, "Prediction line must be a JSON object."

    record_id = record.get("id")
    if record_id is not None and not isinstance(record_id, str):
        record_id = None

    for field_name in PREDICTION_FIELDS:
        if field_name not in record:
            continue

        value = record[field_name]
        if isinstance(value, str):
            try:
                return record_id, json.loads(value), None
            except json.JSONDecodeError as exc:
                return (
                    record_id,
                    None,
                    f"{field_name} is not valid JSON: {exc.msg} at column {exc.colno}.",
                )

        return record_id, value, None

    if "task" in record:
        return record_id, record, None

    return record_id, None, "No prediction output field found."


def read_predictions(path: Path) -> list[PredictionLine]:
    predictions: list[PredictionLine] = []

    try:
        handle = path.open(encoding="utf-8")
    except OSError as exc:
        return [
            PredictionLine(
                line_number=0,
                raw=None,
                valid_json=False,
                error=f"Could not read {path}: {exc}",
            )
        ]

    with handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue

            try:
                raw = json.loads(line)
            except json.JSONDecodeError as exc:
                predictions.append(
                    PredictionLine(
                        line_number=line_number,
                        raw=None,
                        valid_json=False,
                        error=f"Invalid JSON: {exc.msg} at column {exc.colno}.",
                    )
                )
                continue

            record_id, output, output_error = extract_prediction_output(raw)
            predictions.append(
                PredictionLine(
                    line_number=line_number,
                    raw=raw,
                    valid_json=True,
                    record_id=record_id,
                    output=output,
                    output_error=output_error,
                )
            )

    return predictions


def prediction_map(
    gold_records: list[dict[str, Any]],
    predictions: list[PredictionLine],
) -> tuple[dict[str, PredictionLine], int]:
    by_id = {
        prediction.record_id: prediction
        for prediction in predictions
        if prediction.valid_json and prediction.record_id
    }

    if by_id:
        matched = {
            str(gold.get("id")): by_id[str(gold.get("id"))]
            for gold in gold_records
            if str(gold.get("id")) in by_id
        }
        extra = sum(
            1
            for prediction in predictions
            if prediction.valid_json
            and prediction.record_id
            and prediction.record_id not in matched
        )
        return matched, extra

    matched = {}
    for index, gold in enumerate(gold_records):
        if index < len(predictions):
            matched[str(gold.get("id"))] = predictions[index]
    extra = max(0, len(predictions) - len(gold_records))
    return matched, extra


def schema_errors_for_output(
    output: Any,
    task: str,
    validators: validate_dataset.Validators,
) -> list[str]:
    if not isinstance(output, dict):
        return ["Prediction output must be a JSON object."]

    if output.get("task") != task:
        return [f"task must be {task!r}; got {output.get('task')!r}."]

    validator = validators.task_outputs.get(task)
    if validator is None:
        return [f"No validator loaded for task {task!r}."]

    return [
        validate_dataset.format_schema_error(error)
        for error in sorted(
            validator.iter_errors(output),
            key=lambda item: list(item.absolute_path),
        )
    ]


def schema_key_counts(output: Any, task: str, validators: validate_dataset.Validators) -> tuple[int, int]:
    if not isinstance(output, dict):
        task_schema = validators.task_outputs[task].schema
        return len(task_schema.get("required", [])), 0

    task_schema = validators.task_outputs[task].schema
    required_keys = set(task_schema.get("required", []))
    allowed_keys = set(task_schema.get("properties", {}).keys())
    output_keys = set(output.keys())

    missing = len(required_keys - output_keys)
    extra = len(output_keys - allowed_keys)
    return missing, extra


def iter_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        strings: list[str] = []
        for item in value:
            strings.extend(iter_strings(item))
        return strings
    if isinstance(value, dict):
        strings = []
        for item in value.values():
            strings.extend(iter_strings(item))
        return strings
    return []


def has_no_prose_violation(output: Any) -> bool:
    for text in iter_strings(output):
        for pattern, _reason in validate_dataset.GOLD_PROSE_PATTERNS:
            if pattern.search(text):
                return True
    return False


def throughline_label(output: Any) -> str | None:
    if isinstance(output, dict) and isinstance(output.get("primary_throughline"), str):
        return output["primary_throughline"]
    return None


def has_insufficient_evidence_signal(output: Any) -> bool:
    if not isinstance(output, dict):
        return False

    if output.get("primary_throughline") == "insufficient_evidence":
        return True

    insufficient = output.get("insufficient_evidence")
    if isinstance(insufficient, list) and len(insufficient) > 0:
        return True

    for field_name in ("theme_drift", "character_consistency"):
        field_value = output.get(field_name)
        if isinstance(field_value, dict) and field_value.get("status") == "insufficient_evidence":
            return True

    questions = output.get("questions")
    if isinstance(questions, list):
        for question in questions:
            if isinstance(question, dict) and question.get("throughline") == "insufficient_evidence":
                return True

    return False


def update_warning_prefix_metrics(result: EvaluationResult, output: Any) -> None:
    if not isinstance(output, dict):
        return

    warnings = output.get("warnings")
    if not isinstance(warnings, list):
        return

    for warning in warnings:
        if not isinstance(warning, str):
            result.warning_prefix_total += 1
            result.warning_prefix_invalid_count += 1
            continue

        result.warning_prefix_total += 1
        if warning.startswith(WARNING_PREFIXES):
            result.warning_prefix_valid_count += 1
        else:
            result.warning_prefix_invalid_count += 1


def update_question_metrics(result: EvaluationResult, output: Any) -> None:
    if not isinstance(output, dict):
        return

    suggestions = output.get("suggestions")
    if isinstance(suggestions, list):
        for suggestion in suggestions:
            result.suggestion_question_total += 1
            if isinstance(suggestion, str) and suggestion.strip().endswith("?"):
                result.suggestion_question_valid_count += 1
            else:
                result.suggestion_question_invalid_count += 1

    questions = output.get("questions")
    if isinstance(questions, list):
        for question in questions:
            value = question.get("question") if isinstance(question, dict) else None
            result.suggestion_question_total += 1
            if isinstance(value, str) and value.strip().endswith("?"):
                result.suggestion_question_valid_count += 1
            else:
                result.suggestion_question_invalid_count += 1


def metadata_status(record: dict[str, Any]) -> str | None:
    metadata = record.get("metadata")
    if not isinstance(metadata, dict):
        return None
    status = metadata.get("training_eligibility")
    return status if isinstance(status, str) else None


def is_provisional_or_review_required_gold(record: dict[str, Any]) -> bool:
    metadata = record.get("metadata")
    if not isinstance(metadata, dict):
        return False

    if metadata.get("human_review_required") is True:
        return True

    gold_status = metadata.get("evaluation_gold_status")
    if isinstance(gold_status, str) and gold_status != "safe_final_gold":
        return True

    return False


def manual_review_row(record: dict[str, Any], prediction: PredictionLine | None) -> dict[str, str]:
    record_id = str(record.get("id", ""))
    task = str(record.get("task", ""))
    has_prediction = prediction is not None and prediction.output is not None

    return {
        "id": record_id,
        "task": task,
        "prediction_present": "yes" if has_prediction else "no",
        "evidence_span_relevance": "manual_review_required",
        "change_vs_steadfast_contrast_accuracy": "manual_review_required",
        "appropriately_refused_to_overclaim": "manual_review_required",
        "no_prose_boundary_preserved": "manual_review_required",
    }


def evaluate(
    gold_records: list[dict[str, Any]],
    predictions: list[PredictionLine],
    validators: validate_dataset.Validators,
) -> EvaluationResult:
    result = EvaluationResult(
        gold_count=len(gold_records),
        prediction_line_count=len(predictions),
        valid_prediction_json_count=sum(1 for prediction in predictions if prediction.valid_json),
    )

    for prediction in predictions:
        if not prediction.valid_json or prediction.error:
            result.invalid_prediction_lines.append(
                f"line {prediction.line_number}: {prediction.error or 'invalid JSON'}"
            )
        elif prediction.output_error:
            result.invalid_prediction_lines.append(
                f"line {prediction.line_number}: {prediction.output_error}"
            )

    predictions_by_gold_id, extra_count = prediction_map(gold_records, predictions)
    result.extra_prediction_count = extra_count

    for gold in gold_records:
        record_id = str(gold.get("id"))
        task = str(gold.get("task"))
        gold_output = gold.get("gold_output")
        prediction = predictions_by_gold_id.get(record_id)
        output = prediction.output if prediction is not None else None

        result.task_count[task] += 1

        status = metadata_status(gold)
        if status in DRAFT_OR_BLOCKED_STATUSES:
            result.draft_or_blocked_leak_count += 1

        if is_provisional_or_review_required_gold(gold):
            result.provisional_or_review_required_gold_count += 1

        if prediction is None or prediction.output is None:
            result.missing_prediction_count += 1
            result.manual_review_rows.append(manual_review_row(gold, prediction))
            continue

        errors = schema_errors_for_output(output, task, validators)
        if errors:
            for error in errors:
                line = prediction.line_number if prediction else "?"
                result.schema_errors.append(f"{record_id} prediction line {line}: {error}")
        else:
            result.schema_compliant_count += 1

        missing_keys, extra_keys = schema_key_counts(output, task, validators)
        result.missing_key_count += missing_keys
        result.extra_key_count += extra_keys

        if task == "out_of_scope_refusal" and has_no_prose_violation(output):
            result.refusal_no_prose_violation_count += 1

        if task == "throughline_classification":
            gold_label = throughline_label(gold_output)
            predicted_label = throughline_label(output)
            if gold_label is not None and predicted_label is not None:
                result.throughline_confusion_counts[gold_label][predicted_label] += 1

        if has_insufficient_evidence_signal(gold_output):
            result.insufficient_evidence_cases += 1
            if has_insufficient_evidence_signal(output):
                result.insufficient_evidence_calibrated_count += 1
            else:
                result.overclaim_count += 1

        update_warning_prefix_metrics(result, output)
        update_question_metrics(result, output)
        result.manual_review_rows.append(manual_review_row(gold, prediction))

    return result


def rate(numerator: int, denominator: int) -> str:
    if denominator <= 0:
        return "n/a"
    return f"{numerator / denominator:.2%}"


def render_counter(counter: Counter[str]) -> str:
    if not counter:
        return "None"
    return ", ".join(f"{key}: {value}" for key, value in sorted(counter.items()))


def render_confusion(confusion: dict[str, Counter[str]]) -> list[str]:
    if not confusion:
        return ["No throughline labels were available in this gold set."]

    lines = ["| Gold | Predicted | Count |", "| --- | --- | ---: |"]
    for gold_label in sorted(confusion):
        for predicted_label, count in sorted(confusion[gold_label].items()):
            lines.append(f"| {gold_label} | {predicted_label} | {count} |")
    return lines


def render_manual_review(rows: list[dict[str, str]]) -> list[str]:
    header = [
        "| id | task | prediction_present | evidence_span_relevance | "
        "change_vs_steadfast_contrast_accuracy | appropriately_refused_to_overclaim | "
        "no_prose_boundary_preserved |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    body = [
        "| {id} | {task} | {prediction_present} | {evidence_span_relevance} | "
        "{change_vs_steadfast_contrast_accuracy} | {appropriately_refused_to_overclaim} | "
        "{no_prose_boundary_preserved} |".format(**row)
        for row in rows
    ]
    return header + body


def write_report(
    report_path: Path,
    result: EvaluationResult,
    gold_path: Path,
    predictions_path: Path,
) -> None:
    json_denominator = max(result.gold_count, result.prediction_line_count)
    schema_denominator = result.gold_count

    lines = [
        "# Evaluation Report",
        "",
        f"- Gold: `{gold_path}`",
        f"- Predictions: `{predictions_path}`",
        f"- Gold records: {result.gold_count}",
        f"- Prediction lines: {result.prediction_line_count}",
        f"- Task count: {render_counter(result.task_count)}",
        "",
        "## Automated Metrics",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        (
            f"| JSON validity rate | {rate(result.valid_prediction_json_count, json_denominator)} "
            f"({result.valid_prediction_json_count}/{json_denominator}) |"
        ),
        (
            f"| Schema compliance rate | {rate(result.schema_compliant_count, schema_denominator)} "
            f"({result.schema_compliant_count}/{schema_denominator}) |"
        ),
        f"| Refusal no-prose violation count | {result.refusal_no_prose_violation_count} |",
        f"| Missing prediction count | {result.missing_prediction_count} |",
        f"| Extra prediction count | {result.extra_prediction_count} |",
        f"| Missing key count | {result.missing_key_count} |",
        f"| Extra key count | {result.extra_key_count} |",
        (
            f"| Warning-prefix validity | {rate(result.warning_prefix_valid_count, result.warning_prefix_total)} "
            f"({result.warning_prefix_valid_count}/{result.warning_prefix_total}) |"
        ),
        (
            f"| Suggestion-as-question validity | "
            f"{rate(result.suggestion_question_valid_count, result.suggestion_question_total)} "
            f"({result.suggestion_question_valid_count}/{result.suggestion_question_total}) |"
        ),
        (
            f"| Insufficient-evidence calibration count | "
            f"{result.insufficient_evidence_calibrated_count}/{result.insufficient_evidence_cases} |"
        ),
        f"| Overclaim count where gold says insufficient_evidence | {result.overclaim_count} |",
        f"| draft_or_blocked_leak_count | {result.draft_or_blocked_leak_count} |",
        (
            f"| provisional_or_review_required_gold_count | "
            f"{result.provisional_or_review_required_gold_count} |"
        ),
        "",
        "## Throughline Confusion Counts",
        "",
        *render_confusion(result.throughline_confusion_counts),
        "",
        "## Manual Review Fields",
        "",
        (
            "These fields require human judgment and are intentionally not scored "
            "as automated pass/fail metrics."
        ),
        "",
        *render_manual_review(result.manual_review_rows),
    ]

    if result.invalid_prediction_lines:
        lines.extend(["", "## Prediction Parsing Issues", ""])
        lines.extend(f"- {issue}" for issue in result.invalid_prediction_lines)

    if result.schema_errors:
        lines.extend(["", "## Schema Issues", ""])
        lines.extend(f"- {issue}" for issue in result.schema_errors)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    try:
        validators = validate_dataset.load_validators(args.schemas)
    except ValueError as exc:
        print(f"Schema setup error: {exc}", file=sys.stderr)
        return 2

    gold_records_raw, gold_errors = read_jsonl(args.gold)
    if gold_errors:
        for error in gold_errors:
            print(error, file=sys.stderr)
        return 2

    gold_records: list[dict[str, Any]] = []
    for index, record in enumerate(gold_records_raw, start=1):
        if not isinstance(record, dict):
            print(f"{args.gold}:{index}: Gold record must be a JSON object.", file=sys.stderr)
            return 2
        gold_records.append(record)

    predictions = read_predictions(args.predictions)
    result = evaluate(gold_records, predictions, validators)
    write_report(args.report, result, args.gold, args.predictions)

    json_denominator = max(result.gold_count, result.prediction_line_count)
    print(f"Gold records: {result.gold_count}")
    print(
        "JSON validity rate: "
        f"{rate(result.valid_prediction_json_count, json_denominator)}"
    )
    print(
        "Schema compliance rate: "
        f"{rate(result.schema_compliant_count, result.gold_count)}"
    )
    print(f"draft_or_blocked_leak_count: {result.draft_or_blocked_leak_count}")
    print(f"Report written to {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
