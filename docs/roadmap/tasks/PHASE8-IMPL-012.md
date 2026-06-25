# PHASE8-IMPL-012

## ID

`PHASE8-IMPL-012`

## Title

Writer Assistant Core review queue storage and owner-review workflow planning

## Status

Active after `PHASE8-IMPL-012-T005`. `PHASE8-IMPL-012-T001` is complete as docs/status/planning only. `PHASE8-IMPL-012-T002` is complete as docs/decision only and accepted the review queue storage contract decision. `PHASE8-IMPL-012-T003` is complete as docs/decision only and accepted the owner action workflow boundary decision. `PHASE8-IMPL-012-T004` is complete as tests-first only and added expected-red review queue storage contract tests. `PHASE8-IMPL-012-T005` is complete and created the minimal pure review queue storage helper `backend/story_knowledge/review_queue_storage.py`; the target review queue storage contract now passes. `PHASE8-IMPL-012-T006` is ready/active. `PHASE8-IMPL-012-T007` is planned. `PHASE8-IMPL-012` starts after completed `PHASE8-IMPL-011` (complete through `PHASE8-IMPL-011-T007`).

## Goal

Publish the planning and contract parent that decides whether and how the in-memory review queue entries produced by the completed `PHASE8-IMPL-011` candidate review gate should be stored, listed, loaded, and prepared for future owner-review workflows without turning queue state into approval, canon truth, apply-promotion, review UI/API scope creep, or memory/canon mutation.

This parent is planning/contract-first. It does not implement review queue storage, owner action workflow, review UI/API, backend review routes, frontend review UI, apply-promotion, memory/canon mutation, raw artifact persistence, or runtime extraction in `PHASE8-IMPL-012-T001`. `PHASE8-IMPL-012-T001` is docs/status/planning only.

## Why Now

`PHASE8-IMPL-011` is complete through `PHASE8-IMPL-011-T007`. It delivered the candidate review gate and persistence boundary:

- `backend/story_knowledge/candidate_review_gate.py` as a pure, standard-library-only, deterministic, candidate-only/review-pending persistence gate;
- `tests/test_writer_assistant_core_candidate_review_gate_contract.py` candidate review gate contract tests;
- candidate draft validation;
- candidate-only record construction;
- an in-memory review queue entry builder (`build_review_queue_entry`);
- project-local candidate-only persistence through existing candidate persistence helpers;
- no review queue storage/listing;
- no review UI/API;
- no owner action workflow beyond undecided/pending metadata;
- no apply-promotion;
- no memory/canon mutation;
- no runtime extraction.

The review queue entry is built in memory only; it is not stored, listed, or loaded yet. The next risk is accidental queue storage, review UI/API, owner action workflow, or apply-promotion without an explicit contract. Before implementing any review queue storage or owner actions, the app needs a parent that defines storage, lifecycle, owner-action boundaries, and no-canon/no-promotion safety rules. Queue presence remains non-approval, and owner review remains mandatory before anything can become approved truth.

## Dependencies

- Completed parent: `PHASE8-IMPL-011` - Writer Assistant Core candidate review queue and persistence gate planning.
- Completed child: `PHASE8-IMPL-011-T007` - Roadmap/status closeout.
- Foundation from `PHASE8-IMPL-006` through `PHASE8-IMPL-011`.
- Existing modules and tests:
  - `backend/story_knowledge/candidate_review_gate.py`
  - `backend/story_knowledge/candidate_schema.py`
  - `backend/story_knowledge/candidate_record.py`
  - `backend/story_knowledge/candidate_storage.py`
  - `backend/story_knowledge/candidate_persistence.py`
  - `backend/story_knowledge/candidate_index.py`
  - `backend/story_knowledge/extraction_orchestrator.py`
  - `backend/story_knowledge/source_map.py`
  - `backend/story_knowledge/evidence.py`
  - `tests/test_writer_assistant_core_candidate_review_gate_contract.py`
  - `tests/test_writer_assistant_core_candidate_schema_contract.py`
  - `tests/test_writer_assistant_core_candidate_record_contract.py`
  - `tests/test_writer_assistant_core_candidate_storage_contract.py`
  - `tests/test_writer_assistant_core_candidate_persistence_contract.py`
  - `tests/test_writer_assistant_core_candidate_list_contract.py`
  - `tests/test_writer_assistant_core_candidate_index_contract.py`
  - `tests/test_writer_assistant_core_candidate_index_safety_regression.py`
  - `tests/test_writer_assistant_core_extraction_orchestrator_contract.py`

