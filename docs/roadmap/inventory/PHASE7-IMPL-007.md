# PHASE7-IMPL-007 Inventory

## Task Identity

- Task ID: `PHASE7-IMPL-007`
- Canonical title: Project Overview shell
- Type: runtime parent
- Status: `active_next` in `docs/roadmap/roadmap_index.yaml`
- Depends on: `PHASE7-IMPL-006`
- Primary predecessor: `PHASE7-IMPL-006` - Shared owner-authored document editor

Boundary concepts:

- project overview / workspace shell
- owner-authored prose storage
- no generated prose
- no model calls
- no extraction
- no memory/canon mutation
- local-first

Machine-readable roadmap tags should use the registered governance tags, especially `read_only_overview`, `empty_states_only`, `owner_authored_prose_storage`, `no_generated_prose`, `no_model_calls`, `no_memory_canon_mutation`, and `local_first`.

## Current Implementation Surfaces

### `frontend/src/App.jsx`

- Owns active project state through `activeProjectId`.
- Loads project library data with `listProjects()` and stores it in `projects`.
- Creates blank projects through `createProject(title)` and switches to the returned `project_id`.
- Loads scenes, notes, materials, bible, storyform, storyform context, and OMI summary when `activeProjectId` changes.
- Holds scene/note/material lists in frontend state, making cheap frontend counts possible without new runtime data sources.
- Uses shared document descriptors for the active scene, note, or material editor.
- Renders `ProjectNav`, `ProjectContext`, `OMIPanel`, `Editor`, and `AnalysisSidebar`.
- There is no dedicated Project Overview component or landing surface today.
- The current default visible workspace after project selection is still editor-centric; a future overview shell could be inserted in the main content area before or alongside the editor if the child task defines a safe active-workspace-page contract.
- Story Check remains manually invoked from the analysis sidebar for selected scenes and must not auto-run for overview rendering.

### `frontend/src/components/ProjectNav.jsx`

- Provides project library selection and blank project creation.
- Renders scene, note, and material sections.
- Normalizes scene records from legacy strings or metadata-shaped records.
- Normalizes note/material records and falls back from blank titles to IDs.
- Uses generic `activeDocumentType` plus `activeDocumentId` for active highlighting.
- Selection callbacks pass IDs, not display titles.
- There is no Overview nav item today.
- A later overview integration task can add an Overview navigation item if it preserves existing document selection behavior and does not trigger body reads, model calls, or project writes.

### `frontend/src/components/Editor.jsx`

- Is document-type neutral for scene/note/material body editing.
- Receives `selectedDocumentId`, `documentType`, `documentError`, `isDirty`, `content`, loading/saving flags, and save handlers.
- Should remain separate from the overview shell; overview should not inject metadata, titles, summaries, or generated text into the editor body.

### `frontend/src/api.js`

- Project helpers: `listProjects()`, `createProject(title)`.
- Scene helpers: `fetchScenes(projectId)`, `fetchScene(sceneId, projectId)`, `saveScene(sceneId, content, projectId)`.
- Note helpers: `fetchNotes(projectId)`, `fetchNote(noteId, projectId)`, `saveNote(noteId, content, projectId)`, plus metadata helpers.
- Material helpers: `fetchMaterials(projectId)`, `fetchMaterial(materialId, projectId)`, `saveMaterial(materialId, content, projectId)`, plus metadata helpers.
- OMI helpers include summary retrieval and candidate/idea/promotion routes.
- There is no dedicated overview API helper today.
- Project metadata is available indirectly through `listProjects()` records; a later child should decide whether this is enough or whether a narrow deterministic overview helper is needed.

### `backend/main.py`

- Available project routes:
  - `GET /api/projects`
  - `POST /api/projects`
- Available scene routes:
  - `GET /api/projects/{project_name}/scenes`
  - `GET /api/projects/{project_name}/scenes/{scene_id}`
  - `PUT /api/projects/{project_name}/scenes/{scene_id}`
- Available note/material routes:
  - list, body read/write, metadata read/write for notes and materials.
- Available OMI summary route:
  - `GET /api/projects/{project_name}/omi`
- There is no dedicated project overview route today.
- A later backend child should add or verify deterministic overview data only if existing project/list/metadata helpers are insufficient.

### `backend/project_manager.py`

