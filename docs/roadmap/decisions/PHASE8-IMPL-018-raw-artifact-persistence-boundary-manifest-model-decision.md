# PHASE8-IMPL-018-T002 Raw Artifact Persistence Boundary and Manifest Model Decision

## 1. Decision summary

`PHASE8-IMPL-018-T002` accepts a docs/status decision for the future raw artifact persistence boundary and manifest model. The decision is planning/governance only: it implements no runtime behavior, no backend helpers, no frontend code, no tests, no raw artifact files, no raw artifact indexes, no extraction execution, no model calls, no apply-promotion changes, no approved memory/canon mutation, no generated prose, and no training artifacts.

Future raw artifact persistence must be project-local, manifest-backed, evidence_provenance_linked, path-safe, and fail-closed. Raw artifacts are support data only: not canon, not approved memory, not candidates by themselves, and not training data. Boundary markers: `raw_artifacts_support_data_only`, `raw_artifacts_not_canon`, `raw_artifacts_not_candidates`, `raw_artifacts_not_training_data`, `project_local_raw_artifacts`, `manifest_backed_raw_artifacts`, `evidence_provenance_linked`, `path_safe_fail_closed`, `no_runtime_extraction`, `no_booknlp_spacy_runtime`, `no_model_calls`, `no_apply_promotion`, `no_memory_canon_mutation`, `no_generated_prose`, `generated_prose_permanently_forbidden`, and `no_training_artifacts`.

## 2. Raw artifact definition

Raw artifacts are project-local support data emitted by or supplied to extraction/analysis pipelines. Examples include:

- tool output files
- parser output files
- extraction run metadata
- source maps
- evidence-span maps
- provenance records
- offset maps
- intermediate normalized artifacts
- adapter-specific raw bundle payloads

Raw artifacts are not canon. Raw artifacts are not approved memory. Raw artifacts are not candidates by themselves. Raw artifacts are not training data. Raw artifacts are not evidence by themselves unless linked to a specific source/evidence/provenance record. Raw artifacts do not authorize promotion. Raw artifacts do not authorize candidate creation by themselves.

## 3. Non-canon / non-candidate / non-training boundary

Raw artifact persistence is support-data persistence only. A valid raw artifact bundle may later be referenced by separate candidate, evidence, review, or promotion workflows, but persistence of the bundle alone never creates truth, approval, candidate records, review queue entries, promotion records, memory records, canon records, JSONL, datasets, model artifacts, or training manifests.

Candidate persistence is a separate validated workflow. Apply-promotion is a separate owner-confirmed workflow. Training data creation remains outside this parent and is not authorized by raw artifact presence.

## 4. Project-local storage boundary

Future raw artifact bundles should use this project-local root:

```text
projects/{project_id}/writer_assistant/raw_artifacts/{raw_artifact_bundle_id}/
```

All paths must be project-local. All persisted file paths in manifests must be relative to the bundle root. Absolute paths are forbidden. Path traversal is forbidden. Symlinks are forbidden unless validation explicitly rejects them. Bundle ids must be safe ids. File ids must be safe ids. Writes outside the project root are forbidden.

## 5. Raw artifact bundle layout

Future bundle layout:

```text
manifest.json
artifacts/
indexes/
quarantine/
logs/
README.md
```

`manifest.json` is required. `artifacts/` stores allowlisted artifact files only. `indexes/` stores derived/rebuildable navigation data only. `quarantine/` stores rejected or unsafe bundle material only if a later implementation authorizes quarantine storage. `logs/` is allowed only for non-runtime metadata and must not persist execution logs that reveal external secrets. `README.md` or bundle notes are allowed only if owner-authored/admin-authored and non-prose-generating.

## 6. Manifest model

Future manifests must include these required fields:

- `schema_version`
- `raw_artifact_bundle_id`
- `project_id`
- `created_at`
- `updated_at` or null
- `status`
- `artifact_source_type`
- `artifact_source_id`
- `extraction_run_id` or null
- `source_refs`
- `evidence_refs`
- `provenance_refs`
- `source_locator_refs`
- `tool_name` or null
- `tool_version` or null
- `adapter_name` or null
- `adapter_version` or null
- `pipeline_name` or null
- `pipeline_version` or null
- `artifact_files`
- `bundle_hash`
- `manifest_hash` or `content_hash`
- `boundary_flags`
- `validation_status`
- `quarantine_reason` or null
- `no_generated_prose_confirmation`
- `no_model_call_confirmation`
- `no_training_artifact_confirmation`
- `no_apply_promotion_confirmation`
- `no_memory_canon_mutation_confirmation`
- `no_runtime_extraction_confirmation`

