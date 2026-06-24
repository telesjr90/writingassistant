# PHASE8-IMPL-011 Review Queue Data Shape and Lifecycle Decision

## 1. Decision Summary

- T003 accepts a review queue data shape and lifecycle boundary.
- Review queue entries are review workflow support, not approved truth.
- Queue presence does not imply owner approval.
- Queue sorting, grouping, priority, confidence, or source count does not imply canon truth.
- Review queue entries may reference candidate records or future persisted candidate records only after the T002 persistence gate.
- Review queue implementation remains deferred.
- Review UI/API remains deferred.
- Owner decisions remain deferred.
- Apply-promotion remains deferred.
- Memory/canon mutation remains forbidden.
- T004 should encode persistence gate and review queue boundary tests first.

## 2. Evidence Reviewed

T003 reviewed local repository evidence only:

- `PHASE8-IMPL-011-T001` parent publication in `docs/roadmap/tasks/PHASE8-IMPL-011.md`.
- `PHASE8-IMPL-011-T002` persistence gate decision in `docs/roadmap/decisions/PHASE8-IMPL-011-candidate-draft-to-record-persistence-gate-decision.md`.
- `PHASE8-IMPL-010` review-safe pipeline decision in `docs/roadmap/decisions/PHASE8-IMPL-010-review-safe-extraction-pipeline-contract-decision.md`.
- `PHASE8-IMPL-010` candidate review handoff decision in `docs/roadmap/decisions/PHASE8-IMPL-010-candidate-review-handoff-persistence-boundary-decision.md`.
- `backend/story_knowledge/extraction_orchestrator.py` and `tests/test_writer_assistant_core_extraction_orchestrator_contract.py`.
- `backend/story_knowledge/candidate_schema.py`.
- `backend/story_knowledge/candidate_record.py`.
- `backend/story_knowledge/candidate_persistence.py`.
- `backend/story_knowledge/candidate_index.py`.
- Candidate schema, record, persistence, and index contract tests.
- `backend/story_knowledge/source_map.py` and `backend/story_knowledge/evidence.py`.
- `PHASE8-IMPL-003` and `PHASE8-IMPL-004` candidate foundation parents.
- `PHASE8-IMPL-006` through `PHASE8-IMPL-010` extraction foundation parents.

T003 records:

- no runtime code changes;
- no tests changed;
- no web research;
- no external tool execution;
- no model calls;
- no BookNLP/spaCy runtime.

## 3. Review Queue Purpose

The review queue is:

- a project-local review workflow support structure;
- a way to organize candidate records that require owner review;
- a way to present evidence/provenance and uncertainty;
- a way to separate pending, rejected, needs-info, and ready-for-review states;
- not an approval record;
- not an apply-promotion queue;
- not canon;
- not memory;
- not storyform truth;
- not a generated-prose workflow.

## 4. Review Queue Entry Shape

Future review queue entries should use these required fields:

- `queue_entry_id`
- `project_id`
- `candidate_record_id`
- `candidate_type`
- `target_category`
- `review_status`
- `lifecycle_state`
- `source_document`
- `source_locator`
- `evidence_summary`
- `evidence_refs`
- `provenance_summary`
- `provenance_refs`
- `confidence`
- `uncertainty_flags`
- `normalization_status`
- `raw_output_refs`
- `human_review_required`
- `created_at`
- `updated_at`

Optional fields may include:

- `group_key`
- `sort_key`
- `priority_reason`
- `reviewer_notes`
- `owner_visible_label`
- `related_candidate_ids`
- `conflict_candidate_ids`
- `duplicate_candidate_ids`
- `insufficient_evidence_reason`
- `rejected_output_reason`

Forbidden fields:

- `owner_decision_approved`
- `promoted`
- `approved`
- `canon`
- `memory_destination`
- `apply_promotion`
- `storyform_truth`
- `generated_prose`
- `rewrite`
- `continuation`
- `route_trigger`
- `ui_action_trigger`
- `runtime_tool_trigger`
- `model_call`

## 5. Queue Lifecycle States

Allowed lifecycle states:

- `draft_ready_for_review`
- `needs_more_evidence`
- `blocked_invalid_support`
- `owner_review_pending`
- `owner_reviewed_rejected`
- `owner_reviewed_deferred`
- `duplicate_candidate`
- `superseded_candidate`
- `archived_without_promotion`

Lifecycle state is review workflow state only. It is not canon status, memory status, or apply-promotion. `owner_reviewed_*` states still do not mutate memory/canon.

## 6. Review Status Labels

Allowed `review_status` values:

- `pending`
- `needs_info`
- `rejected`
- `deferred`
- `duplicate`
- `superseded`
- `archived`

Do not use `approved` as a review queue status in `PHASE8-IMPL-011` unless future apply-promotion boundaries define it separately. If local style requires a positive status, use `ready_for_owner_action` rather than `approved`.

Review status does not equal owner decision for memory/canon.

## 7. Candidate Record Relationship

- Queue entries reference candidate records; they do not replace candidate records.
- Queue entries must not embed full candidate records unless future tests authorize a read model.
- Queue entries must not create candidate records automatically.
- Queue entries must not write candidate records directly unless a future persistence gate helper is explicitly authorized.
- Queue entries must not update candidate records to approved, canon, or promoted.
- Candidate records remain candidate-only until future review/apply-promotion boundaries.

