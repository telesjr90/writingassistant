from __future__ import annotations

import argparse
import json
import math
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ELIGIBLE_FOR_TRAINING = "eligible_for_training"
ELIGIBLE_FOR_EVAL_ONLY = "eligible_for_eval_only"
DRAFT_NEEDS_HUMAN_REVIEW = "draft_needs_human_review"
MISSING_ELIGIBILITY = "missing_training_eligibility"
MIN_TRAINING_READY_RECORDS = 20


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Split chat-format SFT message records into compiled train/eval/test JSONL "
            "without silently training on blocked, draft, human-review, or eval-only records."
        )
    )
    parser.add_argument("--input", required=True, type=Path, help="Message JSONL input path.")
    parser.add_argument("--output-dir", required=True, type=Path, help="Compiled output directory.")
    parser.add_argument("--train-ratio", required=True, type=float, help="Train split ratio.")
    parser.add_argument("--eval-ratio", required=True, type=float, help="Eval split ratio.")
    parser.add_argument("--test-ratio", required=True, type=float, help="Test split ratio.")
    parser.add_argument("--seed", required=True, type=int, help="Deterministic shuffle seed.")
    parser.add_argument(
        "--allow-tiny-smoke-split",
        action="store_true",
        help=(
            "Write tiny smoke-test split files even when fewer than 20 eligible_for_training "
            "records exist. Output is still not training-ready."
        ),
    )
    return parser.parse_args(argv)


def validate_ratios(train_ratio: float, eval_ratio: float, test_ratio: float) -> None:
    ratios = [train_ratio, eval_ratio, test_ratio]
    if any(ratio < 0 for ratio in ratios):
        raise ValueError("Split ratios must be non-negative.")
    if not any(ratio > 0 for ratio in ratios):
        raise ValueError("At least one split ratio must be greater than zero.")

    total = sum(ratios)
    if not math.isclose(total, 1.0, rel_tol=1e-9, abs_tol=1e-9):
        raise ValueError(f"Split ratios must sum to 1.0; got {total}.")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    try:
        handle = path.open(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"Could not read input {path}: {exc}") from exc

    with handle:
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


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=False))
            handle.write("\n")


def training_eligibility(record: dict[str, Any]) -> str:
    metadata = record.get("metadata")
    if isinstance(metadata, dict):
        value = metadata.get("training_eligibility")
        if isinstance(value, str) and value:
            return value
    return MISSING_ELIGIBILITY


def task_name(record: dict[str, Any]) -> str:
    value = record.get("task")
    if isinstance(value, str) and value:
        return value
    return "missing_task"


def human_review_required(record: dict[str, Any]) -> bool:
    metadata = record.get("metadata")
    return isinstance(metadata, dict) and metadata.get("human_review_required") is True


def is_blocked_eligibility(eligibility: str) -> bool:
    return eligibility.startswith("blocked_")


def split_allocations(total: int, ratios: tuple[float, ...]) -> list[int]:
    raw_counts = [total * ratio for ratio in ratios]
    counts = [math.floor(value) for value in raw_counts]
    remainder = total - sum(counts)
    order = sorted(
        range(len(ratios)),
        key=lambda index: (raw_counts[index] - counts[index], ratios[index]),
        reverse=True,
    )
    for index in order[:remainder]:
        counts[index] += 1
    return counts


def stratified_split(
    records: list[dict[str, Any]],
    ratios: tuple[float, ...],
    labels: tuple[str, ...],
    seed: int,
) -> dict[str, list[dict[str, Any]]]:
    rng = random.Random(seed)
    by_task: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_task[task_name(record)].append(record)

    splits = {label: [] for label in labels}
    for task in sorted(by_task):
        group = list(by_task[task])
        rng.shuffle(group)
        counts = split_allocations(len(group), ratios)
        start = 0
        for label, count in zip(labels, counts):
            end = start + count
            splits[label].extend(group[start:end])
            start = end

    for label in labels:
        rng.shuffle(splits[label])

    return splits


def infer_training_root(output_dir: Path) -> Path:
    resolved = output_dir.resolve()
    for path in (resolved, *resolved.parents):
        if path.name == "training":
            return path
    return Path("training").resolve()


def markdown_count_table(title: str, counter: Counter[str]) -> str:
    lines = [f"## {title}", "", "| Value | Count |", "| --- | ---: |"]
    if counter:
        for key in sorted(counter):
            lines.append(f"| `{key}` | {counter[key]} |")
    else:
        lines.append("| `(none)` | 0 |")
    lines.append("")
    return "\n".join(lines)


