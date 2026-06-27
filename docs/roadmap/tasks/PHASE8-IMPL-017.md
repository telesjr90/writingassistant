# PHASE8-IMPL-017

## ID

`PHASE8-IMPL-017`

## Title

Apply-promotion contract, audit log, and approved memory/canon mutation boundary

## Status

Active MVP-required parent after committed `PHASE8-IMPL-016` closeout. `PHASE8-IMPL-017-T001` is complete/PASS after publishing this parent record, inventory, enrichment JSON, and roadmap/status updates. `PHASE8-IMPL-017-T002` is complete/PASS after accepting the apply-promotion boundary decision and audit model at `docs/roadmap/decisions/PHASE8-IMPL-017-apply-promotion-boundary-audit-model-decision.md`. `PHASE8-IMPL-017-T003` is complete/PASS as an expected-red contract handoff at `tests/test_writer_assistant_core_apply_promotion_contract.py`; the target fails only because future `backend.story_knowledge.apply_promotion` APIs do not exist yet. `PHASE8-IMPL-017-T004` is ready/active next. `PHASE8-IMPL-017-T005` through `PHASE8-IMPL-017-T007` remain planned.

## Goal

Define and sequence the MVP-required apply-promotion workflow and approved memory/canon mutation boundary. This parent owns the future explicit owner-confirmed apply-promotion path, audited promotion records, and approved memory/canon mutation only after explicit owner action.

## Scope

This parent follows `PHASE8-IMPL-016`, which delivered owner-action review command workflow only. `PHASE8-IMPL-017` is the first parent allowed to design and later implement the candidate-to-approved boundary, but `PHASE8-IMPL-017-T001` is docs/status publication only, `PHASE8-IMPL-017-T002` is docs/decision/status only, and `PHASE8-IMPL-017-T003` is tests/docs/status only.

The parent must keep apply-promotion explicit, owner-confirmed, and audited. It must not automatically promote based on confidence, queue status, model output, extraction, candidate persistence, or raw artifact presence. Queue presence is not approval. Confidence is not truth. Candidate persistence is not canon. Extraction is not canon.

Apply-promotion must not call models, run extraction, persist raw artifacts, create training artifacts, or generate prose. Generated prose and prose-production paths remain permanently forbidden.

## Child Sequence

- `PHASE8-IMPL-017-T001` - Parent publication/inventory/enrichment/status alignment. Complete/PASS.
- `PHASE8-IMPL-017-T002` - Apply-promotion boundary decision and audit model. Complete/PASS. Decision: `docs/roadmap/decisions/PHASE8-IMPL-017-apply-promotion-boundary-audit-model-decision.md`.
- `PHASE8-IMPL-017-T003` - Tests-first expected-red apply-promotion contract. Complete/PASS. Contract: `tests/test_writer_assistant_core_apply_promotion_contract.py`.
- `PHASE8-IMPL-017-T004` - Minimal backend apply-promotion service/route implementation. Ready/active next.
- `PHASE8-IMPL-017-T005` - Frontend apply-promotion confirmation workflow/surface. Planned.
- `PHASE8-IMPL-017-T006` - Approved memory/canon mutation safety regression. Planned.
- `PHASE8-IMPL-017-T007` - Parent closeout. Planned.

## Boundary Tags

- `mvp_required_apply_promotion`
- `approved_memory_canon_mutation`
- `owner_confirmed_only`
- `audited_promotion`
- `candidate_to_approved_boundary`
- `no_auto_promotion`
- `no_confidence_as_truth`
- `no_queue_presence_as_approval`
- `no_extraction_as_canon`
- `no_generated_prose`
- `generated_prose_permanently_forbidden`
- `no_model_calls`
- `no_runtime_extraction`
- `no_raw_artifact_persistence`
- `no_training_artifacts`

## Deferred Boundaries

This parent does not authorize `PHASE8-IMPL-017-T001`, `PHASE8-IMPL-017-T002`, or `PHASE8-IMPL-017-T003` to implement runtime behavior. T002 defines the apply-promotion boundary and audit model only. T003 adds expected-red contract tests only; it does not implement apply-promotion, approved memory mutation, canon mutation, raw artifact persistence, runtime extraction, model-assisted extraction, real BookNLP/spaCy install/run/import, NCP/Subtxt/dramatica-flow runtime integration, generated prose, or training artifacts.

Raw artifact persistence remains `PHASE8-IMPL-018`. Runtime extraction plus real BookNLP/spaCy install/run/import remains `PHASE8-IMPL-019`. Model-assisted evidence-backed extraction remains `PHASE8-IMPL-020`. NCP/Subtxt/dramatica-flow analysis-only runtime remains `PHASE8-IMPL-021`. End-to-end MVP validation remains `PHASE8-IMPL-022`.

Fine-tuning remains deferred after MVP.
