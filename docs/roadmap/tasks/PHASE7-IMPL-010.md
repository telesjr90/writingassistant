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
2. `PHASE7-IMPL-010-T002` - Automated regression validation pass. Status: ready.
3. `PHASE7-IMPL-010-T003` - Browser smoke checklist preparation. Status: draft.
4. `PHASE7-IMPL-010-T004` - Browser/manual smoke execution. Status: draft.
5. `PHASE7-IMPL-010-T005` - Validation repair triage. Status: draft.
6. `PHASE7-IMPL-010-T006` - Final validation regression pass. Status: draft.
7. `PHASE7-IMPL-010-T007` - Roadmap/status closeout. Status: draft.

## Child Task Details

### `PHASE7-IMPL-010-T001` - Workspace Validation / Browser and Manual Smoke inventory and child-task plan

- Created the task record, inventory, enrichment JSON, and initial roadmap/status updates.
- Defined the conservative validation child sequence `T001` through `T007`.
- Did not run browser/manual validation, app servers, pytest, or frontend builds.

### `PHASE7-IMPL-010-T002` - Automated regression validation pass

- Run existing backend and frontend source regression suites.
- Record results in validation docs.
- Make no runtime changes unless a tiny validation repair is explicitly needed.

### `PHASE7-IMPL-010-T003` - Browser smoke checklist preparation

- Create a manual/browser smoke checklist with exact flows, expected outcomes, and stop conditions.
- Do not execute browser smoke unless explicitly scoped by the child prompt.

### `PHASE7-IMPL-010-T004` - Browser/manual smoke execution

- Run backend and frontend locally.
- Execute the prepared checklist and record observed results.
- No feature expansion.

### `PHASE7-IMPL-010-T005` - Validation repair triage

- Only if smoke or regression finds issues.
- Classify issues as blocker, deferred, or not-a-bug.
- Perform tiny repair only if explicitly necessary and safe.

### `PHASE7-IMPL-010-T006` - Final validation regression pass

- Rerun roadmap validators and relevant automated tests after any repairs.
- Confirm no boundary drift.

### `PHASE7-IMPL-010-T007` - Roadmap/status closeout

- Record completed validation children.
- Mark the parent complete after closeout validation passes.
- Move the active frontier to the next roadmap-authorized task.

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

## Current Status

`PHASE7-IMPL-010` is the active Phase 7 frontier.

- Active child: `PHASE7-IMPL-010-T001` — complete after inventory/child-task planning.
- Next child: `PHASE7-IMPL-010-T002` — Automated regression validation pass.
- Last completed parent: `PHASE7-IMPL-009` — Memory / Canon shell (approved-only empty states).
