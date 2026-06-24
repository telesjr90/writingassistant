# PHASE8-IMPL-010

## ID

`PHASE8-IMPL-010`

## Title

Writer Assistant Core extraction orchestration planning and review-safe pipeline boundary

## Status

Active after `PHASE8-IMPL-010-T001` publication. `PHASE8-IMPL-010-T001` is complete on successful publication. `PHASE8-IMPL-010-T002` is complete as of 2026-06-23 with the review-safe extraction pipeline contract decision artifact at `docs/roadmap/decisions/PHASE8-IMPL-010-review-safe-extraction-pipeline-contract-decision.md`. `PHASE8-IMPL-010-T003` is complete as of 2026-06-24 with expected-red orchestration contract tests at `tests/test_writer_assistant_core_extraction_orchestrator_contract.py`. `PHASE8-IMPL-010-T004` is complete as of 2026-06-24 with the minimal review-safe orchestration helper at `backend/story_knowledge/extraction_orchestrator.py`. `PHASE8-IMPL-010-T005` is complete as of 2026-06-24 with the candidate review handoff and persistence boundary decision artifact at `docs/roadmap/decisions/PHASE8-IMPL-010-candidate-review-handoff-persistence-boundary-decision.md`. `PHASE8-IMPL-010-T006` is the next ready/active child.

## Goal

Publish the planning and contract parent that decides how the completed Writer Assistant Core extraction support pieces fit together into a review-safe extraction pipeline boundary.

This parent is orchestration planning/contract-first. It does not authorize real extraction tools, runtime extraction, raw artifact writes into real projects, automatic candidate persistence from parser output, backend routes, frontend UI, package changes, generated prose, apply-promotion, or memory/canon mutation.

## Why Now

`PHASE8-IMPL-006` through `PHASE8-IMPL-009` built the evidence/source-map/raw storage/parser/adapter foundation:

- source maps, source locators, evidence records, extraction run provenance, and raw output refs;
- mocked BookNLP adapter contract and normalization foundation;
- raw extraction artifact storage path and manifest helpers;
- pure in-memory BookNLP fixture parser helpers;
- raw artifact bundle builder integration;
- green parser/storage/adapter/source/evidence/candidate regressions.

The system can now parse synthetic BookNLP-like fixture strings into raw artifact bundles, but it has no orchestration contract for sequencing source maps, fixture/raw bundles, adapter validation and normalization, candidate draft support, and owner review.

## Dependencies

- Completed parent: `PHASE8-IMPL-009` - Writer Assistant Core BookNLP fixture parser helper implementation and raw artifact bundle integration.
- Completed child: `PHASE8-IMPL-009-T007` - Roadmap/status closeout.
- Foundation from `PHASE8-IMPL-006` through `PHASE8-IMPL-009`.
- Existing modules and tests:
  - `backend/story_knowledge/source_map.py`
  - `backend/story_knowledge/evidence.py`
  - `backend/story_knowledge/raw_extraction_storage.py`
  - `backend/story_knowledge/booknlp_fixture_parser.py`
  - `backend/story_knowledge/booknlp_adapter_contract.py`
  - `backend/story_knowledge/candidate_persistence.py`
  - `backend/story_knowledge/candidate_index.py`
  - `tests/test_writer_assistant_core_source_evidence_contract.py`
  - `tests/test_writer_assistant_core_raw_extraction_storage_contract.py`
  - `tests/test_writer_assistant_core_booknlp_fixture_parser_contract.py`
  - `tests/test_writer_assistant_core_booknlp_adapter_contract.py`
  - `tests/test_writer_assistant_core_candidate_persistence_contract.py`
  - `tests/test_writer_assistant_core_candidate_index_contract.py`

## Evidence Inputs

- `docs/roadmap/tasks/PHASE8-IMPL-006.md`
- `docs/roadmap/tasks/PHASE8-IMPL-007.md`
- `docs/roadmap/tasks/PHASE8-IMPL-008.md`
- `docs/roadmap/tasks/PHASE8-IMPL-009.md`
- `docs/roadmap/inventory/PHASE8-IMPL-009.md`
- `docs/roadmap/decisions/PHASE8-IMPL-009-parser-implementation-contract-reconciliation-decision.md`
- `docs/roadmap/enrichment/PHASE8-IMPL-009.enrichment.json`
- current roadmap truth files and validation records.

