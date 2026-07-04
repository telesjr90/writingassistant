# PHASE8-UX-003-T002 Harness Route/Workflow Mapping Decision

- Result: PASS for docs/decision/planning.
- Decision record: `docs/roadmap/decisions/PHASE8-UX-003-harness-route-workflow-mapping-decision.md`.
- Target B blockers are mapped to existing OMI Dashboard, Candidate Detail, Evidence Drawer, Apply-Promotion Confirmation, their existing evidence reports, and their focused browser smoke scripts.
- Target C blockers are mapped to existing Notes/Materials project-scoped save/reload proof, analysis-runtime label/status surfaces, owner-authored source create/import/select UI, selected-source Story Check path, and no-prose refusal/fail-closed evidence UI.
- A-category blockers remain manual review only and cannot be marked PASS by automation.
- Future harness assertions must use `PASS`, `FAIL`, `BLOCKED`, `NOT_EXPOSED`, or `MANUAL_REVIEW_REQUIRED`; missing route evidence must not be fake-passed.
- Recommended next child: `PHASE8-UX-003-T003` expected-red owner-harness coverage for the mapped B/C blockers.
- Owner acceptance was not marked PASS. MVP was not marked complete. No frontend/backend/test/harness code changed, no candidates were created, Memory/Canon was not mutated, models/Ollama were not called, extraction was not run, apply-promotion was not enabled or run, no generated prose controls were added, and no staging/commit/push occurred.

# PHASE8-UX-003-T001 Owner Acceptance Harness Route/Workflow Evidence Follow-up Publication

- Result: PASS for docs/status/planning publication.
- New follow-up ID: `PHASE8-UX-003`.
- `PHASE8-UX-003` is published as the separate owner acceptance harness route/workflow evidence follow-up after `PHASE8-UX-002-T007`.
- `PHASE8-UX-003-T001` is complete/PASS as parent/task publication only.
- Next planned child: `PHASE8-UX-003-T002` - Decide harness route/workflow mapping for B/C blockers.
- The follow-up targets B-category candidate/review and apply-promotion blockers already covered by OMI PASS evidence but not wired into the owner harness, plus C-category Notes/Materials, analysis-runtime label, Cyber selected-source Story Check, and no-prose route/workflow blockers.
- A-category blockers remain owner manual review only.
- Owner acceptance was not marked PASS.
- MVP was not marked complete.
- No frontend code, backend code, tests, browser harness scripts, candidates, Memory/Canon mutation, model/Ollama calls, extraction, apply-promotion execution, generated prose controls, staging, commit, or push occurred.

# PHASE8-UX-002-T007 Closeout + Owner Acceptance Harness Rerun

- Result: PARTIAL for owner acceptance closeout; PASS for required roadmap/source/build/OMI evidence validation.
- `PHASE8-UX-002-T007` reran the latest committed UI evidence and owner acceptance harness on 2026-07-04.
- Required OMI browser evidence surfaces are complete/PASS:
  - OMI Dashboard: `node scripts/omi-dashboard-browser-smoke.mjs` -> exit `0`; report `docs/roadmap/validation/omi_dashboard_browser_evidence.md`.
  - OMI Candidate Detail: `node scripts/omi-candidate-detail-browser-smoke.mjs` -> exit `0`; report `docs/roadmap/validation/omi_candidate_detail_browser_evidence.md`.
  - OMI Evidence Drawer: `node scripts/omi-evidence-drawer-browser-smoke.mjs` -> exit `0`; report `docs/roadmap/validation/omi_evidence_drawer_browser_evidence.md`.
  - OMI Apply-Promotion Confirmation: `node scripts/omi-apply-promotion-browser-smoke.mjs` -> exit `0`; report `docs/roadmap/validation/omi_apply_promotion_browser_evidence.md`.
- Apply-promotion evidence remains guarded UI only in the rerun: dashboard/detail/drawer do not expose enabled apply-promotion; confirmation is blocked when blockers are visible; no apply-promotion request was made; final Memory/Canon mutation remains separately controlled by explicit owner-confirmed workflow.
- No generated prose controls were added by the OMI evidence reruns or owner acceptance rerun.
- Owner acceptance harness command: `node scripts/mvp-owner-acceptance-browser-smoke.mjs`.
- Owner acceptance harness result: exit `0`; final automated decision `MANUAL_REVIEW_REQUIRED`; report `artifacts/mvp-readiness/owner-acceptance/evidence-report.md`; checklist `artifacts/mvp-readiness/owner-acceptance/checklist-results.json`; workflow log `artifacts/mvp-readiness/owner-acceptance/workflow-log.json`.
- Owner acceptance gate classification: `docs/roadmap/decisions/PHASE8-UX-002-T007-owner-acceptance-gate-decision.md` classifies remaining blockers as A owner manual review only, B OMI evidence already PASS but not wired into owner harness, or C owner harness route/workflow update. No required blocker is classified as needing new product UI at this gate, and no required blocker is newly deferred post-MVP.
- Owner acceptance manual-review blockers remain exactly as recorded by the harness: owner boundary understanding review; prior Playwright evidence owner review; Notes and Materials save/reload isolation proof not exposed through this harness path; runtime unavailable/failure fail-closed owner review; candidate/review surface `NOT_EXPOSED`; apply-promotion fixture not visible without a review queue entry; model-assisted confidence/output/no-prose boundary review requiring model output or selected owner-authored scene; NCP/Subtxt/dramatica-flow UI/runtime labels `NOT_EXPOSED`; no-prose negative-path checks requiring selected-scene fixture; Cyber detective Story Check blocked because the created project has no scenes and no browser-visible create/import owner-authored scene/source control in that harness path; Cyber detective no-prose prompt/input path not exposed; final owner Accepted/Blocked decision still manual.
- Harness-created Cyber detective project/candidate-planning evidence is authorized harness behavior only. The harness records OMI/setup material as candidate/planning only, Memory/Canon non-canon status PASS, no direct BookNLP/spaCy/NCP/Subtxt/dramatica-flow execution, no generated story prose from the fixture, and no approved Memory/Canon mutation.
- Validation results:
  - `python3 scripts/check_enrichment.py` -> PASS.
  - `python3 scripts/validate_roadmap.py` -> PASS.
  - `python3 -m json.tool docs/roadmap/enrichment/PHASE8-UX-002.enrichment.json >/dev/null` -> PASS.
  - `.venv-unsloth-clean/bin/python -m pytest tests/test_phase8_ux002_mvp_ui_acceptance_expected_red.py -q` -> `20 passed in 0.05s`.
  - `npm --prefix frontend run build` -> PASS; Vite large chunk warning only.
  - OMI browser evidence commands listed above -> PASS.
- `PHASE8-UX-002` remains complete/PARTIAL for T007 closeout evidence, but MVP owner acceptance cannot be marked PASS and MVP is not complete.
- Next explicit owner/roadmap gate: owner review of `artifacts/mvp-readiness/owner-acceptance/evidence-report.md`, the manual acceptance checklist, and `docs/roadmap/decisions/PHASE8-UX-002-T007-owner-acceptance-gate-decision.md`; then an explicit owner Accepted/Blocked decision or a separately published follow-up task for owner harness route/workflow coverage.

# OMI Dashboard Browser Evidence

- Result: PASS for focused OMI Dashboard browser-visible evidence.
- Script: `node scripts/omi-dashboard-browser-smoke.mjs` -> exit `0`.
- Browser evidence report: `docs/roadmap/validation/omi_dashboard_browser_evidence.md`.
- Workflow log: `docs/roadmap/validation/omi-dashboard-browser-evidence/workflow-log.json`.
- Desktop screenshot: `docs/roadmap/validation/omi-dashboard-browser-evidence/screenshots/01-desktop-omi-dashboard.png`.
- Mobile screenshot: `docs/roadmap/validation/omi-dashboard-browser-evidence/screenshots/02-mobile-omi-dashboard.png`.
- Evidence mode: Vite started locally; backend proxy at `127.0.0.1:8000` was unavailable, so the smoke used its read-only zero-state Playwright API fixture and blocked mutating API methods.
- Assertions passed for dashboard reachability, active project/project-local label, OMI boundary banner, candidate/canon status strip, dense workflow rows, separated Approved Memory/Canon snapshot, disabled Apply to Memory/Canon, visible disabled reason, `aria-describedby` association, no generated prose controls, no candidate creation, no Memory/Canon mutation, and mobile stacked workflow rows.
- No backend code changed, no candidates were created, Memory/Canon was not mutated, no model/Ollama calls were made, apply-promotion was not run or enabled, and no generated prose controls were added.
- OMI Dashboard evidence is ready to commit with the current frontend slice; owner acceptance remains pending and MVP is not complete.

# PHASE8-UX-002-T006C Review / Promotion Evidence UI Validation

- Result: PASS for focused T006C source validation before roadmap closeout.
- Focused review/promotion test: `.venv-unsloth-clean/bin/python -m pytest tests/test_phase8_ux002_mvp_ui_acceptance_expected_red.py -q -k ux2_review_promotion_001` -> `1 passed, 6 deselected in 0.03s`.
- Full UX2 expected-red acceptance file: `.venv-unsloth-clean/bin/python -m pytest tests/test_phase8_ux002_mvp_ui_acceptance_expected_red.py -q` -> `7 passed in 0.03s`.
- `PHASE8-UX-002-T006` is complete/PASS. `PHASE8-UX-002-T007` is now complete/PARTIAL for closeout plus owner acceptance harness rerun; owner acceptance remains `MANUAL_REVIEW_REQUIRED`.
- Owner acceptance remains pending and MVP is not complete.

# PHASE8-UX-002-T006B Raw Artifact / Analysis Runtime Status UI

- Result: PASS for T006B implementation and focused validation.
- `PHASE8-UX-002-T006B` implemented only `UX2-RAW-ARTIFACT-001` and `UX2-ANALYSIS-RUNTIME-001` as frontend status/evidence UI.
- Focused raw artifact / analysis runtime test passes: `.venv-unsloth-clean/bin/python -m pytest tests/test_phase8_ux002_mvp_ui_acceptance_expected_red.py -q -k "ux2_raw_artifact_001 or ux2_analysis_runtime_001"` -> `2 passed, 5 deselected in 0.03s`.
- Raw artifact UI evidence labels runtime extraction unavailable, read-only raw artifact evidence, raw artifacts as support data only, raw artifacts as not canon, and raw artifact inspection as non-mutating for memory/canon.
- Analysis runtime UI evidence labels NCP, Subtxt, and dramatica-flow as `NOT_EXPOSED`; NCP is structured context interchange only, Subtxt is rubric/diagnostic guidance only, dramatica-flow is audited allowlist only, and no runtime execution path is exposed.
- Prior `UX2-SOURCE-001`, `UX2-STORYCHECK-001`, `UX2-NOPROSE-001`, and `UX2-NOTES-MATERIALS-001` surfaces remain expected to pass.
- Full `PHASE8-UX-002-T006` remains in progress. T006C is next for `UX2-REVIEW-PROMOTION-001`.
- Owner acceptance remains pending. MVP is not complete. External SaaS investigation remains post-MVP/deferred.
- No backend route/API changes, package changes, tests changes, crawler/raw capture output, `.external_sources`, context artifact changes, runtime extraction, NCP/Subtxt/dramatica-flow execution, model calls, generated prose, canon/memory mutation, apply-promotion shortcut, staging, commit, or push occurred.

# PHASE8-UX-002-T006A Notes/Materials Evidence UI

- Result: PASS for T006A implementation and validation.
- `PHASE8-UX-002-T006A` implemented only `UX2-NOTES-MATERIALS-001` as frontend Notes/Materials project-scoped evidence UI.
- Focused Notes/Materials test passes: `.venv-unsloth-clean/bin/python -m pytest tests/test_phase8_ux002_mvp_ui_acceptance_expected_red.py -q -k ux2_notes_materials_001` -> `1 passed, 6 deselected in 0.03s`.
- Implementation uses existing notes/materials frontend APIs and routes through `createOwnerAuthoredNote`, `createOwnerProvidedMaterial`, and `reloadProjectScopedNotesMaterials`.
- Notes are labeled owner-authored notes; materials are labeled owner-provided materials; both remain project-scoped, not canon by default, and notes/materials do not mutate memory or canon.
- Full `PHASE8-UX-002-T006` remains in progress. T006B is next for the remaining `UX2-RAW-ARTIFACT-001`, `UX2-REVIEW-PROMOTION-001`, and `UX2-ANALYSIS-RUNTIME-001` surfaces.
- Owner acceptance remains pending. MVP is not complete. External SaaS investigation remains post-MVP/deferred.
- No backend route/API changes, package changes, tests changes, crawler/raw capture output, `.external_sources`, context artifact changes, model calls, generated prose, canon/memory mutation, apply-promotion shortcut, staging, commit, or push occurred.

# PHASE8-UX-002-T005 Story Check Diagnostic-Only / No-Prose Evidence UI

- Result: PASS for T005 implementation and validation.
- `PHASE8-UX-002-T005` implemented frontend-only Story Check diagnostic-only/no-prose evidence UI.
- `UX2-STORYCHECK-001` and `UX2-NOPROSE-001` focused tests pass: `.venv-unsloth-clean/bin/python -m pytest tests/test_phase8_ux002_mvp_ui_acceptance_expected_red.py -q -k "ux2_storycheck_001 or ux2_noprose_001"` -> `2 passed, 5 deselected in 0.03s`.
- `UX2-SOURCE-001` regression remains passing: `.venv-unsloth-clean/bin/python -m pytest tests/test_phase8_ux002_mvp_ui_acceptance_expected_red.py -q -k ux2_source_001` -> `1 passed, 6 deselected in 0.03s`.
- Full expected-red file after T005: `3 passed, 4 failed`; remaining failures are expected for `UX2-NOTES-MATERIALS-001`, `UX2-RAW-ARTIFACT-001`, `UX2-REVIEW-PROMOTION-001`, and `UX2-ANALYSIS-RUNTIME-001`.
- `PHASE8-UX-002-T006` is next for Notes/Materials plus runtime/review evidence UI.
- Owner acceptance remains pending. MVP is not complete. External SaaS investigation remains post-MVP/deferred.
- No backend route/API changes, package changes, crawler/raw capture output, `.external_sources`, context artifact changes, model calls, generated prose, canon/memory mutation, apply-promotion shortcut, staging, commit, or push occurred.

# PHASE8-UX-002-T004 Owner-Authored Source UI

- Result: PASS for T004 implementation and validation.
- `PHASE8-UX-002-T004` implemented the browser-visible owner-authored source/scene create/import/select UI using existing project-scoped scene save/list behavior.
- `UX2-SOURCE-001` focused test passes: `.venv-unsloth-clean/bin/python -m pytest tests/test_phase8_ux002_mvp_ui_acceptance_expected_red.py -q -k ux2_source_001` -> `1 passed, 6 deselected in 0.03s`.
- Full expected-red file after T004: `1 passed, 6 failed`; remaining failures are expected for `UX2-STORYCHECK-001`, `UX2-NOPROSE-001`, `UX2-NOTES-MATERIALS-001`, `UX2-RAW-ARTIFACT-001`, `UX2-REVIEW-PROMOTION-001`, and `UX2-ANALYSIS-RUNTIME-001`.
- `PHASE8-UX-002-T005` is next for Story Check diagnostic-only/no-prose evidence UI.
- Owner acceptance remains pending. MVP is not complete. External SaaS investigation remains post-MVP/deferred.
- No backend route/API changes, package changes, crawler/raw capture output, `.external_sources`, context artifact changes, model calls, generated prose, canon/memory mutation, apply-promotion shortcut, staging, commit, or push occurred.

# PHASE8-UX-002-T003 Expected-Red UI Contract Tests

- `PHASE8-UX-002` remains active as the MVP-first UX parent.
- `PHASE8-UX-002-T003` is complete/PASS as tests-first expected-red only.
- Expected-red test file: `tests/test_phase8_ux002_mvp_ui_acceptance_expected_red.py`.
- Targeted expected-red command: `.venv-unsloth-clean/bin/python -m pytest tests/test_phase8_ux002_mvp_ui_acceptance_expected_red.py -q`.
- Expected-red result: `7 failed in 0.12s`; pytest reached collection and execution, and all failures are intended assertion failures for missing PHASE8-UX-002 UX2 UI contract markers.
- System Python note: `python3 -m pytest tests/test_phase8_ux002_mvp_ui_acceptance_expected_red.py -q` remains unavailable because `/usr/bin/python3` has no `pytest` module, but this is not a T003 blocker because the repo virtualenv is the validated test interpreter.
- Intended failures: `UX2-SOURCE-001`, `UX2-STORYCHECK-001`, `UX2-NOPROSE-001`, `UX2-NOTES-MATERIALS-001`, `UX2-RAW-ARTIFACT-001`, `UX2-REVIEW-PROMOTION-001`, and `UX2-ANALYSIS-RUNTIME-001` fail because the corresponding source/create-select, selected-source Story Check, no-prose refusal, notes/materials, raw artifact, review/promotion, and analysis runtime label markers are missing.
- `PHASE8-UX-002-T004` remains next for owner-authored source/scene create/import/select UI.
- Owner acceptance remains pending. MVP is not complete.
- External SaaS investigation remains post-MVP/deferred.
- No frontend/backend implementation, route/API change, package change, crawler script, raw capture, `.external_sources` creation, context tool run, model call, generated prose, copied proprietary content, canon/memory mutation, candidate creation, apply-promotion shortcut, staging, commit, or push occurred in T003.

# PHASE8-UX-002-T002 UI Acceptance Matrix + Route/Workflow Decision

