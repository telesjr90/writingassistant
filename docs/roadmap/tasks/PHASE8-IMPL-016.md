# PHASE8-IMPL-016

## ID

`PHASE8-IMPL-016`

## Title

Frontend owner-action execution workflow and review command boundary

## Status

Active MVP-required parent published after `PHASE8-IMPL-015` closeout. `PHASE8-IMPL-016-T001` is complete/PASS after publishing this parent record, inventory, enrichment JSON, and roadmap/status updates. `PHASE8-IMPL-016-T002` is complete/PASS after accepting the owner-action review command boundary decision. `PHASE8-IMPL-016-T003` is complete/PASS as a tests-first expected-red review command and owner-action candidate review route contract. `PHASE8-IMPL-016-T004` is complete/PASS after implementing the minimal backend review-action command route/helper. `PHASE8-IMPL-016-T005` is complete/PASS after adding the minimal frontend owner-action review workflow/surface for bounded review commands. `PHASE8-IMPL-016-T006` is complete/PASS after adding focused backend route, frontend source, and targeted source boundary safety regressions. `PHASE8-IMPL-016-T007` is ready/active next.

## Goal

Define and sequence the MVP-required frontend owner-action execution workflow and review command boundary without implementing any runtime command handling beyond later child authorization. This parent prepares the review-command contract and owner-confirmed execution path, but it does not implement apply-promotion, approved memory/canon mutation, raw artifact persistence, runtime extraction, model calls, or generated prose.

## Scope

This parent is MVP-required because the product needs an explicit owner-action execution workflow before review actions can become a safe, auditable command boundary. The parent covers:

- owner-action execution workflow planning and sequencing for candidate review
- request/response boundary definition for review commands
- explicit owner-confirmed review actions
- no silent promotion
- no direct memory/canon mutation
- no apply-promotion in this parent
- no raw artifact persistence in this parent
- no runtime extraction in this parent
- no model calls in this parent
- no generated prose in this parent

The parent is intentionally narrow. It exists to publish the execution record and inventory so child tasks can safely split command taxonomy, tests-first boundary contracts, minimal backend route/helper work, frontend workflow/surface work, and safety regression work.

## Child Sequence

- T001 — Parent publication/inventory/enrichment/status alignment. Complete/PASS.
- T002 — Owner-action execution boundary decision: command taxonomy, allowed/forbidden actions, request boundary, response boundary, frontend workflow boundary, route/frontend sequencing, no silent promotion, and explicit deferral of apply-promotion/memory-canon mutation. Complete/PASS.
- T003 — Tests-first command boundary contract for review actions without promotion/canon mutation. Complete/PASS as expected-red; created `tests/test_writer_assistant_review_action_command_routes_contract.py` for `POST /api/projects/{project_id}/review-queue/{queue_entry_id}/actions`, allowed commands (`mark_reviewed`, `request_more_evidence`, `defer`, `reject`, `quarantine`, `update_owner_note`, `set_review_status`), forbidden commands (`apply_promotion`, `promote_candidate`, `write_memory`, `write_canon`, `persist_raw_artifact`, `run_extraction`, `run_booknlp`, `run_spacy`, `call_model`, `generate_prose`, `rewrite_prose`, `continue_scene`, `create_training_jsonl`), fail closed malformed/unsafe payload coverage, route separation, response boundary, no silent promotion, no apply-promotion, no memory/canon mutation, no raw artifact persistence, no runtime extraction, no model calls, and no generated prose.
- T004 — Minimal backend command route/helper implementation for review-action execution only, no apply-promotion/canon mutation. Complete/PASS; added response-only review workflow command acceptance/rejection for `POST /api/projects/{project_id}/review-queue/{queue_entry_id}/actions`.
- T005 — Frontend owner-action workflow/surface implementation for bounded review workflow commands. Complete/PASS; added a frontend API helper for `POST /api/projects/{project_id}/review-queue/{queue_entry_id}/actions`, a candidate-only/no-canon review queue surface with read-only candidate details, evidence/provenance/source locator context, explicit owner confirmation, fail-closed controls for `mark_reviewed`, `request_more_evidence`, `defer`, `reject`, `quarantine`, `update_owner_note`, and `set_review_status`, and source-level frontend boundary tests.
- T006 — Safety regression: no silent promotion, no memory/canon mutation, no generated prose, no model/runtime/raw persistence. Complete/PASS; added focused route/source regression coverage that proves allowed review commands remain response-only workflow state, forbidden commands and payload fields fail closed, frontend controls remain bounded to review workflow commands, and the targeted source boundary scan distinguishes rejected fixtures from implementation behavior without the earlier contradictory substring issue.
- T007 — Parent closeout. Ready/active next.

## Deferred Boundaries

This parent does not authorize:

- apply-promotion implementation
- approved memory/canon mutation
- raw artifact persistence lifecycle
- runtime extraction or BookNLP/spaCy installation and execution
- model-assisted extraction
- NCP/Subtxt/dramatica-flow runtime integration
- end-to-end MVP validation
- fine-tuning, which remains deferred after MVP
- any generated prose or prose-production behavior

Those remain in later MVP-required parents, especially `PHASE8-IMPL-017` through `PHASE8-IMPL-022`.
