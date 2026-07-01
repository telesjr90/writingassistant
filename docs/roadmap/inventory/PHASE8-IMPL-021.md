# PHASE8-IMPL-021 Inventory

## 1. Task Identity

- Parent ID: `PHASE8-IMPL-021`
- Title: Analysis-only NCP/Subtxt/dramatica-flow runtime integration
- Track: Writer Assistant Core
- Phase: Phase 8
- Status: active MVP-required parent; `PHASE8-IMPL-021-T001` complete/PASS; `PHASE8-IMPL-021-T002` complete/PASS; `PHASE8-IMPL-021-T003` ready/active next
- Depends on: completed/PASS `PHASE8-IMPL-020` through `PHASE8-IMPL-020-T007`
- Completed children: `PHASE8-IMPL-021-T001` - Publish/activate analysis-only NCP/Subtxt/dramatica-flow runtime integration parent; `PHASE8-IMPL-021-T002` - Analysis-only runtime integration boundary and allowlist decision
- Current child: `PHASE8-IMPL-021-T003` - Expected-red NCP/Subtxt/dramatica-flow runtime integration contract tests
- Next child status: ready/active
- Planned children: `PHASE8-IMPL-021-T004`, `PHASE8-IMPL-021-T005`, `PHASE8-IMPL-021-T006`, and `PHASE8-IMPL-021-T007`
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

PHASE8-UX-001 is read-only terminology/boundary reference only. It is not roadmap truth and was not edited.

## 4. Child Sequence

- `PHASE8-IMPL-021-T001` - Publish/activate analysis-only NCP/Subtxt/dramatica-flow runtime integration parent. complete/PASS. Output/scope: task record, inventory, enrichment JSON, roadmap/status/governance alignment; docs/status only.
- `PHASE8-IMPL-021-T002` - Analysis-only runtime integration boundary and allowlist decision. complete/PASS. Output/scope: docs/decision only; defines the audited allowlist, blocked prose/outline/write/revise/export paths, NCP/Subtxt/dramatica-flow role boundaries, evidence/provenance/source-locator requirements, request/output/state vocabulary, fail-closed state vocabulary, and no silent fallback.
- `PHASE8-IMPL-021-T003` - Expected-red NCP/Subtxt/dramatica-flow runtime integration contract tests. ready/active next.
- `PHASE8-IMPL-021-T004` - Minimal analysis-only runtime request/allowlist guard implementation. planned.
- `PHASE8-IMPL-021-T005` - Evidence-backed runtime output handoff implementation. planned.
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

## 7. T002 Ready/Active Handoff

T002 is complete/PASS as docs/decision only. It defines the analysis-only runtime integration boundary and audited allowlist before any tests or implementation. It explicitly blocks prose paths, outline paths, rewrite, continuation, draft, revision, polish, expansion, style imitation, chapter generation, write/revise, export-as-prose, automatic canon, apply-promotion, memory/canon mutation, training artifacts, and silent fallback. `PHASE8-IMPL-021-T003` is ready/active next.
