"""Expected-red source contracts for PHASE8-UX-002 MVP UI acceptance surfaces.

These tests intentionally describe browser-visible UI/workflow contracts that
are not implemented yet. They must fail until the PHASE8-UX-002-T004/T005/T006
implementation slices add the corresponding source/Story Check/no-prose UI.
"""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_SRC = REPO_ROOT / "frontend" / "src"

APP_JSX = FRONTEND_SRC / "App.jsx"
API_JS = FRONTEND_SRC / "api.js"
EDITOR_JSX = FRONTEND_SRC / "components" / "Editor.jsx"
PROJECT_NAV_JSX = FRONTEND_SRC / "components" / "ProjectNav.jsx"
ANALYSIS_SIDEBAR_JSX = FRONTEND_SRC / "components" / "AnalysisSidebar.jsx"
REVIEW_QUEUE_PANEL_JSX = FRONTEND_SRC / "components" / "ReviewQueuePanel.jsx"
APPLY_PROMOTION_CONFIRMATION_JSX = (
    FRONTEND_SRC / "components" / "ApplyPromotionConfirmation.jsx"
)
OWNER_ACTION_CONTROLS_JSX = (
    FRONTEND_SRC / "components" / "OwnerActionReviewControls.jsx"
)
OMI_SHELL_JSX = FRONTEND_SRC / "components" / "OMIShell.jsx"
OMI_DASHBOARD_JSX = FRONTEND_SRC / "components" / "OMIDashboard.jsx"
OMI_BOUNDARY_BANNER_JSX = FRONTEND_SRC / "components" / "OMIBoundaryBanner.jsx"
OMI_CANDIDATE_CANON_STATUS_JSX = (
    FRONTEND_SRC / "components" / "OMICandidateCanonStatusStrip.jsx"
)
OMI_WORKFLOW_STATUS_ROW_JSX = (
    FRONTEND_SRC / "components" / "OMIWorkflowStatusRow.jsx"
)
OMI_CANDIDATE_DETAIL_JSX = FRONTEND_SRC / "components" / "OMICandidateDetail.jsx"
OMI_CANDIDATE_FIELD_TABLE_JSX = (
    FRONTEND_SRC / "components" / "OMICandidateFieldTable.jsx"
)
OMI_PROMOTION_READINESS_CHECKLIST_JSX = (
    FRONTEND_SRC / "components" / "OMIPromotionReadinessChecklist.jsx"
)
OMI_EVIDENCE_DRAWER_JSX = FRONTEND_SRC / "components" / "OMIEvidenceDrawer.jsx"

