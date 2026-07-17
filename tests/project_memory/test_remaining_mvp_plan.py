"""Focused regressions for the owner-accepted remaining-MVP delivery graph."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.project_memory import validate_registries


ROOT = Path(__file__).resolve().parents[2]


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _roadmap_tasks() -> dict[str, dict]:
    return {item["id"]: item for item in _load("docs/roadmap/roadmap_index.yaml")["tasks"]}


def _normalized_tasks() -> dict[str, dict]:
    return {item["task_id"]: item for item in _load("docs/project-memory/registries/tasks.json")["records"]}


def test_phase8_impl_024_controlling_order():
    tasks = _roadmap_tasks()
    assert tasks["PHASE8-IMPL-024-T006"]["depends_on"] == ["PHASE8-IMPL-024-T003"]
    assert tasks["PHASE8-IMPL-024-T007"]["depends_on"] == ["PHASE8-IMPL-024-T006"]
    assert tasks["PHASE8-IMPL-024-T007A"]["depends_on"] == ["PHASE8-IMPL-024-T006C"]
    assert tasks["PHASE8-IMPL-024-T007B"]["depends_on"] == ["PHASE8-IMPL-024-T007A"]
    assert tasks["PHASE8-IMPL-024-T007C"]["depends_on"] == ["PHASE8-IMPL-024-T007B"]
    assert tasks["PHASE8-IMPL-024-T004"]["depends_on"] == ["PHASE8-IMPL-024-T007C"]
    assert tasks["PHASE8-IMPL-024-T005"]["depends_on"] == ["PHASE8-IMPL-024-T004C"]
    assert tasks["PHASE8-IMPL-024-T008"]["depends_on"] == ["PHASE8-IMPL-024-T005C"]


def test_phase8_impl_025_activation_is_parent_closeout_only():
    roadmap = _load("docs/roadmap/roadmap_index.yaml")
    tasks = {item["id"]: item for item in roadmap["tasks"]}
    assert roadmap["active_frontier"]["planned_architecture_activation_after"] == ["PHASE8-IMPL-024"]
    assert tasks["PHASE8-IMPL-025"]["depends_on"] == ["PHASE8-IMPL-024"]
    assert tasks["PHASE8-IMPL-025"]["status"] == "planned"
    assert tasks["PHASE8-IMPL-025"]["next_child_task"] is None


def test_phase8_impl_025_graph_is_branched_and_joined():
    tasks = _roadmap_tasks()
    assert tasks["PHASE8-IMPL-025-T004"]["depends_on"] == ["PHASE8-IMPL-025-T003"]
    assert tasks["PHASE8-IMPL-025-T005"]["depends_on"] == ["PHASE8-IMPL-025-T003"]
    assert tasks["PHASE8-IMPL-025-T007"]["depends_on"] == ["PHASE8-IMPL-025-T003"]
    assert set(tasks["PHASE8-IMPL-025-T008"]["depends_on"]) == {
        "PHASE8-IMPL-025-T004", "PHASE8-IMPL-025-T006", "PHASE8-IMPL-025-T007",
    }
    for task_id in ("PHASE8-IMPL-025-T009", "PHASE8-IMPL-025-T010", "PHASE8-IMPL-025-T011"):
        assert tasks[task_id]["depends_on"] == ["PHASE8-IMPL-025-T008"]
    assert set(tasks["PHASE8-IMPL-025-T012"]["depends_on"]) == {
        "PHASE8-IMPL-025-T003F", "PHASE8-IMPL-025-T003G",
        "PHASE8-IMPL-025-T009", "PHASE8-IMPL-025-T010",
        "PHASE8-IMPL-025-T010H", "PHASE8-IMPL-025-T011",
        "PHASE8-IMPL-025-T011H",
    }


def test_terminal_task_and_accepted_children_are_present():
    tasks = _roadmap_tasks()
    normalized = _normalized_tasks()
    expected = {
        "PHASE8-IMPL-025-T003F",
        "PHASE8-IMPL-025-T003G",
        "PHASE8-IMPL-025-T010H",
        "PHASE8-IMPL-025-T011H",
        "PHASE8-IMPL-027",
    }
    assert expected <= tasks.keys()
    assert expected <= normalized.keys()
    assert tasks["PHASE8-IMPL-027"]["depends_on"] == ["PHASE8-IMPL-025-T012"]


def test_current_frontier_and_project_memory_state_are_preserved():
    roadmap = _load("docs/roadmap/roadmap_index.yaml")
    tasks = _normalized_tasks()
    assert roadmap["active_frontier"]["next_readiness_task_id"] == "PHASE8-IMPL-024-T003B"
    assert tasks["PHASE8-IMPL-024-T003B"]["lifecycle"]["status"] == "in_progress"
    assert tasks["PHASE8-IMPL-025"]["lifecycle"]["status"] == "planned"
    assert tasks["PHASE8-IMPL-026"]["lifecycle"]["status"] == "complete"
    active_pm_maintenance = {
        item["task_id"]
        for item in tasks.values()
        if item["task_id"].startswith("PHASE8-IMPL-026-")
        and item["lifecycle"]["status"] == "in_progress"
    }
    assert active_pm_maintenance <= {"PHASE8-IMPL-026-T012"}
    if active_pm_maintenance:
        assert tasks["PHASE8-IMPL-026-T012"]["task_type"] == "governance"
        assert tasks["PHASE8-IMPL-026-T012"]["is_application_frontier"] is False


def test_tracked_registry_has_complete_remaining_mvp_coverage():
    findings = validate_registries.validate()
    errors = [item for item in findings if item["level"] == "error"]
    assert not errors, errors
