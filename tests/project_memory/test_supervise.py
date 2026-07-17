from __future__ import annotations

import copy
import json
import subprocess
from pathlib import Path

import pytest

from scripts.project_memory import supervise


TASK_ID = "PHASE8-IMPL-024-T003B"
SHA = "a" * 40
BASELINE_SHA = "b" * 40


def _inputs(*, mode: str = "implementation") -> dict:
    task_status = "complete" if mode == "governance" else "in_progress"
    return {
        "mode": mode,
        "repository": {
            "name": "WritingAssistantApplication",
            "branch": "docs/opencode-go-routing-small-task-execution",
            "commit": SHA,
            "clean": True,
            "staged": False,
            "detached": False,
            "remote_sha": "c" * 40,
            "ahead": 1,
            "behind": 0,
        },
        "task": {
            "task_id": "PHASE8-IMPL-026-T011" if mode == "governance" else TASK_ID,
            "status": task_status,
            "roadmap_status": "complete" if mode == "governance" else "active",
            "frontier": TASK_ID,
            "is_frontier": mode != "governance",
            "dependencies": [{"task_id": "PHASE8-IMPL-024-T003A", "status": "complete"}],
            "required_sources_present": True,
            "application_task": mode != "governance",
        },
        "routing": {
            "task_id": "PHASE8-IMPL-026-T011" if mode == "governance" else TASK_ID,
            "execution_class": "codex_gpt_5_6_sol" if mode == "governance" else "opencode_go",
            "model_category": "gpt_5_6_sol" if mode == "governance" else "opencode_go_narrow_tests_first",
            "reasoning_level": "high" if mode == "governance" else "focused",
            "risk_class": "critical" if mode == "governance" else "moderate",
            "owner_only": False,
            "delegation_eligible": True,
            "authoritative_source_locator": {
                "path": "docs/project-memory/operations.json" if mode == "governance" else "docs/project-memory/registries/execution-routing.json",
                "symbol": "supervision.governance_maintenance" if mode == "governance" else "PHASE8-IMPL-024-T003",
            },
        },
        "routing_error": None,
        "changed_paths": [],
        "memory": {
            "status": "FRESH",
            "package_commit": SHA,
            "package_branch": "docs/opencode-go-routing-small-task-execution",
            "reasons": [],
            "baseline_is_ancestor": True,
            "packages": {"report": "report", "snapshot": "snapshot", "render": "render", "quality": "quality"},
        },
        "plan_integrity": {
            "blocking_count": 0,
            "advisory_count": 0,
            "advisory_codes": [],
        },
        "validation_evidence": {"status": "PASS", "checks": []},
        "validators": {"result": "PASS", "checks": []},
        "conflicts": [],
    }


def _codes(items: list[dict]) -> set[str]:
    return {item["code"] for item in items}


def test_application_only_commit_lag_is_advisory_and_never_fresh():
    inputs = _inputs()
    inputs["memory"].update({
        "status": "STALE",
        "package_commit": BASELINE_SHA,
        "reasons": ["commit_mismatch", "source_hash_drift"],
    })
    inputs["changed_paths"] = supervise.classify_paths([
        "frontend/src/App.jsx",
        "frontend/tests/contextReadinessWiring.test.mjs",
    ])

    gate = supervise.evaluate_gate(inputs)

    assert gate["result"] == "READY_WITH_ADVISORIES"
    assert "project_memory_commit_lag_application_only" in _codes(gate["advisories"])
    assert gate["project_memory_freshness"] == "STALE_ANCESTOR_APPLICATION_ONLY"
    assert gate["project_memory_freshness"] != "FRESH"


@pytest.mark.parametrize(
    ("routing", "routing_error", "expected"),
    [
        (None, {"classification": "missing_current_routing"}, "routing_resolution_failed"),
        (None, {"classification": "conflicting_current_routing"}, "routing_resolution_failed"),
        ({"owner_only": True, "delegation_eligible": False}, None, "owner_only_or_nondelegable_task"),
    ],
)
def test_routing_absence_conflict_and_owner_only_block(routing, routing_error, expected):
    inputs = _inputs()
    inputs["routing"] = routing
    inputs["routing_error"] = routing_error
    gate = supervise.evaluate_gate(inputs)
    assert gate["result"] == "BLOCKED"
    assert expected in _codes(gate["blockers"])


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        (("task", "status", "inactive"), "inactive_task"),
        (("dependency", "status", "in_progress"), "dependency_ineligible"),
    ],
)
def test_inactive_and_dependency_ineligible_tasks_block(mutation, expected):
    inputs = _inputs()
    target, key, value = mutation
    if target == "task":
        inputs["task"][key] = value
    else:
        inputs["task"]["dependencies"][0][key] = value
    gate = supervise.evaluate_gate(inputs)
    assert gate["result"] == "BLOCKED"
    assert expected in _codes(gate["blockers"])


