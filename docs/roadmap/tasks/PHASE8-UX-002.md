# PHASE8-UX-002 - MVP acceptance UI completion and route wiring

## Status

`PHASE8-UX-002` is published as the active MVP-first UX parent for completing the missing browser-testable UI and workflow surfaces required before owner MVP acceptance.

`PHASE8-UX-002-T001` is complete/PASS as docs/status/planning parent publication only. No UI, routes, tests, crawlers, dependencies, raw captures, context artifacts, `.external_sources`, frontend code, backend code, product behavior, model calls, canon/memory mutation, candidate creation, generated prose, or apply-promotion shortcut were created by T001.

`PHASE8-UX-002-T002` is complete/PASS as docs/decision/planning only. T002 created the UI acceptance matrix and route/workflow decision, recorded browser-testable MVP UI surfaces, preserved SaaS/research deferral, and identified `PHASE8-UX-002-T003` as the next child. No product implementation occurred.

MVP owner acceptance remains pending. MVP is not complete.

## Purpose

Publish `PHASE8-UX-002` as the parent for making the app's own missing MVP acceptance UI/workflow surfaces visible, testable in a browser, and aligned with the owner acceptance checklist.

The parent exists because latest owner acceptance evidence reached `SCRIPT_EXIT=0` but the final automated decision remains `MANUAL_REVIEW_REQUIRED` due to missing browser-visible UI/workflow surfaces. The blocker is not external SaaS research. The blocker is our app's incomplete owner-acceptance UI path.

## Scope

This parent covers planning and sequencing for:

- Owner-authored scene/source create, import, select, save, reload, and project-scoped selection workflows.
- Story Check diagnostic-only UI against a selected owner-authored source.
- Browser-testable no-prose refusal and fail-closed UI paths.
- Project-scoped Notes/Materials save-reload proof.
- Runtime extraction and raw artifact unavailable/fail-closed/read-only evidence states.
- Review queue and apply-promotion evidence UI, including explicit owner confirmation and visible audit details.
- Analysis runtime exposure decision for NCP, Subtxt, and dramatica-flow.

## Product Boundaries

- Analysis-only.
- Candidate-first.
- Evidence/provenance-backed.
- Owner-controlled.
- Owner-authored prose storage/editing is allowed.
- AI-generated prose is permanently forbidden.
- No generated story prose.
- No rewrite, continue, imitate, polish, improve, expand, outline, draft, revise, or story-prose-production controls.
- Queue presence is not approval.
- Confidence is not truth.
- Candidate persistence is not canon.
- Raw artifacts are support data, not canon.
- Apply-promotion must be explicit, audited, owner-confirmed, and separate from extraction, queue state, confidence, and candidate persistence.

## Current Evidence Summary

- `PHASE8-IMPL-022` is complete/PASS as the end-to-end MVP usability validation parent.
- Project isolation browser evidence now passes.
- The MVP owner acceptance harness exists and runs.
- The Cyber Detective owner acceptance fixture exists and was committed.
- Latest owner acceptance evidence reached `SCRIPT_EXIT=0`, but final automated decision remains `MANUAL_REVIEW_REQUIRED`.
- Owner acceptance remains pending.
- MVP is not complete.
- `PHASE8-UX-001` produced the UX/navigation proposal and Impeccable UI/UX QA workflow.
- `PHASE8-UX-002-PRE-T001` is complete/PASS as prepublication reference research boundary.
- `PHASE8-UX-002-PRE-T001-BLACKBOX` is complete/PASS as black-box controlled-experiment methodology addendum.
- `PHASE8-UX-002-PRE-T001-DEFER-SAAS` is complete/PASS and records that all external SaaS investigation is deferred until after MVP UI fixes and MVP owner acceptance.

## Missing UI / Workflow Surfaces

### 1. Owner-authored scene/source workflow

- Create/import/select owner-authored scene/source from browser UI.
- Source must be project-scoped.
- Source must be owner-authored or owner-provided.
- Source must not become canon, memory, training data, or truth automatically.
- Story Check must not run without a selected owner-authored source.

### 2. Story Check diagnostic-only UI

- Story Check must run against a selected owner-authored source.
- Output must be diagnostic/analysis-only.
- Confidence is not truth.
- Model output is not canon.
- No generated prose.
- Missing source must produce disabled/fail-closed UI, not ambiguous behavior.

### 3. No-prose negative-path UI

- Browser-testable refusal/fail-closed behavior for rewrite, continue, outline, draft, polish, improve, expand, imitate, and generate prose.
- No safe arbitrary prompt route may become a prose-generation route.

### 4. Notes/Materials project-scoped UI proof

- Create/save/reload owner-authored notes and materials.
- Confirm project isolation across projects.
- Notes/materials remain owner-authored planning/source material, not canon automatically.

### 5. Runtime extraction / raw artifact UI evidence

- UI-visible unavailable/fail-closed states or read-only evidence view.
- Raw artifacts remain support data only.
- No canon/memory/training mutation.
- No direct runtime tool execution is required by this parent publication task.

### 6. Review/apply-promotion UI evidence

- Safe review queue fixture.
- Apply-promotion requires explicit owner confirmation.
- Audit details visible.
- Failed/rejected promotion leaves approved memory/canon unchanged.
- Queue/candidate/model state cannot bypass promotion.

### 7. Analysis runtime exposure decision

- Decide whether NCP/Subtxt/dramatica-flow remain backend/helper-only or need UI labels/status.
- If UI-facing, expose analysis-only/allowlist status.
- If not UI-facing, document `NOT_EXPOSED` as acceptable for MVP owner acceptance.
- No NCP/Subtxt/dramatica-flow execution is allowed in this parent publication task.

