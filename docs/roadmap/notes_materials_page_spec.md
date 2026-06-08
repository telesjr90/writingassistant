# WORKSPACE-010: Notes / Materials Page Spec

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
- WORKSPACE-009: `docs/roadmap/chapters_scenes_page_spec.md`
- Project file model: `docs/roadmap/project_file_model.md`
- OMI storage model: `docs/roadmap/omi_storage_model.md`
- Project memory/canon storage: `docs/roadmap/project_memory_canon_storage_model.md`

## 1. Purpose

The Notes / Materials page should be the dedicated workspace page for owner-authored notes, research, references, planning material, and project materials. It should let the owner create, select, edit, save, reload, rename, tag, search, filter, and organize notes and materials while preserving owner authorship and source boundaries.

The page should:

- Let the owner create, select, edit, save, reload, rename, tag, search, filter, and organize notes and materials.
- Support owner-authored planning, research, reference, and project-material text only.
- Preserve the notes/materials storage and metadata model from WORKSPACE-006.
- Use the shared editor workflow from WORKSPACE-007.
- Support intentionally empty notes and materials.
- Show safe metadata, provenance, license/status warnings, and broken-link warnings.
- Keep analysis and candidate panels separate from editor content.
- Avoid Dramatica-specific assumptions.
- Avoid model/Ollama calls in the first implementation.
- Avoid treating notes/materials as approved canon or training data by default.

The application may store, edit, and organize owner-authored prose, notes, research, references, metadata, and materials. The AI must never write, rewrite, continue, imitate, polish, improve, expand, or extend story prose.

Standard refusal message:

```text
I can analyze structure and ask diagnostic questions, but I cannot write or rewrite story prose.
```

## 2. Page Layout

First-version sections:

- Page Header.
- Notes List.
- Materials List.
- Type / Tag / Status Filters.
- Local Search Bar.
- Main Note / Material Editor.
- Metadata Panel.
- Linked Targets Panel.
- Reference / License / Provenance Panel.
- Status / Warning Area.
- Empty-State Guidance.
- Future Candidate / Extraction Placeholder.

### Page Header

Purpose:

- Identify the active project and the Notes / Materials workspace area.
- Provide top-level create and navigation actions.
- Show lightweight counts and page-level warning badges.

Data source:

- Active project metadata from `project.json`.
- Note metadata from `note_metadata/*.json`.
- Material metadata from `material_metadata/*.json`.
- Page route and selected document state.

No-prose boundary:

- Header copy is navigation/status text only.
- Do not generate note titles, material titles, summaries, planning prose, research prose, or story prose.

Candidate/canon boundary:

- Notes/materials are project source material, not approved canon by default.
- Candidate counts or linked candidate badges must be labeled candidate-only.
- Approved memory/canon counts may appear only as future approved references, not as inferred truth from notes/materials.

Training-data boundary:

- Header counts must not imply training eligibility.
- Do not count notes/materials as dataset or training records.

Empty state:

- Show zero note/material counts and safe create actions.
- Missing notes/materials folders should appear as an empty or missing-folder state, not a fatal page error.

Error state:

- Invalid project identity blocks normal page load.
- Corrupt optional note/material metadata should show degraded counts plus warnings.

### Notes List

Purpose:

- List notes in the active project.
- Let the owner select, create, rename, tag, and inspect note status.

Data source:

- `note_metadata/{note_id}.json`.
- `notes/{note_id}.md` existence and cheap derived metadata only when needed.

No-prose boundary:

- Note titles, tags, owner notes, and note body content are owner-authored.
- The list must not generate note summaries or synthesize story meaning from note bodies.

Candidate/canon boundary:

- Linked OMI candidates remain candidate-only.
- Linked memory records are references to future approved records only; the note itself does not become canon.

Training-data boundary:

- Notes are not training data by default.
- List badges must not label notes as training-eligible unless a separate future owner-approved training policy exists.

Empty state:

- Show safe create note action.
- Empty projects should not auto-create a note without owner action.

Error state:

- Corrupt note metadata shows a warning row.
- Missing note body is distinct from an intentionally empty note body.
- Unsafe note IDs or filename mismatches should be hidden from normal selection and surfaced as warnings.

### Materials List

Purpose:

- List project materials and references.
- Let the owner select, create, rename, tag, and inspect material status, source kind, and license/provenance warnings.

Data source:

- `material_metadata/{material_id}.json`.
- `materials/{material_id}.md` existence and cheap derived metadata only when needed.

No-prose boundary:

- Material titles, body text, owner notes, citations, and labels are owner-authored or owner-provided.
- The list must not generate summaries, rewrite citations, or synthesize research notes.

Candidate/canon boundary:

- Reference material is not owner-authored story truth unless explicitly marked through a later owner-approved policy.
- Material links to candidates and future memory records remain references.

