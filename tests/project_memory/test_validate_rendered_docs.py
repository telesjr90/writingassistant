"""Semantic rendered-documentation validator tests.

All tests use temporary directories and must not mutate the real repository.
"""

from __future__ import annotations

import hashlib
import importlib
import json
import os
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

_GENERATED_EVIDENCE_BANNER = "# Generated Evidence — Not Project Authority\n\n"
_HISTORICAL_BRANCH = "docs/project-memory-foundation"
_SNAPSHOT_FILES = (
    "run-metadata.json",
    "repository-state.json",
    "roadmap-state.json",
    "registry-validation.json",
    "source-inventory.json",
    "source-hashes.json",
    "convergence-findings.json",
    "snapshot.json",
    "summary.md",
    "FILE-INVENTORY.txt",
    "SHA256SUMS",
)


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


def _write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_sha256_manifest(package_dir: Path) -> None:
    entries = []
    for path in sorted(package_dir.rglob("*")):
        if path.is_file() and path.name != "SHA256SUMS":
            relative = path.relative_to(package_dir).as_posix()
            entries.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {relative}")
    (package_dir / "SHA256SUMS").write_text("\n".join(entries) + "\n", encoding="utf-8")


def _write_exact_package_metadata(package_dir: Path) -> None:
    paths = [
        path.relative_to(package_dir).as_posix()
        for path in sorted(package_dir.rglob("*"))
        if path.is_file() and path.name not in {"FILE-INVENTORY.txt", "SHA256SUMS"}
    ]
    paths.extend(["FILE-INVENTORY.txt", "SHA256SUMS"])
    (package_dir / "FILE-INVENTORY.txt").write_text(
        "\n".join(sorted(paths)) + "\n", encoding="utf-8"
    )
    _write_sha256_manifest(package_dir)


def _git(repo_root: Path, *args: str) -> str:
    env = os.environ.copy()
    env.update(
        {
            "GIT_AUTHOR_DATE": "2026-07-14T21:36:28Z",
            "GIT_COMMITTER_DATE": "2026-07-14T21:36:28Z",
        }
    )
    return subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
        env=env,
    ).stdout.strip()


def _historical_tasks() -> list[dict]:
    return [
        _make_task_record("PHASE8-IMPL-026", "in_progress"),
        _make_task_record("PHASE8-IMPL-026-T001", "complete", "PHASE8-IMPL-026"),
        _make_task_record("PHASE8-IMPL-026-T002", "complete", "PHASE8-IMPL-026"),
        _make_task_record("PHASE8-IMPL-026-T003", "complete", "PHASE8-IMPL-026"),
        _make_task_record(
            "PHASE8-IMPL-026-T004", "complete", "PHASE8-IMPL-026",
            notes="Complete/PASS-WITH-FINDINGS.",
        ),
        _make_task_record(
            "PHASE8-IMPL-026-T004A", "complete", "PHASE8-IMPL-026-T004",
            notes="Complete/PASS-WITH-FINDINGS.",
        ),
        _make_task_record(
            "PHASE8-IMPL-026-T004B", "complete", "PHASE8-IMPL-026-T004",
            notes="Complete/PASS.",
        ),
        _make_task_record(
            "PHASE8-IMPL-026-T004C", "complete", "PHASE8-IMPL-026-T004",
            notes="Complete/PASS-WITH-FINDINGS.",
        ),
        _make_task_record(
            "PHASE8-IMPL-026-T005", "planned", "PHASE8-IMPL-026",
            notes="Planned next. Inactive.",
        ),
    ]


def _historical_pages() -> dict[str, str]:
    pages = {name: "" for name in RENDERED_PAGE_NAMES}
    pages["index.md"] = """## Project Memory Workstream Status

| Task | Snapshot-bound state |
| --- | --- |
| T001 (Authority/Lifecycle foundation) | complete |
| T002 (Schema/registry architecture) | complete |
| T003 (Scanners/snapshot builder) | complete |
| T004 (Human-readable memory) | complete/PASS-WITH-FINDINGS |
| T004A (Architecture/remediation) | complete/PASS-WITH-FINDINGS |
| T004B (Markdown renderer) | complete/PASS |
| T004C (Clean-HEAD publication) | complete/PASS-WITH-FINDINGS |
| T005 (Context-tool integration) | planned/inactive |

Application frontier: PHASE8-IMPL-024-T003A
"""
    pages["current-roadmap.md"] = """Application frontier: PHASE8-IMPL-024-T003A

**Next Project Memory task:** T005 (planned)

PHASE8-IMPL-025 remains planned and inactive.
"""
    pages["remaining-work.md"] = """## Planned

- **T005** — PHASE8-IMPL-026-T005 (planned/inactive)
"""
    return pages


