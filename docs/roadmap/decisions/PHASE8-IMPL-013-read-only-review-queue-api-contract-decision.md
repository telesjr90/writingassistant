# PHASE8-IMPL-013 Read-Only Review Queue API Contract Decision

## 1. Decision Summary

- `PHASE8-IMPL-013-T002` accepts the read-only review queue API contract as docs/decision only.
- A future read-only review queue API contract should be defined before any frontend review UI, but no backend routes are implemented in T002.
- Any future review queue API operations must be read-only (HTTP GET / read-model only) and review-workflow-only; they must never mutate queue entries, candidate records, memory, canon, project source files, raw artifacts, or indexes.
- Queue entries and candidate records remain candidate-only and review-pending. Queue presence is not approval, high confidence is not truth, and a valid API response is not owner approval.
- The future API must expose evidence, provenance, uncertainty, normalization status, and `human_review_required`, and must never expose approval, canon, promotion, apply-promotion, owner action execution results, generated prose, route/model/runtime triggers, or arbitrary filesystem paths.
- The read-only review queue API stays separate from owner action command execution (decided in `PHASE8-IMPL-013-T003`), from apply-promotion, from memory/canon mutation, and from runtime extraction.
- Failures fail closed with safe error/quarantine responses and never repair by writing state.
- T002 does not implement routes, FastAPI endpoints, frontend API helpers, frontend review UI, owner action command API, owner action execution, apply-promotion, memory/canon mutation, raw artifact persistence, or runtime extraction.

## 2. Evidence Reviewed

T002 reviewed local repository evidence only:

- `PHASE8-IMPL-013-T001` parent publication in `docs/roadmap/tasks/PHASE8-IMPL-013.md`, `docs/roadmap/inventory/PHASE8-IMPL-013.md`, and `docs/roadmap/enrichment/PHASE8-IMPL-013.enrichment.json`.
- `PHASE8-IMPL-012-T002` review queue storage contract decision in `docs/roadmap/decisions/PHASE8-IMPL-012-review-queue-storage-contract-decision.md`.
- `PHASE8-IMPL-012-T003` owner action workflow boundary decision in `docs/roadmap/decisions/PHASE8-IMPL-012-owner-action-workflow-boundary-decision.md`.
- `backend/story_knowledge/review_queue_storage.py`, including `validate_review_queue_entry`, `build_review_queue_entry_from_candidate_record`, `review_queue_storage_dir`, `review_queue_entry_path`, `review_queue_index_path`, `write_review_queue_entry`, `read_review_queue_entry`, `list_review_queue_entries`, `build_review_queue_index`, and `validate_owner_action_record`.
- `tests/test_writer_assistant_core_review_queue_storage_contract.py` review queue storage contract tests.
- `backend/story_knowledge/candidate_review_gate.py` and `tests/test_writer_assistant_core_candidate_review_gate_contract.py`.
- `backend/story_knowledge/candidate_schema.py`, `backend/story_knowledge/candidate_record.py`, `backend/story_knowledge/candidate_storage.py`, `backend/story_knowledge/candidate_persistence.py`, and `backend/story_knowledge/candidate_index.py`.
- `backend/story_knowledge/extraction_orchestrator.py`, `backend/story_knowledge/source_map.py`, and `backend/story_knowledge/evidence.py`.
- Current roadmap truth files (`docs/roadmap/implementation_status.md`, `docs/roadmap/roadmap_index.yaml`, `docs/roadmap/task_backlog.md`, `docs/roadmap/phase_map.md`, `docs/master_plan.md`), `docs/roadmap/validation/latest_roadmap_validation.md`, `docs/roadmap/decision_log.md`, `docs/roadmap/risk_register.md`, `docs/roadmap/open_questions.md`, and `docs/roadmap/roadmap_governance.md`.

Confirmed from local files:

- No backend review routes exist; `review_queue` appears only in `backend/story_knowledge/review_queue_storage.py` and `backend/story_knowledge/candidate_review_gate.py`, not in any route file.
- No frontend review UI exists; `frontend/src/api.js` has no review queue helper.
- No owner action command API or owner action execution exists beyond `validate_owner_action_record` shape validation.
- No apply-promotion, memory/canon mutation, raw artifact persistence, or runtime extraction exists in this pipeline.
- `.external_sources/` remains ignored and not staged.

