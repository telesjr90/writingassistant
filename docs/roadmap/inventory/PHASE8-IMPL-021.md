# PHASE8-IMPL-021 Inventory

## 1. Task Identity

- Parent ID: `PHASE8-IMPL-021`
- Title: Analysis-only NCP/Subtxt/dramatica-flow runtime integration
- Track: Writer Assistant Core
- Phase: Phase 8
- Status: active MVP-required parent; `PHASE8-IMPL-021-T001` complete/PASS; `PHASE8-IMPL-021-T002` complete/PASS; `PHASE8-IMPL-021-T003` complete/PASS as tests-first expected-red contract tests only; `PHASE8-IMPL-021-T004` complete/PASS as minimal pure analysis runtime request/allowlist guard helper implementation; `PHASE8-IMPL-021-T005` ready/active next
- Depends on: completed/PASS `PHASE8-IMPL-020` through `PHASE8-IMPL-020-T007`
- Completed children: `PHASE8-IMPL-021-T001` - Publish/activate analysis-only NCP/Subtxt/dramatica-flow runtime integration parent; `PHASE8-IMPL-021-T002` - Analysis-only runtime integration boundary and allowlist decision; `PHASE8-IMPL-021-T003` - Expected-red NCP/Subtxt/dramatica-flow runtime integration contract tests; `PHASE8-IMPL-021-T004` - Minimal analysis-only runtime request/allowlist guard implementation
- Current child: `PHASE8-IMPL-021-T005` - Evidence-backed runtime output handoff implementation
- Next child status: ready/active
- Planned children: `PHASE8-IMPL-021-T006` and `PHASE8-IMPL-021-T007`
- Future MVP-required parent after this: `PHASE8-IMPL-022`

## 2. Why This Parent Exists

PHASE8-IMPL-020 delivered the model-assisted evidence-backed extraction and diagnostic workflow boundary, pure guards, in-memory handoff objects, and safety regression without NCP/Subtxt/dramatica-flow runtime integration.

PHASE8-IMPL-021 now publishes the final analysis-runtime integration parent before end-to-end MVP validation. The parent exists to define and later implement controlled NCP/Subtxt/dramatica-flow integration only inside analysis-only Writer Assistant Core boundaries.

## 3. Boundary Summary

NCP may be used as structured context interchange only. Subtxt may be used as rubric/diagnostic guidance only. dramatica-flow may be used only through audited allowlists that block prose, rewrite, continuation, outline, draft, revision, polish, expansion, style imitation, chapter generation, write/revise, export-as-prose, or story-prose paths.

Runtime outputs must be candidate-first, owner-review-required, evidence-backed, provenance-backed, and source-locator-backed when available. Future request/output vocabulary must preserve `source_refs`, `evidence_refs`, `provenance_refs`, and `source_locator_refs`.

Confidence is not truth. Tool output is not canon. Tool output is not truth. No model output as truth. No automatic canon. No apply-promotion. No memory/canon mutation. No training artifacts. No generated prose. No rewrite. No continuation. No outline. Fail closed. No silent fallback. Owner review remains mandatory and apply-promotion remains the separate explicit audited owner-confirmed path.

T001 publication creates docs/status/governance records only. No backend implementation code, frontend code, tests, package/dependency files, NCP runtime, Subtxt runtime, dramatica-flow runtime, cloned repositories, dependency installs, model/Ollama calls, BookNLP/spaCy extraction, candidate persistence, review queue entries, apply-promotion changes, approved memory/canon mutation, generated prose, or training/JSONL/dataset/model artifacts are created or changed by T001.

T002 creates the analysis-only runtime integration boundary and audited allowlist decision as docs/decision only. NCP is structured context interchange only. Subtxt is rubric/diagnostic guidance only. dramatica-flow is usable only through audited allowlists. Future allowlist records require `tool_name`, `module_or_feature_name`, `allowed_action`, `forbidden_actions`, `output_classes_allowed`, `output_classes_forbidden`, `required_refs`, `source_locator_policy`, `evidence_policy`, `provenance_policy`, `owner_review_policy`, `fail_closed_policy`, `no_silent_fallback_policy`, `no_prose_policy`, `no_training_policy`, `no_canon_policy`, `no_apply_promotion_policy`, `validation_tests_required`, and `audit_notes`.

T002 allows only analysis-only output classes such as `evidence_backed_candidate_observation`, `diagnostic_question`, `uncertainty_note`, `insufficient_evidence_note`, `rubric_mapping_support`, `context_interchange_support`, `quarantined_result`, `unavailable_result`, `fail_closed_result`, `refused_no_prose`, and `blocked_request`. It forbids `generated_prose`, `rewritten_prose`, `continuation`, `outline`, `chapter_generation`, `draft`, `revision`, `polish`, `improvement`, `expansion`, `style_imitation`, `export_as_prose`, `story_prose`, `training_jsonl`, `dataset_manifest`, `model_artifact`, `promotion_record`, `approved_memory`, `canon`, `storyform_truth`, `scene_mutation`, `note_mutation`, and `material_mutation`.

