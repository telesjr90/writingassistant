# WORKSPACE-006: Notes / Materials Data Model Spec

Status: Documentation-only planning handoff. Runtime implementation is future work.

Product working name: Dramatica-Informed Writing Assistant.

Current priority: Pre-Dramatica Project Workspace Foundation.

Related planning:

- WORKSPACE-001: `docs/roadmap/project_workspace_foundation_spec.md`
- WORKSPACE-002: `docs/roadmap/project_creation_flow_spec.md`
- WORKSPACE-003: `docs/roadmap/project_selector_library_spec.md`
- WORKSPACE-004: `docs/roadmap/omi_guided_project_creation_spec.md`
- WORKSPACE-005: `docs/roadmap/chapter_scene_data_model_spec.md`
- Project file model: `docs/roadmap/project_file_model.md`
- OMI storage model: `docs/roadmap/omi_storage_model.md`
- Project memory/canon storage model: `docs/roadmap/project_memory_canon_storage_model.md`

## 1. Purpose

The notes and materials model should let the writer store, edit, organize, search, and later analyze project-adjacent owner-authored or owner-provided content that is not chapter or scene prose.

The first implementation should support:

- Owner-authored planning notes.
- Research notes.
- Worldbuilding notes.
- Character notes.
- Location notes.
- Timeline notes.
- Plot notes.
- Brainstorming.
- Reference links.
- Imported reference metadata.
- Project materials that are not scene/chapter prose.
- Future links to chapters, scenes, OMI candidates, and approved memory/canon records.
- Future candidate extraction from owner-selected notes/materials.

Boundary rules:

- Notes/materials are owner-authored or owner-provided content.
- Saving notes/materials must not be blocked as AI prose generation.
- Notes/materials are not automatically approved canon.
- Notes/materials may become sources for future candidate extraction only through explicit owner action or a later approved policy.
- Notes/materials must not be treated as training data by default.
- External/reference material requires provenance and license caution.
- Notes/materials summaries or labels, if introduced later, are navigation/candidate metadata only and must not become AI-authored story prose.

The application may store, edit, and organize owner-authored prose, notes, and materials. The AI must never write, rewrite, continue, imitate, polish, improve, or extend story prose.

Standard refusal message:

```text
I can analyze structure and ask diagnostic questions, but I cannot write or rewrite story prose.
```

## 2. Notes vs Materials

### Notes

Notes are owner-authored Markdown text for planning, drafting support, research observations, references, reminders, brainstorms, and project organization.

Recommended first-version definition:

- Body content is Markdown/text.
- Content is owner-authored.
- Notes may be general or typed by purpose.
- Notes may link to chapters, scenes, OMI candidates, and future memory records through metadata.
- Notes are not scene/chapter prose.
- Notes are not canon by default.

Example note uses:

- General planning note.
- Character note.
- Location note.
- Timeline note.
- Plot note.
- Continuity note.
- Worldbuilding note.
- Research note.
- Brainstorm note.

### Materials

Materials are broader project resources supplied or tracked by the owner. They may include Markdown/text references, outlines, research links, citation metadata, imported document metadata, image metadata, or records pointing to owner-provided local resources.

Recommended first-version definition:

- Body content is Markdown/text for the first implementation.
- Metadata may describe references, links, citations, license status, usage restrictions, or local reference paths.
- Materials may be owner-authored or owner-provided.
- Materials may link to chapters, scenes, OMI candidates, and future memory records through metadata.
- Materials are not scene/chapter prose.
- Materials are not canon by default.

Explicit non-goals for WORKSPACE-006:

- No binary attachment implementation.
- No OCR/import pipeline.
- No web fetching.
- No external sync.
- No file watcher.
- No automatic conversion of arbitrary documents.
- No training-data ingestion.

Binary/file attachment support should be designed separately before implementation. Until then, material records may contain metadata about an external/local resource, but the first body file should remain Markdown/text.

## 3. Recommended Storage Layout

