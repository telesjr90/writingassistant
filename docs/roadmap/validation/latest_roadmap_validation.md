# PHASE8-IMPL-020-T001 Publication

### Result

- Result: PASS.
- Scope: docs/status/governance publication only.
- Parent task: `PHASE8-IMPL-020` - Model-assisted evidence-backed extraction and diagnostic workflow.
- Parent status: active.
- Completed child recorded: `PHASE8-IMPL-020-T001` - Publish/activate model-assisted evidence-backed extraction parent.
- Active/ready next child: `PHASE8-IMPL-020-T002` - Model-assisted extraction and diagnostic workflow boundary decision.
- Planned children: `PHASE8-IMPL-020-T003`, `PHASE8-IMPL-020-T004`, `PHASE8-IMPL-020-T005`, `PHASE8-IMPL-020-T006`, and `PHASE8-IMPL-020-T007`.
- Prior parent: `PHASE8-IMPL-019` complete/PASS through `PHASE8-IMPL-019-T007`.
- Future MVP-required parents after this active parent: `PHASE8-IMPL-021` and `PHASE8-IMPL-022`.
- Fine-tuning remains deferred after MVP.
- Generated prose/prose-production paths remain permanently forbidden.
- PHASE8-UX-001 remained read-only terminology/boundary reference only.
- No context tools were run inside T001. Generated/context artifacts remain evidence only, not roadmap truth or task completion.

### Files Changed

- Created: `docs/roadmap/tasks/PHASE8-IMPL-020.md`
- Created: `docs/roadmap/inventory/PHASE8-IMPL-020.md`
- Created: `docs/roadmap/enrichment/PHASE8-IMPL-020.enrichment.json`
- Updated: `docs/master_plan.md`
- Updated: `docs/roadmap/implementation_status.md`
- Updated: `docs/roadmap/roadmap_index.yaml`
- Updated: `docs/roadmap/task_backlog.md`
- Updated: `docs/roadmap/phase_map.md`
- Updated: `docs/roadmap/validation/latest_roadmap_validation.md`
- Updated: `docs/roadmap/decision_log.md`
- Updated: `docs/roadmap/risk_register.md`
- Updated: `docs/roadmap/open_questions.md`

### Publication Summary

PHASE8-IMPL-020 publishes and activates the MVP-required model-assisted evidence-backed extraction and diagnostic workflow parent. Model-assisted output may produce evidence-backed candidate observations, diagnostic questions, uncertainty notes, or candidate extraction support only.

Future PHASE8-IMPL-020 contracts must preserve `source_refs`, `evidence_refs`, `provenance_refs`, and `source_locator_refs` when available. Model output is candidate-first and owner-review-required; confidence is not truth; model output is not canon; no automatic canon, no apply-promotion, no memory/canon mutation, no training artifacts, no generated prose, no rewrite, no continuation, no outline, no model output as truth, fail closed, and no silent fallback remain required.

PHASE8-UX-001 may be used only as read-only terminology/boundary reference. It is not roadmap truth, does not override master_plan, implementation_status, roadmap_index, or PHASE8-IMPL parent boundaries, and was not edited.

### Boundary Confirmation

- No backend implementation code changes.
- No frontend implementation code changes.
- No product test changes.
- No routes added.
- No UI added.
- No package/dependency changes.
- No model-assisted extraction implementation.
- No model/Ollama calls.
- No NCP/Subtxt/dramatica-flow runtime.
- No apply-promotion changes.
- No approved memory/canon mutation.
- No candidate/review queue creation.
- No generated prose.
- No training/JSONL/dataset/model artifacts.
- No source-cache/generated context artifacts staged.

### Future Guidance

- `PHASE8-IMPL-020-T002` is ready/active next and remains docs/decision only.
- `PHASE8-IMPL-020-T003` through `PHASE8-IMPL-020-T007` remain planned.
- `PHASE8-IMPL-021` remains the next parent after PHASE8-IMPL-020 closeout.
- `PHASE8-IMPL-022` remains the end-to-end MVP validation parent.
- Fine-tuning remains deferred after MVP.
- Generated prose/prose-production paths remain permanently forbidden.

# PHASE8-IMPL-019-T007 Parent Closeout

### Result

