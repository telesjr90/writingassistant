#!/usr/bin/env python3
"""Deterministically validate specialized Project Memory reviewer guidance."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable


PROTOCOL_PATH = "docs/project-memory/reviewer-protocol.md"
SKILL_PATH = ".agents/skills/project-memory-plan-integrity-review/SKILL.md"
REVIEWER_AGENTS = {
    "backend_contracts": ".opencode/agents/project-memory-backend-contract-reviewer.md",
    "frontend_ui": ".opencode/agents/project-memory-frontend-ui-reviewer.md",
    "test_coverage": ".opencode/agents/project-memory-test-coverage-reviewer.md",
    "roadmap_consistency": ".opencode/agents/project-memory-roadmap-consistency-reviewer.md",
    "enrichment_accuracy": ".opencode/agents/project-memory-enrichment-accuracy-reviewer.md",
    "decision_coherence": ".opencode/agents/project-memory-decision-coherence-reviewer.md",
}
REQUIRED_FILES = (PROTOCOL_PATH, SKILL_PATH, *REVIEWER_AGENTS.values())

REQUIRED_REQUEST_TOKENS = (
    "`repository_root`",
    "`expected_branch`",
    "`expected_full_commit`",
    "`reviewer_domain`",
    "`task_or_feature_scope`",
    "`maximum_file_scope`",
    "`allowed_source_classes`",
    "`protected_paths`",
    "`accepted_plan_integrity_report_path`",
    "`freshness_requirement`",
    "`historical_evidence_permission`",
    "`owner_decision_requirement`",
)
REQUIRED_FINDING_TOKENS = (
    "`finding_id`",
    "`rule_or_concern_id`",
    "`bounded_claim`",
    "`blocking_recommendation`",
    "`affected_ids`",
    "`evidence_locators`",
    "`facts`",
    "`inferences`",
    "`uncertainty_or_conflicting_evidence`",
    "`owner_decision_status`",
    "`recommended_deterministic_follow_up`",
    "`authority_declaration`",
    "`generated_evidence`",
)
REQUIRED_CONTROLS = (
    "write: false",
    "edit: false",
    "patch: false",
    "webfetch: false",
    "task: false",
    "external_directory: deny",
    '"*": deny',
)
ALLOWED_SHELL_GRANTS = (
    '"git status*": allow',
    '"git branch --show-current": allow',
    '"git rev-parse HEAD": allow',
    '"git log -1*": allow',
    '"git diff --quiet": allow',
    '"git diff --cached --quiet": allow',
)
REQUIRED_BOUNDARIES = (
    "generated_evidence",
    "T009",
    "Memory/Canon",
    "apply-promotion",
    "story prose",
    "model",
    "network",
    "external directory",
    "Git mutation",
    "nested agents",
    "retrieval tool",
)


def _missing_tokens(text: str, tokens: Iterable[str]) -> list[str]:
    normalized = " ".join(text.replace("-", " ").split()).lower()
    return sorted(
        token
        for token in tokens
        if " ".join(token.replace("-", " ").split()).lower() not in normalized
    )


def _read(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def validate_reviewer_guidance(repo_root: str | Path) -> dict:
    """Return a stable validation report for the protocol, skill, and agents."""
    root = Path(repo_root).resolve()
    findings: list[dict[str, str]] = []
    contents: dict[str, str] = {}
    for relative_path in REQUIRED_FILES:
        path = root / relative_path
        if not path.is_file():
            findings.append({
                "code": "missing_required_file",
                "path": relative_path,
                "detail": "required reviewer guidance file is missing",
            })
            continue
        contents[relative_path] = _read(root, relative_path)

    protocol = contents.get(PROTOCOL_PATH, "")
    for token in _missing_tokens(
        protocol,
        (*REVIEWER_AGENTS, *REQUIRED_REQUEST_TOKENS, *REQUIRED_FINDING_TOKENS),
    ):
        findings.append({
            "code": "missing_protocol_token",
            "path": PROTOCOL_PATH,
            "detail": token,
        })

    shared = "\n".join(contents.values())
    for token in _missing_tokens(shared, REQUIRED_BOUNDARIES):
        findings.append({
            "code": "missing_shared_boundary",
            "path": "<reviewer-guidance-set>",
            "detail": token,
        })

    skill = contents.get(SKILL_PATH, "")
    for token in _missing_tokens(skill, (PROTOCOL_PATH, "six domains", "facts", "inferences")):
        findings.append({
            "code": "missing_skill_contract",
            "path": SKILL_PATH,
            "detail": token,
        })

    forbidden_grants = (
        "write: true",
        "edit: true",
        "patch: true",
        "webfetch: true",
        "task: true",
        "external_directory: allow",
    )
    for domain, relative_path in REVIEWER_AGENTS.items():
        agent = contents.get(relative_path, "")
        for token in _missing_tokens(agent, (*REQUIRED_CONTROLS, domain, PROTOCOL_PATH, SKILL_PATH)):
            findings.append({
                "code": "missing_reviewer_control",
                "path": relative_path,
                "detail": token,
            })
        for token in forbidden_grants:
            if token in agent:
                findings.append({
                    "code": "forbidden_permission_grant",
                    "path": relative_path,
                    "detail": token,
                })
        frontmatter = agent.split("---", 2)[1] if agent.count("---") >= 2 else ""
        grants = tuple(
            line.strip()
            for line in frontmatter.splitlines()
            if line.strip().endswith(": allow")
        )
        if grants != ALLOWED_SHELL_GRANTS:
            findings.append({
                "code": "shell_allowlist_mismatch",
                "path": relative_path,
                "detail": json.dumps(grants),
            })

    findings.sort(key=lambda item: (item["code"], item["path"], item["detail"]))
    return {
        "result": "PASS" if not findings else "BLOCKED",
        "checked_files": list(REQUIRED_FILES),
        "reviewer_domains": list(REVIEWER_AGENTS),
        "findings": findings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    report = validate_reviewer_guidance(args.repo_root)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(report["result"])
        for finding in report["findings"]:
            print(f"{finding['code']}: {finding['path']}: {finding['detail']}")
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
