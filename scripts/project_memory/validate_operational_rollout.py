#!/usr/bin/env python3
"""Validate the tracked Project Memory operational rollout contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

REQUIRED_FILES = (
    ".gitignore",
    "docs/project-memory/operations.json",
    "docs/project-memory/operator-manual.md",
    "docs/project-memory/chatgpt-github-supervision-policy.md",
    "scripts/project_memory/operational_rollout.py",
    "scripts/project_memory/supervise.py",
    "scripts/project_memory/build_quality_package.py",
    "scripts/project_memory/validate_operational_rollout.py",
    "tests/project_memory/test_operational_rollout.py",
    "tests/project_memory/test_supervise.py",
    ".github/workflows/project-memory.yml",
    "docs/roadmap/decisions/PHASE8-IMPL-026-T011-synchronization-ci-rebuild-operational-rollout.md",
    "docs/roadmap/decisions/PHASE8-IMPL-026-T011-project-memory-gate-decoupling-and-github-handoff.md",
)

REQUIRED_STALE_REASONS = {
    "dirty_worktree", "staged_changes", "branch_mismatch", "commit_mismatch",
    "accepted_application_commit_mismatch", "missing_required_package",
    "malformed_metadata", "inventory_mismatch", "checksum_failure",
    "registry_hash_drift", "source_hash_drift", "non_current_snapshot",
    "non_publication_eligible_snapshot", "blocked_plan_integrity_readiness",
    "semantic_validation_failure", "authority_validation_failure", "quality_gate_failure",
}

FORBIDDEN_SYNC_METHODS = {
    "path_filtered_cherry_pick", "roadmap_only_copy", "reset", "restore",
    "clean", "stash", "rebase", "amend", "force_push",
}


def _finding(code: str, path: str, detail: str) -> dict[str, str]:
    return {"code": code, "path": path, "detail": detail}


def _gitignore_rules(contents: str) -> set[str]:
    """Return exact active Git ignore rules, excluding blanks and comments."""
    return {
        line.strip()
        for line in contents.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }


def validate_operational_rollout(repo_root: str | Path = ".") -> dict[str, Any]:
    root = Path(repo_root).resolve()
    findings: list[dict[str, str]] = []
    contents: dict[str, str] = {}
    for relative in REQUIRED_FILES:
        path = root / relative
        if not path.is_file():
            findings.append(_finding("missing_required_file", relative, "required T011 file is missing"))
            continue
        contents[relative] = path.read_text(encoding="utf-8")

    if ".codex-context/" not in _gitignore_rules(contents.get(".gitignore", "")):
        findings.append(_finding(
            "generated_evidence_ignore_missing",
            ".gitignore",
            "exact active .codex-context/ ignore rule is required",
        ))

    policy_path = root / "docs/project-memory/operations.json"
    try:
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        findings.append(_finding("malformed_policy", "docs/project-memory/operations.json", str(exc)))
        policy = {}
    expected_scalars = {
        "schema": "project-memory-operations.v1",
        "version": "1.1.0",
        "authoritative_branch": "docs/project-memory-foundation",
        "generated_evidence_authority": "generated_evidence",
    }
    for key, expected in expected_scalars.items():
        if policy.get(key) != expected:
            findings.append(_finding("policy_value_mismatch", "docs/project-memory/operations.json", key))
    cadence = policy.get("cadence", {})
    if cadence.get("kind") != "event_driven_commit_bound" or cadence.get("time_based_schedule_required") is not False:
        findings.append(_finding("cadence_mismatch", "docs/project-memory/operations.json", "event-driven/no-cron cadence required"))
    synchronization = policy.get("synchronization", {})
    if not FORBIDDEN_SYNC_METHODS <= set(synchronization.get("forbidden_methods", [])):
        findings.append(_finding("forbidden_sync_methods_incomplete", "docs/project-memory/operations.json", "required forbidden methods missing"))
    if synchronization.get("automatic_git_mutation") is not False:
        findings.append(_finding("automatic_git_mutation_enabled", "docs/project-memory/operations.json", "must be false"))
    if not REQUIRED_STALE_REASONS <= set(policy.get("stale_state_reasons", [])):
        findings.append(_finding("stale_reasons_incomplete", "docs/project-memory/operations.json", "required stale reasons missing"))
    if policy.get("accepted_readiness") != ["READY", "READY_WITH_ADVISORIES"]:
        findings.append(_finding("readiness_mismatch", "docs/project-memory/operations.json", "accepted readiness values"))
    if policy.get("accepted_nonblocking_advisory_codes") != ["source_missing"]:
        findings.append(_finding("advisory_allowlist_mismatch", "docs/project-memory/operations.json", "only source_missing is accepted"))
    supervision = policy.get("supervision", {})
    profiles = supervision.get("gate_profiles", {})
    if set(profiles) != {"implementation", "closeout", "governance"}:
        findings.append(_finding("supervision_profiles_mismatch", "docs/project-memory/operations.json", "three exact gate profiles required"))
    implementation = profiles.get("implementation", {})
    if (
        implementation.get("application_commit_lag_advisory") != "project_memory_commit_lag_application_only"
        or implementation.get("exact_commit_fresh_required") is not False
        or implementation.get("full_refresh_performed") is not False
        or implementation.get("task_acceptance_allowed") is not False
        or implementation.get("frontier_mutation_allowed") is not False
    ):
        findings.append(_finding("implementation_profile_mismatch", "docs/project-memory/operations.json", "bounded advisory and non-mutation contract"))
    for strict_mode in ("closeout", "governance"):
        profile = profiles.get(strict_mode, {})
        if profile.get("exact_commit_fresh_required") is not True or profile.get("plan_integrity_zero_blockers_required") is not True:
            findings.append(_finding("strict_profile_mismatch", "docs/project-memory/operations.json", strict_mode))
    handoff = supervision.get("handoff", {})
    if handoff != {
        "schema": "project-memory-supervision-handoff.v1",
        "authority_class": "generated_evidence",
        "output_root": ".codex-context/project-memory/handoff",
        "files": ["project-memory-handoff.md", "project-memory-handoff.json", "SHA256SUMS"],
        "atomic": True,
        "network_required": False,
        "tracked_state_mutation": False,
    }:
        findings.append(_finding("handoff_policy_mismatch", "docs/project-memory/operations.json", "deterministic local generated-evidence handoff"))
    no_next = policy.get("closed_parent_no_next_task", {})
    if no_next != {
        "representation": "json_null",
        "parent_status": "complete",
        "maintenance_mode": "operational_procedure",
        "procedure_task_id": "PHASE8-IMPL-026-T011",
        "accepted_evidence_required": True,
        "roadmap_convergence_required": True,
    }:
        findings.append(_finding("no_next_contract_mismatch", "docs/project-memory/operations.json", "closed-parent null contract"))
    boundaries = policy.get("mutation_boundaries", {})
    if not boundaries or any(value is not False for value in boundaries.values()):
        findings.append(_finding("mutation_boundary_mismatch", "docs/project-memory/operations.json", "all automatic mutation flags must be false"))

    manual = contents.get("docs/project-memory/operator-manual.md", "").lower()
    for token in (
        "owner-controlled synchronization", "deterministic refresh", "ci verification",
        "publication acceptance", "historical evidence retention", "stale-state diagnosis",
        "no cron", "generated evidence", "path-filtered",
        "json", "null", "no next project memory implementation task",
        "supervision gate profiles", "project_memory_commit_lag_application_only",
        "chatgpt-github-supervision-policy.md", "fallback/bootstrap",
    ):
        if token not in manual:
            findings.append(_finding("manual_contract_missing", "docs/project-memory/operator-manual.md", token))

    workflow = contents.get(".github/workflows/project-memory.yml", "")
    for token in (
        "pull_request:", "push:", "workflow_dispatch:", "fetch-depth: 0",
        "validate_registries.py --json", "validate_agent_guidance.py --json",
        "validate_reviewer_guidance.py --json", "validate_operational_rollout.py --json",
        "python3 -m pytest tests/project_memory", "scripts/project_memory/supervise.py",
        "actions/checkout@v7", "actions/setup-python@v6",
        "actions/upload-artifact@v7", "actions/download-artifact@v8",
        "actions/github-script@v9", "GITHUB_STEP_SUMMARY",
        "<!-- project-memory-supervision -->", "pull-requests: write",
        "id: validation", "id: strict_refresh", "id: supervise", "if: always()",
        "if-no-files-found: error",
        "project-memory-handoff-artifact/project-memory-handoff.md",
        "project-memory-handoff-artifact/project-memory-handoff.json",
        "project-memory-handoff-artifact/SHA256SUMS",
    ):
        if token not in workflow:
            findings.append(_finding("workflow_contract_missing", ".github/workflows/project-memory.yml", token))
    if "schedule:" in workflow or "cron:" in workflow:
        findings.append(_finding("time_based_trigger_forbidden", ".github/workflows/project-memory.yml", "schedule/cron"))
    if "pip install" in workflow:
        findings.append(_finding("workflow_dependency_install_forbidden", ".github/workflows/project-memory.yml", "dependency install"))
    for forbidden in (
        "pull_request_target", "contents: write", "git push", "git commit",
        "ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION", "secrets.",
    ):
        if forbidden in workflow:
            findings.append(_finding("workflow_security_boundary", ".github/workflows/project-memory.yml", forbidden))
    if "permissions: {}" not in workflow:
        findings.append(_finding("workflow_permissions_mismatch", ".github/workflows/project-memory.yml", "deny by default permissions required"))
    if workflow.count('- ".gitignore"') != 2:
        findings.append(_finding(
            "workflow_ignore_trigger_mismatch",
            ".github/workflows/project-memory.yml",
            ".gitignore must trigger both pull-request and push validation",
        ))

    operational = contents.get("scripts/project_memory/operational_rollout.py", "")
    for token in ("status", "check", "refresh", "ci-check", "diagnostic_only", "allow_detached"):
        if token not in operational:
            findings.append(_finding("cli_contract_missing", "scripts/project_memory/operational_rollout.py", token))
    for command in ("git merge", "git cherry-pick", "git reset", "git restore", "git clean", "git stash", "git rebase", "git commit", "git push"):
        if command in operational:
            findings.append(_finding("forbidden_git_command", "scripts/project_memory/operational_rollout.py", command))
    supervisor = contents.get("scripts/project_memory/supervise.py", "")
    for token in ("implementation", "closeout", "governance", "project_memory_commit_lag_application_only", "SHA256SUMS", "acceptance_claimed"):
        if token not in supervisor:
            findings.append(_finding("supervisor_contract_missing", "scripts/project_memory/supervise.py", token))
    for token in ("urllib", "requests", "http.client", "socket."):
        if token in supervisor:
            findings.append(_finding("supervisor_network_boundary", "scripts/project_memory/supervise.py", token))

    enrichment_path = root / "docs/roadmap/enrichment/PHASE8-IMPL-026.enrichment.json"
    try:
        enrichment = json.loads(enrichment_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        findings.append(_finding("malformed_enrichment", str(enrichment_path.relative_to(root)), str(exc)))
        enrichment = {}
    tasks_path = root / "docs/project-memory/registries/tasks.json"
    try:
        task_records = json.loads(tasks_path.read_text(encoding="utf-8")).get("records", [])
    except (OSError, UnicodeError, json.JSONDecodeError, AttributeError) as exc:
        findings.append(_finding("malformed_task_registry", str(tasks_path.relative_to(root)), str(exc)))
        task_records = []
    t012 = next(
        (
            item for item in task_records
            if isinstance(item, dict) and item.get("task_id") == "PHASE8-IMPL-026-T012"
        ),
        None,
    )
    t012_status = (t012 or {}).get("lifecycle", {}).get("status")
    expected_next = (
        "PHASE8-IMPL-026-T012" if t012_status == "in_progress" else None
    )
    if t012_status not in {None, "in_progress", "complete"}:
        findings.append(_finding(
            "t012_lifecycle_invalid",
            str(tasks_path.relative_to(root)),
            f"expected absent, in_progress, or complete; observed {t012_status!r}",
        ))
    if enrichment.get("next_project_memory_task", "missing") != expected_next:
        findings.append(_finding(
            "next_task_representation_mismatch",
            str(enrichment_path.relative_to(root)),
            f"expected {expected_next!r} for T012 lifecycle {t012_status!r}",
        ))
    if enrichment.get("project_memory_maintenance") != {
        "implementation_task": None,
        "mode": "operational_procedure",
        "procedure_task_id": "PHASE8-IMPL-026-T011",
    }:
        findings.append(_finding("maintenance_mode_mismatch", str(enrichment_path.relative_to(root)), "operational procedure declaration"))

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
    result = validate_operational_rollout(args.repo_root)
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else result["result"])
    return 0 if result["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
