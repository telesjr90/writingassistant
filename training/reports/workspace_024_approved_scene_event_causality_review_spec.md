# WORKSPACE-024 Approved Scene / Event / Causality Review Spec Report

Date/time: 2026-06-10 11:50 AM UTC-7

## Files Inspected

- AGENTS.md
- .cursorrules
- .cursor/rules/project-boundaries.mdc
- .cursor/rules/graphify.mdc
- .cursor/rules/lean-ctx.mdc
- .cursor/rules/workspace-task-safety.mdc
- .cursor/rules/documentation-task-rules.mdc
- CLAUDE.md
- docs/master_plan.md
- docs/plan.md
- docs/roadmap/project_workspace_foundation_spec.md
- docs/roadmap/project_overview_page_spec.md
- docs/roadmap/chapters_scenes_page_spec.md
- docs/roadmap/notes_materials_page_spec.md
- docs/roadmap/project_memory_canon_page_structure_spec.md
- docs/roadmap/omi_ideas_candidates_page_spec.md
- docs/roadmap/approved_characters_page_spec.md
- docs/roadmap/approved_locations_settings_page_spec.md
- docs/roadmap/approved_timeline_page_spec.md
- docs/roadmap/approved_plot_threads_page_spec.md
- docs/roadmap/continuity_consistency_page_spec.md
- docs/roadmap/approved_open_questions_page_spec.md
- docs/roadmap/approved_relationships_page_spec.md
- docs/roadmap/approved_organizations_groups_page_spec.md
- docs/roadmap/approved_objects_items_page_spec.md
- docs/roadmap/approved_annotations_evidence_provenance_page_spec.md
- docs/roadmap/approved_contradictions_page_spec.md
- docs/roadmap/project_memory_canon_storage_model.md
- docs/roadmap/writer_assistant_core_candidate_schemas.md
- docs/roadmap/omi_story_knowledge_candidate_expansion.md
- docs/roadmap/omi_mvp_schema_lifecycle.md
- docs/roadmap/omi_storage_model.md
- docs/roadmap/project_file_model.md
- docs/roadmap/task_backlog.md
- docs/roadmap/phase_map.md
- docs/roadmap/open_questions.md
- docs/roadmap/risk_register.md
- docs/roadmap/decision_log.md
- docs/roadmap/mvp_completion_test_matrix.md

Context prep:

- ai_context/repomix-current-task-context.xml was not present.
- Listed graphify-out/GRAPH_REPORT.md report paths were not present.
- Graphify was available from WSL and returned high-level roadmap links for memory/canon, timeline, scene metadata, OMI, and candidate/canon separation. Targeted roadmap reads supplied the detailed source context.

Runtime files were not edited.

## Files Modified

- docs/master_plan.md
- docs/plan.md
- docs/roadmap/approved_scene_event_causality_review_spec.md
- docs/roadmap/decision_log.md
- docs/roadmap/mvp_completion_test_matrix.md
- docs/roadmap/omi_story_knowledge_candidate_expansion.md
- docs/roadmap/open_questions.md
- docs/roadmap/phase_map.md
- docs/roadmap/project_file_model.md
- docs/roadmap/project_memory_canon_page_structure_spec.md
- docs/roadmap/project_memory_canon_storage_model.md
- docs/roadmap/project_overview_page_spec.md
- docs/roadmap/project_workspace_foundation_spec.md
- docs/roadmap/risk_register.md
- docs/roadmap/task_backlog.md
- docs/roadmap/writer_assistant_core_candidate_schemas.md
- training/reports/workspace_024_approved_scene_event_causality_review_spec.md

## Spec Created / Updated

Created docs/roadmap/approved_scene_event_causality_review_spec.md.

## Page / Spec Purpose

The new spec defines a future approved-only page for owner-approved scene-level review records, event/action records, and causality notes. It distinguishes those approved records from OMI candidates, from owner-authored scene editing, from chronology-focused timeline display, and from contradiction/continuity/open-question ownership.

