# PHASE8-UX-002 - MVP acceptance UI completion and route wiring

## Status

`PHASE8-UX-002` is published as the active MVP-first UX parent for completing the missing browser-testable UI and workflow surfaces required before owner MVP acceptance.

`PHASE8-UX-002-T001` is complete/PASS as docs/status/planning parent publication only. No UI, routes, tests, crawlers, dependencies, raw captures, context artifacts, `.external_sources`, frontend code, backend code, product behavior, model calls, canon/memory mutation, candidate creation, generated prose, or apply-promotion shortcut were created by T001.

`PHASE8-UX-002-T002` is complete/PASS as docs/decision/planning only. T002 created the UI acceptance matrix and route/workflow decision, recorded browser-testable MVP UI surfaces, preserved SaaS/research deferral, and identified `PHASE8-UX-002-T003` as the next child. No product implementation occurred.

`PHASE8-UX-002-T003` is complete/PASS as tests-first expected-red only. T003 added static/source UI contract coverage at `tests/test_phase8_ux002_mvp_ui_acceptance_expected_red.py` for the seven MVP UI/workflow surfaces from the T002 matrix. The validated targeted expected-red command is `.venv-unsloth-clean/bin/python -m pytest tests/test_phase8_ux002_mvp_ui_acceptance_expected_red.py -q`, which reaches pytest collection/execution and produces the intended result: `7 failed in 0.12s`, all assertion failures for missing PHASE8-UX-002 MVP UI contract markers. System `python3 -m pytest tests/test_phase8_ux002_mvp_ui_acceptance_expected_red.py -q` still fails before collection because `/usr/bin/python3` has no `pytest` module, but that is not a T003 blocker because the repo's existing virtualenv is the validated test interpreter. No product implementation occurred.

`PHASE8-UX-002-T004` is complete/PASS as the owner-authored source/scene create/import/select UI implementation. T004 adds frontend-only source workflow support using existing project-scoped scene list/save behavior: the browser can create/import an owner-authored source, select a project-scoped Story Check source, display the selected source, reset/revalidate selection on active project changes, and keep Story Check disabled/fail-closed until `selectedStoryCheckSourceId` is present. Focused validation command `.venv-unsloth-clean/bin/python -m pytest tests/test_phase8_ux002_mvp_ui_acceptance_expected_red.py -q -k ux2_source_001` passes with `1 passed, 6 deselected in 0.03s`. The full expected-red file now reports `1 passed, 6 failed`, with remaining expected-red failures limited to `UX2-STORYCHECK-001`, `UX2-NOPROSE-001`, `UX2-NOTES-MATERIALS-001`, `UX2-RAW-ARTIFACT-001`, `UX2-REVIEW-PROMOTION-001`, and `UX2-ANALYSIS-RUNTIME-001` for T005/T006 follow-up surfaces.

`PHASE8-UX-002-T005` is complete/PASS as the Story Check diagnostic-only/no-prose evidence UI implementation. T005 adds frontend-only selected-source Story Check execution through `runStoryCheckForSelectedSource`, browser-visible diagnostic-only/non-canon result labeling, and a browser-visible no-prose refusal/fail-closed panel for rewrite, continue, outline, draft, polish, improve, expand, imitate, and generate prose intents. Focused validation command `.venv-unsloth-clean/bin/python -m pytest tests/test_phase8_ux002_mvp_ui_acceptance_expected_red.py -q -k "ux2_storycheck_001 or ux2_noprose_001"` passes with `2 passed, 5 deselected in 0.03s`. UX2-SOURCE-001 regression remains passing with `1 passed, 6 deselected in 0.03s`. The full expected-red file now reports `3 passed, 4 failed`, with remaining expected-red failures limited to `UX2-NOTES-MATERIALS-001`, `UX2-RAW-ARTIFACT-001`, `UX2-REVIEW-PROMOTION-001`, and `UX2-ANALYSIS-RUNTIME-001` for T006.

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
- `PHASE8-UX-002-T003` - Expected-red tests for source/Story Check/no-prose UI. Scope: tests-first expected-red. Browser/source tests proving missing source/scene workflow, Story Check diagnostic-only path, no-prose refusal path, Notes/Materials save-reload, runtime/raw artifact UI evidence, review/apply-promotion UI evidence, and analysis-runtime exposure label behavior as applicable. Status: complete/PASS as expected-red only. Test: `tests/test_phase8_ux002_mvp_ui_acceptance_expected_red.py`. Targeted command: `.venv-unsloth-clean/bin/python -m pytest tests/test_phase8_ux002_mvp_ui_acceptance_expected_red.py -q`. Expected-red result: `7 failed in 0.12s`, all intended assertion failures for missing UX2 UI contract markers. System `python3` lacks `pytest`, but that is not a task blocker because the repo virtualenv is the validated interpreter.
- `PHASE8-UX-002-T004` - Implement owner-authored source/scene create/import/select UI. Scope: frontend/API only if needed and explicitly scoped later. Project-scoped owner-authored source workflow that unlocks Story Check and no-prose evidence. Status: complete/PASS.
- `PHASE8-UX-002-T005` - Implement Story Check diagnostic-only/no-prose evidence UI. Scope: frontend/API only if needed and explicitly scoped later. Safe selected-source Story Check path, diagnostic-only output state, and no-prose refusal/fail-closed evidence. Status: complete/PASS.
- `PHASE8-UX-002-T006` - Implement Notes/Materials + runtime/review evidence UI. Scope: likely split if too large. Notes/Materials save-reload proof, raw artifact read-only/support-data UI evidence, safe review/apply-promotion fixture and confirmation evidence. Status: next planned child.
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

