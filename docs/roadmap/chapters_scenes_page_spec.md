# WORKSPACE-009: Chapters / Scenes Page Spec

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
- WORKSPACE-007: `docs/roadmap/user_authored_document_editor_workflow_spec.md`
- WORKSPACE-008: `docs/roadmap/project_overview_page_spec.md`
- Project file model: `docs/roadmap/project_file_model.md`

## 1. Purpose

The Chapters / Scenes page should be the first dedicated writing-organization page in the project workspace. It should let the owner create, select, edit, save, reload, rename, reorder, and organize chapters and scenes while preserving owner authorship.

The page should:

- Let the owner create, select, edit, save, reload, rename, reorder, and organize chapters and scenes.
- Support owner-authored prose editing only.
- Preserve the chapter/scene storage model from WORKSPACE-005.
- Use the shared editor workflow from WORKSPACE-007.
- Support intentionally empty chapters and scenes.
- Show safe metadata and warnings.
- Keep analysis/candidate panels separate from editor content.
- Avoid Dramatica-specific assumptions.
- Avoid model/Ollama calls in the first implementation.

The application may store, edit, and organize owner-authored prose, notes, metadata, and materials. The AI must never write, rewrite, continue, imitate, polish, improve, expand, or extend story prose.

Standard refusal message:

```text
I can analyze structure and ask diagnostic questions, but I cannot write or rewrite story prose.
```

## 2. Page Layout

First-version sections:

- Page Header.
- Chapter Sidebar / Chapter List.
- Scene List for Selected Chapter.
- Standalone / Orphan Scene Area if needed.
- Main Scene Editor.
- Scene Metadata Panel.
- Chapter Metadata Panel.
- Status / Warning Area.
- Empty-State Guidance.
- Future Candidate/Analysis Panel Placeholder.

### Page Header

Purpose:

- Identify the active project and the Chapters / Scenes workspace area.
- Provide top-level create and navigation actions.

Data source:

- Active project metadata from `project.json`.
- Page route state.
- Lightweight chapter/scene counts from chapter and scene metadata.

No-prose boundary:

- Header copy is navigation/status text only.
- Do not generate chapter titles, scene titles, summaries, or story prose.

Candidate/canon boundary:

- Chapter/scene metadata is project organization data, not approved canon by itself.
- Candidate counts or warnings must be labeled as candidate-only if shown.

Empty state:

- Show zero chapter/scene counts and safe create actions.

Error state:

- If project identity is invalid, block normal page load and point to project recovery/help.
- If optional chapter/scene metadata is partially unreadable, show degraded state with warnings.

### Chapter Sidebar / Chapter List

Purpose:

- List chapters in project order.
- Let the owner select a chapter, create a chapter, rename metadata, and start reorder operations.

Data source:

- `chapters/{chapter_id}.json` records.
- `chapter.order_index` as first-version chapter order.

No-prose boundary:

- Chapter titles, tags, and owner notes are owner-authored metadata.
- Do not generate chapter prose, summaries, labels, or replacement titles.

Candidate/canon boundary:

- `summary_candidate_id` is candidate-only.
- `approved_navigation_summary` may appear only when owner-authored or owner-approved and must be labeled as a navigation aid, not prose replacement.

Empty state:

- Show a safe create chapter action.
- Empty projects should not auto-create a chapter without owner action.

Error state:

- Corrupt chapter metadata shows a warning row.
- Missing or duplicate `order_index` shows a warning and uses fallback display order.
- Unsupported metadata version shows needs-migration state.

### Scene List for Selected Chapter

Purpose:

- Show ordered scenes in the selected chapter.
- Let the owner select, create, rename, reorder, or move scenes.

Data source:

- Selected chapter `scene_ids`.
- `scene_metadata/{scene_id}.json`.
- `scenes/{scene_id}.md` existence only, not full body content for listing.

No-prose boundary:

- Scene list must not generate summaries.
- Scene list must not parse full scene bodies to synthesize labels.

Candidate/canon boundary:

- Scene metadata is not canon by itself.
- Candidate links are candidate-only.
- Approved navigation summaries must be owner-authored or owner-approved.

Empty state:

- Empty chapter shows create scene action and notes that empty chapters are allowed.

Error state:

- Missing scene body, missing metadata, duplicate IDs, and chapter/metadata mismatches show warnings without deleting or creating prose.

### Standalone / Orphan Scene Area

Purpose:

- Surface scenes that are not assigned to a chapter or have inconsistent chapter membership.
- Preserve compatibility with existing `projects/example/scenes/{scene_id}.md` style scene files.

Data source:

- `scene_metadata.chapter_id: null`.
- Scene Markdown files without metadata.
- Metadata records not listed in any chapter.

No-prose boundary:

- Do not infer prose meaning or story importance from standalone status.
- Do not create summaries.

Candidate/canon boundary:

- Standalone scenes are source documents, not canon records.
- Orphan warnings are metadata health information only.

Empty state:

- Hide the section when there are no standalone/orphan scenes, or show an empty collapsed state.

Error state:

- Mismatched scene membership should block normal move/reorder until explicit repair is available.

### Main Scene Editor

Purpose:

- Let the owner edit and save selected scene prose.

Data source:

- `scenes/{scene_id}.md`.
- Selected scene metadata for title/status display.
- Shared editor state from WORKSPACE-007.

No-prose boundary:

- Editor content is owner-authored prose.
- Saving editor content must not be blocked as an AI prose-generation request.
- AI output must never be inserted into the editor body.

Candidate/canon boundary:

- Scene prose is project source text, not automatically approved memory/canon.
- Future extraction from scene text creates OMI candidates only.

Empty state:

- No selected scene: prompt the owner to select or create a scene.
- Empty selected scene: show that intentionally empty scenes are valid.

Error state:

- Missing scene body is distinct from empty scene body.
- Corrupt metadata may allow body read-only load where safe but should block normal metadata save.

### Scene Metadata Panel

Purpose:

- Show and edit owner-authored scene metadata.

Data source:

- `scene_metadata/{scene_id}.json`.

Editable fields:

- Title.
- Status.
- Tags.
- Owner notes.
- Future owner-approved links where supported.

Read-only/derived fields:

- `scene_id`.
- `project_id`.
- `chapter_id` unless moving through move operation.
- `content_path`.
- `word_count`.
- `created_at`.
- `updated_at`.

No-prose boundary:

- Metadata save must not write scene body prose.
- No generated titles, summaries, notes, dialogue, or scene text.

Candidate/canon boundary:

- Candidate links stay candidates.
- Future POV/location/timeline links are candidate-backed unless owner-approved.

Empty state:

- Untitled scenes are allowed.

Error state:

- Invalid metadata shows warning and blocks metadata save until recovered.

### Chapter Metadata Panel

Purpose:

- Show and edit owner-authored metadata for the selected chapter.

Data source:

- `chapters/{chapter_id}.json`.

Editable fields:

- Title.
- Status.
- Tags.
- Owner notes.

Read-only/derived fields:

- `chapter_id`.
- `project_id`.
- `order_index`.
- `scene_ids` except through reorder/move controls.
- `created_at`.
- `updated_at`.

No-prose boundary:

- Chapter metadata save must not create or generate chapter prose.

Candidate/canon boundary:

- Navigation summaries are owner-approved navigation aids or candidates, not generated story prose.

Empty state:

- Empty chapter metadata remains valid.

Error state:

- Unsupported or corrupt metadata should show a warning and disable unsafe edits.

### Status / Warning Area

Purpose:

- Show page-level load/save/reload/reorder/move warnings and project health states.

Data source:

- API errors.
- Chapter/scene validation.
- Editor dirty/conflict state.

No-prose boundary:

- Warnings are factual status messages only.

Candidate/canon boundary:

- Warnings may mention candidates or canon only as status labels.

Empty state:

- No warnings when clean.

Error state:

- Blocking errors should prevent destructive operations and preserve owner-authored content.

### Empty-State Guidance

Purpose:

- Provide safe next actions when no chapters, no scenes, or no selected document exists.

Data source:

- Chapter/scene counts and selection state.

No-prose boundary:

- Guidance must be operational, not generated story text.
- Do not suggest "generate" actions.

Candidate/canon boundary:

- OMI links must be labeled idea/candidate review.

Empty state:

- Create chapter.
- Create scene.
- Select existing scene.
- Open OMI ideas/candidates.

Error state:

- If metadata is invalid, show recovery/help instead of create prompts that could worsen state.

### Future Candidate/Analysis Panel Placeholder

Purpose:

- Reserve a place for future diagnostics and candidate extraction without mixing AI output into editor content.

Data source:

- None in first implementation, or existing Story Check diagnostics only when explicitly run.

No-prose boundary:

- No generated prose.
- No apply/insert/rewrite controls.

Candidate/canon boundary:

- Future output is diagnostic or OMI candidate-only.
- No auto-promotion to memory/canon.

Empty state:

- Placeholder may be hidden or say future analysis is unavailable.

Error state:

- Analysis errors must not affect scene save/reload.

## 3. Chapter Operations

Future operations:

- Create chapter.
- Select chapter.
- Rename chapter.
- Edit chapter metadata.
- Reorder chapters.
- Archive chapter later.
- Delete chapter later only after explicit future design.
- Handle empty chapter.
- Handle corrupt chapter metadata.
- Handle chapter with missing scene references.

Operation rules:

- Creating a chapter creates metadata only and no prose.
- Chapter IDs should follow WORKSPACE-005 generated stable ID rules.
- Chapter titles and owner notes are owner-authored fields.
- Empty chapters are valid.
- Selecting a chapter should warn if the current selected scene has unsaved owner-authored edits and selection would change the scene/editor state.
- Renaming a chapter changes title metadata only, not `chapter_id`.
- Reordering chapters updates `chapter.order_index` values and preserves previous files on failure.
- Archiving/deleting should not be in the first implementation unless later approved.
- Delete must never be automated by AI.
- Chapter navigation summaries must be owner-authored or owner-approved.
- Corrupt metadata should show warning and avoid destructive repair.
- Missing scene references should be displayed as warnings and not silently removed.

Prohibited chapter operations:

- Generate chapter prose.
- Write a chapter for the owner.
- Expand notes into a chapter.
- Rewrite chapter material.
- Treat unapproved candidate summaries as chapter truth.

## 4. Scene Operations

Future operations:

- Create scene under selected chapter.
- Create standalone scene if allowed.
- Select scene.
- Edit owner-authored scene prose.
- Save scene body.
- Save scene metadata.
- Reload scene.
- Rename scene.
- Reorder scenes within chapter.
- Move scene between chapters.
- Mark scene status.
- Archive scene later.
- Delete scene later only after explicit future design.
- Handle intentionally empty scene.
- Handle corrupt scene metadata.
- Handle missing scene body versus empty scene body.

Operation rules:

- Creating a scene creates an empty owner-editable body and metadata unless a future explicit owner-provided initial content path is designed.
- Scene IDs should follow WORKSPACE-005 generated stable ID rules.
- Scene titles, owner notes, tags, and body text are owner-authored.
- Selecting a scene must use WORKSPACE-007 unsaved-change protections.
- Saving scene body stores owner-authored text only.
- Saving scene metadata should be separate from body save or jointly tracked with explicit `body_dirty` and `metadata_dirty` state.
- Reload must warn before replacing dirty editor content.
- Missing scene body is invalid or recoverable; empty scene body is a valid intentional document.
- Moving a scene must preserve Markdown content unchanged.
- Reordering scenes updates chapter ordering metadata and should not rewrite scene bodies.
- Archiving/deleting should be future-only unless separately approved.

