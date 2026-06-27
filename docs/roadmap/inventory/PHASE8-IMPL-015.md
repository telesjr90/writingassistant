# PHASE8-IMPL-015 Inventory

## 1. Task Identity

- Parent ID: `PHASE8-IMPL-015`
- Title: Review API route implementation and read-only frontend review queue surface
- Track: Writer Assistant Core
- Phase: Phase 8
- Status: complete/PASS after `PHASE8-IMPL-015-T007`.
- Depends on: completed `PHASE8-IMPL-014` (complete through `PHASE8-IMPL-014-T007`)
- Current child: none; parent closed complete after T007
- Child sequence: T001 complete; T002 complete/PASS; T003 complete/PASS; T004 complete/PASS; T005 complete/PASS; T006 complete/PASS; T007 complete/PASS
- Recommended next parent: `PHASE8-IMPL-016` - Frontend owner-action execution workflow and review command boundary (MVP-required; ready/active pending T001 publication)

## 2. Why This Parent Exists

`PHASE8-IMPL-014` produced the pure `backend.review_api` helper module with all seven public APIs, read-only queue storage integration over `backend/story_knowledge/review_queue_storage.py`, hardened owner action command validation/response shaping, and a validation-only T006 safety regression with no code change. `PHASE8-IMPL-013` previously delivered the read-only review queue API contract, the owner action command API contract, and the review UI planning boundary.

The `backend.review_api` helper module is route-free, frontend-free, and execution-free. The expected-red review API contract tests at `tests/test_writer_assistant_review_api_contract.py` pin the public API surface: `list_review_queue_entries_readonly`, `get_review_queue_entry_readonly`, `get_review_queue_index_readonly`, `get_review_queue_summary_readonly`, `validate_review_queue_read_request`, `validate_owner_action_command_request`, and `build_owner_action_command_response`.

The next risk is accidental FastAPI route registration, accidental owner action command HTTP route registration, accidental frontend command controls, accidental apply-promotion through a route, accidental memory/canon mutation through a route, accidental raw persistence through a route, accidental runtime extraction through a route, accidental model call through a route, or accidental generated prose controls while satisfying read-only review queue display. Before adding routes and frontend surfaces, the app needs a parent that authorizes read-only route registration over `backend.review_api` only, splits read-only review queue endpoints from any future command endpoints, requires fail-closed validation, requires preservation of evidence/provenance/uncertainty, requires no mutation through the read-only surface, requires no command endpoints in this parent, requires no owner action execution, requires no apply-promotion, requires no memory/canon mutation, requires no raw persistence, requires no runtime extraction, requires no model integration, requires no generated prose controls, and preserves the no-promotion/no-canon/no-runtime-extraction/no-generated-prose boundaries.

## 3. Existing Inputs

Foundation modules:

- `backend/review_api.py` (PHASE8-IMPL-014-T003/T004/T005; pure, standard-library-only, route-free, frontend-free helper module with all seven public APIs; read-only list/get/index/summary helpers accept optional keyword-only `project_dir` and use `backend/story_knowledge/review_queue_storage.py` read/list/build helpers when `project_dir` is supplied; write helpers are not called; owner action execution remains absent)
- `backend/story_knowledge/review_queue_storage.py` (PHASE8-IMPL-012-T005; pure, standard-library-only, project-local, candidate-linked, candidate-only, review-workflow-only queue storage helper; project-local queue write/read/list/index plus owner action record shape validation only)
- `backend/story_knowledge/candidate_review_gate.py` (PHASE8-IMPL-011-T005; pure, standard-library-only, deterministic, candidate-only/review-pending persistence gate)
- `backend/story_knowledge/extraction_orchestrator.py` (PHASE8-IMPL-010-T004; pure, in-memory, fixture-only orchestrator)
- `backend/story_knowledge/candidate_schema.py` (PHASE8-IMPL-001-T006; constants-only schema metadata)
- `backend/story_knowledge/candidate_record.py` (PHASE8-IMPL-002-T004; pure validation helpers)
- `backend/story_knowledge/candidate_storage.py` (PHASE8-IMPL-002-T006; pure path helpers)
- `backend/story_knowledge/candidate_persistence.py` (PHASE8-IMPL-003-T004/T006; candidate-only JSON write/read/list)
- `backend/story_knowledge/candidate_index.py` (PHASE8-IMPL-004-T004; derived candidate index build/write/read)
- `backend/story_knowledge/source_map.py` (PHASE8-IMPL-006-T004; source document, source segment, source map, source locator validation)
- `backend/story_knowledge/evidence.py` (PHASE8-IMPL-006-T004; evidence record validation)
- `backend/story_knowledge/booknlp_adapter_contract.py` (PHASE8-IMPL-007-T004; pure mocked BookNLP adapter contract)
- `backend/story_knowledge/booknlp_fixture_parser.py` (PHASE8-IMPL-009-T003-T005; pure in-memory TSV/JSON/Bundle parser)
- `backend/story_knowledge/raw_extraction_storage.py` (PHASE8-IMPL-008-T004; pure path and manifest validation helpers)

