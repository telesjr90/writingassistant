# PHASE8-IMPL-020

## ID

`PHASE8-IMPL-020`

## Title

Model-assisted evidence-backed extraction and diagnostic workflow

## Status

PHASE8-IMPL-020 is active as the next MVP-required Writer Assistant Core parent after completed/PASS `PHASE8-IMPL-019`. `PHASE8-IMPL-020-T001` is complete/PASS as docs/status/publication only. `PHASE8-IMPL-020-T002` is complete/PASS as docs/decision only. `PHASE8-IMPL-020-T003` is complete/PASS as expected-red tests-only handoff. `PHASE8-IMPL-020-T004` is ready/active next. `PHASE8-IMPL-020-T005` through `PHASE8-IMPL-020-T007` are planned. `PHASE8-IMPL-021` and `PHASE8-IMPL-022` remain future MVP-required parents. Fine-tuning remains deferred after MVP. Generated prose/prose-production paths remain permanently forbidden.

## Goal

Publish and sequence the MVP-required model-assisted evidence-backed extraction and diagnostic workflow parent.

## Scope

This parent defines the controlled path for model assistance inside Writer Assistant Core extraction and diagnostic workflows. Model-assisted output may produce evidence-backed candidate observations, diagnostic questions, uncertainty notes, or candidate extraction support only.

Model-assisted output must never become canon by itself, must never apply promotion, must never mutate approved memory/canon, must never create training data, and must never generate, rewrite, continue, imitate, polish, improve, expand, outline, draft, revise, or produce story prose. Confidence is not truth. Owner review remains mandatory. Apply-promotion remains the separate explicit owner-confirmed path.

Model-assisted extraction and diagnostic workflow outputs must be evidence-backed, provenance-backed, and source-locator-backed when source locators are available. Required terms for future contracts include `source_refs`, `evidence_refs`, `provenance_refs`, and `source_locator_refs`. The publication scan marker `source_locator_refs` is intentionally preserved here alongside the boundary tag `source_locator_required_when_available`.

PHASE8-IMPL-020-T001 is docs/status/publication only. It creates the parent task record, inventory, enrichment JSON, and roadmap/status/governance alignment. T001 does not implement model-assisted extraction, call Ollama, call models, add routes, add UI, edit backend implementation code, edit frontend code, edit tests, install dependencies, create review queue entries, persist candidates, mutate canon, apply promotion, create training artifacts, or generate prose.

PHASE8-IMPL-020-T002 is complete/PASS as docs/decision only at `docs/roadmap/decisions/PHASE8-IMPL-020-model-assisted-extraction-diagnostic-workflow-boundary-decision.md`. T002 accepts the future request/output guard boundary, evidence/provenance/source-locator requirements, diagnostic-question and insufficient-evidence fallback, refusal/no-prose checks, model-output-as-candidate-only boundary, fail-closed behavior, state vocabulary, and no silent fallback rule. T002 performs no model calls, no model-assisted extraction implementation, no backend/frontend/test/package changes, no candidate records, no review queue entries, no apply-promotion, no memory/canon mutation, no training artifacts, and no generated prose.

PHASE8-IMPL-020-T003 is complete/PASS as expected-red tests-only handoff at `tests/test_writer_assistant_core_model_assisted_extraction_contract.py`. T003 adds contract coverage for the future `backend.story_knowledge.model_assisted_extraction` module and public APIs without creating the implementation module. The target test fails red only at the missing future module/API boundary. T003 performs no model calls, no model-assisted extraction implementation, no backend/frontend/package changes, no routes/UI, no candidate records, no review queue entries, no apply-promotion, no memory/canon mutation, no training artifacts, and no generated prose.

PHASE8-UX-001 may be used only as read-only terminology/boundary reference for labels such as review, candidate, evidence, provenance, source locator, approved memory/canon, diagnostic question, uncertainty, no automatic canon, unavailable/quarantined state, and owner action. PHASE8-UX-001 is not roadmap truth, does not override master_plan, implementation_status, roadmap_index, or PHASE8-IMPL parent boundaries, and must not be edited by this parent.

## Child Sequence

- `PHASE8-IMPL-020-T001` - Publish/activate model-assisted evidence-backed extraction parent. complete/PASS. Output/scope: task record, inventory, enrichment JSON, roadmap/status/governance alignment; docs/status only; no model-assisted extraction implementation, no model/Ollama calls, no code/tests/package changes.
- `PHASE8-IMPL-020-T002` - Model-assisted extraction and diagnostic workflow boundary decision. complete/PASS. Output/scope: docs/decision only; accepted request/output guard model, evidence/provenance/source-locator requirements, diagnostic question fallback, refusal/no-prose checks, model-output-as-candidate-only boundary, fail-closed behavior, state vocabulary, and no silent fallback rules.
- `PHASE8-IMPL-020-T003` - Expected-red model-assisted extraction contract tests. complete/PASS. Output/scope: tests-first coverage only for future model-assisted request/output guards, evidence-backed diagnostic/candidate handoff, no automatic canon, no apply-promotion, no memory/canon mutation, no training artifacts, no generated prose, no rewrite, no continuation, no outline generation, no model output as truth, fail closed, and no silent fallback; no implementation module created.
- `PHASE8-IMPL-020-T004` - Minimal model-assisted request/output guard implementation. ready/active. Output/scope: minimal guarded helper only if authorized by T003/T004; no routes/UI/package changes unless explicitly scoped.
- `PHASE8-IMPL-020-T005` - Evidence-backed diagnostic/candidate handoff implementation. planned. Output/scope: evidence-backed candidate/diagnostic handoff only; owner review required; no direct canon, no apply-promotion, no training artifacts, and no generated prose.
- `PHASE8-IMPL-020-T006` - Model-assisted extraction safety regression. planned. Output/scope: focused safety regression and minimal hardening if needed for no automatic canon, no apply-promotion, no memory/canon mutation, no training artifacts, no generated prose, no rewrite, no continuation, no outline, no model output as truth, fail closed, and no silent fallback.
- `PHASE8-IMPL-020-T007` - Parent closeout. planned. Output/scope: docs/status/governance closeout only; prepare PHASE8-IMPL-021 after review.

## Required Risk Linkage

PHASE8-IMPL-020 links to risk register entries for model-assisted extraction output being treated as truth, generated prose/rewrite/continuation/outline leakage, apply-promotion bypass, approved memory/canon mutation outside owner-confirmed workflow, training artifact creation from model output, missing evidence/provenance/source-locator support, silent fallback, and confidence being mistaken for truth.

## Parent Boundary Tags

- `writer_assistant_core`
- `model_assisted_extraction`
- `evidence_backed`
- `diagnostic_workflow`
- `candidate_first`
- `owner_review_required`
- `source_refs_required`
- `evidence_refs_required`
- `provenance_refs_required`
- `source_locator_required_when_available`
- `confidence_is_not_truth`
- `no_automatic_canon`
- `no_apply_promotion`
- `no_memory_canon_mutation`
- `no_training_artifacts`
- `no_generated_prose`
- `no_rewrite`
- `no_continuation`
- `no_outline_generation`
- `no_model_output_as_truth`
- `fail_closed`
- `no_silent_fallback`
- `local_first`
- `ux_reference_terms_only`

## Future Parent Boundaries

NCP/Subtxt/dramatica-flow runtime integration remains `PHASE8-IMPL-021`. End-to-end MVP validation remains `PHASE8-IMPL-022`. Fine-tuning remains deferred after MVP. Generated prose, rewrite, continuation, imitation, polish, improvement, expansion, outline generation, chapter generation, write/revise flows, and prose-production paths remain permanently forbidden.
