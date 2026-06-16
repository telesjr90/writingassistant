# PHASE7-IMPL-010

## ID

`PHASE7-IMPL-010`

## Title

Workspace Validation / Browser and Manual Smoke

## Goal

Validate the completed Phase 7 workspace foundation from `PHASE7-IMPL-004` through `PHASE7-IMPL-009` using automated regression checks, a prepared browser/manual smoke checklist, optional owner-observed UI notes, and roadmap/status closeout — without adding runtime feature scope, generated prose, model calls, extraction, apply-promotion, or memory/canon mutation.

## Why Now

`PHASE7-IMPL-004` through `PHASE7-IMPL-009` are complete and committed. The workspace now includes chapter/scene metadata compatibility, notes/materials storage, a shared owner-authored editor, Project Overview, OMI-guided staged project creation, and a read-only Memory / Canon shell. Browser/manual validation was intentionally deferred until this validation parent. The next safe step is to inventory validation scope, define child tasks, and run validation in controlled slices rather than expand product scope.

## Inputs / Dependencies

- Required completed parent tasks:
  - `PHASE7-IMPL-004` - Chapter / Scene Metadata Compatibility Layer
  - `PHASE7-IMPL-005` - Notes / Materials Storage
  - `PHASE7-IMPL-006` - Shared owner-authored document editor
  - `PHASE7-IMPL-007` - Project Overview shell
  - `PHASE7-IMPL-008` - OMI-guided project creation staged flow
  - `PHASE7-IMPL-009` - Memory / Canon shell (approved-only empty states)
- Roadmap authority:
  - `docs/roadmap/roadmap_index.yaml`
  - `docs/roadmap/implementation_status.md`
  - `docs/roadmap/task_backlog.md`
  - `docs/roadmap/phase_map.md`
  - `docs/master_plan.md`
- Validation references:
  - `docs/roadmap/mvp_completion_test_matrix.md`
  - `docs/roadmap/project_workspace_implementation_decision_sweep.md`
- Inventory:
  - `docs/roadmap/inventory/PHASE7-IMPL-010.md`
- Enrichment JSON:
  - `docs/roadmap/enrichment/PHASE7-IMPL-010.enrichment.json`

## Scope

Include:

- Validation of project creation, selection, switching, and blank-project compatibility.
- Validation of OMI-guided staged creation shell behavior and candidate/setup label visibility.
- Validation of Project Overview, shared editor save behavior, dirty-state/keyboard-save safeguards, and workspace view separation.
- Validation of scene/chapter metadata compatibility and notes/materials listing/editing behavior.
- Validation of Memory / Canon shell approved-only empty states and OMI candidate exclusion.
- Automated regression confirmation via existing pytest and frontend source-contract tests.
- Browser/manual smoke checklist preparation and later execution.
- Owner-observed UI smoke notes and validation repair triage only when needed.
- Roadmap/status closeout after validation completes.

Exclude:

- New runtime features unless a later validation repair child explicitly authorizes a tiny safe bug fix.
- Generated prose, summaries, extraction, semantic search, Story Check auto-runs, model calls, or Ollama calls.
- Apply-promotion, memory/canon mutation, OMI candidate promotion, backend approved-memory routes/helpers, or frontend approved-memory API helpers.
- Metadata editing UI, note/material create/import/upload UI, training/JSONL/dataset work, or package/dependency changes.
- Browser/manual validation during `PHASE7-IMPL-010-T001`.

## Product / Safety Boundaries

- Validation confirms existing analysis-only boundaries; it does not weaken them.
- Owner-authored prose storage and editing remain owner-controlled actions, not AI prose generation.
- OMI candidates, promotion audit records, and staged setup data remain non-canon.
- Approved Memory / Canon lists remain empty-state only until future apply-promotion exists.
- Validation must not silently promote candidates, create `memory/*.json`, or mutate durable project truth except through explicit owner/test temp paths during smoke.
- Any repair work must be minimal, explicitly authorized, and classified before implementation.

## Child Task Plan

1. `PHASE7-IMPL-010-T001` - Workspace Validation / Browser and Manual Smoke inventory and child-task plan. Status: complete.
2. `PHASE7-IMPL-010-T002` - Automated regression validation pass. Status: complete.
3. `PHASE7-IMPL-010-T003` - Browser smoke checklist preparation. Status: complete.
4. `PHASE7-IMPL-010-T004` - Browser/manual smoke execution. Status: complete (PARTIAL).
5. `PHASE7-IMPL-010-T005` - Validation repair triage. Status: complete.
6. `PHASE7-IMPL-010-T006` - Final validation regression pass. Status: complete.
7. `PHASE7-IMPL-010-T007` - Roadmap/status closeout. Status: complete.

## Child Task Details

### `PHASE7-IMPL-010-T001` - Workspace Validation / Browser and Manual Smoke inventory and child-task plan

- Created the task record, inventory, enrichment JSON, and initial roadmap/status updates.
- Defined the conservative validation child sequence `T001` through `T007`.
- Did not run browser/manual validation, app servers, pytest, or frontend builds.

### `PHASE7-IMPL-010-T002` - Automated regression validation pass

- Ran existing backend and frontend source regression suites; all passed on first run.
- Recorded results in `docs/roadmap/validation/latest_roadmap_validation.md`.
- No runtime changes were needed.

### `PHASE7-IMPL-010-T003` - Browser smoke checklist preparation

- Created `docs/roadmap/validation/PHASE7-IMPL-010-browser-smoke-checklist.md` with flows A–L, stop conditions, T004 reporting template, and owner observation prompts.
- Did not execute browser smoke, start app servers, or change runtime code or tests.

