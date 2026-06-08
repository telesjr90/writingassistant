# Project Selector / Library Spec

## 1. Purpose

This specification defines `WORKSPACE-003`, the detailed planning handoff for the future Project Selector / Project Library flow in the pre-Dramatica Project Workspace Foundation.

This is documentation only. It does not implement backend routes, frontend UI, tests, package changes, datasets, JSONL records, training data, model calls, project runtime files, OMI records, memory/canon files, extractor logic, Dramatica-specific logic, staging, commits, or pushes.

The future selector/library should let the writer browse local writing projects, inspect lightweight metadata and health warnings, open one project, switch between projects safely, and avoid corrupt or unsafe project folders becoming active silently.

The app remains analysis-only. It may store, edit, save, reload, and organize owner-authored prose, but the AI must never write, rewrite, continue, imitate, polish, improve, or extend story prose.

Standard refusal message:

`I can analyze structure and ask diagnostic questions, but I cannot write or rewrite story prose.`

## 2. Current Context Observed

Current runtime state, inspected read-only for planning:

- `backend/project_manager.py` stores project data under repo-local `projects/`.
- Existing helper `_safe_path_component()` rejects empty values, absolute paths, path traversal, `"."`, and `".."`.
- Current scene operations use `projects/{project_name}/scenes/{scene_id}.md`.
- Current OMI helpers store project-local ideas, candidates, promotion audit records, and `omi/index.json` under an existing project path through owner actions.
- Current OMI promotion records do not apply durable truth.
- `backend/main.py` exposes project-scoped scene, bible, storyform, Story Check, and OMI routes, but no project listing/opening route yet.
- `frontend/src/api.js` hard-codes `PROJECT_ID = 'example'`.
- `frontend/src/App.jsx` has scene-level unsaved-change confirmation and clears the Story Check report on scene switch.
- `frontend/src/components/ProjectNav.jsx` renders scene navigation for the current hard-coded project.
- `frontend/src/components/OMIPanel.jsx` displays candidate-only boundary copy and has no prose-generation controls.

This spec plans future work. It does not change those runtime files.

## 3. Project Library Purpose

The Project Library should allow the owner to:

- View all local projects.
- Open an existing project.
- Switch between projects.
- See basic project metadata.
- See project health and status warnings before opening.
- Avoid opening corrupt or unsafe project folders silently.
- Avoid accidental project deletion.
- Avoid path traversal or unsafe `project_id` behavior.
- Keep pending candidates separate from approved canon.

The library is a navigation and inspection surface. It is not a story-authoring, extraction, training, or promotion surface.

Project Library must not:

- Generate project prose.
- Generate summaries during listing.
- Call Ollama, qwen3, or any other model during listing or opening.
- Run candidate extraction during listing or opening.
- Promote OMI candidates or memory/canon records.
- Write JSONL records or update `training/data/dataset_manifest.json`.
- Treat pending OMI candidates as approved canon.
- Delete or rewrite project folders automatically.

## 4. Discovery Strategy

### Recommended First Implementation

The first implementation should scan `projects/` for immediate child folders that contain a valid `project.json`.

Reasons:

- It avoids a stale index becoming authoritative.
- It lets the library recover if `projects/index.json` is missing.
- It keeps project creation centered on one durable metadata file.
- It can represent missing/corrupt folders as warnings without inventing project truth.
- It keeps `projects/index.json` future-only until scan behavior is reliable.

First implementation rule:

```text
projects/{folder_name}/project.json
```

A folder is a normal openable project only when:

- The folder name is a safe single filesystem component.
- `project.json` exists.
- `project.json` parses as a JSON object.
- Required metadata fields exist and pass validation.
- `project.json.project_id` is safe.
- `project.json.project_id` matches the folder name, unless a future migration/recovery flow explicitly handles mismatch.
- No duplicate active `project_id` has already been accepted into the listing.

### Optional Future `projects/index.json`

