# Project Workspace Foundation Spec

## 1. Purpose

This specification defines `WORKSPACE-001`, the first detailed implementation planning handoff for the pre-Dramatica Project Workspace Foundation.

This is documentation only. It does not implement backend code, frontend code, tests, package changes, extractors, Dramatica-specific logic, project runtime files, OMI records, project memory/canon files, JSONL records, training data, model calls, or apply-promotion behavior.

The Project Workspace Foundation is the next product milestone after the current MVP foundation is accepted. Its purpose is to make the app a usable writing-project workspace before expanding Dramatica-specific analysis, advanced extractor dependencies, graph/timeline visualization, RunPod work, Books 4-5, or fine-tuning.

The app remains analysis-only. It may store, edit, save, reload, and organize owner-authored prose, but the AI must never write, rewrite, continue, imitate, polish, improve, or extend story prose.

Standard refusal message:

`I can analyze structure and ask diagnostic questions, but I cannot write or rewrite story prose.`

## 2. First Usable Workspace Target

The first usable workspace should let the writer:

- Create a new writing project from scratch.
- Create a project through OMI-guided idea capture.
- Select and open projects from a local project library.
- Create, edit, save, and reload owner-authored project material.
- Organize material into chapters, scenes, notes, and project materials.
- See project-specific pages for overview, writing materials, OMI, and approved memory/canon.
- Keep owner-authored prose separate from AI output.
- Keep pending candidates separate from approved canon.
- Avoid any AI prose-generation controls.

Minimum success means a writer can start a blank project, add owner-authored scene/note material, reopen it, and navigate the project without needing Dramatica-specific analysis or a fine-tuned model.

## 3. Product Layer Separation

The implementation must preserve these layers:

1. **Layer A: Owner-authored prose storage and editing**
   - The writer can create, edit, save, reload, and organize their own prose.
   - Owner-authored scene/chapter/note/material content is allowed app content.
   - Owner-authored content fields must not be treated as assistant prose-generation requests.

2. **Layer B: AI-assisted analysis of owner-authored material**
   - The app/AI may analyze owner-authored prose and project materials.
   - Analysis output is diagnostic, structural, candidate-only, and separate from prose fields.

3. **Layer C: Candidate extraction**
   - Future extraction may suggest characters, locations/settings, timeline events, important objects, organizations, relationships, plot threads, unresolved questions, navigation summaries, continuity/consistency flags, and possible contradictions.
   - Candidates should include evidence/provenance where practical.

4. **Layer D: Owner approval**
   - The owner can approve, reject, revise, archive, merge, split, mark uncertain, or request more evidence.
   - Pending, rejected, archived, duplicate, and uncertain candidates are not canon.

5. **Layer E: Approved project memory/canon**
   - Approved project knowledge becomes project-local memory/canon only through explicit owner-controlled promotion and a future apply-promotion step.
   - Approved canon/memory pages read approved records only.

6. **Layer F: Future Dramatica-specific analysis**
   - Dramatica/storyform, throughline, IC/RS, CIPS/dynamics, and fine-tuned analyst model work remains deferred.
   - General continuity, timeline, relationship, and plot assistance must not be labeled as Dramatica proof.

## 4. Project Creation Flows

### Flow A: Blank Project Creation

Blank project creation is the simplest first path.

Required flow:

1. Owner opens project creation.
2. Owner enters at minimum a project title.
3. App derives a filesystem-safe `project_id`.
4. Owner can accept or edit the proposed `project_id` before creation.
5. App validates `project_id` as a single safe path component.
6. App creates project metadata and the default empty workspace structure.
7. App opens the Project Overview for the new project.

Minimum project metadata:

- `schema_version`
- `project_id`
- `title`
- `status`
- `created_at`
- `updated_at`
- `creation_mode: "blank"`
- `owner_approved_truth_policy`

Blank project creation must not:

- Require Dramatica/storyform data.
- Generate premise prose, chapter prose, scene prose, dialogue, or summaries.
- Create candidate/canon records silently.
- Create training records or update dataset files.

### Flow B: OMI-Guided Project Creation

OMI-guided project creation helps organize owner-provided ideas into setup candidates. It must not author story prose.

Required flow:

