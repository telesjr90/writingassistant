"""Source-level regression tests for PHASE7-IMPL-003 frontend project workspace."""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_SRC = REPO_ROOT / "frontend" / "src"

API_JS = FRONTEND_SRC / "api.js"
APP_JSX = FRONTEND_SRC / "App.jsx"
PROJECT_NAV_JSX = FRONTEND_SRC / "components" / "ProjectNav.jsx"


def read_source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def api_source() -> str:
    return read_source(API_JS)


@pytest.fixture(scope="module")
def app_source() -> str:
    return read_source(APP_JSX)


@pytest.fixture(scope="module")
def project_nav_source() -> str:
    return read_source(PROJECT_NAV_JSX)


class TestApiProjectHelpers:
    def test_project_id_remains_example(self, api_source: str) -> None:
        assert re.search(r"""export const PROJECT_ID = ['"]example['"]""", api_source)

    def test_list_projects_exported_and_calls_get(self, api_source: str) -> None:
        assert re.search(r"export async function listProjects\s*\(", api_source)
        assert "client.get('/projects')" in api_source or 'client.get("/projects")' in api_source

    def test_create_project_exported_and_calls_post(self, api_source: str) -> None:
        assert re.search(r"export async function createProject\s*\(", api_source)
        assert (
            "client.post('/projects', { title })" in api_source
            or 'client.post("/projects", { title })' in api_source
        )

    def test_create_project_sends_only_title_not_project_id(self, api_source: str) -> None:
        match = re.search(
            r"export async function createProject\(title\)\s*\{[^}]*\}",
            api_source,
            re.DOTALL,
        )
        assert match is not None
        body = match.group(0)
        assert "project_id" not in body

    @pytest.mark.parametrize(
        "function_name",
        [
            "fetchScenes",
            "fetchScene",
            "saveScene",
            "fetchBible",
            "saveBible",
            "fetchStoryform",
            "saveStoryform",
            "runStoryCheck",
            "fetchStoryformContext",
            "getOMI",
        ],
    )
    def test_existing_helpers_preserve_project_id_default(
        self, api_source: str, function_name: str
    ) -> None:
        pattern = rf"export async function {function_name}\([^)]*projectId = PROJECT_ID"
        assert re.search(pattern, api_source), (
            f"{function_name} should accept optional projectId defaulting to PROJECT_ID"
        )


class TestAppActiveProjectState:
    def test_imports_project_workspace_api_helpers(self, app_source: str) -> None:
        assert "PROJECT_ID" in app_source
        assert "listProjects" in app_source
        assert "createProject" in app_source
        assert re.search(r"from ['\"]\.\/api\.js['\"]", app_source)

    def test_initializes_active_project_id_from_project_id(self, app_source: str) -> None:
        assert re.search(
            r"useState\(PROJECT_ID\)",
            app_source,
        ) or "useState(PROJECT_ID)" in app_source
        assert "activeProjectId" in app_source
        assert re.search(r"const \[activeProjectId,\s*setActiveProjectId\]", app_source)

    def test_includes_project_library_state(self, app_source: str) -> None:
        for token in ("projects", "projectsLoading", "projectsError"):
            assert token in app_source

    def test_load_projects_uses_list_projects(self, app_source: str) -> None:
        assert re.search(r"(const|function)\s+loadProjects\b", app_source)
        assert "listProjects()" in app_source

    def test_handle_select_project_with_unsaved_confirmation(self, app_source: str) -> None:
        assert re.search(r"handleSelectProject\b", app_source)
        assert "UNSAVED_PROJECT_SWITCH_MESSAGE" in app_source
        assert "window.confirm" in app_source
        assert "setActiveProjectId" in app_source

    def test_handle_create_project_trims_and_rejects_blank_title(self, app_source: str) -> None:
        assert re.search(r"handleCreateProject\b", app_source)
        assert ".trim()" in app_source
        assert re.search(r"if\s*\(\s*!trimmedTitle\s*\)", app_source)

    def test_handle_create_project_calls_api_without_project_id(self, app_source: str) -> None:
        match = re.search(
            r"handleCreateProject\s*=\s*useCallback\(async\s*\([^)]*\)\s*=>\s*\{.*?\n\s*\},\s*\[",
            app_source,
            re.DOTALL,
        )
        assert match is not None
        body = match.group(0)
        assert "createProject(trimmedTitle)" in body or "createProject( trimmedTitle )" in body
        assert "project_id" not in body.split("createProject(trimmedTitle)")[0][-200:]

    def test_handle_create_project_refreshes_library_and_selects_created_project(
        self, app_source: str
    ) -> None:
        match = re.search(
            r"handleCreateProject\s*=\s*useCallback\(async\s*\([^)]*\)\s*=>\s*\{.*?\n\s*\},\s*\[",
            app_source,
            re.DOTALL,
        )
        assert match is not None
        body = match.group(0)
        assert "await loadProjects()" in body
        assert "metadata?.project_id" in body or "metadata.project_id" in body
        assert "setActiveProjectId(newProjectId)" in body

    @pytest.mark.parametrize(
        "api_call_pattern",
        [
            r"fetchScenes\(activeProjectId\)",
            r"fetchBible\(activeProjectId\)",
            r"fetchStoryform\(activeProjectId\)",
            r"fetchStoryformContext\(activeProjectId\)",
            r"getOMI\(activeProjectId\)",
            r"fetchScene\([^,]+,\s*activeProjectId\)",
            r"saveScene\([^,]+,\s*[^,]+,\s*activeProjectId\)",
            r"saveBible\([^,]+,\s*activeProjectId\)",
            r"saveStoryform\([^,]+,\s*activeProjectId\)",
            r"runStoryCheck\([^,]+,\s*activeProjectId\)",
        ],
    )
    def test_project_scoped_api_calls_use_active_project_id(
        self, app_source: str, api_call_pattern: str
    ) -> None:
        assert re.search(api_call_pattern, app_source), (
            f"Expected activeProjectId usage matching /{api_call_pattern}/"
        )

    def test_unsaved_confirmation_before_project_create(self, app_source: str) -> None:
        assert "UNSAVED_PROJECT_CREATE_MESSAGE" in app_source


