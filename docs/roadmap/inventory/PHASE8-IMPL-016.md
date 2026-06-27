# PHASE8-IMPL-016 Inventory

## 1. Task Identity

- Parent ID: `PHASE8-IMPL-016`
- Title: Frontend owner-action execution workflow and review command boundary
- Track: Writer Assistant Core
- Phase: Phase 8
- Status: complete/PASS through `PHASE8-IMPL-016-T007`
- Depends on: completed `PHASE8-IMPL-015`
- Current child: none; parent closed after T007
- Child sequence: T001 complete/PASS; T002 complete/PASS; T003 complete/PASS expected-red then PASS after T004; T004 complete/PASS; T005 complete/PASS; T006 complete/PASS; T007 complete/PASS
- Recommended next parent: `PHASE8-IMPL-017` - Apply-promotion contract, audit log, and approved memory/canon mutation boundary (MVP-required; ready/active pending T001 publication)

## 2. Why This Parent Exists

The read-only review queue work from `PHASE8-IMPL-015` established display-only access to review queue state, but the product still needed an explicit owner-action execution workflow before any review command boundary could be considered complete. This parent captured the MVP-required frontend owner-action execution workflow and its command boundary without authorizing silent promotion, direct canon mutation, raw artifact lifecycle changes, runtime extraction, model calls, or generated prose.

The parent was docs/status/planning only at T001. T002 accepted the owner-action review command decision. T003 added the expected-red review command route contract. T004 implemented the minimal backend route/helper. T005 added the frontend workflow/surface. T006 added focused safety regression coverage. T007 closed the parent as docs/status only.

T003/T004/T005/T006 contract and implementation coverage:

- `POST /api/projects/{project_id}/review-queue/{queue_entry_id}/actions` route
- allowed review command validation for `mark_reviewed`, `request_more_evidence`, `defer`, `reject`, `quarantine`, `update_owner_note`, and `set_review_status`
- forbidden command rejection for `apply_promotion`, `promote_candidate`, `write_memory`, `write_canon`, `persist_raw_artifact`, `run_extraction`, `run_booknlp`, `run_spacy`, `call_model`, `generate_prose`, `rewrite_prose`, `continue_scene`, and `create_training_jsonl`
- fail closed malformed/unsafe payload behavior, including queue/candidate mismatch and unsafe write-target fields
- route separation from read-only GET review queue routes and no apply-promotion route in this parent
- response boundary with review workflow state only, candidate linkage, evidence/provenance/source locator preservation, no silent promotion, no apply-promotion, no memory/canon mutation, no raw artifact persistence, no runtime extraction, no model calls, and no generated prose
- T004 minimal backend implementation of the command route/helper as response-only review workflow command acceptance/rejection, with no queue persistence, candidate persistence, apply-promotion, memory/canon mutation, project truth mutation, raw artifact persistence, runtime extraction, model calls, generated prose, or training artifact creation
- T005 minimal frontend workflow/surface with a deterministic helper for `POST /api/projects/{project_id}/review-queue/{queue_entry_id}/actions`, read-only candidate details separated from explicit owner-action controls, candidate-only/no-canon warning text, evidence/provenance/source locator context display and payload preservation, fail-closed unsupported command/missing ID behavior, and no apply-promotion, memory/canon/project truth mutation, raw artifact persistence, runtime extraction, model calls, generated prose, or training artifact creation
- T006 focused safety regression coverage proving the backend route remains response-only review workflow state, forbidden owner-action commands and payload fields fail closed, frontend controls expose only allowed review workflow commands with explicit owner confirmation and candidate-only/no-canon/evidence/provenance/source locator context, and the targeted source boundary scan distinguishes rejected fixtures from implementation behavior without the earlier contradictory forbidden-substring issue

## 3. Boundary Summary

Allowed in this parent:

- owner-action execution workflow planning
- review command taxonomy and sequencing
- explicit owner-confirmed review actions
- request boundary and response boundary definition for review workflow commands
- fail-closed/no silent promotion language
- frontend owner-action workflow/surface implementation for bounded review commands
- minimal backend command route/helper for response-only review workflow command acceptance/rejection
- focused safety regression coverage for owner-action workflow boundaries

Forbidden in this parent:

- apply-promotion
- approved memory/canon mutation
- direct canon mutation
- raw artifact persistence lifecycle changes
- runtime extraction
- model calls
- generated prose
- queue/candidate persistence from command route
- project truth mutation from command route

## 4. MVP Relation

`PHASE8-IMPL-016` is MVP-required and complete/PASS. It delivered the owner-action execution boundary the MVP needed before promotion and canon mutation can be added in `PHASE8-IMPL-017`.

## 5. Cross-References

- Prior parent: `PHASE8-IMPL-015` - review API route implementation and read-only frontend review queue surface
- Next MVP-required parents: `PHASE8-IMPL-017`, `PHASE8-IMPL-018`, `PHASE8-IMPL-019`, `PHASE8-IMPL-020`, `PHASE8-IMPL-021`, `PHASE8-IMPL-022`

## 6. Tracked Artifacts (T004/T005/T006)

Confirmed changed/created implementation and test artifacts from T004/T005/T006 closeout review:

- `backend/review_api.py` (owner-action command validation/response helpers used by command route)
- `backend/routes/review_queue.py` (added `POST /api/projects/{project_id}/review-queue/{queue_entry_id}/actions`)
- `frontend/src/api.js` (deterministic owner-action review command helper)
- `frontend/src/App.jsx` (review queue panel wiring)
- `frontend/src/components/ReviewQueuePanel.jsx` (candidate-only review queue surface)
- `frontend/src/components/OwnerActionReviewControls.jsx` (explicit owner-action review controls)
- `frontend/src/styles.css` (review workflow surface styling)
- `tests/test_writer_assistant_review_action_command_routes_contract.py` (command route contract; PASS after T004)
- `tests/test_frontend_owner_action_review_workflow_source.py` (frontend source boundary tests)
- `tests/test_frontend_project_workspace_source.py` (existing frontend source regression)
- `tests/test_owner_action_review_workflow_safety_regression.py` (T006 focused safety regression)

Confirmed absent from this parent:

- apply-promotion implementation or routes
- approved memory/canon mutation helpers or routes
- raw artifact persistence lifecycle writes
- runtime extraction, BookNLP/spaCy install/run/import, or model calls
- generated prose or prose-production behavior
- training/JSONL/dataset/model artifacts
- package or dependency file changes

Generated context artifacts remain evidence only and must not be treated as roadmap truth:

- `.codex-context/PHASE8-IMPL-016/` (ignored)
- `ai_context/repomix-current-task-context.xml` (ignored; evidence only)
