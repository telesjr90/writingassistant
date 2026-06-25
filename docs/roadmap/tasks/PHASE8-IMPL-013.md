# PHASE8-IMPL-013

## ID

`PHASE8-IMPL-013`

## Title

Writer Assistant Core review UI/API planning and owner-action workflow contract

## Status

Active after `PHASE8-IMPL-013-T001`. `PHASE8-IMPL-013-T001` is complete as docs/status/planning only and created the parent task record, inventory, and enrichment JSON, and updated roadmap/status docs. `PHASE8-IMPL-013-T002` is ready/active. `PHASE8-IMPL-013-T003` through `PHASE8-IMPL-013-T007` are planned. `PHASE8-IMPL-013` started after completed `PHASE8-IMPL-012` (complete through `PHASE8-IMPL-012-T007`).

## Goal

Publish the planning and contract parent that decides whether and how the project-local review queue storage and owner action record validation produced by the completed `PHASE8-IMPL-012` review queue storage helper should be exposed through a read-only review queue API, an owner-action command API, and a frontend review UI, without implementing any backend routes, frontend screens, owner action execution, apply-promotion, or memory/canon mutation.

This parent is planning/contract-first. It does not implement review UI/API, backend review routes, frontend review UI, owner action execution, apply-promotion, memory/canon mutation, raw artifact persistence, or runtime extraction in `PHASE8-IMPL-013-T001`. `PHASE8-IMPL-013-T001` is docs/status/planning only.

## Why Now

`PHASE8-IMPL-012` is complete through `PHASE8-IMPL-012-T007`. It delivered the review queue storage and owner-review workflow planning layer:

- `backend/story_knowledge/review_queue_storage.py` as a pure, standard-library-only, deterministic, project-local, candidate-linked, candidate-only, review-workflow-only queue storage helper;
- `tests/test_writer_assistant_core_review_queue_storage_contract.py` review queue storage contract tests;
- review queue entry validation;
- candidate-linked queue entry construction;
- project-local queue path derivation;
- project-local queue entry write/read/list;
- a derived/rebuildable queue index;
- owner action record shape validation only;
- no owner action execution;
- no review UI/API;
- no backend routes or frontend UI;
- no apply-promotion;
- no memory/canon mutation;
- no runtime extraction.

The review queue is now storable, listable, and indexable, and owner action records can be shape-validated, but nothing exposes the queue to an owner yet. The next risk is accidental backend review routes, owner action execution, review UI scope creep, or apply-promotion without an explicit contract. Before implementing any review route, owner-action command, or frontend review screen, the app needs a parent that defines the read-only review queue API contract, the owner-action command API contract, the review UI planning boundary, and the no-canon/no-promotion safety rules. Queue presence and owner actions remain non-approval, and owner review remains mandatory before anything can become approved truth.

## Planning Questions This Parent Must Answer

- Whether backend review routes are needed before frontend review UI.
- What a read-only review queue API contract would expose (queue list/read, evidence/provenance/uncertainty, non-approval status) without becoming approval or canon truth.
- What an owner-action command API contract would accept and reject (allowed commands/states from `PHASE8-IMPL-012-T003`, fail-closed behavior, audit affirmations) without apply-promotion.
- How a review UI should display evidence/provenance/uncertainty and non-approval status without implying canon.
- How the owner action workflow stays separate from apply-promotion.
- How memory/canon mutation remains deferred.
- How generated prose/rewrite/continuation remains forbidden.
- How runtime extraction remains deferred.

## Dependencies

- Completed parent: `PHASE8-IMPL-012` - Writer Assistant Core review queue storage and owner-review workflow planning.
- Completed child: `PHASE8-IMPL-012-T007` - Roadmap/status closeout.
- Foundation from `PHASE8-IMPL-006` through `PHASE8-IMPL-012`.
- Existing modules and tests:
  - `backend/story_knowledge/review_queue_storage.py`
  - `backend/story_knowledge/candidate_review_gate.py`
  - `backend/story_knowledge/extraction_orchestrator.py`
  - `backend/story_knowledge/candidate_schema.py`
  - `backend/story_knowledge/candidate_record.py`
  - `backend/story_knowledge/candidate_storage.py`
  - `backend/story_knowledge/candidate_persistence.py`
  - `backend/story_knowledge/candidate_index.py`
  - `backend/story_knowledge/source_map.py`
  - `backend/story_knowledge/evidence.py`
  - `tests/test_writer_assistant_core_review_queue_storage_contract.py`
  - `tests/test_writer_assistant_core_candidate_review_gate_contract.py`
  - `tests/test_writer_assistant_core_extraction_orchestrator_contract.py`
  - candidate schema/record/storage/persistence/list/index contract and safety regression tests.

