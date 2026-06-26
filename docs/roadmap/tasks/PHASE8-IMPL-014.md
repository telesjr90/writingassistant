# PHASE8-IMPL-014

## ID

`PHASE8-IMPL-014`

## Title

Writer Assistant Core review API implementation and tests-first route boundary

## Status

Active after `PHASE8-IMPL-014-T005` runtime implementation. `PHASE8-IMPL-014-T001` is complete as docs/status/planning only and created the parent task record, inventory, and enrichment JSON, and updated roadmap/status docs. `PHASE8-IMPL-014-T002` is complete as docs/decision only and created `docs/roadmap/decisions/PHASE8-IMPL-014-review-api-implementation-reconciliation-decision.md`. `PHASE8-IMPL-014-T003` is complete as runtime implementation and created `backend/review_api.py` with all seven public APIs present (`validate_review_queue_read_request`, `validate_owner_action_command_request`, `build_owner_action_command_response`, `list_review_queue_entries_readonly`, `get_review_queue_entry_readonly`, `get_review_queue_index_readonly`, `get_review_queue_summary_readonly`). `PHASE8-IMPL-014-T004` is complete as runtime implementation and updated `backend/review_api.py` so read-only list/get/index/summary helpers accept optional keyword-only `project_dir` and use `review_queue_storage` read/list/build helpers when `project_dir` is supplied; list/get/index/summary helpers remain read-only and side-effect-free; write helpers are not called; owner action execution remains absent; all seven public APIs remain green. `PHASE8-IMPL-014-T005` is complete as runtime implementation and updated `backend/review_api.py` with hardened owner action command request validation (copied normalized output, stricter safe-id checks, required actor reference/id, required safety affirmations, command metadata type checks, and safer reason/status/client id handling) and hardened `build_owner_action_command_response` (validates copied owner action record and queue entry inputs, requires matching project/entry/candidate identifiers, preserves support references from the queue entry, and returns workflow-only response fields); T004 read-only queue helper behavior remains intact; command execution remains absent; write helpers are not called; all seven public APIs remain green. `PHASE8-IMPL-014-T006` is complete as safety regression validation. No `backend/review_api.py` code change was needed. T006 confirmed all seven public APIs remain callable; the review API contract tests pass; review queue storage and candidate review gate regressions pass; source-safety, no-write, workflow-boundary, public-surface, and import-boundary checks pass; no route, frontend, owner action execution, apply-promotion, memory/canon mutation, raw persistence, runtime extraction, model call, package/dependency, training/JSONL/dataset, or generated prose path was added. `PHASE8-IMPL-014-T007` is ready/active as docs/status closeout.

`PHASE8-IMPL-014-T001` is docs/status/planning only. It does not implement `backend.review_api`, does not register FastAPI routes in `backend/app.py`, does not implement frontend review UI or frontend API helpers, does not implement owner action execution, does not implement apply-promotion, does not mutate memory/canon, does not implement raw artifact persistence, does not implement runtime extraction, does not install BookNLP/spaCy, and does not run BookNLP/spaCy or any model. `PHASE8-IMPL-014-T001` records `PHASE8-IMPL-013` as complete through `PHASE8-IMPL-013-T007` and treats the expected-red review API contract tests at `tests/test_writer_assistant_review_api_contract.py` as the implementation handoff to satisfy.

This parent is tests-first-authorized implementation. `PHASE8-IMPL-014-T001` is still docs/status/planning only. Implementation micro-tasks (T003-T006) are explicitly authorized to introduce a pure helper module, request validators, response builders, and read-only review queue helpers over the existing `review_queue_storage.py` helper. Route registration in `backend/app.py`, frontend review UI, frontend API helpers, owner action execution, apply-promotion, memory/canon mutation, raw artifact persistence, runtime extraction, real BookNLP/spaCy install/run/import, model-assisted extraction, and NCP/Subtxt/dramatica-flow runtime integration are excluded from this parent, but they are MVP-required before the app can be treated as usable/testable. Fine-tuning remains deferred outside MVP.

