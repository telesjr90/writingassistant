# PHASE8-IMPL-017 Inventory

## 1. Task Identity

- Parent ID: `PHASE8-IMPL-017`
- Title: Apply-promotion contract, audit log, and approved memory/canon mutation boundary
- Track: Writer Assistant Core
- Phase: Phase 8
- Status: active MVP-required parent; `PHASE8-IMPL-017-T001` complete/PASS; `PHASE8-IMPL-017-T002` complete/PASS
- Depends on: completed `PHASE8-IMPL-016`
- Current child: `PHASE8-IMPL-017-T003` - ready/active next
- Child sequence: T001 complete/PASS; T002 complete/PASS; T003 ready/active; T004 planned; T005 planned; T006 planned; T007 planned

## 2. Why This Parent Exists

`PHASE8-IMPL-016` delivered owner-action review commands and a frontend owner-action review workflow, but explicitly did not deliver apply-promotion or approved memory/canon mutation. `PHASE8-IMPL-017` is the MVP-required parent that owns the future apply-promotion workflow and the approved memory/canon mutation boundary.

The parent exists to move from candidate review workflow support to an explicit candidate-to-approved transition without making queue state, confidence, extraction output, model output, candidate persistence, or raw artifacts into truth. Apply-promotion must be an explicit owner-confirmed action with audit records, destination checks, evidence/provenance/source locator preservation, and fail-closed behavior.

## 3. Boundary Summary

Allowed in this parent sequence:

- apply-promotion boundary decision and audit model
- tests-first expected-red apply-promotion contract
- minimal backend apply-promotion service/route implementation in a later child
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
