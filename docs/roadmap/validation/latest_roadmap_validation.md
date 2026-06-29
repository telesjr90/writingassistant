# PHASE8-IMPL-018-T006 Raw Artifact Safety Regression

### Result

- Result: PASS.
- Scope: raw artifact safety regression coverage only.
- Parent task: `PHASE8-IMPL-018` - Raw artifact persistence implementation and project-local extraction artifact lifecycle.
- Completed child recorded: `PHASE8-IMPL-018-T006` - Raw artifact safety regression: non-canon, non-training, path-safe, no extraction.
- Safety regression test: `tests/test_writer_assistant_core_raw_artifact_safety_regression.py` PASS.
- Existing raw artifact contract: `tests/test_writer_assistant_core_raw_artifacts_contract.py` PASS.
- Existing raw artifact lifecycle/provenance contract: `tests/test_writer_assistant_core_raw_artifact_lifecycle_contract.py` PASS.
- Active parent: `PHASE8-IMPL-018` MVP-required.
- Active/ready next child: `PHASE8-IMPL-018-T007` - Parent closeout.
- Future MVP-required parents: `PHASE8-IMPL-019`, `PHASE8-IMPL-020`, `PHASE8-IMPL-021`, and `PHASE8-IMPL-022`.
- Prior completed child: `PHASE8-IMPL-018-T005` complete/PASS and committed.
- Prior parent: `PHASE8-IMPL-017` remains complete/PASS through `PHASE8-IMPL-017-T007`.
- No context tools were run inside T006. Generated context artifacts remain evidence only, not roadmap truth or task completion.

### Files Changed

- Created: `tests/test_writer_assistant_core_raw_artifact_safety_regression.py`
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

### Safety Regression Summary

- Raw artifacts remain support data only, not canon, not candidates, and not training data.
- Operations are path-safe and fail-closed for unsafe ids, unsafe `relative_path`, missing/unreferenced/hash-mismatched artifact files, invalid manifests, invalid JSON manifests, unsupported statuses, unsupported artifact types, forbidden destination/action fields, missing refs, missing or false boundary confirmations, duplicate conflicts, and quarantine state.
- Tests cover `source_refs`, `evidence_refs`, `provenance_refs`, `source_locator_refs`, `quarantine_reason`, `no_generated_prose_confirmation`, `no_model_call_confirmation`, `no_training_artifact_confirmation`, `no_apply_promotion_confirmation`, `no_memory_canon_mutation_confirmation`, and `no_runtime_extraction_confirmation`.
- Forbidden markers covered include `generated_prose`, `rewritten_prose`, `continuation`, `outline`, `training_jsonl`, `dataset_manifest`, `model_artifact`, `runtime_extraction_trigger`, `promotion_record`, `approved_memory`, `candidate_record`, and `review_queue_entry`.
- No minimal backend hardening patch was required after preserving the accepted raw artifact API boundary.

### Boundary Confirmation

- No routes added.
- No frontend implementation code changes.
- No package/dependency changes.
- No runtime extraction.
- No BookNLP/spaCy install/run/import.
- No model/Ollama calls.
- No NCP/Subtxt/dramatica-flow runtime.
- No apply-promotion changes.
- No approved memory/canon mutation.
- No candidate/review queue creation.
- No generated prose.
- No training/JSONL/dataset/model artifacts.
- No source-cache/generated context artifacts staged.

### Future Guidance

- `PHASE8-IMPL-018-T007` is ready/active next and remains limited to parent closeout.
- `PHASE8-IMPL-019` through `PHASE8-IMPL-022` remain future MVP-required parents.
- Fine-tuning remains deferred after MVP.
- Generated prose/prose-production paths remain permanently forbidden.

# PHASE8-IMPL-018-T005 Raw Artifact Bundle/Index Lifecycle And Provenance Linkage

### Result