The recommended first implementation layout is:

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
- Note metadata lives in `note_metadata/{note_id}.json`.
- Material metadata lives in `material_metadata/{material_id}.json`.
- Metadata may link to chapters, scenes, OMI candidates, and future memory/canon records.
- `scenes/` remains separate from notes/materials.
- `chapters/` remains separate from notes/materials.
- Notes/materials must not be silently promoted into memory/canon.
- Notes/materials must not be silently copied into `bible.json` or `storyform.json`.
- Notes/materials must not be silently copied into OMI promotion records.
- Full body text should not be read just to list projects in the Project Library.

### Compatibility and Lazy Creation

WORKSPACE-002 recommends creating `notes/`, `note_metadata/`, `materials/`, and `material_metadata/` folders during project creation as part of the hybrid folder strategy. If an older project does not have these folders:

- Opening the project should not fail.
- Notes/Materials page should show an empty or missing-folder state.
- Future create actions may create the folders.
- No note/material runtime files should be created by library listing or project opening alone.

## 4. Note Metadata Schema

Future note metadata should use one JSON file per note:

```text
projects/{project_id}/note_metadata/{note_id}.json
```

Note body content remains separate:

```text
projects/{project_id}/notes/{note_id}.md
```

Recommended fields:

```json
{
  "metadata_version": 1,
  "project_id": "example",
  "note_id": "note_001",
  "title": "Planning Note",
  "note_type": "general",
  "status": "draft",
  "tags": [],
  "linked_chapter_ids": [],
  "linked_scene_ids": [],
  "linked_candidate_ids": [],
  "linked_memory_record_ids": [],
  "created_at": "2026-06-08T00:00:00Z",
  "updated_at": "2026-06-08T00:00:00Z",
  "content_path": "notes/note_001.md",
  "word_count": 0,
  "owner_notes": "",
  "summary_candidate_id": null,
  "approved_navigation_summary": null,
  "provenance": {
    "created_by": "owner",
    "creation_method": "manual",
    "source": "manual"
  }
}
```

Field rules:

| Field | Required | Meaning |
| --- | --- | --- |
| `metadata_version` | Yes | Version of the note metadata schema. |
| `project_id` | Yes | Owning project. Must match the project folder/project metadata. |
| `note_id` | Yes | Filesystem-safe note identifier. Must match metadata filename and Markdown filename stem. |
| `title` | Yes | Owner-authored display title. Empty string is allowed for untitled notes. |
| `note_type` | Yes | Owner-selected note classification. |
| `status` | Yes | Owner-controlled lifecycle label. |
| `tags` | No | Owner-authored organization tags. |
| `linked_chapter_ids` | No | Future chapter links. Metadata references only. |
| `linked_scene_ids` | No | Future scene links. Metadata references only. |
| `linked_candidate_ids` | No | Future OMI candidate links. Candidate references only. |
| `linked_memory_record_ids` | No | Future approved memory/canon links. Approved references only after apply-promotion exists. |
| `created_at` | Yes | Creation timestamp. |
| `updated_at` | Yes | Last metadata update timestamp. |
| `content_path` | Yes | Relative path to note Markdown. Must remain inside the project. |
| `word_count` | No | Derived count from note body text. Not owner truth or canon. |
| `owner_notes` | Yes | Owner-authored metadata notes about the note. |
| `summary_candidate_id` | No | Optional OMI navigation-summary candidate reference. |
| `approved_navigation_summary` | No | Optional owner-authored or owner-approved navigation aid. |
| `provenance` | Yes | Metadata about how the record was created or imported. |

Recommended `note_type` values:

- `general`
- `research`
- `worldbuilding`
- `character`
- `location`
- `timeline`
- `plot`
- `continuity`
- `brainstorm`

Boundary rules:

- Note title, `owner_notes`, tags, and body content are owner-authored.
- `word_count` may be derived but is not story truth.
- `approved_navigation_summary` is optional and must be owner-authored or owner-approved.
- Unapproved AI summaries are candidates only.
- Notes are not approved canon by default.
- Notes must not contain generated story prose inserted by AI.

## 5. Material Metadata Schema

Future material metadata should use one JSON file per material:

```text
projects/{project_id}/material_metadata/{material_id}.json
```

Material body content remains separate:

```text
projects/{project_id}/materials/{material_id}.md
```