## Goal

Publish the implementation parent that authorizes a minimal pure `backend.review_api` helper module to satisfy the expected-red review API contract tests added by `PHASE8-IMPL-013-T005`, while preserving the boundaries from `PHASE8-IMPL-013-T002` (read-only review queue API contract), `PHASE8-IMPL-013-T003` (owner action command API contract), and `PHASE8-IMPL-013-T004` (review UI planning boundary).

This parent is tests-first-authorized implementation. `PHASE8-IMPL-014-T001` is docs/status/planning only. The parent as a whole is intended to:

- decide how the future `backend.review_api` module is split between read-only helpers, owner action command validators, and response builders (T002 docs/decision);
- introduce a minimal pure `backend.review_api` helper module with request validators and response builders only (T003);
- introduce read-only review queue helpers (`list_review_queue_entries_readonly`, `get_review_queue_entry_readonly`, `get_review_queue_index_readonly`, `get_review_queue_summary_readonly`) over the existing `review_queue_storage.py` helper only, with no route registration and no state mutation (T004);
- introduce owner action command request validation (`validate_owner_action_command_request`) and response shape building (`build_owner_action_command_response`) only, with no owner action execution, no queue mutation, no candidate mutation, and no apply-promotion (T005);
- validate the implemented module against the expected-red contract tests and the no-route/no-UI/no-promotion boundaries, with conditional hardening only inside `backend.review_api` if needed (T006);
- close the parent as docs/status only (T007).

`PHASE8-IMPL-014-T001` does not implement the helpers, does not change tests, does not register routes, does not implement UI, does not implement owner action execution, does not mutate memory/canon, does not perform apply-promotion, does not persist raw artifacts, and does not implement runtime extraction.

## MVP Scope Correction

`PHASE8-IMPL-014` remains the current active parent, but it is not the final MVP gate. Its exclusions are parent-local exclusions only. The following capabilities are required before MVP usability/testing:

- real BookNLP/spaCy install/run/import with explicit install/run/import tests and environment guards;
- runtime extraction over owner-authored or owner-provided project text only, preserving source maps, evidence, provenance, raw refs, candidate-only outputs, and owner review gates;
- project-local raw artifact persistence with manifests, raw refs, and safe path validation; raw artifacts remain non-canon, non-candidate, and non-training-data unless transformed through the candidate gate;
- frontend owner-action execution for safe owner-review workflow actions only, with confirmation flows for promotion/canon-changing actions and no generated-prose controls;
- explicit audited apply-promotion requiring validated candidate records, evidence, provenance, source locators, owner confirmation, and no automatic execution;
- approved memory/canon mutation only through apply-promotion or another explicit owner-approved workflow;
- model-assisted extraction that produces evidence-backed candidate drafts or diagnostic questions only, never prose, canon writes, or automatic promotion;
- analysis-only NCP/Subtxt/dramatica-flow runtime integration, where NCP is structured context interchange, Subtxt is rubric/diagnostic guidance, and dramatica-flow is audited/allowlisted with prose/outline/chapter generation, rewrite, continuation, write/revise, export-as-prose, and prose-production paths permanently blocked.

Generated prose, rewrite, continuation, imitation, polish, improvement, and expansion are permanently forbidden, not later backlog items. Fine-tuning is the only major listed capability that remains deferred after MVP.

## Why Now

`PHASE8-IMPL-013` is complete through `PHASE8-IMPL-013-T007`. It delivered the review UI/API planning and owner-action workflow contract:

- `docs/roadmap/decisions/PHASE8-IMPL-013-read-only-review-queue-api-contract-decision.md` (read-only review queue API contract);
- `docs/roadmap/decisions/PHASE8-IMPL-013-owner-action-command-api-contract-decision.md` (owner action command API contract);
- `docs/roadmap/decisions/PHASE8-IMPL-013-review-ui-planning-boundary-decision.md` (review UI planning boundary);
- expected-red review API contract tests at `tests/test_writer_assistant_review_api_contract.py` for the future `backend.review_api` module and the future symbols `list_review_queue_entries_readonly`, `get_review_queue_entry_readonly`, `get_review_queue_index_readonly`, `get_review_queue_summary_readonly`, `validate_review_queue_read_request`, `validate_owner_action_command_request`, and `build_owner_action_command_response`;
- the project-local review queue storage helper `backend/story_knowledge/review_queue_storage.py` from `PHASE8-IMPL-012`;
- the candidate review gate helper `backend/story_knowledge/candidate_review_gate.py` from `PHASE8-IMPL-011`;
- candidate schema/record/storage/persistence/list/index helpers from `PHASE8-IMPL-001` through `PHASE8-IMPL-004`;
- source/evidence/parser/adapter/orchestrator helpers from `PHASE8-IMPL-006` through `PHASE8-IMPL-010`;
- no `backend.review_api` module, no backend review routes, no frontend review UI, no frontend API helpers, no owner action command API, no owner action execution, no apply-promotion, no memory/canon mutation, no raw artifact persistence, no runtime extraction, and no real BookNLP/spaCy install/run/import.

The review queue storage helper is storable, listable, and indexable, and owner action records can be shape-validated. The expected-red review API contract tests pin the future public API surface. The next risk is accidental backend route registration, owner action execution, frontend review UI scope creep, or apply-promotion while satisfying the contract tests. Before implementing `backend.review_api`, the app needs a parent that authorizes the pure helper module, splits read-only review queue helpers from owner action command validators, requires fail-closed validation, requires preservation of evidence/provenance/uncertainty, requires no mutation through the read-only surface, requires no owner action execution through the command validator, and preserves the no-route/no-UI/no-promotion/no-memory-canon/no-runtime-extraction/no-generated-prose boundaries.

## Dependencies

- Completed parent: `PHASE8-IMPL-013` - Writer Assistant Core review UI/API planning and owner-action workflow contract.
- Completed child: `PHASE8-IMPL-013-T007` - Roadmap/status closeout.
- Foundation from `PHASE8-IMPL-006` through `PHASE8-IMPL-013`.
- Existing modules and tests:
  - `backend/story_knowledge/review_queue_storage.py`
  - `tests/test_writer_assistant_core_review_queue_storage_contract.py`
  - `backend/story_knowledge/candidate_review_gate.py`
  - `tests/test_writer_assistant_core_candidate_review_gate_contract.py`
  - `backend/story_knowledge/extraction_orchestrator.py`
  - `tests/test_writer_assistant_core_extraction_orchestrator_contract.py`
  - `backend/story_knowledge/candidate_schema.py`
  - `backend/story_knowledge/candidate_record.py`
  - `backend/story_knowledge/candidate_storage.py`
  - `backend/story_knowledge/candidate_persistence.py`
  - `backend/story_knowledge/candidate_index.py`
  - `backend/story_knowledge/source_map.py`
  - `backend/story_knowledge/evidence.py`
  - `backend/story_knowledge/booknlp_adapter_contract.py`
  - `backend/story_knowledge/booknlp_fixture_parser.py`
  - `backend/story_knowledge/raw_extraction_storage.py`
  - `tests/test_writer_assistant_review_api_contract.py`

## Evidence Inputs

