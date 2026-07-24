"""Source contracts for PHASE8-IMPL-024 T004A+T004B responsive containment."""

from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
STYLES_CSS = REPO_ROOT / "frontend" / "src" / "styles.css"
PROJECT_NAV_JSX = REPO_ROOT / "frontend" / "src" / "components" / "ProjectNav.jsx"
OMI_GUIDED_CREATION_JSX = (
    REPO_ROOT / "frontend" / "src" / "components" / "OmiGuidedProjectCreation.jsx"
)
APP_JSX = REPO_ROOT / "frontend" / "src" / "App.jsx"
DASHBOARD_JSX = REPO_ROOT / "frontend" / "src" / "components" / "OMIDashboard.jsx"
FIELD_TABLE_JSX = (
    REPO_ROOT / "frontend" / "src" / "components" / "OMICandidateFieldTable.jsx"
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def styles_css() -> str:
    return read_text(STYLES_CSS)


def project_nav_source() -> str:
    return read_text(PROJECT_NAV_JSX)


def omi_guided_creation_source() -> str:
    return read_text(OMI_GUIDED_CREATION_JSX)


def app_source() -> str:
    return read_text(APP_JSX)


def dashboard_source() -> str:
    return read_text(DASHBOARD_JSX)


def field_table_source() -> str:
    return read_text(FIELD_TABLE_JSX)


# ---------------------------------------------------------------------------
# CSS rule extraction
# ---------------------------------------------------------------------------

def _rule_block(source: str, partial_selector: str) -> str:
    """Return the first CSS rule block whose selector starts with `partial_selector`.

    Handles multi-line selectors separated by commas by matching on the first
    line of the selector group.
    """
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


def _rule_body(source: str, selector: str) -> str:
    return _rule_block(source, selector)


# ---------------------------------------------------------------------------
# Root containment chain (T004A)
# ---------------------------------------------------------------------------

class TestRootContainmentChain:
    def test_app_shell_is_root_flex_shell(self) -> None:
        css = styles_css()
        block = _rule_body(css, ".app-shell")
        assert "display: flex" in block
        assert "width: 100%" in block

    def test_app_shell_children_can_shrink(self) -> None:
        css = styles_css()
        nav_block = _rule_body(css, ".project-nav")
        assert "min-width: 0" in nav_block

        editor_block = _rule_body(css, ".editor-column")
        assert "min-width: 0" in editor_block

    def test_no_document_level_overflow_masking(self) -> None:
        css = styles_css()
        assert "overflow-x: hidden" not in css

    def test_900px_breakpoint_preserved(self) -> None:
        css = styles_css()
        assert "@media (max-width: 900px)" in css


# ---------------------------------------------------------------------------
# Form and label containment (T004A)
# ---------------------------------------------------------------------------

class TestFormLabelContainment:
    def test_project_select_label_has_shrinkable_column_layout(self) -> None:
        css = styles_css()
        block = _rule_body(css, ".project-select-label")
        assert "display: flex" in block
        assert "flex-direction: column" in block
        assert "min-width: 0" in block

    def test_project_select_has_bounded_width(self) -> None:
        css = styles_css()
        block = _rule_body(css, ".project-select")
        assert "max-width: 100%" in block
        assert "min-width: 0" in block

    def test_project_title_input_has_bounded_width(self) -> None:
        css = styles_css()
        block = _rule_body(css, ".project-title-input")
        assert "max-width: 100%" in block
        assert "min-width: 0" in block

    def test_unclassed_textarea_in_project_select_label_has_bounded_width(self) -> None:
        css = styles_css()
        assert ".project-select-label textarea" in css
        block = _rule_body(css, ".project-select-label textarea")
        assert "max-width: 100%" in block
        assert "min-width: 0" in block

    def test_project_selector_section_can_shrink(self) -> None:
        css = styles_css()
        block = _rule_body(css, ".project-selector")
        assert "min-width: 0" in block


# ---------------------------------------------------------------------------
# Desktop navigation and sidebar widths preserved (T004A)
# ---------------------------------------------------------------------------

class TestDesktopPreservedWidths:
    def test_project_nav_desktop_flex_basis_preserved(self) -> None:
        css = styles_css()
        assert "flex: 0 0 260px" in css

    def test_analysis_sidebar_desktop_flex_basis_preserved(self) -> None:
        css = styles_css()
        assert "flex: 0 0 320px" in css

    def test_editor_column_stays_shrinkable(self) -> None:
        css = styles_css()
        block = _rule_body(css, ".editor-column")
        assert "flex: 1 1 auto" in block
        assert "min-width: 0" in block


# ---------------------------------------------------------------------------
# Story Check selector presence (T004A)
# ---------------------------------------------------------------------------

class TestStoryCheckSelectorPresence:
    def test_story_check_selector_has_expected_testid(self) -> None:
        source = project_nav_source()
        assert 'data-testid="ux2-selected-story-check-source"' in source

    def test_story_check_selector_is_a_select_element(self) -> None:
        source = project_nav_source()
        assert "<select" in source
        assert 'data-testid="ux2-selected-story-check-source"' in source

    def test_story_check_selector_has_accessible_label(self) -> None:
        source = project_nav_source()
        assert 'aria-label="Select project-scoped Story Check source"' in source


# ---------------------------------------------------------------------------
# T004B: OMI-specific workspace marker
# ---------------------------------------------------------------------------

class TestOmiWorkspaceMarker:
    def test_omi_workspace_class_conditionally_applied(self) -> None:
        source = app_source()
        assert 'data-active-workspace={activeWorkspaceView}' in source
        assert 'WORKSPACE_VIEWS.OMI_DASHBOARD' in source

    def test_omi_workspace_attribute_not_global(self) -> None:
        css = styles_css()
        assert '.editor-column[data-active-workspace="omi-dashboard"]' in css

    def test_editor_column_omi_workspace_reduces_padding(self) -> None:
        css = styles_css()
        block = _rule_body(css, '.editor-column[data-active-workspace="omi-dashboard"]')
        assert "padding" in block


# ---------------------------------------------------------------------------
# T004B: Status and metric wrapping
# ---------------------------------------------------------------------------

class TestStatusMetricWrapping:
    def test_omi_status_strip_uses_flex_wrap(self) -> None:
        css = styles_css()
        block = _rule_body(css, ".omi-status-strip")
        assert "display: flex" in block
        assert "flex-wrap: wrap" in block

    def test_omi_status_strip_div_has_flex_grow(self) -> None:
        css = styles_css()
        block = _rule_body(css, ".omi-status-strip div")
        assert "flex: 1 1 140px" in block

    def test_omi_grouped_metrics_uses_flex_wrap(self) -> None:
        css = styles_css()
        block = _rule_body(css, ".omi-grouped-metrics")
        assert "display: flex" in block
        assert "flex-wrap: wrap" in block

    def test_omi_candidate_status_grid_uses_flex_wrap(self) -> None:
        css = styles_css()
        block = _rule_body(css, ".omi-candidate-status-grid")
        assert "display: flex" in block
        assert "flex-wrap: wrap" in block

    def test_omi_approved_snapshot_dl_uses_flex_wrap(self) -> None:
        css = styles_css()
        block = _rule_body(css, ".omi-approved-snapshot dl")
        assert "display: flex" in block
        assert "flex-wrap: wrap" in block


# ---------------------------------------------------------------------------
# T004B: Container queries for OMI reflow
# ---------------------------------------------------------------------------

class TestOmiContainerQueries:
    def test_omi_shell_has_container_type_inline_size(self) -> None:
        css = styles_css()
        assert "container-type: inline-size" in css

    def test_candidate_detail_container_query_present(self) -> None:
        css = styles_css()
        assert "@container omi-shell" in css
        assert "omi-candidate-detail-layout" in css

    def test_grouped_review_container_query_present(self) -> None:
        css = styles_css()
        assert "@container omi-shell" in css
        assert "omi-grouped-review-layout" in css


# ---------------------------------------------------------------------------
# T004B: Local overflow containment on table wrappers only
# ---------------------------------------------------------------------------

class TestLocalTableOverflowContainment:
    def test_workflow_table_wrap_has_local_overflow(self) -> None:
        css = styles_css()
        block = _rule_body(css, ".omi-workflow-table-wrap")
        assert "overflow-x: auto" in block

    def test_field_table_wrap_has_local_overflow(self) -> None:
        css = styles_css()
        block = _rule_body(css, ".omi-field-table-wrap")
        assert "overflow-x: auto" in block

    def test_no_omi_shell_overflow_hidden(self) -> None:
        css = styles_css()
        block = _rule_body(css, ".omi-shell")
        assert "overflow-x: hidden" not in block

    def test_no_editor_column_overflow_hidden(self) -> None:
        css = styles_css()
        block = _rule_body(css, ".editor-column")
        assert "overflow-x: hidden" not in block


# ---------------------------------------------------------------------------
# T004B: Sticky field-action column
# ---------------------------------------------------------------------------

class TestStickyFieldActionColumn:
    def test_field_table_last_child_sticky(self) -> None:
        css = styles_css()
        assert ".omi-candidate-field-table th:last-child" in css
        assert ".omi-candidate-field-table td:last-child" in css
        assert "position: sticky" in css

    def test_sticky_surfaces_use_semantic_tokens(self) -> None:
        css = styles_css()
        base_block = (
            _rule_body(css, ".omi-candidate-field-table th:last-child")
            + _rule_body(css, ".omi-candidate-field-table td:last-child")
        )
        assert "#ffffff" not in base_block
        assert "var(--wa-color-surface)" in base_block
        header_block = _rule_body(css, ".omi-candidate-field-table thead th:last-child")
        assert "#fbfcff" not in header_block
        assert "var(--wa-color-surface-subtle)" in header_block


# ---------------------------------------------------------------------------
# Correction: .omi-disabled-action-row restored
# ---------------------------------------------------------------------------

class TestDisabledActionRowRestored:
    def test_disabled_action_row_has_flex_display(self) -> None:
        css = styles_css()
        block = _rule_body(css, ".omi-disabled-action-row")
        assert "display: flex" in block

    def test_disabled_action_row_has_flex_wrap(self) -> None:
        css = styles_css()
        block = _rule_body(css, ".omi-disabled-action-row")
        assert "flex-wrap: wrap" in block

    def test_disabled_action_row_has_gap(self) -> None:
        css = styles_css()
        block = _rule_body(css, ".omi-disabled-action-row")
        assert "gap: 8px" in block

    def test_sticky_disabled_at_mobile(self) -> None:
        css = styles_css()
        mobile_start = css.index("@media (max-width: 900px)")
        mobile_section = css[mobile_start:]
        assert "position: static" in mobile_section
        assert ".omi-candidate-field-table th:last-child" in mobile_section


# ---------------------------------------------------------------------------
# T004B: Scroll affordance text
# ---------------------------------------------------------------------------

class TestScrollAffordance:
    def test_dashboard_has_scroll_guidance(self) -> None:
        source = dashboard_source()
        assert "omi-dashboard-scroll-guidance" in source
        assert "Scroll horizontally within this table to review all columns." in source

    def test_dashboard_scroll_guidance_not_aria_hidden(self) -> None:
        source = dashboard_source()
        before_guidance = source.split("omi-dashboard-scroll-guidance")[0]
        after_testid = source.split("omi-dashboard-scroll-guidance")[1]
        end_line = after_testid.split("\n", 1)[0] if "\n" in after_testid else ""
        guidance_block = before_guidance[-200:] + 'omi-dashboard-scroll-guidance' + after_testid[:200]
        assert 'aria-hidden="true"' not in guidance_block

    def test_candidate_field_table_has_scroll_guidance(self) -> None:
        source = field_table_source()
        assert "omi-candidate-field-scroll-guidance" in source
        assert "Field actions remain visible." in source

    def test_candidate_scroll_guidance_not_aria_hidden(self) -> None:
        source = field_table_source()
        before_guidance = source.split("omi-candidate-field-scroll-guidance")[0]
        after_testid = source.split("omi-candidate-field-scroll-guidance")[1]
        guidance_block = before_guidance[-200:] + 'omi-candidate-field-scroll-guidance' + after_testid[:200]
        assert 'aria-hidden="true"' not in guidance_block

    def test_scroll_guidance_not_css_generated_only(self) -> None:
        dashboard = dashboard_source()
        assert "<p" in dashboard
        assert "omi-dashboard-scroll-guidance" in dashboard


# ---------------------------------------------------------------------------
# T004B: Preserved semantic table structure
# ---------------------------------------------------------------------------

class TestPreservedSemanticTable:
    def test_workflow_table_is_table_element(self) -> None:
        source = dashboard_source()
        assert "<table" in source
        assert "omi-workflow-table" in source

    def test_field_table_is_table_element(self) -> None:
        source = field_table_source()
        assert "<table" in source
        assert "omi-candidate-field-table" in source

    def test_workflow_table_retains_min_width(self) -> None:
        css = styles_css()
        block = _rule_body(css, ".omi-workflow-table")
        assert "min-width" in block

    def test_field_table_retains_min_width(self) -> None:
        css = styles_css()
        block = _rule_body(css, ".omi-candidate-field-table")
        assert "min-width" in block

    def test_mobile_field_table_to_card_preserved(self) -> None:
        css = styles_css()
        mobile_start = css.index("@media (max-width: 900px)")
        mobile_section = css[mobile_start:]
        assert "display: block" in mobile_section
        assert ".omi-candidate-field-table" in mobile_section

    def test_mobile_workflow_table_to_card_preserved(self) -> None:
        css = styles_css()
        mobile_start = css.index("@media (max-width: 900px)")
        mobile_section = css[mobile_start:]
        assert "display: none" in mobile_section
        assert ".omi-workflow-table thead" in mobile_section


# ---------------------------------------------------------------------------
# T004B: No hidden evidence, provenance, status, or owner-action fields
# ---------------------------------------------------------------------------

class TestNoHiddenSafetyFields:
    def test_mobile_field_table_cards_list_all_columns(self) -> None:
        css = styles_css()
        mobile_start = css.index("@media (max-width: 900px)")
        mobile_section = css[mobile_start:]
        assert "Proposed value" in mobile_section
        assert "Decision" in mobile_section
        assert "Evidence" in mobile_section
        assert "Provenance" in mobile_section
        assert "Duplicate/dependency" in mobile_section
        assert "Owner note" in mobile_section
        assert "Field action" in mobile_section

    def test_mobile_workflow_table_cards_list_all_columns(self) -> None:
        css = styles_css()
        mobile_start = css.index("@media (max-width: 900px)")
        mobile_section = css[mobile_start:]
        assert "Count" in mobile_section
        assert "Status" in mobile_section
        assert "Blockers" in mobile_section
        assert "Evidence / Provenance" in mobile_section
        assert "Action" in mobile_section
        assert "Disabled risky action / reason" in mobile_section

    def test_dashboard_has_disabled_apply_reason(self) -> None:
        source = dashboard_source()
        assert "omi-dashboard-disabled-apply-reason" in source

    def test_field_table_has_approval_disabled_reasons(self) -> None:
        source = field_table_source()
        assert "omi-field-approval-disabled-reason" in source


# ---------------------------------------------------------------------------
# T004B: Grouped Review reflow preservation
# ---------------------------------------------------------------------------

class TestGroupedReviewReflow:
    def test_grouped_review_layout_grid_retained_at_desktop(self) -> None:
        css = styles_css()
        block = _rule_body(css, ".omi-grouped-review-layout")
        assert "display: grid" in block

    def test_grouped_review_metrics_wrap(self) -> None:
        css = styles_css()
        block = _rule_body(css, ".omi-grouped-metrics")
        assert "flex-wrap: wrap" in block

    def test_grouped_detail_sticky_preserved_at_desktop(self) -> None:
        css = styles_css()
        assert ".omi-grouped-detail {\n  position: sticky" in css

    def test_mobile_grouped_review_reflow_preserved(self) -> None:
        css = styles_css()
        mobile_start = css.index("@media (max-width: 900px)")
        mobile_section = css[mobile_start:]
        assert ".omi-grouped-review-layout" in mobile_section
        assert "position: static" in mobile_section


# ---------------------------------------------------------------------------
# Design token consumption preserved (T004A)
# ---------------------------------------------------------------------------

class TestDesignTokenPreservation:
    REQUIRED_DESIGN_TOKENS = {
        "--wa-color-canvas",
        "--wa-color-surface",
        "--wa-color-surface-subtle",
        "--wa-color-surface-muted",
        "--wa-color-surface-selected",
        "--wa-color-text",
        "--wa-color-text-strong",
        "--wa-color-text-secondary",
        "--wa-color-text-muted",
        "--wa-color-border",
        "--wa-color-boundary-border",
        "--wa-color-accent",
        "--wa-color-focus",
        "--wa-color-success",
        "--wa-color-success-surface",
        "--wa-color-success-border",
        "--wa-color-warning",
        "--wa-color-warning-surface",
        "--wa-color-warning-border",
        "--wa-color-danger",
        "--wa-color-danger-surface",
        "--wa-color-danger-border",
        "--wa-radius-control",
        "--wa-radius-surface",
        "--wa-radius-pill",
    }

    def test_design_tokens_remain_consumed(self) -> None:
        css = styles_css()
        for token in self.REQUIRED_DESIGN_TOKENS:
            assert token in css, f"Design token {token!r} must remain in styles.css"

    def test_new_rules_consume_design_tokens_not_hardcoded_colors(self) -> None:
        css = styles_css()
        new_rules = "".join(
            _rule_body(css, selector) for selector in [
                ".project-selector",
                ".project-select-label",
                ".project-select",
                ".project-title-input",
            ]
        )
        assert "#" not in new_rules, \
            "New containment rules must use design tokens, not hardcoded colors"


# ---------------------------------------------------------------------------
# Universal box-sizing preserved (T004A)
# ---------------------------------------------------------------------------

class TestBoxSizingPreserved:
    def test_universal_box_sizing_border_box_preserved(self) -> None:
        css = styles_css()
        assert "box-sizing: border-box" in css


# ---------------------------------------------------------------------------
# Context textarea and field-input retain existing containment (T004A)
# ---------------------------------------------------------------------------

class TestExistingContainmentPreserved:
    def test_context_textarea_retains_width_and_resize(self) -> None:
        css = styles_css()
        block = _rule_body(css, ".context-textarea")
        assert "width: 100%" in block
        assert "resize: vertical" in block

    def test_field_input_retains_width_containment(self) -> None:
        css = styles_css()
        block = _rule_body(css, ".field-input")
        assert "width: 100%" in block