The page is explicitly not a scene summary generator, timeline visualizer, causal inference engine, generated fix page, rewrite page, semantic-search page, extractor page, or Dramatica proof page.

## Approved Scene / Event / Causality Display Model

The spec defines display fields for approved records, including record identity, type, title, review/event/action/causality types, status, scope, approved descriptions, source chapter/scene/note/material IDs, source locator and hash fields, owner-approved event/action summaries, cause/effect and related-event IDs, related timeline/plot/continuity/contradiction/story-knowledge IDs, affected scenes/chapters, first/latest seen source, evidence/provenance summary, certainty labels, owner notes, resolution status, timestamps, approval metadata, source candidate IDs, promotion record IDs, revision/supersession fields, tags, and notes.

Display rules require owner-approved or explicitly approved text only. Missing fields must be labeled honestly as Unknown, Not approved yet, Not recorded, or Locator unavailable.

## Relationship to Existing Pages

The spec separates page ownership:

- Chapters / Scenes owns authoring, navigation, save/reload, ordering, and owner-authored prose editing.
- Approved Timeline owns chronology/order-focused timeline_event_memory_record display.
- Approved Scene / Event / Causality Review owns scene-derived event/action/causality records, source-located review records, and owner-approved cause/effect links.
- Approved Plot Threads owns plot-thread status and linked event snapshots.
- Continuity / Consistency, Approved Open Questions, and Approved Contradictions own their issue, question, and conflict records.
- Approved Annotations / Evidence / Provenance owns evidence/provenance record display and source-safety policy.

## Sections

The spec defines the page header, boundary banner, approved scene review list, approved event/action list, causality notes list, record detail panel, source locator panel, cause/effect link panel, related timeline snapshot, related plot thread snapshot, related continuity/contradiction snapshot, linked approved memory snapshot, evidence/provenance panel, linked sources panel, candidate backlog snapshot, empty state, warning state, and future page link reference. Each section includes purpose, data source, candidate/canon boundary, no-prose boundary, empty state, and error state.

## Candidate / Canon Separation

Approved records are read only from future approved memory/audit stores such as memory/scene_reviews.json, memory/events.json, memory/actions.json, memory/causality.json, or equivalent stores.

OMI scene/event/action/causality candidates remain OMI candidates. Pending, rejected, archived, needs-revision, uncertain, duplicate, and approved-but-not-applied candidates do not appear as approved truth. Promotion records are audit-only unless future apply-promotion creates or updates approved memory.

The spec explicitly blocks inference of event type, action type, causal relation, status, source locator, linked records, evidence state, certainty, or Dramatica structure from candidate output.

## Operations

Allowed first-version operations are view-only/detail/filter/link operations over approved records, linked source documents, linked approved memory/canon records, linked adjacent approved pages, OMI audit links, cause/effect panels, evidence/provenance panels, and linked story-knowledge snapshots.

Future-only operations include editing approved records, merge/split, archive/restore, marking causal links resolved, apply-promotion, extraction, causal inference, generated summaries/explanations/fixes, scene rewrites, semantic search, source re-anchoring, timeline or causality visualization, contradiction detection, Dramatica proof classification, and JSONL/training conversion.

## Local Search / Filter Planning

Local search/filter is approved-record-only and deterministic over record IDs, types, titles, review/event/action/causality types, status, scope, source IDs, related record IDs, cause/effect IDs, linked approved story-knowledge IDs, source candidate IDs, promotion record IDs, tags, and approved descriptions.

The spec prohibits semantic search, model/Ollama calls, generated summaries, generated explanations, generated fixes, extraction, causal inference, re-anchoring, Dramatica classification, OMI creation, memory/canon mutation, JSONL creation, and training-data writes during search.

## Warning / Invalid-State Behavior