Prohibited scene controls:

- Continue.
- Rewrite.
- Polish.
- Improve.
- Expand.
- Generate dialogue.
- Generate scene.
- Imitate style.
- Insert AI text.
- Apply AI rewrite.

Story Check or future analysis may read selected owner-authored scene source only when explicitly run, and output must display separately as diagnostics/candidates.

## 5. Document / Editor Behavior

The Chapters / Scenes page should use WORKSPACE-007 for editor state and save/reload behavior.

Required editor state concepts:

- `selected_project_id`.
- `selected_document_type: "scene"`.
- `selected_document_id`.
- `selected_chapter_id`.
- `current_editor_content`.
- `last_saved_content`.
- `current_metadata`.
- `last_saved_metadata`.
- `body_dirty`.
- `metadata_dirty`.
- `save_error`.
- `load_error`.
- `last_saved_at`.
- `loaded_updated_at`.
- `server_updated_at`.
- Optional revision/hash fields later.

Required behavior:

- Track body and metadata dirty state separately.
- Show unsaved-change warnings on scene switch, chapter switch, page navigation, project switch, and browser unload.
- Preserve editor content on save failure.
- Update dirty state only after confirmed save.
- Support intentional empty scene saves.
- Distinguish missing scene file from empty scene file.
- Use `updated_at` / `last_saved_at` comparison for first-version conflict detection.
- Do not automatically merge conflicts in the first implementation.
- Do not call a model on page load, save, reload, switch, reorder, or move.
- Do not create OMI candidates by default.
- Do not promote OMI candidates.
- Do not mutate memory/canon, `bible.json`, or `storyform.json`.
- Do not create JSONL/training records.

Recommended switch flow:

1. Owner selects another scene, chapter, page, or project.
2. If `body_dirty` or `metadata_dirty`, show Save / Discard / Cancel.
3. Save attempts the relevant body and metadata saves.
4. Discard clears local dirty changes only after explicit confirmation.
5. Cancel preserves the current editor state.
6. Successful switch clears selected-document analysis state.

## 6. Ordering and Consistency Behavior

The Chapters / Scenes page should use the ordering model from WORKSPACE-005.

Rules:

- `chapter.order_index` is the first-version chapter order.
- `chapter.scene_ids` is the canonical first-version scene order within a chapter.
- `scene_metadata.chapter_id` is a consistency aid, filter aid, and recovery signal.
- `scene_metadata.order_index` may mirror chapter order but is not canonical.
- Moving scenes should update source chapter, target chapter, and scene metadata atomically in future implementation.
- Reordering scenes should validate unique scene IDs.
- Reordering chapters should validate unique chapter IDs and stable order indexes.
- Duplicate IDs must be rejected.
- Path traversal must be rejected.
- Unsafe IDs must be rejected.
- Inconsistent states should show warnings and avoid silent destructive repair.

Recommended inconsistent-state handling:

| State | Page behavior |
| --- | --- |
| Scene listed in chapter but body missing | Show warning; do not treat as empty scene. |
| Scene listed in chapter but metadata missing | Show warning; allow limited display by ID; repair later. |
| Scene metadata points to different chapter | Show mismatch warning; display by `chapter.scene_ids`; block reorder/move until repaired. |
| Scene appears in multiple chapters | Show duplicate-membership warning; block normal move/reorder. |
| Duplicate scene ID in one chapter | Show invalid-order warning; display first occurrence only. |
| Scene metadata has chapter but chapter omits it | Show orphan/mismatch area. |
| Markdown exists without metadata | Show as legacy standalone scene with missing metadata warning. |
| Metadata exists without Markdown | Show invalid/recoverable; do not create prose. |

No repair should silently rewrite project identity, create story prose, import unknown files as canon, or delete files.

