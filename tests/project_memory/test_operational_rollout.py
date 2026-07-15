"""Focused T011 operational rollout tests using temporary Git repositories."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

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


def _temporary_repository(tmp_path: Path) -> Path:
    repo = tmp_path / "repository"
    ignored = shutil.ignore_patterns(
        ".git", ".codex-context", "ai_context", "graphify-out", "node_modules",
        ".venv", "venv", "__pycache__", ".pytest_cache", "projects", ".external_sources",
    )
    shutil.copytree(SOURCE_ROOT, repo, ignore=ignored)
    for relative in REQUIRED_EXAMPLE_EVIDENCE:
        source = SOURCE_ROOT / relative
        destination = repo / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    _run(repo, "git", "init", "-b", "docs/project-memory-foundation")
    _run(repo, "git", "config", "user.email", "test@example.invalid")
    _run(repo, "git", "config", "user.name", "Project Memory Test")
    _run(repo, "git", "add", ".")
    _run(repo, "git", "add", "-f", "--", *REQUIRED_EXAMPLE_EVIDENCE)
    for relative in REQUIRED_EXAMPLE_EVIDENCE:
        assert _run(repo, "git", "ls-files", "--error-unmatch", "--", relative) == relative
    _run(repo, "git", "commit", "-m", "test: temporary operational fixture")
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
    repo = _temporary_repository(tmp_path)
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
