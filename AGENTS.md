# Agent Instructions

This repository uses AI agents for tightly scoped implementation and
documentation tasks.

These instructions are ordered by priority:

1. Product safety and project boundaries.
2. Task-specific prompt instructions.
3. Repository-level tool discipline in this file.
4. Current accepted owner decisions and roadmap/task authority.
5. Saved context outputs and focused direct reads.

Task-specific prompts may further restrict tools, files, commands, and scope.

## Implementation-only mode

Implementation-only mode is active under the accepted owner decision
`docs/roadmap/decisions/2026-07-17-project-memory-paused-as-an-application-implementation-gate.md`.

Project Memory is preserved in the repository but is paused as an application
implementation, validation, acceptance, and closeout gate. It is advisory and
nonblocking for ordinary application work. Plan Integrity and execution routing
are also not application gates while this pause remains active.

For ordinary application tasks, agents must not invoke or require:

* Project Memory freshness or `FRESH` status;
* Project Memory supervision, handoffs, refresh, publication, or validation;
* Project Source rotations or continuation packages;
* Plan Integrity reports, reviewers, or validators;
* execution-routing resolution or routing validators;
* `scripts/project_memory/*`;
* `tests/project_memory/*`; or
* the Project Memory GitHub workflow.

Do not repair or maintain Project Memory during ordinary application work.
Project Memory consultation, maintenance, publication, governance, or
reactivation may occur only when the owner explicitly requests that activity.
Reactivation as an application gate requires a later explicit owner decision.

## Application authority and gates

Use this authority order for application implementation:

1. current explicit owner decisions;
2. current roadmap and task documents;
3. tracked application code, schemas, fixtures, and tests within their declared
   roles;
4. saved context-tool outputs as non-authoritative navigation aids; and
5. focused direct file reads.

Historical and superseded records remain accurate for the state they document
but do not override current accepted sources. Generated context and model output
are never project truth. Fail closed when current owner decisions, roadmap/task
authority, and tracked application evidence conflict materially.

At an application task's starting gate, verify only the repository root,
expected branch and full commit when the task supplies them, worktree and staged
state, the current task authority, task scope, dependencies, and allowed files.
At closeout, verify the task requirements, reviewed file scope, relevant
application tests, required integration/runtime evidence, and repository state.
Do not add Project Memory, Plan Integrity, supervision, routing, or freshness
requirements to those gates.

Do not execute beyond the task the owner authorized. Task status, dependencies,
and the application frontier remain controlled by accepted roadmap and task
documents and may not be changed unless the task explicitly authorizes those
changes.

## Product safety boundaries

The app is analysis-only.

Agents must never write, rewrite, continue, imitate, polish, improve, expand, or
extend story prose.

Owner-authored prose storage and editing is allowed when the text is authored by
the owner.

Candidates are not canon. Candidate presentation must remain candidate-first,
evidence/provenance-backed, and owner-controlled.

Promotion records are audit-only until an explicitly authorized apply-promotion
workflow exists. Never automatically promote or apply promotion, and never
automatically mutate Memory/Canon.

Do not silently promote model output, NotebookLM output, extracted candidates,
OMI candidates, planning notes, or generated context into durable project
truth.

Do not create or modify training data, JSONL files, dataset manifests, book
source files, model artifacts, or fine-tuning configs unless the task explicitly
authorizes that track.

Do not call Ollama, live models, Story Check, extraction tools, or
Dramatica-specific logic unless the task explicitly authorizes it.

## Git safety

Do not stage, commit, push, amend, rebase, reset, clean, restore, or stash unless
the owner explicitly authorizes the exact action. Never use destructive Git
operations as an implementation shortcut.

## Default task mode: implementation micro-task

For normal Codex, Cursor, Claude, or OpenCode Go implementation micro-tasks:

* One task equals one deliverable.
* Use the smallest correct change.
* Prefer existing code and existing dependencies.
* Prefer direct reads of the small set of files named in the task.
* Prefer `sed`, `grep`, `rg`, `git diff`, and `git status` for focused work.
* Do not run broad repository scans.
* Do not install dependencies.
* Do not expand scope.
* Do not write extra reports unless the task explicitly asks for one.
* Stop after validation and the final response.

