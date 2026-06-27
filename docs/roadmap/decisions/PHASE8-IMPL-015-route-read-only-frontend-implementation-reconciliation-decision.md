# PHASE8-IMPL-015 Route Read-Only Frontend Implementation Reconciliation Decision

## 1. Decision Summary

`PHASE8-IMPL-015-T002` is accepted as docs/decision only.

`PHASE8-IMPL-015` will expose only read-only review queue data. The future backend route set for `PHASE8-IMPL-015-T003` and `PHASE8-IMPL-015-T004` maps one-to-one to the existing `backend.review_api` read helpers:

- `GET /api/projects/{project_id}/review-queue` wraps `list_review_queue_entries_readonly`.
- `GET /api/projects/{project_id}/review-queue/{queue_entry_id}` wraps `get_review_queue_entry_readonly`.
- `GET /api/projects/{project_id}/review-queue/index` wraps `get_review_queue_index_readonly`.
- `GET /api/projects/{project_id}/review-queue/summary` wraps `get_review_queue_summary_readonly`.

T004 is authorized to create `backend/routes/review_queue.py` as the lowest-risk route placement. The file is authorized only for T004 and only for these read-only routes. It must be included from `backend/main.py` only if existing app conventions require router registration there. T004 must not place unrelated routes in the new file.

Owner action command HTTP routes remain deferred to `PHASE8-IMPL-016`. `PHASE8-IMPL-015` has no owner action command HTTP routes. `validate_owner_action_command_request` and `build_owner_action_command_response` remain helper-level workflow shaping only and are not HTTP execution, owner action execution, apply-promotion, memory/canon mutation, raw artifact persistence, runtime extraction, model calls, or generated prose.

## 2. Evidence Reconciled

This decision reconciles:

- `.codex-context/PHASE8-IMPL-015/task_manifest.json`
- `.codex-context/PHASE8-IMPL-015/evidence_manifest.json`
- `.codex-context/PHASE8-IMPL-015/collection_plan.md`
- `backend/review_api.py`
- `tests/test_writer_assistant_review_api_contract.py`
- `backend/story_knowledge/review_queue_storage.py`
- `tests/test_writer_assistant_core_review_queue_storage_contract.py`
- `backend/story_knowledge/candidate_review_gate.py`
- `tests/test_writer_assistant_core_candidate_review_gate_contract.py`
- `docs/roadmap/decisions/PHASE8-IMPL-013-read-only-review-queue-api-contract-decision.md`
- `docs/roadmap/decisions/PHASE8-IMPL-013-owner-action-command-api-contract-decision.md`
- `docs/roadmap/decisions/PHASE8-IMPL-013-review-ui-planning-boundary-decision.md`
- `docs/roadmap/decisions/PHASE8-IMPL-014-review-api-implementation-reconciliation-decision.md`

The generated PHASE8-IMPL-015 context pack files are read-only evidence only. They are not roadmap truth and are not task completion records.

No context tools were run inside T002. LeanCTX, CCE, Graphify, Repomix, AI Context generation, MCP tools, scaffold, collect-plan, context health scripts, and baseline refresh commands remain outside this implementation micro-task.

## 3. Backend Read-Only Route Split

The future read-only route set is exactly four GET routes:

| Purpose | Method and path | Helper |
| --- | --- | --- |
| List review queue entries | `GET /api/projects/{project_id}/review-queue` | `backend.review_api.list_review_queue_entries_readonly` |
| Get one review queue entry | `GET /api/projects/{project_id}/review-queue/{queue_entry_id}` | `backend.review_api.get_review_queue_entry_readonly` |
| Get review queue index | `GET /api/projects/{project_id}/review-queue/index` | `backend.review_api.get_review_queue_index_readonly` |
| Get review queue summary | `GET /api/projects/{project_id}/review-queue/summary` | `backend.review_api.get_review_queue_summary_readonly` |

No POST, PUT, PATCH, DELETE, WebSocket, background task, extraction trigger, owner action command route, apply-promotion route, memory/canon route, raw persistence route, model route, or generated prose route is authorized in `PHASE8-IMPL-015`.

Required path parameters:

- `project_id`: path-safe project identifier accepted by `validate_review_queue_read_request`.
- `queue_entry_id`: path-safe queue entry identifier on the single-entry route only.

Optional query parameters on list, index, and summary routes:

- `review_status`
- `lifecycle_state`
- `candidate_type`
- `target_category`
- `normalization_status`
- `has_raw_refs`
- `confidence_min`
- `confidence_max`
- `sort_by`
- `sort_direction`
- `limit`
- `offset`
- `cursor`

The single-entry route may accept only read-only display filters that `validate_review_queue_read_request` accepts and that do not change identity. Unknown query fields fail closed.

## 4. Error and Response Shape Principles

Routes must validate request data through `backend.review_api.validate_review_queue_read_request` before calling the read helper. Invalid path IDs, unsafe IDs, unknown query fields, malformed booleans/numbers, unsupported filters/sorts, malformed queue entries, missing queue/index storage, missing linked candidate records, invalid candidate linkage, forbidden request fields, and malformed JSON fail closed.

HTTP error shapes should be structured and display-safe:

- `schema_version`
- `project_id` when safely available
- `queue_entry_id` when safely available and relevant
- `error`
- `warnings`
- `errors`

Errors must not repair by writing, must not expose arbitrary filesystem paths, and must not convert invalid support into a clean review-ready entry.

Successful responses must project the existing `backend.review_api` helper response shapes without widening semantics:

- list: `schema_version`, `project_id`, `entries`, `pagination`, `summary`, `metadata`, `warnings`, `errors`
- single entry: `schema_version`, `project_id`, `queue_entry_id` at the route wrapper level or entry level, `entry`, `metadata`, `warnings`, `errors`
- index: `schema_version`, `project_id`, `entries` or an index-compatible read model, `summary`, `metadata`, `warnings`, `errors`
- summary: `schema_version`, `project_id`, `summary`, `metadata`, `warnings`, `errors`

Entry payloads must preserve evidence/provenance/source locators/raw refs/confidence-as-uncertainty/human_review_required and may expose only review support fields from `backend.review_api`: `queue_entry_id`, `project_id`, `candidate_record_id`, `candidate_type`, `target_category`, `review_status`, `lifecycle_state`, `confidence`, `uncertainty_flags`, `normalization_status`, `human_review_required`, `evidence_summary`, `evidence_refs`, `provenance_summary`, `provenance_refs`, `source_document`, `source_locator`, `raw_output_refs`, `created_at`, and `updated_at`.

Queue presence is not approval. A valid API response is not owner approval. Confidence is uncertainty/support strength, not truth. Frontend display is not promotion.

## 5. Backend Route Placement

T004 should create `backend/routes/review_queue.py` and register it from `backend/main.py` only as needed to attach the router to the existing FastAPI app. This is lower risk than placing multiple review queue endpoint bodies directly in `backend/main.py` because it keeps the review queue route boundary source-scannable and prevents accidental mixing with unrelated app routes.

The new route file is authorized only for `PHASE8-IMPL-015-T004` and only for the four read-only review queue GET routes listed in this decision. T004 may edit:

- `backend/routes/review_queue.py`
- `backend/main.py`, only for minimal router inclusion
- `tests/test_writer_assistant_review_api_routes_contract.py`, only if a small contract alignment fix is required by the T003 expected-red tests

T004 may not edit:

- `backend/review_api.py`, except narrow read-only safety fixes deferred to T006
- `backend/story_knowledge/review_queue_storage.py`
- `backend/story_knowledge/candidate_review_gate.py`
- candidate persistence, candidate index, source/evidence, parser, adapter, raw storage, extraction, memory, canon, or model modules
- frontend files
- package or dependency files
- training data, JSONL files, datasets, model artifacts, source-cache files, or project runtime files

## 6. Backend Helper Boundary

T004 routes must wrap `backend.review_api` helpers only:

- `validate_review_queue_read_request`
- `list_review_queue_entries_readonly`
- `get_review_queue_entry_readonly`
- `get_review_queue_index_readonly`
- `get_review_queue_summary_readonly`

T004 routes must not call `review_queue_storage` write helpers directly. They must not call candidate persistence helpers directly. They must not call owner action validation/response helpers except for display-only schema references if explicitly justified in the T004 final response and validated by T006. They must not execute owner action commands.

