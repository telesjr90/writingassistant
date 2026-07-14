# PHASE8-IMPL-026-T004C1 — Post-closeout task-registry synchronization and current-truth quality-gate repair

## Result

T004C1: **complete/PASS**

## Starting repository

- Repository: `WritingAssistantApplication-project-memory`
- Branch: `docs/project-memory-foundation`
- Full HEAD: `a415270b18f978e601a9ffc6d7bcb4ab8a250c42`
- Subject: `docs(pm): record first publication render and close T004 (T004C)`

## Failed refresh

- Run ID: `20260714T042826Z`
- Snapshot: `.codex-context/project-memory/PHASE8-IMPL-026-T004C/20260714T042826Z/`
- Render: `.codex-context/project-memory/rendered/PHASE8-IMPL-026-T004C/20260714T042826Z/`
- Quality: `.codex-context/project-memory/PHASE8-IMPL-026-T004C-quality/20260714T042826Z/`

### Package checksums

All checksums valid. Packages are structurally valid `generated_evidence`.

### Stale rendered statements

The `042826Z` render (and the earlier `033724Z` render) both contain:

1. `_render_index()` lines 718-726 (hardcoded): T004 shown as "in progress", T004C shown as "planned", T004B shown as "in progress".
2. `_render_current_roadmap()` line 899 (hardcoded): "Current Project Memory child: T004B".

These are incorrect for the post-closeout HEAD where T004 is complete and T004C closed.

### Quality-gate false positive

The one-off `/tmp/t004c_refresh_quality_check.py` returned PASS despite the rendered task-state contradiction because it:
- Checked for the literal presence of "Generated evidence" banners and commit hashes (correctly found).
- Used relaxed regex matching for boundary terms and annex terms (correctly passed).
- Did not verify that the rendered task-status table says T004 is complete and T004C is complete.

### Why the refresh is BLOCKED

Despite structurally valid packages, the render:
- Says T004 is "in progress" when it is complete.
- Says T004C is "planned" when it is complete and closed.
- Says T004B is "in progress" when it is complete/PASS.

A structurally current snapshot that renders stale semantic task truth is not an accepted current publication.

## Root cause

### Primary — Renderer hardcodes

`scripts/project_memory/render_docs.py` hardcodes the "Project Memory Workstream Status" table in `_render_index()` (lines 718-726) and the "Current Project Memory child" string in `_render_current_roadmap()` (line 899). These strings were set when T004 was in progress during development and were never updated.

The renderer does NOT read task lifecycle status from the registry for the index page table. This is a renderer defect.

### Contributing — Incomplete task registry

`docs/project-memory/registries/tasks.json` contained records only through T003. T004, T004A, T004B, T004C, and T005 had no normalized records. T003 was marked "planned" with stale notes.

This caused `_render_remaining_work()` to omit T005 (no record to render) and `_render_current_roadmap()` to produce an incomplete task listing.

## Repairs applied

### Registry synchronization

### Task registry (`docs/project-memory/registries/tasks.json`)

Updated:
- `task:PHASE8-IMPL-026-T003`: lifecycle from `planned` to `complete`, updated notes.

Added:
- `task:PHASE8-IMPL-026-T004` — complete/PASS-WITH-FINDINGS; parent PHASE8-IMPL-026; depends_on T003.
- `task:PHASE8-IMPL-026-T004A` — complete/PASS-WITH-FINDINGS; parent T004.
- `task:PHASE8-IMPL-026-T004B` — complete/PASS; parent T004.
- `task:PHASE8-IMPL-026-T004C` — complete/PASS-WITH-FINDINGS; parent T004.
- `task:PHASE8-IMPL-026-T005` — planned; parent PHASE8-IMPL-026; depends_on T004.

### Dependencies registry (`docs/project-memory/registries/dependencies.json`)

Added:
- `dependency:t004-depends-on-t003` — task_depends_on.

### Renderer repair (`scripts/project_memory/render_docs.py`)

Removed hardcoded task-status strings:
- `_render_index()`: Replaced lines 718-726 (hardcoded "Project Memory Workstream Status" table) with registry-derived task-status rows.
- `_render_current_roadmap()`: Replaced line 899 (hardcoded "Current Project Memory child: T004B") with registry-derived next-task identification.

