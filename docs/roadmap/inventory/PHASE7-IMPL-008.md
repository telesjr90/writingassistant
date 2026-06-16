# PHASE7-IMPL-008 Inventory

## Task Identity

- Task ID: `PHASE7-IMPL-008`
- Canonical title: `OMI-guided project creation staged flow`
- Type: runtime parent
- Status: `active_next` in `docs/roadmap/roadmap_index.yaml`
- Depends on: `PHASE7-IMPL-001`, `PHASE7-IMPL-002`, `PHASE7-IMPL-003`
- Primary predecessor: `PHASE7-IMPL-007` - Project Overview shell

Boundary concepts (registered governance tags, see `docs/roadmap/roadmap_governance.md`):

- `candidate_only`
- `no_auto_promotion`
- `no_model_calls`
- `no_generated_prose`
- `no_memory_canon_mutation`
- `local_first`

These match the existing `boundary_tags` already declared for `PHASE7-IMPL-008` in `docs/roadmap/roadmap_index.yaml`.

Additional concepts that should remain visible in prose but are not separate registered tags:

- Staged project creation flow.
- Owner-controlled setup before durable project files are written.
- Final owner confirmation required before any project folder is created.
- Setup-derived structured records remain candidates/setup data.
- Candidate/setup labels remain visible wherever OMI/setup records are referenced.
- No hidden project writes during wizard steps.
- Blank project creation must keep working unchanged.

## Current Implementation Surfaces

### `backend/project_manager.py`

- Blank project creation helpers (`_validate_project_title`, `derive_project_id`, `validate_project_id`, `resolve_project_id_with_collision`, `create_project`) already exist and create `project.json` plus the hybrid core folder set under `WORKSPACE_CORE_FOLDERS`.
- Project ID validation already rejects empty values, absolute paths, path traversal, `.`, `..`, Windows drive letters, reserved names, and unsafe characters via `_PROJECT_ID_PATTERN` and `RESERVED_PROJECT_IDS`.
- Atomic JSON write helper `_write_json_object` exists; it writes a temp file and replaces the destination, and is reused for `project.json`, OMI records, scene/chapter/note/material metadata, and OMI index.
- OMI idea/candidate/promotion lifecycle helpers exist (`create_omi_idea`, `create_omi_candidate`, `update_omi_idea_decision`, `update_omi_candidate_decision`, `create_omi_promotion_record`, `list_omi_ideas`, `list_omi_candidates`, `list_omi_promotions`, `get_omi_summary`) and operate only on existing project paths under `projects/{project_id}/omi/`.
- Promotion helpers create audit-only records (`status: ready_for_manual_application`) and do not apply candidates to durable truth.
- OMI helpers block prose-oriented destinations (`scene_prose`, `chapter`, `dialogue`, `rewrite`, `continuation`, `final_story_text`, and several path components) through `OMI_BLOCKED_DESTINATIONS` and `OMI_PROMOTION_BLOCKED_TARGETS`.
- Staged setup storage does NOT exist. There is no pre-project inbox, no `setup_id` concept, no staged `setup` object, no staged `setup_id` validation, and no `from-omi` finalize-style route contract.
- A first-implementation staged setup helper is expected to live alongside the existing blank project helpers and reuse the same ID validation and atomic write helpers.

### `backend/main.py`

- Routes for project list/create already exist:
  - `GET /api/projects`
  - `POST /api/projects` (blank project only via `ProjectCreate(title: str)`)
- All existing OMI routes are project-scoped and require an existing `project_name`:
  - `GET /api/projects/{project_name}/omi`
  - `POST /api/projects/{project_name}/omi/ideas`
  - `GET /api/projects/{project_name}/omi/ideas/{idea_id}`
  - `POST /api/projects/{project_name}/omi/candidates`
  - `GET /api/projects/{project_name}/omi/candidates/{candidate_id}`
  - `PATCH /api/projects/{project_name}/omi/ideas/{idea_id}/decision`
  - `PATCH /api/projects/{project_name}/omi/candidates/{candidate_id}/decision`
  - `GET /api/projects/{project_name}/omi/promotions`
  - `GET /api/projects/{project_name}/omi/promotions/{promotion_id}`
  - `POST /api/projects/{project_name}/omi/promotions`