def _make_minimal_render_dir(
    base: Path,
    pages: dict[str, str],
    *,
    bound_commit: str = "a415270b18f978e601a9ffc6d7bcb4ab8a250c42",
    branch: str = _HISTORICAL_BRANCH,
    output_name: str = "render_out",
) -> Path:
    """Create a minimal render package structure."""
    render_dir = base / output_name
    docs_dir = render_dir / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    for name in RENDERED_PAGE_NAMES:
        content = pages.get(name, _GENERATED_EVIDENCE_BANNER)
        if "Generated Evidence" not in content:
            content = _GENERATED_EVIDENCE_BANNER + content
        (docs_dir / name).write_text(content, encoding="utf-8")

    manifest = {
        "renderer_name": "project_memory_markdown_renderer",
        "renderer_version": "project_memory_markdown_renderer.v1",
        "authority_class": "generated_evidence",
        "mode": "publication",
        "target_commit": bound_commit,
        "target_branch": branch,
        "source_snapshot_bound_commit": bound_commit,
        "freshness": "current",
        "publication_eligible": True,
        "convergence_result": "PASS_WITH_FINDINGS",
        "page_count": 14,
        "page_navigation_order": list(RENDERED_PAGE_NAMES),
        "page_hashes": {
            name: hashlib.sha256((docs_dir / name).read_bytes()).hexdigest()
            for name in RENDERED_PAGE_NAMES
        },
    }
    _write_json(render_dir / "build-manifest.json", manifest)
    _write_json(
        render_dir / "source-snapshot.json",
        {
            "bound_commit": bound_commit,
            "branch": branch,
            "authority_class": "generated_evidence",
        },
    )
    _write_exact_package_metadata(render_dir)
    return render_dir


