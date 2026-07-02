# PHASE8-UX-002-T002 - UI Acceptance Matrix + Route/Workflow Decision

## Status

- Result: complete/PASS pending validation.
- Scope: docs/decision/planning only.
- Parent: `PHASE8-UX-002 - MVP acceptance UI completion and route wiring`.
- No frontend implementation, backend implementation, tests, route/API changes, product behavior changes, context-tool runs, crawler runs, raw captures, model calls, generated prose, canon/memory mutation, candidate creation, apply-promotion shortcut, staging, commit, or push are included in T002.

## Current Evidence Basis

- `PHASE8-UX-002-T001` published `PHASE8-UX-002` as the active MVP-first UX parent.
- Latest owner acceptance evidence reached `SCRIPT_EXIT=0`, but the final automated decision remains `MANUAL_REVIEW_REQUIRED`.
- MVP owner acceptance remains pending.
- MVP is not complete.
- The blocker is missing browser-visible UI/workflow surfaces in our own app.

## SaaS / Research Deferral

- External SaaS investigation is post-MVP/deferred.
- Dramatica/current-platform investigation is post-MVP/deferred.
- Browsertrix, Crawlee, Stagehand, and Playwright against external SaaS are not part of T002 or the active MVP UI fix path.
- Controlled external experiments and authorized non-black-box external reference collection are post-MVP/deferred.
- `PHASE8-UX-002-T002A` must not be active in the MVP child sequence.

## MVP-Required UI Surfaces

### A. Owner-Authored Scene/Source Create/Import/Select Workflow

- User-visible goal: owner can create, import, save, reload, and select an owner-authored scene/source for the active project before analysis.
- Required browser-visible state: selected project, selected source identity, source type, owner-authored/owner-provided label, saved/reloaded state, and current selection used by Story Check.
- Required disabled/fail-closed state: Story Check and any source-dependent analysis controls are disabled or unavailable until a valid owner-authored source is selected.
- Required project-scoping rule: source lists, selections, saved bodies, and reload evidence must be scoped to the active project only.
- Required provenance/evidence/source-state label: `owner-authored source`, `project-scoped`, `selected source`, and save/reload status.
- Required owner-control rule: source creation/import and selection are explicit owner actions.
- Forbidden behavior: generated source text, automatic canon/memory mutation, hidden source selection, cross-project leakage, training data creation, candidate creation, or promotion.
- Acceptance evidence expected from future tests: browser creates/imports source, selects it, reloads it, shows project-scoped source state, and keeps Story Check disabled until selection exists.
- MVP implementation classification: frontend-first; backend/API-assisted if existing scene/source routes cannot create/import/select project-scoped sources safely.
- Future owner task: `PHASE8-UX-002-T004`.

### B. Story Check Diagnostic-Only UI Against Selected Owner-Authored Source

- User-visible goal: owner runs Story Check only against the selected owner-authored source and sees diagnostic/candidate-first output.
- Required browser-visible state: selected source label, run control, pending/result/error state, diagnostic-only result sections, evidence/provenance/source labels where available, and confidence-is-not-truth label.
- Required disabled/fail-closed state: run control is disabled/unavailable without selected source or if backend/model state is unavailable.
- Required project-scoping rule: request and visible result must belong to the active project and selected source only.
- Required provenance/evidence/source-state label: selected source ID/title, owner-authored/owner-provided status, diagnostic-only, candidate-first, model output is not canon.
- Required owner-control rule: Story Check runs only after owner selects source and clicks the visible app control.
- Forbidden behavior: generated prose, rewrite, continuation, outline/draft/polish/improve/expand/imitate controls, canon/memory mutation, apply-promotion, or raw model output as truth.
- Acceptance evidence expected from future tests: disabled state without source, diagnostic-only result with selected source, no generated prose markers, and non-canon labels.
- MVP implementation classification: frontend-first with existing Story Check route if sufficient; backend/API-assisted later if route cannot bind selected source safely or expose unavailable/fail-closed state.
- Future owner task: `PHASE8-UX-002-T005`.

### C. No-Prose Refusal / Fail-Closed UI

- User-visible goal: forbidden prose-production intents are visibly refused, blocked, redirected to diagnostics, unavailable, or fail-closed.
- Required browser-visible state: refusal/fail-closed result for rewrite, continue, outline, draft, polish, improve, expand, imitate, and generated prose intents.
- Required disabled/fail-closed state: no arbitrary prompt route may become a prose-generation route; unsafe paths return the standard no-prose boundary.
- Required project-scoping rule: any negative-path proof must be active-project scoped and must not mutate source/project state.
- Required provenance/evidence/source-state label: no-prose boundary, analysis-only, no project mutation, no generated story prose.
- Required owner-control rule: owner can observe the refusal path without triggering hidden generation.
- Forbidden behavior: submitting unsafe prompts to a generation endpoint, generating or rewriting story prose, storing generated text, candidates, canon, memory, or training artifacts.
- Acceptance evidence expected from future tests: browser-visible refusal/fail-closed states for all forbidden intent classes.
- MVP implementation classification: frontend-only if the UI exposes safe labels/status/refusal states; backend/API-assisted only if a safe diagnostic input route is explicitly scoped later.
- Future owner task: `PHASE8-UX-002-T005`.