## Parent Goals

- Convert the remaining owner acceptance evidence gaps into a child sequence that can be implemented and validated safely.
- Keep MVP acceptance focused on our app's missing UI/workflow surfaces.
- Make the source selection, Story Check diagnostic-only, no-prose refusal, Notes/Materials, raw artifact evidence, review/apply-promotion, and analysis runtime exposure decisions browser-testable.
- Preserve all product safety boundaries while making acceptance evidence visible.

## Non-Goals

- No frontend implementation in T001.
- No backend implementation in T001.
- No route/API changes in T001.
- No product behavior changes in T001.
- No tests in T001.
- No package/dependency changes.
- No crawler scripts.
- No raw captures.
- No `.external_sources` creation.
- No model calls or Ollama calls.
- No BookNLP/spaCy execution.
- No NCP/Subtxt/dramatica-flow execution.
- No generated prose or prose-production path.
- No canon/memory mutation.
- No candidate creation.
- No apply-promotion shortcut.
- No training/JSONL/dataset/model artifacts.
- Do not mark MVP complete.
- Do not claim owner acceptance.

## SaaS Research Deferral

External SaaS investigation is post-MVP/deferred. Dramatica/current-platform investigation is post-MVP/deferred.

Browsertrix, Crawlee, Stagehand, and Playwright against external SaaS are not part of this MVP UI fix parent. Controlled external experiments are post-MVP/deferred. Authorized non-black-box external reference collection is post-MVP/deferred unless the owner explicitly opens a separate post-MVP research task.

The documented research boundary and controlled-experiment method remain for later reference only. This parent prioritizes building and validating our own missing UI surfaces.

`PHASE8-UX-002-T002A`, if mentioned elsewhere, is post-MVP/deferred only and is not part of the active MVP child sequence.

## Controlled-Experiment / Lawful Non-Black-Box Reference Note

Hidden algorithms, prompts, model weights, model routing, ranking logic, workflow rules, and proprietary implementation details may be known through authorized disclosure, official documentation, owner-provided evidence, or other lawful non-black-box evidence.

Those details must not be claimed as proven from black-box observation alone. Authorized non-black-box reference information still needs to be collected, summarized, provenance-labeled, and reviewed before use as UX/reference input.

No authorized reference collection happens in `PHASE8-UX-002-T001`.

## Active Child Task Sequence

- `PHASE8-UX-002-T001` - Parent publication. Scope: docs/status/planning only. Publish the parent and record boundaries, scope, planned child sequence, validation, and current MVP readiness status. Status: complete/PASS.
- `PHASE8-UX-002-T002` - UI acceptance matrix + route/workflow decision. Scope: docs/decision/planning only. Convert owner acceptance gaps into route/workflow/UI acceptance matrix. Decide which surfaces are MVP-required, which are backend/helper-only, and which remain manual. Status: complete/PASS. Decision: `docs/roadmap/decisions/PHASE8-UX-002-ui-acceptance-matrix-route-workflow-decision.md`. Matrix: `docs/roadmap/ux/PHASE8-UX-002-ui-acceptance-matrix.md`.
- `PHASE8-UX-002-T003` - Expected-red tests for source/Story Check/no-prose UI. Scope: tests-first expected-red. Browser/source tests proving missing source/scene workflow, Story Check diagnostic-only path, no-prose refusal path, Notes/Materials save-reload, runtime/raw artifact UI evidence, and review/apply-promotion UI evidence as applicable. Status: next planned child.
- `PHASE8-UX-002-T004` - Implement owner-authored source/scene create/import/select UI. Scope: frontend/API only if needed and explicitly scoped later. Project-scoped owner-authored source workflow that unlocks Story Check and no-prose evidence.
- `PHASE8-UX-002-T005` - Implement Story Check diagnostic-only/no-prose evidence UI. Scope: frontend/API only if needed and explicitly scoped later. Safe selected-source Story Check path, diagnostic-only output state, and no-prose refusal/fail-closed evidence.
- `PHASE8-UX-002-T006` - Implement Notes/Materials + runtime/review evidence UI. Scope: likely split if too large. Notes/Materials save-reload proof, raw artifact read-only/support-data UI evidence, safe review/apply-promotion fixture and confirmation evidence.
- `PHASE8-UX-002-T007` - Closeout + rerun owner acceptance harness. Scope: docs/status/governance plus owner-run evidence. Re-run owner acceptance harness after missing UI surfaces are built. Do not mark MVP complete unless owner explicitly accepts through the correct checklist/roadmap gate.

`PHASE8-UX-002-T002A` is not included in the active MVP child sequence.

## Validation Commands

T001 validation:

```bash
python3 scripts/check_enrichment.py
python3 scripts/validate_roadmap.py
git diff --check
git status --short --branch
git diff --name-only
```

T002 validation:

```bash
python3 scripts/check_enrichment.py
python3 scripts/validate_roadmap.py
python3 -m json.tool docs/roadmap/enrichment/PHASE8-UX-002.enrichment.json >/dev/null
git diff --check
git status --short --branch
git diff --name-only
```

## MVP Readiness Status

Owner acceptance remains pending. MVP is not complete.

`PHASE8-UX-002` is needed because latest owner acceptance evidence is `MANUAL_REVIEW_REQUIRED` due to missing UI/workflow surfaces. This publication does not claim owner acceptance and does not complete MVP.