Recommended fields:

```json
{
  "metadata_version": 1,
  "project_id": "example",
  "material_id": "material_001",
  "title": "Research Material",
  "material_type": "text_reference",
  "status": "draft",
  "tags": [],
  "source_kind": "owner_text",
  "source_url": null,
  "source_citation": null,
  "local_reference_path": null,
  "linked_chapter_ids": [],
  "linked_scene_ids": [],
  "linked_candidate_ids": [],
  "linked_memory_record_ids": [],
  "created_at": "2026-06-08T00:00:00Z",
  "updated_at": "2026-06-08T00:00:00Z",
  "content_path": "materials/material_001.md",
  "owner_notes": "",
  "provenance": {
    "created_by": "owner",
    "creation_method": "manual",
    "source": "manual"
  },
  "license_status": "owner_provided",
  "usage_restrictions": []
}
```

Field rules:

| Field | Required | Meaning |
| --- | --- | --- |
| `metadata_version` | Yes | Version of the material metadata schema. |
| `project_id` | Yes | Owning project. Must match the project folder/project metadata. |
| `material_id` | Yes | Filesystem-safe material identifier. Must match metadata filename and Markdown filename stem. |
| `title` | Yes | Owner-authored display title. Empty string is allowed for untitled materials. |
| `material_type` | Yes | Owner-selected material classification. |
| `status` | Yes | Owner-controlled lifecycle label. |
| `tags` | No | Owner-authored organization tags. |
| `source_kind` | Yes | Source category such as owner text, citation, link, local reference, imported metadata, or public-domain reference. |
| `source_url` | No | Owner-provided URL metadata only. The app must not fetch web content in this task. |
| `source_citation` | No | Owner-provided citation or bibliographic note. |
| `local_reference_path` | No | Owner-provided local reference path metadata. Must not be opened blindly. |
| `linked_chapter_ids` | No | Future chapter links. Metadata references only. |
| `linked_scene_ids` | No | Future scene links. Metadata references only. |
| `linked_candidate_ids` | No | Future OMI candidate links. Candidate references only. |
| `linked_memory_record_ids` | No | Future approved memory/canon links. Approved references only after apply-promotion exists. |
| `created_at` | Yes | Creation timestamp. |
| `updated_at` | Yes | Last metadata update timestamp. |
| `content_path` | Yes | Relative path to material Markdown. Must remain inside the project. |
| `owner_notes` | Yes | Owner-authored metadata notes about the material. |
| `provenance` | Yes | Metadata about how the record was created or imported. |
| `license_status` | Yes | Owner-provided or review-derived license/provenance state. |
| `usage_restrictions` | No | Owner-provided or review-derived restrictions. |

Recommended `material_type` values:

- `text_reference`
- `outline`
- `research`
- `worldbuilding`
- `character_reference`
- `location_reference`
- `timeline_reference`
- `plot_reference`
- `image_metadata`
- `imported_doc_metadata`
- `link`

Recommended `source_kind` values:

- `owner_text`
- `owner_file_metadata`
- `research_link`
- `citation`
- `public_domain_reference`
- `licensed_reference`
- `unknown_reference`
- `imported_metadata`

Recommended `license_status` values:

- `owner_created`
- `owner_provided`
- `public_domain`
- `licensed_for_project`
- `reference_only`
- `unknown`
- `restricted`

Boundary rules:

- `source_url` and citation metadata may exist, but the app must not fetch web content in this task.
- Imported/reference materials may have provenance and license constraints.
- Project materials are not training data by default.
- Copyrighted/reference material must not be treated as owner-authored story truth unless the owner explicitly says so.
- Reference material may support candidate extraction only with source/provenance and owner review.
- Binary/file attachment support is future-only unless separately designed.

## 6. ID Strategy

Note and material IDs must be stable filesystem-safe components.

Recommended first implementation:

- Backend-generated IDs by default.
- Sequential ID pattern: `note_001`, `note_002`, `material_001`, `material_002`.
- Keep owner-visible titles separate from IDs.
- Do not rename IDs when titles change.
- Do not migrate `project_id`, `note_id`, or `material_id` from display title changes.

