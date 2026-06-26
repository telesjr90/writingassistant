# PHASE8-IMPL-012 Review Queue Storage Contract Decision

## 1. Decision Summary

- `PHASE8-IMPL-012-T002` accepts the review queue storage contract as docs/decision only.
- Queue entries remain workflow support only, not approval, canon, memory, storyform truth, owner decision, generated prose, or apply-promotion.
- Queue storage, if later implemented, must be project-local, candidate-linked, candidate-only, review-workflow-only, evidence/provenance-backed, and fail-closed.
- T002 does not implement queue storage, listing, or loading.
- T002 does not implement an owner action workflow.
- T002 does not implement review UI/API, backend routes, frontend UI, apply-promotion, memory/canon mutation, raw artifact persistence, or runtime extraction.
- `PHASE8-IMPL-012-T003` will decide owner action workflow boundaries.
- `PHASE8-IMPL-012-T004` should add tests-first storage contract coverage.
- `PHASE8-IMPL-012-T005` may implement a minimal helper only if T002-T004 authorize it.

## 2. Evidence Reviewed

T002 reviewed local repository evidence only:

- `PHASE8-IMPL-012-T001` parent publication in `docs/roadmap/tasks/PHASE8-IMPL-012.md`, `docs/roadmap/inventory/PHASE8-IMPL-012.md`, and `docs/roadmap/enrichment/PHASE8-IMPL-012.enrichment.json`.
- `PHASE8-IMPL-011-T002` persistence gate decision in `docs/roadmap/decisions/PHASE8-IMPL-011-candidate-draft-to-record-persistence-gate-decision.md`.
- `PHASE8-IMPL-011-T003` review queue data shape and lifecycle decision in `docs/roadmap/decisions/PHASE8-IMPL-011-review-queue-data-shape-lifecycle-decision.md`.
- `PHASE8-IMPL-011-T004` candidate review gate contract tests in `tests/test_writer_assistant_core_candidate_review_gate_contract.py`.
- `PHASE8-IMPL-011-T005` candidate review gate helper in `backend/story_knowledge/candidate_review_gate.py`.
- `PHASE8-IMPL-011-T006`/`PHASE8-IMPL-011-T007` validation and closeout records.
- `backend/story_knowledge/candidate_review_gate.py`, including the in-memory `build_review_queue_entry` builder.
- candidate review gate contract tests.
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

## 3. Storage Strategy Decision

T002 decides the first storage strategy as a project-local stored queue entry read model linked to candidate records:

- Use project-local stored queue entry records only after tests authorize them.
- Do not treat queue storage as a replacement for candidate records.
- Queue entries reference candidate records by `candidate_record_id`.
- Queue entries duplicate only minimal display/read-model fields needed for the review workflow.
- Candidate records remain the source for candidate content, evidence, source locators, provenance, and candidate-only status.
- Queue entry storage is a review workflow index/read model, not truth storage.
- Queue entries must be rebuildable or repairable from candidate records where practical.
- Queue storage must never write memory/canon or apply promotion.

Local docs do not strongly prefer a derived-only queue view: `PHASE8-IMPL-011-T003` defined a concrete queue entry shape with required identity, lifecycle, and evidence fields, and `build_review_queue_entry` already emits that in-memory shape. A stored, candidate-linked read model is therefore the accepted future direction. Even so, the stored queue remains a derived workflow convenience: candidate records stay authoritative, and a derived-only rebuild path must always be possible. All safety boundaries in this decision apply regardless of whether the queue is stored or rebuilt on demand.

## 4. Storage Root and Path Boundary

Define the future storage root:

- `projects/{project_id}/writer_assistant/review_queue/`

Define the future files if queue entries are stored separately:

- `projects/{project_id}/writer_assistant/review_queue/entries/{queue_entry_id}.json`
- `projects/{project_id}/writer_assistant/review_queue/index.json`

Identity and path rules:

- `project_id` must be path-safe and validated.
- `queue_entry_id` must be path-safe and validated.
- `candidate_record_id` must be path-safe and validated.
- no absolute paths.
- no traversal.
- no backslashes.
- no Windows drive prefixes.
- no nested arbitrary user-provided path segments.
- no hidden dot-path IDs.
- `source_path_hint` remains debug/display metadata only and never a filesystem path.

Path-safety follows the existing `_require_path_safe` rules already used by `candidate_review_gate.py` and candidate storage helpers (reject empty/`.`/`..`, `/`, `\\`, leading `/`, `..` substrings, and Windows drive prefixes).

Forbidden locations:

- `memory/`
- `bible.json`
- `storyform.json`
- `project.json`
- `scenes/`
- `chapters/`
- `notes/`
- `materials/`
- `omi/promotions/`
- `training/`
- `dataset_manifest.json`
- JSONL files
- raw extraction artifact folders (for example `writer_assistant/extractions/`)
- `.external_sources/`
- `frontend/`
- backend route files
- package/dependency files

## 5. Queue Entry Stored Shape

Required stored queue entry fields:

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

Optional fields:

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
- `storage_version`
- `entry_hash`
- `candidate_snapshot_hash`

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
- `raw_artifact_write_intent`
- `training_destination`
- `jsonl_destination`

The required field set is aligned with the `PHASE8-IMPL-011-T003` queue entry shape and the in-memory output of `build_review_queue_entry`, plus optional storage-integrity fields (`storage_version`, `entry_hash`, `candidate_snapshot_hash`) that support drift detection without becoming truth.

## 6. Allowed Review Status and Lifecycle Values

Allowed `review_status` values:

- `pending`
- `needs_info`
- `rejected`
- `deferred`
- `duplicate`
- `superseded`
- `archived`

Allowed `lifecycle_state` values:

- `draft_ready_for_review`
- `needs_more_evidence`
- `blocked_invalid_support`
- `owner_review_pending`
- `owner_reviewed_rejected`
- `owner_reviewed_deferred`
- `duplicate_candidate`
- `superseded_candidate`
- `archived_without_promotion`

Clarifications:

- `approved` is not an allowed queue status in `PHASE8-IMPL-012`.
- `owner_reviewed_*` states do not mutate memory/canon.
- `archived_without_promotion` is not deletion and not promotion.
- queue lifecycle state is workflow state only.

These values match the `PHASE8-IMPL-011-T003` allowed sets and must not be widened to add positive approval/canon/promoted semantics in this parent.

## 7. Candidate Linkage and Integrity Rules

- Queue entries must reference exactly one candidate record.
- Queue entries must validate `candidate_record_id`.
- Queue entries must validate `project_id`.
- Queue entries must preserve `candidate_type` and `target_category` alignment (consistent with `candidate_schema.CORE_CANDIDATE_TARGET_CATEGORIES`).
- Queue entries must not create candidate records automatically.
- Queue entries must not mutate candidate records automatically.
- Queue entries must not mark candidates approved/canon/promoted.
- Queue entries must not prefill owner decisions beyond pending/undecided workflow terms.
- Queue entries must preserve source/evidence/provenance references.
- Queue entries with missing or invalid candidate records fail closed or are quarantined as invalid support.
- duplicate/conflict/related candidate IDs are references only, not merge actions.

## 8. Evidence and Provenance Requirements

Every stored queue entry must preserve or reference:

- source document identity
- source locator
- evidence summary
- evidence record references
- provenance summary
- provenance references
- raw output refs where applicable
- confidence as uncertainty, not approval
- normalization status
- `human_review_required`
- insufficient-evidence or rejected-output reason where applicable

Queue storage must not strip evidence/provenance to create a cleaner-looking task list. A queue entry that cannot preserve or reference its candidate record's source/evidence/provenance must fail closed or be quarantined as invalid support rather than be shown as review-ready.

## 9. Index Contract

Define the future index file:

- `projects/{project_id}/writer_assistant/review_queue/index.json`

The index should contain:

- `schema_version`
- `project_id`
- `generated_at` or `updated_at`
- `entries` list of minimal queue-entry summaries
- counts by `review_status`
- counts by `lifecycle_state`
- counts by `candidate_type`
- optional groups by `source_document` or `target_category`
- no canon/memory fields
- no owner approval fields
- no apply-promotion fields

Index entry summaries should include only:

- `queue_entry_id`
- `candidate_record_id`
- `candidate_type`
- `target_category`
- `review_status`
- `lifecycle_state`
- `confidence`
- `normalization_status`
- `human_review_required`
- `updated_at`

Clarifications:

- the index is derived workflow support only.
- index corruption must not affect candidate records.
- the index is rebuildable from queue entries (and, transitively, from candidate records).
- the index is not approval truth.

This mirrors the existing derived candidate index pattern in `candidate_index.py` (`writer_assistant/index.json` as derived convenience metadata only), keeping queue index behavior consistent with the candidate index boundary.

## 10. Storage Operation Boundary

Define future helper categories (planning names only; T004 may define the actual future API names through tests):

- `validate_review_queue_entry(entry: dict) -> dict`
- `build_review_queue_entry_from_candidate_record(candidate_record: dict, *, project_id: str) -> dict`
- `review_queue_storage_dir(project_dir) -> Path-like value or existing path helper output if allowed later`
- `review_queue_entry_path(project_dir, queue_entry_id) -> Path-like value or existing path helper output if allowed later`
- `write_review_queue_entry(entry, *, project_dir) -> dict`
- `read_review_queue_entry(queue_entry_id, *, project_dir) -> dict`
- `list_review_queue_entries(*, project_dir) -> list[dict]`
- `build_review_queue_index(entries, *, project_id: str) -> dict`

