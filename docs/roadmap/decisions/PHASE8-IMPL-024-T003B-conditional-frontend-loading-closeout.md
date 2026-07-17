# PHASE8-IMPL-024-T003B Conditional Frontend Loading Closeout

## Decision

`PHASE8-IMPL-024-T003B - Conditional frontend loading with distinct absent, invalid, and request-failure states` is **complete/PASS**.

## Parent and Dependency Context

- Parent workstream: `PHASE8-IMPL-024-T003` (Optional-resource handling), active/in progress.
- Dependency: `PHASE8-IMPL-024-T003A` (Context-availability/readiness contract), complete/PASS.
- T003A provides the deterministic read-only `GET /api/projects/{project_name}/context-readiness` endpoint with schema version `project_context_readiness.v1`.
- T003B consumes this contract in the frontend before optional direct-resource loading.
- T003C (console/network regression validation) remains planned; dependency on T003B is now satisfied.
- PHASE8-IMPL-024 remains published/active and incomplete. PHASE8-IMPL-025 remains published/planned and inactive.

## Final Implementation Commit

`83de5db8a8b017bdcc55f22876024219fdb4be3e`

Title: `fix(ui): isolate project-scoped async finalization (T003B)`

The prior interim commit `22d7737df72e70ba4feb44b69d370114bb8ceebd` captured the initial T003B implementation. The final accepted commit `83de5db` supersedes it with production-scoped async finalization guards (session/capture, project-switch reset, stale-operation rejection, and ABA rejection). `22d7737` remains a valid historical ancestor but must not be treated as the final T003B implementation commit.

## Current Exact Closeout Baseline

- Branch: `docs/opencode-go-routing-small-task-execution`
- HEAD: `ceeda25b3a460104ab3e35e395eaea0cbc1d6eaf`
- The final implementation commit `83de5db` is an ancestor on the same branch.
- Subsequent T011 governance commits (between `83de5db` and HEAD) are control-plane only; they did not alter T003B application code or tests.
- Worktree: clean. Staging: empty.

## Changed Application Files

Across the complete T003B implementation history:

- `frontend/src/App.jsx` — Added `fetchProjectContextReadiness` import, `projectGenRef` (monotonically increasing generation ref), `contextReadinessLoading` / `contextReadinessError` state, `createOperationGuard` (immutable session-snapshot guard), `loadInitialData` (captures project identity before async work, queries readiness first, gates optional direct Bible/storyform loads on per-resource `ready` state, keeps scenes/notes/materials/OMI loading independent), `handleSaveStoryform` (post-save guard with saveGuard, re-fetches readiness and storyform context), `handleRetryContextReadiness` (retry guard with retryGuard, clears errors and re-fetches readiness), project-switch resets `isSavingStoryform`, `retrying`, `contextReadinessError`, and `directResourceErrors`.
- `frontend/src/components/ProjectContext.jsx` — Added `getResourceReadinessLabel`, `getResourceReadinessReason` helpers; extended `ContextJsonEditor` to accept `readinessState` and `directError` props and compute `readOnlyMode` from invalid/unavailable/error states; extended `ProjectContext` default export to receive and render `readinessState`, `directError`, `readinessError`, `isLoadingReadiness`, `onRetryReadiness`, `saveDisabled`, and `isSavingResource` props for Bible and storyform editors, including Retry button rendering, distinct status labels, and save-disabled propagation.
- `frontend/tests/contextReadinessApi.test.mjs` — 11 API contract tests for `fetchProjectContextReadiness`: correct endpoint, payload preservation, state preservation (absent/invalid/unavailable/ready), transport-failure rejection, and no cross-contamination with direct Bible/storyform/storyform-context endpoints.
- `frontend/tests/contextReadinessWiring.test.mjs` — 51 wiring/behavioral tests: H1-H5 (createOperationGuard snapshot/isCurrent semantics), L1-L5 (stale-save/A-B/ABA rejection), M1-M5 (stale-retry rejection and reset), R1-R2 (deferred save/retry project-switch behavioral integration), P1-P5 (source assertions for guard usage and project-switch resets), A1-A3 (independent non-optional-context loading), I1-I4 (loadInitialData identity capture and independent processing), B1-B5 (absent Bible/storyform editability/non-readonly/non-alarming), C1-C3 (post-save re-fetch), E1-E3 (direct-failure retry), F1-F3 (invalid/readiness-failure/direct-failure distinctness), G1-G5 (source-level guard checks), N1-N3 (no-prose/no-Story-Check/no-prohibited-request boundaries).

