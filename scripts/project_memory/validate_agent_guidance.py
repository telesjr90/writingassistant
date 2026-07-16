#!/usr/bin/env python3
"""Deterministically validate the tracked Project Memory agent guidance."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Iterable


REQUIRED_FILES = (
    "AGENTS.md",
    "docs/project-memory/ask-protocol.md",
    "docs/project-memory/reviewer-protocol.md",
    ".agents/skills/project-memory-read/SKILL.md",
    ".agents/skills/project-memory-plan-integrity-review/SKILL.md",
    ".agents/skills/writing-assistant-ui-execution/SKILL.md",
    ".opencode/agents/project-memory-ask.md",
    ".opencode/agents/project-memory-frontend-ui-reviewer.md",
)

REQUIRED_PROTOCOL_TOKENS = (
    "`question`",
    "`repository_root`",
    "`expected_branch`",
    "`expected_commit`",
    "`task_or_feature_scope`",
    "`requested_evidence_classes`",
    "`freshness_requirement`",
    "`historical_evidence_permitted`",
    "`maximum_scope`",
    "`protected_paths`",
    "`owner_decision_requirement`",
    "`direct_answer`",
    "`result`",
    "`facts`",
    "`inferences`",
    "`authoritative_sources`",
    "`supporting_generated_evidence`",
    "`source_locators`",
    "`authority_class_by_source`",
    "`source_freshness_and_bound_commit`",
    "`conflicts_and_uncertainty`",
    "`owner_pending_decisions`",
    "`limitations`",
    "`recommended_next_deterministic_check`",
    "`ANSWERED`",
    "`PARTIAL`",
    "`INSUFFICIENT_EVIDENCE`",
    "`CONFLICT`",
    "`OUT_OF_SCOPE`",
)

REQUIRED_SHARED_TOKENS = (
    "generated evidence",
    "Memory/Canon",
    "story prose",
    "model output",
    "docs/roadmap/roadmap_index.yaml",
    "docs/project-memory/registries/execution-routing.json",
    "FRESH",
    "Plan Integrity",
    "dependency eligibility",
    "writing-assistant-ui-execution",
    "Impeccable",
)


def _read(repo_root: Path, relative_path: str) -> str:
    return (repo_root / relative_path).read_text(encoding="utf-8")


def _missing_tokens(text: str, tokens: Iterable[str]) -> list[str]:
    lowered = text.lower()
    return sorted(token for token in tokens if token.lower() not in lowered)


def _active_policy_text(text: str) -> str:
    """Blank locally classified historical/superseded Markdown sections."""
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
        kept.append(line if excluded_level is None else "")
    return "\n".join(kept)


def validate_agent_guidance(repo_root: str | Path) -> dict:
    """Return a stable JSON-serializable validation report."""
    root = Path(repo_root).resolve()
    findings: list[dict[str, str]] = []
    contents: dict[str, str] = {}

    for relative_path in REQUIRED_FILES:
        path = root / relative_path
        if not path.is_file():
            findings.append({
                "code": "missing_required_file",
                "path": relative_path,
                "detail": "required tracked guidance file is missing",
            })
            continue
        contents[relative_path] = _read(root, relative_path)

    protocol = contents.get("docs/project-memory/ask-protocol.md", "")
    for token in _missing_tokens(protocol, REQUIRED_PROTOCOL_TOKENS):
        findings.append({
            "code": "missing_protocol_token",
            "path": "docs/project-memory/ask-protocol.md",
            "detail": token,
        })

    combined = "\n".join(contents.values())
    for token in _missing_tokens(combined, REQUIRED_SHARED_TOKENS):
        findings.append({
            "code": "missing_shared_boundary",
            "path": "<guidance-set>",
            "detail": token,
        })

    obsolete_patterns = (
        "opencode go as the selected low-cost coding-agent platform for remaining mvp",
        "excluded from this implementation workflow: openai",
    )
    for relative_path, text in contents.items():
        lowered = _active_policy_text(text).lower()
        for phrase in obsolete_patterns:
            if phrase in lowered:
                findings.append({
                    "code": "obsolete_active_execution_guidance",
                    "path": relative_path,
                    "detail": phrase,
                })

    agent = contents.get(".opencode/agents/project-memory-ask.md", "")
    required_agent_controls = (
        "write: false",
        "edit: false",
        "patch: false",
        "webfetch: false",
        '"*": deny',
        "external_directory: deny",
    )
    for token in _missing_tokens(agent, required_agent_controls):
        findings.append({
            "code": "missing_read_only_control",
            "path": ".opencode/agents/project-memory-ask.md",
            "detail": token,
        })

    forbidden_grants = (
        "write: true",
        "edit: true",
        "patch: true",
        "webfetch: true",
        "external_directory: allow",
    )
    for token in sorted(forbidden_grants):
        if token in agent:
            findings.append({
                "code": "forbidden_permission_grant",
                "path": ".opencode/agents/project-memory-ask.md",
                "detail": token,
            })

    findings.sort(key=lambda item: (item["code"], item["path"], item["detail"]))
    return {
        "result": "PASS" if not findings else "BLOCKED",
        "checked_files": list(REQUIRED_FILES),
        "findings": findings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    report = validate_agent_guidance(args.repo_root)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(report["result"])
        for finding in report["findings"]:
            print(f"{finding['code']}: {finding['path']}: {finding['detail']}")
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