- `docs/roadmap/tasks/PHASE8-IMPL-013.md`
- `docs/roadmap/inventory/PHASE8-IMPL-013.md`
- `docs/roadmap/enrichment/PHASE8-IMPL-013.enrichment.json`
- `docs/roadmap/decisions/PHASE8-IMPL-013-read-only-review-queue-api-contract-decision.md`
- `docs/roadmap/decisions/PHASE8-IMPL-013-owner-action-command-api-contract-decision.md`
- `docs/roadmap/decisions/PHASE8-IMPL-013-review-ui-planning-boundary-decision.md`
- `docs/roadmap/tasks/PHASE8-IMPL-012.md`
- `docs/roadmap/inventory/PHASE8-IMPL-012.md`
- `docs/roadmap/enrichment/PHASE8-IMPL-012.enrichment.json`
- `docs/roadmap/decisions/PHASE8-IMPL-012-review-queue-storage-contract-decision.md`
- `docs/roadmap/decisions/PHASE8-IMPL-012-owner-action-workflow-boundary-decision.md`
- `backend/story_knowledge/review_queue_storage.py`
- `tests/test_writer_assistant_core_review_queue_storage_contract.py`
- `backend/story_knowledge/candidate_review_gate.py`
- `tests/test_writer_assistant_core_candidate_review_gate_contract.py`
- `backend/story_knowledge/extraction_orchestrator.py`
- `tests/test_writer_assistant_review_api_contract.py`
- current roadmap truth files and validation records.

## Scope

Include:

- docs/status/planning publication in T001;
- review API implementation reconciliation decision (T002 docs/decision only) deciding exact `backend.review_api` scope, module boundaries, whether FastAPI routes remain deferred, and how to satisfy expected-red tests without scope creep;
- minimal `backend.review_api` validators and response builders (T003) as a pure helper module with no FastAPI routes and no `backend/app.py` changes;
- read-only review queue API helper integration (T004) implementing `list_review_queue_entries_readonly`, `get_review_queue_entry_readonly`, `get_review_queue_index_readonly`, and `get_review_queue_summary_readonly` over `review_queue_storage` only, with no route registration and no state mutation;
- owner action command request/response validation integration (T005) implementing `validate_owner_action_command_request` and `build_owner_action_command_response` only, with no owner action execution, no queue mutation, no candidate mutation, and no apply-promotion;
- review API safety regression or conditional hardening (T006) validating expected tests and regressions and patching only inside `backend.review_api` if needed;
- roadmap/status closeout (T007) as docs/status only.

## Exclusions

Explicitly excluded:

- implementation in T001;
- FastAPI route registration in `backend/app.py`;
- any change to `backend/main.py` or any other backend router file;
- frontend review UI;
- frontend API helpers;
- any change to `frontend/src/api.js`, `frontend/src/App.jsx`, `frontend/src/Editor.jsx`, or `frontend/src/ProjectNav.jsx`;
- owner action execution;
- queue mutation through any future command API;
- candidate mutation through any future command API;
- apply-promotion;
- memory/canon mutation;
- raw artifact persistence;
- runtime extraction;
- real BookNLP install, import, run, or execution;
- real spaCy install, import, run, or execution;
- NCP/Subtxt/dramatica-flow runtime integration in this parent;
- model-assisted extraction in this parent;
- package or dependency changes;
- generated prose, rewriting, continuation, imitation, polish, improvement, or expansion;
- model calls, Ollama calls, Story Check calls, demos, or app server runs;
- training data, JSONL records, dataset manifests, model artifacts, or fine-tuning configs.

These exclusions mean "not in `PHASE8-IMPL-014`." They do not mean "not required for MVP." The excluded runtime extraction, raw persistence, real BookNLP/spaCy, model-assisted extraction, analysis-only NCP/Subtxt/dramatica-flow runtime, frontend owner-action execution, apply-promotion, and approved memory/canon mutation work must be scheduled as later MVP-required Phase 8 parents.

## Child-Task Plan

1. `PHASE8-IMPL-014-T001` - Publish review API implementation and tests-first route boundary parent. Status: complete.
2. `PHASE8-IMPL-014-T002` - Review API implementation reconciliation decision. Status: complete.
3. `PHASE8-IMPL-014-T003` - Minimal `backend.review_api` validators and response builders. Status: complete.
4. `PHASE8-IMPL-014-T004` - Read-only review queue API helper integration. Status: complete.
5. `PHASE8-IMPL-014-T005` - Owner action command request/response validation integration. Status: complete.
6. `PHASE8-IMPL-014-T006` - Review API safety regression or conditional hardening. Status: complete.
7. `PHASE8-IMPL-014-T007` - Roadmap/status closeout. Status: ready/active.

