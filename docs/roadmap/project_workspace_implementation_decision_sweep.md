# WORKSPACE-026: Project Workspace Implementation Decision Sweep

Status: Documentation-only planning handoff. Runtime implementation is future work.

Date: 2026-06-10.

Product working name: Dramatica-Informed Writing Assistant.

Current priority: Pre-Dramatica Project Workspace Foundation.

## 1. Purpose

This decision sweep consolidates `WORKSPACE-001` through `WORKSPACE-025` into a practical implementation-readiness handoff for Phase 7 Project Workspace Foundation.

It identifies what is ready, what remains deferred, which decisions are already defaulted, which owner decisions remain, the recommended first runtime implementation sequence, and the single recommended next runtime task.

This is documentation only. It does not implement backend runtime code, frontend runtime code, tests, package changes, datasets, JSONL records, training data, model calls, project runtime files, OMI records, memory/canon files, extractors, semantic search, graph visualization, contradiction detection, Dramatica-specific logic, apply-promotion behavior, staging, commits, or pushes.

The app remains analysis-only. It may store, edit, save, reload, and organize owner-authored prose, notes, metadata, research, references, and materials, but the AI must never write, rewrite, continue, imitate, polish, improve, expand, or extend story prose.

Standard refusal message:

```text
I can analyze structure and ask diagnostic questions, but I cannot write or rewrite story prose.
```

## 2. Overall Readiness Decision

Phase 7 is ready to begin runtime implementation after owner acceptance of the current MVP exit disposition and this decision sweep. No new feature spec is required before the first implementation task.

The safest first runtime slice is backend project creation and safe project metadata. UI pages, project switching, chapter/scene metadata, notes/materials, OMI-guided setup, and memory/canon shells all depend on stable local project identity.

Recommended implementation order:

1. Create/select local projects safely.
2. Remove hard-coded frontend project assumptions.
3. Preserve current scene Markdown compatibility while adding metadata in a staged way.
4. Add notes/materials after project selection and scene compatibility are stable.
5. Share one owner-authored document editor pattern across scenes, notes, and materials.
6. Add Overview, OMI-guided setup, and memory/canon shells without hidden model calls, extraction, apply-promotion, or memory mutation.

## 3. WORKSPACE-001 Through WORKSPACE-025 Readiness

