# CORE-004 Project Memory / Canon Storage Model

Date/time: 2026-06-07 America/Los_Angeles

## Scope

This documentation-only report records the Project Memory / Canon Storage Model planning pass for Writer Assistant Core.

No runtime code, frontend code, extractor code, project memory files, OMI candidates, OMI promotions, JSONL records, training data, model calls, or apply-promotion behavior were created.

## Files Inspected

- `docs/master_plan.md`
- `docs/plan.md`
- `docs/roadmap/writer_assistant_core_candidate_schemas.md`
- `docs/roadmap/project_file_model.md`
- `docs/roadmap/omi_mvp_schema_lifecycle.md`
- `docs/roadmap/omi_storage_model.md`
- `docs/roadmap/task_backlog.md`
- `docs/roadmap/phase_map.md`
- `docs/roadmap/decision_log.md`
- `docs/roadmap/open_questions.md`
- `docs/roadmap/risk_register.md`
- `docs/roadmap/tooling_decisions.md`
- `docs/roadmap/optional_analysis_extractors.md`

## Files Modified

- `docs/roadmap/project_memory_canon_storage_model.md`
- `docs/roadmap/project_file_model.md`
- `docs/roadmap/omi_storage_model.md`
- `docs/roadmap/omi_mvp_schema_lifecycle.md`
- `docs/roadmap/writer_assistant_core_candidate_schemas.md`
- `docs/roadmap/task_backlog.md`
- `docs/roadmap/phase_map.md`
- `docs/roadmap/open_questions.md`
- `docs/roadmap/risk_register.md`
- `docs/roadmap/decision_log.md`
- `docs/master_plan.md`
- `docs/plan.md`
- `training/reports/core_004_project_memory_canon_storage_model.md`

## Recommended Storage Layout

Recommendation: Option B, folder-based memory.

Future target:

```text
projects/{project_id}/memory/
  characters.json
  locations.json
  objects.json
  organizations.json
  timeline.json
  relationships.json
  plot_threads.json
  annotations.json
  open_questions.json
  continuity_warnings.json
  index.json
```

Reason: this layout is more human-readable, safer for incremental writes, easier to review, less likely to suffer whole-file accidental overwrites, more compatible with future search/query, and a better fit for relationship graph/timeline work.

## Rejected Storage Alternatives

- Option A, `project_memory.json`: rejected as default because it is more conflict-prone, harder to review incrementally, and riskier for accidental overwrite.
- Option C, hybrid: rejected as default because ownership between aggregate and detailed files would be ambiguous for the first implementation. It remains a possible later migration path.

## Memory Record Types Defined

- `character_memory_record`
- `location_memory_record`
- `object_memory_record`
- `organization_memory_record`
- `timeline_event_memory_record`
- `relationship_memory_record`
- `plot_thread_memory_record`
- `annotation_memory_record`
- `open_question_memory_record`
- `continuity_warning_memory_record`

Each record type uses a shared durable memory base contract with `record_id`, `project_id`, `record_type`, label/name, status, approval metadata, source candidate IDs, promotion record IDs, evidence references, provenance, confidence at promotion, revision history, supersession links, and notes.

## Promotion Path Summary

Future flow:

```text
owner-authored scene/project text
  -> extractor or manual candidate creation
  -> OMI candidate
  -> owner review
  -> OMI promotion record
  -> future apply-promotion step
  -> project memory/canon record
```

CORE-004 designs the target only. A future task must define atomic apply-promotion behavior, rollback behavior, validation, and tests.

Promotion must fail closed if approval, destination, evidence/provenance, safe target, valid memory record shape, promotion record, or confirmation is missing.

## Index and Search Implications

`memory/index.json` is recommended for the first implementation as derived navigation/search state. It may contain record IDs, record types, labels, aliases, status, source scene IDs, related record IDs, updated timestamps, and search keywords.

The index is not the primary truth source. Category files remain durable memory/canon truth.

## Revision and Rollback Notes

- Records should not be silently overwritten.
- Changes should append revision history.
- Superseded records should remain traceable.
- Delete should be archive-first unless owner explicitly deletes.
- Apply-promotion should be atomic or fail closed.
- Failed promotion must not corrupt memory files.
- Index updates and category-file updates must be consistent or rollback together.

## Remaining Deferred Decisions

- Runtime implementation of `memory/` files.
- Apply-promotion behavior and route/UI design.
- Rollback tests and failure-mode tests.
- Candidate merge/deduplication rules.
- Runtime ID and hash generation.
- Exact evidence locator strategy.
- Annotation UI and storage refinements.
- First extractor strategy and dependency spike.
- Whether `bible.json` should eventually mirror a subset of approved project memory.
- Whether memory records should become per-record files if category files become too large.

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
- No runtime files were created under `projects/`.
- No files were staged or committed.

## Commands Run

- `pwd`
- `git status --short --branch`
- `git log -1 --oneline`
- `ls docs/roadmap`
- `test -f docs/roadmap/writer_assistant_core_candidate_schemas.md && echo "CORE schema spec exists"`
- `test -f docs/roadmap/project_memory_canon_storage_model.md && echo exists || echo missing`
- Targeted `grep` / `sed` inspections for Writer Assistant Core, OMI, project file model, backlog, phase map, open questions, risk register, and decision log.
- Final validation commands are recorded in the task response after execution.
