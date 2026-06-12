# Agent Instructions

This repository uses AI agents for tightly scoped implementation and documentation tasks.

These instructions are ordered by priority:

1. Product safety and project boundaries.
2. Task-specific prompt instructions.
3. Repository-level tool discipline in this file.
4. Precomputed context packs.
5. Direct file reads and focused validation.

Task-specific prompts may further restrict tool use, files, commands, and scope.

## Product safety boundaries

The app is analysis-only.

Agents must never write, rewrite, continue, imitate, polish, improve, expand, or extend story prose.

Owner-authored prose storage and editing is allowed when the text is authored by the owner.

Candidates are not canon.

Promotion records are audit-only until future apply-promotion exists.

Do not silently promote model output, NotebookLM output, extracted candidates, OMI candidates, or planning notes into durable project truth.

Do not create or modify training data, JSONL files, dataset manifests, book source files, model artifacts, or fine-tuning configs unless the task explicitly authorizes that track.

Do not call Ollama, live models, Story Check, extraction tools, or Dramatica-specific logic unless the task explicitly authorizes it.

Do not stage, commit, or push unless the user explicitly asks.

## Default task mode: implementation micro-task

For normal Codex, Cursor, or Claude implementation micro-tasks:

* One task equals one deliverable.
* Use the smallest correct change.
* Prefer existing code and existing dependencies.
* Prefer direct file reads of the small set of files named in the task.
* Prefer sed, grep, rg, git diff, git status, and focused test commands.
* Do not run broad repository scans.
* Do not install dependencies.
* Do not expand scope.
* Do not write extra reports unless the task explicitly asks for a report.
* Stop after validation and final response.

## Context and mapping tools

This repo may use these context and mapping tools:

* Repomix
* Graphify
* LeanCTX
* generated context packs under .codex-context/
* generated context packs under ai_context/

These tools are useful for preparing context, but they must not be repeatedly called during implementation micro-tasks.

## Context-generation mode

Use context-generation mode only when the user explicitly asks to refresh, generate, run, or update context or mapping outputs.

In context-generation mode, the owner or agent may run:

* Repomix
* Graphify
* LeanCTX
* scripts/generate_ai_context.sh
* scripts/context_health_check.sh

The output should be saved to an explicit context folder such as:

* .codex-context/phase7-preflight/
* ai_context/

After context is generated, implementation agents should read the saved outputs instead of regenerating them.

## Implementation mode

In implementation mode, agents must not call:

* LeanCTX
* Graphify
* Repomix
* MCP tools
* subagents
* broad repo scans

Implementation agents may read precomputed outputs such as:

* .codex-context/phase7-preflight/CONTEXT_MANIFEST.md
* .codex-context/phase7-preflight/TOOL_POLICY.md
* .codex-context/phase7-preflight/repo_state.txt
* .codex-context/phase7-preflight/phase7_symbol_map.txt
* .codex-context/phase7-preflight/focused_source_excerpts.txt
* .codex-context/phase7-preflight/repomix_focused_output.xml
* .codex-context/phase7-preflight/graphify_output.txt
* .codex-context/phase7-preflight/validation_snapshot.txt
* ai_context/repomix-current-task-context.xml
* ai_context/repomix-workspace-context.xml
* ai_context/repomix-workspace-docs-context.xml

If the context pack is insufficient, stop and ask the user to refresh the context pack. Do not regenerate it yourself unless the task explicitly switches to context-generation mode.

## Graphify explicit-use rule

When the user explicitly types /graphify, use Graphify before doing other work.

Outside explicit /graphify requests or context-generation tasks:

* Do not run Graphify during implementation micro-tasks.
* Read saved Graphify outputs instead.
* Do not run graphify update after code changes unless the task explicitly asks for graph maintenance.

## LeanCTX rule

LeanCTX may be useful for large context compression and exploration, but it has caused token and tool loops in this repo.

For Codex implementation micro-tasks:

* Do not use LeanCTX.
* Do not call LeanCTX MCP tools.
* Do not inspect LeanCTX descriptors.
* Do not retry LeanCTX calls.
* Read saved context packs instead.

For Claude or Cursor large-context planning tasks, LeanCTX may be used only if the prompt explicitly allows it. If LeanCTX fails once, report it once and continue with saved Repomix or context outputs plus targeted reads. Do not repeatedly call LeanCTX.

## Repomix rule

Repomix should be run before implementation when a context pack is needed.

During implementation micro-tasks:

* Do not run Repomix.
* Do not regenerate Repomix outputs.
* Do not read the entire Repomix XML unless the task explicitly asks for broad architecture review.
* Prefer focused source excerpts and targeted file reads.
* Search or inspect only relevant sections of Repomix output if needed.

## Codex-specific tool discipline

For Codex implementation micro-tasks:

* Do not use LeanCTX.
* Do not use Graphify.
* Do not use Repomix.
* Do not call MCP tools.
* Do not spawn subagents.
* Do not run broad repository searches unless the task explicitly authorizes them.
* Use rg only for explicit symbols named in the task.
* Never call the same discovery, search, or context command more than once unless the previous command failed and the retry reason is stated.
* If more context is needed, stop and ask instead of searching repeatedly.
* If a command fails twice, stop and report BLOCKED.
* If a file write fails, read the target file once, explain the blocker, and stop.
* Do not continue thinking after validation or report is complete.
* Do not stage, commit, or push unless explicitly instructed.

## Validation discipline

Before editing, run only the preflight commands named in the task.

After editing, run only the validation commands named in the task.

Typical validation commands may include:

* git diff --check
* git diff --stat
* git status --short --branch

Use focused pytest commands for the files touched by the task.

Do not run full pytest unless the task asks for it or focused tests fail for unclear reasons.

## File-scope discipline

Respect the task allowlist.

Do not edit files outside the allowlist.

Do not modify these unless the task explicitly allows them:

* dataset files
* package or dependency files
* generated training records
* runtime project fixtures
* book source files
* model artifacts
* hidden context or tool outputs

## Response discipline

Final responses should include:

1. Result: PASS, PARTIAL, or BLOCKED.
2. Files created or modified.
3. Summary of the implemented change.
4. Validation commands and results.
5. Deferred work.
6. Confirmation that no staging, commit, or push was performed unless explicitly requested.
