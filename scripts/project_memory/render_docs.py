#!/usr/bin/env python3
"""Deterministic Markdown renderer for Project Memory.

Converts tracked normalized registries and a selected generated snapshot
into human-readable Markdown documentation.

Uses only Python standard-library modules and read-only Git commands.

Usage:
  python3 scripts/project_memory/render_docs.py \
    --repo-root . \
    --snapshot-dir <SNAPSHOT_DIR> \
    --output-root <OUTPUT_ROOT> \
    --task-id <TASK_ID> \
    --run-id <RUN_ID> \
    --generated-at <RFC3339_UTC> \
    --mode publication \
    --json
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

RENDERER_NAME = "project_memory_markdown_renderer"
RENDERER_VERSION = "project_memory_markdown_renderer.v1"

SCHEMA_VERSION = "1.0.0"
ARCHITECTURE_VERSION = "1.0.0"

RENDERED_PAGE_NAMES = (
    "index.md",
    "application-overview.md",
    "product-boundaries.md",
    "features.md",
    "capabilities.md",
    "current-roadmap.md",
    "remaining-work.md",
    "dependencies.md",
    "decisions.md",
    "assets.md",
    "evidence.md",
    "risks-and-open-questions.md",
    "convergence-findings.md",
    "technical-annex.md",
)

RENDERED_PAGE_NAMES_SET = frozenset(RENDERED_PAGE_NAMES)

VALID_MODES = frozenset(["publication", "historical_preview"])

_PUBLICATION_ROOT = ".codex-context/project-memory/rendered"

_SNAPSHOT_REQUIRED_FILES = frozenset([
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
])

_ALLOWED_SEVERITIES = frozenset(["critical", "error", "warning", "info"])
_ALLOWED_CONVERGENCE_RESULTS = frozenset(["PASS", "PASS_WITH_FINDINGS", "BLOCKED"])

_TRUST_CLASSES = frozenset([
    "authoritative",
    "accepted_evidence",
    "generated_evidence",
    "historical",
    "superseded",
    "uncertain",
    "owner_pending",
    "untrusted",
])

_LIFECYCLE_STATUSES = frozenset([
    "current", "planned", "in_progress", "complete", "blocked",
    "deferred", "historical", "superseded", "rejected", "owner_pending",
])

_GIT_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_ISO8601_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$"
)

_CTRL_CHARS_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]")

_LF_RE = re.compile(r"\r\n|\r")

_STABLE_ID_RE = re.compile(
    r"^(project|feature|boundary|task|decision|capability|asset|evidence|dependency|tool|owner-decision):"
    r"[a-zA-Z0-9][a-zA-Z0-9._-]*$"
)

OUTPUT_JSON_FILES = frozenset(["build-manifest.json", "source-snapshot.json"])

_PROTECTED_AUTHORITY_DIRS = frozenset([
    "docs/project-memory",
    "docs/roadmap",
    "scripts/",
    "tests/",
    "backend/",
    "frontend/",
    ".agents/",
    ".opencode/",
    ".github/",
    ".claude/",
    ".cursor/",
])


def _html_escape(text: str) -> str:
    """HTML-escape raw text, neutralise script/event-handler tags."""
    if not isinstance(text, str):
        text = str(text)
    text = html.escape(text, quote=True)
    return text


def _normalize_text(text: str) -> str:
    """Normalize line endings and strip control characters."""
    if not isinstance(text, str):
        text = str(text)
    text = _LF_RE.sub("\n", text)
    text = _CTRL_CHARS_RE.sub("", text)
    return text


def _sanitize_string(text: str) -> str:
    """Full sanitize pipeline for registry text content."""
    if not isinstance(text, str):
        text = str(text)
    text = re.sub(r'(?i)javascript\s*:', '[javascript:]', text)
    text = _normalize_text(text)
    text = _html_escape(text)
    return text


def _escape_table_cell(text: str) -> str:
    """Escape pipe characters for Markdown table cells."""
    return text.replace("|", "\\|")


def _markdown_code(text: str) -> str:
    """Wrap text in backticks for inline code."""
    text = text.replace("`", "\\`")
    return f"`{text}`"


def _compute_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _run_git(args: list[str], repo_root: Path, timeout: int = 30) -> str:
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True, text=True, timeout=timeout, cwd=str(repo_root),
        )
        if result.returncode != 0:
            raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
        return result.stdout.rstrip("\n")
    except FileNotFoundError:
        raise RuntimeError("git command not found")


def _resolve_repo_root(requested: str) -> Path:
    try:
        root = Path(requested).resolve(strict=True)
    except FileNotFoundError:
        raise ValueError(f"Path does not exist: {requested}")
    if not root.is_dir():
        raise ValueError(f"Not a directory: {root}")
    if not (root / ".git").exists():
        raise ValueError(f"Not a Git repository: {root}")
    return root


def _is_path_safe(repo_root: Path, rel_path: str) -> bool:
    try:
        resolved = (repo_root / rel_path).resolve()
        return resolved.is_relative_to(repo_root)
    except (ValueError, OSError):
        return False


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _sort_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(records, key=lambda r: (r.get("type", ""), r.get("id", "")))


def _group_by_status(
    records: list[dict[str, Any]],
    status_field: str = "lifecycle.status",
) -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for rec in records:
        status = "unknown"
        if status_field == "lifecycle.status":
            lc = rec.get("lifecycle", {})
            if isinstance(lc, dict):
                status = lc.get("status", "unknown")
        else:
            status = rec.get(status_field, "unknown")
        groups.setdefault(str(status), []).append(rec)
    return groups


_PM_PARENT_TASK_ID = "PHASE8-IMPL-026"
_APP_FRONTIER_TASK_ID = "PHASE8-IMPL-024-T003A"

_PM_TASK_DISPLAY_ORDER = (
    "PHASE8-IMPL-026-T001",
    "PHASE8-IMPL-026-T002",
    "PHASE8-IMPL-026-T003",
    "PHASE8-IMPL-026-T004",
    "PHASE8-IMPL-026-T004A",
    "PHASE8-IMPL-026-T004B",
    "PHASE8-IMPL-026-T004C",
    "PHASE8-IMPL-026-T005",
)

_PM_TASK_LABELS = {
    "PHASE8-IMPL-026-T001": "T001 (Authority/Lifecycle foundation)",
    "PHASE8-IMPL-026-T002": "T002 (Schema/registry architecture)",
    "PHASE8-IMPL-026-T003": "T003 (Scanners/snapshot builder)",
    "PHASE8-IMPL-026-T004": "T004 (Human-readable memory)",
    "PHASE8-IMPL-026-T004A": "T004A (Architecture/remediation)",
    "PHASE8-IMPL-026-T004B": "T004B (Markdown renderer)",
    "PHASE8-IMPL-026-T004C": "T004C (Clean-HEAD publication)",
    "PHASE8-IMPL-026-T005": "T005 (Context-tool integration)",
}


def _get_task_by_id(tasks: list[dict[str, Any]], task_id: str) -> dict[str, Any] | None:
    for t in tasks:
        if t.get("task_id") == task_id:
            return t
    return None


def _get_children(tasks: list[dict[str, Any]], parent_task_id: str) -> list[dict[str, Any]]:
    children = [t for t in tasks if t.get("parent_task_id") == parent_task_id]
    children.sort(key=lambda t: t.get("task_id", ""))
    return children


def _validate_task_records(tasks: list[dict[str, Any]]) -> list[str]:
    errors = []
    seen_ids: dict[str, int] = {}
    for t in tasks:
        tid = t.get("task_id", "")
        if tid in seen_ids:
            errors.append(f"Duplicate task_id: {tid}")
        else:
            seen_ids[tid] = 1
    for t in tasks:
        parent = t.get("parent_task_id")
        if parent and parent not in seen_ids:
            errors.append(f"Parent task_id '{parent}' not found for task {t.get('task_id', '')}")
    allowed_lifecycles = frozenset(["planned", "in_progress", "complete", "blocked",
                                     "deferred", "historical", "superseded", "owner_pending"])
    for t in tasks:
        lc_status = t.get("lifecycle", {}).get("status", "")
        if lc_status not in allowed_lifecycles:
            errors.append(f"Unsupported lifecycle status '{lc_status}' for task {t.get('task_id', '')}")
    return errors


def _identify_completed_children(
    tasks: list[dict[str, Any]], parent_task_id: str
) -> list[dict[str, Any]]:
    children = _get_children(tasks, parent_task_id)
    return [c for c in children if c.get("lifecycle", {}).get("status") == "complete"]


def _identify_next_planned_child(
    tasks: list[dict[str, Any]], parent_task_id: str
) -> dict[str, Any] | None:
    children = _get_children(tasks, parent_task_id)
    planned = [c for c in children if c.get("lifecycle", {}).get("status") == "planned"]
    return planned[0] if planned else None


def _derive_task_display_status(task: dict[str, Any]) -> str:
    lc = task.get("lifecycle", {})
    status = lc.get("status", "unknown")
    notes = task.get("notes", "")
    if status == "complete":
        if "PASS-WITH-FINDINGS" in notes:
            return "complete/PASS-WITH-FINDINGS"
        if "PASS" in notes:
            return "complete/PASS"
        return "complete"
    if status == "planned":
        if "inactive" in notes.lower() or "Inactive" in notes:
            return "planned/inactive"
        return "planned"
    if status == "in_progress":
        return "in progress"
    return status


def load_and_validate_inputs(
    repo_root: str,
) -> dict[str, Any]:
    """Load registry manifest and all registries, validate them."""
    root = _resolve_repo_root(repo_root)
    registries_dir = root / "docs" / "project-memory" / "registries"
    schema_path = root / "docs" / "project-memory" / "schemas" / "project-memory.schema.json"

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from scripts.project_memory import validate_registries as vr

    findings = vr.validate(registries_dir)
    errors = [f for f in findings if f.get("level") == "error"]
    if errors:
        raise ValueError(f"Registry validation failed with {len(errors)} errors")

    manifest_path = registries_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    sv = manifest.get("schema_version")
    if sv != SCHEMA_VERSION:
        raise ValueError(f"Unsupported schema version: {sv}")
    av = manifest.get("architecture_version")
    if av != ARCHITECTURE_VERSION:
        raise ValueError(f"Unsupported architecture version: {av}")

    registries: dict[str, dict[str, Any]] = {}
    for decl in manifest.get("registries", []):
        fn = decl.get("filename", "")
        if fn == "manifest.json":
            continue
        reg_path = registries_dir / fn
        if not reg_path.is_file():
            raise ValueError(f"Registry file not found: {fn}")
        data = json.loads(reg_path.read_text(encoding="utf-8"))
        registries[fn] = data

    return {
        "manifest": manifest,
        "registries": registries,
        "registry_dir": str(registries_dir),
    }


def validate_snapshot_package(snapshot_dir: str, repo_root: Path) -> dict[str, Any]:
    """Validate a snapshot package directory.

    Returns the parsed snapshot data bundle.
    """
    snap = Path(snapshot_dir)
    if not snap.is_dir():
        raise ValueError(f"Snapshot directory not found: {snapshot_dir}")

    actual_files: set[str] = set()
    for entry in snap.iterdir():
        if entry.name.startswith("."):
            continue
        if entry.is_file():
            actual_files.add(entry.name)
        elif entry.is_dir():
            raise ValueError(f"Unexpected subdirectory in snapshot: {entry.name}")

    missing = _SNAPSHOT_REQUIRED_FILES - actual_files
    if missing:
        raise ValueError(f"Missing required snapshot files: {sorted(missing)}")
    unexpected = actual_files - _SNAPSHOT_REQUIRED_FILES
    if unexpected:
        raise ValueError(f"Unexpected files in snapshot: {sorted(unexpected)}")

    inventory_path = snap / "FILE-INVENTORY.txt"
    inventory_text = inventory_path.read_text(encoding="utf-8").strip()
    inventory_lines = [l.strip() for l in inventory_text.split("\n") if l.strip()]
    inventory_set = set(inventory_lines)

    for fn in inventory_lines:
        if fn.startswith("/") or ".." in fn.replace("\\", "/").split("/"):
            raise ValueError(f"Traversal or absolute path in FILE-INVENTORY.txt: {fn}")

    snapshot_data: dict[str, Any] = {}
    for fn in actual_files:
        if fn == "FILE-INVENTORY.txt":
            continue
        if fn == "SHA256SUMS":
            continue
        if fn.endswith(".json"):
            try:
                snapshot_data[fn] = json.loads((snap / fn).read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Malformed JSON in {fn}: {exc}")
        else:
            snapshot_data[fn] = (snap / fn).read_text(encoding="utf-8")

    sha256_path = snap / "SHA256SUMS"
    sha256_text = sha256_path.read_text(encoding="utf-8").strip()
    sha256_entries: dict[str, str] = {}
    for line in sha256_text.split("\n"):
        line = line.strip()
        if not line:
            continue
        parts = line.split("  ", 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid SHA256SUMS line: {line}")
        digest, fname = parts
        if fname == "SHA256SUMS":
            raise ValueError("SHA256SUMS must not hash itself")
        if fname.startswith("/") or ".." in fname.replace("\\", "/").split("/"):
            raise ValueError(f"Traversal or absolute path in SHA256SUMS: {fname}")
        sha256_entries[fname] = digest

    covered = set(sha256_entries.keys())
    expected_covered = actual_files - {"SHA256SUMS"}
    if covered != expected_covered:
        missing_cov = expected_covered - covered
        extra_cov = covered - expected_covered
        msg = ""
        if missing_cov:
            msg += f"Missing checksum coverage: {sorted(missing_cov)}. "
        if extra_cov:
            msg += f"Extra checksum entries: {sorted(extra_cov)}."
        raise ValueError(msg.strip())

    for fname, expected_digest in sha256_entries.items():
        actual_digest = _compute_sha256(snap / fname)
        if actual_digest != expected_digest:
            raise ValueError(f"Checksum mismatch for {fname}: expected {expected_digest}, got {actual_digest}")

    snapshot = snapshot_data.get("snapshot.json", {})
    if not isinstance(snapshot, dict):
        raise ValueError("snapshot.json must be a JSON object")

    ac = snapshot.get("authority_class", "")
    if ac != "generated_evidence":
        raise ValueError(f"Snapshot authority_class must be 'generated_evidence', got {ac!r}")
    if snapshot.get("authoritative") is True:
        raise ValueError("Snapshot must not claim authoritative status")

    bound_commit = snapshot.get("bound_commit", "")
    if not _GIT_SHA_RE.match(bound_commit):
        raise ValueError(f"Invalid or missing bound_commit: {bound_commit!r}")

    snap_branch = snapshot.get("branch", "")
    if not snap_branch:
        raise ValueError("Missing branch in snapshot")

    snapshot_task_id = snapshot.get("task_id", "")
    if not snapshot_task_id:
        raise ValueError("Missing task_id in snapshot")

    snapshot_generated_at = snapshot.get("generated_at", "")
    if not snapshot_generated_at:
        raise ValueError("Missing generated_at in snapshot")

    pub_eligible = snapshot.get("publication_eligible", False)

    convergence = snapshot_data.get("convergence-findings.json", {})
    if not isinstance(convergence, dict):
        raise ValueError("convergence-findings.json must be a JSON object")

    conv_result = convergence.get("result", "")
    if conv_result not in _ALLOWED_CONVERGENCE_RESULTS:
        raise ValueError(f"Invalid convergence result: {conv_result!r}")

    findings = convergence.get("findings", [])
    if not isinstance(findings, list):
        raise ValueError("convergence findings must be a list")

    for f in findings:
        sev = f.get("severity", "")
        if sev not in _ALLOWED_SEVERITIES:
            raise ValueError(f"Invalid finding severity: {sev!r}")
        code = f.get("code", "")
        if not code:
            raise ValueError("Finding missing code")
        fid = f.get("finding_id", "")
        if not fid:
            raise ValueError("Finding missing finding_id")

    source_inventory = snapshot_data.get("source-inventory.json", {})
    source_hashes = snapshot_data.get("source-hashes.json", {})

    return {
        "snapshot_dir": str(snap),
        "snapshot": snapshot,
        "convergence": convergence,
        "findings": findings,
        "bound_commit": bound_commit,
        "snapshot_branch": snap_branch,
        "snapshot_task_id": snapshot_task_id,
        "snapshot_run_id": snapshot.get("snapshot_id", "").split("/")[-1] if "/" in snapshot.get("snapshot_id", "") else "",
        "snapshot_generated_at": snapshot_generated_at,
        "publication_eligible": pub_eligible,
        "conv_result": conv_result,
        "source_inventory": source_inventory,
        "source_hashes": source_hashes,
        "run_metadata": snapshot_data.get("run-metadata.json", {}),
        "registry_validation": snapshot_data.get("registry-validation.json", {}),
    }


def classify_freshness(
    bound_commit: str,
    snapshot_branch: str,
    target_commit: str,
    target_branch: str,
    mode: str,
) -> str:
    """Classify freshness of snapshot relative to target."""
    if mode == "historical_preview":
        return "historical"
    if snapshot_branch != target_branch:
        return "stale"
    if bound_commit != target_commit:
        return "stale"
    return "current"


def _build_page_model(
    registries: dict[str, dict[str, Any]],
    manifest: dict[str, Any],
    findings: list[dict[str, Any]],
    source_inventory: dict[str, Any],
    source_hashes: dict[str, Any],
    missing_sources: set[str],
) -> dict[str, Any]:
    """Build the complete page model from registries and snapshot data."""
    model: dict[str, Any] = {}

    all_records: list[dict[str, Any]] = []
    records_by_type: dict[str, list[dict[str, Any]]] = {}
    records_by_id: dict[str, dict[str, Any]] = {}

    reg_by_filename: dict[str, dict[str, Any]] = {}
    for decl in manifest.get("registries", []):
        reg_by_filename[decl["filename"]] = decl

    for fn, data in registries.items():
        rtype = data.get("registry_type", "")
        recs = data.get("records", [])
        if isinstance(recs, list):
            records_by_type[rtype] = recs
            for rec in recs:
                if isinstance(rec, dict):
                    rid = rec.get("id", "")
                    if rid:
                        records_by_id[rid] = rec
                        all_records.append(rec)

    missing_set = missing_sources

    model["projects"] = records_by_type.get("project", [])
    model["features"] = records_by_type.get("feature", [])
    model["boundaries"] = records_by_type.get("boundary", [])
    model["tasks"] = records_by_type.get("task", [])
    model["decisions"] = records_by_type.get("decision", [])
    model["capabilities"] = records_by_type.get("capability", [])
    model["assets"] = records_by_type.get("asset", [])
    model["evidence"] = records_by_type.get("evidence", [])
    model["dependencies"] = records_by_type.get("dependency", [])
    model["tools"] = records_by_type.get("tool", [])
    model["owner_decisions"] = records_by_type.get("owner_decision", [])
    model["findings"] = findings
    model["all_records"] = all_records
    model["records_by_id"] = records_by_id
    model["records_by_type"] = records_by_type
    model["missing_sources"] = missing_set

    counts_by_type = {rt: len(recs) for rt, recs in records_by_type.items()}
    model["counts_by_type"] = counts_by_type

    counts_by_auth: dict[str, int] = {}
    for rec in all_records:
        ac = rec.get("authority_class", "unknown")
        counts_by_auth[ac] = counts_by_auth.get(ac, 0) + 1
    model["counts_by_authority"] = counts_by_auth

    counts_by_lifecycle: dict[str, int] = {}
    for rec in all_records:
        lc = rec.get("lifecycle", {})
        st = lc.get("status", "unknown") if isinstance(lc, dict) else "unknown"
        counts_by_lifecycle[st] = counts_by_lifecycle.get(st, 0) + 1
    model["counts_by_lifecycle"] = counts_by_lifecycle

    model["total_records"] = len(all_records)

    finding_by_code: dict[str, int] = {}
    finding_by_severity: dict[str, int] = {}
    for f in findings:
        code = f.get("code", "unknown")
        sev = f.get("severity", "unknown")
        finding_by_code[code] = finding_by_code.get(code, 0) + 1
        finding_by_severity[sev] = finding_by_severity.get(sev, 0) + 1
    model["finding_by_code"] = finding_by_code
    model["finding_by_severity"] = finding_by_severity

    return model


def _render_banner(
    mode: str,
    freshness: str,
    snapshot_task_id: str,
    snapshot_run_id: str,
    snapshot_branch: str,
    bound_commit: str,
    target_branch: str,
    target_commit: str,
    generated_at: str,
    convergence_result: str,
    publication_eligible: bool,
    missing_source_count: int,
) -> str:
    lines: list[str] = []
    lines.append("<!--")
    lines.append("  Generated evidence — not project authority")
    lines.append(f"  Renderer: {RENDERER_VERSION}")
    lines.append(f"  Mode: {mode}")
    lines.append(f"  Source snapshot task ID: {snapshot_task_id}")
    lines.append(f"  Source snapshot run ID: {snapshot_run_id}")
    lines.append(f"  Source snapshot branch: {snapshot_branch}")
    lines.append(f"  Source snapshot bound commit: {bound_commit}")
    lines.append(f"  Target branch: {target_branch}")
    lines.append(f"  Target commit: {target_commit}")
    lines.append(f"  Generated: {generated_at}")
    lines.append(f"  Convergence result: {convergence_result}")
    lines.append(f"  Freshness: {freshness}")
    lines.append(f"  Publication eligible: {publication_eligible}")
    lines.append(f"  Unavailable source count: {missing_source_count}")
    lines.append(f"  See: convergence-findings.md")
    lines.append(f"  See: technical-annex.md")
    lines.append("-->")
    lines.append("")
    lines.append("# Generated Evidence — Not Project Authority")
    lines.append("")
    lines.append("> **Generated evidence — not project authority.**  ")
    lines.append(f"> Renderer: `{RENDERER_VERSION}` | Mode: `{mode}`  ")
    lines.append(f"> Source snapshot: `{snapshot_task_id}/{snapshot_run_id}`  ")
    lines.append(f"> Snapshot bound commit: `{bound_commit}` on branch `{snapshot_branch}`  ")
    lines.append(f"> Target: `{target_commit}` on branch `{target_branch}`  ")
    lines.append(f"> Generated: {generated_at}  ")
    lines.append(f"> Convergence: `{convergence_result}` | Freshness: `{freshness}`  ")
    lines.append(f"> Publication eligible: `{publication_eligible}`  ")
    lines.append(f"> Unavailable sources: {missing_source_count}  ")
    lines.append(f"> See [convergence-findings.md](convergence-findings.md) | [technical-annex.md](technical-annex.md)")
    lines.append("")

    if freshness == "historical":
        lines.append("> **Historical preview — this snapshot does not represent the current repository commit.**")
        lines.append("")

    return "\n".join(lines)


def _source_availability(
    locators: list[dict[str, Any]],
    repo_root: Path,
    missing_set: set[str],
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for loc in locators:
        path = loc.get("path", "")
        info = {
            "path": path,
            "line_start": loc.get("line_start"),
            "line_end": loc.get("line_end"),
            "json_pointer": loc.get("json_pointer"),
            "available": path not in missing_set,
            "display": _sanitize_string(path),
        }
        result.append(info)
    return result


def _render_record_table(records: list[dict[str, Any]], fields: list[str]) -> str:
    if not records:
        return "_No records._\n"
    lines: list[str] = []
    header = "| " + " | ".join(fields) + " |"
    lines.append(header)
    sep = "|" + "|".join("---" for _ in fields) + "|"
    lines.append(sep)
    for rec in records:
        cells: list[str] = []
        for field in fields:
            value = _get_field(rec, field)
            cells.append(_escape_table_cell(_sanitize_string(value)))
        lines.append("| " + " | ".join(cells) + " |")
    lines.append("")
    return "\n".join(lines)


def _get_field(rec: dict[str, Any], field: str) -> str:
    if field == "id":
        return _markdown_code(rec.get("id", ""))
    if field == "title":
        return rec.get("title", "")
    if field == "authority_class":
        return rec.get("authority_class", "")
    if field == "lifecycle":
        lc = rec.get("lifecycle", {})
        return lc.get("status", "") if isinstance(lc, dict) else ""
    if field == "status":
        lc = rec.get("lifecycle", {})
        return lc.get("status", "") if isinstance(lc, dict) else ""
    if field == "type":
        return rec.get("type", "")
    if field == "implementation_status":
        return rec.get("implementation_status", "")
    if field == "validated":
        return str(rec.get("validated", ""))
    if field == "implemented":
        return str(rec.get("implemented", ""))
    if field == "project_id":
        return rec.get("project_id", "")
    if field == "boundary_id":
        return rec.get("boundary_id", "")
    if field == "category":
        return rec.get("category", "")
    if field == "is_non_negotiable":
        return str(rec.get("is_non_negotiable", ""))
    if field == "severity":
        return rec.get("severity", "")
    if field == "code":
        return rec.get("code", "")
    if field == "blocks_publication":
        return str(rec.get("blocks_publication", ""))
    if field == "owner_review_required":
        return str(rec.get("owner_review_required", ""))
    if field == "task_id":
        return rec.get("task_id", "")
    if field == "parent_task_id":
        return rec.get("parent_task_id", "")
    if field == "depends_on":
        deps = rec.get("depends_on", [])
        return ", ".join(deps) if isinstance(deps, list) else str(deps)
    if field == "source_id":
        return rec.get("source_id", "")
    if field == "target_id":
        return rec.get("target_id", "")
    if field == "dependency_type":
        return rec.get("dependency_type", "")
    if field == "is_separate":
        return str(rec.get("is_separate", ""))
    if field == "description":
        return rec.get("description", "")
    if field == "asset_type":
        return rec.get("asset_type", "")
    if field == "asset_id":
        return rec.get("asset_id", "")
    if field == "evidence_type":
        return rec.get("evidence_type", "")
    if field == "decision_id":
        return rec.get("decision_id", "")
    if field == "owner_decision_id":
        return rec.get("owner_decision_id", "")
    if field == "tool_name":
        return rec.get("tool_name", "")
    if field == "tool_type":
        return rec.get("tool_type", "")
    if field == "provenance_state":
        return rec.get("provenance_state", "")
    return ""


def _render_index(model: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("## Purpose of Project Memory")
    lines.append("")
    lines.append("Project Memory is a normalized, machine-readable, commit-bound system that records the accepted plan, compares it with actual implementation, explains discrepancies with evidence, and surfaces confidence and provenance for owner review.")
    lines.append("")
    lines.append("## Application Summary")
    lines.append("")
    proj_recs = model.get("projects", [])
    for proj in proj_recs:
        lines.append(f"- **{_sanitize_string(proj.get('title', ''))}** — {_sanitize_string(proj.get('description', ''))}")
    lines.append("")

    lines.append("## Active Application Frontier")
    lines.append("")
    lines.append(f"`PHASE8-IMPL-024-T003A` — Context-availability/readiness contract")
    lines.append("")

    lines.append("## Project Memory Workstream Status")
    lines.append("")
    tasks = model.get("tasks", [])
    task_by_id = {t.get("task_id", ""): t for t in tasks}
    missing = []
    for tid in _PM_TASK_DISPLAY_ORDER:
        if tid not in task_by_id:
            missing.append(tid)
    if missing:
        raise ValueError(f"Required PM task records missing from registry: {missing}")
    parent_rec = task_by_id.get(_PM_PARENT_TASK_ID)
    parent_label = _derive_task_display_status(parent_rec) if parent_rec else "unknown"
    lines.append("| Task | Status |")
    lines.append("|---|---|")
    lines.append(f"| {_sanitize_string(_PM_PARENT_TASK_ID)} (published/active) | {_sanitize_string(parent_label)} |")
    for tid in _PM_TASK_DISPLAY_ORDER:
        rec = task_by_id[tid]
        label = _PM_TASK_LABELS.get(tid, tid)
        display_status = _derive_task_display_status(rec)
        lines.append(f"| {_sanitize_string(label)} | {_sanitize_string(display_status)} |")
    lines.append("")

    lines.append("## PHASE8-IMPL-025 Status")
    lines.append("")
    lines.append("`published/planned` and **inactive**. The application frontier has not advanced. No agent, retrieval, or orchestration work has been activated.")
    lines.append("")

    lines.append("## Record Summary")
    lines.append("")
    lines.append("| Dimension | Counts |")
    lines.append("|---|---|")
    for rt, cnt in sorted(model.get("counts_by_type", {}).items()):
        lines.append(f"| {_sanitize_string(rt)} | {cnt} |")
    lines.append(f"| **Total records** | {model.get('total_records', 0)} |")
    lines.append("")

    lines.append("### By Authority Class")
    lines.append("")
    for ac, cnt in sorted(model.get("counts_by_authority", {}).items()):
        lines.append(f"- `{_sanitize_string(ac)}`: {cnt}")
    lines.append("")

    lines.append("### By Lifecycle")
    lines.append("")
    for st, cnt in sorted(model.get("counts_by_lifecycle", {}).items()):
        lines.append(f"- `{_sanitize_string(st)}`: {cnt}")
    lines.append("")

    find_count = len(model.get("findings", []))
    lines.append(f"## Convergence")
    lines.append(f"Findings: {find_count}")
    lines.append("")
    missing_count = len(model.get("missing_sources", set()))
    lines.append(f"**Unavailable sources:** {missing_count}")
    lines.append("")

    lines.append("## Navigation")
    lines.append("")
    for i, page in enumerate(RENDERED_PAGE_NAMES, 1):
        title = page.replace(".md", "").replace("-", " ").title()
        lines.append(f"{i}. [{title}]({page})")
    lines.append("")

    lines.append("## Authority vs. Generated Evidence")
    lines.append("")
    lines.append("Tracked registries under `docs/project-memory/registries/` carry accepted normalized records. Generated snapshots under `.codex-context/project-memory/` are `generated_evidence` — they report convergence findings without claiming authority. Rendered documentation is also `generated_evidence` and never becomes an additional tier in the authority hierarchy.")
    lines.append("")

    return "\n".join(lines)


def _render_application_overview(model: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("## Application Projects")
    lines.append("")
    proj_recs = _sort_records(model.get("projects", []))
    for proj in proj_recs:
        lines.append(f"### {_sanitize_string(proj.get('title', ''))}")
        lines.append("")
        lines.append(f"- **ID:** {_markdown_code(proj.get('id', ''))}")
        lines.append(f"- **Project ID:** {_sanitize_string(proj.get('project_id', ''))}")
        lines.append(f"- **Authority:** {_markdown_code(proj.get('authority_class', ''))}")
        lc = proj.get("lifecycle", {})
        lines.append(f"- **Lifecycle:** {_markdown_code(lc.get('status', ''))}")
        desc = proj.get("description", "")
        if desc:
            lines.append(f"- **Description:** {_sanitize_string(desc)}")
        notes = proj.get("notes", "")
        if notes:
            lines.append(f"- **Notes:** {_sanitize_string(notes)}")
        lines.append("")
        prov = proj.get("provenance", {})
        if isinstance(prov, dict):
            locators = prov.get("source_locators", [])
            if locators:
                lines.append("**Source references:**")
                for loc in locators:
                    lines.append(f"- {_markdown_code(loc.get('path', ''))}")
                lines.append("")
    return "\n".join(lines)


def _render_product_boundaries(model: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("## Non-Negotiable Product Boundaries")
    lines.append("")
    boundaries = _sort_records(model.get("boundaries", []))
    for b in boundaries:
        lines.append(f"### {_sanitize_string(b.get('title', ''))}")
        lines.append("")
        lines.append(f"- **ID:** {_markdown_code(b.get('id', ''))}")
        lines.append(f"- **Boundary ID:** {_sanitize_string(b.get('boundary_id', ''))}")
        lines.append(f"- **Category:** {_markdown_code(b.get('category', ''))}")
        lines.append(f"- **Non-negotiable:** {b.get('is_non_negotiable', False)}")
        lines.append(f"- **Authority:** {_markdown_code(b.get('authority_class', ''))}")
        lc = b.get("lifecycle", {})
        lines.append(f"- **Lifecycle:** {_markdown_code(lc.get('status', ''))}")
        desc = b.get("description", "")
        if desc:
            lines.append(f"- **Description:** {_sanitize_string(desc)}")
        notes = b.get("notes", "")
        if notes:
            lines.append(f"- **Notes:** {_sanitize_string(notes)}")
        lines.append("")
    return "\n".join(lines)


def _render_features(model: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("## Features")
    lines.append("")
    features = _sort_records(model.get("features", []))
    for feat in features:
        lines.append(f"### {_sanitize_string(feat.get('title', ''))}")
        lines.append("")
        lines.append(f"- **ID:** {_markdown_code(feat.get('id', ''))}")
        lines.append(f"- **Feature ID:** {_sanitize_string(feat.get('feature_id', ''))}")
        impl = feat.get("implementation_status", "")
        lines.append(f"- **Implementation status:** `{_sanitize_string(impl)}`")
        lines.append(f"- **Authority:** {_markdown_code(feat.get('authority_class', ''))}")
        lc = feat.get("lifecycle", {})
        lines.append(f"- **Lifecycle:** {_markdown_code(lc.get('status', ''))}")
        desc = feat.get("description", "")
        if desc:
            lines.append(f"- **Description:** {_sanitize_string(desc)}")
        parent = feat.get("parent_task_id", "")
        if parent:
            lines.append(f"- **Parent task:** {_markdown_code(parent)}")
        notes = feat.get("notes", "")
        if notes:
            lines.append(f"- **Notes:** {_sanitize_string(notes)}")
        lines.append("")
    return "\n".join(lines)


def _render_capabilities(model: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("## Capabilities")
    lines.append("")
    lines.append("A capability being represented in the registry does not imply it is active or validated.")
    lines.append("")
    capabilities = _sort_records(model.get("capabilities", []))
    for cap in capabilities:
        lines.append(f"### {_sanitize_string(cap.get('title', ''))}")
        lines.append("")
        lines.append(f"- **ID:** {_markdown_code(cap.get('id', ''))}")
        lines.append(f"- **Capability ID:** {_sanitize_string(cap.get('capability_id', ''))}")
        lines.append(f"- **Implemented:** {cap.get('implemented', False)}")
        lines.append(f"- **Validated:** {cap.get('validated', False)}")
        lines.append(f"- **Authority:** {_markdown_code(cap.get('authority_class', ''))}")
        lc = cap.get("lifecycle", {})
        lines.append(f"- **Lifecycle:** {_markdown_code(lc.get('status', ''))}")
        desc = cap.get("description", "")
        if desc:
            lines.append(f"- **Description:** {_sanitize_string(desc)}")
        assoc = cap.get("associated_tasks", [])
        if assoc:
            lines.append(f"- **Associated tasks:** {', '.join(_sanitize_string(t) for t in assoc)}")
        notes = cap.get("notes", "")
        if notes:
            lines.append(f"- **Notes:** {_sanitize_string(notes)}")
        lines.append("")
    return "\n".join(lines)


def _render_current_roadmap(model: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("## Roadmap Tasks")
    lines.append("")
    lines.append(f"**Active application parent:** PHASE8-IMPL-024")
    lines.append(f"**Immediate application frontier:** PHASE8-IMPL-024-T003A")
    lines.append(f"**Active Project Memory parent:** PHASE8-IMPL-026")
    tasks = model.get("tasks", [])
    pm_children = _get_children(tasks, _PM_PARENT_TASK_ID)
    pm_children = [c for c in pm_children if c.get("task_id", "").startswith(_PM_PARENT_TASK_ID + "-T")]
    completed_ids = {c["task_id"] for c in pm_children if c.get("lifecycle", {}).get("status") == "complete"}
    next_child = None
    for child in pm_children:
        if child["task_id"] not in completed_ids:
            next_child = child
            break
    if next_child:
        short_id = next_child["task_id"].replace(_PM_PARENT_TASK_ID + "-", "")
        next_status = next_child.get("lifecycle", {}).get("status", "")
        lines.append(f"**Next Project Memory task:** {short_id} ({next_status})")
    else:
        lines.append(f"**Next Project Memory task:** (all complete)")
    lines.append(f"**PHASE8-IMPL-025:** published/planned, inactive")
    lines.append("")

    tasks = _sort_records(model.get("tasks", []))
    for task in tasks:
        lines.append(f"### {_sanitize_string(task.get('title', ''))}")
        lines.append("")
        lines.append(f"- **ID:** {_markdown_code(task.get('id', ''))}")
        tid = task.get("task_id", "")
        lines.append(f"- **Task ID:** {_sanitize_string(tid)}")
        lines.append(f"- **Authority:** {_markdown_code(task.get('authority_class', ''))}")
        lc = task.get("lifecycle", {})
        lines.append(f"- **Lifecycle:** {_markdown_code(lc.get('status', ''))}")
        parent = task.get("parent_task_id", "")
        if parent:
            lines.append(f"- **Parent:** {_markdown_code(parent)}")
        deps = task.get("depends_on", [])
        if deps:
            lines.append(f"- **Depends on:** {', '.join(_markdown_code(d) for d in deps)}")
        task_type = task.get("task_type", "")
        if task_type:
            lines.append(f"- **Type:** {_markdown_code(task_type)}")
        is_frontier = task.get("is_application_frontier", False)
        if is_frontier:
            lines.append(f"- **Application frontier:** Yes")
        is_blocking = task.get("is_blocking", False)
        if is_blocking:
            lines.append(f"- **Blocking:** Yes")
        notes = task.get("notes", "")
        if notes:
            lines.append(f"- **Notes:** {_sanitize_string(notes)}")
        lines.append("")
    return "\n".join(lines)


def _render_remaining_work(model: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("## Remaining Work")
    lines.append("")
    lines.append("Only work that is not fully complete and validated is shown.")
    lines.append("")

    tasks = model.get("tasks", [])
    incomplete: list[dict[str, Any]] = []
    for task in tasks:
        lc = task.get("lifecycle", {})
        st = lc.get("status", "")
        if isinstance(lc, dict) and st not in ("complete", "superseded", "rejected"):
            incomplete.append(task)

    groups = _group_by_status(incomplete)
    ordered_groups = ["blocked", "in_progress", "planned", "owner_pending", "deferred", "unknown"]
    for group in ordered_groups:
        recs = groups.get(group, [])
        if not recs:
            continue
        lines.append(f"### {group.replace('_', ' ').title()}")
        lines.append("")
        for rec in sorted(recs, key=lambda r: r.get("id", "")):
            lines.append(f"- **{_sanitize_string(rec.get('title', ''))}** ({_markdown_code(rec.get('id', ''))}) — {_sanitize_string(rec.get('task_id', ''))}")
        lines.append("")

    if not incomplete:
        lines.append("_No remaining work._")
        lines.append("")

    return "\n".join(lines)


def _render_dependencies(model: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("## Dependencies")
    lines.append("")
    deps = _sort_records(model.get("dependencies", []))
    for dep in deps:
        lines.append(f"### {_sanitize_string(dep.get('title', ''))}")
        lines.append("")
        lines.append(f"- **ID:** {_markdown_code(dep.get('id', ''))}")
        lines.append(f"- **Source:** {_markdown_code(dep.get('source_id', ''))}")
        lines.append(f"- **Target:** {_markdown_code(dep.get('target_id', ''))}")
        lines.append(f"- **Type:** {_markdown_code(dep.get('dependency_type', ''))}")
        lines.append(f"- **Separate:** {dep.get('is_separate', False)}")
        lines.append(f"- **Authority:** {_markdown_code(dep.get('authority_class', ''))}")
        lc = dep.get("lifecycle", {})
        lines.append(f"- **Lifecycle:** {_markdown_code(lc.get('status', ''))}")
        notes = dep.get("notes", "")
        if notes:
            lines.append(f"- **Notes:** {_sanitize_string(notes)}")
        lines.append("")
    if not deps:
        lines.append("_No dependency records._")
        lines.append("")
    return "\n".join(lines)


def _render_decisions(model: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("## Accepted Decisions")
    lines.append("")
    decisions = _sort_records(model.get("decisions", []))
    for d in decisions:
        lines.append(f"### {_sanitize_string(d.get('title', ''))}")
        lines.append("")
        lines.append(f"- **ID:** {_markdown_code(d.get('id', ''))}")
        lines.append(f"- **Decision ID:** {_sanitize_string(d.get('decision_id', ''))}")
        lines.append(f"- **Authority:** {_markdown_code(d.get('authority_class', ''))}")
        lc = d.get("lifecycle", {})
        lines.append(f"- **Lifecycle:** {_markdown_code(lc.get('status', ''))}")
        question = d.get("question", "")
        if question:
            lines.append(f"- **Question:** {_sanitize_string(question)}")
        option = d.get("selected_option", "")
        if option:
            lines.append(f"- **Selected:** {_sanitize_string(option)}")
        rationale = d.get("rationale", "")
        if rationale:
            lines.append(f"- **Rationale:** {_sanitize_string(rationale)}")
        affected = d.get("affected_tasks", [])
        if affected:
            lines.append(f"- **Affected tasks:** {', '.join(_sanitize_string(t) for t in affected)}")
        notes = d.get("notes", "")
        if notes:
            lines.append(f"- **Notes:** {_sanitize_string(notes)}")
        lines.append("")

    owner_decisions = _sort_records(model.get("owner_decisions", []))
    if owner_decisions:
        lines.append("## Owner Decisions")
        lines.append("")
        for od in owner_decisions:
            lines.append(f"### {_sanitize_string(od.get('title', ''))}")
            lines.append("")
            lines.append(f"- **ID:** {_markdown_code(od.get('id', ''))}")
            lines.append(f"- **Decision ID:** {_sanitize_string(od.get('owner_decision_id', ''))}")
            lines.append(f"- **Authority:** {_markdown_code(od.get('authority_class', ''))}")
            lc = od.get("lifecycle", {})
            lines.append(f"- **Lifecycle:** {_markdown_code(lc.get('status', ''))}")
            question = od.get("question", "")
            if question:
                lines.append(f"- **Question:** {_sanitize_string(question)}")
            option = od.get("selected_option", "")
            if option:
                lines.append(f"- **Selected:** {_sanitize_string(option)}")
            rationale = od.get("rationale", "")
            if rationale:
                lines.append(f"- **Rationale:** {_sanitize_string(rationale)}")
            notes = od.get("notes", "")
            if notes:
                lines.append(f"- **Notes:** {_sanitize_string(notes)}")
            lines.append("")

    if not decisions and not owner_decisions:
        lines.append("_No decision records._")
        lines.append("")

    return "\n".join(lines)


def _render_assets(model: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("## Tracked Assets")
    lines.append("")
    assets = _sort_records(model.get("assets", []))
    for a in assets:
        lines.append(f"### {_sanitize_string(a.get('title', ''))}")
        lines.append("")
        lines.append(f"- **ID:** {_markdown_code(a.get('id', ''))}")
        lines.append(f"- **Asset ID:** {_sanitize_string(a.get('asset_id', ''))}")
        lines.append(f"- **Asset type:** {_markdown_code(a.get('asset_type', ''))}")
        afp = a.get("asset_path", "")
        if afp:
            lines.append(f"- **Path:** {_markdown_code(afp)}")
        lines.append(f"- **Durable fixture:** {a.get('is_durable_fixture', False)}")
        lines.append(f"- **Authority:** {_markdown_code(a.get('authority_class', ''))}")
        lc = a.get("lifecycle", {})
        lines.append(f"- **Lifecycle:** {_markdown_code(lc.get('status', ''))}")
        role = a.get("role", "")
        if role:
            lines.append(f"- **Role:** {_sanitize_string(role)}")
        desc = a.get("description", "")
        if desc:
            lines.append(f"- **Description:** {_sanitize_string(desc)}")
        warnings = a.get("warnings", [])
        if warnings:
            lines.append(f"- **Warnings:** {', '.join(_sanitize_string(w) for w in warnings)}")
        notes = a.get("notes", "")
        if notes:
            lines.append(f"- **Notes:** {_sanitize_string(notes)}")
        lines.append("")
    if not assets:
        lines.append("_No asset records._")
        lines.append("")
    return "\n".join(lines)


def _render_evidence(model: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("## Evidence Records")
    lines.append("")
    evidence = _sort_records(model.get("evidence", []))
    for ev in evidence:
        lines.append(f"### {_sanitize_string(ev.get('title', ''))}")
        lines.append("")
        lines.append(f"- **ID:** {_markdown_code(ev.get('id', ''))}")
        lines.append(f"- **Evidence ID:** {_sanitize_string(ev.get('evidence_id', ''))}")
        lines.append(f"- **Type:** {_markdown_code(ev.get('evidence_type', ''))}")
        lines.append(f"- **Authority:** {_markdown_code(ev.get('authority_class', ''))}")
        lc = ev.get("lifecycle", {})
        lines.append(f"- **Lifecycle:** {_markdown_code(lc.get('status', ''))}")
        desc = ev.get("description", "")
        if desc:
            lines.append(f"- **Description:** {_sanitize_string(desc)}")
        assoc_task = ev.get("associated_task_id", "")
        if assoc_task:
            lines.append(f"- **Associated task:** {_sanitize_string(assoc_task)}")
        binding = ev.get("bound_commit", "")
        if binding:
            lines.append(f"- **Bound commit:** {_markdown_code(binding)}")
        is_defect = ev.get("is_blocking_defect", False)
        if is_defect:
            lines.append(f"- **Blocking defect:** Yes")
        notes = ev.get("notes", "")
        if notes:
            lines.append(f"- **Notes:** {_sanitize_string(notes)}")
        lines.append("")
    if not evidence:
        lines.append("_No evidence records._")
        lines.append("")
    return "\n".join(lines)


def _render_risks_and_open_questions(model: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("## Risks and Open Questions")
    lines.append("")
    lines.append("### Active Risks")
    lines.append("")
    lines.append("- **Stale memory:** Remains active — requires future operational automation.")
    lines.append("- **Branch synchronization inconsistency:** Remains active — partial branch synchronization awaits future operational work.")
    lines.append("- **Prompt injection in future retrieval:** Remains active — repository content is data, trust-aware retrieval remains future.")
    lines.append("- **Competing renderer authority:** Mitigated by fixed `generated_evidence` classification and banners.")
    lines.append("- **Hidden missing evidence:** Mitigated by mandatory unavailable-source presentation.")
    lines.append("- **Stale rendering:** Mitigated by strict publication rejection and historical-preview labeling.")
    lines.append("- **Markdown injection:** Mitigated by renderer-owned templates and escaping.")
    lines.append("- **Nondeterministic documentation:** Mitigated by fixed inputs, ordering, timestamps, and hash validation.")
    lines.append("- **Partial output:** Mitigated by atomic build.")
    lines.append("")
    lines.append("### Open Questions")
    lines.append("")
    lines.append("- **Q151** — Full Plan Integrity classification model (open)")
    lines.append("- **Q152** — Serena adoption criteria (open)")
    lines.append("- **Q153** — Embedding-model selection (open)")
    lines.append("- **Q154** — Operational synchronization cadence (open)")
    lines.append("")
    return "\n".join(lines)


def _render_convergence_findings(model: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("## Convergence Findings")
    lines.append("")
    findings = model.get("findings", [])
    lines.append(f"**Total findings:** {len(findings)}")
    lines.append("")
    codes = model.get("finding_by_code", {})
    if codes:
        lines.append("### By Code")
        lines.append("")
        for code, cnt in sorted(codes.items()):
            lines.append(f"- `{_sanitize_string(code)}`: {cnt}")
        lines.append("")
    sevs = model.get("finding_by_severity", {})
    if sevs:
        lines.append("### By Severity")
        lines.append("")
        for sev, cnt in sorted(sevs.items()):
            lines.append(f"- `{_sanitize_string(sev)}`: {cnt}")
        lines.append("")

    for f in findings:
        lines.append(f"### {_sanitize_string(f.get('title', ''))}")
        lines.append("")
        lines.append(f"- **Finding ID:** `{_sanitize_string(f.get('finding_id', ''))}`")
        lines.append(f"- **Code:** `{_sanitize_string(f.get('code', ''))}`")
        lines.append(f"- **Severity:** `{_sanitize_string(f.get('severity', ''))}`")
        lines.append(f"- **Blocks publication:** {f.get('blocks_publication', False)}")
        lines.append(f"- **Owner review required:** {f.get('owner_review_required', False)}")
        lines.append(f"- **Explanation:** {_sanitize_string(f.get('explanation', ''))}")
        affected = f.get("affected_record_ids", [])
        if affected:
            lines.append(f"- **Affected records:** {', '.join(_markdown_code(r) for r in affected)}")
        slocs = f.get("source_locators", [])
        if slocs:
            lines.append(f"- **Source locators:** {', '.join(_markdown_code(s) for s in slocs)}")
        auth = f.get("authority_context", "")
        if auth:
            lines.append(f"- **Authority context:** `{_sanitize_string(auth)}`")
        evidence = f.get("evidence", {})
        if evidence:
            lines.append(f"- **Evidence:** {_sanitize_string(json.dumps(evidence, sort_keys=True))}")
        action = f.get("suggested_action", "")
        if action:
            lines.append(f"- **Suggested action:** {_sanitize_string(action)}")
        lines.append("")
    if not findings:
        lines.append("_No convergence findings._")
        lines.append("")
    return "\n".join(lines)


def _render_technical_annex(
    model: dict[str, Any],
    command: str,
    input_package: str,
    snapshot_task_id: str,
    snapshot_run_id: str,
    registry_hashes: dict[str, str],
    source_hashes: dict[str, str],
    page_hashes: dict[str, str],
    page_count: int,
    mode: str,
) -> str:
    lines: list[str] = []
    lines.append("## Technical Annex")
    lines.append("")
    lines.append("### Renderer Identity")
    lines.append("")
    lines.append(f"- **Name:** `{RENDERER_NAME}`")
    lines.append(f"- **Version:** `{RENDERER_VERSION}`")
    lines.append(f"- **Schema version:** `{SCHEMA_VERSION}`")
    lines.append(f"- **Architecture version:** `{ARCHITECTURE_VERSION}`")
    lines.append("")

    lines.append("### Command")
    lines.append("")
    lines.append(f"```text\n{command}\n```")
    lines.append("")

    lines.append("### Input Package")
    lines.append("")
    lines.append(f"- **Snapshot identity:** `{snapshot_task_id}/{snapshot_run_id}`")
    lines.append(f"- **Snapshot directory:** `{input_package}`")
    lines.append("")

    lines.append("### Registry Hashes")
    lines.append("")
    if registry_hashes:
        for path, h in sorted(registry_hashes.items()):
            lines.append(f"- `{_sanitize_string(path)}`: `{h}`")
    lines.append("")

    lines.append("### Source Snapshot Hashes")
    lines.append("")
    if source_hashes:
        for path, h in sorted(source_hashes.items())[:30]:
            lines.append(f"- `{_sanitize_string(path)}`: `{h}`")
        if len(source_hashes) > 30:
            lines.append(f"- _... and {len(source_hashes) - 30} more_")
    lines.append("")

    lines.append("### Page List and Hashes")
    lines.append("")
    for page in RENDERED_PAGE_NAMES:
        h = page_hashes.get(page, "")
        lines.append(f"- `{page}`: `{h}`")
    lines.append("")

    lines.append("### Authority Hierarchy")
    lines.append("")
    lines.append("1. Accepted roadmap and decision records")
    lines.append("2. Live code and schemas")
    lines.append("3. Automated tests")
    lines.append("4. Accepted manual validation")
    lines.append("5. Exact Git history")
    lines.append("6. Normalized Project Memory registries")
    lines.append("7. Generated context and evidence")
    lines.append("")

    lines.append("### Trust Classes")
    lines.append("")
    for tc in sorted(_TRUST_CLASSES):
        lines.append(f"- `{tc}`")
    lines.append("")

    lines.append("### Lifecycle Vocabulary")
    lines.append("")
    for st in sorted(_LIFECYCLE_STATUSES):
        lines.append(f"- `{st}`")
    lines.append("")

    lines.append("### Exclusions and Limitations")
    lines.append("")
    lines.append("- No network access during rendering")
    lines.append("- No model, AI, or embedding service used")
    lines.append("- No external tools or dependencies beyond Python standard library")
    lines.append("- No Git history scanning beyond read-only commands")
    lines.append("- No MkDocs or site generation")
    lines.append("- No registry, schema, scanner, or snapshot mutation")
    lines.append("- Output is generated evidence, never authoritative")
    lines.append("")

    lines.append("### Determinism Rules")
    lines.append("")
    lines.append("- UTF-8 encoding with LF line endings")
    lines.append("- Sorted JSON keys with stable indentation")
    lines.append("- Stable record sorting by type and ID")
    lines.append("- Fixed 14-page navigation order")
    lines.append("- No random identifiers or locale-dependent formatting")
    lines.append("- Explicit timestamps, no current-clock reads")
    lines.append("- Identical inputs produce byte-identical output")
    lines.append("")

    return "\n".join(lines)


def render_page_set(
    model: dict[str, Any],
    banner: str,
    mode: str,
    command: str,
    input_package: str,
    snapshot_task_id: str,
    snapshot_run_id: str,
    registry_hashes: dict[str, str],
    source_hashes: dict[str, str],
) -> tuple[dict[str, str], dict[str, str]]:
    """Render all 14 pages. Returns (pages, page_hashes)."""
    pages: dict[str, str] = {}
    page_hashes: dict[str, str] = {}

    renderers: list[tuple[str, callable]] = [
        ("index.md", lambda m: _render_index(m)),
        ("application-overview.md", lambda m: _render_application_overview(m)),
        ("product-boundaries.md", lambda m: _render_product_boundaries(m)),
        ("features.md", lambda m: _render_features(m)),
        ("capabilities.md", lambda m: _render_capabilities(m)),
        ("current-roadmap.md", lambda m: _render_current_roadmap(m)),
        ("remaining-work.md", lambda m: _render_remaining_work(m)),
        ("dependencies.md", lambda m: _render_dependencies(m)),
        ("decisions.md", lambda m: _render_decisions(m)),
        ("assets.md", lambda m: _render_assets(m)),
        ("evidence.md", lambda m: _render_evidence(m)),
        ("risks-and-open-questions.md", lambda m: _render_risks_and_open_questions(m)),
        ("convergence-findings.md", lambda m: _render_convergence_findings(m)),
        ("technical-annex.md", lambda m: _render_technical_annex(
            m, command, input_package, snapshot_task_id, snapshot_run_id,
            registry_hashes, source_hashes, page_hashes, 14, mode,
        )),
    ]

    for page_name, render_fn in renderers:
        body = render_fn(model)
        full_page = banner + "\n" + body
        full_page = full_page.rstrip("\n") + "\n"
        pages[page_name] = full_page
        page_hashes[page_name] = hashlib.sha256(full_page.encode("utf-8")).hexdigest()

    return pages, page_hashes


def build_manifest(
    mode: str,
    task_id: str,
    run_id: str,
    generated_at: str,
    command: str,
    repo_root_path: str,
    target_branch: str,
    target_commit: str,
    snapshot_task_id: str,
    snapshot_run_id: str,
    snapshot_branch: str,
    bound_commit: str,
    snapshot_generated_at: str,
    conv_result: str,
    findings: list[dict[str, Any]],
    freshness: str,
    publication_eligible: bool,
    page_hashes: dict[str, str],
    registry_hashes: dict[str, str],
    source_hashes: dict[str, str],
    missing_source_count: int,
    warnings: list[str],
) -> dict[str, Any]:
    finding_by_code: dict[str, int] = {}
    finding_by_severity: dict[str, int] = {}
    for f in findings:
        code = f.get("code", "unknown")
        sev = f.get("severity", "unknown")
        finding_by_code[code] = finding_by_code.get(code, 0) + 1
        finding_by_severity[sev] = finding_by_severity.get(sev, 0) + 1

    manifest: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "architecture_version": ARCHITECTURE_VERSION,
        "renderer_name": RENDERER_NAME,
        "renderer_version": RENDERER_VERSION,
        "authority_class": "generated_evidence",
        "mode": mode,
        "task_id": task_id,
        "run_id": run_id,
        "generated_at": generated_at,
        "command": command,
        "repository_root": repo_root_path,
        "target_branch": target_branch,
        "target_commit": target_commit,
        "source_snapshot_task_id": snapshot_task_id,
        "source_snapshot_run_id": snapshot_run_id,
        "source_snapshot_branch": snapshot_branch,
        "source_snapshot_bound_commit": bound_commit,
        "source_snapshot_generated_at": snapshot_generated_at,
        "convergence_result": conv_result,
        "finding_counts_by_code": finding_by_code,
        "finding_counts_by_severity": finding_by_severity,
        "unavailable_source_count": missing_source_count,
        "freshness": freshness,
        "publication_eligible": publication_eligible,
        "page_count": len(RENDERED_PAGE_NAMES),
        "page_navigation_order": list(RENDERED_PAGE_NAMES),
        "page_hashes": page_hashes,
        "registry_hashes": registry_hashes,
        "exclusions": [
            "No MkDocs generation",
            "No network access",
            "No model/AI usage",
            "No external tools",
            "No registry/schema/scanner mutation",
        ],
        "warnings": warnings,
        "known_limitations": [
            "This is generated evidence, not project authority.",
            "Stale memory detection requires future operational automation.",
            "Branch synchronization remains future operational work.",
            "Rendered output never becomes an additional authority tier.",
        ],
        "no_network": True,
        "no_model": True,
        "no_external_tool": True,
    }
    return manifest


def build_source_snapshot_record(
    snapshot_task_id: str,
    snapshot_run_id: str,
    bound_commit: str,
    snapshot_branch: str,
    snapshot_generated_at: str,
    conv_result: str,
    freshness: str,
    publication_eligible: bool,
    target_commit: str,
    target_branch: str,
    registry_hashes: dict[str, str],
    source_hashes: dict[str, str],
    findings_summary: dict[str, Any],
    missing_source_count: int,
    snapshot_package_hashes: dict[str, str],
) -> dict[str, Any]:
    return {
        "source_snapshot_identity": f"{snapshot_task_id}/{snapshot_run_id}",
        "bound_commit": bound_commit,
        "branch": snapshot_branch,
        "task_id": snapshot_task_id,
        "run_id": snapshot_run_id,
        "generated_at": snapshot_generated_at,
        "authority_class": "generated_evidence",
        "publication_eligible": publication_eligible,
        "convergence_result": conv_result,
        "freshness_classification": freshness,
        "target_commit": target_commit,
        "target_branch": target_branch,
        "registry_file_hashes": registry_hashes,
        "source_hashes": source_hashes,
        "findings_summary": findings_summary,
        "unavailable_source_count": missing_source_count,
        "limitations": [
            "Snapshot represents state at bound_commit, not current HEAD.",
            "Generated evidence, not authoritative.",
        ],
    }


def render(
    repo_root: str,
    snapshot_dir: str,
    output_root: str,
    task_id: str,
    run_id: str,
    generated_at: str,
    mode: str,
) -> dict[str, Any]:
    """Main render function. Validates inputs, renders pages, writes atomic output.

    Returns a summary dict.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    if mode not in VALID_MODES:
        raise ValueError(f"Invalid mode: {mode!r}. Must be one of {sorted(VALID_MODES)}")

    warnings: list[str] = []
    command = (
        f"python3 scripts/project_memory/render_docs.py "
        f"--repo-root {repo_root} --snapshot-dir {snapshot_dir} "
        f"--output-root {output_root} --task-id {task_id} --run-id {run_id} "
        f"--generated-at {generated_at} --mode {mode}"
    )

    root = _resolve_repo_root(repo_root)
    output_path = Path(output_root)
    if not output_path.is_absolute():
        output_path = (root / output_root).resolve()
    else:
        output_path = output_path.resolve()

    if output_path == root:
        raise ValueError("Output root must not be the repository root")

    for prot in _PROTECTED_AUTHORITY_DIRS:
        prot_path = (root / prot).resolve()
        try:
            if output_path.is_relative_to(prot_path) or output_path == prot_path:
                raise ValueError(f"Output must not be inside protected authority dir: {prot}")
        except AttributeError:
            try:
                output_path.relative_to(prot_path)
                raise ValueError(f"Output must not be inside protected authority dir: {prot}")
            except ValueError:
                pass

    pub_root = (root / _PUBLICATION_ROOT).resolve()
    if mode == "publication":
        try:
            if not output_path.is_relative_to(pub_root):
                raise ValueError(f"Publication mode requires output under {_PUBLICATION_ROOT}")
        except AttributeError:
            try:
                output_path.relative_to(pub_root)
            except ValueError:
                raise ValueError(f"Publication mode requires output under {_PUBLICATION_ROOT}")
    else:
        try:
            if output_path.is_relative_to(pub_root):
                raise ValueError("Historical-preview mode must not output under publication root")
        except AttributeError:
            try:
                output_path.relative_to(pub_root)
                raise ValueError("Historical-preview mode must not output under publication root")
            except ValueError:
                pass

    import scripts.project_memory.validate_registries as vr_mod
    registries_dir = root / "docs" / "project-memory" / "registries"
    findings = vr_mod.validate(registries_dir)
    errors = [f for f in findings if f.get("level") == "error"]
    if errors:
        raise ValueError(f"Registry validation failed with {len(errors)} errors")

    manifest = json.loads((registries_dir / "manifest.json").read_text(encoding="utf-8"))
    sv = manifest.get("schema_version")
    if sv != SCHEMA_VERSION:
        raise ValueError(f"Unsupported schema version: {sv}")
    av = manifest.get("architecture_version")
    if av != ARCHITECTURE_VERSION:
        raise ValueError(f"Unsupported architecture version: {av}")

    registries: dict[str, dict[str, Any]] = {}
    registry_hashes: dict[str, str] = {}
    for decl in manifest.get("registries", []):
        fn = decl.get("filename", "")
        if fn == "manifest.json":
            continue
        reg_path = registries_dir / fn
        if not reg_path.is_file():
            raise ValueError(f"Registry file not found: {fn}")
        data = json.loads(reg_path.read_text(encoding="utf-8"))
        registries[fn] = data
        registry_hashes[fn] = _compute_sha256(reg_path)

    snap_bundle = validate_snapshot_package(snapshot_dir, root)
    snapshot = snap_bundle["snapshot"]
    bound_commit = snap_bundle["bound_commit"]
    snapshot_branch = snap_bundle["snapshot_branch"]
    snapshot_task_id = snap_bundle["snapshot_task_id"]
    snapshot_run_id = snap_bundle["snapshot_run_id"]
    snapshot_generated_at = snap_bundle["snapshot_generated_at"]
    publication_eligible = snap_bundle["publication_eligible"]
    conv_result = snap_bundle["conv_result"]
    findings_list = snap_bundle["findings"]
    source_inventory = snap_bundle["source_inventory"]
    source_hashes_data = snap_bundle["source_hashes"]

    target_branch = _run_git(["rev-parse", "--abbrev-ref", "HEAD"], root)
    target_commit = _run_git(["rev-parse", "HEAD"], root)

    staged_raw = _run_git(["diff", "--cached", "--stat"], root)
    staged = bool(staged_raw.strip())
    dirty_raw = _run_git(["diff", "--stat"], root)
    dirty = bool(dirty_raw.strip())

    if mode == "publication":
        if dirty:
            raise ValueError("Publication mode requires a clean worktree")
        if staged:
            raise ValueError("Publication mode requires an empty staging area")
        if not publication_eligible:
            raise ValueError("Selected snapshot is not publication eligible")
        if conv_result == "BLOCKED":
            raise ValueError("Cannot render a BLOCKED convergence snapshot")
        for f in findings_list:
            sev = f.get("severity", "")
            if sev == "critical":
                raise ValueError(f"Critical finding in snapshot: {f.get('code', '')}")
            if f.get("blocks_publication"):
                raise ValueError(f"Publication-blocking finding in snapshot: {f.get('code', '')}")
        if snapshot_branch != target_branch:
            raise ValueError(
                f"Snapshot branch '{snapshot_branch}' != target branch '{target_branch}'"
            )
        if bound_commit != target_commit:
            raise ValueError(
                f"Snapshot bound_commit '{bound_commit[:12]}...' != target HEAD '{target_commit[:12]}...'"
            )
    else:
        if publication_eligible and bound_commit == target_commit and snapshot_branch == target_branch:
            pass

    freshness = classify_freshness(bound_commit, snapshot_branch, target_commit, target_branch, mode)

    missing_set: set[str] = set()
    for f in findings_list:
        if f.get("code") == "source_missing":
            slocs = f.get("source_locators", [])
            for sloc in slocs:
                if sloc:
                    missing_set.add(sloc)

    model = _build_page_model(
        registries, manifest, findings_list,
        source_inventory, source_hashes_data, missing_set,
    )

    missing_source_count = len(missing_set)

    banner = _render_banner(
        mode=mode,
        freshness=freshness,
        snapshot_task_id=snapshot_task_id,
        snapshot_run_id=snapshot_run_id,
        snapshot_branch=snapshot_branch,
        bound_commit=bound_commit,
        target_branch=target_branch,
        target_commit=target_commit,
        generated_at=generated_at,
        convergence_result=conv_result,
        publication_eligible=publication_eligible,
        missing_source_count=missing_source_count,
    )

    pages, page_hashes = render_page_set(
        model=model,
        banner=banner,
        mode=mode,
        command=command,
        input_package=snapshot_dir,
        snapshot_task_id=snapshot_task_id,
        snapshot_run_id=snapshot_run_id,
        registry_hashes=registry_hashes,
        source_hashes=source_inventory.get("source_hashes", {}),
    )

    snapshot_package_hashes: dict[str, str] = {}
    for fn in sorted(_SNAPSHOT_REQUIRED_FILES - {"SHA256SUMS"}):
        fpath = Path(snapshot_dir) / fn
        if fpath.is_file():
            snapshot_package_hashes[fn] = _compute_sha256(fpath)

    manifest_data = build_manifest(
        mode=mode,
        task_id=task_id,
        run_id=run_id,
        generated_at=generated_at,
        command=command,
        repo_root_path=str(root),
        target_branch=target_branch,
        target_commit=target_commit,
        snapshot_task_id=snapshot_task_id,
        snapshot_run_id=snapshot_run_id,
        snapshot_branch=snapshot_branch,
        bound_commit=bound_commit,
        snapshot_generated_at=snapshot_generated_at,
        conv_result=conv_result,
        findings=findings_list,
        freshness=freshness,
        publication_eligible=publication_eligible,
        page_hashes=page_hashes,
        registry_hashes=registry_hashes,
        source_hashes=source_inventory.get("source_hashes", {}),
        missing_source_count=missing_source_count,
        warnings=warnings,
    )

    findings_summary = {
        "total": len(findings_list),
        "by_code": {},
        "by_severity": {},
    }
    for f in findings_list:
        c = f.get("code", "unknown")
        s = f.get("severity", "unknown")
        findings_summary["by_code"][c] = findings_summary["by_code"].get(c, 0) + 1
        findings_summary["by_severity"][s] = findings_summary["by_severity"].get(s, 0) + 1

    source_snapshot_data = build_source_snapshot_record(
        snapshot_task_id=snapshot_task_id,
        snapshot_run_id=snapshot_run_id,
        bound_commit=bound_commit,
        snapshot_branch=snapshot_branch,
        snapshot_generated_at=snapshot_generated_at,
        conv_result=conv_result,
        freshness=freshness,
        publication_eligible=publication_eligible,
        target_commit=target_commit,
        target_branch=target_branch,
        registry_hashes=registry_hashes,
        source_hashes=source_inventory.get("source_hashes", {}),
        findings_summary=findings_summary,
        missing_source_count=missing_source_count,
        snapshot_package_hashes=snapshot_package_hashes,
    )

    run_dir = output_path / task_id / run_id
    if run_dir.exists():
        raise FileExistsError(f"Run directory already exists: {run_dir}")

    tmp_dir = Path(tempfile.mkdtemp(prefix=f"render_{task_id}_", dir=output_path.parent if output_path.parent.exists() else None))

    try:
        tmp_run_dir = tmp_dir / task_id / run_id
        docs_dir = tmp_run_dir / "docs"
        docs_dir.mkdir(parents=True, exist_ok=True)

        for page_name in RENDERED_PAGE_NAMES:
            (docs_dir / page_name).write_text(pages[page_name], encoding="utf-8")

        _write_json(tmp_run_dir / "build-manifest.json", manifest_data)
        _write_json(tmp_run_dir / "source-snapshot.json", source_snapshot_data)

        build_hash = {page_name: _compute_sha256(docs_dir / page_name) for page_name in RENDERED_PAGE_NAMES}
        build_hash["build-manifest.json"] = _compute_sha256(tmp_run_dir / "build-manifest.json")
        build_hash["source-snapshot.json"] = _compute_sha256(tmp_run_dir / "source-snapshot.json")

        file_list = sorted(
            [f"docs/{p}" for p in RENDERED_PAGE_NAMES]
            + ["build-manifest.json", "source-snapshot.json",
               "FILE-INVENTORY.txt", "SHA256SUMS"]
        )

        inventory_path = tmp_run_dir / "FILE-INVENTORY.txt"
        inventory_path.write_text("\n".join(file_list) + "\n", encoding="utf-8")

        sha256_lines = []
        for fn in sorted(tmp_run_dir.iterdir()):
            if fn.name == "SHA256SUMS":
                continue
            if fn.is_file():
                h = _compute_sha256(fn)
                sha256_lines.append(f"{h}  {fn.name}")
            elif fn.is_dir() and fn.name == "docs":
                for df in sorted(fn.iterdir()):
                    if df.is_file():
                        h = _compute_sha256(df)
                        sha256_lines.append(f"{h}  docs/{df.name}")
        (tmp_run_dir / "SHA256SUMS").write_text("\n".join(sorted(sha256_lines)) + "\n", encoding="utf-8")

        for fpath in [docs_dir / p for p in RENDERED_PAGE_NAMES] + [
            tmp_run_dir / "build-manifest.json",
            tmp_run_dir / "source-snapshot.json",
            tmp_run_dir / "FILE-INVENTORY.txt",
            tmp_run_dir / "SHA256SUMS",
        ]:
            if not fpath.exists():
                raise RuntimeError(f"Missing output file: {fpath}")

        from scripts.project_memory.validate_rendered_docs import (
            validate_rendered_package,
            RESULT_BLOCKED,
        )
        sem_result = validate_rendered_package(
            repo_root=repo_root,
            snapshot_dir=snapshot_dir,
            render_dir=str(tmp_run_dir),
            registries=registries,
            snapshot_bundle=snap_bundle,
            expected_task_states=None,
        )
        if sem_result.get("result") == RESULT_BLOCKED:
            raise ValueError(
                "Semantic publication validation BLOCKED: rendered task state "
                "contradicts normalized task records. "
                + "; ".join(sem_result.get("errors", [])[:3])
            )

        output_path.mkdir(parents=True, exist_ok=True)
        task_dir = output_path / task_id
        task_dir.mkdir(parents=True, exist_ok=True)

        os.rename(str(tmp_run_dir), str(run_dir))

        try:
            shutil.rmtree(str(tmp_dir))
        except Exception:
            pass

        errs = []
        finding_by_severity: dict[str, int] = {}
        finding_by_code: dict[str, int] = {}
        for f in findings_list:
            c = f.get("code", "unknown")
            s = f.get("severity", "unknown")
            finding_by_code[c] = finding_by_code.get(c, 0) + 1
            finding_by_severity[s] = finding_by_severity.get(s, 0) + 1

        return {
            "result": "PASS",
            "renderer_name": RENDERER_NAME,
            "renderer_version": RENDERER_VERSION,
            "mode": mode,
            "output_directory": str(run_dir),
            "task_id": task_id,
            "run_id": run_id,
            "target_commit": target_commit,
            "source_snapshot_bound_commit": bound_commit,
            "freshness": freshness,
            "publication_eligible": publication_eligible,
            "convergence_result": conv_result,
            "page_count": len(RENDERED_PAGE_NAMES),
            "finding_counts_by_code": finding_by_code,
            "finding_counts_by_severity": finding_by_severity,
            "errors": errs,
            "warnings": warnings,
        }

    except Exception:
        try:
            shutil.rmtree(str(tmp_dir))
        except Exception:
            pass
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic Markdown renderer for Project Memory.")
    parser.add_argument("--repo-root", required=True, help="Path to repository root.")
    parser.add_argument("--snapshot-dir", required=True, help="Path to snapshot package directory.")
    parser.add_argument("--output-root", required=True, help="Path to output root directory.")
    parser.add_argument("--task-id", required=True, help="Render task ID.")
    parser.add_argument("--run-id", required=True, help="Render run ID.")
    parser.add_argument("--generated-at", required=True, help="ISO 8601 timestamp.")
    parser.add_argument("--mode", required=True, choices=sorted(VALID_MODES), help="Render mode.")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON.")
    args = parser.parse_args()

    try:
        result = render(
            repo_root=args.repo_root,
            snapshot_dir=args.snapshot_dir,
            output_root=args.output_root,
            task_id=args.task_id,
            run_id=args.run_id,
            generated_at=args.generated_at,
            mode=args.mode,
        )
    except Exception as exc:
        if args.json:
            print(json.dumps({"result": "FAIL", "error": str(exc), "renderer_name": RENDERER_NAME, "renderer_version": RENDERER_VERSION}, indent=2, sort_keys=True))
        else:
            print(f"ERROR: {exc}")
        return 1

    if args.json:
        output = {**result, "renderer_name": RENDERER_NAME, "renderer_version": RENDERER_VERSION}
        print(json.dumps(output, indent=2, sort_keys=True))
        return 0

    print(f"Rendered: {result['output_directory']}")
    print(f"Result: {result['result']}")
    print(f"Pages: {result['page_count']}")
    print(f"Mode: {result['mode']}")
    print(f"Freshness: {result['freshness']}")
    print(f"Publication eligible: {result['publication_eligible']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
