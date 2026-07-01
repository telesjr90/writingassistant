# PHASE8-IMPL-022

## ID

`PHASE8-IMPL-022`

## Title

End-to-end MVP usability validation

## Status

PHASE8-IMPL-022 is active as the MVP-required end-to-end usability validation parent after completed/PASS `PHASE8-IMPL-021`. `PHASE8-IMPL-022-T001` is complete/PASS as docs/status/planning publication only. `PHASE8-IMPL-022-T002` is complete/PASS as docs/decision/planning only. `PHASE8-IMPL-022-T003` is complete/PASS as expected-red end-to-end MVP smoke/contract tests only. `PHASE8-IMPL-022-T004` is ready/active next as minimal MVP smoke harness implementation. `PHASE8-IMPL-022-T005` through `PHASE8-IMPL-022-T007` are planned.

## Goal

PHASE8-IMPL-022 validates whether the Writer Assistant Core MVP is actually usable end-to-end after `PHASE8-IMPL-014` through `PHASE8-IMPL-021` delivered the required parts.

The parent covers the complete MVP path:

- owner-authored or owner-provided project text
- runtime extraction availability and guarded failure behavior
- raw artifact persistence
- candidate creation/review handoff
- review queue/read-only review surface
- frontend owner-action execution
- explicit audited apply-promotion
- approved memory/canon mutation only through owner-approved workflow
- model-assisted evidence-backed extraction
- analysis-only NCP/Subtxt/dramatica-flow runtime integration
- safe unavailable/quarantine/fail-closed states
- no generated prose/prose-production behavior

## Boundary

PHASE8-IMPL-022 is validation/orchestration/smoke planning first, not feature expansion by default. T001 publishes roadmap records only. T002 defines the validation matrix and acceptance gates only and remains docs/decision/planning only unless explicitly scoped otherwise.

PHASE8-IMPL-022 must not weaken prior boundaries: candidate-first; owner review required; evidence/provenance/source-locator backed when available; confidence is not truth; tool output is not canon; no model output as truth; no automatic canon; no apply-promotion outside explicit audited owner-confirmed path; no memory/canon mutation outside owner-approved workflow; no training artifacts; no generated prose; no rewrite; no continuation; no outline; fail closed; no silent fallback; queue presence is not approval; candidate persistence is not canon.

Fine-tuning remains deferred after MVP. Generated prose/prose-production paths remain permanently forbidden. T001 does not mark MVP complete and does not record an end-to-end usability pass yet. PHASE8-IMPL-022 is the validation parent that will prove or reveal gaps.

## Child Sequence

- `PHASE8-IMPL-022-T001` - Parent publication and MVP usability validation scope. complete/PASS. Output/scope: parent task record, inventory, enrichment JSON, roadmap/status/governance alignment; docs/status/planning publication only.
- `PHASE8-IMPL-022-T002` - MVP end-to-end usability validation matrix and acceptance gates. complete/PASS. Output/scope: `docs/roadmap/decisions/PHASE8-IMPL-022-mvp-usability-validation-matrix-decision.md`; docs/decision/planning only.
- `PHASE8-IMPL-022-T003` - Expected-red end-to-end MVP smoke/contract tests. complete/PASS. Output/scope: `tests/test_writer_assistant_core_mvp_usability_smoke_contract.py` covering the future public APIs `validate_mvp_usability_smoke_matrix`, `validate_mvp_usability_smoke_request`, `build_mvp_usability_smoke_plan`, `validate_mvp_usability_smoke_result`, `build_mvp_usability_evidence_packet`, `classify_mvp_usability_blockers`, and `run_guarded_mvp_usability_smoke` for future `backend.story_knowledge.mvp_usability_smoke`; expected-red collection failure only; tests-first expected-red only; the smoke harness is intentionally not implemented and remains deferred to T004.
- `PHASE8-IMPL-022-T004` - Minimal MVP smoke harness implementation. ready/active next. Will implement the future `backend.story_knowledge.mvp_usability_smoke` module against the T003 expected-red contract and convert the T003 expected-red failures into a green contract.
- `PHASE8-IMPL-022-T005` - MVP workflow fixture and owner-action validation coverage. planned.
- `PHASE8-IMPL-022-T006` - MVP usability safety regression and no-prose/no-canon boundary validation. planned.
- `PHASE8-IMPL-022-T007` - Parent closeout. planned.