- Result: PASS.
- Scope: docs/status/governance parent closeout only.
- Parent task: `PHASE8-IMPL-019` - Guarded runtime extraction: real BookNLP/spaCy install/run/import and candidate-first extraction pipeline.
- Completed child recorded: `PHASE8-IMPL-019-T007` - Parent closeout.
- Parent result: complete/PASS.
- Completed child sequence: `PHASE8-IMPL-019-T001`, `PHASE8-IMPL-019-T002`, `PHASE8-IMPL-019-T003`, `PHASE8-IMPL-019-T004`, `PHASE8-IMPL-019-T005`, `PHASE8-IMPL-019-T006`, and `PHASE8-IMPL-019-T007` are complete/PASS.
- Next parent recommendation: `PHASE8-IMPL-020` - Model-assisted evidence-backed extraction and diagnostic workflow.
- PHASE8-IMPL-020 through PHASE8-IMPL-022 remain future MVP-required parents.
- Fine-tuning remains deferred after MVP.
- Generated prose/prose-production paths remain permanently forbidden.
- PHASE8-UX-001 remained read-only terminology/boundary reference only.
- No context tools were run for context generation. Generated/context artifacts remain evidence only, not roadmap truth or task completion.

### Files Changed

- Updated: `docs/roadmap/tasks/PHASE8-IMPL-019.md`
- Updated: `docs/roadmap/inventory/PHASE8-IMPL-019.md`
- Updated: `docs/roadmap/enrichment/PHASE8-IMPL-019.enrichment.json`
- Updated: `docs/master_plan.md`
- Updated: `docs/roadmap/implementation_status.md`
- Updated: `docs/roadmap/roadmap_index.yaml`
- Updated: `docs/roadmap/task_backlog.md`
- Updated: `docs/roadmap/phase_map.md`
- Updated: `docs/roadmap/validation/latest_roadmap_validation.md`
- Updated: `docs/roadmap/decision_log.md`
- Updated: `docs/roadmap/risk_register.md`
- Updated: `docs/roadmap/open_questions.md`

### Parent Closeout Summary

T001 published/activated the parent. T002 accepted the guarded runtime extraction boundary/environment model decision. T003 added expected-red runtime extraction contract tests. T004 implemented minimal guarded runtime extraction helper APIs. T005 implemented guarded request/raw artifact handoff and focused tests. T006 added runtime extraction safety regression and minimal hardening. T007 closes the parent.

Final artifacts are `backend/story_knowledge/runtime_extraction.py`, `tests/test_writer_assistant_core_runtime_extraction_contract.py`, `tests/test_writer_assistant_core_runtime_extraction_raw_artifact_handoff_contract.py`, `tests/test_writer_assistant_core_runtime_extraction_safety_regression.py`, and `docs/roadmap/decisions/PHASE8-IMPL-019-guarded-runtime-extraction-boundary-environment-model-decision.md`.

Final behavior includes explicit runtime extraction environment/availability states, BookNLP/spaCy availability/probe guard shape, path-safe request validation, owner-authored/owner-provided source boundary, source/evidence/provenance/source-locator ref preservation, deterministic plan building, transient probe result behavior, guarded fail-closed runtime execution shell, PHASE8-IMPL-018 raw artifact handoff persistence, candidate-review draft handoff only, quarantine handling, no silent fallback, and no full BookNLP/spaCy extraction over project text yet.

### Boundary Confirmation

- No package/dependency changes.
- No routes.
- No UI.
- No frontend changes.
- No full runtime extraction over project text.
- No model/Ollama calls.
- No NCP/Subtxt/dramatica-flow runtime.
- No apply-promotion changes.
- No approved memory/canon mutation.
- No candidate persistence/review queue creation.
- No training/JSONL/dataset/model artifacts.
- No generated prose.
- No staging, commit, or push performed.

### Future Guidance

- Commit T007 after review.
- Prepare `PHASE8-IMPL-020-T001` only after review.
- Keep PHASE8-IMPL-020 through PHASE8-IMPL-022 future MVP-required.
- Keep fine-tuning deferred after MVP.
- Keep generated prose/prose-production paths permanently forbidden.

# PHASE8-IMPL-019-T004 Minimal Guarded Runtime Extraction Helper

### Result