T002 implemented no runtime, code, tests, routes, UI, dependency, model, persistence, canon, promotion, training, or generated-prose changes.

T003 adds expected-red contract tests only at `tests/test_writer_assistant_core_analysis_runtime_integration_contract.py` for the future `backend.story_knowledge.analysis_runtime_integration` helper. The expected future public APIs are `validate_analysis_runtime_allowlist_record`, `validate_analysis_runtime_request`, `build_analysis_runtime_plan`, `validate_analysis_runtime_output`, `build_analysis_runtime_candidate_support`, `build_analysis_runtime_diagnostic_questions`, `quarantine_analysis_runtime_output`, and `run_guarded_analysis_runtime_integration`. T003 records the tests-first expected-red contract for allowlist validation, request validation, deterministic in-memory plan building, output validation, candidate support, diagnostic questions, quarantine/fail-closed runtime behavior, and NCP/Subtxt/dramatica-flow boundaries. T003 implemented no runtime, helper implementation, routes, UI, dependency changes, model calls, persistence, canon, promotion, training, or generated-prose behavior.

T004 creates the minimal pure analysis runtime request/allowlist guard helper at `backend/story_knowledge/analysis_runtime_integration.py`. The implemented public APIs are `validate_analysis_runtime_allowlist_record`, `validate_analysis_runtime_request`, `build_analysis_runtime_plan`, `validate_analysis_runtime_output`, `build_analysis_runtime_candidate_support`, `build_analysis_runtime_diagnostic_questions`, `quarantine_analysis_runtime_output`, and `run_guarded_analysis_runtime_integration`. The helper validates audited allowlist records, request confirmations and refs, deterministic in-memory non-executing plans, output classes, candidate-first support, diagnostic questions, quarantine records, and explicit fail-closed/unavailable/blocked states. T004 added no NCP/Subtxt/dramatica-flow execution, no routes, no UI, no frontend changes, no package/dependency changes, no model/Ollama calls, no persistence, no canon mutation, no apply-promotion, no training artifacts, and no generated prose behavior.

PHASE8-UX-001 is read-only terminology/boundary reference only. It is not roadmap truth and was not edited.

## 4. Child Sequence

- `PHASE8-IMPL-021-T001` - Publish/activate analysis-only NCP/Subtxt/dramatica-flow runtime integration parent. complete/PASS. Output/scope: task record, inventory, enrichment JSON, roadmap/status/governance alignment; docs/status only.
- `PHASE8-IMPL-021-T002` - Analysis-only runtime integration boundary and allowlist decision. complete/PASS. Output/scope: docs/decision only; defines the audited allowlist, blocked prose/outline/write/revise/export paths, NCP/Subtxt/dramatica-flow role boundaries, evidence/provenance/source-locator requirements, request/output/state vocabulary, fail-closed state vocabulary, and no silent fallback.
- `PHASE8-IMPL-021-T003` - Expected-red NCP/Subtxt/dramatica-flow runtime integration contract tests. complete/PASS. Output/scope: tests-first expected-red contract only; absent future import target `backend.story_knowledge.analysis_runtime_integration`; no helper implementation, runtime, routes, UI, dependency changes, model calls, persistence, canon, promotion, training, or generated-prose behavior.
- `PHASE8-IMPL-021-T004` - Minimal analysis-only runtime request/allowlist guard implementation. complete/PASS. Output/scope: `backend/story_knowledge/analysis_runtime_integration.py`; pure in-memory allowlist/request/output/state guards only; no NCP/Subtxt/dramatica-flow execution, no routes/UI/frontend/package changes, no model/Ollama calls, no persistence, no canon mutation, no apply-promotion, no training artifacts, no generated prose.
- `PHASE8-IMPL-021-T005` - Evidence-backed runtime output handoff implementation. ready/active next.
- `PHASE8-IMPL-021-T006` - Analysis-only runtime integration safety regression. planned.
- `PHASE8-IMPL-021-T007` - Parent closeout. planned.

## 5. Existing Model-assisted Context

- Present/read-only context: `backend/story_knowledge/model_assisted_extraction.py`
- Present/read-only context: `tests/test_writer_assistant_core_model_assisted_extraction_contract.py`
- Present/read-only context: `tests/test_writer_assistant_core_model_assisted_extraction_handoff_contract.py`
- Present/read-only context: `tests/test_writer_assistant_core_model_assisted_extraction_safety_regression.py`
- Present/read-only context: `docs/roadmap/decisions/PHASE8-IMPL-020-model-assisted-extraction-diagnostic-workflow-boundary-decision.md`

## 6. T001 Publication Inventory Result

