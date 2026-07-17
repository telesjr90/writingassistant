"""Focused deterministic remaining-MVP execution-routing regressions."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from scripts.project_memory import validate_registries  # noqa: E402
from scripts.project_memory.execution_routing import (  # noqa: E402
    CURRENT_DECISION,
    HISTORICAL_ROUTING_DECISION,
    ROUTING_SOURCE,
    UI_SKILL,
    RoutingResolutionError,
    build_prompt_routing_header,
    is_ui_related,
    remaining_mvp_task_ids,
    resolve_execution_route,
    validate_execution_routing,
)


BRANCH = "docs/opencode-go-routing-small-task-execution"
ROUTING_SCRIPT = REPO_ROOT / "scripts/project_memory/execution_routing.py"


def _load(relative: str) -> dict:
    return json.loads((REPO_ROOT / relative).read_text(encoding="utf-8"))


def _registry() -> dict:
    return copy.deepcopy(_load(ROUTING_SOURCE))


def _roadmap() -> dict:
    return copy.deepcopy(_load("docs/roadmap/roadmap_index.yaml"))


def _route(registry: dict, task_id: str) -> dict:
    return next(record for record in registry["records"] if record["task_id"] == task_id)


def _resolve(task_id: str, registry: dict, roadmap: dict, **kwargs) -> dict:
    return resolve_execution_route(
        task_id,
        repo_root=REPO_ROOT,
        registry=registry,
        roadmap=roadmap,
        current_branch=BRANCH,
        require_eligible=False,
        **kwargs,
    )


def _resolve_eligible(task_id: str, registry: dict, roadmap: dict, **kwargs) -> dict:
    return resolve_execution_route(
        task_id,
        repo_root=REPO_ROOT,
        registry=registry,
        roadmap=roadmap,
        current_branch=BRANCH,
        require_eligible=True,
        **kwargs,
    )


def _run_cli(task_id: str, *args: str) -> tuple[subprocess.CompletedProcess[str], dict]:
    command = [
        sys.executable,
        str(ROUTING_SCRIPT),
        "resolve",
        task_id,
        "--repo-root",
        str(REPO_ROOT),
        *args,
    ]
    assert "--allow-inactive" not in command
    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result, json.loads(result.stdout)


def _finding_ids(report: dict) -> set[str]:
    return {finding["rule_id"] for finding in report["findings"]}


def test_execution_routing_registry_schema_and_seed_validation_pass():
    schema = _load("docs/project-memory/schemas/project-memory.schema.json")
    routing_def = schema["$defs"]["ExecutionRoutingRecord"]
    required = set(routing_def["allOf"][1]["required"])
    assert {
        "task_id", "execution_class", "model_category", "reasoning_level",
        "risk_class", "rationale", "escalation_conditions", "owner_only",
        "delegation_eligible", "authoritative_source_locator",
        "applicability_scope_id", "capability_tags", "required_skills",
        "inheritance",
    } <= required
    errors = [item for item in validate_registries.validate() if item["level"] == "error"]
    assert not errors, errors


def test_complete_remaining_mvp_routing_coverage_and_source_locators():
    registry = _registry()
    roadmap = _roadmap()
    report = validate_execution_routing(
        REPO_ROOT, registry=registry, roadmap=roadmap, current_branch=BRANCH
    )
    remaining = remaining_mvp_task_ids(roadmap)
    assert report["result"] == "PASS", report["findings"]
    assert report["remaining_task_count"] == len(remaining) == 45
    assert report["explicit_record_count"] == 34
    for task_id in remaining:
        resolved = _resolve(task_id, registry, roadmap)
        assert resolved["execution_class"] in {
            "codex_gpt_5_6_sol", "opencode_go", "owner_decision"
        }
        assert resolved["authoritative_source_locator"] == {
            "path": ROUTING_SOURCE,
            "symbol": task_id if resolved["resolution"] == "explicit" else resolved["inherited_from_task_id"],
        }


def test_explicit_aggregates_and_owner_only_tasks_remain_non_delegable():
    registry = _registry()
    roadmap = _roadmap()
    for task_id in (
        "PHASE8-IMPL-024",
        "PHASE8-IMPL-024-T003",
        "PHASE8-IMPL-024-T004",
        "PHASE8-IMPL-024-T005",
        "PHASE8-IMPL-024-T006",
        "PHASE8-IMPL-024-T007B",
    ):
        assert _route(registry, task_id)["delegation_eligible"] is False

    with pytest.raises(RoutingResolutionError) as exc:
        _resolve_eligible("PHASE8-IMPL-024-T003", registry, roadmap)
    assert exc.value.finding["rule_id"] == "ROUTING-012"


@pytest.mark.parametrize(
    "task_id",
    (
        "PHASE8-IMPL-024-T004A",
        "PHASE8-IMPL-024-T004B",
        "PHASE8-IMPL-024-T004C",
        "PHASE8-IMPL-024-T005A",
        "PHASE8-IMPL-024-T006A",
    ),
)
def test_allowlisted_inherited_ui_leaves_are_delegable(task_id: str):
    resolved = _resolve(task_id, _registry(), _roadmap())
    assert resolved["resolution"] == "inherited"
    assert resolved["execution_class"] == "opencode_go"
    assert resolved["delegation_eligible"] is True
    assert resolved["authoritative_source_locator"] == {
        "path": ROUTING_SOURCE,
        "symbol": resolved["inherited_from_task_id"],
    }


def test_missing_routing_fails_closed():
    registry = _registry()
    roadmap = _roadmap()
    registry["records"] = [
        item for item in registry["records"] if item["task_id"] != "PHASE8-IMPL-027"
    ]
    report = validate_execution_routing(
        REPO_ROOT, registry=registry, roadmap=roadmap, current_branch=BRANCH
    )
    assert "ROUTING-007" in _finding_ids(report)
    with pytest.raises(RoutingResolutionError):
        _resolve("PHASE8-IMPL-027", registry, roadmap)


def test_conflicting_routing_fails_closed():
    registry = _registry()
    roadmap = _roadmap()
    duplicate = copy.deepcopy(_route(registry, "PHASE8-IMPL-027"))
    duplicate["id"] = "routing:PHASE8-IMPL-027-conflict"
    registry["records"].append(duplicate)
    report = validate_execution_routing(
        REPO_ROOT, registry=registry, roadmap=roadmap, current_branch=BRANCH
    )
    assert "ROUTING-008" in _finding_ids(report)
    with pytest.raises(RoutingResolutionError):
        _resolve("PHASE8-IMPL-027", registry, roadmap)


def test_safe_parent_inheritance_is_allowlisted_and_deterministic():
    resolved = _resolve("PHASE8-IMPL-024-T003B", _registry(), _roadmap())
    assert resolved["resolution"] == "inherited"
    assert resolved["inherited_from_task_id"] == "PHASE8-IMPL-024-T003"
    assert resolved["execution_class"] == "opencode_go"
    assert resolved["model_category"] == "opencode_go_narrow_tests_first"
    assert resolved["reasoning_level"] == "focused"
    assert resolved["risk_class"] == "moderate"
    assert resolved["rationale"] == (
        "The backend readiness contract is established; the remaining frontend "
        "and regression slices are bounded and tests-first."
    )
    assert resolved["escalation_conditions"] == [
        "schema or persistence contract changes",
        "same exact validation fails twice",
        "failure-state semantics require architecture changes",
    ]
    assert resolved["delegation_eligible"] is True
    assert UI_SKILL in resolved["required_skills"]

    repeated = _resolve("PHASE8-IMPL-024-T003B", _registry(), _roadmap())
    assert json.dumps(resolved, sort_keys=True) == json.dumps(repeated, sort_keys=True)


def test_t003c_inherits_the_same_delegable_narrow_route():
    resolved = _resolve("PHASE8-IMPL-024-T003C", _registry(), _roadmap())
    assert resolved["resolution"] == "inherited"
    assert resolved["inherited_from_task_id"] == "PHASE8-IMPL-024-T003"
    assert resolved["execution_class"] == "opencode_go"
    assert resolved["model_category"] == "opencode_go_narrow_tests_first"
    assert resolved["delegation_eligible"] is True


def test_standard_cli_resolves_t003b_without_bypass_flags():
    result, payload = _run_cli("PHASE8-IMPL-024-T003B")
    assert result.returncode == 0, payload
    assert payload["resolution"] == "inherited"
    assert payload["execution_class"] == "opencode_go"
    assert payload["delegation_eligible"] is True


@pytest.mark.parametrize(
    ("task_id", "rule_id"),
    (
        ("PHASE8-IMPL-024-T003C", "ROUTING-014"),
        ("PHASE8-IMPL-024-T004A", "ROUTING-014"),
    ),
)
def test_standard_cli_future_inherited_leaves_pass_delegation_then_fail_eligibility(
    task_id: str, rule_id: str
):
    result, payload = _run_cli(task_id)
    assert result.returncode == 1
    assert payload["finding"]["rule_id"] == rule_id
    assert payload["finding"]["rule_id"] != "ROUTING-012"


def test_standard_cli_blocks_aggregate_and_owner_executor_delegation():
    aggregate_result, aggregate = _run_cli("PHASE8-IMPL-024-T003")
    assert aggregate_result.returncode == 1
    assert aggregate["finding"]["rule_id"] == "ROUTING-012"

    owner_result, owner = _run_cli(
        "PHASE8-IMPL-024-T007B", "--executor", "opencode_go"
    )
    assert owner_result.returncode == 1
    assert owner["finding"]["classification"] == "owner_only_task_delegated"


def test_non_allowlisted_child_cannot_inherit():
    with pytest.raises(RoutingResolutionError) as exc:
        _resolve("PHASE8-IMPL-024-T003A", _registry(), _roadmap())
    assert exc.value.finding["rule_id"] == "ROUTING-007"


def test_allowlisted_non_leaf_cannot_inherit():
    registry = _registry()
    roadmap = _roadmap()
    roadmap["tasks"].append({
        "id": "PHASE8-IMPL-024-T003B1",
        "title": "Synthetic nested child",
        "type": "runtime_microtask",
        "status": "planned",
        "parent": "PHASE8-IMPL-024-T003B",
        "depends_on": ["PHASE8-IMPL-024-T003B"],
        "boundary_tags": [],
    })
    report = validate_execution_routing(
        REPO_ROOT, registry=registry, roadmap=roadmap, current_branch=BRANCH
    )
    assert any(
        finding["rule_id"] == "ROUTING-005"
        and finding["locator"] == "task_id=PHASE8-IMPL-024-T003B"
        for finding in report["findings"]
    )


def test_owner_only_boundary_cannot_be_inherited_away():
    roadmap = _roadmap()
    task = next(item for item in roadmap["tasks"] if item["id"] == "PHASE8-IMPL-024-T003B")
    task["boundary_tags"].append("owner_review_required")
    with pytest.raises(RoutingResolutionError) as exc:
        _resolve("PHASE8-IMPL-024-T003B", _registry(), roadmap)
    assert exc.value.finding["rule_id"] == "ROUTING-005"
    assert exc.value.finding["classification"] == "unsafe_parent_inheritance"


def test_inactive_and_dependency_ineligible_leaves_remain_blocked():
    inactive_roadmap = _roadmap()
    inactive_task = next(
        item for item in inactive_roadmap["tasks"]
        if item["id"] == "PHASE8-IMPL-024-T003B"
    )
    inactive_task["status"] = "inactive"
    with pytest.raises(RoutingResolutionError) as inactive_exc:
        _resolve_eligible("PHASE8-IMPL-024-T003B", _registry(), inactive_roadmap)
    assert inactive_exc.value.finding["rule_id"] == "ROUTING-013"

    dependency_roadmap = _roadmap()
    dependency_task = next(
        item for item in dependency_roadmap["tasks"]
        if item["id"] == "PHASE8-IMPL-024-T003B"
    )
    dependency_task["depends_on"] = ["PHASE8-IMPL-024-T003C"]
    with pytest.raises(RoutingResolutionError) as dependency_exc:
        _resolve_eligible("PHASE8-IMPL-024-T003B", _registry(), dependency_roadmap)
    assert dependency_exc.value.finding["rule_id"] == "ROUTING-014"


def test_delegation_metadata_must_match_explicit_task_type():
    registry = _registry()
    _route(registry, "PHASE8-IMPL-024-T003")["delegation_eligible"] = True
    report = validate_execution_routing(
        REPO_ROOT, registry=registry, roadmap=_roadmap(), current_branch=BRANCH
    )
    assert any(
        finding["rule_id"] == "ROUTING-012"
        and finding["classification"] == "delegation_eligibility_mismatch"
        for finding in report["findings"]
    )


def test_explicit_child_override_requires_and_uses_override_metadata():
    registry = _registry()
    roadmap = _roadmap()
    parent = _route(registry, "PHASE8-IMPL-024-T003")
    parent["inheritance"]["allow_explicit_overrides"] = True
    child = copy.deepcopy(parent)
    child.update({
        "id": "routing:PHASE8-IMPL-024-T003B",
        "title": "T003B explicit override",
        "task_id": "PHASE8-IMPL-024-T003B",
        "execution_class": "codex_gpt_5_6_sol",
        "model_category": "gpt_5_6_sol",
        "reasoning_level": "high",
        "risk_class": "critical",
        "delegation_eligible": True,
        "parent_override": {
            "enabled": True,
            "rationale": "Fixture proves an explicit exceptional child overrides allowlisted inheritance.",
        },
        "authoritative_source_locator": {
            "path": ROUTING_SOURCE,
            "symbol": "PHASE8-IMPL-024-T003B",
        },
        "inheritance": {
            "enabled": False,
            "eligible_children": [],
            "allow_explicit_overrides": False,
        },
    })
    registry["records"].append(child)
    resolved = _resolve("PHASE8-IMPL-024-T003B", registry, roadmap)
    assert resolved["resolution"] == "explicit"
    assert resolved["execution_class"] == "codex_gpt_5_6_sol"


def test_conflicting_explicit_child_without_override_fails_closed():
    registry = _registry()
    roadmap = _roadmap()
    parent = _route(registry, "PHASE8-IMPL-024-T003")
    child = copy.deepcopy(parent)
    child.update({
        "id": "routing:PHASE8-IMPL-024-T003B-conflict",
        "title": "T003B conflicting explicit route",
        "task_id": "PHASE8-IMPL-024-T003B",
        "execution_class": "codex_gpt_5_6_sol",
        "model_category": "gpt_5_6_sol",
        "reasoning_level": "high",
        "risk_class": "critical",
        "delegation_eligible": True,
        "authoritative_source_locator": {
            "path": ROUTING_SOURCE,
            "symbol": "PHASE8-IMPL-024-T003B",
        },
        "inheritance": {
            "enabled": False,
            "eligible_children": [],
            "allow_explicit_overrides": False,
        },
    })
    registry["records"].append(child)
    with pytest.raises(RoutingResolutionError) as exc:
        _resolve("PHASE8-IMPL-024-T003B", registry, roadmap)
    assert exc.value.finding["rule_id"] == "ROUTING-004"


@pytest.mark.parametrize(
    ("metadata_field", "value", "rule_id"),
    (
        ("effective_branch", "other-branch", "ROUTING-001"),
        ("decision_path", HISTORICAL_ROUTING_DECISION, "ROUTING-010"),
    ),
)
def test_stale_or_historical_scope_is_rejected(metadata_field: str, value: str, rule_id: str):
    registry = _registry()
    registry["metadata"][metadata_field] = value
    with pytest.raises(RoutingResolutionError) as exc:
        _resolve("PHASE8-IMPL-024-T003B", registry, _roadmap())
    assert exc.value.finding["rule_id"] == rule_id


def test_t007b_is_owner_only_and_non_delegable():
    registry = _registry()
    roadmap = _roadmap()
    route = _resolve("PHASE8-IMPL-024-T007B", registry, roadmap)
    assert route["execution_class"] == "owner_decision"
    assert route["model_category"] == "owner_only"
    assert route["owner_only"] is True
    assert route["delegation_eligible"] is False
    with pytest.raises(RoutingResolutionError) as exc:
        _resolve(
            "PHASE8-IMPL-024-T007B",
            registry,
            roadmap,
            delegated_executor="opencode_go",
        )
    assert exc.value.finding["classification"] == "owner_only_task_delegated"


def test_ui_task_without_shared_impeccable_skill_fails():
    registry = _registry()
    roadmap = _roadmap()
    _route(registry, "PHASE8-IMPL-024-T007A")["required_skills"] = []
    report = validate_execution_routing(
        REPO_ROOT, registry=registry, roadmap=roadmap, current_branch=BRANCH
    )
    assert "UI-001" in _finding_ids(report)


def test_non_ui_task_does_not_require_ui_skill():
    registry = _registry()
    roadmap = _roadmap()
    tasks = {item["id"]: item for item in roadmap["tasks"]}
    route = _route(registry, "PHASE8-IMPL-025-T001")
    assert not is_ui_related(tasks["PHASE8-IMPL-025-T001"], route)
    assert route["required_skills"] == []


def test_prompt_header_contains_all_committed_routing_fields():
    route = _resolve("PHASE8-IMPL-024-T003B", _registry(), _roadmap())
    header = build_prompt_routing_header(route)
    for label in (
        "Task ID", "Resolved execution class", "Resolved model category",
        "Reasoning level", "Risk class", "Owner-only", "Rationale",
        "Escalation conditions", "Authoritative routing source",
    ):
        assert label in header
    assert ROUTING_SOURCE in header
    assert (
        f"{ROUTING_SOURCE}#symbol=PHASE8-IMPL-024-T003"
        in header
    )


def test_current_decision_and_historical_scope_metadata_are_explicit():
    metadata = _registry()["metadata"]
    assert metadata["decision_path"] == CURRENT_DECISION
    assert HISTORICAL_ROUTING_DECISION in metadata["historical_scopes_preserved"]
    assert HISTORICAL_ROUTING_DECISION in metadata["supersedes_for_current_scope"]
