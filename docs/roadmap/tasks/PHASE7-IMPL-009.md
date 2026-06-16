# PHASE7-IMPL-009

## ID

`PHASE7-IMPL-009`

## Title

Memory / Canon shell (approved-only empty states)

## Goal

Add a read-only Memory / Canon shell for approved-only project knowledge categories, showing safe empty states and clear candidate/canon boundaries without adding apply-promotion, approved-memory mutation, extraction, generated summaries, model calls, semantic search, or browser/manual validation.

## Why Now

`PHASE7-IMPL-008` completed the OMI-guided staged project creation flow. The workspace now supports project creation/selection, shared scene/note/material editing, deterministic Project Overview, OMI candidate review, and a frontend-transient setup shell. The next safe workspace slice is to expose the approved-memory/canon area as a shell with empty states before any apply-promotion or durable memory mutation exists.

## Inputs / Dependencies

- Required completed parent tasks:
  - `PHASE7-IMPL-007` - Project Overview shell
  - `PHASE7-IMPL-008` - OMI-guided project creation staged flow
- Roadmap authority:
  - `docs/roadmap/roadmap_index.yaml`
  - `docs/roadmap/implementation_status.md`
  - `docs/roadmap/task_backlog.md`
  - `docs/roadmap/phase_map.md`
- Primary specs:
  - `docs/roadmap/project_memory_canon_page_structure_spec.md`
  - `docs/roadmap/project_memory_canon_storage_model.md`
  - `docs/roadmap/approved_characters_page_spec.md`
  - `docs/roadmap/approved_locations_settings_page_spec.md`
  - `docs/roadmap/approved_timeline_page_spec.md`
  - `docs/roadmap/approved_plot_threads_page_spec.md`
  - `docs/roadmap/continuity_consistency_page_spec.md`
  - `docs/roadmap/approved_open_questions_page_spec.md`
  - `docs/roadmap/approved_relationships_page_spec.md`
  - `docs/roadmap/approved_organizations_groups_page_spec.md`
  - `docs/roadmap/approved_objects_items_page_spec.md`
  - `docs/roadmap/omi_storage_model.md`
  - `docs/roadmap/omi_story_knowledge_candidate_expansion.md`
- Inventory:
  - `docs/roadmap/inventory/PHASE7-IMPL-009.md`
- Enrichment JSON:
  - `docs/roadmap/enrichment/PHASE7-IMPL-009.enrichment.json`

## Scope

Include:

- Read-only Memory / Canon shell structure.
- Approved-only category cards or tabs for characters, locations/settings, timeline, plot threads, continuity/consistency, open questions, relationships, organizations/groups, and objects/items.
- Safe empty states when no approved records exist.
- Clear labels that OMI candidates, approved-but-not-applied candidates, and promotion records are not canon.
- Frontend workspace integration as a shell view in later children.
- Source-level tests for no candidate-as-canon, no apply-promotion, no memory/canon mutation, no extraction, no generated summaries, no model calls, no Story Check auto-runs, and no editor contamination.

Exclude:

- Apply-promotion.
- Promotion execution.
- Memory/canon mutation.
- Approved-truth mutation.
- Generated prose, AI-written story content, summaries, extraction, semantic search, Story Check auto-runs, Dramatica analysis, model calls, or Ollama calls.
- Training data, JSONL data, dataset artifacts, or browser/manual validation.
- Metadata editing UI, note/material create/import/upload UI, or category detail editing.

## Safety / Product Boundaries

- Approved memory/canon lists may show only future applied memory/canon records.
- OMI candidates are not canon.
- Approved OMI candidates are not canon until a future apply-promotion step creates applied memory records.
- Promotion records are audit records only.
- Missing `memory/` storage is a valid empty state.
- Opening the shell must not create `memory/*.json`.
- The shell must not infer, extract, generate, approve, promote, mutate, or summarize anything.
- The shell must remain separate from scene/note/material editor save behavior.