Record:

- no runtime code changes
- no tests changed
- no web research
- no external tool execution
- no model calls
- no BookNLP/spaCy runtime

## 3. API Purpose

The future read-only review queue API exists to:

- let an owner inspect candidate-linked review queue entries that the `PHASE8-IMPL-012` queue storage helper can store, list, and index;
- present each entry with its evidence, provenance, source identity/locator, uncertainty, normalization status, and `human_review_required` so the owner can review candidate support;
- expose review workflow status (`review_status`) and lifecycle workflow state (`lifecycle_state`) as non-approval workflow metadata only;
- support a future review UI with read models, summaries, and an index view;
- keep candidate records authoritative and queue entries derived workflow support only.

The API never establishes project truth. Reading a queue entry is not approving it. The API is a review surface, not an approval, canon, promotion, or apply-promotion path.

## 4. Backend Route Timing Decision

- Decision: define the read-only review queue API contract first, before any frontend review UI, but do not implement routes in T002.
- Rationale: the queue storage helper already produces a stable, validated read model. Defining the read contract first lets `PHASE8-IMPL-013-T004` (review UI planning) and any future tests/implementation depend on a fixed, evidence-backed, non-approval contract rather than improvising routes underneath a UI.
- The contract is read-only and review-workflow-only. It is the read half of the review surface; the owner action command API (write/command half) is a separate decision in `PHASE8-IMPL-013-T003`.
- Future route implementation remains deferred until `PHASE8-IMPL-013-T005` tests (if authorized) and a later owner-approved implementation task explicitly authorize it.
- No FastAPI endpoint, router, or frontend API helper is created in T002.

## 5. Read-Only Operation Set

Define future operation names as planning terms only (not implemented in T002):

- `list_review_queue_entries_readonly`
- `get_review_queue_entry_readonly`
- `get_review_queue_index_readonly`
- `get_review_queue_filters_readonly`
- `get_review_queue_summary_readonly`

If future HTTP route examples are used, they must remain future-only and read-only (GET only), consistent with existing `/api/projects/{project_id}/...` conventions:

- `GET /api/projects/{project_id}/review-queue`
- `GET /api/projects/{project_id}/review-queue/{queue_entry_id}`
- `GET /api/projects/{project_id}/review-queue/index`
- `GET /api/projects/{project_id}/review-queue/summary`

These routes are planning illustrations only. T002 does not implement them. No POST/PUT/PATCH/DELETE or any mutation verb is defined for the read-only review queue API; mutation/command verbs belong to the separate owner action command API decided in T003.

The read operations map onto the existing pure helpers as a future read layer:

- list/get/index operations would read through `list_review_queue_entries`, `read_review_queue_entry`, and `build_review_queue_index`-style derived output;
- summary/filters operations would derive counts and allowed-value metadata from validated entries only;
- no read operation may create, mutate, repair, or delete queue entries, candidate records, indexes, or any project file.

## 6. Request and Query Contract

Allowed read parameters only:

- `project_id` (path parameter, path-safe and validated)
- `queue_entry_id` (path parameter for single-entry reads, path-safe and validated)
- `review_status` filter (allowlist from the queue storage allowed `review_status` values)
- `lifecycle_state` filter (allowlist from the queue storage allowed `lifecycle_state` values)
- `candidate_type` filter (allowlist from `candidate_schema.CORE_CANDIDATE_TYPES`)
- `target_category` filter (allowlist from `candidate_schema.CORE_CANDIDATE_TARGET_CATEGORIES`)
- `normalization_status` filter
- `has_raw_refs` filter (boolean over presence of `raw_output_refs`)
- `confidence_min` / `confidence_max` as uncertainty filters only (bounded 0.0-1.0)
- `sort_by` from a fixed allowlist (see Section 11)
- `sort_direction` from a fixed allowlist (`asc`, `desc`)
- `limit` / `offset` or cursor-style pagination (planning only)

Reject (request must fail closed):

- `owner_decision` writes
- `review_status` mutation
- `lifecycle_state` mutation
- `action_command` execution
- approve/promote/canon flags
- apply-promotion intent
- memory/canon destination
- raw artifact write/read intent beyond safe references
- runtime/model/tool intent
- generated prose/rewrite/continuation fields
- path fields
- filesystem paths
- arbitrary project file paths
- unknown query/path fields

