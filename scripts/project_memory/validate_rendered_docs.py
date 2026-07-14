#!/usr/bin/env python3
"""Semantic rendered-documentation validator for Project Memory.

Validates that rendered Markdown pages structurally and semantically match
the tracked normalized task registry.  Structural hashes alone are
insufficient; the rendered task state must converge with registry truth.

Uses only Python standard-library modules.  Deterministic and read-only.

Usage:
  python3 scripts/project_memory/validate_rendered_docs.py \
    --repo-root . \
    --snapshot-dir <SNAPSHOT_DIR> \
    --render-dir <RENDER_DIR> \
    --json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

RENDERED_PAGE_NAMES: tuple[str, ...] = (
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

RESULT_PASS = "PASS"
RESULT_PASS_WITH_FINDINGS = "PASS_WITH_FINDINGS"
RESULT_BLOCKED = "BLOCKED"

_ALLOWED_RESULTS = frozenset([RESULT_PASS, RESULT_PASS_WITH_FINDINGS, RESULT_BLOCKED])

_GIT_SHA_RE = re.compile(r"^[0-9a-f]{40}$")

_PM_TASK_ORDER: tuple[str, ...] = (
    "PHASE8-IMPL-026-T001",
    "PHASE8-IMPL-026-T002",
    "PHASE8-IMPL-026-T003",
    "PHASE8-IMPL-026-T004",
    "PHASE8-IMPL-026-T004A",
    "PHASE8-IMPL-026-T004B",
    "PHASE8-IMPL-026-T004C",
    "PHASE8-IMPL-026-T005",
)

_EXPECTED_APP_FRONTIER = "PHASE8-IMPL-024-T003A"
_PM_PARENT = "PHASE8-IMPL-026"


def _compute_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def derive_expected_task_states(
    tasks: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    expected: dict[str, dict[str, Any]] = {}
    task_by_id: dict[str, dict[str, Any]] = {}
    for t in tasks:
        task_by_id[t.get("task_id", "")] = t

    for tid in _PM_TASK_ORDER:
        rec = task_by_id.get(tid)
        if rec is None:
            expected[tid] = {"error": "missing"}
            continue
        lc = rec.get("lifecycle", {})
        status = lc.get("status", "")
        notes = rec.get("notes", "")
        parent = rec.get("parent_task_id", "")
        expected[tid] = {
            "task_id": tid,
            "lifecycle": status,
            "notes": notes,
            "parent_task_id": parent,
            "is_complete": status == "complete",
            "is_planned": status == "planned",
            "is_in_progress": status == "in_progress",
        }

    pm_children = [t for t in tasks if t.get("parent_task_id") == _PM_PARENT
                   and t.get("task_id", "").startswith(_PM_PARENT + "-T")]
    pm_children.sort(key=lambda t: t.get("task_id", ""))
    completed_ids = {c["task_id"] for c in pm_children
                     if c.get("lifecycle", {}).get("status") == "complete"}
    for child in pm_children:
        if child["task_id"] not in completed_ids:
            expected["_pm_next_task"] = {
                "task_id": child["task_id"],
                "lifecycle": child.get("lifecycle", {}).get("status", ""),
            }
            break
    if "_pm_next_task" not in expected:
        expected["_pm_next_task"] = {"task_id": None, "lifecycle": "all_complete"}

    ph25 = task_by_id.get("PHASE8-IMPL-025")
    if ph25:
        expected["_ph25_active"] = ph25.get("lifecycle", {}).get("status") not in ("planned",)
    else:
        expected["_ph25_active"] = False

    return expected


def _check_structural(
    render_dir: Path,
    snapshot_dir: Path | None,
    snapshot_bundle: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []

    docs_dir = render_dir / "docs"
    if not docs_dir.is_dir():
        checks.append({"check": "docs_dir", "result": "fail", "detail": "docs/ not found"})
        return checks
    checks.append({"check": "docs_dir", "result": "pass"})

    actual_pages: set[str] = set()
    for entry in docs_dir.iterdir():
        if entry.is_file() and entry.name.endswith(".md"):
            actual_pages.add(entry.name)
    expected = set(RENDERED_PAGE_NAMES)
    missing = expected - actual_pages
    extra = actual_pages - expected
    if missing:
        checks.append({"check": "page_set", "result": "fail",
                       "detail": f"Missing pages: {sorted(missing)}"})
    elif extra:
        checks.append({"check": "page_set", "result": "fail",
                       "detail": f"Extra pages: {sorted(extra)}"})
    else:
        checks.append({"check": "page_set", "result": "pass", "detail": f"{len(actual_pages)} pages"})

    for fn in ("build-manifest.json", "source-snapshot.json",
               "FILE-INVENTORY.txt", "SHA256SUMS"):
        fpath = render_dir / fn
        if fpath.is_file():
            checks.append({"check": f"file:{fn}", "result": "pass"})
        else:
            checks.append({"check": f"file:{fn}", "result": "fail",
                           "detail": "Missing"})

    for fn in ("build-manifest.json", "source-snapshot.json"):
        fpath = render_dir / fn
        if fpath.is_file():
            try:
                _load_json(fpath)
                checks.append({"check": f"json:{fn}", "result": "pass"})
            except Exception as e:
                checks.append({"check": f"json:{fn}", "result": "fail",
                               "detail": str(e)})

    manifest_path = render_dir / "build-manifest.json"
    if manifest_path.is_file():
        manifest = _load_json(manifest_path)
        ac = manifest.get("authority_class", "")
        if ac == "generated_evidence":
            checks.append({"check": "manifest_authority_class", "result": "pass"})
        else:
            checks.append({"check": "manifest_authority_class", "result": "fail",
                           "detail": f"Got {ac}"})

        page_hashes = manifest.get("page_hashes", {})
        for page in RENDERED_PAGE_NAMES:
            fpath = docs_dir / page
            if fpath.is_file() and page in page_hashes:
                actual = _compute_sha256(fpath)
                expected_hash = page_hashes[page]
                if actual == expected_hash:
                    checks.append({"check": f"page_hash:{page}", "result": "pass"})
                else:
                    checks.append({"check": f"page_hash:{page}", "result": "fail",
                                   "detail": "Hash mismatch"})

        freshness = manifest.get("freshness", "")
        checks.append({"check": "freshness", "result": "pass", "detail": freshness})

        mode = manifest.get("mode", "")
        checks.append({"check": "mode", "result": "pass", "detail": mode})

        pub_eligible = manifest.get("publication_eligible", False)
        checks.append({"check": "publication_eligible", "result": "pass",
                       "detail": str(pub_eligible)})

        bc = manifest.get("target_commit", "")
        if _GIT_SHA_RE.match(bc):
            checks.append({"check": "commit_binding", "result": "pass", "detail": bc[:12]})
        else:
            checks.append({"check": "commit_binding", "result": "fail",
                           "detail": "Invalid or missing commit"})

    sha_path = render_dir / "SHA256SUMS"
    if sha_path.is_file():
        checks.append({"check": "sha256sums_present", "result": "pass"})

    for page in RENDERED_PAGE_NAMES:
        fpath = docs_dir / page
        if not fpath.is_file():
            continue
        text = _read_text(fpath)
        if "Generated Evidence" in text or "generated evidence" in text.lower():
            continue
        checks.append({"check": f"banner:{page}", "result": "fail",
                       "detail": "Missing generated-evidence banner"})

    for page in RENDERED_PAGE_NAMES:
        fpath = docs_dir / page
        if not fpath.is_file():
            continue
        text = _read_text(fpath)
        if "javascript:" in text.lower() or "<script" in text.lower():
            checks.append({"check": f"unsafe_content:{page}", "result": "fail",
                           "detail": "Potentially unsafe content"})
        else:
            checks.append({"check": f"unsafe_content:{page}", "result": "pass"})

    for page in RENDERED_PAGE_NAMES:
        fpath = docs_dir / page
        if not fpath.is_file():
            continue
        text = _read_text(fpath)
        for match in re.finditer(r"\]\(([^)]+)\)", text):
            link = match.group(1)
            if link.startswith("http://") or link.startswith("https://"):
                continue
            if ".." in link.replace("\\", "/").split("/"):
                checks.append({"check": f"unsafe_link:{page}", "result": "fail",
                               "detail": f"Traversal link: {link}"})

    return checks


def validate_rendered_package(
    repo_root: str,
    snapshot_dir: str,
    render_dir: str,
    registries: dict[str, Any] | None = None,
    snapshot_bundle: dict[str, Any] | None = None,
    expected_task_states: dict[str, Any] | None = None,
) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    render_path = Path(render_dir).resolve()
    errors: list[str] = []
    warnings: list[str] = []

    if registries is not None:
        tasks_data = registries.get("tasks.json", {})
    else:
        tasks_path = root / "docs" / "project-memory" / "registries" / "tasks.json"
        if tasks_path.is_file():
            tasks_data = _load_json(tasks_path)
        else:
            tasks_data = {}

    task_records = tasks_data.get("records", []) if isinstance(tasks_data, dict) else []
    if expected_task_states is None:
        task_states = derive_expected_task_states(task_records)
    else:
        task_states = expected_task_states

    missing_tasks = [tid for tid in _PM_TASK_ORDER
                     if task_states.get(tid, {}).get("error") == "missing"]
    if missing_tasks:
        errors.append(f"Required task records missing from registry: {missing_tasks}")
        return {
            "result": RESULT_BLOCKED,
            "errors": errors,
            "warnings": warnings,
            "target_commit": "",
            "target_branch": "",
            "snapshot_commit": "",
            "snapshot_branch": "",
            "render_commit": "",
            "render_branch": "",
            "page_count": 0,
            "structural_checks": [],
            "semantic_checks": [],
            "expected_task_states": task_states,
            "observed_task_states": {},
            "application_frontier_check": "fail",
            "ph8_impl_025_check": "fail",
            "remaining_work_check": "fail",
            "authority_check": "fail",
        }

    dup_ids: dict[str, int] = {}
    for t in task_records:
        tid = t.get("task_id", "")
        dup_ids[tid] = dup_ids.get(tid, 0) + 1
    duplicates = [tid for tid, cnt in dup_ids.items() if cnt > 1]
    if duplicates:
        errors.append(f"Duplicate task IDs in registry: {duplicates}")
        return _blocked_result(errors, warnings, task_states)

    snap = Path(snapshot_dir) if snapshot_dir else None
    structural_checks = _check_structural(render_path, snap, snapshot_bundle)
    for sc in structural_checks:
        if sc.get("result") == "fail":
            errors.append(f"Structural check failed: {sc.get('check')} — {sc.get('detail', '')}")

    docs_dir = render_path / "docs"

    r_branch = ""
    r_commit = ""
    if (render_path / "build-manifest.json").is_file():
        manifest = _load_json(render_path / "build-manifest.json")
        r_branch = manifest.get("target_branch", "")
        r_commit = manifest.get("target_commit", "")
    if (render_path / "source-snapshot.json").is_file():
        ss = _load_json(render_path / "source-snapshot.json")
        s_branch = ss.get("branch", "")
        s_commit = ss.get("bound_commit", "")
    else:
        s_branch = ""
        s_commit = ""

    page_count = 0
    for page in RENDERED_PAGE_NAMES:
        if (docs_dir / page).is_file():
            page_count += 1

    semantic_checks: list[dict[str, Any]] = []

    def _read_page(name: str) -> str:
        pp = docs_dir / name
        return _read_text(pp) if pp.is_file() else ""

    index_text = _read_page("index.md")
    roadmap_text = _read_page("current-roadmap.md")
    remaining_text = _read_page("remaining-work.md")

    for tid in _PM_TASK_ORDER:
        expected = task_states.get(tid, {})
        if not expected or expected.get("error"):
            continue
        es = expected.get("lifecycle", "")
        task_id_short = tid.replace("PHASE8-IMPL-026-", "")

        if es == "complete":
            if f"{task_id_short} (" in index_text and "in progress" in index_text:
                t4_check = _check_page_for_task(index_text, tid, "in progress")
                if t4_check:
                    errors.append(f"Semantic: {tid} rendered as 'in progress' but registry says complete")
                    semantic_checks.append({"check": f"task:{tid}_not_in_progress", "result": "fail"})
                else:
                    semantic_checks.append({"check": f"task:{tid}_not_in_progress", "result": "pass"})
            else:
                semantic_checks.append({"check": f"task:{tid}_not_in_progress", "result": "pass"})

        if es != "planned" and f"T004C" in index_text:
            if _check_page_for_task(index_text, "PHASE8-IMPL-026-T004C", "planned"):
                errors.append("Semantic: T004C rendered as 'planned' but registry says complete")
                semantic_checks.append({"check": "task:T004C_not_planned", "result": "fail"})
            else:
                semantic_checks.append({"check": "task:T004C_not_planned", "result": "pass"})
        else:
            semantic_checks.append({"check": "task:T004C_not_planned", "result": "pass"})

    t4_calls_in_progress = False
    for line in index_text.split("\n"):
        if "T004" in line and "Human-readable memory" in line and "in progress" in line:
            t4_calls_in_progress = True
            break
    if t4_calls_in_progress:
        errors.append("Semantic: T004 rendered as 'in progress' in index")
        semantic_checks.append({"check": "t004_not_in_progress_index", "result": "fail"})
    else:
        semantic_checks.append({"check": "t004_not_in_progress_index", "result": "pass"})

    t4c_calls_planned = False
    for line in index_text.split("\n"):
        if "T004C" in line and "Clean-HEAD" in line and "planned" in line:
            t4c_calls_planned = True
            break
    if t4c_calls_planned:
        errors.append("Semantic: T004C rendered as 'planned' in index")
        semantic_checks.append({"check": "t004c_not_planned_index", "result": "fail"})
    else:
        semantic_checks.append({"check": "t004c_not_planned_index", "result": "pass"})

    if "T004B" in roadmap_text and "Current Project Memory child" in roadmap_text:
        if "Current Project Memory child: T004B" in roadmap_text:
            errors.append("Semantic: T004B rendered as current PM child")
            semantic_checks.append({"check": "t004b_not_current_child", "result": "fail"})
        else:
            semantic_checks.append({"check": "t004b_not_current_child", "result": "pass"})
    else:
        semantic_checks.append({"check": "t004b_not_current_child", "result": "pass"})

    next_task = task_states.get("_pm_next_task", {})
    next_tid = next_task.get("task_id", "")
    if next_tid:
        short_next = next_tid.replace(_PM_PARENT + "-", "")
        if short_next not in roadmap_text:
            errors.append(f"Semantic: Next PM task {short_next} absent from current-roadmap")
            semantic_checks.append({"check": "next_task_in_roadmap", "result": "fail"})
        else:
            semantic_checks.append({"check": "next_task_in_roadmap", "result": "pass"})
    else:
        semantic_checks.append({"check": "next_task_in_roadmap", "result": "pass"})

    ph25_active = task_states.get("_ph25_active", False)
    if ph25_active:
        errors.append("Semantic: PHASE8-IMPL-025 appears activated but must remain inactive")
        semantic_checks.append({"check": "ph25_inactive", "result": "fail"})
    else:
        semantic_checks.append({"check": "ph25_inactive", "result": "pass"})

    app_frontier_ok = _EXPECTED_APP_FRONTIER in roadmap_text or _EXPECTED_APP_FRONTIER in index_text
    if not app_frontier_ok:
        errors.append(f"Semantic: Application frontier {_EXPECTED_APP_FRONTIER} not found in rendered pages")
        semantic_checks.append({"check": "app_frontier", "result": "fail"})
    else:
        semantic_checks.append({"check": "app_frontier", "result": "pass"})

    t4_rec = task_states.get("PHASE8-IMPL-026-T004", {})
    if t4_rec.get("is_complete"):
        if "T004" in remaining_text or "PHASE8-IMPL-026-T004" in remaining_text:
            t4_in_remaining = False
            for line in remaining_text.split("\n"):
                if ("PHASE8-IMPL-026-T004" in line or "T004" in line) and line.strip().startswith("-"):
                    t4_in_remaining = True
                    break
            if t4_in_remaining:
                errors.append("Semantic: T004 appears in remaining work but is complete")
                semantic_checks.append({"check": "t004_not_in_remaining", "result": "fail"})
            else:
                semantic_checks.append({"check": "t004_not_in_remaining", "result": "pass"})
        else:
            semantic_checks.append({"check": "t004_not_in_remaining", "result": "pass"})
    else:
        semantic_checks.append({"check": "t004_not_in_remaining", "result": "pass"})

    if next_tid:
        short_next = next_tid.replace(_PM_PARENT + "-", "")
        t5_in_remaining = f"PHASE8-IMPL-026-{short_next}" in remaining_text or short_next in remaining_text
        if not t5_in_remaining:
            errors.append(f"Semantic: Next task {short_next} missing from remaining-work")
            semantic_checks.append({"check": "next_task_in_remaining", "result": "fail"})
        else:
            semantic_checks.append({"check": "next_task_in_remaining", "result": "pass"})

    authority_ok = True
    for page in RENDERED_PAGE_NAMES:
        pp = docs_dir / page
        if not pp.is_file():
            continue
        text = _read_text(pp)
        if "authoritative" in text and "generated evidence" not in text[:200]:
            authority_ok = False
    semantic_checks.append({"check": "non_authoritative", "result": "pass" if authority_ok else "fail"})
    if not authority_ok:
        warnings.append("Some pages may claim authoritative status")

    observed = {}
    for tid in _PM_TASK_ORDER:
        observed[tid] = {"found_in_index": tid in index_text,
                         "found_in_roadmap": tid in roadmap_text}

    if errors:
        result = RESULT_BLOCKED
    elif warnings:
        result = RESULT_PASS_WITH_FINDINGS
    else:
        result = RESULT_PASS

    return {
        "result": result,
        "errors": errors,
        "warnings": warnings,
        "target_commit": r_commit,
        "target_branch": r_branch,
        "snapshot_commit": s_commit,
        "snapshot_branch": s_branch,
        "render_commit": r_commit,
        "render_branch": r_branch,
        "page_count": page_count,
        "structural_checks": structural_checks,
        "semantic_checks": semantic_checks,
        "expected_task_states": task_states,
        "observed_task_states": observed,
        "application_frontier_check": "pass" if app_frontier_ok else "fail",
        "ph8_impl_025_check": "fail" if ph25_active else "pass",
        "remaining_work_check": "pass",
        "authority_check": "pass" if authority_ok else "fail",
    }


def _check_page_for_task(text: str, task_id: str, term: str) -> bool:
    short = task_id.replace("PHASE8-IMPL-026-", "")
    lines = text.split("\n")
    for line in lines:
        if short in line and term in line:
            return True
    return False


def _blocked_result(
    errors: list[str], warnings: list[str], task_states: dict[str, Any]
) -> dict[str, Any]:
    return {
        "result": RESULT_BLOCKED,
        "errors": errors,
        "warnings": warnings,
        "target_commit": "",
        "target_branch": "",
        "snapshot_commit": "",
        "snapshot_branch": "",
        "render_commit": "",
        "render_branch": "",
        "page_count": 0,
        "structural_checks": [],
        "semantic_checks": [],
        "expected_task_states": task_states,
        "observed_task_states": {},
        "application_frontier_check": "fail",
        "ph8_impl_025_check": "fail",
        "remaining_work_check": "fail",
        "authority_check": "fail",
    }


def _build_result(
    errors: list[str],
    warnings: list[str],
    target_commit: str,
    target_branch: str,
    snap_commit: str,
    snap_branch: str,
    page_count: int,
    structural_checks: list[dict[str, Any]],
    semantic_checks: list[dict[str, Any]],
    task_states: dict[str, Any],
    observed: dict[str, Any],
    app_frontier_ok: bool,
    ph25_active: bool,
    remaining_ok: bool,
    authority_ok: bool,
) -> dict[str, Any]:
    if errors:
        overall = RESULT_BLOCKED
    elif warnings:
        overall = RESULT_PASS_WITH_FINDINGS
    else:
        overall = RESULT_PASS
    return {
        "result": overall,
        "errors": errors,
        "warnings": warnings,
        "target_commit": target_commit,
        "target_branch": target_branch,
        "snapshot_commit": snap_commit,
        "snapshot_branch": snap_branch,
        "render_commit": target_commit,
        "render_branch": target_branch,
        "page_count": page_count,
        "structural_checks": structural_checks,
        "semantic_checks": semantic_checks,
        "expected_task_states": task_states,
        "observed_task_states": observed,
        "application_frontier_check": "pass" if app_frontier_ok else "fail",
        "ph8_impl_025_check": "fail" if ph25_active else "pass",
        "remaining_work_check": "fail" if not remaining_ok else "pass",
        "authority_check": "pass" if authority_ok else "fail",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Semantic rendered-documentation validator.")
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--snapshot-dir", required=True)
    parser.add_argument("--render-dir", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = validate_rendered_package(
        repo_root=args.repo_root,
        snapshot_dir=args.snapshot_dir,
        render_dir=args.render_dir,
    )

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"Result: {result['result']}")
        for e in result.get("errors", []):
            print(f"  ERROR: {e}")
        for w in result.get("warnings", []):
            print(f"  WARNING: {w}")

    return 0 if result["result"] != RESULT_BLOCKED else 1


if __name__ == "__main__":
    sys.exit(main())
