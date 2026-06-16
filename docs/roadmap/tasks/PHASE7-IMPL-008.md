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

- `backend/project_manager.py` provides blank project creation (`create_project`), ID derivation/validation, collision handling, hybrid core folder creation, atomic JSON writes, and OMI idea/candidate/promotion helpers. No staged setup helpers exist yet.
- `backend/main.py` exposes project list/create and project-scoped OMI routes only. There are no staged setup routes and no `POST /api/projects/from-omi` route.
- `frontend/src/App.jsx` holds active project state, loads project library and OMI summary, renders `ProjectNav`/`ProjectOverview`/`ProjectContext`/`OMIPanel`/`Editor`/`AnalysisSidebar`, and routes to Overview after project creation. There is no staged creation wizard.
- `frontend/src/api.js` provides project list/create helpers plus scene/note/material/OMI helpers. There are no staged setup helpers.
- `frontend/src/components/OMIPanel.jsx` renders owner raw idea form, candidate form, decision controls, promotion readiness, candidate details, and promotion records. It is project-local only.
- `frontend/src/components/ProjectNav.jsx` renders project library and blank project creation. There is no OMI-guided creation entry yet.
- `frontend/src/components/ProjectOverview.jsx` is a standalone prop-driven overview shell using deterministic project metadata and counts.
- Existing tests cover blank project creation helpers, project ID validation, collision handling, scene/note/material route compatibility, and OMI no-prose/no-silent-promotion behavior. Staged setup coverage does not exist.

## Child Task Plan

1. `PHASE7-IMPL-008-T001` - OMI-guided project creation staged flow inventory and child-task plan. Status: in progress (this task).
2. `PHASE7-IMPL-008-T002` - Staged flow data contract and source-level tests. Status: draft.
3. `PHASE7-IMPL-008-T003` - Backend staged setup storage helpers. Status: draft.
4. `PHASE7-IMPL-008-T004` - Backend staged setup routes and compatibility tests. Status: draft.
5. `PHASE7-IMPL-008-T005` - Frontend API helpers and staged creation UI shell. Status: draft.
6. `PHASE7-IMPL-008-T006` - Staged flow regression coverage. Status: draft.
7. `PHASE7-IMPL-008-T007` - Roadmap/status closeout. Status: draft.

## Child Task Details

### `PHASE7-IMPL-008-T002` - Staged flow data contract and source-level tests

- Define the staged setup state shape (raw idea, optional owner inputs, setup candidate entries with visible labels, selected initialization fields, status, final confirmation flag, timestamps, project ID preview).
- Define source-level expectations for no hidden project writes, no model calls, no OMI record creation before confirmation, blank project compatibility, candidate/setup labels, and cancel/project-switch cleanup.
- Avoid runtime implementation unless a tiny source-test-support change is explicitly required.

### `PHASE7-IMPL-008-T003` - Backend staged setup storage helpers

- Add deterministic staged setup helpers only if needed for the chosen implementation (transient frontend state vs. durable backend staged setup).
- Reuse `_safe_path_component`/`validate_project_id` patterns if any staged setup ID touches the filesystem.
- Keep setup drafts separate from durable project truth until finalize.
- No generated prose, no model calls, no apply-promotion, no memory/canon mutation.

### `PHASE7-IMPL-008-T004` - Backend staged setup routes and compatibility tests

- Add staged setup read/write/cancel/finalize routes only if needed.
- Enforce path safety, owner confirmation, no hidden durable writes, blank project creation compatibility.
- No apply-promotion, no memory/canon mutation, no model calls, no setup prose generation.

### `PHASE7-IMPL-008-T005` - Frontend API helpers and staged creation UI shell

- Add minimal API helpers if staged setup routes exist.
- Add the OMI-guided creation wizard entry point beside the blank project form.
- Add wizard steps for owner input, candidate/setup review, final confirmation.
- Keep candidate/setup labels visible at all times.
- No generated prose or model calls. No shared-editor entry from the wizard.

### `PHASE7-IMPL-008-T006` - Staged flow regression coverage

- Source-level and route tests for:
  - no hidden writes before final confirmation
  - final confirmation required to create a project folder
  - candidate/setup labels visible
  - cancel/project-switch cleanup
  - blank project creation compatibility preserved
  - no model/extraction/apply-promotion/memory mutation
  - no Story Check auto-runs

### `PHASE7-IMPL-008-T007` - Roadmap/status closeout

- Record completed child tasks.
- Mark the parent complete if all child tasks pass.
- Move the active frontier to the next published Phase 7 task (`PHASE7-IMPL-009` - Project Memory / Canon shell and approved-only empty states) according to roadmap authority.

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

## Validation Expectations

For `PHASE7-IMPL-008-T001`:

- `python3 scripts/check_enrichment.py`
- `python3 scripts/validate_roadmap.py`
- Scoped `git diff -- ...` if raw git is allowed by local hooks; otherwise record the skip.

For later children, source-level frontend tests plus focused backend helper/route regressions named by each child prompt. Browser/manual validation remains under `PHASE7-IMPL-010`.

## Final Completion Summary

`PHASE7-IMPL-008` is not yet complete. The active child task is `PHASE7-IMPL-008-T001` (this task).

## Current Status

`PHASE7-IMPL-008-T001` is in progress. The task record, inventory, and enrichment JSON for `PHASE7-IMPL-008` are now created. The next child task is `PHASE7-IMPL-008-T002` - Staged flow data contract and source-level tests.
