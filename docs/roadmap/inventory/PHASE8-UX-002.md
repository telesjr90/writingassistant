# PHASE8-UX-002 Inventory

## Relevant Docs

- `docs/roadmap/decisions/PHASE8-UX-002-ui-acceptance-matrix-route-workflow-decision.md`
- `docs/roadmap/ux/PHASE8-UX-002-ui-acceptance-matrix.md`
- `docs/roadmap/ux/PHASE8-UX-001-master-plan-ux-navigation-proposal.md`
- `docs/roadmap/ux/PHASE8-UX-001-impeccable-ui-ux-qa-workflow.md`
- `docs/roadmap/ux/PHASE8-UX-002-prepublication-reference-research-boundary.md`
- `docs/roadmap/ux/PHASE8-UX-002-prepublication-controlled-experiment-method.md`
- `docs/roadmap/validation/mvp_owner_acceptance_browser_evidence.md`
- `docs/roadmap/validation/mvp_owner_manual_acceptance_checklist.md`
- `docs/roadmap/validation/latest_roadmap_validation.md`
- `docs/roadmap/implementation_status.md`
- `docs/roadmap/roadmap_index.yaml`
- `docs/roadmap/task_backlog.md`
- `docs/roadmap/phase_map.md`
- `docs/roadmap/decision_log.md`
- `docs/roadmap/risk_register.md`
- `docs/roadmap/open_questions.md`
- `docs/roadmap/context_execution_standard.md`
- `docs/master_plan.md`

## Relevant Harness / Evidence Artifacts

- `scripts/mvp-owner-acceptance-browser-smoke.mjs`
- `docs/roadmap/validation/mvp_owner_acceptance_browser_evidence.md`
- `docs/roadmap/validation/mvp_owner_manual_acceptance_checklist.md`
- `artifacts/mvp-readiness/owner-acceptance/` as owner-run evidence output, not committed roadmap truth.
- `artifacts/mvp-readiness/project-isolation/` as prior project isolation browser evidence output.
- `scripts/omi-dashboard-browser-smoke.mjs`
- `scripts/omi-candidate-detail-browser-smoke.mjs`
- `scripts/omi-evidence-drawer-browser-smoke.mjs`
- `scripts/omi-apply-promotion-browser-smoke.mjs`
- `docs/roadmap/validation/omi_dashboard_browser_evidence.md`
- `docs/roadmap/validation/omi_candidate_detail_browser_evidence.md`
- `docs/roadmap/validation/omi_evidence_drawer_browser_evidence.md`
- `docs/roadmap/validation/omi_apply_promotion_browser_evidence.md`

The T007 owner acceptance harness rerun reached exit `0`, but final automated decision remains `MANUAL_REVIEW_REQUIRED`. Owner acceptance remains pending and MVP is not complete.

## Planned Frontend Areas to Inspect in Later Tasks

Later implementation or tests-first tasks may inspect only when explicitly scoped:

- Project creation, project selection, project header, and active project routing.
- Scene/source list, create/import/select controls, selected source state, save/reload state, and selected-source Story Check binding.
- `AnalysisSidebar` / Story Check control and result display.
- Safe no-prose refusal/fail-closed UI surfaces for forbidden prose-production intents.
- Notes and Materials navigation, body editor, create controls, save/reload behavior, and project isolation.
- Runtime/raw artifact unavailable/read-only support-data labels and evidence surfaces.
- Review queue display, owner-action controls, candidate-only/non-canon labels, and explicit no-promotion warnings.
- Apply-promotion confirmation UI, audit detail display, and failed/rejected unchanged-memory/canon evidence.
- Memory/Canon approved-only views.
- NCP/Subtxt/dramatica-flow `NOT_EXPOSED` or analysis-label-only status surfaces.

## Planned Backend/API Areas to Inspect Only If Later Implementation Requires Route Support

Later tasks may inspect backend/API areas only if explicitly scoped by the child task:

- Existing project/scene/source routes and storage helpers.
- Existing Story Check route behavior, selected-source requirements, and unavailable/fail-closed response shape.
- Notes and Materials routes and storage helpers for create/save/reload proof.
- Review queue routes and review API helpers.
- Apply-promotion route and audit helpers, including invalid-promotion fail-closed behavior and unchanged approved memory/canon proof.
- Raw artifact manifest/read/list helpers for read-only evidence or unavailable status.
- Runtime extraction availability/status helpers.
- Analysis runtime helper/status boundaries for NCP, Subtxt, and dramatica-flow.

