"""Focused T011 operational rollout tests using temporary Git repositories."""

from __future__ import annotations

import json
import os
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

T012_PROPOSED_TREE_PATHS = frozenset({
    ".github/workflows/project-memory.yml",
    ".agents/skills/project-memory-plan-integrity-review/SKILL.md",
    ".agents/skills/project-memory-read/SKILL.md",
    ".agents/skills/writing-assistant-ui-execution/SKILL.md",
    ".opencode/agents/project-memory-ask.md",
    ".opencode/agents/project-memory-frontend-ui-reviewer.md",
    "AGENTS.md",
    "docs/master_plan.md",
    "docs/project-memory/ask-protocol.md",
    "docs/project-memory/chatgpt-github-supervision-policy.md",
    "docs/project-memory/operations.json",
    "docs/project-memory/operator-manual.md",
    "docs/project-memory/registries/decisions.json",
    "docs/project-memory/registries/dependencies.json",
    "docs/project-memory/registries/execution-routing.json",
    "docs/project-memory/registries/manifest.json",
    "docs/project-memory/registries/owner-decisions.json",
    "docs/project-memory/registries/tasks.json",
    "docs/project-memory/registries/tools.json",
    "docs/project-memory/reviewer-protocol.md",
    "docs/project-memory/schemas/project-memory.schema.json",
    "docs/roadmap/decision_log.md",
    "docs/roadmap/decisions/PHASE8-IMPL-023-opencode-go-model-routing-and-small-task-execution.md",
    "docs/roadmap/decisions/PHASE8-IMPL-026-T011-inherited-leaf-execution-routing-repair.md",
    "docs/roadmap/decisions/PHASE8-IMPL-026-T011-project-memory-gate-decoupling-and-github-handoff.md",
    "docs/roadmap/decisions/PHASE8-IMPL-026-T012-current-truth-execution-routing-and-ui-guidance.md",
    "docs/roadmap/enrichment/PHASE8-IMPL-026-T012.enrichment.json",
    "docs/roadmap/enrichment/PHASE8-IMPL-026.enrichment.json",
    "docs/roadmap/implementation_status.md",
    "docs/roadmap/inventory/PHASE8-IMPL-026-T012.md",
    "docs/roadmap/inventory/PHASE8-IMPL-026.md",
    "docs/roadmap/open_questions.md",
    "docs/roadmap/phase_map.md",
    "docs/roadmap/risk_register.md",
    "docs/roadmap/roadmap_index.yaml",
    "docs/roadmap/task_backlog.md",
    "docs/roadmap/tasks/PHASE8-IMPL-026-T012.md",
    "docs/roadmap/tasks/PHASE8-IMPL-026.md",
    "scripts/project_memory/execution_routing.py",
    "scripts/project_memory/operational_rollout.py",
    "scripts/project_memory/plan_integrity.py",
    "scripts/project_memory/render_docs.py",
    "scripts/project_memory/supervise.py",
    "scripts/project_memory/validate_agent_guidance.py",
    "scripts/project_memory/validate_current_truth.py",
    "scripts/project_memory/validate_operational_rollout.py",
    "scripts/project_memory/validate_registries.py",
    "scripts/project_memory/validate_reviewer_guidance.py",
    "tests/project_memory/test_agent_guidance_and_ask.py",
    "tests/project_memory/test_current_truth_governance.py",
    "tests/project_memory/test_current_truth_invocation.py",
    "tests/project_memory/test_execution_routing.py",
    "tests/project_memory/test_operational_rollout.py",
    "tests/project_memory/requirements-ci.txt",
    "tests/project_memory/test_plan_integrity.py",
    "tests/project_memory/test_remaining_mvp_plan.py",
    "tests/project_memory/test_supervise.py",
    "tests/project_memory/test_tracked_registry_source_locators.py",
    "tests/project_memory/test_tracked_task_registry_current_state.py",
    "tests/project_memory/test_validate_registries.py",
})


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


