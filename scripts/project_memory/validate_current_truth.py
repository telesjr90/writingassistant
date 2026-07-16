#!/usr/bin/env python3
"""Validate delimited current-truth blocks and active shared agent guidance."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.project_memory.execution_routing import (
    ROUTING_SOURCE,
    UI_SKILL,
    validate_execution_routing,
)


ROADMAP_PATH = "docs/roadmap/roadmap_index.yaml"
START = "<!-- CURRENT-REPOSITORY-TRUTH:START -->"
END = "<!-- CURRENT-REPOSITORY-TRUTH:END -->"
CURRENT_TRUTH_FILES = (
    "docs/master_plan.md",
    "docs/roadmap/implementation_status.md",
    "docs/roadmap/task_backlog.md",
    "docs/roadmap/phase_map.md",
    "docs/roadmap/risk_register.md",
    "docs/roadmap/open_questions.md",
)
TASK_LIFECYCLE_SURFACES = (
    "docs/roadmap/tasks/PHASE8-IMPL-026.md",
    "docs/roadmap/tasks/PHASE8-IMPL-026-T012.md",
)
ACTIVE_GUIDANCE_FILES = (
    "AGENTS.md",
    "docs/project-memory/ask-protocol.md",
    "docs/project-memory/reviewer-protocol.md",
    ".agents/skills/project-memory-read/SKILL.md",
    ".agents/skills/project-memory-plan-integrity-review/SKILL.md",
    ".agents/skills/writing-assistant-ui-execution/SKILL.md",
    ".opencode/agents/project-memory-ask.md",
    ".opencode/agents/project-memory-frontend-ui-reviewer.md",
)
FIELD_PATTERN = re.compile(r"^- ([A-Za-z][A-Za-z /-]+):\s*`?([^`\n]+?)`?\s*$")


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _finding(
    rule_id: str,
    file: str,
    locator: str,
    offending_value: Any,
    expected_value: Any,
    classification: str,
    next_action: str,
) -> dict[str, Any]:
    return {
        "file": file,
        "locator": locator,
        "offending_value": offending_value,
        "expected_value": expected_value,
        "rule_id": rule_id,
        "classification": classification,
        "next_action": next_action,
    }


def current_blocks(text: str) -> list[tuple[int, str]]:
    """Return active blocks with their starting line; history outside is ignored."""
    blocks: list[tuple[int, str]] = []
    offset = 0
    while True:
        start = text.find(START, offset)
        if start < 0:
            break
        end = text.find(END, start + len(START))
        if end < 0:
            blocks.append((text.count("\n", 0, start) + 1, ""))
            break
        line = text.count("\n", 0, start) + 1
        blocks.append((line, text[start + len(START):end]))
        offset = end + len(END)
    return blocks


def _parse_fields(block: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in block.splitlines():
        match = FIELD_PATTERN.match(line.strip())
        if match:
            fields[match.group(1)] = match.group(2).strip()
    return fields


def _t012_status_line(text: str) -> tuple[int | None, str | None]:
    heading = re.search(
        r"^(#{1,6})\s+PHASE8-IMPL-026-T012\b.*$",
        text,
        flags=re.MULTILINE,
    )
    if not heading:
        return None, None
    section_start = heading.end()
    level = len(heading.group(1))
    next_heading = re.search(
        rf"^#{{1,{level}}}\s+",
        text[section_start:],
        flags=re.MULTILINE,
    )
    section_end = section_start + next_heading.start() if next_heading else len(text)
    section = text[section_start:section_end]
    status = re.search(r"^Status:\s*(.+?)\s*$", section, flags=re.MULTILINE | re.IGNORECASE)
    if status:
        absolute = section_start + status.start()
        return text.count("\n", 0, absolute) + 1, " ".join(status.group(1).split())
    status_heading = re.search(
        r"^#{2,6}\s+Status\s*$",
        section,
        flags=re.MULTILINE | re.IGNORECASE,
    )
    if status_heading:
        body_start = status_heading.end()
        first_line = re.search(r"\S[^\n]*", section[body_start:])
        if first_line:
            absolute = section_start + body_start + first_line.start()
            return (
                text.count("\n", 0, absolute) + 1,
                " ".join(first_line.group(0).split()),
            )
    return text.count("\n", 0, heading.start()) + 1, None


def active_guidance_text(text: str) -> str:
    """Exclude locally classified historical/superseded Markdown sections."""
    kept: list[str] = []
    excluded_level: int | None = None
    heading_pattern = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
    for line in text.splitlines():
        heading = heading_pattern.match(line)
        if heading:
            level = len(heading.group(1))
            title = heading.group(2).lower()
            if excluded_level is not None and level <= excluded_level:
                excluded_level = None
            if "historical" in title or "superseded" in title:
                excluded_level = level
                kept.append("")
                continue
        if excluded_level is None:
            kept.append(line)
        else:
            kept.append("")
    return "\n".join(kept)


def validate_current_truth(repo_root: str | Path = ROOT) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    roadmap = _load(root / ROADMAP_PATH)
    frontier = roadmap["active_frontier"]
    expected = {
        "Active application parent": frontier["current_parent_task_id"],
        "Immediate application frontier": frontier["next_readiness_task_id"],
        "Planned architecture parent": frontier["planned_architecture_parent_task_id"],
        "Terminal MVP gate": frontier["terminal_mvp_task_id"],
        "Current routing source": ROUTING_SOURCE,
    }
    findings: list[dict[str, Any]] = []
    observed_frontiers: list[tuple[str, str]] = []

    indexed_t012 = next(
        (task for task in roadmap.get("tasks", []) if task.get("id") == "PHASE8-IMPL-026-T012"),
        None,
    )
    expected_t012_status = {
        "active": "in progress/validation pending",
        "complete": "complete/PASS",
        "done": "complete/PASS",
    }.get(indexed_t012.get("status") if indexed_t012 else None)
    if expected_t012_status is None:
        findings.append(_finding(
            "TRUTH-005", ROADMAP_PATH, "task PHASE8-IMPL-026-T012 status",
            indexed_t012.get("status") if indexed_t012 else None,
            "active, complete, or done",
            "unsupported_t012_lifecycle",
            "Publish a supported T012 lifecycle in the authoritative roadmap index.",
        ))
    else:
        for relative in TASK_LIFECYCLE_SURFACES:
            path = root / relative
            line, actual = _t012_status_line(
                path.read_text(encoding="utf-8") if path.is_file() else ""
            )
            normalized_actual = re.sub(r"\s*/\s*", "/", actual.lower()) if actual else None
            if normalized_actual is None or not normalized_actual.startswith(expected_t012_status.lower()):
                findings.append(_finding(
                    "TRUTH-005", relative,
                    f"line {line}: PHASE8-IMPL-026-T012 Status" if line else "T012 section",
                    actual, expected_t012_status,
                    "task_lifecycle_surface_mismatch",
                    f"Converge the T012 status with {ROADMAP_PATH}.",
                ))

    for relative in CURRENT_TRUTH_FILES:
        path = root / relative
        if not path.is_file():
            findings.append(_finding(
                "TRUTH-001", relative, "file", None, "tracked file",
                "missing_current_truth_surface", "Restore the tracked current-truth surface.",
            ))
            continue
        blocks = current_blocks(path.read_text(encoding="utf-8"))
        if len(blocks) != 1:
            findings.append(_finding(
                "TRUTH-001", relative, "current block count", len(blocks), 1,
                "missing_or_ambiguous_current_truth_block",
                "Keep exactly one delimited current repository truth block.",
            ))
            continue
        line, block = blocks[0]
        fields = _parse_fields(block)
        for name, value in expected.items():
            actual = fields.get(name)
            if actual != value:
                findings.append(_finding(
                    "TRUTH-002", relative, f"line {line}: {name}", actual, value,
                    "stale_current_statement",
                    f"Derive {name} from {ROADMAP_PATH} and update the active block.",
                ))
        observed = fields.get("Immediate application frontier")
        if observed:
            observed_frontiers.append((relative, observed))
        lowered = " ".join(block.lower().split())
        forbidden_subtxt = (
            "full subtxt runtime remains owner-blocked",
            "subtxt licensing remains pending",
            "subtxt authorization remains pending",
        )
        for phrase in forbidden_subtxt:
            if phrase in lowered:
                findings.append(_finding(
                    "TRUTH-004", relative, f"line {line}", phrase,
                    "full Subtxt authorized and planned under PHASE8-IMPL-025 T005/T006",
                    "stale_active_subtxt_blocker",
                    "Move the old claim to explicit history and state current authorization.",
                ))

    frontier_values = {value for _, value in observed_frontiers}
    if len(frontier_values) > 1:
        findings.append(_finding(
            "TRUTH-003", "<current-truth-blocks>", "Immediate application frontier",
            sorted(frontier_values), frontier["next_readiness_task_id"],
            "conflicting_current_next_task_claims",
            "Make every active block derive the same frontier from roadmap_index.yaml.",
        ))

    obsolete_patterns = (
        re.compile(r"opencode go as the selected low-cost coding-agent platform for remaining mvp", re.I),
        re.compile(r"excluded from this implementation workflow:[^\n]*(gpt|codex)", re.I),
    )
    for relative in ACTIVE_GUIDANCE_FILES:
        path = root / relative
        if not path.is_file():
            findings.append(_finding(
                "GUIDANCE-001", relative, "file", None, "tracked guidance file",
                "missing_active_guidance", "Restore the required shared guidance file.",
            ))
            continue
        text = path.read_text(encoding="utf-8")
        active_text = active_guidance_text(text)
        for pattern in obsolete_patterns:
            match = pattern.search(active_text)
            if match:
                findings.append(_finding(
                    "GUIDANCE-002", relative,
                    f"line {active_text.count(chr(10), 0, match.start()) + 1}", match.group(0),
                    "committed per-task execution routing",
                    "obsolete_active_opencode_only_or_gpt_exclusion",
                    "Scope historical routing and resolve current tasks from the routing registry.",
                ))

    shared_bindings = (
        "AGENTS.md",
        "docs/project-memory/ask-protocol.md",
        "docs/project-memory/reviewer-protocol.md",
        ".agents/skills/project-memory-read/SKILL.md",
        ".agents/skills/project-memory-plan-integrity-review/SKILL.md",
        ".agents/skills/writing-assistant-ui-execution/SKILL.md",
    )
    for relative in shared_bindings:
        text = (root / relative).read_text(encoding="utf-8") if (root / relative).is_file() else ""
        for required in (ROADMAP_PATH, ROUTING_SOURCE):
            if required not in text:
                findings.append(_finding(
                    "GUIDANCE-003", relative, "current source binding", None, required,
                    "shared_guidance_missing_current_source",
                    "Bind the shared policy to live roadmap and routing authority.",
                ))
    frontend_wrapper = root / ".opencode/agents/project-memory-frontend-ui-reviewer.md"
    if frontend_wrapper.is_file() and UI_SKILL not in frontend_wrapper.read_text(encoding="utf-8"):
        findings.append(_finding(
            "UI-002", str(frontend_wrapper.relative_to(root)), "shared skill reference", None,
            UI_SKILL, "opencode_frontend_reviewer_bypasses_shared_ui_skill",
            "Make the OpenCode wrapper invoke the shared UI execution skill.",
        ))

    routing_report = validate_execution_routing(root, roadmap=roadmap)
    findings.extend(routing_report["findings"])
    findings.sort(key=lambda item: (
        item.get("file", ""), item.get("locator", ""), item.get("rule_id", "")
    ))
    return {
        "result": "PASS" if not findings else "BLOCKED",
        "checked_current_truth_files": list(CURRENT_TRUTH_FILES),
        "checked_guidance_files": list(ACTIVE_GUIDANCE_FILES),
        "expected": expected,
        "findings": findings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    report = validate_current_truth(args.repo_root)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(report["result"])
        for finding in report["findings"]:
            print(f"{finding['rule_id']}: {finding['file']}:{finding['locator']}")
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
