# PHASE8-IMPL-013 Inventory

## 1. Task Identity

- Parent ID: `PHASE8-IMPL-013`
- Title: Writer Assistant Core review UI/API planning and owner-action workflow contract
- Track: Writer Assistant Core
- Phase: Phase 8
- Status: active
- Depends on: completed `PHASE8-IMPL-012` (complete through `PHASE8-IMPL-012-T007`)

## 2. Why This Parent Exists

- `PHASE8-IMPL-012` created `backend/story_knowledge/review_queue_storage.py`, a project-local candidate-linked review-workflow-only queue storage helper plus owner action record shape validation only.
- The review queue is now storable, listable, and indexable, and owner action records can be shape-validated, but nothing exposes the queue to an owner yet.
- The next risk is accidental backend review routes, owner action execution, review UI scope creep, or apply-promotion without an explicit contract.
- Before implementing any review route, owner-action command, or frontend review screen, the app needs a parent that defines the read-only review queue API contract, the owner-action command API contract, the review UI planning boundary, and the no-canon/no-promotion safety rules.
- Queue presence and owner actions remain non-approval, and owner review remains mandatory before anything can become approved truth.

## 3. Existing Inputs

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
- candidate schema/record/storage/persistence/list/index contract and safety regression tests:
  - `tests/test_writer_assistant_core_candidate_schema_contract.py`
  - `tests/test_writer_assistant_core_candidate_record_contract.py`
  - `tests/test_writer_assistant_core_candidate_storage_contract.py`
  - `tests/test_writer_assistant_core_candidate_persistence_contract.py`
  - `tests/test_writer_assistant_core_candidate_list_contract.py`
  - `tests/test_writer_assistant_core_candidate_index_contract.py`
  - `tests/test_writer_assistant_core_candidate_index_safety_regression.py`
- `backend/story_knowledge/source_map.py`
- `backend/story_knowledge/evidence.py`
- `PHASE8-IMPL-012` decision docs:
  - `docs/roadmap/decisions/PHASE8-IMPL-012-review-queue-storage-contract-decision.md`
  - `docs/roadmap/decisions/PHASE8-IMPL-012-owner-action-workflow-boundary-decision.md`
- `PHASE8-IMPL-011` and `PHASE8-IMPL-012` task records and closeouts:
  - `docs/roadmap/tasks/PHASE8-IMPL-011.md`
  - `docs/roadmap/tasks/PHASE8-IMPL-012.md`
  - `docs/roadmap/inventory/PHASE8-IMPL-012.md`
  - `docs/roadmap/enrichment/PHASE8-IMPL-012.enrichment.json`

## 4. Inherited Artifacts

From `PHASE8-IMPL-011` and `PHASE8-IMPL-012`:

- `backend/story_knowledge/candidate_review_gate.py`
- `backend/story_knowledge/review_queue_storage.py`
- `backend/story_knowledge/extraction_orchestrator.py`
- candidate review gate contract tests (`tests/test_writer_assistant_core_candidate_review_gate_contract.py`)
- review queue storage contract tests (`tests/test_writer_assistant_core_review_queue_storage_contract.py`)

## 5. Missing/Deferred Layers

- read-only review queue API;
- owner action command API;
- review UI planning;
- backend route implementation;
- frontend review UI implementation;
- owner action execution;
- apply-promotion;
- memory/canon mutation.

## 6. Scope

- read-only review queue API contract decision;
- owner-action command API contract decision;
- review UI planning boundary decision;
- review API/UI contract tests if authorized;
- review API/UI safety regression or conditional hardening decision;
- roadmap/status closeout.

## 7. Non-Scope

Explicitly excluded:

- review UI/API implementation in T001;
- backend review routes;
- frontend review UI;
- owner action execution;
- automatic candidate approval;
- approved/canon/promoted states;
- apply-promotion;
- memory/canon mutation;
- raw artifact persistence;
- real runtime extraction;
- real BookNLP/spaCy install, run, or import;
- package or dependency changes;
- generated prose;
- rewriting;
- continuation;
- model calls;
- training/JSONL/dataset work.

## 8. Safety Boundaries

- The review queue is workflow support only.
- Owner action is not promotion.
- A candidate record is not canon.
- Queue state is not approval.
- Evidence/provenance must be displayed in any future review surface.
- Confidence is uncertainty, not truth.

## 9. Risks

- read-only queue API mistaken for an approval API;
- owner action command API mistaken for apply-promotion;
- review UI scope creep into implementation;
- backend route scope creep;
- frontend UI scope creep;
- owner action execution creep;
- apply-promotion bypass;
- memory/canon mutation;
- missing evidence/provenance display in review surfaces;
- confidence presented as truth;
- generated prose leakage;
- runtime extraction creep.

## 10. Child Tasks

1. `PHASE8-IMPL-013-T001` - Publish review UI/API planning and owner-action workflow contract parent (complete).
2. `PHASE8-IMPL-013-T002` - Read-only review queue API contract decision (ready/active).
3. `PHASE8-IMPL-013-T003` - Owner action command API contract decision (planned).
4. `PHASE8-IMPL-013-T004` - Review UI planning boundary decision (planned).
5. `PHASE8-IMPL-013-T005` - Review API/UI contract tests, if authorized (planned).
6. `PHASE8-IMPL-013-T006` - Review API/UI safety regression or conditional hardening decision (planned).
7. `PHASE8-IMPL-013-T007` - Roadmap/status closeout (planned).