## T001 Publication Result

PHASE8-IMPL-022-T001 is complete/PASS as docs/status/planning publication only. It publishes `PHASE8-IMPL-022 - End-to-end MVP usability validation` as the active MVP-required parent, creates the parent task record, inventory, and enrichment JSON, and updates roadmap/status/governance docs only.

T001 added no backend code, tests, routes, frontend code, package/dependency edits, runtime extraction execution, BookNLP/spaCy execution, NCP/Subtxt/dramatica-flow execution, model/Ollama calls, candidate persistence, review queue entries, approved memory/canon mutation, apply-promotion, training/JSONL/dataset/model artifacts, generated prose, rewrite, continuation, outline, draft, revision, polish, expansion, style imitation, export-as-prose, chapter prose, or story prose.

## T002 Result

PHASE8-IMPL-022-T002 is complete/PASS as docs/decision/planning only. It creates `docs/roadmap/decisions/PHASE8-IMPL-022-mvp-usability-validation-matrix-decision.md`, defining the MVP end-to-end usability validation matrix and acceptance gates without adding backend code, tests, routes, frontend code, package/dependency changes, runtime extraction execution, BookNLP/spaCy execution, NCP/Subtxt/dramatica-flow execution, model/Ollama calls, candidates, review queue entries, apply-promotion, approved memory/canon mutation, training artifacts, generated prose, rewrite, continuation, or outline.

## T003 Result

PHASE8-IMPL-022-T003 is complete/PASS as expected-red tests-first only. T003 added the expected-red end-to-end MVP smoke/contract test file `tests/test_writer_assistant_core_mvp_usability_smoke_contract.py` that imports the future `backend.story_knowledge.mvp_usability_smoke` module and asserts the future public API surface (`validate_mvp_usability_smoke_matrix`, `validate_mvp_usability_smoke_request`, `build_mvp_usability_smoke_plan`, `validate_mvp_usability_smoke_result`, `build_mvp_usability_evidence_packet`, `classify_mvp_usability_blockers`, and `run_guarded_mvp_usability_smoke`), the matrix/request/plan/result/evidence-packet/blocker-classification/guarded-run contracts, the gate coverage markers, and the candidate-first, owner-review-required, evidence/provenance/source-locator-backed, fail-closed, no-silent-fallback, no automatic canon, no apply-promotion outside audited owner-confirmed path, no memory/canon mutation outside owner-approved workflow, queue-presence-is-not-approval, candidate-persistence-is-not-canon, no generated prose, no rewrite, no continuation, no outline, and no training artifact boundaries. The future `backend/story_knowledge/mvp_usability_smoke.py` module is intentionally absent, so the target pytest fails at collection with `ModuleNotFoundError: No module named 'backend.story_knowledge.mvp_usability_smoke'`, which is the expected-red signal. T003 did not implement the smoke harness, did not add routes, did not add frontend code, did not change package/dependency files, did not run runtime extraction, did not run BookNLP/spaCy, did not run NCP/Subtxt/dramatica-flow, did not call models/Ollama, did not create candidate records, did not create review queue entries, did not apply-promotion, did not mutate approved memory/canon, did not create training artifacts, and did not generate prose. T003 also did not mark MVP complete and did not claim the end-to-end usability gate; PHASE8-IMPL-022 remains active and the smoke harness implementation is deferred to `PHASE8-IMPL-022-T004`.

## T004 Ready/Active Next Scope

PHASE8-IMPL-022-T004 is ready/active next and should convert the T003 expected-red end-to-end MVP smoke/contract tests into green by implementing the future `backend/story_knowledge/mvp_usability_smoke.py` module and its documented public APIs against the T002 validation matrix and acceptance gates. T004 should remain validation/orchestration/smoke planning first, must not weaken the candidate-first/owner-review/candidate-canon/audit boundaries, and must not mark MVP complete or claim the end-to-end usability gate. Fine-tuning remains deferred after MVP. Generated prose/prose-production paths remain permanently forbidden.