Contract and regression tests:

- `tests/test_writer_assistant_review_api_contract.py` (PHASE8-IMPL-013-T005; expected-red for future `backend.review_api`; now green per PHASE8-IMPL-014)
- `tests/test_writer_assistant_core_review_queue_storage_contract.py`
- `tests/test_writer_assistant_core_candidate_review_gate_contract.py`
- `tests/test_writer_assistant_core_extraction_orchestrator_contract.py`
- `tests/test_writer_assistant_core_candidate_schema_contract.py`
- `tests/test_writer_assistant_core_candidate_record_contract.py`
- `tests/test_writer_assistant_core_candidate_storage_contract.py`
- `tests/test_writer_assistant_core_candidate_persistence_contract.py`
- `tests/test_writer_assistant_core_candidate_list_contract.py`
- `tests/test_writer_assistant_core_candidate_index_contract.py`
- `tests/test_writer_assistant_core_candidate_index_safety_regression.py`
- `tests/test_writer_assistant_core_source_evidence_contract.py`
- `tests/test_writer_assistant_core_booknlp_adapter_contract.py`
- `tests/test_writer_assistant_core_booknlp_fixture_parser_contract.py`
- `tests/test_writer_assistant_core_raw_extraction_storage_contract.py`

Roadmap foundation:

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

## 4. Inherited Artifacts

From `PHASE8-IMPL-011`, `PHASE8-IMPL-012`, `PHASE8-IMPL-013`, and `PHASE8-IMPL-014`:

- `backend/review_api.py` (pure helper module only; all seven public APIs)
- `backend/story_knowledge/review_queue_storage.py`
- `backend/story_knowledge/candidate_review_gate.py`
- `backend/story_knowledge/extraction_orchestrator.py`
- `tests/test_writer_assistant_review_api_contract.py`
- `tests/test_writer_assistant_core_review_queue_storage_contract.py`
- `tests/test_writer_assistant_core_candidate_review_gate_contract.py`
- `tests/test_writer_assistant_core_extraction_orchestrator_contract.py`
- candidate review gate / review queue storage / orchestrator / review API contract tests

## 5. Missing/Deferred Layers

Implemented in this parent (planned scope):

- backend read-only review queue routes wrapping `backend.review_api` helpers only (complete/PASS in T004);
- backend route file `backend/routes/review_queue.py` authorized by T002 for T004 only and only for read-only review queue GET routes;
- optional frontend API helper module and optional read-only review queue surface component, or a frontend implementation plan if T005 confirms frontend tests/implementation would require package or harness changes;
- read-only route contract tests at the FastAPI test client level in `tests/test_writer_assistant_review_api_routes_contract.py`;
- optional frontend contract tests only if T005 confirms an existing frontend/component test harness is available without package changes.

Still missing/deferred after this parent:

- FastAPI route registration for owner action command HTTP endpoints;
- frontend owner action command controls;
- frontend owner-action execution workflow;
- owner action execution workflow;
- apply-promotion;
- memory/canon mutation;
- raw artifact persistence;
- real BookNLP/spaCy runtime;
- runtime extraction;
- byte-to-character source matching;
- NCP/Subtxt/dramatica-flow implementation;
- model-assisted extraction;
- training/JSONL/dataset work.

## 6. Implementation Target

- Read-only review queue routes registered in `backend/routes/review_queue.py`, with minimal `backend/main.py` inclusion only as needed, wrapping `backend.review_api` helpers only. T004 completed this target with four GET-only routes.
- Read-only route response projection of the existing `backend.review_api` helper shapes only; no new helper shapes in `backend.review_api` unless T006 read-only safety fix is required.
- Optional frontend API helper module `frontend/src/api/reviewQueue.js` and read-only review queue surface component `frontend/src/components/ReviewQueueSurface.jsx`, or a frontend implementation plan if T005 follows the planning path.
- T005 followed the planning path and created `docs/roadmap/decisions/PHASE8-IMPL-015-frontend-read-only-surface-implementation-decision.md` because no usable frontend/component test harness exists without package changes. No production frontend files or frontend tests were added.
- No owner action command HTTP route, no apply-promotion route, no memory/canon mutation route, no raw persistence route, no runtime extraction route, no model integration route, no generated prose route.
- No frontend owner action command controls, no apply-promotion controls, no memory/canon write controls, no runtime extraction controls, no raw artifact persistence controls, no model call controls, no generated prose controls.

## 7. Scope

