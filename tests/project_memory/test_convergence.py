"""Tests for the deterministic convergence checker.

All tests use temporary directories.
Must not mutate the real repository.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.project_memory import convergence as conv
from scripts.project_memory import repository_state as rst


def _init_git_repo(path: Path) -> None:
    subprocess.run(["git", "init"], cwd=str(path), capture_output=True, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=str(path), capture_output=True, check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=str(path), capture_output=True, check=True,
    )


def _commit(repo: Path, message: str) -> None:
    subprocess.run(["git", "add", "-A"], cwd=str(repo), capture_output=True, check=True)
    subprocess.run(
        ["git", "commit", "-m", message],
        cwd=str(repo), capture_output=True, check=True,
    )


def _write_file(repo: Path, rel_path: str, content: str) -> Path:
    full = repo / rel_path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(content, encoding="utf-8")
    return full


class TestConvergenceResult:
    """Test convergence compute_convergence."""

    def test_pass_with_no_findings(self, tmp_path):
        _init_git_repo(tmp_path)
        _write_file(tmp_path, "README.md", "# Test\n")
        (tmp_path / "docs" / "roadmap").mkdir(parents=True, exist_ok=True)
        index = {
            "schema_version": "1.0",
            "active_frontier": {
                "current_parent_task_id": "PHASE8-IMPL-024",
                "next_readiness_task_id": "PHASE8-IMPL-024-T003A",
                "planned_architecture_parent_task_id": "PHASE8-IMPL-025",
            },
            "tasks": [
                {"id": "PHASE8-IMPL-025", "title": "025", "status": "planned"},
            ],
        }
        (tmp_path / "docs" / "roadmap" / "roadmap_index.yaml").write_text(
            json.dumps(index), encoding="utf-8"
        )
        _commit(tmp_path, "initial")

        repo_state = rst.collect_repository_state(str(tmp_path))
        rmap_state = rst.parse_roadmap_state(str(tmp_path))
        result = conv.compute_convergence(
            repo_root=str(tmp_path),
            registry_validation_findings=[],
            repository_state=repo_state,
            roadmap_state=rmap_state,
            source_locator_results={"total_locators": 0},
            require_clean=True,
        )
        assert result["result"] == "PASS"
        assert result["finding_count"] == 0

    def test_warning_only_returns_pass_with_findings(self, tmp_path):
        _init_git_repo(tmp_path)
        _write_file(tmp_path, "README.md", "# Test\n")
        (tmp_path / "docs" / "roadmap").mkdir(parents=True, exist_ok=True)
        index = {
            "schema_version": "1.0",
            "active_frontier": {
                "current_parent_task_id": "PHASE8-IMPL-024",
                "next_readiness_task_id": "PHASE8-IMPL-024-T003A",
                "planned_architecture_parent_task_id": "PHASE8-IMPL-025",
            },
            "tasks": [
                {"id": "PHASE8-IMPL-025", "title": "025", "status": "planned"},
            ],
        }
        (tmp_path / "docs" / "roadmap" / "roadmap_index.yaml").write_text(
            json.dumps(index), encoding="utf-8"
        )
        _commit(tmp_path, "initial")

        source_locator_results = {
            "missing_count": 1,
            "missing_sources": [{"path": "missing.txt", "record_id": "task:TEST", "authority_class": "generated_evidence", "reason": "not_found"}],
            "invalid_count": 0,
            "invalid_locators": [],
            "excluded_count": 0,
            "excluded_sources": [],
        }
        result = conv.compute_convergence(
            repo_root=str(tmp_path),
            registry_validation_findings=[],
            repository_state=rst.collect_repository_state(str(tmp_path)),
            roadmap_state=rst.parse_roadmap_state(str(tmp_path)),
            source_locator_results=source_locator_results,
            require_clean=True,
        )
        assert result["result"] == "PASS_WITH_FINDINGS"
        assert result["finding_count"] >= 1

    def test_frontier_mismatch_blocks(self, tmp_path):
        _init_git_repo(tmp_path)
        _write_file(tmp_path, "README.md", "# Test\n")
        (tmp_path / "docs" / "roadmap").mkdir(parents=True, exist_ok=True)
        index = {
            "schema_version": "1.0",
            "active_frontier": {
                "current_parent_task_id": "PHASE8-IMPL-024",
                "next_readiness_task_id": "WRONG-TASK",
                "planned_architecture_parent_task_id": "PHASE8-IMPL-025",
            },
            "tasks": [
                {"id": "PHASE8-IMPL-025", "title": "025", "status": "planned"},
            ],
        }
        (tmp_path / "docs" / "roadmap" / "roadmap_index.yaml").write_text(
            json.dumps(index), encoding="utf-8"
        )
        _commit(tmp_path, "initial")
        result = conv.compute_convergence(
            repo_root=str(tmp_path),
            registry_validation_findings=[],
            repository_state=rst.collect_repository_state(str(tmp_path)),
            roadmap_state=rst.parse_roadmap_state(str(tmp_path)),
            source_locator_results={"total_locators": 0},
            require_clean=True,
        )
        assert result["result"] == "BLOCKED"

    def test_ph8_impl_025_unexpected_activation_blocks(self, tmp_path):
        _init_git_repo(tmp_path)
        _write_file(tmp_path, "README.md", "# Test\n")
        (tmp_path / "docs" / "roadmap").mkdir(parents=True, exist_ok=True)
        index = {
            "schema_version": "1.0",
            "active_frontier": {
                "current_parent_task_id": "PHASE8-IMPL-024",
                "next_readiness_task_id": "PHASE8-IMPL-024-T003A",
                "planned_architecture_parent_task_id": "PHASE8-IMPL-025",
            },
            "tasks": [
                {"id": "PHASE8-IMPL-025", "title": "025", "status": "in_progress"},
            ],
        }
        (tmp_path / "docs" / "roadmap" / "roadmap_index.yaml").write_text(
            json.dumps(index), encoding="utf-8"
        )
        _commit(tmp_path, "initial")
        result = conv.compute_convergence(
            repo_root=str(tmp_path),
            registry_validation_findings=[],
            repository_state=rst.collect_repository_state(str(tmp_path)),
            roadmap_state=rst.parse_roadmap_state(str(tmp_path)),
            source_locator_results={"total_locators": 0},
            require_clean=True,
        )
        assert result["result"] == "BLOCKED"

    def test_dirty_worktree_blocks_when_require_clean(self, tmp_path):
        _init_git_repo(tmp_path)
        _write_file(tmp_path, "README.md", "# Test\n")
        _commit(tmp_path, "initial")
        (tmp_path / "docs" / "roadmap").mkdir(parents=True, exist_ok=True)
        index = {
            "schema_version": "1.0",
            "active_frontier": {
                "current_parent_task_id": "PHASE8-IMPL-024",
                "next_readiness_task_id": "PHASE8-IMPL-024-T003A",
                "planned_architecture_parent_task_id": "PHASE8-IMPL-025",
            },
            "tasks": [
                {"id": "PHASE8-IMPL-025", "title": "025", "status": "planned"},
            ],
        }
        (tmp_path / "docs" / "roadmap" / "roadmap_index.yaml").write_text(
            json.dumps(index), encoding="utf-8"
        )
        _write_file(tmp_path, "README.md", "# Modified\n")
        result = conv.compute_convergence(
            repo_root=str(tmp_path),
            repository_state=rst.collect_repository_state(str(tmp_path)),
            roadmap_state=rst.parse_roadmap_state(str(tmp_path)),
            require_clean=True,
        )
        assert result["result"] == "BLOCKED"

    def test_dirty_worktree_passes_when_not_require_clean(self, tmp_path):
        _init_git_repo(tmp_path)
        _write_file(tmp_path, "README.md", "# Test\n")
        _commit(tmp_path, "initial")
        (tmp_path / "docs" / "roadmap").mkdir(parents=True, exist_ok=True)
        index = {
            "schema_version": "1.0",
            "active_frontier": {
                "current_parent_task_id": "PHASE8-IMPL-024",
                "next_readiness_task_id": "PHASE8-IMPL-024-T003A",
                "planned_architecture_parent_task_id": "PHASE8-IMPL-025",
            },
            "tasks": [
                {"id": "PHASE8-IMPL-025", "title": "025", "status": "planned"},
            ],
        }
        (tmp_path / "docs" / "roadmap" / "roadmap_index.yaml").write_text(
            json.dumps(index), encoding="utf-8"
        )
        _write_file(tmp_path, "README.md", "# Modified\n")
        result = conv.compute_convergence(
            repo_root=str(tmp_path),
            repository_state=rst.collect_repository_state(str(tmp_path)),
            roadmap_state=rst.parse_roadmap_state(str(tmp_path)),
            require_clean=False,
        )
        assert result["result"] in ("PASS", "PASS_WITH_FINDINGS")

    def test_registry_validation_errors_block(self, tmp_path):
        _init_git_repo(tmp_path)
        _write_file(tmp_path, "README.md", "# Test\n")
        (tmp_path / "docs" / "roadmap").mkdir(parents=True, exist_ok=True)
        index = {
            "schema_version": "1.0",
            "active_frontier": {
                "current_parent_task_id": "PHASE8-IMPL-024",
                "next_readiness_task_id": "PHASE8-IMPL-024-T003A",
                "planned_architecture_parent_task_id": "PHASE8-IMPL-025",
            },
            "tasks": [
                {"id": "PHASE8-IMPL-025", "title": "025", "status": "planned"},
            ],
        }
        (tmp_path / "docs" / "roadmap" / "roadmap_index.yaml").write_text(
            json.dumps(index), encoding="utf-8"
        )
        _commit(tmp_path, "initial")
        result = conv.compute_convergence(
            repo_root=str(tmp_path),
            registry_validation_findings=[
                {"level": "error", "code": "TEST_ERROR", "message": "test error"},
            ],
            repository_state=rst.collect_repository_state(str(tmp_path)),
            roadmap_state=rst.parse_roadmap_state(str(tmp_path)),
            source_locator_results={"total_locators": 0},
            require_clean=True,
        )
        assert result["result"] == "BLOCKED"


class TestFindingSorting:
    """Test finding sorting determinism."""

    def test_findings_sort_deterministically(self):
        f1 = conv.make_finding(
            code="source_missing", severity="warning",
            title="T1", explanation="E1", affected_record_ids=["task:B"],
        )
        f2 = conv.make_finding(
            code="source_missing", severity="warning",
            title="T2", explanation="E2", affected_record_ids=["task:A"],
        )
        f3 = conv.make_finding(
            code="registry_validation_failed", severity="critical",
            title="T3", explanation="E3",
        )
        findings = [f2, f3, f1]
        sorted_f = conv.sort_findings(findings)
        assert sorted_f[0]["severity"] == "critical"
        assert sorted_f[0]["code"] == "registry_validation_failed"

    def test_deterministic_finding_ids(self):
        f1 = conv.make_finding(
            code="test_code", severity="warning",
            title="Test", explanation="Deterministic",
            affected_record_ids=["task:A"],
        )
        f2 = conv.make_finding(
            code="test_code", severity="warning",
            title="Test", explanation="Deterministic",
            affected_record_ids=["task:A"],
        )
        assert f1["finding_id"] == f2["finding_id"]


class TestFindingCodes:
    """Test that all required finding codes exist."""

    def test_all_required_codes_present(self):
        required = [
            "registry_validation_failed",
            "source_missing",
            "source_not_tracked",
            "source_excluded",
            "source_locator_invalid",
            "source_line_range_invalid",
            "task_missing_from_roadmap",
            "task_status_mismatch",
            "decision_missing",
            "decision_status_mismatch",
            "frontier_mismatch",
            "planned_parent_activated_unexpectedly",
            "accepted_evidence_missing",
            "generated_evidence_unavailable",
            "source_hash_conflict",
            "supersession_conflict",
            "dependency_conflict",
            "working_tree_dirty",
            "staging_not_empty",
            "snapshot_not_commit_bound",
        ]
        for code in required:
            assert code in conv.CODES, f"Missing code: {code}"