- Created: `docs/roadmap/tasks/PHASE8-IMPL-021.md`
- Created: `docs/roadmap/inventory/PHASE8-IMPL-021.md`
- Created: `docs/roadmap/enrichment/PHASE8-IMPL-021.enrichment.json`
- Updated roadmap/status/governance docs only.

No backend implementation code, frontend implementation code, product tests, routes, UI, package/dependency files, NCP/Subtxt/dramatica-flow runtime, cloned repositories, dependency installs, model/Ollama calls, BookNLP/spaCy extraction over project text, apply-promotion changes, approved memory/canon mutation, candidate/review queue creation, generated prose, or training/JSONL/dataset/model artifacts were created or changed by T001.

## 7. T003 Ready/Active Handoff

T003 is complete/PASS as tests-first expected-red contract tests only. It defines the future helper contract before implementation. The contract requires allowlist fields `tool_name`, `module_or_feature_name`, `allowed_action`, `forbidden_actions`, `output_classes_allowed`, `output_classes_forbidden`, `required_refs`, `source_locator_policy`, `evidence_policy`, `provenance_policy`, `owner_review_policy`, `fail_closed_policy`, `no_silent_fallback_policy`, `no_prose_policy`, `no_training_policy`, `no_canon_policy`, `no_apply_promotion_policy`, `validation_tests_required`, and `audit_notes`; request refs `source_refs`, `evidence_refs`, `provenance_refs`, and `source_locator_refs`; allowed outputs `evidence_backed_candidate_observation`, `diagnostic_question`, `uncertainty_note`, `insufficient_evidence_note`, `rubric_mapping_support`, `context_interchange_support`, `quarantined_result`, `unavailable_result`, `fail_closed_result`, `refused_no_prose`, and `blocked_request`; forbidden outputs `generated_prose`, `rewritten_prose`, `continuation`, `outline`, `chapter_generation`, `draft`, `revision`, `polish`, `improvement`, `expansion`, `style_imitation`, `export_as_prose`, `story_prose`, `training_jsonl`, `dataset_manifest`, `model_artifact`, `promotion_record`, `approved_memory`, `canon`, `storyform_truth`, `scene_mutation`, `note_mutation`, and `material_mutation`; and states including `allowlist_missing`, `allowlist_denied`, `unsupported_tool`, `unsupported_action`, and `forbidden_output_type`.

NCP remains structured context interchange only. Subtxt remains rubric/diagnostic guidance only. dramatica-flow remains audited allowlist only. Runtime outputs remain candidate-first and owner review is mandatory. Confidence is not truth. Tool output is not canon. Tool output is not truth. No model output as truth. No automatic canon. No apply-promotion. No memory/canon mutation. No training artifacts. No generated prose. No rewrite. No continuation. No outline. Fail closed. No silent fallback. Queue presence is not approval. Candidate persistence is not canon.

`PHASE8-IMPL-021-T004` is complete/PASS. `PHASE8-IMPL-021-T005` is ready/active next. `PHASE8-IMPL-021-T006` and `PHASE8-IMPL-021-T007` remain planned. `PHASE8-IMPL-022` remains future MVP-required. Fine-tuning remains deferred after MVP. Generated prose/prose-production paths remain permanently forbidden.

## 8. T004 Implementation Inventory Result

T004 is complete/PASS. Final artifact: `backend/story_knowledge/analysis_runtime_integration.py`.

The helper is pure, deterministic, in-memory, and local-first. It implements allowlist validation, request validation, deterministic non-executing plan building, output validation, candidate support shaping, diagnostic question shaping, quarantine output shaping, and guarded runtime state reporting through `validate_analysis_runtime_allowlist_record`, `validate_analysis_runtime_request`, `build_analysis_runtime_plan`, `validate_analysis_runtime_output`, `build_analysis_runtime_candidate_support`, `build_analysis_runtime_diagnostic_questions`, `quarantine_analysis_runtime_output`, and `run_guarded_analysis_runtime_integration`.

Runtime outputs remain candidate-first and owner review is required. Confidence is not truth. Tool output is not canon. Tool output is not truth. No automatic canon. No apply-promotion. No memory/canon mutation. No training artifacts. No generated prose. No rewrite. No continuation. No outline. Fail closed. No silent fallback.

T004 added no NCP/Subtxt/dramatica-flow execution, no routes, no UI, no frontend changes, no package/dependency changes, no model/Ollama calls, no candidate persistence, no review queue entries, no approved memory/canon mutation, no apply-promotion, no training artifacts, and no generated prose behavior.

`PHASE8-IMPL-021-T005` is ready/active next. `PHASE8-IMPL-021-T006` and `PHASE8-IMPL-021-T007` remain planned. `PHASE8-IMPL-022` remains future MVP-required. Fine-tuning remains deferred after MVP. Generated prose/prose-production paths remain permanently forbidden.