1. Owner enters an owner-authored idea in an OMI-guided project setup flow.
2. OMI stores or stages the raw idea as owner input, not assistant output.
3. The app proposes setup candidates only, such as title candidates, project metadata candidates, genre/format labels, planning-note candidates, or diagnostic questions.
4. Setup candidates are visibly labeled as candidates.
5. Owner approves, rejects, or revises setup fields.
6. App creates the project only after explicit owner confirmation.
7. Approved setup metadata may populate `project.json`.
8. OMI raw idea/candidate records remain separate from project canon.
9. App opens the Project Overview for the new project.

OMI-guided creation may use:

- Owner-provided title or title candidate.
- Owner-provided description as metadata if explicitly approved.
- Owner-approved format/status tags.
- Owner-approved diagnostic project setup answers.

OMI-guided creation must not:

- Generate story prose.
- Generate sample scenes, chapters, dialogue, openings, endings, blurbs, or style examples.
- Treat setup candidates as canon.
- Mutate `memory/*.json`, `bible.json`, `storyform.json`, scenes, chapters, notes, or materials without explicit owner action.

If durable OMI records are required before a `project_id` exists, that requires a later pre-project inbox/storage task. The first implementation can keep setup data in wizard state until the owner confirms project creation, then write project-local OMI records under the new project.

## 5. Project Library and Selector

The first project selector/library should support:

- Listing local projects.
- Opening an existing project.
- Showing project title.
- Showing `project_id`.
- Showing last modified date.
- Showing basic counts for chapters, scenes, notes/materials, OMI candidates, and approved memory records where available.
- Showing creation mode where available: `blank`, `omi_guided`, or `imported`.
- Handling missing/corrupt project metadata without crashing.
- Preventing path traversal and unsafe project IDs.
- Avoiding accidental project deletion.

Project library implementation target:

- `projects/index.json` can exist as a rebuildable index.
- The index should be rebuildable from project folders and `project.json` where practical.
- `projects/index.json` is navigation metadata, not story truth.
- Corrupt or missing metadata should show a repair/import-needed state, not silently invent project truth.

Deletion/archive policy:

- First implementation should not expose permanent delete.
- Future archive can set `project.json.status = "archived"` and hide archived projects by default.
- Future delete must require explicit confirmation and should be a separate task.

## 6. Workspace Pages and Views

The first implementation should expose these navigation targets.

### Required Functional Pages

These pages should be usable in the first workspace implementation:

- **Project Library / Selector**
  - Lists projects and opens a selected project.

- **Project Overview**
  - Shows metadata, current counts, recent chapters/scenes/notes, OMI status summary, approved memory summary, and warnings about missing/corrupt metadata.
  - Must not imply pending candidates are approved truth.

- **Chapters / Scenes**
  - Lets the owner create, select, edit metadata for, order, save, reload, and navigate chapters/scenes.
  - Scene prose fields are owner-authored content only.

- **Notes / Materials**
  - Lets the owner create, select, edit, save, reload, and organize notes/materials.
  - Notes/materials are owner-authored or owner-supplied project material, not canon by default.

- **OMI Ideas and Candidates**
  - Shows guided project setup ideas/candidates and later story-knowledge candidates.
  - Candidate status, owner decision, provenance, and destination must be visible.
  - Dedicated page planning: `docs/roadmap/omi_ideas_candidates_page_spec.md`.

- **Approved Project Memory / Canon**
  - Shows approved memory/canon categories and empty states.
  - Reads only approved memory/canon records after future apply-promotion exists.
  - Before apply-promotion exists, it should clearly say no approved memory/canon records exist yet.
  - Shared cross-linking, `memory/index.json`, category registry, count snapshots, and non-destructive health warning planning are defined in `docs/roadmap/project_memory_canon_cross_linking_health_spec.md`.

### Required Navigation Entries With Placeholder Support

These pages should be represented early but may start as empty-state placeholders until candidate extraction, owner approval, and memory/canon application exist:

- **Characters**
- **Locations / Settings**
- **Timeline**
- **Plot Threads**
- **Objects / Items**
- **Continuity / Consistency**
- **Approved Contradictions**
- **Approved Scene / Event / Causality Review**
- **Open Questions**
- **Relationships**
- **Organizations / Groups**
- **Annotations / Evidence / Provenance**

