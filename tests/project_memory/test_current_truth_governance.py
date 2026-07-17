"""Focused current-truth and shared UI-policy governance regressions."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from scripts.project_memory import validate_current_truth as current_truth  # noqa: E402
from scripts.project_memory.validate_agent_guidance import validate_agent_guidance  # noqa: E402


def _copy_fixture(tmp_path: Path, monkeypatch) -> Path:
    paths = set(current_truth.CURRENT_TRUTH_FILES)
    paths.update(current_truth.ACTIVE_GUIDANCE_FILES)
    paths.update(current_truth.TASK_LIFECYCLE_SURFACES)
    paths.add(current_truth.ROADMAP_PATH)
    for relative in paths:
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO_ROOT / relative, target)
    monkeypatch.setattr(
        current_truth,
        "validate_execution_routing",
        lambda *_args, **_kwargs: {"result": "PASS", "findings": []},
    )
    return tmp_path


def _replace(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    assert old in text
    path.write_text(text.replace(old, new), encoding="utf-8")


def _codes(report: dict) -> set[str]:
    return {finding["rule_id"] for finding in report["findings"]}


def test_valid_explicit_roadmap_index_binding_passes(tmp_path: Path, monkeypatch):
    root = _copy_fixture(tmp_path, monkeypatch)
    report = current_truth.validate_current_truth(root)
    assert report["result"] == "PASS", report["findings"]


def test_missing_explicit_roadmap_index_binding_fails(tmp_path: Path, monkeypatch):
    root = _copy_fixture(tmp_path, monkeypatch)
    agents = root / "AGENTS.md"
    _replace(agents, "docs/roadmap/roadmap_index.yaml", "roadmap index")
    report = current_truth.validate_current_truth(root)
    assert "GUIDANCE-003" in _codes(report)
    assert any(
        finding["file"] == "AGENTS.md"
        and finding["expected_value"] == current_truth.ROADMAP_PATH
        for finding in report["findings"]
    )


def test_stale_active_frontier_fails(tmp_path: Path, monkeypatch):
    root = _copy_fixture(tmp_path, monkeypatch)
    master = root / "docs/master_plan.md"
    _replace(
        master,
        "- Immediate application frontier: `PHASE8-IMPL-024-T003B`",
        "- Immediate application frontier: `PHASE8-IMPL-024-T003A`",
    )
    report = current_truth.validate_current_truth(root)
    assert "TRUTH-002" in _codes(report)


def test_conflicting_unqualified_next_task_claims_fail(tmp_path: Path, monkeypatch):
    root = _copy_fixture(tmp_path, monkeypatch)
    phase_map = root / "docs/roadmap/phase_map.md"
    _replace(
        phase_map,
        "- Immediate application frontier: `PHASE8-IMPL-024-T003B`",
        "- Immediate application frontier: `PHASE8-IMPL-024-T003C`",
    )
    report = current_truth.validate_current_truth(root)
    assert "TRUTH-003" in _codes(report)


def test_t012_lifecycle_mismatch_in_active_task_surface_fails(tmp_path: Path, monkeypatch):
    root = _copy_fixture(tmp_path, monkeypatch)
    parent = root / "docs/roadmap/tasks/PHASE8-IMPL-026.md"
    _replace(
        parent,
        "Status: complete/PASS.",
        "Status: in progress/validation pending.",
    )
    report = current_truth.validate_current_truth(root)
    assert "TRUTH-005" in _codes(report)
    assert any(
        finding["file"] == "docs/roadmap/tasks/PHASE8-IMPL-026.md"
        and finding["classification"] == "task_lifecycle_surface_mismatch"
        for finding in report["findings"]
    )


def test_historical_next_and_routing_claims_are_allowed(tmp_path: Path, monkeypatch):
    root = _copy_fixture(tmp_path, monkeypatch)
    agents = root / "AGENTS.md"
    agents.write_text(
        agents.read_text(encoding="utf-8")
        + "\n## Historical state at an earlier commit\n\n"
        + "OpenCode Go as the selected low-cost coding-agent platform for remaining MVP.\n"
        + "Excluded from this implementation workflow: GPT and Codex.\n"
        + "The recommended next task was T017C1.\n",
        encoding="utf-8",
    )
    report = current_truth.validate_current_truth(root)
    assert report["result"] == "PASS", report["findings"]


def test_superseded_routing_claims_are_allowed(tmp_path: Path, monkeypatch):
    root = _copy_fixture(tmp_path, monkeypatch)
    agents = root / "AGENTS.md"
    agents.write_text(
        agents.read_text(encoding="utf-8")
        + "\n## Superseded PHASE8-IMPL-023 routing\n\n"
        + "OpenCode Go as the selected low-cost coding-agent platform for remaining MVP.\n"
        + "Excluded from this implementation workflow: GPT and Codex.\n",
        encoding="utf-8",
    )
    report = current_truth.validate_current_truth(root)
    assert report["result"] == "PASS", report["findings"]


def test_active_opencode_only_and_gpt_exclusion_fails(tmp_path: Path, monkeypatch):
    root = _copy_fixture(tmp_path, monkeypatch)
    agents = root / "AGENTS.md"
    agents.write_text(
        agents.read_text(encoding="utf-8")
        + "\n## Active executor policy\n\n"
        + "OpenCode Go as the selected low-cost coding-agent platform for remaining MVP.\n"
        + "Excluded from this implementation workflow: GPT and Codex.\n",
        encoding="utf-8",
    )
    report = current_truth.validate_current_truth(root)
    assert "GUIDANCE-002" in _codes(report)


def test_agent_guidance_validator_allows_locally_historical_routing(tmp_path: Path, monkeypatch):
    root = _copy_fixture(tmp_path, monkeypatch)
    agents = root / "AGENTS.md"
    agents.write_text(
        agents.read_text(encoding="utf-8")
        + "\n## Historical execution routing\n\n"
        + "OpenCode Go as the selected low-cost coding-agent platform for remaining MVP.\n",
        encoding="utf-8",
    )
    report = validate_agent_guidance(root)
    assert report["result"] == "PASS", report["findings"]


def test_agent_guidance_validator_rejects_active_opencode_only_routing(tmp_path: Path, monkeypatch):
    root = _copy_fixture(tmp_path, monkeypatch)
    agents = root / "AGENTS.md"
    agents.write_text(
        agents.read_text(encoding="utf-8")
        + "\n## Active execution routing\n\n"
        + "OpenCode Go as the selected low-cost coding-agent platform for remaining MVP.\n",
        encoding="utf-8",
    )
    report = validate_agent_guidance(root)
    assert report["result"] == "BLOCKED"
    assert any(item["code"] == "obsolete_active_execution_guidance" for item in report["findings"])


def test_active_full_subtxt_owner_blocked_claim_fails(tmp_path: Path, monkeypatch):
    root = _copy_fixture(tmp_path, monkeypatch)
    status = root / "docs/roadmap/implementation_status.md"
    _replace(
        status,
        current_truth.END,
        "- Full Subtxt runtime remains owner-blocked\n" + current_truth.END,
    )
    report = current_truth.validate_current_truth(root)
    assert "TRUTH-004" in _codes(report)


def test_shared_ui_skill_and_opencode_wrapper_are_discoverable():
    skill_path = REPO_ROOT / ".agents/skills/writing-assistant-ui-execution/SKILL.md"
    wrapper_path = REPO_ROOT / ".opencode/agents/project-memory-frontend-ui-reviewer.md"
    skill = skill_path.read_text(encoding="utf-8")
    wrapper = wrapper_path.read_text(encoding="utf-8")
    assert skill_path.is_file()
    assert ".agents/skills/impeccable/SKILL.md" in skill
    assert all(mode in skill for mode in ("UI audit mode", "UI implementation mode", "UI validation mode"))
    assert ".agents/skills/writing-assistant-ui-execution/SKILL.md" in wrapper
    assert "UI audit mode" in wrapper


def test_current_task_and_decision_source_locators_exist():
    task = REPO_ROOT / "docs/roadmap/tasks/PHASE8-IMPL-026-T012.md"
    decision = REPO_ROOT / "docs/roadmap/decisions/PHASE8-IMPL-026-T012-current-truth-execution-routing-and-ui-guidance.md"
    inventory = REPO_ROOT / "docs/roadmap/inventory/PHASE8-IMPL-026-T012.md"
    for path in (task, decision, inventory):
        assert path.is_file()
    inventory_text = inventory.read_text(encoding="utf-8")
    assert "docs/roadmap/tasks/PHASE8-IMPL-026-T012.md" in inventory_text
    assert "docs/roadmap/decisions/PHASE8-IMPL-026-T012-current-truth-execution-routing-and-ui-guidance.md" in inventory_text
    assert "docs/project-memory/registries/execution-routing.json" in inventory_text


def test_t011_routing_repair_is_an_operational_event_not_a_new_child():
    decision_path = (
        REPO_ROOT
        / "docs/roadmap/decisions/PHASE8-IMPL-026-T011-inherited-leaf-execution-routing-repair.md"
    )
    roadmap = json.loads(
        (REPO_ROOT / "docs/roadmap/roadmap_index.yaml").read_text(encoding="utf-8")
    )
    decisions = json.loads(
        (REPO_ROOT / "docs/project-memory/registries/decisions.json").read_text(encoding="utf-8")
    )
    owner_decisions = json.loads(
        (REPO_ROOT / "docs/project-memory/registries/owner-decisions.json").read_text(
            encoding="utf-8"
        )
    )
    enrichment = json.loads(
        (REPO_ROOT / "docs/roadmap/enrichment/PHASE8-IMPL-026.enrichment.json").read_text(
            encoding="utf-8"
        )
    )

    assert decision_path.is_file()
    assert not any(item.get("id") == "PHASE8-IMPL-026-T013" for item in roadmap["tasks"])
    assert any(
        item.get("decision_id") == "pmf-t011-inherited-leaf-execution-routing-repair"
        for item in decisions["records"]
    )
    assert any(
        item.get("owner_decision_id") == "inherited-leaf-execution-routing-repair"
        for item in owner_decisions["records"]
    )
    assert enrichment["next_project_memory_task"] is None
    event = enrichment["operational_maintenance_events"][-1]
    assert event["procedure_task_id"] == "PHASE8-IMPL-026-T011"
    assert event["new_roadmap_child"] is False
    assert event["application_frontier"] == "PHASE8-IMPL-024-T003B"
    assert event["application_implementation"] is False