### `PHASE7-IMPL-010-T004` - Browser/manual smoke execution

- Started backend (`ANALYSIS_MODE=mock`) and frontend dev servers locally.
- Executed checklist flows A–L with PARTIAL overall result.
- Playwright/browser MCP unavailable; API/server-log/frontend-source fallback used for flows blocked by environment.
- Created smoke project `smoke-blank-1781586974`; reverted reversible scene edit on `example/scene_001`.
- No runtime code or test changes.

### `PHASE7-IMPL-010-T005` - Validation repair triage

- Triaged T004 PARTIAL results; no product defect confirmed.
- Classified gaps as environment limitation, deferred validation, repair-candidate (interactive UI only), or confirmed pass.
- No runtime repair authorized; interactive browser rerun deferred to owner/environment when Playwright deps or browser MCP are available.
- F/G remain deferred (no note/material fixtures); future fixture creation is a separate authorized validation helper task, not T005 scope.

### `PHASE7-IMPL-010-T006` - Final validation regression pass

- Reran roadmap validators and relevant automated tests after T005 triage; all passed on first run.
- Confirmed no boundary drift; no runtime repairs needed.
- Interactive UI flows remain deferred (Playwright `libnspr4.so` missing; browser MCP unavailable during T004).

### `PHASE7-IMPL-010-T007` - Roadmap/status closeout

- Recorded completed validation children T001 through T007.
- Marked the parent complete after closeout validation passed.
- Updated roadmap/status docs with final validation outcome, deferred interactive browser notes, and local smoke artifact guidance.
- Published Phase 7 parent sequence (`PHASE7-IMPL-001` through `PHASE7-IMPL-010`) is complete; next parent/child frontier requires owner/roadmap confirmation because no next published parent exists in `docs/roadmap/roadmap_index.yaml`.

## Acceptance Criteria

- Validation scope for `PHASE7-IMPL-004` through `PHASE7-IMPL-009` is documented before execution children run.
- Automated regression suites pass or failures are recorded with triage classification.
- Browser/manual smoke checklist exists before execution unless explicitly deferred with recorded rationale.
- Browser/manual smoke results are recorded without turning validation into feature expansion.
- No generated prose, summaries, extraction, semantic search, Story Check auto-runs, model/Ollama calls, apply-promotion, memory/canon mutation, training/JSONL/dataset changes, or new runtime feature scope are introduced by validation work.
- Candidate/canon boundaries, owner-authored save behavior, and workspace view separation remain intact after validation and any authorized repairs.

## Validation Expectations

For `PHASE7-IMPL-010-T001`:

- `python3 scripts/check_enrichment.py`
- `python3 scripts/validate_roadmap.py`
- Scoped `git diff -- ...` if raw git is allowed by local hooks; otherwise record the skip.
- No pytest, app servers, frontend builds, browser/manual validation, model calls, or Ollama calls.

For `PHASE7-IMPL-010-T002` and later children, use the validation commands named by each child prompt, including focused pytest suites and roadmap validators as applicable.

## Final Completion Summary

`PHASE7-IMPL-010` is complete as of the T007 closeout.

Final outcome:

- T001 created the inventory, task record, enrichment JSON, and initial roadmap/status updates.
- T002 ran automated regression validation; all relevant pytest suites passed on first run.
- T003 created the browser/manual smoke checklist (`docs/roadmap/validation/PHASE7-IMPL-010-browser-smoke-checklist.md`).
- T004 executed browser/manual smoke with PARTIAL overall result because Playwright Chromium failed (`libnspr4.so` missing) and Cursor browser MCP was unavailable; API/server-log/frontend-source fallback used for blocked flows.
- T005 triaged T004 results; no product defect confirmed; no runtime repair authorized.
- T006 reran roadmap validators and relevant automated tests; all passed on first run.
- T007 closed out roadmap/status and recorded the published Phase 7 parent sequence as complete.

Validation outcome:

- Automated regression validation passed (T002 and T006).
- Browser/manual smoke was attempted (T004) with PARTIAL result due to environment/browser tooling limits, not a confirmed product blocker.
- No runtime repair was required or performed (T005).
- Interactive UI flows D, E, H, I, J, K, and L remain deferred for owner/environment rerun when browser tooling is available.
- Note/material browser flows F/G remain deferred unless controlled fixtures are authorized later.

Local smoke artifact (must remain uncommitted): `projects/smoke-blank-1781586974/`.

`PHASE7-IMPL-010` did not add generated prose, summaries, extraction, semantic search, Story Check auto-runs, model calls, Ollama calls, apply-promotion, memory/canon mutation, OMI candidate promotion, backend approved-memory routes/helpers, frontend approved-memory API helpers, metadata editing UI, note/material create/import/upload UI, runtime features, package/dependency changes, or training/JSONL/dataset work.

## Current Status

`PHASE7-IMPL-010` is complete. The published Phase 7 parent sequence (`PHASE7-IMPL-001` through `PHASE7-IMPL-010`) is complete.

- Last completed child: `PHASE7-IMPL-010-T007` — Roadmap/status closeout.
- Prior completed child: `PHASE7-IMPL-010-T006` — Final validation regression pass.
- Prior completed child: `PHASE7-IMPL-010-T005` — Validation repair triage.
- Prior completed child: `PHASE7-IMPL-010-T004` — Browser/manual smoke execution (PARTIAL).
- Last completed parent: `PHASE7-IMPL-010` — Workspace Validation / Browser and Manual Smoke.
- Next parent/child: requires owner/roadmap confirmation; no next published parent exists in `docs/roadmap/roadmap_index.yaml`.