T004 routes must not call:

- `write_review_queue_entry`
- candidate record mutation or candidate JSON write helpers
- candidate index write helpers
- owner action execution helpers
- apply-promotion helpers
- memory/canon write helpers
- raw artifact persistence helpers
- extraction orchestrators or external runtime adapters
- model/Ollama/Story Check calls
- generated prose, rewrite, continuation, outline, chapter, write, revise, or prose-production paths

## 7. Owner Action Command HTTP Route Boundary

Owner action command HTTP routes remain deferred to `PHASE8-IMPL-016`.

`PHASE8-IMPL-015` has no owner action command routes. It must not expose POST/PUT/PATCH/DELETE routes for owner commands, review decisions, reviewer notes, metadata edits, status changes, queue mutation, candidate mutation, promotion readiness, apply-promotion, or memory/canon writes.

`validate_owner_action_command_request` and `build_owner_action_command_response` remain helper-level workflow shaping only. They are not HTTP execution, not owner action execution, not queue mutation, not candidate mutation, not approval, not apply-promotion, not memory/canon mutation, not raw artifact persistence, not runtime extraction, not model calls, and not generated prose.

## 8. T003 Backend Route Contract Tests

T003 must add expected-red route contract tests at:

- `tests/test_writer_assistant_review_api_routes_contract.py`

T003 must test:

- read-only route paths and GET-only methods;
- safe `project_id` handling;
- safe `queue_entry_id` handling;
- missing queue/index behavior;
- malformed queue entry behavior;
- unknown filters/sorts/query fields;
- response shape preserves evidence/provenance/source locators/raw refs/confidence-as-uncertainty/human_review_required;
- no write/mutation behavior;
- no owner-action execution;
- no apply-promotion;
- no memory/canon mutation;
- no raw persistence;
- no runtime extraction;
- no model calls;
- no generated prose.

T003 must stay tests-first. It must not create `backend/routes/review_queue.py`, must not edit `backend/main.py`, must not register routes, must not modify frontend files, and must not change packages.

## 9. T004 Minimal Backend Route Implementation

T004 must satisfy the T003 tests with the smallest route implementation. It may add the approved route file and minimal router registration only. Routes must build request dictionaries from safe path/query data, validate through `backend.review_api`, call the matching read-only helper, return the helper projection, and convert validation/storage failures into structured read-only errors.

T004 must preserve tests-first route boundary: the route implementation must be driven by `tests/test_writer_assistant_review_api_routes_contract.py`, not by new UI requirements or owner command workflows.

T004 may edit exactly:

- `backend/routes/review_queue.py`
- `backend/main.py`
- `tests/test_writer_assistant_review_api_routes_contract.py`, only for narrow expected-red-to-green contract alignment if the test target itself contains an implementation-inconsistent assertion

T004 must not edit backend helper modules, frontend files, package/dependency files, training/source-cache files, project runtime files, or generated context artifacts.

## 10. PHASE8-IMPL-015-T005 Frontend API Helper and Read-Only Surface

`PHASE8-IMPL-015-T005` should produce a frontend implementation plan, not frontend contract tests, unless a local frontend/component test harness already exists without package changes at T005 start. Frontend contract tests remain deferred if package changes or test-harness changes would be required.

If T005 is limited to planning, it must create:

- `docs/roadmap/decisions/PHASE8-IMPL-015-frontend-read-only-surface-implementation-decision.md`

If T005 later confirms frontend implementation is allowed without package/test-harness changes, the candidate frontend API helper module is:

- `frontend/src/api/reviewQueue.js`

The candidate read-only review queue surface component/page is:

- `frontend/src/components/ReviewQueueSurface.jsx`

Allowed fields to display:

- `queue_entry_id`
- `candidate_record_id`
- `candidate_type`
- `target_category`
- `review_status`
- `lifecycle_state`
- `confidence` as uncertainty/support strength
- `uncertainty_flags`
- `normalization_status`
- `human_review_required`
- `evidence_summary`
- `evidence_refs`
- `provenance_summary`
- `provenance_refs`
- `source_document`
- `source_locator`
- `raw_output_refs` as support-only references
- `created_at`
- `updated_at`
- summary/count metadata and read-only pagination/filter state

