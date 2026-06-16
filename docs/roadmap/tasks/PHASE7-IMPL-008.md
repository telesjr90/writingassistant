# PHASE7-IMPL-008

## ID

`PHASE7-IMPL-008`

## Title

OMI-guided project creation staged flow

## Goal

Add a staged, owner-controlled OMI-guided project creation flow that lets the owner collect setup inputs and review candidate/setup planning data before final project creation, without generated prose, model calls, hidden project writes, apply-promotion, or memory/canon mutation.

## Why Now

`PHASE7-IMPL-001`/`002`/`003` provided safe project creation, library, and switching. `PHASE7-IMPL-004`/`005`/`006`/`007` added chapter/scene metadata compatibility, notes/materials storage, the shared owner-authored editor, and the deterministic Project Overview shell. The workspace can now create, select, and open projects while keeping the OMI panel candidate-only. The next safe step is a staged OMI-guided creation flow that keeps setup data separate from durable project truth until the owner explicitly confirms.

## Inputs / Dependencies

- Required completed parent tasks:
  - `PHASE7-IMPL-001` - Project Creation and Safe Project Metadata Backend
  - `PHASE7-IMPL-002` - Project Selector / Library
  - `PHASE7-IMPL-003` - Frontend Project Switching / Remove Hard-Coded Project Assumptions
- Helpful completed parent tasks:
  - `PHASE7-IMPL-004` - Chapter / Scene Metadata Compatibility Layer
  - `PHASE7-IMPL-005` - Notes / Materials Storage
  - `PHASE7-IMPL-006` - Shared owner-authored document editor
  - `PHASE7-IMPL-007` - Project Overview shell
- Roadmap authority:
  - `docs/roadmap/roadmap_index.yaml`
  - `docs/roadmap/implementation_status.md`
  - `docs/roadmap/task_backlog.md`
  - `docs/roadmap/project_workspace_implementation_decision_sweep.md`
- Source specs:
  - `docs/roadmap/project_workspace_foundation_spec.md`
  - `docs/roadmap/project_creation_flow_spec.md`
  - `docs/roadmap/omi_guided_project_creation_spec.md`
  - `docs/roadmap/project_file_model.md`
  - `docs/roadmap/omi_mvp_schema_lifecycle.md`
  - `docs/roadmap/omi_storage_model.md`
  - `docs/roadmap/omi_ideas_candidates_page_spec.md`
- Inventory:
  - `docs/roadmap/inventory/PHASE7-IMPL-008.md`
- Enrichment JSON:
  - `docs/roadmap/enrichment/PHASE7-IMPL-008.enrichment.json`

## Scope

Include:

- A staged owner-controlled setup wizard that collects owner-authored inputs only.
- A final confirmation step that lists the exact `project_id`, exact `project.json` initialization fields, and which setup candidates (if any) become project-local OMI records.
- A reuse-friendly data contract for staged setup state, candidate/setup labels, final confirmation, no hidden writes, no model calls, and blank project compatibility.
- Reuse of existing `_safe_path_component`/`validate_project_id` patterns and existing project creation helpers for the confirmed finalize step.
- After confirmation, write deterministic `project.json` metadata, the existing hybrid core folder set, and (optionally) explicitly owner-selected project-local OMI records.
- Routing the owner to the Project Overview shell after the new project is created.
- Source-level regression coverage for staged setup contract, no hidden writes, no model call path, blank project compatibility, candidate labels, and cancel/project-switch cleanup.

Exclude:

- Generated prose, AI-written setup suggestions, AI-written premise copy, AI-written genre copy, AI-written sample openings, AI-written blurbs, AI-written summaries.
- Extraction, semantic search, Story Check auto-runs, model/Ollama calls, AI rewrite/continue/polish/improve controls.
- Apply-promotion behavior. OMI promotion records remain audit-only.
- Memory/canon mutation. `memory/*.json` files must not be created.
- Hidden project writes during wizard steps.
- Dramatica-specific analysis, NCP/Dramatica UI, IC/RS/CIPS/dynamics truth claims.
- Training data, JSONL records, dataset artifacts, `training/data/dataset_manifest.json` updates.
- Browser/manual validation (remains under `PHASE7-IMPL-010`).
- Permanent project delete or archive UI.
- Metadata editing UI, note/material create/import/upload UI, chapter/scene create/edit UI, applied memory/canon UI.
- Reuse of an unguarded model path. Any future model-assisted setup candidate path would need a separate approved task with input/output guards.

## Product / Safety Boundaries

