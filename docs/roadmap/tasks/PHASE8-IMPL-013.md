# PHASE8-IMPL-013

## ID

`PHASE8-IMPL-013`

## Title

Writer Assistant Core review UI/API planning and owner-action workflow contract

## Status

Active after `PHASE8-IMPL-013-T006`. `PHASE8-IMPL-013-T001` is complete as docs/status/planning only and created the parent task record, inventory, and enrichment JSON, and updated roadmap/status docs. `PHASE8-IMPL-013-T002` is complete as docs/decision only and accepted the read-only review queue API contract decision at `docs/roadmap/decisions/PHASE8-IMPL-013-read-only-review-queue-api-contract-decision.md`. `PHASE8-IMPL-013-T003` is complete as docs/decision only and accepted the owner action command API contract decision at `docs/roadmap/decisions/PHASE8-IMPL-013-owner-action-command-api-contract-decision.md`. `PHASE8-IMPL-013-T004` is complete as docs/decision only and accepted the review UI planning boundary decision at `docs/roadmap/decisions/PHASE8-IMPL-013-review-ui-planning-boundary-decision.md`. `PHASE8-IMPL-013-T005` is complete as tests-first expected-red review API contract coverage at `tests/test_writer_assistant_review_api_contract.py`. `PHASE8-IMPL-013-T006` is complete as validation-only review API/UI safety regression; all requested checks matched the expected-red handoff and existing regressions passed, so no hardening patch was needed. `PHASE8-IMPL-013-T007` is ready/active. `PHASE8-IMPL-013` started after completed `PHASE8-IMPL-012` (complete through `PHASE8-IMPL-012-T007`).

`PHASE8-IMPL-013-T002` accepted the read-only review queue API contract: define the read-only review queue API contract before any frontend review UI but implement no routes in T002; future review queue API operations are read-only (GET/read-model only) and review-workflow-only and never mutate queue entries, candidate records, memory, canon, project source files, raw artifacts, or indexes. The decision records the future read-only operation set (planning terms only), safe request/query parameters, the read-only response shape, queue/candidate exposure rules (queue presence is not approval, high confidence is not truth, response validity is not owner approval), mandatory evidence/provenance/uncertainty display, filtering/sorting/pagination as workflow convenience only, a fail-closed error/quarantine policy that never repairs by writing, owner action API separation (deferred to T003), apply-promotion/memory-canon/runtime-extraction/raw-artifact boundaries, the review UI relationship (deferred to T004), and security/path-safety rules. T002 implemented no routes, FastAPI endpoints, frontend API helpers, frontend review UI, owner action command API, owner action execution, apply-promotion, memory/canon mutation, raw artifact persistence, runtime extraction, package changes, model calls, tests, or training/JSONL/dataset work.

`PHASE8-IMPL-013-T003` accepted the owner action command API contract: define the future command contract before review UI planning but implement no routes in T003. The future command API is a review-workflow-only command boundary for metadata on candidate-linked queue entries. Accepted commands are `request_more_evidence`, `mark_needs_info`, `defer_review`, `reject_candidate`, `mark_duplicate`, `mark_superseded`, `archive_without_promotion`, `add_reviewer_note`, `clear_reviewer_note`, `edit_queue_metadata`, `prepare_for_promotion_review`, and `mark_ready_for_separate_promotion_flow`; the last two are pointers to a future separate promotion workflow only, not approval or promotion. Rejected commands include approval, promotion, apply-promotion, memory/canon writes, generated prose/rewrite/continuation, runtime extraction, BookNLP/spaCy runs, raw artifact persistence, training/JSONL export, and unknown commands. The decision records safe request/response shapes, actor/audit requirements, queue/candidate relationship boundaries, evidence/provenance preservation, fail-closed validation, error/quarantine policy, apply-promotion and memory/canon boundaries, runtime/raw/dependency boundaries, generated prose boundaries, and T004/T005/T006 handoffs. T003 implemented no backend routes, FastAPI endpoints, frontend helpers, frontend UI, owner action execution, queue mutation, candidate mutation, apply-promotion, memory/canon mutation, raw artifact persistence, runtime extraction, package changes, model calls, tests, or training/JSONL/dataset work.

