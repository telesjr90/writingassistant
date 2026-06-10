# WORKSPACE-025 Project Memory / Canon Cross-Linking and Health Spec Report

Date/time: 2026-06-10 12:12:49 PDT

## Result

PASS: documentation-only planning package created in the WSL repo path.

## Context and Tooling

- Verified WSL repo root with `pwd` and `git rev-parse --show-toplevel`.
- Required preflight Git commands ran directly in the WSL shell.
- Graphify was available from WSL and the suggested roadmap queries were run from `docs/`.
- `ai_context/repomix-current-task-context.xml` existed but was not readable from this session; proceeded with Graphify output and targeted roadmap source reads.

## Files Inspected

- `AGENTS.md`
- `.claude/skills/workspace-doc-task/SKILL.md`
- `docs/master_plan.md`
- `docs/plan.md`
- `docs/roadmap/project_workspace_foundation_spec.md`
- `docs/roadmap/project_overview_page_spec.md`
- `docs/roadmap/project_memory_canon_page_structure_spec.md`
- `docs/roadmap/omi_ideas_candidates_page_spec.md`
- `docs/roadmap/approved_scene_event_causality_review_spec.md`
- `docs/roadmap/project_memory_canon_storage_model.md`
- `docs/roadmap/writer_assistant_core_candidate_schemas.md`
- `docs/roadmap/omi_story_knowledge_candidate_expansion.md`
- `docs/roadmap/project_file_model.md`
- `docs/roadmap/task_backlog.md`
- `docs/roadmap/phase_map.md`
- `docs/roadmap/decision_log.md`
- `docs/roadmap/open_questions.md`
- `docs/roadmap/risk_register.md`
- `docs/roadmap/mvp_completion_test_matrix.md`

## Files Modified

- `docs/roadmap/project_memory_canon_cross_linking_health_spec.md`
- `training/reports/workspace_025_project_memory_canon_cross_linking_health_spec.md`
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
- `docs/roadmap/open_questions.md`
- `docs/roadmap/risk_register.md`

## Spec Created

Created `docs/roadmap/project_memory_canon_cross_linking_health_spec.md`.

## Cross-Linking Purpose

The spec defines future project-level cross-linking, navigation, index-health, and reference-health planning for approved memory/canon. It consolidates the approved-memory category page series into shared rules for record identity, link identity, category registry behavior, counts, health warnings, local filtering, API planning, and frontend planning.

## Covered Categories

The spec covers characters, locations/settings, timeline events, plot threads, continuity/consistency issues, open questions, relationships, organizations/groups, objects/items, annotations/evidence/provenance, contradictions, and scene reviews/events/actions/causality notes.

Future extensibility is reserved for aliases/nicknames, chapter/scene navigation summaries, owner review notes, and Dramatica-specific records as a later separate approved-memory family.

## Memory/Index Planning

The spec documents future folder-based planning for `memory/index.json` plus approved category files. It clarifies that exact runtime schema is deferred, category files may be combined or split later, `memory/index.json` should be derived/rebuildable or health-checkable, approved category files remain authoritative unless a later implementation changes that, and pending candidates must never appear as approved truth.

## Shared Record/Link Model

The spec defines planning fields for approved records, including `record_id`, `record_type`, `category`, `display_title`, `status`, `approval_state`, linked record/candidate/promotion/source/evidence/provenance IDs, supersession fields, audit timestamps, schema/version fields, tags, and notes.

It also defines planning fields for link metadata, including `link_id`, source/target IDs and types, `link_type`, `link_direction`, `link_status`, supporting evidence/provenance IDs, source candidate IDs, promotion record IDs, and notes.

## Navigation/Count Planning

The spec defines category cards, approved record counts, pending candidate counts as OMI links only, promotion audit counts, health warning counts, broken-link counts, missing-source counts, last-updated timestamps, empty states, unavailable states, not implemented states, and links to category, OMI, evidence, and provenance pages.

Required labels include `Approved records`, `Pending candidates`, `Promotion audit records`, `Health warnings`, `Broken links`, `Missing sources`, and `Not implemented yet`.

## Candidate/Canon Separation

The spec states that approved memory records may link to OMI candidates and promotion records only as audit/provenance context. OMI candidates do not become approved truth through linking, promotion records do not become approved truth without future apply-promotion, cross-links do not promote or validate truth claims, and future extractor/model-created links must enter OMI first.

## Health and Warning Behavior

