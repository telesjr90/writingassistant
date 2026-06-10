# WORKSPACE-021 Approved Objects / Items Page Spec Report

Date/time: 2026-06-10 17:14:25 UTC

## Files Inspected

- `.cursorrules`
- `.cursor/rules/project-boundaries.mdc`
- `.cursor/rules/graphify.mdc`
- `.cursor/rules/lean-ctx.mdc`
- `.cursor/rules/workspace-task-safety.mdc`
- `.cursor/rules/documentation-task-rules.mdc`
- `AGENTS.md`
- `CLAUDE.md`
- `docs/master_plan.md`
- `docs/plan.md`
- `docs/roadmap/project_workspace_foundation_spec.md`
- `docs/roadmap/project_overview_page_spec.md`
- `docs/roadmap/chapters_scenes_page_spec.md`
- `docs/roadmap/notes_materials_page_spec.md`
- `docs/roadmap/project_memory_canon_page_structure_spec.md`
- `docs/roadmap/omi_ideas_candidates_page_spec.md`
- `docs/roadmap/approved_characters_page_spec.md`
- `docs/roadmap/approved_locations_settings_page_spec.md`
- `docs/roadmap/approved_timeline_page_spec.md`
- `docs/roadmap/approved_plot_threads_page_spec.md`
- `docs/roadmap/continuity_consistency_page_spec.md`
- `docs/roadmap/approved_open_questions_page_spec.md`
- `docs/roadmap/approved_relationships_page_spec.md`
- `docs/roadmap/approved_organizations_groups_page_spec.md`
- `docs/roadmap/project_memory_canon_storage_model.md`
- `docs/roadmap/writer_assistant_core_candidate_schemas.md`
- `docs/roadmap/omi_story_knowledge_candidate_expansion.md`
- `docs/roadmap/omi_mvp_schema_lifecycle.md`
- `docs/roadmap/omi_storage_model.md`
- `docs/roadmap/project_file_model.md`
- `docs/roadmap/task_backlog.md`
- `docs/roadmap/phase_map.md`
- `docs/roadmap/decision_log.md`
- `docs/roadmap/open_questions.md`
- `docs/roadmap/risk_register.md`
- `docs/roadmap/mvp_completion_test_matrix.md`

Repomix and Graphify report files were attempted through the prior task context but were not accessible. Graphify CLI queries were used from WSL and targeted roadmap relationships instead.

## Files Modified

- `docs/roadmap/approved_objects_items_page_spec.md`
- `training/reports/workspace_021_approved_objects_items_page_spec.md`
- `docs/master_plan.md`
- `docs/plan.md`
- `docs/roadmap/project_workspace_foundation_spec.md`
- `docs/roadmap/project_overview_page_spec.md`
- `docs/roadmap/project_memory_canon_page_structure_spec.md`
- `docs/roadmap/omi_ideas_candidates_page_spec.md`
- `docs/roadmap/approved_characters_page_spec.md`
- `docs/roadmap/approved_locations_settings_page_spec.md`
- `docs/roadmap/approved_timeline_page_spec.md`
- `docs/roadmap/approved_plot_threads_page_spec.md`
- `docs/roadmap/approved_open_questions_page_spec.md`
- `docs/roadmap/approved_relationships_page_spec.md`
- `docs/roadmap/approved_organizations_groups_page_spec.md`
- `docs/roadmap/project_memory_canon_storage_model.md`
- `docs/roadmap/writer_assistant_core_candidate_schemas.md`
- `docs/roadmap/omi_story_knowledge_candidate_expansion.md`
- `docs/roadmap/project_file_model.md`
- `docs/roadmap/task_backlog.md`
- `docs/roadmap/phase_map.md`
- `docs/roadmap/open_questions.md`
- `docs/roadmap/risk_register.md`
- `docs/roadmap/decision_log.md`
- `docs/roadmap/mvp_completion_test_matrix.md`

## Spec Created/Updated

Created `docs/roadmap/approved_objects_items_page_spec.md` as the WORKSPACE-021 documentation-only planning handoff for the future Approved Objects / Items page.

## Page Purpose

The future page shows owner-approved object/item memory/canon records for the selected project, links to evidence and related approved story knowledge, labels unresolved or missing fields honestly, and keeps object/item candidates in OMI.

## Approved Object/Item Display Model

The spec documents display fields including IDs, titles, type/status/scope, owner-approved description, aliases, owner/holder/creator/related character links, organization/relationship/location links, origin/current locations, timeline/plot/open-question/continuity links, affected scenes/chapters, notes/materials, source and provenance metadata, certainty labels, owner-approved non-Dramatica symbolic/thematic notes, approval metadata, source candidate and promotion audit links, revision/supersession metadata, tags, and notes.

Missing fields are labeled `Unknown`, `Not approved yet`, or `Not recorded`. Unapproved candidates, generated analysis, generated summaries, symbolic interpretations, rewrite suggestions, scene suggestions, and item-fix suggestions are prohibited from appearing as truth.

## Page Sections