## Evidence Inputs

- `docs/roadmap/tasks/PHASE8-IMPL-011.md`
- `docs/roadmap/inventory/PHASE8-IMPL-011.md`
- `docs/roadmap/enrichment/PHASE8-IMPL-011.enrichment.json`
- `docs/roadmap/decisions/PHASE8-IMPL-011-candidate-draft-to-record-persistence-gate-decision.md`
- `docs/roadmap/decisions/PHASE8-IMPL-011-review-queue-data-shape-lifecycle-decision.md`
- `docs/roadmap/tasks/PHASE8-IMPL-010.md`
- `backend/story_knowledge/candidate_review_gate.py`
- `backend/story_knowledge/candidate_schema.py`
- `backend/story_knowledge/candidate_record.py`
- `backend/story_knowledge/candidate_storage.py`
- `backend/story_knowledge/candidate_persistence.py`
- `backend/story_knowledge/candidate_index.py`
- `backend/story_knowledge/extraction_orchestrator.py`
- `backend/story_knowledge/source_map.py`
- `backend/story_knowledge/evidence.py`
- current roadmap truth files and validation records.

## Scope

Include:

- docs/status/planning publication in T001;
- review queue storage contract decision;
- owner action workflow boundary decision;
- tests-first review queue storage contract if authorized by T002/T003;
- optional minimal pure queue storage helper only if later children authorize it;
- review UI/API planning boundary decision without implementing UI;
- safety regression or conditional hardening checks;
- roadmap/status closeout.

## Exclusions

Explicitly excluded:

- implementation in T001;
- review queue storage/listing implementation;
- owner action workflow implementation;
- review UI/API implementation;
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

1. `PHASE8-IMPL-012-T001` - Publish review queue storage and owner-review workflow planning parent. Status: complete.
2. `PHASE8-IMPL-012-T002` - Review queue storage contract decision. Status: complete.
3. `PHASE8-IMPL-012-T003` - Owner action workflow boundary decision. Status: complete.
4. `PHASE8-IMPL-012-T004` - Review queue storage contract tests. Status: complete.
5. `PHASE8-IMPL-012-T005` - Minimal review queue storage helper, if authorized. Status: complete.
6. `PHASE8-IMPL-012-T006` - Review queue safety regression or conditional hardening. Status: ready/active.
7. `PHASE8-IMPL-012-T007` - Roadmap/status closeout. Status: planned.

## Child Task Details

### `PHASE8-IMPL-012-T001` - Publish review queue storage and owner-review workflow planning parent

- Docs/status/planning only.
- Create parent task record, inventory, and enrichment JSON.
- Mark `PHASE8-IMPL-012` active.
- Mark T001 complete on success.
- Mark `PHASE8-IMPL-012-T002` ready/active.
- No runtime code, tests, routes, UI, package changes, review queue storage, owner action workflow, apply-promotion, memory/canon mutation, or project runtime files.

### `PHASE8-IMPL-012-T002` - Review queue storage contract decision