`projects/index.json` may be added later as rebuildable navigation metadata only.

Rules:

- It must be rebuildable from project folders and `project.json`.
- It must not be the only source of project identity.
- It must not contain story prose.
- It must not contain raw model output.
- It must not contain OMI candidate content.
- It must not contain approved memory/canon records.
- It must not contain JSONL records, source book text, model artifacts, or secrets.
- If stale or corrupt, the app should rebuild or ignore it rather than treating it as truth.

### Discovery Edge Cases

Missing `project.json`:

- Do not include as a normal valid project.
- Optionally show an invalid/recoverable row with `metadata_status: "missing_project_json"`.
- Do not auto-create `project.json`.
- Do not infer title, canon, storyform, bible, memory, or OMI truth from folder contents.

Corrupt `project.json`:

- Do not include as a normal valid project.
- Show a warning row with `metadata_status: "invalid_json"` when safe to do so.
- Do not rewrite the file automatically.
- Recovery UI may offer help text or a future owner-initiated repair/import task.

Duplicate `project_id` values:

- Fail closed for normal opening.
- Mark all conflicting folders with `metadata_status: "duplicate_project_id"` or equivalent.
- Do not pick a winner silently.
- Do not rewrite either project identity.
- Recovery must be owner-initiated.

Unsafe folder names:

- Reject or flag folders whose names are not safe single path components.
- Never open by raw folder name if it contains absolute paths, slashes, backslashes, traversal, `"."`, `".."`, control characters, or reserved names.
- Do not follow unsafe symlinks unless a future task explicitly approves a safe symlink policy.

Unreadable files:

- Return a non-fatal warning row when possible.
- Do not leak full host filesystem paths in API errors.
- Do not crash the whole project library.

Empty `projects/`:

- Return an empty valid list and no fatal error.
- Frontend should show an empty library state with a Create Project action linked to WORKSPACE-002.

Existing `example` project:

- Treat `projects/example` as a normal legacy/sample project only if it has valid `project.json`.
- Keep `example` stable until a future implementation replaces the hard-coded frontend `PROJECT_ID = 'example'`.
- Do not mutate `projects/example` as part of selector/library listing.

Content read limits:

- Listing must not read full `scenes/*.md`, `notes/*.md`, `materials/*.md`, chapter prose, or long source material.
- Counts should use directory/file existence, metadata files, small derived indexes, or stored counts when available.
- WORKSPACE-005 defines the future chapter/scene metadata sources for cheap chapter and scene counts. The library should use those metadata sources when available and still avoid reading full scene prose during listing.
- WORKSPACE-006 defines the future note/material metadata sources for cheap notes and materials counts. The library should use those metadata sources when available and still avoid reading full note/material body text during listing.
- Navigation summaries shown in the library must already be owner-authored or owner-approved metadata; listing must not create summaries.

## 5. Library Metadata

Each valid project card or list row should show:

- `project_id`
- Display title.
- Subtitle, if available.
- Owner-authored description excerpt, if available.
- `created_at`
- `updated_at`
- `status`
- `language`
- `creation_method`: `blank` or `omi_guided`; future values may include `legacy` or `imported`.
- Tags, if present and owner-authored.
- Cheap counts, when available.
- Warning badges.

Cheap counts may include:

- Chapters.
- Scenes.
- Notes.
- Materials.
- OMI candidates.
- Approved memory/canon records.

Count rules:

- Counts are derived navigation metadata, not story truth.
- Counts may be missing or stale without blocking project opening.
- Count collection must avoid full prose reads.
- OMI candidate counts must remain separate from approved memory/canon counts.
- Approved memory/canon counts must read only approved memory/canon files after those files exist.

Warning badges:

- Missing metadata.
- Invalid metadata.
- Unsupported schema version.
- Empty project.
- Needs migration.
- Candidate-only data present.
- No approved canon yet.
- Duplicate project ID.
- Unsafe folder name.
- Unreadable metadata.