Placeholder requirements:

- Label the page as approved-memory-only or candidate-review-only.
- Do not read pending candidates as canon.
- Do not show generated fixes or rewrite suggestions.
- Link to OMI Ideas and Candidates when the relevant records are pending review.

## 7. Chapter, Scene, Note, and Material Model

### Common Record Fields

Every workspace record should include:

- Stable ID.
- `project_id`.
- `schema_version`.
- Human-readable title or label.
- `status`.
- `created_at`.
- `updated_at`.
- `created_by: "owner"` for owner-authored content.
- `source_type`.
- Optional tags.
- Optional ordering fields.
- Optional provenance.

Recommended status values:

- `draft`
- `active`
- `archived`
- `needs_review`
- `deleted_by_owner`

### Chapter Record

Target path:

```text
projects/{project_id}/chapters/{chapter_id}.json
```

Minimum fields:

```json
{
  "schema_version": "0.1.0",
  "project_id": "example",
  "chapter_id": "chapter_001",
  "title": "Chapter 1",
  "order": 1,
  "status": "draft",
  "scene_ids": [],
  "created_at": "2026-06-07T00:00:00Z",
  "updated_at": "2026-06-07T00:00:00Z",
  "owner_metadata": {},
  "navigation_summary": null
}
```

Rules:

- Chapter records organize scenes.
- Chapter records do not contain generated prose.
- The first implementation should treat `chapter.scene_ids` as the canonical order and use `scene_metadata.chapter_id` as a consistency aid.
- If both chapter and scene metadata contain links, inconsistency should be reported as a repairable metadata issue.

### Scene Content and Metadata

Target paths:

```text
projects/{project_id}/scenes/{scene_id}.md
projects/{project_id}/scene_metadata/{scene_id}.json
```

Minimum scene metadata fields:

```json
{
  "schema_version": "0.1.0",
  "project_id": "example",
  "scene_id": "scene_001",
  "chapter_id": "chapter_001",
  "title": "Opening Scene",
  "order": 1,
  "status": "draft",
  "content_path": "scenes/scene_001.md",
  "content_source": "owner_authored",
  "created_at": "2026-06-07T00:00:00Z",
  "updated_at": "2026-06-07T00:00:00Z",
  "last_saved_at": "2026-06-07T00:00:00Z",
  "navigation_summary_candidate_id": null,
  "approved_navigation_summary": null,
  "tags": []
}
```

Rules:

- `scenes/{scene_id}.md` stores owner-authored prose.
- AI output must not be written into `scenes/{scene_id}.md`.
- Scene metadata may reference navigation-summary candidates or approved summaries.
- Future summaries are navigation aids only, not replacement prose.

### Note Record

Target paths:

```text
projects/{project_id}/notes/{note_id}.md
projects/{project_id}/note_metadata/{note_id}.json
```

Minimum note metadata fields:

```json
{
  "schema_version": "0.1.0",
  "project_id": "example",
  "note_id": "note_001",
  "title": "Planning Note",
  "status": "draft",
  "content_path": "notes/note_001.md",
  "content_source": "owner_authored",
  "created_at": "2026-06-07T00:00:00Z",
  "updated_at": "2026-06-07T00:00:00Z",
  "tags": []
}
```

Rules:

- Notes store owner-authored planning material.
- Notes are not canon by default.
- Extracted knowledge from notes must enter OMI as candidates.

### Material Record

Target paths:

```text
projects/{project_id}/materials/{material_id}.md
projects/{project_id}/material_metadata/{material_id}.json
```

Minimum material metadata fields:

```json
{
  "schema_version": "0.1.0",
  "project_id": "example",
  "material_id": "material_001",
  "title": "Research Material",
  "material_type": "note",
  "status": "draft",
  "content_path": "materials/material_001.md",
  "content_source": "owner_supplied",
  "created_at": "2026-06-07T00:00:00Z",
  "updated_at": "2026-06-07T00:00:00Z",
  "provenance": {},
  "tags": []
}
```

Recommended `material_type` values:

- `note`
- `research`
- `reference`
- `outline`
- `worldbuilding`
- `source_link`
- `other`

Rules:

- Materials can be owner-authored or owner-supplied.
- Materials are not approved canon by default.
- External/raw source text and training/book artifacts must not be copied into project materials without a separate provenance/licensing review.

## 8. Target File Layout

This target builds on `docs/roadmap/project_file_model.md`, `docs/roadmap/omi_storage_model.md`, and `docs/roadmap/project_memory_canon_storage_model.md`.

Future target shape:

```text
projects/
  index.json
  {project_id}/
    project.json
    chapters/
      {chapter_id}.json
    scenes/
      {scene_id}.md
    scene_metadata/
      {scene_id}.json
    notes/
      {note_id}.md
    note_metadata/
      {note_id}.json
    materials/
      {material_id}.md
    material_metadata/
      {material_id}.json
    omi/
      ideas/
        {idea_id}.json
      candidates/
        {candidate_id}.json
      promotions/
        {promotion_id}.json
      index.json
    memory/
      characters.json
      locations.json
      objects.json
      organizations.json
      timeline.json
      relationships.json
      plot_threads.json
      summaries.json
      annotations.json
      open_questions.json
      continuity_warnings.json
      contradictions.json
      index.json
```

Compatibility notes:

- Existing `bible.json` and `storyform.json` may remain for current Story Check and later Dramatica/NCP context.
- Dramatica/storyform files are not required to create a blank Project Workspace Foundation project.
- `memory/*.json` files should not exist until a future apply-promotion task creates approved records.
- OMI promotion records are audit records, not canon by themselves.
- `projects/index.json` is a project-library convenience and should be rebuildable.

## 9. Owner-Authored Prose Safety Rules

Allowed:

- Owner creates scene prose.
- Owner edits scene prose.
- Owner saves/reloads scene prose.
- Owner creates notes/materials.
- Owner saves/reloads owner-authored notes/materials.
- App stores and organizes owner-authored project material.

Required guardrail behavior:

- No-prose guards must not block chapter/scene/note/material save routes as if owner content were assistant request intent.
- Guard freeform assistant/model request fields before model calls.
- Sanitize model-authored output before display or persistence where future model paths exist.
- Keep AI analysis output out of prose fields.
- Show analysis/candidates/diagnostics separately from editor content.

Prohibited controls and outputs:

- Continue this scene.
- Rewrite this.
- Polish this.
- Improve this prose.
- Make this better.
- Write the next chapter.
- Draft dialogue.
- Imitate this style.
- Insert AI text into the editor.
- Apply AI rewrite to scene.

If a user requests AI-written or AI-rewritten story prose, use the standard refusal message.

## 10. Candidate and Canon Display Rules

Display rules:

- Pending candidates must be visibly labeled as candidates.
- Owner-approved memory/canon must be visibly labeled as approved.
- Rejected, archived, duplicate, uncertain, and pending candidates must not appear as canon.
- OMI promotion records must be labeled as audit/intent records, not canon.
- Project pages must not imply pending candidates are approved truth.
- Empty approved-memory pages should say no approved records exist yet.
- Candidate pages should show status, owner decision, evidence/provenance, source, and destination where available.

Promotion rules:

- Creating a candidate is not approval.
- Approval is not durable canon by itself.
- Recording a promotion is not durable canon by itself.
- Future apply-promotion must be explicit and fail closed.
- Future apply-promotion must write approved memory/canon only after owner approval, destination, evidence/provenance, and final confirmation.
- Future apply-promotion must never mutate owner-authored prose fields.

## 11. Implementation Task Breakdown

The first workspace implementation should follow this sequence:

| ID | Task | Planning output |
| --- | --- | --- |
| WORKSPACE-001 | Project Workspace Foundation Spec | This document |
| WORKSPACE-002 | Project creation flow | `docs/roadmap/project_creation_flow_spec.md` defines blank and OMI-guided creation API/UI/storage planning |
| WORKSPACE-003 | Project selector/library | `docs/roadmap/project_selector_library_spec.md` defines scan-first local project discovery, metadata cards/lists, opening/switching behavior, invalid/corrupt handling, archive/delete planning, API/UI planning, path safety, and future tests |
| WORKSPACE-004 | OMI-guided project creation and idea capture | `docs/roadmap/omi_guided_project_creation_spec.md` defines owner-authored setup inputs, setup candidate classes, wizard flow, staged setup storage, OMI-to-project handoff, API/UI planning, no-prose/no-silent-promotion rules, and future tests |
| WORKSPACE-005 | Chapter and scene data model | `docs/roadmap/chapter_scene_data_model_spec.md`; chapter records, scene Markdown compatibility, scene metadata, IDs, ordering/movement, save/reload, API/UI planning, future extraction provenance, and migration/legacy behavior |
| WORKSPACE-006 | Notes/materials data model | `docs/roadmap/notes_materials_data_model_spec.md`; note/material body files, separate metadata, IDs, organization/linking, save/reload, local search/filter, reference/license boundaries, future extraction provenance, and legacy/recovery behavior |
| WORKSPACE-007 | User-authored document editor and save/reload workflow | `docs/roadmap/user_authored_document_editor_workflow_spec.md`; shared scene/note/material editor state, save/reload semantics, unsaved-change protections, conflict detection, no-prose UI safety, analysis separation, API/UI planning, and future tests |
| WORKSPACE-008 | Project overview page | `docs/roadmap/project_overview_page_spec.md`; safe landing page content, sections, quick actions, recent documents, OMI status, approved memory/canon snapshot, health warnings, API/UI planning, and future tests |
| WORKSPACE-009 | Chapters/scenes page | `docs/roadmap/chapters_scenes_page_spec.md`; page layout, chapter operations, scene operations, shared editor behavior, ordering/consistency behavior, local search/filter, analysis/extraction separation, API/UI planning, and future tests |
| WORKSPACE-010 | Notes/materials page | `docs/roadmap/notes_materials_page_spec.md`; page layout, note operations, material operations, shared editor behavior, organization/linking behavior, local search/filter, analysis/extraction separation, provenance/license warnings, API/UI planning, and future tests |
| WORKSPACE-011 | Project memory/canon page structure | `docs/roadmap/project_memory_canon_page_structure_spec.md`; approved-only page purpose, memory/canon concepts, approved-vs-candidate labeling, category cards, promotion-record snapshots, empty states before apply-promotion, API/UI planning, health warnings, and future tests |
| WORKSPACE-012 | OMI ideas/candidates page | `docs/roadmap/omi_ideas_candidates_page_spec.md`; owner raw ideas, candidate review, evidence/provenance, promotion readiness, promotion audit records, filters/search, health warnings, API/UI planning, and future tests |
| WORKSPACE-013 | Approved characters page | `docs/roadmap/approved_characters_page_spec.md`; approved-character record display, evidence/provenance panel, linked sources panel, candidate backlog snapshot, warning states, API/UI planning, no-prose/no-silent-promotion boundaries, and future tests |
| WORKSPACE-014 | Approved locations/settings page | `docs/roadmap/approved_locations_settings_page_spec.md`; approved-location record display, evidence/provenance panel, linked sources panel, place hierarchy placeholder, scene usage snapshot, candidate backlog snapshot, warning states including parent/child cycle detection, API/UI planning, no-prose/no-silent-promotion boundaries, and future tests |
| WORKSPACE-015 | Approved timeline page | `docs/roadmap/approved_timeline_page_spec.md`; approved-timeline-event record display, evidence/provenance panel, linked sources panel, chronology/ordering placeholder, cause/effect placeholder, scene usage snapshot, candidate backlog snapshot, warning states including sequence collisions, chronology conflicts, and cause/effect cycles, API/UI planning, no-prose/no-silent-promotion boundaries, and future tests |
| WORKSPACE-016 | Approved plot threads page | `docs/roadmap/approved_plot_threads_page_spec.md`; approved-plot-thread record display, evidence/provenance panel, linked sources panel, linked timeline/scene snapshot, related characters/locations/objects snapshot, related open-questions and continuity-warnings placeholders, candidate backlog snapshot, warning states including thread status conflicts, API/UI planning, no-prose/no-silent-promotion boundaries, and future tests |
| WORKSPACE-017 | Continuity/consistency page | `docs/roadmap/continuity_consistency_page_spec.md`; approved continuity/consistency issue display, evidence/provenance panel, linked sources panel, linked story-knowledge snapshot, resolution placeholder, candidate backlog snapshot, warning states including status/resolution conflicts, API/UI planning, no-prose/no-silent-promotion boundaries, and future tests |
| WORKSPACE-018 | Approved open questions page | `docs/roadmap/approved_open_questions_page_spec.md`; approved open-question record display, evidence/provenance panel, linked sources panel, linked story-knowledge snapshot, related plot-thread/continuity snapshot, owner-answer/resolution placeholder, candidate backlog snapshot, warning states including answer/resolution conflicts and related-question link issues, API/UI planning, no-prose/no-silent-promotion boundaries, and future tests |
| WORKSPACE-019 | Approved relationships page | `docs/roadmap/approved_relationships_page_spec.md`; approved-relationship record display, participant snapshot, linked story-knowledge snapshot, related plot/timeline/open-question/continuity snapshots, evidence/provenance panel, candidate backlog snapshot, warning states including participant/type/status conflicts, API/UI planning, no-prose/no-silent-promotion boundaries, and explicit non-Dramatica Relationship Story boundaries |
| WORKSPACE-020 | Approved organizations/groups page | `docs/roadmap/approved_organizations_groups_page_spec.md`; approved organization/group record display, members/leadership snapshot, hierarchy snapshot, linked story-knowledge snapshot, related relationship/plot/timeline/open-question/continuity snapshots, evidence/provenance panel, candidate backlog snapshot, warning states, API/UI planning, no-prose/no-silent-promotion boundaries, and explicit non-Dramatica structural-claim boundaries |
| WORKSPACE-021 | Approved objects/items page | `docs/roadmap/approved_objects_items_page_spec.md`; approved object/item record display, ownership/holder snapshot, location/movement snapshot, linked story-knowledge snapshot, related plot/timeline/open-question/continuity snapshots, evidence/provenance panel, candidate backlog snapshot, warning states, API/UI planning, no-prose/no-silent-promotion boundaries, and explicit non-Dramatica structural/thematic-claim boundaries |
| WORKSPACE-022 | Approved annotations/evidence/provenance page | `docs/roadmap/approved_annotations_evidence_provenance_page_spec.md`; approved annotation/evidence/provenance record display, source locator panel, evidence span panel, provenance chain panel, linked approved-memory snapshot, linked candidate/promotion audit snapshot, copyright/source safety notice, candidate backlog snapshot, warning states, API/UI planning, no-prose/no-silent-promotion boundaries, and explicit non-Dramatica proof boundaries |
| WORKSPACE-023 | Approved contradictions page | `docs/roadmap/approved_contradictions_page_spec.md`; approved contradiction record display, claim pair panel, evidence/provenance panel, linked sources panel, linked approved-memory/story-knowledge snapshots, related continuity/open-question snapshots, resolution placeholder, candidate backlog snapshot, warning states, API/UI planning, no-prose/no-silent-promotion boundaries, and explicit non-Dramatica proof boundaries |
| WORKSPACE-024 | Approved scene/event/causality review page | `docs/roadmap/approved_scene_event_causality_review_spec.md`; approved scene-review, event/action, and causality-note record display, source locator panel, cause/effect panel, evidence/provenance panel, linked sources panel, linked approved-memory/story-knowledge snapshots, related timeline/plot/continuity/contradiction snapshots, candidate backlog snapshot, warning states, API/UI planning, no-prose/no-silent-promotion boundaries, and explicit non-Dramatica proof boundaries |
| WORKSPACE-025 | Tests for user-authored prose save without no-prose overblocking | Future test task |
| WORKSPACE-026 | Tests for no AI prose generation | Future test task |
| WORKSPACE-027 | Tests for no silent promotion | Future test task |
| WORKSPACE-028 | Project-local canon/memory visibility tests | Future test task |