- Docs/decision only. Status: complete.
- Decision artifact: `docs/roadmap/decisions/PHASE8-IMPL-012-review-queue-storage-contract-decision.md`.
- Storage strategy recorded: project-local stored queue entry read model linked to candidate records by `candidate_record_id`; candidate records remain the source of candidate content and candidate-only status; queue entries duplicate only minimal display/read-model fields; queue entries must be rebuildable/repairable from candidate records; queue storage never writes memory/canon or applies promotion.
- Storage root/path boundary recorded: future root `projects/{project_id}/writer_assistant/review_queue/`; optional files `entries/{queue_entry_id}.json` and `index.json`; path-safe validated `project_id`/`queue_entry_id`/`candidate_record_id`; no absolute paths, traversal, backslashes, Windows drive prefixes, nested arbitrary segments, or hidden dot-path IDs; `source_path_hint` stays debug/display metadata only; forbidden locations include `memory/`, `bible.json`, `storyform.json`, `project.json`, `scenes/`, `chapters/`, `notes/`, `materials/`, `omi/promotions/`, `training/`, `dataset_manifest.json`, JSONL files, raw extraction artifact folders, `.external_sources/`, `frontend/`, backend route files, and package/dependency files.
- Queue entry stored shape recorded: required identity/lifecycle/evidence/provenance fields aligned with the `PHASE8-IMPL-011-T003` queue entry shape; optional grouping/notes/integrity fields; forbidden approval/canon/promotion/prose/route/UI/tool/model/raw/training fields.
- Allowed `review_status` values recorded: `pending`, `needs_info`, `rejected`, `deferred`, `duplicate`, `superseded`, `archived`. Allowed `lifecycle_state` values recorded: `draft_ready_for_review`, `needs_more_evidence`, `blocked_invalid_support`, `owner_review_pending`, `owner_reviewed_rejected`, `owner_reviewed_deferred`, `duplicate_candidate`, `superseded_candidate`, `archived_without_promotion`. `approved` is not an allowed queue status; `owner_reviewed_*` and `archived_without_promotion` do not mutate memory/canon or promote.
- Candidate linkage/integrity rules recorded: exactly one candidate record per entry; validated IDs; preserved `candidate_type`/`target_category` alignment; no auto-create/mutate/approve of candidate records; references only for duplicate/conflict/related IDs; fail-closed/quarantine on missing or invalid candidate records.
- Evidence/provenance requirements recorded: source identity, source locator, evidence summary/refs, provenance summary/refs, raw output refs where applicable, confidence-as-uncertainty, normalization status, `human_review_required`, and insufficient-evidence/rejected-output reasons; queue storage must not strip evidence/provenance.
- Index contract recorded: future `index.json` is derived/rebuildable workflow support only with schema version, project id, timestamps, minimal entry summaries, and counts by status/lifecycle/type; no canon/memory/approval/apply-promotion fields; index corruption must not affect candidate records.
- Storage operation boundary recorded: future helper categories named as planning terms only; write/read/list helpers stay project-local, validate before write, fail closed with no partial writes where practical, validate or quarantine on read/list; index helpers stay derived and rebuildable; no owner actions, apply-promotion, memory/canon mutation, or UI/API/routes.
- Owner action relationship recorded: T002 defines storage only; T003 defines owner action workflow boundaries; queue storage may store workflow status/reviewer notes only if T003 authorizes; owner action storage is not apply-promotion or memory/canon mutation.
- Failure/quarantine policy recorded: fail closed or quarantine on invalid IDs, unsupported status/lifecycle, missing evidence/provenance/source locator, invalid linkage, approved/canon/promoted candidates, forbidden destinations/fields, apply-promotion/memory/canon/prose/raw/runtime/training intents, unknown fields, and unsafe paths; no partial write remains after failure unless future tests define a safe candidate-only invalid-support quarantine folder.
- T003 handoff recorded: owner action workflow boundary decision.
- T004/T005 handoff recorded: tests-first storage contract coverage (T004) and optional minimal helper only if authorized (T005).
- No runtime code, tests, queue storage implementation, queue listing/loading, owner action workflow, review UI/API, backend routes, frontend UI, apply-promotion, memory/canon mutation, raw artifact persistence, runtime extraction, real BookNLP/spaCy install/run, package/dependency changes, model calls, or training/JSONL/dataset work was added in T002.

