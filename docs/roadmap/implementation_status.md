# Implementation Status

Status source: this file and `docs/roadmap/roadmap_index.yaml` are the current roadmap execution truth layer.

## Active Frontier

- Current track: Project Workspace Foundation.
- Immediate active parent task: `PHASE7-IMPL-005`.
- Canonical title: Notes / Materials Storage.
- Last completed parent task: `PHASE7-IMPL-004` - Chapter / Scene Metadata Compatibility Layer.
- Next parent task: `PHASE7-IMPL-005` - Notes / Materials Storage.

`PHASE7-IMPL-004` must remain `Chapter / Scene Metadata Compatibility Layer`.

`PHASE7-IMPL-004` is complete as of the T007 closeout. Completed child records:

- `PHASE7-IMPL-004-T002`: read-only backend scene metadata compatibility for legacy Markdown scenes.
- `PHASE7-IMPL-004-T003`: backend scene/chapter metadata write/create helpers.
- `PHASE7-IMPL-004-T004`: route compatibility tests preserving legacy scene route contracts.
- `PHASE7-IMPL-004-T005`: frontend display compatibility for metadata-shaped scene records while preserving legacy string scene IDs.
- `PHASE7-IMPL-004-T006`: legacy scene fallback regression tests.
- `PHASE7-IMPL-004-T007`: roadmap/status closeout.

Final `PHASE7-IMPL-004` behavior preserves existing `scenes/{scene_id}.md` scene bodies, keeps chapter and scene metadata separate from owner-authored Markdown, preserves legacy list/read route shapes, and does not add model calls, generated prose, extraction, OMI/memory/canon mutation, training/JSONL/dataset changes, or browser/manual validation scope.

Browser/manual validation belongs under `PHASE7-IMPL-010`.

Any prior smoke-test/manual-validation use of `PHASE7-IMPL-004` is a numbering drift issue, not a reason to renumber. Correct the reference by moving validation language under `PHASE7-IMPL-010` or a child task of `PHASE7-IMPL-010`; do not change the identity of `PHASE7-IMPL-004`.

## Authority

- GitHub Issues and GitHub Projects are not authoritative yet.
- Published parent task IDs in `docs/roadmap/roadmap_index.yaml` are authoritative for Codex task prompts.
- Parent task identity is immutable after publication.
- New implementation detail belongs in child micro-tasks, not in renamed or repurposed parent IDs.
- Child micro-tasks may use `planning_microtask`, `runtime_microtask`, or `validation_microtask` types.

## Codex Execution Role

Codex is a strict micro-task implementer, not a planner.

Codex prompts should specify one task ID, the exact files allowed to change, the exact validation commands to run, and the final response format. Codex should not infer new roadmap structure during implementation work.

## Context Tool Boundary

Repomix, Graphify, LeanCTX, and CCE are planning/context tools only and must not be run during Codex implementation micro-tasks.

LeanCTX is exceptional fallback only. It is not part of normal Codex implementation execution for this repository.

Context packs and generated maps are refreshable artifacts, not roadmap truth. The control layer is:

1. `docs/roadmap/roadmap_index.yaml`
2. `docs/roadmap/implementation_status.md`
3. `docs/roadmap/validation/latest_roadmap_validation.md`

## Roadmap enrichment scaffold

- The orchestrator scaffold is local and deterministic.
- The orchestrator must not decide task order.
- The orchestrator must not change `active_frontier` automatically.
- The orchestrator must not mark tasks complete.
- The orchestrator must not modify application code.
- The orchestrator may create task manifests, evidence files, enrichment JSON, and rendered task records.
- Generated context files are evidence artifacts, not source of truth.
- Source of truth remains `implementation_status.md`, `roadmap_index.yaml`, reviewed task records, `decision_log.md`, `risk_register.md`, and `open_questions.md`.
- CCE, Graphify, and Repomix may only be run in explicit collect mode after this scaffold is validated.
- `PHASE7-IMPL-004` should be the first orchestrator test case.

## Local tool command syntax

- Local tool command syntax discovery exists for CCE, Graphify, Repomix, and `scripts/generate_ai_context.sh`.
- Exact discovered syntax is recorded in `scripts/roadmap_enrichment/tool_commands.md`.
- AI Context command candidates for `PHASE7-IMPL-004` are recorded under `.codex-context/PHASE7-IMPL-004/`.
- Command discovery does not mean context collection has run.
- `collect-plan` mode exists for the enrichment orchestrator.
- `collect-plan` creates planned evidence files but does not run context tools.
- `PHASE7-IMPL-004` is the first planned collection target.
- CCE readiness was checked before collection.
- Exact CCE syntax is recorded in `scripts/roadmap_enrichment/tool_commands.md`.
- CCE readiness is now ready for explicit authorized collection.
- This does not mean CCE evidence has been collected.
- The first actual use of CCE should happen only in a future explicit collect step for `PHASE7-IMPL-004`.
- `cce init` remains prohibited.
- `PHASE7-IMPL-004` collection attempt 1 produced mixed evidence.
- Enrichment JSON and task record rendering are intentionally deferred.
- `.codex-context/PHASE7-IMPL-004/collection_repair_plan.md` controls the next evidence pass.
