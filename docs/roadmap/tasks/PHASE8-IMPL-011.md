# PHASE8-IMPL-011

## ID

`PHASE8-IMPL-011`

## Title

Writer Assistant Core candidate review queue and persistence gate planning

## Status

Active after `PHASE8-IMPL-011-T004` candidate persistence gate contract tests. `PHASE8-IMPL-011-T001`, `PHASE8-IMPL-011-T002`, `PHASE8-IMPL-011-T003`, and `PHASE8-IMPL-011-T004` are complete. `PHASE8-IMPL-011-T005` is ready/active. `PHASE8-IMPL-011-T006` and `PHASE8-IMPL-011-T007` are planned.

## Goal

Publish the planning and contract parent that decides how in-memory candidate drafts produced by the completed `PHASE8-IMPL-010` fixture orchestrator may later become project-local candidate records and review-queue entries without bypassing owner review, OMI boundaries, candidate-only status, evidence/provenance, or no-silent-promotion rules.

This parent is planning/contract-first. It does not implement candidate persistence, a candidate review queue, candidate review UI/API, apply-promotion, memory/canon mutation, runtime extraction, package changes, or generated prose in `PHASE8-IMPL-011-T001`, `PHASE8-IMPL-011-T002`, or `PHASE8-IMPL-011-T003`.

## Why Now

`PHASE8-IMPL-010` is complete through `PHASE8-IMPL-010-T007`. It delivered the review-safe fixture orchestration boundary:

- `backend/story_knowledge/extraction_orchestrator.py` as a pure, in-memory, fixture-only orchestrator;
- `tests/test_writer_assistant_core_extraction_orchestrator_contract.py` orchestrator contract tests;
- synthetic/in-memory fixture orchestration only;
- `candidate_drafts` as in-memory review support only;
- no automatic candidate persistence from orchestrator output;
- no candidate review UI/API;
- no raw artifact persistence;
- no runtime extraction;
- no memory/canon mutation;
- no apply-promotion.

The orchestrator can return `candidate_drafts` as review support, but there is no explicit gate deciding how those drafts may safely become candidate records or review-queue entries. The next risk is accidental persistence or review/UI expansion without an owner-gated boundary. Before implementing any review queue or candidate persistence from orchestrator output, the app needs a parent that defines the gate, queue shape, review lifecycle, and safety boundaries.

## Dependencies

- Completed parent: `PHASE8-IMPL-010` - Writer Assistant Core extraction orchestration planning and review-safe pipeline boundary.
- Completed child: `PHASE8-IMPL-010-T007` - Roadmap/status closeout.
- Foundation from `PHASE8-IMPL-006` through `PHASE8-IMPL-010`.
- Existing modules and tests:
  - `backend/story_knowledge/extraction_orchestrator.py`
  - `backend/story_knowledge/candidate_schema.py`
  - `backend/story_knowledge/candidate_record.py`
  - `backend/story_knowledge/candidate_persistence.py`
  - `backend/story_knowledge/candidate_index.py`
  - `backend/story_knowledge/source_map.py`
  - `backend/story_knowledge/evidence.py`
  - `tests/test_writer_assistant_core_extraction_orchestrator_contract.py`
  - `tests/test_writer_assistant_core_candidate_schema_contract.py`
  - `tests/test_writer_assistant_core_candidate_record_contract.py`
  - `tests/test_writer_assistant_core_candidate_persistence_contract.py`
  - `tests/test_writer_assistant_core_candidate_index_contract.py`

## Evidence Inputs

- `docs/roadmap/tasks/PHASE8-IMPL-010.md`
- `docs/roadmap/inventory/PHASE8-IMPL-010.md`
- `docs/roadmap/enrichment/PHASE8-IMPL-010.enrichment.json`
- `docs/roadmap/decisions/PHASE8-IMPL-010-review-safe-extraction-pipeline-contract-decision.md`
- `docs/roadmap/decisions/PHASE8-IMPL-010-candidate-review-handoff-persistence-boundary-decision.md`
- `docs/roadmap/tasks/PHASE8-IMPL-006.md`
- `docs/roadmap/tasks/PHASE8-IMPL-007.md`
- `docs/roadmap/tasks/PHASE8-IMPL-008.md`
- `docs/roadmap/tasks/PHASE8-IMPL-009.md`
- current roadmap truth files and validation records.

## Scope

Include:

- docs/status/planning publication in T001;
- candidate draft to candidate record persistence gate decision;
- review queue data shape and lifecycle decision;
- tests-first persistence gate contract if authorized by T002/T003;
- optional minimal pure persistence gate helper only if later children authorize it;
- candidate review UI/API boundary decision without implementing UI;
- safety regression or conditional hardening checks;
- roadmap/status closeout.