class TestProjectNavSelectorUi:
    def test_includes_library_section(self, project_nav_source: str) -> None:
        assert "Library" in project_nav_source
        assert 'aria-label="Project library"' in project_nav_source

    def test_includes_project_selector_with_loading_and_error_states(
        self, project_nav_source: str
    ) -> None:
        assert "<select" in project_nav_source
        assert "projectsLoading" in project_nav_source
        assert "Loading projects" in project_nav_source
        assert "projectsError" in project_nav_source

    def test_disables_invalid_and_warning_projects(self, project_nav_source: str) -> None:
        assert "selectable" in project_nav_source
        assert "disabled={!project.selectable}" in project_nav_source
        assert "Invalid or warning projects are listed but cannot be opened" in project_nav_source

    def test_has_refresh_projects_action(self, project_nav_source: str) -> None:
        assert "onRefreshProjects" in project_nav_source
        assert "Refresh projects" in project_nav_source

    def test_does_not_display_filesystem_paths(self, project_nav_source: str) -> None:
        lower_source = project_nav_source.lower()
        forbidden_path_tokens = [
            "projects/",
            "relative_path",
            "/home/",
            "c:\\",
            ".md",
            "filesystem",
        ]
        for token in forbidden_path_tokens:
            assert token not in lower_source

    def test_includes_create_blank_project_form(self, project_nav_source: str) -> None:
        assert 'aria-label="Create blank project"' in project_nav_source
        assert "Project title" in project_nav_source
        assert "project-title-input" in project_nav_source
        assert "Create blank project" in project_nav_source

    @pytest.mark.parametrize(
        "unsafe_phrase",
        [
            "generate story",
            "write story",
            "continue story",
            "rewrite",
            "improve prose",
            "generate project idea",
        ],
    )
    def test_project_nav_excludes_unsafe_prose_generation_copy(
        self, project_nav_source: str, unsafe_phrase: str
    ) -> None:
        assert unsafe_phrase not in project_nav_source.lower()


class TestProjectWorkspaceSafetyBoundaries:
    WORKSPACE_SOURCES = (API_JS, APP_JSX, PROJECT_NAV_JSX)

    @pytest.mark.parametrize("source_path", WORKSPACE_SOURCES)
    def test_no_prose_generation_ui_copy(self, source_path: Path) -> None:
        lower_source = read_source(source_path).lower()
        forbidden_phrases = [
            "generate story",
            "write story",
            "continue story",
            "rewrite scene",
            "improve prose",
            "generate project idea",
            "polish prose",
        ]
        for phrase in forbidden_phrases:
            assert phrase not in lower_source

    @pytest.mark.parametrize("source_path", [PROJECT_NAV_JSX, APP_JSX])
    def test_project_ui_excludes_forbidden_workspace_terms(self, source_path: Path) -> None:
        lower_source = read_source(source_path).lower()
        forbidden_terms = [
            "apply-promotion",
            "apply promotion",
            "canon promotion",
            "extraction",
            "dramatica",
            "ollama",
            "model generation",
        ]
        for term in forbidden_terms:
            assert term not in lower_source

    def test_create_project_copy_is_safe(self, project_nav_source: str) -> None:
        assert "create blank project" in project_nav_source.lower()


class TestNoBackendOrNetworkMutation:
    @staticmethod
    def _module_ast() -> ast.Module:
        return ast.parse(read_source(Path(__file__)))

    def test_does_not_import_backend_modules(self) -> None:
        for node in ast.walk(self._module_ast()):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert not alias.name.startswith("backend")
            elif isinstance(node, ast.ImportFrom) and node.module:
                assert not node.module.startswith("backend")

    def test_does_not_create_project_fixtures(self) -> None:
        for node in ast.walk(self._module_ast()):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if isinstance(func, ast.Attribute) and func.attr in {"write_text", "mkdir"}:
                pytest.fail("Source tests must not write project fixtures on disk")

    def test_does_not_call_network_apis(self) -> None:
        forbidden_roots = {"requests", "httpx", "axios"}
        for node in ast.walk(self._module_ast()):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".")[0]
                    assert root not in forbidden_roots
            elif isinstance(node, ast.ImportFrom) and node.module:
                root = node.module.split(".")[0]
                assert root not in forbidden_roots
                assert node.module != "fastapi.testclient"