T002 does not implement these helpers.

Storage operation requirements:

- write/read/list helpers must stay project-local.
- write helpers must validate before writing.
- write helpers must fail closed with no partial writes where practical.
- read helpers must validate loaded entries.
- list helpers must validate entries or quarantine invalid support.
- index helpers must be derived and rebuildable.
- no owner actions are executed by storage helpers.
- no apply-promotion occurs.
- no memory/canon mutation occurs.
- no UI/API/routes are created.

## 11. Owner Action Relationship

- T002 defines storage only.
- `PHASE8-IMPL-012-T003` defines owner action workflow boundaries.
- Queue storage may store workflow status and reviewer notes only if T003 authorizes them.
- Queue storage must not store approval as canon truth.
- Owner action storage is not apply-promotion.
- Owner action storage is not memory/canon mutation.
- Review UI/API remains deferred.

## 12. Failure and Quarantine Policy

Fail closed or quarantine when:

- invalid `queue_entry_id`
- invalid `project_id`
- invalid `candidate_record_id`
- unsupported `review_status`
- unsupported `lifecycle_state`
- missing evidence/provenance/source locator
- invalid candidate linkage
- candidate record is approved/canon/promoted
- a forbidden destination appears
- an owner approval field appears
- apply-promotion intent appears
- a memory/canon path appears
- generated prose/rewrite/continuation appears
- raw artifact write intent appears
- runtime extraction/tool/model intent appears
- training/JSONL/dataset field appears
- unknown fields appear
- path traversal or unsafe path segments appear

No partial write should remain after failure unless future tests explicitly quarantine invalid data under a safe invalid-support folder. If quarantine is later used, it must be candidate-only, non-canon, and not approval.

## 13. T003 Handoff

`PHASE8-IMPL-012-T003` - Owner action workflow boundary decision.

T003 should decide:

- allowed owner action commands as planning terms
- allowed owner action states
- whether owner action notes are stored on queue entries or separate action records
- how owner actions relate to candidate records
- how rejected/deferred/needs-info/duplicate/superseded/archived states are represented
- how owner action workflow avoids approval/canon/promotion semantics
- whether any positive owner action label is allowed without apply-promotion
- no implementation
- no routes/UI
- no memory/canon mutation
- no apply-promotion

## 14. T004/T005 Handoff

`PHASE8-IMPL-012-T004` - Review queue storage contract tests.

T004 should:

- be tests-first only
- be expected-red if a future storage helper/module does not exist
- encode the T002 storage contract and the T003 owner action boundary
- use `tmp_path` only
- define future helper/API names
- test entry validation
- test storage paths
- test write/read/list/index if authorized
- test fail-closed unsupported or unsafe entries
- test no approval/canon/promoted status
- test no apply-promotion
- test no memory/canon mutation
- test no UI/API/routes
- test no raw artifact persistence
- test no generated prose
- add no implementation

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

## 15. Explicit Rejections

Reject:

- queue storage implementation in T002
- queue listing/loading implementation in T002
- owner action workflow implementation in T002
- review UI/API implementation in T002
- backend review routes
- frontend review UI
- automatic candidate approval
- queue entry as approval record
- approved/canon/promoted queue status
- owner decision prefill as approved
- apply-promotion
- memory/canon/storyform/bible/project/scenes/notes/materials writes
- raw artifact persistence
- runtime extraction
- real BookNLP/spaCy runtime
- package/dependency changes
- model calls
- generated prose/rewrite/continuation
- training/JSONL/dataset work

## 16. Accepted Decision

- ACCEPT project-local review queue storage as the future direction only after tests authorize it.
- ACCEPT queue entries as candidate-linked workflow support only.
- ACCEPT candidate records as the source of candidate content and candidate-only status.
- ACCEPT queue index as derived/rebuildable workflow support only.
- ACCEPT evidence/provenance/source locator preservation as mandatory.
- ACCEPT the allowed `review_status` and `lifecycle_state` values.
- ACCEPT fail-closed handling for unsafe or unsupported queue entries.
- ACCEPT `PHASE8-IMPL-012-T003` as the owner action workflow boundary decision.
- ACCEPT `PHASE8-IMPL-012-T004` as tests-first storage contract coverage.
- ACCEPT `PHASE8-IMPL-012-T005` as optional minimal helper implementation only if authorized.
- REJECT queue storage implementation in T002, review UI/API, owner-decision approval, apply-promotion, memory/canon mutation, raw persistence, runtime extraction, and generated prose.
