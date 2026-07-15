"""Semantic rendered-documentation validator tests.

All tests use temporary directories and must not mutate the real repository.
"""

from __future__ import annotations

import json
import hashlib
import importlib
import shutil
import subprocess
import uuid
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.project_memory.validate_rendered_docs import (
    _bootstrap_direct_execution_import_path,
    analyze_authority_claims,
    main,
    validate_rendered_package,
    derive_expected_task_states,
    RESULT_PASS,
    RESULT_PASS_WITH_FINDINGS,
    RESULT_BLOCKED,
    RENDERED_PAGE_NAMES,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_SCRIPT = REPO_ROOT / "scripts/project_memory/validate_rendered_docs.py"
PRESERVED_T004C1_SNAPSHOT = REPO_ROOT / ".codex-context/project-memory/PHASE8-IMPL-026-T004C1/20260714T213628Z"
PRESERVED_T004C1_RENDER = REPO_ROOT / ".codex-context/project-memory/rendered/PHASE8-IMPL-026-T004C1/20260714T213628Z"


def _make_task_record(task_id, status, parent=None, notes=""):
    return {
        "id": f"task:{task_id}",
        "type": "task",
        "schema_version": "1.0.0",
        "title": f"Task {task_id}",
        "authority_class": "authoritative",
        "lifecycle": {"status": status},
        "provenance": {"created_by": task_id},
        "task_id": task_id,
        "parent_task_id": parent,
        "depends_on": [],
        "task_type": "infrastructure",
        "is_application_frontier": False,
        "is_blocking": False,
        "notes": notes,
    }


def _make_minimal_render_dir(base: Path, pages: dict[str, str]) -> Path:
    """Create a minimal render package structure."""
    render_dir = base / "render_out"
    docs_dir = render_dir / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    banner = "# Generated Evidence — Not Project Authority\n\n"
    for name in RENDERED_PAGE_NAMES:
        content = pages.get(name, banner)
        if "Generated Evidence" not in content:
            content = banner + content
        (docs_dir / name).write_text(content, encoding="utf-8")

    manifest = {
        "renderer_name": "project_memory_markdown_renderer",
        "renderer_version": "project_memory_markdown_renderer.v1",
        "authority_class": "generated_evidence",
        "mode": "publication",
        "target_commit": "a415270b18f978e601a9ffc6d7bcb4ab8a250c42",
        "target_branch": "docs/project-memory-foundation",
        "source_snapshot_bound_commit": "a415270b18f978e601a9ffc6d7bcb4ab8a250c42",
        "freshness": "current",
        "publication_eligible": True,
        "convergence_result": "PASS_WITH_FINDINGS",
        "page_count": 14,
        "page_navigation_order": list(RENDERED_PAGE_NAMES),
        "page_hashes": {},
    }
    (render_dir / "build-manifest.json").write_text(json.dumps(manifest, sort_keys=True))
    (render_dir / "source-snapshot.json").write_text(
        json.dumps({"bound_commit": "a415270b18f978e601a9ffc6d7bcb4ab8a250c42",
                      "branch": "docs/project-memory-foundation",
                      "authority_class": "generated_evidence"}, sort_keys=True))
    (render_dir / "FILE-INVENTORY.txt").write_text("docs/index.md\n")
    (render_dir / "SHA256SUMS").write_text("")
    return render_dir


class TestDirectExecutionBootstrap:

    @staticmethod
    def _direct_command(repo_root: Path, snapshot_dir: Path, render_dir: Path) -> list[str]:
        return [
            sys.executable,
            str(VALIDATOR_SCRIPT),
            "--repo-root", str(repo_root),
            "--snapshot-dir", str(snapshot_dir),
            "--render-dir", str(render_dir),
            "--json",
        ]

    def test_direct_cli_from_repository_root_returns_valid_json(self):
        result = subprocess.run(
            self._direct_command(
                REPO_ROOT, PRESERVED_T004C1_SNAPSHOT, PRESERVED_T004C1_RENDER
            ),
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr
        report = json.loads(result.stdout)
        assert report["result"] == RESULT_PASS_WITH_FINDINGS
        assert report["authority_check"] == "pass"
        assert report["authority"]["forbidden_claims"] == []
        assert all(check["result"] == "pass" for check in report["semantic_checks"])

    def test_direct_cli_outside_repository_uses_explicit_repo_root(self, tmp_path):
        result = subprocess.run(
            self._direct_command(
                REPO_ROOT, PRESERVED_T004C1_SNAPSHOT, PRESERVED_T004C1_RENDER
            ),
            cwd=tmp_path,
            check=False,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr
        assert json.loads(result.stdout)["result"] == RESULT_PASS_WITH_FINDINGS

    def test_module_import_remains_available(self):
        module = importlib.import_module("scripts.project_memory.validate_rendered_docs")
        assert module.validate_rendered_package is validate_rendered_package

    @pytest.mark.parametrize(
        ("validation_result", "expected_exit"),
        [
            (RESULT_PASS, 0),
            (RESULT_PASS_WITH_FINDINGS, 0),
            (RESULT_BLOCKED, 1),
        ],
    )
    def test_main_preserves_result_exit_codes(
        self, monkeypatch, capsys, validation_result, expected_exit
    ):
        monkeypatch.setattr(
            "scripts.project_memory.validate_rendered_docs.validate_rendered_package",
            lambda **_kwargs: {
                "result": validation_result,
                "errors": ["blocked"] if validation_result == RESULT_BLOCKED else [],
                "warnings": [],
            },
        )
        monkeypatch.setattr(
            sys,
            "argv",
            [
                str(VALIDATOR_SCRIPT),
                "--repo-root", ".",
                "--snapshot-dir", "snapshot",
                "--render-dir", "render",
                "--json",
            ],
        )
        assert main() == expected_exit
        assert json.loads(capsys.readouterr().out)["result"] == validation_result

    def test_direct_cli_invalid_arguments_fail_normally(self, tmp_path):
        result = subprocess.run(
            [sys.executable, str(VALIDATOR_SCRIPT)],
            cwd=tmp_path,
            check=False,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 2
        assert "required" in result.stderr

    def test_bootstrap_does_not_duplicate_repository_root(self, monkeypatch):
        repository_root = str(REPO_ROOT)
        monkeypatch.setattr(
            "scripts.project_memory.validate_rendered_docs.__package__", ""
        )
        monkeypatch.setattr(sys, "path", [repository_root, "sentinel"])
        _bootstrap_direct_execution_import_path()
        _bootstrap_direct_execution_import_path()
        assert sys.path.count(repository_root) == 1


class TestDeriveExpectedTaskStates:

    def test_t004_is_complete(self):
        tasks = [_make_task_record("PHASE8-IMPL-026-T004", "complete",
                                   parent="PHASE8-IMPL-026",
                                   notes="Complete/PASS-WITH-FINDINGS.")]
        states = derive_expected_task_states(tasks)
        t4 = states.get("PHASE8-IMPL-026-T004", {})
        assert t4.get("is_complete") is True
        assert t4.get("lifecycle") == "complete"

    def test_t004c_is_complete(self):
        tasks = [_make_task_record("PHASE8-IMPL-026-T004C", "complete",
                                   parent="PHASE8-IMPL-026-T004",
                                   notes="Complete/PASS-WITH-FINDINGS.")]
        states = derive_expected_task_states(tasks)
        t4c = states.get("PHASE8-IMPL-026-T004C", {})
        assert t4c.get("is_complete") is True
        assert t4c.get("lifecycle") == "complete"

    def test_t005_is_planned(self):
        tasks = [_make_task_record("PHASE8-IMPL-026-T005", "planned",
                                   parent="PHASE8-IMPL-026",
                                   notes="Planned next. Inactive.")]
        states = derive_expected_task_states(tasks)
        t5 = states.get("PHASE8-IMPL-026-T005", {})
        assert t5.get("is_planned") is True
        assert t5.get("is_complete") is False

    def test_next_task_is_t005_when_all_others_complete(self):
        tasks = [
            _make_task_record("PHASE8-IMPL-026", "in_progress", None),
            _make_task_record("PHASE8-IMPL-026-T001", "complete", "PHASE8-IMPL-026"),
            _make_task_record("PHASE8-IMPL-026-T002", "complete", "PHASE8-IMPL-026"),
            _make_task_record("PHASE8-IMPL-026-T003", "complete", "PHASE8-IMPL-026"),
            _make_task_record("PHASE8-IMPL-026-T004", "complete", "PHASE8-IMPL-026"),
            _make_task_record("PHASE8-IMPL-026-T005", "planned", "PHASE8-IMPL-026"),
        ]
        states = derive_expected_task_states(tasks)
        nt = states.get("_pm_next_task", {})
        assert nt.get("task_id") == "PHASE8-IMPL-026-T005"

    def test_no_next_when_all_complete(self):
        tasks = [
            _make_task_record("PHASE8-IMPL-026", "complete", None),
            _make_task_record("PHASE8-IMPL-026-T001", "complete", "PHASE8-IMPL-026"),
            _make_task_record("PHASE8-IMPL-026-T005", "complete", "PHASE8-IMPL-026"),
        ]
        states = derive_expected_task_states(tasks)
        nt = states.get("_pm_next_task", {})
        assert nt.get("task_id") is None


class TestSemanticValidation:

    def _reg_with_tasks(self, tasks):
        return {"tasks.json": {"registry_type": "task", "schema_version": "1.0.0",
                                "records": tasks}}

    def _page(self, text):
        d = {}
        for p in RENDERED_PAGE_NAMES:
            d[p] = ""
        d["index.md"] = text
        d["current-roadmap.md"] = text
        d["remaining-work.md"] = ""
        return d

    def _page_set(self, index="", roadmap="", remaining=""):
        d = {}
        for p in RENDERED_PAGE_NAMES:
            d[p] = ""
        d["index.md"] = index
        d["current-roadmap.md"] = roadmap
        d["remaining-work.md"] = remaining
        return d

    def test_rejects_t004_in_progress(self, tmp_path):
        tasks = [
            _make_task_record("PHASE8-IMPL-026-T004", "complete", "PHASE8-IMPL-026",
                              notes="Complete/PASS-WITH-FINDINGS."),
        ]
        registries = self._reg_with_tasks(tasks)
        pages = self._page_set(
            index="| T004 (Human-readable memory) | in progress |",
            roadmap="T004\n",
        )
        render_dir = _make_minimal_render_dir(tmp_path, pages)
        result = validate_rendered_package(
            repo_root=str(tmp_path),
            snapshot_dir=str(tmp_path),
            render_dir=str(render_dir),
            registries=registries,
        )
        assert result["result"] == RESULT_BLOCKED

    def test_rejects_t004c_planned(self, tmp_path):
        tasks = [
            _make_task_record("PHASE8-IMPL-026-T004C", "complete", "PHASE8-IMPL-026-T004",
                              notes="Complete/PASS-WITH-FINDINGS."),
        ]
        registries = self._reg_with_tasks(tasks)
        pages = self._page_set(
            index="| T004C (Clean-HEAD publication) | planned |",
            roadmap="T004C\n",
        )
        render_dir = _make_minimal_render_dir(tmp_path, pages)
        result = validate_rendered_package(
            repo_root=str(tmp_path),
            snapshot_dir=str(tmp_path),
            render_dir=str(render_dir),
            registries=registries,
        )
        assert result["result"] == RESULT_BLOCKED

    def test_rejects_t004b_as_current_child(self, tmp_path):
        tasks = [
            _make_task_record("PHASE8-IMPL-026-T004B", "complete", "PHASE8-IMPL-026-T004"),
            _make_task_record("PHASE8-IMPL-026-T005", "planned", "PHASE8-IMPL-026"),
        ]
        registries = self._reg_with_tasks(tasks)
        pages = self._page_set(
            roadmap="Current Project Memory child: T004B",
        )
        render_dir = _make_minimal_render_dir(tmp_path, pages)
        result = validate_rendered_package(
            repo_root=str(tmp_path),
            snapshot_dir=str(tmp_path),
            render_dir=str(render_dir),
            registries=registries,
        )
        assert result["result"] == RESULT_BLOCKED

    def test_rejects_t004_in_remaining_work(self, tmp_path):
        tasks = [
            _make_task_record("PHASE8-IMPL-026-T004", "complete", "PHASE8-IMPL-026",
                              notes="Complete/PASS-WITH-FINDINGS."),
        ]
        registries = self._reg_with_tasks(tasks)
        pages = self._page_set(
            remaining="- **T004** (`task:PHASE8-IMPL-026-T004`) — PHASE8-IMPL-026-T004",
        )
        render_dir = _make_minimal_render_dir(tmp_path, pages)
        result = validate_rendered_package(
            repo_root=str(tmp_path),
            snapshot_dir=str(tmp_path),
            render_dir=str(render_dir),
            registries=registries,
        )
        assert result["result"] == RESULT_BLOCKED

    def test_rejects_missing_t005_from_remaining(self, tmp_path):
        tasks = [
            _make_task_record("PHASE8-IMPL-026-T004", "complete", "PHASE8-IMPL-026",
                              notes="Complete/PASS-WITH-FINDINGS."),
            _make_task_record("PHASE8-IMPL-026-T005", "planned", "PHASE8-IMPL-026",
                              notes="Planned next. Inactive."),
        ]
        registries = self._reg_with_tasks(tasks)
        pages = self._page_set(
            remaining="## Remaining Work\n\n### Planned\n\n- **Other task**\n",
        )
        render_dir = _make_minimal_render_dir(tmp_path, pages)
        result = validate_rendered_package(
            repo_root=str(tmp_path),
            snapshot_dir=str(tmp_path),
            render_dir=str(render_dir),
            registries=registries,
        )
        assert result["result"] == RESULT_BLOCKED

    def test_rejects_t005_active_or_complete(self, tmp_path):
        tasks = [
            _make_task_record("PHASE8-IMPL-026-T005", "planned", "PHASE8-IMPL-026",
                              notes="Planned next. Inactive."),
        ]
        registries = self._reg_with_tasks(tasks)
        pages = self._page_set(
            index="T005 complete/PASS",
            roadmap="T005 (Context-tool integration) active",
        )
        render_dir = _make_minimal_render_dir(tmp_path, pages)
        result = validate_rendered_package(
            repo_root=str(tmp_path),
            snapshot_dir=str(tmp_path),
            render_dir=str(render_dir),
            registries=registries,
        )
        assert result["result"] == RESULT_BLOCKED

    def test_rejects_app_frontier_drift(self, tmp_path):
        tasks = [
            _make_task_record("PHASE8-IMPL-024-T003A", "planned", "PHASE8-IMPL-024"),
        ]
        registries = self._reg_with_tasks(tasks)
        pages = self._page_set(
            roadmap="Application frontier: PHASE8-IMPL-025-T001",
        )
        render_dir = _make_minimal_render_dir(tmp_path, pages)
        result = validate_rendered_package(
            repo_root=str(tmp_path),
            snapshot_dir=str(tmp_path),
            render_dir=str(render_dir),
            registries=registries,
        )
        assert result["result"] == RESULT_BLOCKED

    def test_rejects_ph25_activation(self, tmp_path):
        tasks = [
            _make_task_record("PHASE8-IMPL-025", "in_progress", None,
                              notes="Activated."),
        ]
        registries = self._reg_with_tasks(tasks)
        pages = self._page_set(
            roadmap="PHASE8-IMPL-025 active",
        )
        render_dir = _make_minimal_render_dir(tmp_path, pages)
        result = validate_rendered_package(
            repo_root=str(tmp_path),
            snapshot_dir=str(tmp_path),
            render_dir=str(render_dir),
            registries=registries,
        )
        assert result["result"] == RESULT_BLOCKED

    def test_accepts_correct_render(self, tmp_path):
        tasks = [
            _make_task_record("PHASE8-IMPL-026", "in_progress", None),
            _make_task_record("PHASE8-IMPL-026-T001", "complete", "PHASE8-IMPL-026"),
            _make_task_record("PHASE8-IMPL-026-T002", "complete", "PHASE8-IMPL-026"),
            _make_task_record("PHASE8-IMPL-026-T003", "complete", "PHASE8-IMPL-026"),
            _make_task_record("PHASE8-IMPL-026-T004", "complete", "PHASE8-IMPL-026",
                              notes="Complete/PASS-WITH-FINDINGS."),
            _make_task_record("PHASE8-IMPL-026-T004A", "complete", "PHASE8-IMPL-026-T004",
                              notes="Complete/PASS-WITH-FINDINGS."),
            _make_task_record("PHASE8-IMPL-026-T004B", "complete", "PHASE8-IMPL-026-T004",
                              notes="Complete/PASS."),
            _make_task_record("PHASE8-IMPL-026-T004C", "complete", "PHASE8-IMPL-026-T004",
                              notes="Complete/PASS-WITH-FINDINGS."),
            _make_task_record("PHASE8-IMPL-026-T005", "planned", "PHASE8-IMPL-026",
                              notes="Planned next. Inactive."),
        ]
        registries = self._reg_with_tasks(tasks)
        pages = self._page_set(
            index="""## Project Memory Workstream Status

| T004 (Human-readable memory) | complete/PASS-WITH-FINDINGS |
| T004A (Architecture/remediation) | complete/PASS-WITH-FINDINGS |
| T004C (Clean-HEAD publication) | complete/PASS-WITH-FINDINGS |
| T005 (Context-tool integration) | planned/inactive |

PHASE8-IMPL-024-T003A
""",
            roadmap="""PHASE8-IMPL-024-T003A
**Next actionable Project Memory task:** T005 (planned/inactive)
PHASE8-IMPL-025: published/planned, inactive""",
            remaining="""### Planned

- **T005** — PHASE8-IMPL-026-T005""",
        )
        render_dir = _make_minimal_render_dir(tmp_path, pages)
        result = validate_rendered_package(
            repo_root=str(tmp_path),
            snapshot_dir=str(tmp_path),
            render_dir=str(render_dir),
            registries=registries,
        )
        assert result["result"] in (RESULT_PASS, RESULT_PASS_WITH_FINDINGS)

    def test_duplicate_task_ids_fail_closed(self, tmp_path):
        tasks = [
            _make_task_record("PHASE8-IMPL-026-T004", "complete", "PHASE8-IMPL-026"),
            _make_task_record("PHASE8-IMPL-026-T004", "complete", "PHASE8-IMPL-026"),
        ]
        registries = self._reg_with_tasks(tasks)
        pages = self._page_set(index="empty")
        render_dir = _make_minimal_render_dir(tmp_path, pages)
        result = validate_rendered_package(
            repo_root=str(tmp_path),
            snapshot_dir=str(tmp_path),
            render_dir=str(render_dir),
            registries=registries,
        )
        assert result["result"] == RESULT_BLOCKED

    def test_missing_t004_fails_closed(self, tmp_path):
        tasks = []
        registries = self._reg_with_tasks(tasks)
        pages = self._page_set(index="empty")
        render_dir = _make_minimal_render_dir(tmp_path, pages)
        result = validate_rendered_package(
            repo_root=str(tmp_path),
            snapshot_dir=str(tmp_path),
            render_dir=str(render_dir),
            registries=registries,
        )
        assert result["result"] == RESULT_BLOCKED

    def test_missing_t005_fails_closed(self, tmp_path):
        tasks = [
            _make_task_record("PHASE8-IMPL-026-T001", "complete", "PHASE8-IMPL-026"),
            _make_task_record("PHASE8-IMPL-026-T002", "complete", "PHASE8-IMPL-026"),
            _make_task_record("PHASE8-IMPL-026-T003", "complete", "PHASE8-IMPL-026"),
            _make_task_record("PHASE8-IMPL-026-T004", "complete", "PHASE8-IMPL-026"),
            _make_task_record("PHASE8-IMPL-026-T004A", "complete", "PHASE8-IMPL-026-T004"),
            _make_task_record("PHASE8-IMPL-026-T004B", "complete", "PHASE8-IMPL-026-T004"),
            _make_task_record("PHASE8-IMPL-026-T004C", "complete", "PHASE8-IMPL-026-T004"),
        ]
        registries = self._reg_with_tasks(tasks)
        pages = self._page_set(index="empty")
        render_dir = _make_minimal_render_dir(tmp_path, pages)
        result = validate_rendered_package(
            repo_root=str(tmp_path),
            snapshot_dir=str(tmp_path),
            render_dir=str(render_dir),
            registries=registries,
        )
        assert result["result"] == RESULT_BLOCKED

    def test_contradictory_parent_refs_fail_closed(self, tmp_path):
        tasks = [
            _make_task_record("PHASE8-IMPL-026-T004A", "complete",
                              parent="PHASE8-IMPL-026",
                              notes="Complete/PASS-WITH-FINDINGS."),
        ]
        registries = self._reg_with_tasks(tasks)
        pages = self._page_set(index="")
        render_dir = _make_minimal_render_dir(tmp_path, pages)
        result = validate_rendered_package(
            repo_root=str(tmp_path),
            snapshot_dir=str(tmp_path),
            render_dir=str(render_dir),
            registries=registries,
        )
        assert result["result"] == RESULT_BLOCKED

    def test_old_stale_output_pattern_rejected(self, tmp_path):
        tasks = [
            _make_task_record("PHASE8-IMPL-026-T004", "complete", "PHASE8-IMPL-026",
                              notes="Complete/PASS-WITH-FINDINGS."),
            _make_task_record("PHASE8-IMPL-026-T004B", "complete", "PHASE8-IMPL-026-T004",
                              notes="Complete/PASS."),
            _make_task_record("PHASE8-IMPL-026-T004C", "complete", "PHASE8-IMPL-026-T004",
                              notes="Complete/PASS-WITH-FINDINGS."),
            _make_task_record("PHASE8-IMPL-026-T005", "planned", "PHASE8-IMPL-026",
                              notes="Planned next. Inactive."),
        ]
        registries = self._reg_with_tasks(tasks)
        stale_pages = self._page_set(
            index="""| T004 (Human-readable memory) | in progress |
| T004B (Markdown renderer) | in progress |
| T004C (Clean-HEAD publication) | planned |""",
            roadmap="Current Project Memory child: T004B",
            remaining="- **T004** (`task:PHASE8-IMPL-026-T004`) — PHASE8-IMPL-026-T004",
        )
        render_dir = _make_minimal_render_dir(tmp_path, stale_pages)
        result = validate_rendered_package(
            repo_root=str(tmp_path),
            snapshot_dir=str(tmp_path),
            render_dir=str(render_dir),
            registries=registries,
        )
        assert result["result"] == RESULT_BLOCKED

    def test_missing_pages_fails_structural(self, tmp_path):
        tasks = [
            _make_task_record("PHASE8-IMPL-026-T001", "complete", "PHASE8-IMPL-026"),
            _make_task_record("PHASE8-IMPL-026-T002", "complete", "PHASE8-IMPL-026"),
            _make_task_record("PHASE8-IMPL-026-T003", "complete", "PHASE8-IMPL-026"),
        ]
        registries = self._reg_with_tasks(tasks)
        render_dir = tmp_path / "partial_render"
        docs_dir = render_dir / "docs"
        docs_dir.mkdir(parents=True)
        (docs_dir / "index.md").write_text("empty")
        (render_dir / "build-manifest.json").write_text(
            json.dumps({"authority_class": "generated_evidence"}))
        result = validate_rendered_package(
            repo_root=str(tmp_path),
            snapshot_dir=str(tmp_path),
            render_dir=str(render_dir),
            registries=registries,
        )
        assert result["result"] == RESULT_BLOCKED

    def test_identical_inputs_same_result(self, tmp_path):
        tasks = [
            _make_task_record("PHASE8-IMPL-026", "in_progress", None),
            _make_task_record("PHASE8-IMPL-026-T001", "complete", "PHASE8-IMPL-026"),
            _make_task_record("PHASE8-IMPL-026-T002", "complete", "PHASE8-IMPL-026"),
            _make_task_record("PHASE8-IMPL-026-T003", "complete", "PHASE8-IMPL-026"),
            _make_task_record("PHASE8-IMPL-026-T004", "complete", "PHASE8-IMPL-026",
                              notes="Complete/PASS-WITH-FINDINGS."),
            _make_task_record("PHASE8-IMPL-026-T004A", "complete", "PHASE8-IMPL-026-T004"),
            _make_task_record("PHASE8-IMPL-026-T004B", "complete", "PHASE8-IMPL-026-T004"),
            _make_task_record("PHASE8-IMPL-026-T004C", "complete", "PHASE8-IMPL-026-T004"),
            _make_task_record("PHASE8-IMPL-026-T005", "planned", "PHASE8-IMPL-026"),
        ]
        registries = self._reg_with_tasks(tasks)
        pages = self._page_set(
            index="PHASE8-IMPL-024-T003A\n| T004 (Human-readable memory) | complete/PASS-WITH-FINDINGS |\n| T005 | planned/inactive |\n",
            roadmap="PHASE8-IMPL-024-T003A\n**Next actionable Project Memory task:** T005 (planned/inactive)",
            remaining="## Planned\n- **T005**\n",
        )
        render_dir = _make_minimal_render_dir(tmp_path, pages)
        r1 = validate_rendered_package(
            repo_root=str(tmp_path), snapshot_dir=str(tmp_path),
            render_dir=str(render_dir), registries=registries,
        )
        r2 = validate_rendered_package(
            repo_root=str(tmp_path), snapshot_dir=str(tmp_path),
            render_dir=str(render_dir), registries=registries,
        )
        assert r1["result"] == r2["result"]


class TestCLI:

    def _reg_with_tasks(self, tasks):
        return {"tasks.json": {"registry_type": "task", "schema_version": "1.0.0",
                                "records": tasks}}

    def _page_set(self, index="", roadmap="", remaining=""):
        d = {}
        for p in RENDERED_PAGE_NAMES:
            d[p] = ""
        d["index.md"] = index
        d["current-roadmap.md"] = roadmap
        d["remaining-work.md"] = remaining
        return d

    def test_cli_json_output(self, tmp_path):
        tasks = [
            _make_task_record("PHASE8-IMPL-026", "in_progress", None),
            _make_task_record("PHASE8-IMPL-026-T001", "complete", "PHASE8-IMPL-026"),
            _make_task_record("PHASE8-IMPL-026-T002", "complete", "PHASE8-IMPL-026"),
            _make_task_record("PHASE8-IMPL-026-T003", "complete", "PHASE8-IMPL-026"),
            _make_task_record("PHASE8-IMPL-026-T004", "complete", "PHASE8-IMPL-026",
                              notes="Complete/PASS-WITH-FINDINGS."),
            _make_task_record("PHASE8-IMPL-026-T004A", "complete", "PHASE8-IMPL-026-T004"),
            _make_task_record("PHASE8-IMPL-026-T004B", "complete", "PHASE8-IMPL-026-T004"),
            _make_task_record("PHASE8-IMPL-026-T004C", "complete", "PHASE8-IMPL-026-T004"),
            _make_task_record("PHASE8-IMPL-026-T005", "planned", "PHASE8-IMPL-026"),
        ]
        registries = self._reg_with_tasks(tasks)
        pages = self._page_set(
            index="PHASE8-IMPL-024-T003A\n| T004 | complete/PASS-WITH-FINDINGS |\n| T005 | planned/inactive |\n",
            roadmap="PHASE8-IMPL-024-T003A\n**Next actionable Project Memory task:** T005 (planned/inactive)",
            remaining="## Planned\n- **T005**\n",
        )
        render_dir = _make_minimal_render_dir(tmp_path, pages)
        result = validate_rendered_package(
            repo_root=str(tmp_path), snapshot_dir=str(tmp_path),
            render_dir=str(render_dir), registries=registries,
        )
        assert result["result"] in (RESULT_PASS, RESULT_PASS_WITH_FINDINGS)
        assert isinstance(result.get("page_count"), int)
        assert isinstance(result.get("structural_checks"), list)
        assert isinstance(result.get("semantic_checks"), list)


class TestAuthoritySemantics:

    @staticmethod
    def _authority_docs(tmp_path, text):
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "index.md").write_text(text, encoding="utf-8")
        return docs_dir

    @pytest.mark.parametrize(
        ("text", "classification"),
        [
            ("# Generated Evidence — Not Project Authority", "generated_evidence_banner"),
            ("This generated package is not project authority", "generated_evidence_non_authority"),
            ("Generated evidence is non-authoritative", "generated_evidence_non_authority"),
            ("The roadmap is authoritative over this render", "higher_authority_tracked_source"),
            ("| Tier 1 | authoritative | accepted roadmap |", "authority_hierarchy_description"),
            ("Trust class `authoritative` describes accepted tracked sources.", "trust_class_description"),
            ("model output is not truth", "candidate_non_authority_boundary"),
            ("generated evidence cannot establish canon", "generated_evidence_non_authority"),
            ("The validator rejects the forbidden pattern: This generated page is authoritative.",
             "technical_validation_description"),
            ("> Historical quotation: This generated page is authoritative.", "historical_quotation"),
            ("Inline code: `authoritative`", "inline_code_reference"),
            ("See the [authoritative tracked roadmap](docs/roadmap/roadmap_index.yaml).",
             "higher_authority_tracked_source"),
            ("authority_class: generated_evidence", "generated_evidence_classification"),
        ],
    )
    def test_allowed_authority_language(self, tmp_path, text, classification):
        result = analyze_authority_claims(self._authority_docs(tmp_path, text))
        assert result["result"] == "pass"
        assert result["forbidden_claims"] == []
        assert classification in {r["classification"] for r in result["allowed_references"]}

    def test_fenced_code_is_not_treated_as_a_live_claim(self, tmp_path):
        text = """Technical example:\n```text\nThis generated page is authoritative\n```\n"""
        result = analyze_authority_claims(self._authority_docs(tmp_path, text))
        assert result["result"] == "pass"
        assert result["forbidden_claims"] == []

    @pytest.mark.parametrize(
        ("text", "rule"),
        [
            ("This generated page is authoritative", "generated_self_authority"),
            ("This render is the project source of truth", "generated_self_authority"),
            ("This snapshot controls roadmap status", "generated_controls_task_status"),
            ("Generated documentation overrides the roadmap", "generated_overrides_tracked_sources"),
            ("This generated output establishes canon", "generated_establishes_canon"),
            ("This page resolves owner decisions", "generated_resolves_owner_decisions"),
            ("The generated package automatically approves candidates", "generated_approves_candidates"),
            ("# This generated page is authoritative", "generated_self_authority"),
            ("| Claim | This render is the project source of truth |", "generated_self_authority"),
            ("Generated evidence has equal or greater authority", "generated_equal_or_greater_authority"),
        ],
    )
    def test_forbidden_authority_language(self, tmp_path, text, rule):
        result = analyze_authority_claims(self._authority_docs(tmp_path, text))
        assert result["result"] == "fail"
        assert len(result["forbidden_claims"]) == 1
        assert result["forbidden_claims"][0]["rule"] == rule

    def test_mixed_allowed_and_forbidden_language_fails(self, tmp_path):
        text = """Generated evidence is non-authoritative.
This generated page is authoritative.
"""
        result = analyze_authority_claims(self._authority_docs(tmp_path, text))
        assert result["result"] == "fail"
        assert result["allowed_references"]
        assert len(result["forbidden_claims"]) == 1

    def test_failure_diagnostics_include_required_line_evidence(self, tmp_path):
        result = analyze_authority_claims(
            self._authority_docs(tmp_path, "safe line\nThis snapshot controls task status\n")
        )
        claim = result["forbidden_claims"][0]
        assert claim["page"] == "index.md"
        assert claim["line"] == 2
        assert claim["text"] == "This snapshot controls task status"
        assert claim["rule"] == "generated_controls_task_status"
        assert claim["classification"]
        assert claim["reason"]

    def test_preserved_t004c1_render_passes_repaired_authority_gate(self):
        repo_root = Path(__file__).resolve().parents[2]
        snapshot_dir = repo_root / ".codex-context/project-memory/PHASE8-IMPL-026-T004C1/20260714T213628Z"
        render_dir = repo_root / ".codex-context/project-memory/rendered/PHASE8-IMPL-026-T004C1/20260714T213628Z"
        result = validate_rendered_package(
            repo_root=str(repo_root),
            snapshot_dir=str(snapshot_dir),
            render_dir=str(render_dir),
        )
        assert result["result"] == RESULT_PASS_WITH_FINDINGS
        assert result["authority_check"] == "pass"
        assert result["authority"]["result"] == "pass"
        assert result["authority"]["forbidden_claims"] == []
        assert result["authority"]["allowed_references"]
        assert len(result["nonblocking_findings"]) == 4
        assert {f["code"] for f in result["nonblocking_findings"]} == {"source_missing"}
        assert len(result["warnings"]) == 4
        assert all(w.startswith("source_missing:") for w in result["warnings"])
        assert result["application_frontier_check"] == "pass"
        assert result["ph8_impl_025_check"] == "pass"
        assert result["remaining_work_check"] == "pass"
        assert all(c["result"] == "pass" for c in result["semantic_checks"])
        assert result["repository_currentness"] == "historical"
        assert result["expected_task_states"]["_pm_next_task"]["task_id"] == "PHASE8-IMPL-026-T005"
        assert "PHASE8-IMPL-026-T006" not in result["expected_task_states"]

    def test_preserved_t004c2_render_uses_its_snapshot_bound_task_state(self):
        repo_root = Path(__file__).resolve().parents[2]
        snapshot_dir = repo_root / ".codex-context/project-memory/PHASE8-IMPL-026-T004C2/20260714T221454Z"
        render_dir = repo_root / ".codex-context/project-memory/rendered/PHASE8-IMPL-026-T004C2/20260714T221454Z"
        result = validate_rendered_package(
            repo_root=str(repo_root),
            snapshot_dir=str(snapshot_dir),
            render_dir=str(render_dir),
        )
        assert result["result"] == RESULT_PASS_WITH_FINDINGS
        assert result["repository_currentness"] == "historical"
        assert result["expected_task_states"]["_pm_next_task"]["task_id"] == "PHASE8-IMPL-026-T005"
        assert "PHASE8-IMPL-026-T006" not in result["expected_task_states"]
        assert len(result["nonblocking_findings"]) == 4

    def test_render_contradicting_its_own_snapshot_is_blocked(self, tmp_path):
        repo_root = Path(__file__).resolve().parents[2]
        snapshot_dir = repo_root / ".codex-context/project-memory/PHASE8-IMPL-026-T004C1/20260714T213628Z"
        source_render = repo_root / ".codex-context/project-memory/rendered/PHASE8-IMPL-026-T004C1/20260714T213628Z"
        render_dir = tmp_path / "render"
        shutil.copytree(source_render, render_dir)

        roadmap_path = render_dir / "docs/current-roadmap.md"
        roadmap = roadmap_path.read_text(encoding="utf-8").replace(
            "**Next Project Memory task:** T005 (planned)",
            "**Next Project Memory task:** T999 (planned)",
        )
        roadmap_path.write_text(roadmap, encoding="utf-8")
        manifest_path = render_dir / "build-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["page_hashes"]["current-roadmap.md"] = hashlib.sha256(
            roadmap_path.read_bytes()
        ).hexdigest()
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        result = validate_rendered_package(
            repo_root=str(repo_root),
            snapshot_dir=str(snapshot_dir),
            render_dir=str(render_dir),
        )
        assert result["result"] == RESULT_BLOCKED
        assert any("Next PM task T005 absent" in error for error in result["errors"])

    def test_current_snapshot_registry_hash_drift_is_blocked(self):
        repo_root = Path(__file__).resolve().parents[2]
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=repo_root,
            check=True, capture_output=True, text=True,
        ).stdout.strip()
        registry_names = [
            "assets.json", "boundaries.json", "capabilities.json", "decisions.json",
            "dependencies.json", "evidence.json", "features.json", "manifest.json",
            "owner-decisions.json", "projects.json", "tasks.json", "tools.json",
        ]
        registry_hashes = {}
        for name in registry_names:
            path = f"docs/project-memory/registries/{name}"
            blob = subprocess.run(
                ["git", "show", f"{head}:{path}"], cwd=repo_root,
                check=True, capture_output=True,
            ).stdout
            registry_hashes[path] = hashlib.sha256(blob).hexdigest()

        snapshot_bundle = {
            "snapshot": {
                "bound_commit": head,
                "branch": "docs/project-memory-foundation",
                "registry_hashes": registry_hashes,
            },
            "findings": [],
        }
        render_dir = repo_root / ".codex-context/project-memory/rendered/PHASE8-IMPL-026-T004C2/20260714T221454Z"
        result = validate_rendered_package(
            repo_root=str(repo_root),
            snapshot_dir=str(repo_root),
            render_dir=str(render_dir),
            snapshot_bundle=snapshot_bundle,
            registries={"tasks.json": {}},
        )
        assert result["result"] == RESULT_BLOCKED
        assert any(
            "Current publication snapshot differs from current tracked registry" in error
            for error in result["errors"]
        )

    def test_preserved_t004c1_packages_are_not_mutated(self):
        repo_root = Path(__file__).resolve().parents[2]
        roots = [
            repo_root / ".codex-context/project-memory/PHASE8-IMPL-026-T004C1/20260714T213628Z",
            repo_root / ".codex-context/project-memory/rendered/PHASE8-IMPL-026-T004C1/20260714T213628Z",
            repo_root / ".codex-context/project-memory/PHASE8-IMPL-026-T004C1-quality/20260714T213628Z",
        ]

        def package_hashes():
            return {
                str(path.relative_to(repo_root)): hashlib.sha256(path.read_bytes()).hexdigest()
                for package_root in roots
                for path in sorted(package_root.rglob("*"))
                if path.is_file()
            }

        before = package_hashes()
        analyze_authority_claims(roots[1] / "docs")
        after = package_hashes()
        assert after == before
