"""Tests for the deterministic snapshot builder.

All tests use temporary directories and temporary Git repositories.
Must not mutate the real repository.
Must not create .codex-context/project-memory/ in the real repository.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.project_memory import build_snapshot as bs


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


def _registries_dir(tmp_path: Path) -> str:
    return str(tmp_path / "docs" / "project-memory" / "registries")


class TestSnapshotBuilder:
    """Test build_snapshot function."""

    def _setup_clean_repo(self, tmp_path: Path) -> str:
        _init_git_repo(tmp_path)
        _write_file(tmp_path, "README.md", "# Test\n")
        registry_dir = tmp_path / "docs" / "project-memory" / "registries"
        registry_dir.mkdir(parents=True, exist_ok=True)
        (tmp_path / "docs" / "project-memory" / "schemas").mkdir(parents=True, exist_ok=True)
        (tmp_path / "docs" / "project-memory" / "schemas" / "project-memory.schema.json").write_text("{}", encoding="utf-8")
        (tmp_path / "docs" / "roadmap").mkdir(parents=True, exist_ok=True)
        (tmp_path / "docs" / "roadmap" / "roadmap_index.yaml").write_text(json.dumps({
            "schema_version": "1.0",
            "active_frontier": {
                "current_parent_task_id": "PHASE8-IMPL-024",
                "next_readiness_task_id": "PHASE8-IMPL-024-T003A",
                "planned_architecture_parent_task_id": "PHASE8-IMPL-025",
            },
            "tasks": [{"id": "PHASE8-IMPL-025", "title": "025", "status": "planned"}],
        }), encoding="utf-8")
        manifest = {
            "registry_type": "manifest",
            "schema_version": "1.0.0",
            "architecture_version": "1.0.0",
            "description": "Test manifest.",
            "registries": [
                {"filename": "projects.json", "record_type": "project", "required": True,
                 "tracked_or_generated": "tracked", "validation_order": 0},
            ],
            "generated_snapshot_output_root": ".codex-context/project-memory/",
        }
        (registry_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        (registry_dir / "projects.json").write_text(json.dumps({
            "registry_type": "project", "schema_version": "1.0.0", "records": [],
        }), encoding="utf-8")
        _commit(tmp_path, "initial commit")
        return str(tmp_path)

    def _build(self, tmp_path, **kwargs):
        rd = _registries_dir(tmp_path)
        merged = {"registries_dir": rd, "nonpublication": False}
        merged.update(kwargs)
        return bs.build_snapshot(**merged)

    def test_clean_repo_creates_complete_package(self, tmp_path):
        repo_root = self._setup_clean_repo(tmp_path)
        output_dir = tmp_path / ".codex-context" / "project-memory"
        result = self._build(
            tmp_path, repo_root=repo_root, output_root=str(output_dir),
            task_id="TEST-T001", run_id="test-run-001",
            generated_at="2026-01-01T00:00:00Z", require_clean=True,
        )
        assert result["result"] in ("PASS", "PASS_WITH_FINDINGS")
        run_dir = output_dir / "TEST-T001" / "test-run-001"
        assert run_dir.exists()
        expected_files = [
            "run-metadata.json", "repository-state.json", "roadmap-state.json",
            "registry-validation.json", "source-inventory.json", "source-hashes.json",
            "convergence-findings.json", "snapshot.json", "summary.md",
            "FILE-INVENTORY.txt", "SHA256SUMS",
        ]
        for fn in expected_files:
            assert (run_dir / fn).is_file(), f"Missing: {fn}"

    def test_dirty_publication_blocked(self, tmp_path):
        repo_root = self._setup_clean_repo(tmp_path)
        _write_file(tmp_path, "README.md", "# Modified\n")
        output_dir = tmp_path / ".codex-context" / "project-memory"
        with pytest.raises(RuntimeError) as exc:
            self._build(
                tmp_path, repo_root=repo_root, output_root=str(output_dir),
                task_id="TEST-T002", require_clean=True,
            )
        assert "dirty" in str(exc.value).lower() or "clean" in str(exc.value).lower()

    def test_nonpublication_mode_marks_output_ineligible(self, tmp_path):
        repo_root = self._setup_clean_repo(tmp_path)
        _write_file(tmp_path, "README.md", "# Modified\n")
        output_dir = tmp_path / ".codex-context" / "project-memory"
        result = self._build(
            tmp_path, repo_root=repo_root, output_root=str(output_dir),
            task_id="TEST-T003", run_id="nonpub-001",
            generated_at="2026-01-01T00:00:00Z", require_clean=False,
            nonpublication=True,
        )
        assert result["publication_eligible"] is False
        assert result["freshness_state"] == "dirty"
        assert result["authority_class"] == "generated_evidence"
        run_dir = output_dir / "TEST-T003" / "nonpub-001"
        assert run_dir.exists()
        snapshot = json.loads((run_dir / "snapshot.json").read_text(encoding="utf-8"))
        assert snapshot["publication_eligible"] is False
        assert snapshot["freshness_state"] == "dirty"
        assert snapshot["authority_class"] == "generated_evidence"

    def test_existing_run_not_overwritten(self, tmp_path):
        repo_root = self._setup_clean_repo(tmp_path)
        output_dir = tmp_path / ".codex-context" / "project-memory"
        self._build(
            tmp_path, repo_root=repo_root, output_root=str(output_dir),
            task_id="TEST-T004", run_id="run-001",
            generated_at="2026-01-01T00:00:00Z", require_clean=True,
        )
        with pytest.raises(FileExistsError):
            self._build(
                tmp_path, repo_root=repo_root, output_root=str(output_dir),
                task_id="TEST-T004", run_id="run-001",
                generated_at="2026-01-01T00:00:00Z", require_clean=True,
            )

    def test_json_files_parse(self, tmp_path):
        repo_root = self._setup_clean_repo(tmp_path)
        output_dir = tmp_path / ".codex-context" / "project-memory"
        self._build(
            tmp_path, repo_root=repo_root, output_root=str(output_dir),
            task_id="TEST-T005", run_id="run-001",
            generated_at="2026-01-01T00:00:00Z", require_clean=True,
        )
        run_dir = output_dir / "TEST-T005" / "run-001"
        json_files = [
            "run-metadata.json", "repository-state.json", "roadmap-state.json",
            "registry-validation.json", "source-inventory.json", "source-hashes.json",
            "convergence-findings.json", "snapshot.json",
        ]
        for fn in json_files:
            data = json.loads((run_dir / fn).read_text(encoding="utf-8"))
            assert isinstance(data, (dict, list))

    def test_file_inventory_complete(self, tmp_path):
        repo_root = self._setup_clean_repo(tmp_path)
        output_dir = tmp_path / ".codex-context" / "project-memory"
        self._build(
            tmp_path, repo_root=repo_root, output_root=str(output_dir),
            task_id="TEST-T006", run_id="run-001",
            generated_at="2026-01-01T00:00:00Z", require_clean=True,
        )
        run_dir = output_dir / "TEST-T006" / "run-001"
        inventory = (run_dir / "FILE-INVENTORY.txt").read_text(encoding="utf-8").strip().split("\n")
        expected = [
            "FILE-INVENTORY.txt", "convergence-findings.json",
            "registry-validation.json", "repository-state.json",
            "roadmap-state.json", "run-metadata.json", "snapshot.json",
            "source-hashes.json", "source-inventory.json", "summary.md",
        ]
        assert sorted(inventory) == sorted(expected)

    def test_sha256sums_verifies(self, tmp_path):
        repo_root = self._setup_clean_repo(tmp_path)
        output_dir = tmp_path / ".codex-context" / "project-memory"
        self._build(
            tmp_path, repo_root=repo_root, output_root=str(output_dir),
            task_id="TEST-T007", run_id="run-001",
            generated_at="2026-01-01T00:00:00Z", require_clean=True,
        )
        run_dir = output_dir / "TEST-T007" / "run-001"
        sums = (run_dir / "SHA256SUMS").read_text(encoding="utf-8").strip().split("\n")
        for line in sums:
            if not line.strip():
                continue
            digest, filename = line.split("  ")
            actual = bs._compute_sha256_file(run_dir / filename)
            assert digest == actual, f"SHA256 mismatch for {filename}"

    def test_deterministic_output(self, tmp_path):
        repo_root = self._setup_clean_repo(tmp_path)
        output_dir1 = tmp_path / "c1" / "project-memory"
        output_dir2 = tmp_path / "c2" / "project-memory"
        gt = "2026-01-01T00:00:00Z"
        rdir = _registries_dir(tmp_path)
        bs.build_snapshot(
            repo_root=repo_root, output_root=str(output_dir1),
            task_id="TEST-T008", run_id="run-001", generated_at=gt,
            require_clean=True, registries_dir=rdir, nonpublication=True,
        )
        bs.build_snapshot(
            repo_root=repo_root, output_root=str(output_dir2),
            task_id="TEST-T008", run_id="run-001", generated_at=gt,
            require_clean=True, registries_dir=rdir, nonpublication=True,
        )
        run1 = output_dir1 / "TEST-T008" / "run-001"
        run2 = output_dir2 / "TEST-T008" / "run-001"
        snapshot1 = json.loads((run1 / "snapshot.json").read_text(encoding="utf-8"))
        snapshot2 = json.loads((run2 / "snapshot.json").read_text(encoding="utf-8"))
        assert snapshot1["bound_commit"] == snapshot2["bound_commit"]
        assert snapshot1["authority_class"] == snapshot2["authority_class"]
        assert snapshot1["task_id"] == snapshot2["task_id"]
        assert snapshot1["convergence"]["result"] == snapshot2["convergence"]["result"]
        assert snapshot1["convergence"]["finding_count"] == snapshot2["convergence"]["finding_count"]

    def test_builder_does_not_mutate_source(self, tmp_path):
        repo_root = self._setup_clean_repo(tmp_path)
        readme = tmp_path / "README.md"
        content_before = readme.read_text(encoding="utf-8")
        output_dir = tmp_path / ".codex-context" / "project-memory"
        self._build(
            tmp_path, repo_root=repo_root, output_root=str(output_dir),
            task_id="TEST-T009", run_id="run-001",
            generated_at="2026-01-01T00:00:00Z", require_clean=True,
        )
        assert readme.read_text(encoding="utf-8") == content_before

    def test_json_flag_stable_summary(self, tmp_path):
        repo_root = self._setup_clean_repo(tmp_path)
        output_dir = tmp_path / ".codex-context" / "project-memory"
        result1 = self._build(
            tmp_path, repo_root=repo_root, output_root=str(output_dir),
            task_id="TEST-T010", run_id="run-001",
            generated_at="2026-01-01T00:00:00Z", require_clean=True,
        )
        run_dir = output_dir / "TEST-T010" / "run-001"
        shutil.rmtree(str(run_dir))
        result2 = self._build(
            tmp_path, repo_root=repo_root, output_root=str(output_dir),
            task_id="TEST-T010", run_id="run-001",
            generated_at="2026-01-01T00:00:00Z", require_clean=True,
        )
        assert result1["result"] == result2["result"]
        assert result1["finding_count"] == result2["finding_count"]

    def test_output_root_escape_rejected(self, tmp_path):
        self._setup_clean_repo(tmp_path)
        with pytest.raises(ValueError):
            bs._validate_output_root(tmp_path, "/tmp/escape")

    def test_output_root_in_protected_path_rejected(self, tmp_path):
        self._setup_clean_repo(tmp_path)
        protected = tmp_path / "docs" / "project-memory" / "output"
        protected.mkdir(parents=True, exist_ok=True)
        with pytest.raises(ValueError):
            bs._validate_output_root(tmp_path, "docs/project-memory/output")

    def test_snapshot_claims_generated_evidence(self, tmp_path):
        repo_root = self._setup_clean_repo(tmp_path)
        output_dir = tmp_path / ".codex-context" / "project-memory"
        self._build(
            tmp_path, repo_root=repo_root, output_root=str(output_dir),
            task_id="TEST-T011", run_id="run-001",
            generated_at="2026-01-01T00:00:00Z", require_clean=True,
        )
        run_dir = output_dir / "TEST-T011" / "run-001"
        snapshot = json.loads((run_dir / "snapshot.json").read_text(encoding="utf-8"))
        assert snapshot["authority_class"] == "generated_evidence"
        assert "authoritative" not in str(snapshot.get("authority_class", ""))


class TestCLI:
    """Test the build_snapshot CLI using subprocess against real scripts."""

    def _setup_clean_repo(self, tmp_path: Path) -> str:
        _init_git_repo(tmp_path)
        _write_file(tmp_path, "README.md", "# Test\n")
        (tmp_path / "docs" / "project-memory" / "schemas").mkdir(parents=True, exist_ok=True)
        (tmp_path / "docs" / "project-memory" / "schemas" / "project-memory.schema.json").write_text("{}", encoding="utf-8")
        (tmp_path / "docs" / "roadmap").mkdir(parents=True, exist_ok=True)
        (tmp_path / "docs" / "roadmap" / "roadmap_index.yaml").write_text(json.dumps({
            "schema_version": "1.0",
            "active_frontier": {"current_parent_task_id": "PHASE8-IMPL-024",
                                "next_readiness_task_id": "PHASE8-IMPL-024-T003A",
                                "planned_architecture_parent_task_id": "PHASE8-IMPL-025"},
            "tasks": [{"id": "PHASE8-IMPL-025", "title": "025", "status": "planned"}],
        }), encoding="utf-8")
        registry_dir = tmp_path / "docs" / "project-memory" / "registries"
        registry_dir.mkdir(parents=True, exist_ok=True)
        manifest = {
            "registry_type": "manifest", "schema_version": "1.0.0",
            "architecture_version": "1.0.0", "description": "Test manifest.",
            "registries": [{"filename": "projects.json", "record_type": "project",
                            "required": True, "tracked_or_generated": "tracked",
                            "validation_order": 0}],
            "generated_snapshot_output_root": ".codex-context/project-memory/",
        }
        (registry_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        (registry_dir / "projects.json").write_text(json.dumps({
            "registry_type": "project", "schema_version": "1.0.0", "records": [],
        }), encoding="utf-8")
        _commit(tmp_path, "initial commit")
        return str(tmp_path)

    def test_cli_json_output(self, tmp_path):
        repo_root = self._setup_clean_repo(tmp_path)
        bs_path = str(Path(__file__).resolve().parents[2] / "scripts" / "project_memory" / "build_snapshot.py")
        output_dir = tmp_path / ".codex-context" / "project-memory"
        reg_dir = _registries_dir(tmp_path)
        result = subprocess.run(
            [sys.executable, bs_path,
             "--repo-root", repo_root, "--output-root", str(output_dir),
             "--task-id", "TEST-CLI-001", "--run-id", "cli-run-001",
             "--generated-at", "2026-01-01T00:00:00Z",
             "--registries-dir", reg_dir, "--json"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"
        data = json.loads(result.stdout)
        assert data["task_id"] == "TEST-CLI-001"
        assert data["result"] in ("PASS", "PASS_WITH_FINDINGS")

    def test_cli_human_readable_output(self, tmp_path):
        repo_root = self._setup_clean_repo(tmp_path)
        bs_path = str(Path(__file__).resolve().parents[2] / "scripts" / "project_memory" / "build_snapshot.py")
        output_dir = tmp_path / ".codex-context" / "project-memory"
        reg_dir = _registries_dir(tmp_path)
        result = subprocess.run(
            [sys.executable, bs_path,
             "--repo-root", repo_root, "--output-root", str(output_dir),
             "--task-id", "TEST-CLI-002", "--run-id", "cli-run-002",
             "--generated-at", "2026-01-01T00:00:00Z",
             "--registries-dir", reg_dir],
            capture_output=True, text=True,
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert "Snapshot built" in result.stdout
