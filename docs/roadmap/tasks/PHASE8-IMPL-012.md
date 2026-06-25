# PHASE8-IMPL-012

## ID

`PHASE8-IMPL-012`

## Title

Writer Assistant Core review queue storage and owner-review workflow planning

## Status

Active after `PHASE8-IMPL-012-T001`. `PHASE8-IMPL-012-T001` is complete as docs/status/planning only. `PHASE8-IMPL-012-T002` is ready/active. `PHASE8-IMPL-012-T003` through `PHASE8-IMPL-012-T007` are planned. `PHASE8-IMPL-012` starts after completed `PHASE8-IMPL-011` (complete through `PHASE8-IMPL-011-T007`).

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
2. `PHASE8-IMPL-012-T002` - Review queue storage contract decision. Status: ready/active.
3. `PHASE8-IMPL-012-T003` - Owner action workflow boundary decision. Status: planned.
4. `PHASE8-IMPL-012-T004` - Review queue storage contract tests. Status: planned.
5. `PHASE8-IMPL-012-T005` - Minimal review queue storage helper, if authorized. Status: planned.
6. `PHASE8-IMPL-012-T006` - Review queue safety regression or conditional hardening. Status: planned.
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

- Docs/decision only.
- Decide whether review queue entries should be stored separately or derived from candidate records.
- Decide storage root, identity rules, allowed fields, lifecycle/status rules, evidence/provenance requirements, and forbidden destinations.
- No runtime code or tests.

### `PHASE8-IMPL-012-T003` - Owner action workflow boundary decision

- Docs/decision only.
- Define owner action workflow states and commands as planning terms.
- Clarify owner actions are not apply-promotion.
- Clarify owner action storage is not memory/canon mutation.
- Clarify review UI/API remains deferred.
- No runtime code or tests.

### `PHASE8-IMPL-012-T004` - Review queue storage contract tests

- Tests-first only.
- Expected-red if a future queue storage helper does not exist.
- Define a future helper/API only after T002/T003 authorize it.
- `tmp_path` only for any filesystem assertions.
- No UI/routes.
- No apply-promotion.
- No memory/canon mutation.

### `PHASE8-IMPL-012-T005` - Minimal review queue storage helper, if authorized

- Optional pure helper implementation only if T002-T004 authorize it.
- Project-local queue storage only.
- Candidate-linked, candidate-only, review-workflow-only.
- No review UI/API.
- No owner action execution beyond safe metadata if explicitly tested.
- No apply-promotion.
- No memory/canon mutation.

### `PHASE8-IMPL-012-T006` - Review queue safety regression or conditional hardening

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

`PHASE8-IMPL-012` is active after T001. `PHASE8-IMPL-012-T001` is complete as docs/status/planning only and created the parent task record, inventory, and enrichment JSON, and updated roadmap/status docs. `PHASE8-IMPL-011` is recorded as complete through `PHASE8-IMPL-011-T007`. Review queue entries remain workflow support only and are built in memory only by the completed `PHASE8-IMPL-011` candidate review gate; they are not stored, listed, or loaded yet. `PHASE8-IMPL-012-T002` is ready/active as the review queue storage contract decision. No review queue storage, owner action workflow, review UI/API, backend review routes, frontend review UI, apply-promotion, memory/canon mutation, raw artifact persistence, runtime extraction, real BookNLP/spaCy install/run/import, package/dependency changes, generated prose, model calls, or training/JSONL/dataset work is authorized or was added in T001.

## Next Child

`PHASE8-IMPL-012-T002` - Review queue storage contract decision.
