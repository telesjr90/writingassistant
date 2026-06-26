# PHASE8-IMPL-014 Inventory

## 1. Task Identity

- Parent ID: `PHASE8-IMPL-014`
- Title: Writer Assistant Core review API implementation and tests-first route boundary
- Track: Writer Assistant Core
- Phase: Phase 8
- Status: complete
- Depends on: completed `PHASE8-IMPL-013` (complete through `PHASE8-IMPL-013-T007`)
- Current child: none; parent closed after `PHASE8-IMPL-014-T007`
- Recommended next parent: `PHASE8-IMPL-015` - Review API route implementation and read-only frontend review queue surface (MVP-required; recommendation-only until separately published)

## 2. Why This Parent Exists

`PHASE8-IMPL-013` produced the read-only review queue API contract decision, the owner action command API contract decision, the review UI planning boundary decision, and the expected-red review API contract tests at `tests/test_writer_assistant_review_api_contract.py` for the future `backend.review_api` module.

The expected-red contract tests pin the public API surface: `list_review_queue_entries_readonly`, `get_review_queue_entry_readonly`, `get_review_queue_index_readonly`, `get_review_queue_summary_readonly`, `validate_review_queue_read_request`, `validate_owner_action_command_request`, and `build_owner_action_command_response`.

The next risk is accidental backend route registration, owner action execution, frontend review UI scope creep, or apply-promotion while satisfying the contract tests. Before implementing `backend.review_api`, the app needs a parent that authorizes a minimal pure helper module, splits read-only review queue helpers from owner action command validators, requires fail-closed validation, requires preservation of evidence/provenance/uncertainty, requires no mutation through the read-only surface, requires no owner action execution through the command validator, and preserves the no-route/no-UI/no-promotion/no-memory-canon/no-runtime-extraction/no-generated-prose boundaries.

## 3. Existing Inputs

Foundation modules:

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

- `tests/test_writer_assistant_review_api_contract.py` (PHASE8-IMPL-013-T005; expected-red for future `backend.review_api`)
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

From `PHASE8-IMPL-011`, `PHASE8-IMPL-012`, and `PHASE8-IMPL-013`:

- `backend/story_knowledge/review_queue_storage.py`
- `backend/story_knowledge/candidate_review_gate.py`
- `backend/story_knowledge/extraction_orchestrator.py`
- `tests/test_writer_assistant_review_api_contract.py`
- `tests/test_writer_assistant_core_review_queue_storage_contract.py`
- `tests/test_writer_assistant_core_candidate_review_gate_contract.py`
- candidate review gate / review queue storage / orchestrator contract tests

## 5. Missing/Deferred Layers

Implemented in this parent:

- `backend/review_api.py` with all seven public APIs (`list_review_queue_entries_readonly`, `get_review_queue_entry_readonly`, `get_review_queue_index_readonly`, `get_review_queue_summary_readonly`, `validate_review_queue_read_request`, `validate_owner_action_command_request`, `build_owner_action_command_response`).

Still missing/deferred after this parent:
- FastAPI route registration in `backend/app.py`;
- frontend review UI;
- frontend API helpers;
- owner action execution workflow;
- owner action storage/write/read/list beyond validation only;
- apply-promotion;
- memory/canon mutation;
- orchestrator auto-persistence;
- raw artifact persistence;
- real BookNLP/spaCy runtime;
- runtime extraction;
- byte-to-character source matching;
- NCP/Subtxt/dramatica-flow implementation;
- model-assisted extraction;
- training/JSONL/dataset work.

## 6. Implementation Target

- `backend/review_api.py` implemented as a pure helper module only.
- No route registration.
- No UI yet.
- Pure request validators only (`validate_review_queue_read_request`, `validate_owner_action_command_request`).
- Pure response builders only (`build_owner_action_command_response`).
- Read-only review queue helpers only (`list_review_queue_entries_readonly`, `get_review_queue_entry_readonly`, `get_review_queue_index_readonly`, `get_review_queue_summary_readonly`) over `review_queue_storage.py` only.
- No owner action execution.
- No queue mutation through any future command API.
- No candidate mutation through any future command API.

## 7. Scope

- docs/status/planning publication in T001;
- review API implementation reconciliation decision (T002 docs/decision only);
- minimal `backend.review_api` validators and response builders (T003);
- read-only review queue API helper integration (T004);
- owner action command request/response validation integration (T005);
- review API safety regression or conditional hardening (T006);
- roadmap/status closeout (T007).