## Scope

Include:

- docs/status/planning publication in T001;
- review-safe orchestration pipeline contract decision;
- source map to fixture/raw bundle to adapter validation/normalization to candidate draft support to owner-review sequencing;
- tests-first orchestration contract if authorized by T002;
- optional minimal pure orchestration helper only if later children authorize it;
- candidate review handoff and persistence boundary decision;
- safety regression or hardening checks;
- roadmap/status closeout.

## Exclusions

Explicitly excluded:

- real BookNLP install, import, run, execution, or runtime output parsing;
- real spaCy install, import, run, or execution;
- parsing real runtime BookNLP files from disk;
- raw artifact write/read/list helpers unless a later child explicitly authorizes a pure tmp_path-only test helper;
- raw artifact writes into real project directories;
- extraction orchestrator that runs real tools;
- backend extraction routes or API endpoints;
- frontend extraction/review UI;
- package or dependency changes;
- automatic candidate JSON persistence from raw/parser output;
- memory/canon mutation;
- apply-promotion;
- generated prose, rewriting, continuation, imitation, polish, improvement, or expansion;
- model calls, Ollama calls, Story Check calls, demos, or app server runs;
- training data, JSONL records, dataset manifests, model artifacts, or fine-tuning configs.

## Child-Task Plan

1. `PHASE8-IMPL-010-T001` - Publish extraction orchestration planning parent. Status: complete.
2. `PHASE8-IMPL-010-T002` - Review-safe extraction pipeline contract decision. Status: complete.
3. `PHASE8-IMPL-010-T003` - Extraction orchestration contract tests. Status: complete with expected-red target coverage.
4. `PHASE8-IMPL-010-T004` - Minimal review-safe orchestration helper. Status: complete.
5. `PHASE8-IMPL-010-T005` - Candidate review handoff and persistence boundary decision. Status: complete.
6. `PHASE8-IMPL-010-T006` - Orchestration safety regression or conditional hardening. Status: ready/active.
7. `PHASE8-IMPL-010-T007` - Roadmap/status closeout. Status: planned.

## Child Task Details

### `PHASE8-IMPL-010-T001` - Publish extraction orchestration planning parent

- Docs/status/planning only.
- Create parent task record, inventory, and enrichment JSON.
- Mark `PHASE8-IMPL-010` active.
- Mark T001 complete on success.
- Mark `PHASE8-IMPL-010-T002` ready/active.
- No runtime code, tests, routes, UI, package changes, raw artifact helpers, extraction implementation, or project runtime files.

### `PHASE8-IMPL-010-T002` - Review-safe extraction pipeline contract decision

- Docs/decision only.
- Decide the intended orchestration flow: source map to fixture/raw bundle to adapter validation/normalization to candidate draft support to owner review.
- Decide what remains candidate-only and what is forbidden.
- Decide whether the first orchestrator contract should use synthetic fixture inputs only.
- No runtime code or tests.

### `PHASE8-IMPL-010-T002` - Review-safe extraction pipeline contract decision

- Docs/decision only.
- Status: complete as of 2026-06-23.
- Decision artifact: `docs/roadmap/decisions/PHASE8-IMPL-010-review-safe-extraction-pipeline-contract-decision.md`.
- Accept the review-safe extraction pipeline contract shape: source map to fixture/raw bundle to adapter validation/normalization to candidate draft support to owner review.
- Accept the first orchestration mode as synthetic fixture orchestration only.
- Accept the future pure orchestrator module name `backend/story_knowledge/extraction_orchestrator.py` and the public API set `validate_extraction_pipeline_request`, `build_fixture_extraction_pipeline_plan`, and `run_fixture_extraction_pipeline`.
- Accept the request dict fields and required safe policy flags (`human_review_required = true`, `persist_candidates = false`, `persist_raw_artifacts = false`, `allow_runtime_tools = false`, `allow_model_calls = false`, `allow_canon_write = false`, `allow_prose_generation = false`).
- Accept the output dict fields and required safe policy output values.
- Keep candidate drafts in-memory only; reject automatic candidate persistence, raw artifact writes, canon/memory mutation, model calls, generated prose, rewrite, and continuation.
- T003 is tests-first and expected-red if no orchestration module exists.