### `PHASE8-IMPL-012-T003` - Owner action workflow boundary decision

- Docs/decision only. Status: complete.
- Decision artifact: `docs/roadmap/decisions/PHASE8-IMPL-012-owner-action-workflow-boundary-decision.md`.
- Owner action purpose recorded: owner actions are explicit review workflow commands on candidate-linked queue entries that capture owner review intent and mark candidate support as needs-info, rejected, deferred, duplicate, superseded, or archived, with reviewer notes or evidence requests; they are not a promotion path, memory/canon mutation, automatic approval, storyform truth, generated prose workflow, runtime extraction, or raw artifact persistence.
- Allowed owner action commands recorded: `request_more_evidence`, `mark_needs_info`, `defer_review`, `reject_candidate`, `mark_duplicate`, `mark_superseded`, `archive_without_promotion`, `add_reviewer_note`, `clear_reviewer_note`, `edit_queue_metadata`; optional future-only `prepare_for_promotion_review` and `mark_ready_for_separate_promotion_flow`; `approve_candidate`, `promote_candidate`, `write_to_memory`, `write_to_canon`, `apply_promotion`, `generate_prose`, `rewrite_source`, `continue_scene`, and `run_extractor` are not allowed.
- Allowed owner action states recorded: `pending`, `needs_info`, `deferred`, `rejected`, `duplicate`, `superseded`, `archived_without_promotion`, `blocked_invalid_support`, `ready_for_separate_promotion_review`; `ready_for_separate_promotion_review` is only a pointer to a future separate promotion workflow and is not approval or memory/canon mutation; `approved`, `promoted`, `canon`, and `memory` are not allowed states.
- Owner action record shape recorded: required identity/action/result/actor/evidence/provenance and `human_review_required`/`no_promotion_performed`/`no_memory_canon_mutation` fields; optional previous-state/relation/integrity fields; forbidden approval/canon/promotion/destination/prose/route/UI/tool/model/raw/training fields.
- Queue entry mutation boundary recorded: owner actions may update only workflow fields (`review_status`, `lifecycle_state`, `reviewer_notes`, `insufficient_evidence_reason`, `rejected_output_reason`, `duplicate_candidate_ids`, `conflict_candidate_ids`, `related_candidate_ids`, `updated_at`) if future tests authorize; approved/promoted/canon status, memory/canon destination, apply-promotion flag, candidate content rewrite, source/evidence/provenance deletion, raw artifact write/list/load, route/UI trigger, and model/tool invocation are forbidden.
- Candidate record relationship recorded: owner actions may reference candidate records but must not modify them unless a later tests-first helper authorizes safe candidate-only metadata synchronization; owner actions must not set approved/canon/promoted status, prefill owner decision as approved, write memory/canon, or change candidate-only status; candidate records remain separate from queue entries and action records.
- Apply-promotion boundary recorded: owner action workflow is not apply-promotion; apply-promotion remains unimplemented and out of scope; any future apply-promotion path must be a separate owner-approved, audited, explicit, separately tested parent/task and must not be hidden inside queue storage or owner action helpers.
- Memory/canon boundary recorded: owner action workflow must never write `memory/*.json`, `memory/index.json`, `bible.json`, `storyform.json`, `project.json`, `scenes/`, `chapters/`, `notes/`, `materials/`, or owner-authored source files; owner actions are workflow metadata only.
- Evidence/provenance requirements recorded: every future owner action record or queue update must preserve or reference source identity, source locator, evidence/provenance refs, `candidate_record_id`, `queue_entry_id`, action command, actor reference, timestamp, reason/reviewer note where applicable, `human_review_required`, `no_promotion_performed`, and `no_memory_canon_mutation`; owner actions must not strip evidence/provenance.
- Owner action storage boundary recorded: T003 defines action storage shape only if later authorized and does not implement it; potential future storage root `projects/{project_id}/writer_assistant/review_queue/actions/{action_id}.json` sits inside the T002 review queue boundary; future action storage must be project-local, validate before writing, fail closed, and never write memory/canon, raw artifacts, training/JSONL/dataset files, or trigger UI/API routes.
- Review UI/API boundary recorded: T003 does not implement review UI/API, backend routes, or frontend screens; UI/API planning remains deferred; any future review UI/API must display evidence/provenance, uncertainty, non-approval status, and no-promotion warnings, and must not perform apply-promotion unless a separate approved workflow exists.
- Failure/quarantine policy recorded: fail closed or quarantine on unsupported command/state, approved/promoted/canon state requests, apply-promotion/memory-canon/prose/raw/runtime/tool/model/training intents, missing `queue_entry_id`/`candidate_record_id`/source/evidence/provenance refs, invalid actor reference, unsafe IDs/path traversal, unknown fields, and any attempt to mutate candidate content or approved truth; no partial write remains after failure unless future tests define a safe invalid-support quarantine path.
- T004 handoff recorded: tests-first storage contract and owner action boundary coverage.
- T005/T006 handoff recorded: optional minimal helper only if authorized (T005); safety regression or conditional hardening (T006).
- No runtime code, tests, owner action workflow implementation, owner action storage, review queue storage, queue listing/loading, review UI/API, backend routes, frontend UI, apply-promotion, memory/canon mutation, candidate/canon/memory mutation, raw artifact persistence, runtime extraction, real BookNLP/spaCy install/run, package/dependency changes, model calls, or training/JSONL/dataset work was added in T003.

