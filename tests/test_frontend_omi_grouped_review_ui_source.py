"""Focused source contract for PHASE8-IMPL-023-T023B grouped owner review."""

from __future__ import annotations

import hashlib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_SRC = REPO_ROOT / "frontend" / "src"
APP = FRONTEND_SRC / "App.jsx"
SHELL = FRONTEND_SRC / "components" / "OMIShell.jsx"
DASHBOARD = FRONTEND_SRC / "components" / "OMIDashboard.jsx"
WORKFLOW_STATUS_ROW = FRONTEND_SRC / "components" / "OMIWorkflowStatusRow.jsx"
CANDIDATE_DETAIL = FRONTEND_SRC / "components" / "OMICandidateDetail.jsx"
GROUPED_REVIEW = FRONTEND_SRC / "components" / "OMIGroupedReview.jsx"
APPLY_PROMOTION_ROUTE = FRONTEND_SRC / "components" / "OMIApplyPromotionRoute.jsx"

# The pure grouping helper and focused unit test stay checksum-protected.
# Shared API/backend files may evolve through later accepted application tasks;
# route, wiring, lifecycle, and backend tests validate grouped-review behavior semantically.
T023A_PURE_GROUPING_CONTRACT_SHA256 = {
    FRONTEND_SRC / "omiGroupedReview.js": "0f813c6aaf06f1747ac64c87ee2383cbeafc1ae057d75b241029d1779606973c",
    REPO_ROOT / "frontend" / "tests" / "omiGroupedReview.test.mjs": "76ce95aac206bbd3663b8364adf780a1c56ddd074650900dfe3221f369272a63",
}


def source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def dashboard_row(dashboard: str, area: str) -> str:
    start = dashboard.index(f"area: '{area}'")
    end = dashboard.find("\n    {\n      area:", start)
    if end == -1:
        end = dashboard.index("\n  ];", start)
    return dashboard[start:end]


def test_shell_recognizes_and_renders_grouped_review() -> None:
    shell = source(SHELL)

    assert "import OMIGroupedReview from './OMIGroupedReview.jsx'" in shell
    assert "destination === 'grouped-review'" in shell
    assert "setOmiView('grouped-review')" in shell
    assert "omiView === 'grouped-review'" in shell
    assert "<OMIGroupedReview" in shell
    assert "Grouped Owner Review" in shell
    assert "onBackToDashboard={handleBackToDashboard}" in shell
    assert "setOmiView('dashboard')" in shell


def test_shell_consumes_dashboard_reset_request_through_one_local_reset() -> None:
    shell = source(SHELL)
    reset = shell[
        shell.index("const handleBackToDashboard = useCallback(() => {"):
        shell.index("function handleNavigate")
    ]

    assert "dashboardResetRequest = 0" in shell
    assert "useEffect(() => {" in reset
    assert "handleBackToDashboard();" in reset
    assert "[dashboardResetRequest, handleBackToDashboard]" in reset
    for local_reset in (
        "setOmiView('dashboard')",
        "setSelectedCandidateId('')",
        "setSelectedEvidence(null)",
        "evidenceOpenerRef.current = null",
    ):
        assert reset.count(local_reset) == 1


def test_shell_keeps_inner_navigation_state_and_back_cancel_wiring_local() -> None:
    shell = source(SHELL)

    for shell_owned_state in (
        "const [omiView, setOmiView] = useState('dashboard')",
        "const [selectedCandidateId, setSelectedCandidateId] = useState('')",
        "const [selectedEvidence, setSelectedEvidence] = useState(null)",
        "const evidenceOpenerRef = useRef(null)",
    ):
        assert shell_owned_state in shell

    assert "onCancel={handleBackToDashboard}" in shell
    assert shell.count("onBackToDashboard={handleBackToDashboard}") == 2
    navigate = shell[shell.index("function handleNavigate"):shell.index("function handleOpenEvidence")]
    assert "handleBackToDashboard();" in navigate