Warnings are non-destructive and include missing/corrupt memory files, unsupported schema, missing candidate/promotion/approved-memory references, broken source links, broken locators, hash mismatch, unsafe IDs, duplicate IDs, unsupported locator type, locator out of range, event/action/status/causality conflicts, broken cause/effect links, cycles/self-links where represented, broken related page links, unsafe excerpts, missing evidence, promotion records without approved memory, candidate backlog without approved records, unimplemented related pages/entities, and corrupt memory/index.json.

Warnings must not auto-repair, auto-delete, rewrite identity, retitle, infer events/actions/causality, re-anchor source text, invent evidence, generate summaries/explanations/fixes, promote candidates, mutate memory/canon, or leak host filesystem paths.

## API Planning

The spec documents future read-only route planning:

- GET /api/projects/{project_id}/memory/scene-events
- GET /api/projects/{project_id}/memory/scene-events/{record_id}
- GET /api/projects/{project_id}/memory/scene-events/{record_id}/provenance
- GET /api/projects/{project_id}/memory/scene-events/health

It notes that later implementation may use one scene-events endpoint family, split scene-reviews/events/actions/causality endpoint families, or composition from a future memory/canon summary endpoint.

Each route group documents purpose, request shape, response shape, validation, path safety, candidate/canon boundary, no-prose boundary, source/evidence safety, and expected errors.

## Frontend Planning

The spec documents future components: ApprovedSceneEventCausalityReviewPage, SceneEventCausalityBoundaryBanner, ApprovedSceneReviewList, ApprovedEventActionList, CausalityNotesList, SceneEventCausalityRecordDetailPanel, SceneEventSourceLocatorPanel, CauseEffectLinkPanel, RelatedTimelineSnapshot, RelatedPlotThreadSnapshot, RelatedContinuityContradictionSnapshot, LinkedSceneEventApprovedMemorySnapshot, SceneEventEvidencePanel, SceneEventSourceLinksPanel, SceneEventCandidateBacklogSnapshot, SceneEventSearchFilterControls, SceneEventWarningsPanel, SceneEventEmptyState, and SceneEventFuturePagesReference.

The spec prohibits AI writing buttons, generated scene summary buttons, generated causal explanation buttons, generated fix buttons, rewrite buttons, semantic-search buttons in first version, event extraction controls, causal inference controls, Dramatica classification controls, training conversion controls, and promotion controls.

## Future Tests Identified

Future test categories include no memory directory and no approved records; loading approved records; excluding pending candidates and audit-only promotion records from approved truth; corrupt memory files; duplicate IDs; unsafe IDs; broken source links; unsupported/out-of-range locators; source hash mismatch; broken cause/effect links; cycles/self-links; broken cross-page links; candidate/promotion/memory link warnings; type/status/causality conflicts; unsafe excerpts; model-free local search/filter; no OMI creation; no memory/canon mutation; no promotion; no JSONL/training writes; no AI prose-generation controls; no generated summaries/explanations/fixes/rewrites; no invented events/actions/causal links/evidence; no extraction or causal inference; no source re-anchoring; and no Dramatica proof claims.

## Remaining Deferred Decisions

Deferred decisions include exact runtime schema, file layout, relationship to timeline records, allowed enums, memory envelope and migration behavior, endpoint composition, source locator strategy, cause/effect relation model, cycle-check timing, OMI filter strategy, source hash and source safety policies, apply-promotion behavior, owner-controlled edit/resolution workflow, future visualization strategy, semantic search placement, and any future Dramatica-specific taxonomy.

## Safety Confirmations

- No backend runtime code changed.
- No frontend runtime code changed.
- No tests changed.
- No package/dependency files changed.
- No dataset files changed.
- No JSONL/training records created.
- training/data/dataset_manifest.json was not updated.
- No training/fine-tuning run.
- No Ollama/live model call.
- No packages installed.
- No Dramatica-specific logic implemented.
- No runtime project files created.
- No OMI records created.
- No memory/canon files created.
- No staging.
- No commits.
