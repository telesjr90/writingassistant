# WORKSPACE-026 Project Workspace Implementation Decision Sweep Report

Date/time: 2026-06-10, generated during the WORKSPACE-026 documentation task.

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
- `docs/roadmap/project_creation_flow_spec.md`
- `docs/roadmap/project_selector_library_spec.md`
- `docs/roadmap/omi_guided_project_creation_spec.md`
- `docs/roadmap/chapter_scene_data_model_spec.md`
- `docs/roadmap/notes_materials_data_model_spec.md`
- `docs/roadmap/user_authored_document_editor_workflow_spec.md`
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
- `docs/roadmap/approved_annotations_evidence_provenance_page_spec.md`
- `docs/roadmap/approved_contradictions_page_spec.md`
- `docs/roadmap/approved_scene_event_causality_review_spec.md`
- `docs/roadmap/project_memory_canon_cross_linking_health_spec.md`
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

Graphify was available from WSL and returned scoped context for workspace defaults, remaining decisions, first runtime slice, MVP exit acceptance, candidate/canon boundaries, and no-prose rules.

The Repomix task context file and Graphify report files were attempted through the available file-read path but were not accessible in this environment; the task continued with targeted reads of the source-of-truth docs and WSL Graphify queries.

## Files Modified

- `docs/roadmap/project_workspace_implementation_decision_sweep.md`
- `docs/roadmap/task_backlog.md`
- `docs/roadmap/phase_map.md`
- `docs/roadmap/open_questions.md`
- `docs/roadmap/risk_register.md`
- `docs/roadmap/decision_log.md`
- `docs/roadmap/mvp_completion_test_matrix.md`
- `docs/master_plan.md`
- `docs/plan.md`
- `docs/roadmap/project_workspace_foundation_spec.md`
- `training/reports/workspace_026_project_workspace_implementation_decision_sweep.md`

## Decision Sweep Created

Created `docs/roadmap/project_workspace_implementation_decision_sweep.md` as the WORKSPACE-026 implementation-readiness consolidation for Phase 7 Project Workspace Foundation.

## WORKSPACE-001 Through WORKSPACE-025 Readiness Summary

WORKSPACE-001 through WORKSPACE-012 are ready enough to drive the first runtime implementation sequence, with WORKSPACE-002 as the first implementation source for backend project creation and safe metadata.

WORKSPACE-013 through WORKSPACE-025 are ready as approved-memory/canon shell, empty-state, label, and future health planning. They remain deferred for real records until memory storage and apply-promotion exist.

No new feature spec is required before starting `PHASE7-IMPL-001`.

## Implementation Defaults Consolidated

- Project creation defaults to owner-editable title, title-derived owner-editable safe `project_id`, server-side validation, collision fail-closed behavior, metadata-only `project.json`, blank project path, and staged/later OMI-guided setup.
- Project Library defaults to scan-first local discovery, valid/invalid project states, local search/filter/sort, no delete in the first version, and future-only archive/delete.
- Chapter/scene storage preserves current `scenes/{scene_id}.md` compatibility and adds chapter/scene metadata only through planned implementation.
- Notes/materials default to Markdown/text bodies plus separate metadata, provenance/license warnings, and no extraction during first save/search.
- Shared editor defaults to one owner-authored document editor pattern with dirty state, save/reload, unsaved switch protections, no AI prose controls, and no overblocking of owner-authored saves.
- Project Overview defaults to safe read-only landing behavior with metadata, recent-document metadata, OMI status, memory/canon empty state or snapshot, and health warnings.
- OMI keeps existing MVP behavior; typed candidates and apply-promotion remain future-only.
- Approved memory/canon starts as shell/empty-state/category cards; real memory files, `memory/index.json`, cross-link health, and apply-promotion remain planned.

## Remaining Owner Decisions

Immediate blockers:

- Accept/document current public-domain `projects/example` fixture state or request replacement.
- Accept previous localhost smoke-test sandbox limitation or rerun in socket-enabled local environment.
- Confirm `PHASE7-IMPL-001` as the first runtime implementation task.
- Decide whether to push local `main` before implementation begins.

