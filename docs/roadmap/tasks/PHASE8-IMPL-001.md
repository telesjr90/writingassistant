# PHASE8-IMPL-001

## ID

`PHASE8-IMPL-001`

## Title

Writer Assistant Core implementation readiness and first runtime slice plan

## Goal

Promote Writer Assistant Core as the next published roadmap frontier after the completed Phase 7 Project Workspace Foundation, then prepare the first safe runtime slice through context planning, source inventory, schema alignment, OMI candidate-first boundaries, and acceptance criteria before any extraction, candidate creation, model call, UI expansion, apply-promotion, or memory/canon mutation is implemented.

## Why Now

`PHASE7-IMPL-001` through `PHASE7-IMPL-010` are complete. The app now has the Project Workspace Foundation needed before Writer Assistant Core work begins. The next product direction is to help identify, organize, connect, annotate, and review story knowledge from owner-authored project text, but runtime work must begin conservatively with readiness and context planning.

## Dependencies

- Completed parent: `PHASE7-IMPL-010` - Workspace Validation / Browser and Manual Smoke.
- Completed child: `PHASE7-IMPL-010-T007` - Roadmap/status closeout.
- Planning references:
  - `docs/roadmap/writer_assistant_core_candidate_schemas.md`
  - `docs/roadmap/omi_story_knowledge_candidate_expansion.md`
  - `docs/roadmap/omi_mvp_schema_lifecycle.md`
  - `docs/roadmap/omi_storage_model.md`
  - `docs/roadmap/project_memory_canon_storage_model.md`
  - `docs/roadmap/project_memory_canon_page_structure_spec.md`
  - approved category page specs `WORKSPACE-013` through `WORKSPACE-025`

## Scope

Include:

- Publish the Phase 8 parent in the roadmap/status layer.
- Define a conservative child-task sequence for implementation readiness.
- Plan current code, storage, and test inventory before implementation.
- Plan targeted context collection questions before any context tools run.
- Align the first runtime slice with Writer Assistant Core candidate schemas.
- Preserve source/evidence/provenance requirements from the first selected slice.
- Keep OMI as the central candidate review and future promotion layer.
- Select the first implementation slice only after context is collected and reviewed.
- Define acceptance criteria for the first implementation task.

## Exclusions

- Runtime extraction implementation in T001.
- Context-tool execution in T001.
- Backend extraction routes.
- Frontend extraction UI.
- Candidate creation runtime changes.
- Model/Ollama calls.
- Story Check auto-runs.
- Semantic search.
- Generated prose, rewriting, continuation, style imitation, or prose improvement.
- Summaries as final or approved truth.
- Apply-promotion.
- OMI candidate promotion.
- Memory/canon mutation.
- Package/dependency changes.
- Training data, JSONL records, dataset manifests, or model artifacts.
- Dramatica analysis.

## Child-Task Plan

1. `PHASE8-IMPL-001-T001` - Publish Writer Assistant Core parent and child-task plan. Status: complete.
2. `PHASE8-IMPL-001-T002` - Context collection plan for Writer Assistant Core. Status: complete.
3. `PHASE8-IMPL-001-T003` - Targeted context collection and source inventory. Status: complete.
4. `PHASE8-IMPL-001-T004` - First runtime slice decision. Status: ready.
5. `PHASE8-IMPL-001-T005` - First slice contract/source tests. Status: planned.
6. `PHASE8-IMPL-001-T006` - First slice implementation prompt/repair plan. Status: planned.
7. `PHASE8-IMPL-001-T007` - Roadmap/status closeout. Status: planned.

## Child Task Details

### `PHASE8-IMPL-001-T001` - Publish Writer Assistant Core parent and child-task plan

- Docs/status/planning only.
- Publish parent, inventory, enrichment JSON, and roadmap/status updates.
- No context tools run.
- No runtime code, tests, backend/frontend/package files, project runtime files, training data, JSONL records, or dataset manifests changed.

### `PHASE8-IMPL-001-T002` - Context collection plan for Writer Assistant Core

- Docs/planning only.
- Define exact context questions, target files, allowed tools, expected outputs, and validation boundaries.
- Output: `docs/roadmap/context/PHASE8-IMPL-001-context-collection-plan.md`.
- Do not run broad tool execution.
- Do not implement runtime behavior.

