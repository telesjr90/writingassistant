# PHASE8-IMPL-019 Inventory

## 1. Task Identity

- Parent ID: `PHASE8-IMPL-019`
- Title: Guarded runtime extraction: real BookNLP/spaCy install/run/import and candidate-first extraction pipeline
- Track: Writer Assistant Core
- Phase: Phase 8
- Status: active MVP-required parent; `PHASE8-IMPL-019-T001` complete/PASS; `PHASE8-IMPL-019-T002` ready/active next; `PHASE8-IMPL-019-T003` through `PHASE8-IMPL-019-T007` planned
- Depends on: completed/committed `PHASE8-IMPL-018` through `PHASE8-IMPL-018-T007`
- Current child: `PHASE8-IMPL-019-T001` complete/PASS
- Next child: `PHASE8-IMPL-019-T002` ready/active next
- Future MVP-required parents: `PHASE8-IMPL-020`, `PHASE8-IMPL-021`, `PHASE8-IMPL-022`

## 2. Why This Parent Exists

Deliver real BookNLP/spaCy install/run/import checks and guarded runtime extraction from owner-authored or owner-provided project text into raw artifact bundles and candidate-first review handoff, without canon mutation, model calls, automatic apply-promotion, training artifacts, or generated prose.

`PHASE8-IMPL-018` delivered project-local raw artifact persistence helpers only. `PHASE8-IMPL-019` now publishes the guarded runtime extraction parent that will later decide and implement availability, environment guards, install/run/import verification, request validation, source/evidence/provenance rules, raw artifact handoff, and candidate-first owner-review handoff. T001 itself is docs/status only.

## 3. Boundary Summary

Runtime extraction in PHASE8-IMPL-019 may be introduced only through explicitly scoped children after T001 and may run only over owner-authored or owner-provided project text/materials. Output is candidate-first and owner-review-gated; runtime extraction output is never canon by itself, raw tool output is never authoritative by itself, extractor confidence is not truth, and extractor output cannot mutate approved memory/canon, apply promotion, create training data, or generate prose. Raw artifacts must be persisted through PHASE8-IMPL-018 helpers. Candidate persistence/review queue handoff may use existing candidate/review infrastructure only when explicitly scoped. Apply-promotion remains the separate PHASE8-IMPL-017 owner-confirmed path. Missing tools, missing models, unsafe paths, missing source/evidence/provenance, invalid source locators, malformed tool outputs, or unavailable environment must fail-closed or return explicit unavailable/quarantined state. No silent fallback may claim extraction succeeded.

Required future request and handoff vocabulary includes `source_refs`, `evidence_refs`, `provenance_refs`, `source_locator_refs`, availability, unavailable, quarantine, fail-closed, no silent fallback, raw artifact persistence, candidate-first, owner review, no automatic canon, no apply-promotion, no memory/canon mutation, no model calls, no generated prose, and no training artifacts.

PHASE8-UX-001 was used only as a read-only terminology/boundary reference for labels such as review, candidate, evidence, provenance, source locator, raw artifact, approved memory/canon, owner action, unavailable/quarantined state, and no automatic canon. PHASE8-UX-001 is not roadmap truth, does not override master_plan, implementation_status, roadmap_index, or PHASE8-IMPL parent boundaries, and was not edited.

## 4. Child Sequence

- `PHASE8-IMPL-019-T001` - Publish/activate guarded runtime extraction parent. complete/PASS. Output/scope: task record, inventory, enrichment JSON, roadmap/status/governance alignment; docs/status only; no install/import/run, no runtime extraction, no code/tests/package changes.
- `PHASE8-IMPL-019-T002` - Guarded runtime extraction boundary decision and environment model. ready/active next. Output/scope: decision document defining BookNLP/spaCy dependency policy, environment guard model, install/import/run verification rules, extractor request shape, source/evidence/provenance requirements, raw artifact persistence handoff, candidate-first handoff, unavailable/quarantine semantics, and no-prose/no-canon/no-training boundaries; docs/decision only.
- `PHASE8-IMPL-019-T003` - Expected-red guarded runtime extraction contract tests. planned. Output/scope: expected-red tests for future availability checks, import/run guards, request validation, raw artifact handoff, candidate-first handoff, fail-closed unavailable/quarantine behavior, and no-canon/no-prose/no-training/no-apply-promotion boundaries; no implementation.
- `PHASE8-IMPL-019-T004` - Minimal guarded dependency availability and import/run probe implementation. planned. Output/scope: minimal backend helper for BookNLP/spaCy availability/import/run probes with environment guards and explicit unavailable states; no package/dependency changes unless separately authorized.
- `PHASE8-IMPL-019-T005` - Guarded runtime extraction request and raw artifact handoff implementation. planned. Output/scope: bounded backend runtime extraction helper that validates owner-provided source requests, invokes allowed extractor adapters only under environment guards, stores raw outputs through PHASE8-IMPL-018 raw artifact helpers, and returns candidate-first handoff data without canon mutation.
- `PHASE8-IMPL-019-T006` - Runtime extraction safety regression. planned. Output/scope: focused regression tests proving no automatic canon, no apply-promotion, no candidate/review queue side effects unless explicitly scoped, no model calls, no generated prose, no training artifacts, path safety, unavailable/quarantine behavior, and no silent fallback.
- `PHASE8-IMPL-019-T007` - Parent closeout. planned. Output/scope: parent closeout docs/status/governance, PHASE8-IMPL-020 ready/active next; docs/status only.

