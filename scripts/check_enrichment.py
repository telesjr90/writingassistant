#!/usr/bin/env python3
"""Validate roadmap enrichment scaffold pointers and conventions."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "docs" / "roadmap" / "roadmap_index.yaml"
GOVERNANCE_PATH = ROOT / "docs" / "roadmap" / "roadmap_governance.md"

PARENT_RE = re.compile(r"^PHASE[0-9]+-IMPL-[0-9]{3}$")
CHILD_RE = re.compile(r"^(PHASE[0-9]+-IMPL-[0-9]{3})-T[0-9]{3}$")
PHASE7_PARENT_RE = re.compile(r"^PHASE7-IMPL-[0-9]{3}$")
BACKTICK_RE = re.compile(r"`([^`]+)`")

POINTER_FIELDS = {
    "task_record": "docs/roadmap/tasks/",
    "inventory_record": "docs/roadmap/inventory/",
    "enrichment_record": "docs/roadmap/enrichment/",
    "context_pack": ".codex-context/",
}

ACTIVE_COLLECT_PLAN_FILES = [
    "task_manifest.json",
    "evidence_manifest.json",
    "collection_plan.md",
    "cce-queries.md",
    "graphify-queries.md",
    "repomix-include-candidates.txt",
    "ai-context-command-candidates.md",
]


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


def load_known_boundary_tags() -> set[str] | None:
    if not GOVERNANCE_PATH.exists():
        return None
    text = GOVERNANCE_PATH.read_text(encoding="utf-8")
    return {match.group(1) for match in BACKTICK_RE.finditer(text)}


def is_child_task(task: dict[str, Any]) -> bool:
    task_id = task.get("id")
    if not isinstance(task_id, str):
        return False
    if CHILD_RE.match(task_id):
        return True
    return task.get("parent") is not None


def validate() -> list[str]:
    errors: list[str] = []

    try:
        data = load_index()
    except ValueError as exc:
        return [str(exc)]

    tasks = data.get("tasks")
    if not isinstance(tasks, list):
        return ["tasks must be a list"]

    tasks_by_id = {task.get("id"): task for task in tasks if isinstance(task, dict)}

    phase7_parents = [
        task
        for task in tasks
        if isinstance(task, dict)
        and isinstance(task.get("id"), str)
        and PHASE7_PARENT_RE.match(task["id"])
        and not is_child_task(task)
    ]

    for task in phase7_parents:
        task_id = task["id"]
        for field, prefix in POINTER_FIELDS.items():
            value = task.get(field)
            if not isinstance(value, str):
                errors.append(f"{task_id} missing string pointer field {field}")
                continue
            if not value.startswith(prefix):
                errors.append(f"{task_id} {field} must start with {prefix}")

    active = data.get("active_frontier")
    if isinstance(active, dict):
        active_id = active.get("current_parent_task_id")
        active_task = tasks_by_id.get(active_id)
        if not isinstance(active_task, dict):
            errors.append(f"active frontier task {active_id!r} does not exist")
        else:
            for field in POINTER_FIELDS:
                if field not in active_task:
                    errors.append(f"active frontier task {active_id} missing {field}")
            context_pack = active_task.get("context_pack")
            if isinstance(context_pack, str):
                context_dir = ROOT / context_pack
                has_collect_plan = (context_dir / "evidence_manifest.json").exists()
                if has_collect_plan:
                    for filename in ACTIVE_COLLECT_PLAN_FILES:
                        if not (context_dir / filename).exists():
                            errors.append(f"active frontier task {active_id} missing collect-plan file {context_pack}{filename}")
    else:
        errors.append("active_frontier must be an object")

    task_004 = tasks_by_id.get("PHASE7-IMPL-004")
    if not isinstance(task_004, dict):
        errors.append("PHASE7-IMPL-004 must exist")
    else:
        for field in POINTER_FIELDS:
            if field not in task_004:
                errors.append(f"PHASE7-IMPL-004 missing {field}")

    task_004_t001 = tasks_by_id.get("PHASE7-IMPL-004-T001")
    if not isinstance(task_004_t001, dict):
        errors.append("PHASE7-IMPL-004-T001 must exist")
    else:
        if task_004_t001.get("type") != "planning_microtask":
            errors.append("PHASE7-IMPL-004-T001 must remain planning_microtask")
        if task_004_t001.get("status") != "ready":
            errors.append("PHASE7-IMPL-004-T001 must remain status ready")
        if task_004_t001.get("parent") != "PHASE7-IMPL-004":
            errors.append("PHASE7-IMPL-004-T001 must remain parent PHASE7-IMPL-004")

    known_tags = load_known_boundary_tags()
    if known_tags is not None:
        for task in tasks:
            if not isinstance(task, dict):
                continue
            task_id = task.get("id", "<unknown>")
            boundary_tags = task.get("boundary_tags", [])
            if not isinstance(boundary_tags, list):
                errors.append(f"{task_id} boundary_tags must be a list")
                continue
            for tag in boundary_tags:
                if tag not in known_tags:
                    errors.append(f"{task_id} uses unknown boundary tag {tag!r}")

    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
