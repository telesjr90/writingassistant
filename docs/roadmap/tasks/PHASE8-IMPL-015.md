# PHASE8-IMPL-015

## ID

`PHASE8-IMPL-015`

## Title

Review API route implementation and read-only frontend review queue surface

## Status

Active after `PHASE8-IMPL-015-T006` route/frontend read-only safety regression. `PHASE8-IMPL-015-T001` and `PHASE8-IMPL-015-T002` are complete. `PHASE8-IMPL-015-T003` is complete/PASS as tests-first expected-red contract coverage. `PHASE8-IMPL-015-T004` is complete/PASS and created `backend/routes/review_queue.py` with four GET-only read-only review queue routes over `backend.review_api`, plus minimal `backend/main.py` router inclusion; the route contract now passes. `PHASE8-IMPL-015-T005` is complete/PASS as the planning path because no usable frontend/component test harness exists without package changes at T005 start. `PHASE8-IMPL-015-T006` is complete/PASS as validation-only safety regression with no hardening required. `PHASE8-IMPL-015-T007` is ready/active for docs/status closeout. `PHASE8-IMPL-015` is read-only route/frontend surface work only unless a future child decision narrows the boundary further.

`PHASE8-IMPL-015-T001` is docs/status/planning only. It creates the parent task record, inventory, enrichment JSON, and roadmap/status updates. It does not implement routes, frontend review UI, frontend API helpers, owner action execution, apply-promotion, memory/canon mutation, raw artifact persistence, runtime extraction, model-assisted extraction, real BookNLP/spaCy install/run/import, NCP/Subtxt/dramatica-flow runtime integration, or generated prose.

## Goal

Publish the implementation parent that authorizes route wiring over the existing `backend.review_api` helper module (T003-T005 from `PHASE8-IMPL-014`) and a read-only frontend review queue surface, while keeping owner action execution, apply-promotion, memory/canon mutation, raw artifact persistence, runtime extraction, model-assisted extraction, real BookNLP/spaCy install/run/import, and NCP/Subtxt/dramatica-flow runtime integration out of this parent unless a later child explicitly authorizes a narrow display-only boundary.

This parent is tests-first-authorized implementation. `PHASE8-IMPL-015-T001` is docs/status/planning only. The parent as a whole is intended to:

- decide how the read-only review queue routes will be split between list/get/index/summary endpoints, how the route responses project the existing `backend.review_api` helper shapes, and whether owner-action command HTTP routes remain deferred (T002 docs/decision; complete);
- add backend route contract tests for the read-only review queue endpoints (T003);
- add minimal backend route registration over `backend.review_api` for read-only review queue endpoints only, with no owner action command route, no apply-promotion route, no memory/canon mutation route, no raw persistence route, and no FastAPI hookup for generated prose (T004);
- decide whether to add frontend API helper and read-only review queue surface contract tests, or whether the existing frontend test harness limits authorize a frontend implementation plan instead (T005; complete/PASS as planning path);
- run a route/frontend read-only safety regression or apply conditional hardening inside `backend/main.py` (or the documented future route file) plus any approved frontend surface, with no generated prose controls and no command controls (T006);
- close the parent as docs/status only (T007).

`PHASE8-IMPL-015-T001` does not implement routes, does not change tests, does not modify `backend/main.py` or `backend/app.py`, does not modify frontend files, does not implement owner action execution, does not mutate memory/canon, does not perform apply-promotion, does not persist raw artifacts, and does not implement runtime extraction.

## MVP Scope Correction

`PHASE8-IMPL-015` is MVP-required. Its exclusions are parent-local exclusions only. The following capabilities are required before MVP usability/testing, but only after `PHASE8-IMPL-015`:

- frontend owner-action execution for safe owner-review workflow actions only, with confirmation flows for promotion/canon-changing actions and no generated-prose controls (`PHASE8-IMPL-016`);
- explicit audited apply-promotion requiring validated candidate records, evidence, provenance, source locators, owner confirmation, and no automatic execution (`PHASE8-IMPL-017`);
- approved memory/canon mutation only through apply-promotion or another explicit owner-approved workflow (`PHASE8-IMPL-017`);
- project-local raw artifact persistence with manifests, raw refs, and safe path validation; raw artifacts remain non-canon, non-candidate, and non-training-data unless transformed through the candidate gate (`PHASE8-IMPL-018`);
- real BookNLP/spaCy install/run/import with explicit install/run/import tests and environment guards (`PHASE8-IMPL-019`);
- runtime extraction over owner-authored or owner-provided project text only, preserving source maps, evidence, provenance, raw refs, candidate-only outputs, and owner review gates (`PHASE8-IMPL-019`);
- model-assisted extraction that produces evidence-backed candidate drafts or diagnostic questions only, never prose, canon writes, or automatic promotion (`PHASE8-IMPL-020`);
- analysis-only NCP/Subtxt/dramatica-flow runtime integration, where NCP is structured context interchange, Subtxt is rubric/diagnostic guidance, and dramatica-flow is audited/allowlisted with prose/outline/chapter generation, rewrite, continuation, write/revise, export-as-prose, and prose-production paths permanently blocked (`PHASE8-IMPL-021`);
- end-to-end MVP usability validation (`PHASE8-IMPL-022`).

Generated prose, rewrite, continuation, imitation, polish, improvement, and expansion are permanently forbidden, not later backlog items. Fine-tuning is the only major listed capability that remains deferred after MVP.

## Why Now

`PHASE8-IMPL-014` is complete through `PHASE8-IMPL-014-T007`. It delivered the pure `backend.review_api` helper module only with all seven public APIs, read-only queue storage integration over `backend/story_knowledge/review_queue_storage.py` via optional keyword-only `project_dir`, hardened owner action command validation/response shaping, and a validation-only T006 safety regression that required no code change. `PHASE8-IMPL-013` previously delivered the read-only review queue API contract, the owner action command API contract, and the review UI planning boundary.

- `docs/roadmap/decisions/PHASE8-IMPL-013-read-only-review-queue-api-contract-decision.md` (read-only review queue API contract);
- `docs/roadmap/decisions/PHASE8-IMPL-013-owner-action-command-api-contract-decision.md` (owner action command API contract);
- `docs/roadmap/decisions/PHASE8-IMPL-013-review-ui-planning-boundary-decision.md` (review UI planning boundary);
- `docs/roadmap/decisions/PHASE8-IMPL-014-review-api-implementation-reconciliation-decision.md` (review API implementation reconciliation);
- the pure `backend/review_api.py` helper module from `PHASE8-IMPL-014-T003`/`T004`/`T005` with all seven public APIs and T004 read-only queue storage integration;
- the project-local review queue storage helper `backend/story_knowledge/review_queue_storage.py` from `PHASE8-IMPL-012-T005`;
- the candidate review gate helper `backend/story_knowledge/candidate_review_gate.py` from `PHASE8-IMPL-011-T005`;
- candidate schema/record/storage/persistence/list/index helpers from `PHASE8-IMPL-001` through `PHASE8-IMPL-004`;
- source/evidence/parser/adapter/orchestrator helpers from `PHASE8-IMPL-006` through `PHASE8-IMPL-010`;
- expected-red review API contract tests at `tests/test_writer_assistant_review_api_contract.py`;
- no FastAPI route registration, no frontend review UI, no frontend API helpers, no owner action command API routes, no owner action execution, no apply-promotion, no memory/canon mutation, no raw artifact persistence, no runtime extraction, no real BookNLP/spaCy install/run/import, no model-assisted extraction, and no NCP/Subtxt/dramatica-flow runtime integration.

The review queue storage helper is storable, listable, and indexable. The owner action record validator validates record shape only. The `backend.review_api` helper now reads through `review_queue_storage` when `project_dir` is supplied, but it is not wired into FastAPI routes, the frontend cannot call it, and the read-only helper shape is purely a planning/boundary contract today. The next risk is accidental route registration while keeping read-only, accidental owner action command HTTP route registration, accidental frontend command controls, accidental apply-promotion through a route, accidental memory/canon mutation through a route, accidental raw persistence through a route, accidental runtime extraction through a route, or accidental generated prose controls while satisfying read-only review queue display. Before adding routes and frontend surfaces, the app needs a parent that authorizes read-only route registration over `backend.review_api` only, splits read-only review queue endpoints from any future command endpoints, requires fail-closed validation, requires preservation of evidence/provenance/uncertainty, requires no mutation through the read-only surface, requires no command endpoints in this parent, requires no owner action execution, requires no apply-promotion, requires no memory/canon mutation, requires no raw persistence, requires no runtime extraction, requires no model integration, requires no generated prose controls, and preserves the no-promotion/no-canon/no-runtime-extraction/no-generated-prose boundaries.

