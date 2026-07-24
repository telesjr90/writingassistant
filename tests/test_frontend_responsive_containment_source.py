"""Focused source contracts for PHASE8-IMPL-024-T004A responsive containment."""

from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
STYLES_CSS = REPO_ROOT / "frontend" / "src" / "styles.css"
PROJECT_NAV_JSX = REPO_ROOT / "frontend" / "src" / "components" / "ProjectNav.jsx"
OMI_GUIDED_CREATION_JSX = (
    REPO_ROOT / "frontend" / "src" / "components" / "OmiGuidedProjectCreation.jsx"
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def styles_css() -> str:
    return read_text(STYLES_CSS)


def project_nav_source() -> str:
    return read_text(PROJECT_NAV_JSX)


def omi_guided_creation_source() -> str:
    return read_text(OMI_GUIDED_CREATION_JSX)


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
# Root containment chain
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
# Form and label containment
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
# Desktop navigation and sidebar widths preserved
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
# Story Check selector presence
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
# OMI table/grid/workspace rules not changed
# ---------------------------------------------------------------------------

class TestOmiRulesUnchanged:
    def test_new_rules_do_not_reference_omi_table_metric_or_workspace_selectors(self) -> None:
        css = styles_css()
        new_containment_selectors = [
            ".project-selector",
            ".project-select-label",
            ".project-select",
            ".project-title-input",
        ]
        for selector in new_containment_selectors:
            block = _rule_body(css, selector)
            assert ".omi-status-strip" not in block
            assert ".omi-grouped-metrics" not in block
            assert ".omi-workflow-table" not in block
            assert ".omi-candidate-field-table" not in block
            assert ".omi-grouped-review-layout" not in block

    def test_omi_status_strip_unchanged(self) -> None:
        css = styles_css()
        block = _rule_body(css, ".omi-status-strip")
        assert "grid-template-columns: repeat(7, minmax(110px, 1fr))" in block

    def test_omi_workflow_table_unchanged(self) -> None:
        css = styles_css()
        block = _rule_body(css, ".omi-workflow-table")
        assert "width: 100%" in block
        assert "min-width: 980px" in block

    def test_omi_grouped_metrics_unchanged(self) -> None:
        css = styles_css()
        block = _rule_body(css, ".omi-grouped-metrics")
        assert "grid-template-columns: repeat(6, minmax(100px, 1fr))" in block

    def test_omi_candidate_field_table_unchanged(self) -> None:
        css = styles_css()
        block = _rule_body(css, ".omi-candidate-field-table")
        assert "min-width: 1120px" in block

    def test_omi_grouped_review_layout_unchanged(self) -> None:
        css = styles_css()
        block = _rule_body(css, ".omi-grouped-review-layout")
        assert "grid-template-columns: minmax(320px, 0.85fr) minmax(420px, 1.15fr)" in block


# ---------------------------------------------------------------------------
# Design token consumption preserved
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
# Universal box-sizing preserved
# ---------------------------------------------------------------------------

class TestBoxSizingPreserved:
    def test_universal_box_sizing_border_box_preserved(self) -> None:
        css = styles_css()
        assert "box-sizing: border-box" in css


# ---------------------------------------------------------------------------
# Context textarea and field-input retain existing containment
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
