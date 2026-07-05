from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_SRC = REPO_ROOT / "frontend" / "src"

OMI_PANEL = FRONTEND_SRC / "components" / "OMIPanel.jsx"
OMI_CANDIDATE_DETAIL = FRONTEND_SRC / "components" / "OMICandidateDetail.jsx"
OMI_CANDIDATE_FIELD_TABLE = FRONTEND_SRC / "components" / "OMICandidateFieldTable.jsx"
OMI_PROMOTION_READINESS_CHECKLIST = (
    FRONTEND_SRC / "components" / "OMIPromotionReadinessChecklist.jsx"
)
API_JS = FRONTEND_SRC / "api.js"


def read_source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def combined_omi_source() -> str:
    return "\n".join(
        read_source(path)
        for path in (
            OMI_PANEL,
            OMI_CANDIDATE_DETAIL,
            OMI_CANDIDATE_FIELD_TABLE,
            OMI_PROMOTION_READINESS_CHECKLIST,
            API_JS,
        )
    )


def test_empty_candidate_shell_and_extraction_unavailable_labels_are_visible() -> None:
    source = combined_omi_source()

    assert 'data-testid="omi-empty-candidate-shell-warning"' in source
    assert 'data-testid="omi-extraction-unavailable-notice"' in source
    assert (
        "This is a manual candidate shell. No extraction has populated characters, "
        "locations, timeline, or story facts."
    ) in source
    assert (
        "Automatic extraction of characters, locations, timeline, and other story facts "
        "is not available from this screen yet."
    ) in source
    assert "isEmptyManualCandidateShell" in source


def test_approval_copy_is_lifecycle_only_and_keeps_memory_canon_unchanged() -> None:
    source = combined_omi_source()

    assert "Owner decision approved." in source
    assert "Approval does not extract new fields." in source
    assert "Approval does not mutate Memory/Canon." in source
    assert "Promotion remains separate/guarded." in source
    assert "Approval cannot be saved until confirmation is checked." in source
    assert "approval is status metadata only" in source


def test_decision_form_maps_decisions_to_backend_valid_statuses() -> None:
    source = read_source(OMI_PANEL)

    assert "DECISION_STATUS_RULES" in source
    assert "approve: {" in source
    assert "status: 'approved'" in source
    assert "reject: {" in source
    assert "status: 'rejected'" in source
    assert "needs_revision: {" in source
    assert "status: 'candidate'" in source
    assert "pending: {" in source
    assert "status: 'owner_review'" in source
    assert "disabled={isUpdating || statusIsLocked}" in source
    assert "decision !== 'approve' || approvalConfirmed" in source


def test_backend_400_validation_reason_is_rendered_without_success_reset() -> None:
    panel_source = read_source(OMI_PANEL)
    api_source = read_source(API_JS)

    assert 'data-testid="omi-decision-error"' in panel_source
    assert "onError(updateError instanceof Error ? updateError.message" in panel_source
    assert "Request failed (${status}): ${detailText}" in api_source
    assert "typeof detail === 'string' ? detail : JSON.stringify(detail)" in api_source


def test_empty_approved_candidate_is_not_described_as_extracted_or_promotion_ready() -> None:
    source = combined_omi_source()

    assert "Manual candidate shell has no extracted fields, summary, or evidence." in source
    assert "An empty approved candidate has not captured real story facts." in source
    assert "Empty manual shells are not evidence that story facts were captured." in source
    assert "manual shell; extraction unavailable here" in source
    assert "extracted successfully" not in source.lower()
    assert "characters extracted" not in source.lower()
    assert "locations extracted" not in source.lower()
    assert "timeline extracted" not in source.lower()


def test_no_generated_prose_or_apply_promotion_execution_controls_were_added() -> None:
    source = "\n".join(
        read_source(path)
        for path in (
            OMI_PANEL,
            OMI_CANDIDATE_DETAIL,
            OMI_CANDIDATE_FIELD_TABLE,
            OMI_PROMOTION_READINESS_CHECKLIST,
        )
    )

    forbidden_markers = (
        "runStoryCheck(",
        "runStoryCheckForSelectedSource(",
        "applyOMIPromotion",
        "apply_omi_promotion",
        "mutateMemory",
        "mutateCanon",
    )
    for marker in forbidden_markers:
        assert marker not in source


def test_storyform_missing_is_labeled_as_context_readiness_not_omi_extraction() -> None:
    source = combined_omi_source()

    assert (
        "Missing storyform or storyform context is Story Check/context readiness. "
        "It is not OMI raw idea extraction failure."
    ) in source
