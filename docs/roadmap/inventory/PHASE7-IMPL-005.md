# PHASE7-IMPL-005 Inventory

## Task Identity

- Task ID: `PHASE7-IMPL-005`
- Canonical title: Notes / Materials Storage
- Type: `runtime`
- Current roadmap status: `active_next`
- Active track: Project Workspace Foundation
- Dependencies from roadmap authority: `PHASE7-IMPL-003`
- Preceding completed parent: `PHASE7-IMPL-004` - Chapter / Scene Metadata Compatibility Layer
- Primary source specs:
  - `docs/roadmap/notes_materials_data_model_spec.md` (`WORKSPACE-006`)
  - `docs/roadmap/notes_materials_page_spec.md` (`WORKSPACE-010`)
  - `docs/roadmap/user_authored_document_editor_workflow_spec.md` (`WORKSPACE-007`)
  - `docs/roadmap/project_workspace_implementation_decision_sweep.md`
  - `docs/roadmap/project_file_model.md`

## Boundary Summary

`PHASE7-IMPL-005` covers owner-authored notes and owner-provided materials storage/routes. Notes and materials are Markdown/text body files with separate metadata records. They are project source material, not approved canon by default and not training data by default.

Extracted knowledge from notes/materials must enter OMI as candidates only in later explicitly scoped tasks. Storage, save, list, and route behavior must not run extraction or silently promote material into durable truth.

Hard boundaries:

- No model calls or Ollama calls.
- No generated prose, generated summaries, generated navigation prose, or metadata-derived prose.
- No extraction behavior, semantic search, web fetching, OCR, binary import, external sync, file watcher, attachments, package installs, or training-data ingestion.
- No OMI candidate creation, OMI promotion, memory/canon mutation, `bible.json` mutation, or `storyform.json` mutation from note/material storage operations.
- No runtime project fixture writes during inventory work.
- No frontend or backend runtime implementation during `PHASE7-IMPL-005-T001`.

## Target Storage Model

The first-version layout from `WORKSPACE-006` is:

```text
projects/{project_id}/
  notes/
    {note_id}.md
  note_metadata/
    {note_id}.json
  materials/
    {material_id}.md
  material_metadata/
    {material_id}.json
```

Rules:

- Note body content remains owner-authored Markdown/text in `notes/{note_id}.md`.
- Material body content remains owner-authored or owner-provided Markdown/text in `materials/{material_id}.md`.
- Metadata lives separately in `note_metadata/{note_id}.json` and `material_metadata/{material_id}.json`.
- Listing/opening a project must not create note/material files.
- Future create actions may create missing folders.
- Notes/materials must not be silently copied into `bible.json`, `storyform.json`, OMI promotion records, memory/canon files, JSONL files, training data, or dataset manifests.

Expected note metadata fields from `WORKSPACE-006`:

- `metadata_version`
- `project_id`
- `note_id`
- `title`
- `note_type`
- `status`
- `tags`
- `linked_chapter_ids`
- `linked_scene_ids`
- `linked_candidate_ids`
- `linked_memory_record_ids`
- `created_at`
- `updated_at`
- `content_path`
- `word_count`
- `owner_notes`
- `summary_candidate_id`
- `approved_navigation_summary`
- `provenance`

Expected material metadata fields from `WORKSPACE-006`:

- `metadata_version`
- `project_id`
- `material_id`
- `title`
- `material_type`
- `status`
- `tags`
- `source_kind`
- `source_url`
- `source_citation`
- `local_reference_path`
- `linked_chapter_ids`
- `linked_scene_ids`
- `linked_candidate_ids`
- `linked_memory_record_ids`
- `created_at`
- `updated_at`
- `content_path`
- `owner_notes`
- `provenance`
- `license_status`
- `usage_restrictions`

ID rules from the spec:

- IDs must be stable filesystem-safe single path components.
- Recommended generated patterns: `note_001`, `note_002`, `material_001`, `material_002`.
- Titles stay separate from IDs.
- Collisions fail closed.
- Reserved names include project/storage folders such as `project`, `chapters`, `scenes`, `scene_metadata`, `notes`, `note_metadata`, `materials`, `material_metadata`, `memory`, `omi`, `bible`, `storyform`, and host-reserved names.

## Current Backend Evidence

Relevant `backend/project_manager.py` patterns:

- `WORKSPACE_CORE_FOLDERS` already includes `notes`, `note_metadata`, `materials`, and `material_metadata` for blank-project folder creation.
- `_safe_path_component(value, label)` rejects empty values, path traversal, absolute paths, multi-part paths, `.`, and `..`.
- `_project_dir(project_name)` derives the safe project directory.
- `_scene_path(project_name, scene_id)` is the closest body-file helper pattern for Markdown/text storage.
- `_scene_metadata_path(project_name, scene_id)` and `_chapter_metadata_path(project_name, chapter_id)` are direct metadata path patterns.
- `_write_json_object(path, data, label, overwrite=...)` writes JSON through a temp file and supports fail-closed collision behavior.
- `_load_json_object_from_path(path, label)` loads JSON metadata and requires a JSON object.
- `_utc_now()` and `_utc_after(previous_timestamp)` provide timestamp patterns for create/update.
- `_copy_metadata_payload`, `_string_or_none`, `_string_list`, `_metadata_object`, and `_safe_scene_id_list` are reusable validation/normalization patterns.
- `load_scene`, `save_scene`, and `list_scenes` provide the current body read/write/list behavior to mirror for notes/materials.
- `create_scene_metadata`, `update_scene_metadata`, `load_scene_metadata`, `create_chapter_metadata`, and `update_chapter_metadata` provide the closest helper-level metadata create/update/read patterns.