## 8. Non-Scope

Explicitly excluded for the entire parent:

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
- package or dependency changes;
- generated prose, rewriting, continuation, imitation, polish, improvement, or expansion;
- model calls, Ollama calls, Story Check calls, demos, or app server runs;
- training data, JSONL records, dataset manifests, model artifacts, or fine-tuning configs.

## 9. Safety Boundaries

- The review queue is workflow support only.
- Owner action is not promotion.
- A candidate record is not canon.
- Queue state is not approval.
- Evidence/provenance must be displayed in any future review surface.
- Confidence is uncertainty, not truth.
- Read-only helpers must never mutate queue entries, candidate records, indexes, project files, raw artifacts, memory, or canon.
- Owner action command validators must never execute owner actions, must never write memory/canon, must never apply-promotion, and must never generate prose.
- `backend.review_api` must never register FastAPI routes or import `backend/app.py`.
- `backend.review_api` must never be imported into frontend code.

## 10. Risks

- `backend.review_api` registers routes in `backend/app.py` (route scope creep);
- read-only helper mutates storage accidentally;
- owner action command validator becomes hidden execution;
- `prepare_for_promotion_review` or `mark_ready_for_separate_promotion_flow` misread as approval/promotion;
- hidden apply-promotion through the command API;
- memory/canon mutation through the read-only helper or command validator;
- evidence/provenance omitted from the read-only response;
- confidence presented as truth;
- route/UI scope creep into a later child;
- frontend API helper scope creep into a later child;
- generated prose leakage into reviewer notes or response shapes;
- runtime extraction or raw artifact persistence creep through the command API;
- BookNLP/spaCy install/run creep through the helper module;
- package/dependency changes leak into implementation micro-tasks.

## 11. T001 Precondition Findings

- Local roadmap files show `PHASE8-IMPL-013` complete through `PHASE8-IMPL-013-T007`.
- Local roadmap files show `PHASE8-IMPL-013-T001`, T002, T003, T004, T005, T006, and T007 complete.
- Local roadmap files show `PHASE8-IMPL-014` recommended-only (task_backlog.md entry as RECOMMENDED ONLY) and not active/published before this publication.
- Local roadmap files show the active parent/child pending next parent publication after `PHASE8-IMPL-013-T007`.
- `tests/test_writer_assistant_review_api_contract.py` exists and is tracked.
- `backend/story_knowledge/review_queue_storage.py` exists and is tracked.
- `tests/test_writer_assistant_core_review_queue_storage_contract.py` exists and is tracked.
- `backend/story_knowledge/candidate_review_gate.py` exists and is tracked.
- `tests/test_writer_assistant_core_candidate_review_gate_contract.py` exists and is tracked.
- `backend.review_api` exists as `backend/review_api.py` with all seven public APIs present; read-only list/get/index/summary helpers accept optional keyword-only `project_dir` and use `review_queue_storage` read/list/build helpers when `project_dir` is supplied; write helpers are not called; owner action execution remains absent.
- No frontend review UI exists (no review literals in `frontend/src/api.js`, `frontend/src/App.jsx`, `frontend/src/components/Editor.jsx`, or `frontend/src/components/ProjectNav.jsx`).
- No owner action command API implementation exists beyond `validate_owner_action_record` shape validation.
- No owner action execution exists.
- No apply-promotion exists in this pipeline.
- No memory/canon mutation exists.
- No raw artifact persistence exists.
- No runtime extraction exists.
- No real BookNLP/spaCy install/run/import exists.
- `.external_sources/` remains ignored/protected from commit and must not be staged.

## 12. Child Sequence

1. `PHASE8-IMPL-014-T001` - Publish review API implementation and tests-first route boundary parent. Status: complete.
2. `PHASE8-IMPL-014-T002` - Review API implementation reconciliation decision. Status: complete.
3. `PHASE8-IMPL-014-T003` - Minimal `backend.review_api` validators and response builders. Status: complete.
4. `PHASE8-IMPL-014-T004` - Read-only review queue API helper integration. Status: complete.
5. `PHASE8-IMPL-014-T005` - Owner action command request/response validation integration. Status: complete.
6. `PHASE8-IMPL-014-T006` - Review API safety regression or conditional hardening. Status: complete.
7. `PHASE8-IMPL-014-T007` - Roadmap/status closeout. Status: complete.