Validation requirements:

- ID is a single path component.
- ID is not empty.
- ID is not `.` or `..`.
- ID is not an absolute path.
- ID contains no `/` or `\`.
- ID contains no path traversal.
- ID contains no leading dot.
- ID rejects reserved host names where relevant.
- ID length should be capped. Recommended cap: 64 characters for first implementation.
- Recommended pattern: lowercase ASCII letters, digits, and underscores: `^[a-z0-9][a-z0-9_]{0,63}$`.
- Hyphen support may be allowed only if it aligns with backend safe path helpers and tests.

Collision handling:

- New note/material creation must fail closed if the generated or requested ID already exists.
- Server-side ID generation should find the next available sequential ID.
- Client-side previews are advisory only.
- The backend must revalidate every ID and collision before writing files.

Reserved names:

- Reject names that would conflict with project folders or metadata such as `project`, `project_json`, `chapters`, `scenes`, `scene_metadata`, `notes`, `note_metadata`, `materials`, `material_metadata`, `memory`, `omi`, `bible`, `storyform`, `index`, `con`, `nul`, `prn`, `aux`, `com1`, and `lpt1`.
- Keep the reserved-name list aligned with project creation and backend path-safety helpers.

## 7. Organization and Linking Model

First-version organization should be metadata-driven and local.

Recommended first-version organization:

- Tags are stored in metadata.
- `note_type` and `material_type` are stored in metadata.
- Links to chapters/scenes are stored in metadata as ID arrays.
- Links to OMI candidates are stored in metadata as ID arrays.
- Links to future memory/canon records are stored in metadata as ID arrays.
- Link targets are not duplicated into body text.
- Body text remains owner-authored Markdown/text.
- Default list order is `updated_at` descending.
- Fallback list order is title, then ID.
- Manual ordering is deferred unless the first UI needs curated sections.

Link rules:

- Links are references, not canon claims.
- A note linked to a scene is not scene prose.
- A material linked to a memory record is not itself approved canon.
- Pending/rejected OMI candidates linked from notes/materials must remain visibly candidate-only.
- Approved memory/canon links may be shown only after future apply-promotion creates approved records.
- Broken links should be displayed as warnings with the missing target ID and target type.
- Broken links should not block body save.
- Broken links should block only operations that require a valid target, such as "filter by linked approved memory record" if the record is missing.

Backlinks and indexes:

- First implementation can compute backlinks by scanning metadata.
- A future `notes/index.json` or `materials/index.json` may be added only as rebuildable navigation metadata.
- Any future index must not become authoritative story truth.
- Any future index must not contain full body text, generated prose, unapproved candidate content, or canon records.

## 8. Save and Reload Behavior

Owner-authored note/material body save is allowed. The no-prose guard must not treat note/material save content as an AI prose-generation request.

Rules:

- Saving `notes/{note_id}.md` stores owner-authored note text.
- Saving `materials/{material_id}.md` stores owner-authored or owner-provided material text.
- Saving metadata updates `note_metadata/{note_id}.json` or `material_metadata/{material_id}.json`.
- Body save and metadata save may be separate route operations.
- Body save must never call a model.
- Body save must never create OMI candidates by default.
- Body save must never promote OMI candidates.
- Body save must never write approved memory/canon.
- Body save must never create JSONL records or update `training/data/dataset_manifest.json`.
- Save failures must preserve the current editor content in memory/UI.
- Reload must not overwrite unsaved edits without confirmation.
- Note/material switch and project switch should warn when current owner-authored edits are unsaved.
- Empty note save/load is valid when intentional.
- Empty material save/load is valid when intentional for owner-created text materials; reference-only material metadata may exist without body text if the UI clearly labels it.

Recommended first-version conflict behavior:

- Use last-loaded metadata timestamps or content hashes as optional conflict detection if cheap.
- If a conflict is detected, block overwrite and ask the owner to reload, save as a copy, or discard local changes.
- Do not silently merge note/material body text.

## 9. Local Search and Filter Planning

First-version search should be local, deterministic, and model-free.

Searchable fields:

- Title.
- Tags.
- `note_type`.
- `material_type`.
- Owner-authored body text, if cheap and safe.
- Linked chapter IDs.
- Linked scene IDs.
- Linked candidate IDs.
- Linked memory record IDs.
- Owner-authored `owner_notes`.
- Owner-authored/source citation labels where safe.

Filter fields:

- Note/material kind.
- Type.
- Status.
- Tags.
- Linked chapter.
- Linked scene.
- Has OMI candidate links.
- Has approved memory/canon links.
- Has source URL.
- License/provenance status for materials.
- Updated date range, if useful.

Rules:

- No semantic search in the first implementation.
- No model/Ollama call for search.
- No generated summaries during search.
- No candidate extraction during search.
- Search must not promote candidates.
- Search must not mutate memory/canon.
- Search results must distinguish notes/materials from approved canon/memory.
- Search snippets, if shown, should be verbatim owner-authored or owner-provided excerpts from local content and kept short.
- External URLs are searched only as metadata strings; no fetching.

Recommended first-version result shape:

```json
{
  "query": "watchtower",
  "results": [
    {
      "result_type": "note",
      "id": "note_001",
      "title": "Planning Note",
      "matched_fields": ["title", "body"],
      "snippet": "short owner-authored excerpt",
      "status": "draft",
      "tags": []
    }
  ]
}
```

## 10. UI Planning

Future UI surfaces:

- Notes/Materials page.
- Note list.
- Material list.
- Create note action.
- Create material action.
- Rename note/material action.
- Tag/filter/search controls.
- Note editor.
- Material editor.
- Metadata panel.
- Linked chapters/scenes/candidates display.
- Future approved memory/canon link display.
- Safe empty states.
- Unsaved change indicators.
- Invalid/corrupt warning states.
- Reference/license warning labels for materials.

UI boundaries:

- No AI writing buttons.
- No "continue", "rewrite", "polish", "improve", or style imitation controls.
- No "generate note", "generate material", "write worldbuilding", or "write outline" controls.
- Future analysis/extraction actions must be clearly labeled as candidate creation or diagnostics only.
- Search/filter controls must not imply semantic/model analysis in first version.
- Notes/materials must be visually distinct from approved memory/canon.
- Candidate links must remain visibly candidate-only unless future apply-promotion has produced approved records.

## 11. API Planning

These routes are future planning only. Do not implement them during WORKSPACE-006.

Every route must validate `project_id`; note routes must validate `note_id`; material routes must validate `material_id`. IDs must align with backend safe path helpers and reject traversal, absolute paths, slashes, backslashes, empty values, dot, dot-dot, leading dots, and reserved names.

Every route must preserve the no-prose and candidate/canon boundaries:

- Owner-authored body text may be saved through explicit note/material save routes.
- API routes must not generate, rewrite, continue, imitate, polish, improve, or extend prose.
- Listing, loading, saving, filtering, and searching must not call Ollama or any model.
- Listing, loading, saving, filtering, and searching must not create JSONL/training records.
- Listing, loading, saving, filtering, and searching must not create OMI promotion records.
- Listing, loading, saving, filtering, and searching must not write approved memory/canon.
- External/reference metadata must not be treated as training data or project canon by default.

### `GET /api/projects/{project_id}/notes`

Purpose: list note metadata.

Request: optional query parameters may include `type`, `status`, `tag`, `linked_chapter_id`, `linked_scene_id`, and `updated_after`.

Response shape:

```json
{
  "project_id": "example",
  "notes": [
    {
      "note_id": "note_001",
      "title": "Planning Note",
      "note_type": "general",
      "status": "draft",
      "tags": [],
      "updated_at": "2026-06-08T00:00:00Z",
      "word_count": 0,
      "warnings": []
    }
  ],
  "warnings": []
}
```

Validation: should not read full note body unless explicitly needed for body search or cheap derived metadata.

Expected errors: invalid `project_id`, missing project, unreadable notes directory, corrupt metadata.

### `POST /api/projects/{project_id}/notes`

Purpose: create an empty owner-editable note body plus metadata.

Request shape:

```json
{
  "title": "Planning Note",
  "note_type": "general",
  "status": "draft",
  "tags": []
}
```

Response: created note metadata and initial content state.

Validation: generated note ID must be collision-free; title and tags are owner-authored metadata.

Expected errors: invalid `project_id`, duplicate/generated ID collision, invalid metadata, write failure.

### `GET /api/projects/{project_id}/notes/{note_id}`

Purpose: load owner-authored note body content.

Request: path parameters only.

Response shape:

```json
{
  "project_id": "example",
  "note_id": "note_001",
  "content": "Owner-authored note text",
  "metadata": {
    "title": "Planning Note",
    "note_type": "general",
    "status": "draft"
  },
  "warnings": []
}
```

Validation: content is owner-authored storage, not assistant output.

Expected errors: invalid IDs, missing note, unreadable content, corrupt metadata.

### `PUT /api/projects/{project_id}/notes/{note_id}`

Purpose: save owner-authored note Markdown/text content.

Request shape:

```json
{
  "content": "Owner-authored note text",
  "last_known_updated_at": "2026-06-08T00:00:00Z"
}
```

Response shape:

```json
{
  "project_id": "example",
  "note_id": "note_001",
  "saved": true,
  "updated_at": "2026-06-08T00:00:00Z",
  "word_count": 42
}
```

Validation: do not run freeform AI-request no-prose guard against owner save content; do validate size limits, path safety, project membership, and optional conflict token.

Expected errors: invalid IDs, missing note, conflict, content too large, write failure.

### `GET /api/projects/{project_id}/notes/{note_id}/metadata`

Purpose: load one note metadata record.

Request: path parameters only.

Response: full note metadata plus warnings.

Expected errors: invalid IDs, missing metadata, corrupt metadata, project mismatch.

### `PATCH /api/projects/{project_id}/notes/{note_id}/metadata`

Purpose: update owner-authored note metadata.

Request shape:

```json
{
  "title": "Updated note title",
  "note_type": "research",
  "status": "active",
  "tags": ["revision"],
  "linked_chapter_ids": ["chapter_001"],
  "linked_scene_ids": ["scene_001"],
  "owner_notes": "Owner-authored metadata note"
}
```

Response: updated note metadata.

Validation: cannot mutate `project_id`, `note_id`, or `content_path` into unsafe paths; linked IDs must be safe and should warn if targets are missing.

Expected errors: invalid IDs, missing metadata, unsupported metadata version, invalid references, write conflict, write failure.

### `GET /api/projects/{project_id}/materials`

Purpose: list material metadata.

Request: optional query parameters may include `type`, `status`, `tag`, `source_kind`, `license_status`, `linked_chapter_id`, `linked_scene_id`, and `updated_after`.

Response shape:

```json
{
  "project_id": "example",
  "materials": [
    {
      "material_id": "material_001",
      "title": "Research Material",
      "material_type": "text_reference",
      "status": "draft",
      "source_kind": "owner_text",
      "license_status": "owner_provided",
      "updated_at": "2026-06-08T00:00:00Z",
      "warnings": []
    }
  ],
  "warnings": []
}
```

Validation: should not fetch external URLs or open local reference paths during listing.

Expected errors: invalid `project_id`, missing project, unreadable materials directory, corrupt metadata.

### `POST /api/projects/{project_id}/materials`

Purpose: create an empty owner-editable material body plus metadata, or a reference-only material metadata record when explicitly requested.

Request shape:

```json
{
  "title": "Research Material",
  "material_type": "text_reference",
  "status": "draft",
  "source_kind": "owner_text",
  "source_url": null,
  "source_citation": null,
  "license_status": "owner_provided",
  "tags": []
}
```

Response: created material metadata and initial content state.

Validation: generated material ID must be collision-free; URL and citation are metadata only; no web fetch; no binary import.

Expected errors: invalid `project_id`, duplicate/generated ID collision, invalid metadata, unsafe local path metadata, write failure.

### `GET /api/projects/{project_id}/materials/{material_id}`

Purpose: load owner-authored or owner-provided material body content.

Request: path parameters only.

Response shape:

```json
{
  "project_id": "example",
  "material_id": "material_001",
  "content": "Owner-provided material text",
  "metadata": {
    "title": "Research Material",
    "material_type": "text_reference",
    "status": "draft"
  },
  "warnings": []
}
```

Validation: content is stored project material, not assistant output.

Expected errors: invalid IDs, missing material, unreadable content, corrupt metadata.

### `PUT /api/projects/{project_id}/materials/{material_id}`

Purpose: save owner-authored or owner-provided material Markdown/text content.

Request shape:

```json
{
  "content": "Owner-provided material text",
  "last_known_updated_at": "2026-06-08T00:00:00Z"
}
```

Response shape:

```json
{
  "project_id": "example",
  "material_id": "material_001",
  "saved": true,
  "updated_at": "2026-06-08T00:00:00Z"
}
```

Validation: do not run freeform AI-request no-prose guard against owner save content; do validate size limits, path safety, project membership, license/provenance metadata presence where required, and optional conflict token.

Expected errors: invalid IDs, missing material, conflict, content too large, write failure.

### `GET /api/projects/{project_id}/materials/{material_id}/metadata`

Purpose: load one material metadata record.

Request: path parameters only.

Response: full material metadata plus warnings.

Expected errors: invalid IDs, missing metadata, corrupt metadata, project mismatch.

### `PATCH /api/projects/{project_id}/materials/{material_id}/metadata`

Purpose: update owner-authored material metadata.

Request shape:

```json
{
  "title": "Updated material title",
  "material_type": "research",
  "status": "active",
  "tags": ["reference"],
  "source_kind": "research_link",
  "source_url": "https://example.invalid/source",
  "source_citation": "Owner-entered citation",
  "license_status": "reference_only",
  "usage_restrictions": ["do_not_train"],
  "owner_notes": "Owner-authored metadata note"
}
```

Response: updated material metadata.

Validation: cannot mutate `project_id`, `material_id`, or `content_path` into unsafe paths; URLs are metadata only; local paths are metadata only and must not be opened blindly; linked IDs must be safe and should warn if targets are missing.

Expected errors: invalid IDs, missing metadata, unsupported metadata version, invalid references, unsafe URL/local path metadata, write conflict, write failure.

### `GET /api/projects/{project_id}/notes-materials/search`

Purpose: local deterministic search across note/material metadata and optionally body text.

Request query parameters:

```text
q=watchtower
kind=all|notes|materials
type=research
status=active
tag=reference
include_body=true
```

Response shape:

```json
{
  "project_id": "example",
  "query": "watchtower",
  "results": [
    {
      "result_type": "note",
      "id": "note_001",
      "title": "Planning Note",
      "matched_fields": ["title", "body"],
      "snippet": "short owner-authored excerpt",
      "warnings": []
    }
  ],
  "warnings": []
}
```

Validation: no semantic search, no model call, no generated summary, no extraction, no mutation.

Expected errors: invalid `project_id`, invalid query/filter values, search index corruption if a future index exists, unreadable metadata.

## 12. Invalid and Corrupt State Handling

Future implementation should make invalid state visible and recoverable where safe.

| State | Behavior |
| --- | --- |
| Missing `notes/` directory | Do not block opening project; show empty notes state; create folder only through explicit future create action. |
| Missing `note_metadata/` directory | Treat existing note Markdown as legacy/recoverable if discovered by Notes page; do not create metadata silently during library listing. |
| Missing `materials/` directory | Do not block opening project; show empty materials state; create folder only through explicit future create action. |
| Missing `material_metadata/` directory | Treat existing material Markdown as legacy/recoverable if discovered by Materials page; do not create metadata silently during library listing. |
| Corrupt note metadata JSON | Keep body loadable only if safe; show metadata warning; never rewrite silently. |
| Corrupt material metadata JSON | Keep body loadable only if safe; show metadata warning; never rewrite silently. |
| Metadata project mismatch | Block normal metadata save; show recovery/help state. |
| Filename/ID mismatch | Block normal write; show warning; do not rename silently. |
| Unsafe note/material filename | Ignore or quarantine in warning state; do not open through normal route. |
| Metadata exists without body | Show reference-only or missing-body warning depending on type; do not infer content. |
| Body exists without metadata | Show legacy/recoverable warning; do not treat as canon. |
| Broken linked chapter/scene/candidate/memory ID | Show broken-link warning; preserve link until owner edits. |
| Unsupported metadata version | Show needs-migration warning; do not normal-save until migration is approved. |
| Unreadable file | Show warning without leaking sensitive host paths. |

Recovery must be explicit. The app must not silently rewrite identity fields, delete files, import unknown files as canon, fetch external content, create OMI records, or call AI to repair content.

## 13. Future Extraction Implications

Notes/materials may be source material for future extraction, but extraction is not part of WORKSPACE-006 implementation.

Rules:

- Extraction should run only when the owner chooses or a later approved policy allows it.
- Extraction source text must be owner-authored or owner-provided note/material text.
- Extraction output becomes OMI candidates.
- Extraction must not modify note body text.
- Extraction must not modify material body text.
- Extraction must not modify approved memory/canon without future owner promotion.
- Extraction must not write `bible.json` or `storyform.json` as truth.
- Extraction must not create training JSONL or update `training/data/dataset_manifest.json`.
- Notes/materials should provide source IDs and evidence spans for candidate provenance.
- External/reference materials require license/provenance caution before analysis output is used.

Minimum future provenance support:

```json
{
  "source_type": "note",
  "project_id": "example",
  "note_id": "note_001",
  "source_path": "notes/note_001.md",
  "source_hash": "sha256:...",
  "evidence": [
    {
      "quote": "short owner-authored excerpt",
      "start_offset": 0,
      "end_offset": 42
    }
  ]
}
```

For materials, provenance should also include source kind, citation, license status, usage restrictions, and whether the excerpt is owner-created or reference-only.

Evidence excerpts must stay short and source-grounded. They are not generated story prose.

## 14. Future Tests

Future implementation should include tests for:

- Create note.
- Create material.
- Save/reload owner-authored note body.
- Save/reload owner-authored material body.
- Save/reload note metadata.
- Save/reload material metadata.
- Empty note behavior.
- Empty material behavior.
- Invalid `note_id` rejected.
- Invalid `material_id` rejected.
- Path traversal rejected.
- Duplicate IDs rejected.
- Corrupt note metadata handled safely.
- Corrupt material metadata handled safely.
- Body-without-metadata handled as legacy/recoverable.
- Metadata-without-body handled safely.
- Broken links displayed safely.
- Local search does not call model/Ollama.
- Local search does not create summaries.
- Local search does not trigger extraction.
- Owner-authored body save not blocked by no-prose guard.
- No AI prose-generation controls exposed.
- No OMI promotion during save/load/search.
- No memory/canon mutation during save/load/search.
- No `bible.json` or `storyform.json` truth mutation during note/material operations.
- No JSONL/training writes.
- `training/data/dataset_manifest.json` unchanged.
- External/reference material is not treated as training data by default.

## 15. Deferred Decisions

Deferred to future implementation tasks:

- Whether body search should be eager scan, cached index, or optional per-query scan.
- Whether to add rebuildable `notes/index.json` or `materials/index.json`.
- Whether manual ordering is needed beyond updated/title/ID sort.
- Exact status enum beyond first-version labels.
- Exact note/material type enum after UI design.
- Exact conflict detection strategy: timestamp, content hash, revision counter, or hybrid.
- Whether word count is updated on every body save or lazily.
- Whether reference-only materials require a body file.
- Safe policy for opening local reference paths.
- Binary attachment support.
- OCR/import pipeline.
- Web clipping/fetching.
- External sync.
- License/provenance review workflow for reference materials.
- Browser/manual acceptance checklist for implemented Notes/Materials page.

## 16. Implementation Non-Goals

WORKSPACE-006 does not implement:

- Backend note/material routes.
- Frontend Notes/Materials UI.
- Runtime note/material files under `projects/`.
- Binary attachments.
- OCR/import pipeline.
- Web fetching.
- External sync.
- Extractor logic.
- Dramatica-specific logic.
- OMI records.
- Memory/canon runtime files.
- JSONL records.
- Training or fine-tuning.
- Ollama/live model verification.
- Package/dependency changes.