Added deterministic task-selection helpers:
- `_get_task_by_id()` — locate task by stable ID.
- `_get_children()` — locate direct children by parent reference.
- `_validate_task_records()` — fail closed on duplicates, unsupported lifecycle, contradictory parent refs.
- `_identify_completed_children()` — find completed children.
- `_identify_next_planned_child()` — identify next planned/inactive child.
- `_derive_task_display_status()` — derive human-readable status from lifecycle + notes.

The renderer now:
- Derives task status from validated task records.
- Identifies the next planned inactive Project Memory task.
- Distinguishes completed children from planned next.
- Excludes completed tasks from remaining work.
- Fails closed when required task records are missing.

### Semantic validator (`scripts/project_memory/validate_rendered_docs.py`)

Created a reusable semantic rendered-package validator:
- Standard-library only.
- CLI: `--repo-root`, `--snapshot-dir`, `--render-dir`, `--json`.
- Structural checks: page set, JSON parsing, checksums, banners, links, unsafe content.
- Semantic checks: rendered task status converges with normalized registry.
- Results: `PASS`, `PASS_WITH_FINDINGS`, `BLOCKED`.
- Any semantic task-state contradiction produces `BLOCKED`.

### Renderer semantic integration

The renderer (`render()` function) now:
1. Builds the temporary render package.
2. Runs internal structural verification.
3. Calls `validate_rendered_package()` before atomic finalization.
4. Refuses atomic rename when semantic validation returns `BLOCKED`.
5. Cleans temporary output after failure.

### Source locators

Every record references tracked regular-file locators:
- `docs/roadmap/tasks/PHASE8-IMPL-026.md`
- `docs/roadmap/implementation_status.md`
- `docs/roadmap/decisions/PHASE8-IMPL-026-T004C-clean-head-documentation-generation-and-t004-closeout.md`
- `scripts/project_memory/render_docs.py`
- `tests/project_memory/test_render_docs.py`

No generated-evidence package, directory, or absolute path was used as an authoritative source locator.

## Regression tests

Expanded test coverage:

- `tests/project_memory/test_tracked_task_registry_current_state.py`:
  Updated from 29 tests (registry-only) to include renderer-output
  validation tests proving the renderer now derives task status from
  the registry. Added tests for helper functions, fail-closed behavior,
  deterministic task selection, and lifecycle-change responsiveness.

- `tests/project_memory/test_render_docs.py`:
  Updated test fixture to include all 8 required PM task records.
  Existing renderer tests now validate registry-derived task status.

- `tests/project_memory/test_validate_rendered_docs.py`:
  New — focused tests for the semantic rendered-package validator.
  Covers: reject T004 in progress, reject T004C planned, reject
  obsolete current child, reject T004 in remaining work, reject
  missing T005 from remaining, reject T005 active/complete, reject
  application-frontier drift, reject PHASE8-IMPL-025 activation,
  accept correct render, duplicates fail closed, missing records
  fail closed, contradictory parent refs fail closed, old stale
  output pattern rejected, missing pages fail structural,
  identical inputs produce same result, CLI output shape.

Focused test count (renderer + registry-state + validator): 140
Total Project Memory test count: 217

## Validation results

- Registry validation: PASS (0 errors, 0 warnings)
- Roadmap validation: PASS
- Enrichment validation: PASS
- All 217 Project Memory tests pass (was 177, now 217 after repair)
- Focused renderer/registry-state/validator tests: 140
- All compilation checks pass
- Prior evidence packages: checksums verified, byte-identical
- No protected paths modified beyond authorization

## Renderer defect boundary (RESOLVED)

The renderer (`scripts/project_memory/render_docs.py`) has been modified in T004C1.

Hardcoded status strings in `_render_index()` and the hardcoded
"Current Project Memory child: T004B" in `_render_current_roadmap()`
have been removed. Task status is now derived from the validated
task registry.

The renderer now:
- Derives Project Memory workstream status from validated task records.
- Identifies T005 as the next planned inactive Project Memory task.
- Fails closed when required task records are missing, duplicate IDs
  exist, lifecycle is unsupported, or parent references contradict the
  hierarchy.
- Refuses atomic publication when semantic validation returns BLOCKED.

A semantic publication quality gate now exists and is integrated into
the renderer's atomic publication path.

## Not generated

- No snapshot from dirty worktree.
- No publication render from dirty worktree.
- No publication-eligible output created.

## Prior evidence preserved

- `20260714T033724Z` packages: unchanged.
- `20260714T042826Z` packages: unchanged.
- Protected-input hashes: identical before and after.

## Status

