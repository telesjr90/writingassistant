# WORKSPACE-005: Chapter and Scene Data Model Spec

Status: Documentation-only planning handoff. Runtime implementation is future work.

Product working name: Dramatica-Informed Writing Assistant.

Current priority: Pre-Dramatica Project Workspace Foundation.

Related planning:

- WORKSPACE-001: `docs/roadmap/project_workspace_foundation_spec.md`
- WORKSPACE-002: `docs/roadmap/project_creation_flow_spec.md`
- WORKSPACE-003: `docs/roadmap/project_selector_library_spec.md`
- WORKSPACE-004: `docs/roadmap/omi_guided_project_creation_spec.md`
- Project file model: `docs/roadmap/project_file_model.md`

## 1. Purpose

The chapter and scene data model should let the writer organize, edit, save, reload, and navigate owner-authored prose inside local projects before any Dramatica-specific layer is implemented.

The first implementation should support:

- Chapters containing ordered scenes.
- Standalone scenes when a scene has not been assigned to a chapter.
- Compatibility with current Markdown scene files under `projects/{project_id}/scenes/{scene_id}.md`.
- Separate metadata JSON files for scene organization, navigation, and future analysis support.
- Safe save/reload behavior for owner-authored prose.
- Future candidate extraction from owner-authored text.
- Future navigation, continuity, and timeline features through metadata and candidate provenance.
- No Dramatica-specific requirements in the chapter/scene storage contract.

The model must not introduce any AI prose-writing path. The application may store, edit, and organize owner-authored prose. The AI must never write, rewrite, continue, imitate, polish, improve, or extend story prose.

Standard refusal message:

```text
I can analyze structure and ask diagnostic questions, but I cannot write or rewrite story prose.
```

## 2. Recommended Storage Layout

The recommended first implementation layout is:

```text
projects/{project_id}/
  chapters/
    {chapter_id}.json
  scenes/
    {scene_id}.md
  scene_metadata/
    {scene_id}.json
```

Rules:

- Scene prose remains in `scenes/{scene_id}.md` as owner-authored Markdown.
- Scene metadata lives in `scene_metadata/{scene_id}.json`.
- Chapter records live in `chapters/{chapter_id}.json`.
- Notes/materials are separate workspace content defined by WORKSPACE-006 and must not be stored inside chapter or scene metadata.
- Shared editor save/reload behavior for scene bodies is defined by WORKSPACE-007.
- Chapter records store chapter-level metadata and scene ordering.
- `chapter.scene_ids` is the canonical first-version scene ordering model.
- `scene_metadata.chapter_id` may exist as a consistency aid, filter aid, and recovery signal, but it must not be the only ordering source.
- Existing scene files such as `projects/example/scenes/{scene_id}.md` remain compatible.
- Full scene/chapter prose should not be read just to list projects in the Project Library.
- Project Overview recent-document and count behavior is defined by WORKSPACE-008 and should use metadata rather than full body reads.
- Metadata files may be read for chapter/scene pages, but prose should be loaded only when opening or previewing a scene.

### Compatibility With Existing Scene Files

Current projects may have scene Markdown without chapter records or scene metadata. Future implementation should treat these as compatible legacy standalone scenes:

- List the scene by `scene_id`.
- Treat `chapter_id` as `null` until assigned.
- Create missing metadata only through an explicit owner action or implementation-defined migration step.
- Do not rewrite scene prose during metadata repair.
- Do not infer canon from scene file names.

## 3. Chapter Record Schema

Future chapter records should use one JSON file per chapter:

```text
projects/{project_id}/chapters/{chapter_id}.json
```

Recommended fields:

