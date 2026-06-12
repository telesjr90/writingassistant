# Tool Command Probe Template

## Purpose

Use this template to document local command availability and syntax for roadmap enrichment context tools without running context generation, repository analysis, indexing, retrieval, or packing.

## Allowed discovery commands

- `command -v cce || true`
- `command -v code-context-engine || true`
- `command -v graphify || true`
- `command -v repomix || true`
- `command -v npx || true`
- `cce --help`
- `code-context-engine --help`
- `graphify --help`
- `repomix --help`
- `npx repomix --help`
- `test -f scripts/generate_ai_context.sh && sed -n '1,240p' scripts/generate_ai_context.sh`
- Narrow grep in `scripts/`, `docs/`, and top-level docs for known command names.

## Prohibited commands

- `cce init`
- `cce index`
- `cce search` against the repository
- Graphify extraction, update, query, analysis, or install commands against the repository
- Repomix pack generation commands
- `scripts/generate_ai_context.sh` generation modes unless a future task explicitly authorizes collection
- LeanCTX context/planning commands
- MCP tools
- Broad repository discovery
- Application tests or app servers

## Required output fields

- installed or present
- executable or script path
- help command attempted
- observed syntax
- config required
- output convention
- safe candidate command
- notes

