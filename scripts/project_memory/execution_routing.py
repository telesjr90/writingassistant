#!/usr/bin/env python3
"""Validate and resolve the owner-approved remaining-MVP execution routing.

The tracked routing registry is the only executor-selection input. Roadmap
status and dependencies remain authoritative for eligibility; routing never
changes task lifecycle, order, authority, or acceptance.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
ROUTING_PATH = ROOT / "docs" / "project-memory" / "registries" / "execution-routing.json"
ROADMAP_PATH = ROOT / "docs" / "roadmap" / "roadmap_index.yaml"
ROUTING_SOURCE = "docs/project-memory/registries/execution-routing.json"
CURRENT_DECISION = (
    "docs/roadmap/decisions/"
    "PHASE8-IMPL-026-T012-current-truth-execution-routing-and-ui-guidance.md"
)
HISTORICAL_ROUTING_DECISION = (
    "docs/roadmap/decisions/"
    "PHASE8-IMPL-023-opencode-go-model-routing-and-small-task-execution.md"
)
UI_SKILL = "writing-assistant-ui-execution"

EXECUTION_CLASSES = {
    "codex_gpt_5_6_sol",
    "opencode_go",
    "owner_decision",
}
MODEL_CATEGORIES = {
    "gpt_5_6_sol",
    "opencode_go_narrow_tests_first",
    "opencode_go_strongest_suitable",
    "owner_only",
}
REASONING_LEVELS = {"focused", "high", "owner"}
RISK_CLASSES = {"moderate", "high", "critical", "owner_only"}
COMPLETE_STATUSES = {"complete", "done", "historical", "superseded"}
UI_CAPABILITY_TAGS = {
    "frontend_ui",
    "ui_audit",
    "ui_implementation",
    "ui_validation",
    "accessibility",
    "responsive_ui",
    "browser_ui",
}
REQUIRED_RECORD_FIELDS = (
    "task_id",
    "execution_class",
    "model_category",
    "reasoning_level",
    "risk_class",
    "rationale",
    "escalation_conditions",
    "owner_only",
    "authoritative_source_locator",
    "applicability_scope_id",
    "capability_tags",
    "required_skills",
    "delegation_eligible",
)


class RoutingResolutionError(ValueError):
    """Fail-closed routing resolution error with a structured finding."""

    def __init__(self, finding: dict[str, Any]):
        self.finding = finding
        super().__init__(finding["message"])


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain one JSON object")
    return data


def _finding(
    rule_id: str,
    file: str,
    locator: str,
    offending_value: Any,
    expected_value: Any,
    classification: str,
    next_action: str,
    message: str,
) -> dict[str, Any]:
    return {
        "rule_id": rule_id,
        "file": file,
        "locator": locator,
        "offending_value": offending_value,
        "expected_value": expected_value,
        "classification": classification,
        "next_action": next_action,
        "message": message,
    }


def _git_branch(root: Path) -> str:
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=root,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    branch = result.stdout.strip()
    if branch or os.environ.get("GITHUB_ACTIONS") != "true":
        return branch
    event_branch = os.environ.get("GITHUB_HEAD_REF") or os.environ.get("GITHUB_REF_NAME")
    event_sha = os.environ.get("GITHUB_SHA", "")
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout.strip()
    if event_branch and event_sha == head:
        return event_branch
    return ""


def _roadmap_by_id(roadmap: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        item["id"]: item
        for item in roadmap.get("tasks", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }


def _belongs_to_roots(
    task_id: str,
    roots: set[str],
    tasks: dict[str, dict[str, Any]],
) -> bool:
    seen: set[str] = set()
    current = task_id
    while current and current not in seen:
        if current in roots:
            return True
        seen.add(current)
        parent = tasks.get(current, {}).get("parent")
        current = parent if isinstance(parent, str) else ""
    return False


def remaining_mvp_task_ids(roadmap: dict[str, Any]) -> list[str]:
    """Derive the active/planned remaining-MVP task set from roadmap authority."""
    tasks = _roadmap_by_id(roadmap)
    roots = set(
        roadmap.get("active_frontier", {}).get("remaining_mvp_parent_task_ids", [])
    )
    return sorted(
        task_id
        for task_id, item in tasks.items()
        if item.get("status") not in COMPLETE_STATUSES
        and _belongs_to_roots(task_id, roots, tasks)
    )


def is_ui_related(task: dict[str, Any], route: dict[str, Any] | None) -> bool:
    """Classify UI scope from explicit metadata before any title fallback."""
    boundary_tags = set(task.get("boundary_tags", []))
    capability_tags = set((route or {}).get("capability_tags", []))
    if "review_ui_planning" in boundary_tags:
        return True
    if capability_tags & UI_CAPABILITY_TAGS:
        return True
    if any(
        scope == "frontend/" or scope.startswith("frontend/")
        for scope in (route or {}).get("allowed_path_prefixes", [])
    ):
        return True
    validation = set((route or {}).get("validation_requirements", []))
    if validation & {"playwright", "accessibility", "responsive_widths", "keyboard"}:
        return True
    title = str(task.get("title", "")).lower()
    return any(token in title for token in ("frontend", " ui", "responsive", "accessibility"))


def _active_records(registry: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        record
        for record in registry.get("records", [])
        if isinstance(record, dict)
        and record.get("lifecycle", {}).get("status") == "current"
    ]


def _mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def _records_for_task(
    registry: dict[str, Any], task_id: str
) -> list[dict[str, Any]]:
    return [record for record in _active_records(registry) if record.get("task_id") == task_id]


def _resolution_error(
    rule_id: str,
    task_id: str,
    offending: Any,
    expected: Any,
    classification: str,
    next_action: str,
    message: str,
) -> RoutingResolutionError:
    return RoutingResolutionError(
        _finding(
            rule_id,
            ROUTING_SOURCE,
            f"task_id={task_id}",
            offending,
            expected,
            classification,
            next_action,
            message,
        )
    )


def _resolve_record(
    registry: dict[str, Any],
    roadmap: dict[str, Any],
    task_id: str,
) -> tuple[dict[str, Any], str]:
    tasks = _roadmap_by_id(roadmap)
    direct = _records_for_task(registry, task_id)
    if len(direct) > 1:
        raise _resolution_error(
            "ROUTING-008",
            task_id,
            len(direct),
            1,
            "conflicting_current_routing",
            "Retain exactly one current routing record for the task.",
            f"Task {task_id} has multiple current routing records.",
        )
    parent_id = tasks.get(task_id, {}).get("parent")
    parent_records = _records_for_task(registry, parent_id) if parent_id else []
    parent_record = parent_records[0] if len(parent_records) == 1 else None

    if direct:
        record = direct[0]
        inheritance = _mapping((parent_record or {}).get("inheritance"))
        eligible_children = _string_list(inheritance.get("eligible_children"))
        if inheritance.get("enabled") and task_id in eligible_children:
            differs = any(
                record.get(field) != parent_record.get(field)
                for field in (
                    "execution_class",
                    "model_category",
                    "reasoning_level",
                    "risk_class",
                    "rationale",
                    "escalation_conditions",
                    "owner_only",
                    "applicability_scope_id",
                    "capability_tags",
                    "required_skills",
                )
            )
            valid_override = (
                inheritance.get("allow_explicit_overrides") is True
                and _mapping(record.get("parent_override")).get("enabled") is True
                and bool(_mapping(record.get("parent_override")).get("rationale"))
            )
            if differs and not valid_override:
                raise _resolution_error(
                    "ROUTING-004",
                    task_id,
                    "parent/child disagreement",
                    "explicit parent_override with rationale",
                    "ambiguous_parent_child_routing",
                    "Add a valid explicit child override or remove the conflict.",
                    f"Task {task_id} conflicts with inherited parent routing without a valid override.",
                )
        return record, "explicit"

    if not parent_record:
        raise _resolution_error(
            "ROUTING-007",
            task_id,
            None,
            "one explicit record or provably safe parent inheritance",
            "missing_current_routing",
            "Add an applicable current routing record.",
            f"Task {task_id} has no current routing record.",
        )
    inheritance = _mapping(parent_record.get("inheritance"))
    if not inheritance.get("enabled") or task_id not in _string_list(inheritance.get("eligible_children")):
        raise _resolution_error(
            "ROUTING-007",
            task_id,
            None,
            "explicit record or listed safe inheritance",
            "missing_current_routing",
            "Add an explicit route or list the child in safe inheritance metadata.",
            f"Task {task_id} is not covered by safe parent inheritance.",
        )
    if any(item.get("parent") == task_id for item in tasks.values()):
        raise _resolution_error(
            "ROUTING-005",
            task_id,
            "aggregate child",
            "allowlisted leaf task",
            "unsafe_parent_inheritance",
            "Add an explicit nondelegable aggregate route or inherit only to a leaf task.",
            f"Task {task_id} cannot inherit an executor route because it is not a leaf task.",
        )
    if parent_record.get("owner_only") or "owner_review_required" in set(
        tasks.get(task_id, {}).get("boundary_tags", [])
    ):
        raise _resolution_error(
            "ROUTING-005",
            task_id,
            "owner boundary",
            "explicit owner-only route",
            "unsafe_parent_inheritance",
            "Create an explicit owner-only routing record.",
            f"Task {task_id} cannot inherit across an owner-only boundary.",
        )
    inherited = dict(parent_record)
    inherited["task_id"] = task_id
    inherited["inherited_from_task_id"] = parent_record["task_id"]
    inherited["authoritative_source_locator"] = dict(
        parent_record["authoritative_source_locator"]
    )
    # Aggregate records remain nondelegable, but their exact allowlisted leaf
    # children are delegable after the inheritance and owner-boundary checks
    # above. Execution eligibility is still evaluated separately from the
    # child's own lifecycle, dependencies, and active-frontier status.
    inherited["delegation_eligible"] = True
    return inherited, "inherited"


def validate_execution_routing(
    repo_root: str | Path = ROOT,
    *,
    registry: dict[str, Any] | None = None,
    roadmap: dict[str, Any] | None = None,
    current_branch: str | None = None,
) -> dict[str, Any]:
    """Return deterministic routing and UI-policy validation findings."""
    root = Path(repo_root).resolve()
    registry = registry if registry is not None else _load_json(root / ROUTING_SOURCE)
    roadmap = roadmap if roadmap is not None else _load_json(root / "docs/roadmap/roadmap_index.yaml")
    current_branch = current_branch if current_branch is not None else _git_branch(root)
    findings: list[dict[str, Any]] = []
    metadata = registry.get("metadata", {})
    scope_id = metadata.get("scope_id")

    expected_metadata = {
        "contract_schema_version": "execution-routing.v1",
        "status": "current",
        "effective_branch": current_branch,
        "commit_binding_mode": "containing_tracked_commit",
        "decision_path": CURRENT_DECISION,
    }
    for key, expected in expected_metadata.items():
        actual = metadata.get(key)
        if actual != expected:
            findings.append(_finding(
                "ROUTING-001",
                ROUTING_SOURCE,
                f"/metadata/{key}",
                actual,
                expected,
                "stale_or_inapplicable_routing_scope",
                "Update the current routing scope metadata from the accepted decision.",
                f"Routing metadata {key} is not current/applicable.",
            ))
    if HISTORICAL_ROUTING_DECISION not in metadata.get("historical_scopes_preserved", []):
        findings.append(_finding(
            "ROUTING-010",
            ROUTING_SOURCE,
            "/metadata/historical_scopes_preserved",
            metadata.get("historical_scopes_preserved"),
            [HISTORICAL_ROUTING_DECISION],
            "historical_scope_not_preserved",
            "Record the PHASE8-IMPL-023 decision as historical scope only.",
            "Historical PHASE8-IMPL-023 routing applicability is not preserved explicitly.",
        ))

    tasks = _roadmap_by_id(roadmap)
    remaining = remaining_mvp_task_ids(roadmap)
    active_records = _active_records(registry)
    current_task_ids = [
        record["task_id"]
        for record in active_records
        if isinstance(record.get("task_id"), str)
    ]

    for index, record in enumerate(active_records):
        locator = f"/records/{index}"
        for field in REQUIRED_RECORD_FIELDS:
            if field not in record:
                findings.append(_finding(
                    "ROUTING-002", ROUTING_SOURCE, f"{locator}/{field}", None,
                    "required field", "malformed_routing_record",
                    "Add the required routing field.",
                    f"Routing record for {record.get('task_id')} is missing {field}.",
                ))
        task_id = record.get("task_id")
        shape_checks = (
            ("rationale", isinstance(record.get("rationale"), str) and bool(record.get("rationale", "").strip()), "non-empty string"),
            ("escalation_conditions", isinstance(record.get("escalation_conditions"), list) and bool(record.get("escalation_conditions")) and len(_string_list(record.get("escalation_conditions"))) == len(record.get("escalation_conditions", [])) and all(item.strip() for item in _string_list(record.get("escalation_conditions"))), "non-empty list of non-empty strings"),
            ("owner_only", isinstance(record.get("owner_only"), bool), "boolean"),
            ("delegation_eligible", isinstance(record.get("delegation_eligible"), bool), "boolean"),
            ("capability_tags", isinstance(record.get("capability_tags"), list) and len(_string_list(record.get("capability_tags"))) == len(record.get("capability_tags", [])), "list of strings"),
            ("required_skills", isinstance(record.get("required_skills"), list) and len(_string_list(record.get("required_skills"))) == len(record.get("required_skills", [])), "list of strings"),
            ("inheritance", isinstance(record.get("inheritance"), dict), "object"),
        )
        for field, valid, expected_shape in shape_checks:
            if not valid:
                findings.append(_finding(
                    "ROUTING-002", ROUTING_SOURCE, f"{locator}/{field}",
                    record.get(field), expected_shape, "malformed_routing_record",
                    "Correct the field shape in the canonical routing registry.",
                    f"Routing record {task_id} has malformed {field}.",
                ))
        if task_id not in remaining:
            findings.append(_finding(
                "ROUTING-009", ROUTING_SOURCE, f"{locator}/task_id", task_id,
                "an active/planned remaining-MVP task",
                "stale_current_routing_record",
                "Mark completed/out-of-scope routing historical or remove it from the current scope.",
                f"Current routing record {task_id!r} is outside the remaining-MVP task set.",
            ))
        if record.get("applicability_scope_id") != scope_id:
            findings.append(_finding(
                "ROUTING-001", ROUTING_SOURCE, f"{locator}/applicability_scope_id",
                record.get("applicability_scope_id"), scope_id,
                "stale_or_inapplicable_routing_record",
                "Bind the record to the current routing scope.",
                f"Routing record {task_id} belongs to another scope.",
            ))
        expected_sets = (
            ("execution_class", EXECUTION_CLASSES),
            ("model_category", MODEL_CATEGORIES),
            ("reasoning_level", REASONING_LEVELS),
            ("risk_class", RISK_CLASSES),
        )
        for field, allowed in expected_sets:
            if record.get(field) not in allowed:
                findings.append(_finding(
                    "ROUTING-002", ROUTING_SOURCE, f"{locator}/{field}",
                    record.get(field), sorted(allowed), "malformed_routing_record",
                    "Use one allowed normalized routing value.",
                    f"Routing record {task_id} has invalid {field}.",
                ))
        expected_owner = record.get("execution_class") == "owner_decision"
        if record.get("owner_only") is not expected_owner:
            findings.append(_finding(
                "ROUTING-006", ROUTING_SOURCE, f"{locator}/owner_only",
                record.get("owner_only"), expected_owner,
                "owner_only_executor_mismatch",
                "Make owner_only and execution_class consistent.",
                f"Routing record {task_id} misstates owner-only status.",
            ))
        provides_inheritance = _mapping(record.get("inheritance")).get("enabled") is True
        if (provides_inheritance or expected_owner) and record.get("delegation_eligible") is not False:
            findings.append(_finding(
                "ROUTING-012", ROUTING_SOURCE, f"{locator}/delegation_eligible",
                record.get("delegation_eligible"), False,
                "delegation_eligibility_mismatch",
                "Keep inheritance-providing aggregate records and owner-only tasks nondelegable.",
                f"Routing record {task_id} misstates delegation eligibility for its own task type.",
            ))
        source = _mapping(record.get("authoritative_source_locator"))
        if source.get("path") != ROUTING_SOURCE or source.get("symbol") != task_id:
            findings.append(_finding(
                "ROUTING-003", ROUTING_SOURCE, f"{locator}/authoritative_source_locator",
                source, {"path": ROUTING_SOURCE, "symbol": task_id},
                "invalid_authoritative_source_locator",
                "Point the record to its committed routing-registry symbol.",
                f"Routing record {task_id} lacks its committed source locator.",
            ))
        task = tasks.get(task_id, {})
        if task and is_ui_related(task, record) and UI_SKILL not in record.get("required_skills", []):
            findings.append(_finding(
                "UI-001", ROUTING_SOURCE, f"{locator}/required_skills",
                record.get("required_skills"), [UI_SKILL],
                "ui_task_missing_impeccable_wrapper",
                "Add the shared UI execution skill requirement.",
                f"UI-related task {task_id} does not require the shared Impeccable wrapper.",
            ))

    for task_id in remaining:
        try:
            _resolve_record(registry, roadmap, task_id)
        except RoutingResolutionError as exc:
            findings.append(exc.finding)

    for task_id in sorted(set(current_task_ids)):
        if current_task_ids.count(task_id) > 1:
            findings.append(_finding(
                "ROUTING-008", ROUTING_SOURCE, f"task_id={task_id}",
                current_task_ids.count(task_id), 1,
                "conflicting_current_routing",
                "Retain exactly one current routing record.",
                f"Task {task_id} has conflicting active routing records.",
            ))

    unique = {
        json.dumps(item, sort_keys=True): item
        for item in findings
    }
    ordered = sorted(
        unique.values(),
        key=lambda item: (item["file"], item["locator"], item["rule_id"], item["message"]),
    )
    return {
        "result": "PASS" if not ordered else "BLOCKED",
        "routing_source": ROUTING_SOURCE,
        "scope_id": scope_id,
        "remaining_task_count": len(remaining),
        "explicit_record_count": len(active_records),
        "findings": ordered,
    }


def _dependency_eligible(task: dict[str, Any], tasks: dict[str, dict[str, Any]]) -> bool:
    return all(
        tasks.get(dep, {}).get("status") in {"complete", "done"}
        for dep in task.get("depends_on", [])
    )


def resolve_execution_route(
    task_id: str,
    *,
    repo_root: str | Path = ROOT,
    registry: dict[str, Any] | None = None,
    roadmap: dict[str, Any] | None = None,
    current_branch: str | None = None,
    delegated_executor: str | None = None,
    require_eligible: bool = True,
) -> dict[str, Any]:
    """Resolve exactly one applicable route and fail closed on ambiguity."""
    root = Path(repo_root).resolve()
    registry = registry if registry is not None else _load_json(root / ROUTING_SOURCE)
    roadmap = roadmap if roadmap is not None else _load_json(root / "docs/roadmap/roadmap_index.yaml")
    current_branch = current_branch if current_branch is not None else _git_branch(root)
    metadata = registry.get("metadata", {})
    if metadata.get("status") != "current" or metadata.get("effective_branch") != current_branch:
        raise _resolution_error(
            "ROUTING-001", task_id, metadata,
            {"status": "current", "effective_branch": current_branch},
            "stale_or_inapplicable_routing_scope",
            "Use a current routing registry applicable to this branch.",
            "Routing scope is stale or inapplicable.",
        )
    if metadata.get("decision_path") != CURRENT_DECISION:
        raise _resolution_error(
            "ROUTING-010", task_id, metadata.get("decision_path"), CURRENT_DECISION,
            "historical_routing_used_as_current",
            "Resolve from the accepted current routing decision.",
            "A historical routing scope cannot select the current executor.",
        )

    validation = validate_execution_routing(
        root,
        registry=registry,
        roadmap=roadmap,
        current_branch=current_branch,
    )
    if validation["findings"]:
        raise RoutingResolutionError(validation["findings"][0])

    tasks = _roadmap_by_id(roadmap)
    task = tasks.get(task_id)
    if task is None:
        raise _resolution_error(
            "ROUTING-007", task_id, None, "authoritative roadmap task",
            "unknown_task", "Publish the task in roadmap authority before routing it.",
            f"Task {task_id} is not present in the authoritative roadmap.",
        )
    record, resolution = _resolve_record(registry, roadmap, task_id)

    if record.get("owner_only") and delegated_executor is not None:
        raise _resolution_error(
            "ROUTING-006", task_id, delegated_executor, "owner_decision",
            "owner_only_task_delegated",
            "Return the task to the owner; no agent may select the component foundation.",
            f"Owner-only task {task_id} cannot be delegated.",
        )
    if delegated_executor and not record.get("owner_only"):
        expected = record.get("execution_class")
        if delegated_executor != expected:
            raise _resolution_error(
                "ROUTING-011", task_id, delegated_executor, expected,
                "executor_mismatch",
                "Use the committed resolved execution class or record a new owner decision.",
                f"Task {task_id} was delegated to the wrong executor.",
            )

    if require_eligible:
        if not record.get("delegation_eligible"):
            raise _resolution_error(
                "ROUTING-012", task_id, False, True,
                "aggregate_or_owner_task_not_delegable",
                "Resolve the eligible leaf task instead.",
                f"Task {task_id} is an aggregate or owner task and cannot produce an implementation prompt.",
            )
        if task.get("status") not in {"active", "published/active", "planned"}:
            raise _resolution_error(
                "ROUTING-013", task_id, task.get("status"), "active or planned",
                "inactive_task", "Select a current planned task.",
                f"Task {task_id} is not active or planned.",
            )
        if not _dependency_eligible(task, tasks):
            raise _resolution_error(
                "ROUTING-014", task_id, task.get("depends_on"), "all dependencies complete",
                "dependency_ineligible",
                "Complete and accept every dependency before prompt generation.",
                f"Task {task_id} has incomplete dependencies.",
            )
        frontier = roadmap.get("active_frontier", {}).get("next_readiness_task_id")
        active_parent = roadmap.get("active_frontier", {}).get("current_parent_task_id")
        if _belongs_to_roots(task_id, {active_parent}, tasks) and task_id != frontier:
            raise _resolution_error(
                "ROUTING-015", task_id, task_id, frontier,
                "not_current_frontier",
                "Generate the prompt only for the authoritative immediate frontier.",
                f"Task {task_id} is not the current application frontier.",
            )

    resolved = {
        key: record.get(key)
        for key in REQUIRED_RECORD_FIELDS
    }
    resolved.update({
        "task_id": task_id,
        "resolution": resolution,
        "inherited_from_task_id": record.get("inherited_from_task_id"),
        "routing_source": ROUTING_SOURCE,
        "scope_id": metadata.get("scope_id"),
    })
    return resolved


def build_prompt_routing_header(route: dict[str, Any]) -> str:
    """Render the mandatory implementation-prompt routing header."""
    source = route.get("authoritative_source_locator", {})
    source_text = f"{source.get('path')}#symbol={source.get('symbol')}"
    escalations = "; ".join(route.get("escalation_conditions", []))
    return "\n".join([
        "## Committed execution routing",
        f"- Task ID: `{route['task_id']}`",
        f"- Resolved execution class: `{route['execution_class']}`",
        f"- Resolved model category: `{route['model_category']}`",
        f"- Reasoning level: `{route['reasoning_level']}`",
        f"- Risk class: `{route['risk_class']}`",
        f"- Owner-only: `{str(bool(route['owner_only'])).lower()}`",
        f"- Rationale: {route['rationale']}",
        f"- Escalation conditions: {escalations}",
        f"- Authoritative routing source: `{source_text}`",
    ])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("--repo-root", default=".")
    validate_parser.add_argument("--json", action="store_true")
    resolve_parser = subparsers.add_parser("resolve")
    resolve_parser.add_argument("task_id")
    resolve_parser.add_argument("--repo-root", default=".")
    resolve_parser.add_argument("--executor")
    resolve_parser.add_argument("--allow-inactive", action="store_true")
    resolve_parser.add_argument("--prompt-header", action="store_true")
    args = parser.parse_args(argv)

    try:
        if args.command == "validate":
            report = validate_execution_routing(args.repo_root)
            if args.json:
                print(json.dumps(report, indent=2, sort_keys=True))
            else:
                print(report["result"])
                for finding in report["findings"]:
                    print(f"{finding['rule_id']}: {finding['file']}:{finding['locator']}: {finding['message']}")
            return 0 if report["result"] == "PASS" else 1
        route = resolve_execution_route(
            args.task_id,
            repo_root=args.repo_root,
            delegated_executor=args.executor,
            require_eligible=not args.allow_inactive,
        )
        print(build_prompt_routing_header(route) if args.prompt_header else json.dumps(route, indent=2, sort_keys=True))
        return 0
    except (RoutingResolutionError, ValueError, OSError, subprocess.SubprocessError) as exc:
        finding = exc.finding if isinstance(exc, RoutingResolutionError) else {"message": str(exc)}
        print(json.dumps({"result": "BLOCKED", "finding": finding}, indent=2, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