## 5. Existing Raw Artifact Helper From PHASE8-IMPL-018

- Present/read-only context: `backend/story_knowledge/raw_artifacts.py`
- Present/read-only context: `tests/test_writer_assistant_core_raw_artifacts_contract.py`
- Present/read-only context: `tests/test_writer_assistant_core_raw_artifact_lifecycle_contract.py`
- Present/read-only context: `tests/test_writer_assistant_core_raw_artifact_safety_regression.py`

## 6. Existing Extraction Orchestration Planning/Helper Context

- Present/read-only context: `backend/story_knowledge/extraction_orchestrator.py`
- Present/read-only context: `tests/test_writer_assistant_core_extraction_orchestrator_contract.py`

## 7. Existing BookNLP Fixture Parser Context

- Present/read-only context: `backend/story_knowledge/booknlp_fixture_parser.py`
- Relevant BookNLP fixture parser tests: present in prior parser/orchestrator/raw artifact contract coverage where applicable; specific additional parser test filenames are deferred to T002/T003 inspection.

## 8. Existing Candidate/Review/Apply-Promotion Infrastructure

- Present/read-only context: `backend/story_knowledge/candidate_record.py`
- Present/read-only context: `backend/story_knowledge/candidate_storage.py`
- Present/read-only context: `backend/story_knowledge/review_queue_storage.py`
- Present/read-only context: `backend/review_api.py`
- Present/read-only context: `backend/routes/review_queue.py`
- Absent/deferred; not created in T001: `backend/routes/review_actions.py`
- Present/read-only context: `backend/story_knowledge/apply_promotion.py`
- Present/read-only context: `backend/routes/apply_promotion.py`
- Present/read-only context: `frontend/src/components/ApplyPromotionConfirmation.jsx`
- Tests for candidate/review/apply-promotion safety: present in prior parent contract/regression suites and deferred to T002/T003 focused enumeration.

## 9. Existing Guardrails

- Present/read-only context: `backend/guardrails.py`
- Present/read-only context: `tests/test_guardrails.py`

## 10. Runtime Dependency Manifests To Inspect Later But Not Edit In T001

- Present/read-only context: `backend/requirements.txt`
- Present/read-only context: `training/requirements-unsloth.txt`
- Present/read-only context: `frontend/package.json`
- Absent/deferred; not created in T001: `package.json`
- Package/dependency files are read-only context for T001 and were not edited.

## 11. T001 Publication Inventory Result

- Present/read-only context: `backend/story_knowledge/raw_artifacts.py`
- Present/read-only context: `tests/test_writer_assistant_core_raw_artifacts_contract.py`
- Present/read-only context: `tests/test_writer_assistant_core_raw_artifact_lifecycle_contract.py`
- Present/read-only context: `tests/test_writer_assistant_core_raw_artifact_safety_regression.py`
- Present/read-only context: `backend/story_knowledge/extraction_orchestrator.py`
- Present/read-only context: `tests/test_writer_assistant_core_extraction_orchestrator_contract.py`
- Present/read-only context: `backend/story_knowledge/booknlp_fixture_parser.py`
- Present/read-only context: `backend/story_knowledge/candidate_record.py`
- Present/read-only context: `backend/story_knowledge/candidate_storage.py`
- Present/read-only context: `backend/story_knowledge/review_queue_storage.py`
- Present/read-only context: `backend/review_api.py`
- Present/read-only context: `backend/routes/review_queue.py`
- Present/read-only context: `backend/story_knowledge/apply_promotion.py`
- Present/read-only context: `backend/routes/apply_promotion.py`
- Present/read-only context: `frontend/src/components/ApplyPromotionConfirmation.jsx`
- Present/read-only context: `backend/guardrails.py`
- Present/read-only context: `tests/test_guardrails.py`
- Present/read-only context: `backend/requirements.txt`
- Present/read-only context: `training/requirements-unsloth.txt`
- Present/read-only context: `frontend/package.json`
- Absent/deferred; not created in T001: `backend/routes/review_actions.py`
- Absent/deferred; not created in T001: `package.json`

No backend implementation code, frontend implementation code, product tests, routes, UI, package/dependency files, runtime extraction, BookNLP/spaCy install/run/import, model/Ollama calls, NCP/Subtxt/dramatica-flow runtime, apply-promotion changes, approved memory/canon mutation, candidate/review queue creation, generated prose, or training/JSONL/dataset/model artifacts were created or changed by T001.