| Workspace ID | Spec file | Topic | Implementation readiness status | Blocking decisions, if any | Recommended first implementation phase or deferred phase |
| --- | --- | --- | --- | --- | --- |
| WORKSPACE-001 | `docs/roadmap/project_workspace_foundation_spec.md` | Project Workspace Foundation | Ready as umbrella target. | Owner accepts Phase 7 as next runtime track after MVP exit disposition. | Phase 7 umbrella. |
| WORKSPACE-002 | `docs/roadmap/project_creation_flow_spec.md` | Project Creation Flow | Ready for first runtime implementation. | None that block backend start. | `PHASE7-IMPL-001`. |
| WORKSPACE-003 | `docs/roadmap/project_selector_library_spec.md` | Project Selector / Library | Ready after project metadata backend exists. | Invalid-folder placement can default to warning section. | `PHASE7-IMPL-002`. |
| WORKSPACE-004 | `docs/roadmap/omi_guided_project_creation_spec.md` | OMI-Guided Project Creation | Ready as staged later flow. | Durable pre-project inbox deferred; staged wizard state is default. | `PHASE7-IMPL-008`. |
| WORKSPACE-005 | `docs/roadmap/chapter_scene_data_model_spec.md` | Chapter / Scene Data Model | Ready after creation/selection. | Metadata migration timing is slice-scoped. | `PHASE7-IMPL-004`. |
| WORKSPACE-006 | `docs/roadmap/notes_materials_data_model_spec.md` | Notes / Materials Data Model | Ready after project selection plumbing. | Attachments/import/extraction deferred. | `PHASE7-IMPL-005`. |
| WORKSPACE-007 | `docs/roadmap/user_authored_document_editor_workflow_spec.md` | Shared User-Authored Document Editor Workflow | Ready after scene/note/material route surfaces exist. | Per-project draft preservation deferred. | `PHASE7-IMPL-006`. |
| WORKSPACE-008 | `docs/roadmap/project_overview_page_spec.md` | Project Overview Page | Ready as shell/lightweight page. | Approved-memory snapshot can be empty-state only. | `PHASE7-IMPL-007`. |
| WORKSPACE-009 | `docs/roadmap/chapters_scenes_page_spec.md` | Chapters / Scenes Page | Ready after metadata/editor work. | None beyond sequence. | `PHASE7-IMPL-004` and `PHASE7-IMPL-006`. |
| WORKSPACE-010 | `docs/roadmap/notes_materials_page_spec.md` | Notes / Materials Page | Ready after storage/routes/editor work. | Attachment/import scope deferred. | `PHASE7-IMPL-005` and `PHASE7-IMPL-006`. |
| WORKSPACE-011 | `docs/roadmap/project_memory_canon_page_structure_spec.md` | Project Memory / Canon Page Structure | Ready for shell/empty-state only before apply-promotion. | First depth defaults to shell/empty state. | `PHASE7-IMPL-009`. |
| WORKSPACE-012 | `docs/roadmap/omi_ideas_candidates_page_spec.md` | OMI Ideas / Candidates Page | Ready as page planning; current OMI MVP remains sufficient for first slice. | Typed candidates and apply-promotion deferred. | Later Phase 7 or Phase 8. |
| WORKSPACE-013 | `docs/roadmap/approved_characters_page_spec.md` | Approved Characters Page | Ready for approved-only empty/card state. | Needs memory storage/apply-promotion for real records. | Deferred after `PHASE7-IMPL-009`. |
| WORKSPACE-014 | `docs/roadmap/approved_locations_settings_page_spec.md` | Approved Locations / Settings Page | Ready for approved-only empty/card state. | Needs memory storage/apply-promotion for real records. | Deferred after `PHASE7-IMPL-009`. |
| WORKSPACE-015 | `docs/roadmap/approved_timeline_page_spec.md` | Approved Timeline Page | Ready for approved-only empty/card state. | Needs memory storage/apply-promotion for real records. | Deferred after `PHASE7-IMPL-009`. |
| WORKSPACE-016 | `docs/roadmap/approved_plot_threads_page_spec.md` | Approved Plot Threads Page | Ready for approved-only empty/card state. | Needs memory storage/apply-promotion for real records. | Deferred after `PHASE7-IMPL-009`. |
| WORKSPACE-017 | `docs/roadmap/continuity_consistency_page_spec.md` | Continuity / Consistency Page | Ready for approved-only empty/card state. | Detection and generated fixes deferred. | Deferred after `PHASE7-IMPL-009`. |
| WORKSPACE-018 | `docs/roadmap/approved_open_questions_page_spec.md` | Approved Open Questions Page | Ready for approved-only empty/card state. | Generated answers and extraction deferred. | Deferred after `PHASE7-IMPL-009`. |
| WORKSPACE-019 | `docs/roadmap/approved_relationships_page_spec.md` | Approved Relationships Page | Ready for approved-only empty/card state. | Graphing and Dramatica RS claims deferred. | Deferred after `PHASE7-IMPL-009`. |
| WORKSPACE-020 | `docs/roadmap/approved_organizations_groups_page_spec.md` | Approved Organizations / Groups Page | Ready for approved-only empty/card state. | Extraction/graphing and Dramatica claims deferred. | Deferred after `PHASE7-IMPL-009`. |
| WORKSPACE-021 | `docs/roadmap/approved_objects_items_page_spec.md` | Approved Objects / Items Page | Ready for approved-only empty/card state. | Inference, symbolic interpretation, and extraction deferred. | Deferred after `PHASE7-IMPL-009`. |
| WORKSPACE-022 | `docs/roadmap/approved_annotations_evidence_provenance_page_spec.md` | Approved Annotations / Evidence / Provenance Page | Ready for approved-only empty/card state. | Evidence extraction/indexing deferred. | Deferred after `PHASE7-IMPL-009`. |
| WORKSPACE-023 | `docs/roadmap/approved_contradictions_page_spec.md` | Approved Contradictions Page | Ready for approved-only empty/card state. | Detection and generated fixes deferred. | Deferred after `PHASE7-IMPL-009`. |
| WORKSPACE-024 | `docs/roadmap/approved_scene_event_causality_review_spec.md` | Approved Scene / Event / Causality Review | Ready for approved-only empty/card state. | Extraction, causal inference, summaries, visualization deferred. | Deferred after `PHASE7-IMPL-009`. |
| WORKSPACE-025 | `docs/roadmap/project_memory_canon_cross_linking_health_spec.md` | Project Memory / Canon Cross-Linking and Health | Ready as future read-only health planning. | `memory/index.json`, rebuild/repair, and real health checks deferred. | Deferred after memory/canon shell. |

