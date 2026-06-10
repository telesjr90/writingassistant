# WORKSPACE-023 Approved Contradictions Page Spec Report

Date/time: 2026-06-10T11:43:40-07:00

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
- `docs/roadmap/project_memory_canon_page_structure_spec.md`
- `docs/roadmap/omi_ideas_candidates_page_spec.md`
- `docs/roadmap/continuity_consistency_page_spec.md`
- `docs/roadmap/approved_open_questions_page_spec.md`
- `docs/roadmap/approved_relationships_page_spec.md`
- `docs/roadmap/approved_organizations_groups_page_spec.md`
- `docs/roadmap/approved_objects_items_page_spec.md`
- `docs/roadmap/approved_annotations_evidence_provenance_page_spec.md`
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

Optional context: `ai_context/repomix-current-task-context.xml` and Graphify report files were present but not readable through the file-read tool, so the task proceeded with targeted source-of-truth docs and successful direct WSL Graphify query output.

## Files Modified

- Created `docs/roadmap/approved_contradictions_page_spec.md`.
- Created `training/reports/workspace_023_approved_contradictions_page_spec.md`.
- Updated `docs/master_plan.md`.
- Updated `docs/plan.md`.
- Updated `docs/roadmap/project_workspace_foundation_spec.md`.
- Updated `docs/roadmap/project_overview_page_spec.md`.
- Updated `docs/roadmap/project_memory_canon_page_structure_spec.md`.
- Updated `docs/roadmap/project_memory_canon_storage_model.md`.
- Updated `docs/roadmap/writer_assistant_core_candidate_schemas.md`.
- Updated `docs/roadmap/omi_story_knowledge_candidate_expansion.md`.
- Updated `docs/roadmap/project_file_model.md`.
- Updated `docs/roadmap/task_backlog.md`.
- Updated `docs/roadmap/phase_map.md`.
- Updated `docs/roadmap/open_questions.md`.
- Updated `docs/roadmap/risk_register.md`.
- Updated `docs/roadmap/decision_log.md`.
- Updated `docs/roadmap/mvp_completion_test_matrix.md`.

## Spec Created

`docs/roadmap/approved_contradictions_page_spec.md` was created as the WORKSPACE-023 documentation-only planning handoff.

The spec defines the future Approved Contradictions page as an approved-only project memory/canon page for owner-approved `contradiction_memory_record` records or equivalent approved cross-record conflict records. It explicitly excludes automatic contradiction detection, generated explanations, generated fixes, scene rewrites, semantic search, source re-anchoring, graph visualization, apply-promotion, and Dramatica proof.

## Page Purpose

The page is intended to show approved contradiction records for the selected project only, keep OMI contradiction candidates and promotion records separate from approved truth, distinguish contradictions from broader continuity/consistency warnings, link records to sources/evidence/provenance/approved memory where available, and display unresolved or broken state honestly.

## Approved Contradiction Display Model

The spec defines fields for contradiction identity, type, status, severity, resolution, scope, owner-approved description, claim A/B summaries, claim A/B source references and locators, claim-side linked memory records, affected chapters/scenes, linked notes/materials, linked story-knowledge records, linked continuity/open-question/annotation/evidence/provenance records, related contradictions, first/latest source, evidence/provenance summary, certainty label, owner resolution note, resolution decision, approval metadata, source candidate IDs, promotion record IDs, revision history, supersession, tags, and notes.

Rules require stored approved fields only. Generated contradiction analysis, summaries, explanations, fixes, rewrite suggestions, scene suggestions, repair suggestions, invented evidence, and Dramatica proof claims are prohibited.

## Page Sections

The spec defines Page Header, Contradictions Boundary Banner, Approved Contradiction List, Contradiction Detail Panel, Contradiction Claims / Pair Panel, Evidence / Provenance Panel, Linked Sources Panel, Linked Approved Memory Snapshot, Related Continuity / Consistency Snapshot, Related Open Questions Snapshot, Related Story Knowledge Snapshot, Resolution Status Placeholder, Candidate Backlog Snapshot, Empty State, Warning State, and Future Page Link Reference.

Each section documents purpose, data source, candidate/canon boundary, no-prose boundary, empty state, and error state.

## Candidate / Canon Separation

Approved records are read only from future approved memory such as `memory/contradictions.json` or equivalent approved memory/audit storage. OMI contradiction candidates remain in OMI candidates. Pending, rejected, archived, needs-revision, duplicate, uncertain, and approved-but-not-applied candidates do not appear as approved contradictions. Promotion records are audit-only unless future apply-promotion creates or updates approved contradiction memory. Candidate backlog may show counts and links only. Contradiction type, severity, status, resolution, claim pair state, evidence state, related links, and certainty are not inferred from candidates.