## Accepted Frontend Behavior

1. **Readiness-first loading:** `loadInitialData` captures the project identity, issues `fetchProjectContextReadiness`, and only issues direct GET requests for resources whose `ready` state is `true`. Absent, invalid, unavailable, and not-applicable resources skip direct loading.
2. **Distinct UI states:**
   - `absent`: resource textarea is editable; Save button is enabled; label reads "Not stored"; no alarming status.
   - `invalid`: resource textarea is read-only; Save button is disabled; label reads "Invalid" with reason.
   - `unavailable`: similar to invalid with "Unavailable" label and reason.
   - `readiness-request error`: textarea read-only; label reads "Availability could not be checked."
   - `direct-resource load failure`: textarea read-only with "Load failed" label; Retry button is visible.
3. **Absent Bible and storyform remain owner-editable and saveable:** No read-only or disabled state is imposed on normally absent optional resources.
4. **Retry:** `handleRetryContextReadiness` clears direct-resource errors and re-fetches readiness; Retry button is rendered when a direct error is detected.
5. **Independent unrelated loading:** Scenes, notes, materials, and OMI loading proceed independently of optional-context readiness. Rejected readiness does not block processing of unrelated fulfilled results.

## Stale-Operation and Session-Generation Behavior

1. **Monotonically increasing generation:** `projectGenRef` increments on every project switch.
2. **Immutable session snapshots:** `createOperationGuard` captures `{ projectId, generation }` at call time. `isCurrent()` compares the captured snapshot against the live ref.
3. **Stale-save rejection:** A save finalization whose guard is not current is skipped (state not written into the current project).
4. **Stale-retry rejection:** Same pattern for retry finalization.
5. **ABA rejection:** An operation initiated in project A, after A→B→A, is rejected because the captured generation (`gen=N`) does not match the live generation (`gen=N+2`).
6. **Project-switch reset:** On project switch, `isSavingStoryform`, `retrying`, `contextReadinessError`, and `directResourceErrors` are reset.

## Test Results from This Closeout Run

- Focused context-readiness tests (API + wiring): **62 passed, 0 failed**.
- Complete frontend node test suite: **89 passed, 0 failed** (62 readiness + 27 existing).
- Frontend production build: **PASS** (vite v8.0.14, 422ms).
- git diff --check: **PASS** (no whitespace errors).

## Explicit Non-Implementation of T003C

T003C (console/network regression validation) was not executed. No browser, application server, console, network, Playwright, or runtime validation was performed. T003C remains planned and becomes the next readiness task/application frontier.

## Safety Boundary

No model/runtime execution, Story Check invocation, candidate creation, promotion, apply-promotion, Memory/Canon mutation, or story-prose generation occurred during T003B. The existing analysis-only, candidate-first, owner-controlled boundaries are preserved.

## Next Planned Task

`PHASE8-IMPL-024-T003C` — Console and network regression validation. Dependency on T003B is satisfied. T003 (parent) remains active/in progress.

## PHASE8-IMPL-025 Inactive

PHASE8-IMPL-025 remains published/planned and inactive. T003C validation, T006 navigation, T007 UI review/foundation, T004 responsive, T005 accessibility, T008 validation suites, and parent closeout must complete before PHASE8-IMPL-025 may activate.