Accepted future status values are:

- `pending_validation`
- `valid`
- `rejected`
- `quarantined`
- `superseded`
- `deleted_tombstone`

These values preserve fail-closed semantics: unknown status, missing validation state, missing required boundary confirmations, or contradictory status must reject or quarantine the bundle.

## 7. Artifact file reference model

Each future `artifact_files` entry must include:

- `artifact_file_id`
- `artifact_type`
- `relative_path`
- `media_type`
- `encoding`
- `size_bytes`
- `sha256`
- `record_count` or null
- `line_count` or null
- `schema_name` or null
- `schema_version` or null
- `parser_hint` or null
- `source_locator_refs`
- `evidence_refs`
- `provenance_refs`
- `boundary_flags`

Allowed future `artifact_type` values are strictly allowlisted:

- `source_snapshot`
- `token_table`
- `entity_table`
- `quote_table`
- `event_table`
- `coref_table`
- `dependency_table`
- `offset_map`
- `source_map`
- `evidence_map`
- `provenance_map`
- `adapter_metadata`
- `parser_metadata`
- `normalized_intermediate`

Forbidden artifact_type or destination/action values include:

- `canon`
- `approved_memory`
- `candidate_record`
- `review_queue_entry`
- `promotion_record`
- `training_jsonl`
- `dataset_manifest`
- `model_artifact`
- `generated_prose`
- `rewritten_prose`
- `continuation`
- `outline`
- `model_prompt`
- `model_completion`
- `runtime_extraction_trigger`

## 8. Source/evidence/provenance linkage model

Every valid bundle must link to `source_refs`. Every valid bundle must link to `provenance_refs`. `evidence_refs` are required when the artifact supports candidate/evidence workflows. `source_locator_refs` are required when offsets, spans, rows, records, or source mappings are available.

Raw artifact ids may be referenced later by candidate records, but raw artifact persistence must not create candidate records automatically. Raw artifact ids may be referenced later by apply-promotion audit records, but raw artifact persistence must not apply promotion automatically. A raw artifact without sufficient source/provenance linkage must be rejected or quarantined.

## 9. Bundle/index lifecycle model

Validation and manifest building perform no candidate/canon/training mutation. Writing a valid bundle writes `manifest.json` plus allowlisted artifact files only. Index entries are derived or rebuildable from manifests. Indexes are support/navigation data only, not canon.

Index writes must not create candidates. Index writes must not promote canon. Duplicate bundle ids must fail closed or return a deterministic existing result. Stale or invalid bundle references must fail closed. Deleting should be tombstone/quarantine-aware if allowed later, not silent removal that breaks provenance.

## 10. Validation and fail-closed model

Future validation must reject unknown schema versions, unsafe ids, missing required fields, unsupported statuses, unsupported artifact types, absolute paths, traversal paths, symlinks, missing files, hash mismatches, size mismatches, missing source/provenance linkage, contradictory boundary flags, and any marker for canon/candidate/training/model/prose/runtime-extraction destinations.

Fail-closed means the helper returns a validation error or quarantine/rejection result and performs no partial write outside the allowed bundle boundary.

## 11. Quarantine/rejection model

Invalid bundles fail closed. Invalid paths fail closed. Unsupported artifact types fail closed. Missing required source/provenance fails closed. Generated prose/model/training/canon/candidate destination markers fail closed.

Rejected or quarantined bundles must not appear as valid support data. Quarantined bundles must not be referenced as valid evidence in candidate/promotion workflows. Quarantine state is support/audit metadata only and is not approval, canon, or a training signal.

## 12. Separation from apply-promotion and approved memory/canon

`PHASE8-IMPL-017` apply-promotion remains the only approved path to approved memory/canon mutation. Raw artifact persistence must not call apply-promotion. Raw artifact persistence must not create promotion audit records. Raw artifact persistence must not write approved_memory. Raw artifact persistence must not mutate canon.

Raw artifacts may only be referenced by future candidates/promotions as support data after separate validated workflows. `no_apply_promotion` and `no_memory_canon_mutation` are required boundary confirmations.

## 13. Separation from runtime extraction and model calls

`PHASE8-IMPL-018-T002` does not implement runtime extraction. `PHASE8-IMPL-018` as a parent does not authorize real extraction execution until a later explicitly scoped child, and real BookNLP/spaCy runtime remains `PHASE8-IMPL-019`.