No backend/API inspection in T002 authorizes route changes, behavior changes, runtime execution, model calls, or product implementation.

## T002 Artifacts

- Decision doc: `docs/roadmap/decisions/PHASE8-UX-002-ui-acceptance-matrix-route-workflow-decision.md`
- Acceptance matrix: `docs/roadmap/ux/PHASE8-UX-002-ui-acceptance-matrix.md`
- T003 next scope: expected-red tests for source/scene create/import/select, Story Check disabled/result states, no-prose refusal/fail-closed paths, Notes/Materials save/reload proof, runtime/raw artifact unavailable/read-only evidence, review/apply-promotion confirmation/audit evidence, and NCP/Subtxt/dramatica-flow exposure decision behavior.
- T004/T005/T006 implementation split: T004 source/scene workflow, T005 Story Check/no-prose evidence UI, T006 Notes/Materials plus runtime/review evidence UI.
- Backend/frontend areas remain future inspection only and were not touched in T002.

## T003 Expected-Red Test Artifact

- Expected-red test file: `tests/test_phase8_ux002_mvp_ui_acceptance_expected_red.py`.
- Targeted expected-red command: `.venv-unsloth-clean/bin/python -m pytest tests/test_phase8_ux002_mvp_ui_acceptance_expected_red.py -q`.
- Expected-red result: `7 failed in 0.12s`; pytest reached collection and execution, and all failures are intended assertion failures for missing PHASE8-UX-002 MVP browser-visible UI/workflow contract markers.
- System Python note: `python3 -m pytest tests/test_phase8_ux002_mvp_ui_acceptance_expected_red.py -q` fails before collection because `/usr/bin/python3` has no `pytest` module, but this is not a T003 blocker because the repo's existing virtualenv is the validated test interpreter.
- Intended red failure summary: `UX2-SOURCE-001` source create/import/select markers missing; `UX2-STORYCHECK-001` selected-source diagnostic-only Story Check markers missing; `UX2-NOPROSE-001` no-prose refusal/fail-closed markers missing; `UX2-NOTES-MATERIALS-001` notes/materials create/save/reload markers missing; `UX2-RAW-ARTIFACT-001` runtime unavailable/read-only raw artifact evidence markers missing; `UX2-REVIEW-PROMOTION-001` review/apply-promotion confirmation and audit markers missing; `UX2-ANALYSIS-RUNTIME-001` `NOT_EXPOSED`/label-only analysis runtime markers missing.
- T003 is complete/PASS as tests-first expected-red only. No frontend implementation, backend implementation, route/API changes, product behavior changes, crawler scripts, raw captures, `.external_sources`, context artifacts, model calls, generated prose, canon/memory mutation, candidate creation, apply-promotion shortcut, package/dependency changes, staging, commit, or push occurred.
- Future implementation owner: `PHASE8-UX-002-T004` for owner-authored source/scene create/import/select UI.
- Future implementation owner: `PHASE8-UX-002-T005` for Story Check diagnostic-only/no-prose evidence UI.
- Future implementation owner: `PHASE8-UX-002-T006` for Notes/Materials plus runtime/review evidence UI.

## T004 Owner-Authored Source UI Implementation

