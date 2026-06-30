# PHASE8-IMPL-019

## ID

`PHASE8-IMPL-019`

## Title

Guarded runtime extraction: real BookNLP/spaCy install/run/import and candidate-first extraction pipeline

## Status

PHASE8-IMPL-019 is active after PHASE8-IMPL-019-T004 minimal guarded dependency availability and import/run probe implementation. PHASE8-IMPL-019-T001 is complete/PASS. PHASE8-IMPL-019-T002 is complete/PASS. PHASE8-IMPL-019-T003 is complete/PASS as expected-red tests-only handoff. PHASE8-IMPL-019-T004 is complete/PASS. PHASE8-IMPL-019-T005 is ready/active next. PHASE8-IMPL-019-T006 and PHASE8-IMPL-019-T007 remain planned. PHASE8-IMPL-020 through PHASE8-IMPL-022 remain future MVP-required parents. Fine-tuning remains deferred after MVP. Generated prose/prose-production paths remain permanently forbidden.

## Goal

Deliver real BookNLP/spaCy install/run/import checks and guarded runtime extraction from owner-authored or owner-provided project text into raw artifact bundles and candidate-first review handoff, without canon mutation, model calls, automatic apply-promotion, training artifacts, or generated prose.

## Scope

This parent publishes and sequences the MVP-required guarded runtime extraction track for real BookNLP/spaCy install/run/import plus runtime extraction over owner-authored or owner-provided project text. `PHASE8-IMPL-019-T001` is docs/status/publication only. `PHASE8-IMPL-019-T002` is docs/decision/status only and accepts the Guarded runtime extraction boundary and environment model at `docs/roadmap/decisions/PHASE8-IMPL-019-guarded-runtime-extraction-boundary-environment-model-decision.md`. T002 does not install dependencies, import or run BookNLP, import or run spaCy, implement runtime extraction, change backend/frontend implementation, change product tests, add routes, add UI, call models/Ollama, create candidates, create review queue entries, mutate approved memory/canon, apply promotion, create training artifacts, or generate prose.

Runtime extraction in PHASE8-IMPL-019 may be introduced only through explicitly scoped children after T001 and may run only over owner-authored or owner-provided project text/materials. Output is candidate-first and owner-review-gated; runtime extraction output is never canon by itself, raw tool output is never authoritative by itself, extractor confidence is not truth, and extractor output cannot mutate approved memory/canon, apply promotion, create training data, or generate prose. Raw artifacts must be persisted through PHASE8-IMPL-018 helpers. Candidate persistence/review queue handoff may use existing candidate/review infrastructure only when explicitly scoped. Apply-promotion remains the separate PHASE8-IMPL-017 owner-confirmed path. Missing tools, missing models, unsafe paths, missing source/evidence/provenance, invalid source locators, malformed tool outputs, or unavailable environment must fail-closed or return explicit unavailable/quarantined state. No silent fallback may claim extraction succeeded.

`source_refs`, `evidence_refs`, `provenance_refs`, and `source_locator_refs` are required contract terms for future runtime extraction handoff. Source locator preservation is required where available. Raw artifact persistence means PHASE8-IMPL-018 project-local manifest-backed raw artifact persistence only. The future install/import/run guard model must distinguish configured, disabled, unavailable, dependency_missing, model_missing, configuration_invalid, probe_failed, runtime_failed, malformed_output, unsafe_path, missing_source_refs, missing_evidence_refs, missing_provenance_refs, missing_source_locator_refs, quarantined, rejected, valid, and fail_closed states.

The accepted T002 dependency policy records BookNLP and spaCy as MVP-required for PHASE8-IMPL-019 while keeping dependency changes out of T002. Future runtime extraction must be guarded by environment guards such as `WRITER_ASSISTANT_RUNTIME_EXTRACTION_ENABLED`, `WRITER_ASSISTANT_BOOKNLP_ENABLED`, `WRITER_ASSISTANT_SPACY_ENABLED`, `WRITER_ASSISTANT_BOOKNLP_MODEL_DIR`, `WRITER_ASSISTANT_BOOKNLP_JAVA_HOME`, `WRITER_ASSISTANT_SPACY_MODEL`, `WRITER_ASSISTANT_EXTRACTION_TIMEOUT_SECONDS`, and `WRITER_ASSISTANT_EXTRACTION_MAX_INPUT_CHARS` if implemented in a later task. These names are decision-level contracts only in T002.

T003 is complete/PASS as tests-first expected-red coverage for a future `backend/story_knowledge/runtime_extraction.py` helper, including `validate_runtime_extraction_environment`, `check_booknlp_availability`, `check_spacy_availability`, `validate_runtime_extraction_request`, `build_runtime_extraction_plan`, `run_runtime_extraction_probe`, `run_guarded_runtime_extraction`, `build_raw_artifact_handoff`, `build_candidate_review_handoff`, and `quarantine_runtime_extraction_output`. T003 did not implement runtime extraction.