- Result: PASS.
- Scope: minimal backend helper plus roadmap/status updates.
- Parent task: `PHASE8-IMPL-019` - Guarded runtime extraction: real BookNLP/spaCy install/run/import and candidate-first extraction pipeline.
- Parent status: active.
- Completed child recorded: `PHASE8-IMPL-019-T004` - Minimal guarded dependency availability and import/run probe implementation.
- Prior completed children: `PHASE8-IMPL-019-T001`, `PHASE8-IMPL-019-T002`, and `PHASE8-IMPL-019-T003`.
- Active/ready next child: `PHASE8-IMPL-019-T005` - Guarded runtime extraction request and raw artifact handoff implementation.
- Planned children: `PHASE8-IMPL-019-T006` and `PHASE8-IMPL-019-T007`.
- Future MVP-required parents after `PHASE8-IMPL-019`: `PHASE8-IMPL-020`, `PHASE8-IMPL-021`, and `PHASE8-IMPL-022`.
- Fine-tuning remains deferred after MVP.
- Generated prose/prose-production paths remain permanently forbidden.
- PHASE8-UX-001 remained read-only terminology/boundary reference only.
- No context tools were run inside T004. Generated context artifacts remain evidence only, not roadmap truth or task completion.

### Files Changed

- Created: `backend/story_knowledge/runtime_extraction.py`
- Updated: `docs/roadmap/tasks/PHASE8-IMPL-019.md`
- Updated: `docs/roadmap/inventory/PHASE8-IMPL-019.md`
- Updated: `docs/roadmap/enrichment/PHASE8-IMPL-019.enrichment.json`
- Updated: `docs/master_plan.md`
- Updated: `docs/roadmap/implementation_status.md`
- Updated: `docs/roadmap/roadmap_index.yaml`
- Updated: `docs/roadmap/task_backlog.md`
- Updated: `docs/roadmap/phase_map.md`
- Updated: `docs/roadmap/validation/latest_roadmap_validation.md`
- Updated: `docs/roadmap/decision_log.md`
- Updated: `docs/roadmap/risk_register.md`
- Updated: `docs/roadmap/open_questions.md`

### Implementation Summary

`PHASE8-IMPL-019-T004` creates `backend/story_knowledge/runtime_extraction.py` as the minimal guarded runtime extraction helper. It implements `validate_runtime_extraction_environment`, `check_booknlp_availability`, `check_spacy_availability`, `validate_runtime_extraction_request`, `build_runtime_extraction_plan`, `run_runtime_extraction_probe`, `run_guarded_runtime_extraction`, `build_raw_artifact_handoff`, `build_candidate_review_handoff`, and `quarantine_runtime_extraction_output`.

The helper is disabled/fail-closed by default, separates dependency/import/probe availability from runtime extraction success, validates owner-authored or owner-provided request boundaries, rejects unsafe ids/paths, requires source/evidence/provenance/source-locator refs, builds deterministic side-effect-free plans, returns transient probe status, and produces draft-only raw artifact/candidate review handoff and quarantine shapes. Probe success is not runtime extraction success.

T004 does not install dependencies, edit package files, add routes/UI, run full runtime extraction over project text, call models/Ollama, persist candidates or review queue entries, mutate approved memory/canon, apply promotion, create training artifacts, or generate prose. Raw artifact persistence through PHASE8-IMPL-018 helpers remains future T005 scope.

### T005 Handoff

`PHASE8-IMPL-019-T005` is ready/active next for guarded runtime extraction request and raw artifact handoff implementation. It must preserve owner-authored or owner-provided source boundaries, PHASE8-IMPL-018 raw artifact support data vocabulary, candidate-first owner review handoff, explicit unavailable/quarantine states, and no automatic canon/apply-promotion/memory-canon mutation/model calls/training artifacts/generated prose.

### Boundary Confirmation

- Backend implementation limited to `backend/story_knowledge/runtime_extraction.py`.
- No frontend implementation code changes.
- No product test changes.
- No routes added.
- No UI added.
- No package/dependency changes.
- No dependency install.
- No full runtime extraction over project text.
- No BookNLP/spaCy package addition.
- No model/Ollama calls.
- No NCP/Subtxt/dramatica-flow runtime.
- No apply-promotion changes.
- No approved memory/canon mutation.
- No candidate/review queue creation.
- No generated prose.
- No training/JSONL/dataset/model artifacts.
- No source-cache/generated context artifacts staged.

### Future Guidance

- `PHASE8-IMPL-019-T005` is ready/active next.
- `PHASE8-IMPL-019-T006` and `PHASE8-IMPL-019-T007` remain planned.
- `PHASE8-IMPL-020` remains the next parent after `PHASE8-IMPL-019`.
- `PHASE8-IMPL-020` owns model-assisted extraction.
- `PHASE8-IMPL-021` owns NCP/Subtxt/dramatica-flow runtime.
- `PHASE8-IMPL-022` owns end-to-end MVP validation.
- Fine-tuning remains deferred after MVP.
- Generated prose/prose-production paths remain permanently forbidden.

