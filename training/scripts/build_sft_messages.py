from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from copy import deepcopy
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import validate_dataset


SYSTEM_MESSAGE = (
    "You are a Dramatica-informed narrative analysis assistant. "
    "You do not write, rewrite, continue, imitate, or improve prose. "
    "You only perform structural analysis, throughline classification, and writer-focused "
    "diagnostic questioning. "
    "Return only valid JSON matching the requested schema. "
    "If evidence is insufficient, say what is missing instead of guessing."
)

TASK_SCHEMA_FILES = {
    "story_check": "story_check.schema.json",
    "throughline_classification": "throughline_classification.schema.json",
    "writer_questions": "writer_questions.schema.json",
    "out_of_scope_refusal": "out_of_scope_refusal.schema.json",
}

ELIGIBLE_FOR_TRAINING = "eligible_for_training"
ELIGIBLE_FOR_EVAL_ONLY = "eligible_for_eval_only"
DRAFT_NEEDS_HUMAN_REVIEW = "draft_needs_human_review"
BLOCKED_PENDING_OWNER_DECISION = "blocked_pending_owner_decision"
BLOCKED_PENDING_ALIGNED_STORYFORM = "blocked_pending_aligned_storyform"
MISSING_ELIGIBILITY = "missing_training_eligibility"
MIN_TRAINING_READY_RECORDS = 20

DEFAULT_INCLUDED_ELIGIBILITIES = (ELIGIBLE_FOR_TRAINING,)
BLOCKED_ELIGIBILITIES = {
    BLOCKED_PENDING_OWNER_DECISION,
    BLOCKED_PENDING_ALIGNED_STORYFORM,
}


def parse_bool(value: str | bool) -> bool:
    if isinstance(value, bool):
        return value

    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off"}:
        return False

    raise argparse.ArgumentTypeError(f"Expected a boolean value, got {value!r}.")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Convert validated multi-task SFT records into chat-format message JSONL while "
            "separating draft, eval-only, and blocked review candidates."
        )
    )
    parser.add_argument("--input", required=True, type=Path, help="Validated SFT JSONL input.")
    parser.add_argument("--schemas", required=True, type=Path, help="Path to training/schemas.")
    parser.add_argument("--output", required=True, type=Path, help="Message JSONL output path.")
    parser.add_argument(
        "--review-output",
        required=True,
        type=Path,
        help="JSONL output path for non-emitted review candidate records.",
    )
    parser.add_argument(
        "--include-eligibility",
        action="append",
        dest="include_eligibility",
        help=(
            "training_eligibility value to emit to the messages output. May be repeated. "
            "Defaults to eligible_for_training only."
        ),
    )
    parser.add_argument(
        "--include-blocked",
        nargs="?",
        const="true",
        default="false",
        type=parse_bool,
        help=(
            "Allow blocked records into the messages output only when their exact eligibility "
            "is also passed via --include-eligibility. Default: false."
        ),
    )
    return parser.parse_args(argv)


def load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as handle:
            data = json.load(handle)
    except OSError as exc:
        raise ValueError(f"Could not read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object.")

    return data


def load_task_schemas(schema_dir: Path) -> dict[str, dict[str, Any]]:
    schemas: dict[str, dict[str, Any]] = {}
    for task, filename in TASK_SCHEMA_FILES.items():
        schema_path = schema_dir / filename
        if not schema_path.exists():
            raise ValueError(f"Missing required schema: {schema_path}")
        schemas[task] = load_json(schema_path)
    return schemas


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"{path}:{line_number}: invalid JSON: {exc.msg} at column {exc.colno}"
                ) from exc
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number}: JSONL record must be an object.")
            records.append(value)
    return records


def json_text(value: Any, *, pretty: bool = False) -> str:
    if pretty:
        return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=False)
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=False)