`confidence_min`/`confidence_max` are uncertainty filters, not truth ranking. Filters narrow what is displayed for workflow convenience and never imply approval, rejection, deletion, or canon. Any unknown, unsafe, or mutation-shaped parameter fails closed (see Section 12).

## 7. Response Shape Contract

The response must expose only review-workflow support fields:

- `schema_version`
- `project_id`
- queue entries (list operations) or a single queue entry (single-entry operation)
- `queue_entry_id`
- `candidate_record_id`
- `candidate_type`
- `target_category`
- `review_status`
- `lifecycle_state`
- `confidence` (as uncertainty)
- `uncertainty_flags`
- `normalization_status`
- `human_review_required`
- `evidence_summary`
- `evidence_refs`
- `provenance_summary`
- `provenance_refs`
- `source_document` summary/ref
- `source_locator` summary/ref
- `raw_output_refs` as support-only references
- `created_at`
- `updated_at`
- pagination/index/summary metadata (counts by `review_status`, `lifecycle_state`, `candidate_type`)

The response must never expose:

- approved status
- canon truth
- memory writes
- promoted state
- apply-promotion triggers
- owner action execution results
- generated prose
- route triggers
- model calls
- runtime extraction triggers
- raw artifact persistence commands
- filesystem paths, except safe display/debug path hints already accepted by source contracts (`source_path_hint` remains debug/display-only metadata, never a filesystem path input/output)

The response read model is aligned with the `PHASE8-IMPL-012` stored queue entry shape and its derived index summary. The API may project or summarize entry fields but must not add positive approval/canon/promotion semantics, must not strip required evidence/provenance support, and must not return any field outside the validated queue entry/index/summary shape.

## 8. Queue Entry Exposure Rules

- Queue entries are workflow support only.
- Queue presence is not approval; appearing in the queue or in a response page does not establish truth.
- High confidence is not truth; `confidence` is uncertainty metadata only.
- Response validity is not owner approval; a well-formed response is not a decision.
- The read-only API cannot mutate queue entries, candidate records, memory, canon, project source files, raw artifacts, or indexes.
- The read-only API must not introduce or reflect `approved`, `promoted`, `canon`, `memory_destination`, `apply_promotion`, or owner-decision-approved fields, consistent with the forbidden fields in the `PHASE8-IMPL-012` storage contract.
- Allowed `review_status` and `lifecycle_state` values are exactly those accepted by `validate_review_queue_entry`; the API must not widen them to add approval/canon/promoted semantics.
- Entries that fail validation, lack required support, or carry forbidden fields must not be presented as review-ready (see Sections 9, 10, and 12).

## 9. Candidate Record Exposure Rules

- Candidate records remain the source of candidate content and candidate-only status; queue entries reference candidate records by `candidate_record_id`.
- The read-only API may expose candidate-linked summary/read-model fields needed for review but must not present candidate records as approved, canon, promoted, or owner-approved.
- The API must not create candidate records, mutate candidate records, or change candidate status through any read operation.
- If a queue entry references a missing, invalid, approved, promoted, or canon candidate record, the entry fails closed or is presented through a safe quarantine/error response, not as a clean review-ready entry (see Section 12).
- Candidate exposure must preserve candidate-only/review-pending framing and never imply durable project truth.

## 10. Evidence and Provenance Display Requirements

The future API must preserve and make available:

- source identity (`source_document`)
- source locator (`source_locator`)
- evidence references (`evidence_refs`) and evidence summary (`evidence_summary`)
- provenance references (`provenance_refs`) and provenance summary (`provenance_summary`)
- raw refs where applicable (`raw_output_refs`) as support-only references
- normalization status (`normalization_status`)
- insufficient-evidence or rejected-output reasons where applicable (`insufficient_evidence_reason`, `rejected_output_reason`)
- `human_review_required`
- explicit no-promotion / no-canon messaging in any future surface

The API must not strip evidence/provenance to create a cleaner-looking task list. A queue entry that cannot preserve or reference its candidate record's source/evidence/provenance must fail closed or be quarantined as invalid support rather than be exposed as review-ready. Confidence is displayed as uncertainty, not approval.

## 11. Filtering, Sorting, and Pagination Boundary