### `PHASE8-IMPL-010-T003` - Extraction orchestration contract tests

- Tests-first if authorized by T002.
- Status: complete as of 2026-06-24.
- Expected-red contract file: `tests/test_writer_assistant_core_extraction_orchestrator_contract.py`.
- Expected-red target result: `.venv-unsloth-clean/bin/python -m pytest tests/test_writer_assistant_core_extraction_orchestrator_contract.py -q` fails during collection with `ImportError: cannot import name 'extraction_orchestrator' from 'backend.story_knowledge'`.
- Failure is limited to the missing future module/symbol; no syntax errors, unrelated import failures, skips, or xfails are introduced.
- Future module remains `backend/story_knowledge/extraction_orchestrator.py`.
- Future public APIs remain `validate_extraction_pipeline_request`, `build_fixture_extraction_pipeline_plan`, and `run_fixture_extraction_pipeline`.
- Tests cover request validation, strict safe policy flags, fixture-only plan shape, in-memory run output shape, integration with source/evidence/raw/parser/adapter helpers, fail-closed/quarantine behavior, no side effects, no persistence/canon/prose behavior, and a future source-level boundary scan.
- Define a future pure orchestration module/API if authorized by T002.
- tmp_path/in-memory only.
- No real BookNLP/spaCy, routes, UI, or real project runtime writes.
- T003 does not implement the orchestrator module, helper functions, raw artifact write/read/list helpers, runtime extraction, routes, UI, package changes, candidate persistence, canon/memory mutation, or generated prose behavior.

### `PHASE8-IMPL-010-T004` - Minimal review-safe orchestration helper

- Optional implementation only if T002/T003 authorize.
- Status: complete as of 2026-06-24.
- Module: `backend/story_knowledge/extraction_orchestrator.py`.
- Implemented APIs: `validate_extraction_pipeline_request`, `build_fixture_extraction_pipeline_plan`, and `run_fixture_extraction_pipeline`.
- Orchestrator contract result: `.venv-unsloth-clean/bin/python -m pytest tests/test_writer_assistant_core_extraction_orchestrator_contract.py -q` passed with 67 tests.
- Pure standard-library helper over existing in-memory parser/storage/source/evidence/adapter helpers.
- No real tool runtime.
- No filesystem writes.
- No runtime extraction, real BookNLP/spaCy install/run/import, route/UI/package changes, raw artifact persistence, automatic candidate persistence, candidate/canon/memory mutation, or generated prose behavior.

### `PHASE8-IMPL-010-T005` - Candidate review handoff and persistence boundary decision

- Docs/decision only unless prior tasks authorize tests.
- Status: complete as of 2026-06-24.
- Decision artifact: `docs/roadmap/decisions/PHASE8-IMPL-010-candidate-review-handoff-persistence-boundary-decision.md`.
- Accepted candidate drafts as in-memory review support only.
- Recorded that candidate draft support is not candidate persistence.
- Deferred candidate persistence to a future owner-approved task using existing candidate schema/record validators, source locators, evidence, provenance, candidate-only status, project-local candidate storage, and existing candidate index helpers.
- Deferred candidate review UI/API to a future parent.
- Deferred owner decisions, apply-promotion, raw artifact persistence, and real runtime extraction.
- Preserved no candidate/canon/memory mutation, no raw writes, no routes/UI/package changes, no tests, and no implementation claims.
- T006 handoff: run safety regressions and conditionally harden `backend/story_knowledge/extraction_orchestrator.py` only if a validation gap exists.

### `PHASE8-IMPL-010-T006` - Orchestration safety regression or conditional hardening

- Status: ready/active after T005.
- Validate no runtime extraction, no filesystem leakage, no canon/memory mutation, no generated prose, and no route/UI/package changes.
- Conditional repair only if tests reveal gaps and the task explicitly authorizes repair.

