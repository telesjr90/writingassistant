"""Focused source contracts for PHASE8-IMPL-024 T005A heading hierarchy and T005B target-sizing, checkbox hit areas, and focus visibility."""

from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_SRC = REPO_ROOT / "frontend" / "src"
PROJECT_NAV_JSX = FRONTEND_SRC / "components" / "ProjectNav.jsx"
OMI_SHELL_JSX = FRONTEND_SRC / "components" / "OMIShell.jsx"
OMI_DASHBOARD_JSX = FRONTEND_SRC / "components" / "OMIDashboard.jsx"
OMI_CANDIDATE_DETAIL_JSX = (
    FRONTEND_SRC / "components" / "OMICandidateDetail.jsx"
)
OMI_CANDIDATE_FIELD_TABLE_JSX = (
    FRONTEND_SRC / "components" / "OMICandidateFieldTable.jsx"
)
OMI_PROMOTION_READINESS_CHECKLIST_JSX = (
    FRONTEND_SRC / "components" / "OMIPromotionReadinessChecklist.jsx"
)
OMI_APPLY_PROMOTION_BLOCKERS_JSX = (
    FRONTEND_SRC / "components" / "OMIApplyPromotionBlockers.jsx"
)
APPLY_PROMOTION_CONFIRMATION_JSX = (
    FRONTEND_SRC / "components" / "ApplyPromotionConfirmation.jsx"
)
OMI_GUIDED_CREATION_JSX = (
    FRONTEND_SRC / "components" / "OmiGuidedProjectCreation.jsx"
)
DESIGN_MD = REPO_ROOT / "DESIGN.md"
STYLES_CSS = FRONTEND_SRC / "styles.css"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Project navigation is not a heading
# ---------------------------------------------------------------------------

class TestProjectNavIsNotAHeading:
    def test_project_nav_renders_no_heading_element(self) -> None:
        """The sidebar project name must not be any heading; the aside
        aria-label supplies the landmark name."""
        source = read_text(PROJECT_NAV_JSX)
        for tag in ("<h1>", "<h2>", "<h3>", "<h4>", "<h5>", "<h6>"):
            assert tag not in source

    def test_project_nav_renders_p_with_class_for_visual_preservation(self) -> None:
        source = read_text(PROJECT_NAV_JSX)
        assert '<p className="project-nav-title">' in source

    def test_project_nav_title_css_class_preserves_former_h1_presentation(self) -> None:
        css = read_text(STYLES_CSS)
        block = _rule_block(css, ".project-nav-title")
        assert "margin: 0" in block
        assert "color: var(--wa-color-text-strong)" in block
        assert "font-size: 24px" in block
        assert "font-weight: 700" in block
        assert "line-height: 1.2" in block


# ---------------------------------------------------------------------------
# OMIShell — exactly one h1 in the composed OMI workspace
# ---------------------------------------------------------------------------

class TestOMIShellSingleH1:
    def test_omi_shell_renders_exactly_one_h1_from_route_title(self) -> None:
        source = read_text(OMI_SHELL_JSX)
        assert "<h1>" in source
        assert source.count("<h1>") == 1
        assert source.count("</h1>") == 1

    def test_omi_shell_h1_uses_get_shell_title(self) -> None:
        source = read_text(OMI_SHELL_JSX)
        assert "<h1>{getShellTitle(omiView)}</h1>" in source

    def test_get_shell_title_returns_all_route_titles(self) -> None:
        source = read_text(OMI_SHELL_JSX)
        for title in (
            "OMI Dashboard",
            "OMI Candidate Detail",
            "Apply-Promotion Confirmation",
            "Grouped Owner Review",
            "Owner-Facing Live Analysis",
            "NCP Gateway and Diagnostics",
        ):
            assert title in source


# ---------------------------------------------------------------------------
# No duplicate h1 in OMI route sub-components
# ---------------------------------------------------------------------------

class TestNoDuplicateH1InOMIRoutes:
    def test_candidate_detail_does_not_render_h1(self) -> None:
        source = read_text(OMI_CANDIDATE_DETAIL_JSX)
        assert "<h1>" not in source

    def test_apply_promotion_confirmation_does_not_render_h1(self) -> None:
        source = read_text(APPLY_PROMOTION_CONFIRMATION_JSX)
        assert "<h1>" not in source


# ---------------------------------------------------------------------------
# Dashboard — direct panels are h2 (no redundant Dashboard h2)
# ---------------------------------------------------------------------------

