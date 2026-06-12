# Implementation Status

Status source: this file and `docs/roadmap/roadmap_index.yaml` are the current roadmap execution truth layer.

## Active Frontier

- Current track: Project Workspace Foundation.
- Immediate active parent task: `PHASE7-IMPL-004`.
- Canonical title: Chapter / Scene Metadata Compatibility Layer.
- First ready planning/inventory micro-task: `PHASE7-IMPL-004-T001` - Read-only chapter and scene metadata compatibility inventory.

`PHASE7-IMPL-004` must remain `Chapter / Scene Metadata Compatibility Layer`.

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
