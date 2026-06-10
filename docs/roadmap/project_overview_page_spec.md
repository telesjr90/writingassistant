# WORKSPACE-008: Project Overview Page Spec

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
- WORKSPACE-011: `docs/roadmap/project_memory_canon_page_structure_spec.md`
- WORKSPACE-012: `docs/roadmap/omi_ideas_candidates_page_spec.md`
- WORKSPACE-013: `docs/roadmap/approved_characters_page_spec.md`
- WORKSPACE-014: `docs/roadmap/approved_locations_settings_page_spec.md`
- WORKSPACE-015: `docs/roadmap/approved_timeline_page_spec.md`
- WORKSPACE-016: `docs/roadmap/approved_plot_threads_page_spec.md`
- WORKSPACE-017: `docs/roadmap/continuity_consistency_page_spec.md`
- WORKSPACE-018: `docs/roadmap/approved_open_questions_page_spec.md`
- WORKSPACE-019: `docs/roadmap/approved_relationships_page_spec.md`
- Project file model: `docs/roadmap/project_file_model.md`
- Project memory/canon storage: `docs/roadmap/project_memory_canon_storage_model.md`
- OMI storage: `docs/roadmap/omi_storage_model.md`

## 1. Purpose

The Project Overview page should be the safe project-level landing page after a project is created or opened. It should orient the owner, show lightweight project status, and provide navigation into the workspace without generating story prose, rewriting project material, or silently promoting candidates.

The Project Overview page should:

- Be the landing page after project creation.
- Be the landing page after opening an existing project from the Project Library.
- Show safe project metadata.
- Help the owner navigate to writing and organization areas.
- Show lightweight project status.
- Show project health warnings.
- Show next-step guidance without generating story prose.
- Distinguish owner-authored metadata, pending candidates, promotion records, and approved canon.
- Avoid Dramatica-specific assumptions.
- Avoid model/Ollama calls in the first implementation.

The application may store, edit, and organize owner-authored prose, notes, metadata, and materials. The AI must never write, rewrite, continue, imitate, polish, improve, or extend story prose.

Standard refusal message:

```text
I can analyze structure and ask diagnostic questions, but I cannot write or rewrite story prose.
```

## 2. Safe Overview Content

Allowed first-version overview content:

- Project title.
- Subtitle.
- Owner-authored description.
- Language.
- Status.
- `creation_method`.
- `created_at`.
- `updated_at`.
- Tags.
- Counts for chapters, scenes, notes, and materials if cheap.
- Counts for OMI ideas, candidates, and promotion records if cheap.
- Approved memory/canon counts if approved memory files exist later.
- Warning badges for missing/corrupt metadata.
- Empty-state guidance.
- Links/cards to workspace pages.

Boundary rules:

- Owner-authored descriptions may be displayed.
- Generated story summaries are prohibited.
- Unapproved AI summaries must not appear as project truth.
- Candidate summaries must be clearly labeled as candidate/pending.
- Approved navigation summaries must be owner-authored or owner-approved.
- Overview should not read full scene, note, or material bodies unless a future decision explicitly approves a body-read use case.
- Overview should not generate summaries.
- Overview should not trigger candidate extraction.
- Overview should not call Ollama, qwen3, or any model.
- Overview should not create or modify project files.

Recommended first implementation content sources:

| Content | Source | Rule |
| --- | --- | --- |
| Project metadata | `project.json` | Display owner-authored metadata only. |
| Chapter count | `chapters/*.json` or future metadata/index | Do not read scene prose. |
| Scene count | `scene_metadata/*.json` or `scenes/*.md` filename count | Do not read full body text. |
| Note count | `note_metadata/*.json` or `notes/*.md` filename count | Do not read full body text. |
| Material count | `material_metadata/*.json` or `materials/*.md` filename count | Do not fetch URLs or read full body text. |
| OMI counts | `omi/index.json` and lightweight record metadata | Candidate labels required. |
| Approved memory counts | `memory/index.json` or approved `memory/*.json` files later | Approved labels required. |
| Health warnings | Validation results from project/metadata scans | Non-destructive only. |

## 3. Page Sections

First-version Project Overview sections:

- Project Header.
- Project Health / Warnings.
- Quick Actions.
- Workspace Navigation Cards.
- Recent Documents.
- OMI Status.
- Approved Memory / Canon Snapshot.
- Empty-State Next Steps.

