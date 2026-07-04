# PHASE8-UX-003 Harness Route/Workflow Mapping Decision

## 1. Purpose

Decide the exact owner acceptance harness route/workflow mapping for the `PHASE8-UX-003` target B/C blockers before any harness implementation.

This decision maps future owner-harness assertions to existing UI surfaces and existing evidence only. It does not implement the harness, product UI, backend code, tests, browser scripts, candidates, Memory/Canon mutation, model calls, extraction, apply-promotion, or generated prose controls.

## 2. Source evidence

- `docs/roadmap/tasks/PHASE8-UX-003.md`
- `docs/roadmap/inventory/PHASE8-UX-003.md`
- `docs/roadmap/enrichment/PHASE8-UX-003.enrichment.json`
- `docs/roadmap/decisions/PHASE8-UX-002-T007-owner-acceptance-gate-decision.md`
- `docs/roadmap/implementation_status.md`
- `docs/roadmap/validation/latest_roadmap_validation.md`
- `docs/roadmap/decision_log.md`
- `docs/roadmap/risk_register.md`
- `docs/roadmap/open_questions.md`
- `docs/roadmap/task_backlog.md`
- `docs/roadmap/phase_map.md`
- `docs/roadmap/roadmap_index.yaml`
- `artifacts/mvp-readiness/owner-acceptance/evidence-report.md`
- `artifacts/mvp-readiness/owner-acceptance/workflow-log.json`
- `artifacts/mvp-readiness/owner-acceptance/checklist-results.json`
- `scripts/mvp-owner-acceptance-browser-smoke.mjs`
- `scripts/omi-dashboard-browser-smoke.mjs`
- `scripts/omi-candidate-detail-browser-smoke.mjs`
- `scripts/omi-evidence-drawer-browser-smoke.mjs`
- `scripts/omi-apply-promotion-browser-smoke.mjs`
- `docs/roadmap/validation/omi_dashboard_browser_evidence.md`
- `docs/roadmap/validation/omi_candidate_detail_browser_evidence.md`
- `docs/roadmap/validation/omi_evidence_drawer_browser_evidence.md`
- `docs/roadmap/validation/omi_apply_promotion_browser_evidence.md`

## 3. Current PHASE8-UX-003 status

`PHASE8-UX-003` is active as the owner acceptance harness route/workflow evidence follow-up after `PHASE8-UX-002-T007`.

`PHASE8-UX-003-T001` is complete/PASS as docs/status/planning publication only. `PHASE8-UX-003-T002` is complete/PASS by this decision as docs/decision/planning only.

Owner acceptance remains pending. MVP is not complete. `PHASE8-UX-003-T003` is the recommended next child for expected-red owner-harness coverage.

## 4. Non-negotiable boundaries

- Existing UI surfaces only.
- No new product UI unless a later task proves an existing route cannot satisfy the blocker.
- Do not mark owner acceptance PASS.
- Do not mark MVP complete.
- Do not treat OMI evidence as owner acceptance by itself.
- Do not treat queue presence as approval.
- Do not treat confidence as truth.
- Do not treat candidate persistence as canon.
- Do not treat promotion audit records as applied Memory/Canon.
- Do not mutate Memory/Canon.
- Do not create candidates in this decision.
- Do not call models/Ollama.
- Do not run extraction.
- Do not run or enable apply-promotion.
- Do not generate, rewrite, continue, outline, draft, polish, improve, expand, imitate, revise, or produce story prose.
- Do not add generated prose controls.

## 5. Result model for future harness assertions

Future owner-harness assertions must use the existing result vocabulary:

| Result | Meaning |
| --- | --- |
| `PASS` | The harness reached an existing surface and verified the blocker-specific visible evidence without forbidden side effects. |
| `FAIL` | The harness found an exposed forbidden behavior, missing required guard copy on a reachable surface, generated prose, unsafe mutation, bypass, or false success claim. |
| `BLOCKED` | Required infrastructure, startup, browser tooling, backend/frontend availability, or safe fixture prerequisites prevented the assertion from running. |
| `NOT_EXPOSED` | The existing app/harness route did not expose the surface needed for the assertion. This is not a PASS. |
| `MANUAL_REVIEW_REQUIRED` | Automation can gather evidence, but owner judgement or review is still required. This is not a PASS. |

