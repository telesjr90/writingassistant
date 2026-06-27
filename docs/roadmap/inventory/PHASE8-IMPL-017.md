# PHASE8-IMPL-017 Inventory

## 1. Task Identity

- Parent ID: `PHASE8-IMPL-017`
- Title: Apply-promotion contract, audit log, and approved memory/canon mutation boundary
- Track: Writer Assistant Core
- Phase: Phase 8
- Status: active MVP-required parent; `PHASE8-IMPL-017-T001` complete/PASS; `PHASE8-IMPL-017-T002` complete/PASS; `PHASE8-IMPL-017-T003` complete/PASS expected-red contract handoff; `PHASE8-IMPL-017-T004` complete/PASS minimal backend apply-promotion service/route implementation
- Depends on: completed `PHASE8-IMPL-016`
- Current child: `PHASE8-IMPL-017-T005` - ready/active next
- Child sequence: T001 complete/PASS; T002 complete/PASS; T003 complete/PASS expected-red; T004 complete/PASS backend implementation; T005 ready/active; T006 planned; T007 planned

## 2. Why This Parent Exists

`PHASE8-IMPL-016` delivered owner-action review commands and a frontend owner-action review workflow, but explicitly did not deliver apply-promotion or approved memory/canon mutation. `PHASE8-IMPL-017` is the MVP-required parent that owns the future apply-promotion workflow and the approved memory/canon mutation boundary.

The parent exists to move from candidate review workflow support to an explicit candidate-to-approved transition without making queue state, confidence, extraction output, model output, candidate persistence, or raw artifacts into truth. Apply-promotion must be an explicit owner-confirmed action with audit records, destination checks, evidence/provenance/source locator preservation, and fail-closed behavior.

## 3. Boundary Summary

Allowed in this parent sequence:

- apply-promotion boundary decision and audit model
- tests-first expected-red apply-promotion contract
- minimal backend apply-promotion service/route implementation in T004
- frontend apply-promotion confirmation workflow/surface in a later child
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

`PHASE8-IMPL-017` is MVP-required and active. It is required before the MVP can claim approved memory/canon mutation through owner-approved workflow. `PHASE8-IMPL-018` through `PHASE8-IMPL-022` remain future MVP-required parents.

## 5. Cross-References

- Prior parent: `PHASE8-IMPL-016` - frontend owner-action execution workflow and review command boundary
- Decision document: `docs/roadmap/decisions/PHASE8-IMPL-017-apply-promotion-boundary-audit-model-decision.md`
- Next MVP-required parents: `PHASE8-IMPL-018`, `PHASE8-IMPL-019`, `PHASE8-IMPL-020`, `PHASE8-IMPL-021`, `PHASE8-IMPL-022`

## 6. Future Parent Deferrals

- `PHASE8-IMPL-018` owns raw artifact persistence.
- `PHASE8-IMPL-019` owns runtime extraction plus real BookNLP/spaCy install/run/import.
- `PHASE8-IMPL-020` owns model-assisted evidence-backed extraction.
- `PHASE8-IMPL-021` owns NCP/Subtxt/dramatica-flow analysis-only runtime integration.
- `PHASE8-IMPL-022` owns end-to-end MVP usability validation.

Generated context artifacts remain evidence only and must not be treated as roadmap truth:

- `.codex-context/PHASE8-IMPL-016/` (ignored)
- `ai_context/repomix-current-task-context.xml` (ignored; evidence only)
