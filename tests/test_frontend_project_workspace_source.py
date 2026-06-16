"""Source-level regression tests for PHASE7-IMPL-003 frontend project workspace."""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_SRC = REPO_ROOT / "frontend" / "src"
BACKEND_SRC = REPO_ROOT / "backend"
ROADMAP_ROOT = REPO_ROOT / "docs" / "roadmap"

API_JS = FRONTEND_SRC / "api.js"
APP_JSX = FRONTEND_SRC / "App.jsx"
SHARED_DOCUMENT_CONTROLLER_JS = FRONTEND_SRC / "sharedDocumentController.js"
PROJECT_NAV_JSX = FRONTEND_SRC / "components" / "ProjectNav.jsx"
PROJECT_OVERVIEW_JSX = FRONTEND_SRC / "components" / "ProjectOverview.jsx"
OMI_PANEL_JSX = FRONTEND_SRC / "components" / "OMIPanel.jsx"
EDITOR_JSX = FRONTEND_SRC / "components" / "Editor.jsx"
PROJECT_CONTEXT_JSX = FRONTEND_SRC / "components" / "ProjectContext.jsx"
BACKEND_MAIN_PY = BACKEND_SRC / "main.py"
PROJECT_MANAGER_PY = BACKEND_SRC / "project_manager.py"
TASK_007_MD = ROADMAP_ROOT / "tasks" / "PHASE7-IMPL-007.md"
INVENTORY_007_MD = ROADMAP_ROOT / "inventory" / "PHASE7-IMPL-007.md"
ENRICHMENT_007_JSON = ROADMAP_ROOT / "enrichment" / "PHASE7-IMPL-007.enrichment.json"
PROJECT_OVERVIEW_SPEC_MD = ROADMAP_ROOT / "project_overview_page_spec.md"
TASK_008_MD = ROADMAP_ROOT / "tasks" / "PHASE7-IMPL-008.md"
INVENTORY_008_MD = ROADMAP_ROOT / "inventory" / "PHASE7-IMPL-008.md"
ENRICHMENT_008_JSON = ROADMAP_ROOT / "enrichment" / "PHASE7-IMPL-008.enrichment.json"
PROJECT_CREATION_SPEC_MD = ROADMAP_ROOT / "project_creation_flow_spec.md"
OMI_GUIDED_CREATION_SPEC_MD = ROADMAP_ROOT / "omi_guided_project_creation_spec.md"
OMI_SCHEMA_LIFECYCLE_MD = ROADMAP_ROOT / "omi_mvp_schema_lifecycle.md"
OMI_STORAGE_MODEL_MD = ROADMAP_ROOT / "omi_storage_model.md"
OMI_IDEAS_CANDIDATES_SPEC_MD = ROADMAP_ROOT / "omi_ideas_candidates_page_spec.md"


def read_source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def api_source() -> str:
    return read_source(API_JS)


@pytest.fixture(scope="module")
def app_source() -> str:
    return read_source(APP_JSX)


@pytest.fixture(scope="module")
def shared_document_controller_source() -> str:
    return read_source(SHARED_DOCUMENT_CONTROLLER_JS)


@pytest.fixture(scope="module")
def project_nav_source() -> str:
    return read_source(PROJECT_NAV_JSX)


@pytest.fixture(scope="module")
def project_overview_source() -> str:
    return read_source(PROJECT_OVERVIEW_JSX)


@pytest.fixture(scope="module")
def omi_panel_source() -> str:
    return read_source(OMI_PANEL_JSX)


@pytest.fixture(scope="module")
def editor_source() -> str:
    return read_source(EDITOR_JSX)


@pytest.fixture(scope="module")
def project_context_source() -> str:
    return read_source(PROJECT_CONTEXT_JSX)


@pytest.fixture(scope="module")
def backend_main_source() -> str:
    return read_source(BACKEND_MAIN_PY)


@pytest.fixture(scope="module")
def project_manager_source() -> str:
    return read_source(PROJECT_MANAGER_PY)


@pytest.fixture(scope="module")
def task_007_source() -> str:
    return read_source(TASK_007_MD)


@pytest.fixture(scope="module")
def inventory_007_source() -> str:
    return read_source(INVENTORY_007_MD)


@pytest.fixture(scope="module")
def enrichment_007_source() -> str:
    return read_source(ENRICHMENT_007_JSON)


@pytest.fixture(scope="module")
def project_overview_spec_source() -> str:
    return read_source(PROJECT_OVERVIEW_SPEC_MD)


@pytest.fixture(scope="module")
def task_008_source() -> str:
    return read_source(TASK_008_MD)


@pytest.fixture(scope="module")
def inventory_008_source() -> str:
    return read_source(INVENTORY_008_MD)


@pytest.fixture(scope="module")
def enrichment_008_source() -> str:
    return read_source(ENRICHMENT_008_JSON)


@pytest.fixture(scope="module")
def project_creation_spec_source() -> str:
    return read_source(PROJECT_CREATION_SPEC_MD)


@pytest.fixture(scope="module")
def omi_guided_creation_spec_source() -> str:
    return read_source(OMI_GUIDED_CREATION_SPEC_MD)


@pytest.fixture(scope="module")
def omi_schema_lifecycle_source() -> str:
    return read_source(OMI_SCHEMA_LIFECYCLE_MD)


@pytest.fixture(scope="module")
def omi_storage_model_source() -> str:
    return read_source(OMI_STORAGE_MODEL_MD)


@pytest.fixture(scope="module")
def omi_ideas_candidates_spec_source() -> str:
    return read_source(OMI_IDEAS_CANDIDATES_SPEC_MD)


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


