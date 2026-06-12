# Roadmap Enrichment Tool Commands

## Safety rule

These commands are for explicit collection mode only and must not be run during Codex implementation micro-tasks. This file documents local command syntax discovered through harmless command presence and help probes only. It does not mean context collection has run.

## CCE

- installed: yes
- executable candidates:
  - `/home/tjrpirateking/.local/bin/cce`
  - `/home/tjrpirateking/.local/bin/code-context-engine`
- help command attempted:
  - `cce --help`: succeeded
  - `code-context-engine --help`: succeeded
  - `cce search --help`: initially failed while loading `.context-engine.yaml`; succeeded after config repair
  - `code-context-engine search --help`: initially failed while loading `.context-engine.yaml`; succeeded after config repair
  - `cce status --help`: succeeded after config repair
  - `code-context-engine status --help`: succeeded after config repair
- observed syntax:
  - Top-level syntax: `cce [OPTIONS] COMMAND [ARGS]...`
  - Alias syntax: `code-context-engine [OPTIONS] COMMAND [ARGS]...`
  - Commands shown by help include `index`, `search`, `status`, `list`, `init`, `serve`, `sessions`, and service commands.
  - Search syntax: `cce search [OPTIONS] QUERY`
  - Official docs show `cce search "auth flow"` as the CLI query-test command.
  - Search options shown by help: `--top-k INTEGER`, default `5`
  - Alias search syntax: `code-context-engine search [OPTIONS] QUERY`
  - MCP retrieval tool: `context_search`, described by official docs as hybrid vector + BM25 search with graph expansion.
- `.context-engine.yaml` repaired: yes
- config repair summary:
  - Replaced invalid unquoted YAML alias-like ignore entry `**pycache**` with `__pycache__`.
  - Quoted `compression.output` as `"off"` because CCE requires a string and YAML parsed bare `off` as boolean `false`.
- config required:
  - `.context-engine.yaml` is an accepted project-level config file.
  - `compression.output` supports `off`, `lite`, `standard`, and `max`; current `"off"` preserves disabled output compression.
  - `retrieval.top_k` and `retrieval.confidence_threshold` are documented config keys.
  - After repair, `cce search --help` and `code-context-engine search --help` parse the config successfully.
- output convention:
  - Search help says it shows results and updates savings stats.
  - Retrieval output format was not observed because search was not run.
- safe PHASE7-IMPL-004 candidate command:
  - `cce search --top-k 8 "Find backend files that list, read, write, or create scenes."`
- CCE ready for collect mode: ready for explicit authorized collection
- notes:
  - Do not run `cce init`; it writes editor/agent configuration, including Codex global config and `AGENTS.md`.
  - Do not run `cce index` or `cce search` during Codex implementation micro-tasks.
  - CCE command syntax is known, but actual retrieval/search/indexing has intentionally not been run.
  - Future collect mode may use CCE only after explicit user authorization.
  - Graphify, Repomix, and AI Context command syntax were not retested during the CCE readiness repair.

## Graphify

- installed: yes
- executable candidates:
  - `/home/tjrpirateking/.local/bin/graphify`
- help command attempted:
  - `graphify --help`: succeeded
- observed syntax:
  - Top-level syntax: `graphify <command>`
  - Query syntax from help: `graphify query "<question>" [--dfs] [--context C] [--budget N] [--graph <path>]`
  - Path syntax from help: `graphify path "A" "B" [--graph <path>]`
  - Explain syntax from help: `graphify explain "X" [--graph <path>]`
  - Update/extract commands exist but are prohibited unless a future explicit collect/update task authorizes them.
- config required:
  - Existing graph path defaults to `graphify-out/graph.json` for query/path/explain commands.
- output convention:
  - Help implies query/path/explain print scoped graph-derived text to stdout.
- safe PHASE7-IMPL-004 candidate command:
  - `graphify query "Which backend routes call which project storage helpers for scenes?" --graph graphify-out/graph.json --budget 2000`
- notes:
  - This command was not run.
  - Future collect mode may use read-only query/path/explain against an existing graph if explicitly authorized.
  - Do not run `graphify update`, `graphify extract`, or install commands unless explicitly authorized.

## Repomix

- installed: yes
- executable candidates:
  - `/home/tjrpirateking/.nvm/versions/node/v24.16.0/bin/repomix`
  - `/home/tjrpirateking/.nvm/versions/node/v24.16.0/bin/npx`
- help command attempted:
  - `repomix --help`: succeeded
  - `npx repomix --help`: succeeded
- observed syntax:
  - Top-level syntax: `repomix [options] [directories...]`
  - Config syntax: `repomix --config <path>`
  - Stdin file list syntax: `repomix --stdin`
  - Output syntax: `repomix --output <file>`
  - Compression syntax: `repomix --compress`
  - Token count tree syntax: `repomix --token-count-tree`
- config required:
  - Existing script uses `repomix.workspace-docs.config.json` and `repomix.config.json`.
- output convention:
  - Default output is `repomix-output.xml`.
  - Existing AI context script writes to `ai_context/repomix-workspace-docs-context.xml`, `ai_context/repomix-workspace-context.xml`, or `ai_context/repomix-current-task-context.xml`.
- safe PHASE7-IMPL-004 candidate command:
  - `printf '%s\n' AGENTS.md docs/roadmap/implementation_status.md docs/roadmap/roadmap_index.yaml docs/roadmap/project_workspace_implementation_decision_sweep.md docs/roadmap/task_backlog.md | repomix --stdin --compress --token-count-tree --output ai_context/repomix-current-task-context.xml`
- notes:
  - This command was not run.
  - Future collect mode should prefer a scoped file list and an explicit output path.

## AI Context Script

- present: yes
- path:
  - `scripts/generate_ai_context.sh`
- help/dry-run support if discovered:
  - No explicit `--help` or dry-run mode was discovered in the script body.
  - Running with no arguments defaults to `docs` mode and generates context, so it is not a safe help command.
- observed syntax:
  - `./scripts/generate_ai_context.sh docs`
  - `./scripts/generate_ai_context.sh full`
  - `./scripts/generate_ai_context.sh task <file1> <file2> ...`
- exact example command from this prompt:
  - Preserved in `.codex-context/PHASE7-IMPL-004/ai-context-command-candidates.md`.
- PHASE7-IMPL-004 candidate command:
  - Preserved in `.codex-context/PHASE7-IMPL-004/ai-context-command-candidates.md`.
- output convention if discovered:
  - `docs` mode writes `ai_context/repomix-workspace-docs-context.xml`.
  - `full` mode writes `ai_context/repomix-workspace-context.xml`.
  - `task` mode writes `ai_context/repomix-current-task-context.xml`.
- notes:
  - The AI Context script was read but not run.
  - Verify output path before running because task mode writes to the shared `ai_context/repomix-current-task-context.xml` path.

## Unknowns / follow-ups

- Decide whether future collection should use CCE, Graphify, Repomix, the AI Context script, or a smaller subset for `PHASE7-IMPL-004`.
- Confirm whether AI Context task mode should support a task-specific output path before using it for orchestrator evidence.