### D. Notes/Materials Project-Scoped Create/Save/Reload Proof

- User-visible goal: owner can create, edit, save, reload, and reselect notes/materials as owner-authored or owner-provided project material.
- Required browser-visible state: note/material list, selected item, body editor, saved state, reload proof, and active project label.
- Required disabled/fail-closed state: no model analysis, extraction, summary, promotion, or canon mutation occurs from note/material creation or save.
- Required project-scoping rule: notes/materials are stored and listed only for the active project.
- Required provenance/evidence/source-state label: owner-authored note or owner-provided material, project-scoped, not canon by default.
- Required owner-control rule: create/save/reload are explicit owner actions.
- Forbidden behavior: generated notes/materials, automatic summaries, automatic extraction, candidate creation, canon/memory mutation, training artifacts, or cross-project leakage.
- Acceptance evidence expected from future tests: browser creates/saves/reloads note and material, switches projects without leakage, and shows owner-authored/provided labels.
- MVP implementation classification: frontend-first using existing notes/materials routes if sufficient; backend/API-assisted later if create/list/reload support is incomplete.
- Future owner task: `PHASE8-UX-002-T006`.

### E. Runtime Extraction / Raw Artifact Unavailable or Read-Only Evidence UI

- User-visible goal: owner can see runtime/raw artifact status without raw artifacts becoming canon, candidates, or training data.
- Required browser-visible state: unavailable/fail-closed runtime status or read-only raw artifact evidence panel, with support-data-only labels.
- Required disabled/fail-closed state: runtime execution controls remain unavailable/fail-closed unless separately authorized; raw bodies are not editable as canon.
- Required project-scoping rule: runtime/raw artifact status and read-only evidence are active-project scoped.
- Required provenance/evidence/source-state label: support data only, raw artifacts are not canon, source/evidence/provenance/source-locator refs when available.
- Required owner-control rule: owner can inspect evidence/status only; no hidden runtime execution occurs from inspection.
- Forbidden behavior: executing BookNLP/spaCy/NCP/Subtxt/dramatica-flow in T002/T003, raw artifact promotion, candidate creation, memory/canon mutation, generated prose, or training artifacts.
- Acceptance evidence expected from future tests: visible unavailable/read-only state, support-data labels, and no mutation from inspection.
- MVP implementation classification: UI-only labels/status are acceptable if route support is absent; read-only backend/API-assisted evidence may be added later if existing raw artifact routes are sufficient or explicitly scoped.
- Future owner task: `PHASE8-UX-002-T006`.

### F. Review / Apply-Promotion Confirmation and Audit Evidence UI

- User-visible goal: owner can see review/apply-promotion status, explicit confirmation requirements, audit evidence, and failed/rejected unchanged approved memory/canon behavior.
- Required browser-visible state: review queue item or fixture state, candidate-only/non-canon label, explicit confirmation surface, audit details, and approved memory/canon unchanged evidence for failure/rejection.
- Required disabled/fail-closed state: apply-promotion is unavailable/fail-closed without valid candidate, evidence/provenance/source locators, owner confirmation, and allowed destination.
- Required project-scoping rule: review entries, promotion requests, audit records, and approved memory/canon views are active-project scoped.
- Required provenance/evidence/source-state label: candidate persistence is not canon, queue presence is not approval, confidence is not truth, apply-promotion is explicit/audited/owner-confirmed.
- Required owner-control rule: owner confirmation is mandatory and separate from extraction, queue state, confidence, and candidate persistence.
- Forbidden behavior: automatic promotion, hidden canon/memory mutation, treating queue/candidate/model/extraction/raw artifact state as approval, generated prose, or training artifacts.
- Acceptance evidence expected from future tests: visible explicit confirmation path, audit details, fail-closed invalid promotion, and unchanged approved memory/canon after rejection/failure.
- MVP implementation classification: frontend/API-assisted where existing review/apply-promotion routes are sufficient; UI-only labels are acceptable for unavailable/empty fixture states.
- Future owner task: `PHASE8-UX-002-T006`.

### G. NCP/Subtxt/Dramatica-Flow Exposure Decision