T004 is complete/PASS as the minimal guarded dependency availability and import/run probe implementation at `backend/story_knowledge/runtime_extraction.py`. It implements disabled-by-default environment validation, explicit BookNLP/spaCy availability states, request validation, deterministic plan building, transient probe results, fail-closed guarded runtime execution, raw artifact support-data handoff shape, candidate draft review handoff shape, and quarantine output shape. T004 does not install dependencies, edit package files, add routes/UI, run full runtime extraction over project text, call models/Ollama, persist candidates or review queue entries, mutate approved memory/canon, apply promotion, create training artifacts, or generate prose.

PHASE8-UX-001 was used only as a read-only terminology/boundary reference for labels such as review, candidate, evidence, provenance, source locator, raw artifact, approved memory/canon, owner action, unavailable/quarantined state, and no automatic canon. PHASE8-UX-001 is not roadmap truth, does not override master_plan, implementation_status, roadmap_index, or PHASE8-IMPL parent boundaries, and was not edited.

## Child Sequence

- `PHASE8-IMPL-019-T001` - Publish/activate guarded runtime extraction parent. complete/PASS. Output/scope: task record, inventory, enrichment JSON, roadmap/status/governance alignment; docs/status only; no install/import/run, no runtime extraction, no code/tests/package changes.
- `PHASE8-IMPL-019-T002` - Guarded runtime extraction boundary decision and environment model. complete/PASS. Output/scope: decision document defining BookNLP/spaCy dependency policy, environment guard model, install/import/run verification rules, extractor request shape, source/evidence/provenance requirements, raw artifact persistence handoff, candidate-first handoff, unavailable/quarantine semantics, and no-prose/no-canon/no-training boundaries; docs/decision only.
- `PHASE8-IMPL-019-T003` - Expected-red guarded runtime extraction contract tests. complete/PASS. Output/scope: expected-red tests for future availability checks, import/run guards, request validation, raw artifact handoff, candidate-first handoff, fail-closed unavailable/quarantine behavior, and no-canon/no-prose/no-training/no-apply-promotion boundaries; no implementation.
- `PHASE8-IMPL-019-T004` - Minimal guarded dependency availability and import/run probe implementation. complete/PASS. Output/scope: minimal backend helper for BookNLP/spaCy availability/import/run probes with environment guards and explicit unavailable states; no package/dependency changes.
- `PHASE8-IMPL-019-T005` - Guarded runtime extraction request and raw artifact handoff implementation. ready/active next. Output/scope: bounded backend runtime extraction helper that validates owner-provided source requests, invokes allowed extractor adapters only under environment guards, stores raw outputs through PHASE8-IMPL-018 raw artifact helpers, and returns candidate-first handoff data without canon mutation.
- `PHASE8-IMPL-019-T006` - Runtime extraction safety regression. planned. Output/scope: focused regression tests proving no automatic canon, no apply-promotion, no candidate/review queue side effects unless explicitly scoped, no model calls, no generated prose, no training artifacts, path safety, unavailable/quarantine behavior, and no silent fallback.
- `PHASE8-IMPL-019-T007` - Parent closeout. planned. Output/scope: parent closeout docs/status/governance, PHASE8-IMPL-020 ready/active next; docs/status only.

## Required Risk Linkage

PHASE8-IMPL-019 links to risk register entries for extractor output treated as canon, BookNLP/spaCy instability blocking MVP runtime extraction, raw artifact leakage into canon/training, apply-promotion bypass, memory/canon mutation outside approved workflow, and generated prose reintroduced as future scope.

## Parent Boundary Tags

- `writer_assistant_core`
- `runtime_extraction`
- `booknlp`
- `spacy`
- `install_import_run_guards`
- `environment_guards`
- `owner_authored_or_owner_provided_sources_only`
- `evidence_provenance_required`
- `source_locator_required_when_available`
- `raw_artifact_handoff`
- `candidate_first`
- `owner_review_required`
- `no_automatic_canon`
- `no_apply_promotion`
- `no_memory_canon_mutation`
- `no_model_calls`
- `no_generated_prose`
- `no_training_artifacts`
- `path_safe`
- `fail_closed`
- `quarantine_aware`
- `no_silent_fallback`
- `ux_reference_terms_only`

## Future Parent Boundaries

Model-assisted extraction remains `PHASE8-IMPL-020`. NCP/Subtxt/dramatica-flow runtime integration remains `PHASE8-IMPL-021`. End-to-end MVP validation remains `PHASE8-IMPL-022`. Fine-tuning remains deferred after MVP. Generated prose, rewrite, continuation, imitation, polish, improvement, expansion, outline generation, chapter generation, write/revise flows, and prose-production paths remain permanently forbidden.