Authorship and prose boundaries:

- Descriptions and notes shown on project cards are owner-authored only.
- Project cards must not contain AI-generated story prose.
- Project cards must not use pending candidate prose as display summary.
- Summaries used for navigation must be owner-authored, owner-approved candidate metadata, or already approved navigation metadata.
- OMI setup data may be summarized only as candidate status/counts unless the owner approved metadata into `project.json`.

## 6. Sorting, Filtering, and Search

First-version sorting:

- Default sort: `updated_at` descending.
- If `updated_at` is missing or invalid, fallback to title.
- If title is missing, fallback to `project_id`.
- Invalid/corrupt rows should be grouped after valid projects by default unless the user enables a recovery-focused view.

Optional first filters:

- Status.
- Creation method.
- Has scenes.
- Has OMI candidates.
- Has approved memory.

Simple local search:

- Search over project title.
- Search over `project_id`.
- Search over owner-authored description.
- Search over tags.

Search rules:

- No model call.
- No semantic search in the first implementation.
- No extraction or summarization during listing.
- No full scene/chapter/note/material reads.
- Search results must keep invalid/corrupt warnings visible.

## 7. Project Opening Behavior

Opening a project means making one validated project active in the app shell and loading the Project Overview.

Required opening behavior:

1. Owner selects a project from the library.
2. Frontend sends a specific `project_id`.
3. Backend validates `project_id` as a safe single path component.
4. Backend loads `projects/{project_id}/project.json`.
5. Backend validates required metadata.
6. App opens Project Overview by default.

First implementation does not need to persist a last-opened page. A future preference may store last opened page or selected scene after the selector is stable.

Missing optional folders:

- Missing `chapters/`, `scene_metadata/`, `notes/`, `materials/`, `omi/`, or `memory/` should not block opening.
- Project Overview should show empty states or warnings.
- Missing optional folders should not be auto-created during read-only opening unless a future owner-approved repair action requests it.

Corrupt required metadata:

- Corrupt `project.json`, missing required identity fields, unsupported schema, or project ID mismatch should block normal opening.
- Frontend should show a recovery/help state with a non-destructive explanation.

Opening must not:

- Trigger candidate extraction.
- Call Ollama, qwen3, or any model.
- Promote OMI candidates.
- Create OMI promotion records.
- Create or mutate memory/canon records.
- Create `memory/` files.
- Update bible/storyform/scenes/notes/materials.
- Create JSONL records or training artifacts.

## 8. Project Switching Behavior

Switching projects means leaving one active project and loading another.

Required behavior:

- If the current editor has unsaved owner-authored changes, warn before switching.
- The app should either preserve unsaved state per project or require explicit discard/save before switching.
- Switching must clear project-specific transient analysis state.
- Switching must load project-scoped OMI data, memory records, bible/storyform context, scenes, notes, and project metadata only for the new project.
- Switching must not mix OMI candidates, promotion records, approved memory/canon, bible/storyform, notes, scenes, or analysis reports across projects.
- Current hard-coded `PROJECT_ID = 'example'` should be removed only in a future implementation task.

Transient state to clear or reload on switch:

- Selected scene ID.
- Editor content and saved baseline.
- Story Check report.
- OMI summary and selected OMI record.
- Bible/storyform text and status.
- Project Overview counts.
- Any candidate extraction state.
- Any approved memory/canon cache.

Unsaved-change policy options:

1. Block switch until owner saves or discards.
2. Preserve unsaved drafts keyed by `project_id` and content ID.
3. Auto-save only after an explicit owner setting exists.

Recommended first implementation:

- Warn and require explicit save/discard.
- Do not auto-save during project switch.

## 9. Invalid and Corrupt Project Handling

The selector should represent these states explicitly.