### Project Header

Purpose:

- Identify the active project.
- Show owner-authored project metadata at a glance.

Data source:

- `project.json`.

Candidate/canon labeling:

- Project metadata is not story canon unless a later field explicitly says so.
- Display title, subtitle, description, language, status, creation method, tags, created timestamp, and updated timestamp as project metadata.

No-prose boundary:

- Do not generate title, subtitle, description, tagline, logline, premise prose, or summary.
- Display only stored owner-authored metadata.

Empty state:

- Untitled or missing optional fields should show neutral empty labels.

Error state:

- If required project metadata is corrupt, normal overview loading should fail into project recovery/help state.
- If optional metadata is missing, show warnings without blocking the page.

### Project Health / Warnings

Purpose:

- Surface non-destructive project health issues.
- Help the owner understand missing/corrupt/unsafe states before editing.

Data source:

- Project validation.
- Metadata scans for chapters, scenes, notes, materials, OMI, and memory folders where present.

Candidate/canon labeling:

- Health warnings are diagnostic UI, not story truth.

No-prose boundary:

- Warnings must be factual status messages.
- Do not generate repair text that rewrites project material.

Empty state:

- Show "No blocking project warnings" or equivalent when clean.

Error state:

- If health scan partially fails, show partial results plus warning.
- Do not crash the whole overview if one optional folder is unreadable.

### Quick Actions

Purpose:

- Help the owner start common workspace tasks.

Data source:

- Routing/page availability.
- Project validation state.

Candidate/canon labeling:

- Actions that open candidate pages must be labeled as OMI/candidate review, not canon.

No-prose boundary:

- Quick actions must not write, continue, rewrite, polish, improve, imitate, generate, or extend prose.
- Quick actions must not trigger model calls.

Empty state:

- In a blank project, show actions to create/open a chapter, scene, note, or material, and to open OMI ideas/candidates.

Error state:

- Disable actions that require valid metadata when the relevant area is corrupt.

Allowed first-version quick actions:

- Create/open chapter.
- Create/open scene.
- Create/open note.
- Create/open material.
- Open OMI ideas/candidates.
- Open Project Context / metadata.
- Open Approved Memory / Canon page placeholder.

Prohibited actions:

- Write story for me.
- Continue scene.
- Rewrite scene.
- Polish prose.
- Improve prose.
- Imitate style.
- Generate chapter.
- Generate dialogue.
- Generate plot.

Future analysis/extraction actions:

- May be added later only as candidate-only or diagnostic actions.
- Must be separate from writing actions.
- Must not be triggered by opening Project Overview.

### Workspace Navigation Cards

Purpose:

- Provide clear navigation to project workspace areas.

Data source:

- Static route definitions plus available counts/status.

Candidate/canon labeling:

- Cards leading to OMI must say candidates/pending where applicable.
- Cards leading to approved memory/canon must say approved and show empty/placeholder state when no approved records exist.

No-prose boundary:

- Navigation card labels and descriptions must not contain generated story prose or summaries.

Empty state:

- Cards should still appear for empty projects.

Error state:

- Cards can show warning badges for relevant corrupt/missing metadata.

Recommended cards:

- Project Overview.
- Chapters / Scenes.
- Notes / Materials.
- OMI Ideas / Candidates.
- Project Context / Metadata.
- Approved Memory / Canon.
- Future approved Characters.
- Future approved Locations / Settings.
- Future Timeline.
- Future Plot Threads.
- Future Continuity / Consistency.
- Future Approved Open Questions.
- Future Approved Relationships.

WORKSPACE-009 defines the detailed target for the Chapters / Scenes navigation card and destination page.

WORKSPACE-010 defines the detailed target for the Notes / Materials navigation card and destination page.

WORKSPACE-011 defines the detailed target for the Approved Memory / Canon navigation card and destination page.

### Recent Documents

Purpose:

- Help the owner return to recently touched scenes, notes, and materials.

Data source:

- Metadata `updated_at` values from scene, note, and material metadata.
- Filename timestamps only if metadata is missing and a future implementation safely chooses that fallback.

Candidate/canon labeling:

- Recent documents are source documents, not canon snapshots.
- Candidate badges may show linked candidates only as candidate links.

No-prose boundary:

- Do not parse full body text for overview.
- Do not generate summaries.
- Do not display unapproved AI summaries as truth.

Empty state:

- Show no recent documents and link to create scene/note/material.

Error state:

- Invalid/corrupt documents should show warnings instead of breaking the panel.

Display fields:

- Title.
- Type: scene, note, or material.
- Status.
- `updated_at`.
- Optional word count if already stored/derived in metadata.
- Warning badge where applicable.

### OMI Status

Purpose:

- Show the owner whether idea/candidate review needs attention.

Data source:

- `omi/index.json`.
- Lightweight OMI record metadata when needed for counts.

Candidate/canon labeling:

- Pending candidates are not canon.
- Approved candidates are not canon until future apply-promotion creates durable records.
- Promotion records are audit records, not canon by themselves.

No-prose boundary:

- Do not display candidate content as project truth.
- Do not generate OMI summaries.

Empty state:

- Show no OMI ideas/candidates yet.
- Link to OMI Ideas/Candidates page.

Error state:

- Missing OMI folder is not fatal.
- Corrupt OMI metadata should show warning and link to OMI page/recovery later.

Counts to show:

- Raw ideas.
- Candidates.
- Approved candidates.
- Rejected candidates.
- Promotion records.
- Pending/needs-review candidates where cheap.

### Approved Memory / Canon Snapshot

Purpose:

- Show whether approved project memory/canon exists.

Data source:

- Future `memory/index.json`.
- Future approved `memory/*.json` files.

Candidate/canon labeling:

- Show approved counts only.
- Do not show pending candidates as memory/canon.
- Promotion records are not canon unless future apply-promotion has succeeded.

No-prose boundary:

- Do not generate canon summaries.
- Do not create memory files.
- Do not run apply-promotion from overview unless a future explicit flow is designed.

Empty state:

- Placeholder is acceptable in the first implementation.
- Before apply-promotion exists, show that no approved memory/canon records exist yet.

Error state:

- Corrupt memory metadata should show warning and avoid displaying records as approved.

### Empty-State Next Steps

Purpose:

- Help the owner find a safe first action in a blank project.

Data source:

- Project counts and page availability.

Candidate/canon labeling:

- Any OMI action must say candidate/idea review.

No-prose boundary:

- Guidance must be operational, not generated story text.
- Do not suggest "generate" actions.

Empty state examples:

- Create a scene.
- Create a note.
- Add project material.
- Open OMI ideas/candidates.
- Review project metadata.

Error state:

- If project metadata is invalid, next steps should point to recovery/help rather than creation.

## 4. Recent Documents Behavior

First implementation should use metadata `updated_at` values only.

Rules:

- Recent documents may include scenes, notes, and materials.
- Do not parse full body text for overview.
- Do not generate summaries.
- Distinguish document type.
- Show title, type, status, `updated_at`, and maybe word count.
- Invalid/corrupt documents should show warnings instead of breaking the page.
- Missing optional metadata should show recoverable/legacy warnings.
- Recent documents should be project-scoped and must not mix across projects.

Recommended sort:

- `updated_at` descending.
- Fallback to title, then document ID.

Recommended limit:

- 5 to 10 documents in the first UI.

## 5. OMI Status Snapshot

The overview may show lightweight OMI state.

Rules:

- Show counts for raw ideas, candidates, approved candidates, rejected candidates, promotion records, and pending review candidates where cheap.
- Show "pending candidates are not canon" or equivalent.
- Promotion records are audit records, not canon by themselves.
- No automatic promotion.
- No OMI candidate content should be displayed as approved truth.
- Link to OMI Ideas/Candidates page.
- Missing OMI folders are valid empty state.
- Corrupt OMI metadata should show warning.

The overview must not:

- Create OMI records.
- Update owner decisions.
- Create promotion records.
- Apply promotions.
- Treat approved candidate status as approved canon.
- Call a model to summarize OMI state.

## 6. Approved Memory / Canon Snapshot

The first implementation may show a placeholder only.

Rules:

- If `memory/*.json` exists later, show approved counts only.
- Approved counts must come from approved memory/canon records, not pending candidates.
- Do not show pending, rejected, archived, uncertain, or duplicate candidates as memory/canon.
- Do not create memory files from overview.
- Do not run apply-promotion from overview unless a future explicit flow is designed.
- Corrupt memory files should show health warnings and avoid approved display.