def _temporary_repository(
    tmp_path: Path,
    proposed_tree_paths: frozenset[str] = T012_PROPOSED_TREE_PATHS,
    t012_lifecycle: str = "in_progress",
) -> Path:
    assert _run(SOURCE_ROOT, "git", "rev-parse", "--is-inside-work-tree") == "true"
    assert Path(_run(SOURCE_ROOT, "git", "rev-parse", "--show-toplevel")).resolve() == SOURCE_ROOT
    staged = subprocess.run(
        ("git", "diff", "--cached", "--quiet"),
        cwd=SOURCE_ROOT,
        capture_output=True,
        check=False,
    )
    assert staged.returncode == 0, staged.stderr.decode(errors="replace")
    for relative in proposed_tree_paths:
        path = PurePosixPath(relative)
        assert path.parts and not path.is_absolute() and ".." not in path.parts
        assert not relative.startswith(".codex-context/")

    source_head = _run(SOURCE_ROOT, "git", "rev-parse", "HEAD")
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
    for relative in sorted(proposed_tree_paths):
        source = SOURCE_ROOT / relative
        target = repo / relative
        if source.is_file() or source.is_symlink():
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists() or target.is_symlink():
                target.unlink()
            if source.is_symlink():
                target.symlink_to(source.readlink())
            else:
                shutil.copy2(source, target)
        elif target.exists() or target.is_symlink():
            target.unlink()
    source_paths.update(
        relative
        for relative in proposed_tree_paths
        if (SOURCE_ROOT / relative).is_file() or (SOURCE_ROOT / relative).is_symlink()
    )
    assert t012_lifecycle in {"in_progress", "complete"}
    tasks_path = repo / "docs/project-memory/registries/tasks.json"
    tasks_registry = json.loads(tasks_path.read_text(encoding="utf-8"))
    t012 = next(
        item for item in tasks_registry["records"]
        if item.get("task_id") == "PHASE8-IMPL-026-T012"
    )
    t012["lifecycle"]["status"] = t012_lifecycle
    tasks_path.write_text(json.dumps(tasks_registry, indent=2) + "\n", encoding="utf-8")
    enrichment_path = repo / "docs/roadmap/enrichment/PHASE8-IMPL-026.enrichment.json"
    enrichment = json.loads(enrichment_path.read_text(encoding="utf-8"))
    enrichment["next_project_memory_task"] = (
        "PHASE8-IMPL-026-T012" if t012_lifecycle == "in_progress" else None
    )
    enrichment_path.write_text(json.dumps(enrichment, indent=2) + "\n", encoding="utf-8")
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
    fixture_tree = _run(repo, "git", "write-tree")

    for relative in REQUIRED_EXAMPLE_EVIDENCE:
        if relative in source_paths:
            assert (repo / relative).is_file()
            assert _run(
                repo, "git", "ls-files", "--error-unmatch", "--", relative
            ) == relative
    _run(repo, "git", "commit", "-m", "test: temporary operational fixture")
    assert _run(repo, "git", "rev-parse", "HEAD^{tree}") == fixture_tree

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


def test_fixture_is_hermetic_and_policy_forbids_automatic_mutation(tmp_path):
    token = uuid.uuid4().hex
    source_status_before = _run(
        SOURCE_ROOT, "git", "status", "--porcelain=v1", "--untracked-files=all"
    )
    untracked_relative = f".operational-rollout-untracked-{token}"
    unrelated_tracked_relative = ".gitignore"
    ignored_root = SOURCE_ROOT / ".codex-context"
    ignored_root_existed = ignored_root.exists()
    ignored_relative = f".codex-context/operational-rollout-{token}/sentinel.txt"
    untracked_sentinel = SOURCE_ROOT / untracked_relative
    unrelated_tracked = SOURCE_ROOT / unrelated_tracked_relative
    unrelated_tracked_original = unrelated_tracked.read_bytes()
    ignored_sentinel = SOURCE_ROOT / ignored_relative
    try:
        untracked_sentinel.write_text("untracked fixture sentinel\n", encoding="utf-8")
        unrelated_tracked.write_bytes(
            unrelated_tracked_original + f"\nfixture-{token}\n".encode()
        )
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
        assert (repo / unrelated_tracked_relative).read_bytes() == unrelated_tracked_original
        ui_wrapper = ".agents/skills/writing-assistant-ui-execution/SKILL.md"
        assert (repo / ui_wrapper).read_bytes() == (SOURCE_ROOT / ui_wrapper).read_bytes()
        assert _run(repo, "git", "ls-files", "--error-unmatch", "--", ui_wrapper) == ui_wrapper
    finally:
        untracked_sentinel.unlink(missing_ok=True)
        unrelated_tracked.write_bytes(unrelated_tracked_original)
        ignored_sentinel.unlink(missing_ok=True)
        ignored_sentinel.parent.rmdir()
        if not ignored_root_existed:
            ignored_root.rmdir()

    assert _run(
        SOURCE_ROOT, "git", "status", "--porcelain=v1", "--untracked-files=all"
    ) == source_status_before

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


