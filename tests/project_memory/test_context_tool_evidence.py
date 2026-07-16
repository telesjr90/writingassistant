"""Focused tests for read-only existing context-tool evidence import.

Artifact tests use temporary repositories and fixture-generated packages only.
No context collector is installed or executed.
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
from scripts.project_memory import context_tool_evidence as cte


CURRENT_SHA = "a" * 40
STALE_SHA = "b" * 40
REPO_ROOT = Path(__file__).resolve().parents[2]


def _write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _json(path: Path, data) -> Path:
    return _write(path, json.dumps(data, indent=2, sort_keys=True) + "\n")


def _make_repo(tmp_path: Path, *, with_outputs: bool = True) -> Path:
    repo = tmp_path
    _write(repo / ".git" / "HEAD", "ref: refs/heads/test-branch\n")
    _write(repo / ".git" / "refs" / "heads" / "test-branch", CURRENT_SHA + "\n")
    _write(repo / ".gitignore", ".codex-context/\nai_context/\ngraphify-out/\n")
    _write(repo / ".graphifyignore", "graphify-out/\n.codex-context/\nai_context/\n")
    _write(
        repo / "docs" / "roadmap" / "context_tool_policy.md",
        "Repomix uses ai_context. Graphify uses graphify-out. CCE uses .codex-context.\n",
    )
    _write(
        repo / "docs" / "roadmap" / "context_execution_standard.md",
        "Repomix generated evidence: ai_context/repomix-workspace-context.xml\n"
        "Graphify graph: graphify-out/graph.json\n"
        "CCE output: .codex-context/<TASK>/cce-findings.md\n",
    )
    _write(
        repo / "scripts" / "generate_ai_context.sh",
        "repomix --output ai_context/repomix-workspace-context.xml\n",
    )
    _write(
        repo / "scripts" / "roadmap_enrichment" / "tool_commands.md",
        "graphify query x --graph graphify-out/graph.json\n"
        "cce search x > .codex-context/TASK/cce-findings.md\n",
    )
    _json(
        repo / "repomix.config.json",
        {"output": {"filePath": "ai_context/repomix-workspace-context.xml"}},
    )
    _json(
        repo / "docs" / "project-memory" / "registries" / "tasks.json",
        {"registry_type": "task", "schema_version": "1.0.0", "records": []},
    )
    if with_outputs:
        (repo / ".codex-context").mkdir(exist_ok=True)
        (repo / "ai_context").mkdir(exist_ok=True)
        (repo / "graphify-out").mkdir(exist_ok=True)
    return repo


def _manifest(
    package: Path,
    tool: str,
    *,
    commit: str | None = CURRENT_SHA,
    branch: str | None = "test-branch",
    authority: str = "generated_evidence",
    historical: bool = False,
    include_scope: bool = True,
    checksum: str = "valid",
) -> Path:
    package.mkdir(parents=True, exist_ok=True)
    data = {
        "authority_class": authority,
        "generated_at": "2026-07-14T22:30:00Z",
        "generator": {"name": tool, "version": "1.2.3"},
        "repository_root": "/fixture/repository",
        "tool": {"identity": tool, "version": "1.2.3"},
    }
    if commit is not None:
        data["bound_commit"] = commit
    if branch is not None:
        data["branch"] = branch
    if historical:
        data["freshness_state"] = "historical"
    if include_scope:
        data["included_scopes"] = ["docs/roadmap"]
        data["exclusions"] = [".git", "node_modules", ".venv"]
    manifest = _json(package / "manifest.json", data)
    if checksum != "absent":
        digest = hashlib.sha256(manifest.read_bytes()).hexdigest()
        if checksum == "mismatch":
            digest = "0" * 64
        _write(package / "SHA256SUMS", f"{digest}  manifest.json\n")
    return package


def _descriptor(repo: Path, rel: str) -> dict:
    return next(item for item in cte.discover_context_artifacts(repo) if item["source_package_path"] == rel)


def _inspect(repo: Path, rel: str) -> dict:
    return cte.inspect_context_artifact(repo, _descriptor(repo, rel))


def _envelope(repo: Path, rel: str) -> dict:
    return cte.normalize_context_artifact(
        _inspect(repo, rel), current_branch="test-branch", current_commit=CURRENT_SHA,
    )


def _package_hashes(path: Path) -> dict[str, str]:
    return {
        item.name: hashlib.sha256(item.read_bytes()).hexdigest()
        for item in sorted(path.iterdir()) if item.is_file()
    }


class TestAttribution:
    def test_strong_repomix_attribution_from_tracked_output_convention(self, tmp_path):
        repo = _make_repo(tmp_path)
        _write(repo / "ai_context" / "repomix-workspace-context.xml", "<file_summary>fixture</file_summary>\n")
        inspected = _inspect(repo, "ai_context/repomix-workspace-context.xml")
        assert inspected["tool_identity"] == "repomix"
        assert inspected["attribution"] == "strong"

    def test_strong_graphify_attribution(self, tmp_path):
        repo = _make_repo(tmp_path)
        _manifest(repo / "graphify-out", "Graphify")
        _json(repo / "graphify-out" / "graph.json", {"nodes": []})
        inspected = _inspect(repo, "graphify-out")
        assert inspected["tool_identity"] == "graphify"
        assert inspected["attribution"] == "strong"

    def test_strong_cce_attribution(self, tmp_path):
        repo = _make_repo(tmp_path)
        package = _manifest(repo / ".codex-context" / "TASK", "CCE")
        _write(package / "cce-findings.md", "bounded fixture summary\n")
        inspected = _inspect(repo, ".codex-context/TASK")
        assert inspected["tool_identity"] == "cce"
        assert inspected["attribution"] == "strong"

    def test_filename_only_attribution_is_rejected(self, tmp_path):
        repo = _make_repo(tmp_path)
        _write(repo / "ai_context" / "cce-results.md", "no metadata\n")
        inspected = _inspect(repo, "ai_context/cce-results.md")
        assert inspected["tool_identity"] == cte.UNKNOWN_TOOL
        assert inspected["attribution"] == "unknown"

    def test_ambiguous_attribution_is_quarantined(self, tmp_path):
        repo = _make_repo(tmp_path)
        package = _manifest(repo / ".codex-context" / "MIXED", "Repomix")
        _write(package / "commands.txt", "repomix --output pack.xml\ncce search query\n")
        envelope = _envelope(repo, ".codex-context/MIXED")
        assert envelope["tool"]["identity"] == cte.UNKNOWN_TOOL
        assert "ambiguous_tool_origin" in envelope["consumption"]["quarantine_reasons"]


class TestFreshnessAndEligibility:
    def test_current_is_eligible_when_all_requirements_pass(self, tmp_path):
        repo = _make_repo(tmp_path)
        _manifest(repo / ".codex-context" / "CURRENT", "Repomix")
        envelope = _envelope(repo, ".codex-context/CURRENT")
        assert envelope["freshness"] == "current"
        assert envelope["consumption"]["default_eligible"] is True

    def test_stale_commit_is_quarantined(self, tmp_path):
        repo = _make_repo(tmp_path)
        _manifest(repo / ".codex-context" / "STALE", "Graphify", commit=STALE_SHA)
        envelope = _envelope(repo, ".codex-context/STALE")
        assert envelope["freshness"] == "stale"
        assert envelope["consumption"]["default_eligible"] is False

    def test_historical_is_preserved_and_quarantined(self, tmp_path):
        repo = _make_repo(tmp_path)
        _manifest(repo / ".codex-context" / "HISTORY", "CCE", historical=True)
        envelope = _envelope(repo, ".codex-context/HISTORY")
        assert envelope["freshness"] == "historical"
        assert envelope["consumption"]["default_eligible"] is False

    def test_unknown_when_commit_is_absent(self, tmp_path):
        repo = _make_repo(tmp_path)
        _manifest(repo / ".codex-context" / "UNKNOWN", "CCE", commit=None)
        assert _envelope(repo, ".codex-context/UNKNOWN")["freshness"] == "unknown"

    def test_unknown_when_branch_is_absent(self, tmp_path):
        repo = _make_repo(tmp_path)
        _manifest(repo / ".codex-context" / "UNKNOWN", "CCE", branch=None)
        assert _envelope(repo, ".codex-context/UNKNOWN")["freshness"] == "unknown"

    def test_branch_mismatch_with_current_commit_is_unusable(self, tmp_path):
        repo = _make_repo(tmp_path)
        _manifest(repo / ".codex-context" / "BRANCH", "CCE", branch="other")
        assert _envelope(repo, ".codex-context/BRANCH")["freshness"] == "unusable"

    def test_commit_and_branch_mismatch_remains_stale(self, tmp_path):
        repo = _make_repo(tmp_path)
        _manifest(repo / ".codex-context" / "BOTH", "CCE", commit=STALE_SHA, branch="other")
        envelope = _envelope(repo, ".codex-context/BOTH")
        assert envelope["freshness"] == "stale"
        assert "branch_mismatch" in envelope["consumption"]["quarantine_reasons"]

    def test_unbounded_scope_is_quarantined(self, tmp_path):
        repo = _make_repo(tmp_path)
        _manifest(repo / ".codex-context" / "SCOPE", "CCE", include_scope=False)
        envelope = _envelope(repo, ".codex-context/SCOPE")
        assert envelope["scope_bounded"] is False
        assert "scope_unbounded" in envelope["consumption"]["quarantine_reasons"]

    def test_read_import_approval_is_separate_from_execution(self, tmp_path):
        repo = _make_repo(tmp_path)
        _manifest(repo / ".codex-context" / "CURRENT", "CCE")
        envelope = _envelope(repo, ".codex-context/CURRENT")
        assert envelope["consumption"]["read_import_approved"] is True
        assert envelope["consumption"]["live_execution_approved"] is False


class TestChecksumsAndAuthority:
    def test_checksum_success(self, tmp_path):
        repo = _make_repo(tmp_path)
        _manifest(repo / ".codex-context" / "GOOD", "CCE")
        assert _inspect(repo, ".codex-context/GOOD")["checksum_status"] == "valid"

    def test_checksum_absence_is_reported_but_not_required(self, tmp_path):
        repo = _make_repo(tmp_path)
        _manifest(repo / ".codex-context" / "NONE", "CCE", checksum="absent")
        envelope = _envelope(repo, ".codex-context/NONE")
        assert envelope["provenance"]["checksum_status"] == "absent"
        assert envelope["consumption"]["default_eligible"] is True

    def test_checksum_mismatch_is_unusable(self, tmp_path):
        repo = _make_repo(tmp_path)
        _manifest(repo / ".codex-context" / "BAD", "CCE", checksum="mismatch")
        envelope = _envelope(repo, ".codex-context/BAD")
        assert envelope["freshness"] == "unusable"
        assert "checksum_mismatch" in envelope["consumption"]["quarantine_reasons"]

    def test_envelope_authority_is_generated_evidence(self, tmp_path):
        repo = _make_repo(tmp_path)
        _manifest(repo / ".codex-context" / "AUTH", "CCE")
        envelope = _envelope(repo, ".codex-context/AUTH")
        assert envelope["authority_class"] == "generated_evidence"
        assert envelope["trust_class"] == "generated_evidence"

    def test_authority_self_claim_is_rejected(self, tmp_path):
        repo = _make_repo(tmp_path)
        _manifest(repo / ".codex-context" / "AUTH", "CCE", authority="authoritative")
        envelope = _envelope(repo, ".codex-context/AUTH")
        assert envelope["freshness"] == "unusable"
        assert "authority_self_claim" in envelope["consumption"]["quarantine_reasons"]

    def test_text_authority_self_claim_is_rejected(self, tmp_path):
        repo = _make_repo(tmp_path)
        package = repo / ".codex-context" / "AUTH-TEXT"
        package.mkdir()
        _write(
            package / "summary.md",
            "tool: CCE\nauthority_class: authoritative\nbound_commit: " + CURRENT_SHA + "\nbranch: test-branch\n",
        )
        envelope = _envelope(repo, ".codex-context/AUTH-TEXT")
        assert envelope["freshness"] == "unusable"
        assert "authority_self_claim" in envelope["consumption"]["quarantine_reasons"]


class TestPathAndContentSafety:
    @pytest.mark.parametrize("value", ["../escape", "/tmp/external"])
    def test_traversal_and_absolute_paths_rejected(self, tmp_path, value):
        repo = _make_repo(tmp_path)
        inspected = cte.inspect_context_artifact(repo, value)
        assert inspected["findings"][0]["code"] == "unsafe_source_path"

    def test_symlink_escape_is_quarantined(self, tmp_path):
        repo = _make_repo(tmp_path)
        outside = _write(tmp_path.parent / "external-context", "secret\n")
        (repo / "ai_context" / "escape").symlink_to(outside)
        envelope = _envelope(repo, "ai_context/escape")
        assert envelope["safety"] == "unsafe"
        assert envelope["consumption"]["default_eligible"] is False

    def test_special_file_is_quarantined(self, tmp_path):
        repo = _make_repo(tmp_path)
        package = _manifest(repo / ".codex-context" / "FIFO", "CCE")
        os.mkfifo(package / "pipe")
        envelope = _envelope(repo, ".codex-context/FIFO")
        assert envelope["safety"] == "unsafe"
        assert "special_file" in envelope["consumption"]["quarantine_reasons"]

    @pytest.mark.parametrize(
        "rel",
        [".env", "credentials.json", "node_modules/a.js", ".venv/lib/a.py", "cache/data.json", "model.gguf", "dataset.jsonl"],
    )
    def test_sensitive_and_excluded_content_is_quarantined(self, tmp_path, rel):
        repo = _make_repo(tmp_path)
        package = _manifest(repo / ".codex-context" / "UNSAFE", "CCE")
        _write(package / rel, "fixture\n")
        envelope = _envelope(repo, ".codex-context/UNSAFE")
        assert envelope["consumption"]["default_eligible"] is False
        assert "excluded_or_sensitive_path" in envelope["consumption"]["quarantine_reasons"]

    def test_oversized_metadata_is_quarantined(self, tmp_path, monkeypatch):
        repo = _make_repo(tmp_path)
        package = repo / ".codex-context" / "LARGE"
        package.mkdir()
        monkeypatch.setattr(cte, "MAX_METADATA_BYTES", 64)
        _write(package / "manifest.json", "{" + (" " * 100) + "}")
        envelope = _envelope(repo, ".codex-context/LARGE")
        assert "malformed_or_oversized_metadata" in envelope["consumption"]["quarantine_reasons"]


class TestPackageBuild:
    def test_linked_worktree_git_identity_uses_common_dir(self, tmp_path):
        repo = tmp_path / "worktree"
        admin = tmp_path / "admin"
        repo.mkdir()
        _write(repo / ".git", "gitdir: ../admin/worktrees/worktree\n")
        _write(admin / "worktrees" / "worktree" / "HEAD", "ref: refs/heads/test-branch\n")
        _write(admin / "worktrees" / "worktree" / "commondir", "../..\n")
        _write(admin / "refs" / "heads" / "test-branch", CURRENT_SHA + "\n")
        assert cte._read_git_identity(repo) == ("test-branch", CURRENT_SHA)

    def test_empty_root_package_has_exact_inventory(self, tmp_path):
        repo = _make_repo(tmp_path, with_outputs=False)
        result = cte.build_context_evidence_package(
            repo, ".codex-context/project-memory", "PHASE8-IMPL-026-T005", "20260714T230000Z",
        )
        run_dir = Path(result["output_directory"])
        assert result["artifact_count"] == 0
        assert sorted(item.name for item in run_dir.iterdir()) == list(cte.EXACT_PACKAGE_FILES)
        assert cte.validate_context_evidence_package(run_dir)["result"] == "PASS"

    def test_package_records_false_execution_network_model_and_registry_flags(self, tmp_path):
        repo = _make_repo(tmp_path)
        result = cte.build_context_evidence_package(
            repo, ".codex-context/project-memory", "PHASE8-IMPL-026-T005", "20260714T230001Z",
        )
        metadata = json.loads((Path(result["output_directory"]) / "run-metadata.json").read_text())
        assert metadata["tool_execution_performed"] is False
        assert metadata["network_access_performed"] is False
        assert metadata["model_call_performed"] is False
        assert metadata["registry_mutation_performed"] is False

    def test_one_envelope_per_discovered_artifact(self, tmp_path):
        repo = _make_repo(tmp_path)
        _manifest(repo / ".codex-context" / "ONE", "CCE")
        _write(repo / "ai_context" / "unknown.txt", "unknown\n")
        result = cte.build_context_evidence_package(
            repo, ".codex-context/project-memory", "PHASE8-IMPL-026-T005", "20260714T230002Z",
        )
        run_dir = Path(result["output_directory"])
        envelopes = json.loads((run_dir / "artifact-envelopes.json").read_text())["artifacts"]
        inventory = json.loads((run_dir / "artifact-inventory.json").read_text())["artifacts"]
        assert len(envelopes) == len(inventory) == 3  # CCE, unknown, empty graphify root

    def test_deterministic_byte_identical_output(self, tmp_path):
        repo = _make_repo(tmp_path)
        _manifest(repo / ".codex-context" / "ONE", "CCE")
        result = cte.build_context_evidence_package(
            repo, ".codex-context/project-memory", "PHASE8-IMPL-026-T005", "20260714T230003Z",
        )
        run_dir = Path(result["output_directory"])
        first = _package_hashes(run_dir)
        shutil.rmtree(run_dir)
        second_result = cte.build_context_evidence_package(
            repo, ".codex-context/project-memory", "PHASE8-IMPL-026-T005", "20260714T230003Z",
        )
        assert first == _package_hashes(Path(second_result["output_directory"]))

    def test_overwrite_refusal(self, tmp_path):
        repo = _make_repo(tmp_path)
        args = (repo, ".codex-context/project-memory", "PHASE8-IMPL-026-T005", "20260714T230004Z")
        cte.build_context_evidence_package(*args)
        with pytest.raises(FileExistsError):
            cte.build_context_evidence_package(*args)

    def test_atomic_cleanup_on_failure(self, tmp_path, monkeypatch):
        repo = _make_repo(tmp_path)
        monkeypatch.setattr(cte.os, "rename", lambda *_: (_ for _ in ()).throw(OSError("fixture failure")))
        with pytest.raises(OSError, match="fixture failure"):
            cte.build_context_evidence_package(
                repo, ".codex-context/project-memory", "PHASE8-IMPL-026-T005", "20260714T230005Z",
            )
        assert not list((repo / ".codex-context").glob("context_evidence_*"))
        assert not (repo / ".codex-context" / "project-memory" / "PHASE8-IMPL-026-T005" / "20260714T230005Z").exists()

    def test_source_artifact_and_registry_immutability(self, tmp_path):
        repo = _make_repo(tmp_path)
        package = _manifest(repo / ".codex-context" / "ONE", "CCE")
        registry = repo / "docs" / "project-memory" / "registries" / "tasks.json"
        before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in (package / "manifest.json", registry)}
        cte.build_context_evidence_package(
            repo, ".codex-context/project-memory", "PHASE8-IMPL-026-T005", "20260714T230006Z",
        )
        after = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in (package / "manifest.json", registry)}
        assert before == after

    def test_module_has_no_subprocess_network_or_model_execution(self):
        source = Path(cte.__file__).read_text(encoding="utf-8")
        assert "import subprocess" not in source
        assert "import socket" not in source
        assert "import urllib" not in source
        assert "import requests" not in source
        assert "ollama" not in source.lower()

    def test_cli_json_output(self, tmp_path):
        repo = _make_repo(tmp_path)
        cli = REPO_ROOT / "scripts" / "project_memory" / "build_context_tool_evidence.py"
        completed = subprocess.run(
            [sys.executable, str(cli), "--repo-root", str(repo),
             "--output-root", ".codex-context/project-memory",
             "--task-id", "PHASE8-IMPL-026-T005", "--run-id", "20260714T230007Z", "--json"],
            capture_output=True, text=True, check=False,
        )
        assert completed.returncode == 0, completed.stderr
        data = json.loads(completed.stdout)
        assert data["result"] in {"PASS", "PASS_WITH_FINDINGS"}
        assert data["tool_execution_performed"] is False


class TestRoadmapPreservation:
    def test_t006_and_t007_remain_contingent_and_inactive(self):
        text = (REPO_ROOT / "docs" / "roadmap" / "tasks" / "PHASE8-IMPL-026.md").read_text()
        assert "T006" in text and "Contingent on Serena" in text
        assert "T007" in text and "Contingent on provenance" in text

    def test_application_frontier_is_preserved(self):
        text = (REPO_ROOT / "docs" / "roadmap" / "implementation_status.md").read_text()
        assert "PHASE8-IMPL-024-T003B" in text

    def test_ph8_impl_025_remains_published_planned_and_inactive(self):
        tasks = json.loads((REPO_ROOT / "docs" / "project-memory" / "registries" / "tasks.json").read_text())
        record = next(item for item in tasks["records"] if item["task_id"] == "PHASE8-IMPL-025")
        assert record["lifecycle"]["status"] == "planned"
        assert "inactive" in record["notes"].lower()
