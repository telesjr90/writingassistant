# PHASE8-IMPL-010 Inventory

## 1. Task Identity

- Parent ID: `PHASE8-IMPL-010`
- Title: Writer Assistant Core extraction orchestration planning and review-safe pipeline boundary
- Track: Writer Assistant Core
- Phase: Phase 8
- Status: active
- Depends on: completed `PHASE8-IMPL-009`
- Current child: `PHASE8-IMPL-010-T001` - Publish extraction orchestration planning parent
- Next child: `PHASE8-IMPL-010-T002` - Review-safe extraction pipeline contract decision

## 2. Why This Parent Exists

`PHASE8-IMPL-006` through `PHASE8-IMPL-009` built the evidence/source-map/raw storage/parser/adapter foundation.

The system can now parse synthetic BookNLP-like fixture strings into raw artifact bundles, but there is no orchestration contract for a review-safe extraction pipeline.

Before real runtime extraction, routes, UI, or persistence workflows, the app needs a contract for sequencing, boundaries, failure behavior, and owner-review handoff.

## 3. Existing Inputs

Foundation modules:

- `backend/story_knowledge/source_map.py`
- `backend/story_knowledge/evidence.py`
- `backend/story_knowledge/raw_extraction_storage.py`
- `backend/story_knowledge/booknlp_fixture_parser.py`
- `backend/story_knowledge/booknlp_adapter_contract.py`
- `backend/story_knowledge/candidate_persistence.py`
- `backend/story_knowledge/candidate_index.py`

Contract and regression tests:

- `tests/test_writer_assistant_core_source_evidence_contract.py`
- `tests/test_writer_assistant_core_raw_extraction_storage_contract.py`
- `tests/test_writer_assistant_core_booknlp_fixture_parser_contract.py`
- `tests/test_writer_assistant_core_booknlp_adapter_contract.py`
- `tests/test_writer_assistant_core_candidate_persistence_contract.py`
- `tests/test_writer_assistant_core_candidate_index_contract.py`

Roadmap foundation:

- `docs/roadmap/tasks/PHASE8-IMPL-006.md`
- `docs/roadmap/tasks/PHASE8-IMPL-007.md`
- `docs/roadmap/tasks/PHASE8-IMPL-008.md`
- `docs/roadmap/tasks/PHASE8-IMPL-009.md`
- `docs/roadmap/inventory/PHASE8-IMPL-009.md`
- `docs/roadmap/decisions/PHASE8-IMPL-009-parser-implementation-contract-reconciliation-decision.md`
- `docs/roadmap/enrichment/PHASE8-IMPL-009.enrichment.json`

## 4. Scope

- orchestration contract publication;
- review-safe pipeline decision;
- tests-first orchestration contract if authorized;
- optional minimal pure helper if authorized;
- candidate review handoff boundary decision;
- safety regressions/hardening;
- closeout.

## 5. Non-Scope

Explicitly excluded:

- real BookNLP install, run, or import;
- spaCy install, run, or import;
- real runtime extraction;
- parsing real BookNLP output files from disk;
- raw artifact write/read/list helpers into real projects;
- backend routes;
- frontend UI;
- package/dependency changes;
- automatic candidate persistence from raw outputs;
- memory/canon mutation;
- apply-promotion;
- generated prose;
- rewriting;
- continuation;
- model calls;
- training/JSONL/dataset work.

## 6. Risks

- orchestration mistaken for real extraction runtime;
- parser output mistaken for candidate truth;
- candidate drafts persisted without owner review;
- raw artifacts treated as canon;
- source/evidence locator mismatch;
- synthetic fixtures overfitting the pipeline;
- accidental filesystem writes;
- accidental route/UI/package scope creep;
- memory/canon mutation;
- generated prose behavior;
- future real BookNLP runtime introduced too early.

## 7. T001 Precondition Findings

- Local roadmap files show `PHASE8-IMPL-009` complete.
- Local roadmap files show `PHASE8-IMPL-009-T007` complete.
- Local roadmap files show `PHASE8-IMPL-010` recommended but not active before this publication.
- Local roadmap files show no active child after `PHASE8-IMPL-009-T007`.
- `backend/story_knowledge/booknlp_fixture_parser.py` exists and is tracked.
- `backend/story_knowledge/raw_extraction_storage.py` exists and is tracked.
- `tests/test_writer_assistant_core_booknlp_fixture_parser_contract.py` exists and is tracked.
- `tests/test_writer_assistant_core_raw_extraction_storage_contract.py` exists and is tracked.
- No runtime extraction is authorized or claimed by this parent.
- No raw artifact write/read/list helpers are authorized by this parent.
- No extraction orchestrator is authorized by T001.
- No backend extraction routes or frontend extraction UI are authorized by T001.
- BookNLP and spaCy are not installed or run by T001.
- `.external_sources/` remains protected from commit and must not be staged.

## 8. Child Sequence

1. `PHASE8-IMPL-010-T001` - Publish extraction orchestration planning parent.
2. `PHASE8-IMPL-010-T002` - Review-safe extraction pipeline contract decision.
3. `PHASE8-IMPL-010-T003` - Extraction orchestration contract tests.
4. `PHASE8-IMPL-010-T004` - Minimal review-safe orchestration helper.
5. `PHASE8-IMPL-010-T005` - Candidate review handoff and persistence boundary decision.
6. `PHASE8-IMPL-010-T006` - Orchestration safety regression or conditional hardening.
7. `PHASE8-IMPL-010-T007` - Roadmap/status closeout.