- Status: `PHASE8-UX-002-T004` complete/PASS.
- Implementation files touched: `frontend/src/App.jsx`, `frontend/src/api.js`, and `frontend/src/components/ProjectNav.jsx`; `frontend/src/components/AnalysisSidebar.jsx` was updated only for selected-source fail-closed Story Check gating/copy.
- `UX2-SOURCE-001` is implemented/source-gated: owner can create/import an owner-authored source through the browser using existing project-scoped scene save/list behavior, choose a project-scoped selected source, and see selected source state before Story Check.
- Focused source test: `.venv-unsloth-clean/bin/python -m pytest tests/test_phase8_ux002_mvp_ui_acceptance_expected_red.py -q -k ux2_source_001` -> `1 passed, 6 deselected in 0.03s`.
- Full expected-red file after T004: `.venv-unsloth-clean/bin/python -m pytest tests/test_phase8_ux002_mvp_ui_acceptance_expected_red.py -q` -> `1 passed, 6 failed`; remaining expected-red surfaces are limited to `UX2-STORYCHECK-001`, `UX2-NOPROSE-001`, `UX2-NOTES-MATERIALS-001`, `UX2-RAW-ARTIFACT-001`, `UX2-REVIEW-PROMOTION-001`, and `UX2-ANALYSIS-RUNTIME-001`.
- T004 keeps selected source UI state only. Selected source is not canon, memory, training data, approved truth, a candidate promotion, or owner acceptance.
- T005 is next for Story Check diagnostic-only/no-prose evidence UI.
- Owner acceptance remains pending; MVP is not complete. External SaaS investigation remains post-MVP/deferred. No generated prose/prose-production behavior, backend route/API changes, package changes, context artifact updates, crawlers/raw captures, model calls, canon/memory mutation, apply-promotion shortcut, staging, commit, or push occurred.

## T005 Story Check Diagnostic-Only / No-Prose Evidence UI Implementation

- Status: `PHASE8-UX-002-T005` complete/PASS.
- Implementation files touched: `frontend/src/App.jsx`, `frontend/src/api.js`, and `frontend/src/components/AnalysisSidebar.jsx`.
- `UX2-STORYCHECK-001` is implemented/source-gated: Story Check runs only through `runStoryCheckForSelectedSource` after `selectedStoryCheckSourceId` and selected owner-authored source metadata are present, and the result surface labels output as diagnostic-only, analysis-only, non-canon, confidence-not-truth, and unable to become approved memory automatically.
- `UX2-NOPROSE-001` is implemented as browser-visible refusal/fail-closed evidence: `NoProseRefusal` displays the analysis-only no-prose boundary, confirms no arbitrary prompt route is available, and visibly refuses rewrite, continue, outline, draft, polish, improve, expand, imitate, and generate prose intents without exposing executable prose-production controls.
- Focused T005 test: `.venv-unsloth-clean/bin/python -m pytest tests/test_phase8_ux002_mvp_ui_acceptance_expected_red.py -q -k "ux2_storycheck_001 or ux2_noprose_001"` -> `2 passed, 5 deselected in 0.03s`.
- Source regression: `.venv-unsloth-clean/bin/python -m pytest tests/test_phase8_ux002_mvp_ui_acceptance_expected_red.py -q -k ux2_source_001` -> `1 passed, 6 deselected in 0.03s`.
- Full expected-red file after T005: `.venv-unsloth-clean/bin/python -m pytest tests/test_phase8_ux002_mvp_ui_acceptance_expected_red.py -q` -> `3 passed, 4 failed`; remaining expected-red surfaces are limited to `UX2-NOTES-MATERIALS-001`, `UX2-RAW-ARTIFACT-001`, `UX2-REVIEW-PROMOTION-001`, and `UX2-ANALYSIS-RUNTIME-001`.
- T006 is next for Notes/Materials plus runtime/review evidence UI.
- Owner acceptance remains pending; MVP is not complete. External SaaS investigation remains post-MVP/deferred. No generated prose/prose-production behavior, backend route/API changes, package changes, context artifact updates, crawlers/raw captures, model calls, canon/memory mutation, apply-promotion shortcut, staging, commit, or push occurred.

## T006A Notes/Materials Evidence UI Implementation