- No staged-setup routes exist today. There is no `POST /api/omi/project-setups`, no `GET/PATCH /api/omi/project-setups/{setup_id}`, and no `POST /api/projects/from-omi` route.
- No existing route writes project files before final confirmation. The blank `POST /api/projects` writes `project.json` and core folders as part of its single, owner-confirmed request.
- A staged-creation backend child must keep blank project creation unchanged and add new routes only if the staged flow needs durable state. A first implementation can keep the wizard in transient frontend state until final confirmation.

### `frontend/src/App.jsx`

- Active project is held in `activeProjectId` and switched through `handleSelectProject` with unsaved-changes confirmation.
- Project creation is initiated through `handleCreateProject`, which calls `createProject(title)` and resets active workspace to Overview after creation succeeds.
- Project list state is loaded by `loadProjects()` via `listProjects()`.
- OMI summary is loaded into `omiData` and rendered into `OMIPanel` only after a project is selected.
- The OMI panel is rendered inside the editor workspace view, not inside the Overview workspace view.
- No staged OMI-guided creation UI exists. There is no wizard shell, no setup draft state, no candidate/setup review screen, and no final confirmation surface.
- A staged OMI-guided creation flow must coexist with the existing blank project creation without removing or rewriting it.

### `frontend/src/api.js`

- Existing helpers used by `App.jsx`:
  - `listProjects()`, `createProject(title)`
  - `getOMI(projectId)`, `createOMIIdea(projectId, payload)`, `createOMICandidate(projectId, payload)`, `createOMIPromotion(projectId, payload)`, plus decision update helpers
- All existing OMI helpers are project-scoped (`projectId` parameter required), so a staged pre-project wizard cannot reuse them as-is.
- Missing staged setup helpers:
  - No `createOMISetup(payload)` or equivalent.
  - No `getOMISetup(setupId)` or equivalent.
  - No `updateOMISetup(setupId, payload)` or equivalent.
  - No `createProjectFromOMISetup(payload)` or equivalent.
- If the staged flow is implemented transiently in frontend state only, no new helpers are required beyond what already exists; if it is implemented with a backend staged-setup route, new helpers must be added.

### `frontend/src/components/OMIPanel.jsx`

- Renders owner raw idea form, candidate form, candidate review (decision/destination), promotion readiness checklist, and selected candidate details.
- Exposes owner decision controls (`approve`, `reject`, `needs_revision`, `pending`) and a final-confirmation checkbox for promotion records.
- Promotion readiness blockers are visible per candidate (`owner approval`, `approval confirmation`, `allowed destination`, `provenance`, `structured content`, `safe target label/path`).
- Candidate labels are always visible (e.g. `Planning note`, `Project bible candidate`, `Storyform context candidate`, `Scene prompt context candidate`, `Template starter candidate`, plus `Pending`, `Approved`, `Rejected`, `Needs revision`, `Archived`).
- No-prose boundary copy is visible at the panel header.
- The current OMI panel is project-local: it relies on a selected project and operates on `omi/ideas/`, `omi/candidates/`, and `omi/promotions/` records under that project.
- The existing OMI panel can be reused for guided setup only if the staged setup is converted into project-local OMI records after final confirmation. A separate staged setup wizard component is preferred for the wizard surface to avoid mixing pre-project setup state with post-creation candidate review.

### `frontend/src/components/ProjectNav.jsx`

- Renders project library selector with `listProjects()` data, blank project creation form, and refresh button.
- Active project is selected via `onSelectProject`.
- Blank project creation form is the only existing creation surface. There is no OMI-guided creation button, no setup wizard entry, and no setup draft indicator.
- A staged OMI-guided creation surface can be added beside the blank project form without disturbing existing navigation.

### `frontend/src/components/ProjectOverview.jsx`