- docs/status/planning publication in T001;
- route/read-only frontend implementation reconciliation decision (T002 docs/decision only);
- backend route contract tests for read-only review queue endpoints (T003 tests-first or expected-red);
- minimal backend route implementation over `backend.review_api` for read-only review queue endpoints only (T004);
- frontend API helper/read-only review queue surface contract or implementation plan (T005);
- route/frontend read-only safety regression or conditional hardening (T006);
- roadmap/status closeout (T007).

## 8. Non-Scope

Explicitly excluded for the entire parent:

- any FastAPI route that writes, mutates, or persists queue state, candidate state, owner action state, memory/canon state, raw artifact state, or generated prose state;
- any FastAPI route that runs runtime extraction, calls a model, installs or imports BookNLP/spaCy, or imports NCP/Subtxt/dramatica-flow runtime code;
- any FastAPI route that performs apply-promotion, executes owner actions, or auto-promotes candidates;
- owner action command HTTP routes (deferred to `PHASE8-IMPL-016`);
- frontend owner-action command controls;
- apply-promotion;
- memory/canon mutation;
- raw artifact persistence;
- runtime extraction;
- real BookNLP install, import, run, or execution;
- real spaCy install, import, run, or execution;
- package or dependency changes;
- generated prose, rewriting, continuation, imitation, polish, improvement, or expansion;
- model calls, Ollama calls, Story Check calls, demos, or app server runs;
- training data, JSONL records, dataset manifests, model artifacts, or fine-tuning configs;
- mutating the existing `backend.review_api` helper module beyond narrow read-only safety fixes authorized in T006;
- mutating `backend/story_knowledge/review_queue_storage.py`, `candidate_review_gate.py`, `extraction_orchestrator.py`, `booknlp_fixture_parser.py`, `raw_extraction_storage.py`, `booknlp_adapter_contract.py`, `source_map.py`, or `evidence.py` beyond narrow read-only safety fixes authorized in T006;
- mutating frontend files outside the approved frontend surface file (if T005 authorizes implementation);
- mutating tests outside the approved read-only route contract test file and the approved frontend contract test file (if T005 authorizes frontend contract tests).

## 9. Safety Boundaries

- The review queue is workflow support only.
- Queue presence is non-approval.
- Owner action is not promotion.
- Owner action command validation is not owner action execution.
- A candidate record is not canon.
- Queue state is not approval.
- Evidence/provenance must be displayed in any future review surface.
- Confidence is uncertainty/support strength, not truth.
- Valid API response is not owner approval.
- Frontend display is not promotion.
- Read-only helpers must never mutate queue entries, candidate records, indexes, project files, raw artifacts, memory, or canon.
- Owner action command validators must never execute owner actions, must never write memory/canon, must never apply-promotion, and must never generate prose.
- Read-only review queue routes must never mutate storage, never call write helpers, never call apply-promotion, never write memory/canon, never persist raw artifacts, never run runtime extraction, never call a model, and never generate prose.
- `backend.review_api` must never register FastAPI routes or import `backend/app.py` or `backend/main.py`.
- Read-only routes added in this parent must register only in `backend/main.py` (or in the T002-approved route file).
- Frontend read-only review queue surface must remain read-only; it must never expose owner action command controls, apply-promotion controls, memory/canon write controls, runtime extraction controls, raw artifact persistence controls, model call controls, or generated prose controls.

## 10. Risks

- `backend/main.py` (or new `backend/routes/review_queue.py`) registers owner action command HTTP routes instead of read-only routes (route scope creep);
- `backend/main.py` (or new route file) mutates storage accidentally through the read-only surface;
- `backend/main.py` (or new route file) calls `validate_owner_action_command_request` or `build_owner_action_command_response` as if they executed owner actions (hidden execution);
- `backend/main.py` (or new route file) calls apply-promotion or mutates memory/canon through a route;
- frontend read-only surface exposes owner action command controls, apply-promotion controls, memory/canon write controls, runtime extraction controls, raw artifact persistence controls, model call controls, or generated prose controls (UI scope creep);
- frontend API helper mutates storage or calls apply-promotion (helper scope creep);
- evidence/provenance omitted from the read-only route response or the frontend surface;
- confidence presented as truth instead of uncertainty/support strength;
- new route file is added without T002 authorization (file scope creep);
- mutating `backend.review_api.py` beyond narrow read-only safety fixes (helper scope creep);
- mutating `backend/story_knowledge/review_queue_storage.py` beyond narrow read-only safety fixes (storage scope creep);
- generated prose leakage into reviewer notes, response shapes, or route responses;
- runtime extraction or raw artifact persistence creep through the new route file or frontend helper;
- BookNLP/spaCy install/run creep through the new route file or frontend helper;
- NCP/Subtxt/dramatica-flow runtime creep through the new route file or frontend helper;
- package/dependency changes leak into implementation micro-tasks;
- mutating tests outside the approved contract test files (test scope creep);
- mutating frontend files outside the approved frontend surface file (frontend scope creep).