Training-data boundary:

- Materials are not training data by default.
- Reference or external material must not be treated as training data without a separate future rights and owner-approval workflow.

Empty state:

- Show safe create material action.
- Reference-only material metadata may exist without editable body content if clearly labeled.

Error state:

- Corrupt material metadata shows a warning row.
- Missing material body is distinct from an empty body and distinct from reference-only metadata.
- Unknown or restricted license status should show a warning without blocking metadata inspection.

### Type / Tag / Status Filters

Purpose:

- Narrow visible notes/materials by kind, type, tags, status, links, and material source/license fields.

Data source:

- `note_type`, `material_type`, `tags`, `status`, linked IDs, `source_kind`, and `license_status` from metadata.

No-prose boundary:

- Filters operate on stored metadata only.
- Filters must not generate descriptions, labels, or summaries.

Candidate/canon boundary:

- Filters for candidate links and approved memory links must be visually distinct.
- Filtering by approved memory link does not promote a note/material into memory/canon.

Training-data boundary:

- No filter should imply dataset inclusion.
- Future training eligibility filters require a separate design and are not part of first implementation.

Empty state:

- If filters match no records, show clear no-results state and option to clear filters.

Error state:

- Invalid filter values should be rejected or ignored with a warning.
- Broken linked IDs should appear as broken-link filters/warnings rather than silently removed.

### Local Search Bar

Purpose:

- Provide deterministic project-local search across notes/materials metadata and optionally cheap/safe body text.

Data source:

- Note/material titles.
- Tags.
- Type.
- Status.
- Owner-authored body text if cheap and safe.
- Owner notes.
- Material `source_kind`, `source_url`, `source_citation`.
- Linked chapter, scene, candidate, and memory record IDs.

No-prose boundary:

- Search must not generate summaries.
- Snippets, if shown, should be short verbatim owner-authored or owner-provided excerpts.

Candidate/canon boundary:

- Search results must distinguish notes, materials, OMI candidates, and approved canon.
- Candidate links are not approved canon.

Training-data boundary:

- Search must not create JSONL/training records or update dataset metadata.
- Search snippets are display-only and not training extraction.

Empty state:

- Empty query shows normal list state or recent/updated documents.
- No matches shows no-results guidance without generation.

Error state:

- Invalid search query/filter values return safe errors.
- Search index corruption, if a future index exists, should fall back or warn without treating the index as authoritative truth.

### Main Note / Material Editor

Purpose:

- Let the owner edit and save the selected note or material body.

Data source:

- `notes/{note_id}.md` for selected notes.
- `materials/{material_id}.md` for selected materials with editable text/Markdown body.
- Selected note/material metadata for title, status, and document identity.
- Shared editor state from WORKSPACE-007.

No-prose boundary:

- Editor content is owner-authored or owner-provided text.
- Saving editor content must not be blocked as an AI prose-generation request.
- AI output must never be inserted into the editor body.

Candidate/canon boundary:

- Note/material body content is project source material, not approved memory/canon by default.
- Future extraction from body content creates OMI candidates only.

Training-data boundary:

- Editor saves must not write JSONL files, training records, or `training/data/dataset_manifest.json`.
- Body text must not become training data by default.

Empty state:

- No selected document: prompt the owner to select or create a note/material.
- Empty selected note/material: show that intentionally empty documents are valid where applicable.

Error state:

- Missing body is distinct from empty body.
- Corrupt metadata may allow safe body viewing but should block normal metadata save until repaired.
- Save failure must preserve current editor content.

### Metadata Panel

Purpose:

- Show and edit owner-authored metadata for the selected note/material.

Data source:

- `note_metadata/{note_id}.json`.
- `material_metadata/{material_id}.json`.

Editable note fields:

- Title.
- `note_type`.
- Status.
- Tags.
- Owner notes.
- Linked chapter, scene, candidate, and future memory record IDs.

Editable material fields:

- Title.
- `material_type`.
- Status.
- Tags.
- Owner notes.
- Source/provenance/license fields described in the material-specific panel below.
- Linked chapter, scene, candidate, and future memory record IDs.

Read-only/derived fields:

- `project_id`.
- `note_id` or `material_id`.
- `content_path`.
- `word_count` where available.
- `created_at`.
- `updated_at`.
- Optional future revision/hash fields.

No-prose boundary:

- Metadata save must not write body text.
- No generated titles, summaries, owner notes, citations, or planning prose.

Candidate/canon boundary:

- `summary_candidate_id` is candidate-only.
- `approved_navigation_summary`, if shown later, must be owner-authored or owner-approved and labeled as a navigation aid.

Training-data boundary:

- Metadata must not mark records as training data unless a separate future training eligibility workflow exists.

Empty state:

- Empty title and owner notes are allowed where the data model allows them.
- Untitled notes/materials should show neutral labels.

Error state:

- Unsupported metadata version shows needs-migration state.
- Corrupt metadata blocks unsafe metadata save and shows recovery guidance.

### Linked Targets Panel

Purpose:

- Show and edit links from notes/materials to chapters, scenes, OMI candidates, and future memory records.

Data source:

- `linked_chapter_ids`.
- `linked_scene_ids`.
- `linked_candidate_ids`.
- `linked_memory_record_ids`.
- Lightweight chapter/scene/candidate/memory metadata for labels, when available.

No-prose boundary:

- Link labels are IDs and stored titles/status labels only.
- Do not generate relationship explanations or summaries from links.

Candidate/canon boundary:

- Chapter and scene links are organization references.
- Candidate links remain candidate-only.
- Memory links are approved references only when future approved records exist.

Training-data boundary:

- Links do not make a note/material training data.
- Links to reference materials must not be copied into dataset files.

Empty state:

- Show no linked targets and allow explicit owner link selection.

Error state:

- Broken links show warning with missing target ID and target type.
- Do not silently repair, remove, rename, or promote links.

### Reference / License / Provenance Panel

Purpose:

- Show material source metadata, provenance, license status, usage restrictions, and reference warnings.
- Show note provenance where helpful, with emphasis on manual owner creation.

Data source:

- Material `source_kind`, `source_url`, `source_citation`, `local_reference_path`, `provenance`, `license_status`, and `usage_restrictions`.
- Note `provenance`.

No-prose boundary:

- Citations and owner notes are owner-provided fields.
- Do not rewrite citations or generate bibliographic prose.
- Do not fetch URLs or read local reference paths in the first implementation.

Candidate/canon boundary:

- Reference material is not approved story truth by default.
- Provenance warnings are source-status metadata, not canon claims.

Training-data boundary:

- Unknown, restricted, reference-only, or licensed statuses must block any future default training interpretation.
- First implementation has no training eligibility behavior.

Empty state:

- Owner-created notes/materials may show manual provenance.
- Missing optional source metadata is allowed for owner-created text materials.

Error state:

- Unknown, restricted, unsafe, or missing license/provenance fields show warnings.
- Unsafe URL/local path metadata should be rejected or displayed as invalid metadata without opening the target.

### Status / Warning Area

Purpose:

- Show page-level load/save/reload/search/filter/link/provenance warnings.

Data source:

- API errors.
- Metadata validation.
- Editor dirty/conflict state.
- Broken link checks.
- License/provenance checks.

No-prose boundary:

- Warnings are factual status messages only.
- Do not generate repair prose or replacement content.

Candidate/canon boundary:

- Warnings may mention candidate/canon state only as labels.
- Warnings must not promote candidates or canonize source text.

Training-data boundary:

- Warnings should explicitly show that notes/materials are not training data by default where relevant.

Empty state:

- No warnings when clean.

Error state:

- Blocking errors should disable unsafe saves but preserve owner-authored content.
- Non-blocking warnings should allow body save when safe.

### Empty-State Guidance

Purpose:

- Provide safe next actions when no notes, no materials, or no selected document exists.

Data source:

- Note/material counts.
- Selection state.
- Project validation state.

No-prose boundary:

- Guidance must be operational, not generated planning or story text.
- Do not suggest "generate" actions.

Candidate/canon boundary:

- Links to OMI must be labeled idea/candidate review.
- Links to approved memory/canon must be labeled approved-only placeholders where appropriate.

Training-data boundary:

- Empty-state guidance must not suggest creating training examples or dataset records.

Empty state:

- Create note.
- Create material.
- Select an existing note/material.
- Open OMI ideas/candidates.

Error state:

- If metadata is invalid, show recovery/help state instead of create prompts that could worsen the state.

### Future Candidate / Extraction Placeholder

Purpose:

- Reserve a place for future diagnostics and candidate extraction without mixing AI output into editor content.

Data source:

- None in the first implementation.
- Future explicitly run extraction output from selected owner-authored note/material source.

No-prose boundary:

- No generated prose.
- No apply/insert/rewrite controls.
- No "generate note", "generate material", "write worldbuilding", or "write outline" controls.

Candidate/canon boundary:

- Future output is diagnostic or OMI candidate-only.
- No auto-promotion to memory/canon.

Training-data boundary:

- Future extraction must not create JSONL/training records or update dataset manifests.

Empty state:

- Placeholder may be hidden or say future extraction is unavailable.

Error state:

- Extraction errors must not affect body save/reload.
- Candidate panel failure must not mutate notes/materials.

## 3. Note Operations

Future operations:

- Create note.
- Select note.
- Rename note.
- Edit owner-authored note body.
- Save note body.
- Save note metadata.
- Reload note.
- Tag note.
- Set `note_type`.
- Link note to chapters, scenes, candidates, and future memory records.
- Search/filter notes.
- Handle intentionally empty note.
- Handle corrupt note metadata.
- Handle missing note body versus empty note body.
- Archive note later.
- Delete note later only after explicit future design.

Operation rules:

- Creating a note creates an empty owner-editable body and metadata unless a future explicit owner-provided initial content path is designed.
- Note IDs should follow WORKSPACE-006 generated stable ID rules.
- Note titles, body content, tags, and `owner_notes` are owner-authored.
- Note navigation summaries must be owner-authored or owner-approved.
- Selecting a note must use WORKSPACE-007 unsaved-change protections.
- Saving note body stores owner-authored note text only.
- Saving note metadata should be separate from body save or jointly tracked with explicit `body_dirty` and `metadata_dirty` state.
- Reload must warn before replacing dirty editor content.
- Missing note body is invalid or recoverable; empty note body is valid when intentional.
- Archiving should be future-only unless separately approved.
- Delete should not be in the first implementation and must never be automated by AI.

Prohibited note operations:

- Generate note prose.
- Write planning text for the owner.
- Expand notes into scenes, chapters, outlines, or worldbuilding prose.
- Rewrite or polish note text.
- Generate navigation summaries without owner approval.
- Treat notes as approved canon by default.
- Treat notes as training data by default.

## 4. Material Operations

Future operations:

- Create material.
- Select material.
- Rename material.
- Edit owner-authored or owner-provided material body when text/Markdown.
- Save material body.
- Save material metadata.
- Reload material.
- Tag material.
- Set `material_type`.
- Set `source_kind`, `source_url`, `source_citation`, and `local_reference_path` metadata.
- Set `license_status` and `usage_restrictions`.
- Link material to chapters, scenes, candidates, and future memory records.
- Search/filter materials.
- Handle intentionally empty material.
- Handle corrupt material metadata.
- Handle missing material body versus empty material body.
- Archive material later.
- Delete material later only after explicit future design.

Operation rules:

- Creating a material creates an empty owner-editable text/Markdown body plus metadata, or reference-only metadata only when explicitly supported.
- Material IDs should follow WORKSPACE-006 generated stable ID rules.
- First implementation is text/Markdown only.
- Material titles, body content, tags, citations, source metadata, usage restrictions, and `owner_notes` are owner-authored or owner-provided.
- Saving material body stores owner-authored or owner-provided material text only.
- Saving material metadata must preserve source/provenance/license fields.
- Missing material body is distinct from empty material body and from reference-only material metadata.
- Reference material is not owner-authored story truth unless explicitly marked by future owner policy.
- Reference material is not training data by default.
- Archiving should be future-only unless separately approved.
- Delete should not be in the first implementation and must never be automated by AI.

Explicit future-only material capabilities:

- Binary attachments.
- OCR.
- Web clipping.
- Web fetching.
- External sync.
- File watcher/import pipeline.
- Automatic conversion of arbitrary documents.

Prohibited material operations:

- Generate material prose.
- Rewrite or polish material text.
- Fetch web content in the first implementation.
- Open local reference paths blindly.
- Treat reference material as canon by default.
- Treat reference material as training data by default.

## 5. Document / Editor Behavior

The Notes / Materials page should use WORKSPACE-007 for editor state and save/reload behavior.

Required editor state concepts:

- `selected_project_id`.
- `selected_document_type: "note" | "material"`.
- `selected_document_id`.
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
- Show unsaved-change warnings on note/material switch, page navigation, project switch, and browser unload.
- Show unsaved-change warnings on create-new-note/material actions if current document is dirty.
- Preserve editor content on save failure.
- Update dirty state only after confirmed save.
- Support intentional empty note/material saves.
- Distinguish missing body file from empty body file.
- Distinguish missing metadata from corrupt metadata.
- Use `updated_at` / `last_saved_at` comparison for first-version conflict detection.
- Do not automatically merge conflicts in the first implementation.
- Do not call a model on page load, save, reload, switch, search, or filter.
- Do not fetch web content on save, reload, switch, search, or filter.
- Do not create OMI candidates by default.
- Do not promote OMI candidates.
- Do not mutate memory/canon, `bible.json`, or `storyform.json`.
- Do not create JSONL/training records.

Recommended switch flow:

1. Owner selects another note/material, page, or project.
2. If `body_dirty` or `metadata_dirty`, show Save / Discard / Cancel.
3. Save attempts the relevant body and metadata saves.
4. Discard clears local dirty changes only after explicit confirmation.
5. Cancel preserves the current editor state.
6. Successful switch clears selected-document analysis state.

Conflict behavior:

- First implementation may use timestamps.
- Save should fail closed or warn if the server/disk document changed after load.
- No automatic merge.
- Owner choices should be Reload, explicit Overwrite if separately allowed, or Cancel.
- Cancel preserves local editor content.

## 6. Organization and Linking Behavior

The Notes / Materials page should use WORKSPACE-006 metadata-driven organization.

Organization fields:

- Tags.
- `note_type`.
- `material_type`.
- Status.
- Material `source_kind`.
- Material `license_status`.
- Material `usage_restrictions`.
- Owner notes.

Link fields:

- `linked_chapter_ids`.
- `linked_scene_ids`.
- `linked_candidate_ids`.
- `linked_memory_record_ids`.

Rules:

- Links are metadata references, not canon claims.
- Link targets are not duplicated into body text.
- Body text remains owner-authored or owner-provided Markdown/text.
- Broken links should be displayed as warnings with missing target ID and target type.
- Broken links should not block body save.
- Broken links should block only operations that require a valid target.
- No silent repair of links.
- No silent removal of links.
- No silent canon promotion.
- No silent training-data promotion.
- Default list order is `updated_at` descending.
- Fallback list order is title, then ID.
- Manual ordering is deferred unless later UI design requires curated ordering.

Material provenance rules:

- `source_url` and `local_reference_path` are metadata only in the first implementation.
- Do not fetch URLs.
- Do not open local paths blindly.
- Preserve `source_citation`, `provenance`, `license_status`, and `usage_restrictions`.
- Unknown, restricted, reference-only, or missing license status should show warnings.

## 7. Local Search / Filter Planning

First-version local search/filter may operate over:

- Note/material title.
- Tags.
- Type.
- Status.
- Owner-authored body text if cheap and safe.
- `owner_notes`.
- Material `source_kind`.
- Material `source_url`.
- Material `source_citation`.
- Linked chapter IDs.
- Linked scene IDs.
- Linked candidate IDs.
- Linked future memory record IDs.

Recommended first filters:

- Kind: notes, materials, or all.
- `note_type`.
- `material_type`.
- Status.
- Tags.
- Linked chapter.
- Linked scene.
- Has OMI candidate links.
- Has approved memory/canon links.
- Has source URL.
- `source_kind`.
- `license_status`.
- Has warning.
- Missing body.
- Corrupt metadata.

Rules:

- No semantic search in the first implementation.
- No model/Ollama call.
- No generated summaries.
- No extraction during search.
- No web fetching during search.
- No local reference path opening during search.
- Search must not create candidates.
- Search must not promote candidates.
- Search must not mutate memory/canon.
- Search must not write training data.
- Search results must distinguish notes, materials, OMI candidates, and approved canon.
- Search snippets, if shown, should be short verbatim excerpts from local content and kept clearly source-bound.

