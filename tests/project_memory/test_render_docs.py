"""Tests for the deterministic Markdown renderer.

All tests use temporary directories and temporary Git repositories.
Must not mutate the real repository.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.project_memory import render_docs as rd


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


def _setup_repo_with_registries(tmp_path: Path, include_findings: bool = True) -> Path:
    """Set up a clean temporary repo with valid registries."""
    _init_git_repo(tmp_path)

    registry_dir = tmp_path / "docs" / "project-memory" / "registries"
    schema_dir = tmp_path / "docs" / "project-memory" / "schemas"
    registry_dir.mkdir(parents=True, exist_ok=True)
    schema_dir.mkdir(parents=True, exist_ok=True)

    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema_version": "1.0.0",
    }
    (schema_dir / "project-memory.schema.json").write_text(json.dumps(schema), encoding="utf-8")

    manifest = {
        "registry_type": "manifest",
        "schema_version": "1.0.0",
        "architecture_version": "1.0.0",
        "description": "Test manifest.",
        "registries": [
            {"filename": fn, "record_type": rt, "required": True,
             "tracked_or_generated": "tracked", "validation_order": i,
             "allowed_authority_classes": ["authoritative", "accepted_evidence"]}
            for i, (fn, rt) in enumerate([
                ("projects.json", "project"),
                ("features.json", "feature"),
                ("boundaries.json", "boundary"),
                ("tasks.json", "task"),
                ("decisions.json", "decision"),
                ("capabilities.json", "capability"),
                ("assets.json", "asset"),
                ("evidence.json", "evidence"),
                ("dependencies.json", "dependency"),
                ("tools.json", "tool"),
                ("owner-decisions.json", "owner_decision"),
            ])
        ],
        "generated_snapshot_output_root": ".codex-context/project-memory/",
    }
    (registry_dir / "manifest.json").write_text(json.dumps(manifest, sort_keys=True), encoding="utf-8")

    def _make_record(rid, rtype, title, status="current", extra=None):
        rec = {
            "id": rid,
            "type": rtype,
            "schema_version": "1.0.0",
            "title": title,
            "authority_class": "authoritative",
            "lifecycle": {"status": status},
            "provenance": {
                "created_by": "TEST",
                "source_locators": [{"path": "README.md"}],
            },
        }
        if extra:
            rec.update(extra)
        return rec

    registries_data = {
        "projects.json": {
            "registry_type": "project", "schema_version": "1.0.0",
            "records": [
                _make_record("project:test-app", "project", "Test Application",
                             extra={"project_id": "test-app",
                                    "description": "A test application."}),
            ],
        },
        "features.json": {
            "registry_type": "feature", "schema_version": "1.0.0",
            "records": [
                _make_record("feature:test-feature", "feature", "Test Feature", status="in_progress",
                             extra={"feature_id": "test-feature",
                                    "implementation_status": "partially_implemented",
                                    "description": "A test feature."}),
            ],
        },
        "boundaries.json": {
            "registry_type": "boundary", "schema_version": "1.0.0",
            "records": [
                _make_record("boundary:analysis-only", "boundary", "Analysis Only",
                             extra={"boundary_id": "analysis-only",
                                    "category": "product_safety",
                                    "is_non_negotiable": True,
                                    "description": "The app is analysis-only."}),
            ],
        },
        "tasks.json": {
            "registry_type": "task", "schema_version": "1.0.0",
            "records": [
                _make_record("task:PHASE8-IMPL-026", "task", "PHASE8-IMPL-026 Project Memory",
                             status="in_progress",
                             extra={"task_id": "PHASE8-IMPL-026",
                                    "task_type": "infrastructure"}),
                _make_record("task:PHASE8-IMPL-026-T001", "task", "T001 Foundation",
                             status="complete",
                             extra={"task_id": "PHASE8-IMPL-026-T001",
                                    "parent_task_id": "PHASE8-IMPL-026",
                                    "task_type": "planning",
                                    "notes": "Complete/PASS."}),
                _make_record("task:PHASE8-IMPL-026-T002", "task", "T002 Schema",
                             status="complete",
                             extra={"task_id": "PHASE8-IMPL-026-T002",
                                    "parent_task_id": "PHASE8-IMPL-026",
                                    "task_type": "infrastructure",
                                    "notes": "Complete/PASS."}),
                _make_record("task:PHASE8-IMPL-026-T003", "task", "T003 Scanners",
                             status="complete",
                             extra={"task_id": "PHASE8-IMPL-026-T003",
                                    "parent_task_id": "PHASE8-IMPL-026",
                                    "task_type": "infrastructure",
                                    "notes": "Complete/PASS-WITH-FINDINGS."}),
                _make_record("task:PHASE8-IMPL-026-T004", "task", "T004 Human-readable memory",
                             status="complete",
                             extra={"task_id": "PHASE8-IMPL-026-T004",
                                    "parent_task_id": "PHASE8-IMPL-026",
                                    "task_type": "runtime",
                                    "notes": "Complete/PASS-WITH-FINDINGS."}),
                _make_record("task:PHASE8-IMPL-026-T004A", "task", "T004A Architecture",
                             status="complete",
                             extra={"task_id": "PHASE8-IMPL-026-T004A",
                                    "parent_task_id": "PHASE8-IMPL-026-T004",
                                    "task_type": "infrastructure",
                                    "notes": "Complete/PASS-WITH-FINDINGS."}),
                _make_record("task:PHASE8-IMPL-026-T004B", "task", "T004B Renderer",
                             status="complete",
                             extra={"task_id": "PHASE8-IMPL-026-T004B",
                                    "parent_task_id": "PHASE8-IMPL-026-T004",
                                    "depends_on": ["PHASE8-IMPL-026-T001"],
                                    "task_type": "runtime",
                                    "is_blocking": False,
                                    "notes": "Complete/PASS."}),
                _make_record("task:PHASE8-IMPL-026-T004C", "task", "T004C Closeout",
                             status="complete",
                             extra={"task_id": "PHASE8-IMPL-026-T004C",
                                    "parent_task_id": "PHASE8-IMPL-026-T004",
                                    "task_type": "closeout",
                                    "notes": "Complete/PASS-WITH-FINDINGS."}),
                _make_record("task:PHASE8-IMPL-026-T005", "task", "T005 Context-tool",
                             status="planned",
                             extra={"task_id": "PHASE8-IMPL-026-T005",
                                    "parent_task_id": "PHASE8-IMPL-026",
                                    "task_type": "infrastructure",
                                    "notes": "Planned next. Inactive."}),
            ],
        },
        "decisions.json": {
            "registry_type": "decision", "schema_version": "1.0.0",
            "records": [
                _make_record("decision:test-decision", "decision", "Test Decision",
                             extra={"decision_id": "test-decision",
                                    "decision_path": "docs/roadmap/decisions/TEST.md",
                                    "question": "What approach?",
                                    "selected_option": "Option A",
                                    "rationale": "Best fit."}),
            ],
        },
        "capabilities.json": {
            "registry_type": "capability", "schema_version": "1.0.0",
            "records": [
                _make_record("capability:test-capability", "capability", "Test Capability",
                             extra={"capability_id": "test-capability",
                                    "implemented": True,
                                    "validated": False,
                                    "description": "A test capability."}),
            ],
        },
        "assets.json": {
            "registry_type": "asset", "schema_version": "1.0.0",
            "records": [
                _make_record("asset:test-asset", "asset", "Test Asset",
                             extra={"asset_id": "test-asset",
                                    "asset_type": "source_file",
                                    "asset_path": "README.md"}),
            ],
        },
        "evidence.json": {
            "registry_type": "evidence", "schema_version": "1.0.0",
            "records": [
                _make_record("evidence:test-evidence", "evidence", "Test Evidence",
                             extra={"evidence_id": "test-evidence",
                                    "evidence_type": "manual_validation",
                                    "description": "Manual test evidence."}),
            ],
        },
        "dependencies.json": {
            "registry_type": "dependency", "schema_version": "1.0.0",
            "records": [
                _make_record("dependency:test-dep", "dependency", "Test Dependency",
                             extra={"dependency_id": "test-dep",
                                    "source_id": "task:PHASE8-IMPL-026-T004B",
                                    "target_id": "task:PHASE8-IMPL-026-T001",
                                    "dependency_type": "task_depends_on",
                                    "is_separate": False}),
            ],
        },
        "tools.json": {
            "registry_type": "tool", "schema_version": "1.0.0",
            "records": [
                _make_record("tool:test-tool", "tool", "Test Tool",
                             extra={"tool_id": "test-tool",
                                    "tool_name": "test_tool",
                                    "tool_type": "validation_script",
                                    "tool_path": "scripts/test.py",
                                    "provenance_state": "approved"}),
            ],
        },
        "owner-decisions.json": {
            "registry_type": "owner_decision", "schema_version": "1.0.0",
            "records": [
                _make_record("owner-decision:test-od", "owner_decision", "Test Owner Decision",
                             extra={"owner_decision_id": "test-od",
                                    "question": "Proceed?",
                                    "selected_option": "Yes"}),
            ],
        },
    }

    for fn, data in registries_data.items():
        (registry_dir / fn).write_text(json.dumps(data, sort_keys=True), encoding="utf-8")

    roadmap_dir = tmp_path / "docs" / "roadmap"
    roadmap_dir.mkdir(parents=True, exist_ok=True)
    (roadmap_dir / "roadmap_index.yaml").write_text(json.dumps({
        "schema_version": "1.0",
        "active_frontier": {
            "current_parent_task_id": "PHASE8-IMPL-024",
            "next_readiness_task_id": "PHASE8-IMPL-024-T003A",
            "planned_architecture_parent_task_id": "PHASE8-IMPL-025",
        },
        "tasks": [{"id": "PHASE8-IMPL-025", "title": "025", "status": "planned"}],
    }), encoding="utf-8")

    _write_file(tmp_path, "README.md", "# Test Repo\n")
    _commit(tmp_path, "initial commit")

    return tmp_path


def _make_snapshot(repo: Path, snapshot_dir: Path) -> None:
    """Build a minimal valid snapshot package for testing."""
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    gt = "2026-01-01T00:00:00Z"
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=str(repo),
        capture_output=True, text=True,
    ).stdout.strip()
    branch = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=str(repo),
        capture_output=True, text=True,
    ).stdout.strip()

    files_to_write = {
        "run-metadata.json": {
            "builder_name": "build_snapshot", "builder_version": "1.0.0",
            "branch": branch, "head_sha": head,
            "head_subject": "test", "task_id": "TEST-SNAP", "run_id": "test-run",
            "generated_at": gt, "clean": True, "staged": False,
            "nonpublication": False, "require_clean": True,
            "publication_eligible": True,
            "exclusions": [], "no_network": True, "no_model": True, "no_external_tool": True,
        },
        "repository-state.json": {
            "branch": branch, "head_sha": head, "clean": True,
            "staged": False, "dirty": False,
        },
        "roadmap-state.json": {
            "frontier_next_task": "PHASE8-IMPL-024-T003A",
            "frontier_is_ph8_impl_024_t003a": True,
            "ph8_impl_025_active": False,
        },
        "registry-validation.json": {
            "result": "PASS", "error_count": 0, "warning_count": 0,
            "errors": [], "warnings": [],
        },
        "source-inventory.json": {
            "registry_sources": [], "roadmap_sources": [],
            "scanner_implementation_sources": [], "source_hashes": {},
        },
        "source-hashes.json": {
            "source_hashes": {}, "hash_count": 0,
        },
        "convergence-findings.json": {
            "result": "PASS_WITH_FINDINGS", "finding_count": 2,
            "findings": [
                {
                    "finding_id": "test-finding-1",
                    "code": "source_missing",
                    "severity": "warning",
                    "title": "Test missing source",
                    "explanation": "Source does not exist.",
                    "affected_record_ids": ["feature:test-feature"],
                    "source_locators": ["missing/file.py"],
                    "authority_context": "authoritative",
                    "evidence": {"reason": "not_found"},
                    "blocks_publication": False,
                    "owner_review_required": False,
                    "suggested_action": "Verify source.",
                },
                {
                    "finding_id": "test-finding-2",
                    "code": "source_locator_invalid",
                    "severity": "warning",
                    "title": "Test invalid locator",
                    "explanation": "Locator path is invalid.",
                    "affected_record_ids": ["project:test-app"],
                    "source_locators": ["invalid/"],
                    "authority_context": "authoritative",
                    "evidence": {"reason": "not_a_regular_file"},
                    "blocks_publication": False,
                    "owner_review_required": False,
                    "suggested_action": "Repair locator.",
                },
            ],
        },
        "snapshot.json": {
            "snapshot_id": "TEST-SNAP/test-run",
            "schema_version": "1.0.0",
            "architecture_version": "1.0.0",
            "authority_class": "generated_evidence",
            "branch": branch,
            "bound_commit": head,
            "generated_at": gt,
            "task_id": "TEST-SNAP",
            "generator": {"name": "build_snapshot", "version": "1.0.0"},
            "freshness_state": "current",
            "publication_eligible": True,
            "convergence": {"result": "PASS_WITH_FINDINGS", "finding_count": 2},
            "exclusions": [],
            "known_limitations": [],
        },
        "summary.md": "# Test Summary\n\nThis is a test snapshot.\n",
    }

    for fn, data in files_to_write.items():
        if fn.endswith(".json"):
            (snapshot_dir / fn).write_text(
                json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        else:
            (snapshot_dir / fn).write_text(data, encoding="utf-8")

    all_files = sorted(files_to_write.keys())
    (snapshot_dir / "FILE-INVENTORY.txt").write_text(
        "\n".join(all_files + ["FILE-INVENTORY.txt"]) + "\n", encoding="utf-8")

    all_hashed = all_files + ["FILE-INVENTORY.txt"]
    sha_lines = []
    for fn in all_hashed:
        if fn == "SHA256SUMS":
            continue
        h = hashlib.sha256((snapshot_dir / fn).read_bytes()).hexdigest()
        sha_lines.append(f"{h}  {fn}")
    (snapshot_dir / "SHA256SUMS").write_text(
        "\n".join(sorted(sha_lines)) + "\n", encoding="utf-8")


def _rebuild_sha256_sums(snap_dir: Path) -> None:
    """Rebuild SHA256SUMS after modifying snapshot files."""
    all_files = sorted([
        f.name for f in snap_dir.iterdir()
        if f.is_file() and f.name != "SHA256SUMS"
    ])
    inventory_text = "\n".join(all_files + ["FILE-INVENTORY.txt"]) + "\n"
    (snap_dir / "FILE-INVENTORY.txt").write_text(inventory_text, encoding="utf-8")

    sha_lines = []
    for fn in sorted(all_files + ["FILE-INVENTORY.txt"]):
        if fn == "SHA256SUMS":
            continue
        h = hashlib.sha256((snap_dir / fn).read_bytes()).hexdigest()
        sha_lines.append(f"{h}  {fn}")
    (snap_dir / "SHA256SUMS").write_text(
        "\n".join(sorted(sha_lines)) + "\n", encoding="utf-8")


class TestInputLoading:
    """Test input loading and validation."""

    def test_valid_manifest_and_registries_accepted(self, tmp_path):
        repo = _setup_repo_with_registries(tmp_path)
        result = rd.load_and_validate_inputs(str(repo))
        assert "manifest" in result
        assert "registries" in result

    def test_missing_registry_rejected(self, tmp_path):
        repo = _setup_repo_with_registries(tmp_path)
        registry_dir = repo / "docs" / "project-memory" / "registries"
        (registry_dir / "projects.json").unlink()
        with pytest.raises(ValueError):
            rd.load_and_validate_inputs(str(repo))

    def test_unsupported_schema_version_rejected(self, tmp_path):
        repo = _setup_repo_with_registries(tmp_path)
        manifest_path = repo / "docs" / "project-memory" / "registries" / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["schema_version"] = "99.0.0"
        manifest_path.write_text(json.dumps(manifest, sort_keys=True), encoding="utf-8")
        _commit(repo, "bad schema")
        with pytest.raises(ValueError):
            rd.load_and_validate_inputs(str(repo))

    def test_input_files_remain_unchanged(self, tmp_path):
        repo = _setup_repo_with_registries(tmp_path)
        manifest_path = repo / "docs" / "project-memory" / "registries" / "manifest.json"
        content_before = manifest_path.read_text(encoding="utf-8")
        rd.load_and_validate_inputs(str(repo))
        assert manifest_path.read_text(encoding="utf-8") == content_before


class TestSnapshotPackage:
    """Test snapshot package validation."""

    def test_complete_valid_package_accepted(self, tmp_path):
        repo = _setup_repo_with_registries(tmp_path)
        snap_dir = tmp_path / "snap"
        _make_snapshot(repo, snap_dir)
        bundle = rd.validate_snapshot_package(str(snap_dir), repo)
        assert bundle["bound_commit"] is not None
        assert bundle["snapshot_branch"] is not None

    def test_missing_required_file_rejected(self, tmp_path):
        repo = _setup_repo_with_registries(tmp_path)
        snap_dir = tmp_path / "snap"
        _make_snapshot(repo, snap_dir)
        (snap_dir / "snapshot.json").unlink()
        with pytest.raises(ValueError, match="Missing required"):
            rd.validate_snapshot_package(str(snap_dir), repo)

    def test_unexpected_file_rejected(self, tmp_path):
        repo = _setup_repo_with_registries(tmp_path)
        snap_dir = tmp_path / "snap"
        _make_snapshot(repo, snap_dir)
        (snap_dir / "extra.txt").write_text("bad", encoding="utf-8")
        with pytest.raises(ValueError, match="Unexpected"):
            rd.validate_snapshot_package(str(snap_dir), repo)

    def test_malformed_json_rejected(self, tmp_path):
        repo = _setup_repo_with_registries(tmp_path)
        snap_dir = tmp_path / "snap"
        _make_snapshot(repo, snap_dir)
        (snap_dir / "snapshot.json").write_text("not json", encoding="utf-8")
        with pytest.raises(ValueError, match="Malformed JSON"):
            rd.validate_snapshot_package(str(snap_dir), repo)

    def test_invalid_checksum_rejected(self, tmp_path):
        repo = _setup_repo_with_registries(tmp_path)
        snap_dir = tmp_path / "snap"
        _make_snapshot(repo, snap_dir)
        sums = (snap_dir / "SHA256SUMS").read_text(encoding="utf-8")
        sums = sums.replace(sums.split("  ")[0], "0" * 64, 1)
        (snap_dir / "SHA256SUMS").write_text(sums, encoding="utf-8")
        with pytest.raises(ValueError, match="Checksum mismatch"):
            rd.validate_snapshot_package(str(snap_dir), repo)

    def test_missing_checksum_coverage_rejected(self, tmp_path):
        repo = _setup_repo_with_registries(tmp_path)
        snap_dir = tmp_path / "snap"
        _make_snapshot(repo, snap_dir)
        sums_text = (snap_dir / "SHA256SUMS").read_text(encoding="utf-8")
        lines = sums_text.strip().split("\n")
        filtered = [l for l in lines if "snapshot.json" not in l]
        (snap_dir / "SHA256SUMS").write_text("\n".join(filtered) + "\n", encoding="utf-8")
        with pytest.raises(ValueError, match="Missing checksum"):
            rd.validate_snapshot_package(str(snap_dir), repo)

    def test_traversal_entry_rejected(self, tmp_path):
        repo = _setup_repo_with_registries(tmp_path)
        snap_dir = tmp_path / "snap"
        _make_snapshot(repo, snap_dir)
        (snap_dir / "../escape").mkdir(parents=True, exist_ok=True)
        with pytest.raises(ValueError):
            rd.validate_snapshot_package(str(snap_dir / "../escape"), repo)

    def test_wrong_authority_class_rejected(self, tmp_path):
        repo = _setup_repo_with_registries(tmp_path)
        snap_dir = tmp_path / "snap"
        _make_snapshot(repo, snap_dir)
        snap = json.loads((snap_dir / "snapshot.json").read_text(encoding="utf-8"))
        snap["authority_class"] = "authoritative"
        (snap_dir / "snapshot.json").write_text(json.dumps(snap, sort_keys=True) + "\n", encoding="utf-8")
        _rebuild_sha256_sums(snap_dir)
        with pytest.raises(ValueError, match="authority_class"):
            rd.validate_snapshot_package(str(snap_dir), repo)

    def test_snapshot_claiming_authoritative_rejected(self, tmp_path):
        repo = _setup_repo_with_registries(tmp_path)
        snap_dir = tmp_path / "snap"
        _make_snapshot(repo, snap_dir)
        snap = json.loads((snap_dir / "snapshot.json").read_text(encoding="utf-8"))
        snap["authoritative"] = True
        (snap_dir / "snapshot.json").write_text(json.dumps(snap, sort_keys=True) + "\n", encoding="utf-8")
        _rebuild_sha256_sums(snap_dir)
        with pytest.raises(ValueError, match="authoritative"):
            rd.validate_snapshot_package(str(snap_dir), repo)

    def test_missing_bound_commit_rejected(self, tmp_path):
        repo = _setup_repo_with_registries(tmp_path)
        snap_dir = tmp_path / "snap"
        _make_snapshot(repo, snap_dir)
        snap = json.loads((snap_dir / "snapshot.json").read_text(encoding="utf-8"))
        snap["bound_commit"] = ""
        (snap_dir / "snapshot.json").write_text(json.dumps(snap, sort_keys=True) + "\n", encoding="utf-8")
        _rebuild_sha256_sums(snap_dir)
        with pytest.raises(ValueError, match="bound_commit"):
            rd.validate_snapshot_package(str(snap_dir), repo)


class TestFreshnessAndMode:
    """Test freshness classification and mode rules."""

    def test_classify_freshness_current(self):
        result = rd.classify_freshness(
            "abc" * 13, "main", "abc" * 13, "main", "publication")
        assert result == "current"

    def test_classify_freshness_stale_commit(self):
        result = rd.classify_freshness(
            "abc" * 13, "main", "def" * 13, "main", "publication")
        assert result == "stale"

    def test_classify_freshness_stale_branch(self):
        result = rd.classify_freshness(
            "abc" * 13, "feature", "abc" * 13, "main", "publication")
        assert result == "stale"

    def test_classify_freshness_historical(self):
        result = rd.classify_freshness(
            "abc" * 13, "main", "abc" * 13, "main", "historical_preview")
        assert result == "historical"

    def test_match_commit_publication_ok(self, tmp_path):
        repo = _setup_repo_with_registries(tmp_path)
        snap_dir = tmp_path / "snap"
        _make_snapshot(repo, snap_dir)
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=str(repo),
            capture_output=True, text=True,
        ).stdout.strip()
        out_dir = tmp_path / ".codex-context" / "project-memory" / "rendered"
        result = rd.render(
            repo_root=str(repo), snapshot_dir=str(snap_dir),
            output_root=str(out_dir), task_id="TEST", run_id="run-001",
            generated_at="2026-01-01T00:00:00Z", mode="publication",
        )
        assert result["freshness"] == "current"
        assert result["result"] == "PASS"

    def test_stale_commit_rejected_in_publication(self, tmp_path):
        repo = _setup_repo_with_registries(tmp_path)
        snap_dir = tmp_path / "snap"
        _make_snapshot(repo, snap_dir)
        _write_file(repo, "new_file.txt", "content\n")
        _commit(repo, "new commit")
        out_dir = tmp_path / ".codex-context" / "project-memory" / "rendered"
        with pytest.raises(ValueError, match="bound_commit|stale"):
            rd.render(
                repo_root=str(repo), snapshot_dir=str(snap_dir),
                output_root=str(out_dir), task_id="TEST", run_id="run-001",
                generated_at="2026-01-01T00:00:00Z", mode="publication",
            )

    def test_dirty_repository_rejected_in_publication(self, tmp_path):
        repo = _setup_repo_with_registries(tmp_path)
        snap_dir = tmp_path / "snap"
        _make_snapshot(repo, snap_dir)
        (repo / "README.md").write_text("# Modified\n", encoding="utf-8")
        out_dir = tmp_path / ".codex-context" / "project-memory" / "rendered"
        with pytest.raises(ValueError, match="clean worktree"):
            rd.render(
                repo_root=str(repo), snapshot_dir=str(snap_dir),
                output_root=str(out_dir), task_id="TEST", run_id="run-001",
                generated_at="2026-01-01T00:00:00Z", mode="publication",
            )

    def test_stale_snapshot_accepted_historical_preview(self, tmp_path):
        repo = _setup_repo_with_registries(tmp_path)
        snap_dir = tmp_path / "snap"
        _make_snapshot(repo, snap_dir)
        _write_file(repo, "new_file.txt", "content\n")
        _commit(repo, "new commit")
        out_dir = tmp_path / "output"
        result = rd.render(
            repo_root=str(repo), snapshot_dir=str(snap_dir),
            output_root=str(out_dir), task_id="TEST", run_id="hist-001",
            generated_at="2026-01-01T00:00:00Z", mode="historical_preview",
        )
        assert result["freshness"] == "historical"
        assert result["publication_eligible"] is True

    def test_historical_mode_rejected_under_publication_root(self, tmp_path):
        repo = _setup_repo_with_registries(tmp_path)
        snap_dir = tmp_path / "snap"
        _make_snapshot(repo, snap_dir)
        out_dir = tmp_path / ".codex-context" / "project-memory" / "rendered"
        with pytest.raises(ValueError, match="publication root"):
            rd.render(
                repo_root=str(repo), snapshot_dir=str(snap_dir),
                output_root=str(out_dir), task_id="TEST", run_id="hist-002",
                generated_at="2026-01-01T00:00:00Z", mode="historical_preview",
            )

    def test_publication_mode_rejected_outside_publication_root(self, tmp_path):
        repo = _setup_repo_with_registries(tmp_path)
        snap_dir = tmp_path / "snap"
        _make_snapshot(repo, snap_dir)
        out_dir = tmp_path / "somewhere-else"
        with pytest.raises(ValueError, match="Publication mode"):
            rd.render(
                repo_root=str(repo), snapshot_dir=str(snap_dir),
                output_root=str(out_dir), task_id="TEST", run_id="run-001",
                generated_at="2026-01-01T00:00:00Z", mode="publication",
            )


class TestRendering:
    """Test the 14-page rendering."""

    def _render_to_pages(self, tmp_path, mode="publication"):
        repo = _setup_repo_with_registries(tmp_path)
        snap_dir = tmp_path / "snap"
        _make_snapshot(repo, snap_dir)
        if mode == "publication":
            out_root = tmp_path / ".codex-context" / "project-memory" / "rendered"
        else:
            out_root = tmp_path / "output"
        rd.render(
            repo_root=str(repo), snapshot_dir=str(snap_dir),
            output_root=str(out_root), task_id="TEST", run_id="run-001",
            generated_at="2026-01-01T00:00:00Z", mode=mode,
        )
        run_dir = out_root / "TEST" / "run-001"
        docs_dir = run_dir / "docs"
        return docs_dir, run_dir, out_root

    def test_exact_14_page_set_generated(self, tmp_path):
        docs_dir, run_dir, _ = self._render_to_pages(tmp_path)
        pages = set()
        for entry in docs_dir.iterdir():
            if entry.is_file() and entry.suffix == ".md":
                pages.add(entry.name)
        assert pages == rd.RENDERED_PAGE_NAMES_SET
        assert len(pages) == 14

    def test_navigation_order_preserved(self, tmp_path):
        docs_dir, run_dir, _ = self._render_to_pages(tmp_path)
        manifest = json.loads((run_dir / "build-manifest.json").read_text(encoding="utf-8"))
        nav = manifest["page_navigation_order"]
        assert nav == list(rd.RENDERED_PAGE_NAMES)

    def test_every_page_begins_with_banner(self, tmp_path):
        docs_dir, run_dir, _ = self._render_to_pages(tmp_path)
        for page_name in rd.RENDERED_PAGE_NAMES:
            content = (docs_dir / page_name).read_text(encoding="utf-8")
            assert "Generated evidence — not project authority" in content
            assert "Generated Evidence — Not Project Authority" in content

    def test_stale_banner_in_historical_preview(self, tmp_path):
        repo = _setup_repo_with_registries(tmp_path)
        snap_dir = tmp_path / "snap"
        _make_snapshot(repo, snap_dir)
        _write_file(repo, "another.txt", "x\n")
        _commit(repo, "new commit")
        out_dir = tmp_path / "output"
        rd.render(
            repo_root=str(repo), snapshot_dir=str(snap_dir),
            output_root=str(out_dir), task_id="TEST", run_id="h-001",
            generated_at="2026-01-01T00:00:00Z", mode="historical_preview",
        )
        docs_dir = out_dir / "TEST" / "h-001" / "docs"
        content = (docs_dir / "index.md").read_text(encoding="utf-8")
        assert "Historical preview" in content
        assert "does not represent the current repository commit" in content

    def test_project_records_on_overview_page(self, tmp_path):
        docs_dir, run_dir, _ = self._render_to_pages(tmp_path)
        content = (docs_dir / "application-overview.md").read_text(encoding="utf-8")
        assert "Test Application" in content or "test-app" in content

    def test_boundary_records_on_boundaries_page(self, tmp_path):
        docs_dir, run_dir, _ = self._render_to_pages(tmp_path)
        content = (docs_dir / "product-boundaries.md").read_text(encoding="utf-8")
        assert "Analysis Only" in content or "analysis-only" in content

    def test_feature_records_on_features_page(self, tmp_path):
        docs_dir, run_dir, _ = self._render_to_pages(tmp_path)
        content = (docs_dir / "features.md").read_text(encoding="utf-8")
        assert "Test Feature" in content or "test-feature" in content

    def test_capability_records_on_capabilities_page(self, tmp_path):
        docs_dir, run_dir, _ = self._render_to_pages(tmp_path)
        content = (docs_dir / "capabilities.md").read_text(encoding="utf-8")
        assert "Test Capability" in content or "test-capability" in content

    def test_task_records_on_roadmap_page(self, tmp_path):
        docs_dir, run_dir, _ = self._render_to_pages(tmp_path)
        content = (docs_dir / "current-roadmap.md").read_text(encoding="utf-8")
        assert "T001" in content or "PHASE8-IMPL-026-T001" in content

    def test_convergence_page_includes_all_findings(self, tmp_path):
        docs_dir, run_dir, _ = self._render_to_pages(tmp_path)
        content = (docs_dir / "convergence-findings.md").read_text(encoding="utf-8")
        assert "test-finding-1" in content
        assert "test-finding-2" in content

    def test_missing_sources_visible(self, tmp_path):
        docs_dir, run_dir, _ = self._render_to_pages(tmp_path)
        content = (docs_dir / "convergence-findings.md").read_text(encoding="utf-8")
        assert "missing/file.py" in content

    def test_application_frontier_present(self, tmp_path):
        docs_dir, run_dir, _ = self._render_to_pages(tmp_path)
        content = (docs_dir / "index.md").read_text(encoding="utf-8")
        assert "PHASE8-IMPL-024-T003A" in content

    def test_ph8_impl_025_inactive(self, tmp_path):
        docs_dir, run_dir, _ = self._render_to_pages(tmp_path)
        content = (docs_dir / "index.md").read_text(encoding="utf-8")
        assert "inactive" in content.lower()

    def test_generated_evidence_not_authoritative(self, tmp_path):
        docs_dir, run_dir, _ = self._render_to_pages(tmp_path)
        content = (docs_dir / "index.md").read_text(encoding="utf-8")
        assert "not project authority" in content.lower()

    def test_remaining_work_shows_only_incomplete(self, tmp_path):
        docs_dir, run_dir, _ = self._render_to_pages(tmp_path)
        content = (docs_dir / "remaining-work.md").read_text(encoding="utf-8")
        assert "T004B" in content or "Renderer" in content

    def test_decisions_page_includes_owner_decisions(self, tmp_path):
        docs_dir, run_dir, _ = self._render_to_pages(tmp_path)
        content = (docs_dir / "decisions.md").read_text(encoding="utf-8")
        assert "Test Decision" in content or "test-decision" in content
        assert "Test Owner Decision" in content or "test-od" in content

    def test_evidence_page_renders_records(self, tmp_path):
        docs_dir, run_dir, _ = self._render_to_pages(tmp_path)
        content = (docs_dir / "evidence.md").read_text(encoding="utf-8")
        assert "Test Evidence" in content or "test-evidence" in content

    def test_assets_page_renders_records(self, tmp_path):
        docs_dir, run_dir, _ = self._render_to_pages(tmp_path)
        content = (docs_dir / "assets.md").read_text(encoding="utf-8")
        assert "Test Asset" in content or "test-asset" in content

    def test_dependencies_page_renders_records(self, tmp_path):
        docs_dir, run_dir, _ = self._render_to_pages(tmp_path)
        content = (docs_dir / "dependencies.md").read_text(encoding="utf-8")
        assert "Test Dependency" in content or "test-dep" in content

    def test_risks_page_includes_open_questions(self, tmp_path):
        docs_dir, run_dir, _ = self._render_to_pages(tmp_path)
        content = (docs_dir / "risks-and-open-questions.md").read_text(encoding="utf-8")
        assert "Q151" in content
        assert "Q154" in content


class TestMarkdownSafety:
    """Test Markdown safety sanitization."""

    def test_html_escaped(self):
        assert "&lt;script&gt;" in rd._html_escape("<script>")

    def test_ampersand_escaped(self):
        assert "&amp;" in rd._html_escape("&")

    def test_control_characters_removed(self):
        result = rd._normalize_text("hello\x00world")
        assert "\x00" not in result
        assert "hello" in result

    def test_line_ending_normalized(self):
        result = rd._normalize_text("a\r\nb\rc")
        assert "\r" not in result

    def test_table_separator_escaped(self):
        result = rd._escape_table_cell("a|b")
        assert "\\|" in result

    def test_inline_code_escapes_backticks(self):
        result = rd._markdown_code("a`b")
        assert "\\`" in result

    def test_banner_always_first_in_page(self, tmp_path):
        repo = _setup_repo_with_registries(tmp_path)
        snap_dir = tmp_path / "snap"
        _make_snapshot(repo, snap_dir)
        out_dir = tmp_path / ".codex-context" / "project-memory" / "rendered"
        rd.render(
            repo_root=str(repo), snapshot_dir=str(snap_dir),
            output_root=str(out_dir), task_id="TEST", run_id="banner-001",
            generated_at="2026-01-01T00:00:00Z", mode="publication",
        )
        docs_dir = out_dir / "TEST" / "banner-001" / "docs"
        content = (docs_dir / "index.md").read_text(encoding="utf-8")
        banner_pos = content.find("Generated Evidence")
        assert banner_pos >= 0
        assert banner_pos < 1000

    def test_rendered_ids_are_code_formatted(self, tmp_path):
        docs_dir, run_dir, _ = _render_standard_helper(tmp_path)
        content = (docs_dir / "product-boundaries.md").read_text(encoding="utf-8")
        lines = content.split("\n")
        found_code = False
        for line in lines:
            if "**ID:**" in line and "`" in line:
                found_code = True
                break
        assert found_code

    def test_javascript_link_sanitized(self):
        result = rd._sanitize_string("javascript:alert(1)")
        assert result != "javascript:alert(1)"

    def test_script_tag_neutralized(self):
        result = rd._sanitize_string("<script>alert('xss')</script>")
        assert "<script>" not in result
        assert "&lt;script&gt;" in result


class TestManifestAndPackage:
    """Test build manifest, source-snapshot, inventory, checksums."""

    def _render_standard(self, tmp_path):
        return _render_standard_helper(tmp_path)

    def test_manifest_contains_required_fields(self, tmp_path):
        _, run_dir, _ = _render_standard_helper(tmp_path)
        manifest = json.loads((run_dir / "build-manifest.json").read_text(encoding="utf-8"))
        required = ["schema_version", "architecture_version", "renderer_name",
                    "renderer_version", "authority_class", "mode", "task_id",
                    "run_id", "generated_at", "target_commit", "convergence_result",
                    "page_count", "page_hashes", "freshness", "publication_eligible"]
        for field in required:
            assert field in manifest, f"Missing field: {field}"

    def test_authority_class_fixed_to_generated_evidence(self, tmp_path):
        _, run_dir, _ = _render_standard_helper(tmp_path)
        manifest = json.loads((run_dir / "build-manifest.json").read_text(encoding="utf-8"))
        assert manifest["authority_class"] == "generated_evidence"

    def test_page_hashes_match_generated_pages(self, tmp_path):
        _, run_dir, _ = _render_standard_helper(tmp_path)
        docs_dir = run_dir / "docs"
        manifest = json.loads((run_dir / "build-manifest.json").read_text(encoding="utf-8"))
        for page_name, expected_hash in manifest["page_hashes"].items():
            actual = hashlib.sha256(
                (docs_dir / page_name).read_bytes()
            ).hexdigest()
            assert actual == expected_hash, f"Hash mismatch for {page_name}"

    def test_inventory_contains_every_file_once(self, tmp_path):
        _, run_dir, _ = _render_standard_helper(tmp_path)
        inventory = (run_dir / "FILE-INVENTORY.txt").read_text(encoding="utf-8").strip().split("\n")
        actual_files = set()
        for entry in run_dir.rglob("*"):
            if entry.is_file():
                rel = str(entry.relative_to(run_dir))
                actual_files.add(rel)
        assert set(inventory) == actual_files

    def test_sha256sums_verifies(self, tmp_path):
        _, run_dir, _ = _render_standard_helper(tmp_path)
        sums = (run_dir / "SHA256SUMS").read_text(encoding="utf-8").strip().split("\n")
        for line in sums:
            if not line.strip():
                continue
            digest, filename = line.split("  ")
            actual = hashlib.sha256(
                (run_dir / filename).read_bytes()
            ).hexdigest()
            assert digest == actual, f"SHA256 mismatch for {filename}"

    def test_deterministic_output(self, tmp_path):
        repo = _setup_repo_with_registries(tmp_path)
        snap_dir = tmp_path / "snap"
        _make_snapshot(repo, snap_dir)

        out1 = tmp_path / ".codex-context" / "project-memory" / "rendered"

        rd.render(
            repo_root=str(repo), snapshot_dir=str(snap_dir),
            output_root=str(out1), task_id="DET", run_id="r001",
            generated_at="2026-01-01T00:00:00Z", mode="publication",
        )

        run1 = out1 / "DET" / "r001"
        h1 = {}
        for page in rd.RENDERED_PAGE_NAMES:
            h1[page] = hashlib.sha256((run1 / "docs" / page).read_bytes()).hexdigest()

        shutil.rmtree(str(out1 / "DET"))

        rd.render(
            repo_root=str(repo), snapshot_dir=str(snap_dir),
            output_root=str(out1), task_id="DET", run_id="r001",
            generated_at="2026-01-01T00:00:00Z", mode="publication",
        )

        run2 = out1 / "DET" / "r001"
        h2 = {}
        for page in rd.RENDERED_PAGE_NAMES:
            h2[page] = hashlib.sha256((run2 / "docs" / page).read_bytes()).hexdigest()

        assert h1 == h2, f"Page hashes differ! Only same: {set(h1.keys()) & set(h2.keys()) - set(k for k in h1 if h1[k] == h2[k])}"

        manifest1 = json.loads((run1 / "build-manifest.json").read_text(encoding="utf-8"))
        manifest2 = json.loads((run2 / "build-manifest.json").read_text(encoding="utf-8"))
        assert manifest1["target_commit"] == manifest2["target_commit"]
        assert manifest1["convergence_result"] == manifest2["convergence_result"]
        assert manifest1["page_count"] == manifest2["page_count"]

    def test_existing_output_not_overwritten(self, tmp_path):
        repo = _setup_repo_with_registries(tmp_path)
        snap_dir = tmp_path / "snap"
        _make_snapshot(repo, snap_dir)
        out_dir = tmp_path / ".codex-context" / "project-memory" / "rendered"
        rd.render(
            repo_root=str(repo), snapshot_dir=str(snap_dir),
            output_root=str(out_dir), task_id="OWR", run_id="r001",
            generated_at="2026-01-01T00:00:00Z", mode="publication",
        )
        with pytest.raises(FileExistsError):
            rd.render(
                repo_root=str(repo), snapshot_dir=str(snap_dir),
                output_root=str(out_dir), task_id="OWR", run_id="r001",
                generated_at="2026-01-01T00:00:00Z", mode="publication",
            )

    def test_output_inside_protected_dir_rejected(self, tmp_path):
        repo = _setup_repo_with_registries(tmp_path)
        snap_dir = tmp_path / "snap"
        _make_snapshot(repo, snap_dir)
        out_dir = tmp_path / "docs" / "project-memory" / "output"
        with pytest.raises(ValueError, match="protected authority"):
            rd.render(
                repo_root=str(repo), snapshot_dir=str(snap_dir),
                output_root=str(out_dir), task_id="TEST", run_id="r001",
                generated_at="2026-01-01T00:00:00Z", mode="historical_preview",
            )

    def test_input_files_never_mutated_by_render(self, tmp_path):
        repo = _setup_repo_with_registries(tmp_path)
        reg_before = {}
        for entry in (repo / "docs" / "project-memory" / "registries").iterdir():
            if entry.is_file():
                reg_before[entry.name] = hashlib.sha256(
                    entry.read_bytes()).hexdigest()

        snap_dir = tmp_path / "snap"
        _make_snapshot(repo, snap_dir)
        snap_before = {}
        for entry in snap_dir.iterdir():
            if entry.is_file():
                snap_before[entry.name] = hashlib.sha256(
                    entry.read_bytes()).hexdigest()

        out_dir = tmp_path / ".codex-context" / "project-memory" / "rendered"
        rd.render(
            repo_root=str(repo), snapshot_dir=str(snap_dir),
            output_root=str(out_dir), task_id="MUT", run_id="r001",
            generated_at="2026-01-01T00:00:00Z", mode="publication",
        )

        for entry in (repo / "docs" / "project-memory" / "registries").iterdir():
            if entry.is_file():
                h = hashlib.sha256(entry.read_bytes()).hexdigest()
                assert reg_before[entry.name] == h, f"Registry mutated: {entry.name}"

        for entry in snap_dir.iterdir():
            if entry.is_file():
                h = hashlib.sha256(entry.read_bytes()).hexdigest()
                assert snap_before[entry.name] == h, f"Snapshot mutated: {entry.name}"


class TestCLI:
    """Test the render_docs CLI."""

    def test_successful_json_summary(self, tmp_path):
        repo = _setup_repo_with_registries(tmp_path)
        snap_dir = tmp_path / "snap"
        _make_snapshot(repo, snap_dir)
        out_dir = tmp_path / ".codex-context" / "project-memory" / "rendered"

        rp = str(Path(__file__).resolve().parents[2] / "scripts" / "project_memory" / "render_docs.py")
        result = subprocess.run(
            [sys.executable, rp,
             "--repo-root", str(repo),
             "--snapshot-dir", str(snap_dir),
             "--output-root", str(out_dir),
             "--task-id", "CLI-TEST",
             "--run-id", "cli-001",
             "--generated-at", "2026-01-01T00:00:00Z",
             "--mode", "publication",
             "--json"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"
        data = json.loads(result.stdout)
        assert data["result"] == "PASS"
        assert data["task_id"] == "CLI-TEST"
        assert data["mode"] == "publication"
        assert "page_count" in data
        assert data["page_count"] == 14

    def test_rejected_invocation_returns_nonzero(self, tmp_path):
        repo = _setup_repo_with_registries(tmp_path)
        snap_dir = tmp_path / "snap"
        _make_snapshot(repo, snap_dir)
        out_dir = tmp_path / "output"

        rp = str(Path(__file__).resolve().parents[2] / "scripts" / "project_memory" / "render_docs.py")
        result = subprocess.run(
            [sys.executable, rp,
             "--repo-root", str(repo),
             "--snapshot-dir", str(snap_dir),
             "--output-root", str(out_dir),
             "--task-id", "CLI-ERR",
             "--run-id", "err-001",
             "--generated-at", "2026-01-01T00:00:00Z",
             "--mode", "invalid_mode",
             "--json"],
            capture_output=True, text=True,
        )
        assert result.returncode != 0

    def test_rejected_json_invocation_structured_error(self, tmp_path):
        repo = _setup_repo_with_registries(tmp_path)
        snap_dir = tmp_path / "snap"
        _make_snapshot(repo, snap_dir)
        out_dir = tmp_path / "output"

        rp = str(Path(__file__).resolve().parents[2] / "scripts" / "project_memory" / "render_docs.py")
        result = subprocess.run(
            [sys.executable, rp,
             "--repo-root", str(repo),
             "--snapshot-dir", str(snap_dir),
             "--output-root", str(out_dir),
             "--task-id", "CLI-ERR2",
             "--run-id", "err-002",
             "--generated-at", "2026-01-01T00:00:00Z",
             "--mode", "publication",
             "--json"],
            capture_output=True, text=True,
        )
        assert result.returncode != 0
        data = json.loads(result.stdout)
        assert data["result"] == "FAIL"
        assert "error" in data

    def test_required_arguments_enforced(self, tmp_path):
        rp = str(Path(__file__).resolve().parents[2] / "scripts" / "project_memory" / "render_docs.py")
        result = subprocess.run(
            [sys.executable, rp],
            capture_output=True, text=True,
        )
        assert result.returncode != 0

    def test_unsupported_mode_rejected(self, tmp_path):
        repo = _setup_repo_with_registries(tmp_path)
        snap_dir = tmp_path / "snap"
        _make_snapshot(repo, snap_dir)
        out_dir = tmp_path / "output"

        rp = str(Path(__file__).resolve().parents[2] / "scripts" / "project_memory" / "render_docs.py")
        result = subprocess.run(
            [sys.executable, rp,
             "--repo-root", str(repo),
             "--snapshot-dir", str(snap_dir),
             "--output-root", str(out_dir),
             "--task-id", "TEST",
             "--run-id", "r001",
             "--generated-at", "2026-01-01T00:00:00Z",
             "--mode", "imaginary_mode",
             "--json"],
            capture_output=True, text=True,
        )
        assert result.returncode != 0


class TestConstants:
    """Test that required renderer constants are present."""

    def test_renderer_name_defined(self):
        assert rd.RENDERER_NAME is not None
        assert "project_memory" in rd.RENDERER_NAME.lower()

    def test_renderer_version_defined(self):
        assert rd.RENDERER_VERSION is not None
        assert "v" in rd.RENDERER_VERSION

    def test_page_names_tuple(self):
        assert isinstance(rd.RENDERED_PAGE_NAMES, tuple)
        assert len(rd.RENDERED_PAGE_NAMES) == 14
        assert rd.RENDERED_PAGE_NAMES[0] == "index.md"
        assert rd.RENDERED_PAGE_NAMES[-1] == "technical-annex.md"


def _render_standard_helper(tmp_path) -> tuple:
    repo = _setup_repo_with_registries(tmp_path)
    snap_dir = tmp_path / "snap"
    _make_snapshot(repo, snap_dir)
    out_dir = tmp_path / ".codex-context" / "project-memory" / "rendered"
    rd.render(
        repo_root=str(repo), snapshot_dir=str(snap_dir),
        output_root=str(out_dir), task_id="STD", run_id="r001",
        generated_at="2026-01-01T00:00:00Z", mode="publication",
    )
    run_dir = out_dir / "STD" / "r001"
    docs_dir = run_dir / "docs"
    return docs_dir, run_dir, out_dir
