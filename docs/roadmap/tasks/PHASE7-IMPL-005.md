# PHASE7-IMPL-005

## ID

`PHASE7-IMPL-005`

## Title

Notes / Materials Storage

## Goal

Add owner-authored notes and owner-provided materials storage/routes while preserving local-first project safety, separating body files from metadata, and keeping notes/materials out of canon, OMI, memory, and training data by default.

## Why now

`PHASE7-IMPL-004` completed chapter/scene metadata compatibility. The active Phase 7 frontier now moves to notes/materials so the workspace can store project-adjacent owner-authored and owner-provided text before shared editor expansion in `PHASE7-IMPL-006`.

## Inputs / Dependencies

- Required prior parent task: `PHASE7-IMPL-003`.
- Completed preceding parent task: `PHASE7-IMPL-004`.
- Roadmap authority:
  - `docs/roadmap/roadmap_index.yaml`
  - `docs/roadmap/implementation_status.md`
  - `docs/roadmap/project_workspace_implementation_decision_sweep.md`
  - `docs/roadmap/task_backlog.md`
- Source specs:
  - `docs/roadmap/notes_materials_data_model_spec.md`
  - `docs/roadmap/notes_materials_page_spec.md`
  - `docs/roadmap/user_authored_document_editor_workflow_spec.md`
  - `docs/roadmap/project_file_model.md`
- Inventory:
  - `docs/roadmap/inventory/PHASE7-IMPL-005.md`
- Enrichment JSON:
  - `docs/roadmap/enrichment/PHASE7-IMPL-005.enrichment.json`

## Scope

Include:

- Owner-authored note Markdown/text body storage.
- Owner-provided material Markdown/text body storage for the first version.
- Separate note/material metadata records.
- Safe local project path handling.
- Future route/API/frontend compatibility planning.
- Focused helper, route, and source tests in child tasks.

Exclude:

- Runtime implementation during `PHASE7-IMPL-005-T001`.
- Binary attachment implementation.
- Web fetching, OCR, external sync, file watchers, arbitrary import pipelines, and package installs.
- Extraction, semantic search, generated summaries, generated navigation prose, model calls, and Ollama calls.
- OMI candidate creation, OMI promotion, memory/canon mutation, `bible.json` mutation, `storyform.json` mutation, JSONL/training/dataset changes, and runtime project fixture writes.
- Shared editor implementation unless a later PHASE7-IMPL-005 child explicitly scopes a minimal display shell. Full shared editor work belongs to `PHASE7-IMPL-006`.

## Product / Safety Boundaries

- Notes/materials are owner-authored or owner-provided content.
- Notes/materials are not approved canon by default.
- Notes/materials are not training data by default.
- Extracted knowledge from notes/materials must remain future OMI candidate work unless explicitly scoped later.
- AI output must never be inserted into note/material body content.
- Metadata fields such as titles, tags, owner notes, citations, source URLs, and license notes are owner-authored or owner-provided.
- Search/filter behavior, if later scoped, must be local and deterministic unless a future task explicitly approves otherwise.

## Current Evidence Summary

Backend:

- `backend/project_manager.py` already creates core folders including `notes`, `note_metadata`, `materials`, and `material_metadata` for blank projects.
- Existing scene helpers provide body read/write/list patterns.
- Existing chapter/scene metadata helpers provide JSON metadata path, read, create, update, timestamp, and normalization patterns.
- No note/material helpers exist yet.

Routes:

- `backend/main.py` has project and scene route patterns.
- No note/material routes exist yet.

Frontend:

- `frontend/src/api.js` has project-scoped API helper patterns.
- `frontend/src/App.jsx` controls active project and current scene editor state.
- `frontend/src/components/ProjectNav.jsx` renders project and scene navigation only.
- `frontend/src/components/Editor.jsx` is the current owner-authored scene editor.
- No notes/materials UI or shared editor exists yet.

Tests:

- `tests/test_project_manager.py` is the primary helper-level test target.
- `tests/test_scene_routes.py` is the route test pattern.
- `tests/test_frontend_project_workspace_source.py` is the frontend source-level regression pattern.

## Child Micro-task Sequence

Completed sequence:

1. `PHASE7-IMPL-005-T001` - Notes / Materials Storage and Routes Inventory. Status: complete.
2. `PHASE7-IMPL-005-T002` - Backend note/material storage helpers. Status: complete.
3. `PHASE7-IMPL-005-T003` - Backend note/material routes. Status: complete.
4. `PHASE7-IMPL-005-T004` - Route compatibility and path-safety tests. Status: complete.
5. `PHASE7-IMPL-005-T005` - Frontend API compatibility helpers for notes/materials. Status: complete.
6. `PHASE7-IMPL-005-T006` - Minimal notes/materials navigation/display shell. Status: complete.
7. `PHASE7-IMPL-005-T007` - Roadmap/status closeout. Status: complete after the closeout validation recorded in `docs/roadmap/validation/latest_roadmap_validation.md`.

## Acceptance Criteria

- Notes use `notes/{note_id}.md` for Markdown/text bodies and `note_metadata/{note_id}.json` for metadata.
- Materials use `materials/{material_id}.md` for Markdown/text bodies and `material_metadata/{material_id}.json` for metadata.
- Metadata identity and content paths are derived safely from requested project/document IDs.
- Body save routes do not create metadata records.
- Metadata writes require existing note/material body files in this implementation slice.
- Read/list operations do not create metadata files as a side effect.
- Path safety and server-derived identity/path fields are enforced by helpers and routes.
- Frontend API helpers and the minimal navigation/display shell can list, select, load, and save exact owner-authored note/material body content by ID.
- Notes/materials remain source material, not canon and not training data by default.
- Save/list/load operations do not call models, run extraction, create summaries, create OMI candidates, promote candidates, mutate memory/canon, mutate `bible.json` or `storyform.json`, create JSONL/training records, or update dataset manifests.
- Metadata editing UI and the full shared editor refactor remain deferred.

## Validation Checklist

Final closeout validation:

- `.venv-unsloth-clean/bin/python -m pytest tests/test_project_manager.py`
- `.venv-unsloth-clean/bin/python -m pytest tests/test_note_material_routes.py`
- `.venv-unsloth-clean/bin/python -m pytest tests/test_frontend_project_workspace_source.py`
- `.venv-unsloth-clean/bin/python -m pytest tests/test_scene_routes.py`
- `python3 scripts/check_enrichment.py`
- `python3 scripts/validate_roadmap.py`
- `git diff --check`
- `git status --short --branch`

## Completion Summary

`PHASE7-IMPL-005` is complete after `PHASE7-IMPL-005-T007` records the implementation status and validation results.

Implemented behavior:

- Backend helpers store note and material body files separately from metadata files.
- Backend routes expose note/material list, body read/write, and metadata read/write endpoints through the helper layer.
- Route compatibility and path-safety tests cover unsafe project/document IDs, missing body reads, read-only list behavior, metadata identity/path derivation, and body-only save behavior.
- Frontend API helpers expose note/material route calls without transforming body content.
- The minimal frontend shell lists notes/materials, selects documents by ID, loads exact body content, and saves exact owner-authored content without metadata injection.

Deferred work:

- Full shared scene/note/material editor workflow remains under `PHASE7-IMPL-006`.
- Browser/manual validation remains under `PHASE7-IMPL-010`.
- Extraction, semantic search, summaries, OMI candidate creation, memory/canon mutation, training/JSONL/dataset updates, and model/Ollama calls remain out of scope.
