# WORKSPACE-020 Approved Organizations / Groups Page Spec Report

Date/time: 2026-06-10 09:50 America/Los_Angeles.

## Files Inspected

- `AGENTS.md`
- `CLAUDE.md`
- `.cursorrules`
- `.cursor/rules/project-boundaries.mdc`
- `.cursor/rules/graphify.mdc`
- `.cursor/rules/lean-ctx.mdc`
- `.cursor/rules/workspace-task-safety.mdc`
- `.cursor/rules/documentation-task-rules.mdc`
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

Graphify was available from the WSL shell and returned scoped roadmap context for approved memory/canon pages, OMI candidate boundaries, and existing approved category specs. The Repomix task context and generated Graphify report files were not accessible through the file read tool in this session, so the task continued with Graphify query output and targeted roadmap reads.

## Files Modified

- `docs/roadmap/approved_organizations_groups_page_spec.md`
- `training/reports/workspace_020_approved_organizations_groups_page_spec.md`
- `docs/master_plan.md`
- `docs/plan.md`
- `docs/roadmap/project_memory_canon_storage_model.md`
- `docs/roadmap/project_file_model.md`
- `docs/roadmap/writer_assistant_core_candidate_schemas.md`
- `docs/roadmap/omi_story_knowledge_candidate_expansion.md`
- `docs/roadmap/project_memory_canon_page_structure_spec.md`
- `docs/roadmap/project_overview_page_spec.md`
- `docs/roadmap/task_backlog.md`
- `docs/roadmap/phase_map.md`
- `docs/roadmap/decision_log.md`
- `docs/roadmap/risk_register.md`
- `docs/roadmap/mvp_completion_test_matrix.md`

## Spec Created

Created `docs/roadmap/approved_organizations_groups_page_spec.md` as the documentation-only WORKSPACE-020 handoff.

## Page Purpose

The future Approved Organizations / Groups page is planned as an approved-only project-local page for applied `organization_memory_record` or `group_memory_record` entries. It shows owner-approved organization/group memory/canon records as project truth, while routing extracted/manual/future model-assisted organization/group candidates to OMI.

## Approved Organization / Group Display Model

The spec defines display planning for approved fields including IDs, display title, organization type/status/scope, aliases, members, leaders, related characters, hierarchy links, allied/opposed organizations, related relationships, locations, objects, timeline events, plot threads, open questions, continuity issues, affected scenes/chapters, notes/materials, first/latest sources, evidence/provenance, confidence/certainty labels, owner notes, approval metadata, source candidate IDs, promotion record IDs, revision history, supersession metadata, tags, and notes.

Missing or unresolved fields must display as `Unknown`, `Not approved yet`, or `Not recorded`. Unapproved candidates, generated organization analysis, generated summaries, rewrite suggestions, scene suggestions, faction-fix suggestions, and Dramatica structural claims are prohibited.

## Page Sections

The spec defines these future sections: Page Header; Organizations / Groups Boundary Banner; Approved Organization List; Organization Detail Panel; Evidence / Provenance Panel; Linked Sources Panel; Members / Leadership Snapshot; Organization Hierarchy Snapshot; Linked Story Knowledge Snapshot; Related Relationship / Plot / Timeline Snapshot; Related Open Questions / Continuity Snapshot; Candidate Backlog Snapshot; Empty State; Warning State; Future Page Link Reference.

Each section documents purpose, data source, candidate/canon boundary, no-prose boundary, empty state, and error state.

## Candidate / Canon Separation

Approved organization/group truth is planned to load only from future approved memory stores such as `memory/organizations.json`, optional `memory/groups.json`, or equivalent applied memory/canon storage. OMI organization/group candidates stay in OMI. Pending, rejected, archived, needs-revision, approved-but-not-applied, and promotion-record-only states do not appear as approved organizations/groups.

Promotion records remain audit-only unless future apply-promotion creates or updates approved organization/group memory. Source candidate and promotion audit links may appear only as provenance. Organization type, status, hierarchy, membership, leadership, relationships, evidence state, related links, and certainty must not be inferred as truth from candidate output.

## Page Operations

Allowed first-version operations include viewing approved lists/details, local search/filter, opening linked source documents and approved related pages, opening related OMI candidate or promotion audit links as provenance, and showing members/leadership, hierarchy, and linked story-knowledge snapshots.

Future-only operations include editing approved organization/group memory, merge/split, archive/restore, mark resolved/changed, apply-promotion, extraction, organization graph visualization, organization/faction fixes, scene/dialogue rewrites, contradiction detection, and Dramatica structural classification.

