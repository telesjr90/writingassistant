# PHASE8-IMPL-018

## ID

`PHASE8-IMPL-018`

## Title

Raw artifact persistence implementation and project-local extraction artifact lifecycle

## Status

Complete/PASS MVP-required parent after committed `PHASE8-IMPL-017` complete/PASS closeout through `PHASE8-IMPL-017-T007`. `PHASE8-IMPL-018-T001` is complete/PASS after publishing this parent record, inventory, enrichment JSON, and roadmap/status updates. `PHASE8-IMPL-018-T002` is complete/PASS after accepting the raw artifact persistence boundary decision and manifest model at `docs/roadmap/decisions/PHASE8-IMPL-018-raw-artifact-persistence-boundary-manifest-model-decision.md`. `PHASE8-IMPL-018-T003` is complete/PASS as an expected-red contract handoff at `tests/test_writer_assistant_core_raw_artifacts_contract.py`. `PHASE8-IMPL-018-T004` is complete/PASS after adding the minimal backend raw artifact persistence helper at `backend/story_knowledge/raw_artifacts.py`; the raw artifact persistence contract now passes. `PHASE8-IMPL-018-T005` is complete/PASS after hardening raw artifact bundle/index lifecycle and provenance linkage in `backend/story_knowledge/raw_artifacts.py` with focused lifecycle tests at `tests/test_writer_assistant_core_raw_artifact_lifecycle_contract.py`. `PHASE8-IMPL-018-T006` is complete/PASS after adding raw artifact safety regression coverage at `tests/test_writer_assistant_core_raw_artifact_safety_regression.py`, proving raw artifacts remain support data only, not canon, not candidates, not training data, path-safe, fail-closed, no extraction, no_runtime_extraction, no_booknlp_spacy_runtime, no_model_calls, no_apply_promotion, no_memory_canon_mutation, and no_generated_prose. `PHASE8-IMPL-018-T007` is complete/PASS as parent closeout. `PHASE8-IMPL-019` is ready/active next as the future MVP-required parent for real BookNLP/spaCy install/run/import plus runtime extraction. `PHASE8-IMPL-020` through `PHASE8-IMPL-022` remain future MVP-required parents. Fine-tuning remains deferred after MVP. Generated prose/prose-production paths remain permanently forbidden.

## Goal

Define and sequence the MVP-required raw artifact persistence lifecycle for Writer Assistant Core. This parent owns project-local raw artifact persistence only: raw artifact bundle/schema/manifest decisions, expected-red persistence contract tests, minimal backend raw artifact persistence helpers, raw artifact bundle/index lifecycle and provenance linkage, safety regression coverage, and parent closeout.

## Scope

This parent follows `PHASE8-IMPL-017`, which delivered explicit owner-confirmed apply-promotion, audited promotion records, and approved memory/canon mutation through valid apply-promotion only. `PHASE8-IMPL-018` must keep raw artifact persistence strictly separate from apply-promotion, approved memory/canon mutation, candidate persistence, extraction execution, model calls, and generated prose.

`PHASE8-IMPL-018` owns raw artifact persistence lifecycle only. Raw artifacts are project-local support data only. Raw artifacts are not canon, not approved memory, not candidates by themselves, and not training data. Raw artifact persistence must be manifest-backed, path-safe, fail-closed, and evidence/provenance-linked. Raw artifact persistence must preserve source/evidence/provenance linkage, must not automatically create candidates, and must not automatically promote to canon.

This parent does not authorize runtime extraction itself unless a later child explicitly implements a bounded helper for storing already-produced raw bundles. Raw artifact persistence must not call models, must not trigger extraction, must not install/run/import BookNLP or spaCy, must not call NCP/Subtxt/dramatica-flow runtimes, and must not generate prose.

Apply-promotion and approved memory/canon mutation were delivered in `PHASE8-IMPL-017` and must remain separate from raw artifact persistence. Real BookNLP/spaCy install/run/import plus runtime extraction remains `PHASE8-IMPL-019`. Model-assisted evidence-backed extraction remains `PHASE8-IMPL-020`. NCP/Subtxt/dramatica-flow analysis-only runtime remains `PHASE8-IMPL-021`. End-to-end MVP usability validation remains `PHASE8-IMPL-022`.