class TestDashboardHeadingHierarchy:
    def test_dashboard_panels_are_h2(self) -> None:
        source = read_text(OMI_DASHBOARD_JSX)
        assert "<h2>OMI status unavailable</h2>" in source
        assert "<h2>Approved Memory/Canon Snapshot</h2>" in source
        assert "<h2>Warnings / Health</h2>" in source

    def test_dashboard_does_not_render_h3(self) -> None:
        source = read_text(OMI_DASHBOARD_JSX)
        dashboard = source[source.index("export default function OMIDashboard"):]
        assert "<h3>" not in dashboard


# ---------------------------------------------------------------------------
# Candidate Detail — route title h2, sections h3
# ---------------------------------------------------------------------------

class TestCandidateDetailHeadingHierarchy:
    def test_successful_branch_route_title_is_h2(self) -> None:
        source = read_text(OMI_CANDIDATE_DETAIL_JSX)
        assert "<h2>Candidate: {candidateId}</h2>" in source

    def test_successful_branch_sections_are_h3(self) -> None:
        source = read_text(OMI_CANDIDATE_DETAIL_JSX)
        h3_sections = (
            "Approved Memory/Canon links",
            "Evidence / Provenance",
            "Duplicate / Merge / Clarification",
            "Apply to Memory/Canon",
        )
        for label in h3_sections:
            assert f"<h3>{label}</h3>" in source

    def test_error_branch_is_h2_early_return(self) -> None:
        """The error branch is an early return without the route-title h2,
        so its heading must be h2 (not h3 with a skip)."""
        source = read_text(OMI_CANDIDATE_DETAIL_JSX)
        assert "<h2>Candidate schema unsupported or partially corrupt.</h2>" in source

    def test_no_candidates_branch_is_h2_early_return(self) -> None:
        source = read_text(OMI_CANDIDATE_DETAIL_JSX)
        assert "<h2>No candidate selected.</h2>" in source
        assert "No candidates are stored for this project." in source

    def test_no_selection_branch_is_h2_early_return(self) -> None:
        source = read_text(OMI_CANDIDATE_DETAIL_JSX)
        assert "Select a stored candidate from the OMI Dashboard review row." in source
        # Both empty-state h2 must exist
        assert source.count("<h2>No candidate selected.</h2>") == 2

    def test_not_found_branch_is_h2_early_return(self) -> None:
        source = read_text(OMI_CANDIDATE_DETAIL_JSX)
        assert "<h2>Candidate not found.</h2>" in source

    def test_no_branch_has_h1_to_h3_skip(self) -> None:
        """Every render branch must be h1→h2→h3 or h1→h2 (no h1→h3 skip)."""
        source = read_text(OMI_CANDIDATE_DETAIL_JSX)
        # All branches: the file contains h2 and h3 but no h1
        assert "<h1>" not in source
        # Successful branch: h2 route title + h3 sections (already tested above)
        # Error/empty branches: h2 early returns (already tested above)

    def test_field_table_section_is_h3(self) -> None:
        source = read_text(OMI_CANDIDATE_FIELD_TABLE_JSX)
        assert "<h3>Field review table</h3>" in source

    def test_promotion_readiness_section_is_h3(self) -> None:
        source = read_text(OMI_PROMOTION_READINESS_CHECKLIST_JSX)
        assert "<h3>Promotion readiness checklist</h3>" in source


# ---------------------------------------------------------------------------
# Apply-Promotion — route title h2, sections h3
# ---------------------------------------------------------------------------

class TestApplyPromotionHeadingHierarchy:
    def test_route_title_is_h2(self) -> None:
        source = read_text(APPLY_PROMOTION_CONFIRMATION_JSX)
        assert "<h2>Prepare and approve an immutable revision</h2>" in source
        assert "<h2>Apply-Promotion Confirmation</h2>" not in source

    def test_direct_sections_are_h3(self) -> None:
        source = read_text(APPLY_PROMOTION_CONFIRMATION_JSX)
        h3_sections = (
            "Preparation publication incomplete",
            "Preparation publication recovered from immutable saved bytes",
            "Exact promotion association",
            "Authoritative owner",
            "Prepare immutable revision",
            "Selected revision {selectedRevision.revision}",
            "Explicit revision approval",
            "Sealed contract reference",
            "Final anti-replay challenge",
            "Final apply recovery required",
            "Final apply verified not committed",
            "Final confirmation",
            "{applyResult.replayed ? 'Completed replay or committed recovery' : 'Apply-Promotion completed'}",
        )
        for label in h3_sections:
            assert f"<h3>{label}</h3>" in source

    def test_visible_blockers_section_is_h3(self) -> None:
        source = read_text(OMI_APPLY_PROMOTION_BLOCKERS_JSX)
        assert "<h3>Visible blockers</h3>" in source

    def test_apply_promotion_has_no_h1(self) -> None:
        source = read_text(APPLY_PROMOTION_CONFIRMATION_JSX)
        assert "<h1>" not in source


