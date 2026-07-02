# PHASE8-UX-002 Prepublication Reference Research Boundary

## Purpose

Crawler/browser-automation reference research is a planning input for `PHASE8-UX-002`. It may inform route, workflow, and UI acceptance matrix decisions before implementation starts.

This boundary does not implement UI, create roadmap truth by itself, or make Dramatica or any external SaaS reference a product requirement. External references may be used only as summarized design-pattern input for owner review.

## Current Acceptance Evidence Summary

Recent owner acceptance evidence shows the Cyber Detective owner acceptance harness reached `SCRIPT_EXIT=0`, but the final automated decision remains `MANUAL_REVIEW_REQUIRED`. MVP owner acceptance remains pending and MVP is not complete.

Key UI gaps feeding `PHASE8-UX-002`:

- Missing owner-authored scene/source create, import, and select UI.
- Story Check requires a selected source.
- No safe no-prose prompt route exists for refusal/fail-closed browser checks.
- Notes/Materials save-reload proof is not fully UI-exposed for owner acceptance.
- Runtime extraction/raw artifact evidence UI is missing.
- Apply-promotion fixture and explicit owner-confirmation proof are missing.
- NCP/Subtxt/dramatica-flow are not UI-exposed and need a backend/helper-only versus analysis-label/status decision.

This is why `PHASE8-UX-002` is needed: the remaining acceptance blocker is missing safe UI/workflow surface evidence, not test tooling.

## Tool Roles

### Playwright

- Manual login/session capture.
- Codegen for recording safe workflows.
- Screenshots.
- Trace Viewer for actions, DOM snapshots, console logs, screenshots/screencasts, and network requests.
- Safe high-level network observation for route/workflow mapping.
- Auth state is local-only and must not be committed.

### Browsertrix Crawler

- High-fidelity browser-based visual crawl.
- Authenticated browser profile support.
- Screenshots, screencasting, WACZ, and replayable archive output.
- Use only for safe page inventory and visual reference capture.

### Crawlee + PlaywrightCrawler

- Structured crawler for JavaScript-heavy pages.
- Persistent request queues.
- Extract page metadata into JSONL/Markdown.
- Capture safe UI metadata: headings, nav, buttons, links, forms, tables, panels, modals, screenshots, and safe route/network summaries.
- Do not dump raw page bodies or proprietary text.

### Stagehand

- Optional AI-assisted observe/extract helper.
- Use only for controlled page summaries and action discovery.
- Do not use autonomous agent mode for broad uncontrolled actions.
- Do not allow destructive, mutating, publishing, exporting, purchasing, or data-changing actions.

## Safe Phased Workflow

- Phase A: manual authenticated walkthrough.
- Phase B: screenshot and trace capture.
- Phase C: safe page inventory.
- Phase D: structured UI/workflow extraction.
- Phase E: summarization into UX research docs.
- Phase F: mapping to `PHASE8-UX-002` acceptance gaps.

## Raw Untracked Output Structure

Planned raw capture output must remain untracked and must not be created by this prepublication task:

```text
.external_sources/dramatica-ui-reference/
  README.md
  SCOPE.md
  DO_NOT_COMMIT.md
  auth/
    .gitkeep
    README-auth-state-is-local-only.md
  playwright/
    screenshots/
    traces/
    codegen-drafts/
    workflow-notes/
    safe-network-summaries/
  browsertrix/
    profiles/
    wacz/
    screenshots/
    screencasts/
    crawl-reports/
    replay-notes/
  crawlee/
    storage/
    pages.jsonl
    workflows.jsonl
    components.jsonl
    route-map.jsonl
    safe-network-summary.jsonl
  stagehand/
    observed-actions.jsonl
    extracted-page-summaries.jsonl
    rejected-agent-runs.md
  summaries/
    page-inventory-draft.md
    workflow-inventory-draft.md
    pattern-map-draft.md
```

## Committed Docs Output Structure

Planned committed output for a future approved research spike:

```text
docs/roadmap/ux/
  PHASE8-UX-002-mvp-acceptance-ui-completion.md
  PHASE8-UX-002-ui-acceptance-matrix.md
  PHASE8-UX-002-reference-research-summary.md
  PHASE8-UX-002-pattern-map.md
  PHASE8-UX-002-route-workflow-gap-map.md
  PHASE8-UX-002-rejected-patterns.md
  PHASE8-UX-002-research-boundary-decision.md
```

## Safe Page Capture Schema

- URL.
- Title.
- Route or page label.
- Visible nav items.
- Headings.
- Buttons.
- Forms.
- Panels/cards.
- Tables/lists.
- Dialogs/modals.
- Screenshots.
- Safe network summary.
- Workflow notes.
- Patterns to borrow.
- Patterns to reject.
- Mapping to our UI.

## Safe Workflow Schema

- Workflow name.
- Entry point.
- Steps.
- User action.
- Visible result.
- Screenshot.
- Safe network observations.
- UI state changes.
- Warnings/modals.
- Patterns to borrow.
- Patterns to reject.
- `PHASE8-UX-002` gap mapped.

## Black-Box Controlled-Experiment Methodology

This is black-box UX/workflow inference only. Hidden algorithms, prompts, model weights, model routing, ranking logic, or proprietary implementation details can be known only through explicit authorized disclosure, official documentation, owner-provided evidence, or other lawful non-black-box evidence. They must not be claimed as known from black-box controlled experiments alone.

`PHASE8-UX` may retrieve and summarize authorized non-black-box reference information when the owner has authorization to access or provide it. This includes official documentation, owner-provided evidence, authorized disclosures, and other lawful reference materials about algorithms, prompts, model routing, ranking logic, workflow rules, or implementation details. That information still needs to be collected, provenance-labeled, summarized, and reviewed before it can be used as `PHASE8-UX` reference input.

The research may record only observed UI behavior, safe route/network metadata, and cautious inferred dependencies. Every dependency relationship must be labeled with one of these confidence values:

- `observed`
- `inferred`
- `unknown`

Inferred dependencies are hypotheses, not truth. They do not become product requirements by themselves. External SaaS behavior must not be copied or cloned, and captured output must not be used for training or fine-tuning.

Authorized non-black-box evidence is reference material, not automatic roadmap truth. It may inform UI/workflow planning only after it is summarized in committed research docs and mapped to our app's analysis-only, candidate-first, evidence/provenance-backed, owner-controlled boundaries.

Controlled experiment plan:

- Create or use a small owner-controlled test story in the external SaaS account.
- Change exactly one variable at a time.
- Capture the before state.
- Make the single change.
- Capture the after state.
- Record which UI panels changed.
- Record which buttons or controls became enabled or disabled.
- Record which workflow states changed.
- Record which warnings or modals appeared or disappeared.
- Record safe route/network observations at route-shape/status-class level only.
- Record whether suggestions, memory/reference chips, analysis labels, or reports changed at a high level.
- Record alternative explanations such as cache, session history, background recomputation, prior state, or account configuration.
- Repeat over time to build an inferred dependency graph.

Example variables:

- Project title.
- Story premise.
- Protagonist or character name.
- Goal, problem, conflict, or theme field.
- Genre, format, or length field.
- Selected storyform or story point field.
- Scene/source content field.
- Analysis option or toggle.
- Review or candidate status.
- Memory/reference toggle if exposed.

Allowed observation examples:

- Panel X updated.
- Button Y became enabled or disabled.
- Report Z changed label or state.
- Route shape `/api/...` was called.
- Suggestion category changed at a high level.
- Memory/reference chip appeared or disappeared.
- Warning or validation state appeared.

Forbidden observation examples:

- Any claim that hidden reasoning, model routing, ranking logic, prompt design, model weights, or proprietary implementation details are known solely from black-box observation.
- Any copied external platform text, output body, API payload, screenshot, trace, HAR/WARC/WACZ, auth state, browser profile, or raw scraped content in committed docs.
- Any claim that external SaaS behavior is a requirement for our app.
- Any use of captured output for training or fine-tuning.