## Dependencies

- Completed parent: `PHASE8-IMPL-014` - Writer Assistant Core review API implementation and tests-first route boundary.
- Completed child: `PHASE8-IMPL-014-T007` - Roadmap/status closeout.
- Foundation from `PHASE8-IMPL-006` through `PHASE8-IMPL-014`.
- Existing modules and tests:
  - `backend/review_api.py`
  - `tests/test_writer_assistant_review_api_contract.py`
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

## Evidence Inputs

- `docs/roadmap/tasks/PHASE8-IMPL-014.md`
- `docs/roadmap/inventory/PHASE8-IMPL-014.md`
- `docs/roadmap/enrichment/PHASE8-IMPL-014.enrichment.json`
- `docs/roadmap/decisions/PHASE8-IMPL-014-review-api-implementation-reconciliation-decision.md`
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
- `backend/review_api.py`
- `backend/story_knowledge/review_queue_storage.py`
- `tests/test_writer_assistant_review_api_contract.py`
- `tests/test_writer_assistant_core_review_queue_storage_contract.py`
- `backend/story_knowledge/candidate_review_gate.py`
- `tests/test_writer_assistant_core_candidate_review_gate_contract.py`
- `backend/story_knowledge/extraction_orchestrator.py`
- `tests/test_writer_assistant_core_extraction_orchestrator_contract.py`
- current roadmap truth files and validation records.

## Scope

Include:

- docs/status/planning publication in T001;
- route/read-only frontend implementation reconciliation decision (T002 docs/decision only) deciding exact route split, route response projection of the existing `backend.review_api` helper shapes, whether any new route file is added vs editing `backend/main.py`, whether owner-action command HTTP routes remain deferred to `PHASE8-IMPL-016`, and whether T005 produces frontend contract tests or a frontend implementation plan given the existing frontend test-harness constraints;
- backend route contract tests for read-only review queue endpoints (T003) as expected-red or near-red tests that pin the future read-only route surface;
- minimal backend route implementation over `backend.review_api` for read-only review queue endpoints only (T004) with no FastAPI hookup for owner action commands, no apply-promotion route, no memory/canon mutation route, no raw persistence route, no runtime extraction route, no model integration route, no generated prose route, and no frontend changes;
- frontend API helper/read-only review queue surface contract or implementation plan (T005), depending on existing frontend test harness constraints;
- route/frontend read-only safety regression or conditional hardening (T006) validating expected tests and regressions and patching only inside the approved route file and the approved frontend surface if needed;
- roadmap/status closeout (T007) as docs/status only.

## Exclusions

Explicitly excluded:

- implementation in T001;
- any FastAPI route that writes, mutates, or persists queue state, candidate state, owner action state, memory/canon state, raw artifact state, or generated prose state;
- any FastAPI route that runs runtime extraction, calls a model, installs or imports BookNLP/spaCy, or imports NCP/Subtxt/dramatica-flow runtime code;
- any FastAPI route that performs apply-promotion, executes owner actions, or auto-promotes candidates;
- owner action execution workflow;
- frontend owner-action command controls;
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
- training data, JSONL records, dataset manifests, model artifacts, or fine-tuning configs;
- mutating the existing `backend.review_api` helper module beyond narrow read-only safety fixes authorized in T006;
- mutating `backend/story_knowledge/review_queue_storage.py` beyond narrow safety fixes authorized in T006.

These exclusions mean "not in `PHASE8-IMPL-015`." They do not mean "not required for MVP." The excluded frontend owner-action execution, apply-promotion, approved memory/canon mutation, raw artifact persistence, real BookNLP/spaCy runtime, runtime extraction, model-assisted extraction, and analysis-only NCP/Subtxt/dramatica-flow runtime work must be scheduled as later MVP-required Phase 8 parents `PHASE8-IMPL-016` through `PHASE8-IMPL-022`.

## Child-Task Plan