@pytest.mark.parametrize(
    "path",
    [
        "docs/project-memory/registries/tasks.json",
        "docs/roadmap/roadmap_index.yaml",
        "scripts/project_memory/plan_integrity.py",
        "AGENTS.md",
        ".github/workflows/project-memory.yml",
    ],
)
def test_control_plane_and_status_frontier_changes_block_implementation(path):
    inputs = _inputs()
    inputs["changed_paths"] = supervise.classify_paths([path])
    gate = supervise.evaluate_gate(inputs)
    assert gate["result"] == "BLOCKED"
    assert "control_plane_changes_require_strict_gate" in _codes(gate["blockers"])


@pytest.mark.parametrize("mode", ["closeout", "governance"])
def test_strict_modes_block_stale_memory(mode):
    inputs = _inputs(mode=mode)
    if mode == "closeout":
        inputs["task"].update({"status": "complete", "roadmap_status": "complete", "is_frontier": False, "frontier": "PHASE8-IMPL-024-T003C"})
    inputs["memory"].update({"status": "STALE", "package_commit": BASELINE_SHA, "reasons": ["commit_mismatch"]})
    gate = supervise.evaluate_gate(inputs)
    assert gate["result"] == "BLOCKED"
    assert "exact_commit_project_memory_required" in _codes(gate["blockers"])


def test_exact_commit_closeout_can_pass_without_mutating_status():
    inputs = _inputs(mode="closeout")
    inputs["task"].update({
        "status": "complete",
        "roadmap_status": "complete",
        "is_frontier": False,
        "frontier": "PHASE8-IMPL-024-T003C",
    })
    before = copy.deepcopy(inputs)
    gate = supervise.evaluate_gate(inputs)
    assert gate["result"] == "READY"
    assert gate["acceptance_claimed"] is False
    assert inputs == before


