"""Focused tests for the deterministic T009 Plan Integrity engine."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.project_memory import build_plan_integrity_report as builder
from scripts.project_memory import plan_integrity as integrity


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=repo, capture_output=True, text=True, check=True,
    ).stdout.strip()


def _write(repo: Path, relative: str, content: str) -> None:
    path = repo / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _record(record_id: str, record_type: str, title: str, **values):
    record = {
        "id": record_id,
        "type": record_type,
        "schema_version": "1.0.0",
        "title": title,
        "authority_class": "authoritative",
        "lifecycle": {"status": "current"},
        "provenance": {"created_by": "TEST", "source_locators": []},
    }
    record.update(values)
    return record


def _task(task_id: str, status: str, depends_on=(), source: str | None = None, notes: str = ""):
    locators = [{"path": source}] if source else [{"path": "docs/roadmap/tasks/PHASE8-IMPL-026.md"}]
    return _record(
        f"task:{task_id}", "task", task_id,
        lifecycle={"status": status},
        provenance={"created_by": "TEST", "accepted_by": "TEST", "source_locators": locators},
        task_id=task_id,
        parent_task_id=None if task_id in {"PHASE8-IMPL-025", "PHASE8-IMPL-026"} else "PHASE8-IMPL-026",
        depends_on=list(depends_on),
        task_type="infrastructure",
        classification="test",
        is_application_frontier=False,
        is_blocking=False,
        notes=notes,
    )


def _boundary(boundary_id: str):
    return _record(
        f"boundary:{boundary_id}", "boundary", boundary_id,
        lifecycle={"status": "current"},
        provenance={"created_by": "TEST", "source_locators": [{"path": "docs/roadmap/tasks/PHASE8-IMPL-026.md"}]},
        boundary_id=boundary_id,
        category="product_safety",
        is_non_negotiable=True,
        description=boundary_id,
    )


def _application_task(
    task_id: str, status: str, *, is_frontier: bool
) -> dict:
    return _record(
        f"task:{task_id}", "task", task_id,
        lifecycle={"status": status},
        provenance={
            "created_by": "TEST",
            "accepted_by": "TEST",
            "source_locators": [{"path": "docs/roadmap/implementation_status.md"}],
        },
        task_id=task_id,
        parent_task_id="PHASE8-IMPL-024",
        depends_on=[],
        task_type="runtime",
        classification="test application task",
        is_application_frontier=is_frontier,
        is_blocking=False,
        notes="test application sequencing",
    )


def _plan() -> dict:
    tasks = [
        _record(
            "task:PHASE8-IMPL-024", "task", "PHASE8-IMPL-024",
            lifecycle={"status": "in_progress"},
            provenance={
                "created_by": "TEST", "accepted_by": "TEST",
                "source_locators": [{"path": "docs/roadmap/implementation_status.md"}],
            },
            task_id="PHASE8-IMPL-024", parent_task_id=None, depends_on=[],
            task_type="runtime", classification="application parent",
            is_application_frontier=True, is_blocking=True,
            notes="Active application implementation parent.",
        ),
        _application_task("PHASE8-IMPL-024-T003A", "complete", is_frontier=False),
        _application_task("PHASE8-IMPL-024-T003B", "planned", is_frontier=True),
        _task("PHASE8-IMPL-025", "planned"),
        _task("PHASE8-IMPL-026", "in_progress"),
        _task("PHASE8-IMPL-026-T003", "complete", source="scripts/t003.py"),
        _task("PHASE8-IMPL-026-T005", "complete", source="scripts/t005.py"),
        _task("PHASE8-IMPL-026-T006", "planned", ["PHASE8-IMPL-026-T005"], notes="owner-deferred contingent inactive"),
        _task("PHASE8-IMPL-026-T007", "planned", ["PHASE8-IMPL-026-T005"], notes="owner-deferred contingent inactive"),
        _task("PHASE8-IMPL-026-T008", "complete", source="scripts/t008.py", notes="Complete/PASS"),
        _task("PHASE8-IMPL-026-T009", "complete", ["PHASE8-IMPL-026-T003"], source="scripts/t009.py", notes="Complete/PASS"),
        _task("PHASE8-IMPL-026-T010", "planned", ["PHASE8-IMPL-026-T009"]),
        _task("PHASE8-IMPL-026-T011", "planned", ["PHASE8-IMPL-026-T010"]),
    ]
    return {
        "registries": {
            "tasks": {"records": tasks},
            "dependencies": {"records": []},
            "decisions": {"records": []},
            "owner-decisions": {"records": []},
            "features": {"records": []},
            "capabilities": {"records": []},
            "assets": {"records": []},
            "evidence": {"records": []},
            "tools": {"records": []},
            "boundaries": {"records": [_boundary(value) for value in integrity._REQUIRED_BOUNDARIES]},
        },
        "roadmap": {
            "docs/roadmap/enrichment/PHASE8-IMPL-026.enrichment.json": {
                "next_project_memory_task": "PHASE8-IMPL-026-T010 — next planned/inactive",
                "application_frontier_next_task": "PHASE8-IMPL-024-T003B",
            },
            "docs/roadmap/roadmap_index.yaml": {
                "active_frontier": {"next_readiness_task_id": "PHASE8-IMPL-024-T003B"}
            },
        },
        "source_hashes": {},
    }


def _closed_plan() -> dict:
    plan = _plan()
    tasks = plan["registries"]["tasks"]["records"]
    by_task = {record["task_id"]: record for record in tasks}
    for number in (1, 2, 4):
        task_id = f"PHASE8-IMPL-026-T{number:03d}"
        tasks.append(_task(task_id, "complete", source=f"scripts/t{number:03d}.py"))
    parent = by_task["PHASE8-IMPL-026"]
    parent["lifecycle"]["status"] = "complete"
    parent["provenance"]["source_locators"] = [{"path": "scripts/parent.py"}]
    parent["notes"] = "Complete and closed; ongoing maintenance is the operational procedure."
    for task_id in ("PHASE8-IMPL-026-T010", "PHASE8-IMPL-026-T011"):
        record = by_task[task_id]
        record["lifecycle"]["status"] = "complete"
        record["provenance"]["source_locators"] = [
            {"path": f"scripts/{task_id.rsplit('-', 1)[-1].lower()}.py"}
        ]
    for task_id in integrity._DEFERRED_PROJECT_MEMORY_TASKS:
        by_task[task_id]["provenance"]["owner_decision_ref"] = (
            "owner-decision:t006-t007-no-measured-gap-deferral"
        )
        by_task[task_id]["notes"] = "Owner-deferred, contingent, planned, inactive, and unimplemented."

    plan["registries"]["owner-decisions"]["records"] = [
        _record(
            "owner-decision:t006-t007-no-measured-gap-deferral",
            "owner_decision",
            "deferred pilots",
            affected_tasks=sorted(integrity._DEFERRED_PROJECT_MEMORY_TASKS),
        ),
        _record(
            "owner-decision:q154-event-driven-commit-bound-cadence",
            "owner_decision",
            "Q154 cadence",
            provenance={"created_by": "TEST", "accepted_by": "owner", "source_locators": []},
            affected_tasks=["PHASE8-IMPL-026", "PHASE8-IMPL-026-T011"],
        ),
    ]
    plan["registries"]["evidence"]["records"] = [
        _record(
            "evidence:t011",
            "evidence",
            "T011 accepted evidence",
            authority_class="accepted_evidence",
            associated_task_id="PHASE8-IMPL-026-T011",
        )
    ]
    enrichment = plan["roadmap"]["docs/roadmap/enrichment/PHASE8-IMPL-026.enrichment.json"]
    enrichment.update({
        "next_project_memory_task": None,
        "next_operational_step": "Maintain Project Memory through the T011 operational procedure.",
        "project_memory_maintenance": {
            "implementation_task": None,
            "mode": "operational_procedure",
            "procedure_task_id": "PHASE8-IMPL-026-T011",
        },
        "sole_next_implementation_focus": "PHASE8-IMPL-024-T003B",
        "status": "complete/PASS-WITH-FINDINGS",
    })
    closeout = "There is no next Project Memory implementation task; ongoing maintenance is the T011 procedure."
    plan["roadmap"].update({
        "docs/roadmap/tasks/PHASE8-IMPL-026.md": closeout,
        "docs/roadmap/implementation_status.md": closeout + " Sole next implementation focus: PHASE8-IMPL-024-T003B.",
        "docs/roadmap/task_backlog.md": closeout,
        "docs/roadmap/phase_map.md": closeout,
        "docs/roadmap/decision_log.md": closeout + " PHASE8-IMPL-024-T003B.",
        "docs/roadmap/open_questions.md": (
            "Q152 remains open. Q153 remains open. Resolved by PHASE8-IMPL-026-T011."
        ),
    })
    return plan


def _implementation(repo: Path, plan: dict) -> dict:
    sources = []
    for task in plan["registries"]["tasks"]["records"]:
        for path in integrity._record_locator_paths(task):
            exists = (
                path.startswith("scripts/")
                or path == "docs/roadmap/implementation_status.md"
            )
            sources.append({
                "record_id": task["id"], "registry": "tasks", "path": path,
                "authority_class": "authoritative", "safe": True, "exists": exists,
                "regular_file": exists, "tracked": exists,
            })
    for boundary in plan["registries"]["boundaries"]["records"]:
        sources.append({
            "record_id": boundary["id"], "registry": "boundaries",
            "path": "docs/roadmap/tasks/PHASE8-IMPL-026.md", "authority_class": "authoritative",
            "safe": True, "exists": True, "regular_file": True, "tracked": True,
        })
    return {
        "repository_root": str(repo), "branch": "test", "commit": "a" * 40,
        "dirty": False, "staged": False, "branch_matches": True, "commit_matches": True,
        "registry_validation_findings": [], "source_records": sources,
        "modified_paths": [], "untracked_paths": [],
    }


def _source(
    record_id: str,
    path: str,
    *,
    registry: str = "tasks",
    authority_class: str = "authoritative",
    safe: bool = True,
    exists: bool = True,
    regular_file: bool = True,
    tracked: bool = True,
) -> dict:
    return {
        "record_id": record_id,
        "registry": registry,
        "path": path,
        "authority_class": authority_class,
        "safe": safe,
        "exists": exists,
        "regular_file": regular_file,
        "tracked": tracked,
    }


def _set_task_source(plan: dict, task_id: str, path: str) -> dict:
    task = next(
        item for item in plan["registries"]["tasks"]["records"]
        if item["task_id"] == task_id
    )
    task["provenance"]["source_locators"] = [{"path": path}]
    return task


def _init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-b", "test")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")

    plan = _plan()
    tasks = plan["registries"]["tasks"]["records"]
    boundaries = plan["registries"]["boundaries"]["records"]
    manifest = {
        "registry_type": "manifest", "schema_version": "1.0.0", "architecture_version": "1.0.0",
        "registries": [
            {"filename": "boundaries.json", "record_type": "boundary", "required": True,
             "tracked_or_generated": "tracked", "allowed_authority_classes": ["authoritative"],
             "validation_order": 0, "cross_reference_policy": "allow_all"},
            {"filename": "tasks.json", "record_type": "task", "required": True,
             "tracked_or_generated": "tracked", "allowed_authority_classes": ["authoritative"],
             "validation_order": 1, "cross_reference_policy": "allow_all"},
        ],
        "generated_snapshot_output_root": ".codex-context/project-memory/",
    }
    _write(repo, "docs/project-memory/registries/manifest.json", json.dumps(manifest))
    _write(repo, "docs/project-memory/registries/tasks.json", json.dumps({"registry_type": "task", "schema_version": "1.0.0", "records": tasks}))
    _write(repo, "docs/project-memory/registries/boundaries.json", json.dumps({"registry_type": "boundary", "schema_version": "1.0.0", "records": boundaries}))
    _write(repo, "docs/roadmap/tasks/PHASE8-IMPL-026.md", "# fixture\n")
    _write(repo, "docs/roadmap/implementation_status.md", "# fixture application status\n")
    _write(repo, "docs/roadmap/enrichment/PHASE8-IMPL-026.enrichment.json", json.dumps(plan["roadmap"]["docs/roadmap/enrichment/PHASE8-IMPL-026.enrichment.json"]))
    _write(repo, "docs/roadmap/roadmap_index.yaml", json.dumps(plan["roadmap"]["docs/roadmap/roadmap_index.yaml"]))
    for name in ("t003", "t005", "t008", "t009"):
        _write(repo, f"scripts/{name}.py", f"# {name}\n")
    _write(repo, ".gitignore", ".codex-context/\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "fixture")
    return repo


@pytest.mark.parametrize(
    ("kwargs", "expected"),
    [
        ({}, "matching"),
        ({"observed": "different"}, "diverging"),
        ({"historical": True, "superseded_by": "decision:new"}, "superseded"),
        ({"unresolved_equal_authority_conflict": True}, "conflicting"),
        ({"required_evidence_present": False}, "insufficient_evidence"),
    ],
)
def test_all_five_q151_classifications(kwargs, expected):
    observed = kwargs.pop("observed", "same")
    assert integrity.classify_claims("same", observed, **kwargs) == expected


@pytest.mark.parametrize(
    ("findings", "expected"),
    [([], "READY"), ([{"blocking": False}], "READY_WITH_ADVISORIES"), ([{"blocking": True}], "BLOCKED")],
)
def test_readiness_tri_state(findings, expected):
    assert integrity.derive_readiness(findings)["result"] == expected


def test_confidence_basis_is_deterministic_and_not_confidence_as_truth():
    one = integrity.deterministic_confidence_basis(classification="insufficient_evidence", rule_id="R", evidence_count=0, required_evidence=True)
    two = integrity.deterministic_confidence_basis(classification="insufficient_evidence", rule_id="R", evidence_count=0, required_evidence=True)
    assert one == two
    assert one["inputs_complete"] is False
    assert integrity.classify_claims("x", "x", required_evidence_present=False) == "insufficient_evidence"


def test_current_lifecycle_deferred_t008_t009_and_t010_next(tmp_path):
    plan = _plan()
    comparisons = integrity.build_comparisons(plan, _implementation(tmp_path, plan))
    by_id = {item["subject_id"]: item for item in comparisons}
    assert by_id["PHASE8-IMPL-026-T006"]["classification"] == "matching"
    assert by_id["PHASE8-IMPL-026-T007"]["classification"] == "matching"
    assert by_id["PHASE8-IMPL-026-T008"]["observed_state"]["lifecycle"] == "complete"
    assert by_id["PHASE8-IMPL-026-T009"]["observed_state"]["lifecycle"] == "complete"
    assert by_id["project-memory-next-actionable"]["expected_state"]["task_id"] == "PHASE8-IMPL-026-T010"


def test_closed_parent_with_explicit_null_next_task_is_matching(tmp_path):
    plan = _closed_plan()
    implementation = _implementation(tmp_path, plan)
    comparisons = integrity.build_comparisons(plan, implementation)
    sequence = next(
        item for item in comparisons
        if item["subject_id"] == "project-memory-next-actionable"
    )
    report = integrity.run_plan_integrity_checks(plan, implementation, comparisons)
    assert sequence["classification"] == "matching"
    assert sequence["expected_state"] == {"task_id": None}
    assert sequence["observed_state"] == {"task_id": None}
    assert sequence["declaration"] == {
        "kind": "explicit_null",
        "valid": True,
        "reasons": [],
    }
    assert report["by_code"] == {"source_missing": 3}
    assert integrity.derive_readiness(report["findings"])["result"] == "READY_WITH_ADVISORIES"


def test_application_frontier_advances_without_reopening_project_memory(tmp_path):
    plan = _closed_plan()
    implementation = _implementation(tmp_path, plan)
    comparisons = integrity.build_comparisons(plan, implementation)
    by_type = {item["subject_type"]: item for item in comparisons}
    assert by_type["application_frontier"]["expected_state"] == {
        "task_id": "PHASE8-IMPL-024-T003B"
    }
    assert by_type["application_frontier"]["classification"] == "matching"
    assert by_type["sequence"]["expected_state"] == {"task_id": None}
    assert by_type["sequence"]["observed_state"] == {"task_id": None}
    assert by_type["sequence"]["classification"] == "matching"


def test_wrong_project_memory_application_frontier_still_blocks(tmp_path):
    plan = _closed_plan()
    plan["roadmap"]["docs/roadmap/enrichment/PHASE8-IMPL-026.enrichment.json"][
        "application_frontier_next_task"
    ] = "PHASE8-IMPL-024-T003A"
    implementation = _implementation(tmp_path, plan)
    report = integrity.run_plan_integrity_checks(plan, implementation)
    assert report["by_code"]["application_frontier_mismatch"] == 1
    assert integrity.derive_readiness(report["findings"])["result"] == "BLOCKED"


def test_generated_inputs_cannot_derive_project_memory_task_from_application_frontier(tmp_path):
    plan = _closed_plan()
    implementation = _implementation(tmp_path, plan)
    implementation["generated_next_task"] = "PHASE8-IMPL-024-T003B"
    comparisons = integrity.build_comparisons(plan, implementation)
    sequence = next(
        item for item in comparisons
        if item["subject_id"] == "project-memory-next-actionable"
    )
    assert sequence["expected_state"] == {"task_id": None}
    assert sequence["observed_state"] == {"task_id": None}
    assert sequence["classification"] == "matching"


def test_active_parent_with_null_next_task_remains_blocked(tmp_path):
    plan = _closed_plan()
    parent = next(
        item for item in plan["registries"]["tasks"]["records"]
        if item["task_id"] == "PHASE8-IMPL-026"
    )
    parent["lifecycle"]["status"] = "in_progress"
    implementation = _implementation(tmp_path, plan)
    comparisons = integrity.build_comparisons(plan, implementation)
    sequence = next(
        item for item in comparisons
        if item["subject_id"] == "project-memory-next-actionable"
    )
    report = integrity.run_plan_integrity_checks(plan, implementation, comparisons)
    blockers = [item["code"] for item in report["findings"] if item["blocking"]]
    assert sequence["classification"] == "insufficient_evidence"
    assert sequence["declaration"]["valid"] is False
    assert sequence["declaration"]["reasons"] == ["project_memory_parent_not_complete"]
    assert blockers == ["next_actionable_mismatch"]
    assert integrity.derive_readiness(report["findings"])["result"] == "BLOCKED"


def test_incomplete_actionable_project_memory_child_with_null_remains_blocked(tmp_path):
    plan = _closed_plan()
    child = next(
        item for item in plan["registries"]["tasks"]["records"]
        if item["task_id"] == "PHASE8-IMPL-026-T011"
    )
    child["lifecycle"]["status"] = "planned"
    child["provenance"].pop("accepted_by", None)
    implementation = _implementation(tmp_path, plan)
    comparisons = integrity.build_comparisons(plan, implementation)
    sequence = next(
        item for item in comparisons
        if item["subject_id"] == "project-memory-next-actionable"
    )
    assert sequence["classification"] == "insufficient_evidence"
    assert sequence["declaration"]["valid"] is False
    assert sequence["declaration"]["reasons"] == [
        "required_child_not_complete:PHASE8-IMPL-026-T011"
    ]


@pytest.mark.parametrize(
    "path",
    [
        "scripts/delivery.py",
        "tests/test_delivery.py",
        "backend/delivery.py",
        "frontend/delivery.ts",
        "docs/project-memory/delivery.md",
        ".agents/skills/delivery/SKILL.md",
        ".opencode/agents/delivery.md",
    ],
)
def test_task_linked_tracked_delivery_roots_prove_implementation(tmp_path, path):
    plan = _plan()
    task = _set_task_source(plan, "PHASE8-IMPL-026-T008", path)
    implementation = _implementation(tmp_path, plan)
    implementation["source_records"] = [_source(task["id"], path)]
    assessment = integrity._implementation_assessment(task, plan, implementation)
    assert assessment["implementation_present"] is True
    assert assessment["tracked_delivery_artifacts"] == [path]


def test_root_agents_counts_only_when_directly_task_linked(tmp_path):
    plan = _plan()
    task = _set_task_source(plan, "PHASE8-IMPL-026-T008", "AGENTS.md")
    implementation = _implementation(tmp_path, plan)
    implementation["source_records"] = [_source(task["id"], "AGENTS.md")]
    assert integrity._implementation_present(task, plan, implementation) is True

    evidence = _record(
        "evidence:agents", "evidence", "agents",
        authority_class="accepted_evidence",
        associated_task_id=task["task_id"],
    )
    plan["registries"]["evidence"]["records"] = [evidence]
    implementation["source_records"] = [
        _source(
            evidence["id"], "AGENTS.md", registry="evidence",
            authority_class="accepted_evidence",
        )
    ]
    assert integrity._implementation_present(task, plan, implementation) is False


def test_t008_real_non_code_locator_pattern_is_matching(tmp_path):
    plan = _plan()
    task = next(
        item for item in plan["registries"]["tasks"]["records"]
        if item["task_id"] == "PHASE8-IMPL-026-T008"
    )
    task_paths = [
        "docs/project-memory/ask-protocol.md",
        ".agents/skills/project-memory-read/SKILL.md",
        ".opencode/agents/project-memory-ask.md",
        "docs/roadmap/decisions/PHASE8-IMPL-026-T008-shared-agent-guidance-and-project-memory-ask.md",
    ]
    task["provenance"]["source_locators"] = [{"path": path} for path in task_paths]
    evidence = _record(
        "evidence:t008", "evidence", "T008 evidence",
        authority_class="accepted_evidence",
        associated_task_id=task["task_id"],
        provenance={
            "created_by": "TEST",
            "accepted_by": "TEST",
            "source_locators": [
                {"path": "tests/project_memory/test_agent_guidance_and_ask.py"},
                {"path": "scripts/project_memory/validate_agent_guidance.py"},
            ],
        },
    )
    plan["registries"]["evidence"]["records"] = [evidence]
    implementation = _implementation(tmp_path, plan)
    implementation["source_records"] = [
        *[_source(task["id"], path) for path in task_paths],
        _source(
            evidence["id"],
            "tests/project_memory/test_agent_guidance_and_ask.py",
            registry="evidence", authority_class="accepted_evidence",
        ),
        _source(
            evidence["id"],
            "scripts/project_memory/validate_agent_guidance.py",
            registry="evidence", authority_class="accepted_evidence",
        ),
    ]
    comparisons = integrity.build_comparisons(plan, implementation)
    t008 = next(item for item in comparisons if item["subject_id"] == task["task_id"])
    findings = integrity.run_plan_integrity_checks(plan, implementation, comparisons)
    assert t008["classification"] == "matching"
    assert t008["observed_state"]["lifecycle"] == "complete"
    assert set(t008["observed_state"]["tracked_delivery_artifacts"]) == {
        "docs/project-memory/ask-protocol.md",
        ".agents/skills/project-memory-read/SKILL.md",
        ".opencode/agents/project-memory-ask.md",
        "tests/project_memory/test_agent_guidance_and_ask.py",
        "scripts/project_memory/validate_agent_guidance.py",
    }
    assert not any(
        item["code"] == "task_state_mismatch"
        and item["subject_id"] == task["task_id"]
        for item in findings["findings"]
    )


@pytest.mark.parametrize(
    "path",
    [
        "docs/roadmap/tasks/PHASE8-IMPL-026.md",
        "docs/roadmap/decisions/PHASE8-IMPL-026-T008-shared-agent-guidance-and-project-memory-ask.md",
        "docs/roadmap/implementation_status.md",
    ],
)
def test_roadmap_and_status_support_alone_do_not_prove_implementation(tmp_path, path):
    plan = _plan()
    task = _set_task_source(plan, "PHASE8-IMPL-026-T008", path)
    implementation = _implementation(tmp_path, plan)
    implementation["source_records"] = [_source(task["id"], path)]
    comparison = next(
        item for item in integrity.build_comparisons(plan, implementation)
        if item["subject_id"] == task["task_id"]
    )
    assert comparison["classification"] == "insufficient_evidence"
    assert comparison["observed_state"]["implementation_present"] is False


def test_registry_lifecycle_and_generated_evidence_alone_do_not_prove_implementation(tmp_path):
    plan = _plan()
    task = next(
        item for item in plan["registries"]["tasks"]["records"]
        if item["task_id"] == "PHASE8-IMPL-026-T008"
    )
    implementation = _implementation(tmp_path, plan)
    implementation["source_records"] = []
    assert integrity._implementation_present(task, plan, implementation) is False

    implementation["source_records"] = [
        _source(
            task["id"], "docs/project-memory/generated.md",
            authority_class="generated_evidence",
        )
    ]
    assert integrity._implementation_present(task, plan, implementation) is False


@pytest.mark.parametrize(
    "values",
    [
        {"tracked": False},
        {"exists": False},
        {"safe": False},
        {"regular_file": False},
    ],
)
def test_untracked_missing_unsafe_or_directory_locator_does_not_prove_implementation(
    tmp_path, values
):
    plan = _plan()
    path = "docs/project-memory/delivery.md"
    task = _set_task_source(plan, "PHASE8-IMPL-026-T008", path)
    implementation = _implementation(tmp_path, plan)
    implementation["source_records"] = [_source(task["id"], path, **values)]
    comparison = next(
        item for item in integrity.build_comparisons(plan, implementation)
        if item["subject_id"] == task["task_id"]
    )
    assert comparison["classification"] == "insufficient_evidence"
    assert comparison["observed_state"]["implementation_present"] is False


def test_planned_task_with_only_roadmap_document_remains_planned(tmp_path):
    plan = _plan()
    implementation = _implementation(tmp_path, plan)
    task = next(
        item for item in plan["registries"]["tasks"]["records"]
        if item["task_id"] == "PHASE8-IMPL-026-T010"
    )
    implementation["source_records"].append(
        _source(task["id"], "docs/roadmap/tasks/PHASE8-IMPL-026.md")
    )
    comparison = next(
        item for item in integrity.build_comparisons(plan, implementation)
        if item["subject_id"] == task["task_id"]
    )
    assert comparison["classification"] == "matching"
    assert comparison["observed_state"]["lifecycle"] == "planned"


def test_complete_task_with_tracked_non_code_delivery_can_match(tmp_path):
    plan = _plan()
    path = "docs/project-memory/implemented-contract.md"
    task = _set_task_source(plan, "PHASE8-IMPL-026-T008", path)
    implementation = _implementation(tmp_path, plan)
    implementation["source_records"] = [_source(task["id"], path)]
    comparison = next(
        item for item in integrity.build_comparisons(plan, implementation)
        if item["subject_id"] == task["task_id"]
    )
    assert comparison["classification"] == "matching"
    assert comparison["observed_state"]["implementation_present"] is True


def test_lifecycle_divergence_and_next_actionable_mismatch(tmp_path):
    plan = _plan()
    plan["registries"]["tasks"]["records"][-2]["lifecycle"]["status"] = "complete"
    plan["roadmap"]["docs/roadmap/enrichment/PHASE8-IMPL-026.enrichment.json"]["next_project_memory_task"] = "PHASE8-IMPL-026-T009"
    comparisons = integrity.build_comparisons(plan, _implementation(tmp_path, plan))
    checks = integrity.run_plan_integrity_checks(plan, _implementation(tmp_path, plan), comparisons)
    assert checks["by_code"]["task_state_mismatch"] >= 1
    assert checks["by_code"]["next_actionable_mismatch"] == 1


@pytest.mark.parametrize(("key", "code"), [("dirty", "working_tree_dirty"), ("staged", "staging_not_empty"), ("branch_matches", "branch_mismatch"), ("commit_matches", "commit_mismatch")])
def test_repository_binding_failures(tmp_path, key, code):
    plan = _plan()
    implementation = _implementation(tmp_path, plan)
    implementation[key] = False if key.endswith("matches") else True
    findings = integrity.run_plan_integrity_checks(plan, implementation)["by_code"]
    assert findings[code] == 1


def test_registry_failure_blocks(tmp_path):
    plan = _plan()
    implementation = _implementation(tmp_path, plan)
    implementation["registry_validation_findings"] = [{"level": "error", "code": "BAD"}]
    report = integrity.run_plan_integrity_checks(plan, implementation)
    assert report["by_code"]["registry_validation_failed"] == 1
    assert integrity.derive_readiness(report["findings"])["result"] == "BLOCKED"


def test_missing_dependency_cycle_and_incomplete_prerequisite(tmp_path):
    plan = _plan()
    tasks = plan["registries"]["tasks"]["records"]
    t009 = next(item for item in tasks if item["task_id"].endswith("T009"))
    t003 = next(item for item in tasks if item["task_id"].endswith("T003"))
    t009["depends_on"].append("PHASE8-IMPL-026-MISSING")
    t003["depends_on"] = ["PHASE8-IMPL-026-T009"]
    t003["lifecycle"]["status"] = "planned"
    report = integrity.run_plan_integrity_checks(plan, _implementation(tmp_path, plan))
    assert report["by_code"]["missing_required_dependency"] == 1
    assert report["by_code"]["dependency_cycle"] == 1
    assert report["by_code"]["completed_task_incomplete_dependency"] >= 1


def test_completed_task_missing_evidence_and_stale_missing_evidence(tmp_path):
    plan = _plan()
    implementation = _implementation(tmp_path, plan)
    implementation["source_records"] = [item for item in implementation["source_records"] if item["record_id"] != "task:PHASE8-IMPL-026-T008"]
    implementation["source_records"].append({
        "record_id": "task:PHASE8-IMPL-026-T008", "path": "missing.py", "safe": True,
        "exists": False, "authority_class": "authoritative", "registry": "tasks",
    })
    report = integrity.run_plan_integrity_checks(plan, implementation)
    assert report["by_code"]["completed_task_missing_required_evidence"] == 1
    assert report["by_code"]["source_missing"] >= 1


def test_decision_locator_reference_supersession_and_current_conflict(tmp_path):
    plan = _plan()
    old = _record(
        "decision:old", "decision", "old", lifecycle={"status": "superseded", "superseded_by": "decision:new"},
        decision_id="old", decision_path="missing.md", question="same", selected_option="A",
        affected_tasks=["PHASE8-IMPL-026-MISSING"],
    )
    new = _record(
        "decision:new", "decision", "new", lifecycle={"status": "current", "supersedes": ["decision:old"]},
        decision_id="new", decision_path="missing-new.md", question="same", selected_option="B", affected_tasks=[],
    )
    conflict = _record(
        "decision:conflict", "decision", "conflict", decision_id="conflict",
        decision_path="missing-conflict.md", question="same", selected_option="C", affected_tasks=[],
    )
    plan["registries"]["decisions"]["records"] = [old, new, conflict]
    report = integrity.run_plan_integrity_checks(plan, _implementation(tmp_path, plan))
    assert report["by_code"]["decision_locator_invalid"] == 3
    assert report["by_code"]["decision_task_reference_missing"] == 1
    assert "supersession_invalid" not in report["by_code"]
    assert report["by_code"]["unresolved_authoritative_conflict"] == 1


def test_invalid_supersession_and_cycle(tmp_path):
    plan = _plan()
    a = _record("decision:a", "decision", "a", lifecycle={"status": "current", "supersedes": ["decision:b"]}, decision_id="a", decision_path="x", affected_tasks=[])
    b = _record("decision:b", "decision", "b", lifecycle={"status": "current", "supersedes": ["decision:a"]}, decision_id="b", decision_path="y", affected_tasks=[])
    plan["registries"]["decisions"]["records"] = [a, b]
    report = integrity.run_plan_integrity_checks(plan, _implementation(tmp_path, plan))
    assert report["by_code"]["supersession_invalid"] == 2
    assert report["by_code"]["supersession_cycle"] == 1


def test_generated_evidence_authority_rejected(tmp_path):
    plan = _plan()
    plan["registries"]["features"]["records"] = [_record("feature:bad", "feature", "bad", authority_class="generated_evidence")]
    report = integrity.run_plan_integrity_checks(plan, _implementation(tmp_path, plan))
    assert report["by_code"]["generated_evidence_claims_authority"] == 1


def test_exact_duplicate_ownership_and_capability_overlap_only(tmp_path):
    plan = _plan()
    plan["registries"]["assets"]["records"] = [
        _record("asset:a", "asset", "a", asset_path="same", asset_id="a"),
        _record("asset:b", "asset", "b", asset_path="same", asset_id="b"),
    ]
    plan["registries"]["capabilities"]["records"] = [
        _record("capability:a", "capability", "Exact", associated_tasks=["T"], capability_id="a"),
        _record("capability:b", "capability", "Exact", associated_tasks=["T"], capability_id="b"),
        _record("capability:c", "capability", "Exact-ish", associated_tasks=["T"], capability_id="c"),
    ]
    report = integrity.run_plan_integrity_checks(plan, _implementation(tmp_path, plan))
    assert report["by_code"]["exact_ownership_conflict"] == 1
    assert report["by_code"]["exact_capability_overlap"] == 1
    overlaps = [item for item in report["findings"] if item["code"] == "exact_capability_overlap"]
    assert overlaps[0]["evidence"]["overlap_outcome"] == "REUSE"


def test_frontier_ph8_impl_025_and_product_boundary_violations(tmp_path):
    plan = _plan()
    plan["roadmap"]["docs/roadmap/roadmap_index.yaml"]["active_frontier"]["next_readiness_task_id"] = "OTHER"
    next(item for item in plan["registries"]["tasks"]["records"] if item["task_id"] == "PHASE8-IMPL-025")["lifecycle"]["status"] = "in_progress"
    plan["registries"]["boundaries"]["records"] = []
    report = integrity.run_plan_integrity_checks(plan, _implementation(tmp_path, plan))
    assert report["by_code"]["application_frontier_mismatch"] == 1
    assert report["by_code"]["ph8_impl_025_activated"] == 1
    assert report["by_code"]["product_boundary_violation"] == len(integrity._REQUIRED_BOUNDARIES)


def test_deterministic_ordering_and_byte_identical_core_output(tmp_path):
    plan = _plan()
    implementation = _implementation(tmp_path, plan)
    first = integrity.run_plan_integrity_checks(copy.deepcopy(plan), copy.deepcopy(implementation))
    second = integrity.run_plan_integrity_checks(copy.deepcopy(plan), copy.deepcopy(implementation))
    assert json.dumps(first, sort_keys=True).encode() == json.dumps(second, sort_keys=True).encode()
    assert first["findings"] == integrity.sort_findings(reversed(first["findings"]))


def test_atomic_exact_package_inventory_checksums_and_overwrite(tmp_path):
    repo = _init_repo(tmp_path)
    result = builder.build_plan_integrity_package(repo, ".codex-context/project-memory", "PHASE8-IMPL-026-T009", "20260101T000000Z")
    package = Path(result["output_directory"])
    assert sorted(item.name for item in package.iterdir()) == list(builder.EXACT_PACKAGE_FILES)
    assert builder.validate_plan_integrity_package(package)["result"] == "PASS"
    metadata = json.loads((package / "run-metadata.json").read_text())
    assert metadata["authority_class"] == "generated_evidence"
    assert metadata["bound_commit"] == _git(repo, "rev-parse", "HEAD")
    with pytest.raises(FileExistsError):
        builder.build_plan_integrity_package(repo, ".codex-context/project-memory", "PHASE8-IMPL-026-T009", "20260101T000000Z")


def test_dirty_staged_registry_failure_and_cleanup(tmp_path):
    repo = _init_repo(tmp_path)
    _write(repo, "dirty.txt", "dirty")
    with pytest.raises(RuntimeError, match="dirty"):
        builder.build_plan_integrity_package(repo, ".codex-context/project-memory", "T", "20260101T000001Z")
    _git(repo, "add", "dirty.txt")
    with pytest.raises(RuntimeError, match="dirty|Staging"):
        builder.build_plan_integrity_package(repo, ".codex-context/project-memory", "T", "20260101T000002Z")
    assert not (repo / ".codex-context/project-memory/T").exists()


def test_direct_cli_json_inside_and_outside_repository(tmp_path):
    repo = _init_repo(tmp_path)
    script = Path(__file__).resolve().parents[2] / "scripts/project_memory/build_plan_integrity_report.py"
    inside = subprocess.run(
        [sys.executable, str(script), "--repo-root", ".", "--output-root", ".codex-context/project-memory", "--task-id", "T", "--run-id", "20260101T000003Z", "--json"],
        cwd=repo, capture_output=True, text=True,
    )
    assert inside.returncode == 0, inside.stderr + inside.stdout
    assert json.loads(inside.stdout)["authority_class"] == "generated_evidence"
    outside = subprocess.run(
        [sys.executable, str(script), "--repo-root", str(repo), "--output-root", ".codex-context/project-memory", "--task-id", "T", "--run-id", "20260101T000004Z", "--json"],
        cwd=tmp_path, capture_output=True, text=True,
    )
    assert outside.returncode == 0, outside.stderr + outside.stdout
    assert json.loads(outside.stdout)["readiness"] in integrity.READINESS_RESULTS


def test_engine_has_no_network_model_subprocess_or_mutation_implementation():
    source = Path(integrity.__file__).read_text(encoding="utf-8")
    assert "import subprocess" not in source
    assert "urllib" not in source and "requests" not in source
    assert "ollama" not in source.lower()
    assert "write_text(" not in source and "write_bytes(" not in source
    assert "roadmap_mutation" not in source
