# PHASE8-IMPL-012 Owner Action Workflow Boundary Decision

## 1. Decision Summary

- `PHASE8-IMPL-012-T003` accepts the owner action workflow boundary as docs/decision only.
- Owner actions are review workflow commands and states only.
- Owner actions are not apply-promotion.
- Owner action storage is not memory/canon mutation.
- Owner action status is not approval/canon truth.
- Owner actions do not write approved memory, storyform, bible, scenes, notes, materials, or owner-authored source files.
- Review UI/API remains deferred.
- Backend routes and frontend UI remain deferred.
- T003 does not implement owner actions, queue storage, UI/API, routes, tests, apply-promotion, or memory/canon mutation.
- `PHASE8-IMPL-012-T004` should encode the T002 storage contract and the T003 owner action boundaries as tests-first coverage.
- `PHASE8-IMPL-012-T005` may implement a minimal storage helper only if T002-T004 authorize it.

## 2. Evidence Reviewed

T003 reviewed local repository evidence only:

- `PHASE8-IMPL-012-T001` parent publication in `docs/roadmap/tasks/PHASE8-IMPL-012.md`, `docs/roadmap/inventory/PHASE8-IMPL-012.md`, and `docs/roadmap/enrichment/PHASE8-IMPL-012.enrichment.json`.
- `PHASE8-IMPL-012-T002` review queue storage contract decision in `docs/roadmap/decisions/PHASE8-IMPL-012-review-queue-storage-contract-decision.md`.
- `PHASE8-IMPL-011-T002` candidate draft to record persistence gate decision in `docs/roadmap/decisions/PHASE8-IMPL-011-candidate-draft-to-record-persistence-gate-decision.md`.
- `PHASE8-IMPL-011-T003` review queue data shape and lifecycle decision in `docs/roadmap/decisions/PHASE8-IMPL-011-review-queue-data-shape-lifecycle-decision.md`.
- `PHASE8-IMPL-011-T005` candidate review gate helper `backend/story_knowledge/candidate_review_gate.py`, including the in-memory `build_review_queue_entry` builder.
- `PHASE8-IMPL-011-T006`/`PHASE8-IMPL-011-T007` validation and closeout records.
- `tests/test_writer_assistant_core_candidate_review_gate_contract.py` candidate review gate contract tests.
- `backend/story_knowledge/candidate_schema.py`.
- `backend/story_knowledge/candidate_record.py`.
- `backend/story_knowledge/candidate_storage.py`.
- `backend/story_knowledge/candidate_persistence.py`.
- `backend/story_knowledge/candidate_index.py`.
- `backend/story_knowledge/source_map.py` and `backend/story_knowledge/evidence.py`.
- `backend/story_knowledge/extraction_orchestrator.py`.
- candidate schema/record/storage/persistence/list/index contract and safety regression tests.

Record:

- no runtime code changes
- no tests changed
- no web research
- no external tool execution
- no model calls
- no BookNLP/spaCy runtime

## 3. Owner Action Purpose

Define owner actions as:

- explicit review workflow commands on candidate-linked queue entries
- a way to capture owner review intent at queue level
- a way to mark candidate support as needs information, rejected, deferred, duplicate, superseded, or archived
- a way to add reviewer notes or requests for more evidence
- not a promotion path
- not memory/canon mutation
- not automatic approval
- not storyform truth
- not a generated prose workflow
- not runtime extraction
- not raw artifact persistence

Owner actions express how the owner is reviewing a candidate-linked queue entry. They never establish project truth, and they never bypass the future, separate, owner-approved apply-promotion gate.

## 4. Allowed Owner Action Commands

Define allowed owner action commands as planning terms:

- `request_more_evidence`
- `mark_needs_info`
- `defer_review`
- `reject_candidate`
- `mark_duplicate`
- `mark_superseded`
- `archive_without_promotion`
- `add_reviewer_note`
- `clear_reviewer_note`
- `edit_queue_metadata`

