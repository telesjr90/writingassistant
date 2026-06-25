# PHASE8-IMPL-012 Inventory

## 1. Task Identity

- Parent ID: `PHASE8-IMPL-012`
- Title: Writer Assistant Core review queue storage and owner-review workflow planning
- Track: Writer Assistant Core
- Phase: Phase 8
- Status: active
- Depends on: completed `PHASE8-IMPL-011` (complete through `PHASE8-IMPL-011-T007`)

## 2. Why This Parent Exists

- `PHASE8-IMPL-011` created `backend/story_knowledge/candidate_review_gate.py` and an in-memory review queue entry builder (`build_review_queue_entry`).
- The review queue entry is built in memory only; it is not stored, listed, or loaded yet.
- The next risk is accidental review queue storage, review UI/API, owner action workflow, or apply-promotion without an explicit contract.
- Before implementing review queue storage or owner actions, the app needs a parent that defines storage, lifecycle, owner-action boundaries, and no-canon/no-promotion safety rules.
- Queue presence remains non-approval, and owner review remains mandatory before anything can become approved truth.

## 3. Existing Inputs

- `backend/story_knowledge/candidate_review_gate.py`
- `tests/test_writer_assistant_core_candidate_review_gate_contract.py`
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
- `backend/story_knowledge/extraction_orchestrator.py`
- `tests/test_writer_assistant_core_extraction_orchestrator_contract.py`
- `PHASE8-IMPL-011` decision docs:
  - `docs/roadmap/decisions/PHASE8-IMPL-011-candidate-draft-to-record-persistence-gate-decision.md`
  - `docs/roadmap/decisions/PHASE8-IMPL-011-review-queue-data-shape-lifecycle-decision.md`
- `PHASE8-IMPL-010` and `PHASE8-IMPL-011` task records and closeouts:
  - `docs/roadmap/tasks/PHASE8-IMPL-010.md`
  - `docs/roadmap/tasks/PHASE8-IMPL-011.md`
  - `docs/roadmap/inventory/PHASE8-IMPL-011.md`
  - `docs/roadmap/enrichment/PHASE8-IMPL-011.enrichment.json`

## 4. Scope

- review queue storage contract decision;
- owner action workflow boundary decision;
- tests-first review queue storage contract if authorized;
- optional minimal pure queue storage helper only if authorized;
- review UI/API planning boundary decision without implementation;
- safety regression or conditional hardening;
- roadmap/status closeout.

## 5. Non-Scope

Explicitly excluded:

- queue storage implementation in T001;
- owner action implementation in T001;
- review UI/API implementation;
- backend review routes;
- frontend review UI;
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

## 6. Risks

- queue entry mistaken for approval;
- owner action mistaken for promotion;
- queue storage writes memory/canon;
- queue storage duplicates candidate truth;
- queue storage drifts from candidate record evidence/provenance;
- review UI/API scope creep;
- backend route scope creep;
- apply-promotion bypass;
- memory/canon mutation;
- missing evidence/provenance display;
- generated prose leakage;
- runtime extraction creep;
- raw artifact persistence creep.

## 7. Child Tasks

1. `PHASE8-IMPL-012-T001` - Publish review queue storage and owner-review workflow planning parent (complete).
2. `PHASE8-IMPL-012-T002` - Review queue storage contract decision (ready/active).
3. `PHASE8-IMPL-012-T003` - Owner action workflow boundary decision (planned).
4. `PHASE8-IMPL-012-T004` - Review queue storage contract tests (planned).
5. `PHASE8-IMPL-012-T005` - Minimal review queue storage helper, if authorized (planned).
6. `PHASE8-IMPL-012-T006` - Review queue safety regression or conditional hardening (planned).
7. `PHASE8-IMPL-012-T007` - Roadmap/status closeout (planned).