The owner harness may exit `0` while final automated decision remains `MANUAL_REVIEW_REQUIRED`.

## 6. Mapping table for every target B blocker

| Blocker | Existing surface route/workflow | Existing evidence | Future harness assertion | Future result rule |
| --- | --- | --- | --- | --- |
| `candidate_review_candidate_first_visible` | Navigate OMI Dashboard to Candidate Detail for an existing candidate or read-only fixture candidate. | Candidate Detail report PASS; Evidence Drawer report PASS. | Verify candidate-first copy and no Memory/Canon mutation before/after. | `PASS` only if Candidate Detail/Evidence Drawer are reachable and copy is visible; `NOT_EXPOSED` if no candidate/detail route is reachable. |
| `candidate_review_queue_not_approval` | Candidate Detail / review queue status area. | Candidate Detail report shows approval disabled and "ready" is not Memory/Canon change. | Verify queue/readiness copy says queue/readiness is not approval and approval controls remain disabled unless separately authorized. | `PASS` only for explicit visible non-approval copy; queue presence alone is never PASS. |
| `candidate_review_read_only_state` | OMI Dashboard, Candidate Detail, Evidence Drawer. | All three reports record no mutating API requests and unchanged counts/snapshots. | Verify navigation/read-only evidence does not create candidates or mutate approved Memory/Canon. | `PASS` only if before/after snapshots and mutating-request checks are unchanged; otherwise `FAIL`. |
| `candidate_review_owner_action_explicit` | Candidate Detail review controls and disabled owner-action state. | Candidate Detail report shows candidate/field approval disabled with associated reasons. | Verify owner actions require explicit controls and cannot be inferred from detail visibility, queue status, or confidence. | `PASS` only if explicit owner-action controls/reasons are visible; `NOT_EXPOSED` if the route lacks the controls. |
| `candidate_review_confidence_not_truth` | Candidate Detail and Evidence Drawer confidence/support copy. | Candidate Detail and Evidence Drawer reports show confidence as support strength, not truth. | Verify confidence/support wording is visible and not presented as canon truth. | `PASS` only with visible confidence-not-truth copy; missing copy is `FAIL` if route is reached. |
| `candidate_review_persistence_not_canon` | Candidate Detail candidate/canon boundary copy. | Candidate Detail report shows candidate remains candidate until separately confirmed apply-promotion completes. | Verify persisted candidate/review state is visibly not approved Memory/Canon. | `PASS` only with visible not-canon copy and unchanged Memory/Canon snapshot. |
| `apply_promotion_requires_confirmation` | Apply-Promotion Confirmation surface opened from existing OMI shell/fixture. | Apply-Promotion report PASS. | Verify owner final confirmation section exists and final action remains guarded while blockers are visible. | `PASS` only on existing confirmation route; do not run apply-promotion. |
| `apply_promotion_audit_details` | Apply-Promotion Confirmation audit preview/details. | Apply-Promotion report shows Candidate Snapshot, Destination, Target Path, Evidence/Provenance, Source Location, Before-State, Audit Preview. | Verify audit details are visible before any final action. | `PASS` only if audit preview/details are visible; `NOT_EXPOSED` if route cannot be opened. |
| `apply_promotion_only_approved_workflow` | Apply-Promotion Confirmation boundary copy. | Apply-Promotion report shows this is the only screen that may lead to Memory/Canon mutation. | Verify no other OMI surface exposes enabled apply-promotion and confirmation route remains guarded. | `PASS` only if Dashboard/Detail/Drawer lack enabled bypass and Confirmation states the approved workflow boundary. |
| `apply_promotion_failed_rejected_unchanged` | Blocked Apply-Promotion Confirmation before/after snapshot. | Apply-Promotion report shows Memory/Canon unchanged and no request in blocked state. | Verify blocked/rejected state does not submit and Memory/Canon snapshot remains unchanged. | `PASS` only if no apply request is made and snapshots match; any mutation is `FAIL`. |
| `apply_promotion_no_bypass` | Dashboard, Candidate Detail, Evidence Drawer, Apply-Promotion Confirmation. | All four OMI reports show no enabled bypass path and no mutating requests in evidence states. | Verify extraction/model/queue/candidate/evidence routes do not expose enabled bypass to Memory/Canon mutation. | `PASS` only across all four existing OMI evidence surfaces; if any route exposes bypass, `FAIL`. |