| Task | Status |
|------|--------|
| T004 | complete/PASS-WITH-FINDINGS (unchanged) |
| T004A | complete/PASS-WITH-FINDINGS (unchanged) |
| T004B | complete/PASS (unchanged) |
| T004C | complete/PASS-WITH-FINDINGS (unchanged) |
| T004C1 | complete/PASS |
| T005 | planned/inactive (unchanged) |

## Next steps

1. **Post-repair clean-HEAD refresh** — The next operational step is a clean-HEAD refresh to generate an accepted current publication snapshot and render bound to the T004C1 commit.

2. **T005** — Existing context-tool integration. Remains planned/inactive. Must not start before the post-T004C1 clean-HEAD refresh passes.

## T005

T005 remains next and inactive. It must not start before the post-repair clean-HEAD refresh.

## Q151–Q154 disposition

- Q151 — Full Plan Integrity classification model: open.
- Q152 — Serena adoption criteria: open.
- Q153 — Embedding-model selection: open.
- Q154 — Operational synchronization cadence: open, refined:
  - Clean-HEAD commit binding works (proven by T003B, T004C, 042826Z refresh).
  - Registry freshness, renderer derivation, and semantic publication validation must all converge.
  - T004C1 repairs registry lag, renderer hardcodes, and adds semantic publication validation.
  - A clean-HEAD refresh is still required.
  - Operational cadence remains unresolved.

## Application frontier

Unchanged: `PHASE8-IMPL-024-T003A`. PHASE8-IMPL-025 remains published/planned and inactive.

## Remaining risks

- **Normalized task registry lagging accepted roadmap truth** — Mitigated but active. Registries now contain T004/T005 records but must be maintained with ongoing discipline.
- **Current-truth quality check false positives** — Mitigated. Semantic rendered-package validator (`validate_rendered_docs.py`) now verifies rendered task-state convergence with normalized records.
- **Structurally valid generated packages mistaken for accepted publications** — Mitigated. Publication acceptance now requires both structural integrity and semantic task-state convergence. The renderer refuses atomic publication on semantic BLOCKED.
- **Stale-memory / branch-synchronization** — Unchanged (active).
- **Q154 cadence** — Unchanged (active).
- **Renderer hardcodes stale task status** — Resolved. Renderer now derives task status from validated task registries.
- **Future retrieval prompt injection** — Unchanged (active).
- **External-tool provenance** — Unchanged.
- **Duplicate context systems** — Unchanged.
- **Model-generated amendments** — Unchanged.

## Changed tracked files

Created:
- `tests/project_memory/test_tracked_task_registry_current_state.py`
- `tests/project_memory/test_validate_rendered_docs.py`
- `scripts/project_memory/validate_rendered_docs.py`
- `docs/roadmap/decisions/PHASE8-IMPL-026-T004C1-post-closeout-task-registry-and-current-truth-gate-repair.md`

Modified:
- `scripts/project_memory/render_docs.py`
- `docs/project-memory/registries/tasks.json`
- `docs/project-memory/registries/dependencies.json`
- `docs/project-memory/README.md`
- `docs/project-memory/rendering/README.md`
- `tests/project_memory/test_tracked_task_registry_current_state.py`
- `tests/project_memory/test_render_docs.py`
- `docs/roadmap/tasks/PHASE8-IMPL-026.md`
- `docs/roadmap/inventory/PHASE8-IMPL-026.md`
- `docs/roadmap/enrichment/PHASE8-IMPL-026.enrichment.json`
- `docs/roadmap/decision_log.md`
- `docs/roadmap/implementation_status.md`
- `docs/roadmap/task_backlog.md`
- `docs/roadmap/phase_map.md`
- `docs/roadmap/open_questions.md`
- `docs/roadmap/risk_register.md`

Not modified:
- Schema (`docs/project-memory/schemas/`)
- Registry manifest (`docs/project-memory/registries/manifest.json`)
- Validator, scanners, convergence, snapshot builder (other than renderer)
- Protected test files (other than authorized modifications)
- Application code, dependencies, environment files
- Registry files other than tasks.json and dependencies.json
- Prior evidence packages

## Confirmation

- No snapshot or publication render was generated from the dirty worktree.
- Prior evidence packages remain byte-identical.
- No schema, registry manifest, protected test, application code, dependency, tool, model, plugin, or MCP server was modified.
- No accepted current publication exists for this commit; a clean-HEAD refresh is required.