- Provides safe project creation and project library scan helpers.
- `list_projects()` returns project metadata records with title, created/updated timestamps, schema version, creation method, status, warnings, and relative path where available.
- Provides scene body helpers plus scene metadata compatibility helpers.
- Provides chapter metadata helpers.
- Provides note/material body and metadata helpers, including mixed metadata-backed and body-only listing.
- Existing helpers can support cheap scene/note/material counts from list outputs without reading full body text.
- Chapter counts may require direct chapter metadata helper use or a future narrow helper; defer unless the next child proves it is needed.

### `tests/test_frontend_project_workspace_source.py`

- Provides source-level frontend coverage for project-scoped API calls, scene metadata display compatibility, note/material helpers, shared document state, Editor neutrality, ProjectNav parity, and safety/no-prose terms.
- There is no overview-shell source contract coverage today.
- `PHASE7-IMPL-007-T002` should add source-level tests for overview data contract, counts, safe empty states, navigation, and no hidden model/extraction calls.

## Existing Working Behavior From Prior Phases

- Project creation/listing/selection is implemented.
- Chapter/scene metadata compatibility is implemented while preserving legacy `scenes/{scene_id}.md` files.
- Notes/materials storage, routes, API helpers, and minimal navigation/display shell are implemented.
- The shared owner-authored editor supports scenes, notes, and materials with ID-based selection and exact body load/save.
- Source-level regression coverage exists for exact body load/save, dirty-state handling, keyboard save, project/document switching, Editor neutrality, ProjectNav parity, and no unsafe generation/extraction/model behavior.

## Overview Shell Opportunities

Safe first-version overview content can be built from deterministic local project data only:

- Project title, project ID, status, warnings, schema version, creation method, `created_at`, and `updated_at` from project library metadata.
- Scene count from existing scene list state or scene metadata/list helpers.
- Note count from existing note metadata/list state.
- Material count from existing material metadata/list state.
- Chapter count if chapter metadata helpers provide a cheap count; otherwise defer.
- OMI status/counts from the existing `getOMI()` summary already loaded by `App.jsx`.
- Approved memory/canon snapshot as an empty-state shell only until approved-memory implementation exists.
- Workspace navigation cards or buttons for Scenes, Notes, Materials, OMI, Project Context, and Approved Memory/Canon placeholder.
- Neutral empty states such as missing optional metadata, no scenes, no notes, no materials, or no approved memory/canon yet.

All overview content must be factual UI/status content from project metadata or existing local records. It must not be an AI story summary, premise, logline, navigation prose, generated next step, extraction result, or Dramatica analysis.

## Overview Shell Gaps and Risks

- The overview must not become an AI summary page.
- Counts must not require full body reads, extraction, Story Check, semantic search, or model calls.
- Missing or incomplete project metadata should produce safe empty states or warnings.
- Legacy projects may have incomplete `project.json` data or missing metadata folders.
- Chapter count may need helper support or may be deferred if no cheap path exists.
- OMI and memory/canon sections should remain status/empty-state shells and must not promote candidates or create memory files.
- Browser/manual validation is not part of this parent and remains deferred to `PHASE7-IMPL-010`.
- Overview integration must not break the shared editor's document selection, dirty-state guards, or body-only save behavior.
- Project switching must refresh overview data and avoid stale counts/status from the previous project.
- Overview rendering must not auto-run Story Check or any hidden model-backed analysis.

## Boundaries

PHASE7-IMPL-007 must not add:

- generated prose,
- AI-generated project summaries, loglines, premises, note summaries, or material summaries,
- rewriting, continuation, style imitation, polishing, or prose improvement,
- extraction or semantic search,
- model/Ollama calls,
- Story Check auto-runs,
- OMI/canon/memory mutation,
- metadata editing UI unless a later child explicitly allows it,
- Dramatica-specific analysis,
- training, JSONL, dataset, model artifact, or runtime project fixture changes,
- browser/manual validation.

## Recommended Next Child

`PHASE7-IMPL-007-T002` - Overview data contract and source-level tests.

Likely allowed files:

- `tests/test_frontend_project_workspace_source.py`
- documentation/status files only if a validator requires a docs-only adjustment

Likely scope:

- Define source-level expectations for project metadata display, scene/note/material counts, safe empty states, overview navigation, and no hidden model/extraction calls.
- Avoid runtime implementation unless a tiny source-test-support adjustment is explicitly required by the T002 task.
