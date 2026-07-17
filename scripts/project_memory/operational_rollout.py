#!/usr/bin/env python3
"""Event-driven Project Memory status, refresh, and ephemeral CI orchestration."""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterator

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.project_memory import build_plan_integrity_report
from scripts.project_memory import build_quality_package
from scripts.project_memory import build_snapshot
from scripts.project_memory import render_docs

OPERATIONS_SCHEMA = "project-memory-operations.v1"
DEFAULT_TASK_ID = "PHASE8-IMPL-026-T011"
GIT_SHA_LENGTH = 40


class OperationalError(RuntimeError):
    """Fail-closed operational contract error."""


def _json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise OperationalError(f"Expected JSON object: {path}")
    return value


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=root, text=True, capture_output=True, check=False
    )
    if result.returncode:
        raise OperationalError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.rstrip("\n")


def _repo_state(root: Path) -> dict[str, Any]:
    top = Path(_git(root, "rev-parse", "--show-toplevel")).resolve()
    if top != root:
        raise OperationalError(f"Repository identity mismatch: {top}")
    branch = _git(root, "branch", "--show-current")
    commit = _git(root, "rev-parse", "HEAD")
    staged = bool(_git(root, "diff", "--cached", "--name-only"))
    porcelain = _git(root, "status", "--porcelain=v1")
    return {
        "repository_root": str(root),
        "branch": branch,
        "detached": not bool(branch),
        "commit": commit,
        "staged": staged,
        "dirty": bool(porcelain),
        "porcelain": porcelain.splitlines(),
    }


def _load_policy(root: Path) -> dict[str, Any]:
    policy_path = root / "docs/project-memory/operations.json"
    try:
        policy = _json(policy_path)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise OperationalError(f"Malformed operational policy: {exc}") from exc
    if policy.get("schema") != OPERATIONS_SCHEMA:
        raise OperationalError("Unsupported operational policy schema")
    return policy


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _current_hashes(root: Path, paths: list[str]) -> dict[str, str]:
    return {
        relative: _sha256(root / relative)
        for relative in sorted(paths)
        if (root / relative).is_file()
    }


def _latest_package(base: Path, required_file: str) -> Path | None:
    if not base.is_dir():
        return None
    candidates = sorted(
        (child for child in base.iterdir() if child.is_dir() and (child / required_file).is_file()),
        key=lambda path: path.name,
    )
    return candidates[-1] if candidates else None


def _selected_packages(
    output_root: Path,
    task_id: str,
    explicit: dict[str, str | None],
) -> dict[str, Path | None]:
    discovered = {
        "report": _latest_package(output_root / task_id, "readiness.json"),
        "snapshot": _latest_package(output_root / task_id, "snapshot.json"),
        "render": _latest_package(output_root / "rendered" / task_id, "build-manifest.json"),
        "quality": _latest_package(output_root / f"{task_id}-quality", "quality-report.json"),
    }
    for name, value in explicit.items():
        if value:
            discovered[name] = Path(value).resolve()
    return discovered