## Evidence Inputs

- `docs/roadmap/tasks/PHASE8-IMPL-012.md`
- `docs/roadmap/inventory/PHASE8-IMPL-012.md`
- `docs/roadmap/enrichment/PHASE8-IMPL-012.enrichment.json`
- `docs/roadmap/decisions/PHASE8-IMPL-012-review-queue-storage-contract-decision.md`
- `docs/roadmap/decisions/PHASE8-IMPL-012-owner-action-workflow-boundary-decision.md`
- `backend/story_knowledge/review_queue_storage.py`
- `backend/story_knowledge/candidate_review_gate.py`
- `backend/story_knowledge/extraction_orchestrator.py`
- `backend/story_knowledge/candidate_schema.py`
- `backend/story_knowledge/candidate_record.py`
- `backend/story_knowledge/candidate_storage.py`
- `backend/story_knowledge/candidate_persistence.py`
- `backend/story_knowledge/candidate_index.py`
- `backend/story_knowledge/source_map.py`
- `backend/story_knowledge/evidence.py`
- current roadmap truth files and validation records.

## Scope

Include:

- docs/status/planning publication in T001;
- read-only review queue API contract decision;
- owner-action command API contract decision;
- review UI planning boundary decision;
- review API/UI contract tests if authorized by prior children;
- review API/UI safety regression or conditional hardening decision;
- roadmap/status closeout.

## Exclusions

Explicitly excluded:

- implementation in T001;
- review UI/API implementation;
- backend review routes or API endpoints;
- frontend review UI;
- owner action execution;
- automatic candidate approval;
- approved/canon/promoted states;
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

1. `PHASE8-IMPL-013-T001` - Publish review UI/API planning and owner-action workflow contract parent. Status: complete.
2. `PHASE8-IMPL-013-T002` - Read-only review queue API contract decision. Status: ready/active.
3. `PHASE8-IMPL-013-T003` - Owner action command API contract decision. Status: planned.
4. `PHASE8-IMPL-013-T004` - Review UI planning boundary decision. Status: planned.
5. `PHASE8-IMPL-013-T005` - Review API/UI contract tests, if authorized. Status: planned.
6. `PHASE8-IMPL-013-T006` - Review API/UI safety regression or conditional hardening decision. Status: planned.
7. `PHASE8-IMPL-013-T007` - Roadmap/status closeout. Status: planned.

## Child Task Details

### `PHASE8-IMPL-013-T001` - Publish review UI/API planning and owner-action workflow contract parent

- Docs/status/planning only.
- Create parent task record, inventory, and enrichment JSON.
- Mark `PHASE8-IMPL-013` active.
- Mark T001 complete on success.
- Mark `PHASE8-IMPL-013-T002` ready/active.
- Keep `PHASE8-IMPL-013-T003` through `PHASE8-IMPL-013-T007` planned.
- No runtime code, tests, routes, UI, package changes, review UI/API, owner action execution, apply-promotion, memory/canon mutation, or project runtime files.

### `PHASE8-IMPL-013-T002` - Read-only review queue API contract decision

- Docs/decision only.
- Decide whether backend review routes are needed before frontend UI.
- Decide a read-only review queue API contract shape (queue list/read read models, evidence/provenance/uncertainty exposure, non-approval status) without implementing routes.
- Keep the queue API read-only and review-workflow-only; queue presence stays non-approval.
- No runtime code or tests.

### `PHASE8-IMPL-013-T003` - Owner action command API contract decision

- Docs/decision only.
- Decide an owner-action command API contract: accepted commands/states aligned with `PHASE8-IMPL-012-T003`, rejected commands/states, fail-closed behavior, and required audit affirmations (`no_promotion_performed`, `no_memory_canon_mutation`).
- Clarify owner action commands are not apply-promotion and owner action execution stays deferred.
- No runtime code, tests, owner action execution, or apply-promotion.

### `PHASE8-IMPL-013-T004` - Review UI planning boundary decision

- Docs/decision only.
- Decide the frontend review UI display/interaction boundary: evidence/provenance/uncertainty display, non-approval status, no-promotion warnings, and the no-prose boundary.
- Keep review UI implementation deferred.
- No runtime code, tests, or frontend implementation.

### `PHASE8-IMPL-013-T005` - Review API/UI contract tests, if authorized