`PHASE8-IMPL-013-T004` accepted the review UI planning boundary before any review UI implementation exists. The future review UI is an owner-facing review surface for candidate-linked queue entries that must display workflow state, evidence, provenance, source locators, uncertainty/support strength, insufficient-evidence and rejected-output states, and owner-action controls as planning terms only. The decision records future list/detail view display contracts, evidence/provenance/source locator display requirements, uncertainty/confidence language, insufficient-evidence/rejected-output requirements, read-only versus command interaction separation, accessibility/usability expectations, empty/error/quarantine state requirements, and mobile/desktop planning boundaries. It keeps frontend implementation, backend routes, frontend API helpers, owner action execution, apply-promotion, memory/canon mutation, runtime extraction, raw artifact persistence, generated prose/rewrite/continuation, tests, and package changes deferred. T005 is tests-first only if authorized.

`PHASE8-IMPL-013-T005` added tests-first expected-red API contract coverage only. The future backend/API module name recorded for implementation handoff is `backend.review_api`, with expected symbols `list_review_queue_entries_readonly`, `get_review_queue_entry_readonly`, `get_review_queue_index_readonly`, `get_review_queue_summary_readonly`, `validate_review_queue_read_request`, `validate_owner_action_command_request`, and `build_owner_action_command_response`. The target command `.venv-unsloth-clean/bin/python -m pytest tests/test_writer_assistant_review_api_contract.py -q` is expected-red with collection `ImportError: cannot import name 'review_api' from 'backend'`, limited to the missing future module. Frontend UI contract tests are deferred because no local frontend/component test harness exists and `frontend/package.json` has no usable test command or test dependencies; no package changes were authorized. T005 implemented no backend routes, FastAPI endpoints, frontend review UI, frontend API helpers, owner action execution, apply-promotion, memory/canon mutation, runtime extraction, raw artifact persistence, generated prose/rewrite/continuation, package changes, or training/JSONL/dataset work.

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
2. `PHASE8-IMPL-013-T002` - Read-only review queue API contract decision. Status: complete.
3. `PHASE8-IMPL-013-T003` - Owner action command API contract decision. Status: complete.
4. `PHASE8-IMPL-013-T004` - Review UI planning boundary decision. Status: complete.
5. `PHASE8-IMPL-013-T005` - Review API/UI contract tests, if authorized. Status: complete.
6. `PHASE8-IMPL-013-T006` - Review API/UI safety regression or conditional hardening decision. Status: complete.
7. `PHASE8-IMPL-013-T007` - Roadmap/status closeout. Status: ready/active.

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

- Docs/decision only. Complete.
- Decided to define the read-only review queue API contract before frontend UI and to implement no routes in T002.
- Decided a read-only review queue API contract shape (queue list/read read models, index/summary metadata, evidence/provenance/uncertainty exposure, non-approval status) without implementing routes.
- Kept the queue API read-only and review-workflow-only; queue presence stays non-approval and a valid response is not owner approval.
- Recorded safe request/query parameters, the read-only response shape, queue/candidate exposure rules, evidence/provenance display requirements, filtering/sorting/pagination boundary, fail-closed error/quarantine policy, owner action API separation, apply-promotion/memory-canon/runtime/raw boundaries, review UI relationship, and security/path safety.
- Decision artifact: `docs/roadmap/decisions/PHASE8-IMPL-013-read-only-review-queue-api-contract-decision.md`.
- No runtime code or tests.

### `PHASE8-IMPL-013-T003` - Owner action command API contract decision