def test_dashboard_enables_only_implemented_destination_controls() -> None:
    dashboard = source(DASHBOARD)

    enabled_rows = {
        "Candidates": "candidates",
        "Grouped Review": "grouped-review",
        "Promotion Handoff Readiness": "promotion-handoff",
    }
    for area, destination in enabled_rows.items():
        row = dashboard_row(dashboard, area)
        assert "action:" in row
        assert f"onAction: () => onNavigate('{destination}')" in row
        assert "Unavailable in this version" not in row

    assert "onClick={() => onNavigate('approved-memory-canon')}" in dashboard
    assert 'aria-label="Open Approved Memory/Canon"' in dashboard
    assert "Review promotion readiness" in dashboard
    assert "Open handoff queue" not in dashboard
    assert dashboard.count("onAction: () => onNavigate(") == 3


def test_unavailable_dashboard_rows_are_status_only_without_callbacks() -> None:
    dashboard = source(DASHBOARD)

    for area in (
        "Owner Input",
        "Duplicate Decisions",
        "Promotion Audit Records",
        "Deferred Categories",
        "Warnings / Health",
    ):
        row = dashboard_row(dashboard, area)
        assert "unavailable: 'Unavailable in this version'" in row
        assert "onAction:" not in row

    for unsupported_destination in (
        "owner-input",
        "duplicate-decisions",
        "promotion-audits",
        "deferred-categories",
        "health",
    ):
        assert f"onNavigate('{unsupported_destination}')" not in dashboard


def test_workflow_status_row_renders_button_only_for_actionable_rows() -> None:
    row = source(WORKFLOW_STATUS_ROW)

    assert "row.onAction && row.action ?" in row
    assert row.count("<button") == 1
    assert "onClick={row.onAction}" in row
    assert '<span className="muted-copy">{row.unavailable}</span>' in row


def test_inner_navigation_clears_navigation_scoped_shell_state() -> None:
    shell = source(SHELL)
    navigate = shell[shell.index("function handleNavigate"):shell.index("function handleOpenEvidence")]
    candidates = navigate[
        navigate.index("destination === 'candidates'"):
        navigate.index("destination === 'promotion-handoff'")
    ]
    promotion = navigate[
        navigate.index("destination === 'promotion-handoff'"):
        navigate.index("destination === 'grouped-review'")
    ]
    grouped = navigate[
        navigate.index("destination === 'grouped-review'"):
        navigate.index("destination === 'approved-memory-canon'")
    ]

    assert "const firstCandidateId = getCandidateId(candidates[0])" in candidates
    assert "setSelectedCandidateId(firstCandidateId)" in candidates
    for branch in (candidates, promotion, grouped):
        assert "setSelectedEvidence(null)" in branch
        assert "evidenceOpenerRef.current = null" in branch

    assert "setSelectedCandidateId('')" in grouped
    assert "setOmiView('grouped-review')" in grouped
    assert "candidates.some(" in promotion
    assert "getCandidateId(candidate) === selectedCandidateId" in promotion
    assert "? selectedCandidateId" in promotion
    assert ": getCandidateId(candidates[0])" in promotion
    assert "setOmiView('apply-promotion')" in promotion


def test_memory_canon_and_unknown_destinations_fail_closed_through_reset() -> None:
    shell = source(SHELL)
    navigate = shell[shell.index("function handleNavigate"):shell.index("function handleOpenEvidence")]
    memory = navigate[navigate.index("destination === 'approved-memory-canon'"):]

    assert "handleBackToDashboard();" in memory
    assert "onOpenMemoryCanon();" in memory
    assert memory.index("handleBackToDashboard();") < memory.index("onOpenMemoryCanon();")
    assert navigate.rstrip().endswith("handleBackToDashboard();\n  }")


def test_missing_loading_and_error_return_paths_use_existing_back_callback() -> None:
    candidate = source(CANDIDATE_DETAIL)
    grouped = source(GROUPED_REVIEW)
    candidate_loading = candidate[
        candidate.index("if (isLoading)"):
        candidate.index("if (error)")
    ]
    candidate_error = candidate[
        candidate.index("if (error)"):
        candidate.index("if (storedCandidates.length === 0)")
    ]
    grouped_loading = grouped[
        grouped.index("if (isLoading)"):
        grouped.index("\n  return (\n    <section\n", grouped.index("if (isLoading)"))
    ]

    for state in (candidate_loading, candidate_error, grouped_loading):
        assert "onClick={onBackToDashboard}" in state
        assert "Back to OMI Dashboard" in state


def test_apply_promotion_route_remains_review_only_and_unavailable() -> None:
    route = source(APPLY_PROMOTION_ROUTE)

    assert "applyPromotionAvailable={false}" in route
    assert "onCancel={onCancel}" in route
    assert "submitApplyPromotion" not in source(SHELL)


