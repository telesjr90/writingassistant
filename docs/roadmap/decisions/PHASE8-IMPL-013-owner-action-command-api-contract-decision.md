# PHASE8-IMPL-013 Owner Action Command API Contract Decision

## 1. Decision Summary

- `PHASE8-IMPL-013-T003` accepts the owner action command API contract as docs/decision only.
- A future owner action command API is a command boundary for review workflow metadata only.
- It is not the T002 read-only review queue API, not apply-promotion, not memory/canon mutation, not generated prose/rewrite/continuation, not runtime extraction, not review UI implementation, and not automatic candidate approval.
- The command API contract should be defined before review UI planning so T004 can plan controls against a fixed fail-closed command vocabulary, but T003 implements no route, endpoint, helper, UI, owner action execution, queue mutation, or candidate mutation.
- Accepted commands are limited to review workflow commands aligned with `PHASE8-IMPL-012-T003`; approval, promotion, canon, memory, runtime extraction, raw artifact persistence, generated prose, training/JSONL, and unknown commands are rejected.
- Any future command response is workflow state only and must include audit/evidence/provenance fields plus explicit no-promotion/no-memory-canon affirmations.

## 2. Evidence Reviewed

T003 reviewed local repository evidence only:

- `docs/roadmap/tasks/PHASE8-IMPL-013.md`
- `docs/roadmap/inventory/PHASE8-IMPL-013.md`
- `docs/roadmap/enrichment/PHASE8-IMPL-013.enrichment.json`
- `docs/roadmap/decisions/PHASE8-IMPL-013-read-only-review-queue-api-contract-decision.md`
- `docs/roadmap/tasks/PHASE8-IMPL-012.md`
- `docs/roadmap/inventory/PHASE8-IMPL-012.md`
- `docs/roadmap/enrichment/PHASE8-IMPL-012.enrichment.json`
- `docs/roadmap/decisions/PHASE8-IMPL-012-review-queue-storage-contract-decision.md`
- `docs/roadmap/decisions/PHASE8-IMPL-012-owner-action-workflow-boundary-decision.md`
- `backend/story_knowledge/review_queue_storage.py`
- `tests/test_writer_assistant_core_review_queue_storage_contract.py`
- `backend/story_knowledge/candidate_review_gate.py`
- `tests/test_writer_assistant_core_candidate_review_gate_contract.py`
- `backend/story_knowledge/candidate_schema.py`
- `backend/story_knowledge/candidate_record.py`
- `backend/story_knowledge/candidate_storage.py`
- `backend/story_knowledge/candidate_persistence.py`
- `backend/story_knowledge/candidate_index.py`
- `backend/story_knowledge/extraction_orchestrator.py`
- `frontend/src/api.js`
- Current roadmap/status files and validation records.

Confirmed from local files:

- `PHASE8-IMPL-013` is active after T002; T001 and T002 are complete; T003 was ready/active; T004 was planned/next.
- `PHASE8-IMPL-012` is complete through T007.
- `backend/story_knowledge/review_queue_storage.py`, `tests/test_writer_assistant_core_review_queue_storage_contract.py`, `backend/story_knowledge/candidate_review_gate.py`, and `tests/test_writer_assistant_core_candidate_review_gate_contract.py` are tracked.
- `backend/story_knowledge/review_queue_storage.py` provides owner action record shape validation only through `validate_owner_action_record`; it does not execute owner actions.
- No owner action command API, backend review routes, frontend review UI, apply-promotion, memory/canon mutation, raw artifact persistence, or runtime extraction exists in this pipeline.
- `frontend/src/api.js` has no review queue or owner action helper.
- The requested `backend/app.py` file is not present or tracked in this checkout; existing roadmap/master-plan records identify backend route code under `backend/main.py`.
- `.external_sources/` remains ignored/protected from commit and was not staged.

## 3. Command API Purpose

The future owner action command API exists only to accept owner review workflow commands against candidate-linked review queue entries.

It may express workflow metadata such as needs-more-evidence, rejected, deferred, duplicate, superseded, archived-without-promotion, reviewer notes, and readiness for a separate future promotion review.

It is not:

- a read-only review queue API;
- apply-promotion;
- memory/canon mutation;
- generated prose, rewrite, continuation, improvement, polish, expansion, or imitation;
- runtime extraction;
- raw artifact persistence;
- review UI implementation;
- automatic candidate approval.

## 4. Command API Route Timing Decision

Decision: define the owner action command API contract before review UI planning, but do not implement routes in T003.