## 7. Analysis / Extraction Integration Placeholder

First implementation may show a placeholder only.

Future integration rules:

- Story Check can be run on selected owner-authored scene only when explicitly requested.
- Future extraction can read selected scene/chapter source only when explicitly requested or allowed by later policy.
- Extraction output becomes OMI candidates only.
- Analysis output appears outside the editor body.
- Candidate outputs never mutate scene prose.
- Candidate outputs never mutate chapter metadata as truth without explicit owner approval.
- No auto-promotion to memory/canon.
- No apply-promotion from this page unless a future explicit flow is designed.
- No Dramatica-specific page requirements yet.
- No model/Ollama calls during first-version page load, list, save, reload, reorder, move, or search.

Allowed future controls, if separately designed:

- Run Story Check.
- Extract candidates.
- View evidence spans.
- Open OMI candidate review.

Prohibited future controls:

- Apply AI output to editor.
- Rewrite selected text.
- Continue from cursor.
- Expand outline into prose.
- Generate scene from metadata.
- Promote candidate to canon without explicit promotion flow.

## 8. Local Search / Filter Planning

First-version local search/filter may operate over:

- Chapter title.
- Scene title.
- Tags.
- Status.
- Owner-authored metadata notes if cheap/safe.
- Chapter ID or scene ID for exact lookup.

Optional future body search:

- Body search may be added later only if explicitly implemented as local deterministic text search.
- Body search should not generate summaries.
- Body search should not trigger extraction.
- Body search should not call a model.

Rules:

- No semantic search in the first version.
- No model/Ollama call.
- No generated summaries.
- No extraction during search.
- Search results must remain project-scoped.
- Search must not mutate files.
- Search must not create OMI candidates or memory/canon records.

Recommended first filters:

- Chapter status.
- Scene status.
- Tags.
- Has warning.
- Standalone/orphan scenes.
- Empty scenes.

## 9. API Planning

These route groups are future planning only. Do not implement them during WORKSPACE-009.

Every route must validate `project_id`; chapter routes must validate `chapter_id`; scene routes must validate `scene_id`. IDs must align with backend safe path helpers and reject traversal, absolute paths, slashes, backslashes, empty values, dot, dot-dot, leading dots, unsafe names, and reserved names.

Every route must preserve no-prose and candidate/canon boundaries:

- Owner-authored prose may be saved only through explicit scene save routes.
- Routes must not generate, rewrite, continue, imitate, polish, improve, expand, or extend prose.
- Routes must not call Ollama or any model during list/load/save/reload/reorder/search.
- Routes must not create JSONL/training records.
- Routes must not create OMI records by default.
- Routes must not create OMI promotion records.
- Routes must not write approved memory/canon.

### Chapter Route Group

Routes:

- `GET /api/projects/{project_id}/chapters`
- `POST /api/projects/{project_id}/chapters`
- `GET /api/projects/{project_id}/chapters/{chapter_id}`
- `PATCH /api/projects/{project_id}/chapters/{chapter_id}`
- `POST /api/projects/{project_id}/reorder-chapters`

Purpose:

- List, create, load, update, and reorder chapter metadata.

Page dependency:

- Chapter sidebar.
- Chapter metadata panel.
- Chapter reorder controls.
- Empty-state chapter creation.

Validation:

- Safe `project_id` and `chapter_id`.
- Metadata version.
- Project/chapter ID match.
- Collision-free generated ID for create.
- Unique chapter order for reorder.

No-prose boundary:

- Chapter routes write metadata only.
- No generated chapter text.

Candidate/canon boundary:

- Candidate summary references remain candidate-only.
- Approved navigation summaries require owner-authored or owner-approved source.

Expected errors:

- 400 invalid ID.
- 404 missing project/chapter.
- 409 ID collision or reorder conflict.
- 422 corrupt metadata, unsupported version, or project mismatch.
- 500 sanitized unreadable/write failure.

