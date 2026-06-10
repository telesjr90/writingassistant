# WORKSPACE-022 Approved Annotations / Evidence / Provenance Page Spec Report

Date/time: Wednesday Jun 10, 2026, 10:35 AM UTC-7

## Files inspected

- `AGENTS.md`
- `CLAUDE.md`
- `.claude/skills/workspace-doc-task/SKILL.md`
- `.claude/skills/no-prose-boundary/SKILL.md`
- `ai_context/repomix-current-task-context.xml` attempted; unavailable due permission denial
- `docs/graphify-out/GRAPH_REPORT.md`
- `backend/graphify-out/GRAPH_REPORT.md`
- `frontend/src/graphify-out/GRAPH_REPORT.md`
- `tests/graphify-out/GRAPH_REPORT.md`
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
- `docs/roadmap/approved_objects_items_page_spec.md`
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

## Files modified

- `docs/roadmap/approved_annotations_evidence_provenance_page_spec.md`
- `training/reports/workspace_022_approved_annotations_evidence_provenance_page_spec.md`
- `docs/master_plan.md`
- `docs/plan.md`
- `docs/roadmap/project_workspace_foundation_spec.md`
- `docs/roadmap/project_overview_page_spec.md`
- `docs/roadmap/project_memory_canon_page_structure_spec.md`
- `docs/roadmap/omi_ideas_candidates_page_spec.md`
- `docs/roadmap/project_memory_canon_storage_model.md`
- `docs/roadmap/writer_assistant_core_candidate_schemas.md`
- `docs/roadmap/omi_story_knowledge_candidate_expansion.md`
- `docs/roadmap/project_file_model.md`
- `docs/roadmap/task_backlog.md`
- `docs/roadmap/phase_map.md`
- `docs/roadmap/decision_log.md`

## Spec created/updated

Created `docs/roadmap/approved_annotations_evidence_provenance_page_spec.md` as the WORKSPACE-022 documentation-only planning handoff.

## Page purpose

The future page shows only owner-approved annotation, evidence span, provenance, or equivalent approved audit records for the selected project. It separates approved project truth and audit context from OMI candidates, generated/extracted candidates, and promotion records that have not been applied by future owner-controlled apply-promotion.

The page is not a generated summary page, writing-assistance page, evidence explanation generator, or Dramatica structural proof page.

## Approved annotation/evidence/provenance display model

The spec defines display fields for record identity, type, status, scope, owner-approved description, source document references, source locators, stored hashes, safe excerpts, span/line/paragraph/anchor metadata, linked candidate/promotion/memory/story-knowledge IDs, confidence/certainty labels, owner notes, timestamps, approval metadata, revision/supersession metadata, tags, and notes.

The display rules prohibit unapproved candidates as truth, generated summaries, generated explanations, generated interpretations, rewritten excerpts, and invented evidence. Missing or unresolved fields must be labeled honestly.

## Page sections

The spec defines Page Header, Boundary Banner, Approved Record List, Record Detail Panel, Source Locator Panel, Evidence Span Panel, Provenance Chain Panel, Linked Approved Memory Snapshot, Linked Candidate / Promotion Audit Snapshot, Related Story Knowledge Snapshot, Copyright / Source Safety Notice, Candidate Backlog Snapshot, Empty State, Warning State, and Future Page Link Reference.

Each section documents purpose, data source, candidate/canon boundary, no-prose boundary, empty state, and error state.

## Candidate/canon separation

Approved records come only from future approved memory/audit stores such as `memory/annotations.json`, `memory/evidence_spans.json`, `memory/provenance.json`, or an equivalent approved store after future apply-promotion.

OMI annotation/evidence/provenance candidates remain in OMI. Pending, rejected, archived, duplicate, uncertain, and needs-revision candidates are not approved truth. Promotion records are audit-only until future apply-promotion creates or updates approved memory.

Evidence/provenance records may support approved memory but do not automatically promote, validate, or create canon, and they are not Dramatica proof unless a future Dramatica-specific approved memory record explicitly says so.

## Page operations

First-version operations are view-only: record list, record details, local approved-only filtering/searching, source locator display, evidence span metadata, provenance chain snapshot, linked approved memory, linked OMI candidate or promotion audit context, related story-knowledge links, and copyright/source safety notice.