### `PHASE8-IMPL-001-T003` - Targeted context collection and source inventory

- Completed with direct file/source inspection only.
- Produced `docs/roadmap/context/PHASE8-IMPL-001-targeted-context-report.md`.
- Answered T002 question groups A-H and evaluated first runtime slice candidates.
- Recommended T004 consider Writer Assistant Core candidate schema constants plus source-level/contract tests before extraction runtime.
- No context tools, runtime implementation, tests, routes, UI, extraction, model calls, apply-promotion, or memory/canon mutation.

### `PHASE8-IMPL-001-T004` - First runtime slice decision

- Choose the smallest safe first implementation slice.
- Define whether the first slice is schema-only, storage-only, route-only, or source-level tests first.
- No runtime implementation unless explicitly scoped by that child prompt.

### `PHASE8-IMPL-001-T005` - First slice contract/source tests

- Add tests or contract coverage for the selected first slice.
- No production runtime implementation unless explicitly authorized by task scope.

### `PHASE8-IMPL-001-T006` - First slice implementation prompt/repair plan

- Prepare or execute the first tiny implementation slice according to T004/T005.
- Preserve candidate-first, no-prose, no-promotion, evidence/provenance, and OMI review boundaries.

### `PHASE8-IMPL-001-T007` - Roadmap/status closeout

- Close the readiness parent after child outcomes are recorded.
- Move the active frontier to the first actual Writer Assistant Core implementation parent or next roadmap-authorized task.

## Acceptance Criteria

- `PHASE8-IMPL-001` exists as the active Phase 8 Writer Assistant Core parent.
- The T001-T007 child sequence is published and conservative.
- T001 is recorded as complete (docs/status/planning only).
- T002 is recorded as complete with context collection plan at `docs/roadmap/context/PHASE8-IMPL-001-context-collection-plan.md`.
- T003 is complete and produced the targeted context report at `docs/roadmap/context/PHASE8-IMPL-001-targeted-context-report.md`.
- T004 is the current ready child for first runtime slice decision.
- OMI remains the candidate-first review and future promotion layer.
- Candidate output, model output, NotebookLM output, extracted candidates, and planning notes remain non-canon until explicit owner review and future owner-controlled promotion.
- No runtime extraction, candidate creation, backend route, frontend UI, model call, apply-promotion, memory/canon mutation, or training/dataset work is claimed by this parent promotion task.

## Validation Expectations

For `PHASE8-IMPL-001-T002`:

- `python3 scripts/check_enrichment.py`
- `python3 scripts/validate_roadmap.py`
- Non-LeanCTX whitespace check on changed docs

For `PHASE8-IMPL-001-T003`:

- `python3 scripts/check_enrichment.py`
- `python3 scripts/validate_roadmap.py`
- Non-LeanCTX whitespace check on changed docs

For `PHASE8-IMPL-001-T001`:

- `python3 scripts/check_enrichment.py`
- `python3 scripts/validate_roadmap.py`
- `git diff --check`

Do not run pytest unless runtime code or tests were accidentally changed. Do not run app servers, frontend build, browser/manual validation, model calls, Ollama, CCE, Graphify, Repomix, AI Context generation, MCP tools, LeanCTX, or broad discovery.

## Safety / Product Boundaries

- The app is analysis-only.
- The app must not write, rewrite, continue, imitate, polish, improve, expand, or extend story prose.
- Owner-authored prose storage and editing remain allowed only when text is authored by the owner.
- Story knowledge extracted or inferred from owner-authored text must remain candidate-only until explicit owner review.
- OMI is the central review and future promotion layer.
- Promotion records are audit-only until future apply-promotion exists.
- Memory/canon mutation is out of scope for this parent until a later owner-authorized task selects it.
- Context outputs are evidence, not roadmap truth.

## Current Status

`PHASE8-IMPL-001` is active. Current ready child: `PHASE8-IMPL-001-T004` - First runtime slice decision. Last completed child: `PHASE8-IMPL-001-T003` - Targeted context collection and source inventory. Prior completed child: `PHASE8-IMPL-001-T002` - Context collection plan for Writer Assistant Core. Prior completed child: `PHASE8-IMPL-001-T001` - Publish Writer Assistant Core parent and child-task plan.
