#!/usr/bin/env python3
"""Deterministic convergence checker for Project Memory.

Computes structured convergence findings from registry validation,
repository state, roadmap state, and source locator validation.

Usage:
  python3 scripts/project_memory/convergence.py --repo-root . --json
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import uuid
from collections import OrderedDict
from pathlib import Path
from typing import Any

_SCANNER_NAME = "convergence"
_SCANNER_VERSION = "1.0.0"

CODES: dict[str, str] = {
    "registry_validation_failed": "Registry validation produced errors.",
    "source_missing": "A source file referenced by a registry does not exist.",
    "source_not_tracked": "A source file is not tracked by Git.",
    "source_excluded": "A source file is in an excluded or protected path.",
    "source_locator_invalid": "A source locator has an invalid path.",
    "source_line_range_invalid": "A source locator line range is invalid.",
    "task_missing_from_roadmap": "A task referenced in a registry is missing from the roadmap.",
    "task_status_mismatch": "A task status differs between registry and roadmap.",
    "decision_missing": "A decision referenced in a registry has no decision record.",
    "decision_status_mismatch": "A decision status differs between registry and roadmap.",
    "frontier_mismatch": "The application frontier does not match expected value.",
    "planned_parent_activated_unexpectedly": "PHASE8-IMPL-025 shows unexpected activation.",
    "accepted_evidence_missing": "Expected accepted evidence is unavailable.",
    "generated_evidence_unavailable": "Generated evidence artifact is unavailable.",
    "source_hash_conflict": "A source file hash differs between records.",
    "supersession_conflict": "Supersession metadata is inconsistent.",
    "dependency_conflict": "Dependency graph has conflicts.",
    "working_tree_dirty": "Working tree is dirty for publication snapshot.",
    "staging_not_empty": "Staging area is not empty for publication snapshot.",
    "snapshot_not_commit_bound": "Snapshot was not created from a clean committed HEAD.",
}


def _stable_hash(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()[:12]


def _finding_id(code: str, **context) -> str:
    parts = [code] + sorted(f"{k}={v}" for k, v in context.items())
    return f"{code}-{_stable_hash('|'.join(parts))}"


_SEVERITY_RANK = {"critical": 0, "error": 1, "warning": 2, "info": 3}


def make_finding(
    code: str,
    severity: str,
    title: str,
    explanation: str,
    affected_record_ids: list[str] | None = None,
    source_locators: list[str] | None = None,
    authority_context: str = "",
    evidence: dict[str, Any] | None = None,
    blocks_publication: bool = False,
    owner_review_required: bool = False,
    suggested_action: str = "",
) -> dict[str, Any]:
    """Create a deterministic convergence finding."""
    if affected_record_ids is None:
        affected_record_ids = []
    if source_locators is None:
        source_locators = []
    if evidence is None:
        evidence = {}
    fid = _finding_id(code, affected=",".join(sorted(affected_record_ids)))
    finding: dict[str, Any] = {
        "finding_id": fid,
        "code": code,
        "severity": severity,
        "title": title,
        "explanation": explanation,
        "affected_record_ids": sorted(affected_record_ids),
        "source_locators": sorted(source_locators),
        "authority_context": authority_context,
        "evidence": evidence,
        "blocks_publication": blocks_publication,
        "owner_review_required": owner_review_required,
        "suggested_action": suggested_action,
    }
    return finding


def sort_findings(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Sort findings deterministically by severity, code, record, ID."""
    return sorted(findings, key=lambda f: (
        _SEVERITY_RANK.get(f.get("severity", "info"), 99),
        f.get("code", ""),
        ",".join(f.get("affected_record_ids", [])),
        f.get("finding_id", ""),
    ))