## Child Task Details

### `PHASE8-IMPL-014-T001` - Publish review API implementation and tests-first route boundary parent

- Docs/status/planning only.
- Create parent task record, inventory, and enrichment JSON.
- Mark `PHASE8-IMPL-014` active.
- Mark T001 complete on success.
- Mark `PHASE8-IMPL-014-T002` ready/active.
- Keep `PHASE8-IMPL-014-T003` through `PHASE8-IMPL-014-T007` planned.
- No runtime code, tests, routes, UI, package changes, `backend.review_api` implementation, frontend API helpers, owner action execution, apply-promotion, memory/canon mutation, raw artifact persistence, runtime extraction, or project runtime files.

### `PHASE8-IMPL-014-T002` - Review API implementation reconciliation decision

- Docs/decision only.
- Decide exact `backend.review_api` scope (single module vs submodules), module boundaries (validators, response builders, read-only helpers), and the order in which T003-T005 introduce public APIs.
- Decide whether FastAPI routes remain deferred until a later owner-approved parent.
- Decide how the future module satisfies the expected-red tests at `tests/test_writer_assistant_review_api_contract.py` without scope creep.
- Decide the read-only helper behavior: read-only review queue helpers over `review_queue_storage.py` only, no state mutation through the read-only surface, fail-closed validation, evidence/provenance/uncertainty preservation, no project file writes, no raw artifact writes, no routes, no UI.
- Decide the owner action command validator behavior: command request validation and response building only, no execution, no queue mutation, no candidate mutation, no apply-promotion, no memory/canon mutation, no raw artifact writes, no model calls, no generated prose, no routes, no UI.
- Decide boundary tags used by T003-T006: `review_api_implementation`, `route_boundary`, `tests_first`, `no_apply_promotion`, `no_memory_canon_mutation`, `no_generated_prose`, `no_runtime_extraction`, `owner_review_required`. Add concise definitions to `docs/roadmap/roadmap_governance.md` only if validators require new tags.
- No implementation claimed.
- No tests claimed.
- No routes claimed.
- No UI claimed.
- No owner action execution claimed.

### `PHASE8-IMPL-014-T003` - Minimal `backend.review_api` validators and response builders

- Pure helper module only.
- Create `backend/review_api.py` (top-level `backend.review_api`, importable as `from backend import review_api`).
- Implement pure request validators only: `validate_review_queue_read_request` and `validate_owner_action_command_request`.
- Implement pure response builders only: `build_owner_action_command_response`.
- Validators must be pure: only `dict`/non-dict input handling, only structural validation, no filesystem reads/writes, no model calls, no tool execution, no import of `backend/app.py` or any FastAPI module.
- Validators must fail closed for unknown/forbidden fields and unsafe IDs/path traversal.
- Validators must require `project_id` (read API) and the T003 owner action command request required fields.
- Validators must enforce T002 read-only response allowed-field set and T003 owner action command allowed command set.
- Response builder must emit the T003 owner action command response required fields with `no_promotion_performed = True` and `no_memory_canon_mutation = True` by default.
- Do not implement read operations in T003; T004 adds `list_review_queue_entries_readonly`, `get_review_queue_entry_readonly`, `get_review_queue_index_readonly`, and `get_review_queue_summary_readonly`.
- Do not register routes in `backend/app.py`.
- Do not modify `backend/app.py`, `backend/main.py`, or any backend router file.
- Do not modify `backend/story_knowledge/review_queue_storage.py`, `candidate_review_gate.py`, `extraction_orchestrator.py`, `booknlp_fixture_parser.py`, `raw_extraction_storage.py`, `booknlp_adapter_contract.py`, `source_map.py`, or `evidence.py`.
- Do not modify candidate schema/record/storage/persistence/list/index modules.
- Do not implement frontend UI, frontend API helpers, owner action execution, apply-promotion, memory/canon mutation, raw artifact persistence, runtime extraction, or generated prose.
- Do not modify tests.
- Do not modify `package.json`, `requirements.txt`, or any dependency file.