## 4. Consolidated Implementation Defaults

### Project Creation

- Require an owner-editable title.
- Derive a filesystem-safe `project_id` from the title.
- Let the owner accept or edit the proposed `project_id`.
- Validate `project_id` server-side as one safe path component.
- Treat `project_id` as stable after creation, even if title changes later.
- Fail closed on collisions; the UI may propose suffixes, but the backend must never silently overwrite an existing project.
- Write metadata-only `project.json` as the durable identity source.
- Create a blank project path with safe minimal folders only.
- Keep OMI-guided setup separate/staged unless a later slice explicitly implements it.
- Do not create canon, memory, candidates, storyform, generated summaries, or generated prose during blank project creation.
- Create `bible.json`, `storyform.json`, and OMI folders lazily by default unless a runtime compatibility test in `PHASE7-IMPL-001` shows eager empty files are safer.

### Project Library

- Scan `projects/` first; do not depend on `projects/index.json`.
- Treat any future `projects/index.json` as rebuildable navigation metadata only.
- Valid projects require safe folder names and valid matching `project.json`.
- Show invalid, corrupt, unsafe, unreadable, duplicate, or missing-metadata folders in a warning section by default.
- Provide local search/filter/sort over metadata and cheap counts.
- Do not read full scene/note/material bodies during listing.
- Do not expose permanent delete in the first version.
- Keep archive/delete future-only until separately planned and owner-approved.

### Chapter / Scene Storage

- Preserve current `scenes/{scene_id}.md` compatibility.
- Store scene prose as owner-authored Markdown only.
- Add `chapters/{chapter_id}.json` and `scene_metadata/{scene_id}.json` through a planned compatibility/migration slice.
- Treat legacy scene Markdown without metadata as standalone compatible scenes.
- Use `chapter.scene_ids` as canonical first-version order and `scene_metadata.chapter_id` as a consistency aid.
- Do not rewrite scene prose during metadata creation, repair, move, reorder, or listing.
- Keep summaries prohibited unless they are owner-authored or owner-approved navigation aids; candidate summaries remain OMI candidates only.

### Notes / Materials Storage

- Store note bodies as Markdown/text in `notes/{note_id}.md`.
- Store material bodies as Markdown/text in `materials/{material_id}.md` for the first version.
- Store metadata separately in `note_metadata/{note_id}.json` and `material_metadata/{material_id}.json`.
- Include source, reference, license, provenance, and usage-warning fields for materials.
- Keep notes/materials as source material, not canon by default.
- Use local deterministic search/filter only.
- Do not run extraction, semantic search, web fetching, binary import, model calls, OMI promotion, memory mutation, training writes, or generated summaries during first save/search/list operations.

### Shared Editor

- Use one owner-authored document editor pattern for scenes, notes, and materials.
- Track selected project, selected document, body dirty state, metadata dirty state, save/reload status, last-saved baseline, and load errors.
- Require save/discard/cancel before document, page, or project switches when there are unsaved edits.
- Preserve owner text after save failures.
- Distinguish intentionally empty bodies from missing body files.
- Do not expose AI prose-generation controls.
- Do not block owner-authored saves as assistant prose-generation requests.
- Keep analysis/candidate panels separate from editor body content.

