# WORKSPACE-007: User-Authored Document Editor / Save-Reload Workflow Spec

Status: Documentation-only planning handoff. Runtime implementation is future work.

Product working name: Dramatica-Informed Writing Assistant.

Current priority: Pre-Dramatica Project Workspace Foundation.

Related planning:

- WORKSPACE-001: `docs/roadmap/project_workspace_foundation_spec.md`
- WORKSPACE-002: `docs/roadmap/project_creation_flow_spec.md`
- WORKSPACE-003: `docs/roadmap/project_selector_library_spec.md`
- WORKSPACE-004: `docs/roadmap/omi_guided_project_creation_spec.md`
- WORKSPACE-005: `docs/roadmap/chapter_scene_data_model_spec.md`
- WORKSPACE-006: `docs/roadmap/notes_materials_data_model_spec.md`
- Project file model: `docs/roadmap/project_file_model.md`

## 1. Purpose and Scope

The shared document editor should let the owner create, edit, save, reload, and organize owner-authored or owner-provided project documents across scenes, notes, and materials without treating those saved fields as AI prose-generation requests.

The editor should support owner-authored or owner-provided:

- Scene prose.
- Chapter/scene notes.
- General notes.
- Research notes.
- Project materials.
- Planning text.
- Reference notes.

Boundary rules:

- Editor content is owner-authored or owner-provided.
- Saving editor content must not be blocked as AI prose generation.
- Editor content is not automatically approved canon.
- Editor content may later be source material for candidate extraction.
- Editor content must not be training data by default.
- AI output must never be inserted into editor content.
- Future analysis/extraction must operate separately from the editor and produce diagnostics or candidates only.

The application may store, edit, and organize owner-authored prose, notes, and materials. The AI must never write, rewrite, continue, imitate, polish, improve, or extend story prose.

Standard refusal message:

```text
I can analyze structure and ask diagnostic questions, but I cannot write or rewrite story prose.
```

## 2. Shared Document Types

First-version shared editor document types:

- `scene`
- `note`
- `material`

Optional/future document types:

- `chapter_note`
- `project_overview_note`
- Project Overview itself is a landing/navigation page defined by WORKSPACE-008, not a document body editor in the first implementation.
- `omi_raw_idea_view`, read-only or OMI-scoped unless separately designed.
- `approved_memory_record_editor`, only after a separate memory/canon editing safety design.

### Scene Document

Body path:

```text
projects/{project_id}/scenes/{scene_id}.md
```

Metadata path:

```text
projects/{project_id}/scene_metadata/{scene_id}.json
```

Editable fields:

- Body Markdown/plain text.
- Title.
- Status.
- Tags.
- Owner notes.
- Future optional metadata links where owner-approved.

Read-only or derived fields:

- `scene_id`
- `project_id`
- `content_path`
- `word_count`
- `created_at`
- Server/disk `updated_at`
- Source hash or revision token, if implemented.

Empty behavior:

- Intentionally empty scenes are valid.
- Empty scenes are distinct from missing scene files.

Save/reload expectations:

- Save updates owner-authored scene body and optional metadata.
- Reload reads body and metadata from disk/server.
- Save/reload must not call a model, write OMI promotions, or mutate memory/canon.
- WORKSPACE-009 defines how the Chapters / Scenes page should apply this shared editor behavior to scene selection, chapter switching, scene movement, page navigation, and candidate-only analysis separation.

### Note Document

Body path:

```text
projects/{project_id}/notes/{note_id}.md
```

Metadata path:

```text
projects/{project_id}/note_metadata/{note_id}.json
```

Editable fields:

- Body Markdown/plain text.
- Title.
- `note_type`.
- Status.
- Tags.
- Owner notes.
- Chapter/scene/candidate/memory links as metadata references.

Read-only or derived fields:

- `note_id`
- `project_id`
- `content_path`
- `word_count`
- `created_at`
- Server/disk `updated_at`
- Source hash or revision token, if implemented.

Empty behavior:

- Intentionally empty notes are valid.
- Empty notes are distinct from missing note files.

Save/reload expectations:

- Save updates owner-authored note body and optional metadata.
- Reload reads body and metadata from disk/server.
- Save/reload must not call a model, write OMI promotions, or mutate memory/canon.

### Material Document

Body path:

```text
projects/{project_id}/materials/{material_id}.md
```

Metadata path:

```text
projects/{project_id}/material_metadata/{material_id}.json
```

Editable fields:

- Body Markdown/plain text when the material has editable body content.
- Title.
- `material_type`.
- Status.
- Tags.
- Owner notes.
- Source URL/citation metadata.
- License status and usage restrictions.
- Chapter/scene/candidate/memory links as metadata references.

Read-only or derived fields:

- `material_id`
- `project_id`
- `content_path`
- `created_at`
- Server/disk `updated_at`
- Source hash or revision token, if implemented.

Empty behavior:

- Intentionally empty owner-created materials are valid.
- Reference-only material metadata may exist without body content if clearly labeled.
- Empty material body is distinct from missing material file.

Save/reload expectations:

- Save updates owner-authored or owner-provided material body and optional metadata.
- Reload reads body and metadata from disk/server.
- Save/reload must not fetch web content, call a model, write OMI promotions, or mutate memory/canon.

## 3. Editor State Model

The shared editor should model document state explicitly so scenes, notes, and materials behave consistently.

Future frontend/editor states:

| State | Meaning |
| --- | --- |
| `loading` | Document body and/or metadata is being loaded. |
| `loaded_clean` | Body and metadata match the last confirmed loaded/saved server state. |
| `loaded_dirty` | Body or metadata has local unsaved owner edits. |
| `saving` | A save request is in progress. |
| `saved` | Last save completed and local baseline was updated. |
| `save_failed` | Last save failed; local editor content is preserved. |
| `reload_pending` | Reload was requested while dirty content requires confirmation. |
| `conflict_detected` | Server/disk document changed after the editor loaded it. |
| `invalid_document` | ID, metadata, or body/metadata shape is invalid. |
| `not_found` | Document does not exist. |
| `read_only` | Document can be inspected but not edited. |
| `blocked_action` | Requested action is disallowed by safety or validation rules. |

Minimum editor state fields:

```json
{
  "selected_project_id": "example",
  "selected_document_type": "scene",
  "selected_document_id": "scene_001",
  "current_editor_content": "",
  "last_saved_content": "",
  "current_metadata": {},
  "last_saved_metadata": {},
  "body_dirty": false,
  "metadata_dirty": false,
  "save_error": null,
  "load_error": null,
  "last_saved_at": null,
  "loaded_updated_at": null,
  "server_updated_at": null,
  "loaded_revision": null,
  "server_revision": null
}
```

Dirty detection:

- `body_dirty` is true when `current_editor_content !== last_saved_content`.
- `metadata_dirty` is true when current editable metadata differs from the last saved/loaded metadata baseline.
- Overall dirty state is `body_dirty || metadata_dirty`.
- Dirty state should reset only after a confirmed successful save or an owner-confirmed discard/reload.
- Save failure must not update `last_saved_content` or `last_saved_metadata`.

Project scoping:

- Editor state must include `selected_project_id`.
- Switching projects must clear document-specific editor state and analysis state.
- Unsaved content must not leak across projects.

## 4. Save Behavior

Save behavior must preserve owner control and avoid silent side effects.

Rules:

- Save owner-authored body content for scenes, notes, and materials.
- Save metadata separately or together depending on implementation, but track body and metadata dirty state separately.
- Preserve editor content on save failure.
- Update dirty state only after confirmed save.
- Support intentional empty body saves.
- Reject invalid document IDs.
- Reject path traversal.
- Validate `project_id`, `document_type`, and `document_id` server-side.
- Validate that `document_type` is allow-listed.
- Avoid model/Ollama calls.
- Avoid OMI candidate creation by default.
- Avoid OMI promotion.
- Avoid memory/canon mutation.
- Avoid `bible.json` or `storyform.json` truth mutation.
- Avoid dataset/training writes.
- Avoid writing AI output into body files.

Recommended save flow:

1. Owner edits body and/or metadata.
2. UI marks `body_dirty` and/or `metadata_dirty`.
3. Owner chooses Save, or uses a keyboard shortcut mapped to Save.
4. Frontend sends current body and/or metadata plus last-known revision/timestamp.
5. Backend validates path safety, document type, IDs, project membership, and conflict token if available.
6. Backend writes only the requested document body/metadata.
7. Backend returns updated metadata, timestamp, and revision/hash if available.
8. Frontend updates `last_saved_content`, `last_saved_metadata`, dirty flags, and save status only after success.

Failure behavior:

- Keep `current_editor_content`.
- Keep current editable metadata.
- Keep dirty flags.
- Show a save failure banner/status.
- Do not silently retry destructive writes.
- Do not overwrite local content with server content after a failed save.