def _materialize_historical_package(
    tmp_path: Path, case: str, *, advance_head: bool = True
) -> dict[str, Path | str]:
    repo_root = tmp_path / f"repo-{case.lower()}"
    repo_root.mkdir()
    _git(repo_root, "init", "-b", _HISTORICAL_BRANCH)
    _git(repo_root, "config", "user.name", "Project Memory Test")
    _git(repo_root, "config", "user.email", "project-memory-test@example.invalid")

    registry_root = repo_root / "docs/project-memory/registries"
    registry_root.mkdir(parents=True)
    tasks_path = registry_root / "tasks.json"
    owner_decisions_path = registry_root / "owner-decisions.json"
    _write_json(
        tasks_path,
        {
            "registry_type": "task",
            "schema_version": "1.0.0",
            "records": _historical_tasks(),
        },
    )
    _write_json(
        owner_decisions_path,
        {
            "registry_type": "owner-decision",
            "schema_version": "1.0.0",
            "records": [],
        },
    )
    _git(repo_root, "add", "docs/project-memory/registries")
    _git(repo_root, "commit", "-m", f"test: {case} snapshot registry state")
    bound_commit = _git(repo_root, "rev-parse", "HEAD")

    registry_hashes = {
        path.relative_to(repo_root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in (tasks_path, owner_decisions_path)
    }
    findings = [
        {
            "authority_class": "generated_evidence",
            "blocks_publication": False,
            "code": "source_missing",
            "finding_id": f"finding:{case.lower()}-source-missing-{index}",
            "severity": "warning",
            "title": f"Historical source {index} is unavailable",
        }
        for index in range(1, 5)
    ]

    snapshot_dir = tmp_path / f"snapshot-{case.lower()}"
    snapshot_dir.mkdir()
    common_metadata = {"authority_class": "generated_evidence"}
    for name in (
        "run-metadata.json",
        "repository-state.json",
        "roadmap-state.json",
        "registry-validation.json",
        "source-inventory.json",
        "source-hashes.json",
    ):
        _write_json(snapshot_dir / name, common_metadata)
    _write_json(
        snapshot_dir / "convergence-findings.json",
        {
            "authority_class": "generated_evidence",
            "result": "PASS_WITH_FINDINGS",
            "findings": findings,
        },
    )
    _write_json(
        snapshot_dir / "snapshot.json",
        {
            "authority_class": "generated_evidence",
            "authoritative": False,
            "bound_commit": bound_commit,
            "branch": _HISTORICAL_BRANCH,
            "generated_at": "2026-07-14T21:36:28Z",
            "publication_eligible": True,
            "registry_hashes": registry_hashes,
            "snapshot_id": f"{case}/synthetic-preservation",
            "task_id": f"PHASE8-IMPL-026-{case}",
        },
    )
    (snapshot_dir / "summary.md").write_text(
        _GENERATED_EVIDENCE_BANNER + "Deterministic synthetic historical snapshot.\n",
        encoding="utf-8",
    )
    _write_exact_package_metadata(snapshot_dir)
    assert tuple(sorted(path.name for path in snapshot_dir.iterdir())) == tuple(
        sorted(_SNAPSHOT_FILES)
    )

    render_dir = _make_minimal_render_dir(
        tmp_path,
        _historical_pages(),
        bound_commit=bound_commit,
        output_name=f"render-{case.lower()}",
    )

    if advance_head:
        current_tasks = _historical_tasks()
        next(task for task in current_tasks if task["task_id"] == "PHASE8-IMPL-026-T005")[
            "lifecycle"
        ]["status"] = "complete"
        current_tasks.append(
            _make_task_record(
                "PHASE8-IMPL-026-T006", "planned", "PHASE8-IMPL-026",
                notes="Later current-registry lifecycle state.",
            )
        )
        _write_json(
            tasks_path,
            {
                "registry_type": "task",
                "schema_version": "1.0.0",
                "records": current_tasks,
            },
        )
        _git(repo_root, "add", "docs/project-memory/registries/tasks.json")
        _git(repo_root, "commit", "-m", "test: advance current registry lifecycle")

    return {
        "repo_root": repo_root,
        "snapshot_dir": snapshot_dir,
        "render_dir": render_dir,
        "bound_commit": bound_commit,
        "tasks_path": tasks_path,
    }


@pytest.fixture
def historical_package_factory(tmp_path):
    def materialize(case: str, *, advance_head: bool = True):
        return _materialize_historical_package(
            tmp_path, case, advance_head=advance_head
        )

    return materialize


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

    def test_direct_cli_from_repository_root_returns_valid_json(
        self, tmp_path, historical_package_factory
    ):
        package = historical_package_factory("T004C1")
        assert package["repo_root"].is_relative_to(tmp_path)
        result = subprocess.run(
            self._direct_command(
                package["repo_root"], package["snapshot_dir"], package["render_dir"]
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

    def test_direct_cli_outside_repository_uses_explicit_repo_root(
        self, tmp_path, historical_package_factory
    ):
        package = historical_package_factory("T004C1")
        outside_repository = tmp_path / "outside-repository"
        outside_repository.mkdir()
        result = subprocess.run(
            self._direct_command(
                package["repo_root"], package["snapshot_dir"], package["render_dir"]
            ),
            cwd=outside_repository,
            check=False,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr
        assert json.loads(result.stdout)["result"] == RESULT_PASS_WITH_FINDINGS

    def test_source_has_no_fixed_historical_package_dependencies(self):
        source = Path(__file__).read_text(encoding="utf-8")
        for case in ("T004C1", "T004C2"):
            fixed_package_prefix = (
                ".codex-context/project-memory/"
                + "PHASE8-IMPL-026-"
                + case
            )
            assert fixed_package_prefix not in source

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

    def test_preserved_t004c1_render_passes_repaired_authority_gate(
        self, historical_package_factory
    ):
        # "Preserved" now means a deterministic synthetic preservation fixture,
        # not ignored evidence from a source worktree.
        package = historical_package_factory("T004C1")
        current_tasks = json.loads(package["tasks_path"].read_text(encoding="utf-8"))[
            "records"
        ]
        assert next(
            task for task in current_tasks
            if task["task_id"] == "PHASE8-IMPL-026-T005"
        )["lifecycle"]["status"] == "complete"
        assert any(task["task_id"] == "PHASE8-IMPL-026-T006" for task in current_tasks)

        result = validate_rendered_package(
            repo_root=str(package["repo_root"]),
            snapshot_dir=str(package["snapshot_dir"]),
            render_dir=str(package["render_dir"]),
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

    def test_preserved_t004c2_render_uses_its_snapshot_bound_task_state(
        self, historical_package_factory
    ):
        # This synthetic preservation case has a later current-registry commit;
        # the render must still use the registry state at its own bound commit.
        package = historical_package_factory("T004C2")
        current_tasks = json.loads(package["tasks_path"].read_text(encoding="utf-8"))[
            "records"
        ]
        assert next(
            task for task in current_tasks
            if task["task_id"] == "PHASE8-IMPL-026-T005"
        )["lifecycle"]["status"] == "complete"
        assert any(task["task_id"] == "PHASE8-IMPL-026-T006" for task in current_tasks)

        result = validate_rendered_package(
            repo_root=str(package["repo_root"]),
            snapshot_dir=str(package["snapshot_dir"]),
            render_dir=str(package["render_dir"]),
        )
        assert result["result"] == RESULT_PASS_WITH_FINDINGS
        assert result["repository_currentness"] == "historical"
        assert result["expected_task_states"]["_pm_next_task"]["task_id"] == "PHASE8-IMPL-026-T005"
        assert "PHASE8-IMPL-026-T006" not in result["expected_task_states"]
        assert result["authority_check"] == "pass"
        assert result["authority"]["forbidden_claims"] == []
        assert all(check["result"] == "pass" for check in result["semantic_checks"])
        assert len(result["nonblocking_findings"]) == 4
        assert {f["code"] for f in result["nonblocking_findings"]} == {"source_missing"}
        assert len(result["warnings"]) == 4
        assert all(w.startswith("source_missing:") for w in result["warnings"])

    def test_render_contradicting_its_own_snapshot_is_blocked(
        self, tmp_path, historical_package_factory
    ):
        package = historical_package_factory("T004C1")
        render_dir = tmp_path / "contradictory-render"
        shutil.copytree(package["render_dir"], render_dir)

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
        _write_json(manifest_path, manifest)
        _write_sha256_manifest(render_dir)

        result = validate_rendered_package(
            repo_root=str(package["repo_root"]),
            snapshot_dir=str(package["snapshot_dir"]),
            render_dir=str(render_dir),
        )
        assert result["result"] == RESULT_BLOCKED
        assert result["errors"] == [
            "Semantic: Next PM task T005 absent from current-roadmap"
        ]
        assert all(check["result"] == "pass" for check in result["structural_checks"])

    def test_current_snapshot_registry_hash_drift_is_blocked(
        self, historical_package_factory
    ):
        package = historical_package_factory("T004C2", advance_head=False)
        tasks_path = package["tasks_path"]
        drifted_registry = json.loads(tasks_path.read_text(encoding="utf-8"))
        drifted_registry["records"][0]["notes"] += " Deterministic registry drift."
        _write_json(tasks_path, drifted_registry)

        result = validate_rendered_package(
            repo_root=str(package["repo_root"]),
            snapshot_dir=str(package["snapshot_dir"]),
            render_dir=str(package["render_dir"]),
        )
        assert result["result"] == RESULT_BLOCKED
        assert len(result["errors"]) == 1
        assert (
            "Current publication snapshot differs from current tracked registry"
            in result["errors"][0]
        )

    def test_preserved_t004c1_packages_are_not_mutated(
        self, historical_package_factory
    ):
        # Byte preservation now covers real temporary snapshot/render packages,
        # including both inventories and both checksum manifests.
        package = historical_package_factory("T004C1")
        roots = [package["snapshot_dir"], package["render_dir"]]

        def package_hashes():
            return {
                f"{package_root.name}/{path.relative_to(package_root)}": hashlib.sha256(
                    path.read_bytes()
                ).hexdigest()
                for package_root in roots
                for path in sorted(package_root.rglob("*"))
                if path.is_file()
            }

        before = package_hashes()
        result = validate_rendered_package(
            repo_root=str(package["repo_root"]),
            snapshot_dir=str(package["snapshot_dir"]),
            render_dir=str(package["render_dir"]),
        )
        after = package_hashes()
        assert result["result"] == RESULT_PASS_WITH_FINDINGS
        assert after == before
