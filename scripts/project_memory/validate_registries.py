#!/usr/bin/env python3
"""Project Memory registry validator.

Discover and validate all tracked normalized registry files through the
registry manifest. Uses only Python standard-library modules.

Usage:
  python3 scripts/project_memory/validate_registries.py
  python3 scripts/project_memory/validate_registries.py --json
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REGISTRIES_DIR = ROOT / "docs" / "project-memory" / "registries"
SCHEMA_PATH = ROOT / "docs" / "project-memory" / "schemas" / "project-memory.schema.json"
MANIFEST_PATH = REGISTRIES_DIR / "manifest.json"
ROADMAP_INDEX_PATH = ROOT / "docs" / "roadmap" / "roadmap_index.yaml"

TRUST_CLASSES = frozenset([
    "authoritative",
    "accepted_evidence",
    "generated_evidence",
    "historical",
    "superseded",
    "uncertain",
    "owner_pending",
    "untrusted",
])

LIFECYCLE_STATUSES = frozenset([
    "current",
    "planned",
    "in_progress",
    "complete",
    "blocked",
    "deferred",
    "historical",
    "superseded",
    "rejected",
    "owner_pending",
])

_AUTHORITATIVE_ELIGIBLE = frozenset(["authoritative", "accepted_evidence"])

_GIT_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_ISO8601_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$"
)
_STABLE_ID_RE = re.compile(
    r"^(project|feature|boundary|task|decision|capability|asset|evidence|dependency|tool|owner-decision):"
    r"[a-zA-Z0-9][a-zA-Z0-9._-]*$"
)

_VALID_RECORD_TYPES = frozenset([
    "project", "feature", "boundary", "task", "decision",
    "capability", "asset", "evidence", "dependency", "tool", "owner_decision",
])

_SOURCE_LOCATOR_VALID_KEYS = frozenset([
    "path", "line_start", "line_end", "json_pointer",
    "symbol", "task_id", "decision_id", "evidence_artifact_id",
])


def _finding(
    level: str,
    code: str,
    message: str,
    registry_file: str = "",
    record_id: str = "",
    detail: str = "",
) -> dict[str, str]:
    return {
        "level": level,
        "code": code,
        "message": message,
        "registry_file": registry_file,
        "record_id": record_id,
        "detail": detail,
    }


def _parse_json(path: Path) -> Any:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _is_repo_relative_path(value: str) -> bool:
    if not value:
        return False
    if os.path.isabs(value):
        return False
    if value.startswith("/") or value.startswith("\\"):
        return False
    parts = value.replace("\\", "/").split("/")
    if ".." in parts:
        return False
    return True


def _validate_source_locator(locator: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(locator, dict):
        errors.append("source locator must be a dict")
        return errors
    if "path" not in locator:
        errors.append("source locator missing 'path'")
        return errors
    path_val = locator.get("path")
    if not isinstance(path_val, str) or not path_val.strip():
        errors.append(f"source locator path must be a non-empty string: {path_val!r}")
    elif not _is_repo_relative_path(path_val):
        errors.append(
            f"source locator path must be repository-relative (no absolute, no ..): {path_val!r}"
        )
    for key in locator:
        if key not in _SOURCE_LOCATOR_VALID_KEYS:
            errors.append(f"unknown source locator key: {key!r}")
    line_start = locator.get("line_start")
    if line_start is not None:
        if not isinstance(line_start, int) or line_start < 1:
            errors.append(f"line_start must be positive integer: {line_start!r}")
    line_end = locator.get("line_end")
    if line_end is not None:
        if not isinstance(line_end, int) or line_end < 1:
            errors.append(f"line_end must be positive integer: {line_end!r}")
    if line_start is not None and line_end is not None and line_start > line_end:
        errors.append(f"line_start ({line_start}) > line_end ({line_end})")
    json_pointer = locator.get("json_pointer")
    if json_pointer is not None:
        if not isinstance(json_pointer, str):
            errors.append("json_pointer must be a string")
        elif json_pointer != "" and not json_pointer.startswith("/"):
            errors.append(f"json_pointer must be empty or start with /: {json_pointer!r}")
    return errors


def _record_label(rec: dict[str, Any]) -> str:
    rid = rec.get("id", "?")
    rtype = rec.get("type", "?")
    return f"{rtype}:{rid}"


def validate(
    registries_dir: Path | None = None,
    roadmap_index_path: Path | None = None,
) -> list[dict[str, str]]:
    """Validate all registries. Returns list of findings (empty = PASS)."""
    use_tracked_registries = registries_dir is None
    if registries_dir is None:
        registries_dir = REGISTRIES_DIR
    if roadmap_index_path is None and use_tracked_registries:
        roadmap_index_path = ROADMAP_INDEX_PATH
    manifest_path = registries_dir / "manifest.json"

    findings: list[dict[str, str]] = []

    # 0. Load and validate manifest
    if not manifest_path.exists():
        findings.append(_finding("error", "MISSING_MANIFEST",
                                 f"manifest not found at {manifest_path}"))

    try:
        manifest = _parse_json(manifest_path)
    except Exception as exc:
        findings.append(_finding("error", "MANIFEST_PARSE_ERROR",
                                 f"failed to parse manifest: {exc}"))
        return findings

    if not isinstance(manifest, dict):
        findings.append(_finding("error", "MANIFEST_NOT_DICT",
                                 "manifest must be a JSON object"))
        return findings

    schema_version = manifest.get("schema_version")
    if schema_version != "1.0.0":
        findings.append(_finding("error", "UNSUPPORTED_SCHEMA_VERSION",
                                 f"manifest schema_version must be '1.0.0', got {schema_version!r}"))

    arch_version = manifest.get("architecture_version")
    if arch_version != "1.0.0":
        findings.append(_finding("error", "UNSUPPORTED_ARCH_VERSION",
                                 f"manifest architecture_version must be '1.0.0', got {arch_version!r}"))

    gen_root = manifest.get("generated_snapshot_output_root")
    if gen_root != ".codex-context/project-memory/":
        findings.append(_finding("error", "INVALID_GENERATED_ROOT",
                                 f"generated_snapshot_output_root must be '.codex-context/project-memory/'"))

    registry_decls = manifest.get("registries")
    if not isinstance(registry_decls, list):
        findings.append(_finding("error", "MISSING_REGISTRIES",
                                 "manifest must contain a 'registries' list"))
        return findings

    # Build registry map: filename -> decl
    reg_by_filename: dict[str, dict[str, Any]] = {}
    for decl in registry_decls:
        fn = decl.get("filename")
        if not isinstance(fn, str):
            findings.append(_finding("error", "INVALID_REGISTRY_DECL",
                                     f"registry declaration missing 'filename': {decl!r}"))
            continue
        if fn in reg_by_filename:
            findings.append(_finding("error", "DUPLICATE_REGISTRY_DECL",
                                     f"duplicate registry filename in manifest: {fn}"))
        reg_by_filename[fn] = decl

    # 1. Verify all declared registries have files, no undeclared files
    declared_filenames = set(reg_by_filename.keys())
    actual_filenames: set[str] = set()
    if registries_dir.exists():
        for entry in registries_dir.iterdir():
            if entry.is_file() and entry.suffix == ".json":
                actual_filenames.add(entry.name)

    for fn in sorted(declared_filenames):
        if fn not in actual_filenames:
            findings.append(_finding("error", "MISSING_REGISTRY_FILE",
                                     f"declared registry file not found: {fn}",
                                     registry_file=fn))

    for fn in sorted(actual_filenames - declared_filenames - {"manifest.json"}):
        findings.append(_finding("error", "UNDECLARED_REGISTRY_FILE",
                                 f"registry file not declared in manifest: {fn}",
                                 registry_file=fn))

    if findings:
        return _sort_findings(findings)

    # 2. Load all registries
    registries: dict[str, dict[str, Any]] = {}
    for fn in sorted(declared_filenames):
        path = registries_dir / fn
        try:
            data = _parse_json(path)
        except Exception as exc:
            findings.append(_finding("error", "REGISTRY_PARSE_ERROR",
                                     f"failed to parse {fn}: {exc}",
                                     registry_file=fn))
            continue
        if not isinstance(data, dict):
            findings.append(_finding("error", "REGISTRY_NOT_DICT",
                                     f"registry file must be a JSON object: {fn}",
                                     registry_file=fn))
            continue
        registries[fn] = data

    if findings:
        return _sort_findings(findings)

    # 3. Validate each registry container and its records
    all_ids: dict[str, str] = {}  # id -> filename
    all_record_types: dict[str, str] = {}  # id -> type
    task_records_by_task_id: dict[str, dict[str, Any]] = {}

    for fn in sorted(declared_filenames):
        data = registries.get(fn)
        if data is None:
            continue
        decl = reg_by_filename[fn]

        expected_type = decl.get("record_type")
        registry_type = data.get("registry_type")
        if registry_type != expected_type:
            findings.append(_finding("error", "REGISTRY_TYPE_MISMATCH",
                                     f"{fn}: registry_type '{registry_type}' != declared '{expected_type}'",
                                     registry_file=fn))

        sv = data.get("schema_version")
        if sv != "1.0.0":
            findings.append(_finding("error", "REGISTRY_SCHEMA_VERSION",
                                     f"{fn}: schema_version must be '1.0.0', got {sv!r}",
                                     registry_file=fn))

        records = data.get("records")
        if not isinstance(records, list):
            findings.append(_finding("error", "REGISTRY_NO_RECORDS",
                                     f"{fn}: must contain a 'records' list",
                                     registry_file=fn))
            continue

        allowed_classes = set(decl.get("allowed_authority_classes", []))

        for idx, record in enumerate(records):
            if not isinstance(record, dict):
                findings.append(_finding("error", "RECORD_NOT_DICT",
                                         f"{fn}[{idx}]: record must be a dict",
                                         registry_file=fn))
                continue

            rid = record.get("id")
            rtype = record.get("type")
            rec_label = f"{fn}[{idx}]"

            # id check
            if not isinstance(rid, str) or not rid:
                findings.append(_finding("error", "MISSING_ID",
                                         f"{rec_label}: missing or empty id",
                                         registry_file=fn))
            elif not _STABLE_ID_RE.match(rid):
                findings.append(_finding("error", "INVALID_ID",
                                         f"{rec_label}: id '{rid}' does not match stable id pattern",
                                         registry_file=fn, record_id=rid))
            else:
                if rid in all_ids:
                    findings.append(_finding("error", "DUPLICATE_ID",
                                             f"{rec_label}: duplicate id '{rid}' (first seen in {all_ids[rid]})",
                                             registry_file=fn, record_id=rid))
                else:
                    all_ids[rid] = fn

            # type check
            if rtype != expected_type:
                findings.append(_finding("error", "RECORD_TYPE_MISMATCH",
                                         f"{rec_label}: record type '{rtype}' != expected '{expected_type}'",
                                         registry_file=fn, record_id=(rid or "")))

            if rid:
                all_record_types[rid] = (rtype or "")

            if rtype == "task":
                task_id = record.get("task_id")
                if not isinstance(task_id, str) or not task_id:
                    findings.append(_finding(
                        "error", "MISSING_TASK_ID",
                        f"{rec_label}: task record missing non-empty task_id",
                        registry_file=fn, record_id=(rid or ""),
                    ))
                elif task_id in task_records_by_task_id:
                    findings.append(_finding(
                        "error", "DUPLICATE_TASK_IDENTITY",
                        f"{rec_label}: duplicate task_id '{task_id}'",
                        registry_file=fn, record_id=(rid or ""),
                    ))
                else:
                    task_records_by_task_id[task_id] = record

            # schema_version
            rsv = record.get("schema_version")
            if rsv != "1.0.0":
                findings.append(_finding("error", "RECORD_SCHEMA_VERSION",
                                         f"{rec_label}: schema_version must be '1.0.0', got {rsv!r}",
                                         registry_file=fn, record_id=(rid or "")))

            # title
            title = record.get("title")
            if not isinstance(title, str) or not title.strip():
                findings.append(_finding("error", "MISSING_TITLE",
                                         f"{rec_label}: missing or empty title",
                                         registry_file=fn, record_id=(rid or "")))

            # authority_class
            ac = record.get("authority_class")
            if ac not in TRUST_CLASSES:
                findings.append(_finding("error", "INVALID_TRUST_CLASS",
                                         f"{rec_label}: unknown authority_class '{ac}'",
                                         registry_file=fn, record_id=(rid or "")))
            elif allowed_classes and ac not in allowed_classes:
                findings.append(_finding("error", "DISALLOWED_TRUST_CLASS",
                                         f"{rec_label}: authority_class '{ac}' not in allowed classes for {fn}",
                                         registry_file=fn, record_id=(rid or "")))

            # lifecycle
            lifecycle = record.get("lifecycle")
            if not isinstance(lifecycle, dict):
                findings.append(_finding("error", "MISSING_LIFECYCLE",
                                         f"{rec_label}: missing lifecycle metadata",
                                         registry_file=fn, record_id=(rid or "")))
            else:
                status = lifecycle.get("status")
                if status not in LIFECYCLE_STATUSES:
                    findings.append(_finding("error", "INVALID_LIFECYCLE_STATUS",
                                             f"{rec_label}: unknown lifecycle status '{status}'",
                                             registry_file=fn, record_id=(rid or "")))
                if status == "superseded":
                    if not lifecycle.get("superseded_by"):
                        findings.append(_finding("error", "SUPERSEDED_WITHOUT_SUPERSEDED_BY",
                                                 f"{rec_label}: status 'superseded' but no superseded_by",
                                                 registry_file=fn, record_id=(rid or "")))
                if status == "current" and lifecycle.get("superseded_by"):
                    findings.append(_finding("error", "CURRENT_WITH_SUPERSEDED_BY",
                                             f"{rec_label}: status 'current' but has superseded_by",
                                             registry_file=fn, record_id=(rid or "")))

                supersedes = lifecycle.get("supersedes")
                if isinstance(supersedes, list):
                    for sid in supersedes:
                        if not isinstance(sid, str) or not _STABLE_ID_RE.match(sid):
                            findings.append(_finding("error", "INVALID_SUPERSEDES_ID",
                                                     f"{rec_label}: invalid supersedes id '{sid}'",
                                                     registry_file=fn, record_id=(rid or "")))

                effective_from = lifecycle.get("effective_from")
                if effective_from is not None:
                    if not isinstance(effective_from, str):
                        findings.append(_finding("error", "EFFECTIVE_FROM_NOT_STRING",
                                                 f"{rec_label}: effective_from must be a string",
                                                 registry_file=fn, record_id=(rid or "")))
                    elif not _ISO8601_RE.match(effective_from):
                        findings.append(_finding("error", "INVALID_TIMESTAMP",
                                                 f"{rec_label}: effective_from '{effective_from}' is not valid ISO 8601",
                                                 registry_file=fn, record_id=(rid or "")))

            # provenance
            provenance = record.get("provenance")
            if isinstance(provenance, dict):
                created_at = provenance.get("created_at")
                if created_at is not None:
                    if not isinstance(created_at, str):
                        findings.append(_finding("error", "CREATED_AT_NOT_STRING",
                                                 f"{rec_label}: provenance.created_at must be a string",
                                                 registry_file=fn, record_id=(rid or "")))
                    elif not _ISO8601_RE.match(created_at):
                        findings.append(_finding("error", "INVALID_TIMESTAMP",
                                                 f"{rec_label}: provenance.created_at '{created_at}' is not valid ISO 8601",
                                                 registry_file=fn, record_id=(rid or "")))

                source_locators = provenance.get("source_locators")
                if isinstance(source_locators, list):
                    for sl_idx, sl in enumerate(source_locators):
                        sl_errors = _validate_source_locator(sl)
                        for err in sl_errors:
                            findings.append(_finding("error", "INVALID_SOURCE_LOCATOR",
                                                     f"{rec_label}: source_locators[{sl_idx}]: {err}",
                                                     registry_file=fn, record_id=(rid or "")))

            # Generated/authoritativeness checks
            if ac in ("generated_evidence", "untrusted"):
                if rtype in ("project", "feature", "boundary", "task", "decision",
                             "capability", "dependency", "owner_decision"):
                    if ac != "generated_evidence" or rtype != "evidence":
                        findings.append(_finding("error", "UNAUTHORITATIVE_RECORD",
                                                 f"{rec_label}: record with authority_class '{ac}' cannot carry default-authority record type '{rtype}'",
                                                 registry_file=fn, record_id=(rid or "")))

    # 4. Cross-record reference validation
    for fn in sorted(declared_filenames):
        data = registries.get(fn)
        if data is None:
            continue
        records = data.get("records", [])
        for idx, record in enumerate(records):
            if not isinstance(record, dict):
                continue
            rid = record.get("id", "")
            rec_label = f"{fn}[{idx}]"

            lifecycle = record.get("lifecycle")
            if isinstance(lifecycle, dict):
                superseded_by = lifecycle.get("superseded_by")
                if isinstance(superseded_by, str) and superseded_by:
                    if superseded_by not in all_ids:
                        findings.append(_finding("error", "UNKNOWN_SUPERSEDED_BY",
                                                 f"{rec_label}: superseded_by '{superseded_by}' not found in any registry",
                                                 registry_file=fn, record_id=rid))
                    else:
                        # Check supersession symmetry
                        target_fn = all_ids[superseded_by]
                        target_data = registries.get(target_fn)
                        if target_data:
                            target_records = target_data.get("records", [])
                            target_record = None
                            for tr in target_records:
                                if tr.get("id") == superseded_by:
                                    target_record = tr
                                    break
                            if target_record:
                                target_lc = target_record.get("lifecycle", {})
                                target_supersedes = target_lc.get("supersedes", [])
                                if rid not in target_supersedes:
                                    findings.append(_finding("error", "SUPERSESSION_ASYMMETRY",
                                                             f"{rec_label}: superseded_by '{superseded_by}' does not reference back in its supersedes list",
                                                             registry_file=fn, record_id=rid))

                supersedes = lifecycle.get("supersedes")
                if isinstance(supersedes, list):
                    for sid in supersedes:
                        if sid not in all_ids:
                            findings.append(_finding("error", "UNKNOWN_SUPERSEDES",
                                                     f"{rec_label}: supersedes '{sid}' not found in any registry",
                                                     registry_file=fn, record_id=rid))

            # owner decision ref
            provenance = record.get("provenance")
            if isinstance(provenance, dict):
                odr = provenance.get("owner_decision_ref")
                if isinstance(odr, str) and odr:
                    if odr not in all_ids:
                        findings.append(_finding("error", "UNKNOWN_OWNER_DECISION_REF",
                                                 f"{rec_label}: owner_decision_ref '{odr}' not found in any registry",
                                                 registry_file=fn, record_id=rid))

            # task-specific validation
            if record.get("type") == "task":
                parent_task_id = record.get("parent_task_id")
                if isinstance(parent_task_id, str) and parent_task_id:
                    expected_pid = f"task:{parent_task_id}"
                    if expected_pid not in all_ids:
                        findings.append(_finding("error", "UNKNOWN_PARENT_TASK",
                                                 f"{rec_label}: parent_task_id '{parent_task_id}' not found as task record",
                                                 registry_file=fn, record_id=rid))

                depends_on = record.get("depends_on")
                if isinstance(depends_on, list):
                    for dep in depends_on:
                        expected_did = f"task:{dep}"
                        if expected_did not in all_ids:
                            findings.append(_finding("error", "UNKNOWN_TASK_DEPENDENCY",
                                                     f"{rec_label}: depends_on '{dep}' not found as task record",
                                                     registry_file=fn, record_id=rid))

            # dependency record validation
            if record.get("type") == "dependency":
                source_id = record.get("source_id")
                target_id = record.get("target_id")
                if isinstance(source_id, str) and source_id:
                    if source_id not in all_ids:
                        findings.append(_finding("error", "UNKNOWN_SOURCE_ID",
                                                 f"{rec_label}: source_id '{source_id}' not found",
                                                 registry_file=fn, record_id=rid))
                if isinstance(target_id, str) and target_id:
                    if target_id not in all_ids:
                        findings.append(_finding("error", "UNKNOWN_TARGET_ID",
                                                 f"{rec_label}: target_id '{target_id}' not found",
                                                 registry_file=fn, record_id=rid))

            # Git SHA validation
            for field_name in ("bound_commit",):
                value = record.get(field_name)
                if isinstance(value, str) and value:
                    if not _GIT_SHA_RE.match(value):
                        findings.append(_finding("error", "INVALID_GIT_SHA",
                                                 f"{rec_label}: {field_name} '{value}' is not a valid full Git SHA",
                                                 registry_file=fn, record_id=rid))

    # 5. Detect dependency cycles of any length in normalized task records.
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(task_id: str, trail: tuple[str, ...]) -> None:
        if task_id in visited:
            return
        if task_id in visiting:
            cycle = trail[trail.index(task_id):] + (task_id,)
            findings.append(_finding(
                "error", "TASK_DEPENDENCY_CYCLE",
                "task dependency cycle: " + " -> ".join(cycle),
                registry_file="tasks.json", record_id=f"task:{task_id}",
            ))
            return
        visiting.add(task_id)
        record = task_records_by_task_id.get(task_id, {})
        dependencies = record.get("depends_on", [])
        if isinstance(dependencies, list):
            for dependency in dependencies:
                if isinstance(dependency, str) and dependency in task_records_by_task_id:
                    visit(dependency, trail + (task_id,))
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in sorted(task_records_by_task_id):
        visit(task_id, ())

    # 6. Prove complete normalized coverage for the roadmap-declared remaining
    # MVP parent set. The validator derives descendants and edges generically;
    # generated evidence is never an input to this authority comparison.
    if roadmap_index_path is not None:
        try:
            roadmap = _parse_json(roadmap_index_path)
        except Exception as exc:
            findings.append(_finding(
                "error", "ROADMAP_INDEX_PARSE_ERROR",
                f"failed to parse roadmap index: {exc}",
                registry_file="tasks.json",
            ))
            return _sort_findings(findings)

        roadmap_tasks = roadmap.get("tasks") if isinstance(roadmap, dict) else None
        frontier = roadmap.get("active_frontier") if isinstance(roadmap, dict) else None
        roots = frontier.get("remaining_mvp_parent_task_ids") if isinstance(frontier, dict) else None
        if not isinstance(roadmap_tasks, list) or not isinstance(roots, list) or not roots:
            findings.append(_finding(
                "error", "MISSING_REMAINING_MVP_SCOPE",
                "roadmap index must declare tasks and non-empty active_frontier.remaining_mvp_parent_task_ids",
                registry_file="tasks.json",
            ))
            return _sort_findings(findings)

        roadmap_by_id: dict[str, dict[str, Any]] = {}
        for item in roadmap_tasks:
            if not isinstance(item, dict):
                continue
            task_id = item.get("id")
            if not isinstance(task_id, str) or not task_id:
                continue
            if task_id in roadmap_by_id:
                findings.append(_finding(
                    "error", "DUPLICATE_ROADMAP_TASK_IDENTITY",
                    f"duplicate roadmap task id '{task_id}'",
                    registry_file="tasks.json", record_id=f"task:{task_id}",
                ))
            else:
                roadmap_by_id[task_id] = item

        root_set = {item for item in roots if isinstance(item, str)}
        for root_id in sorted(root_set):
            if root_id not in roadmap_by_id:
                findings.append(_finding(
                    "error", "UNKNOWN_REMAINING_MVP_PARENT",
                    f"remaining MVP parent '{root_id}' is not a roadmap task",
                    registry_file="tasks.json", record_id=f"task:{root_id}",
                ))

        def is_remaining_mvp_task(task_id: str) -> bool:
            seen: set[str] = set()
            current = task_id
            while current and current not in seen:
                if current in root_set:
                    return True
                seen.add(current)
                item = roadmap_by_id.get(current, {})
                parent = item.get("parent")
                current = parent if isinstance(parent, str) else ""
            return False

        dependency_edges = {
            (record.get("source_id"), record.get("target_id"))
            for record in registries.get("dependencies.json", {}).get("records", [])
            if isinstance(record, dict) and record.get("type") == "dependency"
        }
        lifecycle_map = {
            "active": "in_progress",
            "published/active": "in_progress",
            "planned": "planned",
            "complete": "complete",
            "done": "complete",
            "historical": "historical",
            "deferred": "deferred",
        }

        for task_id, roadmap_task in sorted(roadmap_by_id.items()):
            if not is_remaining_mvp_task(task_id):
                continue
            normalized = task_records_by_task_id.get(task_id)
            if normalized is None or normalized.get("authority_class") != "authoritative":
                findings.append(_finding(
                    "error", "MISSING_NORMALIZED_MVP_TASK",
                    f"roadmap remaining-MVP task '{task_id}' lacks exactly one authoritative normalized task record",
                    registry_file="tasks.json", record_id=f"task:{task_id}",
                ))
                continue

            expected_parent = roadmap_task.get("parent")
            if normalized.get("parent_task_id") != expected_parent:
                findings.append(_finding(
                    "error", "MVP_TASK_PARENT_MISMATCH",
                    f"{task_id}: roadmap parent {expected_parent!r} != normalized parent {normalized.get('parent_task_id')!r}",
                    registry_file="tasks.json", record_id=f"task:{task_id}",
                ))

            roadmap_dependencies = roadmap_task.get("depends_on", [])
            normalized_dependencies = normalized.get("depends_on", [])
            if isinstance(roadmap_dependencies, list) and isinstance(normalized_dependencies, list):
                if sorted(roadmap_dependencies) != sorted(normalized_dependencies):
                    findings.append(_finding(
                        "error", "MVP_TASK_DEPENDENCY_MISMATCH",
                        f"{task_id}: roadmap dependencies {sorted(roadmap_dependencies)!r} != normalized dependencies {sorted(normalized_dependencies)!r}",
                        registry_file="tasks.json", record_id=f"task:{task_id}",
                    ))
                for dependency in roadmap_dependencies:
                    if dependency not in task_records_by_task_id:
                        findings.append(_finding(
                            "error", "MISSING_NORMALIZED_MVP_DEPENDENCY",
                            f"{task_id}: dependency '{dependency}' lacks a normalized task record",
                            registry_file="tasks.json", record_id=f"task:{task_id}",
                        ))
                    edge = (f"task:{task_id}", f"task:{dependency}")
                    if edge not in dependency_edges:
                        findings.append(_finding(
                            "error", "MISSING_NORMALIZED_MVP_DEPENDENCY_EDGE",
                            f"{task_id}: dependency '{dependency}' lacks a normalized dependency record",
                            registry_file="dependencies.json", record_id=f"task:{task_id}",
                        ))

            expected_lifecycle = lifecycle_map.get(roadmap_task.get("status"))
            actual_lifecycle = normalized.get("lifecycle", {}).get("status")
            if expected_lifecycle is not None and actual_lifecycle != expected_lifecycle:
                findings.append(_finding(
                    "error", "MVP_TASK_LIFECYCLE_MISMATCH",
                    f"{task_id}: roadmap status {roadmap_task.get('status')!r} expects {expected_lifecycle!r}, got {actual_lifecycle!r}",
                    registry_file="tasks.json", record_id=f"task:{task_id}",
                ))

    return _sort_findings(findings)


def _sort_findings(findings: list[dict[str, str]]) -> list[dict[str, str]]:
    return sorted(findings, key=lambda f: (
        f.get("registry_file", ""),
        f.get("record_id", ""),
        f.get("code", ""),
        f.get("message", ""),
    ))


def main() -> int:
    json_output = "--json" in sys.argv

    try:
        findings = validate()
    except Exception as exc:
        if json_output:
            print(json.dumps({"errors": [{
                "level": "error", "code": "VALIDATOR_EXCEPTION",
                "message": str(exc),
            }]}, indent=2))
        else:
            print("FAIL")
            print(f"- validator exception: {exc}")
        return 1

    errors = [f for f in findings if f["level"] == "error"]
    warnings = [f for f in findings if f["level"] == "warning"]

    if json_output:
        output: dict[str, Any] = {
            "result": "PASS" if not errors else "FAIL",
            "errors": errors,
            "warnings": warnings,
        }
        print(json.dumps(output, indent=2))
    else:
        if errors or warnings:
            print("FAIL" if errors else "PASS (warnings)")
            for f in findings:
                prefix = "ERROR" if f["level"] == "error" else "WARN"
                loc = f.get("registry_file", "")
                rid = f.get("record_id", "")
                where = f"{loc}" + (f":{rid}" if rid else "")
                print(f"  [{prefix}] {where}: {f['code']}: {f['message']}")
        else:
            print("PASS")

    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