- Standalone prop-driven overview shell.
- Renders project title/ID/status/creation method, scene/note/material counts, OMI status, and an approved memory/canon empty-state line.
- Uses only deterministic local data passed via props. No internal fetches, no model calls, no body reads.
- After successful project creation, the app already routes the owner to Overview (via `setActiveWorkspaceView(WORKSPACE_VIEWS.OVERVIEW)` in `App.jsx`).
- The Overview shell does not need backend helper changes for `PHASE7-IMPL-008`; it already accepts the deterministic props required to show a new project.

### `frontend/src/components/ProjectContext.jsx`

- Bible/Storyform JSON editors and a read-only storyform prompt context view.
- Not directly relevant to a staged creation flow beyond reaffirming the no-prose/no-AI-rewrite boundary.
- It must not be mutated by staged setup.

### Existing tests

- `tests/test_project_manager.py` covers blank project creation helpers, project ID derivation/validation, collision handling, hybrid folder creation, atomic write semantics, and OMI helper lifecycle. Stage-setup behavior is not yet covered.
- `tests/test_scene_routes.py` covers scene routes only; no staged setup coverage exists.
- `tests/test_note_material_routes.py` covers note/material routes only; no staged setup coverage exists.
- `tests/test_frontend_project_workspace_source.py` covers frontend source-level contracts (API helpers, Editor neutrality, ProjectNav parity, Overview data contract). Source-level staged setup coverage does not exist.
- `tests/test_omi_boundaries.py` and `tests/test_omi_routes.py` cover OMI no-prose and route behavior; they do not cover any staged setup storage.
- Source-level staged setup regression tests must be added if `PHASE7-IMPL-008-T002` defines staged setup contract.

## Existing Working Behavior From Prior Phases

- Safe blank project creation, listing, and selection work end-to-end (`PHASE7-IMPL-001`/`002`/`003`).
- `project.json` and the hybrid core folder set (`chapters/`, `scenes/`, `scene_metadata/`, `notes/`, `note_metadata/`, `materials/`, `material_metadata/`) are created by blank project creation; OMI/memory/storyform folders are intentionally deferred.
- Chapter/scene metadata compatibility layer exists; `scenes/{scene_id}.md` compatibility is preserved.
- Notes/Materials storage, routes, API helpers, and minimal navigation/display shell are stable.
- Shared owner-authored scene/note/material editor is stable with ID-based selection, dirty state, project-switch protection, and exact body load/save.
- Deterministic Project Overview shell renders deterministic project metadata and counts.
- OMI raw idea and structured candidate planning records can be created/listed/loaded under existing projects.
- OMI owner decision and destination selection work without apply-promotion.
- OMI promotion gate can create audit-only records when readiness passes.
- OMI no-prose and no-silent-promotion tests cover blocked prose destinations, owner-decision gates, record-only promotion creation, path traversal, and UI boundary copy.
- Story Check continues to require an explicit `runStoryCheck` invocation; it does not auto-run on overview, project switch, or staged creation.

## Staged OMI-Guided Creation Opportunities

Safe staged-flow behavior that can be implemented later, while staying inside the existing boundary tags:

- Collect owner-authored setup inputs (working title, optional subtitle, description, language, tags, status, premise note, optional chapter or scene placeholder labels, optional owner notes about characters, locations, themes, plot ideas, research needs) before any durable project files are written.
- Keep all pre-confirmation setup data in a clearly labeled staged setup object. First implementation may use transient frontend state only; later implementations may add a staged setup route.
- Display visible setup candidate labels for every setup-derived structured field (e.g. `Setup candidate: project title`, `Setup candidate: genre tag`, `Setup candidate: premise note`, `Setup candidate: initial chapter placeholder`, `Setup candidate: initial scene placeholder`, `Setup candidate: character note`, `Setup candidate: location note`, `Setup candidate: research note`).
- Show a final review/confirmation screen that lists the exact metadata that will initialize `project.json` plus which setup candidates will become project-local OMI records (if any).
- Create the project only after explicit owner confirmation. No wizard step should write to `projects/{project_id}/` or create project-local OMI records.
- After confirmation, write only deterministic `project.json` metadata, the hybrid core folder set, and any explicitly owner-selected project-local OMI records.
- Pending or rejected setup candidates remain non-canon. They should not initialize `project.json`, `bible.json`, `storyform.json`, scenes, chapters, notes, materials, or memory/canon.
- Route the new project to the Project Overview shell after creation, matching existing behavior.
- Show safe setup empty states and validation errors using existing style.
- Reuse `_safe_path_component`/`validate_project_id` patterns for any staged-setup IDs that touch the filesystem.