Optional future commands only if later authorized:

- `prepare_for_promotion_review`
- `mark_ready_for_separate_promotion_flow`

Clarify:

- Do not allow `approve_candidate` in `PHASE8-IMPL-012`.
- Do not allow `promote_candidate` in `PHASE8-IMPL-012`.
- Do not allow `write_to_memory`.
- Do not allow `write_to_canon`.
- Do not allow `apply_promotion`.
- Do not allow `generate_prose`.
- Do not allow `rewrite_source`.
- Do not allow `continue_scene`.
- Do not allow `run_extractor`.

The optional future commands are pointers to a future, separate, owner-approved promotion-review workflow only. They do not promote, approve, or mutate memory/canon, and they are not authorized for implementation in this parent.

## 5. Allowed Owner Action States

Define allowed workflow states:

- `pending`
- `needs_info`
- `deferred`
- `rejected`
- `duplicate`
- `superseded`
- `archived_without_promotion`
- `blocked_invalid_support`
- `ready_for_separate_promotion_review`

Clarify:

- `ready_for_separate_promotion_review` is not approval.
- `ready_for_separate_promotion_review` does not mutate memory/canon.
- `ready_for_separate_promotion_review` may only point to a future separate promotion workflow.
- `approved` is not an allowed `PHASE8-IMPL-012` owner action state.
- `promoted` is not an allowed `PHASE8-IMPL-012` owner action state.
- `canon` is not an allowed state.
- `memory` is not an allowed state.

These owner action states are review workflow metadata only. They align with the T002 storage `review_status`/`lifecycle_state` values (`pending`, `needs_info`, `rejected`, `deferred`, `duplicate`, `superseded`, `archived`; `draft_ready_for_review`, `needs_more_evidence`, `blocked_invalid_support`, `owner_review_pending`, `owner_reviewed_rejected`, `owner_reviewed_deferred`, `duplicate_candidate`, `superseded_candidate`, `archived_without_promotion`) and must not be widened to add positive approval/canon/promoted semantics.

## 6. Owner Action Record Shape

Define a future owner action record shape if action records are stored separately.

Required fields:

- `action_id`
- `project_id`
- `queue_entry_id`
- `candidate_record_id`
- `action_command`
- `resulting_review_status`
- `resulting_lifecycle_state`
- `actor_id` or `actor_ref`
- `acted_at`
- `reason_code`
- `reviewer_note`
- `source_document`
- `source_locator`
- `evidence_refs`
- `provenance_refs`
- `human_review_required`
- `no_promotion_performed`
- `no_memory_canon_mutation`

Optional fields:

- `previous_review_status`
- `previous_lifecycle_state`
- `related_candidate_ids`
- `duplicate_candidate_ids`
- `superseded_by_candidate_id`
- `requested_evidence_note`
- `action_batch_id`
- `storage_version`
- `action_hash`

Forbidden fields:

- `approved`
- `promoted`
- `canon`
- `memory_destination`
- `apply_promotion`
- `storyform_truth`
- `bible_destination`
- `generated_prose`
- `rewrite`
- `continuation`
- `route_trigger`
- `ui_action_trigger`
- `runtime_tool_trigger`
- `model_call`
- `raw_artifact_write_intent`
- `training_destination`
- `jsonl_destination`

T003 defines this shape as planning only and does not implement action storage. The `no_promotion_performed` and `no_memory_canon_mutation` required fields are audit affirmations, not behavior switches; they must always be true for any owner action record because no promotion or memory/canon mutation path exists in this parent.

## 7. Queue Entry Mutation Boundary

Define:

- Owner actions may update queue workflow fields only if future tests/helper authorize it.
- Allowed queue fields for future mutation:
  - `review_status`
  - `lifecycle_state`
  - `reviewer_notes`
  - `insufficient_evidence_reason`
  - `rejected_output_reason`
  - `duplicate_candidate_ids`
  - `conflict_candidate_ids`
  - `related_candidate_ids`
  - `updated_at`
