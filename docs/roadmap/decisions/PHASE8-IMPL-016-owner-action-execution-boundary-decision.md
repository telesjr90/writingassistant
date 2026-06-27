# PHASE8-IMPL-016 Owner-Action Execution Boundary Decision

## Status

Accepted for `PHASE8-IMPL-016-T002`.

This decision is documentation only. It defines the owner-action execution boundary for the future review command workflow and does not implement runtime behavior, backend routes, frontend controls, tests, apply-promotion, approved memory/canon mutation, raw artifact persistence, runtime extraction, model calls, or generated prose.

## Purpose

Owner-action execution in `PHASE8-IMPL-016` means owner-confirmed review workflow commands for candidate review.

Commands affect review workflow state only. They may mark, annotate, defer, reject, or quarantine candidate review items inside bounded review state, but they do not apply promotion, mutate approved memory/canon, create raw artifacts, run extraction or models, or generate prose.

The boundary preserves the existing product rule that review queue entries and candidates are not canon. Queue presence, candidate presence, confidence, review status, and command acceptance are workflow facts only. They are not approval, not promotion, and not project truth.

## Allowed Command Taxonomy

`PHASE8-IMPL-016` allows safe review-workflow commands only. Existing earlier terms remain preferred where they do not violate current MVP boundaries.

Allowed command families:

- mark reviewed / acknowledge: owner-confirmed acknowledgement that the candidate was reviewed, without approving or promoting it
- request more evidence / `request_more_evidence` / `mark_needs_info`: move the review item to a needs-evidence workflow state
- defer / `defer_review`: leave the candidate pending for later review
- reject / `reject_candidate`: reject the candidate as a candidate-only review item without mutating canon
- quarantine / flag unsafe or malformed candidate / `blocked_invalid_support`: record invalid support, malformed payload, unsafe intent, or candidate/queue mismatch as review workflow metadata only
- update review note / owner rationale metadata / `add_reviewer_note` / `clear_reviewer_note`: preserve owner-authored rationale or clear it without rewriting candidate content
- set review workflow status where bounded to non-canon review state: for example `pending`, `needs_info`, `deferred`, `rejected`, `duplicate`, `superseded`, `archived_without_promotion`, `blocked_invalid_support`, or another explicitly non-canon review workflow state

Optional prior terms such as `mark_duplicate`, `mark_superseded`, `archive_without_promotion`, and `edit_queue_metadata` remain allowed only as review workflow metadata commands. They cannot change candidate content, approved memory/canon, source files, raw artifacts, or project truth.

No allowed command may silently promote a candidate. No allowed command may be treated as apply-promotion.

## Forbidden Command Taxonomy

The following commands, intents, payloads, and effects are forbidden in `PHASE8-IMPL-016`:

- `apply-promotion`
- promote candidate into approved memory/canon
- write to approved memory/canon
- mutate bible, storyform, scenes, notes, materials, project metadata, owner-authored source files, or any other project truth
- persist raw extraction artifacts
- run runtime extraction
- install, run, or import BookNLP or spaCy
- call models or Ollama
- model-assisted extraction
- NCP/Subtxt/dramatica-flow runtime execution
- generate, rewrite, continue, imitate, polish, improve, expand, outline, draft, revise, or produce story prose
- create training data, JSONL files, datasets, model artifacts, or training manifests

Rejected command names include `approve_candidate`, `promote_candidate`, `write_to_memory`, `write_to_canon`, `apply_promotion`, `generate_prose`, `rewrite_source`, `continue_scene`, `run_extractor`, `persist_raw_artifact`, and any unknown or unsupported future command.

## Request Boundary

A future review command request should contain only the fields needed to validate and record a bounded review workflow action.

Expected future request shape in prose:

- `project_id`
- `queue_entry_id` or `candidate_id`, as applicable
- `action_type`
- `actor` or an owner confirmation marker
- explicit confirmation where the action changes review workflow state, rejects, defers, quarantines, or records owner rationale
- `owner_note` or rationale metadata when supplied by the owner
- expected current review status/version if available, so stale commands fail closed
- evidence, provenance, and source locator preservation requirements or references

The request must not include a payload field that can directly write canon, approved memory, bible, storyform, scenes, notes, materials, project truth, raw artifacts, generated prose, training data, JSONL, datasets, model artifacts, or training manifests.

The request boundary must preserve immutable candidate linkage. A command may identify the candidate or queue entry under review, but it cannot rewrite candidate content or convert candidate state into approved truth.