## Current Evidence Summary

- `frontend/src/App.jsx` currently has `overview` and `editor` workspace views. There is no Memory / Canon view yet.
- `frontend/src/components/ProjectNav.jsx` has an Overview workspace button and scene/note/material document navigation. There is no Memory / Canon nav entry yet.
- `frontend/src/components/ProjectOverview.jsx` displays a simple approved-memory/canon empty-state line, but it is not the dedicated Memory / Canon shell.
- `frontend/src/components/OMIPanel.jsx` manages raw ideas, candidates, owner decisions, readiness checks, and promotion audit records. These records remain candidate/audit-only and must not populate approved Memory / Canon lists.
- `frontend/src/components/OmiGuidedProjectCreation.jsx` keeps setup/candidate data frontend-transient and not approved truth.
- `frontend/src/components/Editor.jsx` and `frontend/src/sharedDocumentController.js` support scene, note, and material editing only. Memory / Canon must not become a document type or save path.
- `frontend/src/api.js` has no approved-memory helper. Initial empty-state shell can avoid API changes.
- `backend/project_manager.py` has project and OMI helpers, but no approved-memory/canon helpers, no apply-promotion helper, and no memory/canon mutation helper.
- `backend/main.py` has project, scene, note/material, Story Check, bible/storyform, and OMI routes, but no Memory / Canon routes and no apply-promotion route.

## Child Task Plan

1. `PHASE7-IMPL-009-T001` - Memory / Canon shell inventory and child-task plan. Status: complete.
2. `PHASE7-IMPL-009-T002` - Approved-memory shell data contract and source-level tests. Status: complete.
3. `PHASE7-IMPL-009-T003` - Memory / Canon shell component. Status: complete.
4. `PHASE7-IMPL-009-T004` - ProjectNav/App integration. Status: complete.
5. `PHASE7-IMPL-009-T005` - Approved-category empty-state coverage. Status: complete.
6. `PHASE7-IMPL-009-T006` - Memory / Canon shell regression coverage. Status: complete.
7. `PHASE7-IMPL-009-T007` - Roadmap/status closeout. Status: complete.

## Child Task Details

### `PHASE7-IMPL-009-T001` - Memory / Canon shell inventory and child-task plan

- Created the task record, inventory, enrichment JSON, and initial roadmap/status updates.
- Defined the conservative child task sequence for approved-only empty states.

### `PHASE7-IMPL-009-T002` - Approved-memory shell data contract and source-level tests

- Locked the approved-memory category list, approved-only empty states, candidate exclusion, no apply-promotion, no memory/canon mutation, and no extraction/model/summary behavior in source-level tests.

### `PHASE7-IMPL-009-T003` - Memory / Canon shell component

- Added standalone `MemoryCanonShell.jsx` as a read-only shell with category cards/tabs and approved-only empty states.
- No backend route/API dependency, no mutation, and no `memory/` file creation on page load.

### `PHASE7-IMPL-009-T004` - ProjectNav/App integration

- Added Memory / Canon as a separate `memory-canon` workspace view in `App.jsx` and `ProjectNav.jsx`.
- Preserved Project Overview/editor/OMI panel separation, editor save path isolation, and no candidate promotion.

### `PHASE7-IMPL-009-T005` - Approved-category empty-state coverage

- Ensured characters, locations/settings, timeline, plot threads, continuity/consistency, open questions, relationships, organizations/groups, and objects/items have visible approved-only empty states.
- Kept copy safe and non-generative.

### `PHASE7-IMPL-009-T006` - Memory / Canon shell regression coverage

- Added regression coverage for project-switch separation, keyboard-save/editor gating, no OMI candidate/promotion flow into `approvedRecordsByCategory`, no API/backend helper drift, no mutation actions, approved-only empty-state preservation, App/Nav integration, OMI separation, Project Overview separation, OMI-guided setup non-canon behavior, and safety/no-prose boundaries.
- Runtime fixes were not needed.

