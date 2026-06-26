# PHASE8-IMPL-014 Review API Implementation Reconciliation Decision

## 1. Decision Summary

`PHASE8-IMPL-014-T002` accepts this implementation reconciliation decision as docs/decision only.

The future `backend.review_api` implementation must be a single pure helper module at `backend/review_api.py`. It must be standard-library-only, route-free, frontend-free, project-local, deterministic, and bounded to request validation, response-shape building, and read-only review queue helpers over `backend/story_knowledge/review_queue_storage.py`.

The public API surface remains exactly:

- `list_review_queue_entries_readonly`
- `get_review_queue_entry_readonly`
- `get_review_queue_index_readonly`
- `get_review_queue_summary_readonly`
- `validate_review_queue_read_request`
- `validate_owner_action_command_request`
- `build_owner_action_command_response`

`PHASE8-IMPL-014-T002` does not implement `backend.review_api`, does not create backend routes, does not create frontend API helpers or UI, does not execute owner actions, does not apply promotion, does not mutate memory/canon, does not persist raw artifacts, does not run extraction, and does not run models or context tools.

## 2. Evidence Reconciled

This decision reconciles:

- the expected-red handoff at `tests/test_writer_assistant_review_api_contract.py`;
- `docs/roadmap/decisions/PHASE8-IMPL-013-read-only-review-queue-api-contract-decision.md`;
- `docs/roadmap/decisions/PHASE8-IMPL-013-owner-action-command-api-contract-decision.md`;
- `docs/roadmap/decisions/PHASE8-IMPL-013-review-ui-planning-boundary-decision.md`;
- `backend/story_knowledge/review_queue_storage.py`;
- `backend/story_knowledge/candidate_review_gate.py`;
- `docs/roadmap/tasks/PHASE8-IMPL-014.md`;
- `docs/roadmap/inventory/PHASE8-IMPL-014.md`;
- `docs/roadmap/enrichment/PHASE8-IMPL-014.enrichment.json`;
- `.codex-context/PHASE8-IMPL-014/collection_plan.md`;
- `.codex-context/PHASE8-IMPL-014/evidence_manifest.json`;
- `docs/roadmap/context_execution_standard.md`;
- `scripts/roadmap_enrichment/README.md`;
- `scripts/roadmap_enrichment/enrich_task.py`;
- `scripts/roadmap_enrichment/tool_commands.md`.

The already-generated context artifacts are evidence only. They are not roadmap truth and not task-completion records.

## 3. Child Task Split

T003 must create only the minimal `backend.review_api` validators and response builder:

- implement `validate_review_queue_read_request`;
- implement `validate_owner_action_command_request`;
- implement `build_owner_action_command_response`;
- keep the module pure and standard-library-only;
- perform no filesystem reads/writes, no storage integration, no route registration, no frontend work, no owner action execution, no promotion, no memory/canon mutation, no raw persistence, no runtime extraction, and no model/tool execution.

T004 must add only read-only review queue helper integration:

- implement `list_review_queue_entries_readonly`;
- implement `get_review_queue_entry_readonly`;
- implement `get_review_queue_index_readonly`;
- implement `get_review_queue_summary_readonly`;
- read through `review_queue_storage.list_review_queue_entries`, `review_queue_storage.read_review_queue_entry`, and `review_queue_storage.build_review_queue_index` only;
- validate requests through `validate_review_queue_read_request`;
- never call `write_review_queue_entry`, never mutate candidates, never write indexes, never write project files, and never write raw artifacts, memory, or canon.

T005 must integrate only owner action command request/response validation:

- refine `validate_owner_action_command_request` against the accepted command vocabulary and required/optional field set;
- refine `build_owner_action_command_response` as a response-shape builder only;
- return explicit no-promotion and no-memory/canon affirmations;
- never execute an owner action, never mutate queue state, never mutate candidate state, never apply promotion, and never write memory/canon.

T006 must be safety regression or conditional hardening only:

- run the expected review API contract and relevant focused regressions;
- patch only `backend.review_api` if the tests expose a narrow safety/contract gap;
- keep routes, frontend, owner action execution, apply-promotion, memory/canon mutation, raw persistence, runtime extraction, package changes, and model/tool execution outside the parent.

T007 must be roadmap/status closeout only.

## 4. Read Request Validator

`validate_review_queue_read_request` may return a deep or shallow copy of a valid read request containing only the allowed read fields from the expected-red contract:

- `project_id`;
- `queue_entry_id`;
- `review_status`;
- `lifecycle_state`;
- `candidate_type`;
- `target_category`;
- `normalization_status`;
- `has_raw_refs`;
- `confidence_min`;
- `confidence_max`;
- `sort_by`;
- `sort_direction`;
- `limit`;
- `offset`;
- `cursor`.

It must reject non-dict input, missing `project_id`, unsafe IDs, unknown fields, unsupported filters, unsupported sorts, malformed pagination, and every mutation/runtime/path/prose-shaped field, including owner-decision, approval, promotion, canon, apply-promotion, memory/canon destination, raw artifact read/write intent, runtime tool triggers, model calls, BookNLP/spaCy triggers, generated prose, rewrite, continuation, arbitrary paths, and filesystem paths.

