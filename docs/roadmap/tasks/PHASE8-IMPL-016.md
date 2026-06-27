# PHASE8-IMPL-016

## ID

`PHASE8-IMPL-016`

## Title

Frontend owner-action execution workflow and review command boundary

## Status

Active MVP-required parent published after `PHASE8-IMPL-015` closeout. `PHASE8-IMPL-016-T001` is complete/PASS after publishing this parent record, inventory, enrichment JSON, and roadmap/status updates. `PHASE8-IMPL-016-T002` is ready/active next.

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
- T002 — Owner-action execution boundary decision: command taxonomy, allowed/forbidden actions, route/frontend sequencing, and explicit deferral of apply-promotion/memory-canon mutation. Ready/active next.
- T003 — Tests-first command boundary contract for review actions without promotion/canon mutation. Planned.
- T004 — Minimal backend command route/helper implementation for review-action execution only, no apply-promotion/canon mutation. Planned.
- T005 — Frontend owner-action workflow/surface implementation or planning path, depending on existing frontend harness/package constraints. Planned.
- T006 — Safety regression: no silent promotion, no memory/canon mutation, no generated prose, no model/runtime/raw persistence. Planned.
- T007 — Parent closeout. Planned.

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