1. `PHASE8-IMPL-015-T001` - Publish review API route implementation and read-only frontend review queue surface parent. Status: complete.
2. `PHASE8-IMPL-015-T002` - Route/read-only frontend implementation reconciliation decision. Status: complete.
3. `PHASE8-IMPL-015-T003` - Backend route contract tests for read-only review queue endpoints. Status: complete/PASS expected-red.
4. `PHASE8-IMPL-015-T004` - Minimal backend route implementation over `backend.review_api` for read-only review queue endpoints. Status: complete/PASS.
5. `PHASE8-IMPL-015-T005` - Frontend API helper/read-only review queue surface contract or implementation plan, depending on existing frontend test harness constraints. Status: complete/PASS.
6. `PHASE8-IMPL-015-T006` - Route/frontend read-only safety regression or conditional hardening. Status: complete/PASS.
7. `PHASE8-IMPL-015-T007` - Roadmap/status closeout. Status: ready/active.

## Child Task Details

### `PHASE8-IMPL-015-T001` - Publish review API route implementation and read-only frontend review queue surface parent

- Docs/status/planning only.
- Create parent task record, inventory, and enrichment JSON.
- Mark `PHASE8-IMPL-015` active.
- Mark T001 complete on success.
- Mark `PHASE8-IMPL-015-T002` ready/active.
- Keep `PHASE8-IMPL-015-T003` through `PHASE8-IMPL-015-T007` planned.
- No runtime code, tests, routes, UI, package changes, route registration, frontend API helpers, frontend review UI, owner action execution, apply-promotion, memory/canon mutation, raw artifact persistence, runtime extraction, or project runtime files.

### `PHASE8-IMPL-015-T002` - Route/read-only frontend implementation reconciliation decision

- Docs/decision only.
- Decision accepted at `docs/roadmap/decisions/PHASE8-IMPL-015-route-read-only-frontend-implementation-reconciliation-decision.md`.
- Decide exact read-only review queue route split (list/get/index/summary), whether new routes are added to `backend/main.py` or to a future `backend/routes/review_queue.py` file added in T004, the route response projection of the existing `backend.review_api` helper shapes, and whether any non-read route (such as a health check) is added. Result: four GET-only routes, no non-read route, no owner action command HTTP route.
- Decide whether owner action command HTTP routes remain deferred to `PHASE8-IMPL-016` and remain out of scope for this parent. Result: deferred to `PHASE8-IMPL-016`.
- Decide how the future read-only routes satisfy the future contract tests added by T003 without scope creep. Result: T003 target is `tests/test_writer_assistant_review_api_routes_contract.py`.
- Decide the read-only route behavior: read-only review queue routes over `backend.review_api` only, no state mutation, no apply-promotion, no memory/canon mutation, no raw persistence, no runtime extraction, no model calls, no UI changes beyond what T005 authorizes, no generated prose. Result: accepted.
- Decide whether T005 produces frontend API helper + read-only review queue surface contract tests or whether the existing frontend test harness constraints authorize a frontend implementation plan instead. Result: T005 should produce a frontend implementation plan unless an existing frontend/component test harness is available without package changes at T005 start.
- Decide boundary tags used by T003-T006: `review_route_implementation`, `route_boundary`, `frontend_read_only_surface`, `tests_first`, `no_apply_promotion`, `no_memory_canon_mutation`, `no_generated_prose`, `no_runtime_extraction`, `owner_review_required`. Add concise definitions to `docs/roadmap/roadmap_governance.md` only if validators require new tags.
- No implementation claimed.
- No tests claimed.
- No routes claimed.
- No UI claimed.
- No owner action execution claimed.
- Status: complete/PASS.

### `PHASE8-IMPL-015-T003` - Backend route contract tests for read-only review queue endpoints

- Tests-first or expected-red only.
- Target file: `tests/test_writer_assistant_review_api_routes_contract.py`.
- Add backend route contract tests for the future read-only review queue routes that wrap the existing `backend.review_api` helper module.
- Pin the future read-only route surface at the FastAPI test client level: route paths, HTTP methods, request/query parameter shapes, response shapes projected from `backend.review_api`, fail-closed behavior, evidence/provenance/uncertainty preservation, no-state-mutation guarantees, no-apply-promotion guarantees, no-memory/canon-mutation guarantees, no-raw-persistence guarantees, no-runtime-extraction guarantees, no-model-call guarantees, and no-generated-prose guarantees.
- Do not register routes in `backend/main.py`, do not add a new `backend/routes/review_queue.py` file, do not modify `backend/app.py` or `backend/main.py`, do not modify `backend/review_api.py` beyond narrow test-authorized read-only safety fixes.
- Do not modify tests outside the approved contract test file.
- Do not modify package/dependency files.
- Do not implement owner action command HTTP routes, frontend review UI, frontend API helpers, owner action execution, apply-promotion, memory/canon mutation, raw artifact persistence, runtime extraction, model integration, or generated prose.
- Status: complete/PASS expected-red. Added `tests/test_writer_assistant_review_api_routes_contract.py`; collection passes; the focused route contract run is expected-red because the read-only review queue routes are absent until T004. No routes, router registration, backend helper changes, frontend changes, package changes, runtime project files, source-cache changes, training files, model artifacts, owner action execution, apply-promotion, memory/canon mutation, raw artifact persistence, runtime extraction, model calls, or generated prose were added.

