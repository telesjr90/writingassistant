# PHASE8-IMPL-016 Inventory

## 1. Task Identity

- Parent ID: `PHASE8-IMPL-016`
- Title: Frontend owner-action execution workflow and review command boundary
- Track: Writer Assistant Core
- Phase: Phase 8
- Status: active MVP-required parent; `PHASE8-IMPL-016-T001` complete/PASS; `PHASE8-IMPL-016-T002` complete/PASS; `PHASE8-IMPL-016-T003` complete/PASS as tests-first expected-red contract; `PHASE8-IMPL-016-T004` complete/PASS
- Depends on: completed `PHASE8-IMPL-015`
- Current child: `PHASE8-IMPL-016-T005` ready/active next
- Child sequence: T001 complete/PASS; T002 complete/PASS; T003 complete/PASS expected-red; T004 complete/PASS; T005 ready/active next; T006 planned; T007 planned
- Recommended next parent after this one: `PHASE8-IMPL-017` - Apply-promotion contract, audit log, and approved memory/canon mutation boundary

## 2. Why This Parent Exists

The read-only review queue work from `PHASE8-IMPL-015` established display-only access to review queue state, but the product still needs an explicit owner-action execution workflow before any review command boundary can be considered complete. This parent captures the MVP-required frontend owner-action execution workflow and its command boundary without authorizing silent promotion, direct canon mutation, raw artifact lifecycle changes, runtime extraction, model calls, or generated prose.

The parent was docs/status/planning only at T001. T002 accepted the owner-action review command decision. T003 added the expected-red review command route contract for future owner-action candidate review commands, without implementing runtime behavior. Later children can author backend helper wiring, frontend workflow surface, and safety regression in controlled steps.

T003/T004 contract coverage:

- future `POST /api/projects/{project_id}/review-queue/{queue_entry_id}/actions` route
- allowed review command validation for `mark_reviewed`, `request_more_evidence`, `defer`, `reject`, `quarantine`, `update_owner_note`, and `set_review_status`
- forbidden command rejection for `apply_promotion`, `promote_candidate`, `write_memory`, `write_canon`, `persist_raw_artifact`, `run_extraction`, `run_booknlp`, `run_spacy`, `call_model`, `generate_prose`, `rewrite_prose`, `continue_scene`, and `create_training_jsonl`
- fail closed malformed/unsafe payload behavior, including queue/candidate mismatch and unsafe write-target fields
- route separation from read-only GET review queue routes and no apply-promotion route in this parent
- response boundary with review workflow state only, candidate linkage, evidence/provenance/source locator preservation, no silent promotion, no apply-promotion, no memory/canon mutation, no raw artifact persistence, no runtime extraction, no model calls, and no generated prose
- T004 minimal backend implementation of the command route/helper as response-only review workflow command acceptance/rejection, with no queue persistence, candidate persistence, apply-promotion, memory/canon mutation, project truth mutation, raw artifact persistence, runtime extraction, model calls, generated prose, or training artifact creation

## 3. Boundary Summary

Allowed in this parent:

- owner-action execution workflow planning
- review command taxonomy and sequencing
- explicit owner-confirmed review actions
- request boundary and response boundary definition for review workflow commands
- fail-closed/no silent promotion language
- frontend owner-action workflow/surface planning

Forbidden in this parent:

- apply-promotion
- approved memory/canon mutation
- direct canon mutation
- raw artifact persistence lifecycle changes
- runtime extraction
- model calls
- generated prose
- backend command route behavior beyond response-only review workflow command acceptance/rejection
- frontend runtime implementation beyond planning/artifacts in later children

## 4. MVP Relation

`PHASE8-IMPL-016` is MVP-required and active. It sequences the owner-action execution boundary that the MVP needs before promotion and canon mutation can be added in `PHASE8-IMPL-017`.

## 5. Cross-References

- Prior parent: `PHASE8-IMPL-015` - review API route implementation and read-only frontend review queue surface
- Next MVP-required parents: `PHASE8-IMPL-017`, `PHASE8-IMPL-018`, `PHASE8-IMPL-019`, `PHASE8-IMPL-020`, `PHASE8-IMPL-021`, `PHASE8-IMPL-022`
