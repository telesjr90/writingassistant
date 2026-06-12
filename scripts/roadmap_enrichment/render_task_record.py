#!/usr/bin/env python3
"""Render a roadmap task record from an existing enrichment file."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
INDEX_PATH = ROOT / "docs" / "roadmap" / "roadmap_index.yaml"


def load_index() -> dict[str, Any]:
    try:
        raw = INDEX_PATH.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"could not read {INDEX_PATH}: {exc}") from exc

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"could not parse {INDEX_PATH} as JSON-compatible YAML: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError("roadmap index root must be an object")
    return data


def task_map(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    tasks = data.get("tasks")
    if not isinstance(tasks, list):
        raise ValueError("tasks must be a list")
    return {task.get("id"): task for task in tasks if isinstance(task, dict) and isinstance(task.get("id"), str)}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a task record from enrichment JSON.")
    parser.add_argument("--task", required=True, help="Task ID to render.")
    parser.add_argument("--dry-run", action="store_true", help="Print render plan without writing.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        data = load_index()
        tasks_by_id = task_map(data)
    except ValueError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    task = tasks_by_id.get(args.task)
    if not isinstance(task, dict):
        print(f"FAIL: task {args.task!r} does not exist", file=sys.stderr)
        return 1

    enrichment_record = task.get("enrichment_record")
    task_record = task.get("task_record")
    if not isinstance(enrichment_record, str) or not isinstance(task_record, str):
        print(f"FAIL: task {args.task} is missing enrichment_record or task_record", file=sys.stderr)
        return 1

    enrichment_path = ROOT / enrichment_record
    task_record_path = ROOT / task_record
    if not enrichment_path.exists():
        print(f"FAIL: enrichment record does not exist yet: {enrichment_record}", file=sys.stderr)
        return 1

    if args.dry_run:
        print(f"Would render {enrichment_record} -> {task_record}")
        return 0

    print(f"FAIL: rendering is scaffold-only for now: {task_record_path.relative_to(ROOT)}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())