## 11. T001 Precondition Findings

## 11. T003 Contract Test Handoff

- `PHASE8-IMPL-015-T003` added `tests/test_writer_assistant_review_api_routes_contract.py` as tests-first expected-red backend route contract coverage.
- The pinned route surface is exactly four GET-only paths: `GET /api/projects/{project_id}/review-queue`, `GET /api/projects/{project_id}/review-queue/{queue_entry_id}`, `GET /api/projects/{project_id}/review-queue/index`, and `GET /api/projects/{project_id}/review-queue/summary`.
- The contract covers safe and unsafe `project_id` handling, safe and unsafe `queue_entry_id` handling, GET-only behavior, unknown filters/sorts/query fields, forbidden GET request bodies, missing queue/index responses, malformed queue entry fail-closed behavior, response shape preservation, and route source safety checks once `backend/routes/review_queue.py` exists.
- Response-shape coverage preserves `schema_version`, `project_id`, `queue_entry_id`, `entries`/`entry`/index-compatible `entries`/`summary`, candidate linkage, evidence, provenance, source document, source locator, raw refs as support-only metadata, confidence as uncertainty/support strength, normalization status, `human_review_required`, and no-promotion/no-memory-canon boundary metadata.
- The tests assert no write/mutation behavior, no owner action execution, no apply-promotion, no memory/canon mutation, no raw artifact persistence, no runtime extraction, no model calls, and no generated prose.
- The focused contract run is expected-red only because the read-only routes are absent until T004; collection passes and existing review API/review queue/candidate gate regressions pass.
- T003 did not create `backend/routes/review_queue.py`, did not edit `backend/main.py`, did not edit `backend/app.py`, did not edit `backend/review_api.py`, did not edit frontend/package/runtime/training/model/source-cache files, and did not stage, commit, or push.

## 12. T001 Precondition Findings

- Local roadmap files show `PHASE8-IMPL-014` complete through `PHASE8-IMPL-014-T007`.
- Local roadmap files show `PHASE8-IMPL-014-T001`, T002, T003, T004, T005, T006, and T007 complete.
- Local roadmap files show `PHASE8-IMPL-015` recommended-only (task_backlog.md entry as MVP-required future work) and not active/published before this publication.
- Local roadmap files show the active parent/child pending next parent publication after `PHASE8-IMPL-014-T007`.
- `tests/test_writer_assistant_review_api_contract.py` exists and is tracked; review API contract tests pass (161 tests) after `PHASE8-IMPL-014`.
- `backend/review_api.py` exists and is tracked; all seven public APIs present; read-only list/get/index/summary helpers accept optional keyword-only `project_dir`; write helpers are not called; owner action execution remains absent.
- `backend/story_knowledge/review_queue_storage.py` exists and is tracked.
- `tests/test_writer_assistant_core_review_queue_storage_contract.py` exists and is tracked.
- `backend/story_knowledge/candidate_review_gate.py` exists and is tracked.
- `tests/test_writer_assistant_core_candidate_review_gate_contract.py` exists and is tracked.
- No FastAPI review route registration exists in `backend/app.py`, `backend/main.py`, or any other backend router file.
- No frontend review UI exists (no review literals in `frontend/src/api.js`, `frontend/src/App.jsx`, `frontend/src/components/Editor.jsx`, or `frontend/src/components/ProjectNav.jsx`).
- No frontend API helper exists for the read-only review queue surface.
- No owner action command API route exists beyond `validate_owner_action_record` shape validation.
- No owner action execution exists.
- No apply-promotion exists.
- No memory/canon mutation exists.
- No raw artifact persistence exists.
- No runtime extraction exists.
- No real BookNLP/spaCy install/run/import exists.
- `.external_sources/` remains ignored/protected from commit and must not be staged.

## 12. Child Sequence

1. `PHASE8-IMPL-015-T001` - Publish review API route implementation and read-only frontend review queue surface parent. Status: complete.
2. `PHASE8-IMPL-015-T002` - Route/read-only frontend implementation reconciliation decision. Status: complete.
3. `PHASE8-IMPL-015-T003` - Backend route contract tests for read-only review queue endpoints. Status: complete/PASS expected-red.
4. `PHASE8-IMPL-015-T004` - Minimal backend route implementation over `backend.review_api` for read-only review queue endpoints. Status: complete/PASS.
5. `PHASE8-IMPL-015-T005` - Frontend API helper/read-only review queue surface contract or implementation plan, depending on existing frontend test harness constraints. Status: complete/PASS.
6. `PHASE8-IMPL-015-T006` - Route/frontend read-only safety regression or conditional hardening. Status: complete/PASS.
7. `PHASE8-IMPL-015-T007` - Roadmap/status closeout. Status: complete/PASS.
