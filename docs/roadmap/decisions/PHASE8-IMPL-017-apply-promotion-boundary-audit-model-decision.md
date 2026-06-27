# PHASE8-IMPL-017 Apply-Promotion Boundary and Audit Model Decision

## Decision Summary

`PHASE8-IMPL-017-T002` accepts this decision as the formal apply-promotion boundary and audit model for `PHASE8-IMPL-017`.

Apply-promotion is the only approved path from candidate/review workflow state into approved memory/canon for this parent. Apply-promotion must be explicit, owner-confirmed, audited, evidence/provenance-backed, and fail closed.

T002 is decision-only. It implements no runtime behavior, no backend route, no backend service/helper, no frontend UI, no product tests, no approved memory/canon mutation, no raw artifact persistence, no runtime extraction, no model calls, and no generated prose or prose-production behavior.

## Promotion Boundary

Candidate records, review queue entries, owner-action review commands, confidence, extraction output, model output, raw artifact refs, and queue presence are not canon.

Promotion requires explicit owner selection and final confirmation. Promotion must not run automatically. Promotion must not be inferred from confidence, queue status, review status, candidate persistence, model output, extraction output, or raw artifact existence.

Promotion must be separate from extraction, queue state, confidence, candidate persistence, and frontend review commands.

Required boundary statements:

- candidate persistence is not canon
- queue presence is not approval
- confidence is not truth
- raw artifacts are support data
- extraction is not canon
- no_auto_promotion
- no_confidence_as_truth
- no_queue_presence_as_approval
- no_extraction_as_canon

## Required Promotion Preconditions

Future apply-promotion must validate these preconditions before any approved memory/canon mutation:

- safe `project_id`
- valid `candidate_id`
- candidate record exists
- candidate type is supported by the approved-memory/canon destination
- candidate is candidate-only before promotion
- review queue entry linkage if applicable
- explicit owner approval state
- final owner confirmation
- destination selected by owner
- destination is allowlisted
- safe target path/record key
- evidence present
- provenance present
- source locator present where available
- actor/audit metadata present
- no generated prose fields
- no model prompt/output fields
- no raw artifact body promoted directly
- no training/model artifact destination

## Destination Boundary

Allowed future destination categories at the decision level only:

- approved characters
- approved locations/settings
- approved timeline/events
- approved relationships
- approved organizations
- approved objects
- approved plot threads
- approved continuity/consistency records
- approved open questions
- approved project memory/canon index entries

Exact schemas, file paths, and record keys may be refined by `PHASE8-IMPL-017-T003` and `PHASE8-IMPL-017-T004`, but destinations must remain project-local and owner-approved only.

## Forbidden Destinations and Actions

Future apply-promotion and any surrounding workflow must explicitly forbid:

- story prose generation
- scene/chapter/paragraph/dialogue writing
- rewriting, continuation, polish, improvement, or expansion
- direct bible/storyform/story truth mutation without apply-promotion audit
- automatic memory/canon mutation
- raw artifact persistence
- raw artifact body as canon
- runtime extraction
- BookNLP/spaCy install/run/import
- model/Ollama calls
- NCP/Subtxt/dramatica-flow runtime
- training JSONL, dataset, or model artifact writes
- external sync/push
- hidden file writes outside project-local approved memory/canon paths

Generated prose and prose-production paths remain permanently forbidden.

## Audit Model

Future apply-promotion audit records must include, at minimum:

- `promotion_record_id`
- `project_id`
- `candidate_id`
- `queue_entry_id` or null
- `candidate_type`
- `source_candidate_snapshot_hash` or equivalent deterministic snapshot marker
- `destination_type`
- `destination_path` or `destination_key`
- `owner_actor_id` or `owner_actor_label`
- `owner_confirmation`
- `owner_note`
- `evidence_refs`
- `provenance_refs`
- `source_locator_refs`
- `applied_at`
- `created_at`
- `promotion_status`
- `before_state_ref` or null
- `after_state_ref` or null
- `mutation_summary`
- `boundary_flags`
- `no_generated_prose_confirmation`
- `no_model_call_confirmation`
- `no_training_artifact_confirmation`

Audit records must be append-only or immutable once applied, except for a separately audited correction workflow that is out of scope for T002.

## Transaction and Mutation Model

Future apply-promotion is a two-stage operation:

1. validate and build a promotion plan
2. apply the owner-confirmed promotion plan and write an audit record

Future implementation must fail closed before mutation if validation fails. Partial mutation without audit is forbidden. Audit without actual approved mutation must be explicitly marked as `rejected`, `blocked`, or `dry_run`, not `applied`.

Idempotency and duplicate prevention must be considered in `PHASE8-IMPL-017-T003` and `PHASE8-IMPL-017-T004`.

## Failure and Quarantine Model

Future apply-promotion must fail closed for:

- missing candidate
- unsafe `project_id`
- unsafe destination/path
- unsupported candidate type
- missing evidence/provenance/source locator
- missing owner confirmation
- generated prose fields
- model prompt/output fields
- raw artifact body as target content
- stale candidate snapshot
- invalid queue linkage
- attempted automatic promotion
- attempted memory/canon mutation outside apply-promotion
- attempted training/model artifact write

Failures should be explicit and auditable without mutating approved memory/canon.

## T003 Expected-Red Contract Guidance

`PHASE8-IMPL-017-T003` should add expected-red contract tests before implementation for:

- expected-red imports for the future apply-promotion module/service
- validation of required preconditions
- fail-closed forbidden destinations/actions
- audit record shape
- plan/apply separation
- no automatic promotion
- no confidence-as-truth
- no queue-presence-as-approval
- no extraction-as-canon
- no model calls
- no generated prose
- no raw artifact body promoted directly
- no training artifacts
- approved memory/canon unchanged on validation failure

T003 should preserve the boundary flags `no_auto_promotion`, `no_confidence_as_truth`, `no_queue_presence_as_approval`, `no_extraction_as_canon`, `no_generated_prose`, `no_model_calls`, and `no_training_artifacts`.

## Future Child Task Handoff

- `PHASE8-IMPL-017-T003`: expected-red apply-promotion contract tests
- `PHASE8-IMPL-017-T004`: minimal backend apply-promotion service/route implementation, only after T003
- `PHASE8-IMPL-017-T005`: frontend apply-promotion confirmation workflow/surface
- `PHASE8-IMPL-017-T006`: approved memory/canon mutation safety regression
- `PHASE8-IMPL-017-T007`: parent closeout