### `PHASE8-IMPL-014-T004` - Read-only review queue API helper integration

- Pure helper integration only.
- Add the four read-only review queue helpers in `backend/review_api.py`: `list_review_queue_entries_readonly`, `get_review_queue_entry_readonly`, `get_review_queue_index_readonly`, and `get_review_queue_summary_readonly`.
- Helpers must validate input through `validate_review_queue_read_request` from T003.
- Helpers must read through the existing `backend/story_knowledge/review_queue_storage.py` API only (`list_review_queue_entries`, `read_review_queue_entry`, `build_review_queue_index`, etc.).
- Helpers must produce the T002 read-only response shape, including `schema_version`, `project_id`, and the allowed-field set, with `entries` (list) or `entry` (single-entry) or `index` / `summary` payloads.
- Helpers must preserve evidence, provenance, source document, source locator, raw output refs, uncertainty, normalization status, and `human_review_required`.
- Helpers must fail closed for unsafe `project_id`, unsafe `queue_entry_id`, malformed queue entries, missing linked candidate records, invalid candidate linkage, and unknown query fields.
- Helpers must NOT mutate storage: no `write_review_queue_entry`, no candidate record mutation, no candidate JSON writes, no index writes, no project file writes, no raw artifact writes, no memory/canon writes.
- Helpers must NOT register routes in `backend/app.py`.
- Helpers must NOT modify `backend/app.py`, `backend/main.py`, or any backend router file.
- Helpers must NOT modify `review_queue_storage.py` unless a narrow safety fix is required; if a narrow safety fix is required, it must be limited to validation/path-safety rules and must not change the helper's public API contract.
- Do not modify frontend files, tests, or package/dependency files.
- Do not implement owner action execution, apply-promotion, memory/canon mutation, raw artifact persistence, runtime extraction, or generated prose.

### `PHASE8-IMPL-014-T005` - Owner action command request/response validation integration

- Pure validator/builder integration only.
- Refine `validate_owner_action_command_request` and `build_owner_action_command_response` to enforce the T003 owner action command request and response contracts.
- Validator must accept only the T003 allowed commands: `request_more_evidence`, `mark_needs_info`, `defer_review`, `reject_candidate`, `mark_duplicate`, `mark_superseded`, `archive_without_promotion`, `add_reviewer_note`, `clear_reviewer_note`, `edit_queue_metadata`, `prepare_for_promotion_review`, `mark_ready_for_separate_promotion_flow`.
- Validator must reject all T003 rejected commands and any unknown command.
- Validator must require `actor_ref` or `actor_id`, `reason_code`, `reviewer_note`, `client_request_id`, `human_review_required = True`, `no_promotion_requested = True`, `no_memory_canon_mutation_requested = True`, and the other T003 required request fields.
- Validator must reject any T003 forbidden request field.
- Validator must not mutate the caller input.
- Response builder must emit the T003 owner action command response required fields with `no_promotion_performed = True` and `no_memory_canon_mutation = True` and must not include any T003 forbidden response field.
- Validator must NOT execute the command: no queue writes, no candidate writes, no apply-promotion, no memory/canon writes, no project file writes, no raw artifact writes, no model calls, no tool execution, no generated prose.
- Validator must NOT register routes in `backend/app.py`.
- Do not modify frontend files, tests, or package/dependency files.
- Do not implement owner action execution, apply-promotion, memory/canon mutation, raw artifact persistence, runtime extraction, or generated prose.

### `PHASE8-IMPL-014-T006` - Review API safety regression or conditional hardening