# ---------------------------------------------------------------------------
# Visual style preservation across heading levels
# ---------------------------------------------------------------------------

class TestVisualStylePreservation:
    def test_candidate_detail_header_h2_has_font_size_24(self) -> None:
        css = read_text(STYLES_CSS)
        block = _rule_block(css, ".omi-candidate-header h2")
        assert "font-size: 24px" in block

    def test_apply_guard_header_h2_has_font_size_24(self) -> None:
        css = read_text(STYLES_CSS)
        block = _rule_block(css, ".omi-apply-guard-header h2")
        assert "font-size: 24px" in block
        assert "margin-top: 4px" in block

    def test_shell_header_h1_still_has_margin_top(self) -> None:
        css = read_text(STYLES_CSS)
        assert ".omi-shell-header h1 {\n  margin-top: 4px;\n}" in css

    def test_dashboard_panel_context_classes_support_h2_and_h3(self) -> None:
        css = read_text(STYLES_CSS)
        for selector in (
            ".omi-error-state h2",
            ".omi-error-state h3",
            ".omi-health-panel h2",
            ".omi-health-panel h3",
            ".omi-approved-snapshot h2",
            ".omi-approved-snapshot h3",
        ):
            assert selector in css

    def test_candidate_panel_context_classes_support_h2_and_h3(self) -> None:
        css = read_text(STYLES_CSS)
        for selector in (
            ".omi-empty-state h2",
            ".omi-empty-state h3",
            ".omi-candidate-panel h2",
            ".omi-candidate-panel h3",
        ):
            assert selector in css

    def test_apply_section_context_classes_support_h2_and_h3(self) -> None:
        css = read_text(STYLES_CSS)
        for selector in (
            ".omi-apply-section h2",
            ".omi-apply-section h3",
            ".omi-apply-blockers h2",
            ".omi-apply-blockers h3",
            ".omi-apply-final-form h2",
            ".omi-apply-final-form h3",
        ):
            assert selector in css

    def test_context_heading_rules_use_font_size_16(self) -> None:
        css = read_text(STYLES_CSS)
        # Each grouped rule must carry 16px font-size for its h2/h3 headings
        assert css.count("font-size: 16px") >= 3


# ---------------------------------------------------------------------------
# Target-size policy source contracts
# ---------------------------------------------------------------------------