```json
{
  "metadata_version": 1,
  "project_id": "example",
  "chapter_id": "chapter_001",
  "title": "Chapter title",
  "order_index": 0,
  "scene_ids": ["scene_001"],
  "status": "draft",
  "owner_notes": "",
  "created_at": "2026-06-07T00:00:00Z",
  "updated_at": "2026-06-07T00:00:00Z",
  "summary_candidate_id": null,
  "approved_navigation_summary": null,
  "tags": [],
  "provenance": {
    "created_by": "owner",
    "creation_method": "blank",
    "source": "manual"
  }
}
```

Field rules:

| Field | Required | Meaning |
| --- | --- | --- |
| `metadata_version` | Yes | Version of the chapter metadata schema. |
| `project_id` | Yes | Owning project. Must match the project folder/project metadata. |
| `chapter_id` | Yes | Filesystem-safe chapter identifier. Must match the filename stem. |
| `title` | Yes | Owner-authored display title. Empty string is allowed for untitled chapters. |
| `order_index` | Yes | Chapter order among chapters. First implementation may use zero-based integers. |
| `scene_ids` | Yes | Ordered list of scene IDs in this chapter. Canonical scene order for the chapter. |
| `status` | Yes | Owner-controlled lifecycle label such as `draft`, `active`, `revising`, `complete`, `archived`. |
| `owner_notes` | Yes | Owner-authored chapter notes. |
| `created_at` | Yes | Creation timestamp. |
| `updated_at` | Yes | Last metadata update timestamp. |
| `summary_candidate_id` | No | Optional reference to an OMI navigation-summary candidate. |
| `approved_navigation_summary` | No | Optional owner-authored or owner-approved navigation aid. |
| `tags` | No | Owner-authored organization tags. |
| `provenance` | Yes | Metadata about how the record was created or imported. |

Boundary rules:

- `title`, `owner_notes`, and `tags` are owner-authored fields.
- `approved_navigation_summary` is optional and must be owner-authored or explicitly owner-approved.
- `summary_candidate_id` may point to candidate metadata only; it does not make the summary approved.
- Chapter records must not contain generated chapter prose.
- Empty chapters are valid.
- Chapter metadata is not approved story canon by itself.

## 4. Scene Metadata Schema

Future scene metadata should use one JSON file per scene:

```text
projects/{project_id}/scene_metadata/{scene_id}.json
```

Scene prose remains separate:

```text
projects/{project_id}/scenes/{scene_id}.md
```

Recommended metadata fields:

```json
{
  "metadata_version": 1,
  "project_id": "example",
  "scene_id": "scene_001",
  "chapter_id": "chapter_001",
  "title": "Scene title",
  "order_index": 0,
  "status": "draft",
  "pov_character_id": null,
  "location_ids": [],
  "timeline_position": null,
  "owner_notes": "",
  "created_at": "2026-06-07T00:00:00Z",
  "updated_at": "2026-06-07T00:00:00Z",
  "content_path": "scenes/scene_001.md",
  "word_count": 0,
  "summary_candidate_id": null,
  "approved_navigation_summary": null,
  "tags": [],
  "provenance": {
    "created_by": "owner",
    "creation_method": "blank",
    "source": "manual"
  }
}
```

Field rules:

| Field | Required | Meaning |
| --- | --- | --- |
| `metadata_version` | Yes | Version of the scene metadata schema. |
| `project_id` | Yes | Owning project. Must match the project folder/project metadata. |
| `scene_id` | Yes | Filesystem-safe scene identifier. Must match metadata filename and Markdown filename stem. |
| `chapter_id` | No | Owning chapter, or `null` for standalone/unassigned scenes. |
| `title` | Yes | Owner-authored display title. Empty string is allowed for untitled scenes. |
| `order_index` | No | Consistency/display aid. Chapter `scene_ids` remains canonical for ordered chapter scenes. |
| `status` | Yes | Owner-controlled lifecycle label such as `draft`, `active`, `revising`, `complete`, `archived`. |
| `pov_character_id` | No | Future optional link. Candidate-backed unless owner-approved. |
| `location_ids` | No | Future optional location links. Candidate-backed unless owner-approved. |
| `timeline_position` | No | Future optional timeline position. Candidate-backed unless owner-approved. |
| `owner_notes` | Yes | Owner-authored scene notes. |
| `created_at` | Yes | Creation timestamp. |
| `updated_at` | Yes | Last metadata update timestamp. |
| `content_path` | Yes | Relative path to scene Markdown. Must remain inside the project. |
| `word_count` | No | Derived count from owner-authored scene text; not owner truth or canon. |
| `summary_candidate_id` | No | Optional reference to an OMI navigation-summary candidate. |
| `approved_navigation_summary` | No | Optional owner-authored or owner-approved navigation aid. |
| `tags` | No | Owner-authored organization tags. |
| `provenance` | Yes | Metadata about how the record was created or imported. |