## Page Operations

Allowed first-version operations include viewing approved contradiction records, viewing details, local filtering/search, opening linked source references, opening linked approved memory/canon records, opening linked OMI candidate or promotion records, and showing claims/pair, evidence/provenance, linked story-knowledge, and resolution-placeholder panels.

Future-only operations include editing approved contradiction memory, merge/split, archive/restore, marking resolved, apply-promotion, contradiction detection, contradiction extraction, generated explanations/fixes, scene rewrites, semantic search, automatic source re-anchoring, graph visualization, Dramatica proof classification, and JSONL/training conversion.

## Local Search / Filter Planning

Local search/filter is approved-only and deterministic over approved contradiction IDs, titles, types, statuses, severity, resolution, scope, claim summaries, claim source IDs, affected chapter/scene IDs, linked story-knowledge IDs, source candidate IDs, promotion record IDs, tags, and stored approved description.

The spec prohibits semantic search, model/Ollama calls, generated summaries, generated explanations, generated fixes, detection, extraction, source re-anchoring, Dramatica classification, project mutation, OMI record creation, memory/canon writes, JSONL writes, and training-data writes during search.

## Warning / Invalid-State Behavior

Warnings cover missing/corrupt memory, unsupported schema, missing source candidate/promotion/approved-memory references, broken claim A/B source references, missing/unsupported/out-of-range/same claim locators, broken source and story-knowledge references, unsafe IDs, duplicate contradiction IDs, type/status/severity/resolution conflicts, broken/cyclic related contradiction links, source hash mismatch, unsafe excerpts, missing evidence, promotion records without approved memory, OMI candidates with no approved records, unimplemented related pages, and corrupt `memory/index.json`.

Warnings are non-destructive and do not auto-repair, auto-delete, retitle, infer claims, re-anchor source text, invent evidence, generate summaries/explanations/fixes, promote candidates, mutate memory/canon, or leak host filesystem paths.

## API Planning

The spec documents future route groups only:

- `GET /api/projects/{project_id}/memory/contradictions`
- `GET /api/projects/{project_id}/memory/contradictions/{contradiction_id}`
- `GET /api/projects/{project_id}/memory/contradictions/{contradiction_id}/provenance`
- `GET /api/projects/{project_id}/memory/contradictions/health`

Each route group documents purpose, request shape, response shape, validation, path safety, candidate/canon boundary, no-prose boundary, source/evidence safety, and expected errors.

## Frontend Planning

The spec documents future components for `ApprovedContradictionsPage`, boundary banner, approved list/list items, detail panel, claims pair panel, evidence panel, source links panel, linked approved memory snapshot, related continuity/open-question/story-knowledge snapshots, resolution placeholder, candidate backlog snapshot, search/filter controls, warnings panel, empty state, and future pages reference.

The frontend plan prohibits AI writing buttons, generated explanation/fix buttons, rewrite buttons, semantic-search buttons in the first version, detection controls, repair controls, Dramatica classification controls, training conversion controls, and promote-candidate controls.

## Future Tests Identified

Future tests should cover empty/missing memory, approved contradiction load, candidate exclusion, promotion-record-only exclusion, corrupt memory warnings, duplicate/unsafe IDs, broken claim source links, unsupported/out-of-range locators, same-locator warnings, broken candidate/promotion/memory/story-knowledge links, broken/cyclic related contradiction links, severity/status/resolution conflicts, source hash mismatch, copyright-unsafe excerpts, local search with no model calls, no OMI/memory/canon mutation, no promotion, no JSONL/training writes, no AI prose controls, no generated explanations/fixes/rewrites/summaries, no invented evidence, no detection, no source re-anchoring, and no Dramatica proof claims.

## Remaining Deferred Decisions

Deferred decisions include exact runtime schema, enum values, memory envelope version, endpoint composition, category file versus continuity subcategory versus approved audit store, claim locator format, OMI filter strategy, source hash strategy, source safety policy, apply-promotion behavior, owner-controlled resolution workflow, visualization/search placement, future Dramatica taxonomy, and browser/manual acceptance checklist.

## Safety Confirmations

- No backend runtime code changed.
- No frontend runtime code changed.
- No tests changed.
- No package/dependency files changed.
- No dataset files changed.
- No JSONL/training records created.
- No `training/data/dataset_manifest.json` updates.
- No training/fine-tuning run.
- No Ollama/live model calls.
- No packages installed.
- No Dramatica-specific logic implemented.
- No runtime project files created.
- No OMI records created.
- No memory/canon runtime files created.
- No staging occurred.
- No commits occurred.