- Status: `PHASE8-UX-002-T006A` complete/PASS for `UX2-NOTES-MATERIALS-001` only.
- Implementation files touched: `frontend/src/App.jsx`, `frontend/src/api.js`, `frontend/src/components/ProjectNav.jsx`, and `frontend/src/components/Editor.jsx`.
- `UX2-NOTES-MATERIALS-001` is implemented/project-scoped: the browser can create an owner-authored note, create an owner-provided material, save each body, reload project-scoped notes/materials after save, and see save/reload proof in the editor.
- Frontend helper evidence uses existing routes only: `createOwnerAuthoredNote`, `createOwnerProvidedMaterial`, and `reloadProjectScopedNotesMaterials`.
- Focused Notes/Materials test: `.venv-unsloth-clean/bin/python -m pytest tests/test_phase8_ux002_mvp_ui_acceptance_expected_red.py -q -k ux2_notes_materials_001` -> `1 passed, 6 deselected in 0.03s`.
- Notes/materials remain owner-authored or owner-provided, project-scoped, not canon by default, and notes/materials do not mutate memory or canon.
- Full `PHASE8-UX-002-T006` remains in progress. T006B is next for `UX2-RAW-ARTIFACT-001`, `UX2-REVIEW-PROMOTION-001`, and `UX2-ANALYSIS-RUNTIME-001`.
- Owner acceptance remains pending; MVP is not complete. External SaaS investigation remains post-MVP/deferred. No backend route/API changes, package changes, tests changes, context artifact updates, crawlers/raw captures, model calls, generated prose, canon/memory mutation, apply-promotion shortcut, staging, commit, or push occurred.

## T006B Raw Artifact / Analysis Runtime Evidence UI Implementation

- Status: `PHASE8-UX-002-T006B` complete/PASS for `UX2-RAW-ARTIFACT-001` and `UX2-ANALYSIS-RUNTIME-001` only.
- Implementation files touched: `frontend/src/App.jsx`, `frontend/src/api.js`, and `frontend/src/components/AnalysisSidebar.jsx`.
- `UX2-RAW-ARTIFACT-001` is implemented/status-only: `fetchRawArtifactEvidenceStatus` returns read-only support-data boundary evidence, the UI labels runtime extraction unavailable, and raw artifact inspection is shown as non-canon and non-mutating.
- `UX2-ANALYSIS-RUNTIME-001` is implemented/label-only: NCP, Subtxt, and dramatica-flow are shown as `NOT_EXPOSED`; NCP remains structured context interchange only, Subtxt remains rubric/diagnostic guidance only, dramatica-flow remains audited allowlist only, and no runtime execution path is exposed.
- Focused T006B test: `.venv-unsloth-clean/bin/python -m pytest tests/test_phase8_ux002_mvp_ui_acceptance_expected_red.py -q -k "ux2_raw_artifact_001 or ux2_analysis_runtime_001"` -> `2 passed, 5 deselected in 0.03s`.
- Full `PHASE8-UX-002-T006` remains in progress. T006C is next for `UX2-REVIEW-PROMOTION-001`.
- Owner acceptance remains pending; MVP is not complete. External SaaS investigation remains post-MVP/deferred. No backend route/API changes, package changes, tests changes, context artifact updates, crawlers/raw captures, runtime extraction, NCP/Subtxt/dramatica-flow execution, model calls, generated prose, canon/memory mutation, apply-promotion shortcut, staging, commit, or push occurred.

## T006C Review / Promotion Evidence UI Implementation

- Status: `PHASE8-UX-002-T006C` complete/PASS for `UX2-REVIEW-PROMOTION-001`.
- Implementation files touched: `frontend/src/components/ReviewQueuePanel.jsx` and `frontend/src/components/ApplyPromotionConfirmation.jsx`.
- `UX2-REVIEW-PROMOTION-001` is implemented as review/promotion evidence UI: review queue fixture evidence states queue presence is not approval and candidate persistence is not canon; apply-promotion confirmation is explicitly owner-confirmed; promotion audit evidence remains visible; failed and rejected promotion outcomes are labeled as leaving approved memory/canon unchanged.
- Focused review/promotion test: `.venv-unsloth-clean/bin/python -m pytest tests/test_phase8_ux002_mvp_ui_acceptance_expected_red.py -q -k ux2_review_promotion_001` -> `1 passed, 6 deselected in 0.03s`.
- Full UX2 acceptance file: `.venv-unsloth-clean/bin/python -m pytest tests/test_phase8_ux002_mvp_ui_acceptance_expected_red.py -q` -> `7 passed in 0.03s`.
- `PHASE8-UX-002-T006` is complete/PASS. `PHASE8-UX-002-T007` is next for closeout plus owner acceptance harness rerun.
- Owner acceptance remains pending; MVP is not complete. External SaaS investigation remains post-MVP/deferred. No backend route/API changes, package changes, tests changes, context artifact updates, crawlers/raw captures, model calls, generated prose, approved memory/canon mutation, automatic promotion, apply-promotion shortcut, staging, commit, or push occurred.

