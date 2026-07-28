"""Focused source contracts for PHASE8-IMPL-024 T005A heading hierarchy and minimum operable-target policy."""

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
        assert "<h3>" not in source


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
        assert "<h2>Apply-Promotion Confirmation</h2>" in source

    def test_direct_sections_are_h3(self) -> None:
        source = read_text(APPLY_PROMOTION_CONFIRMATION_JSX)
        h3_sections = (
            "Candidate Snapshot",
            "Destination",
            "Evidence / Provenance Summary",
            "Source Location Summary",
            "Duplicate / Link / Dependency Summary",
            "Approved Memory/Canon Before-State",
            "Promotion Audit Record",
            "Failure Safety",
            "Owner Final Confirmation",
        )
        for label in h3_sections:
            assert f"<h3>{label}</h3>" in source

    def test_visible_blockers_section_is_h3(self) -> None:
        source = read_text(OMI_APPLY_PROMOTION_BLOCKERS_JSX)
        assert "<h3>Visible Blockers</h3>" in source

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
    if not first_line.startswith("."):
        first_line = "." + first_line
    escaped = re.escape(first_line)

    pattern = rf"(?m)^{escaped}(?=[\s,\n.{{])"
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