### `PHASE8-IMPL-012-T004` - Review queue storage contract tests

- Tests-first only. Status: complete.
- Added `tests/test_writer_assistant_core_review_queue_storage_contract.py`, which imports the future `backend.story_knowledge.review_queue_storage` module normally and is expected-red until `PHASE8-IMPL-012-T005` creates the module, if authorized.
- Encoded future public APIs: `validate_review_queue_entry`, `build_review_queue_entry_from_candidate_record`, `review_queue_storage_dir`, `review_queue_entry_path`, `review_queue_index_path`, `write_review_queue_entry`, `read_review_queue_entry`, `list_review_queue_entries`, `build_review_queue_index`, and `validate_owner_action_record`.
- Encoded the T002 storage contract (queue entry shape, allowed `review_status`/`lifecycle_state` values, forbidden fields, project-local storage paths, derived/rebuildable index contract) and the T003 owner action boundary (allowed/forbidden commands and states, owner action record shape, `no_promotion_performed`/`no_memory_canon_mutation` affirmations).
- `tmp_path` only for all filesystem assertions; synthetic in-test fixtures only, reusing existing candidate record validators and `candidate_review_gate.build_review_queue_entry` for faithful queue entry fixtures.
- Expected-red target result: collection `ImportError: cannot import name 'review_queue_storage' from 'backend.story_knowledge'`, limited to the missing future module; no syntax errors, no unrelated import failures, no skips, no xfails.
- Candidate review gate contract, candidate regressions (schema/record/storage/persistence/list/index/index-safety), orchestrator contract, source/evidence contract (632 combined), and focused OMI/project regressions (109) pass.
- No queue storage implementation, queue listing/loading, owner action workflow, review UI/API, backend routes, frontend UI, apply-promotion, memory/canon mutation, candidate/canon/memory mutation, raw artifact persistence, runtime extraction, real BookNLP/spaCy install/run, or package changes were added.
- No UI/routes.
- No apply-promotion.
- No memory/canon mutation.

### `PHASE8-IMPL-012-T005` - Minimal review queue storage helper, if authorized