T003 validation:

```bash
python3 scripts/check_enrichment.py
python3 scripts/validate_roadmap.py
python3 -m json.tool docs/roadmap/enrichment/PHASE8-UX-002.enrichment.json >/dev/null
.venv-unsloth-clean/bin/python -m pytest tests/test_phase8_ux002_mvp_ui_acceptance_expected_red.py -q
git diff --check
git status --short --branch
git diff --name-only
```

The T003 targeted pytest command is expected-red and should fail until future implementation adds the required MVP UI/workflow surfaces. The expected-red result is `7 failed in 0.12s`, with intended assertion failures for:

- `UX2-SOURCE-001`: owner-authored source create/import/select markers are missing.
- `UX2-STORYCHECK-001`: selected-source diagnostic-only Story Check markers are missing.
- `UX2-NOPROSE-001`: no-prose refusal/fail-closed markers for forbidden intents are missing.
- `UX2-NOTES-MATERIALS-001`: project-scoped notes/materials create/save/reload proof markers are missing.
- `UX2-RAW-ARTIFACT-001`: runtime unavailable/read-only raw artifact evidence markers are missing.
- `UX2-REVIEW-PROMOTION-001`: review/apply-promotion confirmation and audit markers are missing.
- `UX2-ANALYSIS-RUNTIME-001`: `NOT_EXPOSED`/label-only analysis runtime markers are missing.

Roadmap validation and enrichment JSON validation must still pass.

T004 validation:

```bash
python3 scripts/check_enrichment.py
python3 scripts/validate_roadmap.py
python3 -m json.tool docs/roadmap/enrichment/PHASE8-UX-002.enrichment.json >/dev/null
.venv-unsloth-clean/bin/python -m pytest tests/test_phase8_ux002_mvp_ui_acceptance_expected_red.py -q -k ux2_source_001
.venv-unsloth-clean/bin/python -m pytest tests/test_phase8_ux002_mvp_ui_acceptance_expected_red.py -q
git diff --check
git status --short --branch
git diff --name-only
```

T004 expected result: focused `UX2-SOURCE-001` passes. Full expected-red file may continue to fail only for the remaining T005/T006 surfaces listed above. Owner acceptance remains pending, MVP is not complete, and external SaaS investigation remains post-MVP/deferred. No generated prose/prose-production behavior, backend route/API change, package change, context artifact update, crawler/raw capture, model call, canon/memory mutation, candidate promotion, apply-promotion shortcut, staging, commit, or push occurred in T004.

T005 validation:

```bash
python3 scripts/check_enrichment.py
python3 scripts/validate_roadmap.py
python3 -m json.tool docs/roadmap/enrichment/PHASE8-UX-002.enrichment.json >/dev/null
.venv-unsloth-clean/bin/python -m pytest tests/test_phase8_ux002_mvp_ui_acceptance_expected_red.py -q -k "ux2_storycheck_001 or ux2_noprose_001"
.venv-unsloth-clean/bin/python -m pytest tests/test_phase8_ux002_mvp_ui_acceptance_expected_red.py -q -k ux2_source_001
.venv-unsloth-clean/bin/python -m pytest tests/test_phase8_ux002_mvp_ui_acceptance_expected_red.py -q
git diff --check
git status --short --branch
git diff --name-only
```

T005 expected result: focused `UX2-STORYCHECK-001` and `UX2-NOPROSE-001` pass; `UX2-SOURCE-001` remains passing. Full expected-red file may continue to fail only for `UX2-NOTES-MATERIALS-001`, `UX2-RAW-ARTIFACT-001`, `UX2-REVIEW-PROMOTION-001`, and `UX2-ANALYSIS-RUNTIME-001`. T006 is next. Owner acceptance remains pending, MVP is not complete, and external SaaS investigation remains post-MVP/deferred. No generated prose/prose-production behavior, backend route/API change, package change, context artifact update, crawler/raw capture, model call, canon/memory mutation, candidate promotion, apply-promotion shortcut, staging, commit, or push occurred in T005.

## MVP Readiness Status

Owner acceptance remains pending. MVP is not complete.

`PHASE8-UX-002` is needed because latest owner acceptance evidence is `MANUAL_REVIEW_REQUIRED` due to missing UI/workflow surfaces. This publication does not claim owner acceptance and does not complete MVP.
