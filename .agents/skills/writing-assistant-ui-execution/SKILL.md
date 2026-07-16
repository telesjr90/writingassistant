---
name: writing-assistant-ui-execution
description: Shared, fail-closed UI execution policy for Writing Assistant audits, implementation, and validation using the installed Impeccable guidance.
---

# Writing Assistant UI Execution

Use this project-owned wrapper for every task that audits, reviews, plans,
designs, implements, tests, validates, or closes frontend, UI, or UX behavior.
It is the shared policy layer for Codex and OpenCode Go. Apply the installed
`.agents/skills/impeccable/SKILL.md` guidance within the accepted task scope;
do not copy or replace that guidance here.

## Required gate and authority

Before UI inspection or execution:

1. Verify the exact repository root, expected branch, full commit, clean
   worktree, and empty staging area.
2. Require current Project Memory status `FRESH` and zero Plan Integrity
   blockers for that exact clean commit.
3. Read `docs/roadmap/roadmap_index.yaml` for the current application frontier,
   task status, dependencies, activation boundary, and accepted task sources.
4. Resolve the task through
   `docs/project-memory/registries/execution-routing.json` using
   `scripts/project_memory/execution_routing.py`. Fail closed for missing,
   conflicting, stale, inapplicable, owner-only, inactive, or
   dependency-ineligible routing.
5. Read the accepted task and decision records, then read the installed
   Impeccable skill. Use only the applicable guidance within the task's
   allowlist and explicit tool permissions.

Authority remains, in order: current accepted owner decisions; current roadmap
execution records and task definitions; tracked code, schemas, tests, and
fixtures within their declared roles; current commit-bound Project Memory;
clearly labeled historical or superseded records; generated evidence. The
Impeccable skill and its output are guidance and generated evidence, never
project truth or task authority.

## Modes

### UI audit mode

Use applicable Impeccable audit, critique, interaction, layout, clarity,
hierarchy, responsive, and accessibility guidance. Remain read-only unless the
task explicitly authorizes mutation. Report facts separately from generated
recommendations.

### UI implementation mode

Use applicable Impeccable layout, interaction, component, clarity, responsive,
accessibility, and hardening guidance before and during authorized edits. Edit
only task-allowed files and run only task-authorized validation. Do not broaden
scope or select a dependency or component foundation.

### UI validation mode

Use applicable Impeccable review and hardening guidance together with only the
task-authorized Playwright, accessibility, responsive-width, keyboard, browser
console, network, and loading/degraded/failure/retry/recovery checks. Validation
evidence cannot establish acceptance unless the accepted task contract assigns
that role to the check.

## Fail-closed boundaries

- `PHASE8-IMPL-024-T007B` is owner-only. No agent may select the component
  foundation or treat an Impeccable recommendation as that decision.
- Browser execution, repository mutation, asset generation, dependency
  installation, network access, external tools, model calls, and application
  servers require explicit task authorization. Stop when authorization is
  absent.
- Do not execute beyond the active task, alter task status or dependencies,
  create an owner decision, or use historical/superseded routing as current.
- Preserve the analysis-only, candidate-first, evidence/provenance-backed,
  owner-controlled product boundary. Never generate story prose, automatically
  promote or apply promotion, or automatically mutate Memory/Canon.
- Preserve Git safety. Do not stage, commit, push, amend, rebase, reset, clean,
  restore, or stash unless the owner explicitly authorizes the exact action.