Recommended first UI:

- "No approved memory/canon records yet" when memory is absent.
- Link to Approved Memory / Canon page placeholder.
- Label promotion records as audit records if present but unapplied.

## 7. Project Health and Warnings

The overview should make health warnings visible without performing destructive repair.

Warnings to support:

- Missing `project.json`.
- Invalid project metadata.
- Unsupported `schema_version`.
- Project ID mismatch.
- Missing expected folders.
- Corrupt chapter metadata.
- Corrupt scene metadata.
- Corrupt note metadata.
- Corrupt material metadata.
- Unsafe IDs.
- Candidate data present but no approved canon.
- OMI promotion records present but no apply-promotion behavior.
- No scenes yet.
- No notes/materials yet.
- Missing OMI folder.
- Missing memory folder.
- Unreadable optional folder or file.

Rules:

- Warnings are non-destructive.
- No auto-repair unless a future owner-approved repair flow exists.
- No auto-delete.
- No silent identity rewrite.
- No automatic folder creation while loading overview.
- No leaking sensitive host filesystem paths in UI/API errors.
- Invalid required project identity should block normal overview.
- Invalid optional metadata should show warning and allow partial overview where safe.

Recommended severity levels:

- `blocking`: project cannot safely open normally.
- `warning`: page can load with degraded/partial data.
- `info`: empty state or future feature not yet present.

## 8. API Planning

These routes are future planning only. Do not implement them during WORKSPACE-008.

Overview data may be provided in two ways:

1. Dedicated backend overview summary endpoint.
2. Frontend composition from project, chapter, scene, note, material, OMI, health, and memory endpoints.

Recommended first implementation:

- Use a dedicated backend `GET /api/projects/{project_id}/overview` summary endpoint if it reduces frontend complexity and centralizes path-safety/health validation.
- Keep the endpoint lightweight and read-only.
- Do not read full document bodies.
- Do not call models.
- Do not mutate files.
- Keep health details in a separate `GET /api/projects/{project_id}/health` endpoint if the health response becomes large.

### `GET /api/projects/{project_id}/overview`

Purpose:

- Return lightweight data needed by Project Overview.

Request:

- Path parameter: safe `project_id`.

Response shape:

```json
{
  "project_id": "example",
  "project": {
    "title": "Project Title",
    "subtitle": null,
    "description": "Owner-authored project description",
    "language": "en",
    "status": "active",
    "creation_method": "blank",
    "created_at": "2026-06-08T00:00:00Z",
    "updated_at": "2026-06-08T00:00:00Z",
    "tags": []
  },
  "counts": {
    "chapters": 0,
    "scenes": 0,
    "notes": 0,
    "materials": 0,
    "omi_ideas": 0,
    "omi_candidates": 0,
    "omi_promotion_records": 0,
    "approved_memory_records": 0
  },
  "recent_documents": [],
  "omi_status": {
    "ideas": 0,
    "candidates": 0,
    "approved_candidates": 0,
    "rejected_candidates": 0,
    "pending_candidates": 0,
    "promotion_records": 0,
    "note": "Pending candidates are not canon."
  },
  "approved_memory_status": {
    "available": false,
    "record_count": 0,
    "counts_by_type": {},
    "note": "No approved memory/canon records yet."
  },
  "warnings": []
}
```

Validation:

- Validate `project_id` as a safe single path component.
- Validate `project.json` required identity.
- Validate optional metadata defensively.
- Do not trust frontend project ID alone.

No-prose boundary:

- No generated story prose.
- No generated summaries.
- No model calls.

Candidate/canon boundary:

- Pending/rejected candidates are candidate-only.
- Promotion records are audit-only.
- Approved memory counts come only from approved records after future apply-promotion exists.

Expected errors:

- 400 invalid `project_id`.
- 404 missing project.
- 422 invalid required project metadata.
- 500 unreadable project metadata with sanitized message.

### `GET /api/projects/{project_id}/health`

Purpose:

- Return detailed project health/warning information.

Request:

- Path parameter only.

Response shape:

```json
{
  "project_id": "example",
  "status": "warning",
  "warnings": [
    {
      "code": "missing_notes_folder",
      "severity": "info",
      "message": "Notes folder is not present yet.",
      "target": "notes"
    }
  ]
}
```

Validation:

- Validate `project_id`.
- Sanitize file path details.

No-prose boundary:

- Health messages are status text only.
- No AI repair prose.

Candidate/canon boundary:

- Health checks may mention candidates/promotions but must not change their state.

Expected errors:

- 400 invalid `project_id`.
- 404 missing project.
- 500 unreadable required metadata.

### `GET /api/projects/{project_id}/recent-documents`

Purpose:

- Return lightweight recent scene/note/material metadata.

Request query parameters:

```text
limit=10
types=scene,note,material
```

Response shape:

```json
{
  "project_id": "example",
  "documents": [
    {
      "document_type": "scene",
      "document_id": "scene_001",
      "title": "Opening Scene",
      "status": "draft",
      "updated_at": "2026-06-08T00:00:00Z",
      "word_count": 123,
      "warnings": []
    }
  ],
  "warnings": []
}
```

Validation:

- Validate project ID and optional type filters.
- Read metadata only.
- Do not parse full body text.

No-prose boundary:

- No generated summaries.
- No model calls.

Candidate/canon boundary:

- Recent documents are source documents, not approved canon.

Expected errors:

- 400 invalid `project_id`.
- 400 invalid query filter.
- 404 missing project.
- Partial warnings for corrupt optional metadata.

## 9. Frontend Planning

Do not implement UI in WORKSPACE-008.

Future UI surfaces:

- Project Overview page.
- Project header component.
- Health/warning banner.
- Quick action cards.
- Workspace navigation cards.
- Recent documents panel.
- OMI status panel.
- Approved memory/canon snapshot panel.
- Empty states.
- Error states.
- Loading states.

Frontend rules:

- No AI writing buttons.
- No generated story prose.
- No unapproved summary display as truth.
- Navigation cards should lead to future pages defined by WORKSPACE-001 and adjacent specs.
- Candidate panels must use candidate/pending labels.
- Approved memory panels must use approved labels only when approved records exist.
- Opening Project Overview must not trigger analysis, extraction, model calls, promotion, or file mutation.

Suggested loading behavior:

- Show page shell while overview summary loads.
- Show partial panels where data is available.
- Show warnings for degraded optional sections.
- Use Project Library recovery state for blocking project metadata failures.

## 10. Future Tests

Future implementation should include tests for:

- Overview loads valid project metadata.
- Overview handles empty project.
- Overview handles missing optional folders.
- Overview handles corrupt metadata warnings.
- Overview handles missing OMI folder.
- Overview handles missing memory folder.
- Overview rejects path traversal in `project_id`.
- Overview does not call Ollama/model.
- Overview does not read full document bodies for generated summaries.
- Overview does not create/modify project files.
- Overview does not create OMI records.
- Overview does not mutate memory/canon.
- Overview does not promote candidates.
- Overview displays candidate vs approved labels correctly.
- Overview labels promotion records as audit records, not canon.
- Overview links to chapters/scenes, notes/materials, OMI, and memory/canon pages.
- Overview shows no AI prose-generation controls.
- Recent documents use metadata timestamps.
- Corrupt recent-document metadata shows warnings.
- Empty-state next steps do not include generate/write/rewrite actions.
- No JSONL/training writes.
- `training/data/dataset_manifest.json` unchanged.

## 11. Deferred Decisions

Deferred to future implementation tasks:

- Dedicated overview endpoint versus frontend composition after route implementation details are clearer.
- Whether overview health scan should be synchronous, cached, or split from summary.
- Exact warning code taxonomy.
- Recent document limit and sorting tie-breakers.
- Whether optional stored owner-approved navigation summaries appear in overview.
- Whether Project Overview can later show owner-authored excerpts.
- Exact quick action layout.
- Whether project metadata editing happens inline on overview or in Project Context / metadata page.
- How approved memory/canon counts are computed after apply-promotion exists.
- Whether overview includes a future extraction/analysis status panel after extraction policy is designed.

## 12. Implementation Non-Goals

WORKSPACE-008 does not implement:

- Project Overview UI.
- Backend overview routes.
- Project creation.
- Project selector/library.
- Editor changes.
- Extractor logic.
- Dramatica-specific logic.
- Runtime project files under `projects/`.
- OMI records.
- Memory/canon runtime files.
- JSONL records.
- Training or fine-tuning.
- Ollama/live model verification.
- Package/dependency changes.