### Project Overview

- Open Project Overview after project creation and project selection.
- Display safe owner-authored project metadata from `project.json`.
- Show cheap counts, recent-document metadata, OMI status, approved memory/canon snapshot or empty state, and non-destructive health warnings.
- Do not read full bodies just to generate summaries.
- Do not generate project summaries, premise text, loglines, diagnostics, or setup prose.
- Do not trigger model calls, extraction, OMI record creation, memory/canon mutation, or project writes on page load.

### OMI

- Keep existing OMI MVP behavior as the foundation.
- Treat raw ideas as owner input and candidates as candidate-only records.
- Keep promotion records audit-only until apply-promotion exists.
- Keep future typed story-knowledge candidates separate from the first implementation slice unless a later task explicitly selects them.
- Do not implement apply-promotion in Phase 7 foundation slices.
- Do not call a model for OMI-guided setup unless a later guarded model path is explicitly implemented and tested.

### Approved Memory / Canon

- Show shell/empty-state/category cards before memory files exist.
- Label pages as approved-memory-only and show candidate/audit links separately.
- Defer approved category pages with real records until memory storage and apply-promotion exist.
- Treat `memory/index.json` and cross-link health as planned unless a later task implements a read-only health stub.
- Do not create `memory/` files on page load.
- Do not treat approved candidates or promotion records as durable canon.

## 5. Remaining Owner Decisions

### A. Decisions That Block Starting Phase 7 Implementation

1. Accept/document the current public-domain `projects/example` fixture state, or request a fixture replacement before Phase 7 begins.
2. Accept the previous localhost smoke-test sandbox limitation as documented, or request a socket-enabled rerun before declaring the MVP foundation fully accepted.
3. Confirm `PHASE7-IMPL-001 - Project Creation and Safe Project Metadata Backend` as the first runtime implementation slice.
4. Decide whether to push local `main` before implementation begins. Recommended for repo hygiene because the branch is ahead of remote; not technically required for local implementation.

### B. Decisions That Can Be Deferred Until Later Slices

1. Whether Node engine metadata should be declared before or with the first frontend implementation slice.
2. Whether invalid project folders are shown in a warning section or recovery tab. Default: warning section first.
3. Whether blank projects create `bible.json` and `storyform.json` immediately or lazily. Default: lazy unless compatibility tests require eager empty files.
4. Whether OMI folders are lazy-created or initialized with blank project. Default: lazy-created on first OMI owner action.
5. Whether candidate extraction is manual-only first, automatic, scheduled, hybrid, or future-only. Default: future-only until workspace save/edit flows are stable.
6. First approved-memory implementation depth. Default: shell/empty state before real memory files and before apply-promotion.
7. Whether `memory/index.json` appears as a read-only health stub before real memory records exist. Default: defer.
8. Whether the first Project Library UI uses cards, table, or both.
9. Archive support timing. Default: future-only; permanent delete remains absent until separate owner-approved task.
10. Whether OMI-guided setup eventually uses transient wizard state, browser-local draft state, or durable pre-project inbox. Default: transient/staged wizard state first.

### C. Decisions Already Defaulted by Existing Specs

1. `project_id` remains separate from display title.
2. `project_id` remains stable after title rename.
3. Project creation uses title-derived, owner-editable, filesystem-safe IDs.
4. Collisions fail closed; backend never silently overwrites a project.
5. Project Library is scan-first and local.
6. First selector does not expose permanent delete.
7. Scene prose remains owner-authored Markdown in `scenes/{scene_id}.md`.
8. Chapter/scene metadata is added separately and must preserve existing scene Markdown compatibility.
9. Notes/materials are Markdown/text plus metadata in the first version.
10. Notes/materials are not approved canon or training data by default.
11. Shared editor saves are owner-authored content storage, not assistant requests.
12. OMI candidates are not canon.
13. Promotion records are audit-only until apply-promotion exists.
14. Approved memory/canon pages read applied memory/canon only; empty states are valid before apply-promotion.
15. Dramatica-specific implementation remains deferred.
16. Fine-tuning, JSONL creation, dataset manifest updates, extractor installs, semantic search, graph visualization, contradiction detection, and model calls are out of scope for Phase 7 foundation implementation unless a future task explicitly approves them.

