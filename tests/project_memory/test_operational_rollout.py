"""Focused T011 operational rollout tests using temporary Git repositories."""

from __future__ import annotations

import json
import shutil
import subprocess
import tarfile
import uuid
from pathlib import Path
from pathlib import PurePosixPath

import pytest

from scripts.project_memory import operational_rollout as rollout
from scripts.project_memory import validate_operational_rollout as validator

SOURCE_ROOT = Path(__file__).resolve().parents[2]
REQUIRED_EXAMPLE_EVIDENCE = (
    "projects/example/bible.json",
    "projects/example/project.json",
    "projects/example/scenes/scene_001.md",
    "projects/example/storyform.json",
)


def _run(repo: Path, *args: str) -> str:
    result = subprocess.run(args, cwd=repo, text=True, capture_output=True, check=True)
    return result.stdout.strip()


def _nul_paths(repo: Path, *args: str) -> tuple[str, ...]:
    result = subprocess.run(args, cwd=repo, text=True, capture_output=True, check=True)
    return tuple(path for path in result.stdout.split("\0") if path)


def _archive_destination(root: Path, member_name: str) -> Path:
    member_path = PurePosixPath(member_name)
    if not member_path.parts or member_path.is_absolute() or ".." in member_path.parts:
        raise AssertionError(f"unsafe archive member path: {member_name!r}")
    destination = root.joinpath(*member_path.parts)
    if not destination.resolve(strict=False).is_relative_to(root.resolve()):
        raise AssertionError(f"archive member escapes destination: {member_name!r}")
    return destination


def _archive_link_destination(
    root: Path,
    member_destination: Path,
    link_name: str,
    *,
    hard_link: bool,
) -> Path:
    link_path = PurePosixPath(link_name)
    if link_path.is_absolute():
        raise AssertionError(f"unsafe absolute archive link: {link_name!r}")
    link_base = root if hard_link else member_destination.parent
    destination = link_base.joinpath(*link_path.parts).resolve(strict=False)
    if not destination.is_relative_to(root.resolve()):
        raise AssertionError(f"archive link escapes destination: {link_name!r}")
    return destination


def _extract_tracked_archive(archive_path: Path, destination: Path) -> None:
    destination.mkdir()
    with tarfile.open(archive_path, mode="r:") as archive:
        members = archive.getmembers()
        seen: set[Path] = set()
        for member in members:
            target = _archive_destination(destination, member.name)
            if target in seen:
                raise AssertionError(f"duplicate archive member: {member.name!r}")
            seen.add(target)
            if member.issym() or member.islnk():
                _archive_link_destination(
                    destination,
                    target,
                    member.linkname,
                    hard_link=member.islnk(),
                )
            elif not (member.isdir() or member.isfile()):
                raise AssertionError(f"unsupported archive member: {member.name!r}")

        for member in members:
            target = _archive_destination(destination, member.name)
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
                continue

            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.parent.resolve().is_relative_to(destination.resolve()):
                raise AssertionError(f"archive parent escapes destination: {member.name!r}")
            if target.exists() or target.is_symlink():
                raise AssertionError(f"archive member already exists: {member.name!r}")

            if member.isfile():
                source = archive.extractfile(member)
                if source is None:
                    raise AssertionError(f"archive file has no content: {member.name!r}")
                with source, target.open("xb") as output:
                    shutil.copyfileobj(source, output)
                target.chmod(member.mode & 0o777)
            elif member.issym():
                _archive_link_destination(
                    destination,
                    target,
                    member.linkname,
                    hard_link=False,
                )
                target.symlink_to(member.linkname)
            else:
                link_target = _archive_link_destination(
                    destination,
                    target,
                    member.linkname,
                    hard_link=True,
                )
                if not link_target.is_file() or link_target.is_symlink():
                    raise AssertionError(f"unsafe archive hard link: {member.linkname!r}")
                target.hardlink_to(link_target)