class TestProjectOverviewDataContract:
    """PHASE7-IMPL-007-T002 source contract before overview runtime work."""

    def test_allowed_overview_data_is_deterministic_and_local(
        self,
        task_007_source: str,
        inventory_007_source: str,
        enrichment_007_source: str,
    ) -> None:
        allowed_contract_terms = (
            "project title/ID/status",
            "warnings",
            "timestamps",
            "cheap counts",
            "scene/note/material counts",
            "safe empty states",
            "deterministic project-local metadata/status/counts/empty states",
        )
        combined_contract = "\n".join(
            [task_007_source, inventory_007_source, enrichment_007_source]
        )
        for term in allowed_contract_terms:
            assert term in combined_contract, (
                f"PHASE7-IMPL-007 contract should allow deterministic overview data: {term}"
            )

        forbidden_contract_outputs = (
            "AI-generated project summaries",
            "note summaries",
            "material summaries",
            "Story Check auto-runs",
            "model/Ollama calls",
            "OMI/canon/memory mutation",
            "training/JSONL/dataset",
        )
        for term in forbidden_contract_outputs:
            assert term in combined_contract, (
                f"PHASE7-IMPL-007 contract should explicitly exclude {term}"
            )

    def test_project_identity_inputs_exist_without_dedicated_overview_route(
        self,
        app_source: str,
        api_source: str,
        backend_main_source: str,
        project_manager_source: str,
        inventory_007_source: str,
    ) -> None:
        for frontend_token in (
            "const [activeProjectId, setActiveProjectId] = useState(PROJECT_ID)",
            "const [projects, setProjects] = useState([])",
            "listProjects()",
            "setActiveProjectId(newProjectId)",
        ):
            assert frontend_token in app_source

        assert "export async function listProjects()" in api_source
        assert "export async function createProject(title)" in api_source
        assert '@app.get("/api/projects")' in backend_main_source
        assert "def get_projects()" in backend_main_source
        assert "def list_projects(" in project_manager_source
        assert "def load_project_metadata(" in project_manager_source

        for metadata_field in (
            '"project_id"',
            '"title"',
            '"created_at"',
            '"updated_at"',
            '"creation_method"',
            '"status"',
            '"warnings"',
        ):
            assert metadata_field in project_manager_source

        assert "There is no dedicated project overview route today." in inventory_007_source

    def test_overview_counts_must_use_existing_lists_not_analysis(
        self,
        app_source: str,
        backend_main_source: str,
        project_manager_source: str,
        task_007_source: str,
        inventory_007_source: str,
    ) -> None:
        for list_call in (
            "fetchScenes(activeProjectId)",
            "fetchNotes(activeProjectId)",
            "fetchMaterials(activeProjectId)",
        ):
            assert list_call in app_source

        for route_name in ("def get_scenes(", "def get_notes(", "def get_materials("):
            assert route_name in backend_main_source

        for helper_name in (
            "def list_scenes(",
            "def list_note_metadata(",
            "def list_material_metadata(",
        ):
            assert helper_name in project_manager_source

        assert "Chapter count if chapter metadata helpers provide a cheap count; otherwise defer." in (
            inventory_007_source
        )
        assert "scene/note/material counts" in task_007_source

        initial_load_block = app_source.split("async function loadInitialData()", 1)[1].split(
            "const refreshOMI",
            1,
        )[0]
        assert "runStoryCheck" not in initial_load_block
        assert "analysis_engine" not in initial_load_block
        assert "extract" not in initial_load_block.lower()

    def test_safe_overview_sections_are_shell_status_sections(
        self, inventory_007_source: str, project_overview_spec_source: str
    ) -> None:
        for section_label in (
            "Project Header",
            "Workspace Navigation Cards",
            "Scenes",
            "Notes",
            "Materials",
            "OMI",
            "Approved Memory / Canon",
        ):
            assert section_label in project_overview_spec_source or section_label in inventory_007_source

        assert "Approved memory/canon snapshot as an empty-state shell only" in (
            inventory_007_source
        )
        assert "OMI and memory/canon sections should remain status/empty-state shells" in (
            inventory_007_source
        )
        assert "must not promote candidates or create memory files" in inventory_007_source

    def test_empty_state_contract_is_factual_not_story_guidance(
        self, inventory_007_source: str, project_nav_source: str
    ) -> None:
        for existing_empty_state in ("No scenes yet.", "No notes yet.", "No materials yet."):
            assert existing_empty_state in project_nav_source

        for planned_empty_state in (
            "missing optional metadata",
            "no scenes",
            "no notes",
            "no materials",
            "no approved memory/canon yet",
        ):
            assert planned_empty_state in inventory_007_source

        assert "generated next step" in inventory_007_source
        lower_runtime_nav = project_nav_source.lower()
        for forbidden_empty_state_behavior in (
            "story suggestions",
            "generated next step",
            "ai story summary",
            "extracted character",
            "extracted location",
            "extracted timeline",
        ):
            assert forbidden_empty_state_behavior not in lower_runtime_nav

    def test_navigation_contract_uses_existing_workspace_surfaces_without_mutation(
        self,
        app_source: str,
        project_nav_source: str,
        inventory_007_source: str,
    ) -> None:
        for nav_callback in (
            "onSelectScene(sceneId)",
            "onSelectNote?.(noteId)",
            "onSelectMaterial?.(materialId)",
        ):
            assert nav_callback in project_nav_source

        for existing_surface in ("ProjectNav", "ProjectContext", "OMIPanel", "Editor"):
            assert existing_surface in app_source

        assert "Workspace navigation cards or buttons" in inventory_007_source
        assert "does not trigger body reads, model calls, or project writes" in (
            inventory_007_source
        )

        project_nav_source_lower = project_nav_source.lower()
        for forbidden_nav_behavior in (
            "metadata editor",
            "edit metadata",
            "upload material",
            "import material",
            "apply promotion",
        ):
            assert forbidden_nav_behavior not in project_nav_source_lower

    def test_app_and_project_nav_have_safe_overview_integration_surfaces(
        self, app_source: str, project_nav_source: str, inventory_007_source: str
    ) -> None:
        assert "activeProjectId" in app_source
        assert "activeDocumentType" in app_source
        assert "activeDocumentId={activeDocument.id}" in app_source
        assert "hasUnsavedDocumentChanges" in app_source
        assert "activeProjectLabel" in project_nav_source

        assert "There is no dedicated Project Overview component or landing surface today." in (
            inventory_007_source
        )
        assert "There is no Overview nav item today." in inventory_007_source
        assert "must not break the shared editor's document selection" in inventory_007_source

    def test_backend_overview_helper_is_optional_and_must_be_deterministic(
        self,
        backend_main_source: str,
        project_manager_source: str,
        task_007_source: str,
        inventory_007_source: str,
    ) -> None:
        assert "/overview" not in backend_main_source
        assert "overview" not in project_manager_source.lower()
        assert "There is no dedicated overview API helper today." in inventory_007_source
        assert "deterministic project overview data helpers only if existing project/list/metadata helpers are insufficient" in (
            task_007_source
        )

        for backend_source in (backend_main_source, project_manager_source):
            assert "analysis_engine.run_story_check" not in backend_source.split("def get_projects", 1)[0]
            assert "summarize" not in backend_source.lower()
            assert "semantic search" not in backend_source.lower()

    def test_existing_data_sources_are_sufficient_for_first_overview_shell(
        self, app_source: str, api_source: str
    ) -> None:
        for state_token in (
            "const [projects, setProjects] = useState([])",
            "const [activeProjectId, setActiveProjectId] = useState(PROJECT_ID)",
            "const [scenes, setScenes] = useState([])",
            "const [notes, setNotes] = useState([])",
            "const [materials, setMaterials] = useState([])",
            "const [omiData, setOmiData] = useState({ index: null, ideas: [], candidates: [] })",
        ):
            assert state_token in app_source

        for load_call in (
            "listProjects()",
            "fetchScenes(activeProjectId)",
            "fetchNotes(activeProjectId)",
            "fetchMaterials(activeProjectId)",
            "getOMI(activeProjectId)",
        ):
            assert load_call in app_source

        for api_helper in (
            "export async function listProjects()",
            "export async function fetchScenes(",
            "export async function fetchNotes(",
            "export async function fetchMaterials(",
            "export async function getOMI(",
        ):
            assert api_helper in api_source

        assert "/overview" not in api_source

    def test_overview_counts_can_be_derived_from_loaded_lists_without_body_reads(
        self, app_source: str
    ) -> None:
        initial_load_block = app_source.split("async function loadInitialData()", 1)[1].split(
            "const refreshOMI",
            1,
        )[0]

        for list_setter in (
            "setScenes(Array.isArray(scenePayload) ? scenePayload : scenePayload.scenes ?? [])",
            "setNotes(notesPayload?.notes ?? [])",
            "setMaterials(materialsPayload?.materials ?? [])",
        ):
            assert list_setter in initial_load_block

        for body_fetch in ("fetchScene(", "fetchNote(", "fetchMaterial("):
            assert body_fetch not in initial_load_block

        for unsafe_count_source in (
            "runStoryCheck",
            "extract",
            "summar",
            "analysis",
            "model",
        ):
            assert unsafe_count_source not in initial_load_block.lower()

    def test_chapter_count_is_deferred_without_blocking_overview_shell(
        self,
        app_source: str,
        api_source: str,
        inventory_007_source: str,
    ) -> None:
        assert "Chapter count if chapter metadata helpers provide a cheap count; otherwise defer." in (
            inventory_007_source
        )
        assert "Chapter count may need helper support or may be deferred if no cheap path exists." in (
            inventory_007_source
        )
        assert "fetchChapters" not in app_source
        assert "fetchChapters" not in api_source
        assert "chapter count" not in api_source.lower()

    def test_t004_does_not_require_dedicated_backend_overview_route(
        self,
        api_source: str,
        backend_main_source: str,
        project_manager_source: str,
        task_007_source: str,
        inventory_007_source: str,
    ) -> None:
        for source in (api_source, backend_main_source, project_manager_source):
            assert "/overview" not in source
            assert "get_project_overview" not in source
            assert "load_project_overview" not in source

        assert "Frontend overview shell component" in task_007_source
        assert "Add a minimal overview component using deterministic data." in (
            task_007_source
        )
        assert "There is no dedicated project overview route today." in inventory_007_source
        assert "There is no dedicated overview API helper today." in inventory_007_source

    def test_optional_future_backend_helper_must_remain_read_only_and_local(
        self, task_007_source: str, inventory_007_source: str
    ) -> None:
        combined_contract = "\n".join([task_007_source, inventory_007_source])
        for required_boundary in (
            "project-local",
            "full body reads",
            "extraction",
            "model calls",
            "OMI/canon/memory mutation",
            "no Story Check auto-runs",
        ):
            assert required_boundary in combined_contract

        for deferred_or_optional in (
            "Backend/project data helper compatibility, if needed",
            "if existing project/list/metadata helpers are insufficient",
        ):
            assert deferred_or_optional in combined_contract

    def test_overview_runtime_must_not_depend_on_mutating_or_model_api_helpers(
        self, app_source: str, api_source: str
    ) -> None:
        assert "fetchNoteMetadata" not in app_source
        assert "saveNoteMetadata" not in app_source
        assert "fetchMaterialMetadata" not in app_source
        assert "saveMaterialMetadata" not in app_source

        initial_load_block = app_source.split("async function loadInitialData()", 1)[1].split(
            "const refreshOMI",
            1,
        )[0]
        for mutating_or_model_helper in (
            "saveNoteMetadata(",
            "saveMaterialMetadata(",
            "runStoryCheck(",
            "saveBible(",
            "saveStoryform(",
            "approveOMICandidate(",
            "rejectOMICandidate(",
        ):
            assert mutating_or_model_helper not in initial_load_block

        assert "export async function runStoryCheck(" in api_source
        assert "const handleRunStoryCheck" in app_source
        assert "onRunStoryCheck={handleRunStoryCheck}" in app_source

    @pytest.mark.parametrize(
        "source_path",
        [
            APP_JSX,
            PROJECT_NAV_JSX,
            PROJECT_OVERVIEW_JSX,
            EDITOR_JSX,
            PROJECT_CONTEXT_JSX,
            API_JS,
            SHARED_DOCUMENT_CONTROLLER_JS,
        ],
    )
    def test_runtime_sources_exclude_overview_forbidden_behavior(
        self, source_path: Path
    ) -> None:
        lower_source = read_source(source_path).lower()
        forbidden_terms = [
            "generated summary",
            "ai summary",
            "summarize project",
            "summarize note",
            "summarize material",
            "extract characters",
            "extract locations",
            "extract timeline",
            "semantic search",
            "model call",
            "apply promotion",
            "canon mutation",
            "memory mutation",
            "training data",
            "jsonl",
            "dataset",
        ]
        for term in forbidden_terms:
            assert term not in lower_source, (
                f"{source_path.relative_to(REPO_ROOT)} must not contain overview-forbidden term {term!r}"
            )

        if source_path in {APP_JSX, PROJECT_NAV_JSX, EDITOR_JSX, PROJECT_CONTEXT_JSX}:
            assert "ollama" not in lower_source
            assert "dramatica" not in lower_source


class TestProjectOverviewShellComponent:
    """PHASE7-IMPL-007-T004 source contract for the standalone overview shell."""

    def test_component_exists_and_exports_default_project_overview(
        self, project_overview_source: str
    ) -> None:
        assert PROJECT_OVERVIEW_JSX.exists()
        assert "export default function ProjectOverview({" in project_overview_source

    def test_component_is_prop_driven_and_has_no_api_dependency(
        self, project_overview_source: str
    ) -> None:
        for prop_name in (
            "project",
            "scenes",
            "notes",
            "materials",
            "omiStatus",
            "approvedMemoryStatus",
        ):
            assert prop_name in project_overview_source

        assert "import " not in project_overview_source
        for forbidden_runtime_dependency in (
            "../api",
            "fetch(",
            "client.",
            "axios",
            "save",
            "metadata",
            "/overview",
        ):
            assert forbidden_runtime_dependency not in project_overview_source

    def test_project_identity_uses_safe_prop_fallbacks(
        self, project_overview_source: str
    ) -> None:
        for helper_name in (
            "function getProjectTitle(project)",
            "function getProjectId(project)",
            "function getOptionalProjectField(project, fieldName)",
        ):
            assert helper_name in project_overview_source

        for fallback in (
            "Untitled project",
            "Unknown project ID",
            "Not available",
            "project.project_id ?? project.projectId ?? project.id",
            "project.title ?? project.name",
            "creation_method",
            "'status'",
        ):
            assert fallback in project_overview_source

    def test_counts_are_derived_from_arrays_and_chapter_count_is_omitted(
        self, project_overview_source: str
    ) -> None:
        assert "function countItems(items)" in project_overview_source
        assert "Array.isArray(items) ? items.length : 0" in project_overview_source
        for count_assignment in (
            "const sceneCount = countItems(scenes)",
            "const noteCount = countItems(notes)",
            "const materialCount = countItems(materials)",
        ):
            assert count_assignment in project_overview_source

        assert "chapter" not in project_overview_source.lower()
        for body_access in ("content", "body", "fetchScene", "fetchNote", "fetchMaterial"):
            assert body_access not in project_overview_source

    def test_shell_sections_are_factual_workspace_status_sections(
        self, project_overview_source: str
    ) -> None:
        for section_label in (
            "Project",
            "Scenes",
            "Notes",
            "Materials",
            "OMI",
            "Approved Memory / Canon",
        ):
            assert section_label in project_overview_source

        assert "Project overview" in project_overview_source
        assert "Project ID" in project_overview_source
        assert "Creation method" in project_overview_source

    def test_empty_states_are_simple_and_non_generative(
        self, project_overview_source: str
    ) -> None:
        for empty_state in (
            "No scenes yet.",
            "No notes yet.",
            "No materials yet.",
            "OMI workspace status is not available yet.",
            "No approved memory/canon items shown here yet.",
        ):
            assert empty_state in project_overview_source

        for forbidden_empty_state in (
            "suggest",
            "next step",
            "summary",
            "premise",
            "logline",
        ):
            assert forbidden_empty_state not in project_overview_source.lower()

    def test_navigation_callbacks_are_direct_optional_buttons(
        self, project_overview_source: str
    ) -> None:
        assert "function OverviewAction({ onClick, children })" in project_overview_source
        assert '<button type="button" onClick={onClick}>' in project_overview_source
        for callback_name in (
            "onOpenScenes",
            "onOpenNotes",
            "onOpenMaterials",
            "onOpenOmi",
            "onOpenApprovedMemory",
        ):
            assert callback_name in project_overview_source

        for label in (
            "Open scenes",
            "Open notes",
            "Open materials",
            "Open OMI",
            "Open approved memory",
        ):
            assert label in project_overview_source

    def test_no_backend_overview_or_api_helper_dependency_was_added(
        self,
        app_source: str,
        api_source: str,
        backend_main_source: str,
        project_overview_source: str,
    ) -> None:
        combined_runtime = "\n".join(
            [app_source, api_source, backend_main_source, project_overview_source]
        )
        for forbidden_overview_dependency in (
            "/overview",
            "fetchOverview",
            "getProjectOverview",
            "saveOverview",
        ):
            assert forbidden_overview_dependency not in combined_runtime

        assert "ProjectOverview" in app_source