def check_status(
    *,
    repo_root: str | Path,
    expected_branch: str,
    expected_commit: str,
    output_root: str | Path,
    task_id: str = DEFAULT_TASK_ID,
    report_dir: str | None = None,
    snapshot_dir: str | None = None,
    render_dir: str | None = None,
    quality_dir: str | None = None,
    accepted_application_commit: str | None = None,
    allow_detached: bool = False,
) -> dict[str, Any]:
    root = Path(repo_root).resolve(strict=True)
    policy = _load_policy(root)
    state = _repo_state(root)
    reasons: list[str] = []
    findings: list[dict[str, Any]] = []

    if state["dirty"]:
        reasons.append("dirty_worktree")
    if state["staged"]:
        reasons.append("staged_changes")
    if state["detached"]:
        if not allow_detached:
            reasons.append("branch_mismatch")
    elif state["branch"] != expected_branch:
        reasons.append("branch_mismatch")
    if state["commit"] != expected_commit:
        reasons.append("commit_mismatch")
    if len(expected_commit) != GIT_SHA_LENGTH:
        reasons.append("malformed_metadata")

    requested = Path(output_root)
    output = (root / requested).resolve() if not requested.is_absolute() else requested.resolve()
    packages = _selected_packages(
        output, task_id,
        {"report": report_dir, "snapshot": snapshot_dir, "render": render_dir, "quality": quality_dir},
    )
    if any(path is None for path in packages.values()):
        reasons.append("missing_required_package")
    else:
        try:
            report_path = packages["report"]
            snapshot_path = packages["snapshot"]
            render_path = packages["render"]
            quality_path = packages["quality"]
            assert report_path and snapshot_path and render_path and quality_path
            report_validation = build_plan_integrity_report.validate_plan_integrity_package(report_path)
            if report_validation["result"] != "PASS":
                reasons.extend(["inventory_mismatch", "checksum_failure"])
            metadata = _json(report_path / "run-metadata.json")
            readiness = _json(report_path / "readiness.json")
            report_findings = _json(report_path / "findings.json")
            if [metadata.get("branch"), metadata.get("bound_commit")] != [expected_branch, expected_commit]:
                reasons.append("commit_mismatch")
            if readiness.get("result") not in policy["accepted_readiness"]:
                reasons.append("blocked_plan_integrity_readiness")
            unsupported = [
                item for item in report_findings.get("findings", [])
                if item.get("blocking")
                or item.get("code") not in policy["accepted_nonblocking_advisory_codes"]
            ]
            if unsupported:
                reasons.append("unsupported_plan_integrity_advisory")

            snapshot_bundle = render_docs.validate_snapshot_package(str(snapshot_path), root)
            snapshot = snapshot_bundle["snapshot"]
            if snapshot.get("freshness_state") != "current":
                reasons.append("non_current_snapshot")
            if not snapshot.get("publication_eligible"):
                reasons.append("non_publication_eligible_snapshot")
            if [snapshot.get("branch"), snapshot.get("bound_commit")] != [expected_branch, expected_commit]:
                reasons.append("commit_mismatch")

            current_registry = _current_hashes(root, sorted(snapshot.get("registry_hashes", {})))
            if current_registry != snapshot.get("registry_hashes", {}):
                reasons.append("registry_hash_drift")
            source_paths = sorted(snapshot.get("source_hashes", {}))
            current_sources = _current_hashes(root, source_paths)
            expected_sources = {
                path: digest for path, digest in snapshot.get("source_hashes", {}).items()
                if (root / path).is_file()
            }
            if current_sources != expected_sources:
                reasons.append("source_hash_drift")

            manifest = _json(render_path / "build-manifest.json")
            if [manifest.get("target_branch"), manifest.get("target_commit")] != [expected_branch, expected_commit]:
                reasons.append("commit_mismatch")
            quality_validation = build_quality_package.validate_quality_package(quality_path)
            if quality_validation["result"] != "PASS":
                reasons.extend(["inventory_mismatch", "checksum_failure", "quality_gate_failure"])
            quality = _json(quality_path / "quality-report.json")
            semantic = quality.get("semantic_validation", {})
            authority = quality.get("authority_validation", {})
            if semantic.get("result") == "BLOCKED":
                reasons.append("semantic_validation_failure")
            if authority.get("result") != "PASS":
                reasons.append("authority_validation_failure")
            if quality.get("result") not in {"PASS", "PASS_WITH_FINDINGS"}:
                reasons.append("quality_gate_failure")
            if accepted_application_commit is not None:
                recorded = quality.get("accepted_application_commit")
                if recorded != accepted_application_commit:
                    reasons.append("accepted_application_commit_mismatch")
            findings = report_findings.get("findings", [])
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError, KeyError, OperationalError) as exc:
            reasons.append("malformed_metadata")
            findings.append({"code": "status_validation_error", "detail": str(exc)})

    reasons = sorted(set(reasons))
    fresh = not reasons
    return {
        "schema": "project-memory-operational-status.v1",
        "result": "FRESH" if fresh else "STALE",
        "refresh_required": not fresh,
        "reasons": reasons,
        "repository": state,
        "expected_branch": expected_branch,
        "expected_commit": expected_commit,
        "task_id": task_id,
        "packages": {name: str(path) if path else None for name, path in packages.items()},
        "findings": findings,
        "authority_class": "generated_evidence",
        "diagnostic_only": True,
    }