### `PHASE8-IMPL-010-T007` - Roadmap/status closeout

- Close parent after authorized decisions/tests/helpers are complete.
- Summarize final decisions and any helper behavior.
- Recommend next parent only.
- No runtime expansion.

## Acceptance Criteria

- `docs/roadmap/tasks/PHASE8-IMPL-010.md` exists.
- `docs/roadmap/inventory/PHASE8-IMPL-010.md` exists.
- `docs/roadmap/enrichment/PHASE8-IMPL-010.enrichment.json` exists.
- `PHASE8-IMPL-010` is active in roadmap/status docs.
- `PHASE8-IMPL-010-T001` is complete.
- `PHASE8-IMPL-010-T002` is complete.
- `PHASE8-IMPL-010-T003` is complete with expected-red contract tests.
- `PHASE8-IMPL-010-T004` is complete with a pure in-memory orchestration helper.
- `PHASE8-IMPL-010-T005` is complete with a candidate review handoff and persistence boundary decision.
- `PHASE8-IMPL-010-T006` is ready/active.
- T001 records `PHASE8-IMPL-009` complete through T007.
- T001 records `PHASE8-IMPL-006` through `PHASE8-IMPL-009` artifacts as the foundation.
- T001 creates no backend code, tests, routes, UI, packages, project runtime files, training data, JSONL records, or datasets.
- T001 does not install or run BookNLP/spaCy.
- T001 does not implement extraction.
- T001 preserves no-prose and no-canon-mutation boundaries.

## Validation Expectations

- `python3 scripts/check_enrichment.py`
- `python3 scripts/validate_roadmap.py`
- non-LeanCTX whitespace check for changed docs
- narrow `/usr/bin/git diff --check -- ...`
- `.external_sources/` source-cache safety checks

Do not run pytest for T005 because no runtime code or tests should change.

## Safety/Product Boundaries

- Owner review remains mandatory before anything can become approved truth.
- Parser output, raw artifacts, and adapter output remain support/candidate-draft material only.
- Candidate JSON persistence from parser outputs is not authorized unless a later owner-approved child explicitly defines a review-safe boundary.
- No real extraction runtime is authorized.
- No memory/canon mutation is authorized.
- No generated prose, rewrite, or continuation behavior is authorized.

## Current Status

`PHASE8-IMPL-010` is active after T001 publication. `PHASE8-IMPL-010-T001` is complete. `PHASE8-IMPL-010-T002` is complete as of 2026-06-23 with the review-safe extraction pipeline contract decision. `PHASE8-IMPL-010-T003` is complete as of 2026-06-24 with expected-red extraction orchestration contract tests. `PHASE8-IMPL-010-T004` is complete as of 2026-06-24 with `backend/story_knowledge/extraction_orchestrator.py`, implementing `validate_extraction_pipeline_request`, `build_fixture_extraction_pipeline_plan`, and `run_fixture_extraction_pipeline`. The orchestrator contract passes with 67 tests. The helper is pure, standard-library, in-memory, fixture-only orchestration over existing source/evidence/raw/parser/adapter helpers and does not add runtime extraction, raw artifact persistence, automatic candidate persistence, routes, UI, package changes, generated prose behavior, or memory/canon mutation.

`PHASE8-IMPL-010-T005` is complete as of 2026-06-24 with `docs/roadmap/decisions/PHASE8-IMPL-010-candidate-review-handoff-persistence-boundary-decision.md`. T005 accepts candidate drafts as in-memory review support only and records that candidate persistence, review UI/API, owner decisions, apply-promotion, raw artifact persistence, and real runtime extraction remain deferred to future owner-approved tasks. Candidate drafts are not candidate records, canon, memory, owner decisions, or promotion. Any future persisted candidate must require source document refs, source locators, evidence records, provenance metadata, bounded confidence, human review, candidate-only status, and no canon/memory destination fields. T005 did not implement persistence, routes, UI, tests, runtime extraction, raw writes, apply-promotion, or memory/canon mutation.

## Next Child

`PHASE8-IMPL-010-T006` - Orchestration safety regression or conditional hardening.