class TestProjectOverviewIntegration:
    """PHASE7-IMPL-007-T005 source contract for App/ProjectNav overview wiring."""

    def test_app_imports_and_conditionally_renders_project_overview(
        self, app_source: str
    ) -> None:
        assert "import ProjectOverview from './components/ProjectOverview.jsx';" in app_source
        assert "const WORKSPACE_VIEWS = {" in app_source
        assert "OVERVIEW: 'overview'" in app_source
        assert "EDITOR: 'editor'" in app_source
        assert "const [activeWorkspaceView, setActiveWorkspaceView] = useState(WORKSPACE_VIEWS.OVERVIEW)" in (
            app_source
        )
        assert "activeWorkspaceView === WORKSPACE_VIEWS.OVERVIEW ? (" in app_source
        assert "<ProjectOverview" in app_source

    def test_app_passes_deterministic_overview_props_only(
        self, app_source: str
    ) -> None:
        for prop in (
            "project={activeProject}",
            "scenes={scenes}",
            "notes={notes}",
            "materials={materials}",
            "omiStatus={{",
            "approvedMemoryStatus=\"No approved memory/canon items shown here yet.\"",
        ):
            assert prop in app_source

        overview_render = app_source.split("<ProjectOverview", 1)[1].split("/>", 1)[0]
        for forbidden_prop_or_helper in (
            "sceneContent",
            "noteContent",
            "materialContent",
            "saveNoteMetadata",
            "saveMaterialMetadata",
            "fetchOverview",
            "getProjectOverview",
            "saveOverview",
        ):
            assert forbidden_prop_or_helper not in overview_render

    def test_project_nav_accepts_and_renders_overview_workspace_item(
        self, app_source: str, project_nav_source: str
    ) -> None:
        assert "activeWorkspaceView = 'overview'" in project_nav_source
        assert "onSelectOverview" in project_nav_source
        assert 'aria-label="Workspace"' in project_nav_source
        assert "Overview" in project_nav_source
        assert "activeWorkspaceView === 'overview' ? ' is-active' : ''" in project_nav_source
        assert "onClick={() => onSelectOverview?.()}" in project_nav_source
        assert "activeWorkspaceView={activeWorkspaceView}" in app_source
        assert "onSelectOverview={handleSelectOverview}" in app_source

    def test_document_selection_switches_to_editor_view_and_keeps_id_callbacks(
        self, app_source: str, project_nav_source: str
    ) -> None:
        for callback_name, id_token in (
            ("handleSelectScene", "sceneId"),
            ("handleSelectNote", "noteId"),
            ("handleSelectMaterial", "materialId"),
        ):
            body = TestSharedDocumentStateContract._callback_body(app_source, callback_name)
            assert "setActiveWorkspaceView(WORKSPACE_VIEWS.EDITOR)" in body
            assert id_token in body

        for nav_callback in (
            "onSelectScene(sceneId)",
            "onSelectNote?.(noteId)",
            "onSelectMaterial?.(materialId)",
        ):
            assert nav_callback in project_nav_source

    def test_overview_selection_and_project_switch_preserve_dirty_guard(
        self, app_source: str
    ) -> None:
        overview_body = TestSharedDocumentStateContract._callback_body(
            app_source,
            "handleSelectOverview",
        )
        assert "hasUnsavedDocumentChanges" in overview_body
        assert "window.confirm(UNSAVED_PROJECT_SWITCH_MESSAGE)" in overview_body
        assert "setActiveWorkspaceView(WORKSPACE_VIEWS.OVERVIEW)" in overview_body

        project_switch_body = TestSharedDocumentStateContract._callback_body(
            app_source,
            "handleSelectProject",
        )
        assert "hasUnsavedDocumentChanges" in project_switch_body
        assert "window.confirm(UNSAVED_PROJECT_SWITCH_MESSAGE)" in project_switch_body
        assert "setActiveProjectId(projectId)" in project_switch_body
        assert "setActiveWorkspaceView(WORKSPACE_VIEWS.OVERVIEW)" in app_source

    def test_keyboard_save_is_editor_view_only(self, app_source: str) -> None:
        assert "function handleKeyDown(event)" in app_source
        keydown_body = app_source.split("function handleKeyDown(event)", 1)[1].split(
            "window.addEventListener('keydown'",
            1,
        )[0]
        assert "event.preventDefault()" in keydown_body
        assert "activeWorkspaceView !== WORKSPACE_VIEWS.EDITOR" in keydown_body
        assert "handleSaveNote()" in keydown_body
        assert "handleSaveMaterial()" in keydown_body
        assert "handleSave();" in keydown_body

    def test_overview_callbacks_are_safe_view_switches(
        self, app_source: str
    ) -> None:
        callback_body = TestSharedDocumentStateContract._callback_body(
            app_source,
            "handleOpenEditorWorkspace",
        )
        assert "setActiveWorkspaceView(WORKSPACE_VIEWS.EDITOR)" in callback_body
        for forbidden_operation in (
            "save",
            "fetch",
            "runStoryCheck",
            "createOMI",
            "updateOMI",
            "Promotion",
        ):
            assert forbidden_operation not in callback_body

        overview_render = app_source.split("<ProjectOverview", 1)[1].split("/>", 1)[0]
        for callback_prop in (
            "onOpenScenes={handleOpenEditorWorkspace}",
            "onOpenNotes={handleOpenEditorWorkspace}",
            "onOpenMaterials={handleOpenEditorWorkspace}",
            "onOpenOmi={handleOpenEditorWorkspace}",
        ):
            assert callback_prop in overview_render

    def test_no_backend_or_api_overview_dependency_after_integration(
        self, app_source: str, api_source: str, project_overview_source: str
    ) -> None:
        combined_runtime = "\n".join([app_source, api_source, project_overview_source])
        for forbidden_dependency in (
            "/overview",
            "fetchOverview",
            "getProjectOverview",
            "saveOverview",
        ):
            assert forbidden_dependency not in combined_runtime


class TestProjectOverviewRegressionCoverage:
    """PHASE7-IMPL-007-T006 regression guard for the integrated overview view."""

    def test_overview_is_workspace_view_not_document_type(
        self, app_source: str, shared_document_controller_source: str
    ) -> None:
        assert "const WORKSPACE_VIEWS = {" in app_source
        assert "OVERVIEW: 'overview'" in app_source
        assert "EDITOR: 'editor'" in app_source
        assert "const [activeWorkspaceView, setActiveWorkspaceView]" in app_source

        document_types_block = shared_document_controller_source.split(
            "export const DOCUMENT_TYPES = Object.freeze({",
            1,
        )[1].split("});", 1)[0]
        assert "SCENE: 'scene'" in document_types_block
        assert "NOTE: 'note'" in document_types_block
        assert "MATERIAL: 'material'" in document_types_block
        assert "overview" not in document_types_block

    def test_overview_selection_is_not_document_body_load_or_save(
        self, app_source: str
    ) -> None:
        overview_body = TestSharedDocumentStateContract._callback_body(
            app_source,
            "handleSelectOverview",
        )
        assert "setActiveWorkspaceView(WORKSPACE_VIEWS.OVERVIEW)" in overview_body
        for forbidden_operation in (
            "setSelectedDocumentType",
            "setSelectedSceneId",
            "setSelectedNoteId",
            "setSelectedMaterialId",
            "fetchScene",
            "fetchNote",
            "fetchMaterial",
            "saveScene",
            "saveNote",
            "saveMaterial",
        ):
            assert forbidden_operation not in overview_body

    def test_editor_and_overview_rendering_are_separate_branches(
        self, app_source: str
    ) -> None:
        overview_branch = app_source.split(
            "activeWorkspaceView === WORKSPACE_VIEWS.OVERVIEW ? (",
            1,
        )[1].split(") : (", 1)[0]
        editor_branch = app_source.split(") : (", 1)[1].split("</main>", 1)[0]

        assert "<ProjectOverview" in overview_branch
        assert "<Editor" not in overview_branch
        assert "<ProjectContext" not in overview_branch
        assert "<OMIPanel" not in overview_branch
        assert "<Editor" in editor_branch
        assert "<ProjectOverview" not in editor_branch

    def test_project_overview_props_remain_deterministic_and_body_free(
        self, app_source: str
    ) -> None:
        overview_render = app_source.split("<ProjectOverview", 1)[1].split("/>", 1)[0]
        for expected_prop in (
            "project={activeProject}",
            "scenes={scenes}",
            "notes={notes}",
            "materials={materials}",
            "omiStatus={{",
            "ideas: omiData?.ideas",
            "candidates: omiData?.candidates",
            "approvedMemoryStatus=\"No approved memory/canon items shown here yet.\"",
        ):
            assert expected_prop in overview_render

        for forbidden_prop in (
            "sceneContent",
            "noteContent",
            "materialContent",
            "lastSavedContent",
            "lastSavedNoteContent",
            "lastSavedMaterialContent",
            "saveScene",
            "saveNote",
            "saveMaterial",
            "runStoryCheck",
            "createOMICandidate",
            "createOMIPromotion",
        ):
            assert forbidden_prop not in overview_render

    def test_project_overview_count_and_status_contract_remains_shell_only(
        self, project_overview_source: str
    ) -> None:
        assert "Array.isArray(items) ? items.length : 0" in project_overview_source
        for count_line in (
            "const sceneCount = countItems(scenes)",
            "const noteCount = countItems(notes)",
            "const materialCount = countItems(materials)",
            "{getStatusCount(omiStatus, 'ideas')} ideas",
            "{getStatusCount(omiStatus, 'candidates')} candidates",
        ):
            assert count_line in project_overview_source

        assert "No approved memory/canon items shown here yet." in project_overview_source
        assert "OMI workspace status is not available yet." in project_overview_source
        assert "chapter" not in project_overview_source.lower()
        for forbidden_body_source in ("content", "body", "fetchScene", "fetchNote", "fetchMaterial"):
            assert forbidden_body_source not in project_overview_source

    def test_project_nav_overview_item_is_workspace_only(
        self, project_nav_source: str
    ) -> None:
        workspace_nav = project_nav_source.split('aria-label="Workspace"', 1)[1].split(
            "</nav>",
            1,
        )[0]
        assert "activeWorkspaceView === 'overview' ? ' is-active' : ''" in workspace_nav
        assert "onClick={() => onSelectOverview?.()}" in workspace_nav
        assert "Overview" in workspace_nav
        assert "Project status" in workspace_nav

        for forbidden_workspace_action in (
            "onSelectScene",
            "onSelectNote",
            "onSelectMaterial",
            "activeDocumentType",
            "activeDocumentId",
            "DOCUMENT_TYPES",
            "save",
            "fetch",
            "import",
            "upload",
            "promotion",
        ):
            assert forbidden_workspace_action not in workspace_nav

    def test_document_highlighting_and_callbacks_still_use_type_and_id(
        self, project_nav_source: str
    ) -> None:
        for active_check in (
            "isActiveDocument(activeDocumentType, activeDocumentId, DOCUMENT_TYPES.SCENE, sceneId)",
            "isActiveDocument(activeDocumentType, activeDocumentId, DOCUMENT_TYPES.NOTE, noteId)",
            "isActiveDocument(activeDocumentType, activeDocumentId, DOCUMENT_TYPES.MATERIAL, materialId)",
        ):
            assert active_check in project_nav_source

        for id_callback in (
            "onSelectScene(sceneId)",
            "onSelectNote?.(noteId)",
            "onSelectMaterial?.(materialId)",
        ):
            assert id_callback in project_nav_source

    def test_overview_navigation_callbacks_only_switch_local_view(
        self, app_source: str
    ) -> None:
        callback_body = TestSharedDocumentStateContract._callback_body(
            app_source,
            "handleOpenEditorWorkspace",
        )
        assert "setActiveWorkspaceView(WORKSPACE_VIEWS.EDITOR)" in callback_body
        for forbidden_operation in (
            "save",
            "fetch",
            "runStoryCheck",
            "createOMI",
            "updateOMI",
            "Promotion",
            "metadata",
        ):
            assert forbidden_operation not in callback_body

        overview_render = app_source.split("<ProjectOverview", 1)[1].split("/>", 1)[0]
        for callback_prop in (
            "onOpenScenes={handleOpenEditorWorkspace}",
            "onOpenNotes={handleOpenEditorWorkspace}",
            "onOpenMaterials={handleOpenEditorWorkspace}",
            "onOpenOmi={handleOpenEditorWorkspace}",
        ):
            assert callback_prop in overview_render

    def test_dirty_state_guards_overview_document_and_project_switches(
        self, app_source: str
    ) -> None:
        for callback_name in (
            "handleSelectOverview",
            "handleSelectProject",
            "handleSelectScene",
            "handleSelectNote",
            "handleSelectMaterial",
        ):
            body = TestSharedDocumentStateContract._callback_body(app_source, callback_name)
            assert "hasUnsavedDocumentChanges" in body
            assert "window.confirm" in body

        assert "const hasUnsavedDocumentChanges = hasUnsavedDocumentEdits({" in app_source
        assert "activeWorkspaceView" not in app_source.split(
            "const hasUnsavedDocumentChanges = hasUnsavedDocumentEdits({",
            1,
        )[1].split("});", 1)[0]

    def test_keyboard_save_is_gated_to_editor_view_and_document_save_handlers(
        self, app_source: str
    ) -> None:
        keydown_body = app_source.split("function handleKeyDown(event)", 1)[1].split(
            "window.addEventListener('keydown'",
            1,
        )[0]
        assert "event.preventDefault()" in keydown_body
        assert "activeWorkspaceView !== WORKSPACE_VIEWS.EDITOR" in keydown_body
        assert keydown_body.index("activeWorkspaceView !== WORKSPACE_VIEWS.EDITOR") < keydown_body.index(
            "handleSaveNote()"
        )
        assert "handleSaveNote()" in keydown_body
        assert "handleSaveMaterial()" in keydown_body
        assert "handleSave();" in keydown_body
        assert "ProjectOverview" not in keydown_body

    def test_project_switch_resets_overview_and_clears_stale_document_state(
        self, app_source: str
    ) -> None:
        project_reset_block = app_source.split("useEffect(() => {", 1)[1].split(
            "async function loadInitialData()",
            1,
        )[0]
        for reset in (
            "setActiveWorkspaceView(WORKSPACE_VIEWS.OVERVIEW)",
            "setSelectedSceneId('')",
            "setSelectedDocumentType('')",
            "setSelectedNoteId('')",
            "setSelectedMaterialId('')",
            "setSceneContent('')",
            "setNoteContent('')",
            "setMaterialContent('')",
            "setLastSavedContent('')",
            "setLastSavedNoteContent('')",
            "setLastSavedMaterialContent('')",
        ):
            assert reset in project_reset_block

        initial_load_block = app_source.split("async function loadInitialData()", 1)[1].split(
            "const refreshOMI",
            1,
        )[0]
        assert "fetchOverview" not in initial_load_block
        assert "/overview" not in initial_load_block
        assert "setScenes(Array.isArray(scenePayload) ? scenePayload : scenePayload.scenes ?? [])" in (
            initial_load_block
        )
        assert "setNotes(notesPayload?.notes ?? [])" in initial_load_block
        assert "setMaterials(materialsPayload?.materials ?? [])" in initial_load_block

    def test_no_runtime_overview_backend_or_api_dependency_exists(
        self,
        app_source: str,
        api_source: str,
        project_overview_source: str,
        backend_main_source: str,
        project_manager_source: str,
    ) -> None:
        runtime_sources = (
            app_source,
            api_source,
            project_overview_source,
            backend_main_source,
            project_manager_source,
        )
        for source in runtime_sources:
            for forbidden_dependency in (
                "'/overview",
                '"/overview',
                "`/overview",
                "@app.get(\"/api/projects/{project_name}/overview\")",
                "fetchOverview",
                "getProjectOverview",
                "saveOverview",
                "overview route",
                "project overview api",
            ):
                assert forbidden_dependency not in source.lower()

    def test_editor_and_metadata_contracts_remain_separate_from_overview(
        self, app_source: str, editor_source: str, project_nav_source: str
    ) -> None:
        assert "selectedDocumentId={activeEditorDocument.id}" in app_source
        assert "documentType={activeEditorDocument.type}" in app_source
        assert "documentError={activeEditorDocument.error}" in app_source
        assert "selectedDocumentId" in editor_source
        assert "selectedSceneId" not in editor_source

        for save_call in (
            "saveScene(selectedSceneId, sceneContent, activeProjectId)",
            "saveNote(selectedNoteId, noteContent, activeProjectId)",
            "saveMaterial(selectedMaterialId, materialContent, activeProjectId)",
        ):
            assert save_call in app_source

        for metadata_helper in (
            "fetchNoteMetadata",
            "saveNoteMetadata",
            "fetchMaterialMetadata",
            "saveMaterialMetadata",
        ):
            assert metadata_helper not in app_source

        assert "onSelectOverview?.()" in project_nav_source
        assert "onSelectOverview?.(activeDocumentId)" not in project_nav_source

    @pytest.mark.parametrize(
        "source_path",
        [
            APP_JSX,
            PROJECT_NAV_JSX,
            PROJECT_OVERVIEW_JSX,
            EDITOR_JSX,
            SHARED_DOCUMENT_CONTROLLER_JS,
            API_JS,
        ],
    )
    def test_overview_frontend_runtime_excludes_unsafe_terms(
        self, source_path: Path
    ) -> None:
        lower_source = read_source(source_path).lower()
        for forbidden_term in (
            "generated summary",
            "ai summary",
            "summarize project",
            "summarize note",
            "summarize material",
            "extract characters",
            "extract locations",
            "extract timeline",
            "semantic search",
            "story analysis",
            "story check auto-run",
            "dramatica analysis",
            "ollama call",
            "model call",
            "apply promotion",
            "canon mutation",
            "memory mutation",
            "training data",
            "jsonl",
            "dataset",
        ):
            assert forbidden_term not in lower_source