Validation must fail closed by raising `TypeError` or `ValueError`. It must not repair by writing state.

## 5. Read-Only Helper Responses

The four read-only helpers may return dictionaries with only review support fields:

- `schema_version`;
- `project_id`;
- `entries`, `entry`, `index`, or `summary` depending on the helper;
- queue entry identifiers and candidate linkage fields;
- `candidate_type`;
- `target_category`;
- `review_status`;
- `lifecycle_state`;
- `confidence`;
- `uncertainty_flags`;
- `normalization_status`;
- `human_review_required`;
- `evidence_summary`;
- `evidence_refs`;
- `provenance_summary`;
- `provenance_refs`;
- `source_document`;
- `source_locator`;
- `raw_output_refs`;
- `created_at`;
- `updated_at`;
- pagination, summary, metadata, warnings, and errors.

They must preserve evidence, provenance, source document identity, source locators, raw output references, uncertainty, normalization status, and human-review-required state. `raw_output_refs` are support-only metadata. They are not raw artifact persistence, not canon, not candidate approval, and not training data.

They must reject or quarantine invalid support. Failure cases include forbidden fields, unsafe `project_id`, unsafe `queue_entry_id`, malformed requests, invalid queue entries, unavailable or missing storage, missing indexes, missing or invalid candidate linkage, unsafe paths, unsupported filters/sorts, and any approval/promotion/canon/memory/runtime/raw-write/prose intent.

Queue presence is not approval. Confidence is uncertainty/support strength, not truth. A valid API response is not owner approval.

## 6. Owner Action Command Validator and Response Builder

`validate_owner_action_command_request` may return a copy of a valid owner action command request with the required and optional fields from the expected-red contract. It must require project, queue, candidate, command, audit/reason/note, human-review, no-promotion, and no-memory/canon affirmations. It must allow only:

- `request_more_evidence`;
- `mark_needs_info`;
- `defer_review`;
- `reject_candidate`;
- `mark_duplicate`;
- `mark_superseded`;
- `archive_without_promotion`;
- `add_reviewer_note`;
- `clear_reviewer_note`;
- `edit_queue_metadata`;
- `prepare_for_promotion_review`;
- `mark_ready_for_separate_promotion_flow`.

`prepare_for_promotion_review` and `mark_ready_for_separate_promotion_flow` are workflow pointers only. They are not approval, not promotion, not canon, and not apply-promotion.

The validator must reject unsafe IDs, missing required fields, unknown fields, unsupported commands, unsafe commands, false no-promotion/no-memory/canon affirmations, `human_review_required` false, arbitrary path fields, generated prose fields, runtime/model/tool triggers, raw artifact persistence intent, training/JSONL intent, approval/canon/promotion fields, and memory/canon destinations.

`build_owner_action_command_response` is a response-shape builder only. It may return a dictionary containing schema/version, IDs, command, accepted flag, review/lifecycle workflow states, an owner action record shape, evidence/provenance/source support, `human_review_required`, `no_promotion_performed`, `no_memory_canon_mutation`, warnings, and errors. It must not execute an owner action, mutate queue state, mutate candidate records, write raw artifacts, write memory/canon, apply promotion, call models, or generate prose.

## 7. Route and UI Boundary

No FastAPI route registration is implemented in this parent. `backend.review_api` must not import FastAPI, `APIRouter`, `backend.app`, `backend.main`, or any route module. `backend/app.py`, `backend/main.py`, and backend route files remain out of scope.

No frontend review UI and no frontend API helpers are implemented in this parent. Frontend owner-action execution remains MVP-required future work outside `PHASE8-IMPL-014`.

## 8. Runtime and Product Safety Boundary

`PHASE8-IMPL-014` does not implement runtime extraction, model-assisted extraction, raw artifact persistence, real BookNLP/spaCy install/run/import, NCP/Subtxt/dramatica-flow runtime integration, frontend owner-action execution, owner action execution, apply-promotion, approved memory/canon mutation, training, JSONL, dataset manifests, model artifacts, or package/dependency changes.

Those runtime layers remain MVP-required in later parents `PHASE8-IMPL-015` through `PHASE8-IMPL-022`, except fine-tuning, which remains deferred after MVP.

Generated prose, rewrite, continuation, imitation, polish, improvement, expansion, outline, chapter generation, write/revise flows, and all prose-production paths remain permanently forbidden. They are not future, deferred, optional, nice-to-have, or later features.

## 9. Context Execution Boundary

CCE, Graphify, Repomix, LeanCTX, AI Context generation, MCP tools, scaffold, collect-plan, and context health scripts are not part of implementation micro-tasks. They must not run inside T003-T007 implementation prompts unless a future task explicitly switches to context collection or context validation mode.

Generated context artifacts may be cited as evidence, but roadmap truth remains controlled by the roadmap truth layer and reviewed decision/task/status records.

## 10. Implementation Handoff

The expected-red tests at `tests/test_writer_assistant_review_api_contract.py` remain the implementation handoff. T003-T006 must make those tests pass without broadening the public API surface, adding routes, adding UI, executing owner actions, applying promotion, mutating memory/canon, persisting raw artifacts, running extraction, calling models, installing dependencies, or generating prose.
