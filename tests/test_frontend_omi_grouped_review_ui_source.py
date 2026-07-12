"""Focused source contract for PHASE8-IMPL-023-T023B grouped owner review."""

from __future__ import annotations

import hashlib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_SRC = REPO_ROOT / "frontend" / "src"
APP = FRONTEND_SRC / "App.jsx"
SHELL = FRONTEND_SRC / "components" / "OMIShell.jsx"
GROUPED_REVIEW = FRONTEND_SRC / "components" / "OMIGroupedReview.jsx"

UNCHANGED_SHA256 = {
    FRONTEND_SRC / "omiGroupedReview.js": "0f813c6aaf06f1747ac64c87ee2383cbeafc1ae057d75b241029d1779606973c",
    REPO_ROOT / "frontend" / "tests" / "omiGroupedReview.test.mjs": "76ce95aac206bbd3663b8364adf780a1c56ddd074650900dfe3221f369272a63",
    FRONTEND_SRC / "api.js": "be637430c152ebaa6d7866dd3c8f7782284dceac4d569adb4275457aae9ee52f",
    REPO_ROOT / "backend" / "main.py": "c86441a7e7a439f7247d5468aacd89bbcdb2ed8889f0ac0c9d375fedb9fe2dba",
    REPO_ROOT / "backend" / "project_manager.py": "ab43a5e790e8b470355b55a070e0168d020b6076a08882d5ae3c03f99c6228ec",
}


def source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


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


def test_t023a_api_and_backend_contract_files_are_unchanged() -> None:
    for path, expected_digest in UNCHANGED_SHA256.items():
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected_digest, path
