"""Focused source guards for MVP project isolation browser evidence."""

from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "mvp-project-isolation-browser-smoke.mjs"
APP_JSX = REPO_ROOT / "frontend" / "src" / "App.jsx"
MEMORY_CANON_SHELL_JSX = (
    REPO_ROOT / "frontend" / "src" / "components" / "MemoryCanonShell.jsx"
)
PROJECT_NAV_JSX = REPO_ROOT / "frontend" / "src" / "components" / "ProjectNav.jsx"


def read_source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def function_body(source: str, function_name: str) -> str:
    match = re.search(rf"(async\s+)?function {function_name}\([^)]*\) \{{", source)
    assert match is not None, f"{function_name} should exist"
    start = match.end()
    depth = 1
    index = start

    while index < len(source) and depth:
        char = source[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
        index += 1

    assert depth == 0, f"{function_name} body should parse by braces"
    return source[start : index - 1]


def test_memory_canon_shell_is_stable_active_content_scope() -> None:
    source = read_source(MEMORY_CANON_SHELL_JSX)

    assert 'className={shellClassName}' in source
    assert "memory-canon-shell" in source
    assert 'aria-label="Memory / Canon"' in source
    assert "projectTitle" in source
    assert "approvedRecordsByCategory" in source
    assert "Candidate-only records are never displayed as approved" in source
    assert "No apply-promotion in this phase" in source


def test_app_renders_memory_canon_for_active_project_with_empty_approved_records() -> None:
    source = read_source(APP_JSX)
    memory_branch = source.split(
        "activeWorkspaceView === WORKSPACE_VIEWS.MEMORY_CANON ? (",
        1,
    )[1].split(") : (", 1)[0]

    assert "<MemoryCanonShell" in memory_branch
    assert "projectTitle={activeProject.title}" in memory_branch
    assert "approvedRecordsByCategory={{}}" in memory_branch
    assert "<OMIPanel" not in memory_branch
    assert "<OmiGuidedProjectCreation" not in memory_branch


def test_project_library_can_still_list_example_project() -> None:
    source = read_source(PROJECT_NAV_JSX)

    assert 'aria-label="Project library"' in source
    assert "<select" in source
    assert "projectOptions.map" in source
    assert "formatProjectOptionLabel(project)" in source


def test_evidence_script_scopes_omi_memory_leakage_checks_to_active_content() -> None:
    source = read_source(SCRIPT)
    helper_body = function_body(source, "getActiveOmiMemoryText")
    workflow_body = function_body(source, "runWorkflow")
    omi_assertion_block = workflow_body.split(
        "const omiMemoryText = await getActiveOmiMemoryText();",
        1,
    )[1].split(
        "softAssert(\n    'setup_candidate_not_labeled_approved_memory_or_canon'",
        1,
    )[0]

    assert "section.memory-canon-shell" in helper_body
    assert "getByRole('region', { name: /memory\\s*\\/\\s*canon/i })" in helper_body
    assert "main.editor-column[aria-label=\"Project workspace\"]" in helper_body
    assert "getVisibleText()" not in omi_assertion_block
    assert "locator('body')" not in omi_assertion_block
    assert "omi_memory_view_no_princess_and_pea" in omi_assertion_block
    assert "omi_memory_view_no_scene_001" in omi_assertion_block
    assert "containsExampleLeakage(omiMemoryText)" in omi_assertion_block


def test_evidence_script_does_not_hide_example_project_globally() -> None:
    source = read_source(SCRIPT)

    assert "The Princess and the Pea" in source
    assert "EXAMPLE_LEAKAGE_MARKERS" in source
    assert "Project library" not in function_body(source, "containsExampleLeakage")
    assert "The Princess and the Pea" not in read_source(APP_JSX)
    assert "The Princess and the Pea" not in read_source(MEMORY_CANON_SHELL_JSX)