- Staged setup must be owner-controlled. Owner input is the only source of setup data.
- Setup candidates are not canon. They must remain visibly labeled as candidates.
- Pending or rejected setup candidates must not initialize `project.json`, `bible.json`, `storyform.json`, scenes, chapters, notes, materials, or memory/canon.
- Final confirmation must be explicit and must list the exact initialization fields and any project-local OMI records that will be written.
- The finalize step must call existing blank project creation helpers and reuse the existing hybrid core folder set.
- Setup data that becomes a project-local OMI record after confirmation is still candidate-only. It must not be auto-promoted to memory/canon.
- Setup data must never call a model, run Story Check, run extraction, run semantic search, mutate OMI promotion records, or mutate memory/canon.
- The wizard must clear stale setup draft state on cancel, on project switch, on completion, and on app reload.
- The shared owner-authored scene/note/material editor must not be reached from the wizard.
- The Project Overview shell must remain read-only and must not write any setup or candidate state on display.
- The OMI panel must keep its existing no-prose/no-silent-promotion boundary copy.

## Current Evidence Summary

- `backend/project_manager.py` provides blank project creation (`create_project`), ID derivation/validation, collision handling, hybrid core folder creation, atomic JSON writes, and OMI idea/candidate/promotion helpers. Backend staged setup storage helpers were intentionally deferred.
- `backend/main.py` exposes project list/create and project-scoped OMI routes only. Backend staged setup routes were intentionally deferred, and there is no `POST /api/projects/from-omi` route.
- `frontend/src/App.jsx` holds active project state, loads project library and OMI summary, renders `ProjectNav`/`ProjectOverview`/`ProjectContext`/`OMIPanel`/`Editor`/`AnalysisSidebar`, routes to Overview after project creation, and integrates the frontend-transient `OmiGuidedProjectCreation` shell.
- `frontend/src/api.js` provides project list/create helpers plus scene/note/material/OMI helpers. No staged setup API helpers were added.
- `frontend/src/components/OmiGuidedProjectCreation.jsx` provides the owner-authored setup input, review, visible setup/candidate labels, cancel/reset behavior, and explicit final confirmation shell. It keeps staged setup state in frontend state and calls the existing create-project path only after final confirmation.
- `frontend/src/components/OMIPanel.jsx` renders owner raw idea form, candidate form, decision controls, promotion readiness, candidate details, and promotion records. It is project-local only.
- `frontend/src/components/ProjectNav.jsx` renders project library and blank project creation. Blank project creation remains compatible and unchanged by the staged shell.
- `frontend/src/components/ProjectOverview.jsx` is a standalone prop-driven overview shell using deterministic project metadata and counts.
- Existing tests now cover staged setup contract, backend storage/route deferment, frontend-transient shell behavior, final confirmation gating, blank project compatibility, no staged API/routes/helpers, no OMI writes during staged steps, no hidden writes before final confirmation, visible setup/candidate labels, App/editor/overview separation, and no-prose/model/extraction safety.

## Child Task Plan

1. `PHASE7-IMPL-008-T001` - OMI-guided project creation staged flow inventory and child-task plan. Status: complete.
2. `PHASE7-IMPL-008-T002` - Staged flow data contract and source-level tests. Status: complete.
3. `PHASE7-IMPL-008-T003` - Backend staged setup storage helpers. Status: complete; backend staged setup storage deferred by decision.
4. `PHASE7-IMPL-008-T004` - Backend staged setup routes and compatibility tests. Status: complete; backend staged setup routes deferred by decision.
5. `PHASE7-IMPL-008-T005` - Frontend API helpers and staged creation UI shell. Status: complete.
6. `PHASE7-IMPL-008-T006` - Staged flow regression coverage. Status: complete.
7. `PHASE7-IMPL-008-T007` - Roadmap/status closeout. Status: complete.

## Child Task Details

### `PHASE7-IMPL-008-T002` - Staged flow data contract and source-level tests

- Completed source-level contract coverage for staged setup state, owner-authored inputs, visible setup/candidate labels, final confirmation, no hidden writes, blank project compatibility, OMI compatibility, backend/helper compatibility, frontend integration surfaces, and safety/no-prose boundaries.
- Runtime implementation was not added in this child.

### `PHASE7-IMPL-008-T003` - Backend staged setup storage helpers

- Path A was selected. Backend staged setup storage helpers were deferred because frontend-transient staged setup state satisfies the contract and avoids hidden pre-confirmation backend writes.
- Existing project creation remains the final durable project creation path.
- No backend runtime code was changed.

### `PHASE7-IMPL-008-T004` - Backend staged setup routes and compatibility tests

- Backend staged setup routes were deferred following the T003 storage decision.
- Compatibility tests locked route absence, existing durable project creation, blank project compatibility, no hidden pre-confirmation writes, OMI route compatibility, and frontend-transient setup compatibility.
- No backend route/runtime code was changed.

### `PHASE7-IMPL-008-T005` - Frontend API helpers and staged creation UI shell