## Context and mapping tools

This repository may use Repomix, Graphify, LeanCTX,
`scripts/generate_ai_context.sh`, `scripts/context_health_check.sh`, and saved
context packs under `.codex-context/` or `ai_context/`.

### Context-generation mode

Use context-generation mode only when the owner explicitly asks to refresh,
generate, run, or update context or mapping outputs. In that mode, the task may
authorize:

* Repomix;
* Graphify;
* LeanCTX;
* `scripts/generate_ai_context.sh`; and
* `scripts/context_health_check.sh`.

Save output only to the explicit context folder authorized by the task. Context
outputs are generated evidence and never authority.

### Implementation mode

Implementation agents must consume existing saved context outputs rather than
regenerate them. During implementation micro-tasks, do not run Repomix,
Graphify, LeanCTX, context-generation scripts, MCP context tools, or subagents.
Do not inspect generated context files beyond the task's relevant saved pack.

If the saved context pack and focused allowed reads are insufficient, stop and
ask the owner for refreshed context or expanded read scope. Do not switch into
context-generation mode without explicit authorization.

When the owner explicitly types `/graphify`, use Graphify before other task work
within the authorized context-generation scope. Do not run Graphify maintenance
after implementation unless the task explicitly asks for it.

## Codex-specific tool discipline

For Codex implementation micro-tasks:

* Do not use LeanCTX, Graphify, Repomix, MCP tools, or subagents.
* Do not run broad repository searches unless the task explicitly authorizes
  them.
* Use `rg` only for explicit symbols or patterns named in the task.
* Never repeat the same discovery, search, or context command unless the prior
  command failed and the retry reason is stated.
* If more context is needed, stop and ask instead of searching repeatedly.
* If a command fails twice, stop and report `BLOCKED`.
* If a file write fails, read the target once, explain the blocker, and stop.
* Do not stage, commit, or push without explicit owner authorization.

## Validation discipline

Before editing, run only the preflight commands named in the task. After editing,
run only the validation commands named in the task.

Use focused tests for touched application behavior by default. Run a broad
backend application suite only when the task or the risk of the change makes a
broad run appropriate, using:

```bash
python3 -m pytest -q tests --ignore=tests/project_memory
```

Do not run `tests/project_memory` during ordinary application validation. Do not
run full application tests merely to compensate for unclear scope. If a focused
test fails for an unclear reason, diagnose within the authorized scope before
considering a broader application-only run.

Typical documentation and repository-state checks include:

* `git diff --check`;
* `git diff --stat`;
* `git diff --name-only`; and
* `git status --short --branch`.

Application acceptance is based on task requirements, relevant application
tests, required integration/runtime evidence, reviewed file scope, and
repository state. Passing tests do not authorize automatic task, roadmap,
candidate, promotion, or Memory/Canon mutation.

## File-scope discipline

Respect the task allowlist. Do not edit files outside it.

Do not modify these unless the task explicitly allows them:

* datasets or generated training records;
* package or dependency files;
* runtime project fixtures;
* book source files;
* model artifacts; or
* hidden context or tool outputs.

Preserve unrelated owner changes in a dirty worktree. Stop when unrelated
changes overlap the task and cannot be separated safely.

## Project Memory when explicitly requested

Project Memory operational and consultation documents remain preserved under
`docs/project-memory/`. They may be used only for an explicit owner-requested
Project Memory consultation, maintenance, publication, governance, or
reactivation task. Their historical technical contracts do not make Project
Memory an ordinary application gate while implementation-only mode is active.

An explicit Project Memory task remains read-only or mutation-bounded according
to its own owner authorization. Never automatically mutate roadmap state,
Memory/Canon, candidates, promotions, story prose, registries, or generated
evidence, and never treat model output as truth.

## Response discipline

Final responses should include:

1. Result: `PASS`, `PARTIAL`, or `BLOCKED`.
2. Files created or modified.
3. Summary of the implemented change.
4. Validation commands and results.
5. Deferred work.
6. Confirmation that no staging, commit, or push was performed unless
   explicitly requested.