def _temporary_repository(tmp_path: Path) -> Path:
    assert _run(SOURCE_ROOT, "git", "rev-parse", "--is-inside-work-tree") == "true"
    assert Path(_run(SOURCE_ROOT, "git", "rev-parse", "--show-toplevel")).resolve() == SOURCE_ROOT
    staged = subprocess.run(
        ("git", "diff", "--cached", "--quiet"),
        cwd=SOURCE_ROOT,
        capture_output=True,
        check=False,
    )
    assert staged.returncode == 0, staged.stderr.decode(errors="replace")
    unstaged_paths = set(
        _nul_paths(SOURCE_ROOT, "git", "diff", "--name-only", "-z")
    )
    executing_test = Path(__file__).resolve().relative_to(SOURCE_ROOT).as_posix()
    assert not unstaged_paths or unstaged_paths == {executing_test}

    source_head = _run(SOURCE_ROOT, "git", "rev-parse", "HEAD")
    source_tree = _run(SOURCE_ROOT, "git", "rev-parse", "HEAD^{tree}")
    source_paths = set(
        _nul_paths(SOURCE_ROOT, "git", "ls-tree", "-r", "--name-only", "-z", "HEAD")
    )
    archive_path = tmp_path / "tracked-head.tar"
    repo = tmp_path / "repository"
    subprocess.run(
        (
            "git",
            "archive",
            "--format=tar",
            "--output",
            str(archive_path),
            "HEAD",
        ),
        cwd=SOURCE_ROOT,
        capture_output=True,
        check=True,
    )
    _extract_tracked_archive(archive_path, repo)
    assert not (repo / ".git").exists()
    assert not (
        repo / ".codex-context/project-memory/example-run/example.json"
    ).exists()

    _run(repo, "git", "init", "-b", "docs/project-memory-foundation")
    _run(repo, "git", "config", "user.email", "test@example.invalid")
    _run(repo, "git", "config", "user.name", "Project Memory Test")
    _run(repo, "git", "add", "--all")
    staged_paths = set(_nul_paths(repo, "git", "ls-files", "-z"))
    assert not staged_paths - source_paths
    ignored_tracked_paths = sorted(source_paths - staged_paths)
    assert all(
        (repo / relative).exists() or (repo / relative).is_symlink()
        for relative in ignored_tracked_paths
    )
    if ignored_tracked_paths:
        _run(repo, "git", "add", "-f", "--", *ignored_tracked_paths)
    assert set(_nul_paths(repo, "git", "ls-files", "-z")) == source_paths
    assert _run(repo, "git", "write-tree") == source_tree

    for relative in REQUIRED_EXAMPLE_EVIDENCE:
        if relative in source_paths:
            assert (repo / relative).is_file()
            assert _run(
                repo, "git", "ls-files", "--error-unmatch", "--", relative
            ) == relative
    _run(repo, "git", "commit", "-m", "test: temporary operational fixture")
    assert _run(repo, "git", "rev-parse", "HEAD^{tree}") == source_tree

    source_git_dir = Path(
        _run(SOURCE_ROOT, "git", "rev-parse", "--absolute-git-dir")
    ).resolve()
    fixture_git_dir = Path(
        _run(repo, "git", "rev-parse", "--absolute-git-dir")
    ).resolve()
    assert fixture_git_dir == (repo / ".git").resolve()
    assert fixture_git_dir != source_git_dir
    assert _run(repo, "git", "rev-parse", "--is-inside-work-tree") == "true"
    assert Path(_run(repo, "git", "rev-parse", "--show-toplevel")).resolve() == repo
    source_commit_lookup = subprocess.run(
        ("git", "cat-file", "-e", f"{source_head}^{{commit}}"),
        cwd=repo,
        capture_output=True,
        check=False,
    )
    assert source_commit_lookup.returncode != 0
    assert _run(repo, "git", "remote") == ""

    ignored = _run(
        repo,
        "git",
        "check-ignore",
        "-v",
        ".codex-context/project-memory/example-run/example.json",
    )
    assert ".gitignore" in ignored
    assert ".codex-context/" in ignored
    assert _run(repo, "git", "status", "--porcelain=v1", "--untracked-files=all") == ""
    return repo