## Child Sequence

- `PHASE8-IMPL-018-T001` - Parent publication/inventory/enrichment/status alignment. Complete/PASS.
- `PHASE8-IMPL-018-T002` - Raw artifact persistence boundary decision and manifest model. Complete/PASS.
- `PHASE8-IMPL-018-T003` - Tests-first expected-red raw artifact persistence contract. Complete/PASS as expected-red handoff in `tests/test_writer_assistant_core_raw_artifacts_contract.py`.
- `PHASE8-IMPL-018-T004` - Minimal backend raw artifact persistence helper implementation. Complete/PASS in `backend/story_knowledge/raw_artifacts.py`.
- `PHASE8-IMPL-018-T005` - Raw artifact bundle/index lifecycle and provenance linkage. Complete/PASS in `backend/story_knowledge/raw_artifacts.py` with `tests/test_writer_assistant_core_raw_artifact_lifecycle_contract.py`.
- `PHASE8-IMPL-018-T006` - Raw artifact safety regression: non-canon, non-training, path-safe, no extraction. Complete/PASS in `tests/test_writer_assistant_core_raw_artifact_safety_regression.py`.
- `PHASE8-IMPL-018-T007` - Parent closeout. Complete/PASS.

## Parent Closeout Summary

Parent result: complete/PASS. `PHASE8-IMPL-018-T001` through `PHASE8-IMPL-018-T007` are complete/PASS.

Delivered decision: `PHASE8-IMPL-018-T002` accepted the raw artifact persistence boundary and manifest model at `docs/roadmap/decisions/PHASE8-IMPL-018-raw-artifact-persistence-boundary-manifest-model-decision.md`.

Delivered implementation: `PHASE8-IMPL-018-T004` added `backend/story_knowledge/raw_artifacts.py` with `validate_raw_artifact_manifest`, `build_raw_artifact_manifest`, `validate_raw_artifact_file_ref`, `raw_artifact_bundle_storage_dir`, `raw_artifact_manifest_path`, `raw_artifact_index_path`, `write_raw_artifact_bundle`, `read_raw_artifact_manifest`, `read_raw_artifact_file`, `list_raw_artifact_bundles`, `rebuild_raw_artifact_index`, `quarantine_raw_artifact_bundle`, and `compute_raw_artifact_bundle_hash`.

Delivered contracts/regressions: `tests/test_writer_assistant_core_raw_artifacts_contract.py`, `tests/test_writer_assistant_core_raw_artifact_lifecycle_contract.py`, and `tests/test_writer_assistant_core_raw_artifact_safety_regression.py`.

Delivered behavior: manifest-backed raw artifact bundles; project-local path-safe storage helpers; valid-only default listing/indexing; derived/rebuildable support-data indexes; `source_refs`, `evidence_refs`, `provenance_refs`, and `source_locator_refs`; quarantine handling; `superseded` and `deleted_tombstone` exclusion by default; duplicate/idempotency handling; canonical deterministic bundle hashing; fail-closed validation; and safety regression coverage for support data only, not canon, not approved memory, not candidates, not training data, no_runtime_extraction, no_booknlp_spacy_runtime, no_model_calls, no_apply_promotion, no_memory_canon_mutation, and no_generated_prose behavior.

Explicit non-deliveries: no runtime extraction; no real BookNLP/spaCy install/run/import; no model-assisted extraction; no NCP/Subtxt/dramatica-flow runtime; no routes; no UI; no apply-promotion changes; no approved memory/canon mutation beyond the existing `PHASE8-IMPL-017` path; no candidate/review queue creation; no training/JSONL/dataset/model artifacts; and no generated prose.

`PHASE8-IMPL-019` is ready/active next only as a future MVP-required parent handoff for real BookNLP/spaCy install/run/import plus runtime extraction. It must be bounded by environment guards, source/evidence/provenance requirements, raw artifact persistence support from `PHASE8-IMPL-018`, candidate-first output, owner review, no automatic canon, no generated prose, and no apply-promotion unless explicitly owner-confirmed through the existing separate path. `PHASE8-IMPL-020` through `PHASE8-IMPL-022` remain future MVP-required parents. Generated context artifacts remain evidence only, not roadmap truth or task completion.

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