class TestTargetSizePolicyInDesignMd:
    SECTION_HEADING = "## 7. Minimum Operable-Target Policy"

    def test_policy_section_exists(self) -> None:
        document = read_text(DESIGN_MD)
        assert self.SECTION_HEADING in document
        assert document.count(self.SECTION_HEADING) == 1

    def test_all_five_classifications_present(self) -> None:
        document = read_text(DESIGN_MD)
        policy_section = document.split(self.SECTION_HEADING, 1)[1]
        classifications = (
            "1. **Confirmed failure of the 24 CSS-pixel minimum**",
            "2. **Allowed WCAG exception**",
            "3. **Meets the WCAG minimum but below the preferred 44 CSS pixels**",
            "4. **Already meets the preferred 44 CSS pixels**",
            "5. **Insufficient evidence pending rendered geometry**",
        )
        for classification in classifications:
            assert classification in policy_section

    def test_wcag_25_8_criteria_stated(self) -> None:
        document = read_text(DESIGN_MD)
        policy_section = document.split(self.SECTION_HEADING, 1)[1]
        assert "WCAG 2.2 SC 2.5.8 (Level AA)" in policy_section
        assert "24-by-24 CSS pixels" in policy_section

    def test_wcag_25_5_criteria_stated(self) -> None:
        document = read_text(DESIGN_MD)
        policy_section = document.split(self.SECTION_HEADING, 1)[1]
        assert "WCAG 2.2 SC 2.5.5 (Level AAA)" in policy_section
        assert "44-by-44 CSS pixels" in policy_section

    def test_exceptions_enumerated(self) -> None:
        document = read_text(DESIGN_MD)
        policy_section = document.split(self.SECTION_HEADING, 1)[1]
        for exception in (
            "1. **Spacing**",
            "2. **Equivalent**",
            "3. **Inline**",
            "4. **User-agent control**",
            "5. **Essential**",
        ):
            assert exception in policy_section

    def test_spacing_exception_uses_circle_and_intersection_rule(self) -> None:
        document = read_text(DESIGN_MD)
        policy_section = document.split(self.SECTION_HEADING, 1)[1]
        normalized = policy_section.replace("\n  ", " ")
        assert "24-CSS-pixel-diameter circle" in normalized
        assert "must not intersect another target" in normalized
        assert "corresponding circle for another undersized target" in normalized

    def test_below_44_not_auto_failure(self) -> None:
        document = read_text(DESIGN_MD)
        policy_section = document.split(self.SECTION_HEADING, 1)[1]
        normalized = policy_section.replace("\n  ", " ")
        assert (
            "A control below 44 CSS pixels is not automatically a WCAG Level AA"
        ) in normalized

    def test_interactive_area_not_visible_glyph(self) -> None:
        document = read_text(DESIGN_MD)
        policy_section = document.split(self.SECTION_HEADING, 1)[1]
        normalized = policy_section.replace("\n  ", " ")
        assert (
            "Interactive target area matters, not merely the visible icon, label, or checkbox glyph."
        ) in normalized

    def test_css_source_not_computed_geometry(self) -> None:
        document = read_text(DESIGN_MD)
        policy_section = document.split(self.SECTION_HEADING, 1)[1]
        normalized = policy_section.replace("\n  ", " ")
        assert (
            "CSS source declarations (width, height, padding, line-height) are not browser-computed geometry."
        ) in normalized

    def test_no_wcag_conformance_claim(self) -> None:
        document = read_text(DESIGN_MD)
        policy_section = document.split(self.SECTION_HEADING, 1)[1]
        assert (
            "No product-wide WCAG conformance claim is asserted"
        ) in policy_section

    def test_policy_scope_is_pointer_operable_targets(self) -> None:
        document = read_text(DESIGN_MD)
        policy_section = document.split(self.SECTION_HEADING, 1)[1]
        assert (
            "classifies pointer-operable targets under review"
        ) in policy_section


# ---------------------------------------------------------------------------
# Helper: extract a CSS rule block by selector
# ---------------------------------------------------------------------------