def test_t006b_navigation_adds_no_runtime_or_mutation_calls() -> None:
    navigation_sources = "\n".join(
        source(path)
        for path in (SHELL, DASHBOARD, WORKFLOW_STATUS_ROW, CANDIDATE_DETAIL)
    )

    for forbidden in (
        "fetch(",
        "axios",
        "callModel",
        "ollama",
        "runStoryCheck",
        "extractOMICandidates",
        "createOMICandidate",
        "createOMIPromotion",
        "submitApplyPromotion",
        "saveMemory",
        "saveCanon",
        "updateMemory",
        "updateCanon",
    ):
        assert forbidden not in navigation_sources


def test_current_inner_route_identities_and_non_mutating_boundary_remain() -> None:
    shell = source(SHELL)

    for route_identity in (
        "import OMICandidateDetail from './OMICandidateDetail.jsx'",
        "import OMIGroupedReview from './OMIGroupedReview.jsx'",
        "import OMIApplyPromotionRoute from './OMIApplyPromotionRoute.jsx'",
        "<OMICandidateDetail",
        "<OMIGroupedReview",
        "<OMIApplyPromotionRoute",
    ):
        assert route_identity in shell

    assert "from '../api.js'" not in shell
    for forbidden_mutation in (
        "fetch(",
        "axios",
        "setOmiData",
        "createOMIPromotion",
        "submitApplyPromotion",
        "saveMemory",
        "saveCanon",
        "updateMemory",
        "updateCanon",
    ):
        assert forbidden_mutation not in shell


def test_app_passes_existing_server_confirmed_handler_and_status_props() -> None:
    app = source(APP)
    shell_call = app[app.index("<OMIShell"):app.index("/>", app.index("<OMIShell"))]

    assert "isUpdating={isUpdatingOMI}" in shell_call
    assert "status={omiStatus}" in shell_call
    assert "error={omiError}" in shell_call
    assert "onUpdateCandidateDecision={handleUpdateOMICandidateDecision}" in shell_call
    handler = app[
        app.index("const handleUpdateOMICandidateDecision"):
        app.index("const handleCreateOMIPromotion")
    ]
    assert "await updateOMICandidateDecision(activeProjectId, candidateId, payload)" in handler
    assert "await refreshOMI()" in handler
    assert "setIsUpdatingOMI(true)" in handler
    assert "setIsUpdatingOMI(false)" in handler


def test_grouped_component_uses_t023a_contract_and_explicit_source_scope() -> None:
    grouped = source(GROUPED_REVIEW)

    assert "buildGroupedReviewModel" in grouped
    assert "selectLinkedReviewCandidates" in grouped
    assert "from '../omiGroupedReview.js'" in grouped
    assert "selectedSourceIdeaId" in grouped
    assert "setSelectedSourceIdeaId" in grouped
    assert "Source idea" in grouped
    assert "Selected source ID:" in grouped
    assert "eligibleSources[0]?.ideaId" in grouped
    assert "sourceIdeaId: selectedSourceIdeaId" in grouped
    assert "idea_2ef4930a04924577a2983e45408bba39" not in grouped


def test_search_adapter_review_uncertainty_and_conflict_filters_exist() -> None:
    grouped = source(GROUPED_REVIEW)

    for marker in (
        'type="search"',
        "Search candidates",
        "Source adapter",
        "Owner decision / review",
        "Uncertainty only",
        "Conflict only",
        "Clear filters",
        "Showing {resultCount} of {model.totalCount}",
        "No candidates match these filters",
    ):
        assert marker in grouped


def test_native_disclosures_and_selected_candidate_detail_exist() -> None:
    grouped = source(GROUPED_REVIEW)

    assert "<details" in grouped
    assert "<summary>" in grouped
    assert "Adapter groups" in grouped
    assert "Finding types:" in grouped
    assert 'aria-current={candidate.candidateId === selectedCandidateId' in grouped
    assert 'aria-label="Selected candidate detail"' in grouped
    for label in (
        "Candidate ID",
        "Source adapter / tool source",
        "Original finding type",
        "Storage candidate type",
        "Extracted or diagnostic claim",
        "Support strength (not truth)",
        "Conflict-group ID",
        "Candidate fingerprint",
        "Evidence fingerprint",
        "Lifecycle status",
        "Stored review status",
        "Evidence count",
        "Source locator",
        "Provenance",
    ):
        assert label in grouped