- Status: complete.
- Created `backend/story_knowledge/review_queue_storage.py` as a pure, standard-library-only, deterministic, project-local, candidate-linked, candidate-only, review-workflow-only queue storage helper over existing candidate validation and candidate review gate helpers.
- Implemented APIs: `validate_review_queue_entry`, `build_review_queue_entry_from_candidate_record`, `review_queue_storage_dir`, `review_queue_entry_path`, `review_queue_index_path`, `write_review_queue_entry`, `read_review_queue_entry`, `list_review_queue_entries`, `build_review_queue_index`, and `validate_owner_action_record`.
- `validate_review_queue_entry` accepts only dict input, deep-copies, rejects missing/unknown/forbidden fields, enforces allowed `review_status`/`lifecycle_state` values, validates confidence and path-safe IDs, and fails closed with generic `ValueError`.
- `build_review_queue_entry_from_candidate_record` delegates to `candidate_review_gate.build_review_queue_entry`, sets `review_status = "pending"`/`lifecycle_state = "draft_ready_for_review"`, preserves source/evidence/provenance support, and fails closed for invalid/approved/promoted candidate records.
- `review_queue_storage_dir`/`review_queue_entry_path`/`review_queue_index_path` derive project-local `writer_assistant/review_queue/` paths only, create no directories, and reject unsafe IDs.
- `write_review_queue_entry` validates before writing, writes only under `writer_assistant/review_queue/entries/`, fails closed with no partial write, and returns candidate-linked review-workflow-only metadata.
- `read_review_queue_entry`/`list_review_queue_entries` validate loaded entries, fail closed on missing/malformed data, and never read memory/canon/raw locations.
- `build_review_queue_index` returns a derived/rebuildable index (schema version, project id, timestamp, minimal entry summaries, counts by status/lifecycle/type) and writes no files.
- `validate_owner_action_record` validates owner action record shape only against the T003 allowed commands/states, requires `no_promotion_performed`/`no_memory_canon_mutation` true, and rejects forbidden commands/states/fields; it executes no owner actions.
- Target contract result: `tests/test_writer_assistant_core_review_queue_storage_contract.py` PASS (359 tests).
- Candidate review gate/candidate/orchestrator/source-evidence regressions PASS (632 tests); focused OMI/project regressions PASS (109 tests).
- No runtime extraction; no real BookNLP/spaCy install/run (availability guard reports both false); no route/UI/package changes; no review UI/API; no owner action workflow execution; no apply-promotion; no raw artifact persistence; no memory/canon mutation.

### `PHASE8-IMPL-012-T006` - Review queue safety regression or conditional hardening

- Status: ready/active.
- Validate no approval/canon/memory mutation.
- Validate no apply-promotion.
- Validate no route/UI/package/runtime expansion.
- Validate no generated prose.
- Conditionally repair only if tests reveal gaps.

### `PHASE8-IMPL-012-T007` - Roadmap/status closeout

- Close parent.
- Summarize decisions/tests/helpers if any.
- Recommend next parent only.
- No runtime expansion.

## Acceptance Criteria

- `docs/roadmap/tasks/PHASE8-IMPL-012.md` exists.
- `docs/roadmap/inventory/PHASE8-IMPL-012.md` exists.
- `docs/roadmap/enrichment/PHASE8-IMPL-012.enrichment.json` exists.
- `PHASE8-IMPL-012` is active in roadmap/status docs.
- `PHASE8-IMPL-012-T001` is complete if successful.
- `PHASE8-IMPL-012-T002` is ready/active.
- T001 records `PHASE8-IMPL-011` as complete through T007.
- T001 records review queue entries as workflow support only.
- T001 creates no backend code, tests, routes, UI, packages, project runtime files, training data, JSONL records, or datasets.
- T001 does not implement review queue storage.
- T001 does not implement owner action workflow.
- T001 does not implement review UI/API.
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
- Review queue entries are workflow support only; queue presence is non-approval and is not canon, memory, owner decisions, or promotion.
- Review queue storage is not authorized unless a later owner-approved child explicitly defines a queue storage contract.
- An owner action workflow is a review surface, not apply-promotion; owner action storage is not memory/canon mutation.
- No real extraction runtime is authorized.
- No apply-promotion is authorized.
- No memory/canon mutation is authorized.
- No backend routes or frontend UI are authorized.
- No package/dependency changes are authorized.
- No generated prose, rewrite, or continuation behavior is authorized.

