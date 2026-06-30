# PHASE8-IMPL-019 guarded runtime extraction boundary and environment model decision

Decision result: Accepted for PHASE8-IMPL-019-T002.

## Purpose

Define the exact boundary and environment model for future guarded runtime extraction with real BookNLP/spaCy install/run/import checks and candidate-first extraction handoff.

## Dependency policy

BookNLP and spaCy are MVP-required for PHASE8-IMPL-019, but PHASE8-IMPL-019-T002 does not install, import, or run them. Future install/import/run probes must be explicit, test-covered, environment-gated, and separate from runtime extraction on real project text. No silent fallback may claim runtime extraction passed.

Missing tools, missing language models, unsupported OS/runtime, unavailable Java or model data, invalid config, or a failed probe must return an explicit unavailable or fail-closed status such as `unavailable`, `dependency_missing`, `model_missing`, `configuration_invalid`, `probe_failed`, or `fail_closed`. Runtime dependency changes require a later explicitly scoped task. `backend/requirements.txt` remains read-only in T002. `training/requirements-unsloth.txt` remains unrelated to runtime extraction dependencies. Any future dependency additions must preserve local-first/privacy constraints and must not add training/model artifact behavior.

## Environment guard model

Future runtime extraction must be disabled/unavailable by safe default unless explicitly enabled by required environment/config flags. Proposed future environment variable names are decision-level contracts only in T002 and are not implemented here:

- `WRITER_ASSISTANT_RUNTIME_EXTRACTION_ENABLED`
- `WRITER_ASSISTANT_BOOKNLP_ENABLED`
- `WRITER_ASSISTANT_SPACY_ENABLED`
- `WRITER_ASSISTANT_BOOKNLP_MODEL_DIR`
- `WRITER_ASSISTANT_BOOKNLP_JAVA_HOME`
- `WRITER_ASSISTANT_SPACY_MODEL`
- `WRITER_ASSISTANT_EXTRACTION_TIMEOUT_SECONDS`
- `WRITER_ASSISTANT_EXTRACTION_MAX_INPUT_CHARS`

Future code must distinguish `configured`, `disabled`, `unavailable`, `dependency_missing`, `model_missing`, `probe_failed`, `unsafe_path`, `malformed_output`, `missing_evidence`, `missing_provenance`, `quarantined`, `fail_closed`, and `valid`. T003/T004 may refine exact config parsing, but safe defaults must never enable runtime extraction implicitly.

## Install/import/run verification rules

Future T003/T004/T005 work must keep import checks separate from run checks. A run check must use a tiny owner-approved or public-domain safe probe fixture, not project canon. BookNLP and spaCy probes must not create canon, candidates, review queue entries, training artifacts, dataset manifests, model artifacts, approved memory, or promotion records. Probe outputs are raw support data only or transient availability results.

Probe success does not imply runtime extraction success on real project text. Probe failure must be explicit and fail closed. Probe logs may be preserved only if safe, local, non-secret, and not training/model artifacts. Malformed probe outputs must be quarantined or reported unavailable and must not be indexed as valid support data.

## Runtime extraction request shape

Future runtime extraction requests must be explicit structured requests with fields such as:

- `project_id`
- `extraction_request_id`
- `source_type`
- `source_id`
- `source_path` or `source_ref`
- `owner_provided_text_ref` or `owner_authored_document_ref`
- `requested_extractors`
- `requested_artifact_types`
- `source_refs`
- `evidence_refs`
- `provenance_refs`
- `source_locator_refs`
- `boundary_confirmations`
- `environment_profile`
- `max_input_chars`
- `timeout_seconds`
- `actor` or `requested_by`
- `created_at`

`project_id` and all ids must be path-safe. The source must be owner-authored or owner-provided. Raw source text must not be treated as user request intent for no-prose guard purposes. Requests fail closed if source, evidence, or provenance is missing; unsafe paths fail closed; unsupported source types fail closed; requested extractors must be allowlisted; and requested artifact types must be support-data only.

Requests for `generated_prose`, `continuation`, `rewrite`, `outline`, `model_prompt`, `model_completion`, `training_jsonl`, `dataset_manifest`, `model_artifact`, `promotion_record`, `candidate_record`, `review_queue_entry`, `approved_memory`, or canon artifacts must be rejected.

## Source/evidence/provenance model

`source_refs` and `provenance_refs` are required. `evidence_refs` are required when outputs support candidate/review workflows. `source_locator_refs` are required when offsets, spans, or records are available. Source locators must include safe document/source identity and span/offset information where available. Offsets must be non-negative and bounded. Invalid locators fail closed or quarantine.

No evidence or provenance may be invented. Raw tool output is never authoritative by itself. Confidence is support strength/uncertainty, not truth.

## Raw artifact handoff

All future raw runtime outputs must be persisted through PHASE8-IMPL-018 raw artifact helpers. Raw artifact bundles remain project-local support data only. Raw artifacts are not canon, not approved memory, not candidates by themselves, and not training data.

