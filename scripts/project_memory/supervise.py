#!/usr/bin/env python3
"""Deterministic application, closeout, and governance supervision handoff.

The supervisor reads tracked authority and existing generated evidence.  It
never accepts a command from repository content, never uses the network, and
never mutates roadmap, registry, application, candidate, or Memory/Canon state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.project_memory import execution_routing
from scripts.project_memory import operational_rollout
from scripts.project_memory import plan_integrity
from scripts.project_memory import repository_state
from scripts.project_memory import validate_registries


ROOT = Path(__file__).resolve().parents[2]
SCHEMA = "project-memory-supervision-handoff.v1"
EVIDENCE_SCHEMA = "project-memory-supervision-evidence.v1"
AUTHORITY_CLASS = "generated_evidence"
MODES = ("implementation", "closeout", "governance")
RESULTS = ("READY", "READY_WITH_ADVISORIES", "BLOCKED")
TASK_ID_PATTERN = re.compile(r"^PHASE[0-9]+-(?:IMPL|UX)-[0-9]{3}(?:-T[0-9]{3}[A-Z0-9]*)?$")
FULL_SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")
HANDOFF_FILES = (
    "project-memory-handoff.md",
    "project-memory-handoff.json",
    "SHA256SUMS",
)

APPLICATION_CATEGORIES = {"application_code", "application_test"}
CONTROL_PLANE_CATEGORIES = {
    "task_dependency_frontier_authority",
    "routing_control_plane",
    "project_memory_schema_registry",
    "project_memory_tooling_validator",
    "project_instructions_agent_guidance",
    "workflow_operational_policy",
    "authority_decision",
}
COMPLETE_STATUSES = {"complete", "done"}
ACTIVE_STATUSES = {"active", "in_progress", "planned", "published/active"}


class SupervisionError(RuntimeError):
    """Fail-closed supervision input or output error."""


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SupervisionError(f"Expected JSON object: {path.name}")
    return value


def _git(root: Path, *args: str, allow_failure: bool = False) -> str:
    result = subprocess.run(
        ["git", *args], cwd=root, text=True, capture_output=True, check=False
    )
    if result.returncode and not allow_failure:
        raise SupervisionError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.rstrip("\n") if result.returncode == 0 else ""


def _canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _finding(code: str, detail: str) -> dict[str, str]:
    return {"code": code, "detail": detail}


def _safe_relative(value: str) -> bool:
    path = PurePosixPath(value)
    return bool(value) and not path.is_absolute() and ".." not in path.parts and "\x00" not in value


def classify_path(path: str) -> str:
    """Classify one normalized tracked path, with control planes before apps."""
    if not _safe_relative(path) or path.startswith(".git/"):
        return "unrelated_or_unsafe"
    if path == "AGENTS.md" or path.startswith(".agents/skills/") or path.startswith(".opencode/agents/"):
        return "project_instructions_agent_guidance"
    if path.startswith(".github/workflows/"):
        return "workflow_operational_policy"
    if path == ".gitignore" or path in {
        "docs/project-memory/operations.json",
        "docs/project-memory/operator-manual.md",
        "docs/project-memory/chatgpt-github-supervision-policy.md",
    }:
        return "workflow_operational_policy"
    if path == "docs/project-memory/registries/execution-routing.json" or path == "scripts/project_memory/execution_routing.py":
        return "routing_control_plane"
    if path.startswith("docs/project-memory/schemas/") or path.startswith("docs/project-memory/registries/"):
        return "project_memory_schema_registry"
    if path.startswith("scripts/project_memory/") or path.startswith("tests/project_memory/"):
        return "project_memory_tooling_validator"
    if path.startswith("docs/roadmap/decisions/"):
        return "authority_decision"
    if (
        path == "docs/master_plan.md"
        or path == "docs/roadmap/roadmap_index.yaml"
        or path == "docs/roadmap/implementation_status.md"
        or path == "docs/roadmap/task_backlog.md"
        or path == "docs/roadmap/phase_map.md"
        or path.startswith("docs/roadmap/tasks/")
        or path.startswith("docs/roadmap/inventory/")
        or path.startswith("docs/roadmap/enrichment/")
    ):
        return "task_dependency_frontier_authority"
    if path.startswith("docs/project-memory/"):
        return "workflow_operational_policy"
    if path.startswith("frontend/tests/") or (path.startswith("tests/") and not path.startswith("tests/project_memory/")):
        return "application_test"
    if path.startswith("backend/") or path.startswith("frontend/"):
        return "application_code"
    return "unrelated_or_unsafe"


def classify_paths(paths: list[str]) -> list[dict[str, str]]:
    return [
        {"path": path, "category": classify_path(path)}
        for path in sorted(set(paths))
    ]


def _add_unique(items: list[dict[str, str]], code: str, detail: str) -> None:
    finding = _finding(code, detail)
    if finding not in items:
        items.append(finding)


def evaluate_gate(inputs: dict[str, Any]) -> dict[str, Any]:
    """Evaluate supplied deterministic facts without mutating them."""
    mode = inputs.get("mode")
    if mode not in MODES:
        raise SupervisionError(f"Unsupported mode: {mode!r}")
    repository = inputs.get("repository", {})
    task = inputs.get("task", {})
    routing = inputs.get("routing")
    blockers: list[dict[str, str]] = []
    advisories: list[dict[str, str]] = []

    if not repository.get("clean") or repository.get("staged"):
        _add_unique(blockers, "repository_not_clean", "A clean worktree and empty staging are required.")
    if repository.get("detached") and not repository.get("trusted_ci_detached"):
        _add_unique(blockers, "detached_head", "Detached local HEAD is not accepted.")
    if not task or not task.get("task_id"):
        _add_unique(blockers, "missing_or_ambiguous_task", "One authoritative task is required.")
    if not task.get("required_sources_present", False):
        _add_unique(blockers, "missing_required_task_sources", "A required authoritative task source is missing.")
    if inputs.get("routing_error"):
        detail = json.dumps(inputs["routing_error"], sort_keys=True)
        _add_unique(blockers, "routing_resolution_failed", detail)
    if not routing:
        _add_unique(blockers, "routing_resolution_failed", "No applicable routing record resolved.")
    elif routing.get("owner_only") or not routing.get("delegation_eligible"):
        _add_unique(blockers, "owner_only_or_nondelegable_task", "Owner-only, aggregate, or nondelegable routing cannot execute.")
    if inputs.get("conflicts"):
        _add_unique(blockers, "authoritative_conflict", json.dumps(inputs["conflicts"], sort_keys=True))
    if inputs.get("validators", {}).get("result") != "PASS":
        _add_unique(blockers, "required_validator_failure", "One or more deterministic validators failed.")
    plan = inputs.get("plan_integrity", {})
    if int(plan.get("blocking_count", 0)):
        _add_unique(blockers, "plan_integrity_blocker", f"Plan Integrity reports {plan.get('blocking_count')} blocker(s).")

    evidence = inputs.get("validation_evidence", {})
    evidence_status = evidence.get("status", "NOT_SUPPLIED")
    if evidence_status in {"BLOCKED", "FAIL"}:
        _add_unique(blockers, "task_validation_evidence_failed", "Supplied task-validation evidence failed closed.")

    changed = inputs.get("changed_paths", [])
    categories = {item.get("category") for item in changed}
    control = sorted(category for category in categories if category in CONTROL_PLANE_CATEGORIES)
    unsafe = sorted(item.get("path", "") for item in changed if item.get("category") == "unrelated_or_unsafe")
    if mode == "implementation" and control:
        _add_unique(
            blockers,
            "control_plane_changes_require_strict_gate",
            "Control-plane categories require closeout or governance: " + ", ".join(control),
        )
    if mode == "implementation" and unsafe:
        _add_unique(blockers, "unauthorized_changed_paths", ", ".join(unsafe))

    status = str(task.get("status", ""))
    dependencies = task.get("dependencies", [])
    if mode == "implementation":
        if status not in ACTIVE_STATUSES:
            _add_unique(blockers, "inactive_task", f"Task lifecycle is {status!r}.")
        incomplete = sorted(
            item.get("task_id", "")
            for item in dependencies
            if item.get("status") not in COMPLETE_STATUSES
        )
        if incomplete:
            _add_unique(blockers, "dependency_ineligible", ", ".join(incomplete))
        if not task.get("is_frontier"):
            _add_unique(blockers, "not_current_frontier", "Implementation task is not the sole current frontier.")
        if evidence_status == "NOT_SUPPLIED":
            _add_unique(advisories, "task_validation_evidence_not_supplied", "No bounded task-test evidence was supplied.")
    elif mode == "closeout":
        if status not in COMPLETE_STATUSES:
            _add_unique(blockers, "task_status_not_synchronized_for_closeout", "Closeout requires explicitly synchronized complete status.")
        if task.get("is_frontier"):
            _add_unique(blockers, "frontier_not_advanced_for_closeout", "Closeout requires an explicitly advanced authoritative frontier.")
        if evidence_status != "PASS":
            _add_unique(blockers, "task_validation_evidence_required", "Closeout requires passing bounded task-test evidence.")

    memory = inputs.get("memory", {})
    memory_status = memory.get("status", "STALE")
    freshness = "FRESH" if memory_status == "FRESH" and memory.get("package_commit") == repository.get("commit") else "STALE"
    if mode == "implementation" and freshness != "FRESH":
        allowed_reasons = {"commit_mismatch", "source_hash_drift", "accepted_application_commit_mismatch"}
        reasons = set(memory.get("reasons", []))
        application_only = bool(changed) and all(
            item.get("category") in APPLICATION_CATEGORIES for item in changed
        )
        advisory_eligible = (
            memory.get("baseline_is_ancestor") is True
            and memory.get("package_branch") == repository.get("branch")
            and bool(reasons)
            and reasons <= allowed_reasons
            and application_only
            and not control
            and not unsafe
            and not inputs.get("conflicts")
            and int(plan.get("blocking_count", 0)) == 0
        )
        if advisory_eligible:
            freshness = "STALE_ANCESTOR_APPLICATION_ONLY"
            _add_unique(
                advisories,
                "project_memory_commit_lag_application_only",
                "Project Memory is bound to an ancestor; only bounded application code/tests changed.",
            )
        else:
            _add_unique(blockers, "project_memory_staleness_not_application_only", ", ".join(sorted(reasons)) or "unbound")
    elif mode in {"closeout", "governance"} and freshness != "FRESH":
        _add_unique(blockers, "exact_commit_project_memory_required", "Strict supervision requires exact-commit FRESH Project Memory.")

    for code in sorted(set(plan.get("advisory_codes", []))):
        _add_unique(advisories, code, "Accepted nonblocking Plan Integrity advisory.")

    blockers.sort(key=lambda item: (item["code"], item["detail"]))
    advisories.sort(key=lambda item: (item["code"], item["detail"]))
    result = "BLOCKED" if blockers else ("READY_WITH_ADVISORIES" if advisories else "READY")
    if result == "BLOCKED":
        next_action = "Resolve every reported blocker; do not mutate task or frontier state through generated evidence."
    elif mode == "implementation":
        next_action = "Continue only bounded same-task implementation; task acceptance remains a separate explicit closeout action."
    elif mode == "closeout":
        next_action = "Present strict closeout evidence for owner/executor acceptance; this handoff does not accept the task."
    else:
        next_action = "Present strict governance evidence for acceptance; this handoff does not mutate authority."
    return {
        "result": result,
        "blockers": blockers,
        "advisories": advisories,
        "project_memory_freshness": freshness,
        "acceptance_claimed": False,
        "state_mutation_performed": False,
        "next_deterministic_action": next_action,
    }


def build_payload(inputs: dict[str, Any], gate: dict[str, Any]) -> dict[str, Any]:
    changed = inputs.get("changed_paths", [])
    categories: dict[str, int] = {}
    for item in changed:
        category = str(item.get("category"))
        categories[category] = categories.get(category, 0) + 1
    return {
        "schema": SCHEMA,
        "authority_class": AUTHORITY_CLASS,
        "mode": inputs["mode"],
        "result": gate["result"],
        "repository": inputs["repository"],
        "task": inputs["task"],
        "routing": inputs.get("routing"),
        "routing_error": inputs.get("routing_error"),
        "changed_path_classification": {
            "paths": changed,
            "counts": dict(sorted(categories.items())),
            "application_only": bool(changed) and all(item.get("category") in APPLICATION_CATEGORIES for item in changed),
            "control_plane_sensitive": any(item.get("category") in CONTROL_PLANE_CATEGORIES for item in changed),
        },
        "project_memory": {**inputs.get("memory", {}), "freshness_classification": gate["project_memory_freshness"]},
        "plan_integrity": inputs.get("plan_integrity", {}),
        "validator_evidence": inputs.get("validators", {}),
        "task_validation_evidence": inputs.get("validation_evidence", {}),
        "blockers": gate["blockers"],
        "advisories": gate["advisories"],
        "next_deterministic_action": gate["next_deterministic_action"],
        "acceptance_claimed": False,
        "authority_mutation_performed": False,
        "application_mutation_performed": False,
        "state_mutation_performed": False,
        "git_mutation_performed": False,
        "network_access_performed": False,
        "checksums": {"algorithm": "sha256", "manifest": "SHA256SUMS"},
    }


def _routing_text(routing: dict[str, Any] | None) -> str:
    if not routing:
        return "unresolved"
    locator = routing.get("authoritative_source_locator", {})
    return f"{routing.get('execution_class')} via {locator.get('path')}#symbol={locator.get('symbol')}"


def render_pr_comment(payload: dict[str, Any]) -> str:
    task = payload["task"]
    repo = payload["repository"]
    classification = payload["changed_path_classification"]
    blockers = ", ".join(item["code"] for item in payload["blockers"]) or "none"
    advisories = ", ".join(item["code"] for item in payload["advisories"]) or "none"
    value = "\n".join([
        "<!-- project-memory-supervision -->",
        "## Project Memory supervision",
        "",
        f"- Exact SHA: `{repo['commit']}`",
        f"- Task: `{task['task_id']}`",
        f"- Mode: `{payload['mode']}`",
        f"- Gate result: **{payload['result']}**",
        f"- Routing: `{_routing_text(payload.get('routing'))}`",
        f"- Changed paths: `{json.dumps(classification['counts'], sort_keys=True)}`",
        f"- Project Memory: `{payload['project_memory']['freshness_classification']}`",
        f"- Blockers: {blockers}",
        f"- Advisories: {advisories}",
        f"- Next action: {payload['next_deterministic_action']}",
        "",
        "Generated evidence only. This check does not accept a task or mutate roadmap state.",
    ]) + "\n"
    if len(value) >= 8000:
        raise SupervisionError("PR comment exceeds the 8,000-character bound")
    return value


def _render_markdown(payload: dict[str, Any]) -> str:
    comment = render_pr_comment(payload)
    paths = payload["changed_path_classification"]["paths"]
    path_lines = [f"- `{item['path']}` — `{item['category']}`" for item in paths] or ["- None"]
    return comment + "\n### Changed-path detail\n\n" + "\n".join(path_lines) + "\n"


def _write_text(path: Path, value: str) -> None:
    path.write_text(value, encoding="utf-8", newline="\n")


def _reject_symlink_components(root: Path, target: Path) -> None:
    try:
        relative = target.relative_to(root)
    except ValueError as exc:
        raise SupervisionError("Handoff output must remain inside the repository") from exc
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise SupervisionError(f"Handoff output has a symlink component: {part}")


def verify_handoff_package(package_dir: str | Path) -> dict[str, Any]:
    package = Path(package_dir)
    errors: list[str] = []
    if package.is_symlink() or not package.is_dir():
        return {"result": "BLOCKED", "errors": ["package is missing or symlinked"]}
    actual = sorted(path.name for path in package.iterdir())
    if actual != sorted(HANDOFF_FILES):
        errors.append("inventory mismatch")
    checksums = package / "SHA256SUMS"
    if checksums.is_file() and not checksums.is_symlink():
        expected: dict[str, str] = {}
        for line in checksums.read_text(encoding="utf-8").splitlines():
            parts = line.split("  ", 1)
            if len(parts) != 2 or not re.fullmatch(r"[0-9a-f]{64}", parts[0]) or parts[1] not in HANDOFF_FILES[:2]:
                errors.append("malformed checksum manifest")
                continue
            expected[parts[1]] = parts[0]
        if sorted(expected) != sorted(HANDOFF_FILES[:2]):
            errors.append("checksum coverage mismatch")
        for name, digest in expected.items():
            path = package / name
            if not path.is_file() or path.is_symlink() or _sha256(path) != digest:
                errors.append(f"checksum mismatch: {name}")
    else:
        errors.append("missing checksum manifest")
    try:
        payload = _load_json(package / "project-memory-handoff.json")
        if payload.get("schema") != SCHEMA or payload.get("authority_class") != AUTHORITY_CLASS:
            errors.append("handoff schema or authority mismatch")
        if payload.get("result") not in RESULTS:
            errors.append("invalid handoff result")
    except (OSError, UnicodeError, json.JSONDecodeError, SupervisionError) as exc:
        errors.append(f"malformed handoff JSON: {exc}")
    return {"result": "PASS" if not errors else "BLOCKED", "errors": sorted(set(errors))}


def write_handoff_package(repo_root: str | Path, payload: dict[str, Any]) -> Path:
    root = Path(repo_root).resolve(strict=True)
    task_id = str(payload.get("task", {}).get("task_id", ""))
    commit = str(payload.get("repository", {}).get("commit", ""))
    mode = str(payload.get("mode", ""))
    if not TASK_ID_PATTERN.fullmatch(task_id) or not FULL_SHA_PATTERN.fullmatch(commit) or mode not in MODES:
        raise SupervisionError("Unsafe task, commit, or mode in handoff path")
    base = root / ".codex-context/project-memory/handoff"
    final = base / task_id / commit / mode
    _reject_symlink_components(root, final)
    final.parent.mkdir(parents=True, exist_ok=True)
    _reject_symlink_components(root, final.parent)
    temporary = Path(tempfile.mkdtemp(prefix=".handoff-", dir=final.parent))
    try:
        markdown = _render_markdown(payload)
        json_text = _canonical_json(payload)
        _write_text(temporary / HANDOFF_FILES[0], markdown)
        _write_text(temporary / HANDOFF_FILES[1], json_text)
        manifest = "\n".join(
            f"{_sha256(temporary / name)}  {name}" for name in HANDOFF_FILES[:2]
        ) + "\n"
        _write_text(temporary / HANDOFF_FILES[2], manifest)
        verification = verify_handoff_package(temporary)
        if verification["result"] != "PASS":
            raise SupervisionError("Handoff verification failed: " + "; ".join(verification["errors"]))
        if final.exists():
            if final.is_symlink() or not final.is_dir():
                raise SupervisionError("Existing handoff target is unsafe")
            same = all(
                (final / name).is_file()
                and not (final / name).is_symlink()
                and (final / name).read_bytes() == (temporary / name).read_bytes()
                for name in HANDOFF_FILES
            )
            if not same:
                raise SupervisionError("A different handoff already exists for this exact task/SHA/mode")
            return final
        os.rename(temporary, final)
        return final
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)


def validate_evidence(path: Path | None, root: Path, task_id: str, commit: str) -> dict[str, Any]:
    if path is None:
        return {"status": "NOT_SUPPLIED", "checks": []}
    try:
        candidate = path if path.is_absolute() else root / path
        _reject_symlink_components(root, candidate)
        candidate = candidate.resolve(strict=True)
        candidate.relative_to(root)
        if candidate.is_symlink() or not candidate.is_file() or candidate.stat().st_size > 1_000_000:
            raise SupervisionError("Evidence must be one bounded regular file")
        value = _load_json(candidate)
        if value.get("schema") != EVIDENCE_SCHEMA:
            raise SupervisionError("Unsupported evidence schema")
        if value.get("task_id") != task_id or value.get("commit") != commit:
            raise SupervisionError("Evidence task or commit binding mismatch")
        checks = value.get("checks")
        if not isinstance(checks, list) or any(
            not isinstance(item, dict)
            or not isinstance(item.get("name"), str)
            or item.get("result") not in {"PASS", "FAIL"}
            for item in checks
        ):
            raise SupervisionError("Malformed evidence checks")
        sanitized = [
            {"name": item["name"][:160], "result": item["result"]}
            for item in sorted(checks, key=lambda item: item["name"])
        ]
        return {"status": "FAIL" if any(item["result"] == "FAIL" for item in sanitized) else "PASS", "checks": sanitized}
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError, SupervisionError) as exc:
        return {"status": "BLOCKED", "checks": [], "error": str(exc)}


def _repo_state(root: Path) -> dict[str, Any]:
    top = Path(_git(root, "rev-parse", "--show-toplevel")).resolve()
    if top != root:
        raise SupervisionError(f"Repository identity mismatch: {top}")
    actual_branch = _git(root, "branch", "--show-current")
    detached = not bool(actual_branch)
    trusted_ci = os.environ.get("GITHUB_ACTIONS") == "true"
    branch = actual_branch or (os.environ.get("GITHUB_HEAD_REF") if trusted_ci else "") or (os.environ.get("GITHUB_REF_NAME") if trusted_ci else "")
    commit = _git(root, "rev-parse", "HEAD")
    porcelain = _git(root, "status", "--porcelain=v1")
    staged = bool(_git(root, "diff", "--cached", "--name-only"))
    remote_sha = _git(root, "rev-parse", "@{upstream}", allow_failure=True) or None
    ahead = behind = None
    if remote_sha:
        counts = _git(root, "rev-list", "--left-right", "--count", "HEAD...@{upstream}")
        values = counts.split()
        if len(values) == 2:
            ahead, behind = int(values[0]), int(values[1])
    return {
        "name": root.name,
        "branch": branch,
        "commit": commit,
        "clean": not bool(porcelain),
        "staged": staged,
        "detached": detached,
        "trusted_ci_detached": detached and trusted_ci and bool(branch),
        "remote_sha": remote_sha,
        "ahead": ahead,
        "behind": behind,
    }


def _records(path: Path) -> list[dict[str, Any]]:
    value = _load_json(path).get("records", [])
    if not isinstance(value, list):
        raise SupervisionError(f"Malformed registry records: {path.name}")
    return [item for item in value if isinstance(item, dict)]


def _task_inputs(root: Path, roadmap: dict[str, Any], task_id: str, mode: str) -> tuple[dict[str, Any], list[dict[str, str]]]:
    roadmap_matches = [item for item in roadmap.get("tasks", []) if isinstance(item, dict) and item.get("id") == task_id]
    registry_matches = [item for item in _records(root / "docs/project-memory/registries/tasks.json") if item.get("task_id") == task_id]
    if len(registry_matches) != 1 or (mode != "governance" and len(roadmap_matches) != 1) or len(roadmap_matches) > 1:
        raise SupervisionError(f"Task {task_id} is missing or ambiguous")
    registry_task = registry_matches[0]
    roadmap_task = roadmap_matches[0] if roadmap_matches else {
        "id": task_id,
        "status": registry_task.get("lifecycle", {}).get("status"),
    }
    by_id = {
        item.get("task_id"): item
        for item in _records(root / "docs/project-memory/registries/tasks.json")
        if isinstance(item.get("task_id"), str)
    }
    dependencies = []
    for dependency_id in registry_task.get("depends_on", roadmap_task.get("depends_on", [])):
        dependencies.append({
            "task_id": dependency_id,
            "status": by_id.get(dependency_id, {}).get("lifecycle", {}).get("status", "missing"),
        })
    frontier = roadmap.get("active_frontier", {}).get("next_readiness_task_id")
    sources = registry_task.get("provenance", {}).get("source_locators", [])
    required_present = bool(sources) and all(
        isinstance(item, dict)
        and isinstance(item.get("path"), str)
        and _safe_relative(item["path"])
        and (root / item["path"]).is_file()
        for item in sources
    )
    conflicts: list[dict[str, str]] = []
    declared_frontier = registry_task.get("is_application_frontier")
    if mode != "governance" and isinstance(declared_frontier, bool) and declared_frontier != (frontier == task_id):
        conflicts.append({"code": "task_frontier_disagreement", "detail": task_id})
    return ({
        "task_id": task_id,
        "status": registry_task.get("lifecycle", {}).get("status"),
        "roadmap_status": roadmap_task.get("status"),
        "frontier": frontier,
        "is_frontier": frontier == task_id,
        "dependencies": dependencies,
        "required_sources_present": required_present,
        "application_task": mode != "governance",
    }, conflicts)


VALIDATOR_COMMANDS = {
    "current_truth": ("python3", "scripts/project_memory/validate_current_truth.py"),
    "registries": ("python3", "scripts/project_memory/validate_registries.py", "--json"),
    "agent_guidance": ("python3", "scripts/project_memory/validate_agent_guidance.py", "--json"),
    "reviewer_guidance": ("python3", "scripts/project_memory/validate_reviewer_guidance.py", "--json"),
    "operational_rollout": ("python3", "scripts/project_memory/validate_operational_rollout.py", "--json"),
    "routing": ("python3", "scripts/project_memory/execution_routing.py", "validate", "--repo-root", "."),
    "enrichment": ("python3", "scripts/check_enrichment.py"),
    "roadmap": ("python3", "scripts/validate_roadmap.py"),
}


def _run_validators(root: Path, mode: str) -> dict[str, Any]:
    names = ["current_truth", "routing"] if mode == "implementation" else list(VALIDATOR_COMMANDS)
    checks = []
    for name in names:
        result = subprocess.run(
            VALIDATOR_COMMANDS[name], cwd=root, text=True, capture_output=True, check=False
        )
        checks.append({"name": name, "result": "PASS" if result.returncode == 0 else "FAIL"})
    return {
        "result": "PASS" if all(item["result"] == "PASS" for item in checks) else "BLOCKED",
        "checks": checks,
    }


def _portable_package_path(root: Path, value: str | None) -> str | None:
    if not value:
        return None
    try:
        return Path(value).resolve().relative_to(root).as_posix()
    except ValueError:
        return "external_generated_evidence"


def _live_plan_integrity(root: Path, branch: str, commit: str) -> dict[str, Any]:
    try:
        plan_inputs = plan_integrity.load_plan_inputs(root)
        state = repository_state.collect_repository_state(str(root))
        state["branch"] = branch
        state["head_sha"] = commit
        registry_findings = validate_registries.validate(
            root / "docs/project-memory/registries",
            root / "docs/roadmap/roadmap_index.yaml",
        )
        implementation = plan_integrity.load_implementation_inputs(
            root,
            plan_inputs=plan_inputs,
            expected_branch=branch,
            expected_commit=commit,
            repository_state_override=state,
            registry_findings=registry_findings,
        )
        comparisons = plan_integrity.build_comparisons(plan_inputs, implementation)
        report = plan_integrity.run_plan_integrity_checks(plan_inputs, implementation, comparisons)
        readiness = plan_integrity.derive_readiness(report["findings"])
        return {
            "blocking_count": readiness["blocking_count"],
            "advisory_count": readiness["advisory_count"],
            "advisory_codes": sorted({
                item["code"] for item in report["findings"] if not item["blocking"]
            }),
        }
    except Exception:
        return {
            "blocking_count": 1,
            "advisory_count": 0,
            "advisory_codes": [],
            "evaluation_error": True,
        }


def collect_inputs(
    *,
    repo_root: str | Path,
    mode: str,
    task_id: str | None,
    evidence_path: Path | None = None,
) -> dict[str, Any]:
    root = Path(repo_root).resolve(strict=True)
    state = _repo_state(root)
    if not FULL_SHA_PATTERN.fullmatch(state["commit"]):
        raise SupervisionError("HEAD is not a full Git SHA")
    roadmap = _load_json(root / "docs/roadmap/roadmap_index.yaml")
    resolved_task_id = task_id or (
        "PHASE8-IMPL-026-T011" if mode == "governance"
        else roadmap.get("active_frontier", {}).get("next_readiness_task_id")
    )
    if not isinstance(resolved_task_id, str) or not TASK_ID_PATTERN.fullmatch(resolved_task_id):
        raise SupervisionError("Task ID is missing, ambiguous, or malformed")
    task, conflicts = _task_inputs(root, roadmap, resolved_task_id, mode)
    policy = _load_json(root / "docs/project-memory/operations.json")
    routing_error = None
    routing: dict[str, Any] | None
    if mode == "governance":
        route = policy.get("supervision", {}).get("governance_maintenance_route")
        routing = dict(route) if isinstance(route, dict) else None
        if routing:
            routing["task_id"] = resolved_task_id
        else:
            routing_error = {"classification": "missing_governance_maintenance_route"}
    else:
        try:
            routing = execution_routing.resolve_execution_route(
                resolved_task_id,
                repo_root=root,
                current_branch=state["branch"],
                require_eligible=mode == "implementation",
            )
        except execution_routing.RoutingResolutionError as exc:
            routing = None
            routing_error = exc.finding
    status = operational_rollout.check_status(
        repo_root=root,
        expected_branch=state["branch"],
        expected_commit=state["commit"],
        output_root=root / ".codex-context/project-memory",
        task_id=operational_rollout.DEFAULT_TASK_ID,
        allow_detached=state["trusted_ci_detached"],
    )
    packages = status.get("packages", {})
    report_dir = Path(packages["report"]) if packages.get("report") else None
    package_commit = package_branch = None
    plan = _live_plan_integrity(root, state["branch"], state["commit"])
    if report_dir and report_dir.is_dir():
        try:
            metadata = _load_json(report_dir / "run-metadata.json")
            readiness = _load_json(report_dir / "readiness.json")
            findings = _load_json(report_dir / "findings.json")
            package_commit = metadata.get("bound_commit")
            package_branch = metadata.get("branch")
            items = findings.get("findings", [])
            package_plan = {
                "blocking_count": readiness.get("blocking_count", 0),
                "advisory_count": readiness.get("advisory_count", 0),
                "advisory_codes": sorted({
                    item.get("code") for item in items
                    if isinstance(item, dict) and not item.get("blocking") and isinstance(item.get("code"), str)
                }),
            }
            if package_plan["blocking_count"] > plan["blocking_count"]:
                plan = package_plan
        except (OSError, UnicodeError, json.JSONDecodeError, SupervisionError):
            status.setdefault("reasons", []).append("malformed_metadata")
    trusted_baseline = os.environ.get("PROJECT_MEMORY_BASELINE_SHA") if os.environ.get("GITHUB_ACTIONS") == "true" else None
    if package_commit is None and isinstance(trusted_baseline, str) and FULL_SHA_PATTERN.fullmatch(trusted_baseline):
        package_commit = trusted_baseline
        package_branch = state["branch"]
        status["result"] = "STALE"
        status["reasons"] = ["commit_mismatch"]
    baseline_is_ancestor = False
    changed_paths: list[str] = []
    if isinstance(package_commit, str) and FULL_SHA_PATTERN.fullmatch(package_commit):
        baseline_is_ancestor = subprocess.run(
            ["git", "merge-base", "--is-ancestor", package_commit, state["commit"]],
            cwd=root, capture_output=True, check=False,
        ).returncode == 0
        if baseline_is_ancestor:
            changed_paths = _git(root, "diff", "--name-only", f"{package_commit}..{state['commit']}").splitlines()
    memory = {
        "status": status.get("result", "STALE"),
        "package_commit": package_commit,
        "package_branch": package_branch,
        "reasons": sorted(set(status.get("reasons", []))),
        "baseline_is_ancestor": baseline_is_ancestor,
        "packages": {name: _portable_package_path(root, value) for name, value in sorted(packages.items())},
    }
    return {
        "mode": mode,
        "repository": state,
        "task": task,
        "routing": routing,
        "routing_error": routing_error,
        "changed_paths": classify_paths(changed_paths),
        "memory": memory,
        "plan_integrity": plan,
        "validation_evidence": validate_evidence(evidence_path, root, resolved_task_id, state["commit"]),
        "validators": _run_validators(root, mode),
        "conflicts": conflicts,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=MODES, required=True)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--task-id")
    parser.add_argument("--evidence-json", type=Path)
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        inputs = collect_inputs(
            repo_root=args.repo_root,
            mode=args.mode,
            task_id=args.task_id,
            evidence_path=args.evidence_json,
        )
        gate = evaluate_gate(inputs)
        payload = build_payload(inputs, gate)
        package = write_handoff_package(args.repo_root, payload)
        markdown = package / HANDOFF_FILES[0]
        json_path = package / HANDOFF_FILES[1]
        sums = package / HANDOFF_FILES[2]
        print(f"HANDOFF_MARKDOWN={markdown}")
        print(f"HANDOFF_JSON={json_path}")
        print(f"HANDOFF_CHECKSUMS={sums}")
        print(f"RESULT={gate['result']}")
        if args.json:
            print(_canonical_json({
                "result": gate["result"],
                "markdown": str(markdown),
                "json": str(json_path),
                "checksums": str(sums),
            }), end="")
        return 1 if gate["result"] == "BLOCKED" else 0
    except Exception as exc:
        print(f"RESULT=BLOCKED\nERROR={exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