- User-visible goal: owner can understand whether analysis runtimes are exposed in MVP and that they are analysis-only.
- Required browser-visible state: `NOT_EXPOSED` or unavailable labels for runtime execution, plus optional analysis-lens labels/status only.
- Required disabled/fail-closed state: no runtime execution, no outline/generation/revision controls, no automatic canon, and no hidden model/tool invocation from labels.
- Required project-scoping rule: any visible status label belongs to the active project/workflow context and does not imply project truth.
- Required provenance/evidence/source-state label: NCP is structured context interchange only; Subtxt is rubric/diagnostic guidance only; dramatica-flow is audited allowlist only.
- Required owner-control rule: owner can see status/availability; runtime execution requires a separately scoped future task.
- Forbidden behavior: executing NCP/Subtxt/dramatica-flow, cloning external repos, installing dependencies, generating prose/outlines, treating labels as truth, or mutating memory/canon.
- Acceptance evidence expected from future tests: visible `NOT_EXPOSED`/unavailable or label-only behavior and no runtime execution path.
- MVP implementation classification: decision-only/UI-only labels for MVP.
- Future owner task: `PHASE8-UX-002-T007` for final closeout verification; T003 records expected-red behavior and T006 may expose the label/status surface if needed.

## Route / Workflow Decision

- Existing scene/source/project routes should be used for owner-authored source create/import/select workflows if they can provide project-scoped create/list/read/update/select behavior without hidden canon/candidate/training side effects.
- Existing notes/materials/project routes should be used for Notes/Materials create/save/reload proof if they can create/list/read/update active-project items and preserve owner-authored/provided labels.
- Existing Story Check route should be used only after a selected owner-authored source is bound to the request and the UI can show disabled/unavailable/fail-closed state without source.
- Existing review queue and apply-promotion routes should be used for review/apply-promotion evidence if they can expose candidate-only review state, explicit owner confirmation, audit details, and failed/rejected unchanged memory/canon evidence.
- Runtime/raw artifact workflows may need API support later if existing routes do not expose read-only manifest/status/evidence or unavailable/fail-closed state.
- Story Check selected-source binding may need API support later if the current route cannot safely associate analysis with the selected owner-authored source.
- Notes/materials create/import may need API support later if existing routes require preexisting IDs or cannot show create/reload proof.
- Source/scene import may need API support later if current routes support only reading/updating existing scene IDs.
- Workflows must fail closed until route support exists for selected source binding, safe no-prose refusal paths, runtime/raw artifact read-only evidence, and valid apply-promotion confirmation/audit state.
- UI-only labels/status surfaces are acceptable for no-prose boundary labels, unavailable runtime status, `NOT_EXPOSED` analysis runtime status, support-data-only raw artifact warnings, candidate/non-canon warnings, and confidence-is-not-truth labels.
- Persisted evidence or audit records are required for saved owner-authored sources, notes/materials save/reload proof, raw artifact manifests if exposed as read-only evidence, review queue entries if used, promotion audit records if apply-promotion is exercised, and approved memory/canon unchanged evidence.
- `NCP/Subtxt/dramatica-flow` runtime execution remains `NOT_EXPOSED` and acceptable for MVP if visible labels/status make the analysis-only boundary clear.

## Analysis Runtime Exposure Decision

MVP decision: explicit split.

- Selected labels may be browser-visible: NCP as structured context interchange only, Subtxt as rubric/diagnostic guidance only, and dramatica-flow as audited allowlist only.
- Runtime execution is not exposed in the active MVP UI acceptance fix path.
- Visible status may say `NOT_EXPOSED`, `Unavailable`, or `Analysis runtime labels only`.
- This decision does not execute NCP, Subtxt, or dramatica-flow.
- This decision does not add generated prose, outline, rewrite, continuation, draft, polish, improve, expand, imitate, revise, or story-prose-production behavior.

## PHASE8-UX-002-T003 Expected-Red Test Scope

`PHASE8-UX-002-T003` should add expected-red browser/source tests for:

- Source/scene create/import/select browser-visible workflow.
- Story Check disabled without selected owner-authored source.
- Story Check diagnostic-only result state with selected source.
- No-prose refusal/fail-closed path for forbidden intents.
- Notes/Materials create/save/reload project-scoped proof.
- Runtime/raw artifact unavailable/read-only evidence surface.
- Review/apply-promotion confirmation and audit evidence surface.
- NCP/Subtxt/dramatica-flow exposure decision behavior.

## T004 / T005 / T006 Implementation Split

- `PHASE8-UX-002-T004`: owner-authored source/scene create/import/select UI.
- `PHASE8-UX-002-T005`: Story Check diagnostic-only/no-prose evidence UI.
- `PHASE8-UX-002-T006`: Notes/Materials plus runtime/review evidence UI.
- `PHASE8-UX-002-T006` may be split later if the Notes/Materials, runtime/raw artifact, and review/apply-promotion evidence surfaces are too large for one safe implementation slice.

## Non-Goals

- No implementation in T002.
- No tests in T002.
- No route/API changes in T002.
- No SaaS research.
- No context tools.
- No generated prose.
- No MVP completion claim.
