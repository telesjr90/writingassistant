# PHASE8-IMPL-017

## ID

`PHASE8-IMPL-017`

## Title

Apply-promotion contract, audit log, and approved memory/canon mutation boundary

## Status

Complete/PASS MVP-required parent after committed `PHASE8-IMPL-016` closeout. `PHASE8-IMPL-017-T001` is complete/PASS after publishing this parent record, inventory, enrichment JSON, and roadmap/status updates. `PHASE8-IMPL-017-T002` is complete/PASS after accepting the apply-promotion boundary decision and audit model at `docs/roadmap/decisions/PHASE8-IMPL-017-apply-promotion-boundary-audit-model-decision.md`. `PHASE8-IMPL-017-T003` is complete/PASS as an expected-red contract handoff at `tests/test_writer_assistant_core_apply_promotion_contract.py`. `PHASE8-IMPL-017-T004` is complete/PASS after implementing the minimal backend apply-promotion service at `backend/story_knowledge/apply_promotion.py`, the backend route at `backend/routes/apply_promotion.py`, and route inclusion in `backend/main.py`. `PHASE8-IMPL-017-T005` is complete/PASS after implementing the minimal frontend apply-promotion confirmation workflow/surface. `PHASE8-IMPL-017-T006` is complete/PASS after adding approved memory/canon mutation safety regression coverage. `PHASE8-IMPL-017-T007` is complete/PASS after parent closeout. Recommended next parent: `PHASE8-IMPL-018` - Raw artifact persistence implementation and project-local extraction artifact lifecycle.

## Goal

Define and sequence the MVP-required apply-promotion workflow and approved memory/canon mutation boundary. This parent owns the future explicit owner-confirmed apply-promotion path, audited promotion records, and approved memory/canon mutation only after explicit owner action.

## Scope

This parent follows `PHASE8-IMPL-016`, which delivered owner-action review command workflow only. `PHASE8-IMPL-017` is the first parent allowed to design and implement the candidate-to-approved boundary, but `PHASE8-IMPL-017-T001` is docs/status publication only, `PHASE8-IMPL-017-T002` is docs/decision/status only, and `PHASE8-IMPL-017-T003` is tests/docs/status only. `PHASE8-IMPL-017-T004` implements only the minimal backend apply-promotion service/route boundary needed by the contract: explicit owner-confirmed promotion requests, validated plans, approved-memory writes, and immutable project-local audit records. `PHASE8-IMPL-017-T005` implements only the minimal frontend confirmation surface and API helper needed to call the backend apply-promotion route after final owner confirmation. `PHASE8-IMPL-017-T006` adds focused safety regression coverage for approved memory/canon mutation boundaries and minimal source marker hardening only. `PHASE8-IMPL-017-T007` is docs/status/governance closeout only.

The parent must keep apply-promotion explicit, owner-confirmed, and audited. It must not automatically promote based on confidence, queue status, model output, extraction, candidate persistence, or raw artifact presence. Queue presence is not approval. Confidence is not truth. Candidate persistence is not canon. Extraction is not canon.

Apply-promotion must not call models, run extraction, persist raw artifacts, create training artifacts, or generate prose. Generated prose and prose-production paths remain permanently forbidden.

## Child Sequence

- `PHASE8-IMPL-017-T001` - Parent publication/inventory/enrichment/status alignment. Complete/PASS.
- `PHASE8-IMPL-017-T002` - Apply-promotion boundary decision and audit model. Complete/PASS. Decision: `docs/roadmap/decisions/PHASE8-IMPL-017-apply-promotion-boundary-audit-model-decision.md`.
- `PHASE8-IMPL-017-T003` - Tests-first expected-red apply-promotion contract. Complete/PASS. Contract: `tests/test_writer_assistant_core_apply_promotion_contract.py`.
- `PHASE8-IMPL-017-T004` - Minimal backend apply-promotion service/route implementation. Complete/PASS. Implementation: `backend/story_knowledge/apply_promotion.py`; route: `backend/routes/apply_promotion.py`.
- `PHASE8-IMPL-017-T005` - Frontend apply-promotion confirmation workflow/surface. Complete/PASS.
- `PHASE8-IMPL-017-T006` - Approved memory/canon mutation safety regression. Complete/PASS. Regression: `tests/test_apply_promotion_memory_canon_safety_regression.py`.
- `PHASE8-IMPL-017-T007` - Parent closeout. Complete/PASS.