Future raw artifact persistence helpers may store already-produced raw bundles but must not trigger extraction. No BookNLP/spaCy install/run/import is authorized in T002. No model/Ollama calls are authorized. No NCP/Subtxt/dramatica-flow runtime calls are authorized. No generated prose is authorized. Required flags include `no_runtime_extraction`, `no_booknlp_spacy_runtime`, `no_model_calls`, and `no_generated_prose`.

## 14. Security/path-safety model

Future helpers must normalize paths under the project root and bundle root, reject absolute paths, reject `..` traversal, reject hidden path escapes, reject symlinks, reject unsafe ids, reject duplicate file ids, reject file references outside the bundle, reject special device paths, and validate hashes before marking a bundle valid.

Manifests may store relative paths only. Runtime environment secrets, external absolute file paths, and machine-local temporary paths must not be persisted as valid artifact references.

## 15. Future T003 expected-red contract guidance

`PHASE8-IMPL-018-T003` should add expected-red tests for future module `backend.story_knowledge.raw_artifacts` and public APIs:

- `validate_raw_artifact_manifest`
- `build_raw_artifact_manifest`
- `validate_raw_artifact_file_ref`
- `raw_artifact_bundle_storage_dir`
- `raw_artifact_manifest_path`
- `raw_artifact_index_path`
- `write_raw_artifact_bundle`
- `read_raw_artifact_manifest`
- `read_raw_artifact_file`
- `list_raw_artifact_bundles`
- `rebuild_raw_artifact_index`
- `quarantine_raw_artifact_bundle`
- `compute_raw_artifact_bundle_hash`

T003 tests should be expected-red and fail only because the future module/API does not exist yet. T003 must not implement raw artifact persistence helpers.

## 16. Future T004 implementation guidance

`PHASE8-IMPL-018-T004` may implement minimal backend helpers only if separately authorized. Implementation should be standard-library-first, project-local paths only, manifest-backed writes, fail-closed validation, and no runtime extraction.

T004 must not call models, create candidates, call apply-promotion, mutate approved memory/canon, create training artifacts, or generate prose.

## 17. Future T005 bundle/index lifecycle guidance

`PHASE8-IMPL-018-T005` may implement bundle/index lifecycle and provenance linkage only if separately authorized. The index must be derived/rebuildable from manifests. Manifest-source/evidence/provenance linkage must be preserved. Stale/quarantine handling must fail closed.

T005 must not execute extraction, create candidates, or promote canon.

## 18. Future T006 safety regression guidance

`PHASE8-IMPL-018-T006` must prove:

- raw artifacts remain support data only
- raw artifacts are non-canon
- raw artifacts are non-candidate
- raw artifacts are non-training
- path traversal fails closed
- missing source/provenance fails closed
- unsupported artifact types fail closed
- raw artifact helpers do not trigger extraction
- raw artifact helpers do not call models
- raw artifact helpers do not call apply-promotion
- raw artifact helpers do not mutate approved memory/canon
- raw artifact helpers do not generate prose

## 19. Explicitly forbidden behavior

Forbidden behavior includes backend implementation in T002, frontend implementation in T002, product test changes in T002, raw artifact persistence runtime implementation in T002, raw artifact write/read/list helper implementation in T002, raw artifact storage file creation in T002, raw artifact index creation in T002, runtime extraction, BookNLP/spaCy install/run/import, model-assisted extraction, model/Ollama calls, NCP/Subtxt/dramatica-flow runtime calls, apply-promotion changes, approved memory/canon mutation, candidate creation from raw artifacts, review queue entry creation from raw artifacts, promotion audit creation from raw artifacts, generated prose, rewritten prose, continuation, outline generation, model prompts/completions as artifact files, training JSONL, dataset manifests, model artifacts, and package/dependency changes.

Generated prose and prose-production paths remain permanently forbidden.

## 20. Open follow-ups, if any

No unresolved product decision remains for T002. Follow-ups are implementation sequencing only:

- `PHASE8-IMPL-018-T003` ready/active next for expected-red raw artifact persistence contract tests.
- `PHASE8-IMPL-018-T004` planned for minimal backend helpers only if separately authorized.
- `PHASE8-IMPL-018-T005` planned for bundle/index lifecycle and provenance linkage only if separately authorized.
- `PHASE8-IMPL-018-T006` planned for safety regression proving support-data-only, non-canon, non-candidate, non-training, path-safe, fail-closed, no_runtime_extraction, no_booknlp_spacy_runtime, no_model_calls, no_apply_promotion, no_memory_canon_mutation, and no_generated_prose behavior.
- `PHASE8-IMPL-018-T007` planned for parent closeout.