- Validation-only; conditional hardening inside `backend.review_api` only if expected tests or regressions fail.
- Run `tests/test_writer_assistant_review_api_contract.py` and confirm the file is now green (no longer expected-red) and the existing regressions remain green (`tests/test_writer_assistant_core_review_queue_storage_contract.py`, `tests/test_writer_assistant_core_candidate_review_gate_contract.py`, candidate regressions, orchestrator contract, source/evidence contract, parser/storage/adapter regressions, focused OMI/project regressions).
- Confirm `backend.review_api` source does not contain `@app.get`, `@app.post`, `@app.put`, `@app.patch`, `@app.delete`, `APIRouter`, `FastAPI(`, `write_to_memory`, `write_to_canon`, `apply_promotion`, `promote_candidate`, `approve_candidate`, `generated_prose`, `rewrite_source`, `continue_scene`, `run_booknlp`, `run_spacy`, `persist_raw_artifact`, `create_training_record`, or `export_jsonl`.
- Confirm no route registration appears in `backend/app.py`, `backend/main.py`, or any backend router file.
- Confirm no frontend files changed and no review UI exists.
- Confirm BookNLP/spaCy availability guard still reports both false.
- Confirm `.external_sources/` remains ignored/protected from commit.
- If expected tests fail, narrow patch only inside `backend/review_api.py` and only to satisfy the contract tests without scope creep.
- No implementation outside `backend.review_api` unless T002/T003-T005 explicitly authorize it.

### `PHASE8-IMPL-014-T007` - Roadmap/status closeout

- Docs/status closeout only.
- Close `PHASE8-IMPL-014` as COMPLETE after T001-T006.
- Confirm tracked artifacts: `tests/test_writer_assistant_review_api_contract.py`, `backend/review_api.py`, `backend/story_knowledge/review_queue_storage.py`, `tests/test_writer_assistant_core_review_queue_storage_contract.py`, `backend/story_knowledge/candidate_review_gate.py`, `tests/test_writer_assistant_core_candidate_review_gate_contract.py`.
- Re-validate: review API contract passes (no longer expected-red); existing regressions remain green; `.external_sources/` remains ignored and not staged.
- Recommend next parent only.

## Acceptance Criteria

- `docs/roadmap/tasks/PHASE8-IMPL-014.md` exists.
- `docs/roadmap/inventory/PHASE8-IMPL-014.md` exists.
- `docs/roadmap/enrichment/PHASE8-IMPL-014.enrichment.json` exists.
- `PHASE8-IMPL-014` is active in roadmap/status docs.
- `PHASE8-IMPL-014-T001` is complete.
- `PHASE8-IMPL-014-T002` is ready/active.
- T001 records `PHASE8-IMPL-013` as complete through T007.
- T001 records the review queue as workflow support only and owner actions as non-promotion.
- T001 records the expected-red `backend.review_api` contract test handoff from `PHASE8-IMPL-013-T005`.
- T001 creates no backend code, tests, routes, UI, packages, project runtime files, training data, JSONL records, or datasets.
- T001 does not implement `backend.review_api`.
- T001 does not register FastAPI routes.
- T001 does not implement frontend review UI.
- T001 does not implement owner action execution.
- T001 does not implement apply-promotion.
- T001 does not mutate memory/canon.
- T001 preserves no-prose, no-canon-mutation, no-runtime-extraction, no-raw-persistence, and no-route/no-UI boundaries.

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
- Read-only helpers in `backend.review_api` must never mutate queue entries, candidate records, indexes, project files, raw artifacts, memory, or canon.
- Owner action command validators in `backend.review_api` must never execute owner actions, must never write memory/canon, must never apply-promotion, and must never generate prose.
- `backend.review_api` must never register FastAPI routes or import `backend/app.py`.
- `backend.review_api` must never be imported into frontend code.
- No real extraction runtime is authorized.
- No apply-promotion is authorized.
- No memory/canon mutation is authorized.
- No package/dependency changes are authorized.
- No generated prose, rewrite, or continuation behavior is authorized.

## Current Status

