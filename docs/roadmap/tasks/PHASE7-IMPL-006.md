# PHASE7-IMPL-006

## ID

`PHASE7-IMPL-006`

## Title

Shared owner-authored document editor

## Goal

Consolidate and harden the current scene/note/material owner-authored editing flow into a shared editor pattern that preserves exact user-authored content, supports consistent selection/load/save/dirty-state behavior, and avoids generated prose, extraction, summaries, model calls, or memory/canon mutation.

## Why Now

`PHASE7-IMPL-004` completed chapter/scene metadata compatibility and `PHASE7-IMPL-005` completed notes/materials storage, routes, API helpers, and a minimal navigation/display shell. The frontend now supports scenes, notes, and materials, but the editing behavior is still an incremental shell with duplicated state and handlers. A shared editor pass should consolidate the pattern before broader workspace pages build on it.

## Inputs / Dependencies

- Required completed parent tasks:
  - `PHASE7-IMPL-004` - Chapter / Scene Metadata Compatibility Layer
  - `PHASE7-IMPL-005` - Notes / Materials Storage
- Roadmap authority:
  - `docs/roadmap/roadmap_index.yaml`
  - `docs/roadmap/implementation_status.md`
  - `docs/roadmap/task_backlog.md`
  - `docs/roadmap/project_workspace_implementation_decision_sweep.md`
- Source specs:
  - `docs/roadmap/user_authored_document_editor_workflow_spec.md`
  - `docs/roadmap/chapter_scene_data_model_spec.md`
  - `docs/roadmap/notes_materials_data_model_spec.md`
  - `docs/roadmap/notes_materials_page_spec.md`
- Inventory:
  - `docs/roadmap/inventory/PHASE7-IMPL-006.md`
- Enrichment JSON:
  - `docs/roadmap/enrichment/PHASE7-IMPL-006.enrichment.json`

## Scope

Include:

- Shared frontend owner-authored document editing contract for `scene`, `note`, and `material`.
- Consistent active document type and document ID handling.
- Consistent body content, last-saved baseline, dirty-state, loading-state, save-state, and error handling.
- Consistent body-only load/save behavior.
- Consistent active navigation selection behavior.
- Source-level regression coverage before and during refactor slices.

Exclude:

- Backend route or storage redesign unless a later child task identifies a narrow compatibility bug.
- Metadata editing UI unless a later child task explicitly scopes it.
- Full browser/manual validation; that remains under `PHASE7-IMPL-010`.
- Generated prose, summaries, extraction, semantic search, model/Ollama calls, OMI promotion, memory/canon mutation, Dramatica-specific analysis, training data, JSONL, dataset, model artifact, or runtime project fixture changes.

## Product / Safety Boundaries

- Editor body content is owner-authored or owner-provided.
- Saving editor body content must preserve exact content and must not be treated as an AI prose-generation request.
- AI output must never be inserted into scene, note, or material body content.
- Notes/materials and scenes are not training data by default.
- Future analysis/extraction must remain separate from editor body content and produce diagnostics or candidates only.

## Current Evidence Summary

- `frontend/src/App.jsx` currently owns separate scene, note, and material state groups plus a shared `selectedDocumentType`.
- `frontend/src/components/Editor.jsx` already accepts `documentType`, `selectedDocumentId`, and generic `documentError`, but shared controller logic is not extracted.
- `frontend/src/components/ProjectNav.jsx` renders scene, note, and material lists with ID-based selection and active highlighting.
- `frontend/src/api.js` exposes scene, note, and material body helpers; metadata helpers exist for notes/materials but are not used by the minimal shell.
- `tests/test_frontend_project_workspace_source.py` provides source-level guard coverage but not browser/runtime UI validation.

## Child Task Plan

1. `PHASE7-IMPL-006-T001` - Shared owner-authored document editor inventory and child-task plan. Status: complete after validation.
2. `PHASE7-IMPL-006-T002` - Shared document state contract and source-level tests.
3. `PHASE7-IMPL-006-T003` - Extract shared editor controller helpers.
4. `PHASE7-IMPL-006-T004` - Editor component prop cleanup and behavior parity.
5. `PHASE7-IMPL-006-T005` - Project navigation document selection parity.
6. `PHASE7-IMPL-006-T006` - Shared editor regression coverage.
7. `PHASE7-IMPL-006-T007` - Roadmap/status closeout.

## Child Task Details

### `PHASE7-IMPL-006-T002` - Shared document state contract and source-level tests

- Define the frontend state/handler contract for active document type, active document ID, content, dirty state, loading state, save status, and error handling.
- Add source-level tests for the contract.
- Avoid runtime refactor unless tiny and explicitly required by the T002 task.

### `PHASE7-IMPL-006-T003` - Extract shared editor controller helpers

- Reduce duplicated scene/note/material selection, load, save, and dirty-state logic.
- Keep behavior unchanged.
- Do not redesign UI.

### `PHASE7-IMPL-006-T004` - Editor component prop cleanup and behavior parity

- Make `Editor.jsx` document-type neutral.
- Preserve exact body editing for scenes, notes, and materials.
- Keep labels, statuses, disabled/loading states, empty-body messaging, and errors consistent.
- Do not add generated text.

### `PHASE7-IMPL-006-T005` - Project navigation document selection parity

- Make scene/note/material active selection and labels consistent.
- Preserve ID-based selection and title fallback.
- Do not add metadata editing UI.

### `PHASE7-IMPL-006-T006` - Shared editor regression coverage

- Add or strengthen source-level tests for dirty-state, keyboard save, project switch, active document type, body-only save, no metadata injection, and no model/extraction terms.
- Run backend route/helper tests as regression checks when scoped by the child task.

### `PHASE7-IMPL-006-T007` - Roadmap/status closeout

- Record completed child tasks.
- Mark the parent complete if all child tasks pass.
- Move active frontier to the next published Phase 7 task according to roadmap authority.

## Acceptance Criteria

- Scene, note, and material body editing share a documented frontend contract.
- Selection/load/save behavior uses document IDs, not display titles.
- Body saves preserve exact owner-authored content and do not inject metadata.
- Dirty-state, save status, loading state, and error handling are consistent across document types.
- Project switch behavior remains protected when owner-authored document content has unsaved changes.
- Existing scene behavior remains stable.
- Note/material minimal shell behavior remains stable.
- No generated prose, summaries, extraction, model/Ollama calls, OMI/canon/memory mutation, Dramatica analysis, training/JSONL/dataset work, or runtime project fixture changes are introduced.

## Validation Expectations

For `PHASE7-IMPL-006-T001`:

- `python3 scripts/check_enrichment.py`
- `python3 scripts/validate_roadmap.py`
- Scoped `git diff -- ...` if raw git is allowed by local hooks.

For later implementation children, use focused frontend source tests and the existing route/helper regression tests named by each child prompt. Browser/manual validation remains under `PHASE7-IMPL-010`.

## Current Status

`PHASE7-IMPL-006-T001` is the active child task. Runtime implementation has not started. The next recommended child task is `PHASE7-IMPL-006-T002` - Shared document state contract and source-level tests.
