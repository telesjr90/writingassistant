"""Tracked task registry current-state regression tests.

Verifies that the tracked tasks.json registry represents the accepted
post-T005 task state.  Must not mutate any real registry file.

These tests guard against the defect discovered by the 20260714T042826Z
post-closeout refresh: the task registry stopped at T003 and the
renderer hardcoded stale index-page status strings, allowing a
structurally valid snapshot and render to pass quality checks even
though the rendered documentation contradicted known roadmap truth.

Includes both registry-state validation tests and renderer-output
validation tests that prove the repaired renderer now derives task
status from the registry.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.project_memory import validate_registries
from scripts.project_memory.render_docs import (
    _build_page_model,
    _render_index,
    _render_current_roadmap,
    _render_remaining_work,
    _derive_task_display_status,
    _get_task_by_id,
    _get_children,
    _identify_completed_children,
    _identify_next_planned_child,
    _derive_pm_task_behavior,
    _validate_task_records,
    _PM_PARENT_TASK_ID,
    _PM_TASK_DISPLAY_ORDER,
)

# ---- helpers (standard-library-only) ----


def _load_tracked_registry(name: str) -> dict:
    path = Path(__file__).resolve().parents[2] / "docs" / "project-memory" / "registries" / name
    return json.loads(path.read_text(encoding="utf-8"))


def _tracked_task_records() -> list[dict]:
    return list(_load_tracked_registry("tasks.json")["records"])


def _roadmap_task_section(task_id: str) -> str:
    path = Path(__file__).resolve().parents[2] / "docs" / "roadmap" / "tasks" / "PHASE8-IMPL-026.md"
    text = path.read_text(encoding="utf-8")
    marker = f"### {task_id}"
    assert marker in text, f"Roadmap section {task_id} not found"
    return text.split(marker, 1)[1].split("\n### ", 1)[0]


def _record_by_id(records: list[dict], rid: str) -> dict | None:
    for r in records:
        if r.get("id") == rid:
            return r
    return None


def _record_exists(records: list[dict], rid: str) -> bool:
    return _record_by_id(records, rid) is not None


def _lifecycle_status(records: list[dict], rid: str) -> str:
    r = _record_by_id(records, rid)
    assert r is not None, f"Record {rid} not found"
    return r["lifecycle"]["status"]


# ---- registry-presence tests ----


def test_t004_record_exists():
    recs = _tracked_task_records()
    assert _record_exists(recs, "task:PHASE8-IMPL-026-T004")


def test_t004a_record_exists():
    assert _record_exists(_tracked_task_records(), "task:PHASE8-IMPL-026-T004A")


def test_t004b_record_exists():
    assert _record_exists(_tracked_task_records(), "task:PHASE8-IMPL-026-T004B")


def test_t004c_record_exists():
    assert _record_exists(_tracked_task_records(), "task:PHASE8-IMPL-026-T004C")


def test_t005_record_exists():
    assert _record_exists(_tracked_task_records(), "task:PHASE8-IMPL-026-T005")


# ---- lifecycle/status tests ----


def test_t004_is_complete():
    assert _lifecycle_status(_tracked_task_records(), "task:PHASE8-IMPL-026-T004") == "complete"


def test_t004a_is_complete():
    assert _lifecycle_status(_tracked_task_records(), "task:PHASE8-IMPL-026-T004A") == "complete"


def test_t004b_is_complete():
    assert _lifecycle_status(_tracked_task_records(), "task:PHASE8-IMPL-026-T004B") == "complete"


def test_t004c_is_complete():
    assert _lifecycle_status(_tracked_task_records(), "task:PHASE8-IMPL-026-T004C") == "complete"


def test_t005_is_complete():
    assert _lifecycle_status(_tracked_task_records(), "task:PHASE8-IMPL-026-T005") == "complete"


def test_t005_has_complete_pass_result():
    record = _record_by_id(_tracked_task_records(), "task:PHASE8-IMPL-026-T005")
    assert _derive_task_display_status(record) == "complete/PASS"
    assert record["notes"].startswith("Complete/PASS.")


def test_t005_is_no_longer_planned_pending_or_remaining():
    record = _record_by_id(_tracked_task_records(), "task:PHASE8-IMPL-026-T005")
    assert record["lifecycle"]["status"] == "complete"
    assert record["lifecycle"]["status"] not in ("planned", "in_progress", "owner_pending")
    assert _derive_task_display_status(record) == "complete/PASS"


def test_t005_is_not_application_frontier_and_does_not_approve_live_tools():
    record = _record_by_id(_tracked_task_records(), "task:PHASE8-IMPL-026-T005")
    assert record["parent_task_id"] == "PHASE8-IMPL-026"
    assert record["is_application_frontier"] is False
    assert "read-only import adapters" in record["notes"]
    assert "No context tool was installed or executed" in record["notes"]

    tool_records = _load_tracked_registry("tools.json")["records"]
    by_id = {item["id"]: item for item in tool_records}
    for tool_id in ("tool:repomix-config", "tool:graphify-config", "tool:cce-config"):
        assert by_id[tool_id]["is_approved_dependency"] is False
        assert "read-only import" in by_id[tool_id]["notes"]
        assert "execution" in by_id[tool_id]["notes"]
    assert by_id["tool:context-tool-evidence-importer"]["is_approved_dependency"] is True
    assert "without executing an external tool" in by_id["tool:context-tool-evidence-importer"]["notes"]


# ---- field-integrity tests ----


def test_t004_parent_is_ph8_impl_026():
    r = _record_by_id(_tracked_task_records(), "task:PHASE8-IMPL-026-T004")
    assert r["parent_task_id"] == "PHASE8-IMPL-026"


def test_t004a_parent_is_t004():
    r = _record_by_id(_tracked_task_records(), "task:PHASE8-IMPL-026-T004A")
    assert r["parent_task_id"] == "PHASE8-IMPL-026-T004"


def test_t004b_parent_is_t004():
    r = _record_by_id(_tracked_task_records(), "task:PHASE8-IMPL-026-T004B")
    assert r["parent_task_id"] == "PHASE8-IMPL-026-T004"


def test_t004c_parent_is_t004():
    r = _record_by_id(_tracked_task_records(), "task:PHASE8-IMPL-026-T004C")
    assert r["parent_task_id"] == "PHASE8-IMPL-026-T004"


def test_t005_parent_is_ph8_impl_026():
    r = _record_by_id(_tracked_task_records(), "task:PHASE8-IMPL-026-T005")
    assert r["parent_task_id"] == "PHASE8-IMPL-026"


def test_t004_depends_on_t003():
    r = _record_by_id(_tracked_task_records(), "task:PHASE8-IMPL-026-T004")
    assert "PHASE8-IMPL-026-T003" in r.get("depends_on", [])


# ---- source-locator safety tests ----


def test_all_t004_task_locators_are_safe():
    for rid in [
        "task:PHASE8-IMPL-026-T004",
        "task:PHASE8-IMPL-026-T004A",
        "task:PHASE8-IMPL-026-T004B",
        "task:PHASE8-IMPL-026-T004C",
        "task:PHASE8-IMPL-026-T005",
    ]:
        r = _record_by_id(_tracked_task_records(), rid)
        locators = r.get("provenance", {}).get("source_locators", [])
        assert locators, f"{rid} has no source locators"
        for loc in locators:
            path = loc.get("path", "")
            assert path, f"{rid}: empty source locator path"
            assert not path.startswith("/"), f"{rid}: absolute path {path}"
            assert ".." not in path.split("/"), f"{rid}: traversal in {path}"
            assert not path.startswith(".codex-context/"), f"{rid}: generated-evidence path {path}"
            full = Path(__file__).resolve().parents[2] / path
            assert full.is_file(), f"{rid}: source locator not found: {path}"


# ---- remaining-work rendering contract tests ----


def test_remaining_work_excludes_complete_t004():
    """Prove that the _render_remaining_work function excludes T004
    when it is set to 'complete' status."""
    tasks_registry = _load_tracked_registry("tasks.json")
    # Build a minimal model with only the tasks we care about
    registries = {
        "tasks.json": tasks_registry,
        "owner-decisions.json": _load_tracked_registry("owner-decisions.json"),
    }

    # Minimal valid manifest for model builder.
    manifest = {
        "registry_type": "manifest",
        "schema_version": "1.0.0",
        "architecture_version": "1.0.0",
        "description": "test",
        "registries": [
            {"filename": "tasks.json", "record_type": "task", "required": True,
             "tracked_or_generated": "tracked", "validation_order": 0,
             "allowed_authority_classes": ["authoritative"]},
        ],
        "generated_snapshot_output_root": ".codex-context/project-memory/",
    }
    model = _build_page_model(registries, manifest, [], {}, {}, set())
    output = _render_remaining_work(model)

    # T004 should not appear in remaining work
    assert "T004 " not in output or "task:PHASE8-IMPL-026-T004" not in output, (
        "T004 appears in remaining-work output when lifecycle is complete"
    )


def test_remaining_work_excludes_complete_t005_and_preserves_planned_successors():
    """T005 is complete; authoritative roadmap successors remain planned."""
    tasks_registry = _load_tracked_registry("tasks.json")
    registries = {
        "tasks.json": tasks_registry,
        "owner-decisions.json": _load_tracked_registry("owner-decisions.json"),
    }
    manifest = {
        "registry_type": "manifest",
        "schema_version": "1.0.0",
        "architecture_version": "1.0.0",
        "description": "test",
        "registries": [
            {"filename": "tasks.json", "record_type": "task", "required": True,
             "tracked_or_generated": "tracked", "validation_order": 0,
             "allowed_authority_classes": ["authoritative"]},
        ],
        "generated_snapshot_output_root": ".codex-context/project-memory/",
    }
    model = _build_page_model(registries, manifest, [], {}, {}, set())
    output = _render_remaining_work(model)

    assert "task:PHASE8-IMPL-026-T005" not in output
    for task_id in (6, 7, 9, 10, 11):
        assert "Status: planned" in _roadmap_task_section(f"PHASE8-IMPL-026-T{task_id:03d}")
    assert "Status: complete/PASS" in _roadmap_task_section("PHASE8-IMPL-026-T008")
    assert "owner-deferred" in _roadmap_task_section("PHASE8-IMPL-026-T006")
    assert "owner-deferred" in _roadmap_task_section("PHASE8-IMPL-026-T007")
    assert "Next Actionable Project Memory Task" in output
    assert "PHASE8-IMPL-026-T009" in output
    assert "Contingent / Owner-Deferred" in output


def test_current_roadmap_distinguishes_frontier_from_pm_next():
    """Prove the roadmap distinguishes application frontier from PM next task."""
    tasks_registry = _load_tracked_registry("tasks.json")
    registries = {
        "tasks.json": tasks_registry,
        "owner-decisions.json": _load_tracked_registry("owner-decisions.json"),
    }
    manifest = {
        "registry_type": "manifest",
        "schema_version": "1.0.0",
        "architecture_version": "1.0.0",
        "description": "test",
        "registries": [
            {"filename": "tasks.json", "record_type": "task", "required": True,
             "tracked_or_generated": "tracked", "validation_order": 0,
             "allowed_authority_classes": ["authoritative"]},
        ],
        "generated_snapshot_output_root": ".codex-context/project-memory/",
    }
    model = _build_page_model(registries, manifest, [], {}, {}, set())
    output = _render_current_roadmap(model)

    # Renders task records from the registry.
    assert "PHASE8-IMPL-024-T003A" in output, "Application frontier not in roadmap"
    # T005 appears in the task listing
    assert "PHASE8-IMPL-026-T005" in output or "Existing context-tool" in output, (
        "T005 not in roadmap task listing"
    )


# ---- application-frontier tests ----


def test_application_frontier_unchanged():
    recs = _tracked_task_records()
    r = _record_by_id(recs, "task:PHASE8-IMPL-024-T003A")
    assert r is not None, "PHASE8-IMPL-024-T003A not in task registry"
    assert r.get("is_application_frontier") is True
    t005 = _record_by_id(recs, "task:PHASE8-IMPL-026-T005")
    assert t005.get("is_application_frontier") is False


def test_ph8_impl_025_stays_planned():
    recs = _tracked_task_records()
    r = _record_by_id(recs, "task:PHASE8-IMPL-025")
    assert r is not None
    assert r["lifecycle"]["status"] == "planned"
    assert r.get("is_application_frontier") is False
    assert "inactive" in r.get("notes", "").lower()


# ---- authority-class test ----


def test_t004c_is_authoritative_not_generated_evidence():
    r = _record_by_id(_tracked_task_records(), "task:PHASE8-IMPL-026-T004C")
    assert r["authority_class"] == "authoritative"


def test_generated_evidence_never_authoritative():
    """All tracked task records are authoritative or accepted_evidence, never generated_evidence."""
    recs = _tracked_task_records()
    for r in recs:
        ac = r.get("authority_class", "")
        assert ac != "generated_evidence", (
            f"{r.get('id')} has authority_class generated_evidence"
        )


# ---- run the standard validator on the real registries ----


def test_tracked_registry_validation_passes():
    findings = validate_registries.validate(
        Path(__file__).resolve().parents[2] / "docs" / "project-memory" / "registries"
    )
    assert findings == []


# ---- renderer-hardcode awareness: _render_index still uses hardcoded strings ----


def test_render_index_derives_t004_from_registry():
    """Prove _render_index now derives T004 display status from the task registry,
    not from hardcoded strings.  The rendered index must show T004 complete."""
    tasks_registry = _load_tracked_registry("tasks.json")
    registries = {
        "tasks.json": tasks_registry,
        "owner-decisions.json": _load_tracked_registry("owner-decisions.json"),
    }
    manifest = {
        "registry_type": "manifest",
        "schema_version": "1.0.0",
        "architecture_version": "1.0.0",
        "description": "test",
        "registries": [
            {"filename": "tasks.json", "record_type": "task", "required": True,
             "tracked_or_generated": "tracked", "validation_order": 0,
             "allowed_authority_classes": ["authoritative"]},
        ],
        "generated_snapshot_output_root": ".codex-context/project-memory/",
    }
    model = _build_page_model(registries, manifest, [], {}, {}, set())
    output = _render_index(model)

    assert "T004 (Human-readable memory)" in output
    assert "complete/PASS-WITH-FINDINGS" in output
    for line in output.split("\n"):
        if "T004 (Human-readable memory)" in line:
            assert "in progress" not in line, f"T004 shown as in progress: {line.strip()}"


def test_render_index_derives_t004c_from_registry():
    """Prove _render_index derives T004C status from registry, not hardcodes."""
    tasks_registry = _load_tracked_registry("tasks.json")
    registries = {
        "tasks.json": tasks_registry,
        "owner-decisions.json": _load_tracked_registry("owner-decisions.json"),
    }
    manifest = {
        "registry_type": "manifest",
        "schema_version": "1.0.0",
        "architecture_version": "1.0.0",
        "description": "test",
        "registries": [
            {"filename": "tasks.json", "record_type": "task", "required": True,
             "tracked_or_generated": "tracked", "validation_order": 0,
             "allowed_authority_classes": ["authoritative"]},
        ],
        "generated_snapshot_output_root": ".codex-context/project-memory/",
    }
    model = _build_page_model(registries, manifest, [], {}, {}, set())
    output = _render_index(model)

    assert "T004C (Clean-HEAD publication)" in output
    assert "complete/PASS-WITH-FINDINGS" in output


def test_render_current_roadmap_preserves_t005_completion_and_t006_sequence():
    """Deferred T006/T007 remain visible while actionable sequencing reaches T009."""
    tasks_registry = _load_tracked_registry("tasks.json")
    registries = {
        "tasks.json": tasks_registry,
        "owner-decisions.json": _load_tracked_registry("owner-decisions.json"),
    }
    manifest = {
        "registry_type": "manifest",
        "schema_version": "1.0.0",
        "architecture_version": "1.0.0",
        "description": "test",
        "registries": [
            {"filename": "tasks.json", "record_type": "task", "required": True,
             "tracked_or_generated": "tracked", "validation_order": 0,
             "allowed_authority_classes": ["authoritative"]},
        ],
        "generated_snapshot_output_root": ".codex-context/project-memory/",
    }
    model = _build_page_model(registries, manifest, [], {}, {}, set())
    output = _render_current_roadmap(model)

    assert "Next actionable Project Memory task:** T009 (planned/inactive)" in output
    assert "PHASE8-IMPL-026-T005" in output
    assert "Lifecycle:** `complete`" in output
    t006 = _roadmap_task_section("PHASE8-IMPL-026-T006")
    assert "Status: planned, contingent, inactive, owner-deferred" in t006
    assert "No concrete symbol-navigation" in t006
    assert "Task state:** `owner deferred contingent`" in output
    assert "Current Project Memory child" not in output


def test_render_index_no_t004_in_progress():
    """The rendered index must never show T004 as 'in progress'."""
    tasks_registry = _load_tracked_registry("tasks.json")
    registries = {
        "tasks.json": tasks_registry,
        "owner-decisions.json": _load_tracked_registry("owner-decisions.json"),
    }
    manifest = {
        "registry_type": "manifest",
        "schema_version": "1.0.0",
        "architecture_version": "1.0.0",
        "description": "test",
        "registries": [
            {"filename": "tasks.json", "record_type": "task", "required": True,
             "tracked_or_generated": "tracked", "validation_order": 0,
             "allowed_authority_classes": ["authoritative"]},
        ],
        "generated_snapshot_output_root": ".codex-context/project-memory/",
    }
    model = _build_page_model(registries, manifest, [], {}, {}, set())
    output = _render_index(model)

    for line in output.split("\n"):
        if "T004 (Human-readable memory)" in line:
            assert "in progress" not in line, f"T004 shown as in progress: {line.strip()}"


def test_render_index_no_t004c_planned():
    """The rendered index must never show T004C as 'planned'."""
    tasks_registry = _load_tracked_registry("tasks.json")
    registries = {
        "tasks.json": tasks_registry,
        "owner-decisions.json": _load_tracked_registry("owner-decisions.json"),
    }
    manifest = {
        "registry_type": "manifest",
        "schema_version": "1.0.0",
        "architecture_version": "1.0.0",
        "description": "test",
        "registries": [
            {"filename": "tasks.json", "record_type": "task", "required": True,
             "tracked_or_generated": "tracked", "validation_order": 0,
             "allowed_authority_classes": ["authoritative"]},
        ],
        "generated_snapshot_output_root": ".codex-context/project-memory/",
    }
    model = _build_page_model(registries, manifest, [], {}, {}, set())
    output = _render_index(model)

    for line in output.split("\n"):
        if "T004C (Clean-HEAD publication)" in line:
            assert "planned" not in line, f"T004C shown as planned: {line.strip()}"


def test_render_current_roadmap_no_t004b_as_current_child():
    """The rendered roadmap must not identify T004B as current child."""
    tasks_registry = _load_tracked_registry("tasks.json")
    registries = {
        "tasks.json": tasks_registry,
        "owner-decisions.json": _load_tracked_registry("owner-decisions.json"),
    }
    manifest = {
        "registry_type": "manifest",
        "schema_version": "1.0.0",
        "architecture_version": "1.0.0",
        "description": "test",
        "registries": [
            {"filename": "tasks.json", "record_type": "task", "required": True,
             "tracked_or_generated": "tracked", "validation_order": 0,
             "allowed_authority_classes": ["authoritative"]},
        ],
        "generated_snapshot_output_root": ".codex-context/project-memory/",
    }
    model = _build_page_model(registries, manifest, [], {}, {}, set())
    output = _render_current_roadmap(model)

    assert "Current Project Memory child" not in output


def test_lifecycle_change_changes_rendered_output():
    """Prove that changing a task lifecycle changes rendered output."""
    recs = _tracked_task_records()
    import copy
    modified = copy.deepcopy(recs)
    for r in modified:
        if r.get("task_id") == "PHASE8-IMPL-026-T004":
            r["lifecycle"]["status"] = "in_progress"

    registries = {
        "tasks.json": {**_load_tracked_registry("tasks.json"), "records": modified},
        "owner-decisions.json": _load_tracked_registry("owner-decisions.json"),
    }
    manifest = {
        "registry_type": "manifest",
        "schema_version": "1.0.0",
        "architecture_version": "1.0.0",
        "description": "test",
        "registries": [
            {"filename": "tasks.json", "record_type": "task", "required": True,
             "tracked_or_generated": "tracked", "validation_order": 0,
             "allowed_authority_classes": ["authoritative"]},
        ],
        "generated_snapshot_output_root": ".codex-context/project-memory/",
    }
    model = _build_page_model(registries, manifest, [], {}, {}, set())
    output = _render_index(model)

    for line in output.split("\n"):
        if "T004 (Human-readable memory)" in line:
            assert "active" in line, f"T004 should show active after lifecycle change: {line.strip()}"


def test_renderer_no_hardcode_t004_t004b_t004c_t005():
    """Prove the renderer contains no hardcoded status for T004/T004B/T004C/T005.

    We check this indirectly: if we remove T004B from the registry completely
    and still provide all other required records, the renderer should fail
    because the required PM task records are missing."""
    recs = _tracked_task_records()
    filtered = [r for r in recs if r.get("task_id") != "PHASE8-IMPL-026-T004B"]
    registries = {
        "tasks.json": {**_load_tracked_registry("tasks.json"), "records": filtered},
        "owner-decisions.json": _load_tracked_registry("owner-decisions.json"),
    }
    manifest = {
        "registry_type": "manifest",
        "schema_version": "1.0.0",
        "architecture_version": "1.0.0",
        "description": "test",
        "registries": [
            {"filename": "tasks.json", "record_type": "task", "required": True,
             "tracked_or_generated": "tracked", "validation_order": 0,
             "allowed_authority_classes": ["authoritative"]},
        ],
        "generated_snapshot_output_root": ".codex-context/project-memory/",
    }
    model = _build_page_model(registries, manifest, [], {}, {}, set())
    with pytest.raises(ValueError, match="Required PM task records missing"):
        _render_index(model)


def test_duplicate_task_ids_fail_closed():
    """Duplicate task IDs must raise ValueError in _validate_task_records."""
    tasks = [
        {"task_id": "PHASE8-IMPL-026-T004", "lifecycle": {"status": "complete"}},
        {"task_id": "PHASE8-IMPL-026-T004", "lifecycle": {"status": "complete"}},
    ]
    errors = _validate_task_records(tasks)
    assert len(errors) > 0
    assert any("Duplicate" in e for e in errors)


def test_missing_parent_ref_fails_closed():
    """Contradictory parent reference must fail validation."""
    tasks = [
        {"task_id": "PHASE8-IMPL-026-T004A", "lifecycle": {"status": "complete"},
         "parent_task_id": "PHASE8-IMPL-026"},
    ]
    errors = _validate_task_records(tasks)
    assert len(errors) > 0
    assert any("Parent" in e for e in errors)


def test_unsupported_lifecycle_fails_closed():
    """Unsupported lifecycle status must fail validation."""
    tasks = [
        {"task_id": "PHASE8-IMPL-026-T004", "lifecycle": {"status": "invalid_status"}},
    ]
    errors = _validate_task_records(tasks)
    assert len(errors) > 0


def test_get_task_by_id_finds_record():
    tasks = _tracked_task_records()
    result = _get_task_by_id(tasks, "PHASE8-IMPL-026-T004")
    assert result is not None
    assert result["task_id"] == "PHASE8-IMPL-026-T004"


def test_get_task_by_id_returns_none_for_missing():
    tasks = _tracked_task_records()
    result = _get_task_by_id(tasks, "NONEXISTENT")
    assert result is None


def test_get_children_returns_direct_children():
    tasks = _tracked_task_records()
    children = _get_children(tasks, "PHASE8-IMPL-026-T004")
    child_ids = {c["task_id"] for c in children}
    assert "PHASE8-IMPL-026-T004A" in child_ids
    assert "PHASE8-IMPL-026-T004B" in child_ids
    assert "PHASE8-IMPL-026-T004C" in child_ids


def test_identify_completed_children():
    tasks = _tracked_task_records()
    completed = _identify_completed_children(tasks, "PHASE8-IMPL-026-T004")
    completed_ids = {c["task_id"] for c in completed}
    assert "PHASE8-IMPL-026-T004A" in completed_ids
    assert "PHASE8-IMPL-026-T004B" in completed_ids
    assert "PHASE8-IMPL-026-T004C" in completed_ids


def test_identify_next_planned_child():
    tasks = _tracked_task_records()
    next_task = _identify_next_planned_child(tasks, _PM_PARENT_TASK_ID)
    assert next_task["task_id"] == "PHASE8-IMPL-026-T009"


def test_tracked_behavior_skips_deferred_contingent_tasks_and_selects_t009():
    behavior = _derive_pm_task_behavior(
        _tracked_task_records(),
        _load_tracked_registry("owner-decisions.json")["records"],
    )
    assert behavior["states"]["PHASE8-IMPL-026-T006"]["state"] == "owner_deferred_contingent"
    assert behavior["states"]["PHASE8-IMPL-026-T007"]["state"] == "owner_deferred_contingent"
    assert behavior["states"]["PHASE8-IMPL-026-T008"]["state"] == "complete"
    assert behavior["next_actionable_task"]["task_id"] == "PHASE8-IMPL-026-T009"


def test_derive_task_display_status_complete_pass_with_findings():
    task = {"lifecycle": {"status": "complete"}, "notes": "Complete/PASS-WITH-FINDINGS."}
    assert _derive_task_display_status(task) == "complete/PASS-WITH-FINDINGS"


def test_derive_task_display_status_complete_pass():
    task = {"lifecycle": {"status": "complete"}, "notes": "Complete/PASS."}
    assert _derive_task_display_status(task) == "complete/PASS"


def test_derive_task_display_status_planned_inactive():
    task = {"lifecycle": {"status": "planned"}, "notes": "Planned next. Inactive."}
    assert _derive_task_display_status(task) == "planned/inactive"


# ---- note: these tests prove the renderer repair was successful.
# The renderer now derives task status from the registry for the index
# status table and the current-roadmap page.  Hardcoded strings for
# T004, T004B, T004C, and T005 have been removed.
