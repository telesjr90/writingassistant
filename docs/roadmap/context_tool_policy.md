# Context Tool Policy

Roadmap work is docs-first.

`docs/roadmap/roadmap_index.yaml` and `docs/roadmap/implementation_status.md` are the control layer for current task identity, active frontier, and execution boundaries.

## Tool Roles

- Repomix is for scoped frozen context packs before planning sessions.
- Graphify is for topology and dependency questions.
- CCE is for targeted retrieval and delta analysis only after the registry and validator are stable.
- LeanCTX is exceptional fallback only.

## Codex Micro-Task Boundary

Codex must not run Repomix, Graphify, LeanCTX, CCE, MCP tools, or broad scans during implementation micro-tasks.

Codex micro-tasks should read only the files named in the prompt, modify only the allowed files, and run only the validation commands named in the prompt.

Context packs are refreshable artifacts, not source of truth. If a context pack disagrees with the roadmap control layer, the control layer wins until a human-approved roadmap update changes it.

