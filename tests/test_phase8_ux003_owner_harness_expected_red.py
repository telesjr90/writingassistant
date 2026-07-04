"""Expected-red contracts for PHASE8-UX-003 owner harness route coverage.

These tests are intentionally static. They inspect the committed harness,
decision, and evidence-contract sources without launching Playwright, servers,
Ollama, extraction, or apply-promotion.
"""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

OWNER_HARNESS = REPO_ROOT / "scripts" / "mvp-owner-acceptance-browser-smoke.mjs"
OMI_DASHBOARD_HARNESS = REPO_ROOT / "scripts" / "omi-dashboard-browser-smoke.mjs"
OMI_CANDIDATE_DETAIL_HARNESS = (
    REPO_ROOT / "scripts" / "omi-candidate-detail-browser-smoke.mjs"
)
OMI_EVIDENCE_DRAWER_HARNESS = (
    REPO_ROOT / "scripts" / "omi-evidence-drawer-browser-smoke.mjs"
)
OMI_APPLY_PROMOTION_HARNESS = (
    REPO_ROOT / "scripts" / "omi-apply-promotion-browser-smoke.mjs"
)

TASK_RECORD = REPO_ROOT / "docs" / "roadmap" / "tasks" / "PHASE8-UX-003.md"
MAPPING_DECISION = (
    REPO_ROOT
    / "docs"
    / "roadmap"
    / "decisions"
    / "PHASE8-UX-003-harness-route-workflow-mapping-decision.md"
)
GATE_DECISION = (
    REPO_ROOT
    / "docs"
    / "roadmap"
    / "decisions"
    / "PHASE8-UX-002-T007-owner-acceptance-gate-decision.md"
)
LATEST_VALIDATION = (
    REPO_ROOT / "docs" / "roadmap" / "validation" / "latest_roadmap_validation.md"
)
OWNER_EVIDENCE_REPORT = (
    REPO_ROOT / "artifacts" / "mvp-readiness" / "owner-acceptance" / "evidence-report.md"
)

B_BLOCKERS = (
    "candidate_review_candidate_first_visible",
    "candidate_review_queue_not_approval",
    "candidate_review_read_only_state",
    "candidate_review_owner_action_explicit",
    "candidate_review_confidence_not_truth",
    "candidate_review_persistence_not_canon",
    "apply_promotion_requires_confirmation",
    "apply_promotion_audit_details",
    "apply_promotion_only_approved_workflow",
    "apply_promotion_failed_rejected_unchanged",
    "apply_promotion_no_bypass",
)

C_NON_CYBER_BLOCKERS = (
    "manual_workspace_notes_project_scoped",
    "manual_workspace_materials_project_scoped",
    "model_assisted_ncp_structured_context_only",
    "model_assisted_subtxt_rubric_only",
    "model_assisted_dramatica_flow_analysis_only",
)

C_CYBER_BLOCKERS = (
    "cyber_fixture_story_check_selected_source_path",
    "cyber_fixture_no_prose_prompt_path",
)

A_MANUAL_REVIEW_ONLY_BLOCKERS = (
    "startup_owner_understands_analysis_boundaries",
    "project_isolation_playwright_evidence_reviewed",
    "runtime_extraction_unavailable_fail_closed",
    "runtime_extraction_failures_no_success_claim",
    "model_assisted_evidence_backed_only",
    "model_assisted_confidence_not_truth",
    "model_assisted_output_not_canon",
    "final explicit owner Accepted/Blocked decision",
)