`PHASE8-IMPL-014` is active after `PHASE8-IMPL-014-T006`. `PHASE8-IMPL-014-T001` is complete as docs/status/planning only and created the parent task record, inventory, and enrichment JSON, and updated roadmap/status docs. `PHASE8-IMPL-014-T002` is complete as docs/decision only and created `docs/roadmap/decisions/PHASE8-IMPL-014-review-api-implementation-reconciliation-decision.md`. `PHASE8-IMPL-014-T003` is complete as runtime implementation and created `backend/review_api.py` with all seven public APIs present. `PHASE8-IMPL-014-T004` is complete as runtime implementation and updated `backend/review_api.py` so read-only list/get/index/summary helpers accept optional keyword-only `project_dir` and use `backend/story_knowledge/review_queue_storage.py` read/list/build helpers when `project_dir` is supplied; list/get/index/summary helpers remain read-only and side-effect-free; write helpers are not called; owner action execution remains absent; all seven public APIs remain green. `PHASE8-IMPL-014-T005` is complete as runtime implementation and updated `backend/review_api.py` with hardened owner action command request validation (copied normalized output, stricter safe-id checks, required actor reference/id, required safety affirmations, command metadata type checks, and safer reason/status/client id handling) and hardened `build_owner_action_command_response` (validates copied owner action record and queue entry inputs, requires matching project/entry/candidate identifiers, preserves support references from the queue entry, and returns workflow-only response fields); T004 read-only queue helper behavior remains intact; command execution remains absent; write helpers are not called; all seven public APIs remain green; the review API contract tests at `tests/test_writer_assistant_review_api_contract.py` pass (161 tests); review queue storage plus candidate review gate regressions pass (513 tests). `PHASE8-IMPL-014-T006` is complete as safety regression validation. No `backend/review_api.py` code change was needed. T006 confirmed all seven public APIs remain callable; the review API contract tests pass; review queue storage and candidate review gate regressions pass; source-safety, no-write, workflow-boundary, public-surface, and import-boundary checks pass; no route, frontend, owner action execution, apply-promotion, memory/canon mutation, raw persistence, runtime extraction, model call, package/dependency, training/JSONL/dataset, or generated prose path was added. `PHASE8-IMPL-014-T007` is ready/active as docs/status closeout. `PHASE8-IMPL-013` is complete through `PHASE8-IMPL-013-T007` and is recorded as the foundation. The review queue storage helper `backend/story_knowledge/review_queue_storage.py` from `PHASE8-IMPL-012-T005` is the only storage foundation for T004; the candidate review gate `backend/story_knowledge/candidate_review_gate.py` from `PHASE8-IMPL-011-T005` is the only candidate persistence foundation. Route registration, frontend review UI/API helpers, frontend owner-action execution, apply-promotion, approved memory/canon mutation, raw artifact persistence, runtime extraction, real BookNLP/spaCy install/run/import, model-assisted extraction, and analysis-only NCP/Subtxt/dramatica-flow runtime integration remain excluded from `PHASE8-IMPL-014` but are MVP-required in later Phase 8 parents. Package/dependency changes remain excluded from this parent and must be handled only by the future BookNLP/spaCy runtime parent. Generated prose, rewrite, continuation, imitation, polish, improvement, expansion, outline generation, chapter generation, write/revise flows, and prose-production paths remain permanently forbidden. No FastAPI route registration in `backend/app.py` or `backend/main.py`, no frontend review UI, no frontend API helpers, no owner action execution, no queue mutation through the read-only surface or through the command validator, no candidate mutation through the read-only surface or through the command validator, no apply-promotion, no memory/canon mutation, no raw artifact persistence, no runtime extraction, no real BookNLP/spaCy install/run/import, no package/dependency changes, no model calls, and no training/JSONL/dataset work was added in T003 beyond the pure `backend/review_api.py` helper module.

## Next Child

`PHASE8-IMPL-014-T007` - Roadmap/status closeout (ready/active; docs/status only).