def test_policy_is_event_driven_commit_bound_and_forbids_automatic_mutation(tmp_path):
    token = uuid.uuid4().hex
    untracked_relative = f".operational-rollout-untracked-{token}"
    ignored_root = SOURCE_ROOT / ".codex-context"
    ignored_root_existed = ignored_root.exists()
    ignored_relative = f".codex-context/operational-rollout-{token}/sentinel.txt"
    untracked_sentinel = SOURCE_ROOT / untracked_relative
    ignored_sentinel = SOURCE_ROOT / ignored_relative
    try:
        untracked_sentinel.write_text("untracked fixture sentinel\n", encoding="utf-8")
        ignored_sentinel.parent.mkdir(parents=True, exist_ok=True)
        ignored_sentinel.write_text("ignored fixture sentinel\n", encoding="utf-8")
        assert _run(
            SOURCE_ROOT,
            "git",
            "status",
            "--porcelain=v1",
            "--untracked-files=all",
            "--",
            untracked_relative,
        ) == f"?? {untracked_relative}"
        ignored_check = subprocess.run(
            ("git", "check-ignore", "-q", "--", ignored_relative),
            cwd=SOURCE_ROOT,
            capture_output=True,
            check=False,
        )
        assert ignored_check.returncode == 0

        repo = _temporary_repository(tmp_path)
        assert not (repo / untracked_relative).exists()
        assert not (repo / ignored_relative).exists()
    finally:
        untracked_sentinel.unlink(missing_ok=True)
        ignored_sentinel.unlink(missing_ok=True)
        ignored_sentinel.parent.rmdir()
        if not ignored_root_existed:
            ignored_root.rmdir()

    policy = json.loads((repo / "docs/project-memory/operations.json").read_text(encoding="utf-8"))
    assert policy["schema"] == "project-memory-operations.v1"
    assert policy["cadence"] == {
        "kind": "event_driven_commit_bound",
        "time_based_schedule_required": False,
        "events": policy["cadence"]["events"],
    }
    assert "accepted_application_commit_synchronized" in policy["cadence"]["events"]
    assert policy["closed_parent_no_next_task"]["representation"] == "json_null"
    assert policy["synchronization"]["automatic_git_mutation"] is False
    assert all(value is False for value in policy["mutation_boundaries"].values())


def test_operational_validator_accepts_complete_tracked_contract(tmp_path):
    repo = _temporary_repository(tmp_path)
    result = validator.validate_operational_rollout(repo)
    assert result == {
        "result": "PASS",
        "checked_files": list(validator.REQUIRED_FILES),
        "findings": [],
    }


def test_status_is_read_only_and_reports_missing_package_and_dirty_state(tmp_path):
    repo = _temporary_repository(tmp_path)
    commit = _run(repo, "git", "rev-parse", "HEAD")
    (repo / "dirty.txt").write_text("dirty\n", encoding="utf-8")
    before = _run(repo, "git", "status", "--porcelain=v1")
    result = rollout.check_status(
        repo_root=repo,
        expected_branch="docs/project-memory-foundation",
        expected_commit=commit,
        output_root=repo / ".codex-context/project-memory",
    )
    assert result["result"] == "STALE"
    assert result["refresh_required"] is True
    assert {"dirty_worktree", "missing_required_package"} <= set(result["reasons"])
    assert result["diagnostic_only"] is True
    assert _run(repo, "git", "status", "--porcelain=v1") == before


def test_refresh_rejects_dirty_or_mismatched_repository(tmp_path):
    repo = _temporary_repository(tmp_path)
    commit = _run(repo, "git", "rev-parse", "HEAD")
    (repo / "dirty.txt").write_text("dirty\n", encoding="utf-8")
    with pytest.raises(rollout.OperationalError, match="clean worktree"):
        rollout.refresh(
            repo_root=repo,
            output_root=repo / ".codex-context/project-memory",
            task_id=rollout.DEFAULT_TASK_ID,
            expected_branch="docs/project-memory-foundation",
            expected_commit=commit,
        )


