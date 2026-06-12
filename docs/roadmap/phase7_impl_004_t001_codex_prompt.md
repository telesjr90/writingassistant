# Codex Prompt: PHASE7-IMPL-004-T001

## Task

Read-only chapter and scene metadata compatibility inventory.

## Goal

Inventory how the current repo stores, reads, lists, orders, and displays chapters and scenes, especially any legacy scene Markdown assumptions and any project-aware metadata assumptions.

## Hard limits

* Do not modify runtime code.
* Do not modify tests.
* Do not modify project prose.
* Do not rewrite scene Markdown.
* Do not generate story prose.
* Do not call Ollama or any model.
* Do not run Repomix, Graphify, LeanCTX, CCE, MCP tools, or broad external discovery.
* Do not stage, commit, or push.

## Allowed output file

The future Codex run may create exactly one inventory report:

* `docs/roadmap/phase7_impl_004_t001_inventory.md`

## Allowed read-only context

The future Codex run may inspect only files and directories that are necessary to answer the inventory question. It should start with:

* `AGENTS.md`
* `docs/roadmap/implementation_status.md`
* `docs/roadmap/roadmap_index.yaml`
* `docs/roadmap/project_workspace_implementation_decision_sweep.md`
* `docs/roadmap/task_backlog.md`
* backend or server files related to projects, chapters, scenes, and file storage
* frontend files related to project switching, chapter lists, scene lists, scene display, and scene selection
* tests related to projects, chapters, scenes, or file storage

It must keep inspection narrow and stop once it has enough evidence.

## Inventory report requirements

The inventory report must include:

1. Summary of current chapter storage assumptions.
2. Summary of current scene storage assumptions.
3. Existing file paths or modules that read chapter/scene data.
4. Existing file paths or modules that write or create chapter/scene data.
5. Existing API routes or handlers related to chapters/scenes.
6. Existing frontend components or hooks related to chapter/scene display.
7. Places that assume hard-coded or legacy project paths.
8. Places that assume scene Markdown body content instead of metadata.
9. Existing tests that should protect compatibility.
10. Gaps that PHASE7-IMPL-004-T002 or later tasks should address.
11. Explicit "must not touch" areas for future implementation.
12. Suggested file allowlist for PHASE7-IMPL-004-T002.

## Product boundaries

* Preserve owner-authored prose exactly.
* Metadata compatibility must not rewrite scene bodies.
* No generated prose.
* No prose rewriting, continuation, imitation, polishing, or improvement.
* No model calls.
* No memory/canon mutation.
* No OMI promotion or candidate approval behavior.
* No hidden Project Overview work.

## Validation for the future Codex run

The future Codex run should run:

```bash
git diff --check
git status --short --branch
```

If the local hook requires those exact validation commands to be wrapped through LeanCTX, the future Codex run may use the exact hook-provided LeanCTX wrapper only for those validation commands.

It should not need to run the application or tests because the task is read-only documentation inventory.

## Final response format for the future Codex run

* Result: PASS, PARTIAL, or BLOCKED
* Files changed
* Summary
* Validation run and result
* Key inventory findings
* Suggested next task
* Confirm no staging, commit, or push