## 5. Reload Behavior

Reload reads the current document body and metadata from disk/server.

Rules:

- Warn before overwriting dirty editor content.
- Allow owner to cancel reload.
- Preserve unsaved local content if reload fails.
- Distinguish `not_found` from an empty file.
- Distinguish missing metadata from invalid metadata.
- Distinguish metadata mismatch from body not found.
- Do not auto-repair destructively.
- Do not create missing files during reload.
- Do not call a model.
- Do not create candidates.
- Do not mutate memory/canon.

Recommended reload flow:

1. Owner chooses Reload or document load happens through navigation.
2. If current document is dirty, show Save / Discard and reload / Cancel.
3. If owner cancels, keep current editor state unchanged.
4. If owner discards, load body and metadata from disk/server.
5. If reload succeeds, update current content, current metadata, saved baselines, and server revision/timestamp.
6. If reload fails, preserve previous local editor state and show load/reload error.

Missing and invalid states:

| State | Behavior |
| --- | --- |
| Missing body file | Show `not_found` or invalid/recoverable state. Do not treat as empty. |
| Empty body file | Load as empty content and allow intentional save. |
| Missing metadata | Show recoverable metadata warning if body exists. |
| Corrupt metadata | Load body only if safe; show warning; block metadata save until repaired. |
| Body/metadata ID mismatch | Block normal save; show recovery/help state. |
| Unsupported metadata version | Show needs-migration warning; do not normal-save until migration is approved. |

## 6. Unsaved-Change Protections

The editor must protect owner-authored content from accidental loss.

Required warnings:

- Scene switch warning.
- Note switch warning.
- Material switch warning.
- Project switch warning.
- Browser unload warning.
- Route/page navigation warning.
- Create-new-document warning if current document is dirty.
- Future delete/archive warning if current document is dirty.

Recommended owner choices:

- Save.
- Discard.
- Cancel.

Project switch behavior:

- Warn if any editor document in the current project has unsaved owner-authored changes.
- Either preserve unsaved state per project or require explicit Save/Discard before switching.
- First implementation should require explicit Save/Discard/Cancel before project switch unless per-project draft preservation is deliberately implemented.
- Clear project-specific transient analysis state after switch.
- Clear or reload OMI candidates, bible/storyform, memory/canon, analysis state, document lists, and editor state for the selected project.
- Never mix document content across projects.
- Never carry unsaved content from one project into another project editor.

## 7. Conflict Detection Planning

First-version conflict detection may use timestamp comparison:

- Store `loaded_updated_at` when the document loads.
- Send `last_known_updated_at` on save.
- Backend compares with current server/disk metadata timestamp.
- If server/disk updated after the editor loaded, return a conflict response.

Future conflict detection may use:

- Body content hash.
- Metadata hash.
- Revision counter.
- Per-file modification time plus hash.
- Combined document ETag-style token.

Conflict behavior:

- No automatic merge in first version.
- Save should fail closed or warn on detected conflict.
- Owner chooses Reload, Overwrite, or Cancel.
- Overwrite must be explicit.
- Cancel preserves local editor content.
- Reload must warn if local content is dirty.
- Conflict UI should show document identity, last local load time, current server update time, and affected body/metadata side if known.

## 8. No-Prose UI Safety

The shared editor may provide owner-editing and organization controls only.

Prohibited controls:

- Write.
- Continue.
- Rewrite.
- Polish.
- Improve.
- Make better.
- Imitate style.
- Expand scene.
- Generate dialogue.
- Generate chapter.
- Generate prose.
- Insert AI text.
- Apply AI rewrite.

Allowed controls:

- Save.
- Reload.
- Rename metadata.
- Tag.
- Link.
- Organize.
- Format owner-authored text with basic local editor formatting.
- Analyze structure, only as a separate candidate/diagnostic action.
- Extract candidates, only when later implemented and candidate-only.
- Ask diagnostic questions, only separate from editor writing.

No-prose guard behavior:

- Do not run freeform assistant-request guards against owner-authored body save content.
- Do guard future assistant/model instruction fields before model calls.
- Do sanitize future model output before display/persistence where applicable.
- Do keep AI analysis output out of editor body.
- If the owner asks the assistant to write or rewrite prose, use the standard refusal message.

## 9. Analysis and Extraction Separation

Future Story Check or extraction may read owner-authored source text, but it must not edit that text.

Rules:

- Analysis reads owner-authored scene/note/material content as source.
- Analysis output appears in diagnostics, analysis sidebars, or candidate review panels.
- Analysis output must not appear in editor body as inserted text.
- Analysis output may reference evidence spans.
- Extraction output routes to OMI candidates.
- Extraction must not create OMI promotion records by default.
- Extraction must not mutate approved memory/canon without explicit owner promotion.
- Extraction must not mutate `bible.json` or `storyform.json` as truth.
- Extraction must not create JSONL/training records.
- The owner may manually write their own conclusions into the editor, but the app must not auto-insert AI text.

Allowed future analysis actions:

- Run Story Check on selected owner-authored scene, where supported.
- Run candidate extraction on selected owner-authored documents, when later implemented.
- Ask diagnostic questions in a separate panel.
- Show evidence locators pointing back to source spans.

Prohibited future analysis actions:

- Apply suggestion to editor.
- Rewrite selected text.
- Continue from cursor.
- Expand outline into prose.
- Generate scene from note.
- Promote candidate to canon without explicit future promotion flow.

## 10. API Planning

These routes are future planning only. Do not implement them during WORKSPACE-007.

First implementation may choose either:

- A shared document route layer for `scene`, `note`, and `material`; or
- Type-specific routes from WORKSPACE-005 and WORKSPACE-006 with a shared frontend adapter/state model.

Recommendation:

- Use type-specific backend routes first if that keeps validation and storage behavior simpler.
- Use a shared frontend document adapter so UI state, dirty checks, save/reload, and switch protections are consistent.
- Consider shared backend document routes later if type-specific behavior becomes duplicated.

Every route must validate `project_id`, `document_type`, and `document_id`. IDs must align with backend safe path helpers and reject traversal, absolute paths, slashes, backslashes, empty values, dot, dot-dot, leading dots, and reserved names.

### `GET /api/projects/{project_id}/documents/{document_type}/{document_id}`

Purpose: load a document body plus editable metadata summary.

Request: path parameters only.

Response shape:

```json
{
  "project_id": "example",
  "document_type": "scene",
  "document_id": "scene_001",
  "content": "Owner-authored text",
  "metadata": {
    "title": "Opening Scene",
    "status": "draft",
    "tags": []
  },
  "updated_at": "2026-06-08T00:00:00Z",
  "revision": "optional-revision-token",
  "warnings": []
}
```

Validation: document type must be allow-listed; content is owner-authored/owner-provided storage, not assistant output.

Expected errors: invalid project ID, invalid document type, invalid document ID, missing document, unreadable body, corrupt metadata, project mismatch.

### `PUT /api/projects/{project_id}/documents/{document_type}/{document_id}`

Purpose: save owner-authored or owner-provided document body.

Request shape:

```json
{
  "content": "Owner-authored text",
  "last_known_updated_at": "2026-06-08T00:00:00Z",
  "last_known_revision": "optional-revision-token"
}
```

Response shape:

```json
{
  "project_id": "example",
  "document_type": "scene",
  "document_id": "scene_001",
  "saved": true,
  "updated_at": "2026-06-08T00:00:01Z",
  "revision": "optional-new-revision-token",
  "word_count": 123
}
```

Validation: do not guard owner body as an assistant request; do validate size, path safety, document type, project membership, conflict token, and file state.

Expected errors: invalid IDs, missing document, conflict, content too large, read-only document, write failure.

### `GET /api/projects/{project_id}/documents/{document_type}/{document_id}/metadata`

Purpose: load full document metadata.

Request: path parameters only.

Response: full metadata record plus warnings.

Expected errors: invalid IDs, missing metadata, corrupt metadata, unsupported metadata version, project mismatch.

### `PATCH /api/projects/{project_id}/documents/{document_type}/{document_id}/metadata`

Purpose: update editable metadata fields.

Request shape:

```json
{
  "title": "Updated title",
  "status": "active",
  "tags": ["revision"],
  "owner_notes": "Owner-authored metadata note",
  "last_known_updated_at": "2026-06-08T00:00:00Z"
}
```

Response: updated metadata record plus revision/timestamp.

Validation: cannot mutate identity fields into unsafe values; linked IDs must be safe; candidate/canon links remain references only.

Expected errors: invalid IDs, missing metadata, corrupt metadata, unsupported version, conflict, invalid references, write failure.

### `POST /api/projects/{project_id}/documents/{document_type}`

Purpose: create a new empty owner-editable document of an allowed type.