Boundary rules:

- Scene prose is stored only in `scenes/{scene_id}.md`.
- Scene metadata must not contain generated scene text, dialogue, continuation, rewrite, polish, or style imitation.
- `word_count` may be derived automatically from the Markdown content, but it must be treated as derived navigation metadata.
- Future POV, location, and timeline links are optional and candidate-backed unless explicitly owner-approved.
- `approved_navigation_summary` must not be unapproved AI prose.
- Empty scenes are valid when intentionally saved.

## 5. ID Strategy

Chapter and scene IDs must be stable filesystem-safe components.

Recommended first implementation:

- Backend-generated IDs by default.
- Sequential ID pattern: `chapter_001`, `chapter_002`, `scene_001`, `scene_002`.
- Preserve existing scene IDs such as `scene_001`.
- Keep owner-visible titles separate from IDs.
- Do not rename IDs when titles change.
- Do not migrate `project_id`, `chapter_id`, or `scene_id` from display title changes.

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

- New chapter/scene creation must fail closed if the generated or requested ID already exists.
- Server-side ID generation should find the next available sequential ID.
- Client-side previews are advisory only.
- The backend must revalidate every ID and collision before writing files.

Reserved names:

- Reject names that would conflict with project folders or metadata such as `project`, `project_json`, `chapters`, `scenes`, `scene_metadata`, `memory`, `omi`, `bible`, `storyform`, `index`, `con`, `nul`, `prn`, `aux`, `com1`, and `lpt1`.
- Keep the reserved-name list aligned with project creation and backend path-safety helpers.

## 6. Ordering and Movement Behavior

### Chapter Order

First implementation should use `chapter.order_index` as the canonical chapter order.

Rules:

- List chapters by ascending `order_index`.
- If `order_index` is missing or duplicated, show a health warning.
- Fallback display order for damaged metadata should be title, then `chapter_id`.
- Reordering chapters should update all affected `order_index` values together.
- Failed reorder must preserve the previous chapter files.

A future `chapters/index.json` may be considered only if chapter counts grow or multi-file ordering becomes hard to manage. If added, it should be rebuildable navigation metadata, not story truth.

### Scene Order Within Chapters

First implementation should use `chapter.scene_ids` as canonical order for scenes inside a chapter.

Rules:

- Scene order in a chapter is the order of IDs in `chapter.scene_ids`.
- `scene_metadata.order_index` may mirror this order for display and recovery but is not the canonical source.
- A scene with `chapter_id: null` and absent from all chapter `scene_ids` is standalone/unassigned.
- A scene with metadata but missing Markdown content is an invalid or recoverable scene state, not approved canon.
- A Markdown scene without metadata should appear as a legacy standalone scene with a warning.

### Moving Scenes Between Chapters

Moving a scene should be treated as an atomic metadata operation:

- Remove `scene_id` from the source chapter `scene_ids`.
- Insert `scene_id` into the target chapter `scene_ids` at the requested position.
- Update `scene_metadata.chapter_id`.
- Update `scene_metadata.order_index` where used.
- Update affected `updated_at` timestamps.
- Preserve the scene Markdown content unchanged.