- Added `frontend/src/components/OmiGuidedProjectCreation.jsx` as a frontend-transient staged creation shell.
- Added minimal `App.jsx` integration while preserving blank project creation, Project Overview, editor behavior, backend routes, `api.js`, and OMI backend behavior.
- The shell collects owner-authored setup input, shows visible setup/candidate labels, supports review/cancel/reset, and calls the existing create-project path only after explicit final confirmation.
- No staged setup backend API helpers, backend storage, backend routes, OMI draft-step writes, model calls, extraction, apply-promotion, or memory/canon mutation were added.

### `PHASE7-IMPL-008-T006` - Staged flow regression coverage

- Added source-level regression coverage for local reset behavior, final confirmation gating, existing final create-project path, blank project compatibility, no staged backend API/helper/route dependency, no OMI writes during staged draft steps, no hidden writes before final confirmation, visible setup/candidate labels, owner-authored input only, App integration, Project Overview/editor separation, and safety/no-prose boundaries.
- Runtime fixes were not needed.

### `PHASE7-IMPL-008-T007` - Roadmap/status closeout

- Recorded completed child tasks.
- Marked the parent complete after closeout validation passed.
- Moved the active frontier to the next published Phase 7 task (`PHASE7-IMPL-009` - Memory / Canon shell (approved-only empty states)) according to roadmap authority.

## Acceptance Criteria

- A staged, owner-controlled OMI-guided creation wizard exists, or the existing blank project creation remains the only creation path with documented rationale.
- Setup inputs are owner-authored only.
- Setup candidates carry visible candidate/setup labels and are never silently promoted.
- Final confirmation is explicit; no project folder is written before confirmation.
- Finalized projects use the existing blank project creation path with the existing hybrid core folder set.
- Project-local OMI records created from setup are candidate-only and never auto-promoted.
- Blank project creation keeps working unchanged.
- Existing shared editor, Overview shell, scene/note/material routes, OMI routes, and project library remain stable.
- No generated prose, summaries, extraction, semantic search, Story Check auto-runs, model/Ollama calls, OMI promotion/apply-promotion, or memory/canon mutation are added.
- No Dramatica-specific analysis, training data, JSONL records, dataset artifacts, or browser/manual validation are added.
- No metadata editing UI, note/material create/import/upload UI, or applied memory/canon UI is added.

## Source-Level Contract Compatibility Notes

The completed closeout preserves the source-level contract phrases used by PHASE7-IMPL-008 regression tests:

- `project ID preview` remains a contract concept for deterministic preview without writes.
- `No staged setup helpers exist yet` remains true for backend runtime source; backend staged setup storage was deferred.
- `No staged-setup routes exist today` remains true for backend runtime source; backend staged setup routes were deferred.
- `A first implementation can keep the wizard in transient frontend state until final confirmation.` This is the delivered T005 approach.
- `staged setup helpers only if needed` and `Add deterministic staged setup helpers only if needed` remain the T003 decision boundary; helpers were not needed in this slice.
- `Add staged setup read/write/cancel/finalize routes only if needed.` remains the T004 decision boundary; routes were not needed in this slice.
- `Add minimal API helpers if staged setup routes exist.` remains the T005 API boundary; staged routes did not exist, so no staged API helpers were added.
- `staged creation wizard` remains the UI shell concept for the frontend-transient staged creation shell.
- `Routing the owner to the Project Overview shell` remains the post-create navigation expectation.
- `final confirmation required to create a project folder` remains the durable write boundary.

## Validation Expectations

For `PHASE7-IMPL-008-T001`:

- `python3 scripts/check_enrichment.py`
- `python3 scripts/validate_roadmap.py`
- Scoped `git diff -- ...` if raw git is allowed by local hooks; otherwise record the skip.

For later children, source-level frontend tests plus focused backend helper/route regressions named by each child prompt. Browser/manual validation remains under `PHASE7-IMPL-010`.

## Final Completion Summary

`PHASE7-IMPL-008` is complete as of the T007 closeout.

Final outcome:

- T001 created the inventory, task record, enrichment JSON, and initial status updates.
- T002 locked the staged flow data contract with source-level tests.
- T003 selected Path A and deferred backend staged setup storage helpers.
- T004 deferred backend staged setup routes and locked the existing project creation route/helper as the durable creation path.
- T005 added the frontend-transient `OmiGuidedProjectCreation` shell and minimal `App.jsx` integration.
- T006 added staged flow regression coverage.
- T007 closed out roadmap/status and moved the active frontier to `PHASE7-IMPL-009`.

Delivered behavior remains frontend-transient until final owner confirmation. Existing project creation remains the only durable project creation path. No staged backend storage, staged backend routes, or staged backend API helpers were introduced. No OMI records are created during staged draft steps. No hidden project writes occur before final confirmation. Candidate/setup labels remain visible. Blank project creation remains compatible. Browser/manual validation remains deferred to `PHASE7-IMPL-010` or another roadmap-authorized validation phase.

## Current Status

`PHASE7-IMPL-008` is complete. The active Phase 7 frontier is `PHASE7-IMPL-009` - Memory / Canon shell (approved-only empty states).
