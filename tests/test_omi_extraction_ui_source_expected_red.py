from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_SRC = REPO_ROOT / "frontend" / "src"

API_JS = FRONTEND_SRC / "api.js"
OMI_PANEL = FRONTEND_SRC / "components" / "OMIPanel.jsx"
OMI_CANDIDATE_DETAIL = FRONTEND_SRC / "components" / "OMICandidateDetail.jsx"
OMI_CANDIDATE_FIELD_TABLE = FRONTEND_SRC / "components" / "OMICandidateFieldTable.jsx"
OMI_PROMOTION_READINESS_CHECKLIST = (
    FRONTEND_SRC / "components" / "OMIPromotionReadinessChecklist.jsx"
)


def read_source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def combined_extraction_source() -> str:
    return "\n".join(
        read_source(path)
        for path in (
            API_JS,
            OMI_PANEL,
            OMI_CANDIDATE_DETAIL,
            OMI_CANDIDATE_FIELD_TABLE,
            OMI_PROMOTION_READINESS_CHECKLIST,
        )
    )


def test_frontend_api_exposes_raw_idea_extraction_helper_expected_red() -> None:
    source = read_source(API_JS)

    assert "extractOMICandidates" in source
    assert "/omi/extractions" in source
    assert "raw_idea" in source
    assert "source_idea_id" in source
    assert "persist_candidates" in source


def test_omi_panel_has_extraction_action_status_and_result_surface_expected_red() -> None:
    source = read_source(OMI_PANEL)

    expected_markers = [
        "onExtractCandidates",
        "isExtractingCandidates",
        "extractionStatus",
        "extractionResult",
        'data-testid="omi-extraction-action"',
        'data-testid="omi-extraction-status"',
        'data-testid="omi-extraction-result"',
        'aria-label="Extract candidates from raw idea"',
    ]
    for marker in expected_markers:
        assert marker in source


def test_omi_panel_groups_extracted_candidates_by_type_expected_red() -> None:
    source = read_source(OMI_PANEL)

    assert "groupExtractedCandidatesByType" in source
    assert 'data-testid="omi-extracted-candidate-groups"' in source
    assert 'data-testid="omi-extracted-candidate-group"' in source
    for candidate_type in (
        "character",
        "location",
        "timeline_event",
        "relationship",
        "organization",
        "object",
        "plot_thread",
        "story_fact",
        "open_question",
        "storyform_context",
    ):
        assert candidate_type in source


def test_candidate_detail_has_extraction_claim_evidence_and_provenance_expected_red() -> None:
    source = "\n".join(
        read_source(path)
        for path in (OMI_CANDIDATE_DETAIL, OMI_CANDIDATE_FIELD_TABLE)
    )

    expected_markers = [
        "extracted_claim",
        "source_excerpt",
        "source_locator",
        "support_strength",
        "support strength, not truth",
        'data-testid="omi-extracted-candidate-detail"',
        'data-testid="omi-extracted-candidate-evidence"',
        'data-testid="omi-extracted-candidate-provenance"',
    ]
    for marker in expected_markers:
        assert marker in source


def test_empty_fail_closed_extraction_state_and_safety_copy_expected_red() -> None:
    source = combined_extraction_source()

    expected_markers = [
        'data-testid="omi-extraction-empty-state"',
        'data-testid="omi-extraction-fail-closed-state"',
        "No evidence-backed candidates were extracted",
        "Extraction failed closed",
        "Extracted candidates are not Memory/Canon",
        "Extraction does not enable apply-promotion",
        "Queue presence is not approval",
        "Candidate persistence is not canon",
    ]
    for marker in expected_markers:
        assert marker in source


def test_extraction_ui_keeps_generated_prose_and_auto_promotion_controls_absent() -> None:
    source = combined_extraction_source().lower()

    forbidden_markers = [
        "generateomiprose",
        "generate omi prose",
        "rewrite extracted prose",
        "continue extracted story",
        "polish extracted prose",
        "improve extracted prose",
        "autopromote",
        "auto apply-promotion",
        "autoapplypromotion",
        "apply extracted candidates automatically",
        "mutatememory",
        "mutatecanon",
    ]
    for marker in forbidden_markers:
        assert marker not in source