## 7. Mapping table for every target C blocker

| Blocker | Existing surface route/workflow | Existing evidence | Future harness assertion | Future result rule |
| --- | --- | --- | --- | --- |
| `manual_workspace_notes_project_scoped` | Existing Notes UI plus existing save/reload path for owner-authored notes. | T006A status records Notes project-scoped evidence UI using existing note APIs and reload proof path; owner acceptance report currently lacks route coverage. | Create or use an owner-authored note through existing UI only, reload project-scoped notes, and verify it is not canon and does not mutate Memory/Canon. | `PASS` only if the existing UI route is reachable and save/reload proof is observed; otherwise `MANUAL_REVIEW_REQUIRED` or `NOT_EXPOSED`. |
| `manual_workspace_materials_project_scoped` | Existing Materials UI plus existing save/reload path for owner-provided materials. | T006A status records Materials project-scoped evidence UI using existing material APIs and reload proof path; owner acceptance report currently lacks route coverage. | Create or use an owner-provided material through existing UI only, reload project-scoped materials, and verify it is not canon and does not mutate Memory/Canon. | `PASS` only if the existing UI route is reachable and save/reload proof is observed; otherwise `MANUAL_REVIEW_REQUIRED` or `NOT_EXPOSED`. |
| `model_assisted_ncp_structured_context_only` | Existing analysis-runtime label/status surface. | T006B status records NCP as structured context interchange only and `NOT_EXPOSED` for runtime execution. | Navigate to the analysis-runtime label surface and verify NCP is label/status only with no runtime execution path. | `PASS` only if label/status is visible; no runtime execution is allowed. |
| `model_assisted_subtxt_rubric_only` | Existing analysis-runtime label/status surface. | T006B status records Subtxt as rubric/diagnostic guidance only and `NOT_EXPOSED` for runtime execution. | Navigate to the analysis-runtime label surface and verify Subtxt is rubric/diagnostic only with no prose-generation or runtime execution path. | `PASS` only if label/status is visible; if not visible, `NOT_EXPOSED`. |
| `model_assisted_dramatica_flow_analysis_only` | Existing analysis-runtime label/status surface. | T006B status records dramatica-flow as analysis-only through audited allowlists and `NOT_EXPOSED` for runtime execution. | Navigate to the analysis-runtime label surface and verify dramatica-flow is analysis-only/audited-allowlist labeled with no generation/revision/continuation path. | `PASS` only if label/status is visible and no execution/generation control appears. |
| `cyber_fixture_story_check_selected_source_path` | Existing owner-authored source create/import/select UI followed by existing selected-source Story Check path. | T004/T005 status records owner-authored source UI and selected-source diagnostic-only Story Check UI; owner acceptance report currently records missing Cyber fixture route in the harness path. | Use the Cyber fixture only as owner-authored analysis input, create/import/select it as an owner-authored source through existing UI, then submit Story Check only after selected-source proof is visible. | `PASS` only if selected source visibly contains the owner-authored fixture and Story Check stays diagnostic-only; missing safe selected-source route is `MANUAL_REVIEW_REQUIRED` or `NOT_EXPOSED`. |
| `cyber_fixture_no_prose_prompt_path` | Existing no-prose refusal/fail-closed UI and selected-source analysis surface. | T005 status records no-prose refusal/fail-closed evidence UI; owner acceptance report currently records missing safe Cyber no-prose route in the harness path. | Verify no-prose refusal/fail-closed evidence for rewrite, continue, outline, draft, polish, improve, expand, imitate, and generate-prose intents without submitting unsafe arbitrary prompts. | `PASS` only if existing no-prose evidence is visible for the Cyber selected-source path; missing safe route remains `MANUAL_REVIEW_REQUIRED` or `NOT_EXPOSED`. |

## 8. A-category manual review table