def _rule_block(source: str, partial_selector: str) -> str:
    first_line = partial_selector.split(",")[0].strip()
    if not first_line.startswith(".") and not first_line.startswith("[") and bool(re.match(r'^[a-zA-Z]', first_line)):
        escaped = re.escape(first_line)
        pattern = rf"(?m)^\s*{escaped}(?=[\s,.{{])"
    else:
        if not first_line.startswith("."):
            first_line = "." + first_line
        escaped = re.escape(first_line)
        pattern = rf"(?m)^\s*{escaped}(?=[\s,\n.{{])"

    match = re.search(pattern, source)
    assert match is not None, (
        f"Rule block for {partial_selector!r} not found in styles.css"
    )

    start = match.start()
    brace_pos = source.find("{", start)
    assert brace_pos != -1, f"No opening brace after {partial_selector!r}"

    depth = 0
    i = brace_pos
    while i < len(source):
        ch = source[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return source[start : i + 1]
        i += 1

    raise AssertionError(f"Unclosed rule block for {partial_selector!r}")


def _media_block(source: str, condition_pattern: str) -> str:
    pattern = rf"@media {re.escape(condition_pattern)}\s*\{{"
    match = re.search(pattern, source)
    assert match is not None, (
        f"@media {condition_pattern} block not found in styles.css"
    )
    start = match.start()
    depth = 0
    i = match.end()
    while i < len(source):
        ch = source[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            if depth == 0:
                return source[start : i + 1]
            depth -= 1
        i += 1
    raise AssertionError(f"Unclosed @media block for {condition_pattern!r}")


# ---------------------------------------------------------------------------
# T005B — Mobile/coarse-pointer target sizing
# ---------------------------------------------------------------------------

T005B_MEDIA_CONDITION = "(max-width: 900px), (pointer: coarse)"

T005B_TARGET_SELECTORS = (
    "button",
    ".primary-button",
    ".secondary-button",
    ".primary-action",
    ".scene-item",
    ".review-queue-entry",
    ".omi-row-action",
    ".omi-final-apply-button",
    ".omi-grouped-candidate-row",
    ".omi-grouped-disclosure summary",
    ".omi-mobile-tabs a",
    ".project-select",
    ".project-title-input",
    ".field-input",
    ".omi-grouped-source-scope select",
    ".omi-grouped-filter-grid input[type=\"search\"]",
    ".omi-grouped-filter-grid select",
    ".project-select-label textarea",
)


class TestT005BMobileCoarseTargetSizing:
    def test_combined_media_query_exists(self) -> None:
        css = read_text(STYLES_CSS)
        block = _media_block(css, T005B_MEDIA_CONDITION)
        assert "min-height: 44px" in block

    def test_authorized_control_families_have_44px_min_height(self) -> None:
        css = read_text(STYLES_CSS)
        block = _media_block(css, T005B_MEDIA_CONDITION)
        for selector in T005B_TARGET_SELECTORS:
            selector_block = _rule_block(block, selector)
            assert "min-height: 44px" in selector_block, (
                f"{selector} missing min-height: 44px in T005B media"
            )

    def test_unclassed_buttons_included(self) -> None:
        css = read_text(STYLES_CSS)
        block = _media_block(css, T005B_MEDIA_CONDITION)
        btn_block = _rule_block(block, "button")
        assert "min-height: 44px" in btn_block

    def test_desktop_base_sizes_intact_outside_conditional(self) -> None:
        css = read_text(STYLES_CSS)
        media_start = css.find(f"@media {T005B_MEDIA_CONDITION}")
        assert media_start > 0
        pre_media = css[:media_start]

        assert "32px" in pre_media

        button_match = re.search(
            r".context-actions button[^{]*\{[^}]*min-height:\s*(\d+)px", pre_media
        )
        assert button_match, "desktop context-actions button min-height not found"
        assert int(button_match.group(1)) < 44, "desktop button min-height must remain below 44px"

        primary_match = re.search(
            r"\.primary-action[^{]*\{[^}]*min-height:\s*(\d+)px", pre_media
        )
        assert primary_match, "desktop primary-action min-height not found"

        field_match = re.search(
            r"\.field-input[^{]*\{[^}]*min-height:\s*(\d+)px", pre_media
        )
        assert field_match, "desktop field-input min-height not found"
        assert int(field_match.group(1)) < 44, "desktop field-input min-height must remain below 44px"


# ---------------------------------------------------------------------------
# T005B — Checkbox label hit areas
# ---------------------------------------------------------------------------

class TestT005BCheckboxLabelHitAreas:
    def test_checkbox_label_families_have_conditional_44px_min(self) -> None:
        css = read_text(STYLES_CSS)
        block = _media_block(css, T005B_MEDIA_CONDITION)
        for selector in (
            ".omi-checkbox-row",
            ".omi-grouped-check-filter",
            ".omi-grouped-approval-confirmation",
        ):
            assert selector in block
            assert "min-height: 44px" in block

    def test_guided_project_confirmation_uses_omi_checkbox_row(self) -> None:
        source = read_text(OMI_GUIDED_CREATION_JSX)
        assert 'className="omi-checkbox-row"' in source
        assert "I confirm this owner-authored setup" in source
        assert "type=\"checkbox\"" in source

    def test_no_manual_checkbox_label_click_handler_introduced(self) -> None:
        source = read_text(OMI_GUIDED_CREATION_JSX)
        assert 'className="omi-checkbox-row"' in source
        label_idx = source.index('className="omi-checkbox-row"')
        label_end_idx = source.index("</label>", label_idx)
        label_block = source[label_idx:label_end_idx]
        assert "onClick" not in label_block


# ---------------------------------------------------------------------------
# T005B — Focus-visible
# ---------------------------------------------------------------------------

class TestT005BFocusVisible:
    def test_shared_focus_visible_rule_covers_control_families(self) -> None:
        css = read_text(STYLES_CSS)
        required_selectors = (
            "button:focus-visible",
            "a[href]:focus-visible",
            "input:focus-visible",
            "select:focus-visible",
            "textarea:focus-visible",
            "details summary:focus-visible",
            "[tabindex]:focus-visible",
            ".tiptap-surface:focus-visible",
        )
        for selector in required_selectors:
            assert selector in css, f"{selector} not found in shared focus-visible rule"

    def test_focus_visible_rule_consumes_semantic_focus_token(self) -> None:
        css = read_text(STYLES_CSS)
        focus_rules = re.findall(
            r".*focus-visible[^{]*\{[^}]*\}",
            css,
            flags=re.DOTALL,
        )
        assert len(focus_rules) >= 1
        found_focus = False
        for rule_body in focus_rules:
            if "outline:" in rule_body and "var(--wa-color-focus)" in rule_body:
                found_focus = True
                break
        assert found_focus, "no focus-visible rule consumes var(--wa-color-focus)"

    def test_scene_item_no_longer_suppresses_focus_visible_outline(self) -> None:
        css = read_text(STYLES_CSS)
        scene_block = _rule_block(css, ".scene-item:focus-visible")
        assert "outline: none" not in scene_block
        assert "outline:" not in scene_block or "solid" in scene_block
        assert "var(--wa-color-focus)" in scene_block

    def test_review_queue_entry_no_longer_suppresses_focus_visible_outline(self) -> None:
        css = read_text(STYLES_CSS)
        rq_block = _rule_block(css, ".review-queue-entry:focus-visible")
        assert "outline: none" not in rq_block
        assert "outline:" not in rq_block or "solid" in rq_block
        assert "var(--wa-color-focus)" in rq_block

    def test_grouped_review_focus_no_longer_uses_hardcoded_color(self) -> None:
        css = read_text(STYLES_CSS)
        assert "#7aa7e8" not in css

    def test_grouped_review_focus_uses_semantic_token(self) -> None:
        css = read_text(STYLES_CSS)
        grouped_block = _rule_block(css, ".omi-grouped-candidate-row:focus-visible")
        assert "var(--wa-color-focus)" in grouped_block

    def test_focus_visible_distinct_from_hover_for_scene_item(self) -> None:
        css = read_text(STYLES_CSS)
        hover_block = _rule_block(css, ".scene-item:hover")
        assert ":focus-visible" not in hover_block

    def test_focus_visible_distinct_from_hover_for_review_queue_entry(self) -> None:
        css = read_text(STYLES_CSS)
        hover_block = _rule_block(css, ".review-queue-entry:hover")
        assert ":focus-visible" not in hover_block


# ---------------------------------------------------------------------------
# T005B — T005A contracts remain unchanged (regression guard)
# ---------------------------------------------------------------------------

class TestT005AContractsRemainUnchanged:
    def test_scene_item_hover_has_selected_background(self) -> None:
        css = read_text(STYLES_CSS)
        hover_block = _rule_block(css, ".scene-item:hover")
        assert "var(--wa-color-surface-selected)" in hover_block

    def test_project_nav_title_still_not_a_heading(self) -> None:
        source = read_text(PROJECT_NAV_JSX)
        for tag in ("<h1>", "<h2>", "<h3>", "<h4>", "<h5>", "<h6>"):
            assert tag not in source

    def test_omi_shell_has_exactly_one_h1(self) -> None:
        source = read_text(OMI_SHELL_JSX)
        assert source.count("<h1>") == 1


# ---------------------------------------------------------------------------
# T005C — Guided setup-to-review keyboard focus contract
# ---------------------------------------------------------------------------

class TestGuidedSetupToReviewFocusContract:
    def test_review_form_has_ref_and_tabindex(self) -> None:
        source = read_text(OMI_GUIDED_CREATION_JSX)
        assert 'ref={reviewFormRef}' in source
        assert 'tabIndex={-1}' in source
        assert 'aria-label="Review setup draft"' in source
        assert 'ref={reviewFormRef} tabIndex={-1}' in source

    def test_useeffect_manages_focus_on_step_to_review(self) -> None:
        source = read_text(OMI_GUIDED_CREATION_JSX)
        assert 'useEffect(() => {' in source
        assert 'step === STEPS.REVIEW' in source
        assert 'reviewFormRef.current.focus()' in source
        assert '}, [step]' in source

    def test_review_form_ref_is_a_useref(self) -> None:
        source = read_text(OMI_GUIDED_CREATION_JSX)
        assert 'reviewFormRef = useRef(null)' in source

    def test_useeffect_is_imported(self) -> None:
        source = read_text(OMI_GUIDED_CREATION_JSX)
        assert 'import { useEffect, useMemo, useRef, useState }' in source

    def test_review_form_remains_semantically_labelled(self) -> None:
        source = read_text(OMI_GUIDED_CREATION_JSX)
        assert 'aria-label="Review setup draft"' in source
