# PHASE8-IMPL-011 Inventory

## 1. Task Identity

- Parent ID: `PHASE8-IMPL-011`
- Title: Writer Assistant Core candidate review queue and persistence gate planning
- Track: Writer Assistant Core
- Phase: Phase 8
- Status: active
- Depends on: completed `PHASE8-IMPL-010`
- Current child: `PHASE8-IMPL-011-T001` - Publish candidate review queue and persistence gate planning parent
- Next child: `PHASE8-IMPL-011-T002` - Candidate draft to candidate record persistence gate decision

## 2. Why This Parent Exists

`PHASE8-IMPL-010` created a pure in-memory fixture orchestrator (`backend/story_knowledge/extraction_orchestrator.py`) and boundary decisions for a review-safe extraction pipeline.

The orchestrator can return `candidate_drafts` as review support only. Candidate drafts are not candidate records, canon, memory, owner decisions, or promotion.

The next risk is accidental persistence or UI/review expansion without an explicit gate. The orchestrator output could be mistaken for persisted candidates, and persisted candidates could be mistaken for approved truth.

Before implementing any review queue or candidate persistence from orchestrator output, the app needs a parent that defines the persistence gate, review queue shape, review lifecycle, and safety boundaries. This parent stays planning/contract-first and does not persist candidates, build a review queue, add review UI/API, implement apply-promotion, or mutate memory/canon.

## 3. Existing Inputs

Foundation modules:

- `backend/story_knowledge/extraction_orchestrator.py`
- `backend/story_knowledge/candidate_schema.py`
- `backend/story_knowledge/candidate_record.py`
- `backend/story_knowledge/candidate_persistence.py`
- `backend/story_knowledge/candidate_index.py`
- `backend/story_knowledge/source_map.py`
- `backend/story_knowledge/evidence.py`

Contract and regression tests:

- `tests/test_writer_assistant_core_extraction_orchestrator_contract.py`
- `tests/test_writer_assistant_core_candidate_schema_contract.py`
- `tests/test_writer_assistant_core_candidate_record_contract.py`
- `tests/test_writer_assistant_core_candidate_persistence_contract.py`
- `tests/test_writer_assistant_core_candidate_index_contract.py`

Roadmap foundation:

- `docs/roadmap/tasks/PHASE8-IMPL-006.md`
- `docs/roadmap/tasks/PHASE8-IMPL-007.md`
- `docs/roadmap/tasks/PHASE8-IMPL-008.md`
- `docs/roadmap/tasks/PHASE8-IMPL-009.md`
- `docs/roadmap/tasks/PHASE8-IMPL-010.md`
- `docs/roadmap/inventory/PHASE8-IMPL-010.md`
- `docs/roadmap/enrichment/PHASE8-IMPL-010.enrichment.json`
- `docs/roadmap/decisions/PHASE8-IMPL-010-review-safe-extraction-pipeline-contract-decision.md`
- `docs/roadmap/decisions/PHASE8-IMPL-010-candidate-review-handoff-persistence-boundary-decision.md`

## 4. Scope

- candidate draft to candidate record persistence gate decision;
- review queue data shape and lifecycle decision;
- tests-first persistence gate contract if authorized;
- optional minimal pure helper only if authorized;
- candidate review UI/API boundary decision without implementing UI;
- safety regression or conditional hardening;
- closeout.

## 5. Non-Scope

Explicitly excluded:

- automatic persistence from orchestrator output;
- review UI/API implementation;
- backend review routes;
- frontend review UI;
- apply-promotion;
- memory/canon mutation;
- raw artifact persistence;
- real runtime extraction;
- real BookNLP/spaCy install, run, or import;
- package/dependency changes;
- generated prose;
- rewriting;
- continuation;
- model calls;
- training/JSONL/dataset work.

## 6. Risks

- candidate drafts mistaken for persisted candidates;
- persisted candidates mistaken for canon;
- owner decisions prefilled from confidence;
- review queue treated as approval queue;
- apply-promotion bypass;
- memory/canon mutation;
- evidence/provenance missing;
- source locator mismatch;
- route/UI scope creep;
- orchestrator auto-persistence;
- raw artifact persistence creep;
- generated prose leakage.

## 7. T001 Precondition Findings

- Local roadmap files show `PHASE8-IMPL-010` complete.
- Local roadmap files show `PHASE8-IMPL-010-T007` complete.
- Local roadmap files show `PHASE8-IMPL-011` recommended but not active/published before this publication.
- Local roadmap files show the active parent/child pending next parent publication after `PHASE8-IMPL-010-T007`.
- `backend/story_knowledge/extraction_orchestrator.py` exists and is tracked.
- `tests/test_writer_assistant_core_extraction_orchestrator_contract.py` exists and is tracked.
- Candidate schema/record/persistence/index helpers and tests exist and are tracked.
- No automatic candidate persistence from orchestrator output exists.
- No candidate review UI/API exists.
- No backend extraction/review routes exist.
- No frontend extraction/review UI exists.
- No apply-promotion exists in this pipeline.
- No memory/canon mutation exists.
- No runtime extraction exists.
- No real BookNLP/spaCy install or run exists.
- `.external_sources/` remains ignored/protected from commit and must not be staged.

## 8. Child Sequence

1. `PHASE8-IMPL-011-T001` - Publish candidate review queue and persistence gate planning parent.
2. `PHASE8-IMPL-011-T002` - Candidate draft to candidate record persistence gate decision.
3. `PHASE8-IMPL-011-T003` - Review queue data shape and lifecycle decision.
4. `PHASE8-IMPL-011-T004` - Candidate persistence gate contract tests.
5. `PHASE8-IMPL-011-T005` - Minimal candidate persistence gate helper, if authorized.
6. `PHASE8-IMPL-011-T006` - Candidate review gate safety regression or conditional hardening.
7. `PHASE8-IMPL-011-T007` - Roadmap/status closeout.