## Current Status

`PHASE8-IMPL-012` is active after T005. `PHASE8-IMPL-012-T001` is complete as docs/status/planning only and created the parent task record, inventory, and enrichment JSON, and updated roadmap/status docs. `PHASE8-IMPL-012-T002` is complete as docs/decision only and accepted `docs/roadmap/decisions/PHASE8-IMPL-012-review-queue-storage-contract-decision.md`, which records a project-local, candidate-linked, candidate-only, review-workflow-only, evidence/provenance-backed, fail-closed review queue storage contract with allowed `review_status`/`lifecycle_state` values, a stored queue entry shape, a derived/rebuildable index contract, a storage operation boundary, candidate linkage/integrity rules, and forbidden destinations. `PHASE8-IMPL-012-T003` is complete as docs/decision only and accepted `docs/roadmap/decisions/PHASE8-IMPL-012-owner-action-workflow-boundary-decision.md`, which records owner actions as review workflow commands and states only (not apply-promotion, not memory/canon mutation, not approval/canon truth), the allowed owner action commands and states, a future owner action record shape, the queue entry mutation boundary, the candidate record relationship, apply-promotion and memory/canon boundaries, evidence/provenance requirements, an owner action storage boundary, a deferred review UI/API boundary, and a fail-closed/quarantine policy. `PHASE8-IMPL-012-T004` is complete as tests-first only and added `tests/test_writer_assistant_core_review_queue_storage_contract.py`, an expected-red contract test that imports the future `backend.story_knowledge.review_queue_storage` module and encodes the T002 storage contract and T003 owner action boundary across queue entry validation, queue entry build-from-candidate, storage path helpers, write/read/list/index helpers, owner action record validation, fail-closed matrices, no-side-effect guarantees, and a future production source-level boundary scan. The target pytest is expected-red with a collection `ImportError` limited to the missing future module, and the candidate review gate/candidate/orchestrator/source-evidence regressions (632) and focused OMI/project regressions (109) pass. `PHASE8-IMPL-012-T005` is complete and created `backend/story_knowledge/review_queue_storage.py`, a pure, standard-library-only, deterministic, project-local, candidate-linked, candidate-only, review-workflow-only queue storage helper over existing candidate validation and candidate review gate helpers, implementing `validate_review_queue_entry`, `build_review_queue_entry_from_candidate_record`, `review_queue_storage_dir`, `review_queue_entry_path`, `review_queue_index_path`, `write_review_queue_entry`, `read_review_queue_entry`, `list_review_queue_entries`, `build_review_queue_index`, and `validate_owner_action_record`; the target review queue storage contract now passes (359 tests), and candidate review gate/candidate/orchestrator/source-evidence regressions (632) and focused OMI/project regressions (109) still pass. `PHASE8-IMPL-011` is recorded as complete through `PHASE8-IMPL-011-T007`. Review queue entries remain workflow support only; the new helper stores queue entries only under project-local `writer_assistant/review_queue/` (exercised in tmp_path tests), validates before write, fails closed, and the derived index remains rebuildable workflow support only. `PHASE8-IMPL-012-T006` is ready/active as the review queue safety regression or conditional hardening child. No queue storage owner action workflow execution, owner action storage, review UI/API, backend review routes, frontend review UI, apply-promotion, memory/canon mutation, candidate/canon/memory mutation, raw artifact persistence, runtime extraction, real BookNLP/spaCy install/run/import, package/dependency changes, generated prose, model calls, or training/JSONL/dataset work is authorized or was added in T005; T005 added only the minimal pure review queue storage helper.

## Next Child

`PHASE8-IMPL-012-T006` - Review queue safety regression or conditional hardening.