FORBIDDEN_PROSE_INTENTS = (
    "rewrite",
    "continue",
    "outline",
    "draft",
    "polish",
    "improve",
    "expand",
    "imitate",
    "generate prose",
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def combined_text(paths: tuple[Path, ...]) -> str:
    return "\n".join(read_text(path) for path in paths)


def assert_present(source: str, markers: tuple[str, ...], contract_id: str) -> None:
    missing = [marker for marker in markers if marker not in source]
    assert not missing, (
        f"{contract_id} expected-red owner-harness coverage markers are missing: "
        f"{', '.join(missing)}"
    )


def test_phase8_ux003_b_blockers_require_owner_harness_route_markers() -> None:
    """B blockers need owner-harness markers, not only separate OMI evidence."""

    source = combined_text(
        (
            OWNER_HARNESS,
            MAPPING_DECISION,
            OMI_DASHBOARD_HARNESS,
            OMI_CANDIDATE_DETAIL_HARNESS,
            OMI_EVIDENCE_DRAWER_HARNESS,
            OMI_APPLY_PROMOTION_HARNESS,
        )
    )

    assert_present(source, B_BLOCKERS, "PHASE8-UX-003-B-source-inventory")
    assert_present(
        source,
        (
            "PHASE8_UX003_OWNER_HARNESS_B_ROUTE_COVERAGE",
            "phase8Ux003OwnerHarnessMappedBBlockers",
            "owner_harness_route:evidence:omi_dashboard",
            "owner_harness_route:evidence:omi_candidate_detail",
            "owner_harness_route:evidence:omi_evidence_drawer",
            "owner_harness_route:evidence:omi_apply_promotion_confirmation",
            "owner_harness_result_rule:missing_route_is_not_exposed_not_pass",
            "owner_harness_assertion:apply_promotion_not_executed",
        ),
        "PHASE8-UX-003-B",
    )


def test_phase8_ux003_c_non_cyber_blockers_require_owner_harness_route_markers() -> None:
    """T004 wires non-Cyber C blockers to existing route/workflow evidence."""

    source = combined_text((OWNER_HARNESS, MAPPING_DECISION, TASK_RECORD))

    assert_present(source, C_NON_CYBER_BLOCKERS, "PHASE8-UX-003-C-NON-CYBER-source-inventory")
    assert_present(
        source,
        (
            "PHASE8_UX003_OWNER_HARNESS_C_NON_CYBER_ROUTE_COVERAGE",
            "phase8Ux003OwnerHarnessMappedCNonCyberBlockers",
            "owner_harness_route:notes_project_scoped_save_reload",
            "owner_harness_route:materials_project_scoped_save_reload",
            "owner_harness_route:analysis_runtime_label_status",
            "owner_harness_result_rule:manual_or_not_exposed_is_not_pass",
        ),
        "PHASE8-UX-003-C-NON-CYBER",
    )


def test_phase8_ux003_c_cyber_blockers_are_wired_by_t005() -> None:
    """Cyber selected-source and no-prose coverage is wired through existing UI in T005."""

    source = combined_text((OWNER_HARNESS, MAPPING_DECISION, TASK_RECORD))

    assert_present(source, C_CYBER_BLOCKERS, "PHASE8-UX-003-C-CYBER-source-inventory")
    assert_present(
        source,
        (
            "PHASE8_UX003_OWNER_HARNESS_C_CYBER_ROUTE_COVERAGE",
            "owner_harness_route:cyber_owner_authored_source_select",
            "owner_harness_route:cyber_selected_source_story_check",
            "owner_harness_route:cyber_no_prose_refusal_fail_closed",
            "owner_harness_result_rule:manual_or_not_exposed_is_not_pass",
            "PHASE8-UX-003-T005",
            "PHASE8-UX-003-T005 covered Cyber selected-source Story Check and no-prose refusal/fail-closed evidence through existing owner-authored source UI",
            "cyberFixtureSelectedSourceEvidence",
            "cyberFixtureStoryCheckEvidence",
            "cyberFixtureNoProseEvidence",
            "Cyber C remains MANUAL_REVIEW_REQUIRED unless both Cyber selected-source Story Check route evidence and Cyber no-prose evidence are PASS",
        ),
        "PHASE8-UX-003-C-CYBER",
    )


def test_phase8_ux003_a_blockers_remain_manual_review_only() -> None:
    """A blockers must not be converted into automated PASS assertions."""

    source = combined_text((OWNER_HARNESS, MAPPING_DECISION, GATE_DECISION))

    assert_present(
        source,
        A_MANUAL_REVIEW_ONLY_BLOCKERS,
        "PHASE8-UX-003-A-manual-source-inventory",
    )
    assert "A-category manual review table" in source
    assert "Manual owner review only." in source
    assert "Required final result" in source
    assert "finalDecision = FINAL_DECISIONS.MANUAL_REVIEW_REQUIRED" in source
    assert "FINAL_DECISIONS.READY_FOR_OWNER_REVIEW" in source
    assert "owner acceptance remains pending" in source.lower()


def test_phase8_ux003_static_guardrails_do_not_allow_mapped_evidence_to_complete_mvp() -> None:
    """Mapped evidence cannot mark owner acceptance PASS or MVP complete by itself."""

    source = combined_text(
        (
            OWNER_HARNESS,
            TASK_RECORD,
            MAPPING_DECISION,
            GATE_DECISION,
            LATEST_VALIDATION,
            OWNER_EVIDENCE_REPORT,
        )
    )

    assert "Do not mark owner acceptance PASS" in source
    assert "Do not mark MVP complete" in source
    assert "Owner acceptance remains pending" in source
    assert "MVP is not complete" in source
    assert "Final automated decision: **MANUAL_REVIEW_REQUIRED**" in source
    assert "final owner Accepted/Blocked decision" in source
    assert "SCRIPT_EXIT=0" in source


def test_phase8_ux003_static_guardrails_do_not_run_forbidden_paths() -> None:
    """Expected-red coverage must remain evidence-only and non-mutating."""

    source = combined_text(
        (
            OWNER_HARNESS,
            OMI_DASHBOARD_HARNESS,
            OMI_CANDIDATE_DETAIL_HARNESS,
            OMI_EVIDENCE_DRAWER_HARNESS,
            OMI_APPLY_PROMOTION_HARNESS,
            MAPPING_DECISION,
        )
    )

    assert "run apply-promotion" in source
    assert "does not execute" in source
    assert "does not mutate Memory/Canon" in source
    assert "no Memory/Canon mutation" in source
    assert "Do not mutate Memory/Canon" in source
    assert "Do not call models/Ollama" in source
    assert "No model/Ollama calls" in source
    assert "Do not run extraction" in source
    assert "Do not run or enable apply-promotion" in source
    assert "Do not add generated prose controls" in source
    assert "do not create candidates" in source.lower()
    assert "didGenerateStoryProseFromFixture" in source

    for intent in FORBIDDEN_PROSE_INTENTS:
        assert intent in source
