#!/usr/bin/env python3
"""Deterministic Plan Integrity analysis for Project Memory.

The engine compares accepted tracked plan records with bounded repository
implementation evidence.  It is read-only: returned reports are generated
evidence and never update roadmap, registry, Memory/Canon, candidate, or
promotion state.
"""

from __future__ import annotations

import hashlib
import json
import os
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

AUTHORITY_CLASS = "generated_evidence"
ENGINE_NAME = "project_memory_plan_integrity"
ENGINE_VERSION = "1.0.0"

CLASSIFICATIONS = (
    "matching",
    "diverging",
    "superseded",
    "conflicting",
    "insufficient_evidence",
)
READINESS_RESULTS = ("READY", "READY_WITH_ADVISORIES", "BLOCKED")
OVERLAP_OUTCOMES = (
    "REUSE", "EXTEND", "REFACTOR", "SUPERSEDE", "KEEP_SEPARATE",
    "TRUE_NEW", "INSUFFICIENT_EVIDENCE",
)

RULE_GROUPS = (
    "task_state_convergence",
    "decision_supersession_integrity",
    "dependency_delivery_integrity",
    "evidence_traceability_integrity",
    "exact_duplicate_overlap_integrity",
    "product_boundary_integrity",
)

_SEVERITY_RANK = {"critical": 0, "error": 1, "warning": 2, "info": 3}
_AUTHORITY_RANK = {
    "authoritative": 0,
    "accepted_evidence": 1,
    "historical": 4,
    "superseded": 4,
    "generated_evidence": 6,
    "uncertain": 7,
    "owner_pending": 7,
    "untrusted": 8,
}

_ROADMAP_FILES = (
    "docs/roadmap/tasks/PHASE8-IMPL-026.md",
    "docs/roadmap/enrichment/PHASE8-IMPL-026.enrichment.json",
    "docs/roadmap/implementation_status.md",
    "docs/roadmap/task_backlog.md",
    "docs/roadmap/phase_map.md",
    "docs/roadmap/decision_log.md",
    "docs/roadmap/open_questions.md",
    "docs/roadmap/risk_register.md",
    "docs/roadmap/roadmap_index.yaml",
)

_REQUIRED_BOUNDARIES = {
    "analysis-only": "analysis-only",
    "candidate-first": "candidate-first",
    "evidence-provenance-backed": "evidence/provenance",
    "owner-controlled": "owner control and no automatic roadmap mutation",
    "no-generated-prose": "no generated story prose",
    "no-automatic-memory-canon-mutation": "no Memory/Canon mutation",
    "no-automatic-promotion": "no automatic promotion",
    "no-auto-apply-promotion": "no automatic apply-promotion",
    "model-output-not-canon": "model output not treated as truth",
}