### `PHASE8-IMPL-015-T004` - Minimal backend route implementation over `backend.review_api` for read-only review queue endpoints

- Minimal route registration only.
- Status: complete/PASS. Created `backend/routes/review_queue.py` and included the router from `backend/main.py`.
- Register read-only review queue routes in `backend/routes/review_queue.py` and include them from `backend/main.py` only as needed to attach the router to the existing app. `backend/routes/review_queue.py` is authorized only for T004 and only for read-only routes that wrap the existing `backend.review_api` helper module.
- Routes must call `backend.review_api` helpers only (`list_review_queue_entries_readonly`, `get_review_queue_entry_readonly`, `get_review_queue_index_readonly`, `get_review_queue_summary_readonly`, plus `validate_review_queue_read_request`).
- Routes must produce the T002 read-only response shape including `schema_version`, `project_id`, `queue_entry_id` (single-entry routes), and the allowed-field set with `entries`/`entry`/`index`/`summary` payloads.
- Routes must preserve evidence, provenance, source document, source locator, raw output refs, uncertainty, normalization status, and `human_review_required`.
- Routes must fail closed for unsafe `project_id`, unsafe `queue_entry_id`, malformed queue entries, missing linked candidate records, invalid candidate linkage, unknown query fields, malformed JSON, invalid HTTP methods, and forbidden request/response fields.
- Routes must NOT mutate storage: no `write_review_queue_entry`, no candidate record mutation, no candidate JSON writes, no index writes, no project file writes, no raw artifact writes, no memory/canon writes, no training/JSONL writes.
- Routes must NOT register owner action command HTTP routes, apply-promotion routes, memory/canon mutation routes, raw persistence routes, runtime extraction routes, model integration routes, or generated prose routes.
- Routes must NOT modify `backend/review_api.py` beyond narrow T006 read-only safety fixes; routes must NOT modify `backend/story_knowledge/review_queue_storage.py`, `candidate_review_gate.py`, `extraction_orchestrator.py`, `booknlp_fixture_parser.py`, `raw_extraction_storage.py`, `booknlp_adapter_contract.py`, `source_map.py`, or `evidence.py` beyond narrow T006 read-only safety fixes.
- Routes must NOT modify frontend files, tests outside the approved contract test file, or package/dependency files.
- Routes must NOT implement owner action execution, apply-promotion, memory/canon mutation, raw artifact persistence, runtime extraction, or generated prose.

### `PHASE8-IMPL-015-T005` - Frontend API helper/read-only review queue surface contract or implementation plan

- Status: complete/PASS after `PHASE8-IMPL-015-T004`.
- T005 scope depends on the existing frontend test harness decision in T002.
- T005 should produce a frontend implementation plan unless an existing frontend/component test harness is available without package changes at T005 start.
- If frontend contract tests are available without package changes: add frontend API helper + read-only review queue surface contract tests only (tests-first or expected-red).
- If T005 follows the planning path: produce a frontend implementation plan at `docs/roadmap/decisions/PHASE8-IMPL-015-frontend-read-only-surface-implementation-decision.md` that documents the frontend API helper module name (`frontend/src/api/reviewQueue.js`), frontend read-only review queue surface component name (`frontend/src/components/ReviewQueueSurface.jsx`), props, allowlisted fields, evidence/provenance/uncertainty display, accessibility expectations, no-promotion/no-canon/no-generated-prose/no-runtime-extraction display rules, and `human_review_required` warning state.
- T005 followed the planning path because `frontend/package.json` has no runnable test harness (`test` exits with `Error: no test specified`) and no root `package.json` exists. It created `docs/roadmap/decisions/PHASE8-IMPL-015-frontend-read-only-surface-implementation-decision.md`.
- T005 did not implement production frontend files and did not add frontend contract tests.
- Do not register routes in `backend/main.py` or any new route file.
- Do not modify backend `backend.review_api.py`, `backend/story_knowledge/review_queue_storage.py`, or other backend story-knowledge modules beyond narrow T006 read-only safety fixes.
- Do not implement owner action command controls, frontend owner-action execution, apply-promotion, memory/canon mutation, raw artifact persistence, runtime extraction, model integration, or generated prose.
- Do not modify package/dependency files.

