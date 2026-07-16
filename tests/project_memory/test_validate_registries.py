"""Tests for the Project Memory registry validator.

Tests use temporary fixtures and must not mutate committed registry files.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.project_memory import validate_registries  # type: ignore


def _write_registry(tmp_dir: Path, filename: str, data: dict) -> Path:
    path = tmp_dir / filename
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return path


def _build_manifest(registries: list[dict]) -> dict:
    return {
        "registry_type": "manifest",
        "schema_version": "1.0.0",
        "architecture_version": "1.0.0",
        "description": "Test manifest.",
        "registries": registries,
        "generated_snapshot_output_root": ".codex-context/project-memory/",
    }


def _build_registry(registry_type: str, records: list[dict]) -> dict:
    return {
        "registry_type": registry_type,
        "schema_version": "1.0.0",
        "records": records,
    }


def _build_record(
    rid: str,
    rtype: str,
    title: str = "Test Record",
    authority_class: str = "authoritative",
    status: str = "current",
    **extra,
) -> dict:
    rec: dict[str, object] = {
        "id": rid,
        "type": rtype,
        "schema_version": "1.0.0",
        "title": title,
        "authority_class": authority_class,
        "lifecycle": {
            "status": status,
        },
    }
    rec.update(extra)
    return rec


def _build_task_record(
    rid: str,
    task_id: str,
    title: str = "Test Task",
    status: str = "planned",
    **extra,
) -> dict:
    return _build_record(
        rid, "task", title=title, status=status,
        task_id=task_id, **extra,
    )


_FULL_MANIFEST_DECLS = [
    {"filename": "projects.json", "record_type": "project", "required": True, "tracked_or_generated": "tracked", "validation_order": 0},
    {"filename": "features.json", "record_type": "feature", "required": True, "tracked_or_generated": "tracked", "validation_order": 1},
    {"filename": "boundaries.json", "record_type": "boundary", "required": True, "tracked_or_generated": "tracked", "validation_order": 2},
    {"filename": "tasks.json", "record_type": "task", "required": True, "tracked_or_generated": "tracked", "validation_order": 3},
    {"filename": "decisions.json", "record_type": "decision", "required": True, "tracked_or_generated": "tracked", "validation_order": 4},
    {"filename": "capabilities.json", "record_type": "capability", "required": True, "tracked_or_generated": "tracked", "validation_order": 5},
    {"filename": "assets.json", "record_type": "asset", "required": True, "tracked_or_generated": "tracked", "validation_order": 6},
    {"filename": "evidence.json", "record_type": "evidence", "required": True, "tracked_or_generated": "tracked", "validation_order": 7},
    {"filename": "dependencies.json", "record_type": "dependency", "required": True, "tracked_or_generated": "tracked", "validation_order": 8},
    {"filename": "tools.json", "record_type": "tool", "required": True, "tracked_or_generated": "tracked", "validation_order": 9},
    {"filename": "owner-decisions.json", "record_type": "owner_decision", "required": True, "tracked_or_generated": "tracked", "validation_order": 10},
]


def _has_error(findings: list[dict], code: str, fragment: str = "") -> bool:
    for f in findings:
        if f.get("code") == code:
            if fragment:
                if fragment in f.get("message", ""):
                    return True
            else:
                return True
    return False


# --- Test: committed seed registries pass ---

def test_seed_registries_pass():
    findings = validate_registries.validate()
    errors = [f for f in findings if f["level"] == "error"]
    assert not errors, f"seed registries have errors: {errors}"


# --- Test: duplicate global ID fails ---

def test_duplicate_id_fails(tmp_path: Path, monkeypatch):
    registries_dir = tmp_path / "registries"
    registries_dir.mkdir()
    monkeypatch.setattr(validate_registries, "REGISTRIES_DIR", registries_dir)
    monkeypatch.setattr(validate_registries, "MANIFEST_PATH", registries_dir / "manifest.json")

    manifest = _build_manifest([
        {"filename": "projects.json", "record_type": "project", "required": True, "tracked_or_generated": "tracked", "validation_order": 0},
    ])
    _write_registry(registries_dir, "manifest.json", manifest)

    reg = _build_registry("project", [
        _build_record("project:one", "project", title="Project One"),
        _build_record("project:one", "project", title="Project One Duplicate"),
    ])
    _write_registry(registries_dir, "projects.json", reg)

    findings = validate_registries.validate(registries_dir)
    assert _has_error(findings, "DUPLICATE_ID"), "duplicate id should fail"


# --- Test: unknown trust class fails ---

def test_unknown_trust_class_fails(tmp_path: Path, monkeypatch):
    registries_dir = tmp_path / "registries"
    registries_dir.mkdir()
    monkeypatch.setattr(validate_registries, "REGISTRIES_DIR", registries_dir)
    monkeypatch.setattr(validate_registries, "MANIFEST_PATH", registries_dir / "manifest.json")

    manifest = _build_manifest([
        {"filename": "projects.json", "record_type": "project", "required": True, "tracked_or_generated": "tracked", "validation_order": 0},
    ])
    _write_registry(registries_dir, "manifest.json", manifest)

    reg = _build_registry("project", [
        _build_record("project:one", "project", authority_class="made_up_class"),
    ])
    _write_registry(registries_dir, "projects.json", reg)

    findings = validate_registries.validate(registries_dir)
    assert _has_error(findings, "INVALID_TRUST_CLASS"), "unknown trust class should fail"


# --- Test: unknown cross-record reference fails ---

def test_unknown_cross_reference_fails(tmp_path: Path, monkeypatch):
    registries_dir = tmp_path / "registries"
    registries_dir.mkdir()
    monkeypatch.setattr(validate_registries, "REGISTRIES_DIR", registries_dir)
    monkeypatch.setattr(validate_registries, "MANIFEST_PATH", registries_dir / "manifest.json")

    manifest = _build_manifest([
        {"filename": "tasks.json", "record_type": "task", "required": True, "tracked_or_generated": "tracked", "validation_order": 0},
    ])
    _write_registry(registries_dir, "manifest.json", manifest)

    reg = _build_registry("task", [
        _build_task_record("task:PHASE8-IMPL-026-T001", "PHASE8-IMPL-026-T001"),
        _build_task_record(
            "task:PHASE8-IMPL-026-T002", "PHASE8-IMPL-026-T002",
            depends_on=["PHASE8-IMPL-026-NONEXISTENT"],
        ),
    ])
    _write_registry(registries_dir, "tasks.json", reg)

    findings = validate_registries.validate(registries_dir)
    assert _has_error(findings, "UNKNOWN_TASK_DEPENDENCY"), "unknown cross-reference should fail"


# --- Test: path traversal fails ---

def test_path_traversal_in_source_locator_fails(tmp_path: Path, monkeypatch):
    registries_dir = tmp_path / "registries"
    registries_dir.mkdir()
    monkeypatch.setattr(validate_registries, "REGISTRIES_DIR", registries_dir)
    monkeypatch.setattr(validate_registries, "MANIFEST_PATH", registries_dir / "manifest.json")

    manifest = _build_manifest([
        {"filename": "projects.json", "record_type": "project", "required": True, "tracked_or_generated": "tracked", "validation_order": 0},
    ])
    _write_registry(registries_dir, "manifest.json", manifest)

    reg = _build_registry("project", [
        _build_record("project:one", "project",
                      provenance={"source_locators": [{"path": "../outside/file.txt"}]}),
    ])
    _write_registry(registries_dir, "projects.json", reg)

    findings = validate_registries.validate(registries_dir)
    assert _has_error(findings, "INVALID_SOURCE_LOCATOR"), "path traversal should fail"


# --- Test: absolute source path fails ---

def test_absolute_source_path_fails(tmp_path: Path, monkeypatch):
    registries_dir = tmp_path / "registries"
    registries_dir.mkdir()
    monkeypatch.setattr(validate_registries, "REGISTRIES_DIR", registries_dir)
    monkeypatch.setattr(validate_registries, "MANIFEST_PATH", registries_dir / "manifest.json")

    manifest = _build_manifest([
        {"filename": "projects.json", "record_type": "project", "required": True, "tracked_or_generated": "tracked", "validation_order": 0},
    ])
    _write_registry(registries_dir, "manifest.json", manifest)

    reg = _build_registry("project", [
        _build_record("project:one", "project",
                      provenance={"source_locators": [{"path": "/etc/passwd"}]}),
    ])
    _write_registry(registries_dir, "projects.json", reg)

    findings = validate_registries.validate(registries_dir)
    assert _has_error(findings, "INVALID_SOURCE_LOCATOR"), "absolute path should fail"


# --- Test: malformed Git SHA fails ---

def test_malformed_git_sha_fails(tmp_path: Path, monkeypatch):
    registries_dir = tmp_path / "registries"
    registries_dir.mkdir()
    monkeypatch.setattr(validate_registries, "REGISTRIES_DIR", registries_dir)
    monkeypatch.setattr(validate_registries, "MANIFEST_PATH", registries_dir / "manifest.json")

    manifest = _build_manifest([
        {"filename": "evidence.json", "record_type": "evidence", "required": True, "tracked_or_generated": "tracked", "validation_order": 0},
    ])
    _write_registry(registries_dir, "manifest.json", manifest)

    reg = _build_registry("evidence", [
        _build_record("evidence:one", "evidence",
                      evidence_id="ev1", evidence_type="commit_record",
                      bound_commit="not-a-sha"),
    ])
    _write_registry(registries_dir, "evidence.json", reg)

    findings = validate_registries.validate(registries_dir)
    assert _has_error(findings, "INVALID_GIT_SHA"), "malformed git sha should fail"


# --- Test: invalid timestamp fails ---

def test_invalid_timestamp_fails(tmp_path: Path, monkeypatch):
    registries_dir = tmp_path / "registries"
    registries_dir.mkdir()
    monkeypatch.setattr(validate_registries, "REGISTRIES_DIR", registries_dir)
    monkeypatch.setattr(validate_registries, "MANIFEST_PATH", registries_dir / "manifest.json")

    manifest = _build_manifest([
        {"filename": "projects.json", "record_type": "project", "required": True, "tracked_or_generated": "tracked", "validation_order": 0},
    ])
    _write_registry(registries_dir, "manifest.json", manifest)

    reg = _build_registry("project", [
        _build_record("project:one", "project",
                      lifecycle={"status": "current", "effective_from": "not-a-timestamp"}),
    ])
    _write_registry(registries_dir, "projects.json", reg)

    findings = validate_registries.validate(registries_dir)
    assert _has_error(findings, "INVALID_TIMESTAMP"), "invalid timestamp should fail"


# --- Test: wrong record type in registry fails ---

def test_wrong_record_type_in_registry_fails(tmp_path: Path, monkeypatch):
    registries_dir = tmp_path / "registries"
    registries_dir.mkdir()
    monkeypatch.setattr(validate_registries, "REGISTRIES_DIR", registries_dir)
    monkeypatch.setattr(validate_registries, "MANIFEST_PATH", registries_dir / "manifest.json")

    manifest = _build_manifest([
        {"filename": "projects.json", "record_type": "project", "required": True, "tracked_or_generated": "tracked", "validation_order": 0},
    ])
    _write_registry(registries_dir, "manifest.json", manifest)

    reg = _build_registry("project", [
        _build_record("task:PHASE8-IMPL-026", "task"),
    ])
    _write_registry(registries_dir, "projects.json", reg)

    findings = validate_registries.validate(registries_dir)
    assert _has_error(findings, "RECORD_TYPE_MISMATCH"), "wrong record type should fail"


# --- Test: missing required registry fails ---

def test_missing_required_registry_fails(tmp_path: Path, monkeypatch):
    registries_dir = tmp_path / "registries"
    registries_dir.mkdir()
    monkeypatch.setattr(validate_registries, "REGISTRIES_DIR", registries_dir)
    monkeypatch.setattr(validate_registries, "MANIFEST_PATH", registries_dir / "manifest.json")

    manifest = _build_manifest([
        {"filename": "projects.json", "record_type": "project", "required": True, "tracked_or_generated": "tracked", "validation_order": 0},
    ])
    _write_registry(registries_dir, "manifest.json", manifest)
    # do NOT write projects.json

    findings = validate_registries.validate(registries_dir)
    assert _has_error(findings, "MISSING_REGISTRY_FILE"), "missing required registry should fail"


# --- Test: undeclared registry file fails ---

def test_undeclared_registry_file_fails(tmp_path: Path, monkeypatch):
    registries_dir = tmp_path / "registries"
    registries_dir.mkdir()
    monkeypatch.setattr(validate_registries, "REGISTRIES_DIR", registries_dir)
    monkeypatch.setattr(validate_registries, "MANIFEST_PATH", registries_dir / "manifest.json")

    manifest = _build_manifest([
        {"filename": "projects.json", "record_type": "project", "required": True, "tracked_or_generated": "tracked", "validation_order": 0},
    ])
    _write_registry(registries_dir, "manifest.json", manifest)
    _write_registry(registries_dir, "projects.json", _build_registry("project", []))
    # Write an undeclared file
    _write_registry(registries_dir, "extra.json", {"registry_type": "extra", "schema_version": "1.0.0", "records": []})

    findings = validate_registries.validate(registries_dir)
    assert _has_error(findings, "UNDECLARED_REGISTRY_FILE"), "undeclared registry should fail"


# --- Test: direct task dependency cycle fails ---

def test_direct_task_dependency_cycle_fails(tmp_path: Path, monkeypatch):
    registries_dir = tmp_path / "registries"
    registries_dir.mkdir()
    monkeypatch.setattr(validate_registries, "REGISTRIES_DIR", registries_dir)
    monkeypatch.setattr(validate_registries, "MANIFEST_PATH", registries_dir / "manifest.json")

    manifest = _build_manifest([
        {"filename": "tasks.json", "record_type": "task", "required": True, "tracked_or_generated": "tracked", "validation_order": 0},
    ])
    _write_registry(registries_dir, "manifest.json", manifest)

    reg = _build_registry("task", [
        _build_task_record("task:PHASE8-IMPL-026-T002", "PHASE8-IMPL-026-T002",
                           depends_on=["PHASE8-IMPL-026-T003"]),
        _build_task_record("task:PHASE8-IMPL-026-T003", "PHASE8-IMPL-026-T003",
                           depends_on=["PHASE8-IMPL-026-T002"]),
    ])
    _write_registry(registries_dir, "tasks.json", reg)

    findings = validate_registries.validate(registries_dir)
    assert _has_error(findings, "TASK_DEPENDENCY_CYCLE"), "dependency cycle should fail"


# --- Test: invalid supersession state fails ---

def test_superseded_without_superseded_by_fails(tmp_path: Path, monkeypatch):
    registries_dir = tmp_path / "registries"
    registries_dir.mkdir()
    monkeypatch.setattr(validate_registries, "REGISTRIES_DIR", registries_dir)
    monkeypatch.setattr(validate_registries, "MANIFEST_PATH", registries_dir / "manifest.json")

    manifest = _build_manifest([
        {"filename": "decisions.json", "record_type": "decision", "required": True, "tracked_or_generated": "tracked", "validation_order": 0},
    ])
    _write_registry(registries_dir, "manifest.json", manifest)

    reg = _build_registry("decision", [
        _build_record("decision:sup-decision", "decision",
                      decision_id="sup-decision", decision_path="path.md",
                      authority_class="superseded",
                      lifecycle={"status": "superseded"}),
    ])
    _write_registry(registries_dir, "decisions.json", reg)

    findings = validate_registries.validate(registries_dir)
    assert _has_error(findings, "SUPERSEDED_WITHOUT_SUPERSEDED_BY")


# --- Test: current with superseded_by fails ---

def test_current_with_superseded_by_fails(tmp_path: Path, monkeypatch):
    registries_dir = tmp_path / "registries"
    registries_dir.mkdir()
    monkeypatch.setattr(validate_registries, "REGISTRIES_DIR", registries_dir)
    monkeypatch.setattr(validate_registries, "MANIFEST_PATH", registries_dir / "manifest.json")

    manifest = _build_manifest([
        {"filename": "decisions.json", "record_type": "decision", "required": True, "tracked_or_generated": "tracked", "validation_order": 0},
    ])
    _write_registry(registries_dir, "manifest.json", manifest)

    reg = _build_registry("decision", [
        _build_record("decision:broken", "decision",
                      decision_id="broken", decision_path="path.md",
                      authority_class="authoritative",
                      lifecycle={"status": "current", "superseded_by": "decision:other"}),
    ])
    _write_registry(registries_dir, "decisions.json", reg)

    findings = validate_registries.validate(registries_dir)
    assert _has_error(findings, "CURRENT_WITH_SUPERSEDED_BY")


# --- Test: generated/untrusted not eligible for authority ---

def test_untrusted_record_not_eligible_for_authority(tmp_path: Path, monkeypatch):
    registries_dir = tmp_path / "registries"
    registries_dir.mkdir()
    monkeypatch.setattr(validate_registries, "REGISTRIES_DIR", registries_dir)
    monkeypatch.setattr(validate_registries, "MANIFEST_PATH", registries_dir / "manifest.json")

    manifest = _build_manifest([
        {"filename": "projects.json", "record_type": "project", "required": True, "tracked_or_generated": "tracked", "validation_order": 0},
    ])
    _write_registry(registries_dir, "manifest.json", manifest)

    reg = _build_registry("project", [
        _build_record("project:one", "project", authority_class="untrusted"),
    ])
    _write_registry(registries_dir, "projects.json", reg)

    findings = validate_registries.validate(registries_dir)
    assert _has_error(findings, "UNAUTHORITATIVE_RECORD"), "untrusted project should fail"


def test_generated_evidence_project_should_fail(tmp_path: Path, monkeypatch):
    registries_dir = tmp_path / "registries"
    registries_dir.mkdir()
    monkeypatch.setattr(validate_registries, "REGISTRIES_DIR", registries_dir)
    monkeypatch.setattr(validate_registries, "MANIFEST_PATH", registries_dir / "manifest.json")

    manifest = _build_manifest([
        {"filename": "projects.json", "record_type": "project", "required": True, "tracked_or_generated": "tracked", "validation_order": 0},
    ])
    _write_registry(registries_dir, "manifest.json", manifest)

    reg = _build_registry("project", [
        _build_record("project:one", "project", authority_class="generated_evidence"),
    ])
    _write_registry(registries_dir, "projects.json", reg)

    findings = validate_registries.validate(registries_dir)
    assert _has_error(findings, "UNAUTHORITATIVE_RECORD"), "generated_evidence project should fail"


# --- Test: deterministic finding ordering ---

def test_deterministic_finding_order(tmp_path: Path, monkeypatch):
    registries_dir = tmp_path / "registries"
    registries_dir.mkdir()
    monkeypatch.setattr(validate_registries, "REGISTRIES_DIR", registries_dir)
    monkeypatch.setattr(validate_registries, "MANIFEST_PATH", registries_dir / "manifest.json")

    manifest = _build_manifest([
        {"filename": "projects.json", "record_type": "project", "required": True, "tracked_or_generated": "tracked", "validation_order": 0},
    ])
    _write_registry(registries_dir, "manifest.json", manifest)

    reg = _build_registry("project", [
        _build_record("project:one", "project", authority_class="untrusted"),
        _build_record("project:one", "project", authority_class="untrusted"),
    ])
    _write_registry(registries_dir, "projects.json", reg)

    run1 = validate_registries.validate(registries_dir)
    run2 = validate_registries.validate(registries_dir)
    assert run1 == run2, "validator must produce deterministic output"


# --- Test: --json output shape ---

def test_json_output_shape(tmp_path: Path, monkeypatch):
    registries_dir = tmp_path / "registries"
    registries_dir.mkdir()
    monkeypatch.setattr(validate_registries, "REGISTRIES_DIR", registries_dir)
    monkeypatch.setattr(validate_registries, "MANIFEST_PATH", registries_dir / "manifest.json")

    manifest = _build_manifest([
        {"filename": "projects.json", "record_type": "project", "required": True, "tracked_or_generated": "tracked", "validation_order": 0},
    ])
    _write_registry(registries_dir, "manifest.json", manifest)

    reg = _build_registry("project", [
        _build_record("project:one", "project"),
    ])
    _write_registry(registries_dir, "projects.json", reg)

    findings = validate_registries.validate(registries_dir)
    errors = [f for f in findings if f["level"] == "error"]
    assert not errors

    # Verify findings have the expected shape
    for f in findings:
        assert "level" in f
        assert "code" in f
        assert "message" in f
        assert f["level"] in ("error", "warning")


# --- Test: validator does not modify registry files ---

def test_validator_does_not_modify_registry_files(tmp_path: Path, monkeypatch):
    registries_dir = tmp_path / "registries"
    registries_dir.mkdir()
    monkeypatch.setattr(validate_registries, "REGISTRIES_DIR", registries_dir)
    monkeypatch.setattr(validate_registries, "MANIFEST_PATH", registries_dir / "manifest.json")

    manifest = _build_manifest([
        {"filename": "projects.json", "record_type": "project", "required": True, "tracked_or_generated": "tracked", "validation_order": 0},
    ])
    _write_registry(registries_dir, "manifest.json", manifest)

    reg = _build_registry("project", [
        _build_record("project:one", "project"),
    ])
    proj_path = _write_registry(registries_dir, "projects.json", reg)

    mtime_before = os.path.getmtime(str(proj_path))
    validate_registries.validate(registries_dir)
    mtime_after = os.path.getmtime(str(proj_path))
    assert mtime_before == mtime_after, "validator must not modify registry files"


# --- Test: disallowed trust class in registry fails ---

def test_disallowed_trust_class_in_registry_fails(tmp_path: Path, monkeypatch):
    registries_dir = tmp_path / "registries"
    registries_dir.mkdir()
    monkeypatch.setattr(validate_registries, "REGISTRIES_DIR", registries_dir)
    monkeypatch.setattr(validate_registries, "MANIFEST_PATH", registries_dir / "manifest.json")

    manifest = _build_manifest([
        {"filename": "boundaries.json", "record_type": "boundary", "required": True,
         "tracked_or_generated": "tracked", "validation_order": 0,
         "allowed_authority_classes": ["authoritative"]},
    ])
    _write_registry(registries_dir, "manifest.json", manifest)

    reg = _build_registry("boundary", [
        _build_record("boundary:one", "boundary", boundary_id="b1", category="product_safety",
                      is_non_negotiable=True, authority_class="generated_evidence"),
    ])
    _write_registry(registries_dir, "boundaries.json", reg)

    findings = validate_registries.validate(registries_dir)
    assert _has_error(findings, "DISALLOWED_TRUST_CLASS"), "disallowed trust class should fail"


# --- Test: supersession asymmetry detection ---

def test_supersession_asymmetry_fails(tmp_path: Path, monkeypatch):
    registries_dir = tmp_path / "registries"
    registries_dir.mkdir()
    monkeypatch.setattr(validate_registries, "REGISTRIES_DIR", registries_dir)
    monkeypatch.setattr(validate_registries, "MANIFEST_PATH", registries_dir / "manifest.json")

    manifest = _build_manifest([
        {"filename": "decisions.json", "record_type": "decision", "required": True, "tracked_or_generated": "tracked", "validation_order": 0},
    ])
    _write_registry(registries_dir, "manifest.json", manifest)

    reg = _build_registry("decision", [
        _build_record("decision:old", "decision",
                      decision_id="old", decision_path="old.md",
                      authority_class="superseded",
                      lifecycle={"status": "superseded", "superseded_by": "decision:new"}),
        _build_record("decision:new", "decision",
                      decision_id="new", decision_path="new.md",
                      authority_class="authoritative",
                      lifecycle={"status": "current"}),  # no supersedes
    ])
    _write_registry(registries_dir, "decisions.json", reg)

    findings = validate_registries.validate(registries_dir)
    assert _has_error(findings, "SUPERSESSION_ASYMMETRY"), "supersession asymmetry should fail"


def _write_remaining_mvp_fixture(
    tmp_path: Path,
    *,
    child_authority: str = "authoritative",
    include_child: bool = True,
) -> tuple[Path, Path]:
    registries_dir = tmp_path / "registries"
    registries_dir.mkdir()
    manifest = _build_manifest([
        {"filename": "tasks.json", "record_type": "task", "required": True,
         "tracked_or_generated": "tracked", "validation_order": 0},
        {"filename": "dependencies.json", "record_type": "dependency", "required": True,
         "tracked_or_generated": "tracked", "validation_order": 1},
    ])
    _write_registry(registries_dir, "manifest.json", manifest)
    task_records = [
        _build_task_record(
            "task:MVP-PARENT", "MVP-PARENT", status="planned",
            parent_task_id=None, depends_on=[],
        )
    ]
    if include_child:
        task_records.append(_build_task_record(
            "task:MVP-CHILD", "MVP-CHILD", status="planned",
            authority_class=child_authority,
            parent_task_id="MVP-PARENT", depends_on=["MVP-PARENT"],
        ))
    _write_registry(registries_dir, "tasks.json", _build_registry("task", task_records))
    dependency_records = []
    if include_child:
        dependency_records.append(_build_record(
            "dependency:mvp-child-on-parent", "dependency",
            dependency_id="mvp-child-on-parent",
            source_id="task:MVP-CHILD", target_id="task:MVP-PARENT",
            dependency_type="task_depends_on", is_separate=False,
        ))
    _write_registry(
        registries_dir, "dependencies.json",
        _build_registry("dependency", dependency_records),
    )
    roadmap_path = tmp_path / "roadmap_index.yaml"
    roadmap_path.write_text(json.dumps({
        "active_frontier": {"remaining_mvp_parent_task_ids": ["MVP-PARENT"]},
        "tasks": [
            {"id": "MVP-PARENT", "status": "planned", "parent": None, "depends_on": []},
            {"id": "MVP-CHILD", "status": "planned", "parent": "MVP-PARENT", "depends_on": ["MVP-PARENT"]},
        ],
    }), encoding="utf-8")
    return registries_dir, roadmap_path


def test_remaining_mvp_roadmap_and_registry_fixture_pass(tmp_path: Path):
    registries_dir, roadmap_path = _write_remaining_mvp_fixture(tmp_path)
    findings = validate_registries.validate(registries_dir, roadmap_path)
    assert not [f for f in findings if f["level"] == "error"], findings


def test_remaining_mvp_task_omission_fails(tmp_path: Path):
    registries_dir, roadmap_path = _write_remaining_mvp_fixture(
        tmp_path, include_child=False,
    )
    findings = validate_registries.validate(registries_dir, roadmap_path)
    assert _has_error(findings, "MISSING_NORMALIZED_MVP_TASK", "MVP-CHILD")


def test_generated_evidence_cannot_satisfy_remaining_mvp_task(tmp_path: Path):
    registries_dir, roadmap_path = _write_remaining_mvp_fixture(
        tmp_path, child_authority="generated_evidence",
    )
    findings = validate_registries.validate(registries_dir, roadmap_path)
    assert _has_error(findings, "MISSING_NORMALIZED_MVP_TASK", "MVP-CHILD")
    assert _has_error(findings, "UNAUTHORITATIVE_RECORD")


def test_duplicate_task_identity_fails(tmp_path: Path):
    registries_dir, _ = _write_remaining_mvp_fixture(tmp_path)
    tasks_path = registries_dir / "tasks.json"
    tasks = json.loads(tasks_path.read_text(encoding="utf-8"))
    duplicate = dict(tasks["records"][1])
    duplicate["id"] = "task:MVP-CHILD-DUPLICATE"
    tasks["records"].append(duplicate)
    tasks_path.write_text(json.dumps(tasks), encoding="utf-8")
    findings = validate_registries.validate(registries_dir)
    assert _has_error(findings, "DUPLICATE_TASK_IDENTITY", "MVP-CHILD")