## Closeout Summary

`PHASE8-IMPL-017` is complete/PASS. The parent delivered:

- T001 parent publication/inventory/enrichment/status alignment.
- T002 apply-promotion boundary decision and audit model.
- T003 expected-red apply-promotion contract tests.
- T004 backend apply-promotion service and route.
- T005 frontend apply-promotion confirmation workflow/surface.
- T006 approved memory/canon mutation safety regression.
- T007 parent closeout.

Delivered implementation and test inventory:

- Backend module: `backend/story_knowledge/apply_promotion.py`.
- Backend route: `backend/routes/apply_promotion.py`.
- Route path: `POST /api/projects/{project_id}/apply-promotion`.
- Frontend API helper: `submitApplyPromotion(projectId, payload)` in `frontend/src/api.js`.
- Frontend confirmation component: `frontend/src/components/ApplyPromotionConfirmation.jsx`.
- Safety regression: `tests/test_apply_promotion_memory_canon_safety_regression.py`.
- Contract tests: `tests/test_writer_assistant_core_apply_promotion_contract.py`.
- Frontend source tests: `tests/test_frontend_apply_promotion_workflow_source.py`.

Boundary closeout:

- Apply-promotion is explicit owner-confirmed only.
- Apply-promotion is audited.
- Approved memory/canon mutation occurs only through valid apply-promotion.
- Candidate persistence is not canon.
- Queue presence is not approval.
- Confidence is not truth.
- Raw artifacts are support data, not canon.
- Review queue actions do not mutate approved memory/canon.
- Frontend review commands remain separate from apply-promotion.
- Plan-building/validation performs no approved memory/canon mutation.
- Failed validation performs no partial mutation.
- Successful apply writes approved memory/canon plus applied audit record.
- No raw artifact persistence.
- No runtime extraction.
- No BookNLP/spaCy install/run/import.
- No model/Ollama calls.
- No NCP/Subtxt/dramatica-flow runtime.
- No generated prose.
- No training/JSONL/dataset/model artifacts.
- No package/dependency changes.

Validation evidence for T007 closeout: focused PHASE8-IMPL-017 regressions, existing backend review/candidate regressions, `scripts/check_enrichment.py`, `scripts/validate_roadmap.py`, T007 closeout status scan, T007 boundary scan, source-cache/generated artifact safety, and git diff/status checks are the required final validation set.

Recommended next parent: `PHASE8-IMPL-018` - Raw artifact persistence implementation and project-local extraction artifact lifecycle. `PHASE8-IMPL-019` through `PHASE8-IMPL-022` remain future MVP-required parents. Fine-tuning remains deferred after MVP. Generated prose/prose-production paths remain permanently forbidden.

## Boundary Tags

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

## Deferred Boundaries

This parent does not authorize `PHASE8-IMPL-017-T001`, `PHASE8-IMPL-017-T002`, or `PHASE8-IMPL-017-T003` to implement runtime behavior. T002 defines the apply-promotion boundary and audit model only. T003 adds expected-red contract tests only. T004 implements the minimal backend apply-promotion module and route only. T005 implements the minimal frontend API helper and confirmation surface only. T006 adds approved memory/canon safety regression coverage and minimal source marker hardening only. T004/T005/T006 do not implement raw artifact persistence, runtime extraction, model-assisted extraction, real BookNLP/spaCy install/run/import, NCP/Subtxt/dramatica-flow runtime integration, generated prose, or training artifacts.

Raw artifact persistence remains `PHASE8-IMPL-018`. Runtime extraction plus real BookNLP/spaCy install/run/import remains `PHASE8-IMPL-019`. Model-assisted evidence-backed extraction remains `PHASE8-IMPL-020`. NCP/Subtxt/dramatica-flow analysis-only runtime remains `PHASE8-IMPL-021`. End-to-end MVP validation remains `PHASE8-IMPL-022`.

Fine-tuning remains deferred after MVP.