## Exclusions

Explicitly excluded:

- implementation in T001;
- automatic candidate persistence from orchestrator output;
- candidate review queue implementation;
- backend review routes or API endpoints;
- frontend review UI;
- apply-promotion;
- memory/canon mutation;
- raw artifact persistence;
- real runtime extraction;
- real BookNLP install, import, run, or execution;
- real spaCy install, import, run, or execution;
- package or dependency changes;
- generated prose, rewriting, continuation, imitation, polish, improvement, or expansion;
- model calls, Ollama calls, Story Check calls, demos, or app server runs;
- training data, JSONL records, dataset manifests, model artifacts, or fine-tuning configs.

## Child-Task Plan

1. `PHASE8-IMPL-011-T001` - Publish candidate review queue and persistence gate planning parent. Status: complete.
2. `PHASE8-IMPL-011-T002` - Candidate draft to candidate record persistence gate decision. Status: complete.
3. `PHASE8-IMPL-011-T003` - Review queue data shape and lifecycle decision. Status: complete.
4. `PHASE8-IMPL-011-T004` - Candidate persistence gate contract tests. Status: complete.
5. `PHASE8-IMPL-011-T005` - Minimal candidate persistence gate helper, if authorized. Status: ready/active.
6. `PHASE8-IMPL-011-T006` - Candidate review gate safety regression or conditional hardening. Status: planned.
7. `PHASE8-IMPL-011-T007` - Roadmap/status closeout. Status: planned.

## Child Task Details

### `PHASE8-IMPL-011-T001` - Publish candidate review queue and persistence gate planning parent

- Docs/status/planning only.
- Create parent task record, inventory, and enrichment JSON.
- Mark `PHASE8-IMPL-011` active.
- Mark T001 complete on success.
- Mark `PHASE8-IMPL-011-T002` ready/active.
- No runtime code, tests, routes, UI, package changes, candidate persistence, review queue implementation, apply-promotion, memory/canon mutation, or project runtime files.

### `PHASE8-IMPL-011-T002` - Candidate draft to candidate record persistence gate decision

- Docs/decision only.
- Status: complete as of 2026-06-24.
- Decision artifact: `docs/roadmap/decisions/PHASE8-IMPL-011-candidate-draft-to-record-persistence-gate-decision.md`.
- Accepted `candidate_drafts` as validated input support only.
- Accepted a future explicit persistence gate before candidate records may be written.
- Accepted existing candidate schema/record/persistence/index helpers as the only allowed persistence foundation.
- Recorded candidate draft input boundary: app-owned orchestrator or later approved in-memory support only; drafts are not records; drafts require validation, source document ref, source locator, evidence, provenance, bounded confidence, raw output refs where applicable, normalization status, and `human_review_required`.
- Recorded candidate record output boundary: persisted records must remain candidate-only/review-pending, use existing validators and project-local candidate storage helpers, preserve evidence/provenance/source locator/uncertainty, and avoid approved/canon/promoted status.
- Recorded persistence gate requirements: explicit owner-approved helper scope, fail-closed draft validation, candidate record validation, supported `candidate_type`, valid source document/locator/evidence/provenance, bounded confidence as uncertainty, support-only raw refs, `human_review_required = true`, pending/unreviewed owner state only if schema requires it, existing candidate index helpers only, no routes/UI/apply-promotion side effects, and no generated prose.
- Recorded fail-closed rules for unsupported types, missing evidence/locator/source/provenance, invalid confidence, ambiguous attribution, rejected or insufficient evidence where policy requires evidence-backed persistence, unknown fields, owner-decision prefill, approved/canon/promoted status, unsafe destinations, apply-promotion intent, generated prose fields, raw artifact write/read/list intent, runtime extraction/tool/model intent, training/JSONL/dataset fields, and unsafe IDs.
- T003 handoff: review queue data shape and lifecycle decision.
- T004/T005 handoff: tests-first persistence gate contract, then optional minimal helper only if authorized.
- No implementation claimed.
- No tests claimed.
- No runtime extraction claimed.
- No real BookNLP/spaCy install/run/import claimed.
- No route/UI/package changes claimed.
- No candidate/canon/memory mutation claimed.

### `PHASE8-IMPL-011-T003` - Review queue data shape and lifecycle decision