- Result: PASS.
- Scope: raw artifact bundle/index lifecycle and provenance linkage hardening plus focused tests/docs/status alignment only.
- Parent task: `PHASE8-IMPL-018` - Raw artifact persistence implementation and project-local extraction artifact lifecycle.
- Completed child recorded: `PHASE8-IMPL-018-T005` - Raw artifact bundle/index lifecycle and provenance linkage.
- Backend helper: `backend/story_knowledge/raw_artifacts.py`.
- Lifecycle/provenance test: `tests/test_writer_assistant_core_raw_artifact_lifecycle_contract.py` PASS.
- Contract test: `tests/test_writer_assistant_core_raw_artifacts_contract.py` PASS.
- Active parent: `PHASE8-IMPL-018` MVP-required.
- Active/ready next child: `PHASE8-IMPL-018-T006` - Raw artifact safety regression: non-canon, non-training, path-safe, no extraction.
- Planned child: `PHASE8-IMPL-018-T007`.
- Future MVP-required parents: `PHASE8-IMPL-019`, `PHASE8-IMPL-020`, `PHASE8-IMPL-021`, and `PHASE8-IMPL-022`.
- Prior completed child: `PHASE8-IMPL-018-T004` complete/PASS and committed with the minimal backend helper.
- Prior parent: `PHASE8-IMPL-017` remains complete/PASS through `PHASE8-IMPL-017-T007`.
- No context tools were run inside T005. Generated context artifacts remain evidence only, not roadmap truth or task completion.

### Files Changed

- Updated: `backend/story_knowledge/raw_artifacts.py`
- Updated: `tests/test_writer_assistant_core_raw_artifacts_contract.py`
- Created: `tests/test_writer_assistant_core_raw_artifact_lifecycle_contract.py`
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

### Lifecycle/Provenance Summary

- `backend/story_knowledge/raw_artifacts.py` hardens `pending_validation`, `valid`, `rejected`, `quarantined`, `superseded`, and `deleted_tombstone` lifecycle behavior.
- `list_raw_artifact_bundles` and `rebuild_raw_artifact_index` default to valid bundles only.
- Indexes are derived rebuildable support data, not canon, not candidates, and not training data.
- Index entries include safe manifest metadata: `raw_artifact_bundle_id`, `status`, `artifact_source_type`, `artifact_source_id`, `extraction_run_id`, `source_refs`, `evidence_refs`, `provenance_refs`, `source_locator_refs`, artifact file summaries, `bundle_hash`, `manifest_hash` or `content_hash`, `validation_status`, `created_at`, and `updated_at`.
- Valid bundle validation preserves source/evidence/provenance/source locator refs and fails closed when required linkage is missing.
- Artifact file refs preserve `artifact_file_id`, `artifact_type`, `relative_path`, `sha256`, source locator refs, evidence refs, provenance refs, and boundary flags.
- Missing, invalid, stale, non-valid, path-escaping, hash-mismatched, and unreferenced artifact files are excluded from valid support behavior or fail closed.
- Quarantine preserves `quarantine_reason` and safe refs while excluding the bundle from valid listing/indexing.
- Superseded and deleted_tombstone bundles are retained but excluded from default valid listing/indexing.
- Duplicate identical writes remain deterministic and conflicting duplicate writes fail closed.
- `compute_raw_artifact_bundle_hash` remains deterministic with canonical JSON/sorted keys and changes when artifact refs/content metadata change.

### Boundary Confirmation

- No routes added.
- No frontend implementation code changes.
- No package/dependency changes.
- No runtime extraction.
- No BookNLP/spaCy install/run/import.
- No model/Ollama calls.
- No NCP/Subtxt/dramatica-flow runtime.
- No apply-promotion changes.
- No approved memory/canon mutation.
- No candidate/review workflow creation.
- No generated prose.
- No training/JSONL/dataset/model artifacts.
- No source-cache/generated context artifacts staged.

### Future Guidance

- `PHASE8-IMPL-018-T006` is ready/active next and remains limited to safety regression coverage proving raw artifacts remain support data only, path-safe, fail-closed, non-canon, non-candidate, non-training-data, no_runtime_extraction, no_booknlp_spacy_runtime, no_model_calls, no_apply_promotion, no_memory_canon_mutation, and no_generated_prose.
- `PHASE8-IMPL-018-T007` remains planned.
- `PHASE8-IMPL-019` through `PHASE8-IMPL-022` remain future MVP-required parents.
- Fine-tuning remains deferred after MVP.
- Generated prose/prose-production paths remain permanently forbidden.

# PHASE8-IMPL-018-T004 Minimal Backend Raw Artifact Persistence Helper

### Result