- Docs/decision only. Complete.
- Decision artifact: `docs/roadmap/decisions/PHASE8-IMPL-013-owner-action-command-api-contract-decision.md`.
- Accepted the future owner action command API contract before review UI planning, while implementing no routes in T003.
- Recorded the accepted command set: `request_more_evidence`, `mark_needs_info`, `defer_review`, `reject_candidate`, `mark_duplicate`, `mark_superseded`, `archive_without_promotion`, `add_reviewer_note`, `clear_reviewer_note`, `edit_queue_metadata`, `prepare_for_promotion_review`, and `mark_ready_for_separate_promotion_flow`.
- Recorded rejected commands: approval, promotion, apply-promotion, memory/canon writes, generated prose/rewrite/continuation, runtime extraction, BookNLP/spaCy execution, raw artifact persistence, training/JSONL export, and unknown commands.
- Recorded safe request/response shape, actor/audit requirements, queue/candidate relationship boundaries, evidence/provenance requirements, fail-closed validation, error/quarantine policy, apply-promotion/memory-canon/runtime/raw/generated-prose boundaries, and T004/T005/T006 handoffs.
- Clarified owner action commands are not apply-promotion and owner action execution stays deferred.
- The owner action command API is the separate future write/command surface complementing the T002 read-only API, but no command API is implemented in T003.
- No runtime code, tests, routes, frontend UI, owner action execution, queue mutation, candidate mutation, or apply-promotion.

### `PHASE8-IMPL-013-T004` - Review UI planning boundary decision

- Docs/decision only. Complete.
- Decision artifact: `docs/roadmap/decisions/PHASE8-IMPL-013-review-ui-planning-boundary-decision.md`.
- Accepted review UI planning before implementation.
- Recorded future list/detail view display contracts for candidate-linked queue entries.
- Required evidence/provenance/source locator display, confidence as uncertainty/support strength, distinct insufficient-evidence and rejected-output states, visible no-promotion/no-canon warnings, and accessible empty/error/quarantine/mobile/desktop states.
- Kept owner action controls as future planning terms only and separated read-only viewing from command actions.
- Kept apply-promotion, memory/canon mutation, generated prose/rewrite/continuation, runtime extraction, raw artifact persistence, routes, frontend API helpers, frontend UI, tests, and package changes deferred.
- No runtime code, tests, or frontend implementation.

### `PHASE8-IMPL-013-T005` - Review API/UI contract tests, if authorized

- Tests-first only, expected-red, authorized by T002/T003/T004. Complete.
- Added `tests/test_writer_assistant_review_api_contract.py`.
- Future backend/API module recorded: `backend.review_api`.
- Future symbols recorded: `list_review_queue_entries_readonly`, `get_review_queue_entry_readonly`, `get_review_queue_index_readonly`, `get_review_queue_summary_readonly`, `validate_review_queue_read_request`, `validate_owner_action_command_request`, and `build_owner_action_command_response`.
- Encoded read-only request validation, read-only response shape, owner action command request validation, owner action command response shape, no-side-effect/forbidden-path checks, and source-level boundary checks for the future module.
- Expected-red target result: `.venv-unsloth-clean/bin/python -m pytest tests/test_writer_assistant_review_api_contract.py -q` fails during collection with `ImportError: cannot import name 'review_api' from 'backend'`, limited to the missing future module.
- Frontend UI contract test deferred: no local frontend/component test harness exists and `frontend/package.json` has no usable test runner or test dependencies; package changes were not authorized.
- `tmp_path` only for filesystem assertions.
- No route/UI implementation.
- No apply-promotion.
- No memory/canon mutation.
- No backend code, frontend code, frontend API helper, owner action execution, raw artifact persistence, runtime extraction, generated prose, package, training, JSONL, or dataset change.

### `PHASE8-IMPL-013-T006` - Review API/UI safety regression or conditional hardening decision