def test_output_is_deterministic_atomic_and_checksums_verify(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    payload = supervise.build_payload(_inputs(), supervise.evaluate_gate(_inputs()))
    first = supervise.write_handoff_package(repo, payload)
    first_bytes = {path.name: path.read_bytes() for path in first.iterdir()}
    second = supervise.write_handoff_package(repo, payload)
    assert {path.name: path.read_bytes() for path in second.iterdir()} == first_bytes
    assert supervise.verify_handoff_package(first)["result"] == "PASS"

    other = tmp_path / "other"
    other.mkdir()
    original = supervise._write_text
    calls = {"count": 0}

    def fail_second(path: Path, value: str) -> None:
        calls["count"] += 1
        if calls["count"] == 2:
            raise OSError("injected write failure")
        original(path, value)

    monkeypatch.setattr(supervise, "_write_text", fail_second)
    with pytest.raises(OSError, match="injected write failure"):
        supervise.write_handoff_package(other, payload)
    expected = other / ".codex-context/project-memory/handoff" / TASK_ID / SHA / "implementation"
    assert not expected.exists()


@pytest.mark.parametrize("failed_check", ["project_memory_validation_suite", "strict_exact_commit_refresh"])
def test_failed_workflow_gate_still_creates_a_blocked_handoff(tmp_path, failed_check):
    repo = tmp_path / "repo"
    repo.mkdir()
    inputs = _inputs(mode="governance")
    inputs["validation_evidence"] = {
        "status": "FAIL",
        "checks": [{"name": failed_check, "result": "FAIL", "exit_code": 1}],
    }
    if failed_check == "strict_exact_commit_refresh":
        inputs["memory"].update({
            "status": "STALE",
            "package_commit": BASELINE_SHA,
            "reasons": ["commit_mismatch"],
        })

    gate = supervise.evaluate_gate(inputs)
    package = supervise.write_handoff_package(repo, supervise.build_payload(inputs, gate))

    assert gate["result"] == "BLOCKED"
    assert sorted(path.name for path in package.iterdir()) == sorted(supervise.HANDOFF_FILES)
    assert supervise.verify_handoff_package(package)["result"] == "PASS"
    assert json.loads((package / "project-memory-handoff.json").read_text())["result"] == "BLOCKED"


def test_successful_governance_creates_exact_complete_handoff_inventory(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    inputs = _inputs(mode="governance")

    gate = supervise.evaluate_gate(inputs)
    package = supervise.write_handoff_package(repo, supervise.build_payload(inputs, gate))

    assert gate["result"] == "READY"
    assert sorted(path.name for path in package.iterdir()) == sorted(supervise.HANDOFF_FILES)
    assert supervise.verify_handoff_package(package) == {"result": "PASS", "errors": []}


def test_input_collection_failure_still_writes_generated_blocked_handoff(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".gitignore").write_text(".codex-context/\n", encoding="utf-8")
    subprocess.run(["git", "init", "-b", "test"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
    subprocess.run(["git", "add", ".gitignore"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "fixture"], cwd=repo, check=True, capture_output=True)
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo, check=True, text=True, capture_output=True
    ).stdout.strip()
    monkeypatch.setattr(
        supervise,
        "collect_inputs",
        lambda **kwargs: (_ for _ in ()).throw(supervise.SupervisionError("registry malformed")),
    )

    exit_code = supervise.main([
        "--mode", "governance", "--repo-root", str(repo),
        "--task-id", "PHASE8-IMPL-026-T011", "--json",
    ])

    package = (
        repo / ".codex-context/project-memory/handoff/PHASE8-IMPL-026-T011"
        / commit / "governance"
    )
    assert exit_code == 1
    assert supervise.verify_handoff_package(package)["result"] == "PASS"
    payload = json.loads((package / "project-memory-handoff.json").read_text())
    assert payload["result"] == "BLOCKED"
    assert "supervision_input_collection_failed" in _codes(payload["blockers"])
    assert subprocess.run(
        ["git", "status", "--porcelain"], cwd=repo, check=True, text=True, capture_output=True
    ).stdout == ""


def test_symlink_escape_and_malformed_evidence_fail_closed(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    generated = repo / ".codex-context"
    generated.symlink_to(outside, target_is_directory=True)
    payload = supervise.build_payload(_inputs(), supervise.evaluate_gate(_inputs()))
    with pytest.raises(supervise.SupervisionError, match="symlink"):
        supervise.write_handoff_package(repo, payload)

    generated.unlink()
    evidence = repo / "evidence.json"
    evidence.write_text('{"schema":"wrong"}\n', encoding="utf-8")
    result = supervise.validate_evidence(evidence, repo, TASK_ID, SHA)
    assert result["status"] == "BLOCKED"
    assert result["checks"] == []


def test_bounded_workflow_evidence_preserves_exit_status_and_sanitized_output(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    evidence = repo / "evidence.json"
    evidence.write_text(json.dumps({
        "schema": supervise.EVIDENCE_SCHEMA,
        "task_id": TASK_ID,
        "commit": SHA,
        "checks": [{
            "name": "strict_exact_commit_refresh",
            "result": "FAIL",
            "exit_code": 3,
            "outcome": "failure",
            "output_tail": "ROUTING-001 detached branch mismatch",
        }],
    }) + "\n", encoding="utf-8")

    result = supervise.validate_evidence(evidence, repo, TASK_ID, SHA)

    assert result == {
        "status": "FAIL",
        "checks": [{
            "name": "strict_exact_commit_refresh",
            "result": "FAIL",
            "exit_code": 3,
            "outcome": "failure",
            "output_tail": "ROUTING-001 detached branch mismatch",
        }],
    }


@pytest.mark.parametrize(
    ("mode", "validation", "refresh", "supervision", "artifact", "expected"),
    [
        ("governance", "failure", "success", "success", "success", False),
        ("governance", "success", "failure", "success", "success", False),
        ("governance", "success", "success", "failure", "success", False),
        ("governance", "success", "success", "success", "failure", False),
        ("governance", "success", "success", "success", "success", True),
        ("implementation", "success", "skipped", "success", "success", True),
    ],
)
def test_workflow_final_enforcement_truth_table(
    mode, validation, refresh, supervision, artifact, expected
):
    result = supervise.evaluate_workflow_outcomes(
        mode=mode,
        validation_outcome=validation,
        refresh_outcome=refresh,
        supervision_outcome=supervision,
        artifact_outcome=artifact,
    )
    assert result["pass"] is expected


def test_local_handoff_has_no_network_or_authority_mutation(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "docs/roadmap").mkdir(parents=True)
    (repo / ".gitignore").write_text(".codex-context/\n", encoding="utf-8")
    authority = repo / "docs/roadmap/roadmap_index.yaml"
    authority.write_text('{"sentinel":true}\n', encoding="utf-8")
    subprocess.run(["git", "init", "-b", "test"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "fixture"], cwd=repo, check=True, capture_output=True)
    before = authority.read_bytes()
    status_before = subprocess.run(["git", "status", "--porcelain"], cwd=repo, check=True, text=True, capture_output=True).stdout
    payload = supervise.build_payload(_inputs(), supervise.evaluate_gate(_inputs()))
    supervise.write_handoff_package(repo, payload)
    assert authority.read_bytes() == before
    assert subprocess.run(["git", "status", "--porcelain"], cwd=repo, check=True, text=True, capture_output=True).stdout == status_before
    source = Path(supervise.__file__).read_text(encoding="utf-8")
    assert all(token not in source for token in ("urllib", "requests", "http.client", "socket."))


def test_premature_closeout_is_impossible_and_comment_is_bounded():
    inputs = _inputs()
    before = copy.deepcopy(inputs)
    payload = supervise.build_payload(inputs, supervise.evaluate_gate(inputs))
    comment = supervise.render_pr_comment(payload)
    assert payload["acceptance_claimed"] is False
    assert payload["state_mutation_performed"] is False
    assert payload["task"]["status"] == "in_progress"
    assert payload["task"]["frontier"] == TASK_ID
    assert "acceptance" in payload["next_deterministic_action"].lower()
    assert "<!-- project-memory-supervision -->" in comment
    assert len(comment) < 8000
    assert inputs == before


def test_governance_maintenance_uses_tracked_task_registry_without_new_roadmap_child(tmp_path):
    repo = tmp_path / "repo"
    source = repo / "docs/roadmap/decisions/t011.md"
    source.parent.mkdir(parents=True)
    source.write_text("accepted\n", encoding="utf-8")
    registry = repo / "docs/project-memory/registries/tasks.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(json.dumps({
        "records": [{
            "task_id": "PHASE8-IMPL-026-T011",
            "lifecycle": {"status": "complete"},
            "depends_on": [],
            "provenance": {"source_locators": [{"path": "docs/roadmap/decisions/t011.md"}]},
            "is_application_frontier": False,
        }],
    }), encoding="utf-8")
    roadmap = {"active_frontier": {"next_readiness_task_id": TASK_ID}, "tasks": []}

    task, conflicts = supervise._task_inputs(
        repo, roadmap, "PHASE8-IMPL-026-T011", "governance"
    )

    assert task["status"] == "complete"
    assert task["frontier"] == TASK_ID
    assert task["application_task"] is False
    assert conflicts == []


def test_workflow_permissions_triggers_and_comment_boundary_are_safe():
    workflow = (supervise.ROOT / ".github/workflows/project-memory.yml").read_text(encoding="utf-8")
    assert "pull_request:" in workflow
    assert "push:" in workflow
    assert "workflow_dispatch:" in workflow
    assert "pull_request_target" not in workflow
    assert "contents: write" not in workflow
    assert "actions/upload-artifact@" in workflow
    assert "GITHUB_STEP_SUMMARY" in workflow
    assert "<!-- project-memory-supervision -->" in workflow
    assert "pull-requests: write" in workflow
    assert "permissions: {}" in workflow
    assert "git push" not in workflow
    assert "workflow_dispatch.inputs" not in workflow
    assert "actions/checkout@v7" in workflow
    assert "actions/setup-python@v6" in workflow
    assert "actions/upload-artifact@v7" in workflow
    assert "actions/download-artifact@v8" in workflow
    assert "actions/github-script@v9" in workflow
    assert "id: validation" in workflow
    assert "id: strict_refresh" in workflow
    assert "id: supervise" in workflow
    assert "if-no-files-found: error" in workflow
    assert "project-memory-handoff-artifact/project-memory-handoff.md" in workflow
    assert "project-memory-handoff-artifact/project-memory-handoff.json" in workflow
    assert "project-memory-handoff-artifact/SHA256SUMS" in workflow
    assert "ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION" not in workflow
    assert "secrets." not in workflow
    assert "git commit" not in workflow


def test_workflow_installs_only_pinned_project_memory_test_dependencies_before_validation():
    workflow = (supervise.ROOT / ".github/workflows/project-memory.yml").read_text(encoding="utf-8")
    requirements_relative = "tests/project_memory/requirements-ci.txt"
    requirements = (supervise.ROOT / requirements_relative).read_text(encoding="utf-8").splitlines()

    assert requirements == ["pytest==9.1.1"]
    assert all(line and "==" in line for line in requirements)

    setup_index = workflow.index("uses: actions/setup-python@v6")
    install_index = workflow.index("- name: Install pinned Project Memory CI test dependencies")
    validation_index = workflow.index("- name: Compile and validate Project Memory")
    assert setup_index < install_index < validation_index

    install_step = workflow[install_index:validation_index]
    assert "python3 -m pip install \\\n" in install_step
    assert "--disable-pip-version-check \\\n" in install_step
    assert "--no-input \\\n" in install_step
    assert f"-r {requirements_relative}" in install_step
    assert "continue-on-error" not in install_step
    assert "backend/requirements" not in install_step
    assert "training/requirements" not in install_step
    assert "frontend" not in install_step
    assert "python3 -m pip install pytest" not in workflow

    assert "python3 -m pytest tests/project_memory -q -p no:cacheprovider" in workflow
    assert "- name: Enforce gate and validation result" in workflow
    assert "--validation-outcome \"$VALIDATION_OUTCOME\"" in workflow
    assert "pull_request_target" not in workflow
    assert "contents: write" not in workflow
    assert "secrets." not in workflow
    assert "git commit" not in workflow
    assert "git push" not in workflow