Future-only operations include editing, merging/splitting, archiving/restoring, apply-promotion, extraction, generated annotations, generated summaries, generated interpretations, generated excerpts, semantic search, automatic re-anchoring, evidence graph visualization, contradiction detection, Dramatica proof classification, and JSONL/training conversion.

## Local search/filter planning

Search/filter is planned as local deterministic filtering over approved fields such as record IDs, record types, titles, type labels, status, scope, source document IDs, locator types, linked candidate/promotion/memory/story-knowledge IDs, tags, and approved descriptions when available.

Search must not call models/Ollama, perform semantic search, generate summaries/explanations, extract evidence, re-anchor source text, detect contradictions, or classify Dramatica roles.

## Warning/invalid-state behavior

The spec covers missing/corrupt memory files, unsupported schema, broken source/candidate/promotion/memory/story-knowledge references, broken locators, hash mismatches, unsafe IDs, duplicate IDs, unsupported locator types, out-of-range spans, unsafe excerpts, missing evidence, broken/cyclic provenance chains, promotion-record-only states, OMI candidate-only states, unimplemented related pages, and corrupt memory indexes.

Warnings are non-destructive and must not auto-repair, auto-delete, rewrite identity, retitle, infer locators, re-anchor source text, invent evidence, generate summaries, promote candidates, mutate memory/canon, or leak host filesystem paths.

## API planning

The spec documents future route groups without implementation:

- `GET /api/projects/{project_id}/memory/evidence`
- `GET /api/projects/{project_id}/memory/evidence/{record_id}`
- `GET /api/projects/{project_id}/memory/evidence/{record_id}/provenance`
- `GET /api/projects/{project_id}/memory/evidence/health`

Each route group includes purpose, request shape, response shape, validation, path safety, candidate/canon boundary, no-prose boundary, copyright/source safety, and expected errors. It leaves open whether annotations, evidence spans, and provenance share one endpoint family or split into parallel endpoint families.

## Frontend planning

The spec documents future components without implementation: `ApprovedAnnotationsEvidenceProvenancePage`, `AnnotationsEvidenceBoundaryBanner`, `ApprovedEvidenceRecordList`, `ApprovedEvidenceRecordListItem`, `EvidenceRecordDetailPanel`, `SourceLocatorPanel`, `EvidenceSpanPanel`, `ProvenanceChainPanel`, `LinkedApprovedMemorySnapshot`, `LinkedCandidatePromotionAuditSnapshot`, `RelatedStoryKnowledgeSnapshot`, `CopyrightSourceSafetyNotice`, `EvidenceCandidateBacklogSnapshot`, `EvidenceSearchFilterControls`, `EvidenceWarningsPanel`, `EvidenceEmptyState`, and `EvidenceFuturePagesReference`.

The plan explicitly blocks AI writing buttons, generated annotation/summary/interpretation controls, first-version semantic-search controls, evidence generation, evidence explanation, source summary, source rewrite, annotation creation, proof inference, Dramatica role classification, training conversion, and candidate promotion controls.

## Future tests identified

Future tests cover no memory/no records, approved record loading, candidate/promotion separation, corrupt file warnings, duplicate and unsafe IDs, broken links and locators, unsupported locator types, hash mismatches, copyright-unsafe excerpts, broken/cyclic provenance chains, no model calls during search, no OMI creation, no memory/canon mutation, no candidate promotion, no JSONL/training writes, no AI prose-generation controls, no generated annotations/summaries/explanations/interpretations, no invented evidence, no re-anchoring, and no Dramatica proof claims.

## Remaining deferred decisions

- Exact approved memory file schema and whether annotations, evidence spans, and provenance are stored in separate files or a combined audit store.
- Whether future APIs use one evidence/audit endpoint family or split annotation/evidence/provenance endpoint families.
- Exact source locator encoding, hash policy, and excerpt safety policy.
- Future apply-promotion behavior that creates or updates approved memory/canon records.
- Future visualization or graph features after first-version view-only behavior is accepted.
- Future Dramatica-specific evidence/proof handling, if ever approved and evidence-backed.

## Safety confirmations

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
- No memory/canon runtime files created.
- No staging occurred.
- No commits occurred.
