# PHASE8-IMPL-018-T002 Raw Artifact Persistence Boundary Decision

### Result

- Result: PASS.
- Scope: docs/status decision only.
- Parent task: `PHASE8-IMPL-018` - Raw artifact persistence implementation and project-local extraction artifact lifecycle.
- Completed child recorded: `PHASE8-IMPL-018-T002` - Raw artifact persistence boundary decision and manifest model.
- Decision record: `docs/roadmap/decisions/PHASE8-IMPL-018-raw-artifact-persistence-boundary-manifest-model-decision.md`.
- Active parent: `PHASE8-IMPL-018` MVP-required.
- Active/ready next child: `PHASE8-IMPL-018-T003` - Tests-first expected-red raw artifact persistence contract.
- Planned children: `PHASE8-IMPL-018-T004`, `PHASE8-IMPL-018-T005`, `PHASE8-IMPL-018-T006`, and `PHASE8-IMPL-018-T007`.
- Prior completed child: `PHASE8-IMPL-018-T001` complete/PASS and committed.
- Prior parent: `PHASE8-IMPL-017` remains complete/PASS through `PHASE8-IMPL-017-T007`.
- No context tools were run inside T002. Generated context artifacts remain evidence only, not roadmap truth or task completion.

### Files Changed

- Created: `docs/roadmap/decisions/PHASE8-IMPL-018-raw-artifact-persistence-boundary-manifest-model-decision.md`
- Updated: `docs/roadmap/tasks/PHASE8-IMPL-018.md`
- Updated: `docs/roadmap/inventory/PHASE8-IMPL-018.md`
- Updated: `docs/roadmap/enrichment/PHASE8-IMPL-018.enrichment.json`
- Updated: `docs/roadmap/implementation_status.md`
- Updated: `docs/roadmap/roadmap_index.yaml`
- Updated: `docs/roadmap/task_backlog.md`
- Updated: `docs/roadmap/phase_map.md`
- Updated: `docs/roadmap/validation/latest_roadmap_validation.md`
- Updated: `docs/roadmap/decision_log.md`
- Updated: `docs/roadmap/risk_register.md`
- Updated: `docs/roadmap/open_questions.md`
- Updated: `docs/master_plan.md`

### Decision Summary

- Raw artifacts are project-local support data only.
- Raw artifacts are not canon, not approved memory, not candidates by themselves, and not training data.
- Raw artifacts are not evidence by themselves unless linked to source/evidence/provenance records.
- Future storage root is `projects/{project_id}/writer_assistant/raw_artifacts/{raw_artifact_bundle_id}/`.
- Required future bundle layout includes `manifest.json`, `artifacts/`, `indexes/`, `quarantine/`, optional metadata-only `logs/`, and owner/admin-authored non-prose bundle notes if needed.
- Required manifest model includes `artifact_files`, `bundle_hash`, manifest/content hash, `source_refs`, `evidence_refs`, `provenance_refs`, `source_locator_refs`, validation/quarantine status, and boundary confirmations.
- Required artifact file model includes `artifact_file_id`, `artifact_type`, `relative_path`, `media_type`, `encoding`, `size_bytes`, `sha256`, record/line/schema metadata, source/evidence/provenance/source-locator refs, and `boundary_flags`.
- Raw artifact persistence must be path-safe and fail-closed.
- Invalid bundles, invalid paths, unsupported artifact types, missing source/provenance, and forbidden canon/candidate/training/model/prose/runtime markers are rejected or quarantined.
- Indexes are derived/rebuildable support/navigation data only and are not canon.
- Raw artifact persistence remains separate from apply-promotion and approved memory/canon mutation.
- Raw artifact persistence remains separate from runtime extraction, BookNLP/spaCy runtime, model/Ollama calls, NCP/Subtxt/dramatica-flow runtime, and generated prose.

### Future Guidance

- `PHASE8-IMPL-018-T003` is ready/active next and should add expected-red tests for future `backend.story_knowledge.raw_artifacts`.
- Target future APIs include `validate_raw_artifact_manifest`, `build_raw_artifact_manifest`, `validate_raw_artifact_file_ref`, `raw_artifact_bundle_storage_dir`, `raw_artifact_manifest_path`, `raw_artifact_index_path`, `write_raw_artifact_bundle`, `read_raw_artifact_manifest`, `read_raw_artifact_file`, `list_raw_artifact_bundles`, `rebuild_raw_artifact_index`, `quarantine_raw_artifact_bundle`, and `compute_raw_artifact_bundle_hash`.
- T004 may implement minimal backend helpers only if separately authorized, standard-library-first, project-local, manifest-backed, and fail-closed.
- T005 may implement derived/rebuildable bundle/index lifecycle and source/evidence/provenance linkage only if separately authorized.
- T006 must prove raw artifacts remain support data only, non-canon, non-candidate, non-training, path-safe, fail-closed, and do not trigger extraction, call models, call apply-promotion, mutate approved memory/canon, or generate prose.

### Boundary Confirmation

- No backend implementation code changes in T002.
- No frontend implementation code changes in T002.
- No product test changes in T002.
- No package/dependency changes.
- No raw artifact persistence runtime implementation.
- No raw artifact write/read/list helpers.
- No raw artifact files or indexes created.
- No runtime extraction.
- No BookNLP/spaCy install/run/import.
- No model/Ollama calls.
- No NCP/Subtxt/dramatica-flow runtime.
- No apply-promotion changes.
- No approved memory/canon mutation.
- No generated prose.
- No training/JSONL/dataset/model artifacts.
- No source-cache/generated context artifacts staged.
- No staging, commit, or push.

### MVP Scope Preservation

- `PHASE8-IMPL-018` remains MVP-required and active.
- `PHASE8-IMPL-019` remains future MVP-required for real BookNLP/spaCy install/run/import plus runtime extraction.
- `PHASE8-IMPL-020` remains future MVP-required for model-assisted evidence-backed extraction.
- `PHASE8-IMPL-021` remains future MVP-required for NCP/Subtxt/dramatica-flow analysis-only runtime integration.
- `PHASE8-IMPL-022` remains future MVP-required for end-to-end MVP usability validation.
- Fine-tuning remains deferred after MVP.
- Generated prose/prose-production paths remain permanently forbidden.

### Boundary Markers

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