## 6. Recommended Runtime Implementation Sequence

### PHASE7-IMPL-001 - Project Creation and Safe Project Metadata Backend

- Goal: add safe backend project creation and project metadata primitives.
- Why next: every later workspace page needs safe project identity before UI selection, switching, chapters/scenes, notes/materials, OMI-guided setup, or memory/canon shells can be reliable.
- Files likely touched: `backend/project_manager.py`, `backend/main.py`, focused backend tests under `tests/`, and possibly test helpers.
- Must not touch: frontend UI unless explicitly expanded, package/dependency files, training/dataset files, runtime fixture data outside safe temp tests, OMI records, memory/canon files, JSONL files, or `training/data/dataset_manifest.json`.
- Acceptance criteria: create project from title and optional owner metadata; validate safe `project_id`; reject collisions and unsafe values; write metadata-only `project.json`; fail closed without overwriting existing projects; preserve current routes; no model/Ollama calls; no generated prose; no OMI candidate/promotion creation; no memory/canon mutation.
- Tests/validation: backend unit/route tests for ID validation, creation, collision, unsafe values, metadata serialization, rollback/failure behavior, and no accidental mutation of existing project files.
- Rollback/safety notes: use temp/atomic write behavior where practical; cleanup only transaction-created empty files/folders; ambiguous cleanup fails into repair-needed state.
- Dependencies: `WORKSPACE-002` and existing safe path helper patterns.
- Deferred items: selector UI, hard-coded frontend project switching, OMI-guided setup, chapter/scene metadata migration, notes/materials, memory/canon.

### PHASE7-IMPL-002 - Project Library / Selector Backend and Frontend

- Goal: add scan-first project listing and simple selector/opening.
- Why next: once projects can exist, the owner needs to discover and open them.
- Files likely touched: `backend/project_manager.py`, `backend/main.py`, `frontend/src/api.js`, `frontend/src/App.jsx`, selector/library components, focused tests.
- Must not touch: deletion, archive mutation, extraction, memory/canon mutation, training data, package files, model paths.
- Acceptance criteria: list valid projects; return invalid/corrupt warnings; search/filter/sort locally over metadata; open selected project without reading full bodies; no delete; no model calls; no generated summaries.
- Tests/validation: backend listing tests and frontend build/manual selector checklist.
- Rollback/safety notes: listing is read-only; invalid folders are not auto-repaired.
- Dependencies: `PHASE7-IMPL-001`, `WORKSPACE-003`.
- Deferred items: archive/delete, recovery/import, `projects/index.json`.

### PHASE7-IMPL-003 - Remove Hardcoded Frontend PROJECT_ID and Support Project Switching

- Goal: replace hard-coded `PROJECT_ID = "example"` with selected-project state and safe switching.
- Why next: existing UI must become project-aware before workspace pages can operate on the selected project.
- Files likely touched: `frontend/src/api.js`, `frontend/src/App.jsx`, `frontend/src/components/ProjectNav.jsx`, `frontend/src/components/Editor.jsx`, `frontend/src/components/OMIPanel.jsx`, `frontend/src/components/ProjectContext.jsx`.
- Must not touch: apply-promotion, extraction, memory/canon mutation, model paths, package files.
- Acceptance criteria: selected project ID flows through API calls; switching prompts protect unsaved edits; project-specific state clears/reloads on switch; `example` remains openable.
- Tests/validation: frontend build and manual switching checklist.
- Rollback/safety notes: keep empty/selector state when no project is selected; do not auto-save or discard without owner confirmation.
- Dependencies: `PHASE7-IMPL-002`.
- Deferred items: per-project draft preservation.