- Filtering, sorting, and pagination are allowed for workflow convenience only.
- `sort_by` allowlist (planning): `confidence`, `created_at`, `updated_at`, `candidate_type`, `review_status`, `lifecycle_state`, `queue_entry_id`.
- `sort_direction` allowlist (planning): `asc`, `desc`.
- Sorting by confidence, created_at, updated_at, type, status, or lifecycle is not a truth ranking; it is display ordering only.
- Pagination cannot hide insufficient-evidence warnings, invalid-support indicators, or `human_review_required` state; summaries and per-entry support fields must remain accurate across pages.
- Filters cannot imply approval or rejection by omission; an entry excluded by a filter is not deleted, rejected, approved, or promoted.
- Default ordering should be deterministic (for example by `queue_entry_id`, consistent with `list_review_queue_entries` and `build_review_queue_index` ordering) so paging is stable.

## 12. Error and Quarantine Response Policy

Fail closed for:

- unsafe `project_id` or `queue_entry_id`
- invalid filters
- unknown query fields
- invalid pagination parameters
- malformed stored queue entries
- missing linked candidate record
- invalid candidate linkage
- approved/canon/promoted candidate records
- missing evidence/provenance/source locator
- forbidden request fields
- path traversal
- raw/runtime/model/tool/prose intent in the request

The future read-only API may return safe, structured error/quarantine responses (for example a not-found, invalid-request, or invalid-support indication) so a review UI can show the problem honestly. It must not repair by writing unless a later task explicitly authorizes repair. No read operation may create, overwrite, rebuild, or delete queue entries, candidate records, indexes, or any project file as a side effect of an error. Error responses must not leak filesystem paths beyond safe display/debug hints already accepted by source contracts.

## 13. Owner Action API Separation

- T002 does not define or implement the owner action command API.
- `PHASE8-IMPL-013-T003` decides the owner action command API contract.
- The read-only queue API cannot execute commands.
- The read-only queue API cannot update `review_status` or `lifecycle_state`.
- The read-only queue API cannot create owner action records.
- The read-only queue API cannot write reviewer notes.
- The read API and the future owner action command API are separate surfaces: reads never carry command/mutation intent, and any command behavior belongs solely to the T003 decision and a later authorized implementation.

## 14. Apply-Promotion Boundary

- The read-only review queue API is not apply-promotion.
- No route or response may perform or imply promotion.
- Any future apply-promotion remains separate, owner-approved, audited, explicit, and separately tested, and must not be hidden inside the review queue API.
- The read API must not expose apply-promotion triggers, promoted state, or canon destinations, consistent with the `PHASE8-IMPL-012` apply-promotion boundary.

## 15. Memory/Canon Boundary

- No read-only review queue API route may write `memory/*.json`, `memory/index.json`, `bible.json`, `storyform.json`, `project.json`, scenes, chapters, notes, materials, or owner-authored source files.
- An API response is not approved truth.
- The read API exposes candidate-only/review-pending workflow data and must never present or produce approved memory/canon records.

## 16. Runtime Extraction and Raw Artifact Boundary

- No runtime extraction is performed or triggered by the read-only review queue API.
- No BookNLP/spaCy run or import is involved.
- No raw artifact persistence occurs; the API adds no raw write/read/list helpers.
- `raw_output_refs` are exposed as support-only metadata references, not as raw artifact read/write commands.
- The read API must not include any model/tool/runtime trigger field or behavior.

## 17. Review UI Relationship

- T002 may describe what a future review UI needs from the read-only API but does not implement UI.
- `PHASE8-IMPL-013-T004` decides the review UI planning boundary.
- A future review UI must show non-approval status, must display evidence/provenance/uncertainty and `human_review_required`, and must show no-promotion / no-canon warnings.
- UI needs from the read API include: a list view with filters/sort/pagination, a single-entry detail view with full evidence/provenance/source locator and uncertainty, an index/summary view with counts by status/lifecycle/type, and clear candidate-vs-canon and non-approval labeling.
- The UI must not imply that queue presence, confidence ranking, or a valid response is approval or canon.

## 18. Security and Path Safety Boundary