SOURCE_PATHS = (
    APP_JSX,
    API_JS,
    EDITOR_JSX,
    PROJECT_NAV_JSX,
    ANALYSIS_SIDEBAR_JSX,
    REVIEW_QUEUE_PANEL_JSX,
    APPLY_PROMOTION_CONFIRMATION_JSX,
    OWNER_ACTION_CONTROLS_JSX,
    OMI_SHELL_JSX,
    OMI_DASHBOARD_JSX,
    OMI_BOUNDARY_BANNER_JSX,
    OMI_CANDIDATE_CANON_STATUS_JSX,
    OMI_WORKFLOW_STATUS_ROW_JSX,
    OMI_CANDIDATE_DETAIL_JSX,
    OMI_CANDIDATE_FIELD_TABLE_JSX,
    OMI_PROMOTION_READINESS_CHECKLIST_JSX,
    OMI_EVIDENCE_DRAWER_JSX,
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


def read_source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def combined_source(paths: tuple[Path, ...] = SOURCE_PATHS) -> str:
    return "\n".join(read_source(path) for path in paths)


def assert_markers_present(
    source: str,
    markers: tuple[str, ...],
    surface_id: str,
) -> None:
    missing = [marker for marker in markers if marker not in source]
    assert not missing, (
        f"{surface_id} expected-red UI contract markers are missing: "
        f"{', '.join(missing)}"
    )


def test_ux2_source_001_owner_authored_source_create_import_select_contract() -> None:
    """UX2-SOURCE-001 requires a project-scoped source workflow before Story Check."""

    source = combined_source((APP_JSX, API_JS, PROJECT_NAV_JSX, ANALYSIS_SIDEBAR_JSX))

    assert_markers_present(
        source,
        (
            "data-testid=\"ux2-source-create-import\"",
            "data-testid=\"ux2-source-import-owner-authored\"",
            "data-testid=\"ux2-selected-story-check-source\"",
            "selectedStoryCheckSourceId",
            "owner-authored source",
            "project-scoped selected source",
            "Story Check requires a selected owner-authored source",
            "createOrImportOwnerAuthoredSource",
            "selectStoryCheckSource",
        ),
        "UX2-SOURCE-001",
    )


def test_ux2_storycheck_001_diagnostic_only_selected_source_contract() -> None:
    """UX2-STORYCHECK-001 requires diagnostic-only Story Check bound to selected source."""

    source = combined_source((APP_JSX, API_JS, ANALYSIS_SIDEBAR_JSX))

    assert_markers_present(
        source,
        (
            "data-testid=\"ux2-story-check-run\"",
            "data-testid=\"ux2-story-check-selected-source\"",
            "data-testid=\"ux2-story-check-diagnostic-result\"",
            "runStoryCheckForSelectedSource",
            "diagnostic-only",
            "analysis-only result",
            "model output is not canon",
            "confidence is not truth",
            "output cannot become approved memory automatically",
            "disabled={!selectedStoryCheckSourceId || isAnalyzing}",
        ),
        "UX2-STORYCHECK-001",
    )


def test_ux2_noprose_001_refusal_fail_closed_contract() -> None:
    """UX2-NOPROSE-001 requires safe refusal UI for every forbidden prose intent."""

    source = combined_source((APP_JSX, API_JS, ANALYSIS_SIDEBAR_JSX))

    assert_markers_present(
        source,
        (
            "data-testid=\"ux2-no-prose-refusal-panel\"",
            "data-testid=\"ux2-no-arbitrary-prompt-route\"",
            "analysis-only no-prose boundary",
            "no generated story prose",
            "arbitrary prompt route is unavailable",
            "NoProseRefusal",
            "refuseForbiddenProseIntent",
        )
        + tuple(f"data-testid=\"ux2-no-prose-{intent.replace(' ', '-')}-refused\"" for intent in FORBIDDEN_PROSE_INTENTS)
        + tuple(f"forbidden intent: {intent}" for intent in FORBIDDEN_PROSE_INTENTS),
        "UX2-NOPROSE-001",
    )


def test_ux2_notes_materials_001_project_scoped_create_save_reload_contract() -> None:
    """UX2-NOTES-MATERIALS-001 requires create/save/reload proof without canon mutation."""

    source = combined_source((APP_JSX, API_JS, PROJECT_NAV_JSX, EDITOR_JSX))

    assert_markers_present(
        source,
        (
            "data-testid=\"ux2-note-create\"",
            "data-testid=\"ux2-material-create\"",
            "data-testid=\"ux2-note-save-reload-proof\"",
            "data-testid=\"ux2-material-save-reload-proof\"",
            "createOwnerAuthoredNote",
            "createOwnerProvidedMaterial",
            "reloadProjectScopedNotesMaterials",
            "owner-authored note",
            "owner-provided material",
            "not canon by default",
            "notes/materials do not mutate memory or canon",
        ),
        "UX2-NOTES-MATERIALS-001",
    )


def test_ux2_raw_artifact_001_unavailable_read_only_evidence_contract() -> None:
    """UX2-RAW-ARTIFACT-001 requires support-data-only raw artifact evidence UI."""

    source = combined_source((APP_JSX, API_JS, ANALYSIS_SIDEBAR_JSX, REVIEW_QUEUE_PANEL_JSX))

    assert_markers_present(
        source,
        (
            "data-testid=\"ux2-runtime-extraction-unavailable\"",
            "data-testid=\"ux2-raw-artifact-read-only-evidence\"",
            "fetchRawArtifactEvidenceStatus",
            "runtime extraction unavailable",
            "read-only raw artifact evidence",
            "raw artifacts are support data only",
            "raw artifacts are not canon",
            "raw artifact inspection does not mutate memory or canon",
        ),
        "UX2-RAW-ARTIFACT-001",
    )


def test_ux2_review_promotion_001_confirmation_audit_contract() -> None:
    """UX2-REVIEW-PROMOTION-001 requires explicit confirmation and audit evidence UI."""

    source = combined_source(
        (
            APP_JSX,
            API_JS,
            REVIEW_QUEUE_PANEL_JSX,
            APPLY_PROMOTION_CONFIRMATION_JSX,
            OWNER_ACTION_CONTROLS_JSX,
        )
    )

    assert_markers_present(
        source,
        (
            "data-testid=\"ux2-review-queue-fixture\"",
            "data-testid=\"ux2-apply-promotion-owner-confirmation\"",
            "data-testid=\"ux2-promotion-audit-evidence\"",
            "data-testid=\"ux2-approved-memory-unchanged-after-rejection\"",
            "explicit owner confirmation",
            "apply-promotion is explicit/audited/owner-confirmed",
            "candidate persistence is not canon",
            "queue presence is not approval",
            "failed promotion leaves approved memory/canon unchanged",
            "rejected promotion leaves approved memory/canon unchanged",
        ),
        "UX2-REVIEW-PROMOTION-001",
    )


def test_ux2_analysis_runtime_001_not_exposed_label_only_contract() -> None:
    """UX2-ANALYSIS-RUNTIME-001 requires NOT_EXPOSED labels and no runtime execution UI."""

    source = combined_source((APP_JSX, API_JS, ANALYSIS_SIDEBAR_JSX))

    assert_markers_present(
        source,
        (
            "data-testid=\"ux2-analysis-runtime-status\"",
            "NCP: NOT_EXPOSED",
            "Subtxt: NOT_EXPOSED",
            "dramatica-flow: NOT_EXPOSED",
            "analysis runtime labels only",
            "runtime execution is not exposed",
            "NCP is structured context interchange only",
            "Subtxt is rubric/diagnostic guidance only",
            "dramatica-flow is audited allowlist only",
            "no runtime execution path",
        ),
        "UX2-ANALYSIS-RUNTIME-001",
    )


def test_omi_dashboard_only_boundary_and_separation_contract() -> None:
    """First OMI frontend slice requires dashboard-only safe review operations."""

    source = combined_source(
        (
            APP_JSX,
            PROJECT_NAV_JSX,
            OMI_SHELL_JSX,
            OMI_DASHBOARD_JSX,
            OMI_BOUNDARY_BANNER_JSX,
            OMI_CANDIDATE_CANON_STATUS_JSX,
            OMI_WORKFLOW_STATUS_ROW_JSX,
        )
    )

    assert_markers_present(
        source,
        (
            "data-testid=\"omi-dashboard\"",
            "data-testid=\"omi-boundary-banner\"",
            "data-testid=\"omi-candidate-canon-status\"",
            "data-testid=\"omi-dashboard-approved-memory-snapshot\"",
            "data-testid=\"omi-dashboard-disabled-apply-reason\"",
            "data-testid=\"omi-workspace-entry\"",
            "OMI stores review material only. Nothing becomes Memory/Canon until the owner explicitly confirms a separate apply-promotion step.",
            "Disabled: apply-promotion requires owner approval, destination, evidence/provenance review, duplicate resolution, dependency review, and final confirmation.",
            "aria-describedby={disabledApplyReasonId}",
            "Owner Input",
            "Candidates",
            "Grouped Review",
            "Duplicate Decisions",
            "Promotion Handoff Readiness",
            "Promotion Audit Records",
            "Deferred Categories",
            "Approved Memory/Canon Snapshot",
            "Warnings / Health",
            "Loading OMI status.",
            "No owner input is stored for this project.",
            "No candidates are stored for this project.",
            "No inferred counts are shown while OMI status is degraded.",
            "Candidates are not approved Memory/Canon",
            "Approved Memory/Canon is shown separately from candidates and promotion audit records.",
        ),
        "OMI-DASHBOARD-ONLY",
    )


def test_omi_dashboard_source_has_no_generated_prose_controls() -> None:
    """OMI Dashboard must not expose prose-production controls."""

    source = combined_source(
        (
            OMI_SHELL_JSX,
            OMI_DASHBOARD_JSX,
            OMI_BOUNDARY_BANNER_JSX,
            OMI_CANDIDATE_CANON_STATUS_JSX,
            OMI_WORKFLOW_STATUS_ROW_JSX,
        )
    ).lower()

    forbidden_control_labels = (
        "rewrite",
        "continue",
        "outline",
        "draft",
        "polish",
        "improve",
        "expand",
        "imitate",
        "generate prose",
        "generated prose",
    )

    assert not [
        label for label in forbidden_control_labels if label in source
    ], "OMI dashboard source must not expose generated-prose controls."


def test_omi_candidate_detail_only_review_packet_contract() -> None:
    """Second OMI slice requires candidate-detail-only stored review metadata UI."""

    source = combined_source(
        (
            OMI_SHELL_JSX,
            OMI_DASHBOARD_JSX,
            OMI_CANDIDATE_DETAIL_JSX,
            OMI_CANDIDATE_FIELD_TABLE_JSX,
            OMI_PROMOTION_READINESS_CHECKLIST_JSX,
        )
    )

    assert_markers_present(
        source,
        (
            "data-testid=\"omi-candidate-detail\"",
            "data-testid=\"omi-candidate-field-table\"",
            "data-testid=\"omi-promotion-readiness-checklist\"",
            "Candidate: Pending Review",
            "Candidate: Owner Approved",
            "Destination",
            "Source",
            "Field",
            "Proposed value",
            "Decision",
            "Evidence",
            "Provenance",
            "Duplicate/dependency",
            "Owner note",
            "Promotion Audit Record",
            "Not Applied to Memory/Canon",
            "Approved Memory/Canon links",
            "Read-only reference",
            "No candidate selected.",
            "Candidate not found.",
            "Unsupported candidate schema",
            "Missing destination",
            "Missing evidence",
            "Missing provenance",
            "Required field decisions unresolved",
            "Duplicate unresolved",
            "Dependency unresolved",
            "No approved Memory/Canon links.",
            "Candidate schema unsupported or partially corrupt.",
            "This remains a candidate until apply-promotion is separately confirmed and completed.",
            "Ready means the handoff packet is complete. Memory/Canon has not changed.",
            "Evidence supports review. It is not canon truth until owner approval and apply-promotion are complete.",
            "Confidence indicates support strength, not truth.",
            "Stored review metadata only",
            "Missing / Not linked / Unavailable",
            "Owner approval prepares this candidate for a future handoff. It does not update Memory/Canon.",
            "Fields",
            "Evidence",
            "Readiness",
            "onNavigate={handleNavigate}",
            "setOmiView('candidate-detail')",
        ),
        "OMI-CANDIDATE-DETAIL-ONLY",
    )


def test_omi_candidate_detail_disabled_reason_associations() -> None:
    """Candidate and field approval disabled reasons must be programmatically associated."""

    source = combined_source(
        (
            OMI_CANDIDATE_DETAIL_JSX,
            OMI_CANDIDATE_FIELD_TABLE_JSX,
        )
    )

    assert_markers_present(
        source,
        (
            "data-testid=\"omi-candidate-approval-disabled-reason\"",
            "data-testid=\"omi-field-approval-disabled-reason\"",
            "aria-describedby={approvalReasonId}",
            "aria-describedby={reasonId}",
            "Approve Candidate for Handoff",
            "Approve field",
            "aria-label={`Approve field ${row.field} for handoff`}",
        ),
        "OMI-CANDIDATE-DISABLED-ASSOCIATIONS",
    )


def test_omi_candidate_detail_no_enabled_apply_or_generated_prose_controls() -> None:
    """Candidate Detail must not enable apply-promotion or expose story prose controls."""

    source = combined_source(
        (
            OMI_CANDIDATE_DETAIL_JSX,
            OMI_CANDIDATE_FIELD_TABLE_JSX,
            OMI_PROMOTION_READINESS_CHECKLIST_JSX,
        )
    )
    lowered = source.lower()

    assert "apply to memory/canon" in lowered
    assert "disabled: apply-promotion requires a completed route-backed confirmation and every handoff gate." in lowered
    assert "submitApplyPromotion" not in source
    assert "createOMIPromotion" not in source
    assert "updateOMICandidateDecision" not in source

    forbidden_control_labels = (
        "rewrite",
        "continue",
        "outline",
        "draft",
        "polish",
        "improve",
        "expand",
        "imitate",
        "generate prose",
        "generated prose",
        "compose",
    )

    assert not [
        label for label in forbidden_control_labels if label in lowered
    ], "OMI candidate detail source must not expose generated-prose controls."


def test_omi_evidence_drawer_stored_review_metadata_only_contract() -> None:
    """Third OMI slice requires a contextual stored-review-metadata-only evidence drawer."""

    source = combined_source(
        (
            OMI_SHELL_JSX,
            OMI_CANDIDATE_DETAIL_JSX,
            OMI_CANDIDATE_FIELD_TABLE_JSX,
            OMI_EVIDENCE_DRAWER_JSX,
        )
    )

    assert_markers_present(
        source,
        (
            "data-testid=\"omi-evidence-drawer\"",
            "data-testid=\"omi-evidence-drawer-trigger\"",
            "data-testid=\"omi-field-evidence-drawer-trigger\"",
            "Evidence scope:",
            "Scope",
            "Source type",
            "Source location",
            "Quote exactness",
            "Confidence/support",
            "Original wording/excerpt",
            "Evidence summary",
            "Supports claim",
            "Limitations / ambiguity",
            "Provenance chain",
            "Related IDs",
            "Timestamps",
            "Source hash",
            "Snapshot hash",
            "Stored source metadata only",
            "Missing",
            "Not linked",
            "Unavailable",
            "Evidence supports review. It is not canon truth until owner approval and apply-promotion are complete.",
            "Viewing evidence does not copy source text into Memory/Canon.",
            "Confidence indicates support strength, not truth.",
            "Source record loading",
            "Source record missing",
            "Source location unsafe",
            "Source location out of range",
            "Source record corrupt",
            "Source record belongs to another project",
            "Source open action unavailable",
            "Source open action failed closed",
            "Source-opening failures must not create fallback summaries or inferred evidence.",
            "role=\"dialog\"",
            "aria-modal=\"true\"",
            "aria-labelledby={titleId}",
            "data-testid=\"omi-evidence-drawer-close-top\"",
            "data-testid=\"omi-evidence-drawer-close-bottom\"",
            "document.addEventListener('keydown', handleKeyDown)",
            "opener.focus()",
            "buildCandidateEvidenceScope",
            "buildFieldEvidenceScope",
        ),
        "OMI-EVIDENCE-DRAWER-STORED-METADATA",
    )


def test_omi_evidence_drawer_disabled_reason_associations_and_footer_groups() -> None:
    """Evidence Drawer source opening and footer controls must be associated and grouped."""

    source = combined_source((OMI_EVIDENCE_DRAWER_JSX,))

    assert_markers_present(
        source,
        (
            "data-testid=\"omi-source-open-disabled-reason\"",
            "aria-describedby={sourceReasonId}",
            "aria-describedby={copyDisabled ? copyReasonId : undefined}",
            "Navigation / copy",
            "Copy source location",
            "Open source record",
            "Review marking",
            "Mark evidence accepted for review",
            "Mark insufficient evidence",
            "Owner note",
            "Add owner note",
            "Close",
            "Close drawer",
            "Disabled: evidence review marking is review metadata only and is not wired in this slice.",
            "Disabled: owner note storage is future review metadata wiring only.",
        ),
        "OMI-EVIDENCE-DRAWER-FOOTER-ASSOCIATIONS",
    )


def test_omi_evidence_drawer_no_apply_promotion_or_generated_prose_controls() -> None:
    """Evidence Drawer must not enable apply-promotion or expose story prose controls."""

    source = combined_source(
        (
            OMI_EVIDENCE_DRAWER_JSX,
            OMI_CANDIDATE_DETAIL_JSX,
            OMI_CANDIDATE_FIELD_TABLE_JSX,
        )
    )
    lowered = source.lower()

    assert "submitApplyPromotion" not in source
    assert "createOMIPromotion" not in source
    assert "updateOMICandidateDecision" not in source
    assert "apply to memory/canon" not in read_source(OMI_EVIDENCE_DRAWER_JSX).lower()

    forbidden_control_labels = (
        "rewrite",
        "continue",
        "outline",
        "draft",
        "polish",
        "improve",
        "expand",
        "imitate",
        "generate prose",
        "generated prose",
        "compose",
    )

    assert not [
        label for label in forbidden_control_labels if label in lowered
    ], "OMI evidence drawer source must not expose generated-prose controls."
