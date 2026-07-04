# PHASE8-UX-003 - Owner Acceptance Harness Route/Workflow Evidence Follow-up

## Status

`PHASE8-UX-003` is published as the follow-up parent for owner acceptance harness route/workflow evidence coverage after `PHASE8-UX-002-T007`.

`PHASE8-UX-003-T001` is complete/PASS as docs/status/planning publication only. No frontend code, backend code, tests, browser harness scripts, candidates, Memory/Canon mutation, model/Ollama calls, extraction, apply-promotion, generated prose controls, staging, commit, or push were performed.

`PHASE8-UX-003-T002` is the next planned child.

Owner acceptance remains pending. MVP is not complete.

## Purpose

Wire the owner acceptance harness to already-existing PASS surfaces and route/workflow evidence, so owner acceptance can distinguish:

- Items already covered by OMI evidence.
- Items needing harness navigation only.
- Items requiring owner manual review.
- Items unavailable by design.

This follow-up targets the remaining B/C blockers from `docs/roadmap/decisions/PHASE8-UX-002-T007-owner-acceptance-gate-decision.md` without reopening `PHASE8-UX-002` and without adding new product UI by default.

## Scope

- Harness route/workflow evidence only.
- Existing UI surfaces only.
- No new product UI unless a later task explicitly proves it is required.
- No Memory/Canon mutation.
- No apply-promotion execution.
- No generated prose.
- No model output treated as canon or truth.
- No runtime extraction success claim.

## Target B Blockers

- `candidate_review_candidate_first_visible`
- `candidate_review_queue_not_approval`
- `candidate_review_read_only_state`
- `candidate_review_owner_action_explicit`
- `candidate_review_confidence_not_truth`
- `candidate_review_persistence_not_canon`
- `apply_promotion_requires_confirmation`
- `apply_promotion_audit_details`
- `apply_promotion_only_approved_workflow`
- `apply_promotion_failed_rejected_unchanged`
- `apply_promotion_no_bypass`

These are already covered by OMI Dashboard, Candidate Detail, Evidence Drawer, and Apply-Promotion Confirmation browser evidence, but they were not wired into the owner acceptance harness route/workflow.

## Target C Blockers

- `manual_workspace_notes_project_scoped`
- `manual_workspace_materials_project_scoped`
- `model_assisted_ncp_structured_context_only`
- `model_assisted_subtxt_rubric_only`
- `model_assisted_dramatica_flow_analysis_only`
- `cyber_fixture_story_check_selected_source_path`
- `cyber_fixture_no_prose_prompt_path`

These need harness route/workflow coverage through existing Notes/Materials, analysis-runtime label, owner-authored source, Story Check, and no-prose evidence surfaces.

## Manual Review Only A Blockers

The follow-up must not target these as automation PASS:

- `startup_owner_understands_analysis_boundaries`
- `project_isolation_playwright_evidence_reviewed`
- `runtime_extraction_unavailable_fail_closed`
- `runtime_extraction_failures_no_success_claim`
- `model_assisted_evidence_backed_only`
- `model_assisted_confidence_not_truth`
- `model_assisted_output_not_canon`
- final explicit owner Accepted/Blocked decision

Automation may gather evidence for these items, but owner judgement remains required.

## Boundaries

- Analysis-only.
- Candidate-first.
- Owner review required.
- Evidence/provenance-backed.
- Owner-controlled.
- Owner-authored prose storage/editing is allowed.
- Generated prose/prose-production remains permanently forbidden.
- No rewrite, continuation, imitation, polish, improvement, expansion, outline, draft, chapter generation, or story-prose-production controls.
- Queue presence is not approval.
- Confidence is not truth.
- Candidate persistence is not canon.
- Raw artifacts are support data only.
- Apply-promotion remains explicit, audited, owner-confirmed, and guarded.
- Apply-promotion stays disabled/guarded in browser smoke evidence unless a later authorized apply-promotion implementation task exists.
- No model/Ollama calls.
- No extraction.
- No apply-promotion execution.
- No Memory/Canon mutation.
- No candidate creation.
- No product UI expansion by default.

## Planned Child Sequence

- `PHASE8-UX-003-T001` - Publish follow-up parent/task records only. Status: complete/PASS. Scope: docs/status/planning only.
- `PHASE8-UX-003-T002` - Decide harness route/workflow mapping for B/C blockers. Scope: docs/decision/planning only.
- `PHASE8-UX-003-T003` - Add expected-red harness coverage for target B/C blockers. Scope: harness/test planning or expected-red coverage only when explicitly authorized.
- `PHASE8-UX-003-T004` - Wire owner harness to existing Notes/Materials, OMI review, OMI apply-promotion, and analysis-runtime label surfaces. Scope: browser harness route/workflow only; existing UI surfaces only.
- `PHASE8-UX-003-T005` - Wire Cyber fixture selected-source Story Check and no-prose evidence paths using existing owner-authored source UI only. Scope: browser harness route/workflow only.
- `PHASE8-UX-003-T006` - Rerun owner acceptance harness and classify remaining manual items. Scope: validation/evidence only.
- `PHASE8-UX-003-T007` - Closeout and owner Accepted/Blocked gate preparation. Scope: docs/status/governance only; do not mark owner acceptance PASS.

## Validation Commands

T001 validation:

```bash
python3 scripts/check_enrichment.py
python3 scripts/validate_roadmap.py
python3 -m json.tool docs/roadmap/enrichment/PHASE8-UX-002.enrichment.json >/dev/null
git diff --check
git status --short --branch
git diff --name-only
```

## Non-Goals

- Do not reopen `PHASE8-UX-002`.
- Do not classify this follow-up as MVP complete.
- Do not mark owner acceptance PASS.
- Do not implement frontend code.
- Do not implement backend code.
- Do not edit tests in T001.
- Do not edit browser harness scripts in T001.
- Do not create candidates.
- Do not mutate Memory/Canon.
- Do not call models/Ollama.
- Do not run extraction.
- Do not run or enable apply-promotion.
- Do not add generated prose controls.
- Do not stage, commit, or push.

## Publication Note

`PHASE8-UX-003` is MVP-required only as owner acceptance harness evidence coverage if the owner requires additional automated route/workflow evidence before final acceptance. It does not itself complete MVP and cannot replace the final explicit owner Accepted/Blocked decision.