def test_existing_evidence_drawer_callback_receives_fail_closed_scope() -> None:
    grouped = source(GROUPED_REVIEW)
    shell = source(SHELL)

    assert "Open evidence and provenance" in grouped
    assert "onOpenEvidence(buildEvidenceScope(selectedCandidate), event.currentTarget)" in grouped
    assert "candidateId: candidate?.candidateId" in grouped
    assert "evidenceSummary: evidence" in grouped
    assert "provenanceChain: provenance" in grouped
    assert "sourceOpenState: 'unavailable'" in grouped
    assert "onOpenEvidence={handleOpenEvidence}" in shell
    assert "<OMIEvidenceDrawer" in shell


def test_single_candidate_owner_decisions_and_approval_confirmation_exist() -> None:
    grouped = source(GROUPED_REVIEW)

    assert "pending: 'owner_review'" in grouped
    assert "approve: 'approved'" in grouped
    assert "reject: 'rejected'" in grouped
    assert "needs_revision: 'candidate'" in grouped
    assert "Move to owner review" in grouped
    assert "Approve review lifecycle" in grouped
    assert "Reject candidate" in grouped
    assert "Needs revision" in grouped
    assert "Archived records receive no grouped-review action" in grouped
    assert "I confirm this owner decision approves this candidate for review lifecycle only" in grouped
    assert "approval_confirmed: decision === 'approve' && approvalConfirmed" in grouped
    assert "No batch action is available" in grouped


def test_request_payload_is_bounded_and_waits_for_server_confirmation() -> None:
    grouped = source(GROUPED_REVIEW)
    submit = grouped[
        grouped.index("async function handleDecision"):
        grouped.index("if (isLoading)")
    ]

    assert "const serverRecord = await onUpdateCandidateDecision" in submit
    assert "owner_decision:" in submit
    assert "decision," in submit
    assert "approval_confirmed:" in submit
    assert "decided_by: 'owner'" in submit
    assert "notes," in submit
    assert "status: DECISION_STATUS[decision]" in submit
    for forbidden in (
        "destination:",
        "candidate_content:",
        "promotion:",
        "canon:",
        "memory:",
        "model:",
        "tool:",
        "prose:",
    ):
        assert forbidden not in submit
    assert "setSelectedCandidate" not in submit
    assert "setOmiData" not in submit
    assert "serverRecord.status" not in submit
    assert "The displayed lifecycle is never updated optimistically" in grouped


def test_error_status_pending_and_focus_contracts_exist() -> None:
    grouped = source(GROUPED_REVIEW)

    assert 'role="alert"' in grouped
    assert 'role="status"' in grouped
    assert 'aria-live="polite"' in grouped
    assert "Prior candidate state remains displayed" in grouped
    assert "disabled={requestPending" in grouped
    assert "actionStatusRef.current?.focus()" in grouped
    assert 'tabIndex="-1"' in grouped


def test_grouped_review_has_no_risky_workflow_imports_or_controls() -> None:
    grouped = source(GROUPED_REVIEW)

    for marker in (
        "OMIApplyPromotion",
        "createOMIPromotion",
        "submitApplyPromotion",
        "onOpenApplyPromotion",
        "createOMICandidate",
        "onCreateCandidate",
        "runStoryCheck",
        "extractOMICandidates",
        "callModel",
        "generateProse",
        "rewriteProse",
        "Approve all",
        "Resolve all conflicts",
    ):
        assert marker not in grouped
    assert "from '../api.js'" not in grouped
    assert "fetch(" not in grouped
    assert "axios" not in grouped


def test_static_safety_copy_keeps_review_separate_from_truth_and_canon() -> None:
    grouped = source(GROUPED_REVIEW)

    for boundary in (
        "Queue presence is not approval.",
        "Support and confidence are not truth.",
        "Candidate persistence is not canon.",
        "Tool output is not canon.",
        "Approval does not apply promotion.",
        "Memory/Canon remains unchanged.",
    ):
        assert boundary in grouped


def test_t023a_pure_grouping_contract_files_are_unchanged() -> None:
    for path, expected_digest in T023A_PURE_GROUPING_CONTRACT_SHA256.items():
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected_digest, path
