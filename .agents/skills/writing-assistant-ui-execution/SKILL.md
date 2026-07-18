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
2. Read the current explicit owner decisions and current roadmap/task documents
   for the task scope, status, dependencies, activation boundary, and accepted
   sources.
3. Review the relevant tracked frontend/application code, schemas, fixtures,
   and tests, using saved context outputs only as non-authoritative navigation.
4. Read the accepted task and decision records, then read the installed
   Impeccable skill. Use only the applicable guidance within the task's
   allowlist and explicit tool permissions.

Implementation-only mode is active under
`docs/roadmap/decisions/2026-07-17-project-memory-paused-as-an-application-implementation-gate.md`.
Do not require or invoke Project Memory freshness, supervision, Plan Integrity,
execution-routing resolution, Project Memory scripts, or Project Memory tests
for ordinary UI work. Project Memory remains preserved and may be used only
when the owner explicitly requests bounded Project Memory work.

Authority remains, in order: current accepted owner decisions; current roadmap
execution records and task definitions; tracked code, schemas, tests, and
fixtures within their declared roles; saved context outputs as supporting
navigation; focused direct reads; clearly labeled historical or superseded
records. The Impeccable skill and its output are guidance and generated
evidence, never project truth or task authority.

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
  create an owner decision, or use historical/superseded records as current.
- Preserve the analysis-only, candidate-first, evidence/provenance-backed,
  owner-controlled product boundary. Never generate story prose, automatically
  promote or apply promotion, or automatically mutate Memory/Canon.
- Preserve Git safety. Do not stage, commit, push, amend, rebase, reset, clean,
  restore, or stash unless the owner explicitly authorizes the exact action.