### PHASE7-IMPL-004 - Chapter / Scene Metadata Compatibility Layer

- Goal: add chapter records and scene metadata while preserving `scenes/{scene_id}.md`.
- Why next: the workspace needs scene organization without risking owner-authored prose.
- Files likely touched: `backend/project_manager.py`, `backend/main.py`, `frontend/src/components/ProjectNav.jsx`, `frontend/src/components/Editor.jsx`, chapter/scene components, focused tests.
- Must not touch: scene body rewriting, generated summaries, model paths, extraction, OMI promotion, memory/canon mutation, training data.
- Acceptance criteria: existing scene Markdown remains compatible; legacy scenes list as standalone; chapter/scene metadata can be created/loaded/saved; reorder/move updates metadata only.
- Tests/validation: backend tests for legacy scenes, metadata validation, reorder/move consistency, missing body versus empty body; frontend build if UI changes.
- Rollback/safety notes: metadata repair does not rewrite prose; corrupt metadata blocks unsafe reorder/move.
- Dependencies: `PHASE7-IMPL-003`, `WORKSPACE-005`.
- Deferred items: generated navigation summaries, extraction provenance, advanced timeline/continuity links.

### PHASE7-IMPL-005 - Notes / Materials Storage and Routes

- Goal: add owner-authored notes and owner-provided materials storage/routes.
- Why next: notes/materials expand the workspace beyond scenes while reusing safe project identity.
- Files likely touched: `backend/project_manager.py`, `backend/main.py`, `frontend/src/api.js`, notes/materials components, focused tests.
- Must not touch: binary import, web fetching, external sync, extraction, semantic search, training data, memory/canon mutation, package files.
- Acceptance criteria: create/list/load/save note and material bodies/metadata; preserve source/reference/license/provenance fields; local deterministic search/filter if included; no extraction during save/search.
- Tests/validation: backend tests for save/load, metadata validation, missing body versus empty body, source/license warnings, path safety; frontend build if UI changes.
- Rollback/safety notes: save failure preserves owner content; warnings are non-destructive.
- Dependencies: `PHASE7-IMPL-003`, `WORKSPACE-006`.
- Deferred items: attachments, web import, OCR, semantic search.

### PHASE7-IMPL-006 - Shared Scene / Note / Material Editor UI

- Goal: implement one shared owner-authored editor pattern across scenes, notes, and materials.
- Why next: duplicated editor behavior would increase data-loss risk across document types.
- Files likely touched: `frontend/src/components/Editor.jsx`, new shared editor component/hooks, page components, `frontend/src/api.js`, focused UI tests if available.
- Must not touch: AI prose controls, model calls, extraction, memory/canon mutation, package files unless separately approved.
- Acceptance criteria: dirty state, save/reload, missing-vs-empty body behavior, unsaved switch protection, save failure preservation, and no AI prose controls across document types.
- Tests/validation: frontend build and manual browser editor checklist.
- Rollback/safety notes: existing scene editor safety should not regress.
- Dependencies: `PHASE7-IMPL-004`, `PHASE7-IMPL-005`, `WORKSPACE-007`.
- Deferred items: collaborative editing, per-project drafts, rich conflict merge UI.

### PHASE7-IMPL-007 - Project Overview Page Shell

- Goal: add safe landing page with metadata, navigation, cheap counts, OMI status, approved-memory empty state, and warnings.
- Why next: Overview provides orientation after creation/open without requiring memory/canon or extraction.
- Files likely touched: `frontend/src/App.jsx`, new Overview component, `frontend/src/api.js`, possibly read-only backend summary route.
- Must not touch: body-derived generated summaries, model calls, extraction, OMI creation, memory/canon mutation.
- Acceptance criteria: shows project metadata and empty states; uses cheap counts; labels candidate/canon status; no writes on load.
- Tests/validation: backend summary tests if route added; frontend build; manual overview checklist.
- Rollback/safety notes: overview is read-only except explicit navigation actions.
- Dependencies: `PHASE7-IMPL-002` or `PHASE7-IMPL-003`, `WORKSPACE-008`.
- Deferred items: health repair, generated summaries, real approved-memory counts before memory exists.