- The future API must use path-safe project/queue/candidate IDs, consistent with the `_require_safe_id` rules already used by `review_queue_storage.py` (reject empty/`.`/`..`, `/`, `\`, leading `/`, dot-path IDs, and Windows drive prefixes).
- `source_path_hint` remains debug/display-only and is never a filesystem path input.
- No arbitrary path inputs are accepted.
- No direct filesystem paths appear in request parameters.
- Path traversal and unsafe identifiers fail closed (see Section 12).

## 19. T003 Handoff

`PHASE8-IMPL-013-T003` - Owner action command API contract decision.

T003 should decide:

- accepted/rejected owner action commands (aligned with the `PHASE8-IMPL-012-T003` allowed commands/states)
- command input shape
- result shape
- actor/audit fields
- fail-closed behavior
- no apply-promotion
- no memory/canon mutation
- no generated prose
- no runtime extraction
- no owner action execution in T003

The owner action command API is the separate write/command surface that complements this read-only API; the two contracts must stay structurally separate.

## 20. T004/T005/T006 Handoff

- `PHASE8-IMPL-013-T004` - Review UI planning boundary decision, docs/decision only. Must require non-approval status, evidence/provenance/uncertainty display, and no-promotion warnings, and keep UI implementation deferred.
- `PHASE8-IMPL-013-T005` - Review API/UI contract tests if authorized, tests-first expected-red only. Should encode the T002 read-only contract (and T003/T004 boundaries), use `tmp_path` for any filesystem assertions, and add no route/UI implementation, apply-promotion, or memory/canon mutation.
- `PHASE8-IMPL-013-T006` - Safety regression or conditional hardening decision, no implementation unless authorized by prior tasks and owner scope. Should validate no review UI/API, no backend routes, no owner action execution, no apply-promotion, no memory/canon mutation, and no generated prose.

## 21. Explicit Rejections

Reject in T002:

- route implementation
- FastAPI endpoint implementation
- frontend API helper implementation
- frontend review UI
- owner action command API implementation
- owner action execution
- queue mutation through the read API
- candidate mutation through the read API
- owner decision writes
- approval/canon/promoted states
- apply-promotion
- memory/canon mutation
- raw artifact persistence
- runtime extraction
- real BookNLP/spaCy runtime
- package changes
- model calls
- generated prose/rewrite/continuation
- training/JSONL/dataset work

## 22. Accepted Decision

- ACCEPT defining the read-only review queue API contract before frontend review UI, without implementing routes in T002.
- ACCEPT the read-only operation set as planning terms only (`list_review_queue_entries_readonly`, `get_review_queue_entry_readonly`, `get_review_queue_index_readonly`, `get_review_queue_filters_readonly`, `get_review_queue_summary_readonly`) with GET-only future route examples.
- ACCEPT the safe read request/query parameters and the fail-closed rejection of all mutation/command/path/unknown parameters.
- ACCEPT the read-only response shape exposing evidence/provenance/uncertainty/normalization/`human_review_required` and forbidding approval/canon/promotion/apply-promotion/execution/prose/trigger fields.
- ACCEPT queue entries and candidate records as candidate-only/review-pending; queue presence, high confidence, and response validity are not approval.
- ACCEPT mandatory evidence/provenance/source-locator preservation and honest insufficient-evidence/rejected-output labeling.
- ACCEPT filtering/sorting/pagination as workflow convenience only, never truth ranking, never approval/rejection by omission, and never hiding insufficient-evidence warnings.
- ACCEPT fail-closed error/quarantine responses that never repair by writing.
- ACCEPT separation from the owner action command API (T003), apply-promotion, memory/canon mutation, and runtime extraction.
- ACCEPT `PHASE8-IMPL-013-T003` as the owner action command API contract decision, `PHASE8-IMPL-013-T004` as the review UI planning boundary decision, `PHASE8-IMPL-013-T005` as tests-first review API/UI contract coverage if authorized, and `PHASE8-IMPL-013-T006` as safety regression or conditional hardening.
- REJECT route implementation, FastAPI endpoints, frontend API helpers, frontend review UI, owner action command API, owner action execution, queue/candidate mutation through the read API, owner decision writes, approval/canon/promoted states, apply-promotion, memory/canon mutation, raw artifact persistence, runtime extraction, real BookNLP/spaCy runtime, package changes, model calls, generated prose/rewrite/continuation, and training/JSONL/dataset work in T002.