Request shape:

```json
{
  "title": "Untitled",
  "status": "draft",
  "tags": [],
  "metadata": {}
}
```

Response: created document body/metadata summary.

Validation: generated ID must be safe and collision-free; body starts empty unless a future explicit owner-provided initial content path is designed.

Expected errors: invalid project ID, invalid document type, ID collision, invalid metadata, write failure.

### `POST /api/projects/{project_id}/documents/{document_type}/{document_id}/reload-check`

Purpose: compare local editor revision/timestamp with server/disk state before reload or save.

Request shape:

```json
{
  "last_known_updated_at": "2026-06-08T00:00:00Z",
  "last_known_revision": "optional-revision-token"
}
```

Response shape:

```json
{
  "project_id": "example",
  "document_type": "scene",
  "document_id": "scene_001",
  "changed_on_server": false,
  "current_updated_at": "2026-06-08T00:00:00Z",
  "current_revision": "optional-revision-token"
}
```

Validation: check only metadata/revision state; do not mutate files.

Expected errors: invalid IDs, missing document, unreadable metadata.

## 11. Frontend Planning

Future UI surfaces:

- Shared editor component.
- Document header.
- Body editor.
- Metadata panel.
- Save control.
- Reload control.
- Dirty indicator.
- Body dirty and metadata dirty indicators.
- Save failure banner.
- Load/reload failure banner.
- Conflict warning modal.
- Project/document switch confirmation modal.
- Read-only/corrupt warning state.
- Not-found state.
- Invalid-document state.
- Source/evidence locator support later.

Recommended shared component responsibilities:

- Render body content for supported document types.
- Track editable content changes.
- Expose save/reload actions.
- Show save/reload status.
- Show dirty state.
- Disable editing for read-only/corrupt states.
- Avoid rendering any AI-writing controls.

Recommended parent/workspace responsibilities:

- Track selected project/document.
- Load document lists.
- Handle project/document switching.
- Scope analysis/candidate state by project and document.
- Provide type-specific metadata panels.
- Route analysis and extraction output to separate panels.

## 12. Future Tests

Future implementation should include tests for:

- Save owner-authored scene body.
- Save owner-authored note body.
- Save owner-authored material body.
- Save intentionally empty body.
- Save metadata separately from body.
- Save failure preserves editor content.
- Dirty state updates only after successful save.
- Reload warns before overwriting dirty content.
- Reload failure preserves unsaved local content.
- Project switch warns and clears project-scoped state.
- Document switch warns.
- Browser unload warning exists.
- Route/page navigation warning exists.
- Create-new-document action warns when current document is dirty.
- Invalid document IDs rejected.
- Invalid document type rejected.
- Path traversal rejected.
- Missing file versus empty file handled correctly.
- Corrupt metadata warning shown.
- Body/metadata mismatch warning shown.
- Conflict detection warning shown.
- No owner-authored save overblocked by no-prose guard.
- No AI prose-generation controls exposed.
- No model/Ollama call during save/reload/switch.
- No OMI promotion during save/reload/switch.
- No memory/canon mutation during save/reload/switch.
- No `bible.json` or `storyform.json` truth mutation during save/reload/switch.
- No JSONL/training writes.
- `training/data/dataset_manifest.json` unchanged.

## 13. Deferred Decisions

Deferred to future implementation tasks:

- Shared backend document routes versus type-specific backend routes.
- Exact editor library/component split for scene, note, and material bodies.
- Whether per-project unsaved drafts are preserved or project switching requires explicit Save/Discard.
- Conflict token strategy: timestamp, hash, revision counter, or hybrid.
- Whether metadata and body saves are atomic together or separately confirmed.
- Autosave policy. First recommendation is no autosave until conflict and recovery behavior are implemented.
- Local draft recovery after browser crash.
- Maximum body size limits by document type.
- Rich text versus Markdown storage beyond current Markdown/text body files.
- Source/evidence locator UI details.
- Whether approved memory/canon record editing should use this shared editor after a separate safety design.

## 14. Implementation Non-Goals

WORKSPACE-007 does not implement:

- Backend document routes.
- Frontend editor changes.
- Save/reload changes.
- Frontend note/material UI.
- Extractor logic.
- Dramatica-specific logic.
- Runtime project files under `projects/`.
- OMI records.
- Memory/canon runtime files.
- JSONL records.
- Training or fine-tuning.
- Ollama/live model verification.
- Package/dependency changes.
