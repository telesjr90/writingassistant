"""Focused source contracts for the bounded T007C design foundation gate."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DESIGN_MD = REPO_ROOT / "DESIGN.md"
DESIGN_SIDECAR = REPO_ROOT / ".impeccable" / "design.json"
STYLES_CSS = REPO_ROOT / "frontend" / "src" / "styles.css"
PACKAGE_JSON = REPO_ROOT / "frontend" / "package.json"
OMI_LOADING_STATE = REPO_ROOT / "frontend" / "src" / "components" / "OMILoadingState.jsx"
OMI_DASHBOARD = REPO_ROOT / "frontend" / "src" / "components" / "OMIDashboard.jsx"
OMI_CANDIDATE_DETAIL = (
    REPO_ROOT / "frontend" / "src" / "components" / "OMICandidateDetail.jsx"
)
OMI_GROUPED_REVIEW = (
    REPO_ROOT / "frontend" / "src" / "components" / "OMIGroupedReview.jsx"
)

REQUIRED_HEADINGS = [
    "## 1. Overview",
    "## 2. Colors",
    "## 3. Typography",
    "## 4. Elevation",
    "## 5. Components",
    "## 6. Do's and Don'ts",
    "## 7. Minimum Operable-Target Policy",
]

REQUIRED_FRONTMATTER_GROUPS = {
    "name",
    "description",
    "colors",
    "typography",
    "rounded",
    "spacing",
    "components",
}

REQUIRED_CSS_TOKENS = {
    "--wa-color-canvas": "#f5f7fb",
    "--wa-color-surface": "#ffffff",
    "--wa-color-surface-subtle": "#fbfcff",
    "--wa-color-surface-muted": "#f7f9fc",
    "--wa-color-surface-selected": "#eef4ff",
    "--wa-color-text": "#172033",
    "--wa-color-text-strong": "#101828",
    "--wa-color-text-secondary": "#46546c",
    "--wa-color-text-muted": "#637089",
    "--wa-color-border": "#dfe5ef",
    "--wa-color-boundary-border": "#9fb3d4",
    "--wa-color-accent": "#234a84",
    "--wa-color-focus": "#7aa2e8",
    "--wa-color-success": "#3b6948",
    "--wa-color-success-surface": "#f3fbf5",
    "--wa-color-success-border": "#8ec79c",
    "--wa-color-warning": "#9a6500",
    "--wa-color-warning-surface": "#fff9eb",
    "--wa-color-warning-border": "#d7b46a",
    "--wa-color-danger": "#a93636",
    "--wa-color-danger-surface": "#fff7f7",
    "--wa-color-danger-border": "#e2a3a3",
    "--wa-radius-control": "6px",
    "--wa-radius-surface": "8px",
    "--wa-radius-pill": "999px",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def split_frontmatter(document: str) -> tuple[str, str]:
    assert document.startswith("---\n"), "DESIGN.md must start with YAML frontmatter"
    closing = document.find("\n---\n", 4)
    assert closing != -1, "DESIGN.md frontmatter must have a closing delimiter"
    return document[4:closing], document[closing + 5 :]


def css_rule(css: str, selector_pattern: str) -> str:
    matches = re.findall(
        rf"{selector_pattern}\s*\{{(?P<body>.*?)\}}",
        css,
        flags=re.DOTALL,
    )
    assert matches, f"missing CSS rule for {selector_pattern}"
    return "\n".join(matches)


def test_design_document_frontmatter_and_required_sections() -> None:
    assert DESIGN_MD.is_file()
    frontmatter, body = split_frontmatter(read_text(DESIGN_MD))

    top_level_groups = {
        match.group(1)
        for match in re.finditer(r"^([a-z][a-z0-9-]*):(?:\s|$)", frontmatter, re.MULTILINE)
    }
    assert REQUIRED_FRONTMATTER_GROUPS <= top_level_groups

    headings = re.findall(r"^## .+$", body, flags=re.MULTILINE)
    assert headings == REQUIRED_HEADINGS
    for heading in REQUIRED_HEADINGS:
        assert body.count(heading) == 1

    colors_block = re.search(
        r"^colors:\n(?P<body>.*?)(?=^typography:)",
        frontmatter,
        flags=re.MULTILINE | re.DOTALL,
    )
    assert colors_block
    color_values = re.findall(
        r'^  [a-z0-9-]+:\s+"(?P<value>#[0-9a-fA-F]{6})"$',
        colors_block.group("body"),
        flags=re.MULTILINE,
    )
    assert len(color_values) >= 22
    assert all(re.fullmatch(r"#[0-9a-fA-F]{6}", value) for value in color_values)


def test_design_document_preserves_product_and_execution_boundaries() -> None:
    document = read_text(DESIGN_MD).lower()

    required_policy_language = (
        "native html is the default",
        "radix is limited to complex interaction behavior",
        "application-owned visual language and product semantics",
        "analysis-only",
        "candidate-first",
        "evidence and provenance",
        "owner authority",
        "automatically promote",
        "automatically apply promotion",
        "automatically mutate approved memory or canon",
        "generated story-prose",
        "no wcag conformance claim",
        "t004 owns responsive",
        "t005 owns heading, target-size, focus, and keyboard completion",
    )
    for phrase in required_policy_language:
        assert phrase in document

    assert "meets wcag" not in document
    assert "wcag conformant" not in document
    assert "responsive work is complete" not in document

    anti_reference_fragments = (
        "generic ai chat or co-writer",
        "opaque automated system",
        "dense generic saas administration dashboard",
        "decorative or playful presentation",
        "unavailable, blocked, review-only, or not-yet-implemented behavior appear actionable",
    )
    dont_section = document.split("### don't", 1)[1]
    for fragment in anti_reference_fragments:
        assert fragment in dont_section


def test_impeccable_sidecar_is_schema_v2_extension_only() -> None:
    assert DESIGN_SIDECAR.is_file()
    payload = json.loads(read_text(DESIGN_SIDECAR))

    assert payload["schemaVersion"] == 2
    assert payload["generatedAt"].endswith("Z")
    assert payload["title"] == "Design System: Writing Assistant Application"
    assert "extensions" in payload
    assert "tokens" not in payload
    assert "colors" not in payload
    assert "typography" not in payload
    assert "rounded" not in payload
    assert "spacing" not in payload

    extensions = payload["extensions"]
    assert set(("colorMeta", "typographyMeta", "shadows", "focusRings", "breakpoints", "narrative")) <= set(extensions)
    assert extensions["breakpoints"] == [
        {
            "name": "current-compact-layout",
            "value": "900px",
            "purpose": "Actual current CSS breakpoint; T004 owns responsive completion.",
        }
    ]
    assert extensions["shadows"][0]["value"] == "0 18px 50px rgba(15, 23, 42, 0.08)"
    assert extensions["focusRings"][0]["value"] == "0 0 0 3px rgba(122, 162, 232, 0.2)"
    assert any(component["refersTo"] == "radix-evidence-dialog" for component in payload["components"])


def test_css_defines_semantic_tokens_and_shared_selectors_consume_them() -> None:
    css = read_text(STYLES_CSS)
    root_block = css_rule(css, r":root")

    for token, value in REQUIRED_CSS_TOKENS.items():
        assert re.search(
            rf"^\s*{re.escape(token)}:\s*{re.escape(value)};\s*$",
            root_block,
            flags=re.MULTILINE,
        ), f"missing exact token {token}: {value}"

    for token in (
        "--wa-space-4",
        "--wa-space-6",
        "--wa-space-8",
        "--wa-space-10",
        "--wa-space-12",
        "--wa-space-14",
        "--wa-space-16",
        "--wa-space-20",
        "--wa-space-24",
        "--wa-space-32",
        "--wa-shadow-panel",
        "--wa-font-ui",
        "--wa-font-monospace",
        "--wa-focus-ring",
    ):
        assert token in root_block

    selector_expectations = {
        r"body": ("var(--wa-color-text)", "var(--wa-color-canvas)", "var(--wa-font-ui)"),
        r"\.primary-button": ("var(--wa-color-accent)", "var(--wa-color-surface)"),
        r"\.secondary-button": ("var(--wa-color-accent)", "var(--wa-radius-control)"),
        r"\.context-status": ("var(--wa-color-success)",),
        r"\.save-status": ("var(--wa-color-success)",),
        r"\.error-copy": ("var(--wa-color-danger)",),
        r"\.review-boundary-note": ("var(--wa-color-boundary-border)", "var(--wa-color-surface-subtle)"),
        r"\.omi-loading-state": ("var(--wa-color-surface-muted)", "var(--wa-color-border)"),
        r"\.omi-status-badge": ("var(--wa-color-accent)", "var(--wa-radius-pill)"),
    }
    for selector, expected_values in selector_expectations.items():
        block = css_rule(css, selector)
        for expected_value in expected_values:
            assert expected_value in block, f"{selector} does not consume {expected_value}"

    boundary_block = css_rule(
        css,
        r"\.omi-boundary-banner,\s*\.omi-error-state,\s*\.omi-health-panel",
    )
    assert "var(--wa-color-boundary-border)" in boundary_block
    assert "var(--wa-radius-surface)" in boundary_block

    empty_block = css_rule(
        css,
        r"\.omi-empty-state,\s*\.omi-candidate-panel,\s*\.omi-candidate-actions",
    )
    assert "var(--wa-color-surface-subtle)" in empty_block
    assert "var(--wa-color-border)" in empty_block


def test_omi_loading_state_is_a_children_only_presentational_leaf() -> None:
    loading_source = read_text(OMI_LOADING_STATE)
    expected_source = """export default function OMILoadingState({ children }) {
  return (
    <p className=\"omi-loading-state\" role=\"status\">
      {children}
    </p>
  );
}
"""
    assert loading_source == expected_source

    lower_loading_source = loading_source.lower()
    assert "import " not in loading_source
    for forbidden in (
        "usestate",
        "useeffect",
        "usecallback",
        "usememo",
        "useref",
        "fetch(",
        "axios",
        "@radix-ui",
        "promotion",
        "memory",
        "canon",
    ):
        assert forbidden not in lower_loading_source
    for loading_copy in (
        "Loading OMI status.",
        "Loading candidate.",
        "Loading grouped owner review.",
    ):
        assert loading_copy not in loading_source

    callers = (
        (OMI_DASHBOARD, "Loading OMI status.", "{isLoading && ("),
        (OMI_CANDIDATE_DETAIL, "Loading candidate.", "if (isLoading) {"),
        (OMI_GROUPED_REVIEW, "Loading grouped owner review.", "if (isLoading) {"),
    )
    for path, loading_copy, loading_marker in callers:
        caller_source = read_text(path)
        assert "import OMILoadingState from './OMILoadingState.jsx';" in caller_source
        assert "<OMILoadingState>" in caller_source
        assert "</OMILoadingState>" in caller_source
        assert loading_copy in caller_source
        assert '<p className="omi-loading-state" role="status">' not in caller_source
        assert loading_marker in caller_source


def test_dependency_and_scope_boundaries_remain_unchanged() -> None:
    package = json.loads(read_text(PACKAGE_JSON))
    dependencies = package.get("dependencies", {})
    radix_dependencies = sorted(name for name in dependencies if name.startswith("@radix-ui/"))

    assert radix_dependencies == ["@radix-ui/react-dialog"]
    for forbidden in (
        "tailwindcss",
        "shadcn-ui",
        "react-aria",
        "react-aria-components",
        "@radix-ui/themes",
        "radix-ui",
    ):
        assert forbidden not in dependencies
        assert forbidden not in package.get("devDependencies", {})

    changed_prohibited = subprocess.check_output(
        [
            "git",
            "diff",
            "--name-only",
            "HEAD",
            "--",
            "docs/roadmap",
            "frontend/package.json",
            "frontend/package-lock.json",
        ],
        cwd=REPO_ROOT,
        text=True,
    ).splitlines()
    assert changed_prohibited == []
