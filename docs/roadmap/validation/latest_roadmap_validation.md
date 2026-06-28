# PHASE8-IMPL-018-T003 Expected-Red Raw Artifact Persistence Contract

### Result

- Result: PASS.
- Scope: tests/docs/status expected-red contract handoff only.
- Parent task: `PHASE8-IMPL-018` - Raw artifact persistence implementation and project-local extraction artifact lifecycle.
- Completed child recorded: `PHASE8-IMPL-018-T003` - Tests-first expected-red raw artifact persistence contract.
- Expected-red test file: `tests/test_writer_assistant_core_raw_artifacts_contract.py`.
- Expected-red target: future `backend.story_knowledge.raw_artifacts` module/API.
- Active parent: `PHASE8-IMPL-018` MVP-required.
- Active/ready next child: `PHASE8-IMPL-018-T004` - Minimal backend raw artifact persistence helper implementation.
- Planned children: `PHASE8-IMPL-018-T005`, `PHASE8-IMPL-018-T006`, and `PHASE8-IMPL-018-T007`.
- Prior completed child: `PHASE8-IMPL-018-T002` complete/PASS and committed.
- Prior parent: `PHASE8-IMPL-017` remains complete/PASS through `PHASE8-IMPL-017-T007`.
- No context tools were run inside T003. Generated context artifacts remain evidence only, not roadmap truth or task completion.

### Files Changed

- Created: `tests/test_writer_assistant_core_raw_artifacts_contract.py`
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

### Expected-Red Contract Summary

- Future module/API import contract targets `backend.story_knowledge.raw_artifacts`.
- Target future APIs include `validate_raw_artifact_manifest`, `build_raw_artifact_manifest`, `validate_raw_artifact_file_ref`, `raw_artifact_bundle_storage_dir`, `raw_artifact_manifest_path`, `raw_artifact_index_path`, `write_raw_artifact_bundle`, `read_raw_artifact_manifest`, `read_raw_artifact_file`, `list_raw_artifact_bundles`, `rebuild_raw_artifact_index`, `quarantine_raw_artifact_bundle`, and `compute_raw_artifact_bundle_hash`.
- Manifest validation coverage requires `schema_version`, `raw_artifact_bundle_id`, `project_id`, `created_at`, `updated_at`, `status`, `artifact_source_type`, `artifact_source_id`, `extraction_run_id`, `source_refs`, `evidence_refs`, `provenance_refs`, `source_locator_refs`, tool/adapter/pipeline metadata, `artifact_files`, `bundle_hash`, manifest/content hash, `boundary_flags`, `validation_status`, `quarantine_reason`, and no-runtime/no-prose/no-training/no-apply-promotion/no-memory-canon mutation confirmations.
- Artifact file reference coverage requires `artifact_file_id`, `artifact_type`, `relative_path`, `media_type`, `encoding`, `size_bytes`, `sha256`, count/schema/parser metadata, `source_locator_refs`, `evidence_refs`, `provenance_refs`, and `boundary_flags`.
- Status and artifact type coverage allow only support data values and reject unknown status or forbidden canon/candidate/training/model/prose/runtime destinations.
- Project-local path safety coverage rejects absolute paths, path traversal, unsafe project ids, unsafe raw artifact bundle ids, unsafe artifact file ids, symlink-like patterns, reserved path patterns, and writes outside project root.
- Source/evidence/provenance coverage requires source and provenance linkage for valid bundles, evidence linkage when supporting evidence workflows, and source locator linkage when offsets/spans/records are available.
- Bundle write/read/list/index/quarantine/hash coverage specifies validation-first writes, manifest plus artifact files only, valid manifest/file reads only, quarantine exclusion by default, derived/rebuildable support-data indexes, deterministic hashes, and duplicate/conflicting bundle fail-closed behavior.
- Boundary coverage confirms raw artifact persistence remains support data, not canon, not candidates, not training data, with no_runtime_extraction, no_model_calls, no_apply_promotion, no_memory_canon_mutation, and no_generated_prose.
- Expected-red failure shape is limited to `ModuleNotFoundError`/`ImportError` for missing future `backend.story_knowledge.raw_artifacts` module/API.

### Boundary Confirmation

- No backend implementation code changes in T003.
- No frontend implementation code changes in T003.
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

### Future Guidance

- `PHASE8-IMPL-018-T004` is ready/active next and may implement minimal backend raw artifact persistence helpers only if separately authorized.
- `PHASE8-IMPL-018-T005` through `PHASE8-IMPL-018-T007` remain planned.
- `PHASE8-IMPL-019` through `PHASE8-IMPL-022` remain future MVP-required parents.
- Fine-tuning remains deferred after MVP.
- Generated prose/prose-production paths remain permanently forbidden.
