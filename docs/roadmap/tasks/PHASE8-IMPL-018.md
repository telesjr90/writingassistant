# PHASE8-IMPL-018

## ID

`PHASE8-IMPL-018`

## Title

Raw artifact persistence implementation and project-local extraction artifact lifecycle

## Status

MVP-required active parent after committed `PHASE8-IMPL-017` complete/PASS closeout through `PHASE8-IMPL-017-T007`. `PHASE8-IMPL-018-T001` is complete/PASS after publishing this parent record, inventory, enrichment JSON, and roadmap/status updates. `PHASE8-IMPL-018-T002` is ready/active next for the raw artifact persistence boundary decision and manifest model. `PHASE8-IMPL-018-T003` through `PHASE8-IMPL-018-T007` remain planned. `PHASE8-IMPL-019` through `PHASE8-IMPL-022` remain future MVP-required parents. Fine-tuning remains deferred after MVP. Generated prose/prose-production paths remain permanently forbidden.

## Goal

Define and sequence the MVP-required raw artifact persistence lifecycle for Writer Assistant Core. This parent owns project-local raw artifact persistence only: raw artifact bundle/schema/manifest decisions, expected-red persistence contract tests, minimal backend raw artifact persistence helpers, raw artifact bundle/index lifecycle and provenance linkage, safety regression coverage, and parent closeout.

## Scope

This parent follows `PHASE8-IMPL-017`, which delivered explicit owner-confirmed apply-promotion, audited promotion records, and approved memory/canon mutation through valid apply-promotion only. `PHASE8-IMPL-018` must keep raw artifact persistence strictly separate from apply-promotion, approved memory/canon mutation, candidate persistence, extraction execution, model calls, and generated prose.

`PHASE8-IMPL-018` owns raw artifact persistence lifecycle only. Raw artifacts are project-local support data only. Raw artifacts are not canon, not approved memory, not candidates by themselves, and not training data. Raw artifact persistence must be manifest-backed, path-safe, fail-closed, and evidence/provenance-linked. Raw artifact persistence must preserve source/evidence/provenance linkage, must not automatically create candidates, and must not automatically promote to canon.

This parent does not authorize runtime extraction itself unless a later child explicitly implements a bounded helper for storing already-produced raw bundles. Raw artifact persistence must not call models, must not trigger extraction, must not install/run/import BookNLP or spaCy, must not call NCP/Subtxt/dramatica-flow runtimes, and must not generate prose.

Apply-promotion and approved memory/canon mutation were delivered in `PHASE8-IMPL-017` and must remain separate from raw artifact persistence. Real BookNLP/spaCy install/run/import plus runtime extraction remains `PHASE8-IMPL-019`. Model-assisted evidence-backed extraction remains `PHASE8-IMPL-020`. NCP/Subtxt/dramatica-flow analysis-only runtime remains `PHASE8-IMPL-021`. End-to-end MVP usability validation remains `PHASE8-IMPL-022`.

## Child Sequence

- `PHASE8-IMPL-018-T001` - Parent publication/inventory/enrichment/status alignment. Complete/PASS.
- `PHASE8-IMPL-018-T002` - Raw artifact persistence boundary decision and manifest model. Ready/active next.
- `PHASE8-IMPL-018-T003` - Tests-first expected-red raw artifact persistence contract. Planned.
- `PHASE8-IMPL-018-T004` - Minimal backend raw artifact persistence helper implementation. Planned.
- `PHASE8-IMPL-018-T005` - Raw artifact bundle/index lifecycle and provenance linkage. Planned.
- `PHASE8-IMPL-018-T006` - Raw artifact safety regression: non-canon, non-training, path-safe, no extraction. Planned.
- `PHASE8-IMPL-018-T007` - Parent closeout. Planned.

## Parent Boundary Tags

- `mvp_required_raw_artifact_persistence`
- `raw_artifacts_support_data_only`
- `raw_artifacts_not_canon`
- `raw_artifacts_not_candidates`
- `raw_artifacts_not_training_data`
- `project_local_raw_artifacts`
- `manifest_backed_raw_artifacts`
- `evidence_provenance_linked`
- `path_safe_fail_closed`
- `no_runtime_extraction`
- `no_booknlp_spacy_runtime`
- `no_model_calls`
- `no_apply_promotion`
- `no_memory_canon_mutation`
- `no_generated_prose`
- `generated_prose_permanently_forbidden`
- `no_training_artifacts`

## Deferred Boundaries

This parent does not authorize backend implementation code, frontend implementation code, product test changes, package/dependency changes, runtime extraction, BookNLP/spaCy install/run/import, model-assisted extraction, model/Ollama calls, NCP/Subtxt/dramatica-flow runtime, apply-promotion changes, approved memory/canon mutation, raw artifact-driven candidate creation, raw artifact-driven canon promotion, generated prose, or training/JSONL/dataset/model artifacts in `PHASE8-IMPL-018-T001`.

`PHASE8-IMPL-018-T002` will define the raw artifact persistence boundary and manifest model only. `PHASE8-IMPL-018-T003` will add expected-red contract tests only. `PHASE8-IMPL-018-T004` will be the first child allowed to implement minimal backend raw artifact persistence helpers if separately authorized by the child contract. `PHASE8-IMPL-018-T005` is limited to bundle/index lifecycle and provenance linkage. `PHASE8-IMPL-018-T006` is limited to safety regression coverage proving raw artifacts remain support data only, path-safe, fail-closed, non-canon, non-candidate, non-training-data, and no_runtime_extraction.

Real BookNLP/spaCy install/run/import plus runtime extraction remains `PHASE8-IMPL-019`. Model-assisted evidence-backed extraction remains `PHASE8-IMPL-020`. NCP/Subtxt/dramatica-flow analysis-only runtime remains `PHASE8-IMPL-021`. End-to-end MVP validation remains `PHASE8-IMPL-022`. Fine-tuning remains deferred after MVP. Generated prose remains permanently forbidden.
