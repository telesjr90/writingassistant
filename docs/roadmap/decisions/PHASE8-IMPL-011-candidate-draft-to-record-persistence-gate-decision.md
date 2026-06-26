# PHASE8-IMPL-011 Candidate Draft to Candidate Record Persistence Gate Decision

## 1. Decision Summary

- T002 accepts a persistence gate between orchestrator `candidate_drafts` and persisted candidate records.
- `candidate_drafts` remain in-memory support until a future authorized helper validates and converts them.
- Candidate persistence is not automatic.
- Candidate persistence requires explicit owner-approved scope, source locator, evidence, provenance, candidate-only status, and fail-closed validation.
- Persisted candidate records remain non-canon and non-memory.
- Owner decisions are not prefilled by orchestrator confidence, tool output, parser output, or adapter output.
- Review queue planning remains T003.
- Contract tests remain T004.
- Minimal helper implementation remains optional and deferred to T005 if authorized.
- Review UI/API, apply-promotion, memory/canon mutation, raw artifact persistence, and runtime extraction remain deferred.

## 2. Evidence Reviewed

Reviewed local project evidence:

- `docs/roadmap/decisions/PHASE8-IMPL-010-review-safe-extraction-pipeline-contract-decision.md`
- `docs/roadmap/decisions/PHASE8-IMPL-010-candidate-review-handoff-persistence-boundary-decision.md`
- `backend/story_knowledge/extraction_orchestrator.py`
- `tests/test_writer_assistant_core_extraction_orchestrator_contract.py`
- `backend/story_knowledge/candidate_schema.py`
- `backend/story_knowledge/candidate_record.py`
- `backend/story_knowledge/candidate_persistence.py`
- `backend/story_knowledge/candidate_index.py`
- `tests/test_writer_assistant_core_candidate_schema_contract.py`
- `tests/test_writer_assistant_core_candidate_record_contract.py`
- `tests/test_writer_assistant_core_candidate_persistence_contract.py`
- `tests/test_writer_assistant_core_candidate_index_contract.py`
- `backend/story_knowledge/source_map.py`
- `backend/story_knowledge/evidence.py`
- `tests/test_writer_assistant_core_source_evidence_contract.py`
- `docs/roadmap/tasks/PHASE8-IMPL-003.md`
- `docs/roadmap/tasks/PHASE8-IMPL-004.md`
- `docs/roadmap/tasks/PHASE8-IMPL-006.md` through `docs/roadmap/tasks/PHASE8-IMPL-010.md`

Record:

- no runtime code changes
- no tests changed
- no web research
- no external tool execution
- no model calls
- no BookNLP/spaCy runtime

## 3. Candidate Draft Input Boundary

Accepted candidate draft input:

- `candidate_drafts` must come from the app-owned orchestrator or later approved in-memory support structures.
- `candidate_drafts` are not trusted as valid records by themselves.
- Every draft must be validated before persistence.
- Drafts must include or map to:
  - `candidate_type` or `target_category`
  - `source_document` ref
  - `source_locator`
  - `evidence`
  - `provenance`
  - `confidence`
  - `raw_output_refs` where applicable
  - `normalization_status`
  - `human_review_required`
- Drafts with insufficient evidence, rejected output, ambiguous attribution, missing locators, missing provenance, unsafe fields, or unsupported candidate types must fail closed.

Rejected draft input:

- drafts from arbitrary JSON without validation
- drafts that include `owner_decision`
- drafts that include promoted, approved, canon, or memory status
- drafts that include apply-promotion intent
- drafts that include prose-generation content
- drafts that include persistence destinations outside project-local candidate storage
- drafts that request route, UI, model, or tool execution

## 4. Candidate Record Output Boundary

Persisted candidate record output:

- must use existing candidate schema/record validators
- must use project-local candidate storage helpers only
- must keep candidate-only status
- must not set approved, canon, or promoted state
- must not write memory/canon
- must not apply promotion
- must not update owner-approved truth
- must not create raw artifact persistence
- must not create training, JSONL, or dataset records
- must not store generated prose or rewritten prose
- must preserve evidence, provenance, and source locator fields
- must preserve raw support limitations and uncertainty
- must preserve `human_review_required`

## 5. Persistence Gate Requirements

A future persistence gate helper may convert `candidate_drafts` to candidate records only when all are true:

- explicit owner-approved implementation task authorizes the persistence gate helper
- request policy says `persist_candidates` is true only within that authorized helper scope
- each candidate draft validates against allowed draft fields
- each converted record validates with existing candidate record validation
- `candidate_type` is supported by candidate schema constants
- `source_document` ref is present and valid
- `source_locator` is present and valid
- evidence record is present and valid
- provenance is present and valid
- confidence is bounded and never treated as approval
- `raw_output_refs` remain support-only
- `human_review_required` is true
- `owner_decision` is absent or explicitly set to pending or unreviewed if existing schema requires a value
- promoted, approved, canon, and memory flags are absent or false
- destination is limited to candidate storage/review queue, not memory/canon
- index updates use existing candidate index helpers only
- no route, UI, or apply-promotion side effect occurs
- no generated prose content is accepted

## 6. Fail-Closed Rejection Rules

Reject or quarantine without persistence when:

- unsupported `candidate_type`
- missing evidence
- missing `source_locator`
- missing `source_document`
- missing provenance
- invalid confidence
- ambiguous quote or coreference attribution
- `normalization_status` is `rejected_output`
- `normalization_status` is `insufficient_evidence` and local policy requires evidence-backed persistence only
- unknown fields appear
- `owner_decision` is prefilled as approved or rejected
- status implies approved, canon, or promoted
- destination points to memory, canon, storyform, bible, scenes, notes, materials, or project files
- any apply-promotion intent appears
- generated prose, rewrite, or continuation fields appear
- raw artifact write, read, or list intent appears
- runtime extraction, tool, or model intent appears
- training, JSONL, or dataset fields appear
- path traversal or unsafe project/candidate IDs appear

## 7. Review Queue Relationship

- T002 does not define full review queue shape.
- T003 will define review queue data shape and lifecycle.
- T002 only decides that any persisted candidate record meant for review must remain candidate-only and review-pending.
- Review queue entries may reference candidate records, but cannot be approval records.
- Queue presence is not owner approval.
- Queue sorting, filtering, or grouping must not imply truth.
- Review queue implementation remains deferred.

## 8. Owner Review Boundary

- Owner review is mandatory before any candidate can become approved truth.
- Owner review is not performed by the orchestrator.
- Owner review is not performed by the persistence gate.
- Owner review is not implied by confidence.
- Owner review is not implied by schema validity.
- Owner review is not implied by queue inclusion.
- Owner review UI/API remains deferred.

## 9. Apply-Promotion Boundary

- apply-promotion remains out of scope.
- Candidate persistence is not promotion.
- Review queue inclusion is not promotion.
- Owner acceptance in a future review UI is still not memory/canon mutation unless a separate apply-promotion path is approved.
- Future apply-promotion must be owner-approved, audited, explicit, and separately tested.

## 10. Memory/Canon Boundary

No candidate persistence path may write:

- `memory/*.json`
- `memory/index.json`
- `bible.json`
- `storyform.json`
- `project.json`
- `scenes/`
- `notes/`
- `materials/`
- owner-authored source files

Candidate records are not durable project truth. Candidate records must remain visually and structurally separated from approved memory/canon.

## 11. Evidence and Provenance Requirements

Every future persisted candidate must preserve:

- source document identity
- source locator
- evidence excerpt or source-derived support
- provenance including adapter/orchestrator/parser context where applicable
- raw output refs where applicable
- confidence as uncertainty, not approval
- normalization status
- `human_review_required` flag
- no canon/memory destination fields

## 12. T003 Handoff

`PHASE8-IMPL-011-T003` - Review queue data shape and lifecycle decision.

T003 should decide:

- review queue entry shape
- queue lifecycle states
- how candidate records enter a queue
- how insufficient-evidence/rejected-output records are represented
- owner action labels
- evidence/provenance display requirements
- grouping/sorting/filtering boundaries
- no apply-promotion boundary
- no memory/canon mutation boundary
- no UI/API implementation

## 13. T004/T005 Handoff

`PHASE8-IMPL-011-T004` - Candidate persistence gate contract tests.

T004 should:

- remain tests-first only
- be expected-red if the future gate helper does not exist
- define future helper/API only after T002/T003 decisions
- test draft validation
- test conversion to candidate-only records
- test fail-closed unsupported or unsafe drafts
- test no owner decision prefill
- test no apply-promotion
- test no memory/canon mutation
- use `tmp_path` only if isolated filesystem tests are needed
- add no routes/UI

`PHASE8-IMPL-011-T005` - Minimal candidate persistence gate helper, if authorized.

T005 should:

- implement only if T002-T004 authorize
- use existing candidate validators and persistence/index helpers
- remain candidate-only
- remain project-local
- add no orchestrator auto-persistence
- add no review UI/API
- add no apply-promotion
- add no memory/canon mutation

## 14. Explicit Rejections

Reject:

- automatic persistence from orchestrator output
- candidate persistence inside `extraction_orchestrator.py`
- direct use of `candidate_drafts` as candidate records
- owner decision prefill from confidence
- approved, canon, or promoted status in persistence gate output
- memory, canon, storyform, bible, project, scenes, notes, or materials writes
- review UI/API in T002
- backend routes in T002
- frontend UI in T002
- apply-promotion
- raw artifact persistence
- runtime extraction
- real BookNLP/spaCy runtime
- package/dependency changes
- generated prose, rewrite, or continuation
- training, JSONL, or dataset work

## 15. Accepted Decision

- ACCEPT `candidate_drafts` as validated input support only.
- ACCEPT a future explicit persistence gate before candidate records may be written.
- ACCEPT existing candidate schema/record/persistence/index helpers as the only allowed persistence foundation.
- ACCEPT source locators, evidence, and provenance as mandatory.
- ACCEPT candidate-only and review-pending status as mandatory.
- ACCEPT T003 as review queue shape/lifecycle decision.
- ACCEPT T004 as tests-first persistence gate contract.
- ACCEPT T005 as optional helper implementation only if authorized.
- REJECT automatic persistence, owner-decision prefill, apply-promotion, memory/canon mutation, raw persistence, runtime extraction, and generated prose.
