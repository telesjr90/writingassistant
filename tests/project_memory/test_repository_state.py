"""Tests for the deterministic repository-state scanner.

All tests use temporary directories and temporary Git repositories.
Must not mutate the real repository.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.project_memory import repository_state as rst


def _init_git_repo(path: Path) -> None:
    """Initialize a temporary git repository."""
    subprocess.run(["git", "init"], cwd=str(path), capture_output=True, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=str(path), capture_output=True, check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=str(path), capture_output=True, check=True,
    )


def _commit(repo: Path, message: str, files: list[str] | None = None) -> None:
    if files:
        subprocess.run(["git", "add"] + files, cwd=str(repo), capture_output=True, check=True)
    else:
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


class TestCollectRepositoryState:
    """Test collect_repository_state function."""

    def test_clean_repository_detected(self, tmp_path):
        _init_git_repo(tmp_path)
        _write_file(tmp_path, "README.md", "# Test\n")
        _commit(tmp_path, "initial commit")
        state = rst.collect_repository_state(str(tmp_path))
        assert state["clean"] is True
        assert state["dirty"] is False
        assert state["staged"] is False
        assert len(state["modified_paths"]) == 0

    def test_dirty_repository_detected(self, tmp_path):
        _init_git_repo(tmp_path)
        _write_file(tmp_path, "README.md", "# Test\n")
        _commit(tmp_path, "initial commit")
        _write_file(tmp_path, "README.md", "# Modified\n")
        state = rst.collect_repository_state(str(tmp_path))
        assert state["dirty"] is True
        assert state["clean"] is False
        assert len(state["modified_paths"]) >= 1

    def test_staged_repository_detected(self, tmp_path):
        _init_git_repo(tmp_path)
        _write_file(tmp_path, "README.md", "# Test\n")
        _commit(tmp_path, "initial commit")
        _write_file(tmp_path, "README.md", "# Staged change\n")
        subprocess.run(["git", "add", "README.md"], cwd=str(tmp_path), capture_output=True, check=True)
        state = rst.collect_repository_state(str(tmp_path))
        assert state["staged"] is True
        assert state["staged_empty"] is False

    def test_head_captured(self, tmp_path):
        _init_git_repo(tmp_path)
        _write_file(tmp_path, "README.md", "# Test\n")
        _commit(tmp_path, "test commit subject")
        state = rst.collect_repository_state(str(tmp_path))
        assert len(state["head_sha"]) == 40
        assert state["head_subject"] == "test commit subject"
        assert state["branch"] in ("master", "main")

    def test_untracked_files_expanded(self, tmp_path):
        _init_git_repo(tmp_path)
        _write_file(tmp_path, "tracked.txt", "tracked\n")
        _commit(tmp_path, "add tracked")
        _write_file(tmp_path, "untracked.txt", "untracked\n")
        _write_file(tmp_path, "another_untracked.bin", "binary\n")
        state = rst.collect_repository_state(str(tmp_path))
        untracked = state["untracked_paths"]
        assert "untracked.txt" in untracked
        assert "another_untracked.bin" in untracked

    def test_tracked_files_listed(self, tmp_path):
        _init_git_repo(tmp_path)
        _write_file(tmp_path, "a.py", "pass\n")
        _write_file(tmp_path, "b.py", "pass\n")
        _commit(tmp_path, "add files")
        state = rst.collect_repository_state(str(tmp_path))
        tracked = state["tracked_files"]
        assert "a.py" in tracked
        assert "b.py" in tracked

    def test_invalid_root_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            non_repo = Path(td) / "not_a_repo"
            non_repo.mkdir()
            with pytest.raises(ValueError):
                rst.collect_repository_state(str(non_repo))

    def test_nonexistent_root_rejected(self, tmp_path):
        nonexistent = tmp_path / "does_not_exist"
        with pytest.raises(ValueError):
            rst.collect_repository_state(str(nonexistent))

    def test_worktree_output_parsed(self, tmp_path):
        _init_git_repo(tmp_path)
        _write_file(tmp_path, "README.md", "# Test\n")
        _commit(tmp_path, "initial")
        state = rst.collect_repository_state(str(tmp_path))
        assert state["worktree_count"] >= 1
        assert len(state["worktrees"]) >= 1


class TestSourceInventory:
    """Test collect_source_inventory function."""

    def test_tracked_source_hashed(self, tmp_path):
        _init_git_repo(tmp_path)
        content = "# Test file\n"
        _write_file(tmp_path, "docs/project-memory/registries/manifest.json", '{"test": true}')
        _write_file(tmp_path, "docs/roadmap/roadmap_index.yaml", '{"test": true}')
        _write_file(tmp_path, "scripts/project_memory/repository_state.py", content)
        # Create a minimal registry dir
        (tmp_path / "docs" / "project-memory" / "registries").mkdir(parents=True, exist_ok=True)
        (tmp_path / "docs" / "project-memory" / "registries" / "manifest.json").write_text(
            json.dumps({"test": True}), encoding="utf-8"
        )
        (tmp_path / "docs" / "roadmap").mkdir(parents=True, exist_ok=True)
        (tmp_path / "docs" / "roadmap" / "roadmap_index.yaml").write_text(
            json.dumps({"test": True}), encoding="utf-8"
        )
        inventory = rst.collect_source_inventory(str(tmp_path))
        assert "source_hashes" in inventory
        assert "registry_sources" in inventory
        assert "roadmap_sources" in inventory

    def test_hash_order_deterministic(self, tmp_path):
        _init_git_repo(tmp_path)
        (tmp_path / "docs" / "project-memory" / "registries").mkdir(parents=True, exist_ok=True)
        (tmp_path / "docs" / "roadmap").mkdir(parents=True, exist_ok=True)
        (tmp_path / "docs" / "project-memory" / "registries" / "manifest.json").write_text(
            json.dumps({"test": True}), encoding="utf-8"
        )
        (tmp_path / "docs" / "roadmap" / "roadmap_index.yaml").write_text(
            json.dumps({"test": True}), encoding="utf-8"
        )
        inv1 = rst.collect_source_inventory(str(tmp_path))
        inv2 = rst.collect_source_inventory(str(tmp_path))
        assert inv1["source_hashes"] == inv2["source_hashes"]


class TestHashFile:
    """Test hash_file function."""

    def test_hash_regular_file(self, tmp_path):
        content = "hello world\n"
        path = _write_file(tmp_path, "test.txt", content)
        info = rst.hash_file(tmp_path, "test.txt")
        assert "sha256" in info
        assert info["byte_size"] == len(content.encode("utf-8"))
        import hashlib
        expected = hashlib.sha256(content.encode("utf-8")).hexdigest()
        assert info["sha256"] == expected

    def test_hash_missing_file(self, tmp_path):
        info = rst.hash_file(tmp_path, "nonexistent.txt")
        assert "error" in info

    def test_hash_absolute_path_rejected(self, tmp_path):
        info = rst.hash_file(tmp_path, "/etc/passwd")
        assert "error" in info

    def test_hash_traversal_rejected(self, tmp_path):
        info = rst.hash_file(tmp_path, "../outside/file.txt")
        assert "error" in info


class TestSourceLocatorValidation:
    """Test validate_source_locators function."""

    def test_missing_source_produces_finding(self, tmp_path):
        _init_git_repo(tmp_path)
        registry_dir = tmp_path / "registries"
        registry_dir.mkdir()
        reg = {
            "registry_type": "task",
            "schema_version": "1.0.0",
            "records": [{
                "id": "task:TEST-001",
                "type": "task",
                "schema_version": "1.0.0",
                "title": "Test Task",
                "authority_class": "authoritative",
                "lifecycle": {"status": "planned"},
                "task_id": "TEST-001",
                "provenance": {
                    "source_locators": [{"path": "missing/file.md"}],
                },
            }],
        }
        (registry_dir / "tasks.json").write_text(json.dumps(reg), encoding="utf-8")
        result = rst.validate_source_locators(str(tmp_path), str(registry_dir))
        assert result["missing_count"] >= 1
        assert len(result["missing_sources"]) >= 1

    def test_valid_source(self, tmp_path):
        _init_git_repo(tmp_path)
        registry_dir = tmp_path / "registries"
        registry_dir.mkdir()
        _write_file(tmp_path, "real_file.md", "# real\n")
        reg = {
            "registry_type": "task",
            "schema_version": "1.0.0",
            "records": [{
                "id": "task:TEST-002",
                "type": "task",
                "schema_version": "1.0.0",
                "title": "Test Task",
                "authority_class": "authoritative",
                "lifecycle": {"status": "planned"},
                "task_id": "TEST-002",
                "provenance": {
                    "source_locators": [{"path": "real_file.md"}],
                },
            }],
        }
        (registry_dir / "tasks.json").write_text(json.dumps(reg), encoding="utf-8")
        result = rst.validate_source_locators(str(tmp_path), str(registry_dir))
        assert result["valid_count"] >= 1

    def test_line_range_beyond_file(self, tmp_path):
        _init_git_repo(tmp_path)
        registry_dir = tmp_path / "registries"
        registry_dir.mkdir()
        _write_file(tmp_path, "short.txt", "one line\n")
        reg = {
            "registry_type": "task",
            "schema_version": "1.0.0",
            "records": [{
                "id": "task:TEST-003",
                "type": "task",
                "schema_version": "1.0.0",
                "title": "Test Task",
                "authority_class": "authoritative",
                "lifecycle": {"status": "planned"},
                "task_id": "TEST-003",
                "provenance": {
                    "source_locators": [{"path": "short.txt", "line_start": 999}],
                },
            }],
        }
        (registry_dir / "tasks.json").write_text(json.dumps(reg), encoding="utf-8")
        result = rst.validate_source_locators(str(tmp_path), str(registry_dir))
        assert result["invalid_count"] >= 1


class TestRoadmapState:
    """Test parse_roadmap_state function."""

    def test_expected_frontier_passes(self, tmp_path):
        _init_git_repo(tmp_path)
        (tmp_path / "docs" / "roadmap").mkdir(parents=True, exist_ok=True)
        index = {
            "schema_version": "1.0",
            "active_frontier": {
                "current_parent_task_id": "PHASE8-IMPL-024",
                "next_readiness_task_id": "PHASE8-IMPL-024-T003A",
                "planned_architecture_parent_task_id": "PHASE8-IMPL-025",
            },
            "tasks": [
                {"id": "PHASE8-IMPL-026-T001", "title": "T001", "status": "complete/PASS"},
                {"id": "PHASE8-IMPL-026-T002", "title": "T002", "status": "complete/PASS"},
                {"id": "PHASE8-IMPL-025", "title": "PHASE8-IMPL-025", "status": "planned"},
            ],
        }
        (tmp_path / "docs" / "roadmap" / "roadmap_index.yaml").write_text(
            json.dumps(index), encoding="utf-8"
        )
        state = rst.parse_roadmap_state(str(tmp_path))
        assert state["frontier_is_ph8_impl_024_t003a"] is True
        assert state["frontier_next_task"] == "PHASE8-IMPL-024-T003A"
        assert state["ph8_impl_025_active"] is False

    def test_missing_roadmap_file(self, tmp_path):
        _init_git_repo(tmp_path)
        state = rst.parse_roadmap_state(str(tmp_path))
        assert "error" in state


class TestMainCLI:
    """Test CLI entry points."""

    def test_json_output(self, tmp_path):
        _init_git_repo(tmp_path)
        _write_file(tmp_path, "README.md", "# Test\n")
        _commit(tmp_path, "initial")
        result = subprocess.run(
            [sys.executable, str(Path(__file__).resolve().parents[2] / "scripts" / "project_memory" / "repository_state.py"),
             "--repo-root", str(tmp_path), "--json"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["clean"] is True

    def test_human_readable_output(self, tmp_path):
        _init_git_repo(tmp_path)
        _write_file(tmp_path, "README.md", "# Test\n")
        _commit(tmp_path, "initial")
        result = subprocess.run(
            [sys.executable, str(Path(__file__).resolve().parents[2] / "scripts" / "project_memory" / "repository_state.py"),
             "--repo-root", str(tmp_path)],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        assert "Repository:" in result.stdout