Rationale: T004 needs a stable command vocabulary and safety envelope before it can plan owner-action controls. Defining the contract first prevents the UI plan from inventing approval, promotion, canon, runtime extraction, or generated-prose controls.

Future route implementation remains deferred until tests authorize it. T003 creates no FastAPI endpoint, router, frontend API helper, UI control, queue mutation helper, candidate mutation helper, or owner action execution path.

## 5. Accepted Command Set

Accepted future command names as planning terms only:

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
- `prepare_for_promotion_review`
- `mark_ready_for_separate_promotion_flow`

`prepare_for_promotion_review` and `mark_ready_for_separate_promotion_flow` are not approval and not promotion. They are pointers to a future separate promotion workflow only. They cannot write memory/canon and cannot call apply-promotion.

## 6. Rejected Command Set

Rejected commands:

- `approve_candidate`
- `promote_candidate`
- `apply_promotion`
- `write_to_memory`
- `write_to_canon`
- `mutate_memory`
- `mark_canon`
- `mark_approved_truth`
- `generate_prose`
- `rewrite_source`
- `continue_scene`
- `run_extractor`
- `run_booknlp`
- `run_spacy`
- `persist_raw_artifact`
- `create_training_record`
- `export_jsonl`
- any unknown command

Rejected commands fail closed and must not be silently mapped to accepted commands.

## 7. Request Body Contract

Future request shape, planning only.

Required fields:

- `project_id`
- `queue_entry_id`
- `candidate_record_id`
- `action_command`
- `actor_ref` or `actor_id`
- `reason_code`
- `reviewer_note`
- `client_request_id`
- `human_review_required`
- `no_promotion_requested`
- `no_memory_canon_mutation_requested`

Optional fields:

- `previous_review_status`
- `previous_lifecycle_state`
- `target_review_status`
- `target_lifecycle_state`
- `related_candidate_ids`
- `duplicate_candidate_ids`
- `superseded_by_candidate_id`
- `requested_evidence_note`
- `command_metadata`
- `idempotency_key`

Rejected request fields:

- `approved`
- `promoted`
- `canon`
- `owner_decision_approved`
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
- arbitrary path fields
- source body edits

Unknown fields fail closed.

## 8. Response Shape Contract

Future response shape, planning only.

Required fields:

- `schema_version`
- `project_id`
- `queue_entry_id`
- `candidate_record_id`
- `action_command`
- `accepted`
- `review_status`
- `lifecycle_state`
- `owner_action_record`
- `evidence_refs`
- `provenance_refs`
- `source_locator`
- `source_document`
- `human_review_required`
- `no_promotion_performed`
- `no_memory_canon_mutation`
- `warnings`
- `errors`

Response must not include:

- approved truth;
- canon truth;
- promoted state;
- memory write result;
- apply-promotion result;
- generated prose;
- rewritten source;
- continuation text;
- runtime extraction output;
- raw artifact persistence result.

## 9. Actor and Audit Requirements

Future command handling must require:

- `actor_ref` or `actor_id`;
- `acted_at` or a server timestamp in future implementation;
- `client_request_id` or `idempotency_key` if command side effects are later implemented;
- `reason_code`;
- `reviewer_note`;
- previous status/lifecycle if available;
- resulting status/lifecycle;
- `no_promotion_performed` true;
- `no_memory_canon_mutation` true;
- evidence/provenance references;
- source locator/source document references.

Audit fields are required support for review workflow traceability. They are not authorization to promote, approve, write canon, or mutate memory.

## 10. Queue Entry Relationship

- A future command API may update queue workflow fields only if later tests and implementation authorize it.
- T003 does not implement queue updates.
- Command response is workflow state only.
- Command handling cannot create approved, canon, or promoted queue state.
- Command handling cannot delete evidence/provenance.
- Command handling cannot hide uncertainty.
- Command handling cannot write raw artifacts.

## 11. Candidate Record Relationship

- A future command API may reference candidate records by `candidate_record_id`.
- It must not mutate candidate content.
- It must not mark candidate records approved, canon, or promoted.
- It must not prefill owner decision as approved.
- It must preserve candidate-only status.
- Any future candidate metadata synchronization must be candidate-only, review-workflow-only, separately tested, and not memory/canon mutation.

## 12. Evidence and Provenance Requirements

Future command handling must preserve:

- source document identity;
- source locator;
- evidence refs;
- provenance refs;
- `queue_entry_id`;
- `candidate_record_id`;
- action command;
- actor ref;
- timestamp;
- reason/note;
- `human_review_required`;
- `no_promotion_performed`;
- `no_memory_canon_mutation`.