# PHASE8-IMPL-019-T001 Publication

### Result

- Result: PASS.
- Scope: docs/status/governance publication only.
- Parent task: `PHASE8-IMPL-019` - Guarded runtime extraction: real BookNLP/spaCy install/run/import and candidate-first extraction pipeline.
- Parent status: active.
- Completed child recorded: `PHASE8-IMPL-019-T001` - Publish/activate guarded runtime extraction parent.
- Active/ready next child: `PHASE8-IMPL-019-T002` - Guarded runtime extraction boundary decision and environment model.
- Planned children: `PHASE8-IMPL-019-T003`, `PHASE8-IMPL-019-T004`, `PHASE8-IMPL-019-T005`, `PHASE8-IMPL-019-T006`, and `PHASE8-IMPL-019-T007`.
- Future MVP-required parents after `PHASE8-IMPL-019`: `PHASE8-IMPL-020`, `PHASE8-IMPL-021`, and `PHASE8-IMPL-022`.
- Fine-tuning remains deferred after MVP.
- Generated prose/prose-production paths remain permanently forbidden.
- PHASE8-UX-001 remained read-only terminology/boundary reference only.
- No context tools were run inside T001. Generated context artifacts remain evidence only, not roadmap truth or task completion.

### Files Changed

- Created: `docs/roadmap/tasks/PHASE8-IMPL-019.md`
- Created: `docs/roadmap/inventory/PHASE8-IMPL-019.md`
- Created: `docs/roadmap/enrichment/PHASE8-IMPL-019.enrichment.json`
- Updated: `docs/master_plan.md`
- Updated: `docs/roadmap/implementation_status.md`
- Updated: `docs/roadmap/roadmap_index.yaml`
- Updated: `docs/roadmap/task_backlog.md`
- Updated: `docs/roadmap/phase_map.md`
- Updated: `docs/roadmap/validation/latest_roadmap_validation.md`
- Updated: `docs/roadmap/decision_log.md`
- Updated: `docs/roadmap/risk_register.md`
- Updated: `docs/roadmap/open_questions.md`

### Publication Summary

Deliver real BookNLP/spaCy install/run/import checks and guarded runtime extraction from owner-authored or owner-provided project text into raw artifact bundles and candidate-first review handoff, without canon mutation, model calls, automatic apply-promotion, training artifacts, or generated prose.

Runtime extraction in PHASE8-IMPL-019 may be introduced only through explicitly scoped children after T001 and may run only over owner-authored or owner-provided project text/materials. Output is candidate-first and owner-review-gated; runtime extraction output is never canon by itself, raw tool output is never authoritative by itself, extractor confidence is not truth, and extractor output cannot mutate approved memory/canon, apply promotion, create training data, or generate prose. Raw artifacts must be persisted through PHASE8-IMPL-018 helpers. Candidate persistence/review queue handoff may use existing candidate/review infrastructure only when explicitly scoped. Apply-promotion remains the separate PHASE8-IMPL-017 owner-confirmed path. Missing tools, missing models, unsafe paths, missing source/evidence/provenance, invalid source locators, malformed tool outputs, or unavailable environment must fail-closed or return explicit unavailable/quarantined state. No silent fallback may claim extraction succeeded.

Future runtime extraction contracts must preserve `source_refs`, `evidence_refs`, `provenance_refs`, and `source_locator_refs`; use PHASE8-IMPL-018 raw artifact persistence; return candidate-first handoff for owner review; and distinguish availability, unavailable, quarantine, fail-closed, malformed output, unsafe path, and missing evidence/provenance states. The install_import_run boundary is published for later children only.

PHASE8-UX-001 was used only as a read-only terminology/boundary reference for labels such as review, candidate, evidence, provenance, source locator, raw artifact, approved memory/canon, owner action, unavailable/quarantined state, and no automatic canon. PHASE8-UX-001 is not roadmap truth, does not override master_plan, implementation_status, roadmap_index, or PHASE8-IMPL parent boundaries, and was not edited.

### Boundary Confirmation

- No backend implementation code changes.
- No frontend implementation code changes.
- No product test changes.
- No routes added.
- No UI added.
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