class TestOmiGuidedProjectCreationStagedFlowContract:
    """PHASE7-IMPL-008-T002 source contract before staged-flow runtime work."""

    def test_staged_setup_state_shape_is_documented_before_runtime_work(
        self,
        task_008_source: str,
        inventory_008_source: str,
        enrichment_008_source: str,
    ) -> None:
        combined_contract = "\n".join([task_008_source, inventory_008_source, enrichment_008_source])
        for concept in (
            "raw idea",
            "optional owner inputs",
            "setup candidate entries with visible labels",
            "selected initialization fields",
            "status",
            "final confirmation flag",
            "timestamps",
            "project ID preview",
        ):
            assert concept in combined_contract

        for separation_rule in (
            "separate from durable project truth",
            "before final project creation",
            "until the owner explicitly confirms",
        ):
            assert separation_rule in combined_contract

    def test_owner_authored_input_only_and_no_generated_setup_contract(
        self,
        task_008_source: str,
        inventory_008_source: str,
        omi_guided_creation_spec_source: str,
    ) -> None:
        combined_contract = "\n".join(
            [task_008_source, inventory_008_source, omi_guided_creation_spec_source]
        )
        for owner_input in (
            "owner-authored inputs only",
            "Raw idea",
            "Working title",
            "Owner-authored description",
            "Owner-authored premise note",
            "Owner-authored prose snippets",
        ):
            assert owner_input in combined_contract

        for prohibited_output in (
            "Generated prose",
            "AI-written setup suggestions",
            "AI-written premise copy",
            "AI-written genre copy",
            "AI-written sample openings",
            "AI-written blurbs",
            "AI-written summaries",
        ):
            assert prohibited_output in combined_contract

    def test_visible_setup_candidate_labels_remain_required(
        self,
        task_008_source: str,
        inventory_008_source: str,
        omi_guided_creation_spec_source: str,
        omi_panel_source: str,
    ) -> None:
        combined_contract = "\n".join(
            [task_008_source, inventory_008_source, omi_guided_creation_spec_source]
        )
        for label_contract in (
            "Setup candidates are not canon",
            "visibly labeled as candidates",
            "Setup candidate: project title",
            "Setup candidate: genre tag",
            "Setup candidate: premise note",
            "Setup candidate: character note",
            "not initialize `project.json`",
        ):
            assert label_contract in combined_contract

        for existing_visible_label in (
            "Project bible candidate",
            "Storyform context candidate",
            "Scene prompt context candidate",
            "Pending",
            "Approved",
            "Rejected",
            "Needs revision",
        ):
            assert existing_visible_label in omi_panel_source

    def test_final_confirmation_boundary_blocks_hidden_project_creation(
        self,
        task_008_source: str,
        inventory_008_source: str,
        omi_guided_creation_spec_source: str,
        backend_main_source: str,
    ) -> None:
        combined_contract = "\n".join(
            [task_008_source, inventory_008_source, omi_guided_creation_spec_source]
        )
        for final_confirmation_term in (
            "final confirmation step",
            "explicit final confirmation",
            "before confirmation",
            "after confirmation",
            "final_confirmation",
            "No hidden project writes during wizard steps",
        ):
            assert final_confirmation_term in combined_contract

        assert "POST /api/projects/from-omi" in combined_contract
        assert "/api/projects/from-omi" not in backend_main_source
        assert "class ProjectCreate" in backend_main_source
        assert '@app.post("/api/projects")' in backend_main_source

    def test_no_hidden_project_writes_before_confirmation_contract(
        self,
        task_008_source: str,
        inventory_008_source: str,
        app_source: str,
        api_source: str,
    ) -> None:
        combined_contract = "\n".join([task_008_source, inventory_008_source])
        for forbidden_pre_confirmation_write in (
            "`project.json`",
            "`bible.json`",
            "`storyform.json`",
            "scenes, chapters, notes, materials",
            "memory/canon",
            "OMI promotion records",
        ):
            assert forbidden_pre_confirmation_write in combined_contract

        for staged_helper in (
            "createOMISetup",
            "updateOMISetup",
            "createProjectFromOMISetup",
            "fetchOMISetup",
            "from-omi",
        ):
            assert staged_helper not in app_source
            assert staged_helper not in api_source

    def test_blank_project_creation_compatibility_is_locked(
        self,
        app_source: str,
        api_source: str,
        backend_main_source: str,
        project_manager_source: str,
        project_creation_spec_source: str,
    ) -> None:
        assert "createProject(trimmedTitle)" in app_source
        assert "export async function createProject(title)" in api_source
        assert "client.post('/projects', { title })" in api_source
        assert '@app.post("/api/projects")' in backend_main_source
        assert "return project_manager.create_project(title=payload.title)" in backend_main_source
        assert "def create_project(" in project_manager_source
        assert "derive_project_id" in project_manager_source
        assert "validate_project_id" in project_manager_source
        assert "resolve_project_id_with_collision" in project_manager_source
        assert "Project creation must follow these principles" in project_creation_spec_source
        assert "Blank project creation is the first implementation path." in project_creation_spec_source

    def test_project_id_preview_must_reuse_safe_creation_rules_without_writes(
        self,
        task_008_source: str,
        inventory_008_source: str,
        project_creation_spec_source: str,
        project_manager_source: str,
    ) -> None:
        combined_contract = "\n".join([task_008_source, inventory_008_source, project_creation_spec_source])
        for preview_contract in (
            "project ID preview",
            "exact `project_id`",
            "project_id",
            "derive_project_id",
            "validate_project_id",
            "collision",
        ):
            assert preview_contract in combined_contract or preview_contract in project_manager_source

        for helper_name in (
            "def derive_project_id(",
            "def validate_project_id(",
            "def resolve_project_id_with_collision(",
        ):
            assert helper_name in project_manager_source

        assert "preview must not create a project directory" not in project_manager_source.lower()

    def test_cancel_project_switch_and_completion_cleanup_contract(
        self,
        task_008_source: str,
        inventory_008_source: str,
        app_source: str,
    ) -> None:
        combined_contract = "\n".join([task_008_source, inventory_008_source])
        for cleanup_term in (
            "clear stale setup draft state on cancel",
            "on project switch",
            "on completion",
            "on app reload",
            "no auto-resume of abandoned staged setup",
        ):
            assert cleanup_term in combined_contract

        assert "handleSelectProject" in app_source
        assert "UNSAVED_PROJECT_SWITCH_MESSAGE" in app_source
        assert "setActiveProjectId(projectId)" in app_source

    def test_omi_compatibility_stays_candidate_only_until_owner_confirmation(
        self,
        task_008_source: str,
        inventory_008_source: str,
        omi_guided_creation_spec_source: str,
        omi_schema_lifecycle_source: str,
        omi_storage_model_source: str,
        omi_ideas_candidates_spec_source: str,
    ) -> None:
        combined_contract = "\n".join(
            [
                task_008_source,
                inventory_008_source,
                omi_guided_creation_spec_source,
                omi_schema_lifecycle_source,
                omi_storage_model_source,
                omi_ideas_candidates_spec_source,
            ]
        )
        for omi_boundary in (
            "candidate-only",
            "not canon",
            "must not be auto-promoted",
            "Promotion records remain audit-only",
            "apply-promotion",
            "memory/canon mutation",
            "project-local OMI records",
            "after final confirmation",
        ):
            assert omi_boundary in combined_contract

    def test_backend_staged_setup_helpers_are_optional_future_work(
        self,
        task_008_source: str,
        inventory_008_source: str,
        backend_main_source: str,
        project_manager_source: str,
    ) -> None:
        combined_contract = "\n".join([task_008_source, inventory_008_source])
        for optional_contract in (
            "if needed",
            "transient frontend state",
            "staged setup route",
            "Reuse `_safe_path_component`/`validate_project_id` patterns",
            "reuse the same ID validation",
            "path safety",
            "No staged setup helpers exist yet",
        ):
            assert optional_contract in combined_contract

        for absent_backend_surface in (
            "create_staged_setup",
            "load_staged_setup",
            "update_staged_setup",
            "finalize_staged_setup",
            "project-setups",
            "from-omi",
        ):
            assert absent_backend_surface not in backend_main_source
            assert absent_backend_surface not in project_manager_source

    def test_frontend_integration_surface_is_future_and_separate_from_editor(
        self,
        task_008_source: str,
        inventory_008_source: str,
        app_source: str,
        api_source: str,
        project_nav_source: str,
    ) -> None:
        combined_contract = "\n".join([task_008_source, inventory_008_source])
        for future_surface in (
            "frontend/src/App.jsx",
            "frontend/src/api.js",
            "staged creation wizard",
            "Routing the owner to the Project Overview shell",
            "The shared owner-authored editor must not be reached from the staged setup wizard.",
        ):
            assert future_surface in combined_contract

        assert "Create blank project" in project_nav_source
        assert "handleCreateProject" in app_source
        assert "createProject(title)" in api_source
        assert "OMI-guided" not in app_source
        assert "OMI-guided" not in project_nav_source
        assert "StagedSetupWizard" not in app_source
        assert "selectedDocumentType" in app_source

    @pytest.mark.parametrize(
        "source_path",
        [
            APP_JSX,
            API_JS,
            PROJECT_NAV_JSX,
            PROJECT_OVERVIEW_JSX,
            PROJECT_CONTEXT_JSX,
            EDITOR_JSX,
            SHARED_DOCUMENT_CONTROLLER_JS,
        ],
    )
    def test_frontend_runtime_sources_exclude_staged_flow_forbidden_terms(
        self, source_path: Path
    ) -> None:
        lower_source = read_source(source_path).lower()
        for forbidden_term in (
            "generated setup",
            "generated prose",
            "ai-written setup",
            "ai suggestion",
            "summarize project",
            "summarize idea",
            "summarize note",
            "summarize material",
            "extract characters",
            "extract locations",
            "extract timeline",
            "semantic search",
            "story analysis",
            "story check auto-run",
            "dramatica analysis",
            "ollama call",
            "model call",
            "apply promotion",
            "canon mutation",
            "memory mutation",
            "hidden project write",
            "training data",
            "jsonl",
            "dataset",
        ):
            assert forbidden_term not in lower_source

    def test_backend_runtime_has_no_staged_setup_or_hidden_write_surface(
        self, backend_main_source: str, project_manager_source: str
    ) -> None:
        for source in (backend_main_source, project_manager_source):
            for absent_surface in (
                "project-setups",
                "projects/from-omi",
                "create_project_from_omi",
                "staged_setup",
                "setup_id",
                "hidden project write",
                "generated setup",
                "ai-written setup",
                "model call",
                "semantic search",
            ):
                assert absent_surface not in source.lower()