Missing evidence/provenance/source support fails closed or returns a safe quarantine response.

## 13. Fail-Closed Validation Policy

Fail closed for:

- unsupported command;
- rejected command;
- missing required fields;
- invalid actor field;
- invalid `project_id`;
- invalid `queue_entry_id`;
- invalid `candidate_record_id`;
- unsafe IDs/path traversal;
- approved/canon/promoted intent;
- apply-promotion intent;
- memory/canon destination;
- generated prose/rewrite/continuation intent;
- raw artifact write intent;
- runtime extraction/tool/model intent;
- training/JSONL/dataset intent;
- unknown fields;
- missing audit affirmations;
- `no_promotion_requested` false;
- `no_memory_canon_mutation_requested` false;
- `human_review_required` false.

Validation must reject rather than sanitize unsafe intent into a safe command.

## 14. Error and Quarantine Response Policy

Future command API behavior should return safe validation errors or rejected/quarantined command responses.

It must not:

- partially write unsafe commands;
- repair by writing memory/canon;
- silently coerce unsafe commands into safe commands;
- convert rejected commands into allowed ones;
- hide missing support data;
- leak arbitrary filesystem paths.

## 15. Apply-Promotion Boundary

The owner action command API is not apply-promotion.

`ready_for_separate_promotion_review`, `prepare_for_promotion_review`, and `mark_ready_for_separate_promotion_flow` are pointers only. They do not approve, promote, create canon truth, or write memory/canon.

Any future apply-promotion remains separate, owner-approved, audited, explicit, and separately tested.

## 16. Memory/Canon Boundary

The command API must never write:

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

The command API response is not approved truth.

## 17. Runtime Extraction and Raw Artifact Boundary

The command API must not:

- run runtime extraction;
- import or run BookNLP;
- import or run spaCy;
- persist raw artifacts;
- add raw write/read/list helpers;
- trigger tool/model execution.

Raw refs are support-only metadata.

## 18. Generated Prose/Rewriting/Continuation Boundary

The command API must not generate prose, rewrite source, continue scenes, improve prose, polish prose, expand prose, or imitate style.

Reviewer notes are owner-authored workflow metadata only. They are not assistant-authored story prose and must not become a generation surface.

## 19. Review UI Relationship

T003 may describe what a future UI needs from the command API, but it does not implement UI.

T004 decides the review UI planning boundary. Any future UI must show command effects as workflow state only, not approval/canon truth. It must show no-promotion/no-memory-canon warnings and must not expose controls for approval, promotion, memory/canon mutation, generated prose, runtime extraction, raw artifact persistence, training, or JSONL export.

## 20. T004 Handoff

T004 should decide the review UI planning boundary for:

- evidence/provenance/uncertainty display;
- non-approval status;
- no-promotion warnings;
- allowed owner-action controls as UI planning terms only;
- no frontend implementation;
- no route implementation;
- no apply-promotion;
- no memory/canon mutation;
- no generated prose.

T004 should use the accepted and rejected command sets here as the control vocabulary for planning, not as implemented behavior.

## 21. T005/T006 Handoff

- T005 should add review API/UI contract tests only if authorized by T002, T003, and T004. Tests-first expected-red behavior is appropriate if no future API/UI boundary helper exists.
- T006 should run a safety regression or conditional hardening decision only after prior tests and owner scope authorize it. No implementation should occur unless prior tasks explicitly authorize it.

## 22. Explicit Rejections

T003 rejects:

- command API implementation;
- route implementation;
- FastAPI endpoint implementation;
- frontend API helper implementation;
- frontend review UI;
- owner action execution;
- queue mutation implementation;
- candidate mutation implementation;
- owner decision approval;
- approval/canon/promoted states;
- apply-promotion;
- memory/canon mutation;
- raw artifact persistence;
- runtime extraction;
- real BookNLP/spaCy runtime;
- package changes;
- model calls;
- generated prose/rewrite/continuation;
- training/JSONL/dataset work.

## 23. Accepted Decision

Accepted: define the future owner action command API contract now, before review UI planning, as a review-workflow-only command boundary with a fail-closed accepted/rejected command set, safe request and response shapes, required actor/audit/evidence/provenance fields, explicit no-promotion and no-memory-canon affirmations, and strict separation from apply-promotion, memory/canon mutation, generated prose, runtime extraction, raw artifact persistence, backend route implementation, frontend implementation, and tests.

No implementation is authorized or performed in T003.