- Result: PASS.
- Scope: minimal backend raw artifact persistence helper plus docs/status alignment only.
- Parent task: `PHASE8-IMPL-018` - Raw artifact persistence implementation and project-local extraction artifact lifecycle.
- Completed child recorded: `PHASE8-IMPL-018-T004` - Minimal backend raw artifact persistence helper implementation.
- Backend helper: `backend/story_knowledge/raw_artifacts.py`.
- Contract test: `tests/test_writer_assistant_core_raw_artifacts_contract.py` PASS.
- Active parent: `PHASE8-IMPL-018` MVP-required.
- Active/ready next child: `PHASE8-IMPL-018-T005` - Raw artifact bundle/index lifecycle and provenance linkage.
- Planned children: `PHASE8-IMPL-018-T006` and `PHASE8-IMPL-018-T007`.
- Future MVP-required parents: `PHASE8-IMPL-019`, `PHASE8-IMPL-020`, `PHASE8-IMPL-021`, and `PHASE8-IMPL-022`.
- Prior completed child: `PHASE8-IMPL-018-T003` complete/PASS and committed as expected-red contract handoff.
- Prior parent: `PHASE8-IMPL-017` remains complete/PASS through `PHASE8-IMPL-017-T007`.
- No context tools were run inside T004. Generated context artifacts remain evidence only, not roadmap truth or task completion.

### Files Changed

- Created: `backend/story_knowledge/raw_artifacts.py`
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

### Backend Helper Summary

- `backend/story_knowledge/raw_artifacts.py` implements `validate_raw_artifact_manifest`, `build_raw_artifact_manifest`, `validate_raw_artifact_file_ref`, `raw_artifact_bundle_storage_dir`, `raw_artifact_manifest_path`, `raw_artifact_index_path`, `write_raw_artifact_bundle`, `read_raw_artifact_manifest`, `read_raw_artifact_file`, `list_raw_artifact_bundles`, `rebuild_raw_artifact_index`, `quarantine_raw_artifact_bundle`, and `compute_raw_artifact_bundle_hash`.
- Manifest validation is fail-closed and requires required fields, allowed lifecycle statuses, source/evidence/provenance/source locator linkage for valid bundles, manifest/content hash presence, boundary flags, and no-runtime/no-prose/no-training/no-apply-promotion/no-memory-canon mutation confirmations.
- Artifact file validation allows support data artifact types only, requires path-safe `relative_path`, `artifact_file_id`, `sha256`, media/encoding/count/schema/parser fields, evidence/provenance/source locator refs, and boundary flags.
- Path helpers keep storage under `projects/{project_id}/writer_assistant/raw_artifacts/{raw_artifact_bundle_id}/` with deterministic `manifest.json`, `artifacts/`, `indexes/`, and `quarantine/` layout.
- Write/read/list/index/quarantine/hash helpers validate before write, avoid partial writes on validation failure, read only manifest-referenced files, exclude quarantined/rejected bundles by default, build rebuildable support-data indexes, record quarantine reasons, and compute deterministic hashes.
- Duplicate bundle ids are deterministic: identical manifests return the same result; conflicting manifests fail closed.

### Boundary Confirmation

- No routes added.
- No frontend implementation code changes.
- No package/dependency changes.
- No runtime extraction.
- No BookNLP/spaCy install/run/import.
- No model/Ollama calls.
- No NCP/Subtxt/dramatica-flow runtime.
- No apply-promotion changes.
- No approved memory/canon mutation.
- No candidate/review workflow creation.
- No generated prose.
- No training/JSONL/dataset/model artifacts.
- No source-cache/generated context artifacts staged.

### Future Guidance

- `PHASE8-IMPL-018-T005` is ready/active next and remains limited to raw artifact bundle/index lifecycle and provenance linkage.
- `PHASE8-IMPL-018-T006` through `PHASE8-IMPL-018-T007` remain planned.
- `PHASE8-IMPL-019` through `PHASE8-IMPL-022` remain future MVP-required parents.
- Fine-tuning remains deferred after MVP.
- Generated prose/prose-production paths remain permanently forbidden.

## PHASE8-UX-001 - Master Plan UX / Navigation Proposal

Validation status: Planned / pending execution.

Expected checks before and after the docs-only UX proposal task:

- `python3 scripts/check_enrichment.py`
- `python3 scripts/validate_roadmap.py`
- `git diff --check`
- `git status --short --branch`

Expected outputs:

- `docs/roadmap/ux/PHASE8-UX-001-master-plan-ux-navigation-proposal.md`
- `docs/roadmap/ux/PHASE8-UX-001-impeccable-ui-ux-qa-workflow.md`

Generated context evidence, if collected, must remain under `.codex-context/PHASE8-UX-001/` and must not be staged.