- Forbidden queue mutations:
  - `approved` status
  - `promoted` status
  - `canon` status
  - memory/canon destination
  - apply-promotion flag
  - candidate content rewrite
  - source/evidence/provenance deletion
  - raw artifact write/list/load
  - route/UI trigger
  - model/tool invocation

Clarify:

- Queue mutation is workflow support only.
- Queue mutation is not candidate truth mutation.
- Queue mutation is not project truth mutation.
- Queue mutation is not promotion.

## 8. Candidate Record Relationship

Define:

- Owner actions may reference candidate records.
- Owner actions must not directly modify candidate records unless a later tests-first helper explicitly authorizes safe candidate metadata synchronization.
- Owner actions must not set candidate record status to approved/canon/promoted.
- Owner actions must not prefill owner decision as approved.
- Owner actions must not write memory/canon.
- Owner actions must preserve candidate-only status.
- Candidate records remain separate from queue entries and action records.
- Any future synchronization must be candidate-only and review-workflow-only.

Candidate records remain the source of candidate content and candidate-only status, consistent with the T002 storage contract. Owner action records and queue entries are derived workflow support layers around those candidate records.

## 9. Apply-Promotion Boundary

State:

- Owner action workflow is not apply-promotion.
- apply-promotion remains unimplemented and out of scope.
- Marking `ready_for_separate_promotion_review` is only a pointer to future review, not promotion.
- Rejecting, deferring, or archiving a queue entry is not memory/canon mutation.
- Any future apply-promotion path must be a separate owner-approved parent/task, audited, explicit, separately tested, and must not be hidden inside queue storage or owner action helpers.

## 10. Memory/Canon Boundary

State:

Owner action workflow must never write:

- `memory/*.json`
- `memory/index.json`
- `bible.json`
- `storyform.json`
- `project.json`
- `scenes/`
- `chapters/`
- `notes/`
- `materials/`
- owner-authored source files

Owner actions are workflow metadata only.

Queue storage and action records are not approved truth.

## 11. Evidence and Provenance Requirements

State:

Every future owner action record or queue update must preserve or reference:

- source document identity
- source locator
- evidence references
- provenance references
- `candidate_record_id`
- `queue_entry_id`
- action command
- actor reference
- timestamp
- reason or reviewer note where applicable
- `human_review_required`
- `no_promotion_performed`
- `no_memory_canon_mutation`

Owner action records must not strip evidence/provenance to create a simpler task list. An owner action that cannot preserve or reference its candidate record's source/evidence/provenance must fail closed or be quarantined as invalid support rather than be recorded as a clean review action.

## 12. Owner Action Storage Boundary

State:

- T003 defines action storage shape only if later authorized.
- T003 does not implement action storage.
- Future action storage, if implemented, must be project-local under a queue/action workflow boundary.
- Future action storage must not write memory/canon.
- Future action storage must not write raw artifacts.
- Future action storage must not create training/JSONL/dataset files.
- Future action storage must not trigger UI/API routes.
- Future action storage must validate before writing and fail closed.

Potential future storage root if action records are stored separately:

- `projects/{project_id}/writer_assistant/review_queue/actions/{action_id}.json`

Do not authorize implementation in T003. This root sits inside the T002 review queue boundary `projects/{project_id}/writer_assistant/review_queue/` and shares its path-safety and forbidden-location rules.

## 13. Review UI/API Boundary

State:

- T003 does not implement review UI/API.
- T003 does not define backend routes.
- T003 does not define frontend screens.
- UI/API planning remains deferred unless local roadmap requires a later decision parent.
- Any future review UI/API must display evidence/provenance, uncertainty, non-approval status, and no-promotion warnings.
- UI/API must not hide that queue state is not canon truth.
- UI/API must not perform apply-promotion unless a separate approved workflow exists.