Implementation should not start Dramatica-specific analysis, extractor dependencies, or memory/canon apply-promotion before the basic workspace create/select/save/reload flows exist.

## 12. Acceptance Checklist for First Usable Workspace

The first implementation can be accepted when:

- A blank project can be created from a title.
- The app generates or accepts a filesystem-safe `project_id`.
- A project can be opened from the local project library.
- Missing/corrupt project metadata is handled without crashing.
- A chapter can be created.
- A scene can be created under a chapter.
- A scene can be edited, saved, reloaded, and reopened.
- A note can be created, edited, saved, reloaded, and reopened.
- Notes/materials are visibly separate from approved canon.
- Project Overview displays selected project metadata and counts.
- Chapters/Scenes page supports basic organization and navigation.
- Notes/Materials page supports basic organization and navigation.
- OMI Ideas and Candidates page or panel is visible for project setup/candidate review.
- Approved Project Memory/Canon page or shell is visible and does not show pending candidates as canon.
- Characters, Locations/Settings, Objects/Items, Timeline, Plot Threads, Continuity/Consistency, Approved Contradictions, Approved Scene / Event / Causality Review, Open Questions, Relationships, Organizations/Groups, and Annotations/Evidence/Provenance pages have at least clear empty states or placeholders.
- Owner-authored prose saves are not blocked by no-prose guards.
- No AI prose-generation controls are exposed.
- AI output is not inserted into editor content.
- Candidate/canon labels are clear.
- No silent promotion occurs.
- No project memory/canon runtime files are required before apply-promotion exists.
- No Dramatica-specific logic is required.
- No training data, JSONL records, dataset manifest updates, package installs, model calls, or fine-tuning are required.

