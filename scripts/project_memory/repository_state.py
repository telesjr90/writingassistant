#!/usr/bin/env python3
"""Deterministic repository-state scanner for Project Memory.

Collects read-only Git repository state without mutation. Uses only Python
standard-library modules and read-only Git commands.

Usage:
  python3 scripts/project_memory/repository_state.py --repo-root .
  python3 scripts/project_memory/repository_state.py --repo-root . --json
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import warnings
from pathlib import Path
from typing import Any

_SCANNER_NAME = "repository_state"
_SCANNER_VERSION = "1.0.0"

_EXCLUDED_PATHS_PREFIXES = frozenset([
    ".git/",
    "__pycache__/",
    "node_modules/",
    ".venv",
    "venv",
    ".env",
    "*.pyc",
])

_EXCLUDED_DIRS = frozenset([
    ".git",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
])


def _run_git(args: list[str], repo_root: Path, timeout: int = 30) -> str:
    """Run a read-only git command and return stdout."""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(repo_root),
        )
        if result.returncode != 0:
            raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
        return result.stdout.rstrip("\n")
    except FileNotFoundError:
        raise RuntimeError("git command not found")


def _resolve_repo_root(requested: str) -> Path:
    """Resolve and validate a repository root path."""
    try:
        root = Path(requested).resolve(strict=True)
    except FileNotFoundError:
        raise ValueError(f"Path does not exist: {requested}")
    if not root.is_dir():
        raise ValueError(f"Not a directory: {root}")
    git_dir = root / ".git"
    if not git_dir.exists():
        raise ValueError(f"Not a Git repository (no .git): {root}")
    return root


def _is_path_safe(repo_root: Path, rel_path: str) -> bool:
    """Check that a repository-relative path does not escape the repo."""
    try:
        resolved = (repo_root / rel_path).resolve()
        return resolved.is_relative_to(repo_root)
    except (ValueError, OSError):
        return False


def _is_regular_file_safe(repo_root: Path, rel_path: str) -> bool:
    """Check that a path is a safe regular file inside the repo."""
    if not _is_path_safe(repo_root, rel_path):
        return False
    full = (repo_root / rel_path).resolve()
    try:
        return full.is_file() and not full.is_symlink()
    except OSError:
        return False


def _is_excluded_path(rel_path: str) -> bool:
    """Check if a path should be excluded from hashing."""
    parts = rel_path.replace("\\", "/").split("/")
    for part in parts:
        if part in _EXCLUDED_DIRS:
            return True
    if rel_path.startswith(".codex-context/") or rel_path == ".codex-context":
        return False
    if rel_path.startswith("ai_context/") or rel_path == "ai_context":
        return False
    if rel_path.startswith("graphify-out/") or rel_path == "graphify-out":
        return False
    if ".venv" in parts or "venv" in parts:
        return True
    return False


def _is_protected_path(rel_path: str) -> bool:
    """Check if a path is protected and should not be read."""
    if rel_path.startswith(".git/"):
        return True
    if rel_path.startswith("projects/") and "/omi/" in rel_path:
        return True
    return False


def hash_file(repo_root: Path, rel_path: str) -> dict[str, Any]:
    """Hash a regular file with SHA-256. Returns hash info or error info."""
    result: dict[str, Any] = {"path": rel_path, "algorithm": "sha256"}
    if not _is_path_safe(repo_root, rel_path):
        result["error"] = "path_unsafe"
        return result
    full = (repo_root / rel_path).resolve()
    try:
        if not full.is_file() or full.is_symlink():
            result["error"] = "not_a_regular_file"
            return result
    except OSError:
        result["error"] = "os_error"
        return result
    try:
        content = full.read_bytes()
    except Exception as exc:
        result["error"] = f"read_error: {exc}"
        return result
    sha = hashlib.sha256(content).hexdigest()
    result["sha256"] = sha
    result["byte_size"] = len(content)
    return result


def collect_repository_state(repo_root: str, generated_at: str | None = None) -> dict[str, Any]:
    """Collect deterministic repository state.

    Args:
        repo_root: Path to the repository root.
        generated_at: ISO 8601 timestamp (defaults to now if None).

    Returns:
        Dict with repository state information.
    """
    from datetime import datetime, timezone

    root = _resolve_repo_root(repo_root)
    if generated_at is None:
        generated_at = datetime.now(timezone.utc).isoformat()

    branch = _run_git(["rev-parse", "--abbrev-ref", "HEAD"], root)
    head_sha = _run_git(["rev-parse", "HEAD"], root)
    head_subject = _run_git(["log", "-1", "--format=%s", "HEAD"], root)

    staged_raw = _run_git(["diff", "--cached", "--stat"], root)
    staged = bool(staged_raw.strip())

    dirty_raw = _run_git(["diff", "--stat"], root)
    dirty = bool(dirty_raw.strip())

    modified_paths: list[str] = []
    if dirty:
        mod_files = _run_git(["diff", "--name-only"], root)
        modified_paths = sorted([p for p in mod_files.split("\n") if p.strip()])

    untracked_paths: list[str] = []
    untracked_raw = _run_git(["ls-files", "--others", "--exclude-standard"], root)
    untracked_paths = sorted([p for p in untracked_raw.split("\n") if p.strip()])

    tracked_raw = _run_git(["ls-files"], root)
    tracked_files = sorted([p for p in tracked_raw.split("\n") if p.strip()])

    worktrees_raw = _run_git(["worktree", "list", "--porcelain"], root)
    worktrees: list[dict[str, str]] = []
    current_wt: dict[str, str] = {}
    for line in worktrees_raw.split("\n"):
        if not line.strip():
            if current_wt:
                worktrees.append(current_wt)
                current_wt = {}
            continue
        if " " in line:
            key, value = line.split(" ", 1)
            current_wt[key] = value
        else:
            current_wt["_raw"] = line
    if current_wt:
        worktrees.append(current_wt)

    state: dict[str, Any] = {
        "scanner_name": _SCANNER_NAME,
        "scanner_version": _SCANNER_VERSION,
        "generated_at": generated_at,
        "repository_root": str(root),
        "branch": branch,
        "head_sha": head_sha,
        "head_subject": head_subject,
        "staged": staged,
        "staged_empty": not staged,
        "dirty": dirty,
        "clean": not dirty,
        "modified_paths": modified_paths,
        "untracked_paths": untracked_paths,
        "tracked_files": tracked_files,
        "tracked_file_count": len(tracked_files),
        "worktrees": worktrees,
        "worktree_count": len(worktrees),
    }

    return state


def collect_source_inventory(
    repo_root: str,
    registry_dir: str | None = None,
) -> dict[str, Any]:
    """Collect source inventory and hashes for tracked authoritative sources.

    Args:
        repo_root: Path to the repository root.
        registry_dir: Optional path to registries directory.

    Returns:
        Dict with source inventory and hashes.
    """
    root = _resolve_repo_root(repo_root)
    if registry_dir is None:
        registry_dir = str(root / "docs" / "project-memory" / "registries")

    inventory: dict[str, Any] = {
        "scanner_name": _SCANNER_NAME,
        "scanner_version": _SCANNER_VERSION,
        "registry_sources": [],
        "roadmap_sources": [],
        "scanner_implementation_sources": [],
        "source_hashes": {},
    }

    registry_path = Path(registry_dir)
    if registry_path.is_dir():
        for entry in sorted(registry_path.iterdir()):
            if entry.is_file() and entry.suffix == ".json":
                rel = str(entry.relative_to(root))
                info = hash_file(root, rel)
                inventory["registry_sources"].append(info)
                if "sha256" in info:
                    inventory["source_hashes"][rel] = info["sha256"]

    roadmap_files = [
        "docs/roadmap/roadmap_index.yaml",
        "docs/roadmap/implementation_status.md",
        "docs/roadmap/decision_log.md",
        "docs/roadmap/task_backlog.md",
        "docs/roadmap/phase_map.md",
        "docs/roadmap/open_questions.md",
        "docs/roadmap/risk_register.md",
        "docs/roadmap/roadmap_governance.md",
        "docs/roadmap/context_tool_policy.md",
        "docs/roadmap/context_execution_standard.md",
    ]
    for rp in sorted(roadmap_files):
        full = root / rp
        if full.is_file():
            info = hash_file(root, rp)
            inventory["roadmap_sources"].append(info)
            if "sha256" in info:
                inventory["source_hashes"][rp] = info["sha256"]

    scanner_files = [
        "scripts/project_memory/__init__.py",
        "scripts/project_memory/validate_registries.py",
        "scripts/project_memory/repository_state.py",
        "scripts/project_memory/convergence.py",
        "scripts/project_memory/build_snapshot.py",
    ]
    for sp in sorted(scanner_files):
        full = root / sp
        if full.is_file():
            info = hash_file(root, sp)
            inventory["scanner_implementation_sources"].append(info)
            if "sha256" in info:
                inventory["source_hashes"][sp] = info["sha256"]

    return inventory


def parse_roadmap_state(repo_root: str) -> dict[str, Any]:
    """Parse roadmap_index.yaml and return normalized roadmap state.

    Args:
        repo_root: Path to the repository root.

    Returns:
        Dict with parsed roadmap state.
    """
    root = _resolve_repo_root(repo_root)
    index_path = root / "docs" / "roadmap" / "roadmap_index.yaml"

    if not index_path.is_file():
        return {"error": "roadmap_index.yaml not found"}

    try:
        data = json.loads(index_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"error": f"invalid JSON in roadmap_index.yaml: {exc}"}

    result: dict[str, Any] = {
        "schema_version": data.get("schema_version"),
        "active_frontier": data.get("active_frontier", {}),
        "tasks": [],
        "task_index": {},
    }

    frontier = result["active_frontier"]
    if isinstance(frontier, dict):
        result["frontier_parent"] = frontier.get("current_parent_task_id")
        result["frontier_next_task"] = frontier.get("next_readiness_task_id")
        result["frontier_title"] = frontier.get("next_readiness_task_title")
        result["planned_parent"] = frontier.get("planned_architecture_parent_task_id")
        result["planned_parent_title"] = frontier.get("planned_architecture_parent_task_title")

    tasks = data.get("tasks", [])
    task_index: dict[str, dict] = {}
    for task in tasks:
        tid = task.get("id", "")
        if tid:
            task_index[tid] = {
                "id": tid,
                "title": task.get("title", ""),
                "type": task.get("type", ""),
                "status": task.get("status", ""),
                "parent": task.get("parent"),
                "depends_on": task.get("depends_on", []),
            }

    result["tasks"] = tasks
    result["task_index"] = task_index

    ph8_impl_026_tasks = {}
    for prefix in [
        "PHASE8-IMPL-026-T001",
        "PHASE8-IMPL-026-T002",
        "PHASE8-IMPL-026-T003",
        "PHASE8-IMPL-026-T003A",
        "PHASE8-IMPL-026-T003B",
    ]:
        for tid, info in task_index.items():
            if tid == prefix or tid.startswith(prefix + "-"):
                ph8_impl_026_tasks[prefix] = info
                break

    result["ph8_impl_026_tasks"] = ph8_impl_026_tasks
    result["ph8_impl_025_active"] = False
    result["frontier_is_ph8_impl_024_t003b"] = (
        result.get("frontier_next_task") == "PHASE8-IMPL-024-T003B"
    )

    return result


def validate_source_locators(
    repo_root: str,
    registry_dir: str | None = None,
) -> dict[str, Any]:
    """Validate source locators in tracked registries against the filesystem.

    Args:
        repo_root: Path to the repository root.
        registry_dir: Optional path to registries directory.

    Returns:
        Dict with locator validation results.
    """
    root = _resolve_repo_root(repo_root)
    if registry_dir is None:
        registry_dir = str(root / "docs" / "project-memory" / "registries")

    result: dict[str, Any] = {
        "valid_locators": [],
        "invalid_locators": [],
        "missing_sources": [],
        "excluded_sources": [],
        "total_locators": 0,
        "valid_count": 0,
        "invalid_count": 0,
        "missing_count": 0,
        "excluded_count": 0,
    }

    registry_path = Path(registry_dir)
    if not registry_path.is_dir():
        return result

    for entry in sorted(registry_path.iterdir()):
        if not entry.is_file() or entry.suffix != ".json":
            continue
        if entry.name == "manifest.json":
            continue
        try:
            data = json.loads(entry.read_text(encoding="utf-8"))
        except Exception:
            continue
        records = data.get("records", [])
        if not isinstance(records, list):
            continue
        for record in records:
            if not isinstance(record, dict):
                continue
            rid = record.get("id", "")
            ac = record.get("authority_class", "")
            provenance = record.get("provenance")
            if not isinstance(provenance, dict):
                continue
            locators = provenance.get("source_locators", [])
            if not isinstance(locators, list):
                continue
            for sl in locators:
                if not isinstance(sl, dict):
                    continue
                path_val = sl.get("path", "")
                if not path_val:
                    continue
                result["total_locators"] += 1
                loc_info = {
                    "path": path_val,
                    "record_id": rid,
                    "authority_class": ac,
                    "line_start": sl.get("line_start"),
                    "line_end": sl.get("line_end"),
                }

                if not _is_path_safe(root, path_val):
                    result["invalid_locators"].append({**loc_info, "reason": "path_unsafe"})
                    result["invalid_count"] += 1
                    continue

                if _is_protected_path(path_val):
                    result["excluded_sources"].append({**loc_info, "reason": "protected_path"})
                    result["excluded_count"] += 1
                    continue

                full = root / path_val
                if not full.exists():
                    result["missing_sources"].append({**loc_info, "reason": "not_found"})
                    result["missing_count"] += 1
                    continue

                if not full.is_file() or full.is_symlink():
                    result["invalid_locators"].append({**loc_info, "reason": "not_a_regular_file"})
                    result["invalid_count"] += 1
                    continue

                line_start = sl.get("line_start")
                line_end = sl.get("line_end")
                if line_start is not None or line_end is not None:
                    try:
                        lines = full.read_text(encoding="utf-8").split("\n")
                        line_count = len(lines)
                        if line_start is not None and line_start > line_count:
                            result["invalid_locators"].append({
                                **loc_info,
                                "reason": f"line_start {line_start} > {line_count}",
                            })
                            result["invalid_count"] += 1
                            continue
                        if line_end is not None and line_end > line_count:
                            result["invalid_locators"].append({
                                **loc_info,
                                "reason": f"line_end {line_end} > {line_count}",
                            })
                            result["invalid_count"] += 1
                            continue
                    except Exception:
                        pass

                result["valid_locators"].append(loc_info)
                result["valid_count"] += 1

    return result


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Collect deterministic repository state.")
    parser.add_argument("--repo-root", default=".", help="Path to repository root.")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON.")
    args = parser.parse_args()

    try:
        state = collect_repository_state(args.repo_root)
    except Exception as exc:
        if args.json:
            print(json.dumps({"error": str(exc)}, indent=2))
        else:
            print(f"ERROR: {exc}")
        return 1

    if args.json:
        print(json.dumps(state, indent=2, sort_keys=True))
        return 0

    print(f"Repository: {state['repository_root']}")
    print(f"Branch: {state['branch']}")
    print(f"HEAD: {state['head_sha']}")
    print(f"Subject: {state['head_subject']}")
    print(f"Staged: {state['staged']}")
    print(f"Clean: {state['clean']}")
    print(f"Dirty: {state['dirty']}")
    print(f"Tracked files: {state['tracked_file_count']}")
    print(f"Worktrees: {state['worktree_count']}")
    if state["modified_paths"]:
        print("Modified paths:")
        for p in state["modified_paths"]:
            print(f"  {p}")
    if state["untracked_paths"]:
        print("Untracked paths:")
        for p in state["untracked_paths"]:
            print(f"  {p}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
