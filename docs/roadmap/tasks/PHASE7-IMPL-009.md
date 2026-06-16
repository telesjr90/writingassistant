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

1. `PHASE7-IMPL-009-T001` - Memory / Canon shell inventory and child-task plan. Status: in progress.
2. `PHASE7-IMPL-009-T002` - Approved-memory shell data contract and source-level tests. Status: draft.
3. `PHASE7-IMPL-009-T003` - Memory / Canon shell component. Status: draft.
4. `PHASE7-IMPL-009-T004` - ProjectNav/App integration. Status: draft.
5. `PHASE7-IMPL-009-T005` - Approved-category empty-state coverage. Status: draft.
6. `PHASE7-IMPL-009-T006` - Memory / Canon shell regression coverage. Status: draft.
7. `PHASE7-IMPL-009-T007` - Roadmap/status closeout. Status: draft.

## Child Task Details

### `PHASE7-IMPL-009-T002` - Approved-memory shell data contract and source-level tests

- Lock category list, approved-only empty states, candidate exclusion, no apply-promotion, no memory/canon mutation, no extraction/model/summaries.
- Tests only unless tiny source comment fixes are needed.

### `PHASE7-IMPL-009-T003` - Memory / Canon shell component

- Add a read-only shell component with category cards/tabs and approved-only empty states.
- No backend route/API dependency unless already existing and read-only.
- No mutation.

### `PHASE7-IMPL-009-T004` - ProjectNav/App integration

- Add Memory / Canon shell as a workspace view.
- Preserve Project Overview/editor/OMI panel separation.
- No editor save path.
- No candidate promotion.

### `PHASE7-IMPL-009-T005` - Approved-category empty-state coverage

- Ensure characters, locations/settings, timeline, plot threads, continuity/consistency, open questions, relationships, organizations/groups, and objects/items have visible approved-only empty states.
- Keep copy safe and non-generative.

### `PHASE7-IMPL-009-T006` - Memory / Canon shell regression coverage

- Cover no candidate-as-canon, no apply-promotion, no mutation, no generated summaries/extraction/model calls, no editor contamination, and project-switch/selection safety.

### `PHASE7-IMPL-009-T007` - Roadmap/status closeout

- Close parent if all child tasks pass.
- Move active frontier according to roadmap authority.

## Acceptance Criteria

- Memory / Canon shell exists as a read-only workspace surface.
- Category structure covers characters, locations/settings, timeline, plot threads, continuity/consistency, open questions, relationships, organizations/groups, and objects/items.
- Empty states clearly state no approved records exist.
- OMI candidates and promotion records are not displayed as approved canon.
- No apply-promotion behavior is added.
- No memory/canon mutation is added.
- No generated prose, summaries, extraction, semantic search, Story Check auto-runs, model/Ollama calls, Dramatica analysis, training/JSONL/dataset changes, or browser/manual validation are added.
- Existing Project Overview, Editor, OMI panel, project switching, and staged creation behavior remain stable.

## Validation Expectations

For `PHASE7-IMPL-009-T001`:

- `python3 scripts/check_enrichment.py`
- `python3 scripts/validate_roadmap.py`
- Scoped `git diff -- ...` if raw git is allowed by local hooks; otherwise record the skip.

For later children, use source-level frontend tests and focused regressions named by each child prompt. Browser/manual validation remains under `PHASE7-IMPL-010`.

## Current Status

`PHASE7-IMPL-009-T001` is in progress. This task creates the task record, inventory, enrichment JSON, and status updates before runtime implementation begins. The next child is `PHASE7-IMPL-009-T002` - Approved-memory shell data contract and source-level tests.