- Docs/decision only.
- Status: complete as of 2026-06-24.
- Decision artifact: `docs/roadmap/decisions/PHASE8-IMPL-011-review-queue-data-shape-lifecycle-decision.md`.
- Accepted review queue entries as workflow support only, not approval records, canon, memory, storyform truth, or apply-promotion.
- Recorded queue presence as non-approval; sorting, grouping, priority, confidence, and source count do not imply truth.
- Recorded required queue entry fields: `queue_entry_id`, `project_id`, `candidate_record_id`, `candidate_type`, `target_category`, `review_status`, `lifecycle_state`, `source_document`, `source_locator`, `evidence_summary`, `evidence_refs`, `provenance_summary`, `provenance_refs`, `confidence`, `uncertainty_flags`, `normalization_status`, `raw_output_refs`, `human_review_required`, `created_at`, and `updated_at`.
- Recorded forbidden queue fields: approval, canon, memory destination, apply-promotion, generated prose, rewrite/continuation, route/UI triggers, runtime tool triggers, and model calls.
- Recorded lifecycle states: `draft_ready_for_review`, `needs_more_evidence`, `blocked_invalid_support`, `owner_review_pending`, `owner_reviewed_rejected`, `owner_reviewed_deferred`, `duplicate_candidate`, `superseded_candidate`, and `archived_without_promotion`.
- Recorded review status labels: `pending`, `needs_info`, `rejected`, `deferred`, `duplicate`, `superseded`, and `archived`; `approved` is not a PHASE8-IMPL-011 queue status.
- Recorded evidence/provenance display requirements, insufficient-evidence and rejected-output handling, grouping/sorting/filtering boundaries, future owner action labels, storage/persistence boundaries, and T004/T005/T006 handoffs.
- No implementation claimed.
- No tests claimed.
- No runtime extraction claimed.
- No real BookNLP/spaCy install/run/import claimed.
- No route/UI/package changes claimed.
- No candidate/canon/memory mutation claimed.

### `PHASE8-IMPL-011-T004` - Candidate persistence gate contract tests

- Tests-first only.
- Status: complete as of 2026-06-24.
- Added expected-red contract coverage in `tests/test_writer_assistant_core_candidate_review_gate_contract.py`.
- Future module: `backend/story_knowledge/candidate_review_gate.py`.
- Future public APIs encoded by the contract: `validate_candidate_draft_for_persistence(draft) -> dict`, `build_candidate_record_from_draft(draft, *, project_id) -> dict`, `build_review_queue_entry(candidate_record, *, project_id) -> dict`, and `persist_candidate_record_for_review(candidate_record, *, project_dir) -> dict`.
- Encoded the T002 persistence gate and T003 review queue data shape/lifecycle boundaries.
- Covered draft validation, draft-to-record conversion, review queue entry shape, persistence gate behavior, fail-closed unsupported/unsafe drafts, no owner-decision prefill, no approved/canon/promoted status, no apply-promotion, no memory/canon mutation, no UI/API/routes, no generated prose, no-side-effect guarantees, and a future production source-level boundary scan.
- Target expected-red result: `.venv-unsloth-clean/bin/python -m pytest tests/test_writer_assistant_core_candidate_review_gate_contract.py -q` fails during collection with `ImportError: cannot import name 'candidate_review_gate' from 'backend.story_knowledge'`, limited to the missing future module/symbol; no syntax errors, no unrelated import failures, no skipped tests, and no xfails.
- Regression results: candidate schema/record/storage/persistence/list/index/index-safety regressions PASS (307 tests); orchestrator contract and source/evidence contract PASS (171 tests); focused OMI/project regressions PASS (109 tests).
- Used `tmp_path` only for filesystem assertions; no real project files created.
- No implementation added: no candidate_review_gate module, no candidate persistence gate helper, no review queue implementation, no review UI/API, no backend routes, no frontend UI, no package/dependency changes, no runtime extraction, no real BookNLP/spaCy install/run, and no candidate/canon/memory mutation.
- T005 handoff: minimal candidate persistence gate helper, only if authorized.

### `PHASE8-IMPL-011-T005` - Minimal candidate persistence gate helper, if authorized

- Optional pure helper implementation only if T002-T004 authorize.
- Candidate-only records through existing validators.
- Project-local candidate storage only in `tmp_path` tests or as existing candidate persistence helpers allow.
- No orchestrator auto-persistence.
- No review UI/API.
- No apply-promotion.
- No memory/canon mutation.

### `PHASE8-IMPL-011-T006` - Candidate review gate safety regression or conditional hardening

- Validate no owner-decision prefill, no approval/canon/memory mutation, no apply-promotion, no generated prose, and no route/UI/package/runtime expansion.
- Conditional repair only if tests reveal gaps.