- `PHASE8-UX-002` remains active: MVP acceptance UI completion and route wiring.
- `PHASE8-UX-002-T002` is complete/PASS as docs/decision/planning only.
- Decision record: `docs/roadmap/decisions/PHASE8-UX-002-ui-acceptance-matrix-route-workflow-decision.md`.
- Acceptance matrix: `docs/roadmap/ux/PHASE8-UX-002-ui-acceptance-matrix.md`.
- T003 is next for expected-red tests covering source/scene create/import/select, Story Check disabled/result states, no-prose refusal/fail-closed paths, Notes/Materials save/reload proof, runtime/raw artifact unavailable/read-only evidence, review/apply-promotion confirmation/audit evidence, and NCP/Subtxt/dramatica-flow exposure decision behavior.
- Owner acceptance remains pending and MVP is not complete.
- External SaaS investigation remains post-MVP/deferred. No product implementation occurred. Generated prose/prose-production remains permanently forbidden.

# PHASE8-UX-002-T001-MASTER-PLAN-ALIGNMENT Master Plan Alignment

### Result

- Result: PASS for docs/status/planning alignment.
- Scope: master plan and roadmap/status governance only; no product implementation.
- Updated `docs/master_plan.md` so it records `PHASE8-UX-002 - MVP acceptance UI completion and route wiring` as the active MVP-first UX parent after `PHASE8-IMPL-022`.
- Recorded that `PHASE8-UX-002-T001` is complete/PASS as docs/status/planning parent publication only.
- Recorded that latest owner acceptance evidence reached `SCRIPT_EXIT=0`, final automated decision remains `MANUAL_REVIEW_REQUIRED`, owner acceptance remains pending, and MVP is not complete.
- Recorded the seven MVP UI/workflow gaps: owner-authored source workflow, selected-source Story Check diagnostic-only UI, no-prose refusal/fail-closed UI, Notes/Materials save-reload proof, runtime/raw artifact evidence UI, review/apply-promotion evidence UI, and NCP/Subtxt/dramatica-flow exposure decision.
- Recorded active children `PHASE8-UX-002-T001` through `PHASE8-UX-002-T007`; `PHASE8-UX-002-T002A` remains post-MVP/deferred only.
- Recorded that external SaaS investigation, Dramatica/current-platform investigation, Browsertrix, Crawlee, Stagehand, Playwright against external SaaS, controlled external experiments, and authorized non-black-box external reference collection are post-MVP/deferred unless separately opened by the owner.
- Updated status breadcrumbs in `docs/roadmap/implementation_status.md` and `docs/roadmap/open_questions.md` to remove stale unpublished/active-parent-none wording.

### Boundary Summary

- No frontend/backend/tests/package changes.
- No crawler scripts, raw captures, `.external_sources`, context artifacts, model/Ollama calls, generated prose, copied proprietary content, canon/memory mutation, candidate creation, apply-promotion shortcut, training/JSONL/dataset/model artifacts, staging, commit, or push.

# PHASE8-UX-002-PRE-T001-DEFER-SAAS External SaaS Investigation Deferral

### Result

- Result: PASS for docs/status/planning update.
- Scope: prepublication UX/reference research deferral only; no `PHASE8-UX-002` task, inventory, enrichment, implementation, crawler, or raw capture output created.
- Updated boundary doc: `docs/roadmap/ux/PHASE8-UX-002-prepublication-reference-research-boundary.md` to record the SaaS deferral status section.
- Updated controlled-experiment method doc: `docs/roadmap/ux/PHASE8-UX-002-prepublication-controlled-experiment-method.md` to record that controlled external experiments are deferred post-MVP.
- Updated cross-reference in: `docs/roadmap/ux/PHASE8-UX-001-master-plan-ux-navigation-proposal.md`.
- Updated roadmap governance breadcrumbs: `docs/roadmap/implementation_status.md`, `docs/roadmap/decision_log.md`, `docs/roadmap/risk_register.md`, `docs/roadmap/open_questions.md`.
- External SaaS investigation, Playwright against external SaaS, Browsertrix, Crawlee, Stagehand, external crawling, screenshots/traces/HAR/WACZ, and raw capture workflows are deferred until after MVP UI fixes and MVP owner acceptance.
- The previous `T002A` external SaaS UI reference research spike is reclassified as post-MVP / deferred, not an active `PHASE8-UX-002` child in the MVP path.
- The active `PHASE8-UX-002` parent must prioritize building our own missing UI surfaces: owner-authored scene/source create/import/select UI, Story Check against selected owner-authored source, no-prose refusal/fail-closed UI, Notes/Materials save-reload project-scoped proof, runtime/raw artifact UI evidence, review/apply-promotion UI evidence, and NCP/Subtxt/dramatica-flow exposure decision.
- `PHASE8-UX-002-T001` (parent publication) is the next UX work. The first recommended UX child after `T001` is the MVP UI acceptance matrix and missing UI route/workflow fixes.
- Controlled external experiments and authorized non-black-box external reference collection are deferred post-MVP unless the owner explicitly opens a separate post-MVP research task.
- The distinction remains: lawful non-black-box evidence may establish information, but black-box observation alone cannot prove hidden algorithms or implementation details.
- Raw capture prohibitions remain in force. `.external_sources/dramatica-ui-reference/` was not created.
- Owner acceptance remains pending and MVP is not complete.
- No product implementation has started.

### Boundary Summary

- No frontend/backend/tests/package changes.
- No crawler scripts, crawler runs, external SaaS Playwright runs, Browsertrix, Crawlee, Stagehand, model/Ollama calls, or `.external_sources` creation.
- No raw captures or `auth state`, browser profiles, HAR/WARC/WACZ, traces, or screenshots committed.
- No canon/memory mutation, no apply-promotion shortcut, no model calls, no generated prose, no training/JSONL/dataset work.

# PHASE8-UX-002-PRE-T001-BLACKBOX Controlled-Experiment Method Addendum

### Result

- Result: PASS for docs/status/planning update.
- Scope: prepublication UX/reference research boundary only; no `PHASE8-UX-002` task, inventory, enrichment, implementation, crawler, or raw capture output created.
- Created standalone method doc: `docs/roadmap/ux/PHASE8-UX-002-prepublication-controlled-experiment-method.md`.
- Updated boundary doc: `docs/roadmap/ux/PHASE8-UX-002-prepublication-reference-research-boundary.md`.
- Controlled experiments belong to proposed future `PHASE8-UX-002-T002A` after `T001` parent publication and `T002` acceptance matrix framing.
- `PHASE8-UX-002` should still start with `PHASE8-UX-002-T001` parent publication after review.
- Owner acceptance remains pending; MVP is not complete.
- No product implementation has started.
- Raw captures remain forbidden from Git; `.external_sources/dramatica-ui-reference/` is only a proposed untracked raw-output location and was not created.
- Inferred dependency graphs are hypothesis maps, not roadmap truth, product architecture, canon, or product requirements.

### Boundary Summary

- No frontend/backend/tests/package changes.
- No crawler scripts, crawler runs, external SaaS Playwright runs, Browsertrix, Crawlee, Stagehand, model/Ollama calls, or `.external_sources` creation.
- Controlled experiment observations must be labeled `observed`, `inferred`, or `unknown`.
- Hidden algorithms, prompts, model weights, model routing, ranking logic, and proprietary implementation details can be known only through explicit authorized disclosure, official documentation, owner-provided evidence, or other lawful non-black-box evidence; they must not be claimed as known from black-box observations alone.
- `PHASE8-UX` may retrieve authorized official documentation, owner-provided evidence, authorized disclosures, and other lawful non-black-box reference materials after that collection is explicitly scoped; the information still needs to be collected, summarized, provenance-labeled, and reviewed before use as UX/reference input.
- Captured output must not be used for training or fine-tuning.

# PHASE8-UX-002-PRE-T001 Reference Research Boundary

### Result

- Result: PASS for docs/status/planning update.
- Scope: prepublication UX/reference research boundary only; no `PHASE8-UX-002` task, inventory, enrichment, implementation, crawler, or raw capture output created.
- Created boundary doc: `docs/roadmap/ux/PHASE8-UX-002-prepublication-reference-research-boundary.md`.
- Updated UX/reference planning docs and roadmap governance breadcrumbs.
- Owner acceptance evidence remains `MANUAL_REVIEW_REQUIRED`; MVP is not complete.
- `PHASE8-UX-002` should still start with `PHASE8-UX-002-T001` parent publication after review.
- Proposed research spike: `PHASE8-UX-002-T002A` External SaaS UI reference research spike, proposed only and not executed.

### Boundary Summary

- No product implementation started.
- No frontend/backend/tests/package changes.
- No crawler scripts, crawler runs, Playwright external SaaS runs, Browsertrix, Crawlee, Stagehand, model/Ollama calls, or `.external_sources` creation.
- Raw captures remain forbidden from Git; `.external_sources/dramatica-ui-reference/` is only a proposed untracked raw-output location.

# MVP-READINESS-OWNER-ACCEPTANCE-005 Safe Cyber Detective Story Check and No-Prose Boundary Fixture

### Result

- Result: PASS for harness/source/docs update; browser acceptance script not run by Codex.
- Scope: owner acceptance readiness harness and documentation only; no product behavior changes.
- Updated script: `scripts/mvp-owner-acceptance-browser-smoke.mjs`.
- Updated source tests: `tests/test_mvp_owner_acceptance_browser_smoke_source.py`.
- Updated validation/governance docs.
- Story Check diagnosis: the app exposes a visible `Run Story Check` control, but the Cyber detective fixture project is created from OMI-guided setup text and has no browser-visible create/import owner-authored scene/source workflow. The harness only submits Story Check if a selected scene visibly contains the owner-authored fixture text; otherwise it records `MANUAL_REVIEW_REQUIRED` with missing-surface evidence.
- No-prose negative-path diagnosis: no safe browser-visible analysis-only prompt/input route is exposed for rewrite, continuation, outline, draft, polish, improve, expand, or imitation prompts. The harness records `MANUAL_REVIEW_REQUIRED` and does not submit unsafe prompts.
- Added checklist IDs for safe source selection, Story Check submission/result/no-prose output, and no-prose negative refusals.
- Added screenshots for Cyber fixture source/scene selection, Story Check before submit, Story Check result/error when run, and no-prose negative prompt attempt/result.
- Generated story-prose markers cause `FAIL`; missing safe UI remains `MANUAL_REVIEW_REQUIRED` instead of fake `PASS`.

### Boundary Summary

- No frontend/backend product behavior changes.
- No generated prose, continuation, rewrite, outline, draft, polish, improvement, expansion, imitation, or story-prose path.
- No direct `/api/chat` or generation endpoint calls.
- No BookNLP/spaCy, NCP/Subtxt/dramatica-flow, apply-promotion, approved memory/canon mutation, training/JSONL/dataset/model artifacts, staging, commit, or push.
- MVP readiness decision remains **MANUAL_REVIEW_REQUIRED** until owner run/review resolves remaining manual items; this does not mark MVP complete.

# MVP-READINESS-OWNER-ACCEPTANCE-004 Cyber Detective Owner Fixture Automation

### Result

- Result: PASS for harness/source/docs update; browser acceptance script not run by Codex.
- Scope: owner acceptance readiness harness and documentation only; no product behavior changes.
- Updated script: `scripts/mvp-owner-acceptance-browser-smoke.mjs`.
- Updated source tests: `tests/test_mvp_owner_acceptance_browser_smoke_source.py`.
- Updated validation docs: `docs/roadmap/validation/mvp_owner_acceptance_browser_evidence.md` and `docs/roadmap/validation/mvp_owner_manual_acceptance_checklist.md`.
- Added default fixture support with `MVP_ACCEPTANCE_FIXTURE=cyber-detective`.
- The fixture title is `Cyber detective`; it is owner-authored MVP acceptance source material with mature/violent content warning metadata for internal evidence only.
- The harness creates `Cyber detective MVP Acceptance <timestamp>` through the browser UI, fills OMI-guided setup fields with the owner-authored fixture, reviews before create, records source visibility, creates the project, and verifies active project scoping.
- OMI/setup fixture material remains candidate/planning only; Memory/Canon remains approved-only and must not display the fixture as approved canon.
- Story Check and no-prose checks record `PASS`, `BLOCKED`, `MANUAL_REVIEW_REQUIRED`, or `NOT_EXPOSED` based on safe browser exposure. Missing safe Cyber detective source/input paths are not fake-passed.
- The harness does not run the live acceptance script in this task; owner must run it with backend/frontend and Ollama available if model-backed evidence is desired.

### Boundary Summary

- Cyber detective is used only as owner-authored analysis/testing fixture material.
- No generated prose, continuation, rewrite, outline, draft, polish, improvement, expansion, imitation, or story-prose path was added.
- No direct `/api/chat` or direct generation endpoint calls were added.
- No BookNLP/spaCy execution and no NCP/Subtxt/dramatica-flow execution.
- No automatic memory/canon mutation, no apply-promotion shortcut, no training/JSONL/dataset/model artifacts, no staging, commit, or push.
- MVP readiness decision remains **MANUAL_REVIEW_REQUIRED** until owner runs and reviews evidence; this does not mark MVP complete.

# MVP-READINESS-OWNER-ACCEPTANCE-003 WSL-to-Windows Ollama Host Fallback

### Result

- Result: PASS for harness/source/docs update; browser acceptance script not run by Codex.
- Scope: owner acceptance readiness harness and documentation only; no product behavior changes.
- Updated script: `scripts/mvp-owner-acceptance-browser-smoke.mjs`.
- Updated source tests: `tests/test_mvp_owner_acceptance_browser_smoke_source.py`.
- Updated validation docs: `docs/roadmap/validation/mvp_owner_acceptance_browser_evidence.md` and `docs/roadmap/validation/mvp_owner_manual_acceptance_checklist.md`.
- The harness now tries Ollama readiness candidates in order: `OLLAMA_BASE_URL`, `OLLAMA_HOST`, `http://localhost:11434`, and detected WSL Windows-host fallback.
- WSL/Ubuntu running the backend or test may not reach Windows-hosted Ollama at `localhost`; use the Windows host IP from the WSL default gateway.
- Recommended WSL test command:

```bash
WINDOWS_HOST=$(ip route show | grep -i default | awk '{ print $3 }')
export OLLAMA_HOST="http://$WINDOWS_HOST:11434"
curl "$OLLAMA_HOST/api/version"
```

- Backend inspection found Story Check reads `OLLAMA_BASE_URL`, not `OLLAMA_HOST`; if backend runs in WSL and Ollama runs on Windows, start backend with:

```bash
WINDOWS_HOST=$(ip route show | grep -i default | awk '{ print $3 }')
export OLLAMA_BASE_URL="http://$WINDOWS_HOST:11434"
PY=".venv-unsloth-clean/bin/python"
"$PY" -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### Boundary Summary

- Ollama checks remain readiness-only `/api/version` and `/api/tags`.
- No `/api/chat` or generation endpoint calls were added to the harness.
- No frontend/backend product logic, package/dependency files, generated prose, BookNLP/spaCy, NCP/Subtxt/dramatica-flow, canon/memory mutation, apply-promotion, staging, commit, or push.
- MVP readiness decision remains **MANUAL_REVIEW_REQUIRED** until owner runs and reviews evidence; this does not mark MVP complete.

# MVP-READINESS-OWNER-ACCEPTANCE-002 Owner Acceptance Browser Evidence Harness

### Result

- Result: PASS for harness/source/docs creation; browser acceptance script not run by Codex.
- Scope: automated owner MVP acceptance checklist evidence runner only; no product fixes.
- Created script: `scripts/mvp-owner-acceptance-browser-smoke.mjs`.
- Created source tests: `tests/test_mvp_owner_acceptance_browser_smoke_source.py`.
- Created evidence doc: `docs/roadmap/validation/mvp_owner_acceptance_browser_evidence.md`.
- Evidence output directory for owner runs: `artifacts/mvp-readiness/owner-acceptance`.
- Script output artifacts: `screenshots/*.png`, `workflow-log.json`, `checklist-results.json`, and `evidence-report.md`.
- Result model: `PASS`, `FAIL`, `BLOCKED`, `NOT_EXPOSED`, and `MANUAL_REVIEW_REQUIRED`.
- MVP owner acceptance remains pending; this task does not mark MVP complete.

### Harness Coverage

- Startup checks cover frontend navigation, backend `/api/projects`, existing project isolation script presence, and Ollama readiness through `/api/version` and `/api/tags`.
- If Ollama is unreachable, the harness records `startup_ollama_unreachable = BLOCKED`, blocks model-backed checks, and records remediation to run `ollama serve`, then retry `curl http://localhost:11434/api/version`.
- Project isolation and manual workspace checks use browser-visible project creation/switching, scoped Scenes text, and scoped Memory/Canon text.
- Runtime extraction, candidate/review, apply-promotion, model-assisted, and no-prose checks record visible evidence where available and otherwise mark `NOT_EXPOSED` or `MANUAL_REVIEW_REQUIRED`; absent surfaces are not treated as PASS.
- Final owner decision remains pending; the script may output `READY_FOR_OWNER_REVIEW`, `BLOCKED`, or `MANUAL_REVIEW_REQUIRED`, but not owner acceptance.

### Boundary Summary

- No frontend/backend product logic changes, package/dependency changes, generated prose, model creative generation calls, BookNLP/spaCy execution, NCP/Subtxt/dramatica-flow execution, automatic canon/memory mutation, apply-promotion shortcut, training artifacts, staging, commit, or push.

### Validation Owner Manual Follow-Up

- Owner should run `node scripts/mvp-owner-acceptance-browser-smoke.mjs` only after frontend/backend are running and Ollama is running if model-backed workflow review is desired.
- Review `artifacts/mvp-readiness/owner-acceptance/evidence-report.md` before making any owner MVP acceptance decision.

# MVP-READINESS-OWNER-ACCEPTANCE-001 Owner Manual Acceptance Checklist and Evidence Review

### Result

- Result: READY FOR OWNER MANUAL ACCEPTANCE TESTING.
- Scope: docs/governance checklist and evidence review only; no product changes.
- Created checklist: `docs/roadmap/validation/mvp_owner_manual_acceptance_checklist.md`.
- Project isolation blocker is repaired and live browser evidence passed.
- Evidence script: `scripts/mvp-project-isolation-browser-smoke.mjs`.
- Evidence report: `artifacts/mvp-readiness/project-isolation/evidence-report.md`.
- Workflow log: `artifacts/mvp-readiness/project-isolation/workflow-log.json`.
- Browser evidence result: PASS; `SCRIPT_EXIT=0`; blockers: none.
- Covered browser smoke path: project creation, active project switching, Scenes project isolation, and Memory/Canon project isolation.

### MVP Readiness Decision

- `PHASE8-IMPL-022` closeout plus repair evidence supports readiness for owner manual acceptance testing.
- MVP owner acceptance is still pending until the checklist is completed and explicitly owner-accepted.
- This does not mark MVP complete and does not claim final end-to-end usability acceptance.
- Fine-tuning remains deferred after MVP.
- Generated prose/prose-production remains permanently forbidden.

### Checklist Coverage

- Startup requirements: Ollama reachable if model-backed workflows are tested, backend running, frontend running, and browser evidence script available.
- Project isolation: confirmed by Playwright evidence with `SCRIPT_EXIT=0`.
- Manual workspace checks: create/select project, Overview, Scenes empty/new project behavior, Notes, Materials, Memory/Canon approved-only boundary, and OMI/setup candidate boundary.
- Runtime extraction checks: unavailable/fail-closed states, raw artifact support-data-only behavior, and no canon mutation.
- Candidate/review checks: candidate-first behavior, review queue/read-only state, and owner-action execution only.
- Apply-promotion checks: explicit owner confirmation only, audit behavior, and approved memory/canon mutation only through approved workflow.
- Model-assisted / analysis runtime checks: evidence-backed only, confidence is not truth, and NCP/Subtxt/dramatica-flow analysis-only boundaries.
- No-prose checks: no rewrite, no continuation, no outline, and no generated prose.
- Final owner decision section: Pending owner acceptance, Accepted by owner, or Blocked with reason.

### Validation Owner Manual Follow-Up

- `python3 scripts/check_enrichment.py`
- `python3 scripts/validate_roadmap.py`
- `git diff --check`
- `git status --short --branch`

# MVP-READINESS-REPAIR-001 Project Isolation Routing Repair Attempt

### Result

- Result: PASS for focused source/backend validation; browser evidence not rerun by Codex.
- Scope: project-scoped Scenes and OMI/Memory/Canon routing repair only.
- Repair summary: frontend project reload now clears stale project-scoped state on active project changes, loads scenes/notes/materials/OMI independently from optional bible/storyform context so missing optional files cannot preserve example data, and keeps the OMI-guided setup shell on the overview view so Memory/Canon approved-only copy is not co-rendered with setup candidate copy.
- Backend/source coverage added for non-example empty scenes and OMI summaries remaining project-scoped even when `example` has data.
- MVP manual readiness remains blocked until the owner reruns `scripts/mvp-project-isolation-browser-smoke.mjs` with backend and frontend running and records exit code `0`.
- No generated prose, model/Ollama calls, BookNLP/spaCy execution, NCP/Subtxt/dramatica-flow execution, automatic canon/memory mutation, apply-promotion shortcut, training artifacts, staging, commit, or push.

### Validation

- `.venv-unsloth-clean/bin/python -m pytest tests/test_frontend_project_workspace_source.py tests/test_project_creation.py tests/test_scene_routes.py tests/test_omi_routes.py tests/test_omi_boundaries.py -q` — PASS (`468 passed`, warnings only).

# MVP-READINESS-BROWSER-EVIDENCE-001-C Project Isolation Browser Evidence Record

### Result

- Result: FAIL-with-evidence / MVP manual readiness **BLOCKED**.
- Scope: docs/governance record only; no product fix attempted.
- Task: `MVP-READINESS-BROWSER-EVIDENCE-001-C` — Record browser evidence in UX/readiness docs.
- Parent evidence task: `MVP-READINESS-BROWSER-EVIDENCE-001`.
- Evidence script: `scripts/mvp-project-isolation-browser-smoke.mjs`.
- Evidence directory: `artifacts/mvp-readiness/project-isolation`.
- Browser/app/script ran; exit code `1`; workflow log records `toolingBlocked: false`.
- Treat as **FAIL-with-evidence**, not tooling blocked.

### Evidence Summary

- New project created and activated: `MVP Isolation Test 1782963719999` (`mvp-isolation-test-1782963719999`).
- Post-create header/selector/overview project id matched the new project (not `example`).
- Blockers captured:
  - `hardcoded_scene_route` — `scenes_nav_no_scene_001_leak`
  - `hardcoded_scene_route` — `new_project_scene_list_has_no_example_scene_items`
  - `omi_cross_project_data_leakage` — `omi_memory_view_no_princess_and_pea`
  - `omi_cross_project_data_leakage` — `omi_memory_view_no_scene_001`
  - `candidate_setup_not_visible` — `setup_candidate_not_labeled_approved_memory_or_canon`
- Artifacts: `evidence-report.md`, `workflow-log.json`, five screenshots under `screenshots/`.

### MVP Readiness Decision

- Owner manual readiness browser evidence reproduced project isolation/routing leakage.
- MVP manual readiness is blocked until project isolation passes.
- `PHASE8-IMPL-022` closeout remains valid as smoke-harness closeout only.
- `PHASE8-IMPL-022` closeout does not equal owner MVP acceptance.
- Full manual MVP testing should run Ollama, backend, frontend, and browser/manual checks; this evidence script did not call Ollama/model directly.
- This does not mark MVP complete and does not claim end-to-end usability has passed.
- Generated prose/prose-production remains permanently forbidden.

### Docs Updated

- `docs/roadmap/validation/mvp_manual_readiness_project_isolation_blocker.md` (created)
- `docs/roadmap/validation/latest_roadmap_validation.md`
- `docs/roadmap/ux/PHASE8-UX-001-master-plan-ux-navigation-proposal.md`
- `docs/roadmap/decision_log.md`
- `docs/roadmap/risk_register.md`
- `docs/roadmap/open_questions.md`

### Validation Owner Manual Follow-Up

- `python3 scripts/check_enrichment.py`
- `python3 scripts/validate_roadmap.py`
- `git diff --check`
- `git status --short --branch`

### Recommended Next Step

- Implement scoped project isolation fixes for scenes navigation and OMI/Memory/Canon views, then re-run `node scripts/mvp-project-isolation-browser-smoke.mjs` until exit code `0`.

# MVP-READINESS-BROWSER-TOOLING-001 Playwright Browser Evidence Tooling Install Record

### Result

- Result: PASS.
- Scope: docs/governance record only; package metadata inspection only.
- Task: `MVP-READINESS-BROWSER-TOOLING-001` — Record Playwright browser evidence tooling install.
- Prior inspection state: no root `package.json`; `frontend/package.json` existed; browser/test dependencies were none found; no Playwright/Puppeteer references.
- Owner manual install (approved): `npm install -D @playwright/test` under `frontend/`; `npx playwright install chromium`.
- Changed package files inspected: `frontend/package.json`, `frontend/package-lock.json`.

### Package / Tooling Summary

- `@playwright/test` `^1.61.1` added to `frontend/package.json` `devDependencies` only.
- `frontend/package-lock.json` records `@playwright/test`, transitive `playwright`, and `playwright-core` at `1.61.1` with `dev: true`.
- No root `package.json`; no backend package manifest; no Puppeteer references; no production/runtime dependency changes to React/Vite/TipTap/axios.
- Existing frontend npm scripts unchanged; no Playwright config file; no browser evidence script added in this task.
- Intended use: MVP readiness browser screenshots/workflow evidence tooling only — not product runtime behavior, not app test harness expansion by default, and not prose generation.

### Boundary Summary

- Owner approved Playwright as MVP readiness evidence tooling after browser automation dependencies were missing.
- This install does not mark MVP complete.
- This does not claim end-to-end usability has passed.
- This does not change product behavior; no backend app logic, frontend app logic, routes, UI, or browser evidence script was added in this task.
- Generated prose/prose-production paths remain permanently forbidden.
- Known project isolation bug remains deferred; this task does not fix it.
- No staging, commit, or push performed in this task.

### Docs Updated

- `docs/roadmap/validation/latest_roadmap_validation.md`
- `docs/roadmap/decision_log.md`
- `docs/roadmap/risk_register.md`
- `docs/roadmap/open_questions.md`

### Validation Owner Manual Follow-Up

- `python3 scripts/check_enrichment.py`
- `python3 scripts/validate_roadmap.py`
- `git diff --check`
- `git status --short --branch`

### Recommended Next Step

- Commit the owner-reviewed Playwright package install (`frontend/package.json`, `frontend/package-lock.json`) after review, then create the browser evidence script in a separately scoped task.

# PHASE8-IMPL-022-T007 Parent Closeout

### Result

- Result: PASS.
- Scope: docs/status/governance closeout only.
- Parent task: `PHASE8-IMPL-022` - End-to-end MVP usability validation.
- Parent status: complete/PASS.
- Completed children recorded: `PHASE8-IMPL-022-T001`, `PHASE8-IMPL-022-T002`, `PHASE8-IMPL-022-T003`, `PHASE8-IMPL-022-T004`, `PHASE8-IMPL-022-T005`, `PHASE8-IMPL-022-T006`, and `PHASE8-IMPL-022-T007`.
- No active child remains for `PHASE8-IMPL-022`.
- Active parent after closeout: none / pending owner roadmap decision.

### Final Artifacts

- `docs/roadmap/decisions/PHASE8-IMPL-022-mvp-usability-validation-matrix-decision.md`
- `backend/story_knowledge/mvp_usability_smoke.py`
- `tests/test_writer_assistant_core_mvp_usability_smoke_contract.py`
- `tests/test_writer_assistant_core_mvp_usability_smoke_workflow_contract.py`
- `tests/test_writer_assistant_core_mvp_usability_smoke_safety_regression.py`

### Child Summary

T001 published the parent and MVP usability validation scope. T002 created the MVP end-to-end usability validation matrix and acceptance gates decision. T003 added expected-red MVP smoke/contract tests. T004 implemented the minimal pure in-memory MVP smoke harness and made T003 green. T005 added workflow fixture and owner-action validation coverage. T006 added safety regression/no-prose/no-canon/no-training/no-silent-fallback coverage and minimal helper hardening. T007 closes the parent as docs/status/governance only.

### Final Behavior

PHASE8-IMPL-022 validates the complete MVP path through a deterministic in-memory smoke harness and tests covering project/workspace load, owner-authored or owner-provided source confirmation, source_refs, evidence_refs, provenance_refs, source_locator_refs, runtime extraction availability and guarded failure behavior, BookNLP/spaCy availability/import/run signals as scoped by earlier parents, raw artifact persistence expectations, candidate creation/review handoff expectations, review queue/read-only review surface expectations, frontend owner-action execution expectations, explicit audited apply-promotion expectation, approved memory/canon mutation only through owner-approved workflow expectation, model-assisted evidence-backed extraction expectation, analysis-only NCP/Subtxt/dramatica-flow integration expectation, unavailable/quarantine/fail_closed/fail closed behavior, no generated prose/no rewrite/no continuation/no outline/no training artifacts/no silent fallback, blocker triage, evidence packet preservation, and support-data-only evidence behavior.

### Boundary Summary

PHASE8-IMPL-022 preserved candidate-first, owner review required, evidence/provenance/source-locator backed when available, confidence is not truth, tool output is not canon, model output is not canon, no model output as truth, no automatic canon, no apply-promotion outside explicit audited owner-confirmed path, no memory/canon mutation outside owner-approved workflow, no training artifacts, no generated prose, no rewrite, no continuation, no outline, fail closed, no silent fallback, queue presence is not approval, candidate persistence is not canon, MVP is not complete unless explicitly authorized by an existing roadmap file, and end-to-end usability has not passed unless explicitly authorized by an existing roadmap file.

PHASE8-IMPL-022 added no routes, frontend code, package/dependency changes, real runtime extraction execution, BookNLP/spaCy execution, NCP/Subtxt/dramatica-flow execution, model/Ollama calls, network/subprocess behavior, runtime project file writes, candidate persistence writes, review queue writes, apply-promotion behavior changes, approved memory/canon mutation, training/JSONL/dataset/model artifacts, generated prose, or prose-production behavior.

PHASE8-IMPL-022 is complete/PASS as the end-to-end MVP usability validation parent. This closeout does not by itself declare the whole MVP complete or record an end-to-end usability pass for production use. MVP readiness/completion requires the next explicit owner/roadmap gate. Fine-tuning remains deferred after MVP. Generated prose/prose-production paths remain permanently forbidden and are not future roadmap features.

# PHASE8-IMPL-022-T005 MVP Workflow Fixture and Owner-Action Validation Coverage

### Result

- Result: PASS.
- Scope: focused workflow fixture and owner-action validation coverage only.
- Parent task: `PHASE8-IMPL-022` - End-to-end MVP usability validation.
- Parent status: active.
- Completed child recorded: `PHASE8-IMPL-022-T005` - MVP workflow fixture and owner-action validation coverage.
- Final artifacts: `backend/story_knowledge/mvp_usability_smoke.py`, `tests/test_writer_assistant_core_mvp_usability_smoke_contract.py`, and `tests/test_writer_assistant_core_mvp_usability_smoke_workflow_contract.py`.
- Active/ready next child: `PHASE8-IMPL-022-T006` - MVP usability safety regression and no-prose/no-canon boundary validation.
- Planned child: `PHASE8-IMPL-022-T007`.
- Fine-tuning remains deferred after MVP.
- Generated prose/prose-production paths remain permanently forbidden.

### Coverage Summary

T005 adds a realistic in-memory workflow fixture covering safe project_id, workspace/project load, owner-authored or owner-provided source confirmation, source_refs, evidence_refs, provenance_refs, source_locator_refs, runtime extraction, BookNLP, spaCy, raw artifact persistence, candidate review, review handoff, review queue item visible, read-only review surface, frontend owner-action execution, owner action, owner command, explicit confirmation, apply-promotion audited owner confirmation, approved memory/canon owner-approved workflow, model-assisted evidence-backed extraction, analysis-only NCP/Subtxt/dramatica-flow, unavailable, quarantine, fail_closed, fail closed, no generated prose, no rewrite, no continuation, no outline, no training artifacts, no silent fallback, end-to-end smoke, and MVP blocker triage.

Owner-action validation proves review queue item visible/read-only, owner command available, owner command requires explicit confirmation, apply-promotion requires explicit audited owner confirmation, approved memory/canon mutation is allowed only after owner-approved workflow, queue presence is not approval, candidate persistence is not canon, confidence is not truth, tool output is not canon, model output is not canon, no automatic canon, no apply-promotion outside explicit audited owner-confirmed path, and no memory/canon mutation outside owner-approved workflow. Forbidden owner-action shortcuts fail closed.

Minimal helper hardening in `backend/story_knowledge/mvp_usability_smoke.py` validates optional workflow fixture and owner-action expectation dictionaries, preserves support-data-only evidence packet fields, and classifies blockers. T005 adds no routes, frontend, package/dependency files, real runtime extraction, BookNLP/spaCy execution, NCP/Subtxt/dramatica-flow execution, model/Ollama calls, network/subprocess behavior, persistence, candidate/review queue writes, apply-promotion changes, approved memory/canon mutation, training artifacts, or generated prose.

MVP is not complete and end-to-end usability has not passed.

# PHASE8-IMPL-022-T004 Minimal MVP Smoke Harness Implementation

### Result

- Result: PASS.
- Scope: minimal pure in-memory MVP usability smoke harness implementation plus docs/status/governance alignment.
- Parent task: `PHASE8-IMPL-022` - End-to-end MVP usability validation.
- Parent status: active.
- Completed child recorded: `PHASE8-IMPL-022-T004` - Minimal MVP smoke harness implementation.
- Final artifacts: `backend/story_knowledge/mvp_usability_smoke.py` and `tests/test_writer_assistant_core_mvp_usability_smoke_contract.py`.
- Contract result: T004 turns the T003 expected-red contract green.
- Active/ready next child: `PHASE8-IMPL-022-T005` - MVP workflow fixture and owner-action validation coverage.
- Planned children: `PHASE8-IMPL-022-T006` and `PHASE8-IMPL-022-T007`.
- Fine-tuning remains deferred after MVP.
- Generated prose/prose-production paths remain permanently forbidden.

### Boundary Confirmation

T004 adds no routes, frontend, package/dependency files, real runtime extraction, BookNLP/spaCy execution, NCP/Subtxt/dramatica-flow execution, model/Ollama calls, network/subprocess behavior, persistence, candidate/review queue writes, apply-promotion changes, approved memory/canon mutation, training artifacts, or generated prose.

The helper preserves candidate-first, owner review required, evidence/provenance/source-locator refs when provided, confidence is not truth, tool output is not canon, model output is not canon, no model output as truth, no automatic canon, no apply-promotion outside explicit audited owner-confirmed path, no memory/canon mutation outside owner-approved workflow, queue presence is not approval, candidate persistence is not canon, no generated prose, no rewrite, no continuation, no outline, no training artifacts, fail closed, no silent fallback, MVP is not complete, and end-to-end usability has not passed.

# PHASE8-IMPL-022-T003 Expected-Red MVP Smoke/Contract Tests

### Result

- Result: PASS.
- Scope: tests-first expected-red contract only.
- Parent task: `PHASE8-IMPL-022` - End-to-end MVP usability validation.
- Parent status: active.
- Completed child recorded: `PHASE8-IMPL-022-T003` - Expected-red end-to-end MVP smoke/contract tests.
- Test file: `tests/test_writer_assistant_core_mvp_usability_smoke_contract.py`.
- Expected-red target: future `backend.story_knowledge.mvp_usability_smoke` module and the documented public APIs `validate_mvp_usability_smoke_matrix`, `validate_mvp_usability_smoke_request`, `build_mvp_usability_smoke_plan`, `validate_mvp_usability_smoke_result`, `build_mvp_usability_evidence_packet`, `classify_mvp_usability_blockers`, and `run_guarded_mvp_usability_smoke`.
- Active/ready next child: `PHASE8-IMPL-022-T004` - Minimal MVP smoke harness implementation.
- Planned children: `PHASE8-IMPL-022-T005`, `PHASE8-IMPL-022-T006`, and `PHASE8-IMPL-022-T007`.
- Future MVP-required parents after this active parent: none remaining; `PHASE8-IMPL-022` is the final MVP-required validation parent.
- Fine-tuning remains deferred after MVP.
- Generated prose/prose-production paths remain permanently forbidden.
- PHASE8-UX-001 remained read-only terminology/boundary reference only.
- No context tools, CCE, Graphify, Repomix, LeanCTX, AI context generation, source-cache refresh, baseline refresh, scaffold, collect-plan, context health scripts, Claude subagents, models/Ollama, runtime extraction, BookNLP/spaCy, NCP/Subtxt/dramatica-flow, or subprocess runtime workflows were run for T003.

### Files Changed

- Created: `tests/test_writer_assistant_core_mvp_usability_smoke_contract.py`
- Updated: `docs/roadmap/tasks/PHASE8-IMPL-022.md`
- Updated: `docs/roadmap/inventory/PHASE8-IMPL-022.md`
- Updated: `docs/roadmap/enrichment/PHASE8-IMPL-022.enrichment.json`
- Updated: `docs/master_plan.md`
- Updated: `docs/roadmap/implementation_status.md`
- Updated: `docs/roadmap/roadmap_index.yaml`
- Updated: `docs/roadmap/task_backlog.md`
- Updated: `docs/roadmap/phase_map.md`
- Updated: `docs/roadmap/validation/latest_roadmap_validation.md`
- Updated: `docs/roadmap/decision_log.md`
- Updated: `docs/roadmap/risk_register.md`
- Updated: `docs/roadmap/open_questions.md`

### Contract Summary

T003 adds expected-red tests for the future public APIs: `validate_mvp_usability_smoke_matrix`, `validate_mvp_usability_smoke_request`, `build_mvp_usability_smoke_plan`, `validate_mvp_usability_smoke_result`, `build_mvp_usability_evidence_packet`, `classify_mvp_usability_blockers`, and `run_guarded_mvp_usability_smoke`.

The contract requires a matrix with `matrix_key`, `matrix_version`, `matrix_intent`, `gate_ids`, `coverage_markers`, and `gate_definitions` for `workspace_project_baseline`, `owner_authored_source`, `runtime_extraction_environment`, `runtime_extraction_unavailable`, `raw_artifact_persistence`, `candidate_creation`, `review_queue_read_only`, `frontend_owner_action`, `apply_promotion_audited`, `approved_memory_canon_mutation`, `model_assisted_evidence_backed`, `analysis_only_runtime_integration`, `no_prose_no_rewrite_no_continuation_no_outline`, `no_training_artifacts`, `no_silent_fallback`, `end_to_end_smoke`, and `mvp_blocker_triage`. It requires requests with `project_id`, `smoke_key`, `smoke_intent`, `source_refs`, `evidence_refs`, `provenance_refs`, `source_locator_refs`, owner-authored or owner-provided source boundary, no generated prose, no rewrite, no continuation, no outline, no training, no canon, and no apply-promotion confirmations.

Coverage markers include `workspace/project load`, `owner-authored or owner-provided project text`, `runtime extraction`, `BookNLP`, `spaCy`, `unavailable`, `quarantine`, `fail_closed`, `raw artifact persistence`, `candidate creation`, `candidate review`, `review handoff`, `review queue`, `read-only review surface`, `frontend owner-action execution`, `apply-promotion`, `approved memory/canon`, `model-assisted evidence-backed extraction`, `analysis-only NCP/Subtxt/dramatica-flow`, `candidate-first`, `owner review required`, `confidence is not truth`, `tool output is not canon`, `model output is not canon`, `no model output as truth`, `no automatic canon`, `no apply-promotion outside explicit audited owner-confirmed path`, `no memory/canon mutation outside owner-approved workflow`, `queue presence is not approval`, `candidate persistence is not canon`, `no generated prose`, `no rewrite`, `no continuation`, `no outline`, `no training artifacts`, `no silent fallback`, `MVP is not complete`, and `end-to-end usability has not passed`.

### Boundary Confirmation

The MVP usability smoke contract is candidate-first; owner review required; evidence/provenance/source-locator backed when available; confidence is not truth; tool output is not canon; model output is not canon; no model output as truth; no automatic canon; no apply-promotion outside explicit audited owner-confirmed path; no memory/canon mutation outside owner-approved workflow; no training artifacts; no generated prose; no rewrite; no continuation; no outline; fail closed; no silent fallback; queue presence is not approval; candidate persistence is not canon; MVP is not complete; and end-to-end usability has not passed.

T003 implemented no smoke harness, no runtime, helper, routes, UI, dependency changes, model calls, persistence, canon, promotion, training, or generated-prose behavior. T003 also did not mark MVP complete and did not record an end-to-end usability pass.

# PHASE8-IMPL-022-T002 Validation Matrix Decision Snapshot

- Result: PASS; `PHASE8-IMPL-022-T002` is complete/PASS as docs/decision/planning only.
- Decision file: `docs/roadmap/decisions/PHASE8-IMPL-022-mvp-usability-validation-matrix-decision.md`.
- Scope: T002 defines the MVP end-to-end usability validation matrix and acceptance gates only. It covers owner-authored or owner-provided project text, project/workspace load path required for validation, runtime extraction, BookNLP, spaCy, unavailable/quarantine/fail-closed behavior, raw artifact persistence, candidate creation, review handoff, review queue, read-only review surface, frontend owner-action execution, apply-promotion, approved memory/canon, model-assisted evidence-backed extraction, analysis-only NCP/Subtxt/dramatica-flow, no generated prose, no prose-production, no training artifacts, no silent fallback, end-to-end smoke, and MVP blocker triage.
- T003 handoff: `PHASE8-IMPL-022-T003` is ready/active next and should convert the T002 matrix into expected-red end-to-end MVP smoke/contract tests. T003 remains tests-first expected-red only and should not implement the smoke harness.
- Boundary: candidate-first; owner review required; evidence/provenance/source-locator backed when available; confidence is not truth; tool output is not canon; model output is not canon; no model output as truth; no automatic canon; no apply-promotion outside explicit audited owner-confirmed path; no memory/canon mutation outside owner-approved workflow; no training artifacts; no generated prose; no rewrite; no continuation; no outline; fail closed; no silent fallback; queue presence is not approval; candidate persistence is not canon.
- MVP scope preservation: PHASE8-IMPL-022 remains active; T004 through T007 remain planned; fine-tuning remains deferred after MVP; generated prose/prose-production paths remain permanently forbidden; T002 does not mark MVP complete and does not record an end-to-end usability pass.
- Context execution boundary: used already-generated context artifacts as evidence only; did not run CCE, Graphify, Repomix, LeanCTX, AI Context generation, scaffold, collect-plan, source-cache refresh, baseline refresh, MCP tools, Codex subagents, models/Ollama, runtime extraction, BookNLP/spaCy, NCP/Subtxt/dramatica-flow, or subprocess runtime workflows.

# PHASE8-IMPL-022-T001 Publication Validation Snapshot

- Result: PASS; publication files are present and roadmap validation confirms registry/enrichment shape.
- Scope: PHASE8-IMPL-022 is active as the MVP-required End-to-end MVP usability validation parent after completed/PASS PHASE8-IMPL-021. PHASE8-IMPL-022-T001 is complete/PASS as docs/status/planning publication only. PHASE8-IMPL-022-T002 is ready/active next and should define the MVP end-to-end usability validation matrix and acceptance gates only; T002 remains docs/decision/planning only unless explicitly scoped otherwise. PHASE8-IMPL-022-T003 through PHASE8-IMPL-022-T007 are planned. The parent validates owner-authored or owner-provided project text, runtime extraction availability and guarded failure behavior, raw artifact persistence, candidate creation/review handoff, candidate review and review queue/read-only review surface, frontend owner-action execution, explicit audited apply-promotion, approved memory/canon mutation only through owner-approved workflow, model-assisted evidence-backed extraction, analysis-only NCP/Subtxt/dramatica-flow runtime integration, safe unavailable/quarantine/fail-closed states, and no generated prose/prose-production behavior. PHASE8-IMPL-022 is validation/orchestration/smoke planning first, not feature expansion by default. Candidate-first, owner review, evidence/provenance/source-locator backed when available, confidence is not truth, tool output is not canon, no model output as truth, no automatic canon, no apply-promotion outside explicit audited owner-confirmed path, no memory/canon mutation outside owner-approved workflow, no training artifacts, no generated prose, no rewrite, no continuation, no outline, fail closed, no silent fallback, queue presence is not approval, and candidate persistence is not canon remain required. Fine-tuning remains deferred after MVP. Generated prose/prose-production paths remain permanently forbidden. T001 does not mark MVP complete and does not record an end-to-end usability pass yet; PHASE8-IMPL-022 will prove or reveal gaps.
- Context execution boundary: used already-generated context artifacts as evidence only; did not run CCE, Graphify, Repomix, LeanCTX, AI Context generation, scaffold, collect-plan, source-cache refresh, baseline refresh, MCP tools, Codex subagents, models/Ollama, runtime extraction, BookNLP/spaCy, NCP/Subtxt/dramatica-flow, or subprocess runtime workflows.

# PHASE8-IMPL-021-T007 Parent Closeout

### Result

- Result: PASS.
- Scope: docs/status/governance closeout only.
- Parent task: `PHASE8-IMPL-021` - Analysis-only NCP/Subtxt/dramatica-flow runtime integration.
- Parent status: complete/PASS.
- Completed children recorded: `PHASE8-IMPL-021-T001`, `PHASE8-IMPL-021-T002`, `PHASE8-IMPL-021-T003`, `PHASE8-IMPL-021-T004`, `PHASE8-IMPL-021-T005`, `PHASE8-IMPL-021-T006`, and `PHASE8-IMPL-021-T007`.
- Recommended next MVP-required parent after review: `PHASE8-IMPL-022`.
- Fine-tuning remains deferred after MVP.
- Generated prose/prose-production paths remain permanently forbidden.

### Final Artifacts

- `docs/roadmap/decisions/PHASE8-IMPL-021-analysis-only-runtime-integration-boundary-allowlist-decision.md`
- `backend/story_knowledge/analysis_runtime_integration.py`
- `tests/test_writer_assistant_core_analysis_runtime_integration_contract.py`
- `tests/test_writer_assistant_core_analysis_runtime_integration_handoff_contract.py`
- `tests/test_writer_assistant_core_analysis_runtime_integration_safety_regression.py`

### Closeout Summary

PHASE8-IMPL-021 delivered the analysis-only NCP/Subtxt/dramatica-flow runtime boundary and audited allowlist decision, expected-red analysis runtime contract tests, pure in-memory analysis runtime guard helper, allowlist validation, request validation, non-executing plan building, output validation, candidate support shaping, diagnostic question shaping, quarantine/fail-closed wrapping, guarded runtime state reporting, evidence-backed candidate/diagnostic/review handoff objects, handoff validation, safety regression coverage, and minimal hardening for unsafe refs/allowlist values, missing-ref status preservation, nested forbidden output rejection, prose/improvement intent refusal, and explicit non-execution flags.

PHASE8-IMPL-021 added no NCP execution, no Subtxt execution, no dramatica-flow execution, no repository cloning, no dependency installation, no model/Ollama calls, no network/subprocess runtime behavior, no routes, no UI, no frontend changes, no package/dependency changes, no candidate persistence, no review queue entry creation, no apply-promotion changes, no approved memory/canon mutation, no bible/storyform/scenes/notes/materials mutation, no training/JSONL/dataset/model artifacts, no generated prose, no rewrite, no continuation, no outline, no draft, no revision, no polish, no expansion, no style imitation, no export-as-prose, no chapter prose, and no story prose.

NCP is structured context interchange only. Subtxt is rubric/diagnostic guidance only. dramatica-flow is audited allowlist only. Runtime outputs are candidate-first and owner review is required. `source_refs`, `evidence_refs`, `provenance_refs`, and `source_locator_refs` are preserved when available. Confidence is not truth. Tool output is not canon. Tool output is not truth. No model output as truth. No automatic canon. No apply-promotion. No memory/canon mutation. No training artifacts. No generated prose. No rewrite. No continuation. No outline. Fail closed. No silent fallback. Queue presence is not approval. Candidate persistence is not canon. Apply-promotion remains the separate explicit audited owner-confirmed path.

PHASE8-UX-001 remains read-only terminology/boundary reference only. No context tools, CCE, Graphify, Repomix, LeanCTX, AI context generation, source-cache refresh, baseline refresh, scaffold, collect-plan, context health scripts, Codex subagents, NCP runtime, Subtxt runtime, dramatica-flow runtime, models/Ollama, network, subprocess, repository cloning, or dependency installation were run for T007.

# PHASE8-IMPL-021-T006 Analysis Runtime Integration Safety Regression

### Result

- Result: PASS.
- Scope: analysis runtime integration safety regression, minimal helper hardening, docs/status/governance, and final validation.
- Parent task: `PHASE8-IMPL-021` - Analysis-only NCP/Subtxt/dramatica-flow runtime integration.
- Parent status: active.
- Completed child recorded: `PHASE8-IMPL-021-T006` - Analysis-only runtime integration safety regression.
- Final artifact: `tests/test_writer_assistant_core_analysis_runtime_integration_safety_regression.py`.
- Helper hardening artifact: `backend/story_knowledge/analysis_runtime_integration.py`.
- Active/ready next child: `PHASE8-IMPL-021-T007` - Parent closeout.
- Future MVP-required parent after this active parent: `PHASE8-IMPL-022`.
- Fine-tuning remains deferred after MVP.
- Generated prose/prose-production paths remain permanently forbidden.

### Safety Regression Summary

T006 adds focused safety regression coverage proving no runtime/tool execution, no NCP/Subtxt/dramatica-flow execution, no network/subprocess/model/Ollama/backend.analysis_engine calls, no git clone, no dependency install, no file write path, no persistence helper, no apply-promotion, no memory/canon mutation, and explicit disabled/unavailable/blocked/fail_closed states instead of silent success.

T006 covers unsafe source and request rejection, allowlist bypass rejection, missing/invalid refs, direct and nested forbidden output classes, refused_no_prose, blocked_request, quarantined, and fail_closed states. Required markers include `unsafe_path`, `allowlist_missing`, `allowlist_denied`, `unsupported_tool`, `unsupported_action`, `missing_source_refs`, `missing_evidence_refs`, `missing_provenance_refs`, `missing_source_locator_refs`, `source_locator_invalid`, `forbidden_output_type`, `refused_no_prose`, `blocked_request`, `quarantined`, and `fail_closed`.

Minimal helper hardening rejects unsafe allowlist/ref values, preserves explicit missing-ref states, rejects nested forbidden output classes, catches improvement/prose intents, and keeps shared non-execution flags explicit.

### Boundary Confirmation

NCP is structured context interchange only. Subtxt is rubric/diagnostic guidance only. dramatica-flow is audited allowlist only. Runtime outputs remain candidate-first and owner review required. Confidence is not truth. Tool output is not canon. Tool output is not truth. No automatic canon. No apply-promotion. No memory/canon mutation. No training artifacts. No generated prose. No rewrite. No continuation. No outline. Fail closed. No silent fallback. Queue presence is not approval. Candidate persistence is not canon.

T006 added no NCP execution, no Subtxt execution, no dramatica-flow execution, no routes, no UI, no frontend changes, no package/dependency changes, no model/Ollama calls, no network/subprocess calls, no persistence, no candidate persistence, no review queue entries, no approved memory/canon mutation, no apply-promotion, no training artifacts, and no generated prose behavior.

# PHASE8-IMPL-021-T005 Runtime Output Handoff Implementation

### Result

- Result: PASS.
- Scope: evidence-backed runtime output handoff implementation plus docs/status final validation.
- Parent task: `PHASE8-IMPL-021` - Analysis-only NCP/Subtxt/dramatica-flow runtime integration.
- Parent status: active.
- Completed child recorded: `PHASE8-IMPL-021-T005` - Evidence-backed runtime output handoff implementation.
- Final artifacts: `backend/story_knowledge/analysis_runtime_integration.py`, `tests/test_writer_assistant_core_analysis_runtime_integration_contract.py`, and `tests/test_writer_assistant_core_analysis_runtime_integration_handoff_contract.py`.
- Active/ready next child: `PHASE8-IMPL-021-T006` - Analysis-only runtime integration safety regression.
- Planned child: `PHASE8-IMPL-021-T007`.
- Future MVP-required parent after this active parent: `PHASE8-IMPL-022`.
- Fine-tuning remains deferred after MVP.
- Generated prose/prose-production paths remain permanently forbidden.

### Handoff Summary

T005 adds public helper APIs `build_analysis_runtime_candidate_observation_handoff`, `build_analysis_runtime_diagnostic_handoff`, `build_analysis_runtime_review_handoff`, and `validate_analysis_runtime_review_handoff`.

Candidate observation handoffs are pure dictionaries/lists, in-memory only, candidate-first, owner review required, evidence-backed, provenance-backed, and source-locator-backed when available. They preserve `source_refs`, `evidence_refs`, `provenance_refs`, and `source_locator_refs`, and fail closed on missing/invalid refs, insufficient evidence, rejected, quarantined, unavailable, or fail_closed states.

Diagnostic handoffs preserve diagnostic questions, uncertainty notes, insufficient-evidence notes, refused_no_prose, blocked_request, quarantined, unavailable, and fail_closed states. They do not contain prose suggestions, rewrites, continuations, outlines, drafts, revisions, polish, expansion, style imitation, export-as-prose, chapter prose, or story prose.

Review handoffs aggregate candidate and diagnostic handoffs only. They are not persistence, not review queue creation, not canon, not approved memory, not apply-promotion, and not training data.

### Boundary Confirmation

NCP is structured context interchange only. Subtxt is rubric/diagnostic guidance only. dramatica-flow is audited allowlist only. Confidence is not truth. Tool output is not canon. Tool output is not truth. No automatic canon. No apply-promotion. No memory/canon mutation. No training artifacts. No generated prose. No rewrite. No continuation. No outline. Fail closed. No silent fallback. Queue presence is not approval. Candidate persistence is not canon.

T005 added no NCP execution, no Subtxt execution, no dramatica-flow execution, no routes, no UI, no frontend changes, no package/dependency changes, no model/Ollama calls, no persistence, no candidate persistence, no review queue entries, no approved memory/canon mutation, no apply-promotion, no training artifacts, and no generated prose behavior.

# PHASE8-IMPL-021-T004 Guard Helper Implementation

### Result

- Result: PASS.
- Scope: minimal pure analysis runtime request/allowlist guard helper implementation plus docs/status final validation.
- Parent task: `PHASE8-IMPL-021` - Analysis-only NCP/Subtxt/dramatica-flow runtime integration.
- Parent status: active.
- Completed child recorded: `PHASE8-IMPL-021-T004` - Minimal analysis-only runtime request/allowlist guard implementation.
- Final artifact: `backend/story_knowledge/analysis_runtime_integration.py`.
- Active/ready next child: `PHASE8-IMPL-021-T005` - Evidence-backed runtime output handoff implementation.
- Planned children: `PHASE8-IMPL-021-T006` and `PHASE8-IMPL-021-T007`.
- Future MVP-required parent after this active parent: `PHASE8-IMPL-022`.
- Fine-tuning remains deferred after MVP.
- Generated prose/prose-production paths remain permanently forbidden.

### Helper Summary

T004 implements `validate_analysis_runtime_allowlist_record`, `validate_analysis_runtime_request`, `build_analysis_runtime_plan`, `validate_analysis_runtime_output`, `build_analysis_runtime_candidate_support`, `build_analysis_runtime_diagnostic_questions`, `quarantine_analysis_runtime_output`, and `run_guarded_analysis_runtime_integration`.

The helper validates audited allowlist records, request refs and confirmations, deterministic in-memory non-executing plans, allowed analysis output classes, forbidden output classes, candidate-first support, diagnostic questions without prose suggestions, quarantine records, and explicit disabled/unavailable/allowlist_missing/allowlist_denied/request_invalid/unsupported_tool/unsupported_action/blocked_request/fail_closed states. It preserves `source_refs`, `evidence_refs`, `provenance_refs`, and `source_locator_refs` when available.

### Boundary Confirmation

NCP is structured context interchange only. Subtxt is rubric/diagnostic guidance only. dramatica-flow is audited allowlist only. Runtime outputs remain candidate-first and owner review is required. Confidence is not truth. Tool output is not canon. Tool output is not truth. No model output as truth. No automatic canon. No apply-promotion. No memory/canon mutation. No training artifacts. No generated prose. No rewrite. No continuation. No outline. Fail closed. No silent fallback. Queue presence is not approval. Candidate persistence is not canon.

T004 added no NCP execution, no Subtxt execution, no dramatica-flow execution, no routes, no UI, no frontend changes, no package/dependency changes, no model/Ollama calls, no persistence, no candidate persistence, no review queue entries, no approved memory/canon mutation, no apply-promotion, no training artifacts, and no generated prose behavior.

# PHASE8-IMPL-021-T003 Expected-red Contract Tests

### Result

- Result: PASS.
- Scope: tests-first expected-red contract only.
- Parent task: `PHASE8-IMPL-021` - Analysis-only NCP/Subtxt/dramatica-flow runtime integration.
- Parent status: active.
- Completed child recorded: `PHASE8-IMPL-021-T003` - Expected-red NCP/Subtxt/dramatica-flow runtime integration contract tests.
- Test file: `tests/test_writer_assistant_core_analysis_runtime_integration_contract.py`.
- Expected-red target: future `backend.story_knowledge.analysis_runtime_integration` module and public API.
- Active/ready next child: `PHASE8-IMPL-021-T004` - Minimal analysis-only runtime request/allowlist guard implementation.
- Planned children: `PHASE8-IMPL-021-T005`, `PHASE8-IMPL-021-T006`, and `PHASE8-IMPL-021-T007`.
- Future MVP-required parent after this active parent: `PHASE8-IMPL-022`.
- Fine-tuning remains deferred after MVP.
- Generated prose/prose-production paths remain permanently forbidden.
- No context tools, CCE, Graphify, Repomix, AI context generation, source-cache refresh, baseline refresh, scaffold, collect-plan, context health scripts, Codex subagents, model/Ollama calls, BookNLP/spaCy extraction, NCP runtime, Subtxt runtime, or dramatica-flow runtime were run for task context; hook-required compact wrappers were used only when direct git/rg checks were blocked.

### Files Changed

- Created: `tests/test_writer_assistant_core_analysis_runtime_integration_contract.py`
- Updated: `docs/roadmap/tasks/PHASE8-IMPL-021.md`
- Updated: `docs/roadmap/inventory/PHASE8-IMPL-021.md`
- Updated: `docs/roadmap/enrichment/PHASE8-IMPL-021.enrichment.json`
- Updated: `docs/master_plan.md`
- Updated: `docs/roadmap/implementation_status.md`
- Updated: `docs/roadmap/roadmap_index.yaml`
- Updated: `docs/roadmap/task_backlog.md`
- Updated: `docs/roadmap/phase_map.md`
- Updated: `docs/roadmap/validation/latest_roadmap_validation.md`
- Updated: `docs/roadmap/decision_log.md`
- Updated: `docs/roadmap/risk_register.md`
- Updated: `docs/roadmap/open_questions.md`

### Contract Summary

T003 adds expected-red tests for the future public APIs: `validate_analysis_runtime_allowlist_record`, `validate_analysis_runtime_request`, `build_analysis_runtime_plan`, `validate_analysis_runtime_output`, `build_analysis_runtime_candidate_support`, `build_analysis_runtime_diagnostic_questions`, `quarantine_analysis_runtime_output`, and `run_guarded_analysis_runtime_integration`.

The contract requires allowlist records with `tool_name`, `module_or_feature_name`, `allowed_action`, `forbidden_actions`, `output_classes_allowed`, `output_classes_forbidden`, `required_refs`, `source_locator_policy`, `evidence_policy`, `provenance_policy`, `owner_review_policy`, `fail_closed_policy`, `no_silent_fallback_policy`, `no_prose_policy`, `no_training_policy`, `no_canon_policy`, `no_apply_promotion_policy`, `validation_tests_required`, and `audit_notes`. It requires requests with `source_refs`, `evidence_refs`, `provenance_refs`, and `source_locator_refs`, owner-authored or owner-provided source boundary, no generated prose, no rewrite, no continuation, no outline, no training, no canon, and no apply-promotion confirmations.

Allowed output classes are `evidence_backed_candidate_observation`, `diagnostic_question`, `uncertainty_note`, `insufficient_evidence_note`, `rubric_mapping_support`, `context_interchange_support`, `quarantined_result`, `unavailable_result`, `fail_closed_result`, `refused_no_prose`, and `blocked_request`. Forbidden output classes are `generated_prose`, `rewritten_prose`, `continuation`, `outline`, `chapter_generation`, `draft`, `revision`, `polish`, `improvement`, `expansion`, `style_imitation`, `export_as_prose`, `story_prose`, `model_prompt_artifact`, `model_completion_artifact`, `training_jsonl`, `dataset_manifest`, `model_artifact`, `promotion_record`, `approved_memory`, `canon`, `bible`, `storyform_truth`, `scene_mutation`, `note_mutation`, and `material_mutation`.

Required states include `disabled`, `unavailable`, `dependency_missing`, `configuration_invalid`, `allowlist_missing`, `allowlist_denied`, `unsupported_tool`, `unsupported_action`, `request_invalid`, `unsafe_path`, `missing_source_refs`, `missing_evidence_refs`, `missing_provenance_refs`, `missing_source_locator_refs`, `source_locator_invalid`, `unsupported_output_type`, `forbidden_output_type`, `malformed_output`, `evidence_insufficient`, `refused_no_prose`, `blocked_request`, `quarantined`, `rejected`, `diagnostic_questions_ready`, `candidate_support_ready`, `valid`, and `fail_closed`.

### Boundary Confirmation

NCP is structured context interchange only. Subtxt is rubric/diagnostic guidance only. dramatica-flow is audited allowlist only and its prose/write/revise/export/chapter/outline/generation paths are blocked. Runtime outputs remain candidate-first and owner review remains mandatory. Confidence is not truth. Tool output is not canon. Tool output is not truth. No model output as truth. No automatic canon. No apply-promotion. No memory/canon mutation. No training artifacts. No generated prose. No rewrite. No continuation. No outline. Fail closed. No silent fallback. Queue presence is not approval. Candidate persistence is not canon. Apply-promotion remains the separate explicit audited owner-confirmed path.

T003 implemented no runtime, helper implementation, routes, UI, dependency changes, model calls, persistence, canon, promotion, training, or generated-prose behavior.

# PHASE8-IMPL-021-T002 Boundary and Allowlist Decision

### Result

- Result: PASS.
- Scope: docs/decision only.
- Parent task: `PHASE8-IMPL-021` - Analysis-only NCP/Subtxt/dramatica-flow runtime integration.
- Parent status: active.
- Completed child recorded: `PHASE8-IMPL-021-T002` - Analysis-only runtime integration boundary and allowlist decision.
- Decision record: `docs/roadmap/decisions/PHASE8-IMPL-021-analysis-only-runtime-integration-boundary-allowlist-decision.md`.
- Active/ready next child: `PHASE8-IMPL-021-T003` - Expected-red NCP/Subtxt/dramatica-flow runtime integration contract tests.
- Planned children: `PHASE8-IMPL-021-T004`, `PHASE8-IMPL-021-T005`, `PHASE8-IMPL-021-T006`, and `PHASE8-IMPL-021-T007`.
- Future MVP-required parent after this active parent: `PHASE8-IMPL-022`.
- Fine-tuning remains deferred after MVP.
- Generated prose/prose-production paths remain permanently forbidden.
- No context tools, CCE, Graphify, Repomix, LeanCTX, AI context generation, source-cache refresh, baseline refresh, scaffold, collect-plan, context health scripts, Codex subagents, model/Ollama calls, BookNLP/spaCy extraction, NCP runtime, Subtxt runtime, or dramatica-flow runtime were run.

### Files Changed

- Created: `docs/roadmap/decisions/PHASE8-IMPL-021-analysis-only-runtime-integration-boundary-allowlist-decision.md`
- Updated: `docs/roadmap/tasks/PHASE8-IMPL-021.md`
- Updated: `docs/roadmap/inventory/PHASE8-IMPL-021.md`
- Updated: `docs/roadmap/enrichment/PHASE8-IMPL-021.enrichment.json`
- Updated: `docs/master_plan.md`
- Updated: `docs/roadmap/implementation_status.md`
- Updated: `docs/roadmap/roadmap_index.yaml`
- Updated: `docs/roadmap/task_backlog.md`
- Updated: `docs/roadmap/phase_map.md`
- Updated: `docs/roadmap/validation/latest_roadmap_validation.md`
- Updated: `docs/roadmap/decision_log.md`
- Updated: `docs/roadmap/risk_register.md`
- Updated: `docs/roadmap/open_questions.md`

### Decision Summary

T002 defines NCP as structured context interchange only, Subtxt as rubric/diagnostic guidance only, and dramatica-flow as usable only through audited allowlists. Future allowlist records must include `tool_name`, `module_or_feature_name`, `allowed_action`, `forbidden_actions`, `output_classes_allowed`, `output_classes_forbidden`, `required_refs`, `source_locator_policy`, `evidence_policy`, `provenance_policy`, `owner_review_policy`, `fail_closed_policy`, `no_silent_fallback_policy`, `no_prose_policy`, `no_training_policy`, `no_canon_policy`, `no_apply_promotion_policy`, `validation_tests_required`, and `audit_notes`.

Allowed future output classes are `evidence_backed_candidate_observation`, `diagnostic_question`, `uncertainty_note`, `insufficient_evidence_note`, `rubric_mapping_support`, `context_interchange_support`, `quarantined_result`, `unavailable_result`, `fail_closed_result`, `refused_no_prose`, and `blocked_request`. Forbidden future output classes include `generated_prose`, `rewritten_prose`, `continuation`, `outline`, `chapter_generation`, `draft`, `revision`, `polish`, `improvement`, `expansion`, `style_imitation`, `export_as_prose`, `story_prose`, `training_jsonl`, `dataset_manifest`, `model_artifact`, `promotion_record`, `approved_memory`, `canon`, `storyform_truth`, `scene_mutation`, `note_mutation`, and `material_mutation`.

Required future states include `disabled`, `unavailable`, `dependency_missing`, `configuration_invalid`, `allowlist_missing`, `allowlist_denied`, `unsupported_tool`, `unsupported_action`, `request_invalid`, `unsafe_path`, `missing_source_refs`, `missing_evidence_refs`, `missing_provenance_refs`, `missing_source_locator_refs`, `source_locator_invalid`, `unsupported_output_type`, `forbidden_output_type`, `malformed_output`, `evidence_insufficient`, `refused_no_prose`, `blocked_request`, `quarantined`, `rejected`, `diagnostic_questions_ready`, `candidate_support_ready`, `valid`, and `fail_closed`.

### Boundary Confirmation

Runtime outputs are candidate-first and owner review is required. `source_refs`, `evidence_refs`, `provenance_refs`, and `source_locator_refs` must be preserved when available. Confidence is not truth. Tool output is not canon. Tool output is not truth. No model output as truth. No automatic canon. No apply-promotion. No memory/canon mutation. No training artifacts. No generated prose. No rewrite. No continuation. No outline. Fail closed. No silent fallback. Queue presence is not approval. Candidate persistence is not canon. Apply-promotion remains the separate explicit audited owner-confirmed path.

T002 implemented no runtime, code, tests, routes, UI, dependency, model, persistence, canon, promotion, training, or generated-prose changes.

# PHASE8-IMPL-021-T001 Publication

### Result

- Result: PASS.
- Scope: docs/status/governance publication only.
- Parent task: `PHASE8-IMPL-021` - Analysis-only NCP/Subtxt/dramatica-flow runtime integration.
- Parent status: active.
- Completed child recorded: `PHASE8-IMPL-021-T001` - Publish/activate analysis-only NCP/Subtxt/dramatica-flow runtime integration parent.
- Active/ready next child: `PHASE8-IMPL-021-T002` - Analysis-only runtime integration boundary and allowlist decision.
- Planned children: `PHASE8-IMPL-021-T003`, `PHASE8-IMPL-021-T004`, `PHASE8-IMPL-021-T005`, `PHASE8-IMPL-021-T006`, and `PHASE8-IMPL-021-T007`.
- Prior parent: `PHASE8-IMPL-020` complete/PASS through `PHASE8-IMPL-020-T007`.
- Future MVP-required parent after this active parent: `PHASE8-IMPL-022`.
- Fine-tuning remains deferred after MVP.
- Generated prose/prose-production paths remain permanently forbidden.
- PHASE8-UX-001 remained read-only terminology/boundary reference only.
- No context tools, CCE, Graphify, Repomix, AI context generation, source-cache refresh, baseline refresh, scaffold, collect-plan, context health scripts, Codex subagents, model/Ollama calls, BookNLP/spaCy extraction, NCP runtime, Subtxt runtime, or dramatica-flow runtime were run.

### Files Changed

- Created: `docs/roadmap/tasks/PHASE8-IMPL-021.md`
- Created: `docs/roadmap/inventory/PHASE8-IMPL-021.md`
- Created: `docs/roadmap/enrichment/PHASE8-IMPL-021.enrichment.json`
- Updated: `docs/master_plan.md`
- Updated: `docs/roadmap/implementation_status.md`
- Updated: `docs/roadmap/roadmap_index.yaml`
- Updated: `docs/roadmap/task_backlog.md`
- Updated: `docs/roadmap/phase_map.md`
- Updated: `docs/roadmap/validation/latest_roadmap_validation.md`
- Updated: `docs/roadmap/decision_log.md`
- Updated: `docs/roadmap/risk_register.md`
- Updated: `docs/roadmap/open_questions.md`

### Publication Summary

PHASE8-IMPL-021 publishes and activates the MVP-required Analysis-only NCP/Subtxt/dramatica-flow runtime integration parent. NCP may be used as structured context interchange only. Subtxt may be used as rubric/diagnostic guidance only. dramatica-flow may be used only through an audited allowlist that blocks prose paths, outline paths, rewrite, continuation, draft, revision, polish, expansion, style imitation, chapter generation, write/revise, export-as-prose, and story-prose paths.

Future PHASE8-IMPL-021 contracts must preserve `source_refs`, `evidence_refs`, `provenance_refs`, and `source_locator_refs` when available. Runtime output is candidate-first and owner-review-required; confidence is not truth; tool output is not canon; no automatic canon, no apply-promotion, no memory/canon mutation, no training artifacts, no generated prose, no rewrite, no continuation, no outline, no model output as truth, fail closed, and no silent fallback remain required.

### Boundary Confirmation

- No NCP runtime implemented.
- No Subtxt runtime implemented.
- No dramatica-flow runtime implemented.
- No repositories cloned.
- No dependencies installed.
- No backend implementation code changed.
- No frontend implementation code changed.
- No tests changed.
- No routes added.
- No UI added.
- No package/dependency changes.
- No model/Ollama calls.
- No BookNLP/spaCy extraction over project text.
- No candidate records created.
- No review queue entries created.
- No apply-promotion changes.
- No approved memory/canon mutation.
- No bible/storyform/scenes/notes/materials mutation.
- No training/JSONL/dataset/model artifacts.
- No generated prose, rewrite, continuation, outline, draft, revision, polish, expansion, style imitation, or story prose.
- No staging, commit, or push.

### Future Guidance

- `PHASE8-IMPL-021-T002` is ready/active next for the analysis-only runtime integration boundary and allowlist decision.
- `PHASE8-IMPL-021-T003` through `PHASE8-IMPL-021-T007` remain planned.
- `PHASE8-IMPL-022` remains the end-to-end MVP validation parent.
- Fine-tuning remains deferred after MVP.
- Generated prose/prose-production paths remain permanently forbidden.

# PHASE8-IMPL-020-T007 Parent Closeout

### Result

- Result: PASS.
- Scope: docs/status/governance parent closeout only.
- Parent task: `PHASE8-IMPL-020` - Model-assisted evidence-backed extraction and diagnostic workflow.
- Parent result: complete/PASS.
- Completed child sequence: `PHASE8-IMPL-020-T001`, `PHASE8-IMPL-020-T002`, `PHASE8-IMPL-020-T003`, `PHASE8-IMPL-020-T004`, `PHASE8-IMPL-020-T005`, `PHASE8-IMPL-020-T006`, and `PHASE8-IMPL-020-T007` are complete/PASS.
- Completed child recorded: `PHASE8-IMPL-020-T007` - Parent closeout.
- Recommended next MVP-required parent after review: `PHASE8-IMPL-021` - NCP/Subtxt/dramatica-flow analysis-only runtime integration.
- Future MVP-required parent after that: `PHASE8-IMPL-022` - End-to-end MVP usability validation.
- Fine-tuning remains deferred after MVP.
- Generated prose/prose-production paths remain permanently forbidden.
- PHASE8-UX-001 remained read-only terminology/boundary reference only.
- No context tools, CCE, Graphify, Repomix, LeanCTX, AI context generation, source-cache refresh, baseline refresh, scaffold, collect-plan, context health scripts, Codex subagents, model/Ollama calls, BookNLP/spaCy extraction, or NCP/Subtxt/dramatica-flow runtime were run.

### Files Changed

- Updated: `docs/roadmap/tasks/PHASE8-IMPL-020.md`
- Updated: `docs/roadmap/inventory/PHASE8-IMPL-020.md`
- Updated: `docs/roadmap/enrichment/PHASE8-IMPL-020.enrichment.json`
- Updated: `docs/master_plan.md`
- Updated: `docs/roadmap/implementation_status.md`
- Updated: `docs/roadmap/roadmap_index.yaml`
- Updated: `docs/roadmap/task_backlog.md`
- Updated: `docs/roadmap/phase_map.md`
- Updated: `docs/roadmap/validation/latest_roadmap_validation.md`
- Updated: `docs/roadmap/decision_log.md`
- Updated: `docs/roadmap/risk_register.md`
- Updated: `docs/roadmap/open_questions.md`

### Final Artifact Summary

- `docs/roadmap/decisions/PHASE8-IMPL-020-model-assisted-extraction-diagnostic-workflow-boundary-decision.md`
- `backend/story_knowledge/model_assisted_extraction.py`
- `tests/test_writer_assistant_core_model_assisted_extraction_contract.py`
- `tests/test_writer_assistant_core_model_assisted_extraction_handoff_contract.py`
- `tests/test_writer_assistant_core_model_assisted_extraction_safety_regression.py`

### Final Behavior Summary

PHASE8-IMPL-020 delivered the model-assisted extraction boundary decision, pure model-assisted extraction guard helper, request validation, environment validation, in-memory prompt packet shaping, output validation, in-memory candidate support shaping, in-memory diagnostic question shaping, quarantine/fail-closed handling, in-memory diagnostic/candidate/review handoff objects, safety regression coverage, and minimal validation hardening for forbidden output classes, nested forbidden outputs, source locator refs, path traversal variants, and blocked forced success states.

### Final Boundary Summary

PHASE8-IMPL-020 did not add model/Ollama calls, `backend.analysis_engine` imports/calls, routes, UI, frontend changes, package/dependency changes, BookNLP/spaCy extraction, NCP/Subtxt/dramatica-flow runtime, candidate persistence, review queue entry creation, apply-promotion changes, approved memory/canon mutation, bible/storyform/scenes/notes/materials mutation, training/JSONL/dataset/model artifacts, generated prose, rewrite, continuation, outline, draft, revision, polish, expansion, style imitation, or story prose.

### Model-assisted Safety Summary

Model-assisted extraction remains local-first and guarded, candidate-first, and owner-review-required. `source_refs`, `evidence_refs`, `provenance_refs`, and `source_locator_refs` are preserved when available. Confidence is not truth; model output is not canon; no model output as truth; no automatic canon; no apply-promotion; no memory/canon mutation; no training artifacts; no generated prose; no rewrite; no continuation; no outline; fail closed; no silent fallback. Queue presence is not approval. Candidate persistence is not canon. Apply-promotion remains the separate explicit audited owner-confirmed path.

### Future Guidance

- `PHASE8-IMPL-021` is the recommended next MVP-required parent after review.
- `PHASE8-IMPL-022` remains future MVP-required.
- Fine-tuning remains deferred after MVP.
- Generated prose/prose-production paths remain permanently forbidden.
- PHASE8-UX-001 remains read-only terminology/boundary reference only.

# PHASE8-IMPL-020-T003 Expected-red Contract Tests

### Result

- Result: PASS.
- Scope: tests-first expected-red contract only.
- Parent task: `PHASE8-IMPL-020` - Model-assisted evidence-backed extraction and diagnostic workflow.
- Parent status: active.
- Completed child recorded: `PHASE8-IMPL-020-T003` - Expected-red model-assisted extraction contract tests.
- Test file: `tests/test_writer_assistant_core_model_assisted_extraction_contract.py`.
- Expected-red target: future `backend.story_knowledge.model_assisted_extraction` module and public API.
- Active/ready next child: `PHASE8-IMPL-020-T004` - Minimal model-assisted request/output guard implementation.
- Planned children: `PHASE8-IMPL-020-T005`, `PHASE8-IMPL-020-T006`, and `PHASE8-IMPL-020-T007`.
- Prior children: `PHASE8-IMPL-020-T001` complete/PASS as docs/status publication only; `PHASE8-IMPL-020-T002` complete/PASS as docs/decision only.
- Future MVP-required parents after this active parent: `PHASE8-IMPL-021` and `PHASE8-IMPL-022`.
- Fine-tuning remains deferred after MVP.
- Generated prose/prose-production paths remain permanently forbidden.
- PHASE8-UX-001 remained read-only terminology/boundary reference only.
- No context tools, context generation, model calls, implementation modules, candidate records, review queue entries, apply-promotion, memory/canon mutation, training artifacts, or generated prose were created.

### Files Changed

- Created: `tests/test_writer_assistant_core_model_assisted_extraction_contract.py`
- Updated: `docs/roadmap/tasks/PHASE8-IMPL-020.md`
- Updated: `docs/roadmap/inventory/PHASE8-IMPL-020.md`
- Updated: `docs/roadmap/enrichment/PHASE8-IMPL-020.enrichment.json`
- Updated: `docs/master_plan.md`
- Updated: `docs/roadmap/implementation_status.md`
- Updated: `docs/roadmap/roadmap_index.yaml`
- Updated: `docs/roadmap/task_backlog.md`
- Updated: `docs/roadmap/phase_map.md`
- Updated: `docs/roadmap/validation/latest_roadmap_validation.md`
- Updated: `docs/roadmap/decision_log.md`
- Updated: `docs/roadmap/risk_register.md`
- Updated: `docs/roadmap/open_questions.md`

### Contract Summary

T003 adds expected-red tests for the future public APIs: `validate_model_assisted_extraction_request`, `validate_model_assisted_environment`, `build_model_assisted_extraction_prompt_packet`, `validate_model_assisted_output`, `build_model_assisted_candidate_support`, `build_model_assisted_diagnostic_questions`, `quarantine_model_assisted_output`, and `run_guarded_model_assisted_extraction`.

The contract covers path-safe owner-authored or owner-provided requests; required `source_refs`, `evidence_refs`, `provenance_refs`, and `source_locator_refs`; raw source text separated from user intent; disabled/unavailable/fail-closed model-use states; prompt packet no-prose/no-rewrite/no-continuation/no-outline/no-training/no-canon/no-apply-promotion guards; allowed candidate/diagnostic/uncertainty/insufficient-evidence/refusal/quarantined outputs only; forbidden prose, model artifact, training, promotion, canon, bible, storyform, scene, note, and material mutation outputs; traceable evidence/provenance/source-locator support; candidate-first owner-review handoff; no automatic canon; no apply-promotion; no memory/canon mutation; no training artifacts; no generated prose; fail closed; and no silent fallback.

### Boundary Confirmation

- No `backend/story_knowledge/model_assisted_extraction.py` implementation module created.
- No backend implementation code changes.
- No frontend implementation code changes.
- No routes added.
- No UI added.
- No package/dependency changes.
- No model calls.
- No NCP/Subtxt/dramatica-flow runtime.
- No apply-promotion changes.
- No approved memory/canon mutation.
- No candidate records created.
- No review queue entries created.
- No generated prose.
- No training/JSONL/dataset/model artifacts.
- No source-cache/generated context artifacts staged.

### Future Guidance

- `PHASE8-IMPL-020-T004` is ready/active next for minimal model-assisted request/output guard implementation.
- `PHASE8-IMPL-020-T005` through `PHASE8-IMPL-020-T007` remain planned.
- `PHASE8-IMPL-021` remains the next parent after PHASE8-IMPL-020 closeout.
- `PHASE8-IMPL-022` remains the end-to-end MVP validation parent.
- Fine-tuning remains deferred after MVP.
- Generated prose/prose-production paths remain permanently forbidden.

# PHASE8-IMPL-020-T002 Boundary Decision

### Result

- Result: PASS.
- Scope: docs/decision only.
- Parent task: `PHASE8-IMPL-020` - Model-assisted evidence-backed extraction and diagnostic workflow.
- Parent status: active.
- Completed child recorded: `PHASE8-IMPL-020-T002` - Model-assisted extraction and diagnostic workflow boundary decision.
- Decision record: `docs/roadmap/decisions/PHASE8-IMPL-020-model-assisted-extraction-diagnostic-workflow-boundary-decision.md`.
- Active/ready next child: `PHASE8-IMPL-020-T003` - Expected-red model-assisted extraction contract tests.
- Planned children: `PHASE8-IMPL-020-T004`, `PHASE8-IMPL-020-T005`, `PHASE8-IMPL-020-T006`, and `PHASE8-IMPL-020-T007`.
- Prior child: `PHASE8-IMPL-020-T001` complete/PASS as docs/status publication only.
- Future MVP-required parents after this active parent: `PHASE8-IMPL-021` and `PHASE8-IMPL-022`.
- Fine-tuning remains deferred after MVP.
- Generated prose/prose-production paths remain permanently forbidden.
- PHASE8-UX-001 remained read-only terminology/boundary reference only.
- No context tools were run inside T002. Generated/context artifacts remain evidence only, not roadmap truth or task completion.

### Files Changed

- Created: `docs/roadmap/decisions/PHASE8-IMPL-020-model-assisted-extraction-diagnostic-workflow-boundary-decision.md`
- Updated: `docs/roadmap/tasks/PHASE8-IMPL-020.md`
- Updated: `docs/roadmap/inventory/PHASE8-IMPL-020.md`
- Updated: `docs/roadmap/enrichment/PHASE8-IMPL-020.enrichment.json`
- Updated: `docs/master_plan.md`
- Updated: `docs/roadmap/implementation_status.md`
- Updated: `docs/roadmap/roadmap_index.yaml`
- Updated: `docs/roadmap/task_backlog.md`
- Updated: `docs/roadmap/phase_map.md`
- Updated: `docs/roadmap/validation/latest_roadmap_validation.md`
- Updated: `docs/roadmap/decision_log.md`
- Updated: `docs/roadmap/risk_register.md`
- Updated: `docs/roadmap/open_questions.md`

### Decision Summary

PHASE8-IMPL-020-T002 accepts the future model-assisted extraction and diagnostic workflow boundary. Future model-assisted requests must be path-safe, over owner-authored or owner-provided project text/materials only, preserve `source_refs`, `evidence_refs`, `provenance_refs`, and `source_locator_refs` when available, separate raw source text from user intent, and include explicit no generated prose/no rewrite/no continuation/no outline/no training/no canon/no apply-promotion guard confirmations.

Allowed future outputs are evidence-backed candidate observation, diagnostic question, uncertainty note, insufficient-evidence note, candidate extraction support, safe refusal / blocked request result, and unavailable / fail-closed / quarantined result. Forbidden future outputs include generated_prose, rewritten_prose, continuation, outline, draft, revision, style imitation, polish/improvement/expansion, model_prompt artifact, model_completion artifact, training_jsonl, dataset_manifest, model_artifact, promotion_record, approved_memory, canon, bible, storyform, scene_mutation, note_mutation, and material_mutation.

Confidence is not truth. Model output is not canon. No model output as truth. No automatic canon, no apply-promotion, no memory/canon mutation, no training artifacts, fail closed, and no silent fallback remain required. Future candidate support is candidate-first and owner-review-required; queue presence is not approval; candidate persistence is not canon; apply-promotion remains the separate explicit audited owner-confirmed path from PHASE8-IMPL-017.

### Boundary Confirmation

- No backend implementation code changes.
- No frontend implementation code changes.
- No product test changes.
- No routes added.
- No UI added.
- No package/dependency changes.
- No model-assisted extraction implementation.
- No model/Ollama calls.
- No NCP/Subtxt/dramatica-flow runtime.
- No apply-promotion changes.
- No approved memory/canon mutation.
- No candidate records created.
- No review queue entries created.
- No generated prose.
- No training/JSONL/dataset/model artifacts.
- No source-cache/generated context artifacts staged.

### Future Guidance

- `PHASE8-IMPL-020-T003` is complete/PASS as expected-red model-assisted extraction contract tests.
- `PHASE8-IMPL-020-T004` is ready/active next.
- `PHASE8-IMPL-020-T005` through `PHASE8-IMPL-020-T007` remain planned.
- `PHASE8-IMPL-021` remains the next parent after PHASE8-IMPL-020 closeout.
- `PHASE8-IMPL-022` remains the end-to-end MVP validation parent.
- Fine-tuning remains deferred after MVP.
- Generated prose/prose-production paths remain permanently forbidden.

# PHASE8-IMPL-020-T001 Publication

### Result

- Result: PASS.
- Scope: docs/status/governance publication only.
- Parent task: `PHASE8-IMPL-020` - Model-assisted evidence-backed extraction and diagnostic workflow.
- Parent status: active.
- Completed child recorded: `PHASE8-IMPL-020-T001` - Publish/activate model-assisted evidence-backed extraction parent.
- Active/ready next child: `PHASE8-IMPL-020-T002` - Model-assisted extraction and diagnostic workflow boundary decision.
- Planned children: `PHASE8-IMPL-020-T003`, `PHASE8-IMPL-020-T004`, `PHASE8-IMPL-020-T005`, `PHASE8-IMPL-020-T006`, and `PHASE8-IMPL-020-T007`.
- Prior parent: `PHASE8-IMPL-019` complete/PASS through `PHASE8-IMPL-019-T007`.
- Future MVP-required parents after this active parent: `PHASE8-IMPL-021` and `PHASE8-IMPL-022`.
- Fine-tuning remains deferred after MVP.
- Generated prose/prose-production paths remain permanently forbidden.
- PHASE8-UX-001 remained read-only terminology/boundary reference only.
- No context tools were run inside T001. Generated/context artifacts remain evidence only, not roadmap truth or task completion.

### Files Changed

- Created: `docs/roadmap/tasks/PHASE8-IMPL-020.md`
- Created: `docs/roadmap/inventory/PHASE8-IMPL-020.md`
- Created: `docs/roadmap/enrichment/PHASE8-IMPL-020.enrichment.json`
- Updated: `docs/master_plan.md`
- Updated: `docs/roadmap/implementation_status.md`
- Updated: `docs/roadmap/roadmap_index.yaml`
- Updated: `docs/roadmap/task_backlog.md`
- Updated: `docs/roadmap/phase_map.md`
- Updated: `docs/roadmap/validation/latest_roadmap_validation.md`
- Updated: `docs/roadmap/decision_log.md`
- Updated: `docs/roadmap/risk_register.md`
- Updated: `docs/roadmap/open_questions.md`

### Publication Summary

PHASE8-IMPL-020 publishes and activates the MVP-required model-assisted evidence-backed extraction and diagnostic workflow parent. Model-assisted output may produce evidence-backed candidate observations, diagnostic questions, uncertainty notes, or candidate extraction support only.

Future PHASE8-IMPL-020 contracts must preserve `source_refs`, `evidence_refs`, `provenance_refs`, and `source_locator_refs` when available. Model output is candidate-first and owner-review-required; confidence is not truth; model output is not canon; no automatic canon, no apply-promotion, no memory/canon mutation, no training artifacts, no generated prose, no rewrite, no continuation, no outline, no model output as truth, fail closed, and no silent fallback remain required.

PHASE8-UX-001 may be used only as read-only terminology/boundary reference. It is not roadmap truth, does not override master_plan, implementation_status, roadmap_index, or PHASE8-IMPL parent boundaries, and was not edited.

### Boundary Confirmation

- No backend implementation code changes.
- No frontend implementation code changes.
- No product test changes.
- No routes added.
- No UI added.
- No package/dependency changes.
- No model-assisted extraction implementation.
- No model/Ollama calls.
- No NCP/Subtxt/dramatica-flow runtime.
- No apply-promotion changes.
- No approved memory/canon mutation.
- No candidate/review queue creation.
- No generated prose.
- No training/JSONL/dataset/model artifacts.
- No source-cache/generated context artifacts staged.

### Future Guidance

- `PHASE8-IMPL-020-T002` is ready/active next and remains docs/decision only.
- `PHASE8-IMPL-020-T003` through `PHASE8-IMPL-020-T007` remain planned.
- `PHASE8-IMPL-021` remains the next parent after PHASE8-IMPL-020 closeout.
- `PHASE8-IMPL-022` remains the end-to-end MVP validation parent.
- Fine-tuning remains deferred after MVP.
- Generated prose/prose-production paths remain permanently forbidden.

# PHASE8-IMPL-019-T007 Parent Closeout

### Result

- Result: PASS.
- Scope: docs/status/governance parent closeout only.
- Parent task: `PHASE8-IMPL-019` - Guarded runtime extraction: real BookNLP/spaCy install/run/import and candidate-first extraction pipeline.
- Completed child recorded: `PHASE8-IMPL-019-T007` - Parent closeout.
- Parent result: complete/PASS.
- Completed child sequence: `PHASE8-IMPL-019-T001`, `PHASE8-IMPL-019-T002`, `PHASE8-IMPL-019-T003`, `PHASE8-IMPL-019-T004`, `PHASE8-IMPL-019-T005`, `PHASE8-IMPL-019-T006`, and `PHASE8-IMPL-019-T007` are complete/PASS.
- Next parent recommendation: `PHASE8-IMPL-020` - Model-assisted evidence-backed extraction and diagnostic workflow.
- PHASE8-IMPL-020 through PHASE8-IMPL-022 remain future MVP-required parents.
- Fine-tuning remains deferred after MVP.
- Generated prose/prose-production paths remain permanently forbidden.
- PHASE8-UX-001 remained read-only terminology/boundary reference only.
- No context tools were run for context generation. Generated/context artifacts remain evidence only, not roadmap truth or task completion.

### Files Changed

- Updated: `docs/roadmap/tasks/PHASE8-IMPL-019.md`
- Updated: `docs/roadmap/inventory/PHASE8-IMPL-019.md`
- Updated: `docs/roadmap/enrichment/PHASE8-IMPL-019.enrichment.json`
- Updated: `docs/master_plan.md`
- Updated: `docs/roadmap/implementation_status.md`
- Updated: `docs/roadmap/roadmap_index.yaml`
- Updated: `docs/roadmap/task_backlog.md`
- Updated: `docs/roadmap/phase_map.md`
- Updated: `docs/roadmap/validation/latest_roadmap_validation.md`
- Updated: `docs/roadmap/decision_log.md`
- Updated: `docs/roadmap/risk_register.md`
- Updated: `docs/roadmap/open_questions.md`

### Parent Closeout Summary

T001 published/activated the parent. T002 accepted the guarded runtime extraction boundary/environment model decision. T003 added expected-red runtime extraction contract tests. T004 implemented minimal guarded runtime extraction helper APIs. T005 implemented guarded request/raw artifact handoff and focused tests. T006 added runtime extraction safety regression and minimal hardening. T007 closes the parent.

Final artifacts are `backend/story_knowledge/runtime_extraction.py`, `tests/test_writer_assistant_core_runtime_extraction_contract.py`, `tests/test_writer_assistant_core_runtime_extraction_raw_artifact_handoff_contract.py`, `tests/test_writer_assistant_core_runtime_extraction_safety_regression.py`, and `docs/roadmap/decisions/PHASE8-IMPL-019-guarded-runtime-extraction-boundary-environment-model-decision.md`.

Final behavior includes explicit runtime extraction environment/availability states, BookNLP/spaCy availability/probe guard shape, path-safe request validation, owner-authored/owner-provided source boundary, source/evidence/provenance/source-locator ref preservation, deterministic plan building, transient probe result behavior, guarded fail-closed runtime execution shell, PHASE8-IMPL-018 raw artifact handoff persistence, candidate-review draft handoff only, quarantine handling, no silent fallback, and no full BookNLP/spaCy extraction over project text yet.

### Boundary Confirmation

- No package/dependency changes.
- No routes.
- No UI.
- No frontend changes.
- No full runtime extraction over project text.
- No model/Ollama calls.
- No NCP/Subtxt/dramatica-flow runtime.
- No apply-promotion changes.
- No approved memory/canon mutation.
- No candidate persistence/review queue creation.
- No training/JSONL/dataset/model artifacts.
- No generated prose.
- No staging, commit, or push performed.

### Future Guidance

- Commit T007 after review.
- Prepare `PHASE8-IMPL-020-T001` only after review.
- Keep PHASE8-IMPL-020 through PHASE8-IMPL-022 future MVP-required.
- Keep fine-tuning deferred after MVP.
- Keep generated prose/prose-production paths permanently forbidden.

# PHASE8-IMPL-019-T004 Minimal Guarded Runtime Extraction Helper

### Result

- Result: PASS.
- Scope: minimal backend helper plus roadmap/status updates.
- Parent task: `PHASE8-IMPL-019` - Guarded runtime extraction: real BookNLP/spaCy install/run/import and candidate-first extraction pipeline.
- Parent status: active.
- Completed child recorded: `PHASE8-IMPL-019-T004` - Minimal guarded dependency availability and import/run probe implementation.
- Prior completed children: `PHASE8-IMPL-019-T001`, `PHASE8-IMPL-019-T002`, and `PHASE8-IMPL-019-T003`.
- Active/ready next child: `PHASE8-IMPL-019-T005` - Guarded runtime extraction request and raw artifact handoff implementation.
- Planned children: `PHASE8-IMPL-019-T006` and `PHASE8-IMPL-019-T007`.
- Future MVP-required parents after `PHASE8-IMPL-019`: `PHASE8-IMPL-020`, `PHASE8-IMPL-021`, and `PHASE8-IMPL-022`.
- Fine-tuning remains deferred after MVP.
- Generated prose/prose-production paths remain permanently forbidden.
- PHASE8-UX-001 remained read-only terminology/boundary reference only.
- No context tools were run inside T004. Generated context artifacts remain evidence only, not roadmap truth or task completion.

### Files Changed

- Created: `backend/story_knowledge/runtime_extraction.py`
- Updated: `docs/roadmap/tasks/PHASE8-IMPL-019.md`
- Updated: `docs/roadmap/inventory/PHASE8-IMPL-019.md`
- Updated: `docs/roadmap/enrichment/PHASE8-IMPL-019.enrichment.json`
- Updated: `docs/master_plan.md`
- Updated: `docs/roadmap/implementation_status.md`
- Updated: `docs/roadmap/roadmap_index.yaml`
- Updated: `docs/roadmap/task_backlog.md`
- Updated: `docs/roadmap/phase_map.md`
- Updated: `docs/roadmap/validation/latest_roadmap_validation.md`
- Updated: `docs/roadmap/decision_log.md`
- Updated: `docs/roadmap/risk_register.md`
- Updated: `docs/roadmap/open_questions.md`

### Implementation Summary

`PHASE8-IMPL-019-T004` creates `backend/story_knowledge/runtime_extraction.py` as the minimal guarded runtime extraction helper. It implements `validate_runtime_extraction_environment`, `check_booknlp_availability`, `check_spacy_availability`, `validate_runtime_extraction_request`, `build_runtime_extraction_plan`, `run_runtime_extraction_probe`, `run_guarded_runtime_extraction`, `build_raw_artifact_handoff`, `build_candidate_review_handoff`, and `quarantine_runtime_extraction_output`.

The helper is disabled/fail-closed by default, separates dependency/import/probe availability from runtime extraction success, validates owner-authored or owner-provided request boundaries, rejects unsafe ids/paths, requires source/evidence/provenance/source-locator refs, builds deterministic side-effect-free plans, returns transient probe status, and produces draft-only raw artifact/candidate review handoff and quarantine shapes. Probe success is not runtime extraction success.

T004 does not install dependencies, edit package files, add routes/UI, run full runtime extraction over project text, call models/Ollama, persist candidates or review queue entries, mutate approved memory/canon, apply promotion, create training artifacts, or generate prose. Raw artifact persistence through PHASE8-IMPL-018 helpers remains future T005 scope.

### T005 Handoff

`PHASE8-IMPL-019-T005` is ready/active next for guarded runtime extraction request and raw artifact handoff implementation. It must preserve owner-authored or owner-provided source boundaries, PHASE8-IMPL-018 raw artifact support data vocabulary, candidate-first owner review handoff, explicit unavailable/quarantine states, and no automatic canon/apply-promotion/memory-canon mutation/model calls/training artifacts/generated prose.

### Boundary Confirmation

- Backend implementation limited to `backend/story_knowledge/runtime_extraction.py`.
- No frontend implementation code changes.
- No product test changes.
- No routes added.
- No UI added.
- No package/dependency changes.
- No dependency install.
- No full runtime extraction over project text.
- No BookNLP/spaCy package addition.
- No model/Ollama calls.
- No NCP/Subtxt/dramatica-flow runtime.
- No apply-promotion changes.
- No approved memory/canon mutation.
- No candidate/review queue creation.
- No generated prose.
- No training/JSONL/dataset/model artifacts.
- No source-cache/generated context artifacts staged.

### Future Guidance

- `PHASE8-IMPL-019-T005` is ready/active next.
- `PHASE8-IMPL-019-T006` and `PHASE8-IMPL-019-T007` remain planned.
- `PHASE8-IMPL-020` remains the next parent after `PHASE8-IMPL-019`.
- `PHASE8-IMPL-020` owns model-assisted extraction.
- `PHASE8-IMPL-021` owns NCP/Subtxt/dramatica-flow runtime.
- `PHASE8-IMPL-022` owns end-to-end MVP validation.
- Fine-tuning remains deferred after MVP.
- Generated prose/prose-production paths remain permanently forbidden.

# PHASE8-IMPL-019-T001 Publication

### Result

- Result: PASS.
- Scope: docs/status/governance publication only.
- Parent task: `PHASE8-IMPL-019` - Guarded runtime extraction: real BookNLP/spaCy install/run/import and candidate-first extraction pipeline.
- Parent status: active.
- Completed child recorded: `PHASE8-IMPL-019-T001` - Publish/activate guarded runtime extraction parent.
- Active/ready next child: `PHASE8-IMPL-019-T002` - Guarded runtime extraction boundary decision and environment model.
- Planned children: `PHASE8-IMPL-019-T003`, `PHASE8-IMPL-019-T004`, `PHASE8-IMPL-019-T005`, `PHASE8-IMPL-019-T006`, and `PHASE8-IMPL-019-T007`.
- Future MVP-required parents after `PHASE8-IMPL-019`: `PHASE8-IMPL-020`, `PHASE8-IMPL-021`, and `PHASE8-IMPL-022`.
- Fine-tuning remains deferred after MVP.
- Generated prose/prose-production paths remain permanently forbidden.
- PHASE8-UX-001 remained read-only terminology/boundary reference only.
- No context tools were run inside T001. Generated context artifacts remain evidence only, not roadmap truth or task completion.

### Files Changed

- Created: `docs/roadmap/tasks/PHASE8-IMPL-019.md`
- Created: `docs/roadmap/inventory/PHASE8-IMPL-019.md`
- Created: `docs/roadmap/enrichment/PHASE8-IMPL-019.enrichment.json`
- Updated: `docs/master_plan.md`
- Updated: `docs/roadmap/implementation_status.md`
- Updated: `docs/roadmap/roadmap_index.yaml`
- Updated: `docs/roadmap/task_backlog.md`
- Updated: `docs/roadmap/phase_map.md`
- Updated: `docs/roadmap/validation/latest_roadmap_validation.md`
- Updated: `docs/roadmap/decision_log.md`
- Updated: `docs/roadmap/risk_register.md`
- Updated: `docs/roadmap/open_questions.md`

### Publication Summary

Deliver real BookNLP/spaCy install/run/import checks and guarded runtime extraction from owner-authored or owner-provided project text into raw artifact bundles and candidate-first review handoff, without canon mutation, model calls, automatic apply-promotion, training artifacts, or generated prose.

Runtime extraction in PHASE8-IMPL-019 may be introduced only through explicitly scoped children after T001 and may run only over owner-authored or owner-provided project text/materials. Output is candidate-first and owner-review-gated; runtime extraction output is never canon by itself, raw tool output is never authoritative by itself, extractor confidence is not truth, and extractor output cannot mutate approved memory/canon, apply promotion, create training data, or generate prose. Raw artifacts must be persisted through PHASE8-IMPL-018 helpers. Candidate persistence/review queue handoff may use existing candidate/review infrastructure only when explicitly scoped. Apply-promotion remains the separate PHASE8-IMPL-017 owner-confirmed path. Missing tools, missing models, unsafe paths, missing source/evidence/provenance, invalid source locators, malformed tool outputs, or unavailable environment must fail-closed or return explicit unavailable/quarantined state. No silent fallback may claim extraction succeeded.

Future runtime extraction contracts must preserve `source_refs`, `evidence_refs`, `provenance_refs`, and `source_locator_refs`; use PHASE8-IMPL-018 raw artifact persistence; return candidate-first handoff for owner review; and distinguish availability, unavailable, quarantine, fail-closed, malformed output, unsafe path, and missing evidence/provenance states. The install_import_run boundary is published for later children only.

PHASE8-UX-001 was used only as a read-only terminology/boundary reference for labels such as review, candidate, evidence, provenance, source locator, raw artifact, approved memory/canon, owner action, unavailable/quarantined state, and no automatic canon. PHASE8-UX-001 is not roadmap truth, does not override master_plan, implementation_status, roadmap_index, or PHASE8-IMPL parent boundaries, and was not edited.

### Boundary Confirmation

- No backend implementation code changes.
- No frontend implementation code changes.
- No product test changes.
- No routes added.
- No UI added.
- No package/dependency changes.
- No runtime extraction.
- No BookNLP/spaCy install/run/import.
- No model/Ollama calls.
- No NCP/Subtxt/dramatica-flow runtime.
- No apply-promotion changes.
- No approved memory/canon mutation.
- No candidate/review queue creation.
- No generated prose.
- No training/JSONL/dataset/model artifacts.
- No source-cache/generated context artifacts staged.

### Future Guidance

- `PHASE8-IMPL-019-T002` is ready/active next and remains docs/decision only.
- `PHASE8-IMPL-020` remains the next parent after `PHASE8-IMPL-019`.
- `PHASE8-IMPL-020` through `PHASE8-IMPL-022` remain future MVP-required parents.
- Fine-tuning remains deferred after MVP.
- Generated prose/prose-production paths remain permanently forbidden.

# PHASE8-IMPL-018-T007 Parent Closeout

### Result

- Result: PASS.
- Scope: docs/status/governance parent closeout only.
- Parent task: `PHASE8-IMPL-018` - Raw artifact persistence implementation and project-local extraction artifact lifecycle.
- Completed child recorded: `PHASE8-IMPL-018-T007` - Parent closeout.
- Parent result: complete/PASS.
- Completed child sequence: `PHASE8-IMPL-018-T001`, `PHASE8-IMPL-018-T002`, `PHASE8-IMPL-018-T003`, `PHASE8-IMPL-018-T004`, `PHASE8-IMPL-018-T005`, `PHASE8-IMPL-018-T006`, and `PHASE8-IMPL-018-T007` are complete/PASS.
- Delivered decision: `docs/roadmap/decisions/PHASE8-IMPL-018-raw-artifact-persistence-boundary-manifest-model-decision.md`.
- Delivered backend helper: `backend/story_knowledge/raw_artifacts.py`.
- Delivered contracts/regressions: `tests/test_writer_assistant_core_raw_artifacts_contract.py`, `tests/test_writer_assistant_core_raw_artifact_lifecycle_contract.py`, and `tests/test_writer_assistant_core_raw_artifact_safety_regression.py`.
- Active/ready next parent: `PHASE8-IMPL-019` - Real BookNLP/spaCy install/run/import and runtime extraction pipeline.
- Future MVP-required parents after `PHASE8-IMPL-019`: `PHASE8-IMPL-020`, `PHASE8-IMPL-021`, and `PHASE8-IMPL-022`.
- Fine-tuning remains deferred after MVP.
- Generated prose/prose-production paths remain permanently forbidden.
- No context tools were run inside T007. Generated context artifacts remain evidence only, not roadmap truth or task completion.

### Files Changed

- Updated: `docs/roadmap/tasks/PHASE8-IMPL-018.md`
- Updated: `docs/roadmap/inventory/PHASE8-IMPL-018.md`
- Updated: `docs/roadmap/enrichment/PHASE8-IMPL-018.enrichment.json`
- Updated: `docs/roadmap/implementation_status.md`
- Updated: `docs/roadmap/roadmap_index.yaml`
- Updated: `docs/roadmap/task_backlog.md`
- Updated: `docs/roadmap/phase_map.md`
- Updated: `docs/roadmap/validation/latest_roadmap_validation.md`
- Updated: `docs/roadmap/decision_log.md`
- Updated: `docs/roadmap/risk_register.md`
- Updated: `docs/roadmap/open_questions.md`
- Updated: `docs/master_plan.md`

### Parent Closeout Summary

- Raw artifact persistence is manifest-backed by `manifest.json`, bundle-based, index-aware, project-local, path-safe, quarantine-aware, evidence/provenance-linked, and fail-closed.
- Implemented APIs include `validate_raw_artifact_manifest`, `build_raw_artifact_manifest`, `validate_raw_artifact_file_ref`, `raw_artifact_bundle_storage_dir`, `raw_artifact_manifest_path`, `raw_artifact_index_path`, `write_raw_artifact_bundle`, `read_raw_artifact_manifest`, `read_raw_artifact_file`, `list_raw_artifact_bundles`, `rebuild_raw_artifact_index`, `quarantine_raw_artifact_bundle`, and `compute_raw_artifact_bundle_hash`.
- Delivered behavior includes valid-only default listing/indexing, derived/rebuildable support-data indexes, `source_refs`, `evidence_refs`, `provenance_refs`, `source_locator_refs`, quarantine handling, superseded/deleted_tombstone exclusion by default, duplicate/idempotency handling, canonical deterministic bundle hashing, and fail-closed validation.
- Raw artifacts remain support data only, not canon, not approved memory, not candidates, and not training data.

### Boundary Confirmation

- No runtime extraction.
- No real BookNLP/spaCy install/run/import.
- No model-assisted extraction.
- No model/Ollama calls.
- No NCP/Subtxt/dramatica-flow runtime.
- No routes added.
- No UI added.
- No package/dependency changes.
- No apply-promotion changes.
- No approved memory/canon mutation beyond the existing `PHASE8-IMPL-017` path.
- No candidate/review queue creation.
- No generated prose.
- No training/JSONL/dataset/model artifacts.
- No source-cache/generated context artifacts staged.

### Future Guidance

- `PHASE8-IMPL-019` is ready/active next only as a future MVP-required parent handoff for real BookNLP/spaCy install/run/import plus runtime extraction.
- `PHASE8-IMPL-019` must be bounded by environment guards, source/evidence/provenance requirements, raw artifact persistence support from `PHASE8-IMPL-018`, candidate-first output, owner review, no automatic canon, no generated prose, and no apply-promotion unless explicitly owner-confirmed through the existing separate path.
- Do not implement `PHASE8-IMPL-019` until separately scoped.

# PHASE8-IMPL-018-T006 Raw Artifact Safety Regression

### Result

- Result: PASS.
- Scope: raw artifact safety regression coverage only.
- Parent task: `PHASE8-IMPL-018` - Raw artifact persistence implementation and project-local extraction artifact lifecycle.
- Completed child recorded: `PHASE8-IMPL-018-T006` - Raw artifact safety regression: non-canon, non-training, path-safe, no extraction.
- Safety regression test: `tests/test_writer_assistant_core_raw_artifact_safety_regression.py` PASS.
- Existing raw artifact contract: `tests/test_writer_assistant_core_raw_artifacts_contract.py` PASS.
- Existing raw artifact lifecycle/provenance contract: `tests/test_writer_assistant_core_raw_artifact_lifecycle_contract.py` PASS.
- Active parent: `PHASE8-IMPL-018` MVP-required.
- Active/ready next child: `PHASE8-IMPL-018-T007` - Parent closeout.
- Future MVP-required parents: `PHASE8-IMPL-019`, `PHASE8-IMPL-020`, `PHASE8-IMPL-021`, and `PHASE8-IMPL-022`.
- Prior completed child: `PHASE8-IMPL-018-T005` complete/PASS and committed.
- Prior parent: `PHASE8-IMPL-017` remains complete/PASS through `PHASE8-IMPL-017-T007`.
- No context tools were run inside T006. Generated context artifacts remain evidence only, not roadmap truth or task completion.

### Files Changed

- Created: `tests/test_writer_assistant_core_raw_artifact_safety_regression.py`
- Updated: `docs/roadmap/tasks/PHASE8-IMPL-018.md`
- Updated: `docs/roadmap/inventory/PHASE8-IMPL-018.md`
- Updated: `docs/roadmap/enrichment/PHASE8-IMPL-018.enrichment.json`
- Updated: `docs/roadmap/implementation_status.md`
- Updated: `docs/roadmap/roadmap_index.yaml`
- Updated: `docs/roadmap/task_backlog.md`
- Updated: `docs/roadmap/phase_map.md`
- Updated: `docs/roadmap/validation/latest_roadmap_validation.md`
- Updated: `docs/roadmap/decision_log.md`
- Updated: `docs/roadmap/risk_register.md`
- Updated: `docs/roadmap/open_questions.md`
- Updated: `docs/master_plan.md`

### Safety Regression Summary

- Raw artifacts remain support data only, not canon, not candidates, and not training data.
- Operations are path-safe and fail-closed for unsafe ids, unsafe `relative_path`, missing/unreferenced/hash-mismatched artifact files, invalid manifests, invalid JSON manifests, unsupported statuses, unsupported artifact types, forbidden destination/action fields, missing refs, missing or false boundary confirmations, duplicate conflicts, and quarantine state.
- Tests cover `source_refs`, `evidence_refs`, `provenance_refs`, `source_locator_refs`, `quarantine_reason`, `no_generated_prose_confirmation`, `no_model_call_confirmation`, `no_training_artifact_confirmation`, `no_apply_promotion_confirmation`, `no_memory_canon_mutation_confirmation`, and `no_runtime_extraction_confirmation`.
- Forbidden markers covered include `generated_prose`, `rewritten_prose`, `continuation`, `outline`, `training_jsonl`, `dataset_manifest`, `model_artifact`, `runtime_extraction_trigger`, `promotion_record`, `approved_memory`, `candidate_record`, and `review_queue_entry`.
- No minimal backend hardening patch was required after preserving the accepted raw artifact API boundary.

### Boundary Confirmation

- No routes added.
- No frontend implementation code changes.
- No package/dependency changes.
- No runtime extraction.
- No BookNLP/spaCy install/run/import.
- No model/Ollama calls.
- No NCP/Subtxt/dramatica-flow runtime.
- No apply-promotion changes.
- No approved memory/canon mutation.
- No candidate/review queue creation.
- No generated prose.
- No training/JSONL/dataset/model artifacts.
- No source-cache/generated context artifacts staged.

### Future Guidance

- `PHASE8-IMPL-018-T007` is ready/active next and remains limited to parent closeout.
- `PHASE8-IMPL-019` through `PHASE8-IMPL-022` remain future MVP-required parents.
- Fine-tuning remains deferred after MVP.
- Generated prose/prose-production paths remain permanently forbidden.

# PHASE8-IMPL-018-T005 Raw Artifact Bundle/Index Lifecycle And Provenance Linkage

### Result

- Result: PASS.
- Scope: raw artifact bundle/index lifecycle and provenance linkage hardening plus focused tests/docs/status alignment only.
- Parent task: `PHASE8-IMPL-018` - Raw artifact persistence implementation and project-local extraction artifact lifecycle.
- Completed child recorded: `PHASE8-IMPL-018-T005` - Raw artifact bundle/index lifecycle and provenance linkage.
- Backend helper: `backend/story_knowledge/raw_artifacts.py`.
- Lifecycle/provenance test: `tests/test_writer_assistant_core_raw_artifact_lifecycle_contract.py` PASS.
- Contract test: `tests/test_writer_assistant_core_raw_artifacts_contract.py` PASS.
- Active parent: `PHASE8-IMPL-018` MVP-required.
- Active/ready next child: `PHASE8-IMPL-018-T006` - Raw artifact safety regression: non-canon, non-training, path-safe, no extraction.
- Planned child: `PHASE8-IMPL-018-T007`.
- Future MVP-required parents: `PHASE8-IMPL-019`, `PHASE8-IMPL-020`, `PHASE8-IMPL-021`, and `PHASE8-IMPL-022`.
- Prior completed child: `PHASE8-IMPL-018-T004` complete/PASS and committed with the minimal backend helper.
- Prior parent: `PHASE8-IMPL-017` remains complete/PASS through `PHASE8-IMPL-017-T007`.
- No context tools were run inside T005. Generated context artifacts remain evidence only, not roadmap truth or task completion.

### Files Changed

- Updated: `backend/story_knowledge/raw_artifacts.py`
- Updated: `tests/test_writer_assistant_core_raw_artifacts_contract.py`
- Created: `tests/test_writer_assistant_core_raw_artifact_lifecycle_contract.py`
- Updated: `docs/roadmap/tasks/PHASE8-IMPL-018.md`
- Updated: `docs/roadmap/inventory/PHASE8-IMPL-018.md`
- Updated: `docs/roadmap/enrichment/PHASE8-IMPL-018.enrichment.json`
- Updated: `docs/roadmap/implementation_status.md`
- Updated: `docs/roadmap/roadmap_index.yaml`
- Updated: `docs/roadmap/task_backlog.md`
- Updated: `docs/roadmap/phase_map.md`
- Updated: `docs/roadmap/validation/latest_roadmap_validation.md`
- Updated: `docs/roadmap/decision_log.md`
- Updated: `docs/roadmap/risk_register.md`
- Updated: `docs/roadmap/open_questions.md`
- Updated: `docs/master_plan.md`

### Lifecycle/Provenance Summary

- `backend/story_knowledge/raw_artifacts.py` hardens `pending_validation`, `valid`, `rejected`, `quarantined`, `superseded`, and `deleted_tombstone` lifecycle behavior.
- `list_raw_artifact_bundles` and `rebuild_raw_artifact_index` default to valid bundles only.
- Indexes are derived rebuildable support data, not canon, not candidates, and not training data.
- Index entries include safe manifest metadata: `raw_artifact_bundle_id`, `status`, `artifact_source_type`, `artifact_source_id`, `extraction_run_id`, `source_refs`, `evidence_refs`, `provenance_refs`, `source_locator_refs`, artifact file summaries, `bundle_hash`, `manifest_hash` or `content_hash`, `validation_status`, `created_at`, and `updated_at`.
- Valid bundle validation preserves source/evidence/provenance/source locator refs and fails closed when required linkage is missing.
- Artifact file refs preserve `artifact_file_id`, `artifact_type`, `relative_path`, `sha256`, source locator refs, evidence refs, provenance refs, and boundary flags.
- Missing, invalid, stale, non-valid, path-escaping, hash-mismatched, and unreferenced artifact files are excluded from valid support behavior or fail closed.
- Quarantine preserves `quarantine_reason` and safe refs while excluding the bundle from valid listing/indexing.
- Superseded and deleted_tombstone bundles are retained but excluded from default valid listing/indexing.
- Duplicate identical writes remain deterministic and conflicting duplicate writes fail closed.
- `compute_raw_artifact_bundle_hash` remains deterministic with canonical JSON/sorted keys and changes when artifact refs/content metadata change.

### Boundary Confirmation

- No routes added.
- No frontend implementation code changes.
- No package/dependency changes.
- No runtime extraction.
- No BookNLP/spaCy install/run/import.
- No model/Ollama calls.
- No NCP/Subtxt/dramatica-flow runtime.
- No apply-promotion changes.
- No approved memory/canon mutation.
- No candidate/review workflow creation.
- No generated prose.
- No training/JSONL/dataset/model artifacts.
- No source-cache/generated context artifacts staged.

### Future Guidance

- `PHASE8-IMPL-018-T006` is ready/active next and remains limited to safety regression coverage proving raw artifacts remain support data only, path-safe, fail-closed, non-canon, non-candidate, non-training-data, no_runtime_extraction, no_booknlp_spacy_runtime, no_model_calls, no_apply_promotion, no_memory_canon_mutation, and no_generated_prose.
- `PHASE8-IMPL-018-T007` remains planned.
- `PHASE8-IMPL-019` through `PHASE8-IMPL-022` remain future MVP-required parents.
- Fine-tuning remains deferred after MVP.
- Generated prose/prose-production paths remain permanently forbidden.

# PHASE8-IMPL-018-T004 Minimal Backend Raw Artifact Persistence Helper

### Result

- Result: PASS.
- Scope: minimal backend raw artifact persistence helper plus docs/status alignment only.
- Parent task: `PHASE8-IMPL-018` - Raw artifact persistence implementation and project-local extraction artifact lifecycle.
- Completed child recorded: `PHASE8-IMPL-018-T004` - Minimal backend raw artifact persistence helper implementation.
- Backend helper: `backend/story_knowledge/raw_artifacts.py`.
- Contract test: `tests/test_writer_assistant_core_raw_artifacts_contract.py` PASS.
- Active parent: `PHASE8-IMPL-018` MVP-required.
- Active/ready next child: `PHASE8-IMPL-018-T005` - Raw artifact bundle/index lifecycle and provenance linkage.
- Planned children: `PHASE8-IMPL-018-T006` and `PHASE8-IMPL-018-T007`.
- Future MVP-required parents: `PHASE8-IMPL-019`, `PHASE8-IMPL-020`, `PHASE8-IMPL-021`, and `PHASE8-IMPL-022`.
- Prior completed child: `PHASE8-IMPL-018-T003` complete/PASS and committed as expected-red contract handoff.
- Prior parent: `PHASE8-IMPL-017` remains complete/PASS through `PHASE8-IMPL-017-T007`.
- No context tools were run inside T004. Generated context artifacts remain evidence only, not roadmap truth or task completion.

### Files Changed

- Created: `backend/story_knowledge/raw_artifacts.py`
- Updated: `docs/roadmap/tasks/PHASE8-IMPL-018.md`
- Updated: `docs/roadmap/inventory/PHASE8-IMPL-018.md`
- Updated: `docs/roadmap/enrichment/PHASE8-IMPL-018.enrichment.json`
- Updated: `docs/roadmap/implementation_status.md`
- Updated: `docs/roadmap/roadmap_index.yaml`
- Updated: `docs/roadmap/task_backlog.md`
- Updated: `docs/roadmap/phase_map.md`
- Updated: `docs/roadmap/validation/latest_roadmap_validation.md`
- Updated: `docs/roadmap/decision_log.md`
- Updated: `docs/roadmap/risk_register.md`
- Updated: `docs/roadmap/open_questions.md`

### Backend Helper Summary

- `backend/story_knowledge/raw_artifacts.py` implements `validate_raw_artifact_manifest`, `build_raw_artifact_manifest`, `validate_raw_artifact_file_ref`, `raw_artifact_bundle_storage_dir`, `raw_artifact_manifest_path`, `raw_artifact_index_path`, `write_raw_artifact_bundle`, `read_raw_artifact_manifest`, `read_raw_artifact_file`, `list_raw_artifact_bundles`, `rebuild_raw_artifact_index`, `quarantine_raw_artifact_bundle`, and `compute_raw_artifact_bundle_hash`.
- Manifest validation is fail-closed and requires required fields, allowed lifecycle statuses, source/evidence/provenance/source locator linkage for valid bundles, manifest/content hash presence, boundary flags, and no-runtime/no-prose/no-training/no-apply-promotion/no-memory-canon mutation confirmations.
- Artifact file validation allows support data artifact types only, requires path-safe `relative_path`, `artifact_file_id`, `sha256`, media/encoding/count/schema/parser fields, evidence/provenance/source locator refs, and boundary flags.
- Path helpers keep storage under `projects/{project_id}/writer_assistant/raw_artifacts/{raw_artifact_bundle_id}/` with deterministic `manifest.json`, `artifacts/`, `indexes/`, and `quarantine/` layout.
- Write/read/list/index/quarantine/hash helpers validate before write, avoid partial writes on validation failure, read only manifest-referenced files, exclude quarantined/rejected bundles by default, build rebuildable support-data indexes, record quarantine reasons, and compute deterministic hashes.
- Duplicate bundle ids are deterministic: identical manifests return the same result; conflicting manifests fail closed.

### Boundary Confirmation

- No routes added.
- No frontend implementation code changes.
- No package/dependency changes.
- No runtime extraction.
- No BookNLP/spaCy install/run/import.
- No model/Ollama calls.
- No NCP/Subtxt/dramatica-flow runtime.
- No apply-promotion changes.
- No approved memory/canon mutation.
- No candidate/review workflow creation.
- No generated prose.
- No training/JSONL/dataset/model artifacts.
- No source-cache/generated context artifacts staged.

### Future Guidance

- `PHASE8-IMPL-018-T005` is ready/active next and remains limited to raw artifact bundle/index lifecycle and provenance linkage.
- `PHASE8-IMPL-018-T006` through `PHASE8-IMPL-018-T007` remain planned.
- `PHASE8-IMPL-019` through `PHASE8-IMPL-022` remain future MVP-required parents.
- Fine-tuning remains deferred after MVP.
- Generated prose/prose-production paths remain permanently forbidden.

## PHASE8-UX-001 - Master Plan UX / Navigation Proposal

Validation status: Planned / pending execution.

Expected checks before and after the docs-only UX proposal task:

- `python3 scripts/check_enrichment.py`
- `python3 scripts/validate_roadmap.py`
- `git diff --check`
- `git status --short --branch`

Expected outputs:

- `docs/roadmap/ux/PHASE8-UX-001-master-plan-ux-navigation-proposal.md`
- `docs/roadmap/ux/PHASE8-UX-001-impeccable-ui-ux-qa-workflow.md`

Generated context evidence, if collected, must remain under `.codex-context/PHASE8-UX-001/` and must not be staged.
# PHASE8-UX-002-T001 Parent Publication Validation

`PHASE8-UX-002 - MVP acceptance UI completion and route wiring` is published as the active MVP-first UI parent. `PHASE8-UX-002-T001` is complete/PASS as docs/status/planning parent publication only.

Roadmap status: owner acceptance remains pending; MVP is not complete. Latest owner acceptance evidence remains `MANUAL_REVIEW_REQUIRED` due to missing UI/workflow surfaces.

Publication artifacts:

- `docs/roadmap/tasks/PHASE8-UX-002.md`
- `docs/roadmap/inventory/PHASE8-UX-002.md`
- `docs/roadmap/enrichment/PHASE8-UX-002.enrichment.json`

Deferred research status: external SaaS investigation, Dramatica/current-platform investigation, controlled external experiments, Browsertrix, Crawlee, Stagehand, Playwright against external SaaS, and authorized non-black-box external reference collection are post-MVP/deferred. `PHASE8-UX-002-T002A` is post-MVP/deferred only and is not part of the active MVP child sequence.

Boundary validation: no frontend/backend/tests/package changes, no crawler scripts, no raw captures, no `.external_sources`, no context bundle, no model calls, no generated prose, no hidden algorithm claims from black-box observation, no copied proprietary content, no canon/memory mutation, no apply-promotion shortcut, and no staging/commit/push.