def _run_ids() -> tuple[str, str]:
    now = datetime.now(timezone.utc).replace(microsecond=0)
    return (
        now.strftime("%Y%m%dT%H%M%SZ"),
        (now + timedelta(seconds=1)).strftime("%Y%m%dT%H%M%SZ"),
    )


def _iso_from_run_id(run_id: str) -> str:
    return datetime.strptime(run_id, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")


@contextlib.contextmanager
def _trusted_detached_branch(expected_branch: str) -> Iterator[None]:
    """Report a trusted CI branch to existing read-only builders in detached mode."""
    from scripts.project_memory import repository_state, validate_rendered_docs

    original_repo_git = repository_state._run_git
    original_render_git = render_docs._run_git
    original_validate_git = validate_rendered_docs._run_git

    def repo_git(args: list[str], repo_root: Path, timeout: int = 30) -> str:
        if args == ["rev-parse", "--abbrev-ref", "HEAD"]:
            return expected_branch
        return original_repo_git(args, repo_root, timeout)

    def render_git(args: list[str], repo_root: Path, timeout: int = 30) -> str:
        if args == ["rev-parse", "--abbrev-ref", "HEAD"]:
            return expected_branch
        return original_render_git(args, repo_root, timeout)

    def validate_git(repo_root: Path, args: list[str]) -> str:
        if args in (["branch", "--show-current"], ["rev-parse", "--abbrev-ref", "HEAD"]):
            return expected_branch
        return original_validate_git(repo_root, args)

    repository_state._run_git = repo_git
    render_docs._run_git = render_git
    validate_rendered_docs._run_git = validate_git
    try:
        yield
    finally:
        repository_state._run_git = original_repo_git
        render_docs._run_git = original_render_git
        validate_rendered_docs._run_git = original_validate_git


def refresh(
    *,
    repo_root: str | Path,
    output_root: str | Path,
    task_id: str,
    expected_branch: str,
    expected_commit: str,
    allow_detached: bool = False,
) -> dict[str, Any]:
    root = Path(repo_root).resolve(strict=True)
    policy = _load_policy(root)
    state = _repo_state(root)
    if state["dirty"] or state["staged"]:
        raise OperationalError("Refresh requires a clean worktree and empty staging")
    if state["commit"] != expected_commit:
        raise OperationalError("Refresh expected full commit does not match HEAD")
    if state["detached"] and not allow_detached:
        raise OperationalError("Local refresh requires a non-detached branch")
    if not state["detached"] and state["branch"] != expected_branch:
        raise OperationalError("Refresh expected branch does not match current branch")

    output_arg = Path(output_root)
    output = (root / output_arg).resolve() if not output_arg.is_absolute() else output_arg.resolve()
    required_output = (root / policy["local_publication_output_root"]).resolve()
    if output != required_output:
        raise OperationalError(f"Refresh output must resolve to {required_output}")

    report_run_id, publication_run_id = _run_ids()
    generated_at = _iso_from_run_id(publication_run_id)
    branch_context = _trusted_detached_branch(expected_branch) if state["detached"] else contextlib.nullcontext()
    with branch_context:
        report = build_plan_integrity_report.build_plan_integrity_package(
            root, policy["local_publication_output_root"], task_id, report_run_id,
            expected_branch=expected_branch, expected_commit=expected_commit,
        )
        report_dir = Path(report["output_directory"])
        findings = _json(report_dir / "findings.json")
        if report["readiness"] not in policy["accepted_readiness"]:
            blocker_codes = sorted({
                item.get("code", "")
                for item in findings.get("findings", [])
                if item.get("blocking")
            })
            raise OperationalError(
                "Plan Integrity readiness blocked refresh: "
                + json.dumps(
                    {
                        "readiness": report["readiness"],
                        "blocking_finding_codes": blocker_codes,
                        "findings_path": str(report_dir / "findings.json"),
                    },
                    sort_keys=True,
                )
            )
        unsupported = [
            item for item in findings.get("findings", [])
            if item.get("blocking")
            or item.get("code") not in policy["accepted_nonblocking_advisory_codes"]
        ]
        if unsupported:
            raise OperationalError("Unsupported Plan Integrity advisories block publication")

        snapshot = build_snapshot.build_snapshot(
            repo_root=str(root), output_root=policy["local_publication_output_root"],
            task_id=task_id, run_id=publication_run_id, generated_at=generated_at,
            require_clean=True, nonpublication=False,
        )
        snapshot_dir = Path(snapshot["output_directory"])
        render = render_docs.render(
            repo_root=str(root), snapshot_dir=str(snapshot_dir),
            output_root=f"{policy['local_publication_output_root']}/rendered",
            task_id=task_id, run_id=publication_run_id, generated_at=generated_at,
            mode="publication",
        )
        render_dir = Path(render["output_directory"])
        quality = build_quality_package.build_quality_package(
            repo_root=root, report_dir=report_dir, snapshot_dir=snapshot_dir,
            render_dir=render_dir, output_root=policy["local_publication_output_root"],
            task_id=task_id, run_id=publication_run_id,
            expected_branch=expected_branch, expected_commit=expected_commit,
            accepted_advisory_codes=set(policy["accepted_nonblocking_advisory_codes"]),
        )

    status = check_status(
        repo_root=root, expected_branch=expected_branch, expected_commit=expected_commit,
        output_root=output, task_id=task_id, report_dir=str(report_dir),
        snapshot_dir=str(snapshot_dir), render_dir=str(render_dir),
        quality_dir=quality["output_directory"], allow_detached=allow_detached,
    )
    if status["refresh_required"]:
        raise OperationalError(f"Final refresh verification failed: {status['reasons']}")
    return {
        "schema": "project-memory-operational-refresh.v1",
        "result": quality["result"],
        "task_id": task_id,
        "report_run_id": report_run_id,
        "publication_run_id": publication_run_id,
        "branch": expected_branch,
        "bound_commit": expected_commit,
        "plan_integrity": report,
        "snapshot": snapshot,
        "render": render,
        "semantic_validation": str(Path(quality["quality_report"])),
        "quality": quality,
        "status": status,
        "findings": findings.get("findings", []),
        "checksums": {
            "report": _sha256(report_dir / "SHA256SUMS"),
            "snapshot": _sha256(snapshot_dir / "SHA256SUMS"),
            "render": _sha256(render_dir / "SHA256SUMS"),
            "quality": _sha256(Path(quality["output_directory"]) / "SHA256SUMS"),
        },
        "boundaries": {
            "generated_evidence_only": True,
            "git_mutation_performed": False,
            "reviewer_or_model_performed": False,
            "application_worktree_access_performed": False,
        },
    }


def _copy_checkout(source: Path, destination: Path) -> None:
    if destination.exists():
        raise FileExistsError(f"CI checkout destination already exists: {destination}")
    destination.mkdir(parents=True)
    tracked = _git(source, "ls-files", "-z").split("\0")
    for relative in sorted(item for item in tracked if item):
        src = source / relative
        dst = destination / relative
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_symlink():
            os.symlink(os.readlink(src), dst)
        else:
            shutil.copy2(src, dst)
    git_dir = source / ".git"
    if not git_dir.is_dir():
        raise OperationalError("CI ephemeral copy requires a repository with a .git directory")
    shutil.copytree(git_dir, destination / ".git", symlinks=True)


def ci_check(
    *,
    repo_root: str | Path,
    output_root: str | Path,
    task_id: str,
    expected_branch: str,
    expected_commit: str,
) -> dict[str, Any]:
    root = Path(repo_root).resolve(strict=True)
    before = _repo_state(root)
    if before["dirty"] or before["staged"] or before["commit"] != expected_commit:
        raise OperationalError("CI check requires an exact clean checkout")
    if not expected_branch or len(expected_commit) != GIT_SHA_LENGTH:
        raise OperationalError("CI check requires explicit expected branch and full commit")
    temporary_root = Path(output_root).resolve()
    if temporary_root == root or temporary_root.is_relative_to(root):
        raise OperationalError("CI output root must be outside the tracked repository")
    temporary_root.mkdir(parents=True, exist_ok=True)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    shadow = temporary_root / f"project-memory-ci-{run_id}"
    _copy_checkout(root, shadow)
    shadow_state = _repo_state(shadow)
    if shadow_state["commit"] != expected_commit or shadow_state["dirty"]:
        raise OperationalError("Ephemeral CI checkout does not match the exact source commit")
    result = refresh(
        repo_root=shadow, output_root=shadow / ".codex-context/project-memory",
        task_id=task_id, expected_branch=expected_branch,
        expected_commit=expected_commit, allow_detached=True,
    )
    shadow_after = _repo_state(shadow)
    after = _repo_state(root)
    if shadow_after["dirty"] or shadow_after["staged"]:
        raise OperationalError("Ephemeral checkout became dirty")
    if after != before:
        raise OperationalError("Source checkout changed during CI check")
    return {
        "schema": "project-memory-ci-check.v1",
        "result": result["result"],
        "expected_branch": expected_branch,
        "expected_commit": expected_commit,
        "temporary_root": str(temporary_root),
        "ephemeral_checkout": str(shadow),
        "refresh": result,
        "source_checkout_clean_after": True,
        "ephemeral_checkout_clean_after": True,
        "generated_evidence_committed": False,
        "git_mutation_performed": False,
        "reviewer_or_model_performed": False,
    }


def _expected(args: argparse.Namespace) -> tuple[str, str]:
    branch = args.expected_branch or os.environ.get("GITHUB_HEAD_REF") or os.environ.get("GITHUB_REF_NAME")
    commit = args.expected_commit or os.environ.get("GITHUB_SHA")
    if not branch or not commit:
        raise OperationalError("Expected branch and full commit are required")
    return branch, commit


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("status", "check"):
        sub = subparsers.add_parser(name)
        sub.add_argument("--repo-root", default=".")
        sub.add_argument("--output-root", default=".codex-context/project-memory")
        sub.add_argument("--task-id", default=DEFAULT_TASK_ID)
        sub.add_argument("--expected-branch")
        sub.add_argument("--expected-commit")
        sub.add_argument("--report-dir")
        sub.add_argument("--snapshot-dir")
        sub.add_argument("--render-dir")
        sub.add_argument("--quality-dir")
        sub.add_argument("--accepted-application-commit")
        sub.add_argument("--allow-detached", action="store_true")
        sub.add_argument("--json", action="store_true")
    refresh_parser = subparsers.add_parser("refresh")
    refresh_parser.add_argument("--repo-root", default=".")
    refresh_parser.add_argument("--output-root", default=".codex-context/project-memory")
    refresh_parser.add_argument("--task-id", default=DEFAULT_TASK_ID)
    refresh_parser.add_argument("--expected-branch")
    refresh_parser.add_argument("--expected-commit")
    refresh_parser.add_argument("--allow-detached", action="store_true")
    refresh_parser.add_argument("--json", action="store_true")
    ci_parser = subparsers.add_parser("ci-check")
    ci_parser.add_argument("--repo-root", default=".")
    ci_parser.add_argument("--output-root", required=True)
    ci_parser.add_argument("--task-id", default=DEFAULT_TASK_ID)
    ci_parser.add_argument("--expected-branch")
    ci_parser.add_argument("--expected-commit")
    ci_parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        expected_branch, expected_commit = _expected(args)
        if args.command in {"status", "check"}:
            result = check_status(
                repo_root=args.repo_root, expected_branch=expected_branch,
                expected_commit=expected_commit, output_root=args.output_root,
                task_id=args.task_id, report_dir=args.report_dir,
                snapshot_dir=args.snapshot_dir, render_dir=args.render_dir,
                quality_dir=args.quality_dir,
                accepted_application_commit=args.accepted_application_commit,
                allow_detached=args.allow_detached,
            )
            exit_code = 0 if not result["refresh_required"] else 2
        elif args.command == "refresh":
            result = refresh(
                repo_root=args.repo_root, output_root=args.output_root,
                task_id=args.task_id, expected_branch=expected_branch,
                expected_commit=expected_commit,
                allow_detached=args.allow_detached,
            )
            exit_code = 0
        else:
            result = ci_check(
                repo_root=args.repo_root, output_root=args.output_root,
                task_id=args.task_id, expected_branch=expected_branch,
                expected_commit=expected_commit,
            )
            exit_code = 0
    except Exception as exc:
        result = {"result": "BLOCKED", "error": str(exc)}
        exit_code = 3
    if getattr(args, "json", False):
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(result.get("result", "BLOCKED"))
        if result.get("error"):
            print(result["error"])
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
