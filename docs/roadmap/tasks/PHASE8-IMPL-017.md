# PHASE8-IMPL-017

## ID

`PHASE8-IMPL-017`

## Title

Apply-promotion contract, audit log, and approved memory/canon mutation boundary

## Status

Active MVP-required parent after committed `PHASE8-IMPL-016` closeout. `PHASE8-IMPL-017-T001` is complete/PASS after publishing this parent record, inventory, enrichment JSON, and roadmap/status updates. `PHASE8-IMPL-017-T002` is ready/active next. `PHASE8-IMPL-017-T003` through `PHASE8-IMPL-017-T007` remain planned.

## Goal

Define and sequence the MVP-required apply-promotion workflow and approved memory/canon mutation boundary. This parent owns the future explicit owner-confirmed apply-promotion path, audited promotion records, and approved memory/canon mutation only after explicit owner action.

## Scope

This parent follows `PHASE8-IMPL-016`, which delivered owner-action review command workflow only. `PHASE8-IMPL-017` is the first parent allowed to design and later implement the candidate-to-approved boundary, but `PHASE8-IMPL-017-T001` is docs/status publication only.

The parent must keep apply-promotion explicit, owner-confirmed, and audited. It must not automatically promote based on confidence, queue status, model output, extraction, candidate persistence, or raw artifact presence. Queue presence is not approval. Confidence is not truth. Candidate persistence is not canon. Extraction is not canon.

Apply-promotion must not call models, run extraction, persist raw artifacts, create training artifacts, or generate prose. Generated prose and prose-production paths remain permanently forbidden.

## Child Sequence

- `PHASE8-IMPL-017-T001` - Parent publication/inventory/enrichment/status alignment. Complete/PASS.
- `PHASE8-IMPL-017-T002` - Apply-promotion boundary decision and audit model. Ready/active next.
- `PHASE8-IMPL-017-T003` - Tests-first expected-red apply-promotion contract. Planned.
- `PHASE8-IMPL-017-T004` - Minimal backend apply-promotion service/route implementation. Planned.
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

This parent does not authorize `PHASE8-IMPL-017-T001` to implement runtime behavior. T001 does not implement apply-promotion, approved memory mutation, canon mutation, raw artifact persistence, runtime extraction, model-assisted extraction, real BookNLP/spaCy install/run/import, NCP/Subtxt/dramatica-flow runtime integration, generated prose, or training artifacts.

Raw artifact persistence remains `PHASE8-IMPL-018`. Runtime extraction plus real BookNLP/spaCy install/run/import remains `PHASE8-IMPL-019`. Model-assisted evidence-backed extraction remains `PHASE8-IMPL-020`. NCP/Subtxt/dramatica-flow analysis-only runtime remains `PHASE8-IMPL-021`. End-to-end MVP validation remains `PHASE8-IMPL-022`.

Fine-tuning remains deferred after MVP.
