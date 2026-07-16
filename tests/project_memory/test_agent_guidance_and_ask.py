"""Focused T008 contracts for shared guidance and Project Memory Ask.

Tests inspect tracked files or temporary copies only. They do not run an agent,
model, retrieval system, network service, or external tool.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_ROOT = REPO_ROOT / "docs" / "project-memory" / "registries"

sys.path.insert(0, str(REPO_ROOT))
from scripts.project_memory.validate_agent_guidance import (  # noqa: E402
    REQUIRED_FILES,
    REQUIRED_PROTOCOL_TOKENS,
    validate_agent_guidance,
)
from scripts.project_memory.render_docs import _derive_pm_task_behavior  # noqa: E402


def _text(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def _registry(name: str) -> dict:
    return json.loads((REGISTRY_ROOT / name).read_text(encoding="utf-8"))


def _record(name: str, record_id: str) -> dict:
    return next(item for item in _registry(name)["records"] if item["id"] == record_id)


def _copy_guidance_fixture(tmp_path: Path) -> Path:
    for relative_path in REQUIRED_FILES:
        target = tmp_path / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO_ROOT / relative_path, target)
    return tmp_path


def test_owner_decision_defers_t006_t007_for_no_measured_gap():
    record = _record(
        "owner-decisions.json",
        "owner-decision:t006-t007-no-measured-gap-deferral",
    )
    selected = record["selected_option"].lower()
    rationale = record["rationale"].lower()
    assert record["lifecycle"]["status"] == "current"
    assert record["authority_class"] == "authoritative"
    assert {"PHASE8-IMPL-026-T006", "PHASE8-IMPL-026-T007"} <= set(record["affected_tasks"])
    assert all(word in selected for word in ("defer", "contingent", "planned", "inactive", "unimplemented"))
    assert all(gap in rationale for gap in ("symbol-navigation", "retrieval-quality", "citation", "scale", "latency", "maintainability"))


def test_t005_zero_artifact_result_is_topology_not_retrieval_deficiency():
    decision = _text(
        "docs/roadmap/decisions/PHASE8-IMPL-026-T006-T007-owner-deferral-no-measured-gap.md"
    )
    assert "worktree's topology" in decision
    assert "not evidence of a Serena deficiency or a vector-retrieval deficiency" in decision


def test_t006_t007_are_planned_contingent_inactive_and_unimplemented():
    for task_id in ("PHASE8-IMPL-026-T006", "PHASE8-IMPL-026-T007"):
        record = _record("tasks.json", f"task:{task_id}")
        notes = record["notes"].lower()
        assert record["lifecycle"]["status"] == "planned"
        assert all(word in notes for word in ("owner-deferred", "contingent", "inactive", "unimplemented"))
        assert record["is_application_frontier"] is False
        assert record["is_blocking"] is False


def test_t006_t007_are_not_approved_installed_active_complete_or_required_by_t008():
    tasks = _registry("tasks.json")["records"]
    by_task = {record["task_id"]: record for record in tasks}
    for task_id in ("PHASE8-IMPL-026-T006", "PHASE8-IMPL-026-T007"):
        notes = by_task[task_id]["notes"].lower()
        assert by_task[task_id]["lifecycle"]["status"] != "complete"
        assert all(phrase in notes for phrase in ("not rejected", "approved", "installed", "active", "complete", "required by t008"))
    assert by_task["PHASE8-IMPL-026-T008"]["depends_on"] == ["PHASE8-IMPL-026-T004"]


def test_t008_through_t011_complete_and_t012_lifecycle_controls_maintenance_selection():
    tasks = _registry("tasks.json")["records"]
    by_task = {record["task_id"]: record for record in tasks}
    behavior = _derive_pm_task_behavior(
        tasks,
        _registry("owner-decisions.json")["records"],
    )
    t008 = _record("tasks.json", "task:PHASE8-IMPL-026-T008")
    t009 = _record("tasks.json", "task:PHASE8-IMPL-026-T009")
    t010 = by_task["PHASE8-IMPL-026-T010"]
    t011 = by_task["PHASE8-IMPL-026-T011"]
    t012 = by_task["PHASE8-IMPL-026-T012"]
    remaining_task_ids = {
        task_id
        for task_id, state in behavior["states"].items()
        if state["state"] != "complete"
    }
    selected_next_ids = (
        [behavior["next_actionable_task"]["task_id"]]
        if behavior["next_actionable_task"] is not None
        else []
    )

    assert t008["lifecycle"]["status"] == "complete"
    assert "complete/pass" in t008["notes"].lower()
    assert t009["lifecycle"]["status"] == "complete"
    assert any(result in t009["notes"].lower() for result in ("complete/pass", "complete/pass-with-findings"))
    assert t009["lifecycle"]["status"] not in {"planned", "in_progress", "current"}
    assert behavior["states"]["PHASE8-IMPL-026-T009"]["actionable"] is False
    assert "PHASE8-IMPL-026-T009" not in remaining_task_ids

    assert t010["lifecycle"]["status"] == "complete"
    assert "complete/pass" in t010["notes"].lower()
    assert behavior["states"]["PHASE8-IMPL-026-T010"]["state"] == "complete"
    assert "PHASE8-IMPL-026-T010" not in remaining_task_ids
    delivery_paths = {locator["path"] for locator in t010["provenance"]["source_locators"]}
    assert {
        "docs/project-memory/reviewer-protocol.md",
        ".agents/skills/project-memory-plan-integrity-review/SKILL.md",
        "scripts/project_memory/validate_reviewer_guidance.py",
        "scripts/project_memory/reviewer_findings.py",
        "tests/project_memory/test_plan_integrity_reviewers.py",
        "docs/roadmap/decisions/PHASE8-IMPL-026-T010-specialized-plan-integrity-reviewers.md",
    } <= delivery_paths

    assert t011["lifecycle"]["status"] == "complete"
    assert "complete/pass" in t011["notes"].lower()
    assert behavior["states"]["PHASE8-IMPL-026-T011"]["state"] == "complete"
    assert behavior["states"]["PHASE8-IMPL-026-T011"]["actionable"] is False
    assert "PHASE8-IMPL-026-T011" not in remaining_task_ids
    if t012["lifecycle"]["status"] == "complete":
        assert selected_next_ids == []
        assert behavior["states"]["PHASE8-IMPL-026-T012"]["actionable"] is False
    else:
        assert t012["lifecycle"]["status"] == "in_progress"
        assert selected_next_ids == ["PHASE8-IMPL-026-T012"]
        assert behavior["states"]["PHASE8-IMPL-026-T012"]["actionable"] is True

    assert "reviewer agent" not in t009["notes"].lower()
    assert t010["lifecycle"]["status"] != "in_progress"


def test_t010_and_t011_are_complete():
    assert _record("tasks.json", "task:PHASE8-IMPL-026-T010")["lifecycle"]["status"] == "complete"
    assert _record("tasks.json", "task:PHASE8-IMPL-026-T011")["lifecycle"]["status"] == "complete"


def test_dependency_registry_does_not_make_retrieval_pilots_required_by_t008():
    dependencies = _registry("dependencies.json")["records"]
    t008_edges = [item for item in dependencies if item["source_id"] == "task:PHASE8-IMPL-026-T008"]
    assert [item["target_id"] for item in t008_edges] == ["task:PHASE8-IMPL-026-T004"]


def test_root_guidance_preserves_source_precedence_and_product_boundaries():
    root = _text("AGENTS.md")
    section = root.split("## Project Memory consultation", 1)[1]
    normalized = " ".join(section.split())
    assert "accepted roadmap and decision records before code/tests" in normalized
    assert "Registries and generated evidence are navigation aids, never authority" in normalized
    assert "Separate facts from inference" in normalized
    assert all(value in normalized for value in ("freshness", "commit binding"))
    assert "Fail closed" in normalized
    assert "Never automatically mutate roadmap state" in normalized
    assert all(
        value in normalized
        for value in ("Memory/Canon", "story prose", "model output as truth")
    )


def test_read_skill_references_current_sources_instead_of_copying_project_truth():
    skill = _text(".agents/skills/project-memory-read/SKILL.md")
    assert "docs/roadmap/roadmap_index.yaml" in skill
    assert "docs/roadmap/implementation_status.md" in skill
    assert "docs/project-memory/registries/manifest.json" in skill
    assert "Do not copy the roadmap or schema into this skill" in skill
    assert len(skill.splitlines()) < 120


def test_ask_protocol_contains_all_request_and_response_fields():
    protocol = _text("docs/project-memory/ask-protocol.md")
    for token in REQUIRED_PROTOCOL_TOKENS:
        assert token in protocol


def test_ask_protocol_separates_facts_from_inference():
    protocol = _text("docs/project-memory/ask-protocol.md")
    assert "Facts and inferences are separate lists" in protocol
    assert "confidence language does not convert an inference into a fact" in protocol


def test_ask_protocol_requires_source_authority_freshness_commit_and_owner_status():
    protocol = _text("docs/project-memory/ask-protocol.md")
    assert "authority class, freshness, and bound commit" in protocol
    assert "conflicts_and_uncertainty" in protocol
    assert "owner_pending_decisions" in protocol


def test_ask_protocol_fail_closed_cases_are_explicit():
    protocol = _text("docs/project-memory/ask-protocol.md").lower()
    for required in (
        "branch or commit binding is stale",
        "unapproved tool",
        "sources conflict",
        "outside the repository or maximum scope",
        "owner-pending",
        "untrusted",
        "quarantined",
    ):
        assert required in protocol


def test_generated_evidence_cannot_override_authority():
    protocol = _text("docs/project-memory/ask-protocol.md")
    assert "Generated evidence never becomes\nauthority" in protocol
    assert "do not override accepted roadmap records" in protocol


def test_opencode_agent_is_strictly_read_only():
    agent = _text(".opencode/agents/project-memory-ask.md")
    for control in (
        "write: false",
        "edit: false",
        "patch: false",
        "webfetch: false",
        "external_directory: deny",
        '"*": deny',
    ):
        assert control in agent
    assert "Do not access any external worktree" in agent


def test_opencode_shell_allowlist_contains_only_read_only_git_inspection():
    agent = _text(".opencode/agents/project-memory-ask.md")
    frontmatter = agent.split("---", 2)[1]
    allowed = [line.strip() for line in frontmatter.splitlines() if line.strip().endswith(": allow")]
    assert allowed == [
        '"git status*": allow',
        '"git branch --show-current": allow',
        '"git rev-parse HEAD": allow',
        '"git log -1*": allow',
        '"git diff --quiet": allow',
        '"git diff --cached --quiet": allow',
    ]


def test_opencode_agent_grants_no_mutation_install_network_server_model_or_retrieval_tool():
    agent = _text(".opencode/agents/project-memory-ask.md")
    assert not any(token in agent for token in ("write: true", "edit: true", "patch: true", "webfetch: true"))
    assert "Do not\nwrite, edit, patch, install packages, use the network, start a server, invoke a\nmodel/tool runner" in agent
    assert "Do not use or require\nSerena, LlamaIndex, Qdrant, embeddings, MCP" in agent


def test_no_automatic_roadmap_memory_promotion_or_prose_mutation_allowed():
    combined = "\n".join(
        _text(path)
        for path in (
            "docs/project-memory/ask-protocol.md",
            ".agents/skills/project-memory-read/SKILL.md",
            ".opencode/agents/project-memory-ask.md",
        )
    )
    for boundary in ("activate", "close", "reorder", "registries", "Memory/Canon", "promote", "apply promotion", "story prose"):
        assert boundary in combined


def test_application_frontier_and_ph8_impl_025_remain_unchanged():
    completed = _record("tasks.json", "task:PHASE8-IMPL-024-T003A")
    frontier = _record("tasks.json", "task:PHASE8-IMPL-024-T003B")
    ph25 = _record("tasks.json", "task:PHASE8-IMPL-025")
    assert completed["is_application_frontier"] is False
    assert completed["lifecycle"]["status"] == "complete"
    assert frontier["is_application_frontier"] is True
    assert frontier["lifecycle"]["status"] == "planned"
    assert ph25["lifecycle"]["status"] == "planned"
    assert "inactive" in ph25["notes"].lower()


def test_guidance_validator_passes_real_repository():
    report = validate_agent_guidance(REPO_ROOT)
    assert report == {
        "result": "PASS",
        "checked_files": list(REQUIRED_FILES),
        "findings": [],
    }


def test_guidance_validator_is_deterministic(tmp_path):
    fixture = _copy_guidance_fixture(tmp_path)
    first = validate_agent_guidance(fixture)
    second = validate_agent_guidance(fixture)
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


def test_guidance_validator_fails_closed_and_sorts_findings(tmp_path):
    fixture = _copy_guidance_fixture(tmp_path)
    (fixture / "docs/project-memory/ask-protocol.md").write_text("# incomplete\n", encoding="utf-8")
    (fixture / ".opencode/agents/project-memory-ask.md").write_text(
        "write: true\nedit: true\nwebfetch: true\n", encoding="utf-8"
    )
    report = validate_agent_guidance(fixture)
    assert report["result"] == "BLOCKED"
    keys = [(item["code"], item["path"], item["detail"]) for item in report["findings"]]
    assert keys == sorted(keys)
    assert {item["code"] for item in report["findings"]} >= {
        "missing_protocol_token",
        "missing_read_only_control",
        "forbidden_permission_grant",
    }


def test_guidance_validator_json_cli(tmp_path):
    fixture = _copy_guidance_fixture(tmp_path)
    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts/project_memory/validate_agent_guidance.py"),
            "--repo-root",
            str(fixture),
            "--json",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert json.loads(result.stdout)["result"] == "PASS"


def test_decision_and_evidence_records_are_current_and_cross_referenced():
    decision = _record("decisions.json", "decision:pmf-t008-agent-guidance-ask")
    evidence = _record("evidence.json", "evidence:ph8-impl-026-t008-agent-guidance-ask")
    assert decision["lifecycle"]["status"] == "current"
    assert decision["authority_class"] == "authoritative"
    assert evidence["lifecycle"]["status"] == "current"
    assert evidence["authority_class"] == "accepted_evidence"
    assert evidence["associated_task_id"] == "PHASE8-IMPL-026-T008"


def test_t010_decision_and_evidence_records_are_current_and_non_authoritative_output_is_explicit():
    decision = _record("decisions.json", "decision:pmf-t010-specialized-reviewers")
    evidence = _record("evidence.json", "evidence:ph8-impl-026-t010-specialized-reviewers")
    assert decision["lifecycle"]["status"] == "current"
    assert decision["authority_class"] == "authoritative"
    assert evidence["lifecycle"]["status"] == "current"
    assert evidence["authority_class"] == "accepted_evidence"
    assert evidence["associated_task_id"] == "PHASE8-IMPL-026-T010"
    assert "generated_evidence" in decision["selected_option"]
    assert "without running an agent, model, network" in evidence["description"]


def test_t011_decision_evidence_and_owner_cadence_are_current():
    decision = _record("decisions.json", "decision:pmf-t011-operational-rollout")
    evidence = _record("evidence.json", "evidence:ph8-impl-026-t011-operational-rollout")
    owner = _record("owner-decisions.json", "owner-decision:q154-event-driven-commit-bound-cadence")
    assert decision["lifecycle"]["status"] == "current"
    assert decision["authority_class"] == "authoritative"
    assert evidence["authority_class"] == "accepted_evidence"
    assert evidence["associated_task_id"] == "PHASE8-IMPL-026-T011"
    assert owner["provenance"]["accepted_by"] == "owner"
    assert "event-driven" in owner["selected_option"].lower()
    assert "no cron" in owner["selected_option"].lower()