def write_too_small_report(
    output_dir: Path,
    input_path: Path,
    task_counts: Counter[str],
    eligibility_counts: Counter[str],
    eligible_for_training_count: int,
    allow_tiny_smoke_split: bool,
) -> Path:
    training_root = infer_training_root(output_dir)
    reports_dir = training_root / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = reports_dir / "BLOCKED_compiled_training_split_too_small.md"

    split_status = (
        "Tiny smoke-test split allowed and written."
        if allow_tiny_smoke_split
        else "No train/eval/test split files were written."
    )

    content = "\n".join(
        [
            "# BLOCKED: Compiled Training Split Too Small",
            "",
            f"- Input: `{input_path}`",
            f"- Output directory: `{output_dir}`",
            f"- Minimum `eligible_for_training` records required: {MIN_TRAINING_READY_RECORDS}",
            f"- Current `eligible_for_training` records: {eligible_for_training_count}",
            f"- Split status: {split_status}",
            "",
            "The current Elena v2 seed is not sufficient for full fine-tuning. "
            "Do not treat this compiled output as training-ready until the gate is met.",
            "",
            "The current seed may still be useful for:",
            "",
            "- validator testing",
            "- refusal examples",
            "- review workflow testing",
            "- missing-evidence behavior",
            "- future owner-review repair",
            "",
            markdown_count_table("Counts By Task", task_counts),
            markdown_count_table("Counts By Training Eligibility", eligibility_counts),
            "## Required Next Step",
            "",
            "Add or repair enough owner-approved records so at least "
            f"{MIN_TRAINING_READY_RECORDS} records are `eligible_for_training`. "
            "Core Elena storyform decisions that remain owner-deferred should not be "
            "converted into confident final labels.",
            "",
        ]
    )

    report_path.write_text(content, encoding="utf-8")
    return report_path


def print_counter(title: str, counter: Counter[str]) -> None:
    print(title)
    if not counter:
        print("  (none)")
        return
    for key in sorted(counter):
        print(f"  {key}: {counter[key]}")


def compile_splits(
    records: list[dict[str, Any]],
    train_ratio: float,
    eval_ratio: float,
    test_ratio: float,
    seed: int,
) -> tuple[dict[str, list[dict[str, Any]]], Counter[str]]:
    skipped: Counter[str] = Counter()

    training_records: list[dict[str, Any]] = []
    eval_only_records: list[dict[str, Any]] = []

    for record in records:
        eligibility = training_eligibility(record)
        if is_blocked_eligibility(eligibility):
            skipped[eligibility] += 1
            continue
        if eligibility == ELIGIBLE_FOR_TRAINING and not human_review_required(record):
            training_records.append(record)
            continue
        if eligibility == ELIGIBLE_FOR_TRAINING and human_review_required(record):
            skipped["eligible_for_training_with_human_review_required"] += 1
            continue
        if eligibility == ELIGIBLE_FOR_EVAL_ONLY:
            eval_only_records.append(record)
            continue
        if eligibility == DRAFT_NEEDS_HUMAN_REVIEW or human_review_required(record):
            skipped[DRAFT_NEEDS_HUMAN_REVIEW] += 1
            continue
        skipped[eligibility] += 1

    splits = stratified_split(
        training_records,
        (train_ratio, eval_ratio, test_ratio),
        ("train", "eval", "test"),
        seed,
    )

    eval_test_ratio_total = eval_ratio + test_ratio
    if eval_only_records and eval_test_ratio_total > 0:
        eval_test_splits = stratified_split(
            eval_only_records,
            (eval_ratio / eval_test_ratio_total, test_ratio / eval_test_ratio_total),
            ("eval", "test"),
            seed + 1,
        )
        splits["eval"].extend(eval_test_splits["eval"])
        splits["test"].extend(eval_test_splits["test"])
    elif eval_only_records:
        skipped[ELIGIBLE_FOR_EVAL_ONLY] += len(eval_only_records)

    return splits, skipped


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    try:
        validate_ratios(args.train_ratio, args.eval_ratio, args.test_ratio)
        records = read_jsonl(args.input)
    except ValueError as exc:
        print(f"split_dataset.py: error: {exc}", file=sys.stderr)
        return 2

    args.output_dir.mkdir(parents=True, exist_ok=True)

    task_counts: Counter[str] = Counter(task_name(record) for record in records)
    eligibility_counts: Counter[str] = Counter(training_eligibility(record) for record in records)
    eligible_for_training_count = eligibility_counts[ELIGIBLE_FOR_TRAINING]

    print(f"Read {len(records)} record(s) from {args.input}.")
    print_counter("Counts by task:", task_counts)
    print_counter("Counts by training_eligibility:", eligibility_counts)

    gate_blocked = eligible_for_training_count < MIN_TRAINING_READY_RECORDS
    report_path: Path | None = None
    if gate_blocked:
        report_path = write_too_small_report(
            args.output_dir,
            args.input,
            task_counts,
            eligibility_counts,
            eligible_for_training_count,
            args.allow_tiny_smoke_split,
        )
        print(
            "BLOCKED: fewer than "
            f"{MIN_TRAINING_READY_RECORDS} eligible_for_training records exist. "
            f"Wrote {report_path}."
        )
        if not args.allow_tiny_smoke_split:
            print("Compiled output training-ready: no.")
            print("No split files written; pass --allow-tiny-smoke-split for smoke-test files.")
            return 0

    splits, skipped_counts = compile_splits(
        records,
        args.train_ratio,
        args.eval_ratio,
        args.test_ratio,
        args.seed,
    )

    write_jsonl(args.output_dir / "train.jsonl", splits["train"])
    write_jsonl(args.output_dir / "eval.jsonl", splits["eval"])
    write_jsonl(args.output_dir / "test.jsonl", splits["test"])

    split_counts = Counter({name: len(items) for name, items in splits.items()})
    print_counter("Compiled split counts:", split_counts)
    print_counter("Skipped counts by training_eligibility/reason:", skipped_counts)

    if gate_blocked:
        print("Compiled output training-ready: no, smoke-test split only.")
    else:
        print("Compiled output training-ready: yes.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