Raw artifact status must support `valid`, `pending_validation`, `rejected`, `quarantined`, `superseded`, and `deleted_tombstone` where applicable. Malformed, unsupported, unsafe, or incomplete outputs must be rejected or quarantined. Missing raw artifact persistence must fail closed; runtime extraction cannot claim success if raw persistence fails.

## Candidate-first owner-review handoff

Runtime extraction may produce candidate draft handoff data only when explicitly scoped in future children. Candidate persistence or review queue handoff may use existing candidate/review infrastructure only when explicitly scoped. Runtime extraction output is never approval and never canon. Queue presence is not approval. Candidate persistence is not canon. Owner review is required before promotion.

Apply-promotion remains the separate PHASE8-IMPL-017 owner-confirmed path. No automatic apply-promotion is allowed. The accepted handoff is candidate-first, owner review required, no automatic canon, no apply-promotion, and no memory/canon mutation.

## Unavailable/quarantine/fail-closed semantics

Recommended future statuses and meanings:

- `disabled`: runtime extraction or a specific extractor is intentionally off.
- `unavailable`: the environment cannot safely perform the requested operation; unavailable is not success.
- `dependency_missing`: a required package/tool/runtime is absent.
- `model_missing`: required BookNLP/spaCy model data is absent.
- `configuration_invalid`: required config is absent, malformed, unsafe, or inconsistent.
- `probe_failed`: import/run probe failed.
- `runtime_failed`: guarded execution failed after passing availability checks.
- `malformed_output`: output shape/content cannot be validated.
- `unsafe_path`: request or output points outside allowlisted project-local paths.
- `missing_source_refs`: source references are absent.
- `missing_evidence_refs`: required evidence references are absent.
- `missing_provenance_refs`: provenance references are absent.
- `missing_source_locator_refs`: required source locator refs are absent.
- `quarantined`: output is preserved only as unsafe/invalid support for inspection; quarantine is not success.
- `rejected`: output/request failed validation and must not be used.
- `valid`: request/output passed the applicable guard checks.

Fallback is allowed only when clearly reported as unavailable/fail-closed and never as successful extraction. No silent fallback may claim extraction passed. Unsafe or unsupported results must not be indexed as valid support data.

## No-prose / no-canon / no-training boundaries

PHASE8-IMPL-019-T002 and future PHASE8-IMPL-019 runtime extraction boundaries explicitly forbid: generated prose, rewrite, continuation, style imitation, polish/improvement, outline generation, chapter/scene generation, model prompts/completions as raw artifacts, training JSONL, dataset manifests, model artifacts, direct memory/canon writes, bible/storyform/scenes/notes/materials mutation, apply-promotion, candidate/review queue creation unless a future child explicitly scopes it, model/Ollama calls in PHASE8-IMPL-019, and generated prose/prose-production behavior.

PHASE8-IMPL-020 owns model-assisted extraction. PHASE8-IMPL-021 owns NCP/Subtxt/dramatica-flow runtime. PHASE8-IMPL-022 owns end-to-end MVP validation. Fine-tuning remains deferred after MVP. Generated prose/prose-production paths remain permanently forbidden.

## UX terminology reference

PHASE8-UX-001 was used only as read-only terminology/boundary reference. It may inform labels like review, candidate, evidence, provenance, source locator, raw artifact, approved memory/canon, owner action, unavailable, quarantined, and no automatic canon. It does not authorize UX implementation. It does not override roadmap truth. It was not edited.

## T003 handoff

PHASE8-IMPL-019-T003 is ready/active next and must remain tests-first expected-red only. It should add expected-red tests for a future backend helper, likely `backend/story_knowledge/runtime_extraction.py`, without implementing runtime extraction.

Expected future public API names may include:

- `validate_runtime_extraction_environment`
- `check_booknlp_availability`
- `check_spacy_availability`
- `validate_runtime_extraction_request`
- `build_runtime_extraction_plan`
- `run_runtime_extraction_probe`
- `run_guarded_runtime_extraction`
- `build_raw_artifact_handoff`
- `build_candidate_review_handoff`
- `quarantine_runtime_extraction_output`

T003 must test the accepted dependency policy, environment guards, install/import/run split, availability/unavailable statuses, request validation, source/evidence/provenance/source-locator requirements, PHASE8-IMPL-018 raw artifact handoff, candidate-first owner-review handoff, fail-closed/quarantine behavior, and no-prose/no-canon/no-training/no-apply-promotion/no-model-call boundaries. T003 must not implement runtime extraction.

## Explicit non-deliveries in T002

PHASE8-IMPL-019-T002 delivered docs/decision/status only: no install/import/run; no runtime extraction; no backend code; no frontend code; no product tests; no routes; no UI; no dependency/package changes; no model/Ollama calls; no NCP/Subtxt/dramatica-flow runtime; no apply-promotion changes; no approved memory/canon mutation; no candidate/review queue creation; no generated prose; no training/JSONL/dataset/model artifacts.