def test_refresh_status_and_ci_check_are_commit_bound_and_ephemeral(tmp_path, monkeypatch):
    repo = _temporary_repository(tmp_path)
    commit = _run(repo, "git", "rev-parse", "HEAD")
    monkeypatch.setattr(rollout, "_run_ids", lambda: ("20260715T070000Z", "20260715T070001Z"))
    refresh = rollout.refresh(
        repo_root=repo,
        output_root=repo / ".codex-context/project-memory",
        task_id=rollout.DEFAULT_TASK_ID,
        expected_branch="docs/project-memory-foundation",
        expected_commit=commit,
    )
    assert refresh["result"] in {"PASS", "PASS_WITH_FINDINGS"}
    assert refresh["plan_integrity"]["readiness"] == "READY_WITH_ADVISORIES"
    assert refresh["plan_integrity"]["findings_by_code"] == {"source_missing": 4}
    assert refresh["branch"] == "docs/project-memory-foundation"
    assert refresh["bound_commit"] == commit
    assert refresh["status"]["refresh_required"] is False
    assert refresh["quality"]["t011_classification"] == "matching"
    assert refresh["quality"]["t011_task_state_mismatch"] is False
    assert _run(repo, "git", "status", "--porcelain=v1", "--untracked-files=all") == ""
    ignored = _run(repo, "git", "status", "--ignored", "--porcelain=v1", "--untracked-files=all")
    assert ".codex-context/" in ignored

    explicit = refresh["status"]["packages"]
    checked = rollout.check_status(
        repo_root=repo,
        expected_branch="docs/project-memory-foundation",
        expected_commit=commit,
        output_root=repo / ".codex-context/project-memory",
        task_id=rollout.DEFAULT_TASK_ID,
        report_dir=explicit["report"],
        snapshot_dir=explicit["snapshot"],
        render_dir=explicit["render"],
        quality_dir=explicit["quality"],
    )
    assert checked["result"] == "FRESH"

    ci_root = tmp_path / "ci-output"
    monkeypatch.setattr(rollout, "_run_ids", lambda: ("20260715T080000Z", "20260715T080001Z"))
    ci = rollout.ci_check(
        repo_root=repo,
        output_root=ci_root,
        task_id=rollout.DEFAULT_TASK_ID,
        expected_branch="docs/project-memory-foundation",
        expected_commit=commit,
    )
    assert ci["result"] in {"PASS", "PASS_WITH_FINDINGS"}
    assert Path(ci["ephemeral_checkout"]).is_relative_to(ci_root)
    assert ci["source_checkout_clean_after"] is True
    assert ci["ephemeral_checkout_clean_after"] is True
    assert ci["generated_evidence_committed"] is False
    assert _run(repo, "git", "status", "--porcelain=v1", "--untracked-files=all") == ""
    assert _run(
        Path(ci["ephemeral_checkout"]),
        "git",
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
    ) == ""


def test_status_detects_checksum_and_registry_hash_drift(tmp_path, monkeypatch):
    repo = _temporary_repository(tmp_path)
    commit = _run(repo, "git", "rev-parse", "HEAD")
    monkeypatch.setattr(rollout, "_run_ids", lambda: ("20260715T090000Z", "20260715T090001Z"))
    refresh = rollout.refresh(
        repo_root=repo,
        output_root=repo / ".codex-context/project-memory",
        task_id=rollout.DEFAULT_TASK_ID,
        expected_branch="docs/project-memory-foundation",
        expected_commit=commit,
    )
    assert refresh["plan_integrity"]["readiness"] == "READY_WITH_ADVISORIES"
    assert refresh["plan_integrity"]["findings_by_code"] == {"source_missing": 4}
    packages = refresh["status"]["packages"]
    quality_report = Path(packages["quality"]) / "quality-report.json"
    quality_report.write_text(quality_report.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    tasks = repo / "docs/project-memory/registries/tasks.json"
    tasks.write_text(tasks.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    result = rollout.check_status(
        repo_root=repo,
        expected_branch="docs/project-memory-foundation",
        expected_commit=commit,
        output_root=repo / ".codex-context/project-memory",
        task_id=rollout.DEFAULT_TASK_ID,
        report_dir=packages["report"], snapshot_dir=packages["snapshot"],
        render_dir=packages["render"], quality_dir=packages["quality"],
    )
    assert result["result"] == "STALE"
    assert "dirty_worktree" in result["reasons"]
    assert "registry_hash_drift" in result["reasons"]
    assert "checksum_failure" in result["reasons"]


def test_cli_status_uses_meaningful_stale_exit_code(tmp_path):
    repo = _temporary_repository(tmp_path)
    commit = _run(repo, "git", "rev-parse", "HEAD")
    exit_code = rollout.main([
        "status", "--repo-root", str(repo),
        "--output-root", str(repo / ".codex-context/project-memory"),
        "--expected-branch", "docs/project-memory-foundation",
        "--expected-commit", commit, "--json",
    ])
    assert exit_code == 2


def test_workflow_has_no_schedule_or_dependency_install(tmp_path):
    repo = _temporary_repository(tmp_path)
    workflow = (repo / ".github/workflows/project-memory.yml").read_text(encoding="utf-8")
    assert "schedule:" not in workflow
    assert "cron:" not in workflow
    assert "pip install" not in workflow
    assert "upload-artifact" not in workflow
    assert "operational_rollout.py ci-check" in workflow
    assert workflow.count('- ".gitignore"') == 2