Deferrable:

- Node engine metadata timing.
- Invalid project folder warning section versus recovery tab.
- Lazy versus eager `bible.json`/`storyform.json`.
- Lazy versus eager OMI folder creation.
- Candidate extraction trigger policy.
- First approved-memory implementation depth.
- `memory/index.json` read-only stub timing.
- Project Library cards/table/both.
- Archive/delete timing.
- Durable pre-project OMI inbox versus staged wizard state.

Already defaulted:

- Stable `project_id`.
- Scan-first library.
- No delete first.
- Scene Markdown compatibility.
- Notes/materials Markdown/text plus metadata.
- Owner-authored saves allowed.
- Candidates are not canon.
- Promotion records are audit-only.
- Approved memory/canon pages read applied memory only.
- Dramatica, extraction, semantic search, graph visualization, fine-tuning, JSONL, and model calls remain deferred.

## Recommended Implementation Sequence

1. `PHASE7-IMPL-001 - Project Creation and Safe Project Metadata Backend`
2. `PHASE7-IMPL-002 - Project Library / Selector Backend and Frontend`
3. `PHASE7-IMPL-003 - Remove Hardcoded Frontend PROJECT_ID and Support Project Switching`
4. `PHASE7-IMPL-004 - Chapter / Scene Metadata Compatibility Layer`
5. `PHASE7-IMPL-005 - Notes / Materials Storage and Routes`
6. `PHASE7-IMPL-006 - Shared Scene / Note / Material Editor UI`
7. `PHASE7-IMPL-007 - Project Overview Page Shell`
8. `PHASE7-IMPL-008 - OMI-Guided Project Creation Staged Flow`
9. `PHASE7-IMPL-009 - Project Memory / Canon Shell and Approved-Only Empty States`
10. `PHASE7-IMPL-010 - Implementation Readiness Test Matrix / Manual Browser Checklist`

## Recommended Immediate Next Runtime Task

Recommended next task: `PHASE7-IMPL-001 - Project Creation and Safe Project Metadata Backend`.

This should come before UI pages because the rest of Phase 7 needs safe project identity, collision handling, metadata storage, and create/open behavior before project switching and page routing can be reliable.

## Phase 7 Acceptance Checklist

The sweep defines checks for blank project creation, `project_id` validation/collisions, scan/select/switch, scene save/reload, chapter/scene organization where included, notes/materials save/reload, material references, shared editor dirty state, Overview shell, OMI status, memory/canon shell, candidate/canon labels, no AI prose controls, no model calls during storage/search/navigation, backend tests, frontend build, and manual browser checklist.

## Roadmap Updates

Roadmap docs were updated minimally to register WORKSPACE-026 as the completed planning handoff, point Phase 7 toward the PHASE7-IMPL sequence, distinguish immediate blockers from deferred decisions, record the decision-log handoff, add implementation-handoff risks, and add the new Phase 7 acceptance matrix reference.

## Remaining Deferred Decisions

Archive/delete, project recovery/import, `projects/index.json`, durable pre-project OMI inbox, candidate extraction triggers, typed OMI story-knowledge candidates, memory storage files, `memory/index.json`, apply-promotion, real approved category records, cross-link repair, semantic search, graph visualization, contradiction detection, external extractor installs, Dramatica-specific logic, fine-tuning, JSONL, dataset, RunPod, and live model tracks remain deferred.

## Safety Confirmations

- No backend runtime code changed.
- No frontend runtime code changed.
- No tests changed.
- No package/dependency files changed.
- No dataset files changed.
- No JSONL/training records created.
- `training/data/dataset_manifest.json` was not updated.
- No training/fine-tuning was run.
- No Ollama/live model call was made.
- No packages were installed.
- No Dramatica-specific logic was implemented.
- No runtime project files were created.
- No OMI records were created.
- No memory/canon files were created.
- No staging occurred.
- No commits occurred.