This parent did not authorize frontend implementation code, package/dependency changes, runtime extraction, BookNLP/spaCy install/run/import, model-assisted extraction, model/Ollama calls, NCP/Subtxt/dramatica-flow runtime, apply-promotion changes, approved memory/canon mutation, raw artifact-driven candidate creation, raw artifact-driven canon promotion, generated prose, or training/JSONL/dataset/model artifacts in `PHASE8-IMPL-018-T001` through `PHASE8-IMPL-018-T007`. `PHASE8-IMPL-018-T003` authorized only expected-red contract tests and roadmap/status updates. `PHASE8-IMPL-018-T004` authorized only the minimal backend raw artifact persistence helper and docs/status alignment. `PHASE8-IMPL-018-T005` authorized only raw artifact bundle/index lifecycle and provenance linkage hardening plus focused lifecycle/provenance tests and docs/status alignment.

`PHASE8-IMPL-018-T002` defined the raw artifact persistence boundary and manifest model only. It decided future raw artifacts are project-local support data only, not canon, not approved memory, not candidates by themselves, not training data, manifest-backed by `manifest.json`, linked through `source_refs`, `evidence_refs`, `provenance_refs`, and `source_locator_refs`, path-safe, fail-closed, quarantined/rejected when invalid, and separate from apply-promotion, approved memory/canon mutation, runtime extraction, model calls, and generated prose. Contract symbols include `validate_raw_artifact_manifest`, `build_raw_artifact_manifest`, `validate_raw_artifact_file_ref`, `raw_artifact_bundle_storage_dir`, `raw_artifact_manifest_path`, `raw_artifact_index_path`, `write_raw_artifact_bundle`, `read_raw_artifact_manifest`, `read_raw_artifact_file`, `list_raw_artifact_bundles`, `rebuild_raw_artifact_index`, `quarantine_raw_artifact_bundle`, and `compute_raw_artifact_bundle_hash`. `PHASE8-IMPL-018-T003` added expected-red contract tests only at `tests/test_writer_assistant_core_raw_artifacts_contract.py`. `PHASE8-IMPL-018-T004` implemented the minimal standard-library backend helper at `backend/story_knowledge/raw_artifacts.py` and moved the raw artifact persistence contract to PASS. `PHASE8-IMPL-018-T005` is complete/PASS and hardened `pending_validation`, `valid`, `rejected`, `quarantined`, `superseded`, and `deleted_tombstone` lifecycle handling; default valid-only listing/indexing; derived support data index entries containing safe manifest metadata, `bundle_hash`, `manifest_hash`, source/evidence/provenance/source locator refs, and artifact file summaries; fail-closed stale/missing/invalid manifest and missing/hash-mismatched artifact behavior; quarantine reason preservation; deterministic duplicate handling; and canonical JSON hash behavior. Raw artifact indexes remain support data, not canon, not candidates, not training data. `PHASE8-IMPL-018-T006` is complete/PASS with `tests/test_writer_assistant_core_raw_artifact_safety_regression.py`, proving raw artifacts remain support data only, path-safe, fail-closed, non-canon, non-candidate, not candidates, non-training-data, not training data, no extraction, no_runtime_extraction, no_booknlp_spacy_runtime, no_model_calls, no_apply_promotion, no_memory_canon_mutation, no_generated_prose, quarantine safe, and unable to create approved memory/canon, candidates, review queue entries, training artifacts, apply-promotion side effects, model calls, or generated prose/prose-production behavior. `PHASE8-IMPL-018-T007` is complete/PASS and closes the parent.

Real BookNLP/spaCy install/run/import plus runtime extraction is ready/active next in `PHASE8-IMPL-019`. Model-assisted evidence-backed extraction remains `PHASE8-IMPL-020`. NCP/Subtxt/dramatica-flow analysis-only runtime remains `PHASE8-IMPL-021`. End-to-end MVP validation remains `PHASE8-IMPL-022`. Fine-tuning remains deferred after MVP. Generated prose remains permanently forbidden.