No note or material body/metadata helpers are present yet.

Relevant `backend/main.py` patterns:

- `ProjectCreate` and `SceneUpdate` are existing Pydantic request model patterns.
- `get_projects` / `post_project` show project route error handling.
- `get_scenes`, `get_scene`, and `update_scene` show project-scoped document route shapes.
- No note/material routes are present yet.

## Current Frontend Evidence

Relevant `frontend/src/api.js` patterns:

- Project-scoped helpers accept `projectId = PROJECT_ID`.
- Scene helpers use `/projects/${projectId}/scenes`, `/projects/${projectId}/scenes/${sceneId}`, and PUT `{ content }`.
- Notes/materials API helpers do not exist yet.

Relevant frontend state and UI assumptions:

- `frontend/src/App.jsx` owns `activeProjectId`, selected scene state, dirty-state checks, scene load/save, and project-scoped API calls.
- `frontend/src/components/ProjectNav.jsx` renders project navigation and the current scene list. It has scene option normalization from PHASE7-IMPL-005 predecessor work, but no notes/materials navigation.
- `frontend/src/components/Editor.jsx` is the current owner-authored body editor used for scenes.
- `frontend/src/components/ProjectContext.jsx` handles Bible/storyform JSON, not notes/materials.
- No Notes / Materials page or shared scene/note/material editor exists yet. Shared editor expansion belongs to `PHASE7-IMPL-006` unless a PHASE7-IMPL-005 child explicitly scopes a minimal shell.

## Current Tests Evidence

Relevant tests to extend:

- `tests/test_project_manager.py`: backend helper tests for scenes, project creation, metadata helpers, OMI boundaries, path safety, and no-prose overblocking. This is the primary target for `PHASE7-IMPL-005-T002`.
- `tests/test_scene_routes.py`: route testing pattern with fake FastAPI/Pydantic modules and direct route function calls. This is the likely target for note/material route tests after backend helpers exist.
- `tests/test_frontend_project_workspace_source.py`: source-level frontend workspace checks. This is the likely target for frontend API/source compatibility checks.

No note/material-specific tests are present yet.

## Proposed Child Task Sequence

No PHASE7-IMPL-005 child task IDs are currently registered in `docs/roadmap/roadmap_index.yaml`. Proposed minimal sequence:

1. `PHASE7-IMPL-005-T001` - Notes / Materials Storage and Routes Inventory. Type: `planning_microtask`. Status: this artifact task.
2. `PHASE7-IMPL-005-T002` - Backend note/material storage helpers. Type: `runtime_microtask`.
3. `PHASE7-IMPL-005-T003` - Backend note/material routes. Type: `runtime_microtask`.
4. `PHASE7-IMPL-005-T004` - Route compatibility and path-safety tests. Type: `validation_microtask`.
5. `PHASE7-IMPL-005-T005` - Frontend API compatibility helpers for notes/materials. Type: `runtime_microtask`.
6. `PHASE7-IMPL-005-T006` - Minimal notes/materials navigation/display shell, only if still in scope after route/API work. Type: `runtime_microtask`.
7. `PHASE7-IMPL-005-T007` - Roadmap/status closeout. Type: `runtime_microtask`.

## Recommended Next Implementation Child

Recommended next child:

`PHASE7-IMPL-005-T002` - Backend note/material storage helpers.

Likely allowed files:

- `backend/project_manager.py`
- `tests/test_project_manager.py`

Likely T002 scope:

- Safe note/material path helpers.
- Note body save/load/list helpers.
- Material body save/load/list helpers.
- Note metadata create/update/load/list helpers.
- Material metadata create/update/load/list helpers.
- Sequential ID generation or fail-closed requested-ID creation, consistent with local specs.
- Safe derived identity fields and `content_path`.
- Metadata-only source/provenance/license warning fields.
- Tests for path safety, collision behavior, missing vs empty body behavior, metadata defaults, timestamp updates, and no mutation of scenes, OMI, memory/canon, training files, JSONL files, dataset manifests, bible, or storyform.

Out of scope for T002:

- Backend routes.
- Frontend changes.
- Search UI or semantic search.
- Extraction or candidate creation.
- Web fetching, OCR, binary import, external sync, attachments, or package changes.
- Shared editor implementation.
- Memory/canon or OMI mutation.

## Evidence Quality Notes

- Roadmap authority files and local specs are primary for identity, status, scope, and boundaries.
- Current source files were read directly for focused inventory only.
- No CCE, Graphify, Repomix, AI Context generation, MCP tools, or broad discovery were run.
- No runtime implementation, tests, app servers, frontend builds, model calls, or project fixture writes were performed for this inventory.