All setup content must be owner-authored or deterministic metadata. The app must not call a model, generate setup prose, generate a premise blurb, generate a sample opening, generate genre copy, summarize owner input, run Story Check, run extraction, run semantic search, create apply-promotion, or mutate memory/canon.

## Staged Flow Gaps and Risks

- Staged setup storage does not yet exist; either transient frontend state (Option D from `docs/roadmap/omi_guided_project_creation_spec.md` §7) or a new staged setup route will need to be chosen.
- Final confirmation boundary must be explicit: a project folder must not be created before the owner confirms.
- Wizard steps must not write hidden durable project files or hidden OMI records. Only the confirmed finalize step may call existing project creation helpers.
- Setup candidates must remain visible as candidates; they must not be silently promoted to canon or to durable OMI status beyond what the owner approved for project-local OMI import.
- No apply-promotion behavior is added in this phase. Promotion records remain audit-only.
- No memory/canon mutation. The approved-only memory/canon pages continue to read no records until a later `PHASE7-IMPL-009` shell task and a future apply-promotion.
- No model calls, no Ollama calls, no Story Check auto-runs, no extraction, no semantic search, no AI-written setup suggestions.
- Project ID collision and path safety must reuse existing helper patterns; no new path-validation code should be invented for staged setup.
- Stale setup draft state must clear on cancel, on project switch, on completion, and on app reload. There must be no auto-resume of abandoned staged setup unless a later durable inbox task is explicitly scoped.
- Legacy blank project creation must keep working unchanged and remain the default entry path.
- The shared owner-authored editor must not be reached from the staged setup wizard.
- The Project Overview shell must remain read-only and must not write any setup or candidate state on display.
- Browser/manual validation remains deferred to `PHASE7-IMPL-010` or another roadmap-authorized validation phase; this task must not add it.
- Avoid broad rewrites of `OMIPanel.jsx`, `ProjectNav.jsx`, or the project creation form.

## Boundaries

PHASE7-IMPL-008 must NOT add:

- Generated prose, AI-written setup suggestions, AI-written premise copy, AI-written genre copy, or any AI-written text inserted into owner inputs.
- Project summaries, loglines, blurbs, premise drafts, or navigation prose generated by AI.
- Extraction, semantic search, model calls, Ollama calls, Story Check auto-runs, or any hidden analysis path.
- Apply-promotion behavior. OMI promotion records remain audit-only.
- Durable memory/canon mutation. `memory/*.json` files must not be created.
- Hidden project writes during wizard steps. Only the confirmed finalize step may create `projects/{project_id}/`.
- Dramatica-specific analysis, NCP/Dramatica UI, IC/RS/CIPS/dynamics truth claims, or storyform context mutation.
- Training data, JSONL records, dataset artifacts, or `training/data/dataset_manifest.json` updates.
- Browser/manual validation.
- Metadata editing UI, note/material create/import/upload UI, chapter/scene create/edit UI, or applied memory/canon UI.
- Permanent project delete or archive UI.

## Recommended Next Child

`PHASE7-IMPL-008-T002` - Staged flow data contract and source-level tests.

Likely allowed files for the next child:

- `docs/roadmap/tasks/PHASE7-IMPL-008.md` (status update if needed)
- `tests/test_frontend_project_workspace_source.py` (source-level contract tests)
- `backend/project_manager.py` and `tests/test_project_manager.py` only if tiny helper-test support changes are explicitly required by the T002 prompt.

Likely scope:

- Define the source-level staged setup data contract: setup state shape, candidate labels, final confirmation flag, no hidden writes, no model calls, blank project compatibility.
- Avoid runtime implementation unless explicitly scoped by the T002 prompt.