_DELIVERY_ROOTS = (
    "scripts/",
    "tests/",
    "backend/",
    "frontend/",
    ".agents/",
    ".opencode/",
    "docs/project-memory/",
)
_TRUSTED_IMPLEMENTATION_AUTHORITIES = {"authoritative", "accepted_evidence"}
_PROJECT_MEMORY_PARENT = "PHASE8-IMPL-026"
_DEFERRED_PROJECT_MEMORY_TASKS = {
    "PHASE8-IMPL-026-T006",
    "PHASE8-IMPL-026-T007",
}
_NO_NEXT_ROADMAP_TOKENS = {
    "docs/roadmap/tasks/PHASE8-IMPL-026.md": (
        "there is no next project memory implementation task",
        "ongoing maintenance",
    ),
    "docs/roadmap/implementation_status.md": (
        "there is no next project memory implementation task",
        "sole next implementation focus",
    ),
    "docs/roadmap/task_backlog.md": (
        "there is no next project memory implementation task",
        "ongoing maintenance",
    ),
    "docs/roadmap/phase_map.md": (
        "there is no next project memory implementation task",
        "ongoing maintenance",
    ),
    "docs/roadmap/open_questions.md": (
        "q152 remains open",
        "q153 remains open",
        "resolved by phase8-impl-026-t011",
    ),
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _stable_id(prefix: str, *parts: Any) -> str:
    material = "|".join(str(part) for part in parts)
    return f"{prefix}-{hashlib.sha256(material.encode('utf-8')).hexdigest()[:16]}"


def _safe_relative_path(value: str) -> bool:
    if not isinstance(value, str) or not value or os.path.isabs(value):
        return False
    normalized = value.replace("\\", "/")
    return not normalized.startswith("/") and ".." not in normalized.split("/")


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _registry_records(plan_inputs: dict[str, Any], name: str) -> list[dict[str, Any]]:
    value = plan_inputs.get("registries", {}).get(name, {})
    records = value.get("records", []) if isinstance(value, dict) else []
    return [record for record in records if isinstance(record, dict)]


def _record_locator_paths(record: dict[str, Any]) -> list[str]:
    provenance = record.get("provenance", {})
    locators = provenance.get("source_locators", []) if isinstance(provenance, dict) else []
    return sorted(
        locator.get("path", "")
        for locator in locators
        if isinstance(locator, dict) and isinstance(locator.get("path"), str)
    )


def load_plan_inputs(
    repo_root: str | Path,
    *,
    registries_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Load accepted plan sources without mutating them."""
    root = Path(repo_root).resolve(strict=True)
    registry_root = (
        Path(registries_dir).resolve(strict=True)
        if registries_dir is not None
        else root / "docs" / "project-memory" / "registries"
    )
    manifest = _load_json(registry_root / "manifest.json")
    registries: dict[str, Any] = {}
    source_hashes: dict[str, str] = {}
    for declaration in sorted(manifest.get("registries", []), key=lambda item: item["filename"]):
        filename = declaration["filename"]
        path = registry_root / filename
        registries[filename.removesuffix(".json")] = _load_json(path)
        try:
            relative = path.relative_to(root).as_posix()
        except ValueError:
            relative = path.as_posix()
        source_hashes[relative] = _sha256_file(path)

    roadmap: dict[str, Any] = {}
    for relative in _ROADMAP_FILES:
        path = root / relative
        if not path.is_file():
            roadmap[relative] = {"missing": True}
            continue
        raw = path.read_text(encoding="utf-8")
        if path.suffix in {".json", ".yaml"}:
            try:
                roadmap[relative] = json.loads(raw)
            except json.JSONDecodeError as exc:
                roadmap[relative] = {"malformed": str(exc), "raw": raw}
        else:
            roadmap[relative] = raw
        source_hashes[relative] = _sha256_bytes(raw.encode("utf-8"))

    return {
        "input_type": "accepted_plan",
        "authority_classes": ["authoritative", "accepted_evidence"],
        "manifest": manifest,
        "registries": registries,
        "roadmap": roadmap,
        "source_hashes": dict(sorted(source_hashes.items())),
        "risk_input": "docs/roadmap/risk_register.md",
    }


def load_implementation_inputs(
    repo_root: str | Path,
    *,
    plan_inputs: dict[str, Any] | None = None,
    expected_branch: str | None = None,
    expected_commit: str | None = None,
    repository_state_override: dict[str, Any] | None = None,
    registry_findings: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Load commit-bound implementation evidence using established scanners."""
    root = Path(repo_root).resolve(strict=True)
    if plan_inputs is None:
        plan_inputs = load_plan_inputs(root)
    if repository_state_override is None:
        from scripts.project_memory import repository_state

        repository_state_override = repository_state.collect_repository_state(str(root))
    if registry_findings is None:
        from scripts.project_memory import validate_registries

        registry_findings = validate_registries.validate()

    state = dict(repository_state_override)
    tracked_files = set(state.get("tracked_files", []))
    source_records: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for registry_name, container in sorted(plan_inputs.get("registries", {}).items()):
        for record in container.get("records", []) if isinstance(container, dict) else []:
            if not isinstance(record, dict):
                continue
            for path in _record_locator_paths(record):
                key = (record.get("id", ""), path)
                if key in seen:
                    continue
                seen.add(key)
                item: dict[str, Any] = {
                    "record_id": record.get("id", ""),
                    "registry": registry_name,
                    "path": path,
                    "authority_class": record.get("authority_class", ""),
                    "safe": _safe_relative_path(path),
                }
                full = root / path
                regular_file = item["safe"] and full.is_file() and not full.is_symlink()
                item["regular_file"] = regular_file
                item["tracked"] = path in tracked_files
                if regular_file:
                    item.update({"exists": True, "sha256": _sha256_file(full)})
                else:
                    item["exists"] = False
                source_records.append(item)
    source_records.sort(key=lambda item: (item["record_id"], item["path"]))

    return {
        "input_type": "tracked_implementation_evidence",
        "repository_root": str(root),
        "branch": state.get("branch", ""),
        "commit": state.get("head_sha", state.get("commit", "")),
        "head_subject": state.get("head_subject", ""),
        "dirty": bool(state.get("dirty", False) or state.get("untracked_paths")),
        "staged": bool(state.get("staged", False)),
        "modified_paths": sorted(state.get("modified_paths", [])),
        "untracked_paths": sorted(state.get("untracked_paths", [])),
        "expected_branch": expected_branch,
        "expected_commit": expected_commit,
        "branch_matches": expected_branch is None or state.get("branch") == expected_branch,
        "commit_matches": expected_commit is None or state.get("head_sha", state.get("commit")) == expected_commit,
        "registry_validation_findings": registry_findings,
        "source_records": source_records,
    }


def deterministic_confidence_basis(
    *, classification: str, rule_id: str, evidence_count: int, required_evidence: bool
) -> dict[str, Any]:
    """Return a deterministic, non-probabilistic confidence basis."""
    complete = classification not in {"insufficient_evidence", "conflicting"}
    return {
        "method": "exact_rule_evaluation",
        "rule_id": rule_id,
        "evidence_count": int(evidence_count),
        "required_evidence": bool(required_evidence),
        "inputs_complete": complete,
        "basis": (
            "All required exact inputs satisfied the deterministic rule."
            if complete
            else "Required exact inputs were absent, invalid, or unresolved."
        ),
    }


def classify_claims(
    expected: Any,
    observed: Any,
    *,
    required_evidence_present: bool = True,
    required_trust_satisfied: bool = True,
    stale: bool = False,
    superseded_by: str | None = None,
    historical: bool = False,
    unresolved_equal_authority_conflict: bool = False,
) -> str:
    """Apply the exact Q151 classification vocabulary."""
    if unresolved_equal_authority_conflict:
        return "conflicting"
    if historical and superseded_by:
        return "superseded"
    if not required_evidence_present or not required_trust_satisfied or stale:
        return "insufficient_evidence"
    if expected == observed:
        return "matching"
    return "diverging"


def _comparison(
    *,
    subject_type: str,
    subject_id: str,
    expected: Any,
    observed: Any,
    classification: str,
    locators: Iterable[str],
    authority_classes: Iterable[str],
    branch: str,
    commit: str,
    rule_id: str,
    severity: str = "info",
    blocking: bool = False,
    explanation: str,
    owner_review_required: bool = False,
    next_check: str,
    required_evidence: bool = True,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    locator_list = sorted(set(locator for locator in locators if locator))
    authority_list = sorted(set(authority_classes))
    result: dict[str, Any] = {
        "comparison_id": _stable_id("comparison", rule_id, subject_type, subject_id),
        "subject_type": subject_type,
        "subject_id": subject_id,
        "classification": classification,
        "expected_state": expected,
        "observed_state": observed,
        "evidence_locators": locator_list,
        "authority_classes": authority_list,
        "branch": branch,
        "commit": commit,
        "rule_id": rule_id,
        "severity": severity,
        "confidence": 1.0 if classification not in {"conflicting", "insufficient_evidence"} else 0.0,
        "confidence_basis": deterministic_confidence_basis(
            classification=classification,
            rule_id=rule_id,
            evidence_count=len(locator_list),
            required_evidence=required_evidence,
        ),
        "blocking": blocking,
        "explanation": explanation,
        "owner_review_required": owner_review_required,
        "next_deterministic_check": next_check,
    }
    if extra:
        result.update(extra)
    return result


def _record_is_current_and_trusted(record: dict[str, Any]) -> bool:
    return (
        record.get("authority_class") in _TRUSTED_IMPLEMENTATION_AUTHORITIES
        and record.get("lifecycle", {}).get("status") not in {
            "historical", "superseded", "retired",
        }
    )


def _task_linked_record_ids(
    task_record: dict[str, Any], plan_inputs: dict[str, Any]
) -> set[str]:
    """Return records with an explicit, current structured link to a task."""
    task_id = task_record.get("task_id", "")
    linked = {task_record.get("id", "")}
    for container in plan_inputs.get("registries", {}).values():
        records = container.get("records", []) if isinstance(container, dict) else []
        for record in records:
            if not isinstance(record, dict) or not _record_is_current_and_trusted(record):
                continue
            related = (
                record.get("associated_task_id") == task_id
                or task_id in record.get("associated_tasks", [])
                or task_id in record.get("affected_tasks", [])
            )
            if related:
                linked.add(record.get("id", ""))
    return {value for value in linked if value}


def _is_delivery_source(source: dict[str, Any], *, direct_task_link: bool) -> bool:
    """Classify one task-linked locator as tracked delivery implementation."""
    path = source.get("path", "")
    if not (
        source.get("safe")
        and source.get("exists")
        and source.get("regular_file", source.get("exists"))
        and source.get("tracked")
        and source.get("authority_class") in _TRUSTED_IMPLEMENTATION_AUTHORITIES
    ):
        return False
    if path == "AGENTS.md":
        return direct_task_link
    return path.startswith(_DELIVERY_ROOTS)


def _implementation_assessment(
    task_record: dict[str, Any],
    plan_inputs: dict[str, Any],
    implementation: dict[str, Any],
) -> dict[str, Any]:
    """Assess implementation from explicit tracked delivery relationships."""
    task_record_id = task_record.get("id", "")
    linked_ids = _task_linked_record_ids(task_record, plan_inputs)
    deliveries = sorted({
        source.get("path", "")
        for source in implementation.get("source_records", [])
        if source.get("record_id") in linked_ids
        and _is_delivery_source(
            source, direct_task_link=source.get("record_id") == task_record_id
        )
    })
    accepted_evidence_ids = sorted(
        record.get("id", "")
        for record in _registry_records(plan_inputs, "evidence")
        if record.get("associated_task_id") == task_record.get("task_id")
        and _record_is_current_and_trusted(record)
    )
    accepted = bool(
        accepted_evidence_ids
        or task_record.get("provenance", {}).get("accepted_by")
    )
    return {
        "implementation_present": bool(deliveries and accepted),
        "tracked_delivery_artifacts": deliveries,
        "accepted_evidence_present": accepted,
        "accepted_evidence_ids": accepted_evidence_ids,
    }


def _implementation_present(
    record: dict[str, Any],
    plan_inputs: dict[str, Any],
    implementation: dict[str, Any],
) -> bool:
    return _implementation_assessment(
        record, plan_inputs, implementation
    )["implementation_present"]


def _next_actionable(tasks: list[dict[str, Any]]) -> str | None:
    by_id = {record.get("task_id"): record for record in tasks}
    for number in range(1, 12):
        task_id = f"PHASE8-IMPL-026-T{number:03d}"
        record = by_id.get(task_id)
        if not record or task_id in _DEFERRED_PROJECT_MEMORY_TASKS:
            continue
        if record.get("lifecycle", {}).get("status") != "planned":
            continue
        dependencies = record.get("depends_on", [])
        if all(by_id.get(dep, {}).get("lifecycle", {}).get("status") == "complete" for dep in dependencies):
            return task_id
    return None


def _no_next_project_memory_contract(
    plan_inputs: dict[str, Any], tasks: list[dict[str, Any]]
) -> tuple[bool, list[str]]:
    """Validate the explicit closed-parent state that permits a null next task."""
    reasons: list[str] = []
    by_task = {record.get("task_id"): record for record in tasks}
    parent = by_task.get(_PROJECT_MEMORY_PARENT)
    if not parent or parent.get("lifecycle", {}).get("status") != "complete":
        reasons.append("project_memory_parent_not_complete")
    else:
        parent_notes = str(parent.get("notes", "")).casefold()
        if "closed" not in parent_notes or "operational procedure" not in parent_notes:
            reasons.append("project_memory_parent_closeout_not_explicit")

    for number in range(1, 12):
        task_id = f"PHASE8-IMPL-026-T{number:03d}"
        record = by_task.get(task_id)
        if record is None:
            reasons.append(f"required_child_missing:{task_id}")
            continue
        lifecycle = record.get("lifecycle", {}).get("status")
        if task_id in _DEFERRED_PROJECT_MEMORY_TASKS:
            notes = str(record.get("notes", "")).casefold()
            owner_ref = record.get("provenance", {}).get("owner_decision_ref")
            if lifecycle != "planned" or not all(
                token in notes for token in ("owner-deferred", "contingent", "inactive", "unimplemented")
            ) or owner_ref != "owner-decision:t006-t007-no-measured-gap-deferral":
                reasons.append(f"contingent_child_not_owner_deferred:{task_id}")
        elif lifecycle != "complete":
            reasons.append(f"required_child_not_complete:{task_id}")

    owner_decisions = {
        record.get("id"): record
        for record in _registry_records(plan_inputs, "owner-decisions")
    }
    deferral = owner_decisions.get("owner-decision:t006-t007-no-measured-gap-deferral", {})
    if not _record_is_current_and_trusted(deferral) or not _DEFERRED_PROJECT_MEMORY_TASKS <= set(
        deferral.get("affected_tasks", [])
    ):
        reasons.append("owner_deferral_evidence_missing")
    cadence = owner_decisions.get("owner-decision:q154-event-driven-commit-bound-cadence", {})
    if (
        not _record_is_current_and_trusted(cadence)
        or cadence.get("provenance", {}).get("accepted_by") != "owner"
        or _PROJECT_MEMORY_PARENT not in cadence.get("affected_tasks", [])
        or "PHASE8-IMPL-026-T011" not in cadence.get("affected_tasks", [])
    ):
        reasons.append("q154_owner_decision_missing")

    closeout_evidence = [
        record for record in _registry_records(plan_inputs, "evidence")
        if record.get("associated_task_id") == "PHASE8-IMPL-026-T011"
        and _record_is_current_and_trusted(record)
    ]
    if not closeout_evidence:
        reasons.append("t011_accepted_evidence_missing")

    enrichment = plan_inputs.get("roadmap", {}).get(
        "docs/roadmap/enrichment/PHASE8-IMPL-026.enrichment.json", {}
    )
    if not isinstance(enrichment, dict):
        reasons.append("enrichment_missing_or_malformed")
    else:
        maintenance = enrichment.get("project_memory_maintenance")
        if maintenance != {
            "implementation_task": None,
            "mode": "operational_procedure",
            "procedure_task_id": "PHASE8-IMPL-026-T011",
        }:
            reasons.append("operational_maintenance_declaration_missing")
        if enrichment.get("status") != "complete/PASS-WITH-FINDINGS":
            reasons.append("enrichment_parent_closeout_mismatch")
        if "operational" not in str(enrichment.get("next_operational_step", "")).casefold():
            reasons.append("enrichment_operational_step_missing")

    roadmap = plan_inputs.get("roadmap", {})
    for path, tokens in _NO_NEXT_ROADMAP_TOKENS.items():
        value = roadmap.get(path)
        text = value.casefold() if isinstance(value, str) else ""
        if not all(token in text for token in tokens):
            reasons.append(f"roadmap_closeout_mismatch:{path}")
    return not reasons, sorted(reasons)


def _expected_application_frontier(
    plan_inputs: dict[str, Any], tasks: list[dict[str, Any]]
) -> tuple[str | None, bool, list[str]]:
    """Return the authoritative application frontier independently of PM sequencing."""
    reasons: list[str] = []
    enrichment = plan_inputs.get("roadmap", {}).get(
        "docs/roadmap/enrichment/PHASE8-IMPL-026.enrichment.json", {}
    )
    expected = (
        enrichment.get("application_frontier_next_task")
        if isinstance(enrichment, dict)
        else None
    )
    if not isinstance(expected, str) or not expected.strip():
        return None, False, ["application_frontier_declaration_missing"]

    by_task = {record.get("task_id"): record for record in tasks}
    record = by_task.get(expected)
    if record is None:
        reasons.append("application_frontier_task_missing")
    else:
        if record.get("is_application_frontier") is not True:
            reasons.append("application_frontier_task_not_marked")
        if record.get("lifecycle", {}).get("status") not in {"planned", "in_progress"}:
            reasons.append("application_frontier_task_not_actionable")

    def is_descendant(record: dict[str, Any], parent_task_id: str) -> bool:
        seen: set[str] = set()
        current = record.get("parent_task_id")
        while isinstance(current, str) and current not in seen:
            if current == parent_task_id:
                return True
            seen.add(current)
            current = by_task.get(current, {}).get("parent_task_id")
        return False

    declared_children = sorted(
        record.get("task_id")
        for record in tasks
        if is_descendant(record, "PHASE8-IMPL-024")
        and record.get("is_application_frontier") is True
    )
    if declared_children != [expected]:
        reasons.append("application_frontier_registry_mismatch")
    return expected, not reasons, sorted(reasons)


def _declared_next_actionable(
    plan_inputs: dict[str, Any], tasks: list[dict[str, Any]]
) -> tuple[str | None, bool, str, list[str]]:
    enrichment = plan_inputs.get("roadmap", {}).get(
        "docs/roadmap/enrichment/PHASE8-IMPL-026.enrichment.json", {}
    )
    if not isinstance(enrichment, dict) or "next_project_memory_task" not in enrichment:
        return None, False, "missing", ["next_project_memory_task_missing"]
    value = enrichment["next_project_memory_task"]
    if value is None:
        valid, reasons = _no_next_project_memory_contract(plan_inputs, tasks)
        return None, valid, "explicit_null", reasons
    if not isinstance(value, str) or not value.strip():
        return None, False, "invalid", ["next_project_memory_task_must_be_task_id_or_null"]
    for number in range(1, 12):
        task_id = f"PHASE8-IMPL-026-T{number:03d}"
        if task_id in value:
            return task_id, True, "task_id", []
    return None, False, "invalid", ["next_project_memory_task_unknown"]


def build_comparisons(
    plan_inputs: dict[str, Any], implementation_inputs: dict[str, Any]
) -> list[dict[str, Any]]:
    """Build deterministic accepted-plan versus implementation comparisons."""
    comparisons: list[dict[str, Any]] = []
    branch = implementation_inputs.get("branch", "")
    commit = implementation_inputs.get("commit", "")
    tasks = _registry_records(plan_inputs, "tasks")
    by_task = {record.get("task_id"): record for record in tasks}

    for task_id in [f"PHASE8-IMPL-026-T{number:03d}" for number in range(6, 12)]:
        record = by_task.get(task_id)
        if record is None:
            comparisons.append(_comparison(
                subject_type="task", subject_id=task_id,
                expected={"record": "required"}, observed={"record": "missing"},
                classification="insufficient_evidence", locators=[], authority_classes=[],
                branch=branch, commit=commit, rule_id="PI-TASK-001", severity="critical",
                blocking=True, explanation="Required bounded task record is missing.",
                owner_review_required=True, next_check="Restore and validate the tracked task record.",
            ))
            continue
        expected_lifecycle = record.get("lifecycle", {}).get("status")
        assessment = _implementation_assessment(
            record, plan_inputs, implementation_inputs
        )
        present = assessment["implementation_present"]
        observed_lifecycle = "complete" if present else "planned"
        if task_id in {"PHASE8-IMPL-026-T006", "PHASE8-IMPL-026-T007"}:
            observed_lifecycle = "planned"
        required_evidence_present = (
            expected_lifecycle != "complete" or present
        )
        classification = classify_claims(
            expected_lifecycle,
            observed_lifecycle,
            required_evidence_present=required_evidence_present,
        )
        comparisons.append(_comparison(
            subject_type="task", subject_id=task_id,
            expected={
                "lifecycle": expected_lifecycle,
                "parent": record.get("parent_task_id"),
                "dependencies": sorted(record.get("depends_on", [])),
                "contingent": task_id in {"PHASE8-IMPL-026-T006", "PHASE8-IMPL-026-T007"},
            },
            observed={
                "lifecycle": observed_lifecycle,
                "implementation_present": present,
                "tracked_delivery_artifacts": assessment["tracked_delivery_artifacts"],
                "accepted_evidence_present": assessment["accepted_evidence_present"],
                "accepted_evidence_ids": assessment["accepted_evidence_ids"],
                "inactive": expected_lifecycle == "planned",
            },
            classification=classification,
            locators=_record_locator_paths(record), authority_classes=[record.get("authority_class", "")],
            branch=branch, commit=commit, rule_id="PI-TASK-001",
            severity="error" if classification != "matching" else "info",
            blocking=classification != "matching",
            explanation=(
                "Accepted task lifecycle agrees with bounded tracked implementation evidence."
                if classification == "matching" else
                "Accepted task lifecycle and bounded tracked implementation evidence disagree."
            ),
            owner_review_required=classification != "matching",
            next_check="Re-read the task registry and its tracked implementation locators.",
            required_evidence=required_evidence_present,
        ))

    expected_next = _next_actionable(tasks)
    observed_next, declaration_valid, declaration_kind, declaration_reasons = (
        _declared_next_actionable(plan_inputs, tasks)
    )
    next_classification = classify_claims(
        expected_next, observed_next, required_evidence_present=declaration_valid
    )
    comparisons.append(_comparison(
        subject_type="sequence", subject_id="project-memory-next-actionable",
        expected={"task_id": expected_next}, observed={"task_id": observed_next},
        classification=next_classification,
        locators=["docs/project-memory/registries/tasks.json", "docs/roadmap/enrichment/PHASE8-IMPL-026.enrichment.json"],
        authority_classes=["authoritative"], branch=branch, commit=commit,
        rule_id="PI-TASK-002",
        severity="critical" if next_classification != "matching" else "info",
        blocking=next_classification != "matching",
        explanation="Next-actionable state is derived from lifecycle, dependency, and owner-deferral records.",
        owner_review_required=next_classification != "matching",
        next_check="Derive the next actionable task again from validated task and dependency records.",
        required_evidence=declaration_valid,
        extra={
            "declaration": {
                "kind": declaration_kind,
                "valid": declaration_valid,
                "reasons": declaration_reasons,
            }
        },
    ))

    expected_frontier, frontier_declaration_valid, frontier_reasons = (
        _expected_application_frontier(plan_inputs, tasks)
    )
    roadmap_index = plan_inputs.get("roadmap", {}).get("docs/roadmap/roadmap_index.yaml", {})
    frontier = roadmap_index.get("active_frontier", {}) if isinstance(roadmap_index, dict) else {}
    observed_frontier = frontier.get("next_readiness_task_id") if isinstance(frontier, dict) else None
    frontier_class = classify_claims(
        expected_frontier, observed_frontier,
        required_evidence_present=(
            frontier_declaration_valid and observed_frontier is not None
        ),
    )
    comparisons.append(_comparison(
        subject_type="application_frontier", subject_id=expected_frontier or "application-frontier",
        expected={"task_id": expected_frontier}, observed={"task_id": observed_frontier},
        classification=frontier_class, locators=[
            "docs/project-memory/registries/tasks.json",
            "docs/roadmap/enrichment/PHASE8-IMPL-026.enrichment.json",
            "docs/roadmap/roadmap_index.yaml",
        ],
        authority_classes=["authoritative"], branch=branch, commit=commit,
        rule_id="PI-TASK-003", severity="critical" if frontier_class != "matching" else "info",
        blocking=frontier_class != "matching", explanation="Application frontier must match authoritative application sequencing.",
        owner_review_required=frontier_class != "matching",
        next_check="Inspect active_frontier.next_readiness_task_id in roadmap_index.yaml.",
        required_evidence=(frontier_declaration_valid and observed_frontier is not None),
        extra={
            "declaration": {
                "valid": frontier_declaration_valid,
                "reasons": frontier_reasons,
            }
        },
    ))

    impl025 = by_task.get("PHASE8-IMPL-025", {})
    impl025_status = impl025.get("lifecycle", {}).get("status")
    impl025_class = classify_claims("planned", impl025_status, required_evidence_present=bool(impl025))
    comparisons.append(_comparison(
        subject_type="task", subject_id="PHASE8-IMPL-025",
        expected={"lifecycle": "planned", "active": False},
        observed={"lifecycle": impl025_status, "active": impl025_status not in {"planned", None}},
        classification=impl025_class, locators=_record_locator_paths(impl025),
        authority_classes=[impl025.get("authority_class", "")], branch=branch, commit=commit,
        rule_id="PI-TASK-004", severity="critical" if impl025_class != "matching" else "info",
        blocking=impl025_class != "matching", explanation="PHASE8-IMPL-025 must remain published/planned and inactive.",
        owner_review_required=impl025_class != "matching",
        next_check="Inspect PHASE8-IMPL-025 accepted task and roadmap status.",
    ))

    boundaries = {record.get("boundary_id"): record for record in _registry_records(plan_inputs, "boundaries")}
    for boundary_id, meaning in sorted(_REQUIRED_BOUNDARIES.items()):
        record = boundaries.get(boundary_id)
        observed = bool(
            record
            and record.get("authority_class") == "authoritative"
            and record.get("lifecycle", {}).get("status") == "current"
            and record.get("is_non_negotiable") is True
        )
        classification = classify_claims(True, observed, required_evidence_present=record is not None)
        comparisons.append(_comparison(
            subject_type="product_boundary", subject_id=boundary_id,
            expected={"required": True, "meaning": meaning}, observed={"enforced": observed},
            classification=classification,
            locators=_record_locator_paths(record or {}),
            authority_classes=[(record or {}).get("authority_class", "")],
            branch=branch, commit=commit, rule_id="PI-BOUNDARY-001",
            severity="critical" if classification != "matching" else "info",
            blocking=classification != "matching",
            explanation=f"Required product boundary: {meaning}.",
            owner_review_required=classification != "matching",
            next_check="Validate the authoritative non-negotiable boundary record.",
        ))

    return sorted(comparisons, key=lambda item: (
        item["rule_id"], item["subject_type"], item["subject_id"], item["comparison_id"]
    ))


def _finding(
    *, rule_group: str, code: str, severity: str, subject_type: str,
    subject_id: str, classification: str, locators: Iterable[str], blocking: bool,
    explanation: str, owner_review_required: bool, next_check: str,
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    locator_list = sorted(set(value for value in locators if value))
    return {
        "finding_id": _stable_id("finding", rule_group, code, subject_type, subject_id, *locator_list),
        "rule_group": rule_group,
        "code": code,
        "severity": severity,
        "subject_type": subject_type,
        "subject_id": subject_id,
        "classification": classification,
        "evidence_locators": locator_list,
        "blocking": bool(blocking),
        "explanation": explanation,
        "owner_review_required": bool(owner_review_required),
        "next_deterministic_check": next_check,
        "evidence": evidence or {},
    }


def sort_findings(findings: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Sort by the T009 consolidated readiness ordering contract."""
    return sorted(findings, key=lambda item: (
        0 if item.get("blocking") else 1,
        _SEVERITY_RANK.get(item.get("severity", "info"), 99),
        item.get("rule_group", ""),
        item.get("subject_type", ""),
        item.get("subject_id", ""),
        item.get("code", ""),
        "|".join(item.get("evidence_locators", [])),
        item.get("finding_id", ""),
    ))


def _dependency_cycles(graph: dict[str, set[str]]) -> list[list[str]]:
    cycles: set[tuple[str, ...]] = set()
    visiting: list[str] = []
    visited: set[str] = set()

    def visit(node: str) -> None:
        if node in visiting:
            start = visiting.index(node)
            cycle = visiting[start:] + [node]
            core = cycle[:-1]
            rotations = [tuple(core[index:] + core[:index]) for index in range(len(core))]
            cycles.add(min(rotations) + (min(rotations)[0],))
            return
        if node in visited:
            return
        visiting.append(node)
        for target in sorted(graph.get(node, set())):
            visit(target)
        visiting.pop()
        visited.add(node)

    for node in sorted(graph):
        visit(node)
    return [list(cycle) for cycle in sorted(cycles)]


def run_plan_integrity_checks(
    plan_inputs: dict[str, Any],
    implementation_inputs: dict[str, Any],
    comparisons: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Run all bounded deterministic Plan Integrity rule groups."""
    comparisons = comparisons if comparisons is not None else build_comparisons(plan_inputs, implementation_inputs)
    findings: list[dict[str, Any]] = []

    if implementation_inputs.get("dirty"):
        findings.append(_finding(
            rule_group="evidence_traceability_integrity", code="working_tree_dirty",
            severity="critical", subject_type="repository", subject_id="worktree",
            classification="insufficient_evidence", locators=implementation_inputs.get("modified_paths", []) + implementation_inputs.get("untracked_paths", []),
            blocking=True, explanation="Plan Integrity publication requires a clean worktree.",
            owner_review_required=False, next_check="Commit authorized tracked changes and retry from clean HEAD.",
        ))
    if implementation_inputs.get("staged"):
        findings.append(_finding(
            rule_group="evidence_traceability_integrity", code="staging_not_empty",
            severity="critical", subject_type="repository", subject_id="index",
            classification="insufficient_evidence", locators=[], blocking=True,
            explanation="Plan Integrity publication requires empty staging.", owner_review_required=False,
            next_check="Commit the staged T009 change and retry from clean HEAD.",
        ))
    if not implementation_inputs.get("branch_matches", True):
        findings.append(_finding(
            rule_group="evidence_traceability_integrity", code="branch_mismatch", severity="critical",
            subject_type="repository", subject_id="branch", classification="diverging", locators=[".git/HEAD"],
            blocking=True, explanation="Repository branch does not match the required branch binding.",
            owner_review_required=True, next_check="Verify the required branch and current symbolic HEAD.",
        ))
    if not implementation_inputs.get("commit_matches", True):
        findings.append(_finding(
            rule_group="evidence_traceability_integrity", code="commit_mismatch", severity="critical",
            subject_type="repository", subject_id="commit", classification="diverging", locators=[".git/HEAD"],
            blocking=True, explanation="Repository commit does not match the required full commit binding.",
            owner_review_required=True, next_check="Verify the required and observed full commit IDs.",
        ))
    registry_errors = [item for item in implementation_inputs.get("registry_validation_findings", []) if item.get("level") == "error"]
    if registry_errors:
        findings.append(_finding(
            rule_group="evidence_traceability_integrity", code="registry_validation_failed", severity="critical",
            subject_type="registry_bundle", subject_id="tracked-registries", classification="insufficient_evidence",
            locators=[item.get("registry_file", "") for item in registry_errors], blocking=True,
            explanation=f"Registry validation produced {len(registry_errors)} error(s).", owner_review_required=True,
            next_check="Run validate_registries.py and repair every error.", evidence={"errors": registry_errors},
        ))

    comparison_codes = {
        "application_frontier": "application_frontier_mismatch",
        "sequence": "next_actionable_mismatch",
    }
    for comparison in comparisons:
        if comparison["classification"] in {"matching", "superseded"}:
            continue
        code = comparison_codes.get(comparison["subject_type"], "task_state_mismatch")
        if comparison["subject_id"] == "PHASE8-IMPL-025":
            code = "ph8_impl_025_activated"
        findings.append(_finding(
            rule_group=("product_boundary_integrity" if comparison["subject_type"] == "product_boundary" else "task_state_convergence"),
            code=("product_boundary_violation" if comparison["subject_type"] == "product_boundary" else code),
            severity=comparison["severity"], subject_type=comparison["subject_type"],
            subject_id=comparison["subject_id"], classification=comparison["classification"],
            locators=comparison["evidence_locators"], blocking=comparison["blocking"],
            explanation=comparison["explanation"], owner_review_required=comparison["owner_review_required"],
            next_check=comparison["next_deterministic_check"],
            evidence={"comparison_id": comparison["comparison_id"]},
        ))

    tasks = _registry_records(plan_inputs, "tasks")
    task_by_id = {record.get("task_id"): record for record in tasks}
    graph: dict[str, set[str]] = defaultdict(set)
    for task in tasks:
        task_id = task.get("task_id", "")
        for dependency in task.get("depends_on", []):
            graph[task_id].add(dependency)
            if dependency not in task_by_id:
                findings.append(_finding(
                    rule_group="dependency_delivery_integrity", code="missing_required_dependency",
                    severity="critical", subject_type="task", subject_id=task_id,
                    classification="insufficient_evidence", locators=_record_locator_paths(task), blocking=True,
                    explanation=f"Required dependency {dependency} has no task record.", owner_review_required=True,
                    next_check="Restore the missing task record or correct the dependency declaration.",
                    evidence={"missing_dependency": dependency},
                ))
            elif task.get("lifecycle", {}).get("status") == "complete" and task_by_id[dependency].get("lifecycle", {}).get("status") != "complete":
                findings.append(_finding(
                    rule_group="dependency_delivery_integrity", code="completed_task_incomplete_dependency",
                    severity="critical", subject_type="task", subject_id=task_id, classification="diverging",
                    locators=_record_locator_paths(task) + _record_locator_paths(task_by_id[dependency]), blocking=True,
                    explanation=f"Completed task depends on incomplete prerequisite {dependency}.", owner_review_required=True,
                    next_check="Reconcile task completion with prerequisite lifecycle state.",
                    evidence={"dependency": dependency},
                ))
    for cycle in _dependency_cycles(graph):
        findings.append(_finding(
            rule_group="dependency_delivery_integrity", code="dependency_cycle", severity="critical",
            subject_type="dependency_graph", subject_id="->".join(cycle), classification="conflicting",
            locators=["docs/project-memory/registries/tasks.json", "docs/project-memory/registries/dependencies.json"],
            blocking=True, explanation="Task dependency graph contains a cycle.", owner_review_required=True,
            next_check="Remove or explicitly supersede one edge in the cycle.", evidence={"cycle": cycle},
        ))

    decisions = _registry_records(plan_inputs, "decisions")
    owner_decisions = _registry_records(plan_inputs, "owner-decisions")
    all_decisions = decisions + owner_decisions
    decision_by_id = {record.get("id"): record for record in all_decisions}
    supersession_graph: dict[str, set[str]] = defaultdict(set)
    current_claims: dict[str, list[dict[str, Any]]] = defaultdict(list)
    root = Path(implementation_inputs.get("repository_root", "."))
    for decision in all_decisions:
        decision_id = decision.get("id", "")
        path = decision.get("decision_path")
        if path and (not _safe_relative_path(path) or not (root / path).is_file()):
            findings.append(_finding(
                rule_group="decision_supersession_integrity", code="decision_locator_invalid",
                severity="critical", subject_type="decision", subject_id=decision_id,
                classification="insufficient_evidence", locators=[path], blocking=True,
                explanation="Decision path is unsafe or unavailable.", owner_review_required=True,
                next_check="Restore or correct the accepted decision locator.",
            ))
        for task_id in decision.get("affected_tasks", []):
            if task_id not in task_by_id:
                findings.append(_finding(
                    rule_group="decision_supersession_integrity", code="decision_task_reference_missing",
                    severity="error", subject_type="decision", subject_id=decision_id,
                    classification="insufficient_evidence", locators=_record_locator_paths(decision), blocking=True,
                    explanation=f"Decision references missing task {task_id}.", owner_review_required=True,
                    next_check="Restore the task record or correct affected_tasks.",
                ))
        lifecycle = decision.get("lifecycle", {})
        for target in lifecycle.get("supersedes", []):
            supersession_graph[decision_id].add(target)
            target_record = decision_by_id.get(target)
            if not target_record or target_record.get("lifecycle", {}).get("superseded_by") != decision_id:
                findings.append(_finding(
                    rule_group="decision_supersession_integrity", code="supersession_invalid",
                    severity="error", subject_type="decision", subject_id=decision_id,
                    classification="conflicting", locators=_record_locator_paths(decision), blocking=True,
                    explanation=f"Supersession target {target} is absent or not reciprocally linked.",
                    owner_review_required=True, next_check="Repair both sides of the supersession relationship.",
                ))
        if lifecycle.get("status") == "current" and decision.get("question"):
            current_claims[decision["question"]].append(decision)
    for cycle in _dependency_cycles(supersession_graph):
        findings.append(_finding(
            rule_group="decision_supersession_integrity", code="supersession_cycle",
            severity="critical", subject_type="decision_graph", subject_id="->".join(cycle),
            classification="conflicting", locators=[], blocking=True,
            explanation="Decision supersession graph contains a cycle.", owner_review_required=True,
            next_check="Repair the accepted supersession chain.", evidence={"cycle": cycle},
        ))
    for question, claim_records in current_claims.items():
        selected = {record.get("selected_option") for record in claim_records}
        ranks = {_AUTHORITY_RANK.get(record.get("authority_class", ""), 99) for record in claim_records}
        if len(selected) > 1 and len(ranks) == 1:
            findings.append(_finding(
                rule_group="decision_supersession_integrity", code="unresolved_authoritative_conflict",
                severity="critical", subject_type="decision_subject", subject_id=_stable_id("question", question),
                classification="conflicting", locators=[path for record in claim_records for path in _record_locator_paths(record)],
                blocking=True, explanation="Current equal-authority decision records disagree without resolution.",
                owner_review_required=True, next_check="Record an accepted resolution or explicit supersession.",
            ))

    source_by_record: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for source in implementation_inputs.get("source_records", []):
        source_by_record[source.get("record_id", "")].append(source)
        if not source.get("safe"):
            findings.append(_finding(
                rule_group="evidence_traceability_integrity", code="source_locator_invalid",
                severity="critical", subject_type="record", subject_id=source.get("record_id", ""),
                classification="insufficient_evidence", locators=[source.get("path", "")], blocking=True,
                explanation="Authoritative source locator is unsafe.", owner_review_required=True,
                next_check="Replace the locator with a repository-relative non-traversing path.",
            ))
        elif not source.get("exists"):
            findings.append(_finding(
                rule_group="evidence_traceability_integrity", code="source_missing",
                severity="warning", subject_type="record", subject_id=source.get("record_id", ""),
                classification="insufficient_evidence", locators=[source.get("path", "")], blocking=False,
                explanation="A declared non-required source is unavailable in this branch.", owner_review_required=False,
                next_check="Inspect the source on its owning branch or update the historical locator.",
            ))
    for task in tasks:
        if task.get("lifecycle", {}).get("status") != "complete":
            continue
        sources = source_by_record.get(task.get("id", ""), [])
        if not any(source.get("exists") and source.get("safe") for source in sources):
            findings.append(_finding(
                rule_group="evidence_traceability_integrity", code="completed_task_missing_required_evidence",
                severity="critical", subject_type="task", subject_id=task.get("task_id", ""),
                classification="insufficient_evidence", locators=[source.get("path", "") for source in sources],
                blocking=True, explanation="Completed task has no available required tracked source evidence.",
                owner_review_required=True, next_check="Restore at least one accepted tracked implementation or decision source.",
            ))

    all_records = [
        record for container in plan_inputs.get("registries", {}).values()
        if isinstance(container, dict) for record in container.get("records", []) if isinstance(record, dict)
    ]
    ids: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in all_records:
        ids[record.get("id", "")].append(record)
        if record.get("authority_class") == "generated_evidence" and record.get("type") != "evidence":
            findings.append(_finding(
                rule_group="evidence_traceability_integrity", code="generated_evidence_claims_authority",
                severity="critical", subject_type=record.get("type", "record"), subject_id=record.get("id", ""),
                classification="conflicting", locators=_record_locator_paths(record), blocking=True,
                explanation="Generated evidence is not eligible to claim tracked project authority.", owner_review_required=True,
                next_check="Quarantine the record as evidence-only and restore authoritative tracked truth.",
            ))
    for record_id, records in ids.items():
        if record_id and len(records) > 1:
            findings.append(_finding(
                rule_group="exact_duplicate_overlap_integrity", code="duplicate_record_id", severity="critical",
                subject_type="record", subject_id=record_id, classification="conflicting",
                locators=[path for record in records for path in _record_locator_paths(record)], blocking=True,
                explanation="The exact stable record ID is owned by more than one record.", owner_review_required=True,
                next_check="Preserve one stable owner and explicitly supersede or rename the duplicate.",
                evidence={"overlap_outcome": "REFACTOR"},
            ))

    for registry_name, key in (("assets", "asset_path"), ("tools", "tool_path")):
        ownership: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for record in _registry_records(plan_inputs, registry_name):
            if record.get(key):
                ownership[record[key]].append(record)
        for owned_path, records in ownership.items():
            if len(records) > 1:
                findings.append(_finding(
                    rule_group="exact_duplicate_overlap_integrity", code="exact_ownership_conflict",
                    severity="error", subject_type=registry_name[:-1], subject_id=owned_path,
                    classification="conflicting", locators=[owned_path], blocking=True,
                    explanation="Two current records claim exact ownership of the same path.", owner_review_required=True,
                    next_check="Choose REUSE, EXTEND, REFACTOR, SUPERSEDE, or KEEP_SEPARATE with traceable ownership.",
                    evidence={"record_ids": sorted(record.get("id", "") for record in records), "overlap_outcome": "REFACTOR"},
                ))

    capability_keys: dict[tuple[str, tuple[str, ...]], list[dict[str, Any]]] = defaultdict(list)
    for capability in _registry_records(plan_inputs, "capabilities"):
        exact_key = (capability.get("title", ""), tuple(sorted(capability.get("associated_tasks", []))))
        capability_keys[exact_key].append(capability)
    for exact_key, records in capability_keys.items():
        if exact_key[0] and len(records) > 1:
            findings.append(_finding(
                rule_group="exact_duplicate_overlap_integrity", code="exact_capability_overlap",
                severity="warning", subject_type="capability", subject_id=exact_key[0],
                classification="matching", locators=[path for record in records for path in _record_locator_paths(record)],
                blocking=False, explanation="Exact capability title and associated-task set overlap deterministically.",
                owner_review_required=False, next_check="Reuse the existing capability unless an explicit extension is required.",
                evidence={"record_ids": sorted(record.get("id", "") for record in records), "overlap_outcome": "REUSE"},
            ))

    ordered = sort_findings(findings)
    return {
        "engine_name": ENGINE_NAME,
        "engine_version": ENGINE_VERSION,
        "finding_count": len(ordered),
        "findings": ordered,
        "by_code": dict(sorted(Counter(item["code"] for item in ordered).items())),
        "by_severity": dict(sorted(Counter(item["severity"] for item in ordered).items())),
        "blocking_count": sum(1 for item in ordered if item["blocking"]),
        "conflict_count": sum(1 for item in ordered if item["classification"] == "conflicting"),
        "insufficient_evidence_count": sum(1 for item in ordered if item["classification"] == "insufficient_evidence"),
    }


def derive_readiness(findings: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Derive READY, READY_WITH_ADVISORIES, or BLOCKED exactly."""
    items = list(findings)
    blocking = [item for item in items if item.get("blocking")]
    if blocking:
        result = "BLOCKED"
        explanation = "At least one deterministic blocking condition exists."
    elif items:
        result = "READY_WITH_ADVISORIES"
        explanation = "Only nonblocking information or warnings remain."
    else:
        result = "READY"
        explanation = "No unresolved blocking, error, critical, required conflict, or required insufficient-evidence finding exists."
    return {
        "result": result,
        "ready": result != "BLOCKED",
        "blocking_count": len(blocking),
        "advisory_count": len(items) - len(blocking),
        "finding_count": len(items),
        "explanation": explanation,
        "rule": "PI-READINESS-001",
    }


def comparison_counts(comparisons: Iterable[dict[str, Any]]) -> dict[str, int]:
    counts = Counter(item.get("classification", "") for item in comparisons)
    return {name: counts.get(name, 0) for name in CLASSIFICATIONS}