| A blocker | Future harness handling | Allowed automated evidence | Required final result |
| --- | --- | --- | --- |
| `startup_owner_understands_analysis_boundaries` | Manual owner review only. | Display current boundary evidence/checklist. | `MANUAL_REVIEW_REQUIRED` until owner records acceptance. |
| `project_isolation_playwright_evidence_reviewed` | Manual owner review only. | Reference prior project isolation PASS evidence. | `MANUAL_REVIEW_REQUIRED` until owner records review. |
| `runtime_extraction_unavailable_fail_closed` | Manual owner review only. | Show visible unavailable/fail-closed wording. | `MANUAL_REVIEW_REQUIRED`. |
| `runtime_extraction_failures_no_success_claim` | Manual owner review only. | Show visible failure/no-success-claim wording if available. | `MANUAL_REVIEW_REQUIRED`. |
| `model_assisted_evidence_backed_only` | Manual owner review only. | Gather visible model/Story Check diagnostic evidence when safely selected. | `MANUAL_REVIEW_REQUIRED`. |
| `model_assisted_confidence_not_truth` | Manual owner review only. | Gather confidence-not-truth evidence from existing result surfaces. | `MANUAL_REVIEW_REQUIRED`. |
| `model_assisted_output_not_canon` | Manual owner review only. | Gather output-not-canon evidence from existing result surfaces. | `MANUAL_REVIEW_REQUIRED`. |
| Final owner Accepted/Blocked decision | Owner decision only. | Present evidence bundle and checklist. | `MANUAL_REVIEW_REQUIRED` until owner explicitly decides. |

## 9. Existing UI/evidence surface inventory

| Surface | Existing evidence | Current role in PHASE8-UX-003 |
| --- | --- | --- |
| Owner acceptance harness | `scripts/mvp-owner-acceptance-browser-smoke.mjs`; artifacts under `artifacts/mvp-readiness/owner-acceptance/`. | Result model and final decision carrier; currently `MANUAL_REVIEW_REQUIRED`. |
| OMI Dashboard | `docs/roadmap/validation/omi_dashboard_browser_evidence.md`; `scripts/omi-dashboard-browser-smoke.mjs`. | B mapping support for dashboard reachability, disabled apply, candidate/canon separation, no mutation. |
| OMI Candidate Detail | `docs/roadmap/validation/omi_candidate_detail_browser_evidence.md`; `scripts/omi-candidate-detail-browser-smoke.mjs`. | B mapping support for candidate-first, confidence-not-truth, candidate-not-canon, read-only review. |
| OMI Evidence Drawer | `docs/roadmap/validation/omi_evidence_drawer_browser_evidence.md`; `scripts/omi-evidence-drawer-browser-smoke.mjs`. | B mapping support for evidence/provenance, confidence/support, no apply path, read-only behavior. |
| Apply-Promotion Confirmation | `docs/roadmap/validation/omi_apply_promotion_browser_evidence.md`; `scripts/omi-apply-promotion-browser-smoke.mjs`. | B mapping support for confirmation, audit details, blocked unchanged state, no bypass. |
| Notes/Materials UI | T006A roadmap/status evidence. | C mapping target for project-scoped save/reload proof. |
| Analysis-runtime label/status UI | T006B roadmap/status evidence. | C mapping target for NCP/Subtxt/dramatica-flow label-only assertions. |
| Owner-authored source UI | T004 roadmap/status evidence. | C mapping target for Cyber fixture source create/import/select before Story Check. |
| Selected-source Story Check UI | T005 roadmap/status evidence. | C mapping target for Cyber diagnostic-only selected-source Story Check. |
| No-prose refusal/fail-closed UI | T005 roadmap/status evidence. | C mapping target for Cyber no-prose evidence without unsafe prompt submission. |

## 10. Future T003 expected-red coverage plan

`PHASE8-UX-003-T003` should add expected-red owner-harness coverage only. It should not wire the harness or change product code.

Expected-red targets:

- B OMI route coverage for Dashboard, Candidate Detail, Evidence Drawer, and Apply-Promotion Confirmation.
- B assertion IDs matching all target B blockers.
- C Notes/Materials route coverage for project-scoped save/reload proof.
- C analysis-runtime label coverage for NCP, Subtxt, and dramatica-flow.
- C Cyber selected-source route coverage for owner-authored source create/import/select before Story Check.
- C Cyber no-prose route coverage for refusal/fail-closed evidence.
- Result model enforcement: missing route is `NOT_EXPOSED` or `MANUAL_REVIEW_REQUIRED`, never fake `PASS`.
- Final automated decision remains `MANUAL_REVIEW_REQUIRED` while A items or final owner decision remain unresolved.

