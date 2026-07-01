# PHASE8-IMPL-020 Inventory

## 1. Task Identity

- Parent ID: `PHASE8-IMPL-020`
- Title: Model-assisted evidence-backed extraction and diagnostic workflow
- Track: Writer Assistant Core
- Phase: Phase 8
- Status: active MVP-required parent; `PHASE8-IMPL-020-T001` complete/PASS; `PHASE8-IMPL-020-T002` complete/PASS as docs/decision only; `PHASE8-IMPL-020-T003` complete/PASS as expected-red tests-only handoff; `PHASE8-IMPL-020-T004` complete/PASS as minimal model-assisted request/output guard implementation; `PHASE8-IMPL-020-T005` complete/PASS as evidence-backed diagnostic/candidate handoff implementation; `PHASE8-IMPL-020-T006` complete/PASS as model-assisted extraction safety regression
- Depends on: completed/PASS `PHASE8-IMPL-019` through `PHASE8-IMPL-019-T007`
- Completed child: `PHASE8-IMPL-020-T006` - Model-assisted extraction safety regression
- Current child: `PHASE8-IMPL-020-T007` - Parent closeout
- Next child status: ready/active
- Planned child: none under this parent after T007 closeout
- Future MVP-required parents: `PHASE8-IMPL-021`, `PHASE8-IMPL-022`

## 2. Why This Parent Exists

PHASE8-IMPL-019 delivered the guarded runtime extraction helper boundary and raw artifact handoff without model calls. PHASE8-IMPL-020 now publishes the model-assisted evidence-backed extraction and diagnostic workflow parent so future children can define and implement model assistance only inside strict analysis boundaries.

Model assistance may support evidence-backed candidate observations, diagnostic questions, uncertainty notes, and candidate extraction support. It must never become canon by itself, apply promotion, mutate approved memory/canon, create training data, or generate prose.

## 3. Boundary Summary

Model-assisted extraction and diagnostic workflow output must be candidate-first, owner-review-required, evidence-backed, provenance-backed, and source-locator-backed when available. Required future request/output vocabulary includes `source_refs`, `evidence_refs`, `provenance_refs`, `source_locator_refs`, diagnostic questions, candidate observations, uncertainty notes, confidence is not truth, no automatic canon, no apply-promotion, no memory/canon mutation, no training artifacts, no generated prose, no rewrite, no continuation, no outline, no model output as truth, fail closed, no silent fallback, and local-first execution.

Model output may never be treated as truth by confidence score, fluent wording, extracted pattern, diagnostic framing, queue presence, raw artifact presence, or candidate persistence. Owner review remains mandatory. Apply-promotion remains the separate explicit owner-confirmed path from PHASE8-IMPL-017.

T001 publication creates docs/status/governance records only. No backend implementation code, frontend code, tests, package/dependency files, model-assisted extraction, model/Ollama calls, routes, UI, candidate persistence, review queue entries, apply-promotion changes, approved memory/canon mutation, generated prose, or training/JSONL/dataset/model artifacts are created or changed by T001.

PHASE8-UX-001 is read-only terminology/boundary reference only. It is not roadmap truth and was not edited.

## 4. Child Sequence

- `PHASE8-IMPL-020-T001` - Publish/activate model-assisted evidence-backed extraction parent. complete/PASS. Output/scope: task record, inventory, enrichment JSON, roadmap/status/governance alignment; docs/status only.
- `PHASE8-IMPL-020-T002` - Model-assisted extraction and diagnostic workflow boundary decision. complete/PASS. Output/scope: docs/decision only; accepted request/output guard model, evidence/provenance/source-locator requirements, diagnostic-question fallback, refusal/no-prose checks, model-output-as-candidate-only boundary, state vocabulary, fail-closed behavior, and no silent fallback.
- `PHASE8-IMPL-020-T003` - Expected-red model-assisted extraction contract tests. complete/PASS. Output/scope: tests-only contract at `tests/test_writer_assistant_core_model_assisted_extraction_contract.py`; expected-red import boundary for future `backend.story_knowledge.model_assisted_extraction`; no implementation module created.
- `PHASE8-IMPL-020-T004` - Minimal model-assisted request/output guard implementation. complete/PASS. Output/scope: pure guarded helper at `backend/story_knowledge/model_assisted_extraction.py`; no model calls, no routes/UI, no persistence, no apply-promotion, no memory/canon mutation, no training artifacts, and no generated prose.
- `PHASE8-IMPL-020-T005` - Evidence-backed diagnostic/candidate handoff implementation. complete/PASS.
- `PHASE8-IMPL-020-T006` - Model-assisted extraction safety regression. complete/PASS.
- `PHASE8-IMPL-020-T007` - Parent closeout. ready/active next.

## 5. Existing Runtime Extraction Context

- Present/read-only context: `backend/story_knowledge/runtime_extraction.py`
- Present/read-only context: `tests/test_writer_assistant_core_runtime_extraction_contract.py`
- Present/read-only context: `tests/test_writer_assistant_core_runtime_extraction_raw_artifact_handoff_contract.py`
- Present/read-only context: `tests/test_writer_assistant_core_runtime_extraction_safety_regression.py`
- Present/read-only context: `docs/roadmap/decisions/PHASE8-IMPL-019-guarded-runtime-extraction-boundary-environment-model-decision.md`

## 6. Existing Candidate/Review/Apply-Promotion Context