If any write fails, implementation should preserve or restore the previous metadata state and show an error. It must not delete scene prose.

### Inconsistent Ordering Recovery

Invalid states and recommended behavior:

| State | Future behavior |
| --- | --- |
| `chapter.scene_ids` references missing scene Markdown | Show warning; keep chapter readable; do not create prose; offer metadata repair later. |
| `chapter.scene_ids` references missing scene metadata | Show warning; allow read-only listing from ID; offer metadata creation later. |
| Scene metadata points to chapter A, but chapter B lists the scene | Show warning; use `chapter.scene_ids` for display order; require explicit repair before reorder. |
| Scene appears in multiple chapters | Show duplicate-membership warning; block normal move/reorder until owner chooses one location. |
| Duplicate scene ID appears twice in one `scene_ids` list | Show invalid ordering warning; display first occurrence only with warning; block reorder until repaired. |
| Scene metadata has `chapter_id` but no chapter lists it | Show as orphan/mismatch; allow owner to assign or clear chapter reference. |
| Scene Markdown exists without metadata | Show as legacy standalone scene with missing metadata warning. |
| Metadata exists without Markdown | Show as invalid/recoverable; do not treat as saved prose. |

No repair should silently rewrite project identity, create story prose, import unknown files as canon, or delete files.

## 7. Save and Reload Behavior

Owner-authored scene prose save is allowed. The no-prose guard must not treat scene save content as an AI prose-generation request.

Rules:

- Saving `scenes/{scene_id}.md` stores owner-authored text.
- Saving metadata updates `chapters/{chapter_id}.json` or `scene_metadata/{scene_id}.json`.
- Prose save and metadata save may be separate route operations.
- Scene prose save must never call a model.
- Scene prose save must never create OMI candidates by default.
- Scene prose save must never promote OMI candidates or write approved memory/canon.
- Save failures must preserve the current editor content in memory/UI.
- Reload must not overwrite unsaved edits without confirmation.
- Scene switch and project switch should warn when current owner-authored edits are unsaved.
- Empty scene save/load is valid when intentional.
- Saving chapter/scene metadata must not write generated prose into the scene Markdown.

Recommended first-version concurrency behavior:

- Use last-loaded metadata timestamps or content hashes as optional conflict detection if cheap.
- If a conflict is detected, block overwrite and ask the owner to reload, save as a copy, or discard local changes.
- Do not silently merge prose.

## 8. Chapter and Scene UI Planning

Future UI surfaces:

- Chapters/Scenes page.
- Chapter list or sidebar.
- Scene list nested under each chapter.
- Standalone/unassigned scenes section.
- Create chapter action.
- Create scene action.
- Rename chapter action.
- Rename scene action.
- Reorder chapters.
- Reorder scenes within a chapter.
- Move scene between chapters.
- Scene editor.
- Scene metadata panel.
- Chapter metadata panel.
- Safe empty states for no chapters, empty chapter, no scene selected, and intentionally empty scene.
- Unsaved change indicators.
- Invalid/corrupt metadata warning states.

UI boundaries:

- No AI writing buttons.
- No "write opening", "write scene", "continue", "rewrite", "polish", "improve", or style imitation controls.
- Future analysis/extraction actions must be clearly labeled as candidate creation or diagnostics only.
- Navigation summaries must be labeled as owner-approved navigation aids or candidates, not replacement prose.
- Empty chapter/scene actions create organization containers and owner-editable files only.

## 9. API Planning

These routes are future planning only. Do not implement them during WORKSPACE-005.

Every route must validate `project_id`; chapter routes must validate `chapter_id`; scene routes must validate `scene_id`. IDs must align with backend safe path helpers and reject traversal, absolute paths, slashes, backslashes, empty values, dot, dot-dot, leading dots, and reserved names.

Every route must preserve the no-prose and candidate/canon boundaries:

- Owner-authored prose may be saved through explicit scene save routes.
- API routes must not generate, rewrite, continue, imitate, polish, improve, or extend prose.
- Listing, loading, saving, and reordering must not call Ollama or any model.
- Listing, loading, saving, and reordering must not create JSONL/training records.
- Listing, loading, saving, and reordering must not create OMI promotion records.
- Listing, loading, saving, and reordering must not write approved memory/canon.

### `GET /api/projects/{project_id}/chapters`

Purpose: list chapter metadata in order.

Request: path parameter only.

Response shape:

```json
{
  "project_id": "example",
  "chapters": [
    {
      "chapter_id": "chapter_001",
      "title": "Chapter title",
      "order_index": 0,
      "scene_ids": ["scene_001"],
      "status": "draft",
      "updated_at": "2026-06-07T00:00:00Z",
      "warnings": []
    }
  ],
  "warnings": []
}
```

Expected errors: invalid `project_id`, missing project, unreadable chapters directory, corrupt metadata.

### `POST /api/projects/{project_id}/chapters`

Purpose: create an empty chapter record.

Request shape:

```json
{
  "title": "Chapter title",
  "status": "draft",
  "after_chapter_id": null,
  "tags": []
}
```

Response: created chapter record.

Validation: title is owner-authored metadata; generated ID must be collision-free; tags are owner-authored labels.

Expected errors: invalid `project_id`, duplicate/generated ID collision, invalid title length, write failure.

### `GET /api/projects/{project_id}/chapters/{chapter_id}`

Purpose: load one chapter metadata record.

Request: path parameters only.

Response: full chapter record plus warnings.

Expected errors: invalid IDs, missing chapter, corrupt metadata, project mismatch.

### `PATCH /api/projects/{project_id}/chapters/{chapter_id}`

Purpose: update owner-authored chapter metadata.

Request shape:

```json
{
  "title": "Updated title",
  "status": "revising",
  "owner_notes": "Owner-authored note",
  "tags": ["revision"]
}
```

Response: updated chapter record.

Validation: cannot write prose body; cannot mutate `project_id` or `chapter_id`; cannot approve candidate summaries without explicit future owner-approval path.

Expected errors: invalid IDs, missing chapter, unsupported metadata version, write conflict, write failure.

### `GET /api/projects/{project_id}/scenes`

Purpose: list scenes with lightweight metadata.

Request: optional filters may include `chapter_id`, `status`, or `include_unassigned`.

Response shape:

```json
{
  "project_id": "example",
  "scenes": [
    {
      "scene_id": "scene_001",
      "chapter_id": "chapter_001",
      "title": "Scene title",
      "status": "draft",
      "content_path": "scenes/scene_001.md",
      "word_count": 0,
      "updated_at": "2026-06-07T00:00:00Z",
      "warnings": []
    }
  ],
  "warnings": []
}
```

Validation: should not read full scene prose just to list scenes unless deriving a cheap word count is explicitly needed and safe.

Expected errors: invalid `project_id`, missing project, unreadable scenes directory, corrupt metadata.

### `POST /api/projects/{project_id}/scenes`

Purpose: create an empty owner-editable scene Markdown file plus metadata.

Request shape:

```json
{
  "title": "Scene title",
  "chapter_id": "chapter_001",
  "after_scene_id": null,
  "status": "draft",
  "tags": []
}
```

Response: created scene metadata and initial content state.

Validation: generated scene ID must be collision-free; optional chapter must exist; initial content is empty unless owner provided explicit text in a future create-and-save route.

Expected errors: invalid IDs, missing chapter, duplicate/generated ID collision, write failure, inconsistent ordering.

### `GET /api/projects/{project_id}/scenes/{scene_id}`

Purpose: load owner-authored scene Markdown content.

Request: path parameters only.

Response shape:

```json
{
  "project_id": "example",
  "scene_id": "scene_001",
  "content": "Owner-authored scene text",
  "metadata": {
    "title": "Scene title",
    "chapter_id": "chapter_001",
    "status": "draft"
  },
  "warnings": []
}
```

