# Roadmap Enrichment Scaffold

This directory contains the local scaffold for later roadmap enrichment. It does not run enrichment by itself and must not be treated as an autonomous planner.

Intended pipeline:

```text
roadmap_index.yaml
  -> select explicit task or active task
  -> write task manifest
  -> collect CCE evidence in explicit collect mode
  -> collect Graphify topology in explicit collect mode
  -> create scoped Repomix pack in explicit collect mode
  -> write enrichment JSON
  -> render task record
  -> run validators
  -> human review
```

Rules:

- The orchestrator is dumb, not autonomous.
- It must not decide product order.
- It must not invent tasks.
- It must not rewrite the roadmap from scratch.
- It must not run implementation changes.
- `PHASE7-IMPL-004` is the first intended test case.
- `enrich_all.py` must not be used until `enrich_task.py` works for one task.

The first scaffold version may write task manifests only. Evidence collection, enrichment JSON creation, and task record rendering are later explicit steps.

## Modes

### scaffold

`scaffold` mode selects an explicit parent task or the active parent task and writes `.codex-context/<TASK_ID>/task_manifest.json`.

It does not collect evidence and does not call CCE, Graphify, Repomix, AI Context, LeanCTX, MCP tools, tests, or app servers.

### collect-plan

`collect-plan` mode creates planned evidence files for the selected parent task:

- `.codex-context/<TASK_ID>/collection_plan.md`
- `.codex-context/<TASK_ID>/cce-queries.md`
- `.codex-context/<TASK_ID>/graphify-queries.md`
- `.codex-context/<TASK_ID>/repomix-include-candidates.txt`
- `.codex-context/<TASK_ID>/ai-context-command-candidates.md`
- `.codex-context/<TASK_ID>/evidence_manifest.json`

Collect-plan does not run tools because command planning must stay separate from collection. Planned evidence files describe intended future collection commands and outputs; collected evidence files are created only in later explicit collection tasks.

`PHASE7-IMPL-004` is the first test case for collect-plan mode. Future collect-plan or collect modes should use `scripts/roadmap_enrichment/tool_commands.md` for documented command syntax and must not infer product order or task priority.

## Tool Command Discovery

Tool command discovery records local executable availability and help syntax without running context generation.

Discovery is intentionally separate from collection because CCE retrieval, Graphify analysis, Repomix packing, and AI Context generation can scan or write large context artifacts. Those commands belong only in a future explicit collect-plan or collect mode.

Documented syntax lives in:

- `scripts/roadmap_enrichment/tool_commands.md`
- `scripts/roadmap_enrichment/templates/tool_command_probe.md`
- `.codex-context/PHASE7-IMPL-004/ai-context-command-candidates.md`

Future collect-plan and collect modes should read `tool_commands.md` to choose candidate commands, then require an explicit human-approved task before running any command that indexes, retrieves, analyzes, packs, or writes generated context.

## CCE

CCE can be used in explicit collect mode after user authorization.

- `cce search` is the documented query-test CLI.
- Local help confirms `cce search [OPTIONS] QUERY` with `--top-k`.
- `cce init` is not allowed in this orchestrated workflow because it writes editor/agent configuration.
- CCE results are evidence artifacts, not roadmap authority.
- Actual CCE retrieval/search/indexing has not been run yet.