- Present/read-only context: `backend/story_knowledge/candidate_record.py`
- Present/read-only context: `backend/story_knowledge/candidate_storage.py`
- Present/read-only context: `backend/story_knowledge/review_queue_storage.py`
- Present/read-only context: `backend/review_api.py`
- Present/read-only context: `backend/routes/review_queue.py`
- Present/read-only context: `backend/story_knowledge/apply_promotion.py`
- Present/read-only context: `backend/routes/apply_promotion.py`
- Present/read-only context: `frontend/src/components/ApplyPromotionConfirmation.jsx`

## 7. Existing Guardrails

- Present/read-only context: `backend/guardrails.py`
- Present/read-only context: `tests/test_guardrails.py`

## 8. Runtime Dependency And Model Context To Inspect Later But Not Edit In T001

- Present/read-only context: `backend/analysis_engine.py`
- Present/read-only context: `backend/analysis_modes.py`
- Present/read-only context: `backend/requirements.txt`
- Present/read-only context: `frontend/package.json`
- Present/read-only context: `training/requirements-unsloth.txt`

Package/dependency files are read-only context for T001 and were not edited.

## 9. T001 Publication Inventory Result

- Created: `docs/roadmap/tasks/PHASE8-IMPL-020.md`
- Created: `docs/roadmap/inventory/PHASE8-IMPL-020.md`
- Created: `docs/roadmap/enrichment/PHASE8-IMPL-020.enrichment.json`
- Updated roadmap/status/governance docs only.

No backend implementation code, frontend implementation code, product tests, routes, UI, package/dependency files, model-assisted extraction, model/Ollama calls, NCP/Subtxt/dramatica-flow runtime, apply-promotion changes, approved memory/canon mutation, candidate/review queue creation, generated prose, or training/JSONL/dataset/model artifacts were created or changed by T001.

## 10. T003 Expected-red Contract Result

- Created: `tests/test_writer_assistant_core_model_assisted_extraction_contract.py`
- Result: complete/PASS as tests-first expected-red handoff.
- Future module covered: `backend.story_knowledge.model_assisted_extraction`
- Future public APIs covered: `validate_model_assisted_extraction_request`, `validate_model_assisted_environment`, `build_model_assisted_extraction_prompt_packet`, `validate_model_assisted_output`, `build_model_assisted_candidate_support`, `build_model_assisted_diagnostic_questions`, `quarantine_model_assisted_output`, and `run_guarded_model_assisted_extraction`.
- Boundary: no implementation module, backend implementation code, frontend code, package/dependency changes, routes, UI, model calls, candidate records, review queue entries, apply-promotion, memory/canon mutation, training artifacts, or generated prose were created.

## 11. T004 Minimal Guard Implementation Result

- Created: `backend/story_knowledge/model_assisted_extraction.py`
- Result: complete/PASS as minimal model-assisted request/output guard implementation.
- Public APIs implemented: `validate_model_assisted_extraction_request`, `validate_model_assisted_environment`, `build_model_assisted_extraction_prompt_packet`, `validate_model_assisted_output`, `build_model_assisted_candidate_support`, `build_model_assisted_diagnostic_questions`, `quarantine_model_assisted_output`, and `run_guarded_model_assisted_extraction`.
- Boundary: pure, deterministic, local-first, side-effect-free in-memory helper only; no model calls, no Ollama calls, no analysis engine imports, no backend routes, no UI/frontend changes, no package/dependency changes, no candidate persistence, no review queue entries, no apply-promotion, no memory/canon mutation, no training artifacts, and no generated prose/rewrite/continuation/outline/prose-production behavior were created.

## 12. T005 Evidence-backed Handoff Implementation Result

- Updated: `backend/story_knowledge/model_assisted_extraction.py`
- Created: `tests/test_writer_assistant_core_model_assisted_extraction_handoff_contract.py`
- Result: complete/PASS as evidence-backed diagnostic/candidate handoff implementation.
- Public APIs implemented: `build_model_assisted_review_handoff`, `validate_model_assisted_review_handoff`, `build_model_assisted_diagnostic_handoff`, and `build_model_assisted_candidate_observation_handoff`.
- Boundary: pure in-memory handoff objects only; evidence/provenance/source-locator refs preserved; diagnostic questions and candidate observations remain candidate-first and owner-review-required; queue presence is not approval; candidate persistence is not canon; apply-promotion remains separate explicit owner-confirmed path; no model calls, no candidate records, no review queue entries, no apply-promotion, no memory/canon mutation, no training artifacts, and no generated prose.

## 13. T006 Safety Regression Result

- Updated: `backend/story_knowledge/model_assisted_extraction.py`
- Created: `tests/test_writer_assistant_core_model_assisted_extraction_safety_regression.py`
- Result: complete/PASS as focused model-assisted extraction safety regression.
- Coverage: no model/Ollama/network/process/analysis_engine execution, unsafe path/source/id/source-locator rejection, missing ref fail-closed behavior, forbidden output/prose rejection, prompt packet guard safety, in-memory handoff safety, explicit state vocabulary, and no false success.
- Boundary: pure, deterministic, local-first, side-effect-free in-memory helper only; no routes/UI/frontend/package changes, no candidate persistence, no review queue entries, no apply-promotion, no memory/canon mutation, no training artifacts, and no generated prose/rewrite/continuation/outline/prose-production behavior.
