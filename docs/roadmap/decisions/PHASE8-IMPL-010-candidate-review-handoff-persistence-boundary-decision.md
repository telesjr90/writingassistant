# PHASE8-IMPL-010 Candidate Review Handoff and Persistence Boundary Decision

## 1. Decision Summary

- T005 accepts a boundary where orchestration outputs remain in-memory support unless a future owner-approved task explicitly persists candidate records.
- Candidate draft support is not candidate persistence.
- Candidate persistence remains deferred.
- Candidate review UI/API remains deferred.
- Owner decisions remain deferred.
- Apply-promotion remains deferred.
- Memory/canon mutation remains forbidden.
- Raw artifact persistence remains deferred.
- Real runtime extraction remains deferred.
- T006 should validate safety boundaries and conditionally harden only if gaps exist.

## 2. Evidence Reviewed

Reviewed local project evidence:

- `docs/roadmap/decisions/PHASE8-IMPL-010-review-safe-extraction-pipeline-contract-decision.md`
- `backend/story_knowledge/extraction_orchestrator.py`
- `tests/test_writer_assistant_core_extraction_orchestrator_contract.py`
- `backend/story_knowledge/booknlp_fixture_parser.py`
- `tests/test_writer_assistant_core_booknlp_fixture_parser_contract.py`
- `backend/story_knowledge/raw_extraction_storage.py`
- `tests/test_writer_assistant_core_raw_extraction_storage_contract.py`
- `backend/story_knowledge/booknlp_adapter_contract.py`
- `tests/test_writer_assistant_core_booknlp_adapter_contract.py`
- `backend/story_knowledge/source_map.py`
- `backend/story_knowledge/evidence.py`
- `tests/test_writer_assistant_core_source_evidence_contract.py`
- `backend/story_knowledge/candidate_schema.py`
- `backend/story_knowledge/candidate_record.py`
- `backend/story_knowledge/candidate_persistence.py`
- `backend/story_knowledge/candidate_index.py`
- `tests/test_writer_assistant_core_candidate_schema_contract.py`
- `tests/test_writer_assistant_core_candidate_record_contract.py`
- `tests/test_writer_assistant_core_candidate_persistence_contract.py`
- `tests/test_writer_assistant_core_candidate_index_contract.py`
- `docs/roadmap/tasks/PHASE8-IMPL-006.md`
- `docs/roadmap/tasks/PHASE8-IMPL-007.md`
- `docs/roadmap/tasks/PHASE8-IMPL-008.md`
- `docs/roadmap/tasks/PHASE8-IMPL-009.md`

Evidence confirmed:

- the T002 review-safe pipeline contract already requires `persist_candidates = false`, `persist_raw_artifacts = false`, `allow_canon_write = false`, and `allow_prose_generation = false`;
- `backend/story_knowledge/extraction_orchestrator.py` returns review-safe, in-memory orchestration output only and does not invoke candidate persistence or index writers;
- orchestrator contract tests already enforce no side effects, no persistence, no canon/memory mutation, and no runtime extraction broadening;
- parser/storage/adapter/source/evidence helpers remain support-only and do not authorize candidate persistence from orchestrator output;
- candidate schema/record/persistence/index helpers exist separately and are not an authorization for orchestrator-driven persistence.

This task used local repository evidence only.

- No web research.
- No external tool execution.
- No model calls.
- No real BookNLP/spaCy runtime.
- No code/test changes.

## 3. Candidate Draft vs Candidate Record Boundary

Candidate draft support means:

- in-memory only;
- derived from parser/adapter/orchestrator support;
- evidence/provenance-backed;
- review-only;
- non-canon;
- non-memory;
- non-promoted;
- no owner decision;
- no persistence destination.

Candidate record means:

- persisted candidate JSON or app-owned candidate record;
- must use existing candidate schema/record validation;
- must preserve candidate-only status;
- must be created only by a future owner-approved task;
- must not imply canon/memory approval;
- must not bypass owner review.

Decision:

- Orchestrator output can contain `candidate_drafts` only.
- Orchestrator output cannot persist candidate records in `PHASE8-IMPL-010`.
- Converting `candidate_drafts` to candidate records is deferred.

## 4. Future Candidate Persistence Gate

A future task may persist candidate records only if all of these are true:

- explicit owner approval for candidate persistence scope;
- existing candidate schema/record validators are used;
- source locator, evidence, and provenance are required for every persisted candidate;
- candidate status remains candidate-only;
- no promoted, approved-memory, or canon status is implied;
- no owner decision is prefilled by orchestration;
- no apply-promotion occurs;
- no memory/canon writes occur;
- persistence destination is project-local candidate storage only;
- indexes are updated only through existing candidate index helpers;
- review UI/API boundary is defined before user-facing workflows.

## 5. Candidate Review UI/API Gate

Candidate review UI/API remains deferred until a later parent.

A future review workflow must:

- show candidate drafts/records as suggestions only;
- show evidence, provenance, and source locators;
- show insufficient-evidence or rejected-output status when applicable;
- require explicit owner action;
- separate accept/reject/edit from apply-promotion;
- never write memory/canon directly;
- never hide raw support limitations;
- never treat BookNLP/coreference/quote/event signals as approved truth.

## 6. Owner Decision Boundary

- Owner decisions are not stored by orchestrator.
- Owner decisions are not implied by high confidence.
- Owner decisions are not implied by successful parser/orchestrator validation.
- Owner decisions require a future review mechanism.
- Owner decisions may later update candidate state, but not memory/canon directly unless future apply-promotion is separately authorized.

## 7. Apply-Promotion Boundary

- apply-promotion remains out of scope.
- Candidate persistence, candidate review, and apply-promotion are separate gates.
- Accepting a candidate in review is not the same as writing approved memory/canon.
- Any apply-promotion path must be future owner-approved, audited, explicit, and tested separately.

## 8. Raw Artifact Persistence Boundary

- raw artifact path and manifest helpers exist;
- fixture parser/orchestrator currently builds raw bundles in memory;
- raw artifact persistence remains deferred;
- no raw write/read/list helpers are authorized;
- future raw persistence must be explicit, project-local, manifest-backed, non-canon, non-candidate, and not training data.

## 9. Runtime Extraction Boundary

- real BookNLP/spaCy runtime remains deferred;
- fixture orchestration is not runtime extraction;
- future runtime extraction needs separate package/dependency decision, security/privacy review, local execution policy, source-to-output mapping, and owner approval.

## 10. Evidence/Provenance Requirement

Any future candidate persistence must require:

- `source_document` ref;
- `source_locator`;
- evidence record;
- provenance metadata;
- `raw_output_refs` where applicable;
- confidence bounded and not treated as approval;
- `human_review_required`;
- no canon/memory destination fields.

## 11. T006 Handoff

`PHASE8-IMPL-010-T006` remains:

- `PHASE8-IMPL-010-T006` - Orchestration safety regression or conditional hardening.

T006 should:

- run orchestrator, parser, storage, adapter, source/evidence, candidate, and OMI/project regressions;
- confirm no raw persistence, candidate persistence, memory/canon mutation, routes/UI/package changes, runtime extraction, tool execution, or prose behavior;
- inspect source-level boundaries;
- conditionally harden `backend/story_knowledge/extraction_orchestrator.py` only if a validation gap exists;
- not implement persistence, routes, UI, runtime extraction, or apply-promotion.

## 12. Explicit Rejections

Reject:

- automatic candidate persistence from orchestrator output;
- candidate review UI/API in `PHASE8-IMPL-010`;
- owner decision creation in orchestrator output;
- apply-promotion;
- memory/canon mutation;
- raw artifact persistence;
- real runtime extraction;
- backend extraction routes;
- frontend extraction/review UI;
- package changes;
- model calls;
- generated prose, rewrite, or continuation;
- training/JSONL/dataset work.

## 13. Accepted Decision

- ACCEPT candidate drafts as in-memory review support.
- ACCEPT candidate persistence as deferred.
- ACCEPT review UI/API as deferred.
- ACCEPT owner decisions as deferred.
- ACCEPT apply-promotion as deferred.
- ACCEPT raw artifact persistence as deferred.
- ACCEPT runtime extraction as deferred.
- ACCEPT evidence, provenance, and source locator as mandatory for any future persisted candidate.
- ACCEPT T006 as safety regression/conditional hardening.
- REJECT automatic persistence, canon mutation, and promotion behavior.