| State | Meaning | Future UI Behavior |
| --- | --- | --- |
| `valid` | Safe folder and valid `project.json` | Normal card/list row and Open action. |
| `missing_project_json` | Folder exists without `project.json` | Warning row or hidden-by-default recovery view; no normal Open action. |
| `invalid_json` | `project.json` does not parse as JSON object | Warning row with recovery/help state; no normal Open action. |
| `project_id_mismatch` | Folder name and `project.json.project_id` differ | Warning row; block normal open; owner-initiated repair/import only. |
| `unsupported_schema_version` | Metadata schema is newer/unknown or otherwise unsupported | Warning row; block or limited-open depending on migration policy; no silent rewrite. |
| `missing_required_folders` | Required folder for the chosen implementation is missing | Warn; block only if the folder is truly required for opening. |
| `unreadable_project` | Permissions or IO error prevents metadata read | Warning row; do not leak host paths; no normal Open action. |
| `unsafe_folder_name` | Folder is not a safe path component | Warning or hidden invalid row; never open by raw path. |
| `duplicate_project_id` | Multiple folders claim the same project ID | Warning rows; no silent winner; owner must resolve. |
| `partial_creation_leftover` | Folder appears created by failed creation flow | Warning row; offer future recover/import/delete guidance only through explicit owner action. |

Safety rules:

- Show warnings instead of crashing.
- Allow safe recovery where appropriate.
- Avoid destructive repair.
- Never auto-delete.
- Never silently rewrite project identity.
- Never import unknown folders as canon.
- Never trust metadata enough to bypass path validation.
- Avoid exposing sensitive host filesystem paths in API errors.

## 10. Archive and Delete Planning

Deletion is not part of the first selector/library implementation unless the owner later approves it explicitly.

Future archive behavior:

- Archive before delete.
- Archive status may live in `project.json.status = "archived"`.
- Archived projects may be hidden by default.
- The library should have an "include archived" filter before any delete path exists.
- Archiving must be an explicit owner action.
- Archiving must not delete files.
- Archiving must not run AI or candidate extraction.

Future delete behavior:

- Permanent delete must require explicit confirmation.
- Delete should likely require typing the project title or `project_id`.
- Delete must never be automated by AI.
- Delete must not run as a side effect of failed open, failed migration, or corrupt metadata.
- Delete must be a separate implementation task with tests and owner approval.
- Any delete planning should consider a backup/archive export before removal.

## 11. API Planning

These routes are planning targets only. They are not implemented by this documentation task.

### `GET /api/projects`

Purpose:

- List local projects and invalid/recoverable project folders for the Project Library.

Request:

- No body.
- Optional query params may include `include_invalid`, `include_archived`, `status`, `creation_method`, `has_scenes`, `has_omi_candidates`, `has_approved_memory`, `search`, `sort`, and `direction`.

Response shape:

```json
{
  "projects": [
    {
      "project_id": "example",
      "folder_name": "example",
      "title": "Example Project",
      "subtitle": "",
      "description_excerpt": "",
      "status": "active",
      "language": "en",
      "creation_method": "blank",
      "created_at": "2026-06-07T00:00:00Z",
      "updated_at": "2026-06-07T00:00:00Z",
      "counts": {
        "chapters": 0,
        "scenes": 1,
        "notes": 0,
        "materials": 0,
        "omi_candidates": 0,
        "approved_memory_records": 0
      },
      "metadata_status": "valid",
      "warning_badges": []
    }
  ],
  "invalid_projects": [
    {
      "folder_name": "bad-folder",
      "metadata_status": "invalid_json",
      "warning_badges": ["invalid metadata"],
      "openable": false
    }
  ],
  "errors": []
}
```

Validation:

- Scan only safe immediate children of `projects/`.
- Validate folder names before using them as path components.
- Parse only `project.json` and cheap metadata/count sources.
- Represent invalid entries safely.

No-prose boundary:

- Does not generate descriptions or summaries.
- Does not call a model.
- Does not read full prose content.

Candidate/canon boundary:

- Counts OMI candidates separately from approved memory/canon.
- Does not treat candidate-only data as approved truth.