## T007 Closeout + Owner Acceptance Harness Rerun

- Status: `PHASE8-UX-002-T007` complete/PARTIAL.
- Required validation passed: `python3 scripts/check_enrichment.py`, `python3 scripts/validate_roadmap.py`, enrichment JSON parse, full UX2 pytest (`20 passed in 0.05s`), and `npm --prefix frontend run build`.
- OMI Dashboard, Candidate Detail, Evidence Drawer, and Apply-Promotion Confirmation browser evidence scripts all passed with exit `0`.
- Apply-promotion remains guarded evidence UI only: dashboard/detail/drawer expose no enabled apply-promotion path, blocked confirmation makes no apply-promotion request, and final Memory/Canon mutation remains separately controlled by explicit owner-confirmed workflow.
- Owner acceptance harness command: `node scripts/mvp-owner-acceptance-browser-smoke.mjs`.
- Owner acceptance result: exit `0`; final automated decision `MANUAL_REVIEW_REQUIRED`; evidence under `artifacts/mvp-readiness/owner-acceptance/`.
- Remaining blockers are manual-review/not-exposed owner acceptance items, especially owner boundary review, project isolation evidence owner review, Notes/Materials save-reload proof in the harness path, runtime fail-closed review, candidate/review and apply-promotion surfaces without a queue fixture, model/no-prose checks needing selected owner-authored scene or model output, Cyber detective Story Check blocked by missing selected scene/source workflow, Cyber detective no-prose prompt/input path not exposed, and final explicit owner decision.
- No backend code changed, no unauthorized candidates were created, Memory/Canon was not mutated outside authorized harness behavior, no model/Ollama calls were added, apply-promotion was not newly enabled, no generated prose controls were added, no staging/commit/push occurred, and MVP was not declared complete.

## Known Acceptance Gaps

- Story Check diagnostic-only selected-source acceptance is implemented in T005.
- No-prose refusal/fail-closed acceptance is implemented in T005; no safe arbitrary prompt route is exposed as a prose-generation path.
- Notes/Materials create/save/reload source-contract evidence is implemented in T006A; broader owner browser acceptance remains pending.
- Runtime extraction/raw artifact unavailable/read-only evidence is implemented in T006B; broader owner browser acceptance remains pending.
- Review/apply-promotion evidence is implemented in T006C with a safe fixture, explicit owner confirmation, visible audit details, and proof that failed/rejected promotion leaves approved memory/canon unchanged.
- NCP/Subtxt/dramatica-flow `NOT_EXPOSED` analysis-runtime label evidence is implemented in T006B; runtime execution remains unexposed.

## Post-MVP / Deferred Research Docs

- `docs/roadmap/ux/PHASE8-UX-002-prepublication-reference-research-boundary.md`
- `docs/roadmap/ux/PHASE8-UX-002-prepublication-controlled-experiment-method.md`

External SaaS investigation, Dramatica/current-platform investigation, controlled external experiments, Browsertrix, Crawlee, Stagehand, Playwright against external SaaS, and authorized non-black-box external reference collection are post-MVP/deferred unless the owner explicitly opens a separate post-MVP research task.

`PHASE8-UX-002-T002A` is post-MVP/deferred only and is not part of the active MVP child sequence.

## Disallowed Raw Capture Areas

- `.external_sources/**`
- raw screenshots
- traces
- HAR/WARC/WACZ
- auth state
- browser profiles
- crawler scripts
- generated capture outputs
- Browsertrix outputs
- Crawlee outputs
- Stagehand outputs
- Playwright outputs against external SaaS
- raw copied external platform content

Raw captures remain forbidden from Git. T001 created no raw capture output and no `.external_sources` directory.

## Boundary Inventory

- No frontend/backend/tests/package changes in T001.
- No crawler scripts or external SaaS runs.
- No raw captures.
- No context bundle.
- No `.external_sources` creation.
- No model/Ollama calls.
- No generated prose.
- No hidden algorithm claims from black-box observation.
- No copied proprietary content.
- No canon/memory mutation.
- No candidate creation.
- No apply-promotion shortcut.
- No staging, commit, or push.