### `PHASE7-IMPL-009-T007` - Roadmap/status closeout

- Recorded completed child tasks.
- Marked the parent complete after closeout validation passed.
- Moved the active frontier to the next published Phase 7 task (`PHASE7-IMPL-010` - Workspace Validation / Browser and Manual Smoke) according to roadmap authority.

## Acceptance Criteria

- Memory / Canon shell exists as a read-only workspace surface.
- Category structure covers characters, locations/settings, timeline, plot threads, continuity/consistency, open questions, relationships, organizations/groups, and objects/items.
- Empty states clearly state no approved records exist.
- OMI candidates and promotion records are not displayed as approved canon.
- No apply-promotion behavior is added.
- No memory/canon mutation is added.
- No generated prose, summaries, extraction, semantic search, Story Check auto-runs, model/Ollama calls, Dramatica analysis, training/JSONL/dataset changes, or browser/manual validation are added.
- Existing Project Overview, Editor, OMI panel, project switching, and staged creation behavior remain stable.

## Source-Level Contract Compatibility Notes

The completed closeout preserves the source-level contract phrases used by PHASE7-IMPL-009 regression tests:

- `Initial empty-state shell can avoid API changes` remains true; no frontend approved-memory API helper was added.
- `No API is required for the initial approved-only empty-state shell` remains true; the shell renders static category structure and safe empty states without approved-memory API calls.
- `No Memory / Canon routes` remains true for backend runtime source; no backend approved-memory routes were added.
- `No approved-memory helper exists` remains true for `frontend/src/api.js`.
- `Approved-memory read APIs unless a later contract proves they are needed` remains the deferred boundary for future read APIs.
- Memory / Canon is integrated as a separate `workspace view`, not a document type.
- `not become a document type` and `must not become a document type or save path` remain the editor/shared-document-controller boundary.
- `not the dedicated Memory / Canon shell` remains true for `ProjectOverview.jsx`; the dedicated shell is `MemoryCanonShell.jsx`.
- `preserve project overview/editor/omi panel separation` remains the App/Nav integration boundary.

## Validation Expectations

For `PHASE7-IMPL-009-T001`:

- `python3 scripts/check_enrichment.py`
- `python3 scripts/validate_roadmap.py`
- Scoped `git diff -- ...` if raw git is allowed by local hooks; otherwise record the skip.

For later children, use source-level frontend tests and focused regressions named by each child prompt. Browser/manual validation remains under `PHASE7-IMPL-010`.

## Final Completion Summary

`PHASE7-IMPL-009` is complete as of the T007 closeout.

Final outcome:

- T001 created the inventory, task record, enrichment JSON, and initial status updates.
- T002 locked the approved-memory shell data contract with source-level tests.
- T003 added standalone `MemoryCanonShell.jsx`.
- T004 integrated Memory / Canon as a separate `memory-canon` workspace view in App/ProjectNav.
- T005 hardened per-category approved-only empty states for all required categories.
- T006 added Memory / Canon shell regression coverage.
- T007 closed out roadmap/status and moved the active frontier to `PHASE7-IMPL-010`.

Delivered behavior remains read-only and approved-only. OMI candidates, approved-but-not-applied candidates, and promotion records are not displayed as approved canon. No backend approved-memory routes, backend approved-memory helpers, frontend approved-memory API helpers, apply-promotion, memory/canon mutation, generated prose, summaries, extraction, semantic search, Story Check auto-runs, model/Ollama calls, training/JSONL/dataset work, metadata editing UI, note/material create/import/upload UI, or browser/manual validation were added. Browser/manual validation remains deferred to `PHASE7-IMPL-010` or another roadmap-authorized validation phase.

## Current Status

`PHASE7-IMPL-009` is complete. The active Phase 7 frontier is `PHASE7-IMPL-010` - Workspace Validation / Browser and Manual Smoke.
