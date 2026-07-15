#!/usr/bin/env python3
"""Build a deterministic Project Memory operational quality package."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.project_memory import build_plan_integrity_report
from scripts.project_memory import render_docs
from scripts.project_memory import validate_rendered_docs

PACKAGE_VERSION = "project_memory_quality_package.v1"
EXACT_FILES = ("FILE-INVENTORY.txt", "SHA256SUMS", "quality-report.json", "summary.md")
ACCEPTED_READINESS = frozenset({"READY", "READY_WITH_ADVISORIES"})
ACCEPTED_ADVISORY_CODES = frozenset({"source_missing"})


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _validate_inventory_and_checksums(package_dir: Path) -> dict[str, Any]:
    errors: list[str] = []
    inventory_path = package_dir / "FILE-INVENTORY.txt"
    sums_path = package_dir / "SHA256SUMS"
    if not inventory_path.is_file() or not sums_path.is_file():
        return {"result": "BLOCKED", "errors": ["missing inventory or checksum manifest"]}
    inventory = inventory_path.read_text(encoding="utf-8").splitlines()
    actual = sorted(
        path.relative_to(package_dir).as_posix()
        for path in package_dir.rglob("*")
        if path.is_file()
    )
    accepted_inventory_shapes = [actual, sorted(item for item in actual if item != "SHA256SUMS")]
    if sorted(inventory) not in accepted_inventory_shapes:
        errors.append("inventory mismatch")
    covered: list[str] = []
    for line in sums_path.read_text(encoding="utf-8").splitlines():
        try:
            digest, relative = line.split("  ", 1)
        except ValueError:
            errors.append("malformed checksum line")
            continue
        if relative.startswith("/") or ".." in relative.replace("\\", "/").split("/"):
            errors.append(f"unsafe checksum path: {relative}")
            continue
        target = package_dir / relative
        covered.append(relative)
        if not target.is_file() or _sha256(target) != digest:
            errors.append(f"checksum failure: {relative}")
    expected_coverage = sorted(item for item in actual if item != "SHA256SUMS")
    if sorted(covered) != expected_coverage:
        errors.append("checksum coverage mismatch")
    return {"result": "PASS" if not errors else "BLOCKED", "errors": errors}


def validate_quality_package(package_dir: str | Path) -> dict[str, Any]:
    path = Path(package_dir)
    errors: list[str] = []
    if not path.is_dir():
        return {"result": "BLOCKED", "errors": ["quality package is missing"]}
    actual = sorted(item.name for item in path.iterdir())
    if actual != list(EXACT_FILES) or any(not item.is_file() for item in path.iterdir()):
        errors.append("exact quality-package inventory mismatch")
    manifest = _validate_inventory_and_checksums(path)
    errors.extend(manifest["errors"])
    try:
        report = _load_json(path / "quality-report.json")
        if report.get("schema") != PACKAGE_VERSION:
            errors.append("quality-report schema mismatch")
        if report.get("authority_class") != "generated_evidence":
            errors.append("quality-report authority mismatch")
        if report.get("result") not in {"PASS", "PASS_WITH_FINDINGS"}:
            errors.append("quality-report result is not passing")
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        errors.append(f"invalid quality-report.json: {exc}")
    return {"result": "PASS" if not errors else "BLOCKED", "errors": errors}


def build_quality_package(
    *,
    repo_root: str | Path,
    report_dir: str | Path,
    snapshot_dir: str | Path,
    render_dir: str | Path,
    output_root: str | Path,
    task_id: str,
    run_id: str,
    expected_branch: str,
    expected_commit: str,
    accepted_advisory_codes: set[str] | frozenset[str] = ACCEPTED_ADVISORY_CODES,
) -> dict[str, Any]:
    root = Path(repo_root).resolve(strict=True)
    report_path = Path(report_dir).resolve(strict=True)
    snapshot_path = Path(snapshot_dir).resolve(strict=True)
    render_path = Path(render_dir).resolve(strict=True)
    output = Path(output_root)
    output = (root / output).resolve() if not output.is_absolute() else output.resolve()

    report_validation = build_plan_integrity_report.validate_plan_integrity_package(report_path)
    if report_validation["result"] != "PASS":
        raise RuntimeError("Plan Integrity package validation failed: " + "; ".join(report_validation["errors"]))
    report_meta = _load_json(report_path / "run-metadata.json")
    readiness = _load_json(report_path / "readiness.json")
    findings = _load_json(report_path / "findings.json")
    comparisons = _load_json(report_path / "comparisons.json")
    if readiness.get("result") not in ACCEPTED_READINESS:
        raise RuntimeError("Plan Integrity readiness is blocked")
    unsupported = sorted({
        item.get("code", "")
        for item in findings.get("findings", [])
        if item.get("blocking") or item.get("code") not in accepted_advisory_codes
    })
    if unsupported:
        raise RuntimeError(f"Unsupported Plan Integrity findings: {unsupported}")

    snapshot_bundle = render_docs.validate_snapshot_package(str(snapshot_path), root)
    snapshot = snapshot_bundle["snapshot"]
    if snapshot.get("freshness_state") != "current" or not snapshot.get("publication_eligible"):
        raise RuntimeError("Snapshot is not current and publication eligible")
    if snapshot_bundle.get("conv_result") == "BLOCKED":
        raise RuntimeError("Snapshot convergence is blocked")

    semantic = validate_rendered_docs.validate_rendered_package(
        repo_root=str(root), snapshot_dir=str(snapshot_path), render_dir=str(render_path)
    )
    if semantic.get("result") == validate_rendered_docs.RESULT_BLOCKED:
        raise RuntimeError("Rendered semantic or authority validation blocked")
    manifest = _load_json(render_path / "build-manifest.json")

    bindings = {
        "plan_integrity": [report_meta.get("branch"), report_meta.get("bound_commit")],
        "snapshot": [snapshot.get("branch"), snapshot.get("bound_commit")],
        "render": [manifest.get("target_branch"), manifest.get("target_commit")],
        "render_source_snapshot": [manifest.get("source_snapshot_branch"), manifest.get("source_snapshot_bound_commit")],
    }
    for name, pair in bindings.items():
        if pair != [expected_branch, expected_commit]:
            raise RuntimeError(f"{name} branch/full-commit binding mismatch")

    package_checks = {
        "plan_integrity": _validate_inventory_and_checksums(report_path),
        "snapshot": _validate_inventory_and_checksums(snapshot_path),
        "render": _validate_inventory_and_checksums(render_path),
    }
    blocked_checks = [name for name, check in package_checks.items() if check["result"] != "PASS"]
    if blocked_checks:
        raise RuntimeError(f"Inventory/checksum verification failed: {blocked_checks}")

    t011 = next(
        (item for item in comparisons.get("comparisons", []) if item.get("subject_id") == "PHASE8-IMPL-026-T011"),
        None,
    )
    t011_classification = t011.get("classification") if t011 else None
    task_state_mismatch = [
        item for item in findings.get("findings", [])
        if item.get("code") == "task_state_mismatch" and item.get("subject_id") == "PHASE8-IMPL-026-T011"
    ]
    warnings = list(semantic.get("warnings", []))
    result = "PASS_WITH_FINDINGS" if findings.get("finding_count", 0) or warnings else "PASS"
    quality_report = {
        "schema": PACKAGE_VERSION,
        "authority_class": "generated_evidence",
        "accepted_current_publication": True,
        "result": result,
        "task_id": task_id,
        "run_id": run_id,
        "branch": expected_branch,
        "bound_commit": expected_commit,
        "plan_integrity": {
            "result": readiness.get("result"),
            "finding_count": findings.get("finding_count", 0),
            "finding_codes": sorted(findings.get("by_code", {})),
        },
        "snapshot": {
            "result": snapshot_bundle.get("conv_result"),
            "freshness": snapshot.get("freshness_state"),
            "publication_eligible": snapshot.get("publication_eligible"),
        },
        "render": {
            "result": "PASS",
            "freshness": manifest.get("freshness"),
            "page_count": manifest.get("page_count"),
        },
        "semantic_validation": semantic,
        "authority_validation": {
            "result": "PASS" if semantic.get("authority_check") == "pass" else "BLOCKED",
            "detail": semantic.get("authority", {}),
        },
        "t011": {
            "classification": t011_classification,
            "observed_lifecycle": (t011 or {}).get("observed_state", {}).get("lifecycle"),
            "task_state_mismatch": bool(task_state_mismatch),
        },
        "bindings": bindings,
        "package_checks": package_checks,
        "warnings": warnings,
        "boundaries": {
            "generated_evidence_only": True,
            "git_mutation_performed": False,
            "reviewer_or_model_performed": False,
            "roadmap_or_registry_mutation_performed": False,
            "memory_canon_or_promotion_mutation_performed": False,
            "story_prose_mutation_performed": False,
        },
    }

    run_dir = output / f"{task_id}-quality" / run_id
    if run_dir.exists():
        raise FileExistsError(f"Quality run directory already exists: {run_dir}")
    output.parent.mkdir(parents=True, exist_ok=True)
    temp_root = Path(tempfile.mkdtemp(prefix=f"quality_{task_id}_", dir=output.parent))
    try:
        temp_run = temp_root / f"{task_id}-quality" / run_id
        temp_run.mkdir(parents=True)
        (temp_run / "quality-report.json").write_text(
            json.dumps(quality_report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        summary = (
            "Generated evidence — not project authority\n\n"
            "# Project Memory Operational Quality Package\n\n"
            f"- Result: **{result}**\n- Branch: `{expected_branch}`\n"
            f"- Commit: `{expected_commit}`\n- Plan Integrity: `{readiness.get('result')}`\n"
            f"- Snapshot: `{snapshot_bundle.get('conv_result')}`\n"
            f"- Render/Semantic/Authority: `PASS`\n"
        )
        (temp_run / "summary.md").write_text(summary, encoding="utf-8")
        (temp_run / "FILE-INVENTORY.txt").write_text("\n".join(EXACT_FILES) + "\n", encoding="utf-8")
        sums = [
            f"{_sha256(temp_run / name)}  {name}"
            for name in EXACT_FILES if name != "SHA256SUMS"
        ]
        (temp_run / "SHA256SUMS").write_text("\n".join(sums) + "\n", encoding="utf-8")
        validation = validate_quality_package(temp_run)
        if validation["result"] != "PASS":
            raise RuntimeError("Malformed quality package: " + "; ".join(validation["errors"]))
        output.mkdir(parents=True, exist_ok=True)
        (output / f"{task_id}-quality").mkdir(parents=True, exist_ok=True)
        os.rename(temp_run, run_dir)
    except Exception:
        shutil.rmtree(temp_root, ignore_errors=True)
        raise
    shutil.rmtree(temp_root, ignore_errors=True)
    return {
        "result": result,
        "output_directory": str(run_dir),
        "quality_report": str(run_dir / "quality-report.json"),
        "t011_classification": t011_classification,
        "t011_task_state_mismatch": bool(task_state_mismatch),
        "checksums": {name: _sha256(run_dir / name) for name in EXACT_FILES},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--report-dir", required=True)
    parser.add_argument("--snapshot-dir", required=True)
    parser.add_argument("--render-dir", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--expected-branch", required=True)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = build_quality_package(
            repo_root=args.repo_root, report_dir=args.report_dir,
            snapshot_dir=args.snapshot_dir, render_dir=args.render_dir,
            output_root=args.output_root, task_id=args.task_id, run_id=args.run_id,
            expected_branch=args.expected_branch, expected_commit=args.expected_commit,
        )
    except Exception as exc:
        result = {"result": "BLOCKED", "error": str(exc)}
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else result["result"])
    return 0 if result.get("result") in {"PASS", "PASS_WITH_FINDINGS"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