- `PHASE8-IMPL-019-T002` is ready/active next and remains docs/decision only.
- `PHASE8-IMPL-020` remains the next parent after `PHASE8-IMPL-019`.
- `PHASE8-IMPL-020` through `PHASE8-IMPL-022` remain future MVP-required parents.
- Fine-tuning remains deferred after MVP.
- Generated prose/prose-production paths remain permanently forbidden.

# PHASE8-IMPL-018-T007 Parent Closeout

### Result

- Result: PASS.
- Scope: docs/status/governance parent closeout only.
- Parent task: `PHASE8-IMPL-018` - Raw artifact persistence implementation and project-local extraction artifact lifecycle.
- Completed child recorded: `PHASE8-IMPL-018-T007` - Parent closeout.
- Parent result: complete/PASS.
- Completed child sequence: `PHASE8-IMPL-018-T001`, `PHASE8-IMPL-018-T002`, `PHASE8-IMPL-018-T003`, `PHASE8-IMPL-018-T004`, `PHASE8-IMPL-018-T005`, `PHASE8-IMPL-018-T006`, and `PHASE8-IMPL-018-T007` are complete/PASS.
- Delivered decision: `docs/roadmap/decisions/PHASE8-IMPL-018-raw-artifact-persistence-boundary-manifest-model-decision.md`.
- Delivered backend helper: `backend/story_knowledge/raw_artifacts.py`.
- Delivered contracts/regressions: `tests/test_writer_assistant_core_raw_artifacts_contract.py`, `tests/test_writer_assistant_core_raw_artifact_lifecycle_contract.py`, and `tests/test_writer_assistant_core_raw_artifact_safety_regression.py`.
- Active/ready next parent: `PHASE8-IMPL-019` - Real BookNLP/spaCy install/run/import and runtime extraction pipeline.
- Future MVP-required parents after `PHASE8-IMPL-019`: `PHASE8-IMPL-020`, `PHASE8-IMPL-021`, and `PHASE8-IMPL-022`.
- Fine-tuning remains deferred after MVP.
- Generated prose/prose-production paths remain permanently forbidden.
- No context tools were run inside T007. Generated context artifacts remain evidence only, not roadmap truth or task completion.

### Files Changed

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

### Parent Closeout Summary

- Raw artifact persistence is manifest-backed by `manifest.json`, bundle-based, index-aware, project-local, path-safe, quarantine-aware, evidence/provenance-linked, and fail-closed.
- Implemented APIs include `validate_raw_artifact_manifest`, `build_raw_artifact_manifest`, `validate_raw_artifact_file_ref`, `raw_artifact_bundle_storage_dir`, `raw_artifact_manifest_path`, `raw_artifact_index_path`, `write_raw_artifact_bundle`, `read_raw_artifact_manifest`, `read_raw_artifact_file`, `list_raw_artifact_bundles`, `rebuild_raw_artifact_index`, `quarantine_raw_artifact_bundle`, and `compute_raw_artifact_bundle_hash`.
- Delivered behavior includes valid-only default listing/indexing, derived/rebuildable support-data indexes, `source_refs`, `evidence_refs`, `provenance_refs`, `source_locator_refs`, quarantine handling, superseded/deleted_tombstone exclusion by default, duplicate/idempotency handling, canonical deterministic bundle hashing, and fail-closed validation.
- Raw artifacts remain support data only, not canon, not approved memory, not candidates, and not training data.

### Boundary Confirmation

- No runtime extraction.
- No real BookNLP/spaCy install/run/import.
- No model-assisted extraction.
- No model/Ollama calls.
- No NCP/Subtxt/dramatica-flow runtime.
- No routes added.
- No UI added.
- No package/dependency changes.
- No apply-promotion changes.
- No approved memory/canon mutation beyond the existing `PHASE8-IMPL-017` path.
- No candidate/review queue creation.
- No generated prose.
- No training/JSONL/dataset/model artifacts.
- No source-cache/generated context artifacts staged.

### Future Guidance

- `PHASE8-IMPL-019` is ready/active next only as a future MVP-required parent handoff for real BookNLP/spaCy install/run/import plus runtime extraction.
- `PHASE8-IMPL-019` must be bounded by environment guards, source/evidence/provenance requirements, raw artifact persistence support from `PHASE8-IMPL-018`, candidate-first output, owner review, no automatic canon, no generated prose, and no apply-promotion unless explicitly owner-confirmed through the existing separate path.
- Do not implement `PHASE8-IMPL-019` until separately scoped.

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