## 13. Deferred Decisions

These remain follow-up decisions for later implementation tasks:

- Exact `project_id` slug collision strategy.
- Whether `projects/index.json` is eagerly maintained or rebuilt on library load.
- Whether project creation creates all empty directories immediately or lazily on first use.
- Whether OMI-guided setup uses temporary wizard state or a durable pre-project inbox before project confirmation. WORKSPACE-004 recommends a first implementation with staged setup state converted into project-local OMI records only after final project creation confirmation.
- Whether chapter ordering lives only in chapter records, in a separate index, or in both with consistency checks.
- Whether scenes can belong to multiple chapters or exactly one chapter.
- Whether notes and materials share one metadata model or stay separate.
- Whether rich text editor storage remains Markdown/plain text or gains a separate rich-text representation.
- Whether candidate extraction triggers are manual-only, after-save, scheduled, or hybrid.
- Which approved memory/canon category pages must be fully functional before extraction exists.
- How navigation summaries are written, reviewed, approved, and displayed without becoming generated story prose.
- How contradictions are shown: side-by-side evidence, page-level lists, inline flags, OMI candidate queues, or a combination. WORKSPACE-023 recommends a future approved-only page with claim-pair and evidence/provenance panels, while pending contradiction candidates remain in OMI.
- How approved scene/event/causality review records are stored: separate `memory/scene_reviews.json`, `memory/events.json`, `memory/actions.json`, `memory/causality.json`, a shared scene-events store, timeline extensions, or an approved audit store. WORKSPACE-024 recommends a future approved-only page but defers the exact runtime schema and file layout.

## 14. Related Specifications

- `docs/master_plan.md`
- `docs/plan.md`
- `docs/roadmap/task_backlog.md`
- `docs/roadmap/phase_map.md`
- `docs/roadmap/project_file_model.md`
- `docs/roadmap/project_creation_flow_spec.md`
- `docs/roadmap/project_selector_library_spec.md`
- `docs/roadmap/omi_guided_project_creation_spec.md`
- `docs/roadmap/omi_mvp_schema_lifecycle.md`
- `docs/roadmap/omi_storage_model.md`
- `docs/roadmap/omi_story_knowledge_candidate_expansion.md`
- `docs/roadmap/writer_assistant_core_candidate_schemas.md`
- `docs/roadmap/project_memory_canon_storage_model.md`
- `docs/roadmap/approved_objects_items_page_spec.md`
- `docs/roadmap/approved_annotations_evidence_provenance_page_spec.md`
- `docs/roadmap/approved_contradictions_page_spec.md`
- `docs/roadmap/approved_scene_event_causality_review_spec.md`
- `docs/roadmap/mvp_completion_test_matrix.md`
- `docs/roadmap/risk_register.md`
- `docs/roadmap/open_questions.md`
