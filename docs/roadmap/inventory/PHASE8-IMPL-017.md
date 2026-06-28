# PHASE8-IMPL-017 Inventory

## 1. Task Identity

- Parent ID: `PHASE8-IMPL-017`
- Title: Apply-promotion contract, audit log, and approved memory/canon mutation boundary
- Track: Writer Assistant Core
- Phase: Phase 8
- Status: complete/PASS MVP-required parent; `PHASE8-IMPL-017-T001` complete/PASS; `PHASE8-IMPL-017-T002` complete/PASS; `PHASE8-IMPL-017-T003` complete/PASS expected-red contract handoff; `PHASE8-IMPL-017-T004` complete/PASS minimal backend apply-promotion service/route implementation; `PHASE8-IMPL-017-T005` complete/PASS frontend apply-promotion confirmation workflow/surface; `PHASE8-IMPL-017-T006` complete/PASS approved memory/canon mutation safety regression; `PHASE8-IMPL-017-T007` complete/PASS parent closeout
- Depends on: completed `PHASE8-IMPL-016`
- Current child: none; parent complete/PASS
- Child sequence: T001 complete/PASS; T002 complete/PASS; T003 complete/PASS expected-red; T004 complete/PASS backend implementation; T005 complete/PASS frontend confirmation workflow; T006 complete/PASS safety regression; T007 complete/PASS parent closeout

## 2. Why This Parent Exists

`PHASE8-IMPL-016` delivered owner-action review commands and a frontend owner-action review workflow, but explicitly did not deliver apply-promotion or approved memory/canon mutation. `PHASE8-IMPL-017` is the MVP-required parent that owns the future apply-promotion workflow and the approved memory/canon mutation boundary.

The parent exists to move from candidate review workflow support to an explicit candidate-to-approved transition without making queue state, confidence, extraction output, model output, candidate persistence, or raw artifacts into truth. Apply-promotion must be an explicit owner-confirmed action with audit records, destination checks, evidence/provenance/source locator preservation, and fail-closed behavior.

## 3. Boundary Summary

Allowed in this parent sequence:

- apply-promotion boundary decision and audit model
- tests-first expected-red apply-promotion contract
- minimal backend apply-promotion service/route implementation in T004
- frontend apply-promotion confirmation workflow/surface in T005
- approved memory/canon mutation safety regression
- parent closeout after validation

Forbidden in `PHASE8-IMPL-017-T001`:

- apply-promotion runtime implementation
- approved memory/canon mutation runtime implementation
- project truth mutation
- raw artifact persistence
- runtime extraction
- BookNLP/spaCy install/run/import
- model/Ollama calls
- NCP/Subtxt/dramatica-flow runtime
- generated prose or prose-production behavior
- training/JSONL/dataset/model artifacts

Forbidden in `PHASE8-IMPL-017-T002`:

- backend implementation code changes
- frontend implementation code changes
- product test changes
- apply-promotion runtime implementation
- approved memory/canon mutation runtime implementation
- project truth mutation
- raw artifact persistence
- runtime extraction
- BookNLP/spaCy install/run/import
- model/Ollama calls
- NCP/Subtxt/dramatica-flow runtime
- generated prose or prose-production behavior
- training/JSONL/dataset/model artifacts

`PHASE8-IMPL-017-T002` changed docs/status only and created the decision document `docs/roadmap/decisions/PHASE8-IMPL-017-apply-promotion-boundary-audit-model-decision.md`. No backend/frontend/tests/runtime files changed.

Forbidden in `PHASE8-IMPL-017-T003`:

- backend implementation code changes
- frontend implementation code changes
- package/dependency changes
- apply-promotion runtime implementation
- approved memory/canon mutation runtime implementation
- project truth mutation
- raw artifact persistence
- runtime extraction
- BookNLP/spaCy install/run/import
- model/Ollama calls
- NCP/Subtxt/dramatica-flow runtime
- generated prose or prose-production behavior
- training/JSONL/dataset/model artifacts

`PHASE8-IMPL-017-T003` added only `tests/test_writer_assistant_core_apply_promotion_contract.py` as an expected-red contract for future `backend.story_knowledge.apply_promotion` APIs. The target is expected to fail only because the future module/API is absent before T004.

Allowed and completed in `PHASE8-IMPL-017-T004`:

- `backend/story_knowledge/apply_promotion.py` implements the minimal backend apply-promotion APIs.
- `backend/routes/apply_promotion.py` exposes `POST /api/projects/{project_id}/apply-promotion`.
- `backend/main.py` includes the new route.
- Apply-promotion remains explicit owner-confirmed, audited, evidence/provenance/source-locator-backed, project-local, and fail-closed.
- Approved memory/canon mutation is bounded to `writer_assistant/approved_memory/` after valid owner-confirmed apply-promotion only.
- Promotion audit records are bounded to `writer_assistant/promotion_audit/`.
- No frontend implementation code, raw artifact persistence, runtime extraction, model calls, generated prose, or training artifacts were added.

Allowed and completed in `PHASE8-IMPL-017-T005`:

- `frontend/src/api.js` exposes `submitApplyPromotion(projectId, payload)` for `POST /api/projects/{project_id}/apply-promotion`.
- `frontend/src/components/ApplyPromotionConfirmation.jsx` provides a separate final owner confirmation surface from review workflow commands.
- Apply-promotion remains explicit owner-confirmed, audited by the backend, evidence/provenance/source-locator-backed, project-local, and fail-closed.
- The frontend destination allowlist is limited to approved memory/canon destination categories.
- No backend implementation code, raw artifact persistence, runtime extraction, model calls, generated prose, or training artifacts were added.

Allowed and completed in `PHASE8-IMPL-017-T006`:

- `tests/test_apply_promotion_memory_canon_safety_regression.py` proves validation and plan-building do not mutate approved memory/canon.
- Missing or false `owner_confirmation` fails closed without approved memory/canon writes or applied audit records.
- Failed validation for unsafe destinations, missing evidence/provenance/source locators, unsupported candidate type, and forbidden fields does not partially mutate approved memory/canon.
- Valid apply-promotion writes one structured approved-memory JSON file and one applied promotion audit JSON record with evidence/provenance/source locator refs and no generated-prose/model/training confirmations.
- Duplicate apply behavior is deterministic and does not create duplicate conflicting applied audit records.
- Review queue action commands remain separate from apply-promotion and do not create approved memory/canon files.
- Frontend source safety preserves final owner confirmation, candidate-only/no-canon warning copy, and review/apply separation.
- Backend source safety rejects unsupported destinations/actions without adding runtime extraction, model calls, generated prose, raw artifact persistence, or training artifacts.
- Minimal backend hardening changed only forbidden runtime marker construction in `backend/story_knowledge/apply_promotion.py` without adding destination categories or product behavior.

Allowed and completed in `PHASE8-IMPL-017-T007`:

- Docs/status/governance closeout only.
- Parent marked complete/PASS.
- `PHASE8-IMPL-017-T007` marked complete/PASS.
- `PHASE8-IMPL-018` recommended as active/ready next parent.
- No backend implementation code, frontend implementation code, product tests, package/dependency files, raw artifact persistence, runtime extraction, BookNLP/spaCy install/run/import, model/Ollama calls, NCP/Subtxt/dramatica-flow runtime, generated prose, or training/JSONL/dataset/model artifacts were added.

Required boundary tags for this parent:

- `mvp_required_apply_promotion`
- `approved_memory_canon_mutation`
- `owner_confirmed_only`
- `audited_promotion`
- `candidate_to_approved_boundary`
- `no_auto_promotion`
- `no_confidence_as_truth`
- `no_queue_presence_as_approval`
- `no_extraction_as_canon`
- `no_generated_prose`
- `generated_prose_permanently_forbidden`
- `no_model_calls`
- `no_runtime_extraction`
- `no_raw_artifact_persistence`
- `no_training_artifacts`

## 4. MVP Relation

`PHASE8-IMPL-017` is MVP-required and complete/PASS. It delivered the explicit owner-confirmed apply-promotion path and approved memory/canon mutation boundary required before the MVP can claim approved memory/canon mutation through owner-approved workflow. `PHASE8-IMPL-018` is the next active/ready MVP-required parent. `PHASE8-IMPL-019` through `PHASE8-IMPL-022` remain future MVP-required parents.

## 5. Cross-References

- Prior parent: `PHASE8-IMPL-016` - frontend owner-action execution workflow and review command boundary
- Decision document: `docs/roadmap/decisions/PHASE8-IMPL-017-apply-promotion-boundary-audit-model-decision.md`
- Final delivered backend module: `backend/story_knowledge/apply_promotion.py`
- Final delivered backend route: `backend/routes/apply_promotion.py`
- Final delivered route path: `POST /api/projects/{project_id}/apply-promotion`
- Final delivered frontend API helper: `submitApplyPromotion(projectId, payload)` in `frontend/src/api.js`
- Final delivered frontend confirmation component: `frontend/src/components/ApplyPromotionConfirmation.jsx`
- Final delivered safety regression: `tests/test_apply_promotion_memory_canon_safety_regression.py`
- Final delivered contract tests: `tests/test_writer_assistant_core_apply_promotion_contract.py`
- Final delivered frontend source tests: `tests/test_frontend_apply_promotion_workflow_source.py`
- Next MVP-required parents: `PHASE8-IMPL-018`, `PHASE8-IMPL-019`, `PHASE8-IMPL-020`, `PHASE8-IMPL-021`, `PHASE8-IMPL-022`

## 6. Future Parent Deferrals

- `PHASE8-IMPL-018` owns raw artifact persistence.
- `PHASE8-IMPL-019` owns runtime extraction plus real BookNLP/spaCy install/run/import.
- `PHASE8-IMPL-020` owns model-assisted evidence-backed extraction.
- `PHASE8-IMPL-021` owns NCP/Subtxt/dramatica-flow analysis-only runtime integration.
- `PHASE8-IMPL-022` owns end-to-end MVP usability validation.

Generated context artifacts remain evidence only and must not be treated as roadmap truth or task completion:

- `.codex-context/PHASE8-IMPL-016/` (ignored)
- `.codex-context/PHASE8-IMPL-017/` (ignored/evidence only if present)
- `ai_context/repomix-current-task-context.xml` (ignored; evidence only)