Expected errors:

- 500 only for unexpected application failures.
- Per-project corrupt/unreadable states should be returned as warning rows where practical.

### `GET /api/projects/{project_id}`

Purpose:

- Load one project's metadata for opening and Project Overview initialization.

Request:

- No body.

Response shape:

```json
{
  "project": {
    "project_id": "example",
    "title": "Example Project",
    "subtitle": "",
    "description": "",
    "status": "active",
    "language": "en",
    "creation_method": "blank",
    "created_at": "2026-06-07T00:00:00Z",
    "updated_at": "2026-06-07T00:00:00Z",
    "default_view": "overview"
  },
  "health": {
    "metadata_status": "valid",
    "warnings": []
  }
}
```

Validation:

- Validate `project_id` server-side as a safe path component.
- Load `project.json` only.
- Validate required metadata and folder/name identity.

No-prose boundary:

- Reads owner-authored metadata only.
- Does not generate text or call a model.

Candidate/canon boundary:

- Does not read or promote OMI candidates.
- Does not load approved memory/canon unless Project Overview requests it through a separate read path.

Expected errors:

- 400 invalid `project_id`.
- 404 project or `project.json` not found.
- 409 duplicate or identity mismatch where applicable.
- 422 unsupported schema or invalid metadata.

### `PATCH /api/projects/{project_id}`

Purpose:

- Update owner-authored project metadata such as title, subtitle, description, tags, language, or status.

Request shape:

```json
{
  "title": "Example Project",
  "subtitle": "",
  "description": "",
  "language": "en",
  "status": "active",
  "tags": []
}
```

Response shape:

```json
{
  "project": {
    "project_id": "example",
    "title": "Example Project",
    "updated_at": "2026-06-07T00:00:00Z"
  }
}
```

Validation:

- `project_id` path identity cannot be changed by this route.
- Metadata fields must be length-limited and JSON-serializable.
- Status values must be allow-listed.

No-prose boundary:

- Owner-authored metadata saves are allowed.
- This route must not be treated as an assistant prose-generation request.
- This route must not generate replacement descriptions.

Candidate/canon boundary:

- Does not mutate scenes, notes, materials, OMI candidates, promotion records, bible, storyform, or memory/canon.

Expected errors:

- 400 invalid project ID or invalid metadata.
- 404 project not found.
- 409 update conflict, if future write-version checks exist.
- 422 unsupported schema or corrupt metadata.

### `GET /api/projects/{project_id}/health`

Purpose:

- Return detailed project health information for a selected project without opening it normally.

Request:

- No body.

Response shape:

```json
{
  "project_id": "example",
  "status": "valid",
  "checks": [
    {
      "check": "project_json",
      "status": "pass",
      "severity": "info",
      "message": "Project metadata is valid."
    },
    {
      "check": "approved_memory",
      "status": "warning",
      "severity": "info",
      "message": "No approved canon records yet."
    }
  ],
  "openable": true
}
```

Validation:

- Validate `project_id` before reading.
- Use project-relative paths in messages.
- Avoid sensitive host paths.

No-prose boundary:

- Health messages are operational diagnostics only.
- No summaries, rewrites, or model calls.

Candidate/canon boundary:

- Health may report candidate counts and approved-memory counts separately.
- Health must not promote or apply candidates.

Expected errors:

- 400 invalid `project_id`.
- 404 project not found.
- 422 corrupt metadata where the health route cannot produce a structured result.

### `POST /api/projects/index/rebuild` Later

Purpose:

- Future owner/developer-triggered rebuild of `projects/index.json` as derived navigation metadata.

Request shape:

```json
{
  "include_invalid": true
}
```

Response shape:

```json
{
  "status": "rebuilt",
  "project_count": 1,
  "invalid_count": 0,
  "index_path": "projects/index.json"
}
```

Validation:

- Rebuild from folder scan and valid `project.json`.
- Do not trust the existing index.
- Write only derived navigation data.