Confidence legend:

- `observed`: directly visible in UI/network metadata under a controlled one-variable change.
- `inferred`: reasonable hypothesis supported by repeated observations but not directly proven.
- `unknown`: insufficient evidence, confounded result, or hidden behavior cannot be observed.

The inferred dependency graph is a hypothesis map only. It can inform future `PHASE8-UX-002-T002A` research summaries and `T002` acceptance-matrix thinking, but it is not roadmap truth, product architecture, canon, or a product requirement source.

## Explicit Exclusions

- Account settings, billing, subscription, invoices, and license details.
- Exports/downloads of proprietary story datasets.
- Other users' content.
- Sample projects not licensed/reusable.
- Direct scraping of educational/proprietary text.
- AI-generated outputs copied from the reference platform.
- Private notes, uploads, and account identifiers.
- Raw HAR bodies, cookies, `localStorage`, `sessionStorage`, and auth state.
- Browser profiles.
- WACZ/WARC/HAR/traces in Git.
- Destructive actions: delete, publish, export, invite, purchase, submit support requests, and change settings.

## Mapping to Our Planned UI Surfaces

- Project Overview.
- Scene/source workflow.
- Story Check.
- OMI.
- Review Queue.
- Candidate Detail.
- Apply-Promotion Confirmation.
- Approved Memory/Canon.
- Raw Artifact Viewer.
- Future NCP/Subtxt/dramatica-flow analysis lenses.

## Proposed Placement in PHASE8-UX-002

- `PHASE8-UX-002-T001` — Parent publication.
- `PHASE8-UX-002-T002` — UI acceptance matrix + route/workflow decision.
- `PHASE8-UX-002-T002A` — External SaaS UI reference research spike.
- `PHASE8-UX-002-T003` — Expected-red tests for source/Story Check/no-prose UI.
- `PHASE8-UX-002-T004` — Implement owner-authored source/scene UI.
- `PHASE8-UX-002-T005` — Implement Story Check diagnostic/no-prose evidence UI.
- `PHASE8-UX-002-T006` — Implement Notes/Materials + runtime/review evidence UI.
- `PHASE8-UX-002-T007` — Closeout + rerun owner acceptance harness.

## Proposed Research Spike Name

`PHASE8-UX-002-T002A` — External SaaS UI reference research spike.

## Future Codex/Aider Boundary

Use this concise boundary for any future research prompt:

```text
Research/docs only.
No product UI implementation.
No crawler scripts unless explicitly approved later.
No dependencies.
No raw captures committed.
No copying proprietary UI, code, or content.
No private-content crawling.
No model training.
Committed output is summarized UX docs only.
```

## Research Safety Rules

- Use only the owner's authenticated account.
- Do not bypass login, rate limits, CAPTCHAs, access controls, or terms.
- Do not crawl other users' private content.
- Do not download proprietary datasets for redistribution.
- Do not train models on captured platform content.
- Do not copy proprietary code.
- Do not commit auth state, cookies, browser profiles, traces, screenshots, HAR/WARC/WACZ, raw scraped content, or copied platform text.
- Store raw capture output only under an untracked path such as `.external_sources/dramatica-ui-reference/`.
- Commit only summarized research docs.
- Use captured material only to summarize design patterns, workflows, and inspiration.
- Keep all research separate from product implementation.
- Do not implement `PHASE8-UX-002` UI yet.

## Product Boundaries

- Analysis-only.
- Candidate-first.
- Evidence/provenance-backed.
- Owner-controlled.
- Owner-authored prose storage/editing is allowed.
- AI-generated prose is permanently forbidden.
- The app must never generate, rewrite, continue, imitate, polish, improve, expand, outline, draft, revise, or produce story prose.
- Queue presence is not approval.
- Confidence is not truth.
- Candidate persistence is not canon.
- Raw artifacts are support data, not canon.
- Apply-promotion must be explicit, audited, owner-confirmed, and separate from extraction, queue state, confidence, and candidate persistence.
