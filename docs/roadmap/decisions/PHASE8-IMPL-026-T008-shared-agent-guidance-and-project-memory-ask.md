# PHASE8-IMPL-026-T008 — Shared Agent Guidance and Project Memory Ask

## Result

T008: **complete/PASS**.

T008 provides a deterministic, repository-native, read-only Project Memory Ask
contract for Codex, OpenCode, and compatible agents. It requires no Serena,
LlamaIndex, Qdrant, embeddings, MCP server, network service, model adapter, or
external retrieval system.

## Delivered contract

- `docs/project-memory/ask-protocol.md` defines bounded request fields,
  response fields, result vocabulary, authority precedence, freshness and
  owner-decision reporting, and fail-closed behavior.
- `.agents/skills/project-memory-read/SKILL.md` defines source consultation
  order, bounded search, registry/publication use, citations, uncertainty, stop
  conditions, and product boundaries without copying project truth.
- `.opencode/agents/project-memory-ask.md` defines a read-only subagent. Write,
  edit, patch, network, and external-directory access are denied; shell access
  is denied by default and limited to explicit read-only Git inspection.
- `scripts/project_memory/validate_agent_guidance.py` deterministically checks
  required files, Ask fields/result vocabulary, shared safety boundaries, and
  read-only OpenCode controls.
- `tests/project_memory/test_agent_guidance_and_ask.py` validates the complete
  T006/T007 owner-deferral and T008 Ask/guidance contract using tracked files and
  temporary fixtures only.
- The human-readable renderer derives active, actionable planned, contingent,
  and owner-deferred contingent behavior from normalized task records and linked
  accepted owner decisions. T006/T007 remain visible but cannot displace T009 as
  the next actionable task.
- Rendered-package semantic validation is bound to the selected snapshot's
  commit and registry hashes. Preserved T004C1/T004C2 packages are validated
  against their own historical normalized state, while current publications
  still require exact convergence with current tracked registries.

## Authority and response behavior

Accepted roadmap and decisions precede live code/schemas, tests, accepted live
validation, exact Git history, normalized registries, and generated evidence.
Registries and the current rendered publication are navigation aids, not
authority. Generated evidence and model output never become project truth.

Ask responses separate facts from inference and report source paths/line ranges
or stable IDs, authority class, freshness, bound commit, uncertainty, conflicts,
and owner-decision status. Stale, conflicting, owner-pending, unsupported-tool,
untrusted/quarantined, protected-path, and out-of-scope requests fail closed.

## Preserved state

- T005 remains complete/PASS.
- T006 and T007 remain owner-deferred, contingent, planned, inactive, and
  unimplemented because no benchmarkable capability gap has been measured.
- T009 is next, planned/inactive.
- T010 and T011 remain planned.
- The application frontier remains `PHASE8-IMPL-024-T003A`.
- PHASE8-IMPL-025 remains published/planned and inactive.
- No retrieval pilot is adopted.

## Safety boundaries

The guidance cannot automatically activate, close, reorder, rewrite, or amend
roadmap tasks; mutate Project Memory registries or Memory/Canon; promote a
candidate; apply promotion; create training data; generate story prose; or
treat model output as truth. Tests do not call a model or run an OpenCode agent.