### `PHASE8-IMPL-015-T006` - Route/frontend read-only safety regression or conditional hardening

- Validation-only; conditional hardening inside `backend.review_api.py`, the approved route file, the approved frontend surface, or the approved frontend test file only if expected tests or regressions fail.
- Run `tests/test_writer_assistant_review_api_contract.py`, the future read-only route contract tests from T003, and any approved frontend contract tests from T005; confirm they are now green (no longer expected-red) and existing regressions remain green (`tests/test_writer_assistant_core_review_queue_storage_contract.py`, `tests/test_writer_assistant_core_candidate_review_gate_contract.py`, candidate regressions, orchestrator contract, source/evidence contract, parser/storage/adapter regressions, focused OMI/project regressions).
- Confirm the approved route file source does not contain `@app.post`, `@app.put`, `@app.patch`, `@app.delete`, `APIRouter().post`, `FastAPI(` (in the route file specifically; the existing FastAPI app definition is allowed), `write_to_memory`, `write_to_canon`, `apply_promotion`, `promote_candidate`, `approve_candidate`, `execute_owner_action`, `generated_prose`, `rewrite_source`, `continue_scene`, `run_booknlp`, `run_spacy`, `persist_raw_artifact`, `create_training_record`, or `export_jsonl`.
- Confirm no route registration appears in `backend/app.py` or any backend router file other than the approved route file.
- Confirm no frontend files outside the approved frontend surface file were changed and no command controls exist.
- Confirm BookNLP/spaCy availability guard still reports both false.
- Confirm `.external_sources/` remains ignored/protected from commit.
- Status: complete/PASS. T006 used the corrected scoped frontend planning-path non-implementation check: `frontend/src/api/reviewQueue.js` and `frontend/src/components/ReviewQueueSurface.jsx` do not exist, no frontend files are changed, and no T005-approved frontend surface exists; therefore no T005-created command/promotion/canon/runtime/model/prose controls exist. Route contract, existing review API contract, review queue storage/candidate gate regressions, broader candidate/orchestrator regressions, roadmap validation, approved route source scan, `backend/main.py` inclusion scan, BookNLP/spaCy runtime import guard, raw/model/runtime/prose source scan, git diff check, and source-cache safety all passed. No conditional hardening was required.
- If expected tests fail, narrow patch only inside `backend.review_api.py`, the approved route file, the approved frontend surface, or the approved frontend test file, and only to satisfy the contract tests without scope creep.
- No implementation outside `backend.review_api.py`, the approved route file, the approved frontend surface, or the approved frontend test file unless T002-T005 explicitly authorize it.

### `PHASE8-IMPL-015-T007` - Roadmap/status closeout

- Docs/status closeout only.
- Close `PHASE8-IMPL-015` as COMPLETE after T001-T006.
- Confirm tracked artifacts: `backend/review_api.py`, `tests/test_writer_assistant_review_api_contract.py`, the approved route file, the approved frontend surface, `backend/story_knowledge/review_queue_storage.py`, `tests/test_writer_assistant_core_review_queue_storage_contract.py`, `backend/story_knowledge/candidate_review_gate.py`, `tests/test_writer_assistant_core_candidate_review_gate_contract.py`, and any approved frontend contract test file.
- Re-validate: review API contract passes (no longer expected-red); new read-only route contract passes (no longer expected-red); existing regressions remain green; `.external_sources/` remains ignored and not staged.
- Recommend next parent only.

## Acceptance Criteria