Required labels/warnings:

- pending candidates are not canon
- queue presence is not approval
- confidence is uncertainty/support strength
- frontend display is not promotion
- owner action execution is not available in this parent
- apply-promotion is not available in this parent

The frontend surface must have no generated prose controls, no owner action controls, no write controls, no approval controls, no promotion controls, no apply-promotion controls, no memory/canon controls, no raw persistence controls, no runtime extraction controls, no model call controls, and no route-trigger controls.

## 11. PHASE8-IMPL-015-T006 Safety Regression Expectations

`PHASE8-IMPL-015-T006` must run focused route/frontend read-only safety regressions and source checks. It must include:

- route no-write checks for the approved route file;
- checks that no POST/PUT/PATCH/DELETE owner command routes were added;
- checks that T004 routes call `backend.review_api` read helpers only;
- checks that route source does not call write helpers, candidate persistence writes, apply-promotion, owner action execution, memory/canon mutation, raw artifact persistence, runtime extraction, model calls, generated prose, or package/runtime installers;
- frontend no-command-control checks if T005 implements any frontend surface;
- no BookNLP/spaCy runtime/import checks;
- no NCP/Subtxt/dramatica-flow runtime import checks;
- no model/runtime extraction/raw persistence checks;
- `.external_sources/` not staged and ignored/protected checks.

T006 may conditionally harden only the approved route file, the approved frontend surface, the approved frontend API helper, `backend.review_api.py`, or the approved tests if focused validation exposes a narrow read-only safety gap. It must not broaden PHASE8-IMPL-015 into command execution, apply-promotion, memory/canon mutation, raw artifact persistence, runtime extraction, model calls, package changes, or generated prose.

## 12. Future Parent Boundary

`PHASE8-IMPL-016` remains the future parent for frontend owner-action execution workflow and review command boundary. It is the first parent allowed to consider owner action command HTTP routes and frontend owner-action controls, and only within safe owner-review workflow boundaries.

`PHASE8-IMPL-017` remains the future parent for apply-promotion and approved memory/canon mutation. Apply-promotion must be explicit, audited, owner-confirmed, evidence/provenance-backed, and never automatic.

`PHASE8-IMPL-018+` remain future for raw artifact persistence, runtime extraction, model-assisted extraction, real BookNLP/spaCy runtime, NCP/Subtxt/dramatica-flow analysis-only runtime integrations, and end-to-end MVP validation as already documented.

Fine-tuning remains deferred after MVP.

Generated prose, rewrite, continuation, imitation, polish, improvement, expansion, outline generation, chapter generation, write/revise flows, export-as-prose, and prose-production paths remain permanently forbidden. They are not deferred future features.

## 13. Accepted Decision

- ACCEPT the four-route GET-only read-only route split over `backend.review_api` list/get/index/summary helpers.
- ACCEPT `backend/routes/review_queue.py` as the T004 route placement, authorized only for T004 and only for read-only review queue routes, with minimal `backend/main.py` router inclusion if required.
- ACCEPT `tests/test_writer_assistant_review_api_routes_contract.py` as the T003 expected-red route contract test target.
- ACCEPT that T004 wraps `backend.review_api` helpers only and does not call storage write helpers, candidate persistence helpers, owner action execution, apply-promotion, memory/canon mutation, raw persistence, runtime extraction, model calls, or generated prose paths.
- ACCEPT that owner action command HTTP routes remain deferred to `PHASE8-IMPL-016`.
- ACCEPT that T005 should produce a frontend implementation plan unless an existing frontend test harness can be used without package changes.
- ACCEPT T006 route no-write, frontend no-command-control, no BookNLP/spaCy runtime/import, no model/runtime extraction/raw persistence, no generated prose, and source-cache safety regressions.
- REJECT route implementation, frontend implementation, backend code changes, frontend file changes, test changes, package changes, runtime/training/model/source-cache changes, owner action execution, apply-promotion, memory/canon mutation, runtime extraction, raw artifact persistence, model calls, and generated prose in T002.