### PHASE7-IMPL-008 - OMI-Guided Project Creation Staged Flow

- Goal: add staged owner-controlled OMI-guided setup after blank creation and selector are stable.
- Why next: guided setup depends on safe project creation and selected-project handoff.
- Files likely touched: project creation frontend, OMI components, `backend/main.py`, `backend/project_manager.py`, focused tests.
- Must not touch: model calls unless separately approved, generated prose, apply-promotion, memory/canon mutation.
- Acceptance criteria: staged setup captures owner input; candidate labels remain visible; project is created only after final confirmation; selected fields initialize `project.json`; OMI records remain candidate/audit-only after project creation.
- Tests/validation: guided creation flow tests and no-prose/no-silent-promotion tests.
- Rollback/safety notes: leaving wizard before confirmation creates no project; partial handoff fails closed.
- Dependencies: `PHASE7-IMPL-001` through `PHASE7-IMPL-003`, `WORKSPACE-004`.
- Deferred items: durable pre-project inbox and model-assisted candidate generation.

### PHASE7-IMPL-009 - Project Memory / Canon Shell and Approved-Only Empty States

- Goal: add memory/canon navigation shells, category cards, labels, and empty states.
- Why next: visible candidate/canon separation helps prepare later Core work without implementing memory storage.
- Files likely touched: frontend page/navigation components, possibly read-only backend stubs.
- Must not touch: `memory/` runtime files, apply-promotion, extraction, contradiction detection, semantic search, graph visualization, model calls.
- Acceptance criteria: approved-only empty states; candidate and promotion-record labels; links to OMI where relevant; no `memory/` creation on load.
- Tests/validation: frontend build and manual label/empty-state checklist.
- Rollback/safety notes: page load is read-only and empty-state tolerant.
- Dependencies: `PHASE7-IMPL-007`, `WORKSPACE-011`, `WORKSPACE-013` through `WORKSPACE-025`.
- Deferred items: real memory storage, `memory/index.json`, apply-promotion, category records, health repair.

### PHASE7-IMPL-010 - Implementation Readiness Test Matrix / Manual Browser Checklist

- Goal: define and run the Phase 7 validation matrix after the first implementation slices.
- Why next: the workspace foundation needs explicit acceptance before extraction, memory/canon, or Dramatica work expands.
- Files likely touched: docs, tests, possibly manual report files.
- Must not touch: training data, JSONL, live model paths, package files unless explicitly part of runtime implementation validation.
- Acceptance criteria: project creation, selection, switching, save/reload, dirty-state, overview, OMI status, memory/canon shell, candidate/canon labels, no AI prose controls, no model calls during storage/search/navigation, backend tests, frontend build, and browser checklist pass or have documented owner exceptions.
- Tests/validation: backend tests, frontend build, manual browser checklist; no live Ollama unless separately requested.
- Rollback/safety notes: validation should not mutate durable project truth except through explicit owner/test temp paths.
- Dependencies: preceding implementation slices.
- Deferred items: extractor evaluation, apply-promotion tests, Dramatica-specific tests.

## 7. Recommended Immediate Next Runtime Task

Recommended next task:

`PHASE7-IMPL-001 - Project Creation and Safe Project Metadata Backend`.

This comes before UI pages because every later workspace surface needs a safe project identity, collision policy, durable `project.json`, and create/open contract. Implementing UI pages first would preserve the hard-coded `example` assumption and make later switching riskier.

Minimal runtime behavior:

- Add backend project creation.
- Validate owner-provided or title-derived `project_id`.
- Write metadata-only `project.json`.
- Create only safe minimal folders.
- Reject collisions and unsafe path values.
- Preserve current scene/context/OMI routes for existing projects.

Likely touched:

- `backend/project_manager.py`
- `backend/main.py`
- Focused tests under `tests/`

Tests to add/update:

