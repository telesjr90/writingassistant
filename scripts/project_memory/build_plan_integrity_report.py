#!/usr/bin/env python3
"""Build an atomic generated-evidence Plan Integrity package."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.project_memory import plan_integrity as integrity

PACKAGE_VERSION = "1.0.0"
EXACT_PACKAGE_FILES = (
    "FILE-INVENTORY.txt",
    "SHA256SUMS",
    "comparisons.json",
    "dependency-report.json",
    "findings.json",
    "implementation-input.json",
    "plan-input.json",
    "readiness.json",
    "run-metadata.json",
    "summary.md",
    "traceability.json",
)


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _generated_at(run_id: str) -> str:
    try:
        parsed = datetime.strptime(run_id, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
    except ValueError as exc:
        raise ValueError("run_id must use UTC YYYYMMDDTHHMMSSZ format") from exc
    return parsed.isoformat().replace("+00:00", "Z")


def _safe_output_root(repo_root: Path, output_root: str | Path) -> Path:
    requested = Path(output_root)
    output = (repo_root / requested).resolve() if not requested.is_absolute() else requested.resolve()
    allowed = (repo_root / ".codex-context" / "project-memory").resolve()
    if output != allowed:
        raise ValueError("output_root must resolve to .codex-context/project-memory")
    return output


def _summary(metadata: dict[str, Any], readiness: dict[str, Any], comparisons: dict[str, Any], findings: dict[str, Any]) -> str:
    lines = [
        "Generated evidence — not project authority",
        "",
        "# Deterministic Plan Integrity Report",
        "",
        f"- Task: `{metadata['task_id']}`",
        f"- Branch: `{metadata['branch']}`",
        f"- Commit: `{metadata['bound_commit']}`",
        f"- Readiness: **{readiness['result']}**",
        f"- Comparisons: {comparisons['comparison_count']}",
        f"- Findings: {findings['finding_count']} ({findings['blocking_count']} blocking)",
        "",
        "## Classification counts",
        "",
    ]
    for name, count in comparisons["counts"].items():
        lines.append(f"- `{name}`: {count}")
    lines += ["", "## Findings", ""]
    if findings["findings"]:
        for item in findings["findings"]:
            lines.append(f"- [{item['severity'].upper()}] `{item['code']}`: {item['explanation']}")
    else:
        lines.append("- None")
    lines += [
        "",
        "## Execution boundary",
        "",
        "No external tool, network, model, roadmap mutation, registry mutation, source mutation, or application-worktree access occurred. No reviewer agent ran. The package is generated_evidence and cannot mutate authoritative state, Memory/Canon, candidates, promotions, or story prose.",
        "",
    ]
    return "\n".join(lines)


def validate_plan_integrity_package(package_dir: str | Path) -> dict[str, Any]:
    """Validate exact inventory, JSON, checksums, authority, and readiness shape."""
    path = Path(package_dir)
    errors: list[str] = []
    actual = sorted(item.name for item in path.iterdir()) if path.is_dir() else []
    if actual != list(EXACT_PACKAGE_FILES):
        errors.append(f"Exact package mismatch: {actual}")
    if path.is_dir() and any(not item.is_file() for item in path.iterdir()):
        errors.append("Package contains a non-file entry")
    json_names = tuple(name for name in EXACT_PACKAGE_FILES if name.endswith(".json"))
    loaded: dict[str, Any] = {}
    for name in json_names:
        try:
            loaded[name] = json.loads((path / name).read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            errors.append(f"Invalid JSON {name}: {exc}")
    try:
        inventory = (path / "FILE-INVENTORY.txt").read_text(encoding="utf-8").splitlines()
        if inventory != list(EXACT_PACKAGE_FILES):
            errors.append("FILE-INVENTORY.txt mismatch")
    except OSError as exc:
        errors.append(f"Cannot read FILE-INVENTORY.txt: {exc}")
    try:
        pairs = []
        for line in (path / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
            digest, name = line.split("  ", 1)
            pairs.append((digest, name))
        expected_names = sorted(name for name in EXACT_PACKAGE_FILES if name != "SHA256SUMS")
        if sorted(name for _, name in pairs) != expected_names:
            errors.append("SHA256SUMS coverage mismatch")
        for digest, name in pairs:
            if Path(name).name != name or _sha256(path / name) != digest:
                errors.append(f"Checksum mismatch: {name}")
    except (OSError, ValueError) as exc:
        errors.append(f"Invalid SHA256SUMS: {exc}")

    metadata = loaded.get("run-metadata.json", {})
    required_metadata = {
        "authority_class": "generated_evidence",
        "application_worktree_access_performed": False,
        "external_tool_performed": False,
        "model_call_performed": False,
        "network_access_performed": False,
        "registry_mutation_performed": False,
        "roadmap_mutation_performed": False,
        "source_mutation_performed": False,
        "reviewer_agent_performed": False,
    }
    for key, expected in required_metadata.items():
        if metadata.get(key) != expected:
            errors.append(f"run-metadata.json {key} must be {expected!r}")
    if loaded.get("readiness.json", {}).get("result") not in integrity.READINESS_RESULTS:
        errors.append("Invalid readiness result")
    comparisons = loaded.get("comparisons.json", {}).get("comparisons", [])
    if any(item.get("classification") not in integrity.CLASSIFICATIONS for item in comparisons):
        errors.append("Invalid comparison classification")
    if any(item.get("branch") != metadata.get("branch") or item.get("commit") != metadata.get("bound_commit") for item in comparisons):
        errors.append("Comparison branch/commit binding mismatch")
    try:
        first_line = (path / "summary.md").read_text(encoding="utf-8").splitlines()[0]
        if first_line != "Generated evidence — not project authority":
            errors.append("summary.md authority banner mismatch")
    except (OSError, IndexError) as exc:
        errors.append(f"Invalid summary.md: {exc}")
    return {"result": "PASS" if not errors else "BLOCKED", "errors": errors}


def build_plan_integrity_package(
    repo_root: str | Path,
    output_root: str | Path,
    task_id: str,
    run_id: str,
    *,
    expected_branch: str | None = None,
    expected_commit: str | None = None,
    registries_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Build exactly one clean-HEAD, commit-bound generated package atomically."""
    root = Path(repo_root).resolve(strict=True)
    if not (root / ".git").exists():
        raise ValueError(f"Not a Git repository: {root}")
    output = _safe_output_root(root, output_root)
    generated_at = _generated_at(run_id)

    from scripts.project_memory import validate_registries

    effective_registries_dir = (
        Path(registries_dir)
        if registries_dir is not None
        else root / "docs" / "project-memory" / "registries"
    )
    validation_findings = validate_registries.validate(effective_registries_dir)
    errors = [item for item in validation_findings if item.get("level") == "error"]
    if errors:
        raise RuntimeError(f"Registry validation failed with {len(errors)} error(s)")

    plan = integrity.load_plan_inputs(root, registries_dir=effective_registries_dir)
    implementation = integrity.load_implementation_inputs(
        root, plan_inputs=plan, expected_branch=expected_branch,
        expected_commit=expected_commit, registry_findings=validation_findings,
    )
    if implementation["dirty"]:
        raise RuntimeError("Working tree is dirty; Plan Integrity report requires clean HEAD")
    if implementation["staged"]:
        raise RuntimeError("Staging area is not empty; Plan Integrity report requires clean HEAD")
    if not implementation["branch_matches"] or not implementation["commit_matches"]:
        raise RuntimeError("Repository branch or commit binding mismatch")

    comparisons = integrity.build_comparisons(plan, implementation)
    findings = integrity.run_plan_integrity_checks(plan, implementation, comparisons)
    readiness = integrity.derive_readiness(findings["findings"])
    run_dir = output / task_id / run_id
    if run_dir.exists():
        raise FileExistsError(f"Run directory already exists: {run_dir}")

    metadata = {
        "authority_class": integrity.AUTHORITY_CLASS,
        "branch": implementation["branch"],
        "bound_commit": implementation["commit"],
        "engine_name": integrity.ENGINE_NAME,
        "engine_version": integrity.ENGINE_VERSION,
        "generated_at": generated_at,
        "package_version": PACKAGE_VERSION,
        "repository_root": str(root),
        "result": readiness["result"],
        "run_id": run_id,
        "task_id": task_id,
        "application_worktree_access_performed": False,
        "external_tool_performed": False,
        "model_call_performed": False,
        "network_access_performed": False,
        "registry_mutation_performed": False,
        "roadmap_mutation_performed": False,
        "source_mutation_performed": False,
        "reviewer_agent_performed": False,
    }
    comparisons_doc = {
        "authority_class": integrity.AUTHORITY_CLASS,
        "comparison_count": len(comparisons),
        "counts": integrity.comparison_counts(comparisons),
        "comparisons": comparisons,
    }
    findings_doc = {"authority_class": integrity.AUTHORITY_CLASS, **findings}
    dependencies = _registry_records(plan, "dependencies")
    dependency_report = {
        "authority_class": integrity.AUTHORITY_CLASS,
        "dependency_count": len(dependencies),
        "dependencies": dependencies,
        "cycle_count": findings["by_code"].get("dependency_cycle", 0),
        "missing_required_count": findings["by_code"].get("missing_required_dependency", 0),
    }
    traceability = {
        "authority_class": integrity.AUTHORITY_CLASS,
        "branch": implementation["branch"],
        "commit": implementation["commit"],
        "plan_source_hashes": plan["source_hashes"],
        "implementation_sources": implementation["source_records"],
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    temp_root = Path(tempfile.mkdtemp(prefix=f"plan_integrity_{task_id}_", dir=output.parent))
    try:
        temp_run = temp_root / task_id / run_id
        temp_run.mkdir(parents=True, exist_ok=False)
        _write_json(temp_run / "run-metadata.json", metadata)
        _write_json(temp_run / "plan-input.json", plan)
        _write_json(temp_run / "implementation-input.json", implementation)
        _write_json(temp_run / "comparisons.json", comparisons_doc)
        _write_json(temp_run / "findings.json", findings_doc)
        _write_json(temp_run / "dependency-report.json", dependency_report)
        _write_json(temp_run / "traceability.json", traceability)
        _write_json(temp_run / "readiness.json", readiness)
        (temp_run / "summary.md").write_text(
            _summary(metadata, readiness, comparisons_doc, findings_doc), encoding="utf-8"
        )
        (temp_run / "FILE-INVENTORY.txt").write_text(
            "\n".join(EXACT_PACKAGE_FILES) + "\n", encoding="utf-8"
        )
        checksums = [
            f"{_sha256(temp_run / name)}  {name}"
            for name in EXACT_PACKAGE_FILES if name != "SHA256SUMS"
        ]
        (temp_run / "SHA256SUMS").write_text("\n".join(checksums) + "\n", encoding="utf-8")
        validation = validate_plan_integrity_package(temp_run)
        if validation["result"] != "PASS":
            raise RuntimeError("Malformed output package: " + "; ".join(validation["errors"]))
        output.mkdir(parents=True, exist_ok=True)
        (output / task_id).mkdir(parents=True, exist_ok=True)
        os.rename(temp_run, run_dir)
    except Exception:
        shutil.rmtree(temp_root, ignore_errors=True)
        raise
    shutil.rmtree(temp_root, ignore_errors=True)
    return {
        "authority_class": integrity.AUTHORITY_CLASS,
        "bound_branch": implementation["branch"],
        "bound_commit": implementation["commit"],
        "comparison_count": len(comparisons),
        "comparison_counts": comparisons_doc["counts"],
        "finding_count": findings["finding_count"],
        "findings_by_code": findings["by_code"],
        "findings_by_severity": findings["by_severity"],
        "blocking_count": findings["blocking_count"],
        "conflict_count": findings["conflict_count"],
        "insufficient_evidence_count": findings["insufficient_evidence_count"],
        "output_directory": str(run_dir),
        "readiness": readiness["result"],
        "result": readiness["result"],
        "run_id": run_id,
        "task_id": task_id,
    }


def _registry_records(plan: dict[str, Any], name: str) -> list[dict[str, Any]]:
    container = plan.get("registries", {}).get(name, {})
    return container.get("records", []) if isinstance(container, dict) else []


def main() -> int:
    parser = argparse.ArgumentParser(description="Build deterministic Plan Integrity report.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output-root", default=".codex-context/project-memory")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        result = build_plan_integrity_package(
            args.repo_root, args.output_root, args.task_id, args.run_id
        )
    except Exception as exc:
        if args.json:
            print(json.dumps({"error": str(exc)}, indent=2, sort_keys=True))
        else:
            print(f"ERROR: {exc}")
        return 1
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"Plan Integrity report: {result['output_directory']}")
        print(f"Readiness: {result['readiness']}")
    return 0 if result["readiness"] != "BLOCKED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
