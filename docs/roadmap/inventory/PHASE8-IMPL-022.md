# PHASE8-IMPL-022 Inventory

## Parent

- ID: `PHASE8-IMPL-022`
- Title: End-to-end MVP usability validation
- Status: active
- T001 status: complete/PASS as docs/status/planning publication only
- T002 status: complete/PASS as docs/decision/planning only
- T003 status: complete/PASS as expected-red end-to-end MVP smoke/contract tests only
- T004 status: ready/active next as minimal MVP smoke harness implementation
- T005 through T007 status: planned

## Parent Records

- Task record: `docs/roadmap/tasks/PHASE8-IMPL-022.md`
- Inventory record: `docs/roadmap/inventory/PHASE8-IMPL-022.md`
- Enrichment record: `docs/roadmap/enrichment/PHASE8-IMPL-022.enrichment.json`
- T002 decision record: `docs/roadmap/decisions/PHASE8-IMPL-022-mvp-usability-validation-matrix-decision.md`

## Validation Scope Inventory

PHASE8-IMPL-022 validates the complete Writer Assistant Core MVP path:

- owner-authored or owner-provided project text
- runtime extraction availability and guarded failure behavior
- raw artifact persistence
- candidate creation/review handoff
- candidate review and review queue/read-only review surface
- frontend owner-action execution
- explicit audited apply-promotion
- approved memory/canon mutation only through owner-approved workflow
- model-assisted evidence-backed extraction
- analysis-only NCP/Subtxt/dramatica-flow runtime integration
- safe unavailable/quarantine/fail-closed states
- no generated prose/prose-production behavior

## Child Inventory

- `PHASE8-IMPL-022-T001` - Parent publication and MVP usability validation scope. complete/PASS. Docs/status/planning publication only.
- `PHASE8-IMPL-022-T002` - MVP end-to-end usability validation matrix and acceptance gates. complete/PASS. Docs/decision/planning only; decision record is `docs/roadmap/decisions/PHASE8-IMPL-022-mvp-usability-validation-matrix-decision.md`.
- `PHASE8-IMPL-022-T003` - Expected-red end-to-end MVP smoke/contract tests. complete/PASS. Expected-red collection failure only; final test artifact is `tests/test_writer_assistant_core_mvp_usability_smoke_contract.py` covering the future public APIs `validate_mvp_usability_smoke_matrix`, `validate_mvp_usability_smoke_request`, `build_mvp_usability_smoke_plan`, `validate_mvp_usability_smoke_result`, `build_mvp_usability_evidence_packet`, `classify_mvp_usability_blockers`, and `run_guarded_mvp_usability_smoke` for future `backend.story_knowledge.mvp_usability_smoke`; tests-first expected-red only; the smoke harness is intentionally not implemented.
- `PHASE8-IMPL-022-T004` - Minimal MVP smoke harness implementation. ready/active next. Will implement the future `backend.story_knowledge.mvp_usability_smoke` module against the T003 expected-red contract.
- `PHASE8-IMPL-022-T005` - MVP workflow fixture and owner-action validation coverage. planned.
- `PHASE8-IMPL-022-T006` - MVP usability safety regression and no-prose/no-canon boundary validation. planned.
- `PHASE8-IMPL-022-T007` - Parent closeout. planned.

## Boundary Inventory

PHASE8-IMPL-022 is validation/orchestration/smoke planning first, not feature expansion by default.

Required preserved boundaries: candidate-first; owner review required; evidence/provenance/source-locator backed when available; confidence is not truth; tool output is not canon; no model output as truth; no automatic canon; no apply-promotion outside explicit audited owner-confirmed path; no memory/canon mutation outside owner-approved workflow; no training artifacts; no generated prose; no rewrite; no continuation; no outline; fail closed; no silent fallback; queue presence is not approval; candidate persistence is not canon.

Fine-tuning remains deferred after MVP. Generated prose/prose-production paths remain permanently forbidden. T001 does not mark MVP complete and does not record an end-to-end usability pass yet.