def compute_convergence(
    repo_root: str,
    registry_validation_findings: list[dict[str, str]] | None = None,
    repository_state: dict[str, Any] | None = None,
    roadmap_state: dict[str, Any] | None = None,
    source_locator_results: dict[str, Any] | None = None,
    require_clean: bool = True,
) -> dict[str, Any]:
    """Compute convergence findings and overall result.

    Returns:
        Dict with 'result' ('PASS', 'PASS_WITH_FINDINGS', 'BLOCKED')
        and 'findings' list.
    """
    findings: list[dict[str, Any]] = []

    if repository_state is None:
        from . import repository_state as rs
        repository_state = rs.collect_repository_state(repo_root)

    if roadmap_state is None:
        from . import repository_state as rs
        roadmap_state = rs.parse_roadmap_state(repo_root)

    if source_locator_results is None:
        from . import repository_state as rs
        source_locator_results = rs.validate_source_locators(repo_root)

    has_critical = False
    has_blocking = False

    if registry_validation_findings:
        errors = [f for f in registry_validation_findings if f.get("level") == "error"]
        if errors:
            finding = make_finding(
                code="registry_validation_failed",
                severity="critical",
                title="Registry validation produced errors",
                explanation=f"Tracked registries have {len(errors)} validation errors.",
                evidence={"error_count": len(errors), "errors": errors},
                blocks_publication=True,
                owner_review_required=True,
                suggested_action="Repair registry validation errors before creating a publication snapshot.",
            )
            findings.append(finding)
            has_critical = True
            has_blocking = True

    rs = repository_state or {}
    if rs.get("dirty", False) and require_clean:
        finding = make_finding(
            code="working_tree_dirty",
            severity="critical" if require_clean else "warning",
            title="Working tree is dirty",
            explanation=f"Repository has {len(rs.get('modified_paths', []))} modified files.",
            evidence={"modified_paths": rs.get("modified_paths", [])},
            blocks_publication=require_clean,
            owner_review_required=require_clean,
            suggested_action="Commit changes or use nonpublication mode for testing.",
        )
        findings.append(finding)
        if require_clean:
            has_critical = True
            has_blocking = True

    if rs.get("staged", False) and require_clean:
        finding = make_finding(
            code="staging_not_empty",
            severity="critical" if require_clean else "warning",
            title="Staging area is not empty",
            explanation="Files are staged but not committed.",
            blocks_publication=require_clean,
            owner_review_required=require_clean,
            suggested_action="Commit staged changes or unstage before creating a publication snapshot.",
        )
        findings.append(finding)
        if require_clean:
            has_critical = True
            has_blocking = True

    rmap = roadmap_state or {}
    frontier_next = rmap.get("frontier_next_task", "")
    if frontier_next and frontier_next != "PHASE8-IMPL-024-T003A":
        finding = make_finding(
            code="frontier_mismatch",
            severity="critical",
            title="Application frontier mismatch",
            explanation=f"Expected PHASE8-IMPL-024-T003A but found '{frontier_next}'.",
            evidence={"expected": "PHASE8-IMPL-024-T003A", "actual": frontier_next},
            blocks_publication=True,
            owner_review_required=True,
            suggested_action="Investigate why the application frontier changed.",
        )
        findings.append(finding)
        has_critical = True
        has_blocking = True

    task_index = rmap.get("task_index", {})
    ph_025 = task_index.get("PHASE8-IMPL-025", {})
    if ph_025.get("status") not in ("planned", "published/planned", "", None):
        finding = make_finding(
            code="planned_parent_activated_unexpectedly",
            severity="critical",
            title="PHASE8-IMPL-025 unexpectedly activated",
            explanation=f"PHASE8-IMPL-025 status is '{ph_025.get('status')}' but should remain planned/inactive.",
            evidence={"ph8_impl_025_status": ph_025.get("status", "")},
            blocks_publication=True,
            owner_review_required=True,
            suggested_action="Verify PHASE8-IMPL-025 activation before proceeding.",
        )
        findings.append(finding)
        has_critical = True
        has_blocking = True

    sl = source_locator_results or {}
    if sl.get("missing_count", 0) > 0:
        for loc in sl.get("missing_sources", []):
            finding = make_finding(
                code="source_missing",
                severity="warning",
                title=f"Source file not found: {loc.get('path', '')}",
                explanation=f"Source referenced by record {loc.get('record_id', '')} does not exist.",
                affected_record_ids=[loc.get("record_id", "")] if loc.get("record_id") else [],
                source_locators=[loc.get("path", "")],
                authority_context=loc.get("authority_class", ""),
                evidence={"reason": loc.get("reason", "")},
                suggested_action="Verify source exists in the repository or update the registry locator.",
            )
            findings.append(finding)

    if sl.get("invalid_count", 0) > 0:
        for loc in sl.get("invalid_locators", []):
            sev = "error" if loc.get("authority_class") == "authoritative" else "warning"
            finding = make_finding(
                code="source_locator_invalid",
                severity=sev,
                title=f"Invalid source locator: {loc.get('path', '')}",
                explanation=f"Source locator is invalid: {loc.get('reason', '')}",
                affected_record_ids=[loc.get("record_id", "")] if loc.get("record_id") else [],
                source_locators=[loc.get("path", "")],
                authority_context=loc.get("authority_class", ""),
                evidence={"reason": loc.get("reason", "")},
                suggested_action="Repair the source locator in the registry record.",
            )
            findings.append(finding)

    if sl.get("excluded_count", 0) > 0:
        for loc in sl.get("excluded_sources", []):
            finding = make_finding(
                code="source_excluded",
                severity="info",
                title=f"Source in excluded/protected path: {loc.get('path', '')}",
                explanation="Source locator references a protected or excluded path.",
                affected_record_ids=[loc.get("record_id", "")] if loc.get("record_id") else [],
                source_locators=[loc.get("path", "")],
                authority_context=loc.get("authority_class", ""),
                evidence={"reason": loc.get("reason", "")},
                suggested_action="No action needed if path is intentionally excluded.",
            )
            findings.append(finding)

    findings = sort_findings(findings)

    if has_blocking:
        result = "BLOCKED"
    elif findings:
        result = "PASS_WITH_FINDINGS"
    else:
        result = "PASS"

    return {
        "scanner_name": _SCANNER_NAME,
        "scanner_version": _SCANNER_VERSION,
        "result": result,
        "finding_count": len(findings),
        "findings": findings,
        "finding_codes": sorted(set(f["code"] for f in findings)),
        "blocked": has_blocking,
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Compute convergence findings.")
    parser.add_argument("--repo-root", default=".", help="Path to repository root.")
    parser.add_argument("--require-clean", action="store_true", default=True,
                        help="Require clean worktree (default).")
    parser.add_argument("--no-require-clean", action="store_false", dest="require_clean",
                        help="Allow dirty worktree for testing.")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON.")
    args = parser.parse_args()

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from scripts.project_memory import validate_registries as vr

    try:
        registry_findings = vr.validate()
    except Exception as exc:
        registry_findings = [{
            "level": "error",
            "code": "VALIDATOR_EXCEPTION",
            "message": str(exc),
        }]

    try:
        result = compute_convergence(
            repo_root=args.repo_root,
            registry_validation_findings=registry_findings,
            require_clean=args.require_clean,
        )
    except Exception as exc:
        if args.json:
            print(json.dumps({"error": str(exc)}, indent=2))
        else:
            print(f"ERROR: {exc}")
        return 1

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0

    print(f"Convergence result: {result['result']}")
    print(f"Findings: {result['finding_count']}")
    for f in result["findings"]:
        sev = f["severity"].upper()
        print(f"  [{sev}] {f['code']}: {f['title']}")
        if f.get("suggested_action"):
            print(f"    -> {f['suggested_action']}")

    return 0 if result["result"] != "BLOCKED" else 1


if __name__ == "__main__":
    sys.exit(main())