def prompt_field(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json_text(value, pretty=True)


def training_eligibility(record: dict[str, Any]) -> str:
    metadata = record.get("metadata")
    if isinstance(metadata, dict):
        value = metadata.get("training_eligibility")
        if isinstance(value, str) and value:
            return value
    return MISSING_ELIGIBILITY


def is_blocked_eligibility(eligibility: str) -> bool:
    return eligibility in BLOCKED_ELIGIBILITIES or eligibility.startswith("blocked_")


def should_emit_record(
    eligibility: str,
    included_eligibilities: set[str],
    include_blocked: bool,
) -> bool:
    if eligibility not in included_eligibilities:
        return False
    if is_blocked_eligibility(eligibility) and not include_blocked:
        return False
    return True


def make_user_message(record: dict[str, Any], task_schema: dict[str, Any]) -> str:
    return (
        f"TASK: {record['task']}\n"
        f"ALLOWED OUTPUT SCHEMA:\n{json_text(task_schema, pretty=True)}\n"
        f"STORYFORM CONTEXT:\n{prompt_field(record['storyform_context'])}\n"
        f"STORY BIBLE:\n{prompt_field(record['bible_summary'])}\n"
        f"SCENE TEXT:\n{record['scene_text']}\n"
        f"USER REQUEST:\n{record['user_request']}"
    )


def make_message_record(
    record: dict[str, Any],
    task_schema: dict[str, Any],
) -> dict[str, Any]:
    metadata = record.get("metadata")
    if not isinstance(metadata, dict):
        metadata = {}

    return {
        "messages": [
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": make_user_message(record, task_schema)},
            {"role": "assistant", "content": json_text(record["gold_output"])},
        ],
        "task": record["task"],
        "metadata": deepcopy(metadata),
    }


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=False))
            handle.write("\n")


def print_counter(title: str, counter: Counter[str]) -> None:
    print(title)
    if not counter:
        print("  (none)")
        return
    for key in sorted(counter):
        print(f"  {key}: {counter[key]}")


def validate_input(input_path: Path, schemas_path: Path) -> int:
    validators = validate_dataset.load_validators(schemas_path)
    record_count, findings = validate_dataset.validate_jsonl(
        input_path,
        validators,
        strict=True,
    )
    validate_dataset.print_report(input_path, record_count, findings)
    if any(finding.severity == "error" for finding in findings):
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    included_eligibilities = set(
        args.include_eligibility or DEFAULT_INCLUDED_ELIGIBILITIES
    )

    try:
        validation_status = validate_input(args.input, args.schemas)
        if validation_status != 0:
            return validation_status
        task_schemas = load_task_schemas(args.schemas)
        records = read_jsonl(args.input)
    except ValueError as exc:
        print(f"build_sft_messages.py: error: {exc}", file=sys.stderr)
        return 2

    message_records: list[dict[str, Any]] = []
    review_records: list[dict[str, Any]] = []
    task_counts: Counter[str] = Counter()
    eligibility_counts: Counter[str] = Counter()
    emitted_eligibility_counts: Counter[str] = Counter()
    review_eligibility_counts: Counter[str] = Counter()

    for record in records:
        task = record.get("task")
        eligibility = training_eligibility(record)
        task_counts[str(task)] += 1
        eligibility_counts[eligibility] += 1

        if should_emit_record(eligibility, included_eligibilities, args.include_blocked):
            task_schema = task_schemas[record["task"]]
            message_records.append(make_message_record(record, task_schema))
            emitted_eligibility_counts[eligibility] += 1
        else:
            review_records.append(record)
            review_eligibility_counts[eligibility] += 1

    write_jsonl(args.output, message_records)
    write_jsonl(args.review_output, review_records)

    non_training_included = sorted(
        eligibility
        for eligibility in included_eligibilities
        if eligibility != ELIGIBLE_FOR_TRAINING
    )
    if non_training_included or args.include_blocked:
        print(
            "WARNING: messages output includes requested non-default eligibility gates; "
            "do not treat it as training-ready without review.",
            file=sys.stderr,
        )

    print(f"Read {len(records)} record(s) from {args.input}.")
    print(f"Wrote {len(message_records)} message record(s) to {args.output}.")
    print(f"Wrote {len(review_records)} review candidate record(s) to {args.review_output}.")
    print_counter("Input counts by task:", task_counts)
    print_counter("Input counts by training_eligibility:", eligibility_counts)
    print_counter("Message output counts by training_eligibility:", emitted_eligibility_counts)
    print_counter("Review output counts by training_eligibility:", review_eligibility_counts)

    if set(included_eligibilities) == {ELIGIBLE_FOR_TRAINING} and not args.include_blocked:
        print("Message output eligibility-gated: yes, eligible_for_training only.")
        if len(message_records) < MIN_TRAINING_READY_RECORDS:
            print(
                "Full fine-tuning dataset training-ready: no, fewer than "
                f"{MIN_TRAINING_READY_RECORDS} eligible_for_training records were emitted."
            )
            print(
                "Current Elena v2 seed remains useful for validator testing, refusal examples, "
                "review workflow testing, missing-evidence behavior, and future owner-review repair."
            )
    else:
        print("Message output eligibility-gated: no, non-training eligibility was requested.")
        print("Full fine-tuning dataset training-ready: no.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
