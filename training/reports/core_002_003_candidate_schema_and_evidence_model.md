# CORE-002 / CORE-003 Candidate Schema and Evidence Model

Date/time: 2026-06-07 America/Los_Angeles

## Scope

This documentation-only report records the Writer Assistant Core candidate schema and evidence/provenance planning pass.

No runtime schema, backend code, frontend code, extractor code, project memory/canon file, JSONL record, training data, model artifact, or promotion behavior was implemented.

## Files Inspected

- `docs/master_plan.md`
- `docs/plan.md`
- `docs/roadmap/task_backlog.md`
- `docs/roadmap/phase_map.md`
- `docs/roadmap/decision_log.md`
- `docs/roadmap/open_questions.md`
- `docs/roadmap/risk_register.md`
- `docs/roadmap/tooling_decisions.md`
- `docs/roadmap/optional_analysis_extractors.md`
- `docs/roadmap/omi_mvp_schema_lifecycle.md`
- `docs/roadmap/omi_storage_model.md`
- `docs/roadmap/project_file_model.md`
- `docs/roadmap/ncp_compatibility_subset.md`

## Files Modified

- `docs/roadmap/writer_assistant_core_candidate_schemas.md`
- `docs/roadmap/omi_mvp_schema_lifecycle.md`
- `docs/roadmap/omi_storage_model.md`
- `docs/roadmap/project_file_model.md`
- `docs/roadmap/task_backlog.md`
- `docs/roadmap/phase_map.md`
- `docs/roadmap/open_questions.md`
- `docs/roadmap/risk_register.md`
- `docs/roadmap/decision_log.md`
- `training/reports/core_002_003_candidate_schema_and_evidence_model.md`

## Schemas Added

Created `docs/roadmap/writer_assistant_core_candidate_schemas.md` with candidate schemas for:

- `character_candidate`
- `location_candidate`
- `object_candidate`
- `organization_candidate`
- `timeline_event_candidate`
- `relationship_candidate`
- `plot_thread_candidate`
- `continuity_warning_candidate`
- `annotation_candidate`
- `open_question_candidate`

Each candidate type uses the shared base candidate contract and stores type-specific fields under `candidate_content`.

## Evidence Model Summary

The reusable evidence model includes:

- `evidence_id`
- `source_type`
- `source_path`
- `source_scene_id`
- `source_scene_title`
- `source_text_excerpt`
- `start_offset`
- `end_offset`
- `paragraph_index`
- `line_start`
- `line_end`
- `quote_exact`
- `summary`
- `supports_claim`
- `confidence`
- `notes`

Exact offsets and line numbers are preferred but optional at first if the app cannot reliably provide them.

## Provenance Model Summary

The reusable provenance model includes:

- `created_by`
- `source_type`
- `tool`
- `model`
- `extractor`
- `prompt_id`
- `timestamp`
- `source_hash`
- `snapshot_hash`
- `human_review_required`
- `owner_reviewed`
- `license_status`
- `notes`

Provenance is required for candidate trust and future promotion. Tool/model/extractor fields may be null for manual owner-created candidates.

## Owner Decision Model Summary

The owner decision model includes:

- `decision`
- `decided_by`
- `decided_at`
- `notes`
- `revision_request`
- `approval_confirmed`

Allowed decisions:

- `undecided`
- `approve`
- `reject`
- `needs_revision`
- `archive`
- `promote`

## Promotion Status Model Summary

The promotion status model includes:

- `eligible`
- `blocked_reasons`
- `destination`
- `promotion_record_id`
- `promoted_at`
- `requires_confirmation`
- `confirmation_received`

Candidate creation is not promotion. Promotion requires owner approval, destination, evidence/provenance, and final confirmation.

## OMI Updates Made

- `docs/roadmap/omi_mvp_schema_lifecycle.md` now references the CORE-002/CORE-003 schema spec and clarifies that Writer Assistant Core candidate types are future OMI-supported classes.
- `docs/roadmap/omi_storage_model.md` now references the schema spec as the typed candidate/content contract while preserving OMI as the storage/review/promotion record model.
- Both docs clarify that these typed candidates are not runtime extractor implementations, project memory/canon files, or durable truth mutations.

## Unresolved Decisions Moved to CORE-004 or Later

- Final project memory/canon file layout.
- Whether approved candidates feed separate `memory/*.json` files, one `project_memory.json`, existing `bible.json`, or another structure.
- Runtime candidate ID format.
- Source hash and snapshot hash implementation.
- Runtime locator choice for evidence spans.
- Annotation storage location and UI treatment.
- First extractor strategy and dependency spike.
- Candidate merge/deduplication behavior.
- Apply-promotion behavior and rollback model.

## Safety Confirmations

- No runtime code changed.
- No packages installed.
- No extractor dependencies added.
- No JSONL records created.
- `training/data/dataset_manifest.json` was not changed.
- No training ran.
- No Ollama/live model call was made.
- No Books 4-5 work was done.
- No candidates were promoted into bible, storyform, scenes, project metadata, owner memory, project memory, or canon.
- No files were staged or committed.

## Commands Run

- `pwd`
- `git status --short --branch`
- `git log -1 --oneline`
- `ls docs/roadmap`
- `test -f docs/roadmap/writer_assistant_core_candidate_schemas.md && echo exists || echo missing`
- Targeted `grep` / `sed` inspections for OMI, project file model, phase map, backlog, open questions, and risk register.
- Final validation commands are recorded in the task response after execution.
