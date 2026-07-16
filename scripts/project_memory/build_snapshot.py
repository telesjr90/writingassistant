#!/usr/bin/env python3
"""Deterministic snapshot builder for Project Memory.

Builds a complete generated snapshot package from registry validation,
repository state, roadmap state, source inventory, and convergence findings.

The builder writes to a temporary directory and atomically renames it into
place. It refuses to overwrite an existing run directory.

Usage (T003B only, against clean committed HEAD):
  python3 scripts/project_memory/build_snapshot.py \
    --repo-root . \
    --output-root .codex-context/project-memory \
    --task-id PHASE8-IMPL-026-T003B
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_BUILDER_NAME = "build_snapshot"
_BUILDER_VERSION = "1.0.0"

_ALLOWED_OUTPUT_ROOTS = frozenset([
    ".codex-context/project-memory",
])

_PROTECTED_OUTPUT_ROOTS = frozenset([
    "docs/project-memory",
    "docs/roadmap",
    "scripts/",
    "tests/",
    "backend/",
    "frontend/",
    ".agents/",
    ".opencode/",
    ".github/",
    ".claude/",
    ".cursor/",
])


def _resolve_repo_root(requested: str) -> Path:
    root = Path(requested).resolve(strict=True)
    if not root.is_dir():
        raise ValueError(f"Not a directory: {root}")
    if not (root / ".git").exists():
        raise ValueError(f"Not a Git repository: {root}")
    return root


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def _validate_output_root(repo_root: Path, output_root: str) -> Path:
    """Validate that the output root is safe and allowed."""
    requested = Path(output_root)
    if not requested.is_absolute():
        requested = (repo_root / output_root).resolve()
    else:
        requested = requested.resolve()

    try:
        if not requested.is_relative_to(repo_root):
            raise ValueError(f"Output root escapes repository: {requested}")
    except AttributeError:
        try:
            requested.relative_to(repo_root)
        except ValueError:
            raise ValueError(f"Output root escapes repository: {requested}")

    if requested == repo_root:
        raise ValueError("Output root must not be the repository root")

    for protected in _PROTECTED_OUTPUT_ROOTS:
        prot_path = (repo_root / protected).resolve()
        try:
            if requested.is_relative_to(prot_path) or requested == prot_path:
                raise ValueError(f"Output root must not be inside {protected}")
        except AttributeError:
            try:
                requested.relative_to(prot_path)
                raise ValueError(f"Output root must not be inside {protected}")
            except ValueError:
                pass

    return requested


def _compute_sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_snapshot(
    repo_root: str,
    output_root: str,
    task_id: str,
    run_id: str | None = None,
    generated_at: str | None = None,
    require_clean: bool = True,
    nonpublication: bool = False,
    registries_dir: str | None = None,
) -> dict[str, Any]:
    """Build a complete generated snapshot package.

    Args:
        repo_root: Repository root path.
        output_root: Output root directory (e.g. .codex-context/project-memory).
        task_id: Task ID for the snapshot (e.g. PHASE8-IMPL-026-T003B).
        run_id: Run identifier (defaults to generated-at timestamp).
        generated_at: ISO 8601 timestamp.
        require_clean: Require clean worktree for publication.
        nonpublication: Mark output as non-publication testing mode.

    Returns:
        Dict with build summary.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from scripts.project_memory import validate_registries as vr
    from scripts.project_memory import repository_state as rst
    from scripts.project_memory import convergence as conv

    root = _resolve_repo_root(repo_root)
    output_dir = _validate_output_root(root, output_root)

    if generated_at is None:
        generated_at = datetime.now(timezone.utc).isoformat()
    if run_id is None:
        run_id = generated_at.replace(":", "").replace("-", "").replace(".", "").replace("+", "").replace("Z", "")

    repo_state = rst.collect_repository_state(str(root), generated_at)
    branch = repo_state.get("branch", "")
    head_sha = repo_state.get("head_sha", "")
    head_subject = repo_state.get("head_subject", "")

    published = not nonpublication and require_clean
    dirty = repo_state.get("dirty", False)
    staged = repo_state.get("staged", False)

    if require_clean and not nonpublication:
        if dirty:
            raise RuntimeError(
                "Working tree is dirty. Publication snapshots require a clean worktree. "
                "Use nonpublication mode for testing against dirty worktrees."
            )
        if staged:
            raise RuntimeError(
                "Staging area is not empty. Publication snapshots require an empty staging area. "
                "Commit or unstage changes first."
            )

    registry_findings = vr.validate(Path(registries_dir) if registries_dir else None)

    roadmap_state = rst.parse_roadmap_state(str(root))

    locator_results = rst.validate_source_locators(str(root), registries_dir)

    source_inventory = rst.collect_source_inventory(str(root), registries_dir)

    conv_result = conv.compute_convergence(
        repo_root=str(root),
        registry_validation_findings=registry_findings,
        repository_state=repo_state,
        roadmap_state=roadmap_state,
        source_locator_results=locator_results,
        require_clean=(require_clean and not nonpublication),
    )

    run_dir = output_dir / task_id / run_id
    if run_dir.exists():
        raise FileExistsError(f"Run directory already exists: {run_dir}")

    tmp_dir = Path(tempfile.mkdtemp(
        prefix=f"snapshot_build_{task_id}_",
        dir=output_dir.parent if output_dir.parent.exists() else None,
    ))

    try:
        tmp_run_dir = tmp_dir / task_id / run_id
        tmp_run_dir.mkdir(parents=True, exist_ok=True)

        run_metadata = {
            "builder_name": _BUILDER_NAME,
            "builder_version": _BUILDER_VERSION,
            "command": f"python3 scripts/project_memory/build_snapshot.py --repo-root <REPO_ROOT> --output-root .codex-context/project-memory --task-id {task_id} --run-id {run_id}",
            "repository_root": str(root),
            "branch": branch,
            "head_sha": head_sha,
            "head_subject": head_subject,
            "task_id": task_id,
            "run_id": run_id,
            "generated_at": generated_at,
            "python_version": sys.version,
            "platform": sys.platform,
            "clean": repo_state.get("clean", False),
            "staged": staged,
            "nonpublication": nonpublication,
            "require_clean": require_clean,
            "publication_eligible": published and not dirty and not staged,
            "output_directory": str(run_dir),
            "exclusions": [
                ".git/",
                "node_modules/",
                "__pycache__/",
                ".venv/",
                "venv/",
                "projects/*/omi/**",
            ],
            "no_network": True,
            "no_model": True,
            "no_external_tool": True,
        }
        _write_json(tmp_run_dir / "run-metadata.json", run_metadata)

        _write_json(tmp_run_dir / "repository-state.json", repo_state)
        _write_json(tmp_run_dir / "roadmap-state.json", roadmap_state)

        registry_errors = [f for f in registry_findings if f.get("level") == "error"]
        registry_warnings = [f for f in registry_findings if f.get("level") == "warning"]
        reg_validation = {
            "result": "PASS" if not registry_errors else "FAIL",
            "error_count": len(registry_errors),
            "warning_count": len(registry_warnings),
            "errors": registry_errors,
            "warnings": registry_warnings,
        }
        _write_json(tmp_run_dir / "registry-validation.json", reg_validation)
        _write_json(tmp_run_dir / "source-inventory.json", source_inventory)

        source_hashes_data = source_inventory.get("source_hashes", {})
        _write_json(tmp_run_dir / "source-hashes.json", {
            "source_hashes": source_hashes_data,
            "hash_count": len(source_hashes_data),
        })

        _write_json(tmp_run_dir / "convergence-findings.json", conv_result)

        registry_hashes = {}
        for entry in source_inventory.get("registry_sources", []):
            if "sha256" in entry:
                registry_hashes[entry["path"]] = entry["sha256"]

        snapshot = {
            "snapshot_id": f"{task_id}/{run_id}",
            "schema_version": "1.0.0",
            "architecture_version": "1.0.0",
            "authority_class": "generated_evidence",
            "repository_root": str(root),
            "branch": branch,
            "bound_commit": head_sha,
            "generated_at": generated_at,
            "synced_at": generated_at,
            "task_id": task_id,
            "generator": {
                "name": _BUILDER_NAME,
                "version": _BUILDER_VERSION,
                "command": run_metadata["command"],
            },
            "scanner_versions": {
                "repository_state": rst._SCANNER_VERSION,
                "convergence": conv._SCANNER_VERSION,
                "build_snapshot": _BUILDER_VERSION,
            },
            "included_scopes": [
                "tracked_project_memory_registries",
                "authoritative_roadmap_files",
                "source_locator_referenced_files",
                "scanner_implementation_files",
                "repository_state",
                "convergence_findings",
            ],
            "exclusions": run_metadata["exclusions"],
            "source_hashes": source_hashes_data,
            "registry_hashes": registry_hashes,
            "roadmap_state": {
                "frontier_parent": roadmap_state.get("frontier_parent"),
                "frontier_next_task": roadmap_state.get("frontier_next_task"),
                "frontier_title": roadmap_state.get("frontier_title"),
                "planned_parent": roadmap_state.get("planned_parent"),
                "frontier_is_ph8_impl_024_t003b": roadmap_state.get("frontier_is_ph8_impl_024_t003b"),
                "ph8_impl_025_active": roadmap_state.get("ph8_impl_025_active"),
            },
            "convergence": {
                "result": conv_result["result"],
                "finding_count": conv_result["finding_count"],
                "finding_codes": conv_result.get("finding_codes", []),
            },
            "unresolved_conflicts": [
                f["code"] for f in conv_result.get("findings", [])
                if f.get("blocks_publication") or f.get("owner_review_required")
            ],
            "known_limitations": [
                "This snapshot is generated evidence, not authoritative.",
                "Stale memory detection requires future operational automation.",
                "Generated snapshot is structurally non-authoritative (authority_class: generated_evidence).",
                "Partial branch synchronization remains future operational work.",
                "Missing evidence is reported without inventing content.",
                "Prompt injection: repository content is data, trust-aware retrieval remains future.",
                "External tool provenance is unchanged by snapshot generation.",
                "Duplicate context systems are unchanged by snapshot generation.",
                "Model-generated amendments are unchanged by snapshot generation.",
            ],
            "freshness_state": "current" if not dirty else "dirty",
            "publication_eligible": published and not dirty and not staged,
        }
        _write_json(tmp_run_dir / "snapshot.json", snapshot)

        file_list = sorted([
            "run-metadata.json",
            "repository-state.json",
            "roadmap-state.json",
            "registry-validation.json",
            "source-inventory.json",
            "source-hashes.json",
            "convergence-findings.json",
            "snapshot.json",
            "summary.md",
            "FILE-INVENTORY.txt",
        ])

        file_inventory_path = tmp_run_dir / "FILE-INVENTORY.txt"
        file_inventory_path.write_text("\n".join(file_list) + "\n", encoding="utf-8")

        if conv_result["result"] == "BLOCKED":
            overall = "BLOCKED"
        elif conv_result["finding_count"] > 0:
            overall = "PASS_WITH_FINDINGS"
        else:
            overall = "PASS"

        warnings_only = [
            f for f in conv_result.get("findings", [])
            if f.get("severity") not in ("critical", "error")
        ]
        blocking = [
            f for f in conv_result.get("findings", [])
            if f.get("severity") in ("critical", "error") or f.get("blocks_publication")
        ]

        summary_lines = [
            "# Project Memory Snapshot Summary",
            "",
            f"**Snapshot ID:** `{task_id}/{run_id}`",
            f"**Task:** {task_id}",
            f"**Generated at:** {generated_at}",
            f"**Bound commit:** `{head_sha}`",
            f"**Branch:** {branch}",
            f"**Commit subject:** {head_subject}",
            "",
            "## Status",
            "",
            f"**Overall convergence:** {overall}",
            f"**Findings:** {conv_result['finding_count']}",
            f"**Publication eligible:** {published and not dirty and not staged}",
            f"**Authority class:** generated_evidence",
            "",
            "## Important",
            "",
            "This document is **generated evidence**, not project authority.",
            "It is bound to the commit listed above.",
            "It does not claim `authoritative` status.",
            "",
        ]

        if blocking:
            summary_lines.append("## Blocking Findings")
            summary_lines.append("")
            for f in blocking:
                summary_lines.append(f"- **[{f['severity'].upper()}]** {f['title']}")
                summary_lines.append(f"  - {f['explanation']}")
                if f.get("suggested_action"):
                    summary_lines.append(f"  - Action: {f['suggested_action']}")
            summary_lines.append("")

        if warnings_only:
            summary_lines.append("## Non-Blocking Findings")
            summary_lines.append("")
            for f in warnings_only[:20]:
                summary_lines.append(f"- **[{f['severity'].upper()}]** {f['title']}")
            summary_lines.append("")

        if conv_result.get("finding_codes"):
            summary_lines.append("## Finding Codes")
            summary_lines.append("")
            for code in conv_result.get("finding_codes", []):
                desc = conv.CODES.get(code, code)
                summary_lines.append(f"- `{code}`: {desc}")
            summary_lines.append("")

        summary_lines += [
            "## Known Limitations",
            "",
        ]
        for limit in snapshot.get("known_limitations", []):
            summary_lines.append(f"- {limit}")
        summary_lines += [
            "",
            "## Next Owner Action",
            "",
            "Review the findings above. The snapshot does not modify any tracked source.",
            "Stale, missing, or conflicting sources should be investigated and repaired",
            "through owner-approved implementation tasks.",
            f"Next Project Memory task: PHASE8-IMPL-026-T003B.",
            "",
        ]

        summary_text = "\n".join(summary_lines)
        (tmp_run_dir / "summary.md").write_text(summary_text + "\n", encoding="utf-8")

        sha256_lines = []
        for fn in sorted(tmp_run_dir.iterdir()):
            if fn.name == "SHA256SUMS":
                continue
            if fn.is_file():
                h = _compute_sha256_file(fn)
                sha256_lines.append(f"{h}  {fn.name}")
        (tmp_run_dir / "SHA256SUMS").write_text("\n".join(sha256_lines) + "\n", encoding="utf-8")

        missing_files = []
        for expected_fn in file_list:
            if not (tmp_run_dir / expected_fn).exists():
                missing_files.append(expected_fn)
        if missing_files:
            raise RuntimeError(f"Missing expected output files: {missing_files}")

        output_dir.mkdir(parents=True, exist_ok=True)
        task_dir = output_dir / task_id
        task_dir.mkdir(parents=True, exist_ok=True)

        os.rename(str(tmp_run_dir), str(run_dir))

        try:
            shutil.rmtree(str(tmp_dir))
        except Exception:
            pass

        return {
            "builder_name": _BUILDER_NAME,
            "builder_version": _BUILDER_VERSION,
            "result": overall,
            "snapshot_id": snapshot["snapshot_id"],
            "bound_commit": head_sha,
            "generated_at": generated_at,
            "task_id": task_id,
            "run_id": run_id,
            "output_directory": str(run_dir),
            "publication_eligible": published and not dirty and not staged,
            "freshness_state": snapshot["freshness_state"],
            "authority_class": snapshot["authority_class"],
            "finding_count": conv_result["finding_count"],
            "files_written": file_list + ["SHA256SUMS"],
        }

    except Exception:
        try:
            shutil.rmtree(str(tmp_dir))
        except Exception:
            pass
        raise


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Build Project Memory snapshot package.")
    parser.add_argument("--repo-root", default=".", help="Path to repository root.")
    parser.add_argument("--output-root", default=".codex-context/project-memory",
                        help="Output root directory.")
    parser.add_argument("--task-id", required=True, help="Task ID for the snapshot.")
    parser.add_argument("--run-id", default=None, help="Run identifier.")
    parser.add_argument("--generated-at", default=None, help="ISO 8601 timestamp.")
    parser.add_argument("--require-clean", action="store_true", default=True,
                        help="Require clean worktree (default).")
    parser.add_argument("--no-require-clean", action="store_false", dest="require_clean",
                        help="Allow dirty worktree for testing.")
    parser.add_argument("--nonpublication", action="store_true", default=False,
                        help="Mark output as non-publication testing mode.")
    parser.add_argument("--registries-dir", default=None,
                        help="Explicit path to registries directory for testing.")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON summary.")
    args = parser.parse_args()

    try:
        result = build_snapshot(
            repo_root=args.repo_root,
            output_root=args.output_root,
            task_id=args.task_id,
            run_id=args.run_id,
            generated_at=args.generated_at,
            require_clean=args.require_clean,
            nonpublication=args.nonpublication,
            registries_dir=args.registries_dir,
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

    print(f"Snapshot built: {result['snapshot_id']}")
    print(f"Output: {result['output_directory']}")
    print(f"Result: {result['result']}")
    print(f"Publication eligible: {result['publication_eligible']}")
    print(f"Findings: {result['finding_count']}")
    print(f"Bound commit: {result['bound_commit']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