## Local Search / Filter Planning

Search/filter is local, deterministic, and approved-record-only. Planned fields include display title, type, status, scope, aliases, members, leaders, related characters, parent/child organization IDs, tags, approved description, linked source IDs, affected scene/chapter IDs, linked relationship/location/object/timeline/plot-thread/open-question/continuity IDs, source candidate IDs, and promotion record IDs.

No semantic search, model/Ollama calls, generated summaries, generated organization analysis, extraction, contradiction detection, or Dramatica classification occurs during search.

## Warning / Invalid-State Behavior

The spec plans non-destructive warnings for missing/corrupt memory files, unsupported schema, missing source candidates, broken member/leader/character references, broken parent/child/allied/opposed organization links, hierarchy cycles, broken related entity/source links, duplicate IDs, unsafe IDs, type/status conflicts, membership/leadership conflicts, missing affected sources, promotion-record-only states, candidate-only states, unavailable related pages/entities, insufficient evidence, and corrupt `memory/index.json`.

Warnings must not auto-repair, auto-delete, rewrite identity, retitle, infer members/leaders, correct roles/status, resolve hierarchy, promote candidates, generate fixes/summaries/explanations, or leak host filesystem paths.

## API Planning

Future route group planning:

- `GET /api/projects/{project_id}/memory/organizations`
- `GET /api/projects/{project_id}/memory/organizations/{organization_id}`
- `GET /api/projects/{project_id}/memory/organizations/{organization_id}/provenance`
- `GET /api/projects/{project_id}/memory/organizations/health`

The spec notes that groups may be represented as `organization_type` values inside organizations, or by parallel group endpoints in a later decision. Each route section covers purpose, request shape, response shape, validation, path safety, candidate/canon boundary, no-prose boundary, and expected errors.

## Frontend Planning

Future components include `ApprovedOrganizationsGroupsPage`, `OrganizationsGroupsBoundaryBanner`, `ApprovedOrganizationList`, `ApprovedOrganizationListItem`, `OrganizationDetailPanel`, `OrganizationEvidencePanel`, `OrganizationSourceLinksPanel`, `OrganizationMembersLeadershipSnapshot`, `OrganizationHierarchySnapshot`, `OrganizationLinkedStoryKnowledgeSnapshot`, `OrganizationRelatedRelationshipPlotTimelineSnapshot`, `OrganizationRelatedQuestionsContinuitySnapshot`, `OrganizationCandidateBacklogSnapshot`, `OrganizationSearchFilterControls`, `OrganizationWarningsPanel`, `OrganizationEmptyState`, and `OrganizationFuturePagesReference`.

The spec prohibits AI writing buttons, generated organization analysis buttons, first-version generated graph buttons, and controls such as generate faction, fix organization, rewrite scene, generate group conflict, resolve hierarchy, explain faction arc, classify antagonist group, prove RS, or classify Dramatica role.

## Future Tests Identified

Future tests should cover empty/missing memory states, approved organization/group loading, candidate exclusion, promotion-record-only exclusion, corrupt memory warning, duplicate IDs, unsafe IDs, broken member/leader/source/entity links, hierarchy cycles, type/status conflicts, membership/leadership conflicts, related organization cycles, local search without model calls, no OMI creation, no memory/canon mutation, no promotion, no AI prose controls, no generated organization analysis/fixes/rewrites/summaries/explanations, no generated graph in first version, no Dramatica structural claims, and no JSONL/training writes.

## Remaining Deferred Decisions

- Whether groups remain `organization_type` values in `memory/organizations.json` or later get `memory/groups.json` and parallel route groups.
- Exact organization/group schema names, envelope version, and enum values.
- Exact frontend route names and unavailable-page behavior.
- Whether hierarchy/alliance/opposition links remain simple lists or later support graph data.
- Whether edit, merge/split, archive/restore, or apply-promotion flows live on this page or another memory management surface.
- How future Dramatica-specific organization/group classifications are stored without blending into generic story knowledge.

## Safety Confirmations

- No backend runtime code changed.
- No frontend runtime code changed.
- No tests changed.
- No package/dependency files changed.
- No dataset files changed.
- No JSONL/training records created.
- `training/data/dataset_manifest.json` unchanged.
- No training/fine-tuning run.
- No Ollama/live model call.
- No packages installed.
- No Dramatica-specific logic implemented.
- No runtime project files created.
- No OMI records created.
- No memory/canon files created.
- No staging performed.
- No commits performed.