No-prose boundary:

- No model call, no generated summaries, no full prose reads.

Candidate/canon boundary:

- Do not copy candidate content or memory/canon records into the index.

Expected errors:

- 500 write failure.
- Per-project errors should be captured as index warnings where practical.

### `PATCH /api/projects/{project_id}/archive` Later

Purpose:

- Future explicit owner action to mark a project archived.

Request shape:

```json
{
  "archived": true,
  "confirmation": "example"
}
```

Response shape:

```json
{
  "project": {
    "project_id": "example",
    "status": "archived",
    "updated_at": "2026-06-07T00:00:00Z"
  }
}
```

Validation:

- Validate `project_id`.
- Require explicit confirmation.
- Allow unarchive if owner confirms.

No-prose boundary:

- No generated text.

Candidate/canon boundary:

- Archiving changes project metadata only.
- It does not mutate OMI, scenes, notes, memory/canon, bible, or storyform.

Expected errors:

- 400 invalid confirmation.
- 404 project not found.
- 422 corrupt project metadata.

## 12. Frontend Planning

Future UI surfaces:

- Project Library screen.
- Project cards or table.
- Project search, filter, and sort controls.
- Project switcher in the app shell.
- Empty library state.
- Invalid/corrupt project warning state.
- Open Project action.
- Create Project action linking to WORKSPACE-002 and the WORKSPACE-004 OMI-guided creation path.
- Archive/delete placeholders only if future-approved.
- Project Overview as the open target.

Project Library screen:

- First screen when no active project is selected.
- Shows valid projects with metadata and warnings.
- Can show invalid/recoverable rows in a separate warning section.
- Provides local search/filter/sort controls.
- Provides Create Project entry point.

Project card/table:

- Shows title, `project_id`, status, updated date, creation method, language, description excerpt, tags, counts, and warning badges.
- Does not show generated story prose.
- Does not show pending candidate content as canon.

Project switcher:

- Shows the active project title and `project_id`.
- Opens the library or compact dropdown.
- Uses unsaved-change protection before switching.

Empty library state:

- Explain that no valid projects were found.
- Link to Create Project.
- Optionally show invalid/recoverable folders if any exist.

Invalid/corrupt warning state:

- Explains the problem without host path leakage.
- Offers non-destructive help or future repair/import action.
- Does not offer one-click destructive delete in the first implementation.

Control boundaries:

- No AI writing buttons.
- No controls named or behaving like "generate project", "write my story", "continue", "rewrite", "polish", "improve", "draft dialogue", or "imitate this style".
- OMI-guided creation remains idea organization and candidate review only.
- Project Library must not expose extraction, promotion, or apply-canon actions.

## 13. Security and Path Safety

Project selector/library must reuse or align with backend safe path helpers.

`project_id` requirements:

- Must be one filesystem-safe component.
- Must not be empty.
- Must not be `"."` or `".."`.
- Must not be an absolute path.
- Must not contain `..` traversal components.
- Must not contain `/` or `\`.
- Must not contain control characters.
- Must not be a reserved name.
- Should align with WORKSPACE-002 first implementation slug rules.

Backend requirements:

- Never trust `project_id` from the frontend alone.
- Validate on every route.
- Resolve all project paths from the canonical `PROJECTS_DIR`.
- Do not use raw `project_id` in host filesystem error messages.
- Do not follow unsafe symlinks during library scanning unless a future task explicitly approves a safe symlink policy.
- Avoid reading outside `projects/`.
- Fail closed on ambiguous identity, duplicate IDs, corrupt metadata, or unsupported schema.

Frontend requirements:

- Treat backend validation errors as authoritative.
- Do not construct filesystem paths.
- Do not hide warnings that block normal opening.
- Do not assume `project_id` is safe because it came from an earlier list response.

## 14. Future Tests

Future implementation should add tests before or with runtime changes.

Project library tests:

- Project library lists valid projects.
- Empty `projects/` returns an empty list safely.
- Missing `project.json` is handled safely.
- Corrupt `project.json` is handled safely.
- Unsafe folder names are ignored or flagged.
- Duplicate `project_id` behavior fails closed.
- Unsupported schema version is flagged.
- Unreadable metadata does not crash the whole listing.
- Listing does not read full scene/chapter/note/material content.
- Existing `example` project lists when its metadata is valid.

Path safety tests:

- Project ID path traversal is rejected.
- Absolute paths are rejected.
- Dot and dot-dot are rejected.
- Slashes and backslashes are rejected.
- Reserved names are rejected.
- Frontend-provided `project_id` is revalidated server-side.

Project opening tests:

- Opening project loads project metadata.
- Invalid/corrupt metadata blocks normal opening with a recovery state.
- Missing optional folders do not block opening.
- Opening project lands on Project Overview.
- Opening does not call Ollama or any live model.
- Opening does not trigger extraction.
- Opening does not promote OMI candidates.
- Opening does not create or mutate memory/canon.

Project switching tests:

- Unsaved editor changes warn before project switch.
- Explicit cancel preserves current project and unsaved text.
- Explicit discard or save permits switch.
- Project switch clears project-specific transient analysis state.
- OMI candidates, memory records, bible/storyform, notes, and scenes do not mix across projects.

No-prose and data safety tests:

- No model/Ollama call during listing or opening.
- No JSONL/training writes.
- No `training/data/dataset_manifest.json` update.
- No OMI promotion or memory/canon mutation during listing/opening.
- No AI prose-generation controls in Project Library UI.
- Project cards do not show AI-generated story prose.
- Pending candidates are not displayed as approved canon.

Frontend tests:

- Project Library screen renders.
- Project cards/table render valid metadata.
- Search/filter/sort controls operate locally.
- Empty library state renders.
- Invalid/corrupt warning state renders.
- Open action selects a project only after backend validation.
- Create Project action links to WORKSPACE-002 flow.
- Project switcher handles unsaved-change confirmation.

## 15. Deferred Decisions

These remain for implementation or later planning tasks:

- Exact invalid-folder visibility: hidden by default, warning section, or recovery tab.
- Whether project cards or a table should be the first UI presentation.
- Whether folder scan should include only directories or also safe symlinks after a separate policy review.
- Whether duplicate `project_id` conflicts block all duplicates or allow an advanced recovery open.
- Whether `projects/index.json` is introduced immediately after scan-first listing or deferred until performance requires it.
- Whether invalid/corrupt project recovery includes owner-created `project.json` scaffolding.
- Whether last-opened project/page is stored in browser local storage, repo-local settings, or not at all.
- Whether unsaved editor state is preserved per project or switch requires save/discard.
- Exact status taxonomy for `active`, `draft`, `archived`, `template`, `needs_review`, and `legacy`.
- Whether archive is included in the first selector implementation or a later project-management task.
- Whether permanent delete is ever added, and what backup/export behavior is required first.

## 16. Related Specifications

- `docs/roadmap/project_workspace_foundation_spec.md`
- `docs/roadmap/project_creation_flow_spec.md`
- `docs/roadmap/omi_guided_project_creation_spec.md`
- `docs/roadmap/project_file_model.md`
- `docs/roadmap/omi_mvp_schema_lifecycle.md`
- `docs/roadmap/omi_storage_model.md`
- `docs/roadmap/omi_story_knowledge_candidate_expansion.md`
- `docs/roadmap/project_memory_canon_storage_model.md`
- `docs/roadmap/writer_assistant_core_candidate_schemas.md`
- `docs/roadmap/task_backlog.md`
- `docs/roadmap/phase_map.md`
- `docs/roadmap/open_questions.md`
- `docs/roadmap/risk_register.md`
- `docs/roadmap/mvp_completion_test_matrix.md`
- `docs/master_plan.md`
- `docs/plan.md`