The spec defines non-destructive warning behavior for missing/corrupt memory/index/category files, unsupported schemas, duplicate/unsafe IDs, broken cross-record/source/evidence/provenance/OMI/promotion links, cycles, source hash mismatches, locator issues, index mismatches, registry mismatches, missing approval metadata, missing evidence/provenance, candidate/promotion records shown as approved truth, host path leakage, and copyright-unsafe excerpts.

Warnings must not auto-repair, auto-delete, auto-merge, auto-promote, rewrite IDs, rewrite locators, infer missing links, generate summaries/explanations/fixes, mutate memory/canon, mutate OMI, or write training data.

## Operations

Allowed first-version operations are view-only and navigation-only: view health summary, counts, cross-link warnings, broken-reference warnings, index mismatch warnings, linked category/source/evidence/provenance/OMI/promotion records, local warning filters, and boundary labels.

Future-only operations include repair/rebuild index, apply-promotion, edit/merge/split/archive/restore/deduplicate approved memory, auto-linking, extraction, generated summaries/explanations, semantic search, graph/timeline visualization, contradiction detection, source re-anchoring, training/JSONL conversion, and Dramatica classification.

## Local Search/Filter Planning

The spec plans deterministic local filtering over record IDs, record types, categories, display titles, status, approval state, link IDs, health warning type, severity, source file, tags, and timestamps. It explicitly excludes semantic search, model/Ollama calls, generated summaries, generated explanations, extraction, repair, re-indexing, contradiction detection, and Dramatica classification.

## API Planning

The spec documents future planning for:

- `GET /api/projects/{project_id}/memory`
- `GET /api/projects/{project_id}/memory/index`
- `GET /api/projects/{project_id}/memory/health`
- `GET /api/projects/{project_id}/memory/links`
- `GET /api/projects/{project_id}/memory/categories`
- `GET /api/projects/{project_id}/memory/categories/{category}`
- `GET /api/projects/{project_id}/memory/records/{record_id}`

All routes are future-only and must define purpose, request shape, response shape, validation, path safety, candidate/canon boundary, no-prose boundary, source/evidence safety, index health behavior, and expected errors.

## Frontend Planning

The spec documents future components for the memory/canon health page, boundary banner, category cards, health summary, index status, cross-link warnings, broken references, category registry, record lookup, candidate/promotion audit links, evidence/provenance links, source document links, search/filter controls, warning list, empty state, not implemented state, and future actions reference.

It prohibits first-version buttons or controls for AI writing, generated summaries, generated explanations, repair, apply-promotion, rebuild-index, semantic search, graph visualization, fix memory, repair canon, summarize project, explain canon, infer links, generate links, resolve contradiction, rewrite scene, classify Dramatica role, convert to training data, or promote candidate.

## Future Tests Identified

Future tests cover missing memory/index, valid category registry, approved counts, empty state, candidates/promotions not counted as approved truth, corrupt files, unsupported schemas, duplicate/unsafe IDs, broken record/source/evidence/provenance/OMI/promotion links, cycles, source hash and locator warnings, index/registry mismatches, approval/evidence/provenance gaps, host path leakage, copyright-unsafe excerpts, local filter no-model behavior, no OMI creation, no memory/canon mutation, no promotion, no index rebuild, no training writes, no prose-generation controls, no generated summaries/explanations/fixes, no invented links/evidence, no Dramatica proof claims, and unchanged `training/data/dataset_manifest.json`.

## Remaining Deferred Decisions

- Exact runtime schema for shared record/link envelopes.
- Globally unique IDs versus category-scoped IDs.
- Explicit link records versus category fields versus derived index entries.
- Category registry file shape and migration behavior.
- Required/optional/lazy/rebuildable `memory/index.json` behavior.
- Health warning severity model.
- Source document registry and locator format.
- Category-specific evidence/provenance requirements.
- Host path redaction policy.
- Copyright-safe excerpt policy.
- Future apply-promotion, repair, rebuild, edit, merge/split, archive/restore, and deduplication workflows.
- Whether Dramatica-specific approved-memory records become a separate future family.
- Browser/manual acceptance checklist for implemented memory/canon health page.

## Safety Confirmations

- No backend runtime code changed.
- No frontend runtime code changed.
- No tests changed.
- No package/dependency files changed.
- No dataset files changed.
- No JSONL/training records created.
- `training/data/dataset_manifest.json` was not updated.
- No training/fine-tuning run.
- No Ollama/live model call.
- No packages installed.
- No Dramatica-specific logic implemented.
- No runtime project files created.
- No OMI records created.
- No memory/canon runtime files created.
- No staging performed.
- No commits performed.