## 14. Failure and Quarantine Policy

Fail closed or quarantine when:

- unsupported owner action command
- unsupported owner action state
- approved/promoted/canon state requested
- apply-promotion intent appears
- memory/canon destination appears
- generated prose/rewrite/continuation appears
- raw artifact write intent appears
- runtime extraction/tool/model intent appears
- training/JSONL/dataset field appears
- missing `queue_entry_id`
- missing `candidate_record_id`
- missing source/evidence/provenance references
- invalid actor reference
- unsafe IDs or path traversal
- unknown fields
- any attempt to mutate candidate content or approved truth

No partial write should remain after failure unless future tests define a safe invalid-support quarantine path. If quarantine is later used, it must be candidate-only, non-canon, and not approval.

## 15. T004 Handoff

`PHASE8-IMPL-012-T004` - Review queue storage contract tests.

T004 should:

- be tests-first only
- be expected-red if a future storage helper/module does not exist
- encode the T002 storage contract and the T003 owner action boundary
- use `tmp_path` only
- define future helper/API names
- test queue entry validation
- test queue storage paths
- test write/read/list/index if authorized
- test owner action command/state validation if in scope
- test owner action record shape if in scope
- test fail-closed unsupported or unsafe entries/actions
- test no approval/canon/promoted status
- test no apply-promotion
- test no memory/canon mutation
- test no UI/API/routes
- test no raw artifact persistence
- test no generated prose
- add no implementation

## 16. T005/T006 Handoff

`PHASE8-IMPL-012-T005` - Minimal review queue storage helper, if authorized.

T005 should:

- implement only if T002-T004 authorize
- stay project-local
- stay candidate-linked
- stay candidate-only and review-workflow-only
- use existing candidate validation helpers where appropriate
- add no review UI/API
- add no backend routes
- execute no owner action beyond safe metadata if explicitly tested
- add no apply-promotion
- add no memory/canon mutation
- add no runtime extraction

`PHASE8-IMPL-012-T006` - Review queue safety regression or conditional hardening.

T006 should:

- validate no approval/canon/memory mutation
- validate no apply-promotion
- validate no route/UI/package/runtime expansion
- validate no generated prose
- validate no raw artifact persistence
- conditionally repair only if tests reveal gaps

## 17. Explicit Rejections

Reject:

- owner action workflow implementation in T003
- owner action storage implementation in T003
- review queue storage implementation in T003
- review UI/API implementation in T003
- backend review routes
- frontend review UI
- `approve_candidate` command
- `promote_candidate` command
- `write_to_memory` command
- `write_to_canon` command
- `apply_promotion` command
- approved/canon/promoted owner action state
- owner action as memory/canon truth
- automatic candidate approval
- queue entry as approval record
- memory/canon/storyform/bible/project/scenes/notes/materials writes
- raw artifact persistence
- runtime extraction
- real BookNLP/spaCy runtime
- package/dependency changes
- model calls
- generated prose/rewrite/continuation
- training/JSONL/dataset work

## 18. Accepted Decision

- ACCEPT owner actions as review workflow commands only.
- ACCEPT owner action states as workflow metadata only.
- ACCEPT no approval/canon/promoted states in `PHASE8-IMPL-012`.
- ACCEPT `ready_for_separate_promotion_review` only as a pointer to a future separate workflow, not promotion.
- ACCEPT owner action records as future optional audit/workflow support only.
- ACCEPT queue mutation only for workflow fields if later authorized by tests.
- ACCEPT evidence/provenance preservation as mandatory.
- ACCEPT review UI/API as deferred.
- ACCEPT `PHASE8-IMPL-012-T004` as tests-first queue storage and owner action boundary coverage.
- ACCEPT `PHASE8-IMPL-012-T005` as optional helper implementation only if authorized.
- REJECT apply-promotion, memory/canon mutation, review UI/API, backend routes, frontend UI, runtime extraction, raw persistence, and generated prose.
