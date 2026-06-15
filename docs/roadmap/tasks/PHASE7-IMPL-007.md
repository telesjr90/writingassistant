# PHASE7-IMPL-007

## ID

`PHASE7-IMPL-007`

## Title

Project Overview shell

## Goal

Add a safe project overview landing shell that gives the writer project-local workspace status and navigation using existing deterministic project data, while preserving owner-authored content boundaries and avoiding generated prose, extraction, model calls, OMI/canon/memory mutation, or Dramatica analysis.

## Why Now

`PHASE7-IMPL-006` completed the shared owner-authored scene/note/material editor path. The workspace can now create/select projects, load document lists, edit owner-authored body content, and keep scene/note/material editor behavior consistent. The next safe step is a read-only overview shell that orients the owner after project selection without adding analysis, summaries, extraction, or hidden mutations.

## Inputs / Dependencies

- Required completed parent task:
  - `PHASE7-IMPL-006` - Shared owner-authored document editor
- Roadmap authority:
  - `docs/roadmap/roadmap_index.yaml`
  - `docs/roadmap/implementation_status.md`
  - `docs/roadmap/task_backlog.md`
  - `docs/roadmap/project_workspace_implementation_decision_sweep.md`
- Source specs:
  - `docs/roadmap/project_overview_page_spec.md`
  - `docs/roadmap/project_workspace_foundation_spec.md`
  - `docs/roadmap/project_file_model.md`
  - `docs/roadmap/chapter_scene_data_model_spec.md`
  - `docs/roadmap/notes_materials_data_model_spec.md`
  - `docs/roadmap/user_authored_document_editor_workflow_spec.md`
- Inventory:
  - `docs/roadmap/inventory/PHASE7-IMPL-007.md`
- Enrichment JSON:
  - `docs/roadmap/enrichment/PHASE7-IMPL-007.enrichment.json`

## Scope

Include:

- Safe project overview data contract for project title/ID/status, warnings, timestamps, and cheap counts.
- Frontend overview shell using deterministic project-local data already available or narrowly exposed by existing helpers.
- Safe empty states for absent scenes, notes, materials, OMI data, and approved memory/canon.
- Navigation affordances into existing workspace areas.
- Source-level regression coverage for no hidden model calls, extraction, summaries, metadata mutation, or Story Check auto-runs.

Exclude:

- AI-generated project summaries, note summaries, material summaries, loglines, premises, or navigation prose.
- Extraction, semantic search, model/Ollama calls, Story Check auto-runs, OMI promotion, memory/canon mutation, Dramatica-specific analysis, training data, JSONL, dataset artifacts, package changes, app servers, frontend builds, runtime project fixture writes, and browser/manual validation.
- Metadata editing UI unless a later child task explicitly scopes it.
- Note/material create/import/upload flows.
- Full approved memory/canon implementation.

## Product / Safety Boundaries

- Overview content must be factual UI/status content from project metadata or deterministic local records.
- Owner-authored project metadata may be displayed as stored.
- Scene, note, and material bodies must not be read for summary generation.
- Overview rendering must not create files, repair metadata, promote candidates, mutate memory/canon, run Story Check, or call models.
- Approved memory/canon sections are empty-state placeholders until later approved-memory implementation exists.

## Current Evidence Summary

- `frontend/src/App.jsx` loads active project library metadata, scenes, notes, materials, bible, storyform, storyform context, and OMI summary on project change.
- `frontend/src/components/ProjectNav.jsx` currently provides project and document navigation but has no Overview nav item.
- `frontend/src/components/Editor.jsx` is document-neutral for scene/note/material body editing and should remain separate from overview display.
- `frontend/src/api.js` has project list/create helpers plus scene/note/material body helpers and OMI summary helpers; it has no dedicated overview API helper.
- `backend/main.py` has project, scene, note/material, OMI, bible/storyform, and Story Check routes; it has no dedicated overview route.
- `backend/project_manager.py` has project metadata listing plus scene/chapter/note/material helper surfaces that can support cheap counts if a later child needs a narrow overview helper.
- `tests/test_frontend_project_workspace_source.py` has source-level guards for the shared editor and workspace safety boundaries but no overview shell contract yet.

## Child Task Plan

1. `PHASE7-IMPL-007-T001` - Project Overview shell inventory and child-task plan. Status: complete after validation.
2. `PHASE7-IMPL-007-T002` - Overview data contract and source-level tests.
3. `PHASE7-IMPL-007-T003` - Backend/project data helper compatibility, if needed.
4. `PHASE7-IMPL-007-T004` - Frontend overview shell component.
5. `PHASE7-IMPL-007-T005` - ProjectNav/App overview integration.
6. `PHASE7-IMPL-007-T006` - Overview regression coverage.
7. `PHASE7-IMPL-007-T007` - Roadmap/status closeout.

## Child Task Details

### `PHASE7-IMPL-007-T002` - Overview data contract and source-level tests

- Define source-level expectations for project title/ID/status, scene/note/material counts, safe empty states, overview navigation, and no hidden model/extraction calls.
- Avoid runtime implementation unless a tiny source-test-support change is explicitly required.

### `PHASE7-IMPL-007-T003` - Backend/project data helper compatibility, if needed

- Add or verify deterministic project overview data helpers only if existing project/list/metadata helpers are insufficient.
- Keep helpers read-only or metadata-only as scoped.
- Do not summarize bodies, run extraction, call models, or mutate memory/canon.

### `PHASE7-IMPL-007-T004` - Frontend overview shell component

- Add a minimal overview component using deterministic data.
- Show factual project metadata, cheap counts, warnings, empty states, and navigation only.
- Do not add generated summaries or analysis.

### `PHASE7-IMPL-007-T005` - ProjectNav/App overview integration

- Add Overview as a safe landing/nav option if needed.
- Preserve scene/note/material editor selection, dirty-state guards, and body-only save behavior.
- Avoid stale overview data after project switches.

### `PHASE7-IMPL-007-T006` - Overview regression coverage

- Add or strengthen source-level/frontend tests for counts, empty states, navigation, no metadata mutation, no Story Check auto-runs, no model/extraction terms, and project-switch freshness.
- Run backend/helper/route regressions only as scoped by the child prompt.

### `PHASE7-IMPL-007-T007` - Roadmap/status closeout

- Record completed child tasks.
- Mark the parent complete if all child tasks pass.
- Move active frontier to the next published Phase 7 task according to roadmap authority.

## Acceptance Criteria

- Project Overview shell has a documented data contract before runtime implementation.
- Overview displays only deterministic project-local metadata/status/counts/empty states.
- Overview navigation uses existing workspace routes/surfaces and does not trigger model-backed behavior.
- Scene, note, material, and shared editor behavior remain stable.
- Overview rendering does not read document bodies to generate summaries.
- No generated prose, summaries, extraction, semantic search, Story Check auto-runs, model/Ollama calls, OMI/canon/memory mutation, Dramatica analysis, training/JSONL/dataset work, browser/manual validation, package changes, app servers, or runtime project fixture changes are introduced.

## Validation Expectations

For `PHASE7-IMPL-007-T001`:

- `python3 scripts/check_enrichment.py`
- `python3 scripts/validate_roadmap.py`
- Scoped `git diff -- ...` if raw git is allowed by local hooks.

For later children, use source-level frontend tests and focused backend/helper/route regressions named by each child prompt. Browser/manual validation remains under `PHASE7-IMPL-010`.

## Current Status

`PHASE7-IMPL-007-T001` is the active child task. Runtime implementation has not started. The next recommended child task is `PHASE7-IMPL-007-T002` - Overview data contract and source-level tests.