- Complete. Validation-only; no hardening patch was needed.
- Expected-red review API contract result: `.venv-unsloth-clean/bin/python -m pytest tests/test_writer_assistant_review_api_contract.py -q` fails during collection with `ImportError: cannot import name 'review_api' from 'backend'`, limited to the missing future `backend.review_api` module.
- Existing regressions passed: review queue storage contract (359), candidate review gate contract (154), candidate regressions (307), orchestrator contract (67), source/evidence contract (104), parser/storage/adapter regressions (64 + 185 + 148), and focused OMI/project regressions (109).
- Frontend UI contract tests remain deferred because no local frontend/component test harness exists and no package changes are authorized.
- Validated absent: backend review API module, backend review routes, FastAPI review endpoints, frontend review API helpers, frontend review UI, owner action command API implementation, owner action execution beyond owner action record validation, apply-promotion, memory/canon mutation, raw artifact persistence, runtime extraction, generated prose/rewrite/continuation, and package/dependency changes.
- `backend/story_knowledge/review_queue_storage.py` remains storage/read/list/index plus owner action record shape validation only.
- No backend code, frontend code, tests, project runtime files, package/dependency files, raw artifacts, training files, JSONL files, or datasets changed.
- Source-cache safety passed: `.external_sources/` is not staged and appears ignored only.
- T007 closeout handoff: ready/active.

### `PHASE8-IMPL-013-T007` - Roadmap/status closeout

- Ready/active after T006.
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
- `PHASE8-IMPL-013-T001` is complete.
- `PHASE8-IMPL-013-T002` is complete.
- `PHASE8-IMPL-013-T003` is complete.
- `PHASE8-IMPL-013-T004` is complete if successful.
- `PHASE8-IMPL-013-T005` is complete if successful.
- `PHASE8-IMPL-013-T006` is complete if successful.
- `PHASE8-IMPL-013-T007` is ready/active.
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

Do not run pytest in T004 because no tests or runtime code change.

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

`PHASE8-IMPL-013` is active after T006. `PHASE8-IMPL-013-T001` is complete as docs/status/planning only and created the parent task record, inventory, and enrichment JSON, and updated roadmap/status docs. `PHASE8-IMPL-013-T002` is complete as docs/decision only and accepted the read-only review queue API contract decision at `docs/roadmap/decisions/PHASE8-IMPL-013-read-only-review-queue-api-contract-decision.md`. `PHASE8-IMPL-013-T003` is complete as docs/decision only and accepted the owner action command API contract decision at `docs/roadmap/decisions/PHASE8-IMPL-013-owner-action-command-api-contract-decision.md`. `PHASE8-IMPL-013-T004` is complete as docs/decision only and accepted the review UI planning boundary decision at `docs/roadmap/decisions/PHASE8-IMPL-013-review-ui-planning-boundary-decision.md`. `PHASE8-IMPL-013-T005` is complete as tests-first expected-red review API contract coverage at `tests/test_writer_assistant_review_api_contract.py`; frontend UI contract tests remain deferred because no local frontend/component test harness exists without package changes. `PHASE8-IMPL-013-T006` is complete as validation-only safety regression: the expected-red review API contract remains limited to missing `backend.review_api`, existing backend/core regressions pass, route/UI/API absence checks pass, `.external_sources/` is not staged and ignored, and no hardening patch was needed. `PHASE8-IMPL-012` is recorded as complete through `PHASE8-IMPL-012-T007`. The review queue remains workflow support only; the `backend/story_knowledge/review_queue_storage.py` helper stores queue entries under project-local `writer_assistant/review_queue/` (exercised in tmp_path tests), validates owner action record shape only, and performs no owner action execution. Queue presence is non-approval, and owner review remains mandatory before anything can become approved truth. The child sequence is T001 parent publication (complete), T002 read-only review queue API contract decision (complete), T003 owner action command API contract decision (complete), T004 review UI planning boundary decision (complete), T005 review API/UI contract tests if authorized (complete), T006 review API/UI safety regression or conditional hardening decision (complete), and T007 roadmap/status closeout (ready/active). No review UI/API, backend routes, frontend UI, frontend API helpers, owner action execution, apply-promotion, memory/canon mutation, candidate/canon/memory mutation, raw artifact persistence, runtime extraction, real BookNLP/spaCy install/run/import, package/dependency changes, generated prose/rewrite/continuation, model calls, training/JSONL/dataset work, or raw artifact writes is authorized or was added in T001-T006.

## Next Child

`PHASE8-IMPL-013-T007` - Roadmap/status closeout.