class TestSceneMetadataDisplayCompatibility:
    def test_normalizes_legacy_scene_string_ids(self, project_nav_source: str) -> None:
        assert "function normalizeSceneOption" in project_nav_source
        assert "typeof scene === 'string'" in project_nav_source
        assert "sceneId: scene" in project_nav_source
        assert "label: scene" in project_nav_source
        assert "chapterId: null" in project_nav_source
        assert "metadataExists: false" in project_nav_source

    def test_normalizes_metadata_shaped_scene_records(self, project_nav_source: str) -> None:
        assert "function normalizeSceneList" in project_nav_source
        assert "scene.scene_id" in project_nav_source
        assert "scene.sceneId" in project_nav_source
        assert "scene.id" in project_nav_source
        assert "scene.chapter_id" in project_nav_source
        assert "scene.metadata_exists" in project_nav_source

    def test_scene_title_label_falls_back_to_scene_id(self, project_nav_source: str) -> None:
        assert "function getSceneOptionLabel" in project_nav_source
        assert ".trim()" in project_nav_source
        assert "const title = rawTitle || sceneId || ''" in project_nav_source
        assert "sceneOption.label || sceneOption.sceneId" in project_nav_source

    def test_scene_order_uses_metadata_order_fields_only_for_display_order(
        self, project_nav_source: str
    ) -> None:
        assert "function normalizeSceneOrder" in project_nav_source
        assert "scene.order_index" in project_nav_source
        assert "scene.orderIndex" in project_nav_source
        assert "scene.order" in project_nav_source
        assert "left.orderIndex - right.orderIndex" in project_nav_source
        assert "left.originalIndex - right.originalIndex" in project_nav_source

    def test_scene_selection_uses_scene_id_not_title(self, project_nav_source: str) -> None:
        assert "function getSceneOptionId" in project_nav_source
        assert "const sceneId = getSceneOptionId(scene)" in project_nav_source
        assert "onSelectScene(sceneId)" in project_nav_source
        assert "onSelectScene(sceneLabel)" not in project_nav_source

    def test_mixed_metadata_and_legacy_scenes_remain_display_safe(
        self, project_nav_source: str
    ) -> None:
        assert ".map(normalizeSceneOption)" in project_nav_source
        assert ".filter((scene) => scene?.sceneId)" in project_nav_source
        assert "scene.metadata_exists" in project_nav_source
        assert "const sceneLabel = getSceneOptionLabel(scene)" in project_nav_source
        assert "<span>{sceneLabel}</span>" in project_nav_source
        assert "onSelectScene(sceneId)" in project_nav_source

    def test_scene_display_does_not_inject_metadata_into_editor_body(
        self, project_nav_source: str
    ) -> None:
        assert "fetchScene" not in project_nav_source
        assert "saveScene" not in project_nav_source
        assert "content_path" not in project_nav_source
        assert "sceneContent" not in project_nav_source

    @pytest.mark.parametrize(
        "unsafe_phrase",
        [
            "generate story",
            "write story",
            "continue story",
            "rewrite",
            "improve prose",
            "generate project idea",
            "generate summary",
            "scene summary",
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


class TestApiNoteMaterialHelpers:
    """PHASE7-IMPL-005 frontend API compatibility helpers for notes and materials."""

    NOTE_HELPERS = (
        "fetchNotes",
        "fetchNote",
        "saveNote",
        "fetchNoteMetadata",
        "saveNoteMetadata",
    )

    MATERIAL_HELPERS = (
        "fetchMaterials",
        "fetchMaterial",
        "saveMaterial",
        "fetchMaterialMetadata",
        "saveMaterialMetadata",
    )

    ALL_NEW_HELPERS = NOTE_HELPERS + MATERIAL_HELPERS

    # ---- 1 & 2: All 10 helpers are exported ----

    @pytest.mark.parametrize("function_name", NOTE_HELPERS)
    def test_note_helpers_are_exported(
        self, api_source: str, function_name: str
    ) -> None:
        pattern = rf"export async function {function_name}\s*\("
        assert re.search(pattern, api_source), (
            f"{function_name} should be exported as async function"
        )

    @pytest.mark.parametrize("function_name", MATERIAL_HELPERS)
    def test_material_helpers_are_exported(
        self, api_source: str, function_name: str
    ) -> None:
        pattern = rf"export async function {function_name}\s*\("
        assert re.search(pattern, api_source), (
            f"{function_name} should be exported as async function"
        )

    # ---- 3: Note helpers call the correct endpoint strings ----

    def test_fetch_notes_uses_list_endpoint(self, api_source: str) -> None:
        assert (
            "client.get(`/projects/${projectId}/notes`)" in api_source
        )

    def test_fetch_note_uses_id_endpoint(self, api_source: str) -> None:
        assert (
            "client.get(`/projects/${projectId}/notes/${noteId}`)"
            in api_source
        )

    def test_fetch_note_metadata_uses_metadata_endpoint(
        self, api_source: str
    ) -> None:
        assert (
            "client.get(`/projects/${projectId}/notes/${noteId}/metadata`)"
            in api_source
        )

    # ---- 4: Material helpers call the correct endpoint strings ----

    def test_fetch_materials_uses_list_endpoint(self, api_source: str) -> None:
        assert (
            "client.get(`/projects/${projectId}/materials`)" in api_source
        )

    def test_fetch_material_uses_id_endpoint(self, api_source: str) -> None:
        assert (
            "client.get(`/projects/${projectId}/materials/${materialId}`)"
            in api_source
        )

    def test_fetch_material_metadata_uses_metadata_endpoint(
        self, api_source: str
    ) -> None:
        assert (
            "client.get(`/projects/${projectId}/materials/${materialId}/metadata`)"
            in api_source
        )

    # ---- 5: Save helpers send body payloads with { content } ----

    def test_save_note_sends_content_payload(self, api_source: str) -> None:
        assert (
            "client.put(`/projects/${projectId}/notes/${noteId}`, { content })"
            in api_source
        )

    def test_save_material_sends_content_payload(self, api_source: str) -> None:
        assert (
            "client.put(`/projects/${projectId}/materials/${materialId}`, { content })"
            in api_source
        )

    # ---- 6: Metadata save helpers send payloads with { metadata } ----

    def test_save_note_metadata_sends_metadata_payload(
        self, api_source: str
    ) -> None:
        assert (
            "client.put(`/projects/${projectId}/notes/${noteId}/metadata`, { metadata })"
            in api_source
        )

    def test_save_material_metadata_sends_metadata_payload(
        self, api_source: str
    ) -> None:
        assert (
            "client.put(`/projects/${projectId}/materials/${materialId}/metadata`, { metadata })"
            in api_source
        )

    # ---- 7: Helpers preserve existing PROJECT_ID default behaviour ----

    @pytest.mark.parametrize("function_name", ALL_NEW_HELPERS)
    def test_new_helpers_preserve_project_id_default(
        self, api_source: str, function_name: str
    ) -> None:
        pattern = (
            rf"export async function {function_name}\([^)]*projectId = PROJECT_ID"
        )
        assert re.search(pattern, api_source), (
            f"{function_name} should accept optional projectId defaulting to PROJECT_ID"
        )

    # ---- 8: Existing scene API helper source patterns remain intact ----

    def test_existing_scene_helpers_remain_intact(self, api_source: str) -> None:
        for fn in ("fetchScenes", "fetchScene", "saveScene"):
            pattern = rf"export async function {fn}\s*\("
            assert re.search(pattern, api_source), (
                f"existing helper {fn} should remain exported"
            )
        assert (
            "client.get(`/projects/${projectId}/scenes/${sceneId}`)" in api_source
        )
        assert (
            "client.put(`/projects/${projectId}/scenes/${sceneId}`, { content })"
            in api_source
        )

    # ---- 9: No prose, summary, extraction, model, OMI, memory/canon, or
    #          training/dataset behaviour was introduced ----

    def test_api_js_excludes_forbidden_workspace_terms(
        self, api_source: str
    ) -> None:
        lower_source = api_source.lower()
        forbidden_terms = [
            "apply-promotion",
            "apply promotion",
            "canon promotion",
            "extraction",
            "dramatica",
            "ollama",
            "model generation",
            "notes summary",
            "material summary",
            "navigation prose",
        ]
        for term in forbidden_terms:
            assert term not in lower_source, (
                f"api.js should not contain forbidden term {term!r}"
            )

    def test_api_js_does_not_inject_metadata_into_content_payload(
        self, api_source: str
    ) -> None:
        """Save body helpers must not bundle metadata into the body payload.

        The saveNote and saveMaterial helpers are body-only; metadata writes
        use the dedicated metadata PUT helpers.
        """
        for endpoint_pattern, id_label in (
            (
                r"client\.put\(`/projects/\$\{projectId\}/notes/\$\{noteId\}`,\s*(\{[^}]*\})\)",
                "note",
            ),
            (
                r"client\.put\(`/projects/\$\{projectId\}/materials/\$\{materialId\}`,\s*(\{[^}]*\})\)",
                "material",
            ),
        ):
            match = re.search(endpoint_pattern, api_source)
            assert match is not None, (
                f"expected save body endpoint for {id_label}"
            )
            payload = match.group(1)
            assert "metadata" not in payload, (
                f"{id_label} body save payload must not include metadata: {payload!r}"
            )
            assert "content" in payload, (
                f"{id_label} body save payload must include content: {payload!r}"
            )

    def test_metadata_helpers_carry_no_extra_body_fields(
        self, api_source: str
    ) -> None:
        """Metadata PUT helpers must send a flat { metadata } payload only."""
        for endpoint_pattern, label in (
            (
                r"client\.put\(`/projects/\$\{projectId\}/notes/\$\{noteId\}/metadata`,\s*(\{[^}]*\})\)",
                "note",
            ),
            (
                r"client\.put\(`/projects/\$\{projectId\}/materials/\$\{materialId\}/metadata`,\s*(\{[^}]*\})\)",
                "material",
            ),
        ):
            match = re.search(endpoint_pattern, api_source)
            assert match is not None, (
                f"expected metadata PUT endpoint for {label}"
            )
            payload = match.group(1)
            assert "metadata" in payload, (
                f"{label} metadata payload must include metadata: {payload!r}"
            )
            assert "content" not in payload, (
                f"{label} metadata payload must not include content: {payload!r}"
            )


class TestNoteMaterialShellSource:
    def test_app_imports_only_body_level_note_material_helpers(
        self, app_source: str
    ) -> None:
        for helper in (
            "fetchNotes",
            "fetchNote",
            "saveNote",
            "fetchMaterials",
            "fetchMaterial",
            "saveMaterial",
        ):
            assert helper in app_source

        for metadata_helper in (
            "fetchNoteMetadata",
            "saveNoteMetadata",
            "fetchMaterialMetadata",
            "saveMaterialMetadata",
        ):
            assert metadata_helper not in app_source

    def test_project_nav_has_notes_and_materials_sections(
        self, project_nav_source: str
    ) -> None:
        assert 'aria-label="Notes"' in project_nav_source
        assert 'aria-label="Materials"' in project_nav_source
        assert "No notes yet." in project_nav_source
        assert "No materials yet." in project_nav_source
        assert "Loading notes..." in project_nav_source
        assert "Loading materials..." in project_nav_source

    def test_note_material_labels_fallback_to_ids(self, project_nav_source: str) -> None:
        assert "function normalizeNoteOption" in project_nav_source
        assert "function normalizeMaterialOption" in project_nav_source
        assert "note.note_id" in project_nav_source
        assert "material.material_id" in project_nav_source
        assert "const title = rawTitle || noteId" in project_nav_source
        assert "const title = rawTitle || materialId" in project_nav_source

    def test_note_material_selection_uses_ids_not_titles(
        self, project_nav_source: str
    ) -> None:
        assert "const noteId = getNoteOptionId(note)" in project_nav_source
        assert "const materialId = getMaterialOptionId(material)" in project_nav_source
        assert "onSelectNote?.(noteId)" in project_nav_source
        assert "onSelectMaterial?.(materialId)" in project_nav_source
        assert "onSelectNote?.(noteLabel)" not in project_nav_source
        assert "onSelectMaterial?.(materialLabel)" not in project_nav_source

    def test_app_fetches_exact_note_and_material_bodies(self, app_source: str) -> None:
        assert "fetchNotes(activeProjectId)" in app_source
        assert "fetchMaterials(activeProjectId)" in app_source
        assert "fetchNote(noteId, activeProjectId)" in app_source
        assert "fetchMaterial(materialId, activeProjectId)" in app_source
        assert "const loadedContent = getDocumentResponseContent(data)" in app_source
        assert "setNoteContent(loadedContent)" in app_source
        assert "setMaterialContent(loadedContent)" in app_source

    def test_app_saves_body_content_by_id(self, app_source: str) -> None:
        assert "saveNote(selectedNoteId, noteContent, activeProjectId)" in app_source
        assert (
            "saveMaterial(selectedMaterialId, materialContent, activeProjectId)"
            in app_source
        )
        assert "saveNote(selectedNoteId, noteLabel" not in app_source
        assert "saveMaterial(selectedMaterialId, materialLabel" not in app_source

    def test_editor_supports_document_type_without_shared_refactor(
        self, editor_source: str
    ) -> None:
        assert "DOCUMENT_TYPE_LABELS" in editor_source
        assert "selectedDocumentId" in editor_source
        assert "documentType = DEFAULT_DOCUMENT_TYPE" in editor_source
        assert "documentError" in editor_source
        assert "isDirty" in editor_source
        assert "resolveActiveDocumentType(documentType)" in editor_source
        assert "selectedSceneId" not in editor_source
        assert "sceneError" not in editor_source
        assert "hasUnsavedChanges" not in editor_source
        assert "shared editor" not in editor_source.lower()

    def test_app_uses_active_document_type_without_metadata_editing_ui(
        self, app_source: str
    ) -> None:
        assert "selectedDocumentType" in app_source
        assert "activeDocumentType" in app_source
        assert "documentType={activeEditorDocument.type}" in app_source
        assert "documentError={activeEditorDocument.error}" in app_source
        assert "isDirty={activeEditorDocument.isDirty}" in app_source
        assert "hasUnsavedChanges={activeEditorDocument.isDirty}" not in app_source
        assert "fetchNoteMetadata" not in app_source
        assert "saveNoteMetadata" not in app_source
        assert "fetchMaterialMetadata" not in app_source
        assert "saveMaterialMetadata" not in app_source

    def test_project_context_is_not_used_for_notes_materials(
        self, project_context_source: str
    ) -> None:
        assert "fetchNote" not in project_context_source
        assert "fetchMaterial" not in project_context_source
        assert "saveNote" not in project_context_source
        assert "saveMaterial" not in project_context_source


class TestSharedDocumentControllerSource:
    def test_shared_document_controller_module_exists(
        self, shared_document_controller_source: str, app_source: str
    ) -> None:
        assert "from './sharedDocumentController.js'" in app_source
        assert "export const DOCUMENT_TYPES" in shared_document_controller_source
        assert "export const DEFAULT_DOCUMENT_TYPE" in shared_document_controller_source

    def test_supported_document_types_are_exact(
        self, shared_document_controller_source: str
    ) -> None:
        for expected in ("SCENE: 'scene'", "NOTE: 'note'", "MATERIAL: 'material'"):
            assert expected in shared_document_controller_source

        assert "DOCUMENT_TYPE_VALUES = Object.freeze(Object.values(DOCUMENT_TYPES))" in (
            shared_document_controller_source
        )
        assert "export function isSupportedDocumentType" in shared_document_controller_source
        assert "export function resolveActiveDocumentType" in shared_document_controller_source

    def test_helper_extracts_content_without_metadata(
        self, shared_document_controller_source: str
    ) -> None:
        assert "export function getDocumentResponseContent" in shared_document_controller_source
        assert "return response?.content ?? ''" in shared_document_controller_source
        assert "metadata" not in shared_document_controller_source

    def test_helper_builds_document_descriptors(
        self, shared_document_controller_source: str
    ) -> None:
        assert "export function createDocumentDescriptor" in shared_document_controller_source
        for field in (
            "type: resolveActiveDocumentType(type)",
            "id: id ?? ''",
            "content: content ?? ''",
            "isDirty: Boolean(isDirty)",
            "isLoading: Boolean(isLoading)",
            "isSaving: Boolean(isSaving)",
            "error: error ?? ''",
            "saveStatus: saveStatus ?? ''",
            "onChange",
            "onSave",
        ):
            assert field in shared_document_controller_source

    def test_helper_controls_save_eligibility_and_unsaved_state(
        self, shared_document_controller_source: str
    ) -> None:
        assert "export function hasUnsavedDocumentEdits" in shared_document_controller_source
        assert "Boolean(scene || note || material)" in shared_document_controller_source
        assert "export function canSaveDocument" in shared_document_controller_source
        assert "Boolean(document?.id) && !document.isLoading && !document.isSaving" in (
            shared_document_controller_source
        )


class TestEditorDocumentNeutralContract:
    def test_editor_uses_document_neutral_props(self, editor_source: str) -> None:
        for expected_prop in (
            "selectedDocumentId",
            "documentError",
            "documentType = DEFAULT_DOCUMENT_TYPE",
            "isDirty",
        ):
            assert expected_prop in editor_source

        for scene_specific_prop in (
            "selectedSceneId",
            "sceneError",
            "hasUnsavedChanges",
        ):
            assert scene_specific_prop not in editor_source

    def test_app_passes_document_neutral_editor_props(self, app_source: str) -> None:
        for expected_prop in (
            "selectedDocumentId={activeEditorDocument.id}",
            "documentType={activeEditorDocument.type}",
            "documentError={activeEditorDocument.error}",
            "isDirty={activeEditorDocument.isDirty}",
        ):
            assert expected_prop in app_source

        editor_call = app_source.split("<Editor", 1)[1].split("/>", 1)[0]
        assert "selectedSceneId=" not in editor_call
        assert "sceneError=" not in editor_call
        assert "hasUnsavedChanges={activeEditorDocument.isDirty}" not in app_source

    def test_editor_labels_are_document_type_aware(self, editor_source: str) -> None:
        for document_type_key in (
            "[DOCUMENT_TYPES.SCENE]",
            "[DOCUMENT_TYPES.NOTE]",
            "[DOCUMENT_TYPES.MATERIAL]",
        ):
            assert document_type_key in editor_source

        assert "resolveActiveDocumentType(documentType)" in editor_source
        assert "DOCUMENT_TYPE_LABELS[resolvedDocumentType]" in editor_source
        assert "'aria-label': labels.surfaceAria" in editor_source
        assert "`No ${resolvedDocumentType} selected`" in editor_source

    def test_editor_save_status_and_loading_are_generic(
        self, editor_source: str
    ) -> None:
        assert "if (isLoading)" in editor_source
        assert "if (isSaving)" in editor_source
        assert "if (isDirty)" in editor_source
        assert "save-status${isDirty ? ' is-unsaved' : ''}" in editor_source
        assert "disabled={saveDisabled}" in editor_source
        assert "{isSaving ? 'Saving...' : 'Save'}" in editor_source

    def test_editor_preserves_exact_body_content_path(
        self, editor_source: str
    ) -> None:
        assert "content: textToHtml(content)" in editor_source
        assert "currentEditor.getText({ blockSeparator: '\\n\\n' })" in editor_source
        assert "editor.commands.setContent(textToHtml(content), { emitUpdate: false })" in (
            editor_source
        )
        assert "<EditorContent editor={editor} />" in editor_source

        for forbidden_body_injection in (
            "metadata",
            "title:",
            "summary",
            "documentTitle",
        ):
            assert forbidden_body_injection not in editor_source


class TestSharedDocumentStateContract:
    """PHASE7-IMPL-006-T002 source contract before shared editor refactor."""

    DOCUMENT_TYPES = ("scene", "note", "material")

    @staticmethod
    def _callback_body(source: str, callback_name: str) -> str:
        pattern = (
            rf"const {callback_name}\s*=\s*useCallback"
            rf"\((?:async\s*)?\([^)]*\)\s*=>\s*\{{(?P<body>.*?)\n\s*\}},\s*\["
        )
        match = re.search(pattern, source, re.DOTALL)
        assert match is not None, f"Expected useCallback body for {callback_name}"
        return match.group("body")

    def test_active_document_type_contract_covers_all_document_types(
        self, app_source: str
    ) -> None:
        assert "selectedDocumentType" in app_source
        assert "setSelectedDocumentType" in app_source

        expected_setters = {
            "scene": "setSelectedDocumentType(DOCUMENT_TYPES.SCENE)",
            "note": "setSelectedDocumentType(DOCUMENT_TYPES.NOTE)",
            "material": "setSelectedDocumentType(DOCUMENT_TYPES.MATERIAL)",
        }
        for document_type, setter in expected_setters.items():
            assert setter in app_source, (
                f"{document_type} selection must set active document type"
            )

        assert "const activeDocumentType = resolveActiveDocumentType(selectedDocumentType)" in (
            app_source
        )
        assert "activeDocumentType={activeDocumentType || DEFAULT_DOCUMENT_TYPE}" in app_source

    def test_editor_receives_generic_selected_document_ids(
        self, app_source: str, editor_source: str
    ) -> None:
        assert "selectedDocumentId" in editor_source
        assert "selectedSceneId" not in editor_source
        assert "selectedNoteId" not in editor_source
        assert "selectedMaterialId" not in editor_source

        assert "selectedDocumentId={activeEditorDocument.id}" in app_source
        assert "id: selectedSceneId" in app_source
        assert "id: selectedNoteId" in app_source
        assert "id: selectedMaterialId" in app_source

    def test_editor_body_content_comes_from_document_body_state(
        self, app_source: str
    ) -> None:
        assert "content={activeEditorDocument.content}" in app_source
        assert "content: sceneContent" in app_source
        assert "content: noteContent" in app_source
        assert "content: materialContent" in app_source

        assert "const loadedContent = getDocumentResponseContent(data)" in app_source
        assert "setSceneContent(loadedContent)" in app_source
        assert "setNoteContent(loadedContent)" in app_source
        assert "setMaterialContent(loadedContent)" in app_source
        assert "setSceneContent(data.metadata" not in app_source
        assert "setNoteContent(data.metadata" not in app_source
        assert "setMaterialContent(data.metadata" not in app_source

    def test_save_handlers_use_document_ids_and_body_content_only(
        self, app_source: str, api_source: str
    ) -> None:
        expected_app_calls = (
            "saveScene(selectedSceneId, sceneContent, activeProjectId)",
            "saveNote(selectedNoteId, noteContent, activeProjectId)",
            "saveMaterial(selectedMaterialId, materialContent, activeProjectId)",
        )
        for call in expected_app_calls:
            assert call in app_source

        forbidden_title_calls = (
            "saveScene(selectedSceneId, sceneLabel",
            "saveNote(selectedNoteId, noteLabel",
            "saveMaterial(selectedMaterialId, materialLabel",
            "saveNote(selectedNoteId, note.title",
            "saveMaterial(selectedMaterialId, material.title",
        )
        for call in forbidden_title_calls:
            assert call not in app_source

        expected_payloads = (
            "client.put(`/projects/${projectId}/scenes/${sceneId}`, { content })",
            "client.put(`/projects/${projectId}/notes/${noteId}`, { content })",
            "client.put(`/projects/${projectId}/materials/${materialId}`, { content })",
        )
        for payload in expected_payloads:
            assert payload in api_source

    def test_dirty_state_contract_spans_scene_note_and_material(
        self, app_source: str
    ) -> None:
        expected_dirty_checks = (
            "const isDirty = selectedSceneId !== '' && sceneContent !== lastSavedContent",
            "selectedNoteId !== '' && noteContent !== lastSavedNoteContent",
            "selectedMaterialId !== '' && materialContent !== lastSavedMaterialContent",
            "const hasUnsavedDocumentChanges = hasUnsavedDocumentEdits({",
        )
        for check in expected_dirty_checks:
            assert check in app_source

        for handler_name, setter in (
            ("handleSceneContentChange", "setSceneContent(nextContent)"),
            ("handleNoteContentChange", "setNoteContent(nextContent)"),
            ("handleMaterialContentChange", "setMaterialContent(nextContent)"),
        ):
            body = self._callback_body(app_source, handler_name)
            assert setter in body
            assert "Unsaved changes" in body

        for save_handler, last_saved_setter in (
            ("handleSave", "setLastSavedContent(sceneContent)"),
            ("handleSaveNote", "setLastSavedNoteContent(noteContent)"),
            ("handleSaveMaterial", "setLastSavedMaterialContent(materialContent)"),
        ):
            body = self._callback_body(app_source, save_handler)
            assert last_saved_setter in body
            assert "set" in body and "SaveStatus('Saved')" in body

    def test_dirty_state_blocks_document_and_project_switches(
        self, app_source: str
    ) -> None:
        for callback_name, message in (
            ("handleSelectScene", "UNSAVED_CHANGES_MESSAGE"),
            ("handleSelectNote", "UNSAVED_NOTE_SWITCH_MESSAGE"),
            ("handleSelectMaterial", "UNSAVED_MATERIAL_SWITCH_MESSAGE"),
            ("handleSelectProject", "UNSAVED_PROJECT_SWITCH_MESSAGE"),
            ("handleCreateProject", "UNSAVED_PROJECT_CREATE_MESSAGE"),
        ):
            body = self._callback_body(app_source, callback_name)
            assert "hasUnsavedDocumentChanges" in body
            if callback_name in {"handleSelectProject", "handleCreateProject"}:
                assert message in body
            else:
                assert "getDocumentSwitchMessage" in body
                assert "DOCUMENT_SWITCH_MESSAGES" in body
            assert "window.confirm" in body

    def test_loading_error_and_save_status_contract_is_document_typed(
        self, app_source: str, editor_source: str
    ) -> None:
        assert "DOCUMENT_TYPE_LABELS" in editor_source
        for document_type_key in (
            "[DOCUMENT_TYPES.SCENE]",
            "[DOCUMENT_TYPES.NOTE]",
            "[DOCUMENT_TYPES.MATERIAL]",
        ):
            assert document_type_key in editor_source

        for expected_prop in (
            "isLoading={activeEditorDocument.isLoading}",
            "isSaving={activeEditorDocument.isSaving}",
            "saveStatus={activeEditorDocument.saveStatus}",
            "documentError={activeEditorDocument.error}",
            "isLoading: isLoadingScene",
            "isLoading: isLoadingNote",
            "isLoading: isLoadingMaterial",
            "isSaving",
            "isSaving: isSavingNote",
            "isSaving: isSavingMaterial",
            "saveStatus",
            "saveStatus: noteSaveStatus",
            "saveStatus: materialSaveStatus",
            "error: sceneError",
            "error: noteError",
            "error: materialError",
        ):
            assert expected_prop in app_source

        for callback_name, loading_setter, error_setter in (
            ("handleSelectScene", "setIsLoadingScene(true)", "setSceneError('')"),
            ("handleSelectNote", "setIsLoadingNote(true)", "setNoteError('')"),
            ("handleSelectMaterial", "setIsLoadingMaterial(true)", "setMaterialError('')"),
        ):
            body = self._callback_body(app_source, callback_name)
            assert loading_setter in body
            assert error_setter in body
            assert "finally" in body

    def test_keyboard_save_dispatches_by_active_document_type_and_save_guards(
        self, app_source: str
    ) -> None:
        assert "function handleKeyDown(event)" in app_source
        assert "event.key.toLowerCase() === 's'" in app_source
        assert "activeDocumentType === DOCUMENT_TYPES.NOTE" in app_source
        assert "handleSaveNote()" in app_source
        assert "activeDocumentType === DOCUMENT_TYPES.MATERIAL" in app_source
        assert "handleSaveMaterial()" in app_source
        assert "handleSave();" in app_source

        for callback_name, selected_id, saving_flag in (
            ("handleSave", "selectedSceneId", "isSaving"),
            ("handleSaveNote", "selectedNoteId", "isSavingNote"),
            ("handleSaveMaterial", "selectedMaterialId", "isSavingMaterial"),
        ):
            body = self._callback_body(app_source, callback_name)
            assert f"if (!{selected_id} || {saving_flag})" in body
            assert "return;" in body

    def test_project_switch_resets_active_document_state_and_body_content(
        self, app_source: str
    ) -> None:
        assert "useEffect(() => {" in app_source
        assert "}, [activeProjectId]);" in app_source

        for reset in (
            "setSelectedSceneId('')",
            "setSelectedDocumentType('')",
            "setSelectedNoteId('')",
            "setSelectedMaterialId('')",
            "setSceneContent('')",
            "setLastSavedContent('')",
            "setNoteContent('')",
            "setLastSavedNoteContent('')",
            "setMaterialContent('')",
            "setLastSavedMaterialContent('')",
            "setNoteError('')",
            "setMaterialError('')",
        ):
            assert reset in app_source

    def test_project_nav_selection_parity_for_scene_note_and_material(
        self, app_source: str, project_nav_source: str
    ) -> None:
        assert "activeDocumentType = DEFAULT_DOCUMENT_TYPE" in project_nav_source
        assert "activeDocumentId = ''" in project_nav_source
        assert "activeDocumentType={activeDocumentType || DEFAULT_DOCUMENT_TYPE}" in app_source
        assert "activeDocumentId={activeDocument.id}" in app_source

        expected_active_checks = (
            "isActiveDocument(activeDocumentType, activeDocumentId, DOCUMENT_TYPES.SCENE, sceneId)",
            "isActiveDocument(activeDocumentType, activeDocumentId, DOCUMENT_TYPES.NOTE, noteId)",
            "isActiveDocument(activeDocumentType, activeDocumentId, DOCUMENT_TYPES.MATERIAL, materialId)",
        )
        for check in expected_active_checks:
            assert check in project_nav_source

        expected_id_callbacks = (
            "onSelectScene(sceneId)",
            "onSelectNote?.(noteId)",
            "onSelectMaterial?.(materialId)",
        )
        for callback in expected_id_callbacks:
            assert callback in project_nav_source

        forbidden_label_callbacks = (
            "onSelectScene(sceneLabel)",
            "onSelectNote?.(noteLabel)",
            "onSelectMaterial?.(materialLabel)",
        )
        for callback in forbidden_label_callbacks:
            assert callback not in project_nav_source

        for empty_state in ("No scenes yet.", "No notes yet.", "No materials yet."):
            assert empty_state in project_nav_source

    def test_project_nav_label_fallback_parity_for_document_groups(
        self, project_nav_source: str
    ) -> None:
        for helper_name in (
            "getSceneOptionLabel",
            "getNoteOptionLabel",
            "getMaterialOptionLabel",
        ):
            assert f"function {helper_name}" in project_nav_source

        assert "return sceneOption.label || sceneOption.sceneId" in project_nav_source
        assert "return noteOption.label || noteOption.title || noteOption.noteId" in project_nav_source
        assert (
            "return materialOption.label || materialOption.title || materialOption.materialId"
            in project_nav_source
        )
        assert "const title = rawTitle || sceneId || ''" in project_nav_source
        assert "const title = rawTitle || noteId" in project_nav_source
        assert "const title = rawTitle || materialId" in project_nav_source

    def test_project_nav_app_call_uses_generic_active_document_props(
        self, app_source: str
    ) -> None:
        project_nav_call = app_source.split("<ProjectNav", 1)[1].split("/>", 1)[0]
        assert "activeDocumentType={activeDocumentType || DEFAULT_DOCUMENT_TYPE}" in (
            project_nav_call
        )
        assert "activeDocumentId={activeDocument.id}" in project_nav_call
        assert "selectedSceneId=" not in project_nav_call
        assert "selectedNoteId=" not in project_nav_call
        assert "selectedMaterialId=" not in project_nav_call


class TestSharedEditorRegressionCoverage:
    """PHASE7-IMPL-006-T006 regression guard for the shared editor path."""

    @staticmethod
    def _callback_body(source: str, callback_name: str) -> str:
        pattern = (
            rf"const {callback_name}\s*=\s*useCallback"
            rf"\((?:async\s*)?\([^)]*\)\s*=>\s*\{{(?P<body>.*?)\n\s*\}},\s*\["
        )
        match = re.search(pattern, source, re.DOTALL)
        assert match is not None, f"Expected useCallback body for {callback_name}"
        return match.group("body")

    def test_shared_controller_contract_remains_complete(
        self, shared_document_controller_source: str
    ) -> None:
        expected_exports = (
            "export const DOCUMENT_TYPES",
            "export const DOCUMENT_TYPE_VALUES",
            "export const DEFAULT_DOCUMENT_TYPE",
            "export function isSupportedDocumentType",
            "export function resolveActiveDocumentType",
            "export function getDocumentResponseContent",
            "export function hasUnsavedDocumentEdits",
            "export function getDocumentSwitchMessage",
            "export function createDocumentDescriptor",
            "export function getActiveDocumentDescriptor",
            "export function canSaveDocument",
        )
        for expected_export in expected_exports:
            assert expected_export in shared_document_controller_source

        for document_type in ("SCENE: 'scene'", "NOTE: 'note'", "MATERIAL: 'material'"):
            assert document_type in shared_document_controller_source
        assert "isSupportedDocumentType(documentType) ? documentType : DEFAULT_DOCUMENT_TYPE" in (
            shared_document_controller_source
        )
        assert "return response?.content ?? ''" in shared_document_controller_source
        assert "descriptors[resolvedType] ?? descriptors[DEFAULT_DOCUMENT_TYPE]" in (
            shared_document_controller_source
        )

    def test_exact_body_load_paths_cover_scene_note_and_material(
        self, app_source: str
    ) -> None:
        expected_loads = (
            ("handleSelectScene", "fetchScene(sceneId, activeProjectId)", "setSceneContent(loadedContent)"),
            ("handleSelectNote", "fetchNote(noteId, activeProjectId)", "setNoteContent(loadedContent)"),
            (
                "handleSelectMaterial",
                "fetchMaterial(materialId, activeProjectId)",
                "setMaterialContent(loadedContent)",
            ),
        )
        for callback_name, fetch_call, content_setter in expected_loads:
            body = self._callback_body(app_source, callback_name)
            assert fetch_call in body
            assert "const loadedContent = getDocumentResponseContent(data)" in body
            assert content_setter in body
            assert ".metadata" not in body

    def test_exact_body_save_paths_cover_scene_note_and_material(
        self, app_source: str
    ) -> None:
        expected_saves = (
            ("handleSave", "saveScene(selectedSceneId, sceneContent, activeProjectId)"),
            ("handleSaveNote", "saveNote(selectedNoteId, noteContent, activeProjectId)"),
            (
                "handleSaveMaterial",
                "saveMaterial(selectedMaterialId, materialContent, activeProjectId)",
            ),
        )
        for callback_name, save_call in expected_saves:
            body = self._callback_body(app_source, callback_name)
            assert save_call in body
            assert "metadata" not in body
            assert "Label" not in body
            assert ".title" not in body

        for metadata_helper in (
            "fetchNoteMetadata",
            "saveNoteMetadata",
            "fetchMaterialMetadata",
            "saveMaterialMetadata",
        ):
            assert metadata_helper not in app_source

    def test_dirty_state_load_save_and_switch_baselines_are_preserved(
        self, app_source: str
    ) -> None:
        for dirty_check in (
            "sceneContent !== lastSavedContent",
            "noteContent !== lastSavedNoteContent",
            "materialContent !== lastSavedMaterialContent",
            "const hasUnsavedDocumentChanges = hasUnsavedDocumentEdits({",
        ):
            assert dirty_check in app_source

        expected_baselines = (
            ("handleSelectScene", "setLastSavedContent(loadedContent)"),
            ("handleSelectNote", "setLastSavedNoteContent(loadedContent)"),
            ("handleSelectMaterial", "setLastSavedMaterialContent(loadedContent)"),
            ("handleSave", "setLastSavedContent(sceneContent)"),
            ("handleSaveNote", "setLastSavedNoteContent(noteContent)"),
            ("handleSaveMaterial", "setLastSavedMaterialContent(materialContent)"),
        )
        for callback_name, baseline_update in expected_baselines:
            body = self._callback_body(app_source, callback_name)
            assert baseline_update in body

    def test_keyboard_save_dispatch_and_save_guards_are_document_type_aware(
        self, app_source: str
    ) -> None:
        assert "function handleKeyDown(event)" in app_source
        assert "event.preventDefault()" in app_source
        assert "activeDocumentType === DOCUMENT_TYPES.NOTE" in app_source
        assert "activeDocumentType === DOCUMENT_TYPES.MATERIAL" in app_source
        assert "handleSaveNote()" in app_source
        assert "handleSaveMaterial()" in app_source
        assert "handleSave();" in app_source

        for callback_name, guard in (
            ("handleSave", "if (!selectedSceneId || isSaving)"),
            ("handleSaveNote", "if (!selectedNoteId || isSavingNote)"),
            ("handleSaveMaterial", "if (!selectedMaterialId || isSavingMaterial)"),
        ):
            body = self._callback_body(app_source, callback_name)
            assert guard in body
            assert "return;" in body

    def test_project_and_document_switch_guards_remain_in_place(
        self, app_source: str
    ) -> None:
        for callback_name in (
            "handleSelectProject",
            "handleCreateProject",
            "handleSelectScene",
            "handleSelectNote",
            "handleSelectMaterial",
        ):
            body = self._callback_body(app_source, callback_name)
            assert "hasUnsavedDocumentChanges" in body
            assert "window.confirm" in body

        for switch_message in (
            "Discard unsaved changes and load another scene?",
            "Discard unsaved changes and load another note?",
            "Discard unsaved changes and load another material?",
            "Discard unsaved document changes and switch projects?",
        ):
            assert switch_message in app_source

    def test_project_switch_clears_stale_document_selection_and_bodies(
        self, app_source: str
    ) -> None:
        reset_block = app_source.split("async function loadInitialData()", 1)[0]
        for reset_call in (
            "setSelectedSceneId('')",
            "setSelectedDocumentType('')",
            "setSelectedNoteId('')",
            "setSelectedMaterialId('')",
            "setSceneContent('')",
            "setLastSavedContent('')",
            "setNoteContent('')",
            "setLastSavedNoteContent('')",
            "setMaterialContent('')",
            "setLastSavedMaterialContent('')",
        ):
            assert reset_call in reset_block

    def test_editor_remains_document_neutral_and_body_only(
        self, editor_source: str
    ) -> None:
        for expected in (
            "selectedDocumentId",
            "documentError",
            "documentType = DEFAULT_DOCUMENT_TYPE",
            "resolveActiveDocumentType(documentType)",
            "EditorContent editor={editor}",
            "onChange(currentEditor.getText({ blockSeparator: '\\n\\n' }))",
        ):
            assert expected in editor_source

        for forbidden in (
            "selectedSceneId",
            "sceneError",
            "metadata",
            "summary",
        ):
            assert forbidden not in editor_source

    def test_project_nav_remains_type_and_id_parity_aligned(
        self, project_nav_source: str
    ) -> None:
        assert "activeDocumentType = DEFAULT_DOCUMENT_TYPE" in project_nav_source
        assert "activeDocumentId = ''" in project_nav_source
        assert "function isActiveDocument" in project_nav_source
        for active_check in (
            "isActiveDocument(activeDocumentType, activeDocumentId, DOCUMENT_TYPES.SCENE, sceneId)",
            "isActiveDocument(activeDocumentType, activeDocumentId, DOCUMENT_TYPES.NOTE, noteId)",
            "isActiveDocument(activeDocumentType, activeDocumentId, DOCUMENT_TYPES.MATERIAL, materialId)",
        ):
            assert active_check in project_nav_source

        for id_callback in (
            "onSelectScene(sceneId)",
            "onSelectNote?.(noteId)",
            "onSelectMaterial?.(materialId)",
        ):
            assert id_callback in project_nav_source

        for forbidden_ui in (
            "metadata editor",
            "edit metadata",
            "upload material",
            "import material",
            "create note",
        ):
            assert forbidden_ui not in project_nav_source.lower()

    def test_api_helper_route_shapes_remain_body_and_metadata_separated(
        self, api_source: str, app_source: str
    ) -> None:
        expected_body_helpers = (
            "client.get(`/projects/${projectId}/scenes/${sceneId}`)",
            "client.put(`/projects/${projectId}/scenes/${sceneId}`, { content })",
            "client.get(`/projects/${projectId}/notes/${noteId}`)",
            "client.put(`/projects/${projectId}/notes/${noteId}`, { content })",
            "client.get(`/projects/${projectId}/materials/${materialId}`)",
            "client.put(`/projects/${projectId}/materials/${materialId}`, { content })",
        )
        for helper_shape in expected_body_helpers:
            assert helper_shape in api_source

        expected_metadata_helpers = (
            "client.put(`/projects/${projectId}/notes/${noteId}/metadata`, { metadata })",
            "client.put(`/projects/${projectId}/materials/${materialId}/metadata`, { metadata })",
        )
        for helper_shape in expected_metadata_helpers:
            assert helper_shape in api_source
            assert helper_shape not in app_source

    @pytest.mark.parametrize(
        "source_path",
        [APP_JSX, PROJECT_NAV_JSX, EDITOR_JSX, API_JS, SHARED_DOCUMENT_CONTROLLER_JS],
    )
    def test_shared_editor_sources_exclude_unsafe_future_behavior(
        self, source_path: Path
    ) -> None:
        lower_source = read_source(source_path).lower()
        forbidden_terms = [
            "generated prose",
            "improve prose",
            "summarize note",
            "summarize material",
            "extraction",
            "semantic search",
            "ollama",
            "apply promotion",
            "canon mutation",
            "memory mutation",
            "storyform inference",
            "dramatica analysis",
            "training data",
            "jsonl",
            "dataset",
        ]
        for term in forbidden_terms:
            assert term not in lower_source, (
                f"{source_path.relative_to(REPO_ROOT)} should not contain {term!r}"
            )

        assert "rewrite scene" not in lower_source
        assert "rewrite note" not in lower_source
        assert "rewrite material" not in lower_source