@pytest.mark.parametrize(
    ("relative", "old", "new", "expected_code"),
    [
        (
            ".github/workflows/project-memory.yml",
            "python3 -m pip install",
            "python3 -m pip check",
            "workflow_contract_missing",
        ),
        (
            "tests/project_memory/requirements-ci.txt",
            "pytest==9.1.1",
            "pytest>=9.1.1",
            "workflow_test_dependency_mismatch",
        ),
        (
            ".github/workflows/project-memory.yml",
            "tests/project_memory/requirements-ci.txt",
            "backend/requirements.txt",
            "workflow_dependency_install_forbidden",
        ),
    ],
)
def test_operational_validator_rejects_missing_unpinned_or_application_dependency_installs(
    tmp_path, relative, old, new, expected_code
):
    repo = _temporary_repository(tmp_path)
    path = repo / relative
    contents = path.read_text(encoding="utf-8")
    assert old in contents
    path.write_text(contents.replace(old, new, 1), encoding="utf-8")

    result = validator.validate_operational_rollout(repo)

    assert result["result"] == "BLOCKED"
    assert expected_code in {finding["code"] for finding in result["findings"]}


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
    tasks = json.loads(
        (repo / "docs/project-memory/registries/tasks.json").read_text(encoding="utf-8")
    )["records"]
    by_task = {item["task_id"]: item for item in tasks}
    assert by_task["PHASE8-IMPL-026"]["lifecycle"]["status"] == "complete"
    assert by_task["PHASE8-IMPL-026-T012"]["lifecycle"]["status"] == "in_progress"
    assert all(
        by_task[task_id]["lifecycle"]["status"] == "planned"
        and "owner-deferred" in by_task[task_id]["notes"].lower()
        for task_id in ("PHASE8-IMPL-026-T006", "PHASE8-IMPL-026-T007")
    )
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
    comparisons = json.loads(
        (Path(explicit["report"]) / "comparisons.json").read_text(encoding="utf-8")
    )["comparisons"]
    sequence = next(
        item for item in comparisons
        if item["subject_id"] == "project-memory-next-actionable"
    )
    assert sequence["expected_state"] == {"task_id": "PHASE8-IMPL-026-T012"}
    assert sequence["observed_state"] == {"task_id": "PHASE8-IMPL-026-T012"}
    assert sequence["classification"] == "matching"
    frontier = next(
        item for item in comparisons
        if item["subject_type"] == "application_frontier"
    )
    assert frontier["expected_state"] == {"task_id": "PHASE8-IMPL-024-T003B"}
    assert frontier["observed_state"] == {"task_id": "PHASE8-IMPL-024-T003B"}
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

    stale_binding = rollout.check_status(
        repo_root=repo,
        expected_branch="docs/project-memory-foundation",
        expected_commit="0" * 40,
        output_root=repo / ".codex-context/project-memory",
        task_id=rollout.DEFAULT_TASK_ID,
        report_dir=explicit["report"],
        snapshot_dir=explicit["snapshot"],
        render_dir=explicit["render"],
        quality_dir=explicit["quality"],
    )
    assert stale_binding["result"] == "STALE"
    assert "commit_mismatch" in stale_binding["reasons"]
    assert stale_binding["refresh_required"] is True

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