Recommended first-version result shape:

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
      "status": "draft",
      "tags": [],
      "warnings": []
    }
  ],
  "warnings": []
}
```

## 8. Analysis / Extraction Integration Placeholder

First implementation may show a placeholder only.

Future integration rules:

- Future extraction can read selected owner-authored note/material source only when explicitly run.
- Extraction from external/reference material must respect provenance, license status, and usage restrictions.
- Extraction output routes to OMI candidates only.
- Analysis output appears outside the editor body.
- Candidate outputs never mutate note/material body content.
- Candidate outputs never mutate note/material metadata as truth without explicit owner approval.
- No auto-promotion to memory/canon.
- No apply-promotion from this page unless a future explicit flow is designed.
- No training data writes.
- No Dramatica-specific page requirements yet.
- No model/Ollama calls during first-version page load, list, save, reload, switch, search, or filter.

Allowed future controls, if separately designed:

- Run candidate extraction on selected owner-authored note/material.
- View source evidence spans.
- Open linked OMI candidate review.
- Show diagnostic questions separate from editor content.

Prohibited future controls:

- Apply AI output to editor.
- Rewrite selected text.
- Continue from cursor.
- Expand note into prose.
- Generate material.
- Generate scene from note.
- Promote candidate to canon without explicit promotion flow.
- Write training records.

## 9. API Planning

These route groups are future planning only. Do not implement them during WORKSPACE-010.

Every route must validate `project_id`; note routes must validate `note_id`; material routes must validate `material_id`. IDs must align with backend safe path helpers and reject traversal, absolute paths, slashes, backslashes, empty values, dot, dot-dot, leading dots, unsafe names, and reserved names.

Every route must preserve no-prose, candidate/canon, and training-data boundaries:

- Owner-authored or owner-provided text may be saved only through explicit note/material save routes.
- Routes must not generate, rewrite, continue, imitate, polish, improve, expand, or extend prose.
- Routes must not call Ollama or any model during list/load/save/reload/search/filter.
- Routes must not fetch web content or open local reference paths in the first implementation.
- Routes must not create JSONL/training records.
- Routes must not update `training/data/dataset_manifest.json`.
- Routes must not create OMI records by default.
- Routes must not create OMI promotion records.
- Routes must not write approved memory/canon.

### Note List / Create Route Group

Routes:

- `GET /api/projects/{project_id}/notes`
- `POST /api/projects/{project_id}/notes`

Purpose:

- List note metadata.
- Create empty owner-editable notes.

Page dependency:

- Notes List.
- Page Header counts.
- Empty-state note creation.
- Search/filter.

Validation:

- Safe `project_id`.
- Optional safe filter parameters.
- Collision-free generated note ID.
- Metadata version and project ID match.

No-prose boundary:

- Listing reads metadata by default.
- Create starts with empty content unless a future explicit owner-provided initial content path is designed.
- No generated note titles or body content.

Candidate/canon boundary:

- Note records are source documents, not approved canon.
- Candidate links remain candidate-only.

Training-data boundary:

- List/create must not create training records or mark notes training-eligible.

Expected errors:

- 400 invalid project ID or filter.
- 404 missing project.
- 409 ID collision.
- 422 corrupt metadata, unsupported version, or project mismatch.
- 500 sanitized unreadable/write failure.

### Note Body Route Group

Routes:

- `GET /api/projects/{project_id}/notes/{note_id}`
- `PUT /api/projects/{project_id}/notes/{note_id}`

Purpose:

- Load and save owner-authored note Markdown/text body.

Page dependency:

- Main Note / Material Editor.
- Save/reload controls.
- Conflict detection.

Validation:

- Safe `project_id` and `note_id`.
- Existing note or explicit recoverable state.
- Optional conflict token such as `last_known_updated_at`.
- Size limits.

No-prose boundary:

- Save content is owner-authored storage, not an assistant request.
- Do not run freeform model-request guard against owner body save content.

Candidate/canon boundary:

- Saving note body does not approve canon, create candidates, or promote memory.

Training-data boundary:

- Saving note body must not write JSONL/training records.

Expected errors:

- 400 invalid ID.
- 404 missing note body.
- 409 conflict.
- 413 content too large.
- 422 body/metadata mismatch.
- 500 sanitized write failure.

### Note Metadata Route Group

Routes:

- `GET /api/projects/{project_id}/notes/{note_id}/metadata`
- `PATCH /api/projects/{project_id}/notes/{note_id}/metadata`

Purpose:

- Load and save owner-authored note metadata.

Page dependency:

- Metadata Panel.
- Linked Targets Panel.
- Note rename/status/type/tags/owner notes.

Validation:

- Safe IDs.
- Metadata version.
- Project/note ID match.
- Safe linked IDs.
- `content_path` remains inside project.

No-prose boundary:

- Metadata routes must not write note body text.
- No generated note summaries or owner notes.

Candidate/canon boundary:

- Candidate references stay candidates.
- Future memory links remain explicit references.

Training-data boundary:

- Metadata save must not set training data state in first implementation.

Expected errors:

- 400 invalid ID.
- 404 missing metadata.
- 409 conflict.
- 422 corrupt metadata, unsupported version, invalid reference, or project mismatch.
- 500 sanitized write failure.

### Material List / Create Route Group

Routes:

- `GET /api/projects/{project_id}/materials`
- `POST /api/projects/{project_id}/materials`

Purpose:

- List material metadata.
- Create empty owner-editable text/Markdown materials or explicitly supported reference-only material metadata.

Page dependency:

- Materials List.
- Page Header counts.
- Empty-state material creation.
- Search/filter.
- Reference / License / Provenance Panel.

Validation:

- Safe `project_id`.
- Optional safe filter parameters.
- Collision-free generated material ID.
- Metadata version and project ID match.
- Source/provenance/license fields valid where required.

No-prose boundary:

- Listing reads metadata by default.
- Create starts with empty text/Markdown body or explicit reference-only metadata.
- No generated material titles, citations, or body content.

Candidate/canon boundary:

- Material records are source/reference documents, not approved canon.
- Candidate links remain candidate-only.

Training-data boundary:

- List/create must not create training records or mark materials training-eligible.

Expected errors:

- 400 invalid project ID or filter.
- 404 missing project.
- 409 ID collision.
- 422 corrupt metadata, unsupported version, project mismatch, invalid source/provenance/license field, or unsafe local path metadata.
- 500 sanitized unreadable/write failure.

### Material Body Route Group

Routes:

- `GET /api/projects/{project_id}/materials/{material_id}`
- `PUT /api/projects/{project_id}/materials/{material_id}`

Purpose:

- Load and save owner-authored or owner-provided material Markdown/text body.

Page dependency:

- Main Note / Material Editor.
- Save/reload controls.
- Conflict detection.

Validation:

- Safe `project_id` and `material_id`.
- Existing material body or explicit reference-only/missing-body state.
- Optional conflict token such as `last_known_updated_at`.
- Size limits.

No-prose boundary:

- Save content is owner-authored or owner-provided storage, not an assistant request.
- Do not run freeform model-request guard against owner body save content.

Candidate/canon boundary:

- Saving material body does not approve canon, create candidates, or promote memory.

Training-data boundary:

- Saving material body must not write JSONL/training records.

Expected errors:

- 400 invalid ID.
- 404 missing material body when body is required.
- 409 conflict.
- 413 content too large.
- 422 body/metadata mismatch or restricted/read-only material state.
- 500 sanitized write failure.

### Material Metadata Route Group

Routes:

- `GET /api/projects/{project_id}/materials/{material_id}/metadata`
- `PATCH /api/projects/{project_id}/materials/{material_id}/metadata`

Purpose:

- Load and save owner-authored or owner-provided material metadata.

Page dependency:

- Metadata Panel.
- Linked Targets Panel.
- Reference / License / Provenance Panel.
- Material rename/status/type/tags/source/license/owner notes.

Validation:

- Safe IDs.
- Metadata version.
- Project/material ID match.
- Safe linked IDs.
- `content_path` remains inside project.
- URLs are metadata only.
- Local paths are metadata only and must not be opened blindly.
- License and usage restriction values are bounded.

No-prose boundary:

- Metadata routes must not write material body text.
- No generated citations, summaries, or owner notes.

Candidate/canon boundary:

- Candidate references stay candidates.
- Reference metadata is not canon by default.

Training-data boundary:

- Metadata save must not make external/reference material training data by default.

Expected errors:

- 400 invalid ID.
- 404 missing metadata.
- 409 conflict.
- 422 corrupt metadata, unsupported version, invalid reference, unsafe URL/local path metadata, invalid license status, or project mismatch.
- 500 sanitized write failure.

### Notes-Materials Search Route Group

Routes:

- `GET /api/projects/{project_id}/notes-materials/search`

Purpose:

- Provide deterministic local search/filter over notes/materials metadata and optionally body text.

Page dependency:

- Local Search Bar.
- Type / Tag / Status Filters.
- Notes List.
- Materials List.

Validation:

- Safe `project_id`.
- Bounded query length.
- Bounded filter values.
- Optional `include_body` should be explicit if body search is not always performed.

No-prose boundary:

- Search must not generate summaries.
- Snippets must be source-bound excerpts if shown.

Candidate/canon boundary:

- Results must label note, material, candidate, and approved memory/canon distinctions.

Training-data boundary:

- Search must not create JSONL/training records or dataset entries.

Expected errors:

- 400 invalid project ID, query, or filter.
- 404 missing project.
- 422 unreadable/corrupt metadata or index inconsistency.
- 500 sanitized search failure.

### Link Update / Metadata Patch Route Group

Routes:

- May use `PATCH /api/projects/{project_id}/notes/{note_id}/metadata`.
- May use `PATCH /api/projects/{project_id}/materials/{material_id}/metadata`.
- Optional future dedicated route: `PATCH /api/projects/{project_id}/notes-materials/{kind}/{id}/links`.

Purpose:

- Update linked chapter, scene, candidate, and future memory record references.

Page dependency:

- Linked Targets Panel.
- BrokenLinkWarning.
- Search/filter link filters.

Validation:

- Safe project/document IDs.
- Safe linked target IDs.
- Target existence check where available.
- Preserve broken links until owner explicitly changes them.

No-prose boundary:

- Link updates must not write body content.

Candidate/canon boundary:

- Link updates do not promote candidates or canonize notes/materials.

Training-data boundary:

- Link updates do not create training data.

Expected errors:

- 400 invalid IDs.
- 404 missing document metadata.
- 409 conflict.
- 422 invalid link field, broken required target, or corrupt metadata.
- 500 sanitized write failure.

### Optional Future Archive Route Group

Routes:

- Optional future `PATCH /api/projects/{project_id}/notes/{note_id}/archive`.
- Optional future `PATCH /api/projects/{project_id}/materials/{material_id}/archive`.

Purpose:

- Move notes/materials out of active lists without permanent deletion.

Page dependency:

- Future archive controls.

Validation:

- Separate future design required before implementation.
- Dirty editor state must warn before archive.

No-prose boundary:

- Archive must not write body content.

Candidate/canon boundary:

- Archive does not alter candidate or memory/canon status.

Training-data boundary:

- Archive does not create or remove training records.

Expected errors:

- Invalid IDs.
- Missing document.
- Conflict.
- Corrupt metadata.
- Write failure.

Permanent delete is explicitly deferred until a separate future design approves destructive behavior.

## 10. Frontend Planning

Do not implement UI in WORKSPACE-010.

Future components:

- `NotesMaterialsPage`.
- `NotesList`.
- `MaterialsList`.
- `NotesMaterialsSearch`.
- `NotesMaterialsFilters`.
- `NoteMaterialEditor`.
- `NoteMetadataPanel`.
- `MaterialMetadataPanel`.
- `LinkedTargetsPanel`.
- `ReferenceProvenancePanel`.
- `UnsavedChangeModal`.
- `CorruptDocumentWarning`.
- `BrokenLinkWarning`.
- `EmptyStateGuidance`.
- `CandidateExtractionPlaceholder`.

Frontend responsibilities:

- Track active project, selected kind, selected document ID, body dirty state, metadata dirty state, load/save status, conflict state, and warnings.
- Load note/material metadata before loading body content.
- Load body content only for the selected/opened note/material unless local body search is explicitly run.
- Preserve editor state on failed saves.
- Warn before discarding dirty body or metadata.
- Scope all state by project.
- Keep analysis/candidate state separate from editor state.
- Avoid rendering AI writing buttons.
- Avoid rendering semantic/model search controls in first implementation.

UI labeling rules:

- Label note body and note metadata as owner-authored project notes.
- Label material body and material metadata as owner-authored or owner-provided project material.
- Label reference material source/provenance/license state clearly.
- Label OMI links as candidates/pending unless future approved records exist.
- Label approved canon links as approved only if future approved memory records exist.
- Label training-data eligibility as unavailable/not default unless a future training policy exists.

Prohibited UI controls:

- Write.
- Continue.
- Rewrite.
- Polish.
- Improve.
- Expand.
- Imitate style.
- Generate note.
- Generate material.
- Write worldbuilding.
- Write outline.
- Generate scene from note.
- Insert AI text.
- Apply AI rewrite.

## 11. Future Tests

Future implementation should include tests for:

- Page loads notes/materials for valid project.
- Empty notes/materials state.
- Missing notes/materials folders show safe empty/missing-folder state.
- Create note.
- Create material.
- Select note.
- Select material.
- Save/reload note body.
- Save/reload material body.
- Save/reload note metadata.
- Save/reload material metadata.
- Intentionally empty note handled safely.
- Intentionally empty material handled safely.
- Missing note body versus empty note body distinguished.
- Missing material body versus empty material body distinguished.
- Reference-only material metadata state shown where supported.
- Corrupt note metadata warning shown.
- Corrupt material metadata warning shown.
- Broken chapter links warning shown.
- Broken scene links warning shown.
- Broken candidate links warning shown.
- Broken future memory links warning shown.
- Local search/filter does not call model/Ollama.
- Local search/filter does not fetch URLs.
- Local search/filter does not open local reference paths.
- No generated summaries.
- No extraction during search.
- No AI prose-generation controls.
- Invalid note IDs rejected.
- Invalid material IDs rejected.
- Invalid linked IDs rejected.
- Path traversal rejected.
- Duplicate IDs rejected.
- Unsaved-change warning on note/material switch.
- Unsaved-change warning on page navigation.
- Unsaved-change warning on project switch.
- Browser unload warning when dirty.
- Save failure preserves content.
- Conflict detection warning appears.
- External/reference material not treated as canon by default.
- External/reference material not treated as training data by default.
- Unknown/restricted license warning shown.
- Candidate extraction placeholder does not insert text into editor.
- No OMI promotion or memory/canon mutation.
- No `bible.json` or `storyform.json` truth mutation.
- No JSONL/training writes.
- `training/data/dataset_manifest.json` unchanged.

## 12. Deferred Decisions

Deferred to future implementation tasks:

- Whether body search should be eager scan, cached index, optional per-query scan, or deferred.
- Whether to add rebuildable `notes/index.json` or `materials/index.json`.
- Whether manual ordering is needed beyond updated/title/ID sort.
- Exact note status enum beyond first-version labels.
- Exact material status enum beyond first-version labels.
- Exact note type enum after UI design.
- Exact material type enum after UI design.
- Exact create dialog fields.
- Separate versus combined body/metadata save behavior.
- Conflict token strategy: timestamp, hash, revision counter, or hybrid.
- Whether word count updates on every body save or lazily.
- Whether reference-only materials require body files.
- Safe policy for opening local reference paths.
- Archive timing and archived-list behavior.
- Permanent delete design for notes and materials.
- Repair flow for missing/corrupt metadata.
- License/provenance review workflow for reference materials.
- Binary attachment support.
- OCR/import pipeline.
- Web clipping/fetching.
- External sync.
- Future extraction trigger policy.
- Browser/manual acceptance checklist for the implemented Notes / Materials page.

## 13. Implementation Non-Goals

WORKSPACE-010 does not implement:

- Notes / Materials UI.
- Backend note/material routes.
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