The spec defines Page Header, Objects / Items Boundary Banner, Approved Object List, Object Detail Panel, Evidence / Provenance Panel, Linked Sources Panel, Ownership / Holder Snapshot, Location / Movement Snapshot, Linked Story Knowledge Snapshot, Related Plot / Timeline Snapshot, Related Open Questions / Continuity Snapshot, Candidate Backlog Snapshot, Empty State, Warning State, and Future Page Link Reference.

Each section documents purpose, data source, candidate/canon boundary, no-prose boundary, empty state, and error state.

## Candidate/Canon Separation

Approved records are future reads from `memory/objects.json`, `memory/items.json`, or equivalent approved memory/canon storage. OMI object/item candidates stay in OMI, pending/rejected/needs-revision candidates do not appear as approved objects/items, and promotion records are audit-only until future apply-promotion creates or updates approved memory.

Candidate backlog display is count/link-only. Object type, status, ownership, holder, location, movement, symbolic notes, evidence state, related links, and certainty must not be inferred as truth from candidate output.

## Page Operations

First-version operations are view-only: list/detail display, local approved-only search/filter, opening linked sources and approved pages when available, opening related OMI candidate or promotion audit links, and showing ownership/holder, location/movement, and linked story-knowledge snapshots.

Future-only operations include editing, merging/splitting, archiving/restoring, marking object/item resolution, apply-promotion, extraction, ownership/location inference, graph visualization, object/item fixes, scene/dialogue rewrites, contradiction detection, and Dramatica classification.

## Local Search/Filter Planning

Search/filter is deterministic and local over approved fields: title, type/status/scope, aliases, owner/holder/creator/related character IDs, organization/relationship/location IDs, origin/current location IDs, tags, approved description, linked source IDs, affected scene/chapter IDs, timeline/plot/open-question/continuity IDs, source candidate IDs, and promotion record IDs.

No semantic search, model/Ollama calls, generated summaries, generated object analysis, symbolic interpretation, extraction, contradiction detection, or Dramatica classification are allowed during search.

## Warning/Invalid-State Behavior

The spec defines non-destructive warnings for missing or corrupt memory files, unsupported schemas, broken candidate/source/entity links, duplicate or unsafe IDs, type/status conflicts, ownership/holder conflicts, location/movement conflicts, missing affected sources, broken/cyclic related-object links, promotion records without approved memory, OMI candidates without approved records, not-yet-implemented related pages, insufficient evidence, and corrupt memory indexes.

Warnings do not auto-repair, delete, rewrite identity, retitle, infer owners/holders/locations/symbolic meaning, correct roles/status, resolve continuity, promote candidates, or leak host filesystem paths.

## API Planning

The spec plans future read-only route groups or equivalent memory/canon summary composition:

- `GET /api/projects/{project_id}/memory/objects`
- `GET /api/projects/{project_id}/memory/objects/{object_id}`
- `GET /api/projects/{project_id}/memory/objects/{object_id}/provenance`
- `GET /api/projects/{project_id}/memory/objects/health`

Items may be represented as object types or by later parallel item endpoints. Each route group documents purpose, request/response shape, validation, path safety, candidate/canon boundary, no-prose boundary, and expected errors.

## Frontend Planning

The spec plans future components including `ApprovedObjectsItemsPage`, `ObjectsItemsBoundaryBanner`, `ApprovedObjectList`, `ApprovedObjectListItem`, `ObjectDetailPanel`, evidence/source/snapshot panels, search/filter controls, warnings, empty state, and future page references.

The UI must not include AI writing buttons, generated object analysis buttons, generated graph buttons, or controls that generate items, fix object continuity, rewrite scenes, generate clues, explain symbolism, classify thematic role, prove Issue/Variation, or classify Dramatica role.

## Future Tests Identified

Future tests cover empty/missing memory, approved record loading, candidate exclusion, promotion audit exclusion before apply-promotion, corrupt memory warnings, duplicate and unsafe IDs, broken links, conflict warnings, local search without model calls, no OMI creation, no memory/canon mutation, no promotion, no AI prose controls, no generated analysis/fixes/rewrites/summaries/symbolic explanations, no Dramatica claims, and no JSONL/training writes.

## Remaining Deferred Decisions

- Whether items are stored as `object_type` values in `memory/objects.json` or in parallel `memory/items.json` / item endpoints.
- Exact canonical schema for `object_memory_record` and `item_memory_record`.
- Whether related object links are represented in the first implementation.
- Exact frontend route naming and placement in project navigation.
- Whether symbolic/thematic notes remain on objects/items or move to a later approved non-Dramatica annotation model.
- Future implementation details for read-only routes, frontend components, and validation warnings.

## Safety Confirmations

- No backend runtime code changed.
- No frontend runtime code changed.
- No tests changed.
- No package/dependency files changed.
- No dataset files changed.
- No JSONL/training records created.
- No `training/data/dataset_manifest.json` updates occurred.
- No training/fine-tuning was run.
- No Ollama/live model calls were made.
- No packages were installed.
- No Dramatica-specific logic was implemented.
- No runtime project files were created.
- No OMI records were created.
- No memory/canon runtime files were created.
- No staging occurred.
- No commits occurred.