- Project creation success.
- Title-derived ID behavior.
- Owner-edited ID behavior.
- Unsafe ID rejection.
- Collision rejection.
- Metadata serialization.
- Failure/rollback behavior.
- Existing project route compatibility.
- No model/Ollama path called.
- No OMI/memory/canon/training mutation.

Must remain untouched:

- Frontend UI unless the implementation prompt explicitly expands scope.
- `training/data/dataset_manifest.json`
- JSONL files.
- Package/dependency files.
- Runtime project fixture files outside controlled test temp paths.
- OMI runtime records.
- Memory/canon runtime files.
- Apply-promotion.
- Extraction.
- AI prose generation.

## 8. Required Safety Boundary Prompt For Future Implementation

Future Phase 7 implementation prompts should repeat these boundaries:

- Verify WSL repo root with `pwd` and `git rev-parse --show-toplevel`.
- Do not write to `C:\home...`, `/mnt/c/home/...`, Git Bash paths, or Windows mirror paths.
- The app is analysis-only.
- AI must not write, rewrite, continue, imitate, polish, improve, expand, or extend story prose.
- Owner-authored text saves are allowed and must not be overblocked.
- Candidates are not canon.
- Promotion records are audit-only until apply-promotion exists.
- No model/Ollama calls unless the task explicitly requires them.
- No training, JSONL creation, dataset files, or `training/data/dataset_manifest.json` changes.
- No raw book source commits.
- No external extractor installs unless separately approved after a dedicated spike.
- No Dramatica-specific implementation during Phase 7.

## 9. Phase 7 Acceptance Checklist

- [ ] Create blank project.
- [ ] Validate `project_id` and collision handling.
- [ ] Scan and select projects.
- [ ] Show invalid project states safely.
- [ ] Switch projects without data loss.
- [ ] Remove hard-coded frontend `PROJECT_ID`.
- [ ] Create/edit/save/reload scenes.
- [ ] Preserve existing `scenes/{scene_id}.md` compatibility.
- [ ] Organize chapters/scenes if included.
- [ ] Create/edit/save/reload notes.
- [ ] Add/reference materials with provenance/license warnings.
- [ ] Shared editor dirty-state behavior works for scenes, notes, and materials.
- [ ] Project Overview shell loads without writes or model calls.
- [ ] OMI status visibility remains candidate/audit-only.
- [ ] Approved memory/canon shell or empty state is present.
- [ ] Candidate/canon labels are visible and consistent.
- [ ] No AI prose-generation controls exist.
- [ ] No model calls occur during storage, search, listing, project switching, or navigation.
- [ ] Backend tests pass for implemented slices.
- [ ] Frontend build passes for frontend slices.
- [ ] Manual browser checklist passes or has documented owner exception.

## 10. Roadmap Update Decisions

WORKSPACE-026 should be registered as the completed planning handoff after `WORKSPACE-001` through `WORKSPACE-025`.

Roadmap docs should treat the next implementation track as:

1. Finish or record owner acceptance for MVP exit disposition.
2. Review/commit the WORKSPACE-026 documentation package.
3. Start `PHASE7-IMPL-001`.

The former future safety-test ideas should move under Phase 7 validation planning rather than occupying `WORKSPACE-026`, because this task now owns that workspace ID.

## 11. Deferred Decisions And Non-Goals

Deferred:

- Runtime project selector recovery/import.
- Archive/delete.
- `projects/index.json`.
- OMI durable pre-project inbox.
- Candidate extraction triggers.
- Typed OMI story-knowledge candidates.
- Project memory/canon storage files.
- `memory/index.json`.
- Apply-promotion.
- Approved category pages with real records.
- Cross-link health repair/rebuild.
- Semantic search.
- Graph visualization.
- Contradiction detection.
- External extractor installs.
- Dramatica-specific logic.
- Fine-tuning, JSONL, dataset, RunPod, and live model tracks.

Non-goals for Phase 7 first slices:

- No generated prose.
- No generated summaries.
- No generated fixes.
- No rewrite/continue/polish/improve controls.
- No memory/canon mutation.
- No training data mutation.
- No hidden model calls.