### `PHASE8-IMPL-011-T007` - Roadmap/status closeout

- Close parent.
- Summarize decisions/tests/helpers if any.
- Recommend next parent only.
- No runtime expansion.

## Acceptance Criteria

- `docs/roadmap/tasks/PHASE8-IMPL-011.md` exists.
- `docs/roadmap/inventory/PHASE8-IMPL-011.md` exists.
- `docs/roadmap/enrichment/PHASE8-IMPL-011.enrichment.json` exists.
- `PHASE8-IMPL-011` is active in roadmap/status docs.
- `PHASE8-IMPL-011-T001` is complete if successful.
- `PHASE8-IMPL-011-T002` is complete.
- `PHASE8-IMPL-011-T003` is ready/active.
- T001 records `PHASE8-IMPL-010` as complete through T007.
- T001 records candidate draft support as in-memory only.
- T001 creates no backend code, tests, routes, UI, packages, project runtime files, training data, JSONL records, or datasets.
- T001 does not persist candidate records.
- T001 does not implement a review queue.
- T001 does not implement apply-promotion.
- T001 does not mutate memory/canon.
- T001 preserves no-prose and no-canon-mutation boundaries.

## Validation Expectations

- `python3 scripts/check_enrichment.py`
- `python3 scripts/validate_roadmap.py`
- non-LeanCTX whitespace check for changed docs
- narrow `/usr/bin/git diff --check -- ...`
- `.external_sources/` source-cache safety checks

Do not run pytest in T001 because no tests or runtime code change.

## Safety/Product Boundaries

- Owner review remains mandatory before anything can become approved truth.
- Candidate drafts are in-memory review support only; they are not candidate records, canon, memory, owner decisions, or promotion.
- Candidate persistence from orchestrator output is not authorized unless a later owner-approved child explicitly defines a review-safe gate.
- A review queue is a review surface, not an approval or canon queue.
- No real extraction runtime is authorized.
- No apply-promotion is authorized.
- No memory/canon mutation is authorized.
- No backend routes or frontend UI are authorized.
- No package/dependency changes are authorized.
- No generated prose, rewrite, or continuation behavior is authorized.

## Current Status

`PHASE8-IMPL-011` is active after T003. `PHASE8-IMPL-011-T001` is complete as docs/status/planning only and created the parent task record, inventory, and enrichment JSON, and updated roadmap/status docs. `PHASE8-IMPL-011-T002` is complete as docs/decision only and created `docs/roadmap/decisions/PHASE8-IMPL-011-candidate-draft-to-record-persistence-gate-decision.md`. T002 accepted a future explicit candidate draft to candidate record persistence gate, recorded candidate draft input and candidate record output boundaries, required existing candidate schema/record/persistence/index helpers, source locators, evidence, provenance, candidate-only/review-pending status, no owner-decision prefill, no apply-promotion, no memory/canon mutation, and fail-closed rejection rules. `PHASE8-IMPL-011-T003` is complete as docs/decision only and created `docs/roadmap/decisions/PHASE8-IMPL-011-review-queue-data-shape-lifecycle-decision.md`. T003 accepted review queue entries as workflow support only, queue presence as non-approval, lifecycle states as review workflow states only, evidence/provenance/source locator display as mandatory, insufficiency/rejected-output handling as explicit states or quarantine paths, grouping/sorting/filtering as workflow convenience only, and owner action labels as future planning terms only. `PHASE8-IMPL-011-T004` is complete as tests-first only and added expected-red contract coverage in `tests/test_writer_assistant_core_candidate_review_gate_contract.py` for the future `backend.story_knowledge.candidate_review_gate` module and its `validate_candidate_draft_for_persistence`, `build_candidate_record_from_draft`, `build_review_queue_entry`, and `persist_candidate_record_for_review` APIs. The target pytest is expected-red with a collection `ImportError` limited to the missing future module; candidate, orchestrator, source/evidence, and focused OMI/project regressions pass. `PHASE8-IMPL-011-T005` is ready/active. `PHASE8-IMPL-011-T006` and `PHASE8-IMPL-011-T007` are planned. No candidate persistence, candidate review gate implementation, candidate review queue implementation, candidate review UI/API, apply-promotion, memory/canon mutation, runtime extraction, backend routes, frontend UI, package/dependency changes, generated prose, or training/JSONL/dataset work was added by T001, T002, T003, or T004.

## Next Child

`PHASE8-IMPL-011-T005` - Minimal candidate persistence gate helper, if authorized.
