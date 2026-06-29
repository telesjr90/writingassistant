#!/usr/bin/env python3
"""Validate the roadmap control registry.

The registry is stored as JSON-compatible YAML so this script can use only the
Python standard library. If the file is changed to general YAML syntax later,
installing PyYAML or returning to JSON-compatible YAML will be required.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "docs" / "roadmap" / "roadmap_index.yaml"

PARENT_RE = re.compile(r"^PHASE[0-9]+-IMPL-[0-9]{3}$")
UX_PARENT_RE = re.compile(r"^PHASE[0-9]+-UX-[0-9]{3}$")
CHILD_RE = re.compile(r"^(PHASE[0-9]+-IMPL-[0-9]{3})-T[0-9]{3}$")

PARENT_TASK_TYPES = {"runtime", "validation", "docs-only"}
CHILD_TASK_TYPES = {"planning_microtask", "runtime_microtask", "validation_microtask"}
TASK_TYPES = PARENT_TASK_TYPES | CHILD_TASK_TYPES

REQUIRED_TOP_LEVEL = {
    "schema_version",
    "active_frontier",
    "id_policy",
    "source_hierarchy",
    "tasks",
}
REQUIRED_TASK_FIELDS = {
    "id",
    "title",
    "type",
    "status",
    "parent",
    "depends_on",
    "boundary_tags",
}


def load_registry() -> dict[str, Any]:
    try:
        raw = INDEX_PATH.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"could not read {INDEX_PATH}: {exc}") from exc

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(
            "roadmap_index.yaml must remain JSON-compatible YAML for this "
            f"dependency-free validator, or PyYAML must be added externally: {exc}"
        ) from exc

    if not isinstance(data, dict):
        raise ValueError("registry root must be an object")
    return data


def require(condition: bool, errors: list[str], message: str) -> None:
    if not condition:
        errors.append(message)


def validate_registry(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    missing_top = sorted(REQUIRED_TOP_LEVEL - data.keys())
    require(not missing_top, errors, f"missing top-level fields: {missing_top}")

    tasks = data.get("tasks")
    require(isinstance(tasks, list), errors, "tasks must be a list")
    if not isinstance(tasks, list):
        return errors

    seen: set[str] = set()
    duplicate_ids: set[str] = set()
    tasks_by_id: dict[str, dict[str, Any]] = {}

    for index, task in enumerate(tasks):
        if not isinstance(task, dict):
            errors.append(f"task at index {index} must be an object")
            continue

        task_id = task.get("id")
        if isinstance(task_id, str):
            if task_id in seen:
                duplicate_ids.add(task_id)
            seen.add(task_id)
            tasks_by_id[task_id] = task

        missing_fields = sorted(REQUIRED_TASK_FIELDS - task.keys())
        require(
            not missing_fields,
            errors,
            f"{task_id or f'task at index {index}'} missing required fields: {missing_fields}",
        )

        require(isinstance(task.get("id"), str), errors, f"task at index {index} id must be a string")
        require(isinstance(task.get("title"), str), errors, f"{task_id} title must be a string")
        require(
            task.get("type") in TASK_TYPES,
            errors,
            f"{task_id} type must be one of {sorted(TASK_TYPES)}",
        )
        require(isinstance(task.get("status"), str), errors, f"{task_id} status must be a string")
        require(isinstance(task.get("depends_on"), list), errors, f"{task_id} depends_on must be a list")
        require(isinstance(task.get("boundary_tags"), list), errors, f"{task_id} boundary_tags must be a list")

    require(not duplicate_ids, errors, f"duplicate task IDs: {sorted(duplicate_ids)}")

    for task_id, task in tasks_by_id.items():
        parent_match = PARENT_RE.match(task_id)
        ux_parent_match = UX_PARENT_RE.match(task_id)
        child_match = CHILD_RE.match(task_id)
        require(
            bool(parent_match or ux_parent_match or child_match),
            errors,
            f"{task_id} does not match parent or child task ID policy",
        )

        for dep in task.get("depends_on", []):
            require(isinstance(dep, str), errors, f"{task_id} depends_on contains a non-string reference")
            if isinstance(dep, str):
                require(dep in tasks_by_id, errors, f"{task_id} depends on unknown task {dep}")

        if child_match:
            implied_parent = child_match.group(1)
            require(implied_parent in tasks_by_id, errors, f"{task_id} has missing parent task {implied_parent}")
            require(
                task.get("parent") == implied_parent,
                errors,
                f"{task_id} parent field {task.get('parent')!r} does not match implied parent {implied_parent}",
            )
            require(
                task.get("type") in CHILD_TASK_TYPES,
                errors,
                f"{task_id} is a child task and must use one of {sorted(CHILD_TASK_TYPES)}",
            )
        elif parent_match or ux_parent_match:
            require(task.get("parent") is None, errors, f"{task_id} is a parent task and parent must be null")
            require(
                task.get("type") in PARENT_TASK_TYPES,
                errors,
                f"{task_id} is a parent task and must use one of {sorted(PARENT_TASK_TYPES)}",
            )
            if ux_parent_match:
                require(
                    task.get("type") == "docs-only",
                    errors,
                    f"{task_id} UX parent task must use type docs-only",
                )

        if task.get("type") in {"validation", "validation_microtask"}:
            tags = task.get("boundary_tags", [])
            require("validation" in tags, errors, f"{task_id} validation task must include validation boundary tag")
            require(
                task_id == "PHASE7-IMPL-010"
                or task.get("parent") == "PHASE7-IMPL-010"
                or task_id.startswith("PHASE7-IMPL-004-T"),
                errors,
                f"{task_id} is validation work but is not PHASE7-IMPL-010, a child of PHASE7-IMPL-010, or a PHASE7-IMPL-004 compatibility test micro-task",
            )

    active = data.get("active_frontier")
    require(isinstance(active, dict), errors, "active_frontier must be an object")
    if isinstance(active, dict):
        active_id = active.get("current_parent_task_id")
        active_title = active.get("current_parent_task_title")
        require(active_id in tasks_by_id, errors, f"active parent task {active_id!r} does not exist")
        if active_id in tasks_by_id:
            actual_title = tasks_by_id[active_id].get("title")
            require(
                active_title == actual_title,
                errors,
                f"active title {active_title!r} does not match task title {actual_title!r}",
            )

    task_004 = tasks_by_id.get("PHASE7-IMPL-004")
    require(task_004 is not None, errors, "PHASE7-IMPL-004 must exist")
    if task_004 is not None:
        require(
            task_004.get("title") == "Chapter / Scene Metadata Compatibility Layer",
            errors,
            "PHASE7-IMPL-004 title must be exactly Chapter / Scene Metadata Compatibility Layer",
        )
        require(task_004.get("type") == "runtime", errors, "PHASE7-IMPL-004 type must be runtime")

    task_010 = tasks_by_id.get("PHASE7-IMPL-010")
    require(task_010 is not None, errors, "PHASE7-IMPL-010 must exist")
    if task_010 is not None:
        require(task_010.get("type") == "validation", errors, "PHASE7-IMPL-010 type must be validation")

    task_004_t001 = tasks_by_id.get("PHASE7-IMPL-004-T001")
    require(task_004_t001 is not None, errors, "PHASE7-IMPL-004-T001 must exist")
    if task_004_t001 is not None:
        require(
            task_004_t001.get("type") == "planning_microtask",
            errors,
            "PHASE7-IMPL-004-T001 type must be planning_microtask",
        )
        require(task_004_t001.get("status") == "ready", errors, "PHASE7-IMPL-004-T001 status must be ready")
        require(
            task_004_t001.get("parent") == "PHASE7-IMPL-004",
            errors,
            "PHASE7-IMPL-004-T001 parent must be PHASE7-IMPL-004",
        )

    return errors


def main() -> int:
    try:
        registry = load_registry()
        errors = validate_registry(registry)
    except ValueError as exc:
        print("FAIL")
        print(f"- {exc}")
        return 1

    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