## Response Boundary

A future review command response should report command acceptance or rejection and updated review workflow state only.

Expected future response shape in prose:

- command accepted or rejected
- updated review workflow state only
- immutable candidate linkage
- preserved evidence/provenance/source locator context or references
- no canon mutation result
- no apply-promotion result
- no raw artifact result
- warnings that queue state, candidate state, and review status are not canon
- fail closed errors for unsafe, unknown, malformed, unsupported, stale, mismatched, or out-of-scope commands

The response must not imply approval, project truth, canon mutation, memory/canon writes, apply-promotion, raw artifact persistence, runtime extraction, model output, generated prose, or training-data creation.

## Frontend Workflow Boundary

Frontend owner-action workflow in `PHASE8-IMPL-016` must keep read-only candidate details separate from command controls.

Future UI expectations:

- read-only candidate details remain visually and behaviorally separate from owner command controls
- command controls require explicit owner action and must not silently execute commands
- dangerous or irreversible future actions are not part of `PHASE8-IMPL-016`
- UI displays candidate-only and no-canon warnings
- UI preserves evidence, provenance, source locator, raw-ref-as-support, and uncertainty context
- UI exposes no prose-generation controls
- UI does not imply queue presence, confidence, or review status equals truth
- UI does not present apply-promotion, approved memory/canon mutation, raw artifact persistence, runtime extraction, model calls, or generated-prose controls

Reviewer notes are owner-authored rationale metadata only. They must not be generated, rewritten, polished, improved, expanded, or converted into story prose.

## Backend Route/Helper Sequencing

This decision defines future sequencing only:

- `PHASE8-IMPL-016-T003`: tests-first command boundary contract for review actions without promotion/canon mutation; expected-red route/helper contract where implementation is absent
- `PHASE8-IMPL-016-T004`: minimal backend command route/helper implementation for review-action execution only, if authorized by T003
- `PHASE8-IMPL-016-T005`: frontend owner-action workflow/surface implementation or planning path, depending on existing frontend harness/package constraints
- `PHASE8-IMPL-016-T006`: safety regression for no silent promotion, no memory/canon mutation, no generated prose, no model/runtime/raw persistence, and fail-closed unsafe commands
- `PHASE8-IMPL-016-T007`: parent closeout

T003 should keep the command route separate from read-only GET routes. T004, if authorized, is limited to review-action execution only and cannot implement apply-promotion or approved memory/canon mutation.

## Future Parent Deferrals

This decision does not authorize the deferred MVP-required parents:

- apply-promotion remains `PHASE8-IMPL-017`
- approved memory/canon mutation remains `PHASE8-IMPL-017`
- raw artifact persistence lifecycle remains `PHASE8-IMPL-018`
- real BookNLP/spaCy runtime extraction remains `PHASE8-IMPL-019`
- model-assisted extraction remains `PHASE8-IMPL-020`
- NCP/Subtxt/dramatica-flow runtime remains `PHASE8-IMPL-021`
- E2E MVP validation remains `PHASE8-IMPL-022`
- fine-tuning remains deferred after MVP

Generated prose and prose-production paths remain permanently forbidden, not deferred.

## Failure And Quarantine Policy

Review command handling must fail closed when:

- `action_type` is unknown
- a future action is unsupported
- a request includes unsafe or prose-generation intent
- required owner confirmation is missing
- candidate/queue linkage mismatches
- expected current review status/version is stale or incompatible
- the payload is malformed
- the request attempts promotion, canon writes, raw persistence, runtime extraction, model calls, generated prose, or training-data creation

Failure may record rejection or quarantine workflow metadata only. A rejection or quarantine action may update bounded review workflow metadata but cannot mutate approved memory/canon, apply promotion, rewrite candidate content, persist raw artifacts, run extraction, call models, or generate prose.

## T003 Test Implications

`PHASE8-IMPL-016-T003` should test:

- expected-red command boundary route/helper contract
- allowed review commands accepted at validation level only
- forbidden promotion, canon, raw persistence, runtime, model, and prose commands rejected
- no mutation of approved memory/canon
- no apply-promotion
- no generated prose
- fail-closed behavior for unknown, unsupported, malformed, unsafe, stale, mismatched, or missing-confirmation requests
- command route remains separate from read-only GET routes

T003 should not implement runtime behavior. It should encode the contract that T004 may satisfy only inside the review-action execution boundary.