def test_clean_detached_github_refresh_uses_the_trusted_expected_branch(tmp_path):
    """A full-history detached checkout must validate routing against its event branch."""
    repo = _temporary_repository(tmp_path)
    expected_branch = "docs/opencode-go-routing-small-task-execution"
    _run(repo, "git", "branch", "-m", expected_branch)
    commit = _run(repo, "git", "rev-parse", "HEAD")
    _run(repo, "git", "checkout", "--detach", commit)
    assert _run(repo, "git", "branch", "--show-current") == ""
    assert not (repo / ".codex-context").exists()
    github_env = os.environ.copy()
    github_env.update({
        "GITHUB_ACTIONS": "true",
        "GITHUB_REF_NAME": expected_branch,
        "GITHUB_SHA": commit,
    })
    for command in (
        ("python3", "scripts/project_memory/validate_registries.py", "--json"),
        ("python3", "scripts/project_memory/execution_routing.py", "validate", "--repo-root", "."),
    ):
        validation = subprocess.run(
            command, cwd=repo, env=github_env, text=True, capture_output=True, check=False
        )
        assert validation.returncode == 0, validation.stdout + validation.stderr
    unbound_env = dict(github_env, GITHUB_SHA="0" * 40)
    unbound = subprocess.run(
        ("python3", "scripts/project_memory/execution_routing.py", "validate", "--repo-root", "."),
        cwd=repo,
        env=unbound_env,
        text=True,
        capture_output=True,
        check=False,
    )
    assert unbound.returncode == 1
    result = subprocess.run(
        (
            "python3", "scripts/project_memory/operational_rollout.py", "refresh",
            "--repo-root", ".",
            "--output-root", ".codex-context/project-memory",
            "--task-id", rollout.DEFAULT_TASK_ID,
            "--expected-branch", expected_branch,
            "--expected-commit", commit,
            "--allow-detached", "--json",
        ),
        cwd=repo,
        env=github_env,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    refresh = json.loads(result.stdout)
    assert refresh["status"]["result"] == "FRESH"
    snapshot = json.loads(
        (Path(refresh["snapshot"]["output_directory"]) / "convergence-findings.json").read_text(
            encoding="utf-8"
        )
    )
    assert snapshot["blocked"] is False
    assert "registry_validation_failed" not in snapshot["finding_codes"]
    assert _run(repo, "git", "status", "--porcelain=v1", "--untracked-files=all") == ""


def test_refresh_after_t012_completion_has_no_project_memory_task(tmp_path, monkeypatch):
    repo = _temporary_repository(tmp_path, t012_lifecycle="complete")
    commit = _run(repo, "git", "rev-parse", "HEAD")
    monkeypatch.setattr(rollout, "_run_ids", lambda: ("20260715T085000Z", "20260715T085001Z"))
    refresh = rollout.refresh(
        repo_root=repo,
        output_root=repo / ".codex-context/project-memory",
        task_id=rollout.DEFAULT_TASK_ID,
        expected_branch="docs/project-memory-foundation",
        expected_commit=commit,
    )
    assert refresh["status"]["result"] == "FRESH"
    tasks = json.loads(
        (repo / "docs/project-memory/registries/tasks.json").read_text(encoding="utf-8")
    )["records"]
    by_task = {item["task_id"]: item for item in tasks}
    assert by_task["PHASE8-IMPL-026-T012"]["lifecycle"]["status"] == "complete"
    assert all(
        by_task[task_id]["lifecycle"]["status"] == "planned"
        for task_id in ("PHASE8-IMPL-026-T006", "PHASE8-IMPL-026-T007")
    )
    comparisons = json.loads(
        (Path(refresh["status"]["packages"]["report"]) / "comparisons.json").read_text(
            encoding="utf-8"
        )
    )["comparisons"]
    sequence = next(
        item for item in comparisons
        if item["subject_id"] == "project-memory-next-actionable"
    )
    assert sequence["expected_state"] == {"task_id": None}
    assert sequence["observed_state"] == {"task_id": None}
    assert sequence["classification"] == "matching"
    frontier = next(
        item for item in comparisons
        if item["subject_type"] == "application_frontier"
    )
    assert frontier["expected_state"] == {"task_id": "PHASE8-IMPL-024-T003B"}
    assert frontier["observed_state"] == {"task_id": "PHASE8-IMPL-024-T003B"}


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


def test_workflow_has_safe_supervision_publication_boundaries(tmp_path):
    repo = _temporary_repository(tmp_path)
    workflow = (repo / ".github/workflows/project-memory.yml").read_text(encoding="utf-8")
    assert "schedule:" not in workflow
    assert "cron:" not in workflow
    assert "python3 -m pip install pytest" not in workflow
    assert "actions/checkout@v7" in workflow
    assert "actions/setup-python@v6" in workflow
    assert "actions/upload-artifact@v7" in workflow
    assert "actions/download-artifact@v8" in workflow
    assert "actions/github-script@v9" in workflow
    assert "scripts/project_memory/supervise.py" in workflow
    assert "GITHUB_STEP_SUMMARY" in workflow
    assert "<!-- project-memory-supervision -->" in workflow
    assert "pull_request_target" not in workflow
    assert "contents: write" not in workflow
    assert "pull-requests: write" in workflow
    assert "git push" not in workflow
    assert workflow.count('- ".gitignore"') == 2
    assert "id: strict_refresh" in workflow
    assert "id: supervise" in workflow
    assert "if: always()" in workflow
    assert "if-no-files-found: error" in workflow
    assert "project-memory-handoff-artifact/project-memory-handoff.md" in workflow
    assert "project-memory-handoff-artifact/project-memory-handoff.json" in workflow
    assert "project-memory-handoff-artifact/SHA256SUMS" in workflow
    assert ".codex-context/project-memory/handoff/\n" not in workflow