## 8. Evidence and Provenance Display Requirements

Every queue entry must support display of:

- source document identity;
- source locator;
- evidence excerpt or evidence summary;
- evidence record references;
- provenance summary;
- raw output references where applicable;
- normalization status;
- confidence as uncertainty, not approval;
- insufficient-evidence or rejected-output reasons where applicable;
- `human_review_required`.

Queue display must never hide uncertainty or raw-tool limitations.

## 9. Insufficient Evidence and Rejected Output Handling

- `insufficient_evidence` candidates may enter a queue only as `needs_more_evidence` or `blocked_invalid_support`.
- `rejected_output` support may be tracked for audit/review only, not as a ready candidate.
- Ambiguous attribution must be clearly marked.
- Unsupported candidate types must be rejected or quarantined.
- Invalid source/evidence/provenance must fail closed.
- Queue state must not make invalid support look review-ready.

## 10. Grouping, Sorting, and Filtering Boundary

Grouping, sorting, and filtering are allowed only for workflow convenience.

Allowed grouping/sorting fields:

- `candidate_type`
- `target_category`
- `source_document`
- confidence band
- evidence completeness
- `normalization_status`
- `created_at`
- `related_candidate_ids`
- `duplicate_candidate_ids`
- `conflict_candidate_ids`

Forbidden implications:

- sorting by confidence does not imply truth;
- grouping by source count does not imply approval;
- priority is not owner decision;
- queue position is not canon status;
- filter visibility is not deletion or rejection.

## 11. Owner Action Labels

Future owner action labels are UI/API planning terms only:

- `mark_needs_info`
- `mark_deferred`
- `reject_candidate`
- `mark_duplicate`
- `archive_candidate`
- `request_more_evidence`
- `edit_candidate_support`

Owner actions are not implemented in T003. Owner action labels do not mutate memory/canon. Owner acceptance/promotion remains deferred. Apply-promotion remains a separate future path.

## 12. No Apply-Promotion Boundary

- Review queue lifecycle is not apply-promotion.
- Review queue entries cannot write approved memory/canon.
- Review queue entries cannot update storyform, bible, or project truth.
- Any apply-promotion path remains future owner-approved, audited, explicit, and separately tested.
- T003 does not authorize apply-promotion.

## 13. Storage and Persistence Boundary

- T003 defines queue shape only.
- T003 does not implement queue storage.
- Future queue storage must be project-local, candidate-linked, candidate-only, non-canon, and evidence/provenance-backed.
- Future queue storage must not write raw artifacts, memory/canon, project source files, training data, JSONL, or datasets.
- Future queue storage must not run tools or models.
- Future queue storage must not create UI/API routes without separate authorization.

## 14. T004 Handoff

`PHASE8-IMPL-011-T004` is Candidate persistence gate contract tests.

T004 should:

- be tests-first;
- be expected-red if a future helper/module does not exist;
- encode T002 persistence gate rules;
- encode T003 queue data shape/lifecycle boundaries;
- define future module/API only after T002/T003 decisions;
- test draft-to-record conversion boundary;
- test review queue entry shape if in scope;
- test fail-closed unsupported/unsafe drafts;
- test no owner decision prefill;
- test no approved/canon/promoted status;
- test no apply-promotion;
- test no memory/canon mutation;
- test no UI/API/routes;
- test no generated prose;
- use `tmp_path` only if isolated filesystem tests are needed.

## 15. T005/T006 Handoff

`PHASE8-IMPL-011-T005` is Minimal candidate persistence gate helper, if authorized.

T005 should:

- implement only if T002-T004 authorize;
- use existing candidate validators and persistence/index helpers;
- remain candidate-only;
- remain project-local;
- not wire orchestrator to auto-persist;
- not implement review UI/API;
- not implement apply-promotion;
- not mutate memory/canon.

`PHASE8-IMPL-011-T006` is Candidate review gate safety regression or conditional hardening.

T006 should:

- validate no owner-decision prefill;
- validate no approval/canon/memory mutation;
- validate no apply-promotion;
- validate no generated prose;
- validate no route/UI/package/runtime expansion;
- conditionally repair only if tests reveal gaps.

## 16. Explicit Rejections

Reject:

- review queue implementation in T003;
- review UI/API implementation in T003;
- backend review routes;
- frontend review UI;
- automatic candidate persistence;
- queue entry as approval record;
- owner decision prefill;
- approved/canon/promoted status in queue entries;
- apply-promotion;
- memory/canon/storyform/bible/project/scenes/notes/materials writes;
- raw artifact persistence;
- runtime extraction;
- real BookNLP/spaCy runtime;
- package/dependency changes;
- model calls;
- generated prose/rewrite/continuation;
- training/JSONL/dataset work.

## 17. Accepted Decision

- ACCEPT review queue entries as workflow support only.
- ACCEPT queue presence as non-approval.
- ACCEPT lifecycle states as review workflow states only.
- ACCEPT evidence/provenance/source locator display as mandatory.
- ACCEPT insufficient-evidence/rejected-output handling as explicit queue states or quarantine paths.
- ACCEPT grouping/sorting/filtering as workflow convenience only.
- ACCEPT owner action labels as future planning terms only.
- ACCEPT T004 as tests-first persistence/queue boundary contract.
- REJECT review queue implementation, UI/API, owner-decision prefill, apply-promotion, memory/canon mutation, runtime extraction, and generated prose.
