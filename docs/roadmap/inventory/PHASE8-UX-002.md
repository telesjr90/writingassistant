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

The owner acceptance harness reached `SCRIPT_EXIT=0`, but final automated decision remains `MANUAL_REVIEW_REQUIRED`. Owner acceptance remains pending and MVP is not complete.

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

## Known Acceptance Gaps

- Missing browser UI to create/import/select owner-authored scene/source for the Cyber Detective fixture project.
- Story Check cannot be accepted until it runs against a selected owner-authored source and returns diagnostic-only output.
- Missing-source Story Check path needs disabled/fail-closed browser evidence.
- No safe arbitrary prompt route may be used as a no-prose test path.
- Browser-testable refusal/fail-closed behavior is needed for rewrite, continue, outline, draft, polish, improve, expand, imitate, and generate prose requests.
- Notes/Materials create/save/reload and project isolation proof need browser evidence.
- Runtime extraction/raw artifact states need UI-visible unavailable/fail-closed or read-only evidence.
- Review/apply-promotion evidence needs a safe fixture, explicit owner confirmation, visible audit details, and proof that failed/rejected promotion leaves approved memory/canon unchanged.
- NCP/Subtxt/dramatica-flow need a UI-facing versus backend/helper-only exposure decision; `NOT_EXPOSED` may be acceptable for MVP owner acceptance if documented.

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