- Tests-first only, expected-red, if authorized by T002/T003/T004.
- Define a future API/UI-boundary contract only after prior children authorize it.
- `tmp_path` only for any filesystem assertions.
- No route/UI implementation.
- No apply-promotion.
- No memory/canon mutation.

### `PHASE8-IMPL-013-T006` - Review API/UI safety regression or conditional hardening decision

- Validate boundaries or prepare handoff.
- No implementation unless explicitly authorized by prior tests and owner scope.
- Validate no review UI/API, no backend routes, no owner action execution, no apply-promotion, no memory/canon mutation, and no generated prose.

### `PHASE8-IMPL-013-T007` - Roadmap/status closeout

- Docs/status closeout only.
- Close parent, summarize decisions/tests if any, and recommend the next parent only.
- No runtime expansion.

## Inherited Artifacts

From `PHASE8-IMPL-011` and `PHASE8-IMPL-012`:

- `backend/story_knowledge/candidate_review_gate.py`
- `backend/story_knowledge/review_queue_storage.py`
- `backend/story_knowledge/extraction_orchestrator.py`
- `tests/test_writer_assistant_core_candidate_review_gate_contract.py`
- `tests/test_writer_assistant_core_review_queue_storage_contract.py`
- `tests/test_writer_assistant_core_extraction_orchestrator_contract.py`

## Missing/Deferred Layers

- read-only review queue API;
- owner action command API;
- review UI planning and implementation;
- backend route implementation;
- frontend review UI implementation;
- owner action execution;
- apply-promotion;
- memory/canon mutation.

## Acceptance Criteria

- `docs/roadmap/tasks/PHASE8-IMPL-013.md` exists.
- `docs/roadmap/inventory/PHASE8-IMPL-013.md` exists.
- `docs/roadmap/enrichment/PHASE8-IMPL-013.enrichment.json` exists.
- `PHASE8-IMPL-013` is active in roadmap/status docs.
- `PHASE8-IMPL-013-T001` is complete if successful.
- `PHASE8-IMPL-013-T002` is ready/active.
- `PHASE8-IMPL-013-T003` through `PHASE8-IMPL-013-T007` are planned.
- T001 records `PHASE8-IMPL-012` as complete through T007.
- T001 records the review queue as workflow support only and owner actions as non-promotion.
- T001 creates no backend code, tests, routes, UI, packages, project runtime files, training data, JSONL records, or datasets.
- T001 does not implement review UI/API.
- T001 does not implement backend routes.
- T001 does not implement frontend review UI.
- T001 does not implement owner action execution.
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
- The review queue is workflow support only; queue presence is non-approval and is not canon, memory, owner decisions, or promotion.
- Owner action is a review surface, not apply-promotion; owner action storage and execution are not memory/canon mutation.
- A candidate record is not canon; queue state is not approval.
- Evidence/provenance must be displayed in any future review surface.
- Confidence is uncertainty, not truth.
- Review UI/API, backend routes, and frontend review UI are not authorized unless a later owner-approved child explicitly defines and implements them.
- No real extraction runtime is authorized.
- No apply-promotion is authorized.
- No memory/canon mutation is authorized.
- No package/dependency changes are authorized.
- No generated prose, rewrite, or continuation behavior is authorized.

## Current Status

`PHASE8-IMPL-013` is active after T001. `PHASE8-IMPL-013-T001` is complete as docs/status/planning only and created the parent task record, inventory, and enrichment JSON, and updated roadmap/status docs. `PHASE8-IMPL-012` is recorded as complete through `PHASE8-IMPL-012-T007`. The review queue remains workflow support only; the `backend/story_knowledge/review_queue_storage.py` helper stores queue entries under project-local `writer_assistant/review_queue/` (exercised in tmp_path tests), validates owner action record shape only, and performs no owner action execution. Queue presence is non-approval, and owner review remains mandatory before anything can become approved truth. The child sequence is T001 parent publication (complete), T002 read-only review queue API contract decision (ready/active), T003 owner action command API contract decision (planned), T004 review UI planning boundary decision (planned), T005 review API/UI contract tests if authorized (planned), T006 review API/UI safety regression or conditional hardening decision (planned), and T007 roadmap/status closeout (planned). No review UI/API, backend routes, frontend UI, owner action execution, apply-promotion, memory/canon mutation, candidate/canon/memory mutation, raw artifact persistence, runtime extraction, real BookNLP/spaCy install/run/import, package/dependency changes, generated prose/rewrite/continuation, model calls, or training/JSONL/dataset work is authorized or was added in T001.

## Next Child

`PHASE8-IMPL-013-T002` - Read-only review queue API contract decision.