## 11. Future T004 owner harness wiring plan

`PHASE8-UX-003-T004` should wire the owner harness to existing Notes/Materials, OMI review, OMI apply-promotion, and analysis-runtime label surfaces.

Planned split:

- Wire B OMI review assertions to the existing OMI evidence workflows or equivalent browser navigation.
- Wire B apply-promotion assertions to the guarded confirmation route without submitting apply-promotion.
- Wire C Notes/Materials assertions to existing project-scoped create/save/reload UI proof.
- Wire C NCP/Subtxt/dramatica-flow assertions to existing label/status surfaces.
- Preserve no mutation and no generated prose controls.

## 12. Future T005 Cyber fixture selected-source/no-prose wiring plan

`PHASE8-UX-003-T005` should wire the Cyber fixture path only through existing owner-authored source UI and existing selected-source analysis surfaces.

Planned split:

- Create/import/select the Cyber fixture as owner-authored source material through the browser UI.
- Verify selected source contains the owner-authored fixture before Story Check.
- Run Story Check only after selected-source proof and only through the app UI.
- Verify result is diagnostic/candidate analysis only, not canon/truth/approved Memory.
- Verify no generated story prose appears.
- Verify no-prose refusal/fail-closed evidence for unsafe rewrite/continue/outline/draft/polish/improve/expand/imitate/generate-prose intents.
- Do not submit unsafe arbitrary prompts through a freeform generation route.

## 13. Pass/fail/manual-review rules

- `PASS` requires a reachable existing UI/evidence surface, blocker-specific visible evidence, and no forbidden side effects.
- `FAIL` is required for generated prose, unsafe mutation, apply-promotion execution during blocked evidence, enabled bypass, confidence presented as truth, queue treated as approval, candidate persistence treated as canon, or false extraction success.
- `NOT_EXPOSED` is required when the current route does not expose the needed surface.
- `MANUAL_REVIEW_REQUIRED` is required when owner judgement is necessary even if evidence is gathered.
- B/C automation can reduce route/workflow blockers, but cannot complete A manual-review items or the final owner decision.

## 14. Failure and unavailable-state rules

- Missing browser route, selector, fixture prerequisite, or safe selected source must not be fake-passed.
- Tooling/startup failures are `BLOCKED` if the assertion cannot run.
- Runtime/extraction unavailability must be explicit and fail closed.
- Failed runtime checks must not claim extraction success.
- Backend unavailable fixture mode may support route evidence only when mutating requests are blocked and the report states fixture mode.
- Apply-promotion confirmation evidence must remain blocked/guarded unless a later authorized task explicitly permits a real owner-confirmed apply-promotion run.

## 15. What must not happen

- Do not implement frontend code, backend code, tests, or browser harness scripts in T002.
- Do not create candidates.
- Do not mutate Memory/Canon.
- Do not call models/Ollama.
- Do not run extraction.
- Do not run or enable apply-promotion.
- Do not add generated prose controls.
- Do not add arbitrary prompt boxes.
- Do not treat existing OMI evidence as owner acceptance by itself.
- Do not mark owner acceptance PASS.
- Do not mark MVP complete.
- Do not stage, commit, or push.

## 16. Open questions

- During T004, should the owner harness reference existing OMI evidence reports directly, rerun equivalent OMI route navigation inside the owner harness, or do both? Recommended: rerun equivalent route navigation where safe and retain report references as supporting evidence.
- During T005, if the Cyber fixture selected-source route is still not reachable through existing UI, should the harness keep the result `MANUAL_REVIEW_REQUIRED` or should a later product UI follow-up be proposed? Recommended: keep `MANUAL_REVIEW_REQUIRED`/`NOT_EXPOSED` in T005 and propose product UI only after proving the existing route cannot satisfy the blocker.

## 17. Next child recommendation

Proceed to `PHASE8-UX-003-T003` for expected-red owner-harness coverage for the mapped B/C blockers.

T003 should remain expected-red harness coverage only and must not change product UI, backend code, owner acceptance status, MVP completion status, candidates, Memory/Canon, model/extraction behavior, apply-promotion behavior, or generated prose controls.
