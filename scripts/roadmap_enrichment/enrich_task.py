#!/usr/bin/env python3
"""Create scaffold and collect-plan files for one roadmap task."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
INDEX_PATH = ROOT / "docs" / "roadmap" / "roadmap_index.yaml"
CCE_QUERIES_PATH = ROOT / "scripts" / "roadmap_enrichment" / "templates" / "cce_queries.yaml"
GRAPHIFY_QUERIES_PATH = ROOT / "scripts" / "roadmap_enrichment" / "templates" / "graphify_queries.yaml"
TOOL_COMMANDS_PATH = ROOT / "scripts" / "roadmap_enrichment" / "tool_commands.md"


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
    parser = argparse.ArgumentParser(description="Create scaffold roadmap enrichment files.")
    selector = parser.add_mutually_exclusive_group(required=True)
    selector.add_argument("--task", help="Task ID to scaffold.")
    selector.add_argument("--active", action="store_true", help="Use active_frontier.current_parent_task_id.")
    parser.add_argument("--mode", required=True, choices=["scaffold", "collect-plan"], help="Scaffold mode to run.")
    return parser.parse_args()


def select_task(data: dict[str, Any], task_id: str | None, active: bool) -> dict[str, Any]:
    tasks_by_id = task_map(data)

    if active:
        active = data.get("active_frontier")
        if not isinstance(active, dict):
            raise ValueError("active_frontier must be an object")
        task_id = active.get("current_parent_task_id")

    task = tasks_by_id.get(task_id)
    if not isinstance(task, dict):
        raise ValueError(f"task {task_id!r} does not exist")

    if task.get("parent") is not None or "-T" in str(task.get("id")):
        raise ValueError(f"task {task_id} is a child micro-task; select a parent task")

    context_pack = task.get("context_pack")
    if not isinstance(context_pack, str) or not context_pack:
        raise ValueError(f"task {task_id} is missing context_pack")

    return task


def build_manifest(task: dict[str, Any]) -> dict[str, Any]:
    manifest = {
        "task_id": task.get("id"),
        "title": task.get("title"),
        "status": task.get("status"),
        "type": task.get("type"),
        "parent": task.get("parent"),
        "boundary_tags": task.get("boundary_tags", []),
        "task_record": task.get("task_record"),
        "inventory_record": task.get("inventory_record"),
        "enrichment_record": task.get("enrichment_record"),
        "context_pack": task.get("context_pack"),
    }
    return manifest


def write_manifest(task: dict[str, Any]) -> Path:
    manifest = build_manifest(task)
    context_dir = ROOT / str(task["context_pack"])
    context_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = context_dir / "task_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest_path


def load_query_template(path: Path) -> dict[str, list[str]]:
    if not path.exists():
        raise ValueError(f"query template does not exist: {path.relative_to(ROOT)}")

    result: dict[str, list[str]] = {}
    current_key: str | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if not raw_line.startswith(" ") and line.endswith(":"):
            current_key = line[:-1]
            result[current_key] = []
            continue
        stripped = line.strip()
        if current_key and stripped.startswith("- "):
            value = stripped[2:].strip()
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            result[current_key].append(value)
            continue
        raise ValueError(f"unsupported query template syntax in {path.relative_to(ROOT)}: {raw_line}")
    return result


def render_query(query: str, task: dict[str, Any]) -> str:
    return query.replace("{{ task_id }}", str(task["id"])).replace("{{ title }}", str(task["title"]))


def task_queries(path: Path, task: dict[str, Any]) -> list[str]:
    template = load_query_template(path)
    queries = template.get(str(task["id"]), template.get("default", []))
    return [render_query(query, task) for query in queries]


def write_query_file(path: Path, title: str, task: dict[str, Any], queries: list[str]) -> None:
    lines = [
        f"# {title}",
        "",
        f"- Task ID: `{task['id']}`",
        f"- Title: {task['title']}",
        "- Status: planned only; commands were not run.",
        "",
        "## Queries",
        "",
    ]
    lines.extend(f"- {query}" for query in queries)
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def phase7_impl_004_repomix_candidates() -> list[str]:
    return [
        "# Starter candidate list for PHASE7-IMPL-004.",
        "# These are likely paths only. This is not a broad glob list.",
        "AGENTS.md",
        "CLAUDE.md",
        "docs/roadmap/implementation_status.md",
        "docs/roadmap/roadmap_index.yaml",
        "docs/roadmap/project_workspace_implementation_decision_sweep.md",
        "docs/roadmap/task_backlog.md",
        "docs/roadmap/phase_map.md",
        "docs/roadmap/decision_log.md",
        "docs/roadmap/risk_register.md",
        "docs/roadmap/open_questions.md",
        "scripts/validate_roadmap.py",
        "scripts/check_enrichment.py",
        "# Backend/frontend/test file candidates must be filled after CCE/Graphify",
        "# or manual read-only inventory identifies exact paths.",
    ]


def default_repomix_candidates(task: dict[str, Any]) -> list[str]:
    return [
        f"# Starter candidate list for {task['id']}.",
        "# Fill exact paths after explicit collection or manual read-only inventory.",
        "AGENTS.md",
        "CLAUDE.md",
        "docs/roadmap/implementation_status.md",
        "docs/roadmap/roadmap_index.yaml",
        "docs/roadmap/task_backlog.md",
        "docs/roadmap/phase_map.md",
    ]


def ensure_ai_context_candidates(path: Path, task: dict[str, Any]) -> None:
    note = (
        "\n## Collect-Plan Note\n\n"
        f"- Collect-plan mode prepared planned evidence files for `{task['id']}`.\n"
        "- AI Context generation was not run.\n"
        "- Verify the output path before running any future AI Context command.\n"
    )
    if path.exists():
        text = path.read_text(encoding="utf-8")
        if "## Collect-Plan Note" not in text:
            path.write_text(text.rstrip() + note + "\n", encoding="utf-8")
        return

    path.write_text(
        f"# {task['id']} AI Context Command Candidates\n\n"
        "No AI Context command has been confirmed for this task yet.\n"
        "AI Context generation was not run.\n"
        "Verify the output path before running any future AI Context command.\n"
        + note,
        encoding="utf-8",
    )


def write_collection_plan(context_dir: Path, task: dict[str, Any], outputs: dict[str, str]) -> None:
    lines = [
        f"# Collection Plan: {task['id']}",
        "",
        f"- Task ID: `{task['id']}`",
        f"- Title: {task['title']}",
        f"- Status: {task['status']}",
        f"- Boundary tags: {', '.join(task.get('boundary_tags', []))}",
        "",
        "## Exact Intended Evidence Outputs",
        "",
    ]
    lines.extend(f"- `{path}`" for path in outputs.values())
    lines.extend(
        [
            "",
            "## Manual Collection Steps",
            "",
            "1. Review `scripts/roadmap_enrichment/tool_commands.md` for confirmed local syntax.",
            "2. Run only human-approved collection commands in a future explicit collect task.",
            "3. Save CCE findings, Graphify output, Repomix output, inventory, enrichment JSON, and rendered task record to the planned paths.",
            "4. Re-run roadmap and enrichment validators after collected evidence is written.",
            "",
            "## Safety Rules",
            "",
            "- Collect-plan mode does not run CCE, Graphify, Repomix, AI Context generation, LeanCTX, MCP tools, tests, or app servers.",
            "- Do not modify application code during collection planning.",
            "- Generated context files are evidence artifacts, not source of truth.",
            "- Source of truth remains the roadmap control layer and reviewed task records.",
            "",
            "## Tool Command References",
            "",
            "- `scripts/roadmap_enrichment/tool_commands.md`",
            "- `scripts/roadmap_enrichment/templates/tool_command_probe.md`",
            "",
            "No collection commands were run by collect-plan mode.",
            "",
        ]
    )
    (context_dir / "collection_plan.md").write_text("\n".join(lines), encoding="utf-8")


def write_collect_plan(task: dict[str, Any]) -> list[Path]:
    manifest_path = write_manifest(task)
    context_dir = ROOT / str(task["context_pack"])
    task_id = str(task["id"])

    cce_queries_path = context_dir / "cce-queries.md"
    graphify_queries_path = context_dir / "graphify-queries.md"
    repomix_candidates_path = context_dir / "repomix-include-candidates.txt"
    ai_context_candidates_path = context_dir / "ai-context-command-candidates.md"
    evidence_manifest_path = context_dir / "evidence_manifest.json"

    write_query_file(cce_queries_path, "CCE Query Plan", task, task_queries(CCE_QUERIES_PATH, task))
    write_query_file(
        graphify_queries_path,
        "Graphify Query Plan",
        task,
        task_queries(GRAPHIFY_QUERIES_PATH, task),
    )

    candidates = phase7_impl_004_repomix_candidates() if task_id == "PHASE7-IMPL-004" else default_repomix_candidates(task)
    repomix_candidates_path.write_text("\n".join(candidates) + "\n", encoding="utf-8")
    ensure_ai_context_candidates(ai_context_candidates_path, task)

    expected_future_outputs = {
        "cce_findings": f".codex-context/{task_id}/cce-findings.md",
        "graphify_output": f".codex-context/{task_id}/graphify-output.md",
        "repomix_output": f".codex-context/{task_id}/repomix-output.md",
        "inventory": str(task.get("inventory_record")),
        "enrichment_json": str(task.get("enrichment_record")),
        "task_record": str(task.get("task_record")),
    }
    outputs = {
        "task_manifest": str(manifest_path.relative_to(ROOT)),
        "cce_queries": str(cce_queries_path.relative_to(ROOT)),
        "graphify_queries": str(graphify_queries_path.relative_to(ROOT)),
        "repomix_include_candidates": str(repomix_candidates_path.relative_to(ROOT)),
        "ai_context_command_candidates": str(ai_context_candidates_path.relative_to(ROOT)),
        "evidence_manifest": str(evidence_manifest_path.relative_to(ROOT)),
    }
    write_collection_plan(context_dir, task, {**outputs, **expected_future_outputs})

    evidence_manifest = {
        "task_id": task_id,
        "title": task.get("title"),
        "mode": "collect-plan",
        "collection_status": "planned_not_collected",
        "task_manifest": outputs["task_manifest"],
        "cce_queries": outputs["cce_queries"],
        "graphify_queries": outputs["graphify_queries"],
        "repomix_include_candidates": outputs["repomix_include_candidates"],
        "ai_context_command_candidates": outputs["ai_context_command_candidates"],
        "tool_commands": "scripts/roadmap_enrichment/tool_commands.md",
        "expected_future_outputs": expected_future_outputs,
    }
    evidence_manifest_path.write_text(json.dumps(evidence_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return [
        manifest_path,
        context_dir / "collection_plan.md",
        cce_queries_path,
        graphify_queries_path,
        repomix_candidates_path,
        ai_context_candidates_path,
        evidence_manifest_path,
    ]


def main() -> int:
    args = parse_args()

    try:
        data = load_index()
        task = select_task(data, args.task, args.active)
        if args.mode == "scaffold":
            written_paths = [write_manifest(task)]
        else:
            written_paths = write_collect_plan(task)
    except ValueError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    for path in written_paths:
        print(path.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