Validation: content is owner-authored storage, not assistant output.

Expected errors: invalid IDs, missing scene, unreadable content, corrupt metadata.

### `PUT /api/projects/{project_id}/scenes/{scene_id}`

Purpose: save owner-authored scene Markdown content.

Request shape:

```json
{
  "content": "Owner-authored scene text",
  "last_known_updated_at": "2026-06-07T00:00:00Z"
}
```

Response shape:

```json
{
  "project_id": "example",
  "scene_id": "scene_001",
  "saved": true,
  "updated_at": "2026-06-07T00:00:00Z",
  "word_count": 123
}
```

Validation: do not run freeform AI-request no-prose guard against owner save content; do validate size limits, path safety, project membership, and optional conflict token.

Expected errors: invalid IDs, missing scene, conflict, content too large, write failure.

### `GET /api/projects/{project_id}/scenes/{scene_id}/metadata`

Purpose: load one scene metadata record.

Request: path parameters only.

Response: full scene metadata plus warnings.

Expected errors: invalid IDs, missing metadata, corrupt metadata, project mismatch.

### `PATCH /api/projects/{project_id}/scenes/{scene_id}/metadata`

Purpose: update owner-authored scene metadata.

Request shape:

```json
{
  "title": "Updated title",
  "status": "revising",
  "owner_notes": "Owner-authored note",
  "tags": ["revision"],
  "pov_character_id": null,
  "location_ids": []
}
```

Response: updated scene metadata.

Validation: cannot mutate `project_id`, `scene_id`, or `content_path` into unsafe paths; future POV/location/timeline links remain candidate-backed unless approved.

Expected errors: invalid IDs, missing metadata, unsupported metadata version, invalid references, write conflict, write failure.

### `POST /api/projects/{project_id}/chapters/{chapter_id}/reorder-scenes`

Purpose: reorder scenes within a chapter or move scenes into the chapter.

Request shape:

```json
{
  "scene_ids": ["scene_001", "scene_002"]
}
```

Response: updated chapter record and updated scene metadata summaries.

Validation: list must contain unique safe scene IDs; all listed scenes must exist; duplicate membership across chapters must be resolved explicitly.

Expected errors: invalid IDs, missing chapter, missing scene, duplicate scene IDs, inconsistent ordering, write failure.

### `POST /api/projects/{project_id}/reorder-chapters`

Purpose: reorder chapters.

Request shape:

```json
{
  "chapter_ids": ["chapter_001", "chapter_002"]
}
```

Response: updated chapter summaries in order.

Validation: list must contain unique known chapter IDs; no unknown chapter may be silently dropped.

Expected errors: invalid `project_id`, invalid chapter IDs, missing chapter, duplicate chapter ID, write failure.

## 10. Future Extraction Implications

Chapter/scene structure should support future candidate extraction, but extraction is not part of WORKSPACE-005 implementation.

Rules:

- Extraction should run manually first unless a later decision changes the trigger policy.
- Extraction source text must be owner-authored chapter/scene/note/material text.
- Extraction output becomes OMI candidates.
- Extraction must not modify scene prose.
- Extraction must not modify chapter metadata except through explicit owner-approved metadata actions.
- Extraction must not write approved memory/canon without future owner promotion.
- Extraction must not write `bible.json` or `storyform.json` as truth.
- Extraction must not create training JSONL or update `training/data/dataset_manifest.json`.
- Candidate provenance should include `project_id`, `chapter_id`, `scene_id`, source path, source hash, evidence span, locator strategy, extraction time, and tool/model identity if any.

Minimum future provenance support:

```json
{
  "source_type": "scene",
  "project_id": "example",
  "chapter_id": "chapter_001",
  "scene_id": "scene_001",
  "source_path": "scenes/scene_001.md",
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

Evidence excerpts must stay short and source-grounded. They are not generated story prose.

## 11. Invalid and Corrupt State Handling

Future implementation should make invalid state visible and recoverable where safe.

| State | Behavior |
| --- | --- |
| Missing `chapters/` directory | Do not block opening project; show no chapters/legacy mode. |
| Missing `scenes/` directory | Show no scenes; allow future create action if project metadata is valid. |
| Missing `scene_metadata/` directory | Treat existing Markdown scenes as legacy standalone scenes with warning. |
| Corrupt chapter JSON | Exclude from normal editing; show warning/recovery state; never auto-delete. |
| Corrupt scene metadata JSON | Keep scene Markdown loadable if safe; show metadata warning; never rewrite silently. |
| Metadata project mismatch | Block normal metadata save; show recovery/help state. |
| Filename/ID mismatch | Block normal write; show warning; do not rename silently. |
| Unsafe chapter/scene filename | Ignore or quarantine in warning state; do not open through normal route. |
| Duplicate chapter IDs | Impossible if filenames unique, but duplicate internal IDs should be warning/blocking metadata corruption. |
| Duplicate scene IDs | Block creation; duplicate references in order lists require explicit repair. |
| Unsupported metadata version | Show needs-migration warning; do not normal-save until migration is approved. |
| Unreadable file | Show warning without leaking sensitive host paths. |

Recovery must be explicit. The app must not silently rewrite identity fields, delete files, import unknown files as canon, or call AI to repair prose.

## 12. Future Tests

Future implementation should include tests for:

- Create chapter.
- Create scene under chapter.
- Save/reload owner-authored scene prose.
- Save/reload intentionally empty scene.
- Save/reload chapter metadata.
- Scene metadata references chapter.
- `chapter.scene_ids` ordering works.
- Moving scene between chapters updates ordering safely.
- Invalid `chapter_id` rejected.
- Invalid `scene_id` rejected.
- Path traversal rejected.
- Duplicate IDs rejected.
- Corrupted chapter metadata handled safely.
- Corrupted scene metadata handled safely.
- Missing scene metadata handled as legacy/recoverable.
- Missing scene Markdown handled as invalid/recoverable.
- Unsaved edits warn before scene switch.
- Unsaved edits warn before project switch.
- Owner-authored prose save not blocked by no-prose guard.
- No AI prose-generation controls exposed in Chapters/Scenes UI.
- No model/Ollama call during list/load/save/reorder.
- No OMI promotion during list/load/save/reorder.
- No memory/canon mutation during list/load/save/reorder.
- No `bible.json` or `storyform.json` truth mutation during chapter/scene operations.
- No JSONL/training writes.
- `training/data/dataset_manifest.json` unchanged.

## 13. Deferred Decisions

Deferred to future implementation tasks:

- Exact server-side transaction helper for multi-file scene moves.
- Whether chapter reorder needs a future rebuildable `chapters/index.json`.
- Whether to support owner-edited IDs after creation. First recommendation is stable generated IDs only.
- Exact status enum beyond first-version labels.
- Exact conflict detection strategy: timestamp, content hash, revision counter, or hybrid.
- Whether word count is updated on every scene save or lazily on listing.
- Whether navigation summaries are owner-authored fields, approved OMI candidates, or both in the first UI.
- Whether extraction trigger is manual-only or later hybrid after save.
- Migration details for existing projects with only `scenes/*.md`.
- Browser/manual acceptance checklist for the implemented Chapters/Scenes page.

## 14. Implementation Non-Goals

WORKSPACE-005 does not implement:

- Backend chapter routes.
- Scene model changes.
- Frontend editor changes.
- Project creation.
- Project selector/library UI.
- OMI-guided project creation.
- Extractor logic.
- Dramatica-specific logic.
- Runtime project files under `projects/`.
- OMI records.
- Memory/canon runtime files.
- JSONL records.
- Training or fine-tuning.
- Ollama/live model verification.
- Package/dependency changes.