### Scene List / Create Route Group

Routes:

- `GET /api/projects/{project_id}/scenes`
- `POST /api/projects/{project_id}/scenes`

Purpose:

- List scene metadata and create empty owner-editable scenes.

Page dependency:

- Scene list.
- Standalone/orphan scene area.
- Scene create actions.
- Search/filter.

Validation:

- Safe `project_id`.
- Optional safe `chapter_id` filter.
- Collision-free generated scene ID.
- Existing target chapter when creating under chapter.

No-prose boundary:

- Listing reads metadata only.
- Create starts with empty content unless a future explicit owner-provided initial content path is designed.

Candidate/canon boundary:

- Scene records are source documents, not approved canon.

Expected errors:

- 400 invalid ID/filter.
- 404 missing project or target chapter.
- 409 ID collision or inconsistent ordering.
- 422 corrupt metadata.
- 500 sanitized unreadable/write failure.

### Scene Body Route Group

Routes:

- `GET /api/projects/{project_id}/scenes/{scene_id}`
- `PUT /api/projects/{project_id}/scenes/{scene_id}`

Purpose:

- Load and save owner-authored scene Markdown body.

Page dependency:

- Main scene editor.
- Save/reload controls.
- Conflict detection.

Validation:

- Safe `project_id` and `scene_id`.
- Existing scene or explicit recoverable state.
- Optional conflict token such as `last_known_updated_at`.
- Size limits.

No-prose boundary:

- Save content is owner-authored storage, not an assistant request.
- Do not run model request guard against owner body save content.
- Do guard future assistant/model instruction fields separately.

Candidate/canon boundary:

- Saving scene body does not approve canon, create candidates, or promote memory.

Expected errors:

- 400 invalid ID.
- 404 missing scene body.
- 409 conflict.
- 413 content too large.
- 422 body/metadata mismatch.
- 500 sanitized write failure.

### Scene Metadata Route Group

Routes:

- `GET /api/projects/{project_id}/scenes/{scene_id}/metadata`
- `PATCH /api/projects/{project_id}/scenes/{scene_id}/metadata`

Purpose:

- Load and save owner-authored scene metadata.

Page dependency:

- Scene metadata panel.
- Scene rename/status/tags/owner notes.

Validation:

- Safe IDs.
- Metadata version.
- Project/scene ID match.
- Safe linked IDs.
- `content_path` remains inside project.

No-prose boundary:

- Metadata routes must not write scene body prose.
- No generated scene summaries or notes.

Candidate/canon boundary:

- Candidate references stay candidates.
- Future owner-approved links must remain explicit.

Expected errors:

- 400 invalid ID.
- 404 missing metadata.
- 409 conflict.
- 422 corrupt metadata, unsupported version, invalid reference, or project mismatch.
- 500 sanitized write failure.

### Reorder / Move Scene Route Group

Routes:

- `POST /api/projects/{project_id}/chapters/{chapter_id}/reorder-scenes`

Purpose:

- Reorder scenes within a chapter and support move-into-target-chapter behavior when designed.

Page dependency:

- Scene reorder controls.
- Move scene dialog.
- Consistency warnings.

Validation:

- Safe project, chapter, and scene IDs.
- Unique scene IDs.
- All listed scenes exist.
- Duplicate chapter membership resolved explicitly.
- Source/target chapter state remains consistent.

No-prose boundary:

- Reorder/move must preserve scene Markdown unchanged.

Candidate/canon boundary:

- Reorder/move changes organization metadata only, not canon.

Expected errors:

- 400 invalid ID.
- 404 missing chapter/scene.
- 409 duplicate membership, inconsistent ordering, or conflict.
- 422 corrupt metadata.
- 500 sanitized write failure.

## 10. Frontend Planning

Do not implement UI in WORKSPACE-009.

Future components:

- `ChaptersScenesPage`.
- `ChapterSidebar`.
- `ChapterListItem`.
- `SceneList`.
- `SceneListItem`.
- `SceneEditor`.
- `ChapterMetadataPanel`.
- `SceneMetadataPanel`.
- `ReorderControls`.
- `MoveSceneDialog`.
- `UnsavedChangeModal`.
- `CorruptDocumentWarning`.
- `EmptyStateGuidance`.
- `CandidateAnalysisPanelPlaceholder`.

Frontend responsibilities:

- Track active project, selected chapter, selected scene, body dirty state, metadata dirty state, load/save status, conflict state, and warnings.
- Load chapter and scene metadata before loading scene body.
- Load scene body only for selected/opened scene.
- Preserve editor state on failed saves.
- Warn before discarding dirty scene body or metadata.
- Keep analysis/candidate state separate from editor state.
- Scope all state by project.
- Avoid rendering AI writing buttons.

UI labeling rules:

- Owner-authored scene body and metadata should be labeled as owner-authored project content.
- Candidate references should be labeled candidate/pending.
- Approved canon links should be labeled approved only if future approved records exist.
- Warning badges should be status labels, not story interpretation.

## 11. Future Tests

Future implementation should include tests for:

- Page loads chapters/scenes for valid project.
- Page handles no chapters and no scenes.
- Page handles existing legacy scene Markdown without metadata.
- Create chapter.
- Create scene under chapter.
- Create standalone scene if supported.
- Select chapter.
- Select scene.
- Save/reload scene body.
- Save/reload intentionally empty scene body.
- Save/reload scene metadata.
- Save/reload chapter metadata.
- Missing scene body versus empty scene body distinguished.
- Corrupt chapter metadata warning shown.
- Corrupt scene metadata warning shown.
- Reorder chapters.
- Reorder scenes.
- Move scene between chapters.
- Inconsistent `chapter.scene_ids` / `scene_metadata.chapter_id` warning shown.
- Duplicate scene IDs rejected.
- Duplicate chapter IDs rejected.
- Unsaved edits warn before scene switch.
- Unsaved edits warn before chapter switch if selection would change editor state.
- Unsaved edits warn before page navigation, project switch, and browser unload.
- Save failure preserves content.
- Conflict detection warning appears.
- Invalid IDs rejected.
- Path traversal rejected.
- No model/Ollama call during page load/save/reload/reorder/search.
- No generated summaries.
- No AI prose-generation controls.
- Analysis/candidate panel does not insert text into editor.
- No OMI promotion or memory/canon mutation.
- No `bible.json` or `storyform.json` truth mutation.
- No JSONL/training writes.
- `training/data/dataset_manifest.json` unchanged.

## 12. Deferred Decisions

Deferred to future implementation tasks:

- Whether standalone scene creation is enabled in the first page implementation or only legacy standalone display.
- Exact chapter/scene create dialog fields.
- Exact drag/drop versus button-based reorder controls.
- Whether move scene is a dedicated dialog or part of reorder controls.
- Whether body search is included in first implementation or deferred.
- Whether chapter metadata and scene metadata save separately or through one page-level save action.
- Conflict token strategy: timestamp, hash, revision counter, or hybrid.
- Whether unsaved per-project drafts are preserved or project switch requires Save/Discard.
- Archive/delete design for chapters and scenes.
- Repair flow for missing/corrupt metadata.
- Whether owner-approved navigation summaries appear in lists.
- Future extraction trigger policy.

## 13. Implementation Non-Goals

WORKSPACE-009 does not implement:

- Chapters / Scenes UI.
- Backend chapter/scene routes.
- Editor changes.
- Project creation.
- Project selector/library.
- Extractor logic.
- Dramatica-specific logic.
- Runtime project files under `projects/`.
- OMI records.
- Memory/canon runtime files.
- JSONL records.
- Training or fine-tuning.
- Ollama/live model verification.
- Package/dependency changes.