- `docs/roadmap/tasks/PHASE8-IMPL-015.md` exists.
- `docs/roadmap/inventory/PHASE8-IMPL-015.md` exists.
- `docs/roadmap/enrichment/PHASE8-IMPL-015.enrichment.json` exists.
- `PHASE8-IMPL-015` is active in roadmap/status docs.
- `PHASE8-IMPL-015-T001` is complete.
- `PHASE8-IMPL-015-T002` is complete.
- `PHASE8-IMPL-015-T003` is complete/PASS expected-red.
- `PHASE8-IMPL-015-T004` is ready/active.
- T001 records `PHASE8-IMPL-014` as complete through T007.
- T001 records the `backend.review_api` helper module boundary from `PHASE8-IMPL-014` as preserved.
- T001 records the review queue as workflow support only and queue presence as non-approval.
- T001 records confidence as uncertainty/support strength, not truth.
- T001 records valid API response as not owner approval and owner action command validation as not owner action execution.
- T001 records frontend display as not promotion and apply-promotion as not implemented in this parent.
- T001 records approved memory/canon mutation, runtime extraction, raw artifact persistence, model-assisted extraction, real BookNLP/spaCy install/run/import, and NCP/Subtxt/dramatica-flow runtime integration as out of scope for this parent.
- T001 creates no backend code, tests, routes, UI, packages, project runtime files, training data, JSONL records, or datasets.
- T001 does not register routes.
- T001 does not implement frontend review UI.
- T001 does not implement frontend API helpers.
- T001 does not implement owner action execution.
- T001 does not implement apply-promotion.
- T001 does not mutate memory/canon.
- T001 preserves no-prose, no-canon-mutation, no-runtime-extraction, no-raw-persistence, no-model-integration, no-real-booknlp-spacy-runtime, no-NCP-Subtxt-dramatica-flow-runtime, and no-route/UI/command-execution boundaries.

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
- Confidence is uncertainty/support strength, not truth.
- Valid API response is not owner approval.
- Frontend display is not promotion.
- Read-only helpers in `backend.review_api` and any future read-only review queue route must never mutate queue entries, candidate records, indexes, project files, raw artifacts, memory, or canon.
- Owner action command validators in `backend.review_api` must never execute owner actions, must never write memory/canon, must never apply-promotion, and must never generate prose; no owner action command HTTP route is added in this parent.
- Routes added in this parent must never register routes in `backend/app.py` or in any non-approved route file, must never import runtime extraction, model integration, raw persistence, or generated prose modules, and must never call apply-promotion.
- Frontend surface added in this parent must remain read-only; it must never expose owner action command controls, apply-promotion controls, memory/canon write controls, runtime extraction controls, raw artifact persistence controls, model call controls, or generated prose controls.
- No real extraction runtime is authorized.
- No apply-promotion is authorized.
- No memory/canon mutation is authorized.
- No raw artifact persistence is authorized.
- No package/dependency changes are authorized.
- No generated prose, rewrite, or continuation behavior is authorized.

## Current Status

`PHASE8-IMPL-015` is active after `PHASE8-IMPL-015-T006` route/frontend read-only safety regression. `PHASE8-IMPL-015-T001` is complete as docs/status/planning only and created the parent task record, inventory, enrichment JSON, and roadmap/status updates. `PHASE8-IMPL-015-T002` is complete as docs/decision only and created `docs/roadmap/decisions/PHASE8-IMPL-015-route-read-only-frontend-implementation-reconciliation-decision.md`. `PHASE8-IMPL-015-T003` is complete/PASS as tests-first expected-red coverage and added `tests/test_writer_assistant_review_api_routes_contract.py`. `PHASE8-IMPL-015-T004` is complete/PASS and added the four GET-only read-only review queue routes in `backend/routes/review_queue.py` with minimal `backend/main.py` router inclusion. The route contract now passes. `PHASE8-IMPL-015-T005` is complete/PASS and created `docs/roadmap/decisions/PHASE8-IMPL-015-frontend-read-only-surface-implementation-decision.md` as the planning path because no usable frontend/component test harness exists without package changes. `PHASE8-IMPL-015-T006` is complete/PASS as validation-only safety regression with the corrected scoped frontend planning-path non-implementation check. `PHASE8-IMPL-015-T007` is ready/active. T006 added no backend route changes, production frontend files, frontend tests, package files, owner action command route, write route, owner action execution, apply-promotion, memory/canon mutation, raw artifact persistence, runtime extraction, model calls, generated prose behavior, runtime project files, training files, model artifacts, or source-cache changes.

## Next Child

`PHASE8-IMPL-015-T007` - Roadmap/status closeout.

## Recommended Next Parent

After `PHASE8-IMPL-015` completes (post `PHASE8-IMPL-015-T007`): `PHASE8-IMPL-016` - Frontend owner-action execution workflow and review command boundary (MVP-required; recommendation-only until separately published).
